"""Data models for migration packages."""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from datetime import datetime


@dataclass
class MigrationPackage:
    """Represents a migration package containing related artifacts."""
    
    name: str
    artifacts: List[str]  # List of artifact names
    
    # Size metrics
    total_loc: int = 0
    total_complexity: float = 0.0
    total_artifacts: int = 0
    
    # Dependencies
    external_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)  # Artifacts in multiple packages
    
    # Metadata
    created_date: Optional[datetime] = None
    description: Optional[str] = None
    priority: Optional[int] = None  # 1=highest, lower numbers = higher priority
    
    # Artifact breakdown by type
    programs: List[str] = field(default_factory=list)
    copybooks: List[str] = field(default_factory=list)
    jcl: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate totals after initialization."""
        if self.total_artifacts == 0:
            self.total_artifacts = len(self.artifacts)
    
    def add_artifact(self, artifact_name: str, artifact_type: str) -> None:
        """Add an artifact to the package."""
        if artifact_name not in self.artifacts:
            self.artifacts.append(artifact_name)
            self.total_artifacts = len(self.artifacts)
            
            # Add to type-specific list
            if artifact_type == 'PROGRAM':
                self.programs.append(artifact_name)
            elif artifact_type == 'COPYBOOK':
                self.copybooks.append(artifact_name)
            elif artifact_type == 'JCL':
                self.jcl.append(artifact_name)
            elif artifact_type == 'DATASET':
                self.datasets.append(artifact_name)
    
    def add_external_dependency(self, artifact_name: str) -> None:
        """Add an external dependency."""
        if artifact_name not in self.external_dependencies:
            self.external_dependencies.append(artifact_name)
    
    def add_conflict(self, artifact_name: str) -> None:
        """Add a conflict (artifact in multiple packages)."""
        if artifact_name not in self.conflicts:
            self.conflicts.append(artifact_name)
    
    def is_self_contained(self) -> bool:
        """Check if package is self-contained (no external dependencies)."""
        return len(self.external_dependencies) == 0
    
    def has_conflicts(self) -> bool:
        """Check if package has conflicts."""
        return len(self.conflicts) > 0
    
    def get_artifact_count_by_type(self) -> Dict[str, int]:
        """Get count of artifacts by type."""
        return {
            'programs': len(self.programs),
            'copybooks': len(self.copybooks),
            'jcl': len(self.jcl),
            'datasets': len(self.datasets)
        }
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"Package '{self.name}': {self.total_artifacts} artifacts, "
            f"{self.total_loc} LOC, complexity={self.total_complexity:.1f}"
        )


@dataclass
class PackageConstraints:
    """Constraints for migration package creation."""
    
    max_artifacts: Optional[int] = None
    max_loc: Optional[int] = None
    max_complexity: Optional[float] = None
    allow_external_deps: bool = False
    max_external_deps: Optional[int] = None
    
    def validate_package(self, package: MigrationPackage) -> List[str]:
        """
        Validate a package against constraints.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if self.max_artifacts and package.total_artifacts > self.max_artifacts:
            errors.append(
                f"Package exceeds max artifacts: {package.total_artifacts} > {self.max_artifacts}"
            )
        
        if self.max_loc and package.total_loc > self.max_loc:
            errors.append(
                f"Package exceeds max LOC: {package.total_loc} > {self.max_loc}"
            )
        
        if self.max_complexity and package.total_complexity > self.max_complexity:
            errors.append(
                f"Package exceeds max complexity: {package.total_complexity:.1f} > {self.max_complexity}"
            )
        
        if not self.allow_external_deps and len(package.external_dependencies) > 0:
            errors.append(
                f"Package has external dependencies but they are not allowed: "
                f"{len(package.external_dependencies)} dependencies"
            )
        
        if (self.max_external_deps and 
            len(package.external_dependencies) > self.max_external_deps):
            errors.append(
                f"Package exceeds max external dependencies: "
                f"{len(package.external_dependencies)} > {self.max_external_deps}"
            )
        
        return errors
    
    def is_valid(self, package: MigrationPackage) -> bool:
        """Check if package is valid against constraints."""
        return len(self.validate_package(package)) == 0


@dataclass
class PackageConflict:
    """Represents a conflict between packages."""
    
    artifact_name: str
    packages: List[str]  # List of package names containing this artifact
    
    def __str__(self) -> str:
        """String representation."""
        return f"Artifact '{self.artifact_name}' in packages: {', '.join(self.packages)}"
