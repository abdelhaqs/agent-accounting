# Project Handoff — Zerion Agent Accounting Pipeline

> This document captures the current state and next steps so a Kimi agent (or anyone) can pick up the work later.
> Last updated: 2026-08-26

---

## 1. Project Overview

**Goal:** Track ERC-20 transfers and current token balances for multiple on-chain wallets ("agents") using the Zerion API, then land the data in Google Cloud Storage as the first stage of a data pipeline.

**Current scope (MVP):**
- Pull transactions and positions from the Zerion API for each configured wallet.
- Extract every ERC-20 transfer and current balance (including vault/LP receipt tokens).
- Export raw API pages + processed `transfers.json` / `balances.json` to local disk or GCS.
- Deploy as a Cloud Run Job on GCP with a GCS volume mount so output lands directly in a bucket.

**Out of scope for now:**
- BigQuery loading and transformations.
- dbt models.
- Scheduled/automated runs (Cloud Scheduler + Workflows).
- Multi-chain support beyond Base.

---

## 2. Repository & Environment

### GitHub
- **Repository:** https://github.com/abdelhaqs/agent-accounting
- **Default branch:** `main`
- **Local clone:** `C:\Users\chris\Projects\agent-accounting`
- **Old folder (can be deleted):** `C:\Users\chris\Projects\ZerionBond`

### GCP Project
- **Project ID:** `agent-accounting-506719`
- **Region:** `us-central1`
- **Artifact Registry repo:** `zerion` (Docker)
- **Container image:** `us-central1-docker.pkg.dev/agent-accounting-506719/zerion/zerion-sync:latest`
- **GCS bucket:** `agent-accounting-506719-zerion-raw-data`
- **Cloud Run Job:** `zerion-sync`
- **Secret Manager secret:** `zerion-api-key`

### Agents being tracked
See `agents.yaml`:

| Agent name | Address |
|------------|---------|
| Yieldseeker Base Agent 2 | `0xe51b7dba38e732a19838c3f23816df7092441597` |
| ZyFAI Base Agent 2 | `0xBf96c935F7cB35b86Efaa0693D81d875f4B4e7eb` |
| Mamo Base Agent 2 | `0x53d78cc346e05f153401ac4c0c7626062e0b9a40` |
| Surfliquid Base Agent 1 | `0x0373beEef981B60dD35D05db9D32DDc100474a11` |

**Note:** Zerion returns "Unsupported address" for `0xe51b...` and `0x53d7...`. The script skips them gracefully and continues with the supported addresses. This is a Zerion indexing limitation, not a code bug.

---

## 3. What Is Already Done

### Code
- `main.py` — syncs transactions and balances, exports JSON, handles unsupported addresses, logs to `zerion_sync.log`.
- `zerion_client.py` — Zerion API client with retries and pagination.
- `storage.py` — SQLite persistence with `agent_name` support.
- `test_sync.py` — 9 unit tests, all passing.
- `agents.yaml` — config file for tracking multiple wallets.
- `Dockerfile` — container image for Cloud Run Job.
- `.dockerignore` and updated `.gitignore`.

### Documentation
- `README.md` — setup, usage, minimal GCP deploy guide.
- `docs/pipeline_architecture_gcp.md` — full GCP architecture (Cloud Run → GCS → BigQuery → dbt) with Terraform IaC.
- `docs/cost_estimate_gcp.md` — cost estimate (~$6–9/month for 4 agents every 30 min).
- `docs/pipeline_diagram_gcp.png` — architecture diagram.

### Terraform
- `terraform/` — full pipeline module (Cloud Run Job + GCS + BigQuery + Workflows + Scheduler).
- `terraform/minimal/` — stripped-down module for the current MVP: only Cloud Run Job + GCS + Secret Manager.
- `terraform/minimal/terraform.tfvars` — created with project ID and image URL prefilled. **Still needs the Zerion API key pasted in.**

### Validation
- `python -m unittest test_sync -v` — 9/9 tests pass.
- `terraform validate` passes for both `terraform/` and `terraform/minimal/`.

---

## 4. What Is NOT Done Yet

The GCP infrastructure has **not** been deployed yet. The next owner needs to:

1. Paste the Zerion API key into `terraform/minimal/terraform.tfvars`.
2. Enable GCP APIs.
3. Build and push the Docker image to Artifact Registry.
4. Run `terraform apply` in `terraform/minimal/`.
5. Execute the Cloud Run Job manually and verify files appear in GCS.
6. (Later) Add Cloud Scheduler + Workflows for automation.
7. (Later) Add BigQuery + dbt for transformations.

---

## 5. Immediate Next Steps (MVP Deploy)

