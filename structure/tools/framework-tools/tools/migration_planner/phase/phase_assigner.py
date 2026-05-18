"""Phase assignment and dependency validation."""

import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque

from ..models import (
    BusinessFlow,
    WorkpackageAssignment,
    PhaseAssignment,
    MigrationSequenceItem,
)


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class PhaseAssigner:
    """Assigns migration phases based on dependencies and validates DAG."""
    
    def __init__(self):
        """Initialize the phase assigner."""
        self.flow_map: Dict[str, BusinessFlow] = {}
        self.workpackage_map: Dict[str, WorkpackageAssignment] = {}
        self.phase_assignments: Dict[int, PhaseAssignment] = {}
        self.flow_phases: Dict[str, int] = {}
        self.flow_waves: Dict[str, int] = {}  # Wave within phase
        self.coordination_deps: Dict[str, List[str]] = {}
        self.shared_context: Dict[str, Dict] = {}
    
    def assign_phases(
        self,
        workpackages: List[WorkpackageAssignment],
        flows: List[BusinessFlow],
        coordination_deps: Dict[str, List[str]] = None,
        shared_context: Dict[str, Dict] = None
    ) -> Tuple[List[PhaseAssignment], List[MigrationSequenceItem]]:
        """
        Assign phases based on dependencies.
        
        Args:
            workpackages: List of workpackage assignments
            flows: List of business flows
            coordination_deps: Optional coordination dependencies (soft prerequisites)
            shared_context: Optional shared module context
            
        Returns:
            Tuple of (phase assignments, migration sequence)
            
        Raises:
            ValidationError: If dependency validation fails
        """
        logger.info("Starting phase assignment")
        
        # Build lookup maps
        self.flow_map = {flow.flow_id: flow for flow in flows}
        self.workpackage_map = {wp.flow_id: wp for wp in workpackages}
        
        # Store coordination dependencies
        self.coordination_deps = coordination_deps or {}
        self.shared_context = shared_context or {}
        
        # Validate dependencies
        logger.info("Validating dependency graph")
        self.validate_dag(flows)
        
        # Assign phases using topological sort
        logger.info("Assigning phases to flows")
        self._assign_phases_to_flows(flows)
        
        # Calculate waves within phases based on soft prerequisites
        logger.info("Calculating migration waves")
        self._calculate_waves(workpackages)
        
        # Generate phase metadata
        logger.info("Generating phase metadata")
        phase_list = self._generate_phase_metadata(workpackages)
        
        # Generate migration sequence
        logger.info("Generating migration sequence")
        migration_sequence = self._generate_migration_sequence(workpackages)
        
        logger.info(f"Phase assignment complete: {len(phase_list)} phases")
        return phase_list, migration_sequence
    
    def validate_dag(self, flows: List[BusinessFlow]) -> None:
        """
        Validate that the dependency graph forms a DAG.
        
        Args:
            flows: List of business flows
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate all flow references exist
        self._validate_flow_references(flows)
        
        # Detect cycles
        cycles = self.detect_cycles(flows)
        if cycles:
            cycle_str = "; ".join([" -> ".join(cycle) for cycle in cycles])
            raise ValidationError(
                f"Circular dependencies detected: {cycle_str}"
            )
        
        logger.info("Dependency graph validation passed")
    
    def detect_cycles(self, flows: List[BusinessFlow]) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.
        
        Args:
            flows: List of business flows
            
        Returns:
            List of cycles (each cycle is a list of flow IDs)
        """
        # Build adjacency list
        graph: Dict[str, List[str]] = defaultdict(list)
        for flow in flows:
            graph[flow.flow_id] = flow.required_flows.copy()
        
        # Track visited nodes and recursion stack
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []
        
        def dfs(node: str) -> bool:
            """DFS helper to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        # Check all nodes
        for flow in flows:
            if flow.flow_id not in visited:
                dfs(flow.flow_id)
        
        return cycles
    
    def _validate_flow_references(self, flows: List[BusinessFlow]) -> None:
        """
        Validate that all flow references exist.
        
        Args:
            flows: List of business flows
            
        Raises:
            ValidationError: If a referenced flow does not exist
        """
        flow_ids = {flow.flow_id for flow in flows}
        
        for flow in flows:
            for required_flow in flow.required_flows:
                if required_flow not in flow_ids:
                    raise ValidationError(
                        f"Flow '{flow.flow_id}' references non-existent "
                        f"flow '{required_flow}'"
                    )
    
    def _assign_phases_to_flows(self, flows: List[BusinessFlow]) -> None:
        """
        Assign phases to flows using topological sorting.
        
        Args:
            flows: List of business flows
        """
        # Build adjacency list and in-degree map
        graph: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = defaultdict(int)
        
        for flow in flows:
            if flow.flow_id not in in_degree:
                in_degree[flow.flow_id] = 0
            
            for required_flow in flow.required_flows:
                graph[required_flow].append(flow.flow_id)
                in_degree[flow.flow_id] += 1
        
        # Initialize queue with flows that have no dependencies (phase 1)
        queue: deque = deque()
        for flow in flows:
            if in_degree[flow.flow_id] == 0:
                self.flow_phases[flow.flow_id] = 1
                queue.append((flow.flow_id, 1))
                logger.debug(f"Flow {flow.flow_id} assigned to phase 1")
        
        # Process flows level by level
        while queue:
            current_flow, current_phase = queue.popleft()
            
            # Process dependent flows
            for dependent_flow in graph[current_flow]:
                in_degree[dependent_flow] -= 1
                
                if in_degree[dependent_flow] == 0:
                    # All dependencies satisfied, assign to next phase
                    # Calculate minimum phase based on all dependencies
                    max_dep_phase = 0
                    dep_flow = self.flow_map[dependent_flow]
                    for req_flow in dep_flow.required_flows:
                        max_dep_phase = max(
                            max_dep_phase,
                            self.flow_phases[req_flow]
                        )
                    
                    next_phase = max_dep_phase + 1
                    self.flow_phases[dependent_flow] = next_phase
                    queue.append((dependent_flow, next_phase))
                    logger.debug(
                        f"Flow {dependent_flow} assigned to phase {next_phase}"
                    )
    
    def _calculate_waves(self, workpackages: List[WorkpackageAssignment]) -> None:
        """
        Calculate migration waves within each phase based on soft prerequisites.
        
        Waves allow parallel migration of flows that don't have hard or soft
        dependencies on each other.
        
        Args:
            workpackages: List of workpackage assignments
        """
        # Group flows by phase
        flows_by_phase: Dict[int, List[str]] = defaultdict(list)
        for wp in workpackages:
            phase = self.flow_phases[wp.flow_id]
            flows_by_phase[phase].append(wp.flow_id)
        
        # Calculate waves for each phase
        for phase_num, flow_ids in flows_by_phase.items():
            # Build soft dependency graph for this phase
            soft_graph: Dict[str, List[str]] = defaultdict(list)
            soft_in_degree: Dict[str, int] = defaultdict(int)
            
            for flow_id in flow_ids:
                if flow_id not in soft_in_degree:
                    soft_in_degree[flow_id] = 0
                
                # Add soft prerequisites (coordination dependencies)
                soft_prereqs = self.coordination_deps.get(flow_id, [])
                for prereq_flow in soft_prereqs:
                    # Only consider prerequisites in the same phase
                    if prereq_flow in flow_ids:
                        soft_graph[prereq_flow].append(flow_id)
                        soft_in_degree[flow_id] += 1
            
            # Assign waves using topological sort within phase
            queue: deque = deque()
            current_wave = 1
            
            # Start with flows that have no soft prerequisites
            for flow_id in flow_ids:
                if soft_in_degree[flow_id] == 0:
                    self.flow_waves[flow_id] = current_wave
                    queue.append((flow_id, current_wave))
            
            # Process flows wave by wave
            while queue:
                current_flow, wave = queue.popleft()
                
                # Process flows that depend on this one
                for dependent_flow in soft_graph[current_flow]:
                    soft_in_degree[dependent_flow] -= 1
                    
                    if soft_in_degree[dependent_flow] == 0:
                        # Calculate wave based on all soft prerequisites
                        max_prereq_wave = 0
                        for prereq in self.coordination_deps.get(dependent_flow, []):
                            if prereq in self.flow_waves:
                                max_prereq_wave = max(
                                    max_prereq_wave,
                                    self.flow_waves[prereq]
                                )
                        
                        next_wave = max_prereq_wave + 1
                        self.flow_waves[dependent_flow] = next_wave
                        queue.append((dependent_flow, next_wave))
            
            # Assign wave 1 to any flows not yet assigned (no soft deps)
            for flow_id in flow_ids:
                if flow_id not in self.flow_waves:
                    self.flow_waves[flow_id] = 1
        
        # Log wave statistics
        wave_counts = defaultdict(int)
        for wave in self.flow_waves.values():
            wave_counts[wave] += 1
        logger.info(f"Calculated {len(wave_counts)} waves: {dict(wave_counts)}")
    
    def _generate_phase_metadata(
        self,
        workpackages: List[WorkpackageAssignment]
    ) -> List[PhaseAssignment]:
        """
        Generate phase metadata.
        
        Args:
            workpackages: List of workpackage assignments
            
        Returns:
            List of phase assignments
        """
        # Group workpackages by phase
        phases_dict: Dict[int, PhaseAssignment] = {}
        
        for wp in workpackages:
            phase_num = self.flow_phases[wp.flow_id]
            
            if phase_num not in phases_dict:
                phases_dict[phase_num] = PhaseAssignment(
                    phase_id=phase_num,
                    workpackages=[],
                    dependencies=[]
                )
            
            phases_dict[phase_num].add_workpackage(wp.workpackage_id)
        
        # Calculate phase dependencies
        for phase_num, phase_assignment in phases_dict.items():
            dep_phases: Set[int] = set()
            
            # Check all workpackages in this phase
            for wp_id in phase_assignment.workpackages:
                # Find the workpackage
                wp = next(
                    (w for w in workpackages if w.workpackage_id == wp_id),
                    None
                )
                if wp:
                    flow = self.flow_map[wp.flow_id]
                    # Add phases of required flows
                    for req_flow_id in flow.required_flows:
                        req_phase = self.flow_phases[req_flow_id]
                        if req_phase < phase_num:
                            dep_phases.add(req_phase)
            
            phase_assignment.dependencies = sorted(list(dep_phases))
        
        # Convert to sorted list
        phase_list = [
            phases_dict[phase_num]
            for phase_num in sorted(phases_dict.keys())
        ]
        
        return phase_list
    
    def _generate_migration_sequence(
        self,
        workpackages: List[WorkpackageAssignment]
    ) -> List[MigrationSequenceItem]:
        """
        Generate migration sequence sorted by phase, wave, and workpackage ID.
        
        Args:
            workpackages: List of workpackage assignments
            
        Returns:
            List of migration sequence items
        """
        sequence: List[MigrationSequenceItem] = []
        sequence_num = 1
        
        # Sort workpackages by phase, wave, then by workpackage ID
        sorted_workpackages = sorted(
            workpackages,
            key=lambda wp: (
                self.flow_phases[wp.flow_id],
                self.flow_waves.get(wp.flow_id, 1),
                wp.workpackage_id
            )
        )
        
        for wp in sorted_workpackages:
            flow = self.flow_map[wp.flow_id]
            phase = self.flow_phases[wp.flow_id]
            wave = self.flow_waves.get(wp.flow_id, 1)
            
            # Find prerequisite workpackage IDs (hard dependencies)
            prerequisites: List[int] = []
            for req_flow_id in flow.required_flows:
                req_wp = self.workpackage_map.get(req_flow_id)
                if req_wp:
                    prerequisites.append(req_wp.workpackage_id)
            
            prerequisites.sort()
            
            # Find soft prerequisite workpackage IDs (coordination dependencies)
            soft_prerequisites: List[int] = []
            coord_flows = self.coordination_deps.get(wp.flow_id, [])
            for coord_flow_id in coord_flows:
                coord_wp = self.workpackage_map.get(coord_flow_id)
                if coord_wp:
                    soft_prerequisites.append(coord_wp.workpackage_id)
            
            soft_prerequisites.sort()
            
            # Get shared module context for this flow
            shared_module_context = self.shared_context.get(wp.flow_id, {})
            
            item = MigrationSequenceItem(
                sequence_number=sequence_num,
                workpackage_id=wp.workpackage_id,
                flow_id=wp.flow_id,
                phase=phase,
                wave=wave,
                prerequisites=prerequisites,
                soft_prerequisites=soft_prerequisites,
                shared_module_context=shared_module_context
            )
            
            sequence.append(item)
            sequence_num += 1
        
        return sequence
    
    def topological_sort(self, flows: List[BusinessFlow]) -> List[str]:
        """
        Sort flows in dependency order using topological sort.
        
        Args:
            flows: List of business flows
            
        Returns:
            List of flow IDs in topological order
            
        Raises:
            ValidationError: If graph contains cycles
        """
        # Validate first
        self.validate_dag(flows)
        
        # Build adjacency list and in-degree map
        graph: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = defaultdict(int)
        
        for flow in flows:
            if flow.flow_id not in in_degree:
                in_degree[flow.flow_id] = 0
            
            for required_flow in flow.required_flows:
                graph[required_flow].append(flow.flow_id)
                in_degree[flow.flow_id] += 1
        
        # Initialize queue with flows that have no dependencies
        queue: deque = deque()
        for flow in flows:
            if in_degree[flow.flow_id] == 0:
                queue.append(flow.flow_id)
        
        # Process flows
        result: List[str] = []
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
