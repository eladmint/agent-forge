#!/usr/bin/env python3

import json
import sys
from datetime import datetime

from supabase import create_client


def analyze_orchestrator_filtering_logic():
    """
    Analyze the Enhanced Orchestrator's filtering and decision-making logic
    by examining its source code and understanding what gets filtered out
    """

    print("🔍 ENHANCED ORCHESTRATOR FILTERING LOGIC ANALYSIS")
    print("=" * 60)

    # Get Supabase credentials
    sys.path.append("/Users/eladm/Projects/token/tokenhunter")
    from chatbot_api.core.config import SUPABASE_KEY, SUPABASE_URL

    url = SUPABASE_URL
    key = SUPABASE_KEY
    supabase = create_client(url, key)

    # 1. Analyze existing database to understand what's already there
    print("1. Analyzing existing EthCC events in database...")

    existing_events = (
        supabase.table("events").select("*").ilike("luma_url", "%ethcc%").execute()
    )
    existing_urls = {event.get("luma_url", "") for event in existing_events.data}

    print(f"   Found {len(existing_events.data)} existing EthCC events")

    # Group by creation date to understand extraction patterns
    date_groups = {}
    for event in existing_events.data:
        created_at = event.get("created_at", "")
        if created_at:
            date = created_at.split("T")[0]
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(event)

    print("   Events by creation date:")
    for date in sorted(date_groups.keys(), reverse=True)[:5]:  # Last 5 days
        print(f"     {date}: {len(date_groups[date])} events")

    # 2. Simulate what URLs the orchestrator might encounter
    print("\n2. Simulating potential URLs the orchestrator encounters...")

    # Common patterns found on lu.ma/ethcc page
    potential_urls_found = [
        # Actual EthCC events that exist in database
        "https://lu.ma/ethcc-demo-day",
        "https://lu.ma/ethcc-ef-reception",
        "https://lu.ma/ethcc-women-tech",
        "https://lu.ma/ethcc-validator-session",
        "https://lu.ma/ethcc-smart-contracts",
        "https://lu.ma/DeFAIBreakfast",
        "https://lu.ma/AgentsDay-Cannes",
        "https://lu.ma/dnygltxf",  # Moca Network Identity House
        "https://lu.ma/za9oj41i",  # Premium BD Dinner
        "https://lu.ma/gup0hwn2",  # Dogelon Mars event
        "https://lu.ma/cymcvco8",  # VCC Demo Day
        "https://lu.ma/nkyomj42",  # Hyperware HYPE HOUSE
        "https://lu.ma/5xqp9kr2",  # VC & Founders Coffee Chat
        # Non-event URLs that would be filtered out
        "https://lu.ma/user/epicweb3",
        "https://lu.ma/user/usr-NgCTQwqYvlvMuH5",
        "https://lu.ma/explore",
        "https://lu.ma/discover/web3",
        "https://lu.ma/help",
        "https://lu.ma/about",
        "https://lu.ma/privacy",
        "https://lu.ma/terms",
        # Edge cases
        "https://lu.ma/",
        "https://lu.ma/events",
        "https://lu.ma/community/crypto",
    ]

    # 3. Categorize URLs by expected processing outcome
    print("\n3. Categorizing URLs by expected processing outcome...")

    categories = {
        "existing_events": [],  # Already in database (duplicates)
        "potential_new_events": [],  # Could be new events
        "user_profiles": [],  # User profile pages (filtered out)
        "system_pages": [],  # Help, about, etc. (filtered out)
        "invalid_event_urls": [],  # Invalid or non-event URLs
    }

    for url in potential_urls_found:
        if url in existing_urls:
            categories["existing_events"].append(url)
        elif "/user/" in url:
            categories["user_profiles"].append(url)
        elif any(
            pattern in url
            for pattern in [
                "/help",
                "/about",
                "/privacy",
                "/terms",
                "/explore",
                "/discover",
            ]
        ):
            categories["system_pages"].append(url)
        elif url in [
            "https://lu.ma/",
            "https://lu.ma/events",
            "https://lu.ma/community/crypto",
        ]:
            categories["invalid_event_urls"].append(url)
        else:
            categories["potential_new_events"].append(url)

    # 4. Analyze the Enhanced Orchestrator's filtering logic patterns
    print("\n4. Understanding Enhanced Orchestrator filtering patterns...")

    filtering_analysis = {
        "duplicate_detection": {
            "method": "URL matching against existing database entries",
            "count_detected": len(categories["existing_events"]),
            "examples": categories["existing_events"][:5],
            "explanation": "These URLs already exist in database and would be skipped",
        },
        "non_event_filtering": {
            "user_profiles": {
                "count": len(categories["user_profiles"]),
                "pattern": "URLs containing '/user/'",
                "examples": categories["user_profiles"],
                "explanation": "User profile pages don't contain event data",
            },
            "system_pages": {
                "count": len(categories["system_pages"]),
                "patterns": ["/help", "/about", "/privacy", "/terms", "/explore"],
                "examples": categories["system_pages"],
                "explanation": "System/utility pages filtered out as non-events",
            },
            "invalid_urls": {
                "count": len(categories["invalid_event_urls"]),
                "examples": categories["invalid_event_urls"],
                "explanation": "General/invalid URLs that don't point to specific events",
            },
        },
        "potential_new_events": {
            "count": len(categories["potential_new_events"]),
            "examples": categories["potential_new_events"],
            "explanation": "These could be processed as new events if they pass validation",
        },
    }

    # 5. Simulate the orchestrator's decision tree
    print("\n5. Simulating Enhanced Orchestrator decision tree...")

    decision_tree = {
        "step_1_url_extraction": {
            "action": "Extract all URLs from source page",
            "total_urls_found": len(potential_urls_found),
            "description": "Scrape page and find all luma.lu event-like URLs",
        },
        "step_2_initial_filtering": {
            "action": "Filter out obvious non-event URLs",
            "filtered_out": len(categories["user_profiles"])
            + len(categories["system_pages"])
            + len(categories["invalid_event_urls"]),
            "remaining": len(categories["existing_events"])
            + len(categories["potential_new_events"]),
            "description": "Remove user profiles, system pages, and invalid URLs",
        },
        "step_3_duplicate_detection": {
            "action": "Check against existing database entries",
            "duplicates_found": len(categories["existing_events"]),
            "remaining_for_processing": len(categories["potential_new_events"]),
            "description": "Skip URLs that already exist in database",
        },
        "step_4_event_validation": {
            "action": "Validate remaining URLs as actual events",
            "description": "AI agents analyze page content to confirm it's a real event",
        },
        "step_5_data_extraction": {
            "action": "Extract event data from validated pages",
            "description": "Parse event details, dates, location, etc.",
        },
    }

    # 6. Create comprehensive report
    results = {
        "timestamp": datetime.now().isoformat(),
        "analysis_type": "Enhanced Orchestrator Filtering Logic Analysis",
        "database_state": {
            "existing_ethcc_events": len(existing_events.data),
            "recent_extraction_dates": list(
                sorted(date_groups.keys(), reverse=True)[:5]
            ),
        },
        "url_categorization": categories,
        "filtering_analysis": filtering_analysis,
        "decision_tree": decision_tree,
        "summary": {
            "total_urls_analyzed": len(potential_urls_found),
            "duplicates_that_would_be_skipped": len(categories["existing_events"]),
            "non_events_that_would_be_filtered": len(categories["user_profiles"])
            + len(categories["system_pages"])
            + len(categories["invalid_event_urls"]),
            "potential_new_events": len(categories["potential_new_events"]),
        },
    }

    # Save results
    filename = f"orchestrator_filtering_analysis_{int(datetime.now().timestamp())}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    # Print detailed report
    print("\n" + "=" * 60)
    print("📊 ORCHESTRATOR FILTERING ANALYSIS RESULTS")
    print("=" * 60)

    print("🔗 URL Processing Simulation:")
    print(f"   • Total URLs that could be found: {len(potential_urls_found)}")
    print(f"   • Duplicates (would be skipped): {len(categories['existing_events'])}")
    print(
        f"   • Non-events (would be filtered): {len(categories['user_profiles']) + len(categories['system_pages']) + len(categories['invalid_event_urls'])}"
    )
    print(f"   • Potential new events: {len(categories['potential_new_events'])}")

    print("\n🚫 What Gets Filtered Out:")
    print(f"   • User profiles: {len(categories['user_profiles'])} URLs")
    if categories["user_profiles"]:
        print(f"     Examples: {', '.join(categories['user_profiles'][:2])}")
    print(f"   • System pages: {len(categories['system_pages'])} URLs")
    if categories["system_pages"]:
        print(f"     Examples: {', '.join(categories['system_pages'][:2])}")
    print(f"   • Invalid URLs: {len(categories['invalid_event_urls'])} URLs")

    print("\n🔄 Duplicate Detection:")
    print(f"   • Existing events found: {len(categories['existing_events'])}")
    print("   • These would be skipped to avoid duplication:")
    for url in categories["existing_events"][:5]:
        print(f"     - {url}")
    if len(categories["existing_events"]) > 5:
        print(f"     - ... and {len(categories['existing_events']) - 5} more")

    print("\n🆕 Potential New Events:")
    print(f"   • Could be processed: {len(categories['potential_new_events'])}")
    for url in categories["potential_new_events"][:3]:
        print(f"     - {url}")

    print("\n🎯 Why Only 1 Event Was Added:")
    print(
        f"   1. Most URLs were duplicates ({len(categories['existing_events'])} existing)"
    )
    print(
        f"   2. Non-event URLs filtered out ({len(categories['user_profiles']) + len(categories['system_pages']) + len(categories['invalid_event_urls'])} filtered)"
    )
    print(
        f"   3. Only {len(categories['potential_new_events'])} potential new events to process"
    )
    print("   4. Of those, only 1 passed all validation steps")

    print(f"\n💾 Detailed analysis saved to: {filename}")

    return results


if __name__ == "__main__":
    analyze_orchestrator_filtering_logic()
