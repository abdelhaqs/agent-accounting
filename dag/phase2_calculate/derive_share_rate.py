"""Phase 2 Calculator: Derive Global Share Exchange Rate (Net Assets / Total Shares)."""
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

from common.config import OUTPUT_DIR, ONE_SHARE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("derive_share_rate")


def derive_share_rate() -> dict:
    logger.info("Deriving share exchange rate...")

    net_path = OUTPUT_DIR / "02_net_assets.json"
    vault_path = OUTPUT_DIR / "01_vault_balance.json"

    if not net_path.exists() or not vault_path.exists():
        logger.error("Required artifacts missing (02_net_assets.json or 01_vault_balance.json).")
        raise FileNotFoundError("Missing prerequisite artifacts.")

    with open(net_path, "r", encoding="utf-8") as f:
        net_data = json.load(f)
    with open(vault_path, "r", encoding="utf-8") as f:
        vault_data = json.load(f)

    net_assets_raw = net_data.get("net_assets_raw", 0)
    net_assets_usdc = net_data.get("net_assets_usdc", 0.0)
    total_shares_raw = vault_data.get("raw_total_shares", 0)
    total_shares = vault_data.get("total_shares", 0.0)

    # Derive rate: (net_assets_raw * ONE_SHARE) / total_shares_raw
    if total_shares_raw <= 0:
        logger.warning("Total shares is 0. Using baseline 1:1 rate (1.000000).")
        derived_rate_raw = ONE_SHARE
        derived_rate = 1.0
    else:
        derived_rate_raw = (net_assets_raw * ONE_SHARE) // total_shares_raw
        derived_rate = derived_rate_raw / 1e6

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "net_assets_usdc": net_assets_usdc,
        "net_assets_raw": net_assets_raw,
        "total_shares": total_shares,
        "total_shares_raw": total_shares_raw,
        "derived_rate": derived_rate,
        "derived_rate_raw": derived_rate_raw,
        "derived_rate_formatted": f"{derived_rate:.6f}",
    }

    output_path = OUTPUT_DIR / "02_derived_rate.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info(
        "Derived Rate: %s USDC/share ($%.2f assets / %.2f shares) -> %s",
        data["derived_rate_formatted"],
        net_assets_usdc,
        total_shares,
        output_path.name,
    )
    return data


if __name__ == "__main__":
    derive_share_rate()
