"""
Masumi-Enabled Navigation Agent Example

This example demonstrates how to wrap an Agent Forge navigation agent
for integration with the Masumi Network using the bridge adapter.
"""

import asyncio
from typing import Optional, Dict, Any
import logging

from core.agents.base import AsyncContextAgent
from core.shared.masumi import MasumiBridgeAdapter, MasumiConfig


class MasumiNavigationAgent(AsyncContextAgent):
    """
    Enhanced navigation agent optimized for Masumi Network integration.
    
    This agent can navigate websites, extract content, and participate
    in the Masumi AI Agent Economy with verifiable execution proofs.
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        extraction_target: str = "title",
        **kwargs
    ):
        super().__init__(name="MasumiNavigationAgent", **kwargs)
        self.url = url
        self.extraction_target = extraction_target
        
    async def run(self, url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Navigate to URL and extract specified content.
        
        Args:
            url: Target URL to navigate to
            **kwargs: Additional parameters
            
        Returns:
            Extracted data with metadata
        """
        target_url = url or self.url
        
        if not target_url:
            self.logger.error("No URL provided for navigation")
            return {"error": "No URL provided", "success": False}
        
        self.logger.info(f"Starting navigation to: {target_url}")
        
        try:
            # Use Steel Browser integration for navigation
            response = await self.browser_client.navigate(target_url)
            
            if not response or not response.get('success'):
                return {
                    "error": "Navigation failed",
                    "url": target_url,
                    "success": False
                }
            
            # Extract requested data
            extracted_data = {
                "url": target_url,
                "success": True,
                "extraction_target": self.extraction_target,
                "timestamp": response.get('timestamp'),
            }
            
            # Extract different types of content based on target
            if self.extraction_target == "title":
                extracted_data["title"] = response.get('page_title', '')
                
            elif self.extraction_target == "content":
                extracted_data["content"] = response.get('content', '')
                extracted_data["content_length"] = len(extracted_data["content"])
                
            elif self.extraction_target == "metadata":
                extracted_data["metadata"] = {
                    "title": response.get('page_title', ''),
                    "status_code": response.get('status_code'),
                    "final_url": response.get('final_url', target_url),
                    "load_time": response.get('load_time')
                }
                
            elif self.extraction_target == "links":
                extracted_data["links"] = response.get('links', [])
                extracted_data["link_count"] = len(extracted_data["links"])
                
            else:
                # Default: return basic page info
                extracted_data.update({
                    "title": response.get('page_title', ''),
                    "content_preview": response.get('content', '')[:200] + "..."
                })
            
            self.logger.info(f"Successfully extracted {self.extraction_target} from {target_url}")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error during navigation: {e}")
            return {
                "error": str(e),
                "url": target_url,
                "success": False
            }


async def example_basic_masumi_integration():
    """Basic example of integrating Agent Forge with Masumi Network."""
    
    print("🚀 Agent Forge + Masumi Network Integration Example")
    print("=" * 50)
    
    # 1. Create configuration for testing
    config = MasumiConfig.for_testing()
    print(f"📡 Using Masumi network: {config.network}")
    print(f"💰 Payment service: {config.payment_service_url}")
    
    # 2. Initialize the bridge adapter
    bridge = MasumiBridgeAdapter(config)
    
    # 3. Create an Agent Forge agent
    navigation_agent = MasumiNavigationAgent(
        url="https://example.com",
        extraction_target="title"
    )
    
    # 4. Wrap the agent for Masumi compatibility
    wrapped_agent = bridge.wrap_agent(
        agent=navigation_agent,
        agent_did="did:cardano:example_navigation_agent",
        price_ada=3.0
    )
    
    print(f"🤖 Created wrapped agent with DID: {wrapped_agent.agent_did}")
    print(f"💵 Service price: {wrapped_agent.price_ada} ADA")
    
    # 5. Execute the agent with Masumi integration
    try:
        job_id = f"job_{asyncio.get_event_loop().time()}"
        
        print(f"⚡ Executing job: {job_id}")
        
        result = await wrapped_agent.execute_with_masumi(
            job_id=job_id,
            url="https://httpbin.org/html",  # Test URL
            extraction_target="title"
        )
        
        print(f"✅ Job completed successfully!")
        print(f"📊 Execution time: {result['execution_time']:.2f}s")
        print(f"🔐 Proof hash: {result['proof_hash'][:16]}...")
        print(f"📝 Decision logs: {result['decision_count']} entries")
        print(f"📄 Result: {result['result']}")
        
    except Exception as e:
        print(f"❌ Execution failed: {e}")
    
    print("\n🎯 Integration completed!")


