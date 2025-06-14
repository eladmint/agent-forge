#!/usr/bin/env python3
"""
Test Specific EthCC Events - Analysis and Investigation
Test specific events from the EthCC Luma list to verify database coverage.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import sys
import os
import requests
from bs4 import BeautifulSoup

# Add current directory to path
sys.path.insert(0, os.getcwd())

from agent_forge.core.shared.database.client import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test events from EthCC Luma list
TEST_EVENTS = [
    {
        "name": "AI x Web3: The Future Is Trustless",
        "url": None,  # We know this exists but need to find URL
        "search_terms": ["AI x Web3", "Future Is Trustless"],
    },
    {
        "name": "RWA Cannes: Tokenizing Finance",
        "url": "https://lu.ma/fq9v7r71",
        "search_terms": ["RWA Cannes", "Tokenizing Finance"],
    },
    {
        "name": "EASYCON MONACO",
        "url": "https://lu.ma/EASYCONMonaco",
        "search_terms": ["EASYCON MONACO", "EASYCON"],
    },
]


class SpecificEthCCTester:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.results = {
            "test_started": datetime.now().isoformat(),
            "test_events": [],
            "summary": {},
        }

    def test_event_in_database(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Test if a specific event is in our database."""

        event_name = event["name"]
        event_url = event["url"]
        search_terms = event["search_terms"]

        logger.info(f"🔍 Testing: {event_name}")

        result = {
            "name": event_name,
            "url": event_url,
            "found_in_database": False,
            "database_matches": [],
            "url_accessible": None,
            "analysis": {},
        }

        try:
            # 1. Search by URL if provided
            if event_url:
                logger.info(f"   Searching by URL: {event_url}")
                url_response = (
                    self.supabase.table("events")
                    .select("*")
                    .eq("luma_url", event_url)
                    .execute()
                )

                if url_response.data:
                    result["found_in_database"] = True
                    result["database_matches"].extend(url_response.data)
                    logger.info(
                        f"   ✅ Found by URL: {url_response.data[0].get('name', 'No name')}"
                    )
                else:
                    logger.info(f"   ❌ Not found by URL")

            # 2. Search by name/terms
            for term in search_terms:
                logger.info(f"   Searching by term: '{term}'")

                # Search in name
                name_response = (
                    self.supabase.table("events")
                    .select("*")
                    .ilike("name", f"%{term}%")
                    .execute()
                )
                if name_response.data:
                    for match in name_response.data:
                        if match not in result["database_matches"]:
                            result["database_matches"].append(match)
                            result["found_in_database"] = True
                            logger.info(
                                f"   ✅ Found by name: {match.get('name', 'No name')}"
                            )

                # Search in description
                desc_response = (
                    self.supabase.table("events")
                    .select("*")
                    .ilike("description", f"%{term}%")
                    .execute()
                )
                if desc_response.data:
                    for match in desc_response.data:
                        if match not in result["database_matches"]:
                            result["database_matches"].append(match)
                            result["found_in_database"] = True
                            logger.info(
                                f"   ✅ Found by description: {match.get('name', 'No name')}"
                            )

            # 3. Test URL accessibility if provided
            if event_url:
                logger.info(f"   Testing URL accessibility...")
                try:
                    response = requests.get(event_url, timeout=10)
                    result["url_accessible"] = response.status_code == 200

                    if result["url_accessible"]:
                        logger.info(
                            f"   ✅ URL accessible (status: {response.status_code})"
                        )

                        # Extract page title for verification
                        soup = BeautifulSoup(response.content, "html.parser")
                        title = soup.find("title")
                        if title:
                            result["analysis"]["page_title"] = title.get_text().strip()
                            logger.info(
                                f"   📄 Page title: {result['analysis']['page_title']}"
                            )
                    else:
                        logger.warning(
                            f"   ⚠️ URL not accessible (status: {response.status_code})"
                        )
                        result["analysis"]["error"] = f"HTTP {response.status_code}"

                except Exception as e:
                    result["url_accessible"] = False
                    result["analysis"]["error"] = str(e)
                    logger.warning(f"   ❌ URL access failed: {str(e)}")

            # 4. Analysis
            result["analysis"]["search_performed"] = len(search_terms)
            result["analysis"]["matches_found"] = len(result["database_matches"])

            if result["found_in_database"]:
                # Check categories of matches
                categories = [
                    match.get("category") for match in result["database_matches"]
                ]
                result["analysis"]["categories"] = list(set(categories))

                # Check if any are categorized as EthCC
                ethcc_matches = [
                    match
                    for match in result["database_matches"]
                    if match.get("category") == "EthCC Event"
                ]
                result["analysis"]["ethcc_categorized"] = len(ethcc_matches)

                logger.info(
                    f"   📊 Found {len(result['database_matches'])} matches, {len(ethcc_matches)} categorized as EthCC"
                )
            else:
                logger.info(f"   📊 No matches found in database")

        except Exception as e:
            logger.error(f"   ❌ Error testing {event_name}: {str(e)}")
            result["analysis"]["error"] = str(e)

        return result

    def test_all_events(self) -> Dict[str, Any]:
        """Test all specified events."""

        logger.info(f"🧪 Testing {len(TEST_EVENTS)} specific EthCC events...")

        found_count = 0
        accessible_count = 0
        ethcc_categorized_count = 0

        for event in TEST_EVENTS:
            result = self.test_event_in_database(event)
            self.results["test_events"].append(result)

            if result["found_in_database"]:
                found_count += 1

            if result["url_accessible"]:
                accessible_count += 1

            if result["analysis"].get("ethcc_categorized", 0) > 0:
                ethcc_categorized_count += 1

            print()  # Add spacing between events

        self.results["summary"] = {
            "total_events_tested": len(TEST_EVENTS),
            "found_in_database": found_count,
            "url_accessible": accessible_count,
            "ethcc_categorized": ethcc_categorized_count,
            "coverage_rate": (found_count / len(TEST_EVENTS)) * 100,
            "ethcc_rate": (ethcc_categorized_count / len(TEST_EVENTS)) * 100,
        }

        logger.info(f"\n📊 TESTING SUMMARY:")
        logger.info(f"   Events tested: {len(TEST_EVENTS)}")
        logger.info(
            f"   Found in database: {found_count} ({(found_count/len(TEST_EVENTS))*100:.1f}%)"
        )
        logger.info(f"   URLs accessible: {accessible_count}")
        logger.info(f"   EthCC categorized: {ethcc_categorized_count}")

        return self.results

    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            timestamp = int(datetime.now().timestamp())
            filename = f"specific_ethcc_test_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {filename}")
        return filename


