# Zerion Wallet Tracker — GCP Deployment Guide

> **Project:** `agent-accounting`  
> **GCP Project:** `agent-accounting-506719`  
> **Region:** `us-central1`  
> **Last updated:** 2026-08-28

---

## Overview

This guide covers deploying the Zerion Wallet Tracker to GCP as a **Cloud Run Job** that writes output to **Cloud Storage** via a GCS volume mount. The job syncs ERC-20 transfers and token balances from the Zerion API for configured wallet addresses.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Cloud Scheduler │────▶│  Cloud Run Job  │────▶│  Cloud Storage  │
│  (every 6 hrs)   │     │  (zerion-sync)  │     │  (JSON output)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌───────────────┐
                        │ Secret Manager│
                        │ Zerion API Key│
                        └───────────────┘
```

---

## Prerequisites

### Tools Required

| Tool | Purpose | Verify Command |
|------|---------|---------------|
| gcloud CLI | GCP authentication & API access | `gcloud --version` |
| Docker Desktop | Build container image | `docker --version` |
| Terraform | Infrastructure as Code | `terraform --version` |

### Install gcloud CLI (if missing)

```powershell
# Download and install silently
New-Item -ItemType Directory -Force -Path "$env:TEMP\gcloud-install" | Set-Location
Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -OutFile "$env:TEMP\gcloud-install\GoogleCloudSDKInstaller.exe"
& "$env:TEMP\gcloud-install\GoogleCloudSDKInstaller.exe" /S /allusers /noreporting

# Add to PATH for current session
$env:PATH = "$env:PATH;$env:ProgramFiles(x86)\Google\Cloud SDK\google-cloud-sdk\bin"
```

### GCP Setup

1. Create a GCP project and enable billing.
2. Authenticate:
   ```powershell
   gcloud auth login
   gcloud auth application-default login   # REQUIRED for Terraform
   gcloud config set project YOUR_PROJECT_ID
   ```

> ⚠️ **CRITICAL:** `gcloud auth application-default login` is **mandatory** for Terraform. Without it, `terraform apply` will fail with a credentials error (see [Error #2](#error-2-terraform-missing-application-default-credentials)).

---

## Configuration

### 1. Clone the Repository

```powershell
git clone https://github.com/abdelhaqs/agent-accounting.git
cd agent-accounting
```

### 2. Configure `terraform.tfvars`

Copy the example and fill in your values:

```powershell
cd terraform/minimal
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id = "your-gcp-project-id"
region     = "us-central1"

# Container image URL (will be built and pushed in Step 4)
sync_image = "us-central1-docker.pkg.dev/your-gcp-project-id/zerion/zerion-sync:latest"

# Your Zerion API key from https://developers.zerion.io/
zerion_api_key = "zk_..."

# Optional: comma-separated chain IDs (default: base)
chain_ids = "base"
```

> ⚠️ **SECURITY:** `terraform.tfvars` is gitignored. Never commit your API key.

### 3. Configure Agents (Optional)

Edit `agents.yaml` in the project root to specify which wallets to track:

```yaml
agents:
  - name: ZyFAI Base Agent 2
    address: "0xBf96c935F7cB35b86Efaa0693D81d875f4B4e7eb"
  - name: Surfliquid Base Agent 1
    address: "0x0373beEef981B60dD35D05db9D32DDc100474a11"
```

If `agents.yaml` is missing, the script falls back to `WALLET_ADDRESS` in `.env`.

---

## Deployment Steps

### Step 1: Enable GCP APIs

```powershell
$PROJECT_ID = "your-gcp-project-id"

gcloud services enable run.googleapis.com storage.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com --project=$PROJECT_ID
```

### Step 2: Configure Docker for Artifact Registry

```powershell
$REGION = "us-central1"
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
```

### Step 3: Create Artifact Registry Repository

```powershell
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$REPO = "zerion"

gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION --project=$PROJECT_ID
```

> If it says "ALREADY_EXISTS", that's fine — continue.

### Step 4: Build and Push Container Image

```powershell
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$IMAGE = "$REGION-docker.pkg.dev/$PROJECT_ID/zerion/zerion-sync:latest"

cd C:\Users\chris\Projects\agent-accounting   # or your project root
docker build -t $IMAGE .
docker push $IMAGE
```

### Step 5: Deploy Infrastructure with Terraform

```powershell
cd terraform/minimal
terraform init
terraform apply -auto-approve
```

This creates:
- Cloud Storage bucket: `YOUR_PROJECT_ID-zerion-raw-data`
- Secret Manager secret: `zerion-api-key`
- Service account: `zerion-sync@YOUR_PROJECT_ID.iam.gserviceaccount.com`
- Cloud Run Job: `zerion-sync`

### Step 6: Execute the Job Manually (First Run)

```powershell
gcloud run jobs execute zerion-sync --region=us-central1 --project=YOUR_PROJECT_ID
```

### Step 7: Verify Output in GCS

```powershell
gcloud storage ls gs://YOUR_PROJECT_ID-zerion-raw-data/
```

Expected:
```
gs://YOUR_PROJECT_ID-zerion-raw-data/zyfai_base_agent_2/
gs://YOUR_PROJECT_ID-zerion-raw-data/surfliquid_base_agent_1/
```

---

## Add Automated Scheduling (Optional)

### Add Cloud Scheduler — Every 6 Hours (00:00, 06:00, 12:00, 18:00 UTC)

```powershell
$PROJECT_ID = "your-gcp-project-id"

