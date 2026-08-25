# ArgoCD Kubernetes namespace
resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

# ArgoCD Helm installation on EKS
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = kubernetes_namespace.argocd.metadata[0].name
  version    = "7.3.11" # Pin version — never use latest in production

  # Wait until all ArgoCD pods are running before
  # Terraform considers this resource complete.
  wait    = true
  timeout = 600 # 10 minutes

  values = [
    yamlencode({
      # Expose ArgoCD server via ClusterIP.
      server = {
        service = {
          type = "ClusterIP"
        }

        # Disable TLS inside the cluster.
        # TLS is terminated at the ALB level.
        extraArgs = ["--insecure"]
        insecure  = true
      }

      configs = {
        params = {
          # Force HTTP — no redirect.
          "server.insecure" = true
	  "server.rootpath" = "/admin/argocd"
          "server.basehref" = "/admin/argocd"
        }
      }

      # Resource limits prevent ArgoCD
      # from starving application pods.
      resources = {
        limits = {
          cpu    = "500m"
          memory = "512Mi"
        }

        requests = {
          cpu    = "250m"
          memory = "256Mi"
        }
      }
    })
  ]

  depends_on = [
    kubernetes_namespace.argocd
  ]
}
