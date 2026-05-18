"""Report generator for missing code detection."""

import json
import csv
from typing import List, Dict, Any, Optional
from io import StringIO
from ..models.missing_artifact import (
    MissingArtifact,
    MissingArtifactReference,
    CompletenessReport
)


class MissingCodeReporter:
    """Generates reports for missing code detection."""
    
    def __init__(self, report: CompletenessReport):
        """
        Initialize reporter with completeness report.
        
        Args:
            report: CompletenessReport object
        """
        self.report = report
    
    def generate_summary_text(self) -> str:
        """
        Generate a text summary of missing artifacts.
        
        Returns:
            Text summary string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("MISSING ARTIFACTS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Overall completeness
        lines.append("OVERALL COMPLETENESS")
        lines.append("-" * 80)
        lines.append(f"Overall: {self.report.overall_completeness:.1%}")
        lines.append("")
        
        # Programs
        lines.append("PROGRAMS")
        lines.append(f"  Referenced: {self.report.total_referenced_programs}")
        lines.append(f"  Found:      {self.report.found_programs}")
        lines.append(f"  Missing:    {self.report.missing_programs}")
        lines.append(f"  Complete:   {self.report.program_completeness:.1%}")
        lines.append("")
        
        # Copybooks
        lines.append("COPYBOOKS")
        lines.append(f"  Referenced: {self.report.total_referenced_copybooks}")
        lines.append(f"  Found:      {self.report.found_copybooks}")
        lines.append(f"  Missing:    {self.report.missing_copybooks}")
        lines.append(f"  Complete:   {self.report.copybook_completeness:.1%}")
        lines.append("")
        
        # Datasets
        lines.append("DATASETS")
        lines.append(f"  Referenced: {self.report.total_referenced_datasets}")
        lines.append(f"  Found:      {self.report.found_datasets}")
        lines.append(f"  Missing:    {self.report.missing_datasets}")
        lines.append(f"  Complete:   {self.report.dataset_completeness:.1%}")
        lines.append("")
        
        # Missing artifacts by severity
        if self.report.missing_artifacts:
            lines.append("MISSING ARTIFACTS BY SEVERITY")
            lines.append("-" * 80)
            
            # Group by severity
            by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
            for artifact in self.report.missing_artifacts:
                by_severity[artifact.severity].append(artifact)
            
            for severity in ['HIGH', 'MEDIUM', 'LOW']:
                artifacts = by_severity[severity]
                if artifacts:
                    lines.append(f"\n{severity} SEVERITY ({len(artifacts)} artifacts)")
                    lines.append("-" * 40)
                    
                    for artifact in artifacts:
                        lines.append(
                            f"  {artifact.artifact_type:10} {artifact.artifact_name:30} "
                            f"(refs: {artifact.reference_count})"
                        )
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_detailed_text(
        self,
        include_references: bool = True
    ) -> str:
        """
        Generate a detailed text report with all missing artifacts.
        
        Args:
            include_references: Include list of where each artifact is referenced
            
        Returns:
            Detailed text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("DETAILED MISSING ARTIFACTS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append(str(self.report))
        lines.append("")
        
        # Detailed list
        if self.report.missing_artifacts:
            lines.append("DETAILED MISSING ARTIFACTS")
            lines.append("-" * 80)
            
            for i, artifact in enumerate(self.report.missing_artifacts, 1):
                lines.append(f"\n{i}. {artifact.artifact_type}: {artifact.artifact_name}")
                lines.append(f"   Severity: {artifact.severity}")
                lines.append(f"   References: {artifact.reference_count}")
                
                if include_references and artifact.referenced_by:
                    lines.append(f"   Referenced by:")
                    for ref in sorted(artifact.referenced_by):
                        lines.append(f"     - {ref}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def export_to_csv(self, include_references: bool = False) -> str:
        """
        Export missing artifacts to CSV format.
        
        Args:
            include_references: Include referenced_by column
            
        Returns:
            CSV string
        """
        output = StringIO()
        
        if include_references:
            fieldnames = [
                'artifact_name',
                'artifact_type',
                'reference_count',
                'severity',
                'referenced_by'
            ]
        else:
            fieldnames = [
                'artifact_name',
                'artifact_type',
                'reference_count',
                'severity'
            ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for artifact in self.report.missing_artifacts:
            row = {
                'artifact_name': artifact.artifact_name,
                'artifact_type': artifact.artifact_type,
                'reference_count': artifact.reference_count,
                'severity': artifact.severity
            }
            
            if include_references:
                row['referenced_by'] = '; '.join(artifact.referenced_by)
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def export_references_to_csv(
        self,
        references: List[MissingArtifactReference]
    ) -> str:
        """
        Export missing artifact references to CSV format.
        
        Args:
            references: List of MissingArtifactReference objects
            
        Returns:
            CSV string
        """
        output = StringIO()
        
        fieldnames = [
            'missing_artifact',
            'missing_artifact_type',
            'referenced_by',
            'referenced_by_type',
            'reference_type',
            'source_file',
            'line_number'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for ref in references:
            writer.writerow({
                'missing_artifact': ref.missing_artifact,
                'missing_artifact_type': ref.missing_artifact_type,
                'referenced_by': ref.referenced_by,
                'referenced_by_type': ref.referenced_by_type,
                'reference_type': ref.reference_type,
                'source_file': ref.source_file or '',
                'line_number': ref.line_number or ''
            })
        
        return output.getvalue()
    
    def export_to_json(self, include_references: bool = True) -> str:
        """
        Export missing artifacts to JSON format.
        
        Args:
            include_references: Include referenced_by list
            
        Returns:
            JSON string
        """
        data = {
            'completeness': {
                'overall': self.report.overall_completeness,
                'programs': {
                    'total_referenced': self.report.total_referenced_programs,
                    'found': self.report.found_programs,
                    'missing': self.report.missing_programs,
                    'completeness': self.report.program_completeness
                },
                'copybooks': {
                    'total_referenced': self.report.total_referenced_copybooks,
                    'found': self.report.found_copybooks,
                    'missing': self.report.missing_copybooks,
                    'completeness': self.report.copybook_completeness
                },
                'datasets': {
                    'total_referenced': self.report.total_referenced_datasets,
                    'found': self.report.found_datasets,
                    'missing': self.report.missing_datasets,
                    'completeness': self.report.dataset_completeness
                }
            },
            'missing_artifacts': []
        }
        
        for artifact in self.report.missing_artifacts:
            artifact_data = {
                'artifact_name': artifact.artifact_name,
                'artifact_type': artifact.artifact_type,
                'reference_count': artifact.reference_count,
                'severity': artifact.severity
            }
            
            if include_references:
                artifact_data['referenced_by'] = artifact.referenced_by
            
            if artifact.first_detected:
                artifact_data['first_detected'] = artifact.first_detected.isoformat()
            
            data['missing_artifacts'].append(artifact_data)
        
        return json.dumps(data, indent=2)
    
    def export_references_to_json(
        self,
        references: List[MissingArtifactReference]
    ) -> str:
        """
        Export missing artifact references to JSON format.
        
        Args:
            references: List of MissingArtifactReference objects
            
        Returns:
            JSON string
        """
        data = {
            'references': []
        }
        
        for ref in references:
            ref_data = {
                'missing_artifact': ref.missing_artifact,
                'missing_artifact_type': ref.missing_artifact_type,
                'referenced_by': ref.referenced_by,
                'referenced_by_type': ref.referenced_by_type,
                'reference_type': ref.reference_type
            }
            
            if ref.source_file:
                ref_data['source_file'] = ref.source_file
            
            if ref.line_number:
                ref_data['line_number'] = ref.line_number
            
            data['references'].append(ref_data)
        
        return json.dumps(data, indent=2)
    
    def generate_html_report(self) -> str:
        """
        Generate an HTML report for missing artifacts.
        
        Returns:
            HTML string
        """
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("  <title>Missing Artifacts Report</title>")
        html.append("  <style>")
        html.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
        html.append("    h1 { color: #333; }")
        html.append("    h2 { color: #666; margin-top: 30px; }")
        html.append("    table { border-collapse: collapse; width: 100%; margin-top: 10px; }")
        html.append("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("    th { background-color: #4CAF50; color: white; }")
        html.append("    tr:nth-child(even) { background-color: #f2f2f2; }")
        html.append("    .summary { background-color: #f9f9f9; padding: 15px; border-radius: 5px; }")
        html.append("    .high { color: #d32f2f; font-weight: bold; }")
        html.append("    .medium { color: #f57c00; font-weight: bold; }")
        html.append("    .low { color: #388e3c; }")
        html.append("    .completeness { font-size: 24px; font-weight: bold; }")
        html.append("  </style>")
        html.append("</head>")
        html.append("<body>")
        
        html.append("  <h1>Missing Artifacts Report</h1>")
        
        # Summary section
        html.append("  <div class='summary'>")
        html.append("    <h2>Completeness Summary</h2>")
        html.append(f"    <p class='completeness'>Overall: {self.report.overall_completeness:.1%}</p>")
        html.append("    <table>")
        html.append("      <tr>")
        html.append("        <th>Artifact Type</th>")
        html.append("        <th>Referenced</th>")
        html.append("        <th>Found</th>")
        html.append("        <th>Missing</th>")
        html.append("        <th>Completeness</th>")
        html.append("      </tr>")
        
        html.append("      <tr>")
        html.append("        <td>Programs</td>")
        html.append(f"        <td>{self.report.total_referenced_programs}</td>")
        html.append(f"        <td>{self.report.found_programs}</td>")
        html.append(f"        <td>{self.report.missing_programs}</td>")
        html.append(f"        <td>{self.report.program_completeness:.1%}</td>")
        html.append("      </tr>")
        
        html.append("      <tr>")
        html.append("        <td>Copybooks</td>")
        html.append(f"        <td>{self.report.total_referenced_copybooks}</td>")
        html.append(f"        <td>{self.report.found_copybooks}</td>")
        html.append(f"        <td>{self.report.missing_copybooks}</td>")
        html.append(f"        <td>{self.report.copybook_completeness:.1%}</td>")
        html.append("      </tr>")
        
        html.append("      <tr>")
        html.append("        <td>Datasets</td>")
        html.append(f"        <td>{self.report.total_referenced_datasets}</td>")
        html.append(f"        <td>{self.report.found_datasets}</td>")
        html.append(f"        <td>{self.report.missing_datasets}</td>")
        html.append(f"        <td>{self.report.dataset_completeness:.1%}</td>")
        html.append("      </tr>")
        
        html.append("    </table>")
        html.append("  </div>")
        
        # Missing artifacts table
        if self.report.missing_artifacts:
            html.append("  <h2>Missing Artifacts</h2>")
            html.append("  <table>")
            html.append("    <tr>")
            html.append("      <th>Artifact Name</th>")
            html.append("      <th>Type</th>")
            html.append("      <th>References</th>")
            html.append("      <th>Severity</th>")
            html.append("    </tr>")
            
            for artifact in self.report.missing_artifacts:
                severity_class = artifact.severity.lower()
                html.append("    <tr>")
                html.append(f"      <td>{artifact.artifact_name}</td>")
                html.append(f"      <td>{artifact.artifact_type}</td>")
                html.append(f"      <td>{artifact.reference_count}</td>")
                html.append(f"      <td class='{severity_class}'>{artifact.severity}</td>")
                html.append("    </tr>")
            
            html.append("  </table>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
    
    def save_report(
        self,
        output_file: str,
        format: str = 'text',
        include_references: bool = True
    ) -> None:
        """
        Save report to a file.
        
        Args:
            output_file: Path to output file
            format: Report format ('text', 'csv', 'json', 'html')
            include_references: Include referenced_by information
        """
        if format == 'text':
            content = self.generate_detailed_text(include_references)
        elif format == 'csv':
            content = self.export_to_csv(include_references)
        elif format == 'json':
            content = self.export_to_json(include_references)
        elif format == 'html':
            content = self.generate_html_report()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(output_file, 'w') as f:
            f.write(content)
