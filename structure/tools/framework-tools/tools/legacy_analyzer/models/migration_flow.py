"""
Data models for migration-focused flow export.

This module defines data models for migration flows, including flow metadata,
entry point types, scope, interfaces, data operations, and dependencies.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ComplexityTier(Enum):
    """Complexity tier classification for migration flows."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class EntryPointType(Enum):
    """Types of entry points for migration flows."""
    
    JCL = "JCL"
    CICS_TRANSACTION = "CICS_TRANSACTION"
    CICS_PROGRAM = "CICS_PROGRAM"
    SCREEN = "SCREEN"
    BATCH = "BATCH"
    EXTERNAL_CALL = "EXTERNAL_CALL"


class InterfaceDirection(Enum):
    """Direction of interface crossing."""
    
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class DataOperationCategory(Enum):
    """Category of data operation."""
    
    DATABASE = "DATABASE"
    DATASET = "DATASET"


class DataOperationType(Enum):
    """Type of data operation."""
    
    READ = "READ"
    WRITE = "WRITE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"
    INSERT = "INSERT"
    UNKNOWN = "UNKNOWN"


class DatasetMode(Enum):
    """Dataset access mode."""
    
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    INOUT = "INOUT"


class DatabaseType(Enum):
    """Type of database system."""
    
    DB2 = "DB2"
    IMS = "IMS"
    IDMS = "IDMS"
    ADABAS = "ADABAS"
    VSAM = "VSAM"
    SQL = "SQL"
    UNKNOWN = "UNKNOWN"


@dataclass
class EntryPointCaller:
    """Represents a caller of an entry point."""
    
    source: str  # JCL name, transaction ID, screen name, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'source': self.source
        }
        if self.metadata:
            result['metadata'] = self.metadata
        return result


@dataclass
class EntryPointTypeInfo:
    """Represents an entry point type with its callers."""
    
    type: str  # EntryPointType value
    callers: List[EntryPointCaller] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'callers': [caller.to_dict() for caller in self.callers]
        }
    
    def add_caller(self, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a caller to this entry point type."""
        caller = EntryPointCaller(source=source, metadata=metadata or {})
        self.callers.append(caller)


@dataclass
class MigrationEntryPoint:
    """Represents the entry point of a migration flow."""
    
    program: str
    types: List[EntryPointTypeInfo] = field(default_factory=list)
    primary_type: Optional[str] = None  # Most common invocation type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'program': self.program,
            'types': [t.to_dict() for t in self.types]
        }
        if self.primary_type:
            result['primaryType'] = self.primary_type
        return result
    
    def add_type(self, entry_type: str, source: str, 
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an entry point type and caller."""
        # Find existing type or create new one
        type_info = next((t for t in self.types if t.type == entry_type), None)
        if type_info is None:
            type_info = EntryPointTypeInfo(type=entry_type)
            self.types.append(type_info)
        
        # Add caller
        type_info.add_caller(source, metadata)
    
    def get_all_callers(self) -> List[str]:
        """Get all caller sources across all types."""
        callers = []
        for type_info in self.types:
            callers.extend([c.source for c in type_info.callers])
        return callers
    
    def determine_primary_type(self) -> Optional[str]:
        """Determine the primary (most common) entry point type."""
        if not self.types:
            return None
        
        # Count callers per type
        type_counts = [(t.type, len(t.callers)) for t in self.types]
        
        # Sort by count (descending)
        type_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Return type with most callers
        return type_counts[0][0] if type_counts else None


@dataclass
class FlowScope:
    """Represents the scope of artifacts within a migration flow."""
    
    programs: List[str] = field(default_factory=list)
    copybooks: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'programs': self.programs,
            'copybooks': self.copybooks,
            'datasets': self.datasets
        }
    
    def add_program(self, program: str) -> None:
        """Add a program to scope."""
        if program not in self.programs:
            self.programs.append(program)
    
    def add_copybook(self, copybook: str) -> None:
        """Add a copybook to scope."""
        if copybook not in self.copybooks:
            self.copybooks.append(copybook)
    
    def add_dataset(self, dataset: str) -> None:
        """Add a dataset to scope."""
        if dataset not in self.datasets:
            self.datasets.append(dataset)
    
    def get_total_artifacts(self) -> int:
        """Get total count of all artifacts in scope."""
        return len(self.programs) + len(self.copybooks) + len(self.datasets)


@dataclass
class FlowInterface:
    """Represents an interface crossing the migration boundary."""
    
    type: str  # Interface type (JCL, PROGRAM_CALL, CICS_LINK, etc.)
    source: str  # Source artifact name
    target: str  # Target artifact name
    direction: str  # INBOUND or OUTBOUND
    external: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'type': self.type,
            'source': self.source,
            'target': self.target
        }
        if self.external:
            result['external'] = self.external
        if self.metadata:
            result['metadata'] = self.metadata
        return result


