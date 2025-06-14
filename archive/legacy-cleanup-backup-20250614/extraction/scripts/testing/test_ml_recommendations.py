#!/usr/bin/env python3

import sys
import asyncio
import json
from datetime import datetime

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.ml.recommendation_engine import MLRecommendationEngine


async def test_recommendation_engine():
    """Test the ML recommendation engine functionality."""

    print("🧠 Testing ML Recommendation Engine")
    print("=" * 50)

    # Initialize the engine
    engine = MLRecommendationEngine()

    # Load user profiles and event data
    print("\n1. 📊 Loading User Profiles...")
    await engine.load_user_profiles()

    print("\n2. 📅 Loading Event Data...")
    await engine.load_event_data()

    # Get metrics
    print("\n3. 📈 System Metrics:")
    metrics = engine.get_recommendation_metrics()
    for key, value in metrics.items():
        print(f"   • {key}: {value}")

    # Test recommendations for different user types
    print("\n4. 🎯 Testing Recommendations:")

    # Test with a user who has profile data
    if engine.user_profiles:
        test_user_id = list(engine.user_profiles.keys())[0]
        print(f"\n   Testing user with profile: {test_user_id}")

        recommendations = await engine.get_recommendations(
            user_id=test_user_id, num_recommendations=5, include_explanation=True
        )

        print(f"   Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"      {i}. {rec.title[:50]}...")
            print(f"         Score: {rec.relevance_score:.3f} | {rec.explanation}")

    # Test with a new user (popularity-based)
    print(f"\n   Testing new user (popularity-based):")
    new_user_recommendations = await engine.get_recommendations(
        user_id="new_user_test", num_recommendations=3, include_explanation=True
    )

    print(f"   Generated {len(new_user_recommendations)} recommendations:")
    for i, rec in enumerate(new_user_recommendations, 1):
        print(f"      {i}. {rec.title[:50]}...")
        print(f"         Score: {rec.relevance_score:.3f} | {rec.explanation}")

    # Test interaction updating
    print("\n5. 🔄 Testing Interaction Updates:")
    if engine.user_profiles:
        test_user = list(engine.user_profiles.keys())[0]
        if engine.event_embeddings:
            test_event = list(engine.event_embeddings.keys())[0]

            print(f"   Updating interaction: user={test_user}, event={test_event}")
            await engine.update_user_interaction(
                user_id=test_user,
                event_id=test_event,
                interaction_type="view",
                interaction_weight=1.0,
            )
            print("   ✅ Interaction updated successfully")

    # Save test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "sample_recommendations": [
            {
                "user_id": test_user_id if engine.user_profiles else "new_user",
                "recommendations": [
                    {
                        "title": rec.title,
                        "relevance_score": rec.relevance_score,
                        "explanation": rec.explanation,
                    }
                    for rec in (
                        recommendations
                        if engine.user_profiles
                        else new_user_recommendations
                    )[:3]
                ],
            }
        ],
    }

    output_file = (
        f"ml_recommendation_test_results_{int(datetime.now().timestamp())}.json"
    )
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2)

    print(f"\n💾 Test results saved to: {output_file}")
    print("\n✅ ML Recommendation Engine test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_recommendation_engine())
