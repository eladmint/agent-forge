"""
🎯 Visual Intelligence Agent for Agent Forge - Enterprise Brand & Competitive Monitoring

ENTERPRISE USE CASES:
- Real-time competitor brand monitoring across websites and social media
- Logo detection and brand presence analysis for market intelligence
- Visual content analysis for marketing competitive research
- Speaker/executive identification for business intelligence
- Corporate event monitoring and competitive positioning

UNIVERSAL MCP COMPATIBILITY:
- Works across ChatGPT, Claude Desktop, Google Gemini, VS Code, Cursor, Zed
- Natural language interface for visual analysis requests
- Cross-platform brand monitoring and competitive intelligence

ENHANCED CAPABILITIES:
- Multi-industry brand recognition (beyond crypto/blockchain)
- Advanced confidence scoring and tier classification
- Enterprise-grade error handling and logging
- Extensible knowledge bases for different verticals

Based on Nuru AI's Enhanced Image Analysis Agent with enterprise adaptations.
"""

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

# Agent Forge imports
from agent_forge.core.agents.base import AsyncContextAgent


class CompanyTier(Enum):
    """Company/sponsor tier classification"""
    TITLE = "title"
    PREMIUM = "premium"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    PARTNER = "partner"
    MEDIA = "media"
    STARTUP = "startup"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence level for detection"""
    VERY_HIGH = "very_high"  # 0.9+
    HIGH = "high"  # 0.8-0.9
    MEDIUM = "medium"  # 0.6-0.8
    LOW = "low"  # 0.4-0.6
    VERY_LOW = "very_low"  # <0.4


@dataclass
class BrandDetection:
    """Enhanced brand/company detection result"""
    name: str
    confidence: float
    tier: CompanyTier
    confidence_level: ConfidenceLevel
    context: str
    image_url: str
    industry: Optional[str]
    detection_details: Dict[str, Any]


@dataclass
class ExecutiveDetection:
    """Executive/speaker detection result from photos"""
    name: str
    title: Optional[str]
    organization: Optional[str]
    confidence: float
    confidence_level: ConfidenceLevel
    context: str
    image_url: str
    industry_relevance: str
    detection_details: Dict[str, Any]


class VisualIntelligenceAgent(AsyncContextAgent):
    """Enterprise Visual Intelligence Agent for brand monitoring and competitive analysis"""

    # Tech industry companies (expandable knowledge base)
    TECH_COMPANIES = {
        # Major Tech
        "microsoft", "google", "apple", "amazon", "meta", "facebook", "tesla", "nvidia", 
        "salesforce", "oracle", "ibm", "intel", "adobe", "servicenow", "workday",
        
        # Cloud & Enterprise
        "aws", "azure", "gcp", "snowflake", "databricks", "palantir", "cloudflare",
        "mongodb", "elastic", "confluent", "datadog", "splunk", "okta",
        
        # Fintech
        "stripe", "square", "paypal", "plaid", "robinhood", "coinbase", "affirm",
        
        # Crypto/Blockchain (from original)
        "binance", "ethereum", "polygon", "solana", "avalanche", "chainlink", "uniswap",
        "opensea", "metamask", "ledger", "consensys", "near", "cosmos", "polkadot",
        
        # AI/ML
        "openai", "anthropic", "scale", "huggingface", "cohere", "stability",
        
        # Startups & Unicorns
        "notion", "figma", "canva", "discord", "slack", "zoom", "atlassian",
        "github", "gitlab", "docker", "kubernetes", "hashicorp", "terraform"
    }

    # Industry executives and leaders (expandable)
    TECH_EXECUTIVES = {
        "satya nadella": {"title": "CEO", "organization": "Microsoft"},
        "sundar pichai": {"title": "CEO", "organization": "Google"},
        "tim cook": {"title": "CEO", "organization": "Apple"},
        "andy jassy": {"title": "CEO", "organization": "Amazon"},
        "mark zuckerberg": {"title": "CEO", "organization": "Meta"},
        "elon musk": {"title": "CEO", "organization": "Tesla"},
        "jensen huang": {"title": "CEO", "organization": "NVIDIA"},
        "marc benioff": {"title": "CEO", "organization": "Salesforce"},
        "brian chesky": {"title": "CEO", "organization": "Airbnb"},
        "patrick collison": {"title": "CEO", "organization": "Stripe"},
        "john collison": {"title": "President", "organization": "Stripe"},
        "sam altman": {"title": "CEO", "organization": "OpenAI"},
        "dario amodei": {"title": "CEO", "organization": "Anthropic"},
        "brian armstrong": {"title": "CEO", "organization": "Coinbase"},
        "vitalik buterin": {"title": "Co-founder", "organization": "Ethereum"},
    }

    # Tier classification indicators
    TIER_INDICATORS = {
        CompanyTier.TITLE: ["title sponsor", "presenting sponsor", "main sponsor", "headline sponsor", "keynote sponsor"],
        CompanyTier.PREMIUM: ["premium sponsor", "platinum sponsor", "premier sponsor"],
        CompanyTier.GOLD: ["gold sponsor", "major sponsor", "principal sponsor"],
        CompanyTier.SILVER: ["silver sponsor", "supporting sponsor", "associate sponsor"],
        CompanyTier.BRONZE: ["bronze sponsor", "community sponsor", "standard sponsor"],
        CompanyTier.PARTNER: ["partner", "official partner", "technology partner", "strategic partner"],
        CompanyTier.MEDIA: ["media partner", "media sponsor", "press partner"],
        CompanyTier.STARTUP: ["startup", "emerging company", "innovation partner"],
    }

    def __init__(self, name: str = "VisualIntelligenceAgent", **kwargs):
        """Initialize the Visual Intelligence Agent"""
        super().__init__(name=name, **kwargs)
        self.genai_model = None
        self.logger.info(f"[{self.name}] Initialized Enterprise Visual Intelligence Agent")

    async def initialize(self):
        """Initialize the agent (part of AsyncContextAgent lifecycle)"""
        self.logger.info(f"[{self.name}] Visual Intelligence Agent ready for enterprise brand monitoring")

    async def cleanup(self):
        """Cleanup resources (part of AsyncContextAgent lifecycle)"""
        self.logger.info(f"[{self.name}] Visual Intelligence Agent cleanup complete")

    def _create_brand_monitoring_prompt(self, image_urls: List[str], target_industry: str = "technology") -> List[str]:
        """Create enhanced prompt for brand/logo detection with industry focus"""

        if target_industry.lower() in ["tech", "technology", "ai", "software"]:
            companies_list = ", ".join(list(self.TECH_COMPANIES)[:25])
            industry_focus = "technology, AI, software, cloud, fintech, and emerging tech companies"
        else:
            companies_list = "various industry leaders"
            industry_focus = f"{target_industry} industry companies and market leaders"

        prompt_parts = [
            f"""Analyze the following image(s) for comprehensive brand monitoring and competitive intelligence. You are an expert in {industry_focus} recognition.

