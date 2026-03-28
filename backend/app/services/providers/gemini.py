"""Google Gemini AI implementation for P.U.L.S.E"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from app.services.base_ai_service import (
    BaseAIService, 
    AIChatMessage, 
    AIParsingResult, 
    AIParsingItem, 
    AINutritionResult, 
    AINutritionItem
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIService):
    """
    Implementation of Gemini AI provider.
    Inherits from BaseAIService to ensure abstraction.
    """
    
    api_key: Optional[str]

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Decrypted User API Key
            model: Gemini model identifier
        """
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini with user's key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.api_key = api_key 
        self.model_name = model
    
    async def chat_message(self, messages: List[AIChatMessage]) -> str:
        """Standardized multi-turn chat interaction"""
        try:
            # Convert AIChatMessage objects to Gemini's history format
            history = []
            if len(messages) > 1:
                for msg in messages[:-1]:
                    history.append({
                        "role": "user" if msg.role == "user" else "model",
                        "parts": [msg.content]
                    })
            
            # Start chat session with history
            chat = self.model.start_chat(history=history)
            
            # Send latest message
            latest_message = messages[-1].content
            
            # Since google-generativeai is sync, we run in executor for non-blocking
            import asyncio
            loop = asyncio.get_event_loop()
            response: GenerateContentResponse = await loop.run_in_executor(None, chat.send_message, latest_message)
            
            return response.text
            
        except Exception as e:
            logger.error(f"GeminiProvider chat error: {str(e)}")
            raise Exception(f"Failed to get response from Gemini: {str(e)}")
            
    async def parse_meal_description(self, description: str) -> AIParsingResult:
        """Extract food items from text using Gemini"""
        prompt = f"""Parse this meal description and return JSON with food items:
        
Meal: {description}

Return JSON in this format:
{{
    "meal_items": [
        {{"food_name": "eggs", "quantity": 2, "unit": "pieces", "estimated_calories": 140, "confidence": 0.95}},
        {{"food_name": "oatmeal", "quantity": 1, "unit": "cups", "estimated_calories": 150, "confidence": 0.85}}
    ],
    "confidence": 0.92
}}

Only return valid JSON, no other text."""
        
        try:
            # Prepare standard message list
            messages = [AIChatMessage(role="user", content=prompt)]
            response = await self.chat_message(messages)
            
            # Extract and parse JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                
                # Convert list of dicts to list of AIParsingItem objects
                items = [AIParsingItem(**item) for item in data.get("meal_items", [])]
                return AIParsingResult(meal_items=items, confidence=data.get("confidence", 0))
            
            return AIParsingResult(meal_items=[], confidence=0)
            
        except Exception as e:
            logger.error(f"GeminiProvider meal parsing error: {str(e)}")
            return AIParsingResult(meal_items=[], confidence=0)

    async def get_nutrition_estimate(self, food_items: List[Dict[str, Any]]) -> AINutritionResult:
        """Calculate estimated macronutrients for items using Gemini"""
        items_str = "\n".join([
            f"- {item['quantity']} {item['unit']} of {item['food_name']}"
            for item in food_items
        ])
        
        prompt = f"""Calculate estimated macronutrients for these foods:

{items_str}

Return JSON:
{{
    "items": [
        {{"food_name": "eggs", "calories": 140, "protein": 13, "carbs": 1.1, "fat": 10}},
        {{"food_name": "oatmeal", "calories": 150, "protein": 5, "carbs": 27, "fat": 3}}
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
            logger.error(f"GeminiProvider nutrition estimation error: {str(e)}")
            return AINutritionResult(items=[], totals={})

    def __del__(self):
        """Clean up by wiping sensitive API key from memory"""
        if hasattr(self, 'api_key'):
            self.api_key = None
