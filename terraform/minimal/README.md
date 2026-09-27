# Agent Accounting GCP Minimal Deployment

This is the simplest production-like deployment: a **Cloud Run Job** that pulls data from the Uniblock/DeBank API and writes raw/processed JSON files directly to **Cloud Storage** via a GCS volume mount.

## What it deploys

- **Cloud Storage** bucket for raw JSON output (`agent-accounting-raw-data`)
- **Secret Manager** secret for `UNIBLOCK_API_KEY`
- **Service account** (`accounting-sync`) with permissions to read the secret and write to the bucket
- **Cloud Run Job** (`agent-accounting-sync`) that runs the Python sync pipeline with the GCS bucket mounted at `/output`
- **BigQuery** warehouse dataset (`agent_accounting`) with `transfers`, `balances`, and `balance_reconciliation` tables

## Before you start

1. Create a GCP project and enable billing.
2. Enable these APIs:
   ```bash
   gcloud services enable run.googleapis.com storage.googleapis.com secretmanager.googleapis.com bigquery.googleapis.com artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
   ```
3. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) and authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
4. Install [Terraform](https://developer.hashicorp.com/terraform/install).

## Build and push the container

From the project root:

```bash
export PROJECT_ID=YOUR_PROJECT_ID
export REGION=us-central1
export REPO=agent-accounting

gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION || true
gcloud auth configure-docker $REGION-docker.pkg.dev

docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/agent-accounting-sync:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/agent-accounting-sync:latest
```

## Deploy with Terraform

```bash
cd terraform/minimal
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars with your project_id, sync_image, and uniblock_api_key

terraform init
terraform plan
terraform apply
```

## Run the job manually

```bash
gcloud run jobs execute agent-accounting-sync --region=us-central1 --project=YOUR_PROJECT_ID
```

## Check the output

```bash
gcloud storage ls gs://YOUR_PROJECT_ID-agent-accounting-raw-data/
```

## Next steps

Once this works, add Cloud Scheduler + Cloud Workflows (see [`terraform/`](../)) to run it automatically every 30 minutes.
