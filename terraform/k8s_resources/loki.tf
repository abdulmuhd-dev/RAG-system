resource "helm_release" "loki" {
  name       = "loki"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "loki"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "6.7.3"

  wait    = true
  timeout = 600

  values = [
    file("${path.module}/loki-values.yml")
  ]

  depends_on = [kubernetes_namespace.monitoring]
}
