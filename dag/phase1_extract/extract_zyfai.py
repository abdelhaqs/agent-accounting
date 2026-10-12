"""Phase 1 Extractor: ZyFAI Base Agent Strategy (Idle USDC & Smart Wallet Portfolio)."""
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
    ZYFAI_STRATEGY_ADDRESS,
    OUTPUT_DIR,
)
from common.rpc import get_token_balance, get_block_number

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_zyfai")


def extract_zyfai() -> dict:
    logger.info("Extracting ZyFAI Strategy balance from Base Sepolia...")
    block = get_block_number(BASE_SEPOLIA_RPC_URL)
    raw_idle = get_token_balance(BASE_SEPOLIA_RPC_URL, BASE_USDC_ADDRESS, ZYFAI_STRATEGY_ADDRESS)

    # In production, integrate with ZyFAI SDK (portfolio.balanceWithFee + staleBalances)
    # On testnet, query on-chain strategy wallet
    deployed_raw = 0
    pending_fee_raw = 0

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "venue": "ZyFAI",
        "chain": "base_sepolia",
        "block_number": block,
        "strategy_address": ZYFAI_STRATEGY_ADDRESS,
        "usdc_address": BASE_USDC_ADDRESS,
        "raw_idle_usdc": raw_idle,
        "idle_usdc": raw_idle / 1e6,
        "raw_deployed_usdc": deployed_raw,
        "deployed_usdc": deployed_raw / 1e6,
        "raw_pending_fee_usdc": pending_fee_raw,
        "pending_fee_usdc": pending_fee_raw / 1e6,
        "total_nav_usdc": (raw_idle + deployed_raw - pending_fee_raw) / 1e6,
    }

    output_path = OUTPUT_DIR / "01_zyfai_balance.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("ZyFAI Total NAV: %.6f USDC -> %s", data["total_nav_usdc"], output_path.name)
    return data


if __name__ == "__main__":
    extract_zyfai()
