"""Phase 2 Calculator: Aggregate Multi-Chain Gross Assets across Hub & Spokes."""
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
logger = logging.getLogger("aggregate_assets")


def _read_json(filename: str, fallback_key: str = "balance_usdc") -> dict:
    path = OUTPUT_DIR / filename
    if not path.exists():
        logger.warning("Artifact %s not found. Using zero balance.", filename)
        return {fallback_key: 0.0, "raw_" + fallback_key: 0}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def aggregate_assets() -> dict:
    logger.info("Aggregating assets across all venue extraction artifacts...")

    vault_data = _read_json("01_vault_balance.json")
    bridge_data = _read_json("01_bridge_balance.json")
    cctp_data = _read_json("01_cctp_inflight.json", fallback_key="in_flight_usdc")
    zyfai_data = _read_json("01_zyfai_balance.json", fallback_key="total_nav_usdc")
    mamo_data = _read_json("01_mamo_balance.json", fallback_key="total_nav_usdc")
    ys_data = _read_json("01_yieldseeker_balance.json", fallback_key="total_nav_usdc")

    vault_usdc = vault_data.get("balance_usdc", 0.0)
    bridge_usdc = bridge_data.get("balance_usdc", 0.0)
    cctp_usdc = cctp_data.get("in_flight_usdc", 0.0)
    zyfai_usdc = zyfai_data.get("total_nav_usdc", 0.0)
    mamo_usdc = mamo_data.get("total_nav_usdc", 0.0)
    ys_usdc = ys_data.get("total_nav_usdc", 0.0)

    total_gross_usdc = vault_usdc + bridge_usdc + cctp_usdc + zyfai_usdc + mamo_usdc + ys_usdc
    total_gross_raw = int(round(total_gross_usdc * 1e6))

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gross_assets_usdc": total_gross_usdc,
        "gross_assets_raw": total_gross_raw,
        "breakdown": {
            "vault_usdc": vault_usdc,
            "bridge_usdc": bridge_usdc,
            "cctp_inflight_usdc": cctp_usdc,
            "zyfai_usdc": zyfai_usdc,
            "mamo_usdc": mamo_usdc,
            "yieldseeker_usdc": ys_usdc,
        },
    }

    output_path = OUTPUT_DIR / "02_total_assets.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("Total Gross Assets: $%.6f USDC -> %s", total_gross_usdc, output_path.name)
    return data


if __name__ == "__main__":
    aggregate_assets()
