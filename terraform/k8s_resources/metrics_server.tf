# Install Metrics Server to collect CPU/RAM metrics from pods.
# Required for HPA to work.
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.12.1"

  wait    = true
  timeout = 300

  set {
    name  = "args[0]"
    value = "--kubelet-insecure-tls"
  }

}
