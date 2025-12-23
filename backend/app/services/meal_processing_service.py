"""
Meal processing service that integrates agentic parsing
"""

from sqlalchemy.orm import Session
from datetime import date
from app.models import MealEntry
from app.services.meal_service import MealService
from app.services.validation_service import MealValidationService
from app.services.nutrition_service import NutritionService
from app.schemas import MealItemCreate, MacronutrientsBase


class MealProcessingService:
    """Service for processing meals with agentic parsing"""
    
    @staticmethod
    async def process_meal_with_agent(
        db: Session,
        user_id: str,
        meal_description: str,
        meal_type: str,
        meal_date: date,
        meal_time = None,
        auto_enrich: bool = True
    ) -> MealEntry:
        """
        Process a meal description using agentic parsing.
        
        Args:
            db: Database session
            user_id: User ID
            meal_description: Raw meal text
            meal_type: Type of meal (BREAKFAST, LUNCH, etc.)
            meal_date: Date of meal
            meal_time: Time of meal (optional)
            auto_enrich: Whether to fetch detailed nutrition data
            
        Returns:
            Created meal entry with parsed items
        """
        try:
            # Parse and enrich meal using agent
            parse_result, enriched_items = await MealValidationService.parse_and_enrich_meal(
                meal_description,
                db,
                enrich_nutrition=auto_enrich
            )
            
            # Create meal entry
            from app.schemas import MealEntryCreate
            meal_data = MealEntryCreate(
                meal_type=meal_type,
                meal_description=meal_description,
                meal_date=meal_date,
                meal_time=meal_time,
                meal_items=[]
            )
            
            meal = MealEntry(
                user_id=user_id,
                meal_type=meal_data.meal_type,
                meal_description=meal_data.meal_description,
                meal_date=meal_data.meal_date,
                meal_time=meal_data.meal_time,
                original_log=meal_description,
                is_processed=True  # Mark as processed by agent
            )
            
            db.add(meal)
            db.flush()  # Get meal_id
            
            # Add enriched items to meal
            for enriched_item in enriched_items:
                # Validate item
                is_valid, errors = MealValidationService.validate_meal_item(
                    enriched_item["food_name"],
                    enriched_item["quantity"],
                    enriched_item["estimated_calories"],
                    enriched_item["confidence_score"]
                )
                
                # Create meal item (add even if validation errors, flag for review)
                item = MealItem(
                    meal_id=meal.meal_id,
                    food_name=enriched_item["food_name"],
                    quantity=enriched_item["quantity"],
                    unit=enriched_item["unit"],
                    calories=enriched_item["estimated_calories"],
                    source=enriched_item["source"],
                    confidence_score=enriched_item["confidence_score"],
                    is_verified=is_valid  # Mark verified if no errors
                )
                
                db.add(item)
                db.flush()
                
                # Add macronutrients if available
                if enriched_item["macronutrients"]:
                    macros = Macronutrients(
                        item_id=item.item_id,
                        protein_grams=enriched_item["macronutrients"].get("protein_grams", 0),
                        carbs_grams=enriched_item["macronutrients"].get("carbs_grams", 0),
                        fat_grams=enriched_item["macronutrients"].get("fat_grams", 0),
                        fiber_grams=enriched_item["macronutrients"].get("fiber_grams", 0),
                        sugar_grams=enriched_item["macronutrients"].get("sugar_grams", 0),
                        sodium_mg=enriched_item["macronutrients"].get("sodium_mg", 0)
                    )
                    db.add(macros)
            
            db.commit()
            db.refresh(meal)
            
            # Update daily summary
            NutritionService.update_daily_summary(db, user_id, meal_date)
            
            return meal
        
        except Exception as e:
            db.rollback()
            raise Exception(f"Meal processing failed: {str(e)}")
    
    @staticmethod
    async def process_meal_manual(
        db: Session,
        user_id: str,
        meal_description: str,
        meal_type: str,
        meal_date: date,
        meal_items: list[dict],
        meal_time = None
    ) -> MealEntry:
        """
        Process a meal with manually provided items.
        
        Args:
            db: Database session
            user_id: User ID
            meal_description: Meal description
            meal_type: Type of meal
            meal_date: Date of meal
            meal_items: List of manually provided items
            meal_time: Time of meal (optional)
            
        Returns:
            Created meal entry
        """
        try:
            # Create meal entry
            meal = MealEntry(
                user_id=user_id,
                meal_type=meal_type,
                meal_description=meal_description,
                meal_date=meal_date,
                meal_time=meal_time,
                original_log=meal_description,
                is_processed=False  # Manual entry
            )
            
            db.add(meal)
            db.flush()
            
            # Add items
            for item_data in meal_items:
                item = MealItem(
                    meal_id=meal.meal_id,
                    food_name=item_data.get("food_name"),
                    quantity=item_data.get("quantity"),
                    unit=item_data.get("unit"),
                    calories=item_data.get("calories"),
                    source="USER_INPUT",
                    confidence_score=1.0,
                    is_verified=True  # Manual entries are pre-verified
                )
                
                db.add(item)
                db.flush()
                
                # Add macros if provided
                if "macronutrients" in item_data:
                    macros = Macronutrients(
                        item_id=item.item_id,
                        protein_grams=item_data["macronutrients"].get("protein_grams", 0),
                        carbs_grams=item_data["macronutrients"].get("carbs_grams", 0),
                        fat_grams=item_data["macronutrients"].get("fat_grams", 0),
                        fiber_grams=item_data["macronutrients"].get("fiber_grams", 0),
                        sugar_grams=item_data["macronutrients"].get("sugar_grams", 0),
                        sodium_mg=item_data["macronutrients"].get("sodium_mg", 0)
                    )
                    db.add(macros)
            
            db.commit()
            db.refresh(meal)
            
            # Update daily summary
            NutritionService.update_daily_summary(db, user_id, meal_date)
            
            return meal
        
        except Exception as e:
            db.rollback()
            raise Exception(f"Manual meal processing failed: {str(e)}")
