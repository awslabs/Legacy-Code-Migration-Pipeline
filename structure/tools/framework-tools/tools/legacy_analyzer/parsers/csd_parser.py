"""CICS System Definition (CSD) file parser.

This module parses CICS CSD files exported via DFHCSDUP and converts them
to CSV format for loading into the inventory database.
"""

import re
import csv
import os
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field

from ..constants import (
    FILE_SIZE_LARGE_BYTES,
    PROGRESS_REPORT_INTERVAL,
    DEFAULT_CACHE_SIZE,
    DEFAULT_CACHE_ENABLED,
    STATUS_ENABLED,
    STATUS_DISABLED,
)


logger = logging.getLogger(__name__)


@dataclass
class CICSResource:
    """Base class for CICS resource definitions."""
    resource_name: str
    resource_type: str
    group_name: str
    status: str = "ENABLED"
    description: Optional[str] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class CICSTransaction(CICSResource):
    """CICS Transaction definition."""
    program_name: Optional[str] = None
    
    def __post_init__(self):
        self.resource_type = "TRANSACTION"


@dataclass
class CICSProgram(CICSResource):
    """CICS Program definition."""
    language: Optional[str] = None
    transaction_id: Optional[str] = None
    
    def __post_init__(self):
        self.resource_type = "PROGRAM"


@dataclass
class CICSFile(CICSResource):
    """CICS File definition."""
    dataset_name: Optional[str] = None
    
    def __post_init__(self):
        self.resource_type = "FILE"


@dataclass
class CICSMapset(CICSResource):
    """CICS Mapset definition."""
    
    def __post_init__(self):
        self.resource_type = "MAPSET"


@dataclass
class CSDData:
    """Container for parsed CSD data."""
    transactions: List[CICSTransaction] = field(default_factory=list)
    programs: List[CICSProgram] = field(default_factory=list)
    files: List[CICSFile] = field(default_factory=list)
    mapsets: List[CICSMapset] = field(default_factory=list)
    
    def get_all_resources(self) -> List[CICSResource]:
        """Get all resources as a flat list."""
        return (self.transactions + self.programs + 
                self.files + self.mapsets)


