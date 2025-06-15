# Enhanced Cardano Client API Reference

## Overview

The Enhanced Cardano Client provides a comprehensive interface for building AI agent economies on the Cardano blockchain. It implements 5 core smart contract architecture patterns for enterprise-grade decentralized applications.

## Quick Start

```python
from src.core.blockchain.cardano_enhanced_client import EnhancedCardanoClient, AgentProfile

# Initialize client
client = EnhancedCardanoClient(
    nmkr_api_key="your_nmkr_key",
    blockfrost_project_id="your_project_id", 
    policy_id="your_policy_id"
)

# Create agent profile
profile = AgentProfile(
    owner_address="addr1_your_address",
    agent_id="ai_agent_001",
    metadata_uri="ipfs://QmYourMetadata",
    staked_amount=1000.0,
    capabilities=["web_automation", "ai_analysis"]
)

# Register agent
result = await client.register_agent(profile, stake_amount=1000.0)
```

## Classes

### EnhancedCardanoClient

Main client class for Cardano blockchain operations.

#### Constructor

```python
EnhancedCardanoClient(
    nmkr_api_key: str,
    blockfrost_project_id: str,
    policy_id: str
)
```

**Parameters:**
- `nmkr_api_key`: NMKR Studio API key for NFT operations
- `blockfrost_project_id`: Blockfrost project ID for blockchain queries
- `policy_id`: NFT policy ID for agent registry

#### Core Methods

##### register_agent()

```python
async def register_agent(
    self, 
    profile: AgentProfile, 
    stake_amount: float
) -> Dict[str, Any]
```

Register an AI agent in the hierarchical registry with reputation staking.

**Parameters:**
- `profile`: Agent profile containing capabilities and metadata
- `stake_amount`: ADA amount to stake (minimum based on capabilities)

**Returns:**
```python
{
    "status": "success",
    "agent_id": "ai_agent_001",
    "transaction_id": "tx_hash_123",
    "stake_amount": 1000.0,
    "stake_tier": "standard",
    "minimum_required": 300.0
}
```

**Raises:**
- `ValueError`: If stake amount is insufficient
- `ConnectionError`: If blockchain connection fails

##### find_agents()

```python
async def find_agents(
    self,
    capabilities: List[str],
    min_reputation: float = 0.0,
    max_agents: int = 10
) -> List[Dict[str, Any]]
```

Discover agents by capabilities and reputation.

**Parameters:**
- `capabilities`: Required agent capabilities
- `min_reputation`: Minimum reputation score (0.0-1.0)
- `max_agents`: Maximum number of agents to return

**Returns:**
```python
[
    {
        "agent_id": "ai_agent_001",
        "owner_address": "addr1_owner",
        "reputation_score": 0.95,
        "capabilities": ["web_automation", "ai_analysis"],
        "stake_tier": "professional",
        "total_executions": 1500,
        "successful_executions": 1425
    }
]
```

##### create_escrow()

```python
async def create_escrow(
    self,
    service_request: ServiceRequest
) -> Dict[str, Any]
```

Create escrow for agent service payment.

**Parameters:**
- `service_request`: Service request with payment details

**Returns:**
```python
{
    "status": "success",
    "escrow_id": "escrow_hash_456",
    "payment_amount": 25.0,
    "agent_id": "ai_agent_001",
    "deadline": "2025-12-31T23:59:59",
    "transaction_id": "tx_hash_789"
}
```

##### release_escrow()

```python
async def release_escrow(
    self,
    escrow_id: str,
    execution_proof: ExecutionProof
) -> Dict[str, Any]
```

Release escrow payment upon successful execution.

**Parameters:**
- `escrow_id`: Escrow identifier
- `execution_proof`: Cryptographic proof of execution

**Returns:**
```python
{
    "status": "success",
    "escrow_id": "escrow_hash_456", 
    "payment_released": 25.0,
    "agent_id": "ai_agent_001",
    "transaction_id": "tx_hash_abc"
}
```

##### distribute_revenue()

```python
async def distribute_revenue(
    self,
    total_revenue: float,
    distribution_period: str
) -> Dict[str, Any]
```

Distribute platform revenue to token holders.

