"""
Agent Forge Masumi Network Bridge Integration

This module provides lightweight integration with Masumi Network infrastructure,
enabling Agent Forge agents to participate in the Masumi AI Agent Economy.

Features:
- Bridge to Masumi CrewAI workflows
- Integration with Masumi hosted payment service
- Agent registration with Masumi registry
- Proof-of-execution compatibility
"""

from .bridge_adapter import MasumiBridgeAdapter, MasumiAgentWrapper
from .payment_client import MasumiPaymentClient
from .registry_client import MasumiRegistryClient
from .config import MasumiConfig

__all__ = [
    'MasumiBridgeAdapter',
    'MasumiAgentWrapper', 
    'MasumiPaymentClient',
    'MasumiRegistryClient',
    'MasumiConfig'
]

__version__ = '1.0.0'