# Shared configuration management
"""
Common configuration management for the Migration Toolkit.

This module provides configuration management utilities used across
multiple tools including:
- Configuration file loading and validation
- Environment variable handling
- Default configuration management
- Tool-specific configuration sections
"""

from .base_config import *

__all__ = [
    'BaseConfig',
    'ConfigManager',
    'load_config',
    'get_tool_config',
    'validate_config',
    'merge_configs',
]