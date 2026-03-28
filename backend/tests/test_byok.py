"""Tests for BYOK (Bring Your Own Key) functionality"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models import User, UserGeminiKey
from app.core.database import SessionLocal
from app.core.encryption_service import EncryptionService
from app.services.gemini_key_service import GeminiKeyService
from app.core.settings import settings


@pytest.fixture
def db_session():
    """Create test database session"""
    return SessionLocal()


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        user_id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()


class TestEncryptionService:
    """Test encryption service"""
    
    def test_generate_key(self):
        """Test encryption key generation"""
        key = EncryptionService.generate_key()
        assert key is not None
        assert len(key) > 0
        assert isinstance(key, str)
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        service = EncryptionService(settings.encryption_key)
        plaintext = "test_api_key_12345678"
        
        encrypted = service.encrypt(plaintext)
        assert encrypted != plaintext
        
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_encrypt_empty_fails(self):
        """Test that encrypting empty data fails"""
        service = EncryptionService(settings.encryption_key)
        
        with pytest.raises(ValueError):
            service.encrypt("")
    
    def test_decrypt_invalid_fails(self):
        """Test that decrypting invalid data fails"""
        service = EncryptionService(settings.encryption_key)
        
        with pytest.raises(ValueError):
            service.decrypt("invalid_encrypted_data")


class TestGeminiKeyService:
    """Test Gemini key service"""
    
    @pytest.mark.asyncio
    async def test_set_user_gemini_key(self, db_session, test_user):
        """Test setting user's Gemini key"""
        test_key = "AIzaSyDummyKeyFor_Testing_12345"
        
        result = await GeminiKeyService.set_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id,
            api_key=test_key
        )
        
        assert result["success"] is True
        assert "saved securely" in result["message"]
        
        # Verify key was stored
        stored_key = db_session.query(UserGeminiKey).filter(
            UserGeminiKey.user_id == test_user.user_id
        ).first()
        assert stored_key is not None
        assert stored_key.encrypted_key != test_key  # Should be encrypted
    
    @pytest.mark.asyncio
    async def test_set_invalid_key_fails(self, db_session, test_user):
        """Test that setting an invalid key fails"""
        with pytest.raises(ValueError):
            await GeminiKeyService.set_user_gemini_key(
                db=db_session,
                user_id=test_user.user_id,
                api_key="short"  # Too short
            )
    
    @pytest.mark.asyncio
    async def test_get_key_status_no_key(self, db_session, test_user):
        """Test getting status when no key is set"""
        status = await GeminiKeyService.get_user_gemini_key_status(
            db=db_session,
            user_id=test_user.user_id
        )
        
        assert status["has_key"] is False
        assert status["setup_required"] is True
    
    @pytest.mark.asyncio
    async def test_get_key_status_with_key(self, db_session, test_user):
        """Test getting status when key is set"""
        test_key = "AIzaSyDummyKeyFor_Testing_12345"
        
        await GeminiKeyService.set_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id,
            api_key=test_key
        )
        
        status = await GeminiKeyService.get_user_gemini_key_status(
            db=db_session,
            user_id=test_user.user_id
        )
        
        assert status["has_key"] is True
        assert status["setup_required"] is False
    
    @pytest.mark.asyncio
    async def test_get_decrypted_key(self, db_session, test_user):
        """Test retrieving and decrypting user's key"""
        test_key = "AIzaSyDummyKeyFor_Testing_12345"
        
        await GeminiKeyService.set_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id,
            api_key=test_key
        )
        
        decrypted_key = await GeminiKeyService.get_decrypted_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id
        )
        
        assert decrypted_key == test_key
    
    @pytest.mark.asyncio
    async def test_get_decrypted_key_not_found(self, db_session, test_user):
        """Test retrieving decrypted key when none exists"""
        result = await GeminiKeyService.get_decrypted_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_key(self, db_session, test_user):
        """Test deleting user's key"""
        test_key = "AIzaSyDummyKeyFor_Testing_12345"
        
        await GeminiKeyService.set_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id,
            api_key=test_key
        )
        
        result = await GeminiKeyService.delete_user_gemini_key(
            db=db_session,
            user_id=test_user.user_id
        )
        
        assert result["success"] is True
        
        # Verify key was deleted
        status = await GeminiKeyService.get_user_gemini_key_status(
            db=db_session,
            user_id=test_user.user_id
        )
        assert status["has_key"] is False
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_key_fails(self, db_session, test_user):
        """Test that deleting nonexistent key fails"""
        with pytest.raises(ValueError):
            await GeminiKeyService.delete_user_gemini_key(
                db=db_session,
                user_id=test_user.user_id
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
