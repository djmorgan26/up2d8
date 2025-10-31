"""OAuth utilities for Google authentication."""

import os
from typing import Dict, Optional
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import httpx

# OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://up2d8.azurewebsites.net/api/v1/auth/google/callback")

# Initialize OAuth
config = Config(environ={
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


async def get_google_user_info(access_token: str) -> Optional[Dict]:
    """
    Fetch user info from Google OAuth token.

    Args:
        access_token: Google OAuth access token

    Returns:
        Dict with user info (email, name, etc.) or None if failed
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Google user info: {e}")
            return None


def validate_oauth_config() -> bool:
    """
    Validate that OAuth environment variables are set.

    Returns:
        True if all required env vars are set, False otherwise
    """
    required_vars = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"Missing OAuth environment variables: {', '.join(missing)}")
        return False

    return True
