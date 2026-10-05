#!/bin/bash

# remove secrets managers from terraform state
terraform state rm aws_secretsmanager_secret.openrouter_api_key
terraform state rm aws_secretsmanager_secret.monitoring

# remove ecr from terraform state
terraform state rm aws_ecr_repository.rag_system
