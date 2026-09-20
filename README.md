# Zerion Wallet Tracker

Sync ERC-20 transfer history and current token balances (including vault share tokens) for one or many wallets/agents using the [Zerion API](https://developers.zerion.io/).

## What it does

1. Pulls every transaction for each configured wallet/agent via `GET /v1/wallets/{wallet}/transactions`.
2. Extracts each ERC-20 transfer, recording direction (`in`/`out`), token, amount, USD value, sender, recipient, chain, and timestamp.
3. Pulls current positions via `GET /v1/wallets/{wallet}/positions?filter[positions]=no_filter` so vault share / LP / receipt tokens are included.
4. Stores everything in a local SQLite database (`zerion.db`), tagged by wallet and agent name.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with your ZERION_API_KEY
```

## Configuring agents (wallets)

The script reads wallets from `agents.yaml` by default. Each wallet is treated as an "agent" and gets its own raw + processed data.

Example `agents.yaml`:

```yaml
agents:
  - name: Yieldseeker Base Agent 2
    address: "0xe51b7dba38e732a19838c3f23816df7092441597"
  - name: ZyFAI Base Agent 2
    address: "0xBf96c935F7cB35b86Efaa0693D81d875f4B4e7eb"
```

`name` is optional — if omitted, the wallet address is used as the agent name and output folder name:

```yaml
agents:
  - address: "0xe51b7dba38e732a19838c3f23816df7092441597"
```

If `agents.yaml` is missing, the script falls back to `WALLET_ADDRESS` in `.env`.

## Run

Just run:

```bash
python main.py
```

This syncs all agents and exports both processed and raw JSON into per-agent folders under `./output/`.

### Output layout

```text
output/
├── yieldseeker_base_agent_2/
│   ├── 20260829_190255/
│   │   ├── transfers.json
│   │   ├── balances.json
│   │   ├── raw_transactions_20260829_190255.json
│   │   └── raw_positions_20260829_190255.json
│   └── 20260829_193044/
│       └── ...
└── zyfai_base_agent_2/
    └── ...
```

### Optional flags

```bash
python main.py --db-path mydata.db --full-resync --rate-limit-delay 0.5 --chain-ids base --output-dir ./data
```

- `--db-path`: SQLite database file (default `zerion.db`).
- `--full-resync`: Drop existing transfer data and re-fetch from the beginning.
- `--rate-limit-delay`: Seconds to sleep between paginated API requests. Increase this if you hit 429s on the free plan (default `0.25`).
- `--chain-ids`: Comma-separated chain ids to sync, e.g. `base` or `base,ethereum` (default: `base`; env: `CHAIN_IDS`; set empty for all chains).
- `--agents-config`: Path to the agents YAML config (default `agents.yaml`; env `AGENTS_CONFIG`).
- `--output-dir`: Directory for per-agent exports (default `./output`).
- `--no-export`: Skip exporting JSON files (only update SQLite).
- `--log-file`: Log file path (default `zerion_sync.log`; set to empty string to disable file logging).

## Error handling

If Zerion returns an error for a specific agent (e.g., "Unsupported address"), the script logs the error, skips that agent, and continues with the rest. A summary of failed agents is printed at the end.

## Database tables

- `transfers` — one row per ERC-20 transfer, includes `wallet` and `agent_name`.
- `balances` — current balance per token per agent, includes `wallet` and `agent_name`.

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

## Tests

```bash
python -m unittest test_sync -v
```

## Deploy to GCP (minimal: API → Cloud Storage)

The fastest way to run this in GCP is to deploy the sync script as a **Cloud Run Job** and mount a **Cloud Storage** bucket at `/output`. No code changes are needed — the script writes the same JSON files it writes locally, but they land directly in GCS.

See the full minimal deployment guide in [`terraform/minimal/`](terraform/minimal/). Quick summary:

```bash
# 1. Build and push the container image
export PROJECT_ID=your-gcp-project
export REGION=us-central1
export REPO=zerion

gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION || true
gcloud auth configure-docker $REGION-docker.pkg.dev

docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/zerion-sync:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/zerion-sync:latest

# 2. Deploy the bucket, secret, service account, and Cloud Run Job
cd terraform/minimal
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform apply

# 3. Run it once manually
gcloud run jobs execute zerion-sync --region=$REGION --project=$PROJECT_ID

# 4. List the output in GCS
gcloud storage ls gs://$PROJECT_ID-zerion-raw-data/
```

Once this is working, add Cloud Scheduler + Cloud Workflows (see [`terraform/`](../terraform)) to run it automatically, then layer on BigQuery and dbt later.

## Documentation & Architecture

Complete technical specifications, runbooks, and architectures are located in [`docs/`](docs/README.md):

### Python ETL Pipeline Scripts (`docs/etl/`)
- **[`main.py`](docs/etl/main.md):** Pipeline orchestrator, multi-agent loop, staging, and archiving.
- **[`zerion_client.py`](docs/etl/zerion_client.md):** Primary Zerion REST API client (portfolio, positions, transfers).
- **[`uniblock_client.py`](docs/etl/uniblock_client.md):** Uniblock Unified API client with automated dual-key failover.
- **[`rpc_client.py`](docs/etl/rpc_client.md):** Base JSON-RPC node client for independent contract ground-truth checks.
- **[`storage.py`](docs/etl/storage.md):** Local SQLite engine (`zerion.db`) schemas and upsert operations for offline testing.
- **[`bigquery_loader.py`](docs/etl/bigquery_loader.md):** Google BigQuery streaming/batch ingestion schemas and tables.

### Architecture & Operations Guides
- **[Documentation Index](docs/README.md):** Master catalog of all documentation.
- **[Core Production Architecture](docs/core_pipeline_and_storage.md):** High-level 3-stage production architecture (Extract, Verify, Archive & Load).
- **[Local Testing & Development Guide](docs/local_testing_and_development.md):** Guide for offline development, local SQLite (`zerion.db`), diagnostic tools, and unit testing.
- **[RPC Client Architecture & Flow](docs/rpc_client_architecture.md):** Base JSON-RPC verification architecture, ABI method selectors, and failover diagram.
- **[Scripts Documentation Manual](docs/scripts_documentation.md):** Reference guide for all 18 Python and PowerShell operational scripts.
- **[GCP Production Cost Audit](docs/cost_estimate_gcp.md):** Real-world cost breakdown based on 30 days of production telemetry ($0.00 – $0.15/mo).
- **[Data Provider Evaluation](docs/provider_evaluation_report.md):** Zerion REST API vs. Uniblock Unified API coverage, latency, and reliability.
- **[Portfolio Comparisons & Value Checks](docs/comparisons_and_value_checks/README.md):** Historical balance mismatch reports, reconciliation audits, and multi-agent comparisons.
- **[GCP Enterprise Architecture](docs/pipeline_architecture_gcp.md):** Full Cloud Run, Cloud Scheduler, Cloud Build, Artifact Registry, BigQuery, and GCS architecture ([Diagram](docs/pipeline_diagram_gcp.png)).
- **[AWS / Supabase Architecture](docs/pipeline_architecture.md):** Alternative staging architecture ([Diagram](docs/pipeline_diagram.png)).
- **[GCP Terraform IaC](terraform/):** Infrastructure-as-Code definitions ([Minimal IaC](terraform/minimal/)).

## Knowledge Base

### Zerion returns "Unsupported address" for some agents

If the script logs `HTTPError: 400 Client Error: Bad Request` with an "Unsupported address" message for an agent, it means Zerion does not index or track that address through its `/wallets/...` endpoints.

Common causes:

1. **The address is a smart contract, not an EOA** — Vault, pool, or agent-contract addresses are often rejected by Zerion's wallet endpoints even if they hold tokens.
2. **Zerion hasn't indexed the address yet** — Low-activity or newly deployed addresses may not be in Zerion's index.
3. **Wrong address copied** — Always verify the address on a block explorer.

How to investigate:

- Check the address on [Basescan](https://basescan.org) to see if it is a contract or an EOA.
- Try the address in the Zerion web/mobile app. If Zerion can't display it there, the API won't work either.
- For contract addresses that Zerion doesn't support, you typically need to read events directly from an RPC node rather than using Zerion's wallet API.

The script handles this gracefully: it logs the failure, skips the unsupported agent, and continues with the rest. Failed agents are summarized at the end of the run.
