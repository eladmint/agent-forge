"""
Base Agent Class for Agent Forge Framework

This module provides the base class that all agents in the Agent Forge framework
should inherit from. It defines the standard interface and common functionality
for autonomous AI web agents.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from core.shared.config.browser_config import STEEL_BROWSER_API_URL
from core.shared.web.browsers import SteelBrowserClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all Agent Forge agents.
    
    This abstract base class defines the standard interface that all agents
    must implement. It provides common functionality and ensures consistent
    behavior across all agents in the framework.
    """
    
    def __init__(self, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Optional name for the agent. If not provided, uses class name.
            config: Optional configuration dictionary for the agent.
        """
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self.is_initialized = False
        self.logger = logging.getLogger(f"agent_forge.{self.name}")
        
        self.logger.info(f"Initializing agent: {self.name}")
        self.browser_client = None         

    async def initialize(self) -> bool:
        """
        Initialize the agent.
        
        This method should be called before running the agent. It performs
        any necessary setup operations such as loading configurations,
        establishing connections, or preparing resources.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        self.logger.info("Initializing functional browser client...") 
        try:
            self.browser_client = SteelBrowserClient(api_url=STEEL_BROWSER_API_URL)
            self.logger.info("Functional browser client initialized successfully.")
            self.logger.info(f"Initializing agent: {self.name}")
            await self._initialize()
            self.is_initialized = True
            self.logger.info(f"Agent {self.name} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize functional browser client: {e}") 
            self.browser_client = None
            self.logger.error(f"Failed to initialize agent {self.name}: {e}")
            return False
    
    async def cleanup(self) -> None:
        """
        Clean up agent resources.
        
        This method should be called when the agent is no longer needed.
        It performs cleanup operations such as closing connections,
        releasing resources, or saving state.
        """
        try:
            self.logger.info(f"Cleaning up agent: {self.name}")
            await self._cleanup()
            self.is_initialized = False
            self.logger.info(f"Agent {self.name} cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup of agent {self.name}: {e}")
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        Execute the main agent logic.
        
        This is the primary method that defines what the agent does.
        All concrete agent implementations must override this method.
        
        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments
            
        Returns:
            Any: The result of the agent's execution
        """
        pass
    
    async def _initialize(self) -> None:
        """
        Perform agent-specific initialization.
        
        This method can be overridden by subclasses to implement
        custom initialization logic. The default implementation
        does nothing.
        """
        pass
    
    async def _cleanup(self) -> None:
        """
        Perform agent-specific cleanup.
        
        This method can be overridden by subclasses to implement
        custom cleanup logic. The default implementation does nothing.
        """
        pass
    
    def is_ready(self) -> bool:
        """
        Check if the agent is ready to run.
        
        Returns:
            bool: True if the agent is initialized and ready, False otherwise.
        """
        return self.is_initialized
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict[str, Any]: Status information including name, initialization state, etc.
        """
        return {
            'name': self.name,
            'initialized': self.is_initialized,
            'ready': self.is_ready(),
            'config': self.config
        }
    
    def __str__(self) -> str:
        """String representation of the agent."""
        status = "ready" if self.is_ready() else "not ready"
        return f"{self.name} ({status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"BaseAgent(name='{self.name}', initialized={self.is_initialized})"


class AsyncContextAgent(BaseAgent):
    """
    Base agent class with async context manager support.
    
    This class extends BaseAgent to provide automatic initialization
    and cleanup when used as an async context manager.
    """
    
    async def __aenter__(self):
        """Enter the async context manager."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        await self.cleanup()
        return False  # Don't suppress exceptions


# Example usage and testing functions
async def test_base_agent():
    """Test function demonstrating BaseAgent usage."""
    
    class TestAgent(BaseAgent):
        """Simple test agent implementation."""
        
        async def run(self, message: str = "Hello, World!") -> str:
            """Simple run method that returns a greeting."""
            if not self.is_ready():
                raise RuntimeError("Agent is not ready")
            
            self.logger.info(f"Running with message: {message}")
            return f"Agent {self.name} says: {message}"
    
    # Test basic agent functionality
    agent = TestAgent(name="TestAgent")
    
    # Initialize and run
    success = await agent.initialize()
    if success:
        result = await agent.run("Framework is working!")
        print(f"Result: {result}")
        print(f"Status: {agent.get_status()}")
    
    # Cleanup
    await agent.cleanup()


if __name__ == "__main__":
    # Run the test if this file is executed directly
    asyncio.run(test_base_agent())