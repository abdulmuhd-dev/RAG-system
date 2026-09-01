output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_version" {
  description = "Kubernetes version"
  value       = aws_eks_cluster.main.version
}

output "cluster_certificate_authority" {
  description = "Cluster CA certificate (base64)"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN — needed for IRSA"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "configure_kubectl" {
  description = "Run this command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
}

output "node_group_role_arn" {
  description = "Node group IAM role ARN"
  value       = aws_iam_role.eks_nodes.arn
}

output "ecr_repository_url" {
  description = "ECR repository URL for docker push"
  value       = aws_ecr_repository.rag_system.repository_url
}

output "docker_push_commands" {
  description = "Commands to push image to ECR"
  value       = <<-EOT
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.rag_system.repository_url}
    docker tag rag-system:latest ${aws_ecr_repository.rag_system.repository_url}:latest
    docker push ${aws_ecr_repository.rag_system.repository_url}:latest
  EOT
}

output "secret_arn" {
  description = "Secrets Manager ARN — needed for K8s secret injection"
  value       = aws_secretsmanager_secret.openrouter_api_key.arn
}

output "alb_controller_role_arn" {
  description = "ALB-Controller IAM Role ARN"
  value = aws_iam_role.alb_controller.arn
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions — add to GitHub environment variables"
  value       = aws_iam_role.github_actions.arn
}

output "external_secrets_role_arn" {
  value = aws_iam_role.external_secrets.arn
}
