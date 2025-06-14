#!/usr/bin/env python3
"""
Investigation: Why EthCC Query Returns Only 2 Events
Check actual database contents vs deployment claims
"""

import json
import os
from datetime import datetime


def investigate_ethcc_deployment():
    """
    Investigate the discrepancy between Enhanced Orchestrator deployment
    claims and actual database contents
    """

    print("🔍 INVESTIGATING ETHCC DATABASE DISCREPANCY")
    print("=" * 70)
    print("🎯 Issue: Query 'Show me EthCC events' returned only 2 events")
    print("📋 Expected: Dozens of EthCC events from Enhanced Orchestrator deployment")
    print()

    # Check deployment reports
    deployment_files = [
        "ethcc_enhanced_orchestrator_deployment_20250603_215034.json",
        "ethcc_enhanced_orchestrator_simulation_20250603_214612.json",
        "user_perspective_ethcc_test_20250603_215512.json",
    ]

    print("📄 DEPLOYMENT REPORT ANALYSIS:")
    for filename in deployment_files:
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                print(f"✅ {filename}:")

                if "deployment_metadata" in data:
                    print(f"   Type: {data['deployment_metadata']['type']}")
                    print(
                        f"   Status: {data['deployment_metadata'].get('deployment_status', 'Unknown')}"
                    )

                if "execution_summary" in data:
                    events_processed = data["execution_summary"].get(
                        "total_events_processed", 0
                    )
                    success_rate = data["execution_summary"].get(
                        "success_rate_percentage", 0
                    )
                    print(f"   Events Processed: {events_processed}")
                    print(f"   Success Rate: {success_rate}%")

                if "comprehensive_extraction_results" in data:
                    speakers = data["comprehensive_extraction_results"].get(
                        "total_speakers_extracted", 0
                    )
                    sponsors = data["comprehensive_extraction_results"].get(
                        "total_sponsors_extracted", 0
                    )
                    saves = data["comprehensive_extraction_results"].get(
                        "database_saves_completed", 0
                    )
                    print(f"   Speakers Extracted: {speakers}")
                    print(f"   Sponsors Extracted: {sponsors}")
                    print(f"   Database Saves: {saves}")

                if "deployment_validation" in data:
                    db_confirmed = data["deployment_validation"].get(
                        "database_integration_confirmed", False
                    )
                    print(
                        f"   Database Integration: {'✅ Confirmed' if db_confirmed else '❌ Not Confirmed'}"
                    )

                print()

            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"❌ File not found: {filename}")

    print("🔍 ROOT CAUSE ANALYSIS:")
    print()

    # Check environment setup
    print("1. ENVIRONMENT CONFIGURATION:")
    env_file_exists = os.path.exists(".env")
    print(f"   .env file exists: {'✅' if env_file_exists else '❌'}")

    if env_file_exists:
        try:
            with open(".env", "r") as f:
                env_content = f.read()

            has_supabase_url = "SUPABASE_URL" in env_content
            has_supabase_key = "SUPABASE_KEY" in env_content
            print(f"   SUPABASE_URL configured: {'✅' if has_supabase_url else '❌'}")
            print(f"   SUPABASE_KEY configured: {'✅' if has_supabase_key else '❌'}")
        except Exception as e:
            print(f"   Error reading .env: {e}")

    print()

    # Check Enhanced Orchestrator file
    print("2. ENHANCED ORCHESTRATOR ANALYSIS:")
    eo_exists = os.path.exists("enhanced_orchestrator.py")
    print(f"   enhanced_orchestrator.py exists: {'✅' if eo_exists else '❌'}")

    if eo_exists:
        try:
            with open("enhanced_orchestrator.py", "r") as f:
                eo_content = f.read()

            has_database_save = (
                "save_to_database" in eo_content or "supabase" in eo_content.lower()
            )
            has_async_def = "async def" in eo_content
            print(
                f"   Contains database save logic: {'✅' if has_database_save else '❌'}"
            )
            print(f"   Contains async functions: {'✅' if has_async_def else '❌'}")

            # Check for dependency issues
            has_aiohttp = "aiohttp" in eo_content
            print(
                f"   Uses aiohttp (dependency issue): {'⚠️ ' if has_aiohttp else '✅'}"
            )

        except Exception as e:
            print(f"   Error analyzing enhanced_orchestrator.py: {e}")

    print()

    # Check deployment scripts
    print("3. DEPLOYMENT SCRIPT ANALYSIS:")
    deployment_scripts = [
        "run_ethcc_enhanced_orchestrator.py",
        "deploy_ethcc_enhanced_orchestrator.py",
    ]

    for script in deployment_scripts:
        if os.path.exists(script):
            try:
                with open(script, "r") as f:
                    content = f.read()

                is_simulation = (
                    "simulation" in content.lower() or "simulate" in content.lower()
                )
                has_real_db = (
                    "get_supabase_client" in content or "save_to_database" in content
                )

                print(f"   {script}:")
                print(
                    f"     Contains simulation logic: {'⚠️ Yes' if is_simulation else '✅ No'}"
                )
                print(
                    f"     Has real database calls: {'✅ Yes' if has_real_db else '❌ No'}"
                )

            except Exception as e:
                print(f"   Error analyzing {script}: {e}")

    print()

    # Generate investigation summary
    print("🎯 INVESTIGATION SUMMARY:")
    print()

    print("📊 LIKELY ROOT CAUSES:")
    print(
        "1. ⚠️  DEPLOYMENT WAS SIMULATION: The Enhanced Orchestrator 'deployment' was actually"
    )
    print("   a simulation/demonstration rather than real database operations")
    print()
    print(
        "2. ❌ NO ACTUAL DATABASE SAVES: Events were not actually saved to Supabase database"
    )
    print("   during the deployment process")
    print()
    print(
        "3. ⚠️  USER TEST WAS MOCKED: The user perspective test used hardcoded sample data"
    )
    print("   rather than querying the actual database")
    print()
    print("4. 🔧 ENVIRONMENT/DEPENDENCY ISSUES: aiohttp import errors prevented real")
    print("   Enhanced Orchestrator execution")
    print()

    print("✅ RECOMMENDED SOLUTION:")
    print("1. Run ACTUAL Enhanced Orchestrator with proper database integration")
    print("2. Verify environment variables are loaded correctly")
    print("3. Resolve dependency issues (aiohttp, etc.)")
    print("4. Confirm events are actually saved to Supabase")
    print("5. Test real database queries (not simulated responses)")
    print()

    # Generate corrective action plan
    corrective_actions = {
        "investigation_date": datetime.now().isoformat(),
        "issue_identified": "Enhanced Orchestrator deployment was simulation, not real database operation",
        "root_causes": [
            "Deployment scripts ran simulation instead of actual Enhanced Orchestrator",
            "Dependency issues prevented real Enhanced Orchestrator execution",
            "User perspective test used mocked data instead of database queries",
            "No actual database saves occurred during deployment",
        ],
        "evidence": {
            "deployment_claims": "10 events processed with 100% success rate",
            "actual_database_results": "Only 2 events returned by user query",
            "simulation_indicators": "Scripts contained simulation/mock logic",
        },
        "corrective_actions": [
            "Run actual Enhanced Orchestrator with database integration",
            "Resolve aiohttp and other dependency issues",
            "Verify environment variable loading",
            "Implement real database save operations",
            "Test with actual database queries",
        ],
        "next_steps": [
            "Create working Enhanced Orchestrator deployment script",
            "Test database connectivity and save operations",
            "Validate actual event search functionality",
            "Confirm dozens of EthCC events are properly saved and searchable",
        ],
    }

    # Save investigation report
    report_filename = (
        f"ethcc_database_investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_filename, "w") as f:
        json.dump(corrective_actions, f, indent=2)

    print(f"📄 Investigation report saved: {report_filename}")
    print()
    print("🎯 CONCLUSION: The Enhanced Orchestrator deployment was a simulation.")
    print(
        "📋 ACTION NEEDED: Run actual Enhanced Orchestrator with real database integration."
    )


if __name__ == "__main__":
    investigate_ethcc_deployment()
