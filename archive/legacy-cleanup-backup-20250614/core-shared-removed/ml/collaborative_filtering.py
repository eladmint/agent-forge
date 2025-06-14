"""
Collaborative Filtering implementation for event recommendations.
Uses user-item interaction matrices and similarity computation.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from .database.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class UserItemInteraction:
    """Represents a user's interaction with an event."""

    user_id: str
    event_id: str
    interaction_type: str  # view, click, save, search, etc.
    weight: float
    timestamp: datetime
    implicit_feedback: bool = True


@dataclass
class CollaborativeRecommendation:
    """Recommendation from collaborative filtering."""

    event_id: str
    score: float
    similar_users: List[Tuple[str, float]]  # (user_id, similarity_score)
    interaction_count: int
    confidence: float


class CollaborativeFilteringEngine:
    """
    Collaborative filtering recommendation engine that:
    1. Builds user-item interaction matrices from search/query data
    2. Computes user-user and item-item similarities
    3. Generates recommendations based on similar users' preferences
    4. Handles both explicit and implicit feedback
    """

    def __init__(self):
        self.supabase = get_supabase_client()

        # Interaction data
        self.user_item_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.interactions: List[UserItemInteraction] = []
        self.user_similarities: Dict[Tuple[str, str], float] = {}
        self.item_similarities: Dict[Tuple[str, str], float] = {}

        # Sparse matrices for efficient computation
        self.user_item_sparse: Optional[csr_matrix] = None
        self.user_index_map: Dict[str, int] = {}
        self.item_index_map: Dict[str, int] = {}
        self.index_user_map: Dict[int, str] = {}
        self.index_item_map: Dict[int, str] = {}

        # Configuration
        self.min_interactions_per_user = 2
        self.min_interactions_per_item = 2
        self.similarity_threshold = 0.1
        self.max_similar_users = 20
        self.interaction_decay_days = 30

        logger.info("Collaborative Filtering Engine initialized")

    async def load_interaction_data(self) -> None:
        """Load and process user-item interaction data from various sources."""
        logger.info("Loading user-item interaction data...")

        # Load from usage tracking (implicit feedback from searches)
        await self._load_search_interactions()

        # Load from hypothetical explicit feedback (if available)
        # await self._load_explicit_interactions()

        # Build the interaction matrix
        self._build_interaction_matrix()

        logger.info(f"Loaded {len(self.interactions)} interactions")
        logger.info(
            f"Users: {len(self.user_index_map)}, Items: {len(self.item_index_map)}"
        )

    async def _load_search_interactions(self) -> None:
        """Load implicit interactions from search/query data."""

        # Get usage tracking data
        usage_response = self.supabase.table("usage_tracking").select("*").execute()
        usage_data = usage_response.data or []

        # Get events data to map queries to events
        events_response = (
            self.supabase.table("events").select("id, name, category").execute()
        )
        events_data = events_response.data or []

        # Create event lookup by name keywords
        event_keywords = {}
        for event in events_data:
            name = event.get("name", "").lower()
            category = (
                event.get("category", "").lower() if event.get("category") else ""
            )

            # Extract keywords from name and category
            keywords = set()
            if name:
                keywords.update(name.split())
            if category:
                keywords.update(category.split())

            event_keywords[event["id"]] = keywords

        # Process usage data to infer interactions
        for usage_item in usage_data:
            user_id = usage_item.get("user_id")
            query = usage_item.get("query", "").lower()
            timestamp_str = usage_item.get("timestamp")
            status = usage_item.get("status", "unknown")

            if not user_id or not query or len(query) < 3:
                continue

            # Parse timestamp
            try:
                if "T" in timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                else:
                    timestamp = datetime.fromisoformat(timestamp_str)
                timestamp = timestamp.replace(tzinfo=None)
            except:
                timestamp = datetime.now()

            # Find matching events based on query keywords
            query_words = set(query.split())

            for event_id, event_keywords_set in event_keywords.items():
                # Calculate keyword overlap
                overlap = len(query_words.intersection(event_keywords_set))
                if overlap > 0:
                    # Calculate interaction weight
                    weight = self._calculate_interaction_weight(
                        overlap, len(query_words), status, timestamp
                    )

                    if weight > 0.1:  # Minimum threshold
                        interaction = UserItemInteraction(
                            user_id=user_id,
                            event_id=event_id,
                            interaction_type="search_match",
                            weight=weight,
                            timestamp=timestamp,
                            implicit_feedback=True,
                        )
                        self.interactions.append(interaction)

    def _calculate_interaction_weight(
        self, keyword_overlap: int, query_length: int, status: str, timestamp: datetime
    ) -> float:
        """Calculate weight for an implicit interaction."""

        # Base weight from keyword overlap
        base_weight = min(1.0, keyword_overlap / max(1, query_length))

        # Status weight
        status_weight = 1.2 if status == "success" else 0.8

        # Temporal decay
        days_ago = (datetime.now() - timestamp).days
        decay_weight = np.exp(-days_ago / self.interaction_decay_days)

        # Query quality weight (longer queries are more specific)
        quality_weight = min(1.5, 1.0 + (query_length - 2) * 0.1)

        return base_weight * status_weight * decay_weight * quality_weight

    def _build_interaction_matrix(self) -> None:
        """Build sparse user-item interaction matrix."""

        # Filter interactions by minimum thresholds
        user_interaction_counts = defaultdict(int)
        item_interaction_counts = defaultdict(int)

        for interaction in self.interactions:
            user_interaction_counts[interaction.user_id] += 1
            item_interaction_counts[interaction.event_id] += 1

        # Filter users and items with sufficient interactions
        valid_users = {
            user_id
            for user_id, count in user_interaction_counts.items()
            if count >= self.min_interactions_per_user
        }
        valid_items = {
            item_id
            for item_id, count in item_interaction_counts.items()
            if count >= self.min_interactions_per_item
        }

        # Create index mappings
        self.user_index_map = {
            user_id: idx for idx, user_id in enumerate(sorted(valid_users))
        }
        self.item_index_map = {
            item_id: idx for idx, item_id in enumerate(sorted(valid_items))
        }
        self.index_user_map = {
            idx: user_id for user_id, idx in self.user_index_map.items()
        }
        self.index_item_map = {
            idx: item_id for item_id, idx in self.item_index_map.items()
        }

        if not self.user_index_map or not self.item_index_map:
            logger.warning("Insufficient data for collaborative filtering")
            return

        # Build interaction matrix
        n_users = len(self.user_index_map)
        n_items = len(self.item_index_map)

        for interaction in self.interactions:
            if (
                interaction.user_id in self.user_index_map
                and interaction.event_id in self.item_index_map
            ):

                user_idx = self.user_index_map[interaction.user_id]
                item_idx = self.item_index_map[interaction.event_id]

                # Aggregate weights for multiple interactions
                current_weight = self.user_item_matrix[interaction.user_id].get(
                    interaction.event_id, 0
                )
                self.user_item_matrix[interaction.user_id][interaction.event_id] = max(
                    current_weight, interaction.weight
                )

        # Convert to sparse matrix
        row_indices = []
        col_indices = []
        data = []

        for user_id, item_weights in self.user_item_matrix.items():
            if user_id not in self.user_index_map:
                continue
            user_idx = self.user_index_map[user_id]

            for item_id, weight in item_weights.items():
                if item_id not in self.item_index_map:
                    continue
                item_idx = self.item_index_map[item_id]

                row_indices.append(user_idx)
                col_indices.append(item_idx)
                data.append(weight)

        self.user_item_sparse = csr_matrix(
            (data, (row_indices, col_indices)), shape=(n_users, n_items)
        )

        logger.info(f"Built sparse matrix: {n_users} users x {n_items} items")
        logger.info(f"Matrix density: {len(data) / (n_users * n_items):.4f}")

    def compute_user_similarities(self, target_user_id: str = None) -> None:
        """Compute user-user cosine similarities."""

        if self.user_item_sparse is None:
            logger.warning("No interaction matrix available for similarity computation")
            return

        if target_user_id and target_user_id not in self.user_index_map:
            logger.warning(f"User {target_user_id} not found in interaction matrix")
            return

        logger.info("Computing user similarities...")

        # Compute cosine similarities
        similarity_matrix = cosine_similarity(self.user_item_sparse)

        # Store similarities above threshold
        if target_user_id:
            # Compute only for target user
            target_idx = self.user_index_map[target_user_id]
            self._store_similarities_for_user(target_idx, similarity_matrix[target_idx])
        else:
            # Compute for all users (expensive)
            for user_idx in range(similarity_matrix.shape[0]):
                self._store_similarities_for_user(user_idx, similarity_matrix[user_idx])

        logger.info("Computed similarities for users")

    def _store_similarities_for_user(
        self, user_idx: int, similarities: np.ndarray
    ) -> None:
        """Store similarities for a specific user."""

        user_id = self.index_user_map[user_idx]

        # Find similar users above threshold
        similar_indices = np.where(similarities > self.similarity_threshold)[0]

        for similar_idx in similar_indices:
            if similar_idx == user_idx:  # Skip self
                continue

            similar_user_id = self.index_user_map[similar_idx]
            similarity_score = similarities[similar_idx]

            self.user_similarities[(user_id, similar_user_id)] = similarity_score

    async def get_collaborative_recommendations(
        self,
        user_id: str,
        num_recommendations: int = 10,
        exclude_interacted: bool = True,
    ) -> List[CollaborativeRecommendation]:
        """
        Get collaborative filtering recommendations for a user.

        Args:
            user_id: Target user ID
            num_recommendations: Number of recommendations to return
            exclude_interacted: Whether to exclude items user has already interacted with

        Returns:
            List of collaborative recommendations
        """

        if user_id not in self.user_index_map:
            logger.info(f"User {user_id} not found in collaborative filtering data")
            return []

        # Compute similarities for this user if not already done
        if not any(pair[0] == user_id for pair in self.user_similarities.keys()):
            self.compute_user_similarities(user_id)

        # Find similar users
        similar_users = [
            (other_user, score)
            for (u1, other_user), score in self.user_similarities.items()
            if u1 == user_id
        ]

        # Sort by similarity score
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[: self.max_similar_users]

        if not similar_users:
            logger.info(f"No similar users found for {user_id}")
            return []

        # Get items interacted with by target user (for exclusion)
        user_items = set(self.user_item_matrix.get(user_id, {}).keys())

        # Aggregate recommendations from similar users
        item_scores = defaultdict(list)
        item_similar_users = defaultdict(list)

        for similar_user, similarity_score in similar_users:
            similar_user_items = self.user_item_matrix.get(similar_user, {})

            for item_id, interaction_weight in similar_user_items.items():
                if exclude_interacted and item_id in user_items:
                    continue

                # Weight the recommendation by user similarity and interaction strength
                score = similarity_score * interaction_weight
                item_scores[item_id].append(score)
                item_similar_users[item_id].append((similar_user, similarity_score))

        # Calculate final scores and create recommendations
        recommendations = []

        for item_id, scores in item_scores.items():
            # Aggregate scores (mean)
            final_score = np.mean(scores)

            # Calculate confidence based on number of similar users who interacted
            confidence = min(1.0, len(scores) / 5.0)  # Max confidence at 5 users

            recommendation = CollaborativeRecommendation(
                event_id=item_id,
                score=final_score,
                similar_users=item_similar_users[item_id][:3],  # Top 3 similar users
                interaction_count=len(scores),
                confidence=confidence,
            )
            recommendations.append(recommendation)

        # Sort by score and return top N
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:num_recommendations]

    def get_item_recommendations(
        self, item_id: str, num_recommendations: int = 5
    ) -> List[Tuple[str, float]]:
        """Get items similar to a given item (item-item collaborative filtering)."""

        if item_id not in self.item_index_map:
            return []

        # For item-item similarity, we'd need to compute item similarities
        # This is computationally expensive, so for now return empty
        # In production, you'd precompute and cache item similarities
        return []

    def get_user_interaction_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's interactions for debugging."""

        user_interactions = [i for i in self.interactions if i.user_id == user_id]

        if not user_interactions:
            return {"error": "No interactions found"}

        # Group by event
        event_interactions = defaultdict(list)
        for interaction in user_interactions:
            event_interactions[interaction.event_id].append(interaction)

        # Calculate statistics
        total_weight = sum(i.weight for i in user_interactions)
        avg_weight = total_weight / len(user_interactions)

        # Find similar users
        similar_users = [
            (other_user, score)
            for (u1, other_user), score in self.user_similarities.items()
            if u1 == user_id
        ]
        similar_users.sort(key=lambda x: x[1], reverse=True)

        return {
            "user_id": user_id,
            "total_interactions": len(user_interactions),
            "unique_events": len(event_interactions),
            "total_weight": round(total_weight, 3),
            "avg_weight": round(avg_weight, 3),
            "similar_users_count": len(similar_users),
            "top_similar_users": similar_users[:5],
            "interaction_types": list(
                set(i.interaction_type for i in user_interactions)
            ),
            "date_range": {
                "earliest": min(i.timestamp for i in user_interactions).isoformat(),
                "latest": max(i.timestamp for i in user_interactions).isoformat(),
            },
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get collaborative filtering system statistics."""

        return {
            "total_interactions": len(self.interactions),
            "unique_users": len(self.user_index_map),
            "unique_items": len(self.item_index_map),
            "matrix_density": (
                len(
                    [
                        i
                        for user_items in self.user_item_matrix.values()
                        for i in user_items
                    ]
                )
                / (len(self.user_index_map) * len(self.item_index_map))
                if self.user_index_map and self.item_index_map
                else 0
            ),
            "computed_similarities": len(self.user_similarities),
            "avg_interactions_per_user": (
                len(self.interactions) / len(self.user_index_map)
                if self.user_index_map
                else 0
            ),
            "avg_interactions_per_item": (
                len(self.interactions) / len(self.item_index_map)
                if self.item_index_map
                else 0
            ),
        }
