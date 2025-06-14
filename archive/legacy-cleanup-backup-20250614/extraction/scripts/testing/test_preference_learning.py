#!/usr/bin/env python3

import asyncio
import json
import sys
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.preference_learner import UserPreferenceLearner


async def test_preference_learning():
    """Test the user preference learning system."""

    print("🧠 Testing User Preference Learning System")
    print("=" * 50)

    # Initialize the learner
    learner = UserPreferenceLearner()

    # Get sample users from the database with interaction counts
    print("\n1. 📊 Loading User Data...")
    usage_response = (
        learner.supabase.table("usage_tracking").select("user_id").execute()
    )

    # Count interactions per user
    from collections import Counter

    user_interaction_counts = Counter(
        [item["user_id"] for item in usage_response.data if item.get("user_id")]
    )

    # Sort users by interaction count (descending)
    user_ids = [user_id for user_id, count in user_interaction_counts.most_common()]

    print(f"Found {len(user_ids)} unique users")
    print(f"Top users by interactions: {list(user_interaction_counts.most_common(5))}")

    # Temporarily lower the threshold for testing
    learner.min_queries_for_learning = 2

    # Test preference learning for multiple users
    print("\n2. 🎯 Learning User Preferences...")
    learned_users = []

    for i, user_id in enumerate(user_ids[:5]):  # Test first 5 users
        print(
            f"   Learning preferences for user {i+1}/{min(5, len(user_ids))}: {user_id}"
        )

        try:
            user_vector = await learner.learn_user_preferences(user_id)
            if user_vector:
                learned_users.append(user_id)
                print(
                    f"   ✅ Learned preferences (confidence: {user_vector.confidence_score:.3f})"
                )

                # Get insights
                insights = learner.get_preference_insights(user_id)
                if insights.get("top_categories"):
                    top_cats = list(insights["top_categories"].keys())[:3]
                    print(f"      Top categories: {top_cats}")
            else:
                print("   ❌ Insufficient data for learning")
        except Exception as e:
            print(f"   ⚠️ Error learning preferences: {e}")

    print(f"\n✅ Successfully learned preferences for {len(learned_users)} users")

    # Test similarity computation
    if len(learned_users) >= 2:
        print("\n3. 👥 Testing User Similarity...")
        test_user = learned_users[0]
        similar_users = await learner.get_similar_users(test_user, top_k=3)

        print(f"   Users similar to {test_user}:")
        for similar_user, similarity in similar_users:
            print(f"      {similar_user}: {similarity:.3f}")

    # Test continuous learning
    if learned_users:
        print("\n4. 🔄 Testing Continuous Learning...")
        test_user = learned_users[0]

        # Simulate new interaction
        new_interaction = {
            "query": "ethereum defi yield farming workshop",
            "query_type": "event_query",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
        }

        print(f"   Updating preferences for {test_user} with new interaction...")
        updated = await learner.update_user_preferences_from_interaction(
            test_user, new_interaction
        )

        if updated:
            print("   ✅ Preferences updated successfully")
            insights_after = learner.get_preference_insights(test_user)
            print(
                f"      New confidence: {insights_after.get('confidence_score', 0):.3f}"
            )
        else:
            print("   ❌ Failed to update preferences")

    # Generate detailed insights for analysis
    print("\n5. 📈 Generating Insights...")
    insights_data = {}

    for user_id in learned_users[:3]:  # Detailed insights for first 3 users
        insights = learner.get_preference_insights(user_id)
        insights_data[user_id] = insights

        print(f"\n   User: {user_id}")
        print(f"   Confidence: {insights.get('confidence_score', 0):.3f}")
        print(f"   Interactions: {insights.get('interaction_count', 0)}")

        top_cats = insights.get("top_categories", {})
        if top_cats:
            print(f"   Top categories: {list(top_cats.items())[:3]}")

        temporal = insights.get("temporal_patterns", {})
        if temporal:
            print(f"   Usage patterns: {temporal}")

    # Save test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "total_users_tested": len(user_ids[:5]),
        "successful_learning": len(learned_users),
        "user_insights": insights_data,
        "cache_stats": {
            "cached_embeddings": len(learner.query_embeddings_cache),
            "learned_vectors": len(learner.user_vectors),
        },
    }

    output_file = (
        f"preference_learning_test_results_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ Preference Learning System test completed!")


if __name__ == "__main__":
    asyncio.run(test_preference_learning())
