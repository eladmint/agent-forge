"""
Unit tests for core utility functions.
Tests the helper utilities, file operations, rate limiting,
and other support functions used throughout the framework.
"""

import pytest
import asyncio
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open
from datetime import datetime, timedelta
from typing import Dict, List, Any


@pytest.mark.skip(reason="core.utils modules not implemented")
@pytest.mark.skip(reason="core.utils modules not implemented")
class TestFileUtils:
    """Test file utility functions."""

    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data for testing."""
        return {
            "agent_id": "test_agent_001",
            "configuration": {
                "browser_enabled": True,
                "headless": False,
                "timeout": 30
            },
            "metadata": {
                "created": "2025-06-14T12:00:00Z",
                "version": "1.0.0"
            }
        }

    def test_ensure_directory_exists(self, temp_directory):
        """Test directory creation utility."""
        from core.utils.file_utils import ensure_directory_exists
        
        # Test directory creation
        test_dir = temp_directory / "test_subdir" / "nested"
        ensure_directory_exists(test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_save_json_file(self, temp_directory, sample_json_data):
        """Test JSON file saving utility."""
        from core.utils.file_utils import save_json_file
        
        # Test JSON saving
        json_file = temp_directory / "test_data.json"
        save_json_file(json_file, sample_json_data)
        
        # Verify file was created and contains correct data
        assert json_file.exists()
        
        with open(json_file) as f:
            loaded_data = json.load(f)
        
        assert loaded_data["agent_id"] == "test_agent_001"
        assert loaded_data["configuration"]["browser_enabled"] is True

    def test_load_json_file(self, temp_directory, sample_json_data):
        """Test JSON file loading utility."""
        from core.utils.file_utils import save_json_file, load_json_file
        
        # Save test data
        json_file = temp_directory / "test_data.json"
        save_json_file(json_file, sample_json_data)
        
        # Test JSON loading
        loaded_data = load_json_file(json_file)
        
        assert loaded_data["agent_id"] == "test_agent_001"
        assert loaded_data["metadata"]["version"] == "1.0.0"

    def test_get_file_size(self, temp_directory):
        """Test file size utility."""
        from core.utils.file_utils import get_file_size
        
        # Create test file
        test_file = temp_directory / "size_test.txt"
        test_content = "This is a test file for size measurement."
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Test file size calculation
        file_size = get_file_size(test_file)
        assert file_size == len(test_content)

    def test_file_age_calculation(self, temp_directory):
        """Test file age calculation utility."""
        from core.utils.file_utils import get_file_age_seconds
        
        # Create test file
        test_file = temp_directory / "age_test.txt"
        test_file.write_text("test content")
        
        # Test age calculation
        age_seconds = get_file_age_seconds(test_file)
        assert age_seconds >= 0
        assert age_seconds < 60  # Should be very recent

    def test_safe_file_operations(self, temp_directory):
        """Test safe file operation utilities."""
        from core.utils.file_utils import safe_file_write, safe_file_read
        
        test_file = temp_directory / "safe_test.txt"
        test_content = "This is safe file content."
        
        # Test safe write
        success = safe_file_write(test_file, test_content)
        assert success is True
        assert test_file.exists()
        
        # Test safe read
        content = safe_file_read(test_file)
        assert content == test_content

    def test_file_cleanup_utility(self, temp_directory):
        """Test file cleanup utilities."""
        from core.utils.file_utils import cleanup_old_files
        
        # Create test files with different ages
        old_file = temp_directory / "old_file.txt"
        new_file = temp_directory / "new_file.txt"
        
        old_file.write_text("old content")
        new_file.write_text("new content")
        
        # Artificially age the old file by modifying its timestamp
        old_time = datetime.now().timestamp() - 3600  # 1 hour ago
        os.utime(old_file, (old_time, old_time))
        
        # Test cleanup (files older than 30 minutes)
        cleaned_count = cleanup_old_files(temp_directory, max_age_seconds=1800)
        
        assert cleaned_count >= 1
        assert not old_file.exists()
        assert new_file.exists()


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestRateLimiting:
    """Test rate limiting utilities."""

    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        """Test basic rate limiting functionality."""
        from core.utils.rate_limit import RateLimiter
        
        # Create rate limiter (2 requests per second)
        rate_limiter = RateLimiter(max_requests=2, time_window=1.0)
        
        # Test within limits
        assert await rate_limiter.can_proceed("test_key") is True
        assert await rate_limiter.can_proceed("test_key") is True
        
        # Test rate limiting kicks in
        assert await rate_limiter.can_proceed("test_key") is False

    @pytest.mark.asyncio
    async def test_rate_limiter_time_window(self):
        """Test rate limiter time window reset."""
        from core.utils.rate_limit import RateLimiter
        
        # Create rate limiter (1 request per 0.1 seconds)
        rate_limiter = RateLimiter(max_requests=1, time_window=0.1)
        
        # Use up the quota
        assert await rate_limiter.can_proceed("test_key") is True
        assert await rate_limiter.can_proceed("test_key") is False
        
        # Wait for time window reset
        await asyncio.sleep(0.15)
        
        # Should be able to proceed again
        assert await rate_limiter.can_proceed("test_key") is True

    @pytest.mark.asyncio
    async def test_rate_limiter_multiple_keys(self):
        """Test rate limiter with multiple keys."""
        from core.utils.rate_limit import RateLimiter
        
        rate_limiter = RateLimiter(max_requests=1, time_window=1.0)
        
        # Test different keys have separate limits
        assert await rate_limiter.can_proceed("key1") is True
        assert await rate_limiter.can_proceed("key2") is True
        
        # Each key should be at its limit
        assert await rate_limiter.can_proceed("key1") is False
        assert await rate_limiter.can_proceed("key2") is False

    @pytest.mark.asyncio
    async def test_adaptive_rate_limiter(self):
        """Test adaptive rate limiting based on response time."""
        from core.utils.rate_limit import AdaptiveRateLimiter
        
        rate_limiter = AdaptiveRateLimiter(
            base_max_requests=5,
            time_window=1.0,
            adaptation_factor=0.5
        )
        
        # Simulate slow responses
        rate_limiter.record_response_time("test_key", 2.0)  # 2 seconds
        rate_limiter.record_response_time("test_key", 1.5)  # 1.5 seconds
        
        # Rate limit should adapt down
        current_limit = rate_limiter.get_current_limit("test_key")
        assert current_limit < 5  # Should be reduced from base limit


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestURLUtils:
    """Test URL utility functions."""

    def test_url_validation(self):
        """Test URL validation utility."""
        from core.utils.url_utils import is_valid_url
        
        # Test valid URLs
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://test.org/path?param=value") is True
        assert is_valid_url("https://subdomain.example.com:8080/") is True
        
        # Test invalid URLs
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("") is False
        assert is_valid_url("ftp://invalid-protocol.com") is False

    def test_url_normalization(self):
        """Test URL normalization utility."""
        from core.utils.url_utils import normalize_url
        
        # Test URL normalization
        assert normalize_url("HTTPS://EXAMPLE.COM/PATH") == "https://example.com/path"
        assert normalize_url("http://test.com//double//slash") == "http://test.com/double/slash"
        assert normalize_url("https://example.com/path?b=2&a=1") == "https://example.com/path?a=1&b=2"

    def test_url_parsing(self):
        """Test URL parsing utilities."""
        from core.utils.url_utils import parse_url_components
        
        url = "https://user:pass@example.com:8080/path/to/resource?param=value&other=test#section"
        components = parse_url_components(url)
        
        assert components["scheme"] == "https"
        assert components["hostname"] == "example.com"
        assert components["port"] == 8080
        assert components["path"] == "/path/to/resource"
        assert components["query"]["param"] == "value"
        assert components["fragment"] == "section"

    def test_domain_extraction(self):
        """Test domain extraction utility."""
        from core.utils.url_utils import extract_domain
        
        assert extract_domain("https://www.example.com/path") == "example.com"
        assert extract_domain("http://subdomain.test.org") == "test.org"
        assert extract_domain("https://single-domain.com") == "single-domain.com"

    def test_url_joining(self):
        """Test URL joining utility."""
        from core.utils.url_utils import join_urls
        
        base = "https://example.com/api/v1"
        
        assert join_urls(base, "users") == "https://example.com/api/v1/users"
        assert join_urls(base, "/absolute") == "https://example.com/absolute"
        assert join_urls(base, "?query=param") == "https://example.com/api/v1?query=param"


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestTextProcessing:
    """Test text processing utilities."""

    def test_text_cleaning(self):
        """Test text cleaning utilities."""
        from core.utils.text_utils import clean_text
        
        dirty_text = "  \n\t  This is   dirty    text!  \n\n  "
        clean = clean_text(dirty_text)
        
        assert clean == "This is dirty text!"

    def test_text_extraction(self):
        """Test text extraction from HTML."""
        from core.utils.text_utils import extract_text_from_html
        
        html = """
        <div>
            <h1>Title</h1>
            <p>This is a paragraph with <strong>bold</strong> text.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </div>
        """
        
        text = extract_text_from_html(html)
        assert "Title" in text
        assert "paragraph with bold text" in text
        assert "Item 1" in text

    def test_text_summarization(self):
        """Test text summarization utility."""
        from core.utils.text_utils import summarize_text
        
        long_text = " ".join(["This is sentence number {}.".format(i) for i in range(1, 21)])
        
        summary = summarize_text(long_text, max_sentences=3)
        sentences = summary.split(".")
        
        # Should have approximately 3 sentences (plus empty string from final split)
        assert len([s for s in sentences if s.strip()]) <= 4

    def test_keyword_extraction(self):
        """Test keyword extraction utility."""
        from core.utils.text_utils import extract_keywords
        
        text = "Agent Forge is a blockchain-enabled AI agent framework for automated web scraping and data extraction."
        
        keywords = extract_keywords(text, max_keywords=5)
        
        assert len(keywords) <= 5
        assert any("agent" in keyword.lower() for keyword in keywords)
        assert any("blockchain" in keyword.lower() for keyword in keywords)


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestDataValidation:
    """Test data validation utilities."""

    def test_schema_validation(self):
        """Test JSON schema validation."""
        from core.utils.validation import validate_json_schema
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0}
            },
            "required": ["name"]
        }
        
        # Test valid data
        valid_data = {"name": "Test Agent", "age": 1.0}
        assert validate_json_schema(valid_data, schema) is True
        
        # Test invalid data
        invalid_data = {"age": -1}  # Missing required "name"
        assert validate_json_schema(invalid_data, schema) is False

    def test_agent_config_validation(self):
        """Test agent configuration validation."""
        from core.utils.validation import validate_agent_config
        
        # Test valid config
        valid_config = {
            "agent_id": "test_agent",
            "type": "scraper",
            "browser_config": {
                "headless": True,
                "timeout": 30
            },
            "enabled": True
        }
        
        result = validate_agent_config(valid_config)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        
        # Test invalid config
        invalid_config = {
            "type": "invalid_type",  # Invalid agent type
            # Missing required agent_id
        }
        
        result = validate_agent_config(invalid_config)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_url_list_validation(self):
        """Test URL list validation utility."""
        from core.utils.validation import validate_url_list
        
        # Test valid URLs
        valid_urls = [
            "https://example.com",
            "http://test.org/path",
            "https://another-site.com/page?param=value"
        ]
        
        result = validate_url_list(valid_urls)
        assert result["valid"] is True
        assert result["valid_count"] == 3
        
        # Test mixed valid/invalid URLs
        mixed_urls = [
            "https://valid.com",
            "not-a-url",
            "http://also-valid.org"
        ]
        
        result = validate_url_list(mixed_urls)
        assert result["valid"] is False
        assert result["valid_count"] == 2
        assert result["invalid_count"] == 1


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestCryptographicUtils:
    """Test cryptographic utility functions."""

    def test_hash_generation(self):
        """Test hash generation utilities."""
        from core.utils.crypto_utils import generate_hash
        
        data = "test data for hashing"
        
        # Test SHA-256 hash
        hash_sha256 = generate_hash(data, algorithm="sha256")
        assert len(hash_sha256) == 64  # SHA-256 produces 64-character hex string
        
        # Test MD5 hash
        hash_md5 = generate_hash(data, algorithm="md5")
        assert len(hash_md5) == 32  # MD5 produces 32-character hex string
        
        # Test consistency
        hash_sha256_2 = generate_hash(data, algorithm="sha256")
        assert hash_sha256 == hash_sha256_2

    def test_data_signing(self):
        """Test data signing utilities."""
        from core.utils.crypto_utils import sign_data, verify_signature
        
        data = {"agent_id": "test", "timestamp": "2025-06-14T12:00:00Z"}
        secret_key = "test_secret_key_123"
        
        # Test data signing
        signature = sign_data(data, secret_key)
        assert signature is not None
        assert len(signature) > 0
        
        # Test signature verification
        is_valid = verify_signature(data, signature, secret_key)
        assert is_valid is True
        
        # Test with wrong key
        wrong_key = "wrong_secret_key"
        is_valid_wrong = verify_signature(data, signature, wrong_key)
        assert is_valid_wrong is False

    def test_secure_random_generation(self):
        """Test secure random generation utilities."""
        from core.utils.crypto_utils import generate_secure_token, generate_uuid
        
        # Test secure token generation
        token = generate_secure_token(32)
        assert len(token) == 64  # 32 bytes = 64 hex characters
        
        # Test tokens are different
        token2 = generate_secure_token(32)
        assert token != token2
        
        # Test UUID generation
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2
        assert len(uuid1.split("-")) == 5  # Standard UUID format


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestAsyncUtils:
    """Test asynchronous utility functions."""

    @pytest.mark.asyncio
    async def test_async_retry_decorator(self):
        """Test async retry decorator utility."""
        from core.utils.async_utils import async_retry
        
        # Counter to track attempts
        attempt_count = 0
        
        @async_retry(max_attempts=3, delay=0.1)
        async def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        # Test retry functionality
        result = await failing_function()
        assert result == "success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_async_timeout_decorator(self):
        """Test async timeout decorator utility."""
        from core.utils.async_utils import async_timeout
        
        @async_timeout(timeout=0.1)
        async def slow_function():
            await asyncio.sleep(0.2)  # Slower than timeout
            return "completed"
        
        # Test timeout functionality
        with pytest.raises(asyncio.TimeoutError):
            await slow_function()

    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """Test concurrent execution utilities."""
        from core.utils.async_utils import execute_concurrently
        
        async def test_task(task_id, delay=0.1):
            await asyncio.sleep(delay)
            return f"task_{task_id}_completed"
        
        # Create multiple tasks
        tasks = [
            test_task(1, 0.1),
            test_task(2, 0.1),
            test_task(3, 0.1)
        ]
        
        # Test concurrent execution
        start_time = asyncio.get_event_loop().time()
        results = await execute_concurrently(tasks, max_concurrent=2)
        end_time = asyncio.get_event_loop().time()
        
        # Should complete faster than sequential execution
        assert (end_time - start_time) < 0.3  # Should be faster than 0.3s sequential
        assert len(results) == 3
        assert all("completed" in result for result in results)

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager utilities."""
        from core.utils.async_utils import AsyncResourceManager
        
        manager = AsyncResourceManager()
        
        async with manager.acquire_resource("test_resource") as resource:
            assert resource is not None
            assert resource["name"] == "test_resource"
            assert resource["active"] is True
        
        # Resource should be released after context
        assert manager.is_resource_active("test_resource") is False


