output "route53_nameservers" {
  description = "Add these 4 nameservers to DigitalPlat DNS settings"
  value       = aws_route53_zone.main.name_servers
}

output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.main.zone_id
}

output "acm_certificate_arn" {
  description = "Wildcard ACM certificate ARN — add to ingress annotation"
  value       = aws_acm_certificate.main.arn
}

output "subdomains" {
  description = "Your application URLs once DNS propagates"
  value = {
    rag_api = "https://rag.${var.domain_name}"
    argocd  = "https://argocd.${var.domain_name}"
 #   grafana = "https://grafana.${var.domain_name}"
  }
}
