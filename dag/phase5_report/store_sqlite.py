"""Phase 5 Reporter: Store calculation & balance snapshot in local SQLite database."""
from __future__ import annotations

import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Path setup
CURRENT_DIR = Path(__file__).resolve().parent
DAG_DIR = CURRENT_DIR.parent
if str(DAG_DIR) not in sys.path:
    sys.path.insert(0, str(DAG_DIR))

from common.config import PROJECT_ROOT, OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("store_sqlite")


def store_sqlite(db_path: Path | None = None) -> None:
    if db_path is None:
        db_path = PROJECT_ROOT / "accounting.db"

    logger.info("Recording accounting snapshot into SQLite (%s)...", db_path.name)

    rate_path = OUTPUT_DIR / "02_derived_rate.json"
    assets_path = OUTPUT_DIR / "02_total_assets.json"

    if not rate_path.exists() or not assets_path.exists():
        logger.warning("Calculation artifacts missing. Skipping SQLite record.")
        return

    with open(rate_path, "r", encoding="utf-8") as f:
        rate_data = json.load(f)
    with open(assets_path, "r", encoding="utf-8") as f:
        assets_data = json.load(f)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rate_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            gross_assets_usdc REAL NOT NULL,
            net_assets_usdc REAL NOT NULL,
            total_shares REAL NOT NULL,
            derived_rate REAL NOT NULL,
            raw_rate INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        INSERT INTO rate_history (
            timestamp, gross_assets_usdc, net_assets_usdc, total_shares, derived_rate, raw_rate
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            assets_data.get("gross_assets_usdc", 0.0),
            rate_data.get("net_assets_usdc", 0.0),
            rate_data.get("total_shares", 0.0),
            rate_data.get("derived_rate", 1.0),
            rate_data.get("derived_rate_raw", 1_000_000),
        ),
    )

    conn.commit()
    conn.close()
    logger.info("Successfully saved snapshot to SQLite rate_history table.")


if __name__ == "__main__":
    store_sqlite()
