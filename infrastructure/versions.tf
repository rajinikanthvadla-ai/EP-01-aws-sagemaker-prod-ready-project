terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    # This will be configured via backend config file or environment variables
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.4.0"
    }
  }
} 