#!/usr/bin/env python3
"""
Agent Forge MCP Server

A FastMCP-based server that exposes Agent Forge agents as MCP tools
for Claude Desktop and other MCP clients.
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

# Import Agent Forge components
from examples.simple_navigation_agent import SimpleNavigationAgent
from examples.nmkr_auditor_agent import NMKRAuditorAgent
from examples.data_compiler_agent import DataCompilerAgent
from examples.text_extraction_agent import EnhancedTextExtractionAgent
from examples.validation_agent import EnhancedValidationAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("Agent Forge")

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
        logger.info(f"Navigating to {url} with target: {extraction_target}")
        
        async with SimpleNavigationAgent(
            url=url,
            extraction_target=extraction_target
        ) as agent:
            result = await agent.run()
            
        logger.info(f"Navigation completed successfully for {url}")
        return {
            "success": True,
            "data": result,
            "agent": "SimpleNavigationAgent",
            "url": url,
            "extraction_target": extraction_target
        }
        
    except Exception as e:
        logger.error(f"Navigation failed for {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "SimpleNavigationAgent",
            "url": url
        }

@mcp.tool()
async def generate_blockchain_proof(
    url: str,
    task_description: str,
    nmkr_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate NMKR Proof-of-Execution NFT for a web automation task.
    
    Args:
        url: The target URL for the automation task
        task_description: Description of the task being performed
        nmkr_api_key: NMKR API key (optional, uses environment variable if not provided)
    
    Returns:
        Dictionary containing blockchain proof data and verification information
    """
    try:
        logger.info(f"Generating blockchain proof for task: {task_description}")
        
        config = {}
        if nmkr_api_key:
            config['nmkr_api_key'] = nmkr_api_key
            
        async with NMKRAuditorAgent(
            url=url,
            task_description=task_description,
            config=config
        ) as agent:
            proof_package = await agent.run()
            
        logger.info(f"Blockchain proof generated successfully")
        return {
            "success": True,
            "proof_package": proof_package,
            "agent": "NMKRAuditorAgent",
            "url": url,
            "task_description": task_description
        }
        
    except Exception as e:
        logger.error(f"Blockchain proof generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "NMKRAuditorAgent",
            "url": url,
            "task_description": task_description
        }

