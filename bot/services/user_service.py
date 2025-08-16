from typing import Optional, Dict, Any
from telegram import User

from services.api_client import APIClient


async def register_or_get_user(api_client: APIClient, telegram_user: User) -> Optional[Dict[str, Any]]:
    """Register new user or get existing user data."""
    try:
        # Try to register user via Telegram
        user_data = {
            "telegram_id": str(telegram_user.id),
            "telegram_username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "preferred_language": telegram_user.language_code or "en"
        }
        
        response = await api_client.post("/auth/register", json=user_data)
        
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 400:
            # User might already exist, try to get by telegram_id
            # This would need a specific endpoint in the API
            return {"telegram_id": str(telegram_user.id)}
        else:
            return None
            
    except Exception as e:
        print(f"Error registering user: {e}")
        return None


async def get_user_token(api_client: APIClient, telegram_id: int) -> Optional[str]:
    """Get authentication token for user."""
    try:
        login_data = {
            "telegram_id": str(telegram_id)
        }
        
        response = await api_client.post("/auth/telegram-login", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            return None
            
    except Exception as e:
        print(f"Error getting user token: {e}")
        return None


async def get_user_profile(api_client: APIClient, token: str) -> Optional[Dict[str, Any]]:
    """Get user profile information."""
    try:
        api_client.set_auth_token(token)
        response = await api_client.get("/users/me")
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None