from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ai-kubernetes-agent"
    ENVIRONMENT: str = "development"
    
    # AWS Credentials & Bedrock Configuration (Qwen3 Coder Next Model)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BEDROCK_MODEL_ID: str = "qwen.qwen3-coder-next"
    AWS_DYNAMODB_TABLE: str = "k8s_investigation_history"

    # Fallback OpenRouter / Local LLM settings
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "qwen/qwen3-coder-next"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Kubernetes configuration
    KUBECONFIG_PATH: str = "~/.kube/config"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
