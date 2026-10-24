# RAG System — Production AI Platform

A production-grade Retrieval-Augmented Generation (RAG) system
built with LangChain, ChromaDB, and Flask. Fully deployed on
AWS EKS with GitOps, observability, and a complete DevSecOps
CI/CD pipeline.

---

## 🏗️ Architecture
![RAG-system Architecture Diagram](architecture_diagram.jpg)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI/RAG | LangChain, ChromaDB, OpenRouter |
| Embeddings | ONNX Runtime (all-MiniLM-L6-v2, local) |
| API | Flask + Gunicorn |
| Container | Docker (multi-stage, non-root, 934MB) |
| Orchestration | Kubernetes (AWS EKS v1.36) |
| IaC | Terraform (3 layers) |
| GitOps | ArgoCD |
| CI/CD | GitHub Actions (OIDC, no long-lived credentials) |
| Secrets | AWS Secrets Manager + External Secrets Operator |
| Ingress | AWS ALB Controller |
| DNS | Route53 + DigitalPlat |
| TLS | AWS ACM |
| Metrics | Prometheus + kube-prometheus-stack |
| Logs | Fluent Bit (DaemonSet) + Loki |
| Dashboard | Grafana |
| Registry | Amazon ECR |

---

## 🔄 RAG Pipeline
![RAG-system Pipeline](RAG_pipeline.png)

---

## 🏗️ Infrastructure — 3 Terraform Layers
![RAG-system Pipeline](terraform_structure.png)

### Deploy Order

```bash
# provision steps 
cd terraform/infrastructure && terraform apply
cd terraform/k8s_resources  && terraform apply
cd terraform/dns_acm        && terraform apply
cd <project root directory> && kubectl apply -f k8s/argocd-app.yml

# destroy (reverse order)
kubectl delete application rag-api -n argocd 
cd terraform/dns_acm        && terraform destroy
cd terraform/k8s_resources  && terraform destroy
cd terraform/infrastructure && terraform destroy
```
---

## 🔐 Security

| Layer | Implementation |
|-------|----------------|
| CI/CD auth | OIDC federation (no long-lived AWS credentials) |
| Pod AWS access | IRSA (IAM Roles for Service Accounts) |
| Secrets | External Secrets Operator → AWS Secrets Manager |
| Container | Non-root user, dropped Linux capabilities |
| Image scanning | Trivy (blocks CRITICAL/HIGH CVEs) |
| Code scanning | Bandit (Python SAST) |
| Dependency scanning | pip-audit (CVE detection) |
| Secret scanning | Gitleaks (pre-push) |
| Network | EKS nodes in private subnets only |
| TLS | ACM wildcard cert, HTTP → HTTPS redirect |

## ♾️ CI/CD Pipeline
