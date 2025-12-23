"""Service layer for all business logic"""

from sqlalchemy.orm import Session
from app.models import User
from app.core.security import get_password_hash, verify_password
from app.schemas import UserCreate, UserResponse


class UserService:
    """Service for user-related operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            dietary_preferences=user_data.dietary_preferences or {},
            daily_calorie_goal=user_data.daily_calorie_goal
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username to search for
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User | None:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID to search for
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        """
        Authenticate user with username and password.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserService.get_user_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
