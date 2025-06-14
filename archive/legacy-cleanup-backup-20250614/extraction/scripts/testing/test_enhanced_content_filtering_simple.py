#!/usr/bin/env python3

import asyncio
import json
import sys
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.enhanced_content_filtering import EnhancedContentFilter


async def test_enhanced_content_filtering_simple():
    """Test the enhanced content filtering with limited scope."""

    print("🎯 Testing Enhanced Content-Based Filtering (Simplified)")
    print("=" * 60)

    # Initialize the filter
    filter_engine = EnhancedContentFilter()

    # Test event feature extraction on a small sample
    print("\n1. 📊 Testing Event Feature Extraction...")

    # Get a small sample of events
    events_response = (
        filter_engine.supabase.table("events").select("*").limit(5).execute()
    )
    events_data = events_response.data or []

    print(f"   Testing with {len(events_data)} sample events")

    # Extract features for sample events
    sample_features = []
    for event in events_data:
        features = await filter_engine._extract_event_features(event)
        if features:
            sample_features.append(features)
            print(f"\n   Event: {features.name[:40]}...")
            print(f"   Category: {features.category}")
            print(f"   Keywords ({len(features.keywords)}): {features.keywords[:5]}")
            print(f"   Has embedding: {features.embedding is not None}")

            if features.temporal_features:
                print(f"   Temporal: {features.temporal_features}")
            if features.location_features:
                print(f"   Location: {features.location_features}")

    # Manually add sample features to the engine
    for features in sample_features:
        filter_engine.event_features[features.event_id] = features
        if features.embedding is not None:
            filter_engine.event_embeddings[features.event_id] = features.embedding

    print(f"\n   Successfully processed {len(sample_features)} events")

    # Test user preference integration
    print("\n2. 🎯 Testing User Preference Integration...")

    # Get a user with interactions
    usage_response = (
        filter_engine.supabase.table("usage_tracking").select("user_id").execute()
    )
    from collections import Counter

    user_interaction_counts = Counter(
        [item["user_id"] for item in usage_response.data if item.get("user_id")]
    )
    top_user = (
        user_interaction_counts.most_common(1)[0][0]
        if user_interaction_counts
        else None
    )

    if top_user:
        print(f"   Testing with user: {top_user}")

        # Learn user preferences
        user_prefs = await filter_engine.preference_learner.learn_user_preferences(
            top_user
        )

        if user_prefs:
            print(
                f"   ✅ Learned preferences (confidence: {user_prefs.confidence_score:.3f})"
            )
            print(
                f"   Category preferences: {list(user_prefs.category_weights.keys())[:3]}"
            )
            print(f"   Temporal patterns: {list(user_prefs.temporal_weights.keys())}")

            # Store in the filter engine
            filter_engine.preference_learner.user_vectors[top_user] = user_prefs

            # Test personalized scoring
            print("\n   Testing personalized event scoring...")

            for features in sample_features[:3]:  # Test first 3 events
                if features.embedding is not None:
                    recommendation = await filter_engine._score_personalized_event(
                        features, user_prefs, None
                    )

                    if recommendation:
                        print(f"\n      Event: {recommendation.event_name[:30]}...")
                        print(f"      Final score: {recommendation.final_score:.3f}")
                        print(
                            f"      Category boost: {recommendation.category_boost:.3f}"
                        )
                        print(
                            f"      Temporal boost: {recommendation.temporal_boost:.3f}"
                        )
                        print(f"      Features used: {recommendation.features_used}")
                        print(f"      Explanation: {recommendation.explanation}")
        else:
            print(f"   ❌ Could not learn preferences for user {top_user}")
    else:
        print("   ❌ No users found for testing")

    # Test basic content filtering
    print("\n3. 🔍 Testing Basic Content Filtering...")

    test_queries = ["blockchain ethereum", "AI conference", "defi yield"]

    for query in test_queries:
        print(f"\n   Query: '{query}'")

        # Test with basic user (no preferences)
        recommendations = await filter_engine.get_personalized_recommendations(
            user_id="test_basic_user", query=query, num_recommendations=2
        )

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"      {i}. {rec.event_name[:35]}...")
                print(f"         Score: {rec.final_score:.3f} | {rec.explanation}")
        else:
            print("      No recommendations generated")

    # Test recommendation insights
    print("\n4. 📈 Testing Recommendation Insights...")

    if sample_features:
        # Generate some sample recommendations for insights
        sample_recs = await filter_engine.get_personalized_recommendations(
            user_id="test_insights_user",
            query="ethereum blockchain conference",
            num_recommendations=3,
        )

        if sample_recs:
            insights = filter_engine.get_recommendation_insights(sample_recs)

            print(f"   Total recommendations: {insights['total_recommendations']}")
            print(
                f"   Score range: {insights['score_stats']['min']:.3f} - {insights['score_stats']['max']:.3f}"
            )
            print(f"   Average score: {insights['score_stats']['avg']:.3f}")
            print(f"   Feature usage: {insights['feature_usage']}")

            if insights["category_distribution"]:
                print(f"   Categories: {insights['category_distribution']}")

    # Test system configuration
    print("\n5. ⚙️ System Configuration Analysis...")

    print(f"   Semantic weight: {filter_engine.semantic_weight}")
    print(f"   Category weight: {filter_engine.category_weight}")
    print(f"   Temporal weight: {filter_engine.temporal_weight}")
    print(f"   Max category boost: {filter_engine.max_category_boost}")
    print(f"   Max temporal boost: {filter_engine.max_temporal_boost}")
    print(f"   Confidence threshold: {filter_engine.confidence_threshold}")

    # Save test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_scope": "simplified",
        "events_processed": len(sample_features),
        "events_with_embeddings": len(
            [f for f in sample_features if f.embedding is not None]
        ),
        "user_tested": top_user if "top_user" in locals() else None,
        "sample_features": [
            {
                "event_id": f.event_id,
                "name": f.name,
                "category": f.category,
                "keywords_count": len(f.keywords),
                "has_embedding": f.embedding is not None,
                "temporal_features": f.temporal_features,
                "location_features": f.location_features,
            }
            for f in sample_features
        ],
        "system_config": {
            "semantic_weight": filter_engine.semantic_weight,
            "category_weight": filter_engine.category_weight,
            "temporal_weight": filter_engine.temporal_weight,
            "max_category_boost": filter_engine.max_category_boost,
            "max_temporal_boost": filter_engine.max_temporal_boost,
        },
    }

    output_file = (
        f"enhanced_content_filtering_simple_test_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ Enhanced Content Filtering (Simplified) test completed!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_content_filtering_simple())
