"""
Enterprise Compliance AVS for Othentic integration.

Provides regulatory compliance and enterprise integration features
including REGKYC and audit trail capabilities.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum

if TYPE_CHECKING:
    from ..client import OthenticAVSClient

logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Compliance status enumeration."""
    PENDING = "pending"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    EXEMPTED = "exempted"


class ComplianceFramework(Enum):
    """Compliance framework enumeration."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    REGKYC = "regkyc"


@dataclass
class ComplianceRecord:
    """Compliance record information."""
    
    record_id: str
    agent_id: str
    framework: ComplianceFramework
    status: ComplianceStatus
    compliance_data: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]
    expiry_date: Optional[datetime]
    last_audit: datetime
    next_audit: datetime
    auditor_id: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['framework'] = self.framework.value
        data['status'] = self.status.value
        data['expiry_date'] = self.expiry_date.isoformat() if self.expiry_date else None
        data['last_audit'] = self.last_audit.isoformat()
        data['next_audit'] = self.next_audit.isoformat()
        return data


class EnterpriseComplianceAVS:
    """
    Enterprise Compliance AVS service.
    
    Provides regulatory compliance and enterprise integration features
    including REGKYC and audit trail capabilities.
    """
    
    def __init__(self, client: 'OthenticAVSClient'):
        """
        Initialize Enterprise Compliance AVS.
        
        Args:
            client: Parent Othentic AVS client
        """
        self.client = client
        self._initialized = False
        
    async def initialize(self):
        """Initialize the Enterprise Compliance AVS."""
        try:
            await self._verify_contract_connection()
            self._initialized = True
            logger.info("Enterprise Compliance AVS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enterprise Compliance AVS: {e}")
            raise
            
    async def _verify_contract_connection(self):
        """Verify connection to the compliance contract."""
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/compliance/health"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if not result.get("healthy", False):
                    raise RuntimeError("Enterprise Compliance AVS is not healthy")
                    
        except Exception as e:
            logger.error(f"Compliance health check failed: {e}")
            raise