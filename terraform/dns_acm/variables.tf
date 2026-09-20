variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Root domain name"
  type        = string
  default     = "abdulmuhd.dpdns.org"
}

variable "alb_hostname" {
  description = "Shared ALB hostname from kubectl get ingress"
  type        = string
  default     = ""
}

variable "alb_hosted_zone_id" {
  description = "ALB hosted zone ID — fixed per AWS region"
  type        = string
  default     = "Z35SXDOTRQ7X7K"
  #  Z35SXDOTRQ7X7K is the fixed zone ID
  # for ALL ALBs in us-east-1
  # This is an AWS constant, not your zone ID
}

variable "rag_alb_hostname" {
  description = "RAG API ALB hostname from kubectl get ingress"
  type        = string
  default     = ""
}

variable "argocd_alb_hostname" {
  description = "ArgoCD ALB hostname from kubectl get svc"
  type        = string
  default     = ""
}
