"""Application settings and configuration"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./pulse.db"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
