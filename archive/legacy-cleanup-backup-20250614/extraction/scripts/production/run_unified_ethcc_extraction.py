import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from extraction.orchestrators.unified_extraction_orchestrator import (
    UnifiedExtractionOrchestrator,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- CONFIGURATION ---
ETHCC_CALENDAR_URLS = ["https://lu.ma/ethcc", "https://lu.ma/cymcvco8"]
# --- END CONFIGURATION ---


async def run_ethcc_extraction():
    """
    Runs the full, unified extraction process for the EthCC calendar.
    This script leverages the UnifiedExtractionOrchestrator to perform a multi-tier
    extraction, ensuring that after discovering event URLs from the main calendar,
    it proceeds to extract detailed information from each individual event page.
    """
    logging.info(
        f"Starting unified extraction for EthCC from URLs: {ETHCC_CALENDAR_URLS}"
    )

    # 1. Initialize the orchestrator with desired settings
    orchestrator = UnifiedExtractionOrchestrator(
        budget_limit=10.0,
        enable_multi_region=True,
        enable_agents=True,
        enable_steel_browser=True,
        save_to_database=True,
    )
    await orchestrator.initialize()

    try:
        # 2. Run the comprehensive extraction process
        results = await orchestrator.extract_comprehensive(
            calendar_urls=ETHCC_CALENDAR_URLS,
            max_concurrent=5,
            enable_calendar_discovery=True,
        )

        # 3. Log the results from the returned stats
        logging.info("--- Unified EthCC Extraction Complete ---")
        logging.info(f"  Total URLs Processed: {results.get('urls_processed', 0)}")
        logging.info(
            f"  Total Events Discovered: {results.get('events_discovered', 0)}"
        )
        logging.info(f"  Total Events Saved to DB: {results.get('events_saved', 0)}")
        logging.info(f"  Total Cost: ${results.get('total_cost', 0):.4f}")
        logging.info(
            f"  Regions Used: {', '.join(results.get('regions_used', [])) or 'N/A'}"
        )
        logging.info(
            f"  Agents Used: {', '.join(results.get('agents_used', [])) or 'N/A'}"
        )
        logging.info(f"  Duration: {results.get('duration_seconds', 0):.2f}s")

        if results.get("events_saved", 0) > 0:
            logging.info("✅ Extraction appears successful.")
        else:
            logging.warning(
                "⚠️ No events were saved. Please review the detailed logs for errors."
            )

    except Exception as e:
        logging.critical(
            f"A critical error occurred during the extraction process: {e}",
            exc_info=True,
        )
    finally:
        # 4. Clean up orchestrator resources
        await orchestrator.cleanup()
        logging.info("Unified EthCC extraction process finished.")


if __name__ == "__main__":
    asyncio.run(run_ethcc_extraction())
