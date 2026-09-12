# Export BigQuery tables to CSV
# Dataset: agent-accounting-506719.agent_accounting
# Run from: C:\Users\chris\Projects\agent-accounting

$PROJECT_ID = "agent-accounting-506719"
$DATASET    = "agent_accounting"
$OUTPUT_DIR = ".\bq_exports"

$tables = @("balance_reconciliation", "balances", "transfers")

# Create output directory
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BigQuery Table Export" -ForegroundColor Cyan
Write-Host "  Project: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "  Dataset: $DATASET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($t in $tables) {
    $csvPath = Join-Path $OUTPUT_DIR "$t.csv"
    $tableRef = "``$PROJECT_ID.$DATASET.$t``"

    Write-Host "[Export] $t ..." -ForegroundColor Yellow

    # Export full table to CSV (max_rows=1000000 avoids the 100-row default limit)
    bq query --use_legacy_sql=false --format=csv --max_rows=1000000 "SELECT * FROM $tableRef" > $csvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  FAILED to export $t" -ForegroundColor Red
        continue
    }

    # Row count from BigQuery (source of truth)
    $countOut = bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) as total FROM $tableRef" 2>$null
    # CSV output has a header line + data line; extract the numeric count
    $bqCount = ($countOut | Select-Object -Skip 1).Trim()

    # Row count from exported CSV
    $csvCount = (Import-Csv $csvPath).Count

    $sizeMB = [math]::Round((Get-Item $csvPath).Length / 1MB, 2)

    if ($csvCount -eq [int]$bqCount) {
        Write-Host "  OK  rows=$csvCount  size=${sizeMB}MB  -> $csvPath" -ForegroundColor Green
    } else {
        Write-Host "  MISMATCH  bq=$bqCount  csv=$csvCount  (may be truncated)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done. Files in: $(Resolve-Path $OUTPUT_DIR)" -ForegroundColor Cyan
