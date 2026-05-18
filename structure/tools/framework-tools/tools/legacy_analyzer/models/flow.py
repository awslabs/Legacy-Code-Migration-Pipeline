"""Data models for program flow analysis."""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from .dependency import Dependency, CircularDependency


@dataclass
class ProgramFlow:
    """Represents the execution flow starting from a program."""
    
    start_program: str
    depth: int  # Maximum depth of the call hierarchy
    programs: List[str]  # All programs in the flow
    dependencies: List[Dependency]  # All dependencies in the flow
    circular_dependencies: List[CircularDependency] = field(default_factory=list)
    
    # Metadata
    total_programs: int = 0
    total_copybooks: int = 0
    total_datasets: int = 0
    
    def __post_init__(self):
        """Calculate totals after initialization."""
        if self.total_programs == 0:
            self.total_programs = len(self.programs)
        
        # Count unique copybooks and datasets from dependencies
        copybooks = set()
        datasets = set()
        
        for dep in self.dependencies:
            if dep.target_type == 'COPYBOOK':
                copybooks.add(dep.target_artifact)
            elif dep.target_type == 'DATASET':
                datasets.add(dep.target_artifact)
        
        if self.total_copybooks == 0:
            self.total_copybooks = len(copybooks)
        if self.total_datasets == 0:
            self.total_datasets = len(datasets)
    
    def get_programs_at_depth(self, depth: int) -> List[str]:
        """Get all programs at a specific depth level."""
        # This would need to be calculated during flow analysis
        # For now, return empty list
        return []
    
    def has_circular_dependencies(self) -> bool:
        """Check if flow has circular dependencies."""
        return len(self.circular_dependencies) > 0


@dataclass
class CallGraph:
    """Represents a call graph for multiple programs."""
    
    nodes: List[str]  # Program names
    edges: List[Tuple[str, str]]  # (caller, callee) pairs
    metadata: Dict[str, Dict] = field(default_factory=dict)  # Additional info per node
    
    def add_node(self, program: str, **kwargs) -> None:
        """Add a node to the graph."""
        if program not in self.nodes:
            self.nodes.append(program)
        if kwargs:
            self.metadata[program] = kwargs
    
    def add_edge(self, caller: str, callee: str) -> None:
        """Add an edge to the graph."""
        edge = (caller, callee)
        if edge not in self.edges:
            self.edges.append(edge)
    
    def get_callers(self, program: str) -> List[str]:
        """Get all programs that call this program."""
        return [caller for caller, callee in self.edges if callee == program]
    
    def get_callees(self, program: str) -> List[str]:
        """Get all programs called by this program."""
        return [callee for caller, callee in self.edges if caller == program]
    
    def get_node_metadata(self, program: str) -> Dict:
        """Get metadata for a node."""
        return self.metadata.get(program, {})
    
    def to_dict(self) -> Dict:
        """Convert call graph to dictionary for serialization with program-to-file mapping."""
        return {
            'nodes': self.nodes,
            'edges': [{'caller': c, 'callee': ce} for c, ce in self.edges],
            'metadata': self.metadata,
            'program_to_file_mapping': self._extract_program_to_file_mapping()
        }
    
    def _extract_program_to_file_mapping(self) -> Dict[str, str]:
        """Extract program-to-file mapping from node metadata."""
        mapping = {}
        for program, metadata in self.metadata.items():
            file_path = metadata.get('file_path')
            if file_path:
                mapping[program] = file_path
        return mapping


@dataclass
class FlowNode:
    """Represents a node in a program flow."""
    
    program_name: str
    depth: int
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    
    # Dependencies at this node
    copybooks: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    
    def add_child(self, child: str) -> None:
        """Add a child node."""
        if child not in self.children:
            self.children.append(child)
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.program_name} (depth={self.depth})"


