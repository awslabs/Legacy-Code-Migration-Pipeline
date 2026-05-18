"""Data flow analyzer for tracking data operations and lineage."""

from typing import List, Dict, Set, Optional
from ..models.dependency import Dependency, DependencyType
from ..models.data_operation import DataOperation, DataLineage, ExtendedProgramFlow, OperationType
from .flow_analyzer import FlowAnalyzer


class DataFlowAnalyzer:
    """Analyzes data flow and operations in program flows."""
    
    def __init__(self, dependencies: List[Dependency]):
        """
        Initialize data flow analyzer.
        
        Args:
            dependencies: List of all dependencies (including data operations)
        """
        self.dependencies = dependencies
        self.flow_analyzer = FlowAnalyzer(dependencies)
        self._data_operations = self._extract_data_operations()
    
    def _extract_data_operations(self) -> List[DataOperation]:
        """
        Extract data operations from dependencies.
        
        Returns:
            List of DataOperation objects
        """
        operations = []
        
        for dep in self.dependencies:
            # Check if this is a data dependency
            if dep.target_type in {'DATASET', 'SQL_TABLE', 'CICS_FILE'}:
                # Infer operation type from dependency type and notes
                operation = self._infer_operation_type(dep)
                
                if operation:
                    data_op = DataOperation(
                        program=dep.source_artifact,
                        target=dep.target_artifact,
                        target_type=dep.target_type,
                        operation=operation,
                        line_number=dep.line_number,
                        source_file=dep.source_file,
                        notes=dep.notes
                    )
                    operations.append(data_op)
        
        return operations
    
    def _infer_operation_type(self, dep: Dependency) -> Optional[str]:
        """
        Infer operation type from dependency.
        
        Args:
            dep: Dependency object
            
        Returns:
            Operation type string or None
        """
        # Check notes for operation hints
        if dep.notes:
            notes_lower = dep.notes.lower()
            if 'read' in notes_lower or 'input' in notes_lower or 'select' in notes_lower:
                return OperationType.READ.value if dep.target_type == 'DATASET' else OperationType.SELECT.value
            elif 'write' in notes_lower or 'output' in notes_lower or 'insert' in notes_lower:
                return OperationType.WRITE.value if dep.target_type == 'DATASET' else OperationType.INSERT.value
            elif 'update' in notes_lower or 'rewrite' in notes_lower:
                return OperationType.UPDATE.value if dep.target_type == 'DATASET' else OperationType.SQL_UPDATE.value
            elif 'delete' in notes_lower:
                return OperationType.DELETE.value if dep.target_type == 'DATASET' else OperationType.SQL_DELETE.value
        
        # Default based on dependency type
        if dep.dependency_type == DependencyType.DATASET_REF:
            return OperationType.READ.value  # Default to read
        elif dep.dependency_type == DependencyType.SQL_TABLE:
            return OperationType.SELECT.value  # Default to select
        elif dep.dependency_type == DependencyType.CICS_FILE:
            return OperationType.CICS_READ.value  # Default to CICS read
        
        return None
    
    def analyze_extended_flow(
        self,
        start_program: str,
        max_depth: int = 10
    ) -> ExtendedProgramFlow:
        """
        Analyze extended program flow with data operations.
        
        Args:
            start_program: Program to start analysis from
            max_depth: Maximum depth to traverse
            
        Returns:
            ExtendedProgramFlow object
        """
        # Get basic program flow
        basic_flow = self.flow_analyzer.analyze_flow(start_program, max_depth)
        
        # Extract program calls
        program_calls = []
        for dep in basic_flow.dependencies:
            if dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.EXEC_PGM
            }:
                program_calls.append((
                    dep.source_artifact,
                    dep.target_artifact,
                    dep.dependency_type
                ))
        
        # Filter data operations to only those in the flow
        flow_programs = set(basic_flow.programs)
        flow_operations = [
            op for op in self._data_operations
            if op.program in flow_programs
        ]
        
        # Create extended flow
        extended_flow = ExtendedProgramFlow(
            start_program=start_program,
            programs=basic_flow.programs,
            program_calls=program_calls,
            data_operations=flow_operations
        )
        
        return extended_flow
    
    def build_lineage(self, artifact: str) -> Optional[DataLineage]:
        """
        Build lineage for a specific data artifact.
        
        Args:
            artifact: Artifact name (dataset, table, file)
            
        Returns:
            DataLineage object or None if not found
        """
        # Find all operations on this artifact
        artifact_ops = [
            op for op in self._data_operations
            if op.target == artifact
        ]
        
        if not artifact_ops:
            return None
        
        # Create lineage
        lineage = DataLineage(
            artifact=artifact,
            artifact_type=artifact_ops[0].target_type
        )
        
        for op in artifact_ops:
            lineage.add_operation(op)
        
        return lineage
    
    def get_all_data_artifacts(self) -> Set[str]:
        """
        Get all data artifacts in the system.
        
        Returns:
            Set of artifact names
        """
        return {op.target for op in self._data_operations}
    
    def get_data_sources(self) -> Set[str]:
        """
        Get all data sources (read-only artifacts).
        
        Returns:
            Set of source artifact names
        """
        sources = set()
        
        for artifact in self.get_all_data_artifacts():
            lineage = self.build_lineage(artifact)
            if lineage and lineage.is_source():
                sources.add(artifact)
        
        return sources
    
    def get_data_sinks(self) -> Set[str]:
        """
        Get all data sinks (write-only artifacts).
        
        Returns:
            Set of sink artifact names
        """
        sinks = set()
        
        for artifact in self.get_all_data_artifacts():
            lineage = self.build_lineage(artifact)
            if lineage and lineage.is_sink():
                sinks.add(artifact)
        
        return sinks
    
    def get_intermediate_data(self) -> Set[str]:
        """
        Get all intermediate data (read and written).
        
        Returns:
            Set of intermediate artifact names
        """
        intermediate = set()
        
        for artifact in self.get_all_data_artifacts():
            lineage = self.build_lineage(artifact)
            if lineage and lineage.is_intermediate():
                intermediate.add(artifact)
        
        return intermediate
    
    def get_impact_analysis(self, artifact: str) -> Dict:
        """
        Analyze impact of changing a data artifact.
        
        Args:
            artifact: Artifact name
            
        Returns:
            Dictionary with impact analysis
        """
        lineage = self.build_lineage(artifact)
        
        if not lineage:
            return {
                'artifact': artifact,
                'found': False,
                'impact': 'none'
            }
        
        # Get all programs affected
        affected_programs = lineage.get_all_programs()
        
        # For each affected program, get its flow
        downstream_programs = set()
        for program in affected_programs:
            try:
                flow = self.flow_analyzer.analyze_flow(program, max_depth=5)
                downstream_programs.update(flow.programs)
            except:
                pass
        
        return {
            'artifact': artifact,
            'found': True,
            'type': lineage.artifact_type,
            'role': 'source' if lineage.is_source() else 'sink' if lineage.is_sink() else 'intermediate',
            'direct_programs': list(affected_programs),
            'downstream_programs': list(downstream_programs - affected_programs),
            'total_affected': len(downstream_programs),
            'operations': {
                'reads': len(lineage.readers),
                'writes': len(lineage.writers),
                'updates': len(lineage.updaters),
                'deletes': len(lineage.deleters)
            }
        }
    
    def trace_data_lineage(
        self,
        source_artifact: str,
        max_hops: int = 5
    ) -> List[Dict]:
        """
        Trace data lineage from source through programs to sinks.
        
        Args:
            source_artifact: Starting artifact
            max_hops: Maximum number of hops to trace
            
        Returns:
            List of lineage steps
        """
        lineage_path = []
        visited = set()
        
        def trace_recursive(artifact: str, hop: int):
            if hop >= max_hops or artifact in visited:
                return
            
            visited.add(artifact)
            
            # Get lineage for this artifact
            lineage = self.build_lineage(artifact)
            if not lineage:
                return
            
            # Add this step
            step = {
                'hop': hop,
                'artifact': artifact,
                'type': lineage.artifact_type,
                'readers': list(lineage.readers),
                'writers': list(lineage.writers)
            }
            lineage_path.append(step)
            
            # Trace through programs that read this artifact
            for program in lineage.readers:
                # Find what this program writes
                program_ops = [op for op in self._data_operations if op.program == program]
                for op in program_ops:
                    if op.is_write() and op.target not in visited:
                        trace_recursive(op.target, hop + 1)
        
        trace_recursive(source_artifact, 0)
        return lineage_path
    
    def get_data_flow_statistics(self) -> Dict:
        """
        Get statistics about data flow in the system.
        
        Returns:
            Dictionary with statistics
        """
        all_artifacts = self.get_all_data_artifacts()
        sources = self.get_data_sources()
        sinks = self.get_data_sinks()
        intermediate = self.get_intermediate_data()
        
        # Count operations by type
        read_ops = sum(1 for op in self._data_operations if op.is_read())
        write_ops = sum(1 for op in self._data_operations if op.is_write())
        update_ops = sum(1 for op in self._data_operations if op.is_update())
        delete_ops = sum(1 for op in self._data_operations if op.is_delete())
        
        # Count by artifact type
        datasets = sum(1 for op in self._data_operations if op.target_type == 'DATASET')
        sql_tables = sum(1 for op in self._data_operations if op.target_type == 'SQL_TABLE')
        cics_files = sum(1 for op in self._data_operations if op.target_type == 'CICS_FILE')
        
        return {
            'total_artifacts': len(all_artifacts),
            'data_sources': len(sources),
            'data_sinks': len(sinks),
            'intermediate_data': len(intermediate),
            'total_operations': len(self._data_operations),
            'operations_by_type': {
                'read': read_ops,
                'write': write_ops,
                'update': update_ops,
                'delete': delete_ops
            },
            'artifacts_by_type': {
                'datasets': datasets,
                'sql_tables': sql_tables,
                'cics_files': cics_files
            }
        }
