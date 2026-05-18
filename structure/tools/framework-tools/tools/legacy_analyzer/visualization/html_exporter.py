"""HTML report exporter for legacy analyzer."""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

from .report_generator import AnalysisResults, ReportGenerator
from ..models.flow import ProgramFlow, CallGraph
from ..models.complexity import ComplexityMetrics
from ..models.package import MigrationPackage


class HTMLExporter:
    """Exports reports as HTML using Jinja2 templates."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize HTML exporter.
        
        Args:
            templates_dir: Path to templates directory (optional)
        """
        if not JINJA2_AVAILABLE:
            raise ImportError(
                "Jinja2 is required for HTML export. "
                "Install it with: pip install jinja2"
            )
        
        # Set templates directory
        if templates_dir is None:
            # Default to templates directory in this package
            templates_dir = Path(__file__).parent / 'templates'
        
        self.templates_dir = Path(templates_dir)
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        self.report_generator = ReportGenerator()
    
    def export_executive_summary(
        self,
        analysis_results: AnalysisResults,
        output_file: str
    ) -> None:
        """
        Export executive summary as HTML.
        
        Args:
            analysis_results: Analysis results to export
            output_file: Output file path
        """
        template = self.env.get_template('executive_summary.html')
        
        # Prepare data for template
        context = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_artifacts': analysis_results.total_artifacts,
            'total_programs': analysis_results.total_programs,
            'total_copybooks': analysis_results.total_copybooks,
            'total_datasets': analysis_results.total_datasets,
            'complexity_distribution': analysis_results.complexity_distribution,
            'total_analyzed': sum(analysis_results.complexity_distribution.values()),
            'missing_artifacts_count': analysis_results.missing_artifacts_count,
            'circular_dependencies_count': analysis_results.circular_dependencies_count,
            'packages': analysis_results.packages
        }
        
        # Calculate completeness score
        if analysis_results.total_artifacts > 0:
            context['completeness_score'] = (
                (analysis_results.total_artifacts - analysis_results.missing_artifacts_count) /
                analysis_results.total_artifacts * 100
            )
        
        # Group missing artifacts by type
        if analysis_results.missing_artifacts:
            missing_by_type = {}
            for artifact in analysis_results.missing_artifacts:
                missing_by_type[artifact.artifact_type] = \
                    missing_by_type.get(artifact.artifact_type, 0) + 1
            context['missing_by_type'] = missing_by_type
        
        # Calculate package totals
        if analysis_results.packages:
            context['total_artifacts_in_packages'] = sum(
                len(pkg.artifacts) for pkg in analysis_results.packages
            )
            context['total_loc'] = sum(
                pkg.total_loc for pkg in analysis_results.packages
            )
        
        # Generate key findings
        key_findings = []
        
        if analysis_results.complexity_metrics:
            high_complexity = [
                name for name, metrics in analysis_results.complexity_metrics.items()
                if metrics.complexity_tier in ['HIGH', 'VERY_HIGH']
            ]
            if high_complexity:
                key_findings.append(
                    f"{len(high_complexity)} programs have HIGH or VERY_HIGH complexity"
                )
        
        if analysis_results.missing_artifacts_count > 0 and analysis_results.total_artifacts > 0:
            completeness = (
                (analysis_results.total_artifacts - analysis_results.missing_artifacts_count) /
                analysis_results.total_artifacts * 100
            )
            key_findings.append(f"Inventory completeness: {completeness:.1f}%")
        
        if analysis_results.circular_dependencies_count > 0:
            key_findings.append(
                f"{analysis_results.circular_dependencies_count} circular dependencies detected"
            )
        
        if not key_findings:
            key_findings.append("No critical issues detected")
        
        context['key_findings'] = key_findings
        
        # Render template
        html = template.render(**context)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def export_artifact_detail(
        self,
        artifact_name: str,
        output_file: str,
        complexity_metrics: Optional[ComplexityMetrics] = None,
        flow: Optional[ProgramFlow] = None,
        callers: Optional[List[str]] = None,
        callees: Optional[List[str]] = None,
        copybooks: Optional[List[str]] = None,
        datasets: Optional[List[str]] = None,
        package_assignment: Optional[str] = None
    ) -> None:
        """
        Export artifact detail as HTML.
        
        Args:
            artifact_name: Name of the artifact
            output_file: Output file path
            complexity_metrics: Complexity metrics for the artifact
            flow: Program flow starting from this artifact
            callers: List of programs that call this artifact
            callees: List of programs called by this artifact
            copybooks: List of copybooks used by this artifact
            datasets: List of datasets accessed by this artifact
            package_assignment: Migration package this artifact belongs to
        """
        template = self.env.get_template('artifact_detail.html')
        
        # Prepare data for template
        context = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'artifact_name': artifact_name,
            'complexity_metrics': complexity_metrics,
            'flow': flow,
            'callers': callers or [],
            'callees': callees or [],
            'copybooks': copybooks or [],
            'datasets': datasets or [],
            'package_assignment': package_assignment
        }
        
        # Render template
        html = template.render(**context)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def export_flow_diagram(
        self,
        flow: ProgramFlow,
        output_file: str,
        complexity_data: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[set] = None,
        title: Optional[str] = None
    ) -> None:
        """
        Export flow diagram as interactive HTML.
        
        Args:
            flow: Program flow to visualize
            output_file: Output file path
            complexity_data: Optional complexity metrics for coloring
            missing_artifacts: Optional set of missing artifact names
            title: Optional title for the diagram
        """
        template = self.env.get_template('flow_diagram.html')
        
        # Build nodes and edges data
        nodes_data = []
        edges_data = []
        
        # Color scheme
        complexity_colors = {
            'LOW': '#90EE90',
            'MEDIUM': '#FFD700',
            'HIGH': '#FFA500',
            'VERY_HIGH': '#FF6347'
        }
        missing_color = '#FF0000'
        default_color = '#87CEEB'
        
        # Add nodes
        for program in flow.programs:
            # Determine color
            color = default_color
            if missing_artifacts and program in missing_artifacts:
                color = missing_color
            elif complexity_data and program in complexity_data:
                metrics = complexity_data[program]
                color = complexity_colors.get(metrics.complexity_tier, default_color)
            
            # Create label
            label = program
            if complexity_data and program in complexity_data:
                metrics = complexity_data[program]
                label = f"{program}\\n({metrics.complexity_tier})"
            
            node_data = {
                'id': program,
                'label': label,
                'color': color,
                'font': {'color': '#000000'}
            }
            
            # Add border for missing artifacts
            if missing_artifacts and program in missing_artifacts:
                node_data['borderWidth'] = 3
                node_data['color'] = {
                    'background': color,
                    'border': missing_color
                }
            
            nodes_data.append(node_data)
        
        # Add edges from dependencies
        for dep in flow.dependencies:
            if dep.target_type == 'PROGRAM':
                edges_data.append({
                    'from': dep.source_artifact,
                    'to': dep.target_artifact,
                    'arrows': 'to'
                })
        
        # Prepare statistics
        stats = {
            'total_nodes': len(flow.programs),
            'total_edges': len([d for d in flow.dependencies if d.target_type == 'PROGRAM']),
            'max_depth': flow.depth,
            'circular_deps': len(flow.circular_dependencies) if flow.circular_dependencies else 0
        }
        
        # Prepare context
        context = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': title or f"Program Flow: {flow.start_program}",
            'nodes_json': json.dumps(nodes_data),
            'edges_json': json.dumps(edges_data),
            'stats': stats
        }
        
        # Render template
        html = template.render(**context)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)


