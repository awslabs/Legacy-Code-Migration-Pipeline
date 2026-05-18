"""Configuration data model for the planner."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PlannerConfig:
    """Configuration for the migration planner."""
    
    flows_file: Path
    output_base: Path
    project_name: str
    classifications_file: Optional[Path] = None
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.flows_file, str):
            self.flows_file = Path(self.flows_file)
        if isinstance(self.output_base, str):
            self.output_base = Path(self.output_base)
        if self.classifications_file and isinstance(self.classifications_file, str):
            self.classifications_file = Path(self.classifications_file)
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.flows_file.exists():
            raise FileNotFoundError(f"Flows file not found: {self.flows_file}")
        
        if self.classifications_file and not self.classifications_file.exists():
            raise FileNotFoundError(
                f"Classifications file not found: {self.classifications_file}"
            )
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"PlannerConfig(project={self.project_name}, "
            f"flows={self.flows_file}, "
            f"output={self.output_base})"
        )
