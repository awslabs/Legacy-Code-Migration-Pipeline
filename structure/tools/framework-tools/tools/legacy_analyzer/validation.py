"""Validation utilities for Legacy Analyzer.

This module provides validation functions for CICS resources, file paths,
and other inputs to ensure data quality and prevent errors.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from .exceptions import (
    ResourceNameValidationError,
    AttributeValidationError,
    CLIFileNotFoundError,
    CLIDirectoryNotFoundError,
    CLIPermissionError,
    CLIValidationError
)


logger = logging.getLogger(__name__)


# Resource Name Validation

def validate_transaction_id(trans_id: str, strict: bool = True) -> Tuple[bool, Optional[str]]:
    """Validate CICS transaction ID.
    
    Transaction IDs should be 1-4 characters, alphanumeric.
    
    Args:
        trans_id: Transaction ID to validate
        strict: If True, enforce 4-character limit strictly
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not trans_id:
        return False, "Transaction ID cannot be empty"
    
    if not trans_id.strip():
        return False, "Transaction ID cannot be whitespace only"
    
    # Check length
    if strict and len(trans_id) > 4:
        return False, f"Transaction ID '{trans_id}' exceeds 4 characters (length: {len(trans_id)})"
    elif len(trans_id) > 8:
        return False, f"Transaction ID '{trans_id}' exceeds maximum length of 8 characters"
    
    # Check characters (alphanumeric and some special chars allowed)
    if not re.match(r'^[A-Z0-9@#$]+$', trans_id, re.IGNORECASE):
        return False, f"Transaction ID '{trans_id}' contains invalid characters (allowed: A-Z, 0-9, @, #, $)"
    
    return True, None


def validate_program_name(program_name: str) -> Tuple[bool, Optional[str]]:
    """Validate CICS program name.
    
    Program names should be 1-8 characters, alphanumeric.
    
    Args:
        program_name: Program name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not program_name:
        return False, "Program name cannot be empty"
    
    if not program_name.strip():
        return False, "Program name cannot be whitespace only"
    
    # Check length
    if len(program_name) > 8:
        return False, f"Program name '{program_name}' exceeds 8 characters (length: {len(program_name)})"
    
    # Check characters (alphanumeric and some special chars allowed)
    if not re.match(r'^[A-Z0-9@#$]+$', program_name, re.IGNORECASE):
        return False, f"Program name '{program_name}' contains invalid characters (allowed: A-Z, 0-9, @, #, $)"
    
    return True, None


def validate_group_name(group_name: str) -> Tuple[bool, Optional[str]]:
    """Validate CICS group name.
    
    Group names should be 1-8 characters, alphanumeric.
    
    Args:
        group_name: Group name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not group_name:
        return False, "Group name cannot be empty"
    
    if not group_name.strip():
        return False, "Group name cannot be whitespace only"
    
    # Check length
    if len(group_name) > 8:
        return False, f"Group name '{group_name}' exceeds 8 characters (length: {len(group_name)})"
    
    # Check characters
    if not re.match(r'^[A-Z0-9@#$]+$', group_name, re.IGNORECASE):
        return False, f"Group name '{group_name}' contains invalid characters (allowed: A-Z, 0-9, @, #, $)"
    
    return True, None


def validate_dataset_name(dataset_name: str) -> Tuple[bool, Optional[str]]:
    """Validate MVS dataset name.
    
    Dataset names follow MVS naming conventions:
    - Up to 44 characters
    - Qualifiers separated by dots
    - Each qualifier 1-8 characters
    - Alphanumeric and special chars (@, #, $)
    
    Args:
        dataset_name: Dataset name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dataset_name:
        return False, "Dataset name cannot be empty"
    
    if not dataset_name.strip():
        return False, "Dataset name cannot be whitespace only"
    
    # Check total length
    if len(dataset_name) > 44:
        return False, f"Dataset name '{dataset_name}' exceeds 44 characters (length: {len(dataset_name)})"
    
    # Check qualifiers
    qualifiers = dataset_name.split('.')
    if not qualifiers:
        return False, f"Dataset name '{dataset_name}' has no qualifiers"
    
    for qualifier in qualifiers:
        if not qualifier:
            return False, f"Dataset name '{dataset_name}' has empty qualifier"
        
        if len(qualifier) > 8:
            return False, f"Dataset name '{dataset_name}' has qualifier '{qualifier}' exceeding 8 characters"
        
        if not re.match(r'^[A-Z0-9@#$]+$', qualifier, re.IGNORECASE):
            return False, f"Dataset name '{dataset_name}' has qualifier '{qualifier}' with invalid characters"
    
    return True, None


def validate_status(status: str) -> Tuple[bool, Optional[str]]:
    """Validate CICS resource status.
    
    Status should be ENABLED or DISABLED.
    
    Args:
        status: Status to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not status:
        return False, "Status cannot be empty"
    
    valid_statuses = {'ENABLED', 'DISABLED'}
    status_upper = status.upper()
    
    if status_upper not in valid_statuses:
        return False, f"Invalid status '{status}' (must be ENABLED or DISABLED)"
    
    return True, None


