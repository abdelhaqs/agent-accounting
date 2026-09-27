# Documentation Index (`docs/`)

**Project:** Agent Accounting & Multi-Wallet Tracking Pipeline  
**GCP Project:** `agent-accounting-506719`  

---

## 📂 Active Documentation Structure

| Resource | Purpose |
| :--- | :--- |
| [**`report/`**](report/README.md) | **Automated Value Check & Reconciliation Reports** generated after each run (`.md` format + HTML dashboard). |
| [**`how_to_trigger_etl_on_gcp.md`**](how_to_trigger_etl_on_gcp.md) | **Operations & Execution Guide** for running, monitoring, and triggering the ETL on Google Cloud Platform. |
| [**`pipeline_architecture_gcp.md`**](pipeline_architecture_gcp.md) | **GCP Cloud Architecture Reference** (Cloud Run, Cloud Workflows, BigQuery, GCS, Secret Manager). |
| [`pipeline_diagram_gcp.png`](pipeline_diagram_gcp.png) | High-resolution GCP Infrastructure architecture diagram. |
| [`pipeline_diagram.png`](pipeline_diagram.png) | Ingestion and reconciliation dataflow diagram. |

---

## 📊 Automated Reports (`docs/report/`)

Every pipeline run automatically computes on-chain reconciliation balances and saves a detailed Markdown report to `docs/report/`:
- **`latest_value_check_report.md`**: Direct link to the most recent run's audit.
- **`latest_audit_dashboard.html`**: Interactive dark-mode HTML dashboard compiled from the latest report.
