"""Aggregate USDC balances from archived balance snapshots for the dashboard.

Reads *_balances_YYYYMMDD_HHMMSS.json files from archive_downloads/full_archive,
sums usd_value of all USDC rows per agent per snapshot, drops near-duplicate
rows within a snapshot (same position double-inserted with tiny value noise),
keeps only the last snapshot per agent per day (some days have multiple
snapshots), and writes:

  1. usdc_balance_data.json  - the aggregated data (live source for the chart)
  2. patches the EMBEDDED_DATA fallback inside usdc_balance_chart.html so the
     dashboard still works when opened directly from disk (file:// fetch of
     JSON is blocked by browsers; in that case the embedded snapshot is used).
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
ARCHIVE_DIR = ROOT / "archive_downloads" / "full_archive"
OUTPUT_JSON = ROOT / "usdc_balance_data.json"
DASHBOARD = ROOT / "usdc_balance_chart.html"

# matches: <anything>_balances_20260902_210815.json
BALANCE_FILE_RE = re.compile(r"^(?P<prefix>.+)_balances_(?P<ts>\d{8}_\d{6})\.json$")


def file_timestamp(ts: str) -> str:
    """'20260902_210815' -> '2026-09-02 21:08:15'"""
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[9:11]}:{ts[11:13]}:{ts[13:15]}"


def main() -> None:
    records = []
    files = sorted(ARCHIVE_DIR.glob("*_balances_*.json"))
    if not files:
        raise SystemExit(f"No balance files found in {ARCHIVE_DIR}")

    for path in files:
        m = BALANCE_FILE_RE.match(path.name)
        if not m:
            print(f"  skipping (no timestamp in name): {path.name}")
            continue
        ts = file_timestamp(m.group("ts"))
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  skipping (invalid JSON): {path.name} ({e})")
            continue
        if not isinstance(rows, list):
            print(f"  skipping (not a list): {path.name}")
            continue

        # Some snapshots list the same position twice (double-inserted rows that
        # differ only by tiny value noise). Within each (wallet, chain, token,
        # position_type) group, drop rows whose value is within 1% of an
        # already-kept row; keep genuinely distinct positions.
        kept_by_group: dict[tuple, list[float]] = {}
        by_agent: dict[str, float] = {}
        for row in rows:
            if row.get("token_symbol") != "USDC":
                continue
            usd = float(row.get("usd_value") or 0)
            key = (row.get("wallet"), row.get("chain"), row.get("token_address"),
                   row.get("position_type"), row.get("is_receipt_token"))
            kept = kept_by_group.setdefault(key, [])
            if any(abs(usd - k) / max(k, 1e-9) <= 0.01 for k in kept):
                continue  # near-duplicate of an existing row in this group
            kept.append(usd)
            agent = row.get("agent_name") or m.group("prefix")
            by_agent[agent] = by_agent.get(agent, 0.0) + usd

        for agent, usd in by_agent.items():
            records.append({"agent": agent, "ts": ts, "usd": round(usd, 2)})

    # Collapse to one point per agent per day: some days have several snapshots
    # (e.g. ZyFAI on 2026-08-30/09-02), which look like duplicated bars.
    # Keep the last snapshot of each day.
    daily: dict[tuple[str, str], dict] = {}
    for r in records:
        key = (r["agent"], r["ts"][:10])
        if key not in daily or r["ts"] > daily[key]["ts"]:
            daily[key] = r
    records = sorted(daily.values(), key=lambda r: (r["agent"], r["ts"]))

    OUTPUT_JSON.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records ({len(files)} files) -> {OUTPUT_JSON}")

    # Refresh the dashboard's embedded fallback snapshot.
    html = DASHBOARD.read_text(encoding="utf-8")
    new_html, n = re.subn(
        r"const EMBEDDED_DATA = \[.*?\];",
        "const EMBEDDED_DATA = " + json.dumps(records) + ";",
        html,
        count=1,
        flags=re.DOTALL,
    )
    if n:
        DASHBOARD.write_text(new_html, encoding="utf-8")
        print(f"Patched EMBEDDED_DATA fallback in {DASHBOARD.name} ({len(records)} records)")
    else:
        print(f"WARNING: EMBEDDED_DATA not found in {DASHBOARD.name}, JSON file still written")


if __name__ == "__main__":
    main()
