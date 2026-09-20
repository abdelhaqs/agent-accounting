# ETL Script: `storage.py`

**Source File:** [`storage.py`](file:///c:/Users/chris/Projects/agent-accounting/storage.py)  
**Role:** Local SQLite Persistence & Staging (`zerion.db`)  
**Language:** Python 3.12  

---

## 1. Overview

`storage.py` encapsulates local database operations using SQLite (`zerion.db`). It provides atomic transactions, upsert mechanics, and query utilities for staging data locally before it is archived or loaded into Google BigQuery.

---

## 2. Database Schema

### Table 1: `balances`
Stores point-in-time token balances and yield vault positions:

```sql
CREATE TABLE IF NOT EXISTS balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT,
    wallet TEXT NOT NULL,
    chain TEXT,
    token_address TEXT,
    token_name TEXT,
    token_symbol TEXT,
    decimals INTEGER,
    balance_raw TEXT,
    balance_float REAL,
    price REAL,
    usd_value REAL,
    is_receipt_token BOOLEAN DEFAULT 0,
    position_type TEXT,
    protocol TEXT,
    timestamp TEXT NOT NULL,
    provider TEXT DEFAULT 'zerion',
    UNIQUE(wallet, chain, token_address, position_type, protocol)
);
```

### Table 2: `transfers`
Stores normalized inbound and outbound transfer events:

```sql
CREATE TABLE IF NOT EXISTS transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet TEXT NOT NULL,
    agent_name TEXT,
    transfer_id TEXT UNIQUE NOT NULL,
    tx_hash TEXT,
    chain TEXT,
    block_timestamp TEXT,
    direction TEXT,
    sender TEXT,
    recipient TEXT,
    fungible_id TEXT,
    token_name TEXT,
    token_symbol TEXT,
    token_address TEXT,
    token_chain TEXT,
    decimals INTEGER,
    amount_raw TEXT,
    amount_float REAL,
    price REAL,
    usd_value REAL,
    provider TEXT DEFAULT 'zerion'
);
```

---

## 3. Key Methods & Class Interface: `Storage`

### `Storage(db_path: str = "zerion.db")`

- **`upsert_balance(balance_data: dict) -> None`**  
  Inserts or updates a position row based on the unique constraint `(wallet, chain, token_address, position_type, protocol)`.

- **`insert_transfer(transfer_data: dict) -> bool`**  
  Inserts a new transfer row using `INSERT OR IGNORE` to prevent duplicate transaction entries. Returns `True` if a new row was inserted.

- **`get_balances(wallet: str = None) -> list[dict]`**  
  Returns all current balance rows, optionally filtered by wallet.

- **`get_transfers(wallet: str = None) -> list[dict]`**  
  Returns all transfer history records, optionally filtered by wallet.

- **`clear_transfers(wallet: str = None) -> None`**  
  Deletes transfers when running with the `--full-resync` flag.
