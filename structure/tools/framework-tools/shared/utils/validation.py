"""
Common validation functions and utilities.

This module provides validation utilities used across multiple tools
in the Migration Toolkit for data sanitization and validation.
"""

import re
import pathlib
from typing import Optional, List, Set
import logging

logger = logging.getLogger(__name__)

# Valid mainframe languages supported by the toolkit
VALID_LANGUAGES = {
    'COBOL', 'PLI', 'PL1', 'ASM', 'ASSEMBLER', 'JCL', 'REXX', 'NATURAL', 'RPG',
    'C', 'CPP', 'JAVA', 'MIXED', 'UNKNOWN', 'DATA'
}

# Valid dependency types
VALID_DEPENDENCY_TYPES = {
    'CALL', 'COPY', 'INCLUDE', 'EXEC', 'DATASET_REF', 'PROGRAM_REF', 
    'COPYBOOK_REF', 'JCL_EXEC', 'CICS_LINK', 'CICS_XCTL', 'SQL_REF',
    'USING', 'PERFORM', 'GOTO'
}

# Mainframe naming patterns
MAINFRAME_NAME_PATTERN = re.compile(r'^[A-Z0-9@#$][A-Z0-9@#$]{0,7}$')
DATASET_NAME_PATTERN = re.compile(r'^[A-Z0-9@#$][A-Z0-9@#$.]{0,43}$')


def validate_artifact_name(name: str) -> bool:
    """
    Validate a mainframe artifact name (program, copybook, etc.).
    
    Mainframe names follow specific conventions:
    - 1-8 characters
    - First character: A-Z, 0-9, @, #, $
    - Remaining characters: A-Z, 0-9, @, #, $
    
    Args:
        name: Artifact name to validate
        
    Returns:
        True if name is valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    return bool(MAINFRAME_NAME_PATTERN.match(name.upper()))


def validate_file_path(file_path: str) -> bool:
    """
    Validate a file path for basic correctness.
    
    Args:
        file_path: File path to validate
        
    Returns:
        True if path appears valid, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    try:
        path = pathlib.Path(file_path)
        # Check for obviously invalid characters
        invalid_chars = ['<', '>', '|', '\0']
        return not any(char in str(path) for char in invalid_chars)
    except (ValueError, TypeError):
        return False


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize a string for database storage.
    
    Args:
        value: String to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value) if value is not None else ''
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"Truncated string to {max_length} characters")
    
    return sanitized.strip()


def is_valid_language(language: str) -> bool:
    """
    Check if a language name is valid.
    
    Args:
        language: Language name to validate
        
    Returns:
        True if language is valid, False otherwise
    """
    if not language or not isinstance(language, str):
        return False
    
    return language.upper() in VALID_LANGUAGES


def normalize_language_name(language: str) -> str:
    """
    Normalize a language name to standard form.
    
    Args:
        language: Language name to normalize
        
    Returns:
        Normalized language name
    """
    if not language or not isinstance(language, str):
        return 'UNKNOWN'
    
    normalized = language.upper().strip()
    
    # Handle common variations
    language_mappings = {
        'PL/I': 'PLI',
        'PL1': 'PLI',
        'PLSQL': 'PLI',
        'ASSEMBLER': 'ASM',
        'ASSEMBLY': 'ASM',
        'C++': 'CPP',
        'CPLUS': 'CPP',
        'JAVASCRIPT': 'JAVA',  # Treat as Java for mainframe context
        'SHELL': 'REXX',       # Treat shell scripts as REXX equivalent
    }
    
    normalized = language_mappings.get(normalized, normalized)
    
    return normalized if normalized in VALID_LANGUAGES else 'UNKNOWN'


def validate_dependency_type(dep_type: str) -> bool:
    """
    Validate a dependency type.
    
    Args:
        dep_type: Dependency type to validate
        
    Returns:
        True if dependency type is valid, False otherwise
    """
    if not dep_type or not isinstance(dep_type, str):
        return False
    
    return dep_type.upper() in VALID_DEPENDENCY_TYPES


def validate_dataset_name(dataset_name: str) -> bool:
    """
    Validate a mainframe dataset name.
    
    Dataset names follow specific conventions:
    - 1-44 characters
    - First character: A-Z, 0-9, @, #, $
    - Remaining characters: A-Z, 0-9, @, #, $, .
    - Periods separate qualifiers
    
    Args:
        dataset_name: Dataset name to validate
        
    Returns:
        True if name is valid, False otherwise
    """
    if not dataset_name or not isinstance(dataset_name, str):
        return False
    
    return bool(DATASET_NAME_PATTERN.match(dataset_name.upper()))


def sanitize_artifact_name(name: str) -> str:
    """
    Sanitize an artifact name for mainframe compatibility.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name that follows mainframe conventions
    """
    if not name or not isinstance(name, str):
        return 'UNKNOWN'
    
    # Convert to uppercase and remove invalid characters
    sanitized = re.sub(r'[^A-Z0-9@#$]', '', name.upper())
    
    # Ensure it starts with a valid character
    if sanitized and sanitized[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$':
        sanitized = 'A' + sanitized[1:]
    
    # Truncate to 8 characters
    sanitized = sanitized[:8]
    
    # If empty after sanitization, provide default
    if not sanitized:
        sanitized = 'UNKNOWN'
    
    return sanitized


def validate_line_number(line_num: int, max_lines: Optional[int] = None) -> bool:
    """
    Validate a line number.
    
    Args:
        line_num: Line number to validate
        max_lines: Maximum valid line number
        
    Returns:
        True if line number is valid, False otherwise
    """
    if not isinstance(line_num, int):
        return False
    
    if line_num < 1:
        return False
    
    if max_lines is not None and line_num > max_lines:
        return False
    
    return True


def get_valid_languages() -> Set[str]:
    """
    Get the set of valid language names.
    
    Returns:
        Set of valid language names
    """
    return VALID_LANGUAGES.copy()


def get_valid_dependency_types() -> Set[str]:
    """
    Get the set of valid dependency types.
    
    Returns:
        Set of valid dependency types
    """
    return VALID_DEPENDENCY_TYPES.copy()