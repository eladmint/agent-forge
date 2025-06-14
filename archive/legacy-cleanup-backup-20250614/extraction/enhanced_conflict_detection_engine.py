#!/usr/bin/env python3
"""
Enhanced Conflict Detection Engine for Phase 19 Registration Integration
=======================================================================

This module provides significantly improved conflict detection algorithms
with higher accuracy, better venue mapping, and sophisticated analysis.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ConflictType(Enum):
    TIME_OVERLAP = "time_overlap"
    TRAVEL_LOGISTICS = "travel_logistics"
    SPEAKER_PRIORITY = "speaker_priority"
    TOPIC_SATURATION = "topic_saturation"
    NETWORKING_OPTIMIZATION = "networking_optimization"
    ENERGY_MANAGEMENT = "energy_management"
    STRATEGIC_REDUNDANCY = "strategic_redundancy"


class ConflictSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ConflictResult:
    conflict_type: ConflictType
    severity: ConflictSeverity
    confidence: float  # 0.0 to 1.0
    details: Dict[str, Any]
    recommendation: str


class EnhancedConflictDetectionEngine:
    def __init__(self):
        self.venue_database = self._initialize_venue_database()
        self.speaker_rankings = self._initialize_speaker_rankings()
        self.topic_categories = self._initialize_topic_categories()
        self.networking_weights = self._initialize_networking_weights()

    def _initialize_venue_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive venue database with accurate travel times"""
        return {
            "Paris Convention Center": {
                "zone": "convention_district",
                "coordinates": (48.8566, 2.3522),
                "parking_difficulty": "high",
                "public_transport": "excellent",
                "capacity": "large",
                "venue_type": "conference_center",
            },
            "Station F": {
                "zone": "bastille_district",
                "coordinates": (48.8324, 2.3890),
                "parking_difficulty": "medium",
                "public_transport": "good",
                "capacity": "large",
                "venue_type": "tech_hub",
            },
            "Louvre": {
                "zone": "central_paris",
                "coordinates": (48.8606, 2.3376),
                "parking_difficulty": "very_high",
                "public_transport": "excellent",
                "capacity": "museum",
                "venue_type": "cultural",
            },
            "Paris Rooftop Venue": {
                "zone": "business_district",
                "coordinates": (48.8738, 2.2975),
                "parking_difficulty": "high",
                "public_transport": "good",
                "capacity": "small",
                "venue_type": "networking",
            },
            "Paris Tech Quarter": {
                "zone": "tech_district",
                "coordinates": (48.8699, 2.3486),
                "parking_difficulty": "medium",
                "public_transport": "excellent",
                "capacity": "medium",
                "venue_type": "startup_hub",
            },
        }

    def _initialize_speaker_rankings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize speaker priority rankings and characteristics"""
        return {
            "Vitalik Buterin": {
                "tier": "S",  # Highest tier
                "priority_score": 100,
                "topics": ["ethereum", "scaling", "consensus", "roadmap"],
                "exclusivity": "critical",  # Cannot be missed
                "typical_audience": 5000,
                "rarity_factor": 0.95,  # Extremely rare speaking opportunities
            },
            "Balaji Srinivasan": {
                "tier": "S",
                "priority_score": 95,
                "topics": ["crypto_economics", "regulation", "networking", "strategy"],
                "exclusivity": "critical",
                "typical_audience": 3000,
                "rarity_factor": 0.90,
            },
            "Naval Ravikant": {
                "tier": "S",
                "priority_score": 90,
                "topics": ["philosophy", "investing", "startups", "wealth"],
                "exclusivity": "critical",
                "typical_audience": 4000,
                "rarity_factor": 0.95,
            },
            "Andreas Antonopoulos": {
                "tier": "A",
                "priority_score": 85,
                "topics": ["bitcoin", "education", "security", "decentralization"],
                "exclusivity": "high",
                "typical_audience": 2000,
                "rarity_factor": 0.70,
            },
            "Multiple experts": {
                "tier": "B",
                "priority_score": 60,
                "topics": ["general"],
                "exclusivity": "medium",
                "typical_audience": 500,
                "rarity_factor": 0.30,
            },
        }

    def _initialize_topic_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize topic categorization and saturation thresholds"""
        return {
            "defi": {
                "subcategories": [
                    "yield_farming",
                    "protocols",
                    "risk_management",
                    "liquidity",
                ],
                "saturation_threshold": 2,  # Max events per day
                "learning_curve": "high",
                "cognitive_load": 0.8,
                "overlap_penalty": 0.7,
            },
            "scaling": {
                "subcategories": ["layer2", "rollups", "sharding", "consensus"],
                "saturation_threshold": 2,
                "learning_curve": "very_high",
                "cognitive_load": 0.9,
                "overlap_penalty": 0.8,
            },
            "keynote": {
                "subcategories": ["roadmap", "vision", "announcement"],
                "saturation_threshold": 1,  # One keynote is usually enough
                "learning_curve": "low",
                "cognitive_load": 0.6,
                "overlap_penalty": 0.5,
            },
            "networking": {
                "subcategories": ["reception", "dinner", "cocktail", "breakfast"],
                "saturation_threshold": 3,
                "learning_curve": "low",
                "cognitive_load": 0.3,
                "overlap_penalty": 0.4,
            },
            "technical": {
                "subcategories": [
                    "architecture",
                    "development",
                    "security",
                    "auditing",
                ],
                "saturation_threshold": 3,
                "learning_curve": "very_high",
                "cognitive_load": 1.0,
                "overlap_penalty": 0.9,
            },
        }

    def _initialize_networking_weights(self) -> Dict[str, float]:
        """Initialize networking opportunity weights"""
        return {
            "vip_investor": 1.0,  # Highest networking value
            "speaker_dinner": 0.9,  # Direct access to speakers
            "startup_pitch": 0.8,  # Business opportunities
            "general_reception": 0.6,  # General networking
            "conference_break": 0.4,  # Casual networking
            "technical_session": 0.2,  # Limited networking
        }

    def calculate_haversine_distance(
        self, coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        R = 6371  # Earth's radius in kilometers

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def enhanced_travel_time_calculation(
        self, venue1: str, venue2: str, time_of_day: datetime
    ) -> Tuple[int, float]:
        """Calculate accurate travel time with traffic and transport considerations"""
        if venue1 not in self.venue_database or venue2 not in self.venue_database:
            return 30, 0.5  # Default estimate with low confidence

        v1_data = self.venue_database[venue1]
        v2_data = self.venue_database[venue2]

        # Calculate base distance
        distance_km = self.calculate_haversine_distance(
            v1_data["coordinates"], v2_data["coordinates"]
        )

        # Base travel time (assuming mixed transport)
        base_time = max(15, distance_km * 3)  # 3 minutes per km minimum

        # Traffic factors based on time of day
        hour = time_of_day.hour
        traffic_multiplier = 1.0

        if 8 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            traffic_multiplier = 1.8
        elif 12 <= hour <= 14:  # Lunch time
            traffic_multiplier = 1.3
        elif 7 <= hour <= 22:  # Regular business hours
            traffic_multiplier = 1.2

        # Venue-specific factors
        parking_penalty = {"very_high": 15, "high": 10, "medium": 5, "low": 0}.get(
            v2_data["parking_difficulty"], 5
        )

        # Public transport bonus
        transport_bonus = {"excellent": -5, "good": -2, "medium": 0, "poor": 10}.get(
            v2_data["public_transport"], 0
        )

        # Calculate final travel time
        final_time = int(
            base_time * traffic_multiplier + parking_penalty + transport_bonus
        )

        # Confidence based on data quality
        confidence = 0.9 if distance_km < 10 else 0.7

        return final_time, confidence

    def enhanced_time_overlap_analysis(
        self, event1: Dict, event2: Dict
    ) -> Optional[ConflictResult]:
        """Enhanced time overlap detection with buffer considerations"""
        start1, end1 = event1["start"], event1["end"]
        start2, end2 = event2["start"], event2["end"]

        # Add buffer time for event transitions
        buffer_minutes = 15
        buffered_end1 = end1 + timedelta(minutes=buffer_minutes)
        buffered_start2 = start2 - timedelta(minutes=buffer_minutes)

        # Check for overlap including buffers
        if buffered_end1 <= start2 or end2 <= buffered_start2:
            return None  # No conflict

        # Calculate overlap duration
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)

        # Enhanced severity calculation
        event1_duration = int((end1 - start1).total_seconds() / 60)
        event2_duration = int((end2 - start2).total_seconds() / 60)

        overlap_percentage = max(
            overlap_minutes / event1_duration, overlap_minutes / event2_duration
        )

        # Determine severity with more nuanced thresholds
        if overlap_percentage >= 0.75 or overlap_minutes >= 90:
            severity = ConflictSeverity.CRITICAL
        elif overlap_percentage >= 0.5 or overlap_minutes >= 60:
            severity = ConflictSeverity.HIGH
        elif overlap_percentage >= 0.25 or overlap_minutes >= 30:
            severity = ConflictSeverity.MEDIUM
        else:
            severity = ConflictSeverity.LOW

        # Factor in event priority
        priority1 = event1.get("priority", "medium")
        priority2 = event2.get("priority", "medium")

        if priority1 == "critical" or priority2 == "critical":
            if severity.value in ["medium", "low"]:
                severity = ConflictSeverity.HIGH

        confidence = 0.95  # High confidence in time overlap detection

        return ConflictResult(
            conflict_type=ConflictType.TIME_OVERLAP,
            severity=severity,
            confidence=confidence,
            details={
                "overlap_minutes": overlap_minutes,
                "overlap_percentage": f"{overlap_percentage:.1%}",
                "event1_priority": priority1,
                "event2_priority": priority2,
                "buffer_considered": True,
            },
            recommendation=self._generate_time_overlap_recommendation(
                overlap_minutes, overlap_percentage, priority1, priority2
            ),
        )

    def enhanced_speaker_conflict_analysis(
        self, event1: Dict, event2: Dict
    ) -> Optional[ConflictResult]:
        """Enhanced speaker conflict detection with VIP rankings"""
        speaker1 = event1.get("speaker", "").strip()
        speaker2 = event2.get("speaker", "").strip()

        if not speaker1 or not speaker2 or speaker1 != speaker2:
            return None

        # Handle "Multiple experts" case
        if speaker1 == "Multiple experts":
            return None  # Not a real conflict for generic speakers

        speaker_data = self.speaker_rankings.get(
            speaker1,
            {
                "tier": "C",
                "priority_score": 50,
                "exclusivity": "medium",
                "rarity_factor": 0.5,
            },
        )

        # Calculate conflict severity based on speaker importance
        priority_score = speaker_data["priority_score"]
        rarity_factor = speaker_data["rarity_factor"]

        if priority_score >= 90:
            severity = ConflictSeverity.CRITICAL
        elif priority_score >= 80:
            severity = ConflictSeverity.HIGH
        elif priority_score >= 60:
            severity = ConflictSeverity.MEDIUM
        else:
            severity = ConflictSeverity.LOW

        confidence = 0.9 + rarity_factor * 0.1  # Higher confidence for rare speakers

        return ConflictResult(
            conflict_type=ConflictType.SPEAKER_PRIORITY,
            severity=severity,
            confidence=confidence,
            details={
                "speaker": speaker1,
                "speaker_tier": speaker_data["tier"],
                "priority_score": priority_score,
                "rarity_factor": rarity_factor,
                "exclusivity": speaker_data["exclusivity"],
            },
            recommendation=self._generate_speaker_conflict_recommendation(
                speaker_data, event1, event2
            ),
        )

    def enhanced_travel_logistics_analysis(
        self, event1: Dict, event2: Dict
    ) -> Optional[ConflictResult]:
        """Enhanced travel logistics analysis with accurate venue data"""
        location1 = event1.get("location", "").strip()
        location2 = event2.get("location", "").strip()

        if not location1 or not location2:
            return None

        # Same location check
        if self._normalize_venue_name(location1) == self._normalize_venue_name(
            location2
        ):
            return None  # No travel conflict

        # Calculate travel time
        end_time1 = event1["end"]
        start_time2 = event2["start"]

        available_time = int((start_time2 - end_time1).total_seconds() / 60)

        # Get accurate travel time
        travel_time, confidence = self.enhanced_travel_time_calculation(
            location1, location2, end_time1
        )

        # Check if travel is feasible
        if available_time >= travel_time + 10:  # 10 minute safety buffer
            return None  # No conflict

        # Calculate severity
        time_deficit = travel_time - available_time

        if time_deficit >= 30:
            severity = ConflictSeverity.CRITICAL
        elif time_deficit >= 15:
            severity = ConflictSeverity.HIGH
        elif time_deficit >= 5:
            severity = ConflictSeverity.MEDIUM
        else:
            severity = ConflictSeverity.LOW

        return ConflictResult(
            conflict_type=ConflictType.TRAVEL_LOGISTICS,
            severity=severity,
            confidence=confidence,
            details={
                "venue1": location1,
                "venue2": location2,
                "travel_time_minutes": travel_time,
                "available_time_minutes": available_time,
                "time_deficit_minutes": time_deficit,
                "feasible": time_deficit <= 0,
            },
            recommendation=self._generate_travel_conflict_recommendation(
                travel_time, available_time, location1, location2
            ),
        )

    def enhanced_topic_saturation_analysis(
        self, events: List[Dict]
    ) -> List[ConflictResult]:
        """Enhanced topic saturation analysis with cognitive load factors"""
        if len(events) < 2:
            return []

        # Group events by category and topic
        category_groups = {}
        topic_groups = {}

        for event in events:
            category = event.get("category", "unknown")
            topic = event.get("topic", "unknown")

            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(event)

            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(event)

        conflicts = []

        # Analyze category saturation
        for category, category_events in category_groups.items():
            if len(category_events) < 2:
                continue

            category_data = self.topic_categories.get(
                category,
                {
                    "saturation_threshold": 3,
                    "cognitive_load": 0.5,
                    "overlap_penalty": 0.5,
                },
            )

            threshold = category_data["saturation_threshold"]
            cognitive_load = category_data["cognitive_load"]

            if len(category_events) > threshold:
                # Calculate severity based on excess and cognitive load
                excess_factor = (len(category_events) - threshold) / threshold
                severity_score = excess_factor * cognitive_load

                if severity_score >= 0.8:
                    severity = ConflictSeverity.CRITICAL
                elif severity_score >= 0.6:
                    severity = ConflictSeverity.HIGH
                elif severity_score >= 0.3:
                    severity = ConflictSeverity.MEDIUM
                else:
                    severity = ConflictSeverity.LOW

                conflicts.append(
                    ConflictResult(
                        conflict_type=ConflictType.TOPIC_SATURATION,
                        severity=severity,
                        confidence=0.8,
                        details={
                            "category": category,
                            "event_count": len(category_events),
                            "threshold": threshold,
                            "cognitive_load": cognitive_load,
                            "excess_factor": excess_factor,
                        },
                        recommendation=self._generate_topic_saturation_recommendation(
                            category, len(category_events), threshold
                        ),
                    )
                )

        return conflicts

    def enhanced_networking_optimization_analysis(
        self, event1: Dict, event2: Dict
    ) -> Optional[ConflictResult]:
        """Enhanced networking value analysis"""
        networking1 = event1.get("networking_value", "medium")
        networking2 = event2.get("networking_value", "medium")

        weight1 = self.networking_weights.get(networking1, 0.5)
        weight2 = self.networking_weights.get(networking2, 0.5)

        # Only flag if there's a significant networking value difference
        value_difference = abs(weight1 - weight2)

        if value_difference < 0.3:
            return None  # Not significant enough

        # Determine which event has higher networking value
        high_value_event = event1 if weight1 > weight2 else event2
        high_value = max(weight1, weight2)

        # Calculate severity based on networking value and opportunity cost
        if high_value >= 0.9:
            severity = ConflictSeverity.HIGH
        elif high_value >= 0.7:
            severity = ConflictSeverity.MEDIUM
        else:
            severity = ConflictSeverity.LOW

        return ConflictResult(
            conflict_type=ConflictType.NETWORKING_OPTIMIZATION,
            severity=severity,
            confidence=0.7,
            details={
                "event1_networking": networking1,
                "event2_networking": networking2,
                "event1_weight": weight1,
                "event2_weight": weight2,
                "value_difference": value_difference,
                "recommended_event": (
                    high_value_event["name"]
                    if "name" in high_value_event
                    else "higher_value_event"
                ),
            },
            recommendation=self._generate_networking_optimization_recommendation(
                networking1, networking2, weight1, weight2
            ),
        )

    def _normalize_venue_name(self, venue: str) -> str:
        """Normalize venue names for comparison"""
        # Extract main venue identifier
        for main_venue in self.venue_database.keys():
            if main_venue in venue:
                return main_venue
        return venue.split(" - ")[0].strip()  # Take first part before dash

    def _generate_time_overlap_recommendation(
        self, overlap_mins: int, overlap_pct: float, priority1: str, priority2: str
    ) -> str:
        """Generate specific recommendation for time overlaps"""
        if overlap_pct >= 0.75:
            return f"Critical overlap ({overlap_mins} minutes). Choose one event or attend virtually if available."
        elif overlap_pct >= 0.5:
            return f"Significant overlap ({overlap_mins} minutes). Consider attending the higher priority event."
        else:
            return f"Partial overlap ({overlap_mins} minutes). You could attend both with careful timing."

    def _generate_speaker_conflict_recommendation(
        self, speaker_data: Dict, event1: Dict, event2: Dict
    ) -> str:
        """Generate speaker conflict recommendation"""
        tier = speaker_data.get("tier", "C")
        if tier == "S":
            return "Same S-tier speaker conflict. This is extremely rare - choose the event with better content fit for your goals."
        else:
            return "Speaker appears at both events. Consider attending the event with better overall agenda alignment."

    def _generate_travel_conflict_recommendation(
        self, travel_time: int, available_time: int, venue1: str, venue2: str
    ) -> str:
        """Generate travel logistics recommendation"""
        if available_time < travel_time:
            deficit = travel_time - available_time
            return f"Impossible travel logistics: need {travel_time} minutes, only {available_time} available. Consider virtual attendance or choose one event."
        else:
            buffer = available_time - travel_time
            if buffer < 15:
                return f"Tight travel schedule: {buffer} minute buffer. Plan transport in advance and have backup options."
            else:
                return f"Feasible travel: {buffer} minute buffer should be sufficient."

    def _generate_topic_saturation_recommendation(
        self, category: str, count: int, threshold: int
    ) -> str:
        """Generate topic saturation recommendation"""
        excess = count - threshold
        return f"Topic saturation detected: {count} {category} events (recommended max: {threshold}). Consider prioritizing the most unique or high-value sessions to avoid information overload."

    def _generate_networking_optimization_recommendation(
        self, net1: str, net2: str, weight1: float, weight2: float
    ) -> str:
        """Generate networking optimization recommendation"""
        if weight1 > weight2:
            return f"Higher networking value at first event ({net1} vs {net2}). Prioritize for strategic connections."
        else:
            return f"Higher networking value at second event ({net2} vs {net1}). Prioritize for strategic connections."

    def analyze_comprehensive_conflicts(
        self, events: List[Dict]
    ) -> List[ConflictResult]:
        """Comprehensive conflict analysis with enhanced algorithms"""
        all_conflicts = []

        # Analyze all pairs of events
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                event1, event2 = events[i], events[j]

                # Time overlap analysis
                time_conflict = self.enhanced_time_overlap_analysis(event1, event2)
                if time_conflict:
                    all_conflicts.append(time_conflict)

                # Speaker conflict analysis
                speaker_conflict = self.enhanced_speaker_conflict_analysis(
                    event1, event2
                )
                if speaker_conflict:
                    all_conflicts.append(speaker_conflict)

                # Travel logistics analysis
                travel_conflict = self.enhanced_travel_logistics_analysis(
                    event1, event2
                )
                if travel_conflict:
                    all_conflicts.append(travel_conflict)

                # Networking optimization analysis
                networking_conflict = self.enhanced_networking_optimization_analysis(
                    event1, event2
                )
                if networking_conflict:
                    all_conflicts.append(networking_conflict)

        # Topic saturation analysis (considers all events together)
        topic_conflicts = self.enhanced_topic_saturation_analysis(events)
        all_conflicts.extend(topic_conflicts)

        return all_conflicts


