"""Call graph builder for program flow analysis."""

from typing import List, Dict, Set, Optional, Tuple
from ..models.flow import CallGraph
from ..models.dependency import Dependency, DependencyType


class CallGraphBuilder:
    """Builds call graphs from dependency data with program-level granularity."""
    
    def __init__(self, dependencies: List[Dependency], program_file_mapping: Optional[Dict[str, Dict]] = None):
        """
        Initialize call graph builder.
        
        Args:
            dependencies: List of all dependencies in the system
            program_file_mapping: Optional mapping of program names to file location metadata
                                 Format: {program_name: {'file_path': str, 'start_line': int, 'end_line': int, ...}}
        """
        self.dependencies = dependencies
        self.program_file_mapping = program_file_mapping or {}
        self._program_calls = self._extract_program_calls()
    
    def _extract_program_calls(self) -> Dict[str, Set[str]]:
        """
        Extract program-to-program call relationships using program names instead of file names.
        
        Returns:
            Dictionary mapping caller program name -> set of callee program names
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
                        # Use program names directly (already program-level in enhanced system)
                        source_program = dep.source_artifact
                        target_program = dep.target_artifact
                        
                        if source_program not in calls:
                            calls[source_program] = set()
                        calls[source_program].add(target_program)
        
        return calls
    
    def build_call_graph(self, programs: List[str]) -> CallGraph:
        """
        Build call graph for specified programs with program-level nodes and file location metadata.
        
        Args:
            programs: List of program names to include in graph
            
        Returns:
            CallGraph object with program-level nodes, edges, and file location metadata
        """
        graph = CallGraph(nodes=[], edges=[], metadata={})
        
        # Add all specified programs as nodes with file location metadata
        for program in programs:
            file_metadata = self._get_program_file_metadata(program)
            graph.add_node(program, **file_metadata)
        
        # Build edges from program-to-program dependencies
        visited = set()
        for program in programs:
            self._add_program_to_graph(program, graph, visited)
        
        return graph
    
    def _add_program_to_graph(
        self,
        program: str,
        graph: CallGraph,
        visited: Set[str]
    ) -> None:
        """
        Recursively add program and its callees to graph with file location metadata.
        
        Args:
            program: Program name to add
            graph: CallGraph to update
            visited: Set of already visited programs
        """
        if program in visited:
            return
        
        visited.add(program)
        
        # Ensure program is in graph with file metadata
        if program not in graph.nodes:
            file_metadata = self._get_program_file_metadata(program)
            graph.add_node(program, **file_metadata)
        
        # Get all programs called by this program
        callees = self._program_calls.get(program, set())
        
        for callee in callees:
            # Add edge between specific programs
            graph.add_edge(program, callee)
            
            # Ensure callee is in graph with file metadata
            if callee not in graph.nodes:
                callee_metadata = self._get_program_file_metadata(callee)
                graph.add_node(callee, **callee_metadata)
            
            # Recursively add callee's dependencies
            self._add_program_to_graph(callee, graph, visited)
    
    def build_full_call_graph(self) -> CallGraph:
        """
        Build complete call graph for all programs in the system with program-level representation.
        
        Returns:
            CallGraph containing all programs from multi-program files as separate entities
        """
        graph = CallGraph(nodes=[], edges=[], metadata={})
        
        # Get all unique programs from dependencies (already program-level)
        all_programs = set()
        for dep in self.dependencies:
            if dep.source_type in {'PROGRAM', 'JCL'}:
                all_programs.add(dep.source_artifact)
            if dep.target_type == 'PROGRAM':
                all_programs.add(dep.target_artifact)
        
        # Also include programs from file mapping that might not have dependencies
        if self.program_file_mapping:
            all_programs.update(self.program_file_mapping.keys())
        
        # Build graph for all programs with file location metadata
        visited = set()
        for program in all_programs:
            self._add_program_to_graph(program, graph, visited)
        
        return graph
    
    def get_callers(self, program: str) -> List[str]:
        """
        Get all programs that call the specified program.
        
        Args:
            program: Program name
            
        Returns:
            List of caller program names
        """
        callers = []
        for caller, callees in self._program_calls.items():
            if program in callees:
                callers.append(caller)
        return callers
    
    def get_callees(self, program: str) -> List[str]:
        """
        Get all programs called by the specified program.
        
        Args:
            program: Program name
            
        Returns:
            List of callee program names
        """
        return list(self._program_calls.get(program, set()))
    
    def _get_program_file_metadata(self, program_name: str) -> Dict:
        """
        Get file location metadata for a program.
        
        Args:
            program_name: Name of the program
            
        Returns:
            Dictionary with file location information
        """
        if program_name in self.program_file_mapping:
            mapping = self.program_file_mapping[program_name]
            return {
                'file_path': mapping.get('file_path'),
                'start_line': mapping.get('start_line'),
                'end_line': mapping.get('end_line'),
                'program_type': mapping.get('program_type'),
                'language': mapping.get('language'),
                'entry_points': mapping.get('entry_points', [])
            }
        else:
            # Return empty metadata if no mapping available
            return {
                'file_path': None,
                'start_line': None,
                'end_line': None,
                'program_type': None,
                'language': None,
                'entry_points': []
            }
    
    def add_metadata_to_graph(
        self,
        graph: CallGraph,
        metadata_provider: callable
    ) -> None:
        """
        Add metadata to graph nodes using a provider function.
        
        Args:
            graph: CallGraph to update
            metadata_provider: Function that takes program name and returns metadata dict
        """
        for program in graph.nodes:
            metadata = metadata_provider(program)
            if metadata:
                # Merge with existing file location metadata
                existing_metadata = graph.metadata.get(program, {})
                existing_metadata.update(metadata)
                graph.metadata[program] = existing_metadata
    
    def get_entry_points(self, all_programs_in_inventory: Optional[Set[str]] = None) -> List[str]:
        """
        Get all entry point programs (programs that are never called).
        
        Args:
            all_programs_in_inventory: Optional set of all program names from inventory.
                                      If provided, includes programs with no dependencies.
        
        Returns:
            List of entry point program names
        """
        # Get all programs that are called by others
        called_programs = set()
        for callees in self._program_calls.values():
            called_programs.update(callees)
        
        # Get ALL programs in the system (both calling and called from dependencies)
        all_programs = set(self._program_calls.keys())
        for callees in self._program_calls.values():
            all_programs.update(callees)
        
        # If inventory provided, include programs that have no dependencies at all
        # (e.g., CICS transactions that don't call anything and aren't called)
        if all_programs_in_inventory:
            all_programs.update(all_programs_in_inventory)
        
        # Entry points are ALL programs that are never called by others
        # This includes leaf programs (that don't call anything) and CICS transactions
        entry_points = all_programs - called_programs
        
        return list(entry_points)
    
    def get_leaf_programs(self) -> List[str]:
        """
        Get all leaf programs (programs that don't call anything).
        
        Returns:
            List of leaf program names
        """
        # Get all programs
        all_programs = set()
        for dep in self.dependencies:
            if dep.source_type in {'PROGRAM', 'JCL'}:
                all_programs.add(dep.source_artifact)
            if dep.target_type == 'PROGRAM':
                all_programs.add(dep.target_artifact)
        
        # Also include programs from file mapping
        if self.program_file_mapping:
            all_programs.update(self.program_file_mapping.keys())
        
        # Get programs that call others
        calling_programs = set(self._program_calls.keys())
        
        # Leaf programs are those that don't call anything
        leaf_programs = all_programs - calling_programs
        
        return list(leaf_programs)
    
    def export_program_to_file_mapping(self) -> Dict[str, Dict]:
        """
        Export program-to-file mapping information for traceability to source code.
        
        Returns:
            Dictionary mapping program names to file location information
        """
        return dict(self.program_file_mapping)
    
    def get_programs_in_file(self, file_path: str) -> List[str]:
        """
        Get all programs contained in a specific file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            List of program names in the file
        """
        programs_in_file = []
        for program_name, mapping in self.program_file_mapping.items():
            if mapping.get('file_path') == file_path:
                programs_in_file.append(program_name)
        
        # Sort by start line if available
        programs_in_file.sort(key=lambda p: self.program_file_mapping[p].get('start_line', 0))
        return programs_in_file
    
    def get_file_for_program(self, program_name: str) -> Optional[str]:
        """
        Get the file path containing a specific program.
        
        Args:
            program_name: Name of the program
            
        Returns:
            File path containing the program, or None if not found
        """
        mapping = self.program_file_mapping.get(program_name)
        return mapping.get('file_path') if mapping else None
