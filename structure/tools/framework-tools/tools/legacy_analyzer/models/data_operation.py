"""Data models for data operations and lineage tracking."""

from dataclasses import dataclass, field
from typing import Optional, List, Set
from enum import Enum


class OperationType(Enum):
    """Types of data operations."""
    
    # File/Dataset operations
    READ = "READ"
    WRITE = "WRITE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    
    # SQL operations
    SELECT = "SELECT"
    INSERT = "INSERT"
    SQL_UPDATE = "SQL_UPDATE"
    SQL_DELETE = "SQL_DELETE"
    
    # CICS operations
    CICS_READ = "CICS_READ"
    CICS_WRITE = "CICS_WRITE"
    CICS_REWRITE = "CICS_REWRITE"
    CICS_DELETE = "CICS_DELETE"
    CICS_BROWSE = "CICS_BROWSE"
    
    # Access modes
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    IO = "I-O"
    EXTEND = "EXTEND"
    
    @classmethod
    def is_read_operation(cls, op_type: str) -> bool:
        """Check if operation is a read operation."""
        return op_type in {
            cls.READ.value, cls.SELECT.value, cls.CICS_READ.value, cls.CICS_BROWSE.value, cls.INPUT.value
        }
    
    @classmethod
    def is_write_operation(cls, op_type: str) -> bool:
        """Check if operation is a write operation."""
        return op_type in {
            cls.WRITE.value, cls.INSERT.value, cls.CICS_WRITE.value, cls.OUTPUT.value
        }
    
    @classmethod
    def is_update_operation(cls, op_type: str) -> bool:
        """Check if operation is an update operation."""
        return op_type in {
            cls.UPDATE.value, cls.SQL_UPDATE.value, cls.CICS_REWRITE.value, cls.IO.value
        }
    
    @classmethod
    def is_delete_operation(cls, op_type: str) -> bool:
        """Check if operation is a delete operation."""
        return op_type in {
            cls.DELETE.value, cls.SQL_DELETE.value, cls.CICS_DELETE.value
        }


@dataclass
class DataOperation:
    """Represents a data operation (CRUD) on a dataset, table, or file."""
    
    program: str
    target: str  # Dataset, table, or file name
    target_type: str  # DATASET, SQL_TABLE, CICS_FILE, etc.
    operation: str  # READ, WRITE, UPDATE, DELETE, SELECT, INSERT, etc.
    
    # Optional details
    access_mode: Optional[str] = None  # INPUT, OUTPUT, I-O, EXTEND
    line_number: Optional[int] = None
    source_file: Optional[str] = None
    
    # SQL-specific
    sql_statement: Optional[str] = None
    columns_accessed: Optional[List[str]] = None
    
    # Additional context
    notes: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.program} --[{self.operation}]--> {self.target}"
    
    def __hash__(self) -> int:
        """Hash based on program, target, and operation."""
        return hash((self.program, self.target, self.operation))
    
    def __eq__(self, other) -> bool:
        """Equality based on program, target, and operation."""
        if not isinstance(other, DataOperation):
            return False
        return (
            self.program == other.program and
            self.target == other.target and
            self.operation == other.operation
        )
    
    def is_read(self) -> bool:
        """Check if this is a read operation."""
        return OperationType.is_read_operation(self.operation)
    
    def is_write(self) -> bool:
        """Check if this is a write operation."""
        return OperationType.is_write_operation(self.operation)
    
    def is_update(self) -> bool:
        """Check if this is an update operation."""
        return OperationType.is_update_operation(self.operation)
    
    def is_delete(self) -> bool:
        """Check if this is a delete operation."""
        return OperationType.is_delete_operation(self.operation)


