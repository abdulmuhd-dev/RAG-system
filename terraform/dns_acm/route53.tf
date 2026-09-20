resource "aws_route53_zone" "main" {
  name = var.domain_name

  tags = {
    Name = var.domain_name
  }
}

# single record — one ALB serves everything
resource "aws_route53_record" "main" {
  count   = var.alb_hostname != "" ? 1 : 0
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "CNAME"
  ttl     = 300
  records = [var.alb_hostname]
}
