"""
Masumi Payment Service Client

Integration with Masumi's hosted payment service using the credentials
and endpoints provided in the hacker guidelines.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from .config import MasumiConfig


class MasumiPaymentClient:
    """Client for Masumi hosted payment service."""
    
    def __init__(self, config: Optional[MasumiConfig] = None):
        self.config = config or MasumiConfig.for_testing()
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP session."""
        headers = {
            'Authorization': f'Bearer {self.config.payment_bearer_token}',
            'Content-Type': 'application/json'
        }
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def verify_payment(self, payment_proof: str, job_id: str) -> bool:
        """
        Verify payment has been made for a specific job.
        
        Args:
            payment_proof: Transaction hash or payment reference
            job_id: Unique job identifier
            
        Returns:
            bool: True if payment is verified, False otherwise
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.config.payment_service_url}/api/v1/payments/verify"
            data = {
                "payment_proof": payment_proof,
                "job_id": job_id,
                "network": self.config.network
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('verified', False)
                else:
                    self.logger.error(f"Payment verification failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error verifying payment: {e}")
            return False
    
    async def create_payment_request(
        self, 
        job_id: str, 
        amount_ada: float, 
        agent_did: str,
        service_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new payment request for an agent service.
        
        Args:
            job_id: Unique job identifier
            amount_ada: Payment amount in ADA
            agent_did: Agent's decentralized identifier
            service_description: Description of the service
            
        Returns:
            Payment request data including payment address and reference
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.config.payment_service_url}/api/v1/payments/request"
            data = {
                "job_id": job_id,
                "amount": amount_ada,
                "currency": "ADA",
                "agent_did": agent_did,
                "service_description": service_description,
                "network": self.config.network,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    self.logger.error(f"Payment request failed: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error creating payment request: {e}")
            return None
    
    async def claim_payment(
        self, 
        job_id: str, 
        proof_hash: str,
        execution_proof: Dict[str, Any]
    ) -> Optional[str]:
        """
        Claim payment after successful job completion.
        
        Args:
            job_id: Unique job identifier
            proof_hash: Hash of execution proof
            execution_proof: Complete execution proof data
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.config.payment_service_url}/api/v1/payments/claim"
            data = {
                "job_id": job_id,
                "proof_hash": proof_hash,
                "execution_proof": execution_proof,
                "network": self.config.network,
                "claimed_at": datetime.utcnow().isoformat()
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('transaction_hash')
                else:
                    self.logger.error(f"Payment claim failed: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error claiming payment: {e}")
            return None
    
    async def get_payment_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current payment status for a job.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Payment status information
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.config.payment_service_url}/api/v1/payments/status/{job_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Payment status check failed: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error checking payment status: {e}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check if Masumi payment service is available.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.config.payment_service_url}/docs"  # Swagger docs endpoint
            
            async with self.session.get(url) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False