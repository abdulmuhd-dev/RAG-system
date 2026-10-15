variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "acm_certificate_arn" {
  description = "ACM wildcard certificate ARN from dns_acm layer"
  type        = string
  default     = "arn:aws:acm:us-east-1:617711905688:certificate/50d73293-aad0-4946-b76c-e5933031be4d"
}
