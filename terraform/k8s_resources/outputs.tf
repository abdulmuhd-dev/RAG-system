output "argocd_get_password" {
 description = "Command to get ArgoCD default password"
 value = <<EOD
     kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
     | base64 -d && echo
    EOD
}

output "argocd_alb_hostname" {
  description = "ArgoCD ALB hostname"
  value       = kubernetes_ingress_v1.argocd.status[0].load_balancer[0].ingress[0].hostname
}
