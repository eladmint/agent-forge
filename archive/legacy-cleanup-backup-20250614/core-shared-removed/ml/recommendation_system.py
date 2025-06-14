"""
Interface wrapper for the hybrid recommendation system to match telegram bot expectations.
"""

import logging
from typing import Any, Dict, List

from .ml.hybrid_recommender import HybridRecommendationEngine

logger = logging.getLogger(__name__)


class HybridRecommendationSystem:
    """
    Interface wrapper for HybridRecommendationEngine to maintain compatibility.
    """

    def __init__(self):
        try:
            self.engine = HybridRecommendationEngine()
            logger.info("Hybrid recommendation system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize hybrid recommendation engine: {e}")
            self.engine = None

    def get_recommendations(
        self, user_id: str, user_query: str = "", limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user."""
        if not self.engine:
            return []

        try:
            recommendations = self.engine.get_hybrid_recommendations(
                user_id=user_id, query=user_query, num_recommendations=limit
            )

            # Convert to expected format
            return [
                {
                    "event_id": rec.event_id,
                    "event_name": rec.event_name,
                    "category": rec.category,
                    "score": rec.final_score,
                    "confidence": rec.confidence,
                    "explanation": rec.explanation,
                }
                for rec in recommendations
            ]
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def update_user_interaction(
        self, user_id: str, event_id: str, interaction_type: str
    ):
        """Update user interaction data."""
        if not self.engine:
            return

        try:
            self.engine.record_user_interaction(user_id, event_id, interaction_type)
        except Exception as e:
            logger.error(f"Error updating user interaction: {e}")
