# Value Check & Reconciliation Reports (`docs/report/`)

This directory contains automated **Value Check & On-Chain Reconciliation Reports** generated in Markdown (`.md`) format after each pipeline execution run.

---

## 🎯 Purpose of Value Check Reports

Every time the accounting pipeline executes, it performs a 2-layer ground truth audit:
1. **API Ingestion:** Pulls token balances and transfers via **Uniblock Direct API (DeBank)**.
2. **On-Chain Cross-Check:** Independently queries the **Base blockchain via JSON-RPC** (`https://mainnet.base.org`), querying ERC-20 `balanceOf` and ERC-4626 vault share assets (e.g. Morpho).

The resulting values are cross-referenced against a strict tolerance:
- **`OK`**: Stored USD value matches on-chain ground truth within **1% or $1.00**.
- **`MISMATCH`**: Difference exceeds 1% and $1.00.
- **`RPC_UNVERIFIED`**: Positions exist that could not be queried on-chain.
- **`FAILED`**: Agent processing aborted due to upstream network or formatting issues.

---

## 📂 Report Files

- **`latest_value_check_report.md`**: Always contains the most recent execution audit report.
- **`value_check_report_<timestamp>.md`**: Timestamped immutable historical audit reports (e.g., `value_check_report_20260927_130618.md`).

---

## 📊 Viewing Reports as an HTML Dashboard

You can compile the latest markdown report into a standalone interactive HTML dashboard at any time:

```powershell
# Windows
.\task.ps1 report

# Linux / macOS
python dag/generate_html_report.py
```

The resulting dashboard will be saved to `docs/report/latest_audit_dashboard.html`.
