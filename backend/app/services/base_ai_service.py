"""Abstract base class for AI providers"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AIChatMessage(BaseModel):
    """Standardized chat message model"""
    role: str  # 'user', 'assistant', 'system'
    content: str


class AIParsingItem(BaseModel):
    """Standardized parsed meal item"""
    food_name: str
    quantity: float
    unit: str
    estimated_calories: Optional[float] = None
    confidence: float = 1.0


class AIParsingResult(BaseModel):
    """Standardized meal parsing result"""
    meal_items: List[AIParsingItem]
    confidence: float


class AINutritionItem(BaseModel):
    """Standardized nutrition item result"""
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float


class AINutritionResult(BaseModel):
    """Standardized nutrition calculation result"""
    items: List[AINutritionItem]
    totals: Dict[str, float]


class BaseAIService(ABC):
    """
    Interface for all AI providers (Gemini, OpenAI, Claude, Local, etc.)
    Ensures consistent behavior across different models.
    """

    @abstractmethod
    async def chat_message(self, messages: List[AIChatMessage]) -> str:
        """
        Send a multi-turn conversation to the AI provider.
        
        Args:
            messages: List of standardized AIChatMessage objects
            
        Returns:
            The text response from the AI
        """
        ...

    @abstractmethod
    async def parse_meal_description(self, description: str) -> AIParsingResult:
        """
        Parse a natural language meal description into structured items.
        
        Args:
            description: Natural language text (e.g., "2 eggs and toast")
            
        Returns:
            AIParsingResult containing a list of items and confidence
        """
        ...

    @abstractmethod
    async def get_nutrition_estimate(self, food_items: List[Dict[str, Any]]) -> AINutritionResult:
        """
        Calculate estimated macronutrients for a list of food items.
        
        Args:
            food_items: List of dictionaries with food_name, quantity, and unit
            
        Returns:
            AINutritionResult containing per-item macros and totals
        """
        ...
