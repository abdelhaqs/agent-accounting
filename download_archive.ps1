# Download archived agent data from GCS
# Usage:
#   .\download_archive.ps1                          # defaults: mamo_base_agent_1
#   .\download_archive.ps1 -Agent zyfai_base_agent_2
#   .\download_archive.ps1 -Agent mamo_base_agent_1 -Prefix Archive

param(
    [string]$Agent  = "mamo_base_agent_1",
    [string]$Bucket = "gs://agent-accounting-506719-zerion-raw-data",
    [string]$Prefix = "Archive"
)

$ErrorActionPreference = "Stop"

$pattern    = "$Bucket/$Prefix/${Agent}_*"
$outputDir  = ".\archive_downloads\$Agent"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GCS Archive Download" -ForegroundColor Cyan
Write-Host "  Pattern: $pattern" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. List what will be downloaded (also verifies auth + path)
Write-Host "[1/3] Listing remote files..." -ForegroundColor Yellow
$remoteFiles = gcloud storage ls $pattern 2>$null
$remoteCount = ($remoteFiles | Measure-Object).Count

if ($remoteCount -eq 0) {
    throw "No files found at $pattern. Check the agent name, prefix, and that you're authenticated (gcloud auth list)."
}
Write-Host "  Found $remoteCount files" -ForegroundColor Green
Write-Host ""

# 2. Prepare local directory
Write-Host "[2/3] Preparing output directory..." -ForegroundColor Yellow
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}
Write-Host "  -> $(Resolve-Path $outputDir)" -ForegroundColor Green
Write-Host ""

# 3. Download
Write-Host "[3/3] Downloading..." -ForegroundColor Yellow
gcloud storage cp $pattern $outputDir
if ($LASTEXITCODE -ne 0) { throw "Download failed (gcloud exit code $LASTEXITCODE)" }

# 4. Verify
$localFiles = Get-ChildItem $outputDir -File
$totalMB    = [math]::Round(($localFiles | Measure-Object Length -Sum).Sum / 1MB, 2)

Write-Host ""
Write-Host "Downloaded $($localFiles.Count)/$remoteCount files ($totalMB MB)" -ForegroundColor Green

if ($localFiles.Count -ne $remoteCount) {
    Write-Host "WARNING: count mismatch - expected $remoteCount, got $($localFiles.Count)" -ForegroundColor Red
}

# Group summary by file type
Write-Host ""
Write-Host "Breakdown by type:" -ForegroundColor Cyan
$localFiles | Group-Object { ($_.Name -replace '_\d{8}_\d{6}\.json$', '') -replace "^${Agent}_", '' } |
    Sort-Object Name |
    ForEach-Object { Write-Host ("  {0,-25} {1,4} files" -f $_.Name, $_.Count) }
