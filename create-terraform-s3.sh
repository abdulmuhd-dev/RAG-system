#!/bin/bash

# Create terraform remote state file storage
# before you run terraform apply

aws s3api create-bucket \
  --bucket rag-system-tfstate-617711905688 \
  --region us-east-1

# enable versioning — lets you recover old state files
aws s3api put-bucket-versioning \
  --bucket rag-system-tfstate-617711905688 \
  --versioning-configuration Status=Enabled

# enable encryption
aws s3api put-bucket-encryption \
  --bucket rag-system-tfstate-617711905688 \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
