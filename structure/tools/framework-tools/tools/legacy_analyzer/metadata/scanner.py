"""Metadata file scanner for discovering CICS and other metadata files.

This module provides functionality to automatically discover metadata files
in source code directories, including:
- CSD files (.csd) - CICS System Definition files
- CSV files (.csv) - Exported CICS inventory
- Future: IMS, DB2, MQ metadata files
"""

import os
import logging
import re
from dataclasses import dataclass, field
from typing import List, Set, Optional
from pathlib import Path

from ..constants import (
    MAX_PREVIEW_LINES,
    MAX_PREVIEW_BYTES,
    FILE_EXT_CSD,
    FILE_EXT_CSV,
    FILE_EXT_JCL,
    SKIP_DIRECTORIES,
)


logger = logging.getLogger(__name__)


@dataclass
class MetadataFiles:
    """Container for discovered metadata files."""
    
    csd_files: List[str] = field(default_factory=list)
    csv_files: List[str] = field(default_factory=list)
    other_files: List[str] = field(default_factory=list)
    
    def get_all_files(self) -> List[str]:
        """Get all discovered files as a flat list."""
        return self.csd_files + self.csv_files + self.other_files
    
    def get_file_count(self) -> int:
        """Get total count of discovered files."""
        return len(self.get_all_files())
    
    def __str__(self) -> str:
        """String representation of discovered files."""
        return (
            f"MetadataFiles(csd={len(self.csd_files)}, "
            f"csv={len(self.csv_files)}, "
            f"other={len(self.other_files)})"
        )


