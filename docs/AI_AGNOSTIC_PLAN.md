# 🤖 AI Provider Agnostic Design Plan

This document outlines the architectural changes required to transform the P.U.L.S.E AI infrastructure from a Gemini-exclusive model into a modular, provider-agnostic system.

---

## 🏗️ 1. Core Architecture Changes

### A. The Abstract Interface (`BaseAIService`)
We will create a formal contract that all AI providers must follow.

```python
# backend/app/services/base_ai_service.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAIService(ABC):
    @abstractmethod
    async def chat_message(self, messages: List[Dict]) -> str:
        """Generic multi-turn chat interaction"""
        pass

    @abstractmethod
    async def parse_meal_description(self, description: str) -> Dict:
        """Extract food items from text"""
        pass

    @abstractmethod
    async def get_nutrition_estimate(self, food_items: List[Dict]) -> Dict:
        """Calculate macros/calories for items"""
        pass
```

### B. Standardized Data Models (Backend)
To ensure consistency across providers, we will use Pydantic models for request and response structures.

- **`AIChatMessage`**: (role, content)
- **`AIParsingResult`**: (meal_items, confidence)
- **`AINutritionResult`**: (items, totals)

---

## 🛠️ 2. Provider Implementations

Each provider will live in its own file under `backend/app/services/providers/`.

1.  **`GeminiProvider`**: Refactored version of the current `GoogleAIService`.
2.  **`OpenAIProvider`**: Using the current industry-standard Chat Completions API.
3.  **`AnthropicProvider`**: Supporting Claude 3+ models.
4.  **`LocalProvider`**: Supporting local execution via Ollama or custom endpoints.

---

## 🏭 3. The Provider Factory

The `AIFactory` (or `AIServiceManager`) will be responsible for resolving which provider to use for a given user session.

```python
# backend/app/services/ai_factory.py
class AIFactory:
    @staticmethod
    def get_service(provider_type: str, api_key: str, model_name: str) -> BaseAIService:
        if provider_type == "gemini":
            return GeminiProvider(api_key, model_name)
        elif provider_type == "openai":
            return OpenAIProvider(api_key, model_name)
        # ... additional providers
```

---

## 🔐 4. Configuration & Database Updates

To support multiple providers, we need to update how user keys are stored.

### Updated Database Model: `UserAIConfig`
We will replace (or migration from) `UserGeminiKey` to a more flexible model:
- `user_id` (FK)
- `provider_type` (Enum: GEMINI, OPENAI, ANTHROPIC, LOCAL)
- `encrypted_api_key` (String)
- `model_name` (String, e.g., 'gpt-4o', 'claude-3.5-sonnet')
- `settings` (JSONField for specific provider tweaks)

---

## 🚦 5. Implementation Roadmap

### Phase 1: Foundation (Current)
1. [ ] Create `BaseAIService` ABC in `backend/app/services/base_ai_service.py`.
2. [ ] Move current Gemini logic into `backend/app/services/providers/gemini.py`.
3. [ ] Update `ChatSessionService` to use the `AIFactory`.

### Phase 2: Multi-Provider Expansion
1. [ ] Implement `OpenAIProvider`.
2. [ ] Implement `AnthropicProvider`.
3. [ ] Create database migration for `UserAIConfig`.

### Phase 3: Frontend Evolution
1. [ ] Update Settings UI to allow choosing a provider.
2. [ ] Add dynamic fields for Provider-specific configurations.

---

## ⚖️ 6. Design Principles

- **Single Responsibility**: Each provider only knows how to talk to its own API.
- **Dependency Inversion**: High-level business logic depends on the `BaseAIService` abstraction, not concrete classes.
- **Graceful Degradation**: If a provider fails or isn't configured, the system provides a clear, helpful error message.

---
*Status: Planning Phase | Author: P.U.L.S.E Arch Team*
