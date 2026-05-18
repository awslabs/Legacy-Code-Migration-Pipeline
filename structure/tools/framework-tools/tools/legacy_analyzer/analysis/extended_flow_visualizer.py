"""Extended flow visualization with data operations."""

import json
from typing import Optional
from ..models.data_operation import ExtendedProgramFlow, DataLineage


class ExtendedFlowVisualizer:
    """Visualizer for extended flows with data operations."""
    
    def __init__(self, flow: ExtendedProgramFlow):
        """
        Initialize extended flow visualizer.
        
        Args:
            flow: ExtendedProgramFlow object to visualize
        """
        self.flow = flow
    
    def to_mermaid(
        self,
        show_operations: bool = True,
        show_operation_labels: bool = True
    ) -> str:
        """
        Generate Mermaid diagram with data operations.
        
        Args:
            show_operations: Include data operations in diagram
            show_operation_labels: Show operation types on edges
            
        Returns:
            Mermaid format string
        """
        lines = ['graph TD']
        lines.append('')
        
        # Programs
        lines.append('    %% Programs')
        for program in self.flow.programs:
            safe_id = self._safe_id(program)
            if program == self.flow.start_program:
                lines.append(f'    {safe_id}["{program}"]:::program_start')
            else:
                lines.append(f'    {safe_id}["{program}"]:::program')
        lines.append('')
        
        # Data sources (read-only)
        if self.flow.data_sources:
            lines.append('    %% Data Sources (Read)')
            for source in sorted(self.flow.data_sources):
                safe_id = self._safe_id(source)
                lines.append(f'    {safe_id}[("{source}")]:::data_source')
            lines.append('')
        
        # Data sinks (write-only)
        if self.flow.data_sinks:
            lines.append('    %% Data Sinks (Write)')
            for sink in sorted(self.flow.data_sinks):
                safe_id = self._safe_id(sink)
                lines.append(f'    {safe_id}[("{sink}")]:::data_sink')
            lines.append('')
        
        # Intermediate data (read/write)
        if self.flow.data_intermediate:
            lines.append('    %% Data Modified (Read/Write)')
            for modified in sorted(self.flow.data_intermediate):
                safe_id = self._safe_id(modified)
                lines.append(f'    {safe_id}[("{modified}")]:::data_modified')
            lines.append('')
        
        # Program calls
        lines.append('    %% Program Calls')
        for caller, callee, call_type in self.flow.program_calls:
            caller_id = self._safe_id(caller)
            callee_id = self._safe_id(callee)
            lines.append(f'    {caller_id} -->|{call_type}| {callee_id}')
        lines.append('')
        
        # Data operations
        if show_operations:
            lines.append('    %% Data Operations')
            for op in self.flow.data_operations:
                prog_id = self._safe_id(op.program)
                target_id = self._safe_id(op.target)
                
                label = op.operation if show_operation_labels else ''
                
                # Different arrow styles for different operations
                if op.is_read():
                    lines.append(f'    {target_id} -.->|{label}| {prog_id}')
                elif op.is_write():
                    lines.append(f'    {prog_id} -.->|{label}| {target_id}')
                elif op.is_update():
                    lines.append(f'    {prog_id} <-.->|{label}| {target_id}')
                elif op.is_delete():
                    lines.append(f'    {prog_id} -.->|{label}| {target_id}')
            lines.append('')
        
        # Styles
        lines.append('    %% Styles')
        lines.append('    classDef program_start fill:#add8e6,stroke:#333,stroke-width:3px')
        lines.append('    classDef program fill:#e6f3ff,stroke:#333,stroke-width:2px')
        lines.append('    classDef data_source fill:#90ee90,stroke:#333,stroke-width:2px')
        lines.append('    classDef data_sink fill:#ffb6c1,stroke:#333,stroke-width:2px')
        lines.append('    classDef data_modified fill:#ffd700,stroke:#333,stroke-width:2px')
        
        return '\n'.join(lines)
    
    def to_data_lineage_mermaid(self) -> str:
        """
        Generate data lineage diagram (sources -> programs -> sinks).
        
        Returns:
            Mermaid format string
        """
        lines = ['graph LR']
        lines.append('')
        
        # Data sources
        if self.flow.data_sources:
            lines.append('    %% Data Sources')
            for source in sorted(self.flow.data_sources):
                safe_id = self._safe_id(source)
                lines.append(f'    {safe_id}[("{source}")]:::source')
            lines.append('')
        
        # Processing programs
        lines.append('    %% Processing Programs')
        for program in self.flow.programs:
            safe_id = self._safe_id(program)
            lines.append(f'    {safe_id}["{program}"]:::processor')
        lines.append('')
        
        # Data sinks
        if self.flow.data_sinks:
            lines.append('    %% Data Sinks')
            for sink in sorted(self.flow.data_sinks):
                safe_id = self._safe_id(sink)
                lines.append(f'    {safe_id}[("{sink}")]:::sink')
            lines.append('')
        
        # Intermediate data
        if self.flow.data_intermediate:
            lines.append('    %% Intermediate Data')
            for intermediate in sorted(self.flow.data_intermediate):
                safe_id = self._safe_id(intermediate)
                lines.append(f'    {safe_id}[("{intermediate}")]:::intermediate')
            lines.append('')
        
        # Data flow edges
        lines.append('    %% Data Flow')
        
        # Sources to programs
        for op in self.flow.data_operations:
            if op.is_read():
                source_id = self._safe_id(op.target)
                prog_id = self._safe_id(op.program)
                lines.append(f'    {source_id} -->|{op.operation}| {prog_id}')
        
        # Programs to sinks
        for op in self.flow.data_operations:
            if op.is_write():
                prog_id = self._safe_id(op.program)
                sink_id = self._safe_id(op.target)
                lines.append(f'    {prog_id} -->|{op.operation}| {sink_id}')
        
        lines.append('')
        
        # Styles
        lines.append('    %% Styles')
        lines.append('    classDef source fill:#90ee90,stroke:#333,stroke-width:2px')
        lines.append('    classDef processor fill:#add8e6,stroke:#333,stroke-width:2px')
        lines.append('    classDef sink fill:#ffb6c1,stroke:#333,stroke-width:2px')
        lines.append('    classDef intermediate fill:#ffd700,stroke:#333,stroke-width:2px')
        
        return '\n'.join(lines)
    
    def to_dot(
        self,
        show_operations: bool = True,
        show_operation_labels: bool = True
    ) -> str:
        """
        Export extended flow as DOT format for Graphviz.
        
        Args:
            show_operations: Include data operations
            show_operation_labels: Show operation types on edges
            
        Returns:
            DOT format string
        """
        lines = ['digraph ExtendedFlow {']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box];')
        lines.append('')
        
        # Programs
        lines.append('    // Programs')
        for program in self.flow.programs:
            if program == self.flow.start_program:
                lines.append(f'    "{program}" [style=filled, fillcolor=lightblue];')
            else:
                lines.append(f'    "{program}";')
        lines.append('')
        
        # Data artifacts
        if show_operations:
            # Sources
            if self.flow.data_sources:
                lines.append('    // Data Sources')
                for source in sorted(self.flow.data_sources):
                    lines.append(f'    "{source}" [shape=cylinder, style=filled, fillcolor=lightgreen];')
                lines.append('')
            
            # Sinks
            if self.flow.data_sinks:
                lines.append('    // Data Sinks')
                for sink in sorted(self.flow.data_sinks):
                    lines.append(f'    "{sink}" [shape=cylinder, style=filled, fillcolor=pink];')
                lines.append('')
            
            # Intermediate
            if self.flow.data_intermediate:
                lines.append('    // Intermediate Data')
                for intermediate in sorted(self.flow.data_intermediate):
                    lines.append(f'    "{intermediate}" [shape=cylinder, style=filled, fillcolor=gold];')
                lines.append('')
        
        # Program calls
        lines.append('    // Program Calls')
        for caller, callee, call_type in self.flow.program_calls:
            lines.append(f'    "{caller}" -> "{callee}" [label="{call_type}"];')
        lines.append('')
        
        # Data operations
        if show_operations:
            lines.append('    // Data Operations')
            for op in self.flow.data_operations:
                label = op.operation if show_operation_labels else ''
                
                if op.is_read():
                    lines.append(f'    "{op.target}" -> "{op.program}" [label="{label}", style=dashed, color=green];')
                elif op.is_write():
                    lines.append(f'    "{op.program}" -> "{op.target}" [label="{label}", style=dashed, color=red];')
                elif op.is_update():
                    lines.append(f'    "{op.program}" -> "{op.target}" [label="{label}", style=dashed, color=orange, dir=both];')
            lines.append('')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def to_json(self, include_lineage: bool = True) -> str:
        """
        Export extended flow as JSON format.
        
        Args:
            include_lineage: Include lineage information
            
        Returns:
            JSON format string
        """
        data = {
            'start_program': self.flow.start_program,
            'programs': self.flow.programs,
            'program_calls': [
                {'caller': c, 'callee': ce, 'type': t}
                for c, ce, t in self.flow.program_calls
            ],
            'data_operations': [
                {
                    'program': op.program,
                    'target': op.target,
                    'target_type': op.target_type,
                    'operation': op.operation,
                    'access_mode': op.access_mode,
                    'line_number': op.line_number
                }
                for op in self.flow.data_operations
            ],
            'summary': {
                'total_programs': len(self.flow.programs),
                'total_operations': len(self.flow.data_operations),
                'data_sources': list(self.flow.data_sources),
                'data_sinks': list(self.flow.data_sinks),
                'intermediate_data': list(self.flow.data_intermediate)
            }
        }
        
        if include_lineage:
            data['lineage'] = {
                artifact: {
                    'type': lineage.artifact_type,
                    'readers': list(lineage.readers),
                    'writers': list(lineage.writers),
                    'updaters': list(lineage.updaters),
                    'role': 'source' if lineage.is_source() else 'sink' if lineage.is_sink() else 'intermediate'
                }
                for artifact, lineage in self.flow.lineage_map.items()
            }
        
        return json.dumps(data, indent=2)
    
    def _safe_id(self, name: str) -> str:
        """Convert name to safe Mermaid ID."""
        return name.replace('-', '_').replace('.', '_').replace(' ', '_')


