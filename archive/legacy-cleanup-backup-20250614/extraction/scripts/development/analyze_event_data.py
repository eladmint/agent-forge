#!/usr/bin/env python3
"""
Event Data Analysis Script for TokenHunter Database
Analyzes current event data structure and quality to inform filtering strategy.
"""

import datetime
import json
import logging
import os
import sys
from collections import defaultdict
from typing import Any, Dict

import pytz
from dateutil import parser as date_parser
from dateutil.parser import ParserError

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_supabase_client():
    """Get Supabase client for database access."""
    try:
        from agent_forge.core.shared.database.client import get_supabase_client

        return get_supabase_client()
    except Exception as e:
        logger.error(f"Failed to get Supabase client: {e}")
        return None


def analyze_date_field(value: Any, field_name: str) -> Dict[str, Any]:
    """Analyze a date field value and extract information."""
    analysis = {
        "field_name": field_name,
        "raw_value": value,
        "value_type": type(value).__name__,
        "is_null": value is None,
        "is_empty": False,
        "is_tbd": False,
        "is_parseable": False,
        "parsed_date": None,
        "parse_error": None,
        "timezone_aware": False,
    }

    if value is None:
        analysis["is_null"] = True
        return analysis

    if isinstance(value, str):
        if not value.strip():
            analysis["is_empty"] = True
            return analysis

        if value.upper() in [
            "TBD",
            "N/A",
            "TBA",
            "TO BE DETERMINED",
            "TO BE ANNOUNCED",
        ]:
            analysis["is_tbd"] = True
            return analysis

        # Try to parse the date string
        try:
            parsed = date_parser.parse(value)
            analysis["is_parseable"] = True
            analysis["parsed_date"] = parsed.isoformat()
            analysis["timezone_aware"] = parsed.tzinfo is not None
        except (ParserError, ValueError, TypeError) as e:
            analysis["parse_error"] = str(e)

    elif isinstance(value, datetime.datetime):
        analysis["is_parseable"] = True
        analysis["parsed_date"] = value.isoformat()
        analysis["timezone_aware"] = value.tzinfo is not None

    return analysis


