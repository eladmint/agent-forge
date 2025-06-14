#!/usr/bin/env python3

import sys
import asyncio
import json
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.enhanced_content_filtering import EnhancedContentFilter


async def test_enhanced_content_filtering():
    """Test the enhanced content-based filtering system."""

    print("🎯 Testing Enhanced Content-Based Filtering")
    print("=" * 50)

    # Initialize the filter
    filter_engine = EnhancedContentFilter()

    # Load event features
    print("\n1. 📊 Loading Event Features...")
    await filter_engine.load_event_features()

    print(f"   Loaded features for {len(filter_engine.event_features)} events")
    print(f"   Generated embeddings for {len(filter_engine.event_embeddings)} events")

    if not filter_engine.event_features:
        print("❌ No event features loaded - cannot proceed with testing")
        return

    # Sample event analysis
    print("\n2. 📝 Sample Event Analysis:")
    sample_events = list(filter_engine.event_features.items())[:3]

    for event_id, features in sample_events:
        print(f"\n   Event: {features.name[:50]}...")
        print(f"   Category: {features.category}")
        print(f"   Keywords: {features.keywords[:5]}")  # First 5 keywords
        print(f"   Has embedding: {features.embedding is not None}")

        if features.temporal_features:
            print(f"   Temporal: {features.temporal_features}")
        if features.location_features:
            print(f"   Location: {features.location_features}")

    # Test with users who have learned preferences
    print("\n3. 🎯 Testing Personalized Recommendations...")

    # Get users with sufficient interaction data
    usage_response = (
        filter_engine.supabase.table("usage_tracking").select("user_id").execute()
    )
    from collections import Counter

    user_interaction_counts = Counter(
        [item["user_id"] for item in usage_response.data if item.get("user_id")]
    )
    potential_users = [
        user_id
        for user_id, count in user_interaction_counts.most_common(5)
        if count >= 2
    ]

    # Try to learn preferences for these users
    test_users = []
    for user_id in potential_users:
        user_prefs = await filter_engine.preference_learner.learn_user_preferences(
            user_id
        )
        if user_prefs:
            test_users.append(user_id)
            filter_engine.preference_learner.user_vectors[user_id] = user_prefs

    test_users = test_users[:3]  # Limit to 3 users

    if not test_users:
        print("   ❌ No users with learned preferences found")
        print("   Testing with basic content filtering instead...")

        # Test basic content filtering
        test_queries = [
            "ethereum conference blockchain",
            "AI artificial intelligence workshop",
            "defi yield farming meetup",
        ]

        for query in test_queries:
            print(f"\n   Query: '{query}'")
            recommendations = await filter_engine.get_personalized_recommendations(
                user_id="test_basic_user", query=query, num_recommendations=3
            )

            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"      {i}. {rec.event_name[:40]}...")
                    print(f"         Score: {rec.final_score:.3f} | {rec.explanation}")
            else:
                print("      No recommendations generated")
    else:
        # Test personalized recommendations
        for user_id in test_users:
            print(f"\n   Testing user: {user_id}")

            # Get user insights
            insights = filter_engine.preference_learner.get_preference_insights(user_id)
            print(f"   User confidence: {insights.get('confidence_score', 0):.3f}")

            top_categories = insights.get("top_categories", {})
            if top_categories:
                print(f"   Top categories: {list(top_categories.keys())[:3]}")

            # Test without query (preference-based)
            print(f"\n   Preference-based recommendations:")
            pref_recommendations = await filter_engine.get_personalized_recommendations(
                user_id=user_id, num_recommendations=3
            )

            if pref_recommendations:
                for i, rec in enumerate(pref_recommendations, 1):
                    print(f"      {i}. {rec.event_name[:40]}...")
                    print(
                        f"         Score: {rec.final_score:.3f} | Confidence: {rec.confidence:.3f}"
                    )
                    print(f"         Features: {rec.features_used}")
                    print(f"         {rec.explanation}")
            else:
                print("      No preference-based recommendations")

            # Test with query
            print(f"\n   Query + preference recommendations:")
            query_recommendations = (
                await filter_engine.get_personalized_recommendations(
                    user_id=user_id,
                    query="blockchain conference ethereum",
                    num_recommendations=3,
                )
            )

            if query_recommendations:
                for i, rec in enumerate(query_recommendations, 1):
                    print(f"      {i}. {rec.event_name[:40]}...")
                    print(
                        f"         Base: {rec.base_similarity:.3f} | Personal: {rec.personalized_similarity:.3f}"
                    )
                    print(
                        f"         Category boost: {rec.category_boost:.3f} | Temporal: {rec.temporal_boost:.3f}"
                    )
                    print(f"         Final: {rec.final_score:.3f}")

    # Test recommendation insights
    print("\n4. 📈 Recommendation Insights...")

    if test_users:
        test_user = test_users[0]
        sample_recommendations = await filter_engine.get_personalized_recommendations(
            user_id=test_user, query="crypto conference", num_recommendations=5
        )

        if sample_recommendations:
            insights = filter_engine.get_recommendation_insights(sample_recommendations)

            print(f"   Total recommendations: {insights['total_recommendations']}")
            print(f"   Average confidence: {insights['avg_confidence']:.3f}")
            print(
                f"   Score range: {insights['score_stats']['min']:.3f} - {insights['score_stats']['max']:.3f}"
            )
            print(f"   Average score: {insights['score_stats']['avg']:.3f}")
            print(f"   Feature usage: {insights['feature_usage']}")
            print(f"   Category distribution: {insights['category_distribution']}")

    # Test performance analysis
    print("\n5. ⚡ Performance Analysis...")

    # Test batch recommendation generation
    if test_users:
        start_time = datetime.now()

        batch_results = []
        for user_id in test_users:
            recommendations = await filter_engine.get_personalized_recommendations(
                user_id=user_id, query="web3 blockchain", num_recommendations=5
            )
            batch_results.append((user_id, len(recommendations)))

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print(f"   Processed {len(test_users)} users in {processing_time:.2f} seconds")
        print(
            f"   Average time per user: {processing_time / len(test_users):.3f} seconds"
        )
        print(f"   Batch results: {batch_results}")

    # Save test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "system_stats": {
            "total_events": len(filter_engine.event_features),
            "events_with_embeddings": len(filter_engine.event_embeddings),
            "users_with_preferences": len(
                filter_engine.preference_learner.user_vectors
            ),
        },
        "sample_events": [
            {
                "event_id": features.event_id,
                "name": features.name,
                "category": features.category,
                "keywords_count": len(features.keywords),
                "has_embedding": features.embedding is not None,
                "temporal_features": features.temporal_features,
                "location_features": features.location_features,
            }
            for _, features in sample_events
        ],
        "test_users": test_users[:3] if test_users else [],
        "performance": {
            "feature_extraction_completed": True,
            "personalization_enabled": len(test_users) > 0,
        },
    }

    # Add sample recommendations to results
    if test_users:
        sample_user = test_users[0]
        sample_recs = await filter_engine.get_personalized_recommendations(
            user_id=sample_user, query="ethereum defi", num_recommendations=3
        )

        test_results["sample_recommendations"] = [
            {
                "event_name": rec.event_name,
                "category": rec.category,
                "final_score": rec.final_score,
                "confidence": rec.confidence,
                "features_used": rec.features_used,
                "explanation": rec.explanation,
            }
            for rec in sample_recs
        ]

    output_file = f"enhanced_content_filtering_test_results_{int(datetime.now().timestamp())}.json"
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ Enhanced Content Filtering test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_content_filtering())
