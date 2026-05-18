"""Priority calculator for business flows."""

from typing import Dict, List
from ..models.business_flow import BusinessFlow
from ..models.priority import PriorityResult, PriorityFactors


class PriorityCalculator:
    """Calculates priority scores for business flows based on complexity metrics."""
    
    def __init__(self, classifications: Dict[str, str]):
        """
        Initialize priority calculator with module classifications.
        
        Args:
            classifications: Dictionary mapping program names to classification types.
                           Programs classified as "COMMONLY_USED" receive bonus weight.
        """
        self.classifications = classifications or {}
    
    def calculate_priority(self, flow: BusinessFlow) -> PriorityResult:
        """
        Calculate priority score for a single business flow.
        
        Priority formula:
        priority = (totalPrograms × 2) + (commonModules × 3) + (compositeScore × 0.5) 
                   + completeFlowBonus + simpleFlowBonus
        
        Args:
            flow: BusinessFlow to calculate priority for
            
        Returns:
            PriorityResult containing score and factor breakdown
        """
        # Extract totalPrograms from complexity
        total_programs = flow.total_programs
        
        # Extract compositeScore from complexity
        composite_score = flow.composite_score
        
        # Count common modules (programs classified as "COMMONLY_USED")
        common_modules = self._count_common_modules(flow)
        
        # Calculate complete flow bonus (-5 if has databases, 0 otherwise)
        complete_flow_bonus = -5 if flow.has_databases() else 0
        
        # Calculate simple flow bonus based on program count
        simple_flow_bonus = self._calculate_simple_flow_bonus(total_programs)
        
        # Calculate final priority score
        priority_score = (
            (total_programs * 2) +
            (common_modules * 3) +
            (composite_score * 0.5) +
            complete_flow_bonus +
            simple_flow_bonus
        )
        
        # Store priority factors breakdown
        factors = PriorityFactors(
            total_programs=total_programs,
            common_modules=common_modules,
            composite_score=composite_score,
            complete_flow_bonus=complete_flow_bonus,
            simple_flow_bonus=simple_flow_bonus
        )
        
        return PriorityResult(
            flow_id=flow.flow_id,
            priority_score=priority_score,
            factors=factors
        )
    
    def calculate_all_priorities(self, flows: List[BusinessFlow]) -> Dict[str, PriorityResult]:
        """
        Calculate priorities for all flows.
        
        Args:
            flows: List of BusinessFlow objects
            
        Returns:
            Dictionary mapping flow_id to PriorityResult
        """
        return {
            flow.flow_id: self.calculate_priority(flow)
            for flow in flows
        }
    
    def _count_common_modules(self, flow: BusinessFlow) -> int:
        """
        Count programs in flow that are classified as "COMMONLY_USED".
        
        Args:
            flow: BusinessFlow to analyze
            
        Returns:
            Count of common modules
        """
        if not self.classifications:
            return 0
        
        count = 0
        for program in flow.programs:
            classification = self.classifications.get(program.name, "")
            if classification == "COMMONLY_USED":
                count += 1
        
        return count
    
    def _calculate_simple_flow_bonus(self, total_programs: int) -> int:
        """
        Calculate simple flow bonus based on program count.
        
        Rules:
        - totalPrograms <= 3: bonus = -3
        - 3 < totalPrograms <= 5: bonus = -1
        - totalPrograms > 5: bonus = 0
        
        Args:
            total_programs: Number of programs in the flow
            
        Returns:
            Simple flow bonus value
        """
        if total_programs <= 3:
            return -3
        elif total_programs <= 5:
            return -1
        else:
            return 0
