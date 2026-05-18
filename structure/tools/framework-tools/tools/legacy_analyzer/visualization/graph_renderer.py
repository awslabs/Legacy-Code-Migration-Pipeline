"""Graph renderer for visualizing program flows and call graphs."""

from typing import Dict, List, Optional, Set
from ..models.flow import CallGraph, ProgramFlow
from ..models.complexity import ComplexityMetrics, ComplexityTier


class GraphRenderer:
    """Renders call graphs and program flows in various formats."""
    
    def __init__(
        self,
        color_by_complexity: bool = True,
        highlight_missing: bool = True,
        include_legend: bool = True
    ):
        """
        Initialize graph renderer.
        
        Args:
            color_by_complexity: Whether to color nodes by complexity level
            highlight_missing: Whether to highlight missing artifacts in red
            include_legend: Whether to include a legend in visualizations
        """
        self.color_by_complexity = color_by_complexity
        self.highlight_missing = highlight_missing
        self.include_legend = include_legend
        
        # Color scheme for complexity levels
        self.complexity_colors = {
            'LOW': '#90EE90',      # Light green
            'MEDIUM': '#FFD700',   # Gold
            'HIGH': '#FFA500',     # Orange
            'VERY_HIGH': '#FF6347' # Tomato red
        }
        
        # Color for missing artifacts
        self.missing_color = '#FF0000'  # Red
        
        # Default color
        self.default_color = '#87CEEB'  # Sky blue
    
    def render_dot(
        self,
        call_graph: CallGraph,
        complexity_data: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[Set[str]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Render call graph in DOT format for Graphviz.
        
        Args:
            call_graph: CallGraph to render
            complexity_data: Optional complexity metrics for coloring
            missing_artifacts: Optional set of missing artifact names
            title: Optional title for the graph
            
        Returns:
            DOT format string
        """
        lines = []
        
        # Graph header
        lines.append('digraph CallGraph {')
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box, style=filled];')
        
        if title:
            lines.append(f'    labelloc="t";')
            lines.append(f'    label="{title}";')
            lines.append(f'    fontsize=16;')
        
        lines.append('')
        
        # Add nodes with styling
        for node in call_graph.nodes:
            color = self._get_node_color(node, complexity_data, missing_artifacts)
            label = self._get_node_label(node, complexity_data)
            
            # Check if missing
            if missing_artifacts and node in missing_artifacts:
                lines.append(f'    "{node}" [label="{label}", fillcolor="{color}", color="red", penwidth=3];')
            else:
                lines.append(f'    "{node}" [label="{label}", fillcolor="{color}"];')
        
        lines.append('')
        
        # Add edges
        for caller, callee in call_graph.edges:
            lines.append(f'    "{caller}" -> "{callee}";')
        
        lines.append('')
        
        # Add legend if requested
        if self.include_legend and (self.color_by_complexity or self.highlight_missing):
            lines.extend(self._generate_dot_legend())
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def render_mermaid(
        self,
        call_graph: CallGraph,
        complexity_data: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[Set[str]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Render call graph in Mermaid format for markdown documentation.
        
        Args:
            call_graph: CallGraph to render
            complexity_data: Optional complexity metrics for coloring
            missing_artifacts: Optional set of missing artifact names
            title: Optional title for the graph
            
        Returns:
            Mermaid format string
        """
        lines = []
        
        # Graph header
        lines.append('```mermaid')
        lines.append('graph TD')
        
        if title:
            lines.append(f'    title["{title}"]')
            lines.append('    style title fill:#fff,stroke:#fff')
            lines.append('')
        
        # Add edges (Mermaid creates nodes automatically)
        for caller, callee in call_graph.edges:
            caller_id = self._sanitize_mermaid_id(caller)
            callee_id = self._sanitize_mermaid_id(callee)
            
            caller_label = self._get_node_label(caller, complexity_data)
            callee_label = self._get_node_label(callee, complexity_data)
            
            lines.append(f'    {caller_id}["{caller_label}"] --> {callee_id}["{callee_label}"]')
        
        lines.append('')
        
        # Add styling for nodes
        if self.color_by_complexity or self.highlight_missing:
            lines.extend(self._generate_mermaid_styles(
                call_graph.nodes,
                complexity_data,
                missing_artifacts
            ))
        
        lines.append('```')
        
        return '\n'.join(lines)
    
    def render_html(
        self,
        call_graph: CallGraph,
        complexity_data: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[Set[str]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Render interactive HTML visualization using vis.js.
        
        Args:
            call_graph: CallGraph to render
            complexity_data: Optional complexity metrics for coloring
            missing_artifacts: Optional set of missing artifact names
            title: Optional title for the graph
            
        Returns:
            HTML string with embedded JavaScript
        """
        # Build nodes data
        nodes_data = []
        for node in call_graph.nodes:
            color = self._get_node_color(node, complexity_data, missing_artifacts)
            label = self._get_node_label(node, complexity_data)
            
            node_data = {
                'id': node,
                'label': label,
                'color': color,
                'font': {'color': '#000000'}
            }
            
            # Add border for missing artifacts
            if missing_artifacts and node in missing_artifacts:
                node_data['borderWidth'] = 3
                node_data['color'] = {
                    'background': color,
                    'border': self.missing_color
                }
            
            nodes_data.append(node_data)
        
        # Build edges data
        edges_data = []
        for caller, callee in call_graph.edges:
            edges_data.append({
                'from': caller,
                'to': callee,
                'arrows': 'to'
            })
        
        # Generate HTML
        html = self._generate_html_template(
            nodes_data,
            edges_data,
            title or "Call Graph"
        )
        
        return html
    
    def render_flow_dot(
        self,
        flow: ProgramFlow,
        complexity_data: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[Set[str]] = None
    ) -> str:
        """
        Render program flow in DOT format.
        
        Args:
            flow: ProgramFlow to render
            complexity_data: Optional complexity metrics for coloring
            missing_artifacts: Optional set of missing artifact names
            
        Returns:
            DOT format string
        """
        # Build call graph from flow
        call_graph = CallGraph(nodes=flow.programs, edges=[])
        
        # Extract edges from dependencies
        for dep in flow.dependencies:
            if dep.target_type == 'PROGRAM':
                call_graph.edges.append((dep.source_artifact, dep.target_artifact))
        
        title = f"Program Flow: {flow.start_program} (Depth: {flow.depth})"
        
        return self.render_dot(call_graph, complexity_data, missing_artifacts, title)
    
    def render_flow_mermaid(
        self,
        flow: ProgramFlow,
        complexity_data: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[Set[str]] = None
    ) -> str:
        """
        Render program flow in Mermaid format.
        
        Args:
            flow: ProgramFlow to render
            complexity_data: Optional complexity metrics for coloring
            missing_artifacts: Optional set of missing artifact names
            
        Returns:
            Mermaid format string
        """
        # Build call graph from flow
        call_graph = CallGraph(nodes=flow.programs, edges=[])
        
        # Extract edges from dependencies
        for dep in flow.dependencies:
            if dep.target_type == 'PROGRAM':
                call_graph.edges.append((dep.source_artifact, dep.target_artifact))
        
        title = f"Program Flow: {flow.start_program} (Depth: {flow.depth})"
        
        return self.render_mermaid(call_graph, complexity_data, missing_artifacts, title)
    
    def _get_node_color(
        self,
        node: str,
        complexity_data: Optional[Dict[str, ComplexityMetrics]],
        missing_artifacts: Optional[Set[str]]
    ) -> str:
        """Get color for a node based on complexity and missing status."""
        # Missing artifacts are red
        if missing_artifacts and node in missing_artifacts:
            return self.missing_color
        
        # Color by complexity if enabled and data available
        if self.color_by_complexity and complexity_data and node in complexity_data:
            metrics = complexity_data[node]
            return self.complexity_colors.get(metrics.complexity_tier, self.default_color)
        
        return self.default_color
    
    def _get_node_label(
        self,
        node: str,
        complexity_data: Optional[Dict[str, ComplexityMetrics]]
    ) -> str:
        """Get label for a node, optionally including complexity info."""
        if complexity_data and node in complexity_data:
            metrics = complexity_data[node]
            return f"{node}\\n({metrics.complexity_tier})"
        return node
    
    def _sanitize_mermaid_id(self, name: str) -> str:
        """Sanitize name for use as Mermaid node ID."""
        # Replace special characters with underscores
        return name.replace('-', '_').replace('.', '_').replace(' ', '_')
    
    def _generate_dot_legend(self) -> List[str]:
        """Generate DOT legend for complexity colors."""
        lines = []
        lines.append('    // Legend')
        lines.append('    subgraph cluster_legend {')
        lines.append('        label="Legend";')
        lines.append('        style=filled;')
        lines.append('        color=lightgrey;')
        lines.append('')
        
        if self.color_by_complexity:
            for tier, color in self.complexity_colors.items():
                lines.append(f'        legend_{tier} [label="{tier}", fillcolor="{color}", shape=box];')
        
        if self.highlight_missing:
            lines.append(f'        legend_missing [label="Missing", fillcolor="{self.missing_color}", shape=box];')
        
        lines.append('    }')
        
        return lines
    
    def _generate_mermaid_styles(
        self,
        nodes: List[str],
        complexity_data: Optional[Dict[str, ComplexityMetrics]],
        missing_artifacts: Optional[Set[str]]
    ) -> List[str]:
        """Generate Mermaid style definitions."""
        lines = []
        lines.append('    %% Styling')
        
        for node in nodes:
            node_id = self._sanitize_mermaid_id(node)
            color = self._get_node_color(node, complexity_data, missing_artifacts)
            
            # Convert hex to Mermaid style
            lines.append(f'    style {node_id} fill:{color}')
        
        return lines
    
    def _generate_html_template(
        self,
        nodes_data: List[Dict],
        edges_data: List[Dict],
        title: str
    ) -> str:
        """Generate HTML template with vis.js visualization."""
        import json
        
        nodes_json = json.dumps(nodes_data, indent=2)
        edges_json = json.dumps(edges_data, indent=2)
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        #mynetwork {{
            width: 100%;
            height: 800px;
            border: 1px solid lightgray;
        }}
        .legend {{
            margin-top: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            padding: 5px 10px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div id="mynetwork"></div>
    
    <div class="legend">
        <strong>Legend:</strong>
'''
        
        # Add legend items
        if self.color_by_complexity:
            for tier, color in self.complexity_colors.items():
                html += f'        <span class="legend-item" style="background-color: {color};">{tier}</span>\n'
        
        if self.highlight_missing:
            html += f'        <span class="legend-item" style="background-color: {self.missing_color}; color: white;">Missing</span>\n'
        
        html += f'''    </div>
    
    <script type="text/javascript">
        // Create nodes and edges
        var nodes = new vis.DataSet({nodes_json});
        var edges = new vis.DataSet({edges_json});
        
        // Create network
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            layout: {{
                hierarchical: {{
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 200
                }}
            }},
            physics: {{
                enabled: false
            }},
            nodes: {{
                shape: 'box',
                margin: 10,
                widthConstraint: {{
                    maximum: 200
                }}
            }},
            edges: {{
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 1
                    }}
                }},
                smooth: {{
                    type: 'cubicBezier'
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        var network = new vis.Network(container, data, options);
        
        // Add click event
        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                console.log("Clicked node:", nodeId);
            }}
        }});
    </script>
</body>
</html>'''
        
        return html
