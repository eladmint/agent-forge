"""
Othentic AVS (Actively Validated Services) integration for Agent Forge.

Provides multi-chain blockchain infrastructure for AI agents through
decentralized validation services and cross-chain operations.
"""

from .client import OthenticAVSClient
from .avs.agent_registry import AgentRegistryAVS
from .avs.payment_processor import UniversalPaymentAVS
from .avs.reputation import ReputationValidationAVS
from .avs.compliance import EnterpriseComplianceAVS
from .avs.cross_chain import CrossChainBridgeAVS

__all__ = [
    'OthenticAVSClient',
    'AgentRegistryAVS',
    'UniversalPaymentAVS', 
    'ReputationValidationAVS',
    'EnterpriseComplianceAVS',
    'CrossChainBridgeAVS'
]

__version__ = '1.0.0'