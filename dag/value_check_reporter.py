"""Automated Markdown Value Check Reporter.

Generates a markdown value check and on-chain reconciliation report
in docs/report/ after each pipeline execution run.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def generate_value_check_report(
    report_dir: Path,
    run_timestamp: str,
    reconciliation: list[dict[str, Any]],
    entries: list[dict[str, Any]] | None = None,
    failed_agents: list[str] | None = None,
    primary_source: str = "uniblock",
    onchain_results: dict[str, dict[str, Any]] | None = None,
) -> Path:
    """Generate and write a value check report markdown file in report_dir."""
    report_dir.mkdir(parents=True, exist_ok=True)
    failed_agents = failed_agents or []
    entries = entries or []
    onchain_results = onchain_results or {}

    # Format human-readable date
    try:
        dt = datetime.strptime(run_timestamp, "%Y%m%d_%H%M%S")
        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        formatted_date = run_timestamp

    # Compute summary statistics
    total_stored_usd = 0.0
    total_onchain_usd = 0.0
    total_unverified_usd = 0.0
    total_same_provider_usd = 0.0

    status_counts: dict[str, int] = {}
    for r in reconciliation:
        st = r.get("status", "UNKNOWN")
        status_counts[st] = status_counts.get(st, 0) + 1
        total_stored_usd += r.get("computed_usd") or 0.0
        total_same_provider_usd += r.get("same_provider_total_usd") or 0.0
        total_onchain_usd += r.get("onchain_total_usd") or 0.0
        total_unverified_usd += r.get("onchain_unverified_usd") or 0.0

    total_agents = len(reconciliation) + len(failed_agents)
    healthy_count = status_counts.get("OK", 0)
    health_pct = (healthy_count / total_agents * 100) if total_agents > 0 else 0.0

    total_covered = total_onchain_usd + total_unverified_usd
    if abs(total_covered) < 1e-9:
        net_delta_pct = 0.0 if abs(total_stored_usd) < 1e-9 else 100.0
    else:
        net_delta_pct = round((total_stored_usd - total_covered) / total_covered * 100, 3)

    lines: list[str] = [
        "# Value Check & On-Chain Reconciliation Report",
        "",
        f"**Execution Run ID:** `{run_timestamp}`  ",
        f"**Run Timestamp:** {formatted_date}  ",
        f"**Primary Source:** **{primary_source.upper()}**  ",
        "**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  ",
        f"**Total Agents Audited:** {total_agents}  ",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"- **Audit Health Score:** **{healthy_count}/{total_agents} Agents Healthy ({health_pct:.1f}%)**",
        f"- **Total Capital Tracked (USD):** **${total_stored_usd:,.2f}**",
        f"- **On-Chain Verified Value:** **${total_onchain_usd:,.2f}**",
        f"- **Unverified / Reward Assets:** **${total_unverified_usd:,.2f}**",
        f"- **Net On-Chain Delta:** **{net_delta_pct:+.3f}%**",
        "",
        "### Status Breakdown:",
        f"- **OK (Healthy):** {status_counts.get('OK', 0)}",
        f"- **MISMATCH:** {status_counts.get('MISMATCH', 0)}",
        f"- **RPC_UNVERIFIED:** {status_counts.get('RPC_UNVERIFIED', 0)}",
        f"- **FAILED:** {len(failed_agents)}",
        "",
        "---",
        "",
        "## 2. Multi-Provider & On-Chain Audit Table",
        "",
        "| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for r in reconciliation:
        name = r.get("agent_name") or r.get("wallet", "Unknown")
        wallet = r.get("wallet", "")
        short_addr = f"`{wallet[:6]}...{wallet[-4:]}`" if len(wallet) >= 10 else f"`{wallet}`"
        provider = r.get("provider", "uniblock")
        stored = f"**${r.get('computed_usd', 0.0):,.2f}**"

        same = f"${r['same_provider_total_usd']:,.2f}" if r.get("same_provider_total_usd") is not None else "n/a"

        onchain_val = r.get("onchain_total_usd")
        onchain_str = f"**${onchain_val:,.2f}**" if onchain_val is not None else "n/a"

        unver_val = r.get("onchain_unverified_usd") or 0.0
        unver_str = f"+${unver_val:,.2f}" if unver_val > 0 else "$0.00"

        delta = r.get("onchain_delta_pct")
        delta_str = f"**{delta:+.3f}%**" if delta is not None else "n/a"

        status = r.get("status", "UNKNOWN")
        status_badge = f"**{status}**" if status == "OK" else f"❌ **{status}**"

        lines.append(
            f"| **{name}** | {short_addr} | {provider} | {stored} | {same} | {onchain_str} | {unver_str} | {delta_str} | {status_badge} |"
        )

    for failed in failed_agents:
        lines.append(f"| **{failed}** | `{failed}` | — | **$0.00** | n/a | n/a | n/a | n/a | ❌ **FAILED** |")

    # Add total row
    lines.append(
        f"| **TOTAL** | — | — | **${total_stored_usd:,.2f}** | **${total_same_provider_usd:,.2f}** | **${total_onchain_usd:,.2f}** | **+${total_unverified_usd:,.2f}** | **{net_delta_pct:+.3f}%** | **{healthy_count}/{total_agents} HEALTHY** |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-Agent Detail Section
    lines.append("## 3. Agent Details & Breakdown")
    lines.append("")
    item_idx = 1
    for r in reconciliation:
        name = r.get("agent_name") or r.get("wallet", "Unknown")
        wallet = r.get("wallet", "").lower()
        lines.append(f"### 3.{item_idx}. {name} (`{wallet}`)")
        item_idx += 1
        lines.append(f"- **Reconciliation Status:** `{r.get('status')}`")
        lines.append(f"- **Stored Pipeline Total:** `${r.get('computed_usd', 0.0):,.2f}`")
        if r.get("onchain_total_usd") is not None:
            lines.append(
                f"- **On-Chain Verified Total:** `${r['onchain_total_usd']:,.2f}` (delta: {r.get('onchain_delta_pct', 0.0):+.3f}%)"
            )
        if r.get("onchain_unverified_usd"):
            lines.append(f"- **Unverified / Reward Assets:** `${r['onchain_unverified_usd']:,.2f}`")

        # Include specific item breakdown if present in onchain_results
        oc = onchain_results.get(wallet)
        if oc and oc.get("details"):
            lines.append("- **Verified Assets Breakdown:**")
            for item in oc["details"]:
                kind = item.get("kind", "asset")
                sym = item.get("symbol") or item.get("underlying_symbol") or "?"
                usd = item.get("usd_value")
                usd_str = f"${usd:,.2f}" if usd is not None else "n/a"
                if kind == "wallet_token":
                    lines.append(f"  - `{sym}`: {usd_str} (wallet token)")
                elif kind == "vault_4626":
                    pool = item.get("pool", "")[:10]
                    lines.append(f"  - `{sym}`: {usd_str} (ERC-4626 vault `{pool}...`)")
                elif kind == "unverified":
                    lines.append(f"  - `{sym}` (unverified/reward): {usd_str}")
        lines.append("")

    report_content = "\n".join(lines) + "\n"

    # Write timestamped report
    report_file = report_dir / f"value_check_report_{run_timestamp}.md"
    report_file.write_text(report_content, encoding="utf-8")
    logger.info("Saved value check report to %s", report_file)

    # Write/update latest_value_check_report.md
    latest_file = report_dir / "latest_value_check_report.md"
    latest_file.write_text(report_content, encoding="utf-8")
    logger.info("Updated latest report at %s", latest_file)

    return report_file
