"""
Artifact model for inventory management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class ArtifactType(Enum):
    """Types of artifacts in the inventory."""
    PROGRAM = "PROGRAM"
    COPYBOOK = "COPYBOOK"
    JCL = "JCL"
    DATASET = "DATASET"
    TRANSACTION = "TRANSACTION"
    FILE = "FILE"
    TABLE = "TABLE"
    MACRO = "MACRO"


@dataclass
class Artifact:
    """Represents a source code artifact in the inventory."""
    
    # Core identification
    artifact_name: str  # Primary name (PROGRAM-ID or filename)
    filename: str  # File name without extension
    artifact_type: ArtifactType
    language: str
    
    # File information
    file_extension: str
    file_path: str
    file_size: Optional[int] = None
    last_modified: Optional[float] = None
    
    # Program information
    program_id: Optional[str] = None  # Extracted PROGRAM-ID
    
    # Analysis status
    analyzed: bool = False
    
    # Program-level information (for multi-program files)
    program_within_file: Optional[str] = None
    file_program_index: Optional[int] = None
    program_start_line: Optional[int] = None
    program_end_line: Optional[int] = None
    program_type: Optional[str] = None
    
    # Mixed content support
    is_mixed_content: bool = False
    program_count: int = 1
    mixed_content_summary: Optional[Dict[str, Any]] = None
    program_boundaries: Optional[List] = None  # List[ProgramBoundary] - avoid circular import
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.artifact_name:
            raise ValueError("artifact_name is required")
        if not self.filename:
            raise ValueError("filename is required")
        if not self.file_path:
            raise ValueError("file_path is required")
    
    @property
    def is_copybook(self) -> bool:
        """Check if this artifact is a copybook."""
        return self.artifact_type == ArtifactType.COPYBOOK
    
    @property
    def is_program(self) -> bool:
        """Check if this artifact is a program."""
        return self.artifact_type == ArtifactType.PROGRAM
    
    @property
    def is_jcl(self) -> bool:
        """Check if this artifact is JCL."""
        return self.artifact_type == ArtifactType.JCL
    
    @property
    def primary_name(self) -> str:
        """Get the primary name for this artifact (PROGRAM-ID if available, otherwise filename)."""
        return self.program_id if self.program_id else self.artifact_name
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'artifact_name': self.artifact_name,
            'filename': self.filename,
            'program_id': self.program_id,
            'artifact_type': self.artifact_type.value,
            'language': self.language,
            'file_extension': self.file_extension,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'analyzed': 1 if self.analyzed else 0,
            'last_modified': self.last_modified,
            'program_within_file': self.program_within_file,
            'file_program_index': self.file_program_index,
            'program_start_line': self.program_start_line,
            'program_end_line': self.program_end_line,
            'program_type': self.program_type
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Artifact':
        """Create artifact from dictionary."""
        return cls(
            artifact_name=data['artifact_name'],
            filename=data['filename'],
            artifact_type=ArtifactType(data['artifact_type']),
            language=data['language'],
            file_extension=data['file_extension'],
            file_path=data['file_path'],
            file_size=data.get('file_size'),
            last_modified=data.get('last_modified'),
            program_id=data.get('program_id'),
            analyzed=bool(data.get('analyzed', 0)),
            program_within_file=data.get('program_within_file'),
            file_program_index=data.get('file_program_index'),
            program_start_line=data.get('program_start_line'),
            program_end_line=data.get('program_end_line'),
            program_type=data.get('program_type')
        )