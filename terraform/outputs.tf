output "gcs_bucket" {
  description = "GCS bucket for raw agent accounting data"
  value       = google_storage_bucket.raw_data.name
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.agent_accounting.dataset_id
}

output "cloud_run_job_name" {
  description = "Name of the Cloud Run Job"
  value       = google_cloud_run_v2_job.accounting_sync.name
}

output "workflow_name" {
  description = "Name of the Cloud Workflows pipeline"
  value       = google_workflows_workflow.accounting_pipeline.name
}

output "scheduler_job_name" {
  description = "Name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.accounting_pipeline.name
}

output "sync_service_account" {
  description = "Email of the service account used by the sync job"
  value       = google_service_account.accounting_sync.email
}
