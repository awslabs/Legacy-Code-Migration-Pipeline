"""
Base configuration management for the Migration Toolkit.

This module provides configuration loading, validation, and management
utilities used across multiple tools.
"""

import os
import yaml
import json
import pathlib
from typing import Dict, Any, Optional, Union, List
import logging

logger = logging.getLogger(__name__)


class BaseConfig:
    """
    Base configuration class for Migration Toolkit tools.
    
    Provides common configuration management functionality including:
    - Loading from YAML and JSON files
    - Environment variable override support
    - Configuration validation
    - Default value management
    """
    
    def __init__(self, config_path: Optional[Union[str, pathlib.Path]] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self._config = {}
        self._defaults = {}
        self._config_path = None
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: Union[str, pathlib.Path]) -> bool:
        """
        Load configuration from a file.
        
        Supports YAML and JSON formats. File format is determined by extension.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        path = pathlib.Path(config_path)
        
        if not path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    logger.error(f"Unsupported configuration file format: {path.suffix}")
                    return False
            
            if not isinstance(config_data, dict):
                logger.error(f"Configuration file must contain a dictionary: {config_path}")
                return False
            
            self._config = config_data
            self._config_path = path
            logger.info(f"Loaded configuration from {config_path}")
            return True
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse configuration file {config_path}: {e}")
            return False
        except (OSError, IOError) as e:
            logger.error(f"Failed to read configuration file {config_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Supports nested keys using dot notation (e.g., 'database.host').
        Environment variables override file values using uppercase keys with
        underscores (e.g., DATABASE_HOST for 'database.host').
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Check environment variable first
        env_key = key.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return self._convert_env_value(env_value)
        
        # Get from config file
        value = self._get_nested_value(self._config, key)
        if value is not None:
            return value
        
        # Get from defaults
        default_value = self._get_nested_value(self._defaults, key)
        if default_value is not None:
            return default_value
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        self._set_nested_value(self._config, key, value)
    
    def set_default(self, key: str, value: Any) -> None:
        """
        Set a default configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Default value to set
        """
        self._set_nested_value(self._defaults, key, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary containing section configuration
        """
        section_config = self._get_nested_value(self._config, section)
        if isinstance(section_config, dict):
            return section_config.copy()
        return {}
    
    def validate_config(self, schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against a schema.
        
        Args:
            schema: Validation schema dictionary
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            return self._validate_recursive(self._config, schema)
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def merge_config(self, other_config: Dict[str, Any]) -> None:
        """
        Merge another configuration dictionary into this one.
        
        Args:
            other_config: Configuration dictionary to merge
        """
        self._config = self._merge_dicts(self._config, other_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the complete configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
    
    def _get_nested_value(self, config_dict: Dict[str, Any], key: str) -> Any:
        """Get a nested value using dot notation."""
        keys = key.split('.')
        value = config_dict
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, config_dict: Dict[str, Any], key: str, value: Any) -> None:
        """Set a nested value using dot notation."""
        keys = key.split('.')
        current = config_dict
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Try to convert to boolean
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _validate_recursive(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Recursively validate configuration against schema."""
        for key, expected_type in schema.items():
            if key not in config:
                logger.error(f"Missing required configuration key: {key}")
                return False
            
            value = config[key]
            
            if isinstance(expected_type, dict):
                if not isinstance(value, dict):
                    logger.error(f"Configuration key '{key}' must be a dictionary")
                    return False
                if not self._validate_recursive(value, expected_type):
                    return False
            elif isinstance(expected_type, type):
                if not isinstance(value, expected_type):
                    logger.error(f"Configuration key '{key}' must be of type {expected_type.__name__}")
                    return False
        
        return True
    
    def _merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result


class ConfigManager:
    """
    Global configuration manager for the Migration Toolkit.
    
    Manages configuration for multiple tools and provides centralized
    configuration access.
    """
    
    _instance = None
    _configs = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_tool_config(self, tool_name: str, config: BaseConfig) -> None:
        """
        Register a tool's configuration.
        
        Args:
            tool_name: Name of the tool
            config: Configuration instance
        """
        self._configs[tool_name] = config
    
    def get_tool_config(self, tool_name: str) -> Optional[BaseConfig]:
        """
        Get a tool's configuration.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Configuration instance or None if not found
        """
        return self._configs.get(tool_name)
    
    def load_tool_config(self, tool_name: str, config_path: Union[str, pathlib.Path]) -> bool:
        """
        Load configuration for a tool.
        
        Args:
            tool_name: Name of the tool
            config_path: Path to configuration file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        config = BaseConfig()
        if config.load_config(config_path):
            self.register_tool_config(tool_name, config)
            return True
        return False


# Convenience functions
def load_config(config_path: Union[str, pathlib.Path]) -> Optional[BaseConfig]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration instance or None if loading failed
    """
    config = BaseConfig()
    if config.load_config(config_path):
        return config
    return None


def get_tool_config(tool_name: str) -> Optional[BaseConfig]:
    """
    Get configuration for a tool from the global manager.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Configuration instance or None if not found
    """
    manager = ConfigManager()
    return manager.get_tool_config(tool_name)


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate a configuration dictionary against a schema.
    
    Args:
        config: Configuration dictionary
        schema: Validation schema
        
    Returns:
        True if valid, False otherwise
    """
    temp_config = BaseConfig()
    temp_config._config = config
    return temp_config.validate_config(schema)


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    
    Args:
        base_config: Base configuration
        override_config: Configuration to merge in
        
    Returns:
        Merged configuration dictionary
    """
    temp_config = BaseConfig()
    temp_config._config = base_config
    temp_config.merge_config(override_config)
    return temp_config.to_dict()