def main():
    """Main execution function."""
    tester = SpecificEthCCTester()

    try:
        # Test specific events
        results = tester.test_all_events()

        # Save results
        results_file = tester.save_results()

        # Print detailed summary
        print("\n" + "=" * 70)
        print("SPECIFIC ETHCC EVENTS TEST RESULTS")
        print("=" * 70)

        summary = results["summary"]
        print(f"Total Events Tested: {summary['total_events_tested']}")
        print(
            f"Found in Database: {summary['found_in_database']} ({summary['coverage_rate']:.1f}%)"
        )
        print(f"URLs Accessible: {summary['url_accessible']}")
        print(
            f"EthCC Categorized: {summary['ethcc_categorized']} ({summary['ethcc_rate']:.1f}%)"
        )

        print(f"\nDetailed Results:")
        for i, test_result in enumerate(results["test_events"], 1):
            status = "✅ FOUND" if test_result["found_in_database"] else "❌ MISSING"
            url_status = ""
            if test_result["url"]:
                url_status = (
                    " (URL ✅)" if test_result["url_accessible"] else " (URL ❌)"
                )

            print(f"{i}. {test_result['name']}: {status}{url_status}")

            if test_result["found_in_database"]:
                matches = test_result["analysis"].get("matches_found", 0)
                ethcc_cat = test_result["analysis"].get("ethcc_categorized", 0)
                print(f"   └─ {matches} matches found, {ethcc_cat} EthCC categorized")

        print(f"\nResults saved to: {results_file}")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Fatal error in testing: {str(e)}")
        raise


if __name__ == "__main__":
    main()
