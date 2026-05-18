"""Data models for program boundary detection and analysis."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ProgramType(Enum):
    """Types of programs that can be detected within files."""
    MAIN = "MAIN"
    PROCEDURE = "PROCEDURE"
    CSECT = "CSECT"
    SUBPROGRAM = "SUBPROGRAM"
    FUNCTION = "FUNCTION"
    ENTRY_POINT = "ENTRY_POINT"
    NESTED = "NESTED"
    JOB = "JOB"  # JCL job
    DATA = "DATA"  # Data section
    ROUTINE = "ROUTINE"  # Assembly routine
    UNKNOWN = "UNKNOWN"  # Unknown type
    
    # Legacy aliases for backward compatibility
    JCL = "JOB"
    ASSEMBLER = "ROUTINE"


@dataclass
class ProgramBoundary:
    """Represents the boundaries and metadata of a program within a source file."""
    
    program_name: str
    start_line: int
    end_line: int
    program_type: ProgramType
    language: str
    entry_points: List[str]
    
    # Optional metadata
    file_path: Optional[str] = None
    confidence_level: float = 1.0  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate program boundary data."""
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if not self.program_name.strip():
            raise ValueError("program_name cannot be empty")
        if self.confidence_level < 0.0 or self.confidence_level > 1.0:
            raise ValueError("confidence_level must be between 0.0 and 1.0")
    
    @property
    def line_count(self) -> int:
        """Number of lines in this program."""
        return self.end_line - self.start_line + 1
    
    def contains_line(self, line_number: int) -> bool:
        """Check if a line number falls within this program's boundaries."""
        return self.start_line <= line_number <= self.end_line
    
    def overlaps_with(self, other: 'ProgramBoundary') -> bool:
        """Check if this program boundary overlaps with another."""
        return not (self.end_line < other.start_line or other.end_line < self.start_line)
    
    def __str__(self) -> str:
        """String representation of program boundary."""
        return f"{self.program_name} ({self.program_type.value}): lines {self.start_line}-{self.end_line}"


@dataclass
class ProgramParseResult:
    """Result of parsing a source file for program boundaries and dependencies."""
    
    file_path: str
    language: str
    programs: List[ProgramBoundary]
    dependencies: Dict[str, List[str]]  # program_name -> list of dependencies
    
    # Validation results
    has_overlaps: bool = False
    has_gaps: bool = False
    coverage_percentage: float = 0.0
    total_lines: int = 0
    
    def __post_init__(self):
        """Validate and calculate coverage statistics."""
        self._validate_boundaries()
        self._calculate_coverage()
    
    def _validate_boundaries(self):
        """Check for overlaps between program boundaries."""
        self.has_overlaps = False
        for i, prog1 in enumerate(self.programs):
            for prog2 in self.programs[i+1:]:
                if prog1.overlaps_with(prog2):
                    self.has_overlaps = True
                    break
            if self.has_overlaps:
                break
    
    def _calculate_coverage(self):
        """Calculate what percentage of the file is covered by program boundaries."""
        if not self.programs or self.total_lines == 0:
            self.coverage_percentage = 0.0
            return
        
        # Create a set of all covered lines
        covered_lines = set()
        for program in self.programs:
            for line in range(program.start_line, program.end_line + 1):
                covered_lines.add(line)
        
        self.coverage_percentage = len(covered_lines) / self.total_lines * 100.0
        
        # Check for gaps (lines not covered by any program)
        all_lines = set(range(1, self.total_lines + 1))
        uncovered_lines = all_lines - covered_lines
        self.has_gaps = len(uncovered_lines) > 0
    
    def get_program_at_line(self, line_number: int) -> Optional[ProgramBoundary]:
        """Get the program that contains the specified line number."""
        for program in self.programs:
            if program.contains_line(line_number):
                return program
        return None
    
    def get_programs_by_type(self, program_type: ProgramType) -> List[ProgramBoundary]:
        """Get all programs of a specific type."""
        return [prog for prog in self.programs if prog.program_type == program_type]


@dataclass
class CopybookAnalysisResult:
    """Result of analyzing copybook content for executable code."""
    
    copybook_name: str
    file_path: str
    has_executable_code: bool
    data_structures: List[str]
    procedure_calls: List[str]
    program_dependencies: List['Dependency']
    confidence_level: float
    
    # Analysis metadata
    language: Optional[str] = None
    analyzed_at: Optional[str] = None
    analysis_notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate copybook analysis result."""
        if self.confidence_level < 0.0 or self.confidence_level > 1.0:
            raise ValueError("confidence_level must be between 0.0 and 1.0")
        if not self.copybook_name.strip():
            raise ValueError("copybook_name cannot be empty")


# Import Dependency here to avoid circular imports
from .dependency import Dependency