#!/usr/bin/env python3
"""
Test Enhanced Orchestrator Service with Browser Automation
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())


# Test browser automation service functionality
async def test_browser_automation_service():
    """Test the enhanced orchestrator service with browser automation"""

    print("🧪 Testing Enhanced Orchestrator Service with Browser Automation")
    print("=" * 60)

    try:
        # Import the enhanced orchestrator service
        from enhanced_orchestrator_service import EnhancedOrchestrator

        # Create orchestrator instance
        orchestrator = EnhancedOrchestrator()

        # Check browser automation availability
        print(
            f"🔍 Browser automation available: {orchestrator.browser_orchestrator is not None}"
        )

        if orchestrator.browser_orchestrator:
            print("✅ Browser automation orchestrator initialized successfully")
        else:
            print("⚠️ Browser automation not available - checking why...")

            # Try to import browser automation manually
            try:
                from browser_automation_orchestrator import (
                    BrowserAutomationOrchestrator,
                )

                print("✅ Browser automation module can be imported")

                # Try to create instance
                browser_orch = BrowserAutomationOrchestrator()
                print("✅ Browser automation orchestrator can be created")

            except ImportError as e:
                print(f"❌ Cannot import browser automation: {e}")
            except Exception as e:
                print(f"❌ Cannot create browser automation orchestrator: {e}")

        # Test URL detection
        test_urls = [
            "https://lu.ma/ethcc",
            "https://eventbrite.com/e/test",
            "https://example.com/event",
        ]

        print("\n🔍 Testing URL detection:")
        for url in test_urls:
            requires_browser = orchestrator._requires_browser_automation(url)
            print(f"  {url} -> Browser automation: {requires_browser}")

        # Test extraction methods
        print("\n🧪 Testing extraction on Luma URL...")
        test_url = "https://lu.ma/ethcc"

        if (
            orchestrator.browser_orchestrator
            and orchestrator._requires_browser_automation(test_url)
        ):
            print("🔧 Would use browser automation for this URL")
            try:
                # Test browser extraction (mock)
                events = await orchestrator._extract_with_browser(test_url)
                print(f"✅ Browser extraction returned {len(events)} events")
                for event in events:
                    print(f"   - {event.title} (method: {event.extraction_method})")
            except Exception as e:
                print(f"❌ Browser extraction failed: {e}")
        else:
            print("🔧 Would use basic extraction for this URL")
            events = await orchestrator._extract_basic(test_url)
            print(f"✅ Basic extraction returned {len(events)} events")
            for event in events:
                print(f"   - {event.title} (method: {event.extraction_method})")

    except Exception as e:
        print(f"❌ Error testing service: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_browser_automation_service())
