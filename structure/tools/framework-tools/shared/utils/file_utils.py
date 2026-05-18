"""
Common file operations and utilities.

This module provides file handling utilities used across multiple tools
in the Migration Toolkit.
"""

import os
import pathlib
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory_path: Union[str, pathlib.Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        path = pathlib.Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False


def get_file_extension(file_path: Union[str, pathlib.Path]) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (without the dot), empty string if no extension
    """
    path = pathlib.Path(file_path)
    return path.suffix.lstrip('.')


def normalize_path(file_path: Union[str, pathlib.Path]) -> str:
    """
    Normalize a file path to use forward slashes.
    
    Args:
        file_path: Path to normalize
        
    Returns:
        Normalized path string with forward slashes
    """
    path = pathlib.Path(file_path)
    # Just normalize separators without resolving to absolute path
    return str(path).replace('\\', '/')


def safe_file_read(file_path: Union[str, pathlib.Path], 
                   encoding: str = 'utf-8',
                   fallback_encodings: Optional[List[str]] = None) -> Optional[str]:
    """
    Safely read a file with encoding fallback.
    
    Args:
        file_path: Path to the file
        encoding: Primary encoding to try
        fallback_encodings: List of fallback encodings to try
        
    Returns:
        File contents as string, or None if reading failed
    """
    if fallback_encodings is None:
        fallback_encodings = ['latin-1', 'cp1252', 'iso-8859-1']
    
    path = pathlib.Path(file_path)
    
    if not path.exists():
        logger.error(f"File does not exist: {file_path}")
        return None
    
    # Try primary encoding first
    encodings_to_try = [encoding] + fallback_encodings
    
    for enc in encodings_to_try:
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
                if enc != encoding:
                    logger.warning(f"Used fallback encoding {enc} for {file_path}")
                return content
        except (UnicodeDecodeError, UnicodeError):
            continue
        except (OSError, IOError) as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    logger.error(f"Failed to read file {file_path} with any encoding")
    return None


def safe_file_write(file_path: Union[str, pathlib.Path], 
                    content: str,
                    encoding: str = 'utf-8',
                    create_dirs: bool = True) -> bool:
    """
    Safely write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: Encoding to use
        create_dirs: Whether to create parent directories
        
    Returns:
        True if write was successful, False otherwise
    """
    path = pathlib.Path(file_path)
    
    if create_dirs:
        if not ensure_directory_exists(path.parent):
            return False
    
    try:
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except (OSError, IOError, UnicodeEncodeError) as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        return False


def get_file_size(file_path: Union[str, pathlib.Path]) -> Optional[int]:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, or None if file doesn't exist or can't be accessed
    """
    try:
        path = pathlib.Path(file_path)
        return path.stat().st_size
    except (OSError, FileNotFoundError):
        return None


def is_file_readable(file_path: Union[str, pathlib.Path]) -> bool:
    """
    Check if a file exists and is readable.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is readable, False otherwise
    """
    try:
        path = pathlib.Path(file_path)
        return path.exists() and path.is_file() and os.access(path, os.R_OK)
    except (OSError, TypeError):
        return False


def find_files_by_extension(directory: Union[str, pathlib.Path], 
                           extensions: Union[str, List[str]],
                           recursive: bool = True) -> List[pathlib.Path]:
    """
    Find all files with specified extensions in a directory.
    
    Args:
        directory: Directory to search
        extensions: File extension(s) to search for (with or without dots)
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    path = pathlib.Path(directory)
    
    if not path.exists() or not path.is_dir():
        return []
    
    # Normalize extensions
    if isinstance(extensions, str):
        extensions = [extensions]
    
    normalized_exts = []
    for ext in extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_exts.append(ext.lower())
    
    found_files = []
    
    try:
        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'
            
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in normalized_exts:
                found_files.append(file_path)
                
    except (OSError, PermissionError) as e:
        logger.error(f"Error searching directory {directory}: {e}")
    
    return sorted(found_files)