"""Enhanced meal routes with agentic processing"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas import MealEntryResponse
from app.services.meal_processing_service import MealProcessingService
from fastapi import Header

router = APIRouter(prefix="/api/meals-ai", tags=["meals-ai"])


class MealLogRequest(BaseModel):
    """Request for logging a meal with natural language"""
    meal_description: str
    meal_type: str  # BREAKFAST, LUNCH, DINNER, SNACK
    meal_date: date
    meal_time: str = None
    auto_enrich: bool = True  # Auto-fetch detailed macros


@router.post("/log-ai", response_model=MealEntryResponse)
async def log_meal_with_ai(
    request: MealLogRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Log a meal using natural language processing.
    The AI agent will parse the description and extract food items automatically.
    
    Args:
        request: Meal logging request with natural language description
        user_id: Current user ID
        db: Database session
        
    Returns:
        Created meal entry with AI-parsed items
    """
    try:
        meal = await MealProcessingService.process_meal_with_agent(
            db=db,
            user_id=user_id,
            meal_description=request.meal_description,
            meal_type=request.meal_type,
            meal_date=request.meal_date,
            meal_time=request.meal_time,
            auto_enrich=request.auto_enrich
        )
        return meal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meal processing failed: {str(e)}"
        )


class ManualMealLogRequest(BaseModel):
    """Request for logging a meal manually"""
    meal_description: str
    meal_type: str
    meal_date: date
    meal_time: str = None
    meal_items: list[dict]  # List of {food_name, quantity, unit, calories, macronutrients?}


@router.post("/log-manual", response_model=MealEntryResponse)
async def log_meal_manual(
    request: ManualMealLogRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Log a meal with manually provided items.
    
    Args:
        request: Meal with manually specified items
        user_id: Current user ID
        db: Database session
        
    Returns:
        Created meal entry
    """
    try:
        meal = await MealProcessingService.process_meal_manual(
            db=db,
            user_id=user_id,
            meal_description=request.meal_description,
            meal_type=request.meal_type,
            meal_date=request.meal_date,
            meal_items=request.meal_items,
            meal_time=request.meal_time
        )
        return meal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meal processing failed: {str(e)}"
        )