**Parameters:**
- `total_revenue`: Total revenue to distribute
- `distribution_period`: Period identifier (e.g., "2025-Q1")

**Returns:**
```python
{
    "status": "success",
    "total_revenue": 10000.0,
    "total_recipients": 150,
    "distribution_period": "2025-Q1",
    "distributions": [
        {
            "recipient_address": "addr1_recipient",
            "participation_tokens": 1000,
            "reward_amount": 66.67
        }
    ]
}
```

##### claim_rewards()

```python
async def claim_rewards(
    self,
    recipient_address: str
) -> Dict[str, Any]
```

Claim accumulated revenue sharing rewards.

**Parameters:**
- `recipient_address`: Address to receive rewards

**Returns:**
```python
{
    "status": "success",
    "recipient_address": "addr1_recipient",
    "claimed_amount": 150.0,
    "transaction_id": "tx_hash_def"
}
```

##### register_cross_chain_service()

```python
async def register_cross_chain_service(
    self,
    agent_id: str,
    supported_chains: List[str]
) -> Dict[str, Any]
```

Register agent for cross-chain operations.

**Parameters:**
- `agent_id`: Agent identifier
- `supported_chains`: List of supported blockchain networks

**Returns:**
```python
{
    "status": "success",
    "agent_id": "ai_agent_001",
    "supported_chains": ["cardano", "ethereum", "polygon"],
    "cross_chain_id": "cross_chain_123",
    "transaction_id": "tx_hash_ghi"
}
```

### Data Classes

#### AgentProfile

```python
@dataclass
class AgentProfile:
    owner_address: str
    agent_id: str
    metadata_uri: str
    staked_amount: float = 0.0
    reputation_score: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    total_executions: int = 0
    successful_executions: int = 0
    framework_version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

#### ServiceRequest

```python
@dataclass
class ServiceRequest:
    requester_address: str
    agent_id: str
    service_hash: str
    payment_amount: float
    escrow_deadline: str
    task_description: str = ""
    pricing_model: str = "per_execution"
    status: str = "pending"
    execution_proof: Optional[ExecutionProof] = None
    
    def generate_hash(self) -> str:
        """Generate deterministic hash for the service request."""
```

#### RevenueShare

```python
@dataclass
class RevenueShare:
    recipient_address: str
    participation_tokens: int
    accumulated_rewards: float = 0.0
    last_claim_block: int = 0
    contribution_score: float = 0.0
    
    def calculate_rewards(self, total_revenue: float, total_tokens: int) -> float:
        """Calculate reward amount based on token participation."""
```

## Smart Contract Patterns

### 1. Hierarchical Agent Registry

Multi-tier staking system with capability-based validation:

- **Basic Tier**: 100 ADA minimum stake
- **Standard Tier**: 500 ADA minimum stake  
- **Professional Tier**: 2,000 ADA minimum stake
- **Enterprise Tier**: 10,000 ADA minimum stake

### 2. Revenue Sharing Model

Token-based profit distribution:

- **Governance Tokens**: Platform decision voting
- **Utility Tokens**: Service payment medium
- **Participation Tokens**: Revenue sharing rights

### 3. Escrow System

Automated payment processing with cryptographic verification:

- **Execution Proofs**: ZK-verifiable task completion
- **Multi-Pricing Models**: Per-execution, subscription, tiered
- **Deadline Management**: Automatic refund mechanisms

### 4. Cross-Chain Protocol

Unified service discovery across 5+ blockchain networks:

- **Bridge Integration**: LayerZero, Wormhole compatibility
- **Unified Registry**: Cross-chain capability advertising
- **Payment Coordination**: Multi-chain escrow handling

### 5. Compliance Framework

Enterprise-ready regulatory compliance:

- **REGKYC Integration**: Privacy-preserving KYC/AML
- **GDPR Compliance**: Data minimization and encryption
- **ABAC Framework**: Attribute-based access control

## Error Handling

### Common Exceptions

```python
# Insufficient staking amount
{
    "status": "error",
    "error": "Insufficient stake amount",
    "provided": 50.0,
    "minimum_required": 300.0
}

# Agent not found
{
    "status": "error", 
    "error": "Agent not found in registry",
    "agent_id": "nonexistent_agent"
}

