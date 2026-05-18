"""Package exporter for migration planning."""

import json
import csv
from typing import List, Dict, Any, TextIO
from ..models.package import MigrationPackage


class PackageExporter:
    """
    Exports migration packages to various formats.
    
    Supported formats:
    - CSV: For project management tools (Excel, Jira, etc.)
    - JSON: For programmatic use
    - Markdown: For documentation
    """
    
    def export_to_csv(self, packages: List[MigrationPackage], output_file: str) -> None:
        """
        Export packages to CSV format.
        
        Creates a CSV with one row per artifact, including package metadata.
        
        Args:
            packages: List of MigrationPackage objects
            output_file: Path to output CSV file
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Package Name',
                'Package Priority',
                'Package Total Artifacts',
                'Package Total LOC',
                'Package Total Complexity',
                'Package Has External Deps',
                'Package Has Conflicts',
                'Artifact Name',
                'Artifact Type',
                'Is Seed Artifact'
            ])
            
            # Write data
            for package in packages:
                for artifact in package.artifacts:
                    # Determine artifact type
                    if artifact in package.programs:
                        artifact_type = 'PROGRAM'
                    elif artifact in package.copybooks:
                        artifact_type = 'COPYBOOK'
                    elif artifact in package.jcl:
                        artifact_type = 'JCL'
                    elif artifact in package.datasets:
                        artifact_type = 'DATASET'
                    else:
                        artifact_type = 'UNKNOWN'
                    
                    writer.writerow([
                        package.name,
                        package.priority or '',
                        package.total_artifacts,
                        package.total_loc,
                        f"{package.total_complexity:.2f}",
                        'Yes' if len(package.external_dependencies) > 0 else 'No',
                        'Yes' if package.has_conflicts() else 'No',
                        artifact,
                        artifact_type,
                        ''  # Seed artifact flag (would need to track separately)
                    ])
    
    def export_to_json(self, packages: List[MigrationPackage], output_file: str) -> None:
        """
        Export packages to JSON format.
        
        Args:
            packages: List of MigrationPackage objects
            output_file: Path to output JSON file
        """
        packages_data = []
        
        for package in packages:
            package_dict = {
                'name': package.name,
                'description': package.description,
                'priority': package.priority,
                'created_date': package.created_date.isoformat() if package.created_date else None,
                'metrics': {
                    'total_artifacts': package.total_artifacts,
                    'total_loc': package.total_loc,
                    'total_complexity': round(package.total_complexity, 2)
                },
                'artifacts': {
                    'programs': package.programs,
                    'copybooks': package.copybooks,
                    'jcl': package.jcl,
                    'datasets': package.datasets
                },
                'external_dependencies': package.external_dependencies,
                'conflicts': package.conflicts,
                'is_self_contained': package.is_self_contained(),
                'has_conflicts': package.has_conflicts()
            }
            packages_data.append(package_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(packages_data, f, indent=2)
    
    def export_to_markdown(self, packages: List[MigrationPackage], output_file: str) -> None:
        """
        Export packages to Markdown format for documentation.
        
        Args:
            packages: List of MigrationPackage objects
            output_file: Path to output Markdown file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Migration Packages\n\n")
            
            # Summary table
            f.write("## Summary\n\n")
            f.write("| Package | Artifacts | LOC | Complexity | External Deps | Conflicts |\n")
            f.write("|---------|-----------|-----|------------|---------------|----------|\n")
            
            for package in packages:
                f.write(f"| {package.name} | {package.total_artifacts} | "
                       f"{package.total_loc} | {package.total_complexity:.1f} | "
                       f"{len(package.external_dependencies)} | "
                       f"{len(package.conflicts)} |\n")
            
            f.write("\n")
            
            # Detailed package information
            f.write("## Package Details\n\n")
            
            for package in packages:
                f.write(f"### {package.name}\n\n")
                
                if package.description:
                    f.write(f"{package.description}\n\n")
                
                # Metrics
                f.write("**Metrics:**\n")
                f.write(f"- Total Artifacts: {package.total_artifacts}\n")
                f.write(f"- Total LOC: {package.total_loc}\n")
                f.write(f"- Total Complexity: {package.total_complexity:.2f}\n")
                f.write(f"- Priority: {package.priority or 'Not set'}\n")
                f.write(f"- Self-contained: {'Yes' if package.is_self_contained() else 'No'}\n")
                f.write("\n")
                
                # Artifact breakdown
                f.write("**Artifacts by Type:**\n")
                counts = package.get_artifact_count_by_type()
                f.write(f"- Programs: {counts['programs']}\n")
                f.write(f"- Copybooks: {counts['copybooks']}\n")
                f.write(f"- JCL: {counts['jcl']}\n")
                f.write(f"- Datasets: {counts['datasets']}\n")
                f.write("\n")
                
                # External dependencies
                if package.external_dependencies:
                    f.write(f"**External Dependencies ({len(package.external_dependencies)}):**\n")
                    for dep in sorted(package.external_dependencies)[:20]:  # Limit to 20
                        f.write(f"- {dep}\n")
                    if len(package.external_dependencies) > 20:
                        f.write(f"- ... and {len(package.external_dependencies) - 20} more\n")
                    f.write("\n")
                
                # Conflicts
                if package.conflicts:
                    f.write(f"**Conflicts ({len(package.conflicts)}):**\n")
                    for conflict in sorted(package.conflicts):
                        f.write(f"- {conflict}\n")
                    f.write("\n")
                
                f.write("---\n\n")
    
    def export_summary_to_csv(self, packages: List[MigrationPackage], output_file: str) -> None:
        """
        Export package summary to CSV (one row per package).
        
        Args:
            packages: List of MigrationPackage objects
            output_file: Path to output CSV file
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Package Name',
                'Priority',
                'Total Artifacts',
                'Programs',
                'Copybooks',
                'JCL',
                'Datasets',
                'Total LOC',
                'Total Complexity',
                'External Dependencies',
                'Conflicts',
                'Self Contained',
                'Created Date',
                'Description'
            ])
            
            # Write data
            for package in packages:
                counts = package.get_artifact_count_by_type()
                
                writer.writerow([
                    package.name,
                    package.priority or '',
                    package.total_artifacts,
                    counts['programs'],
                    counts['copybooks'],
                    counts['jcl'],
                    counts['datasets'],
                    package.total_loc,
                    f"{package.total_complexity:.2f}",
                    len(package.external_dependencies),
                    len(package.conflicts),
                    'Yes' if package.is_self_contained() else 'No',
                    package.created_date.isoformat() if package.created_date else '',
                    package.description or ''
                ])
    
    def export_conflicts_to_csv(self, packages: List[MigrationPackage], output_file: str) -> None:
        """
        Export package conflicts to CSV.
        
        Args:
            packages: List of MigrationPackage objects
            output_file: Path to output CSV file
        """
        # Collect all conflicts
        artifact_packages: Dict[str, List[str]] = {}
        
        for package in packages:
            for conflict in package.conflicts:
                if conflict not in artifact_packages:
                    artifact_packages[conflict] = []
                artifact_packages[conflict].append(package.name)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Artifact Name',
                'Package Count',
                'Packages'
            ])
            
            # Write data
            for artifact, package_names in sorted(artifact_packages.items()):
                writer.writerow([
                    artifact,
                    len(package_names),
                    ', '.join(sorted(package_names))
                ])
    
    def export_external_deps_to_csv(self, packages: List[MigrationPackage], output_file: str) -> None:
        """
        Export external dependencies to CSV.
        
        Args:
            packages: List of MigrationPackage objects
            output_file: Path to output CSV file
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Package Name',
                'External Dependency',
                'Dependency Type'
            ])
            
            # Write data
            for package in packages:
                for ext_dep in sorted(package.external_dependencies):
                    writer.writerow([
                        package.name,
                        ext_dep,
                        ''  # Dependency type (would need to query)
                    ])
    
    def export_artifacts_to_csv(self, package: MigrationPackage, output_file: str) -> None:
        """
        Export all artifacts in a single package to CSV.
        
        Args:
            package: MigrationPackage object
            output_file: Path to output CSV file
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Artifact Name',
                'Artifact Type'
            ])
            
            # Write programs
            for artifact in sorted(package.programs):
                writer.writerow([artifact, 'PROGRAM'])
            
            # Write copybooks
            for artifact in sorted(package.copybooks):
                writer.writerow([artifact, 'COPYBOOK'])
            
            # Write JCL
            for artifact in sorted(package.jcl):
                writer.writerow([artifact, 'JCL'])
            
            # Write datasets
            for artifact in sorted(package.datasets):
                writer.writerow([artifact, 'DATASET'])
