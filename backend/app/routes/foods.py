"""Food database API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.schemas import FoodDatabaseCreate, FoodDatabaseResponse
from app.services.nutrition_service import FoodService
from fastapi import Header

router = APIRouter(prefix="/api/foods", tags=["foods"])


def get_current_user_id(authorization: str = Header(None)) -> str:
    """Extract user ID from JWT token."""
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


@router.get("/search", response_model=list[FoodDatabaseResponse])
def search_foods(
    q: str,
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Search food database by name.
    
    Args:
        q: Search query
        limit: Result limit
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of matching foods
    """
    if len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    foods = FoodService.search_food(db, q, limit)
    return foods


@router.get("/{food_id}", response_model=FoodDatabaseResponse)
def get_food(
    food_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific food by ID.
    
    Args:
        food_id: Food ID
        user_id: Current user ID
        db: Database session
        
    Returns:
        Food entry
    """
    food = FoodService.get_food_by_id(db, food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    return food


@router.get("/category/{category}", response_model=list[FoodDatabaseResponse])
def get_foods_by_category(
    category: str,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get foods by category.
    
    Args:
        category: Food category
        limit: Result limit
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of foods in category
    """
    foods = FoodService.get_foods_by_category(db, category, limit)
    return foods


@router.post("", response_model=FoodDatabaseResponse)
def create_food(
    food_data: FoodDatabaseCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new food entry (user-contributed).
    
    Args:
        food_data: Food creation data
        user_id: Current user ID
        db: Database session
        
    Returns:
        Created food entry
    """
    food = FoodService.create_food(db, food_data)
    return food


@router.get("", response_model=list[FoodDatabaseResponse])
def get_all_foods(
    limit: int = 100,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all foods in database.
    
    Args:
        limit: Result limit
        offset: Result offset
        user_id: Current user ID
        db: Database session
        
    Returns:
        List of foods
    """
    foods = FoodService.get_all_foods(db, limit, offset)
    return foods