DETECTION TARGETS:
1. **Company Logos**: Identify any visible company logos, brand marks, corporate identities, watermarks
2. **Brand Positioning**: Determine competitive positioning from visual placement, size, prominence  
3. **Text Recognition**: Extract company names from signage, banners, presentations, overlays
4. **Market Intelligence**: Understand competitive relationships and market presence from visual context
5. **Event Branding**: Conference sponsors, partners, exhibitors, and their tier positioning

INDUSTRY FOCUS - {target_industry.upper()}:
Pay special attention to: {companies_list}
Also detect: Startups, unicorns, public companies, private companies, consulting firms, vendors

COMPETITIVE TIER ANALYSIS:
- **Title/Keynote**: Dominant branding, main stage presence, primary positioning, largest logos
- **Premium/Platinum**: Major branding presence, prominent placement, significant visual real estate
- **Gold/Principal**: Strong branding presence, good visibility, upper-tier positioning  
- **Silver/Supporting**: Moderate branding presence, clear visibility, mid-tier positioning
- **Bronze/Standard**: Basic branding presence, standard visibility, lower-tier positioning
- **Partner/Strategic**: Technology/business partners, often with "Partner" designation
- **Media/Press**: Media partners, press sponsors, publication logos
- **Startup/Innovation**: Emerging companies, innovation showcases, startup pavilions

