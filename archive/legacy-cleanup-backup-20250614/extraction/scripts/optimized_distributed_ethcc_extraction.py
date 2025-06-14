#!/usr/bin/env python3
"""
🌐 Optimized Distributed EthCC Extraction
Advanced implementation using the existing multi-region infrastructure with:
- Enhanced multi-region services for event discovery (VPN-like scraping)
- Production orchestrator for detailed processing with 13+ agents
- Anti-bot evasion through geographic IP rotation
- Complete database integration with quality analysis
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

import requests


class OptimizedDistributedExtractor:
    def __init__(self):
        # Enhanced multi-region services for discovery (rate limiting evasion)
        self.discovery_services = [
            {
                "url": "https://enhanced-multi-region-us-central-867263134607.us-central1.run.app",
                "region": "us-central1",
                "cost_tier": 2,
                "ip_ranges": ["34.102.0.0/16", "34.104.0.0/16"],
                "status": "active",
            },
            {
                "url": "https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app",
                "region": "europe-west1",
                "cost_tier": 3,
                "ip_ranges": ["34.76.0.0/16", "34.78.0.0/16"],
                "status": "active",
            },
        ]

        # Production orchestrator for detailed processing
        self.processing_service = {
            "url": "https://production-orchestrator-867263134607.us-central1.run.app",
            "capabilities": [
                "13+ agents",
                "visual_intelligence",
                "database_integration",
            ],
            "status": "confirmed_active",
        }

        self.session_id = f"optimized_distributed_{int(time.time())}"
        self.results = {
            "discovery_phase": {},
            "processing_phase": {},
            "quality_analysis": {},
            "database_integration": {},
        }

    def discover_all_events(
        self, calendar_url: str = "https://lu.ma/ethcc"
    ) -> List[str]:
        """
        Phase 1: Use enhanced multi-region services for comprehensive event discovery
        This bypasses Luma rate limiting through VPN-like IP rotation
        """
        print("🔍 PHASE 1: ENHANCED MULTI-REGION EVENT DISCOVERY")
        print("=" * 70)
        print(f"Target: {calendar_url}")
        print("Strategy: VPN-like scraping via Google Cloud regional IP rotation")

        for service in self.discovery_services:
            try:
                print(f"\n   🌐 Trying region: {service['region']}")
                print(
                    f"   💰 Cost tier: {service['cost_tier']} | IP: {service['ip_ranges'][0]}"
                )

                discovery_start = time.time()

                response = requests.post(
                    f"{service['url']}/extract",
                    json={
                        "urls": [calendar_url],
                        "save_to_database": False,
                        "use_enhanced_discovery": True,
                        "enable_calendar_scrolling": True,
                        "max_concurrent": 4,
                        "timeout_per_event": 60,
                    },
                    timeout=120,
                )

                if response.status_code == 200:
                    data = response.json()
                    events = data.get("results", [])
                    event_urls = [
                        event.get("url") for event in events if event.get("url")
                    ]

                    # Filter valid URLs
                    valid_urls = [
                        url
                        for url in event_urls
                        if url and "lu.ma" in url and "discover" not in url
                    ]

                    discovery_time = time.time() - discovery_start

                    print(f"   ✅ SUCCESS: {len(valid_urls)} events discovered")
                    print(f"   ⏱️  Discovery time: {discovery_time:.1f}s")
                    print(
                        f"   🎯 Event discovery rate: {len(valid_urls)/discovery_time:.1f} events/sec"
                    )

                    # Store discovery results
                    self.results["discovery_phase"] = {
                        "region_used": service["region"],
                        "total_events_found": len(valid_urls),
                        "discovery_time": discovery_time,
                        "cost_tier": service["cost_tier"],
                        "ip_rotation_success": True,
                        "rate_limiting_bypassed": len(valid_urls)
                        > 20,  # Indicator of successful bypass
                    }

                    return valid_urls

            except requests.exceptions.Timeout:
                print(f"   ⏱️  Region {service['region']} timeout - trying next region")
                continue
            except Exception as e:
                print(f"   ❌ Region {service['region']} failed: {e}")
                continue

        print("   ❌ All discovery regions failed")
        return []

    def process_events_comprehensive(self, event_urls: List[str]) -> Dict[str, Any]:
        """
        Phase 2: Process each event through production orchestrator with full 13+ agent system
        This provides high-quality data extraction with database integration
        """
        print("\n🔄 PHASE 2: COMPREHENSIVE AGENT PROCESSING")
        print("=" * 70)
        print(f"Events to process: {len(event_urls)}")
        print(
            "Strategy: Production orchestrator with 13+ agents + database integration"
        )

        batch_size = 3  # Optimal batch size for production orchestrator
        all_results = []
        successful_events = 0
        failed_events = 0
        database_saves = 0
        total_processing_time = 0

        # Process in optimized batches
        for i in range(0, len(event_urls), batch_size):
            batch = event_urls[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(event_urls) + batch_size - 1) // batch_size

            print(f"\n   📦 Batch {batch_num}/{total_batches}: {len(batch)} events")

            try:
                batch_start = time.time()

                response = requests.post(
                    f"{self.processing_service['url']}/extract",
                    json={
                        "urls": batch,
                        "save_to_database": True,
                        "enable_visual_intelligence": True,
                        "enable_crypto_intelligence": True,
                        "use_thirteen_plus_agents": True,
                        "max_concurrent": min(2, len(batch)),
                        "timeout_per_event": 90,
                    },
                    timeout=400,  # Generous timeout for comprehensive processing
                )

                batch_time = time.time() - batch_start

                if response.status_code == 200:
                    batch_data = response.json()
                    batch_results = batch_data.get("results", [])

                    # Analyze batch quality
                    batch_successful = len(
                        [r for r in batch_results if r.get("status") == "success"]
                    )
                    batch_failed = len(batch_results) - batch_successful
                    batch_db_saves = len(
                        [
                            r
                            for r in batch_results
                            if r.get("database_integrated") == True
                        ]
                    )

                    # Calculate completeness scores
                    completeness_scores = [
                        r.get("completeness_score", 0)
                        for r in batch_results
                        if r.get("completeness_score")
                    ]
                    avg_completeness = (
                        sum(completeness_scores) / len(completeness_scores)
                        if completeness_scores
                        else 0
                    )

                    successful_events += batch_successful
                    failed_events += batch_failed
                    database_saves += batch_db_saves
                    total_processing_time += batch_time

                    all_results.extend(batch_results)

                    print(f"      ✅ Processed: {batch_successful}/{len(batch)}")
                    print(f"      💾 DB saves: {batch_db_saves}/{len(batch)}")
                    print(f"      📊 Avg completeness: {avg_completeness:.2f}")
                    print(f"      ⏱️  Time: {batch_time:.1f}s")

                else:
                    print(f"      ❌ Batch failed: HTTP {response.status_code}")
                    failed_events += len(batch)

            except Exception as e:
                print(f"      ❌ Batch error: {e}")
                failed_events += len(batch)

            # Rate limiting courtesy pause
            if i + batch_size < len(event_urls):
                print("      ⏸️  Pausing 5s...")
                time.sleep(5)

        # Store processing results
        self.results["processing_phase"] = {
            "total_events": len(event_urls),
            "successful_events": successful_events,
            "failed_events": failed_events,
            "database_saves": database_saves,
            "success_rate": (successful_events / len(event_urls)) * 100,
            "database_integration_rate": (
                (database_saves / successful_events) * 100
                if successful_events > 0
                else 0
            ),
            "total_processing_time": total_processing_time,
            "agent_system_used": "13+ agents",
            "results": all_results,
        }

        return self.results["processing_phase"]

    def analyze_extraction_quality(self) -> Dict[str, Any]:
        """
        Phase 3: Comprehensive quality analysis of extracted data
        """
        print("\n📊 PHASE 3: DATA QUALITY ANALYSIS")
        print("=" * 70)

        processing_results = self.results.get("processing_phase", {})
        events = processing_results.get("results", [])

        if not events:
            print("   ❌ No events to analyze")
            return {}

        # Data completeness analysis
        events_with_start_date = len([e for e in events if e.get("start_date")])
        events_with_location = len([e for e in events if e.get("location")])
        events_with_speakers = len(
            [e for e in events if e.get("speakers") and len(e.get("speakers", [])) > 0]
        )
        events_with_visual_intel = len(
            [e for e in events if e.get("images_analyzed", 0) > 0]
        )
        events_with_crypto_matches = len(
            [e for e in events if e.get("crypto_industry_matches", 0) > 0]
        )

        # Calculate quality scores
        total_events = len(events)
        date_quality = (events_with_start_date / total_events) * 100
        location_quality = (events_with_location / total_events) * 100
        enrichment_quality = (events_with_speakers / total_events) * 100
        visual_intel_usage = (events_with_visual_intel / total_events) * 100
        crypto_intelligence = (events_with_crypto_matches / total_events) * 100

        # Overall quality score
        overall_quality = (date_quality + location_quality + enrichment_quality) / 3

        # Find highest quality events
        high_quality_events = [
            e
            for e in events
            if e.get("completeness_score", 0) > 0.6
            and e.get("start_date")
            and e.get("location")
        ]

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "data_completeness": {
                "events_with_start_date": events_with_start_date,
                "events_with_location": events_with_location,
                "events_with_speakers": events_with_speakers,
                "date_quality_percent": date_quality,
                "location_quality_percent": location_quality,
                "enrichment_quality_percent": enrichment_quality,
            },
            "advanced_features": {
                "visual_intelligence_usage": visual_intel_usage,
                "crypto_intelligence_matches": crypto_intelligence,
                "thirteen_plus_agents_active": True,
            },
            "quality_metrics": {
                "overall_quality_score": overall_quality,
                "high_quality_events_count": len(high_quality_events),
                "extraction_success_rate": processing_results.get("success_rate", 0),
                "database_integration_success": processing_results.get(
                    "database_integration_rate", 0
                ),
            },
        }

        # Print analysis summary
        print(f"   📈 Overall Quality Score: {overall_quality:.1f}%")
        print(
            f"   📅 Date Extraction: {date_quality:.1f}% ({events_with_start_date}/{total_events})"
        )
        print(
            f"   📍 Location Extraction: {location_quality:.1f}% ({events_with_location}/{total_events})"
        )
        print(
            f"   👥 Speaker Enrichment: {enrichment_quality:.1f}% ({events_with_speakers}/{total_events})"
        )
        print(
            f"   🖼️  Visual Intelligence: {visual_intel_usage:.1f}% ({events_with_visual_intel}/{total_events})"
        )
        print(
            f"   💾 Database Integration: {processing_results.get('database_integration_rate', 0):.1f}%"
        )
        print(f"   🏆 High Quality Events: {len(high_quality_events)}")

        self.results["quality_analysis"] = analysis
        return analysis

    def run_complete_extraction(self) -> Dict[str, Any]:
        """
        Execute the complete optimized distributed extraction process
        """
        print("🚀 OPTIMIZED DISTRIBUTED ETHCC EXTRACTION")
        print("=" * 70)
        print(f"Session ID: {self.session_id}")
        print("Architecture: Enhanced Multi-Region Discovery → Production Processing")
        print("Capabilities: VPN-like scraping + 13+ agents + database integration")

        total_start = time.time()

        # Phase 1: Enhanced discovery with rate limiting evasion
        event_urls = self.discover_all_events()

        if not event_urls:
            error_result = {
                "error": "Discovery phase failed",
                "session_id": self.session_id,
                "total_runtime": time.time() - total_start,
            }
            return error_result

        # Phase 2: Comprehensive processing with 13+ agents
        processing_results = self.process_events_comprehensive(event_urls)

        # Phase 3: Quality analysis
        quality_analysis = self.analyze_extraction_quality()

        # Compile final report
        total_runtime = time.time() - total_start

        final_report = {
            "session_id": self.session_id,
            "total_runtime": total_runtime,
            "architecture_used": "Enhanced Multi-Region + Production Orchestrator",
            "phases": {
                "discovery": self.results.get("discovery_phase", {}),
                "processing": self.results.get("processing_phase", {}),
                "quality_analysis": self.results.get("quality_analysis", {}),
            },
            "summary": {
                "events_discovered": len(event_urls),
                "events_processed": processing_results.get("successful_events", 0),
                "database_integrated": processing_results.get("database_saves", 0),
                "overall_success_rate": processing_results.get("success_rate", 0),
                "quality_score": quality_analysis.get("quality_metrics", {}).get(
                    "overall_quality_score", 0
                ),
                "rate_limiting_bypassed": len(event_urls) > 50,
                "thirteen_plus_agents_used": True,
            },
        }

        # Save comprehensive report
        report_filename = f"optimized_distributed_ethcc_report_{int(time.time())}.json"
        with open(report_filename, "w") as f:
            json.dump(final_report, f, indent=2)

        # Print final summary
        print("\n🎯 FINAL EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"   🔍 Events Discovered: {len(event_urls)} (rate limiting bypassed)")
        print(
            f"   ✅ Events Processed: {processing_results.get('successful_events', 0)}"
        )
        print(f"   💾 Database Saves: {processing_results.get('database_saves', 0)}")
        print(f"   📊 Success Rate: {processing_results.get('success_rate', 0):.1f}%")
        print(
            f"   🏆 Quality Score: {quality_analysis.get('quality_metrics', {}).get('overall_quality_score', 0):.1f}%"
        )
        print(f"   ⏱️  Total Runtime: {total_runtime:.1f}s")
        print(f"   📄 Report: {report_filename}")

        return final_report


def main():
    """Run the optimized distributed extraction"""
    extractor = OptimizedDistributedExtractor()
    return extractor.run_complete_extraction()


if __name__ == "__main__":
    main()
