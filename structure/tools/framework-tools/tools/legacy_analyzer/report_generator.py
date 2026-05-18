"""Report generator for artifact lifecycle analysis."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ReportGenerator:
    """Generates comprehensive analysis reports in multiple formats."""
    
    def __init__(self, database: BaseDatabase):
        """
        Initialize report generator with database adapter.
        
        Args:
            database: Database adapter instance
        """
        self.database = database
        self.query_engine = QueryEngine(database)
        self.report_data = {}
        
        # Register artifact analysis queries
        self._register_queries()
    
    def _register_queries(self) -> None:
        """Register all artifact analysis queries."""
            UnreferencedJCLQuery,
            UnreferencedProgramsQuery,
            UnreferencedDatasetsQuery,
            UnreferencedCopybooksQuery,
            MissingJCLQuery,
            MissingProgramsQuery,
            MissingDatasetsQuery,
            ArtifactDependenciesQuery,
            ArtifactRiskAssessmentQuery,
            CleanupRecommendationsQuery
        )
        
        queries = [
            UnreferencedJCLQuery(),
            UnreferencedProgramsQuery(),
            UnreferencedDatasetsQuery(),
            UnreferencedCopybooksQuery(),
            MissingJCLQuery(),
            MissingProgramsQuery(),
            MissingDatasetsQuery(),
            ArtifactDependenciesQuery(),
            ArtifactRiskAssessmentQuery(),
            CleanupRecommendationsQuery()
        ]
        
        self.query_engine.register_queries(queries)
    
    def generate_reports(self, output_dir: str, format: str = 'markdown',
                        analysis_days: int = 365) -> None:
        """
        Generate comprehensive analysis reports.
        
        Args:
            output_dir: Directory to write reports
            format: Report format (json, csv, markdown)
            analysis_days: Number of days for analysis window
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nGenerating artifact lifecycle analysis reports...")
        print(f"  Output directory: {output_dir}")
        print(f"  Format: {format}")
        print(f"  Analysis window: {analysis_days} days")
        
        # Generate executive summary
        print("\n  Generating executive summary...")
        self._generate_executive_summary(analysis_days)
        
        # Generate unreferenced artifact reports
        print("  Generating unreferenced artifact reports...")
        self._generate_unreferenced_reports(analysis_days)
        
        # Generate missing artifact reports
        print("  Generating missing artifact reports...")
        self._generate_missing_reports(analysis_days)
        
        # Generate dependency reports
        print("  Generating dependency reports...")
        self._generate_dependency_reports()
        
        # Generate risk assessment report
        print("  Generating risk assessment report...")
        self._generate_risk_assessment(analysis_days)
        
        # Generate cleanup recommendations
        print("  Generating cleanup recommendations...")
        self._generate_cleanup_recommendations(analysis_days)
        
        # Write reports in requested format
        print(f"\n  Writing reports in {format} format...")
        if format == 'json':
            self._write_json_reports(output_path)
        elif format == 'csv':
            self._write_csv_reports(output_path)
        else:  # markdown
            self._write_markdown_reports(output_path)
        
        print(f"\n✓ Reports generated successfully in {output_dir}")
    
    def _generate_executive_summary(self, analysis_days: int) -> None:
        """Generate executive summary with high-level statistics."""
        summary = {
            'report_date': datetime.now().isoformat(),
            'analysis_window_days': analysis_days,
            'inventory_counts': {},
            'unreferenced_counts': {},
            'missing_counts': {},
            'storage_savings': {}
        }
        
        # Get inventory counts
        cursor = self.database.cursor
        
        # JCL count
        cursor.execute("SELECT COUNT(*) FROM inventory_jcl")
        summary['inventory_counts']['jcl'] = cursor.fetchone()[0]
        
        # Program count
        cursor.execute("SELECT COUNT(*) FROM inventory_programs")
        summary['inventory_counts']['programs'] = cursor.fetchone()[0]
        
        # Copybook count
        cursor.execute("SELECT COUNT(*) FROM inventory_copybooks")
        summary['inventory_counts']['copybooks'] = cursor.fetchone()[0]
        
        # Dataset count
        cursor.execute("SELECT COUNT(*) FROM inventory_datasets")
        summary['inventory_counts']['datasets'] = cursor.fetchone()[0]
        
        # CICS count
        cursor.execute("SELECT COUNT(*) FROM inventory_cics")
        summary['inventory_counts']['cics'] = cursor.fetchone()[0]
        
        # Get unreferenced counts (simplified queries for counts only)
        try:
            result = self.query_engine.execute('unreferenced_jcl', 
                                                     analysis_days=analysis_days)
            results = result.to_list_of_dicts()
            summary['unreferenced_counts']['jcl'] = len(results)
        except:
            summary['unreferenced_counts']['jcl'] = 0
        
        try:
            result = self.query_engine.execute('unreferenced_programs', 
                                                     analysis_days=analysis_days)
            results = result.to_list_of_dicts()
            summary['unreferenced_counts']['programs'] = len(results)
            # Calculate storage savings
            total_bytes = sum(row.get('size_bytes', 0) for row in results)
            summary['storage_savings']['programs_mb'] = round(total_bytes / (1024 * 1024), 2)
        except:
            summary['unreferenced_counts']['programs'] = 0
            summary['storage_savings']['programs_mb'] = 0
        
        try:
            result = self.query_engine.execute('unreferenced_datasets', 
                                                     analysis_days=analysis_days)
            results = result.to_list_of_dicts()
            summary['unreferenced_counts']['datasets'] = len(results)
            # Calculate storage savings
            total_mb = sum(row.get('size_mb', 0) for row in results)
            summary['storage_savings']['datasets_mb'] = round(total_mb, 2)
        except:
            summary['unreferenced_counts']['datasets'] = 0
            summary['storage_savings']['datasets_mb'] = 0
        
        try:
            result = self.query_engine.execute('unreferenced_copybooks')
            results = result.to_list_of_dicts()
            summary['unreferenced_counts']['copybooks'] = len(results)
        except:
            summary['unreferenced_counts']['copybooks'] = 0
        
        # Get missing counts
        try:
            result = self.query_engine.execute('missing_jcl', 
                                                     analysis_days=analysis_days)
            results = result.to_list_of_dicts()
            summary['missing_counts']['jcl'] = len(results)
        except:
            summary['missing_counts']['jcl'] = 0
        
        try:
            result = self.query_engine.execute('missing_programs', 
                                                     analysis_days=analysis_days)
            results = result.to_list_of_dicts()
            summary['missing_counts']['programs'] = len(results)
        except:
            summary['missing_counts']['programs'] = 0
        
        try:
            result = self.query_engine.execute('missing_datasets', 
                                                     analysis_days=analysis_days)
            results = result.to_list_of_dicts()
            summary['missing_counts']['datasets'] = len(results)
        except:
            summary['missing_counts']['datasets'] = 0
        
        # Calculate total storage savings
        summary['storage_savings']['total_mb'] = (
            summary['storage_savings']['programs_mb'] + 
            summary['storage_savings']['datasets_mb']
        )
        summary['storage_savings']['total_gb'] = round(
            summary['storage_savings']['total_mb'] / 1024, 2
        )
        
        self.report_data['executive_summary'] = summary
    
    def _generate_unreferenced_reports(self, analysis_days: int) -> None:
        """Generate detailed reports for unreferenced artifacts."""
        self.report_data['unreferenced'] = {}
        
        # Unreferenced JCL
        try:
            result = self.query_engine.execute('unreferenced_jcl', 
                                                     analysis_days=analysis_days)
            self.report_data['unreferenced']['jcl'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate unreferenced JCL report: {e}")
            self.report_data['unreferenced']['jcl'] = []
        
        # Unreferenced programs
        try:
            result = self.query_engine.execute('unreferenced_programs', 
                                                     analysis_days=analysis_days)
            self.report_data['unreferenced']['programs'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate unreferenced programs report: {e}")
            self.report_data['unreferenced']['programs'] = []
        
        # Unreferenced datasets
        try:
            result = self.query_engine.execute('unreferenced_datasets', 
                                                     analysis_days=analysis_days)
            self.report_data['unreferenced']['datasets'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate unreferenced datasets report: {e}")
            self.report_data['unreferenced']['datasets'] = []
        
        # Unreferenced copybooks
        try:
            result = self.query_engine.execute('unreferenced_copybooks')
            self.report_data['unreferenced']['copybooks'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate unreferenced copybooks report: {e}")
            self.report_data['unreferenced']['copybooks'] = []
    
    def _generate_missing_reports(self, analysis_days: int) -> None:
        """Generate detailed reports for missing artifacts."""
        self.report_data['missing'] = {}
        
        # Missing JCL
        try:
            result = self.query_engine.execute('missing_jcl', 
                                                     analysis_days=analysis_days)
            self.report_data['missing']['jcl'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate missing JCL report: {e}")
            self.report_data['missing']['jcl'] = []
        
        # Missing programs
        try:
            result = self.query_engine.execute('missing_programs', 
                                                     analysis_days=analysis_days)
            self.report_data['missing']['programs'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate missing programs report: {e}")
            self.report_data['missing']['programs'] = []
        
        # Missing datasets
        try:
            result = self.query_engine.execute('missing_datasets', 
                                                     analysis_days=analysis_days)
            self.report_data['missing']['datasets'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate missing datasets report: {e}")
            self.report_data['missing']['datasets'] = []
    
    def _generate_dependency_reports(self) -> None:
        """Generate dependency analysis reports."""
        # For now, just note that dependencies are available
        # Full dependency reports would require specific artifact names
        cursor = self.database.cursor
        try:
            cursor.execute("SELECT COUNT(*) FROM artifact_dependencies")
            count = cursor.fetchone()[0]
            self.report_data['dependencies'] = {
                'total_dependencies': count,
                'note': 'Use artifact_dependencies query with specific artifact names for detailed dependency analysis'
            }
        except:
            self.report_data['dependencies'] = {
                'total_dependencies': 0,
                'note': 'No dependency data available'
            }
    
    def _generate_risk_assessment(self, analysis_days: int) -> None:
        """Generate risk assessment report."""
        try:
            result = self.query_engine.execute('artifact_risk_assessment', 
                                                     analysis_days=analysis_days)
            self.report_data['risk_assessment'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate risk assessment report: {e}")
            self.report_data['risk_assessment'] = []
    
    def _generate_cleanup_recommendations(self, analysis_days: int) -> None:
        """Generate cleanup recommendations report."""
        try:
            result = self.query_engine.execute('cleanup_recommendations', 
                                                     analysis_days=analysis_days,
                                                     top_n=100)
            self.report_data['cleanup_recommendations'] = result.to_list_of_dicts()
        except Exception as e:
            print(f"    Warning: Could not generate cleanup recommendations: {e}")
            self.report_data['cleanup_recommendations'] = []
    
    def _write_json_reports(self, output_path: Path) -> None:
        """Write reports in JSON format."""
        # Write complete report as single JSON file
        report_file = output_path / 'artifact_analysis_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, default=str)
        print(f"    ✓ {report_file}")
        
        # Also write individual section files
        for section, data in self.report_data.items():
            section_file = output_path / f'{section}.json'
            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"    ✓ {section_file}")
    
    def _write_csv_reports(self, output_path: Path) -> None:
        """Write reports in CSV format."""
        # Write unreferenced artifacts
        for artifact_type, data in self.report_data.get('unreferenced', {}).items():
            if data and len(data) > 0:
                csv_file = output_path / f'unreferenced_{artifact_type}.csv'
                self._write_csv_file(csv_file, data)
                print(f"    ✓ {csv_file}")
        
        # Write missing artifacts
        for artifact_type, data in self.report_data.get('missing', {}).items():
            if data and len(data) > 0:
                csv_file = output_path / f'missing_{artifact_type}.csv'
                self._write_csv_file(csv_file, data)
                print(f"    ✓ {csv_file}")
        
        # Write risk assessment
        if self.report_data.get('risk_assessment'):
            csv_file = output_path / 'risk_assessment.csv'
            self._write_csv_file(csv_file, self.report_data['risk_assessment'])
            print(f"    ✓ {csv_file}")
        
        # Write cleanup recommendations
        if self.report_data.get('cleanup_recommendations'):
            csv_file = output_path / 'cleanup_recommendations.csv'
            self._write_csv_file(csv_file, self.report_data['cleanup_recommendations'])
            print(f"    ✓ {csv_file}")
        
        # Write executive summary as CSV
        summary_file = output_path / 'executive_summary.csv'
        self._write_summary_csv(summary_file, self.report_data.get('executive_summary', {}))
        print(f"    ✓ {summary_file}")
    
    def _write_csv_file(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """Write data to CSV file."""
        if not data:
            return
        
        # Get all unique keys from all rows
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(fieldnames)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def _write_summary_csv(self, file_path: Path, summary: Dict[str, Any]) -> None:
        """Write executive summary as CSV."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            
            writer.writerow(['Report Date', summary.get('report_date', '')])
            writer.writerow(['Analysis Window (days)', summary.get('analysis_window_days', '')])
            writer.writerow(['', ''])
            
            writer.writerow(['INVENTORY COUNTS', ''])
            for key, value in summary.get('inventory_counts', {}).items():
                writer.writerow([f'  {key.upper()}', value])
            writer.writerow(['', ''])
            
            writer.writerow(['UNREFERENCED COUNTS', ''])
            for key, value in summary.get('unreferenced_counts', {}).items():
                writer.writerow([f'  {key.upper()}', value])
            writer.writerow(['', ''])
            
            writer.writerow(['MISSING COUNTS', ''])
            for key, value in summary.get('missing_counts', {}).items():
                writer.writerow([f'  {key.upper()}', value])
            writer.writerow(['', ''])
            
            writer.writerow(['STORAGE SAVINGS', ''])
            for key, value in summary.get('storage_savings', {}).items():
                writer.writerow([f'  {key.upper()}', value])
    
    def _write_markdown_reports(self, output_path: Path) -> None:
        """Write reports in Markdown format."""
        # Write main report file
        report_file = output_path / 'ARTIFACT_ANALYSIS_REPORT.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write('# Artifact Lifecycle Analysis Report\n\n')
            
            # Write executive summary
            self._write_markdown_executive_summary(f)
            
            # Write unreferenced artifacts section
            self._write_markdown_unreferenced(f)
            
            # Write missing artifacts section
            self._write_markdown_missing(f)
            
            # Write risk assessment section
            self._write_markdown_risk_assessment(f)
            
            # Write cleanup recommendations section
            self._write_markdown_cleanup_recommendations(f)
            
            # Write dependencies section
            self._write_markdown_dependencies(f)
        
        print(f"    ✓ {report_file}")
    
    def _write_markdown_executive_summary(self, f) -> None:
        """Write executive summary section in Markdown."""
        summary = self.report_data.get('executive_summary', {})
        
        f.write('## Executive Summary\n\n')
        f.write(f"**Report Date:** {summary.get('report_date', 'N/A')}\n\n")
        f.write(f"**Analysis Window:** {summary.get('analysis_window_days', 'N/A')} days\n\n")
        
        f.write('### Inventory Overview\n\n')
        f.write('| Artifact Type | Count |\n')
        f.write('|--------------|-------|\n')
        for key, value in summary.get('inventory_counts', {}).items():
            f.write(f'| {key.upper()} | {value:,} |\n')
        f.write('\n')
        
        f.write('### Unreferenced Artifacts\n\n')
        f.write('| Artifact Type | Count |\n')
        f.write('|--------------|-------|\n')
        for key, value in summary.get('unreferenced_counts', {}).items():
            f.write(f'| {key.upper()} | {value:,} |\n')
        f.write('\n')
        
        f.write('### Missing Artifacts\n\n')
        f.write('| Artifact Type | Count |\n')
        f.write('|--------------|-------|\n')
        for key, value in summary.get('missing_counts', {}).items():
            f.write(f'| {key.upper()} | {value:,} |\n')
        f.write('\n')
        
        f.write('### Potential Storage Savings\n\n')
        savings = summary.get('storage_savings', {})
        f.write(f"- **Programs:** {savings.get('programs_mb', 0):,.2f} MB\n")
        f.write(f"- **Datasets:** {savings.get('datasets_mb', 0):,.2f} MB\n")
        f.write(f"- **Total:** {savings.get('total_mb', 0):,.2f} MB ({savings.get('total_gb', 0):,.2f} GB)\n\n")
        
        f.write('---\n\n')
    
    def _write_markdown_unreferenced(self, f) -> None:
        """Write unreferenced artifacts section in Markdown."""
        f.write('## Unreferenced Artifacts\n\n')
        f.write('Artifacts that exist in inventory but have not been used within the analysis window.\n\n')
        
        unreferenced = self.report_data.get('unreferenced', {})
        
        for artifact_type, data in unreferenced.items():
            f.write(f'### Unreferenced {artifact_type.upper()}\n\n')
            if data and len(data) > 0:
                f.write(f'**Count:** {len(data):,}\n\n')
                f.write(f'**Top 10 by age/size:**\n\n')
                
                # Write table header based on artifact type
                if artifact_type == 'jcl':
                    f.write('| Member Name | Library | Last Modified | Days Since Modified |\n')
                    f.write('|-------------|---------|---------------|--------------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('member_name', '')} | {row.get('library_name', '')} | "
                               f"{row.get('last_modified', '')} | {row.get('days_since_modified', '')} |\n")
                elif artifact_type == 'programs':
                    f.write('| Program Name | Library | Link Date | Size (KB) | Days Unused |\n')
                    f.write('|--------------|---------|-----------|-----------|-------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('program_name', '')} | {row.get('library_name', '')} | "
                               f"{row.get('link_date', '')} | {row.get('size_kb', 0):,.2f} | "
                               f"{row.get('days_unused', '')} |\n")
                elif artifact_type == 'datasets':
                    f.write('| Dataset Name | Creation Date | Size (MB) | Type | Days Since Creation |\n')
                    f.write('|--------------|---------------|-----------|------|--------------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('dataset_name', '')} | {row.get('creation_date', '')} | "
                               f"{row.get('size_mb', 0):,.2f} | {row.get('dataset_type', '')} | "
                               f"{row.get('days_since_creation', '')} |\n")
                elif artifact_type == 'copybooks':
                    f.write('| Copybook Name | Library | Last Modified | Days Since Modified |\n')
                    f.write('|---------------|---------|---------------|--------------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('copybook_name', '')} | {row.get('library_name', '')} | "
                               f"{row.get('last_modified', '')} | {row.get('days_since_modified', '')} |\n")
                f.write('\n')
            else:
                f.write('*No unreferenced artifacts found.*\n\n')
        
        f.write('---\n\n')
    
    def _write_markdown_missing(self, f) -> None:
        """Write missing artifacts section in Markdown."""
        f.write('## Missing Artifacts\n\n')
        
        missing = self.report_data.get('missing', {})
        
        for artifact_type, data in missing.items():
            f.write(f'### Missing {artifact_type.upper()}\n\n')
            if data and len(data) > 0:
                f.write(f'**Count:** {len(data):,}\n\n')
                f.write(f'**Top 10 by usage:**\n\n')
                
                # Write table header based on artifact type
                if artifact_type == 'jcl':
                    f.write('| Job Name | First Seen | Last Seen | Execution Count |\n')
                    f.write('|----------|------------|-----------|----------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('job_name', '')} | {row.get('first_seen', '')} | "
                               f"{row.get('last_seen', '')} | {row.get('execution_count', 0):,} |\n")
                elif artifact_type == 'programs':
                    f.write('| Program Name | Source Type | First Seen | Last Seen | Execution Count |\n')
                    f.write('|--------------|-------------|------------|-----------|----------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('program_name', '')} | {row.get('source_type', '')} | "
                               f"{row.get('first_seen', '')} | {row.get('last_seen', '')} | "
                               f"{row.get('execution_count', 0):,} |\n")
                elif artifact_type == 'datasets':
                    f.write('| Dataset Name | First Seen | Last Seen | Access Count |\n')
                    f.write('|--------------|------------|-----------|-------------|\n')
                    for row in data[:10]:
                        f.write(f"| {row.get('dataset_name', '')} | {row.get('first_seen', '')} | "
                               f"{row.get('last_seen', '')} | {row.get('access_count', 0):,} |\n")
                f.write('\n')
            else:
                f.write('*No missing artifacts found.*\n\n')
        
        f.write('---\n\n')
    
    def _write_markdown_risk_assessment(self, f) -> None:
        """Write risk assessment section in Markdown."""
        f.write('## Risk Assessment\n\n')
        f.write('Risk categorization of unreferenced artifacts.\n\n')
        
        data = self.report_data.get('risk_assessment', [])
        
        if data and len(data) > 0:
            # Group by risk level
            high_risk = [r for r in data if r.get('risk_level') == 'HIGH']
            medium_risk = [r for r in data if r.get('risk_level') == 'MEDIUM']
            low_risk = [r for r in data if r.get('risk_level') == 'LOW']
            
            f.write(f'**Summary:**\n')
            f.write(f'- HIGH Risk: {len(high_risk):,}\n')
            f.write(f'- MEDIUM Risk: {len(medium_risk):,}\n')
            f.write(f'- LOW Risk: {len(low_risk):,}\n\n')
            
            # Show high risk items
            if high_risk:
                f.write('### HIGH Risk Artifacts\n\n')
                f.write('| Artifact Name | Type | Risk Reason | Dependencies | Days Inactive | Action |\n')
                f.write('|---------------|------|-------------|--------------|---------------|--------|\n')
                for row in high_risk[:20]:
                    f.write(f"| {row.get('artifact_name', '')} | {row.get('artifact_type', '')} | "
                           f"{row.get('risk_reason', '')} | {row.get('dependent_count', 0)} | "
                           f"{row.get('days_inactive', '')} | {row.get('recommended_action', '')} |\n")
                f.write('\n')
        else:
            f.write('*No risk assessment data available.*\n\n')
        
        f.write('---\n\n')
    
    def _write_markdown_cleanup_recommendations(self, f) -> None:
        """Write cleanup recommendations section in Markdown."""
        f.write('## Cleanup Recommendations\n\n')
        f.write('Prioritized recommendations for artifact cleanup.\n\n')
        
        data = self.report_data.get('cleanup_recommendations', [])
        
        if data and len(data) > 0:
            f.write(f'**Top {min(len(data), 20)} Cleanup Candidates:**\n\n')
            f.write('| Rank | Artifact Name | Type | Priority Score | Size | Days Inactive | Action |\n')
            f.write('|------|---------------|------|----------------|------|---------------|--------|\n')
            for i, row in enumerate(data[:20], 1):
                size_str = f"{row.get('size_kb', 0):,.2f} KB" if row.get('size_kb') else 'N/A'
                f.write(f"| {i} | {row.get('artifact_name', '')} | {row.get('artifact_type', '')} | "
                       f"{row.get('priority_score', 0):.2f} | {size_str} | "
                       f"{row.get('days_inactive', '')} | {row.get('recommended_action', '')} |\n")
            f.write('\n')
        else:
            f.write('*No cleanup recommendations available.*\n\n')
        
        f.write('---\n\n')
    
    def _write_markdown_dependencies(self, f) -> None:
        """Write dependencies section in Markdown."""
        f.write('## Dependencies\n\n')
        
        deps = self.report_data.get('dependencies', {})
        total = deps.get('total_dependencies', 0)
        
        f.write(f'**Total Dependencies Tracked:** {total:,}\n\n')
        f.write(f'{deps.get("note", "")}\n\n')
        
        f.write('To query specific artifact dependencies, use:\n')
        f.write('```bash\n')
        f.write('  --db your_database.db \\\n')
        f.write('  --artifact_name "PROGRAM_NAME" \\\n')
        f.write('  --direction both\n')
        f.write('```\n\n')
