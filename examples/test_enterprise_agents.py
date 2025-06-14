"""
Test script for enterprise Visual Intelligence and Research Compiler agents
"""

import asyncio
import json
from datetime import datetime
from visual_intelligence_agent import VisualIntelligenceAgent, ResearchType as VisualResearchType
from research_compiler_agent import ResearchCompilerAgent, ResearchType, DataSourceType


async def test_visual_intelligence_agent():
    """Test the Visual Intelligence Agent with enterprise scenarios"""
    print("\n" + "="*80)
    print("🎯 TESTING VISUAL INTELLIGENCE AGENT")
    print("="*80)
    
    agent = VisualIntelligenceAgent()
    await agent.initialize()
    
    # Test 1: Brand Detection for Competitive Intelligence
    print("\n📊 Test 1: Enterprise Brand Detection")
    print("-" * 40)
    
    # Simulate image URLs (in production, these would be real URLs)
    test_image_urls = [
        "https://example.com/conference-sponsor-wall.jpg",
        "https://example.com/tech-summit-main-stage.jpg"
    ]
    
    # Test competitive intelligence analysis
    results = await agent.run_competitive_intelligence(
        image_urls=test_image_urls,
        gemini_model=None,  # Would be injected by MCP in production
        target_industry="technology"
    )
    
    print(f"Detected {results['competitive_intelligence']['total_brands']} brands")
    print(f"High confidence brands: {results['competitive_intelligence']['high_confidence_brands']}")
    print(f"Brand tier distribution: {results['competitive_intelligence']['brand_tiers']}")
    
    # Test 2: Executive Detection for Business Intelligence
    print("\n👔 Test 2: Executive Identification")
    print("-" * 40)
    
    exec_results = await agent.analyze_executives(
        image_urls=["https://example.com/keynote-speaker.jpg"],
        gemini_model=None,
        target_industry="technology"
    )
    
    print(f"Detected {len(exec_results)} executives")
    if exec_results:
        for exec_detection in exec_results[:2]:
            print(f"- {exec_detection.name} ({exec_detection.title}) at {exec_detection.organization}")
            print(f"  Confidence: {exec_detection.confidence:.2f} ({exec_detection.confidence_level.value})")
    
    # Test 3: MCP-Compatible Methods
    print("\n🔌 Test 3: MCP-Compatible Methods")
    print("-" * 40)
    
    # Test brand monitoring for specific competitors
    competitor_results = await agent.monitor_competitor_presence(
        image_urls=test_image_urls,
        competitors=["Microsoft", "Google", "Amazon", "Salesforce"]
    )
    
    print(f"Competitor monitoring results:")
    print(f"- Found {competitor_results['total_competitor_presence']} target competitors")
    print(f"- Analysis: {competitor_results['competitive_analysis']}")
    
    await agent.cleanup()
    print("\n✅ Visual Intelligence Agent tests complete!")


