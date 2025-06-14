"""
Performance tests for Agent Forge framework.
Tests execution speed, memory usage, and scalability
of the AsyncContextAgent and related components.
"""

import pytest
import asyncio
import time
import psutil
import gc
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any
from datetime import datetime, timedelta


class TestAgentPerformance:
    """Performance benchmarks for agents."""

    @pytest.fixture
    def mock_browser_client(self):
        """Mock browser client for performance testing."""
        client = AsyncMock()
        client.navigate.return_value = {"status": "success", "url": "https://example.com"}
        client.extract_data.return_value = {"data": ["item1", "item2", "item3"]}
        client.close.return_value = None
        return client

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_startup_time(self, mock_browser_client):
        """Benchmark agent initialization time."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Measure startup time
        start_time = time.perf_counter()
        
        agent = AsyncContextAgent(
            name="performance_test_agent",
            browser_client=mock_browser_client
        )
        
        # Initialize agent
        await agent.initialize()
        
        end_time = time.perf_counter()
        startup_time = end_time - start_time
        
        # Performance benchmark: Should start within 2 seconds
        assert startup_time < 2.0, f"Agent startup took {startup_time:.3f}s, expected < 2.0s"
        
        # Cleanup
        await agent.cleanup()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_browser_navigation_performance(self, mock_browser_client):
        """Benchmark browser navigation speed."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name="navigation_test_agent",
            browser_client=mock_browser_client
        )
        
        await agent.initialize()
        
        # Measure navigation time
        start_time = time.perf_counter()
        
        result = await agent.navigate("https://example.com")
        
        end_time = time.perf_counter()
        navigation_time = end_time - start_time
        
        # Performance benchmark: Should navigate within 10 seconds
        assert navigation_time < 10.0, f"Navigation took {navigation_time:.3f}s, expected < 10.0s"
        assert result["status"] == "success"
        
        await agent.cleanup()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self, mock_browser_client):
        """Test performance with multiple concurrent agents."""
        from core.agents.base_agent import AsyncContextAgent
        
        num_agents = 10
        
        async def create_and_run_agent(agent_id: int):
            agent = AsyncContextAgent(
                name=f"concurrent_agent_{agent_id}",
                browser_client=mock_browser_client
            )
            
            await agent.initialize()
            
            # Simulate some work
            result = await agent.navigate("https://example.com")
            await asyncio.sleep(0.1)  # Simulate processing time
            
            await agent.cleanup()
            return result
        
        # Measure concurrent execution time
        start_time = time.perf_counter()
        
        # Run agents concurrently
        tasks = [create_and_run_agent(i) for i in range(num_agents)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Performance benchmark: Should handle 10 concurrent agents within 15 seconds
        assert total_time < 15.0, f"Concurrent execution took {total_time:.3f}s, expected < 15.0s"
        assert len(results) == num_agents
        assert all(result["status"] == "success" for result in results)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_memory_usage(self, mock_browser_client):
        """Profile agent memory usage."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        agents = []
        
        # Create multiple agents
        for i in range(5):
            agent = AsyncContextAgent(
                name=f"memory_test_agent_{i}",
                browser_client=mock_browser_client
            )
            await agent.initialize()
            agents.append(agent)
        
        # Get memory usage with agents
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_per_agent = (peak_memory - initial_memory) / len(agents)
        
        # Performance benchmark: Each agent should use less than 50MB
        assert memory_per_agent < 50.0, f"Each agent uses {memory_per_agent:.2f}MB, expected < 50MB"
        
        # Cleanup agents
        for agent in agents:
            await agent.cleanup()
        
        # Force garbage collection
        gc.collect()
        
        # Check memory cleanup
        await asyncio.sleep(0.5)  # Allow cleanup to complete
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_leaked = final_memory - initial_memory
        
        # Memory leak check: Should not leak more than 10MB
        assert memory_leaked < 10.0, f"Memory leak detected: {memory_leaked:.2f}MB"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_data_extraction_performance(self, mock_browser_client):
        """Benchmark data extraction performance."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure mock to return large dataset
        large_dataset = [f"item_{i}" for i in range(1000)]
        mock_browser_client.extract_data.return_value = {"data": large_dataset}
        
        agent = AsyncContextAgent(
            name="extraction_test_agent",
            browser_client=mock_browser_client
        )
        
        await agent.initialize()
        
        # Measure extraction time
        start_time = time.perf_counter()
        
        result = await agent.extract_data("test_selector")
        
        end_time = time.perf_counter()
        extraction_time = end_time - start_time
        
        # Performance benchmark: Should extract 1000 items within 5 seconds
        assert extraction_time < 5.0, f"Data extraction took {extraction_time:.3f}s, expected < 5.0s"
        assert len(result["data"]) == 1000
        
        await agent.cleanup()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_sequential_vs_concurrent_performance(self, mock_browser_client):
        """Compare sequential vs concurrent execution performance."""
        from core.agents.base_agent import AsyncContextAgent
        
        num_tasks = 5
        
        async def run_single_task(task_id: int):
            agent = AsyncContextAgent(
                name=f"task_agent_{task_id}",
                browser_client=mock_browser_client
            )
            
            await agent.initialize()
            await agent.navigate("https://example.com")
            await asyncio.sleep(0.2)  # Simulate work
            await agent.cleanup()
            
            return f"task_{task_id}_complete"
        
        # Test sequential execution
        start_time = time.perf_counter()
        
        sequential_results = []
        for i in range(num_tasks):
            result = await run_single_task(i)
            sequential_results.append(result)
        
        sequential_time = time.perf_counter() - start_time
        
        # Test concurrent execution
        start_time = time.perf_counter()
        
        concurrent_tasks = [run_single_task(i) for i in range(num_tasks)]
        concurrent_results = await asyncio.gather(*concurrent_tasks)
        
        concurrent_time = time.perf_counter() - start_time
        
        # Performance comparison: Concurrent should be significantly faster
        speedup_ratio = sequential_time / concurrent_time
        assert speedup_ratio > 2.0, f"Concurrent speedup only {speedup_ratio:.2f}x, expected > 2.0x"
        
        assert len(sequential_results) == num_tasks
        assert len(concurrent_results) == num_tasks


class TestBrowserPerformance:
    """Performance tests for browser automation."""

    @pytest.fixture
    def performance_browser_client(self):
        """Browser client configured for performance testing."""
        client = AsyncMock()
        
        # Configure realistic response times
        async def mock_navigate(url):
            await asyncio.sleep(0.5)  # Simulate navigation time
            return {"status": "success", "url": url, "load_time": 0.5}
        
        async def mock_extract_data(selector):
            await asyncio.sleep(0.2)  # Simulate extraction time
            return {"data": [f"item_{i}" for i in range(10)]}
        
        client.navigate.side_effect = mock_navigate
        client.extract_data.side_effect = mock_extract_data
        
        return client

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_page_load_performance(self, performance_browser_client):
        """Test page loading performance benchmarks."""
        from core.browser.steel_browser_client import SteelBrowserClient
        
        # Test multiple page loads
        urls = [
            "https://example.com",
            "https://test.org",
            "https://demo.com",
            "https://sample.net",
            "https://benchmark.io"
        ]
        
        start_time = time.perf_counter()
        
        load_times = []
        for url in urls:
            page_start = time.perf_counter()
            result = await performance_browser_client.navigate(url)
            page_end = time.perf_counter()
            
            load_time = page_end - page_start
            load_times.append(load_time)
            
            assert result["status"] == "success"
        
        total_time = time.perf_counter() - start_time
        avg_load_time = sum(load_times) / len(load_times)
        
        # Performance benchmarks
        assert avg_load_time < 1.0, f"Average page load time {avg_load_time:.3f}s, expected < 1.0s"
        assert max(load_times) < 2.0, f"Max page load time {max(load_times):.3f}s, expected < 2.0s"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_browser_sessions(self, performance_browser_client):
        """Test performance with multiple concurrent browser sessions."""
        
        async def browser_session(session_id: int):
            # Simulate a browser session with multiple operations
            await performance_browser_client.navigate(f"https://site{session_id}.com")
            await performance_browser_client.extract_data("div.content")
            await asyncio.sleep(0.1)  # Simulate processing
            return f"session_{session_id}_complete"
        
        num_sessions = 8
        
        start_time = time.perf_counter()
        
        # Run concurrent browser sessions
        tasks = [browser_session(i) for i in range(num_sessions)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_time
        
        # Performance benchmark: 8 concurrent sessions within 10 seconds
        assert total_time < 10.0, f"Concurrent browser sessions took {total_time:.3f}s, expected < 10.0s"
        assert len(results) == num_sessions

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_data_extraction_throughput(self, performance_browser_client):
        """Test data extraction throughput performance."""
        
        selectors = [
            "div.item",
            "span.data",
            "a.link",
            "p.content",
            "li.list-item"
        ]
        
        start_time = time.perf_counter()
        
        total_items = 0
        for selector in selectors:
            result = await performance_browser_client.extract_data(selector)
            total_items += len(result["data"])
        
        total_time = time.perf_counter() - start_time
        
        # Calculate throughput (items per second)
        throughput = total_items / total_time
        
        # Performance benchmark: Should extract at least 100 items/second
        assert throughput > 100, f"Extraction throughput {throughput:.1f} items/s, expected > 100 items/s"


class TestMemoryLeakDetection:
    """Memory leak detection and profiling tests."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_lifecycle_memory_leak(self):
        """Test for memory leaks in agent lifecycle."""
        from core.agents.base_agent import AsyncContextAgent
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple agent lifecycle cycles
        for cycle in range(10):
            agent = AsyncContextAgent(
                name=f"leak_test_agent_{cycle}",
                browser_client=AsyncMock()
            )
            
            await agent.initialize()
            
            # Simulate agent work
            await asyncio.sleep(0.1)
            
            await agent.cleanup()
            
            # Force garbage collection every few cycles
            if cycle % 3 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
        await asyncio.sleep(0.5)  # Allow cleanup to complete
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory leak threshold: Should not grow by more than 20MB
        assert memory_growth < 20.0, f"Memory grew by {memory_growth:.2f}MB, possible leak detected"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_browser_client_memory_usage(self):
        """Profile browser client memory usage patterns."""
        
        process = psutil.Process()
        memory_samples = []
        
        # Sample memory usage over time
        for i in range(20):
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)
            
            # Simulate browser operations
            client = AsyncMock()
            await client.navigate(f"https://test{i}.com")
            await asyncio.sleep(0.05)
            
            if i % 5 == 0:
                gc.collect()
        
        # Analyze memory usage pattern
        memory_trend = memory_samples[-5:] if len(memory_samples) >= 5 else memory_samples
        avg_recent_memory = sum(memory_trend) / len(memory_trend)
        
        # Check for excessive memory growth
        initial_memory = memory_samples[0]
        max_growth = max(memory_samples) - initial_memory
        
        assert max_growth < 100.0, f"Memory grew by {max_growth:.2f}MB, may indicate inefficient usage"


class TestScalabilityBenchmarks:
    """Scalability and load testing benchmarks."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_agent_scaling_limits(self):
        """Test agent scaling limits and performance degradation."""
        from core.agents.base_agent import AsyncContextAgent
        
        scaling_results = []
        
        # Test different numbers of concurrent agents
        for num_agents in [1, 5, 10, 20, 30]:
            start_time = time.perf_counter()
            
            async def create_scaled_agent(agent_id: int):
                agent = AsyncContextAgent(
                    name=f"scale_agent_{agent_id}",
                    browser_client=AsyncMock()
                )
                await agent.initialize()
                await asyncio.sleep(0.1)  # Simulate work
                await agent.cleanup()
                return agent_id
            
            # Run agents at this scale level
            tasks = [create_scaled_agent(i) for i in range(num_agents)]
            results = await asyncio.gather(*tasks)
            
            execution_time = time.perf_counter() - start_time
            
            scaling_results.append({
                "num_agents": num_agents,
                "execution_time": execution_time,
                "agents_per_second": num_agents / execution_time
            })
            
            assert len(results) == num_agents
        
        # Analyze scaling characteristics
        max_agents_per_second = max(result["agents_per_second"] for result in scaling_results)
        
        # Performance benchmark: Should handle at least 50 agents per second at peak
        assert max_agents_per_second > 50, f"Peak throughput {max_agents_per_second:.1f} agents/s, expected > 50"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_long_running_agent_stability(self):
        """Test long-running agent stability and performance."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name="long_running_agent",
            browser_client=AsyncMock()
        )
        
        await agent.initialize()
        
        # Run agent for extended period with periodic tasks
        start_time = time.perf_counter()
        task_count = 0
        
        # Run for up to 10 seconds or 100 tasks
        while (time.perf_counter() - start_time) < 10.0 and task_count < 100:
            # Simulate periodic task
            await asyncio.sleep(0.05)
            task_count += 1
            
            # Periodic memory check
            if task_count % 20 == 0:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                # Memory stability check: Should not exceed 200MB
                assert memory_mb < 200, f"Memory usage {memory_mb:.1f}MB exceeds stability limit"
        
        execution_time = time.perf_counter() - start_time
        tasks_per_second = task_count / execution_time
        
        await agent.cleanup()
        
        # Performance benchmark: Should maintain at least 10 tasks/second
        assert tasks_per_second > 10, f"Long-running performance {tasks_per_second:.1f} tasks/s, expected > 10"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_resource_cleanup_efficiency(self):
        """Test efficiency of resource cleanup operations."""
        
        cleanup_times = []
        
        # Test cleanup efficiency across multiple cycles
        for cycle in range(10):
            # Create resources
            resources = []
            for i in range(20):
                mock_resource = AsyncMock()
                mock_resource.cleanup = AsyncMock()
                resources.append(mock_resource)
            
            # Measure cleanup time
            start_cleanup = time.perf_counter()
            
            # Simulate parallel cleanup
            cleanup_tasks = [resource.cleanup() for resource in resources]
            await asyncio.gather(*cleanup_tasks)
            
            cleanup_time = time.perf_counter() - start_cleanup
            cleanup_times.append(cleanup_time)
        
        # Analyze cleanup performance
        avg_cleanup_time = sum(cleanup_times) / len(cleanup_times)
        max_cleanup_time = max(cleanup_times)
        
        # Performance benchmarks
        assert avg_cleanup_time < 1.0, f"Average cleanup time {avg_cleanup_time:.3f}s, expected < 1.0s"
        assert max_cleanup_time < 2.0, f"Max cleanup time {max_cleanup_time:.3f}s, expected < 2.0s"