OUTPUT FORMAT (JSON):
{{
    "brands": [
        {{
            "name": "Company Name",
            "confidence": 0.95,
            "tier": "premium",
            "industry": "technology",
            "context": "Large logo prominently displayed on main conference backdrop with premium positioning",
            "visual_prominence": "high",
            "detection_method": "logo_recognition_and_text_analysis",
            "competitive_intelligence": "Major sponsor positioning suggests significant market investment"
        }}
    ],
    "market_intelligence": {{
        "dominant_brands": ["Brand1", "Brand2"],
        "competitive_landscape": "Brief analysis of competitive positioning",
        "industry_trends": "Observable trends from brand presence"
    }}
}}

ANALYSIS REQUIREMENTS:
- Provide confidence scores (0.0-1.0) based on logo clarity, text readability, and recognition certainty
- Include detailed context explaining brand positioning and competitive significance
- Classify tier based on visual prominence, placement hierarchy, and market positioning
- Focus on market intelligence value - explain competitive insights from brand presence
- Identify industry trends and market dynamics visible through brand positioning

Analyze each image thoroughly for competitive intelligence and return comprehensive JSON response.""",
        ]

        return prompt_parts

    def _create_executive_detection_prompt(self, image_urls: List[str], target_industry: str = "technology") -> List[str]:
        """Create enhanced prompt for executive/leader detection with industry focus"""

        if target_industry.lower() in ["tech", "technology", "ai", "software"]:
            executives_sample = list(self.TECH_EXECUTIVES.keys())[:15]
            executives_list = ", ".join([name.title() for name in executives_sample])
            industry_focus = "technology, AI, software, and emerging tech industry"
        else:
            executives_list = "various industry leaders and executives"
            industry_focus = f"{target_industry} industry"

        prompt_parts = [
            f"""Analyze the following image(s) for comprehensive executive identification and business intelligence. You are an expert in {industry_focus} leader recognition.

DETECTION TARGETS:
1. **Executive Photos**: Individual headshots, panel photos, keynote speakers, group executive photos
2. **Name Extraction**: Executive names from photo captions, overlays, name tags, presentation slides
3. **Title/Role Detection**: C-level titles, founder roles, VP positions, board positions
4. **Company Intelligence**: Current and former company affiliations, board positions
5. **Event Context**: Speaking roles, panel participation, keynote presentations, networking events

{industry_focus.upper()} EXECUTIVE FOCUS:
Pay special attention to these known leaders: {executives_list}
Also look for: CEOs, CTOs, Founders, VPs, Board Members, Investors, Industry Analysts

EXECUTIVE IDENTIFICATION METHODS:
- **Text-based Detection**: Names from photo captions, slides, name tags, conference badges, introductions
- **Visual Context Analysis**: Executive presence, stage positioning, speaking gestures, audience engagement
- **Professional Recognition**: C-level positioning, company branding, role indicators, panel placement
- **Business Intelligence**: Company transitions, new roles, industry movement, market presence
- **Quality Assessment**: Photo clarity, text readability, context relevance, executive prominence

BUSINESS INTELLIGENCE FEATURES:
- **Executive Roles**: CEO, CTO, Founder, President, VP, Board Member, Advisor, Investor
- **Photo Context**: Keynote, panel, fireside chat, networking, award presentation, company event
- **Market Significance**: Industry influence, company valuation, market position, strategic importance
- **Career Intelligence**: Role changes, company moves, new ventures, board appointments

OUTPUT FORMAT (JSON):
{{
    "executives": [
        {{
            "name": "Executive Name",
            "title": "CEO/Founder/CTO",
            "organization": "Company Name",
            "confidence": 0.92,
            "context": "Keynote speaker at main stage with company branding and title overlay",
            "detection_method": "photo_caption_and_visual_context_analysis",
            "executive_role": "keynote_speaker",
            "photo_type": "professional_keynote",
            "industry_relevance": "very_high",
            "business_intelligence": "CEO of major technology company, significant market influence",
            "market_context": "Leading voice in AI/technology space with strategic industry impact"
        }}
    ],
    "business_intelligence": {{
        "executive_summary": "Overview of executive presence and market significance",
        "company_representation": "Analysis of companies represented",
        "industry_trends": "Executive participation trends and market signals"
    }}
}}

