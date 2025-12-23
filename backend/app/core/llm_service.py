"""
LLM Service abstraction layer - supports multiple providers
Currently configured for local LLM via Ollama
Can be easily extended for OpenAI, Anthropic, etc.
"""

from abc import ABC, abstractmethod
from typing import Optional
import httpx
import json
from app.core.settings import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text response from LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        pass


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using Ollama"""
    
    def __init__(self, endpoint: str, model: str):
        """
        Initialize local LLM provider.
        
        Args:
            endpoint: Ollama server endpoint (e.g., http://localhost:11434)
            model: Model name (e.g., llama2)
        """
        self.endpoint = endpoint
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate response using local LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            
        Returns:
            Generated text
        """
        try:
            url = f"{self.endpoint}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            raise Exception(f"Local LLM error: {str(e)}")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (for future use)"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate response using OpenAI.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            
        Returns:
            Generated text
        """
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider (for future use)"""
    
    def __init__(self, api_key: str, model: str = "claude-2"):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            headers={"x-api-key": api_key},
            timeout=30.0
        )
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate response using Claude.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            
        Returns:
            Generated text
        """
        try:
            url = "https://api.anthropic.com/v1/messages"
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"].strip()
        except Exception as e:
            raise Exception(f"Anthropic error: {str(e)}")


class LLMService:
    """Factory and manager for LLM providers"""
    
    _provider: Optional[LLMProvider] = None
    
    @classmethod
    def initialize(cls):
        """Initialize LLM provider based on settings"""
        service = settings.llm_service.lower()
        
        if service == "local":
            cls._provider = LocalLLMProvider(
                endpoint=settings.llm_local_endpoint,
                model=settings.llm_local_model
            )
        elif service == "openai":
            cls._provider = OpenAIProvider(
                api_key=settings.llm_openai_key
            )
        elif service == "anthropic":
            cls._provider = AnthropicProvider(
                api_key=settings.llm_anthropic_key
            )
        else:
            raise ValueError(f"Unknown LLM service: {service}")
    
    @classmethod
    async def generate(cls, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using configured provider.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            
        Returns:
            Generated text
        """
        if cls._provider is None:
            cls.initialize()
        
        return await cls._provider.generate(prompt, max_tokens)
