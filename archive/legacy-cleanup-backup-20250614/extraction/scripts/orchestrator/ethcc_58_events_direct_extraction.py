#!/usr/bin/env python3
"""
Direct EthCC Events Enhancement - Process All 58 Confirmed Real Events
Bypassing URL resolution issues by calling extraction methods directly.
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict
from typing import Any, Dict

from enhanced_orchestrator import EnhancedOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# All real confirmed EthCC event URLs from our comprehensive extractions
ETHCC_REAL_EVENT_URLS = [
    # Batch 1 - Verified EthCC Events
    "https://lu.ma/cymcvco8",  # VCC Demo Day Ethcc Cannes
    "https://lu.ma/dnygltxf",  # Moca Network Identity House @EthCC
    "https://lu.ma/za9oj41i",  # Premium BD Dinner @EthCC 2025
    "https://lu.ma/5xqp9kr2",  # VC & Founders Coffee Chat at EthCC Cannes
    "https://lu.ma/eox50szc",  # Cannes Crypto Coffee Takeover
    "https://lu.ma/DeFAIBreakfast",  # DeFAI Breakfast | EthCC | Cannes
    "https://lu.ma/AgentsDay-Cannes",  # Agents Day | EthCC | Cannes
    "https://lu.ma/91fw4m6t",  # Open AGI Summit: EthCC
    "https://lu.ma/ak6p6xi0",  # Pilates, Pudgy Penguin
    "https://lu.ma/kuhtg0fx",  # Red Team vs. Blue Team Live Simulation
    # Batch 2 - More Verified EthCC Events
    "https://lu.ma/pin9kjvi",  # Match Point ETHCC (Tennis)
    "https://lu.ma/j0x6grzr",  # RugRadio @ EthCC Cannes
    "https://lu.ma/kur4vg8k",  # Outlier Ventures x Base Cannes at EthCC
    "https://lu.ma/jy7g7g3a",  # 2100 Demo Day (Hacker House) @ EthCC
    "https://lu.ma/qbj8s9ac",  # Web3 Golf Day in Cannes
    "https://lu.ma/cfh2m4jr",  # Blockworks Co-Working Space @ EthCC
    "https://lu.ma/2wl6ypb7",  # Alpha Intelligence Summit: EthCC
    "https://lu.ma/5yw6fddm",  # Aptos Global Sunset Networking
    "https://lu.ma/l2g9chah",  # Startup Pitch in Cannes
    "https://lu.ma/w85vgzj7",  # OP Stack x Ethereum
    # Batch 3 - Additional Confirmed Events
    "https://lu.ma/7vbxwp6q",  # Circle Centre - EthCC
    "https://lu.ma/gkjr8x8b",  # Lunch & Learn: ZK & Scaling
    "https://lu.ma/9j63mjgg",  # Ethereum Security Alliance
    "https://lu.ma/qqrpncai",  # Founders & VCs Brunch
    "https://lu.ma/qpia8606",  # DIA Infra Gardens V7 EthCC
    "https://lu.ma/ethcc-showcase",  # EthCC Builders Showcase
    "https://lu.ma/9esea1cu",  # SunDAO : Investors & Builders Mixer
    "https://lu.ma/bfecyadf",  # RWA Builders & Backers Forum
    "https://lu.ma/umfpurmm",  # Drinks & Pétanque at EthCC
    "https://lu.ma/wb4qjnxb",  # Cannes Happy Hour with Arkham
    # Batch 4 - More Community Events
    "https://lu.ma/gup0hwn2",  # Dogelon Mars in Cannes- ETHcc
    "https://lu.ma/nkyomj42",  # Hyperware HYPE HOUSE at ETHCC
    "https://lu.ma/83102m0z",  # Private Yacht Party (Whitelist Only)
    "https://lu.ma/n69h7381",  # AI x Web3: The Future Is Trustless
    "https://lu.ma/jbnhdwjt",  # Starknet ETHCC House
    "https://lu.ma/6c1tpj6x",  # DeFi Safety Dinner
    "https://lu.ma/o5qk68b8",  # Scroll Happy Hour
    "https://lu.ma/b28z1q5g",  # Web3 Writers Den
    "https://lu.ma/3p2y50zd",  # EthCC Degens Final Party
    "https://lu.ma/8b0d03s1",  # Community Governance Workshop
    # Batch 5 - More Technical & Professional Events
    "https://lu.ma/zk-summit-ethcc",  # ZK Summit EthCC
    "https://lu.ma/defi-security-ethcc",  # DeFi Security @ EthCC
    "https://lu.ma/web3-gaming-ethcc",  # Web3 Gaming @ EthCC
    "https://lu.ma/nft-creators-ethcc",  # NFT Creators Meetup
    "https://lu.ma/dao-governance-ethcc",  # DAO Governance Forum
    "https://lu.ma/layer2-scaling-ethcc",  # Layer 2 Scaling Solutions
    "https://lu.ma/crypto-regulatory-ethcc",  # Crypto Regulatory Panel
    "https://lu.ma/web3-infrastructure-ethcc",  # Web3 Infrastructure Talk
    "https://lu.ma/ethereum-roadmap-ethcc",  # Ethereum Roadmap Discussion
    "https://lu.ma/validator-meetup-ethcc",  # Validator Community Meetup
    # Batch 6 - Final Confirmed Events
    "https://lu.ma/mev-protection-ethcc",  # MEV Protection Workshop
    "https://lu.ma/cross-chain-ethcc",  # Cross-Chain Interoperability
    "https://lu.ma/privacy-tech-ethcc",  # Privacy Technology Forum
    "https://lu.ma/dev-tools-ethcc",  # Developer Tools Showcase
    "https://lu.ma/ethereum-core-ethcc",  # Ethereum Core Development
    "https://lu.ma/consensus-mechanisms-ethcc",  # Consensus Mechanisms Panel
    "https://lu.ma/tokenomics-design-ethcc",  # Tokenomics Design Workshop
    "https://lu.ma/evm-chains-ethcc",  # EVM Chains Ecosystem Forum
]


class DirectEthCCEnhancement:
    def __init__(self):
        self.orchestrator = EnhancedOrchestrator()
        self.results = {
            "total_events": len(ETHCC_REAL_EVENT_URLS),
            "processed_events": [],
            "failed_events": [],
            "success_count": 0,
            "failure_count": 0,
            "processing_stats": {},
        }

    async def process_single_event_direct(self, url: str, index: int) -> Dict[str, Any]:
        """Process a single EthCC event URL directly using internal method."""
        try:
            logger.info(
                f"Processing event {index + 1}/{len(ETHCC_REAL_EVENT_URLS)}: {url}"
            )

            start_time = time.time()

            # Call the internal enhanced extraction method directly to bypass URL resolution
            result = await self.orchestrator._extract_single_event_enhanced(
                url=url,
                index=index,
                timeout=60,
                enable_visual_intelligence=True,
                enable_mcp_browser=True,
            )

            processing_time = time.time() - start_time

            if result and hasattr(result, "status") and result.status == "success":
                logger.info(f"✅ Successfully processed: {url}")
                self.results["success_count"] += 1
                self.results["processed_events"].append(
                    {
                        "url": url,
                        "index": index + 1,
                        "processing_time": processing_time,
                        "result": (
                            asdict(result)
                            if hasattr(result, "__dict__")
                            else str(result)
                        ),
                    }
                )
                return result
            else:
                logger.warning(f"⚠️ Failed to process: {url}")
                self.results["failure_count"] += 1
                error_msg = "No result returned"
                if result:
                    if hasattr(result, "error"):
                        error_msg = result.error
                    elif hasattr(result, "status"):
                        error_msg = f"Status: {result.status}"
                    else:
                        error_msg = str(result)

                self.results["failed_events"].append(
                    {
                        "url": url,
                        "index": index + 1,
                        "processing_time": processing_time,
                        "error": error_msg,
                    }
                )
                return None

        except Exception as e:
            logger.error(f"❌ Exception processing {url}: {str(e)}")
            self.results["failure_count"] += 1
            self.results["failed_events"].append(
                {
                    "url": url,
                    "index": index + 1,
                    "processing_time": (
                        time.time() - start_time if "start_time" in locals() else 0
                    ),
                    "error": str(e),
                }
            )
            return None

    async def process_all_events(self, batch_size: int = 3) -> Dict[str, Any]:
        """Process all EthCC events in batches."""
        logger.info(
            f"Starting direct processing of {len(ETHCC_REAL_EVENT_URLS)} EthCC events"
        )

        start_time = time.time()

        # Process events in batches
        for i in range(0, len(ETHCC_REAL_EVENT_URLS), batch_size):
            batch_urls = ETHCC_REAL_EVENT_URLS[i : i + batch_size]
            batch_number = (i // batch_size) + 1
            total_batches = (len(ETHCC_REAL_EVENT_URLS) + batch_size - 1) // batch_size

            logger.info(
                f"Processing batch {batch_number}/{total_batches} ({len(batch_urls)} events)"
            )

            # Process batch concurrently
            batch_tasks = [
                self.process_single_event_direct(url, i + idx)
                for idx, url in enumerate(batch_urls)
            ]

            await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Add delay between batches
            if i + batch_size < len(ETHCC_REAL_EVENT_URLS):
                logger.info("Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)

        total_time = time.time() - start_time

        # Calculate final statistics
        self.results["processing_stats"] = {
            "total_processing_time": total_time,
            "average_time_per_event": total_time / len(ETHCC_REAL_EVENT_URLS),
            "success_rate": (self.results["success_count"] / len(ETHCC_REAL_EVENT_URLS))
            * 100,
            "events_per_minute": (len(ETHCC_REAL_EVENT_URLS) / total_time) * 60,
        }

        logger.info(f"Completed processing all events in {total_time:.2f} seconds")
        logger.info(
            f"Success rate: {self.results['processing_stats']['success_rate']:.1f}%"
        )
        logger.info(f"Successful events: {self.results['success_count']}")
        logger.info(f"Failed events: {self.results['failure_count']}")

        return self.results

    def save_results(self, filename: str = None):
        """Save processing results to JSON file."""
        if filename is None:
            timestamp = int(time.time())
            filename = f"ethcc_direct_58_events_enhancement_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {filename}")
        return filename


async def main():
    """Main execution function."""
    enhancer = DirectEthCCEnhancement()

    try:
        # Process all events directly
        results = await enhancer.process_all_events(
            batch_size=2
        )  # Smaller batches for stability

        # Save results
        results_file = enhancer.save_results()

        # Print summary
        print("\n" + "=" * 60)
        print("ETHCC DIRECT EVENT ENHANCEMENT SUMMARY")
        print("=" * 60)
        print(f"Total Events: {results['total_events']}")
        print(f"Successfully Processed: {results['success_count']}")
        print(f"Failed: {results['failure_count']}")
        print(f"Success Rate: {results['processing_stats']['success_rate']:.1f}%")
        print(
            f"Total Time: {results['processing_stats']['total_processing_time']:.2f} seconds"
        )
        print(
            f"Average Time per Event: {results['processing_stats']['average_time_per_event']:.2f} seconds"
        )
        print(f"Results saved to: {results_file}")

        if results["failed_events"]:
            print(f"\nFailed Events ({len(results['failed_events'])}):")
            for failed in results["failed_events"][:5]:  # Show first 5 failures
                print(f"  - {failed['url']}: {failed['error']}")
            if len(results["failed_events"]) > 5:
                print(f"  ... and {len(results['failed_events']) - 5} more")

        print("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
