"""Service layer for meal operations"""

import uuid
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    MealEntry, MealItem, Macronutrients, 
    FoodDatabase, DailyNutritionSummary, User
)
from app.schemas import (
    MealEntryCreate, MealEntryUpdate, MealItemCreate, 
    MealItemUpdate, MealEntryResponse
)


class MealService:
    """Service for meal-related operations"""
    
    @staticmethod
    def create_meal_entry(db: Session, user_id: str, meal_data: MealEntryCreate) -> MealEntry:
        """
        Create a new meal entry.
        
        Args:
            db: Database session
            user_id: User ID creating the meal
            meal_data: Meal creation data
            
        Returns:
            Created meal entry
        """
        meal = MealEntry(
            user_id=user_id,
            meal_type=meal_data.meal_type,
            meal_description=meal_data.meal_description,
            meal_date=meal_data.meal_date,
            meal_time=meal_data.meal_time,
            original_log=meal_data.meal_description,
            is_processed=False
        )
        
        db.add(meal)
        db.flush()  # Get meal_id before adding items
        
        # Add meal items if provided
        if meal_data.meal_items:
            for item_data in meal_data.meal_items:
                MealService.add_meal_item(db, meal.meal_id, item_data)
        
        db.commit()
        db.refresh(meal)
        return meal
    
    @staticmethod
    def get_meal_by_id(db: Session, meal_id: str, user_id: str) -> MealEntry | None:
        """
        Get meal by ID (user-specific).
        
        Args:
            db: Database session
            meal_id: Meal ID
            user_id: User ID (for ownership verification)
            
        Returns:
            Meal entry or None
        """
        return db.query(MealEntry).filter(
            and_(MealEntry.meal_id == meal_id, MealEntry.user_id == user_id)
        ).first()
    
    @staticmethod
    def get_user_meals(db: Session, user_id: str, limit: int = 100, offset: int = 0) -> list[MealEntry]:
        """
        Get all meals for a user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Result limit
            offset: Result offset
            
        Returns:
            List of meal entries
        """
        return db.query(MealEntry).filter(
            MealEntry.user_id == user_id
        ).order_by(MealEntry.meal_date.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_user_meals_by_date(db: Session, user_id: str, meal_date: date) -> list[MealEntry]:
        """
        Get all meals for a user on a specific date.
        
        Args:
            db: Database session
            user_id: User ID
            meal_date: Date to filter by
            
        Returns:
            List of meal entries
        """
        return db.query(MealEntry).filter(
            and_(MealEntry.user_id == user_id, MealEntry.meal_date == meal_date)
        ).order_by(MealEntry.meal_time).all()
    
    @staticmethod
    def update_meal_entry(db: Session, meal_id: str, user_id: str, meal_data: MealEntryUpdate) -> MealEntry | None:
        """
        Update a meal entry.
        
        Args:
            db: Database session
            meal_id: Meal ID
            user_id: User ID
            meal_data: Update data
            
        Returns:
            Updated meal or None
        """
        meal = MealService.get_meal_by_id(db, meal_id, user_id)
        if not meal:
            return None
        
        if meal_data.meal_type:
            meal.meal_type = meal_data.meal_type
        if meal_data.meal_description:
            meal.meal_description = meal_data.meal_description
        if meal_data.meal_date:
            meal.meal_date = meal_data.meal_date
        if meal_data.meal_time:
            meal.meal_time = meal_data.meal_time
        
        db.commit()
        db.refresh(meal)
        return meal
    
    @staticmethod
    def delete_meal_entry(db: Session, meal_id: str, user_id: str) -> bool:
        """
        Delete a meal entry.
        
        Args:
            db: Database session
            meal_id: Meal ID
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        meal = MealService.get_meal_by_id(db, meal_id, user_id)
        if not meal:
            return False
        
        db.delete(meal)
        db.commit()
        return True
    
    @staticmethod
    def add_meal_item(db: Session, meal_id: str, item_data: MealItemCreate) -> MealItem:
        """
        Add an item to a meal.
        
        Args:
            db: Database session
            meal_id: Meal ID
            item_data: Item creation data
            
        Returns:
            Created meal item
        """
        item = MealItem(
            meal_id=meal_id,
            food_name=item_data.food_name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            calories=item_data.calories or 0.0
        )
        
        db.add(item)
        db.flush()  # Get item_id
        
        # Add macronutrients if provided
        if item_data.macronutrients:
            macro = Macronutrients(
                item_id=item.item_id,
                protein_grams=item_data.macronutrients.protein_grams,
                carbs_grams=item_data.macronutrients.carbs_grams,
                fat_grams=item_data.macronutrients.fat_grams,
                fiber_grams=item_data.macronutrients.fiber_grams,
                sugar_grams=item_data.macronutrients.sugar_grams,
                sodium_mg=item_data.macronutrients.sodium_mg
            )
            db.add(macro)
        
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def update_meal_item(db: Session, item_id: str, item_data: MealItemUpdate) -> MealItem | None:
        """
        Update a meal item.
        
        Args:
            db: Database session
            item_id: Item ID
            item_data: Update data
            
        Returns:
            Updated item or None
        """
        item = db.query(MealItem).filter(MealItem.item_id == item_id).first()
        if not item:
            return None
        
        if item_data.food_name:
            item.food_name = item_data.food_name
        if item_data.quantity:
            item.quantity = item_data.quantity
        if item_data.unit:
            item.unit = item_data.unit
        if item_data.calories is not None:
            item.calories = item_data.calories
        if item_data.is_verified is not None:
            item.is_verified = item_data.is_verified
        
        # Update macronutrients if provided
        if item_data.macronutrients:
            if item.macronutrients:
                macro = item.macronutrients
            else:
                macro = Macronutrients(item_id=item_id)
                db.add(macro)
            
            macro.protein_grams = item_data.macronutrients.protein_grams
            macro.carbs_grams = item_data.macronutrients.carbs_grams
            macro.fat_grams = item_data.macronutrients.fat_grams
            macro.fiber_grams = item_data.macronutrients.fiber_grams
            macro.sugar_grams = item_data.macronutrients.sugar_grams
            macro.sodium_mg = item_data.macronutrients.sodium_mg
        
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def delete_meal_item(db: Session, item_id: str) -> bool:
        """
        Delete a meal item.
        
        Args:
            db: Database session
            item_id: Item ID
            
        Returns:
            True if deleted, False if not found
        """
        item = db.query(MealItem).filter(MealItem.item_id == item_id).first()
        if not item:
            return False
        
        db.delete(item)
        db.commit()
        return True
    
    @staticmethod
    def get_meal_items(db: Session, meal_id: str) -> list[MealItem]:
        """
        Get all items in a meal.
        
        Args:
            db: Database session
            meal_id: Meal ID
            
        Returns:
            List of meal items
        """
        return db.query(MealItem).filter(MealItem.meal_id == meal_id).all()
