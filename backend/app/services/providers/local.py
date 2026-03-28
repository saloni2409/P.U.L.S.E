"""Local AI provider implementation for P.U.L.S.E (e.g., Ollama)"""

import json
import logging
import re
import httpx
from typing import List, Dict, Any, Optional

from app.services.base_ai_service import (
    BaseAIService, 
    AIChatMessage, 
    AIParsingResult, 
    AIParsingItem, 
    AINutritionResult, 
    AINutritionItem
)

logger = logging.getLogger(__name__)


class LocalProvider(BaseAIService):
    """
    Implementation of a local AI provider (compatible with Ollama by default).
    Inherits from BaseAIService to ensure abstraction.
    """
    
    def __init__(self, base_url: str, model: str = "llama3"):
        """
        Initialize Local provider.
        
        Args:
            base_url: The URL of the local AI server (e.g., http://localhost:11434)
            model: Model name identifier
        """
        self.base_url = base_url.rstrip("/")
        self.model_name = model
    
    async def chat_message(self, messages: List[AIChatMessage]) -> str:
        """Standardized multi-turn chat interaction for Ollama"""
        try:
            # Prepare Ollama chat request format
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": msg.role, "content": msg.content} 
                    for msg in messages
                ],
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract response text
                return data.get("message", {}).get("content", "")
                
        except Exception as e:
            logger.error(f"LocalProvider chat error: {str(e)}")
            raise Exception(f"Failed to get response from local AI: {str(e)}")
            
    async def parse_meal_description(self, description: str) -> AIParsingResult:
        """Extract food items from text using local AI"""
        prompt = f"""Parse this meal description and return JSON with food items:
        
Meal: {description}

Return JSON in this format:
{{
    "meal_items": [
        {{"food_name": "eggs", "quantity": 2, "unit": "pieces", "estimated_calories": 140, "confidence": 0.95}}
    ],
    "confidence": 0.92
}}

Only return valid JSON, no other text."""
        
        try:
            messages = [AIChatMessage(role="user", content=prompt)]
            response = await self.chat_message(messages)
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                items = [AIParsingItem(**item) for item in data.get("meal_items", [])]
                return AIParsingResult(meal_items=items, confidence=data.get("confidence", 0))
            
            return AIParsingResult(meal_items=[], confidence=0)
            
        except Exception as e:
            logger.error(f"LocalProvider meal parsing error: {str(e)}")
            return AIParsingResult(meal_items=[], confidence=0)

    async def get_nutrition_estimate(self, food_items: List[Dict[str, Any]]) -> AINutritionResult:
        """Calculate estimated macronutrients for items using local AI"""
        items_str = "\n".join([
            f"- {item['quantity']} {item['unit']} of {item['food_name']}"
            for item in food_items
        ])
        
        prompt = f"""Calculate estimated macronutrients for these foods:

{items_str}

Return JSON:
{{
    "items": [
        {{"food_name": "eggs", "calories": 140, "protein": 13, "carbs": 1.1, "fat": 10}}
    ],
    "totals": {{"calories": 380, "protein": 18, "carbs": 28.1, "fat": 13}}
}}

Only return JSON, no other text."""
        
        try:
            messages = [AIChatMessage(role="user", content=prompt)]
            response = await self.chat_message(messages)
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                items = [AINutritionItem(**item) for item in data.get("items", [])]
                return AINutritionResult(items=items, totals=data.get("totals", {}))
                
            return AINutritionResult(items=[], totals={})
            
        except Exception as e:
            logger.error(f"LocalProvider nutrition estimation error: {str(e)}")
            return AINutritionResult(items=[], totals={})
