"""Smoke test for the Archive workflow: export_json -> write_run_log -> move_to_archive."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, r"C:\Users\chris\Projects\agent-accounting")

from main import export_json, export_raw, write_run_log, move_to_archive
from storage import Storage

tmp = Path(tempfile.mkdtemp(prefix="archive_test_"))
run_timestamp = "20990101_000000"

# 1. Simulate a run: stage files in RECV/<agent>/<timestamp>/
storage = Storage(str(tmp / "test.db"))
run_dir = tmp / "RECV" / "test_agent" / run_timestamp
t_count, b_count = export_json(storage, "0xabc", run_dir, run_timestamp)
export_raw([{"page": 1}], [{"pos": 1}], run_dir, run_timestamp)
print("staging:", sorted(p.name for p in run_dir.glob("*.json")))

# 2. Write the run log into logs/
archive_dir = tmp / "Archive"
logs_dir = tmp / "logs"
entries = [{
    "agent": "Test Agent", "wallet": "0xabc",
    "transfers": t_count, "balances": b_count,
    "raw_tx": 1, "raw_pos": 1,
    "files": [f.name for f in sorted(run_dir.glob("*.json"))],
}]
write_run_log(logs_dir, run_timestamp, entries, [])

# 3. Move JSONs to the flat Archive/ with an agent prefix
move_to_archive(run_dir, archive_dir, "test_agent")

# Verify
archived = sorted(p.name for p in archive_dir.glob("*.json"))
logs = sorted(p.name for p in logs_dir.glob("*.txt"))
staging_left = list((tmp / "RECV").rglob("*.json"))
print("archived:", archived)
print("logs:", logs)
print("staging leftovers:", staging_left)

assert archived == [
    "test_agent_balances_20990101_000000.json",
    "test_agent_raw_positions_20990101_000000.json",
    "test_agent_raw_transactions_20990101_000000.json",
    "test_agent_transfers_20990101_000000.json",
], archived
assert logs == ["sync_log_20990101_000000.txt"], logs
assert not staging_left, staging_left
assert not run_dir.exists(), "staging dir should be removed"
print("\nLOG CONTENT:\n" + (logs_dir / "sync_log_20990101_000000.txt").read_text())
print("SMOKE TEST PASSED")
