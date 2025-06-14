#!/usr/bin/env python3

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

sys.path.append("/Users/eladm/Projects/token/tokenhunter")

from agent_forge.core.shared.database.client import get_supabase_client


def analyze_user_behavior():
    """Analyze existing user behavior data to understand preferences and usage patterns."""

    supabase = get_supabase_client()

    print("🔍 Analyzing User Behavior Data for ML Recommendations...")
    print("=" * 60)

    # 1. Get usage tracking data
    print("\n1. 📊 Usage Tracking Analysis")
    usage_response = supabase.table("usage_tracking").select("*").execute()
    usage_data = usage_response.data

    print(f"Total tracked interactions: {len(usage_data)}")

    if not usage_data:
        print("❌ No usage data found. Cannot proceed with behavior analysis.")
        return

    # 2. Analyze query patterns
    print("\n2. 🔍 Query Pattern Analysis")
    query_analysis = analyze_query_patterns(usage_data)

    # 3. Analyze user engagement
    print("\n3. 👥 User Engagement Analysis")
    user_analysis = analyze_user_engagement(usage_data)

    # 4. Analyze temporal patterns
    print("\n4. ⏰ Temporal Pattern Analysis")
    temporal_analysis = analyze_temporal_patterns(usage_data)

    # 5. Get event data for content analysis
    print("\n5. 📅 Event Content Analysis")
    events_response = supabase.table("events").select("*").limit(100).execute()
    event_analysis = analyze_event_content(events_response.data)

    # 6. Generate recommendations for ML system design
    print("\n6. 🎯 ML System Recommendations")
    ml_recommendations = generate_ml_recommendations(
        query_analysis, user_analysis, temporal_analysis, event_analysis
    )

    # 7. Save analysis results
    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "total_interactions": len(usage_data),
        "query_analysis": query_analysis,
        "user_analysis": user_analysis,
        "temporal_analysis": temporal_analysis,
        "event_analysis": event_analysis,
        "ml_recommendations": ml_recommendations,
    }

    output_file = f"user_behavior_analysis_{int(datetime.now().timestamp())}.json"
    with open(output_file, "w") as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print(f"\n💾 Analysis saved to: {output_file}")

    return analysis_results


def analyze_query_patterns(usage_data: List[Dict]) -> Dict[str, Any]:
    """Analyze query patterns to understand user search behavior."""

    queries = [item.get("query", "") for item in usage_data if item.get("query")]
    query_types = [item.get("query_type", "unknown") for item in usage_data]

    # Query frequency analysis
    query_counter = Counter(queries)
    type_counter = Counter(query_types)

    # Query length analysis
    query_lengths = [len(q.split()) for q in queries if q]
    avg_query_length = sum(query_lengths) / len(query_lengths) if query_lengths else 0

    # Common terms analysis
    all_terms = []
    for query in queries:
        if query:
            all_terms.extend(query.lower().split())

    common_terms = Counter(all_terms).most_common(20)

    analysis = {
        "total_queries": len(queries),
        "unique_queries": len(set(queries)),
        "avg_query_length": round(avg_query_length, 2),
        "query_type_distribution": dict(type_counter),
        "top_queries": dict(query_counter.most_common(10)),
        "common_terms": dict(common_terms),
        "query_complexity": {
            "short_queries_1_2_words": len([q for q in query_lengths if 1 <= q <= 2]),
            "medium_queries_3_5_words": len([q for q in query_lengths if 3 <= q <= 5]),
            "long_queries_6_plus_words": len([q for q in query_lengths if q >= 6]),
        },
    }

    print(f"   • Total queries: {analysis['total_queries']}")
    print(f"   • Unique queries: {analysis['unique_queries']}")
    print(f"   • Average query length: {analysis['avg_query_length']} words")
    print(f"   • Query types: {list(analysis['query_type_distribution'].keys())}")
    print(f"   • Top terms: {[term for term, _ in common_terms[:5]]}")

    return analysis


