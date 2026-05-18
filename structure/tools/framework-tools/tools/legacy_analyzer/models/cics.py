"""Data models for CICS resources."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CICSResource:
    """Base class for CICS resources."""
    
    resource_name: str
    resource_type: str  # TRANSACTION, PROGRAM, FILE, MAPSET
    group_name: str
    status: str  # ENABLED, DISABLED
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    
    def to_csv_row(self) -> Dict[str, Any]:
        """
        Convert to CSV row format.
        
        Returns:
            Dictionary with CSV column names as keys
        """
        return {
            'resource_name': self.resource_name,
            'resource_type': self.resource_type,
            'group_name': self.group_name,
            'status': self.status,
            'program_name': '',
            'dataset_name': '',
            'description': ''
        }
    
    def __str__(self) -> str:
        """String representation of CICS resource."""
        return f"{self.resource_type}({self.resource_name}) in {self.group_name}"
    
    def __hash__(self) -> int:
        """Hash based on resource name and type."""
        return hash((self.resource_name, self.resource_type))
    
    def __eq__(self, other) -> bool:
        """Equality based on resource name and type."""
        if not isinstance(other, CICSResource):
            return False
        return (self.resource_name == other.resource_name and 
                self.resource_type == other.resource_type)


@dataclass
class CICSTransaction(CICSResource):
    """Represents a CICS transaction definition."""
    
    transaction_id: str = ''  # 4-char transaction code
    program_name: str = ''    # Associated program
    description: Optional[str] = None
    priority: Optional[int] = None
    
    def __init__(
        self,
        transaction_id: str,
        program_name: str,
        group_name: str,
        status: str = 'ENABLED',
        description: Optional[str] = None,
        priority: Optional[int] = None,
        source_file: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        """Initialize CICS transaction."""
        super().__init__(
            resource_name=transaction_id,
            resource_type='TRANSACTION',
            group_name=group_name,
            status=status,
            source_file=source_file,
            line_number=line_number
        )
        self.transaction_id = transaction_id
        self.program_name = program_name
        self.description = description
        self.priority = priority
    
    def to_csv_row(self) -> Dict[str, Any]:
        """
        Convert to CSV row format.
        
        Returns:
            Dictionary with CSV column names as keys
        """
        return {
            'resource_name': self.transaction_id,
            'resource_type': 'TRANSACTION',
            'group_name': self.group_name,
            'status': self.status,
            'program_name': self.program_name,
            'dataset_name': '',
            'description': self.description or ''
        }
    
    def __str__(self) -> str:
        """String representation of CICS transaction."""
        return f"TRANSACTION({self.transaction_id}) -> {self.program_name}"


@dataclass
class CICSProgram(CICSResource):
    """Represents a CICS program definition."""
    
    program_name: str = ''
    language: Optional[str] = None
    transaction_id: Optional[str] = None  # If TRANSID attribute present
    concurrency: Optional[str] = None     # QUASIRENT, THREADSAFE
    
    def __init__(
        self,
        program_name: str,
        group_name: str,
        status: str = 'ENABLED',
        language: Optional[str] = None,
        transaction_id: Optional[str] = None,
        concurrency: Optional[str] = None,
        source_file: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        """Initialize CICS program."""
        super().__init__(
            resource_name=program_name,
            resource_type='PROGRAM',
            group_name=group_name,
            status=status,
            source_file=source_file,
            line_number=line_number
        )
        self.program_name = program_name
        self.language = language
        self.transaction_id = transaction_id
        self.concurrency = concurrency
    
    def to_csv_row(self) -> Dict[str, Any]:
        """
        Convert to CSV row format.
        
        Returns:
            Dictionary with CSV column names as keys
        """
        return {
            'resource_name': self.program_name,
            'resource_type': 'PROGRAM',
            'group_name': self.group_name,
            'status': self.status,
            'program_name': '',
            'dataset_name': '',
            'description': ''
        }
    
    def __str__(self) -> str:
        """String representation of CICS program."""
        lang = f" ({self.language})" if self.language else ""
        return f"PROGRAM({self.program_name}){lang}"


@dataclass
class CICSFile(CICSResource):
    """Represents a CICS file definition."""
    
    file_name: str = ''           # CICS file name (8 chars)
    dataset_name: str = ''        # MVS dataset name
    file_type: Optional[str] = None  # VSAM, etc.
    
    def __init__(
        self,
        file_name: str,
        dataset_name: str,
        group_name: str,
        status: str = 'ENABLED',
        file_type: Optional[str] = None,
        source_file: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        """Initialize CICS file."""
        super().__init__(
            resource_name=file_name,
            resource_type='FILE',
            group_name=group_name,
            status=status,
            source_file=source_file,
            line_number=line_number
        )
        self.file_name = file_name
        self.dataset_name = dataset_name
        self.file_type = file_type
    
    def to_csv_row(self) -> Dict[str, Any]:
        """
        Convert to CSV row format.
        
        Returns:
            Dictionary with CSV column names as keys
        """
        return {
            'resource_name': self.file_name,
            'resource_type': 'FILE',
            'group_name': self.group_name,
            'status': self.status,
            'program_name': '',
            'dataset_name': self.dataset_name,
            'description': ''
        }
    
    def __str__(self) -> str:
        """String representation of CICS file."""
        return f"FILE({self.file_name}) -> {self.dataset_name}"


@dataclass
class CICSMapset(CICSResource):
    """Represents a CICS mapset definition."""
    
    mapset_name: str = ''
    description: Optional[str] = None
    
    def __init__(
        self,
        mapset_name: str,
        group_name: str,
        status: str = 'ENABLED',
        description: Optional[str] = None,
        source_file: Optional[str] = None,
        line_number: Optional[int] = None
    ):
        """Initialize CICS mapset."""
        super().__init__(
            resource_name=mapset_name,
            resource_type='MAPSET',
            group_name=group_name,
            status=status,
            source_file=source_file,
            line_number=line_number
        )
        self.mapset_name = mapset_name
        self.description = description
    
    def to_csv_row(self) -> Dict[str, Any]:
        """
        Convert to CSV row format.
        
        Returns:
            Dictionary with CSV column names as keys
        """
        return {
            'resource_name': self.mapset_name,
            'resource_type': 'MAPSET',
            'group_name': self.group_name,
            'status': self.status,
            'program_name': '',
            'dataset_name': '',
            'description': self.description or ''
        }
    
    def __str__(self) -> str:
        """String representation of CICS mapset."""
        return f"MAPSET({self.mapset_name})"
