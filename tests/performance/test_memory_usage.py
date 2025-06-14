"""
Memory usage profiling and optimization tests.
Tests memory consumption, leak detection, and resource cleanup
for the Agent Forge framework components.
"""

import pytest
import asyncio
import gc
import psutil
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any
from datetime import datetime


class TestMemoryUsage:
    """Memory usage profiling and optimization tests."""

    @pytest.fixture
    def memory_profiler(self):
        """Memory profiling utilities."""
        class MemoryProfiler:
            def __init__(self):
                self.process = psutil.Process()
                self.baseline_memory = self.get_memory_mb()
                self.memory_samples = []
            
            def get_memory_mb(self):
                """Get current memory usage in MB."""
                return self.process.memory_info().rss / 1024 / 1024
            
            def sample_memory(self, label=""):
                """Take a memory sample."""
                memory_mb = self.get_memory_mb()
                self.memory_samples.append({
                    "timestamp": time.perf_counter(),
                    "memory_mb": memory_mb,
                    "delta_mb": memory_mb - self.baseline_memory,
                    "label": label
                })
                return memory_mb
            
            def get_memory_growth(self):
                """Get total memory growth from baseline."""
                current_memory = self.get_memory_mb()
                return current_memory - self.baseline_memory
            
            def get_peak_memory(self):
                """Get peak memory usage from samples."""
                if not self.memory_samples:
                    return self.get_memory_mb()
                return max(sample["memory_mb"] for sample in self.memory_samples)
            
            def force_gc(self):
                """Force garbage collection and wait."""
                gc.collect()
                asyncio.sleep(0.1)  # Allow cleanup to complete
        
        return MemoryProfiler()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_memory_baseline(self, memory_profiler):
        """Test baseline memory usage of AsyncContextAgent."""
        from core.agents.base_agent import AsyncContextAgent
        
        memory_profiler.sample_memory("test_start")
        
        # Create agent without browser client
        agent = AsyncContextAgent(
            name="memory_baseline_agent",
            config={"agent_id": "baseline", "type": "scraper"}
        )
        
        memory_profiler.sample_memory("agent_created")
        
        # Initialize agent
        await agent.initialize()
        memory_profiler.sample_memory("agent_initialized")
        
        # Clean up agent
        await agent.cleanup()
        memory_profiler.sample_memory("agent_cleaned")
        
        # Force garbage collection
        memory_profiler.force_gc()
        await asyncio.sleep(0.2)
        memory_profiler.sample_memory("after_gc")
        
        # Analyze memory usage
        peak_memory = memory_profiler.get_peak_memory()
        final_growth = memory_profiler.get_memory_growth()
        
        # Memory benchmarks
        # Single agent should use less than 10MB at peak
        agent_peak_usage = peak_memory - memory_profiler.baseline_memory
        assert agent_peak_usage < 10.0, f"Agent peak memory usage {agent_peak_usage:.2f}MB, expected < 10MB"
        
        # Should not leak more than 2MB after cleanup
        assert final_growth < 2.0, f"Memory leak {final_growth:.2f}MB detected after cleanup"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_browser_client_memory_usage(self, memory_profiler):
        """Test memory usage of browser client integration."""
        
        # Mock browser client with memory tracking
        browser_memory_usage = {"allocated": 0, "operations": 0}
        
        def mock_navigate(url):
            browser_memory_usage["allocated"] += 5  # Simulate 5MB per navigation
            browser_memory_usage["operations"] += 1
            return {
                "status": "success",
                "url": url,
                "memory_usage": browser_memory_usage["allocated"]
            }
        
        def mock_extract_data(selector):
            browser_memory_usage["allocated"] += 2  # Simulate 2MB per extraction
            browser_memory_usage["operations"] += 1
            return {
                "data": [f"item_{i}" for i in range(100)],  # 100 items
                "memory_usage": browser_memory_usage["allocated"]
            }
        
        def mock_close():
            browser_memory_usage["allocated"] = 0  # Cleanup
            return {"status": "closed"}
        
        mock_browser = AsyncMock()
        mock_browser.navigate.side_effect = mock_navigate
        mock_browser.extract_data.side_effect = mock_extract_data
        mock_browser.close.side_effect = mock_close
        
        from core.agents.base_agent import AsyncContextAgent
        
        memory_profiler.sample_memory("browser_test_start")
        
        agent = AsyncContextAgent(
            name="browser_memory_agent",
            config={"agent_id": "browser_test", "type": "scraper"},
            browser_client=mock_browser
        )
        
        await agent.initialize()
        memory_profiler.sample_memory("browser_agent_initialized")
        
        # Perform multiple browser operations
        for i in range(10):
            await agent.navigate(f"https://example.com/page{i}")
            await agent.extract_data(f"div.content{i}")
            
            if i % 3 == 0:  # Sample memory every 3 operations
                memory_profiler.sample_memory(f"after_operation_{i}")
        
        memory_profiler.sample_memory("operations_complete")
        
        # Clean up
        await agent.cleanup()
        memory_profiler.sample_memory("browser_cleaned")
        
        memory_profiler.force_gc()
        await asyncio.sleep(0.3)
        memory_profiler.sample_memory("after_browser_gc")
        
        # Analyze browser memory usage
        operations_memory = memory_profiler.memory_samples[-4]["delta_mb"]  # Before cleanup
        final_memory = memory_profiler.get_memory_growth()
        
        # Browser operations should use reasonable memory
        assert operations_memory < 50.0, f"Browser operations used {operations_memory:.2f}MB, expected < 50MB"
        
        # Should clean up properly
        assert final_memory < 5.0, f"Browser memory leak {final_memory:.2f}MB detected"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_agents_memory_scaling(self, memory_profiler):
        """Test memory scaling with concurrent agents."""
        from core.agents.base_agent import AsyncContextAgent
        
        memory_profiler.sample_memory("concurrent_test_start")
        
        async def create_and_run_agent(agent_id: int):
            """Create and run a single agent."""
            agent = AsyncContextAgent(
                name=f"concurrent_agent_{agent_id}",
                config={"agent_id": f"agent_{agent_id}", "type": "scraper"},
                browser_client=AsyncMock()
            )
            
            await agent.initialize()
            
            # Simulate some work
            await asyncio.sleep(0.1)
            
            await agent.cleanup()
            return agent_id
        
        # Test different numbers of concurrent agents
        concurrent_levels = [1, 5, 10, 15]
        memory_per_level = {}
        
        for num_agents in concurrent_levels:
            memory_profiler.sample_memory(f"before_{num_agents}_agents")
            
            # Run concurrent agents
            tasks = [create_and_run_agent(i) for i in range(num_agents)]
            results = await asyncio.gather(*tasks)
            
            memory_profiler.sample_memory(f"after_{num_agents}_agents")
            
            # Force cleanup
            memory_profiler.force_gc()
            await asyncio.sleep(0.2)
            memory_profiler.sample_memory(f"cleaned_{num_agents}_agents")
            
            # Calculate memory per agent
            before_sample = next(s for s in memory_profiler.memory_samples if s["label"] == f"before_{num_agents}_agents")
            after_sample = next(s for s in memory_profiler.memory_samples if s["label"] == f"after_{num_agents}_agents")
            
            memory_used = after_sample["memory_mb"] - before_sample["memory_mb"]
            memory_per_agent = memory_used / num_agents if num_agents > 0 else 0
            
            memory_per_level[num_agents] = {
                "total_memory": memory_used,
                "memory_per_agent": memory_per_agent,
                "agents_completed": len(results)
            }
            
            assert len(results) == num_agents, f"Not all agents completed for {num_agents} concurrent agents"
        
        # Analyze memory scaling
        for num_agents, stats in memory_per_level.items():
            # Each agent should use less than 15MB on average
            assert stats["memory_per_agent"] < 15.0, f"Agent memory usage {stats['memory_per_agent']:.2f}MB too high for {num_agents} concurrent agents"
        
        # Memory scaling should be reasonable (not exponential)
        memory_1_agent = memory_per_level[1]["memory_per_agent"]
        memory_15_agents = memory_per_level[15]["memory_per_agent"]
        
        # Memory per agent should not increase dramatically with concurrency
        scaling_factor = memory_15_agents / memory_1_agent if memory_1_agent > 0 else 1
        assert scaling_factor < 3.0, f"Memory scaling factor {scaling_factor:.2f} too high, indicates poor scaling"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_long_running_memory_stability(self, memory_profiler):
        """Test memory stability for long-running agents."""
        from core.agents.base_agent import AsyncContextAgent
        
        mock_browser = AsyncMock()
        mock_browser.navigate.return_value = {"status": "success", "url": "test"}
        mock_browser.extract_data.return_value = {"data": ["item1", "item2"], "metadata": {}}
        
        agent = AsyncContextAgent(
            name="long_running_agent",
            config={"agent_id": "long_running", "type": "scraper"},
            browser_client=mock_browser
        )
        
        await agent.initialize()
        memory_profiler.sample_memory("long_running_start")
        
        # Simulate long-running operation with periodic tasks
        task_count = 0
        start_time = time.perf_counter()
        
        # Run for 5 seconds or 50 tasks, whichever comes first
        while (time.perf_counter() - start_time) < 5.0 and task_count < 50:
            # Simulate periodic task
            await agent.navigate("https://example.com/task")
            await agent.extract_data("div.content")
            
            task_count += 1
            
            # Sample memory every 10 tasks
            if task_count % 10 == 0:
                memory_profiler.sample_memory(f"task_{task_count}")
                
                # Memory stability check during execution
                current_growth = memory_profiler.get_memory_growth()
                assert current_growth < 100.0, f"Memory grew to {current_growth:.2f}MB during long-running operation"
            
            # Small delay to simulate realistic workload
            await asyncio.sleep(0.05)
        
        memory_profiler.sample_memory("long_running_complete")
        
        # Clean up
        await agent.cleanup()
        memory_profiler.force_gc()
        await asyncio.sleep(0.3)
        memory_profiler.sample_memory("long_running_cleaned")
        
        # Analyze memory stability
        task_samples = [s for s in memory_profiler.memory_samples if s["label"].startswith("task_")]
        
        if len(task_samples) >= 2:
            # Check for memory growth trend
            early_memory = task_samples[0]["delta_mb"]
            late_memory = task_samples[-1]["delta_mb"]
            memory_drift = late_memory - early_memory
            
            # Memory should not grow significantly during long operation
            assert memory_drift < 20.0, f"Memory drift {memory_drift:.2f}MB detected in long-running operation"
        
        # Final memory check
        final_growth = memory_profiler.get_memory_growth()
        assert final_growth < 10.0, f"Final memory growth {final_growth:.2f}MB after long-running test"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_data_structure_memory_usage(self, memory_profiler):
        """Test memory usage of data structures and caching."""
        
        memory_profiler.sample_memory("data_test_start")
        
        # Simulate large data extraction results
        large_datasets = []
        
        for dataset_size in [100, 1000, 5000, 10000]:
            # Create dataset
            dataset = [
                {
                    "id": i,
                    "title": f"Item {i}",
                    "description": f"Description for item {i} " * 10,  # Longer descriptions
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "category": f"category_{i % 10}",
                        "tags": [f"tag_{j}" for j in range(i % 5)]
                    }
                }
                for i in range(dataset_size)
            ]
            
            large_datasets.append(dataset)
            memory_profiler.sample_memory(f"dataset_{dataset_size}")
            
            # Memory check for this dataset size
            current_growth = memory_profiler.get_memory_growth()
            expected_max_memory = dataset_size * 0.01  # Rough estimate: 0.01MB per item
            
            assert current_growth < expected_max_memory * 2, f"Dataset {dataset_size} uses {current_growth:.2f}MB, expected < {expected_max_memory * 2:.2f}MB"
        
        # Test data cleanup
        large_datasets.clear()
        memory_profiler.force_gc()
        await asyncio.sleep(0.2)
        memory_profiler.sample_memory("datasets_cleared")
        
        # Memory should decrease after clearing data
        cleared_growth = memory_profiler.get_memory_growth()
        pre_clear_growth = memory_profiler.memory_samples[-2]["delta_mb"]
        
        memory_recovered = pre_clear_growth - cleared_growth
        assert memory_recovered > 0, "No memory recovered after clearing large datasets"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, memory_profiler):
        """Test for memory leaks in agent lifecycle."""
        from core.agents.base_agent import AsyncContextAgent
        
        memory_profiler.sample_memory("leak_test_start")
        
        # Run multiple agent creation/cleanup cycles
        leak_test_cycles = 20
        
        for cycle in range(leak_test_cycles):
            # Create agent
            agent = AsyncContextAgent(
                name=f"leak_test_agent_{cycle}",
                config={"agent_id": f"leak_test_{cycle}", "type": "scraper"},
                browser_client=AsyncMock()
            )
            
            await agent.initialize()
            
            # Simulate some work
            await asyncio.sleep(0.02)  # Small delay
            
            await agent.cleanup()
            
            # Sample memory every 5 cycles
            if cycle % 5 == 0:
                memory_profiler.sample_memory(f"cycle_{cycle}")
                
                # Intermediate leak check
                if cycle > 0:
                    current_growth = memory_profiler.get_memory_growth()
                    max_expected_growth = cycle * 0.5  # Max 0.5MB per cycle
                    
                    assert current_growth < max_expected_growth, f"Potential memory leak detected at cycle {cycle}: {current_growth:.2f}MB growth"
            
            # Force garbage collection every 10 cycles
            if cycle % 10 == 0:
                memory_profiler.force_gc()
                await asyncio.sleep(0.1)
        
        # Final garbage collection
        memory_profiler.force_gc()
        await asyncio.sleep(0.5)
        memory_profiler.sample_memory("leak_test_final")
        
        # Analyze for memory leaks
        final_growth = memory_profiler.get_memory_growth()
        max_acceptable_leak = 5.0  # 5MB total after 20 cycles
        
        assert final_growth < max_acceptable_leak, f"Memory leak detected: {final_growth:.2f}MB growth after {leak_test_cycles} cycles"
        
        # Check memory growth trend
        cycle_samples = [s for s in memory_profiler.memory_samples if s["label"].startswith("cycle_")]
        
        if len(cycle_samples) >= 3:
            # Linear regression to check for consistent growth
            growth_rates = []
            for i in range(1, len(cycle_samples)):
                prev_memory = cycle_samples[i-1]["delta_mb"]
                curr_memory = cycle_samples[i]["delta_mb"]
                growth_rate = curr_memory - prev_memory
                growth_rates.append(growth_rate)
            
            avg_growth_rate = sum(growth_rates) / len(growth_rates)
            
            # Growth rate should be minimal (close to 0)
            assert avg_growth_rate < 0.5, f"Consistent memory growth detected: {avg_growth_rate:.3f}MB per cycle"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_garbage_collection_efficiency(self, memory_profiler):
        """Test garbage collection efficiency."""
        
        memory_profiler.sample_memory("gc_test_start")
        
        # Create objects that should be garbage collected
        temp_objects = []
        
        # Phase 1: Create many temporary objects
        for i in range(1000):
            temp_obj = {
                "id": i,
                "data": [f"item_{j}" for j in range(100)],  # 100 items each
                "nested": {"level1": {"level2": {"level3": f"deep_data_{i}"}}}
            }
            temp_objects.append(temp_obj)
            
            if i % 200 == 0:
                memory_profiler.sample_memory(f"created_{i}")
        
        memory_profiler.sample_memory("objects_created")
        creation_memory = memory_profiler.get_memory_growth()
        
        # Phase 2: Clear references
        temp_objects.clear()
        memory_profiler.sample_memory("references_cleared")
        
        # Phase 3: Force garbage collection
        memory_profiler.force_gc()
        await asyncio.sleep(0.3)
        memory_profiler.sample_memory("after_gc")
        
        # Phase 4: Multiple GC cycles to ensure complete cleanup
        for gc_cycle in range(3):
            memory_profiler.force_gc()
            await asyncio.sleep(0.1)
            memory_profiler.sample_memory(f"gc_cycle_{gc_cycle}")
        
        final_memory = memory_profiler.get_memory_growth()
        
        # Calculate garbage collection efficiency
        memory_recovered = creation_memory - final_memory
        gc_efficiency = (memory_recovered / creation_memory) if creation_memory > 0 else 0
        
        # Garbage collection should recover at least 80% of allocated memory
        assert gc_efficiency > 0.8, f"GC efficiency {gc_efficiency:.2%} too low, only recovered {memory_recovered:.2f}MB of {creation_memory:.2f}MB"
        
        # Final memory should be close to baseline
        assert final_memory < 10.0, f"Final memory growth {final_memory:.2f}MB indicates incomplete garbage collection"