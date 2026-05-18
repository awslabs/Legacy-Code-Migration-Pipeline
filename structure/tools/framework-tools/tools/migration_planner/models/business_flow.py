"""Data models for business flows and programs."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Program:
    """Represents a program within a business flow."""
    
    name: str
    is_utility: bool = False
    
    def __hash__(self) -> int:
        """Hash based on program name."""
        return hash(self.name)
    
    def __eq__(self, other) -> bool:
        """Equality based on program name."""
        if not isinstance(other, Program):
            return False
        return self.name == other.name


@dataclass
class BusinessFlow:
    """Represents a business flow with programs and dependencies."""
    
    flow_id: str
    name: str
    programs: List[Program] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    total_programs: int = 0
    composite_score: float = 0.0
    required_flows: List[str] = field(default_factory=list)
    dependent_flows: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate derived fields."""
        if self.total_programs == 0 and self.programs:
            self.total_programs = len(self.programs)
    
    def has_databases(self) -> bool:
        """Check if flow has database operations."""
        return len(self.databases) > 0
    
    def has_dependencies(self) -> bool:
        """Check if flow has dependencies on other flows."""
        return len(self.required_flows) > 0
    
    def get_program_names(self) -> List[str]:
        """Get list of program names in this flow."""
        return [prog.name for prog in self.programs]
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"BusinessFlow({self.flow_id}): "
            f"{self.total_programs} programs, "
            f"{len(self.databases)} databases, "
            f"{len(self.required_flows)} dependencies"
        )
