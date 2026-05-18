"""
Dependency Validator - Validates dependencies against complete inventory.

This class is responsible for:
1. Validating dependencies against inventory
2. Identifying missing artifacts
3. Providing completeness metrics
4. Preparing validated dependencies for storage
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

from .models.artifact import Artifact
from .models.dependency import Dependency, DependencyType
from .dependency_analyzer import DependencyAnalysisResult
from .models.missing_artifact import MissingArtifact, Severity


class ValidationResult:
    """Container for dependency validation results."""
    
    def __init__(self):
        self.validated_dependencies: List[Dependency] = []
        self.missing_artifacts: List[MissingArtifact] = []
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        self.stats = defaultdict(int)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed without critical errors."""
        return len(self.validation_errors) == 0
    
    @property
    def completeness_score(self) -> float:
        """Calculate completeness score (0.0 to 1.0)."""
        total_deps = len(self.validated_dependencies)
        missing_count = len([m for m in self.missing_artifacts if m.severity == Severity.HIGH])
        
        if total_deps == 0:
            return 1.0
        
        return max(0.0, (total_deps - missing_count) / total_deps)


class DependencyValidator:
    """Validates dependencies against complete inventory."""
    
    # Dependency type mapping from parser types to normalized types
    DEPENDENCY_TYPE_MAPPING = {
        # COBOL
        'copybooks': ('COPYBOOK', DependencyType.COPY),
        'calls': ('PROGRAM', DependencyType.CALL),
        'cics_links': ('PROGRAM', DependencyType.CICS_LINK),
        'cics_transactions': ('TRANSACTION', DependencyType.CICS_TRANSACTION),
        'cics_read_files': ('FILE', DependencyType.CICS_READ),
        'cics_write_files': ('FILE', DependencyType.CICS_WRITE),
        'cics_rewrite_files': ('FILE', DependencyType.CICS_REWRITE),
        'cics_delete_files': ('FILE', DependencyType.CICS_DELETE),
        'cics_browse_files': ('FILE', DependencyType.CICS_BROWSE),
        'sql_includes': ('COPYBOOK', DependencyType.SQL_INCLUDE),
        'sql_tables': ('TABLE', DependencyType.SQL_TABLE),
        
        # PL/I
        'includes': ('COPYBOOK', DependencyType.COPY),
        'cics_xctl': ('PROGRAM', DependencyType.CICS_XCTL),
        'cics_link': ('PROGRAM', DependencyType.CICS_LINK),
        'file_declarations': ('FILE', DependencyType.FILE_REF),
        'file_reads': ('FILE', DependencyType.FILE_REF),
        'file_writes': ('FILE', DependencyType.FILE_REF),
        'cics_reads': ('FILE', DependencyType.CICS_READ),
        'cics_writes': ('FILE', DependencyType.CICS_WRITE),
        'cics_rewrites': ('FILE', DependencyType.CICS_REWRITE),
        'cics_deletes': ('FILE', DependencyType.CICS_DELETE),
        
        # JCL
        'programs': ('PROGRAM', DependencyType.EXEC_PGM),
        'procs': ('JCL', DependencyType.EXEC_PROC),
        'datasets': ('DATASET', DependencyType.DATASET_REF),
        
        # Natural
        'callnat': ('PROGRAM', DependencyType.CALL),
        'fetch': ('PROGRAM', DependencyType.FETCH),
        'using': ('COPYBOOK', DependencyType.COPY),
        'view_of': ('FILE', DependencyType.FILE_REF),
        'reads': ('FILE', DependencyType.FILE_REF),
        'page_ref': ('PAGE', DependencyType.PAGE_REF),
        'web_service': ('EXTERNAL_SERVICE', DependencyType.WEB_SERVICE),
        'work_file': ('FILE', DependencyType.WORK_FILE),
        'fetch_return': ('PROGRAM', DependencyType.FETCH_RETURN),
        
        # RPG
        'files': ('FILE', DependencyType.FILE_REF),
        'sql_tables': ('TABLE', DependencyType.SQL_TABLE),
        'prototypes': ('PROGRAM', DependencyType.CALL),
        
        # REXX
        'procedures': ('PROGRAM', DependencyType.CALL),
        'address_links': ('PROGRAM', DependencyType.CALL),
        'function_calls': ('PROGRAM', DependencyType.CALL),
        'tso_commands': ('PROGRAM', DependencyType.CALL),
        'ispexec_commands': ('PROGRAM', DependencyType.CALL),
        
        # Assembler
        'loads': ('PROGRAM', DependencyType.CALL),
        'xctls': ('PROGRAM', DependencyType.CICS_XCTL),
        'attaches': ('PROGRAM', DependencyType.CALL),
        'external_refs': ('PROGRAM', DependencyType.CALL),
        'macros': ('MACRO', DependencyType.COPY),
    }
    
    def __init__(self, inventory: Dict[str, Artifact], database: Optional[Any] = None):
        """
        Initialize validator with complete inventory.
        
        Args:
            inventory: Complete inventory mapping artifact names to Artifact objects
            database: Optional database adapter for creating stub records
        """
        self.inventory = inventory
        self.database = database
        self.stats = defaultdict(int)
        
        # Create lookup sets for fast validation
        self._create_lookup_sets()
    
    def validate_analysis_results(self, analysis_results: List[DependencyAnalysisResult]) -> ValidationResult:
        """
        Validate all dependency analysis results against inventory.
        
        Args:
            analysis_results: List of dependency analysis results
            
        Returns:
            ValidationResult with validated dependencies and missing artifacts
        """
        print(f"\n=== Phase 6: Validating Dependencies ===")
        print(f"Validating dependencies from {len(analysis_results)} artifacts...")
        
        validation_result = ValidationResult()
        
        for analysis_result in analysis_results:
            try:
                self._validate_single_result(analysis_result, validation_result)
            except Exception as e:
                validation_result.validation_errors.append(
                    f"Error validating {analysis_result.artifact.artifact_name}: {str(e)}"
                )
        
        # Calculate final statistics
        validation_result.stats.update(self.stats)
        
        # Print summary
        print(f"✓ Validated {len(validation_result.validated_dependencies)} dependencies")
        print(f"✓ Found {len(validation_result.missing_artifacts)} missing artifacts")
        print(f"✓ Completeness score: {validation_result.completeness_score:.1%}")
        
        if validation_result.validation_errors:
            print(f"⚠ Validation errors: {len(validation_result.validation_errors)}")
        if validation_result.validation_warnings:
            print(f"⚠ Validation warnings: {len(validation_result.validation_warnings)}")
        
        return validation_result
    
    def _create_lookup_sets(self) -> None:
        """Create lookup sets for fast validation."""
        self.programs = set()
        self.copybooks = set()
        self.jcl = set()
        self.datasets = set()
        self.files = set()
        self.transactions = set()
        self.tables = set()
        
        for artifact in self.inventory.values():
            name = artifact.primary_name
            
            if artifact.is_program:
                self.programs.add(name)
            elif artifact.is_copybook:
                self.copybooks.add(name)
            elif artifact.is_jcl:
                self.jcl.add(name)
            # Add other types as needed
    
    def _validate_single_result(self, analysis_result: DependencyAnalysisResult, 
                               validation_result: ValidationResult) -> None:
        """Validate a single analysis result."""
        artifact = analysis_result.artifact
        
        # Validate program-level dependencies if available
        if analysis_result.program_level_dependencies:
            self._validate_program_level_dependencies(
                analysis_result, validation_result
            )
        else:
            # Validate file-level dependencies
            self._validate_file_level_dependencies(
                analysis_result, validation_result
            )
    
    def _validate_program_level_dependencies(self, analysis_result: DependencyAnalysisResult,
                                           validation_result: ValidationResult) -> None:
        """Validate program-level dependencies."""
        artifact = analysis_result.artifact
        
        for program_name, prog_deps in analysis_result.program_level_dependencies.items():
            source_artifact = program_name
            source_type = 'PROGRAM'
            
            for dep_type, dep_list in prog_deps.items():
                if not isinstance(dep_list, list):
                    continue
                
                # Get target artifact type and normalized dependency type
                if dep_type not in self.DEPENDENCY_TYPE_MAPPING:
                    validation_result.validation_warnings.append(
                        f"Unknown dependency type: {dep_type} in {source_artifact}"
                    )
                    continue
                
                target_artifact_type, normalized_dependency_type = self.DEPENDENCY_TYPE_MAPPING[dep_type]
                
                for target_artifact in dep_list:
                    # Validate dependency
                    is_valid, missing_artifact = self._validate_dependency(
                        source_artifact, target_artifact, target_artifact_type
                    )
                    
                    if is_valid:
                        # Create validated dependency
                        dependency = Dependency(
                            source_artifact=source_artifact,
                            source_type=source_type,
                            target_artifact=target_artifact,
                            target_type=target_artifact_type,
                            dependency_type=normalized_dependency_type,
                            source_language=artifact.language,
                            source_file=artifact.file_path
                        )
                        validation_result.validated_dependencies.append(dependency)
                        self.stats['dependencies_validated'] += 1
                    else:
                        # Add to missing artifacts
                        if missing_artifact:
                            validation_result.missing_artifacts.append(missing_artifact)
                        self.stats['missing_artifacts'] += 1
    
    def _validate_file_level_dependencies(self, analysis_result: DependencyAnalysisResult,
                                        validation_result: ValidationResult) -> None:
        """Validate file-level dependencies."""
        artifact = analysis_result.artifact
        source_artifact = artifact.primary_name
        
        # Determine source type
        if artifact.is_jcl:
            source_type = 'JCL'
        else:
            source_type = 'PROGRAM'
        
        for dep_type, dep_list in analysis_result.file_level_dependencies.items():
            if not isinstance(dep_list, list):
                continue
            
            # Get target artifact type and normalized dependency type
            if dep_type not in self.DEPENDENCY_TYPE_MAPPING:
                validation_result.validation_warnings.append(
                    f"Unknown dependency type: {dep_type} in {source_artifact}"
                )
                continue
            
            target_artifact_type, normalized_dependency_type = self.DEPENDENCY_TYPE_MAPPING[dep_type]
            
            for target_artifact in dep_list:
                # Validate dependency
                is_valid, missing_artifact = self._validate_dependency(
                    source_artifact, target_artifact, target_artifact_type
                )
                
                if is_valid:
                    # Create validated dependency
                    dependency = Dependency(
                        source_artifact=source_artifact,
                        source_type=source_type,
                        target_artifact=target_artifact,
                        target_type=target_artifact_type,
                        dependency_type=normalized_dependency_type,
                        source_language=artifact.language,
                        source_file=artifact.file_path
                    )
                    validation_result.validated_dependencies.append(dependency)
                    self.stats['dependencies_validated'] += 1
                else:
                    # Add to missing artifacts
                    if missing_artifact:
                        validation_result.missing_artifacts.append(missing_artifact)
                    self.stats['missing_artifacts'] += 1
    
    def _validate_dependency(self, source_artifact: str, target_artifact: str, 
                           target_type: str) -> Tuple[bool, Optional[MissingArtifact]]:
        """
        Validate a single dependency against inventory.
        
        Now stores ALL dependencies by creating stub records for missing artifacts.
        
        Returns:
            Tuple of (is_valid=True, missing_artifact_for_reporting)
        """
        # Check if target exists in appropriate lookup set
        target_exists = False
        
        if target_type == 'PROGRAM':
            target_exists = target_artifact in self.programs
        elif target_type == 'COPYBOOK':
            target_exists = target_artifact in self.copybooks
        elif target_type == 'JCL':
            target_exists = target_artifact in self.jcl
        elif target_type == 'DATASET':
            target_exists = target_artifact in self.datasets
        elif target_type == 'FILE':
            target_exists = target_artifact in self.files
        elif target_type == 'TRANSACTION':
            target_exists = target_artifact in self.transactions
        elif target_type == 'TABLE':
            target_exists = target_artifact in self.tables
        else:
            # Unknown target type - assume valid
            target_exists = True
        
        if target_exists:
            # Artifact found in inventory
            return True, None
        else:
            # Artifact NOT found - create stub record and still return valid
            missing_artifact = self._create_stub_record(target_artifact, target_type, source_artifact)
            
            # Return True to store the dependency, but also return missing_artifact for reporting
            return True, missing_artifact
    
    def _create_stub_record(self, artifact_name: str, artifact_type: str, 
                           referenced_by: str) -> MissingArtifact:
        """
        Create a stub inventory record for a missing artifact.
        
        Args:
            artifact_name: Name of the missing artifact
            artifact_type: Type of the artifact (PROGRAM, COPYBOOK, etc.)
            referenced_by: Name of the artifact that references this one
            
        Returns:
            MissingArtifact object for reporting
        """
        # Classify the artifact source
        artifact_source = self._classify_artifact_source(artifact_name, artifact_type)
        
        # Create stub record in database if database is available
        if self.database:
            try:
                cursor = self.database.cursor()
                
                # Check if artifact already exists under ANY type (not just the target type)
                # This prevents phantom COPYBOOK entries for artifacts that exist as MAIN/DATA
                cursor.execute("""
                    SELECT id, artifact_type FROM inventory 
                    WHERE artifact_name = ?
                """, (artifact_name,))
                
                existing = cursor.fetchone()
                if existing:
                    # Artifact exists under a different type — add to lookup sets but don't create stub
                    if artifact_type == 'PROGRAM':
                        self.programs.add(artifact_name)
                    elif artifact_type == 'COPYBOOK':
                        self.copybooks.add(artifact_name)
                    elif artifact_type == 'JCL':
                        self.jcl.add(artifact_name)
                    elif artifact_type == 'FILE':
                        self.files.add(artifact_name)
                    elif artifact_type == 'DATASET':
                        self.datasets.add(artifact_name)
                    elif artifact_type == 'TRANSACTION':
                        self.transactions.add(artifact_name)
                    elif artifact_type == 'TABLE':
                        self.tables.add(artifact_name)
                elif not existing:
                    # Insert stub record
                    stub_data = {
                        'artifact_name': artifact_name,
                        'filename': artifact_name,
                        'artifact_type': artifact_type,
                        'language': 'UNKNOWN',
                        'file_path': f'MISSING/{artifact_source}/{artifact_name}',
                        'file_size': None,
                        'program_count': 0,
                        'found': 0,  # Mark as not found
                        'artifact_source': artifact_source
                    }
                    
                    self.database.insert_rows('inventory', [stub_data])
                    self.database.commit()
                    
                    # Add to lookup sets so we don't create duplicates
                    if artifact_type == 'PROGRAM':
                        self.programs.add(artifact_name)
                    elif artifact_type == 'COPYBOOK':
                        self.copybooks.add(artifact_name)
                    elif artifact_type == 'JCL':
                        self.jcl.add(artifact_name)
                    elif artifact_type == 'FILE':
                        self.files.add(artifact_name)
                    elif artifact_type == 'DATASET':
                        self.datasets.add(artifact_name)
                    elif artifact_type == 'TRANSACTION':
                        self.transactions.add(artifact_name)
                    elif artifact_type == 'TABLE':
                        self.tables.add(artifact_name)
                    
                    self.stats['stub_records_created'] += 1
            
            except Exception as e:
                print(f"  ⚠ Warning: Could not create stub record for {artifact_name}: {e}")
        
        # Create missing artifact record for reporting
        severity = self._determine_missing_severity(artifact_type, artifact_name)
        missing_artifact = MissingArtifact(
            artifact_name=artifact_name,
            artifact_type=artifact_type,
            reference_count=1,
            referenced_by=[referenced_by],
            severity=severity.value if hasattr(severity, 'value') else severity
        )
        
        return missing_artifact
    
    def _classify_artifact_source(self, artifact_name: str, artifact_type: str) -> str:
        """
        Classify the source of a missing artifact.
        
        Returns:
            'SYSTEM' for IBM system copybooks
            'EXTERNAL' for external files/programs
            'MISSING' for artifacts that should exist but don't
        """
        # IBM system copybooks
        if artifact_type == 'COPYBOOK':
            if artifact_name.startswith('DFH'):  # CICS copybooks
                return 'SYSTEM'
            elif artifact_name.startswith('DSN'):  # DB2 copybooks
                return 'SYSTEM'
            elif artifact_name.startswith('SQL'):  # SQL copybooks
                return 'SYSTEM'
        
        # External files (often have special naming patterns)
        if artifact_type == 'FILE':
            if artifact_name.startswith('LIT-'):  # Literal file names
                return 'EXTERNAL'
        
        # Default to MISSING
        return 'MISSING'
    
    def _determine_missing_severity(self, target_type: str, target_artifact: str) -> Severity:
        """Determine severity of missing artifact."""
        # Programs and copybooks are critical
        if target_type in ['PROGRAM', 'COPYBOOK']:
            return Severity.HIGH
        
        # Files and datasets are important
        elif target_type in ['FILE', 'DATASET', 'TABLE']:
            return Severity.MEDIUM
        
        # Transactions and other types are lower priority
        else:
            return Severity.LOW