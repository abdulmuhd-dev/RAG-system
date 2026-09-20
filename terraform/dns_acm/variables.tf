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
