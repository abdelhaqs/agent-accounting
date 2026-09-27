# Agent Accounting

Sync ERC-20 transfer history and token balances (including vault share and LP positions) for on-chain AI agents across EVM networks using the Uniblock / DeBank APIs with independent on-chain JSON-RPC verification.

## What it does

1. Ingests all token balances, protocol positions, and transfer histories for configured AI agents using Uniblock / DeBank.
2. Cross-checks balances against direct on-chain JSON-RPC node responses on Base (`https://mainnet.base.org`).
3. Validates records through strict data quality contracts (schema conformism, positive balance invariants).
4. Stores data in a local SQLite database (`accounting.db`), tagged by wallet and agent name.
5. Stages and archives timestamped snapshot artifacts in `./output/` and `./Archive/`.
6. Loads verified records into Google BigQuery (`agent_accounting` dataset: `transfers`, `balances`, and `balance_reconciliation` tables).
7. Generates human-readable Markdown value check reports and interactive HTML audit dashboards in `docs/report/`.

## Project Layout

```text
agent-accounting/
├── config/              # Configuration files (agents.yaml, .env.example)
├── dag/                 # Pipeline & ETL scripts (main.py, clients, storage, quality, reporter)
├── docs/                # Architecture docs, deployment guides, audit reports
│   └── report/          # Automated value check reports & HTML audit dashboards
├── tests/               # Unit tests & data quality contracts
├── terraform/           # GCP Infrastructure as Code (Cloud Run, GCS, BigQuery, Workflows)
│   └── minimal/         # Minimal GCP deployment (Cloud Run Job + GCS + BigQuery)
├── Dockerfile           # Production container definition
├── Makefile             # CLI automation for Linux/macOS
├── task.ps1             # CLI automation for Windows PowerShell
└── requirements.txt     # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
cp config/.env.example .env
# edit .env with your UNIBLOCK_API_KEY
```

## Configuring agents (wallets)

The pipeline reads wallets from `config/agents.yaml` by default:

```yaml
agents:
  - name: "ZyFAI Base Agent 2"
    address: "0x42b9df65b219b3dd36ff330a4dd8f327a6ada990"
  - name: "YieldSeeker Base Agent 2"
    address: "0xc88bb4a2d39aa4ba3d5267b2d5a3ec78e47be9f7"
  - name: "Mamo Base Agent 2"
    address: "0xec23ecb0ec719c8f0f04620f4c58cf3ea671e6bc"
```

## Running the Pipeline

Using the task runner:
```powershell
# Windows
.\task.ps1 run
# Linux/macOS
make run
```

Or running the pipeline directly:
```bash
python dag/main.py
```

### Optional flags

```bash
python dag/main.py --db-path accounting.db --full-resync --rate-limit-delay 0.5 --chain-ids base --output-dir ./output
```

- `--db-path`: SQLite database file (default `accounting.db`).
- `--full-resync`: Drop existing transfer data and re-fetch from the beginning.
- `--rate-limit-delay`: Seconds to sleep between paginated API requests (default `0.25`).
- `--chain-ids`: Comma-separated chain ids to sync (default: `base`; env: `CHAIN_IDS`).
- `--agents-config`: Path to the agents YAML config (default `config/agents.yaml`; env `AGENTS_CONFIG`).
- `--output-dir`: Directory for per-agent exports (default `./RECV`).
- `--archive-dir`: Final destination for timestamped JSON files (default `./Archive`).
- `--report-dir`: Directory for value check reports (default `docs/report`).
- `--no-export`: Skip exporting JSON files (only update SQLite and BigQuery).
- `--skip-bq`: Skip loading data into Google BigQuery.
- `--log-file`: Log file path (default `accounting_sync.log`).

## Database tables

- `transfers` — one row per ERC-20 transfer, includes `wallet`, `agent_name`, and `provider`.
- `balances` — current balance per token per agent, includes `wallet`, `agent_name`, and `provider`.

## Query examples

```sql
-- all inbound transfers for a specific agent
SELECT * FROM transfers
WHERE direction = 'in' AND agent_name = 'ZyFAI Base Agent 2'
ORDER BY mined_at DESC;

-- current balances across all agents
SELECT agent_name, chain, token_symbol, balance_float, usd_value
FROM balances
ORDER BY usd_value DESC;

-- vault / LP receipt tokens only
SELECT * FROM balances WHERE is_receipt_token = 1;
```

## Running Tests

```bash
pytest tests/ -v
```

## Deploy to GCP (Cloud Run + GCS + BigQuery)

Deploy using Cloud Build and Terraform:

```powershell
# Deploy container and infrastructure
.\dag\deploy-cloudbuild.ps1

# Trigger the Cloud Run Job
.\dag\trigger_sync.ps1
```

Or using standard Terraform:

```bash
cd terraform/minimal
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars with your project_id, sync_image, and uniblock_api_key

terraform init
terraform apply

# Run the job manually
gcloud run jobs execute agent-accounting-sync --region=us-central1
```

## Documentation & Architecture

- **[GCP Pipeline Architecture](docs/pipeline_architecture_gcp.md):** Full Cloud Run, Cloud Scheduler, Cloud Workflows, BigQuery, and GCS pipeline specifications.
- **[How to Trigger ETL on GCP](docs/how_to_trigger_etl_on_gcp.md):** Step-by-step operational guide for triggering, monitoring, and debugging Cloud Run sync runs.
- **[Audit Reports & Dashboards](docs/report/README.md):** Automated Markdown value checks and interactive HTML portfolio dashboards.
- **[Terraform IaC](terraform/README.md):** Infrastructure-as-Code definitions.
