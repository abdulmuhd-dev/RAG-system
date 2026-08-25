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
    MODEL_NAME         = var.model_name
  })
}
