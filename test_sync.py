"""Unit tests for Zerion sync parsing logic."""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from main import load_agents, sync_balances, sync_transfers
from storage import Storage


class TestSync(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.storage = Storage(self.db_path)
        self.wallet = "0x42b9df65b219b3dd36ff330a4dd8f327a6ada990"

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _sample_tx(self):
        return {
            "type": "transactions",
            "id": "52d994a173d755e99845e861d534a419",
            "attributes": {
                "hash": "0x109d8622084d562263230ba5de412b5cd7c372019131e2c9d0a8aa4925eb6034",
                "mined_at": "2022-08-15T11:26:31+00:00",
                "transfers": [
                    {
                        "direction": "in",
                        "sender": "0x60a26d69263ef43e9a68964ba141263f19d71d51",
                        "recipient": self.wallet,
                        "quantity": {"int": "123456780000000000", "decimals": 18, "float": 0.12345678},
                        "price": 106.88,
                        "value": 13.19,
                        "fungible_info": {
                            "id": "bed-token",
                            "name": "Bankless BED Index",
                            "symbol": "BED",
                            "implementations": [
                                {"chain_id": "ethereum", "address": "0x2af1df3ab0ab157e1e2ad8f88a7d04fbea0c7dc6", "decimals": 18}
                            ],
                        },
                    },
                    {
                        "direction": "out",
                        "from": self.wallet,
                        "to": "0x60a26d69263ef43e9a68964ba141263f19d71d51",
                        "quantity": {"string": "500000000000000000", "float": 0.5},
                        "fungible_info": {
                            "name": "Unknown Token",
                            "symbol": "UTK",
                            "implementations": [{"chain_id": "ethereum", "address": "0x0000000000000000000000000000000000000001"}],
                        },
                    },
                ],
            },
            "relationships": {"chain": {"data": {"type": "chains", "id": "ethereum"}}},
        }

    def _sample_position(self):
        return {
            "type": "positions",
            "id": "pos-1",
            "attributes": {
                "position_type": "deposited",
                "quantity": {"string": "1000000000000000000", "float": 1.0},
                "value": 2500.0,
                "price": 2500.0,
                "fungible_info": {
                    "id": "morpho-vault-share",
                    "name": "Morpho Vault Share",
                    "symbol": "mUSD",
                    "implementations": [{"chain_id": "ethereum", "address": "0x1234", "decimals": 18}],
                },
            },
            "relationships": {"chain": {"data": {"type": "chains", "id": "ethereum"}}},
        }

    def _query(self, sql: str):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def test_sync_transfers(self):
        client = MagicMock()
        client.get_transactions.return_value = iter([self._sample_tx()])

        sync_transfers(client, self.wallet, self.storage)

        rows = self._query("SELECT * FROM transfers ORDER BY direction")
        self.assertEqual(len(rows), 2)

        inbound = [r for r in rows if r["direction"] == "in"][0]
        self.assertEqual(inbound["token_symbol"], "BED")
        self.assertEqual(inbound["amount_raw"], "123456780000000000")
        self.assertAlmostEqual(inbound["amount_float"], 0.12345678)
        self.assertEqual(inbound["sender"], "0x60a26d69263ef43e9a68964ba141263f19d71d51")

        outbound = [r for r in rows if r["direction"] == "out"][0]
        self.assertEqual(outbound["token_symbol"], "UTK")
        self.assertEqual(outbound["amount_raw"], "500000000000000000")

    def test_sync_balances(self):
        client = MagicMock()
        client.get_positions.return_value = iter([self._sample_position()])

        sync_balances(client, self.wallet, self.storage)

        rows = self._query("SELECT * FROM balances")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["token_symbol"], "mUSD")
        self.assertEqual(row["position_type"], "deposited")
        self.assertEqual(row["is_receipt_token"], 1)
        self.assertEqual(row["balance_raw"], "1000000000000000000")
        self.assertAlmostEqual(row["balance_float"], 1.0)

    def test_chain_filter_passed_to_client(self):
        client = MagicMock()
        client.get_transactions.return_value = iter([])
        client.get_positions.return_value = iter([])

        sync_transfers(client, self.wallet, self.storage, chain_ids="base")
        sync_balances(client, self.wallet, self.storage, chain_ids="base")

        client.get_transactions.assert_called_once_with(
            self.wallet, chain_ids="base", raw_pages=None
        )
        client.get_positions.assert_called_once_with(
            self.wallet, positions_filter="no_filter", chain_ids="base", raw_pages=None
        )

    def test_raw_pages_collected(self):
        client = MagicMock()
        client.get_transactions.return_value = iter([])
        client.get_positions.return_value = iter([])

        raw_tx: list[dict] = []
        raw_pos: list[dict] = []
        sync_transfers(client, self.wallet, self.storage, raw_pages=raw_tx)
        sync_balances(client, self.wallet, self.storage, raw_pages=raw_pos)

        client.get_transactions.assert_called_once_with(
            self.wallet, chain_ids=None, raw_pages=raw_tx
        )
        client.get_positions.assert_called_once_with(
            self.wallet, positions_filter="no_filter", chain_ids=None, raw_pages=raw_pos
        )

    def test_load_agents_from_yaml(self):
        import tempfile
        from pathlib import Path

        yaml_content = """
agents:
  - name: Agent One
    address: "0x1111111111111111111111111111111111111111"
  - name: Agent Two
    address: "0x2222222222222222222222222222222222222222"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            path = f.name
        try:
            agents = load_agents(path)
            self.assertEqual(len(agents), 2)
            self.assertEqual(agents[0]["name"], "Agent One")
            self.assertEqual(agents[0]["address"], "0x1111111111111111111111111111111111111111")
        finally:
            Path(path).unlink()

    def test_agent_name_defaults_to_address(self):
        import tempfile
        from pathlib import Path

        yaml_content = """
