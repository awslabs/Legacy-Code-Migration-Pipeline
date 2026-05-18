"""
Entry Point Type Detector for Migration Flows

This module detects all ways an entry point program can be invoked,
including JCL, CICS transactions, CICS program definitions, BMS screens,
and external calls. It collects all callers for each invocation type.

Key Concept:
    A single program can be an entry point in multiple ways.
    Example: PAYROLL1 might be:
        - Invoked by JCL PAYROLL01
        - Invoked by JCL PAYWEEK
        - Invoked by CICS transaction PAY1
        - Defined as CICS program in CSD
        - Called from BMS screen PAYSCREEN
    
    This module detects ALL invocation types and ALL callers for each type.
"""

import sqlite3
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
import json


class EntryPointTypeDetector:
    """
    Detects all invocation types and callers for entry point programs.
    
    This class analyzes the database to identify:
    - JCL invocations (from JCL dependencies)
    - CICS transaction invocations (from CSD transaction definitions)
    - CICS program invocations (from CSD program definitions)
    - Screen invocations (from BMS maps)
    - External call invocations (from program calls)
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize the entry point type detector.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        self.cursor = db_connection.cursor()
        
        # Check which tables exist
        self._has_cics_table = self._check_table_exists('inventory_cics')
        self._has_dependencies_table = self._check_table_exists('artifact_dependencies')
        self._has_bms_table = self._check_table_exists('inventory_bms')
    
    def _check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            return self.cursor.fetchone() is not None
        except Exception:
            return False
    
    def detect_entry_point_types(self, program_name: str) -> List[Dict]:
        """
        Detect all invocation types and callers for an entry point program.
        
        This is the main entry point for detecting how a program can be invoked.
        It returns a list of entry point type objects, each containing:
        - type: The invocation type (JCL, CICS_TRANSACTION, etc.)
        - callers: List of caller objects with source and metadata
        
        Args:
            program_name: The entry point program name
            
        Returns:
            List of entry point type dictionaries with structure:
            [
                {
                    'type': 'JCL',
                    'callers': [
                        {'source': 'PAYROLL01', 'metadata': {...}},
                        {'source': 'PAYWEEK', 'metadata': {...}}
                    ]
                },
                {
                    'type': 'CICS_TRANSACTION',
                    'callers': [
                        {'source': 'PAY1', 'metadata': {...}}
                    ]
                }
            ]
        """
        entry_types = []
        
        # Detect JCL invocations
        jcl_callers = self._detect_jcl_invocations(program_name)
        if jcl_callers:
            entry_types.append({
                'type': 'JCL',
                'callers': jcl_callers
            })
        
        # Detect CICS transaction invocations
        cics_trans_callers = self._detect_cics_transaction_invocations(program_name)
        if cics_trans_callers:
            entry_types.append({
                'type': 'CICS_TRANSACTION',
                'callers': cics_trans_callers
            })
        
        # Detect CICS program invocations (CSD definitions)
        cics_prog_callers = self._detect_cics_program_invocations(program_name)
        if cics_prog_callers:
            entry_types.append({
                'type': 'CICS_PROGRAM',
                'callers': cics_prog_callers
            })
        
        # Detect screen invocations (BMS maps)
        screen_callers = self._detect_screen_invocations(program_name)
        if screen_callers:
            entry_types.append({
                'type': 'SCREEN',
                'callers': screen_callers
            })
        
        # Detect external call invocations
        external_callers = self._detect_external_call_invocations(program_name)
        if external_callers:
            entry_types.append({
                'type': 'EXTERNAL_CALL',
                'callers': external_callers
            })
        
        # If no explicit invocation types found, check if this is an inferred
        # entry point (e.g., Natural MAIN programs not called by any other program).
        # This prevents flows from being flagged as "missing entry point types".
        if not entry_types:
            inferred_callers = self._detect_inferred_entry_type(program_name)
            if inferred_callers:
                entry_types.append({
                    'type': 'INFERRED',
                    'callers': inferred_callers
                })
        
        return entry_types
    
    def _detect_jcl_invocations(self, program_name: str) -> List[Dict]:
        """
        Detect JCL invocations of a program.
        
        Looks for JCL members that execute this program via EXEC PGM statements.
        
        Args:
            program_name: The program to check
            
        Returns:
            List of caller dictionaries with JCL metadata
        """
        if not self._has_dependencies_table:
            return []
        
        callers = []
        
        try:
            # Query for JCL dependencies that execute this program
            self.cursor.execute("""
                SELECT DISTINCT 
                    source_artifact_name,
                    source_file_path,
                    line_number
                FROM artifact_dependencies
                WHERE target_artifact_name = ?
                  AND source_artifact_type = 'JCL'
                  AND dependency_type IN ('EXEC_PGM', 'PROGRAM_CALL')
                ORDER BY source_artifact_name
            """, (program_name,))
            
            rows = self.cursor.fetchall()
            
            for row in rows:
                jcl_name, file_path, line_number = row
                
                metadata = {
                    'jclName': jcl_name
                }
                
                # Add optional metadata
                if file_path:
                    metadata['filePath'] = file_path
                if line_number:
                    metadata['lineNumber'] = line_number
                
                # Try to extract job name and step name from file path or JCL name
                # This is a heuristic - actual implementation may vary
                if jcl_name:
                    metadata['jobName'] = jcl_name  # JCL member name is often the job name
                
                callers.append({
                    'source': jcl_name,
                    'metadata': metadata
                })
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Error detecting JCL invocations for {program_name}: {e}")
        
        return callers
    
    def _detect_cics_transaction_invocations(self, program_name: str) -> List[Dict]:
        """
        Detect CICS transaction invocations of a program.
        
        Looks for CICS transaction definitions that invoke this program.
        
        Args:
            program_name: The program to check
            
        Returns:
            List of caller dictionaries with CICS transaction metadata
        """
        if not self._has_cics_table:
            return []
        
        callers = []
        
        try:
            # Query for CICS transactions that invoke this program
            self.cursor.execute("""
                SELECT DISTINCT
                    resource_name,
                    group_name,
                    status,
                    description
                FROM inventory_cics
                WHERE program_name = ?
                  AND resource_type = 'TRANSACTION'
                ORDER BY resource_name
            """, (program_name,))
            
            rows = self.cursor.fetchall()
            
            for row in rows:
                trans_id, csd_group, status, description = row
                
                metadata = {
                    'transactionId': trans_id
                }
                
                # Add optional metadata
                if csd_group:
                    metadata['csdGroup'] = csd_group
                if status:
                    metadata['status'] = status
                if description:
                    metadata['description'] = description
                
                callers.append({
                    'source': trans_id,
                    'metadata': metadata
                })
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Error detecting CICS transaction invocations for {program_name}: {e}")
        
        return callers
    
    def _detect_cics_program_invocations(self, program_name: str) -> List[Dict]:
        """
        Detect CICS program definitions (CSD entries).
        
        Looks for CICS program definitions in the CSD that define this program.
        This is different from transactions - it's the program definition itself.
        
        Args:
            program_name: The program to check
            
        Returns:
            List of caller dictionaries with CICS program metadata
        """
        if not self._has_cics_table:
            return []
        
        callers = []
        
        try:
            # Query for CICS program definitions
            # Note: For program definitions, resource_name is the program name
            self.cursor.execute("""
                SELECT DISTINCT
                    resource_name,
                    group_name,
                    status,
                    language,
                    description
                FROM inventory_cics
                WHERE resource_name = ?
                  AND resource_type = 'PROGRAM'
                ORDER BY resource_name
            """, (program_name,))
            
            rows = self.cursor.fetchall()
            
            for row in rows:
                prog_name, csd_group, status, language, description = row
                
                metadata = {
                    'programName': prog_name
                }
                
                # Add optional metadata
                if csd_group:
                    metadata['csdGroup'] = csd_group
                if status:
                    metadata['status'] = status
                if language:
                    metadata['language'] = language
                if description:
                    metadata['description'] = description
                
                callers.append({
                    'source': prog_name,
                    'metadata': metadata
                })
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Error detecting CICS program definitions for {program_name}: {e}")
        
        return callers
    
    def _detect_screen_invocations(self, program_name: str) -> List[Dict]:
        """
        Detect screen invocations (BMS maps) of a program.
        
        Looks for BMS maps or screens that invoke this program.
        
        Args:
            program_name: The program to check
            
        Returns:
            List of caller dictionaries with screen metadata
        """
        callers = []
        
        try:
            # Check if we have BMS table
            if self._has_bms_table:
                # Query BMS table for maps that reference this program
                self.cursor.execute("""
                    SELECT DISTINCT
                        map_name,
                        mapset_name,
                        description
                    FROM inventory_bms
                    WHERE program_name = ?
                    ORDER BY map_name
                """, (program_name,))
                
                rows = self.cursor.fetchall()
                
                for row in rows:
                    map_name, mapset_name, description = row
                    
                    metadata = {
                        'screenName': map_name
                    }
                    
                    # Add optional metadata
                    if mapset_name:
                        metadata['mapset'] = mapset_name
                    if description:
                        metadata['description'] = description
                    
                    callers.append({
                        'source': map_name,
                        'metadata': metadata
                    })
            
            # Also check dependencies table for BMS references
            if self._has_dependencies_table:
                self.cursor.execute("""
                    SELECT DISTINCT
                        source_artifact_name,
                        source_file_path
                    FROM artifact_dependencies
                    WHERE target_artifact_name = ?
                      AND source_artifact_type IN ('BMS', 'SCREEN', 'MAP')
                      AND dependency_type IN ('PROGRAM_CALL', 'SCREEN_CALL')
                    ORDER BY source_artifact_name
                """, (program_name,))
                
                rows = self.cursor.fetchall()
                
                for row in rows:
                    screen_name, file_path = row
                    
                    # Avoid duplicates from BMS table
                    if not any(c['source'] == screen_name for c in callers):
                        metadata = {
                            'screenName': screen_name
                        }
                        
                        if file_path:
                            metadata['filePath'] = file_path
                        
                        callers.append({
                            'source': screen_name,
                            'metadata': metadata
                        })
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Error detecting screen invocations for {program_name}: {e}")
        
        return callers
    
    def _detect_external_call_invocations(self, program_name: str) -> List[Dict]:
        """
        Detect external call invocations of a program.
        
        Looks for external programs that call this program directly.
        This is different from internal calls within a flow.
        
        Args:
            program_name: The program to check
            
        Returns:
            List of caller dictionaries with external call metadata
        """
        if not self._has_dependencies_table:
            return []
        
        callers = []
        
        try:
            # Query for program calls from external sources
            # External calls are typically PROGRAM_CALL, CICS_LINK, CICS_XCTL, etc.
            self.cursor.execute("""
                SELECT DISTINCT
                    source_artifact_name,
                    source_artifact_type,
                    dependency_type,
                    source_file_path,
                    line_number
                FROM artifact_dependencies
                WHERE target_artifact_name = ?
                  AND source_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('PROGRAM_CALL', 'CICS_LINK', 'CICS_XCTL', 
                                         'CICS_START', 'EXTERNAL_CALL', 'CALL')
                ORDER BY source_artifact_name
            """, (program_name,))
            
            rows = self.cursor.fetchall()
            
            for row in rows:
                caller_prog, source_type, dep_type, file_path, line_number = row
                
                metadata = {
                    'callingProgram': caller_prog,
                    'callType': dep_type
                }
                
                # Add optional metadata
                if file_path:
                    metadata['filePath'] = file_path
                if line_number:
                    metadata['lineNumber'] = line_number
                
                callers.append({
                    'source': caller_prog,
                    'metadata': metadata
                })
        
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Error detecting external call invocations for {program_name}: {e}")
        
        return callers

    def _detect_inferred_entry_type(self, program_name: str) -> List[Dict]:
        """
        Create an INFERRED entry type for programs with no explicit invocation metadata.

        This handles Natural MAIN programs and other entry points that are identified
        by code analysis (not called by any other program) but have no JCL, CICS,
        or screen invocation records.

        Args:
            program_name: The program to check

        Returns:
            List with a single caller dictionary if program exists in inventory,
            empty list otherwise
        """
        if not self._has_dependencies_table:
            return []

        callers = []

        try:
            # Verify the program exists in inventory with source code
            self.cursor.execute("""
                SELECT artifact_type, file_path, language
                FROM inventory
                WHERE artifact_name = ?
                  AND file_path IS NOT NULL
                  AND file_path != ''
                  AND file_path NOT LIKE 'MISSING/%%'
                LIMIT 1
            """, (program_name,))

            row = self.cursor.fetchone()
            if row:
                artifact_type, file_path, language = row

                metadata = {
                    'artifactType': artifact_type or 'PROGRAM',
                    'confidence': 'INFERRED',
                    'description': 'Entry point inferred from code analysis (not called by other programs)'
                }

                if language:
                    metadata['language'] = language
                if file_path:
                    metadata['filePath'] = file_path

                callers.append({
                    'source': program_name,
                    'metadata': metadata
                })

        except Exception as e:
            print(f"Warning: Error detecting inferred entry type for {program_name}: {e}")

        return callers

    
    def determine_primary_type(self, entry_types: List[Dict]) -> Optional[str]:
        """
        Determine the primary (most common) invocation type.
        
        The primary type is determined by counting the number of callers
        for each type. The type with the most callers is considered primary.
        
        Priority order (if counts are equal):
        1. JCL (batch processing is often primary)
        2. CICS_TRANSACTION (online processing)
        3. CICS_PROGRAM (CSD definition)
        4. SCREEN (screen-driven)
        5. EXTERNAL_CALL (external invocation)
        
        Args:
            entry_types: List of entry point type dictionaries
            
        Returns:
            The primary entry point type, or None if no types
        """
        if not entry_types:
            return None
        
        # Count callers per type
        type_counts = []
        for entry_type in entry_types:
            type_name = entry_type['type']
            caller_count = len(entry_type.get('callers', []))
            type_counts.append((type_name, caller_count))
        
        # Sort by count (descending), then by priority
        priority_order = {
            'JCL': 1,
            'CICS_TRANSACTION': 2,
            'CICS_PROGRAM': 3,
            'SCREEN': 4,
            'EXTERNAL_CALL': 5,
            'INFERRED': 6
        }
        
        type_counts.sort(
            key=lambda x: (-x[1], priority_order.get(x[0], 99))
        )
        
        # Return type with most callers (or highest priority if tied)
        return type_counts[0][0] if type_counts else None
    
    def get_all_callers(self, entry_types: List[Dict]) -> List[str]:
        """
        Get all caller sources across all entry point types.
        
        Args:
            entry_types: List of entry point type dictionaries
            
        Returns:
            List of all caller source names
        """
        callers = []
        for entry_type in entry_types:
            for caller in entry_type.get('callers', []):
                callers.append(caller['source'])
        return callers
    
    def get_entry_type_statistics(self, entry_types: List[Dict]) -> Dict:
        """
        Get statistics about entry point types.
        
        Args:
            entry_types: List of entry point type dictionaries
            
        Returns:
            Dictionary with statistics:
            {
                'total_types': int,
                'total_callers': int,
                'types': {type_name: caller_count},
                'primary_type': str
            }
        """
        stats = {
            'total_types': len(entry_types),
            'total_callers': 0,
            'types': {},
            'primary_type': self.determine_primary_type(entry_types)
        }
        
        for entry_type in entry_types:
            type_name = entry_type['type']
            caller_count = len(entry_type.get('callers', []))
            stats['types'][type_name] = caller_count
            stats['total_callers'] += caller_count
        
        return stats
    
    def detect_multiple_programs(self, program_names: List[str]) -> Dict[str, List[Dict]]:
        """
        Detect entry point types for multiple programs efficiently.
        
        This method batches queries for better performance when analyzing
        many programs at once.
        
        Args:
            program_names: List of program names to analyze
            
        Returns:
            Dictionary mapping program names to their entry point types
        """
        results = {}
        
        for program_name in program_names:
            results[program_name] = self.detect_entry_point_types(program_name)
        
        return results
    
    def has_any_invocation_type(self, program_name: str) -> bool:
        """
        Check if a program has any invocation type defined.
        
        This is a quick check to see if a program is an entry point
        without retrieving all the details.
        
        Args:
            program_name: The program to check
            
        Returns:
            True if program has at least one invocation type, False otherwise
        """
        entry_types = self.detect_entry_point_types(program_name)
        return len(entry_types) > 0
    
    def get_programs_by_invocation_type(self, invocation_type: str) -> List[str]:
        """
        Get all programs that can be invoked via a specific type.
        
        Args:
            invocation_type: The invocation type to filter by
                           (JCL, CICS_TRANSACTION, CICS_PROGRAM, SCREEN, EXTERNAL_CALL)
            
        Returns:
            List of program names that have this invocation type
        """
        programs = set()
        
        if invocation_type == 'JCL' and self._has_dependencies_table:
            self.cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'JCL'
                  AND dependency_type IN ('EXEC_PGM', 'PROGRAM_CALL')
            """)
            programs.update(row[0] for row in self.cursor.fetchall())
        
        elif invocation_type == 'CICS_TRANSACTION' and self._has_cics_table:
            self.cursor.execute("""
                SELECT DISTINCT program_name
                FROM inventory_cics
                WHERE resource_type = 'TRANSACTION'
                  AND program_name IS NOT NULL
            """)
            programs.update(row[0] for row in self.cursor.fetchall())
        
        elif invocation_type == 'CICS_PROGRAM' and self._has_cics_table:
            self.cursor.execute("""
                SELECT DISTINCT resource_name
                FROM inventory_cics
                WHERE resource_type = 'PROGRAM'
            """)
            programs.update(row[0] for row in self.cursor.fetchall())
        
        elif invocation_type == 'SCREEN':
            if self._has_bms_table:
                self.cursor.execute("""
                    SELECT DISTINCT program_name
                    FROM inventory_bms
                    WHERE program_name IS NOT NULL
                """)
                programs.update(row[0] for row in self.cursor.fetchall())
            
            if self._has_dependencies_table:
                self.cursor.execute("""
                    SELECT DISTINCT target_artifact_name
                    FROM artifact_dependencies
                    WHERE source_artifact_type IN ('BMS', 'SCREEN', 'MAP')
                      AND dependency_type IN ('PROGRAM_CALL', 'SCREEN_CALL')
                """)
                programs.update(row[0] for row in self.cursor.fetchall())
        
        elif invocation_type == 'EXTERNAL_CALL' and self._has_dependencies_table:
            self.cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('PROGRAM_CALL', 'CICS_LINK', 'CICS_XCTL',
                                         'CICS_START', 'EXTERNAL_CALL', 'CALL')
            """)
            programs.update(row[0] for row in self.cursor.fetchall())
        
        return sorted(list(programs))
