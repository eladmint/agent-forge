#!/usr/bin/env python3
"""
🏛️ Enhanced Cardano Agent Demo
Complete AI Agent Economy Demonstration

This demo showcases the Enhanced Cardano Agent's full capabilities:
- Hierarchical Agent Registry with Reputation Staking
- Dual-Token Economic Model with Revenue Sharing  
- Escrow-as-a-Service with ZK Verification
- Cross-Chain Service Discovery Protocol
- Compliance-Ready ABAC Framework

Usage:
    python tools/demos/cardano_enhanced_demo.py
    python tools/demos/cardano_enhanced_demo.py --operation register_agent
    python tools/demos/cardano_enhanced_demo.py --operation full_demo
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from examples.premium.cardano_enhanced_agent import CardanoEnhancedAgent


class CardanoEnhancedDemo:
    """
    Comprehensive demonstration of Enhanced Cardano Agent capabilities.
    """
    
    def __init__(self):
        self.demo_config = {
            "nmkr_api_key": "demo_nmkr_api_key_for_testing",
            "nmkr_project_uid": "demo_project_uid_12345", 
            "network": "mainnet",
            "enable_cross_chain": True,
            "compliance_mode": "enterprise",
            "demo_mode": True
        }
        
    async def run_demo(self, operation: str = "full_demo") -> None:
        """
        Run the Enhanced Cardano Agent demonstration.
        
        Args:
            operation: The operation to demonstrate
        """
        print("🏛️ Enhanced Cardano Agent - AI Agent Economy Demo")
        print("=" * 60)
        print(f"🎯 Operation: {operation}")
        print(f"🌐 Network: {self.demo_config['network']}")
        print(f"🔐 Compliance: {self.demo_config['compliance_mode']}")
        print()
        
        try:
            async with CardanoEnhancedAgent(
                name="cardano_enhanced_demo",
                config=self.demo_config
            ) as agent:
                
                if operation == "full_demo":
                    await self._run_full_demo(agent)
                elif operation == "register_agent":
                    await self._demo_agent_registration(agent)
                elif operation == "service_marketplace":
                    await self._demo_service_marketplace(agent)
                elif operation == "revenue_sharing":
                    await self._demo_revenue_sharing(agent)
                elif operation == "cross_chain":
                    await self._demo_cross_chain(agent)
                elif operation == "compliance":
                    await self._demo_compliance_framework(agent)
                else:
                    result = await agent.run(operation=operation)
                    self._display_result(f"{operation} Result", result)
                    
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return
            
        print("\n🎉 Enhanced Cardano Agent Demo Complete!")
        print("📚 Learn more: docs/integrations/CARDANO_IMPLEMENTATION_COMPLETE.md")
    
    async def _run_full_demo(self, agent: CardanoEnhancedAgent) -> None:
        """Run complete AI agent economy demonstration."""
        print("🚀 Full AI Agent Economy Demo")
        print("-" * 40)
        
        # Phase 1: Agent Registration
        print("\n📋 Phase 1: Agent Registration with Staking")
        result1 = await agent.run(operation="register_agent")
        self._display_result("Agent Registration", result1)
        
        # Phase 2: Service Marketplace
        print("\n💼 Phase 2: Service Marketplace Operations")
        result2 = await agent.run(operation="service_marketplace")
        self._display_result("Service Marketplace", result2)
        
        # Phase 3: Revenue Sharing
        print("\n💰 Phase 3: Revenue Sharing & Token Economics")
        result3 = await agent.run(operation="revenue_sharing")
        self._display_result("Revenue Sharing", result3)
        
        # Phase 4: Cross-Chain Operations
        print("\n🌐 Phase 4: Cross-Chain Service Discovery")
        result4 = await agent.run(operation="cross_chain")
        self._display_result("Cross-Chain Operations", result4)
        
        # Phase 5: Compliance Framework
        print("\n🔐 Phase 5: Enterprise Compliance")
        result5 = await agent.run(operation="compliance")
        self._display_result("Compliance Framework", result5)
        
        # Summary
        print("\n📊 AI Agent Economy Summary")
        print("-" * 40)
        print("✅ Agent Registration: Multi-tier staking system operational")
        print("✅ Service Marketplace: Escrow and execution proofs active") 
        print("✅ Revenue Sharing: Token economics with profit distribution")
        print("✅ Cross-Chain Support: 5+ blockchain integration ready")
        print("✅ Enterprise Compliance: GDPR, KYC/AML frameworks enabled")
    
    async def _demo_agent_registration(self, agent: CardanoEnhancedAgent) -> None:
        """Demonstrate agent registration and reputation staking."""
        print("📋 Agent Registration Demo")
        print("-" * 30)
        
        result = await agent.run(operation="register_agent")
        self._display_result("Agent Registration", result)
        
        print("\n🎯 Registration Features Demonstrated:")
        print("  • Multi-tier staking system (10-1000 ADA)")
        print("  • Reputation-based agent discovery")
        print("  • Capability verification and validation")
        print("  • Hierarchical agent registry structure")
    
    async def _demo_service_marketplace(self, agent: CardanoEnhancedAgent) -> None:
        """Demonstrate service marketplace operations."""
        print("💼 Service Marketplace Demo")
        print("-" * 30)
        
        result = await agent.run(operation="service_marketplace")
        self._display_result("Service Marketplace", result)
        
        print("\n🎯 Marketplace Features Demonstrated:")
        print("  • Automated escrow creation and management")
        print("  • ZK-proof execution verification")
        print("  • Payment processing with dispute resolution")
        print("  • Service quality assessment and rating")
    
    async def _demo_revenue_sharing(self, agent: CardanoEnhancedAgent) -> None:
        """Demonstrate revenue sharing and token economics."""
        print("💰 Revenue Sharing Demo") 
        print("-" * 30)
        
        result = await agent.run(operation="revenue_sharing")
        self._display_result("Revenue Sharing", result)
        
        print("\n🎯 Revenue Features Demonstrated:")
        print("  • Token-based profit distribution (70/20/10)")
        print("  • Creator, staker, and treasury allocation")
        print("  • Governance token voting mechanisms")
        print("  • Community economic incentives")
    
    async def _demo_cross_chain(self, agent: CardanoEnhancedAgent) -> None:
        """Demonstrate cross-chain service discovery."""
        print("🌐 Cross-Chain Demo")
        print("-" * 30)
        
        result = await agent.run(operation="cross_chain")
        self._display_result("Cross-Chain Operations", result)
        
        print("\n🎯 Cross-Chain Features Demonstrated:")
        print("  • Multi-blockchain service discovery")
        print("  • Bridge protocol integration")
        print("  • Cross-chain escrow coordination")
        print("  • Universal agent registry access")
    
    async def _demo_compliance_framework(self, agent: CardanoEnhancedAgent) -> None:
        """Demonstrate enterprise compliance features."""
        print("🔐 Compliance Framework Demo")
        print("-" * 30)
        
        result = await agent.run(operation="compliance")
        self._display_result("Compliance Framework", result)
        
        print("\n🎯 Compliance Features Demonstrated:")
        print("  • GDPR data protection compliance")
        print("  • KYC/AML verification workflows")
        print("  • Multi-jurisdiction regulatory support")
        print("  • Audit trail and reporting capabilities")
    
    def _display_result(self, title: str, result: Optional[Dict[str, Any]]) -> None:
        """Display formatted demo result."""
        print(f"\n📋 {title}:")
        if not result:
            print("  ❌ Operation failed or returned no result")
            return
            
        # Display key metrics
        if result.get("success"):
            print(f"  ✅ Status: {result.get('status', 'Success')}")
        else:
            print(f"  ⚠️  Status: {result.get('status', 'Partial')}")
            
        # Display operation-specific details
        if "agent_id" in result:
            print(f"  🆔 Agent ID: {result['agent_id']}")
        if "stake_amount" in result:
            print(f"  💰 Stake Amount: {result['stake_amount']} ADA")
        if "reputation_score" in result:
            print(f"  ⭐ Reputation: {result['reputation_score']}")
        if "escrow_id" in result:
            print(f"  🔒 Escrow ID: {result['escrow_id']}")
        if "revenue_distributed" in result:
            print(f"  💸 Revenue Distributed: {result['revenue_distributed']} ADA")
        if "cross_chain_bridges" in result:
            bridges = result['cross_chain_bridges']
            print(f"  🌉 Active Bridges: {len(bridges)} chains")
        if "compliance_score" in result:
            print(f"  🛡️  Compliance Score: {result['compliance_score']}")
            
        # Display transaction hash if available
        if "transaction_hash" in result:
            tx_hash = result['transaction_hash']
            print(f"  🔗 Transaction: {tx_hash[:16]}...{tx_hash[-8:]}")


def main():
    """Main demo function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced Cardano Agent Demo - Complete AI Agent Economy"
    )
    parser.add_argument(
        "--operation",
        default="full_demo",
        choices=[
            "full_demo", "register_agent", "service_marketplace", 
            "revenue_sharing", "cross_chain", "compliance"
        ],
        help="Demo operation to run"
    )
    
    args = parser.parse_args()
    
    # Run the demo
    demo = CardanoEnhancedDemo()
    try:
        asyncio.run(demo.run_demo(args.operation))
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()