@mcp.tool()
async def compile_data_from_sources(
    sources: List[str],
    compilation_strategy: str = "merge",
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Compile data from multiple web sources using Agent Forge data compilation.
    
    Args:
        sources: List of URLs to collect data from
        compilation_strategy: How to combine data ('merge', 'aggregate', 'compare')
        output_format: Format for compiled data ('json', 'csv', 'markdown')
    
    Returns:
        Dictionary containing compiled data and processing metadata
    """
    try:
        logger.info(f"Compiling data from {len(sources)} sources")
        
        async with DataCompilerAgent(
            sources=sources,
            compilation_strategy=compilation_strategy,
            output_format=output_format
        ) as agent:
            compiled_data = await agent.run()
            
        logger.info(f"Data compilation completed successfully")
        return {
            "success": True,
            "compiled_data": compiled_data,
            "agent": "DataCompilerAgent",
            "sources": sources,
            "compilation_strategy": compilation_strategy,
            "output_format": output_format
        }
        
    except Exception as e:
        logger.error(f"Data compilation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "DataCompilerAgent",
            "sources": sources
        }

@mcp.tool()
async def extract_text_content(
    url: str,
    content_type: str = "article",
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Extract and process text content from web pages using intelligent parsing.
    
    Args:
        url: The URL to extract content from
        content_type: Type of content expected ('article', 'blog', 'news', 'documentation')
        include_metadata: Whether to include metadata like author, date, etc.
    
    Returns:
        Dictionary containing extracted text and metadata
    """
    try:
        logger.info(f"Extracting text content from {url}")
        
        async with EnhancedTextExtractionAgent(
            url=url,
            content_type=content_type,
            include_metadata=include_metadata
        ) as agent:
            extracted_content = await agent.run()
            
        logger.info(f"Text extraction completed successfully")
        return {
            "success": True,
            "content": extracted_content,
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
async def validate_website_data(
    url: str,
    validation_rules: Dict[str, Any],
    check_accessibility: bool = True
) -> Dict[str, Any]:
    """
    Validate website data, structure, and accessibility using Agent Forge validation.
    
    Args:
        url: The URL to validate
        validation_rules: Dictionary of validation rules to apply
        check_accessibility: Whether to perform accessibility checks
    
    Returns:
        Dictionary containing validation results and recommendations
    """
    try:
        logger.info(f"Validating website data for {url}")
        
        async with EnhancedValidationAgent(
            url=url,
            validation_rules=validation_rules,
            check_accessibility=check_accessibility
        ) as agent:
            validation_results = await agent.run()
            
        logger.info(f"Website validation completed successfully")
        return {
            "success": True,
            "validation_results": validation_results,
            "agent": "EnhancedValidationAgent",
            "url": url,
            "rules_applied": validation_rules
        }
        
    except Exception as e:
        logger.error(f"Website validation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "EnhancedValidationAgent",
            "url": url
        }

@mcp.tool()
async def get_agent_info() -> Dict[str, Any]:
    """
    Get information about available Agent Forge agents and their capabilities.
    
    Returns:
        Dictionary containing information about all available agents
    """
    agents_info = {
        "SimpleNavigationAgent": {
            "description": "Navigate websites and extract content with Steel Browser integration",
            "capabilities": ["web_navigation", "content_extraction", "anti_detection"],
            "supported_targets": ["title", "content", "metadata", "links"]
        },
        "NMKRAuditorAgent": {
            "description": "Generate blockchain proofs of execution with NMKR NFT integration",
            "capabilities": ["blockchain_proof", "nft_minting", "audit_trail", "cardano_integration"],
            "supported_networks": ["cardano"]
        },
        "DataCompilerAgent": {
            "description": "Compile and aggregate data from multiple web sources",
            "capabilities": ["multi_source_data", "data_aggregation", "format_conversion"],
            "supported_formats": ["json", "csv", "markdown"]
        },
        "EnhancedTextExtractionAgent": {
            "description": "Intelligent text extraction and content processing",
            "capabilities": ["content_parsing", "metadata_extraction", "text_processing"],
            "supported_types": ["article", "blog", "news", "documentation"]
        },
        "EnhancedValidationAgent": {
            "description": "Website validation, testing, and accessibility checking",
            "capabilities": ["data_validation", "accessibility_testing", "structure_analysis"],
            "validation_types": ["content", "structure", "accessibility", "performance"]
        }
    }
    
    return {
        "success": True,
        "framework": "Agent Forge",
        "version": "1.0.0",
        "total_agents": len(agents_info),
        "agents": agents_info,
        "features": {
            "blockchain_integration": True,
            "steel_browser": True,
            "async_architecture": True,
            "production_ready": True,
            "testing_framework": "80+ tests"
        }
    }

# Add a resource for Agent Forge documentation
@mcp.resource("agent-forge://docs/{topic}")
async def get_documentation(topic: str) -> str:
    """Get Agent Forge documentation for specific topics."""
    docs = {
        "getting-started": """
# Agent Forge - Getting Started

Agent Forge is a production-ready framework for building autonomous AI web agents with blockchain integration.

## Key Features:
- AsyncContextAgent architecture with enterprise-grade reliability
- Steel Browser integration for robust web automation
- NMKR Proof-of-Execution NFT generation
- Masumi Network AI Agent Economy participation
- 80+ comprehensive test suite

## Quick Start:
1. Install: pip install agent-forge
2. Import agents: from agent_forge.examples import SimpleNavigationAgent
3. Use async context: async with SimpleNavigationAgent(url="...") as agent:
4. Run agent: result = await agent.run()
        """,
        "blockchain": """
# Blockchain Integration

Agent Forge includes native blockchain integration for verifiable AI execution:

## NMKR Proof-of-Execution:
- Automatic NFT minting with CIP-25 metadata
- Cryptographic proof generation
- IPFS storage for audit logs
- Cardano blockchain integration

## Masumi Network:
- AI Agent Economy participation
- Payment verification and escrow
- Revenue tracking and distribution
- Smart contract automation
        """,
        "architecture": """
# Agent Forge Architecture

## AsyncContextAgent Foundation:
- Production-grade async base class
- Context manager support
- Enterprise error handling
- Advanced configuration management

## Core Components:
- CLI interface with agent discovery
- Steel Browser integration
- Blockchain services (NMKR, Masumi)
- Shared utilities and testing framework
        """
    }
    
    return docs.get(topic, f"Documentation for '{topic}' not found. Available topics: {', '.join(docs.keys())}")

def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Agent Forge MCP Server...")
        logger.info("Available tools: navigate_website, generate_blockchain_proof, compile_data_from_sources, extract_text_content, validate_website_data, get_agent_info")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise

if __name__ == "__main__":
    main()