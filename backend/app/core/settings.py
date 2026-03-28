"""Application settings and configuration"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/pulse"
    db_type: str = "SQL" # SQL or FIRESTORE
    firestore_project_id: str = ""
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    
    # LLM Configuration
    llm_service: Literal["local", "openai", "anthropic"] = "local"
    llm_local_endpoint: str = "http://localhost:11434"
    llm_local_model: str = "llama2"
    llm_openai_key: str = ""
    llm_anthropic_key: str = ""
    
    # BYOK (Bring Your Own Key) Configuration
    byok_enabled: bool = True
    require_user_key: bool = True
    encryption_key: str = ""  # Must be set in .env - base64 Fernet key
    default_gemini_key: str = ""  # Optional fallback for demo/development
    gemini_model: str = "gemini-1.5-pro"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
