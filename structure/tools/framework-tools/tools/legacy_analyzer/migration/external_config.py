"""
External program and caller configuration management.

This module handles loading and managing external program and caller configuration
from YAML files, storing them in the database, and providing APIs to check if
programs are external or to get external callers.
"""

import yaml
import fnmatch
import sqlite3
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import json


class ExternalConfigError(Exception):
    """Raised when external configuration is invalid or cannot be loaded."""
    pass


class ExternalConfigLoader:
    """Loads and manages external program and caller configuration."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize external configuration loader.
        
        Args:
            db_connection: Database connection object
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def load_external_config(self, config_path: str, verbose: bool = True) -> Dict:
        """
        Load external program and caller configuration from YAML file.
        
        Args:
            config_path: Path to external configuration YAML file
            verbose: If True, print progress messages
            
        Returns:
            Dictionary with loaded configuration statistics
            
        Raises:
            ExternalConfigError: If configuration is invalid or cannot be loaded
        """
        if verbose:
            print(f"Loading external configuration from {config_path}...")
        
        try:
            # Parse YAML configuration file
            config = self._parse_yaml_config(config_path)
            
            # Validate configuration schema
            self._validate_config_schema(config)
            
            # Load external programs into database
            programs_loaded = self._load_external_programs(
                config.get('external_programs', []), 
                verbose
            )
            
            # Load external callers into database
            callers_loaded = self._load_external_callers(
                config.get('external_callers', []), 
                verbose
            )
            
            self.conn.commit()
            
            if verbose:
                print(f"✓ Loaded {programs_loaded} external programs")
                print(f"✓ Loaded {callers_loaded} external callers")
            
            return {
                'programs_loaded': programs_loaded,
                'callers_loaded': callers_loaded,
                'config_path': config_path
            }
            
        except Exception as e:
            self.conn.rollback()
            raise ExternalConfigError(f"Failed to load external configuration: {e}")
    
    def _parse_yaml_config(self, config_path: str) -> Dict:
        """
        Parse YAML configuration file.
        
        Args:
            config_path: Path to YAML file
            
        Returns:
            Parsed configuration dictionary
            
        Raises:
            ExternalConfigError: If file cannot be read or parsed
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                config = {}
            
            return config
            
        except FileNotFoundError:
            raise ExternalConfigError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ExternalConfigError(f"Invalid YAML syntax: {e}")
        except Exception as e:
            raise ExternalConfigError(f"Failed to read configuration file: {e}")
    
    def _validate_config_schema(self, config: Dict) -> None:
        """
        Validate configuration schema.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ExternalConfigError: If configuration schema is invalid
        """
        # Check that config is a dictionary
        if not isinstance(config, dict):
            raise ExternalConfigError("Configuration must be a dictionary")
        
        # Validate external_programs section
        if 'external_programs' in config:
            if not isinstance(config['external_programs'], list):
                raise ExternalConfigError("external_programs must be a list")
            
            for idx, prog_config in enumerate(config['external_programs']):
                if not isinstance(prog_config, dict):
                    raise ExternalConfigError(
                        f"external_programs[{idx}] must be a dictionary"
                    )
                
                # Must have either 'pattern' or 'name'
                if 'pattern' not in prog_config and 'name' not in prog_config:
                    raise ExternalConfigError(
                        f"external_programs[{idx}] must have 'pattern' or 'name'"
                    )
        
        # Validate external_callers section
        if 'external_callers' in config:
            if not isinstance(config['external_callers'], list):
                raise ExternalConfigError("external_callers must be a list")
            
            for idx, caller_config in enumerate(config['external_callers']):
                if not isinstance(caller_config, dict):
                    raise ExternalConfigError(
                        f"external_callers[{idx}] must be a dictionary"
                    )
                
                # Must have 'caller' field
                if 'caller' not in caller_config:
                    raise ExternalConfigError(
                        f"external_callers[{idx}] must have 'caller' field"
                    )
                
                # Must have 'calls' field
                if 'calls' not in caller_config:
                    raise ExternalConfigError(
                        f"external_callers[{idx}] must have 'calls' field"
                    )
                
                if not isinstance(caller_config['calls'], list):
                    raise ExternalConfigError(
                        f"external_callers[{idx}].calls must be a list"
                    )
                
                # Validate each call
                for call_idx, call in enumerate(caller_config['calls']):
                    if not isinstance(call, dict):
                        raise ExternalConfigError(
                            f"external_callers[{idx}].calls[{call_idx}] must be a dictionary"
                        )
                    
                    if 'target' not in call:
                        raise ExternalConfigError(
                            f"external_callers[{idx}].calls[{call_idx}] must have 'target' field"
                        )
    
    def _load_external_programs(self, programs: List[Dict], verbose: bool = True) -> int:
        """
        Load external programs into database.
        
        Args:
            programs: List of external program configurations
            verbose: If True, print progress messages
            
        Returns:
            Number of programs loaded
        """
        count = 0
        created_date = datetime.now().strftime('%Y-%m-%d')
        
        for prog_config in programs:
            # Get pattern or name
            pattern = prog_config.get('pattern') or prog_config.get('name')
            program_type = prog_config.get('type', 'EXTERNAL')
            scope = prog_config.get('scope', 'EXTERNAL')
            
            # Determine if it's a pattern (contains wildcards)
            is_pattern = self._is_wildcard_pattern(pattern)
            
            # Insert into database
            self.cursor.execute("""
                INSERT INTO external_program_config 
                (pattern, program_type, scope, is_pattern, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern, program_type, scope, is_pattern, created_date))
            
            count += 1
            
            if verbose and count % 10 == 0:
                print(f"  Loaded {count} external programs...")
        
        return count
    
    def _load_external_callers(self, callers: List[Dict], verbose: bool = True) -> int:
        """
        Load external callers into database.
        
        Args:
            callers: List of external caller configurations
            verbose: If True, print progress messages
            
        Returns:
            Number of caller entries loaded
        """
        count = 0
        created_date = datetime.now().strftime('%Y-%m-%d')
        
        for caller_config in callers:
            caller_name = caller_config['caller']
            calls = caller_config.get('calls', [])
            
            for call in calls:
                target_program = call['target']
                call_type = call.get('type', 'PROGRAM_CALL')
                
                # Extract metadata (everything except 'target' and 'type')
                metadata = {k: v for k, v in call.items() if k not in ['target', 'type']}
                metadata_json = json.dumps(metadata) if metadata else None
                
                # Insert into database
                self.cursor.execute("""
                    INSERT INTO external_caller_config 
                    (caller_name, target_program, call_type, metadata_json, created_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (caller_name, target_program, call_type, metadata_json, created_date))
                
                count += 1
            
            if verbose and count % 10 == 0:
                print(f"  Loaded {count} external caller entries...")
        
        return count
    
    def _is_wildcard_pattern(self, pattern: str) -> bool:
        """
        Check if pattern contains wildcards.
        
        Args:
            pattern: Pattern string
            
        Returns:
            True if pattern contains wildcards (* or ?), False otherwise
        """
        return '*' in pattern or '?' in pattern
    
    def is_external_program(self, program_name: str) -> bool:
        """
        Check if a program is configured as external.
        
        Args:
            program_name: Program name to check
            
        Returns:
            True if program is external, False otherwise
        """
        # Get all external program patterns
        self.cursor.execute("""
            SELECT pattern, is_pattern FROM external_program_config
        """)
        
        for pattern, is_pattern in self.cursor.fetchall():
            if is_pattern:
                # Use pattern matching
                if fnmatch.fnmatch(program_name, pattern):
                    return True
            else:
                # Exact match
                if program_name == pattern:
                    return True
        
        return False
    
    def get_external_programs(self) -> Set[str]:
        """
        Get set of all external program names (exact matches only, not patterns).
        
        Returns:
            Set of external program names
        """
        self.cursor.execute("""
            SELECT pattern FROM external_program_config
            WHERE is_pattern = 0
        """)
        
        return {row[0] for row in self.cursor.fetchall()}
    
    def get_external_patterns(self) -> List[str]:
        """
        Get list of all external program patterns.
        
        Returns:
            List of external program patterns
        """
        self.cursor.execute("""
            SELECT pattern FROM external_program_config
            WHERE is_pattern = 1
        """)
        
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_external_callers(self, target_program: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Get external callers, optionally filtered by target program.
        
        Args:
            target_program: Optional target program to filter by
            
        Returns:
            Dictionary mapping caller name to list of call objects
        """
        if target_program:
            self.cursor.execute("""
                SELECT caller_name, target_program, call_type, metadata_json
                FROM external_caller_config
                WHERE target_program = ?
            """, (target_program,))
        else:
            self.cursor.execute("""
                SELECT caller_name, target_program, call_type, metadata_json
                FROM external_caller_config
            """)
        
        callers = {}
        
        for caller_name, target, call_type, metadata_json in self.cursor.fetchall():
            if caller_name not in callers:
                callers[caller_name] = []
            
            call_info = {
                'target': target,
                'type': call_type
            }
            
            # Add metadata if present
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                    call_info['metadata'] = metadata
                except json.JSONDecodeError:
                    pass
            
            callers[caller_name].append(call_info)
        
        return callers
    
    def matches_external_pattern(self, program_name: str, patterns: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if program name matches any external pattern.
        
        Args:
            program_name: Program name to check
            patterns: Optional list of patterns to check against (if None, queries database)
            
        Returns:
            Tuple of (matches, matched_pattern) where matches is True if program matches
            any pattern, and matched_pattern is the pattern that matched (or None)
        """
        if patterns is None:
            patterns = self.get_external_patterns()
        
        for pattern in patterns:
            if fnmatch.fnmatch(program_name, pattern):
                return True, pattern
        
        return False, None
    
    def clear_external_config(self, verbose: bool = True) -> None:
        """
        Clear all external configuration from database.
        
        Args:
            verbose: If True, print progress messages
        """
        if verbose:
            print("Clearing external configuration...")
        
        self.cursor.execute("DELETE FROM external_program_config")
        programs_deleted = self.cursor.rowcount
        
        self.cursor.execute("DELETE FROM external_caller_config")
        callers_deleted = self.cursor.rowcount
        
        self.conn.commit()
        
        if verbose:
            print(f"✓ Deleted {programs_deleted} external programs")
            print(f"✓ Deleted {callers_deleted} external callers")
    
    def get_config_summary(self) -> Dict:
        """
        Get summary of loaded external configuration.
        
        Returns:
            Dictionary with configuration statistics
        """
        # Count external programs
        self.cursor.execute("""
            SELECT COUNT(*) FROM external_program_config
        """)
        total_programs = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            SELECT COUNT(*) FROM external_program_config WHERE is_pattern = 1
        """)
        pattern_programs = self.cursor.fetchone()[0]
        
        # Count external callers
        self.cursor.execute("""
            SELECT COUNT(DISTINCT caller_name) FROM external_caller_config
        """)
        unique_callers = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            SELECT COUNT(*) FROM external_caller_config
        """)
        total_calls = self.cursor.fetchone()[0]
        
        return {
            'total_external_programs': total_programs,
            'pattern_programs': pattern_programs,
            'exact_programs': total_programs - pattern_programs,
            'unique_external_callers': unique_callers,
            'total_external_calls': total_calls
        }


def load_external_config(db_connection: sqlite3.Connection, config_path: str, verbose: bool = True) -> Dict:
    """
    Convenience function to load external configuration.
    
    Args:
        db_connection: Database connection object
        config_path: Path to external configuration YAML file
        verbose: If True, print progress messages
        
    Returns:
        Dictionary with loaded configuration statistics
        
    Raises:
        ExternalConfigError: If configuration is invalid or cannot be loaded
    """
    loader = ExternalConfigLoader(db_connection)
    return loader.load_external_config(config_path, verbose)


def is_external_program(db_connection: sqlite3.Connection, program_name: str) -> bool:
    """
    Convenience function to check if a program is external.
    
    Args:
        db_connection: Database connection object
        program_name: Program name to check
        
    Returns:
        True if program is external, False otherwise
    """
    loader = ExternalConfigLoader(db_connection)
    return loader.is_external_program(program_name)


def get_external_callers(db_connection: sqlite3.Connection, target_program: Optional[str] = None) -> Dict[str, List[Dict]]:
    """
    Convenience function to get external callers.
    
    Args:
        db_connection: Database connection object
        target_program: Optional target program to filter by
        
    Returns:
        Dictionary mapping caller name to list of call objects
    """
    loader = ExternalConfigLoader(db_connection)
    return loader.get_external_callers(target_program)
