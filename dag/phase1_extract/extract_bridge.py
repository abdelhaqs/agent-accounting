"""Phase 1 Extractor: BridgeAgentStrategy Idle USDC on Arbitrum Sepolia."""
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
    ARBITRUM_USDC_ADDRESS,
    BRIDGE_AGENT_STRATEGY_ADDRESS,
    OUTPUT_DIR,
)
from common.rpc import get_token_balance, get_block_number

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_bridge")


def extract_bridge() -> dict:
    logger.info("Extracting BridgeAgentStrategy balance from Arbitrum Sepolia...")
    block = get_block_number(ARBITRUM_SEPOLIA_RPC_URL)
    raw_usdc = get_token_balance(
        ARBITRUM_SEPOLIA_RPC_URL, ARBITRUM_USDC_ADDRESS, BRIDGE_AGENT_STRATEGY_ADDRESS
    )

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "venue": "BridgeAgentStrategy",
        "chain": "arbitrum_sepolia",
        "block_number": block,
        "strategy_address": BRIDGE_AGENT_STRATEGY_ADDRESS,
        "usdc_address": ARBITRUM_USDC_ADDRESS,
        "raw_balance_usdc": raw_usdc,
        "balance_usdc": raw_usdc / 1e6,
    }

    output_path = OUTPUT_DIR / "01_bridge_balance.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("Bridge Idle: %.6f USDC -> %s", data["balance_usdc"], output_path.name)
    return data


if __name__ == "__main__":
    extract_bridge()
