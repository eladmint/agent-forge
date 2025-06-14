#!/usr/bin/env python3
"""
Script to investigate the Luma ETHCC page and understand why our Enhanced Orchestrator
is only finding a few events when there should be 75+ events.
"""

import json
import sys
import time
from datetime import datetime

# Add the mcp_tools directory to the path
sys.path.append("/Users/eladm/Projects/token/tokenhunter/mcp_tools")

try:
    from steel_enhanced_client import SteelEnhancedMCPClient

    print("✅ SteelEnhancedMCPClient imported successfully")
except ImportError as e:
    print(f"❌ Failed to import SteelEnhancedMCPClient: {e}")
    sys.exit(1)


def investigate_ethcc_page():
    """
    Navigate to the ETHCC page and analyze its structure
    """
    print("🔍 Starting investigation of https://lu.ma/ethcc")

    client = SteelEnhancedMCPClient()
    target_url = "https://lu.ma/ethcc"

    try:
        # Step 1: Navigate to the page
        print(f"📍 Navigating to {target_url}")
        navigation_result = client.navigate_to_page(target_url)
        print(f"Navigation result: {navigation_result}")

        # Step 2: Take a screenshot to see the page layout
        print("📸 Taking screenshot of the page")
        screenshot_result = client.take_screenshot("ethcc_page_investigation")
        print(f"Screenshot result: {screenshot_result}")

        # Step 3: Get page content
        print("📄 Getting page content")
        content_result = client.get_page_content()
        print(f"Content result type: {type(content_result)}")

        # Step 4: Look for event URLs
        print("🔗 Searching for event URLs")
        search_result = client.search_for_patterns(["lu.ma/", "luma.co/", "/event/"])
        print(f"Pattern search result: {search_result}")

        # Step 5: Check for dynamic loading indicators
        print("⏳ Checking for dynamic loading elements")
        dynamic_elements = client.check_for_elements(
            [
                "button[data-testid='load-more']",
                ".infinite-scroll",
                "[data-loading]",
                ".lazy-load",
                "button:contains('Load')",
                "button:contains('Show')",
            ]
        )
        print(f"Dynamic elements: {dynamic_elements}")

        # Step 6: Extract all links
        print("🔗 Extracting all links from the page")
        links_result = client.extract_all_links()
        print(f"Links extraction result: {links_result}")

        # Step 7: Count event-related links
        if isinstance(links_result, dict) and "links" in links_result:
            event_links = [
                link
                for link in links_result["links"]
                if "lu.ma/" in link or "luma.co/" in link
            ]
            print(f"📊 Found {len(event_links)} potential event links")

            # Show first 10 for analysis
            print("🔍 First 10 event links found:")
            for i, link in enumerate(event_links[:10]):
                print(f"  {i+1}. {link}")

        # Step 8: Check page source for JavaScript loading
        print("🔍 Checking for JavaScript-based content loading")
        js_check = client.execute_javascript(
            """
            return {
                hasReact: typeof React !== 'undefined',
                hasVue: typeof Vue !== 'undefined',
                hasAngular: typeof angular !== 'undefined',
                hasJQuery: typeof $ !== 'undefined',
                scripts: Array.from(document.scripts).map(s => s.src || 'inline').slice(0, 5),
                totalElements: document.querySelectorAll('*').length,
                eventCards: document.querySelectorAll('[data-testid*="event"], .event-card, [class*="event"]').length,
                lumaLinks: document.querySelectorAll('a[href*="lu.ma/"]').length
            };
        """
        )
        print(f"JavaScript analysis: {js_check}")

        # Step 9: Try scrolling to trigger lazy loading
        print("📜 Attempting to scroll and trigger lazy loading")
        scroll_result = client.scroll_and_wait()
        print(f"Scroll result: {scroll_result}")

        # Step 10: Re-check links after scrolling
        print("🔗 Re-extracting links after scrolling")
        links_after_scroll = client.extract_all_links()
        if isinstance(links_after_scroll, dict) and "links" in links_after_scroll:
            event_links_after = [
                link
                for link in links_after_scroll["links"]
                if "lu.ma/" in link or "luma.co/" in link
            ]
            print(f"📊 Found {len(event_links_after)} event links after scrolling")

        # Step 11: Save results
        investigation_results = {
            "timestamp": datetime.now().isoformat(),
            "target_url": target_url,
            "navigation_result": navigation_result,
            "screenshot_result": screenshot_result,
            "initial_links_count": len(event_links) if "event_links" in locals() else 0,
            "links_after_scroll_count": (
                len(event_links_after) if "event_links_after" in locals() else 0
            ),
            "javascript_analysis": js_check,
            "dynamic_elements": dynamic_elements,
            "sample_event_links": event_links[:20] if "event_links" in locals() else [],
            "investigation_summary": {
                "expected_events": "75+",
                "found_initial": len(event_links) if "event_links" in locals() else 0,
                "found_after_scroll": (
                    len(event_links_after) if "event_links_after" in locals() else 0
                ),
                "likely_dynamic_loading": (
                    len(event_links_after) > len(event_links)
                    if "event_links" in locals() and "event_links_after" in locals()
                    else False
                ),
            },
        }

        results_file = f"luma_ethcc_investigation_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(investigation_results, f, indent=2)

        print(f"💾 Investigation results saved to: {results_file}")
        return investigation_results

    except Exception as e:
        print(f"❌ Error during investigation: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    results = investigate_ethcc_page()

    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 60)

    if "error" in results:
        print(f"❌ Investigation failed: {results['error']}")
    else:
        summary = results.get("investigation_summary", {})
        print(f"Expected events: {summary.get('expected_events', 'Unknown')}")
        print(f"Found initially: {summary.get('found_initial', 0)}")
        print(f"Found after scroll: {summary.get('found_after_scroll', 0)}")
        print(
            f"Dynamic loading detected: {summary.get('likely_dynamic_loading', False)}"
        )

        if summary.get("found_initial", 0) < 20:
            print("\n⚠️  POTENTIAL ISSUES IDENTIFIED:")
            print("- Low event count suggests JavaScript-based content loading")
            print("- Page likely uses dynamic/lazy loading for events")
            print("- Simple curl/requests will miss most content")
            print("- Enhanced Orchestrator needs browser-based scraping")
