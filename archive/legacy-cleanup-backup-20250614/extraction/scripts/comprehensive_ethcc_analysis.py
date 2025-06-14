#!/usr/bin/env python3
"""
Comprehensive EthCC Data Analysis
Detailed analysis of EthCC events data from Supabase database using correct schema
"""

import logging
import os
import json
import requests
from datetime import datetime
from collections import Counter, defaultdict
import re

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logging.error("Supabase credentials not found in environment variables.")
    exit(1)

class ComprehensiveEthCCAnalyzer:
    def __init__(self):
        self.api_url = f"{SUPABASE_URL}/rest/v1"
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
    def get_all_events(self):
        """Fetch all events from the database."""
        try:
            url = f"{self.api_url}/events"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching events: {e}")
            return []
    
    def analyze_database_schema(self, events):
        """Analyze the actual database schema."""
        if not events:
            return {"error": "No events to analyze"}
        
        sample_event = events[0]
        schema_analysis = {
            "total_fields": len(sample_event.keys()),
            "field_names": list(sample_event.keys()),
            "sample_values": {}
        }
        
        # Get sample values for each field
        for field in sample_event.keys():
            values = [event.get(field) for event in events[:10] if event.get(field) is not None]
            schema_analysis["sample_values"][field] = values[:3] if values else ["No values found"]
        
        return schema_analysis
    
    def analyze_total_events(self, events):
        """Analyze total events and EthCC-specific events."""
        total_events = len(events)
        
        # Find EthCC events using multiple patterns
        ethcc_patterns = [
            r'ethcc',
            r'eth cc',
            r'ethereum community conference',
            r'ethcc[0-9]+',
            r'ethcc\s*[0-9]+',
            r'eth\s*cc\s*[0-9]+',
            r'@ethcc',
            r'#ethcc'
        ]
        
        ethcc_events = []
        pattern_matches = defaultdict(int)
        
        for event in events:
            name = str(event.get('name', '') or '').lower()
            description = str(event.get('description', '') or '').lower()
            combined_text = f"{name} {description}"
            
            is_ethcc = False
            for pattern in ethcc_patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    if not is_ethcc:  # Only add once per event
                        ethcc_events.append(event)
                        is_ethcc = True
                    pattern_matches[pattern] += 1
        
        return {
            "total_events": total_events,
            "ethcc_events": len(ethcc_events),
            "non_ethcc_events": total_events - len(ethcc_events),
            "ethcc_percentage": round((len(ethcc_events) / total_events) * 100, 2),
            "pattern_matches": dict(pattern_matches),
            "ethcc_events_data": ethcc_events
        }
    
    def analyze_data_completeness(self, events):
        """Analyze data completeness using actual schema fields."""
        if not events:
            return {"error": "No events to analyze"}
        
        # Key fields based on actual schema
        key_fields = {
            "name": "Event Name",
            "description": "Event Description", 
            "start_time_iso": "Start Time",
            "end_time_iso": "End Time",
            "location_name": "Location Name",
            "location_address": "Location Address",
            "external_url": "External URL",
            "luma_url": "Luma URL",
            "cost": "Cost Information",
            "category": "Event Category",
            "estimated_attendee_count": "Estimated Attendees",
            "networking_score": "Networking Score",
            "exclusivity_score": "Exclusivity Score",
            "ai_enhanced": "AI Enhanced",
            "completeness_score": "Completeness Score"
        }
        
        total_events = len(events)
        field_analysis = {}
        completeness_scores = []
        
        # Analyze each field
        for field, label in key_fields.items():
            filled_count = 0
            for event in events:
                value = event.get(field)
                if value is not None and str(value).strip() and str(value).strip().lower() not in ['null', 'none', '']:
                    filled_count += 1
            
            percentage = (filled_count / total_events) * 100
            field_analysis[field] = {
                "label": label,
                "filled": filled_count,
                "total": total_events,
                "percentage": round(percentage, 2)
            }
        
        # Calculate custom completeness scores
        essential_fields = ["name", "description", "start_time_iso", "location_name", "external_url"]
        
        for event in events:
            filled_essential = sum(1 for field in essential_fields 
                                 if event.get(field) and str(event.get(field)).strip())
            score = (filled_essential / len(essential_fields)) * 100
            completeness_scores.append(score)
        
        # Quality tiers
        high_quality = sum(1 for score in completeness_scores if score >= 80)
        medium_quality = sum(1 for score in completeness_scores if 50 <= score < 80)
        low_quality = sum(1 for score in completeness_scores if score < 50)
        
        return {
            "total_events": total_events,
            "field_analysis": field_analysis,
            "custom_completeness": {
                "average_score": round(sum(completeness_scores) / len(completeness_scores), 2),
                "high_quality_events": high_quality,
                "medium_quality_events": medium_quality,
                "low_quality_events": low_quality,
                "quality_distribution": {
                    "high (80-100%)": high_quality,
                    "medium (50-79%)": medium_quality,
                    "low (0-49%)": low_quality
                }
            },
            "ai_enhanced_analysis": self.analyze_ai_enhancement(events)
        }
    
    def analyze_ai_enhancement(self, events):
        """Analyze AI enhancement statistics."""
        ai_enhanced_count = sum(1 for event in events if event.get('ai_enhanced'))
        total_events = len(events)
        
        # Analyze completeness scores
        completeness_scores = [event.get('completeness_score') for event in events 
                             if event.get('completeness_score') is not None]
        
        ai_enhanced_scores = [event.get('completeness_score') for event in events 
                            if event.get('ai_enhanced') and event.get('completeness_score') is not None]
        
        return {
            "ai_enhanced_events": ai_enhanced_count,
            "ai_enhancement_percentage": round((ai_enhanced_count / total_events) * 100, 2),
            "completeness_score_analysis": {
                "total_with_scores": len(completeness_scores),
                "average_score": round(sum(completeness_scores) / len(completeness_scores), 2) if completeness_scores else 0,
                "ai_enhanced_average": round(sum(ai_enhanced_scores) / len(ai_enhanced_scores), 2) if ai_enhanced_scores else 0,
                "score_range": {
                    "min": min(completeness_scores) if completeness_scores else 0,
                    "max": max(completeness_scores) if completeness_scores else 0
                }
            }
        }
    
    def analyze_temporal_coverage(self, events):
        """Analyze temporal coverage using actual time fields."""
        temporal_analysis = {
            "total_events": len(events),
            "events_with_start_time": 0,
            "events_with_end_time": 0,
            "temporal_patterns": {},
            "time_distribution": defaultdict(int)
        }
        
        start_times = []
        end_times = []
        dates_found = []
        
        for event in events:
            start_time = event.get('start_time_iso')
            end_time = event.get('end_time_iso')
            
            if start_time:
                temporal_analysis["events_with_start_time"] += 1
                start_times.append(start_time)
                
                # Extract date patterns
                try:
                    if isinstance(start_time, str):
                        # Try to extract date/month patterns
                        date_match = re.search(r'\d{4}-\d{2}-\d{2}', start_time)
                        if date_match:
                            dates_found.append(date_match.group())
                        
                        # Extract month-year for distribution
                        month_match = re.search(r'\d{4}-\d{2}', start_time)
                        if month_match:
                            temporal_analysis["time_distribution"][month_match.group()] += 1
                except:
                    pass
            
            if end_time:
                temporal_analysis["events_with_end_time"] += 1
                end_times.append(end_time)
        
        # Calculate percentages
        temporal_analysis["start_time_percentage"] = round(
            (temporal_analysis["events_with_start_time"] / len(events)) * 100, 2
        )
        temporal_analysis["end_time_percentage"] = round(
            (temporal_analysis["events_with_end_time"] / len(events)) * 100, 2
        )
        
        # Sample times
        temporal_analysis["sample_start_times"] = start_times[:10]
        temporal_analysis["sample_dates_extracted"] = dates_found[:10]
        temporal_analysis["monthly_distribution"] = dict(temporal_analysis["time_distribution"])
        
        return temporal_analysis
    
    def analyze_geographic_coverage(self, events):
        """Analyze geographic coverage using actual location fields."""
        geographic_analysis = {
            "total_events": len(events),
            "events_with_location_name": 0,
            "events_with_location_address": 0,
            "location_patterns": {},
            "city_distribution": Counter(),
            "country_distribution": Counter()
        }
        
        location_names = []
        location_addresses = []
        
        for event in events:
            location_name = event.get('location_name')
            location_address = event.get('location_address')
            
            if location_name and str(location_name).strip():
                geographic_analysis["events_with_location_name"] += 1
                location_names.append(str(location_name).strip())
            
            if location_address and str(location_address).strip():
                geographic_analysis["events_with_location_address"] += 1
                location_addresses.append(str(location_address).strip())
        
        # Analyze location patterns
        all_locations = location_names + location_addresses
        location_counter = Counter(all_locations)
        
        # Extract cities and countries from location data
        city_patterns = [
            (r'brussels|bruxelles', 'Brussels'),
            (r'paris', 'Paris'),
            (r'london', 'London'),
            (r'berlin', 'Berlin'),
            (r'amsterdam', 'Amsterdam'),
            (r'new york|nyc', 'New York'),
            (r'san francisco|sf', 'San Francisco'),
            (r'singapore', 'Singapore'),
            (r'tokyo', 'Tokyo'),
            (r'cannes', 'Cannes')
        ]
        
        country_patterns = [
            (r'belgium|belgique', 'Belgium'),
            (r'france|français', 'France'),
            (r'uk|united kingdom|england', 'United Kingdom'),
            (r'germany|deutschland', 'Germany'),
            (r'netherlands|holland', 'Netherlands'),
            (r'usa|united states|america', 'United States'),
            (r'singapore', 'Singapore'),
            (r'japan', 'Japan')
        ]
        
        for location in all_locations:
            location_lower = location.lower()
            
            # Check city patterns
            for pattern, city in city_patterns:
                if re.search(pattern, location_lower):
                    geographic_analysis["city_distribution"][city] += 1
            
            # Check country patterns  
            for pattern, country in country_patterns:
                if re.search(pattern, location_lower):
                    geographic_analysis["country_distribution"][country] += 1
        
        geographic_analysis.update({
            "location_name_percentage": round(
                (geographic_analysis["events_with_location_name"] / len(events)) * 100, 2
            ),
            "location_address_percentage": round(
                (geographic_analysis["events_with_location_address"] / len(events)) * 100, 2
            ),
            "unique_location_names": len(set(location_names)),
            "unique_location_addresses": len(set(location_addresses)),
            "top_location_names": dict(Counter(location_names).most_common(10)),
            "top_cities": dict(geographic_analysis["city_distribution"].most_common(10)),
            "top_countries": dict(geographic_analysis["country_distribution"].most_common(10)),
            "sample_locations": {
                "names": location_names[:10],
                "addresses": location_addresses[:10]
            }
        })
        
        return geographic_analysis
    
    def analyze_ethcc_specific_quality(self, ethcc_events):
        """Analyze quality metrics specific to EthCC events."""
        if not ethcc_events:
            return {"error": "No EthCC events to analyze"}
        
        analysis = {
            "total_ethcc_events": len(ethcc_events),
            "data_quality": {},
            "content_analysis": {},
            "networking_analysis": {},
            "ai_enhancement": {}
        }
        
        # Data quality for EthCC events
        key_fields = ["name", "description", "start_time_iso", "location_name", "external_url"]
        field_completeness = {}
        
        for field in key_fields:
            filled = sum(1 for event in ethcc_events if event.get(field) and str(event.get(field)).strip())
            field_completeness[field] = {
                "filled": filled,
                "percentage": round((filled / len(ethcc_events)) * 100, 2)
            }
        
        analysis["data_quality"] = field_completeness
        
        # Content analysis
        descriptions = [event.get('description', '') for event in ethcc_events if event.get('description')]
        analysis["content_analysis"] = {
            "events_with_descriptions": len(descriptions),
            "average_description_length": round(sum(len(desc) for desc in descriptions) / len(descriptions), 2) if descriptions else 0,
            "sample_descriptions": descriptions[:3]
        }
        
        # Networking and exclusivity scores
        networking_scores = [event.get('networking_score') for event in ethcc_events if event.get('networking_score') is not None]
        exclusivity_scores = [event.get('exclusivity_score') for event in ethcc_events if event.get('exclusivity_score') is not None]
        
        analysis["networking_analysis"] = {
            "events_with_networking_scores": len(networking_scores),
            "average_networking_score": round(sum(networking_scores) / len(networking_scores), 2) if networking_scores else 0,
            "events_with_exclusivity_scores": len(exclusivity_scores),
            "average_exclusivity_score": round(sum(exclusivity_scores) / len(exclusivity_scores), 2) if exclusivity_scores else 0
        }
        
        # AI enhancement for EthCC events
        ai_enhanced = sum(1 for event in ethcc_events if event.get('ai_enhanced'))
        completeness_scores = [event.get('completeness_score') for event in ethcc_events if event.get('completeness_score') is not None]
        
        analysis["ai_enhancement"] = {
            "ai_enhanced_count": ai_enhanced,
            "ai_enhancement_percentage": round((ai_enhanced / len(ethcc_events)) * 100, 2),
            "average_completeness_score": round(sum(completeness_scores) / len(completeness_scores), 2) if completeness_scores else 0
        }
        
        return analysis
    
    def run_comprehensive_analysis(self):
        """Run all analysis functions."""
        print("Starting Comprehensive EthCC Data Analysis...")
        print("=" * 60)
        
        # Fetch all events
        events = self.get_all_events()
        if not events:
            print("ERROR: No events found in database")
            return None
        
        # Run all analyses
        results = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "database_url": SUPABASE_URL,
                "total_events_analyzed": len(events)
            }
        }
        
        print(f"\nAnalyzing {len(events)} total events...")
        
        # 1. Database Schema Analysis
        print("\n1. Database Schema Analysis...")
        results["database_schema"] = self.analyze_database_schema(events)
        
        # 2. Total Events Analysis
        print("2. Total and EthCC Events Analysis...")
        events_analysis = self.analyze_total_events(events)
        results["events_overview"] = events_analysis
        
        # 3. Data Completeness Analysis
        print("3. Data Completeness Analysis...")
        results["data_completeness"] = self.analyze_data_completeness(events)
        
        # 4. Temporal Coverage Analysis
        print("4. Temporal Coverage Analysis...")
        results["temporal_coverage"] = self.analyze_temporal_coverage(events)
        
        # 5. Geographic Coverage Analysis
        print("5. Geographic Coverage Analysis...")
        results["geographic_coverage"] = self.analyze_geographic_coverage(events)
        
        # 6. EthCC-Specific Quality Analysis
        print("6. EthCC-Specific Quality Analysis...")
        ethcc_events = events_analysis.get("ethcc_events_data", [])
        results["ethcc_specific_analysis"] = self.analyze_ethcc_specific_quality(ethcc_events)
        
        return results
    
    def generate_report(self, results):
        """Generate a comprehensive report."""
        if not results:
            return
        
        print("\n" + "="*80)
        print("COMPREHENSIVE ETHCC DATA ANALYSIS REPORT")
        print("="*80)
        
        # Overview
        overview = results.get("events_overview", {})
        print(f"\n📊 OVERVIEW:")
        print(f"   Total Events in Database: {overview.get('total_events', 0)}")
        print(f"   EthCC-Related Events: {overview.get('ethcc_events', 0)}")
        print(f"   EthCC Percentage: {overview.get('ethcc_percentage', 0)}%")
        
        # Data Quality
        completeness = results.get("data_completeness", {})
        if "custom_completeness" in completeness:
            custom = completeness["custom_completeness"]
            print(f"\n📈 DATA QUALITY METRICS:")
            print(f"   Average Completeness Score: {custom.get('average_score', 0)}%")
            print(f"   High Quality Events (80-100%): {custom.get('high_quality_events', 0)}")
            print(f"   Medium Quality Events (50-79%): {custom.get('medium_quality_events', 0)}")
            print(f"   Low Quality Events (0-49%): {custom.get('low_quality_events', 0)}")
        
        # AI Enhancement
        if "ai_enhanced_analysis" in completeness:
            ai_stats = completeness["ai_enhanced_analysis"]
            print(f"\n🤖 AI ENHANCEMENT STATISTICS:")
            print(f"   AI Enhanced Events: {ai_stats.get('ai_enhanced_events', 0)}")
            print(f"   AI Enhancement Rate: {ai_stats.get('ai_enhancement_percentage', 0)}%")
            if "completeness_score_analysis" in ai_stats:
                scores = ai_stats["completeness_score_analysis"]
                print(f"   Average Completeness Score: {scores.get('average_score', 0)}")
                print(f"   AI Enhanced Average Score: {scores.get('ai_enhanced_average', 0)}")
        
        # Geographic Coverage
        geo = results.get("geographic_coverage", {})
        print(f"\n🌍 GEOGRAPHIC COVERAGE:")
        print(f"   Events with Location Names: {geo.get('events_with_location_name', 0)} ({geo.get('location_name_percentage', 0)}%)")
        print(f"   Events with Location Addresses: {geo.get('events_with_location_address', 0)} ({geo.get('location_address_percentage', 0)}%)")
        print(f"   Unique Locations: {geo.get('unique_location_names', 0)} names, {geo.get('unique_location_addresses', 0)} addresses")
        
        if "top_cities" in geo and geo["top_cities"]:
            print(f"   Top Cities: {', '.join(f'{city} ({count})' for city, count in list(geo['top_cities'].items())[:5])}")
        
        if "top_countries" in geo and geo["top_countries"]:
            print(f"   Top Countries: {', '.join(f'{country} ({count})' for country, count in list(geo['top_countries'].items())[:5])}")
        
        # Temporal Coverage
        temporal = results.get("temporal_coverage", {})
        print(f"\n📅 TEMPORAL COVERAGE:")
        print(f"   Events with Start Times: {temporal.get('events_with_start_time', 0)} ({temporal.get('start_time_percentage', 0)}%)")
        print(f"   Events with End Times: {temporal.get('events_with_end_time', 0)} ({temporal.get('end_time_percentage', 0)}%)")
        
        if "monthly_distribution" in temporal and temporal["monthly_distribution"]:
            print("   Monthly Distribution:")
            for month, count in sorted(temporal["monthly_distribution"].items()):
                print(f"      {month}: {count} events")
        
        # EthCC Specific Analysis
        ethcc = results.get("ethcc_specific_analysis", {})
        if not ethcc.get("error"):
            print(f"\n🏆 ETHCC-SPECIFIC ANALYSIS:")
            print(f"   Total EthCC Events: {ethcc.get('total_ethcc_events', 0)}")
            
            if "data_quality" in ethcc:
                print("   EthCC Data Quality:")
                for field, data in ethcc["data_quality"].items():
                    print(f"      {field}: {data['filled']}/{ethcc.get('total_ethcc_events', 0)} ({data['percentage']}%)")
            
            if "ai_enhancement" in ethcc:
                ai_ethcc = ethcc["ai_enhancement"]
                print(f"   EthCC AI Enhancement: {ai_ethcc.get('ai_enhanced_count', 0)}/{ethcc.get('total_ethcc_events', 0)} ({ai_ethcc.get('ai_enhancement_percentage', 0)}%)")
                print(f"   EthCC Average Completeness: {ai_ethcc.get('average_completeness_score', 0)}")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_ethcc_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 DETAILED REPORT SAVED:")
        print(f"   File: {filename}")
        print(f"   Size: {os.path.getsize(filename)} bytes")
        
        print("\n" + "="*80)
        
        return filename

def main():
    """Main execution function."""
    try:
        analyzer = ComprehensiveEthCCAnalyzer()
        results = analyzer.run_comprehensive_analysis()
        
        if results:
            report_file = analyzer.generate_report(results)
            print(f"\n✅ Analysis Complete! Detailed report saved to: {report_file}")
        else:
            print("\n❌ Analysis failed - no results generated")
            
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()