agents:
  - address: "0x3333333333333333333333333333333333333333"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            path = f.name
        try:
            agents = load_agents(path)
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]["name"], "0x3333333333333333333333333333333333333333")
        finally:
            Path(path).unlink()

    def test_migration_adds_agent_name_column(self):
        import tempfile
        from pathlib import Path

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            # Simulate an old database without agent_name.
            conn = sqlite3.connect(db_path)
            conn.executescript(
                """
                CREATE TABLE transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet TEXT NOT NULL,
                    tx_id TEXT NOT NULL,
                    tx_hash TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    mined_at TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    token_id TEXT,
                    token_name TEXT,
                    token_symbol TEXT,
                    token_address TEXT,
                    chain_id TEXT,
                    decimals INTEGER,
                    amount_raw TEXT,
                    amount_float REAL,
                    price REAL,
                    usd_value REAL
                );
                CREATE TABLE balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    position_type TEXT NOT NULL,
                    token_id TEXT,
                    token_name TEXT,
                    token_symbol TEXT,
                    token_address TEXT,
                    chain_id TEXT,
                    decimals INTEGER,
                    balance_raw TEXT,
                    balance_float REAL,
                    price REAL,
                    usd_value REAL,
                    is_receipt_token INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.close()

            # Storage init should migrate without error.
            Storage(db_path)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            transfers_cols = [r["name"] for r in conn.execute("PRAGMA table_info(transfers)")]
            balances_cols = [r["name"] for r in conn.execute("PRAGMA table_info(balances)")]
            conn.close()

            self.assertIn("agent_name", transfers_cols)
            self.assertIn("agent_name", balances_cols)
        finally:
            Path(db_path).unlink()

    def test_export_json_and_raw(self):
        import json
        import tempfile
        from pathlib import Path

        from main import export_json, export_raw

        client = MagicMock()
        client.get_transactions.return_value = iter([self._sample_tx()])
        client.get_positions.return_value = iter([self._sample_position()])

        sync_transfers(client, self.wallet, self.storage, agent_name="Test Agent")
        sync_balances(client, self.wallet, self.storage, agent_name="Test Agent")

        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            export_json(self.storage, self.wallet, agent_dir)
            export_raw([{"page": 1}], [{"page": 1}], agent_dir)

            transfers_path = agent_dir / "transfers.json"
            balances_path = agent_dir / "balances.json"
            raw_tx_path = agent_dir / "raw_transactions.json"
            raw_pos_path = agent_dir / "raw_positions.json"

            self.assertTrue(transfers_path.exists())
            self.assertTrue(balances_path.exists())
            self.assertTrue(raw_tx_path.exists())
            self.assertTrue(raw_pos_path.exists())

            transfers = json.loads(transfers_path.read_text())
            balances = json.loads(balances_path.read_text())
            self.assertEqual(len(transfers), 2)
            self.assertEqual(len(balances), 1)
            self.assertEqual(balances[0]["token_symbol"], "mUSD")
            self.assertEqual(balances[0]["agent_name"], "Test Agent")

    def test_httperror_skips_agent(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from requests import HTTPError
        from requests.models import Response

        yaml_content = """
agents:
  - name: Good Agent
    address: "0x1111111111111111111111111111111111111111"
  - name: Bad Agent
    address: "0xe51b7dba38e732a19838c3f23816df7092441597"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            agents_path = f.name

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            def fake_get_transactions(wallet, **kwargs):
                if wallet.lower() == "0xe51b7dba38e732a19838c3f23816df7092441597":
                    resp = Response()
                    resp.status_code = 400
                    raise HTTPError("Unsupported address", response=resp)
                return iter([])

            def fake_get_positions(wallet, **kwargs):
                return iter([])

            with patch.dict(os.environ, {"ZERION_API_KEY": "test-key"}):
                with patch("main.ZerionClient") as mock_client_cls:
                    client = MagicMock()
                    client.get_transactions.side_effect = fake_get_transactions
                    client.get_positions.side_effect = fake_get_positions
                    mock_client_cls.return_value = client

                    with tempfile.TemporaryDirectory() as tmpdir:
                        with patch.object(sys, "argv", [
                            "main.py",
                            "--agents-config", agents_path,
                            "--db-path", db_path,
                            "--output-dir", tmpdir,
                            "--log-file", "",
                        ]):
                            from main import main as main_func
                            main_func()

                        # Bad agent should have no output folder; good agent should.
                        self.assertTrue((Path(tmpdir) / "good_agent").exists())
                        self.assertFalse((Path(tmpdir) / "bad_agent").exists())
        finally:
            Path(agents_path).unlink(missing_ok=True)
            Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
