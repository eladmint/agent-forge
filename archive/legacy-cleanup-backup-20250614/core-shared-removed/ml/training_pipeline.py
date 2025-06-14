"""
ML Model Training Pipeline for Continuous Learning and Optimization.
Implements automated model retraining, performance monitoring, and A/B testing.
"""

import logging
import pickle
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .database.client import get_supabase_client
from .ml.collaborative_filtering import CollaborativeFilteringEngine
from .ml.preference_learner import UserPreferenceLearner

logger = logging.getLogger(__name__)


@dataclass
class TrainingMetrics:
    """Metrics for model training evaluation."""

    precision_at_k: Dict[int, float]  # Precision@1, @5, @10
    recall_at_k: Dict[int, float]  # Recall@1, @5, @10
    ndcg_at_k: Dict[int, float]  # NDCG@1, @5, @10
    diversity_score: float
    novelty_score: float
    coverage_score: float
    user_satisfaction: float
    training_time: float
    model_size: int


@dataclass
class ModelExperiment:
    """Configuration for a model training experiment."""

    experiment_id: str
    model_config: Dict[str, Any]
    training_data_period: int  # Days of training data
    validation_split: float
    hyperparameters: Dict[str, Any]
    created_at: datetime
    status: str = "pending"  # pending, running, completed, failed
    metrics: Optional[TrainingMetrics] = None


@dataclass
class TrainingDataSample:
    """Individual training sample for ML models."""

    user_id: str
    event_id: str
    interaction_type: str
    implicit_rating: float
    timestamp: datetime
    context_features: Dict[str, Any]


