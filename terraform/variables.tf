variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "Name of the GCS bucket for raw Zerion data"
  type        = string
  default     = "zerion-raw-data"
}

variable "dataset_id" {
  description = "BigQuery dataset ID for raw tables"
  type        = string
  default     = "zerion_raw"
}

variable "sync_image" {
  description = "Container image URL for the Zerion sync Cloud Run Job"
  type        = string
}

variable "schedule" {
  description = "Cloud Scheduler cron expression"
  type        = string
  default     = "*/30 * * * *"
}

variable "zerion_api_key" {
  description = "Zerion API key to store in Secret Manager"
  type        = string
  sensitive   = true
}

variable "sync_env" {
  description = "Additional environment variables for the Cloud Run Job"
  type        = map(string)
  default = {
    CHAIN_IDS = "base"
  }
}

variable "cloud_run_volumes" {
  description = "Optional GCS volumes to mount into the Cloud Run Job"
  type = list(object({
    name = string
    gcs = optional(object({
      bucket    = string
      read_only = optional(bool, true)
    }))
  }))
  default = []
}

variable "cloud_run_volume_mounts" {
  description = "Volume mounts for the Cloud Run Job container"
  type = list(object({
    name       = string
    mount_path = string
  }))
  default = []
}
