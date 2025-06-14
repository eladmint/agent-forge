"""
OAuth Authentication Routes for Event Registration Platforms

Handles OAuth callbacks and user authentication flows for:
- Meetup
- Eventbrite  
- Google
- GitHub

Integrates with Supabase auth and the registration system.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from ..services.oauth_authentication_service import AuthPlatform, oauth_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])


class AuthCallbackResponse(BaseModel):
    """Response model for auth callbacks"""

    success: bool
    platform: str
    message: str
    telegram_user_id: Optional[str] = None
    next_steps: Optional[list] = []


@auth_router.get("/connect/{platform}")
async def initiate_oauth_flow(
    platform: str,
    request: Request,
    telegram_user_id: str = Query(..., description="Telegram user ID"),
):
    """
    Initiate OAuth flow for a platform

    Args:
        platform: Platform to authenticate with (meetup, eventbrite, google)
        telegram_user_id: Telegram user ID

    Returns:
        Redirect to OAuth authorization URL
    """
    try:
        # Validate platform
        try:
            auth_platform = AuthPlatform(platform.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Unsupported platform: {platform}"
            )

        # Generate OAuth URL
        oauth_url = await oauth_service.generate_oauth_url(
            telegram_user_id=telegram_user_id, platform=auth_platform
        )

        logger.info(f"Generated OAuth URL for {telegram_user_id}/{platform}")

        # Redirect to OAuth provider
        return RedirectResponse(url=oauth_url, status_code=302)

    except Exception as e:
        logger.error(f"OAuth initiation failed for {platform}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initiate OAuth flow: {str(e)}"
        )


@auth_router.get("/callback/{platform}")
async def oauth_callback(
    platform: str,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """
    Handle OAuth callback from platform

    Args:
        platform: Platform that sent the callback
        code: Authorization code
        state: OAuth state
        error: OAuth error if any
        error_description: Error description

    Returns:
        HTML page with success/failure message
    """
    try:
        # Validate platform
        try:
            auth_platform = AuthPlatform(platform.lower())
        except ValueError:
            return HTMLResponse(
                content=generate_callback_html(
                    success=False,
                    platform=platform,
                    message=f"Unsupported platform: {platform}",
                ),
                status_code=400,
            )

        # Handle OAuth callback
        result = await oauth_service.handle_oauth_callback(
            platform=auth_platform,
            code=code,
            state=state,
            error=error or error_description,
        )

        # Generate response HTML
        html_content = generate_callback_html(
            success=result["success"],
            platform=platform,
            message=result.get("message", ""),
            telegram_user_id=result.get("telegram_user_id"),
            user_info=result.get("user_info", {}),
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"OAuth callback failed for {platform}: {str(e)}")

        return HTMLResponse(
            content=generate_callback_html(
                success=False,
                platform=platform,
                message=f"Authentication failed: {str(e)}",
            ),
            status_code=500,
        )


@auth_router.get("/setup-in-progress")
async def oauth_setup_in_progress(
    platform: str = Query(..., description="Platform name"),
    user_id: str = Query(..., description="User ID"),
):
    """Show setup in progress page when OAuth is not configured"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Setup in Progress</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .container {{ text-align: center; background: #f8f9fa; padding: 30px; border-radius: 10px; }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
            h1 {{ color: #333; margin-bottom: 20px; }}
            p {{ color: #666; line-height: 1.6; margin-bottom: 15px; }}
            .platform {{ color: #007bff; font-weight: bold; text-transform: capitalize; }}
            .note {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🔧</div>
            <h1>OAuth Integration Coming Soon</h1>
            <p>We're currently setting up <span class="platform">{platform}</span> authentication.</p>
            <p>This feature will be available shortly. Please check back soon!</p>
            <div class="note">
                <strong>Note:</strong> You can still use other features of the bot while we complete the OAuth setup.
            </div>
        </div>
        <script>
            // Auto-close after 5 seconds
            setTimeout(function() {{
                window.close();
            }}, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@auth_router.get("/status/{telegram_user_id}")
async def get_auth_status(telegram_user_id: str):
    """
    Get authentication status for a user

    Args:
        telegram_user_id: Telegram user ID

    Returns:
        List of connected platforms and their status
    """
    try:
        # For now, return status indicating OAuth setup is in progress
        # TODO: Implement database lookup for actual connected platforms

        platform_status = {}

        # Check which platforms have OAuth configured
        for platform in AuthPlatform:
            oauth_config = oauth_service.oauth_configs.get(platform, {})
            has_client_id = bool(oauth_config.get("client_id"))

            platform_status[platform.value] = {
                "connected": False,  # TODO: Check database for actual connections
                "oauth_configured": has_client_id,
                "status": "ready" if has_client_id else "setup_in_progress",
            }

        total_configured = sum(
            1 for p in platform_status.values() if p["oauth_configured"]
        )

        return {
            "telegram_user_id": telegram_user_id,
            "platforms": platform_status,
            "total_connected": 0,  # TODO: Count actual connections from database
            "total_configured": total_configured,
            "setup_status": "partial" if total_configured > 0 else "in_progress",
        }

    except Exception as e:
        logger.error(f"Failed to get auth status for {telegram_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get authentication status: {str(e)}"
        )


@auth_router.delete("/disconnect/{platform}")
async def disconnect_platform(
    platform: str, telegram_user_id: str = Query(..., description="Telegram user ID")
):
    """
    Disconnect a platform for a user

    Args:
        platform: Platform to disconnect
        telegram_user_id: Telegram user ID

    Returns:
        Success/failure status
    """
    try:
        # Validate platform
        try:
            auth_platform = AuthPlatform(platform.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Unsupported platform: {platform}"
            )

        # TODO: Implement platform disconnection in database
        # For now, return success since no connections are stored yet

        return {
            "success": True,
            "message": f"Platform {platform} disconnection not yet implemented",
            "platform": platform,
            "telegram_user_id": telegram_user_id,
            "note": "OAuth integration in progress",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Platform disconnect failed for {telegram_user_id}/{platform}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to disconnect platform: {str(e)}"
        )


def generate_callback_html(
    success: bool,
    platform: str,
    message: str,
    telegram_user_id: Optional[str] = None,
    user_info: Optional[dict] = None,
) -> str:
    """Generate HTML response for OAuth callback"""

    status_emoji = "✅" if success else "❌"
    status_color = "#28a745" if success else "#dc3545"

    user_display = ""
    if success and user_info:
        user_name = user_info.get("name") or user_info.get("login") or "User"
        user_email = user_info.get("email", "")
        user_display = f"""
        <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
            <h4>Connected Account:</h4>
            <p><strong>Name:</strong> {user_name}</p>
            <p><strong>Email:</strong> {user_email}</p>
        </div>
        """

    next_steps = ""
    if success:
        next_steps = f"""
        <div style="margin: 20px 0; padding: 15px; background: #d4edda; border-radius: 8px; border: 1px solid #c3e6cb;">
            <h4>✅ What's Next?</h4>
            <ol>
                <li>Return to your Telegram bot</li>
                <li>Try registering for events on {platform.title()}</li>
                <li>The bot will now use your connected account</li>
            </ol>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Forge - {platform.title()} Authentication</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 40px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .status-icon {{
                font-size: 64px;
                margin-bottom: 20px;
            }}
            .status-message {{
                color: {status_color};
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 20px;
            }}
            .platform-name {{
                color: #6c757d;
                font-size: 18px;
                margin-bottom: 30px;
            }}
            .close-button {{
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
            }}
            .close-button:hover {{
                background: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status-icon">{status_emoji}</div>
            <div class="status-message">
                {'Authentication Successful!' if success else 'Authentication Failed'}
            </div>
            <div class="platform-name">{platform.title()} Account</div>
            
            {user_display}
            
            <p style="color: #6c757d; line-height: 1.6;">
                {message}
            </p>
            
            {next_steps}
            
            <button class="close-button" onclick="window.close()">
                Close This Window
            </button>
            
            <script>
                // Auto-close after 10 seconds if successful
                if ({str(success).lower()}) {{
                    setTimeout(() => {{
                        window.close();
                    }}, 10000);
                }}
            </script>
        </div>
    </body>
    </html>
    """
