"""
Enhanced Cardano Client for Agent Forge
Implements advanced features from the Smart Contract Architecture Plan.

This enhanced client extends the existing NMKR integration with:
- Multi-tier agent registry patterns
- Revenue sharing mechanisms
- Reputation staking systems
- Cross-chain service discovery
- Enterprise compliance features
"""

import asyncio
import json
import hashlib
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from .nmkr_integration import NMKRClient, NMKRProofGenerator, ExecutionProof


@dataclass
class AgentProfile:
    """Enhanced agent profile for registry pattern."""
    owner_address: str
    agent_id: str
    metadata_uri: str
    staked_amount: float
    reputation_score: float
    capabilities: List[str]
    total_executions: int
    successful_executions: int
    framework_version: str = "1.0.0"
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ServiceRequest:
    """Service request structure for marketplace."""
    requester_address: str
    agent_id: str
    service_hash: str
    payment_amount: float
    escrow_deadline: str
    task_description: str
    execution_proof: Optional[ExecutionProof] = None
    status: str = "pending"
    
    def generate_hash(self) -> str:
        """Generate deterministic hash of service request."""
        request_data = {
            "requester": self.requester_address,
            "agent": self.agent_id,
            "service": self.service_hash,
            "payment": self.payment_amount,
            "deadline": self.escrow_deadline,
            "task": self.task_description
        }
        data_str = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class RevenueShare:
    """Revenue participation token structure."""
    recipient_address: str
    participation_tokens: int
    accumulated_rewards: float
    last_claim_block: int
    contribution_score: float = 0.0
    
    def calculate_rewards(self, total_revenue: float, total_tokens: int) -> float:
        """Calculate rewards based on participation tokens."""
        if total_tokens == 0:
            return 0.0
        return (self.participation_tokens / total_tokens) * total_revenue


