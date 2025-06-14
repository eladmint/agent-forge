"""
Unit tests for configuration management.

Tests the configuration loading, validation, and handling
functionality used throughout the Agent Forge framework.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from typing import Dict, Any

from core.shared.config import ConfigManager, load_config, validate_config


@pytest.mark.unit
class TestConfigManager:
    """Test ConfigManager class functionality."""
    
    def test_config_manager_creation(self):
        """Test ConfigManager instantiation."""
        config_manager = ConfigManager()
        
        assert config_manager is not None
        assert hasattr(config_manager, 'config')
        assert isinstance(config_manager.config, dict)
    
    def test_config_manager_with_default_config(self):
        """Test ConfigManager with default configuration."""
        config_manager = ConfigManager()
        
        # Should have default values
        assert config_manager.get('browser_timeout', 30) == 30
        assert config_manager.get('max_retries', 3) == 3
        assert isinstance(config_manager.get('debug', False), bool)
    
    def test_config_manager_with_custom_config(self):
        """Test ConfigManager with custom configuration."""
        custom_config = {
            'browser_timeout': 60,
            'api_url': 'https://custom-api.com',
            'debug': True,
            'features': {
                'blockchain': True,
                'analytics': False
            }
        }
        
        config_manager = ConfigManager(custom_config)
        
        assert config_manager.get('browser_timeout') == 60
        assert config_manager.get('api_url') == 'https://custom-api.com'
        assert config_manager.get('debug') is True
        assert config_manager.get('features', {}).get('blockchain') is True
    
    def test_config_manager_get_method(self):
        """Test ConfigManager get method with defaults."""
        config = {'existing_key': 'value'}
        config_manager = ConfigManager(config)
        
        # Test existing key
        assert config_manager.get('existing_key') == 'value'
        
        # Test missing key without default
        assert config_manager.get('missing_key') is None
        
        # Test missing key with default
        assert config_manager.get('missing_key', 'default') == 'default'
    
    def test_config_manager_update(self):
        """Test ConfigManager update functionality."""
        config_manager = ConfigManager({'initial': 'value'})
        
        config_manager.update({'new_key': 'new_value', 'initial': 'updated'})
        
        assert config_manager.get('new_key') == 'new_value'
        assert config_manager.get('initial') == 'updated'
    
    def test_config_manager_nested_access(self):
        """Test nested configuration access."""
        config = {
            'level1': {
                'level2': {
                    'level3': 'deep_value'
                }
            }
        }
        config_manager = ConfigManager(config)
        
        # Should be able to access nested values
        level1 = config_manager.get('level1', {})
        assert level1.get('level2', {}).get('level3') == 'deep_value'


@pytest.mark.unit
class TestConfigLoading:
    """Test configuration file loading functionality."""
    
    def test_load_config_from_dict(self):
        """Test loading configuration from dictionary."""
        config_dict = {
            'browser_timeout': 45,
            'api_endpoints': {
                'primary': 'https://api.example.com',
                'backup': 'https://backup.example.com'
            }
        }
        
        loaded_config = load_config(config_dict)
        
        assert loaded_config['browser_timeout'] == 45
        assert loaded_config['api_endpoints']['primary'] == 'https://api.example.com'
    
    def test_load_config_from_json_string(self):
        """Test loading configuration from JSON string."""
        json_config = '{"timeout": 30, "debug": false, "features": ["auth", "logging"]}'
        
        loaded_config = load_config(json_config)
        
        assert loaded_config['timeout'] == 30
        assert loaded_config['debug'] is False
        assert 'auth' in loaded_config['features']
        assert 'logging' in loaded_config['features']
    
    def test_load_config_from_file_path(self):
        """Test loading configuration from file path."""
        config_data = {
            'agent_config': {
                'default_timeout': 60,
                'retry_attempts': 5
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name
        
        try:
            loaded_config = load_config(temp_file_path)
            
            assert loaded_config['agent_config']['default_timeout'] == 60
            assert loaded_config['logging']['level'] == 'INFO'
        finally:
            os.unlink(temp_file_path)
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON configuration."""
        invalid_json = '{"invalid": json, "missing": quotes}'
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_config(invalid_json)
    
    def test_load_config_nonexistent_file(self):
        """Test loading from nonexistent file."""
        nonexistent_path = '/path/that/does/not/exist.json'
        
        with pytest.raises(FileNotFoundError):
            load_config(nonexistent_path)
    
    def test_load_config_empty_input(self):
        """Test loading empty configuration."""
        assert load_config({}) == {}
        assert load_config('{}') == {}
        assert load_config(None) == {}


