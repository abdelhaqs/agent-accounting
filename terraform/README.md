# Agent Accounting GCP Pipeline — Terraform

Infrastructure-as-Code for the Agent Accounting data pipeline on GCP.

## What it deploys

- **Cloud Storage** bucket for raw JSON data (`agent-accounting-raw-data`)
- **BigQuery** dataset + partitioned raw tables (`agent_accounting`)
- **Secret Manager** secret for `UNIBLOCK_API_KEY`
- **Service account** (`accounting-sync`) with least-privilege IAM bindings
- **Cloud Run Job** (`agent-accounting-sync`) that runs the Python sync pipeline
- **Cloud Workflows** (`agent-accounting-pipeline`) orchestration definition
- **Cloud Scheduler** job (`agent-accounting-30min`) to trigger the workflow every 30 minutes

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
gcloud run jobs execute agent-accounting-sync --region=us-central1
gcloud workflows executions list agent-accounting-pipeline --location=us-central1
```
