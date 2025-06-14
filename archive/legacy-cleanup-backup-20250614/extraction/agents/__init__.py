# agents/__init__.py
# Agent Forge Framework Agent Package
"""
Core agent foundation for the Agent Forge framework.

Framework Components:
- base: BaseAgent foundation class for all agents
- models: Core Pydantic data structures

Agent Examples:
- See examples/ directory for working agent implementations
- All examples inherit from BaseAgent and demonstrate framework patterns
"""

# Import core framework components
from .base import BaseAgent

__all__ = [
    "BaseAgent",
]
