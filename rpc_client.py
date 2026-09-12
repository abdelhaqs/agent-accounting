"""Uniblock JSON-RPC client for raw on-chain balance verification on Base.

Endpoint: https://api.uniblock.dev/uni/v1/json-rpc?chainId=8453 (Base mainnet)
Auth: x-api-key header with the same Uniblock API key used for the DeBank proxy.

Used as an independent ground-truth layer: balances come straight from Base
nodes, with no indexer in between. Supports:
- eth_getBalance            -> native ETH balance
- eth_call balanceOf        -> ERC-20 wallet balances
- eth_call convertToAssets  -> ERC-4626 vault shares -> underlying assets
"""
from __future__ import annotations

import logging
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

BASE_CHAIN_ID = 8453
RPC_URL = f"https://api.uniblock.dev/uni/v1/json-rpc?chainId={BASE_CHAIN_ID}"

# Function selectors
SEL_BALANCE_OF = "0x70a08231"        # balanceOf(address)
SEL_CONVERT_TO_ASSETS = "0x07a2d13a"  # convertToAssets(uint256)
SEL_GET_ALL_MARKETS = "0xb0772d0b"   # getAllMarkets() — Compound-fork comptroller
SEL_UNDERLYING = "0x6f307dc3"        # underlying() — Compound-fork mToken
SEL_BALANCE_OF_UNDERLYING = "0x3af9e669"  # balanceOfUnderlying(address)


def _build_retry_adapter(retries: int = 4, backoff_factor: float = 1.0) -> HTTPAdapter:
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["POST"],
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry_strategy)


def _pad_address(address: str) -> str:
    """Zero-pad an address to a 32-byte (64 hex char) ABI word."""
    return address.lower().removeprefix("0x").rjust(64, "0")


def _pad_uint(value: int) -> str:
    return hex(value)[2:].rjust(64, "0")


def _hex_to_int(result: str | None) -> int:
    """Parse a hex RPC result; an empty '0x' return (e.g. call to an EOA or
    non-contract address) is treated as 0."""
    if not result or result == "0x":
        return 0
    return int(result, 16)


class RpcError(Exception):
    """Raised when the JSON-RPC endpoint returns an error object."""


class UniblockRpcClient:
    """Minimal JSON-RPC client for Base via Uniblock."""

    def __init__(self, api_key: str, rate_limit_delay: float = 0.15):
        if not api_key:
            raise ValueError("UNIBLOCK_API_KEY is required for RPC access")
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "content-type": "application/json",
        })
        self.session.mount("https://", _build_retry_adapter())
        self._request_id = 0
        # comptroller -> [(market, underlying)] cache (shared across agents in a run)
        self._market_cache: dict[str, list[tuple[str, str | None]]] = {}

    def call(self, method: str, params: list[Any]) -> Any:
        """Raw JSON-RPC call. Returns the 'result' field or raises RpcError."""
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params,
        }
        response = self.session.post(RPC_URL, json=payload, timeout=30)
        response.raise_for_status()
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)
        body = response.json()
        if "error" in body:
            raise RpcError(f"{method} failed: {body['error']}")
        return body.get("result")

    def get_block_number(self) -> int:
        return int(self.call("eth_blockNumber", []), 16)

    def get_eth_balance(self, wallet: str, block: str = "latest") -> int:
        """Native ETH balance in wei."""
        return _hex_to_int(self.call("eth_getBalance", [wallet, block]))

    def get_erc20_balance(self, token: str, wallet: str, block: str = "latest") -> int:
        """ERC-20 balanceOf(wallet) in the token's raw units."""
        data = SEL_BALANCE_OF + _pad_address(wallet)
        return _hex_to_int(self.call("eth_call", [{"to": token, "data": data}, block]))

    def get_vault_assets(
        self, vault: str, wallet: str, block: str = "latest"
    ) -> tuple[int, int]:
        """ERC-4626 vault position: returns (shares, underlying_assets_raw).

        convertToAssets is called with the wallet's share balance, giving the
        current redeemable amount of the underlying token (e.g. USDC).
        """
        shares = self.get_erc20_balance(vault, wallet, block)
        if shares == 0:
            return 0, 0
        data = SEL_CONVERT_TO_ASSETS + _pad_uint(shares)
        result = self.call("eth_call", [{"to": vault, "data": data}, block])
        return shares, _hex_to_int(result)

    # --- Compound-fork (Moonwell etc.) support ---

    def get_markets(self, comptroller: str, block: str = "latest") -> list[tuple[str, str | None]]:
        """Resolve a Compound-fork comptroller to [(mToken, underlying)] pairs.

        getAllMarkets() on the comptroller, then underlying() per market
        (native-ETH markets revert on underlying() -> None). Cached per run.
        """
        key = comptroller.lower()
        if key in self._market_cache:
            return self._market_cache[key]

        result = self.call("eth_call", [{"to": comptroller, "data": SEL_GET_ALL_MARKETS}, block])
        raw = bytes.fromhex(result[2:])
        count = int.from_bytes(raw[32:64], "big")
        markets: list[tuple[str, str | None]] = []
        for i in range(count):
            market = "0x" + raw[64 + i * 32 + 12: 64 + (i + 1) * 32].hex()
            try:
                u = self.call("eth_call", [{"to": market, "data": SEL_UNDERLYING}, block])
                underlying = "0x" + u[-40:] if u and u != "0x" else None
            except RpcError:
                underlying = None
            markets.append((market, underlying))

        self._market_cache[key] = markets
        return markets

    def find_market_for_underlying(self, comptroller: str, underlying_token: str) -> str | None:
        """Find the mToken market whose underlying matches the given token."""
        target = underlying_token.lower()
        for market, underlying in self.get_markets(comptroller):
            if underlying and underlying.lower() == target:
                return market
        return None

    def get_balance_of_underlying(self, market: str, wallet: str, block: str = "latest") -> int:
        """Compound-fork balanceOfUnderlying(wallet) in underlying raw units."""
        data = SEL_BALANCE_OF_UNDERLYING + _pad_address(wallet)
        return _hex_to_int(self.call("eth_call", [{"to": market, "data": data}, block]))
