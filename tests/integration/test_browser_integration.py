"""
Integration tests for browser automation components.
Tests the integration between AsyncContextAgent and Steel Browser client,
including navigation, data extraction, and error handling workflows.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, List, Any


class TestBrowserIntegration:
    """Test browser integration with AsyncContextAgent."""

    @pytest.fixture
    def mock_steel_browser(self):
        """Mock Steel Browser client for integration testing."""
        browser = AsyncMock()
        
        # Default successful responses
        browser.navigate.return_value = {
            "status": "success",
            "url": "https://example.com",
            "title": "Example Site",
            "load_time": 1.2,
            "response_code": 200
        }
        
        browser.extract_data.return_value = {
            "data": [
                {"title": "Article 1", "url": "/article1", "date": "2025-06-14"},
                {"title": "Article 2", "url": "/article2", "date": "2025-06-13"},
                {"title": "Article 3", "url": "/article3", "date": "2025-06-12"}
            ],
            "metadata": {
                "extraction_method": "css_selector",
                "page_title": "Example Site",
                "total_items": 3,
                "extraction_timestamp": datetime.now().isoformat()
            }
        }
        
        browser.get_page_info.return_value = {
            "url": "https://example.com",
            "title": "Example Site",
            "meta_description": "Example site for testing",
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Agent Forge Browser Client 1.0"
        }
        
        browser.take_screenshot.return_value = {
            "screenshot_path": "/tmp/screenshot_123.png",
            "dimensions": {"width": 1920, "height": 1080},
            "file_size": 245760
        }
        
        browser.close.return_value = {"status": "closed"}
        
        return browser

    @pytest.fixture
    def agent_config(self):
        """Standard agent configuration for testing."""
        return {
            "agent_id": "browser_integration_agent",
            "type": "scraper",
            "browser_config": {
                "headless": True,
                "timeout": 30,
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": "Agent Forge Browser Client 1.0"
            },
            "extraction_config": {
                "default_selector": "div.content",
                "wait_timeout": 10,
                "retry_attempts": 3
            }
        }

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_browser_initialization(self, mock_steel_browser, agent_config):
        """Test agent initialization with browser client."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name=agent_config["agent_id"],
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        # Test initialization
        await agent.initialize()
        
        # Verify agent is properly initialized
        assert agent.is_initialized is True
        assert agent.browser_client is mock_steel_browser
        assert agent.config["browser_config"]["headless"] is True
        
        # Test browser client integration
        assert hasattr(agent, 'navigate')
        assert hasattr(agent, 'extract_data')
        assert hasattr(agent, 'take_screenshot')
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_navigation_integration(self, mock_steel_browser, agent_config):
        """Test navigation integration between agent and browser."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name="navigation_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Test basic navigation
        result = await agent.navigate("https://example.com")
        
        # Verify navigation result
        assert result["status"] == "success"
        assert result["url"] == "https://example.com"
        assert result["title"] == "Example Site"
        assert result["load_time"] > 0
        
        # Verify browser client was called correctly
        mock_steel_browser.navigate.assert_called_once_with("https://example.com")
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_extraction_integration(self, mock_steel_browser, agent_config):
        """Test data extraction integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name="extraction_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Navigate to a page first
        await agent.navigate("https://example.com")
        
        # Test data extraction
        result = await agent.extract_data("article.post")
        
        # Verify extraction result
        assert len(result["data"]) == 3
        assert result["metadata"]["total_items"] == 3
        assert all("title" in item for item in result["data"])
        
        # Verify browser client was called correctly
        mock_steel_browser.extract_data.assert_called_once_with("article.post")
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_step_browser_workflow(self, mock_steel_browser, agent_config):
        """Test multi-step browser workflow integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure browser mock for multi-step workflow
        navigation_calls = []
        extraction_calls = []
        
        def track_navigate(url):
            navigation_calls.append(url)
            return {
                "status": "success",
                "url": url,
                "title": f"Page: {url.split('/')[-1]}",
                "load_time": 1.0
            }
        
        def track_extract(selector):
            extraction_calls.append(selector)
            return {
                "data": [{"item": f"Data from {selector}", "page": len(navigation_calls)}],
                "metadata": {"selector": selector, "page_number": len(navigation_calls)}
            }
        
        mock_steel_browser.navigate.side_effect = track_navigate
        mock_steel_browser.extract_data.side_effect = track_extract
        
        agent = AsyncContextAgent(
            name="multi_step_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Execute multi-step workflow
        workflow_results = []
        
        # Step 1: Navigate to home page and extract main content
        nav1 = await agent.navigate("https://example.com/home")
        data1 = await agent.extract_data("div.main-content")
        workflow_results.append({"step": 1, "navigation": nav1, "extraction": data1})
        
        # Step 2: Navigate to articles page and extract articles
        nav2 = await agent.navigate("https://example.com/articles")
        data2 = await agent.extract_data("article.post")
        workflow_results.append({"step": 2, "navigation": nav2, "extraction": data2})
        
        # Step 3: Navigate to contact page and extract form
        nav3 = await agent.navigate("https://example.com/contact")
        data3 = await agent.extract_data("form.contact-form")
        workflow_results.append({"step": 3, "navigation": nav3, "extraction": data3})
        
        # Verify workflow execution
        assert len(workflow_results) == 3
        assert len(navigation_calls) == 3
        assert len(extraction_calls) == 3
        
        # Verify navigation sequence
        assert navigation_calls[0] == "https://example.com/home"
        assert navigation_calls[1] == "https://example.com/articles"
        assert navigation_calls[2] == "https://example.com/contact"
        
        # Verify extraction sequence
        assert extraction_calls[0] == "div.main-content"
        assert extraction_calls[1] == "article.post"
        assert extraction_calls[2] == "form.contact-form"
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_browser_error_handling_integration(self, mock_steel_browser, agent_config):
        """Test browser error handling integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure browser mock to simulate errors
        error_count = {"navigate": 0, "extract": 0}
        
        def mock_navigate_with_errors(url):
            error_count["navigate"] += 1
            if error_count["navigate"] <= 2:
                if error_count["navigate"] == 1:
                    raise TimeoutError("Page load timeout")
                else:
                    raise ConnectionError("Network connection failed")
            else:
                return {
                    "status": "success",
                    "url": url,
                    "title": "Recovered Page",
                    "load_time": 2.5,
                    "retry_count": error_count["navigate"] - 1
                }
        
        def mock_extract_with_errors(selector):
            error_count["extract"] += 1
            if error_count["extract"] == 1:
                raise ValueError("Invalid selector")
            else:
                return {
                    "data": [{"recovered": "data", "selector": selector}],
                    "metadata": {"retry_success": True, "attempts": error_count["extract"]}
                }
        
        mock_steel_browser.navigate.side_effect = mock_navigate_with_errors
        mock_steel_browser.extract_data.side_effect = mock_extract_with_errors
        
        # Update agent config for retry behavior
        retry_config = agent_config.copy()
        retry_config["extraction_config"]["retry_attempts"] = 3
        retry_config["extraction_config"]["retry_delay"] = 0.1
        
        agent = AsyncContextAgent(
            name="error_handling_agent",
            config=retry_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Test navigation with retries
        nav_result = await agent.navigate_with_retry("https://example.com/error-test")
        
        # Should succeed after retries
        assert nav_result["status"] == "success"
        assert nav_result["title"] == "Recovered Page"
        assert nav_result["retry_count"] == 2
        assert error_count["navigate"] == 3
        
        # Test extraction with retries
        extract_result = await agent.extract_data_with_retry("div.error-test")
        
        # Should succeed after retry
        assert len(extract_result["data"]) == 1
        assert extract_result["data"][0]["recovered"] == "data"
        assert extract_result["metadata"]["retry_success"] is True
        assert error_count["extract"] == 2
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_browser_configuration_integration(self, mock_steel_browser):
        """Test browser configuration integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Custom browser configuration
        custom_config = {
            "agent_id": "config_test_agent",
            "type": "scraper",
            "browser_config": {
                "headless": False,
                "timeout": 60,
                "viewport": {"width": 1366, "height": 768},
                "user_agent": "Custom Agent Browser 2.0",
                "enable_javascript": True,
                "enable_images": False,
                "proxy": {"host": "proxy.example.com", "port": 8080}
            }
        }
        
        agent = AsyncContextAgent(
            name=custom_config["agent_id"],
            config=custom_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Verify browser configuration is applied
        browser_config = agent.config["browser_config"]
        assert browser_config["headless"] is False
        assert browser_config["timeout"] == 60
        assert browser_config["viewport"]["width"] == 1366
        assert browser_config["user_agent"] == "Custom Agent Browser 2.0"
        assert browser_config["enable_javascript"] is True
        assert browser_config["enable_images"] is False
        assert browser_config["proxy"]["host"] == "proxy.example.com"
        
        # Test that configuration affects browser behavior
        # (In real implementation, this would configure the actual browser)
        await agent.navigate("https://config-test.com")
        
        # Verify configuration was passed to browser client
        mock_steel_browser.navigate.assert_called_once()
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_screenshot_integration(self, mock_steel_browser, agent_config):
        """Test screenshot functionality integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name="screenshot_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Navigate to a page
        await agent.navigate("https://example.com/screenshot-test")
        
        # Take screenshot
        screenshot_result = await agent.take_screenshot("test_screenshot")
        
        # Verify screenshot result
        assert screenshot_result["screenshot_path"] == "/tmp/screenshot_123.png"
        assert screenshot_result["dimensions"]["width"] == 1920
        assert screenshot_result["dimensions"]["height"] == 1080
        assert screenshot_result["file_size"] > 0
        
        # Verify browser client was called correctly
        mock_steel_browser.take_screenshot.assert_called_once_with("test_screenshot")
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_page_info_integration(self, mock_steel_browser, agent_config):
        """Test page information retrieval integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        agent = AsyncContextAgent(
            name="page_info_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Navigate to a page
        await agent.navigate("https://example.com/info-test")
        
        # Get page information
        page_info = await agent.get_page_info()
        
        # Verify page information
        assert page_info["url"] == "https://example.com"
        assert page_info["title"] == "Example Site"
        assert page_info["meta_description"] == "Example site for testing"
        assert page_info["viewport"]["width"] == 1920
        assert page_info["user_agent"] == "Agent Forge Browser Client 1.0"
        
        # Verify browser client was called correctly
        mock_steel_browser.get_page_info.assert_called_once()
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_browser_operations(self, mock_steel_browser, agent_config):
        """Test concurrent browser operations integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure browser mock for concurrent operations
        operation_log = []
        
        def log_navigate(url):
            operation_log.append(f"navigate:{url}")
            return {
                "status": "success",
                "url": url,
                "title": f"Page {len(operation_log)}",
                "load_time": 1.0
            }
        
        def log_extract(selector):
            operation_log.append(f"extract:{selector}")
            return {
                "data": [{"concurrent_item": f"Item {len(operation_log)}", "selector": selector}],
                "metadata": {"operation_number": len(operation_log)}
            }
        
        mock_steel_browser.navigate.side_effect = log_navigate
        mock_steel_browser.extract_data.side_effect = log_extract
        
        agent = AsyncContextAgent(
            name="concurrent_browser_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Define concurrent operations
        async def operation_1():
            await agent.navigate("https://example.com/page1")
            return await agent.extract_data("div.content1")
        
        async def operation_2():
            await agent.navigate("https://example.com/page2")
            return await agent.extract_data("div.content2")
        
        async def operation_3():
            await agent.navigate("https://example.com/page3")
            return await agent.extract_data("div.content3")
        
        # Execute operations concurrently
        results = await asyncio.gather(
            operation_1(),
            operation_2(),
            operation_3()
        )
        
        # Verify concurrent execution
        assert len(results) == 3
        assert len(operation_log) == 6  # 3 navigations + 3 extractions
        
        # Verify all operations completed successfully
        for result in results:
            assert len(result["data"]) == 1
            assert "concurrent_item" in result["data"][0]
        
        # Verify browser operations were interleaved (concurrent)
        navigate_operations = [op for op in operation_log if op.startswith("navigate:")]
        extract_operations = [op for op in operation_log if op.startswith("extract:")]
        
        assert len(navigate_operations) == 3
        assert len(extract_operations) == 3
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_browser_session_persistence(self, mock_steel_browser, agent_config):
        """Test browser session persistence integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        # Configure browser mock to track session state
        session_state = {"cookies": {}, "local_storage": {}, "session_history": []}
        
        def mock_navigate_with_session(url):
            session_state["session_history"].append(url)
            return {
                "status": "success",
                "url": url,
                "title": f"Page {len(session_state['session_history'])}",
                "session_cookies": len(session_state["cookies"]),
                "history_length": len(session_state["session_history"])
            }
        
        def mock_set_cookie(name, value):
            session_state["cookies"][name] = value
            return {"status": "cookie_set", "name": name, "value": value}
        
        def mock_get_cookies():
            return {"cookies": session_state["cookies"]}
        
        mock_steel_browser.navigate.side_effect = mock_navigate_with_session
        mock_steel_browser.set_cookie = AsyncMock(side_effect=mock_set_cookie)
        mock_steel_browser.get_cookies = AsyncMock(side_effect=mock_get_cookies)
        
        agent = AsyncContextAgent(
            name="session_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Test session persistence workflow
        # Step 1: Navigate and set session data
        nav1 = await agent.navigate("https://example.com/login")
        await agent.set_cookie("session_id", "abc123")
        await agent.set_cookie("user_pref", "dark_mode")
        
        # Step 2: Navigate to another page (session should persist)
        nav2 = await agent.navigate("https://example.com/dashboard")
        
        # Step 3: Verify session persistence
        cookies = await agent.get_cookies()
        
        # Verify session state
        assert nav1["history_length"] == 1
        assert nav2["history_length"] == 2
        assert len(cookies["cookies"]) == 2
        assert cookies["cookies"]["session_id"] == "abc123"
        assert cookies["cookies"]["user_pref"] == "dark_mode"
        
        # Verify session history  
        assert len(session_state["session_history"]) == 2
        assert session_state["session_history"][0] == "https://example.com/login"
        assert session_state["session_history"][1] == "https://example.com/dashboard"
        
        await agent.cleanup()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_browser_cleanup_integration(self, mock_steel_browser, agent_config):
        """Test browser cleanup integration."""
        from core.agents.base_agent import AsyncContextAgent
        
        cleanup_called = {"count": 0}
        
        def mock_close():
            cleanup_called["count"] += 1
            return {"status": "closed", "cleanup_count": cleanup_called["count"]}
        
        mock_steel_browser.close.side_effect = mock_close
        
        agent = AsyncContextAgent(
            name="cleanup_agent",
            config=agent_config,
            browser_client=mock_steel_browser
        )
        
        await agent.initialize()
        
        # Perform some browser operations
        await agent.navigate("https://example.com/cleanup-test")
        await agent.extract_data("div.test-content")
        
        # Test cleanup
        cleanup_result = await agent.cleanup()
        
        # Verify cleanup was called
        assert cleanup_called["count"] == 1
        mock_steel_browser.close.assert_called_once()
        
        # Verify agent state after cleanup
        assert agent.is_initialized is False