resource "aws_secretsmanager_secret" "openrouter_api_key" {
  name        = "rag-system/openrouter-api-key"
  description = "OpenRouter API key for RAG system"

  # prevents accidental deletion
  recovery_window_in_days = 7

  tags = {
    Name = "rag-system-openrouter-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "openrouter_api_key" {
  secret_id = aws_secretsmanager_secret.openrouter_api_key.id

  secret_string = jsonencode({
    OPENROUTER_API_KEY = var.openrouter_api_key
  })
}

# Monitoring secrets
resource "aws_secretsmanager_secret" "monitoring" {
  name        = "rag-system/monitoring"
  description = "Monitoring system secrets"

  # prevents accidental deletion                 
  recovery_window_in_days = 7

  tags = {
    Name = "Monitoring"
  }
}

resource "aws_secretsmanager_secret_version" "monitoring" {
  secret_id = aws_secretsmanager_secret.monitoring.id

  secret_string = jsonencode({
    GRAFANA_USR = var.grafana_usr
    GRAFANA_PSS = var.grafana_pss
  })
}