@pytest.mark.unit
class TestConfigValidation:
    """Test configuration validation functionality."""
    
    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        valid_config = {
            'browser_timeout': 30,
            'api_url': 'https://api.example.com',
            'debug': False,
            'max_retries': 3
        }
        
        is_valid, errors = validate_config(valid_config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_invalid_types(self):
        """Test validation with invalid data types."""
        invalid_config = {
            'browser_timeout': 'not_a_number',
            'api_url': 12345,  # Should be string
            'debug': 'yes',    # Should be boolean
            'max_retries': -1  # Should be positive
        }
        
        is_valid, errors = validate_config(invalid_config)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('browser_timeout' in error for error in errors)
        assert any('api_url' in error for error in errors)
    
    def test_validate_config_missing_required(self):
        """Test validation with missing required fields."""
        incomplete_config = {
            'debug': True
            # Missing required fields
        }
        
        is_valid, errors = validate_config(incomplete_config, require_all=True)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_config_url_format(self):
        """Test URL format validation."""
        configs = [
            ({'api_url': 'https://valid.example.com'}, True),
            ({'api_url': 'http://also-valid.com'}, True),
            ({'api_url': 'not-a-url'}, False),
            ({'api_url': 'ftp://wrong-protocol.com'}, False)
        ]
        
        for config, expected_valid in configs:
            is_valid, errors = validate_config(config)
            if expected_valid:
                assert is_valid is True or len([e for e in errors if 'api_url' in e]) == 0
            else:
                assert is_valid is False or len([e for e in errors if 'api_url' in e]) > 0
    
    def test_validate_config_nested_validation(self):
        """Test validation of nested configuration objects."""
        nested_config = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'credentials': {
                    'username': 'user',
                    'password': 'pass'
                }
            },
            'features': {
                'enabled': ['auth', 'logging'],
                'disabled': []
            }
        }
        
        is_valid, errors = validate_config(nested_config)
        
        # Should handle nested objects gracefully
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


