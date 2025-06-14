#!/usr/bin/env python3
"""
Background EthCC Extraction Launcher

This script starts the conservative extraction in the background with proper logging
and provides commands to monitor, stop, and resume the process.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime


def start_background_extraction():
    """Start the conservative extraction in the background"""

    # Create log file with timestamp
    timestamp = int(time.time())
    log_file = f"ethcc_extraction_log_{timestamp}.txt"
    pid_file = f"ethcc_extraction_pid_{timestamp}.txt"

    print("🚀 Starting EthCC Conservative Extraction in Background")
    print(f"📄 Log file: {log_file}")
    print(f"🆔 PID file: {pid_file}")
    print("=" * 60)

    # Start the process in background
    with open(log_file, "w") as f:
        process = subprocess.Popen(
            [sys.executable, "run_ethcc_conservative_extraction.py"],
            stdout=f,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,  # Create new process group
        )

    # Save PID for later control
    with open(pid_file, "w") as f:
        json.dump(
            {
                "pid": process.pid,
                "start_time": datetime.now().isoformat(),
                "log_file": log_file,
                "command": "python run_ethcc_conservative_extraction.py",
            },
            f,
            indent=2,
        )

    print(f"✅ Process started with PID: {process.pid}")
    print("📊 Expected duration: ~77 minutes (93 events)")
    print(f"⏰ Expected completion: {(datetime.now().timestamp() + 77*60)}")

    print("\n🛠️ Control Commands:")
    print(f"   Monitor progress: python monitor_extraction.py {pid_file}")
    print(f"   Stop extraction: python stop_extraction.py {pid_file}")
    print(f"   View live logs: tail -f {log_file}")
    print(f"   Check if running: ps -p {process.pid}")

    return process.pid, log_file, pid_file


def check_extraction_status():
    """Check if any extraction is currently running"""
    import glob

    pid_files = glob.glob("ethcc_extraction_pid_*.txt")
    if not pid_files:
        print("❌ No background extraction found")
        return None

    for pid_file in pid_files:
        try:
            with open(pid_file, "r") as f:
                info = json.load(f)

            pid = info["pid"]

            # Check if process is still running
            try:
                os.kill(pid, 0)  # Doesn't actually kill, just checks if exists
                print(f"✅ Extraction running: PID {pid}")
                print(f"   Started: {info['start_time']}")
                print(f"   Log file: {info['log_file']}")
                return info
            except OSError:
                print(f"❌ Process {pid} not running (stale PID file)")

        except Exception as e:
            print(f"⚠️ Error reading {pid_file}: {e}")

    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_extraction_status()
    else:
        # Check if already running
        existing = check_extraction_status()
        if existing:
            print("\n⚠️ Extraction already running!")
            print("Use 'python start_background_extraction.py status' to check status")
        else:
            start_background_extraction()
