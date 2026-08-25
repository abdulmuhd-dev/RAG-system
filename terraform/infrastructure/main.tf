terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket  = "rag-system-tfstate-617711905688"
    key     = "infrastructure/terraform.tfstate"
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


data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}
