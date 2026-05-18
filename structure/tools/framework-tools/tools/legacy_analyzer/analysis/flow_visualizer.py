"""Flow visualization export formats (DOT, Mermaid, JSON)."""

import json
from typing import Dict, List, Set, Optional
from ..models.flow import ProgramFlow, CallGraph
from ..models.dependency import Dependency, CircularDependency, DependencyType


class FlowVisualizer:
    """Export program flows in various visualization formats."""
    
    def __init__(self, flow: ProgramFlow, dependencies: List[Dependency]):
        """
        Initialize flow visualizer.
        
        Args:
            flow: ProgramFlow object to visualize
            dependencies: All dependencies (for copybooks and datasets)
        """
        self.flow = flow
        self.dependencies = dependencies
        self._copybook_deps = self._extract_copybook_deps()
        self._dataset_deps = self._extract_dataset_deps()
    
    def _extract_copybook_deps(self) -> Dict[str, Set[str]]:
        """Extract copybook dependencies for programs in flow."""
        copybooks = {}
        
        for dep in self.dependencies:
            if (dep.source_artifact in self.flow.programs and
                dep.dependency_type in {DependencyType.COPY, DependencyType.INCLUDE} and
                dep.target_type == 'COPYBOOK'):
                if dep.source_artifact not in copybooks:
                    copybooks[dep.source_artifact] = set()
                copybooks[dep.source_artifact].add(dep.target_artifact)
        
        return copybooks
    
    def _extract_dataset_deps(self) -> Dict[str, Set[str]]:
        """Extract dataset dependencies for programs in flow."""
        datasets = {}
        
        for dep in self.dependencies:
            if (dep.source_artifact in self.flow.programs and
                dep.dependency_type == DependencyType.DATASET_REF and
                dep.target_type == 'DATASET'):
                if dep.source_artifact not in datasets:
                    datasets[dep.source_artifact] = set()
                datasets[dep.source_artifact].add(dep.target_artifact)
        
        return datasets
    
    def to_dot(self, include_copybooks: bool = True, include_datasets: bool = True) -> str:
        """
        Export flow as DOT format for Graphviz.
        
        Args:
            include_copybooks: Include copybook dependencies
            include_datasets: Include dataset dependencies
            
        Returns:
            DOT format string
        """
        lines = ['digraph ProgramFlow {']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box];')
        lines.append('')
        
        # Add program nodes
        lines.append('    // Programs')
        for program in self.flow.programs:
            # Check if program is in a circular dependency
            is_circular = any(
                program in cycle.artifacts
                for cycle in self.flow.circular_dependencies
            )
            
            if is_circular:
                lines.append(f'    "{program}" [style=filled, fillcolor=orange];')
            elif program == self.flow.start_program:
                lines.append(f'    "{program}" [style=filled, fillcolor=lightblue];')
            else:
                lines.append(f'    "{program}";')
        
        lines.append('')
        
        # Add copybook nodes if requested
        if include_copybooks:
            all_copybooks = set()
            for copybooks in self._copybook_deps.values():
                all_copybooks.update(copybooks)
            
            if all_copybooks:
                lines.append('    // Copybooks')
                for copybook in sorted(all_copybooks):
                    lines.append(f'    "{copybook}" [shape=note, style=filled, fillcolor=lightyellow];')
                lines.append('')
        
        # Add dataset nodes if requested
        if include_datasets:
            all_datasets = set()
            for datasets in self._dataset_deps.values():
                all_datasets.update(datasets)
            
            if all_datasets:
                lines.append('    // Datasets')
                for dataset in sorted(all_datasets):
                    lines.append(f'    "{dataset}" [shape=cylinder, style=filled, fillcolor=lightgreen];')
                lines.append('')
        
        # Add program call edges
        lines.append('    // Program calls')
        for dep in self.flow.dependencies:
            if (dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM
            } and dep.target_type == 'PROGRAM'):
                label = dep.dependency_type
                lines.append(f'    "{dep.source_artifact}" -> "{dep.target_artifact}" [label="{label}"];')
        
        lines.append('')
        
        # Add copybook edges if requested
        if include_copybooks:
            lines.append('    // Copybook includes')
            for program, copybooks in self._copybook_deps.items():
                for copybook in copybooks:
                    lines.append(f'    "{program}" -> "{copybook}" [style=dashed, color=gray];')
            lines.append('')
        
        # Add dataset edges if requested
        if include_datasets:
            lines.append('    // Dataset references')
            for program, datasets in self._dataset_deps.items():
                for dataset in datasets:
                    lines.append(f'    "{program}" -> "{dataset}" [style=dotted, color=green];')
            lines.append('')
        
        # Add circular dependency annotations
        if self.flow.circular_dependencies:
            lines.append('    // Circular dependencies')
            for i, cycle in enumerate(self.flow.circular_dependencies):
                cycle_label = f"Cycle {i+1}: {' -> '.join(cycle.artifacts)}"
                lines.append(f'    // {cycle_label}')
            lines.append('')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def to_mermaid(self, include_copybooks: bool = True, include_datasets: bool = True) -> str:
        """
        Export flow as Mermaid diagram format.
        
        Args:
            include_copybooks: Include copybook dependencies
            include_datasets: Include dataset dependencies
            
        Returns:
            Mermaid format string
        """
        lines = ['graph TD']
        lines.append('')
        
        # Add program nodes
        lines.append('    %% Programs')
        for program in self.flow.programs:
            # Check if program is in a circular dependency
            is_circular = any(
                program in cycle.artifacts
                for cycle in self.flow.circular_dependencies
            )
            
            safe_id = program.replace('-', '_').replace('.', '_')
            
            if is_circular:
                lines.append(f'    {safe_id}["{program}"]:::circular')
            elif program == self.flow.start_program:
                lines.append(f'    {safe_id}["{program}"]:::start')
            else:
                lines.append(f'    {safe_id}["{program}"]')
        
        lines.append('')
        
        # Add copybook nodes if requested
        if include_copybooks:
            all_copybooks = set()
            for copybooks in self._copybook_deps.values():
                all_copybooks.update(copybooks)
            
            if all_copybooks:
                lines.append('    %% Copybooks')
                for copybook in sorted(all_copybooks):
                    safe_id = copybook.replace('-', '_').replace('.', '_')
                    lines.append(f'    {safe_id}["{copybook}"]:::copybook')
                lines.append('')
        
        # Add dataset nodes if requested
        if include_datasets:
            all_datasets = set()
            for datasets in self._dataset_deps.values():
                all_datasets.update(datasets)
            
            if all_datasets:
                lines.append('    %% Datasets')
                for dataset in sorted(all_datasets):
                    safe_id = dataset.replace('-', '_').replace('.', '_')
                    lines.append(f'    {safe_id}[("{dataset}")]:::dataset')
                lines.append('')
        
        # Add program call edges
        lines.append('    %% Program calls')
        for dep in self.flow.dependencies:
            if (dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM
            } and dep.target_type == 'PROGRAM'):
                source_id = dep.source_artifact.replace('-', '_').replace('.', '_')
                target_id = dep.target_artifact.replace('-', '_').replace('.', '_')
                label = dep.dependency_type
                lines.append(f'    {source_id} -->|{label}| {target_id}')
        
        lines.append('')
        
        # Add copybook edges if requested
        if include_copybooks:
            lines.append('    %% Copybook includes')
            for program, copybooks in self._copybook_deps.items():
                program_id = program.replace('-', '_').replace('.', '_')
                for copybook in copybooks:
                    copybook_id = copybook.replace('-', '_').replace('.', '_')
                    lines.append(f'    {program_id} -.->|COPY| {copybook_id}')
            lines.append('')
        
        # Add dataset edges if requested
        if include_datasets:
            lines.append('    %% Dataset references')
            for program, datasets in self._dataset_deps.items():
                program_id = program.replace('-', '_').replace('.', '_')
                for dataset in datasets:
                    dataset_id = dataset.replace('-', '_').replace('.', '_')
                    lines.append(f'    {program_id} -.->|REF| {dataset_id}')
            lines.append('')
        
        # Add style definitions
        lines.append('    %% Styles')
        lines.append('    classDef start fill:#add8e6,stroke:#333,stroke-width:2px')
        lines.append('    classDef circular fill:#ffa500,stroke:#333,stroke-width:2px')
        lines.append('    classDef copybook fill:#ffffe0,stroke:#333,stroke-width:1px')
        lines.append('    classDef dataset fill:#90ee90,stroke:#333,stroke-width:1px')
        
        return '\n'.join(lines)
    
    def to_json(self, include_copybooks: bool = True, include_datasets: bool = True) -> str:
        """
        Export flow as JSON format.
        
        Args:
            include_copybooks: Include copybook dependencies
            include_datasets: Include dataset dependencies
            
        Returns:
            JSON format string
        """
        data = {
            'start_program': self.flow.start_program,
            'depth': self.flow.depth,
            'total_programs': self.flow.total_programs,
            'total_copybooks': self.flow.total_copybooks,
            'total_datasets': self.flow.total_datasets,
            'programs': self.flow.programs,
            'dependencies': {
                'program_calls': [],
                'copybook_includes': [] if include_copybooks else None,
                'dataset_references': [] if include_datasets else None
            },
            'circular_dependencies': [
                {
                    'artifacts': cycle.artifacts,
                    'dependency_types': cycle.dependency_types
                }
                for cycle in self.flow.circular_dependencies
            ]
        }
        
        # Add program call dependencies
        for dep in self.flow.dependencies:
            if (dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM
            } and dep.target_type == 'PROGRAM'):
                data['dependencies']['program_calls'].append({
                    'source': dep.source_artifact,
                    'target': dep.target_artifact,
                    'type': dep.dependency_type
                })
        
        # Add copybook dependencies if requested
        if include_copybooks:
            for program, copybooks in self._copybook_deps.items():
                for copybook in copybooks:
                    data['dependencies']['copybook_includes'].append({
                        'program': program,
                        'copybook': copybook
                    })
        
        # Add dataset dependencies if requested
        if include_datasets:
            for program, datasets in self._dataset_deps.items():
                for dataset in datasets:
                    data['dependencies']['dataset_references'].append({
                        'program': program,
                        'dataset': dataset
                    })
        
        return json.dumps(data, indent=2)


