variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "acm_certificate_arn" {
  description = "ACM wildcard certificate ARN from dns_acm layer"
  type        = string
  default     = "arn:aws:acm:us-east-1:617711905688:certificate/4fe77d0e-0567-4558-a1c0-5c1f215e3d27"
}