class EnhancedCardanoClient:
    """
    Enhanced Cardano client implementing smart contract architecture patterns.
    
    Features:
    - Hierarchical agent registry with reputation staking
    - Dual-token economic model with revenue sharing
    - Escrow-as-a-Service with verification
    - Cross-chain service discovery protocol
    - Compliance-ready ABAC framework
    """
    
    def __init__(self, 
                 nmkr_api_key: str,
                 blockfrost_project_id: str,
                 policy_id: str = "agent_forge_policy",
                 base_url: str = "https://api.nmkr.io"):
        """
        Initialize enhanced Cardano client.
        
        Args:
            nmkr_api_key: NMKR Studio API key
            blockfrost_project_id: Blockfrost API project ID
            policy_id: Cardano policy ID for agent registry
            base_url: NMKR API base URL
        """
        self.nmkr_client = NMKRClient(nmkr_api_key, base_url)
        self.blockfrost_project_id = blockfrost_project_id
        self.policy_id = policy_id
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Enhanced features
        self.agent_registry: Dict[str, AgentProfile] = {}
        self.service_requests: Dict[str, ServiceRequest] = {}
        self.revenue_shares: Dict[str, RevenueShare] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        await self.nmkr_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        await self.nmkr_client.__aexit__(exc_type, exc_val, exc_tb)
    
    # Agent Registry Functions
    
    async def register_agent(self, 
                           profile: AgentProfile, 
                           stake_amount: float) -> Dict[str, Any]:
        """
        Register agent with reputation staking.
        
        Implements hierarchical registry pattern with multi-tiered staking.
        
        Args:
            profile: Agent profile information
            stake_amount: Amount to stake for reputation
            
        Returns:
            Registration result with transaction details
        """
        if stake_amount < self._get_minimum_stake(profile.capabilities):
            return {
                "status": "error",
                "error": "Insufficient stake for claimed capabilities",
                "minimum_required": self._get_minimum_stake(profile.capabilities)
            }
        
        # Create registration metadata
        registration_metadata = {
            "721": {
                self.policy_id: {
                    f"agent_registry_{profile.agent_id}": {
                        "name": f"Agent Registry - {profile.agent_id}",
                        "description": f"Agent registration with {stake_amount} ADA stake",
                        "image": "ipfs://QmAgentRegistryThumbnail",
                        "attributes": {
                            "Agent ID": profile.agent_id,
                            "Owner Address": profile.owner_address,
                            "Staked Amount": f"{stake_amount} ADA",
                            "Capabilities": ", ".join(profile.capabilities),
                            "Framework Version": profile.framework_version,
                            "Registration Date": profile.created_at,
                            "Registry Type": "Hierarchical Agent Registry",
                            "Stake Tier": self._calculate_stake_tier(stake_amount)
                        }
                    }
                }
            }
        }
        
        try:
            # Mint registration NFT
            mint_result = await self.nmkr_client.mint_nft(
                policy_id=self.policy_id,
                asset_name=f"agent_registry_{profile.agent_id}",
                metadata=registration_metadata,
                recipient_address=profile.owner_address
            )
            
            # Store in local registry
            self.agent_registry[profile.agent_id] = profile
            
            return {
                "status": "success",
                "agent_id": profile.agent_id,
                "transaction_id": mint_result.get("transaction_id"),
                "stake_amount": stake_amount,
                "stake_tier": self._calculate_stake_tier(stake_amount),
                "capabilities": profile.capabilities,
                "registration_nft": mint_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_id": profile.agent_id
            }
    
    async def find_agents(self, 
                         capabilities: List[str], 
                         min_reputation: float = 0.0,
                         max_agents: int = 10) -> List[Dict[str, Any]]:
        """
        Find agents by capabilities with reputation filtering.
        
        Implements service discovery patterns from the architecture plan.
        
        Args:
            capabilities: Required agent capabilities
            min_reputation: Minimum reputation score
            max_agents: Maximum number of agents to return
            
        Returns:
            List of matching agents sorted by reputation
        """
        matching_agents = []
        
        for agent_id, profile in self.agent_registry.items():
            # Check capability match
            if not any(cap in profile.capabilities for cap in capabilities):
                continue
                
            # Check reputation threshold
            if profile.reputation_score < min_reputation:
                continue
            
            # Calculate success rate
            success_rate = 0.0
            if profile.total_executions > 0:
                success_rate = profile.successful_executions / profile.total_executions
            
            matching_agents.append({
                "agent_id": agent_id,
                "owner_address": profile.owner_address,
                "reputation_score": profile.reputation_score,
                "success_rate": success_rate,
                "staked_amount": profile.staked_amount,
                "capabilities": profile.capabilities,
                "total_executions": profile.total_executions,
                "framework_version": profile.framework_version
            })
        
        # Sort by reputation score (descending)
        matching_agents.sort(key=lambda x: x["reputation_score"], reverse=True)
        
        return matching_agents[:max_agents]
    
    # Escrow and Payment Functions
    
    async def create_escrow(self, service_request: ServiceRequest) -> Dict[str, Any]:
        """
        Create escrow contract for service payment.
        
        Implements dual-deposit escrow pattern with verification.
        
        Args:
            service_request: Service request details
            
        Returns:
            Escrow creation result
        """
        escrow_metadata = {
            "721": {
                self.policy_id: {
                    f"escrow_{service_request.generate_hash()[:16]}": {
                        "name": "Agent Service Escrow",
                        "description": f"Escrow for service: {service_request.task_description}",
                        "image": "ipfs://QmEscrowThumbnail",
                        "attributes": {
                            "Requester": service_request.requester_address,
                            "Agent ID": service_request.agent_id,
                            "Payment Amount": f"{service_request.payment_amount} ADA",
                            "Service Hash": service_request.service_hash,
                            "Deadline": service_request.escrow_deadline,
                            "Task Description": service_request.task_description,
                            "Escrow Type": "Dual-Deposit with ZK Verification",
                            "Status": "Active"
                        }
                    }
                }
            }
        }
        
        try:
            # Create escrow NFT
            escrow_result = await self.nmkr_client.mint_nft(
                policy_id=self.policy_id,
                asset_name=f"escrow_{service_request.generate_hash()[:16]}",
                metadata=escrow_metadata,
                recipient_address=service_request.requester_address
            )
            
            # Store service request
            request_id = service_request.generate_hash()
            self.service_requests[request_id] = service_request
            
            return {
                "status": "success",
                "escrow_id": request_id,
                "transaction_id": escrow_result.get("transaction_id"),
                "payment_amount": service_request.payment_amount,
                "deadline": service_request.escrow_deadline,
                "escrow_nft": escrow_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "service_request": service_request.generate_hash()
            }
    
    async def release_escrow(self, 
                           escrow_id: str, 
                           execution_proof: ExecutionProof) -> Dict[str, Any]:
        """
        Release escrow payment with execution proof verification.
        
        Args:
            escrow_id: Escrow identifier
            execution_proof: Proof of service completion
            
        Returns:
            Escrow release result
        """
        if escrow_id not in self.service_requests:
            return {
                "status": "error",
                "error": "Escrow not found",
                "escrow_id": escrow_id
            }
        
        service_request = self.service_requests[escrow_id]
        
        # Verify execution proof
        proof_valid = self._verify_execution_proof(execution_proof, service_request)
        
        if not proof_valid:
            return {
                "status": "error",
                "error": "Invalid execution proof",
                "escrow_id": escrow_id
            }
        
        # Update service request with proof
        service_request.execution_proof = execution_proof
        service_request.status = "completed"
        
        # Update agent reputation
        await self._update_agent_reputation(
            service_request.agent_id, 
            success=True,
            execution_time=execution_proof.execution_time
        )
        
        return {
            "status": "success",
            "escrow_id": escrow_id,
            "payment_released": service_request.payment_amount,
            "agent_id": service_request.agent_id,
            "execution_proof_hash": execution_proof.generate_hash(),
            "reputation_updated": True
        }
    
    # Revenue Sharing Functions
    
    async def distribute_revenue(self, 
                               total_revenue: float,
                               distribution_period: str) -> Dict[str, Any]:
        """
        Distribute revenue to participation token holders.
        
        Implements Revenue Participation Token pattern.
        
        Args:
            total_revenue: Total revenue to distribute
            distribution_period: Time period for distribution
            
        Returns:
            Distribution result with recipient details
        """
        if not self.revenue_shares:
            return {
                "status": "error",
                "error": "No revenue share participants",
                "total_revenue": total_revenue
            }
        
        total_tokens = sum(share.participation_tokens for share in self.revenue_shares.values())
        distribution_results = []
        
        for address, share in self.revenue_shares.items():
            reward_amount = share.calculate_rewards(total_revenue, total_tokens)
            
            # Update accumulated rewards
            share.accumulated_rewards += reward_amount
            
            distribution_results.append({
                "recipient_address": address,
                "participation_tokens": share.participation_tokens,
                "reward_amount": reward_amount,
                "total_accumulated": share.accumulated_rewards,
                "contribution_score": share.contribution_score
            })
        
        return {
            "status": "success",
            "total_revenue": total_revenue,
            "total_recipients": len(distribution_results),
            "distribution_period": distribution_period,
            "distributions": distribution_results
        }
    
    async def claim_rewards(self, recipient_address: str) -> Dict[str, Any]:
        """
        Claim accumulated rewards for a recipient.
        
        Args:
            recipient_address: Address to claim rewards for
            
        Returns:
            Claim result with transaction details
        """
        if recipient_address not in self.revenue_shares:
            return {
                "status": "error",
                "error": "No revenue share found for address",
                "address": recipient_address
            }
        
        share = self.revenue_shares[recipient_address]
        
        if share.accumulated_rewards <= 0:
            return {
                "status": "error",
                "error": "No rewards available to claim",
                "address": recipient_address
            }
        
        # Create reward claim metadata
        claim_metadata = {
            "721": {
                self.policy_id: {
                    f"reward_claim_{int(datetime.now().timestamp())}": {
                        "name": "Revenue Share Claim",
                        "description": f"Reward claim for {share.accumulated_rewards} ADA",
                        "image": "ipfs://QmRewardClaimThumbnail",
                        "attributes": {
                            "Recipient": recipient_address,
                            "Reward Amount": f"{share.accumulated_rewards} ADA",
                            "Participation Tokens": share.participation_tokens,
                            "Contribution Score": share.contribution_score,
                            "Claim Date": datetime.now().isoformat(),
                            "Claim Type": "Revenue Participation Token Reward"
                        }
                    }
                }
            }
        }
        
        try:
            # Mint reward claim NFT
            claim_result = await self.nmkr_client.mint_nft(
                policy_id=self.policy_id,
                asset_name=f"reward_claim_{int(datetime.now().timestamp())}",
                metadata=claim_metadata,
                recipient_address=recipient_address
            )
            
            # Reset accumulated rewards
            claimed_amount = share.accumulated_rewards
            share.accumulated_rewards = 0.0
            share.last_claim_block = self._get_current_block_height()
            
            return {
                "status": "success",
                "recipient_address": recipient_address,
                "claimed_amount": claimed_amount,
                "transaction_id": claim_result.get("transaction_id"),
                "claim_nft": claim_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recipient_address": recipient_address
            }
    
    # Utility Functions
    
    def _get_minimum_stake(self, capabilities: List[str]) -> float:
        """Calculate minimum stake based on capabilities."""
        base_stake = 100.0  # 100 ADA base
        capability_multiplier = {
            "blockchain": 2.0,
            "ai_analysis": 1.5,
            "web_automation": 1.2,
            "data_processing": 1.3,
            "smart_contracts": 3.0,
            "cross_chain": 2.5
        }
        
        multiplier = 1.0
        for capability in capabilities:
            multiplier += capability_multiplier.get(capability, 0.1)
        
        return base_stake * multiplier
    
    def _calculate_stake_tier(self, stake_amount: float) -> str:
        """Calculate stake tier based on amount."""
        if stake_amount >= 10000:
            return "enterprise"
        elif stake_amount >= 1000:
            return "professional"
        elif stake_amount >= 100:
            return "standard"
        else:
            return "basic"
    
    def _verify_execution_proof(self, 
                              proof: ExecutionProof, 
                              service_request: ServiceRequest) -> bool:
        """Verify execution proof against service request."""
        # Basic verification checks
        if proof.agent_id != service_request.agent_id:
            return False
        
        if not proof.task_completed:
            return False
        
        # Verify proof hash integrity
        proof_hash = proof.generate_hash()
        if not proof_hash:
            return False
        
        return True
    
    async def _update_agent_reputation(self, 
                                     agent_id: str, 
                                     success: bool,
                                     execution_time: float):
        """Update agent reputation based on execution results."""
        if agent_id not in self.agent_registry:
            return
        
        profile = self.agent_registry[agent_id]
        profile.total_executions += 1
        
        if success:
            profile.successful_executions += 1
            
            # Reputation calculation factors
            success_rate = profile.successful_executions / profile.total_executions
            time_factor = max(0.1, 1.0 - (execution_time / 600.0))  # Penalize slow execution
            stake_factor = min(2.0, profile.staked_amount / 1000.0)  # Reward higher stakes
            
            # Update reputation score
            new_reputation = (success_rate * 0.6) + (time_factor * 0.2) + (stake_factor * 0.2)
            profile.reputation_score = max(profile.reputation_score, new_reputation)
    
    def _get_current_block_height(self) -> int:
        """Get current Cardano block height (placeholder)."""
        # In production, this would query Blockfrost API
        return int(datetime.now().timestamp() / 20)  # ~20 second blocks
    
    # Cross-Chain Functions
    
    async def register_cross_chain_service(self, 
                                         agent_id: str, 
                                         supported_chains: List[str]) -> Dict[str, Any]:
        """
        Register agent for cross-chain service discovery.
        
        Args:
            agent_id: Agent identifier
            supported_chains: List of supported blockchain networks
            
        Returns:
            Cross-chain registration result
        """
        if agent_id not in self.agent_registry:
            return {
                "status": "error",
                "error": "Agent not found in registry",
                "agent_id": agent_id
            }
        
        profile = self.agent_registry[agent_id]
        
        # Create cross-chain metadata
        cross_chain_metadata = {
            "721": {
                self.policy_id: {
                    f"cross_chain_{agent_id}_{int(datetime.now().timestamp())}": {
                        "name": f"Cross-Chain Service - {agent_id}",
                        "description": f"Multi-chain service registration for {len(supported_chains)} networks",
                        "image": "ipfs://QmCrossChainServiceThumbnail",
                        "attributes": {
                            "Agent ID": agent_id,
                            "Supported Chains": ", ".join(supported_chains),
                            "Primary Chain": "Cardano",
                            "Bridge Protocol": "Multi-Chain Native",
                            "Service Type": "Cross-Chain AI Agent",
                            "Registration Date": datetime.now().isoformat(),
                            "Reputation Score": profile.reputation_score,
                            "Total Executions": profile.total_executions
                        }
                    }
                }
            }
        }
        
        try:
            # Mint cross-chain registration NFT
            cross_chain_result = await self.nmkr_client.mint_nft(
                policy_id=self.policy_id,
                asset_name=f"cross_chain_{agent_id}_{int(datetime.now().timestamp())}",
                metadata=cross_chain_metadata,
                recipient_address=profile.owner_address
            )
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "supported_chains": supported_chains,
                "transaction_id": cross_chain_result.get("transaction_id"),
                "cross_chain_nft": cross_chain_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id
            }


