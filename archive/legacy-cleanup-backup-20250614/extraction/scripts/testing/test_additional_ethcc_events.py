#!/usr/bin/env python3
"""
Test Additional EthCC Events - Database Verification
Test 6 specific EthCC events from the official luma list to verify database coverage.
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

# Additional EthCC events to test from official list
ADDITIONAL_TEST_EVENTS = [
    {
        "name": "Sea Salt & Smart Contracts",
        "url": "https://lu.ma/dmhda78g",
        "search_terms": ["Sea Salt", "Smart Contracts"],
    },
    {
        "name": "Soirée Sur La Plage",
        "url": "https://lu.ma/8gqkzcns",
        "search_terms": ["Soirée Sur La Plage", "Soirée", "Plage"],
    },
    {
        "name": "RWA Builders & Backers Forum",
        "url": "https://lu.ma/bfecyadf",
        "search_terms": ["RWA Builders", "Backers Forum", "RWA"],
    },
    {
        "name": "The MasterMinds' Boat (🇫🇷 🛥️ ) by SwissBorg",
        "url": "https://lu.ma/1jzz6amh",
        "search_terms": ["MasterMinds Boat", "SwissBorg", "MasterMinds"],
    },
    {
        "name": "JummahDAO Cannes",
        "url": "https://lu.ma/d0u29xie",
        "search_terms": ["JummahDAO", "JummahDAO Cannes"],
    },
    {
        "name": "Pragma Cannes",
        "url": "https://lu.ma/pragma-cannes",
        "search_terms": ["Pragma Cannes", "Pragma"],
    },
]


class AdditionalEthCCTester:
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

        logger.info(
            f"🧪 Testing {len(ADDITIONAL_TEST_EVENTS)} additional EthCC events..."
        )

        found_count = 0
        accessible_count = 0
        ethcc_categorized_count = 0

        for event in ADDITIONAL_TEST_EVENTS:
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
            "total_events_tested": len(ADDITIONAL_TEST_EVENTS),
            "found_in_database": found_count,
            "url_accessible": accessible_count,
            "ethcc_categorized": ethcc_categorized_count,
            "coverage_rate": (found_count / len(ADDITIONAL_TEST_EVENTS)) * 100,
            "ethcc_rate": (ethcc_categorized_count / len(ADDITIONAL_TEST_EVENTS)) * 100,
        }

        logger.info(f"\n📊 TESTING SUMMARY:")
        logger.info(f"   Events tested: {len(ADDITIONAL_TEST_EVENTS)}")
        logger.info(
            f"   Found in database: {found_count} ({(found_count/len(ADDITIONAL_TEST_EVENTS))*100:.1f}%)"
        )
        logger.info(f"   URLs accessible: {accessible_count}")
        logger.info(f"   EthCC categorized: {ethcc_categorized_count}")

        return self.results

    def identify_categorization_candidates(self) -> List[Dict[str, Any]]:
        """Identify events that might need categorization fixes."""
        candidates = []

        for test_result in self.results["test_events"]:
            if (
                test_result["found_in_database"]
                and test_result["analysis"].get("ethcc_categorized", 0) == 0
            ):

                # Check if any matches should be EthCC events
                for match in test_result["database_matches"]:
                    name = match.get("name", "").lower()
                    description = match.get("description", "").lower()

                    # Check for EthCC indicators
                    ethcc_indicators = ["ethcc", "cannes", "eth cc"]
                    has_ethcc_indicator = any(
                        indicator in name + description
                        for indicator in ethcc_indicators
                    )

                    if has_ethcc_indicator:
                        candidates.append(
                            {
                                "event_id": match["id"],
                                "name": match.get("name", ""),
                                "current_category": match.get("category"),
                                "luma_url": match.get("luma_url", ""),
                                "reason": "Found in additional EthCC events test - likely EthCC event",
                                "test_event_name": test_result["name"],
                            }
                        )

        return candidates

    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            timestamp = int(datetime.now().timestamp())
            filename = f"additional_ethcc_test_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {filename}")
        return filename


def main():
    """Main execution function."""
    tester = AdditionalEthCCTester()

    try:
        # Test additional events
        results = tester.test_all_events()

        # Identify categorization candidates
        candidates = tester.identify_categorization_candidates()
        if candidates:
            logger.info(f"\n🔍 CATEGORIZATION CANDIDATES:")
            logger.info(
                f"Found {len(candidates)} events that might need EthCC categorization:"
            )
            for candidate in candidates:
                logger.info(
                    f"   - {candidate['name'][:60]}... (currently: {candidate['current_category']})"
                )

        # Save results
        results_file = tester.save_results()

        # Print detailed summary
        print("\n" + "=" * 70)
        print("ADDITIONAL ETHCC EVENTS TEST RESULTS")
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
