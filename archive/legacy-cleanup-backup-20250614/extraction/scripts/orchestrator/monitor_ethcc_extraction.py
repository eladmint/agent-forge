#!/usr/bin/env python3
"""
EthCC Extraction Monitor
Monitors the database for completion of EthCC event extraction
"""

import sys
import time
from datetime import datetime

sys.path.append(".")

from agent_forge.core.shared.database.client import get_supabase_client


def check_extraction_progress():
    """Check current extraction progress"""
    try:
        client = get_supabase_client()

        # Get EthCC events
        ethcc_events = (
            client.table("events").select("*").ilike("luma_url", "%ethcc%").execute()
        )
        current_count = len(ethcc_events.data)

        # Get most recent event
        recent = (
            client.table("events")
            .select("*")
            .ilike("luma_url", "%ethcc%")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        last_update = (
            recent.data[0].get("created_at", "Unknown") if recent.data else "No events"
        )

        return current_count, last_update

    except Exception as e:
        print(f"❌ Error checking progress: {e}")
        return None, None


def monitor_extraction(target_count=90, check_interval=30):
    """Monitor extraction until completion"""
    print("🔍 Starting EthCC Extraction Monitor")
    print(f"📊 Target: {target_count} events")
    print(f"⏱️  Check interval: {check_interval} seconds")
    print("=" * 50)

    start_time = datetime.now()
    last_count = 0
    no_change_cycles = 0

    while True:
        current_count, last_update = check_extraction_progress()

        if current_count is None:
            print(f"❌ Cannot check progress - retrying in {check_interval}s...")
            time.sleep(check_interval)
            continue

        # Calculate progress
        progress = (current_count / target_count) * 100
        elapsed = datetime.now() - start_time

        # Check for changes
        if current_count == last_count:
            no_change_cycles += 1
        else:
            no_change_cycles = 0
            last_count = current_count

        # Display status
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"📊 {current_count}/{target_count} events ({progress:.1f}%) "
            f"| ⏱️ {elapsed} elapsed "
            f"| 🕒 Last: {last_update[:19] if last_update != 'No events' else 'None'}"
        )

        # Check completion conditions
        if current_count >= target_count:
            print("\n" + "=" * 50)
            print("🎯 ✅ EXTRACTION COMPLETED!")
            print(f"📊 Final count: {current_count}/{target_count} events")
            print(f"⏱️  Total time: {elapsed}")
            print(f"📅 Completed at: {datetime.now()}")
            break

        # Check if extraction might be stalled
        if no_change_cycles >= 10:  # 5 minutes of no changes
            print(
                f"\n⚠️  No new events for {no_change_cycles * check_interval // 60} minutes"
            )
            print(f"📊 Current: {current_count}/{target_count} events")
            print("🤔 Extraction might be stalled or completed with fewer events")

            if no_change_cycles >= 20:  # 10 minutes of no changes
                print("\n⏸️  Stopping monitor - extraction appears to have stopped")
                break

        time.sleep(check_interval)

    return current_count


def quick_status():
    """Get quick status without monitoring"""
    current_count, last_update = check_extraction_progress()

    if current_count is not None:
        progress = (current_count / 90) * 100
        print(
            f"📊 EthCC Extraction Status: {current_count}/90 events ({progress:.1f}%)"
        )
        print(
            f"🕒 Last updated: {last_update[:19] if last_update != 'No events' else 'None'}"
        )

        if current_count >= 90:
            print("✅ EXTRACTION COMPLETE!")
        elif current_count >= 80:
            print("🔄 Nearly complete - monitoring recommended")
        else:
            print("🔄 Extraction in progress")
    else:
        print("❌ Could not check status")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor EthCC extraction progress")
    parser.add_argument(
        "--monitor", action="store_true", help="Start continuous monitoring"
    )
    parser.add_argument(
        "--target", type=int, default=90, help="Target number of events"
    )
    parser.add_argument(
        "--interval", type=int, default=30, help="Check interval in seconds"
    )

    args = parser.parse_args()

    if args.monitor:
        final_count = monitor_extraction(args.target, args.interval)
        print(f"\n🎯 Monitoring complete: {final_count} events extracted")
    else:
        quick_status()
