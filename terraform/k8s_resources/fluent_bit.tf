resource "helm_release" "fluent_bit" {
  name       = "fluent-bit"
  repository = "https://fluent.github.io/helm-charts"
  chart      = "fluent-bit"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "0.47.5"

  wait    = true
  timeout = 300

  values = [
    file("${path.module}/fluent-bit-values.yml")
  ]

  depends_on = [helm_release.loki]
}
