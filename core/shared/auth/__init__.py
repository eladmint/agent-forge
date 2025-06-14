"""
Centralized Authentication Module
Provides OAuth, authentication routes, services, and handlers for the entire application.
"""

from .handlers.oauth_handlers import *
from .routes.auth_routes import *
from .services.oauth_authentication_service import *

__all__ = [
    # OAuth Routes
    "create_auth_routes",
    "oauth_router",
    # OAuth Services
    "OAuthAuthenticationService",
    "oauth_service",
    # OAuth Handlers
    "OAuth2Manager",
    "create_auth_url",
    "handle_oauth_callback",
    "get_user_auth_status",
]