class DataLineageVisualizer:
    """Visualizer for data lineage."""
    
    def __init__(self, lineage: DataLineage):
        """
        Initialize lineage visualizer.
        
        Args:
            lineage: DataLineage object to visualize
        """
        self.lineage = lineage
    
    def to_mermaid(self) -> str:
        """
        Generate Mermaid diagram for lineage.
        
        Returns:
            Mermaid format string
        """
        lines = ['graph LR']
        lines.append('')
        
        artifact_id = self._safe_id(self.lineage.artifact)
        
        # Central artifact
        lines.append(f'    {artifact_id}[("{self.lineage.artifact}")]:::artifact')
        lines.append('')
        
        # Readers
        if self.lineage.readers:
            lines.append('    %% Readers')
            for reader in sorted(self.lineage.readers):
                reader_id = self._safe_id(reader)
                lines.append(f'    {reader_id}["{reader}"]:::reader')
                lines.append(f'    {artifact_id} -->|READ| {reader_id}')
            lines.append('')
        
        # Writers
        if self.lineage.writers:
            lines.append('    %% Writers')
            for writer in sorted(self.lineage.writers):
                writer_id = self._safe_id(writer)
                lines.append(f'    {writer_id}["{writer}"]:::writer')
                lines.append(f'    {writer_id} -->|WRITE| {artifact_id}')
            lines.append('')
        
        # Updaters
        if self.lineage.updaters:
            lines.append('    %% Updaters')
            for updater in sorted(self.lineage.updaters):
                updater_id = self._safe_id(updater)
                lines.append(f'    {updater_id}["{updater}"]:::updater')
                lines.append(f'    {updater_id} <-->|UPDATE| {artifact_id}')
            lines.append('')
        
        # Styles
        lines.append('    %% Styles')
        lines.append('    classDef artifact fill:#ffd700,stroke:#333,stroke-width:3px')
        lines.append('    classDef reader fill:#90ee90,stroke:#333,stroke-width:2px')
        lines.append('    classDef writer fill:#ffb6c1,stroke:#333,stroke-width:2px')
        lines.append('    classDef updater fill:#add8e6,stroke:#333,stroke-width:2px')
        
        return '\n'.join(lines)
    
    def _safe_id(self, name: str) -> str:
        """Convert name to safe Mermaid ID."""
        return name.replace('-', '_').replace('.', '_').replace(' ', '_')
