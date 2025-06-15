#!/usr/bin/env python3
"""
Agent Forge Enhanced MCP Server

An enhanced version of the MCP server that includes auto-discovery of Agent Forge agents,
better error handling, and additional features for production use.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Install with: pip install fastmcp")
    exit(1)

# Import auto-discovery system
from mcp_auto_discovery import register_discovered_agents_with_mcp

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create enhanced MCP server
mcp = FastMCP("Agent Forge Enhanced")

# Core manually-defined tools (these are guaranteed to work)
@mcp.tool()
async def get_agent_forge_status() -> Dict[str, Any]:
    """
    Get comprehensive status information about the Agent Forge framework and MCP server.
    
    Returns:
        Dictionary containing framework status, available agents, and system information
    """
    try:
        # Check if Agent Forge core modules are available
        core_available = True
        try:
            from core.agents.base import AsyncContextAgent
        except ImportError:
            core_available = False
        
        # Check if example agents are available
        examples_available = True
        example_agents = []
        try:
            from examples import simple_navigation_agent
            example_agents.append("SimpleNavigationAgent")
        except ImportError:
            examples_available = False
        
        try:
            from examples import nmkr_auditor_agent
            example_agents.append("NMKRAuditorAgent")
        except ImportError:
            pass
        
        # Check blockchain integration status
        blockchain_status = {
            "nmkr_available": False,
            "masumi_available": False,
            "steel_browser_available": False
        }
        
        try:
            from core.blockchain.nmkr_integration import NMKRClient
            blockchain_status["nmkr_available"] = True
        except ImportError:
            pass
        
        try:
            from core.blockchain.masumi_integration import MasumiClient
            blockchain_status["masumi_available"] = True
        except ImportError:
            pass
        
        try:
            from core.shared.web.browsers.steel_browser_client import SteelBrowserClient
            blockchain_status["steel_browser_available"] = True
        except ImportError:
            pass
        
        # Auto-discovery status
        from mcp_auto_discovery import AgentDiscovery
        discovery = AgentDiscovery()
        discovered_agents = discovery.discover_agents()
        
        return {
            "success": True,
            "framework": "Agent Forge",
            "mcp_server": "Enhanced MCP Server",
            "version": "1.0.0",
            "status": {
                "core_available": core_available,
                "examples_available": examples_available,
                "total_discovered_agents": len(discovered_agents),
                "example_agents": example_agents,
                "discovered_agents": list(discovered_agents.keys())
            },
            "blockchain_integration": blockchain_status,
            "environment": {
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
                "log_level": os.getenv('LOG_LEVEL', 'INFO')
            },
            "capabilities": [
                "web_automation",
                "blockchain_proofs",
                "data_compilation",
                "text_extraction",
                "agent_validation",
                "auto_discovery"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get Agent Forge status: {e}")
        return {
            "success": False,
            "error": str(e),
            "framework": "Agent Forge",
            "mcp_server": "Enhanced MCP Server"
        }

@mcp.tool()
async def execute_agent_by_name(
    agent_name: str,
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Execute any discovered Agent Forge agent by name with custom parameters.
    
    Args:
        agent_name: Name of the agent to execute (use get_agent_forge_status to see available agents)
        parameters: Dictionary of parameters to pass to the agent
    
    Returns:
        Dictionary containing execution results
    """
    try:
        logger.info(f"Executing agent '{agent_name}' with parameters: {parameters}")
        
        # Get discovered agents
        from mcp_auto_discovery import AgentDiscovery
        discovery = AgentDiscovery()
        agents = discovery.discover_agents()
        
        if agent_name not in agents:
            available_agents = list(agents.keys())
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found",
                "available_agents": available_agents,
                "suggestion": f"Use one of: {', '.join(available_agents)}"
            }
        
        agent_class = agents[agent_name]
        params = parameters or {}
        
        # Create and execute agent
        agent_instance = agent_class(**params)
        
        async with agent_instance as agent:
            result = await agent.run()
        
        return {
            "success": True,
            "result": result,
            "agent": agent_name,
            "agent_class": agent_class.__name__,
            "parameters": params,
            "execution_method": "dynamic_discovery"
        }
        
    except Exception as e:
        logger.error(f"Failed to execute agent '{agent_name}': {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": agent_name,
            "parameters": parameters
        }

@mcp.tool()
async def test_agent_forge_installation() -> Dict[str, Any]:
    """
    Test the Agent Forge installation and report any issues.
    
    Returns:
        Dictionary containing test results and recommendations
    """
    test_results = {
        "overall_status": "unknown",
        "tests": {},
        "recommendations": []
    }
    
    try:
        # Test 1: Core imports
        try:
            from core.agents.base import AsyncContextAgent
            test_results["tests"]["core_import"] = {"status": "pass", "message": "Core Agent Forge modules imported successfully"}
        except ImportError as e:
            test_results["tests"]["core_import"] = {"status": "fail", "message": f"Core import failed: {str(e)}"}
            test_results["recommendations"].append("Ensure Agent Forge is properly installed and PYTHONPATH is set correctly")
        
        # Test 2: Example agents
        example_tests = {}
        example_agents = [
            ("simple_navigation_agent", "SimpleNavigationAgent"),
            ("nmkr_auditor_agent", "NMKRAuditorAgent"),
            ("data_compiler_agent", "DataCompilerAgent"),
            ("text_extraction_agent", "TextExtractionAgent"),
            ("validation_agent", "ValidationAgent")
        ]
        
        for module_name, class_name in example_agents:
            try:
                module = __import__(f"examples.{module_name}", fromlist=[class_name])
                agent_class = getattr(module, class_name)
                example_tests[class_name] = {"status": "pass", "message": f"{class_name} available"}
            except (ImportError, AttributeError) as e:
                example_tests[class_name] = {"status": "fail", "message": f"Failed to import {class_name}: {str(e)}"}
        
        test_results["tests"]["example_agents"] = example_tests
        
        # Test 3: Auto-discovery
        try:
            from mcp_auto_discovery import AgentDiscovery
            discovery = AgentDiscovery()
            discovered = discovery.discover_agents()
            test_results["tests"]["auto_discovery"] = {
                "status": "pass", 
                "message": f"Auto-discovery found {len(discovered)} agents",
                "discovered_agents": list(discovered.keys())
            }
        except Exception as e:
            test_results["tests"]["auto_discovery"] = {"status": "fail", "message": f"Auto-discovery failed: {str(e)}"}
        
        # Test 4: Dependencies
        dependency_tests = {}
        dependencies = [
            ("fastmcp", "FastMCP MCP server framework"),
            ("aiohttp", "Async HTTP client"),
            ("requests", "HTTP client library")
        ]
        
        for dep_name, description in dependencies:
            try:
                __import__(dep_name)
                dependency_tests[dep_name] = {"status": "pass", "message": f"{description} available"}
            except ImportError:
                dependency_tests[dep_name] = {"status": "fail", "message": f"{description} not available"}
                test_results["recommendations"].append(f"Install {dep_name}: pip install {dep_name}")
        
        test_results["tests"]["dependencies"] = dependency_tests
        
        # Determine overall status
        failed_tests = []
        for test_category, test_data in test_results["tests"].items():
            if isinstance(test_data, dict):
                if test_data.get("status") == "fail":
                    failed_tests.append(test_category)
                elif isinstance(test_data, dict) and any(subtest.get("status") == "fail" for subtest in test_data.values() if isinstance(subtest, dict)):
                    failed_tests.append(test_category)
        
        if not failed_tests:
            test_results["overall_status"] = "pass"
            test_results["message"] = "All tests passed! Agent Forge is properly configured for MCP."
        elif len(failed_tests) <= 2:
            test_results["overall_status"] = "partial"
            test_results["message"] = f"Some tests failed: {', '.join(failed_tests)}. Basic functionality should work."
        else:
            test_results["overall_status"] = "fail"
            test_results["message"] = "Multiple test failures detected. Agent Forge may not function properly."
            test_results["recommendations"].append("Check Agent Forge installation and Python environment setup")
        
        return {
            "success": True,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "test_results": test_results
        }

# Register auto-discovered agents
try:
    logger.info("Registering auto-discovered agents...")
    register_discovered_agents_with_mcp(mcp)
    logger.info("Auto-discovered agents registered successfully")
except Exception as e:
    logger.warning(f"Failed to register auto-discovered agents: {e}")
    logger.info("Continuing with manually defined tools only")

# Add documentation resources
@mcp.resource("agent-forge://help/{topic}")
async def get_help(topic: str) -> str:
    """Get help information for Agent Forge MCP integration."""
    help_topics = {
        "getting-started": """
# Getting Started with Agent Forge MCP

## Quick Test Commands:
1. "Claude, use get_agent_forge_status to show me what Agent Forge agents are available"
2. "Use test_agent_forge_installation to verify everything is working"
3. "Execute execute_agent_by_name with agent_name='simple_navigation' and parameters={'url': 'https://httpbin.org/html'}"

## Available Tools:
- get_agent_forge_status: Check system status and available agents
- execute_agent_by_name: Run any discovered agent dynamically
- test_agent_forge_installation: Verify installation and configuration
- [Auto-discovered tools based on your Agent Forge installation]

## Example Workflows:
- Web scraping: Use navigation agents to extract data from websites
- Blockchain proofs: Generate NMKR NFTs for task verification
- Data compilation: Aggregate information from multiple sources
- Content analysis: Extract and process text content intelligently
        """,
        "troubleshooting": """
# Troubleshooting Agent Forge MCP

## Common Issues:

### "Agent not found" errors:
1. Run get_agent_forge_status to see available agents
2. Check that Agent Forge is properly installed
3. Verify PYTHONPATH includes the Agent Forge directory

### Import errors:
1. Run test_agent_forge_installation for detailed diagnostics
2. Check that all dependencies are installed: pip install -r mcp_requirements.txt
3. Verify Python version is 3.8+ and virtual environment is activated

### Performance issues:
1. Check system resources and network connectivity
2. Verify Steel Browser API keys if using web automation
3. Monitor logs for timeout or rate limiting issues

### Blockchain operations failing:
1. Verify NMKR_API_KEY environment variable is set
2. Check Cardano network connectivity
3. Ensure sufficient ADA for transaction fees
        """,
        "examples": """
# Agent Forge MCP Examples

## Basic Web Navigation:
"Claude, use execute_agent_by_name to run 'simple_navigation' with parameters {'url': 'https://news.ycombinator.com', 'extraction_target': 'title'}"

## Multi-Source Data Compilation:
"Use execute_agent_by_name to run 'data_compiler' with parameters {'sources': ['https://site1.com', 'https://site2.com'], 'compilation_strategy': 'merge'}"

## Blockchain Proof Generation:
"Run 'nmkr_auditor' agent with parameters {'url': 'https://example.com', 'task_description': 'Website analysis for compliance check'}"

## Content Extraction:
"Execute 'text_extraction' agent with parameters {'url': 'https://blog.example.com/article', 'content_type': 'article', 'include_metadata': true}"

## Website Validation:
"Use 'validation' agent with parameters {'url': 'https://mysite.com', 'validation_rules': {'check_links': true, 'check_images': true}}"
        """
    }
    
    return help_topics.get(topic, f"Help topic '{topic}' not found. Available topics: {', '.join(help_topics.keys())}")

def main():
    """Main entry point for the enhanced MCP server."""
    try:
        logger.info("Starting Agent Forge Enhanced MCP Server...")
        logger.info("Core tools: get_agent_forge_status, execute_agent_by_name, test_agent_forge_installation")
        logger.info("Use get_agent_forge_status to see all available agents and capabilities")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start enhanced MCP server: {e}")
        raise

if __name__ == "__main__":
    main()