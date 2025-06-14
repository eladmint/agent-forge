# Agent Forge Enterprise Agents Guide

## 🎯 Overview

This guide covers the two powerful enterprise agents adapted from Nuru AI's production-tested codebase for Agent Forge:

1. **Visual Intelligence Agent** - Enterprise brand monitoring and competitive intelligence through image analysis
2. **Research Compiler Agent** - Comprehensive business research automation for M&A, competitive analysis, and risk assessment

Both agents are MCP-compatible, enabling natural language access across ChatGPT, Claude Desktop, VS Code, Cursor, Zed, and any MCP-enabled platform.

## 🖼️ Visual Intelligence Agent

### Purpose
Transform visual content into actionable business intelligence by detecting brands, logos, executives, and competitive positioning from images.

### Enterprise Use Cases

#### 1. Competitive Intelligence at Trade Shows
```python
# Monitor competitor presence at industry events
results = await agent.monitor_competitor_presence(
    image_urls=["conference_photos/*.jpg"],
    competitors=["Microsoft", "Google", "Amazon", "Salesforce"]
)
# Output: Competitor booth sizes, sponsorship tiers, executive presence
```

#### 2. Brand Monitoring Across Markets
```python
# Track brand presence and positioning
brand_analysis = await agent.analyze_brand_presence(
    image_urls=["market_photos/*.jpg"],
    target_industry="technology"
)
# Output: Brand tier classification, market positioning, competitive landscape
```

#### 3. Executive Movement Tracking
```python
# Identify executives at events for business development
exec_results = await agent.analyze_executives(
    image_urls=["keynote_photos/*.jpg"],
    target_industry="fintech"
)
# Output: Executive names, titles, companies, speaking roles
```

### Key Features

- **Multi-Industry Support**: Pre-configured for tech, fintech, healthcare, retail
- **Tiered Classification**: Title, Premium, Gold, Silver, Bronze, Partner, Media, Startup
- **Confidence Scoring**: Very High (90%+), High (80-90%), Medium (60-80%), Low (40-60%)
- **Business Context**: Competitive positioning insights, not just detection

### Integration Example

```python
from agent_forge.examples.visual_intelligence_agent import VisualIntelligenceAgent

async def monitor_competitor_event():
    agent = VisualIntelligenceAgent()
    await agent.initialize()
    
    # Analyze tech conference for competitive intelligence
    results = await agent.run_competitive_intelligence(
        image_urls=["sponsor_wall.jpg", "main_stage.jpg", "expo_floor.jpg"],
        gemini_model=model,  # Your AI model
        target_industry="technology"
    )
    
    # Extract actionable insights
    print(f"Dominant brands: {results['competitive_intelligence']['brand_tiers']['title']}")
    print(f"New entrants: {results['competitive_intelligence']['brand_tiers']['startup']}")
    
    await agent.cleanup()
```

## 📚 Research Compiler Agent

### Purpose
Automate comprehensive business research by intelligently compiling, deduplicating, and analyzing data from multiple sources.

### Enterprise Use Cases

#### 1. M&A Due Diligence
```python
# Compile comprehensive due diligence report
dd_report = await agent.compile_research(
    raw_data=scraped_data,  # From web scraping, APIs, databases
    research_type=ResearchType.MA_DUE_DILIGENCE,
    target_entity="AcquisitionTarget Inc."
)
# Output: 12-section report with financials, risks, opportunities, recommendations
```

#### 2. Competitive Analysis
```python
# Deep competitive intelligence compilation
comp_analysis = await agent.run(
    raw_data=competitor_data,
    research_type="competitive_analysis",
    target_entity="MainCompetitor Corp"
)
# Output: Product comparison, pricing strategy, market position, SWOT analysis
```

#### 3. Supplier Risk Assessment
```python
# Evaluate supplier risks across multiple dimensions
risk_assessment = await agent.assess_supplier_risk(
    supplier_name="Global Supplies Ltd",
    risk_data=supplier_data
)
# Output: Risk score, compliance status, financial health, recommendations
```

### Key Features

- **Intelligent Deduplication**: Merges similar data points, tracks corroboration
- **Source Classification**: SEC filings (95% confidence), News (75%), Social Media (55%)
- **Automated Insights**: Trend detection, risk identification, opportunity discovery
- **Executive Summaries**: Auto-generated summaries with key findings

### Research Templates

#### M&A Due Diligence Sections
1. Company Overview
2. Financial Performance
3. Market Position
4. Competitive Landscape
5. Legal & Regulatory
6. Intellectual Property
7. Key Personnel
8. Customer Base
9. Technology Assets
10. Risk Assessment
11. Growth Opportunities
12. Valuation Analysis

#### Competitive Analysis Sections
1. Competitor Overview
2. Product Comparison
3. Pricing Strategy
4. Market Share
5. Technology Stack
6. Customer Sentiment
7. Strategic Initiatives
8. Financial Metrics
9. Marketing Approach
10. Strengths & Weaknesses
11. Future Outlook

### Integration Example