def analyze_event_completeness(event: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze completeness of an event record."""
    date_fields = ["start_time_iso", "end_time_iso"]

    # Also check raw_scraped_data for additional date fields
    raw_data = event.get("raw_scraped_data", {})
    if isinstance(raw_data, dict):
        additional_fields = [
            "start_time",
            "end_time",
            "start_date",
            "end_date",
            "primary_date_str",
            "primary_time_str",
        ]
        for field in additional_fields:
            if field in raw_data:
                date_fields.append(f"raw.{field}")

    analysis = {
        "event_id": event.get("id", "unknown"),
        "event_name": event.get("name", "Unknown Event"),
        "has_any_date": False,
        "has_start_date": False,
        "has_end_date": False,
        "has_iso_dates": False,
        "date_fields_analysis": {},
        "best_date_field": None,
        "is_past_event": None,
        "is_undated": True,
    }

    current_time = datetime.datetime.now(pytz.UTC)
    best_date = None
    best_field = None

    for field in date_fields:
        # Handle both direct fields and raw_scraped_data fields
        if field.startswith("raw."):
            actual_field = field[4:]  # Remove 'raw.' prefix
            value = raw_data.get(actual_field) if isinstance(raw_data, dict) else None
        else:
            value = event.get(field)

        if value is not None:
            field_analysis = analyze_date_field(value, field)
            analysis["date_fields_analysis"][field] = field_analysis

            if field_analysis["is_parseable"]:
                analysis["has_any_date"] = True
                analysis["is_undated"] = False

                if "start" in field:
                    analysis["has_start_date"] = True
                if "end" in field:
                    analysis["has_end_date"] = True
                if "iso" in field:
                    analysis["has_iso_dates"] = True

                # Determine best date for past/future classification
                if best_date is None or "iso" in field or "start" in field:
                    try:
                        parsed_date = date_parser.parse(field_analysis["parsed_date"])
                        if parsed_date.tzinfo is None:
                            parsed_date = pytz.timezone("Asia/Dubai").localize(
                                parsed_date
                            )
                        best_date = parsed_date
                        best_field = field
                    except:
                        pass

    if best_date:
        analysis["best_date_field"] = best_field
        analysis["is_past_event"] = best_date < current_time

    return analysis


def analyze_database_events():
    """Main analysis function to examine all events in the database."""
    client = get_supabase_client()
    if not client:
        logger.error("Cannot proceed without database connection")
        return None

    logger.info("Starting comprehensive event data analysis...")

    try:
        # Fetch all events with relevant fields
        logger.info("Fetching all events from database...")
        response = (
            client.table("events")
            .select(
                "id, name, description, start_time_iso, end_time_iso, "
                "timezone, location_name, location_address, "
                "luma_url, created_at, category, cost, raw_scraped_data"
            )
            .execute()
        )

        if not response.data:
            logger.warning("No events found in database")
            return None

        events = response.data
        logger.info(f"Analyzing {len(events)} events...")

        # Initialize analysis containers
        stats = {
            "total_events": len(events),
            "events_with_dates": 0,
            "events_without_dates": 0,
            "past_events": 0,
            "future_events": 0,
            "undated_events": 0,
            "events_with_iso_dates": 0,
            "events_with_start_dates": 0,
            "events_with_end_dates": 0,
            "date_field_usage": defaultdict(int),
            "date_field_quality": defaultdict(list),
            "timezone_analysis": defaultdict(int),
            "date_range_analysis": {
                "earliest_date": None,
                "latest_date": None,
                "date_distribution": defaultdict(int),
            },
        }

        detailed_analysis = []
        date_parsing_errors = []

        # Analyze each event
        for event in events:
            analysis = analyze_event_completeness(event)
            detailed_analysis.append(analysis)

            # Update statistics
            if analysis["has_any_date"]:
                stats["events_with_dates"] += 1

                if analysis["is_past_event"] is True:
                    stats["past_events"] += 1
                elif analysis["is_past_event"] is False:
                    stats["future_events"] += 1
            else:
                stats["events_without_dates"] += 1
                stats["undated_events"] += 1

            if analysis["has_iso_dates"]:
                stats["events_with_iso_dates"] += 1
            if analysis["has_start_date"]:
                stats["events_with_start_dates"] += 1
            if analysis["has_end_date"]:
                stats["events_with_end_dates"] += 1

            # Analyze date field usage and quality
            for field, field_analysis in analysis["date_fields_analysis"].items():
                if not field_analysis["is_null"]:
                    stats["date_field_usage"][field] += 1

                if field_analysis["is_parseable"]:
                    stats["date_field_quality"][field].append("parseable")
                elif field_analysis["is_tbd"]:
                    stats["date_field_quality"][field].append("tbd")
                elif field_analysis["is_empty"]:
                    stats["date_field_quality"][field].append("empty")
                elif field_analysis["parse_error"]:
                    stats["date_field_quality"][field].append("error")
                    date_parsing_errors.append(
                        {
                            "event_id": analysis["event_id"],
                            "field": field,
                            "value": field_analysis["raw_value"],
                            "error": field_analysis["parse_error"],
                        }
                    )

            # Timezone analysis
            timezone = event.get("timezone")
            if timezone:
                stats["timezone_analysis"][timezone] += 1
            else:
                stats["timezone_analysis"]["null"] += 1

            # Date range analysis
            if analysis["best_date_field"]:
                try:
                    best_date_str = analysis["date_fields_analysis"][
                        analysis["best_date_field"]
                    ]["parsed_date"]
                    best_date = date_parser.parse(best_date_str).date()

                    if (
                        stats["date_range_analysis"]["earliest_date"] is None
                        or best_date < stats["date_range_analysis"]["earliest_date"]
                    ):
                        stats["date_range_analysis"]["earliest_date"] = best_date

                    if (
                        stats["date_range_analysis"]["latest_date"] is None
                        or best_date > stats["date_range_analysis"]["latest_date"]
                    ):
                        stats["date_range_analysis"]["latest_date"] = best_date

                    # Group by month for distribution
                    month_key = best_date.strftime("%Y-%m")
                    stats["date_range_analysis"]["date_distribution"][month_key] += 1

                except Exception as e:
                    logger.debug(f"Error processing date for range analysis: {e}")

        # Convert defaultdicts to regular dicts for JSON serialization
        stats["date_field_usage"] = dict(stats["date_field_usage"])
        stats["timezone_analysis"] = dict(stats["timezone_analysis"])
        stats["date_range_analysis"]["date_distribution"] = dict(
            stats["date_range_analysis"]["date_distribution"]
        )

        # Convert dates to strings for JSON serialization
        if stats["date_range_analysis"]["earliest_date"]:
            stats["date_range_analysis"]["earliest_date"] = stats[
                "date_range_analysis"
            ]["earliest_date"].isoformat()
        if stats["date_range_analysis"]["latest_date"]:
            stats["date_range_analysis"]["latest_date"] = stats["date_range_analysis"][
                "latest_date"
            ].isoformat()

        # Calculate percentages and quality metrics
        total = stats["total_events"]
        stats["percentages"] = {
            "events_with_dates": round((stats["events_with_dates"] / total) * 100, 1),
            "events_without_dates": round(
                (stats["events_without_dates"] / total) * 100, 1
            ),
            "past_events": round((stats["past_events"] / total) * 100, 1),
            "future_events": round((stats["future_events"] / total) * 100, 1),
            "undated_events": round((stats["undated_events"] / total) * 100, 1),
            "events_with_iso_dates": round(
                (stats["events_with_iso_dates"] / total) * 100, 1
            ),
        }

        # Prepare final analysis
        final_analysis = {
            "analysis_timestamp": datetime.datetime.now().isoformat(),
            "summary_statistics": stats,
            "date_parsing_errors": date_parsing_errors[:10],  # First 10 errors
            "total_parsing_errors": len(date_parsing_errors),
            "sample_events": {
                "with_complete_dates": [],
                "with_partial_dates": [],
                "without_dates": [],
                "past_events": [],
                "future_events": [],
            },
            "recommendations": [],
        }

        # Collect sample events for each category
        for analysis in detailed_analysis[:100]:  # Limit to first 100 for samples
            if (
                analysis["has_any_date"]
                and analysis["has_start_date"]
                and analysis["has_end_date"]
            ):
                if len(final_analysis["sample_events"]["with_complete_dates"]) < 3:
                    final_analysis["sample_events"]["with_complete_dates"].append(
                        {
                            "id": analysis["event_id"],
                            "name": analysis["event_name"],
                            "best_date_field": analysis["best_date_field"],
                        }
                    )

            elif analysis["has_any_date"]:
                if len(final_analysis["sample_events"]["with_partial_dates"]) < 3:
                    final_analysis["sample_events"]["with_partial_dates"].append(
                        {
                            "id": analysis["event_id"],
                            "name": analysis["event_name"],
                            "best_date_field": analysis["best_date_field"],
                        }
                    )

            elif analysis["is_undated"]:
                if len(final_analysis["sample_events"]["without_dates"]) < 3:
                    final_analysis["sample_events"]["without_dates"].append(
                        {"id": analysis["event_id"], "name": analysis["event_name"]}
                    )

            if analysis["is_past_event"] is True:
                if len(final_analysis["sample_events"]["past_events"]) < 3:
                    final_analysis["sample_events"]["past_events"].append(
                        {
                            "id": analysis["event_id"],
                            "name": analysis["event_name"],
                            "best_date_field": analysis["best_date_field"],
                        }
                    )

            elif analysis["is_past_event"] is False:
                if len(final_analysis["sample_events"]["future_events"]) < 3:
                    final_analysis["sample_events"]["future_events"].append(
                        {
                            "id": analysis["event_id"],
                            "name": analysis["event_name"],
                            "best_date_field": analysis["best_date_field"],
                        }
                    )

        # Generate recommendations
        recommendations = []

        if stats["undated_events"] > stats["total_events"] * 0.1:
            recommendations.append(
                f"High number of undated events ({stats['undated_events']}/{stats['total_events']}). Consider implementing filters to handle these appropriately."
            )

        if stats["past_events"] > stats["future_events"]:
            recommendations.append(
                f"More past events ({stats['past_events']}) than future events ({stats['future_events']}). Default filtering should probably exclude past events for user queries."
            )

        if stats["events_with_iso_dates"] < stats["total_events"] * 0.8:
            recommendations.append(
                f"Only {stats['events_with_iso_dates']}/{stats['total_events']} events have ISO format dates. Consider data migration or normalization."
            )

        if len(date_parsing_errors) > 0:
            recommendations.append(
                f"Found {len(date_parsing_errors)} date parsing errors. Review and clean problematic date values."
            )

        if len(stats["timezone_analysis"]) > 2:
            recommendations.append(
                f"Multiple timezones detected: {list(stats['timezone_analysis'].keys())}. Ensure consistent timezone handling."
            )

        final_analysis["recommendations"] = recommendations

        return final_analysis

    except Exception as e:
        logger.error(f"Error during event analysis: {e}", exc_info=True)
        return None


def print_analysis_report(analysis: Dict[str, Any]):
    """Print a comprehensive analysis report."""
    if not analysis:
        print("No analysis data available.")
        return

    print("=" * 80)
    print("🔍 TokenHunter Event Data Analysis Report")
    print("=" * 80)
    print(f"Analysis Time: {analysis['analysis_timestamp']}")
    print()

    stats = analysis["summary_statistics"]

    print("📊 SUMMARY STATISTICS")
    print("-" * 40)
    print(f"Total Events: {stats['total_events']}")
    print(
        f"Events with Dates: {stats['events_with_dates']} ({stats['percentages']['events_with_dates']}%)"
    )
    print(
        f"Events without Dates: {stats['events_without_dates']} ({stats['percentages']['events_without_dates']}%)"
    )
    print(
        f"Past Events: {stats['past_events']} ({stats['percentages']['past_events']}%)"
    )
    print(
        f"Future Events: {stats['future_events']} ({stats['percentages']['future_events']}%)"
    )
    print(
        f"Undated Events: {stats['undated_events']} ({stats['percentages']['undated_events']}%)"
    )
    print(
        f"Events with ISO Dates: {stats['events_with_iso_dates']} ({stats['percentages']['events_with_iso_dates']}%)"
    )
    print()

    print("📅 DATE FIELD USAGE")
    print("-" * 40)
    for field, count in sorted(
        stats["date_field_usage"].items(), key=lambda x: x[1], reverse=True
    ):
        percentage = round((count / stats["total_events"]) * 100, 1)
        print(f"{field}: {count} events ({percentage}%)")
    print()

    print("🌍 TIMEZONE ANALYSIS")
    print("-" * 40)
    for tz, count in sorted(
        stats["timezone_analysis"].items(), key=lambda x: x[1], reverse=True
    ):
        percentage = round((count / stats["total_events"]) * 100, 1)
        print(f"{tz}: {count} events ({percentage}%)")
    print()

    print("📈 DATE RANGE ANALYSIS")
    print("-" * 40)
    date_range = stats["date_range_analysis"]
    if date_range["earliest_date"] and date_range["latest_date"]:
        print(f"Earliest Event: {date_range['earliest_date']}")
        print(f"Latest Event: {date_range['latest_date']}")
        print("\nDate Distribution (by month):")
        for month, count in sorted(date_range["date_distribution"].items()):
            print(f"  {month}: {count} events")
    else:
        print("No parseable dates found for range analysis.")
    print()

    if analysis["total_parsing_errors"] > 0:
        print(f"⚠️  DATE PARSING ERRORS: {analysis['total_parsing_errors']} total")
        print("-" * 40)
        for error in analysis["date_parsing_errors"]:
            print(f"Event {error['event_id']} - {error['field']}: '{error['value']}'")
            print(f"  Error: {error['error']}")
        if analysis["total_parsing_errors"] > len(analysis["date_parsing_errors"]):
            print(
                f"  ... and {analysis['total_parsing_errors'] - len(analysis['date_parsing_errors'])} more errors"
            )
        print()

    print("📋 SAMPLE EVENTS")
    print("-" * 40)
    samples = analysis["sample_events"]

    if samples["with_complete_dates"]:
        print("Events with Complete Dates:")
        for event in samples["with_complete_dates"]:
            print(f"  • {event['name']} (best field: {event['best_date_field']})")

    if samples["with_partial_dates"]:
        print("\nEvents with Partial Dates:")
        for event in samples["with_partial_dates"]:
            print(f"  • {event['name']} (best field: {event['best_date_field']})")

    if samples["without_dates"]:
        print("\nEvents without Dates:")
        for event in samples["without_dates"]:
            print(f"  • {event['name']}")

    if samples["past_events"]:
        print("\nSample Past Events:")
        for event in samples["past_events"]:
            print(f"  • {event['name']} (from: {event['best_date_field']})")

    if samples["future_events"]:
        print("\nSample Future Events:")
        for event in samples["future_events"]:
            print(f"  • {event['name']} (from: {event['best_date_field']})")
    print()

    print("💡 RECOMMENDATIONS")
    print("-" * 40)
    for i, rec in enumerate(analysis["recommendations"], 1):
        print(f"{i}. {rec}")
    print()

    print("=" * 80)


def main():
    """Main execution function."""
    print("Starting TokenHunter Event Data Analysis...")

    # Run the analysis
    analysis = analyze_database_events()

    if analysis:
        # Print the report
        print_analysis_report(analysis)

        # Save detailed analysis to file
        output_file = (
            f"event_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            with open(output_file, "w") as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"📁 Detailed analysis saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save analysis to file: {e}")
    else:
        print("❌ Analysis failed. Check logs for details.")


if __name__ == "__main__":
    main()
