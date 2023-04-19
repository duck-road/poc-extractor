terraform {
  backend "gcs" {
    bucket      = "aloconcursos-dev-terraform"
    prefix      = "terraform/poc-extractor"
    credentials = "service-account.json"
  }
}