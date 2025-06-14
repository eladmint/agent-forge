"""
Interface wrapper for user preference learning to match telegram bot expectations.
"""

import logging
from typing import Any, Dict, List

from .ml.preference_learner import UserPreferenceLearner

logger = logging.getLogger(__name__)


class UserPreferenceSystem:
    """
    Interface wrapper for UserPreferenceLearner to maintain compatibility.
    """

    def __init__(self):
        try:
            self.learner = UserPreferenceLearner()
            logger.info("User preference system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize user preference learner: {e}")
            self.learner = None

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned preferences for a user."""
        if not self.learner:
            return {}

        try:
            return self.learner.get_user_preferences(user_id)
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    def update_user_preferences(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user preferences based on interaction data."""
        if not self.learner:
            return

        try:
            self.learner.update_preferences(user_id, interaction_data)
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")

    def apply_user_preferences(
        self, events: List[Dict[str, Any]], user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply user preferences to filter/rank events."""
        if not self.learner or not events:
            return events

        try:
            # Basic preference filtering - can be enhanced
            user_id = user_data.get("user_id", "")
            preferences = self.get_user_preferences(user_id)

            if not preferences:
                return events

            # Simple preference-based ranking
            preferred_categories = preferences.get("preferred_categories", [])

            if preferred_categories:
                # Boost events in preferred categories
                for event in events:
                    if event.get("category", "").lower() in [
                        cat.lower() for cat in preferred_categories
                    ]:
                        event["preference_boost"] = True

            return events
        except Exception as e:
            logger.error(f"Error applying user preferences: {e}")
            return events

    def add_personalized_recommendations(
        self, user_query: str, user_data: Dict[str, Any]
    ) -> str:
        """Add personalized recommendation context to user query."""
        if not self.learner:
            return user_query

        try:
            user_id = user_data.get("user_id", "")
            preferences = self.get_user_preferences(user_id)

            if not preferences:
                return user_query

            # Add preference context to query
            preferred_categories = preferences.get("preferred_categories", [])
            if preferred_categories:
                preference_context = (
                    f" (User prefers: {', '.join(preferred_categories)})"
                )
                return user_query + preference_context

            return user_query
        except Exception as e:
            logger.error(f"Error adding personalized recommendations: {e}")
            return user_query
