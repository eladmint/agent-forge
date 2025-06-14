#!/usr/bin/env python3

import sys
import asyncio
import json
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.collaborative_filtering import CollaborativeFilteringEngine


async def test_collaborative_filtering():
    """Test the collaborative filtering recommendation system."""

    print("🤝 Testing Collaborative Filtering System")
    print("=" * 50)

    # Initialize the engine
    engine = CollaborativeFilteringEngine()

    # Load interaction data
    print("\n1. 📊 Loading Interaction Data...")
    await engine.load_interaction_data()

    # Get system statistics
    print("\n2. 📈 System Statistics:")
    stats = engine.get_system_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   • {key}: {value:.4f}")
        else:
            print(f"   • {key}: {value}")

    if not engine.user_index_map:
        print("\n❌ Insufficient data for collaborative filtering")
        return

    # Test user similarity computation
    print("\n3. 👥 Computing User Similarities...")
    test_users = list(engine.user_index_map.keys())[:3]  # Test first 3 users

    for user_id in test_users:
        print(f"   Computing similarities for user: {user_id}")
        engine.compute_user_similarities(user_id)

        # Get user interaction summary
        summary = engine.get_user_interaction_summary(user_id)
        print(f"      Interactions: {summary.get('total_interactions', 0)}")
        print(f"      Similar users: {summary.get('similar_users_count', 0)}")

        top_similar = summary.get("top_similar_users", [])
        if top_similar:
            print(
                f"      Top similar: {top_similar[0][0]} (score: {top_similar[0][1]:.3f})"
            )

    # Test collaborative recommendations
    print("\n4. 🎯 Testing Collaborative Recommendations...")

    for user_id in test_users:
        print(f"\n   Recommendations for user: {user_id}")

        recommendations = await engine.get_collaborative_recommendations(
            user_id=user_id, num_recommendations=5, exclude_interacted=True
        )

        if recommendations:
            print(f"   Generated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"      {i}. Event {rec.event_id[:8]}...")
                print(
                    f"         Score: {rec.score:.3f} | Confidence: {rec.confidence:.3f}"
                )
                print(f"         Based on {len(rec.similar_users)} similar users")
        else:
            print("   ❌ No recommendations generated")

    # Test detailed analysis for top user
    if test_users:
        print("\n5. 🔍 Detailed Analysis for Top User...")
        top_user = test_users[0]

        summary = engine.get_user_interaction_summary(top_user)
        print(f"\n   User: {top_user}")
        print(f"   Total interactions: {summary.get('total_interactions', 0)}")
        print(f"   Unique events: {summary.get('unique_events', 0)}")
        print(f"   Average weight: {summary.get('avg_weight', 0):.3f}")
        print(f"   Interaction types: {summary.get('interaction_types', [])}")

        date_range = summary.get("date_range", {})
        if date_range:
            print(
                f"   Date range: {date_range.get('earliest', '')[:10]} to {date_range.get('latest', '')[:10]}"
            )

        similar_users = summary.get("top_similar_users", [])
        if similar_users:
            print(f"   Top 3 similar users:")
            for user, score in similar_users[:3]:
                print(f"      {user}: {score:.3f}")

    # Test system performance metrics
    print("\n6. ⚡ Performance Metrics...")

    if engine.user_item_sparse is not None:
        print(f"   Sparse matrix shape: {engine.user_item_sparse.shape}")
        print(f"   Non-zero elements: {engine.user_item_sparse.nnz}")
        print(
            f"   Memory efficiency: {engine.user_item_sparse.nnz / (engine.user_item_sparse.shape[0] * engine.user_item_sparse.shape[1]):.6f}"
        )

    # Save test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "system_stats": stats,
        "test_users": test_users[:3],
        "user_summaries": {
            user_id: engine.get_user_interaction_summary(user_id)
            for user_id in test_users[:3]
        },
        "sample_recommendations": [],
    }

    # Get sample recommendations for saving
    for user_id in test_users[:2]:
        recommendations = await engine.get_collaborative_recommendations(
            user_id, num_recommendations=3
        )
        test_results["sample_recommendations"].append(
            {
                "user_id": user_id,
                "recommendations": [
                    {
                        "event_id": rec.event_id,
                        "score": rec.score,
                        "confidence": rec.confidence,
                        "interaction_count": rec.interaction_count,
                    }
                    for rec in recommendations
                ],
            }
        )

    output_file = (
        f"collaborative_filtering_test_results_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ Collaborative Filtering test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_collaborative_filtering())
