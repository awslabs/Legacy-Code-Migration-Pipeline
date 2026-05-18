"""Workpackage assigner for business flows."""

from typing import Dict, List, Set
from ..models.business_flow import BusinessFlow
from ..models.priority import PriorityResult
from ..models.workpackage import WorkpackageAssignment


class WorkpackageAssigner:
    """Assigns workpackage IDs to business flows based on priority order."""
    
    def assign_workpackages(
        self,
        priorities: Dict[str, PriorityResult],
        flows: List[BusinessFlow]
    ) -> List[WorkpackageAssignment]:
        """
        Assign workpackage IDs based on priority order.
        
        Flows are sorted by priority score (ascending) with stable sort by flowId
        for equal priorities. Sequential workpackage IDs are assigned starting from 1.
        Pre-existent modules are identified for each workpackage.
        
        Args:
            priorities: Dictionary mapping flow_id to PriorityResult
            flows: List of BusinessFlow objects
            
        Returns:
            List of WorkpackageAssignment objects sorted by workpackage_id
        """
        # Sort flows by priority score (ascending), then by flowId for stable sort
        sorted_flows = sorted(
            flows,
            key=lambda f: (priorities[f.flow_id].priority_score, f.flow_id)
        )
        
        # Track programs across workpackages
        assigned_programs: Set[str] = set()
        assignments: List[WorkpackageAssignment] = []
        
        # Assign sequential workpackage IDs starting from 1
        for workpackage_id, flow in enumerate(sorted_flows, start=1):
            priority_result = priorities[flow.flow_id]
            
            # Identify pre-existent modules
            preexistent_modules = self.identify_preexistent_modules(
                flow,
                assigned_programs
            )
            
            # Create workpackage assignment
            assignment = WorkpackageAssignment(
                workpackage_id=workpackage_id,
                flow_id=flow.flow_id,
                priority_score=priority_result.priority_score,
                preexistent_modules=preexistent_modules
            )
            
            assignments.append(assignment)
            
            # Update assigned programs set
            assigned_programs.update(flow.get_program_names())
        
        return assignments
    
    def identify_preexistent_modules(
        self,
        flow: BusinessFlow,
        assigned_programs: Set[str]
    ) -> List[str]:
        """
        Identify programs that appear in higher-priority workpackages.
        
        Args:
            flow: BusinessFlow to analyze
            assigned_programs: Set of program names already assigned to workpackages
            
        Returns:
            List of program names that are pre-existent (sorted for consistency)
        """
        preexistent = []
        
        for program in flow.programs:
            if program.name in assigned_programs:
                preexistent.append(program.name)
        
        # Sort for consistent output
        return sorted(preexistent)
