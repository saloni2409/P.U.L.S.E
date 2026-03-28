"""Service for managing user AI configurations with repository abstraction"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.repositories.factory import RepositoryFactory
from app.core.encryption_service import EncryptionService
from app.core.settings import settings


class AIConfigService:
    """
    Service for managing AI Provider configurations via repositories.
    Supports SQL (Postgres/SQLite) and NoSQL (Firestore).
    """
    
    @staticmethod
    def _get_encryption_service() -> EncryptionService:
        """Get encryption service with master key from settings"""
        if not settings.encryption_key:
            raise ValueError("ENCRYPTION_KEY not configured.")
        return EncryptionService(settings.encryption_key)
    
    @staticmethod
    async def set_user_config(
        db: Any,
        user_id: str,
        provider_type: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        is_active: bool = True
    ) -> dict:
        """Set or update user's AI configuration using repository"""
        repo = RepositoryFactory.get_ai_config_repository(db)
        provider_type = provider_type.upper()
        
        # Encrypt key if provided
        encrypted_key = None
        if api_key:
            encryption_service = AIConfigService._get_encryption_service()
            try:
                encrypted_key = encryption_service.encrypt(api_key)
            except Exception as e:
                raise ValueError(f"Failed to encrypt key: {str(e)}")
        
        try:
            # If this is set to active, deactivate other configs for this user
            if is_active:
                repo.deactivate_other_configs(user_id, provider_type)
            
            # Check if config already exists for this provider
            existing = repo.get_config_by_provider(user_id, provider_type)
            
            config_data = {
                "user_id": user_id,
                "provider_type": provider_type,
                "is_active": is_active
            }
            if encrypted_key: config_data["encrypted_key"] = encrypted_key
            if model_name: config_data["model_name"] = model_name
            if base_url: config_data["base_url"] = base_url
            
            result = repo.upsert_config(config_data)
            
            return {
                "success": True,
                "message": f"{provider_type} configuration saved successfully",
                "provider": provider_type
            }
            
        except Exception as e:
            raise Exception(f"Failed to save configuration: {str(e)}")

    @staticmethod
    async def get_active_config(db: Any, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the currently active AI configuration for a user"""
        repo = RepositoryFactory.get_ai_config_repository(db)
        return repo.get_active_config(user_id)

    @staticmethod
    async def get_decrypted_key(db: Any, config: Dict[str, Any]) -> Optional[str]:
        """Decrypt the key from a config dictionary"""
        encrypted_key = config.get("encrypted_key")
        if not encrypted_key:
            return None
            
        encryption_service = AIConfigService._get_encryption_service()
        try:
            return encryption_service.decrypt(encrypted_key)
        except Exception as e:
            raise ValueError(f"Failed to decrypt key: {str(e)}")

    # --- Backward Compatibility Methods ---
    
    @staticmethod
    async def get_decrypted_user_gemini_key(db: Any, user_id: str) -> Optional[str]:
        """Helper for legacy code - gets the active Gemini key"""
        repo = RepositoryFactory.get_ai_config_repository(db)
        config = repo.get_config_by_provider(user_id, "GEMINI")
        
        if not config:
            return None
        return await AIConfigService.get_decrypted_key(db, config)