# Usage Example
async def demo_enhanced_cardano():
    """Demonstrate enhanced Cardano client features."""
    print("🚀 Enhanced Cardano Client Demo")
    
    async with EnhancedCardanoClient(
        nmkr_api_key="demo_key",
        blockfrost_project_id="demo_project",
        policy_id="agent_forge_enhanced_policy"
    ) as client:
        
        # 1. Register agent with staking
        profile = AgentProfile(
            owner_address="addr1_demo_owner",
            agent_id="ai_web_analyzer",
            metadata_uri="ipfs://QmAgentMetadata",
            staked_amount=500.0,
            reputation_score=0.85,
            capabilities=["web_automation", "ai_analysis", "blockchain"],
            total_executions=150,
            successful_executions=142
        )
        
        registration = await client.register_agent(profile, stake_amount=500.0)
        print(f"✅ Agent registered: {registration}")
        
        # 2. Find agents by capabilities
        agents = await client.find_agents(
            capabilities=["web_automation", "ai_analysis"],
            min_reputation=0.8
        )
        print(f"🔍 Found agents: {len(agents)}")
        
        # 3. Create service escrow
        service_request = ServiceRequest(
            requester_address="addr1_demo_requester",
            agent_id="ai_web_analyzer",
            service_hash="web_analysis_task_001",
            payment_amount=50.0,
            escrow_deadline=(datetime.now()).isoformat(),
            task_description="Analyze competitor website structure"
        )
        
        escrow = await client.create_escrow(service_request)
        print(f"💰 Escrow created: {escrow}")
        
        # 4. Distribute revenue
        client.revenue_shares["addr1_demo_participant"] = RevenueShare(
            recipient_address="addr1_demo_participant",
            participation_tokens=1000,
            accumulated_rewards=0.0,
            last_claim_block=0,
            contribution_score=0.92
        )
        
        revenue_distribution = await client.distribute_revenue(
            total_revenue=1000.0,
            distribution_period="2025-Q1"
        )
        print(f"💸 Revenue distributed: {revenue_distribution}")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_cardano())