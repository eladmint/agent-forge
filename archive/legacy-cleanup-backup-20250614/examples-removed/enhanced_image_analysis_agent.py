import logging
from typing import List, Any, Dict, Optional, Tuple
import asyncio
import os
import io
import json
from PIL import Image
import aiohttp
from google.api_core.exceptions import GoogleAPIError
from PIL import UnidentifiedImageError
from dataclasses import dataclass
from enum import Enum

# Setup logger for the agent
logger = logging.getLogger(__name__)


class SponsorTier(Enum):
    """Sponsor tier classification"""

    TITLE = "title"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    PARTNER = "partner"
    MEDIA = "media"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence level for detection"""

    HIGH = "high"  # 0.8+
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"  # 0.3-0.5
    VERY_LOW = "very_low"  # <0.3


@dataclass
class SponsorDetection:
    """Enhanced sponsor detection result"""

    name: str
    confidence: float
    tier: SponsorTier
    confidence_level: ConfidenceLevel
    context: str
    image_url: str
    detection_details: Dict[str, Any]


@dataclass
class SpeakerDetection:
    """Speaker detection result from photos"""

    name: str
    title: Optional[str]
    organization: Optional[str]
    confidence: float
    confidence_level: ConfidenceLevel
    context: str
    image_url: str
    detection_details: Dict[str, Any]


class EnhancedImageAnalysisAgent:
    """Enhanced image analysis agent with advanced sponsor/speaker detection capabilities - Framework-free implementation"""

    # Crypto/blockchain company knowledge base
    KNOWN_CRYPTO_COMPANIES = {
        "binance",
        "coinbase",
        "ethereum",
        "polygon",
        "solana",
        "avalanche",
        "chainlink",
        "uniswap",
        "opensea",
        "metamask",
        "ledger",
        "trezor",
        "compound",
        "aave",
        "maker",
        "synthetix",
        "yearn",
        "curve",
        "consensys",
        "grayscale",
        "galaxy",
        "jump",
        "alameda",
        "ftx",
        "kraken",
        "gemini",
        "crypto.com",
        "okx",
        "huobi",
        "kucoin",
        "near",
        "cosmos",
        "polkadot",
        "cardano",
        "tezos",
        "algorand",
        "flow",
        "dfinity",
        "helium",
        "filecoin",
        "arweave",
        "the graph",
    }

    # Known crypto/blockchain industry speakers and leaders
    KNOWN_CRYPTO_SPEAKERS = {
        "vitalik buterin": {
            "title": "Co-founder",
            "organization": "Ethereum Foundation",
        },
        "changpeng zhao": {"title": "Former CEO", "organization": "Binance"},
        "brian armstrong": {"title": "CEO", "organization": "Coinbase"},
        "brad garlinghouse": {"title": "CEO", "organization": "Ripple"},
        "do kwon": {"title": "Co-founder", "organization": "Terraform Labs"},
        "sergey nazarov": {"title": "Co-founder", "organization": "Chainlink"},
        "sam bankman-fried": {"title": "Former CEO", "organization": "FTX"},
        "hayden adams": {"title": "Founder", "organization": "Uniswap"},
        "stani kulechov": {"title": "Founder", "organization": "Aave"},
        "andre cronje": {"title": "Founder", "organization": "Yearn Finance"},
        "illia polosukhin": {"title": "Co-founder", "organization": "NEAR Protocol"},
        "gavin wood": {"title": "Founder", "organization": "Polkadot"},
        "charles hoskinson": {"title": "Founder", "organization": "Cardano"},
        "silvio micali": {"title": "Founder", "organization": "Algorand"},
        "kathleen breitman": {"title": "Co-founder", "organization": "Tezos"},
        "arthur breitman": {"title": "Co-founder", "organization": "Tezos"},
        "anatoly yakovenko": {"title": "Co-founder", "organization": "Solana"},
        "raj gokal": {"title": "Co-founder", "organization": "Solana"},
        "sandeep nailwal": {"title": "Co-founder", "organization": "Polygon"},
        "jaynti kanani": {"title": "Co-founder", "organization": "Polygon"},
    }

    # Sponsor tier indicators
    TIER_INDICATORS = {
        SponsorTier.TITLE: [
            "title sponsor",
            "presenting sponsor",
            "main sponsor",
            "headline sponsor",
        ],
        SponsorTier.GOLD: ["gold sponsor", "premium sponsor", "platinum sponsor"],
        SponsorTier.SILVER: ["silver sponsor", "supporting sponsor"],
        SponsorTier.BRONZE: ["bronze sponsor", "community sponsor"],
        SponsorTier.PARTNER: ["partner", "official partner", "technology partner"],
        SponsorTier.MEDIA: ["media partner", "media sponsor", "press partner"],
    }

    def __init__(
        self,
        name: str = "EnhancedImageAnalysisAgent",
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the framework-free Enhanced Image Analysis Agent"""
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.genai_model = None

        self.logger.info(
            f"[{self.name}] Initialized framework-free Enhanced Image Analysis Agent"
        )

    def _create_enhanced_sponsor_prompt(self, image_urls: List[str]) -> List[str]:
        """Create enhanced prompt for sponsor/logo detection"""

        crypto_companies_list = ", ".join(
            list(self.KNOWN_CRYPTO_COMPANIES)[:20]
        )  # First 20 for brevity

        prompt_parts = [
            f"""Analyze the following image(s) for comprehensive sponsor and logo detection. You are an expert in cryptocurrency and blockchain industry recognition.

DETECTION TARGETS:
1. **Company Logos**: Identify any visible company logos, brand marks, or corporate identities
2. **Sponsor Tiers**: Determine sponsor level from visual placement, size, and context clues
3. **Text Recognition**: Extract company names from text, banners, signage, or watermarks
4. **Context Analysis**: Understand sponsor relationships and hierarchy from visual layout

CRYPTO/BLOCKCHAIN FOCUS:
Pay special attention to these known industry companies: {crypto_companies_list}
Also look for: DeFi protocols, NFT platforms, Web3 companies, blockchain networks, crypto exchanges, wallet providers

SPONSOR TIER DETECTION:
- **Title/Presenting**: Large prominent placement, main stage branding, primary positioning
- **Gold/Premium**: Prominent placement, significant visual presence, top-tier positioning  
- **Silver/Supporting**: Moderate placement, clear visibility, mid-tier positioning
- **Bronze/Community**: Smaller placement, basic visibility, lower-tier positioning
- **Partner**: Technology/strategic partners, often with "Partner" designation
- **Media**: Press/media partners, usually smaller placement or specific media sections

OUTPUT FORMAT (JSON):
{{
    "sponsors": [
        {{
            "name": "Company Name",
            "confidence": 0.95,
            "tier": "gold",
            "context": "Large logo prominently displayed on main stage backdrop",
            "visual_prominence": "high",
            "detection_method": "logo_recognition"
        }}
    ]
}}

ANALYSIS REQUIREMENTS:
- Provide confidence scores (0.0-1.0) based on logo clarity, text readability, and recognition certainty
- Include context description explaining where/how the sponsor was detected
- Classify tier based on visual prominence, placement, and size relative to other sponsors
- Focus on accuracy over quantity - only include clear, confident detections

Analyze each image thoroughly and return a comprehensive JSON response.""",
        ]

        return prompt_parts

    def _create_speaker_detection_prompt(self, image_urls: List[str]) -> List[str]:
        """Create enhanced prompt for speaker detection with crypto industry focus"""

        # Create a sample of known speakers for the prompt
        known_speakers_sample = list(self.KNOWN_CRYPTO_SPEAKERS.keys())[:10]
        speakers_list = ", ".join([name.title() for name in known_speakers_sample])

        prompt_parts = [
            f"""Analyze the following image(s) for comprehensive speaker identification and extraction. You are an expert in cryptocurrency and blockchain industry speaker recognition.

DETECTION TARGETS:
1. **Speaker Photos**: Individual headshots, panel photos, group photos with speakers
2. **Name Extraction**: Speaker names from photo captions, overlays, name tags, or slides
3. **Title/Role Detection**: Job titles, company affiliations, speaking roles
4. **Context Analysis**: Panel discussions, keynote speakers, workshop leaders
5. **Facial Recognition**: Visual identification of known crypto industry figures

CRYPTO/BLOCKCHAIN SPEAKER FOCUS:
Pay special attention to these known industry leaders: {speakers_list}
Also look for: Protocol founders, DeFi creators, NFT pioneers, Web3 builders, blockchain researchers

SPEAKER IDENTIFICATION METHODS:
- **Text-based Detection**: Names from photo captions, slides, overlays, name tags, conference badges
- **Visual Context Analysis**: Stage presence, panel positioning, speaking gestures, audience attention
- **Professional Recognition**: Industry-standard headshots, company branding, role indicators
- **Multi-speaker Scenarios**: Panel discussions, group photos, stage presentations
- **Quality Assessment**: Photo clarity, text readability, context relevance

ENHANCED ANALYSIS FEATURES:
- **Speaker Roles**: Keynote, panelist, moderator, workshop leader, presenter
- **Photo Types**: Headshot, panel, stage, group, candid, professional
- **Context Clues**: Stage setup, audience, microphones, presentation screens
- **Industry Relevance**: Focus on blockchain/crypto conference speakers vs general attendees

OUTPUT FORMAT (JSON):
{{
    "speakers": [
        {{
            "name": "Speaker Name",
            "title": "CEO/Founder/CTO",
            "organization": "Company Name",
            "confidence": 0.90,
            "context": "Professional headshot with name and title overlay on stage",
            "detection_method": "photo_caption_and_visual_context",
            "speaker_role": "keynote_speaker",
            "photo_type": "professional_headshot",
            "industry_relevance": "high",
            "additional_context": "Speaking at main stage with blockchain conference branding"
        }}
    ]
}}

ANALYSIS REQUIREMENTS:
- Extract complete names when visible (first and last names)
- Include job titles and company affiliations if shown
- Provide confidence based on text clarity, visual context, and recognition certainty
- Describe detection context (where/how the speaker was identified)
- Classify speaker role (keynote, panelist, moderator, presenter)
- Assess photo type and quality for context
- Focus on conference-relevant speakers (not random attendees)
- Prioritize crypto/blockchain industry figures
- Include additional context about speaking environment

Return comprehensive JSON response with all detected speakers and rich metadata.""",
        ]

        return prompt_parts

    def _calculate_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to confidence level enum"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _classify_sponsor_tier(self, context: str, name: str) -> SponsorTier:
        """Classify sponsor tier based on context and visual cues"""
        context_lower = context.lower()
        name_lower = name.lower()

        # Check for explicit tier mentions
        for tier, indicators in self.TIER_INDICATORS.items():
            for indicator in indicators:
                if indicator in context_lower or indicator in name_lower:
                    return tier

        # Visual prominence heuristics
        if any(
            word in context_lower
            for word in ["main stage", "primary", "large", "prominent", "title"]
        ):
            return SponsorTier.TITLE
        elif any(
            word in context_lower for word in ["gold", "premium", "platinum", "major"]
        ):
            return SponsorTier.GOLD
        elif any(
            word in context_lower for word in ["silver", "supporting", "secondary"]
        ):
            return SponsorTier.SILVER
        elif any(
            word in context_lower for word in ["bronze", "community", "small", "minor"]
        ):
            return SponsorTier.BRONZE
        elif any(
            word in context_lower for word in ["partner", "technology", "strategic"]
        ):
            return SponsorTier.PARTNER
        elif any(word in context_lower for word in ["media", "press", "publication"]):
            return SponsorTier.MEDIA

        return SponsorTier.UNKNOWN

    def _enhance_crypto_recognition(self, detected_name: str) -> Tuple[str, float]:
        """Enhance recognition for crypto/blockchain companies"""
        name_lower = detected_name.lower()

        # Check against known crypto companies
        for company in self.KNOWN_CRYPTO_COMPANIES:
            if company in name_lower or name_lower in company:
                return company.title(), 0.95  # High confidence for known entities

        # Check for common crypto/blockchain terms
        crypto_terms = [
            "defi",
            "nft",
            "web3",
            "blockchain",
            "crypto",
            "ethereum",
            "bitcoin",
        ]
        for term in crypto_terms:
            if term in name_lower:
                return detected_name, 0.85  # Enhanced confidence for crypto-related

        return detected_name, 0.7  # Standard confidence

    def _enhance_speaker_recognition(
        self, detected_name: str, detected_title: str = "", detected_org: str = ""
    ) -> Tuple[str, str, str, float]:
        """Enhance speaker recognition for crypto/blockchain industry figures"""
        name_lower = detected_name.lower().strip()

        # Check against known crypto speakers
        if name_lower in self.KNOWN_CRYPTO_SPEAKERS:
            speaker_info = self.KNOWN_CRYPTO_SPEAKERS[name_lower]
            enhanced_name = detected_name.title()
            enhanced_title = detected_title or speaker_info.get("title", "")
            enhanced_org = detected_org or speaker_info.get("organization", "")
            return (
                enhanced_name,
                enhanced_title,
                enhanced_org,
                0.95,
            )  # High confidence for known speakers

        # Check for partial matches (first name + last name variants)
        for known_speaker, info in self.KNOWN_CRYPTO_SPEAKERS.items():
            known_parts = known_speaker.split()
            detected_parts = name_lower.split()

            # Check if both first and last names match
            if len(known_parts) >= 2 and len(detected_parts) >= 2:
                if (
                    known_parts[0] in detected_parts
                    and known_parts[-1] in detected_parts
                ) or (
                    detected_parts[0] in known_parts
                    and detected_parts[-1] in known_parts
                ):
                    enhanced_name = known_speaker.title()
                    enhanced_title = detected_title or info.get("title", "")
                    enhanced_org = detected_org or info.get("organization", "")
                    return (
                        enhanced_name,
                        enhanced_title,
                        enhanced_org,
                        0.90,
                    )  # High confidence for partial match

        # Check if organization matches known crypto companies
        org_lower = detected_org.lower()
        for company in self.KNOWN_CRYPTO_COMPANIES:
            if company in org_lower or org_lower in company:
                return (
                    detected_name,
                    detected_title,
                    detected_org,
                    0.85,
                )  # Enhanced confidence for crypto org

        # Check for crypto-related terms in title
        crypto_titles = [
            "founder",
            "ceo",
            "cto",
            "blockchain",
            "defi",
            "crypto",
            "web3",
            "protocol",
        ]
        title_lower = detected_title.lower()
        for term in crypto_titles:
            if term in title_lower:
                return (
                    detected_name,
                    detected_title,
                    detected_org,
                    0.80,
                )  # Enhanced confidence for crypto role

        return detected_name, detected_title, detected_org, 0.7  # Standard confidence

    def _assess_photo_quality(self, context: str) -> str:
        """Assess photo quality and type from context description"""
        context_lower = context.lower()

        if any(
            term in context_lower
            for term in ["professional", "headshot", "high quality", "clear"]
        ):
            return "professional"
        elif any(
            term in context_lower
            for term in ["panel", "stage", "presentation", "speaking"]
        ):
            return "presentation"
        elif any(
            term in context_lower for term in ["group", "multiple", "panel discussion"]
        ):
            return "group"
        elif any(term in context_lower for term in ["candid", "informal", "audience"]):
            return "candid"
        else:
            return "standard"

    def _determine_speaker_role(
        self, context: str, detection_details: Dict[str, Any]
    ) -> str:
        """Determine speaker role from context and detection details"""
        context_lower = context.lower()

        if any(
            term in context_lower
            for term in ["keynote", "main stage", "opening", "closing"]
        ):
            return "keynote_speaker"
        elif any(term in context_lower for term in ["panel", "panelist", "discussion"]):
            return "panelist"
        elif any(
            term in context_lower for term in ["moderator", "host", "facilitator"]
        ):
            return "moderator"
        elif any(
            term in context_lower for term in ["workshop", "tutorial", "training"]
        ):
            return "workshop_leader"
        elif any(
            term in context_lower for term in ["presenter", "presentation", "demo"]
        ):
            return "presenter"
        else:
            return "speaker"

    async def analyze_sponsors_and_logos(
        self, image_urls: List[str], gemini_model: Any
    ) -> List[SponsorDetection]:
        """Advanced sponsor and logo detection with enhanced capabilities"""

        if not image_urls or not gemini_model:
            self.logger.info(
                f"[{self.name}] No image URLs or model provided for sponsor analysis."
            )
            return []

        self.logger.info(
            f"[{self.name}] Analyzing {len(image_urls)} images for sponsors/logos..."
        )

        # Create enhanced prompt
        prompt_parts = self._create_enhanced_sponsor_prompt(image_urls)
        full_prompt = prompt_parts + image_urls

        try:
            self.logger.debug(
                f"[{self.name}] Sending enhanced sponsor detection request..."
            )

            response = await asyncio.to_thread(
                gemini_model.generate_content,
                full_prompt,
            )

            if response and response.text:
                self.logger.debug(f"[{self.name}] Received sponsor analysis response")

                # Try to parse JSON response
                try:
                    # Extract JSON from response (handle cases where response includes extra text)
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
                    sponsors_data = parsed_response.get("sponsors", [])

                    # Process detected sponsors
                    sponsor_detections = []
                    for sponsor_data in sponsors_data:
                        name = sponsor_data.get("name", "")
                        if not name:
                            continue

                        # Enhance crypto company recognition
                        enhanced_name, base_confidence = (
                            self._enhance_crypto_recognition(name)
                        )

                        # Get reported confidence or use enhanced confidence
                        confidence = sponsor_data.get("confidence", base_confidence)
                        confidence = min(confidence, 1.0)  # Cap at 1.0

                        # Classify sponsor tier
                        context = sponsor_data.get("context", "")
                        tier = self._classify_sponsor_tier(context, enhanced_name)

                        # Create detection object
                        detection = SponsorDetection(
                            name=enhanced_name,
                            confidence=confidence,
                            tier=tier,
                            confidence_level=self._calculate_confidence_level(
                                confidence
                            ),
                            context=context,
                            image_url=(
                                image_urls[0] if image_urls else ""
                            ),  # Primary image
                            detection_details=sponsor_data,
                        )

                        sponsor_detections.append(detection)

                    self.logger.info(
                        f"[{self.name}] Enhanced sponsor analysis found {len(sponsor_detections)} sponsors"
                    )
                    return sponsor_detections

                except json.JSONDecodeError as e:
                    self.logger.warning(
                        f"[{self.name}] Could not parse JSON response, falling back to text parsing: {e}"
                    )
                    # Fallback to simple text parsing
                    return self._fallback_sponsor_parsing(response.text, image_urls)
            else:
                self.logger.warning(
                    f"[{self.name}] Empty response from sponsor analysis"
                )
                return []

        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during enhanced sponsor analysis: {e}",
                exc_info=True,
            )
            return []

    def _fallback_sponsor_parsing(
        self, response_text: str, image_urls: List[str]
    ) -> List[SponsorDetection]:
        """Fallback parsing when JSON parsing fails"""
        sponsors = []
        lines = response_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("*"):
                # Simple name extraction
                enhanced_name, confidence = self._enhance_crypto_recognition(line)

                detection = SponsorDetection(
                    name=enhanced_name,
                    confidence=confidence,
                    tier=SponsorTier.UNKNOWN,
                    confidence_level=self._calculate_confidence_level(confidence),
                    context="Fallback text extraction",
                    image_url=image_urls[0] if image_urls else "",
                    detection_details={"raw_text": line},
                )
                sponsors.append(detection)

        return sponsors

    async def analyze_speakers(
        self, image_urls: List[str], gemini_model: Any
    ) -> List[SpeakerDetection]:
        """Advanced speaker detection from photos"""

        if not image_urls or not gemini_model:
            self.logger.info(
                f"[{self.name}] No image URLs or model provided for speaker analysis."
            )
            return []

        self.logger.info(
            f"[{self.name}] Analyzing {len(image_urls)} images for speakers..."
        )

        # Create speaker detection prompt
        prompt_parts = self._create_speaker_detection_prompt(image_urls)
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
                    speakers_data = parsed_response.get("speakers", [])

                    # Process detected speakers with enhanced recognition
                    speaker_detections = []
                    for speaker_data in speakers_data:
                        name = speaker_data.get("name", "")
                        if not name:
                            continue

                        # Get initial data
                        title = speaker_data.get("title", "")
                        organization = speaker_data.get("organization", "")
                        confidence = speaker_data.get("confidence", 0.7)
                        context = speaker_data.get("context", "")

                        # Enhance speaker recognition with crypto industry knowledge
                        (
                            enhanced_name,
                            enhanced_title,
                            enhanced_org,
                            enhanced_confidence,
                        ) = self._enhance_speaker_recognition(name, title, organization)

                        # Use the higher confidence between detected and enhanced
                        final_confidence = max(confidence, enhanced_confidence)
                        final_confidence = min(final_confidence, 1.0)

                        # Assess photo quality and speaker role
                        photo_type = self._assess_photo_quality(context)
                        speaker_role = self._determine_speaker_role(
                            context, speaker_data
                        )

                        # Create enhanced detection details
                        enhanced_details = speaker_data.copy()
                        enhanced_details.update(
                            {
                                "photo_type": photo_type,
                                "speaker_role": speaker_role,
                                "industry_relevance": (
                                    "high"
                                    if enhanced_confidence > 0.8
                                    else (
                                        "medium"
                                        if enhanced_confidence > 0.7
                                        else "standard"
                                    )
                                ),
                                "recognition_method": (
                                    "crypto_enhanced"
                                    if enhanced_confidence > confidence
                                    else "standard_detection"
                                ),
                            }
                        )

                        detection = SpeakerDetection(
                            name=enhanced_name,
                            title=enhanced_title,
                            organization=enhanced_org,
                            confidence=final_confidence,
                            confidence_level=self._calculate_confidence_level(
                                final_confidence
                            ),
                            context=context,
                            image_url=image_urls[0] if image_urls else "",
                            detection_details=enhanced_details,
                        )

                        speaker_detections.append(detection)

                    self.logger.info(
                        f"[{self.name}] Speaker analysis found {len(speaker_detections)} speakers"
                    )
                    return speaker_detections

                except json.JSONDecodeError as e:
                    self.logger.warning(
                        f"[{self.name}] Could not parse speaker JSON response: {e}"
                    )
                    return []

            return []

        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during speaker analysis: {e}", exc_info=True
            )
            return []

    async def run_comprehensive_analysis(
        self, image_urls: List[str], gemini_model: Any
    ) -> Dict[str, Any]:
        """Run comprehensive image analysis including sponsors and speakers"""

        self.logger.info(
            f"[{self.name}] Starting comprehensive analysis of {len(image_urls)} images"
        )

        # Run both analyses concurrently
        sponsor_task = self.analyze_sponsors_and_logos(image_urls, gemini_model)
        speaker_task = self.analyze_speakers(image_urls, gemini_model)

        sponsor_detections, speaker_detections = await asyncio.gather(
            sponsor_task, speaker_task, return_exceptions=True
        )

        # Handle exceptions
        if isinstance(sponsor_detections, Exception):
            self.logger.error(f"Sponsor detection failed: {sponsor_detections}")
            sponsor_detections = []

        if isinstance(speaker_detections, Exception):
            self.logger.error(f"Speaker detection failed: {speaker_detections}")
            speaker_detections = []

        # Compile results
        results = {
            "sponsors": [
                {
                    "name": s.name,
                    "confidence": s.confidence,
                    "tier": s.tier.value,
                    "confidence_level": s.confidence_level.value,
                    "context": s.context,
                }
                for s in sponsor_detections
            ],
            "speakers": [
                {
                    "name": s.name,
                    "title": s.title,
                    "organization": s.organization,
                    "confidence": s.confidence,
                    "confidence_level": s.confidence_level.value,
                    "context": s.context,
                }
                for s in speaker_detections
            ],
            "summary": {
                "total_sponsors": len(sponsor_detections),
                "total_speakers": len(speaker_detections),
                "high_confidence_sponsors": len(
                    [
                        s
                        for s in sponsor_detections
                        if s.confidence_level == ConfidenceLevel.HIGH
                    ]
                ),
                "high_confidence_speakers": len(
                    [
                        s
                        for s in speaker_detections
                        if s.confidence_level == ConfidenceLevel.HIGH
                    ]
                ),
                "sponsor_tiers": {
                    tier.value: len([s for s in sponsor_detections if s.tier == tier])
                    for tier in SponsorTier
                },
            },
        }

        self.logger.info(
            f"[{self.name}] Comprehensive analysis complete: {results['summary']}"
        )
        return results

    # Backward compatibility method
    async def run_async(self, image_urls: List[str], gemini_model: Any) -> List[str]:
        """Backward compatible method for existing integration"""
        results = await self.run_comprehensive_analysis(image_urls, gemini_model)

        # Return simple list of sponsor names for backward compatibility
        sponsor_names = [sponsor["name"] for sponsor in results["sponsors"]]
        return sponsor_names
