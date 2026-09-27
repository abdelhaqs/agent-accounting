terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------------------------------------------------------------
# GCS raw-data bucket
# -----------------------------------------------------------------------------
resource "google_storage_bucket" "raw_data" {
  name          = "${var.project_id}-${var.bucket_name}"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# -----------------------------------------------------------------------------
# BigQuery warehouse dataset and tables
# -----------------------------------------------------------------------------
resource "google_bigquery_dataset" "agent_accounting" {
  dataset_id  = var.dataset_id
  description = "Agent Accounting data warehouse"
  location    = var.region
}

resource "google_bigquery_table" "raw_transactions" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  table_id   = "raw_transactions"

  time_partitioning {
    type  = "DAY"
    field = "run_timestamp"
  }

  clustering = ["wallet_address"]

  schema = jsonencode([
    { name = "wallet_address", type = "STRING", mode = "REQUIRED" },
    { name = "agent_name", type = "STRING", mode = "NULLABLE" },
    { name = "run_timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "page_index", type = "INTEGER", mode = "REQUIRED" },
    { name = "payload", type = "JSON", mode = "REQUIRED" },
    { name = "loaded_at", type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

resource "google_bigquery_table" "raw_positions" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  table_id   = "raw_positions"

  time_partitioning {
    type  = "DAY"
    field = "run_timestamp"
  }

  clustering = ["wallet_address"]

  schema = jsonencode([
    { name = "wallet_address", type = "STRING", mode = "REQUIRED" },
    { name = "agent_name", type = "STRING", mode = "NULLABLE" },
    { name = "run_timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "page_index", type = "INTEGER", mode = "REQUIRED" },
    { name = "payload", type = "JSON", mode = "REQUIRED" },
    { name = "loaded_at", type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

# -----------------------------------------------------------------------------
# Secret Manager
# -----------------------------------------------------------------------------
resource "google_secret_manager_secret" "uniblock_api_key" {
  secret_id = "uniblock-api-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "uniblock_api_key" {
  secret      = google_secret_manager_secret.uniblock_api_key.id
  secret_data = var.uniblock_api_key
}

# -----------------------------------------------------------------------------
# Service account for the Cloud Run Job
# -----------------------------------------------------------------------------
resource "google_service_account" "accounting_sync" {
  account_id   = "accounting-sync"
  display_name = "Agent Accounting Cloud Run Job"
}

resource "google_project_iam_member" "accounting_sync_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.accounting_sync.email}"
}

resource "google_storage_bucket_iam_member" "accounting_sync_gcs_admin" {
  bucket = google_storage_bucket.raw_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.accounting_sync.email}"
}

resource "google_bigquery_dataset_iam_member" "accounting_sync_bq_editor" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.accounting_sync.email}"
}

resource "google_project_iam_member" "accounting_sync_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.accounting_sync.email}"
}

# -----------------------------------------------------------------------------
# Cloud Run Job
# -----------------------------------------------------------------------------
resource "google_cloud_run_v2_job" "accounting_sync" {
  name     = "agent-accounting-sync"
  location = var.region

  template {
    template {
      service_account = google_service_account.accounting_sync.email

      dynamic "volumes" {
        for_each = var.cloud_run_volumes
        content {
          name = volumes.value.name
          gcs {
            bucket    = volumes.value.gcs.bucket
            read_only = volumes.value.gcs.read_only
          }
        }
      }

      containers {
        image = var.sync_image

        env {
          name  = "UNIBLOCK_API_KEY_SECRET"
          value = google_secret_manager_secret.uniblock_api_key.secret_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.raw_data.name
        }
        env {
          name  = "BQ_DATASET"
          value = google_bigquery_dataset.agent_accounting.dataset_id
        }

        dynamic "env" {
          for_each = var.sync_env
          content {
            name  = env.key
            value = env.value
          }
        }

        dynamic "volume_mounts" {
          for_each = var.cloud_run_volume_mounts
          content {
            name       = volume_mounts.value.name
            mount_path = volume_mounts.value.mount_path
          }
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
    }
  }

  depends_on = [
    google_secret_manager_secret_version.uniblock_api_key,
    google_project_iam_member.accounting_sync_secret_accessor,
    google_storage_bucket_iam_member.accounting_sync_gcs_admin,
    google_bigquery_dataset_iam_member.accounting_sync_bq_editor,
    google_project_iam_member.accounting_sync_bq_job_user,
  ]
}

# -----------------------------------------------------------------------------
# Cloud Workflows
# -----------------------------------------------------------------------------
resource "google_workflows_workflow" "accounting_pipeline" {
  name            = "agent-accounting-pipeline"
  region          = var.region
  service_account = google_service_account.accounting_sync.email
  source_contents = templatefile("${path.module}/workflow.yaml", {
    project_id = var.project_id
    location   = var.region
    job_name   = google_cloud_run_v2_job.accounting_sync.name
  })
}

# -----------------------------------------------------------------------------
# Cloud Scheduler
# -----------------------------------------------------------------------------
resource "google_cloud_scheduler_job" "accounting_pipeline" {
  name             = "agent-accounting-30min"
  description      = "Trigger Agent Accounting pipeline workflow every 30 minutes"
  schedule         = var.schedule
  time_zone        = "UTC"
  region           = var.region
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.accounting_pipeline.id}/executions"

    oauth_token {
      service_account_email = google_service_account.accounting_sync.email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}

# -----------------------------------------------------------------------------
# Service account permission for Cloud Workflows invocation
# -----------------------------------------------------------------------------
resource "google_project_iam_member" "accounting_sync_workflows_invoker" {
  project = var.project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.accounting_sync.email}"
}
