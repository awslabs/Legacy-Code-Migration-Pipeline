"""Summary report generation for legacy analyzer.

Generates comprehensive analysis summary reports in Markdown format from
the analysis database. This module provides functionality to extract and
format statistics about inventory, dependencies, CICS resources, programs,
and migration flows.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional


class SummaryReportGenerator:
    """Generates summary reports from analysis database.
    
    This class queries the analysis database to extract statistics and
    generates a comprehensive summary report in Markdown format.
    """
    
    def __init__(self, db_path: str):
        """Initialize the summary report generator.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def _get_inventory_stats(self) -> Dict[str, Any]:
        """Query inventory statistics from the database.

        Extracts total artifact count and breakdown by language from the
        inventory table. Handles missing table gracefully by returning
        empty statistics.

        Returns:
            Dictionary containing:
                - total: Total number of artifacts
                - by_language: Dictionary mapping language to count

        Raises:
            sqlite3.Error: If database query fails (except for missing table)
        """
        stats = {
            'total': 0,
            'by_language': {}
        }

        try:
            # Query total artifacts count
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory")
            result = cursor.fetchone()
            stats['total'] = result[0] if result else 0

            # Query artifacts by language
            cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM inventory
                GROUP BY language
                ORDER BY count DESC
            """)
            stats['by_language'] = {row[0]: row[1] for row in cursor.fetchall()}

        except sqlite3.OperationalError as e:
            # Handle missing table gracefully
            if 'no such table' in str(e).lower():
                # Return empty stats if table doesn't exist
                pass
            else:
                # Re-raise other operational errors
                raise

        return stats

    def _get_dependency_stats(self) -> Dict[str, Any]:
        """Query dependency statistics from the database.

        Extracts total dependency count and breakdown by dependency type from
        the artifact_dependencies table. Handles missing table gracefully by
        returning empty statistics.

        Returns:
            Dictionary containing:
                - total: Total number of dependencies
                - by_type: Dictionary mapping dependency type to count

        Raises:
            sqlite3.Error: If database query fails (except for missing table)
        """
        stats = {
            'total': 0,
            'by_type': {}
        }

        try:
            # Query total dependencies count
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM artifact_dependencies")
            result = cursor.fetchone()
            stats['total'] = result[0] if result else 0

            # Query dependencies by type
            cursor.execute("""
                SELECT dependency_type, COUNT(*) as count
                FROM artifact_dependencies
                GROUP BY dependency_type
                ORDER BY count DESC
            """)
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

        except sqlite3.OperationalError as e:
            # Handle missing table gracefully
            if 'no such table' in str(e).lower():
                # Return empty stats if table doesn't exist
                pass
            else:
                # Re-raise other operational errors
                raise

        return stats

    def _get_cics_stats(self) -> Dict[str, Any]:
        """Query CICS resource statistics from the database.

        Extracts total CICS resource count and breakdown by resource type from
        the inventory_cics table. Handles missing table gracefully by returning
        empty statistics.

        Returns:
            Dictionary containing:
                - total: Total number of CICS resources
                - by_type: Dictionary mapping resource type to count

        Raises:
            sqlite3.Error: If database query fails (except for missing table)
        """
        stats = {
            'total': 0,
            'by_type': {}
        }

        try:
            # Query total CICS resources count
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory_cics")
            result = cursor.fetchone()
            stats['total'] = result[0] if result else 0

            # Query CICS resources by type
            cursor.execute("""
                SELECT resource_type, COUNT(*) as count
                FROM inventory_cics
                GROUP BY resource_type
                ORDER BY count DESC
            """)
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

        except sqlite3.OperationalError as e:
            # Handle missing table gracefully
            if 'no such table' in str(e).lower():
                # Return empty stats if table doesn't exist
                pass
            else:
                # Re-raise other operational errors
                raise

        return stats

    def _get_program_stats(self) -> Dict[str, Any]:
        """Query program statistics from the database.

        Extracts total program count from the inventory_programs table.
        Handles missing table gracefully by returning empty statistics.

        Returns:
            Dictionary containing:
                - total: Total number of programs

        Raises:
            sqlite3.Error: If database query fails (except for missing table)
        """
        stats = {
            'total': 0
        }

        try:
            # Query total programs count
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory_programs")
            result = cursor.fetchone()
            stats['total'] = result[0] if result else 0

        except sqlite3.OperationalError as e:
            # Handle missing table gracefully
            if 'no such table' in str(e).lower():
                # Return empty stats if table doesn't exist
                pass
            else:
                # Re-raise other operational errors
                raise

        return stats

    def _get_migration_flow_stats(self) -> Dict[str, Any]:
        """Query migration flow statistics from the database.

        Extracts total migration flow count and breakdown by complexity tier
        from the migration_flows table. Handles missing table gracefully by
        returning empty statistics.

        Returns:
            Dictionary containing:
                - total: Total number of migration flows
                - by_complexity: Dictionary mapping complexity tier to count

        Raises:
            sqlite3.Error: If database query fails (except for missing table)
        """
        stats = {
            'total': 0,
            'by_complexity': {}
        }

        try:
            # Query total migration flows count
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM migration_flows")
            result = cursor.fetchone()
            stats['total'] = result[0] if result else 0

            # Query flows by complexity tier
            cursor.execute("""
                SELECT complexity_tier, COUNT(*) as count
                FROM migration_flows
                GROUP BY complexity_tier
                ORDER BY count DESC
            """)
            stats['by_complexity'] = {row[0]: row[1] for row in cursor.fetchall()}

        except sqlite3.OperationalError as e:
            # Handle missing table gracefully
            if 'no such table' in str(e).lower():
                # Return empty stats if table doesn't exist
                pass
            else:
                # Re-raise other operational errors
                raise

        return stats

    def _format_markdown(
        self,
        inventory_stats: Dict[str, Any],
        dependency_stats: Dict[str, Any],
        cics_stats: Dict[str, Any],
        program_stats: Dict[str, Any],
        migration_flow_stats: Dict[str, Any]
    ) -> str:
        """Format statistics as Markdown report.

        Generates a comprehensive Markdown report with sections for inventory,
        dependencies, CICS resources, programs, and migration flows. Sections
        with no data are conditionally included.

        Args:
            inventory_stats: Inventory statistics dictionary
            dependency_stats: Dependency statistics dictionary
            cics_stats: CICS resource statistics dictionary
            program_stats: Program statistics dictionary
            migration_flow_stats: Migration flow statistics dictionary

        Returns:
            Complete Markdown report as a string
        """
        lines = []

        # 1.8.1 Create Markdown header
        lines.append("# Analysis Summary Report")
        lines.append("")

        # 1.8.2 Format inventory statistics section
        lines.append("## Inventory Statistics")
        lines.append("")
        lines.append(f"**Total Artifacts:** {inventory_stats['total']}")
        lines.append("")

        if inventory_stats['by_language']:
            lines.append("### By Language")
            lines.append("")
            lines.append("| Language | Count |")
            lines.append("|----------|-------|")
            for language, count in inventory_stats['by_language'].items():
                lines.append(f"| {language} | {count} |")
            lines.append("")

        # 1.8.3 Format dependency statistics section
        lines.append("## Dependency Statistics")
        lines.append("")
        lines.append(f"**Total Dependencies:** {dependency_stats['total']}")
        lines.append("")

        if dependency_stats['by_type']:
            lines.append("### By Type")
            lines.append("")
            lines.append("| Type | Count |")
            lines.append("|------|-------|")
            for dep_type, count in dependency_stats['by_type'].items():
                lines.append(f"| {dep_type} | {count} |")
            lines.append("")

        # 1.8.4 Format CICS resources section (if data exists)
        if cics_stats['total'] > 0:
            lines.append("## CICS Resources")
            lines.append("")
            lines.append(f"**Total CICS Resources:** {cics_stats['total']}")
            lines.append("")

            if cics_stats['by_type']:
                lines.append("### By Resource Type")
                lines.append("")
                lines.append("| Resource Type | Count |")
                lines.append("|---------------|-------|")
                for resource_type, count in cics_stats['by_type'].items():
                    lines.append(f"| {resource_type} | {count} |")
                lines.append("")

        # 1.8.5 Format programs section
        lines.append("## Programs")
        lines.append("")
        lines.append(f"**Total Programs:** {program_stats['total']}")
        lines.append("")

        # 1.8.6 Format migration flows section (if data exists)
        if migration_flow_stats['total'] > 0:
            lines.append("## Migration Flows")
            lines.append("")
            lines.append(f"**Total Migration Flows:** {migration_flow_stats['total']}")
            lines.append("")

            if migration_flow_stats['by_complexity']:
                lines.append("### By Complexity")
                lines.append("")
                lines.append("| Complexity | Count |")
                lines.append("|------------|-------|")
                for complexity, count in migration_flow_stats['by_complexity'].items():
                    lines.append(f"| {complexity} | {count} |")
                lines.append("")

        # 1.8.7 Return complete Markdown string
        return "\n".join(lines)

    def generate(self, output_path: str) -> None:
        """Generate summary report and write to file.

        This method orchestrates the entire report generation process:
        1. Validates the database path exists
        2. Connects to the database
        3. Queries all statistics
        4. Formats the report as Markdown
        5. Creates output directory if needed
        6. Writes the report to file
        7. Closes the database connection

        Args:
            output_path: Path where the Markdown report should be written

        Raises:
            FileNotFoundError: If the database file doesn't exist
            sqlite3.Error: If database operations fail
            IOError: If the output file cannot be written
            PermissionError: If lacking permissions to write output file
        """
        try:
            # 1.9.1 Validate database path exists
            db_file = Path(self.db_path)
            if not db_file.exists():
                raise FileNotFoundError(
                    f"Database file not found: {self.db_path}"
                )
            if not db_file.is_file():
                raise ValueError(
                    f"Database path is not a file: {self.db_path}"
                )

            # 1.9.2 Connect to database
            try:
                self.conn = sqlite3.connect(self.db_path)
            except sqlite3.Error as e:
                raise sqlite3.Error(
                    f"Failed to connect to database {self.db_path}: {e}"
                ) from e

            # 1.9.3 Call all statistics methods
            try:
                inventory_stats = self._get_inventory_stats()
                dependency_stats = self._get_dependency_stats()
                cics_stats = self._get_cics_stats()
                program_stats = self._get_program_stats()
                migration_flow_stats = self._get_migration_flow_stats()
            except sqlite3.Error as e:
                raise sqlite3.Error(
                    f"Failed to query statistics from database: {e}"
                ) from e

            # 1.9.4 Format as Markdown
            markdown_content = self._format_markdown(
                inventory_stats,
                dependency_stats,
                cics_stats,
                program_stats,
                migration_flow_stats
            )

            # 1.9.5 Create output directory if needed
            output_file = Path(output_path)
            output_dir = output_file.parent

            if output_dir and not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise IOError(
                        f"Failed to create output directory {output_dir}: {e}"
                    ) from e

            # 1.9.6 Write to output file
            try:
                output_file.write_text(markdown_content, encoding='utf-8')
            except (IOError, OSError, PermissionError) as e:
                raise IOError(
                    f"Failed to write report to {output_path}: {e}"
                ) from e

        finally:
            # 1.9.7 Close database connection
            if self.conn is not None:
                try:
                    self.conn.close()
                except sqlite3.Error:
                    # Ignore errors during cleanup
                    pass
                finally:
                    self.conn = None


def generate_summary_report(db_path: str, output_path: str) -> None:
    """Generate summary report from analysis database.
    
    This is a convenience function that creates a SummaryReportGenerator
    instance and generates a summary report in Markdown format. The report
    includes statistics about inventory, dependencies, CICS resources,
    programs, and migration flows.
    
    Args:
        db_path: Path to the SQLite database file containing analysis results
        output_path: Path where the Markdown report should be written
    
    Raises:
        FileNotFoundError: If the database file doesn't exist
        ValueError: If the database path is not a file
        sqlite3.Error: If database connection or query operations fail
        IOError: If the output file cannot be written
        PermissionError: If lacking permissions to write the output file
    
    Example:
        >>> generate_summary_report(
        ...     'analysis.db',
        ...     'reports/analysis_summary.md'
        ... )
    """
    generator = SummaryReportGenerator(db_path)
    generator.generate(output_path)




