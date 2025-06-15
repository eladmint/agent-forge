"""
Cross-Chain Bridge AVS for Othentic integration.

Provides inter-chain asset and state management capabilities
for multi-blockchain operations.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum

if TYPE_CHECKING:
    from ..client import OthenticAVSClient

logger = logging.getLogger(__name__)


class BridgeStatus(Enum):
    """Bridge operation status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SupportedChain(Enum):
    """Supported blockchain enumeration."""
    ETHEREUM = "ethereum"
    CARDANO = "cardano"
    SOLANA = "solana"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    ARBITRUM = "arbitrum"


@dataclass
class CrossChainTransaction:
    """Cross-chain transaction record."""
    
    tx_id: str
    source_chain: SupportedChain
    destination_chain: SupportedChain
    source_address: str
    destination_address: str
    asset_type: str
    amount: str
    status: BridgeStatus
    source_tx_hash: Optional[str] = None
    destination_tx_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['source_chain'] = self.source_chain.value
        data['destination_chain'] = self.destination_chain.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class CrossChainBridgeAVS:
    """
    Cross-Chain Bridge AVS service.
    
    Provides inter-chain asset and state management capabilities
    for multi-blockchain operations.
    """
    
    def __init__(self, client: 'OthenticAVSClient'):
        """
        Initialize Cross-Chain Bridge AVS.
        
        Args:
            client: Parent Othentic AVS client
        """
        self.client = client
        self._initialized = False
        
    async def initialize(self):
        """Initialize the Cross-Chain Bridge AVS."""
        try:
            await self._verify_contract_connection()
            self._initialized = True
            logger.info("Cross-Chain Bridge AVS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cross-Chain Bridge AVS: {e}")
            raise
            
    async def _verify_contract_connection(self):
        """Verify connection to the cross-chain bridge contract."""
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/bridge/health"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if not result.get("healthy", False):
                    raise RuntimeError("Cross-Chain Bridge AVS is not healthy")
                    
        except Exception as e:
            logger.error(f"Cross-chain bridge health check failed: {e}")
            raise