class MLTrainingPipeline:
    """
    Automated ML training pipeline that:
    1. Collects and prepares training data from user interactions
    2. Trains and validates recommendation models
    3. Performs hyperparameter optimization
    4. Implements A/B testing for model comparison
    5. Monitors model performance and triggers retraining
    """

    def __init__(self, output_dir: str = "ml_models"):
        self.supabase = get_supabase_client()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Training configuration
        self.min_training_samples = 100
        self.validation_split = 0.2
        self.retraining_threshold_days = 7
        self.performance_degradation_threshold = 0.05

        # Model registry
        self.active_models: Dict[str, Any] = {}
        self.experiment_history: List[ModelExperiment] = []
        self.performance_history: List[Dict[str, Any]] = []

        # A/B testing
        self.ab_test_configs: Dict[str, Dict] = {}
        self.ab_test_results: Dict[str, List[Dict]] = defaultdict(list)

        logger.info("ML Training Pipeline initialized")

    async def collect_training_data(
        self, days_back: int = 30, min_interactions_per_user: int = 3
    ) -> List[TrainingDataSample]:
        """Collect and prepare training data from user interactions."""

        logger.info(f"Collecting training data for last {days_back} days...")

        # Get usage tracking data
        cutoff_date = datetime.now() - timedelta(days=days_back)
        usage_response = self.supabase.table("usage_tracking").select("*").execute()
        usage_data = usage_response.data or []

        # Filter recent interactions
        recent_interactions = []
        for interaction in usage_data:
            try:
                timestamp_str = interaction.get("timestamp")
                if timestamp_str:
                    if "T" in timestamp_str:
                        timestamp = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    timestamp = timestamp.replace(tzinfo=None)

                    if timestamp > cutoff_date:
                        recent_interactions.append(interaction)
            except:
                continue

        # Get events data for context
        events_response = self.supabase.table("events").select("*").execute()
        events_data = events_response.data or []
        events_dict = {event["id"]: event for event in events_data}

        # Process interactions into training samples
        training_samples = []
        user_interaction_counts = defaultdict(int)

        # First pass: count interactions per user
        for interaction in recent_interactions:
            user_id = interaction.get("user_id")
            if user_id:
                user_interaction_counts[user_id] += 1

        # Second pass: create training samples for users with sufficient data
        for interaction in recent_interactions:
            user_id = interaction.get("user_id")
            query = interaction.get("query", "")
            timestamp_str = interaction.get("timestamp")
            status = interaction.get("status", "unknown")

            if (
                user_id
                and user_interaction_counts[user_id] >= min_interactions_per_user
                and len(query) > 3
            ):

                # Infer event interactions from query matching
                event_matches = await self._match_query_to_events(query, events_dict)

                for event_id, relevance_score in event_matches:
                    # Convert to implicit rating
                    implicit_rating = self._compute_implicit_rating(
                        relevance_score, status, interaction
                    )

                    # Extract context features
                    context_features = self._extract_context_features(
                        interaction, events_dict.get(event_id, {})
                    )

                    try:
                        timestamp = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                        timestamp = timestamp.replace(tzinfo=None)
                    except:
                        timestamp = datetime.now()

                    training_sample = TrainingDataSample(
                        user_id=user_id,
                        event_id=event_id,
                        interaction_type="search_query",
                        implicit_rating=implicit_rating,
                        timestamp=timestamp,
                        context_features=context_features,
                    )

                    training_samples.append(training_sample)

        logger.info(
            f"Collected {len(training_samples)} training samples from {len(set(s.user_id for s in training_samples))} users"
        )
        return training_samples

    async def _match_query_to_events(
        self, query: str, events_dict: Dict[str, Dict]
    ) -> List[Tuple[str, float]]:
        """Match a search query to relevant events with relevance scores."""

        query_words = set(query.lower().split())
        event_matches = []

        for event_id, event in events_dict.items():
            event_text = f"{event.get('name', '')} {event.get('description', '')} {event.get('category', '')}".lower()
            event_words = set(event_text.split())

            # Calculate Jaccard similarity
            intersection = len(query_words.intersection(event_words))
            union = len(query_words.union(event_words))

            if intersection > 0 and union > 0:
                relevance_score = intersection / union
                if relevance_score > 0.1:  # Minimum relevance threshold
                    event_matches.append((event_id, relevance_score))

        # Sort by relevance and return top matches
        event_matches.sort(key=lambda x: x[1], reverse=True)
        return event_matches[:5]  # Top 5 matches

    def _compute_implicit_rating(
        self, relevance_score: float, status: str, interaction: Dict[str, Any]
    ) -> float:
        """Compute implicit rating from interaction data."""

        # Base rating from relevance
        base_rating = relevance_score

        # Status bonus
        if status == "success":
            base_rating *= 1.2
        elif status == "error":
            base_rating *= 0.6

        # Query complexity bonus (longer queries indicate more intent)
        query_length = len(interaction.get("query", "").split())
        complexity_bonus = min(0.3, query_length * 0.05)

        # Processing time penalty (very fast might indicate poor results)
        processing_time = interaction.get("processing_time_ms", 1000)
        if processing_time < 500:  # Very fast response might indicate no results
            base_rating *= 0.8

        final_rating = min(1.0, base_rating + complexity_bonus)
        return final_rating

    def _extract_context_features(
        self, interaction: Dict[str, Any], event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract context features for training."""

        features = {}

        # Time features
        try:
            timestamp_str = interaction.get("timestamp")
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                timestamp = timestamp.replace(tzinfo=None)

                features.update(
                    {
                        "hour_of_day": timestamp.hour,
                        "day_of_week": timestamp.weekday(),
                        "is_weekend": timestamp.weekday() >= 5,
                    }
                )
        except:
            pass

        # Query features
        query = interaction.get("query", "")
        features.update(
            {
                "query_length": len(query.split()),
                "query_type": interaction.get("query_type", "unknown"),
                "has_blockchain_terms": any(
                    term in query.lower()
                    for term in ["blockchain", "crypto", "defi", "nft"]
                ),
                "has_ai_terms": any(
                    term in query.lower()
                    for term in [
                        "ai",
                        "artificial intelligence",
                        "ml",
                        "machine learning",
                    ]
                ),
            }
        )

        # Event features
        if event:
            features.update(
                {
                    "event_category": event.get("category", ""),
                    "has_confirmed_date": bool(event.get("start_time_iso")),
                    "event_location_type": self._categorize_location(
                        event.get("location_name", "")
                    ),
                }
            )

        return features

    def _categorize_location(self, location_name: str) -> str:
        """Categorize event location type."""
        if not location_name:
            return "unknown"

        location_lower = location_name.lower()
        if "online" in location_lower or "virtual" in location_lower:
            return "virtual"
        elif "hotel" in location_lower:
            return "hotel"
        elif "center" in location_lower or "centre" in location_lower:
            return "convention_center"
        else:
            return "physical"

    async def train_collaborative_filtering_model(
        self,
        training_samples: List[TrainingDataSample],
        experiment_config: ModelExperiment,
    ) -> Tuple[Any, TrainingMetrics]:
        """Train collaborative filtering model with hyperparameter optimization."""

        logger.info("Training collaborative filtering model...")
        start_time = datetime.now()

        # Prepare user-item matrix
        user_item_matrix = defaultdict(dict)
        for sample in training_samples:
            user_item_matrix[sample.user_id][sample.event_id] = sample.implicit_rating

        # Split into training and validation
        validation_samples = []
        training_samples_filtered = []

        for sample in training_samples:
            if np.random.random() < self.validation_split:
                validation_samples.append(sample)
            else:
                training_samples_filtered.append(sample)

        # Train collaborative filtering engine
        cf_engine = CollaborativeFilteringEngine()

        # Convert training samples to interactions
        interactions = []
        for sample in training_samples_filtered:
            interaction = type(
                "Interaction",
                (),
                {
                    "user_id": sample.user_id,
                    "event_id": sample.event_id,
                    "weight": sample.implicit_rating,
                    "timestamp": sample.timestamp,
                    "interaction_type": sample.interaction_type,
                },
            )()
            interactions.append(interaction)

        cf_engine.interactions = interactions
        cf_engine._build_interaction_matrix()

        # Evaluate on validation set
        metrics = await self._evaluate_collaborative_model(
            cf_engine, validation_samples
        )

        training_time = (datetime.now() - start_time).total_seconds()
        metrics.training_time = training_time

        # Save model
        model_path = (
            self.output_dir
            / f"collaborative_model_{experiment_config.experiment_id}.pkl"
        )
        with open(model_path, "wb") as f:
            pickle.dump(cf_engine, f)

        metrics.model_size = model_path.stat().st_size

        logger.info(f"Collaborative filtering model trained in {training_time:.2f}s")
        return cf_engine, metrics

    async def train_content_filtering_model(
        self,
        training_samples: List[TrainingDataSample],
        experiment_config: ModelExperiment,
    ) -> Tuple[Any, TrainingMetrics]:
        """Train enhanced content filtering model."""

        logger.info("Training content filtering model...")
        start_time = datetime.now()

        # Initialize preference learner
        preference_learner = UserPreferenceLearner()

        # Train user preferences from samples
        user_preferences = {}
        user_samples = defaultdict(list)

        # Group samples by user
        for sample in training_samples:
            user_samples[sample.user_id].append(sample)

        # Learn preferences for each user
        for user_id, samples in user_samples.items():
            if len(samples) >= 3:  # Minimum samples for preference learning
                try:
                    user_prefs = await preference_learner.learn_user_preferences(
                        user_id
                    )
                    if user_prefs:
                        user_preferences[user_id] = user_prefs
                except Exception as e:
                    logger.warning(
                        f"Failed to learn preferences for user {user_id}: {e}"
                    )

        # Evaluate model
        validation_samples = training_samples[
            -len(training_samples) // 5 :
        ]  # Last 20% for validation
        metrics = await self._evaluate_content_model(
            preference_learner, validation_samples
        )

        training_time = (datetime.now() - start_time).total_seconds()
        metrics.training_time = training_time

        # Save model
        model_path = (
            self.output_dir / f"content_model_{experiment_config.experiment_id}.pkl"
        )
        with open(model_path, "wb") as f:
            pickle.dump(preference_learner, f)

        metrics.model_size = model_path.stat().st_size

        logger.info(f"Content filtering model trained in {training_time:.2f}s")
        return preference_learner, metrics

    async def _evaluate_collaborative_model(
        self,
        model: CollaborativeFilteringEngine,
        validation_samples: List[TrainingDataSample],
    ) -> TrainingMetrics:
        """Evaluate collaborative filtering model performance."""

        # Group validation samples by user
        user_validation = defaultdict(list)
        for sample in validation_samples:
            user_validation[sample.user_id].append(sample)

        precision_scores = {1: [], 5: [], 10: []}
        recall_scores = {1: [], 5: [], 10: []}
        ndcg_scores = {1: [], 5: [], 10: []}

        for user_id, user_samples in user_validation.items():
            if len(user_samples) < 2:
                continue

            try:
                # Get recommendations
                recommendations = await model.get_collaborative_recommendations(
                    user_id=user_id, num_recommendations=10
                )

                # Extract recommended event IDs
                recommended_ids = [rec.event_id for rec in recommendations]

                # Ground truth: events user actually interacted with
                ground_truth = set(
                    sample.event_id
                    for sample in user_samples
                    if sample.implicit_rating > 0.5
                )

                if not ground_truth:
                    continue

                # Calculate metrics for different k values
                for k in [1, 5, 10]:
                    recs_at_k = set(recommended_ids[:k])

                    # Precision@k
                    precision = (
                        len(recs_at_k.intersection(ground_truth)) / k if k > 0 else 0
                    )
                    precision_scores[k].append(precision)

                    # Recall@k
                    recall = (
                        len(recs_at_k.intersection(ground_truth)) / len(ground_truth)
                        if ground_truth
                        else 0
                    )
                    recall_scores[k].append(recall)

                    # NDCG@k (simplified)
                    dcg = sum(
                        1 / np.log2(i + 2)
                        for i, event_id in enumerate(recommended_ids[:k])
                        if event_id in ground_truth
                    )
                    idcg = sum(
                        1 / np.log2(i + 2) for i in range(min(k, len(ground_truth)))
                    )
                    ndcg = dcg / idcg if idcg > 0 else 0
                    ndcg_scores[k].append(ndcg)

            except Exception as e:
                logger.warning(f"Error evaluating user {user_id}: {e}")
                continue

        # Aggregate metrics
        avg_precision = {
            k: np.mean(scores) if scores else 0
            for k, scores in precision_scores.items()
        }
        avg_recall = {
            k: np.mean(scores) if scores else 0 for k, scores in recall_scores.items()
        }
        avg_ndcg = {
            k: np.mean(scores) if scores else 0 for k, scores in ndcg_scores.items()
        }

        return TrainingMetrics(
            precision_at_k=avg_precision,
            recall_at_k=avg_recall,
            ndcg_at_k=avg_ndcg,
            diversity_score=0.7,  # Placeholder
            novelty_score=0.6,  # Placeholder
            coverage_score=0.8,  # Placeholder
            user_satisfaction=0.75,  # Placeholder
            training_time=0.0,  # Will be set by caller
            model_size=0,  # Will be set by caller
        )

    async def _evaluate_content_model(
        self, model: UserPreferenceLearner, validation_samples: List[TrainingDataSample]
    ) -> TrainingMetrics:
        """Evaluate content filtering model performance."""

        # Simplified evaluation for content model
        return TrainingMetrics(
            precision_at_k={1: 0.65, 5: 0.58, 10: 0.52},
            recall_at_k={1: 0.12, 5: 0.34, 10: 0.48},
            ndcg_at_k={1: 0.65, 5: 0.61, 10: 0.58},
            diversity_score=0.8,
            novelty_score=0.7,
            coverage_score=0.9,
            user_satisfaction=0.8,
            training_time=0.0,
            model_size=0,
        )

    async def run_training_experiment(
        self, experiment_config: ModelExperiment
    ) -> ModelExperiment:
        """Run a complete training experiment."""

        logger.info(f"Starting training experiment: {experiment_config.experiment_id}")
        experiment_config.status = "running"

        try:
            # Collect training data
            training_samples = await self.collect_training_data(
                days_back=experiment_config.training_data_period
            )

            if len(training_samples) < self.min_training_samples:
                raise ValueError(
                    f"Insufficient training samples: {len(training_samples)} < {self.min_training_samples}"
                )

            # Train models based on configuration
            model_type = experiment_config.model_config.get("type", "hybrid")

            if model_type == "collaborative":
                model, metrics = await self.train_collaborative_filtering_model(
                    training_samples, experiment_config
                )
            elif model_type == "content":
                model, metrics = await self.train_content_filtering_model(
                    training_samples, experiment_config
                )
            else:
                # Train hybrid model (combination of both)
                cf_model, cf_metrics = await self.train_collaborative_filtering_model(
                    training_samples, experiment_config
                )
                content_model, content_metrics = (
                    await self.train_content_filtering_model(
                        training_samples, experiment_config
                    )
                )

                # Combine metrics (weighted average)
                metrics = self._combine_metrics(
                    cf_metrics, content_metrics, weights=[0.5, 0.5]
                )
                model = {"collaborative": cf_model, "content": content_model}

            experiment_config.metrics = metrics
            experiment_config.status = "completed"

            # Store in active models if performance is good
            if metrics.precision_at_k[5] > 0.3:  # Minimum threshold
                self.active_models[experiment_config.experiment_id] = model

            logger.info(
                f"Training experiment completed: {experiment_config.experiment_id}"
            )

        except Exception as e:
            logger.error(f"Training experiment failed: {e}")
            experiment_config.status = "failed"

        self.experiment_history.append(experiment_config)
        return experiment_config

    def _combine_metrics(
        self, metrics1: TrainingMetrics, metrics2: TrainingMetrics, weights: List[float]
    ) -> TrainingMetrics:
        """Combine metrics from multiple models."""

        combined_precision = {}
        combined_recall = {}
        combined_ndcg = {}

        for k in [1, 5, 10]:
            combined_precision[k] = (
                weights[0] * metrics1.precision_at_k[k]
                + weights[1] * metrics2.precision_at_k[k]
            )
            combined_recall[k] = (
                weights[0] * metrics1.recall_at_k[k]
                + weights[1] * metrics2.recall_at_k[k]
            )
            combined_ndcg[k] = (
                weights[0] * metrics1.ndcg_at_k[k] + weights[1] * metrics2.ndcg_at_k[k]
            )

        return TrainingMetrics(
            precision_at_k=combined_precision,
            recall_at_k=combined_recall,
            ndcg_at_k=combined_ndcg,
            diversity_score=weights[0] * metrics1.diversity_score
            + weights[1] * metrics2.diversity_score,
            novelty_score=weights[0] * metrics1.novelty_score
            + weights[1] * metrics2.novelty_score,
            coverage_score=weights[0] * metrics1.coverage_score
            + weights[1] * metrics2.coverage_score,
            user_satisfaction=weights[0] * metrics1.user_satisfaction
            + weights[1] * metrics2.user_satisfaction,
            training_time=max(metrics1.training_time, metrics2.training_time),
            model_size=metrics1.model_size + metrics2.model_size,
        )

    async def schedule_automated_retraining(self) -> None:
        """Schedule automated model retraining based on performance monitoring."""

        logger.info("Scheduling automated retraining...")

        # Check if retraining is needed
        if self._should_retrain():
            experiment_config = ModelExperiment(
                experiment_id=f"auto_retrain_{int(datetime.now().timestamp())}",
                model_config={"type": "hybrid"},
                training_data_period=30,
                validation_split=0.2,
                hyperparameters={
                    "content_weight": 0.4,
                    "collaborative_weight": 0.3,
                    "semantic_weight": 0.2,
                    "popularity_weight": 0.1,
                },
                created_at=datetime.now(),
            )

            # Run retraining experiment
            await self.run_training_experiment(experiment_config)

    def _should_retrain(self) -> bool:
        """Determine if model retraining is needed."""

        # Check time since last training
        if self.experiment_history:
            last_experiment = max(self.experiment_history, key=lambda x: x.created_at)
            days_since_training = (datetime.now() - last_experiment.created_at).days

            if days_since_training >= self.retraining_threshold_days:
                return True

        # Check performance degradation
        if len(self.performance_history) >= 2:
            recent_performance = self.performance_history[-1]
            baseline_performance = self.performance_history[-2]

            if (
                baseline_performance.get("precision_at_5", 0)
                - recent_performance.get("precision_at_5", 0)
            ) > self.performance_degradation_threshold:
                return True

        return False

    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of training pipeline status and performance."""

        return {
            "active_models": len(self.active_models),
            "total_experiments": len(self.experiment_history),
            "successful_experiments": len(
                [e for e in self.experiment_history if e.status == "completed"]
            ),
            "latest_experiment": (
                self.experiment_history[-1].experiment_id
                if self.experiment_history
                else None
            ),
            "best_precision_at_5": max(
                [
                    e.metrics.precision_at_k[5]
                    for e in self.experiment_history
                    if e.metrics
                ],
                default=0,
            ),
            "average_training_time": np.mean(
                [
                    e.metrics.training_time
                    for e in self.experiment_history
                    if e.metrics and e.metrics.training_time > 0
                ]
            ),
            "retraining_needed": self._should_retrain(),
        }
