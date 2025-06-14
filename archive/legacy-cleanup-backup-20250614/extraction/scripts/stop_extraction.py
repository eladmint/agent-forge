#!/usr/bin/env python3
"""
Stop EthCC Background Extraction

This script gracefully stops the background extraction process.
"""

import glob
import json
import os
import signal
import sys
import time


def stop_extraction(pid_file=None):
    """Stop the extraction process gracefully"""

    if pid_file is None:
        # Find the latest PID file
        pid_files = glob.glob("ethcc_extraction_pid_*.txt")
        if not pid_files:
            print("❌ No extraction process found")
            return
        pid_file = max(pid_files)  # Get the latest one

    try:
        with open(pid_file, "r") as f:
            process_info = json.load(f)
    except Exception as e:
        print(f"❌ Error reading PID file: {e}")
        return

    pid = process_info["pid"]

    print(f"🛑 Stopping extraction process {pid}...")

    try:
        # Check if process exists
        os.kill(pid, 0)

        # Send graceful termination signal
        print("📤 Sending SIGTERM (graceful shutdown)...")
        os.kill(pid, signal.SIGTERM)

        # Wait a moment for graceful shutdown
        time.sleep(5)

        # Check if still running
        try:
            os.kill(pid, 0)
            print("⚠️ Process still running, sending SIGKILL...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(2)
        except OSError:
            pass  # Process already terminated

        # Final check
        try:
            os.kill(pid, 0)
            print("❌ Failed to stop process")
        except OSError:
            print("✅ Process stopped successfully")

            # Check progress
            progress_files = glob.glob("ethcc_conservative_progress_*.json")
            if progress_files:
                latest_progress = max(progress_files)
                try:
                    with open(latest_progress, "r") as f:
                        progress = json.load(f)

                    processed = progress.get("processed_events", 0)
                    speakers = progress.get("events_with_speakers", 0)
                    sponsors = progress.get("events_with_sponsors", 0)

                    print("\n📊 Final Progress:")
                    print(f"   Events processed: {processed}/93")
                    print(f"   Events with speakers: {speakers}")
                    print(f"   Events with sponsors: {sponsors}")
                    print("\n🔄 To resume: python start_background_extraction.py")

                except Exception as e:
                    print(f"⚠️ Could not read final progress: {e}")

    except OSError:
        print("❌ Process not running")


if __name__ == "__main__":
    pid_file = sys.argv[1] if len(sys.argv) > 1 else None
    stop_extraction(pid_file)
