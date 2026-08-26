output "gcs_bucket" {
  description = "GCS bucket for raw Zerion data"
  value       = google_storage_bucket.zerion_raw.name
}

output "cloud_run_job_name" {
  description = "Name of the Cloud Run Job"
  value       = google_cloud_run_v2_job.zerion_sync.name
}

output "sync_service_account" {
  description = "Email of the service account used by the sync job"
  value       = google_service_account.zerion_sync.email
}
