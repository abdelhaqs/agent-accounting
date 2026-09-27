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
  description = "Name of the GCS bucket for raw agent accounting data"
  type        = string
  default     = "agent-accounting-raw-data"
}

variable "sync_image" {
  description = "Container image URL for the Agent Accounting sync Cloud Run Job"
  type        = string
}

variable "uniblock_api_key" {
  description = "Uniblock API key to store in Secret Manager"
  type        = string
  sensitive   = true
}

variable "uniblock_api_key_backup" {
  description = "Optional backup Uniblock API key to store in Secret Manager"
  type        = string
  sensitive   = true
  default     = ""
}

variable "chain_ids" {
  description = "Comma-separated chain ids to sync (default: base)"
  type        = string
  default     = "base"
}
