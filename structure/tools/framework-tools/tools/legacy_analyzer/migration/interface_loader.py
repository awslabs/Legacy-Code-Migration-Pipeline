"""
External Interface Loader

This module loads external interface configuration into database tables.
It supports JSON and CSV formats with automatic format detection.

Configuration Formats:
---------------------

JSON Format (Combined):
    {
      "inbound": [
        {
          "source_name": "EXTERNAL_SYSTEM_A",
          "target_program": "PROGRAM1",
          "dependency_type": "PROGRAM_CALL",
          "system": "Legacy Batch System",
          "description": "Nightly batch job"
        }
      ],
      "outbound": [
        {
          "program_name": "UTILITY_LIB",
          "reason": "configured",
          "description": "Utility library"
        }
      ]
    }

CSV Format (Inbound):
    source_name,target_program,dependency_type,system,description
    EXTERNAL_SYSTEM_A,PROGRAM1,PROGRAM_CALL,Legacy Batch System,Nightly batch job

CSV Format (Outbound):
    program_name,reason,description
    UTILITY_LIB,configured,Utility library

Loading Process:
---------------
1. Auto-detect format from file extension (.json or .csv)
2. Parse configuration data
3. Validate required fields
4. Insert into database tables with duplicate prevention (INSERT OR IGNORE)
5. Preserve metadata as JSON in database
6. Return count of loaded interfaces

Usage:
------
    >>> from interface_loader import ExternalInterfaceLoader
    >>> loader = ExternalInterfaceLoader(db_connection)
    >>> 
    >>> # Load from JSON file
    >>> count = loader.load_inbound_interfaces('config/inbound_interfaces.json')
    >>> print(f"Loaded {count} inbound interfaces")
    >>> 
    >>> # Load from CSV file
    >>> count = loader.load_outbound_interfaces('config/outbound_interfaces.csv')
    >>> print(f"Loaded {count} outbound interfaces")
    >>> 
    >>> # Load both from single file
    >>> counts = loader.load_all('config/external_interfaces.json')
    >>> print(f"Loaded {counts['inbound']} inbound, {counts['outbound']} outbound")
"""

import json
import csv
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ExternalInterfaceLoaderError(Exception):
    """Raised when external interface loading fails."""
    pass


