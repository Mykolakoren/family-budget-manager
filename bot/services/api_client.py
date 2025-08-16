import httpx
from typing import Optional, Dict, Any
from decouple import config


class APIClient:
    """HTTP client for API communication."""
    
    def __init__(self):
        self.base_url = config('API_BASE_URL', default='http://localhost:8000/api/v1')
        self.auth_token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def set_auth_token(self, token: str):
        """Set authentication token."""
        self.auth_token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        return await self.client.get(url, headers=self._get_headers(), **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make POST request."""
        url = f"{self.base_url}{endpoint}"
        return await self.client.post(url, headers=self._get_headers(), **kwargs)
    
    async def patch(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make PATCH request."""
        url = f"{self.base_url}{endpoint}"
        return await self.client.patch(url, headers=self._get_headers(), **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        """Make DELETE request."""
        url = f"{self.base_url}{endpoint}"
        return await self.client.delete(url, headers=self._get_headers(), **kwargs)
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()