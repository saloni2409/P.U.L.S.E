"""Encryption service for securing sensitive data like API keys"""

import os
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional
import base64
from hashlib import sha256


class EncryptionService:
    """
    Service for encrypting/decrypting sensitive data using AES-256 (via Fernet)
    
    Fernet provides AES 128-bit encryption with HMAC authentication.
    Keys must be 32-byte base64 encoded Fernet keys.
    """
    
    def __init__(self, master_key: str):
        """
        Initialize encryption service with master key.
        
        Args:
            master_key: Base64 encoded Fernet key (must be valid)
            
        Raises:
            ValueError: If master key is invalid or not provided
        """
        if not master_key:
            raise ValueError("Master encryption key is required")
        
        try:
            # Validate it's a valid Fernet key
            self.cipher_suite = Fernet(master_key.encode())
            self.master_key = master_key
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {str(e)}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using Fernet (AES-128 with HMAC).
        
        Args:
            plaintext: Data to encrypt (e.g., API key)
            
        Returns:
            Encrypted data as base64 string
            
        Raises:
            ValueError: If plaintext is empty or encryption fails
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty data")
        
        try:
            encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data.
        
        WARNING: Decrypted data should only be kept in memory for as long as needed.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Decrypted plaintext
            
        Raises:
            ValueError: If decryption fails or data is corrupted
        """
        if not encrypted_data:
            raise ValueError("Cannot decrypt empty data")
        
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except InvalidToken:
            raise ValueError("Decryption failed: Invalid or corrupted data")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64 encoded Fernet key as string
            
        Example:
            key = EncryptionService.generate_key()
            print(f"Add to .env: ENCRYPTION_KEY={key}")
        """
        key = Fernet.generate_key()
        return key.decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: str = "P.U.L.S.E") -> str:
        """
        Derive encryption key from a password (not currently used, kept for future).
        
        Args:
            password: Password to derive from
            salt: Salt for key derivation
            
        Returns:
            Base64 encoded key
        """
        combined = f"{password}:{salt}"
        derived = sha256(combined.encode()).digest()
        return base64.urlsafe_b64encode(derived).decode()
