# Zerion GCP Minimal Deployment

This is the simplest production-like deployment: a **Cloud Run Job** that pulls data from the Zerion API and writes raw/processed JSON files directly to **Cloud Storage** via a GCS volume mount.

No BigQuery, no dbt, no scheduler yet — just API → GCS.

## What it deploys

- **Cloud Storage** bucket for raw JSON output
- **Secret Manager** secret for `ZERION_API_KEY`
- **Service account** with permissions to read the secret and write to the bucket
- **Cloud Run Job** that runs the Python sync script with the GCS bucket mounted at `/output`

## Before you start

1. Create a GCP project and enable billing.
2. Enable these APIs:
   ```bash
   gcloud services enable run.googleapis.com storage.googleapis.com secretmanager.googleapis.com --project=YOUR_PROJECT_ID
   ```
3. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) and authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
4. Install [Terraform](https://developer.hashicorp.com/terraform/install).

## Build and push the container

From the project root (not this directory):

```bash
export PROJECT_ID=YOUR_PROJECT_ID
export REGION=us-central1
export REPO=zerion

gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION || true
gcloud auth configure-docker $REGION-docker.pkg.dev

docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/zerion-sync:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/zerion-sync:latest
```

## Deploy with Terraform

```bash
cd terraform/minimal
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars with your project_id, sync_image, and zerion_api_key

terraform init
terraform plan
terraform apply
```

## Run the job manually

```bash
gcloud run jobs execute zerion-sync --region=us-central1 --project=YOUR_PROJECT_ID
```

## Check the output

```bash
gcloud storage ls gs://YOUR_PROJECT_ID-zerion-raw-data/
```

You should see per-agent folders like:

```text
gs://your-project-zerion-raw-data/zyfai_base_agent_2/
gs://your-project-zerion-raw-data/zyfai_base_agent_2/transfers.json
gs://your-project-zerion-raw-data/zyfai_base_agent_2/balances.json
gs://your-project-zerion-raw-data/zyfai_base_agent_2/raw_transactions.json
gs://your-project-zerion-raw-data/zyfai_base_agent_2/raw_positions.json
```

## Next steps

Once this works, add Cloud Scheduler + Cloud Workflows (see [`terraform/`](../)) to run it automatically every 30 minutes, then add BigQuery + dbt for transformations.
