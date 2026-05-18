"""
High-level Python API for Legacy Analyzer.

This module provides a simplified interface to all Legacy Analyzer functionality,
making it easy to use programmatically without dealing with low-level details.
"""

from typing import List, Dict, Optional, Set
from pathlib import Path
from shared.database.adapters import SQLiteAdapter

from .models.dependency import Dependency
from .models.flow import ProgramFlow
from .models.complexity import ComplexityMetrics, ComplexityThresholds
from .models.missing_artifact import MissingArtifact, CompletenessReport
from .models.package import MigrationPackage, PackageConstraints

from .analysis.flow_analyzer import FlowAnalyzer
from .analysis.complexity_analyzer import ComplexityAnalyzer
from .analysis.missing_code_detector import MissingCodeDetector
from .analysis.call_graph import CallGraphBuilder

from .migration.package_builder import PackageBuilder

from .visualization.report_generator import ReportGenerator, AnalysisResults


class LegacyAnalyzerAPI:
    """
    High-level API for Legacy Analyzer.
    
    Provides simplified access to all analysis functionality including:
    - Program flow analysis
    - Complexity analysis
    - Missing code detection
    - Migration package planning
    - Report generation
    
    Example:
        >>> api = LegacyAnalyzerAPI("analyzer.db")
        >>> flow = api.analyze_flow("PAYROLL1")
        >>> complexity = api.analyze_complexity("PAYROLL1", source_code)
        >>> missing = api.detect_missing_artifacts()
        >>> package = api.create_package("Payroll", ["PAYROLL1", "PAYCALC"])
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the API with a database connection.
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self.db = SQLiteAdapter(database_path)
        self.db.connect()
        
        # Initialize components lazily
        self._flow_analyzer: Optional[FlowAnalyzer] = None
        self._complexity_analyzer: Optional[ComplexityAnalyzer] = None
        self._missing_detector: Optional[MissingCodeDetector] = None
        self._package_builder: Optional[PackageBuilder] = None
        self._report_generator: Optional[ReportGenerator] = None
        self._call_graph_builder: Optional[CallGraphBuilder] = None
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # Flow Analysis Methods
    
    def analyze_flow(
        self,
        start_program: str,
        max_depth: int = 10
    ) -> ProgramFlow:
        """
        Analyze program flow starting from a specific program.
        
        Args:
            start_program: Program to start analysis from
            max_depth: Maximum depth to traverse (default 10)
            
        Returns:
            ProgramFlow object with complete flow information
            
        Example:
            >>> flow = api.analyze_flow("PAYROLL1")
            >>> print(f"Flow depth: {flow.depth}")
            >>> print(f"Programs in flow: {len(flow.programs)}")
        """
        if not self._flow_analyzer:
            dependencies = self._load_dependencies()
            self._flow_analyzer = FlowAnalyzer(dependencies)
        
        return self._flow_analyzer.analyze_flow(start_program, max_depth)
    
    def build_call_graph(
        self,
        programs: Optional[List[str]] = None
    ):
        """
        Build call graph for specified programs or all programs.
        
        Args:
            programs: List of program names (None = all programs)
            
        Returns:
            CallGraph object
            
        Example:
            >>> graph = api.build_call_graph(["PAYROLL1", "BILLING2"])
            >>> print(f"Nodes: {len(graph.nodes)}")
            >>> print(f"Edges: {len(graph.edges)}")
        """
        if not self._call_graph_builder:
            dependencies = self._load_dependencies()
            self._call_graph_builder = CallGraphBuilder(dependencies)
        
        if programs is None:
            # Get all programs from database
            programs = self._get_all_programs()
        
        return self._call_graph_builder.build_call_graph(programs)
    
    def get_entry_points(self) -> List[str]:
        """
        Get all entry point programs (programs that are never called).
        
        Returns:
            List of entry point program names
            
        Example:
            >>> entry_points = api.get_entry_points()
            >>> print(f"Found {len(entry_points)} entry points")
        """
        if not self._flow_analyzer:
            dependencies = self._load_dependencies()
            self._flow_analyzer = FlowAnalyzer(dependencies)
        
        # Get all programs from inventory to include programs with no dependencies
        all_programs = set()
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT DISTINCT artifact_name FROM inventory WHERE artifact_type='PROGRAM'")
            all_programs = {row[0] for row in cursor.fetchall()}
        except Exception:
            # If query fails, proceed without inventory programs
            pass
        
        return self._flow_analyzer.get_entry_points(all_programs)
    
    def get_entry_points_with_metadata(
        self,
        include_disabled: bool = False,
        include_inferred: bool = True
    ) -> List:
        """
        Get entry points with full metadata (CICS transactions, JCL, etc.).
        
        This method returns EntryPoint objects with complete metadata including
        transaction IDs, JCL names, confidence levels, and more. It integrates
        CICS metadata from inventory_cics table and JCL dependencies.
        
        Args:
            include_disabled: If True, include DISABLED CICS transactions
            include_inferred: If True, include inferred entry points from code analysis
            
        Returns:
            List of EntryPoint objects with metadata
            
        Example:
            >>> entry_points = api.get_entry_points_with_metadata()
            >>> for ep in entry_points:
            ...     print(f"{ep.program_name} ({ep.entry_type})")
        """
        if not self._flow_analyzer:
            dependencies = self._load_dependencies()
            # Pass database connection to FlowAnalyzer for metadata access
            self._flow_analyzer = FlowAnalyzer(dependencies, db_connection=self.db.conn)
        
        # Get all programs from inventory
        all_programs = set()
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT DISTINCT artifact_name FROM inventory WHERE artifact_type='PROGRAM'")
            all_programs = {row[0] for row in cursor.fetchall()}
        except Exception:
            # If query fails, proceed without inventory programs
            pass
        
        return self._flow_analyzer.get_entry_points_with_metadata(
            all_programs_in_inventory=all_programs,
            include_disabled=include_disabled,
            include_inferred=include_inferred
        )
    
    def detect_circular_dependencies(self) -> List:
        """
        Detect all circular dependencies in the system.
        
        Returns:
            List of CircularDependency objects
            
        Example:
            >>> cycles = api.detect_circular_dependencies()
            >>> for cycle in cycles:
            ...     print(f"Cycle: {' -> '.join(cycle.artifacts)}")
        """
        if not self._flow_analyzer:
            dependencies = self._load_dependencies()
            self._flow_analyzer = FlowAnalyzer(dependencies)
        
        from .analysis.circular_detector import CircularDependencyDetector
        detector = CircularDependencyDetector(self._load_dependencies())
        return detector.detect_all_cycles()
    
    # Complexity Analysis Methods
    
    def analyze_complexity(
        self,
        program_name: str,
        source_code: str,
        language: str,
        dependency_count_in: int = 0,
        dependency_count_out: int = 0
    ) -> ComplexityMetrics:
        """
        Analyze complexity of a single program.
        
        Args:
            program_name: Name of the program
            source_code: Source code content
            language: Programming language (COBOL, PLI, JCL, etc.)
            dependency_count_in: Number of incoming dependencies
            dependency_count_out: Number of outgoing dependencies
            
        Returns:
            ComplexityMetrics object
            
        Example:
            >>> with open("PAYROLL1.cbl") as f:
            ...     source = f.read()
            >>> metrics = api.analyze_complexity("PAYROLL1", source, "COBOL")
            >>> print(f"Complexity tier: {metrics.complexity_tier}")
        """
        if not self._complexity_analyzer:
            self._complexity_analyzer = ComplexityAnalyzer(self.db)
        
        return self._complexity_analyzer.analyze_program(
            program_name=program_name,
            source_code=source_code,
            language=language,
            dependency_count_in=dependency_count_in,
            dependency_count_out=dependency_count_out
        )
    
    def analyze_all_complexity(
        self,
        programs: Dict[str, Dict]
    ) -> Dict[str, ComplexityMetrics]:
        """
        Analyze complexity of multiple programs.
        
        Args:
            programs: Dictionary mapping program names to program info
                     Each program info should have:
                     - 'source_code': str
                     - 'language': str
                     - 'dependency_count_in': int (optional)
                     - 'dependency_count_out': int (optional)
        
        Returns:
            Dictionary mapping program names to ComplexityMetrics
            
        Example:
            >>> programs = {
            ...     "PAYROLL1": {"source_code": code1, "language": "COBOL"},
            ...     "BILLING2": {"source_code": code2, "language": "COBOL"}
            ... }
            >>> results = api.analyze_all_complexity(programs)
        """
        if not self._complexity_analyzer:
            self._complexity_analyzer = ComplexityAnalyzer(self.db)
        
        return self._complexity_analyzer.analyze_all_programs(programs)
    
    def get_complexity_thresholds(self) -> ComplexityThresholds:
        """
        Get current complexity thresholds.
        
        Returns:
            ComplexityThresholds object
        """
        if not self._complexity_analyzer:
            self._complexity_analyzer = ComplexityAnalyzer(self.db)
        
        return self._complexity_analyzer.thresholds
    
    def set_complexity_thresholds(self, thresholds: ComplexityThresholds):
        """
        Set custom complexity thresholds.
        
        Args:
            thresholds: ComplexityThresholds object
        """
        if not self._complexity_analyzer:
            self._complexity_analyzer = ComplexityAnalyzer(self.db)
        
        self._complexity_analyzer.thresholds = thresholds
    
    # Missing Code Detection Methods
    
    def detect_missing_programs(self) -> List[MissingArtifact]:
        """
        Find programs that are called but not found in inventory.
        
        Returns:
            List of MissingArtifact objects for programs
            
        Example:
            >>> missing = api.detect_missing_programs()
            >>> for artifact in missing:
            ...     print(f"{artifact.artifact_name}: {artifact.severity}")
        """
        if not self._missing_detector:
            dependencies = self._load_dependencies()
            self._missing_detector = MissingCodeDetector(dependencies, self.db.conn)
        
        return self._missing_detector.detect_missing_programs()
    
    def detect_missing_copybooks(self) -> List[MissingArtifact]:
        """
        Find copybooks that are included but not found in inventory.
        
        Returns:
            List of MissingArtifact objects for copybooks
        """
        if not self._missing_detector:
            dependencies = self._load_dependencies()
            self._missing_detector = MissingCodeDetector(dependencies, self.db.conn)
        
        return self._missing_detector.detect_missing_copybooks()
    
    def detect_missing_datasets(self) -> List[MissingArtifact]:
        """
        Find datasets that are referenced but not found in inventory.
        
        Returns:
            List of MissingArtifact objects for datasets
        """
        if not self._missing_detector:
            dependencies = self._load_dependencies()
            self._missing_detector = MissingCodeDetector(dependencies, self.db.conn)
        
        return self._missing_detector.detect_missing_datasets()
    
    def detect_all_missing(self) -> List[MissingArtifact]:
        """
        Detect all missing artifacts (programs, copybooks, datasets).
        
        Returns:
            Combined list of all missing artifacts
        """
        if not self._missing_detector:
            dependencies = self._load_dependencies()
            self._missing_detector = MissingCodeDetector(dependencies, self.db.conn)
        
        return self._missing_detector.detect_all_missing()
    
    def calculate_completeness(self) -> CompletenessReport:
        """
        Calculate inventory completeness score.
        
        Returns:
            CompletenessReport with detailed completeness metrics
            
        Example:
            >>> report = api.calculate_completeness()
            >>> print(f"Overall completeness: {report.overall_completeness:.1%}")
        """
        if not self._missing_detector:
            dependencies = self._load_dependencies()
            self._missing_detector = MissingCodeDetector(dependencies, self.db.conn)
        
        return self._missing_detector.calculate_completeness_score()
    
    # Migration Flow Export Methods
    
    def build_migration_flows(
        self,
        external_config_path: Optional[str] = None
    ) -> List[str]:
        """
        Build migration flows for all entry points.
        
        This method analyzes all entry point programs and builds migration-focused
        flow data including scope, interfaces, data operations, complexity metrics,
        and flow dependencies. The data is stored in migration_flows tables.
        
        Args:
            external_config_path: Optional path to external configuration YAML file
                                 for defining external programs and callers
        
        Returns:
            List of flow IDs that were built
            
        Raises:
            FileNotFoundError: If external_config_path is provided but file doesn't exist
            ValueError: If database is not properly initialized
            Exception: If flow building fails
            
        Example:
            >>> api = LegacyAnalyzerAPI("analyzer.db")
            >>> flow_ids = api.build_migration_flows()
            >>> print(f"Built {len(flow_ids)} migration flows")
            
            >>> # With external configuration
            >>> flow_ids = api.build_migration_flows(
            ...     external_config_path="external_config.yaml"
            ... )
        """
        from .migration.flow_builder import MigrationFlowBuilder
        from .migration.external_config import ExternalConfigLoader
        from .migration.schema import MigrationFlowSchema
        
        # Validate database connection
        if not self.db or not self.db.conn:
            raise ValueError("Database connection is not initialized")
        
        # Create migration flow schema if it doesn't exist
        try:
            schema = MigrationFlowSchema(self.db.conn)
            if not schema.is_schema_complete():
                schema.create_schema(verbose=False)
        except Exception as e:
            raise Exception(f"Failed to create migration flow schema: {e}")
        
        # Validate external config file if provided
        if external_config_path:
            config_path = Path(external_config_path)
            if not config_path.exists():
                raise FileNotFoundError(f"External configuration file not found: {external_config_path}")
            
            # Load external configuration
            try:
                config_loader = ExternalConfigLoader(self.db.conn)
                config_loader.load_external_config(external_config_path, verbose=False)
            except Exception as e:
                raise Exception(f"Failed to load external configuration: {e}")
        
        # Build flows
        try:
            builder = MigrationFlowBuilder(self.db.conn)
            flow_ids = builder.build_all_flows()
            
            if not flow_ids:
                print("Warning: No flows were built. Check that entry points exist in the database.")
            
            return flow_ids
        except Exception as e:
            raise Exception(f"Failed to build migration flows: {e}")
    
    def export_migration_flows(
        self,
        output_file: str,
        flow_ids: Optional[List[str]] = None,
        min_complexity: Optional[str] = None,
        business_domain: Optional[str] = None,
        entry_type: Optional[str] = None,
        include_priority: bool = True,
        include_business_domain: bool = True,
        extended_scope: bool = False,
        sort_order: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Export migration flows to JSON format.
        
        This method exports flows from the migration_flows tables to a
        migration-focused JSON format that clearly separates scope from
        interfaces and includes complexity metrics and data operations.
        
        Args:
            output_file: Path to write JSON output
            flow_ids: Optional list of specific flow IDs to export (None = all)
            min_complexity: Minimum complexity tier to include
                          ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')
            business_domain: Filter by business domain
            entry_type: Filter by entry point type
                       ('JCL', 'CICS_TRANSACTION', 'CICS_PROGRAM', 'SCREEN', etc.)
            include_priority: Include priority field in output (default True)
            include_business_domain: Include businessDomain field in output (default True)
            extended_scope: Include utility metadata in scope output (default False)
            sort_order: Sort flows by migration strategy (default None - database order)
                       Options: 'complexity-asc', 'complexity-desc', 'independence',
                               'dependencies', 'name'
        
        Returns:
            Dictionary with 'flows' key containing list of flow objects
            
        Raises:
            ValueError: If database is not initialized or invalid parameters provided
            FileNotFoundError: If output directory doesn't exist
            Exception: If export fails
            
        Example:
            >>> api = LegacyAnalyzerAPI("analyzer.db")
            >>> 
            >>> # Export all flows
            >>> result = api.export_migration_flows("flows.json")
            >>> print(f"Exported {len(result['flows'])} flows")
            >>> 
            >>> # Export specific flows
            >>> result = api.export_migration_flows(
            ...     output_file="payroll_flows.json",
            ...     flow_ids=["FLOW_PAYROLL1", "FLOW_PAYCALC"]
            ... )
            >>> 
            >>> # Export with filters
            >>> result = api.export_migration_flows(
            ...     output_file="high_complexity.json",
            ...     min_complexity="HIGH",
            ...     business_domain="Finance"
            ... )
        """
        from .migration.flow_exporter import MigrationFlowExporter
        
        # Validate database connection
        if not self.db or not self.db.conn:
            raise ValueError("Database connection is not initialized")
        
        # Validate output file path
        if not output_file:
            raise ValueError("output_file parameter is required")
        
        output_path = Path(output_file)
        if not output_path.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {output_path.parent}")
        
        # Validate min_complexity if provided
        if min_complexity:
            valid_tiers = ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
            if min_complexity.upper() not in valid_tiers:
                raise ValueError(
                    f"Invalid min_complexity: {min_complexity}. "
                    f"Must be one of: {', '.join(valid_tiers)}"
                )
            min_complexity = min_complexity.upper()
        
        # Validate flow_ids if provided
        if flow_ids is not None:
            if not isinstance(flow_ids, list):
                raise ValueError("flow_ids must be a list of strings")
            if not flow_ids:
                print("Warning: Empty flow_ids list provided. No flows will be exported.")
        
        # Check if migration_flows table exists
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='migration_flows'
        """)
        if not cursor.fetchone():
            raise ValueError(
                "Migration flows table not found. "
                "Please run build_migration_flows() first."
            )
        
        # Create exporter and export flows
        try:
            exporter = MigrationFlowExporter(self.db.conn)
            
            result = exporter.export_all_flows(
                output_file=output_file,
                flow_ids=flow_ids,
                min_complexity=min_complexity,
                business_domain=business_domain,
                entry_type=entry_type,
                extended_scope=extended_scope,
                sort_order=sort_order
            )
            
            if not result.get('flows'):
                print("Warning: No flows matched the specified filters.")
            
            return result
        except Exception as e:
            raise Exception(f"Failed to export migration flows: {e}")
    
    # Migration Package Methods
    
    def create_package(
        self,
        name: str,
        seed_artifacts: List[str],
        include_transitive: bool = True,
        max_depth: Optional[int] = None,
        constraints: Optional[PackageConstraints] = None
    ) -> MigrationPackage:
        """
        Create a migration package from seed artifacts.
        
        Args:
            name: Package name
            seed_artifacts: List of seed artifact names
            include_transitive: Include transitive dependencies (default True)
            max_depth: Maximum depth for transitive dependencies
            constraints: Package constraints to validate against
            
        Returns:
            MigrationPackage object
            
        Example:
            >>> package = api.create_package(
            ...     "Payroll",
            ...     ["PAYROLL1", "PAYCALC"],
            ...     include_transitive=True
            ... )
            >>> print(f"Package has {len(package.artifacts)} artifacts")
        """
        if not self._package_builder:
            self._package_builder = PackageBuilder(self.db)
        
        return self._package_builder.create_package(
            name=name,
            seed_artifacts=seed_artifacts,
            include_transitive=include_transitive,
            max_depth=max_depth,
            constraints=constraints
        )
    
    def detect_package_conflicts(
        self,
        packages: List[MigrationPackage]
    ) -> List:
        """
        Detect artifacts that appear in multiple packages.
        
        Args:
            packages: List of MigrationPackage objects
            
        Returns:
            List of PackageConflict objects
        """
        if not self._package_builder:
            self._package_builder = PackageBuilder(self.db)
        
        return self._package_builder.detect_conflicts(packages)
    
    def validate_package(
        self,
        package: MigrationPackage,
        constraints: Optional[PackageConstraints] = None
    ) -> tuple:
        """
        Validate a package against constraints.
        
        Args:
            package: MigrationPackage to validate
            constraints: PackageConstraints (optional)
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        if not self._package_builder:
            self._package_builder = PackageBuilder(self.db)
        
        return self._package_builder.validate_package(package, constraints)
    
    # Visualization and Reporting Methods
    
    def export_flow_mermaid(
        self,
        flow: ProgramFlow,
        output_file: Optional[str] = None
    ) -> str:
        """
        Export program flow as Mermaid diagram.
        
        Args:
            flow: ProgramFlow object
            output_file: Optional file path to write to
            
        Returns:
            Mermaid diagram as string
        """
        from .visualization.graph_renderer import GraphRenderer
        
        renderer = GraphRenderer()
        mermaid = renderer.render_mermaid(flow)
        
        if output_file:
            Path(output_file).write_text(mermaid)
        
        return mermaid
    
    def export_flow_dot(
        self,
        flow: ProgramFlow,
        output_file: Optional[str] = None
    ) -> str:
        """
        Export program flow as DOT format for Graphviz.
        
        Args:
            flow: ProgramFlow object
            output_file: Optional file path to write to
            
        Returns:
            DOT format as string
        """
        from .visualization.graph_renderer import GraphRenderer
        
        renderer = GraphRenderer()
        dot = renderer.render_dot(flow)
        
        if output_file:
            Path(output_file).write_text(dot)
        
        return dot
    
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
        if not self._report_generator:
            self._report_generator = ReportGenerator()
        
        return self._report_generator.generate_executive_summary(analysis_results)
    
    def generate_artifact_report(
        self,
        artifact_name: str,
        **kwargs
    ) -> str:
        """
        Generate detailed artifact report.
        
        Args:
            artifact_name: Name of the artifact
            **kwargs: Additional report parameters
            
        Returns:
            Detailed artifact report as formatted text
        """
        if not self._report_generator:
            self._report_generator = ReportGenerator()
        
        return self._report_generator.generate_artifact_report(
            artifact_name=artifact_name,
            **kwargs
        )
    
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
        if not self._report_generator:
            self._report_generator = ReportGenerator()
        
        return self._report_generator.generate_package_report(package)
    
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
        if not self._report_generator:
            self._report_generator = ReportGenerator()
        
        return self._report_generator.generate_complexity_summary(
            complexity_metrics,
            top_n
        )
    
    # Helper Methods
    
    def _load_dependencies(self) -> List[Dependency]:
        """Load all dependencies from database."""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT source_artifact_name, source_artifact_type, target_artifact_name, target_artifact_type,
                   dependency_type, source_file_path, line_number
            FROM artifact_dependencies
        """)
        
        dependencies = []
        for row in cursor.fetchall():
            dep = Dependency(
                source_artifact=row[0],
                source_type=row[1],
                target_artifact=row[2],
                target_type=row[3],
                dependency_type=row[4],
                source_file=row[5],
                line_number=row[6]
            )
            dependencies.append(dep)
        
        return dependencies
    
    def _get_all_programs(self) -> List[str]:
        """Get all program names from database."""
        cursor = self.db.conn.cursor()
        
        programs = set()
        
        # Get from programs table
        try:
            cursor.execute("SELECT program_name FROM programs")
            programs.update(row[0] for row in cursor.fetchall())
        except Exception:
            pass
        
        # Get from dependencies
        try:
            cursor.execute("""
                SELECT DISTINCT source_artifact_name FROM artifact_dependencies
                WHERE source_artifact_type = 'PROGRAM'
                UNION
                SELECT DISTINCT target_artifact_name FROM artifact_dependencies
                WHERE target_artifact_type = 'PROGRAM'
            """)
            programs.update(row[0] for row in cursor.fetchall())
        except Exception:
            pass
        
        return list(programs)
