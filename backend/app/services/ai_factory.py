"""AI Provider Factory for resolving and instantiating AI services"""

from typing import Optional
from app.services.base_ai_service import BaseAIService
from app.services.providers.gemini import GeminiProvider
from app.services.providers.local import LocalProvider


class AIFactory:
    """
    Resolves and instantiates the correct AI Provider based on user configuration.
    
    This factory implements the modular approach by decoupling the service
    invocation from the concrete implementation.
    """
    
    @staticmethod
    def get_service(
        provider_type: str, 
        credential: str, 
        model_name: Optional[str] = None
    ) -> BaseAIService:
        """
        Instantiate the requested AI service provider.
        
        Args:
            provider_type: Type of provider ('gemini', 'openai', 'anthropic', 'local')
            credential: API key for cloud providers or Base URL for local providers
            model_name: (Optional) Model identifier, such as 'gemini-1.5-pro'
            
        Returns:
            The instantiated AIService (inheriting from BaseAIService)
            
        Raises:
            ValueError: If provider_type is unsupported or invalid
        """
        provider_type = provider_type.lower()
        
        if provider_type == "gemini":
            kwargs = {}
            if model_name:
                kwargs["model"] = model_name
            return GeminiProvider(credential, **kwargs)
            
        elif provider_type == "openai":
            # For Phase 2 implementation
            raise ValueError("OpenAI provider is not yet implemented")
            
        elif provider_type == "anthropic":
            # For Phase 2 implementation
            raise ValueError("Anthropic provider is not yet implemented")
            
        elif provider_type == "local":
            if not credential:
                raise ValueError("Local base URL is required")
            return LocalProvider(credential, model=model_name or "llama3")
            
        else:
            raise ValueError(f"Unsupported AI provider type: {provider_type}")
