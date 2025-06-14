#!/usr/bin/env python3
"""
🎯 Extract Events - Simplified Interface to Unified Extraction System

This is the new simplified interface to run comprehensive event extraction
using the organized extraction system with all capabilities:
- Multi-region rate limiting evasion
- Complete 13+ agent system
- Real event extraction
- Database integration
- Cost optimization

Usage:
    python extract_events.py                    # Extract EthCC with full capabilities
    python extract_events.py --url URL          # Extract from specific calendar
    python extract_events.py --quick            # Quick test mode
    python extract_events.py --budget 10.0      # Set budget limit
"""

import asyncio
import sys
from pathlib import Path

# Add extraction system to path
sys.path.append(str(Path(__file__).parent / "extraction" / "orchestrators"))

try:
    from unified_extraction_orchestrator import (
        UnifiedExtractionOrchestrator,
        extract_ethcc_comprehensive,
        extract_quick_test,
    )
except ImportError as e:
    print(f"❌ Could not import unified extraction orchestrator: {e}")
    print("💡 Fallback: Using integrated_main_extractor...")
    try:
        from extraction.orchestrators.integrated_main_extractor import (
            IntegratedMainExtractor,
        )

        FALLBACK_MODE = True
    except ImportError:
        print("❌ No extraction system available. Please check installation.")
        sys.exit(1)


async def main():
    """Main extraction interface"""

    import argparse

    parser = argparse.ArgumentParser(
        description="🎯 Extract Events - Comprehensive Event Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_events.py                           # Extract EthCC comprehensively
  python extract_events.py --url https://lu.ma/event # Extract specific calendar
  python extract_events.py --quick                   # Quick test mode
  python extract_events.py --budget 10.0             # Set budget to $10
  python extract_events.py --help                    # Show this help
        """,
    )

    parser.add_argument(
        "--url",
        default="https://lu.ma/ethcc",
        help="Calendar URL to extract (default: EthCC)",
    )
    parser.add_argument(
        "--budget", type=float, default=5.0, help="Budget limit in USD (default: $5.00)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test mode (no agents, no multi-region, no database)",
    )
    parser.add_argument(
        "--no-agents", action="store_true", help="Disable 13+ agent processing"
    )
    parser.add_argument(
        "--no-multiregion",
        action="store_true",
        help="Disable multi-region rate limiting evasion",
    )
    parser.add_argument(
        "--no-database", action="store_true", help="Don't save results to database"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    import logging

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("🎯 Extract Events - Unified Extraction System")
    print("=" * 60)
    print(f"📅 Calendar URL: {args.url}")
    print(f"💰 Budget: ${args.budget}")
    print(f"⚡ Mode: {'Quick Test' if args.quick else 'Comprehensive'}")
    print("=" * 60)

    try:
        if args.quick:
            # Quick test mode
            print("⚡ Running quick test extraction...")
            results = await extract_quick_test(args.url)
        else:
            # Full comprehensive mode
            print("🚀 Running comprehensive extraction...")

            orchestrator = UnifiedExtractionOrchestrator(
                budget_limit=args.budget,
                enable_multi_region=not args.no_multiregion,
                enable_agents=not args.no_agents,
                enable_steel_browser=True,
                save_to_database=not args.no_database,
            )

            await orchestrator.initialize()

            try:
                results = await orchestrator.extract_comprehensive(
                    calendar_urls=[args.url], enable_calendar_discovery=True
                )
            finally:
                await orchestrator.cleanup()

        # Display results
        print("\n" + "=" * 60)
        print("🎉 EXTRACTION COMPLETE!")
        print("=" * 60)
        print(f"✅ Events Discovered: {results['total_events_discovered']}")
        print(f"💾 Events Saved: {results['events_saved_to_database']}")
        print(f"💰 Total Cost: ${results['total_cost']:.4f}")
        print(f"💸 Budget Remaining: ${results['budget_remaining']:.4f}")
        print(f"⏱️  Processing Time: {results['processing_time']:.2f}s")

        if results["regions_used"]:
            print(f"🌐 Regions Used: {', '.join(results['regions_used'])}")

        if results["agents_used"]:
            print(f"🧠 Agents Used: {', '.join(results['agents_used'])}")

        print(f"🎯 Extraction Method: {results['extraction_method']}")

        # Show capabilities used
        capabilities = results.get("capabilities_used", {})
        print("\n📋 Capabilities Used:")
        for capability, used in capabilities.items():
            status = "✅" if used else "❌"
            print(f"   {status} {capability.replace('_', ' ').title()}")

        if results["total_events_discovered"] > 0:
            print(f"\n🎯 Success! Found {results['total_events_discovered']} events!")
            if results["events_saved_to_database"] > 0:
                print(
                    f"💾 {results['events_saved_to_database']} events saved to database"
                )
        else:
            print("\n⚠️ No events found. Consider:")
            print("   • Checking the calendar URL")
            print("   • Trying with --verbose for more details")
            print("   • Using --quick for a simple test")

        return results

    except KeyboardInterrupt:
        print("\n⏹️ Extraction cancelled by user")
        return None
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return None


if __name__ == "__main__":
    results = asyncio.run(main())

    # Exit with appropriate code
    if results and results.get("total_events_discovered", 0) > 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
