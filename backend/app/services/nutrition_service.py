"""Service layer for nutrition tracking and food database"""

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    DailyNutritionSummary, MealEntry, FoodDatabase
)
from app.schemas import FoodDatabaseCreate


class NutritionService:
    """Service for nutrition-related operations"""
    
    @staticmethod
    def get_daily_summary(db: Session, user_id: str, summary_date: date) -> DailyNutritionSummary | None:
        """
        Get daily nutrition summary for a user.
        
        Args:
            db: Database session
            user_id: User ID
            summary_date: Date for summary
            
        Returns:
            Daily nutrition summary or None
        """
        return db.query(DailyNutritionSummary).filter(
            and_(
                DailyNutritionSummary.user_id == user_id,
                DailyNutritionSummary.date == summary_date
            )
        ).first()
    
    @staticmethod
    def update_daily_summary(db: Session, user_id: str, summary_date: date) -> DailyNutritionSummary:
        """
        Create or update daily nutrition summary by aggregating meal data.
        
        Args:
            db: Database session
            user_id: User ID
            summary_date: Date for summary
            
        Returns:
            Updated daily nutrition summary
        """
        # Get or create summary
        summary = NutritionService.get_daily_summary(db, user_id, summary_date)
        
        if not summary:
            summary = DailyNutritionSummary(
                user_id=user_id,
                date=summary_date,
                total_calories=0.0,
                total_protein=0.0,
                total_carbs=0.0,
                total_fat=0.0,
                total_fiber=0.0,
                meal_count=0
            )
            db.add(summary)
        
        # Get all meals for the date
        meals = db.query(MealEntry).filter(
            and_(
                MealEntry.user_id == user_id,
                MealEntry.meal_date == summary_date
            )
        ).all()
        
        # Reset totals
        summary.total_calories = 0.0
        summary.total_protein = 0.0
        summary.total_carbs = 0.0
        summary.total_fat = 0.0
        summary.total_fiber = 0.0
        summary.meal_count = len(meals)
        
        # Aggregate from meal items
        for meal in meals:
            for item in meal.meal_items:
                if item.calories:
                    summary.total_calories += item.calories
                
                if item.macronutrients:
                    summary.total_protein += item.macronutrients.protein_grams
                    summary.total_carbs += item.macronutrients.carbs_grams
                    summary.total_fat += item.macronutrients.fat_grams
                    summary.total_fiber += item.macronutrients.fiber_grams
        
        db.commit()
        db.refresh(summary)
        return summary
    
    @staticmethod
    def get_date_range_summaries(db: Session, user_id: str, start_date: date, end_date: date) -> list[DailyNutritionSummary]:
        """
        Get nutrition summaries for a date range.
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily summaries
        """
        return db.query(DailyNutritionSummary).filter(
            and_(
                DailyNutritionSummary.user_id == user_id,
                DailyNutritionSummary.date >= start_date,
                DailyNutritionSummary.date <= end_date
            )
        ).order_by(DailyNutritionSummary.date.desc()).all()


class FoodService:
    """Service for food database operations"""
    
    @staticmethod
    def create_food(db: Session, food_data: FoodDatabaseCreate) -> FoodDatabase:
        """
        Create a new food entry.
        
        Args:
            db: Database session
            food_data: Food creation data
            
        Returns:
            Created food entry
        """
        # Check if food already exists with same serving size
        existing = db.query(FoodDatabase).filter(
            and_(
                FoodDatabase.food_name == food_data.food_name,
                FoodDatabase.serving_size == food_data.serving_size,
                FoodDatabase.serving_unit == food_data.serving_unit
            )
        ).first()
        
        if existing:
            return existing
        
        food = FoodDatabase(
            food_name=food_data.food_name,
            serving_size=food_data.serving_size,
            serving_unit=food_data.serving_unit,
            calories_per_serving=food_data.calories_per_serving,
            category=food_data.category,
            verified_by_usda=False
        )
        
        db.add(food)
        db.commit()
        db.refresh(food)
        return food
    
    @staticmethod
    def search_food(db: Session, query: str, limit: int = 10) -> list[FoodDatabase]:
        """
        Search food database by name.
        
        Args:
            db: Database session
            query: Search query
            limit: Result limit
            
        Returns:
            List of matching foods
        """
        return db.query(FoodDatabase).filter(
            FoodDatabase.food_name.ilike(f"%{query}%")
        ).limit(limit).all()
    
    @staticmethod
    def get_food_by_id(db: Session, food_id: str) -> FoodDatabase | None:
        """
        Get food by ID.
        
        Args:
            db: Database session
            food_id: Food ID
            
        Returns:
            Food entry or None
        """
        return db.query(FoodDatabase).filter(FoodDatabase.food_id == food_id).first()
    
    @staticmethod
    def get_foods_by_category(db: Session, category: str, limit: int = 20) -> list[FoodDatabase]:
        """
        Get foods by category.
        
        Args:
            db: Database session
            category: Food category
            limit: Result limit
            
        Returns:
            List of foods in category
        """
        return db.query(FoodDatabase).filter(
            FoodDatabase.category == category
        ).limit(limit).all()
    
    @staticmethod
    def get_all_foods(db: Session, limit: int = 100, offset: int = 0) -> list[FoodDatabase]:
        """
        Get all foods in database.
        
        Args:
            db: Database session
            limit: Result limit
            offset: Result offset
            
        Returns:
            List of foods
        """
        return db.query(FoodDatabase).limit(limit).offset(offset).all()