# 1. Grant the service account permission to trigger Cloud Run Jobs
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:zerion-sync@$PROJECT_ID.iam.gserviceaccount.com" `
  --role="roles/run.invoker"

# 2. Create the scheduled job
gcloud scheduler jobs create http zerion-sync-6hr `
  --schedule="0 0,6,12,18 * * *" `
  --uri="https://us-central1-run.googleapis.com/v2/projects/$PROJECT_ID/locations/us-central1/jobs/zerion-sync:run" `
  --http-method=POST `
  --oauth-service-account-email="zerion-sync@$PROJECT_ID.iam.gserviceaccount.com" `
  --time-zone="UTC" `
  --location="us-central1" `
  --description="Trigger Zerion sync every 6 hours"

# 3. Verify
gcloud scheduler jobs list --location=us-central1 --project=$PROJECT_ID
```

### Manage the Schedule

| Action | Command |
|--------|---------|
| Pause | `gcloud scheduler jobs pause zerion-sync-6hr --location=us-central1 --project=$PROJECT_ID` |
| Resume | `gcloud scheduler jobs resume zerion-sync-6hr --location=us-central1 --project=$PROJECT_ID` |
| Delete | `gcloud scheduler jobs delete zerion-sync-6hr --location=us-central1 --project=$PROJECT_ID` |
| View logs | `gcloud scheduler jobs logs zerion-sync-6hr --location=us-central1 --project=$PROJECT_ID` |

---

## Errors Encountered & Solutions

### Error #1: PowerShell Regex Parsing Error

**Symptom:**
```
At deploy.ps1:44 char:52
+ if ($tfvarsContent -match 'zerion_api_key\s*=\s*"([^"]+)"') {
+                                                    ~
Missing type name after '['.
```

**Cause:** Windows PowerShell 5.1 misinterprets `[` brackets inside regex patterns when using the `-match` operator.

**Solution:** Use `System.Text.RegularExpressions.Regex` instead of `-match`:

```powershell
# ❌ Broken in PowerShell 5.1
if ($tfvarsContent -match 'zerion_api_key\s*=\s*"([^"]+)"') { ... }

# ✅ Works in all PowerShell versions
$re = New-Object System.Text.RegularExpressions.Regex 'zerion_api_key\s*=\s*"([^"]+)"'
$m = $re.Match($tfvarsContent)
if ($m.Success) { ... }
```

**Prevention:** Use manual deployment steps instead of the `deploy.ps1` script, or ensure the script uses `[regex]` objects for all regex operations.

---

### Error #2: Terraform Missing Application Default Credentials

**Symptom:**
```
Error: Attempted to load application default credentials since neither
`credentials` nor `access_token` was set in the provider block.
No credentials loaded. To use your gcloud credentials, run
'gcloud auth application-default login'.
```

**Cause:** Terraform uses Application Default Credentials (ADC), which are separate from `gcloud auth login`.

**Solution:**
```powershell
gcloud auth application-default login
```

Then re-run:
```powershell
terraform apply -auto-approve
```

**Prevention:** Always run both authentication commands before deploying:
```powershell
gcloud auth login                        # For gcloud CLI commands
gcloud auth application-default login    # For Terraform and client libraries
```

---

### Error #3: Cloud Run CPU Limit Too Low

**Symptom:**
```
Error 400: Invalid value specified for cpu.
Total cpu < 1 is not supported with gen2 execution environment
with cpu always allocated (unthrottled).
```

**Cause:** Cloud Run Jobs use the gen2 execution environment by default, which requires a minimum of **1 CPU**. The original terraform config used `cpu = "0.5"`.

**Solution:** Update `terraform/minimal/main.tf` (and `terraform/main.tf`):

```hcl
resources {
  limits = {
    cpu    = "1"      # ❌ Was "0.5"
    memory = "512Mi"
  }
}
```

**Prevention:** Always set `cpu >= 1` for Cloud Run v2 Jobs. Valid values: `"1"`, `"2"`, `"4"`, etc.

---

### Error #4: Terraform Syntax Error (Corrupted File)

**Symptom:**
```
Error: Unsupported argument
An argument named "depends_on" is not expected here.

Error: Argument or block definition required
```

**Cause:** The `main.tf` file had duplicate/misaligned braces after an edit, causing `depends_on` to appear outside the `google_cloud_run_v2_job` resource block.

**Solution:** Restore the correct file structure. The `depends_on` block must be inside the `google_cloud_run_v2_job` resource, not outside it. The correct structure is:

