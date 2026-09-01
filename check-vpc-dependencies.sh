#!/usr/bin/env bash

set -euo pipefail

REGION="us-east-1"
CLUSTER_NAME="rag-system"

echo "=========================================="
echo " Checking Indirect AWS Resources"
echo "=========================================="

# --------------------------------------------------
# Get VPC ID dynamically from EKS
# --------------------------------------------------

VPC_ID=$(aws eks describe-cluster \
  --region "$REGION" \
  --name "$CLUSTER_NAME" \
  --query 'cluster.resourcesVpcConfig.vpcId' \
  --output text 2>/dev/null || true)

if [[ -z "$VPC_ID" || "$VPC_ID" == "None" ]]; then
    echo "❌ Could not determine VPC ID from EKS cluster."
    exit 1
fi

echo
echo "EKS Cluster : $CLUSTER_NAME"
echo "VPC ID      : $VPC_ID"

# --------------------------------------------------
# Check ALBs
# --------------------------------------------------

echo
echo "=========================================="
echo " Application Load Balancers"
echo "=========================================="

ALB_COUNT=$(aws elbv2 describe-load-balancers \
  --region "$REGION" \
  --query "length(LoadBalancers[?VpcId=='$VPC_ID'])" \
  --output text)

if [[ "$ALB_COUNT" -eq 0 ]]; then
    echo "✅ No ALBs found in $VPC_ID"
else
    echo "⚠️  $ALB_COUNT ALB(s) found:"
    echo

    aws elbv2 describe-load-balancers \
      --region "$REGION" \
      --query "LoadBalancers[?VpcId=='$VPC_ID'].[LoadBalancerName,State.Code,DNSName]" \
      --output table
fi

# --------------------------------------------------
# Check Security Groups
# --------------------------------------------------

echo
echo "=========================================="
echo " Security Groups"
echo "=========================================="

aws ec2 describe-security-groups \
  --region "$REGION" \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[*].[GroupId,GroupName,Description]' \
  --output table

# --------------------------------------------------
# Highlight Kubernetes-created Security Groups
# --------------------------------------------------

echo
echo "=========================================="
echo " Kubernetes/ALB Security Groups"
echo "=========================================="

K8S_SG_COUNT=$(aws ec2 describe-security-groups \
  --region "$REGION" \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query "length(SecurityGroups[?starts_with(GroupName, 'k8s-')])" \
  --output text)

if [[ "$K8S_SG_COUNT" -eq 0 ]]; then
    echo "✅ No Kubernetes-created security groups found."
else
    echo "⚠️  Kubernetes-created security groups found:"
    echo

    aws ec2 describe-security-groups \
      --region "$REGION" \
      --filters "Name=vpc-id,Values=$VPC_ID" \
      --query "SecurityGroups[?starts_with(GroupName, 'k8s-')].[GroupId,GroupName,Description]" \
      --output table
fi


# Final result

echo
echo "=========================================="
echo " Verification Complete"
echo "=========================================="

if [[ "$ALB_COUNT" -eq 0 && "$K8S_SG_COUNT" -eq 0 ]]; then
    echo "✅ No obvious ALB/Kubernetes security-group"
    echo "   dependencies remain in $VPC_ID."
    echo
    echo "You can proceed with:"
    echo
    echo "  terraform plan -destroy"
    echo "  terraform destroy"
else
    echo "⚠️  Indirect resources still exist."
    echo "   Investigate them before destroying the VPC."
fi
