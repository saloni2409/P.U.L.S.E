"""Frontend utility functions for API communication"""

import httpx
import os
from typing import Optional, Any

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    """Client for communicating with backend API"""
    
    def __init__(self, base_url: str = BACKEND_URL, timeout: float = 30.0):
        """Initialize API client"""
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
    
    async def post(
        self,
        endpoint: str,
        data: dict,
        token: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Make POST request to backend"""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = await self.client.post(
                endpoint,
                json=data,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"API error: {str(e)}")
    
    async def get(
        self,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Make GET request to backend"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = await self.client.get(
                endpoint,
                headers=headers,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"API error: {str(e)}")
    
    async def close(self):
        """Close client connection"""
        await self.client.aclose()


def get_api_client() -> APIClient:
    """Get API client instance"""
    return APIClient()
