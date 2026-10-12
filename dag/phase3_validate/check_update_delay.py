"""Phase 3 Validator: Check if minimum update delay has elapsed on Accountant."""
from __future__ import annotations

import json
import logging
import sys
import time
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
logger = logging.getLogger("check_update_delay")


def check_update_delay() -> dict:
    logger.info("Checking minimum update delay on AccountantWithRateProviders...")
    state = get_accountant_state(ARBITRUM_SEPOLIA_RPC_URL, ACCOUNTANT_ADDRESS)

    last_update = state.get("lastUpdateTimestamp", 0)
    delay_seconds = state.get("minimumUpdateDelayInSeconds", 3600)
    current_time = int(time.time())

    next_valid_time = last_update + delay_seconds
    seconds_remaining = max(0, next_valid_time - current_time)
    delay_elapsed = current_time >= next_valid_time

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "accountant_address": ACCOUNTANT_ADDRESS,
        "current_timestamp": current_time,
        "last_update_timestamp": last_update,
        "minimum_update_delay_seconds": delay_seconds,
        "next_valid_update_timestamp": next_valid_time,
        "seconds_remaining": seconds_remaining,
        "delay_elapsed": delay_elapsed,
        "status": "PASSED" if delay_elapsed else "WAITING_DELAY",
    }

    output_path = OUTPUT_DIR / "03_check_delay.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    if delay_elapsed:
        logger.info("Delay Check: PASSED (Delay of %ds has elapsed) -> %s", delay_seconds, output_path.name)
    else:
        logger.warning(
            "Delay Check: NOT ELAPSED (%d seconds remaining before next update permitted) -> %s",
            seconds_remaining,
            output_path.name,
        )
    return data


if __name__ == "__main__":
    check_update_delay()
