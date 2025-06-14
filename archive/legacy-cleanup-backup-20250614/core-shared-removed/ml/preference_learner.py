"""
Advanced user preference learning system with real embeddings and continuous learning.
Integrates with existing semantic search infrastructure.
"""

import hashlib
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
import numpy as np

from .ai.embeddings import generate_vertex_embedding_async
from .database.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class UserPreferenceVector:
    """Learned user preference vector with metadata."""

    user_id: str
    embedding_vector: np.ndarray
    confidence_score: float
    source_queries: List[str]
    category_weights: Dict[str, float]
    temporal_weights: Dict[str, float]
    interaction_count: int
    last_updated: datetime
    vector_hash: str = ""

    def __post_init__(self):
        if self.vector_hash == "":
            self.vector_hash = self._compute_vector_hash()

    def _compute_vector_hash(self) -> str:
        """Compute hash of the vector for change detection."""
        vector_bytes = self.embedding_vector.tobytes()
        return hashlib.md5(vector_bytes).hexdigest()


class UserPreferenceLearner:
    """
    Advanced user preference learning system that:
    1. Learns from search queries using real embeddings
    2. Tracks interaction patterns and weights
    3. Implements continuous learning and decay
    4. Integrates with existing semantic search system
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self.user_vectors: Dict[str, UserPreferenceVector] = {}
        self.query_embeddings_cache: Dict[str, np.ndarray] = {}

        # Learning parameters
        self.min_queries_for_learning = 3
        self.interaction_decay_days = 30
        self.embedding_dimension = 768  # Google text-embedding-004
        self.learning_rate = 0.1
        self.confidence_threshold = 0.3

        # Configure Google API if available
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            logger.info("Configured Google API for embeddings")
        else:
            logger.warning("GOOGLE_API_KEY not found - embeddings may not work")

        logger.info("User Preference Learner initialized")

    async def learn_user_preferences(
        self, user_id: str, force_recompute: bool = False
    ) -> Optional[UserPreferenceVector]:
        """
        Learn or update user preferences from their interaction history.

        Args:
            user_id: User identifier
            force_recompute: Force recomputation even if recent vector exists

        Returns:
            UserPreferenceVector if successful, None if insufficient data
        """

        # Check if we have a recent vector and don't need to recompute
        if not force_recompute and user_id in self.user_vectors:
            existing_vector = self.user_vectors[user_id]
            if (datetime.now() - existing_vector.last_updated).days < 1:
                logger.debug(f"Using cached preference vector for user {user_id}")
                return existing_vector

        logger.info(f"Learning preferences for user: {user_id}")

        # Get user's interaction history
        usage_response = (
            self.supabase.table("usage_tracking")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        interactions = usage_response.data or []

        if len(interactions) < self.min_queries_for_learning:
            logger.info(
                f"Insufficient interactions ({len(interactions)}) for user {user_id}"
            )
            return None

        # Extract queries and apply temporal decay
        weighted_queries = await self._extract_weighted_queries(interactions)

        if not weighted_queries:
            logger.info(f"No valid queries found for user {user_id}")
            return None

        # Compute preference embedding from weighted queries
        preference_embedding = await self._compute_preference_embedding(
            weighted_queries
        )

        if preference_embedding is None:
            logger.warning(f"Failed to compute preference embedding for user {user_id}")
            return None

        # Analyze category and temporal patterns
        category_weights = self._analyze_category_preferences(interactions)
        temporal_weights = self._analyze_temporal_patterns(interactions)

        # Compute confidence score
        confidence_score = self._compute_confidence_score(
            interactions, weighted_queries
        )

        # Create user preference vector
        user_vector = UserPreferenceVector(
            user_id=user_id,
            embedding_vector=preference_embedding,
            confidence_score=confidence_score,
            source_queries=[q for q, _ in weighted_queries],
            category_weights=category_weights,
            temporal_weights=temporal_weights,
            interaction_count=len(interactions),
            last_updated=datetime.now(),
        )

        # Cache the vector
        self.user_vectors[user_id] = user_vector

        # Optionally persist to database
        await self._persist_user_vector(user_vector)

        logger.info(
            f"Learned preferences for user {user_id}: confidence={confidence_score:.3f}"
        )
        return user_vector

    async def _extract_weighted_queries(
        self, interactions: List[Dict]
    ) -> List[Tuple[str, float]]:
        """Extract queries with temporal decay weights."""

        weighted_queries = []
        now = datetime.now()

        for interaction in interactions:
            query = interaction.get("query", "").strip()
            if not query or len(query) < 3:
                continue

            # Parse timestamp
            timestamp_str = interaction.get("timestamp")
            if not timestamp_str:
                continue

            try:
                if "T" in timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                else:
                    timestamp = datetime.fromisoformat(timestamp_str)
                timestamp = timestamp.replace(tzinfo=None)  # Make naive for comparison
            except:
                continue

            # Compute temporal decay weight
            days_ago = (now - timestamp).days
            decay_weight = np.exp(-days_ago / self.interaction_decay_days)

            # Additional weight based on query type and success
            type_weight = 1.0
            query_type = interaction.get("query_type", "unknown")
            if query_type in ["event_query", "speaker_query"]:
                type_weight = 1.2
            elif query_type in ["date_query"]:
                type_weight = 1.1

            success_weight = 1.0
            if interaction.get("status") == "success":
                success_weight = 1.1

            final_weight = decay_weight * type_weight * success_weight
            weighted_queries.append((query, final_weight))

        # Sort by weight (descending) and return top queries
        weighted_queries.sort(key=lambda x: x[1], reverse=True)
        return weighted_queries[:20]  # Keep top 20 weighted queries

    async def _compute_preference_embedding(
        self, weighted_queries: List[Tuple[str, float]]
    ) -> Optional[np.ndarray]:
        """Compute user preference embedding from weighted queries."""

        embeddings = []
        weights = []

        for query, weight in weighted_queries:
            # Check cache first
            if query in self.query_embeddings_cache:
                embedding = self.query_embeddings_cache[query]
            else:
                # Get embedding using existing infrastructure
                try:
                    embedding_list = await generate_vertex_embedding_async(query)
                    embedding = np.array(embedding_list) if embedding_list else None
                    if embedding is not None:
                        self.query_embeddings_cache[query] = embedding
                    else:
                        logger.warning(f"Failed to get embedding for query: {query}")
                        continue
                except Exception as e:
                    logger.error(f"Error getting embedding for query '{query}': {e}")
                    continue

            embeddings.append(embedding)
            weights.append(weight)

        if not embeddings:
            return None

        # Compute weighted average of embeddings
        embeddings_array = np.array(embeddings)
        weights_array = np.array(weights)

        # Normalize weights
        weights_normalized = weights_array / np.sum(weights_array)

        # Compute weighted average
        preference_embedding = np.average(
            embeddings_array, axis=0, weights=weights_normalized
        )

        # Normalize the final vector
        preference_embedding = preference_embedding / np.linalg.norm(
            preference_embedding
        )

        return preference_embedding

    def _analyze_category_preferences(
        self, interactions: List[Dict]
    ) -> Dict[str, float]:
        """Analyze user's category preferences from queries."""

        # Category keyword mapping (expanded from recommendation engine)
        category_keywords = {
            "conference": [
                "conference",
                "summit",
                "devcon",
                "ethcc",
                "token2049",
                "symposium",
            ],
            "networking": ["networking", "meetup", "social", "community", "mixer"],
            "workshop": ["workshop", "tutorial", "training", "hands-on", "masterclass"],
            "demo_day": ["demo", "demo day", "showcase", "pitch", "presentation"],
            "party": ["party", "celebration", "social", "drinks", "afterparty"],
            "hackathon": ["hackathon", "hack", "coding", "build", "buidl"],
            "crypto": [
                "bitcoin",
                "ethereum",
                "defi",
                "nft",
                "blockchain",
                "crypto",
                "web3",
            ],
            "ai": ["ai", "artificial intelligence", "machine learning", "ml", "llm"],
            "startup": [
                "startup",
                "entrepreneur",
                "founder",
                "vc",
                "funding",
                "investment",
            ],
            "defi": ["defi", "decentralized finance", "yield", "liquidity", "dex"],
            "nft": ["nft", "non-fungible token", "art", "collectible", "marketplace"],
            "gaming": ["gaming", "gamefi", "play to earn", "metaverse", "virtual"],
        }

        category_scores = defaultdict(float)
        total_interactions = len(interactions)

        for interaction in interactions:
            query = interaction.get("query", "").lower()
            if not query:
                continue

            # Weight by success and recency
            weight = 1.0
            if interaction.get("status") == "success":
                weight *= 1.2

            # Check for category keywords
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in query:
                        category_scores[category] += weight

        # Normalize by total interactions
        if total_interactions > 0:
            category_scores = {
                k: v / total_interactions for k, v in category_scores.items()
            }

        return dict(category_scores)

    def _analyze_temporal_patterns(self, interactions: List[Dict]) -> Dict[str, float]:
        """Analyze user's temporal usage patterns."""

        hour_patterns = defaultdict(int)
        day_patterns = defaultdict(int)

        for interaction in interactions:
            timestamp_str = interaction.get("timestamp")
            if not timestamp_str:
                continue

            try:
                if "T" in timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                else:
                    timestamp = datetime.fromisoformat(timestamp_str)

                # Hour patterns
                hour = timestamp.hour
                if 6 <= hour < 12:
                    hour_patterns["morning"] += 1
                elif 12 <= hour < 18:
                    hour_patterns["afternoon"] += 1
                elif 18 <= hour < 24:
                    hour_patterns["evening"] += 1
                else:
                    hour_patterns["night"] += 1

                # Day patterns
                weekday = timestamp.weekday()
                if weekday < 5:
                    day_patterns["weekday"] += 1
                else:
                    day_patterns["weekend"] += 1

            except:
                continue

        # Normalize patterns
        total_hour = sum(hour_patterns.values())
        total_day = sum(day_patterns.values())

        patterns = {}
        if total_hour > 0:
            for period, count in hour_patterns.items():
                patterns[period] = count / total_hour

        if total_day > 0:
            for period, count in day_patterns.items():
                patterns[period] = count / total_day

        return patterns

    def _compute_confidence_score(
        self, interactions: List[Dict], weighted_queries: List[Tuple[str, float]]
    ) -> float:
        """Compute confidence score for the learned preferences."""

        # Base confidence from interaction count
        interaction_confidence = min(1.0, len(interactions) / 20.0)

        # Query diversity factor
        unique_queries = len(set(q for q, _ in weighted_queries))
        total_queries = len(weighted_queries)
        diversity_factor = unique_queries / total_queries if total_queries > 0 else 0

        # Recent activity factor
        recent_interactions = [
            i
            for i in interactions
            if i.get("timestamp") and self._is_recent(i["timestamp"], days=7)
        ]
        recency_factor = min(1.0, len(recent_interactions) / 5.0)

        # Success rate factor
        successful_interactions = [
            i for i in interactions if i.get("status") == "success"
        ]
        success_rate = (
            len(successful_interactions) / len(interactions) if interactions else 0
        )

        # Combine factors
        confidence = (
            0.4 * interaction_confidence
            + 0.2 * diversity_factor
            + 0.2 * recency_factor
            + 0.2 * success_rate
        )

        return min(1.0, confidence)

    def _is_recent(self, timestamp_str: str, days: int = 7) -> bool:
        """Check if timestamp is within recent days."""
        try:
            if "T" in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                timestamp = datetime.fromisoformat(timestamp_str)
            timestamp = timestamp.replace(tzinfo=None)

            cutoff = datetime.now() - timedelta(days=days)
            return timestamp > cutoff
        except:
            return False

    async def _persist_user_vector(self, user_vector: UserPreferenceVector) -> None:
        """Persist user preference vector to database for future use."""

        try:
            # Store in a user_preferences table (would need to be created)
            vector_data = {
                "user_id": user_vector.user_id,
                "embedding_vector": user_vector.embedding_vector.tolist(),  # Convert to list for JSON
                "confidence_score": user_vector.confidence_score,
                "category_weights": user_vector.category_weights,
                "temporal_weights": user_vector.temporal_weights,
                "interaction_count": user_vector.interaction_count,
                "vector_hash": user_vector.vector_hash,
                "last_updated": user_vector.last_updated.isoformat(),
                "source_queries": user_vector.source_queries[
                    :5
                ],  # Store sample queries
            }

            # For now, we'll skip actual database storage since the table doesn't exist
            # In production, you'd upsert into a user_preferences table
            logger.debug(
                f"User vector computed for {user_vector.user_id} (persistence skipped)"
            )

        except Exception as e:
            logger.error(f"Error persisting user vector for {user_vector.user_id}: {e}")

    async def update_user_preferences_from_interaction(
        self,
        user_id: str,
        interaction_data: Dict[str, Any],
        learning_rate: Optional[float] = None,
    ) -> bool:
        """
        Update user preferences based on new interaction (continuous learning).

        Args:
            user_id: User identifier
            interaction_data: New interaction data
            learning_rate: Custom learning rate (default: use instance setting)

        Returns:
            True if preferences were updated, False otherwise
        """

        if user_id not in self.user_vectors:
            # No existing vector, need to learn from scratch
            await self.learn_user_preferences(user_id)
            return True

        current_vector = self.user_vectors[user_id]
        query = interaction_data.get("query", "").strip()

        if not query or len(query) < 3:
            return False

        try:
            # Get embedding for new query
            embedding_list = await generate_vertex_embedding_async(query)
            query_embedding = np.array(embedding_list) if embedding_list else None
            if query_embedding is None:
                return False

            # Update preference vector using exponential moving average
            lr = learning_rate or self.learning_rate

            # Normalize new query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)

            # Update embedding with learning rate
            updated_embedding = (
                1 - lr
            ) * current_vector.embedding_vector + lr * query_embedding
            updated_embedding = updated_embedding / np.linalg.norm(updated_embedding)

            # Update vector
            current_vector.embedding_vector = updated_embedding
            current_vector.interaction_count += 1
            current_vector.last_updated = datetime.now()
            current_vector.vector_hash = current_vector._compute_vector_hash()

            # Add query to source queries (keep recent ones)
            current_vector.source_queries.append(query)
            current_vector.source_queries = current_vector.source_queries[-10:]

            logger.debug(f"Updated preferences for user {user_id} with new interaction")
            return True

        except Exception as e:
            logger.error(f"Error updating user preferences for {user_id}: {e}")
            return False

    async def get_similar_users(
        self, user_id: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find users with similar preferences for collaborative filtering.

        Args:
            user_id: Target user ID
            top_k: Number of similar users to return

        Returns:
            List of (user_id, similarity_score) tuples
        """

        if user_id not in self.user_vectors:
            return []

        target_vector = self.user_vectors[user_id]
        similarities = []

        for other_user_id, other_vector in self.user_vectors.items():
            if other_user_id == user_id:
                continue

            # Only consider users with sufficient confidence
            if other_vector.confidence_score < self.confidence_threshold:
                continue

            # Compute cosine similarity
            similarity = np.dot(
                target_vector.embedding_vector, other_vector.embedding_vector
            )

            # Weight by confidence scores
            weighted_similarity = similarity * min(
                target_vector.confidence_score, other_vector.confidence_score
            )

            similarities.append((other_user_id, weighted_similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_preference_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user preferences for debugging/analysis."""

        if user_id not in self.user_vectors:
            return {"error": "User preferences not found"}

        vector = self.user_vectors[user_id]

        return {
            "user_id": user_id,
            "confidence_score": vector.confidence_score,
            "interaction_count": vector.interaction_count,
            "top_categories": dict(
                sorted(
                    vector.category_weights.items(), key=lambda x: x[1], reverse=True
                )[:5]
            ),
            "temporal_patterns": vector.temporal_weights,
            "recent_queries": vector.source_queries[-5:],
            "vector_hash": vector.vector_hash,
            "last_updated": vector.last_updated.isoformat(),
        }
