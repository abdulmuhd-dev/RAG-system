resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }

  depends_on = [data.terraform_remote_state.infrastructure]
}

resource "helm_release" "kube_prometheus_stack" {
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "61.3.2"

  wait    = true
  timeout = 600

  values = [
    yamlencode({
      # Grafana — disable built-in
      # deploy Grafana separately for more control
      grafana = {
        enabled = false
      }

      # Prometheus settings
      prometheus = {
        prometheusSpec = {

          scrapeInterval = "15s"

          # scrape ALL ServiceMonitors across namespaces
          # not just the ones in the same namespace
          serviceMonitorSelectorNilUsesHelmValues = false
          podMonitorSelectorNilUsesHelmValues     = false

          retention = "7d"

          resources = {
            requests = {
              cpu    = "200m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }

          # persistent storage for metrics
          storageSpec = {
            volumeClaimTemplate = {
              spec = {
                storageClassName = "gp2"
                accessModes      = ["ReadWriteOnce"]
                resources = {
                  requests = {
                    storage = "10Gi"
                  }
                }
              }
            }
          }
        }
      }

      # AlertManager disabled for now
      alertmanager = {
        enabled = false
      }
    })
  ]

  depends_on = [
    kubernetes_namespace.monitoring
  ]
}

