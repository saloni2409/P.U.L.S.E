"""Meal management API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.core.security import decode_token
from app.schemas import (
    MealEntryCreate, MealEntryUpdate, MealEntryResponse,
    MealItemCreate, MealItemUpdate, MealItemResponse
)
from app.services.meal_service import MealService
from app.services.nutrition_service import NutritionService
from fastapi import Header

router = APIRouter(prefix="/api/meals", tags=["meals"])


def get_current_user_id(authorization: str = Header(None)) -> str:
    """
    Extract user ID from JWT token.
    
    Args:
        authorization: Authorization header
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return payload["sub"]


@router.post("/log", response_model=MealEntryResponse)
def log_meal(
    meal_data: MealEntryCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Log a new meal entry.
    
    Args:
        meal_data: Meal creation data
        user_id: Current user ID
        db: Database session
        
    Returns:
        Created meal entry
    """
    meal = MealService.create_meal_entry(db, user_id, meal_data)
    
    # Update daily nutrition summary
    NutritionService.update_daily_summary(db, user_id, meal.meal_date)
    
    return meal


@router.get("/all", response_model=list[MealEntryResponse])
def get_all_meals(
    limit: int = 100,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all meals for current user.
    
    Args:
        limit: Result limit
        offset: Result offset
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of meal entries
    """
    meals = MealService.get_user_meals(db, user_id, limit, offset)
    return meals


@router.get("/date/{meal_date}", response_model=list[MealEntryResponse])
def get_meals_by_date(
    meal_date: date,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all meals for current user on a specific date.
    
    Args:
        meal_date: Date to filter by
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of meal entries
    """
    meals = MealService.get_user_meals_by_date(db, user_id, meal_date)
    return meals


@router.get("/{meal_id}", response_model=MealEntryResponse)
def get_meal(
    meal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific meal entry.
    
    Args:
        meal_id: Meal ID
        user_id: Current user ID
        db: Database session
        
    Returns:
        Meal entry
    """
    meal = MealService.get_meal_by_id(db, meal_id, user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    return meal


@router.put("/{meal_id}", response_model=MealEntryResponse)
def update_meal(
    meal_id: str,
    meal_data: MealEntryUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a meal entry.
    
    Args:
        meal_id: Meal ID
        meal_data: Update data
        user_id: Current user ID
        db: Database session
        
    Returns:
        Updated meal entry
    """
    meal = MealService.update_meal_entry(db, meal_id, user_id, meal_data)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Update daily nutrition summary
    NutritionService.update_daily_summary(db, user_id, meal.meal_date)
    
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a meal entry.
    
    Args:
        meal_id: Meal ID
        user_id: Current user ID
        db: Database session
    """
    # Get meal first to know the date for updating summary
    meal = MealService.get_meal_by_id(db, meal_id, user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    meal_date = meal.meal_date
    MealService.delete_meal_entry(db, meal_id, user_id)
    
    # Update daily nutrition summary
    NutritionService.update_daily_summary(db, user_id, meal_date)


# Meal Item endpoints
@router.get("/{meal_id}/items", response_model=list[MealItemResponse])
def get_meal_items(
    meal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all items in a meal.
    
    Args:
        meal_id: Meal ID
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of meal items
    """
    # Verify meal ownership
    meal = MealService.get_meal_by_id(db, meal_id, user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    return MealService.get_meal_items(db, meal_id)


@router.post("/{meal_id}/items", response_model=MealItemResponse)
def add_meal_item(
    meal_id: str,
    item_data: MealItemCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Add an item to a meal.
    
    Args:
        meal_id: Meal ID
        item_data: Item creation data
        user_id: Current user ID
        db: Database session
        
    Returns:
        Created meal item
    """
    # Verify meal ownership
    meal = MealService.get_meal_by_id(db, meal_id, user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    item = MealService.add_meal_item(db, meal_id, item_data)
    
    # Update daily nutrition summary
    NutritionService.update_daily_summary(db, user_id, meal.meal_date)
    
    return item


@router.put("/{meal_id}/items/{item_id}", response_model=MealItemResponse)
def update_meal_item(
    meal_id: str,
    item_id: str,
    item_data: MealItemUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a meal item.
    
    Args:
        meal_id: Meal ID
        item_id: Item ID
        item_data: Update data
        user_id: Current user ID
        db: Database session
        
    Returns:
        Updated meal item
    """
    # Verify meal ownership
    meal = MealService.get_meal_by_id(db, meal_id, user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    item = MealService.update_meal_item(db, item_id, item_data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update daily nutrition summary
    NutritionService.update_daily_summary(db, user_id, meal.meal_date)
    
    return item


@router.delete("/{meal_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_item(
    meal_id: str,
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a meal item.
    
    Args:
        meal_id: Meal ID
        item_id: Item ID
        user_id: Current user ID
        db: Database session
    """
    # Verify meal ownership
    meal = MealService.get_meal_by_id(db, meal_id, user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    if not MealService.delete_meal_item(db, item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update daily nutrition summary
    NutritionService.update_daily_summary(db, user_id, meal.meal_date)
