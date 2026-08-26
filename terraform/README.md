# Zerion GCP Pipeline — Terraform

Infrastructure-as-Code for the Zerion data pipeline on GCP.

## What it deploys

- **Cloud Storage** bucket for raw JSON data
- **BigQuery** dataset + partitioned raw tables
- **Secret Manager** secret for `ZERION_API_KEY`
- **Service account** with least-privilege IAM bindings
- **Cloud Run Job** that runs the Python sync script
- **Cloud Workflows** orchestration definition
- **Cloud Scheduler** job to trigger the workflow every 30 minutes

## Prerequisites

1. GCP project with billing enabled.
2. APIs enabled: `run.googleapis.com`, `storage.googleapis.com`, `bigquery.googleapis.com`, `secretmanager.googleapis.com`, `workflows.googleapis.com`, `cloudscheduler.googleapis.com`.
3. A container image for the sync script pushed to Artifact Registry (see the parent doc).

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars

terraform init
terraform plan
terraform apply
```

## Manual test

```bash
gcloud run jobs execute zerion-sync --region=us-central1
gcloud workflows executions list zerion-pipeline --location=us-central1
```
