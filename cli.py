#!/usr/bin/env python3
"""
Agent Forge CLI

Command-line interface for managing and running Agent Forge agents.
"""

import argparse
import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Type, Any
import importlib
import inspect

# Add the current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import BaseAgent for type checking
from core.agents.base import BaseAgent


class AgentForge:
    """Main Agent Forge framework class for CLI operations."""
    
    def __init__(self):
        self.agents: Dict[str, Type[BaseAgent]] = {}
        self.logger = logging.getLogger("agent_forge")
        self._discover_agents()
    
    def _discover_agents(self):
        """Automatically discover and register agents from examples directory."""
        examples_dir = Path(__file__).parent / "examples"
        
        if not examples_dir.exists():
            self.logger.warning("Examples directory not found")
            return
        
        # Scan for Python files in examples directory
        for py_file in examples_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                self._load_agent_from_file(py_file)
            except Exception as e:
                self.logger.debug(f"Could not load agent from {py_file}: {e}")
    
    def _load_agent_from_file(self, py_file: Path):
        """Load an agent class from a Python file."""
        module_name = py_file.stem
        
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if spec is None or spec.loader is None:
            return
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find agent classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, BaseAgent) and 
                obj != BaseAgent and 
                obj.__module__ == module_name):
                
                # Create a CLI-friendly agent name
                agent_name = self._class_name_to_cli_name(name)
                self.agents[agent_name] = obj
                self.logger.debug(f"Registered agent: {agent_name} -> {name}")
    
    def _class_name_to_cli_name(self, class_name: str) -> str:
        """Convert CamelCase class name to CLI-friendly name."""
        # Remove 'Agent' suffix if present
        if class_name.endswith('Agent'):
            class_name = class_name[:-5]
        
        # Convert CamelCase to snake_case
        import re
        cli_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()
        return cli_name
    
    def list_agents(self):
        """List all available agents."""
        if not self.agents:
            print("No agents found.")
            return
        
        print("Available agents:")
        for agent_name, agent_class in sorted(self.agents.items()):
            doc = agent_class.__doc__ or "No description available"
            # Get first line of docstring
            description = doc.split('\n')[0].strip()
            print(f"  {agent_name:<20} - {description}")
    
    async def run_agent(self, agent_name: str, **kwargs) -> Any:
        """Run a specific agent with given parameters."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Use 'list' to see available agents.")
        
        agent_class = self.agents[agent_name]
        
        # Create agent instance with provided kwargs
        try:
            agent = agent_class(**kwargs)
        except Exception as e:
            raise ValueError(f"Failed to create agent '{agent_name}': {e}")
        
        try:
            # Initialize agent
            self.logger.info(f"Initializing agent: {agent_name}")
            success = await agent.initialize()
            if not success:
                raise RuntimeError(f"Agent '{agent_name}' initialization failed")
            
            # Run agent
            self.logger.info(f"Running agent: {agent_name}")
            result = await agent.run()
            
            return result
            
        finally:
            # Always cleanup
            try:
                await agent.cleanup()
            except Exception as e:
                self.logger.warning(f"Cleanup failed for agent '{agent_name}': {e}")


def setup_logging(verbose: bool = False):
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Agent Forge - Framework for autonomous AI web agents",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='Agent Forge 1.0.0')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available agents')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific agent')
    run_parser.add_argument('agent_name', help='Name of the agent to run')
    run_parser.add_argument('--url', help='URL for navigation agents')
    run_parser.add_argument('--task', help='Task description for the agent')
    run_parser.add_argument('--config', help='Path to configuration file')
    run_parser.add_argument('--dry-run', action='store_true', 
                           help='Show what would be done without executing')
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger("agent_forge.cli")
    
    # Create AgentForge instance
    forge = AgentForge()
    
    try:
        if args.command == 'list':
            forge.list_agents()
            
        elif args.command == 'run':
            # Prepare kwargs for agent creation
            agent_kwargs = {}
            
            # Add common parameters
            if args.url:
                agent_kwargs['url'] = args.url
            if args.task:
                agent_kwargs['task_description'] = args.task
            if args.config:
                agent_kwargs['config'] = args.config
            
            if args.dry_run:
                print(f"Would run agent '{args.agent_name}' with parameters: {agent_kwargs}")
                return
            
            # Run the agent
            try:
                result = await forge.run_agent(args.agent_name, **agent_kwargs)
                logger.info(f"Agent completed successfully")
                if args.verbose and result:
                    print(f"Agent result: {result}")
                    
            except Exception as e:
                logger.error(f"Agent execution failed: {e}")
                sys.exit(1)
                
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"CLI error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Import required for module loading
    import importlib.util
    
    # Run the CLI
    asyncio.run(main())