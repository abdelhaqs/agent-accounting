"""Phase 4 Broadcaster: Execute on-chain keeper transaction to AccountantWithRateProviders."""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
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
    ACCOUNTANT_ADDRESS,
    KEEPER_PRIVATE_KEY,
    OUTPUT_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("broadcast_rate")


def broadcast_rate(force: bool = False) -> dict:
    logger.info("Preparing to broadcast updated exchange rate to AccountantWithRateProviders...")

    verdict_path = OUTPUT_DIR / "03_validation_verdict.json"
    if not verdict_path.exists():
        logger.error("03_validation_verdict.json missing. Run circuit_breaker first.")
        raise FileNotFoundError("Missing validation verdict artifact.")

    with open(verdict_path, "r", encoding="utf-8") as f:
        verdict = json.load(f)

    can_broadcast = verdict.get("can_broadcast", False)
    if not can_broadcast and not force:
        logger.error(
            "BROADCAST BLOCKED by Circuit Breaker: %s. Use --force to override.",
            verdict.get("rejection_reasons"),
        )
        return {
            "status": "BLOCKED_BY_CIRCUIT_BREAKER",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reasons": verdict.get("rejection_reasons"),
        }

    rate_raw = verdict.get("proposed_rate_raw", 1_000_000)

    send_cmd = [
        "cast", "send",
        "--rpc-url", ARBITRUM_SEPOLIA_RPC_URL,
        "--private-key", KEEPER_PRIVATE_KEY,
        ACCOUNTANT_ADDRESS,
        "updateExchangeRate(uint96)",
        str(rate_raw),
        "--json",
    ]

    logger.info("Broadcasting transaction to Arbitrum Sepolia with new rate: %d...", rate_raw)
    proc = subprocess.run(send_cmd, capture_output=True, text=True, check=False)

    tx_hash = None
    receipt_data = {}
    success = proc.returncode == 0

    if success:
        try:
            receipt_data = json.loads(proc.stdout)
            tx_hash = receipt_data.get("transactionHash")
            logger.info("✅ Rate updated successfully! Tx Hash: %s", tx_hash)
        except Exception:
            tx_hash = proc.stdout.strip()
    else:
        logger.error("❌ Broadcast failed: %s", proc.stderr.strip())

    receipt_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "SUCCESS" if success else "FAILED",
        "accountant_address": ACCOUNTANT_ADDRESS,
        "proposed_rate_raw": rate_raw,
        "proposed_rate": rate_raw / 1e6,
        "transaction_hash": tx_hash,
        "error": None if success else proc.stderr.strip(),
        "receipt": receipt_data,
    }

    output_path = OUTPUT_DIR / "04_tx_receipt.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(receipt_record, f, indent=2)

    return receipt_record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broadcast rate to Accountant")
    parser.add_argument("--force", action="store_true", help="Force broadcast even if circuit breaker warned")
    args = parser.parse_args()
    broadcast_rate(force=args.force)
