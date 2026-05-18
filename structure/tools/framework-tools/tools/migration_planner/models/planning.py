"""Data models for planning output and metadata."""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

from .workpackage import WorkpackageAssignment
from .phase import PhaseAssignment, MigrationSequenceItem


@dataclass
class Metadata:
    """Metadata for planning output."""
    
    project_name: str
    created_date: str
    phase: str = "WORKPACKAGE_PLANNING"
    version: str = "1.0"
    
    @classmethod
    def create(cls, project_name: str) -> 'Metadata':
        """Create metadata with current timestamp."""
        return cls(
            project_name=project_name,
            created_date=datetime.utcnow().isoformat() + 'Z'
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"Metadata({self.project_name}, {self.phase}, v{self.version})"


@dataclass
class Statistics:
    """Statistics for planning output."""
    
    total_flows: int
    total_phases: int
    average_priority_score: float
    flows_per_phase: Dict[int, int] = field(default_factory=dict)
    
    @classmethod
    def calculate(cls, 
                  flow_priorities: Dict[str, WorkpackageAssignment],
                  phases: List[PhaseAssignment]) -> 'Statistics':
        """Calculate statistics from planning data."""
        total_flows = len(flow_priorities)
        total_phases = len(phases)
        
        # Calculate average priority score
        if total_flows > 0:
            total_score = sum(wp.priority_score for wp in flow_priorities.values())
            avg_score = total_score / total_flows
        else:
            avg_score = 0.0
        
        # Calculate flows per phase
        flows_per_phase = {phase.phase_id: len(phase.workpackages) for phase in phases}
        
        return cls(
            total_flows=total_flows,
            total_phases=total_phases,
            average_priority_score=avg_score,
            flows_per_phase=flows_per_phase
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"Statistics(flows={self.total_flows}, "
            f"phases={self.total_phases}, "
            f"avg_priority={self.average_priority_score:.2f})"
        )


@dataclass
class PlanningData:
    """Complete planning data for output generation."""
    
    metadata: Metadata
    flow_priorities: Dict[str, WorkpackageAssignment]
    phases: List[PhaseAssignment]
    migration_sequence: List[MigrationSequenceItem]
    statistics: Statistics
    shared_module_report: Dict = field(default_factory=dict)
    coordination_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    shared_module_context: Dict[str, Dict] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"PlanningData({self.metadata.project_name}): "
            f"{self.statistics.total_flows} flows, "
            f"{self.statistics.total_phases} phases"
        )
