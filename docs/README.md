# Documentation Index (`docs/`)

**Project:** Agent Accounting & Multi-Wallet Tracking Pipeline  
**GCP Project:** `agent-accounting-506719`  

This directory contains technical specifications, architecture diagrams, cost analyses, script references, and data provider evaluations for the accounting pipeline.

---

## 🛠️ Architecture & Pipeline Specifications

| Document | Focus Area | Description |
| :--- | :--- | :--- |
| [**`core_pipeline_and_storage.md`**](core_pipeline_and_storage.md) | Python Core & Storage | Dedicated breakdown of `main.py`, `rpc_client.py`, `zerion_client.py`, `uniblock_client.py`, `storage.py`, and `bigquery_loader.py`. |
| [**`rpc_client_architecture.md`**](rpc_client_architecture.md) | On-Chain Verification | Mermaid architecture diagram, ABI function selectors, and dual-key failover specifications for Base JSON-RPC verification. |
| [**`pipeline_architecture_gcp.md`**](pipeline_architecture_gcp.md) | GCP Cloud Architecture | Complete cloud deployment architecture (Cloud Run, Cloud Scheduler, Cloud Build, Artifact Registry, BigQuery, GCS). |
| [**`pipeline_architecture.md`**](pipeline_architecture.md) | Pipeline Data Flow | High-level data flow from wallet ingestion to local SQLite, staging, flat archiving, and reporting. |
| [**`scripts_documentation.md`**](scripts_documentation.md) | Script Reference Manual | Comprehensive CLI parameters, usage instructions, and examples for all 18 Python and PowerShell scripts. |
| [**`provider_evaluation_report.md`**](provider_evaluation_report.md) | Data Provider Audit | Evaluation of Zerion REST API vs. DeBank Open API / Uniblock proxy coverage, latency, and reliability. |
| [**`cost_estimate_gcp.md`**](cost_estimate_gcp.md) | Cloud Infrastructure Costs | Detailed cost breakdown of GCP Cloud Run, Cloud Storage, BigQuery, and Secret Manager across scheduled runs. |

---

## 📊 Balance Audits & Reports

Historical mismatch audits, agent comparisons, and on-chain reconciliation reports are maintained in the dedicated subfolder:

👉 [**Comparisons & Value Checks Directory (`docs/comparisons_and_value_checks/`)**](comparisons_and_value_checks/README.md)

---

## 🖼️ Diagrams & Assets

- [`pipeline_diagram_gcp.png`](pipeline_diagram_gcp.png): Full GCP enterprise cloud infrastructure topology.
- [`pipeline_diagram.png`](pipeline_diagram.png): Core ingestion and reconciliation pipeline flow.
- [`generate_diagram_gcp.py`](generate_diagram_gcp.py) & [`generate_diagram.py`](generate_diagram.py): Python scripts to re-render diagrams.