def validate_language(language: str) -> Tuple[bool, Optional[str]]:
    """Validate programming language.
    
    Args:
        language: Language to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not language:
        return False, "Language cannot be empty"
    
    valid_languages = {
        'COBOL', 'PLI', 'PL/I', 'ASSEMBLER', 'ASM', 'C', 'C++',
        'JAVA', 'REXX', 'NATURAL', 'RPG'
    }
    language_upper = language.upper()
    
    if language_upper not in valid_languages:
        logger.warning(f"Unusual language value: {language}")
        # Don't fail, just warn
    
    return True, None


# File and Path Validation

def validate_file_exists(file_path: str, file_type: str = "file") -> None:
    """Validate that a file exists and is readable.
    
    Args:
        file_path: Path to file
        file_type: Type of file for error message (e.g., "CSD file", "CSV file")
        
    Raises:
        CLIFileNotFoundError: If file doesn't exist
        CLIPermissionError: If file is not readable
    """
    path = Path(file_path)
    
    if not path.exists():
        raise CLIFileNotFoundError(
            file_path,
            suggestion=f"Check the {file_type} path and ensure it exists"
        )
    
    if not path.is_file():
        raise CLIValidationError(
            f"Path is not a file: {file_path}",
            parameter="file_path",
            value=file_path,
            suggestion=f"Provide a valid {file_type} path"
        )
    
    if not os.access(file_path, os.R_OK):
        raise CLIPermissionError(
            file_path,
            operation="read",
            suggestion=f"Check {file_type} permissions or run with appropriate privileges"
        )


def validate_directory_exists(dir_path: str, dir_type: str = "directory") -> None:
    """Validate that a directory exists and is accessible.
    
    Args:
        dir_path: Path to directory
        dir_type: Type of directory for error message
        
    Raises:
        CLIDirectoryNotFoundError: If directory doesn't exist
        CLIPermissionError: If directory is not accessible
    """
    path = Path(dir_path)
    
    if not path.exists():
        raise CLIDirectoryNotFoundError(
            dir_path,
            suggestion=f"Check the {dir_type} path and ensure it exists"
        )
    
    if not path.is_dir():
        raise CLIValidationError(
            f"Path is not a directory: {dir_path}",
            parameter="dir_path",
            value=dir_path,
            suggestion=f"Provide a valid {dir_type} path"
        )
    
    if not os.access(dir_path, os.R_OK | os.X_OK):
        raise CLIPermissionError(
            dir_path,
            operation="access",
            suggestion=f"Check {dir_type} permissions or run with appropriate privileges"
        )


def validate_output_file_writable(file_path: str, create_dirs: bool = True) -> None:
    """Validate that an output file can be written.
    
    Args:
        file_path: Path to output file
        create_dirs: If True, create parent directories if they don't exist
        
    Raises:
        CLIPermissionError: If file/directory is not writable
        CLIValidationError: If path is invalid
    """
    path = Path(file_path)
    
    # Check if parent directory exists
    parent_dir = path.parent
    if not parent_dir.exists():
        if create_dirs:
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {parent_dir}")
            except OSError as e:
                raise CLIPermissionError(
                    str(parent_dir),
                    operation="create directory",
                    details=str(e),
                    suggestion="Check directory permissions or specify a different output path"
                )
        else:
            raise CLIDirectoryNotFoundError(
                str(parent_dir),
                suggestion="Create the directory or use --create-dirs option"
            )
    
    # Check if parent directory is writable
    if not os.access(parent_dir, os.W_OK):
        raise CLIPermissionError(
            str(parent_dir),
            operation="write",
            suggestion="Check directory permissions or specify a different output path"
        )
    
    # If file exists, check if it's writable
    if path.exists():
        if not path.is_file():
            raise CLIValidationError(
                f"Output path exists but is not a file: {file_path}",
                parameter="output",
                value=file_path,
                suggestion="Specify a different output file path"
            )
        
        if not os.access(file_path, os.W_OK):
            raise CLIPermissionError(
                file_path,
                operation="write",
                suggestion="Check file permissions or specify a different output path"
            )


def validate_database_path(db_path: str, must_exist: bool = False) -> None:
    """Validate database file path.
    
    Args:
        db_path: Path to database file
        must_exist: If True, database must already exist
        
    Raises:
        CLIFileNotFoundError: If must_exist=True and file doesn't exist
        CLIPermissionError: If file/directory is not accessible
    """
    path = Path(db_path)
    
    if must_exist:
        validate_file_exists(db_path, "database file")
    else:
        # Check if parent directory exists and is writable
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created database directory: {parent_dir}")
            except OSError as e:
                raise CLIPermissionError(
                    str(parent_dir),
                    operation="create directory",
                    details=str(e),
                    suggestion="Check directory permissions or specify a different database path"
                )
        
        if not os.access(parent_dir, os.W_OK):
            raise CLIPermissionError(
                str(parent_dir),
                operation="write",
                suggestion="Check directory permissions or specify a different database path"
            )


# Data Quality Validation

def validate_csd_resource(
    resource_name: str,
    resource_type: str,
    group_name: str,
    status: str = None,
    program_name: str = None,
    dataset_name: str = None,
    language: str = None
) -> List[str]:
    """Validate a complete CSD resource definition.
    
    Args:
        resource_name: Resource name
        resource_type: Resource type (TRANSACTION, PROGRAM, FILE, MAPSET)
        group_name: Group name
        status: Status (ENABLED/DISABLED)
        program_name: Program name (for TRANSACTION)
        dataset_name: Dataset name (for FILE)
        language: Language (for PROGRAM)
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate based on resource type
    if resource_type == 'TRANSACTION':
        is_valid, error = validate_transaction_id(resource_name)
        if not is_valid:
            errors.append(error)
        
        if program_name:
            is_valid, error = validate_program_name(program_name)
            if not is_valid:
                errors.append(f"Program name: {error}")
    
    elif resource_type == 'PROGRAM':
        is_valid, error = validate_program_name(resource_name)
        if not is_valid:
            errors.append(error)
        
        if language:
            is_valid, error = validate_language(language)
            if not is_valid:
                errors.append(f"Language: {error}")
    
    elif resource_type == 'FILE':
        # File names follow similar rules to program names
        is_valid, error = validate_program_name(resource_name)
        if not is_valid:
            errors.append(error)
        
        if dataset_name:
            is_valid, error = validate_dataset_name(dataset_name)
            if not is_valid:
                errors.append(f"Dataset name: {error}")
    
    elif resource_type == 'MAPSET':
        # Mapset names follow similar rules to program names
        is_valid, error = validate_program_name(resource_name)
        if not is_valid:
            errors.append(error)
    
    # Validate group name
    is_valid, error = validate_group_name(group_name)
    if not is_valid:
        errors.append(f"Group name: {error}")
    
    # Validate status if provided
    if status:
        is_valid, error = validate_status(status)
        if not is_valid:
            errors.append(f"Status: {error}")
    
    return errors