```hcl
resource "google_cloud_run_v2_job" "zerion_sync" {
  name     = "zerion-sync"
  location = var.region

  template {
    template {
      # ... containers, volumes, etc.
    }
  }

  depends_on = [
    google_secret_manager_secret_version.zerion_api_key,
    google_project_iam_member.zerion_sync_secret_accessor,
    google_storage_bucket_iam_member.zerion_sync_gcs_admin,
  ]
}
```

**Prevention:** Run `terraform validate` before `terraform apply` to catch syntax errors. Always back up `.tf` files before editing.

---

### Error #5: PowerShell Stops on gcloud stderr

**Symptom:**
```powershell
python.exe : Create request issued for: [zerion]
+   & "$exe_path" $run_args_array
+   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (...):String) [], RemoteException
```

**Cause:** PowerShell with `$ErrorActionPreference = "Stop"` treats any stderr output from external commands as a terminating error. The `gcloud artifacts repositories create` command writes info messages to stderr even on success.

**Solution:** When running scripts with `$ErrorActionPreference = "Stop"`, redirect stderr or check `$LASTEXITCODE` explicitly:

```powershell
# ❌ May fail on stderr even if successful
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION

# ✅ Safer — suppress stderr for expected info messages
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "Repo may already exist, continuing..." }
```

**Prevention:** Use manual deployment steps (Step 1-7 above) instead of automated scripts for better error visibility.

---

### Error #6: Cloud Run Job Not Found

**Symptom:**
```
ERROR: (gcloud.run.jobs.execute) NOT_FOUND: Resource 'zerion-sync' of kind 'JOB'
in region 'us-central1' in project '...' does not exist.
```

**Cause:** Attempting to execute the job before Terraform has successfully created it.

**Solution:** Ensure `terraform apply` completes successfully before running:
```powershell
gcloud run jobs execute zerion-sync --region=us-central1 --project=YOUR_PROJECT_ID
```

Check if the job exists:
```powershell
gcloud run jobs list --region=us-central1 --project=YOUR_PROJECT_ID
```

---

### Error #7: Zerion "Unsupported Address"

**Symptom (in job logs):**
```
HTTPError: 400 Client Error: Bad Request for url:
https://api.zerion.io/v1/wallets/0x.../transactions/
```

**Cause:** Zerion does not index certain addresses (smart contracts, newly deployed addresses, or low-activity wallets).

**Solution:** No code fix needed. The script gracefully skips unsupported agents and continues with the rest. Failed agents are logged at the end:
```
WARNING Completed with 2 failed agent(s): ['0xe51b...', '0x53d7...']
```

**Prevention:** Verify addresses on [Basescan](https://basescan.org) before adding them to `agents.yaml`. If Zerion's mobile/web app can't display the address, the API won't work either.

---

## File Reference

| File | Purpose |
|------|---------|
| `main.py` | Entry point: syncs agents, handles errors, exports JSON |
| `zerion_client.py` | Zerion API client with retries and pagination |
| `storage.py` | SQLite storage for transfers and balances |
| `agents.yaml` | List of wallets/agents to track |
| `Dockerfile` | Container image for Cloud Run Job |
| `terraform/minimal/main.tf` | MVP Terraform: Cloud Run + GCS + Secret Manager |
| `terraform/minimal/variables.tf` | Terraform variables |
| `terraform/minimal/terraform.tfvars` | Local config (API key, project ID) |
| `terraform/main.tf` | Full Terraform: adds BigQuery + Scheduler + Workflows |
| `deploy.ps1` | Automated deployment script (PowerShell) |
| `deploy-cloudbuild.ps1` | Cloud Build deployment script (no local Docker) |

---

## Cost Estimate

For 4 agents synced every 6 hours (~4 runs/day):

| Service | Estimated Monthly Cost |
|---------|----------------------|
| Cloud Run Job | ~$2-4 (4 runs/day × ~30 seconds × 1 vCPU × 0.5 GB) |
| Cloud Storage | ~$0.10-0.50 (small JSON files) |
| Secret Manager | ~$0.40 (1 secret, <10K accesses) |
| Cloud Scheduler | ~$0.10 (1 job) |
| **Total** | **~$3-5/month** |

---

## Destroy Everything

To tear down all infrastructure:

```powershell
cd terraform/minimal
terraform destroy -auto-approve
```

> ⚠️ This deletes the GCS bucket, Cloud Run Job, Secret Manager secret, and service account. Data in the bucket will be lost unless `force_destroy` is false (it is, by default).

---

## Next Steps

1. **Add BigQuery** — Load JSON data into queryable tables (`terraform/` module)
2. **Add dbt** — Transform raw data into staging/intermediate/mart models
3. **Dashboards** — Connect Looker Studio or Grafana to BigQuery
4. **Multi-chain** — Update `chain_ids` in `terraform.tfvars` (e.g., `"base,ethereum"`)
5. **Monitoring** — Set up Cloud Monitoring alerts for failed job executions
