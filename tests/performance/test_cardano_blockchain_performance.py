"""
Performance tests for Cardano blockchain operations

Tests the performance characteristics of:
- NFT minting operations under load
- Agent registration throughput
- Service marketplace transaction speed
- Revenue distribution scalability
- Cross-chain operation latency
- Memory usage and resource optimization
"""

import pytest
import asyncio
import time
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import statistics
import json

# Import classes for performance testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from examples.cardano_enhanced_agent import CardanoEnhancedAgent
from core.blockchain.cardano_enhanced_client import (
    EnhancedCardanoClient,
    AgentProfile,
    ServiceRequest,
    RevenueShare
)
from core.blockchain.nmkr_integration import ExecutionProof


class PerformanceMetrics:
    """Helper class for collecting and analyzing performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "operation_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "throughput": [],
            "error_rates": [],
            "latency_percentiles": {}
        }
    
    def record_operation(self, operation_name: str, start_time: float, end_time: float, 
                        success: bool = True, memory_mb: float = 0, cpu_percent: float = 0):
        """Record performance metrics for an operation."""
        duration = end_time - start_time
        
        self.metrics["operation_times"].append({
            "operation": operation_name,
            "duration": duration,
            "success": success,
            "timestamp": start_time
        })
        
        if memory_mb > 0:
            self.metrics["memory_usage"].append(memory_mb)
        
        if cpu_percent > 0:
            self.metrics["cpu_usage"].append(cpu_percent)
    
    def calculate_throughput(self, total_operations: int, total_time: float) -> float:
        """Calculate operations per second."""
        return total_operations / total_time if total_time > 0 else 0
    
    def get_latency_percentiles(self, operation_name: str = None) -> dict:
        """Calculate latency percentiles for operations."""
        if operation_name:
            durations = [
                op["duration"] for op in self.metrics["operation_times"]
                if op["operation"] == operation_name and op["success"]
            ]
        else:
            durations = [
                op["duration"] for op in self.metrics["operation_times"]
                if op["success"]
            ]
        
        if not durations:
            return {}
        
        return {
            "p50": statistics.median(durations),
            "p90": statistics.quantiles(durations, n=10)[8] if len(durations) >= 10 else max(durations),
            "p95": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations),
            "p99": statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else max(durations),
            "min": min(durations),
            "max": max(durations),
            "avg": statistics.mean(durations),
            "count": len(durations)
        }
    
    def get_error_rate(self, operation_name: str = None) -> float:
        """Calculate error rate for operations."""
        if operation_name:
            operations = [
                op for op in self.metrics["operation_times"]
                if op["operation"] == operation_name
            ]
        else:
            operations = self.metrics["operation_times"]
        
        if not operations:
            return 0.0
        
        errors = sum(1 for op in operations if not op["success"])
        return errors / len(operations)
    
    def get_summary(self) -> dict:
        """Get comprehensive performance summary."""
        return {
            "total_operations": len(self.metrics["operation_times"]),
            "latency_percentiles": self.get_latency_percentiles(),
            "error_rate": self.get_error_rate(),
            "avg_memory_mb": statistics.mean(self.metrics["memory_usage"]) if self.metrics["memory_usage"] else 0,
            "max_memory_mb": max(self.metrics["memory_usage"]) if self.metrics["memory_usage"] else 0,
            "avg_cpu_percent": statistics.mean(self.metrics["cpu_usage"]) if self.metrics["cpu_usage"] else 0,
            "max_cpu_percent": max(self.metrics["cpu_usage"]) if self.metrics["cpu_usage"] else 0
        }


class TestCardanoBlockchainPerformance:
    """Performance tests for Cardano blockchain operations."""
    
    @pytest.fixture
    def performance_config(self):
        """Create configuration optimized for performance testing."""
        return {
            "agent_id": "performance_test_agent",
            "owner_address": "addr1_performance_test",
            "nmkr_api_key": "performance_test_key",
            "blockfrost_project_id": "performance_test_project",
            "connection_pool_size": 20,
            "request_timeout": 10.0,
            "retry_attempts": 3
        }
    
    @pytest.fixture
    def performance_metrics(self):
        """Create performance metrics collector."""
        return PerformanceMetrics()
    
    @pytest.fixture
    async def optimized_client_setup(self, performance_config):
        """Setup optimized client for performance testing."""
        with patch('src.core.blockchain.cardano_enhanced_client.NMKRClient') as mock_nmkr:
            # Setup high-performance mock client
            mock_nmkr_instance = AsyncMock()
            mock_nmkr.return_value = mock_nmkr_instance
            
            # Mock fast responses
            mock_nmkr_instance.mint_nft.return_value = {
                "transaction_id": f"tx_perf_{int(time.time() * 1000)}",
                "status": "success",
                "processing_time": 0.1
            }
            
            client = EnhancedCardanoClient(
                nmkr_api_key=performance_config["nmkr_api_key"],
                blockfrost_project_id=performance_config["blockfrost_project_id"],
                policy_id="performance_test_policy"
            )
            client.nmkr_client = mock_nmkr_instance
            
            yield client, mock_nmkr_instance
    
    @pytest.mark.asyncio
    async def test_nft_minting_throughput(self, optimized_client_setup, performance_metrics):
        """Test NFT minting throughput under high load."""
        client, mock_nmkr = optimized_client_setup
        
        print("\n⚡ Testing NFT Minting Throughput")
        
        # Test parameters
        num_mints = 100
        concurrent_batches = 10
        batch_size = num_mints // concurrent_batches
        
        print(f"🎯 Target: {num_mints} NFT mints in {concurrent_batches} concurrent batches")
        
        async def mint_nft_batch(batch_id: int, batch_size: int):
            """Mint a batch of NFTs concurrently."""
            batch_results = []
            
            for i in range(batch_size):
                start_time = time.time()
                memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                try:
                    # Create test profile
                    profile = AgentProfile(
                        owner_address=f"addr1_batch_{batch_id}_mint_{i}",
                        agent_id=f"perf_agent_{batch_id}_{i}",
                        metadata_uri=f"ipfs://QmPerfTest{batch_id}{i}",
                        staked_amount=100.0,
                        reputation_score=0.8,
                        capabilities=["performance_test"],
                        total_executions=0,
                        successful_executions=0
                    )
                    
                    # Execute registration (includes NFT minting)
                    result = await client.register_agent(profile, 100.0)
                    
                    end_time = time.time()
                    memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    # Record metrics
                    performance_metrics.record_operation(
                        "nft_mint",
                        start_time,
                        end_time,
                        success=(result["status"] == "success"),
                        memory_mb=memory_after - memory_before
                    )
                    
                    batch_results.append({
                        "batch_id": batch_id,
                        "mint_id": i,
                        "result": result,
                        "duration": end_time - start_time
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    performance_metrics.record_operation(
                        "nft_mint",
                        start_time,
                        end_time,
                        success=False
                    )
                    
                    batch_results.append({
                        "batch_id": batch_id,
                        "mint_id": i,
                        "error": str(e),
                        "duration": end_time - start_time
                    })
            
            return batch_results
        
        # Execute concurrent batches
        start_time = time.time()
        
        batch_tasks = [
            mint_nft_batch(batch_id, batch_size)
            for batch_id in range(concurrent_batches)
        ]
        
        batch_results = await asyncio.gather(*batch_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Flatten results
        all_results = [mint for batch in batch_results for mint in batch]
        successful_mints = [r for r in all_results if "result" in r and r["result"]["status"] == "success"]
        failed_mints = [r for r in all_results if "error" in r or ("result" in r and r["result"]["status"] != "success")]
        
        # Calculate performance metrics
        throughput = len(successful_mints) / total_time
        success_rate = len(successful_mints) / len(all_results)
        
        latency_stats = performance_metrics.get_latency_percentiles("nft_mint")
        
        performance_results = {
            "total_mints": len(all_results),
            "successful_mints": len(successful_mints),
            "failed_mints": len(failed_mints),
            "success_rate": success_rate,
            "total_time": total_time,
            "throughput_per_second": throughput,
            "latency_stats": latency_stats,
            "concurrent_batches": concurrent_batches,
            "batch_size": batch_size
        }
        
        # Performance assertions
        assert success_rate >= 0.95  # 95% success rate minimum
        assert throughput >= 10.0    # Minimum 10 mints per second
        assert latency_stats["p95"] <= 2.0  # 95th percentile under 2 seconds
        
        print(f"✅ NFT Minting Performance:")
        print(f"   📊 Throughput: {throughput:.1f} mints/sec")
        print(f"   ✅ Success Rate: {success_rate:.1%}")
        print(f"   ⏱️ P95 Latency: {latency_stats['p95']:.3f}s")
        
        return performance_results
    
    @pytest.mark.asyncio
    async def test_agent_registration_scalability(self, optimized_client_setup, performance_metrics):
        """Test agent registration scalability with increasing load."""
        client, mock_nmkr = optimized_client_setup
        
        print("\n📈 Testing Agent Registration Scalability")
        
        # Scalability test with increasing load
        load_levels = [10, 25, 50, 100, 200]
        scalability_results = []
        
        for load_level in load_levels:
            print(f"🔄 Testing load level: {load_level} concurrent registrations")
            
            start_time = time.time()
            memory_start = psutil.Process().memory_info().rss / 1024 / 1024
            
            async def register_agent_load_test(agent_index: int):
                """Register agent under load test."""
                operation_start = time.time()
                
                try:
                    profile = AgentProfile(
                        owner_address=f"addr1_scale_test_{agent_index}",
                        agent_id=f"scale_agent_{load_level}_{agent_index}",
                        metadata_uri=f"ipfs://QmScaleTest{agent_index}",
                        staked_amount=100.0 + (agent_index % 5) * 100,  # Vary stakes
                        reputation_score=0.7 + (agent_index % 3) * 0.1,
                        capabilities=["scalability_test", f"level_{load_level}"],
                        total_executions=agent_index,
                        successful_executions=agent_index
                    )
                    
                    result = await client.register_agent(profile, profile.staked_amount)
                    
                    operation_end = time.time()
                    performance_metrics.record_operation(
                        f"agent_registration_load_{load_level}",
                        operation_start,
                        operation_end,
                        success=(result["status"] == "success")
                    )
                    
                    return {"success": True, "result": result}
                    
                except Exception as e:
                    operation_end = time.time()
                    performance_metrics.record_operation(
                        f"agent_registration_load_{load_level}",
                        operation_start,
                        operation_end,
                        success=False
                    )
                    
                    return {"success": False, "error": str(e)}
            
            # Execute concurrent registrations
            registration_tasks = [
                register_agent_load_test(i)
                for i in range(load_level)
            ]
            
            registration_results = await asyncio.gather(*registration_tasks, return_exceptions=True)
            
            end_time = time.time()
            memory_end = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Analyze results
            successful_registrations = sum(
                1 for r in registration_results 
                if isinstance(r, dict) and r.get("success", False)
            )
            
            load_duration = end_time - start_time
            load_throughput = successful_registrations / load_duration
            memory_delta = memory_end - memory_start
            
            latency_stats = performance_metrics.get_latency_percentiles(f"agent_registration_load_{load_level}")
            
            scalability_result = {
                "load_level": load_level,
                "successful_registrations": successful_registrations,
                "total_registrations": load_level,
                "success_rate": successful_registrations / load_level,
                "duration": load_duration,
                "throughput": load_throughput,
                "memory_delta_mb": memory_delta,
                "latency_stats": latency_stats
            }
            
            scalability_results.append(scalability_result)
            
            print(f"   ✅ Load {load_level}: {load_throughput:.1f} reg/sec, "
                  f"{scalability_result['success_rate']:.1%} success, "
                  f"{memory_delta:.1f}MB memory")
            
            # Brief pause between load levels
            await asyncio.sleep(0.5)
            gc.collect()  # Force garbage collection
        
        # Analyze scalability characteristics
        throughputs = [r["throughput"] for r in scalability_results]
        load_levels_tested = [r["load_level"] for r in scalability_results]
        
        # Check for linear scalability (should not degrade significantly)
        throughput_efficiency = throughputs[-1] / throughputs[0] if throughputs[0] > 0 else 0
        
        scalability_summary = {
            "load_levels_tested": load_levels_tested,
            "throughput_range": {"min": min(throughputs), "max": max(throughputs)},
            "throughput_efficiency": throughput_efficiency,
            "scalability_results": scalability_results,
            "memory_growth_linear": all(
                r["memory_delta_mb"] < r["load_level"] * 2  # Less than 2MB per agent
                for r in scalability_results
            )
        }
        
        # Performance assertions
        assert throughput_efficiency >= 0.7  # At least 70% efficiency at high load
        assert all(r["success_rate"] >= 0.9 for r in scalability_results)  # 90% success at all loads
        assert scalability_summary["memory_growth_linear"]  # Linear memory growth
        
        print(f"✅ Scalability Test Results:")
        print(f"   📊 Throughput Range: {min(throughputs):.1f} - {max(throughputs):.1f} reg/sec")
        print(f"   ⚡ Efficiency: {throughput_efficiency:.1%}")
        
        return scalability_summary
    
    @pytest.mark.asyncio
    async def test_service_marketplace_transaction_speed(self, optimized_client_setup, performance_metrics):
        """Test service marketplace transaction processing speed."""
        client, mock_nmkr = optimized_client_setup
        
        print("\n🏪 Testing Service Marketplace Transaction Speed")
        
        # Setup test agents in registry
        test_agents = []
        for i in range(10):
            profile = AgentProfile(
                owner_address=f"addr1_marketplace_agent_{i}",
                agent_id=f"marketplace_agent_{i}",
                metadata_uri=f"ipfs://QmMarketplace{i}",
                staked_amount=500.0,
                reputation_score=0.8 + (i % 3) * 0.05,
                capabilities=["marketplace_test", "transaction_speed"],
                total_executions=i * 10,
                successful_executions=i * 9
            )
            client.agent_registry[profile.agent_id] = profile
            test_agents.append(profile)
        
        # Test parameters
        num_transactions = 200
        concurrent_transactions = 20
        
        print(f"🎯 Target: {num_transactions} marketplace transactions with {concurrent_transactions} concurrent")
        
        async def execute_marketplace_transaction(tx_id: int):
            """Execute a complete marketplace transaction."""
            start_time = time.time()
            
            try:
                # 1. Service Discovery
                discovery_start = time.time()
                agents = await client.find_agents(
                    capabilities=["marketplace_test"],
                    min_reputation=0.7,
                    max_agents=5
                )
                discovery_end = time.time()
                
                performance_metrics.record_operation(
                    "service_discovery",
                    discovery_start,
                    discovery_end,
                    success=len(agents) > 0
                )
                
                if not agents:
                    raise Exception("No agents found")
                
                # 2. Create Service Request
                selected_agent = agents[0]
                service_request = ServiceRequest(
                    requester_address=f"addr1_requester_{tx_id}",
                    agent_id=selected_agent["agent_id"],
                    service_hash=f"marketplace_tx_{tx_id}",
                    payment_amount=25.0 + (tx_id % 5) * 10,
                    escrow_deadline=(datetime.now() + timedelta(hours=24)).isoformat(),
                    task_description=f"Marketplace transaction test {tx_id}"
                )
                
                # 3. Create Escrow
                escrow_start = time.time()
                escrow_result = await client.create_escrow(service_request)
                escrow_end = time.time()
                
                performance_metrics.record_operation(
                    "escrow_creation",
                    escrow_start,
                    escrow_end,
                    success=(escrow_result["status"] == "success")
                )
                
                if escrow_result["status"] != "success":
                    raise Exception(f"Escrow creation failed: {escrow_result}")
                
                # 4. Simulate Service Execution
                execution_proof = ExecutionProof(
                    agent_id=selected_agent["agent_id"],
                    execution_id=f"exec_{tx_id}",
                    timestamp=datetime.now().isoformat(),
                    task_completed=True,
                    execution_time=1.5,
                    results={"transaction_test": "completed"},
                    metadata={"test_id": tx_id}
                )
                
                # 5. Release Escrow
                release_start = time.time()
                release_result = await client.release_escrow(
                    escrow_result["escrow_id"],
                    execution_proof
                )
                release_end = time.time()
                
                performance_metrics.record_operation(
                    "escrow_release",
                    release_start,
                    release_end,
                    success=(release_result["status"] == "success")
                )
                
                end_time = time.time()
                
                performance_metrics.record_operation(
                    "complete_marketplace_transaction",
                    start_time,
                    end_time,
                    success=True
                )
                
                return {
                    "tx_id": tx_id,
                    "success": True,
                    "duration": end_time - start_time,
                    "components": {
                        "discovery": discovery_end - discovery_start,
                        "escrow_creation": escrow_end - escrow_start,
                        "escrow_release": release_end - release_start
                    }
                }
                
            except Exception as e:
                end_time = time.time()
                
                performance_metrics.record_operation(
                    "complete_marketplace_transaction",
                    start_time,
                    end_time,
                    success=False
                )
                
                return {
                    "tx_id": tx_id,
                    "success": False,
                    "error": str(e),
                    "duration": end_time - start_time
                }
        
        # Execute transactions in batches for concurrency control
        batch_size = concurrent_transactions
        batches = [
            list(range(i, min(i + batch_size, num_transactions)))
            for i in range(0, num_transactions, batch_size)
        ]
        
        start_time = time.time()
        all_results = []
        
        for batch_idx, batch in enumerate(batches):
            print(f"   🔄 Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} transactions)")
            
            batch_tasks = [execute_marketplace_transaction(tx_id) for tx_id in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
            
            # Brief pause between batches
            await asyncio.sleep(0.1)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_transactions = [r for r in all_results if r["success"]]
        failed_transactions = [r for r in all_results if not r["success"]]
        
        # Component performance analysis
        component_stats = {}
        for component in ["discovery", "escrow_creation", "escrow_release"]:
            component_times = [
                r["components"][component] for r in successful_transactions
                if "components" in r and component in r["components"]
            ]
            if component_times:
                component_stats[component] = {
                    "avg": statistics.mean(component_times),
                    "p95": statistics.quantiles(component_times, n=20)[18] if len(component_times) >= 20 else max(component_times),
                    "min": min(component_times),
                    "max": max(component_times)
                }
        
        transaction_performance = {
            "total_transactions": len(all_results),
            "successful_transactions": len(successful_transactions),
            "failed_transactions": len(failed_transactions),
            "success_rate": len(successful_transactions) / len(all_results),
            "total_time": total_time,
            "throughput": len(successful_transactions) / total_time,
            "latency_stats": performance_metrics.get_latency_percentiles("complete_marketplace_transaction"),
            "component_performance": component_stats,
            "concurrent_transactions": concurrent_transactions
        }
        
        # Performance assertions
        assert transaction_performance["success_rate"] >= 0.95  # 95% success rate
        assert transaction_performance["throughput"] >= 15.0    # 15 transactions per second
        assert transaction_performance["latency_stats"]["p95"] <= 3.0  # P95 under 3 seconds
        
        print(f"✅ Marketplace Transaction Performance:")
        print(f"   📊 Throughput: {transaction_performance['throughput']:.1f} tx/sec")
        print(f"   ✅ Success Rate: {transaction_performance['success_rate']:.1%}")
        print(f"   ⏱️ P95 Latency: {transaction_performance['latency_stats']['p95']:.3f}s")
        
        return transaction_performance
    
    @pytest.mark.asyncio
    async def test_revenue_distribution_performance(self, optimized_client_setup, performance_metrics):
        """Test revenue distribution performance with large number of participants."""
        client, mock_nmkr = optimized_client_setup
        
        print("\n💰 Testing Revenue Distribution Performance")
        
        # Setup large number of revenue share participants
        participant_counts = [100, 500, 1000, 2000]
        distribution_results = []
        
        for participant_count in participant_counts:
            print(f"🎯 Testing {participant_count} revenue share participants")
            
            # Setup participants
            setup_start = time.time()
            
            client.revenue_shares = {}
            total_tokens = 0
            
            for i in range(participant_count):
                tokens = 100 + (i % 10) * 50  # Vary token amounts
                total_tokens += tokens
                
                client.revenue_shares[f"addr1_participant_{i}"] = RevenueShare(
                    recipient_address=f"addr1_participant_{i}",
                    participation_tokens=tokens,
                    accumulated_rewards=0.0,
                    last_claim_block=0,
                    contribution_score=0.7 + (i % 10) * 0.03
                )
            
            setup_end = time.time()
            setup_time = setup_end - setup_start
            
            # Test revenue distribution
            distribution_start = time.time()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            
            total_revenue = 10000.0  # 10,000 ADA to distribute
            
            distribution_result = await client.distribute_revenue(
                total_revenue=total_revenue,
                distribution_period=f"perf_test_{participant_count}"
            )
            
            distribution_end = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            distribution_time = distribution_end - distribution_start
            memory_delta = memory_after - memory_before
            
            performance_metrics.record_operation(
                f"revenue_distribution_{participant_count}",
                distribution_start,
                distribution_end,
                success=(distribution_result["status"] == "success"),
                memory_mb=memory_delta
            )
            
            # Test reward claiming performance
            claim_start = time.time()
            claim_count = min(50, participant_count)  # Test first 50 claims
            claim_results = []
            
            for i in range(claim_count):
                address = f"addr1_participant_{i}"
                claim_result = await client.claim_rewards(address)
                claim_results.append(claim_result)
            
            claim_end = time.time()
            claim_time = claim_end - claim_start
            claim_throughput = claim_count / claim_time if claim_time > 0 else 0
            
            # Analyze distribution performance
            participants_per_second = participant_count / distribution_time if distribution_time > 0 else 0
            
            result = {
                "participant_count": participant_count,
                "setup_time": setup_time,
                "distribution_time": distribution_time,
                "participants_per_second": participants_per_second,
                "memory_delta_mb": memory_delta,
                "claim_testing": {
                    "claims_tested": claim_count,
                    "claim_time": claim_time,
                    "claim_throughput": claim_throughput,
                    "successful_claims": sum(1 for r in claim_results if r["status"] == "success")
                },
                "total_revenue": total_revenue,
                "total_tokens": total_tokens,
                "distribution_success": distribution_result["status"] == "success"
            }
            
            distribution_results.append(result)
            
            print(f"   ✅ {participant_count} participants: {participants_per_second:.1f} dist/sec, "
                  f"{claim_throughput:.1f} claims/sec, {memory_delta:.1f}MB")
            
            # Cleanup for next test
            client.revenue_shares = {}
            gc.collect()
            await asyncio.sleep(0.2)
        
        # Analyze scalability
        distribution_summary = {
            "participant_counts": participant_counts,
            "distribution_results": distribution_results,
            "performance_degradation": {
                "linear_scaling": all(
                    r["participants_per_second"] >= 100  # Minimum 100 participants/sec
                    for r in distribution_results
                ),
                "memory_efficiency": all(
                    r["memory_delta_mb"] < r["participant_count"] * 0.1  # Less than 0.1MB per participant
                    for r in distribution_results
                )
            }
        }
        
        # Performance assertions
        assert distribution_summary["performance_degradation"]["linear_scaling"]
        assert distribution_summary["performance_degradation"]["memory_efficiency"]
        assert all(r["distribution_success"] for r in distribution_results)
        
        print(f"✅ Revenue Distribution Performance Verified:")
        print(f"   📊 Handled up to {max(participant_counts)} participants")
        print(f"   ⚡ Maintained >100 distributions/sec at scale")
        
        return distribution_summary
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self, optimized_client_setup, performance_metrics):
        """Test memory usage patterns and optimization."""
        client, mock_nmkr = optimized_client_setup
        
        print("\n🧠 Testing Memory Usage Optimization")
        
        # Memory usage test scenarios
        test_scenarios = [
            {"name": "agent_registry_growth", "operations": 500},
            {"name": "service_requests_accumulation", "operations": 300},
            {"name": "revenue_shares_expansion", "operations": 1000}
        ]
        
        memory_results = {}
        
        for scenario in test_scenarios:
            print(f"🔍 Testing {scenario['name']} with {scenario['operations']} operations")
            
            # Initial memory measurement
            gc.collect()  # Force garbage collection
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            memory_samples = [initial_memory]
            operation_count = 0
            
            if scenario["name"] == "agent_registry_growth":
                # Test agent registry memory usage
                for i in range(scenario["operations"]):
                    profile = AgentProfile(
                        owner_address=f"addr1_memory_test_agent_{i}",
                        agent_id=f"memory_test_agent_{i}",
                        metadata_uri=f"ipfs://QmMemoryTest{i}",
                        staked_amount=100.0,
                        reputation_score=0.8,
                        capabilities=[f"memory_test_{i % 10}"],
                        total_executions=i,
                        successful_executions=i
                    )
                    
                    client.agent_registry[profile.agent_id] = profile
                    operation_count += 1
                    
                    # Sample memory every 50 operations
                    if operation_count % 50 == 0:
                        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                        memory_samples.append(current_memory)
            
            elif scenario["name"] == "service_requests_accumulation":
                # Test service requests memory usage
                for i in range(scenario["operations"]):
                    service_request = ServiceRequest(
                        requester_address=f"addr1_memory_test_requester_{i}",
                        agent_id=f"memory_test_agent_{i % 10}",
                        service_hash=f"memory_test_service_{i}",
                        payment_amount=25.0,
                        escrow_deadline=datetime.now().isoformat(),
                        task_description=f"Memory test service {i}"
                    )
                    
                    request_id = service_request.generate_hash()
                    client.service_requests[request_id] = service_request
                    operation_count += 1
                    
                    # Sample memory every 30 operations
                    if operation_count % 30 == 0:
                        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                        memory_samples.append(current_memory)
            
            elif scenario["name"] == "revenue_shares_expansion":
                # Test revenue shares memory usage
                for i in range(scenario["operations"]):
                    client.revenue_shares[f"addr1_memory_test_participant_{i}"] = RevenueShare(
                        recipient_address=f"addr1_memory_test_participant_{i}",
                        participation_tokens=100 + i,
                        accumulated_rewards=float(i),
                        last_claim_block=i,
                        contribution_score=0.8
                    )
                    operation_count += 1
                    
                    # Sample memory every 100 operations
                    if operation_count % 100 == 0:
                        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                        memory_samples.append(current_memory)
            
            # Final memory measurement
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_samples.append(final_memory)
            
            # Calculate memory growth
            memory_growth = final_memory - initial_memory
            memory_per_operation = memory_growth / scenario["operations"]
            
            # Check for memory leaks (linear vs exponential growth)
            memory_growth_rate = []
            for i in range(1, len(memory_samples)):
                growth_rate = memory_samples[i] - memory_samples[i-1]
                memory_growth_rate.append(growth_rate)
            
            avg_growth_rate = statistics.mean(memory_growth_rate) if memory_growth_rate else 0
            growth_consistency = statistics.stdev(memory_growth_rate) if len(memory_growth_rate) > 1 else 0
            
            memory_results[scenario["name"]] = {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "memory_per_operation_kb": memory_per_operation * 1024,
                "operations": scenario["operations"],
                "memory_samples": memory_samples,
                "avg_growth_rate": avg_growth_rate,
                "growth_consistency": growth_consistency,
                "linear_growth": growth_consistency < avg_growth_rate * 0.5  # Consistent growth pattern
            }
            
            print(f"   📊 {scenario['name']}: {memory_growth:.1f}MB total, "
                  f"{memory_per_operation * 1024:.2f}KB per operation")
            
            # Cleanup for next scenario
            if scenario["name"] == "agent_registry_growth":
                client.agent_registry = {}
            elif scenario["name"] == "service_requests_accumulation":
                client.service_requests = {}
            elif scenario["name"] == "revenue_shares_expansion":
                client.revenue_shares = {}
            
            gc.collect()
            await asyncio.sleep(0.1)
        
        # Overall memory efficiency analysis
        memory_efficiency = {
            "scenarios_tested": len(test_scenarios),
            "memory_results": memory_results,
            "efficiency_metrics": {
                "max_memory_per_operation_kb": max(
                    r["memory_per_operation_kb"] for r in memory_results.values()
                ),
                "linear_growth_maintained": all(
                    r["linear_growth"] for r in memory_results.values()
                ),
                "memory_leak_detected": any(
                    r["memory_growth_mb"] > r["operations"] * 0.01  # More than 10KB per operation
                    for r in memory_results.values()
                )
            }
        }
        
        # Performance assertions
        assert memory_efficiency["efficiency_metrics"]["linear_growth_maintained"]
        assert not memory_efficiency["efficiency_metrics"]["memory_leak_detected"]
        assert memory_efficiency["efficiency_metrics"]["max_memory_per_operation_kb"] < 10.0  # Less than 10KB per operation
        
        print(f"✅ Memory Usage Optimization Verified:")
        print(f"   📊 Max {memory_efficiency['efficiency_metrics']['max_memory_per_operation_kb']:.2f}KB per operation")
        print(f"   ✅ Linear growth maintained, no memory leaks detected")
        
        return memory_efficiency


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short", "-s"])