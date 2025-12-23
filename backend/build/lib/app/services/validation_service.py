"""
Meal validation and data enrichment service
Handles confidence scoring and data verification
"""

from datetime import date
from sqlalchemy.orm import Session
from app.models import MealItem, Macronutrients, FoodDatabase
from app.agents import MealParsingAgent, MealParseResult
from app.schemas import MacronutrientsBase


class MealValidationService:
    """Service for meal validation and enrichment"""
    
    # Reasonable calorie ranges for validation
    MIN_FOOD_CALORIES = 0
    MAX_FOOD_CALORIES = 2000  # Per serving
    
    @staticmethod
    async def parse_and_enrich_meal(
        meal_description: str,
        db: Session,
        enrich_nutrition: bool = True
    ) -> tuple[MealParseResult, list[dict]]:
        """
        Parse meal description and enrich with nutrition data.
        
        Args:
            meal_description: Raw meal text
            db: Database session
            enrich_nutrition: Whether to fetch detailed macros
            
        Returns:
            Tuple of (parse result, enriched items)
        """
        # Step 1: Parse meal using agent
        parse_result = await MealParsingAgent.parse_meal(meal_description)
        
        enriched_items = []
        
        # Step 2: Enrich each item
        for item in parse_result.items:
            enriched_item = {
                "food_name": item.food_name,
                "quantity": item.quantity,
                "unit": item.unit,
                "estimated_calories": item.estimated_calories,
                "confidence_score": item.confidence_score,
                "macronutrients": None,
                "source": "AGENTIC_IDENTIFIED"
            }
            
            # Try to get nutrition if requested
            if enrich_nutrition:
                macros = await MealParsingAgent.enrich_with_nutrition(
                    item.food_name,
                    item.quantity,
                    item.unit
                )
                if macros:
                    enriched_item["macronutrients"] = macros
            
            # Try to find in food database for better accuracy
            db_food = MealValidationService._find_similar_food(
                db, item.food_name
            )
            if db_food and db_food.calories_per_serving:
                enriched_item["source"] = "DATABASE_MATCHED"
                # Adjust calories based on database
                enriched_item["estimated_calories"] = db_food.calories_per_serving
                # Increase confidence if found in DB
                enriched_item["confidence_score"] = min(
                    1.0,
                    enriched_item["confidence_score"] + 0.2
                )
            
            enriched_items.append(enriched_item)
        
        return parse_result, enriched_items
    
    @staticmethod
    def _find_similar_food(db: Session, food_name: str) -> FoodDatabase | None:
        """
        Find similar food in database using fuzzy matching.
        
        Args:
            db: Database session
            food_name: Food name to search
            
        Returns:
            Best matching food or None
        """
        from sqlalchemy import func
        
        # Case-insensitive search
        words = food_name.lower().split()
        
        # Try to find exact match first
        for word in words:
            if len(word) > 3:  # Skip small words
                food = db.query(FoodDatabase).filter(
                    func.lower(FoodDatabase.food_name).contains(word)
                ).first()
                if food:
                    return food
        
        return None
    
    @staticmethod
    def validate_meal_item(
        food_name: str,
        quantity: float,
        estimated_calories: float | None,
        confidence_score: float
    ) -> tuple[bool, list[str]]:
        """
        Validate meal item data.
        
        Args:
            food_name: Food name
            quantity: Quantity
            estimated_calories: Calories
            confidence_score: Confidence (0.0-1.0)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate food name
        if not food_name or len(food_name.strip()) < 2:
            errors.append("Food name must be at least 2 characters")
        
        # Validate quantity
        if quantity <= 0:
            errors.append("Quantity must be greater than 0")
        
        if quantity > 10000:  # Sanity check
            errors.append("Quantity seems unreasonably large")
        
        # Validate calories if provided
        if estimated_calories is not None:
            if estimated_calories < MealValidationService.MIN_FOOD_CALORIES:
                errors.append("Calories cannot be negative")
            if estimated_calories > MealValidationService.MAX_FOOD_CALORIES:
                errors.append(
                    f"Calories exceed reasonable limit ({MealValidationService.MAX_FOOD_CALORIES})"
                )
        
        # Validate confidence
        if not (0.0 <= confidence_score <= 1.0):
            errors.append("Confidence score must be between 0.0 and 1.0")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def calculate_macro_calories(macros: MacronutrientsBase) -> float:
        """
        Calculate total calories from macronutrients.
        
        Args:
            macros: Macronutrient breakdown
            
        Returns:
            Calculated calories (protein*4 + carbs*4 + fat*9)
        """
        protein_cal = macros.protein_grams * 4
        carbs_cal = macros.carbs_grams * 4
        fat_cal = macros.fat_grams * 9
        
        return protein_cal + carbs_cal + fat_cal
    
    @staticmethod
    def validate_macro_total(
        calories: float,
        macros: MacronutrientsBase,
        tolerance_percent: float = 10
    ) -> bool:
        """
        Validate that macronutrients sum to approximately the calorie count.
        
        Args:
            calories: Total calories
            macros: Macronutrient breakdown
            tolerance_percent: Allowed variance percentage
            
        Returns:
            True if macros are consistent with calories
        """
        calculated_calories = MealValidationService.calculate_macro_calories(macros)
        
        # Calculate variance
        if calories > 0:
            variance = abs(calculated_calories - calories) / calories * 100
            return variance <= tolerance_percent
        
        return True  # Can't validate if no calories
