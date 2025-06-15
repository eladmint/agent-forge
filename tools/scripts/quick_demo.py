"""
Quick Demo Runner - Fixed Import Version
=======================================

Simple demo runner that works without import issues.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent))

# Now we can import our demo
from examples.cardano_hackathon_demo import CardanoHackathonDemo
from live_presentation_demo import LivePresentationDemo

async def run_quick_test():
    """Run a quick test demo."""
    print("🚀 Quick Test Demo Starting...")
    
    # Use the live presentation demo (it's faster and works great)
    demo = LivePresentationDemo()
    results = await demo.run_live_demo()
    
    print(f"\n✅ Quick demo completed in {results['demo_time']:.1f} seconds!")
    return results

async def run_full_demo():
    """Run the full hackathon demo."""
    print("🚀 Full Hackathon Demo Starting...")
    
    # Initialize the full demo
    demo = CardanoHackathonDemo(
        nmkr_api_key=None,  # Demo mode
        testnet=True
    )
    
    # Use test images
    test_images = [
        "berlin_blockchain_week_main_stage.jpg",
        "sponsor_wall_cardano_nmkr.jpg", 
        "expo_hall_booths.jpg",
        "keynote_charles_hoskinson.jpg",
        "networking_area.jpg",
        "midnight_privacy_demo.jpg",
        "world_mobile_booth.jpg",
        "masumi_ai_showcase.jpg"
    ]
    
    # Run the complete demo
    results = await demo.run_complete_demo(test_images)
    
    print(f"\n✅ Full demo completed successfully!")
    return results

def main():
    """Main demo selector."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          🚀 AGENT FORGE - CARDANO HACKATHON DEMO 🚀           ║
║                                                               ║
║  Enterprise AI + Blockchain Verification = Future of Trust    ║
║                                                               ║
║  Berlin Blockchain Week 2025 | Masumi Track | $5,000 Prize    ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("\nFixed Import Version - Choose demo:")
    print("1. Quick Test Demo (Live Presentation Style)")
    print("2. Full Hackathon Demo (Complete Integration)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting Quick Test Demo...")
        results = asyncio.run(run_quick_test())
        print(f"Demo completed! Ready for hackathon presentation.")
        
    elif choice == "2":
        print("\n🚀 Starting Full Hackathon Demo...")
        results = asyncio.run(run_full_demo())
        print(f"Full demo completed! All systems ready.")
        
    elif choice == "3":
        print("\n👋 Exiting. Good luck at the hackathon!")
        sys.exit(0)
        
    else:
        print("\n❌ Invalid choice. Please run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()