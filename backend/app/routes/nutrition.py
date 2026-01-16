"""Nutrition and analytics API routes"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas import DailyNutritionSummaryResponse
from app.services.nutrition_service import NutritionService
from fastapi import Header

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])



@router.get("/daily/{nutrition_date}", response_model=DailyNutritionSummaryResponse)
def get_daily_nutrition(
    nutrition_date: date,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get daily nutrition summary for a specific date.
    
    Args:
        nutrition_date: Date for the summary
        user_id: Current user ID
        db: Database session
        
    Returns:
        Daily nutrition summary
    """
    summary = NutritionService.get_daily_summary(db, user_id, nutrition_date)
    if not summary:
        # Return empty summary if none exists
        summary = NutritionService.update_daily_summary(db, user_id, nutrition_date)
    
    return summary


@router.get("/weekly", response_model=list[DailyNutritionSummaryResponse])
def get_weekly_nutrition(
    end_date: date = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get weekly nutrition summary (last 7 days).
    
    Args:
        end_date: End date (default: today)
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of daily nutrition summaries
    """
    from datetime import timedelta
    
    if not end_date:
        end_date = date.today()
    
    start_date = end_date - timedelta(days=6)
    
    summaries = NutritionService.get_date_range_summaries(
        db, user_id, start_date, end_date
    )
    return summaries


@router.get("/range", response_model=list[DailyNutritionSummaryResponse])
def get_nutrition_range(
    start_date: date,
    end_date: date,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get nutrition summaries for a custom date range.
    
    Args:
        start_date: Start date
        end_date: End date
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of daily nutrition summaries
    """
    summaries = NutritionService.get_date_range_summaries(
        db, user_id, start_date, end_date
    )
    return summaries
