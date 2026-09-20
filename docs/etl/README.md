# ETL Pipeline Scripts Reference (`docs/etl/`)

This directory contains standalone technical documentation for every individual Python script that powers the Agent Accounting ETL pipeline.

---

## 🚀 Production ETL Pipeline Architecture

```mermaid
flowchart LR
    subgraph Extract["1. Extract"]
        ZC["<b>zerion_client.py</b><br/>Primary Zerion API"]
        UC["<b>uniblock_client.py</b><br/>Uniblock Unified API"]
    end

    subgraph Verify["2. Verify"]
        RPC["<b>rpc_client.py</b><br/>Base Node JSON-RPC"]
    end

    subgraph TransformLoad["3. Archive & Load"]
        ARC["<b>Cloud Storage Archive</b><br/>Raw & Processed JSON"]
        BQ["<b>bigquery_loader.py</b><br/>Google BigQuery"]
        ARC --> BQ
    end

    Orchestrator["<b>main.py</b><br/>Pipeline Orchestrator"] -.-> Extract
    Orchestrator -.-> Verify
    Orchestrator -.-> TransformLoad

    style Orchestrator fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff
    style Extract fill:#1e1e2e,stroke:#a855f7,stroke-width:1px,color:#fff
    style Verify fill:#0f172a,stroke:#10b981,stroke-width:1px,color:#fff
    style TransformLoad fill:#181825,stroke:#f59e0b,stroke-width:1px,color:#fff
```

> [!NOTE]  
> The production pipeline streams data to Cloud Storage and BigQuery. The [`storage.py`](storage.md) SQLite engine is used exclusively for offline local development and debugging (see [**Local Testing & Development Guide**](../local_testing_and_development.md)).

---

## Quick Navigation Index

| Script | Role | Stage | Documentation Link |
| :--- | :--- | :--- | :--- |
| [`main.py`](file:///c:/Users/chris/Projects/agent-accounting/main.py) | **Orchestrator** | Coordination & CLI | [**`main.md`**](main.md) |
| [`zerion_client.py`](file:///c:/Users/chris/Projects/agent-accounting/zerion_client.py) | **Primary Ingestion** | Extract (Zerion API) | [**`zerion_client.md`**](zerion_client.md) |
| [`uniblock_client.py`](file:///c:/Users/chris/Projects/agent-accounting/uniblock_client.py) | **Fallback Ingestion** | Extract (Uniblock Unified API) | [**`uniblock_client.md`**](uniblock_client.md) |
| [`rpc_client.py`](file:///c:/Users/chris/Projects/agent-accounting/rpc_client.py) | **On-Chain Verification** | Ground Truth Verify | [**`rpc_client.md`**](rpc_client.md) |
| [`storage.py`](file:///c:/Users/chris/Projects/agent-accounting/storage.py) | **Local Persistence** | Local SQLite Staging | [**`storage.md`**](storage.md) |
| [`bigquery_loader.py`](file:///c:/Users/chris/Projects/agent-accounting/bigquery_loader.py) | **Cloud Data Warehouse** | BigQuery Loading | [**`bigquery_loader.md`**](bigquery_loader.md) |

---

## System Architecture Guide

For the full architectural breakdown connecting all scripts together, see:
👉 [**Core Pipeline Architecture Guide (`docs/core_pipeline_and_storage.md`)**](../core_pipeline_and_storage.md)