def analyze_user_engagement(usage_data: List[Dict]) -> Dict[str, Any]:
    """Analyze user engagement patterns."""

    user_interactions = defaultdict(list)

    for item in usage_data:
        user_id = item.get("user_id", "anonymous")
        timestamp = item.get("timestamp")
        processing_time = item.get("processing_time_ms", 0)
        status = item.get("status", "unknown")

        user_interactions[user_id].append(
            {
                "timestamp": timestamp,
                "processing_time": processing_time,
                "status": status,
                "query": item.get("query", ""),
                "query_type": item.get("query_type", "unknown"),
            }
        )

    # User engagement metrics
    user_counts = {
        user: len(interactions) for user, interactions in user_interactions.items()
    }
    avg_interactions_per_user = (
        sum(user_counts.values()) / len(user_counts) if user_counts else 0
    )

    # Processing time analysis
    processing_times = [
        item.get("processing_time_ms", 0)
        for item in usage_data
        if item.get("processing_time_ms")
    ]
    avg_processing_time = (
        sum(processing_times) / len(processing_times) if processing_times else 0
    )

    # Success rate analysis
    statuses = [item.get("status", "unknown") for item in usage_data]
    status_counter = Counter(statuses)
    success_rate = (
        (status_counter.get("success", 0) / len(statuses)) * 100 if statuses else 0
    )

    analysis = {
        "total_users": len(user_interactions),
        "avg_interactions_per_user": round(avg_interactions_per_user, 2),
        "user_distribution": {
            "single_interaction": len(
                [u for u, count in user_counts.items() if count == 1]
            ),
            "multiple_interactions": len(
                [u for u, count in user_counts.items() if count > 1]
            ),
            "power_users_10_plus": len(
                [u for u, count in user_counts.items() if count >= 10]
            ),
        },
        "engagement_metrics": {
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "success_rate_percent": round(success_rate, 2),
            "status_distribution": dict(status_counter),
        },
        "top_users": dict(Counter(user_counts).most_common(5)),
    }

    print(f"   • Total users: {analysis['total_users']}")
    print(f"   • Avg interactions per user: {analysis['avg_interactions_per_user']}")
    print(
        f"   • Success rate: {analysis['engagement_metrics']['success_rate_percent']}%"
    )
    print(
        f"   • Power users (10+ interactions): {analysis['user_distribution']['power_users_10_plus']}"
    )

    return analysis


def analyze_temporal_patterns(usage_data: List[Dict]) -> Dict[str, Any]:
    """Analyze temporal usage patterns."""

    timestamps = []
    for item in usage_data:
        if item.get("timestamp"):
            try:
                # Handle different timestamp formats
                ts_str = item["timestamp"]
                if "T" in ts_str:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                else:
                    ts = datetime.fromisoformat(ts_str)
                timestamps.append(ts)
            except Exception:
                continue

    if not timestamps:
        return {"error": "No valid timestamps found"}

    # Hour of day analysis
    hours = [ts.hour for ts in timestamps]
    hour_counter = Counter(hours)

    # Day of week analysis
    days = [ts.weekday() for ts in timestamps]  # 0=Monday, 6=Sunday
    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_counter = Counter([day_names[day] for day in days])

    # Recent activity (last 30 days)
    from datetime import timezone

    recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    recent_activity = len(
        [ts for ts in timestamps if ts.replace(tzinfo=timezone.utc) > recent_cutoff]
    )

    analysis = {
        "total_timestamped_interactions": len(timestamps),
        "date_range": {
            "earliest": min(timestamps).isoformat() if timestamps else None,
            "latest": max(timestamps).isoformat() if timestamps else None,
        },
        "hourly_distribution": dict(hour_counter),
        "daily_distribution": dict(day_counter),
        "recent_activity_30_days": recent_activity,
        "peak_hours": [hour for hour, count in hour_counter.most_common(3)],
        "peak_days": [day for day, count in day_counter.most_common(3)],
    }

    print(
        f"   • Date range: {analysis['date_range']['earliest'][:10] if analysis['date_range']['earliest'] else 'N/A'} to {analysis['date_range']['latest'][:10] if analysis['date_range']['latest'] else 'N/A'}"
    )
    print(
        f"   • Recent activity (30 days): {analysis['recent_activity_30_days']} interactions"
    )
    print(f"   • Peak hours: {analysis['peak_hours']}")
    print(f"   • Peak days: {analysis['peak_days']}")

    return analysis


