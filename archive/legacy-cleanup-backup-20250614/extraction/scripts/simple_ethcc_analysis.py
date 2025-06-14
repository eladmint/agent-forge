#!/usr/bin/env python3
"""
Simple EthCC Data Analysis
Quick analysis of EthCC events data from Supabase database
"""

import logging
import os
import json
import requests
from datetime import datetime
from collections import Counter

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logging.error("Supabase credentials not found in environment variables.")
    exit(1)

def main():
    """Run simple analysis."""
    api_url = f"{SUPABASE_URL}/rest/v1"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("EthCC Data Analysis Report")
    print("=" * 50)
    
    try:
        # 1. Get table schema/sample
        print("\n1. Database Schema Analysis:")
        url = f"{api_url}/events?limit=1"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        sample_data = response.json()
        if sample_data:
            print(f"   Sample record columns: {list(sample_data[0].keys())}")
        else:
            print("   No data found")
            return
        
        # 2. Total events count
        print("\n2. Total Events Analysis:")
        headers_count = headers.copy()
        headers_count["Prefer"] = "count=exact"
        
        url = f"{api_url}/events?select=id"
        response = requests.get(url, headers=headers_count)
        response.raise_for_status()
        
        content_range = response.headers.get("Content-Range", "0")
        if "/" in content_range:
            total_events = int(content_range.split("/")[-1])
            print(f"   Total Events: {total_events}")
        else:
            events_data = response.json()
            total_events = len(events_data)
            print(f"   Total Events: {total_events}")
        
        # 3. EthCC specific events
        print("\n3. EthCC Events Analysis:")
        ethcc_patterns = ["ethcc", "ethereum community conference", "eth cc"]
        all_ethcc_events = []
        
        for pattern in ethcc_patterns:
            # Search in name
            url = f"{api_url}/events?name=ilike.*{pattern}*"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                events = response.json()
                all_ethcc_events.extend(events)
                print(f"   Events matching '{pattern}' in name: {len(events)}")
        
        # Remove duplicates
        unique_ethcc_events = []
        seen_ids = set()
        for event in all_ethcc_events:
            event_id = event.get("id")
            if event_id and event_id not in seen_ids:
                unique_ethcc_events.append(event)
                seen_ids.add(event_id)
        
        print(f"   Total unique EthCC events: {len(unique_ethcc_events)}")
        
        # 4. Sample EthCC events
        if unique_ethcc_events:
            print("\n4. Sample EthCC Events:")
            for i, event in enumerate(unique_ethcc_events[:5]):
                print(f"   {i+1}. {event.get('name', 'N/A')}")
                print(f"      Date: {event.get('date', 'N/A')}")
                print(f"      Location: {event.get('location', 'N/A')}")
                print()
        
        # 5. Data completeness analysis
        print("\n5. Data Completeness Analysis:")
        url = f"{api_url}/events"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        all_events = response.json()
        if all_events:
            key_fields = ["name", "description", "date", "location", "url"]
            field_completeness = {}
            
            for field in key_fields:
                filled_count = sum(1 for event in all_events if event.get(field) and str(event.get(field)).strip())
                percentage = (filled_count / len(all_events)) * 100
                field_completeness[field] = {
                    "filled": filled_count,
                    "total": len(all_events),
                    "percentage": round(percentage, 2)
                }
                print(f"   {field}: {filled_count}/{len(all_events)} ({percentage:.1f}%)")
        
        # 6. Location analysis
        print("\n6. Geographic Distribution:")
        locations = [event.get('location') for event in all_events if event.get('location') and str(event.get('location')).strip()]
        location_counter = Counter(locations)
        
        print(f"   Events with location data: {len(locations)}/{len(all_events)} ({len(locations)/len(all_events)*100:.1f}%)")
        print(f"   Unique locations: {len(location_counter)}")
        
        if location_counter:
            print("   Top 10 locations:")
            for location, count in location_counter.most_common(10):
                print(f"      {location}: {count} events")
        
        # 7. Date analysis
        print("\n7. Temporal Coverage:")
        dates = [event.get('date') for event in all_events if event.get('date') and str(event.get('date')).strip()]
        print(f"   Events with date data: {len(dates)}/{len(all_events)} ({len(dates)/len(all_events)*100:.1f}%)")
        
        if dates:
            print("   Sample dates:")
            for date in dates[:10]:
                print(f"      {date}")
        
        # Save summary
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_events": total_events,
            "ethcc_events": len(unique_ethcc_events),
            "data_completeness": field_completeness if 'field_completeness' in locals() else {},
            "geographic_coverage": {
                "events_with_locations": len(locations),
                "unique_locations": len(location_counter),
                "top_locations": dict(location_counter.most_common(5))
            } if 'locations' in locals() else {},
            "temporal_coverage": {
                "events_with_dates": len(dates),
                "sample_dates": dates[:10]
            } if 'dates' in locals() else {}
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ethcc_analysis_summary_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n8. Analysis complete! Summary saved to: {filename}")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response:
            logging.error(f"Response status: {e.response.status_code}")
            logging.error(f"Response text: {e.response.text}")
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()