# Zerion GCP Deployment Script (Cloud Build - no local Docker needed)
# Run this from the project root: C:\Users\chris\Projects\agent-accounting
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Terraform installed
#   - Zerion API key pasted in terraform/minimal/terraform.tfvars
#   - Docker Desktop NOT required (builds in Cloud Build)

$ErrorActionPreference = "Stop"

$PROJECT_ID = "agent-accounting-506719"
$REGION = "us-central1"
$REPO = "zerion"
$IMAGE = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/zerion-sync:latest"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Zerion Wallet Tracker - GCP Deploy" -ForegroundColor Cyan
Write-Host "  (Cloud Build - no local Docker)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Validate prerequisites ---
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow

$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
$terraform = Get-Command terraform -ErrorAction SilentlyContinue

if (-not $gcloud) { throw "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install" }
if (-not $terraform) { throw "Terraform not found. Install from https://developer.hashicorp.com/terraform/install" }

Write-Host "  gcloud:    $($gcloud.Source)" -ForegroundColor Green
Write-Host "  terraform: $($terraform.Source)" -ForegroundColor Green
Write-Host "  (Docker Desktop not required - using Cloud Build)" -ForegroundColor Green
Write-Host ""

# --- Validate tfvars has real API key ---
$tfvarsPath = "terraform/minimal/terraform.tfvars"
$tfvarsContent = Get-Content $tfvarsPath -Raw

if ($tfvarsContent.Contains('PASTE_YOUR_ZERION_API_KEY_HERE')) {
    throw "Zerion API key is still set to placeholder in $tfvarsPath. Please paste your real key."
}

$re = New-Object System.Text.RegularExpressions.Regex 'zerion_api_key\s*=\s*"([^"]+)"'
$m = $re.Match($tfvarsContent)
if ($m.Success) {
    Write-Host "  Zerion API key: configured (length=$($m.Groups[1].Value.Length))" -ForegroundColor Green
} else {
    throw "Could not find zerion_api_key in $tfvarsPath"
}
Write-Host ""

# --- Set gcloud project ---
Write-Host "[2/6] Setting gcloud project to $PROJECT_ID..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host ""

# --- Enable APIs ---
Write-Host "[3/6] Enabling required GCP APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com storage.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com --project=$PROJECT_ID
Write-Host "  APIs enabled." -ForegroundColor Green
Write-Host ""

# --- Build and push container via Cloud Build ---
Write-Host "[4/6] Building and pushing container image via Cloud Build..." -ForegroundColor Yellow

# Create artifact registry repo if it doesn't exist
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "  Repo may already exist, continuing..." -ForegroundColor DarkGray }

gcloud builds submit --tag $IMAGE .
if ($LASTEXITCODE -ne 0) { throw "Cloud Build failed" }

Write-Host "  Image built and pushed: $IMAGE" -ForegroundColor Green
Write-Host ""

# --- Terraform apply ---
Write-Host "[5/6] Running Terraform apply..." -ForegroundColor Yellow
Push-Location terraform/minimal
terraform init
terraform apply -auto-approve
if ($LASTEXITCODE -ne 0) { throw "Terraform apply failed" }
Pop-Location
Write-Host "  Infrastructure deployed." -ForegroundColor Green
Write-Host ""

# --- Execute job ---
Write-Host "[6/6] Executing Cloud Run Job..." -ForegroundColor Yellow
gcloud run jobs execute zerion-sync --region=$REGION --project=$PROJECT_ID
Write-Host "  Job execution started." -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check output in GCS:" -ForegroundColor Yellow
Write-Host "  gcloud storage ls gs://$PROJECT_ID-zerion-raw-data/" -ForegroundColor White
Write-Host ""
Write-Host "View job logs:" -ForegroundColor Yellow
Write-Host "  gcloud logging read 'resource.type=cloud_run_job resource.labels.job_name=zerion-sync' --limit=50 --project=$PROJECT_ID" -ForegroundColor White
Write-Host ""
Write-Host "Run job manually again:" -ForegroundColor Yellow
Write-Host "  gcloud run jobs execute zerion-sync --region=$REGION --project=$PROJECT_ID" -ForegroundColor White
Write-Host ""
Write-Host "Destroy infrastructure (if needed):" -ForegroundColor Yellow
Write-Host "  cd terraform/minimal && terraform destroy" -ForegroundColor White
