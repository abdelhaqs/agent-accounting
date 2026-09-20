# Documentation Index (`docs/`)

**Project:** Agent Accounting & Multi-Wallet Tracking Pipeline  
**GCP Project:** `agent-accounting-506719`  

This directory contains technical specifications, architecture diagrams, cost analyses, script references, and all balance reconciliation/comparison reports.

---

## 📁 1. Comparisons & Value Checks (`docs/comparisons_and_value_checks/`)

All historical discrepancy analyses, mismatch audits, and multi-agent portfolio comparison reports are archived in this subfolder:

| Report File | Date | Scope & Summary |
| :--- | :--- | :--- |
| [**`agents_comparison_latest_20260920.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/comparisons_and_value_checks/agents_comparison_latest_20260920.md) | 2026-09-20 | **Current 7-Agent Comparison:** Complete live breakdown of all active agents including the 3 new ones (Zyfai Risky, Mamo AB Abdelhak, Zyfai Conservative) and deprecation of Surfliquid. |
| [**`mismatch_report_all_agents_20260919_161257.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/comparisons_and_value_checks/mismatch_report_all_agents_20260919_161257.md) | 2026-09-19 | **GCP Run `20260919_161257` Audit:** Deep dive into execution `zerion-sync-jxrjc`, confirming 0 real financial discrepancies and diagnosing 429 quota exhaustion. |
| [**`mismatch_report_all_agents_20260919.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/comparisons_and_value_checks/mismatch_report_all_agents_20260919.md) | 2026-09-19 | **Multi-Agent Balance Audit:** Initial multi-agent health check tracing the resolution of Yieldseeker 2 and evaluating Zerion vs. DeBank coverage. |
| [**`mismatch_report_yieldseeker_base_agent_2_20260914.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/comparisons_and_value_checks/mismatch_report_yieldseeker_base_agent_2_20260914.md) | 2026-09-14 | **Baseline Forensic Report:** Investigation into the historical +12.86% Yearn/Morpho pricing mismatch that established on-chain RPC verification. |

---

## 🛠️ 2. Core Architecture & Pipeline Specifications

| Document | Focus Area | Description |
| :--- | :--- | :--- |
| [**`core_pipeline_and_storage.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/core_pipeline_and_storage.md) | Python Core & Storage | Dedicated breakdown of `main.py`, `rpc_client.py`, `zerion_client.py`, `uniblock_client.py`, `storage.py`, and `bigquery_loader.py`. |
| [**`rpc_client_architecture.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/rpc_client_architecture.md) | On-Chain Verification | Mermaid architecture diagram, ABI function selectors, and dual-key failover specifications for Base JSON-RPC verification. |
| [**`pipeline_architecture_gcp.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/pipeline_architecture_gcp.md) | GCP Cloud Architecture | Complete cloud deployment architecture (Cloud Run, Cloud Scheduler, Cloud Build, Artifact Registry, BigQuery, GCS). |
| [**`pipeline_architecture.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/pipeline_architecture.md) | Pipeline Data Flow | High-level data flow from wallet ingestion to local SQLite, staging, flat archiving, and reporting. |
| [**`scripts_documentation.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/scripts_documentation.md) | Script Reference Manual | Comprehensive CLI parameters, usage instructions, and examples for all 18 Python and PowerShell scripts. |
| [**`provider_evaluation_report.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/provider_evaluation_report.md) | Data Provider Audit | Evaluation of Zerion REST API vs. DeBank Open API / Uniblock proxy coverage, latency, and reliability. |
| [**`cost_estimate_gcp.md`**](file:///c:/Users/chris/Projects/agent-accounting/docs/cost_estimate_gcp.md) | Cloud Infrastructure Costs | Detailed cost breakdown of GCP Cloud Run, Cloud Storage, BigQuery, and Secret Manager across scheduled runs. |

---

## 🖼️ 3. Diagrams & Assets

- [`pipeline_diagram_gcp.png`](file:///c:/Users/chris/Projects/agent-accounting/docs/pipeline_diagram_gcp.png): Full GCP enterprise cloud infrastructure topology.
- [`pipeline_diagram.png`](file:///c:/Users/chris/Projects/agent-accounting/docs/pipeline_diagram.png): Core ingestion and reconciliation pipeline flow.
- [`generate_diagram_gcp.py`](file:///c:/Users/chris/Projects/agent-accounting/docs/generate_diagram_gcp.py) & [`generate_diagram.py`](file:///c:/Users/chris/Projects/agent-accounting/docs/generate_diagram.py): Python scripts to re-render diagrams.
