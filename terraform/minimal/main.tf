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

        volume_mounts {
          name       = "zerion-output"
          mount_path = "/output"
        }

        resources {
          limits = {
            cpu    = "0.5"
            memory = "512Mi"
          }
        }
      }
    }
  }

  depends_on = [
    google_secret_manager_secret_version.zerion_api_key,
    google_project_iam_member.zerion_sync_secret_accessor,
    google_storage_bucket_iam_member.zerion_sync_gcs_admin,
  ]
}
