"""Multi-Chain JSON-RPC client for on-chain balance verification & accounting.

Supports Base Mainnet (8453), Base Sepolia (84532), Arbitrum Mainnet (42161),
Arbitrum Sepolia (421614), and any EVM JSON-RPC endpoint.

Used as an independent ground-truth layer: balances come straight from blockchain
nodes, with no indexer in between. Supports:
- eth_getBalance            -> native ETH balance
- eth_call balanceOf        -> ERC-20 token balances
- eth_call totalSupply      -> BoringVault share supply
- eth_call getRate          -> AccountantWithRateProviders share price
- eth_getLogs               -> Direct ERC-20 transfer event logs
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

BASE_CHAIN_ID = 8453

DEFAULT_PUBLIC_RPCS_BY_CHAIN: dict[int, list[str]] = {
    8453: [
        "https://mainnet.base.org",
        "https://base.llamarpc.com",
        "https://base-rpc.publicnode.com",
        "https://1rpc.io/base",
    ],
    84532: [
        os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org"),
        "https://sepolia.base.org",
        "https://base-sepolia-rpc.publicnode.com",
    ],
    42161: [
        "https://arb1.arbitrum.io/rpc",
        "https://arbitrum.llamarpc.com",
        "https://arbitrum-one-rpc.publicnode.com",
    ],
    421614: [
        os.getenv("ARBITRUM_SEPOLIA_RPC_URL", "https://sepolia-rollup.arbitrum.io/rpc"),
        "https://sepolia-rollup.arbitrum.io/rpc",
        "https://arbitrum-sepolia-rpc.publicnode.com",
    ],
}

CHAIN_NAME_TO_ID: dict[str, int] = {
    "base": 8453,
    "base_mainnet": 8453,
    "base-mainnet": 8453,
    "base_sepolia": 84532,
    "basesepolia": 84532,
    "base-sepolia": 84532,
    "arbitrum": 42161,
    "arbitrum_mainnet": 42161,
    "arbitrum-one": 42161,
    "arbitrum_sepolia": 421614,
    "arbitrumsepolia": 421614,
    "arbitrum-sepolia": 421614,
}

DEFAULT_PUBLIC_RPCS = DEFAULT_PUBLIC_RPCS_BY_CHAIN[BASE_CHAIN_ID]
DEFAULT_PUBLIC_RPC = DEFAULT_PUBLIC_RPCS[0]
UNIBLOCK_RPC_URL = f"https://api.uniblock.dev/uni/v1/json-rpc?chainId={BASE_CHAIN_ID}"
RPC_URL = os.getenv("BASE_RPC_URL") or os.getenv("RPC_URL") or UNIBLOCK_RPC_URL

# Function selectors
SEL_BALANCE_OF = "0x70a08231"        # balanceOf(address)
SEL_CONVERT_TO_ASSETS = "0x07a2d13a"  # convertToAssets(uint256)
SEL_GET_ALL_MARKETS = "0xb0772d0b"   # getAllMarkets() — Compound-fork comptroller
SEL_UNDERLYING = "0x6f307dc3"        # underlying() — Compound-fork mToken
SEL_BALANCE_OF_UNDERLYING = "0x3af9e669"  # balanceOfUnderlying(address)
SEL_TOTAL_SUPPLY = "0x18160ddd"      # totalSupply()
SEL_GET_RATE = "0x679aefce"          # getRate() on AccountantWithRateProviders
SEL_DECIMALS = "0x313ce567"          # decimals()
SEL_SYMBOL = "0x95d89b41"            # symbol()
SEL_NAME = "0x06fdde03"              # name()

EVENT_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def _build_retry_adapter(retries: int = 4, backoff_factor: float = 1.0) -> HTTPAdapter:
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=["POST"],
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry_strategy)


def _parse_keys(
    api_key: str | list[str] | None, backup_api_key: str | list[str] | None = None
) -> list[str]:
    """Normalize primary and optional backup keys into an ordered deduplicated list."""
    keys: list[str] = []
    for item in (api_key, backup_api_key):
        if not item:
            continue
        if isinstance(item, str):
            parts = [p.strip() for p in item.split(",") if p.strip()]
            for p in parts:
                if p not in keys:
                    keys.append(p)
        elif isinstance(item, (list, tuple)):
            for p in item:
                p_str = str(p).strip()
                if p_str and p_str not in keys:
                    keys.append(p_str)
    return keys


def _pad_address(address: str) -> str:
    """Zero-pad an address to a 32-byte (64 hex char) ABI word."""
    return address.lower().removeprefix("0x").rjust(64, "0")


def _pad_uint(value: int) -> str:
    return hex(value)[2:].rjust(64, "0")


def _hex_to_int(result: str | None) -> int:
    """Parse a hex RPC result; an empty '0x' return is treated as 0."""
    if not result or result == "0x":
        return 0
    return int(result, 16)


def _hex_to_string(result: str | None) -> str:
    """Parse an ABI-encoded string return value."""
    if not result or result == "0x" or len(result) < 130:
        return ""
    try:
        raw_bytes = bytes.fromhex(result[2:])
        length = int.from_bytes(raw_bytes[32:64], "big")
        string_bytes = raw_bytes[64:64 + length]
        return string_bytes.decode("utf-8", errors="replace").rstrip("\x00")
    except Exception:
        return ""


class RpcError(Exception):
    """Raised when the JSON-RPC endpoint returns an error object."""


class UniblockRpcClient:
    """Multi-Chain JSON-RPC client for Base, Arbitrum, Testnets, etc."""

    def __init__(
        self,
        api_key: str | list[str] = "",
        backup_api_key: str | list[str] | None = None,
        rate_limit_delay: float = 0.15,
        chain_id: int = BASE_CHAIN_ID,
        rpc_url: str | None = None,
    ):
        self.api_keys = _parse_keys(api_key, backup_api_key)
        if not self.api_keys:
            self.api_keys = [""]
        self.current_key_index = 0
        self.rate_limit_delay = rate_limit_delay
        self.chain_id = chain_id
        self.rpc_url = rpc_url
        self.session = requests.Session()
        if self.api_keys[0]:
            self.session.headers.update({"x-api-key": self.api_keys[0]})
        self.session.headers.update({"content-type": "application/json"})
        self.session.mount("https://", _build_retry_adapter())
        self._request_id = 0
        self._market_cache: dict[str, list[tuple[str, str | None]]] = {}

        # Public RPC pool for this chain
        self.public_rpcs = DEFAULT_PUBLIC_RPCS_BY_CHAIN.get(
            self.chain_id, DEFAULT_PUBLIC_RPCS
        )
        if self.rpc_url and self.rpc_url not in self.public_rpcs:
            self.public_rpcs = [self.rpc_url] + self.public_rpcs

    def _switch_to_next_key(self, reason: str = "") -> bool:
        """Switch to the next available API key if available."""
        if len(self.api_keys) <= 1:
            return False
        next_index = (self.current_key_index + 1) % len(self.api_keys)
        if next_index == self.current_key_index:
            return False
        prev_key = self.api_keys[self.current_key_index]
        next_key = self.api_keys[next_index]
        logger.warning(
            "RPC API key ...%s failed (%s). Switching to backup key ...%s",
            prev_key[-6:] if len(prev_key) >= 6 else prev_key,
            reason,
            next_key[-6:] if len(next_key) >= 6 else next_key,
        )
        self.current_key_index = next_index
        self.session.headers["x-api-key"] = next_key
        return True

    def _call_public_rpc(self, payload: dict[str, Any], method: str) -> Any:
        """Call public RPC endpoints with fallback across the pool."""
        last_err: Exception | None = None
        for rpc_url in self.public_rpcs:
            try:
                resp = requests.post(
                    rpc_url,
                    json=payload,
                    headers={"content-type": "application/json"},
                    timeout=20,
                )
                if resp.status_code == 429:
                    continue
                resp.raise_for_status()
                body = resp.json()
                if "error" in body:
                    raise RpcError(f"{method} failed on public RPC ({rpc_url}): {body['error']}")
                return body.get("result")
            except RpcError:
                raise
            except Exception as exc:
                last_err = exc
                continue
        raise RpcError(f"{method} failed across all public RPC endpoints for chain {self.chain_id}: {last_err}")

    def call(self, method: str, params: list[Any]) -> Any:
        """Raw JSON-RPC call. Returns the 'result' field or raises RpcError."""
        max_attempts = len(self.api_keys) if self.api_keys else 1
        last_exc: Exception | None = None
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params,
        }

        # If explicit custom rpc_url provided or uniblock key not configured, use public pool directly
        if self.rpc_url or getattr(self, "_use_public_rpc", False) or not self.api_keys or not self.api_keys[0]:
            return self._call_public_rpc(payload, method)

        endpoint_url = f"https://api.uniblock.dev/uni/v1/json-rpc?chainId={self.chain_id}"
        for attempt in range(max_attempts):
            try:
                response = self.session.post(endpoint_url, json=payload, timeout=30)
                if response.status_code in (429, 401, 403) and attempt < max_attempts - 1:
                    if self._switch_to_next_key(f"HTTP {response.status_code}"):
                        continue
                response.raise_for_status()
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)
                body = response.json()
                if "error" in body:
                    raise RpcError(f"{method} failed: {body['error']}")
                return body.get("result")
            except RpcError:
                raise
            except requests.RequestException as exc:
                last_exc = exc
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if attempt < max_attempts - 1 and self._switch_to_next_key(
                    f"HTTP {status}" if status else str(exc)
                ):
                    continue
                break

        # Fallback to public RPC pool
        try:
            logger.info("Falling back to public RPC pool for chain %s method %s", self.chain_id, method)
            result = self._call_public_rpc(payload, method)
            self._use_public_rpc = True
            return result
        except Exception as fb_exc:
            logger.debug("Public RPC fallback failed: %s", fb_exc)
        if last_exc:
            raise last_exc

    def get_block_number(self) -> int:
        return int(self.call("eth_blockNumber", []), 16)

    def get_eth_balance(self, wallet: str, block: str = "latest") -> int:
        """Native ETH balance in wei."""
        return _hex_to_int(self.call("eth_getBalance", [wallet, block]))

    def get_erc20_balance(self, token: str, wallet: str, block: str = "latest") -> int:
        """ERC-20 balanceOf(wallet) in the token's raw units."""
        data = SEL_BALANCE_OF + _pad_address(wallet)
        return _hex_to_int(self.call("eth_call", [{"to": token, "data": data}, block]))

    def get_token_decimals(self, token: str, block: str = "latest") -> int:
        """Query decimals() of ERC-20 token."""
        try:
            res = self.call("eth_call", [{"to": token, "data": SEL_DECIMALS}, block])
            return _hex_to_int(res) or 18
        except Exception:
            return 18

    def get_token_symbol(self, token: str, block: str = "latest") -> str:
        """Query symbol() of ERC-20 token."""
        try:
            res = self.call("eth_call", [{"to": token, "data": SEL_SYMBOL}, block])
            return _hex_to_string(res)
        except Exception:
            return ""

    def get_token_name(self, token: str, block: str = "latest") -> str:
        """Query name() of ERC-20 token."""
        try:
            res = self.call("eth_call", [{"to": token, "data": SEL_NAME}, block])
            return _hex_to_string(res)
        except Exception:
            return ""

    def get_vault_total_supply(self, vault: str, block: str = "latest") -> int:
        """Query totalSupply() of BoringVault."""
        try:
            res = self.call("eth_call", [{"to": vault, "data": SEL_TOTAL_SUPPLY}, block])
            return _hex_to_int(res)
        except Exception:
            return 0

    def get_accountant_rate(self, accountant: str, block: str = "latest") -> float:
        """Query getRate() on AccountantWithRateProviders."""
        try:
            res = self.call("eth_call", [{"to": accountant, "data": SEL_GET_RATE}, block])
            val = _hex_to_int(res)
            return val / 1e6 if val else 1.0
        except Exception:
            return 1.0

    def get_vault_assets(
        self, vault: str, wallet: str, block: str = "latest"
    ) -> tuple[int, int]:
        """ERC-4626 vault position: returns (shares, underlying_assets_raw)."""
        shares = self.get_erc20_balance(vault, wallet, block)
        if shares == 0:
            return 0, 0
        data = SEL_CONVERT_TO_ASSETS + _pad_uint(shares)
        result = self.call("eth_call", [{"to": vault, "data": data}, block])
        return shares, _hex_to_int(result)

    def get_transfer_logs(
        self,
        token: str,
        wallet: str,
        from_block: int | str = 0,
        to_block: str = "latest",
    ) -> list[dict[str, Any]]:
        """Fetch Transfer events involving wallet via eth_getLogs."""
        padded_wallet = "0x000000000000000000000000" + wallet.lower().removeprefix("0x")
        events: list[dict[str, Any]] = []
        fb = hex(from_block) if isinstance(from_block, int) else from_block

        # 1. Inbound transfers: Transfer(from, wallet, value) -> topic2 is padded_wallet
        try:
            in_logs = self.call("eth_getLogs", [{
                "fromBlock": fb,
                "toBlock": to_block,
                "address": token,
                "topics": [EVENT_TRANSFER_TOPIC, None, padded_wallet],
            }])
            for log in in_logs or []:
                log["_direction"] = "in"
                events.append(log)
        except Exception as exc:
            logger.debug("Failed to fetch inbound logs for %s: %s", wallet, exc)

        # 2. Outbound transfers: Transfer(wallet, to, value) -> topic1 is padded_wallet
        try:
            out_logs = self.call("eth_getLogs", [{
                "fromBlock": fb,
                "toBlock": to_block,
                "address": token,
                "topics": [EVENT_TRANSFER_TOPIC, padded_wallet, None],
            }])
            for log in out_logs or []:
                log["_direction"] = "out"
                events.append(log)
        except Exception as exc:
            logger.debug("Failed to fetch outbound logs for %s: %s", wallet, exc)

        return events


def get_rpc_client_for_chain(
    chain: str | int,
    api_key: str = "",
    backup_api_key: str = "",
    rate_limit_delay: float = 0.15,
) -> UniblockRpcClient:
    """Factory helper to obtain a configured RPC client for any chain."""
    if isinstance(chain, int):
        chain_id = chain
    else:
        chain_lower = str(chain).lower().replace(" ", "").replace("-", "_")
        chain_id = CHAIN_NAME_TO_ID.get(chain_lower, BASE_CHAIN_ID)

    rpc_url = None
    if chain_id == 84532:
        rpc_url = os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")
    elif chain_id == 421614:
        rpc_url = os.getenv("ARBITRUM_SEPOLIA_RPC_URL", "https://sepolia-rollup.arbitrum.io/rpc")
    elif chain_id == 8453:
        rpc_url = os.getenv("BASE_RPC_URL")
    elif chain_id == 42161:
        rpc_url = os.getenv("ARBITRUM_RPC_URL")

    return UniblockRpcClient(
        api_key=api_key,
        backup_api_key=backup_api_key,
        rate_limit_delay=rate_limit_delay,
        chain_id=chain_id,
        rpc_url=rpc_url,
    )
