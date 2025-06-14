#!/usr/bin/env python3
"""
Agent Forge CLI - Command Line Interface for Agent Framework
A simple CLI for running and managing autonomous AI web agents.
"""

import argparse
import asyncio
import logging
import sys
from typing import Optional

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentForge:
    """Main Agent Forge framework class."""
    
    def __init__(self):
        self.agents = {}
        logger.info("Agent Forge initialized")
    
    def register_agent(self, name: str, agent_class):
        """Register an agent with the framework."""
        self.agents[name] = agent_class
        logger.info(f"Registered agent: {name}")
    
    def list_agents(self):
        """List all registered agents."""
        if not self.agents:
            print("No agents registered")
            return
        
        print("Available agents:")
        for name in self.agents.keys():
            print(f"  - {name}")
    
    async def run_agent(self, agent_name: str, *args, **kwargs):
        """Run a specific agent."""
        if agent_name not in self.agents:
            logger.error(f"Agent '{agent_name}' not found")
            return False
        
        try:
            agent_class = self.agents[agent_name]
            agent = agent_class()
            
            if hasattr(agent, 'run'):
                logger.info(f"Running agent: {agent_name}")
                result = await agent.run(*args, **kwargs)
                logger.info(f"Agent {agent_name} completed successfully")
                return result
            else:
                logger.error(f"Agent {agent_name} does not have a 'run' method")
                return False
                
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}")
            return False


def create_parser():
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Agent Forge - Framework for autonomous AI web agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py list                    # List available agents
  python cli.py run example_agent       # Run a specific agent
  python cli.py --version               # Show version
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Agent Forge 1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available agents')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific agent')
    run_parser.add_argument('agent_name', help='Name of the agent to run')
    run_parser.add_argument('--config', help='Configuration file for the agent')
    run_parser.add_argument('--output', help='Output file for results')
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize Agent Forge
    forge = AgentForge()
    
    # Handle commands
    if args.command == 'list':
        forge.list_agents()
    
    elif args.command == 'run':
        if not args.agent_name:
            parser.error("Agent name is required for 'run' command")
        
        success = await forge.run_agent(args.agent_name)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())