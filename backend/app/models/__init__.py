"""SQLAlchemy ORM models for P.U.L.S.E"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, Text, Date, Time, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """User entity for meal tracking"""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    dietary_preferences = Column(JSON, default={})
    daily_calorie_goal = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    macro_targets = relationship("MacroTargets", back_populates="user", cascade="all, delete-orphan")
    meal_entries = relationship("MealEntry", back_populates="user", cascade="all, delete-orphan")
    daily_summaries = relationship("DailyNutritionSummary", back_populates="user", cascade="all, delete-orphan")


class MacroTargets(Base):
    """User's macro and calorie targets"""
    __tablename__ = "macro_targets"
    
    target_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    daily_calorie_goal = Column(Integer, default=2000)
    protein_percent = Column(Float, default=30.0)
    carbs_percent = Column(Float, default=40.0)
    fat_percent = Column(Float, default=30.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="macro_targets")


class MealEntry(Base):
    """A meal logged by user"""
    __tablename__ = "meal_entries"
    
    meal_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    meal_type = Column(String, nullable=False)  # BREAKFAST, LUNCH, DINNER, SNACK
    meal_description = Column(Text, nullable=False)
    meal_date = Column(Date, nullable=False, index=True)
    meal_time = Column(Time, nullable=True)
    is_processed = Column(Boolean, default=False)
    original_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="meal_entries")
    meal_items = relationship("MealItem", back_populates="meal_entry", cascade="all, delete-orphan")


class MealItem(Base):
    """An individual food item in a meal"""
    __tablename__ = "meal_items"
    
    item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meal_id = Column(String, ForeignKey("meal_entries.meal_id"), nullable=False, index=True)
    food_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # GRAMS, ML, CUPS, PIECES, OUNCES
    calories = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    source = Column(String, default="USER_INPUT")  # USER_INPUT, AGENTIC_IDENTIFIED, MANUAL_CORRECTION
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meal_entry = relationship("MealEntry", back_populates="meal_items")
    macronutrients = relationship("Macronutrients", back_populates="meal_item", uselist=False, cascade="all, delete-orphan")


class Macronutrients(Base):
    """Nutritional breakdown for a meal item"""
    __tablename__ = "macronutrients"
    
    macro_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("meal_items.item_id"), nullable=False, unique=True)
    protein_grams = Column(Float, default=0.0)
    carbs_grams = Column(Float, default=0.0)
    fat_grams = Column(Float, default=0.0)
    fiber_grams = Column(Float, default=0.0)
    sugar_grams = Column(Float, default=0.0)
    sodium_mg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meal_item = relationship("MealItem", back_populates="macronutrients")


class FoodDatabase(Base):
    """Food database for reference"""
    __tablename__ = "food_database"
    
    food_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    food_name = Column(String, nullable=False, index=True)
    serving_size = Column(Float, nullable=False)
    serving_unit = Column(String, nullable=False)
    calories_per_serving = Column(Float, nullable=True)
    category = Column(String, nullable=True)  # FRUIT, VEGETABLE, PROTEIN, GRAIN, DAIRY, etc.
    verified_by_usda = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyNutritionSummary(Base):
    """Daily nutrition summary for a user"""
    __tablename__ = "daily_nutrition_summary"
    
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    total_calories = Column(Float, default=0.0)
    total_protein = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_fat = Column(Float, default=0.0)
    total_fiber = Column(Float, default=0.0)
    meal_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="daily_summaries")
    
    # Composite unique constraint on user_id and date
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='_user_date_uc'),
    )
