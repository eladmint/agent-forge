"""
Universal Payment AVS for Othentic integration.

Provides multi-provider payment processing with escrow capabilities
across cryptocurrency and traditional payment methods.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal

if TYPE_CHECKING:
    from ..client import OthenticAVSClient

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    """Payment method enumeration."""
    # Cryptocurrency
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    CARDANO_ADA = "cardano_ada"
    SOLANA_SOL = "solana_sol"
    POLYGON_MATIC = "polygon_matic"
    USDC = "usdc"
    USDT = "usdt"
    DAI = "dai"
    
    # Traditional Payment
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class EscrowStatus(Enum):
    """Escrow status enumeration."""
    CREATED = "created"
    FUNDED = "funded"
    RELEASED = "released"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


@dataclass
class PaymentRequest:
    """Payment request information."""
    
    request_id: str
    payer_id: str
    payee_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    description: str
    task_id: Optional[str] = None
    escrow_required: bool = True
    escrow_timeout: int = 7200  # 2 hours in seconds
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['payment_method'] = self.payment_method.value
        data['amount'] = str(self.amount)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class PaymentTransaction:
    """Payment transaction record."""
    
    transaction_id: str
    request_id: str
    payer_id: str
    payee_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    escrow_status: Optional[EscrowStatus]
    blockchain_hash: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['payment_method'] = self.payment_method.value
        data['status'] = self.status.value
        data['escrow_status'] = self.escrow_status.value if self.escrow_status else None
        data['amount'] = str(self.amount)
        data['fee_amount'] = str(self.fee_amount) if self.fee_amount else None
        data['created_at'] = self.created_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


@dataclass
class EscrowContract:
    """Escrow contract information."""
    
    escrow_id: str
    payer_id: str
    payee_id: str
    amount: Decimal
    currency: str
    status: EscrowStatus
    task_id: Optional[str]
    release_conditions: List[str]
    timeout_timestamp: datetime
    created_at: datetime
    released_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['amount'] = str(self.amount)
        data['timeout_timestamp'] = self.timeout_timestamp.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['released_at'] = self.released_at.isoformat() if self.released_at else None
        return data


class UniversalPaymentAVS:
    """
    Universal Payment AVS service.
    
    Provides multi-provider payment processing with escrow capabilities
    across cryptocurrency and traditional payment methods.
    """
    
    def __init__(self, client: 'OthenticAVSClient'):
        """
        Initialize Universal Payment AVS.
        
        Args:
            client: Parent Othentic AVS client
        """
        self.client = client
        self._initialized = False
        self._supported_methods = []
        
    async def initialize(self):
        """Initialize the Universal Payment AVS."""
        try:
            # Verify payment processor connectivity
            await self._verify_processor_connection()
            await self._load_supported_methods()
            self._initialized = True
            logger.info("Universal Payment AVS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Universal Payment AVS: {e}")
            raise
            
    async def _verify_processor_connection(self):
        """Verify connection to payment processors."""
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/payments/health"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if not result.get("healthy", False):
                    raise RuntimeError("Universal Payment AVS is not healthy")
                    
        except Exception as e:
            logger.error(f"Payment processor health check failed: {e}")
            raise
            
    async def _load_supported_methods(self):
        """Load supported payment methods."""
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/payments/methods"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                self._supported_methods = [
                    PaymentMethod(method) for method in result.get("methods", [])
                ]
                
        except Exception as e:
            logger.error(f"Failed to load supported payment methods: {e}")
            raise
            
    async def create_payment_request(self, 
                                   request: PaymentRequest) -> Dict[str, Any]:
        """
        Create a new payment request.
        
        Args:
            request: Payment request details
            
        Returns:
            Payment request creation result
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        # Validate payment method is supported
        if request.payment_method not in self._supported_methods:
            raise ValueError(f"Payment method {request.payment_method.value} not supported")
            
        payload = request.to_dict()
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/payments/requests",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Payment request created: {request.request_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to create payment request {request.request_id}: {e}")
            raise
            
    async def process_payment(self, 
                            request_id: str,
                            provider_data: Optional[Dict[str, Any]] = None) -> PaymentTransaction:
        """
        Process a payment request.
        
        Args:
            request_id: Payment request identifier
            provider_data: Provider-specific payment data
            
        Returns:
            Payment transaction record
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = {
            "request_id": request_id,
            "processor_id": self.client.config.agent_id,
            "provider_data": provider_data or {},
            "processing_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/payments/process",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Convert to PaymentTransaction object
                transaction = PaymentTransaction(
                    transaction_id=data['transaction_id'],
                    request_id=data['request_id'],
                    payer_id=data['payer_id'],
                    payee_id=data['payee_id'],
                    amount=Decimal(data['amount']),
                    currency=data['currency'],
                    payment_method=PaymentMethod(data['payment_method']),
                    status=PaymentStatus(data['status']),
                    escrow_status=EscrowStatus(data['escrow_status']) if data.get('escrow_status') else None,
                    blockchain_hash=data.get('blockchain_hash'),
                    provider_transaction_id=data.get('provider_transaction_id'),
                    fee_amount=Decimal(data['fee_amount']) if data.get('fee_amount') else None,
                    created_at=datetime.fromisoformat(data['created_at']),
                    completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                    metadata=data.get('metadata')
                )
                
                logger.info(f"Payment processed: {transaction.transaction_id}")
                return transaction
                
        except Exception as e:
            logger.error(f"Failed to process payment {request_id}: {e}")
            raise
            
    async def create_escrow(self, 
                          payment_request: PaymentRequest,
                          release_conditions: List[str]) -> EscrowContract:
        """
        Create an escrow contract for a payment.
        
        Args:
            payment_request: Payment request to escrow
            release_conditions: Conditions for escrow release
            
        Returns:
            Escrow contract
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        timeout_timestamp = datetime.utcnow() + timedelta(seconds=payment_request.escrow_timeout)
        
        payload = {
            "request_id": payment_request.request_id,
            "payer_id": payment_request.payer_id,
            "payee_id": payment_request.payee_id,
            "amount": str(payment_request.amount),
            "currency": payment_request.currency,
            "task_id": payment_request.task_id,
            "release_conditions": release_conditions,
            "timeout_timestamp": timeout_timestamp.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/payments/escrow/create",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                escrow = EscrowContract(
                    escrow_id=data['escrow_id'],
                    payer_id=data['payer_id'],
                    payee_id=data['payee_id'],
                    amount=Decimal(data['amount']),
                    currency=data['currency'],
                    status=EscrowStatus(data['status']),
                    task_id=data.get('task_id'),
                    release_conditions=data['release_conditions'],
                    timeout_timestamp=datetime.fromisoformat(data['timeout_timestamp']),
                    created_at=datetime.fromisoformat(data['created_at']),
                    metadata=data.get('metadata')
                )
                
                logger.info(f"Escrow contract created: {escrow.escrow_id}")
                return escrow
                
        except Exception as e:
            logger.error(f"Failed to create escrow for {payment_request.request_id}: {e}")
            raise
            
    async def release_escrow(self, 
                           escrow_id: str,
                           release_proof: Dict[str, Any]) -> Dict[str, Any]:
        """
        Release funds from escrow upon condition fulfillment.
        
        Args:
            escrow_id: Escrow contract identifier
            release_proof: Proof that release conditions are met
            
        Returns:
            Escrow release result
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = {
            "escrow_id": escrow_id,
            "releaser_id": self.client.config.agent_id,
            "release_proof": release_proof,
            "release_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/payments/escrow/{escrow_id}/release",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Escrow released: {escrow_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to release escrow {escrow_id}: {e}")
            raise
            
    async def dispute_payment(self, 
                            transaction_id: str,
                            dispute_reason: str,
                            evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispute a payment transaction.
        
        Args:
            transaction_id: Transaction to dispute
            dispute_reason: Reason for dispute
            evidence: Supporting evidence
            
        Returns:
            Dispute creation result
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = {
            "transaction_id": transaction_id,
            "disputer_id": self.client.config.agent_id,
            "dispute_reason": dispute_reason,
            "evidence": evidence,
            "dispute_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/payments/disputes",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Payment dispute created for transaction: {transaction_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to create dispute for transaction {transaction_id}: {e}")
            raise
            
    async def get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """
        Get payment transaction details.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Payment transaction or None if not found
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/payments/transactions/{transaction_id}"
            ) as response:
                if response.status == 404:
                    return None
                    
                response.raise_for_status()
                data = await response.json()
                
                return PaymentTransaction(
                    transaction_id=data['transaction_id'],
                    request_id=data['request_id'],
                    payer_id=data['payer_id'],
                    payee_id=data['payee_id'],
                    amount=Decimal(data['amount']),
                    currency=data['currency'],
                    payment_method=PaymentMethod(data['payment_method']),
                    status=PaymentStatus(data['status']),
                    escrow_status=EscrowStatus(data['escrow_status']) if data.get('escrow_status') else None,
                    blockchain_hash=data.get('blockchain_hash'),
                    provider_transaction_id=data.get('provider_transaction_id'),
                    fee_amount=Decimal(data['fee_amount']) if data.get('fee_amount') else None,
                    created_at=datetime.fromisoformat(data['created_at']),
                    completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                    metadata=data.get('metadata')
                )
                
        except Exception as e:
            logger.error(f"Failed to get transaction {transaction_id}: {e}")
            raise
            
    async def get_payment_history(self, 
                                agent_id: str,
                                limit: int = 100,
                                offset: int = 0) -> List[PaymentTransaction]:
        """
        Get payment history for an agent.
        
        Args:
            agent_id: Agent identifier
            limit: Maximum number of records
            offset: Pagination offset
            
        Returns:
            List of payment transactions
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        params = {
            "agent_id": agent_id,
            "limit": limit,
            "offset": offset
        }
        
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/payments/history",
                params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                transactions = []
                for tx_data in data.get('transactions', []):
                    transactions.append(PaymentTransaction(
                        transaction_id=tx_data['transaction_id'],
                        request_id=tx_data['request_id'],
                        payer_id=tx_data['payer_id'],
                        payee_id=tx_data['payee_id'],
                        amount=Decimal(tx_data['amount']),
                        currency=tx_data['currency'],
                        payment_method=PaymentMethod(tx_data['payment_method']),
                        status=PaymentStatus(tx_data['status']),
                        escrow_status=EscrowStatus(tx_data['escrow_status']) if tx_data.get('escrow_status') else None,
                        blockchain_hash=tx_data.get('blockchain_hash'),
                        provider_transaction_id=tx_data.get('provider_transaction_id'),
                        fee_amount=Decimal(tx_data['fee_amount']) if tx_data.get('fee_amount') else None,
                        created_at=datetime.fromisoformat(tx_data['created_at']),
                        completed_at=datetime.fromisoformat(tx_data['completed_at']) if tx_data.get('completed_at') else None,
                        metadata=tx_data.get('metadata')
                    ))
                
                return transactions
                
        except Exception as e:
            logger.error(f"Failed to get payment history for {agent_id}: {e}")
            raise
            
    def get_supported_methods(self) -> List[PaymentMethod]:
        """
        Get list of supported payment methods.
        
        Returns:
            List of supported payment methods
        """
        return self._supported_methods.copy()
        
    async def get_payment_stats(self) -> Dict[str, Any]:
        """
        Get payment processor statistics.
        
        Returns:
            Payment statistics
        """
        if not self._initialized:
            raise RuntimeError("Universal Payment AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/payments/stats"
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get payment stats: {e}")
            raise