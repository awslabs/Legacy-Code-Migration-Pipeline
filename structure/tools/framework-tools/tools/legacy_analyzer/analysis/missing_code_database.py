"""Database operations for missing code detection."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.missing_artifact import (
    MissingArtifact,
    MissingArtifactReference,
    CompletenessReport
)


class MissingCodeDatabase:
    """Manages database operations for missing code detection."""
    
    def __init__(self, db_connection):
        """
        Initialize missing code database manager.
        
        Args:
            db_connection: Database connection object (e.g., sqlite3.Connection)
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def create_schema(self) -> None:
        """Create database tables for missing artifacts."""
        
        # Create missing_artifacts table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS missing_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_name VARCHAR(44) NOT NULL,
                artifact_type VARCHAR(20) NOT NULL,
                reference_count INTEGER NOT NULL,
                severity VARCHAR(10) NOT NULL,
                first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(artifact_name, artifact_type)
            )
        """)
        
        # Create missing_artifact_references table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS missing_artifact_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                missing_artifact_id INTEGER NOT NULL,
                missing_artifact VARCHAR(44) NOT NULL,
                missing_artifact_type VARCHAR(20) NOT NULL,
                referenced_by VARCHAR(44) NOT NULL,
                referenced_by_type VARCHAR(20) NOT NULL,
                reference_type VARCHAR(20) NOT NULL,
                source_file VARCHAR(255),
                line_number INTEGER,
                FOREIGN KEY (missing_artifact_id) REFERENCES missing_artifacts(id) ON DELETE CASCADE
            )
        """)
        
        # Create completeness_reports table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS completeness_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                total_referenced_programs INTEGER NOT NULL,
                found_programs INTEGER NOT NULL,
                missing_programs INTEGER NOT NULL,
                program_completeness DECIMAL(5,4) NOT NULL,
                
                total_referenced_copybooks INTEGER NOT NULL,
                found_copybooks INTEGER NOT NULL,
                missing_copybooks INTEGER NOT NULL,
                copybook_completeness DECIMAL(5,4) NOT NULL,
                
                total_referenced_datasets INTEGER NOT NULL,
                found_datasets INTEGER NOT NULL,
                missing_datasets INTEGER NOT NULL,
                dataset_completeness DECIMAL(5,4) NOT NULL,
                
                overall_completeness DECIMAL(5,4) NOT NULL
            )
        """)
        
        # Create indexes for performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_missing_artifacts_name 
            ON missing_artifacts(artifact_name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_missing_artifacts_type 
            ON missing_artifacts(artifact_type)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_missing_artifacts_severity 
            ON missing_artifacts(severity)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_missing_refs_artifact_id 
            ON missing_artifact_references(missing_artifact_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_missing_refs_artifact 
            ON missing_artifact_references(missing_artifact, missing_artifact_type)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_missing_refs_referenced_by 
            ON missing_artifact_references(referenced_by)
        """)
        
        self.conn.commit()
    
    def save_missing_artifact(self, artifact: MissingArtifact) -> int:
        """
        Save a missing artifact to the database.
        
        Args:
            artifact: MissingArtifact object to save
            
        Returns:
            Artifact ID
        """
        # Check if artifact already exists
        self.cursor.execute("""
            SELECT id FROM missing_artifacts
            WHERE artifact_name = ? AND artifact_type = ?
        """, (artifact.artifact_name, artifact.artifact_type))
        
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing artifact
            artifact_id = existing[0]
            self.cursor.execute("""
                UPDATE missing_artifacts
                SET reference_count = ?,
                    severity = ?,
                    last_updated = ?
                WHERE id = ?
            """, (
                artifact.reference_count,
                artifact.severity,
                datetime.now(),
                artifact_id
            ))
        else:
            # Insert new artifact
            self.cursor.execute("""
                INSERT INTO missing_artifacts (
                    artifact_name, artifact_type, reference_count,
                    severity, first_detected, last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                artifact.artifact_name,
                artifact.artifact_type,
                artifact.reference_count,
                artifact.severity,
                artifact.first_detected or datetime.now(),
                datetime.now()
            ))
            artifact_id = self.cursor.lastrowid
        
        self.conn.commit()
        return artifact_id
    
    def save_missing_artifacts(self, artifacts: List[MissingArtifact]) -> None:
        """
        Save multiple missing artifacts to the database.
        
        Args:
            artifacts: List of MissingArtifact objects
        """
        for artifact in artifacts:
            self.save_missing_artifact(artifact)
    
    def save_missing_artifact_reference(
        self,
        reference: MissingArtifactReference
    ) -> int:
        """
        Save a missing artifact reference to the database.
        
        Args:
            reference: MissingArtifactReference object to save
            
        Returns:
            Reference ID
        """
        # Get the missing artifact ID
        self.cursor.execute("""
            SELECT id FROM missing_artifacts
            WHERE artifact_name = ? AND artifact_type = ?
        """, (reference.missing_artifact, reference.missing_artifact_type))
        
        row = self.cursor.fetchone()
        if not row:
            # Artifact doesn't exist, create it first
            artifact = MissingArtifact(
                artifact_name=reference.missing_artifact,
                artifact_type=reference.missing_artifact_type,
                reference_count=1,
                severity="LOW"
            )
            artifact_id = self.save_missing_artifact(artifact)
        else:
            artifact_id = row[0]
        
        # Insert reference
        self.cursor.execute("""
            INSERT INTO missing_artifact_references (
                missing_artifact_id, missing_artifact, missing_artifact_type,
                referenced_by, referenced_by_type, reference_type,
                source_file, line_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact_id,
            reference.missing_artifact,
            reference.missing_artifact_type,
            reference.referenced_by,
            reference.referenced_by_type,
            reference.reference_type,
            reference.source_file,
            reference.line_number
        ))
        
        reference_id = self.cursor.lastrowid
        self.conn.commit()
        
        return reference_id
    
    def save_missing_artifact_references(
        self,
        references: List[MissingArtifactReference]
    ) -> None:
        """
        Save multiple missing artifact references to the database.
        
        Args:
            references: List of MissingArtifactReference objects
        """
        for reference in references:
            self.save_missing_artifact_reference(reference)
    
    def load_missing_artifact(
        self,
        artifact_name: str,
        artifact_type: str
    ) -> Optional[MissingArtifact]:
        """
        Load a missing artifact from the database.
        
        Args:
            artifact_name: Name of the artifact
            artifact_type: Type of the artifact
            
        Returns:
            MissingArtifact object or None if not found
        """
        self.cursor.execute("""
            SELECT artifact_name, artifact_type, reference_count,
                   severity, first_detected
            FROM missing_artifacts
            WHERE artifact_name = ? AND artifact_type = ?
        """, (artifact_name, artifact_type))
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        # Get referenced_by list
        self.cursor.execute("""
            SELECT DISTINCT referenced_by
            FROM missing_artifact_references
            WHERE missing_artifact = ? AND missing_artifact_type = ?
        """, (artifact_name, artifact_type))
        
        referenced_by = [row[0] for row in self.cursor.fetchall()]
        
        artifact = MissingArtifact(
            artifact_name=row[0],
            artifact_type=row[1],
            reference_count=row[2],
            referenced_by=referenced_by,
            severity=row[3],
            first_detected=row[4]
        )
        
        return artifact
    
    def load_all_missing_artifacts(
        self,
        artifact_type: Optional[str] = None
    ) -> List[MissingArtifact]:
        """
        Load all missing artifacts from the database.
        
        Args:
            artifact_type: Optional filter by artifact type
            
        Returns:
            List of MissingArtifact objects
        """
        if artifact_type:
            self.cursor.execute("""
                SELECT artifact_name, artifact_type, reference_count,
                       severity, first_detected
                FROM missing_artifacts
                WHERE artifact_type = ?
                ORDER BY 
                    CASE severity
                        WHEN 'HIGH' THEN 0
                        WHEN 'MEDIUM' THEN 1
                        WHEN 'LOW' THEN 2
                    END,
                    reference_count DESC
            """, (artifact_type,))
        else:
            self.cursor.execute("""
                SELECT artifact_name, artifact_type, reference_count,
                       severity, first_detected
                FROM missing_artifacts
                ORDER BY 
                    CASE severity
                        WHEN 'HIGH' THEN 0
                        WHEN 'MEDIUM' THEN 1
                        WHEN 'LOW' THEN 2
                    END,
                    reference_count DESC
            """)
        
        artifacts = []
        for row in self.cursor.fetchall():
            artifact_name, artifact_type_val, ref_count, severity, first_detected = row
            
            # Get referenced_by list
            self.cursor.execute("""
                SELECT DISTINCT referenced_by
                FROM missing_artifact_references
                WHERE missing_artifact = ? AND missing_artifact_type = ?
            """, (artifact_name, artifact_type_val))
            
            referenced_by = [r[0] for r in self.cursor.fetchall()]
            
            artifact = MissingArtifact(
                artifact_name=artifact_name,
                artifact_type=artifact_type_val,
                reference_count=ref_count,
                referenced_by=referenced_by,
                severity=severity,
                first_detected=first_detected
            )
            
            artifacts.append(artifact)
        
        return artifacts
    
    def load_missing_artifact_references(
        self,
        artifact_name: str,
        artifact_type: str
    ) -> List[MissingArtifactReference]:
        """
        Load all references to a missing artifact.
        
        Args:
            artifact_name: Name of the artifact
            artifact_type: Type of the artifact
            
        Returns:
            List of MissingArtifactReference objects
        """
        self.cursor.execute("""
            SELECT missing_artifact, missing_artifact_type,
                   referenced_by, referenced_by_type, reference_type,
                   source_file, line_number
            FROM missing_artifact_references
            WHERE missing_artifact = ? AND missing_artifact_type = ?
            ORDER BY referenced_by, source_file, line_number
        """, (artifact_name, artifact_type))
        
        references = []
        for row in self.cursor.fetchall():
            ref = MissingArtifactReference(
                missing_artifact=row[0],
                missing_artifact_type=row[1],
                referenced_by=row[2],
                referenced_by_type=row[3],
                reference_type=row[4],
                source_file=row[5],
                line_number=row[6]
            )
            references.append(ref)
        
        return references
    
    def save_completeness_report(self, report: CompletenessReport) -> int:
        """
        Save a completeness report to the database.
        
        Args:
            report: CompletenessReport object to save
            
        Returns:
            Report ID
        """
        self.cursor.execute("""
            INSERT INTO completeness_reports (
                report_date,
                total_referenced_programs, found_programs, missing_programs,
                program_completeness,
                total_referenced_copybooks, found_copybooks, missing_copybooks,
                copybook_completeness,
                total_referenced_datasets, found_datasets, missing_datasets,
                dataset_completeness,
                overall_completeness
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            report.total_referenced_programs,
            report.found_programs,
            report.missing_programs,
            report.program_completeness,
            report.total_referenced_copybooks,
            report.found_copybooks,
            report.missing_copybooks,
            report.copybook_completeness,
            report.total_referenced_datasets,
            report.found_datasets,
            report.missing_datasets,
            report.dataset_completeness,
            report.overall_completeness
        ))
        
        report_id = self.cursor.lastrowid
        self.conn.commit()
        
        return report_id
    
    def load_latest_completeness_report(self) -> Optional[CompletenessReport]:
        """
        Load the most recent completeness report.
        
        Returns:
            CompletenessReport object or None if no reports exist
        """
        self.cursor.execute("""
            SELECT 
                total_referenced_programs, found_programs, missing_programs,
                program_completeness,
                total_referenced_copybooks, found_copybooks, missing_copybooks,
                copybook_completeness,
                total_referenced_datasets, found_datasets, missing_datasets,
                dataset_completeness,
                overall_completeness
            FROM completeness_reports
            ORDER BY report_date DESC
            LIMIT 1
        """)
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        # Load missing artifacts
        missing_artifacts = self.load_all_missing_artifacts()
        
        report = CompletenessReport(
            total_referenced_programs=row[0],
            found_programs=row[1],
            missing_programs=row[2],
            program_completeness=row[3],
            total_referenced_copybooks=row[4],
            found_copybooks=row[5],
            missing_copybooks=row[6],
            copybook_completeness=row[7],
            total_referenced_datasets=row[8],
            found_datasets=row[9],
            missing_datasets=row[10],
            dataset_completeness=row[11],
            overall_completeness=row[12],
            missing_artifacts=missing_artifacts
        )
        
        return report
    
    def delete_missing_artifact(
        self,
        artifact_name: str,
        artifact_type: str
    ) -> bool:
        """
        Delete a missing artifact from the database.
        
        Args:
            artifact_name: Name of the artifact
            artifact_type: Type of the artifact
            
        Returns:
            True if deleted, False if not found
        """
        self.cursor.execute("""
            DELETE FROM missing_artifacts
            WHERE artifact_name = ? AND artifact_type = ?
        """, (artifact_name, artifact_type))
        
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def clear_all_missing_artifacts(self) -> int:
        """
        Clear all missing artifacts from the database.
        
        Returns:
            Number of artifacts deleted
        """
        self.cursor.execute("SELECT COUNT(*) FROM missing_artifacts")
        count = self.cursor.fetchone()[0]
        
        self.cursor.execute("DELETE FROM missing_artifacts")
        self.conn.commit()
        
        return count
    
    def get_missing_artifact_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about missing artifacts.
        
        Returns:
            Dictionary with statistics
        """
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_missing,
                SUM(CASE WHEN artifact_type = 'PROGRAM' THEN 1 ELSE 0 END) as missing_programs,
                SUM(CASE WHEN artifact_type = 'COPYBOOK' THEN 1 ELSE 0 END) as missing_copybooks,
                SUM(CASE WHEN artifact_type = 'DATASET' THEN 1 ELSE 0 END) as missing_datasets,
                SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high_severity,
                SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) as medium_severity,
                SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) as low_severity,
                SUM(reference_count) as total_references
            FROM missing_artifacts
        """)
        
        row = self.cursor.fetchone()
        
        return {
            'total_missing': row[0] or 0,
            'missing_programs': row[1] or 0,
            'missing_copybooks': row[2] or 0,
            'missing_datasets': row[3] or 0,
            'high_severity': row[4] or 0,
            'medium_severity': row[5] or 0,
            'low_severity': row[6] or 0,
            'total_references': row[7] or 0
        }