class CallGraphVisualizer:
    """Export call graphs in various visualization formats."""
    
    def __init__(self, call_graph: CallGraph):
        """
        Initialize call graph visualizer.
        
        Args:
            call_graph: CallGraph object to visualize
        """
        self.call_graph = call_graph
    
    def to_dot(self) -> str:
        """
        Export call graph as DOT format for Graphviz.
        
        Returns:
            DOT format string
        """
        lines = ['digraph CallGraph {']
        lines.append('    rankdir=LR;')
        lines.append('    node [shape=box];')
        lines.append('')
        
        # Add nodes
        lines.append('    // Nodes')
        for node in self.call_graph.nodes:
            metadata = self.call_graph.get_node_metadata(node)
            if metadata:
                # Add metadata as label
                label_parts = [node]
                if 'complexity' in metadata:
                    label_parts.append(f"Complexity: {metadata['complexity']}")
                if 'loc' in metadata:
                    label_parts.append(f"LOC: {metadata['loc']}")
                label = '\\n'.join(label_parts)
                lines.append(f'    "{node}" [label="{label}"];')
            else:
                lines.append(f'    "{node}";')
        
        lines.append('')
        
        # Add edges
        lines.append('    // Edges')
        for caller, callee in self.call_graph.edges:
            lines.append(f'    "{caller}" -> "{callee}";')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def to_mermaid(self) -> str:
        """
        Export call graph as Mermaid diagram format.
        
        Returns:
            Mermaid format string
        """
        lines = ['graph LR']
        lines.append('')
        
        # Add nodes
        lines.append('    %% Nodes')
        for node in self.call_graph.nodes:
            safe_id = node.replace('-', '_').replace('.', '_')
            lines.append(f'    {safe_id}["{node}"]')
        
        lines.append('')
        
        # Add edges
        lines.append('    %% Edges')
        for caller, callee in self.call_graph.edges:
            caller_id = caller.replace('-', '_').replace('.', '_')
            callee_id = callee.replace('-', '_').replace('.', '_')
            lines.append(f'    {caller_id} --> {callee_id}')
        
        return '\n'.join(lines)
    
    def to_json(self) -> str:
        """
        Export call graph as JSON format.
        
        Returns:
            JSON format string
        """
        return json.dumps(self.call_graph.to_dict(), indent=2)
