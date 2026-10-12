"""Phase 2 Calculator: Deduct Pending Protocol & Venue Fees from Gross Assets."""
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
logger = logging.getLogger("deduct_venue_fees")


def deduct_venue_fees() -> dict:
    logger.info("Deducting pending venue fees from gross assets...")

    agg_path = OUTPUT_DIR / "02_total_assets.json"
    if not agg_path.exists():
        logger.error("02_total_assets.json missing. Run aggregate_assets first.")
        raise FileNotFoundError(f"{agg_path} does not exist.")

    with open(agg_path, "r", encoding="utf-8") as f:
        agg_data = json.load(f)

    gross_usdc = agg_data.get("gross_assets_usdc", 0.0)

    # In production, check pending fees in ZyFAI / Mamo
    zyfai_fee = 0.0
    zyfai_path = OUTPUT_DIR / "01_zyfai_balance.json"
    if zyfai_path.exists():
        with open(zyfai_path, "r", encoding="utf-8") as f:
            z_data = json.load(f)
            zyfai_fee = z_data.get("pending_fee_usdc", 0.0)

    total_fees_usdc = zyfai_fee
    net_assets_usdc = max(0.0, gross_usdc - total_fees_usdc)
    net_assets_raw = int(round(net_assets_usdc * 1e6))

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gross_assets_usdc": gross_usdc,
        "total_fees_deducted_usdc": total_fees_usdc,
        "net_assets_usdc": net_assets_usdc,
        "net_assets_raw": net_assets_raw,
    }

    output_path = OUTPUT_DIR / "02_net_assets.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("Net Assets (after fees): $%.6f USDC -> %s", net_assets_usdc, output_path.name)
    return data


if __name__ == "__main__":
    deduct_venue_fees()
