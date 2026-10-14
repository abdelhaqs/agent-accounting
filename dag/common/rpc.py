"""JSON-RPC client helper for multi-chain queries."""
from __future__ import annotations

import logging
from typing import Any
import requests

import urllib3
urllib3.disable_warnings()

logger = logging.getLogger(__name__)

# Function selectors
SEL_BALANCE_OF = "0x70a08231"               # balanceOf(address)
SEL_TOTAL_SUPPLY = "0x18160ddd"             # totalSupply()
SEL_GET_RATE = "0x679aefce"                 # getRate()
SEL_CONVERT_TO_ASSETS = "0x07a2d13a"        # convertToAssets(uint256)
SEL_BALANCE_OF_UNDERLYING = "0x3af9e669"    # balanceOfUnderlying(address)
SEL_ACCOUNTANT_STATE = "0x433255de"         # accountantState()
SEL_UPDATE_EXCHANGE_RATE = "0x89791176"     # updateExchangeRate(uint96)


def _pad_address(address: str) -> str:
    clean = address.lower().replace("0x", "")
    return clean.rjust(64, "0")


def _pad_uint(value: int) -> str:
    return hex(value)[2:].rjust(64, "0")


def rpc_call(rpc_url: str, method: str, params: list[Any]) -> Any:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    resp = requests.post(rpc_url, json=payload, headers=headers, verify=False, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC Error ({rpc_url}): {data['error']}")
    return data.get("result")


def get_block_number(rpc_url: str) -> int:
    res = rpc_call(rpc_url, "eth_blockNumber", [])
    return int(res, 16)


def eth_call(rpc_url: str, to: str, data: str, block: str = "latest") -> str:
    return rpc_call(rpc_url, "eth_call", [{"to": to, "data": data}, block])


def get_token_balance(rpc_url: str, token: str, owner: str) -> int:
    call_data = SEL_BALANCE_OF + _pad_address(owner)
    res = eth_call(rpc_url, to=token, data=call_data)
    if not res or res == "0x":
        return 0
    return int(res, 16)


def get_total_supply(rpc_url: str, token: str) -> int:
    res = eth_call(rpc_url, to=token, data=SEL_TOTAL_SUPPLY)
    if not res or res == "0x":
        return 0
    return int(res, 16)


def get_accountant_rate(rpc_url: str, accountant: str) -> int:
    res = eth_call(rpc_url, to=accountant, data=SEL_GET_RATE)
    if not res or res == "0x":
        return 0
    return int(res, 16)


def get_accountant_state(rpc_url: str, accountant: str) -> dict[str, Any]:
    """Decodes AccountantState struct from AccountantWithRateProviders."""
    res = eth_call(rpc_url, to=accountant, data=SEL_ACCOUNTANT_STATE)
    if not res or len(res) < 66:
        return {}
    raw = res[2:]
    chunks = [raw[i:i+64] for i in range(0, len(raw), 64)]
    if len(chunks) < 9:
        return {}
    return {
        "payoutAddress": "0x" + chunks[0][24:],
        "highwaterMark": int(chunks[1], 16),
        "feesOwedInBase": int(chunks[2], 16),
        "totalSharesLastUpdate": int(chunks[3], 16),
        "exchangeRate": int(chunks[4], 16),
        "allowedExchangeRateChangeUpper": int(chunks[5], 16),
        "allowedExchangeRateChangeLower": int(chunks[6], 16),
        "lastUpdateTimestamp": int(chunks[7], 16),
        "isPaused": bool(int(chunks[8], 16)),
        "minimumUpdateDelayInSeconds": int(chunks[9], 16) if len(chunks) > 9 else 3600,
    }
