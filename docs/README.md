# Documentation Index (`docs/`)

**Project:** Agent Accounting & Multi-Wallet Tracking Pipeline  
**GCP Project:** `agent-accounting-506719`  

This directory contains technical specifications, architecture diagrams, cost analyses, script references, and data provider evaluations for the accounting pipeline.

---

## ⚡ 1. Python ETL Pipeline Scripts (`docs/etl/`)

Individual technical guides for every Python script powering the ETL flow:

👉 [**ETL Pipeline Scripts Directory (`docs/etl/`)**](etl/README.md)

| Script Guide | Role | Description |
| :--- | :--- | :--- |
| [**`etl/main.md`**](etl/main.md) | **Orchestrator** | Main CLI execution runner, multi-agent loop, staging, and archiving. |
| [**`etl/zerion_client.md`**](etl/zerion_client.md) | **Primary Ingestion** | Zerion v1 REST API client (portfolio, positions, transfers, pagination). |
| [**`etl/uniblock_client.md`**](etl/uniblock_client.md) | **Fallback Ingestion** | DeBank Open API proxy client with automated dual-key failover. |
| [**`etl/rpc_client.md`**](etl/rpc_client.md) | **On-Chain Verify** | Base JSON-RPC node client for independent contract ground-truth checks. |
| [**`etl/storage.md`**](etl/storage.md) | **Local Persistence** | Local SQLite engine (`zerion.db`) schemas and upsert operations. |
| [**`etl/bigquery_loader.md`**](etl/bigquery_loader.md) | **Warehouse Loader** | Google BigQuery streaming/batch ingestion schemas and reconciliation tables. |

---

## 🛠️ 2. Architecture & Pipeline Specifications

| Document | Focus Area | Description |
| :--- | :--- | :--- |
| [**`core_pipeline_and_storage.md`**](core_pipeline_and_storage.md) | Pipeline Overview | High-level 3-stage model connecting extraction, verification, and warehouse persistence. |
| [**`rpc_client_architecture.md`**](rpc_client_architecture.md) | On-Chain Verification | Mermaid architecture diagram, ABI function selectors, and dual-key failover specifications for Base JSON-RPC verification. |
| [**`pipeline_architecture_gcp.md`**](pipeline_architecture_gcp.md) | GCP Cloud Architecture | Complete cloud deployment architecture (Cloud Run, Cloud Scheduler, Cloud Build, Artifact Registry, BigQuery, GCS). |
| [**`pipeline_architecture.md`**](pipeline_architecture.md) | Pipeline Data Flow | High-level data flow from wallet ingestion to local SQLite, staging, flat archiving, and reporting. |
| [**`scripts_documentation.md`**](scripts_documentation.md) | Script Reference Manual | Comprehensive CLI parameters, usage instructions, and examples for all 18 Python and PowerShell scripts. |
| [**`provider_evaluation_report.md`**](provider_evaluation_report.md) | Data Provider Audit | Evaluation of Zerion REST API vs. DeBank Open API / Uniblock proxy coverage, latency, and reliability. |
| [**`cost_estimate_gcp.md`**](cost_estimate_gcp.md) | Cloud Infrastructure Costs | Detailed cost breakdown of GCP Cloud Run, Cloud Storage, BigQuery, and Secret Manager across scheduled runs. |

---

## 📊 3. Balance Audits & Reports

Historical mismatch audits, agent comparisons, and on-chain reconciliation reports are maintained in the dedicated subfolder:

👉 [**Comparisons & Value Checks Directory (`docs/comparisons_and_value_checks/`)**](comparisons_and_value_checks/README.md)

---

## 🖼️ 4. Diagrams & Assets

- [`pipeline_diagram_gcp.png`](pipeline_diagram_gcp.png): Full GCP enterprise cloud infrastructure topology.
- [`pipeline_diagram.png`](pipeline_diagram.png): Core ingestion and reconciliation pipeline flow.
- [`generate_diagram_gcp.py`](generate_diagram_gcp.py) & [`generate_diagram.py`](generate_diagram.py): Python scripts to re-render diagrams.
