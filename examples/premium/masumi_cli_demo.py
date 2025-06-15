#!/usr/bin/env python3
"""
Masumi CLI Demo

Command-line demonstration of Agent Forge + Masumi Network integration.
This script shows how to use the CLI to test Masumi integration.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.shared.masumi import MasumiBridgeAdapter, MasumiConfig
from examples.simple_navigation_agent import SimpleNavigationAgent
from examples.data_compiler_agent import DataCompilerAgent


async def demo_basic_integration(args):
    """Demo basic Masumi integration."""
    print("🚀 Agent Forge + Masumi Basic Integration Demo")
    print("=" * 50)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    # Create agent
    agent = SimpleNavigationAgent(url=args.url or "https://httpbin.org/html")
    wrapper = bridge.wrap_agent(agent, price_ada=args.price)
    
    print(f"🤖 Created agent: {wrapper.agent_did}")
    print(f"💰 Price: {wrapper.price_ada} ADA")
    
    # Execute with Masumi
    job_id = f"demo_{int(asyncio.get_event_loop().time())}"
    
    try:
        result = await wrapper.execute_with_masumi(
            job_id=job_id,
            url=args.url or "https://httpbin.org/html"
        )
        
        print("✅ Execution successful!")
        print(f"⏱️  Time: {result['execution_time']:.2f}s")
        print(f"🔐 Proof: {result['proof_hash'][:16]}...")
        print(f"📄 Result: {json.dumps(result['result'], indent=2)}")
        
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return False
    
    return True


async def demo_payment_workflow(args):
    """Demo payment verification workflow."""
    print("💰 Masumi Payment Workflow Demo")
    print("=" * 35)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    agent = SimpleNavigationAgent()
    wrapper = bridge.wrap_agent(agent, price_ada=args.price)
    
    job_id = f"payment_demo_{int(asyncio.get_event_loop().time())}"
    
    print(f"💳 Job ID: {job_id}")
    print(f"💵 Price: {wrapper.price_ada} ADA")
    
    try:
        # Simulate payment proof
        payment_proof = f"simulated_tx_{job_id}"
        
        result = await wrapper.execute_with_masumi(
            job_id=job_id,
            payment_proof=payment_proof,
            requester_did="did:cardano:demo_requester",
            url=args.url or "https://httpbin.org/json"
        )
        
        print("✅ Payment workflow completed!")
        print(f"✅ Payment verified: {result['payment_verified']}")
        print(f"🏆 Payment claimed: {result['payment_claimed']}")
        
    except Exception as e:
        print(f"❌ Payment workflow failed: {e}")
        return False
    
    return True


async def demo_multi_agent_workflow(args):
    """Demo multi-agent workflow."""
    print("🤖 Multi-Agent Workflow Demo")
    print("=" * 30)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    # Create multiple agents
    agents = [
        ("Navigator", SimpleNavigationAgent(), 2.0),
        ("Compiler", DataCompilerAgent(), 5.0)
    ]
    
    wrappers = []
    for name, agent, price in agents:
        wrapper = bridge.wrap_agent(agent, price_ada=price)
        wrappers.append((name, wrapper))
        print(f"🤖 Created {name}: {wrapper.agent_did[:20]}... ({price} ADA)")
    
    # Execute workflow
    workflow_id = f"multi_demo_{int(asyncio.get_event_loop().time())}"
    total_cost = 0.0
    
    for i, (name, wrapper) in enumerate(wrappers):
        job_id = f"{workflow_id}_task_{i+1}"
        
        print(f"\n⚡ Executing {name} (Task {i+1})")
        
        try:
            result = await wrapper.execute_with_masumi(
                job_id=job_id,
                url=args.url or "https://httpbin.org/html"
            )
            
            print(f"✅ {name} completed in {result['execution_time']:.2f}s")
            total_cost += wrapper.price_ada
            
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    print(f"\n🎯 Workflow completed!")
    print(f"💰 Total cost: {total_cost} ADA")
    
    return True


async def demo_health_check(args):
    """Demo health check functionality."""
    print("🏥 Masumi Services Health Check")
    print("=" * 32)
    
    config = MasumiConfig.for_testing()
    bridge = MasumiBridgeAdapter(config)
    
    health = await bridge.health_check()
    
    for service, status in health.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}: {'Healthy' if status else 'Unavailable'}")
    
    return all(health.values())


async def demo_config_info(args):
    """Show configuration information."""
    print("⚙️  Masumi Configuration Info")
    print("=" * 30)
    
    config = MasumiConfig.for_testing()
    config_dict = config.to_dict()
    
    print(json.dumps(config_dict, indent=2))
    
    print(f"\n📋 Validation: {'✅ Valid' if config.validate() else '❌ Invalid'}")
    
    return True


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Agent Forge + Masumi Network Integration Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python masumi_cli_demo.py basic --url https://example.com
  python masumi_cli_demo.py payment --price 10.0
  python masumi_cli_demo.py multi-agent --url https://news.ycombinator.com
  python masumi_cli_demo.py health
  python masumi_cli_demo.py config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Demo commands')
    
    # Basic integration demo
    basic_parser = subparsers.add_parser('basic', help='Basic integration demo')
    basic_parser.add_argument('--url', help='URL to navigate to')
    basic_parser.add_argument('--price', type=float, default=3.0, help='Agent price in ADA')
    
    # Payment workflow demo
    payment_parser = subparsers.add_parser('payment', help='Payment workflow demo')
    payment_parser.add_argument('--url', help='URL to navigate to')
    payment_parser.add_argument('--price', type=float, default=5.0, help='Agent price in ADA')
    
    # Multi-agent workflow demo
    multi_parser = subparsers.add_parser('multi-agent', help='Multi-agent workflow demo')
    multi_parser.add_argument('--url', help='URL to navigate to')
    
    # Health check
    subparsers.add_parser('health', help='Check Masumi services health')
    
    # Configuration info
    subparsers.add_parser('config', help='Show configuration information')
    
    return parser


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🌟 Agent Forge + Masumi Network Integration")
    print("=" * 50)
    print(f"Command: {args.command}")
    print(f"Timestamp: {asyncio.get_event_loop().time()}")
    print()
    
    # Route to appropriate demo function
    demos = {
        'basic': demo_basic_integration,
        'payment': demo_payment_workflow,
        'multi-agent': demo_multi_agent_workflow,
        'health': demo_health_check,
        'config': demo_config_info
    }
    
    demo_func = demos.get(args.command)
    if demo_func:
        try:
            success = await demo_func(args)
            if success:
                print(f"\n🎉 Demo '{args.command}' completed successfully!")
            else:
                print(f"\n💥 Demo '{args.command}' failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n💥 Demo '{args.command}' crashed: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())