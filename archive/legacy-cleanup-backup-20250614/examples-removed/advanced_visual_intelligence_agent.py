#!/usr/bin/env python3
"""
Advanced Visual Intelligence Agent for Phase 3 - Floor Plan & Event Analytics

🎯 PART OF MAIN EXTRACTOR SYSTEM
This agent is a core component of the comprehensive 13+ agent extraction framework.
Main orchestrator: /main_extractor.py (previously enhanced_orchestrator.py)

This agent extends the enhanced image analysis capabilities with advanced visual intelligence
for floor plan analysis, booth mapping, crowd analytics, and agenda extraction.

The main extractor coordinates this agent along with 12+ other specialized agents
for comprehensive crypto conference event extraction with database integration.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .enhanced_image_analysis_agent import (
    ConfidenceLevel,
    EnhancedImageAnalysisAgent,
)

logger = logging.getLogger(__name__)


class BoothSize(Enum):
    """Booth size classification"""

    LARGE = "large"  # Major sponsors, prominent placement
    MEDIUM = "medium"  # Standard sponsors
    SMALL = "small"  # Community sponsors
    KIOSK = "kiosk"  # Small info stands
    UNKNOWN = "unknown"


class EventArea(Enum):
    """Event area classification"""

    MAIN_HALL = "main_hall"
    EXHIBITION = "exhibition"
    NETWORKING = "networking"
    WORKSHOP = "workshop"
    REGISTRATION = "registration"
    FOOD_COURT = "food_court"
    STAGE_AREA = "stage_area"
    UNKNOWN = "unknown"


@dataclass
class BoothDetection:
    """Booth/stand detection result from floor plans"""

    booth_id: str
    sponsor_name: Optional[str]
    booth_size: BoothSize
    area: EventArea
    coordinates: Optional[Dict[str, float]]  # x, y, width, height
    prominence_score: float  # 0.0-1.0 based on location and size
    neighbors: List[str]  # Adjacent booth IDs
    confidence: float
    confidence_level: ConfidenceLevel
    context: str
    detection_details: Dict[str, Any]


@dataclass
class AgendaItem:
    """Agenda item extracted from visual schedules"""

    title: str
    speaker_names: List[str]
    time_start: Optional[str]
    time_end: Optional[str]
    location: Optional[str]
    session_type: str  # keynote, panel, workshop, break, etc.
    description: Optional[str]
    confidence: float
    confidence_level: ConfidenceLevel
    context: str
    detection_details: Dict[str, Any]


@dataclass
class CrowdAnalysis:
    """Crowd analysis from event photography"""

    estimated_attendance: int
    engagement_level: str  # high, medium, low
    event_popularity: float  # 0.0-1.0
    audience_composition: Dict[str, float]  # business, casual, mixed
    venue_capacity_utilization: float  # 0.0-1.0
    confidence: float
    confidence_level: ConfidenceLevel
    context: str
    detection_details: Dict[str, Any]


class AdvancedVisualIntelligenceAgent(EnhancedImageAnalysisAgent):
    """Advanced visual intelligence agent for Phase 3 capabilities"""

    def __init__(
        self,
        name: str = "AdvancedVisualIntelligenceAgent",
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the Advanced Visual Intelligence Agent"""
        super().__init__(name=name, logger=logger)

        # Booth size indicators
        self.BOOTH_SIZE_INDICATORS = {
            BoothSize.LARGE: ["large", "premium", "platinum", "title", "main", "major"],
            BoothSize.MEDIUM: ["medium", "standard", "regular", "gold", "silver"],
            BoothSize.SMALL: ["small", "community", "startup", "bronze"],
            BoothSize.KIOSK: ["kiosk", "info", "information", "mini", "popup"],
        }

        # Event area keywords
        self.AREA_KEYWORDS = {
            EventArea.MAIN_HALL: ["main hall", "central", "auditorium", "grand hall"],
            EventArea.EXHIBITION: ["exhibition", "expo", "showcase", "display"],
            EventArea.NETWORKING: ["networking", "lounge", "reception", "social"],
            EventArea.WORKSHOP: ["workshop", "breakout", "meeting", "classroom"],
            EventArea.REGISTRATION: ["registration", "check-in", "entrance", "lobby"],
            EventArea.FOOD_COURT: ["food", "catering", "restaurant", "dining"],
            EventArea.STAGE_AREA: ["stage", "presentation", "speaker", "podium"],
        }

    def _create_floor_plan_analysis_prompt(self, image_urls: List[str]) -> List[str]:
        """Create prompt for floor plan and booth analysis"""

        prompt_parts = [
            """Analyze the following floor plan image(s) for comprehensive booth mapping and spatial analysis. You are an expert in event floor plan interpretation and booth positioning analysis.

DETECTION TARGETS:
1. **Booth Identification**: Individual booths, stands, kiosks, and exhibition spaces
2. **Sponsor Mapping**: Match booth locations to sponsor names when visible
3. **Size Classification**: Determine booth sizes and prominence levels
4. **Spatial Relationships**: Analyze booth positioning, clustering, and traffic flow
5. **Area Classification**: Identify different event areas and zones

BOOTH ANALYSIS REQUIREMENTS:
- **Booth IDs**: Assign unique identifiers (A1, B2, etc.) or extract visible booth numbers
- **Size Assessment**: Classify as Large/Medium/Small/Kiosk based on visual size and prominence
- **Location Analysis**: Determine strategic positioning (near entrance, main stage, high traffic)
- **Sponsor Recognition**: Extract visible company names or match to booth assignments
- **Prominence Scoring**: Rate booth prominence (0.0-1.0) based on size, location, and visibility

SPATIAL INTELLIGENCE:
- **Traffic Flow**: Identify main pathways, entrances, and high-traffic areas
- **Cluster Analysis**: Group related booths (crypto exchanges, DeFi protocols, infrastructure)
- **Strategic Positioning**: Analyze proximity to stages, networking areas, food courts
- **Accessibility**: Identify accessible routes and emergency exits

OUTPUT FORMAT (JSON):
{
    "booths": [
        {
            "booth_id": "A1",
            "sponsor_name": "Binance",
            "booth_size": "large",
            "area": "main_hall",
            "coordinates": {"x": 100, "y": 200, "width": 50, "height": 40},
            "prominence_score": 0.95,
            "neighbors": ["A2", "B1"],
            "strategic_advantages": ["near_main_entrance", "high_visibility"],
            "estimated_traffic": "high",
            "context": "Large prominent booth positioned near main entrance with high visibility"
        }
    ],
    "areas": [
        {
            "area_type": "exhibition",
            "booth_count": 45,
            "total_area": 2500,
            "traffic_level": "high",
            "key_sponsors": ["Binance", "Coinbase", "Ethereum"]
        }
    ],
    "layout_analysis": {
        "total_booths": 75,
        "main_pathways": 4,
        "entrance_points": 3,
        "high_traffic_zones": ["main_entrance", "food_court", "main_stage"],
        "layout_quality": "excellent"
    }
}

ANALYSIS REQUIREMENTS:
- Provide precise booth identification and positioning data
- Include confidence scores for all detections and classifications
- Analyze strategic positioning and traffic flow implications
- Focus on crypto/blockchain industry booth clustering patterns
- Identify premium positioning and sponsorship tier implications

Analyze the floor plan thoroughly and return comprehensive JSON response with spatial intelligence.""",
        ]

        return prompt_parts

    def _create_agenda_extraction_prompt(self, image_urls: List[str]) -> List[str]:
        """Create prompt for agenda and schedule extraction"""

        prompt_parts = [
            """Analyze the following schedule/agenda image(s) for comprehensive event timeline extraction. You are an expert in event schedule analysis and speaker program interpretation.

DETECTION TARGETS:
1. **Session Identification**: Individual talks, panels, workshops, and presentations
2. **Speaker Extraction**: Speaker names, titles, and affiliations from schedule entries
3. **Time Analysis**: Session start/end times, duration, and scheduling patterns
4. **Location Mapping**: Room assignments, stage locations, and venue details
5. **Session Classification**: Keynotes, panels, workshops, networking, breaks

SCHEDULE ANALYSIS REQUIREMENTS:
- **Time Precision**: Extract exact start/end times with timezone consideration
- **Speaker Details**: Full names, titles, company affiliations when available
- **Session Types**: Classify as keynote, panel, workshop, networking, break, etc.
- **Location Data**: Room names, stage assignments, venue sections
- **Topic Analysis**: Extract session topics, themes, and subject matter

CRYPTO CONFERENCE FOCUS:
- **Industry Sessions**: DeFi, NFTs, Web3, blockchain infrastructure, regulation
- **Technical Content**: Protocol deep-dives, technical workshops, developer sessions
- **Business Content**: Investment panels, market analysis, institutional adoption
- **Notable Speakers**: Recognize crypto industry leaders and protocol founders

OUTPUT FORMAT (JSON):
{
    "agenda_items": [
        {
            "title": "The Future of DeFi: Scaling and Sustainability",
            "speaker_names": ["Vitalik Buterin", "Stani Kulechov"],
            "time_start": "10:00",
            "time_end": "10:45",
            "location": "Main Stage",
            "session_type": "panel",
            "description": "Discussion on DeFi scalability solutions and long-term sustainability",
            "topics": ["defi", "scaling", "sustainability"],
            "industry_relevance": "high",
            "expected_audience": "technical",
            "confidence": 0.95
        }
    ],
    "schedule_metadata": {
        "total_sessions": 25,
        "total_speakers": 40,
        "session_types": {"keynote": 3, "panel": 8, "workshop": 6},
        "duration_hours": 8,
        "break_sessions": 4,
        "networking_sessions": 2
    },
    "timeline_analysis": {
        "peak_hours": ["10:00-12:00", "14:00-16:00"],
        "speaker_distribution": "balanced",
        "session_density": "optimal",
        "logistics_quality": "excellent"
    }
}

EXTRACTION REQUIREMENTS:
- Extract all visible session information with high precision
- Identify speaker names even from partial visibility or stylized text
- Determine session importance and audience targeting
- Analyze schedule flow and logistics optimization
- Focus on crypto/blockchain industry relevance and technical depth

Analyze the agenda thoroughly and return comprehensive JSON response with complete schedule intelligence.""",
        ]

        return prompt_parts

    def _create_crowd_analysis_prompt(self, image_urls: List[str]) -> List[str]:
        """Create prompt for crowd and event popularity analysis"""

        prompt_parts = [
            """Analyze the following event photography for comprehensive crowd analysis and engagement assessment. You are an expert in event analytics and audience engagement evaluation.

DETECTION TARGETS:
1. **Attendance Estimation**: Count visible attendees and estimate total crowd size
2. **Engagement Analysis**: Assess audience attention, participation, and interaction levels
3. **Venue Utilization**: Analyze space usage, capacity utilization, and crowd distribution
4. **Demographic Analysis**: Assess audience composition, professional vs casual attendance
5. **Event Popularity**: Determine event success and audience satisfaction indicators

CROWD ANALYSIS REQUIREMENTS:
- **Attendance Metrics**: Precise crowd counting with confidence intervals
- **Engagement Indicators**: Audience attention, device usage, note-taking, networking
- **Space Analysis**: Venue capacity utilization, overflow areas, standing room
- **Professional Assessment**: Business attire, badges, networking behavior patterns
- **Energy Levels**: Audience enthusiasm, speaker response, interaction quality

CRYPTO CONFERENCE CONTEXT:
- **Professional Networking**: Business card exchanges, group discussions, mobile apps
- **Technical Engagement**: Note-taking during technical sessions, developer clustering
- **Investment Focus**: Suited professionals, formal networking, pitch interactions
- **Community Presence**: Casual attendees, t-shirt branding, community builders

OUTPUT FORMAT (JSON):
{
    "crowd_analysis": {
        "estimated_attendance": 450,
        "attendance_range": {"min": 400, "max": 500},
        "engagement_level": "high",
        "audience_composition": {
            "business_professional": 0.65,
            "technical_developers": 0.25,
            "community_casual": 0.10
        },
        "venue_capacity_utilization": 0.85,
        "networking_activity": "high",
        "attention_metrics": {
            "speaker_focused": 0.80,
            "device_distraction": 0.15,
            "note_taking": 0.45
        },
        "event_energy": "excellent",
        "demographic_indicators": {
            "age_distribution": "25-45_majority",
            "gender_balance": "male_majority",
            "international_presence": "high"
        },
        "success_indicators": {
            "full_capacity": true,
            "engaged_audience": true,
            "active_networking": true,
            "positive_energy": true
        }
    }
}

ANALYSIS REQUIREMENTS:
- Provide quantitative metrics with confidence ranges
- Assess both macro (overall crowd) and micro (individual behavior) indicators
- Analyze professional vs casual attendance patterns
- Determine event success and popularity metrics
- Focus on crypto conference-specific engagement patterns

Analyze the crowd and event dynamics thoroughly and return comprehensive JSON response with audience intelligence.""",
        ]

        return prompt_parts

    def _classify_booth_size(
        self, context: str, coordinates: Optional[Dict] = None
    ) -> BoothSize:
        """Classify booth size based on context and coordinates"""
        context_lower = context.lower()

        # Check for explicit size mentions
        for size, indicators in self.BOOTH_SIZE_INDICATORS.items():
            for indicator in indicators:
                if indicator in context_lower:
                    return size

        # Use coordinates if available
        if coordinates and "width" in coordinates and "height" in coordinates:
            area = coordinates["width"] * coordinates["height"]
            if area > 2000:
                return BoothSize.LARGE
            elif area > 1000:
                return BoothSize.MEDIUM
            elif area > 500:
                return BoothSize.SMALL
            else:
                return BoothSize.KIOSK

        # Fallback based on context keywords
        if any(
            word in context_lower for word in ["large", "major", "prominent", "premium"]
        ):
            return BoothSize.LARGE
        elif any(word in context_lower for word in ["medium", "standard", "regular"]):
            return BoothSize.MEDIUM
        elif any(word in context_lower for word in ["small", "community", "startup"]):
            return BoothSize.SMALL
        elif any(word in context_lower for word in ["kiosk", "info", "mini"]):
            return BoothSize.KIOSK

        return BoothSize.UNKNOWN

    def _classify_event_area(self, context: str) -> EventArea:
        """Classify event area based on context"""
        context_lower = context.lower()

        for area, keywords in self.AREA_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context_lower:
                    return area

        return EventArea.UNKNOWN

    def _calculate_prominence_score(self, booth_data: Dict[str, Any]) -> float:
        """Calculate booth prominence score based on multiple factors"""
        score = 0.5  # Base score

        context = booth_data.get("context", "").lower()
        coordinates = booth_data.get("coordinates", {})

        # Size factor
        if "large" in context or "premium" in context:
            score += 0.3
        elif "medium" in context:
            score += 0.1
        elif "small" in context:
            score -= 0.1

        # Location factor
        if any(
            word in context for word in ["entrance", "main", "central", "prominent"]
        ):
            score += 0.2
        elif any(word in context for word in ["corner", "back", "side"]):
            score -= 0.1

        # Strategic advantages
        strategic_advantages = booth_data.get("strategic_advantages", [])
        score += len(strategic_advantages) * 0.05

        # Traffic estimation
        traffic = booth_data.get("estimated_traffic", "")
        if traffic == "high":
            score += 0.1
        elif traffic == "low":
            score -= 0.1

        return min(max(score, 0.0), 1.0)  # Clamp to 0.0-1.0

    async def analyze_floor_plan(
        self, image_urls: List[str], gemini_model: Any
    ) -> List[BoothDetection]:
        """Analyze floor plans for booth mapping and spatial intelligence"""

        if not image_urls or not gemini_model:
            self.logger.info(
                f"[{self.name}] No image URLs or model provided for floor plan analysis."
            )
            return []

        self.logger.info(
            f"[{self.name}] Analyzing {len(image_urls)} floor plan images..."
        )

        # Create floor plan analysis prompt
        prompt_parts = self._create_floor_plan_analysis_prompt(image_urls)
        full_prompt = prompt_parts + image_urls

        try:
            response = await asyncio.to_thread(
                gemini_model.generate_content,
                full_prompt,
            )

            if response and response.text:
                try:
                    # Parse JSON response
                    response_text = response.text.strip()
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        response_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        response_text = response_text[json_start:json_end]

                    parsed_response = json.loads(response_text)
                    booths_data = parsed_response.get("booths", [])

                    # Process detected booths
                    booth_detections = []
                    for booth_data in booths_data:
                        booth_id = booth_data.get("booth_id", "")
                        if not booth_id:
                            continue

                        # Extract booth information
                        sponsor_name = booth_data.get("sponsor_name")
                        context = booth_data.get("context", "")
                        coordinates = booth_data.get("coordinates")
                        confidence = booth_data.get("confidence", 0.7)

                        # Classify booth characteristics
                        booth_size = self._classify_booth_size(context, coordinates)
                        area = self._classify_event_area(context)
                        prominence_score = self._calculate_prominence_score(booth_data)

                        detection = BoothDetection(
                            booth_id=booth_id,
                            sponsor_name=sponsor_name,
                            booth_size=booth_size,
                            area=area,
                            coordinates=coordinates,
                            prominence_score=prominence_score,
                            neighbors=booth_data.get("neighbors", []),
                            confidence=confidence,
                            confidence_level=self._calculate_confidence_level(
                                confidence
                            ),
                            context=context,
                            detection_details=booth_data,
                        )

                        booth_detections.append(detection)

                    self.logger.info(
                        f"[{self.name}] Floor plan analysis found {len(booth_detections)} booths"
                    )
                    return booth_detections

                except json.JSONDecodeError as e:
                    self.logger.warning(
                        f"[{self.name}] Could not parse floor plan JSON response: {e}"
                    )
                    return []

            return []

        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during floor plan analysis: {e}", exc_info=True
            )
            return []

    async def analyze_agenda(
        self, image_urls: List[str], gemini_model: Any
    ) -> List[AgendaItem]:
        """Analyze agenda/schedule images for session extraction"""

        if not image_urls or not gemini_model:
            self.logger.info(
                f"[{self.name}] No image URLs or model provided for agenda analysis."
            )
            return []

        self.logger.info(f"[{self.name}] Analyzing {len(image_urls)} agenda images...")

        # Create agenda extraction prompt
        prompt_parts = self._create_agenda_extraction_prompt(image_urls)
        full_prompt = prompt_parts + image_urls

        try:
            response = await asyncio.to_thread(
                gemini_model.generate_content,
                full_prompt,
            )

            if response and response.text:
                try:
                    # Parse JSON response
                    response_text = response.text.strip()
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        response_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        response_text = response_text[json_start:json_end]

                    parsed_response = json.loads(response_text)
                    agenda_data = parsed_response.get("agenda_items", [])

                    # Process detected agenda items
                    agenda_items = []
                    for item_data in agenda_data:
                        title = item_data.get("title", "")
                        if not title:
                            continue

                        # Extract session information
                        speaker_names = item_data.get("speaker_names", [])
                        time_start = item_data.get("time_start")
                        time_end = item_data.get("time_end")
                        location = item_data.get("location")
                        session_type = item_data.get("session_type", "session")
                        description = item_data.get("description")
                        confidence = item_data.get("confidence", 0.7)
                        context = item_data.get("context", f"Session: {title}")

                        agenda_item = AgendaItem(
                            title=title,
                            speaker_names=speaker_names,
                            time_start=time_start,
                            time_end=time_end,
                            location=location,
                            session_type=session_type,
                            description=description,
                            confidence=confidence,
                            confidence_level=self._calculate_confidence_level(
                                confidence
                            ),
                            context=context,
                            detection_details=item_data,
                        )

                        agenda_items.append(agenda_item)

                    self.logger.info(
                        f"[{self.name}] Agenda analysis found {len(agenda_items)} sessions"
                    )
                    return agenda_items

                except json.JSONDecodeError as e:
                    self.logger.warning(
                        f"[{self.name}] Could not parse agenda JSON response: {e}"
                    )
                    return []

            return []

        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during agenda analysis: {e}", exc_info=True
            )
            return []

    async def analyze_crowd_engagement(
        self, image_urls: List[str], gemini_model: Any
    ) -> Optional[CrowdAnalysis]:
        """Analyze crowd photos for engagement and popularity metrics"""

        if not image_urls or not gemini_model:
            self.logger.info(
                f"[{self.name}] No image URLs or model provided for crowd analysis."
            )
            return None

        self.logger.info(f"[{self.name}] Analyzing {len(image_urls)} crowd images...")

        # Create crowd analysis prompt
        prompt_parts = self._create_crowd_analysis_prompt(image_urls)
        full_prompt = prompt_parts + image_urls

        try:
            response = await asyncio.to_thread(
                gemini_model.generate_content,
                full_prompt,
            )

            if response and response.text:
                try:
                    # Parse JSON response
                    response_text = response.text.strip()
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        response_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        response_text = response_text[json_start:json_end]

                    parsed_response = json.loads(response_text)
                    crowd_data = parsed_response.get("crowd_analysis", {})

                    if not crowd_data:
                        return None

                    # Extract crowd analysis data
                    estimated_attendance = crowd_data.get("estimated_attendance", 0)
                    engagement_level = crowd_data.get("engagement_level", "medium")
                    venue_utilization = crowd_data.get(
                        "venue_capacity_utilization", 0.5
                    )
                    audience_composition = crowd_data.get("audience_composition", {})

                    # Calculate overall event popularity score
                    event_popularity = (
                        venue_utilization * 0.4
                        + (
                            1.0
                            if engagement_level == "high"
                            else 0.5 if engagement_level == "medium" else 0.2
                        )
                        * 0.3
                        + crowd_data.get("attention_metrics", {}).get(
                            "speaker_focused", 0.5
                        )
                        * 0.3
                    )

                    confidence = 0.8  # Base confidence for crowd analysis
                    context = f"Crowd analysis of {estimated_attendance} attendees with {engagement_level} engagement"

                    crowd_analysis = CrowdAnalysis(
                        estimated_attendance=estimated_attendance,
                        engagement_level=engagement_level,
                        event_popularity=event_popularity,
                        audience_composition=audience_composition,
                        venue_capacity_utilization=venue_utilization,
                        confidence=confidence,
                        confidence_level=self._calculate_confidence_level(confidence),
                        context=context,
                        detection_details=crowd_data,
                    )

                    self.logger.info(
                        f"[{self.name}] Crowd analysis: {estimated_attendance} attendees, {engagement_level} engagement"
                    )
                    return crowd_analysis

                except json.JSONDecodeError as e:
                    self.logger.warning(
                        f"[{self.name}] Could not parse crowd analysis JSON response: {e}"
                    )
                    return None

            return None

        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during crowd analysis: {e}", exc_info=True
            )
            return None

    async def run_comprehensive_visual_intelligence(
        self, image_urls: List[str], gemini_model: Any, analysis_types: List[str] = None
    ) -> Dict[str, Any]:
        """Run comprehensive Phase 3 visual intelligence analysis"""

        if analysis_types is None:
            analysis_types = ["floor_plan", "agenda", "crowd", "sponsors", "speakers"]

        self.logger.info(
            f"[{self.name}] Starting comprehensive visual intelligence analysis: {analysis_types}"
        )

        # Prepare tasks based on requested analysis types
        tasks = {}

        if "floor_plan" in analysis_types:
            tasks["floor_plan"] = self.analyze_floor_plan(image_urls, gemini_model)

        if "agenda" in analysis_types:
            tasks["agenda"] = self.analyze_agenda(image_urls, gemini_model)

        if "crowd" in analysis_types:
            tasks["crowd"] = self.analyze_crowd_engagement(image_urls, gemini_model)

        if "sponsors" in analysis_types:
            tasks["sponsors"] = self.analyze_sponsors_and_logos(
                image_urls, gemini_model
            )

        if "speakers" in analysis_types:
            tasks["speakers"] = self.analyze_speakers(image_urls, gemini_model)

        # Run all analyses concurrently
        results = {}
        if tasks:
            completed_tasks = await asyncio.gather(
                *tasks.values(), return_exceptions=True
            )

            # Map results back to analysis types
            for (analysis_type, _), result in zip(
                tasks.items(), completed_tasks, strict=False
            ):
                if isinstance(result, Exception):
                    self.logger.error(f"{analysis_type} analysis failed: {result}")
                    results[analysis_type] = [] if analysis_type != "crowd" else None
                else:
                    results[analysis_type] = result

        # Compile comprehensive results
        comprehensive_results = {
            "floor_plan": {
                "booths": [
                    {
                        "booth_id": b.booth_id,
                        "sponsor_name": b.sponsor_name,
                        "booth_size": b.booth_size.value,
                        "area": b.area.value,
                        "prominence_score": b.prominence_score,
                        "confidence": b.confidence,
                    }
                    for b in results.get("floor_plan", [])
                ],
                "total_booths": len(results.get("floor_plan", [])),
            },
            "agenda": {
                "sessions": [
                    {
                        "title": a.title,
                        "speakers": a.speaker_names,
                        "time_start": a.time_start,
                        "time_end": a.time_end,
                        "location": a.location,
                        "session_type": a.session_type,
                        "confidence": a.confidence,
                    }
                    for a in results.get("agenda", [])
                ],
                "total_sessions": len(results.get("agenda", [])),
            },
            "crowd_analysis": (
                results.get("crowd").__dict__ if results.get("crowd") else None
            ),
            "sponsors": [
                {"name": s.name, "tier": s.tier.value, "confidence": s.confidence}
                for s in results.get("sponsors", [])
            ],
            "speakers": [
                {
                    "name": s.name,
                    "title": s.title,
                    "organization": s.organization,
                    "confidence": s.confidence,
                }
                for s in results.get("speakers", [])
            ],
            "summary": {
                "total_booths": len(results.get("floor_plan", [])),
                "total_sessions": len(results.get("agenda", [])),
                "total_sponsors": len(results.get("sponsors", [])),
                "total_speakers": len(results.get("speakers", [])),
                "has_crowd_data": results.get("crowd") is not None,
                "analysis_types_completed": list(results.keys()),
            },
        }

        self.logger.info(
            f"[{self.name}] Comprehensive visual intelligence complete: {comprehensive_results['summary']}"
        )
        return comprehensive_results
