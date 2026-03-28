"""Service for managing user AI configurations with encryption"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import UserAIConfig, User
from app.core.encryption_service import EncryptionService
from app.core.settings import settings


class AIConfigService:
    """
    Service for managing encrypted AI Provider configurations.
    
    SECURITY NOTES:
    - Keys/Tokens are encrypted at rest using AES-256 (via Fernet)
    - Sensitive data is only decrypted in memory when needed
    - Master encryption key must be set in environment variables
    """
    
    @staticmethod
    def _get_encryption_service() -> EncryptionService:
        """Get encryption service with master key from settings"""
        if not settings.encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY not configured. "
                "Generate one with: python -c 'from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())'"
            )
        return EncryptionService(settings.encryption_key)
    
    @staticmethod
    async def set_user_config(
        db: Session,
        user_id: str,
        provider_type: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        is_active: bool = True
    ) -> dict:
        """
        Set or update user's AI configuration.
        """
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
            # Check if user exists
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # If this is set to active, deactivate other configs for this user
            if is_active:
                db.query(UserAIConfig).filter(
                    UserAIConfig.user_id == user_id
                ).update({"is_active": False})
            
            # Check if config already exists for this provider
            existing_config = db.query(UserAIConfig).filter(
                UserAIConfig.user_id == user_id,
                UserAIConfig.provider_type == provider_type
            ).first()
            
            if existing_config:
                existing_config.encrypted_key = encrypted_key if encrypted_key else existing_config.encrypted_key
                existing_config.model_name = model_name if model_name else existing_config.model_name
                existing_config.base_url = base_url if base_url else existing_config.base_url
                existing_config.is_active = is_active
                existing_config.updated_at = datetime.utcnow()
            else:
                new_config = UserAIConfig(
                    config_id=str(uuid.uuid4()),
                    user_id=user_id,
                    provider_type=provider_type,
                    model_name=model_name,
                    base_url=base_url,
                    encrypted_key=encrypted_key,
                    is_active=is_active
                )
                db.add(new_config)
            
            db.commit()
            
            return {
                "success": True,
                "message": f"{provider_type} configuration saved successfully",
                "provider": provider_type
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save configuration: {str(e)}")

    @staticmethod
    async def get_active_config(db: Session, user_id: str) -> Optional[UserAIConfig]:
        """Get the currently active AI configuration for a user"""
        return db.query(UserAIConfig).filter(
            UserAIConfig.user_id == user_id,
            UserAIConfig.is_active == True
        ).first()

    @staticmethod
    async def get_decrypted_key(db: Session, config: UserAIConfig) -> Optional[str]:
        """Decrypt the key from a config object"""
        if not config.encrypted_key:
            return None
            
        encryption_service = AIConfigService._get_encryption_service()
        try:
            return encryption_service.decrypt(config.encrypted_key)
        except Exception as e:
            raise ValueError(f"Failed to decrypt key: {str(e)}")

    # --- Backward Compatibility Methods ---
    
    @staticmethod
    async def get_decrypted_user_gemini_key(db: Session, user_id: str) -> Optional[str]:
        """Helper for legacy code - gets the active Gemini key"""
        config = db.query(UserAIConfig).filter(
            UserAIConfig.user_id == user_id,
            UserAIConfig.provider_type == "GEMINI"
        ).first()
        
        if not config:
            return None
        return await AIConfigService.get_decrypted_key(db, config)
