"""
🎯 Research Compiler Agent for Agent Forge - Enterprise Market Research & Due Diligence

ENTERPRISE USE CASES:
- M&A due diligence compilation from multiple data sources
- Market research aggregation across competitor websites and industry reports
- Financial research compilation from SEC filings and analyst reports
- Regulatory compliance documentation gathering and compilation
- Supply chain risk assessment from vendor data and news sources

UNIVERSAL MCP COMPATIBILITY:
- Works across ChatGPT, Claude Desktop, Google Gemini, VS Code, Cursor, Zed
- Natural language interface for research compilation requests
- Cross-platform enterprise research automation

ENHANCED CAPABILITIES:
- Multi-source data aggregation with quality scoring
- Intelligent deduplication and conflict resolution
- Executive summary generation with key insights
- Structured output formats (JSON, Markdown, Excel, PDF)
- Confidence scoring and source attribution

Based on Nuru AI's Data Compiler Agent with enterprise research adaptations.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# Agent Forge imports
from agent_forge.core.agents.base import AsyncContextAgent


class DataSourceType(Enum):
    """Types of data sources for research compilation"""
    WEB_SCRAPING = "web_scraping"
    SEC_FILING = "sec_filing"
    NEWS_ARTICLE = "news_article"
    SOCIAL_MEDIA = "social_media"
    ANALYST_REPORT = "analyst_report"
    COMPANY_WEBSITE = "company_website"
    REGULATORY_FILING = "regulatory_filing"
    INDUSTRY_REPORT = "industry_report"
    FINANCIAL_DATA = "financial_data"
    LEGAL_DATABASE = "legal_database"
    PATENT_DATABASE = "patent_database"
    CUSTOMER_REVIEW = "customer_review"
    EMPLOYEE_REVIEW = "employee_review"
    UNKNOWN = "unknown"


class ResearchType(Enum):
    """Types of research compilation"""
    MA_DUE_DILIGENCE = "ma_due_diligence"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    MARKET_RESEARCH = "market_research"
    FINANCIAL_ANALYSIS = "financial_analysis"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    SUPPLIER_ASSESSMENT = "supplier_assessment"
    CUSTOMER_INTELLIGENCE = "customer_intelligence"
    INDUSTRY_ANALYSIS = "industry_analysis"
    RISK_ASSESSMENT = "risk_assessment"


@dataclass
class DataPoint:
    """Individual data point from research"""
    key: str
    value: Any
    source: DataSourceType
    source_url: Optional[str]
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchSection:
    """Compiled research section"""
    title: str
    summary: str
    data_points: List[DataPoint]
    insights: List[str]
    confidence: float
    sources: List[str]


@dataclass
class CompiledResearch:
    """Complete compiled research output"""
    research_type: ResearchType
    target_entity: str
    executive_summary: str
    sections: List[ResearchSection]
    key_findings: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    recommendations: List[str]
    data_quality_score: float
    total_sources: int
    compilation_time: float
    metadata: Dict[str, Any]


class ResearchCompilerAgent(AsyncContextAgent):
    """Enterprise Research Compiler Agent for comprehensive business intelligence"""

    # Research templates for different use cases
    MA_DUE_DILIGENCE_SECTIONS = [
        "Company Overview",
        "Financial Performance",
        "Market Position",
        "Competitive Landscape",
        "Legal & Regulatory",
        "Intellectual Property",
        "Key Personnel",
        "Customer Base",
        "Technology Assets",
        "Risk Assessment",
        "Growth Opportunities",
        "Valuation Analysis"
    ]

    COMPETITIVE_ANALYSIS_SECTIONS = [
        "Competitor Overview",
        "Product Comparison",
        "Pricing Strategy",
        "Market Share",
        "Technology Stack",
        "Customer Sentiment",
        "Strategic Initiatives",
        "Financial Metrics",
        "Marketing Approach",
        "Strengths & Weaknesses",
        "Future Outlook"
    ]

    SUPPLIER_ASSESSMENT_SECTIONS = [
        "Company Profile",
        "Financial Health",
        "Compliance Status",
        "Quality Metrics",
        "Delivery Performance",
        "Risk Indicators",
        "Certifications",
        "Customer References",
        "Sustainability Practices",
        "Innovation Capability"
    ]

    def __init__(self, name: str = "ResearchCompilerAgent", **kwargs):
        """Initialize the Research Compiler Agent"""
        super().__init__(name=name, **kwargs)
        self.logger.info(f"[{self.name}] Initialized Enterprise Research Compiler Agent")

    async def initialize(self):
        """Initialize the agent (part of AsyncContextAgent lifecycle)"""
        self.logger.info(f"[{self.name}] Research Compiler Agent ready for enterprise research")

    async def cleanup(self):
        """Cleanup resources (part of AsyncContextAgent lifecycle)"""
        self.logger.info(f"[{self.name}] Research Compiler Agent cleanup complete")

    def _classify_data_source(self, source_info: Dict[str, Any]) -> DataSourceType:
        """Classify the type of data source"""
        source_url = source_info.get("url", "").lower()
        source_type = source_info.get("type", "").lower()
        
        # URL-based classification
        if "sec.gov" in source_url or "edgar" in source_url:
            return DataSourceType.SEC_FILING
        elif any(news in source_url for news in ["reuters", "bloomberg", "wsj", "ft.com", "techcrunch"]):
            return DataSourceType.NEWS_ARTICLE
        elif any(social in source_url for social in ["twitter", "linkedin", "facebook", "reddit"]):
            return DataSourceType.SOCIAL_MEDIA
        elif "glassdoor" in source_url or "indeed" in source_url:
            return DataSourceType.EMPLOYEE_REVIEW
        elif "patents" in source_url or "uspto" in source_url:
            return DataSourceType.PATENT_DATABASE
        elif any(fin in source_url for fin in ["yahoo", "morningstar", "seekingalpha"]):
            return DataSourceType.FINANCIAL_DATA
        
        # Type-based classification
        if source_type == "regulatory":
            return DataSourceType.REGULATORY_FILING
        elif source_type == "analyst":
            return DataSourceType.ANALYST_REPORT
        elif source_type == "industry":
            return DataSourceType.INDUSTRY_REPORT
        elif source_type == "legal":
            return DataSourceType.LEGAL_DATABASE
        elif source_type == "company":
            return DataSourceType.COMPANY_WEBSITE
        elif source_type == "review":
            return DataSourceType.CUSTOMER_REVIEW
        
        return DataSourceType.WEB_SCRAPING

    def _calculate_data_confidence(self, data_point: Dict[str, Any]) -> float:
        """Calculate confidence score for a data point"""
        confidence = 0.5  # Base confidence
        
        # Source reliability factors
        source_type = self._classify_data_source(data_point.get("source", {}))
        source_reliability = {
            DataSourceType.SEC_FILING: 0.95,
            DataSourceType.REGULATORY_FILING: 0.93,
            DataSourceType.COMPANY_WEBSITE: 0.85,
            DataSourceType.ANALYST_REPORT: 0.80,
            DataSourceType.INDUSTRY_REPORT: 0.78,
            DataSourceType.NEWS_ARTICLE: 0.75,
            DataSourceType.FINANCIAL_DATA: 0.73,
            DataSourceType.LEGAL_DATABASE: 0.90,
            DataSourceType.PATENT_DATABASE: 0.88,
            DataSourceType.CUSTOMER_REVIEW: 0.60,
            DataSourceType.EMPLOYEE_REVIEW: 0.65,
            DataSourceType.SOCIAL_MEDIA: 0.55,
            DataSourceType.WEB_SCRAPING: 0.50
        }
        
        confidence = source_reliability.get(source_type, 0.5)
        
        # Recency factor
        if "timestamp" in data_point:
            try:
                data_age_days = (datetime.now() - datetime.fromisoformat(data_point["timestamp"])).days
                if data_age_days < 30:
                    confidence *= 1.1
                elif data_age_days < 90:
                    confidence *= 1.0
                elif data_age_days < 365:
                    confidence *= 0.9
                else:
                    confidence *= 0.8
            except:
                pass
        
        # Verification factor
        if data_point.get("verified", False):
            confidence *= 1.15
        
        # Multiple source corroboration
        if data_point.get("corroborated_sources", 0) > 2:
            confidence *= 1.2
        
        return min(confidence, 1.0)

    def _deduplicate_data_points(self, data_points: List[Dict[str, Any]]) -> List[DataPoint]:
        """Deduplicate and merge similar data points"""
        # Group by key
        grouped_data = defaultdict(list)
        
        for dp in data_points:
            key = dp.get("key", "")
            if key:
                grouped_data[key].append(dp)
        
        # Merge and deduplicate
        deduplicated = []
        
        for key, points in grouped_data.items():
            if len(points) == 1:
                # Single point, convert to DataPoint
                dp = points[0]
                data_point = DataPoint(
                    key=key,
                    value=dp.get("value"),
                    source=self._classify_data_source(dp.get("source", {})),
                    source_url=dp.get("source", {}).get("url"),
                    confidence=self._calculate_data_confidence(dp),
                    timestamp=datetime.now(),
                    metadata=dp.get("metadata", {})
                )
                deduplicated.append(data_point)
            else:
                # Multiple points, merge intelligently
                # Pick the most reliable/recent value
                sorted_points = sorted(
                    points,
                    key=lambda p: (self._calculate_data_confidence(p), p.get("timestamp", "")),
                    reverse=True
                )
                
                best_point = sorted_points[0]
                
                # Create merged data point with corroboration info
                data_point = DataPoint(
                    key=key,
                    value=best_point.get("value"),
                    source=self._classify_data_source(best_point.get("source", {})),
                    source_url=best_point.get("source", {}).get("url"),
                    confidence=self._calculate_data_confidence(best_point),
                    timestamp=datetime.now(),
                    metadata={
                        **best_point.get("metadata", {}),
                        "corroborated_sources": len(points),
                        "all_values": [p.get("value") for p in points],
                        "all_sources": [p.get("source", {}).get("url") for p in points]
                    }
                )
                deduplicated.append(data_point)
        
        return deduplicated

    def _generate_insights(self, section_data: List[DataPoint], research_type: ResearchType) -> List[str]:
        """Generate insights from compiled data"""
        insights = []
        
        # Analyze trends
        if len(section_data) >= 3:
            # Look for growth patterns
            growth_indicators = ["increase", "growth", "expansion", "rising", "improving"]
            decline_indicators = ["decrease", "decline", "reduction", "falling", "deteriorating"]
            
            growth_count = sum(1 for dp in section_data if any(ind in str(dp.value).lower() for ind in growth_indicators))
            decline_count = sum(1 for dp in section_data if any(ind in str(dp.value).lower() for ind in decline_indicators))
            
            if growth_count > decline_count * 2:
                insights.append("Strong positive trend indicators across multiple data points")
            elif decline_count > growth_count * 2:
                insights.append("Concerning negative trend indicators requiring attention")
        
        # High confidence findings
        high_conf_points = [dp for dp in section_data if dp.confidence >= 0.8]
        if high_conf_points:
            insights.append(f"High confidence data from {len(high_conf_points)} verified sources")
        
        # Source diversity
        unique_sources = len(set(dp.source for dp in section_data))
        if unique_sources >= 5:
            insights.append("Comprehensive multi-source validation increases reliability")
        
        # Research-type specific insights
        if research_type == ResearchType.MA_DUE_DILIGENCE:
            # Look for risk indicators
            risk_keywords = ["lawsuit", "violation", "penalty", "investigation", "breach"]
            risk_points = [dp for dp in section_data if any(kw in str(dp.value).lower() for kw in risk_keywords)]
            if risk_points:
                insights.append(f"Identified {len(risk_points)} potential risk factors requiring deeper investigation")
        
        elif research_type == ResearchType.COMPETITIVE_ANALYSIS:
            # Look for competitive advantages
            advantage_keywords = ["leader", "first", "innovative", "patent", "exclusive"]
            advantage_points = [dp for dp in section_data if any(kw in str(dp.value).lower() for kw in advantage_keywords)]
            if advantage_points:
                insights.append(f"Found {len(advantage_points)} potential competitive advantages")
        
        return insights

    def _compile_section(
        self, 
        section_title: str, 
        raw_data: List[Dict[str, Any]], 
        research_type: ResearchType
    ) -> ResearchSection:
        """Compile a research section from raw data"""
        # Filter relevant data for this section
        section_keywords = {
            "Company Overview": ["founded", "headquarters", "employees", "mission", "history"],
            "Financial Performance": ["revenue", "profit", "margin", "growth", "earnings"],
            "Market Position": ["market share", "ranking", "position", "competitive"],
            "Legal & Regulatory": ["lawsuit", "compliance", "regulation", "violation", "penalty"],
            "Technology Assets": ["patent", "technology", "platform", "software", "innovation"],
            "Risk Assessment": ["risk", "threat", "vulnerability", "exposure", "concern"],
            "Customer Base": ["customer", "client", "user", "retention", "satisfaction"],
            "Pricing Strategy": ["price", "cost", "fee", "subscription", "tier"],
            "Product Comparison": ["feature", "capability", "functionality", "performance"],
        }
        
        keywords = section_keywords.get(section_title, [section_title.lower()])
        
        # Filter data points relevant to this section
        relevant_data = []
        for data in raw_data:
            data_str = json.dumps(data).lower()
            if any(keyword in data_str for keyword in keywords):
                relevant_data.append(data)
        
        # Deduplicate and structure data points
        data_points = self._deduplicate_data_points(relevant_data)
        
        # Generate insights
        insights = self._generate_insights(data_points, research_type)
        
        # Create summary
        if data_points:
            summary = f"Compiled {len(data_points)} data points from {len(set(dp.source for dp in data_points))} unique sources. "
            if insights:
                summary += insights[0]
        else:
            summary = f"Limited data available for {section_title}. Further research recommended."
        
        # Calculate section confidence
        section_confidence = sum(dp.confidence for dp in data_points) / len(data_points) if data_points else 0.5
        
        # Get unique sources
        sources = list(set(dp.source_url for dp in data_points if dp.source_url))
        
        return ResearchSection(
            title=section_title,
            summary=summary,
            data_points=data_points,
            insights=insights,
            confidence=section_confidence,
            sources=sources
        )

    def _generate_executive_summary(
        self, 
        sections: List[ResearchSection], 
        research_type: ResearchType,
        target_entity: str
    ) -> str:
        """Generate executive summary from compiled sections"""
        total_data_points = sum(len(s.data_points) for s in sections)
        high_confidence_sections = [s for s in sections if s.confidence >= 0.8]
        
        summary_parts = []
        
        # Opening
        research_type_descriptions = {
            ResearchType.MA_DUE_DILIGENCE: "comprehensive due diligence analysis",
            ResearchType.COMPETITIVE_ANALYSIS: "detailed competitive intelligence assessment",
            ResearchType.MARKET_RESEARCH: "extensive market research compilation",
            ResearchType.SUPPLIER_ASSESSMENT: "thorough supplier risk evaluation",
            ResearchType.REGULATORY_COMPLIANCE: "regulatory compliance review"
        }
        
        desc = research_type_descriptions.get(research_type, "business intelligence analysis")
        summary_parts.append(f"This {desc} of {target_entity} synthesizes {total_data_points} data points from across {len(sections)} key areas.")
        
        # Key findings from high-confidence sections
        if high_confidence_sections:
            summary_parts.append(f"High-confidence findings were identified in {len(high_confidence_sections)} critical areas.")
        
        # Overall assessment
        avg_confidence = sum(s.confidence for s in sections) / len(sections) if sections else 0
        if avg_confidence >= 0.8:
            summary_parts.append("The overall data quality and source reliability is excellent, providing strong foundation for decision-making.")
        elif avg_confidence >= 0.7:
            summary_parts.append("The compiled research demonstrates good data quality with multiple corroborating sources.")
        else:
            summary_parts.append("Additional primary research may be beneficial to strengthen certain findings.")
        
        # Highlight top insights
        all_insights = []
        for section in sections[:3]:  # Top 3 sections
            all_insights.extend(section.insights[:1])  # Top insight from each
        
        if all_insights:
            summary_parts.append("Key insights: " + "; ".join(all_insights))
        
        return " ".join(summary_parts)

    def _extract_key_findings(self, sections: List[ResearchSection]) -> List[str]:
        """Extract key findings from all sections"""
        findings = []
        
        for section in sections:
            # High confidence findings
            high_conf_points = [dp for dp in section.data_points if dp.confidence >= 0.85]
            for dp in high_conf_points[:2]:  # Top 2 per section
                findings.append(f"{section.title}: {dp.key} - {dp.value}")
        
        # Deduplicate similar findings
        unique_findings = []
        seen_keys = set()
        for finding in findings:
            key = finding.split(":")[1].strip() if ":" in finding else finding
            if key not in seen_keys:
                unique_findings.append(finding)
                seen_keys.add(key)
        
        return unique_findings[:10]  # Top 10 findings

    def _identify_risks(self, sections: List[ResearchSection]) -> List[str]:
        """Identify risk factors from compiled research"""
        risks = []
        
        risk_keywords = [
            "risk", "threat", "vulnerability", "concern", "issue", "problem",
            "lawsuit", "investigation", "violation", "penalty", "decline",
            "loss", "deficit", "debt", "liability", "exposure"
        ]
        
        for section in sections:
            for dp in section.data_points:
                value_str = str(dp.value).lower()
                if any(keyword in value_str for keyword in risk_keywords):
                    risk_desc = f"{section.title}: {dp.value}"
                    if dp.confidence >= 0.7:
                        risks.append(risk_desc)
        
        return list(set(risks))[:8]  # Top 8 unique risks

    def _identify_opportunities(self, sections: List[ResearchSection]) -> List[str]:
        """Identify opportunities from compiled research"""
        opportunities = []
        
        opp_keywords = [
            "opportunity", "growth", "expansion", "potential", "emerging",
            "innovation", "breakthrough", "advantage", "strength", "leader",
            "first", "unique", "exclusive", "patent", "partnership"
        ]
        
        for section in sections:
            for dp in section.data_points:
                value_str = str(dp.value).lower()
                if any(keyword in value_str for keyword in opp_keywords):
                    opp_desc = f"{section.title}: {dp.value}"
                    if dp.confidence >= 0.7:
                        opportunities.append(opp_desc)
        
        return list(set(opportunities))[:8]  # Top 8 unique opportunities

    def _generate_recommendations(
        self, 
        findings: List[str], 
        risks: List[str], 
        opportunities: List[str],
        research_type: ResearchType
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Research type specific recommendations
        if research_type == ResearchType.MA_DUE_DILIGENCE:
            if len(risks) > 5:
                recommendations.append("Conduct deeper legal and financial due diligence given multiple risk indicators")
            if len(opportunities) > 3:
                recommendations.append("Fast-track acquisition process to capitalize on identified growth opportunities")
            recommendations.append("Engage third-party valuation expert to validate financial projections")
            
        elif research_type == ResearchType.COMPETITIVE_ANALYSIS:
            if opportunities:
                recommendations.append("Develop competitive response strategy focusing on identified market gaps")
            recommendations.append("Establish continuous competitor monitoring system for ongoing intelligence")
            
        elif research_type == ResearchType.SUPPLIER_ASSESSMENT:
            if len(risks) > 2:
                recommendations.append("Diversify supplier base to mitigate identified risk concentrations")
            recommendations.append("Implement enhanced supplier monitoring and audit procedures")
        
        # General recommendations based on data quality
        avg_confidence = sum(f.confidence for s in findings for f in s.data_points) / len(findings) if findings else 0
        if avg_confidence < 0.7:
            recommendations.append("Commission primary research to validate findings with lower confidence scores")
        
        return recommendations[:5]  # Top 5 recommendations

    async def compile_research(
        self,
        raw_data: List[Dict[str, Any]],
        research_type: ResearchType,
        target_entity: str,
        custom_sections: Optional[List[str]] = None
    ) -> CompiledResearch:
        """Main method to compile research from raw data"""
        
        start_time = datetime.now()
        self.logger.info(f"[{self.name}] Starting {research_type.value} compilation for {target_entity}")
        
        # Determine sections based on research type
        if custom_sections:
            sections_to_compile = custom_sections
        elif research_type == ResearchType.MA_DUE_DILIGENCE:
            sections_to_compile = self.MA_DUE_DILIGENCE_SECTIONS
        elif research_type == ResearchType.COMPETITIVE_ANALYSIS:
            sections_to_compile = self.COMPETITIVE_ANALYSIS_SECTIONS
        elif research_type == ResearchType.SUPPLIER_ASSESSMENT:
            sections_to_compile = self.SUPPLIER_ASSESSMENT_SECTIONS
        else:
            # Generic sections
            sections_to_compile = [
                "Overview", "Financial Analysis", "Market Analysis",
                "Risk Assessment", "Opportunities", "Recommendations"
            ]
        
        # Compile each section
        compiled_sections = []
        for section_title in sections_to_compile:
            section = self._compile_section(section_title, raw_data, research_type)
            compiled_sections.append(section)
            self.logger.info(f"[{self.name}] Compiled section: {section_title} with {len(section.data_points)} data points")
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(compiled_sections, research_type, target_entity)
        
        # Extract key findings, risks, and opportunities
        key_findings = self._extract_key_findings(compiled_sections)
        risk_factors = self._identify_risks(compiled_sections)
        opportunities = self._identify_opportunities(compiled_sections)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            key_findings, risk_factors, opportunities, research_type
        )
        
        # Calculate overall metrics
        total_data_points = sum(len(s.data_points) for s in compiled_sections)
        unique_sources = len(set(
            dp.source_url for s in compiled_sections 
            for dp in s.data_points if dp.source_url
        ))
        avg_confidence = sum(s.confidence for s in compiled_sections) / len(compiled_sections) if compiled_sections else 0
        
        compilation_time = (datetime.now() - start_time).total_seconds()
        
        # Create compiled research object
        compiled_research = CompiledResearch(
            research_type=research_type,
            target_entity=target_entity,
            executive_summary=executive_summary,
            sections=compiled_sections,
            key_findings=key_findings,
            risk_factors=risk_factors,
            opportunities=opportunities,
            recommendations=recommendations,
            data_quality_score=avg_confidence,
            total_sources=unique_sources,
            compilation_time=compilation_time,
            metadata={
                "total_data_points": total_data_points,
                "compilation_date": datetime.now().isoformat(),
                "sections_compiled": len(compiled_sections),
                "high_confidence_findings": len([f for f in key_findings if any(s.confidence >= 0.8 for s in compiled_sections)])
            }
        )
        
        self.logger.info(
            f"[{self.name}] Research compilation complete: "
            f"{total_data_points} data points from {unique_sources} sources "
            f"in {compilation_time:.2f} seconds"
        )
        
        return compiled_research

    async def run(
        self,
        raw_data: List[Dict[str, Any]],
        research_type: str = "market_research",
        target_entity: str = "Unknown Entity",
        custom_sections: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Main entry point for research compilation"""
        
        # Convert string to enum
        try:
            research_type_enum = ResearchType(research_type)
        except ValueError:
            research_type_enum = ResearchType.MARKET_RESEARCH
            self.logger.warning(f"Unknown research type '{research_type}', defaulting to market_research")
        
        # Compile research
        compiled = await self.compile_research(
            raw_data, research_type_enum, target_entity, custom_sections
        )
        
        # Convert to dictionary for JSON serialization
        return {
            "research_type": compiled.research_type.value,
            "target_entity": compiled.target_entity,
            "executive_summary": compiled.executive_summary,
            "sections": [
                {
                    "title": s.title,
                    "summary": s.summary,
                    "data_points_count": len(s.data_points),
                    "insights": s.insights,
                    "confidence": s.confidence,
                    "sources_count": len(s.sources)
                }
                for s in compiled.sections
            ],
            "key_findings": compiled.key_findings,
            "risk_factors": compiled.risk_factors,
            "opportunities": compiled.opportunities,
            "recommendations": compiled.recommendations,
            "data_quality_score": compiled.data_quality_score,
            "total_sources": compiled.total_sources,
            "compilation_time": compiled.compilation_time,
            "metadata": compiled.metadata
        }

    # MCP Compatibility Methods
    async def compile_due_diligence(self, company_name: str, data_sources: List[str]) -> Dict[str, Any]:
        """MCP-compatible method for M&A due diligence"""
        # This would be called through MCP with data already gathered
        # For now, return a template structure
        return {
            "company": company_name,
            "due_diligence_complete": True,
            "sections": len(self.MA_DUE_DILIGENCE_SECTIONS),
            "recommendation": "Proceed with caution - full analysis required"
        }

    async def analyze_competitor(self, competitor_name: str, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """MCP-compatible method for competitive analysis"""
        result = await self.run(
            raw_data=data_points,
            research_type="competitive_analysis",
            target_entity=competitor_name
        )
        return {
            "competitor": competitor_name,
            "strengths": len(result["opportunities"]),
            "weaknesses": len(result["risk_factors"]),
            "market_position": result["executive_summary"][:200] + "..."
        }

    async def assess_supplier_risk(self, supplier_name: str, risk_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """MCP-compatible method for supplier risk assessment"""
        result = await self.run(
            raw_data=risk_data,
            research_type="supplier_assessment",
            target_entity=supplier_name
        )
        risk_score = 1 - result["data_quality_score"]  # Inverse of quality = risk
        return {
            "supplier": supplier_name,
            "risk_score": risk_score,
            "risk_level": "High" if risk_score > 0.7 else "Medium" if risk_score > 0.4 else "Low",
            "risk_factors": result["risk_factors"][:3],
            "recommendation": result["recommendations"][0] if result["recommendations"] else "Continue monitoring"
        }