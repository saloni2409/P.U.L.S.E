"""Authentication routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas import TokenRequest, TokenResponse, UserCreate, UserResponse
from app.services import UserService

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user response
    """
    try:
        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(credentials: TokenRequest, db: Session = Depends(get_db)):
    """
    Login user and get access token.
    
    Args:
        credentials: Username and password
        db: Database session
        
    Returns:
        Access token response
    """
    user = UserService.authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
