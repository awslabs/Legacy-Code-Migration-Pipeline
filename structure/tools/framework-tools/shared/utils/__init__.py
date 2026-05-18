# Shared utilities
"""
Common utility functions for the Migration Toolkit.

This module provides utility functions used across multiple tools including:
- File operations and path handling
- Data validation and sanitization
- Common data transformations
- Error handling utilities
"""

from .file_utils import *
from .validation import *

__all__ = [
    # File utilities
    'ensure_directory_exists',
    'get_file_extension',
    'normalize_path',
    'safe_file_read',
    'safe_file_write',
    'get_file_size',
    'is_file_readable',
    
    # Validation utilities
    'validate_artifact_name',
    'validate_file_path',
    'sanitize_string',
    'is_valid_language',
    'normalize_language_name',
    'validate_dependency_type',
]