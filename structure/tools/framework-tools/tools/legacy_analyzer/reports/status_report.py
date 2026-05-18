"""
Status report generation for legacy analyzer.

Generates source_analysis_status.json file with analysis progress and metadata.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class StatusReportGenerator:
    """Generates status reports from analysis database."""
    
    def __init__(self, db_path: str, output_dir: str, project_name: Optional[str] = None):
        """
        Initialize with database path and output directory.
        
        Args:
            db_path: Path to SQLite database
            output_dir: Base output directory (where flows/, jobs/, reports/ exist)
            project_name: Optional project name (defaults to database filename)
        """
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.project_name = project_name or self.db_path.stem
        self.conn = None
    
    def generate(self, output_path: Optional[str] = None) -> None:
        """
        Generate status report and write to file.
        
        Args:
            output_path: Optional custom output path (defaults to progress/source_analysis_status.json)
        
        Raises:
            FileNotFoundError: If database doesn't exist
            sqlite3.Error: If database query fails
            IOError: If output file cannot be written
        """
        # Validate database exists
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        try:
            # Gather statistics
            stats = self._gather_statistics()
            
            # Build status report
            status_report = self._build_status_report(stats)
            
            # Determine output path
            if output_path is None:
                output_path = self.output_dir / "progress" / "source_analysis_status.json"
            else:
                output_path = Path(output_path)
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(status_report, f, indent=2, ensure_ascii=False)
            
        finally:
            if self.conn:
                self.conn.close()
    
    def _gather_statistics(self) -> dict:
        """Gather statistics from database."""
        stats = {}
        
        # Total artifacts
        try:
            cursor = self.conn.execute("SELECT COUNT(*) as count FROM inventory")
            stats['total_artifacts'] = cursor.fetchone()['count']
        except sqlite3.OperationalError:
            stats['total_artifacts'] = 0
        
        # Analyzed artifacts (those with dependencies or in flows)
        try:
            cursor = self.conn.execute("""
                SELECT COUNT(DISTINCT source_artifact_name) as count 
                FROM artifact_dependencies
            """)
            stats['analyzed_artifacts'] = cursor.fetchone()['count']
        except sqlite3.OperationalError:
            stats['analyzed_artifacts'] = 0
        
        # Total dependencies
        try:
            cursor = self.conn.execute("SELECT COUNT(*) as count FROM artifact_dependencies")
            stats['total_dependencies'] = cursor.fetchone()['count']
        except sqlite3.OperationalError:
            stats['total_dependencies'] = 0
        
        # Entry points
        try:
            cursor = self.conn.execute("SELECT COUNT(*) as count FROM entry_points")
            stats['entry_points'] = cursor.fetchone()['count']
        except sqlite3.OperationalError:
            stats['entry_points'] = 0
        
        # Business flows
        try:
            cursor = self.conn.execute("SELECT COUNT(*) as count FROM migration_flows")
            stats['business_flows'] = cursor.fetchone()['count']
        except sqlite3.OperationalError:
            stats['business_flows'] = 0
        
        # JCL jobs
        try:
            cursor = self.conn.execute("""
                SELECT COUNT(*) as count 
                FROM inventory 
                WHERE language = 'JCL'
            """)
            stats['jcl_jobs'] = cursor.fetchone()['count']
        except sqlite3.OperationalError:
            stats['jcl_jobs'] = 0
        
        return stats
    
    def _build_status_report(self, stats: dict) -> dict:
        """Build the status report structure."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Build artifact paths relative to output_dir
        artifacts = {
            "database": str(self.db_path),
            "entryPoints": str(self.output_dir / "entry_points" / "entry_points.json"),
            "businessFlows": str(self.output_dir / "flows" / "Business_Flows.json"),
            "jobs": str(self.output_dir / "jobs" / "jobs.json"),
            "summaryReport": str(self.output_dir / "reports" / "analysis_summary.md")
        }
        
        # Build status report
        status_report = {
            "metadata": {
                "projectName": self.project_name,
                "phase": "SOURCE_ANALYSIS",
                "lastUpdated": now,
                "version": "1.0"
            },
            "status": "completed",
            "summary": {
                "totalArtifacts": stats['total_artifacts'],
                "analyzedArtifacts": stats['analyzed_artifacts'],
                "totalDependencies": stats['total_dependencies'],
                "entryPoints": stats['entry_points'],
                "businessFlows": stats['business_flows'],
                "jclJobs": stats['jcl_jobs']
            },
            "artifacts": artifacts,
            "completedAt": now
        }
        
        return status_report


def generate_status_report(
    db_path: str,
    output_dir: str,
    output_path: Optional[str] = None,
    project_name: Optional[str] = None
) -> None:
    """
    Generate status report from analysis database.
    
    Args:
        db_path: Path to SQLite database
        output_dir: Base output directory (where flows/, jobs/, reports/ exist)
        output_path: Optional custom output path (defaults to progress/source_analysis_status.json)
        project_name: Optional project name (defaults to database filename)
    
    Raises:
        FileNotFoundError: If database doesn't exist
        sqlite3.Error: If database query fails
        IOError: If output file cannot be written
    """
    generator = StatusReportGenerator(db_path, output_dir, project_name)
    generator.generate(output_path)
