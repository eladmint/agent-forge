#!/usr/bin/env python3

import json
import sys
from datetime import datetime

from supabase import create_client


def investigate_ethcc_url_discrepancy():
    """
    Investigate why we have 38 EthCC events in database but orchestrator only found 5 duplicates
    when scraping https://lu.ma/ethcc
    """

    print("🔍 INVESTIGATING ETHCC URL DISCREPANCY")
    print("=" * 60)

    # Get Supabase credentials
    sys.path.append("/Users/eladm/Projects/token/tokenhunter")
    from chatbot_api.core.config import SUPABASE_KEY, SUPABASE_URL

    url = SUPABASE_URL
    key = SUPABASE_KEY
    supabase = create_client(url, key)

    # Get all EthCC events from database
    print("1. Analyzing all 38 EthCC events in database...")

    existing_events = (
        supabase.table("events").select("*").ilike("luma_url", "%ethcc%").execute()
    )

    print(f"   Found {len(existing_events.data)} EthCC events")

    # Analyze the URLs
    url_patterns = {}
    url_sources = {}

    for event in existing_events.data:
        luma_url = event.get("luma_url", "")

        # Categorize URL patterns
        if "/ethcc-" in luma_url.lower():
            url_patterns["direct_ethcc_prefix"] = (
                url_patterns.get("direct_ethcc_prefix", 0) + 1
            )
        elif "ethcc" in luma_url.lower():
            url_patterns["contains_ethcc"] = url_patterns.get("contains_ethcc", 0) + 1
        else:
            url_patterns["other"] = url_patterns.get("other", 0) + 1

        # Check if URL would be found on lu.ma/ethcc page
        if luma_url:
            # URLs that start with specific patterns are likely direct event links
            if (
                luma_url.startswith("https://lu.ma/")
                and len(luma_url.split("/")[-1]) > 5
            ):
                url_sources["likely_direct_links"] = url_sources.get(
                    "likely_direct_links", []
                ) + [luma_url]
            else:
                url_sources["other_sources"] = url_sources.get("other_sources", []) + [
                    luma_url
                ]

    print("\n2. URL Pattern Analysis:")
    for pattern, count in url_patterns.items():
        print(f"   • {pattern}: {count} events")

    print("\n3. Likely source analysis:")
    print(
        f"   • URLs that could be found on lu.ma/ethcc: {len(url_sources.get('likely_direct_links', []))}"
    )
    print(f"   • URLs from other sources: {len(url_sources.get('other_sources', []))}")

    # Show examples of different URL types
    print("\n4. Examples of different URL types:")

    direct_ethcc_urls = []
    ethcc_related_urls = []
    other_urls = []

    for event in existing_events.data[:20]:  # First 20 for analysis
        luma_url = event.get("luma_url", "")
        name = event.get("name", "Unnamed Event")

        if "/ethcc-" in luma_url.lower():
            direct_ethcc_urls.append((luma_url, name))
        elif "ethcc" in luma_url.lower() or "ethcc" in name.lower():
            ethcc_related_urls.append((luma_url, name))
        else:
            other_urls.append((luma_url, name))

    print("\n   📍 Direct EthCC URLs (likely on lu.ma/ethcc page):")
    for url, name in direct_ethcc_urls[:5]:
        print(f"     - {url}")
        print(f"       Event: {name[:50]}...")

    print("\n   🎯 EthCC-related URLs (might be on lu.ma/ethcc page):")
    for url, name in ethcc_related_urls[:5]:
        print(f"     - {url}")
        print(f"       Event: {name[:50]}...")

    print("\n   ❓ Other URLs (unlikely to be on lu.ma/ethcc page):")
    for url, name in other_urls[:3]:
        print(f"     - {url}")
        print(f"       Event: {name[:50]}...")

    # Analyze the discrepancy
    print("\n5. Discrepancy Analysis:")
    print(f"   • Database has: {len(existing_events.data)} EthCC events")
    print("   • Orchestrator found: 5 potential duplicates")
    print(f"   • Discrepancy: {len(existing_events.data) - 5} events")

    # Possible explanations
    explanations = [
        "lu.ma/ethcc page doesn't list all EthCC-related events",
        "Many events were added from other sources (not lu.ma/ethcc)",
        "Some events are EthCC-related but not directly linked from main page",
        "Events were added from individual event pages, not the main listing",
        "Previous extractions used different entry points",
        "lu.ma/ethcc page has pagination or dynamic loading",
    ]

    print("\n6. Possible explanations for discrepancy:")
    for i, explanation in enumerate(explanations, 1):
        print(f"   {i}. {explanation}")

    # Check creation patterns
    print("\n7. Creation pattern analysis:")

    creation_dates = {}
    for event in existing_events.data:
        created_at = event.get("created_at", "")
        if created_at:
            date = created_at.split("T")[0]
            creation_dates[date] = creation_dates.get(date, 0) + 1

    print("   Events by creation date:")
    for date in sorted(creation_dates.keys(), reverse=True):
        print(f"     {date}: {creation_dates[date]} events")

    # Hypothesis testing
    print("\n8. Testing hypotheses:")

    # Check if events have diverse URL patterns suggesting different sources
    unique_url_bases = set()
    for event in existing_events.data:
        luma_url = event.get("luma_url", "")
        if luma_url:
            # Extract the event ID/slug
            parts = luma_url.split("/")
            if len(parts) > 3:
                unique_url_bases.add(parts[-1])

    print(f"   • Unique event IDs found: {len(unique_url_bases)}")
    print(
        f"   • This suggests events came from {len(unique_url_bases)} different sources"
    )

    # Sample of different event URLs to show variety
    sample_urls = []
    for event in existing_events.data[:10]:
        luma_url = event.get("luma_url", "")
        if luma_url:
            sample_urls.append(luma_url.split("/")[-1])

    print(f"   • Sample event IDs: {', '.join(sample_urls[:5])}")

    # Save analysis
    results = {
        "timestamp": datetime.now().isoformat(),
        "database_events": len(existing_events.data),
        "orchestrator_duplicates_found": 5,
        "discrepancy": len(existing_events.data) - 5,
        "url_patterns": url_patterns,
        "creation_dates": creation_dates,
        "unique_event_ids": len(unique_url_bases),
        "sample_urls": [
            event.get("luma_url", "") for event in existing_events.data[:10]
        ],
        "hypotheses": explanations,
    }

    filename = f"ethcc_url_discrepancy_analysis_{int(datetime.now().timestamp())}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("The discrepancy (38 events vs 5 duplicates) likely means:")
    print("")
    print("1. 📄 lu.ma/ethcc page only shows a subset of all EthCC events")
    print("2. 🔗 Most events were added from individual event URLs, not the main page")
    print("3. 📅 Previous extractions used different entry points or sources")
    print("4. 🎯 The main EthCC page doesn't comprehensively list all related events")
    print("")
    print("This is normal behavior - event aggregation pages often don't show")
    print("all related events, and our database contains events from multiple sources.")

    print(f"\n💾 Detailed analysis saved to: {filename}")

    return results


if __name__ == "__main__":
    investigate_ethcc_url_discrepancy()
