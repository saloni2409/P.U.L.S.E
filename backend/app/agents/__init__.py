"""
Agentic meal parsing system
Processes meal descriptions to extract food items, quantities, and macronutrients
"""

import json
from typing import Optional
from pydantic import BaseModel
from app.core.llm_service import LLMService


class FoodItemParsed(BaseModel):
    """Parsed food item from meal description"""
    food_name: str
    quantity: float
    unit: str
    estimated_calories: Optional[float] = None
    confidence_score: float  # 0.0-1.0


class MealParseResult(BaseModel):
    """Result of meal parsing"""
    items: list[FoodItemParsed]
    overall_confidence: float  # Average confidence score
    requires_verification: bool  # True if any item has low confidence


class MealParsingAgent:
    """Agent for parsing meal descriptions into structured data"""
    
    # Standard units
    VALID_UNITS = ["GRAMS", "ML", "CUPS", "PIECES", "OUNCES", "TABLESPOONS", "TEASPOONS"]
    
    # Prompt template for meal parsing
    PARSING_PROMPT = """
You are a nutrition expert AI assistant. Your task is to parse a meal description and extract:
1. Individual food items
2. Quantities and units
3. Estimated calorie content per serving

IMPORTANT: Respond ONLY with valid JSON, no other text.

Meal Description: "{meal_description}"

For each food item identified, provide:
- food_name: The name of the food item
- quantity: Numeric quantity
- unit: One of: GRAMS, ML, CUPS, PIECES, OUNCES, TABLESPOONS, TEASPOONS
- estimated_calories: Estimated calories for this quantity
- confidence_score: How confident you are (0.0-1.0) where 1.0 is very confident

Common approximations:
- 1 cup = 240 ml
- 1 tablespoon = 15 ml
- 1 ounce = 28 grams
- 1 piece (fruit) = varies, estimate ~100-150g

Respond with JSON array of items:
[
  {{
    "food_name": "string",
    "quantity": number,
    "unit": "string",
    "estimated_calories": number,
    "confidence_score": number
  }}
]

If confidence is low (<0.6) for any item, flag it for user verification.
"""

    @staticmethod
    async def parse_meal(meal_description: str) -> MealParseResult:
        """
        Parse a meal description using LLM.
        
        Args:
            meal_description: Raw text meal description
            
        Returns:
            Parsed meal result with items and confidence scores
        """
        try:
            # Generate prompt
            prompt = MealParsingAgent.PARSING_PROMPT.format(
                meal_description=meal_description
            )
            
            # Get LLM response
            response = await LLMService.generate(prompt, max_tokens=500)
            
            # Parse JSON response
            items_data = json.loads(response)
            
            # Validate and convert to FoodItemParsed objects
            items = []
            confidence_scores = []
            
            for item_data in items_data:
                # Validate unit
                unit = item_data.get("unit", "").upper()
                if unit not in MealParsingAgent.VALID_UNITS:
                    unit = "GRAMS"  # Default fallback
                
                item = FoodItemParsed(
                    food_name=item_data.get("food_name", "Unknown"),
                    quantity=float(item_data.get("quantity", 0)),
                    unit=unit,
                    estimated_calories=item_data.get("estimated_calories"),
                    confidence_score=float(item_data.get("confidence_score", 0.5))
                )
                items.append(item)
                confidence_scores.append(item.confidence_score)
            
            # Calculate overall confidence
            overall_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0.0
            )
            
            # Check if verification needed (any confidence < 0.6)
            requires_verification = any(s < 0.6 for s in confidence_scores)
            
            return MealParseResult(
                items=items,
                overall_confidence=overall_confidence,
                requires_verification=requires_verification
            )
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response: {str(e)}")
        except Exception as e:
            raise Exception(f"Meal parsing error: {str(e)}")
    
    @staticmethod
    async def enrich_with_nutrition(
        food_name: str,
        quantity: float,
        unit: str
    ) -> Optional[dict]:
        """
        Enrich food item with detailed macronutrient information.
        
        Args:
            food_name: Name of food
            quantity: Quantity consumed
            unit: Unit of measurement
            
        Returns:
            Dictionary with macronutrient breakdown or None
        """
        try:
            prompt = f"""
You are a nutrition database AI. Provide detailed macronutrient information for:
Food: {food_name}
Quantity: {quantity} {unit}

Respond ONLY with valid JSON:
{{
  "protein_grams": number,
  "carbs_grams": number,
  "fat_grams": number,
  "fiber_grams": number,
  "sugar_grams": number,
  "sodium_mg": number
}}

If uncertain about exact values, provide reasonable estimates for a {quantity}{unit} serving.
"""
            
            response = await LLMService.generate(prompt, max_tokens=200)
            nutrition_data = json.loads(response)
            
            return {
                "protein_grams": float(nutrition_data.get("protein_grams", 0)),
                "carbs_grams": float(nutrition_data.get("carbs_grams", 0)),
                "fat_grams": float(nutrition_data.get("fat_grams", 0)),
                "fiber_grams": float(nutrition_data.get("fiber_grams", 0)),
                "sugar_grams": float(nutrition_data.get("sugar_grams", 0)),
                "sodium_mg": float(nutrition_data.get("sodium_mg", 0))
            }
        
        except Exception as e:
            # Fallback: return None if enrichment fails
            return None
