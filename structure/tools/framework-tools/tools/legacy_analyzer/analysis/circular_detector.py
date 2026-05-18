"""Circular dependency detection using DFS algorithm."""

from typing import List, Dict, Set, Optional, Any
import sqlite3
from ..models.dependency import Dependency, CircularDependency, DependencyType


class CircularDependencyDetector:
    """Detects circular dependencies in program call graphs."""
    
    def __init__(self, dependencies: List[Dependency], db_connection: Optional[sqlite3.Connection] = None):
        """
        Initialize circular dependency detector.
        
        Args:
            dependencies: List of all dependencies in the system
            db_connection: Optional database connection for program-file mapping metadata
        """
        self.dependencies = dependencies
        self._program_calls = self._extract_program_calls()
        self._db_connection = db_connection
        self._program_file_mapping = {}
        
        # Load program-file mappings if database connection provided
        if db_connection:
            self._load_program_file_mappings()
    
    def _extract_program_calls(self) -> Dict[str, Set[str]]:
        """
        Extract program-to-program call relationships.
        
        Returns:
            Dictionary mapping caller -> set of callees
        """
        calls = {}
        
        for dep in self.dependencies:
            # Only consider program call dependencies
            if dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM
            }:
                # Source must be a program or JCL
                if dep.source_type in {'PROGRAM', 'JCL'}:
                    # Target must be a program
                    if dep.target_type == 'PROGRAM':
                        if dep.source_artifact not in calls:
                            calls[dep.source_artifact] = set()
                        calls[dep.source_artifact].add(dep.target_artifact)
        
        return calls
    
    def detect_all_cycles(self) -> List[CircularDependency]:
        """
        Detect all circular dependencies in the system.
        
        Uses DFS-based cycle detection algorithm.
        
        Returns:
            List of CircularDependency objects
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        # Get all programs
        all_programs = set(self._program_calls.keys())
        for callees in self._program_calls.values():
            all_programs.update(callees)
        
        # Run DFS from each unvisited program
        for program in all_programs:
            if program not in visited:
                self._dfs_detect_cycles(
                    program,
                    visited,
                    rec_stack,
                    path,
                    cycles
                )
        
        # Remove duplicate cycles
        return self._deduplicate_cycles(cycles)
    
    def _dfs_detect_cycles(
        self,
        program: str,
        visited: Set[str],
        rec_stack: Set[str],
        path: List[str],
        cycles: List[CircularDependency]
    ) -> None:
        """
        DFS traversal to detect cycles.
        
        Args:
            program: Current program being visited
            visited: Set of all visited programs
            rec_stack: Set of programs in current recursion stack
            path: Current path being explored
            cycles: List to accumulate detected cycles
        """
        visited.add(program)
        rec_stack.add(program)
        path.append(program)
        
        # Visit all callees
        callees = self._program_calls.get(program, set())
        for callee in callees:
            if callee not in visited:
                # Continue DFS
                self._dfs_detect_cycles(
                    callee,
                    visited,
                    rec_stack,
                    path,
                    cycles
                )
            elif callee in rec_stack:
                # Found a cycle!
                cycle_start_idx = path.index(callee)
                cycle_programs = path[cycle_start_idx:] + [callee]
                
                # Get dependency types for the cycle
                dep_types = self._get_dependency_types_for_cycle(cycle_programs)
                
                # Create CircularDependency object
                circular_dep = CircularDependency(
                    artifacts=cycle_programs[:-1],  # Don't duplicate the start
                    dependency_types=dep_types
                )
                cycles.append(circular_dep)
        
        # Backtrack
        path.pop()
        rec_stack.remove(program)
    
    def _get_dependency_types_for_cycle(
        self,
        cycle_programs: List[str]
    ) -> List[str]:
        """
        Get dependency types for each edge in the cycle.
        
        Args:
            cycle_programs: List of programs in cycle (with duplicate at end)
            
        Returns:
            List of dependency types
        """
        dep_types = []
        
        for i in range(len(cycle_programs) - 1):
            source = cycle_programs[i]
            target = cycle_programs[i + 1]
            
            # Find the dependency type
            dep_type = self._find_dependency_type(source, target)
            dep_types.append(dep_type)
        
        return dep_types
    
    def _find_dependency_type(self, source: str, target: str) -> str:
        """
        Find the dependency type between two programs.
        
        Args:
            source: Source program
            target: Target program
            
        Returns:
            Dependency type string
        """
        for dep in self.dependencies:
            if (dep.source_artifact == source and 
                dep.target_artifact == target and
                dep.dependency_type in {
                    DependencyType.CALL,
                    DependencyType.CICS_LINK,
                    DependencyType.CICS_START,
                    DependencyType.EXEC_PGM
                }):
                return dep.dependency_type
        
        return "UNKNOWN"
    
    def _deduplicate_cycles(
        self,
        cycles: List[CircularDependency]
    ) -> List[CircularDependency]:
        """
        Remove duplicate cycles (same cycle starting from different points).
        
        Args:
            cycles: List of detected cycles
            
        Returns:
            Deduplicated list of cycles
        """
        unique_cycles = []
        seen_cycle_sets = []
        
        for cycle in cycles:
            # Normalize cycle by sorting (cycles are equivalent regardless of start point)
            cycle_set = frozenset(cycle.artifacts)
            
            if cycle_set not in seen_cycle_sets:
                seen_cycle_sets.append(cycle_set)
                unique_cycles.append(cycle)
        
        return unique_cycles
    
    def _load_program_file_mappings(self) -> None:
        """
        Load program-to-file mappings from database for file location metadata.
        
        This enables the detector to provide file location information for programs
        in circular dependency reports.
        """
        if not self._db_connection:
            return
        
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                SELECT 
                    pfm.program_name, 
                    inv.file_path, 
                    pfm.start_line, 
                    pfm.end_line, 
                    pfm.program_type, 
                    pfm.language
                FROM program_file_mapping pfm
                JOIN inventory inv ON pfm.file_id = inv.id
                ORDER BY inv.file_path, pfm.start_line
            """)
            
            for row in cursor.fetchall():
                program_name, file_path, start_line, end_line, program_type, language = row
                self._program_file_mapping[program_name] = {
                    'file_path': file_path,
                    'start_line': start_line,
                    'end_line': end_line,
                    'program_type': program_type,
                    'language': language
                }
        except Exception as e:
            # If program_file_mapping table doesn't exist, continue without mappings
            print(f"Warning: Could not load program-file mappings: {e}")
    
    def detect_cycles_within_files(self) -> List[Dict[str, Any]]:
        """
        Detect circular dependencies that occur within single files.
        
        Returns:
            List of dictionaries with cycle information and file metadata
        """
        all_cycles = self.detect_all_cycles()
        within_file_cycles = []
        
        for cycle in all_cycles:
            # Get file locations for all programs in cycle
            file_locations = {}
            for program in cycle.artifacts:
                location = self._program_file_mapping.get(program)
                if location:
                    file_path = location['file_path']
                    if file_path not in file_locations:
                        file_locations[file_path] = []
                    file_locations[file_path].append({
                        'program': program,
                        'start_line': location['start_line'],
                        'end_line': location['end_line'],
                        'program_type': location['program_type'],
                        'language': location['language']
                    })
            
            # Check if all programs are in the same file
            if len(file_locations) == 1:
                file_path = list(file_locations.keys())[0]
                within_file_cycles.append({
                    'cycle': cycle,
                    'file_path': file_path,
                    'programs_in_file': file_locations[file_path],
                    'cycle_type': 'WITHIN_FILE'
                })
        
        return within_file_cycles
    
    def detect_cycles_across_files(self) -> List[Dict[str, Any]]:
        """
        Detect circular dependencies that span across multiple files.
        
        Returns:
            List of dictionaries with cycle information and file metadata
        """
        all_cycles = self.detect_all_cycles()
        across_file_cycles = []
        
        for cycle in all_cycles:
            # Get file locations for all programs in cycle
            file_locations = {}
            programs_without_location = []
            
            for program in cycle.artifacts:
                location = self._program_file_mapping.get(program)
                if location:
                    file_path = location['file_path']
                    if file_path not in file_locations:
                        file_locations[file_path] = []
                    file_locations[file_path].append({
                        'program': program,
                        'start_line': location['start_line'],
                        'end_line': location['end_line'],
                        'program_type': location['program_type'],
                        'language': location['language']
                    })
                else:
                    programs_without_location.append(program)
            
            # Check if programs span multiple files
            if len(file_locations) > 1 or programs_without_location:
                across_file_cycles.append({
                    'cycle': cycle,
                    'files_involved': file_locations,
                    'programs_without_location': programs_without_location,
                    'cycle_type': 'ACROSS_FILES',
                    'file_count': len(file_locations)
                })
        
        return across_file_cycles
    
    def generate_program_level_cycle_report(self, cycle: CircularDependency) -> Dict[str, Any]:
        """
        Generate detailed report for a program-level circular dependency with file location information.
        
        Args:
            cycle: CircularDependency object
            
        Returns:
            Dictionary with detailed cycle report including file locations
        """
        report = {
            'cycle_id': hash(tuple(cycle.artifacts)),
            'cycle_length': len(cycle.artifacts),
            'programs': cycle.artifacts,
            'dependency_types': cycle.dependency_types,
            'program_details': [],
            'file_summary': {},
            'validation_results': {}
        }
        
        # Get detailed information for each program in the cycle
        files_involved = set()
        languages_involved = set()
        program_types_involved = set()
        
        for i, program in enumerate(cycle.artifacts):
            program_detail = {
                'program_name': program,
                'position_in_cycle': i,
                'calls_next_program': cycle.artifacts[(i + 1) % len(cycle.artifacts)],
                'dependency_type': cycle.dependency_types[i] if i < len(cycle.dependency_types) else 'UNKNOWN'
            }
            
            # Add file location information if available
            location = self._program_file_mapping.get(program)
            if location:
                program_detail.update({
                    'file_path': location['file_path'],
                    'start_line': location['start_line'],
                    'end_line': location['end_line'],
                    'program_type': location['program_type'],
                    'language': location['language']
                })
                
                files_involved.add(location['file_path'])
                languages_involved.add(location['language'])
                program_types_involved.add(location['program_type'])
            else:
                program_detail.update({
                    'file_path': None,
                    'start_line': None,
                    'end_line': None,
                    'program_type': 'UNKNOWN',
                    'language': 'UNKNOWN'
                })
            
            report['program_details'].append(program_detail)
        
        # Generate file summary
        report['file_summary'] = {
            'total_files': len(files_involved),
            'files': list(files_involved),
            'languages': list(languages_involved),
            'program_types': list(program_types_involved),
            'is_within_single_file': len(files_involved) <= 1,
            'is_cross_language': len(languages_involved) > 1
        }
        
        # Validate cycle accuracy
        report['validation_results'] = self._validate_cycle_accuracy(cycle)
        
        return report
    
    def _validate_cycle_accuracy(self, cycle: CircularDependency) -> Dict[str, Any]:
        """
        Validate the accuracy of a program-level circular dependency.
        
        Args:
            cycle: CircularDependency object to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'dependency_validation': []
        }
        
        # Validate each dependency in the cycle
        for i, program in enumerate(cycle.artifacts):
            next_program = cycle.artifacts[(i + 1) % len(cycle.artifacts)]
            expected_dep_type = cycle.dependency_types[i] if i < len(cycle.dependency_types) else None
            
            # Find the actual dependency
            actual_dep = None
            for dep in self.dependencies:
                if (dep.source_artifact == program and 
                    dep.target_artifact == next_program and
                    dep.dependency_type in {
                        DependencyType.CALL,
                        DependencyType.CICS_LINK,
                        DependencyType.CICS_START,
                        DependencyType.EXEC_PGM
                    }):
                    actual_dep = dep
                    break
            
            dep_validation = {
                'source_program': program,
                'target_program': next_program,
                'expected_type': expected_dep_type,
                'actual_dependency_found': actual_dep is not None,
                'actual_type': actual_dep.dependency_type if actual_dep else None,
                'type_matches': False
            }
            
            if actual_dep:
                dep_validation['type_matches'] = actual_dep.dependency_type == expected_dep_type
                if not dep_validation['type_matches']:
                    validation['warnings'].append(
                        f"Dependency type mismatch: {program} -> {next_program} "
                        f"(expected: {expected_dep_type}, actual: {actual_dep.dependency_type})"
                    )
            else:
                validation['is_valid'] = False
                validation['errors'].append(
                    f"Missing dependency: {program} -> {next_program}"
                )
            
            validation['dependency_validation'].append(dep_validation)
        
        # Check for program existence in inventory
        for program in cycle.artifacts:
            if program not in self._program_file_mapping and self._db_connection:
                validation['warnings'].append(
                    f"Program {program} not found in program-file mapping"
                )
        
        return validation
    
    def get_cycle_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about circular dependencies in the system.
        
        Returns:
            Dictionary with cycle statistics including file-level breakdown
        """
        all_cycles = self.detect_all_cycles()
        within_file_cycles = self.detect_cycles_within_files()
        across_file_cycles = self.detect_cycles_across_files()
        
        # Analyze cycle characteristics
        cycle_lengths = [len(cycle.artifacts) for cycle in all_cycles]
        programs_in_cycles = set()
        for cycle in all_cycles:
            programs_in_cycles.update(cycle.artifacts)
        
        # File-level statistics
        files_with_cycles = set()
        for cycle_info in within_file_cycles:
            files_with_cycles.add(cycle_info['file_path'])
        
        files_in_cross_cycles = set()
        for cycle_info in across_file_cycles:
            files_in_cross_cycles.update(cycle_info['files_involved'].keys())
        
        return {
            'total_cycles': len(all_cycles),
            'within_file_cycles': len(within_file_cycles),
            'across_file_cycles': len(across_file_cycles),
            'programs_in_cycles': len(programs_in_cycles),
            'files_with_internal_cycles': len(files_with_cycles),
            'files_in_cross_cycles': len(files_in_cross_cycles),
            'cycle_length_distribution': {
                'min': min(cycle_lengths) if cycle_lengths else 0,
                'max': max(cycle_lengths) if cycle_lengths else 0,
                'avg': sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else 0
            },
            'cycle_breakdown_by_length': {
                length: cycle_lengths.count(length) 
                for length in set(cycle_lengths)
            }
        }
    
    def validate_program_level_accuracy(self) -> Dict[str, Any]:
        """
        Validate the accuracy of program-level circular dependency detection.
        
        Returns:
            Dictionary with comprehensive validation results
        """
        validation_results = {
            'overall_valid': True,
            'total_cycles_detected': 0,
            'valid_cycles': 0,
            'invalid_cycles': 0,
            'cycles_with_warnings': 0,
            'detailed_results': [],
            'summary_statistics': {}
        }
        
        all_cycles = self.detect_all_cycles()
        validation_results['total_cycles_detected'] = len(all_cycles)
        
        for cycle in all_cycles:
            cycle_report = self.generate_program_level_cycle_report(cycle)
            cycle_validation = cycle_report['validation_results']
            
            if cycle_validation['is_valid']:
                validation_results['valid_cycles'] += 1
            else:
                validation_results['invalid_cycles'] += 1
                validation_results['overall_valid'] = False
            
            if cycle_validation['warnings']:
                validation_results['cycles_with_warnings'] += 1
            
            validation_results['detailed_results'].append({
                'cycle_id': cycle_report['cycle_id'],
                'programs': cycle.artifacts,
                'is_valid': cycle_validation['is_valid'],
                'errors': cycle_validation['errors'],
                'warnings': cycle_validation['warnings'],
                'file_summary': cycle_report['file_summary']
            })
        
        # Generate summary statistics
        validation_results['summary_statistics'] = {
            'accuracy_rate': validation_results['valid_cycles'] / max(validation_results['total_cycles_detected'], 1),
            'error_rate': validation_results['invalid_cycles'] / max(validation_results['total_cycles_detected'], 1),
            'warning_rate': validation_results['cycles_with_warnings'] / max(validation_results['total_cycles_detected'], 1)
        }
        
        return validation_results
    
    def has_cycle_involving(self, program: str) -> bool:
        """
        Check if a specific program is involved in any circular dependency.
        
        Args:
            program: Program name to check
            
        Returns:
            True if program is in a cycle, False otherwise
        """
        cycles = self.detect_all_cycles()
        
        for cycle in cycles:
            if program in cycle.artifacts:
                return True
        
        return False
    
    def get_cycles_involving(self, program: str) -> List[CircularDependency]:
        """
        Get all circular dependencies involving a specific program.
        
        Args:
            program: Program name
            
        Returns:
            List of CircularDependency objects involving the program
        """
        all_cycles = self.detect_all_cycles()
        
        return [
            cycle for cycle in all_cycles
            if program in cycle.artifacts
        ]
    
    def detect_cycle_from_program(
        self,
        start_program: str
    ) -> Optional[CircularDependency]:
        """
        Detect if there's a cycle starting from a specific program.
        
        Args:
            start_program: Program to start detection from
            
        Returns:
            CircularDependency if found, None otherwise
        """
        visited = set()
        rec_stack = set()
        path = []
        cycles = []
        
        self._dfs_detect_cycles(
            start_program,
            visited,
            rec_stack,
            path,
            cycles
        )
        
        if cycles:
            return cycles[0]
        return None