```python
from agent_forge.examples.research_compiler_agent import ResearchCompilerAgent, ResearchType

async def perform_due_diligence():
    agent = ResearchCompilerAgent()
    await agent.initialize()
    
    # Gather data from multiple sources
    raw_data = [
        {"key": "Revenue", "value": "$450M ARR", "source": {"url": "sec.gov", "type": "financial"}},
        {"key": "Patents", "value": "47 AI patents", "source": {"url": "uspto.gov", "type": "patent"}},
        {"key": "Customers", "value": "2500 enterprise", "source": {"url": "company.com", "type": "company"}}
    ]
    
    # Compile comprehensive report
    report = await agent.compile_research(
        raw_data=raw_data,
        research_type=ResearchType.MA_DUE_DILIGENCE,
        target_entity="TargetCorp"
    )
    
    print(f"Executive Summary: {report.executive_summary}")
    print(f"Key Risks: {report.risk_factors[:3]}")
    print(f"Opportunities: {report.opportunities[:3]}")
    print(f"Recommendation: {report.recommendations[0]}")
    
    await agent.cleanup()
```

## 🔌 MCP Integration

Both agents include MCP-compatible methods for natural language access:

### Visual Intelligence MCP Methods
- `analyze_images_for_brands()` - "Find all company logos in these conference photos"
- `monitor_competitor_presence()` - "Check if Microsoft, Google, or Amazon sponsored this event"

### Research Compiler MCP Methods
- `compile_due_diligence()` - "Create a due diligence report for TechCorp acquisition"
- `analyze_competitor()` - "Analyze competitive position of Salesforce"
- `assess_supplier_risk()` - "Evaluate risk level for our main supplier"

## 📊 Output Formats

### Visual Intelligence Output
```json
{
  "brands": [
    {
      "name": "Microsoft",
      "confidence": 0.95,
      "tier": "title",
      "industry": "technology",
      "context": "Title sponsor with dominant main stage presence"
    }
  ],
  "executives": [
    {
      "name": "Satya Nadella",
      "title": "CEO",
      "organization": "Microsoft",
      "confidence": 0.92,
      "industry_relevance": "very_high"
    }
  ],
  "competitive_intelligence": {
    "total_brands": 24,
    "brand_tiers": {"title": 1, "premium": 3, "gold": 5},
    "analysis_summary": "Microsoft dominates with title sponsorship..."
  }
}
```

### Research Compiler Output
```json
{
  "research_type": "ma_due_diligence",
  "target_entity": "TechCorp",
  "executive_summary": "Comprehensive analysis reveals strong growth...",
  "sections": [
    {
      "title": "Financial Performance",
      "summary": "Revenue growing 45% YoY with strong margins",
      "confidence": 0.87,
      "data_points_count": 15,
      "insights": ["Sustainable growth trajectory", "Strong unit economics"]
    }
  ],
  "key_findings": ["Market leader position", "$450M ARR"],
  "risk_factors": ["Regulatory scrutiny in EU", "Key person dependency"],
  "opportunities": ["International expansion", "AI integration"],
  "recommendations": ["Proceed with acquisition at 12-15x ARR multiple"],
  "data_quality_score": 0.84
}
```

## 🚀 Getting Started

1. **Import the agents**:
```python
from agent_forge.examples.visual_intelligence_agent import VisualIntelligenceAgent
from agent_forge.examples.research_compiler_agent import ResearchCompilerAgent
```

2. **Initialize with your use case**:
```python
visual_agent = VisualIntelligenceAgent(name="BrandMonitor")
research_agent = ResearchCompilerAgent(name="DDCompiler")
```

3. **Run analysis**:
```python
# Visual intelligence for events
brand_results = await visual_agent.run(image_urls, model, "technology")

# Research compilation for due diligence  
dd_report = await research_agent.compile_research(data, ResearchType.MA_DUE_DILIGENCE, "Target")
```

## 📈 Business Value

### Visual Intelligence Agent ROI
- **Trade Show Intelligence**: Save $50K+ per event in competitive analysis costs
- **Brand Monitoring**: 10x faster than manual analysis
- **Executive Tracking**: Identify business development opportunities in real-time

### Research Compiler Agent ROI
- **M&A Due Diligence**: Reduce DD time by 70%, save $200K+ per acquisition
- **Competitive Analysis**: Weekly competitor updates vs quarterly reports
- **Supplier Risk**: Prevent supply chain disruptions, save millions in downtime

## 🔐 Best Practices

1. **Data Quality**: Higher quality inputs = better insights
2. **Source Diversity**: Multiple sources increase confidence scores
3. **Regular Updates**: Schedule periodic analysis for continuous intelligence
4. **Human Review**: Use AI insights to augment, not replace, human judgment
5. **Compliance**: Ensure data collection complies with applicable laws

## 🤝 Support

For questions or custom enterprise agent development:
- GitHub Issues: [agent_forge/issues](https://github.com/agent_forge/issues)
- Documentation: [agent_forge/docs](https://github.com/agent_forge/docs)
- Enterprise Support: enterprise@agentforge.ai

---

*These agents demonstrate Agent Forge's capability to build production-ready, enterprise-grade automation. The same framework that powers Nuru AI's event intelligence now enables your business intelligence needs.*