# Download archived agent data from GCS to local archive_downloads
# Uses 'gcloud storage rsync' to pull ONLY new / modified snapshots (incremental & fast).
#
# Usage:
#   .\download_archive.ps1                              # syncs all agents (default)
#   .\download_archive.ps1 -Agent mamo_base_agent_1     # syncs only a specific agent
#   .\download_archive.ps1 -OutputDir .\custom_folder   # custom output directory

param(
    [string]$Agent     = "all",
    [string]$Bucket    = "gs://agent-accounting-506719-zerion-raw-data",
    [string]$Prefix    = "Archive",
    [string]$OutputDir = ".\archive_downloads"
)

$ErrorActionPreference = "Stop"

$source = "$Bucket/$Prefix"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GCS Archive Download (Incremental Sync)" -ForegroundColor Cyan
Write-Host "  Source: $source" -ForegroundColor Cyan
Write-Host "  Target: $OutputDir" -ForegroundColor Cyan
if ($Agent -and $Agent -ne "all") {
    Write-Host "  Filter: Agent = $Agent" -ForegroundColor Cyan
} else {
    Write-Host "  Filter: All Agents" -ForegroundColor Cyan
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Prepare local output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}
$resolvedDir = Resolve-Path $OutputDir
$beforeFiles = Get-ChildItem -Path $OutputDir -File -ErrorAction SilentlyContinue
$beforeCount = ($beforeFiles | Measure-Object).Count

# 2. Run incremental rsync
Write-Host "[1/2] Syncing new snapshots from GCS..." -ForegroundColor Yellow
if ($Agent -and $Agent -ne "all") {
    # Exclude objects that don't match the requested agent prefix
    $excludeRegex = "^(?!${Agent}_).*"
    gcloud storage rsync -r --exclude="$excludeRegex" $source $OutputDir
} else {
    gcloud storage rsync -r $source $OutputDir
}

if ($LASTEXITCODE -ne 0) {
    throw "Archive download failed (gcloud exit code $LASTEXITCODE). Check authentication (gcloud auth list)."
}

# 3. Summary & Verification
Write-Host "[2/2] Calculating summary..." -ForegroundColor Yellow
$localFiles = Get-ChildItem -Path $OutputDir -File
$afterCount = ($localFiles | Measure-Object).Count
$newCount   = [math]::Max(0, $afterCount - $beforeCount)
$totalMB    = [math]::Round(($localFiles | Measure-Object Length -Sum).Sum / 1MB, 2)

Write-Host ""
if ($newCount -gt 0) {
    Write-Host "SUCCESS: Pulled $newCount new snapshot file(s)!" -ForegroundColor Green
} else {
    Write-Host "Already up to date: 0 new files downloaded." -ForegroundColor Green
}
Write-Host "Total archive files: $afterCount ($totalMB MB)" -ForegroundColor Cyan
Write-Host "Archive directory:   $resolvedDir" -ForegroundColor Cyan

# Breakdown by agent
Write-Host ""
Write-Host "Breakdown by agent:" -ForegroundColor Cyan
$localFiles | ForEach-Object {
    if ($_.Name -match '^(?<agent>.+?)_(?<type>balances|transfers|raw_\w+)_\d{8}_\d{6}\.json$') {
        [PSCustomObject]@{ Agent = $Matches.agent; Type = $Matches.type }
    } else {
        [PSCustomObject]@{ Agent = '(other)'; Type = $_.Name }
    }
} | Group-Object Agent | Sort-Object Name | ForEach-Object {
    $agentName = $_.Name
    $count = $_.Count
    Write-Host ("  {0,-32} {1,5} files" -f $agentName, $count)
}
