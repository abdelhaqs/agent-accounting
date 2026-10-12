"""Phase 1 Extractor: YieldSeeker Base Agent Strategy (Idle USDC & Snapshot API NAV)."""
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
    BASE_SEPOLIA_RPC_URL,
    BASE_USDC_ADDRESS,
    YIELDSEEKER_STRATEGY_ADDRESS,
    OUTPUT_DIR,
)
from common.rpc import get_token_balance, get_block_number

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_yieldseeker")


def extract_yieldseeker() -> dict:
    logger.info("Extracting YieldSeeker Strategy balance from Base Sepolia...")
    block = get_block_number(BASE_SEPOLIA_RPC_URL)
    raw_idle = get_token_balance(
        BASE_SEPOLIA_RPC_URL, BASE_USDC_ADDRESS, YIELDSEEKER_STRATEGY_ADDRESS
    )

    # In production, query YieldSeeker Snapshot API (totalValueBase)
    api_nav_raw = 0

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "venue": "YieldSeeker",
        "chain": "base_sepolia",
        "block_number": block,
        "strategy_address": YIELDSEEKER_STRATEGY_ADDRESS,
        "usdc_address": BASE_USDC_ADDRESS,
        "raw_idle_usdc": raw_idle,
        "idle_usdc": raw_idle / 1e6,
        "raw_api_nav_usdc": api_nav_raw,
        "api_nav_usdc": api_nav_raw / 1e6,
        "total_nav_usdc": (raw_idle + api_nav_raw) / 1e6,
    }

    output_path = OUTPUT_DIR / "01_yieldseeker_balance.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("YieldSeeker Total NAV: %.6f USDC -> %s", data["total_nav_usdc"], output_path.name)
    return data


if __name__ == "__main__":
    extract_yieldseeker()
