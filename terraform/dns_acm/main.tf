terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

backend "s3" {
    bucket  = "rag-system-tfstate-617711905688"
    key     = "dns-acm/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "rag-system"
      Environment = "production"
      ManagedBy   = "terraform"
      Owner       = "abdulmuhd-dev"
    }
  }
}

data "terraform_remote_state" "infrastructure" {
  backend = "s3"
  config = {
    bucket = "rag-system-tfstate-617711905688"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}
