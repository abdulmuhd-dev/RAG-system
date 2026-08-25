terraform {
  required_version = ">= 1.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket  = "rag-system-tfstate-617711905688"
    key     = "k8s_resources/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

# Read /infrastructure state
data "terraform_remote_state" "infrastructure" {
  backend = "s3"

  config = {
    bucket  = "rag-system-tfstate-617711905688"
    key     = "infrastructure/terraform.tfstate"
    region  = "us-east-1"
  }
}

# Connects Terraform to EKS cluster so it can
# create K8s resources (namespaces, secrets, etc.)
provider "kubernetes" {
  host                   = data.terraform_remote_state.infrastructure.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.infrastructure.outputs.cluster_certificate_authority)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      data.terraform_remote_state.infrastructure.outputs.cluster_name,
      "--region",
      var.aws_region
    ]
  }
}

# Connects Terraform to EKS cluster so it can
# install Helm charts (ArgoCD, ALB Controller, etc.)
provider "helm" {
  kubernetes {
    host                   = data.terraform_remote_state.infrastructure.outputs.cluster_endpoint
    cluster_ca_certificate = base64decode(data.terraform_remote_state.infrastructure.outputs.cluster_certificate_authority)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        data.terraform_remote_state.infrastructure.outputs.cluster_name,
        "--region",
        var.aws_region
      ]
    }
  }
}

data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}