ANALYSIS REQUIREMENTS:
- Extract complete names and current titles when visible
- Include comprehensive company affiliations and role history when available
- Provide confidence based on text clarity, visual context, and recognition certainty
- Describe detection context and business significance
- Classify executive role and event participation type
- Assess industry relevance and market influence
- Focus on business intelligence value - explain market significance
- Include strategic context about executive presence and industry positioning

Return comprehensive JSON response with all detected executives and rich business intelligence metadata.""",
        ]

        return prompt_parts

    def _calculate_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to confidence level enum"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _classify_company_tier(self, context: str, name: str) -> CompanyTier:
        """Classify company tier based on context and visual positioning"""
        context_lower = context.lower()
        name_lower = name.lower()

        # Check for explicit tier mentions
        for tier, indicators in self.TIER_INDICATORS.items():
            for indicator in indicators:
                if indicator in context_lower or indicator in name_lower:
                    return tier

        # Visual prominence heuristics for competitive intelligence
        if any(word in context_lower for word in ["keynote", "main stage", "primary", "dominant", "title"]):
            return CompanyTier.TITLE
        elif any(word in context_lower for word in ["premium", "platinum", "premier", "major"]):
            return CompanyTier.PREMIUM
        elif any(word in context_lower for word in ["gold", "principal", "large", "prominent"]):
            return CompanyTier.GOLD
        elif any(word in context_lower for word in ["silver", "supporting", "associate", "secondary"]):
            return CompanyTier.SILVER
        elif any(word in context_lower for word in ["bronze", "standard", "community", "basic"]):
            return CompanyTier.BRONZE
        elif any(word in context_lower for word in ["startup", "emerging", "innovation", "new"]):
            return CompanyTier.STARTUP
        elif any(word in context_lower for word in ["partner", "technology", "strategic", "alliance"]):
            return CompanyTier.PARTNER
        elif any(word in context_lower for word in ["media", "press", "publication", "news"]):
            return CompanyTier.MEDIA

        return CompanyTier.UNKNOWN

    def _enhance_brand_recognition(self, detected_name: str, industry: str = "technology") -> Tuple[str, float, str]:
        """Enhance recognition for industry companies with market intelligence"""
        name_lower = detected_name.lower()

        # Check against known companies
        if industry.lower() in ["tech", "technology", "ai", "software"]:
            for company in self.TECH_COMPANIES:
                if company in name_lower or name_lower in company:
                    return company.title(), 0.95, "technology"  # High confidence for known entities

        # Industry-specific term enhancement
        industry_terms = {
            "technology": ["ai", "ml", "saas", "cloud", "api", "platform", "tech", "software", "data"],
            "finance": ["fintech", "bank", "capital", "fund", "investment", "trading", "payment"],
            "healthcare": ["health", "medical", "pharma", "biotech", "diagnostic", "therapeutic"],
            "retail": ["commerce", "marketplace", "retail", "shopping", "consumer", "brand"]
        }

        for term_category, terms in industry_terms.items():
            for term in terms:
                if term in name_lower:
                    return detected_name, 0.85, term_category

        return detected_name, 0.7, "general"

    def _enhance_executive_recognition(
        self, detected_name: str, detected_title: str = "", detected_org: str = "", industry: str = "technology"
    ) -> Tuple[str, str, str, float, str]:
        """Enhance executive recognition with business intelligence"""
        name_lower = detected_name.lower().strip()

        # Check against known executives
        if industry.lower() in ["tech", "technology", "ai", "software"]:
            if name_lower in self.TECH_EXECUTIVES:
                exec_info = self.TECH_EXECUTIVES[name_lower]
                enhanced_name = detected_name.title()
                enhanced_title = detected_title or exec_info.get("title", "")
                enhanced_org = detected_org or exec_info.get("organization", "")
                return enhanced_name, enhanced_title, enhanced_org, 0.95, "very_high"

            # Partial name matching for known executives
            for known_exec, info in self.TECH_EXECUTIVES.items():
                known_parts = known_exec.split()
                detected_parts = name_lower.split()

                if len(known_parts) >= 2 and len(detected_parts) >= 2:
                    if (known_parts[0] in detected_parts and known_parts[-1] in detected_parts):
                        enhanced_name = known_exec.title()
                        enhanced_title = detected_title or info.get("title", "")
                        enhanced_org = detected_org or info.get("organization", "")
                        return enhanced_name, enhanced_title, enhanced_org, 0.90, "high"

        # Check organization for industry relevance
        org_lower = detected_org.lower()
        if industry.lower() in ["tech", "technology"] and any(company in org_lower for company in self.TECH_COMPANIES):
            return detected_name, detected_title, detected_org, 0.85, "high"

        # Title-based industry relevance
        title_lower = detected_title.lower()
        exec_titles = ["ceo", "cto", "founder", "president", "vp", "chief", "director", "head"]
        if any(title in title_lower for title in exec_titles):
            return detected_name, detected_title, detected_org, 0.80, "medium"

        return detected_name, detected_title, detected_org, 0.7, "standard"

    async def analyze_brand_presence(
        self, image_urls: List[str], gemini_model: Any, target_industry: str = "technology"
    ) -> List[BrandDetection]:
        """Advanced brand presence analysis for competitive intelligence"""

        if not image_urls or not gemini_model:
            self.logger.info(f"[{self.name}] No image URLs or model provided for brand analysis.")
            return []

        self.logger.info(f"[{self.name}] Analyzing {len(image_urls)} images for {target_industry} brand presence...")

        prompt_parts = self._create_brand_monitoring_prompt(image_urls, target_industry)
        full_prompt = prompt_parts + image_urls

        try:
            response = await asyncio.to_thread(gemini_model.generate_content, full_prompt)

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
                    brands_data = parsed_response.get("brands", [])

                    # Process detected brands
                    brand_detections = []
                    for brand_data in brands_data:
                        name = brand_data.get("name", "")
                        if not name:
                            continue

                        # Enhance brand recognition
                        enhanced_name, base_confidence, detected_industry = self._enhance_brand_recognition(
                            name, target_industry
                        )

                        confidence = brand_data.get("confidence", base_confidence)
                        confidence = min(confidence, 1.0)

                        context = brand_data.get("context", "")
                        tier = self._classify_company_tier(context, enhanced_name)

                        detection = BrandDetection(
                            name=enhanced_name,
                            confidence=confidence,
                            tier=tier,
                            confidence_level=self._calculate_confidence_level(confidence),
                            context=context,
                            image_url=image_urls[0] if image_urls else "",
                            industry=detected_industry,
                            detection_details=brand_data,
                        )

                        brand_detections.append(detection)

                    self.logger.info(f"[{self.name}] Brand analysis found {len(brand_detections)} companies")
                    return brand_detections

                except json.JSONDecodeError as e:
                    self.logger.warning(f"[{self.name}] Could not parse JSON response: {e}")
                    return []

            return []

        except Exception as e:
            self.logger.error(f"[{self.name}] Error during brand analysis: {e}", exc_info=True)
            return []

    async def analyze_executives(
        self, image_urls: List[str], gemini_model: Any, target_industry: str = "technology"
    ) -> List[ExecutiveDetection]:
        """Advanced executive detection for business intelligence"""

        if not image_urls or not gemini_model:
            self.logger.info(f"[{self.name}] No image URLs or model provided for executive analysis.")
            return []

        self.logger.info(f"[{self.name}] Analyzing {len(image_urls)} images for {target_industry} executives...")

        prompt_parts = self._create_executive_detection_prompt(image_urls, target_industry)
        full_prompt = prompt_parts + image_urls

        try:
            response = await asyncio.to_thread(gemini_model.generate_content, full_prompt)

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
                    executives_data = parsed_response.get("executives", [])

                    # Process detected executives
                    executive_detections = []
                    for exec_data in executives_data:
                        name = exec_data.get("name", "")
                        if not name:
                            continue

                        title = exec_data.get("title", "")
                        organization = exec_data.get("organization", "")
                        confidence = exec_data.get("confidence", 0.7)
                        context = exec_data.get("context", "")

                        # Enhance executive recognition
                        enhanced_name, enhanced_title, enhanced_org, enhanced_confidence, relevance = (
                            self._enhance_executive_recognition(name, title, organization, target_industry)
                        )

                        final_confidence = max(confidence, enhanced_confidence)
                        final_confidence = min(final_confidence, 1.0)

                        detection = ExecutiveDetection(
                            name=enhanced_name,
                            title=enhanced_title,
                            organization=enhanced_org,
                            confidence=final_confidence,
                            confidence_level=self._calculate_confidence_level(final_confidence),
                            context=context,
                            image_url=image_urls[0] if image_urls else "",
                            industry_relevance=relevance,
                            detection_details=exec_data,
                        )

                        executive_detections.append(detection)

                    self.logger.info(f"[{self.name}] Executive analysis found {len(executive_detections)} executives")
                    return executive_detections

                except json.JSONDecodeError as e:
                    self.logger.warning(f"[{self.name}] Could not parse executive JSON response: {e}")
                    return []

            return []

        except Exception as e:
            self.logger.error(f"[{self.name}] Error during executive analysis: {e}", exc_info=True)
            return []

    async def run_competitive_intelligence(
        self, image_urls: List[str], gemini_model: Any, target_industry: str = "technology"
    ) -> Dict[str, Any]:
        """Run comprehensive competitive intelligence analysis"""

        self.logger.info(
            f"[{self.name}] Starting competitive intelligence analysis of {len(image_urls)} images for {target_industry}"
        )

        # Run both analyses concurrently
        brand_task = self.analyze_brand_presence(image_urls, gemini_model, target_industry)
        executive_task = self.analyze_executives(image_urls, gemini_model, target_industry)

        brand_detections, executive_detections = await asyncio.gather(
            brand_task, executive_task, return_exceptions=True
        )

        # Handle exceptions
        if isinstance(brand_detections, Exception):
            self.logger.error(f"Brand detection failed: {brand_detections}")
            brand_detections = []

        if isinstance(executive_detections, Exception):
            self.logger.error(f"Executive detection failed: {executive_detections}")
            executive_detections = []

        # Compile competitive intelligence results
        results = {
            "brands": [
                {
                    "name": b.name,
                    "confidence": b.confidence,
                    "tier": b.tier.value,
                    "confidence_level": b.confidence_level.value,
                    "industry": b.industry,
                    "context": b.context,
                }
                for b in brand_detections
            ],
            "executives": [
                {
                    "name": e.name,
                    "title": e.title,
                    "organization": e.organization,
                    "confidence": e.confidence,
                    "confidence_level": e.confidence_level.value,
                    "industry_relevance": e.industry_relevance,
                    "context": e.context,
                }
                for e in executive_detections
            ],
            "competitive_intelligence": {
                "total_brands": len(brand_detections),
                "total_executives": len(executive_detections),
                "high_confidence_brands": len([b for b in brand_detections if b.confidence >= 0.8]),
                "high_confidence_executives": len([e for e in executive_detections if e.confidence >= 0.8]),
                "brand_tiers": {
                    tier.value: len([b for b in brand_detections if b.tier == tier])
                    for tier in CompanyTier
                },
                "target_industry": target_industry,
                "analysis_summary": f"Detected {len(brand_detections)} brands and {len(executive_detections)} executives in {target_industry} competitive landscape",
            },
        }

        self.logger.info(f"[{self.name}] Competitive intelligence analysis complete")
        return results

    async def run(self, image_urls: List[str], gemini_model: Any = None, target_industry: str = "technology", **kwargs) -> Dict[str, Any]:
        """Main entry point for visual intelligence analysis"""
        return await self.run_competitive_intelligence(image_urls, gemini_model, target_industry)

    # MCP Compatibility Methods
    async def analyze_images_for_brands(self, image_urls: List[str], industry: str = "technology") -> List[str]:
        """MCP-compatible method for brand detection"""
        # This would be called through MCP with proper model injection
        results = await self.run_competitive_intelligence(image_urls, None, industry)
        return [brand["name"] for brand in results["brands"]]

    async def monitor_competitor_presence(self, image_urls: List[str], competitors: List[str]) -> Dict[str, Any]:
        """MCP-compatible method for competitor monitoring"""
        results = await self.run_competitive_intelligence(image_urls, None)
        detected_competitors = [
            brand for brand in results["brands"] 
            if any(comp.lower() in brand["name"].lower() for comp in competitors)
        ]
        return {
            "detected_competitors": detected_competitors,
            "total_competitor_presence": len(detected_competitors),
            "competitive_analysis": f"Found {len(detected_competitors)} target competitors out of {len(results['brands'])} total brands detected"
        }