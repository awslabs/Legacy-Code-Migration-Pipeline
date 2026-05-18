"""Report generator for legacy analyzer."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models.flow import ProgramFlow, CallGraph
from ..models.complexity import ComplexityMetrics
from ..models.package import MigrationPackage
from ..models.missing_artifact import MissingArtifact


class AnalysisResults:
    """Container for analysis results."""
    
    def __init__(
        self,
        total_artifacts: int = 0,
        total_programs: int = 0,
        total_copybooks: int = 0,
        total_datasets: int = 0,
        complexity_distribution: Optional[Dict[str, int]] = None,
        missing_artifacts_count: int = 0,
        circular_dependencies_count: int = 0,
        flows: Optional[Dict[str, ProgramFlow]] = None,
        complexity_metrics: Optional[Dict[str, ComplexityMetrics]] = None,
        missing_artifacts: Optional[List[MissingArtifact]] = None,
        packages: Optional[List[MigrationPackage]] = None,
        dependency_completeness: Optional[float] = None,
        # CICS metadata
        total_cics_transactions: int = 0,
        total_cics_programs: int = 0,
        cics_groups: Optional[List[str]] = None,
        entry_points_by_type: Optional[Dict[str, int]] = None,
        entry_points_by_confidence: Optional[Dict[str, int]] = None,
        enabled_transactions: int = 0,
        disabled_transactions: int = 0
    ):
        """Initialize analysis results."""
        self.total_artifacts = total_artifacts
        self.total_programs = total_programs
        self.total_copybooks = total_copybooks
        self.total_datasets = total_datasets
        self.complexity_distribution = complexity_distribution or {}
        self.missing_artifacts_count = missing_artifacts_count
        self.circular_dependencies_count = circular_dependencies_count
        self.flows = flows or {}
        self.complexity_metrics = complexity_metrics or {}
        self.missing_artifacts = missing_artifacts or []
        self.packages = packages or []
        self.dependency_completeness = dependency_completeness
        # CICS metadata
        self.total_cics_transactions = total_cics_transactions
        self.total_cics_programs = total_cics_programs
        self.cics_groups = cics_groups or []
        self.entry_points_by_type = entry_points_by_type or {}
        self.entry_points_by_confidence = entry_points_by_confidence or {}
        self.enabled_transactions = enabled_transactions
        self.disabled_transactions = disabled_transactions


class ReportGenerator:
    """Generates various reports for legacy analyzer."""
    
    def __init__(self):
        """Initialize report generator."""
        pass
    
    def generate_executive_summary(
        self,
        analysis_results: AnalysisResults
    ) -> str:
        """
        Generate executive summary report.
        
        Args:
            analysis_results: Complete analysis results
            
        Returns:
            Executive summary as formatted text
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("LEGACY ANALYZER - EXECUTIVE SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Inventory Overview
        lines.append("INVENTORY OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Total Artifacts:     {analysis_results.total_artifacts:,}")
        lines.append(f"  Programs:          {analysis_results.total_programs:,}")
        lines.append(f"  Copybooks:         {analysis_results.total_copybooks:,}")
        lines.append(f"  Datasets:          {analysis_results.total_datasets:,}")
        lines.append("")
        
        # Complexity Distribution
        if analysis_results.complexity_distribution:
            lines.append("COMPLEXITY DISTRIBUTION")
            lines.append("-" * 80)
            total_analyzed = sum(analysis_results.complexity_distribution.values())
            for tier in ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']:
                count = analysis_results.complexity_distribution.get(tier, 0)
                percentage = (count / total_analyzed * 100) if total_analyzed > 0 else 0
                lines.append(f"  {tier:12} {count:6,} ({percentage:5.1f}%)")
            lines.append(f"  {'Total':12} {total_analyzed:6,}")
            lines.append("")
        
        # Missing Artifacts
        lines.append("MISSING ARTIFACTS")
        lines.append("-" * 80)
        lines.append(f"Total Missing:       {analysis_results.missing_artifacts_count:,}")
        
        if analysis_results.missing_artifacts:
            # Count by type
            by_type = {}
            by_severity = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            
            for artifact in analysis_results.missing_artifacts:
                by_type[artifact.artifact_type] = by_type.get(artifact.artifact_type, 0) + 1
                by_severity[artifact.severity] = by_severity.get(artifact.severity, 0) + 1
            
            lines.append("")
            lines.append("By Type:")
            for artifact_type, count in sorted(by_type.items()):
                lines.append(f"  {artifact_type:12} {count:6,}")
            
            lines.append("")
            lines.append("By Severity:")
            for severity in ['HIGH', 'MEDIUM', 'LOW']:
                count = by_severity.get(severity, 0)
                lines.append(f"  {severity:12} {count:6,}")
        
        lines.append("")
        
        # Circular Dependencies
        lines.append("CIRCULAR DEPENDENCIES")
        lines.append("-" * 80)
        lines.append(f"Total Cycles:        {analysis_results.circular_dependencies_count:,}")
        lines.append("")
        
        # CICS Transactions
        if analysis_results.total_cics_transactions > 0:
            lines.append("CICS TRANSACTIONS")
            lines.append("-" * 80)
            lines.append(f"Total Transactions:  {analysis_results.total_cics_transactions:,}")
            lines.append(f"  Enabled:           {analysis_results.enabled_transactions:,}")
            lines.append(f"  Disabled:          {analysis_results.disabled_transactions:,}")
            lines.append(f"CICS Programs:       {analysis_results.total_cics_programs:,}")
            
            if analysis_results.cics_groups:
                lines.append(f"CICS Groups:         {len(analysis_results.cics_groups):,}")
                if len(analysis_results.cics_groups) <= 5:
                    for group in sorted(analysis_results.cics_groups):
                        lines.append(f"  • {group}")
            lines.append("")
        
        # Entry Point Breakdown
        if analysis_results.entry_points_by_type:
            lines.append("ENTRY POINTS BY TYPE")
            lines.append("-" * 80)
            total_entry_points = sum(analysis_results.entry_points_by_type.values())
            lines.append(f"Total Entry Points:  {total_entry_points:,}")
            lines.append("")
            
            for entry_type in ['ONLINE', 'BATCH', 'INFERRED']:
                count = analysis_results.entry_points_by_type.get(entry_type, 0)
                percentage = (count / total_entry_points * 100) if total_entry_points > 0 else 0
                lines.append(f"  {entry_type:12} {count:6,} ({percentage:5.1f}%)")
            lines.append("")
        
        # Confidence Level Statistics
        if analysis_results.entry_points_by_confidence:
            lines.append("ENTRY POINT CONFIDENCE")
            lines.append("-" * 80)
            total_entry_points = sum(analysis_results.entry_points_by_confidence.values())
            
            for confidence in ['EXPLICIT', 'INFERRED']:
                count = analysis_results.entry_points_by_confidence.get(confidence, 0)
                percentage = (count / total_entry_points * 100) if total_entry_points > 0 else 0
                lines.append(f"  {confidence:12} {count:6,} ({percentage:5.1f}%)")
            lines.append("")
        
        # Migration Packages
        if analysis_results.packages:
            lines.append("MIGRATION PACKAGES")
            lines.append("-" * 80)
            lines.append(f"Total Packages:      {len(analysis_results.packages):,}")
            
            total_artifacts_in_packages = sum(len(pkg.artifacts) for pkg in analysis_results.packages)
            total_loc = sum(pkg.total_loc for pkg in analysis_results.packages)
            
            lines.append(f"Total Artifacts:     {total_artifacts_in_packages:,}")
            lines.append(f"Total LOC:           {total_loc:,}")
            lines.append("")
        
        # Key Findings
        lines.append("KEY FINDINGS")
        lines.append("-" * 80)
        
        findings = []
        
        # High complexity programs
        if analysis_results.complexity_metrics:
            high_complexity = [
                name for name, metrics in analysis_results.complexity_metrics.items()
                if metrics.complexity_tier in ['HIGH', 'VERY_HIGH']
            ]
            if high_complexity:
                findings.append(f"• {len(high_complexity)} programs have HIGH or VERY_HIGH complexity")
        
        # Missing artifacts
        if analysis_results.missing_artifacts_count > 0:
            completeness = (
                (analysis_results.total_artifacts - analysis_results.missing_artifacts_count) /
                analysis_results.total_artifacts * 100
            ) if analysis_results.total_artifacts > 0 else 100
            findings.append(f"• Inventory completeness: {completeness:.1f}%")
        
        # Circular dependencies
        if analysis_results.circular_dependencies_count > 0:
            findings.append(f"• {analysis_results.circular_dependencies_count} circular dependencies detected")
        
        if not findings:
            findings.append("• No critical issues detected")
        
        for finding in findings:
            lines.append(finding)
        
        lines.append("")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def generate_artifact_report(
        self,
        artifact_name: str,
        complexity_metrics: Optional[ComplexityMetrics] = None,
        flow: Optional[ProgramFlow] = None,
        callers: Optional[List[str]] = None,
        callees: Optional[List[str]] = None,
        copybooks: Optional[List[str]] = None,
        datasets: Optional[List[str]] = None,
        package_assignment: Optional[str] = None
    ) -> str:
        """
        Generate detailed artifact report.
        
        Args:
            artifact_name: Name of the artifact
            complexity_metrics: Complexity metrics for the artifact
            flow: Program flow starting from this artifact
            callers: List of programs that call this artifact
            callees: List of programs called by this artifact
            copybooks: List of copybooks used by this artifact
            datasets: List of datasets accessed by this artifact
            package_assignment: Migration package this artifact belongs to
            
        Returns:
            Detailed artifact report as formatted text
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"ARTIFACT REPORT: {artifact_name}")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Complexity Metrics
        if complexity_metrics:
            lines.append("COMPLEXITY METRICS")
            lines.append("-" * 80)
            lines.append(f"Language:            {complexity_metrics.language}")
            lines.append(f"Lines of Code:       {complexity_metrics.lines_of_code:,}")
            lines.append(f"Cyclomatic:          {complexity_metrics.cyclomatic_complexity}")
            lines.append(f"Dependencies In:     {complexity_metrics.dependency_count_in}")
            lines.append(f"Dependencies Out:    {complexity_metrics.dependency_count_out}")
            lines.append(f"Composite Score:     {complexity_metrics.composite_score:.2f}")
            lines.append(f"Complexity Tier:     {complexity_metrics.complexity_tier}")
            
            if complexity_metrics.is_god_program:
                lines.append("")
                lines.append("⚠️  WARNING: This is a 'god program' with excessive complexity!")
            
            lines.append("")
        
        # Dependencies
        lines.append("DEPENDENCIES")
        lines.append("-" * 80)
        
        if callers:
            lines.append(f"Called By ({len(callers)}):")
            for caller in sorted(callers)[:10]:  # Show first 10
                lines.append(f"  • {caller}")
            if len(callers) > 10:
                lines.append(f"  ... and {len(callers) - 10} more")
        else:
            lines.append("Called By: None (Entry Point)")
        
        lines.append("")
        
        if callees:
            lines.append(f"Calls ({len(callees)}):")
            for callee in sorted(callees)[:10]:  # Show first 10
                lines.append(f"  • {callee}")
            if len(callees) > 10:
                lines.append(f"  ... and {len(callees) - 10} more")
        else:
            lines.append("Calls: None (Leaf Program)")
        
        lines.append("")
        
        # Copybooks
        if copybooks:
            lines.append(f"Copybooks ({len(copybooks)}):")
            for copybook in sorted(copybooks)[:10]:
                lines.append(f"  • {copybook}")
            if len(copybooks) > 10:
                lines.append(f"  ... and {len(copybooks) - 10} more")
            lines.append("")
        
        # Datasets
        if datasets:
            lines.append(f"Datasets ({len(datasets)}):")
            for dataset in sorted(datasets)[:10]:
                lines.append(f"  • {dataset}")
            if len(datasets) > 10:
                lines.append(f"  ... and {len(datasets) - 10} more")
            lines.append("")
        
        # Program Flow
        if flow:
            lines.append("PROGRAM FLOW")
            lines.append("-" * 80)
            lines.append(f"Maximum Depth:       {flow.depth}")
            lines.append(f"Total Programs:      {len(flow.programs)}")
            lines.append(f"Total Copybooks:     {flow.total_copybooks}")
            lines.append(f"Total Datasets:      {flow.total_datasets}")
            
            if flow.circular_dependencies:
                lines.append(f"Circular Deps:       {len(flow.circular_dependencies)}")
            
            lines.append("")
        
        # Package Assignment
        if package_assignment:
            lines.append("MIGRATION PACKAGE")
            lines.append("-" * 80)
            lines.append(f"Assigned To:         {package_assignment}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def generate_package_report(
        self,
        package: MigrationPackage
    ) -> str:
        """
        Generate migration package report.
        
        Args:
            package: Migration package to report on
            
        Returns:
            Package report as formatted text
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"MIGRATION PACKAGE REPORT: {package.name}")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Package Summary
        lines.append("PACKAGE SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Artifacts:     {len(package.artifacts):,}")
        lines.append(f"Total LOC:           {package.total_loc:,}")
        lines.append(f"Total Complexity:    {package.total_complexity:.2f}")
        lines.append("")
        
        # External Dependencies
        if package.external_dependencies:
            lines.append("EXTERNAL DEPENDENCIES")
            lines.append("-" * 80)
            lines.append(f"Count:               {len(package.external_dependencies):,}")
            lines.append("")
            lines.append("Dependencies:")
            for dep in sorted(package.external_dependencies)[:20]:
                lines.append(f"  • {dep}")
            if len(package.external_dependencies) > 20:
                lines.append(f"  ... and {len(package.external_dependencies) - 20} more")
            lines.append("")
        else:
            lines.append("EXTERNAL DEPENDENCIES")
            lines.append("-" * 80)
            lines.append("✓ Package is self-contained (no external dependencies)")
            lines.append("")
        
        # Conflicts
        if package.conflicts:
            lines.append("CONFLICTS")
            lines.append("-" * 80)
            lines.append(f"Count:               {len(package.conflicts):,}")
            lines.append("")
            lines.append("Artifacts in multiple packages:")
            for conflict in sorted(package.conflicts):
                lines.append(f"  ⚠️  {conflict}")
            lines.append("")
        
        # Artifacts List
        lines.append("ARTIFACTS IN PACKAGE")
        lines.append("-" * 80)
        
        # Group by type if possible
        artifacts_by_type = {}
        for artifact in package.artifacts:
            # Try to infer type from name or use generic
            artifact_type = "ARTIFACT"
            artifacts_by_type.setdefault(artifact_type, []).append(artifact)
        
        for artifact_type, artifacts in sorted(artifacts_by_type.items()):
            lines.append(f"{artifact_type}S ({len(artifacts)}):")
            for artifact in sorted(artifacts)[:20]:
                lines.append(f"  • {artifact}")
            if len(artifacts) > 20:
                lines.append(f"  ... and {len(artifacts) - 20} more")
            lines.append("")
        
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def generate_complexity_summary(
        self,
        complexity_metrics: Dict[str, ComplexityMetrics],
        top_n: int = 10
    ) -> str:
        """
        Generate complexity summary report.
        
        Args:
            complexity_metrics: Dictionary of complexity metrics
            top_n: Number of top complex programs to show
            
        Returns:
            Complexity summary as formatted text
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("COMPLEXITY SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Distribution
        distribution = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'VERY_HIGH': 0}
        for metrics in complexity_metrics.values():
            distribution[metrics.complexity_tier] += 1
        
        lines.append("DISTRIBUTION")
        lines.append("-" * 80)
        total = sum(distribution.values())
        for tier in ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']:
            count = distribution[tier]
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"{tier:12} {count:6,} ({percentage:5.1f}%)")
        lines.append("")
        
        # Top Complex Programs
        sorted_metrics = sorted(
            complexity_metrics.values(),
            key=lambda m: m.composite_score,
            reverse=True
        )
        
        lines.append(f"TOP {top_n} MOST COMPLEX PROGRAMS")
        lines.append("-" * 80)
        lines.append(f"{'Program':<20} {'LOC':>8} {'Cyclo':>6} {'Deps':>6} {'Score':>8} {'Tier':<12}")
        lines.append("-" * 80)
        
        for metrics in sorted_metrics[:top_n]:
            total_deps = metrics.dependency_count_in + metrics.dependency_count_out
            lines.append(
                f"{metrics.program_name:<20} "
                f"{metrics.lines_of_code:>8,} "
                f"{metrics.cyclomatic_complexity:>6} "
                f"{total_deps:>6} "
                f"{metrics.composite_score:>8.2f} "
                f"{metrics.complexity_tier:<12}"
            )
        
        lines.append("")
        
        # God Programs
        god_programs = [m for m in complexity_metrics.values() if m.is_god_program]
        if god_programs:
            lines.append("GOD PROGRAMS (Excessive Complexity)")
            lines.append("-" * 80)
            for metrics in god_programs:
                lines.append(f"  ⚠️  {metrics.program_name} - {metrics.complexity_tier}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return '\n'.join(lines)
