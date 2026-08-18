# ArgoCD K8s namespace
resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }

  depends_on = [aws_eks_node_group.main]
}

# ArgoCD helm installation on EKS
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = kubernetes_namespace.argocd.metadata[0].name
  version    = "7.3.11"   # pin version — never use latest in production

  # wait until all ArgoCD pods are running before
  # Terraform considers this resource complete
  wait    = true
  timeout = 600   # 10 minutes

  values = [
    yamlencode({
      # expose ArgoCD server via LoadBalancer
      # so we can access the UI and CLI from outside EKS
      server = {
        service = {
          type = "LoadBalancer"
        }
        # disable TLS inside the cluster
        # TLS is terminated at the ALB level
        extraArgs = ["--insecure"]
      }

      # resource limits prevents ArgoCD
      # from starving app pods
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
    aws_eks_node_group.main,
    kubernetes_namespace.argocd
  ]
}

# helm install ALB controller
resource "helm_release" "alb_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.8.1"

  wait    = true
  timeout = 300

  set {
    name  = "clusterName"
    value = aws_eks_cluster.main.name
  }

  set {
    name  = "serviceAccount.create"
    value = "true"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.alb_controller.arn
  }

  set {
    name  = "region"
    value = var.aws_region
  }

  set {
    name  = "vpcId"
    value = aws_vpc.main.id
  }

  depends_on = [
    aws_eks_node_group.main,
    aws_iam_role_policy_attachment.alb_controller,
  ]
}

# helm install metrics server to collect CPU/RAM metrics from pods
# Required for HPA to work
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

  depends_on = [aws_eks_node_group.main]
}
