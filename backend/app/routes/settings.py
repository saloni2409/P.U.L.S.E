"""User settings routes for AI provider configuration"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.ai_config_service import AIConfigService

router = APIRouter(prefix="/api/user", tags=["settings"])


# Pydantic models for request/response
class SetAIConfigRequest(BaseModel):
    """Request to set AI provider configuration"""
    provider_type: str = Field(..., description="GEMINI, OPENAI, ANTHROPIC, LOCAL")
    api_key: Optional[str] = Field(None, description="API key or token (encrypted)")
    model_name: Optional[str] = Field(None, description="Model ID (e.g., gpt-4, llama3)")
    base_url: Optional[str] = Field(None, description="Base URL for local providers")
    is_active: bool = True


class AIConfigResponse(BaseModel):
    """General AI configuration response (safe)"""
    provider_type: str
    model_name: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class SetAIConfigResponse(BaseModel):
    """Response when setting AI config"""
    success: bool
    message: str
    provider: str


# Endpoints

@router.post("/ai-config", response_model=SetAIConfigResponse)
async def set_ai_config(
    request: SetAIConfigRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Set or update an AI provider configuration.
    """
    try:
        result = await AIConfigService.set_user_config(
            db=db,
            user_id=user_id,
            provider_type=request.provider_type,
            api_key=request.api_key,
            model_name=request.model_name,
            base_url=request.base_url,
            is_active=request.is_active
        )
        return SetAIConfigResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set configuration: {str(e)}"
        )


@router.get("/ai-config/active", response_model=Optional[AIConfigResponse])
async def get_active_ai_config(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get the currently active AI configuration.
    """
    config = await AIConfigService.get_active_config(db, user_id)
    if not config:
        return None
        
    return AIConfigResponse(
        provider_type=str(config.get("provider_type", "")),
        model_name=config.get("model_name"),
        base_url=config.get("base_url"),
        is_active=bool(config.get("is_active", False)),
        created_at=config.get("created_at").isoformat() if hasattr(config.get("created_at"), "isoformat") else str(config.get("created_at", "")),
        updated_at=config.get("updated_at").isoformat() if hasattr(config.get("updated_at"), "isoformat") else str(config.get("updated_at", ""))
    )


# --- Backward Compatibility Endpoints (for Frontend v2 legacy calls) ---

@router.post("/gemini-key", response_model=SetAIConfigResponse)
async def set_gemini_key_legacy(
    request: dict, # Support old {api_key: "..."} format
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    api_key = request.get("api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key required")
        
    result = await AIConfigService.set_user_config(
        db=db,
        user_id=user_id,
        provider_type="GEMINI",
        api_key=api_key
    )
    return SetAIConfigResponse(**result)


@router.get("/gemini-key/status")
async def get_gemini_key_status_legacy(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    config = await AIConfigService.get_active_config(db, user_id)
    has_key = config is not None and config.get("provider_type") == "GEMINI"
    
    updated_at = config.get("updated_at") if config else None
    created_at = config.get("created_at") if config else None
    
    return {
        "has_key": has_key,
        "last_verified": updated_at.isoformat() if (has_key and hasattr(updated_at, "isoformat")) else str(updated_at) if (has_key and updated_at) else None,
        "created_at": created_at.isoformat() if (has_key and hasattr(created_at, "isoformat")) else str(created_at) if (has_key and created_at) else None,
        "setup_required": not has_key
    }
