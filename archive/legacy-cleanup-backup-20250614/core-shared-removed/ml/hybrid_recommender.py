"""
Hybrid recommendation system combining all ML approaches:
- Content-based filtering with personalized vector weighting
- Collaborative filtering using user-item interactions  
- Semantic search integration
- Popularity-based recommendations
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .database.client import get_supabase_client
from .ml.collaborative_filtering import (
    CollaborativeFilteringEngine,
    CollaborativeRecommendation,
)
from .ml.enhanced_content_filtering import (
    EnhancedContentFilter,
    EnhancedContentRecommendation,
)
from .ml.preference_learner import UserPreferenceLearner
from .ml.recommendation_engine import (
    MLRecommendationEngine,
    RecommendationResult,
)

logger = logging.getLogger(__name__)


@dataclass
class HybridRecommendation:
    """Unified recommendation from hybrid system."""

    event_id: str
    event_name: str
    category: str

    # Individual scores from different approaches
    content_score: float = 0.0
    collaborative_score: float = 0.0
    semantic_score: float = 0.0
    popularity_score: float = 0.0

    # Weighted final score
    final_score: float = 0.0
    confidence: float = 0.0

    # Explanation and metadata
    explanation: str = ""
    approaches_used: List[str] = None
    detailed_scores: Dict[str, Any] = None

    def __post_init__(self):
        if self.approaches_used is None:
            self.approaches_used = []
        if self.detailed_scores is None:
            self.detailed_scores = {}


@dataclass
class HybridSystemConfig:
    """Configuration for hybrid recommendation weights."""

    content_weight: float = 0.4
    collaborative_weight: float = 0.3
    semantic_weight: float = 0.2
    popularity_weight: float = 0.1

    # Confidence thresholds for each approach
    min_content_confidence: float = 0.3
    min_collaborative_confidence: float = 0.2
    min_semantic_confidence: float = 0.1

    # System behavior
    fallback_to_popularity: bool = True
    require_multiple_approaches: bool = False
    diversity_factor: float = 0.1


class HybridRecommenderSystem:
    """
    Hybrid recommendation system that intelligently combines:
    1. Enhanced content-based filtering with personalization
    2. Collaborative filtering from user similarities
    3. Semantic search for query-based recommendations
    4. Popularity-based fallbacks for cold start users
    """

    def __init__(self, config: Optional[HybridSystemConfig] = None):
        self.supabase = get_supabase_client()
        self.config = config or HybridSystemConfig()

        # Initialize all recommendation engines
        self.content_filter = EnhancedContentFilter()
        self.collaborative_engine = CollaborativeFilteringEngine()
        self.ml_engine = MLRecommendationEngine()
        self.preference_learner = UserPreferenceLearner()

        # System state
        self.engines_initialized = False
        self.user_approach_preferences: Dict[str, Dict[str, float]] = {}

        logger.info("Hybrid Recommender System initialized")

    async def initialize_engines(self) -> None:
        """Initialize all recommendation engines."""
        if self.engines_initialized:
            return

        logger.info("Initializing hybrid recommendation engines...")

        try:
            # Initialize content filter (load event features for limited set)
            await self._initialize_content_filter()

            # Initialize collaborative filtering
            await self.collaborative_engine.load_interaction_data()

            # Initialize ML engine
            await self.ml_engine.load_user_profiles()
            await self.ml_engine.load_event_data()

            self.engines_initialized = True
            logger.info("All recommendation engines initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing engines: {e}")
            raise

    async def _initialize_content_filter(self) -> None:
        """Initialize content filter with limited scope for performance."""
        # Load a sample of events for testing (in production, load all)
        events_response = self.supabase.table("events").select("*").limit(50).execute()
        events_data = events_response.data or []

        # Extract features for sample events
        for event in events_data:
            features = await self.content_filter._extract_event_features(event)
            if features:
                self.content_filter.event_features[features.event_id] = features
                if features.embedding is not None:
                    self.content_filter.event_embeddings[features.event_id] = (
                        features.embedding
                    )

        logger.info(
            f"Content filter initialized with {len(self.content_filter.event_features)} events"
        )

    async def get_hybrid_recommendations(
        self,
        user_id: str,
        query: Optional[str] = None,
        num_recommendations: int = 10,
        exclude_interacted: bool = True,
        approach_weights: Optional[Dict[str, float]] = None,
    ) -> List[HybridRecommendation]:
        """
        Get hybrid recommendations combining all approaches.

        Args:
            user_id: Target user ID
            query: Optional search query
            num_recommendations: Number of recommendations to return
            exclude_interacted: Whether to exclude previously interacted events
            approach_weights: Custom weights for different approaches

        Returns:
            List of hybrid recommendations sorted by final score
        """

        logger.info(f"Generating hybrid recommendations for user {user_id}")

        # Ensure engines are initialized
        await self.initialize_engines()

        # Use custom weights if provided
        weights = approach_weights or {
            "content": self.config.content_weight,
            "collaborative": self.config.collaborative_weight,
            "semantic": self.config.semantic_weight,
            "popularity": self.config.popularity_weight,
        }

        # Collect recommendations from all approaches
        all_recommendations = {}  # event_id -> recommendation_data

        # 1. Content-based recommendations
        content_recs = await self._get_content_recommendations(
            user_id, query, num_recommendations * 2
        )
        for rec in content_recs:
            if rec.event_id not in all_recommendations:
                all_recommendations[rec.event_id] = {
                    "event_name": rec.event_name,
                    "category": rec.category,
                    "approaches": [],
                    "scores": {},
                }
            all_recommendations[rec.event_id]["approaches"].append("content")
            all_recommendations[rec.event_id]["scores"]["content"] = rec

        # 2. Collaborative filtering recommendations
        collaborative_recs = await self._get_collaborative_recommendations(
            user_id, num_recommendations * 2
        )
        for rec in collaborative_recs:
            if rec.event_id not in all_recommendations:
                # Get event details
                event_details = await self._get_event_details(rec.event_id)
                all_recommendations[rec.event_id] = {
                    "event_name": event_details.get("name", "Unknown Event"),
                    "category": event_details.get("category", ""),
                    "approaches": [],
                    "scores": {},
                }
            all_recommendations[rec.event_id]["approaches"].append("collaborative")
            all_recommendations[rec.event_id]["scores"]["collaborative"] = rec

        # 3. Semantic search recommendations (if query provided)
        if query:
            semantic_recs = await self._get_semantic_recommendations(
                query, num_recommendations * 2
            )
            for rec in semantic_recs:
                if rec.event_id not in all_recommendations:
                    all_recommendations[rec.event_id] = {
                        "event_name": rec.title,
                        "category": "",  # Would need to fetch from database
                        "approaches": [],
                        "scores": {},
                    }
                all_recommendations[rec.event_id]["approaches"].append("semantic")
                all_recommendations[rec.event_id]["scores"]["semantic"] = rec

        # 4. Generate hybrid recommendations
        hybrid_recommendations = []

        for event_id, rec_data in all_recommendations.items():
            hybrid_rec = await self._create_hybrid_recommendation(
                event_id, rec_data, weights, user_id
            )

            if hybrid_rec and hybrid_rec.final_score > 0.1:  # Minimum threshold
                hybrid_recommendations.append(hybrid_rec)

        # 5. Add popularity-based recommendations if needed
        if (
            len(hybrid_recommendations) < num_recommendations
            and self.config.fallback_to_popularity
        ):
            popularity_recs = await self._get_popularity_recommendations(
                user_id, num_recommendations - len(hybrid_recommendations)
            )
            hybrid_recommendations.extend(popularity_recs)

        # 6. Apply diversity if configured
        if self.config.diversity_factor > 0:
            hybrid_recommendations = self._apply_diversity(hybrid_recommendations)

        # Sort by final score and return top N
        hybrid_recommendations.sort(key=lambda x: x.final_score, reverse=True)

        # Update user approach preferences for future weighting
        await self._update_user_approach_preferences(
            user_id, hybrid_recommendations[:num_recommendations]
        )

        return hybrid_recommendations[:num_recommendations]

    async def _get_content_recommendations(
        self, user_id: str, query: Optional[str], num_recommendations: int
    ) -> List[EnhancedContentRecommendation]:
        """Get content-based recommendations."""
        try:
            return await self.content_filter.get_personalized_recommendations(
                user_id=user_id, query=query, num_recommendations=num_recommendations
            )
        except Exception as e:
            logger.error(f"Error getting content recommendations: {e}")
            return []

    async def _get_collaborative_recommendations(
        self, user_id: str, num_recommendations: int
    ) -> List[CollaborativeRecommendation]:
        """Get collaborative filtering recommendations."""
        try:
            return await self.collaborative_engine.get_collaborative_recommendations(
                user_id=user_id, num_recommendations=num_recommendations
            )
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {e}")
            return []

    async def _get_semantic_recommendations(
        self, query: str, num_recommendations: int
    ) -> List[RecommendationResult]:
        """Get semantic search recommendations."""
        try:
            # This would integrate with existing semantic search
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting semantic recommendations: {e}")
            return []

    async def _get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get event details from database."""
        try:
            response = (
                self.supabase.table("events")
                .select("*")
                .eq("id", event_id)
                .single()
                .execute()
            )
            return response.data or {}
        except Exception as e:
            logger.error(f"Error getting event details for {event_id}: {e}")
            return {}

    async def _create_hybrid_recommendation(
        self,
        event_id: str,
        rec_data: Dict[str, Any],
        weights: Dict[str, float],
        user_id: str,
    ) -> Optional[HybridRecommendation]:
        """Create a hybrid recommendation by combining individual scores."""

        approaches = rec_data["approaches"]
        scores = rec_data["scores"]

        # Extract individual scores
        content_score = 0.0
        collaborative_score = 0.0
        semantic_score = 0.0
        popularity_score = 0.5  # Default popularity

        explanation_parts = []
        confidence_factors = []

        # Content-based score
        if "content" in scores:
            content_rec = scores["content"]
            content_score = content_rec.final_score
            confidence_factors.append(content_rec.confidence)
            explanation_parts.append("personalized content match")

        # Collaborative filtering score
        if "collaborative" in scores:
            collab_rec = scores["collaborative"]
            collaborative_score = collab_rec.score
            confidence_factors.append(collab_rec.confidence)
            explanation_parts.append(
                f"liked by {len(collab_rec.similar_users)} similar users"
            )

        # Semantic search score
        if "semantic" in scores:
            semantic_rec = scores["semantic"]
            semantic_score = semantic_rec.relevance_score
            confidence_factors.append(0.7)  # Default semantic confidence
            explanation_parts.append("semantic query match")

        # Calculate weighted final score
        final_score = (
            weights.get("content", 0) * content_score
            + weights.get("collaborative", 0) * collaborative_score
            + weights.get("semantic", 0) * semantic_score
            + weights.get("popularity", 0) * popularity_score
        )

        # Calculate overall confidence
        confidence = np.mean(confidence_factors) if confidence_factors else 0.5

        # Apply approach diversity bonus
        if len(approaches) > 1:
            diversity_bonus = 0.1 * (len(approaches) - 1)
            final_score += diversity_bonus
            explanation_parts.append("multi-approach consensus")

        # Generate explanation
        explanation = (
            f"Recommended because: {', '.join(explanation_parts)}"
            if explanation_parts
            else "General recommendation"
        )

        return HybridRecommendation(
            event_id=event_id,
            event_name=rec_data["event_name"],
            category=rec_data["category"],
            content_score=content_score,
            collaborative_score=collaborative_score,
            semantic_score=semantic_score,
            popularity_score=popularity_score,
            final_score=final_score,
            confidence=confidence,
            explanation=explanation,
            approaches_used=approaches,
            detailed_scores={
                "weights_used": weights,
                "individual_scores": {
                    "content": content_score,
                    "collaborative": collaborative_score,
                    "semantic": semantic_score,
                    "popularity": popularity_score,
                },
            },
        )

    async def _get_popularity_recommendations(
        self, user_id: str, num_recommendations: int
    ) -> List[HybridRecommendation]:
        """Get popularity-based fallback recommendations."""

        try:
            # Get popular events (simplified - could be based on interaction counts)
            events_response = (
                self.supabase.table("events")
                .select("*")
                .limit(num_recommendations * 2)
                .execute()
            )
            events = events_response.data or []

            popularity_recs = []
            for event in events[:num_recommendations]:
                rec = HybridRecommendation(
                    event_id=event["id"],
                    event_name=event.get("name", "Unknown Event"),
                    category=event.get("category", ""),
                    popularity_score=0.7,
                    final_score=0.7,
                    confidence=0.5,
                    explanation="Popular event recommendation",
                    approaches_used=["popularity"],
                )
                popularity_recs.append(rec)

            return popularity_recs

        except Exception as e:
            logger.error(f"Error getting popularity recommendations: {e}")
            return []

    def _apply_diversity(
        self, recommendations: List[HybridRecommendation]
    ) -> List[HybridRecommendation]:
        """Apply diversity to recommendations to avoid over-concentration."""

        if len(recommendations) <= 3:
            return recommendations

        # Group by category
        category_groups = {}
        for rec in recommendations:
            category = rec.category or "uncategorized"
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(rec)

        # Reorder to ensure diversity
        diverse_recs = []
        max_per_category = max(2, len(recommendations) // len(category_groups))

        # Round-robin selection from categories
        while len(diverse_recs) < len(recommendations) and any(
            category_groups.values()
        ):
            for category, recs in list(category_groups.items()):
                if (
                    recs
                    and len([r for r in diverse_recs if r.category == category])
                    < max_per_category
                ):
                    diverse_recs.append(recs.pop(0))
                    if not recs:
                        del category_groups[category]

                if len(diverse_recs) >= len(recommendations):
                    break

        return diverse_recs

    async def _update_user_approach_preferences(
        self, user_id: str, recommendations: List[HybridRecommendation]
    ) -> None:
        """Update user's approach preferences based on recommendation quality."""

        if not recommendations:
            return

        # Calculate approach effectiveness
        approach_scores = {
            "content": [],
            "collaborative": [],
            "semantic": [],
            "popularity": [],
        }

        for rec in recommendations:
            for approach in rec.approaches_used:
                if approach in approach_scores:
                    approach_scores[approach].append(rec.final_score)

        # Update user preferences (simple averaging)
        user_prefs = {}
        for approach, scores in approach_scores.items():
            if scores:
                user_prefs[approach] = np.mean(scores)

        # Store for future use (would persist to database in production)
        self.user_approach_preferences[user_id] = user_prefs

    def get_system_insights(self) -> Dict[str, Any]:
        """Get insights about the hybrid system performance."""

        return {
            "engines_initialized": self.engines_initialized,
            "configuration": {
                "content_weight": self.config.content_weight,
                "collaborative_weight": self.config.collaborative_weight,
                "semantic_weight": self.config.semantic_weight,
                "popularity_weight": self.config.popularity_weight,
            },
            "engines_status": {
                "content_filter_events": len(self.content_filter.event_features),
                "collaborative_users": len(self.collaborative_engine.user_index_map),
                "collaborative_items": len(self.collaborative_engine.item_index_map),
                "ml_engine_users": len(self.ml_engine.user_profiles),
            },
            "user_approach_preferences": len(self.user_approach_preferences),
        }

    async def evaluate_recommendation_quality(
        self, user_id: str, recommendations: List[HybridRecommendation]
    ) -> Dict[str, Any]:
        """Evaluate the quality of hybrid recommendations."""

        if not recommendations:
            return {"error": "No recommendations to evaluate"}

        # Analyze approach distribution
        approach_distribution = {}
        for rec in recommendations:
            for approach in rec.approaches_used:
                approach_distribution[approach] = (
                    approach_distribution.get(approach, 0) + 1
                )

        # Score distribution analysis
        scores = [rec.final_score for rec in recommendations]
        confidence_scores = [rec.confidence for rec in recommendations]

        # Category diversity
        categories = [rec.category for rec in recommendations if rec.category]
        unique_categories = len(set(categories))

        return {
            "total_recommendations": len(recommendations),
            "approach_distribution": approach_distribution,
            "score_statistics": {
                "min": min(scores),
                "max": max(scores),
                "mean": np.mean(scores),
                "std": np.std(scores),
            },
            "confidence_statistics": {
                "min": min(confidence_scores),
                "max": max(confidence_scores),
                "mean": np.mean(confidence_scores),
            },
            "diversity_metrics": {
                "unique_categories": unique_categories,
                "total_categories": len(categories),
                "diversity_ratio": (
                    unique_categories / len(categories) if categories else 0
                ),
            },
            "multi_approach_recommendations": len(
                [rec for rec in recommendations if len(rec.approaches_used) > 1]
            ),
        }
