#!/usr/bin/env python3

import asyncio
import json
import sys
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.hybrid_recommender import HybridRecommenderSystem, HybridSystemConfig


async def test_hybrid_simple():
    """Simple test of hybrid recommendation system core functionality."""

    print("🚀 Testing Hybrid Recommendation System (Core Functionality)")
    print("=" * 60)

    # Initialize with fast configuration
    config = HybridSystemConfig(
        content_weight=0.4,
        collaborative_weight=0.3,
        semantic_weight=0.2,
        popularity_weight=0.1,
    )

    hybrid_system = HybridRecommenderSystem(config)

    # Test system configuration
    print("\n1. ⚙️ System Configuration...")
    print(f"   Content weight: {config.content_weight}")
    print(f"   Collaborative weight: {config.collaborative_weight}")
    print(f"   Semantic weight: {config.semantic_weight}")
    print(f"   Popularity weight: {config.popularity_weight}")

    # Initialize engines (limited scope)
    print("\n2. 🔧 Quick Engine Initialization...")

    try:
        # Initialize just the essential components
        await hybrid_system._initialize_content_filter()
        print(
            f"   ✅ Content filter: {len(hybrid_system.content_filter.event_features)} events"
        )

        await hybrid_system.collaborative_engine.load_interaction_data()
        print(
            f"   ✅ Collaborative filter: {len(hybrid_system.collaborative_engine.user_index_map)} users"
        )

        hybrid_system.engines_initialized = True

    except Exception as e:
        print(f"   ⚠️ Partial initialization: {e}")

    # Get system insights
    print("\n3. 📊 System Status...")
    insights = hybrid_system.get_system_insights()

    for key, value in insights.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for subkey, subvalue in value.items():
                print(f"      {subkey}: {subvalue}")
        else:
            print(f"   {key}: {value}")

    # Test basic hybrid recommendation logic
    print("\n4. 🧪 Testing Hybrid Logic...")

    # Create mock recommendation data to test combination logic
    mock_rec_data = {
        "event_name": "Test Ethereum Conference",
        "category": "Conference",
        "approaches": ["content", "collaborative"],
        "scores": {
            "content": type(
                "MockRec",
                (),
                {
                    "final_score": 0.7,
                    "confidence": 0.8,
                    "event_id": "test-event-1",
                    "event_name": "Test Ethereum Conference",
                    "category": "Conference",
                },
            )(),
            "collaborative": type(
                "MockRec",
                (),
                {
                    "score": 0.6,
                    "confidence": 0.7,
                    "similar_users": [("user1", 0.8), ("user2", 0.6)],
                },
            )(),
        },
    }

    weights = {"content": 0.4, "collaborative": 0.3, "semantic": 0.2, "popularity": 0.1}

    # Test hybrid recommendation creation
    hybrid_rec = await hybrid_system._create_hybrid_recommendation(
        "test-event-1", mock_rec_data, weights, "test-user"
    )

    if hybrid_rec:
        print("   ✅ Hybrid recommendation created:")
        print(f"      Event: {hybrid_rec.event_name}")
        print(f"      Content score: {hybrid_rec.content_score:.3f}")
        print(f"      Collaborative score: {hybrid_rec.collaborative_score:.3f}")
        print(f"      Final score: {hybrid_rec.final_score:.3f}")
        print(f"      Confidence: {hybrid_rec.confidence:.3f}")
        print(f"      Approaches: {hybrid_rec.approaches_used}")
        print(f"      Explanation: {hybrid_rec.explanation}")

    # Test diversity application
    print("\n5. 🎨 Testing Diversity Logic...")

    # Create mock recommendations with different categories
    mock_recommendations = [
        type(
            "MockRec",
            (),
            {
                "event_id": f"event-{i}",
                "event_name": f"Event {i}",
                "category": "Conference" if i % 2 == 0 else "Workshop",
                "final_score": 0.9 - i * 0.1,
                "approaches_used": ["content"],
            },
        )()
        for i in range(6)
    ]

    diverse_recs = hybrid_system._apply_diversity(mock_recommendations)

    print(f"   Original order: {[rec.category for rec in mock_recommendations]}")
    print(f"   Diverse order: {[rec.category for rec in diverse_recs]}")

    # Test with real users if available
    print("\n6. 🎯 Testing with Real Data...")

    # Get a user with interactions
    usage_response = (
        hybrid_system.supabase.table("usage_tracking").select("user_id").execute()
    )
    from collections import Counter

    user_counts = Counter(
        [item["user_id"] for item in usage_response.data if item.get("user_id")]
    )

    if user_counts:
        test_user = user_counts.most_common(1)[0][0]
        print(f"   Testing with real user: {test_user}")

        try:
            # Test with very limited scope
            recs = await hybrid_system.get_hybrid_recommendations(
                user_id=test_user,
                num_recommendations=2,
                exclude_interacted=False,  # Don't exclude for testing
            )

            if recs:
                print(f"   ✅ Generated {len(recs)} recommendations:")
                for i, rec in enumerate(recs, 1):
                    print(f"      {i}. {rec.event_name[:30]}...")
                    print(f"         Score: {rec.final_score:.3f}")
                    print(f"         Approaches: {rec.approaches_used}")
            else:
                print("   ❌ No recommendations generated")

        except Exception as e:
            print(f"   ⚠️ Error in real data test: {e}")
    else:
        print("   ❌ No users found for real data testing")

    # Test evaluation metrics
    print("\n7. 📈 Testing Evaluation Metrics...")

    if "mock_recommendations" in locals():
        # Convert mock to proper format
        hybrid_mocks = [
            type(
                "HybridRec",
                (),
                {
                    "event_id": rec.event_id,
                    "event_name": rec.event_name,
                    "category": rec.category,
                    "final_score": rec.final_score,
                    "confidence": 0.7,
                    "approaches_used": rec.approaches_used,
                },
            )()
            for rec in mock_recommendations[:3]
        ]

        try:
            quality = await hybrid_system.evaluate_recommendation_quality(
                "test-user", hybrid_mocks
            )

            print("   Quality evaluation:")
            print(
                f"      Total recommendations: {quality.get('total_recommendations', 0)}"
            )
            print(
                f"      Approach distribution: {quality.get('approach_distribution', {})}"
            )
            print(
                f"      Score range: {quality['score_statistics']['min']:.3f} - {quality['score_statistics']['max']:.3f}"
            )
            print(
                f"      Diversity ratio: {quality['diversity_metrics']['diversity_ratio']:.3f}"
            )

        except Exception as e:
            print(f"   ⚠️ Error in quality evaluation: {e}")

    # Save simplified test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "simplified_core_functionality",
        "system_configuration": {
            "content_weight": config.content_weight,
            "collaborative_weight": config.collaborative_weight,
            "semantic_weight": config.semantic_weight,
            "popularity_weight": config.popularity_weight,
        },
        "engines_status": insights.get("engines_status", {}),
        "mock_recommendation_test": {
            "hybrid_score_calculated": (
                hybrid_rec.final_score
                if "hybrid_rec" in locals() and hybrid_rec
                else None
            ),
            "approaches_combined": (
                hybrid_rec.approaches_used
                if "hybrid_rec" in locals() and hybrid_rec
                else None
            ),
        },
        "diversity_test": {
            "original_categories": (
                [rec.category for rec in mock_recommendations]
                if "mock_recommendations" in locals()
                else []
            ),
            "diversified_categories": (
                [rec.category for rec in diverse_recs]
                if "diverse_recs" in locals()
                else []
            ),
        },
        "real_data_test": {
            "user_tested": test_user if "test_user" in locals() else None,
            "recommendations_generated": (
                len(recs) if "recs" in locals() and recs else 0
            ),
        },
    }

    output_file = (
        f"hybrid_recommender_simple_test_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ Hybrid Recommendation System (Core) test completed!")


if __name__ == "__main__":
    asyncio.run(test_hybrid_simple())