### Step 0 — Prerequisites
Ensure the following are installed and authenticated:
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) — run `gcloud auth login` and `gcloud config set project agent-accounting-506719`
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — Docker daemon running
- [Terraform](https://developer.hashicorp.com/terraform/install)

### Step 1 — Paste the API key
Open this file:

```text
C:\Users\chris\Projects\agent-accounting\terraform\minimal\terraform.tfvars
```

Replace:

```hcl
zerion_api_key = "PASTE_YOUR_ZERION_API_KEY_HERE"
```

with the actual key. This file is gitignored and will not be committed.

### Step 2 — Run the deploy commands
Open PowerShell in `C:\Users\chris\Projects\agent-accounting` and run:

```powershell
$env:PROJECT_ID = "agent-accounting-506719"
$env:REGION = "us-central1"
$env:REPO = "zerion"

# Enable required APIs
gcloud services enable run.googleapis.com storage.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com --project=$env:PROJECT_ID

# Create Artifact Registry repository (may say "already exists", that's fine)
gcloud artifacts repositories create $env:REPO --repository-format=docker --location=$env:REGION
gcloud auth configure-docker "$env:REGION-docker.pkg.dev"

# Build and push container image
docker build -t "$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPO/zerion-sync:latest" .
docker push "$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPO/zerion-sync:latest"

# Deploy GCS bucket, Secret Manager, service account, and Cloud Run Job
cd terraform/minimal
terraform init
terraform apply
```

When `terraform apply` prompts, type `yes`.

### Step 3 — Run the job manually

```powershell
gcloud run jobs execute zerion-sync --region=$env:REGION --project=$env:PROJECT_ID
```

### Step 4 — Verify output in GCS

```powershell
gcloud storage ls "gs://$env:PROJECT_ID-zerion-raw-data/"
```

Expected structure:

```text
gs://agent-accounting-506719-zerion-raw-data/zyfai_base_agent_2/
gs://agent-accounting-506719-zerion-raw-data/zyfai_base_agent_2/transfers.json
gs://agent-accounting-506719-zerion-raw-data/zyfai_base_agent_2/balances.json
gs://agent-accounting-506719-zerion-raw-data/zyfai_base_agent_2/raw_transactions.json
gs://agent-accounting-506719-zerion-raw-data/zyfai_base_agent_2/raw_positions.json
...
```

Two of the four agents will likely fail with "Unsupported address"; the other two should produce output.

---

## 6. How the Minimal Deploy Works

1. The `Dockerfile` builds an image that runs `python main.py --output-dir /output`.
2. The Cloud Run Job mounts the GCS bucket at `/output` using Cloud Storage FUSE.
3. The script writes JSON files to `/output/<agent>/`, which appears directly in the bucket.
4. The Zerion API key is injected from Secret Manager as the `ZERION_API_KEY` environment variable.
5. `CHAIN_IDS=base` is set so only Base chain data is synced.

No code changes were needed to upload to GCS — the volume mount handles it.

---

## 7. Common Issues & Notes

### "Unsupported address" errors
Two addresses (`0xe51b...` and `0x53d7...`) are not tracked by Zerion's wallet endpoints. This is expected. The script logs the error, skips the agent, and continues.

### PowerShell vs Git Bash
The user works in PowerShell. Use `$env:VAR = "value"` instead of `export VAR=value`.

### Docker Desktop must be running
If `docker build` fails with "Cannot connect to the Docker daemon", start Docker Desktop first.

### Artifact Registry repo already exists
If `gcloud artifacts repositories create` fails with "Repo already exists", ignore it and continue.

### Terraform state
State is stored locally in `terraform/minimal/terraform.tfstate`. Do not delete it. If multiple people/machines will run Terraform, move state to a GCS backend later.

### API key security
- Never commit the API key.
- `terraform.tfvars` is gitignored.
- The key is stored in GCP Secret Manager by Terraform.

---

## 8. Files & Their Purpose

| File / Directory | Purpose |
|------------------|---------|
| `main.py` | Entry point: syncs agents, handles errors, exports JSON. |
| `zerion_client.py` | Zerion API client with retries and pagination. |
| `storage.py` | SQLite storage for transfers and balances. |
| `agents.yaml` | List of wallets/agents to track. |
| `Dockerfile` | Container image for Cloud Run Job. |
| `.dockerignore` | Excludes secrets, DB, logs, output from Docker build. |
| `.gitignore` | Excludes env files, DBs, logs, Terraform state. |
| `README.md` | Project overview + minimal deploy guide. |
| `docs/pipeline_architecture_gcp.md` | Full GCP architecture docs + Terraform. |
| `docs/cost_estimate_gcp.md` | Monthly cost estimate. |
| `terraform/` | Full pipeline Terraform (Cloud Run + GCS + BigQuery + Workflows + Scheduler). |
| `terraform/minimal/` | MVP Terraform (Cloud Run + GCS only). |
| `terraform/minimal/terraform.tfvars` | Local config with API key placeholder. |
| `test_sync.py` | Unit tests. |

---

## 9. Suggested Roadmap After MVP

1. **Schedule runs** — add Cloud Scheduler + Cloud Workflows (`terraform/` module has this).
2. **Load into BigQuery** — add BigQuery raw tables and a loader step.
3. **Transform with dbt** — staging/intermediate/mart models.
4. **Dashboards / API** — Looker Studio or Cloud Run service reading BigQuery.
5. **Add more agents / chains** — update `agents.yaml` and `chain_ids`.

---

## 10. Quick Reference Commands

Run tests:
```powershell
python -m unittest test_sync -v
```

Run locally:
```powershell
python main.py
```

Build container:
```powershell
docker build -t us-central1-docker.pkg.dev/agent-accounting-506719/zerion/zerion-sync:latest .
```

Run Cloud Run Job:
```powershell
gcloud run jobs execute zerion-sync --region=us-central1 --project=agent-accounting-506719
```

List GCS output:
```powershell
gcloud storage ls gs://agent-accounting-506719-zerion-raw-data/
```

Destroy Terraform resources (if needed):
```powershell
cd terraform/minimal
terraform destroy
```