# Invalid execution proof
{
    "status": "error",
    "error": "Invalid execution proof",
    "reason": "Agent ID mismatch"
}
```

## Performance Considerations

### Throughput Metrics

- **NFT Minting**: 10+ operations/second
- **Agent Registration**: 200+ concurrent operations
- **Marketplace Transactions**: 15+ transactions/second
- **Revenue Distribution**: 1000+ participants

### Optimization Tips

1. **Batch Operations**: Group multiple agent registrations
2. **Connection Pooling**: Reuse blockchain connections
3. **Caching**: Cache frequently accessed agent data
4. **Async Processing**: Use async/await throughout

## Security Best Practices

### Input Validation

```python
# Always validate addresses
if not address.startswith("addr1"):
    raise ValueError("Invalid Cardano address format")

# Verify stake amounts
if stake_amount < 0:
    raise ValueError("Stake amount cannot be negative")
```

### Cryptographic Verification

```python
# Verify execution proofs
if not self._verify_execution_proof(proof, request):
    return {"status": "error", "error": "Invalid execution proof"}
```

### Access Control

```python
# Verify ownership before operations
if profile.owner_address != requester_address:
    raise PermissionError("Unauthorized agent modification")
```

## Testing

### Unit Tests

```bash
# Run Cardano client tests
python tests/cardano_test_runner.py --unit

# Run specific test categories
pytest tests/unit/test_cardano_enhanced_client.py -v
```

### Integration Tests

```bash
# Run integration tests
python tests/cardano_test_runner.py --integration
```

### Performance Tests

```bash
# Run performance benchmarks
python tests/cardano_test_runner.py --performance
```

## Examples

### Complete Agent Economy Demo

```python
from examples.cardano_enhanced_agent import CardanoEnhancedAgent

async def demo():
    async with CardanoEnhancedAgent(name="demo_agent") as agent:
        # Run complete AI economy demo
        result = await agent.run("full_demo")
        print(f"Demo completed: {result['summary']}")
        
        # Register new agent
        registration = await agent.run("register", stake_amount=1000.0)
        print(f"Agent registered: {registration['agent_id']}")
        
        # Test marketplace
        marketplace = await agent.run("marketplace")
        print(f"Marketplace demo: {marketplace['transactions']}")
```

### Custom Integration

```python
async def custom_integration():
    client = EnhancedCardanoClient(
        nmkr_api_key=os.getenv("NMKR_API_KEY"),
        blockfrost_project_id=os.getenv("BLOCKFROST_PROJECT_ID"),
        policy_id=os.getenv("POLICY_ID")
    )
    
    # Register AI agent
    profile = AgentProfile(
        owner_address="addr1_custom_owner",
        agent_id="custom_ai_agent",
        metadata_uri="ipfs://QmCustomMetadata",
        capabilities=["custom_capability"]
    )
    
    registration = await client.register_agent(profile, 500.0)
    print(f"Custom agent registered: {registration}")
    
    # Find similar agents
    agents = await client.find_agents(
        capabilities=["custom_capability"],
        min_reputation=0.8
    )
    print(f"Found {len(agents)} similar agents")
```

## Troubleshooting

### Common Issues

**Connection Errors:**
- Verify Blockfrost project ID and API key
- Check network connectivity
- Ensure Cardano node synchronization

**Transaction Failures:**
- Verify sufficient ADA balance
- Check transaction fees
- Validate input parameters

**Performance Issues:**
- Implement connection pooling
- Use batch operations for multiple requests
- Monitor memory usage with large datasets

### Support

For technical support and additional examples:
- 📚 **Documentation**: [docs/](../docs/)
- 🧪 **Tests**: [tests/unit/test_cardano_enhanced_client.py](../../tests/unit/test_cardano_enhanced_client.py)
- 🎯 **Examples**: [examples/cardano_enhanced_agent.py](../../examples/cardano_enhanced_agent.py)
- 📋 **Implementation Guide**: [CARDANO_IMPLEMENTATION_COMPLETE.md](../CARDANO_IMPLEMENTATION_COMPLETE.md)

---

*Enhanced Cardano Client API - Part of Agent Forge Framework*
*Last Updated: 2025-06-15*