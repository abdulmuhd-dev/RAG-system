resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "8.3.4"

  wait    = true
  timeout = 300

  values = [
    templatefile("${path.module}/grafana-values.yml", {
      acm_certificate_arn = var.acm_certificate_arn
    })
  ]

  depends_on = [
    helm_release.kube_prometheus_stack,
    helm_release.loki,
  ]
}

