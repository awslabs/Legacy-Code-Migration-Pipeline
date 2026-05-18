"""Missing code detector for identifying artifacts not in inventory."""

from typing import List, Dict, Set, Optional
from datetime import datetime
from ..models.dependency import Dependency, DependencyType
from ..models.missing_artifact import (
    MissingArtifact,
    MissingArtifactReference,
    CompletenessReport,
    SeverityThreshold
)


class MissingCodeDetector:
    """Detects artifacts referenced in code but not found in inventory."""
    
    def __init__(self, dependencies: List[Dependency], db_connection=None):
        """
        Initialize missing code detector.
        
        Args:
            dependencies: List of all dependencies extracted from code
            db_connection: Optional database connection for querying inventory
        """
        self.dependencies = dependencies
        self.conn = db_connection
        self.cursor = db_connection.cursor() if db_connection else None
        
        # Cache inventory data
        self._inventory_programs: Optional[Set[str]] = None
        self._inventory_copybooks: Optional[Set[str]] = None
        self._inventory_datasets: Optional[Set[str]] = None
    
    def _load_inventory_programs(self) -> Set[str]:
        """Load program names from inventory."""
        if self._inventory_programs is not None:
            return self._inventory_programs
        
        if not self.cursor:
            self._inventory_programs = set()
            return self._inventory_programs
        
        try:
            # Try unified inventory table first
            # Include all executable artifact types: PROGRAM, SUBPROGRAM, SUBROUTINE, etc.
            self.cursor.execute("""
                SELECT artifact_name FROM inventory 
                WHERE artifact_type IN ('PROGRAM', 'SUBPROGRAM', 'SUBROUTINE', 'FUNCTION', 'PROCEDURE')
            """)
            self._inventory_programs = {row[0] for row in self.cursor.fetchall()}
        except Exception:
            # Try separate tables
            try:
                self.cursor.execute("SELECT program_name FROM inventory_programs")
                self._inventory_programs = {row[0] for row in self.cursor.fetchall()}
            except Exception:
                # Try old table name
                try:
                    self.cursor.execute("SELECT program_name FROM programs")
                    self._inventory_programs = {row[0] for row in self.cursor.fetchall()}
                except Exception:
                    self._inventory_programs = set()
        
        return self._inventory_programs
    
    def _load_inventory_copybooks(self) -> Set[str]:
        """Load copybook names from inventory."""
        if self._inventory_copybooks is not None:
            return self._inventory_copybooks
        
        if not self.cursor:
            self._inventory_copybooks = set()
            return self._inventory_copybooks
        
        try:
            # Try unified inventory table first
            # Include all copybook-like types: COPYBOOK, COPYCODE, LDA, GDA, DATA_STRUCTURE, INCLUDE, etc.
            self.cursor.execute("""
                SELECT artifact_name FROM inventory 
                WHERE artifact_type IN ('COPYBOOK', 'COPYCODE', 'LDA', 'GDA', 'DATA_STRUCTURE', 'INCLUDE', 'MACRO')
            """)
            self._inventory_copybooks = {row[0] for row in self.cursor.fetchall()}
        except Exception:
            # Try separate tables
            try:
                self.cursor.execute("SELECT copybook_name FROM inventory_copybooks")
                self._inventory_copybooks = {row[0] for row in self.cursor.fetchall()}
            except Exception:
                # Try old table name
                try:
                    self.cursor.execute("SELECT copybook_name FROM copybooks")
                    self._inventory_copybooks = {row[0] for row in self.cursor.fetchall()}
                except Exception:
                    self._inventory_copybooks = set()
        
        return self._inventory_copybooks
    
    def _load_inventory_datasets(self) -> Set[str]:
        """Load dataset names from inventory."""
        if self._inventory_datasets is not None:
            return self._inventory_datasets
        
        if not self.cursor:
            self._inventory_datasets = set()
            return self._inventory_datasets
        
        try:
            # Try unified inventory table first (datasets can be stored as DATASET or FILE type)
            self.cursor.execute("SELECT artifact_name FROM inventory WHERE artifact_type IN ('DATASET', 'FILE')")
            self._inventory_datasets = {row[0] for row in self.cursor.fetchall()}
        except Exception:
            # Try separate tables
            try:
                self.cursor.execute("SELECT dataset_name FROM inventory_datasets")
                self._inventory_datasets = {row[0] for row in self.cursor.fetchall()}
            except Exception:
                # Try old table name
                try:
                    self.cursor.execute("SELECT dataset_name FROM datasets")
                    self._inventory_datasets = {row[0] for row in self.cursor.fetchall()}
                except Exception:
                    self._inventory_datasets = set()
        
        return self._inventory_datasets
    
    def detect_missing_programs(self) -> List[MissingArtifact]:
        """
        Find programs that are called but not found in inventory.
        
        Returns:
            List of MissingArtifact objects for programs
        """
        inventory_programs = self._load_inventory_programs()
        
        # Find all referenced programs
        referenced_programs: Dict[str, List[Dependency]] = {}
        
        for dep in self.dependencies:
            # Look for program dependencies
            if dep.target_type == 'PROGRAM' and dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM
            }:
                program_name = dep.target_artifact
                if program_name not in referenced_programs:
                    referenced_programs[program_name] = []
                referenced_programs[program_name].append(dep)
        
        # Find missing programs
        missing_programs = []
        
        for program_name, deps in referenced_programs.items():
            if program_name not in inventory_programs:
                # Count references and get referencing artifacts
                reference_count = len(deps)
                referenced_by = list(set(dep.source_artifact for dep in deps))
                
                # Classify severity
                severity = SeverityThreshold.classify(reference_count)
                
                missing_artifact = MissingArtifact(
                    artifact_name=program_name,
                    artifact_type='PROGRAM',
                    reference_count=reference_count,
                    referenced_by=referenced_by,
                    severity=severity,
                    first_detected=datetime.now()
                )
                
                missing_programs.append(missing_artifact)
        
        # Sort by severity and reference count
        missing_programs.sort(
            key=lambda x: (
                {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[x.severity],
                -x.reference_count
            )
        )
        
        return missing_programs
    
    def detect_missing_copybooks(self) -> List[MissingArtifact]:
        """
        Find copybooks that are included but not found in inventory.
        
        Returns:
            List of MissingArtifact objects for copybooks
        """
        inventory_copybooks = self._load_inventory_copybooks()
        
        # Find all referenced copybooks
        referenced_copybooks: Dict[str, List[Dependency]] = {}
        
        for dep in self.dependencies:
            # Look for copybook dependencies
            if dep.target_type == 'COPYBOOK' and dep.dependency_type in {
                DependencyType.COPY,
                DependencyType.INCLUDE,
                DependencyType.SQL_INCLUDE
            }:
                copybook_name = dep.target_artifact
                if copybook_name not in referenced_copybooks:
                    referenced_copybooks[copybook_name] = []
                referenced_copybooks[copybook_name].append(dep)
        
        # Find missing copybooks
        missing_copybooks = []
        
        for copybook_name, deps in referenced_copybooks.items():
            if copybook_name not in inventory_copybooks:
                # Count references and get referencing artifacts
                reference_count = len(deps)
                referenced_by = list(set(dep.source_artifact for dep in deps))
                
                # Classify severity
                severity = SeverityThreshold.classify(reference_count)
                
                missing_artifact = MissingArtifact(
                    artifact_name=copybook_name,
                    artifact_type='COPYBOOK',
                    reference_count=reference_count,
                    referenced_by=referenced_by,
                    severity=severity,
                    first_detected=datetime.now()
                )
                
                missing_copybooks.append(missing_artifact)
        
        # Sort by severity and reference count
        missing_copybooks.sort(
            key=lambda x: (
                {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[x.severity],
                -x.reference_count
            )
        )
        
        return missing_copybooks
    
    def detect_missing_datasets(self) -> List[MissingArtifact]:
        """
        Find datasets that are referenced but not found in inventory.
        
        Returns:
            List of MissingArtifact objects for datasets
        """
        inventory_datasets = self._load_inventory_datasets()
        
        # Find all referenced datasets
        referenced_datasets: Dict[str, List[Dependency]] = {}
        
        for dep in self.dependencies:
            # Look for dataset dependencies
            if dep.target_type == 'DATASET' and dep.dependency_type in {
                DependencyType.DATASET_REF,
                DependencyType.CICS_FILE
            }:
                dataset_name = dep.target_artifact
                if dataset_name not in referenced_datasets:
                    referenced_datasets[dataset_name] = []
                referenced_datasets[dataset_name].append(dep)
        
        # Find missing datasets
        missing_datasets = []
        
        for dataset_name, deps in referenced_datasets.items():
            if dataset_name not in inventory_datasets:
                # Count references and get referencing artifacts
                reference_count = len(deps)
                referenced_by = list(set(dep.source_artifact for dep in deps))
                
                # Classify severity
                severity = SeverityThreshold.classify(reference_count)
                
                missing_artifact = MissingArtifact(
                    artifact_name=dataset_name,
                    artifact_type='DATASET',
                    reference_count=reference_count,
                    referenced_by=referenced_by,
                    severity=severity,
                    first_detected=datetime.now()
                )
                
                missing_datasets.append(missing_artifact)
        
        # Sort by severity and reference count
        missing_datasets.sort(
            key=lambda x: (
                {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[x.severity],
                -x.reference_count
            )
        )
        
        return missing_datasets
    
    def detect_all_missing(self) -> List[MissingArtifact]:
        """
        Detect all missing artifacts (programs, copybooks, datasets).
        
        Returns:
            Combined list of all missing artifacts
        """
        missing = []
        missing.extend(self.detect_missing_programs())
        missing.extend(self.detect_missing_copybooks())
        missing.extend(self.detect_missing_datasets())
        
        return missing
    
    def calculate_completeness_score(self) -> CompletenessReport:
        """
        Calculate inventory completeness score.
        
        Returns:
            CompletenessReport with detailed completeness metrics including
            total inventory size and dependency completeness.
        """
        inventory_programs = self._load_inventory_programs()
        inventory_copybooks = self._load_inventory_copybooks()
        inventory_datasets = self._load_inventory_datasets()
        
        # Count referenced artifacts
        referenced_programs = set()
        referenced_copybooks = set()
        referenced_datasets = set()
        
        for dep in self.dependencies:
            if dep.target_type == 'PROGRAM' and dep.dependency_type in {
                DependencyType.CALL,
                DependencyType.CICS_LINK,
                DependencyType.CICS_START,
                DependencyType.EXEC_PGM
            }:
                referenced_programs.add(dep.target_artifact)
            
            elif dep.target_type == 'COPYBOOK' and dep.dependency_type in {
                DependencyType.COPY,
                DependencyType.INCLUDE,
                DependencyType.SQL_INCLUDE
            }:
                referenced_copybooks.add(dep.target_artifact)
            
            elif dep.target_type == 'DATASET' and dep.dependency_type in {
                DependencyType.DATASET_REF,
                DependencyType.CICS_FILE
            }:
                referenced_datasets.add(dep.target_artifact)
        
        # Calculate found vs missing
        found_programs = len(referenced_programs & inventory_programs)
        missing_programs_count = len(referenced_programs - inventory_programs)
        
        found_copybooks = len(referenced_copybooks & inventory_copybooks)
        missing_copybooks_count = len(referenced_copybooks - inventory_copybooks)
        
        found_datasets = len(referenced_datasets & inventory_datasets)
        missing_datasets_count = len(referenced_datasets - inventory_datasets)
        
        # Inventory totals
        total_inventory_programs = len(inventory_programs)
        total_inventory_copybooks = len(inventory_copybooks)
        total_inventory_datasets = len(inventory_datasets)
        
        # Calculate completeness percentages
        total_referenced_programs = len(referenced_programs)
        total_referenced_copybooks = len(referenced_copybooks)
        total_referenced_datasets = len(referenced_datasets)
        
        program_completeness = (
            found_programs / total_referenced_programs
            if total_referenced_programs > 0 else 1.0
        )
        
        copybook_completeness = (
            found_copybooks / total_referenced_copybooks
            if total_referenced_copybooks > 0 else 1.0
        )
        
        dataset_completeness = (
            found_datasets / total_referenced_datasets
            if total_referenced_datasets > 0 else 1.0
        )
        
        # Calculate overall completeness
        total_referenced = (
            total_referenced_programs +
            total_referenced_copybooks +
            total_referenced_datasets
        )
        
        total_found = found_programs + found_copybooks + found_datasets
        
        overall_completeness = (
            total_found / total_referenced
            if total_referenced > 0 else 1.0
        )
        
        # Get all missing artifacts
        missing_artifacts = self.detect_all_missing()
        
        # Create report
        report = CompletenessReport(
            total_inventory_programs=total_inventory_programs,
            total_inventory_copybooks=total_inventory_copybooks,
            total_inventory_datasets=total_inventory_datasets,
            
            total_referenced_programs=total_referenced_programs,
            found_programs=found_programs,
            missing_programs=missing_programs_count,
            
            total_referenced_copybooks=total_referenced_copybooks,
            found_copybooks=found_copybooks,
            missing_copybooks=missing_copybooks_count,
            
            total_referenced_datasets=total_referenced_datasets,
            found_datasets=found_datasets,
            missing_datasets=missing_datasets_count,
            
            overall_completeness=overall_completeness,
            program_completeness=program_completeness,
            copybook_completeness=copybook_completeness,
            dataset_completeness=dataset_completeness,
            
            missing_artifacts=missing_artifacts
        )
        
        return report
    
    def get_missing_artifact_references(
        self,
        artifact_name: str,
        artifact_type: str
    ) -> List[MissingArtifactReference]:
        """
        Get all references to a specific missing artifact.
        
        Args:
            artifact_name: Name of the missing artifact
            artifact_type: Type of the artifact (PROGRAM, COPYBOOK, DATASET)
            
        Returns:
            List of MissingArtifactReference objects
        """
        references = []
        
        for dep in self.dependencies:
            if (dep.target_artifact == artifact_name and
                dep.target_type == artifact_type):
                
                ref = MissingArtifactReference(
                    missing_artifact=artifact_name,
                    missing_artifact_type=artifact_type,
                    referenced_by=dep.source_artifact,
                    referenced_by_type=dep.source_type,
                    reference_type=dep.dependency_type,
                    source_file=dep.source_file,
                    line_number=dep.line_number
                )
                
                references.append(ref)
        
        return references
    
    def classify_severity(self, artifact: MissingArtifact) -> str:
        """
        Classify missing artifact severity based on reference count.
        
        Args:
            artifact: MissingArtifact to classify
            
        Returns:
            Severity level (HIGH, MEDIUM, LOW)
        """
        return SeverityThreshold.classify(artifact.reference_count)
