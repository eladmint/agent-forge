#!/usr/bin/env python3
"""
Agent Forge Community MCP Server

A FastMCP-based server that exposes Agent Forge community tier agents as MCP tools
for Claude Desktop and other MCP clients.

This server includes only open source community agents.
Premium agents are available in Professional and Enterprise tiers.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Install with: pip install fastmcp")
    exit(1)

# Import Agent Forge community tier components only
from examples.simple_navigation_agent import SimpleNavigationAgent
from examples.text_extraction_agent import EnhancedTextExtractionAgent
from examples.validation_agent import EnhancedValidationAgent
from examples.page_scraper_agent import PageScraperAgent
from examples.documentation_manager_agent import DocumentationManagerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("Agent Forge Community")

@mcp.tool()
async def navigate_website(
    url: str,
    extraction_target: str = "title",
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Navigate to a website and extract content using Agent Forge Steel Browser integration.
    
    Args:
        url: The URL to navigate to
        extraction_target: What to extract ('title', 'content', 'metadata', 'links')
        timeout: Timeout in seconds (default: 30)
    
    Returns:
        Dictionary containing extracted data and execution metadata
    """
    try:
        logger.info(f"Navigating to website: {url}")
        
        async with SimpleNavigationAgent(
            url=url,
            extraction_target=extraction_target,
            timeout=timeout
        ) as agent:
            navigation_data = await agent.run()
            
        logger.info(f"Website navigation completed successfully")
        return {
            "success": True,
            "navigation_data": navigation_data,
            "agent": "SimpleNavigationAgent",
            "url": url
        }
        
    except Exception as e:
        logger.error(f"Website navigation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "SimpleNavigationAgent",
            "url": url
        }

