"""
Analysis Orchestrator - Coordinates the complete analysis workflow.

This class orchestrates the entire legacy analysis process with proper
separation of concerns and error recovery.
"""

import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .inventory_manager import InventoryManager
from .dependency_analyzer import DependencyAnalyzer, DependencyAnalysisResult
from .dependency_validator import DependencyValidator, ValidationResult
from .dependency_loader import DependencyLoader
from .program_level_dependency_loader import ProgramLevelDependencyLoader
from .copybook_analysis_loader import CopybookAnalysisLoader
from .analysis.copybook_analyzer import CopybookAnalyzer
from .models.artifact import Artifact


class AnalysisOrchestrator:
    """Orchestrates the complete legacy analysis workflow."""
    
    def __init__(self, database: BaseDatabase, log_file: Optional[str] = None):
        """
        Initialize analysis orchestrator.
        
        Args:
            database: Database adapter instance
            log_file: Optional log file path
        """
        self.database = database
        self.log_file = log_file
        
        # Initialize components
        self.inventory_manager = InventoryManager(database)
        self.dependency_analyzer = DependencyAnalyzer()
        self.dependency_loader = DependencyLoader(database)
        
        # State tracking
        self.inventory_complete = False
        self.dependencies_analyzed = False
        self.dependencies_validated = False
        self.dependencies_stored = False
        
        # Results
        self.artifacts: List[Artifact] = []
        self.analysis_results: List[DependencyAnalysisResult] = []
        self.validation_result: Optional[ValidationResult] = None
    
    def run_complete_analysis(self, source_directory: str,
                            calculate_complexity: bool = False,
                            enable_program_level: bool = True,
                            enable_copybook_analysis: bool = True) -> Dict[str, any]:
        """
        Run the complete analysis workflow.
        
        Args:
            source_directory: Root directory containing source code
            calculate_complexity: Whether to calculate complexity metrics
            enable_program_level: Whether to detect program boundaries
            
        Returns:
            Dictionary with complete analysis results and statistics
        """
        print("="*80)
        print("LEGACY ANALYZER - COMPLETE ANALYSIS WORKFLOW")
        print("="*80)
        print(f"Source Directory: {source_directory}")
        print(f"Database: {self.database.database_path if hasattr(self.database, 'database_path') else 'In-memory'}")
        print(f"Complexity Analysis: {'Enabled' if calculate_complexity else 'Disabled'}")
        print(f"Program-Level Analysis: {'Enabled' if enable_program_level else 'Disabled'}")
        print(f"Copybook Analysis: {'Enabled' if enable_copybook_analysis else 'Disabled'}")
        print("="*80)
        
        try:
            # Phase 1-4: Complete Inventory
            self._run_inventory_phases(source_directory)
            
            # Phase 5: Dependency Analysis
            self._run_dependency_analysis(calculate_complexity, enable_program_level, enable_copybook_analysis)
            
            # Phase 5a: Resolve cross-file VIEW definitions (Natural)
            self._resolve_global_view_definitions()
            
            # Phase 6: Dependency Validation
            self._run_dependency_validation()
            
            # Phase 7: Dependency Storage
            self._run_dependency_storage()
            
            # Phase 7a: Store Program-Level Dependencies (if enabled)
            if enable_program_level:
                self._run_program_level_storage()
            
            # Phase 7b: Store Copybook Analysis (if enabled)  
            if enable_copybook_analysis:
                self._run_copybook_analysis_storage()
            
            # Phase 8: Final Analysis
            results = self._run_final_analysis(enable_program_level, enable_copybook_analysis)
            
            print("\n" + "="*80)
            print("ANALYSIS COMPLETED SUCCESSFULLY")
            print("="*80)
            
            return results
            
        except Exception as e:
            print(f"\n❌ ANALYSIS FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def run_inventory_only(self, source_directory: str) -> Dict[str, any]:
        """
        Run only the inventory phases (useful for initial discovery).
        
        Args:
            source_directory: Root directory containing source code
            
        Returns:
            Dictionary with inventory results and statistics
        """
        print("="*80)
        print("LEGACY ANALYZER - INVENTORY ONLY")
        print("="*80)
        
        try:
            self._run_inventory_phases(source_directory)
            
            # Return inventory statistics
            return {
                'inventory_complete': self.inventory_complete,
                'artifacts_discovered': len(self.artifacts),
                'inventory_stats': self.inventory_manager.get_inventory_stats()
            }
            
        except Exception as e:
            print(f"\n❌ INVENTORY FAILED: {str(e)}")
            raise
    
    def run_dependency_analysis_only(self, calculate_complexity: bool = False,
                                   enable_program_level: bool = True,
                                   enable_copybook_analysis: bool = True) -> Dict[str, any]:
        """
        Run only dependency analysis (requires inventory to be complete).
        
        Args:
            calculate_complexity: Whether to calculate complexity metrics
            enable_program_level: Whether to detect program boundaries
            
        Returns:
            Dictionary with dependency analysis results
        """
        if not self.inventory_complete:
            raise ValueError("Inventory must be complete before running dependency analysis")
        
        print("="*80)
        print("LEGACY ANALYZER - DEPENDENCY ANALYSIS ONLY")
        print("="*80)
        
        try:
            # Phase 5: Dependency Analysis
            self._run_dependency_analysis(calculate_complexity, enable_program_level, enable_copybook_analysis)
            
            # Phase 6: Dependency Validation
            self._run_dependency_validation()
            
            return {
                'dependencies_analyzed': self.dependencies_analyzed,
                'dependencies_validated': self.dependencies_validated,
                'analysis_results': len(self.analysis_results),
                'validation_result': self.validation_result,
                'analysis_stats': self.dependency_analyzer.get_analysis_stats()
            }
            
        except Exception as e:
            print(f"\n❌ DEPENDENCY ANALYSIS FAILED: {str(e)}")
            raise
    
    def run_artifacts_only(self, source_directory: str, artifact_type: str = 'all') -> Dict[str, any]:
        """
        Run only specialized artifact parsing and loading.
        
        Args:
            source_directory: Root directory containing source code
            artifact_type: Type of artifacts to parse ('csd', 'jcl', 'all')
            
        Returns:
            Dictionary with artifact parsing results
        """
        print("="*80)
        print("LEGACY ANALYZER - SPECIALIZED ARTIFACTS ONLY")
        print("="*80)
        print(f"Source Directory: {source_directory}")
        print(f"Artifact Type: {artifact_type}")
        print("="*80)
        
        try:
            # Create inventory schema
            self.inventory_manager.create_inventory_schema()
            
            # Run specialized artifact parsing based on type
            results = {}
            
            if artifact_type in ['all', 'csd']:
                cics_count = self._parse_csd_artifacts_only(source_directory)
                results['cics_resources'] = cics_count
            
            if artifact_type in ['all', 'jcl']:
                jcl_count = self._parse_jcl_artifacts_only(source_directory)
                results['jcl_jobs'] = jcl_count
            
            # Always populate programs and copybooks from existing inventory if available
            if artifact_type == 'all':
                programs_count = self._populate_programs_from_existing_inventory()
                copybooks_count = self._populate_copybooks_from_existing_inventory()
                results['programs'] = programs_count
                results['copybooks'] = copybooks_count
            
            self.database.commit()
            
            print("\n" + "="*80)
            print("SPECIALIZED ARTIFACTS PARSING COMPLETED")
            print("="*80)
            
            return results
            
        except Exception as e:
            print(f"\n❌ ARTIFACTS PARSING FAILED: {str(e)}")
            raise
    
    def _parse_csd_artifacts_only(self, source_directory: str) -> int:
        """Parse CSD files only."""
        print("\n=== Parsing CSD Files ===")
        return self.inventory_manager._scan_and_parse_csd_files(source_directory)
    
    def _parse_jcl_artifacts_only(self, source_directory: str) -> int:
        """Parse JCL files only."""
        print("\n=== Parsing JCL Files ===")
        return self.inventory_manager._scan_and_parse_jcl_files(source_directory)
    
    def _populate_programs_from_existing_inventory(self) -> int:
        """Populate programs from existing inventory."""
        print("\n=== Populating Programs from Inventory ===")
        self.inventory_manager._populate_programs_from_inventory()
        return self.inventory_manager.stats.get('programs_populated', 0)
    
    def _populate_copybooks_from_existing_inventory(self) -> int:
        """Populate copybooks from existing inventory."""
        print("\n=== Populating Copybooks from Inventory ===")
        self.inventory_manager._populate_copybooks_from_inventory()
        return self.inventory_manager.stats.get('copybooks_populated', 0)
    
    def get_complete_results(self) -> Dict[str, any]:
        """Get complete analysis results."""
        return {
            'inventory_complete': self.inventory_complete,
            'dependencies_analyzed': self.dependencies_analyzed,
            'dependencies_validated': self.dependencies_validated,
            'dependencies_stored': self.dependencies_stored,
            'artifacts': self.artifacts,
            'analysis_results': self.analysis_results,
            'validation_result': self.validation_result,
            'inventory_stats': self.inventory_manager.get_inventory_stats() if self.inventory_complete else {},
            'analysis_stats': self.dependency_analyzer.get_analysis_stats() if self.dependencies_analyzed else {}
        }
    
    def _run_inventory_phases(self, source_directory: str) -> None:
        """Run phases 1-4: Complete inventory discovery and population."""
        # Phase 1: Discover all files
        self.artifacts = self.inventory_manager.discover_all_files(source_directory)
        
        # Phase 2: Extract metadata
        self.inventory_manager.extract_all_metadata()
        
        # Phase 3: Create schema
        self.inventory_manager.create_inventory_schema()
        
        # Phase 3a: Create complexity_metrics table
        from .database_setup import DatabaseSetup
        setup = DatabaseSetup(self.database)
        setup._create_complexity_metrics_table(verbose=False)
        
        # Phase 4: Populate inventory (including specialized tables)
        self.inventory_manager.populate_complete_inventory(source_directory)
        
        self.inventory_complete = True
    
    def _run_dependency_analysis(self, calculate_complexity: bool, 
                               enable_program_level: bool,
                               enable_copybook_analysis: bool) -> None:
        """Run phase 5: Dependency analysis."""
        if not self.inventory_complete:
            raise ValueError("Inventory must be complete before dependency analysis")
        
        self.analysis_results = self.dependency_analyzer.analyze_multiple_artifacts(
            self.artifacts, calculate_complexity, enable_program_level
        )
        
        # Save complexity metrics if calculated
        if calculate_complexity:
            self._save_complexity_metrics()
        
        # Run copybook analysis if enabled
        if enable_copybook_analysis:
            self._run_copybook_analysis()
        
        self.dependencies_analyzed = True


    def _resolve_global_view_definitions(self) -> None:
        """
        Resolve cross-file VIEW definitions for Natural programs.

        Natural VIEW definitions (e.g., '1 EMPL1 VIEW OF EMPLOYEES') map a local
        variable name to a physical file. When a program does 'FIND EMPL1 WITH ...',
        the parser picks up EMPL1 as a FILE_REF target. But the VIEW definition may
        be in a different file (e.g., a Local Data Area .NSL file).

        This method:
        1. Collects all VIEW definitions from all Natural analysis results
        2. Replaces VIEW variable names with physical file names in view_of dependencies
        """
        print(f"\n=== Phase 5a: Resolving Cross-File VIEW Definitions ===")

        # Step 1: Build global VIEW map from all Natural results
        global_view_map = {}  # VIEW_NAME -> PHYSICAL_FILE

        for result in self.analysis_results:
            if result.artifact.language != 'NATURAL':
                continue

            # Check file-level dependencies for view_definitions
            view_defs = result.file_level_dependencies.get('view_definitions', {})
            if isinstance(view_defs, dict):
                for view_name, physical_file in view_defs.items():
                    global_view_map[view_name.upper()] = physical_file.upper()

            # Also check program-level dependencies
            for prog_name, prog_deps in result.program_level_dependencies.items():
                if isinstance(prog_deps, dict):
                    prog_view_defs = prog_deps.get('view_definitions', {})
                    if isinstance(prog_view_defs, dict):
                        for view_name, physical_file in prog_view_defs.items():
                            global_view_map[view_name.upper()] = physical_file.upper()

        if not global_view_map:
            print("✓ No VIEW definitions found — skipping")
            return

        print(f"  Found {len(global_view_map)} VIEW definitions: {dict(list(global_view_map.items())[:5])}")

        # Step 2: Resolve VIEW names in view_of (FILE_REF) dependencies
        resolved_count = 0

        for result in self.analysis_results:
            if result.artifact.language != 'NATURAL':
                continue

            # Resolve in file-level dependencies
            resolved_count += self._resolve_views_in_deps(
                result.file_level_dependencies, global_view_map
            )

            # Resolve in program-level dependencies
            for prog_name, prog_deps in result.program_level_dependencies.items():
                if isinstance(prog_deps, dict):
                    resolved_count += self._resolve_views_in_deps(
                        prog_deps, global_view_map
                    )

        print(f"✓ Resolved {resolved_count} VIEW references to physical files")

    def _resolve_views_in_deps(self, deps: dict, view_map: dict) -> int:
        """Replace VIEW variable names with physical file names in view_of deps."""
        resolved = 0
        view_of = deps.get('view_of', [])
        if not isinstance(view_of, list):
            return 0

        new_view_of = []
        for target in view_of:
            upper_target = target.upper()
            if upper_target in view_map:
                physical = view_map[upper_target]
                if physical not in new_view_of:
                    new_view_of.append(physical)
                resolved += 1
            else:
                if target not in new_view_of:
                    new_view_of.append(target)

        deps['view_of'] = new_view_of
        return resolved

    
    def _run_dependency_validation(self) -> None:
        """Run phase 6: Dependency validation."""
        if not self.dependencies_analyzed:
            raise ValueError("Dependencies must be analyzed before validation")
        
        # Get complete inventory for validation
        inventory = self.inventory_manager.get_complete_inventory()
        
        # Create validator and validate (pass database for stub record creation)
        validator = DependencyValidator(inventory, self.database)
        self.validation_result = validator.validate_analysis_results(self.analysis_results)
        
        self.dependencies_validated = True
    
    def _run_dependency_storage(self) -> None:
        """Run phase 7: Store validated dependencies."""
        if not self.dependencies_validated or not self.validation_result:
            raise ValueError("Dependencies must be validated before storage")
        
        print(f"\n=== Phase 7: Storing Dependencies ===")
        
        # Create dependencies schema
        self.dependency_loader.create_dependencies_schema()
        
        # Store validated dependencies
        if self.validation_result.validated_dependencies:
            # Convert Dependency objects to dictionaries for bulk_insert
            dependency_dicts = []
            for dep in self.validation_result.validated_dependencies:
                dep_dict = {
                    'source_artifact_name': dep.source_artifact,
                    'source_artifact_type': dep.source_type,
                    'target_artifact_name': dep.target_artifact,
                    'target_artifact_type': dep.target_type,
                    'dependency_type': dep.dependency_type.value if hasattr(dep.dependency_type, 'value') else str(dep.dependency_type),
                    'source_file_path': dep.source_file,
                    'line_number': getattr(dep, 'line_number', None)
                }
                dependency_dicts.append(dep_dict)
            
            result = self.dependency_loader.bulk_insert(dependency_dicts)
            stored_count = result.get('inserted', 0) + result.get('updated', 0)
            print(f"✓ Stored {stored_count} validated dependencies")
        else:
            print("✓ No dependencies to store")
        
        # Update complexity metrics with dependency counts (if complexity was calculated)
        if any(r.complexity_metrics for r in self.analysis_results):
            self._update_complexity_with_dependencies()
        
        # Create CICS_TRANSACTION dependencies for migration flow builder
        self._create_cics_transaction_dependencies()
        
        # Create JCL→PROGRAM dependencies for batch entry points
        self._create_jcl_program_dependencies()
        
        self.dependencies_stored = True
    
    def _run_copybook_analysis(self) -> None:
        """Run copybook analysis on copybook artifacts."""
        print(f"\n=== Running Copybook Analysis ===")
        
        # Find copybook artifacts
        copybook_artifacts = [a for a in self.artifacts if a.artifact_type == 'COPYBOOK']
        
        if not copybook_artifacts:
            print("✓ No copybooks found for analysis")
            return
        
        print(f"Analyzing {len(copybook_artifacts)} copybooks...")
        
        copybook_analyzer = CopybookAnalyzer()
        
        for artifact in copybook_artifacts:
            try:
                # Analyze copybook content
                analysis_result = copybook_analyzer.analyze_content(
                    artifact.file_path, 
                    artifact.language
                )
                
                # Find corresponding dependency analysis result and add copybook analysis
                for dep_result in self.analysis_results:
                    if dep_result.artifact.file_path == artifact.file_path:
                        dep_result.copybook_analysis_results.append(analysis_result)
                        break
                        
            except Exception as e:
                print(f"  ⚠ Warning: Error analyzing copybook {artifact.file_path}: {str(e)}")
        
        print(f"✓ Completed copybook analysis")
    
    def _save_complexity_metrics(self) -> None:
        """Save complexity metrics to database with dependency counts."""
        print(f"\n=== Saving Complexity Metrics ===")
        
        from .analysis.complexity_analyzer import ComplexityAnalyzer
        from .models.complexity import ComplexityMetrics
        
        complexity_analyzer = ComplexityAnalyzer(self.database)
        saved_count = 0
        
        # First pass: Save initial metrics from parsers
        for result in self.analysis_results:
            if result.complexity_metrics:
                try:
                    # Check if it's already a ComplexityMetrics object or a dict
                    if isinstance(result.complexity_metrics, ComplexityMetrics):
                        complexity_analyzer.save_metrics(result.complexity_metrics)
                        saved_count += 1
                    elif isinstance(result.complexity_metrics, dict):
                        # Extract LOC metrics from nested dict if present
                        loc_metrics = result.complexity_metrics.get('loc_metrics', {})
                        
                        # Convert dict to ComplexityMetrics object
                        metrics = ComplexityMetrics(
                            program_name=result.artifact.artifact_name,
                            language=result.artifact.language,
                            lines_of_code=loc_metrics.get('loc', result.complexity_metrics.get('loc', 0)),
                            cyclomatic_complexity=result.complexity_metrics.get('cyclomatic_complexity', 0),
                            dependency_count_in=result.complexity_metrics.get('dependency_count_in', 0),
                            dependency_count_out=result.complexity_metrics.get('dependency_count_out', 0),
                            composite_score=result.complexity_metrics.get('composite_score', 0.0),
                            complexity_tier=result.complexity_metrics.get('complexity_tier', 'UNKNOWN'),
                            comment_lines=loc_metrics.get('comment_lines', result.complexity_metrics.get('comment_lines', 0)),
                            blank_lines=loc_metrics.get('blank_lines', result.complexity_metrics.get('blank_lines', 0)),
                            total_lines=loc_metrics.get('total_lines', result.complexity_metrics.get('total_lines', 0)),
                            language_factor=result.complexity_metrics.get('language_factor', 1.0),
                            is_god_program=result.complexity_metrics.get('is_god_program', False)
                        )
                        complexity_analyzer.save_metrics(metrics)
                        saved_count += 1
                except Exception as e:
                    print(f"  ⚠ Warning: Error saving complexity for {result.artifact.artifact_name}: {str(e)}")
        
        if saved_count > 0:
            self.database.commit()
            print(f"✓ Saved initial complexity metrics for {saved_count} programs")
        else:
            print("✓ No complexity metrics to save")
    
    def _update_complexity_with_dependencies(self) -> None:
        """Update complexity metrics with dependency counts and recalculate scores."""
        print(f"\n=== Updating Complexity with Dependency Counts ===")
        
        cursor = self.database.cursor()
        
        # Get all programs with complexity metrics
        cursor.execute("""
            SELECT program_name, lines_of_code, cyclomatic_complexity, language_factor
            FROM complexity_metrics
        """)
        
        programs = cursor.fetchall()
        if not programs:
            print("✓ No complexity metrics to update")
            return
        
        print(f"Updating {len(programs)} programs with dependency counts...")
        
        # Default weights from COMPLEXITY_GUIDE.md
        LOC_WEIGHT = 0.3
        CYCLOMATIC_WEIGHT = 0.4
        DEPS_WEIGHT = 0.3
        
        updated_count = 0
        
        for program_name, loc, cyclomatic, language_factor in programs:
            # Get dependency counts from artifact_dependencies table
            cursor.execute("""
                SELECT COUNT(*) 
                FROM artifact_dependencies 
                WHERE target_artifact_name = ? AND target_artifact_type = 'PROGRAM'
            """, (program_name,))
            deps_in = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM artifact_dependencies 
                WHERE source_artifact_name = ? AND source_artifact_type = 'PROGRAM'
            """, (program_name,))
            deps_out = cursor.fetchone()[0]
            
            # Calculate composite score
            base_score = (loc * LOC_WEIGHT) + (cyclomatic * CYCLOMATIC_WEIGHT) + ((deps_in + deps_out) * DEPS_WEIGHT)
            composite_score = base_score * language_factor
            
            # Determine complexity tier
            if composite_score <= 10:
                complexity_tier = 'LOW'
            elif composite_score <= 25:
                complexity_tier = 'MEDIUM'
            elif composite_score <= 50:
                complexity_tier = 'HIGH'
            else:
                complexity_tier = 'VERY_HIGH'
            
            # Check if god program (score > 100)
            is_god_program = 1 if composite_score > 100 else 0
            
            # Update the record
            cursor.execute("""
                UPDATE complexity_metrics
                SET dependency_count_in = ?,
                    dependency_count_out = ?,
                    composite_score = ?,
                    complexity_tier = ?,
                    is_god_program = ?
                WHERE program_name = ?
            """, (deps_in, deps_out, composite_score, complexity_tier, is_god_program, program_name))
            
            updated_count += 1
        
        self.database.commit()
        print(f"✓ Updated {updated_count} programs with dependency counts and scores")
    

    
    def _run_program_level_storage(self) -> None:
        """Store program-level dependencies using ProgramLevelDependencyLoader."""
        print(f"\n=== Phase 7a: Storing Program-Level Dependencies ===")
        
        # Check if any results have program boundaries
        program_level_results = [r for r in self.analysis_results if r.has_program_boundaries]
        
        if not program_level_results:
            print("✓ No program boundaries detected - skipping program-level storage")
            return
        
        print(f"Processing {len(program_level_results)} files with program boundaries...")
        
        # Use ProgramLevelDependencyLoader for program-level storage
        program_loader = ProgramLevelDependencyLoader(self.database)
        
        total_programs = 0
        total_dependencies = 0
        
        for result in program_level_results:
            try:
                # Convert program-level dependencies to the expected format
                program_dependencies = {}
                for prog_name, prog_deps in result.program_level_dependencies.items():
                    dependencies = []
                    
                    # Handle different dependency formats
                    if isinstance(prog_deps, dict):
                        # Format: {dep_type: [dep_list]} - from mixed content analysis
                        # Use DEPENDENCY_TYPE_MAPPING to get correct target_type and dependency_type
                        from .dependency_validator import DependencyValidator
                        dep_mapping = DependencyValidator.DEPENDENCY_TYPE_MAPPING
                        
                        for dep_type, dep_list in prog_deps.items():
                            if isinstance(dep_list, list):
                                # Look up the correct target type and dependency type
                                if dep_type in dep_mapping:
                                    mapped_target_type, mapped_dep_type = dep_mapping[dep_type]
                                else:
                                    # Skip non-dependency keys (is_global_data_area, is_ddm, metadata, etc.)
                                    continue
                                
                                for dep_target in dep_list:
                                    from .models.dependency import Dependency, DependencyType
                                    dependency = Dependency(
                                        source_artifact=prog_name,
                                        source_type="PROGRAM",
                                        target_artifact=dep_target,
                                        target_type=mapped_target_type,
                                        dependency_type=mapped_dep_type,
                                        source_language=result.artifact.language,
                                        source_file=result.artifact.file_path
                                    )
                                    dependencies.append(dependency)
                    elif isinstance(prog_deps, list):
                        # Format: [Dependency objects] - from regular analysis
                        dependencies = prog_deps
                    else:
                        # Unknown format, skip
                        continue
                    
                    program_dependencies[prog_name] = dependencies
                
                stats = program_loader.store_program_dependencies(
                    result.artifact.file_path,
                    result.program_boundaries,
                    program_dependencies
                )
                
                total_programs += stats.get('programs_stored', 0)
                total_dependencies += stats.get('dependencies_stored', 0)
                
            except Exception as e:
                print(f"  ⚠ Warning: Error storing program-level data for {result.artifact.file_path}: {str(e)}")
        
        print(f"✓ Stored {total_programs} program boundaries and {total_dependencies} program-level dependencies")
        
        # Phase 7a.1: Update inventory with correct program counts and dominance
        self._update_inventory_with_program_boundaries()
    
    def _run_copybook_analysis_storage(self) -> None:
        """Store copybook analysis results using CopybookAnalysisLoader."""
        print(f"\n=== Phase 7b: Storing Copybook Analysis ===")
        
        # Collect all copybook analysis results
        copybook_results = []
        for result in self.analysis_results:
            if hasattr(result, 'copybook_analysis_results'):
                copybook_results.extend(result.copybook_analysis_results)
        
        if not copybook_results:
            print("✓ No copybook analysis results to store")
            return
        
        print(f"Storing {len(copybook_results)} copybook analysis results...")
        
        loader = CopybookAnalysisLoader(self.database)
        stats = loader.store_copybook_analysis(copybook_results)
        
        print(f"✓ Stored {stats.get('stored', 0)} copybook analysis results")
        if stats.get('errors', 0) > 0:
            print(f"⚠ {stats.get('errors', 0)} errors occurred during storage")
    
    def _update_inventory_with_program_boundaries(self) -> None:
        """Update inventory table with correct program counts and dominance after program boundaries are detected."""
        print("  Updating inventory with program boundary information...")
        
        cursor = self.database.cursor()
        
        # Get all files that have program boundaries
        cursor.execute("""
            SELECT inv.id, inv.file_path, COUNT(pfm.id) as actual_program_count,
                   GROUP_CONCAT(pfm.language) as languages,
                   GROUP_CONCAT(pfm.program_type) as types
            FROM inventory inv
            LEFT JOIN program_file_mapping pfm ON inv.id = pfm.file_id
            GROUP BY inv.id, inv.file_path
        """)
        
        files_with_programs = cursor.fetchall()
        
        for file_id, file_path, program_count, languages_str, types_str in files_with_programs:
            if program_count == 0:
                continue  # Skip files with no programs
            
            # Parse languages and types
            languages = languages_str.split(',') if languages_str else []
            types = types_str.split(',') if types_str else []
            
            # Calculate dominance
            dominant_language, dominant_type = self._calculate_dominance(languages, types)
            
            # Determine final language and artifact_type
            final_language = dominant_language if dominant_language else ('MIXED' if len(set(languages)) > 1 else languages[0] if languages else 'UNKNOWN')
            # Map DATA program type to COPYBOOK artifact type for inventory
            mapped_types = [('COPYBOOK' if t == 'DATA' else t) for t in types]
            mapped_dominant = 'COPYBOOK' if dominant_type == 'DATA' else dominant_type
            final_artifact_type = mapped_dominant if mapped_dominant else ('MIXED' if len(set(mapped_types)) > 1 else mapped_types[0] if mapped_types else 'PROGRAM')
            
            # Update inventory record
            cursor.execute("""
                UPDATE inventory 
                SET program_count = ?, 
                    dominant_language = ?, 
                    dominant_type = ?,
                    language = ?,
                    artifact_type = ?
                WHERE id = ?
            """, (
                program_count,
                dominant_language,
                dominant_type, 
                final_language,
                final_artifact_type,
                file_id
            ))
        
        self.database.commit()
        print(f"    ✓ Updated inventory for {len([f for f in files_with_programs if f[2] > 0])} files with program boundaries")
    
    def _calculate_dominance(self, languages: List[str], types: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Calculate dominant language and type from program boundary data."""
        if not languages or not types:
            return None, None
        
        total_count = len(languages)
        
        # Count occurrences
        language_counts = {}
        type_counts = {}
        
        for lang in languages:
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        for typ in types:
            type_counts[typ] = type_counts.get(typ, 0) + 1
        
        # Determine dominant language
        dominant_language = None
        if len(set(languages)) == 1:
            # Single language
            dominant_language = languages[0]
        else:
            # Check for >50% dominance
            for lang, count in language_counts.items():
                if count > total_count / 2:
                    dominant_language = lang
                    break
        
        # Determine dominant type
        dominant_type = None
        if len(set(types)) == 1:
            # Single type
            dominant_type = types[0]
        else:
            # Check for >50% dominance
            for typ, count in type_counts.items():
                if count > total_count / 2:
                    dominant_type = typ
                    break
        
        return dominant_language, dominant_type
    
    def _run_final_analysis(self, enable_program_level: bool = True, 
                          enable_copybook_analysis: bool = True) -> Dict[str, any]:
        """Run phase 8: Final analysis and reporting."""
        print(f"\n=== Phase 8: Final Analysis ===")
        
        # Collect all statistics
        inventory_stats = self.inventory_manager.get_inventory_stats()
        analysis_stats = self.dependency_analyzer.get_analysis_stats()
        
        # Calculate summary metrics
        total_artifacts = len(self.artifacts)
        artifacts_with_deps = len([r for r in self.analysis_results if r.has_dependencies])
        total_dependencies = sum(r.dependency_count for r in self.analysis_results)
        
        missing_artifacts = len(self.validation_result.missing_artifacts) if self.validation_result else 0
        completeness_score = self.validation_result.completeness_score if self.validation_result else 0.0
        
        # Calculate advanced analysis metrics
        program_boundaries_detected = sum(len(r.program_boundaries) for r in self.analysis_results)
        copybooks_analyzed = sum(len(r.copybook_analysis_results) for r in self.analysis_results 
                               if hasattr(r, 'copybook_analysis_results'))
        
        # Print final summary
        print(f"✓ Total artifacts discovered: {total_artifacts}")
        print(f"✓ Artifacts with dependencies: {artifacts_with_deps}")
        print(f"✓ Total dependencies found: {total_dependencies}")
        print(f"✓ Dependencies stored: {len(self.validation_result.validated_dependencies) if self.validation_result else 0}")
        print(f"✓ Missing artifacts: {missing_artifacts}")
        print(f"✓ Inventory completeness: {completeness_score:.1%}")
        
        if enable_program_level:
            print(f"✓ Program boundaries detected: {program_boundaries_detected}")
        
        if enable_copybook_analysis:
            print(f"✓ Copybooks analyzed: {copybooks_analyzed}")
        
        # Build summary with advanced analysis metrics
        summary = {
            'total_artifacts': total_artifacts,
            'artifacts_with_dependencies': artifacts_with_deps,
            'total_dependencies': total_dependencies,
            'dependencies_stored': len(self.validation_result.validated_dependencies) if self.validation_result else 0,
            'missing_artifacts': missing_artifacts,
            'completeness_score': completeness_score
        }
        
        # Add advanced analysis metrics if enabled
        if enable_program_level:
            summary['program_boundaries_detected'] = program_boundaries_detected
        
        if enable_copybook_analysis:
            summary['copybooks_analyzed'] = copybooks_analyzed
        
        return {
            'summary': summary,
            'inventory_stats': inventory_stats,
            'analysis_stats': analysis_stats,
            'validation_result': self.validation_result,
            'artifacts': self.artifacts,
            'analysis_results': self.analysis_results
        }

    def _create_cics_transaction_dependencies(self) -> None:
        """
        Create CICS_TRANSACTION dependencies from inventory_cics table.
        
        The migration flow builder expects entry points to be stored as dependencies
        in the artifact_dependencies table. This method creates dependencies linking
        CICS transactions to their associated programs.
        
        This is called after Phase 7 (dependency storage) when the artifact_dependencies
        table exists.
        """
        cursor = self.database.cursor()
        
        # Check if inventory_cics table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='inventory_cics'
        """)
        if not cursor.fetchone():
            return  # No CICS inventory, skip
        
        # Get CICS transactions with programs
        cursor.execute("""
            SELECT resource_name, program_name
            FROM inventory_cics
            WHERE resource_type = 'TRANSACTION' AND program_name IS NOT NULL
        """)
        
        transactions = cursor.fetchall()
        if not transactions:
            return
        
        created = 0
        for trans_id, program_name in transactions:
            # Check if dependency already exists
            cursor.execute("""
                SELECT COUNT(*) FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND target_artifact_name = ?
                  AND dependency_type = 'CICS_TRANSACTION'
            """, (trans_id, program_name))
            
            if cursor.fetchone()[0] > 0:
                continue
            
            # Create dependency
            cursor.execute("""
                INSERT INTO artifact_dependencies (
                    source_artifact_name,
                    source_artifact_type,
                    target_artifact_name,
                    target_artifact_type,
                    dependency_type,
                    line_number
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trans_id,
                'TRANSACTION',
                program_name,
                'PROGRAM',
                'CICS_TRANSACTION',
                None
            ))
            
            created += 1
        
        if created > 0:
            self.database.commit()
            print(f"✓ Created {created} CICS transaction dependencies")

    def _create_jcl_program_dependencies(self) -> None:
        """
        Create JCL→PROGRAM dependencies by parsing JCL files.
        
        The migration flow builder expects batch entry points to be stored as dependencies
        in the artifact_dependencies table with type 'EXEC_PGM'. This method parses JCL
        files from inventory and creates dependencies for EXEC PGM= statements.
        
        This is called after Phase 7 (dependency storage) when the artifact_dependencies
        table exists.
        """
        from .parsers.jcl_parser import JCLDependencyParser
        
        cursor = self.database.cursor()
        
        # Get all JCL files from inventory
        cursor.execute("""
            SELECT artifact_name, file_path
            FROM inventory
            WHERE language = 'JCL' AND artifact_type = 'JCL'
        """)
        
        jcl_files = cursor.fetchall()
        if not jcl_files:
            return
        
        parser = JCLDependencyParser()
        created = 0
        skipped_system = 0
        skipped_missing = 0
        
        # System/utility programs to skip (not application entry points)
        system_programs = {
            'IDCAMS', 'IEFBR14', 'SORT', 'IEBGENER', 'SDSF', 'IEBCOPY',
            'IEBUPDTE', 'IEBPTPCH', 'IEBCOMPR', 'IEBDG', 'IEBISAM',
            'DFHCSDUP', 'DFHRMUTL', 'DFHSM', 'DFSORT', 'ICETOOL'
        }
        
        for jcl_name, jcl_path in jcl_files:
            try:
                # Read and parse JCL file
                with open(jcl_path, 'r') as f:
                    jcl_content = f.read()
                
                dependencies = parser.parse(jcl_content)
                programs = dependencies.get('programs', [])
                procs = dependencies.get('procs', [])
                
                # Resolve proc names to actual program names by parsing PROC files
                resolved_from_procs = self._resolve_proc_to_programs(procs, jcl_path)
                
                # Combine programs (from EXEC PGM=) and resolved proc targets
                all_targets = list(programs)
                for prog_name in resolved_from_procs:
                    if prog_name not in all_targets:
                        all_targets.append(prog_name)
                
                # Fallback: if proc couldn't be resolved, add proc name itself
                # so the flow builder can still find entry points
                for proc_name in procs:
                    if proc_name not in resolved_from_procs.values() and proc_name not in all_targets:
                        # Check if any resolved program came from this proc
                        if proc_name not in resolved_from_procs:
                            all_targets.append(proc_name)
                
                for program_name in all_targets:
                    # Skip system/utility programs
                    if program_name.upper() in system_programs:
                        skipped_system += 1
                        continue
                    
                    # Check if program exists in inventory (for reporting, but still create dependency)
                    cursor.execute("""
                        SELECT COUNT(*) FROM inventory
                        WHERE artifact_name = ? AND artifact_type = 'PROGRAM'
                    """, (program_name,))
                    
                    program_exists = cursor.fetchone()[0] > 0
                    if not program_exists:
                        # Program not in inventory - might be external or unsupported language
                        # Still create the dependency so flows can be built
                        skipped_missing += 1
                    
                    # Check if dependency already exists
                    cursor.execute("""
                        SELECT COUNT(*) FROM artifact_dependencies
                        WHERE source_artifact_name = ?
                          AND target_artifact_name = ?
                          AND dependency_type = 'EXEC_PGM'
                    """, (jcl_name, program_name))
                    
                    if cursor.fetchone()[0] > 0:
                        continue
                    
                    # Create dependency (even if program doesn't exist in inventory)
                    # This allows flows to be built and shows missing programs
                    cursor.execute("""
                        INSERT INTO artifact_dependencies (
                            source_artifact_name,
                            source_artifact_type,
                            target_artifact_name,
                            target_artifact_type,
                            dependency_type,
                            source_file_path,
                            line_number
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        jcl_name,
                        'JCL',
                        program_name,
                        'PROGRAM',
                        'EXEC_PGM',
                        jcl_path,
                        None
                    ))
                    
                    created += 1
                    
            except Exception as e:
                print(f"  ⚠ Warning: Error parsing JCL {jcl_name}: {e}")
        
        if created > 0:
            self.database.commit()
            print(f"✓ Created {created} JCL→PROGRAM dependencies")
            if skipped_system > 0:
                print(f"  ℹ Skipped {skipped_system} system/utility programs")
            if skipped_missing > 0:
                print(f"  ⚠ {skipped_missing} programs not in inventory (may be external or unsupported language)")
    def _resolve_proc_to_programs(self, proc_names: list, jcl_path: str) -> dict:
        """
        Resolve proc names to actual program names by finding and parsing PROC files.

        Looks for PROC files in the same directory as the JCL file (and inventory),
        then parses EXEC PGM= statements within them to find the actual programs invoked.

        Args:
            proc_names: List of proc names referenced by JCL (e.g., ['EO96W', 'EO97W'])
            jcl_path: Path to the JCL file (used to find sibling PROC files)

        Returns:
            Dictionary mapping resolved program names to their source proc name.
            E.g., {'EA20IS': 'EO96W', 'EO97': 'EO97W'}
        """
        import re
        from pathlib import Path

        resolved = {}
        if not proc_names:
            return resolved

        jcl_dir = Path(jcl_path).parent

        # Also check inventory for proc file paths
        cursor = self.database.cursor()

        exec_pgm_pattern = re.compile(
            r'EXEC\s+PGM=([A-Z0-9#@$]+)',
            re.IGNORECASE
        )
        # Pattern to match symbolic parameter references like &EA20PGM
        symbolic_default_pattern = re.compile(
            r'PROC\s+.*?(\w+)=([A-Z0-9#@$]+)',
            re.IGNORECASE
        )

        for proc_name in proc_names:
            proc_file = None

            # Try common extensions for proc files
            for ext in ['.proc', '.PROC', '.prc', '.PRC', '']:
                candidate = jcl_dir / f"{proc_name}{ext}"
                if candidate.exists():
                    proc_file = candidate
                    break

            # Also try inventory lookup
            if not proc_file:
                try:
                    cursor.execute("""
                        SELECT file_path FROM inventory
                        WHERE artifact_name = ? AND (artifact_type = 'JCL' OR artifact_type = 'PROC')
                    """, (proc_name,))
                    row = cursor.fetchone()
                    if row and row[0] and Path(row[0]).exists():
                        proc_file = Path(row[0])
                except Exception:
                    pass

            if not proc_file:
                continue

            try:
                with open(proc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    proc_content = f.read()

                # First, extract PROC statement default parameter values
                # e.g., //EO96 PROC EA20PGM=EA20IS means &EA20PGM defaults to EA20IS
                param_defaults = {}
                for line in proc_content.split('\n'):
                    if 'PROC ' in line.upper() or 'PROC\t' in line.upper():
                        # Parse all param=value pairs from PROC statement and continuations
                        proc_block = line
                        # Gather continuation lines
                        lines = proc_content.split('\n')
                        idx = lines.index(line) if line in lines else -1
                        if idx >= 0:
                            for i in range(idx + 1, len(lines)):
                                cont = lines[i]
                                if cont.startswith('//') and len(cont) > 2 and cont[2] == ' ':
                                    proc_block += ' ' + cont[2:].strip()
                                else:
                                    break

                        # Extract param=value pairs
                        for match in re.finditer(r'(\w+)=([A-Z0-9#@$]+)', proc_block, re.IGNORECASE):
                            param_name, param_value = match.groups()
                            if param_name.upper() != 'PROC':
                                param_defaults[param_name.upper()] = param_value
                        break

                # Find all EXEC PGM= statements, resolving symbolic parameters
                programs_found = set()
                for match in exec_pgm_pattern.finditer(proc_content):
                    pgm_ref = match.group(1)
                    if pgm_ref.startswith('&'):
                        # Resolve symbolic parameter using PROC defaults
                        param_name = pgm_ref[1:].upper()
                        if param_name in param_defaults:
                            programs_found.add(param_defaults[param_name])
                    else:
                        programs_found.add(pgm_ref)

                # System utilities to skip
                system_progs = {
                    'IDCAMS', 'IEFBR14', 'SORT', 'IEBGENER', 'SDSF', 'IEBCOPY',
                    'IEBUPDTE', 'IEBPTPCH', 'IEBCOMPR', 'IEBDG', 'IEBISAM',
                    'DFHCSDUP', 'DFHRMUTL', 'DFHSM', 'DFSORT', 'ICETOOL',
                    'CHATTER', 'PM62', 'PRINT'
                }

                for pgm in programs_found:
                    if pgm.upper() not in system_progs:
                        resolved[pgm] = proc_name

            except Exception as e:
                print(f"  ⚠ Warning: Error resolving proc {proc_name}: {e}")

        return resolved
