"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, time


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    dietary_preferences: Optional[dict] = None
    daily_calorie_goal: Optional[int] = 2000


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[EmailStr] = None
    dietary_preferences: Optional[dict] = None
    daily_calorie_goal: Optional[int] = None


class UserResponse(UserBase):
    """User response schema"""
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class TokenRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"


# Macro Targets Schemas
class MacroTargetsBase(BaseModel):
    """Base macro targets schema"""
    daily_calorie_goal: int = 2000
    protein_percent: float = 30.0
    carbs_percent: float = 40.0
    fat_percent: float = 30.0


class MacroTargetsUpdate(MacroTargetsBase):
    """Schema for updating macro targets"""
    pass


class MacroTargetsResponse(MacroTargetsBase):
    """Macro targets response schema"""
    target_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Macronutrients Schemas
class MacronutrientsBase(BaseModel):
    """Base macronutrients schema"""
    protein_grams: float = 0.0
    carbs_grams: float = 0.0
    fat_grams: float = 0.0
    fiber_grams: float = 0.0
    sugar_grams: float = 0.0
    sodium_mg: float = 0.0


class MacronutrientsResponse(MacronutrientsBase):
    """Macronutrients response schema"""
    macro_id: str
    item_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Meal Item Schemas
class MealItemBase(BaseModel):
    """Base meal item schema"""
    food_name: str
    quantity: float
    unit: str  # GRAMS, ML, CUPS, PIECES, OUNCES


class MealItemCreate(MealItemBase):
    """Schema for creating meal item"""
    calories: Optional[float] = None
    macronutrients: Optional[MacronutrientsBase] = None


class MealItemUpdate(BaseModel):
    """Schema for updating meal item"""
    food_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    calories: Optional[float] = None
    macronutrients: Optional[MacronutrientsBase] = None
    is_verified: Optional[bool] = None


class MealItemResponse(MealItemBase):
    """Meal item response schema"""
    item_id: str
    meal_id: str
    calories: Optional[float]
    is_verified: bool
    source: str
    confidence_score: float
    macronutrients: Optional[MacronutrientsResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Meal Entry Schemas
class MealEntryBase(BaseModel):
    """Base meal entry schema"""
    meal_type: str  # BREAKFAST, LUNCH, DINNER, SNACK
    meal_description: str
    meal_date: date
    meal_time: Optional[time] = None


class MealEntryCreate(MealEntryBase):
    """Schema for creating meal entry"""
    meal_items: Optional[List[MealItemCreate]] = None


class MealEntryUpdate(BaseModel):
    """Schema for updating meal entry"""
    meal_type: Optional[str] = None
    meal_description: Optional[str] = None
    meal_date: Optional[date] = None
    meal_time: Optional[time] = None


class MealEntryResponse(MealEntryBase):
    """Meal entry response schema"""
    meal_id: str
    user_id: str
    is_processed: bool
    meal_items: List[MealItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Daily Nutrition Summary Schemas
class DailyNutritionSummaryResponse(BaseModel):
    """Daily nutrition summary response schema"""
    summary_id: str
    user_id: str
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    meal_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Food Database Schemas
class FoodDatabaseBase(BaseModel):
    """Base food database schema"""
    food_name: str
    serving_size: float
    serving_unit: str
    calories_per_serving: Optional[float] = None
    category: Optional[str] = None


class FoodDatabaseCreate(FoodDatabaseBase):
    """Schema for creating food"""
    pass


class FoodDatabaseResponse(FoodDatabaseBase):
    """Food database response schema"""
    food_id: str
    verified_by_usda: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