@dataclass
class FlowInterfaces:
    """Collection of inbound and outbound interfaces."""
    
    inbound: List[FlowInterface] = field(default_factory=list)
    outbound: List[FlowInterface] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'inbound': [i.to_dict() for i in self.inbound],
            'outbound': [i.to_dict() for i in self.outbound]
        }
    
    def add_inbound(self, interface: FlowInterface) -> None:
        """Add an inbound interface."""
        interface.direction = InterfaceDirection.INBOUND.value
        self.inbound.append(interface)
    
    def add_outbound(self, interface: FlowInterface) -> None:
        """Add an outbound interface."""
        interface.direction = InterfaceDirection.OUTBOUND.value
        interface.external = True
        self.outbound.append(interface)


@dataclass
class DatabaseOperation:
    """Represents a database operation."""
    
    type: str  # Database type (DB2, IMS, etc.)
    operation: str  # Operation type (READ, WRITE, etc.)
    target: str  # Table/file name
    program: str  # Program performing operation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'operation': self.operation,
            'target': self.target,
            'program': self.program
        }


@dataclass
class DatasetOperation:
    """Represents a dataset operation."""
    
    name: str  # Dataset name
    mode: str  # Access mode (INPUT, OUTPUT, INOUT)
    programs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'mode': self.mode,
            'programs': self.programs
        }
    
    def add_program(self, program: str) -> None:
        """Add a program that accesses this dataset."""
        if program not in self.programs:
            self.programs.append(program)


@dataclass
class DataOperations:
    """Collection of database and dataset operations."""
    
    databases: List[DatabaseOperation] = field(default_factory=list)
    datasets: List[DatasetOperation] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'databases': [db.to_dict() for db in self.databases],
            'datasets': [ds.to_dict() for ds in self.datasets]
        }
    
    def add_database_operation(self, operation: DatabaseOperation) -> None:
        """Add a database operation."""
        self.databases.append(operation)
    
    def add_dataset_operation(self, operation: DatasetOperation) -> None:
        """Add a dataset operation."""
        # Check if dataset already exists
        existing = next((ds for ds in self.datasets if ds.name == operation.name), None)
        if existing:
            # Merge programs
            for program in operation.programs:
                existing.add_program(program)
        else:
            self.datasets.append(operation)


@dataclass
class FlowComplexity:
    """Complexity metrics for a migration flow."""
    
    total_programs: int
    total_lines: int
    cyclomatic_complexity: int
    composite_score: float
    tier: str  # ComplexityTier value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'totalPrograms': self.total_programs,
            'totalLines': self.total_lines,
            'cyclomaticComplexity': self.cyclomatic_complexity,
            'compositeScore': self.composite_score,
            'tier': self.tier
        }


@dataclass
class FlowDependencies:
    """Flow-to-flow dependencies."""
    
    required_flows: List[str] = field(default_factory=list)  # Must migrate before this
    dependent_flows: List[str] = field(default_factory=list)  # Depend on this flow
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'requiredFlows': self.required_flows,
            'dependentFlows': self.dependent_flows
        }
    
    def add_required_flow(self, flow_id: str) -> None:
        """Add a required flow dependency."""
        if flow_id not in self.required_flows:
            self.required_flows.append(flow_id)
    
    def add_dependent_flow(self, flow_id: str) -> None:
        """Add a dependent flow."""
        if flow_id not in self.dependent_flows:
            self.dependent_flows.append(flow_id)


@dataclass
class MigrationFlow:
    """
    Complete migration flow data model.
    
    Represents a migration flow with all associated metadata, scope,
    interfaces, data operations, complexity, and dependencies.
    """
    
    flow_id: str
    name: str
    entry_point: MigrationEntryPoint
    scope: FlowScope
    interfaces: FlowInterfaces
    data_operations: DataOperations
    complexity: FlowComplexity
    dependencies: FlowDependencies
    priority: Optional[int] = None
    business_domain: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'flowId': self.flow_id,
            'name': self.name,
            'entryPoint': self.entry_point.to_dict(),
            'scope': self.scope.to_dict(),
            'interfaces': self.interfaces.to_dict(),
            'dataOperations': self.data_operations.to_dict(),
            'complexity': self.complexity.to_dict(),
            'dependencies': self.dependencies.to_dict()
        }
        
        # Add optional fields
        if self.priority is not None:
            result['priority'] = self.priority
        if self.business_domain:
            result['businessDomain'] = self.business_domain
        
        return result
    
    def get_total_artifacts(self) -> int:
        """Get total count of artifacts in scope."""
        return self.scope.get_total_artifacts()
    
    def get_total_interfaces(self) -> int:
        """Get total count of interfaces."""
        return len(self.interfaces.inbound) + len(self.interfaces.outbound)
    
    def get_total_data_operations(self) -> int:
        """Get total count of data operations."""
        return len(self.data_operations.databases) + len(self.data_operations.datasets)
    
    def has_dependencies(self) -> bool:
        """Check if flow has any dependencies."""
        return (len(self.dependencies.required_flows) > 0 or 
                len(self.dependencies.dependent_flows) > 0)
    
    def is_high_complexity(self) -> bool:
        """Check if flow has high or very high complexity."""
        return self.complexity.tier in [ComplexityTier.HIGH.value, 
                                       ComplexityTier.VERY_HIGH.value]
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"MigrationFlow({self.flow_id}): "
            f"{self.scope.get_total_artifacts()} artifacts, "
            f"{self.get_total_interfaces()} interfaces, "
            f"complexity={self.complexity.tier}"
        )