class CSDParser:
    """Parser for CICS System Definition (CSD) files.
    
    Parses CSD files exported via DFHCSDUP and extracts:
    - TRANSACTION definitions with program associations
    - PROGRAM definitions with language and status
    - FILE definitions with dataset mappings
    - MAPSET definitions for screen layouts
    
    Example CSD format:
        DEFINE TRANSACTION(CAUP) GROUP(CARDDEMO)
        DESCRIPTION(CREDIT CARD DEMO ACCOUNT UPDATE)
               PROGRAM(COACTUPC) STATUS(ENABLED) ...
    
    Features:
    - Compiled regex patterns for fast parsing
    - Streaming parser for large files (>10MB)
    - Progress callback support for long operations
    - Optional caching of parsed results
    """
    
    def __init__(
        self,
        enable_cache: bool = DEFAULT_CACHE_ENABLED,
        cache_size: int = DEFAULT_CACHE_SIZE,
        strict_validation: bool = False
    ):
        """Initialize CSD parser with regex patterns.
        
        Args:
            enable_cache: Enable caching of parsed CSD data
            cache_size: Maximum number of cached parse results (LRU)
            strict_validation: Enable strict validation (fail on warnings)
        """
        self._enable_cache = enable_cache
        self._cache_size = cache_size
        self._strict_validation = strict_validation
        self._parse_cache: Dict[str, tuple] = {}  # file_path -> (mtime, CSDData)
        self._cache_hits = 0
        self._cache_misses = 0
        # Pattern to match DEFINE statements
        # Captures: resource_type, resource_name, group_name
        self.define_pattern = re.compile(
            r'^\s*DEFINE\s+(\w+)\(([^)]+)\)\s+GROUP\(([^)]+)\)',
            re.IGNORECASE
        )
        
        # Pattern to match DESCRIPTION on its own line or inline
        # Handles multi-line descriptions by using DOTALL flag
        self.description_pattern = re.compile(
            r'DESCRIPTION\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match PROGRAM attribute
        # Can appear anywhere in the definition
        self.program_pattern = re.compile(
            r'PROGRAM\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match STATUS attribute
        # Handles STATUS appearing on any line
        self.status_pattern = re.compile(
            r'STATUS\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match DSNAME attribute
        # Handles long dataset names that might wrap
        self.dsname_pattern = re.compile(
            r'DSNAME\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match LANGUAGE attribute
        # Can appear on any line in PROGRAM definitions
        self.language_pattern = re.compile(
            r'LANGUAGE\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match TRANSID attribute
        # Can appear on any line in PROGRAM definitions
        self.transid_pattern = re.compile(
            r'TRANSID\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match DSNAME01 attribute (for LIBRARY resources)
        # Some resources use numbered DSNAME attributes
        self.dsname01_pattern = re.compile(
            r'DSNAME01\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Pattern to match any attribute in format ATTR(value)
        # Useful for extracting any attribute generically
        self.generic_attribute_pattern = re.compile(
            r'(\w+)\(([^)]+)\)',
            re.IGNORECASE | re.DOTALL
        )
    
    def parse_file(
        self, 
        file_path: str,
        use_streaming: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> CSDData:
        """Parse a CSD file and extract all resource definitions.
        
        Args:
            file_path: Path to CSD file
            use_streaming: If True, use streaming parser for large files (>10MB)
            progress_callback: Optional callback function(current, total, message)
                             for progress reporting
            
        Returns:
            CSDData object containing all parsed resources
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
            ValueError: If file format is invalid
        """
        logger.info(f"Parsing CSD file: {file_path}")
        
        # Check cache if enabled
        if self._enable_cache:
            cached_result = self._get_from_cache(file_path)
            if cached_result is not None:
                self._cache_hits += 1
                logger.debug(
                    f"Cache hit for {file_path} "
                    f"(hits: {self._cache_hits}, misses: {self._cache_misses})"
                )
                return cached_result
            self._cache_misses += 1
        
        # Check file size to determine parsing strategy
        try:
            file_size = os.path.getsize(file_path)
            
            # Use streaming parser for files > FILE_SIZE_LARGE_BYTES or if explicitly requested
            if use_streaming or file_size > FILE_SIZE_LARGE_BYTES:
                logger.info(
                    f"Using streaming parser for large file "
                    f"({file_size / (1024*1024):.1f} MB)"
                )
                result = self._parse_file_streaming(
                    file_path, 
                    progress_callback=progress_callback
                )
                
                # Cache result if enabled
                if self._enable_cache:
                    self._add_to_cache(file_path, result)
                
                return result
            
        except OSError as e:
            logger.warning(f"Could not determine file size: {e}")
        
        # Standard in-memory parsing for smaller files
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except FileNotFoundError as e:
            logger.error(f"CSD file not found: {file_path}")
            raise FileNotFoundError(f"CSD file not found: {file_path}") from e
        except IOError as e:
            logger.error(f"Error reading CSD file {file_path}: {e}")
            raise IOError(f"Error reading CSD file {file_path}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error reading CSD file {file_path}: {e}")
            raise ValueError(f"Unexpected error reading CSD file {file_path}: {e}") from e
        
        if not content or not content.strip():
            logger.warning(f"CSD file is empty: {file_path}")
            return CSDData()
        
        result = self.parse(content, source_file=file_path, progress_callback=progress_callback)
        
        # Cache result if enabled
        if self._enable_cache:
            self._add_to_cache(file_path, result)
        
        return result
    
    def validate_csd_syntax(self, content: str) -> Dict[str, List[str]]:
        """Validate CSD file syntax before parsing.
        
        Performs basic syntax validation to catch common errors early.
        
        Args:
            content: CSD file content to validate
            
        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        from ..exceptions import CSDSyntaxError
        
        issues = {
            'errors': [],
            'warnings': []
        }
        
        if not content or not content.strip():
            issues['errors'].append("CSD file is empty")
            return issues
        
        lines = content.split('\n')
        define_count = 0
        in_definition = False
        current_def_line = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('*'):
                continue
            
            # Check for DEFINE statements
            if self.define_pattern.match(line):
                define_count += 1
                in_definition = True
                current_def_line = line_num
                
                # Validate DEFINE syntax
                match = self.define_pattern.match(line)
                if match:
                    resource_type = match.group(1).upper()
                    resource_name = match.group(2).strip()
                    group_name = match.group(3).strip()
                    
                    # Validate resource type
                    valid_types = {'TRANSACTION', 'PROGRAM', 'FILE', 'MAPSET', 
                                 'LIBRARY', 'TDQUEUE', 'TSQUEUE', 'GROUP'}
                    if resource_type not in valid_types:
                        issues['warnings'].append(
                            f"Line {line_num}: Unusual resource type '{resource_type}'"
                        )
                    
                    # Validate resource name not empty
                    if not resource_name:
                        issues['errors'].append(
                            f"Line {line_num}: Empty resource name in DEFINE statement"
                        )
                    
                    # Validate group name not empty
                    if not group_name:
                        issues['errors'].append(
                            f"Line {line_num}: Empty group name in DEFINE statement"
                        )
            
            # Check for malformed lines (lines that look like they should be DEFINE but aren't)
            elif 'DEFINE' in stripped.upper() and not stripped.startswith('*'):
                issues['warnings'].append(
                    f"Line {line_num}: Line contains 'DEFINE' but doesn't match expected format"
                )
        
        # Check if file has any DEFINE statements
        if define_count == 0:
            issues['errors'].append(
                "No valid DEFINE statements found in CSD file"
            )
        else:
            issues['warnings'].append(
                f"Found {define_count} DEFINE statements"
            )
        
        return issues
    
    def parse(
        self, 
        content: str, 
        source_file: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> CSDData:
        """Parse CSD content and extract all resource definitions.
        
        Args:
            content: CSD file content
            source_file: Optional source file path for tracking
            progress_callback: Optional callback function(current, total, message)
                             for progress reporting
            
        Returns:
            CSDData object containing all parsed resources
            
        Raises:
            ValueError: If content is invalid or cannot be parsed
        """
        from ..exceptions import CSDSyntaxError
        
        if not content:
            logger.warning("Empty content provided to parse()")
            return CSDData()
        
        # Validate syntax if strict validation is enabled
        if self._strict_validation:
            validation_issues = self.validate_csd_syntax(content)
            if validation_issues['errors']:
                error_msg = "CSD syntax validation failed:\n  " + "\n  ".join(validation_issues['errors'])
                raise CSDSyntaxError(
                    error_msg,
                    details=f"Found {len(validation_issues['errors'])} syntax errors"
                )
            if validation_issues['warnings']:
                logger.warning(
                    f"CSD syntax validation warnings:\n  " + 
                    "\n  ".join(validation_issues['warnings'])
                )
        
        csd_data = CSDData()
        parse_errors = []
        
        try:
            # Split into resource definitions
            definitions = self._split_definitions(content)
            
            total_definitions = len(definitions)
            logger.info(f"Found {total_definitions} resource definitions")
            
            if total_definitions == 0:
                logger.warning("No valid DEFINE statements found in content")
            
            # Report initial progress
            if progress_callback:
                progress_callback(0, total_definitions, "Starting CSD parsing...")
            
            for idx, (line_num, definition) in enumerate(definitions, 1):
                try:
                    resource = self._parse_definition(definition, source_file, line_num)
                    if resource:
                        self._add_resource(csd_data, resource)
                        logger.debug(
                            f"Successfully parsed {resource.resource_type} "
                            f"'{resource.resource_name}' at line {line_num}"
                        )
                except Exception as e:
                    error_msg = f"Error parsing definition at line {line_num}: {e}"
                    logger.warning(error_msg)
                    parse_errors.append((line_num, str(e)))
                    continue
                
                # Report progress every PROGRESS_REPORT_INTERVAL definitions or at the end
                if progress_callback and (idx % PROGRESS_REPORT_INTERVAL == 0 or idx == total_definitions):
                    progress_callback(
                        idx, 
                        total_definitions,
                        f"Parsed {idx}/{total_definitions} definitions"
                    )
            
            logger.info(
                f"Successfully parsed {len(csd_data.transactions)} transactions, "
                f"{len(csd_data.programs)} programs, "
                f"{len(csd_data.files)} files, "
                f"{len(csd_data.mapsets)} mapsets"
            )
            
            if parse_errors:
                logger.warning(
                    f"Encountered {len(parse_errors)} parsing errors. "
                    f"See previous log messages for details."
                )
            
            # Report completion
            if progress_callback:
                progress_callback(
                    total_definitions,
                    total_definitions,
                    f"Parsing complete: {len(csd_data.get_all_resources())} resources"
                )
            
        except Exception as e:
            logger.error(f"Fatal error during CSD parsing: {e}")
            raise ValueError(f"Fatal error during CSD parsing: {e}") from e
        
        return csd_data
    
    def _split_definitions(self, content: str) -> List[tuple]:
        """Split CSD content into individual resource definitions.
        
        Each definition starts with 'DEFINE' and continues until the next
        'DEFINE' or end of file.
        
        Args:
            content: CSD file content
            
        Returns:
            List of (line_number, definition_text) tuples
            
        Raises:
            ValueError: If content cannot be split into lines
        """
        if not content:
            logger.debug("Empty content provided to _split_definitions")
            return []
        
        try:
            definitions = []
            lines = content.split('\n')
            current_def = []
            start_line = 0
            
            logger.debug(f"Splitting {len(lines)} lines into definitions")
            
            for i, line in enumerate(lines, 1):
                # Check if this is a DEFINE line
                if self.define_pattern.match(line):
                    # Save previous definition if exists
                    if current_def:
                        definitions.append((start_line, '\n'.join(current_def)))
                    # Start new definition
                    current_def = [line]
                    start_line = i
                elif current_def:
                    # Continue current definition
                    current_def.append(line)
            
            # Add last definition
            if current_def:
                definitions.append((start_line, '\n'.join(current_def)))
            
            logger.debug(f"Split content into {len(definitions)} definitions")
            return definitions
            
        except Exception as e:
            logger.error(f"Error splitting definitions: {e}")
            raise ValueError(f"Error splitting definitions: {e}") from e
    
    def _parse_definition(
        self, 
        definition: str, 
        source_file: Optional[str],
        line_number: int
    ) -> Optional[CICSResource]:
        """Parse a single resource definition.
        
        Args:
            definition: Resource definition text
            source_file: Source file path
            line_number: Starting line number
            
        Returns:
            Parsed CICSResource or None if unsupported type
            
        Raises:
            ValueError: If definition format is invalid
        """
        if not definition or not definition.strip():
            logger.debug(f"Empty definition at line {line_number}")
            return None
        
        # Extract DEFINE line
        match = self.define_pattern.search(definition)
        if not match:
            logger.debug(f"No DEFINE pattern match at line {line_number}")
            return None
        
        try:
            resource_type = match.group(1).upper()
            resource_name = match.group(2).strip()
            group_name = match.group(3).strip()
            
            # Validate resource name and group name
            if not resource_name:
                raise ValueError(f"Empty resource name at line {line_number}")
            if not group_name:
                raise ValueError(f"Empty group name at line {line_number}")
            
            # Extract common attributes
            description = self._extract_description(definition)
            status = self._extract_status(definition)
            
            # Validate status
            if status not in [STATUS_ENABLED, STATUS_DISABLED]:
                logger.warning(
                    f"Invalid status '{status}' at line {line_number}, "
                    f"defaulting to {STATUS_ENABLED}"
                )
                status = STATUS_ENABLED
            
            # Parse based on resource type
            if resource_type == "TRANSACTION":
                return self._parse_transaction(
                    resource_name, group_name, definition,
                    description, status, source_file, line_number
                )
            elif resource_type == "PROGRAM":
                return self._parse_program(
                    resource_name, group_name, definition,
                    description, status, source_file, line_number
                )
            elif resource_type == "FILE":
                return self._parse_file(
                    resource_name, group_name, definition,
                    description, status, source_file, line_number
                )
            elif resource_type == "MAPSET":
                return self._parse_mapset(
                    resource_name, group_name, definition,
                    description, status, source_file, line_number
                )
            else:
                # Unsupported resource type (LIBRARY, TDQUEUE, etc.)
                logger.debug(
                    f"Skipping unsupported resource type '{resource_type}' "
                    f"at line {line_number}"
                )
                return None
                
        except Exception as e:
            logger.error(
                f"Error parsing definition at line {line_number}: {e}"
            )
            raise ValueError(
                f"Invalid definition format at line {line_number}: {e}"
            ) from e
    
    def _parse_transaction(
        self,
        resource_name: str,
        group_name: str,
        definition: str,
        description: Optional[str],
        status: str,
        source_file: Optional[str],
        line_number: int
    ) -> CICSTransaction:
        """Parse a TRANSACTION definition.
        
        Raises:
            ValueError: If required attributes are missing
        """
        program_name = self._extract_program(definition)
        
        # Validate transaction ID length (should be 4 characters)
        if len(resource_name) > 4:
            logger.warning(
                f"Transaction ID '{resource_name}' exceeds 4 characters "
                f"at line {line_number}"
            )
        
        # Log if program name is missing (optional but common)
        if not program_name:
            logger.debug(
                f"Transaction '{resource_name}' has no PROGRAM attribute "
                f"at line {line_number}"
            )
        
        return CICSTransaction(
            resource_name=resource_name,
            resource_type="TRANSACTION",
            group_name=group_name,
            status=status,
            description=description,
            program_name=program_name,
            source_file=source_file,
            line_number=line_number
        )
    
    def _parse_program(
        self,
        resource_name: str,
        group_name: str,
        definition: str,
        description: Optional[str],
        status: str,
        source_file: Optional[str],
        line_number: int
    ) -> CICSProgram:
        """Parse a PROGRAM definition."""
        language = self._extract_language(definition)
        transaction_id = self._extract_transid(definition)
        
        return CICSProgram(
            resource_name=resource_name,
            resource_type="PROGRAM",
            group_name=group_name,
            status=status,
            description=description,
            language=language,
            transaction_id=transaction_id,
            source_file=source_file,
            line_number=line_number
        )
    
    def _parse_file(
        self,
        resource_name: str,
        group_name: str,
        definition: str,
        description: Optional[str],
        status: str,
        source_file: Optional[str],
        line_number: int
    ) -> CICSFile:
        """Parse a FILE definition."""
        dataset_name = self._extract_dsname(definition)
        
        return CICSFile(
            resource_name=resource_name,
            resource_type="FILE",
            group_name=group_name,
            status=status,
            description=description,
            dataset_name=dataset_name,
            source_file=source_file,
            line_number=line_number
        )
    
    def _parse_mapset(
        self,
        resource_name: str,
        group_name: str,
        definition: str,
        description: Optional[str],
        status: str,
        source_file: Optional[str],
        line_number: int
    ) -> CICSMapset:
        """Parse a MAPSET definition."""
        return CICSMapset(
            resource_name=resource_name,
            resource_type="MAPSET",
            group_name=group_name,
            status=status,
            description=description,
            source_file=source_file,
            line_number=line_number
        )
    
    def _normalize_multiline_value(self, value: str) -> str:
        """Normalize multi-line attribute values.
        
        Removes extra whitespace and newlines from attribute values
        that may span multiple lines in the CSD file.
        
        Args:
            value: Raw attribute value that may contain newlines
            
        Returns:
            Normalized single-line value
        """
        # Replace newlines and multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', value)
        return normalized.strip()
    
    def _extract_description(self, definition: str) -> Optional[str]:
        """Extract DESCRIPTION attribute.
        
        Handles descriptions that may span multiple lines.
        """
        match = self.description_pattern.search(definition)
        if match:
            raw_value = match.group(1)
            return self._normalize_multiline_value(raw_value)
        return None
    
    def _extract_status(self, definition: str) -> str:
        """Extract STATUS attribute, default to ENABLED.
        
        Handles STATUS appearing on any line of multi-line definitions.
        """
        match = self.status_pattern.search(definition)
        if match:
            raw_value = match.group(1)
            return self._normalize_multiline_value(raw_value).upper()
        return "ENABLED"
    
    def _extract_program(self, definition: str) -> Optional[str]:
        """Extract PROGRAM attribute.
        
        Handles PROGRAM appearing on any line of multi-line definitions.
        """
        match = self.program_pattern.search(definition)
        if match:
            raw_value = match.group(1)
            return self._normalize_multiline_value(raw_value)
        return None
    
    def _extract_dsname(self, definition: str) -> Optional[str]:
        """Extract DSNAME attribute.
        
        Handles long dataset names that may span multiple lines.
        """
        match = self.dsname_pattern.search(definition)
        if match:
            raw_value = match.group(1)
            return self._normalize_multiline_value(raw_value)
        return None
    
    def _extract_language(self, definition: str) -> Optional[str]:
        """Extract LANGUAGE attribute.
        
        Handles LANGUAGE appearing on any line of multi-line definitions.
        """
        match = self.language_pattern.search(definition)
        if match:
            raw_value = match.group(1)
            return self._normalize_multiline_value(raw_value).upper()
        return None
    
    def _extract_transid(self, definition: str) -> Optional[str]:
        """Extract TRANSID attribute.
        
        Handles TRANSID appearing on any line of multi-line definitions.
        """
        match = self.transid_pattern.search(definition)
        if match:
            raw_value = match.group(1)
            return self._normalize_multiline_value(raw_value)
        return None
    
    def _add_resource(self, csd_data: CSDData, resource: CICSResource):
        """Add a resource to the appropriate list in CSDData.
        
        Args:
            csd_data: CSDData object to add resource to
            resource: Resource to add
            
        Raises:
            ValueError: If resource type is unknown
        """
        if not resource:
            logger.warning("Attempted to add None resource")
            return
        
        if isinstance(resource, CICSTransaction):
            csd_data.transactions.append(resource)
        elif isinstance(resource, CICSProgram):
            csd_data.programs.append(resource)
        elif isinstance(resource, CICSFile):
            csd_data.files.append(resource)
        elif isinstance(resource, CICSMapset):
            csd_data.mapsets.append(resource)
        else:
            logger.error(f"Unknown resource type: {type(resource)}")
            raise ValueError(f"Unknown resource type: {type(resource)}")
    
    def to_csv(
        self, 
        csd_data: CSDData, 
        output_file: str,
        include_header: bool = True
    ):
        """Convert parsed CSD data to enhanced CSV format.
        
        CSV Format:
            resource_name,resource_type,group_name,status,program_name,dataset_name,description
        
        Args:
            csd_data: Parsed CSD data
            output_file: Output CSV file path
            include_header: Whether to include CSV header row
            
        Raises:
            IOError: If file cannot be written
            ValueError: If csd_data is invalid
        """
        if not csd_data:
            raise ValueError("csd_data cannot be None")
        
        logger.info(f"Writing CSV to: {output_file}")
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                if include_header:
                    writer.writerow([
                        'resource_name',
                        'resource_type',
                        'group_name',
                        'status',
                        'program_name',
                        'dataset_name',
                        'description'
                    ])
                
                # Write all resources
                resources = csd_data.get_all_resources()
                
                if not resources:
                    logger.warning("No resources to write to CSV")
                
                for resource in resources:
                    try:
                        row = [
                            resource.resource_name,
                            resource.resource_type,
                            resource.group_name,
                            resource.status,
                            getattr(resource, 'program_name', '') or '',
                            getattr(resource, 'dataset_name', '') or '',
                            resource.description or ''
                        ]
                        writer.writerow(row)
                    except Exception as e:
                        logger.error(
                            f"Error writing resource '{resource.resource_name}' "
                            f"to CSV: {e}"
                        )
                        raise
            
            logger.info(
                f"Successfully wrote {len(resources)} resources to CSV: {output_file}"
            )
            
        except IOError as e:
            logger.error(f"Error writing CSV file {output_file}: {e}")
            raise IOError(f"Error writing CSV file {output_file}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error writing CSV file {output_file}: {e}")
            raise
    
    def parse_transactions(self, content: str) -> List[CICSTransaction]:
        """Extract only TRANSACTION definitions.
        
        Args:
            content: CSD file content
            
        Returns:
            List of CICSTransaction objects
        """
        csd_data = self.parse(content)
        return csd_data.transactions
    
    def parse_programs(self, content: str) -> List[CICSProgram]:
        """Extract only PROGRAM definitions.
        
        Args:
            content: CSD file content
            
        Returns:
            List of CICSProgram objects
        """
        csd_data = self.parse(content)
        return csd_data.programs
    
    def parse_files(self, content: str) -> List[CICSFile]:
        """Extract only FILE definitions.
        
        Args:
            content: CSD file content
            
        Returns:
            List of CICSFile objects
        """
        csd_data = self.parse(content)
        return csd_data.files
    
    def parse_mapsets(self, content: str) -> List[CICSMapset]:
        """Extract only MAPSET definitions.
        
        Args:
            content: CSD file content
            
        Returns:
            List of CICSMapset objects
        """
        csd_data = self.parse(content)
        return csd_data.mapsets
    
    def _parse_file_streaming(
        self,
        file_path: str,
        progress_callback: Optional[Callable] = None
    ) -> CSDData:
        """Parse CSD file using streaming approach for large files.
        
        This method reads the file line-by-line and processes definitions
        as they are encountered, minimizing memory usage for large files.
        
        Args:
            file_path: Path to CSD file
            progress_callback: Optional callback function(current, total, message)
            
        Returns:
            CSDData object containing all parsed resources
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        logger.info(f"Streaming parse of CSD file: {file_path}")
        
        csd_data = CSDData()
        parse_errors = []
        
        try:
            # First pass: count total definitions for progress reporting
            total_definitions = 0
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if self.define_pattern.match(line):
                        total_definitions += 1
            
            logger.info(f"Found {total_definitions} resource definitions (streaming)")
            
            if progress_callback:
                progress_callback(0, total_definitions, "Starting streaming parse...")
            
            # Second pass: parse definitions
            current_def = []
            start_line = 0
            definitions_processed = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Check if this is a DEFINE line
                    if self.define_pattern.match(line):
                        # Process previous definition if exists
                        if current_def:
                            try:
                                definition_text = '\n'.join(current_def)
                                resource = self._parse_definition(
                                    definition_text,
                                    file_path,
                                    start_line
                                )
                                if resource:
                                    self._add_resource(csd_data, resource)
                                    definitions_processed += 1
                                    
                                    # Report progress every 100 definitions
                                    if progress_callback and definitions_processed % 100 == 0:
                                        progress_callback(
                                            definitions_processed,
                                            total_definitions,
                                            f"Parsed {definitions_processed}/{total_definitions} definitions"
                                        )
                            except Exception as e:
                                error_msg = f"Error parsing definition at line {start_line}: {e}"
                                logger.warning(error_msg)
                                parse_errors.append((start_line, str(e)))
                        
                        # Start new definition
                        current_def = [line]
                        start_line = line_num
                    elif current_def:
                        # Continue current definition
                        current_def.append(line)
            
            # Process last definition
            if current_def:
                try:
                    definition_text = '\n'.join(current_def)
                    resource = self._parse_definition(
                        definition_text,
                        file_path,
                        start_line
                    )
                    if resource:
                        self._add_resource(csd_data, resource)
                        definitions_processed += 1
                except Exception as e:
                    error_msg = f"Error parsing definition at line {start_line}: {e}"
                    logger.warning(error_msg)
                    parse_errors.append((start_line, str(e)))
            
            logger.info(
                f"Successfully parsed {len(csd_data.transactions)} transactions, "
                f"{len(csd_data.programs)} programs, "
                f"{len(csd_data.files)} files, "
                f"{len(csd_data.mapsets)} mapsets (streaming)"
            )
            
            if parse_errors:
                logger.warning(
                    f"Encountered {len(parse_errors)} parsing errors. "
                    f"See previous log messages for details."
                )
            
            # Report completion
            if progress_callback:
                progress_callback(
                    definitions_processed,
                    total_definitions,
                    f"Streaming parse complete: {len(csd_data.get_all_resources())} resources"
                )
            
        except FileNotFoundError as e:
            logger.error(f"CSD file not found: {file_path}")
            raise FileNotFoundError(f"CSD file not found: {file_path}") from e
        except IOError as e:
            logger.error(f"Error reading CSD file {file_path}: {e}")
            raise IOError(f"Error reading CSD file {file_path}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during streaming parse: {e}")
            raise ValueError(f"Unexpected error during streaming parse: {e}") from e
        
        return csd_data
    
    def validate_csd_data(self, csd_data: CSDData) -> Dict[str, List[str]]:
        """Validate parsed CSD data and return validation issues.
        
        Performs comprehensive data quality checks including:
        - Duplicate detection
        - Missing required attributes
        - Orphaned references
        - Invalid attribute values
        - Resource name format validation
        
        Args:
            csd_data: Parsed CSD data to validate
            
        Returns:
            Dictionary of validation issues by category
        """
        from tools.legacy_analyzer.validation import (
            validate_transaction_id,
            validate_program_name,
            validate_group_name,
            validate_dataset_name,
            validate_status,
            check_orphaned_references
        )
        
        issues = {
            'warnings': [],
            'errors': [],
            'info': []
        }
        
        logger.info("Validating parsed CSD data")
        
        # Check for duplicate resource names within each type
        trans_names = [t.resource_name for t in csd_data.transactions]
        prog_names = [p.resource_name for p in csd_data.programs]
        file_names = [f.resource_name for f in csd_data.files]
        mapset_names = [m.resource_name for m in csd_data.mapsets]
        
        # Check for duplicates
        for name in set([n for n in trans_names if trans_names.count(n) > 1]):
            count = trans_names.count(name)
            issues['warnings'].append(
                f"Duplicate transaction ID: {name} (appears {count} times)"
            )
        
        for name in set([n for n in prog_names if prog_names.count(n) > 1]):
            count = prog_names.count(name)
            issues['warnings'].append(
                f"Duplicate program name: {name} (appears {count} times)"
            )
        
        for name in set([n for n in file_names if file_names.count(n) > 1]):
            count = file_names.count(name)
            issues['warnings'].append(
                f"Duplicate file name: {name} (appears {count} times)"
            )
        
        for name in set([n for n in mapset_names if mapset_names.count(n) > 1]):
            count = mapset_names.count(name)
            issues['warnings'].append(
                f"Duplicate mapset name: {name} (appears {count} times)"
            )
        
        # Validate transaction IDs
        for trans in csd_data.transactions:
            is_valid, error = validate_transaction_id(trans.resource_name, strict=True)
            if not is_valid:
                issues['warnings'].append(
                    f"Transaction '{trans.resource_name}': {error}"
                )
            
            # Check for missing program
            if not trans.program_name:
                issues['warnings'].append(
                    f"Transaction '{trans.resource_name}' has no program defined"
                )
            
            # Validate group name
            is_valid, error = validate_group_name(trans.group_name)
            if not is_valid:
                issues['errors'].append(
                    f"Transaction '{trans.resource_name}': {error}"
                )
            
            # Validate status
            if trans.status:
                is_valid, error = validate_status(trans.status)
                if not is_valid:
                    issues['errors'].append(
                        f"Transaction '{trans.resource_name}': {error}"
                    )
        
        # Validate programs
        for prog in csd_data.programs:
            is_valid, error = validate_program_name(prog.resource_name)
            if not is_valid:
                issues['warnings'].append(
                    f"Program '{prog.resource_name}': {error}"
                )
            
            # Validate group name
            is_valid, error = validate_group_name(prog.group_name)
            if not is_valid:
                issues['errors'].append(
                    f"Program '{prog.resource_name}': {error}"
                )
            
            # Validate status
            if prog.status:
                is_valid, error = validate_status(prog.status)
                if not is_valid:
                    issues['errors'].append(
                        f"Program '{prog.resource_name}': {error}"
                    )
        
        # Validate files
        for file in csd_data.files:
            # Check for missing dataset name
            if not file.dataset_name:
                issues['warnings'].append(
                    f"File '{file.resource_name}' has no dataset name defined"
                )
            else:
                # Validate dataset name format
                is_valid, error = validate_dataset_name(file.dataset_name)
                if not is_valid:
                    issues['warnings'].append(
                        f"File '{file.resource_name}': {error}"
                    )
            
            # Validate group name
            is_valid, error = validate_group_name(file.group_name)
            if not is_valid:
                issues['errors'].append(
                    f"File '{file.resource_name}': {error}"
                )
        
        # Validate mapsets
        for mapset in csd_data.mapsets:
            # Validate group name
            is_valid, error = validate_group_name(mapset.group_name)
            if not is_valid:
                issues['errors'].append(
                    f"Mapset '{mapset.resource_name}': {error}"
                )
        
        # Check for orphaned references (transactions pointing to non-existent programs)
        orphaned = check_orphaned_references(csd_data.transactions, csd_data.programs)
        for orphan in orphaned:
            issues['warnings'].append(orphan['issue'])
        
        # Check for disabled resources
        disabled_count = sum(
            1 for r in csd_data.get_all_resources()
            if r.status and r.status.upper() == 'DISABLED'
        )
        if disabled_count > 0:
            issues['info'].append(
                f"Found {disabled_count} DISABLED resources"
            )
        
        # Summary info
        issues['info'].append(
            f"Total resources: {len(csd_data.get_all_resources())}"
        )
        issues['info'].append(
            f"Transactions: {len(csd_data.transactions)}"
        )
        issues['info'].append(
            f"Programs: {len(csd_data.programs)}"
        )
        issues['info'].append(
            f"Files: {len(csd_data.files)}"
        )
        issues['info'].append(
            f"Mapsets: {len(csd_data.mapsets)}"
        )
        
        # Log validation results
        if issues['errors']:
            logger.error(f"Validation found {len(issues['errors'])} errors")
            for error in issues['errors']:
                logger.error(f"  - {error}")
        
        if issues['warnings']:
            logger.warning(f"Validation found {len(issues['warnings'])} warnings")
            for warning in issues['warnings']:
                logger.warning(f"  - {warning}")
        
        if not issues['errors'] and not issues['warnings']:
            logger.info("Validation passed with no issues")
        
        return issues
    
    def _get_from_cache(self, file_path: str) -> Optional[CSDData]:
        """Get parsed CSD data from cache if available and not stale.
        
        Args:
            file_path: Path to CSD file
            
        Returns:
            Cached CSDData if available and fresh, None otherwise
        """
        if file_path not in self._parse_cache:
            return None
        
        try:
            # Check if file has been modified since caching
            current_mtime = os.path.getmtime(file_path)
            cached_mtime, cached_data = self._parse_cache[file_path]
            
            if current_mtime == cached_mtime:
                return cached_data
            else:
                # File modified, invalidate cache entry
                del self._parse_cache[file_path]
                return None
        except OSError:
            # File no longer exists or inaccessible
            if file_path in self._parse_cache:
                del self._parse_cache[file_path]
            return None
    
    def _add_to_cache(self, file_path: str, csd_data: CSDData):
        """Add parsed CSD data to cache with LRU eviction.
        
        Args:
            file_path: Path to CSD file
            csd_data: Parsed CSD data to cache
        """
        try:
            mtime = os.path.getmtime(file_path)
            
            # Implement simple LRU: remove oldest entry if cache is full
            if len(self._parse_cache) >= self._cache_size:
                # Remove first (oldest) entry
                oldest_key = next(iter(self._parse_cache))
                del self._parse_cache[oldest_key]
                logger.debug(f"Cache full, evicted {oldest_key}")
            
            self._parse_cache[file_path] = (mtime, csd_data)
            logger.debug(f"Cached parse result for {file_path}")
            
        except OSError as e:
            logger.warning(f"Could not cache result for {file_path}: {e}")
    
    def clear_cache(self):
        """Clear the parse cache."""
        self._parse_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Parse cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'size': len(self._parse_cache),
            'max_size': self._cache_size,
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': (
                self._cache_hits / (self._cache_hits + self._cache_misses)
                if (self._cache_hits + self._cache_misses) > 0
                else 0.0
            )
        }