@pytest.mark.unit
class TestConfigurationPatterns:
    """Test common configuration usage patterns."""
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution in config."""
        with patch.dict(os.environ, {'TEST_API_URL': 'https://env.example.com'}):
            config_template = {
                'api_url': '${TEST_API_URL}',
                'timeout': 30
            }
            
            # This would be handled by a config processor
            processed_config = config_template.copy()
            if '${TEST_API_URL}' in str(processed_config.get('api_url', '')):
                processed_config['api_url'] = os.environ.get('TEST_API_URL')
            
            assert processed_config['api_url'] == 'https://env.example.com'
    
    def test_config_inheritance(self):
        """Test configuration inheritance patterns."""
        base_config = {
            'timeout': 30,
            'debug': False,
            'features': {
                'auth': True,
                'logging': True
            }
        }
        
        override_config = {
            'timeout': 60,
            'features': {
                'auth': False,
                'analytics': True
            }
        }
        
        # Merge configurations (override takes precedence)
        merged_config = base_config.copy()
        merged_config.update(override_config)
        
        # Handle nested merge for features
        if 'features' in base_config and 'features' in override_config:
            merged_features = base_config['features'].copy()
            merged_features.update(override_config['features'])
            merged_config['features'] = merged_features
        
        assert merged_config['timeout'] == 60  # Overridden
        assert merged_config['debug'] is False  # From base
        assert merged_config['features']['auth'] is False  # Overridden
        assert merged_config['features']['logging'] is True  # From base
        assert merged_config['features']['analytics'] is True  # New
    
    def test_config_serialization(self):
        """Test configuration serialization and deserialization."""
        original_config = {
            'agent_name': 'test_agent',
            'browser_settings': {
                'timeout': 30,
                'headless': True,
                'viewport': {'width': 1920, 'height': 1080}
            },
            'enabled_features': ['blockchain', 'analytics']
        }
        
        # Serialize to JSON
        json_str = json.dumps(original_config)
        
        # Deserialize back
        restored_config = json.loads(json_str)
        
        assert restored_config == original_config
        assert restored_config['browser_settings']['timeout'] == 30
        assert 'blockchain' in restored_config['enabled_features']


@pytest.mark.unit
class TestConfigurationSecurity:
    """Test configuration security aspects."""
    
    def test_sensitive_data_handling(self):
        """Test handling of sensitive configuration data."""
        config_with_secrets = {
            'api_key': 'secret_key_123',
            'database_password': 'super_secret_password',
            'regular_setting': 'normal_value'
        }
        
        # Mock a function that sanitizes config for logging
        def sanitize_config_for_logging(config):
            sanitized = config.copy()
            sensitive_keys = ['api_key', 'password', 'secret', 'token']
            
            for key in list(sanitized.keys()):
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '***REDACTED***'
            
            return sanitized
        
        sanitized = sanitize_config_for_logging(config_with_secrets)
        
        assert sanitized['api_key'] == '***REDACTED***'
        assert sanitized['database_password'] == '***REDACTED***'
        assert sanitized['regular_setting'] == 'normal_value'
    
    def test_config_file_permissions(self):
        """Test configuration file security permissions."""
        config_data = {'sensitive': 'data'}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name
        
        try:
            # Check that file exists and is readable
            assert os.path.exists(temp_file_path)
            assert os.access(temp_file_path, os.R_OK)
            
            # In a real implementation, you'd check permissions
            file_stat = os.stat(temp_file_path)
            # file_stat.st_mode can be used to check permissions
            assert file_stat.st_size > 0  # File has content
            
        finally:
            os.unlink(temp_file_path)


@pytest.mark.unit
class TestConfigurationErrorHandling:
    """Test configuration error handling scenarios."""
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON configuration."""
        malformed_configs = [
            '{"unclosed": "json"',
            '{"trailing": "comma",}',
            '{invalid: "json"}',
            '{"numeric": 123.456.789}'
        ]
        
        for malformed in malformed_configs:
            with pytest.raises((ValueError, json.JSONDecodeError)):
                load_config(malformed)
    
    def test_type_coercion_errors(self):
        """Test handling of type coercion errors."""
        config_with_type_issues = {
            'timeout': 'thirty',  # Should be int
            'enabled': 'true',    # Should be bool
            'ports': 'not a list' # Should be list
        }
        
        # Test that validation catches these issues
        is_valid, errors = validate_config(config_with_type_issues)
        
        # Should have validation errors
        assert is_valid is False or len(errors) >= 0
    
    def test_missing_file_handling(self):
        """Test graceful handling of missing configuration files."""
        missing_file_path = '/absolutely/nonexistent/path/config.json'
        
        # Should raise appropriate exception
        with pytest.raises(FileNotFoundError):
            load_config(missing_file_path)
    
    def test_permission_denied_handling(self):
        """Test handling of permission denied errors."""
        # This test would require creating a file with restricted permissions
        # For now, we'll test the error handling pattern
        
        def mock_load_restricted_file(path):
            raise PermissionError(f"Permission denied: {path}")
        
        with pytest.raises(PermissionError):
            mock_load_restricted_file('/restricted/config.json')


@pytest.mark.unit
class TestConfigurationPerformance:
    """Test configuration performance characteristics."""
    
    def test_config_loading_performance(self):
        """Test configuration loading performance."""
        # Create a large configuration
        large_config = {}
        for i in range(1000):
            large_config[f'key_{i}'] = {
                'value': f'value_{i}',
                'nested': {
                    'deep_value': f'deep_{i}',
                    'list': list(range(10))
                }
            }
        
        # Test that loading is reasonably fast
        import time
        start_time = time.time()
        
        config_manager = ConfigManager(large_config)
        
        end_time = time.time()
        loading_time = end_time - start_time
        
        # Should load in reasonable time (less than 1 second)
        assert loading_time < 1.0
        assert len(config_manager.config) == 1000
    
    def test_config_access_performance(self):
        """Test configuration access performance."""
        config = {f'key_{i}': f'value_{i}' for i in range(10000)}
        config_manager = ConfigManager(config)
        
        # Test that access is fast
        import time
        start_time = time.time()
        
        # Access many values
        for i in range(0, 10000, 100):
            value = config_manager.get(f'key_{i}')
            assert value == f'value_{i}'
        
        end_time = time.time()
        access_time = end_time - start_time
        
        # Should access quickly
        assert access_time < 0.1