class MarkdownExporter:
    """Exports reports as Markdown."""
    
    def __init__(self):
        """Initialize Markdown exporter."""
        self.report_generator = ReportGenerator()
    
    def export_executive_summary(
        self,
        analysis_results: AnalysisResults,
        output_file: str
    ) -> None:
        """
        Export executive summary as Markdown.
        
        Args:
            analysis_results: Analysis results to export
            output_file: Output file path
        """
        # Generate text report
        text_report = self.report_generator.generate_executive_summary(analysis_results)
        
        # Convert to Markdown format
        markdown = self._text_to_markdown(text_report)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
    
    def export_artifact_detail(
        self,
        artifact_name: str,
        output_file: str,
        **kwargs
    ) -> None:
        """
        Export artifact detail as Markdown.
        
        Args:
            artifact_name: Name of the artifact
            output_file: Output file path
            **kwargs: Additional arguments for report generation
        """
        # Generate text report
        text_report = self.report_generator.generate_artifact_report(
            artifact_name,
            **kwargs
        )
        
        # Convert to Markdown format
        markdown = self._text_to_markdown(text_report)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
    
    def export_package_report(
        self,
        package: MigrationPackage,
        output_file: str
    ) -> None:
        """
        Export package report as Markdown.
        
        Args:
            package: Migration package to export
            output_file: Output file path
        """
        # Generate text report
        text_report = self.report_generator.generate_package_report(package)
        
        # Convert to Markdown format
        markdown = self._text_to_markdown(text_report)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
    
    def _text_to_markdown(self, text: str) -> str:
        """
        Convert text report to Markdown format.
        
        Args:
            text: Text report
            
        Returns:
            Markdown formatted text
        """
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            # Convert section headers (=== lines)
            if line.startswith('==='):
                continue  # Skip separator lines
            
            # Convert subsection headers (--- lines)
            if line.startswith('---'):
                continue  # Skip separator lines
            
            # Check if previous line should be a header
            if markdown_lines and line.strip() == '':
                prev_line = markdown_lines[-1] if markdown_lines else ''
                if prev_line and not prev_line.startswith('#'):
                    # Check if it looks like a header (all caps or title case)
                    if prev_line.isupper() or prev_line.istitle():
                        markdown_lines[-1] = f"## {prev_line}"
            
            # Convert bullet points
            if line.strip().startswith('•'):
                line = line.replace('•', '-')
            
            markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)


