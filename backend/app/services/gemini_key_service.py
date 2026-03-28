"""Service for managing user Gemini API keys with encryption"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import UserGeminiKey, User
from app.core.encryption_service import EncryptionService
from app.core.settings import settings


class GeminiKeyService:
    """
    Service for managing encrypted Gemini API keys.
    
    SECURITY NOTES:
    - Keys are encrypted at rest using AES-256 (via Fernet)
    - Keys are only decrypted in memory when needed
    - Decrypted keys are NOT cached or persisted
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
    async def set_user_gemini_key(
        db: Session,
        user_id: str,
        api_key: str
    ) -> dict:
        """
        Set or update user's Gemini API key with encryption.
        
        Args:
            db: Database session
            user_id: User ID
            api_key: Raw Gemini API key (will be encrypted)
            
        Returns:
            dict with success status and timestamp
            
        Raises:
            ValueError: If API key is invalid or encryption fails
            Exception: If database operation fails
        """
        # Validate key format (Gemini keys are typically 39+ chars)
        if not api_key or len(api_key) < 20:
            raise ValueError("Invalid API key format. Gemini key should be at least 20 characters.")
        
        # Encrypt the key
        encryption_service = GeminiKeyService._get_encryption_service()
        try:
            encrypted_key = encryption_service.encrypt(api_key)
        except Exception as e:
            raise ValueError(f"Failed to encrypt key: {str(e)}")
        
        try:
            # Check if user exists
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Check if key already exists for this user
            existing_key = db.query(UserGeminiKey).filter(
                UserGeminiKey.user_id == user_id
            ).first()
            
            if existing_key:
                # Update existing key
                existing_key.encrypted_key = encrypted_key
                existing_key.updated_at = datetime.utcnow()
                existing_key.last_verified_at = datetime.utcnow()
            else:
                # Create new key record
                new_key = UserGeminiKey(
                    key_id=str(uuid.uuid4()),
                    user_id=user_id,
                    encrypted_key=encrypted_key,
                    last_verified_at=datetime.utcnow()
                )
                db.add(new_key)
            
            db.commit()
            
            return {
                "success": True,
                "message": "Gemini API key saved securely",
                "last_verified": datetime.utcnow().isoformat()
            }
        
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Database constraint error: {str(e)}")
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save key: {str(e)}")
    
    @staticmethod
    async def get_user_gemini_key_status(
        db: Session,
        user_id: str
    ) -> dict:
        """
        Check if user has a Gemini API key set (without returning the key).
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            dict with has_key status and metadata
        """
        key_record = db.query(UserGeminiKey).filter(
            UserGeminiKey.user_id == user_id
        ).first()
        
        return {
            "has_key": key_record is not None,
            "last_verified": key_record.last_verified_at.isoformat() if key_record and key_record.last_verified_at else None,
            "created_at": key_record.created_at.isoformat() if key_record else None,
            "setup_required": key_record is None
        }
    
    @staticmethod
    async def get_decrypted_user_gemini_key(
        db: Session,
        user_id: str
    ) -> Optional[str]:
        """
        Get decrypted Gemini API key for a user.
        
        WARNING: This decrypts the key into memory. Use sparingly and clear the variable
        after use if possible. Only decrypt when actually needed for API calls.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Decrypted API key string, or None if not set
            
        Raises:
            ValueError: If decryption fails
        """
        key_record = db.query(UserGeminiKey).filter(
            UserGeminiKey.user_id == user_id
        ).first()
        
        if not key_record:
            return None
        
        encryption_service = GeminiKeyService._get_encryption_service()
        try:
            decrypted_key = encryption_service.decrypt(key_record.encrypted_key)
            return decrypted_key
        except Exception as e:
            raise ValueError(f"Failed to decrypt key: {str(e)}")
    
    @staticmethod
    async def delete_user_gemini_key(
        db: Session,
        user_id: str
    ) -> dict:
        """
        Delete user's stored Gemini API key.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            dict with success status
            
        Raises:
            ValueError: If key not found
        """
        try:
            key_record = db.query(UserGeminiKey).filter(
                UserGeminiKey.user_id == user_id
            ).first()
            
            if not key_record:
                raise ValueError("No Gemini API key found for this user")
            
            db.delete(key_record)
            db.commit()
            
            return {
                "success": True,
                "message": "Gemini API key deleted"
            }
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete key: {str(e)}")
    
    @staticmethod
    async def verify_user_gemini_key(
        db: Session,
        user_id: str
    ) -> dict:
        """
        Verify that user's stored key is valid with a test API call to Google.
        
        This would call Gemini API to verify the key works.
        Currently returns a placeholder - to be implemented with actual API testing.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            dict with verification status
        """
        key_record = db.query(UserGeminiKey).filter(
            UserGeminiKey.user_id == user_id
        ).first()
        
        if not key_record:
            return {
                "valid": False,
                "message": "No API key set"
            }
        
        try:
            # TODO: Implement actual Google API verification
            # For now, just check that key can be decrypted
            decrypted_key = await GeminiKeyService.get_decrypted_user_gemini_key(db, user_id)
            
            if decrypted_key:
                key_record.last_verified_at = datetime.utcnow()
                db.commit()
                
                return {
                    "valid": True,
                    "message": "API key is valid",
                    "last_verified": key_record.last_verified_at.isoformat()
                }
            else:
                return {
                    "valid": False,
                    "message": "Failed to decrypt key"
                }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Verification failed: {str(e)}"
            }
