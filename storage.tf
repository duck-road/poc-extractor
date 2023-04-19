resource "google_storage_bucket" "function_bucket" {
  name     = "poc-extractor-function-${var.project_id}"
  location = var.region
}

resource "google_storage_bucket" "input_bucket" {
  name     = "poc-extractor-input-${var.project_id}"
  location = var.region
}