class ExternalInterfaceLoader:
    """
    Loads external interface configuration into database tables.
    
    This class handles loading external interface configuration from JSON or CSV
    files into the inbound_interfaces and outbound_interfaces database tables.
    It supports format auto-detection, validation, and duplicate prevention.
    
    Supported Formats:
    -----------------
    
    JSON:
        - Single file with 'inbound' and/or 'outbound' keys
        - Separate files (auto-detected from filename)
        - Flexible metadata support
    
    CSV:
        - Header row required
        - Interface type auto-detected from filename
        - Standard fields plus optional metadata
    
    Required Fields:
    ---------------
    
    Inbound interfaces:
        - source_name: Name of external system calling into our codebase
        - target_program: Program in our codebase being called
        - dependency_type: Type of call (PROGRAM_CALL, CICS_LINK, etc.)
    
    Outbound interfaces:
        - program_name: Name of external program
    
    Optional Fields:
    ---------------
    
    Inbound interfaces:
        - system: Description of external system
        - description: Additional details
        - Any other fields (stored in metadata JSON)
    
    Outbound interfaces:
        - reason: Why it's external ("configured", "missing_source_code", etc.)
        - description: Additional details
        - Any other fields (stored in metadata JSON)
    
    Database Operations:
    -------------------
    
    All insert operations use INSERT OR IGNORE to prevent duplicates:
        - Inbound: UNIQUE constraint on (source_name, target_program, dependency_type)
        - Outbound: UNIQUE constraint on program_name
    
    Metadata is stored as JSON in the database for flexible querying.
    
    Error Handling:
    --------------
    
    Raises ExternalInterfaceLoaderError for:
        - Unsupported file formats
        - Invalid JSON/CSV structure
        - Missing required fields
        - Database errors
    
    Example Usage:
    -------------
        >>> loader = ExternalInterfaceLoader(db_connection)
        >>> 
        >>> # Load inbound interfaces from JSON
        >>> try:
        ...     count = loader.load_inbound_interfaces('config/inbound.json')
        ...     print(f"Successfully loaded {count} inbound interfaces")
        ... except ExternalInterfaceLoaderError as e:
        ...     print(f"Error loading interfaces: {e}")
        >>> 
        >>> # Load outbound interfaces from CSV
        >>> count = loader.load_outbound_interfaces('config/outbound.csv')
        >>> 
        >>> # Load both types from single file
        >>> counts = loader.load_all('config/external_interfaces.json')
        >>> print(f"Inbound: {counts['inbound']}, Outbound: {counts['outbound']}")
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize the ExternalInterfaceLoader.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load external interface configuration from JSON or CSV file.
        
        Auto-detects format based on file extension:
        - .json: JSON format
        - .csv: CSV format
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Dict with 'inbound' and/or 'outbound' lists
            Format: {
                'inbound': [{'source_name': ..., 'target_program': ..., ...}],
                'outbound': [{'program_name': ..., 'reason': ..., ...}]
            }
            
        Raises:
            ExternalInterfaceLoaderError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Auto-detect format based on extension
        extension = path.suffix.lower()
        
        if extension == '.json':
            return self.load_json(file_path)
        elif extension == '.csv':
            return self.load_csv(file_path)
        else:
            raise ExternalInterfaceLoaderError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: .json, .csv"
            )
    
    def load_json(self, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Supports both single-file format (with 'inbound' and 'outbound' keys)
        and separate files (inbound_interfaces.json, outbound_interfaces.json).
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict with 'inbound' and/or 'outbound' lists
            
        Raises:
            ExternalInterfaceLoaderError: If JSON is invalid or missing required fields
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ExternalInterfaceLoaderError(
                    "JSON root must be an object/dictionary"
                )
            
            result = {}
            
            # Check for 'inbound' key
            if 'inbound' in data:
                if not isinstance(data['inbound'], list):
                    raise ExternalInterfaceLoaderError(
                        "'inbound' must be a list"
                    )
                result['inbound'] = data['inbound']
            
            # Check for 'outbound' key
            if 'outbound' in data:
                if not isinstance(data['outbound'], list):
                    raise ExternalInterfaceLoaderError(
                        "'outbound' must be a list"
                    )
                result['outbound'] = data['outbound']
            
            # If neither key exists, assume it's a list of interfaces
            # and try to detect type from filename
            if not result:
                if isinstance(data, list):
                    # Try to detect from filename
                    filename = Path(file_path).stem.lower()
                    if 'inbound' in filename:
                        result['inbound'] = data
                    elif 'outbound' in filename:
                        result['outbound'] = data
                    else:
                        raise ExternalInterfaceLoaderError(
                            "JSON must have 'inbound' and/or 'outbound' keys, "
                            "or filename must contain 'inbound' or 'outbound'"
                        )
            
            return result
            
        except json.JSONDecodeError as e:
            raise ExternalInterfaceLoaderError(f"Invalid JSON: {e}")
        except Exception as e:
            if isinstance(e, (ExternalInterfaceLoaderError, FileNotFoundError)):
                raise
            raise ExternalInterfaceLoaderError(f"Failed to load JSON file: {e}")
    
    def load_csv(self, file_path: str, interface_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from CSV file.
        
        Args:
            file_path: Path to CSV file
            interface_type: 'inbound' or 'outbound' (auto-detected from filename if not provided)
            
        Returns:
            Dict with 'inbound' or 'outbound' list
            
        Raises:
            ExternalInterfaceLoaderError: If CSV is invalid or missing required fields
        """
        try:
            # Auto-detect interface type from filename if not provided
            if interface_type is None:
                filename = Path(file_path).stem.lower()
                if 'inbound' in filename:
                    interface_type = 'inbound'
                elif 'outbound' in filename:
                    interface_type = 'outbound'
                else:
                    raise ExternalInterfaceLoaderError(
                        "Cannot auto-detect interface type from filename. "
                        "Filename must contain 'inbound' or 'outbound', "
                        "or interface_type parameter must be provided."
                    )
            
            # Validate interface_type
            if interface_type not in ['inbound', 'outbound']:
                raise ExternalInterfaceLoaderError(
                    f"Invalid interface_type: {interface_type}. "
                    f"Must be 'inbound' or 'outbound'."
                )
            
            # Read CSV file
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                logger.warning(f"CSV file is empty: {file_path}")
                return {interface_type: []}
            
            return {interface_type: rows}
            
        except Exception as e:
            if isinstance(e, (ExternalInterfaceLoaderError, FileNotFoundError)):
                raise
            raise ExternalInterfaceLoaderError(f"Failed to load CSV file: {e}")
    
    def load_inbound_interfaces(self, file_path: str) -> int:
        """
        Load inbound interfaces from configuration file into database.
        
        Args:
            file_path: Path to configuration file (JSON or CSV)
            
        Returns:
            Number of interfaces loaded
            
        Raises:
            ExternalInterfaceLoaderError: If loading fails
        """
        # Load and parse configuration data from file
        # Auto-detects format (JSON or CSV) based on file extension
        data = self.load_from_file(file_path)
        
        if 'inbound' not in data:
            logger.warning(f"No inbound interfaces found in {file_path}")
            return 0
        
        interfaces = data['inbound']
        count = 0
        cursor = self.db.cursor()
        
        try:
            # Process each inbound interface configuration
            for interface in interfaces:
                # Validate required fields
                # These fields are mandatory for inbound interfaces
                if 'source_name' not in interface:
                    raise ExternalInterfaceLoaderError(
                        "Missing required field 'source_name' in inbound interface"
                    )
                if 'target_program' not in interface:
                    raise ExternalInterfaceLoaderError(
                        "Missing required field 'target_program' in inbound interface"
                    )
                if 'dependency_type' not in interface:
                    raise ExternalInterfaceLoaderError(
                        "Missing required field 'dependency_type' in inbound interface"
                    )
                
                # Extract required fields
                source_name = interface['source_name']
                target_program = interface['target_program']
                dependency_type = interface['dependency_type']
                
                # Build metadata JSON from optional fields
                # Metadata stores additional information like system name, description, etc.
                metadata = {}
                if 'system' in interface and interface['system']:
                    metadata['system'] = interface['system']
                if 'description' in interface and interface['description']:
                    metadata['description'] = interface['description']
                
                # Add any other fields to metadata (flexible schema)
                # This allows for custom fields without schema changes
                for key, value in interface.items():
                    if key not in ['source_name', 'target_program', 'dependency_type', 
                                   'system', 'description'] and value:
                        metadata[key] = value
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                # Insert into database with duplicate prevention
                # INSERT OR IGNORE skips if UNIQUE constraint violated
                # UNIQUE constraint: (source_name, target_program, dependency_type)
                cursor.execute("""
                    INSERT OR IGNORE INTO inbound_interfaces 
                    (source_name, target_program, dependency_type, is_configured, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (source_name, target_program, dependency_type, True, metadata_json))
                
                # Track how many were actually inserted (vs duplicates skipped)
                if cursor.rowcount > 0:
                    count += 1
            
            # Commit all inserts at once (more efficient than per-row commits)
            self.db.commit()
            logger.info(f"Loaded {count} inbound interfaces from {file_path}")
            return count
            
        except sqlite3.Error as e:
            self.db.rollback()
            raise ExternalInterfaceLoaderError(f"Database error: {e}")
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ExternalInterfaceLoaderError):
                raise
            raise ExternalInterfaceLoaderError(f"Failed to load inbound interfaces: {e}")
    
    def load_outbound_interfaces(self, file_path: str) -> int:
        """
        Load outbound interfaces from configuration file into database.
        
        Args:
            file_path: Path to configuration file (JSON or CSV)
            
        Returns:
            Number of interfaces loaded
            
        Raises:
            ExternalInterfaceLoaderError: If loading fails
        """
        # Load and parse configuration data from file
        # Auto-detects format (JSON or CSV) based on file extension
        data = self.load_from_file(file_path)
        
        if 'outbound' not in data:
            logger.warning(f"No outbound interfaces found in {file_path}")
            return 0
        
        interfaces = data['outbound']
        count = 0
        cursor = self.db.cursor()
        
        try:
            # Process each outbound interface configuration
            for interface in interfaces:
                # Validate required fields
                # Only program_name is required for outbound interfaces
                if 'program_name' not in interface:
                    raise ExternalInterfaceLoaderError(
                        "Missing required field 'program_name' in outbound interface"
                    )
                
                # Extract fields
                program_name = interface['program_name']
                reason = interface.get('reason', 'configured')  # Default reason if not specified
                
                # Build metadata JSON from optional fields
                # Metadata stores additional information like description, etc.
                metadata = {}
                if 'description' in interface and interface['description']:
                    metadata['description'] = interface['description']
                
                # Add any other fields to metadata (flexible schema)
                # This allows for custom fields without schema changes
                for key, value in interface.items():
                    if key not in ['program_name', 'reason', 'description'] and value:
                        metadata[key] = value
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                # Insert into database with duplicate prevention
                # INSERT OR IGNORE skips if UNIQUE constraint violated
                # UNIQUE constraint: program_name
                cursor.execute("""
                    INSERT OR IGNORE INTO outbound_interfaces 
                    (program_name, reason, metadata)
                    VALUES (?, ?, ?)
                """, (program_name, reason, metadata_json))
                
                # Track how many were actually inserted (vs duplicates skipped)
                if cursor.rowcount > 0:
                    count += 1
            
            # Commit all inserts at once (more efficient than per-row commits)
            self.db.commit()
            logger.info(f"Loaded {count} outbound interfaces from {file_path}")
            return count
            
        except sqlite3.Error as e:
            self.db.rollback()
            raise ExternalInterfaceLoaderError(f"Database error: {e}")
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ExternalInterfaceLoaderError):
                raise
            raise ExternalInterfaceLoaderError(f"Failed to load outbound interfaces: {e}")
    
    def load_all(self, file_path: str) -> Dict[str, int]:
        """
        Load all external interface configuration from a file.
        
        This method loads both inbound and outbound interfaces from a single
        configuration file (if both are present).
        
        Args:
            file_path: Path to configuration file (JSON or CSV)
            
        Returns:
            Dict with counts: {'inbound': N, 'outbound': M}
            
        Raises:
            ExternalInterfaceLoaderError: If loading fails
        """
        # Load configuration data
        data = self.load_from_file(file_path)
        
        counts = {
            'inbound': 0,
            'outbound': 0
        }
        
        # Load inbound interfaces if present
        if 'inbound' in data:
            # Temporarily store data and call load_inbound_interfaces
            # We need to create a temporary method to avoid re-parsing
            interfaces = data['inbound']
            cursor = self.db.cursor()
            
            try:
                for interface in interfaces:
                    # Validate required fields
                    if 'source_name' not in interface:
                        raise ExternalInterfaceLoaderError(
                            "Missing required field 'source_name' in inbound interface"
                        )
                    if 'target_program' not in interface:
                        raise ExternalInterfaceLoaderError(
                            "Missing required field 'target_program' in inbound interface"
                        )
                    if 'dependency_type' not in interface:
                        raise ExternalInterfaceLoaderError(
                            "Missing required field 'dependency_type' in inbound interface"
                        )
                    
                    # Extract fields
                    source_name = interface['source_name']
                    target_program = interface['target_program']
                    dependency_type = interface['dependency_type']
                    
                    # Build metadata
                    metadata = {}
                    if 'system' in interface and interface['system']:
                        metadata['system'] = interface['system']
                    if 'description' in interface and interface['description']:
                        metadata['description'] = interface['description']
                    
                    for key, value in interface.items():
                        if key not in ['source_name', 'target_program', 'dependency_type', 
                                       'system', 'description'] and value:
                            metadata[key] = value
                    
                    metadata_json = json.dumps(metadata) if metadata else None
                    
                    # Insert into database
                    cursor.execute("""
                        INSERT OR IGNORE INTO inbound_interfaces 
                        (source_name, target_program, dependency_type, is_configured, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    """, (source_name, target_program, dependency_type, True, metadata_json))
                    
                    if cursor.rowcount > 0:
                        counts['inbound'] += 1
                
            except sqlite3.Error as e:
                self.db.rollback()
                raise ExternalInterfaceLoaderError(f"Database error loading inbound: {e}")
        
        # Load outbound interfaces if present
        if 'outbound' in data:
            interfaces = data['outbound']
            cursor = self.db.cursor()
            
            try:
                for interface in interfaces:
                    # Validate required fields
                    if 'program_name' not in interface:
                        raise ExternalInterfaceLoaderError(
                            "Missing required field 'program_name' in outbound interface"
                        )
                    
                    # Extract fields
                    program_name = interface['program_name']
                    reason = interface.get('reason', 'configured')
                    
                    # Build metadata
                    metadata = {}
                    if 'description' in interface and interface['description']:
                        metadata['description'] = interface['description']
                    
                    for key, value in interface.items():
                        if key not in ['program_name', 'reason', 'description'] and value:
                            metadata[key] = value
                    
                    metadata_json = json.dumps(metadata) if metadata else None
                    
                    # Insert into database
                    cursor.execute("""
                        INSERT OR IGNORE INTO outbound_interfaces 
                        (program_name, reason, metadata)
                        VALUES (?, ?, ?)
                    """, (program_name, reason, metadata_json))
                    
                    if cursor.rowcount > 0:
                        counts['outbound'] += 1
                
            except sqlite3.Error as e:
                self.db.rollback()
                raise ExternalInterfaceLoaderError(f"Database error loading outbound: {e}")
        
        self.db.commit()
        logger.info(
            f"Loaded {counts['inbound']} inbound and {counts['outbound']} outbound "
            f"interfaces from {file_path}"
        )
        
        return counts
