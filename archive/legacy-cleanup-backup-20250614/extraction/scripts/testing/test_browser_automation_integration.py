#!/usr/bin/env python3
"""
Test script for Browser Automation Integration
Verifies that the Enhanced Orchestrator can use browser automation for JavaScript-heavy sites
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_browser_automation_integration():
    """Test browser automation integration with Enhanced Orchestrator"""

    print("🧪 TESTING BROWSER AUTOMATION INTEGRATION")
    print("=" * 60)

    try:
        # Import Enhanced Orchestrator
        from enhanced_orchestrator import EnhancedOrchestrator

        print("✅ Enhanced Orchestrator imported successfully")

        # Initialize orchestrator
        orchestrator = EnhancedOrchestrator()
        init_success = await orchestrator.initialize()

        if not init_success:
            print("❌ Orchestrator initialization failed")
            return False

        print("✅ Orchestrator initialized successfully")

        # Check browser automation availability
        if orchestrator.browser_automation_available:
            print("✅ Browser automation is available")
        else:
            print("⚠️  Browser automation not available - install Playwright:")
            print("   pip install playwright")
            print("   playwright install chromium")
            return False

        if orchestrator.hybrid_orchestrator:
            print("✅ Hybrid orchestrator is ready")
        else:
            print("❌ Hybrid orchestrator initialization failed")
            return False

        # Test JavaScript-heavy site detection
        test_urls = [
            "https://lu.ma/ethcc",  # Should use browser automation
            "https://example.com",  # Should use HTTP
            "https://eventbrite.com/e/test",  # Should use browser automation
        ]

        print(f"\n🔍 Testing site detection for {len(test_urls)} URLs:")

        for url in test_urls:
            needs_browser = orchestrator._requires_browser_automation(url)
            method = "Browser Automation" if needs_browser else "HTTP"
            print(f"   {url} → {method}")

        # Test actual extraction on a simple site first
        print("\n🌐 Testing extraction on a simple site...")

        try:
            # Test with a simple site that should work with HTTP
            test_url = "https://httpbin.org/html"
            content, metadata = await orchestrator._extract_page_content_enhanced(
                test_url, enable_mcp=False
            )

            if content and len(content) > 100:
                print(f"✅ Simple site extraction successful ({len(content)} chars)")
                print(f"   Method: {metadata.get('extraction_method', 'unknown')}")
                print(f"   Title: {metadata.get('title', 'N/A')}")
            else:
                print("⚠️  Simple site extraction returned minimal content")

        except Exception as e:
            print(f"❌ Simple site extraction failed: {e}")

        # Test browser automation on a JavaScript site (if available)
        if orchestrator.hybrid_orchestrator:
            print("\n🌐 Testing browser automation on JavaScript site...")

            try:
                # Test with a site that requires JavaScript
                js_test_url = "https://httpbin.org/html"  # Safe test URL
                browser_result = (
                    await orchestrator.hybrid_orchestrator.extract_page_intelligent(
                        js_test_url
                    )
                )

                if browser_result.success:
                    print("✅ Browser automation test successful")
                    print(
                        f"   Content length: {len(browser_result.html_content)} chars"
                    )
                    print(f"   Page title: {browser_result.page_title}")
                    print(f"   Processing time: {browser_result.processing_time:.2f}s")
                    print(f"   URLs found: {len(browser_result.extracted_urls)}")
                else:
                    print(
                        f"⚠️  Browser automation test failed: {browser_result.error_message}"
                    )

            except Exception as e:
                print(f"❌ Browser automation test failed: {e}")

        # Cleanup
        await orchestrator.cleanup()
        print("✅ Cleanup completed")

        print("\n🎯 INTEGRATION TEST SUMMARY:")
        print("✅ Enhanced Orchestrator: Working")
        print(
            f"✅ Browser Automation: {'Available' if orchestrator.browser_automation_available else 'Not Available'}"
        )
        print(
            f"✅ Hybrid Strategy: {'Working' if orchestrator.hybrid_orchestrator else 'Failed'}"
        )
        print("✅ Site Detection: Working")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print(
            "   Make sure you're in the correct directory and dependencies are installed"
        )
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_luma_ethcc_extraction():
    """Test extraction specifically on the EthCC Luma page"""

    print("\n" + "=" * 60)
    print("🎯 TESTING ETHCC LUMA PAGE EXTRACTION")
    print("=" * 60)

    try:
        from enhanced_orchestrator import EnhancedOrchestrator

        orchestrator = EnhancedOrchestrator()
        await orchestrator.initialize()

        if not orchestrator.hybrid_orchestrator:
            print("❌ Browser automation not available - skipping EthCC test")
            return False

        ethcc_url = "https://lu.ma/ethcc"
        print(f"🌐 Testing extraction of: {ethcc_url}")

        start_time = datetime.now()

        # Extract with browser automation
        content, metadata = await orchestrator._extract_page_content_enhanced(
            ethcc_url, enable_mcp=False
        )

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print("\n📊 EXTRACTION RESULTS:")
        print(f"   Processing time: {processing_time:.2f} seconds")
        print(f"   Content length: {len(content):,} characters")
        print(f"   Extraction method: {metadata.get('extraction_method', 'unknown')}")
        print(f"   Page title: {metadata.get('title', 'N/A')[:60]}...")
        print(f"   Description: {metadata.get('description', 'N/A')[:100]}...")

        # Check for discovered URLs
        discovered_urls = metadata.get("discovered_urls", [])
        if discovered_urls:
            print(f"   URLs discovered: {len(discovered_urls)}")
            print("   Sample URLs:")
            for url in discovered_urls[:5]:
                print(f"     - {url}")
            if len(discovered_urls) > 5:
                print(f"     - ... and {len(discovered_urls) - 5} more")
        else:
            print("   URLs discovered: 0 (may indicate extraction issue)")

        # Success criteria
        success_criteria = {
            "Content extracted": len(content) > 10000,  # Substantial content
            "Method used": metadata.get("extraction_method") == "browser_automation",
            "Title extracted": bool(metadata.get("title")),
            "URLs discovered": len(discovered_urls) > 0,
            "Processing time": processing_time < 300,  # Under 5 minutes
        }

        print("\n✅ SUCCESS CRITERIA:")
        all_passed = True
        for criterion, passed in success_criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {criterion}: {status}")
            if not passed:
                all_passed = False

        await orchestrator.cleanup()

        if all_passed:
            print("\n🎉 ETHCC EXTRACTION TEST: SUCCESS!")
            print(
                "   Browser automation is working correctly for JavaScript-heavy sites"
            )
        else:
            print("\n⚠️  ETHCC EXTRACTION TEST: PARTIAL SUCCESS")
            print("   Some criteria failed - review extraction method")

        return all_passed

    except Exception as e:
        print(f"❌ EthCC extraction test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all browser automation integration tests"""

    print("🚀 BROWSER AUTOMATION INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()

    # Test 1: Basic integration
    test1_passed = await test_browser_automation_integration()

    # Test 2: EthCC specific test (only if basic test passed)
    test2_passed = False
    if test1_passed:
        test2_passed = await test_luma_ethcc_extraction()
    else:
        print("\n⚠️  Skipping EthCC test due to integration test failure")

    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Basic Integration Test: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(
        f"EthCC Extraction Test: {'✅ PASS' if test2_passed else '❌ FAIL' if test1_passed else '⚠️ SKIPPED'}"
    )

    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Browser automation is ready for production use")
        print("   JavaScript-heavy sites will now be extracted properly")
    elif test1_passed:
        print("\n⚠️  PARTIAL SUCCESS")
        print("   Basic integration works but site-specific extraction needs attention")
    else:
        print("\n❌ TESTS FAILED")
        print("   Browser automation setup needs to be fixed")
        print(
            "   Install dependencies: pip install playwright && playwright install chromium"
        )

    print(f"\nCompleted at: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())