def check_orphaned_references(
    transactions: list,
    programs: list
) -> List[Dict[str, str]]:
    """Check for orphaned references (transactions pointing to non-existent programs).
    
    Args:
        transactions: List of CICSTransaction objects
        programs: List of CICSProgram objects
        
    Returns:
        List of dictionaries describing orphaned references
    """
    orphaned = []
    
    # Build set of program names
    program_names = {p.resource_name for p in programs}
    
    # Check each transaction
    for trans in transactions:
        if trans.program_name and trans.program_name not in program_names:
            orphaned.append({
                'transaction_id': trans.resource_name,
                'program_name': trans.program_name,
                'group_name': trans.group_name,
                'issue': f"Transaction '{trans.resource_name}' references program '{trans.program_name}' which is not defined"
            })
    
    return orphaned


def check_duplicate_resources(resources: list) -> Dict[str, List]:
    """Check for duplicate resource names.
    
    Args:
        resources: List of CICSResource objects
        
    Returns:
        Dictionary mapping resource names to list of duplicate entries
    """
    from collections import defaultdict
    
    duplicates = defaultdict(list)
    
    for resource in resources:
        key = (resource.resource_name, resource.resource_type)
        duplicates[key].append(resource)
    
    # Filter to only actual duplicates
    return {
        f"{rtype}:{rname}": entries
        for (rname, rtype), entries in duplicates.items()
        if len(entries) > 1
    }


# CLI Option Validation

def validate_option_combination(
    options: Dict[str, any],
    rules: List[Dict[str, any]]
) -> List[str]:
    """Validate CLI option combinations against rules.
    
    Args:
        options: Dictionary of option names to values
        rules: List of validation rules
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    for rule in rules:
        rule_type = rule.get('type')
        
        if rule_type == 'mutually_exclusive':
            # Check that only one of the options is set
            exclusive_options = rule.get('options', [])
            set_options = [opt for opt in exclusive_options if options.get(opt)]
            
            if len(set_options) > 1:
                errors.append(
                    f"Options {', '.join(set_options)} are mutually exclusive. "
                    f"Please specify only one."
                )
        
        elif rule_type == 'requires':
            # Check that if option A is set, option B must also be set
            option_a = rule.get('option')
            option_b = rule.get('requires')
            
            if options.get(option_a) and not options.get(option_b):
                errors.append(
                    f"Option '{option_a}' requires '{option_b}' to be specified"
                )
        
        elif rule_type == 'conflicts':
            # Check that options A and B are not both set
            option_a = rule.get('option')
            option_b = rule.get('conflicts')
            
            if options.get(option_a) and options.get(option_b):
                errors.append(
                    f"Option '{option_a}' conflicts with '{option_b}'. "
                    f"Please specify only one."
                )
    
    return errors
