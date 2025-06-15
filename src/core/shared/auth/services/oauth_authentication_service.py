"""
OAuth Authentication Service for Event Registration Platforms

Handles OAuth callbacks and user authentication flows for:
- Google
- Meetup
- Eventbrite
- GitHub

Integrates with Supabase auth and the registration system.
"""

import logging
import os
from enum import Enum
from typing import Dict
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class AuthPlatform(Enum):
    """Supported OAuth platforms"""

    GOOGLE = "google"
    MEETUP = "meetup"
    EVENTBRITE = "eventbrite"
    GITHUB = "github"


class OAuthAuthenticationService:
    """Service for handling OAuth authentication flows"""

    def __init__(self):
        self.base_url = os.getenv(
            "API_BASE_URL", "https://chatbot-api-service-v2-oo6mrfxexq-uc.a.run.app"
        )
        self.oauth_configs = self._load_oauth_configs()

    def _load_oauth_configs(self) -> Dict[AuthPlatform, Dict[str, str]]:
        """Load OAuth configurations for all platforms"""
        return {
            AuthPlatform.GOOGLE: {
                "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "scope": "openid email profile",
                "redirect_uri": f"{self.base_url}/auth/callback/google",
            },
            AuthPlatform.MEETUP: {
                "client_id": os.getenv("MEETUP_OAUTH_CLIENT_ID", ""),
                "client_secret": os.getenv("MEETUP_OAUTH_CLIENT_SECRET", ""),
                "auth_uri": "https://secure.meetup.com/oauth2/authorize",
                "token_uri": "https://secure.meetup.com/oauth2/access",
                "scope": "basic",
                "redirect_uri": f"{self.base_url}/auth/callback/meetup",
            },
            AuthPlatform.EVENTBRITE: {
                "client_id": os.getenv("EVENTBRITE_OAUTH_CLIENT_ID", ""),
                "client_secret": os.getenv("EVENTBRITE_OAUTH_CLIENT_SECRET", ""),
                "auth_uri": "https://www.eventbrite.com/oauth/authorize",
                "token_uri": "https://www.eventbrite.com/oauth/token",
                "scope": "event",
                "redirect_uri": f"{self.base_url}/auth/callback/eventbrite",
            },
            AuthPlatform.GITHUB: {
                "client_id": os.getenv("GITHUB_OAUTH_CLIENT_ID", ""),
                "client_secret": os.getenv("GITHUB_OAUTH_CLIENT_SECRET", ""),
                "auth_uri": "https://github.com/login/oauth/authorize",
                "token_uri": "https://github.com/login/oauth/access_token",
                "scope": "user:email",
                "redirect_uri": f"{self.base_url}/auth/callback/github",
            },
        }

    async def generate_oauth_url(
        self, telegram_user_id: str, platform: AuthPlatform
    ) -> str:
        """Generate OAuth authorization URL for a platform"""
        if platform not in self.oauth_configs:
            raise HTTPException(
                status_code=400, detail=f"Unsupported platform: {platform.value}"
            )

        config = self.oauth_configs[platform]

        # Check if client ID is configured
        if not config["client_id"]:
            logger.warning(f"OAuth client ID not configured for {platform.value}")
            # Return a placeholder URL indicating setup is in progress
            return f"{self.base_url}/auth/setup-in-progress?platform={platform.value}&user_id={telegram_user_id}"

        # Build OAuth parameters
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "response_type": "code",
            "state": telegram_user_id,  # Use telegram_user_id as state parameter
        }

        # Add platform-specific parameters
        if platform == AuthPlatform.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"

        oauth_url = f"{config['auth_uri']}?{urlencode(params)}"
        logger.info(f"Generated OAuth URL for {telegram_user_id}/{platform.value}")

        return oauth_url

    async def exchange_code_for_token(
        self, platform: AuthPlatform, code: str, state: str
    ) -> Dict:
        """Exchange authorization code for access token"""
        if platform not in self.oauth_configs:
            raise HTTPException(
                status_code=400, detail=f"Unsupported platform: {platform.value}"
            )

        config = self.oauth_configs[platform]

        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"],
        }

        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    config["token_uri"], data=token_data, headers=headers, timeout=30
                )
                response.raise_for_status()

                token_info = response.json()
                logger.info(f"Successfully exchanged code for token: {platform.value}")

                return {
                    "access_token": token_info.get("access_token"),
                    "refresh_token": token_info.get("refresh_token"),
                    "expires_in": token_info.get("expires_in"),
                    "scope": token_info.get("scope"),
                    "platform": platform.value,
                    "telegram_user_id": state,
                }

            except Exception as e:
                logger.error(f"Token exchange failed for {platform.value}: {str(e)}")
                raise HTTPException(
                    status_code=400, detail=f"Token exchange failed: {str(e)}"
                )

    async def get_user_info(self, platform: AuthPlatform, access_token: str) -> Dict:
        """Get user information from OAuth platform"""
        user_info_urls = {
            AuthPlatform.GOOGLE: "https://www.googleapis.com/oauth2/v2/userinfo",
            AuthPlatform.GITHUB: "https://api.github.com/user",
            AuthPlatform.MEETUP: "https://api.meetup.com/members/self",
            AuthPlatform.EVENTBRITE: "https://www.eventbriteapi.com/v3/users/me/",
        }

        if platform not in user_info_urls:
            raise HTTPException(
                status_code=400, detail=f"User info not supported for: {platform.value}"
            )

        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    user_info_urls[platform], headers=headers, timeout=30
                )
                response.raise_for_status()

                user_data = response.json()
                logger.info(f"Retrieved user info for {platform.value}")

                # Normalize user data across platforms
                normalized_data = {
                    "platform": platform.value,
                    "platform_user_id": str(user_data.get("id", "")),
                    "email": user_data.get("email", ""),
                    "name": user_data.get("name", ""),
                    "raw_data": user_data,
                }

                return normalized_data

            except Exception as e:
                logger.error(f"Failed to get user info for {platform.value}: {str(e)}")
                raise HTTPException(
                    status_code=400, detail=f"Failed to get user info: {str(e)}"
                )


# Global service instance
oauth_service = OAuthAuthenticationService()
