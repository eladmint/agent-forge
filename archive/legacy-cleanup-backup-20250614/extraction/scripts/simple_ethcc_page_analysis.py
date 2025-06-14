#!/usr/bin/env python3
"""
Simple analysis of the ETHCC page to understand why our Enhanced Orchestrator
is missing most events. This will help identify the issue.
"""

import json
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def analyze_ethcc_page():
    """
    Analyze the ETHCC page to understand content loading
    """
    target_url = "https://lu.ma/ethcc"
    print(f"🔍 Analyzing {target_url}")

    # Step 1: Try simple HTTP request (what Enhanced Orchestrator likely does)
    print("\n📡 Step 1: Simple HTTP Request Analysis")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(target_url, headers=headers, timeout=30)
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.text)} characters")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for event links
        all_links = soup.find_all("a", href=True)
        event_links = []

        for link in all_links:
            href = link.get("href", "")
            if "lu.ma/" in href and href != "https://lu.ma/ethcc":
                # Convert relative URLs to absolute
                if href.startswith("/"):
                    href = urljoin(target_url, href)
                event_links.append(href)

        # Remove duplicates
        event_links = list(set(event_links))

        print(f"📊 Found {len(event_links)} unique event links in initial HTML")

        # Show first 10 links
        if event_links:
            print("🔗 Sample event links found:")
            for i, link in enumerate(event_links[:10]):
                print(f"  {i+1}. {link}")
        else:
            print("⚠️  No event links found in initial HTML!")

        # Step 2: Look for JavaScript/dynamic loading indicators
        print("\n🔍 Step 2: JavaScript/Dynamic Loading Analysis")

        # Check for React/Next.js indicators
        script_tags = soup.find_all("script")
        js_frameworks = []

        for script in script_tags:
            if script.get("src"):
                src = script.get("src")
                if "react" in src.lower():
                    js_frameworks.append("React")
                elif "next" in src.lower():
                    js_frameworks.append("Next.js")
                elif "vue" in src.lower():
                    js_frameworks.append("Vue.js")

        # Check for async loading patterns
        async_patterns = [
            "data-loading",
            "lazy-load",
            "infinite-scroll",
            "load-more",
            "__NEXT_DATA__",
            "getServerSideProps",
            "getStaticProps",
        ]

        found_patterns = []
        page_text = response.text.lower()
        for pattern in async_patterns:
            if pattern.lower() in page_text:
                found_patterns.append(pattern)

        print(f"🎯 JavaScript frameworks detected: {js_frameworks or 'None obvious'}")
        print(f"🔄 Async loading patterns found: {found_patterns or 'None detected'}")

        # Step 3: Check for API endpoints or data loading
        print("\n🌐 Step 3: API Endpoint Analysis")

        # Look for API calls in the HTML
        api_patterns = [
            r"api\.luma\.co",
            r"\/api\/",
            r"graphql",
            r"fetch\(",
            r"axios\.",
            r"XMLHttpRequest",
        ]

        found_apis = []
        for pattern in api_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                found_apis.extend(matches)

        if found_apis:
            unique_apis = list(set(found_apis))
            print(f"🔌 Potential API calls found: {len(unique_apis)} unique patterns")
            for api in unique_apis[:5]:
                print(f"  - {api}")
        else:
            print("🔌 No obvious API calls found in HTML")

        # Step 4: Check meta tags and structured data
        print("\n📋 Step 4: Meta Tags and Structured Data")

        meta_tags = soup.find_all("meta")
        relevant_meta = []

        for meta in meta_tags:
            if meta.get("property", "").startswith("og:") or meta.get("name") in [
                "description",
                "keywords",
            ]:
                relevant_meta.append(
                    {
                        "name": meta.get("name") or meta.get("property"),
                        "content": (
                            meta.get("content", "")[:100] + "..."
                            if len(meta.get("content", "")) > 100
                            else meta.get("content", "")
                        ),
                    }
                )

        if relevant_meta:
            print("📝 Relevant meta tags:")
            for meta in relevant_meta[:5]:
                print(f"  {meta['name']}: {meta['content']}")

        # Step 5: Generate summary and recommendations
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)

        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_url": target_url,
            "response_status": response.status_code,
            "content_length": len(response.text),
            "initial_event_links_found": len(event_links),
            "sample_event_links": event_links[:10],
            "javascript_frameworks": js_frameworks,
            "async_loading_patterns": found_patterns,
            "api_patterns_found": list(set(found_apis)) if found_apis else [],
            "meta_tags": relevant_meta,
            "analysis": {
                "likely_spa": len(js_frameworks) > 0 or "next" in found_patterns,
                "uses_dynamic_loading": len(found_patterns) > 0,
                "requires_browser": len(event_links) < 20
                and (len(js_frameworks) > 0 or len(found_patterns) > 0),
            },
        }

        # Save results
        results_file = f"ethcc_page_analysis_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Event links found with simple HTTP: {len(event_links)}")
        print("Expected events: 75+")
        print(f"Gap: {75 - len(event_links)} events missing")

        if results["analysis"]["requires_browser"]:
            print("\n⚠️  DIAGNOSIS: Enhanced Orchestrator Issue Identified")
            print("   - Page uses JavaScript/dynamic loading")
            print("   - Simple HTTP requests miss most content")
            print("   - Requires browser automation (Selenium/Playwright)")
            print("   - Current orchestrator likely using requests/curl")
        else:
            print("\n✅ Simple HTTP should work - other issue present")

        print(f"\n💾 Detailed results saved to: {results_file}")

        return results

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    analyze_ethcc_page()
