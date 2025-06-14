#!/usr/bin/env python3
"""
🚀 Main Extractor Runner - Multi-Region Distributed Extraction

This script provides a simple interface to run the multi-region distributed
extraction system with cost optimization and rate limiting evasion.

Usage:
    python run_main_extractor.py --urls "https://lu.ma/ethcc" --budget 10.00
    python run_main_extractor.py --calendar "https://lu.ma/ethcc" --steel-browser
    python run_main_extractor.py --batch-file urls.txt --cost-optimized
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from cost_optimized_extraction_strategy import (
    cost_optimized_extraction,
)
from distributed_extraction_strategy import (
    DistributedExtractionOrchestrator,
    SteelBrowserConfig,
)

# Import comprehensive integrated system
try:
    from integrated_main_extractor import IntegratedMainExtractor

    COMPREHENSIVE_AVAILABLE = True
    logger.info("✅ Comprehensive 13+ agent system available")
except ImportError as e:
    COMPREHENSIVE_AVAILABLE = False
    logger.warning(f"⚠️ Comprehensive agent system not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("extraction.log")],
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Multi-Region Distributed Event Extraction with Rate Limiting Evasion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract single URL with cost optimization
  python run_main_extractor.py --urls "https://lu.ma/ethcc" --budget 10.00

  # Extract calendar with Steel Browser
  python run_main_extractor.py --calendar "https://lu.ma/ethcc" --steel-browser

  # Comprehensive extraction with 13+ agents + database saving
  python run_main_extractor.py --calendar "https://lu.ma/ethcc" --comprehensive --budget 20.00

  # Batch extraction from file
  python run_main_extractor.py --batch-file urls.txt --cost-optimized

  # Benchmark Steel Browser vs Standard
  python run_main_extractor.py --benchmark --test-urls "https://lu.ma/ethcc,https://lu.ma/cymcvco8"
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--urls", type=str, help="Comma-separated URLs to extract")
    input_group.add_argument(
        "--calendar", type=str, help="Calendar URL for comprehensive extraction"
    )
    input_group.add_argument(
        "--batch-file", type=str, help="File containing URLs (one per line)"
    )
    input_group.add_argument(
        "--benchmark", action="store_true", help="Run Steel Browser benchmark"
    )

    # Extraction options
    parser.add_argument(
        "--steel-browser", action="store_true", help="Force Steel Browser usage"
    )
    parser.add_argument(
        "--cost-optimized", action="store_true", help="Use cost-optimized extraction"
    )
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Use integrated 13+ agent system with database saving",
    )
    parser.add_argument(
        "--budget", type=float, default=10.0, help="Daily budget in USD (default: 10.0)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Max concurrent extractions (default: 3)",
    )

    # Output options
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet mode (errors only)"
    )

    # Testing options
    parser.add_argument(
        "--test-urls", type=str, help="Test URLs for benchmark (comma-separated)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run - show what would be extracted"
    )

    return parser.parse_args()


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Configure logging based on verbosity settings"""
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file"""
    try:
        with open(file_path, "r") as f:
            urls = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("#")
            ]
        logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        return urls
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading URLs from file: {e}")
        sys.exit(1)


def save_results(results: List[dict], output_file: Optional[str] = None):
    """Save extraction results to file"""
    if output_file:
        try:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    # Always save to timestamped file
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"extraction_results_{timestamp}.json"
    try:
        with open(backup_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results backed up to {backup_file}")
    except Exception as e:
        logger.warning(f"Error saving backup: {e}")


def print_summary(results: List[dict]):
    """Print extraction summary"""
    successful = sum(1 for r in results if r.get("status") == "success")
    total = len(results)

    print("\n📊 EXTRACTION SUMMARY")
    print(f"{'='*50}")
    print(f"Total URLs processed: {total}")
    print(f"Successful extractions: {successful}")
    print(f"Success rate: {(successful/max(total,1))*100:.1f}%")

    # Cost summary if available
    total_cost = Decimal("0")
    for result in results:
        cost_info = result.get("cost_info", {})
        if "extraction_cost" in cost_info:
            total_cost += Decimal(cost_info["extraction_cost"])

    if total_cost > 0:
        print(f"Total cost: ${total_cost:.4f}")
        if successful > 0:
            print(f"Cost per success: ${total_cost/successful:.4f}")

    # Event summary
    total_events = 0
    for result in results:
        if result.get("status") == "success":
            events = result.get("data", {}).get("events", [])
            event_count = len(events) if isinstance(events, list) else 0
            total_events += event_count

    if total_events > 0:
        print(f"Total events found: {total_events}")
        print(f"Events per successful extraction: {total_events/max(successful,1):.1f}")

    print(f"{'='*50}")


async def run_cost_optimized_extraction(urls: List[str], budget: float) -> List[dict]:
    """Run cost-optimized extraction"""
    logger.info(
        f"🏃 Running cost-optimized extraction for {len(urls)} URLs with ${budget} budget"
    )

    try:
        results = await cost_optimized_extraction(
            urls, daily_budget=Decimal(str(budget))
        )
        return results
    except Exception as e:
        logger.error(f"Cost-optimized extraction failed: {e}")
        return []


async def run_distributed_extraction(
    urls: List[str], use_steel: bool = False, max_concurrent: int = 3
) -> List[dict]:
    """Run distributed extraction with Steel Browser option"""
    logger.info(f"🌐 Running distributed extraction for {len(urls)} URLs")

    # Configure Steel Browser if requested
    steel_config = None
    if use_steel:
        steel_config = SteelBrowserConfig(
            api_key=os.getenv("STEEL_API_KEY", "demo_key"),
            session_duration=3600,
            proxy_rotation=True,
            anti_detection=True,
            residential_proxies=True,
        )

    orchestrator = DistributedExtractionOrchestrator(steel_config)
    await orchestrator.start()

    try:
        results = await orchestrator.extract_distributed(
            urls, max_retries=2, use_steel=use_steel
        )
        return results
    except Exception as e:
        logger.error(f"Distributed extraction failed: {e}")
        return []
    finally:
        await orchestrator.stop()


async def run_comprehensive_extraction(
    urls: List[str], budget: float, max_concurrent: int = 4
) -> List[dict]:
    """Run comprehensive extraction with 13+ agents and database saving"""
    if not COMPREHENSIVE_AVAILABLE:
        logger.error("❌ Comprehensive agent system not available")
        return []

    logger.info(
        f"🧠 Running comprehensive extraction for {len(urls)} URLs with 13+ agents"
    )

    extractor = IntegratedMainExtractor(
        daily_budget=Decimal(str(budget)),
        enable_steel_browser=True,
        enable_comprehensive_agents=True,
        enable_database_saving=True,
    )

    await extractor.start()

    try:
        results = []
        for url in urls:
            if url.startswith("https://lu.ma/") and "/event/" not in url:
                # This is a calendar URL - use comprehensive calendar extraction
                logger.info(f"📅 Processing calendar: {url}")
                calendar_results = await extractor.extract_calendar_comprehensive(
                    calendar_url=url,
                    max_concurrent_events=max_concurrent,
                    timeout_per_event=180,
                    force_steel_browser=False,
                )
                results.extend(calendar_results)
            else:
                # Individual event URL - process with comprehensive agents
                logger.info(f"🎯 Processing individual event: {url}")
                event_result = await extractor._process_single_event_integrated(
                    url, 180, False
                )
                if event_result:
                    results.append(event_result)

        return results

    except Exception as e:
        logger.error(f"Comprehensive extraction failed: {e}")
        return []
    finally:
        await extractor.stop()


async def run_benchmark(test_urls: List[str]) -> dict:
    """Run Steel Browser vs Standard benchmark"""
    logger.info(f"🔧 Running benchmark with {len(test_urls)} test URLs")

    orchestrator = DistributedExtractionOrchestrator()
    await orchestrator.start()

    try:
        benchmark_results = await orchestrator.benchmark_steel_browser(test_urls)
        return benchmark_results
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return {}
    finally:
        await orchestrator.stop()


async def main():
    """Main execution function"""
    args = parse_arguments()
    setup_logging(args.verbose, args.quiet)

    logger.info("🚀 Starting Multi-Region Distributed Event Extraction")

    # Determine URLs to process
    urls = []
    if args.urls:
        urls = [url.strip() for url in args.urls.split(",")]
    elif args.calendar:
        urls = [args.calendar]
    elif args.batch_file:
        urls = load_urls_from_file(args.batch_file)
    elif args.benchmark:
        if args.test_urls:
            urls = [url.strip() for url in args.test_urls.split(",")]
        else:
            # Default benchmark URLs
            urls = [
                "https://lu.ma/ethcc",
                "https://lu.ma/cymcvco8",
                "https://lu.ma/91fw4m6t",
            ]

    if args.dry_run:
        print("🔍 DRY RUN - URLs that would be processed:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
        print("\nConfiguration:")
        print(f"  - Cost optimized: {args.cost_optimized}")
        print(f"  - Comprehensive (13+ agents): {args.comprehensive}")
        print(f"  - Steel Browser: {args.steel_browser}")
        print(f"  - Budget: ${args.budget}")
        print(f"  - Max concurrent: {args.max_concurrent}")
        return

    # Run extraction based on mode
    results = []

    if args.benchmark:
        logger.info("🔧 Running Steel Browser benchmark")
        benchmark_results = await run_benchmark(urls)
        print("\n🔧 BENCHMARK RESULTS:")
        print(json.dumps(benchmark_results, indent=2, default=str))

        # Save benchmark results
        save_results([benchmark_results], args.output)
        return

    elif args.comprehensive:
        logger.info(
            "🧠 Running comprehensive extraction with 13+ agents and database saving"
        )
        results = await run_comprehensive_extraction(
            urls, budget=args.budget, max_concurrent=args.max_concurrent
        )

    elif args.cost_optimized:
        results = await run_cost_optimized_extraction(urls, args.budget)

    else:
        results = await run_distributed_extraction(
            urls, use_steel=args.steel_browser, max_concurrent=args.max_concurrent
        )

    # Process and display results
    if results:
        print_summary(results)
        save_results(results, args.output)

        # Show sample results
        if not args.quiet:
            print("\n📋 SAMPLE RESULTS:")
            for i, result in enumerate(results[:3], 1):
                status = result.get("status", "unknown")
                print(f"\n{i}. Status: {status}")

                if status == "success":
                    data = result.get("data", {})
                    events = data.get("events", [])
                    event_count = len(events) if isinstance(events, list) else 0
                    print(f"   Events found: {event_count}")

                    cost_info = result.get("cost_info", {})
                    if cost_info:
                        cost = cost_info.get("extraction_cost", "N/A")
                        region = cost_info.get("region_used", "N/A")
                        method = cost_info.get("method_used", "N/A")
                        print(f"   Cost: ${cost}, Region: {region}, Method: {method}")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"   Error: {error}")

            if len(results) > 3:
                print(f"\n... and {len(results) - 3} more results")
    else:
        logger.error("❌ No results obtained")
        sys.exit(1)

    logger.info("✅ Extraction completed successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⏹️ Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
