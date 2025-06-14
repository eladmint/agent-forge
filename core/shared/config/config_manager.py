"""
Configuration management system for Agent Forge.

Provides centralized configuration loading, validation, and management
functionality with support for various input formats and validation rules.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse


class ConfigManager:
    """
    Centralized configuration manager for Agent Forge.
    
    Provides unified interface for configuration loading, validation,
    and access with support for nested configurations and defaults.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ConfigManager with optional configuration.
        
        Args:
            config: Initial configuration dictionary
        """
        self.config = config or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with optional default.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def update(self, new_config: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            new_config: Dictionary of new configuration values
        """
        self.config.update(new_config)
    
    def merge(self, other_config: Dict[str, Any], deep_merge: bool = True) -> None:
        """
        Merge another configuration into this one.
        
        Args:
            other_config: Configuration to merge
            deep_merge: Whether to perform deep merge for nested dicts
        """
        if not deep_merge:
            self.config.update(other_config)
            return
        
        def deep_merge_dict(base: Dict, overlay: Dict) -> Dict:
            """Recursively merge dictionaries."""
            result = base.copy()
            for key, value in overlay.items():
                if (key in result and 
                    isinstance(result[key], dict) and 
                    isinstance(value, dict)):
                    result[key] = deep_merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.config = deep_merge_dict(self.config, other_config)
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self.config
    
    def keys(self) -> List[str]:
        """Get all configuration keys."""
        return list(self.config.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config.copy()


def load_config(source: Union[str, Dict[str, Any], Path, None]) -> Dict[str, Any]:
    """
    Load configuration from various sources.
    
    Args:
        source: Configuration source - can be:
                - Dict: Direct configuration dictionary
                - str: JSON string or file path
                - Path: File path to JSON configuration
                - None: Returns empty dict
    
    Returns:
        Loaded configuration dictionary
        
    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If JSON string is invalid
        json.JSONDecodeError: If JSON parsing fails
    """
    if source is None:
        return {}
    
    if isinstance(source, dict):
        return source.copy()
    
    if isinstance(source, (str, Path)):
        source_str = str(source)
        
        # Check if it's a file path
        if os.path.exists(source_str):
            try:
                with open(source_str, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in file {source_str}: {e}")
        
        # Try to parse as JSON string
        if source_str.strip():
            try:
                return json.loads(source_str)
            except json.JSONDecodeError as e:
                # If it looks like a path but doesn't exist, raise FileNotFoundError
                if ('/' in source_str or '\\' in source_str or 
                    source_str.endswith('.json')):
                    raise FileNotFoundError(f"Configuration file not found: {source_str}")
                raise ValueError(f"Invalid JSON string: {e}")
    
    return {}


def validate_config(config: Dict[str, Any], require_all: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        require_all: Whether to require all standard fields
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Define validation rules
    validation_rules = {
        'browser_timeout': {
            'type': (int, float),
            'min_value': 1,
            'max_value': 300
        },
        'api_url': {
            'type': str,
            'format': 'url'
        },
        'debug': {
            'type': bool
        },
        'max_retries': {
            'type': int,
            'min_value': 0,
            'max_value': 10
        }
    }
    
    # Check required fields if specified
    if require_all:
        required_fields = ['browser_timeout', 'api_url']
        for field in required_fields:
            if field not in config:
                errors.append(f"Required field '{field}' is missing")
    
    # Validate each field present in config
    for key, value in config.items():
        if key in validation_rules:
            rule = validation_rules[key]
            
            # Type validation
            if 'type' in rule:
                expected_type = rule['type']
                if isinstance(expected_type, tuple):
                    if not isinstance(value, expected_type):
                        errors.append(f"Field '{key}' must be one of types {expected_type}, got {type(value)}")
                else:
                    if not isinstance(value, expected_type):
                        errors.append(f"Field '{key}' must be of type {expected_type.__name__}, got {type(value)}")
            
            # Numeric range validation
            if isinstance(value, (int, float)):
                if 'min_value' in rule and value < rule['min_value']:
                    errors.append(f"Field '{key}' must be >= {rule['min_value']}, got {value}")
                if 'max_value' in rule and value > rule['max_value']:
                    errors.append(f"Field '{key}' must be <= {rule['max_value']}, got {value}")
            
            # URL format validation
            if rule.get('format') == 'url' and isinstance(value, str):
                if not _is_valid_url(value):
                    errors.append(f"Field '{key}' must be a valid URL, got '{value}'")
    
    return len(errors) == 0, errors


def _is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def create_default_config() -> Dict[str, Any]:
    """
    Create default configuration dictionary.
    
    Returns:
        Default configuration with standard values
    """
    return {
        'browser_timeout': 30,
        'api_url': 'https://api.example.com',
        'debug': False,
        'max_retries': 3,
        'log_level': 'INFO',
        'features': {
            'auth': True,
            'logging': True,
            'analytics': False
        }
    }


def substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Substitute environment variables in configuration values.
    
    Supports ${VAR_NAME} syntax for environment variable substitution.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configuration with environment variables substituted
    """
    def substitute_value(value: Any) -> Any:
        """Recursively substitute environment variables."""
        if isinstance(value, str):
            # Find ${VAR_NAME} patterns
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)
            
            result = value
            for var_name in matches:
                env_value = os.environ.get(var_name)
                if env_value is not None:
                    result = result.replace(f'${{{var_name}}}', env_value)
            
            return result
        elif isinstance(value, dict):
            return {k: substitute_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [substitute_value(item) for item in value]
        else:
            return value
    
    return substitute_value(config)


def sanitize_config_for_logging(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize configuration for safe logging by redacting sensitive values.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Sanitized configuration with sensitive values redacted
    """
    sensitive_keys = ['password', 'key', 'secret', 'token', 'credential']
    
    def sanitize_value(key: str, value: Any) -> Any:
        """Recursively sanitize sensitive values."""
        if isinstance(value, dict):
            return {k: sanitize_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(key, item) for item in value]
        else:
            # Check if key contains sensitive keywords
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                return '***REDACTED***'
            return value
    
    return {k: sanitize_value(k, v) for k, v in config.items()}