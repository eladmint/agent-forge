#!/usr/bin/env python3
"""
Investigate Red Team Scraping Gap
Analyze why "Red Team vs. Blue Team Live Simulation" wasn't captured initially from https://lu.ma/ethcc
and identify improvements for scraping agents.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime

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


class RedTeamScrapingInvestigator:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.results = {
            "investigation_started": datetime.now().isoformat(),
            "red_team_analysis": {},
            "ethcc_page_analysis": {},
            "database_analysis": {},
            "scraping_gaps": [],
            "recommendations": [],
        }

    def analyze_red_team_event_history(self):
        """Analyze the Red Team event in our database to understand when/how it was added."""
        logger.info("🔍 Analyzing Red Team event history in database...")

        try:
            # Search for Red Team event
            red_team_response = (
                self.supabase.table("events")
                .select("*")
                .ilike("name", "%Red Team%")
                .execute()
            )

            if red_team_response.data:
                event = red_team_response.data[0]
                logger.info(f"   ✅ Found Red Team event: {event.get('name')}")
                logger.info(f"   📅 Created: {event.get('created_at')}")
                logger.info(f"   📅 Updated: {event.get('updated_at')}")
                logger.info(f"   🏷️ Category: {event.get('category')}")
                logger.info(f"   🔗 URL: {event.get('luma_url')}")

                # Analyze raw_scraped_data to understand extraction method
                raw_data = event.get("raw_scraped_data", {})
                if raw_data:
                    logger.info(
                        f"   📊 Extraction method: {raw_data.get('extraction_method', 'Unknown')}"
                    )
                    logger.info(
                        f"   📊 Data sources: {raw_data.get('data_sources', [])}"
                    )
                    logger.info(
                        f"   📊 Completeness score: {raw_data.get('completeness_score', 'N/A')}"
                    )

                    if "scraped_at" in raw_data:
                        scraped_timestamp = raw_data["scraped_at"]
                        scraped_date = (
                            datetime.fromtimestamp(scraped_timestamp)
                            if isinstance(scraped_timestamp, (int, float))
                            else "Invalid timestamp"
                        )
                        logger.info(f"   📊 Scraped at: {scraped_date}")

                self.results["red_team_analysis"] = {
                    "found": True,
                    "event_data": event,
                    "extraction_method": raw_data.get("extraction_method"),
                    "created_at": event.get("created_at"),
                    "was_initially_miscategorized": True,  # We just fixed it
                }
            else:
                logger.warning("   ❌ Red Team event not found in database")
                self.results["red_team_analysis"] = {"found": False}

        except Exception as e:
            logger.error(f"   ❌ Error analyzing Red Team event: {str(e)}")
            self.results["red_team_analysis"] = {"error": str(e)}

    def analyze_ethcc_page_content(self):
        """Analyze the main EthCC page to understand link structure and content."""
        logger.info("🔍 Analyzing https://lu.ma/ethcc page content...")

        try:
            response = requests.get("https://lu.ma/ethcc", timeout=15)
            if response.status_code != 200:
                logger.error(
                    f"   ❌ Failed to fetch EthCC page: HTTP {response.status_code}"
                )
                return

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for links to Red Team event
            red_team_links = []
            all_links = soup.find_all("a", href=True)

            logger.info(f"   📊 Total links found: {len(all_links)}")

            # Search for Red Team related links
            for link in all_links:
                href = link.get("href", "")
                text = link.get_text().strip()

                if (
                    "red team" in text.lower()
                    or "blue team" in text.lower()
                    or "kuhtg0fx" in href
                ):
                    red_team_links.append(
                        {
                            "href": href,
                            "text": text,
                            "full_url": (
                                f"https://lu.ma{href}" if href.startswith("/") else href
                            ),
                        }
                    )
                    logger.info(f"   🎯 Found Red Team link: {text} -> {href}")

            # Look for event cards or sections
            event_cards = soup.find_all(
                ["div", "article", "section"],
                class_=re.compile(r"event|card|item", re.I),
            )
            logger.info(f"   📊 Event-like elements found: {len(event_cards)}")

            # Search for Red Team in event cards
            red_team_cards = []
            for card in event_cards:
                card_text = card.get_text().lower()
                if "red team" in card_text or "blue team" in card_text:
                    red_team_cards.append(
                        {
                            "text": card.get_text().strip()[:200] + "...",
                            "html": str(card)[:300] + "...",
                        }
                    )

            # Look for dynamic content indicators
            script_tags = soup.find_all("script")
            has_dynamic_loading = False
            for script in script_tags:
                script_content = script.get_text()
                if any(
                    keyword in script_content
                    for keyword in ["fetch", "XMLHttpRequest", "loadMore", "paginate"]
                ):
                    has_dynamic_loading = True
                    break

            self.results["ethcc_page_analysis"] = {
                "total_links": len(all_links),
                "red_team_links_found": len(red_team_links),
                "red_team_links": red_team_links,
                "red_team_cards_found": len(red_team_cards),
                "red_team_cards": red_team_cards,
                "has_dynamic_loading": has_dynamic_loading,
                "page_size_kb": len(response.content) / 1024,
            }

            if red_team_links:
                logger.info(
                    f"   ✅ Found {len(red_team_links)} Red Team links on EthCC page"
                )
            else:
                logger.warning("   ⚠️ No Red Team links found on EthCC page")
                self.results["scraping_gaps"].append(
                    "Red Team event not visible on main EthCC page"
                )

        except Exception as e:
            logger.error(f"   ❌ Error analyzing EthCC page: {str(e)}")
            self.results["ethcc_page_analysis"] = {"error": str(e)}

    def analyze_database_extraction_patterns(self):
        """Analyze database to understand extraction patterns and potential gaps."""
        logger.info("🔍 Analyzing database extraction patterns...")

        try:
            # Get all EthCC events
            ethcc_response = (
                self.supabase.table("events")
                .select("*")
                .eq("category", "EthCC Event")
                .execute()
            )
            ethcc_events = ethcc_response.data

            logger.info(f"   📊 Total EthCC events: {len(ethcc_events)}")

            # Analyze extraction methods
            extraction_methods = {}
            data_sources = {}
            scraped_dates = []

            for event in ethcc_events:
                raw_data = event.get("raw_scraped_data", {})

                # Track extraction methods
                method = raw_data.get("extraction_method", "unknown")
                extraction_methods[method] = extraction_methods.get(method, 0) + 1

                # Track data sources
                sources = raw_data.get("data_sources", [])
                if isinstance(sources, list):
                    for source in sources:
                        data_sources[source] = data_sources.get(source, 0) + 1

                # Track scraping dates
                if "scraped_at" in raw_data:
                    scraped_dates.append(raw_data["scraped_at"])

            # Find events with URLs containing specific patterns
            luma_events = [
                e
                for e in ethcc_events
                if e.get("luma_url", "").startswith("https://lu.ma/")
            ]

            # Look for events that might have been missed initially
            recent_additions = [
                e
                for e in ethcc_events
                if e.get("created_at", "").startswith("2025-06-04")
            ]

            logger.info(f"   📊 Extraction methods: {extraction_methods}")
            logger.info(f"   📊 Data sources: {data_sources}")
            logger.info(f"   📊 Luma events: {len(luma_events)}")
            logger.info(f"   📊 Recent additions (June 4): {len(recent_additions)}")

            self.results["database_analysis"] = {
                "total_ethcc_events": len(ethcc_events),
                "extraction_methods": extraction_methods,
                "data_sources": data_sources,
                "luma_events_count": len(luma_events),
                "recent_additions_count": len(recent_additions),
                "recent_additions": [e.get("name") for e in recent_additions],
            }

        except Exception as e:
            logger.error(f"   ❌ Error analyzing database patterns: {str(e)}")
            self.results["database_analysis"] = {"error": str(e)}

    def test_current_link_finder_agent(self):
        """Test the current LinkFinderAgent against the EthCC page."""
        logger.info("🔍 Testing current LinkFinderAgent capabilities...")

        try:
            # Import and test LinkFinderAgent
            from extraction.agents.experimental.link_finder_agent import LinkFinderAgent

            agent = LinkFinderAgent()

            # Test on EthCC page
            logger.info("   🤖 Running LinkFinderAgent on https://lu.ma/ethcc...")
            results = agent.find_event_links("https://lu.ma/ethcc")

            if results and hasattr(results, "links_found"):
                links = results.links_found
                logger.info(f"   📊 LinkFinderAgent found {len(links)} links")

                # Check if Red Team URL is in the results
                red_team_url = "https://lu.ma/kuhtg0fx"
                red_team_found = any(red_team_url in str(link) for link in links)

                logger.info(
                    f"   🎯 Red Team URL found by LinkFinderAgent: {red_team_found}"
                )

                # Sample some links for analysis
                sample_links = links[:10] if len(links) > 10 else links
                logger.info("   📋 Sample links found:")
                for i, link in enumerate(sample_links, 1):
                    logger.info(f"      {i}. {link}")

                self.results["link_finder_test"] = {
                    "total_links_found": len(links),
                    "red_team_found": red_team_found,
                    "sample_links": sample_links,
                    "test_successful": True,
                }

                if not red_team_found:
                    self.results["scraping_gaps"].append(
                        "LinkFinderAgent did not discover Red Team event URL"
                    )

            else:
                logger.warning("   ⚠️ LinkFinderAgent returned no results")
                self.results["link_finder_test"] = {
                    "test_successful": False,
                    "error": "No results returned",
                }

        except Exception as e:
            logger.error(f"   ❌ Error testing LinkFinderAgent: {str(e)}")
            self.results["link_finder_test"] = {
                "test_successful": False,
                "error": str(e),
            }

    def generate_improvement_recommendations(self):
        """Generate recommendations based on investigation findings."""
        logger.info("💡 Generating improvement recommendations...")

        recommendations = []

        # Based on Red Team analysis
        if self.results["red_team_analysis"].get("was_initially_miscategorized"):
            recommendations.append(
                {
                    "category": "Categorization",
                    "issue": "Events found but miscategorized",
                    "recommendation": "Implement stricter EthCC event detection patterns in extraction pipeline",
                    "priority": "High",
                    "implementation": "Add EthCC keyword detection and date-based filtering during initial extraction",
                }
            )

        # Based on EthCC page analysis
        ethcc_analysis = self.results.get("ethcc_page_analysis", {})
        if ethcc_analysis.get("has_dynamic_loading"):
            recommendations.append(
                {
                    "category": "Dynamic Content",
                    "issue": "EthCC page uses dynamic loading",
                    "recommendation": "Enhance LinkFinderAgent with JavaScript execution capabilities",
                    "priority": "High",
                    "implementation": "Use Playwright or Selenium to wait for dynamic content loading",
                }
            )

        # If Red Team wasn't found on main page
        if ethcc_analysis.get("red_team_links_found", 0) == 0:
            recommendations.append(
                {
                    "category": "Link Discovery",
                    "issue": "Some events not visible on main conference page",
                    "recommendation": "Implement multi-level scraping: main page + pagination + event discovery",
                    "priority": "Medium",
                    "implementation": 'Add pagination detection and "load more" button clicking',
                }
            )

        # Based on database patterns
        db_analysis = self.results.get("database_analysis", {})
        extraction_methods = db_analysis.get("extraction_methods", {})

        if "manual_addition" in extraction_methods:
            recommendations.append(
                {
                    "category": "Automated Discovery",
                    "issue": f"{extraction_methods.get('manual_addition', 0)} events required manual addition",
                    "recommendation": "Implement fallback discovery mechanisms",
                    "priority": "Medium",
                    "implementation": "Add alternative scraping strategies when primary methods fail",
                }
            )

        # Based on LinkFinder test results
        link_finder_test = self.results.get("link_finder_test", {})
        if not link_finder_test.get("red_team_found", True):
            recommendations.append(
                {
                    "category": "Agent Reliability",
                    "issue": "LinkFinderAgent missing some event URLs",
                    "recommendation": "Improve URL extraction patterns and add content analysis",
                    "priority": "High",
                    "implementation": "Add multiple extraction strategies: CSS selectors, text patterns, and semantic analysis",
                }
            )

        # General recommendations
        recommendations.extend(
            [
                {
                    "category": "Monitoring",
                    "issue": "No automated detection of missed events",
                    "recommendation": "Implement comprehensive event discovery validation",
                    "priority": "Medium",
                    "implementation": "Create automated tests that verify all known events are discoverable",
                },
                {
                    "category": "Robustness",
                    "issue": "Single-point-of-failure in event discovery",
                    "recommendation": "Implement multi-agent redundancy for critical conferences",
                    "priority": "Low",
                    "implementation": "Run multiple scraping agents with different strategies and merge results",
                },
            ]
        )

        self.results["recommendations"] = recommendations

        logger.info(
            f"   💡 Generated {len(recommendations)} improvement recommendations"
        )
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"      {i}. {rec['category']}: {rec['issue']}")

    def run_investigation(self):
        """Run the complete investigation."""
        logger.info("🚀 Starting Red Team scraping gap investigation...")

        # Run all analysis components
        self.analyze_red_team_event_history()
        self.analyze_ethcc_page_content()
        self.analyze_database_extraction_patterns()
        self.test_current_link_finder_agent()
        self.generate_improvement_recommendations()

        # Save results
        timestamp = int(datetime.now().timestamp())
        filename = f"red_team_scraping_investigation_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"📄 Investigation results saved to {filename}")

        return self.results, filename


def main():
    """Main execution function."""

    print("=" * 80)
    print("RED TEAM SCRAPING GAP INVESTIGATION")
    print("=" * 80)
    print(
        "Investigating why 'Red Team vs. Blue Team Live Simulation' wasn't initially captured"
    )
    print("and analyzing scraping pipeline for improvements")
    print()

    investigator = RedTeamScrapingInvestigator()
    results, filename = investigator.run_investigation()

    print("\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)

    # Red Team Analysis
    red_team = results.get("red_team_analysis", {})
    if red_team.get("found"):
        print("✅ Red Team Event Found in Database:")
        print(f"   Extraction Method: {red_team.get('extraction_method', 'Unknown')}")
        print(f"   Created: {red_team.get('created_at', 'Unknown')}")
        print(
            f"   Was Miscategorized: {red_team.get('was_initially_miscategorized', 'Unknown')}"
        )
    else:
        print("❌ Red Team Event Not Found in Database")

    # EthCC Page Analysis
    ethcc_page = results.get("ethcc_page_analysis", {})
    if "total_links" in ethcc_page:
        print("\n📊 EthCC Page Analysis:")
        print(f"   Total Links: {ethcc_page['total_links']}")
        print(f"   Red Team Links Found: {ethcc_page['red_team_links_found']}")
        print(f"   Has Dynamic Loading: {ethcc_page['has_dynamic_loading']}")
        print(f"   Page Size: {ethcc_page['page_size_kb']:.1f} KB")

    # Database Analysis
    db_analysis = results.get("database_analysis", {})
    if "total_ethcc_events" in db_analysis:
        print("\n📊 Database Analysis:")
        print(f"   Total EthCC Events: {db_analysis['total_ethcc_events']}")
        print(f"   Extraction Methods: {db_analysis['extraction_methods']}")
        print(f"   Recent Additions: {db_analysis['recent_additions_count']}")

    # LinkFinder Test
    link_finder = results.get("link_finder_test", {})
    if link_finder.get("test_successful"):
        print("\n🤖 LinkFinderAgent Test:")
        print(f"   Links Found: {link_finder['total_links_found']}")
        print(f"   Red Team Found: {link_finder['red_team_found']}")
    else:
        print(
            f"\n❌ LinkFinderAgent Test Failed: {link_finder.get('error', 'Unknown')}"
        )

    # Scraping Gaps
    gaps = results.get("scraping_gaps", [])
    if gaps:
        print("\n⚠️ Identified Scraping Gaps:")
        for i, gap in enumerate(gaps, 1):
            print(f"   {i}. {gap}")

    # Recommendations
    recommendations = results.get("recommendations", [])
    print(f"\n💡 Improvement Recommendations ({len(recommendations)} total):")

    high_priority = [r for r in recommendations if r["priority"] == "High"]
    medium_priority = [r for r in recommendations if r["priority"] == "Medium"]

    if high_priority:
        print("\n   🔴 HIGH PRIORITY:")
        for i, rec in enumerate(high_priority, 1):
            print(f"      {i}. {rec['category']}: {rec['recommendation']}")

    if medium_priority:
        print("\n   🟡 MEDIUM PRIORITY:")
        for i, rec in enumerate(medium_priority, 1):
            print(f"      {i}. {rec['category']}: {rec['recommendation']}")

    print(f"\n📄 Detailed results saved to: {filename}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    main()
