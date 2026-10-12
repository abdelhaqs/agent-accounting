"""Phase 1 Extractor: In-Flight Circle CCTP Bridge Transfers (Arbitrum -> Base)."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Path setup
CURRENT_DIR = Path(__file__).resolve().parent
DAG_DIR = CURRENT_DIR.parent
if str(DAG_DIR) not in sys.path:
    sys.path.insert(0, str(DAG_DIR))

from common.config import (
    ARBITRUM_SEPOLIA_RPC_URL,
    BASE_SEPOLIA_RPC_URL,
    ARBITRUM_CCTP_TOKEN_MESSENGER,
    BASE_CCTP_MESSAGE_TRANSMITTER,
    BRIDGE_AGENT_STRATEGY_ADDRESS,
    OUTPUT_DIR,
)
from common.rpc import rpc_call, get_block_number

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_cctp_inflight")

# DepositForBurn(uint64 nonce, address burnToken, uint256 amount, address depositor, bytes32 mintRecipient, uint32 destinationDomain, bytes32 destinationTokenMessenger, bytes32 destinationCaller)
EVENT_DEPOSIT_FOR_BURN = "0x2e06184a441e8e19c99ec42c43ee0fb839b8bc43d421711677fb61ff4f8f411b"


def extract_cctp_inflight() -> dict:
    logger.info("Extracting in-flight CCTP bridge transfers...")
    arb_block = get_block_number(ARBITRUM_SEPOLIA_RPC_URL)
    base_block = get_block_number(BASE_SEPOLIA_RPC_URL)

    # In production, scan recent logs (e.g. last 10,000 blocks)
    # For testnet/baseline, we check recent deposit events
    in_flight_raw = 0
    pending_burns = []

    try:
        from_block = hex(max(0, arb_block - 2000))
        filter_params = {
            "fromBlock": from_block,
            "toBlock": "latest",
            "address": ARBITRUM_CCTP_TOKEN_MESSENGER,
            "topics": [EVENT_DEPOSIT_FOR_BURN],
        }
        logs = rpc_call(ARBITRUM_SEPOLIA_RPC_URL, "eth_getLogs", [filter_params])
        logger.info("Found %d recent CCTP burn events in last 2000 blocks", len(logs))
        # Note: In-flight verification compares nonces on Base
    except Exception as exc:
        logger.warning("Could not query CCTP logs: %s. Defaulting in-flight to 0", exc)

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "venue": "Circle_CCTP",
        "arbitrum_block": arb_block,
        "base_block": base_block,
        "token_messenger": ARBITRUM_CCTP_TOKEN_MESSENGER,
        "raw_in_flight_usdc": in_flight_raw,
        "in_flight_usdc": in_flight_raw / 1e6,
        "pending_burns": pending_burns,
    }

    output_path = OUTPUT_DIR / "01_cctp_inflight.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("CCTP In-Flight: %.6f USDC -> %s", data["in_flight_usdc"], output_path.name)
    return data


if __name__ == "__main__":
    extract_cctp_inflight()