@dataclass
class DataLineage:
    """Represents data lineage for a specific data artifact."""
    
    artifact: str  # Dataset, table, or file name
    artifact_type: str  # DATASET, SQL_TABLE, CICS_FILE
    
    # Programs that interact with this artifact
    readers: Set[str] = field(default_factory=set)
    writers: Set[str] = field(default_factory=set)
    updaters: Set[str] = field(default_factory=set)
    deleters: Set[str] = field(default_factory=set)
    
    # All operations on this artifact
    operations: List[DataOperation] = field(default_factory=list)
    
    def add_operation(self, operation: DataOperation) -> None:
        """Add an operation to the lineage."""
        if operation.target != self.artifact:
            raise ValueError(f"Operation target {operation.target} doesn't match artifact {self.artifact}")
        
        self.operations.append(operation)
        
        # Update reader/writer sets
        if operation.is_read():
            self.readers.add(operation.program)
        elif operation.is_write():
            self.writers.add(operation.program)
        elif operation.is_update():
            self.updaters.add(operation.program)
        elif operation.is_delete():
            self.deleters.add(operation.program)
    
    def get_all_programs(self) -> Set[str]:
        """Get all programs that interact with this artifact."""
        return self.readers | self.writers | self.updaters | self.deleters
    
    def is_source(self) -> bool:
        """Check if this artifact is a data source (read-only)."""
        return len(self.readers) > 0 and len(self.writers) == 0 and len(self.updaters) == 0
    
    def is_sink(self) -> bool:
        """Check if this artifact is a data sink (write-only)."""
        return len(self.writers) > 0 and len(self.readers) == 0 and len(self.updaters) == 0
    
    def is_intermediate(self) -> bool:
        """Check if this artifact is intermediate (read and written)."""
        return (len(self.readers) > 0 or len(self.updaters) > 0) and len(self.writers) > 0
    
    def __str__(self) -> str:
        """String representation."""
        role = "source" if self.is_source() else "sink" if self.is_sink() else "intermediate"
        return f"{self.artifact} ({role}): R={len(self.readers)}, W={len(self.writers)}, U={len(self.updaters)}"


@dataclass
class ExtendedProgramFlow:
    """Extended program flow with data operations tracking."""
    
    start_program: str
    programs: List[str]
    program_calls: List[tuple]  # (caller, callee, call_type)
    data_operations: List[DataOperation]
    
    # Aggregated views (computed)
    data_sources: Set[str] = field(default_factory=set)
    data_sinks: Set[str] = field(default_factory=set)
    data_intermediate: Set[str] = field(default_factory=set)
    
    # Lineage tracking
    lineage_map: dict = field(default_factory=dict)  # artifact -> DataLineage
    
    def __post_init__(self):
        """Calculate aggregated views and lineage."""
        self._build_lineage()
        self._categorize_data()
    
    def _build_lineage(self) -> None:
        """Build lineage map from operations."""
        for op in self.data_operations:
            if op.target not in self.lineage_map:
                self.lineage_map[op.target] = DataLineage(
                    artifact=op.target,
                    artifact_type=op.target_type
                )
            self.lineage_map[op.target].add_operation(op)
    
    def _categorize_data(self) -> None:
        """Categorize data artifacts as sources, sinks, or intermediate."""
        for artifact, lineage in self.lineage_map.items():
            if lineage.is_source():
                self.data_sources.add(artifact)
            elif lineage.is_sink():
                self.data_sinks.add(artifact)
            elif lineage.is_intermediate():
                self.data_intermediate.add(artifact)
    
    def get_operations_by_program(self, program: str) -> List[DataOperation]:
        """Get all data operations for a specific program."""
        return [op for op in self.data_operations if op.program == program]
    
    def get_operations_by_target(self, target: str) -> List[DataOperation]:
        """Get all operations on a specific data target."""
        return [op for op in self.data_operations if op.target == target]
    
    def get_lineage(self, artifact: str) -> Optional[DataLineage]:
        """Get lineage for a specific artifact."""
        return self.lineage_map.get(artifact)
    
    def get_data_sources_for_program(self, program: str) -> Set[str]:
        """Get all data sources read by a program."""
        ops = self.get_operations_by_program(program)
        return {op.target for op in ops if op.is_read()}
    
    def get_data_sinks_for_program(self, program: str) -> Set[str]:
        """Get all data sinks written by a program."""
        ops = self.get_operations_by_program(program)
        return {op.target for op in ops if op.is_write()}
    
    def get_impact_analysis(self, artifact: str) -> dict:
        """Get impact analysis for changing an artifact."""
        lineage = self.get_lineage(artifact)
        if not lineage:
            return {'artifact': artifact, 'impact': 'none', 'programs': []}
        
        return {
            'artifact': artifact,
            'type': lineage.artifact_type,
            'role': 'source' if lineage.is_source() else 'sink' if lineage.is_sink() else 'intermediate',
            'programs_affected': list(lineage.get_all_programs()),
            'readers': list(lineage.readers),
            'writers': list(lineage.writers),
            'updaters': list(lineage.updaters),
            'total_operations': len(lineage.operations)
        }
    
    def trace_data_flow(self, source_artifact: str) -> List[str]:
        """Trace data flow from a source through programs to sinks."""
        flow_path = [source_artifact]
        
        lineage = self.get_lineage(source_artifact)
        if not lineage:
            return flow_path
        
        # Get programs that read this source
        for program in lineage.readers:
            flow_path.append(program)
            
            # Get what this program writes
            sinks = self.get_data_sinks_for_program(program)
            flow_path.extend(sinks)
        
        return flow_path
