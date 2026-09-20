# ETL Script: `bigquery_loader.py`

**Source File:** [`bigquery_loader.py`](file:///c:/Users/chris/Projects/agent-accounting/bigquery_loader.py)  
**Role:** Cloud Data Warehouse Loading (Google BigQuery)  
**Language:** Python 3.12  

---

## 1. Overview

`bigquery_loader.py` streams clean accounting data from the pipeline into Google Cloud BigQuery dataset `agent_accounting`. It writes historical position snapshots, transaction transfers, and on-chain reconciliation audit logs.

---

## 2. BigQuery Tables & Schema Mappings

### Table 1: `agent_accounting.balances`
Partitioned by `DAY(updated_at)`, clustered by `wallet`, `token_symbol`.

| Column | Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `wallet` | STRING | REQUIRED | Agent EVM address |
| `agent_name` | STRING | NULLABLE | Human-readable name from config |
| `chain` | STRING | NULLABLE | Blockchain identifier (e.g. `base`) |
| `position_type` | STRING | NULLABLE | Category: `wallet`, `loan`, `deposit`, `reward` |
| `token_symbol` | STRING | NULLABLE | Token ticker (e.g. `USDC`, `WETH`) |
| `token_address` | STRING | NULLABLE | Contract address on-chain |
| `balance_float` | FLOAT | NULLABLE | Human-readable quantity |
| `usd_value` | FLOAT | NULLABLE | Total USD valuation |
| `updated_at` | TIMESTAMP | NULLABLE | Snapshot timestamp |
| `provider` | STRING | NULLABLE | Data provider (`zerion` or `debank`) |

### Table 2: `agent_accounting.transfers`
Partitioned by `DAY(mined_at)`, clustered by `wallet`, `token_symbol`.

| Column | Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `wallet` | STRING | REQUIRED | Agent EVM address |
| `tx_hash` | STRING | NULLABLE | On-chain transaction hash |
| `direction` | STRING | NULLABLE | Transfer direction: `in` or `out` |
| `sender` | STRING | NULLABLE | Source address |
| `recipient` | STRING | NULLABLE | Destination address |
| `amount_float` | FLOAT | NULLABLE | Transferred token amount |
| `usd_value` | FLOAT | NULLABLE | USD value at transaction time |
| `mined_at` | TIMESTAMP | NULLABLE | Block timestamp |

### Table 3: `agent_accounting.balance_reconciliation`
Partitioned by `DAY(loaded_at)`, clustered by `wallet`, `status`.

| Column | Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `run_timestamp` | STRING | REQUIRED | Run ID (e.g. `20260920_120124`) |
| `agent_name` | STRING | NULLABLE | Agent name |
| `wallet` | STRING | REQUIRED | Agent EVM address |
| `provider` | STRING | NULLABLE | Primary data provider used |
| `computed_usd` | FLOAT | NULLABLE | Stored portfolio valuation |
| `onchain_total_usd`| FLOAT | NULLABLE | Direct Base JSON-RPC valuation |
| `onchain_delta_pct`| FLOAT | NULLABLE | Percentage variance |
| `status` | STRING | NULLABLE | Audit verdict: `OK` or `MISMATCH` |
| `loaded_at` | TIMESTAMP | NULLABLE | Verification timestamp |

---

## 3. Key Class Interface: `BigQueryLoader`

### `BigQueryLoader(dataset_id: str, project_id: str = None)`

- **`load_balances(rows: list[dict]) -> int`**  
  Inserts token balance snapshots into `agent_accounting.balances`. Returns count of rows inserted.

- **`load_transfers(rows: list[dict]) -> int`**  
  Inserts transfer events into `agent_accounting.transfers`.

- **`record_reconciliation(reconciliation_data: dict) -> None`**  
  Appends reconciliation audit results to `agent_accounting.balance_reconciliation`.
