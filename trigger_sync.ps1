# Trigger Zerion Sync Flow on Google Cloud Platform
# Run this from the project root: C:\Users\chris\Projects\agent-accounting
#
# Examples:
#   .\trigger_sync.ps1                        # Trigger and wait for completion, then show log
#   .\trigger_sync.ps1 -ShowLogs              # Show detailed Cloud Run execution logs
#   .\trigger_sync.ps1 -UpdateSecret          # Update GCP Secret Manager with current .env key first
#   .\trigger_sync.ps1 -DeployCode            # Rebuild image via Cloud Build first, then run job

param(
    [string]$ProjectId    = "agent-accounting-506719",
    [string]$Region       = "us-central1",
    [string]$JobName      = "zerion-sync",
    [switch]$NoWait       = $false,
    [switch]$ShowLogs     = $true,
    [switch]$UpdateSecret = $false,
    [switch]$DeployCode   = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trigger GCP Cloud Run Job Flow" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor Cyan
Write-Host "  Region:  $Region" -ForegroundColor Cyan
Write-Host "  Job:     $JobName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check prerequisites
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    throw "gcloud CLI not found. Please install the Google Cloud SDK and authenticate with 'gcloud auth login'."
}

# 2. Optionally update GCP Secret Manager with current Uniblock key
if ($UpdateSecret) {
    Write-Host "[Optional] Updating Secret Manager with new Uniblock API key..." -ForegroundColor Yellow
    
    # Read backup key from .env if available, else primary key
    $envContent = Get-Content ".env" -Raw
    $newKey = $null
    if ($envContent -match 'UNIBLOCK_API_KEY_BACKUP=([^\r\n]+)') {
        $newKey = $matches[1].Trim()
    } elseif ($envContent -match 'UNIBLOCK_API_KEY=([^\r\n]+)') {
        $newKey = $matches[1].Trim()
    }

    if ($newKey) {
        Write-Host "  Adding new version to secret 'uniblock-api-key' (ends in ...$($newKey.Substring([math]::Max(0, $newKey.Length - 6))))..." -ForegroundColor White
        $newKey | gcloud secrets versions add uniblock-api-key --data-file=- --project=$ProjectId
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Secret updated successfully." -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Failed to update secret in Secret Manager." -ForegroundColor Red
        }
    } else {
        Write-Host "  WARNING: No UNIBLOCK_API_KEY found in .env." -ForegroundColor Red
    }
    Write-Host ""
}

# 3. Optionally rebuild container image via Cloud Build
if ($DeployCode) {
    Write-Host "[Optional] Rebuilding container image with Cloud Build..." -ForegroundColor Yellow
    $REPO = "zerion"
    $IMAGE = "$Region-docker.pkg.dev/$ProjectId/$REPO/zerion-sync:latest"
    gcloud builds submit --tag $IMAGE . --project=$ProjectId
    if ($LASTEXITCODE -ne 0) { throw "Cloud Build failed." }
    Write-Host "  Build complete." -ForegroundColor Green
    Write-Host ""
}

# 4. Trigger Cloud Run Job
Write-Host "Triggering Cloud Run job '$JobName'..." -ForegroundColor Yellow
$waitFlag = if ($NoWait) { "" } else { "--wait" }

if ($waitFlag) {
    gcloud run jobs execute $JobName --region=$Region --project=$ProjectId --wait
} else {
    gcloud run jobs execute $JobName --region=$Region --project=$ProjectId
}

if ($LASTEXITCODE -ne 0) {
    throw "Cloud Run job execution failed or exited with an error code ($LASTEXITCODE)."
}

Write-Host "Cloud Run job triggered successfully!" -ForegroundColor Green
Write-Host ""

# 5. Fetch recent logs if requested
if ($ShowLogs) {
    Write-Host "Fetching latest Cloud Run execution logs (last 30 entries)..." -ForegroundColor Yellow
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JobName" --limit=30 --format="value(timestamp,textPayload)" --project=$ProjectId
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Helpful commands to monitor progress:" -ForegroundColor Yellow
Write-Host "  View executions list:" -ForegroundColor White
Write-Host "    gcloud run jobs executions list --job=$JobName --region=$Region --project=$ProjectId" -ForegroundColor Gray
Write-Host "  Download latest sync logs:" -ForegroundColor White
Write-Host "    .\download_logs.ps1" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
