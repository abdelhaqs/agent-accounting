"""Phase 1 Extractor: BoringVault Idle USDC & Total Share Supply on Arbitrum Sepolia."""
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
    BORING_VAULT_ADDRESS,
    ACCOUNTANT_ADDRESS,
    OUTPUT_DIR,
)
from common.rpc import get_token_balance, get_total_supply, get_accountant_rate, get_block_number

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_vault")


def extract_vault() -> dict:
    logger.info("Extracting BoringVault balance from Arbitrum Sepolia...")
    block = get_block_number(ARBITRUM_SEPOLIA_RPC_URL)
    raw_usdc = get_token_balance(ARBITRUM_SEPOLIA_RPC_URL, ARBITRUM_USDC_ADDRESS, BORING_VAULT_ADDRESS)
    raw_shares = get_total_supply(ARBITRUM_SEPOLIA_RPC_URL, BORING_VAULT_ADDRESS)
    raw_rate = get_accountant_rate(ARBITRUM_SEPOLIA_RPC_URL, ACCOUNTANT_ADDRESS)

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "venue": "BoringVault",
        "chain": "arbitrum_sepolia",
        "block_number": block,
        "vault_address": BORING_VAULT_ADDRESS,
        "usdc_address": ARBITRUM_USDC_ADDRESS,
        "raw_balance_usdc": raw_usdc,
        "balance_usdc": raw_usdc / 1e6,
        "raw_total_shares": raw_shares,
        "total_shares": raw_shares / 1e6,
        "current_onchain_rate": raw_rate / 1e6,
    }

    output_path = OUTPUT_DIR / "01_vault_balance.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info(
        "Vault: %.6f USDC | Shares: %.6f bcUSD | Rate: %.6f -> %s",
        data["balance_usdc"],
        data["total_shares"],
        data["current_onchain_rate"],
        output_path.name,
    )
    return data


if __name__ == "__main__":
    extract_vault()
