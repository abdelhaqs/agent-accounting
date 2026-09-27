<#
.SYNOPSIS
    Developer CLI & Task Runner for Agent Accounting (Windows Native).
.DESCRIPTION
    Runs tests, linting, formatting, data quality contracts, and dashboard generation.
.EXAMPLE
    .\task.ps1 test
    .\task.ps1 lint
    .\task.ps1 data-check
    .\task.ps1 report
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet("test", "lint", "format", "data-check", "report", "pull-reports", "clean", "help")]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"

switch ($Command) {
    "test" {
        Write-Host "--> Running full unit test suite..." -ForegroundColor Cyan
        pytest tests/ -v
    }
    "lint" {
        Write-Host "--> Linting Python files with flake8..." -ForegroundColor Cyan
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=local_tests,venv,.venv,archive_downloads,Archive
        flake8 . --count --exit-zero --max-complexity=15 --max-line-length=130 --statistics --exclude=local_tests,venv,.venv,archive_downloads,Archive
    }
    "format" {
        Write-Host "--> Formatting Python files with black..." -ForegroundColor Cyan
        black --line-length 130 .
    }
    "data-check" {
        Write-Host "--> Running Data Quality Contracts..." -ForegroundColor Cyan
        pytest tests/test_data_quality.py -v
    }
    "report" {
        Write-Host "--> Compiling Audit Report Dashboard to HTML..." -ForegroundColor Cyan
        python dag/generate_html_report.py
    }
    "pull-reports" {
        Write-Host "--> Pulling latest audit reports from Google Cloud Storage..." -ForegroundColor Cyan
        & .\dag\download_reports.ps1
    }
    "clean" {
        Write-Host "--> Cleaning cache files..." -ForegroundColor Cyan
        Get-ChildItem -Path . -Include __pycache__, .pytest_cache -Recurse -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
        Write-Host "Done." -ForegroundColor Green
    }
    default {
        Write-Host "Agent Accounting Task Runner" -ForegroundColor Yellow
        Write-Host "Usage: .\task.ps1 [command]"
        Write-Host "Commands:"
        Write-Host "  test         : Run full unit test suite (pytest)"
        Write-Host "  lint         : Check code with flake8"
        Write-Host "  format       : Format code with black"
        Write-Host "  data-check   : Run data quality validation"
        Write-Host "  report       : Generate HTML dashboard from latest audit report"
        Write-Host "  pull-reports : Download latest value check reports from GCS into docs/report/"
        Write-Host "  clean        : Remove temporary caches"
    }
}
