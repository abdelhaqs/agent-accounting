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

variable "sync_image" {
  description = "Container image URL for the Zerion sync Cloud Run Job"
  type        = string
}

variable "zerion_api_key" {
  description = "Zerion API key to store in Secret Manager"
  type        = string
  sensitive   = true
}

variable "chain_ids" {
  description = "Comma-separated chain ids to sync (default: base)"
  type        = string
  default     = "base"
}