async def example_masumi_payment_integration():
    """Example demonstrating payment verification and claiming."""
    
    print("💰 Masumi Payment Integration Example")
    print("=" * 40)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    # Create agent for blockchain verification task
    agent = MasumiNavigationAgent(extraction_target="metadata")
    wrapped_agent = bridge.wrap_agent(agent, price_ada=10.0)
    
    # Simulate payment workflow
    job_id = f"paid_job_{int(asyncio.get_event_loop().time())}"
    
    print(f"💳 Creating payment request for job: {job_id}")
    
    try:
        # In real scenario, payment_proof would come from actual transaction
        payment_proof = "simulated_tx_hash_12345"
        
        result = await wrapped_agent.execute_with_masumi(
            job_id=job_id,
            payment_proof=payment_proof,
            requester_did="did:cardano:test_requester",
            url="https://httpbin.org/json"
        )
        
        print(f"💎 Payment verified: {result['payment_verified']}")
        print(f"🏆 Payment claimed: {result['payment_claimed']}")
        print(f"🔐 Execution proof: {result['proof_hash'][:16]}...")
        
    except Exception as e:
        print(f"❌ Payment integration failed: {e}")


async def example_masumi_registry_integration():
    """Example demonstrating agent registry operations."""
    
    print("📋 Masumi Registry Integration Example")
    print("=" * 40)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    # Create and wrap multiple agents
    agents = [
        ("WebNavigator", MasumiNavigationAgent(extraction_target="title"), 2.0),
        ("ContentExtractor", MasumiNavigationAgent(extraction_target="content"), 5.0),
        ("LinkAnalyzer", MasumiNavigationAgent(extraction_target="links"), 3.0),
    ]
    
    print(f"🏗️ Registering {len(agents)} agents with Masumi...")
    
    for name, agent, price in agents:
        wrapped = bridge.wrap_agent(agent, price_ada=price)
        
        # Register with Masumi Network
        success = await bridge.register_agent_with_masumi(
            wrapper=wrapped,
            api_endpoint=f"https://my-agents.com/{name.lower()}",
            description=f"Agent Forge {name} for {agent.extraction_target} extraction"
        )
        
        if success:
            print(f"✅ Registered {name} (DID: {wrapped.agent_did[:20]}...)")
        else:
            print(f"❌ Failed to register {name}")
    
    # Discover agents
    print("\n🔍 Discovering Agent Forge agents in Masumi Network...")
    discovered = await bridge.discover_masumi_agents(
        capabilities=["web_navigation"],
        framework="Agent Forge"
    )
    
    print(f"Found {len(discovered)} Agent Forge agents:")
    for agent_info in discovered:
        print(f"  - {agent_info.get('name', 'Unknown')} ({agent_info.get('pricing', {}).get('amount', 0)} ADA)")


async def example_health_check():
    """Example health check of Masumi services."""
    
    print("🏥 Masumi Services Health Check")
    print("=" * 30)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    health = await bridge.health_check()
    
    for service, status in health.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}: {'Healthy' if status else 'Unavailable'}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("🌟 Agent Forge + Masumi Network Integration Examples")
    print("=" * 60)
    
    # Run examples
    examples = [
        ("Basic Integration", example_basic_masumi_integration),
        ("Payment Integration", example_masumi_payment_integration),
        ("Registry Integration", example_masumi_registry_integration),
        ("Health Check", example_health_check),
    ]
    
    async def run_all_examples():
        for name, example_func in examples:
            print(f"\n🎯 Running: {name}")
            print("-" * 30)
            try:
                await example_func()
            except Exception as e:
                print(f"❌ Example failed: {e}")
            print("-" * 30)
    
    # Run the examples
    asyncio.run(run_all_examples())