class MetadataFileScanner:
    """Scanner for discovering metadata files in source directories.
    
    Automatically discovers and identifies metadata files including:
    - CSD files: CICS System Definition files (*.csd)
    - CSV files: Exported CICS inventory (*.csv, *cics*.csv)
    - Other metadata files (future: IMS, DB2, MQ)
    
    Example usage:
        scanner = MetadataFileScanner()
        metadata = scanner.scan_directory('./examples/code/cobol/carddemoV2')
        
        print(f"Found {len(metadata.csd_files)} CSD files")
        for csd_file in metadata.csd_files:
            print(f"  - {csd_file}")
    """
    
    def __init__(self):
        """Initialize metadata file scanner."""
        # File extension patterns
        self.csd_extensions = {FILE_EXT_CSD}
        self.csv_extensions = {FILE_EXT_CSV}
        
        # File name patterns for CSV files (case-insensitive)
        self.cics_csv_patterns = [
            re.compile(r'.*cics.*\.csv$', re.IGNORECASE),
            re.compile(r'.*inventory.*\.csv$', re.IGNORECASE),
            re.compile(r'.*transaction.*\.csv$', re.IGNORECASE),
        ]
        
        # Directories to skip during scanning
        self.skip_dirs = SKIP_DIRECTORIES
        
        # File patterns to skip
        self.skip_patterns = [
            re.compile(r'^\..+'),  # Hidden files
            re.compile(r'.*\.pyc$'),  # Python bytecode
            re.compile(r'.*\.pyo$'),  # Python optimized
            re.compile(r'.*~$'),  # Backup files
        ]
    
    def scan_directory(
        self,
        root_path: str,
        recursive: bool = True,
        file_types: Optional[Set[str]] = None,
        patterns: Optional[List[str]] = None
    ) -> MetadataFiles:
        """Scan directory for metadata files.
        
        Args:
            root_path: Root directory to scan
            recursive: Whether to scan subdirectories recursively
            file_types: Optional set of file types to scan for.
                       Valid values: 'csd', 'csv', 'all'
                       Default: all types
            patterns: Optional list of glob patterns to filter files.
                     Examples: ['*.csd', '*cics*.csv', 'CARDDEMO.*']
                     If provided, only files matching at least one pattern
                     will be included in the results.
        
        Returns:
            MetadataFiles object containing discovered files
            
        Raises:
            FileNotFoundError: If root_path doesn't exist
            NotADirectoryError: If root_path is not a directory
        """
        # Validate root path
        root_path = os.path.abspath(root_path)
        if not os.path.exists(root_path):
            logger.error(f"Directory not found: {root_path}")
            raise FileNotFoundError(f"Directory not found: {root_path}")
        
        if not os.path.isdir(root_path):
            logger.error(f"Not a directory: {root_path}")
            raise NotADirectoryError(f"Not a directory: {root_path}")
        
        # Default to scanning all file types
        if file_types is None:
            file_types = {'csd', 'csv', 'all'}
        
        # Normalize file types
        file_types = {ft.lower() for ft in file_types}
        if 'all' in file_types:
            file_types = {'csd', 'csv'}
        
        logger.info(
            f"Scanning directory: {root_path} "
            f"(recursive={recursive}, types={file_types}, patterns={patterns})"
        )
        
        metadata = MetadataFiles()
        
        if recursive:
            self._scan_recursive(root_path, metadata, file_types, patterns)
        else:
            self._scan_single_directory(root_path, metadata, file_types, patterns)
        
        logger.info(
            f"Scan complete: found {metadata.get_file_count()} files "
            f"({len(metadata.csd_files)} CSD, {len(metadata.csv_files)} CSV)"
        )
        
        return metadata
    
    def _scan_recursive(
        self,
        root_path: str,
        metadata: MetadataFiles,
        file_types: Set[str],
        patterns: Optional[List[str]] = None
    ):
        """Recursively scan directory tree.
        
        Args:
            root_path: Root directory to scan
            metadata: MetadataFiles object to populate
            file_types: Set of file types to scan for
            patterns: Optional list of glob patterns to filter files
        """
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Filter out directories to skip
                dirnames[:] = [
                    d for d in dirnames
                    if d not in self.skip_dirs
                ]
                
                # Process files in current directory
                for filename in filenames:
                    if self._should_skip_file(filename):
                        continue
                    
                    # Apply pattern filtering if patterns are provided
                    if patterns and not self._matches_any_pattern(filename, patterns):
                        continue
                    
                    file_path = os.path.join(dirpath, filename)
                    self._classify_and_add_file(file_path, metadata, file_types)
        
        except PermissionError as e:
            logger.warning(f"Permission denied accessing directory: {e}")
        except Exception as e:
            logger.error(f"Error during recursive scan: {e}")
            raise
    
    def _scan_single_directory(
        self,
        directory: str,
        metadata: MetadataFiles,
        file_types: Set[str],
        patterns: Optional[List[str]] = None
    ):
        """Scan a single directory (non-recursive).
        
        Args:
            directory: Directory to scan
            metadata: MetadataFiles object to populate
            file_types: Set of file types to scan for
            patterns: Optional list of glob patterns to filter files
        """
        try:
            for filename in os.listdir(directory):
                if self._should_skip_file(filename):
                    continue
                
                # Apply pattern filtering if patterns are provided
                if patterns and not self._matches_any_pattern(filename, patterns):
                    continue
                
                file_path = os.path.join(directory, filename)
                
                # Skip directories in non-recursive mode
                if os.path.isdir(file_path):
                    continue
                
                self._classify_and_add_file(file_path, metadata, file_types)
        
        except PermissionError as e:
            logger.warning(f"Permission denied accessing directory: {e}")
        except Exception as e:
            logger.error(f"Error during single directory scan: {e}")
            raise
    
    def _should_skip_file(self, filename: str) -> bool:
        """Check if file should be skipped.
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if file should be skipped
        """
        for pattern in self.skip_patterns:
            if pattern.match(filename):
                return True
        return False
    
    def _matches_any_pattern(self, filename: str, patterns: List[str]) -> bool:
        """Check if filename matches any of the provided glob patterns.
        
        Pattern matching is case-insensitive to handle files with different
        case conventions (e.g., .CSD vs .csd).
        
        Args:
            filename: Name of file to check
            patterns: List of glob patterns (e.g., ['*.csd', '*cics*.csv'])
            
        Returns:
            True if filename matches at least one pattern
        """
        import fnmatch
        
        # Convert filename to lowercase for case-insensitive matching
        filename_lower = filename.lower()
        
        for pattern in patterns:
            # Convert pattern to lowercase for case-insensitive matching
            pattern_lower = pattern.lower()
            if fnmatch.fnmatch(filename_lower, pattern_lower):
                return True
        return False
    
    def _classify_and_add_file(
        self,
        file_path: str,
        metadata: MetadataFiles,
        file_types: Set[str]
    ):
        """Classify file by type and add to appropriate list.
        
        Args:
            file_path: Path to file
            metadata: MetadataFiles object to populate
            file_types: Set of file types to scan for
        """
        # Skip if not a regular file
        if not os.path.isfile(file_path):
            return
        
        file_type = self.identify_file_type(file_path)
        
        if file_type == 'csd' and 'csd' in file_types:
            metadata.csd_files.append(file_path)
            logger.debug(f"Found CSD file: {file_path}")
        elif file_type == 'csv' and 'csv' in file_types:
            metadata.csv_files.append(file_path)
            logger.debug(f"Found CSV file: {file_path}")
        elif file_type == 'other':
            # Currently not collecting other files, but could in future
            pass
    
    def identify_file_type(self, file_path: str) -> str:
        """Identify metadata file type by extension and content.
        
        This method uses a two-stage identification process:
        1. Extension-based: Quick check using file extension (primary)
        2. Content-based: Peek at file content for validation (secondary)
        
        For files with recognized extensions (.csd, .csv), the extension
        takes precedence. Content validation is used to:
        - Identify files without extensions
        - Provide additional validation (logged as warnings)
        
        Args:
            file_path: Path to file
            
        Returns:
            File type: 'csd', 'csv', or 'other'
        """
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Skip certain file types that shouldn't be identified by content
        # (e.g., JCL files may contain embedded CSD but are primarily JCL)
        skip_content_detection_extensions = {FILE_EXT_JCL, '.proc'}
        
        # Check by extension first (primary identification)
        if ext in self.csd_extensions:
            # Trust the extension, but validate content for logging
            if not self._validate_csd_content(file_path):
                logger.debug(
                    f"File {file_path} has .csd extension but content "
                    f"validation failed (may be empty or non-standard format)"
                )
            return 'csd'
        
        if ext in self.csv_extensions:
            # For CSV files, check filename patterns first
            filename = os.path.basename(file_path)
            if self._is_cics_csv(filename):
                return 'csv'
            
            # If filename doesn't match, check content
            if self._validate_csv_content(file_path):
                logger.debug(
                    f"File {file_path} identified as CICS CSV based on content"
                )
                return 'csv'
            
            # Include all CSV files for now
            return 'csv'
        
        # Skip content-based detection for certain file types
        if ext in skip_content_detection_extensions:
            return 'other'
        
        # For files without recognized extensions, use content-based detection
        if self._validate_csd_content(file_path):
            logger.info(
                f"File {file_path} identified as CSD based on content "
                f"(no .csd extension)"
            )
            return 'csd'
        
        if self._validate_csv_content(file_path):
            logger.info(
                f"File {file_path} identified as CICS CSV based on content "
                f"(no .csv extension)"
            )
            return 'csv'
        
        return 'other'
    
    def _is_cics_csv(self, filename: str) -> bool:
        """Check if CSV filename matches CICS patterns.
        
        Args:
            filename: Name of CSV file
            
        Returns:
            True if filename matches CICS patterns
        """
        for pattern in self.cics_csv_patterns:
            if pattern.match(filename):
                return True
        return False
    
    def _validate_csd_content(self, file_path: str) -> bool:
        """Validate if file content appears to be a CSD file.
        
        CSD files typically contain DEFINE statements for CICS resources.
        This method checks for common CSD patterns in the file content.
        
        The validation looks for CSD keywords at the start of lines (after
        optional whitespace) to avoid false positives from comments or
        embedded text.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if content appears to be CSD format
        """
        try:
            # Read first few lines to check for CSD patterns
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read up to MAX_PREVIEW_LINES or MAX_PREVIEW_BYTES, whichever comes first
                max_bytes = MAX_PREVIEW_BYTES
                max_lines = MAX_PREVIEW_LINES
                bytes_read = 0
                
                # CSD keyword patterns (must be at start of line)
                csd_patterns = [
                    re.compile(r'^\s*DEFINE\s+TRANSACTION', re.IGNORECASE),
                    re.compile(r'^\s*DEFINE\s+PROGRAM', re.IGNORECASE),
                    re.compile(r'^\s*DEFINE\s+FILE', re.IGNORECASE),
                    re.compile(r'^\s*DEFINE\s+MAPSET', re.IGNORECASE),
                    re.compile(r'^\s*DEFINE\s+GROUP', re.IGNORECASE),
                    re.compile(r'^\s*ADD\s+GROUP', re.IGNORECASE),
                    re.compile(r'^\s*DELETE\s+GROUP', re.IGNORECASE),
                    re.compile(r'^\s*INSTALL\s+GROUP', re.IGNORECASE),
                ]
                
                for i, line in enumerate(f):
                    if i >= max_lines or bytes_read >= max_bytes:
                        break
                    bytes_read += len(line.encode('utf-8'))
                    
                    # Check if line matches any CSD pattern
                    for pattern in csd_patterns:
                        if pattern.match(line):
                            return True
                
                return False
                
        except Exception as e:
            logger.debug(f"Error validating CSD content for {file_path}: {e}")
            return False
    
    def _validate_csv_content(self, file_path: str) -> bool:
        """Validate if CSV file content appears to be CICS metadata.
        
        Checks for CICS-related column headers in the CSV file.
        
        Args:
            file_path: Path to CSV file to validate
            
        Returns:
            True if content appears to be CICS metadata CSV
        """
        try:
            # Read first line to check headers
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip().lower()
                
                # Check for CICS-related column headers
                cics_headers = [
                    'resource_name',
                    'resource_type',
                    'transaction',
                    'program',
                    'group_name',
                    'cics',
                    'mapset',
                    'trans_id',
                    'transaction_id'
                ]
                
                # File is likely CICS CSV if it contains CICS-related headers
                for header in cics_headers:
                    if header in first_line:
                        return True
                
                return False
                
        except Exception as e:
            logger.debug(f"Error validating CSV content for {file_path}: {e}")
            return False
    
    def filter_by_pattern(
        self,
        files: List[str],
        pattern: str
    ) -> List[str]:
        """Filter files by glob pattern.
        
        Args:
            files: List of file paths
            pattern: Glob pattern (e.g., '*.csd', '*cics*.csv')
            
        Returns:
            Filtered list of files matching pattern
        """
        import fnmatch
        
        filtered = []
        for file_path in files:
            filename = os.path.basename(file_path)
            if fnmatch.fnmatch(filename, pattern):
                filtered.append(file_path)
        
        return filtered
    
    def get_file_info(self, file_path: str) -> dict:
        """Get detailed information about a metadata file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'type': self.identify_file_type(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'directory': os.path.dirname(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {
                'path': file_path,
                'error': str(e)
            }
