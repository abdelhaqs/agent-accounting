"""Phase 4 Simulator: Simulate updateExchangeRate transaction via eth_call (Dry-Run)."""
from __future__ import annotations

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
logger = logging.getLogger("simulate_tx")


def simulate_broadcast() -> dict:
    logger.info("Simulating updateExchangeRate call on Arbitrum Sepolia (Dry-Run)...")

    rate_path = OUTPUT_DIR / "02_derived_rate.json"
    if not rate_path.exists():
        logger.error("02_derived_rate.json missing. Run derive_share_rate first.")
        raise FileNotFoundError("Missing 02_derived_rate.json")

    with open(rate_path, "r", encoding="utf-8") as f:
        rate_data = json.load(f)

    rate_raw = rate_data.get("derived_rate_raw", 1_000_000)

    # Derive keeper address from private key using cast
    try:
        wallet_cmd = ["cast", "wallet", "address", "--private-key", KEEPER_PRIVATE_KEY]
        keeper_address = subprocess.check_output(wallet_cmd, text=True).strip()
    except Exception as exc:
        logger.warning("Could not derive keeper address: %s", exc)
        keeper_address = "0xe8a7bA64913127AF7e47bF4ca4975Bb846a747F8"

    # Simulate via cast call
    call_cmd = [
        "cast", "call",
        "--rpc-url", ARBITRUM_SEPOLIA_RPC_URL,
        ACCOUNTANT_ADDRESS,
        "updateExchangeRate(uint96)",
        str(rate_raw),
        "--from", keeper_address,
    ]

    sim_success = False
    error_msg = None
    output_raw = ""

    try:
        proc = subprocess.run(call_cmd, capture_output=True, text=True, check=False)
        output_raw = proc.stdout.strip() or proc.stderr.strip()
        sim_success = proc.returncode == 0
        if not sim_success:
            error_msg = proc.stderr.strip()
    except Exception as exc:
        error_msg = str(exc)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "accountant_address": ACCOUNTANT_ADDRESS,
        "simulated_by": keeper_address,
        "proposed_rate_raw": rate_raw,
        "proposed_rate": rate_raw / 1e6,
        "simulation_passed": sim_success,
        "output": output_raw,
        "error": error_msg,
    }

    output_path = OUTPUT_DIR / "04_simulation_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if sim_success:
        logger.info("🟢 Simulation PASSED (Transaction will succeed on-chain) -> %s", output_path.name)
    else:
        logger.warning("🔴 Simulation REVERTED: %s -> %s", error_msg, output_path.name)
    return result


if __name__ == "__main__":
    simulate_broadcast()