class JSONExporter:
    """Exports reports as JSON."""
    
    def __init__(self):
        """Initialize JSON exporter."""
        pass
    
    def export_analysis_results(
        self,
        analysis_results: AnalysisResults,
        output_file: str
    ) -> None:
        """
        Export complete analysis results as JSON.
        
        Args:
            analysis_results: Analysis results to export
            output_file: Output file path
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'inventory': {
                'total_artifacts': analysis_results.total_artifacts,
                'total_programs': analysis_results.total_programs,
                'total_copybooks': analysis_results.total_copybooks,
                'total_datasets': analysis_results.total_datasets
            },
            'complexity_distribution': analysis_results.complexity_distribution,
            'missing_artifacts_count': analysis_results.missing_artifacts_count,
            'circular_dependencies_count': analysis_results.circular_dependencies_count
        }
        
        # Add complexity metrics
        if analysis_results.complexity_metrics:
            data['complexity_metrics'] = {
                name: {
                    'lines_of_code': m.lines_of_code,
                    'cyclomatic_complexity': m.cyclomatic_complexity,
                    'dependency_count_in': m.dependency_count_in,
                    'dependency_count_out': m.dependency_count_out,
                    'composite_score': m.composite_score,
                    'complexity_tier': m.complexity_tier,
                    'language': m.language,
                    'is_god_program': m.is_god_program
                }
                for name, m in analysis_results.complexity_metrics.items()
            }
        
        # Add missing artifacts
        if analysis_results.missing_artifacts:
            data['missing_artifacts'] = [
                {
                    'artifact_name': a.artifact_name,
                    'artifact_type': a.artifact_type,
                    'reference_count': a.reference_count,
                    'severity': a.severity,
                    'referenced_by': a.referenced_by
                }
                for a in analysis_results.missing_artifacts
            ]
        
        # Add packages
        if analysis_results.packages:
            data['packages'] = [
                {
                    'name': p.name,
                    'artifacts': p.artifacts,
                    'total_loc': p.total_loc,
                    'total_complexity': p.total_complexity,
                    'external_dependencies': p.external_dependencies,
                    'conflicts': p.conflicts
                }
                for p in analysis_results.packages
            ]
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def export_flow(
        self,
        flow: ProgramFlow,
        output_file: str
    ) -> None:
        """
        Export program flow as JSON.
        
        Args:
            flow: Program flow to export
            output_file: Output file path
        """
        data = {
            'start_program': flow.start_program,
            'depth': flow.depth,
            'total_programs': len(flow.programs),
            'programs': flow.programs,
            'dependencies': [
                {
                    'source': d.source_artifact,
                    'target': d.target_artifact,
                    'type': d.dependency_type.value if hasattr(d.dependency_type, 'value') else str(d.dependency_type)
                }
                for d in flow.dependencies
            ],
            'circular_dependencies': [
                {
                    'artifacts': c.artifacts,
                    'cycle_length': len(c.artifacts)
                }
                for c in flow.circular_dependencies
            ] if flow.circular_dependencies else []
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


class PDFExporter:
    """Exports reports as PDF (requires weasyprint)."""
    
    def __init__(self):
        """Initialize PDF exporter."""
        try:
            import weasyprint
            self.weasyprint = weasyprint
            self.available = True
        except ImportError:
            self.available = False
        
        self.html_exporter = HTMLExporter() if JINJA2_AVAILABLE else None
    
    def export_from_html(
        self,
        html_file: str,
        output_file: str
    ) -> None:
        """
        Export HTML file as PDF.
        
        Args:
            html_file: Input HTML file path
            output_file: Output PDF file path
        """
        if not self.available:
            raise ImportError(
                "WeasyPrint is required for PDF export. "
                "Install it with: pip install weasyprint"
            )
        
        # Read HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert to PDF
        self.weasyprint.HTML(string=html_content).write_pdf(output_file)
    
    def export_executive_summary(
        self,
        analysis_results: AnalysisResults,
        output_file: str
    ) -> None:
        """
        Export executive summary as PDF.
        
        Args:
            analysis_results: Analysis results to export
            output_file: Output PDF file path
        """
        if not self.available or not self.html_exporter:
            raise ImportError(
                "WeasyPrint and Jinja2 are required for PDF export. "
                "Install them with: pip install weasyprint jinja2"
            )
        
        # Generate HTML first
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
            html_file = tmp.name
        
        try:
            self.html_exporter.export_executive_summary(analysis_results, html_file)
            self.export_from_html(html_file, output_file)
        finally:
            # Clean up temp file
            Path(html_file).unlink(missing_ok=True)
