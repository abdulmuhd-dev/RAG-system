resource "aws_route53_zone" "main" {
  name = var.domain_name

  tags = {
    Name = var.domain_name
  }
}

# single record — one ALB serves everythin
# ALIAS record at apex — Route53 specific feature
# Works like CNAME but allowed at zone apex
resource "aws_route53_record" "main" {
  count   = var.alb_hostname != "" ? 1 : 0
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"
 
  alias {
    name                   = var.alb_hostname
    zone_id                = var.alb_hosted_zone_id
    evaluate_target_health = true
  }
}
