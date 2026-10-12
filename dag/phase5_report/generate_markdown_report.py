"""Phase 5 Reporter: Generate detailed Markdown value check & audit report."""
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

from common.config import PROJECT_ROOT, OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_markdown_report")


def generate_markdown_report() -> Path:
    logger.info("Generating markdown value check report...")

    def _load(f):
        p = OUTPUT_DIR / f
        return json.load(open(p, "r", encoding="utf-8")) if p.exists() else {}

    vault = _load("01_vault_balance.json")
    bridge = _load("01_bridge_balance.json")
    cctp = _load("01_cctp_inflight.json")
    zyfai = _load("01_zyfai_balance.json")
    mamo = _load("01_mamo_balance.json")
    ys = _load("01_yieldseeker_balance.json")
    assets = _load("02_total_assets.json")
    rate = _load("02_derived_rate.json")
    verdict = _load("03_validation_verdict.json")

    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_dir = PROJECT_ROOT / "docs" / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"value_check_report_{now_str}.md"
    latest_file = report_dir / "latest_value_check_report.md"

    md_content = f"""# 📊 Portfolio Value Check & Rate Derivation Report

> **Run Timestamp (UTC)**: `{datetime.now(timezone.utc).isoformat()}`  
> **Circuit Breaker Status**: `{verdict.get('verdict', 'N/A')}`

---

## 🏛️ Venue Breakdown

| Venue / Contract | Network | Balance / NAV (USDC) | Raw Units | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **BoringVault** | Arbitrum Sepolia | `${vault.get('balance_usdc', 0.0):.6f}` | `{vault.get('raw_balance_usdc', 0)}` | Custody & shares |
| **BridgeAgentStrategy** | Arbitrum Sepolia | `${bridge.get('balance_usdc', 0.0):.6f}` | `{bridge.get('raw_balance_usdc', 0)}` | Idle on Hub |
| **Circle CCTP In-Flight** | Cross-Chain | `${cctp.get('in_flight_usdc', 0.0):.6f}` | `{cctp.get('raw_in_flight_usdc', 0)}` | In-transit burns |
| **ZyFAI Base Strategy** | Base Sepolia | `${zyfai.get('total_nav_usdc', 0.0):.6f}` | `{zyfai.get('raw_idle_usdc', 0)}` | Deployed + Stale |
| **Mamo Base Strategy** | Base Sepolia | `${mamo.get('total_nav_usdc', 0.0):.6f}` | `{mamo.get('raw_idle_usdc', 0)}` | Moonwell + Morpho |
| **YieldSeeker Strategy** | Base Sepolia | `${ys.get('total_nav_usdc', 0.0):.6f}` | `{ys.get('raw_idle_usdc', 0)}` | Snapshot NAV |

---

## 🧮 Portfolio Valuation & Rate Derivation

* **Total Gross Assets**: `${assets.get('gross_assets_usdc', 0.0):.6f} USDC`
* **Net Assets (After Venue Fees)**: `${rate.get('net_assets_usdc', 0.0):.6f} USDC`
* **Total Outstanding Shares**: `{rate.get('total_shares', 0.0):.6f} bcUSD`
* **Global Derived Rate**: **`{rate.get('derived_rate_formatted', '1.000000')} USDC / bcUSD`** (`{rate.get('derived_rate_raw', 1000000)}` raw units)

---

## 🛡️ Circuit Breaker & Safety Verdict

* **Allowed to Broadcast**: `{'✅ YES' if verdict.get('can_broadcast') else '❌ NO'}`
* **Rejection Reasons**: `{', '.join(verdict.get('rejection_reasons', [])) or 'None (All checks passed)'}`
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info("Generated markdown reports: %s and %s", report_file.name, latest_file.name)
    return report_file


if __name__ == "__main__":
    generate_markdown_report()