@mcp.tool()
async def extract_text_content(
    url: str,
    content_type: str = "all",
    clean_text: bool = True,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Extract and process text content from a website using advanced text extraction.
    
    Args:
        url: The URL to extract text from
        content_type: Type of content to extract ('all', 'paragraphs', 'headings', 'links')
        clean_text: Whether to clean and normalize the extracted text
        timeout: Timeout in seconds (default: 30)
    
    Returns:
        Dictionary containing extracted text and processing metadata
    """
    try:
        logger.info(f"Extracting text content from: {url}")
        
        async with EnhancedTextExtractionAgent(
            url=url,
            content_type=content_type,
            clean_text=clean_text,
            timeout=timeout
        ) as agent:
            extracted_text = await agent.run()
            
        logger.info(f"Text extraction completed successfully")
        return {
            "success": True,
            "extracted_text": extracted_text,
            "agent": "EnhancedTextExtractionAgent",
            "url": url,
            "content_type": content_type
        }
        
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "EnhancedTextExtractionAgent",
            "url": url
        }

@mcp.tool()
async def validate_page_quality(
    url: str,
    validation_criteria: List[str] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Validate page quality and data integrity using comprehensive validation.
    
    Args:
        url: The URL to validate
        validation_criteria: List of validation criteria to apply
        timeout: Timeout in seconds (default: 30)
    
    Returns:
        Dictionary containing validation results and quality metrics
    """
    try:
        logger.info(f"Validating page quality for: {url}")
        
        if validation_criteria is None:
            validation_criteria = ["accessibility", "performance", "content"]
        
        async with EnhancedValidationAgent(
            url=url,
            validation_criteria=validation_criteria,
            timeout=timeout
        ) as agent:
            validation_results = await agent.run()
            
        logger.info(f"Page validation completed successfully")
        return {
            "success": True,
            "validation_results": validation_results,
            "agent": "EnhancedValidationAgent",
            "url": url,
            "validation_criteria": validation_criteria
        }
        
    except Exception as e:
        logger.error(f"Page validation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "EnhancedValidationAgent",
            "url": url
        }

@mcp.tool()
async def scrape_page_content(
    url: str,
    content_selectors: List[str] = None,
    wait_for: str = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Scrape page content using advanced web scraping with Playwright browser automation.
    
    Args:
        url: The URL to scrape
        content_selectors: CSS selectors for specific content to extract
        wait_for: CSS selector or text to wait for before extraction
        timeout: Timeout in seconds (default: 30)
    
    Returns:
        Dictionary containing scraped content and extraction metadata
    """
    try:
        logger.info(f"Scraping page content from: {url}")
        
        async with PageScraperAgent(
            url=url,
            content_selectors=content_selectors,
            wait_for=wait_for,
            timeout=timeout
        ) as agent:
            scraped_content = await agent.run()
            
        logger.info(f"Page scraping completed successfully")
        return {
            "success": True,
            "scraped_content": scraped_content,
            "agent": "PageScraperAgent",
            "url": url,
            "content_selectors": content_selectors
        }
        
    except Exception as e:
        logger.error(f"Page scraping failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "PageScraperAgent",
            "url": url
        }

@mcp.tool()
async def manage_documentation(
    action: str,
    target_path: str = None,
    content: str = None,
    format: str = "markdown"
) -> Dict[str, Any]:
    """
    Manage and update documentation using automated documentation workflows.
    
    Args:
        action: Documentation action to perform ('generate', 'update', 'validate')
        target_path: Path to documentation file or directory
        content: Content to add or update (for 'update' action)
        format: Documentation format ('markdown', 'html', 'rst')
    
    Returns:
        Dictionary containing documentation management results
    """
    try:
        logger.info(f"Managing documentation: {action}")
        
        async with DocumentationManagerAgent(
            action=action,
            target_path=target_path,
            content=content,
            format=format
        ) as agent:
            doc_results = await agent.run()
            
        logger.info(f"Documentation management completed successfully")
        return {
            "success": True,
            "documentation_results": doc_results,
            "agent": "DocumentationManagerAgent",
            "action": action,
            "target_path": target_path
        }
        
    except Exception as e:
        logger.error(f"Documentation management failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "DocumentationManagerAgent",
            "action": action
        }

# Premium features available in Professional and Enterprise tiers
@mcp.tool()
async def get_premium_features() -> Dict[str, Any]:
    """
    Get information about premium features available in Professional and Enterprise tiers.
    
    Returns:
        Dictionary containing information about premium tier capabilities
    """
    return {
        "message": "Premium features available in paid tiers",
        "professional_tier": {
            "price": "$99/month",
            "features": [
                "Advanced data compilation agents",
                "Multi-agent coordination systems", 
                "Enhanced web automation workflows",
                "Premium support and documentation"
            ]
        },
        "enterprise_tier": {
            "price": "$999/month", 
            "features": [
                "Visual Intelligence Agent - Brand monitoring and competitive intelligence",
                "Research Compiler Agent - M&A due diligence and market research",
                "NMKR Blockchain integration - Proof-of-execution capabilities",
                "Enterprise SSO, audit trails, compliance features",
                "SLA-backed support and custom development"
            ]
        },
        "learn_more": "https://agent-forge.ai/pricing"
    }

# Server diagnostics and health check
@mcp.tool()
async def server_health_check() -> Dict[str, Any]:
    """
    Check Agent Forge Community MCP Server health and status.
    
    Returns:
        Dictionary containing server health information
    """
    return {
        "status": "healthy",
        "server": "Agent Forge Community MCP Server",
        "version": "1.0.0",
        "available_agents": [
            "SimpleNavigationAgent",
            "EnhancedTextExtractionAgent", 
            "EnhancedValidationAgent",
            "PageScraperAgent",
            "DocumentationManagerAgent"
        ],
        "total_tools": 7,
        "tier": "Community (Open Source)",
        "upgrade_info": "Premium agents available in paid tiers"
    }

if __name__ == "__main__":
    print("🚀 Starting Agent Forge Community MCP Server...")
    print("📋 Available Community Agents:")
    print("   • Simple Navigation Agent - Basic web navigation")
    print("   • Text Extraction Agent - Advanced text processing")
    print("   • Validation Agent - Data quality and validation") 
    print("   • Page Scraper Agent - Web scraping with Playwright")
    print("   • Documentation Manager Agent - Automated documentation")
    print()
    print("💰 Premium agents available in Professional ($99/month) and Enterprise ($999/month) tiers")
    print("🔗 Learn more: https://agent-forge.ai/pricing")
    print()
    
    # Run the server
    mcp.run()