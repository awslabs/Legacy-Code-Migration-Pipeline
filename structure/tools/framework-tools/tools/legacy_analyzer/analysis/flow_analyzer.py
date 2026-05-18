"""Program flow analyzer for legacy systems."""

from typing import List, Dict, Set, Optional, Any
import sqlite3
from ..models.flow import ProgramFlow, FlowNode, EntryPoint
from ..models.dependency import Dependency, CircularDependency, DependencyType
from .circular_detector import CircularDependencyDetector
from .entry_point_detector import EntryPointDetector


class FlowAnalyzer:
    """Analyzes program execution flows and builds call hierarchies."""
    
    def __init__(
        self,
        dependencies: List[Dependency],
        db_connection: Optional[sqlite3.Connection] = None
    ):
        """
        Initialize flow analyzer with dependency data.
        
        Args:
            dependencies: List of all dependencies in the system
            db_connection: Optional database connection for metadata-based entry point detection
                          and program-to-file mapping support
        """
        self.dependencies = dependencies
        self._program_calls = self._extract_program_calls()
        self._circular_detector = CircularDependencyDetector(dependencies)
        self._db_connection = db_connection
        self._entry_point_detector = None
        self._program_file_mapping = {}  # Cache for program-to-file mappings
        
        # Initialize entry point detector if database connection provided
        if db_connection:
            self._entry_point_detector = EntryPointDetector(db_connection)
            self._load_program_file_mappings()
    
    def _extract_program_calls(self) -> Dict[str, Set[str]]:
        """
        Extract program-to-program call relationships.
        
        Enhanced for program-level granularity - works with individual program names
        rather than file names when program-level dependencies are available.
        
        Returns:
            Dictionary mapping caller program -> set of callee programs
        """
        calls = {}
        
        for dep in self.dependencies:
            # Only consider program call dependencies
            if dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM,
                DependencyType.FETCH_RETURN
            }:
                # Source must be a program or JCL
                if dep.source_type in {'PROGRAM', 'JCL'}:
                    # Target must be a program
                    if dep.target_type == 'PROGRAM':
                        # Use individual program names for program-level granularity
                        source_program = dep.source_artifact
                        target_program = dep.target_artifact
                        
                        if source_program not in calls:
                            calls[source_program] = set()
                        calls[source_program].add(target_program)
        
        return calls
    
    def analyze_flow(
        self,
        start_program: str,
        max_depth: int = 10
    ) -> ProgramFlow:
        """
        Analyze program flow starting from a specific program.
        
        Enhanced for program-level granularity - operates on individual program names
        and maintains program-to-program call relationships with file location references.
        
        Args:
            start_program: Program name to start analysis from
            max_depth: Maximum depth to traverse (prevents infinite loops)
            
        Returns:
            ProgramFlow object with complete program-level flow information
        """
        # Track visited programs and their depths
        visited_programs = set()
        program_depths = {}
        all_programs = []
        flow_dependencies = []
        
        # Perform recursive traversal using program names
        max_depth_found = self._traverse_flow(
            start_program,
            0,
            max_depth,
            visited_programs,
            program_depths,
            all_programs,
            flow_dependencies
        )
        
        # Detect circular dependencies in this flow at program level
        circular_deps = self._detect_circular_in_flow(all_programs)
        
        # Create ProgramFlow object with program-level information
        flow = ProgramFlow(
            start_program=start_program,
            depth=max_depth_found,
            programs=all_programs,
            dependencies=flow_dependencies,
            circular_dependencies=circular_deps
        )
        
        return flow
    
    def _traverse_flow(
        self,
        program: str,
        current_depth: int,
        max_depth: int,
        visited: Set[str],
        depths: Dict[str, int],
        all_programs: List[str],
        flow_deps: List[Dependency]
    ) -> int:
        """
        Recursively traverse program flow.
        
        Args:
            program: Current program
            current_depth: Current depth in hierarchy
            max_depth: Maximum depth to traverse
            visited: Set of visited programs
            depths: Dictionary of program depths
            all_programs: List to accumulate all programs
            flow_deps: List to accumulate all dependencies
            
        Returns:
            Maximum depth reached
        """
        # Check if we've hit max depth
        if current_depth >= max_depth:
            return current_depth
        
        # Add program to visited set and list
        if program not in visited:
            visited.add(program)
            all_programs.append(program)
            depths[program] = current_depth
        else:
            # Update depth if we found a shorter path
            if current_depth < depths.get(program, float('inf')):
                depths[program] = current_depth
            # Don't traverse again to avoid infinite loops
            return current_depth
        
        # Get programs called by this program
        callees = self._program_calls.get(program, set())
        
        # Track maximum depth
        max_depth_reached = current_depth
        
        # Traverse each callee
        for callee in callees:
            # Find the dependency
            dep = self._find_dependency(program, callee)
            if dep and dep not in flow_deps:
                flow_deps.append(dep)
            
            # Recursively traverse callee (this will add it to visited and all_programs)
            callee_depth = self._traverse_flow(
                callee,
                current_depth + 1,
                max_depth,
                visited,
                depths,
                all_programs,
                flow_deps
            )
            
            # Update max depth
            max_depth_reached = max(max_depth_reached, callee_depth)
        
        return max_depth_reached
    
    def _find_dependency(
        self,
        source: str,
        target: str
    ) -> Optional[Dependency]:
        """
        Find dependency between two programs.
        
        Args:
            source: Source program
            target: Target program
            
        Returns:
            Dependency object or None
        """
        for dep in self.dependencies:
            if (dep.source_artifact == source and
                dep.target_artifact == target and
                dep.dependency_type in {
                    DependencyType.CALL,
                    DependencyType.CICS_LINK,
                    DependencyType.CICS_START,
                    DependencyType.EXEC_PGM,
                    DependencyType.FETCH_RETURN
                }):
                return dep
        return None
    
    def _detect_circular_in_flow(
        self,
        programs: List[str]
    ) -> List[CircularDependency]:
        """
        Detect circular dependencies within a flow.
        
        Args:
            programs: List of programs in the flow
            
        Returns:
            List of CircularDependency objects
        """
        # Get all circular dependencies in the system
        all_cycles = self._circular_detector.detect_all_cycles()
        
        # Filter to only cycles involving programs in this flow
        flow_programs_set = set(programs)
        flow_cycles = []
        
        for cycle in all_cycles:
            # Check if all artifacts in cycle are in the flow
            if all(artifact in flow_programs_set for artifact in cycle.artifacts):
                flow_cycles.append(cycle)
        
        return flow_cycles
    
    def calculate_flow_depth(self, program: str) -> int:
        """
        Calculate maximum depth of a program in the call hierarchy.
        
        This is the longest path from any entry point to this program.
        
        Args:
            program: Program name
            
        Returns:
            Maximum depth (0 if program is an entry point)
        """
        # Find all programs that call this program (directly or indirectly)
        callers = self._find_all_callers(program)
        
        if not callers:
            # This is an entry point
            return 0
        
        # Calculate depth from each caller
        max_depth = 0
        for caller in callers:
            caller_depth = self.calculate_flow_depth(caller)
            max_depth = max(max_depth, caller_depth + 1)
        
        return max_depth
    
    def _find_all_callers(self, program: str) -> Set[str]:
        """
        Find all programs that directly call the specified program.
        
        Args:
            program: Program name
            
        Returns:
            Set of caller program names
        """
        callers = set()
        
        for caller, callees in self._program_calls.items():
            if program in callees:
                callers.add(caller)
        
        return callers
    
    def get_entry_points(
        self,
        all_programs_in_inventory: Optional[Set[str]] = None,
        use_metadata: bool = False,
        include_disabled: bool = False,
        include_inferred: bool = True
    ) -> List[str]:
        """
        Get all entry point programs (programs that are never called).
        
        Enhanced for program-level granularity - identifies programs that are never called
        by other programs, regardless of file structure. This method maintains backward 
        compatibility by returning a simple list of program names.
        
        For full metadata, use get_entry_points_with_metadata() instead.
        
        Args:
            all_programs_in_inventory: Optional set of all program names from inventory.
                                      If provided, includes programs with no dependencies.
            use_metadata: If True, use EntryPointDetector for enhanced detection
            include_disabled: If True, include DISABLED CICS transactions (only with use_metadata=True)
            include_inferred: If True, include inferred entry points (only with use_metadata=True)
        
        Returns:
            List of entry point program names
        """
        # If metadata requested and available, use EntryPointDetector
        if use_metadata and self._entry_point_detector:
            # Get all programs and called programs for inferred detection
            called_programs = set()
            for callees in self._program_calls.values():
                called_programs.update(callees)
            
            all_programs = set(self._program_calls.keys())
            for callees in self._program_calls.values():
                all_programs.update(callees)
            
            if all_programs_in_inventory:
                all_programs.update(all_programs_in_inventory)
            
            # Use EntryPointDetector for program-level granularity
            entry_point_objects = self._entry_point_detector.detect_entry_points(
                all_programs=all_programs,
                called_programs=called_programs,
                include_disabled=include_disabled,
                include_inferred=include_inferred
            )
            
            # Extract just program names for backward compatibility
            return [ep.program_name for ep in entry_point_objects]
        
        # Fallback to code analysis with program-level granularity
        # Get all programs that are called by others (at program level)
        called_programs = set()
        for callees in self._program_calls.values():
            called_programs.update(callees)
        
        # Get ALL programs from all dependencies, not just call dependencies
        all_programs = set()
        for dep in self.dependencies:
            if dep.source_type == 'PROGRAM':
                all_programs.add(dep.source_artifact)
            if dep.target_type == 'PROGRAM':
                all_programs.add(dep.target_artifact)
        
        # If inventory provided, include programs that have no dependencies at all
        # (e.g., CICS transactions that don't call anything and aren't called)
        if all_programs_in_inventory:
            all_programs.update(all_programs_in_inventory)
        
        # Entry points are ALL programs that are never called by other programs
        # This works at program-level granularity regardless of file structure
        entry_points = all_programs - called_programs
        
        return list(entry_points)
    
    def get_entry_points_with_metadata(
        self,
        all_programs_in_inventory: Optional[Set[str]] = None,
        include_disabled: bool = False,
        include_inferred: bool = True
    ) -> List[EntryPoint]:
        """
        Get entry points with full metadata (CICS transactions, JCL, etc.).
        
        This method returns EntryPoint objects with complete metadata including
        transaction IDs, JCL names, confidence levels, and more. It requires
        a database connection to be provided during initialization.
        
        If no database connection is available, falls back to code analysis
        and returns EntryPoint objects with INFERRED confidence.
        
        Args:
            all_programs_in_inventory: Optional set of all program names from inventory
            include_disabled: If True, include DISABLED CICS transactions
            include_inferred: If True, include inferred entry points from code analysis
            
        Returns:
            List of EntryPoint objects with metadata
        """
        # If EntryPointDetector available, use it
        if self._entry_point_detector:
            # Get all programs and called programs for inferred detection
            called_programs = set()
            for callees in self._program_calls.values():
                called_programs.update(callees)
            
            # Get ALL programs from all dependencies, not just call dependencies
            all_programs = set()
            for dep in self.dependencies:
                if dep.source_type == 'PROGRAM':
                    all_programs.add(dep.source_artifact)
                if dep.target_type == 'PROGRAM':
                    all_programs.add(dep.target_artifact)
            
            if all_programs_in_inventory:
                all_programs.update(all_programs_in_inventory)
            
            # Use EntryPointDetector for full metadata
            return self._entry_point_detector.detect_entry_points(
                all_programs=all_programs,
                called_programs=called_programs,
                include_disabled=include_disabled,
                include_inferred=include_inferred
            )
        
        # Fallback to code analysis - create EntryPoint objects with INFERRED confidence
        called_programs = set()
        for callees in self._program_calls.values():
            called_programs.update(callees)
        
        # Get ALL programs from all dependencies, not just call dependencies
        all_programs = set()
        for dep in self.dependencies:
            if dep.source_type == 'PROGRAM':
                all_programs.add(dep.source_artifact)
            if dep.target_type == 'PROGRAM':
                all_programs.add(dep.target_artifact)
        
        if all_programs_in_inventory:
            all_programs.update(all_programs_in_inventory)
        
        # Entry points are programs that are never called
        entry_point_programs = all_programs - called_programs
        
        # Create EntryPoint objects with INFERRED confidence
        entry_points = []
        for program_name in sorted(entry_point_programs):
            entry_point = EntryPoint(
                program_name=program_name,
                entry_type='INFERRED',
                confidence='INFERRED',
                source='CODE_ANALYSIS',
                description='Program not called by any other program'
            )
            entry_points.append(entry_point)
        
        return entry_points
    
    def analyze_multiple_flows(
        self,
        programs: List[str],
        max_depth: int = 10
    ) -> Dict[str, ProgramFlow]:
        """
        Analyze flows for multiple programs.
        
        Args:
            programs: List of programs to analyze
            max_depth: Maximum depth for each flow
            
        Returns:
            Dictionary mapping program name to ProgramFlow
        """
        flows = {}
        
        for program in programs:
            flows[program] = self.analyze_flow(program, max_depth)
        
        return flows
    
    def _load_program_file_mappings(self) -> None:
        """
        Load program-to-file mappings from database for program-level granularity support.
        
        This enables the flow analyzer to provide file location metadata for programs
        while operating at program-level granularity.
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
    
    def get_program_file_location(self, program_name: str) -> Optional[Dict[str, Any]]:
        """
        Get file location information for a program.
        
        Args:
            program_name: Name of the program
            
        Returns:
            Dictionary with file location metadata or None if not found
        """
        return self._program_file_mapping.get(program_name)
    
    def get_programs_in_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get all programs within a specific file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            List of program information dictionaries
        """
        programs_in_file = []
        for program_name, mapping in self._program_file_mapping.items():
            if mapping['file_path'] == file_path:
                program_info = mapping.copy()
                program_info['program_name'] = program_name
                programs_in_file.append(program_info)
        
        # Sort by start line
        programs_in_file.sort(key=lambda x: x['start_line'])
        return programs_in_file
    
    def analyze_flow_with_file_mapping(
        self,
        start_program: str,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze program flow with file location metadata included.
        
        Args:
            start_program: Program name to start analysis from
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary with flow information and file mappings
        """
        # Get standard flow analysis
        flow = self.analyze_flow(start_program, max_depth)
        
        # Add file location metadata for each program
        program_locations = {}
        for program in flow.programs:
            location = self.get_program_file_location(program)
            if location:
                program_locations[program] = location
        
        return {
            'flow': flow,
            'program_locations': program_locations,
            'file_summary': self._get_file_summary(flow.programs)
        }
    
    def _get_file_summary(self, programs: List[str]) -> Dict[str, Any]:
        """
        Get summary of files involved in a flow.
        
        Args:
            programs: List of program names in the flow
            
        Returns:
            Dictionary with file summary information
        """
        files_involved = {}
        
        for program in programs:
            location = self.get_program_file_location(program)
            if location:
                file_path = location['file_path']
                if file_path not in files_involved:
                    files_involved[file_path] = {
                        'programs': [],
                        'languages': set(),
                        'program_types': set()
                    }
                
                files_involved[file_path]['programs'].append(program)
                files_involved[file_path]['languages'].add(location['language'])
                files_involved[file_path]['program_types'].add(location['program_type'])
        
        # Convert sets to lists for JSON serialization
        for file_info in files_involved.values():
            file_info['languages'] = list(file_info['languages'])
            file_info['program_types'] = list(file_info['program_types'])
        
        return {
            'total_files': len(files_involved),
            'files': files_involved
        }
    
    def analyze_all_entry_points(
        self,
        max_depth: int = 10
    ) -> Dict[str, ProgramFlow]:
        """
        Analyze flows for all entry point programs.
        
        Args:
            max_depth: Maximum depth for each flow
            
        Returns:
            Dictionary mapping program name to ProgramFlow
        """
        entry_points = self.get_entry_points()
        return self.analyze_multiple_flows(entry_points, max_depth)
    
    def get_program_statistics(self) -> Dict[str, int]:
        """
        Get statistics about programs in the system.
        
        Returns:
            Dictionary with statistics
        """
        all_programs = set()
        for dep in self.dependencies:
            if dep.source_type in {'PROGRAM', 'JCL'}:
                all_programs.add(dep.source_artifact)
            if dep.target_type == 'PROGRAM':
                all_programs.add(dep.target_artifact)
        
        entry_points = self.get_entry_points()
        
        # Get programs that are called
        called_programs = set()
        for callees in self._program_calls.values():
            called_programs.update(callees)
        
        # Get programs that call others
        calling_programs = set(self._program_calls.keys())
        
        # Leaf programs don't call anything
        leaf_programs = all_programs - calling_programs
        
        return {
            'total_programs': len(all_programs),
            'entry_points': len(entry_points),
            'leaf_programs': len(leaf_programs),
            'calling_programs': len(calling_programs),
            'called_programs': len(called_programs),
            'total_calls': sum(len(callees) for callees in self._program_calls.values())
        }
