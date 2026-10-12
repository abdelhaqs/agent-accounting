"""Phase 3 Gatekeeper: Final Circuit Breaker Evaluation (Go / No-Go Verdict)."""
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

from common.config import OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("circuit_breaker")


def evaluate_circuit_breaker() -> dict:
    logger.info("Evaluating circuit breaker conditions for on-chain broadcast...")

    delay_path = OUTPUT_DIR / "03_check_delay.json"
    bounds_path = OUTPUT_DIR / "03_check_bounds.json"

    if not delay_path.exists() or not bounds_path.exists():
        logger.error("Validation checks incomplete. Missing 03_check_delay or 03_check_bounds.")
        raise FileNotFoundError("Missing validation check artifacts.")

    with open(delay_path, "r", encoding="utf-8") as f:
        delay_data = json.load(f)
    with open(bounds_path, "r", encoding="utf-8") as f:
        bounds_data = json.load(f)

    delay_passed = delay_data.get("delay_elapsed", False)
    bounds_passed = bounds_data.get("within_bounds", False)

    reasons = []
    if not delay_passed:
        reasons.append(f"Minimum update delay not elapsed ({delay_data.get('seconds_remaining', 0)}s left)")
    if not bounds_passed:
        reasons.append("Proposed rate is outside allowed change bounds")

    can_broadcast = delay_passed and bounds_passed

    verdict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "can_broadcast": can_broadcast,
        "verdict": "APPROVED_FOR_BROADCAST" if can_broadcast else "REJECTED_BY_CIRCUIT_BREAKER",
        "delay_check_passed": delay_passed,
        "bounds_check_passed": bounds_passed,
        "rejection_reasons": reasons,
        "proposed_rate": bounds_data.get("proposed_rate"),
        "proposed_rate_raw": bounds_data.get("proposed_rate_raw"),
    }

    output_path = OUTPUT_DIR / "03_validation_verdict.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    if can_broadcast:
        logger.info("🟢 CIRCUIT BREAKER: APPROVED (Safe to broadcast) -> %s", output_path.name)
    else:
        logger.warning("🔴 CIRCUIT BREAKER: HALTED (%s) -> %s", ", ".join(reasons), output_path.name)
    return verdict


if __name__ == "__main__":
    evaluate_circuit_breaker()
