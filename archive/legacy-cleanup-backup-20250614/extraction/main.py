#!/usr/bin/env python3
"""
Nuru AI Extraction Service
Main entry point for the data extraction service.
"""

import asyncio
import logging

# Add the src directory to path for imports
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


def setup_logging():
    """Configure logging for the extraction service."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("extraction.log"), logging.StreamHandler()],
    )


async def main():
    """Main entry point for the Extraction service."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🔍 Starting Nuru AI Extraction Service v2.0.0")

    try:
        # Load configuration
        from agent_forge.core.shared.config import load_settings

        settings = load_settings()

        logger.info("✅ Extraction Service started successfully")

        # Keep the service running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received")
    except Exception as e:
        logger.error(f"❌ Error starting Extraction Service: {e}")
        raise
    finally:
        logger.info("🔄 Extraction Service stopped")


if __name__ == "__main__":
    asyncio.run(main())
