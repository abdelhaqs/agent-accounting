# Download sync run logs from GCS to local logs_downloads
# Uses 'gcloud storage rsync' to pull ONLY new run logs (incremental & fast).
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
Write-Host "  GCS Logs Download (Incremental Sync)" -ForegroundColor Cyan
Write-Host "  Source: $source" -ForegroundColor Cyan
Write-Host "  Target: $OutputDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Prepare output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}
$resolvedDir = Resolve-Path $OutputDir
$beforeFiles = Get-ChildItem -Path $OutputDir -Recurse -File -ErrorAction SilentlyContinue
$beforeCount = ($beforeFiles | Measure-Object).Count

# 2. Download (rsync skips existing files, only transfers new ones)
Write-Host "[1/2] Syncing new run logs from GCS..." -ForegroundColor Yellow
gcloud storage rsync -r $source $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "Logs download failed (gcloud exit code $LASTEXITCODE). Check authentication (gcloud auth list)."
}

# 3. Verify + summarize
Write-Host "[2/2] Calculating summary..." -ForegroundColor Yellow
$localFiles = Get-ChildItem -Path $OutputDir -Recurse -File
$afterCount = ($localFiles | Measure-Object).Count
$newCount   = [math]::Max(0, $afterCount - $beforeCount)
$totalKB    = [math]::Round(($localFiles | Measure-Object Length -Sum).Sum / 1KB, 1)

Write-Host ""
if ($newCount -gt 0) {
    Write-Host "SUCCESS: Pulled $newCount new log file(s)!" -ForegroundColor Green
} else {
    Write-Host "Already up to date: 0 new log files downloaded." -ForegroundColor Green
}
Write-Host "Total log files: $afterCount ($totalKB KB)" -ForegroundColor Cyan
Write-Host "Logs directory:  $resolvedDir" -ForegroundColor Cyan

# Show the 5 most recent run logs
Write-Host ""
Write-Host "Most recent run logs:" -ForegroundColor Cyan
$localFiles | Sort-Object Name -Descending | Select-Object -First 5 |
    ForEach-Object { Write-Host ("  {0}  ({1:yyyy-MM-dd HH:mm})" -f $_.Name, $_.LastWriteTime) }
