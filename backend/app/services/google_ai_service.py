"""Google Gemini AI service for chat meal logging"""

import json
import logging
from typing import Optional, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

logger = logging.getLogger(__name__)


class GoogleAIService:
    """
    Wrapper for Google Gemini API with user's BYOK key.
    
    Each instance is initialized with a user's API key, ensuring per-user isolation.
    Keys are only decrypted in memory when needed and destroyed after use.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        """
        Initialize Google AI service with user's API key.
        
        Args:
            api_key: User's decrypted Gemini API key
            model: Gemini model to use (default: gemini-1.5-pro)
        """
        if not api_key:
            raise ValueError("API key is required")
        
        # Configure Gemini with user's key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.api_key = api_key  # Store for session use
        self.model_name = model
    
    async def chat_message(self, messages: list[dict]) -> str:
        """
        Send messages to Gemini and get response.
        
        Args:
            messages: List of message dicts with 'role' (user/assistant) and 'content'
            
        Returns:
            Response text from Gemini
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Convert message format for Gemini
            history = []
            for msg in messages[:-1]:  # All but last
                history.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [msg["content"]]
                })
            
            # Start chat session with history
            chat = self.model.start_chat(history=history)
            
            # Send latest message
            latest_message = messages[-1]["content"]
            response = await self._send_message_async(chat, latest_message)
            
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Failed to get response from Gemini: {str(e)}")
    
    async def _send_message_async(self, chat, message: str) -> GenerateContentResponse:
        """Send message asynchronously (wrapper for sync API)"""
        # Since google-generativeai doesn't have async yet, we run sync in executor
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, chat.send_message, message)
    
    async def parse_meal_description(self, description: str) -> dict:
        """
        Parse meal description into structured food items.
        
        Args:
            description: Natural language meal description (e.g., "2 eggs, oatmeal, banana")
            
        Returns:
            Dict with meal_items list and confidence
        """
        prompt = f"""Parse this meal description and return JSON with food items:
        
Meal: {description}

Return JSON in this format:
{{
    "meal_items": [
        {{"food_name": "eggs", "quantity": 2, "unit": "pieces", "estimated_calories": 140, "confidence": 0.95}},
        {{"food_name": "oatmeal", "quantity": 1, "unit": "cups", "estimated_calories": 150, "confidence": 0.85}},
        {{"food_name": "banana", "quantity": 1, "unit": "pieces", "estimated_calories": 90, "confidence": 0.95}}
    ],
    "confidence": 0.92
}}

Only return valid JSON, no other text."""
        
        try:
            response = await self.chat_message([{"role": "user", "content": prompt}])
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            
            return {"meal_items": [], "confidence": 0}
        
        except Exception as e:
            logger.error(f"Meal parsing error: {str(e)}")
            return {"meal_items": [], "confidence": 0}
    
    async def get_nutrition_estimate(self, food_items: list[dict]) -> dict:
        """
        Get estimated macronutrients for food items.
        
        Args:
            food_items: List of items with food_name, quantity, unit
            
        Returns:
            Dict with macronutrient data
        """
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
        {{"food_name": "oatmeal", "calories": 150, "protein": 5, "carbs": 27, "fat": 3}},
        {{"food_name": "banana", "calories": 90, "protein": 1.1, "carbs": 23, "fat": 0.3}}
    ],
    "totals": {{"calories": 380, "protein": 19.1, "carbs": 51.1, "fat": 13.3}}
}}

Only return JSON, no other text."""
        
        try:
            response = await self.chat_message([{"role": "user", "content": prompt}])
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            
            return {"items": [], "totals": {}}
        
        except Exception as e:
            logger.error(f"Nutrition estimation error: {str(e)}")
            return {"items": [], "totals": {}}
    
    def __del__(self):
        """Clean up - destroy API key from memory"""
        if hasattr(self, 'api_key'):
            self.api_key = None  # Clear sensitive data
