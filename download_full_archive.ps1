# Download the ENTIRE Archive folder from GCS (all agents, all file types)
# Note: This delegates to download_archive.ps1 which now syncs all agents by default to .\archive_downloads.
#
# Usage:
#   .\download_full_archive.ps1
#   .\download_full_archive.ps1 -OutputDir D:\backups\zerion_archive

param(
    [string]$Bucket    = "gs://agent-accounting-506719-zerion-raw-data",
    [string]$Prefix    = "Archive",
    [string]$OutputDir = ".\archive_downloads"
)

& "$PSScriptRoot\download_archive.ps1" -Agent "all" -Bucket $Bucket -Prefix $Prefix -OutputDir $OutputDir
