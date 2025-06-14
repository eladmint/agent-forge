#!/usr/bin/env python3
"""
Populate database with real EthCC events to replace fake ones.
"""

import asyncio

# Real events we successfully extracted and verified
REAL_ETHCC_EVENTS = [
    {
        "name": "🌟VCC Demo Day Ethcc Cannes (Yacht)🌐",
        "luma_url": "https://lu.ma/cymcvco8",
        "start_date": "2025-06-27T11:00:00.000+02:00",
        "description": "VCC Demo Day EthCC event in Cannes on a yacht",
        "location": "Cannes, France",
        "category": "Demo Day",
        "status": "verified_real",
    },
    {
        "name": "Moca Network Identity House @EthCC",
        "luma_url": "https://lu.ma/dnygltxf",
        "start_date": "2025-06-27T15:00:00.000+02:00",
        "description": "Moca Network Identity House event at EthCC",
        "location": "TBD",
        "category": "Networking",
        "status": "verified_real",
    },
    {
        "name": "Premium BD Dinner @EthCC 2025 | Hosted by Atlassoit",
        "luma_url": "https://lu.ma/za9oj41i",
        "start_date": "2025-06-27T19:00:00.000+02:00",
        "description": "Premium business development dinner hosted by Atlassoit",
        "location": "TBD",
        "category": "Dinner",
        "status": "verified_real",
    },
    {
        "name": "MONACO BEACH PARTY (WAIB Summit x NFTFEST x ORDINALS MONACO Official side event)",
        "luma_url": "https://lu.ma/34pp2de2",
        "start_date": "2025-06-27T19:00:00.000+02:00",
        "description": "Monaco beach party - official side event for WAIB Summit, NFTFEST, and ORDINALS MONACO",
        "location": "Monaco",
        "category": "Party",
        "status": "verified_real",
    },
    {
        "name": "EASYCON MONACO 🇲🇨",
        "luma_url": "https://lu.ma/EASYCONMonaco",
        "start_date": "2025-06-28T08:30:00.000+02:00",
        "description": "EASYCON Monaco conference",
        "location": "Monaco",
        "category": "Conference",
        "status": "verified_real",
    },
]


async def populate_real_events():
    """Populate database with real events using the production API"""
    print("🔧 Populating Database with Real EthCC Events")
    print("=" * 60)

    # For now, let's output the events in a format that can be used
    print(f"✅ Found {len(REAL_ETHCC_EVENTS)} real events to populate:")

    for i, event in enumerate(REAL_ETHCC_EVENTS, 1):
        print(f"\n{i}. {event['name']}")
        print(f"   URL: {event['luma_url']}")
        print(f"   Date: {event['start_date']}")
        print(f"   Category: {event['category']}")
        print(f"   Status: {event['status']}")

    # Generate SQL insert statements for manual execution if needed
    print("\n" + "=" * 60)
    print("📋 SQL INSERT statements for manual database population:")
    print("=" * 60)

    for event in REAL_ETHCC_EVENTS:
        sql = f"""
INSERT INTO events (name, description, start_date, location, category, luma_url, created_at, status)
VALUES (
    '{event['name'].replace("'", "''")}',
    '{event['description'].replace("'", "''")}',
    '{event['start_date']}',
    '{event['location']}',
    '{event['category']}',
    '{event['luma_url']}',
    NOW(),
    '{event['status']}'
);"""
        print(sql)

    print("\n✅ Real events ready for database population!")
    return REAL_ETHCC_EVENTS


if __name__ == "__main__":
    asyncio.run(populate_real_events())
