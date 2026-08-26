"""SQLite storage for transfers and balances."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Transfer:
    wallet: str
    agent_name: str | None
    tx_id: str
    tx_hash: str
    chain: str
    mined_at: datetime
    direction: str
    sender: str
    recipient: str
    token_id: str | None
    token_name: str | None
    token_symbol: str | None
    token_address: str | None
    chain_id: str | None
    decimals: int | None
    amount_raw: str | None
    amount_float: float | None
    price: float | None
    usd_value: float | None


@dataclass(frozen=True)
class Balance:
    wallet: str
    agent_name: str | None
    chain: str
    position_type: str
    token_id: str | None
    token_name: str | None
    token_symbol: str | None
    token_address: str | None
    chain_id: str | None
    decimals: int | None
    balance_raw: str | None
    balance_float: float | None
    price: float | None
    usd_value: float | None
    is_receipt_token: bool


class Storage:
    def __init__(self, db_path: str = "zerion.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _column_exists(self, conn: sqlite3.Connection, table: str, column: str) -> bool:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(row["name"] == column for row in rows)

    def _init_db(self):
        with self._connect() as conn:
            # Create tables first (without agent_name indexes, in case an old table exists).
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet TEXT NOT NULL,
                    agent_name TEXT,
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
                    usd_value REAL,
                    UNIQUE(wallet, tx_id, token_id, direction, sender, recipient, amount_raw)
                );

                CREATE TABLE IF NOT EXISTS balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet TEXT NOT NULL,
                    agent_name TEXT,
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
                    updated_at TEXT NOT NULL,
                    UNIQUE(wallet, chain, token_id, token_address, is_receipt_token)
                );
                """
            )

            # Migration: add agent_name column to existing databases that lack it.
            if not self._column_exists(conn, "transfers", "agent_name"):
                conn.execute("ALTER TABLE transfers ADD COLUMN agent_name TEXT")
            if not self._column_exists(conn, "balances", "agent_name"):
                conn.execute("ALTER TABLE balances ADD COLUMN agent_name TEXT")

            # Create indexes after migration so agent_name is guaranteed to exist.
            conn.executescript(
                """
                CREATE INDEX IF NOT EXISTS idx_transfers_wallet ON transfers(wallet);
                CREATE INDEX IF NOT EXISTS idx_transfers_agent ON transfers(agent_name);
                CREATE INDEX IF NOT EXISTS idx_transfers_mined_at ON transfers(mined_at);
                CREATE INDEX IF NOT EXISTS idx_transfers_symbol ON transfers(token_symbol);

                CREATE INDEX IF NOT EXISTS idx_balances_wallet ON balances(wallet);
                CREATE INDEX IF NOT EXISTS idx_balances_agent ON balances(agent_name);
                CREATE INDEX IF NOT EXISTS idx_balances_symbol ON balances(token_symbol);
                """
            )
            conn.commit()

    def clear_transfers(self, wallet: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM transfers WHERE wallet = ?", (wallet,))
            conn.commit()

    def save_transfers(self, transfers: list[Transfer]):
        if not transfers:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO transfers (
                    wallet, agent_name, tx_id, tx_hash, chain, mined_at, direction, sender, recipient,
                    token_id, token_name, token_symbol, token_address, chain_id, decimals,
                    amount_raw, amount_float, price, usd_value
                ) VALUES (
                    :wallet, :agent_name, :tx_id, :tx_hash, :chain, :mined_at, :direction, :sender, :recipient,
                    :token_id, :token_name, :token_symbol, :token_address, :chain_id, :decimals,
                    :amount_raw, :amount_float, :price, :usd_value
                )
                """,
                [self._transfer_row(t) for t in transfers],
            )
            conn.commit()

    def replace_balances(self, wallet: str, balances: list[Balance]):
        with self._connect() as conn:
            conn.execute("DELETE FROM balances WHERE wallet = ?", (wallet,))
            if balances:
                conn.executemany(
                    """
                    INSERT INTO balances (
                        wallet, agent_name, chain, position_type, token_id, token_name, token_symbol,
                        token_address, chain_id, decimals, balance_raw, balance_float, price,
                        usd_value, is_receipt_token, updated_at
                    ) VALUES (
                        :wallet, :agent_name, :chain, :position_type, :token_id, :token_name, :token_symbol,
                        :token_address, :chain_id, :decimals, :balance_raw, :balance_float, :price,
                        :usd_value, :is_receipt_token, :updated_at
                    )
                    """,
                    [self._balance_row(b) for b in balances],
                )
            conn.commit()

    def get_transfers(self, wallet: str | None = None) -> list[dict[str, Any]]:
        """Return all transfers as plain dicts, optionally filtered by wallet."""
        with self._connect() as conn:
            if wallet:
                rows = conn.execute(
                    "SELECT * FROM transfers WHERE wallet = ? ORDER BY mined_at DESC",
                    (wallet.lower(),),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM transfers ORDER BY mined_at DESC").fetchall()
            return [dict(r) for r in rows]

    def get_balances(self, wallet: str | None = None) -> list[dict[str, Any]]:
        """Return all balances as plain dicts, optionally filtered by wallet."""
        with self._connect() as conn:
            if wallet:
                rows = conn.execute(
                    "SELECT * FROM balances WHERE wallet = ? ORDER BY usd_value DESC NULLS LAST",
                    (wallet.lower(),),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM balances ORDER BY usd_value DESC NULLS LAST"
                ).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["is_receipt_token"] = bool(d["is_receipt_token"])
                result.append(d)
            return result

    @staticmethod
    def _transfer_row(t: Transfer) -> dict[str, Any]:
        return {
            "wallet": t.wallet,
            "agent_name": t.agent_name,
            "tx_id": t.tx_id,
            "tx_hash": t.tx_hash,
            "chain": t.chain,
            "mined_at": t.mined_at.isoformat(),
            "direction": t.direction,
            "sender": t.sender,
            "recipient": t.recipient,
            "token_id": t.token_id,
            "token_name": t.token_name,
            "token_symbol": t.token_symbol,
            "token_address": t.token_address,
            "chain_id": t.chain_id,
            "decimals": t.decimals,
            "amount_raw": t.amount_raw,
            "amount_float": t.amount_float,
            "price": t.price,
            "usd_value": t.usd_value,
        }

    @staticmethod
    def _balance_row(b: Balance) -> dict[str, Any]:
        return {
            "wallet": b.wallet,
            "agent_name": b.agent_name,
            "chain": b.chain,
            "position_type": b.position_type,
            "token_id": b.token_id,
            "token_name": b.token_name,
            "token_symbol": b.token_symbol,
            "token_address": b.token_address,
            "chain_id": b.chain_id,
            "decimals": b.decimals,
            "balance_raw": b.balance_raw,
            "balance_float": b.balance_float,
            "price": b.price,
            "usd_value": b.usd_value,
            "is_receipt_token": int(b.is_receipt_token),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
