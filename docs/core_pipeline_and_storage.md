# Core Pipeline & Storage Architecture (Python)

**Location:** `c:\Users\chris\Projects\agent-accounting`  
**Target Environment:** Python 3.12 / GCP Cloud Run / Local PowerShell  

---

## 1. System Overview & Architecture (Simple 3-Stage Model)

The pipeline automates portfolio accounting and balance reconciliation across multiple Web3 agents using a simple 3-stage process:

```mermaid
flowchart LR
    subgraph S1["1. EXTRACT"]
        direction TB
        A["Tracked Agents<br/>(agents.yaml)"] --> B["<b>zerion_client.py</b><br/>(Primary API)"]
        B -.->|Fallback| C["<b>uniblock_client.py</b><br/>(DeBank Proxy)"]
    end

    subgraph S2["2. VERIFY"]
        direction TB
        D["<b>rpc_client.py</b><br/>Direct Base JSON-RPC<br/>(Ground Truth)"]
    end

    subgraph S3["3. STORE & LOAD"]
        direction TB
        E["<b>storage.py</b><br/>(Local SQLite zerion.db)"]
        F["Flat JSON Archive<br/>(Audit Trail in GCS)"]
        G["<b>bigquery_loader.py</b><br/>(Google BigQuery)"]
        E --> F --> G
    end

    S1 ==>|Balances & Transfers| S3
    S2 -.->|Reconciliation Delta| S3

    style S1 fill:#1e1e2e,stroke:#a855f7,stroke-width:1px,color:#fff
    style S2 fill:#0f172a,stroke:#10b981,stroke-width:1px,color:#fff
    style S3 fill:#181825,stroke:#3b82f6,stroke-width:1px,color:#fff
```

### How It Works in 3 Steps:
1. **Extract:** [`main.py`](etl/main.md) loops through each wallet in `agents.yaml`. It calls [`zerion_client.py`](etl/zerion_client.md) to retrieve token balances and transfers. If Zerion cannot index the address, it falls back to [`uniblock_client.py`](etl/uniblock_client.md) (DeBank).
2. **Verify:** [`rpc_client.py`](etl/rpc_client.md) independently queries Base blockchain nodes via JSON-RPC to read exact on-chain balances and ERC-4626 vault share values, calculating any discrepancy.
3. **Store & Load:** [`storage.py`](etl/storage.md) writes clean records to SQLite (`zerion.db`), raw JSONs are archived to Cloud Storage, and [`bigquery_loader.py`](etl/bigquery_loader.md) ingests rows into Google BigQuery.

---

## 2. Dedicated Script Documentation

Each ETL Python script has its own standalone documentation file:

| Script | Role | Stage | Dedicated Documentation |
| :--- | :--- | :--- | :--- |
| [`main.py`](file:///c:/Users/chris/Projects/agent-accounting/main.py) | Pipeline Orchestrator & CLI Runner | Orchestration | 👉 [**`docs/etl/main.md`**](etl/main.md) |
| [`zerion_client.py`](file:///c:/Users/chris/Projects/agent-accounting/zerion_client.py) | Primary Ingestion (Zerion API v1) | Extraction | 👉 [**`docs/etl/zerion_client.md`**](etl/zerion_client.md) |
| [`uniblock_client.py`](file:///c:/Users/chris/Projects/agent-accounting/uniblock_client.py) | Fallback Ingestion (DeBank Proxy) | Extraction | 👉 [**`docs/etl/uniblock_client.md`**](etl/uniblock_client.md) |
| [`rpc_client.py`](file:///c:/Users/chris/Projects/agent-accounting/rpc_client.py) | Base JSON-RPC Node Verification | Verification | 👉 [**`docs/etl/rpc_client.md`**](etl/rpc_client.md) |
| [`storage.py`](file:///c:/Users/chris/Projects/agent-accounting/storage.py) | Local SQLite Staging (`zerion.db`) | Persistence | 👉 [**`docs/etl/storage.md`**](etl/storage.md) |
| [`bigquery_loader.py`](file:///c:/Users/chris/Projects/agent-accounting/bigquery_loader.py) | Google BigQuery Ingestion | Warehouse Loading | 👉 [**`docs/etl/bigquery_loader.md`**](etl/bigquery_loader.md) |

---

## 3. Component Summaries

### 3.1. `main.py` — Orchestrator & CLI Runner
- **Role:** Loads configurations, coordinates the per-agent loop, isolates errors so one failed agent does not break the pipeline, stages exports in `RECV/`, and moves them to `Archive/`.
- 📖 **Full Guide:** [**`docs/etl/main.md`**](etl/main.md)

### 3.2. `zerion_client.py` — Primary Extraction Client
- **Role:** Fetches portfolio net worth, positions (including vault shares and receipt tokens), and paginated transaction transfer legs via Zerion v1 REST API.
- 📖 **Full Guide:** [**`docs/etl/zerion_client.md`**](etl/zerion_client.md)

### 3.3. `uniblock_client.py` — DeBank Proxy Fallback Client
- **Role:** Provides fallback coverage for smart contracts, complex lending protocols (Morpho, Moonwell), and liquidity pools with automatic dual-key failover (`429` quota rotation).
- 📖 **Full Guide:** [**`docs/etl/uniblock_client.md`**](etl/uniblock_client.md)

### 3.4. `rpc_client.py` — Base Node JSON-RPC Client
- **Role:** Directly inspects Base smart contracts (`chainId=8453`) using standard function selectors (`balanceOf`, `convertToAssets`, `balanceOfUnderlying`) to establish ground truth without indexing lag.
- 📖 **Full Guide:** [**`docs/etl/rpc_client.md`**](etl/rpc_client.md) & [**`docs/rpc_client_architecture.md`**](rpc_client_architecture.md)

### 3.5. `storage.py` — SQLite Local Database Engine
- **Role:** Manages local schema for `balances` and `transfers` tables with unique constraint deduplication and fast querying in `zerion.db`.
- 📖 **Full Guide:** [**`docs/etl/storage.md`**](etl/storage.md)

### 3.6. `bigquery_loader.py` — Cloud Data Warehouse Loader
- **Role:** Streams records into BigQuery tables (`balances`, `transfers`, and `balance_reconciliation`) partitioned by day and clustered by wallet.
- 📖 **Full Guide:** [**`docs/etl/bigquery_loader.md`**](etl/bigquery_loader.md)

---

## 4. Environment Variables Reference

| Variable | Required | Description |
| :--- | :--- | :--- |
| `ZERION_API_KEY` | **Yes** | Zerion API v1 key for wallet & position indexing |
| `UNIBLOCK_API_KEY` | **Yes** | Primary key for DeBank proxy and Base JSON-RPC verification |
| `UNIBLOCK_API_KEY_BACKUP` | Optional | Secondary Uniblock key for automatic failover |
| `AGENTS_CONFIG` | Optional | Custom path to agents YAML (default: `agents.yaml`) |
| `CHAIN_IDS` | Optional | Target chains (default: `base`) |
| `BQ_DATASET` | Optional | BigQuery dataset name (default: `agent_accounting`) |
| `BQ_PROJECT` | Optional | BigQuery GCP Project ID (default: `agent-accounting-506719`) |
