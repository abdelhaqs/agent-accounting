"""Phase 3 Validator: Check if candidate rate is within Accountant rate change bounds."""
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

from common.config import ARBITRUM_SEPOLIA_RPC_URL, ACCOUNTANT_ADDRESS, OUTPUT_DIR
from common.rpc import get_accountant_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("check_rate_bounds")


def check_rate_bounds() -> dict:
    logger.info("Checking candidate rate bounds against AccountantWithRateProviders...")

    rate_path = OUTPUT_DIR / "02_derived_rate.json"
    if not rate_path.exists():
        logger.error("02_derived_rate.json missing. Run derive_share_rate first.")
        raise FileNotFoundError(f"{rate_path} does not exist.")

    with open(rate_path, "r", encoding="utf-8") as f:
        rate_data = json.load(f)

    proposed_rate_raw = rate_data.get("derived_rate_raw", 1_000_000)
    proposed_rate = rate_data.get("derived_rate", 1.0)

    state = get_accountant_state(ARBITRUM_SEPOLIA_RPC_URL, ACCOUNTANT_ADDRESS)
    current_rate_raw = state.get("exchangeRate", 1_000_000)
    current_rate = current_rate_raw / 1e6
    upper_bound_bps = state.get("allowedExchangeRateChangeUpper", 10050)
    lower_bound_bps = state.get("allowedExchangeRateChangeLower", 9950)

    # Upper and lower thresholds: (current_rate * bound_bps) / 10000
    max_allowed_rate_raw = (current_rate_raw * upper_bound_bps) // 10000
    min_allowed_rate_raw = (current_rate_raw * lower_bound_bps) // 10000

    within_upper = proposed_rate_raw <= max_allowed_rate_raw
    within_lower = proposed_rate_raw >= min_allowed_rate_raw
    within_bounds = within_upper and within_lower

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "accountant_address": ACCOUNTANT_ADDRESS,
        "current_onchain_rate": current_rate,
        "current_onchain_rate_raw": current_rate_raw,
        "proposed_rate": proposed_rate,
        "proposed_rate_raw": proposed_rate_raw,
        "upper_bound_bps": upper_bound_bps,
        "lower_bound_bps": lower_bound_bps,
        "min_allowed_rate": min_allowed_rate_raw / 1e6,
        "max_allowed_rate": max_allowed_rate_raw / 1e6,
        "within_bounds": within_bounds,
        "status": "PASSED" if within_bounds else "OUT_OF_BOUNDS",
    }

    output_path = OUTPUT_DIR / "03_check_bounds.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    if within_bounds:
        logger.info(
            "Rate Bounds Check: PASSED (%.6f is within [%.6f, %.6f]) -> %s",
            proposed_rate,
            min_allowed_rate_raw / 1e6,
            max_allowed_rate_raw / 1e6,
            output_path.name,
        )
    else:
        logger.warning(
            "Rate Bounds Check: OUT OF BOUNDS! (%.6f outside [%.6f, %.6f]) -> %s",
            proposed_rate,
            min_allowed_rate_raw / 1e6,
            max_allowed_rate_raw / 1e6,
            output_path.name,
        )
    return data


if __name__ == "__main__":
    check_rate_bounds()
