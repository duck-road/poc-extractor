terraform {
  backend "gcs" {
    bucket      = "poc-extractor"
    prefix      = "terraform/state1"
    credentials = "service-account.json"
  }
}