def analyze_event_content(events_data: List[Dict]) -> Dict[str, Any]:
    """Analyze event content to understand what users are searching for."""

    if not events_data:
        return {"error": "No event data available"}

    # Event categories
    categories = [event.get("category", "unknown") for event in events_data]
    category_counter = Counter(categories)

    # Event locations
    locations = [event.get("location", "unknown") for event in events_data]
    location_counter = Counter(locations)

    # Event timing
    confirmed_dates = len([e for e in events_data if e.get("start_date")])
    tbd_dates = len(events_data) - confirmed_dates

    # Title/description analysis
    titles = [event.get("title", "") for event in events_data if event.get("title")]
    all_title_words = []
    for title in titles:
        all_title_words.extend(title.lower().split())

    common_title_words = Counter(all_title_words).most_common(15)

    analysis = {
        "total_events": len(events_data),
        "category_distribution": dict(category_counter),
        "location_distribution": dict(location_counter.most_common(10)),
        "date_status": {"confirmed_dates": confirmed_dates, "tbd_dates": tbd_dates},
        "content_analysis": {
            "common_title_words": dict(common_title_words),
            "avg_title_length": (
                sum(len(t.split()) for t in titles) / len(titles) if titles else 0
            ),
        },
    }

    print(f"   • Total events: {analysis['total_events']}")
    print(f"   • Categories: {list(analysis['category_distribution'].keys())}")
    print(f"   • Top locations: {list(dict(location_counter.most_common(3)).keys())}")
    print(f"   • Common title words: {[word for word, _ in common_title_words[:5]]}")

    return analysis


def generate_ml_recommendations(
    query_analysis: Dict,
    user_analysis: Dict,
    temporal_analysis: Dict,
    event_analysis: Dict,
) -> Dict[str, Any]:
    """Generate recommendations for ML system design based on analysis."""

    recommendations = {
        "user_modeling_strategy": [],
        "recommendation_algorithms": [],
        "feature_engineering": [],
        "data_requirements": [],
        "implementation_priorities": [],
    }

    # User modeling recommendations
    if user_analysis.get("total_users", 0) > 10:
        if user_analysis.get("user_distribution", {}).get("power_users_10_plus", 0) > 2:
            recommendations["user_modeling_strategy"].append(
                "Implement collaborative filtering - sufficient power users for user-user similarity"
            )
        else:
            recommendations["user_modeling_strategy"].append(
                "Focus on content-based filtering - limited user interaction data"
            )

    # Algorithm recommendations based on query patterns
    if (
        query_analysis.get("unique_queries", 0) / query_analysis.get("total_queries", 1)
        > 0.7
    ):
        recommendations["recommendation_algorithms"].append(
            "High query diversity - implement semantic similarity with query expansion"
        )

    if query_analysis.get("avg_query_length", 0) > 3:
        recommendations["recommendation_algorithms"].append(
            "Complex queries detected - implement intent classification and multi-faceted search"
        )

    # Feature engineering based on data patterns
    common_terms = query_analysis.get("common_terms", {})
    if any(
        term in ["conference", "event", "blockchain", "crypto"]
        for term in common_terms.keys()
    ):
        recommendations["feature_engineering"].append(
            "Add crypto/blockchain domain-specific features and terminology expansion"
        )

    # Temporal features
    if temporal_analysis.get("peak_hours"):
        recommendations["feature_engineering"].append(
            f"Add time-based features - peak usage at hours: {temporal_analysis['peak_hours']}"
        )

    # Data requirements
    recommendations["data_requirements"] = [
        "Implement explicit feedback collection (likes/dislikes, saves, shares)",
        "Track click-through rates and dwell time on recommendations",
        "Collect user preference categories and interests",
        "Add implicit feedback from search result interactions",
    ]

    # Implementation priorities
    recommendations["implementation_priorities"] = [
        "1. Enhance existing semantic search with user preference weighting",
        "2. Implement user preference learning from search history",
        "3. Add collaborative filtering for similar user recommendations",
        "4. Create hybrid system combining content + collaborative filtering",
        "5. Add real-time recommendation updates and A/B testing",
    ]

    print("   🎯 Key Recommendations:")
    for priority in recommendations["implementation_priorities"][:3]:
        print(f"      {priority}")

    return recommendations


if __name__ == "__main__":
    analyze_user_behavior()
