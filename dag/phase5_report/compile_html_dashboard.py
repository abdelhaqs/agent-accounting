"""Phase 5 Reporter: Compile interactive HTML audit dashboard and update usdc_balance_data.json."""
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
logger = logging.getLogger("compile_html_dashboard")


def compile_html_dashboard() -> Path:
    logger.info("Compiling latest HTML audit dashboard...")

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

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Bond App Testnet - Multi-Agent Accounting Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .header {{ border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
    .title {{ font-size: 24px; font-weight: bold; color: #38bdf8; }}
    .status {{ padding: 6px 12px; border-radius: 9999px; font-size: 14px; font-weight: 600; }}
    .status-ok {{ background: #064e3b; color: #34d399; }}
    .status-warn {{ background: #78350f; color: #fbbf24; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; }}
    .card-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; }}
    .card-value {{ font-size: 22px; font-weight: bold; color: #f1f5f9; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ background: #0f172a; color: #94a3b8; font-size: 13px; text-transform: uppercase; }}
    .badge {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }}
    .badge-arb {{ background: #1e3a8a; color: #93c5fd; }}
    .badge-base {{ background: #14532d; color: #86efac; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div class="title">Bond App Testnet — 360° Treasury Audit</div>
        <div style="font-size: 13px; color: #64748b; margin-top: 4px;">Last Synced: {now_iso}</div>
      </div>
      <div class="status {'status-ok' if verdict.get('can_broadcast') else 'status-warn'}">
        {verdict.get('verdict', 'NORMAL')}
      </div>
    </div>

    <div class="cards">
      <div class="card">
        <div class="card-label">Total Protocol Assets</div>
        <div class="card-value">${assets.get('gross_assets_usdc', 0.0):.2f} USDC</div>
      </div>
      <div class="card">
        <div class="card-label">Total Shares Issued</div>
        <div class="card-value">{rate.get('total_shares', 0.0):.2f} bcUSD</div>
      </div>
      <div class="card">
        <div class="card-label">Global Exchange Rate</div>
        <div class="card-value">${rate.get('derived_rate_formatted', '1.000000')}</div>
      </div>
      <div class="card">
        <div class="card-label">BoringVault Balance</div>
        <div class="card-value">${vault.get('balance_usdc', 0.0):.2f} USDC</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Venue / Contract</th>
          <th>Network</th>
          <th>Role</th>
          <th>USDC Balance / NAV</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>BoringVault</strong></td>
          <td><span class="badge badge-arb">Arbitrum Sepolia</span></td>
          <td>Vault & Custody</td>
          <td><strong>${vault.get('balance_usdc', 0.0):.6f}</strong></td>
          <td>Active</td>
        </tr>
        <tr>
          <td><strong>BridgeAgentStrategy</strong></td>
          <td><span class="badge badge-arb">Arbitrum Sepolia</span></td>
          <td>Bridge Escrow (Hub)</td>
          <td>${bridge.get('balance_usdc', 0.0):.6f}</td>
          <td>Active</td>
        </tr>
        <tr>
          <td><strong>Circle CCTP In-Flight</strong></td>
          <td><span class="badge badge-arb">Cross-Chain</span></td>
          <td>In-Transit Burns</td>
          <td>${cctp.get('in_flight_usdc', 0.0):.6f}</td>
          <td>Synchronized</td>
        </tr>
        <tr>
          <td><strong>ZyFAI Agent Strategy</strong></td>
          <td><span class="badge badge-base">Base Sepolia</span></td>
          <td>AI Yield Venue</td>
          <td>${zyfai.get('total_nav_usdc', 0.0):.6f}</td>
          <td>Active</td>
        </tr>
        <tr>
          <td><strong>Mamo Agent Strategy</strong></td>
          <td><span class="badge badge-base">Base Sepolia</span></td>
          <td>Morpho & Moonwell</td>
          <td>${mamo.get('total_nav_usdc', 0.0):.6f}</td>
          <td>Active</td>
        </tr>
        <tr>
          <td><strong>YieldSeeker Strategy</strong></td>
          <td><span class="badge badge-base">Base Sepolia</span></td>
          <td>Dynamic DeFi Venue</td>
          <td>${ys.get('total_nav_usdc', 0.0):.6f}</td>
          <td>Active</td>
        </tr>
      </tbody>
    </table>
  </div>
</body>
</html>
"""

    dashboard_path = PROJECT_ROOT / "docs" / "report" / "latest_audit_dashboard.html"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Also update usdc_balance_data.json
    balance_json_path = PROJECT_ROOT / "usdc_balance_data.json"
    chart_entry = {
        "timestamp": now_iso,
        "total_usdc": assets.get("gross_assets_usdc", 0.0),
        "total_shares": rate.get("total_shares", 0.0),
        "exchange_rate": rate.get("derived_rate", 1.0),
        "breakdown": {
            "vault": vault.get("balance_usdc", 0.0),
            "bridge": bridge.get("balance_usdc", 0.0),
            "cctp_inflight": cctp.get("in_flight_usdc", 0.0),
            "zyfai": zyfai.get("total_nav_usdc", 0.0),
            "mamo": mamo.get("total_nav_usdc", 0.0),
            "yieldseeker": ys.get("total_nav_usdc", 0.0),
        },
    }
    with open(balance_json_path, "w", encoding="utf-8") as f:
        json.dump([chart_entry], f, indent=2)

    logger.info("Compiled HTML dashboard: %s", dashboard_path.name)
    return dashboard_path


if __name__ == "__main__":
    compile_html_dashboard()
