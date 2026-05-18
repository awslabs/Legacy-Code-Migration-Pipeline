"""Data models for missing artifacts."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Severity(Enum):
    """Severity levels for missing artifacts."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class MissingArtifact:
    """Represents an artifact referenced but not found in inventory."""
    
    artifact_name: str
    artifact_type: str  # PROGRAM, COPYBOOK, DATASET
    reference_count: int
    referenced_by: List[str] = field(default_factory=list)
    severity: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    first_detected: Optional[datetime] = None
    
    def __str__(self) -> str:
        """String representation of missing artifact."""
        return f"{self.artifact_type}: {self.artifact_name} (refs: {self.reference_count}, severity: {self.severity})"
    
    def __hash__(self) -> int:
        """Hash based on name and type."""
        return hash((self.artifact_name, self.artifact_type))
    
    def __eq__(self, other) -> bool:
        """Equality based on name and type."""
        if not isinstance(other, MissingArtifact):
            return False
        return (
            self.artifact_name == other.artifact_name and
            self.artifact_type == other.artifact_type
        )


@dataclass
class MissingArtifactReference:
    """Represents a reference to a missing artifact."""
    
    missing_artifact: str
    missing_artifact_type: str
    referenced_by: str
    referenced_by_type: str
    reference_type: str  # COPY, CALL, DATASET_REF, etc.
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    
    def __str__(self) -> str:
        """String representation of reference."""
        location = ""
        if self.source_file:
            location = f" at {self.source_file}"
            if self.line_number:
                location += f":{self.line_number}"
        return f"{self.referenced_by} --[{self.reference_type}]--> {self.missing_artifact}{location}"


@dataclass
class CompletenessReport:
    """Report on inventory completeness."""
    
    # Inventory totals
    total_inventory_programs: int = 0
    total_inventory_copybooks: int = 0
    total_inventory_datasets: int = 0
    
    # Referenced artifacts (dependencies)
    total_referenced_programs: int = 0
    found_programs: int = 0
    missing_programs: int = 0
    
    total_referenced_copybooks: int = 0
    found_copybooks: int = 0
    missing_copybooks: int = 0
    
    total_referenced_datasets: int = 0
    found_datasets: int = 0
    missing_datasets: int = 0
    
    overall_completeness: float = 0.0  # 0.0 to 1.0
    program_completeness: float = 0.0
    copybook_completeness: float = 0.0
    dataset_completeness: float = 0.0
    
    missing_artifacts: List[MissingArtifact] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String representation of completeness report."""
        return f"""Completeness Report:
  Overall: {self.overall_completeness:.1%}
  
  Inventory:
    Programs:  {self.total_inventory_programs}
    Copybooks: {self.total_inventory_copybooks}
    Datasets:  {self.total_inventory_datasets}
  
  Dependency Completeness:
    Programs:  {self.program_completeness:.1%} ({self.found_programs}/{self.total_referenced_programs} referenced found)
    Copybooks: {self.copybook_completeness:.1%} ({self.found_copybooks}/{self.total_referenced_copybooks} referenced found)
    Datasets:  {self.dataset_completeness:.1%} ({self.found_datasets}/{self.total_referenced_datasets} referenced found)
  
  Total Missing: {len(self.missing_artifacts)}"""


# Severity classification thresholds
class SeverityThreshold:
    """Thresholds for severity classification."""
    
    HIGH = 10  # 10+ references = HIGH severity
    MEDIUM = 3  # 3-9 references = MEDIUM severity
    # 1-2 references = LOW severity
    
    @classmethod
    def classify(cls, reference_count: int) -> str:
        """
        Classify severity based on reference count.
        
        Args:
            reference_count: Number of references to the artifact
            
        Returns:
            Severity level (HIGH, MEDIUM, LOW)
        """
        if reference_count >= cls.HIGH:
            return "HIGH"
        elif reference_count >= cls.MEDIUM:
            return "MEDIUM"
        else:
            return "LOW"
