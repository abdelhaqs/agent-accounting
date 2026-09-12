# Download the ENTIRE Archive folder from GCS (all agents, all file types)
# Uses 'gcloud storage rsync' so re-runs skip files you already have (resumable).
#
# Usage:
#   .\download_full_archive.ps1
#   .\download_full_archive.ps1 -OutputDir D:\backups\zerion_archive

param(
    [string]$Bucket    = "gs://agent-accounting-506719-zerion-raw-data",
    [string]$Prefix    = "Archive",
    [string]$OutputDir = ".\archive_downloads\full_archive"
)

$ErrorActionPreference = "Stop"

$source = "$Bucket/$Prefix"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Full GCS Archive Download" -ForegroundColor Cyan
Write-Host "  Source: $source" -ForegroundColor Cyan
Write-Host "  Target: $OutputDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. List remote files (verifies auth + path before downloading)
Write-Host "[1/3] Listing remote files..." -ForegroundColor Yellow
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
Write-Host "[3/3] Downloading (this may take a while)..." -ForegroundColor Yellow
Write-Host "  Re-run this script anytime to resume / pick up new snapshots." -ForegroundColor DarkGray
gcloud storage rsync -r $source $OutputDir
if ($LASTEXITCODE -ne 0) { throw "Download failed (gcloud exit code $LASTEXITCODE). Re-run to resume." }

# 4. Verify + summarize
$localFiles = Get-ChildItem $OutputDir -Recurse -File
$totalMB    = [math]::Round(($localFiles | Measure-Object Length -Sum).Sum / 1MB, 2)

Write-Host ""
Write-Host "Downloaded $($localFiles.Count)/$remoteCount files ($totalMB MB)" -ForegroundColor Green

if ($localFiles.Count -ne $remoteCount) {
    Write-Host "WARNING: count mismatch - expected $remoteCount, got $($localFiles.Count). Re-run to resume." -ForegroundColor Red
}

# Breakdown per agent and data type (filenames look like: <agent>_<type>_<timestamp>.json)
Write-Host ""
Write-Host "Breakdown by agent / type:" -ForegroundColor Cyan
$localFiles | ForEach-Object {
    if ($_.Name -match '^(?<agent>.+?)_(?<type>balances|raw_debank_history|raw_debank_protocols|raw_debank_tokens)_\d{8}_\d{6}\.json$') {
        [PSCustomObject]@{ Agent = $Matches.agent; Type = $Matches.type }
    } else {
        [PSCustomObject]@{ Agent = '(unparsed)'; Type = $_.Name }
    }
} | Group-Object Agent | Sort-Object Name | ForEach-Object {
    $agent = $_.Name
    $types = $_.Group | Group-Object Type | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Count)" }
    Write-Host ("  {0,-30} {1}" -f $agent, ($types -join '  |  '))
}

Write-Host ""
Write-Host "Files are in: $(Resolve-Path $OutputDir)" -ForegroundColor Green