@dataclass
class EntryPoint:
    """Represents an entry point into the application.
    
    Entry points can be detected from multiple sources:
    - ONLINE: CICS transactions (from CSD metadata)
    - BATCH: JCL jobs (from JCL dependencies)
    - INFERRED: Programs not called by others (from code analysis)
    """
    
    program_name: str
    entry_type: str  # ONLINE, BATCH, INFERRED
    confidence: str  # EXPLICIT (from metadata), INFERRED (from code analysis)
    source: str      # CSD, JCL, CODE_ANALYSIS
    
    # ONLINE specific (CICS transactions)
    transaction_id: Optional[str] = None
    cics_group: Optional[str] = None
    mapset_name: Optional[str] = None
    
    # BATCH specific (JCL jobs)
    jcl_name: Optional[str] = None
    job_name: Optional[str] = None
    
    # Common metadata
    status: Optional[str] = None  # ENABLED, DISABLED
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert entry point to dictionary for JSON serialization."""
        result = {
            'program_name': self.program_name,
            'entry_type': self.entry_type,
            'confidence': self.confidence,
            'source': self.source,
        }
        
        # Add optional fields if present
        if self.transaction_id:
            result['transaction_id'] = self.transaction_id
        if self.cics_group:
            result['cics_group'] = self.cics_group
        if self.mapset_name:
            result['mapset_name'] = self.mapset_name
        if self.jcl_name:
            result['jcl_name'] = self.jcl_name
        if self.job_name:
            result['job_name'] = self.job_name
        if self.status:
            result['status'] = self.status
        if self.description:
            result['description'] = self.description
        
        return result
    
    def is_explicit(self) -> bool:
        """Check if this is an explicit entry point (from metadata)."""
        return self.confidence == 'EXPLICIT'
    
    def is_inferred(self) -> bool:
        """Check if this is an inferred entry point (from code analysis)."""
        return self.confidence == 'INFERRED'
    
    def is_enabled(self) -> bool:
        """Check if this entry point is enabled."""
        return self.status == 'ENABLED' if self.status else True
    
    def __str__(self) -> str:
        """String representation."""
        parts = [f"{self.program_name} ({self.entry_type})"]
        if self.transaction_id:
            parts.append(f"TRAN={self.transaction_id}")
        if self.jcl_name:
            parts.append(f"JCL={self.jcl_name}")
        return " ".join(parts)


@dataclass
class ServiceCandidate:
    """Represents a candidate microservice identified from legacy system analysis.
    
    Service candidates are groups of entry points and programs that should be
    considered for consolidation into a single microservice during modernization.
    """
    
    name: str  # Suggested service name
    entry_points: List[EntryPoint]  # Entry points in this service
    grouping_reason: str  # Why these were grouped (CICS_GROUP, DATA_OWNERSHIP, SHARED_PROGRAMS)
    confidence: str  # Confidence level (HIGH, MEDIUM, LOW)
    
    # Shared resources
    shared_data: List[str] = field(default_factory=list)  # Shared datasets/files
    shared_programs: List[str] = field(default_factory=list)  # Shared subprograms
    
    # Complexity metrics
    total_complexity: float = 0.0  # Sum of complexity scores
    total_programs: int = 0  # Total programs in service
    total_transactions: int = 0  # Total CICS transactions
    
    # Additional metadata
    cics_group: Optional[str] = None  # CICS group if grouped by CICS_GROUP
    recommendation: Optional[str] = None  # CONSIDER_MERGE, SPLIT, etc.
    
    def __post_init__(self):
        """Calculate totals after initialization."""
        if self.total_programs == 0:
            # Count unique programs from entry points
            programs = set()
            for ep in self.entry_points:
                programs.add(ep.program_name)
            self.total_programs = len(programs)
        
        if self.total_transactions == 0:
            # Count ONLINE entry points
            self.total_transactions = sum(
                1 for ep in self.entry_points if ep.entry_type == 'ONLINE'
            )
    
    def to_dict(self) -> Dict:
        """Convert service candidate to dictionary for JSON serialization."""
        result = {
            'name': self.name,
            'entry_points': [ep.to_dict() for ep in self.entry_points],
            'grouping_reason': self.grouping_reason,
            'confidence': self.confidence,
            'shared_data': self.shared_data,
            'shared_programs': self.shared_programs,
            'total_complexity': self.total_complexity,
            'total_programs': self.total_programs,
            'total_transactions': self.total_transactions,
        }
        
        # Add optional fields if present
        if self.cics_group:
            result['cics_group'] = self.cics_group
        if self.recommendation:
            result['recommendation'] = self.recommendation
        
        return result
    
    def get_program_names(self) -> List[str]:
        """Get list of all program names in this service candidate."""
        return [ep.program_name for ep in self.entry_points]
    
    def get_transaction_ids(self) -> List[str]:
        """Get list of all transaction IDs in this service candidate."""
        return [
            ep.transaction_id for ep in self.entry_points 
            if ep.transaction_id
        ]
    
    def has_high_confidence(self) -> bool:
        """Check if this is a high confidence service candidate."""
        return self.confidence == 'HIGH'
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} ({self.total_programs} programs, {self.total_transactions} transactions)"
