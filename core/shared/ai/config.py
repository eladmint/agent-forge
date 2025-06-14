"""
Configuration constants and settings for Agent Forge operations.

This module centralizes all AI-related configuration including model settings,
API limits, and operational parameters.
"""

import os
from typing import Any, Dict

# Embedding Configuration
DEFAULT_EMBEDDING_MODEL_ID = "models/text-embedding-004"
EMBEDDING_MAX_LENGTH = 2048  # Safe limit for text-embedding-004
EMBEDDING_DIMENSION = 768  # Expected dimension for text-embedding-004

# Token Counting Configuration
DEFAULT_TOKEN_MODEL = "gemini-1.5-flash-latest"
TOKEN_CACHE_SIZE_LIMIT = 1000

# Prompt Configuration
MAX_PROMPT_CHARS = 30000
DEFAULT_TRUNCATION_STRATEGY = "end"

# Model Configuration
AVAILABLE_MODELS = {
    "embedding": {
        "text-embedding-004": {
            "max_length": 2048,
            "dimension": 768,
            "description": "Google's latest text embedding model",
        }
    },
    "generative": {
        "gemini-1.5-flash-latest": {
            "max_tokens": 32768,
            "description": "Latest Gemini Flash model for general tasks",
        },
        "gemini-1.5-pro": {
            "max_tokens": 32768,
            "description": "Gemini Pro model for complex tasks",
        },
    },
}

# API Limits and Timeouts
API_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# Quality Thresholds
EMBEDDING_SIMILARITY_THRESHOLDS = {
    "high": 0.65,  # High quality matches
    "good": 0.50,  # Good quality matches
    "low": 0.30,  # Low quality matches
}

# Content Processing Limits
MAX_CONTENT_LENGTH = 100000  # Maximum content length to process
MIN_CONTENT_LENGTH = 10  # Minimum content length to be valid


# Environment-based Configuration
def get_model_config(model_type: str = "embedding") -> Dict[str, Any]:
    """
    Get model configuration based on environment settings.

    Args:
        model_type: Type of model ("embedding" or "generative")

    Returns:
        Dict[str, Any]: Model configuration
    """
    env_model = os.environ.get(f"AI_{model_type.upper()}_MODEL")

    if model_type == "embedding":
        model_id = env_model or DEFAULT_EMBEDDING_MODEL_ID
        return {
            "model_id": model_id,
            "max_length": EMBEDDING_MAX_LENGTH,
            "dimension": EMBEDDING_DIMENSION,
        }

    elif model_type == "generative":
        model_id = env_model or DEFAULT_TOKEN_MODEL
        return {
            "model_id": model_id,
            "max_tokens": 32768,
            "timeout": API_TIMEOUT_SECONDS,
        }

    else:
        raise ValueError(f"Unknown model type: {model_type}")


def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration settings.

    Returns:
        Dict[str, Any]: API configuration
    """
    return {
        "timeout": API_TIMEOUT_SECONDS,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY_SECONDS,
        "max_content_length": MAX_CONTENT_LENGTH,
        "min_content_length": MIN_CONTENT_LENGTH,
    }


def get_quality_config() -> Dict[str, Any]:
    """
    Get quality assessment configuration.

    Returns:
        Dict[str, Any]: Quality configuration
    """
    return {
        "similarity_thresholds": EMBEDDING_SIMILARITY_THRESHOLDS,
        "min_embedding_dimension": 100,
        "max_embedding_dimension": 2000,
    }


def validate_model_id(model_id: str, model_type: str) -> bool:
    """
    Validate if a model ID is supported.

    Args:
        model_id: Model identifier to validate
        model_type: Type of model ("embedding" or "generative")

    Returns:
        bool: True if model is supported
    """
    if model_type not in AVAILABLE_MODELS:
        return False

    return model_id in AVAILABLE_MODELS[model_type]


def get_model_info(model_id: str, model_type: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific model.

    Args:
        model_id: Model identifier
        model_type: Type of model

    Returns:
        Dict[str, Any]: Model information
    """
    if not validate_model_id(model_id, model_type):
        return {}

    return AVAILABLE_MODELS[model_type][model_id]


# Development and Testing Configuration
def get_test_config() -> Dict[str, Any]:
    """
    Get configuration for testing environments.

    Returns:
        Dict[str, Any]: Test configuration
    """
    return {
        "use_mock_responses": os.environ.get("USE_TEST_MODE", "false").lower()
        == "true",
        "mock_embedding_dimension": 768,
        "mock_token_count": 50,
        "reduced_timeouts": True,
        "test_model_id": "test-model-001",
    }


# Performance Optimization Settings
OPTIMIZATION_CONFIG = {
    "enable_caching": True,
    "cache_ttl_seconds": 3600,  # 1 hour
    "batch_processing": True,
    "max_batch_size": 10,
    "async_processing": True,
    "thread_pool_size": 4,
}


def get_optimization_config() -> Dict[str, Any]:
    """
    Get performance optimization configuration.

    Returns:
        Dict[str, Any]: Optimization settings
    """
    return OPTIMIZATION_CONFIG.copy()


# Logging Configuration for AI Operations
LOGGING_CONFIG = {
    "log_api_calls": True,
    "log_token_usage": True,
    "log_performance_metrics": True,
    "sensitive_data_masking": True,
    "max_log_content_length": 200,
}


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration for AI operations.

    Returns:
        Dict[str, Any]: Logging configuration
    """
    return LOGGING_CONFIG.copy()
