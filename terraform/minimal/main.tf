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

locals {
  bucket_name = "${var.project_id}-${var.bucket_name}"
}

# -----------------------------------------------------------------------------
# GCS raw-data bucket
# -----------------------------------------------------------------------------
resource "google_storage_bucket" "zerion_raw" {
  name          = local.bucket_name
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true
}

# -----------------------------------------------------------------------------
# Secret Manager
# -----------------------------------------------------------------------------
resource "google_secret_manager_secret" "zerion_api_key" {
  secret_id = "zerion-api-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "zerion_api_key" {
  secret      = google_secret_manager_secret.zerion_api_key.id
  secret_data = var.zerion_api_key
}

# Uniblock API key (DeBank fallback provider)
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
resource "google_service_account" "zerion_sync" {
  account_id   = "zerion-sync"
  display_name = "Zerion sync Cloud Run Job"
}

resource "google_project_iam_member" "zerion_sync_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.zerion_sync.email}"
}

resource "google_storage_bucket_iam_member" "zerion_sync_gcs_admin" {
  bucket = google_storage_bucket.zerion_raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.zerion_sync.email}"
}

# -----------------------------------------------------------------------------
# Cloud Run Job
# -----------------------------------------------------------------------------
resource "google_cloud_run_v2_job" "zerion_sync" {
  name     = "zerion-sync"
  location = var.region

  template {
    template {
      service_account = google_service_account.zerion_sync.email

      volumes {
        name = "zerion-output"
        gcs {
          bucket    = google_storage_bucket.zerion_raw.name
          read_only = false
        }
      }

      containers {
        image = var.sync_image

        env {
          name = "ZERION_API_KEY"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.zerion_api_key.secret_id
              version = "latest"
            }
          }
        }
        env {
          name  = "CHAIN_IDS"
          value = var.chain_ids
        }
        env {
          name  = "AGENTS_CONFIG"
          value = "/app/agents.yaml"
        }
        env {
          name  = "OUTPUT_DIR"
          value = "/output"
        }
        env {
          name  = "BQ_DATASET"
          value = google_bigquery_dataset.agent_accounting.dataset_id
        }
        env {
          name = "UNIBLOCK_API_KEY"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.uniblock_api_key.secret_id
              version = "latest"
            }
          }
        }

        volume_mounts {
          name       = "zerion-output"
          mount_path = "/output"
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
    google_secret_manager_secret_version.zerion_api_key,
    google_secret_manager_secret_version.uniblock_api_key,
    google_project_iam_member.zerion_sync_secret_accessor,
    google_storage_bucket_iam_member.zerion_sync_gcs_admin,
    google_bigquery_dataset_iam_member.zerion_sync_bq_editor,
    google_project_iam_member.zerion_sync_bq_job_user,
  ]
}

# -----------------------------------------------------------------------------
# BigQuery warehouse: balances + transfers
# -----------------------------------------------------------------------------
resource "google_bigquery_dataset" "agent_accounting" {
  dataset_id  = "agent_accounting"
  description = "Agent accounting data synced from Zerion"
  location    = var.region
}

resource "google_bigquery_table" "transfers" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  table_id   = "transfers"

  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "mined_at"
  }

  clustering = ["wallet", "token_symbol"]

  schema = jsonencode([
    { name = "wallet", type = "STRING", mode = "REQUIRED" },
    { name = "agent_name", type = "STRING", mode = "NULLABLE" },
    { name = "tx_id", type = "STRING", mode = "NULLABLE" },
    { name = "tx_hash", type = "STRING", mode = "NULLABLE" },
    { name = "chain", type = "STRING", mode = "NULLABLE" },
    { name = "mined_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "direction", type = "STRING", mode = "NULLABLE" },
    { name = "sender", type = "STRING", mode = "NULLABLE" },
    { name = "recipient", type = "STRING", mode = "NULLABLE" },
    { name = "token_id", type = "STRING", mode = "NULLABLE" },
    { name = "token_name", type = "STRING", mode = "NULLABLE" },
    { name = "token_symbol", type = "STRING", mode = "NULLABLE" },
    { name = "token_address", type = "STRING", mode = "NULLABLE" },
    { name = "chain_id", type = "STRING", mode = "NULLABLE" },
    { name = "decimals", type = "INTEGER", mode = "NULLABLE" },
    { name = "amount_raw", type = "STRING", mode = "NULLABLE" },
    { name = "amount_float", type = "FLOAT", mode = "NULLABLE" },
    { name = "price", type = "FLOAT", mode = "NULLABLE" },
    { name = "usd_value", type = "FLOAT", mode = "NULLABLE" },
    { name = "provider", type = "STRING", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "balances" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  table_id   = "balances"

  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "updated_at"
  }

  clustering = ["wallet", "token_symbol"]

  schema = jsonencode([
    { name = "wallet", type = "STRING", mode = "REQUIRED" },
    { name = "agent_name", type = "STRING", mode = "NULLABLE" },
    { name = "chain", type = "STRING", mode = "NULLABLE" },
    { name = "position_type", type = "STRING", mode = "NULLABLE" },
    { name = "token_id", type = "STRING", mode = "NULLABLE" },
    { name = "token_name", type = "STRING", mode = "NULLABLE" },
    { name = "token_symbol", type = "STRING", mode = "NULLABLE" },
    { name = "token_address", type = "STRING", mode = "NULLABLE" },
    { name = "chain_id", type = "STRING", mode = "NULLABLE" },
    { name = "decimals", type = "INTEGER", mode = "NULLABLE" },
    { name = "balance_raw", type = "STRING", mode = "NULLABLE" },
    { name = "balance_float", type = "FLOAT", mode = "NULLABLE" },
    { name = "price", type = "FLOAT", mode = "NULLABLE" },
    { name = "usd_value", type = "FLOAT", mode = "NULLABLE" },
    { name = "is_receipt_token", type = "BOOLEAN", mode = "NULLABLE" },
    { name = "updated_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "provider", type = "STRING", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "balance_reconciliation" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  table_id   = "balance_reconciliation"

  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "loaded_at"
  }

  clustering = ["wallet", "status"]

  schema = jsonencode([
    { name = "run_timestamp", type = "STRING", mode = "REQUIRED" },
    { name = "agent_name", type = "STRING", mode = "NULLABLE" },
    { name = "wallet", type = "STRING", mode = "REQUIRED" },
    { name = "provider", type = "STRING", mode = "NULLABLE" },
    { name = "computed_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "same_provider_total_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "cross_provider_total_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "same_provider_delta_pct", type = "FLOAT", mode = "NULLABLE" },
    { name = "cross_provider_delta_pct", type = "FLOAT", mode = "NULLABLE" },
    { name = "onchain_total_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "onchain_unverified_usd", type = "FLOAT", mode = "NULLABLE" },
    { name = "onchain_delta_pct", type = "FLOAT", mode = "NULLABLE" },
    { name = "status", type = "STRING", mode = "NULLABLE" },
    { name = "loaded_at", type = "TIMESTAMP", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_dataset_iam_member" "zerion_sync_bq_editor" {
  dataset_id = google_bigquery_dataset.agent_accounting.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.zerion_sync.email}"
}

resource "google_project_iam_member" "zerion_sync_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.zerion_sync.email}"
}