async def test_research_compiler_agent():
    """Test the Research Compiler Agent with enterprise scenarios"""
    print("\n" + "="*80)
    print("📚 TESTING RESEARCH COMPILER AGENT")
    print("="*80)
    
    agent = ResearchCompilerAgent()
    await agent.initialize()
    
    # Test 1: M&A Due Diligence Compilation
    print("\n💼 Test 1: M&A Due Diligence Research")
    print("-" * 40)
    
    # Simulate raw research data
    due_diligence_data = [
        {
            "key": "Founded",
            "value": "2015 in San Francisco",
            "source": {"url": "https://www.company.com/about", "type": "company"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Revenue",
            "value": "$450M ARR (2024)",
            "source": {"url": "https://www.sec.gov/edgar", "type": "financial"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Market Share",
            "value": "15% of enterprise SaaS market",
            "source": {"url": "https://analyst-report.com", "type": "analyst"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Patent Portfolio",
            "value": "47 granted patents in AI/ML",
            "source": {"url": "https://patents.google.com", "type": "patent"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Legal Status",
            "value": "No active litigation",
            "source": {"url": "https://www.sec.gov/litigation", "type": "legal"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Customer Base",
            "value": "2,500+ enterprise customers including Fortune 500",
            "source": {"url": "https://www.company.com/customers", "type": "company"},
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    dd_results = await agent.compile_research(
        raw_data=due_diligence_data,
        research_type=ResearchType.MA_DUE_DILIGENCE,
        target_entity="TechCorp Inc."
    )
    
    print(f"Executive Summary:")
    print(f"{dd_results.executive_summary}\n")
    print(f"Key Findings: {len(dd_results.key_findings)}")
    for finding in dd_results.key_findings[:3]:
        print(f"- {finding}")
    print(f"\nRisk Factors: {len(dd_results.risk_factors)}")
    print(f"Opportunities: {len(dd_results.opportunities)}")
    print(f"Data Quality Score: {dd_results.data_quality_score:.2f}")
    
    # Test 2: Competitive Analysis Compilation
    print("\n🎯 Test 2: Competitive Analysis Research")
    print("-" * 40)
    
    competitive_data = [
        {
            "key": "Pricing Model",
            "value": "Subscription-based, $99-999/month",
            "source": {"url": "https://competitor.com/pricing", "type": "company"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Product Features",
            "value": "AI-powered analytics, real-time dashboards, API access",
            "source": {"url": "https://g2.com/products/competitor", "type": "review"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Market Position",
            "value": "Leader in Gartner Magic Quadrant 2024",
            "source": {"url": "https://www.gartner.com/reports", "type": "analyst"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Recent News",
            "value": "Raised $200M Series D at $2B valuation",
            "source": {"url": "https://techcrunch.com/article", "type": "news"},
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    comp_results = await agent.run(
        raw_data=competitive_data,
        research_type="competitive_analysis",
        target_entity="CompetitorX"
    )
    
    print(f"Competitive Analysis Summary:")
    print(f"Sections compiled: {len(comp_results['sections'])}")
    print(f"Total sources: {comp_results['total_sources']}")
    print(f"Compilation time: {comp_results['compilation_time']:.2f}s")
    
    # Test 3: Supplier Risk Assessment
    print("\n⚠️ Test 3: Supplier Risk Assessment")
    print("-" * 40)
    
    supplier_data = [
        {
            "key": "Financial Health",
            "value": "D&B rating: 3A1, Low risk",
            "source": {"url": "https://dnb.com/supplier", "type": "financial"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Compliance Status",
            "value": "ISO 9001, SOC 2 Type II certified",
            "source": {"url": "https://supplier.com/compliance", "type": "regulatory"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "key": "Delivery Performance",
            "value": "98.5% on-time delivery rate",
            "source": {"url": "internal-metrics", "type": "company"},
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Test MCP-compatible method
    risk_assessment = await agent.assess_supplier_risk(
        supplier_name="Global Supplies Inc.",
        risk_data=supplier_data
    )
    
    print(f"Supplier Risk Assessment:")
    print(f"- Supplier: {risk_assessment['supplier']}")
    print(f"- Risk Score: {risk_assessment['risk_score']:.2f}")
    print(f"- Risk Level: {risk_assessment['risk_level']}")
    print(f"- Recommendation: {risk_assessment['recommendation']}")
    
    await agent.cleanup()
    print("\n✅ Research Compiler Agent tests complete!")


async def main():
    """Run all enterprise agent tests"""
    print("\n🚀 AGENT FORGE ENTERPRISE AGENTS TEST SUITE")
    print("Testing Visual Intelligence and Research Compiler Agents")
    
    # Run tests
    await test_visual_intelligence_agent()
    await test_research_compiler_agent()
    
    print("\n" + "="*80)
    print("🎉 ALL TESTS COMPLETE!")
    print("="*80)
    print("\nThese enterprise agents are now ready for:")
    print("- M&A Due Diligence automation")
    print("- Competitive Intelligence gathering")
    print("- Market Research compilation")
    print("- Supplier Risk assessments")
    print("- Executive & Brand monitoring")
    print("\nMCP Integration enables access via:")
    print("- ChatGPT")
    print("- Claude Desktop")
    print("- VS Code / Cursor / Zed")
    print("- Any MCP-compatible platform")


if __name__ == "__main__":
    asyncio.run(main())