def main():
    """Test the enhanced conflict detection engine"""
    engine = EnhancedConflictDetectionEngine()

    # Test with sample events
    base_date = datetime(2025, 7, 15, 9, 0, 0)

    test_events = [
        {
            "name": "Ethereum Roadmap Keynote - Vitalik Buterin",
            "start": base_date,
            "end": base_date + timedelta(hours=2),
            "location": "Paris Convention Center - Main Hall",
            "priority": "critical",
            "speaker": "Vitalik Buterin",
            "category": "keynote",
        },
        {
            "name": "Layer 2 Scaling Panel",
            "start": base_date + timedelta(minutes=30),
            "end": base_date + timedelta(hours=2, minutes=30),
            "location": "Paris Convention Center - Hall B",
            "priority": "high",
            "speaker": "Multiple experts",
            "category": "panel",
        },
    ]

    conflicts = engine.analyze_comprehensive_conflicts(test_events)

    print("🧪 Enhanced Conflict Detection Engine Test Results:")
    print("=" * 50)

    for conflict in conflicts:
        print(
            f"\n⚠️ {conflict.conflict_type.value.upper()} - {conflict.severity.value.upper()}"
        )
        print(f"   Confidence: {conflict.confidence:.1%}")
        print(f"   Details: {conflict.details}")
        print(f"   Recommendation: {conflict.recommendation}")

    print(f"\n📊 Total conflicts detected: {len(conflicts)}")


if __name__ == "__main__":
    main()
