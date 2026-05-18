"""Data models for workpackage assignment."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class WorkpackageAssignment:
    """Workpackage assignment for a business flow."""
    
    workpackage_id: int
    flow_id: str
    priority_score: float
    preexistent_modules: List[str] = field(default_factory=list)
    
    def has_preexistent_modules(self) -> bool:
        """Check if workpackage has pre-existent modules."""
        return len(self.preexistent_modules) > 0
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"Workpackage {self.workpackage_id}: "
            f"{self.flow_id} (priority={self.priority_score:.2f}, "
            f"preexistent={len(self.preexistent_modules)})"
        )
