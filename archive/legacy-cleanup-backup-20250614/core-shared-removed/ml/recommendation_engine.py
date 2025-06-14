"""
ML-driven recommendation engine for event discovery and personalization.
Leverages existing vector embeddings and user behavior patterns.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from .database.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User preference profile based on search and interaction history."""

    user_id: str
    preference_vector: Optional[np.ndarray] = None
    category_preferences: Dict[str, float] = None
    temporal_preferences: Dict[str, float] = None
    interaction_history: List[Dict] = None
    confidence_score: float = 0.0
    last_updated: datetime = None

    def __post_init__(self):
        if self.category_preferences is None:
            self.category_preferences = {}
        if self.temporal_preferences is None:
            self.temporal_preferences = {}
        if self.interaction_history is None:
            self.interaction_history = []
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class RecommendationResult:
    """Individual recommendation result with scoring details."""

    event_id: str
    title: str
    relevance_score: float
    content_score: float = 0.0
    collaborative_score: float = 0.0
    popularity_score: float = 0.0
    personalization_score: float = 0.0
    explanation: str = ""


class MLRecommendationEngine:
    """
    Hybrid ML recommendation engine combining:
    1. Content-based filtering (semantic vectors + categories)
    2. Collaborative filtering (user-user similarity)
    3. Popularity-based recommendations
    4. Temporal preference modeling
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.event_embeddings: Dict[str, np.ndarray] = {}
        self.user_item_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.popularity_scores: Dict[str, float] = {}

        # Configuration
        self.min_interactions_for_cf = (
            3  # Minimum interactions for collaborative filtering
        )
        self.embedding_dimension = 768  # Google text-embedding-004 dimension
        self.decay_factor = 0.95  # Temporal decay for old interactions

        logger.info("ML Recommendation Engine initialized")

    async def load_user_profiles(self) -> None:
        """Load and compute user profiles from interaction history."""
        logger.info("Loading user profiles from interaction history...")

        # Get usage tracking data
        usage_response = self.supabase.table("usage_tracking").select("*").execute()
        usage_data = usage_response.data

        if not usage_data:
            logger.warning("No usage data found for profile generation")
            return

        # Group interactions by user
        user_interactions = defaultdict(list)
        for interaction in usage_data:
            user_id = interaction.get("user_id", "anonymous")
            user_interactions[user_id].append(interaction)

        # Generate profiles for each user
        for user_id, interactions in user_interactions.items():
            if len(interactions) >= 2:  # Minimum interactions for meaningful profile
                profile = await self._compute_user_profile(user_id, interactions)
                self.user_profiles[user_id] = profile

        logger.info(f"Loaded {len(self.user_profiles)} user profiles")

    async def _compute_user_profile(
        self, user_id: str, interactions: List[Dict]
    ) -> UserProfile:
        """Compute user preference profile from interaction history."""

        # Extract query patterns and preferences
        queries = [i.get("query", "") for i in interactions if i.get("query")]
        query_types = [i.get("query_type", "unknown") for i in interactions]

        # Analyze category preferences from queries
        category_preferences = self._extract_category_preferences(queries)

        # Analyze temporal preferences (when user searches)
        temporal_preferences = self._extract_temporal_preferences(interactions)

        # Compute user preference vector (if we have enough data)
        preference_vector = await self._compute_preference_vector(queries)

        # Confidence score based on interaction volume and diversity
        confidence_score = min(1.0, len(interactions) / 20.0)  # Max at 20 interactions
        query_diversity = len(set(queries)) / len(queries) if queries else 0
        confidence_score *= 0.5 + 0.5 * query_diversity  # Boost for diverse queries

        return UserProfile(
            user_id=user_id,
            preference_vector=preference_vector,
            category_preferences=category_preferences,
            temporal_preferences=temporal_preferences,
            interaction_history=interactions[-10:],  # Keep last 10 interactions
            confidence_score=confidence_score,
            last_updated=datetime.now(),
        )

    def _extract_category_preferences(self, queries: List[str]) -> Dict[str, float]:
        """Extract category preferences from user queries."""

        # Define category keywords mapping
        category_keywords = {
            "conference": ["conference", "summit", "devcon", "ethcc", "token2049"],
            "networking": ["networking", "meetup", "social", "community"],
            "workshop": ["workshop", "tutorial", "training", "hands-on"],
            "demo_day": ["demo", "demo day", "showcase", "pitch"],
            "party": ["party", "celebration", "social", "drinks"],
            "hackathon": ["hackathon", "hack", "coding", "build"],
            "crypto": ["bitcoin", "ethereum", "defi", "nft", "blockchain", "crypto"],
            "ai": ["ai", "artificial intelligence", "machine learning", "ml"],
            "startup": ["startup", "entrepreneur", "founder", "vc", "funding"],
        }

        category_scores = defaultdict(float)
        total_queries = len(queries)

        for query in queries:
            query_lower = query.lower()
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        category_scores[category] += 1.0

        # Normalize by total queries
        if total_queries > 0:
            category_scores = {k: v / total_queries for k, v in category_scores.items()}

        return dict(category_scores)

    def _extract_temporal_preferences(
        self, interactions: List[Dict]
    ) -> Dict[str, float]:
        """Extract temporal usage preferences."""

        hours = []
        days = []

        for interaction in interactions:
            if interaction.get("timestamp"):
                try:
                    ts_str = interaction["timestamp"]
                    if "T" in ts_str:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    else:
                        ts = datetime.fromisoformat(ts_str)

                    hours.append(ts.hour)
                    days.append(ts.weekday())  # 0=Monday, 6=Sunday
                except:
                    continue

        preferences = {}

        # Hour preferences (morning, afternoon, evening, night)
        if hours:
            morning = len([h for h in hours if 6 <= h < 12]) / len(hours)
            afternoon = len([h for h in hours if 12 <= h < 18]) / len(hours)
            evening = len([h for h in hours if 18 <= h < 24]) / len(hours)
            night = len([h for h in hours if 0 <= h < 6]) / len(hours)

            preferences.update(
                {
                    "morning": morning,
                    "afternoon": afternoon,
                    "evening": evening,
                    "night": night,
                }
            )

        # Day preferences (weekday vs weekend)
        if days:
            weekday = len([d for d in days if d < 5]) / len(days)
            weekend = len([d for d in days if d >= 5]) / len(days)

            preferences.update({"weekday": weekday, "weekend": weekend})

        return preferences

    async def _compute_preference_vector(
        self, queries: List[str]
    ) -> Optional[np.ndarray]:
        """Compute user preference vector from search queries."""

        if not queries or len(queries) < 3:
            return None

        # This would typically use the same embedding model as events
        # For now, return a placeholder that could be computed via API call
        # In production, you'd call the embedding service here

        # Placeholder: random vector (in production, use actual embeddings)
        return np.random.randn(self.embedding_dimension)

    async def load_event_data(self) -> None:
        """Load event data and embeddings for recommendation computation."""
        logger.info("Loading event data and embeddings...")

        # Get events with embeddings
        events_response = self.supabase.table("events").select("*").execute()
        events_data = events_response.data

        if not events_data:
            logger.warning("No event data found")
            return

        # Load event embeddings (these should exist from the semantic search system)
        for event in events_data:
            event_id = event["id"]
            # In a real system, you'd load the actual embedding vector
            # For now, use placeholder
            self.event_embeddings[event_id] = np.random.randn(self.embedding_dimension)

        # Compute popularity scores based on hypothetical engagement
        self._compute_popularity_scores(events_data)

        logger.info(f"Loaded {len(self.event_embeddings)} event embeddings")

    def _compute_popularity_scores(self, events_data: List[Dict]) -> None:
        """Compute popularity scores for events."""

        # Placeholder popularity computation
        # In production, this would be based on:
        # - Number of views/searches
        # - Registration counts
        # - Social media mentions
        # - Recency of the event

        for event in events_data:
            event_id = event["id"]
            # Simple popularity based on title length and category
            base_score = 0.5

            # Boost popular event types
            category = event.get("category") or ""
            category = category.lower() if category else ""
            if category in ["conference", "summit", "hackathon"]:
                base_score += 0.3
            elif category in ["networking", "meetup"]:
                base_score += 0.2

            # Add some randomness for demonstration
            import random

            popularity = min(1.0, base_score + random.random() * 0.3)
            self.popularity_scores[event_id] = popularity

    async def get_recommendations(
        self,
        user_id: str,
        num_recommendations: int = 10,
        include_explanation: bool = True,
    ) -> List[RecommendationResult]:
        """
        Get personalized recommendations for a user.

        Args:
            user_id: User identifier
            num_recommendations: Number of recommendations to return
            include_explanation: Whether to include explanation text

        Returns:
            List of recommendation results with scores
        """
        logger.info(f"Generating recommendations for user {user_id}")

        # Ensure data is loaded
        if not self.user_profiles:
            await self.load_user_profiles()
        if not self.event_embeddings:
            await self.load_event_data()

        user_profile = self.user_profiles.get(user_id)
        if not user_profile:
            # New user - use popularity-based recommendations
            return await self._get_popularity_recommendations(num_recommendations)

        # Get candidate events
        candidate_events = await self._get_candidate_events()

        recommendations = []
        for event in candidate_events:
            result = await self._score_recommendation(
                user_profile, event, include_explanation
            )
            if result:
                recommendations.append(result)

        # Sort by relevance score and return top N
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:num_recommendations]

    async def _get_candidate_events(self) -> List[Dict]:
        """Get candidate events for recommendation (e.g., upcoming events)."""

        # Get upcoming events (next 6 months)
        response = self.supabase.table("events").select("*").execute()
        events = response.data or []

        # Filter for upcoming/relevant events
        # In production, you'd filter by date, location, etc.
        return events[:50]  # Limit candidates for performance

    async def _score_recommendation(
        self, user_profile: UserProfile, event: Dict, include_explanation: bool = True
    ) -> Optional[RecommendationResult]:
        """Score a single event recommendation for a user."""

        event_id = event["id"]
        title = event.get("title", "")
        category = event.get("category") or ""
        category = category.lower() if category else ""

        # Content-based score (semantic similarity)
        content_score = 0.0
        if (
            user_profile.preference_vector is not None
            and event_id in self.event_embeddings
        ):
            event_vector = self.event_embeddings[event_id]
            # Cosine similarity
            content_score = np.dot(user_profile.preference_vector, event_vector) / (
                np.linalg.norm(user_profile.preference_vector)
                * np.linalg.norm(event_vector)
            )
            content_score = max(0, content_score)  # Ensure positive

        # Category preference score
        category_score = user_profile.category_preferences.get(category, 0.0)

        # Collaborative filtering score (placeholder)
        collaborative_score = 0.0  # Would compute user-user similarity here

        # Popularity score
        popularity_score = self.popularity_scores.get(event_id, 0.5)

        # Personalization score (combination of factors)
        personalization_score = (
            0.4 * content_score
            + 0.3 * category_score
            + 0.2 * collaborative_score
            + 0.1 * popularity_score
        )

        # Final relevance score with user confidence weighting
        relevance_score = (
            user_profile.confidence_score * personalization_score
            + (1 - user_profile.confidence_score) * popularity_score
        )

        # Generate explanation
        explanation = ""
        if include_explanation:
            explanations = []
            if content_score > 0.7:
                explanations.append("high semantic similarity to your interests")
            if category_score > 0.3:
                explanations.append(f"matches your preference for {category} events")
            if popularity_score > 0.7:
                explanations.append("popular event")

            if explanations:
                explanation = f"Recommended because: {', '.join(explanations)}"
            else:
                explanation = "General recommendation based on current trends"

        return RecommendationResult(
            event_id=event_id,
            title=title,
            relevance_score=relevance_score,
            content_score=content_score,
            collaborative_score=collaborative_score,
            popularity_score=popularity_score,
            personalization_score=personalization_score,
            explanation=explanation,
        )

    async def _get_popularity_recommendations(
        self, num_recommendations: int
    ) -> List[RecommendationResult]:
        """Get popularity-based recommendations for new users."""

        candidate_events = await self._get_candidate_events()
        recommendations = []

        for event in candidate_events:
            event_id = event["id"]
            title = event.get("title", "")
            popularity_score = self.popularity_scores.get(event_id, 0.5)

            result = RecommendationResult(
                event_id=event_id,
                title=title,
                relevance_score=popularity_score,
                popularity_score=popularity_score,
                explanation="Popular event recommendation for new users",
            )
            recommendations.append(result)

        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:num_recommendations]

    async def update_user_interaction(
        self,
        user_id: str,
        event_id: str,
        interaction_type: str,
        interaction_weight: float = 1.0,
    ) -> None:
        """
        Update user interaction data for continuous learning.

        Args:
            user_id: User identifier
            event_id: Event identifier
            interaction_type: Type of interaction (view, click, save, etc.)
            interaction_weight: Weight of the interaction (1.0 = normal)
        """

        # Update user-item matrix for collaborative filtering
        self.user_item_matrix[user_id][event_id] = interaction_weight

        # Update user profile if it exists
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            profile.interaction_history.append(
                {
                    "event_id": event_id,
                    "interaction_type": interaction_type,
                    "weight": interaction_weight,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Keep only recent interactions
            profile.interaction_history = profile.interaction_history[-20:]
            profile.last_updated = datetime.now()

        logger.debug(
            f"Updated interaction: user={user_id}, event={event_id}, type={interaction_type}"
        )

    def get_recommendation_metrics(self) -> Dict[str, Any]:
        """Get recommendation system performance metrics."""

        return {
            "total_users": len(self.user_profiles),
            "total_events": len(self.event_embeddings),
            "avg_user_confidence": (
                np.mean([p.confidence_score for p in self.user_profiles.values()])
                if self.user_profiles
                else 0
            ),
            "users_with_sufficient_data": len(
                [p for p in self.user_profiles.values() if p.confidence_score > 0.5]
            ),
            "interaction_matrix_density": (
                len(
                    [
                        interaction
                        for user_interactions in self.user_item_matrix.values()
                        for interaction in user_interactions.values()
                    ]
                )
                / (len(self.user_profiles) * len(self.event_embeddings))
                if self.user_profiles and self.event_embeddings
                else 0
            ),
        }
