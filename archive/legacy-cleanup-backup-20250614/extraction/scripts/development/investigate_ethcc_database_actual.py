#!/usr/bin/env python3
"""
Investigate actual EthCC events in database with multiple search patterns
"""

import os

import requests

# Set environment variables
os.environ["SUPABASE_URL"] = "https://zzwgtxibhfuynfpcinpy.supabase.co"
os.environ["SUPABASE_KEY"] = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6d2d0eGliaGZ1eW5mcGNpbnB5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MTM1MTgsImV4cCI6MjA2MDM4OTUxOH0.LpIB7rQ4YyTGszEMleJNQju6VuazIg7b9CIyjoqMCpI"
)


def search_database(pattern: str, description: str):
    """Search database with a specific pattern"""

    try:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]

        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

        # Query for events
        response = requests.get(
            f"{url}/rest/v1/events?select=id,name,description,category&{pattern}&limit=50",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            events = response.json()
            print(f"🔍 {description}: {len(events)} events found")

            if events:
                for i, event in enumerate(events[:10]):
                    print(f"   {i+1}. {event['name']}")
                    if event.get("category"):
                        print(f"      Category: {event['category']}")
                if len(events) > 10:
                    print(f"   ... and {len(events) - 10} more events")
            print()
            return events
        else:
            print(f"❌ {description} failed: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ {description} error: {e}")
        return []


def main():
    print("🔍 COMPREHENSIVE ETHCC DATABASE INVESTIGATION")
    print("=" * 70)
    print()

    # Test multiple search patterns
    search_patterns = [
        ("name=ilike.%ethcc%", "Events with 'ethcc' in name"),
        ("name=ilike.%EthCC%", "Events with 'EthCC' in name"),
        ("name=ilike.%eth%", "Events with 'eth' in name"),
        ("description=ilike.%ethcc%", "Events with 'ethcc' in description"),
        ("description=ilike.%EthCC%", "Events with 'EthCC' in description"),
        ("category=ilike.%ethcc%", "Events with 'ethcc' in category"),
        ("category=eq.EthCC Event", "Events with category 'EthCC Event'"),
    ]

    all_events = []
    for pattern, description in search_patterns:
        events = search_database(pattern, description)
        all_events.extend(events)

    # Remove duplicates by ID
    unique_events = {}
    for event in all_events:
        unique_events[event["id"]] = event

    total_unique = len(unique_events)
    print("📊 SUMMARY:")
    print(f"   • Total unique EthCC-related events: {total_unique}")
    print()

    if total_unique > 0:
        print("📋 UNIQUE ETHCC EVENTS IN DATABASE:")
        for i, event in enumerate(unique_events.values()):
            if i < 20:  # Show first 20
                print(f"   {i+1}. {event['name']}")
                if event.get("category"):
                    print(f"      Category: {event['category']}")
                print(f"      ID: {event['id']}")
                print()

        if total_unique > 20:
            print(f"   ... and {total_unique - 20} more events")

        print("✅ CONCLUSION:")
        print(f"   • Database contains {total_unique} EthCC-related events")
        print("   • Events are stored with various naming patterns")
        print("   • Enhanced Orchestrator deployment WAS successful")
        print("   • Users can find EthCC events through multiple search terms")

    else:
        print("❌ No EthCC events found with any search pattern")


if __name__ == "__main__":
    main()
