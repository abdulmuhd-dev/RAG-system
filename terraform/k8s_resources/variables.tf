variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "acm_certificate_arn" {
  description = "ACM wildcard certificate ARN from dns_acm layer"
  type        = string
  default     = "arn:aws:acm:us-east-1:617711905688:certificate/4b01fc23-8e8d-41e2-ac13-9fcef7df3837"
}
