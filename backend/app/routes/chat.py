"""Chat meal logging routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.chat_session_service import ChatSessionService

router = APIRouter(prefix="/api/meals-ai/chat", tags=["chat"])


# Pydantic models

class StartChatRequest(BaseModel):
    """Request to start a chat session"""
    meal_type: Optional[str] = Field(None, description="BREAKFAST, LUNCH, DINNER, or SNACK - optional, will be extracted from conversation")


class ChatMessageRequest(BaseModel):
    """User message in chat"""
    message: str = Field(..., description="User's message")


class MealItem(BaseModel):
    """Food item in meal"""
    food_name: str
    quantity: float
    unit: str
    calories: Optional[float] = None


class UpdateMealItemsRequest(BaseModel):
    """Request to update meal items"""
    meal_items: List[MealItem]


class ChatSessionResponse(BaseModel):
    """Chat session response"""
    session_id: str
    meal_type: Optional[str] = None
    message: Optional[str] = None
    state: str
    meal_items: list = []
    nutrition: dict = {}


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    message_id: str
    role: str  # USER, ASSISTANT, SYSTEM
    content: str
    created_at: str


# Endpoints

@router.post("/start")
async def start_chat_session(
    request: StartChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ChatSessionResponse:
    """
    Start a new chat session for meal logging.
    
    Args:
        request: StartChatRequest with optional meal_type
        user_id: From JWT token
        db: Database session
        
    Returns:
        ChatSessionResponse with initial greeting
    """
    try:
        meal_type = request.meal_type.upper() if request.meal_type else None
        result = await ChatSessionService.create_session(
            db=db,
            user_id=user_id,
            meal_type=meal_type
        )
        
        return ChatSessionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/send-message/{session_id}")
async def send_chat_message(
    session_id: str,
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ChatSessionResponse:
    """
    Send message in chat session and get agent response.
    
    Args:
        session_id: Chat session ID
        request: ChatMessageRequest with message
        user_id: From JWT token
        db: Database session
        
    Returns:
        ChatSessionResponse with agent response
    """
    try:
        result = await ChatSessionService.send_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            message_text=request.message
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ChatSessionResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/messages/{session_id}")
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> List[ChatMessageResponse]:
    """
    Get all messages in a chat session.
    
    Args:
        session_id: Chat session ID
        user_id: From JWT token
        db: Database session
        
    Returns:
        List of messages
    """
    try:
        messages = ChatSessionService.get_session_messages(db, user_id, session_id)
        return [ChatMessageResponse(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/summary/{session_id}")
async def get_meal_summary(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get parsed meal summary for confirmation.
    
    Args:
        session_id: Chat session ID
        user_id: From JWT token
        db: Database session
        
    Returns:
        Meal summary with items and nutrition
    """
    try:
        summary = await ChatSessionService.get_meal_summary(db, user_id, session_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/meal-items/{session_id}")
async def update_meal_items(
    session_id: str,
    request: UpdateMealItemsRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Update meal items in session (user edited in confirmation UI).
    
    Args:
        session_id: Chat session ID
        request: UpdateMealItemsRequest with updated items
        user_id: From JWT token
        db: Database session
        
    Returns:
        Updated session
    """
    try:
        # Convert Pydantic models to dicts
        meal_items = [item.model_dump() for item in request.meal_items]
        
        result = await ChatSessionService.update_meal_items(
            db=db,
            user_id=user_id,
            session_id=session_id,
            meal_items=meal_items
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/save/{session_id}")
async def save_meal_to_log(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Save meal from chat session to meal log.
    
    Args:
        session_id: Chat session ID
        user_id: From JWT token
        db: Database session
        
    Returns:
        Confirmation message
    """
    try:
        result = await ChatSessionService.save_meal_to_log(db, user_id, session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/cancel/{session_id}")
async def cancel_chat_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Cancel chat session without saving.
    
    Args:
        session_id: Chat session ID
        user_id: From JWT token
        db: Database session
        
    Returns:
        Cancellation confirmation
    """
    try:
        result = await ChatSessionService.cancel_session(db, user_id, session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
