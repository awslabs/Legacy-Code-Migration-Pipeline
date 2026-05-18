"""Data models for phase assignment and migration sequence."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class PhaseAssignment:
    """Phase assignment with workpackages and dependencies."""
    
    phase_id: int
    workpackages: List[int] = field(default_factory=list)
    dependencies: List[int] = field(default_factory=list)  # Previous phase IDs
    
    def add_workpackage(self, workpackage_id: int) -> None:
        """Add a workpackage to this phase."""
        if workpackage_id not in self.workpackages:
            self.workpackages.append(workpackage_id)
    
    def add_dependency(self, phase_id: int) -> None:
        """Add a dependency on a previous phase."""
        if phase_id not in self.dependencies:
            self.dependencies.append(phase_id)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"Phase {self.phase_id}: "
            f"{len(self.workpackages)} workpackages, "
            f"depends on phases {self.dependencies}"
        )


@dataclass
class MigrationSequenceItem:
    """Item in the migration sequence."""
    
    sequence_number: int
    workpackage_id: int
    flow_id: str
    phase: int
    wave: int = 1  # Migration wave within phase
    prerequisites: List[int] = field(default_factory=list)  # Hard prerequisites (workpackage IDs)
    soft_prerequisites: List[int] = field(default_factory=list)  # Soft prerequisites (workpackage IDs)
    shared_module_context: dict = field(default_factory=dict)  # Shared module information
    
    def __str__(self) -> str:
        """String representation."""
        prereq_str = f"requires WP{self.prerequisites}" if self.prerequisites else "no prerequisites"
        soft_str = f", recommends WP{self.soft_prerequisites}" if self.soft_prerequisites else ""
        return (
            f"Sequence {self.sequence_number}: "
            f"WP{self.workpackage_id} ({self.flow_id}) "
            f"in Phase {self.phase}, Wave {self.wave}, "
            f"{prereq_str}{soft_str}"
        )
    
    def __lt__(self, other) -> bool:
        """Compare by sequence number for sorting."""
        if not isinstance(other, MigrationSequenceItem):
            return NotImplemented
        return self.sequence_number < other.sequence_number
