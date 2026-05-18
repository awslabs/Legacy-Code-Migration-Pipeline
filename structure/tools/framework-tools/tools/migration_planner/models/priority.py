"""Data models for priority calculation."""

from dataclasses import dataclass


@dataclass
class PriorityFactors:
    """Breakdown of priority score factors."""
    
    total_programs: int
    common_modules: int
    composite_score: float
    complete_flow_bonus: int
    simple_flow_bonus: int
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"PriorityFactors(programs={self.total_programs}, "
            f"common={self.common_modules}, "
            f"composite={self.composite_score:.1f}, "
            f"complete_bonus={self.complete_flow_bonus}, "
            f"simple_bonus={self.simple_flow_bonus})"
        )


@dataclass
class PriorityResult:
    """Result of priority calculation for a flow."""
    
    flow_id: str
    priority_score: float
    factors: PriorityFactors
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"PriorityResult({self.flow_id}): "
            f"score={self.priority_score:.2f}, "
            f"factors={self.factors}"
        )
    
    def __lt__(self, other) -> bool:
        """Compare by priority score for sorting (lower score = higher priority)."""
        if not isinstance(other, PriorityResult):
            return NotImplemented
        return self.priority_score < other.priority_score
