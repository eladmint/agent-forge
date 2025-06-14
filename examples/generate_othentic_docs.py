#!/usr/bin/env python3
"""
Generate Othentic AVS documentation using Documentation Manager Agent
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add agent_forge to path
current_dir = Path(__file__).parent
agent_forge_root = current_dir.parent  
sys.path.insert(0, str(agent_forge_root))

from examples.documentation_manager_agent import DocumentationManagerAgent, AIModel

async def generate_othentic_documentation():
    """Generate documentation for Othentic AVS integration"""
    
    print("🚀 Generating Othentic AVS Documentation")
    print("=" * 50)
    
    # Initialize agent
    agent = DocumentationManagerAgent()
    
    async with agent:
        print("✅ Documentation Manager Agent initialized")
        
        # Planning document paths
        planning_docs = [
            "/Users/eladm/Projects/token/tokenhunter/docs/architecture/blockchain/OTHENTIC_AVS_ARCHITECTURE_PLAN.md",
            "/Users/eladm/Projects/token/tokenhunter/docs/architecture/blockchain/MASUMI_INDEPENDENCE_STRATEGY.md",
            "/Users/eladm/Projects/token/tokenhunter/docs/architecture/blockchain/MULTI_CHAIN_PAYMENT_ARCHITECTURE.md"
        ]
        
        # Check which planning docs exist
        existing_docs = [doc for doc in planning_docs if os.path.exists(doc)]
        print(f"📋 Found {len(existing_docs)} planning documents")
        
        if not existing_docs:
            print("⚠️  No planning documents found, cannot generate documentation")
            return False
        
        # Target structure for Agent Forge docs
        target_structure = {
            "docs_root": "agent_forge/docs",
            "directories": ["blockchain", "payments", "compliance", "api"]
        }
        
        # Step 1: Dry run to show what would be generated
        print("\n📝 Step 1: Planning Documentation Generation")
        print("-" * 45)
        
        dry_result = await agent.run(
            task="update_documentation_set",
            planning_docs=existing_docs,
            target_structure=target_structure,
            ai_model="gemini-2.5",
            dry_run=True
        )
        
        print(f"✅ Plan created:")
        print(f"   - Plan ID: {dry_result['plan']['plan_id']}")
        print(f"   - Tasks: {dry_result['plan']['tasks_count']}")
        print(f"   - Estimated time: {dry_result['plan']['estimated_time']} minutes")
        
        if 'target_files' in dry_result['plan']:
            print(f"   - Files to generate:")
            for file in dry_result['plan']['target_files']:
                print(f"     • {file}")
        
        # Auto-approve for automated execution
        print(f"\n✅ Proceeding with documentation generation...")
        response = 'y'
        
        # Step 2: Generate documentation
        print("\n📄 Step 2: Generating Documentation")
        print("-" * 35)
        
        # Create target directories
        for directory in target_structure["directories"]:
            dir_path = f"agent_forge/docs/{directory}"
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")
        
        # Generate documentation
        result = await agent.run(
            task="update_documentation_set",
            planning_docs=existing_docs,
            target_structure=target_structure,
            ai_model="gemini-2.5",
            dry_run=False
        )
        
        # Display results
        print(f"\n✅ Documentation generation complete!")
        print(f"   - Successful tasks: {result['execution']['successful_tasks']}")
        print(f"   - Failed tasks: {result['execution']['failed_tasks']}")
        print(f"   - Average quality: {result['execution']['average_quality_score']:.2f}")
        print(f"   - Execution time: {result['execution']['total_execution_time']:.1f} seconds")
        
        if result['execution']['generated_files']:
            print(f"   - Generated files:")
            for file in result['execution']['generated_files']:
                if file and os.path.exists(file):
                    file_size = os.path.getsize(file)
                    print(f"     • {file} ({file_size:,} bytes)")
        
        # Step 3: Validate generated documentation
        print("\n🔍 Step 3: Validating Generated Documentation")
        print("-" * 45)
        
        validation_result = await agent.run(
            task="analyze_structure",
            docs_path="agent_forge/docs"
        )
        
        print(f"✅ Validation complete:")
        print(f"   - Total files: {validation_result.get('total_files', 0)}")
        print(f"   - Consistency issues: {len(validation_result.get('consistency_issues', []))}")
        
        if validation_result.get('consistency_issues'):
            print(f"   - Issues found:")
            for issue in validation_result['consistency_issues'][:3]:
                print(f"     • {issue}")
        
        print(f"\n🎉 Othentic AVS Documentation Generation Complete!")
        print("=" * 55)
        
        return True

async def main():
    """Main function"""
    try:
        success = await generate_othentic_documentation()
        
        if success:
            print(f"\n📊 Summary:")
            print(f"✅ Documentation generation successful")
            print(f"📁 Check agent_forge/docs/ for generated files")
            print(f"🔄 Ready for review and refinement")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Documentation generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)