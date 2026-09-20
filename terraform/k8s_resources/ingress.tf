# ArgoCD Ingress resource for AWS Load Balancer Controller.
# Automatically provisions an Application Load Balancer (ALB)
# so the ArgoCD UI can be accessed externally.
resource "kubernetes_ingress_v1" "argocd" {
  metadata {
    name      = "argocd-ingress"
    namespace = kubernetes_namespace.argocd.metadata[0].name

    annotations = {
      "alb.ingress.kubernetes.io/scheme"      = "internet-facing"
      "alb.ingress.kubernetes.io/target-type" = "ip"
      "alb.ingress.kubernetes.io/group.name" =  "platform"
      "alb.ingress.kubernetes.io/listen-ports"        = "[{\"HTTP\": 80}, {\"HTTPS\": 443}]"
      "alb.ingress.kubernetes.io/ssl-redirect"        = "443"
      "alb.ingress.kubernetes.io/certificate-arn"     = var.acm_certificate_arn
      "alb.ingress.kubernetes.io/healthcheck-path"    = "/healthz"
    }
  }

  spec {
    ingress_class_name = "alb"

    rule {

      host = "abdulmuhd.dpdns.org"

      http {
        path {
          path      = "/admin/argocd"
          path_type = "Prefix"

          backend {
            service {
              name = "argocd-server"

              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }

  # Wait for the AWS Load Balancer Controller to
  # populate the Ingress with a load balancer endpoint.
  wait_for_load_balancer = true

  depends_on = [
    helm_release.argocd,
    helm_release.alb_controller
  ]
}
