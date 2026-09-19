# Hosted zone
resource "aws_route53_zone" "main" {
  name = var.domain_name

  tags = {
    Name = var.domain_name
  }
}

# DNS Records
# Only created when ALB hostnames are provided
# Leave empty on first apply (just to get nameservers)
resource "aws_route53_record" "rag_api" {
  count   = var.rag_alb_hostname != "" ? 1 : 0
  zone_id = aws_route53_zone.main.zone_id
  name    = "rag.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [var.rag_alb_hostname]
}

resource "aws_route53_record" "argocd" {
  count   = var.argocd_alb_hostname != "" ? 1 : 0
  zone_id = aws_route53_zone.main.zone_id
  name    = "argocd.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [var.argocd_alb_hostname]
}
