# Download latest Value Check Reports from Google Cloud Storage into docs/report/
# Run from project root: C:\Users\chris\Projects\agent-accounting

param(
    [string]$ProjectId = "agent-accounting-506719",
    [string]$TargetDir = "docs/report"
)

$buckets = @(
    "$ProjectId-zerion-raw-data",
    "$ProjectId-agent-accounting-raw-data"
)

Write-Host "Checking for reports in Google Cloud Storage..." -ForegroundColor Cyan

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

$found = $false
foreach ($bucket in $buckets) {
    Write-Host "Scanning gs://$bucket/reports/..." -ForegroundColor Yellow
    try {
        $list = cmd /c "gcloud storage ls gs://$bucket/reports/ 2>nul"
        if ($LASTEXITCODE -eq 0 -and $list) {
            Write-Host "Found reports in gs://$bucket/reports/! Downloading..." -ForegroundColor Green
            cmd /c "gcloud storage cp -r gs://$bucket/reports/* $TargetDir/"
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Reports downloaded to $TargetDir." -ForegroundColor Green
                $found = $true
                break
            }
        }
    } catch {
        # continue to next bucket
    }
}

if (-not $found) {
    Write-Host "No reports found yet in GCS buckets. Reports will appear after the next Cloud Run execution." -ForegroundColor Yellow
} else {
    Write-Host "You can now commit the new reports to GitHub with: git add docs/report/ && git commit -m 'docs: update latest value check report' && git push" -ForegroundColor Cyan
}
