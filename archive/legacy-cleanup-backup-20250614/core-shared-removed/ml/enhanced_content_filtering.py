"""
Enhanced content-based filtering with personalized vector weighting.
Integrates user preferences with semantic search for improved recommendations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from .ai.embeddings import cosine_similarity, generate_vertex_embedding_async
from .database.client import get_supabase_client
from .ml.preference_learner import UserPreferenceLearner, UserPreferenceVector

logger = logging.getLogger(__name__)


@dataclass
class EnhancedContentRecommendation:
    """Enhanced content-based recommendation with personalization."""

    event_id: str
    event_name: str
    category: str
    base_similarity: float
    personalized_similarity: float
    category_boost: float
    temporal_boost: float
    final_score: float
    confidence: float
    explanation: str
    features_used: List[str]


@dataclass
class EventFeatures:
    """Extracted features from an event for content filtering."""

    event_id: str
    name: str
    category: str
    description: str
    embedding: Optional[np.ndarray]
    keywords: List[str]
    temporal_features: Dict[str, Any]
    location_features: Dict[str, Any]


class EnhancedContentFilter:
    """
    Enhanced content-based filtering that:
    1. Uses personalized vector weighting based on user preferences
    2. Applies category and temporal boosts from user behavior
    3. Combines semantic similarity with behavioral patterns
    4. Provides explainable recommendations with feature attribution
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self.preference_learner = UserPreferenceLearner()

        # Event features cache
        self.event_features: Dict[str, EventFeatures] = {}
        self.event_embeddings: Dict[str, np.ndarray] = {}

        # Personalization weights
        self.semantic_weight = 0.6
        self.category_weight = 0.2
        self.temporal_weight = 0.1
        self.popularity_weight = 0.1

        # Feature boost factors
        self.max_category_boost = 0.3
        self.max_temporal_boost = 0.2
        self.confidence_threshold = 0.3

        logger.info("Enhanced Content Filter initialized")

    async def load_event_features(self) -> None:
        """Load and extract features from all events."""
        logger.info("Loading event features for enhanced content filtering...")

        # Get events data
        events_response = self.supabase.table("events").select("*").execute()
        events_data = events_response.data or []

        if not events_data:
            logger.warning("No events found for feature extraction")
            return

        # Extract features for each event
        for event in events_data:
            event_id = event["id"]
            features = await self._extract_event_features(event)
            if features:
                self.event_features[event_id] = features
                if features.embedding is not None:
                    self.event_embeddings[event_id] = features.embedding

        logger.info(f"Loaded features for {len(self.event_features)} events")

    async def _extract_event_features(
        self, event: Dict[str, Any]
    ) -> Optional[EventFeatures]:
        """Extract comprehensive features from an event."""

        event_id = event["id"]
        name = event.get("name", "")
        category = event.get("category", "")
        description = event.get("description", "")

        # Extract keywords from name and description
        keywords = self._extract_keywords(name, description, category)

        # Generate or retrieve embedding
        embedding = await self._get_event_embedding(event_id, name, description)

        # Extract temporal features
        temporal_features = self._extract_temporal_features(event)

        # Extract location features
        location_features = self._extract_location_features(event)

        return EventFeatures(
            event_id=event_id,
            name=name,
            category=category,
            description=description,
            embedding=embedding,
            keywords=keywords,
            temporal_features=temporal_features,
            location_features=location_features,
        )

    def _extract_keywords(
        self, name: str, description: str, category: str
    ) -> List[str]:
        """Extract keywords from event text fields."""

        # Combine all text
        text = f"{name} {description} {category}".lower()

        # Simple keyword extraction (could be enhanced with NLP)
        words = text.split()

        # Filter out common words and short words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
        }

        keywords = [
            word.strip(".,!?;:()[]{}")
            for word in words
            if len(word) > 2 and word.lower() not in stop_words
        ]

        return list(set(keywords))[:20]  # Limit to top 20 unique keywords

    async def _get_event_embedding(
        self, event_id: str, name: str, description: str
    ) -> Optional[np.ndarray]:
        """Get or generate embedding for an event."""

        # Check if embedding already exists in database
        # (In production, you'd retrieve the stored embedding)

        # Generate embedding from name and description
        text_content = f"{name} {description}".strip()
        if len(text_content) < 10:
            text_content = name  # Fallback to just name

        if not text_content:
            return None

        try:
            embedding_list = await generate_vertex_embedding_async(text_content)
            if embedding_list:
                return np.array(embedding_list)
        except Exception as e:
            logger.error(f"Error generating embedding for event {event_id}: {e}")

        return None

    def _extract_temporal_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal features from event."""

        features = {}

        # Parse start time
        start_time_str = event.get("start_time_iso")
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(
                    start_time_str.replace("Z", "+00:00")
                )
                start_time = start_time.replace(tzinfo=None)

                features.update(
                    {
                        "hour": start_time.hour,
                        "day_of_week": start_time.weekday(),
                        "is_weekend": start_time.weekday() >= 5,
                        "time_category": self._categorize_time(start_time.hour),
                        "days_from_now": (start_time - datetime.now()).days,
                    }
                )
            except:
                pass

        return features

    def _categorize_time(self, hour: int) -> str:
        """Categorize hour into time periods."""
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 24:
            return "evening"
        else:
            return "night"

    def _extract_location_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract location features from event."""

        features = {}

        location_name = event.get("location_name", "")
        location_address = event.get("location_address", "")

        if location_name:
            features["venue_type"] = self._categorize_venue(location_name)

        if location_address:
            features["has_address"] = True
            # Could extract city, country, etc.

        return features

    def _categorize_venue(self, location_name: str) -> str:
        """Categorize venue type from location name."""
        location_lower = location_name.lower()

        if any(
            word in location_lower for word in ["hotel", "marriott", "hilton", "hyatt"]
        ):
            return "hotel"
        elif any(word in location_lower for word in ["center", "centre", "convention"]):
            return "convention_center"
        elif any(
            word in location_lower for word in ["university", "college", "campus"]
        ):
            return "academic"
        elif any(
            word in location_lower for word in ["co-working", "coworking", "office"]
        ):
            return "coworking"
        elif any(
            word in location_lower for word in ["online", "virtual", "zoom", "discord"]
        ):
            return "virtual"
        else:
            return "other"

    async def get_personalized_recommendations(
        self,
        user_id: str,
        query: Optional[str] = None,
        num_recommendations: int = 10,
        exclude_interacted: bool = True,
    ) -> List[EnhancedContentRecommendation]:
        """
        Get personalized content-based recommendations.

        Args:
            user_id: Target user ID
            query: Optional search query for semantic matching
            num_recommendations: Number of recommendations to return
            exclude_interacted: Whether to exclude previously interacted events

        Returns:
            List of enhanced content recommendations
        """

        logger.info(f"Generating personalized recommendations for user {user_id}")

        # Ensure data is loaded
        if not self.event_features:
            await self.load_event_features()

        # Get or learn user preferences
        user_preferences = await self.preference_learner.learn_user_preferences(user_id)

        if not user_preferences:
            logger.info(
                f"No preferences found for user {user_id}, using basic content filtering"
            )
            return await self._get_basic_content_recommendations(
                query, num_recommendations
            )

        # Get user's interaction history for exclusion
        user_interactions = set()
        if exclude_interacted:
            user_interactions = await self._get_user_interactions(user_id)

        # Generate query embedding if provided
        query_embedding = None
        if query:
            try:
                embedding_list = await generate_vertex_embedding_async(query)
                if embedding_list:
                    query_embedding = np.array(embedding_list)
            except Exception as e:
                logger.error(f"Error generating query embedding: {e}")

        # Score all events
        recommendations = []

        for event_id, event_features in self.event_features.items():
            if exclude_interacted and event_id in user_interactions:
                continue

            recommendation = await self._score_personalized_event(
                event_features, user_preferences, query_embedding
            )

            if recommendation and recommendation.final_score > 0.1:  # Minimum threshold
                recommendations.append(recommendation)

        # Sort by final score and return top N
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        return recommendations[:num_recommendations]

    async def _score_personalized_event(
        self,
        event_features: EventFeatures,
        user_preferences: UserPreferenceVector,
        query_embedding: Optional[np.ndarray] = None,
    ) -> Optional[EnhancedContentRecommendation]:
        """Score an event with personalized weighting."""

        if event_features.embedding is None:
            return None

        features_used = []

        # 1. Base semantic similarity
        base_similarity = 0.0
        personalized_similarity = 0.0

        # Query-based similarity
        if query_embedding is not None:
            base_similarity = cosine_similarity(
                query_embedding.tolist(), event_features.embedding.tolist()
            )
            features_used.append("query_semantic")

        # User preference-based similarity
        if user_preferences.embedding_vector is not None:
            personalized_similarity = cosine_similarity(
                user_preferences.embedding_vector.tolist(),
                event_features.embedding.tolist(),
            )
            features_used.append("user_preference_semantic")

        # Use the higher of the two similarities as base
        semantic_score = max(base_similarity, personalized_similarity)

        # 2. Category boost based on user preferences
        category_boost = 0.0
        category = event_features.category.lower() if event_features.category else ""

        if category and category in user_preferences.category_weights:
            category_preference = user_preferences.category_weights[category]
            category_boost = category_preference * self.max_category_boost
            features_used.append("category_preference")

        # 3. Temporal boost based on user patterns
        temporal_boost = 0.0
        temporal_features = event_features.temporal_features

        if temporal_features and user_preferences.temporal_weights:
            time_category = temporal_features.get("time_category")
            is_weekend = temporal_features.get("is_weekend", False)

            # Time of day preference
            if time_category and time_category in user_preferences.temporal_weights:
                time_preference = user_preferences.temporal_weights[time_category]
                temporal_boost += time_preference * self.max_temporal_boost * 0.7
                features_used.append("time_preference")

            # Weekend vs weekday preference
            if is_weekend and "weekend" in user_preferences.temporal_weights:
                weekend_preference = user_preferences.temporal_weights["weekend"]
                temporal_boost += weekend_preference * self.max_temporal_boost * 0.3
                features_used.append("weekend_preference")
            elif not is_weekend and "weekday" in user_preferences.temporal_weights:
                weekday_preference = user_preferences.temporal_weights["weekday"]
                temporal_boost += weekday_preference * self.max_temporal_boost * 0.3
                features_used.append("weekday_preference")

        # 4. Calculate final score with weighted combination
        final_score = (
            self.semantic_weight * semantic_score
            + self.category_weight * category_boost
            + self.temporal_weight * temporal_boost
        )

        # Apply user confidence as a factor
        confidence_factor = 0.5 + 0.5 * user_preferences.confidence_score
        final_score *= confidence_factor

        # Calculate recommendation confidence
        recommendation_confidence = (
            min(1.0, len(features_used) / 4.0) * user_preferences.confidence_score
        )

        # Generate explanation
        explanation = self._generate_explanation(
            semantic_score, category_boost, temporal_boost, features_used, category
        )

        return EnhancedContentRecommendation(
            event_id=event_features.event_id,
            event_name=event_features.name,
            category=event_features.category,
            base_similarity=base_similarity,
            personalized_similarity=personalized_similarity,
            category_boost=category_boost,
            temporal_boost=temporal_boost,
            final_score=final_score,
            confidence=recommendation_confidence,
            explanation=explanation,
            features_used=features_used,
        )

    def _generate_explanation(
        self,
        semantic_score: float,
        category_boost: float,
        temporal_boost: float,
        features_used: List[str],
        category: str,
    ) -> str:
        """Generate human-readable explanation for the recommendation."""

        explanations = []

        if semantic_score > 0.7:
            explanations.append("high semantic relevance to your interests")
        elif semantic_score > 0.5:
            explanations.append("moderate semantic relevance to your interests")

        if category_boost > 0.1:
            explanations.append(f"matches your preference for {category} events")

        if temporal_boost > 0.05:
            explanations.append("aligns with your preferred timing patterns")

        if "user_preference_semantic" in features_used:
            explanations.append("similar to events you've searched for before")

        if not explanations:
            explanations.append("general content-based recommendation")

        return f"Recommended because: {', '.join(explanations)}"

    async def _get_basic_content_recommendations(
        self, query: Optional[str], num_recommendations: int
    ) -> List[EnhancedContentRecommendation]:
        """Get basic content recommendations for users without preferences."""

        if not query:
            return []

        query_embedding = None
        try:
            embedding_list = await generate_vertex_embedding_async(query)
            if embedding_list:
                query_embedding = np.array(embedding_list)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []

        recommendations = []

        for event_id, event_features in self.event_features.items():
            if event_features.embedding is None:
                continue

            similarity = cosine_similarity(
                query_embedding.tolist(), event_features.embedding.tolist()
            )

            if similarity > 0.3:  # Minimum threshold
                recommendation = EnhancedContentRecommendation(
                    event_id=event_features.event_id,
                    event_name=event_features.name,
                    category=event_features.category,
                    base_similarity=similarity,
                    personalized_similarity=0.0,
                    category_boost=0.0,
                    temporal_boost=0.0,
                    final_score=similarity,
                    confidence=0.5,
                    explanation=f"Basic semantic match for query: {query}",
                    features_used=["query_semantic"],
                )
                recommendations.append(recommendation)

        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        return recommendations[:num_recommendations]

    async def _get_user_interactions(self, user_id: str) -> set:
        """Get set of event IDs user has interacted with."""

        # This would typically come from the collaborative filtering engine
        # For now, return empty set
        return set()

    def get_recommendation_insights(
        self, recommendations: List[EnhancedContentRecommendation]
    ) -> Dict[str, Any]:
        """Get insights about the recommendation process."""

        if not recommendations:
            return {"error": "No recommendations to analyze"}

        # Analyze feature usage
        feature_usage = {}
        for rec in recommendations:
            for feature in rec.features_used:
                feature_usage[feature] = feature_usage.get(feature, 0) + 1

        # Analyze score distribution
        scores = [rec.final_score for rec in recommendations]

        # Analyze categories
        categories = [rec.category for rec in recommendations if rec.category]
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "total_recommendations": len(recommendations),
            "feature_usage": feature_usage,
            "score_stats": {
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "avg": sum(scores) / len(scores) if scores else 0,
            },
            "category_distribution": category_counts,
            "avg_confidence": sum(rec.confidence for rec in recommendations)
            / len(recommendations),
        }
