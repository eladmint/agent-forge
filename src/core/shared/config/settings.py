"""
Settings configuration for Agent Forge framework.
Handles environment variables and configuration management.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    """Configuration settings for the Telegram Bot service."""

    # Telegram Bot Configuration
    telegram_bot_token: str
    backend_api_url: str
    allowed_user_ids: Optional[str] = None

    # Database Configuration
    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # AI Configuration
    anthropic_api_key: Optional[str] = None
    vertex_project_id: Optional[str] = None
    vertex_location: Optional[str] = None
    vertex_model_name: Optional[str] = None

    # Service Configuration
    debug: bool = False
    log_level: str = "INFO"

    # Google Cloud Configuration
    google_cloud_project: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        load_dotenv()

        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            backend_api_url=os.getenv("BACKEND_API_URL", ""),
            allowed_user_ids=os.getenv("ALLOWED_TELEGRAM_USER_IDS"),
            database_url=os.getenv("DATABASE_URL"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            vertex_project_id=os.getenv("VERTEX_PROJECT_ID"),
            vertex_location=os.getenv("VERTEX_LOCATION"),
            vertex_model_name=os.getenv("VERTEX_MODEL_NAME"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        )

    def validate(self) -> bool:
        """Validate that required settings are present."""
        required_fields = ["telegram_bot_token", "backend_api_url"]

        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Required setting {field} is missing")

        return True
