#!/usr/bin/env python3

import asyncio
import json
import sys
from datetime import datetime, timedelta

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.training_pipeline import MLTrainingPipeline, ModelExperiment


async def test_training_pipeline():
    """Test the ML training pipeline functionality."""

    print("🔄 Testing ML Training Pipeline")
    print("=" * 40)

    # Initialize training pipeline
    pipeline = MLTrainingPipeline(output_dir="test_ml_models")

    # Test training data collection
    print("\n1. 📊 Testing Training Data Collection...")

    training_samples = await pipeline.collect_training_data(
        days_back=30, min_interactions_per_user=2
    )

    print(f"   Collected {len(training_samples)} training samples")

    if training_samples:
        # Show sample statistics
        unique_users = len(set(sample.user_id for sample in training_samples))
        unique_events = len(set(sample.event_id for sample in training_samples))
        avg_rating = sum(sample.implicit_rating for sample in training_samples) / len(
            training_samples
        )

        print(f"   Unique users: {unique_users}")
        print(f"   Unique events: {unique_events}")
        print(f"   Average implicit rating: {avg_rating:.3f}")

        # Show sample training data
        print("\n   Sample training data:")
        for i, sample in enumerate(training_samples[:3], 1):
            print(f"      {i}. User: {sample.user_id}")
            print(f"         Event: {sample.event_id}")
            print(f"         Rating: {sample.implicit_rating:.3f}")
            print(f"         Context: {list(sample.context_features.keys())}")
            print()
    else:
        print("   ❌ No training samples collected")
        print("   Creating mock samples for testing...")

        # Create mock training samples for testing
        from agent_forge.core.shared.ml.training_pipeline import TrainingDataSample

        mock_samples = [
            TrainingDataSample(
                user_id="test_user_1",
                event_id="test_event_1",
                interaction_type="search_query",
                implicit_rating=0.8,
                timestamp=datetime.now() - timedelta(days=1),
                context_features={
                    "hour_of_day": 14,
                    "day_of_week": 1,
                    "query_length": 3,
                    "has_blockchain_terms": True,
                },
            ),
            TrainingDataSample(
                user_id="test_user_1",
                event_id="test_event_2",
                interaction_type="search_query",
                implicit_rating=0.6,
                timestamp=datetime.now() - timedelta(days=2),
                context_features={
                    "hour_of_day": 10,
                    "day_of_week": 2,
                    "query_length": 2,
                    "has_ai_terms": True,
                },
            ),
            TrainingDataSample(
                user_id="test_user_2",
                event_id="test_event_1",
                interaction_type="search_query",
                implicit_rating=0.9,
                timestamp=datetime.now() - timedelta(days=1),
                context_features={
                    "hour_of_day": 16,
                    "day_of_week": 1,
                    "query_length": 4,
                    "has_blockchain_terms": True,
                },
            ),
        ]

        training_samples = mock_samples
        print(f"   Created {len(mock_samples)} mock training samples")

    # Test experiment configuration
    print("\n2. ⚙️ Testing Experiment Configuration...")

    experiment_configs = [
        ModelExperiment(
            experiment_id="test_collaborative_exp",
            model_config={"type": "collaborative"},
            training_data_period=30,
            validation_split=0.2,
            hyperparameters={"similarity_threshold": 0.1, "min_interactions": 2},
            created_at=datetime.now(),
        ),
        ModelExperiment(
            experiment_id="test_content_exp",
            model_config={"type": "content"},
            training_data_period=30,
            validation_split=0.2,
            hyperparameters={"learning_rate": 0.1, "embedding_dimension": 768},
            created_at=datetime.now(),
        ),
        ModelExperiment(
            experiment_id="test_hybrid_exp",
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
        ),
    ]

    for config in experiment_configs:
        print(f"   Experiment: {config.experiment_id}")
        print(f"      Type: {config.model_config['type']}")
        print(f"      Hyperparameters: {list(config.hyperparameters.keys())}")

    # Test individual components
    print("\n3. 🧪 Testing Training Components...")

    # Test implicit rating computation
    mock_interaction = {
        "query": "ethereum defi conference blockchain",
        "status": "success",
        "processing_time_ms": 1500,
    }

    implicit_rating = pipeline._compute_implicit_rating(
        0.6, "success", mock_interaction
    )
    print(f"   Implicit rating computation: {implicit_rating:.3f}")

    # Test context feature extraction
    mock_event = {
        "name": "Ethereum Developer Conference",
        "category": "Conference",
        "start_time_iso": "2025-07-15T10:00:00Z",
        "location_name": "Convention Center",
    }

    context_features = pipeline._extract_context_features(mock_interaction, mock_event)
    print(f"   Context features extracted: {list(context_features.keys())}")

    # Test query-to-event matching
    events_dict = {
        "event_1": {
            "name": "Ethereum DeFi Summit",
            "description": "Decentralized finance conference",
            "category": "Conference",
        },
        "event_2": {
            "name": "AI Workshop Series",
            "description": "Machine learning and artificial intelligence",
            "category": "Workshop",
        },
    }

    matches = await pipeline._match_query_to_events("ethereum defi", events_dict)
    print(f"   Query matching found {len(matches)} matches:")
    for event_id, score in matches:
        print(f"      {event_id}: {score:.3f}")

    # Test training pipeline summary
    print("\n4. 📈 Testing Pipeline Summary...")

    summary = pipeline.get_training_summary()
    print(f"   Active models: {summary['active_models']}")
    print(f"   Total experiments: {summary['total_experiments']}")
    print(f"   Retraining needed: {summary['retraining_needed']}")

    # Test experiment execution (mock)
    print("\n5. 🔬 Testing Experiment Execution...")

    if len(training_samples) >= 3:  # Need minimum samples
        print("   Running lightweight experiment...")

        # Use a simple experiment to test the pipeline
        test_experiment = ModelExperiment(
            experiment_id="lightweight_test",
            model_config={"type": "collaborative"},
            training_data_period=7,
            validation_split=0.3,
            hyperparameters={"min_interactions": 1},
            created_at=datetime.now(),
        )

        try:
            # Override the collect_training_data method to return our samples
            original_method = pipeline.collect_training_data
            pipeline.collect_training_data = lambda **kwargs: asyncio.create_task(
                asyncio.coroutine(lambda: training_samples)()
            )

            # Run the experiment
            result = await pipeline.run_training_experiment(test_experiment)

            print(f"   ✅ Experiment completed: {result.status}")
            if result.metrics:
                print(f"   Training time: {result.metrics.training_time:.2f}s")
                print(f"   Precision@5: {result.metrics.precision_at_k.get(5, 0):.3f}")
                print(f"   Model size: {result.metrics.model_size} bytes")

            # Restore original method
            pipeline.collect_training_data = original_method

        except Exception as e:
            print(f"   ⚠️ Experiment failed (expected with mock data): {e}")
    else:
        print("   ❌ Insufficient training samples for experiment")

    # Test automated retraining logic
    print("\n6. 🔄 Testing Automated Retraining Logic...")

    should_retrain = pipeline._should_retrain()
    print(f"   Should retrain: {should_retrain}")

    # Test performance tracking
    print("\n7. 📊 Testing Performance Tracking...")

    # Add mock performance history
    pipeline.performance_history = [
        {"precision_at_5": 0.65, "timestamp": datetime.now() - timedelta(days=7)},
        {"precision_at_5": 0.58, "timestamp": datetime.now() - timedelta(days=1)},
    ]

    should_retrain_after_degradation = pipeline._should_retrain()
    print(
        f"   Should retrain after performance degradation: {should_retrain_after_degradation}"
    )

    # Generate final summary
    final_summary = pipeline.get_training_summary()

    # Save test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "training_samples_collected": len(training_samples),
        "unique_users": len(set(sample.user_id for sample in training_samples)),
        "unique_events": len(set(sample.event_id for sample in training_samples)),
        "experiment_configs_tested": len(experiment_configs),
        "pipeline_summary": final_summary,
        "sample_training_data": (
            [
                {
                    "user_id": sample.user_id,
                    "event_id": sample.event_id,
                    "implicit_rating": sample.implicit_rating,
                    "interaction_type": sample.interaction_type,
                    "context_features": sample.context_features,
                }
                for sample in training_samples[:3]
            ]
            if training_samples
            else []
        ),
        "component_tests": {
            "implicit_rating_computed": implicit_rating,
            "context_features_extracted": len(context_features),
            "query_matches_found": len(matches),
            "should_retrain": should_retrain,
            "performance_degradation_detected": should_retrain_after_degradation,
        },
    }

    output_file = (
        f"training_pipeline_test_results_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ ML Training Pipeline test completed!")


if __name__ == "__main__":
    asyncio.run(test_training_pipeline())