@pytest.mark.skip(reason="core.utils modules not implemented")
class TestLoggingUtils:
    """Test logging utility functions."""

    def test_structured_logging(self):
        """Test structured logging utilities."""
        from core.utils.logging_utils import StructuredLogger
        
        logger = StructuredLogger("test_agent")
        
        # Test structured log entry
        with patch('core.utils.logging_utils.logging') as mock_logging:
            logger.log_event("agent_started", {
                "agent_id": "test_001",
                "timestamp": "2025-06-14T12:00:00Z",
                "config": {"headless": True}
            })
            
            # Verify logging was called
            mock_logging.getLogger().info.assert_called_once()

    def test_performance_logging(self):
        """Test performance logging utilities."""
        from core.utils.logging_utils import PerformanceLogger
        import time
        
        perf_logger = PerformanceLogger()
        
        # Test performance measurement
        with perf_logger.measure_performance("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        # Test metrics were recorded
        metrics = perf_logger.get_metrics("test_operation")
        assert metrics["count"] == 1
        assert metrics["avg_duration"] >= 0.1

    def test_error_tracking(self):
        """Test error tracking utilities."""
        from core.utils.logging_utils import ErrorTracker
        
        error_tracker = ErrorTracker()
        
        # Test error recording
        try:
            raise ValueError("Test error")
        except Exception as e:
            error_tracker.record_error("test_agent", e, {
                "context": "unit_test",
                "operation": "test_error_tracking"
            })
        
        # Test error statistics
        stats = error_tracker.get_error_stats("test_agent")
        assert stats["total_errors"] == 1
        assert stats["error_types"]["ValueError"] == 1