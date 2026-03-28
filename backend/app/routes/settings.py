"""User settings routes including Gemini API key management"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.gemini_key_service import GeminiKeyService

router = APIRouter(prefix="/api/user", tags=["settings"])


# Pydantic models for request/response
class SetGeminiKeyRequest(BaseModel):
    """Request to set Gemini API key"""
    api_key: str = Field(..., min_length=20, description="Google Gemini API key")


class GeminiKeyStatusResponse(BaseModel):
    """Response for Gemini key status"""
    has_key: bool
    last_verified: Optional[str] = None
    created_at: Optional[str] = None
    setup_required: bool


class SetGeminiKeyResponse(BaseModel):
    """Response when setting Gemini key"""
    success: bool
    message: str
    last_verified: str


class DeleteKeyResponse(BaseModel):
    """Response when deleting key"""
    success: bool
    message: str


class VerifyKeyResponse(BaseModel):
    """Response for key verification"""
    valid: bool
    message: str
    last_verified: Optional[str] = None


# Endpoints

@router.post("/gemini-key", response_model=SetGeminiKeyResponse)
async def set_gemini_key(
    request: SetGeminiKeyRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Set or update user's Gemini API key.
    
    The API key is encrypted before storage and never persisted in plaintext.
    
    Security:
    - Only HTTPS is allowed
    - User must be authenticated (JWT token)
    - Key is validated for format
    - Key is encrypted with AES-256 before storage
    
    Args:
        request: SetGeminiKeyRequest with api_key
        user_id: Extracted from JWT token
        db: Database session
        
    Returns:
        SetGeminiKeyResponse with success status
        
    Raises:
        HTTPException: 400 if key is invalid
        HTTPException: 401 if not authenticated
        HTTPException: 500 if encryption or storage fails
    """
    try:
        result = await GeminiKeyService.set_user_gemini_key(
            db=db,
            user_id=user_id,
            api_key=request.api_key
        )
        return SetGeminiKeyResponse(
            success=result["success"],
            message=result["message"],
            last_verified=result["last_verified"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set API key: {str(e)}"
        )


@router.get("/gemini-key/status", response_model=GeminiKeyStatusResponse)
async def get_gemini_key_status(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Check if user has a Gemini API key set.
    
    This endpoint does NOT return the actual API key.
    It only indicates whether a key exists and when it was last verified.
    
    Args:
        user_id: Extracted from JWT token
        db: Database session
        
    Returns:
        GeminiKeyStatusResponse with status information
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    try:
        status_info = await GeminiKeyService.get_user_gemini_key_status(
            db=db,
            user_id=user_id
        )
        return GeminiKeyStatusResponse(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check key status: {str(e)}"
        )


@router.delete("/gemini-key", response_model=DeleteKeyResponse)
async def delete_gemini_key(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete user's stored Gemini API key.
    
    This removes the encrypted key from the database.
    User will need to set a new key to use chat features.
    
    Args:
        user_id: Extracted from JWT token
        db: Database session
        
    Returns:
        DeleteKeyResponse with success status
        
    Raises:
        HTTPException: 400 if no key found
        HTTPException: 401 if not authenticated
        HTTPException: 500 if deletion fails
    """
    try:
        result = await GeminiKeyService.delete_user_gemini_key(
            db=db,
            user_id=user_id
        )
        return DeleteKeyResponse(
            success=result["success"],
            message=result["message"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API key: {str(e)}"
        )


@router.post("/gemini-key/verify", response_model=VerifyKeyResponse)
async def verify_gemini_key(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Verify that user's stored Gemini API key is valid.
    
    This makes a test call to the Gemini API to verify the key works.
    Updates last_verified_at timestamp if validation succeeds.
    
    Args:
        user_id: Extracted from JWT token
        db: Database session
        
    Returns:
        VerifyKeyResponse with validation status
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 500 if verification fails
    """
    try:
        result = await GeminiKeyService.verify_user_gemini_key(
            db=db,
            user_id=user_id
        )
        return VerifyKeyResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )
