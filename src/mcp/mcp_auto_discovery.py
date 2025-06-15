#!/usr/bin/env python3
"""
Agent Forge MCP Auto-Discovery System

Automatically discovers Agent Forge agents and creates MCP tools for them.
This module can be imported to extend the main MCP server with dynamic agent discovery.
"""

import inspect
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Any, List, Type, Callable
import logging

from core.agents.base import AsyncContextAgent

logger = logging.getLogger(__name__)

class AgentDiscovery:
    """Auto-discovery system for Agent Forge agents."""
    
    def __init__(self, search_paths: List[str] = None):
        """
        Initialize the agent discovery system.
        
        Args:
            search_paths: List of paths to search for agents. Defaults to examples/ and custom agent directories.
        """
        self.search_paths = search_paths or [
            "examples",
            "custom_agents",  # For user-defined agents
        ]
        self.discovered_agents: Dict[str, Type[AsyncContextAgent]] = {}
        
    def discover_agents(self) -> Dict[str, Type[AsyncContextAgent]]:
        """
        Discover all available Agent Forge agents.
        
        Returns:
            Dictionary mapping agent names to agent classes
        """
        logger.info("Starting agent discovery...")
        
        for search_path in self.search_paths:
            try:
                self._discover_agents_in_path(search_path)
            except Exception as e:
                logger.warning(f"Failed to discover agents in {search_path}: {e}")
                
        logger.info(f"Discovered {len(self.discovered_agents)} agents: {list(self.discovered_agents.keys())}")
        return self.discovered_agents
    
    def _discover_agents_in_path(self, search_path: str) -> None:
        """Discover agents in a specific path."""
        try:
            # Import the module/package
            module = importlib.import_module(search_path)
            
            # If it's a package, iterate through submodules
            if hasattr(module, '__path__'):
                for importer, modname, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                    try:
                        submodule = importlib.import_module(modname)
                        self._extract_agents_from_module(submodule)
                    except Exception as e:
                        logger.debug(f"Failed to import {modname}: {e}")
            else:
                self._extract_agents_from_module(module)
                
        except ImportError as e:
            logger.debug(f"Could not import {search_path}: {e}")
    
    def _extract_agents_from_module(self, module) -> None:
        """Extract agent classes from a module."""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, AsyncContextAgent) and 
                obj is not AsyncContextAgent and
                not name.startswith('_')):
                
                agent_name = self._normalize_agent_name(name)
                self.discovered_agents[agent_name] = obj
                logger.debug(f"Discovered agent: {agent_name} ({name})")
    
    def _normalize_agent_name(self, class_name: str) -> str:
        """Normalize agent class name to a friendly name."""
        # Remove 'Agent' suffix and convert to snake_case
        name = class_name
        if name.endswith('Agent'):
            name = name[:-5]
        
        # Convert CamelCase to snake_case
        import re
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return name

class MCPToolGenerator:
    """Generate MCP tools from discovered agents."""
    
    def __init__(self):
        self.discovery = AgentDiscovery()
    
    def generate_tools_for_agents(self) -> List[Callable]:
        """
        Generate MCP tool functions for all discovered agents.
        
        Returns:
            List of MCP tool functions that can be registered with FastMCP
        """
        agents = self.discovery.discover_agents()
        tools = []
        
        for agent_name, agent_class in agents.items():
            tool_func = self._create_tool_function(agent_name, agent_class)
            tools.append(tool_func)
            
        return tools
    
    def _create_tool_function(self, agent_name: str, agent_class: Type[AsyncContextAgent]) -> Callable:
        """Create an MCP tool function for a specific agent."""
        
        # Extract agent metadata
        agent_doc = agent_class.__doc__ or f"Execute {agent_name} agent"
        agent_signature = self._extract_agent_signature(agent_class)
        
        async def agent_tool(**kwargs) -> Dict[str, Any]:
            """Dynamically generated agent tool function."""
            try:
                logger.info(f"Executing {agent_name} with params: {kwargs}")
                
                # Create agent instance with provided parameters
                agent_instance = agent_class(**kwargs)
                
                # Execute agent
                async with agent_instance as agent:
                    result = await agent.run()
                
                return {
                    "success": True,
                    "result": result,
                    "agent": agent_name,
                    "agent_class": agent_class.__name__,
                    "parameters": kwargs
                }
                
            except Exception as e:
                logger.error(f"Agent {agent_name} execution failed: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "agent": agent_name,
                    "agent_class": agent_class.__name__,
                    "parameters": kwargs
                }
        
        # Set function metadata for MCP
        agent_tool.__name__ = f"run_{agent_name}"
        agent_tool.__doc__ = agent_doc
        agent_tool.__annotations__ = agent_signature
        
        return agent_tool
    
    def _extract_agent_signature(self, agent_class: Type[AsyncContextAgent]) -> Dict[str, Any]:
        """Extract the function signature for an agent's __init__ method."""
        try:
            init_signature = inspect.signature(agent_class.__init__)
            annotations = {}
            
            for param_name, param in init_signature.parameters.items():
                if param_name in ['self', 'args', 'kwargs']:
                    continue
                    
                # Extract type annotation
                annotation = param.annotation if param.annotation != inspect.Parameter.empty else str
                
                # Extract default value
                if param.default != inspect.Parameter.empty:
                    annotation = type(param.default)
                
                annotations[param_name] = annotation
            
            # Add return type
            annotations['return'] = Dict[str, Any]
            
            return annotations
            
        except Exception as e:
            logger.debug(f"Could not extract signature for {agent_class.__name__}: {e}")
            return {'return': Dict[str, Any]}

def register_discovered_agents_with_mcp(mcp_server):
    """
    Register all discovered agents with an existing FastMCP server.
    
    Args:
        mcp_server: FastMCP server instance to register tools with
    """
    generator = MCPToolGenerator()
    tools = generator.generate_tools_for_agents()
    
    for tool_func in tools:
        # Register the tool with the MCP server
        mcp_server.tool()(tool_func)
        logger.info(f"Registered MCP tool: {tool_func.__name__}")
    
    logger.info(f"Registered {len(tools)} auto-discovered agent tools")

# Example usage for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test agent discovery
    discovery = AgentDiscovery()
    agents = discovery.discover_agents()
    
    print(f"\nDiscovered {len(agents)} agents:")
    for name, agent_class in agents.items():
        print(f"  - {name}: {agent_class.__name__}")
        print(f"    Doc: {agent_class.__doc__}")
        
        # Show agent signature
        generator = MCPToolGenerator()
        signature = generator._extract_agent_signature(agent_class)
        print(f"    Signature: {signature}")
        print()
    
    # Test tool generation
    generator = MCPToolGenerator()
    tools = generator.generate_tools_for_agents()
    
    print(f"\nGenerated {len(tools)} MCP tools:")
    for tool in tools:
        print(f"  - {tool.__name__}: {tool.__doc__}")