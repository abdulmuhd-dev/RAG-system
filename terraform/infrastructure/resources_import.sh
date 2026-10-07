#!/bin/bash

# terraform import ecr
terraform import aws_ecr_repository.rag_system rag-system

# terraform import secret
terraform import aws_secretsmanager_secret.openrouter_api_key rag-system/openrouter-api-key

terraform import aws_secretsmanager_secret.monitoring rag-system/monitoring
