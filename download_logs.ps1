# Download sync run logs from GCS to a local folder (mirrors download_full_archive.ps1)
# Uses 'gcloud storage rsync' so re-runs skip files you already have (resumable).
#
# Usage:
#   .\download_logs.ps1
#   .\download_logs.ps1 -OutputDir D:\backups\zerion_logs

param(
    [string]$Bucket    = "gs://agent-accounting-506719-zerion-raw-data",
    [string]$Prefix    = "logs",
    [string]$OutputDir = ".\logs_downloads"
)

$ErrorActionPreference = "Stop"

$source = "$Bucket/$Prefix"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GCS Logs Download" -ForegroundColor Cyan
Write-Host "  Source: $source" -ForegroundColor Cyan
Write-Host "  Target: $OutputDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. List remote files (verifies auth + path before downloading)
Write-Host "[1/3] Listing remote log files..." -ForegroundColor Yellow
$remoteFiles = gcloud storage ls -r "$source/**" 2>$null
$remoteCount = ($remoteFiles | Measure-Object).Count

if ($remoteCount -eq 0) {
    throw "No files found under $source. Check the path and auth (gcloud auth list)."
}
Write-Host "  Found $remoteCount objects" -ForegroundColor Green
Write-Host ""

# 2. Prepare output directory
Write-Host "[2/3] Preparing output directory..." -ForegroundColor Yellow
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}
Write-Host "  -> $(Resolve-Path $OutputDir)" -ForegroundColor Green
Write-Host ""

# 3. Download (rsync = resumable, skips existing files on re-run)
Write-Host "[3/3] Downloading..." -ForegroundColor Yellow
Write-Host "  Re-run this script anytime to pick up new run logs." -ForegroundColor DarkGray
gcloud storage rsync -r $source $OutputDir
if ($LASTEXITCODE -ne 0) { throw "Download failed (gcloud exit code $LASTEXITCODE). Re-run to resume." }

# 4. Verify + summarize
$localFiles = Get-ChildItem $OutputDir -Recurse -File
$totalKB    = [math]::Round(($localFiles | Measure-Object Length -Sum).Sum / 1KB, 1)

Write-Host ""
Write-Host "Downloaded $($localFiles.Count)/$remoteCount log files ($totalKB KB)" -ForegroundColor Green

if ($localFiles.Count -ne $remoteCount) {
    Write-Host "WARNING: count mismatch - expected $remoteCount, got $($localFiles.Count). Re-run to resume." -ForegroundColor Red
}

# Show the 5 most recent run logs
Write-Host ""
Write-Host "Most recent run logs:" -ForegroundColor Cyan
$localFiles | Sort-Object Name -Descending | Select-Object -First 5 |
    ForEach-Object { Write-Host ("  {0}  ({1:yyyy-MM-dd HH:mm})" -f $_.Name, $_.LastWriteTime) }

Write-Host ""
Write-Host "Logs are in: $(Resolve-Path $OutputDir)" -ForegroundColor Green
