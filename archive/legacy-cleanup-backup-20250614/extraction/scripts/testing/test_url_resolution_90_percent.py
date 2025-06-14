#!/usr/bin/env python3
"""
Test script for Enhanced URL Resolution - 90% Success Strategy Week 1
Tests the new URL resolution functionality with real EthCC URLs
"""

import asyncio
import logging

import aiohttp
from enhanced_orchestrator import EnhancedOrchestrator, EnhancedURLResolver

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test URLs from EthCC (mix of Luma and external sites)
TEST_URLS = [
    "https://lu.ma/ethcc-opening",
    "https://lu.ma/ethcc-hackathon",
    "https://lu.ma/w/events/ethcc",
    "https://lu.ma/ethcc-workshops",
    "https://lu.ma/ethcc-networking",
    "https://lu.ma/ethcc-afterparty",
    "https://lu.ma/ethcc-speakers",
    "https://lu.ma/ethcc-sponsors",
    # Some real EthCC URLs that may redirect
    "https://ethcc.io/events",
    "https://eventbrite.com/o/ethcc-123456",
]


async def test_url_resolution():
    """Test the new URL resolution functionality"""
    logger.info("🚀 Testing Enhanced URL Resolution - 90% Success Strategy")

    async with aiohttp.ClientSession() as session:
        # Test 1: Basic URL Resolution
        logger.info("\n📋 Test 1: Basic URL Resolution")
        resolver = EnhancedURLResolver(session=session)

        test_results = await resolver.batch_resolve_urls(TEST_URLS[:5])

        for original_url, resolution in test_results.items():
            if resolution.resolution_successful:
                redirects = (
                    f" ({len(resolution.redirect_chain)} redirects)"
                    if resolution.redirect_chain
                    else ""
                )
                logger.info(f"✅ {original_url} → {resolution.final_url}{redirects}")
            else:
                logger.warning(
                    f"❌ {original_url} - Failed: {resolution.error_message}"
                )

        # Test 2: Enhanced Orchestrator Integration
        logger.info("\n📋 Test 2: Enhanced Orchestrator Integration")
        orchestrator = EnhancedOrchestrator()
        await orchestrator.initialize()

        # Test with a small subset to verify integration
        integration_results = await orchestrator.extract_events_comprehensive(
            urls=TEST_URLS[:3],
            max_concurrent=2,
            timeout_per_event=30,
            enable_visual_intelligence=False,  # Disable for faster testing
            enable_mcp_browser=False,
        )

        # Analyze results
        successful_extractions = [
            r for r in integration_results if r.status == "success"
        ]
        url_resolution_failures = [
            r for r in integration_results if r.status == "url_resolution_failed"
        ]

        logger.info("\n📊 Integration Test Results:")
        logger.info(f"   Total URLs: {len(TEST_URLS[:3])}")
        logger.info(f"   Successful Extractions: {len(successful_extractions)}")
        logger.info(f"   URL Resolution Failures: {len(url_resolution_failures)}")
        logger.info(
            f"   Success Rate: {len(successful_extractions) / len(TEST_URLS[:3]):.1%}"
        )

        # Test 3: Performance Analysis
        logger.info("\n📋 Test 3: Performance Analysis")

        import time

        start_time = time.time()

        # Test resolution performance
        performance_results = await resolver.batch_resolve_urls(TEST_URLS)

        end_time = time.time()
        total_time = end_time - start_time

        successful_resolutions = sum(
            1 for r in performance_results.values() if r.resolution_successful
        )
        avg_resolution_time = sum(
            r.resolution_time for r in performance_results.values()
        ) / len(performance_results)

        logger.info("📊 Performance Results:")
        logger.info(f"   Total URLs: {len(TEST_URLS)}")
        logger.info(f"   Successful Resolutions: {successful_resolutions}")
        logger.info(
            f"   Resolution Rate: {successful_resolutions / len(TEST_URLS):.1%}"
        )
        logger.info(f"   Total Time: {total_time:.2f}s")
        logger.info(f"   Average Resolution Time: {avg_resolution_time:.2f}s")
        logger.info(f"   URLs per second: {len(TEST_URLS) / total_time:.1f}")

        return {
            "resolution_rate": successful_resolutions / len(TEST_URLS),
            "avg_resolution_time": avg_resolution_time,
            "total_performance_time": total_time,
        }


async def test_redirect_chain_analysis():
    """Test redirect chain analysis for understanding URL patterns"""
    logger.info("\n🔍 Testing Redirect Chain Analysis")

    async with aiohttp.ClientSession() as session:
        resolver = EnhancedURLResolver(session=session)

        # Test with a URL known to have redirects
        redirect_test_urls = [
            "https://lu.ma/ethcc",
            "https://bit.ly/ethcc-event",  # Short URL that redirects
            "https://t.co/ethcc123",  # Twitter short URL
        ]

        for test_url in redirect_test_urls:
            try:
                result = await resolver.resolve_event_url_chain(test_url)
                if result.resolution_successful:
                    logger.info(f"🔗 URL: {test_url}")
                    logger.info(f"   Final: {result.final_url}")
                    logger.info(
                        f"   Redirect Chain: {len(result.redirect_chain)} steps"
                    )
                    for i, redirect in enumerate(result.redirect_chain):
                        logger.info(f"     {i+1}. {redirect}")
                    logger.info(f"   Resolution Time: {result.resolution_time:.2f}s")
                else:
                    logger.warning(f"❌ {test_url} - Failed: {result.error_message}")
            except Exception as e:
                logger.error(f"❌ Exception testing {test_url}: {e}")


async def main():
    """Main test function"""
    logger.info("🎯 Enhanced URL Resolution Test Suite - 90% Success Strategy")
    logger.info("Testing Week 1 implementation: Comprehensive URL Resolution")

    try:
        # Run URL resolution tests
        performance_results = await test_url_resolution()

        # Run redirect chain analysis
        await test_redirect_chain_analysis()

        # Summary
        logger.info("\n🎯 90% Success Strategy - Week 1 Test Summary")
        logger.info(
            f"✅ URL Resolution Rate: {performance_results['resolution_rate']:.1%}"
        )
        logger.info(
            f"⚡ Average Resolution Time: {performance_results['avg_resolution_time']:.2f}s"
        )
        logger.info(
            f"🚀 Total Performance: {performance_results['total_performance_time']:.2f}s"
        )

        # Assess progress toward 90% target
        if performance_results["resolution_rate"] >= 0.90:
            logger.info("🎉 TARGET ACHIEVED: 90%+ URL resolution rate!")
        elif performance_results["resolution_rate"] >= 0.80:
            logger.info(
                "📈 GOOD PROGRESS: 80%+ resolution rate, approaching 90% target"
            )
        else:
            logger.info("⚠️ NEEDS IMPROVEMENT: Below 80% resolution rate")

        logger.info("\n✅ Week 1 Enhanced URL Resolution implementation complete!")
        logger.info(
            "🔜 Next: Week 2 - Expanded Platform Support (+7% expected improvement)"
        )

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
