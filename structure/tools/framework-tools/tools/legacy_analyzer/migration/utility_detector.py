"""
Utility program detection for migration flow analysis.

This module identifies utility programs that are shared across multiple flows
based on call frequency and naming patterns.
"""

import fnmatch
from typing import Dict, List, Set, Optional
from datetime import datetime


class UtilityDetector:
    """Detects utility programs shared across multiple flows."""
    
    def __init__(self, db_connection, call_threshold: int = 5):
        """
        Initialize utility detector.
        
        Args:
            db_connection: Database connection object
            call_threshold: Minimum number of flows calling a program to mark as utility
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self.call_threshold = call_threshold
    
    def detect_utility_programs(
        self,
        all_flows: Dict[str, Dict],
        utility_patterns: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Detect utility programs based on call frequency and naming patterns.
        
        Args:
            all_flows: Dictionary mapping flow_id -> flow data (with 'programs' and 'start_program')
            utility_patterns: List of naming patterns (e.g., ['UTIL*', 'COMMON*'])
        
        Returns:
            Dictionary mapping program name -> utility metadata
        """
        if utility_patterns is None:
            utility_patterns = []
        
        # Count how many flows call each program
        program_call_counts = self._count_program_calls(all_flows)
        
        # Track which flows use each program
        program_flows = self._track_program_flows(all_flows)
        
        # Identify utilities
        utilities = {}
        
        for program, call_count in program_call_counts.items():
            is_utility = False
            matched_pattern = None
            
            # Check naming patterns
            if utility_patterns:
                for pattern in utility_patterns:
                    if self._matches_pattern(program, pattern):
                        is_utility = True
                        matched_pattern = pattern
                        break
            
            # Check call frequency
            if call_count >= self.call_threshold:
                is_utility = True
            
            if is_utility:
                utilities[program] = {
                    'is_utility': True,
                    'call_count': call_count,
                    'shared_by_flows': program_flows.get(program, []),
                    'shared_by_flow_count': len(program_flows.get(program, [])),
                    'naming_pattern': matched_pattern,
                    'classification': 'UTILITY'
                }
        
        return utilities
    
    def _count_program_calls(self, all_flows: Dict[str, Dict]) -> Dict[str, int]:
        """
        Count how many flows call each program.
        
        Args:
            all_flows: Dictionary mapping flow_id -> flow data
        
        Returns:
            Dictionary mapping program name -> call count
        """
        program_call_counts = {}
        
        for flow_id, flow in all_flows.items():
            programs = flow.get('programs', [])
            start_program = flow.get('start_program', flow.get('entry_program'))
            
            for program in programs:
                if program not in program_call_counts:
                    program_call_counts[program] = 0
                
                # Only count if this program is not the entry point of this flow
                if program != start_program:
                    program_call_counts[program] += 1
        
        return program_call_counts
    
    def _track_program_flows(self, all_flows: Dict[str, Dict]) -> Dict[str, List[str]]:
        """
        Track which flows use each program.
        
        Args:
            all_flows: Dictionary mapping flow_id -> flow data
        
        Returns:
            Dictionary mapping program name -> list of flow IDs
        """
        program_flows = {}
        
        for flow_id, flow in all_flows.items():
            programs = flow.get('programs', [])
            start_program = flow.get('start_program', flow.get('entry_program'))
            
            for program in programs:
                if program not in program_flows:
                    program_flows[program] = []
                
                # Only track if this program is not the entry point of this flow
                if program != start_program and flow_id not in program_flows[program]:
                    program_flows[program].append(flow_id)
        
        return program_flows
    
    def _matches_pattern(self, program_name: str, pattern: str) -> bool:
        """
        Check if program name matches a pattern.
        
        Args:
            program_name: Program name to check
            pattern: Pattern with wildcards (* and ?)
        
        Returns:
            True if program name matches pattern
        """
        return fnmatch.fnmatch(program_name.upper(), pattern.upper())
    
    def write_utility_metadata(self, utilities: Dict[str, Dict]) -> None:
        """
        Write utility metadata to database.
        
        Args:
            utilities: Dictionary mapping program name -> utility metadata
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        for program_name, metadata in utilities.items():
            # Check if program already exists
            self.cursor.execute("""
                SELECT program_name FROM program_metadata WHERE program_name = ?
            """, (program_name,))
            
            exists = self.cursor.fetchone() is not None
            
            if exists:
                # Update existing record
                self.cursor.execute("""
                    UPDATE program_metadata
                    SET is_utility = ?,
                        call_count = ?,
                        classification = ?,
                        shared_by_flow_count = ?,
                        naming_pattern = ?,
                        updated_date = ?
                    WHERE program_name = ?
                """, (
                    metadata['is_utility'],
                    metadata['call_count'],
                    metadata['classification'],
                    metadata['shared_by_flow_count'],
                    metadata.get('naming_pattern'),
                    current_date,
                    program_name
                ))
            else:
                # Insert new record
                self.cursor.execute("""
                    INSERT INTO program_metadata (
                        program_name,
                        is_utility,
                        call_count,
                        classification,
                        shared_by_flow_count,
                        naming_pattern,
                        created_date,
                        updated_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    program_name,
                    metadata['is_utility'],
                    metadata['call_count'],
                    metadata['classification'],
                    metadata['shared_by_flow_count'],
                    metadata.get('naming_pattern'),
                    current_date,
                    current_date
                ))
        
        self.conn.commit()
    
    def get_utility_programs(self) -> Dict[str, Dict]:
        """
        Get all utility programs from database.
        
        Returns:
            Dictionary mapping program name -> utility metadata
        """
        self.cursor.execute("""
            SELECT 
                program_name,
                is_utility,
                call_count,
                classification,
                shared_by_flow_count,
                naming_pattern
            FROM program_metadata
            WHERE is_utility = 1
        """)
        
        utilities = {}
        
        for row in self.cursor.fetchall():
            program_name = row[0]
            utilities[program_name] = {
                'is_utility': bool(row[1]),
                'call_count': row[2],
                'classification': row[3],
                'shared_by_flow_count': row[4],
                'naming_pattern': row[5]
            }
        
        return utilities
    
    def is_utility_program(self, program_name: str) -> bool:
        """
        Check if a program is marked as a utility.
        
        Args:
            program_name: Program name to check
        
        Returns:
            True if program is a utility
        """
        self.cursor.execute("""
            SELECT is_utility FROM program_metadata WHERE program_name = ?
        """, (program_name,))
        
        result = self.cursor.fetchone()
        return bool(result[0]) if result else False
    
    def get_shared_flows(self, program_name: str) -> List[str]:
        """
        Get list of flows that share a utility program.
        
        Args:
            program_name: Program name to check
        
        Returns:
            List of flow IDs that use this program
        """
        # Query flow_scope table to find flows containing this program
        self.cursor.execute("""
            SELECT DISTINCT flow_id
            FROM flow_scope
            WHERE artifact_type = 'PROGRAM' AND artifact_name = ?
        """, (program_name,))
        
        return [row[0] for row in self.cursor.fetchall()]
    
    def format_extended_scope(
        self,
        programs: List[str],
        utilities: Optional[Dict[str, Dict]] = None
    ) -> List[Dict]:
        """
        Format program list with utility metadata for extended scope format.
        
        Args:
            programs: List of program names
            utilities: Optional dictionary of utility metadata (if None, queries database)
        
        Returns:
            List of program objects with utility metadata
        """
        if utilities is None:
            utilities = self.get_utility_programs()
        
        extended_programs = []
        
        for program in programs:
            if program in utilities:
                # Get shared flows for this utility
                shared_flows = self.get_shared_flows(program)
                
                extended_programs.append({
                    'name': program,
                    'is_utility': True,
                    'shared_by_flows': shared_flows,
                    'call_count': utilities[program]['call_count'],
                    'classification': utilities[program]['classification']
                })
            else:
                extended_programs.append({
                    'name': program,
                    'is_utility': False
                })
        
        return extended_programs


def detect_utility_programs(
    db_connection,
    all_flows: Dict[str, Dict],
    utility_patterns: Optional[List[str]] = None,
    call_threshold: int = 5
) -> Dict[str, Dict]:
    """
    Convenience function to detect utility programs.
    
    Args:
        db_connection: Database connection object
        all_flows: Dictionary mapping flow_id -> flow data
        utility_patterns: List of naming patterns (e.g., ['UTIL*', 'COMMON*'])
        call_threshold: Minimum number of flows calling a program to mark as utility
    
    Returns:
        Dictionary mapping program name -> utility metadata
    """
    detector = UtilityDetector(db_connection, call_threshold)
    return detector.detect_utility_programs(all_flows, utility_patterns)
