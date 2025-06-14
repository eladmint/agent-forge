#!/usr/bin/env python3
"""
Event Recommendation Optimization Service
Part of Phase 21: Advanced Analytics
Handles ML-based recommendation optimization and personalization
"""
import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserPreference:
    """User preference profile"""

    user_id: str
    categories: List[str]
    keywords: List[str]
    time_preferences: Dict[str, Any]
    location_preferences: List[str]
    price_range: Tuple[float, float]
    interaction_history: List[Dict]
    similarity_scores: Dict[str, float]


@dataclass
class RecommendationModel:
    """ML recommendation model"""

    vectorizer: Any
    similarity_matrix: np.ndarray
    user_clusters: np.ndarray
    event_features: np.ndarray
    model_metadata: Dict[str, Any]


class RecommendationOptimizationService:
    """Advanced recommendation optimization with ML"""

    def __init__(self, database_client=None):
        self.db = database_client
        self.models = {}
        self.user_profiles = {}
        self.event_embeddings = {}
        self.interaction_weights = {
            "click": 1.0,
            "bookmark": 2.0,
            "register": 3.0,
            "attend": 5.0,
            "rate": 2.0,
            "share": 1.5,
        }

    async def initialize_models(self):
        """Initialize and load ML models"""
        try:
            logger.info("Initializing recommendation models...")

            # Load or create content-based model
            await self._load_content_model()

            # Load or create collaborative filtering model
            await self._load_collaborative_model()

            # Load or create hybrid model
            await self._load_hybrid_model()

            logger.info("Models initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing models: {e}")

    async def _load_content_model(self):
        """Load content-based recommendation model"""
        model_path = "models/content_model.joblib"

        try:
            if os.path.exists(model_path):
                self.models["content"] = joblib.load(model_path)
                logger.info("Content model loaded")
            else:
                await self._train_content_model()

        except Exception as e:
            logger.error(f"Error loading content model: {e}")
            await self._train_content_model()

    async def _train_content_model(self):
        """Train content-based model"""
        try:
            logger.info("Training content-based model...")

            # Get event data
            events = await self._get_events_for_training()

            if not events:
                logger.warning("No events available for training")
                return

            # Extract features
            descriptions = [self._extract_content_features(event) for event in events]

            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000, stop_words="english", ngram_range=(1, 2)
            )

            # Fit vectorizer
            feature_matrix = vectorizer.fit_transform(descriptions)

            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(feature_matrix)

            # Create model
            model = RecommendationModel(
                vectorizer=vectorizer,
                similarity_matrix=similarity_matrix,
                user_clusters=None,
                event_features=feature_matrix.toarray(),
                model_metadata={
                    "trained_at": datetime.now().isoformat(),
                    "num_events": len(events),
                    "feature_count": feature_matrix.shape[1],
                },
            )

            self.models["content"] = model

            # Save model
            os.makedirs("models", exist_ok=True)
            joblib.dump(model, "models/content_model.joblib")

            logger.info(f"Content model trained with {len(events)} events")

        except Exception as e:
            logger.error(f"Error training content model: {e}")

    async def _load_collaborative_model(self):
        """Load collaborative filtering model"""
        model_path = "models/collaborative_model.joblib"

        try:
            if os.path.exists(model_path):
                self.models["collaborative"] = joblib.load(model_path)
                logger.info("Collaborative model loaded")
            else:
                await self._train_collaborative_model()

        except Exception as e:
            logger.error(f"Error loading collaborative model: {e}")
            await self._train_collaborative_model()

    async def _train_collaborative_model(self):
        """Train collaborative filtering model"""
        try:
            logger.info("Training collaborative filtering model...")

            # Get user interaction data
            interactions = await self._get_user_interactions()

            if not interactions:
                logger.warning("No interactions available for training")
                return

            # Create user-item matrix
            user_item_matrix = self._create_user_item_matrix(interactions)

            # Apply clustering to find user groups
            if user_item_matrix.shape[0] > 5:  # Need minimum users for clustering
                kmeans = KMeans(n_clusters=min(5, user_item_matrix.shape[0] // 2))
                user_clusters = kmeans.fit_predict(user_item_matrix)
            else:
                user_clusters = np.zeros(user_item_matrix.shape[0])

            # Create model
            model = {
                "user_item_matrix": user_item_matrix,
                "user_clusters": user_clusters,
                "trained_at": datetime.now().isoformat(),
                "num_users": user_item_matrix.shape[0],
                "num_items": user_item_matrix.shape[1],
            }

            self.models["collaborative"] = model

            # Save model
            os.makedirs("models", exist_ok=True)
            joblib.dump(model, "models/collaborative_model.joblib")

            logger.info(
                f"Collaborative model trained with {len(interactions)} interactions"
            )

        except Exception as e:
            logger.error(f"Error training collaborative model: {e}")

    async def _load_hybrid_model(self):
        """Load hybrid recommendation model"""
        try:
            # Hybrid model combines content and collaborative
            if "content" in self.models and "collaborative" in self.models:
                self.models["hybrid"] = {
                    "content_weight": 0.6,
                    "collaborative_weight": 0.4,
                    "created_at": datetime.now().isoformat(),
                }
                logger.info("Hybrid model initialized")
            else:
                logger.warning("Cannot create hybrid model without base models")

        except Exception as e:
            logger.error(f"Error initializing hybrid model: {e}")

    async def get_personalized_recommendations(
        self, user_id: str, num_recommendations: int = 10, model_type: str = "hybrid"
    ) -> List[Dict]:
        """Get personalized event recommendations"""
        try:
            logger.info(f"Getting recommendations for user {user_id}")

            # Get or create user profile
            user_profile = await self._get_user_profile(user_id)

            if model_type == "hybrid" and "hybrid" in self.models:
                recommendations = await self._get_hybrid_recommendations(
                    user_profile, num_recommendations
                )
            elif model_type == "content" and "content" in self.models:
                recommendations = await self._get_content_recommendations(
                    user_profile, num_recommendations
                )
            elif model_type == "collaborative" and "collaborative" in self.models:
                recommendations = await self._get_collaborative_recommendations(
                    user_profile, num_recommendations
                )
            else:
                # Fallback to simple recommendations
                recommendations = await self._get_fallback_recommendations(
                    user_profile, num_recommendations
                )

            # Add explanation scores
            recommendations = await self._add_explanation_scores(
                recommendations, user_profile
            )

            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    async def _get_hybrid_recommendations(
        self, user_profile: UserPreference, num_recommendations: int
    ) -> List[Dict]:
        """Get recommendations using hybrid approach"""
        try:
            # Get content-based recommendations
            content_recs = await self._get_content_recommendations(
                user_profile, num_recommendations * 2
            )

            # Get collaborative recommendations
            collab_recs = await self._get_collaborative_recommendations(
                user_profile, num_recommendations * 2
            )

            # Combine and weight recommendations
            hybrid_scores = {}

            # Weight content recommendations
            content_weight = self.models["hybrid"]["content_weight"]
            for rec in content_recs:
                event_id = rec["event_id"]
                hybrid_scores[event_id] = (
                    hybrid_scores.get(event_id, 0) + rec["score"] * content_weight
                )

            # Weight collaborative recommendations
            collab_weight = self.models["hybrid"]["collaborative_weight"]
            for rec in collab_recs:
                event_id = rec["event_id"]
                hybrid_scores[event_id] = (
                    hybrid_scores.get(event_id, 0) + rec["score"] * collab_weight
                )

            # Sort by combined score
            sorted_recommendations = sorted(
                hybrid_scores.items(), key=lambda x: x[1], reverse=True
            )

            # Get top recommendations with event details
            recommendations = []
            for event_id, score in sorted_recommendations[:num_recommendations]:
                event_details = await self._get_event_details(event_id)
                if event_details:
                    event_details["score"] = score
                    event_details["recommendation_type"] = "hybrid"
                    recommendations.append(event_details)

            return recommendations

        except Exception as e:
            logger.error(f"Error in hybrid recommendations: {e}")
            return []

    async def _get_content_recommendations(
        self, user_profile: UserPreference, num_recommendations: int
    ) -> List[Dict]:
        """Get content-based recommendations"""
        try:
            if "content" not in self.models:
                return []

            model = self.models["content"]

            # Create user preference vector
            user_text = self._create_user_preference_text(user_profile)
            user_vector = model.vectorizer.transform([user_text])

            # Calculate similarity with all events
            similarities = cosine_similarity(user_vector, model.event_features)[0]

            # Get top similar events
            top_indices = similarities.argsort()[-num_recommendations:][::-1]

            recommendations = []
            for idx in top_indices:
                event_details = await self._get_event_by_index(idx)
                if event_details:
                    event_details["score"] = float(similarities[idx])
                    event_details["recommendation_type"] = "content"
                    recommendations.append(event_details)

            return recommendations

        except Exception as e:
            logger.error(f"Error in content recommendations: {e}")
            return []

    async def _get_collaborative_recommendations(
        self, user_profile: UserPreference, num_recommendations: int
    ) -> List[Dict]:
        """Get collaborative filtering recommendations"""
        try:
            if "collaborative" not in self.models:
                return []

            model = self.models["collaborative"]

            # Find similar users in the same cluster
            user_cluster = await self._get_user_cluster(user_profile.user_id)
            similar_users = await self._get_similar_users(
                user_profile.user_id, user_cluster
            )

            # Get events liked by similar users
            recommended_events = await self._get_events_from_similar_users(
                similar_users
            )

            # Filter out events user has already interacted with
            user_interactions = set(
                interaction["event_id"]
                for interaction in user_profile.interaction_history
            )

            filtered_events = [
                event
                for event in recommended_events
                if event["event_id"] not in user_interactions
            ]

            # Sort by collaborative score
            sorted_events = sorted(
                filtered_events, key=lambda x: x.get("collab_score", 0), reverse=True
            )

            recommendations = []
            for event in sorted_events[:num_recommendations]:
                event["recommendation_type"] = "collaborative"
                recommendations.append(event)

            return recommendations

        except Exception as e:
            logger.error(f"Error in collaborative recommendations: {e}")
            return []

    async def _get_fallback_recommendations(
        self, user_profile: UserPreference, num_recommendations: int
    ) -> List[Dict]:
        """Get simple fallback recommendations"""
        try:
            # Simple category and keyword matching
            category_filter = (
                user_profile.categories[:3] if user_profile.categories else []
            )
            keyword_filter = user_profile.keywords[:5] if user_profile.keywords else []

            # Get recent events matching preferences
            events = await self._get_events_by_preferences(
                categories=category_filter,
                keywords=keyword_filter,
                limit=num_recommendations * 2,
            )

            # Simple scoring based on matches
            scored_events = []
            for event in events:
                score = self._calculate_simple_score(event, user_profile)
                event["score"] = score
                event["recommendation_type"] = "simple"
                scored_events.append(event)

            # Sort by score
            sorted_events = sorted(
                scored_events, key=lambda x: x["score"], reverse=True
            )

            return sorted_events[:num_recommendations]

        except Exception as e:
            logger.error(f"Error in fallback recommendations: {e}")
            return []

    async def update_user_interaction(
        self, user_id: str, event_id: str, interaction_type: str, metadata: Dict = None
    ):
        """Update user interaction for learning"""
        try:
            interaction = {
                "user_id": user_id,
                "event_id": event_id,
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "weight": self.interaction_weights.get(interaction_type, 1.0),
                "metadata": metadata or {},
            }

            # Store interaction
            await self._store_interaction(interaction)

            # Update user profile
            await self._update_user_profile(user_id, interaction)

            # Trigger model retraining if needed
            await self._check_retrain_trigger()

            logger.info(
                f"Updated interaction: {user_id} -> {event_id} ({interaction_type})"
            )

        except Exception as e:
            logger.error(f"Error updating interaction: {e}")

    async def get_recommendation_explanation(self, user_id: str, event_id: str) -> Dict:
        """Get explanation for why event was recommended"""
        try:
            user_profile = await self._get_user_profile(user_id)
            event_details = await self._get_event_details(event_id)

            explanation = {
                "category_match": self._explain_category_match(
                    user_profile, event_details
                ),
                "keyword_match": self._explain_keyword_match(
                    user_profile, event_details
                ),
                "time_preference": self._explain_time_preference(
                    user_profile, event_details
                ),
                "similar_users": await self._explain_similar_users(user_id, event_id),
                "past_attendance": self._explain_past_attendance(
                    user_profile, event_details
                ),
            }

            return explanation

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {}

    # Helper methods
    async def _get_events_for_training(self) -> List[Dict]:
        """Get events for model training"""
        # Implementation depends on database structure
        return []

    async def _store_interaction(self, interaction: Dict):
        """Store user interaction"""
        # Placeholder - would store to database
        logger.info(f"Storing interaction: {interaction}")

    async def _update_user_profile(self, user_id: str, interaction: Dict):
        """Update user profile based on interaction"""
        # Placeholder - would update user profile
        logger.info(
            f"Updating profile for {user_id} with interaction {interaction['interaction_type']}"
        )

    async def _check_retrain_trigger(self):
        """Check if models need retraining"""
        # Placeholder - would check if enough new data to retrain
        pass

    async def _get_events_by_preferences(
        self, categories=None, keywords=None, limit=10
    ):
        """Get events matching preferences"""
        # Placeholder - return mock events
        return [
            {
                "event_id": f"event_{i}",
                "name": f"Event {i}",
                "category": categories[0] if categories else "general",
                "description": f'Event {i} description with {keywords[0] if keywords else "content"}',
                "location": "Sample Location",
                "created_at": datetime.now().isoformat(),
            }
            for i in range(limit)
        ]

    async def _add_explanation_scores(
        self, recommendations: List[Dict], user_profile
    ) -> List[Dict]:
        """Add explanation scores to recommendations"""
        for rec in recommendations:
            rec["explanation"] = {
                "score": rec.get("score", 0.5),
                "reasons": ["Similar to your interests", "Popular in your area"],
            }
        return recommendations

    async def _get_event_details(self, event_id: str) -> Optional[Dict]:
        """Get event details by ID"""
        # Placeholder - would fetch from database
        return {
            "event_id": event_id,
            "name": f"Event {event_id}",
            "description": "Sample event description",
            "category": "general",
        }

    async def _get_event_by_index(self, index: int) -> Optional[Dict]:
        """Get event by index"""
        # Placeholder - would map index to event
        return {
            "event_id": f"event_{index}",
            "name": f"Event {index}",
            "description": "Sample event description",
        }

    async def _get_user_cluster(self, user_id: str) -> int:
        """Get user cluster assignment"""
        # Placeholder - would get from clustering model
        return 0

    async def _get_similar_users(self, user_id: str, cluster: int) -> List[str]:
        """Get similar users in cluster"""
        # Placeholder - would find similar users
        return [f"user_{i}" for i in range(3)]

    async def _get_events_from_similar_users(
        self, similar_users: List[str]
    ) -> List[Dict]:
        """Get events liked by similar users"""
        # Placeholder - would get events from similar users
        return [
            {
                "event_id": f"collab_event_{i}",
                "name": f"Collaborative Event {i}",
                "collab_score": 0.8 - (i * 0.1),
            }
            for i in range(3)
        ]

    def _extract_content_features(self, event: Dict) -> str:
        """Extract text features from event"""
        features = []
        if event.get("name"):
            features.append(event["name"])
        if event.get("description"):
            features.append(event["description"])
        if event.get("category"):
            features.append(event["category"])
        if event.get("tags"):
            features.extend(event["tags"])

        return " ".join(features)

    async def _get_user_interactions(self) -> List[Dict]:
        """Get user interactions for training"""
        # Implementation depends on database structure
        return []

    def _create_user_item_matrix(self, interactions: List[Dict]) -> np.ndarray:
        """Create user-item interaction matrix"""
        users = list(set(i["user_id"] for i in interactions))
        items = list(set(i["event_id"] for i in interactions))

        matrix = np.zeros((len(users), len(items)))

        user_map = {user: idx for idx, user in enumerate(users)}
        item_map = {item: idx for idx, item in enumerate(items)}

        for interaction in interactions:
            user_idx = user_map[interaction["user_id"]]
            item_idx = item_map[interaction["event_id"]]
            weight = self.interaction_weights.get(interaction["interaction_type"], 1.0)
            matrix[user_idx, item_idx] += weight

        return matrix

    async def _get_user_profile(self, user_id: str) -> UserPreference:
        """Get or create user preference profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]

        # Create default profile
        profile = UserPreference(
            user_id=user_id,
            categories=[],
            keywords=[],
            time_preferences={},
            location_preferences=[],
            price_range=(0.0, float("inf")),
            interaction_history=[],
            similarity_scores={},
        )

        self.user_profiles[user_id] = profile
        return profile

    def _create_user_preference_text(self, user_profile: UserPreference) -> str:
        """Create text representation of user preferences"""
        texts = []
        texts.extend(user_profile.categories)
        texts.extend(user_profile.keywords)
        texts.extend(user_profile.location_preferences)

        return " ".join(texts)

    def _calculate_simple_score(
        self, event: Dict, user_profile: UserPreference
    ) -> float:
        """Calculate simple matching score"""
        score = 0.0

        # Category match
        if event.get("category") in user_profile.categories:
            score += 2.0

        # Keyword match
        event_text = self._extract_content_features(event).lower()
        for keyword in user_profile.keywords:
            if keyword.lower() in event_text:
                score += 1.0

        # Location match
        if event.get("location") in user_profile.location_preferences:
            score += 1.5

        # Recency bonus
        if event.get("created_at"):
            days_old = (
                datetime.now() - datetime.fromisoformat(event["created_at"])
            ).days
            if days_old < 7:
                score += 0.5

        return score


# Initialize service
recommendation_service = RecommendationOptimizationService()

if __name__ == "__main__":
    asyncio.run(recommendation_service.initialize_models())
