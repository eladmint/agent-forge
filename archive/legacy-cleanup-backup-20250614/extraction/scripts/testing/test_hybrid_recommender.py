#!/usr/bin/env python3

import asyncio
import json
import sys
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.hybrid_recommender import HybridRecommenderSystem, HybridSystemConfig


async def test_hybrid_recommender():
    """Test the hybrid recommendation system."""

    print("🚀 Testing Hybrid Recommendation System")
    print("=" * 50)

    # Initialize the hybrid system
    config = HybridSystemConfig(
        content_weight=0.4,
        collaborative_weight=0.3,
        semantic_weight=0.2,
        popularity_weight=0.1,
    )

    hybrid_system = HybridRecommenderSystem(config)

    # Initialize all engines
    print("\n1. 🔧 Initializing Recommendation Engines...")
    start_time = datetime.now()
    await hybrid_system.initialize_engines()
    init_time = (datetime.now() - start_time).total_seconds()

    print(f"   ✅ All engines initialized in {init_time:.2f} seconds")

    # Get system insights
    print("\n2. 📊 System Status and Insights...")
    insights = hybrid_system.get_system_insights()

    print(f"   Engines initialized: {insights['engines_initialized']}")
    print(f"   Configuration: {insights['configuration']}")
    print("   Engine status:")
    for engine, status in insights["engines_status"].items():
        print(f"      {engine}: {status}")

    # Find users with sufficient data
    print("\n3. 👥 Finding Test Users...")

    usage_response = (
        hybrid_system.supabase.table("usage_tracking").select("user_id").execute()
    )
    from collections import Counter

    user_interaction_counts = Counter(
        [item["user_id"] for item in usage_response.data if item.get("user_id")]
    )
    test_users = [
        user_id
        for user_id, count in user_interaction_counts.most_common(3)
        if count >= 2
    ]

    print(f"   Found {len(test_users)} users for testing: {test_users}")

    if not test_users:
        print("   ❌ No users with sufficient data found")
        test_users = ["test_hybrid_user"]  # Use a dummy user for basic testing

    # Test hybrid recommendations for each user
    print("\n4. 🎯 Testing Hybrid Recommendations...")

    for i, user_id in enumerate(test_users, 1):
        print(f"\n   Testing User {i}: {user_id}")

        # Test without query (preference-based)
        print("      Preference-based recommendations:")
        pref_recs = await hybrid_system.get_hybrid_recommendations(
            user_id=user_id, num_recommendations=5
        )

        if pref_recs:
            for j, rec in enumerate(pref_recs, 1):
                print(f"         {j}. {rec.event_name[:40]}...")
                print(
                    f"            Score: {rec.final_score:.3f} | Confidence: {rec.confidence:.3f}"
                )
                print(f"            Approaches: {rec.approaches_used}")
                print(
                    f"            Individual scores: Content={rec.content_score:.3f}, Collab={rec.collaborative_score:.3f}"
                )
                print(f"            {rec.explanation}")
                print()
        else:
            print("         No preference-based recommendations generated")

        # Test with query
        print("      Query-based recommendations (ethereum blockchain):")
        query_recs = await hybrid_system.get_hybrid_recommendations(
            user_id=user_id,
            query="ethereum blockchain conference",
            num_recommendations=3,
        )

        if query_recs:
            for j, rec in enumerate(query_recs, 1):
                print(f"         {j}. {rec.event_name[:40]}...")
                print(
                    f"            Final: {rec.final_score:.3f} | Approaches: {rec.approaches_used}"
                )
                print(
                    f"            Detailed: {rec.detailed_scores.get('individual_scores', {})}"
                )
        else:
            print("         No query-based recommendations generated")

        # Evaluate recommendation quality
        if pref_recs:
            print("      Quality evaluation:")
            quality = await hybrid_system.evaluate_recommendation_quality(
                user_id, pref_recs
            )

            print(
                f"         Approach distribution: {quality.get('approach_distribution', {})}"
            )
            print(
                f"         Score range: {quality['score_statistics']['min']:.3f} - {quality['score_statistics']['max']:.3f}"
            )
            print(
                f"         Diversity ratio: {quality['diversity_metrics']['diversity_ratio']:.3f}"
            )
            print(
                f"         Multi-approach recs: {quality.get('multi_approach_recommendations', 0)}"
            )

    # Test custom weighting
    print("\n5. ⚖️ Testing Custom Weight Configurations...")

    if test_users:
        test_user = test_users[0]

        # Test content-heavy weighting
        print("   Content-heavy weighting (0.7, 0.2, 0.1, 0.0):")
        content_heavy_recs = await hybrid_system.get_hybrid_recommendations(
            user_id=test_user,
            query="defi yield farming",
            num_recommendations=3,
            approach_weights={
                "content": 0.7,
                "collaborative": 0.2,
                "semantic": 0.1,
                "popularity": 0.0,
            },
        )

        for rec in content_heavy_recs:
            print(
                f"      {rec.event_name[:30]}... | Score: {rec.final_score:.3f} | {rec.approaches_used}"
            )

        # Test collaborative-heavy weighting
        print("\n   Collaborative-heavy weighting (0.1, 0.7, 0.1, 0.1):")
        collab_heavy_recs = await hybrid_system.get_hybrid_recommendations(
            user_id=test_user,
            query="AI conference",
            num_recommendations=3,
            approach_weights={
                "content": 0.1,
                "collaborative": 0.7,
                "semantic": 0.1,
                "popularity": 0.1,
            },
        )

        for rec in collab_heavy_recs:
            print(
                f"      {rec.event_name[:30]}... | Score: {rec.final_score:.3f} | {rec.approaches_used}"
            )

    # Test performance analysis
    print("\n6. ⚡ Performance Analysis...")

    if test_users:
        # Batch processing test
        start_time = datetime.now()
        batch_results = []

        for user_id in test_users:
            recs = await hybrid_system.get_hybrid_recommendations(
                user_id=user_id, query="blockchain", num_recommendations=5
            )
            batch_results.append((user_id, len(recs)))

        batch_time = (datetime.now() - start_time).total_seconds()

        print(f"   Processed {len(test_users)} users in {batch_time:.2f} seconds")
        print(f"   Average time per user: {batch_time / len(test_users):.3f} seconds")
        print(f"   Batch results: {batch_results}")

        # Memory usage approximation
        total_events = len(hybrid_system.content_filter.event_features)
        total_users = len(hybrid_system.collaborative_engine.user_index_map)
        print(
            f"   System scale: {total_events} events, {total_users} users in collaborative matrix"
        )

    # Test edge cases
    print("\n7. 🧪 Testing Edge Cases...")

    # New user with no history
    print("   Testing new user with no interaction history:")
    new_user_recs = await hybrid_system.get_hybrid_recommendations(
        user_id="brand_new_user_12345", query="web3 gaming", num_recommendations=3
    )

    if new_user_recs:
        print(f"      Generated {len(new_user_recs)} recommendations for new user")
        for rec in new_user_recs:
            print(
                f"         {rec.event_name[:30]}... | Approaches: {rec.approaches_used}"
            )
    else:
        print("      No recommendations for new user (expected)")

    # Empty query test
    print("\n   Testing with empty query:")
    empty_query_recs = await hybrid_system.get_hybrid_recommendations(
        user_id=test_users[0] if test_users else "test_user",
        query="",
        num_recommendations=2,
    )

    if empty_query_recs:
        print(
            f"      Generated {len(empty_query_recs)} recommendations with empty query"
        )
    else:
        print("      No recommendations with empty query")

    # Save comprehensive test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "initialization_time_seconds": init_time,
        "system_insights": insights,
        "test_users": test_users,
        "configuration": {
            "content_weight": config.content_weight,
            "collaborative_weight": config.collaborative_weight,
            "semantic_weight": config.semantic_weight,
            "popularity_weight": config.popularity_weight,
        },
        "performance_metrics": {
            "batch_processing_time": batch_time if "batch_time" in locals() else 0,
            "average_time_per_user": (
                batch_time / len(test_users)
                if "batch_time" in locals() and test_users
                else 0
            ),
        },
        "sample_recommendations": [],
    }

    # Add sample recommendations to results
    if test_users:
        sample_user = test_users[0]
        sample_recs = await hybrid_system.get_hybrid_recommendations(
            user_id=sample_user, query="ethereum defi", num_recommendations=3
        )

        test_results["sample_recommendations"] = [
            {
                "event_name": rec.event_name,
                "category": rec.category,
                "final_score": rec.final_score,
                "confidence": rec.confidence,
                "approaches_used": rec.approaches_used,
                "content_score": rec.content_score,
                "collaborative_score": rec.collaborative_score,
                "semantic_score": rec.semantic_score,
                "explanation": rec.explanation,
            }
            for rec in sample_recs
        ]

        # Add quality evaluation
        if sample_recs:
            quality_eval = await hybrid_system.evaluate_recommendation_quality(
                sample_user, sample_recs
            )
            test_results["quality_evaluation"] = quality_eval

    output_file = (
        f"hybrid_recommender_test_results_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ Hybrid Recommendation System test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_hybrid_recommender())
