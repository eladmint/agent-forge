"""
OAuth Authentication Handlers for Telegram Bot

Provides commands for users to connect their event platform accounts
for automated registration functionality.

Commands:
- /connect_google - Connect Google account
- /connect_meetup - Connect Meetup account  
- /connect_eventbrite - Connect Eventbrite account
- /auth_status - Check connected accounts
- /disconnect - Disconnect platform accounts
"""

import logging
import os

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

# Configure logging
logger = logging.getLogger(__name__)


class OAuthBotHandlers:
    """OAuth authentication handlers for Telegram bot"""

    def __init__(self):
        self.api_base_url = os.getenv(
            "API_BASE_URL",
            "https://chatbot-api-service-v2-867263134607.us-central1.run.app",
        )

    async def handle_connect_google(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /connect_google command"""
        user_id = str(update.effective_user.id)

        try:
            # Generate OAuth URL through API
            oauth_url = (
                f"{self.api_base_url}/auth/connect/google?telegram_user_id={user_id}"
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔗 Connect Google Account",
                            web_app=WebAppInfo(url=oauth_url),
                        )
                    ]
                ]
            )

            await update.message.reply_text(
                "🔐 **Connect Your Google Account**\n\n"
                "To enable event registration, connect your Google account.\n"
                "This allows you to:\n"
                "• Register for events automatically\n"
                "• Use your real email for confirmations\n"
                "• Access premium features\n\n"
                "Click the button below to securely connect:",
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Failed to generate Google OAuth URL for {user_id}: {str(e)}")
            await update.message.reply_text(
                "❌ Failed to generate authentication link. Please try again later."
            )

    async def handle_connect_meetup(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /connect_meetup command"""
        user_id = str(update.effective_user.id)

        try:
            oauth_url = (
                f"{self.api_base_url}/auth/connect/meetup?telegram_user_id={user_id}"
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔗 Connect Meetup Account",
                            web_app=WebAppInfo(url=oauth_url),
                        )
                    ]
                ]
            )

            await update.message.reply_text(
                "🔐 **Connect Your Meetup Account**\n\n"
                "Connect your Meetup account to:\n"
                "• Automatically RSVP to Meetup events\n"
                "• Join waitlists when events are full\n"
                "• Access your Meetup profile information\n\n"
                "Click the button below to connect:",
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Failed to generate Meetup OAuth URL for {user_id}: {str(e)}")
            await update.message.reply_text(
                "❌ Failed to generate authentication link. Please try again later."
            )

    async def handle_connect_eventbrite(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /connect_eventbrite command"""
        user_id = str(update.effective_user.id)

        try:
            oauth_url = f"{self.api_base_url}/auth/connect/eventbrite?telegram_user_id={user_id}"

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔗 Connect Eventbrite Account",
                            web_app=WebAppInfo(url=oauth_url),
                        )
                    ]
                ]
            )

            await update.message.reply_text(
                "🔐 **Connect Your Eventbrite Account**\n\n"
                "Connect your Eventbrite account to:\n"
                "• Register for Eventbrite events automatically\n"
                "• Purchase tickets with your saved payment methods\n"
                "• Access organizer features if applicable\n\n"
                "Click the button below to connect:",
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(
                f"Failed to generate Eventbrite OAuth URL for {user_id}: {str(e)}"
            )
            await update.message.reply_text(
                "❌ Failed to generate authentication link. Please try again later."
            )

    async def handle_auth_status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle /auth_status command"""
        user_id = str(update.effective_user.id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/auth/status/{user_id}", timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    platforms = data.get("platforms", {})
                    total_connected = data.get("total_connected", 0)

                    status_text = "🔐 **Your Authentication Status**\n\n"
                    status_text += f"**Connected Accounts: {total_connected}**\n\n"

                    # Platform status
                    platform_emojis = {
                        "google": "🔍",
                        "meetup": "👥",
                        "eventbrite": "🎫",
                        "github": "👨‍💻",
                    }

                    for platform, info in platforms.items():
                        emoji = platform_emojis.get(platform, "🔗")
                        if info.get("connected"):
                            status_text += (
                                f"{emoji} **{platform.title()}**: ✅ Connected"
                            )
                            if info.get("platform_email"):
                                status_text += f" ({info['platform_email']})"
                            status_text += "\n"
                        else:
                            status_text += (
                                f"{emoji} **{platform.title()}**: ❌ Not Connected\n"
                            )

                    # Add connection instructions
                    if total_connected == 0:
                        status_text += "\n💡 **Get Started:**\n"
                        status_text += (
                            "Use `/connect_google` to connect your Google account\n"
                        )
                        status_text += "Use `/connect_meetup` for Meetup events\n"
                        status_text += "Use `/connect_eventbrite` for Eventbrite events"

                    # Add disconnect option if any accounts connected
                    keyboard = None
                    if total_connected > 0:
                        keyboard = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "🔓 Manage Connections",
                                        callback_data="manage_auth",
                                    )
                                ]
                            ]
                        )

                    await update.message.reply_text(
                        status_text, reply_markup=keyboard, parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(
                        "❌ Failed to retrieve authentication status. Please try again later."
                    )

        except Exception as e:
            logger.error(f"Failed to get auth status for {user_id}: {str(e)}")
            await update.message.reply_text(
                "❌ Failed to check authentication status. Please try again later."
            )

    async def handle_manage_auth_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle manage auth callback query"""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)

        # Create disconnect options
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔗 Connect More Accounts", callback_data="connect_more"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔓 Disconnect Google", callback_data="disconnect_google"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔓 Disconnect Meetup", callback_data="disconnect_meetup"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔓 Disconnect Eventbrite",
                        callback_data="disconnect_eventbrite",
                    )
                ],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_manage")],
            ]
        )

        await query.edit_message_text(
            "🔐 **Manage Your Connected Accounts**\n\n" "Choose an action below:",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    async def handle_disconnect_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle disconnect platform callback"""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        platform = query.data.replace("disconnect_", "")

        if platform in ["google", "meetup", "eventbrite"]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"{self.api_base_url}/auth/disconnect/{platform}?telegram_user_id={user_id}",
                        timeout=10.0,
                    )

                    if response.status_code == 200:
                        await query.edit_message_text(
                            f"✅ Successfully disconnected your {platform.title()} account.\n\n"
                            f"You can reconnect anytime using `/connect_{platform}`"
                        )
                    else:
                        await query.edit_message_text(
                            f"❌ Failed to disconnect {platform.title()} account. Please try again later."
                        )

            except Exception as e:
                logger.error(f"Failed to disconnect {platform} for {user_id}: {str(e)}")
                await query.edit_message_text(
                    f"❌ Failed to disconnect {platform.title()} account. Please try again later."
                )
        else:
            await query.edit_message_text("❌ Invalid platform specified.")

    async def handle_connect_more_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle connect more accounts callback"""
        query = update.callback_query
        await query.answer()

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔍 Connect Google", callback_data="connect_google_btn"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "👥 Connect Meetup", callback_data="connect_meetup_btn"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🎫 Connect Eventbrite", callback_data="connect_eventbrite_btn"
                    )
                ],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_manage")],
            ]
        )

        await query.edit_message_text(
            "🔗 **Connect Additional Accounts**\n\n" "Choose a platform to connect:",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    async def handle_connect_platform_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle connect platform button callbacks"""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        platform = query.data.replace("connect_", "").replace("_btn", "")

        if platform in ["google", "meetup", "eventbrite"]:
            oauth_url = f"{self.api_base_url}/auth/connect/{platform}?telegram_user_id={user_id}"

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"🔗 Connect {platform.title()}",
                            web_app=WebAppInfo(url=oauth_url),
                        )
                    ]
                ]
            )

            await query.edit_message_text(
                f"🔐 **Connect Your {platform.title()} Account**\n\n"
                "Click the button below to securely connect your account:",
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text("❌ Invalid platform specified.")

    async def handle_cancel_manage_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle cancel manage callback"""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text("❌ Cancelled account management.")


# Create global handlers instance
oauth_handlers = OAuthBotHandlers()


# Handler functions for registration
async def connect_google_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_connect_google(update, context)


async def connect_meetup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_connect_meetup(update, context)


async def connect_eventbrite_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await oauth_handlers.handle_connect_eventbrite(update, context)


async def auth_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_auth_status(update, context)


async def manage_auth_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_manage_auth_callback(update, context)


async def disconnect_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_disconnect_callback(update, context)


async def connect_more_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_connect_more_callback(update, context)


async def connect_platform_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_connect_platform_callback(update, context)


async def cancel_manage_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await oauth_handlers.handle_cancel_manage_callback(update, context)
