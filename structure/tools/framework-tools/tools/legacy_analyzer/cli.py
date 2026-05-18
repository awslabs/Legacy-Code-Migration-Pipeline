"""
New CLI for Legacy Analyzer with proper flow separation.

This CLI uses the refactored architecture with proper separation of concerns:
1. Complete inventory discovery and population
2. Dependency analysis with validation
3. Dependency storage with complete context
"""

import argparse
import sys
from pathlib import Path

from shared.database.adapters import SQLiteAdapter
from .analysis_orchestrator import AnalysisOrchestrator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Legacy Analyzer - Refactored Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete analysis workflow (now includes advanced analysis)
  python -m legacy_analyzer analyze --source-dir ./code --db analyzer.db
  
  # Complete analysis with advanced features disabled
  python -m legacy_analyzer analyze --source-dir ./code --db analyzer.db --no-program-level --no-copybook-analysis
  
  # Inventory only (discovery phase)
  python -m legacy_analyzer inventory --source-dir ./code --db analyzer.db
  
  # Dependencies only (requires existing inventory)
  python -m legacy_analyzer dependencies --db analyzer.db
  
  # Program-level analysis only
  python -m legacy_analyzer program-level --source-dir ./code --db analyzer.db
  
  # Copybook analysis only
  python -m legacy_analyzer copybook-analysis --source-dir ./code --db analyzer.db
  
  # Parse specialized artifacts only (CSD, JCL, etc.)
  python -m legacy_analyzer artifacts --source-dir ./code --db analyzer.db
  python -m legacy_analyzer artifacts --source-dir ./code --db analyzer.db --type csd
  python -m legacy_analyzer artifacts --source-dir ./code --db analyzer.db --type jcl
  
  # Load inventory from CSV files
  python -m legacy_analyzer load --type cics --file cics_inventory.csv --db analyzer.db
  python -m legacy_analyzer load --type jcl --file jcl_inventory.csv --db analyzer.db
  python -m legacy_analyzer load --type programs --file programs.csv --db analyzer.db
  python -m legacy_analyzer load --type copybooks --file copybooks.csv --db analyzer.db
  python -m legacy_analyzer load --type datasets --file datasets.csv --db analyzer.db
  
  # Generate summary report
  python -m legacy_analyzer report summary --db analyzer.db
  python -m legacy_analyzer report summary --db analyzer.db --output custom/path/summary.md
  
  # Generate status report
  python -m legacy_analyzer report status --db analyzer.db --output-dir ./results/analysis
  python -m legacy_analyzer report status --db analyzer.db --output-dir ./results/analysis --project-name "My Project"
  
  # Check analysis status
  python -m legacy_analyzer status --db analyzer.db
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Complete analysis command
    analyze_parser = subparsers.add_parser('analyze', 
                                          help='Run complete analysis workflow')
    analyze_parser.add_argument('--source-dir', required=True, 
                               help='Source code directory')
    analyze_parser.add_argument('--db', required=True, 
                               help='Path to database file')
    analyze_parser.add_argument('--complexity', action='store_true',
                               help='Calculate complexity metrics')
    analyze_parser.add_argument('--no-program-level', action='store_true',
                               help='Disable program-level analysis')
    analyze_parser.add_argument('--no-copybook-analysis', action='store_true',
                               help='Disable copybook analysis')
    analyze_parser.add_argument('--log-file', 
                               help='Path to detailed log file')
    
    # Inventory only command
    inventory_parser = subparsers.add_parser('inventory',
                                           help='Run inventory discovery only')
    inventory_parser.add_argument('--source-dir', required=True,
                                 help='Source code directory')
    inventory_parser.add_argument('--db', required=True,
                                 help='Path to database file')
    inventory_parser.add_argument('--log-file',
                                 help='Path to detailed log file')
    
    # Dependencies only command
    deps_parser = subparsers.add_parser('dependencies',
                                       help='Run dependency analysis only (requires existing inventory)')
    deps_parser.add_argument('--db', required=True,
                            help='Path to database file')
    deps_parser.add_argument('--complexity', action='store_true',
                            help='Calculate complexity metrics')
    deps_parser.add_argument('--no-program-level', action='store_true',
                            help='Disable program-level analysis')
    deps_parser.add_argument('--no-copybook-analysis', action='store_true',
                            help='Disable copybook analysis')
    deps_parser.add_argument('--log-file',
                            help='Path to detailed log file')
    
    # Specialized artifact parsing commands
    artifacts_parser = subparsers.add_parser('artifacts',
                                           help='Parse and load specialized artifacts only')
    artifacts_parser.add_argument('--source-dir', required=True,
                                help='Source code directory')
    artifacts_parser.add_argument('--db', required=True,
                                help='Path to database file')
    artifacts_parser.add_argument('--type', choices=['csd', 'jcl', 'all'], default='all',
                                help='Type of artifacts to parse (default: all)')
    artifacts_parser.add_argument('--log-file',
                                help='Path to detailed log file')
    
    # Program-level analysis command
    program_parser = subparsers.add_parser('program-level',
                                          help='Run program-level dependency analysis')
    program_parser.add_argument('--source-dir', required=True,
                               help='Source code directory')
    program_parser.add_argument('--db', required=True,
                               help='Path to database file')
    program_parser.add_argument('--log-file',
                               help='Path to detailed log file')
    
    # Copybook analysis command
    copybook_parser = subparsers.add_parser('copybook-analysis',
                                           help='Run copybook analysis')
    copybook_parser.add_argument('--source-dir', required=True,
                                help='Source code directory')
    copybook_parser.add_argument('--db', required=True,
                                help='Path to database file')
    copybook_parser.add_argument('--log-file',
                                help='Path to detailed log file')
    
    # Status command
    status_parser = subparsers.add_parser('status',
                                         help='Show analysis status')
    status_parser.add_argument('--db', required=True,
                              help='Path to database file')
    
    # Load command (backward compatibility)
    load_parser = subparsers.add_parser('load',
                                       help='Load inventory data from CSV files')
    load_parser.add_argument('--type', required=True,
                            choices=['cics', 'jcl', 'programs', 'copybooks', 'datasets'],
                            help='Type of inventory to load')
    load_parser.add_argument('--file', required=True,
                            help='Path to CSV file')
    load_parser.add_argument('--db', required=True,
                            help='Path to database file')
    
    # Service command (backward compatibility)
    service_parser = subparsers.add_parser('service',
                                          help='Service grouping analysis')
    service_subparsers = service_parser.add_subparsers(dest='service_command', help='Service commands')
    
    # Service candidates subcommand
    candidates_parser = service_subparsers.add_parser('candidates',
                                                     help='Identify service candidates')
    candidates_parser.add_argument('--db', required=True,
                                  help='Path to database file')
    candidates_parser.add_argument('--output',
                                  help='Output file path (optional)')
    candidates_parser.add_argument('--min-confidence',
                                  choices=['HIGH', 'MEDIUM', 'LOW'],
                                  help='Minimum confidence level to include')
    candidates_parser.add_argument('--format',
                                  choices=['json', 'markdown'],
                                  default='markdown',
                                  help='Output format (default: markdown)')
    
    # Flow command (backward compatibility)
    flow_parser = subparsers.add_parser('flow',
                                       help='Program flow analysis')
    flow_subparsers = flow_parser.add_subparsers(dest='flow_command', help='Flow commands')
    
    # Flow analyze subcommand
    flow_analyze_parser = flow_subparsers.add_parser('analyze',
                                                     help='Analyze program flow')
    flow_analyze_parser.add_argument('--program', required=True,
                                    help='Program name to analyze')
    flow_analyze_parser.add_argument('--db', required=True,
                                    help='Path to database file')
    flow_analyze_parser.add_argument('--max-depth', type=int, default=10,
                                    help='Maximum depth to traverse (default: 10)')
    flow_analyze_parser.add_argument('--output',
                                    help='Output file path (optional)')
    
    # Flow graph subcommand
    flow_graph_parser = flow_subparsers.add_parser('graph',
                                                   help='Generate flow graph')
    flow_graph_parser.add_argument('--db', required=True,
                                  help='Path to database file')
    flow_graph_parser.add_argument('--output', required=True,
                                  help='Output file path')
    flow_graph_parser.add_argument('--format',
                                  choices=['dot', 'json'],
                                  default='dot',
                                  help='Output format (default: dot)')
    
    # Flow entry-points subcommand
    flow_entry_points_parser = flow_subparsers.add_parser('entry-points',
                                                          help='Detect entry points')
    flow_entry_points_parser.add_argument('--db', required=True,
                                         help='Path to database file')
    flow_entry_points_parser.add_argument('--use-metadata', action='store_true',
                                         help='Use CICS/JCL metadata for enhanced detection')
    flow_entry_points_parser.add_argument('--include-disabled', action='store_true',
                                         help='Include disabled CICS transactions')
    flow_entry_points_parser.add_argument('--format',
                                         choices=['json', 'markdown'],
                                         default='markdown',
                                         help='Output format (default: markdown)')
    flow_entry_points_parser.add_argument('--output',
                                         help='Output file path (optional)')
    
    # Flow circular subcommand
    flow_circular_parser = flow_subparsers.add_parser('circular',
                                                      help='Detect circular dependencies')
    flow_circular_parser.add_argument('--db', required=True,
                                     help='Path to database file')
    flow_circular_parser.add_argument('--output',
                                     help='Output file path (optional)')
    flow_circular_parser.add_argument('--format',
                                     choices=['json', 'text'],
                                     default='text',
                                     help='Output format (default: text)')
    
    # Metadata command (backward compatibility)
    metadata_parser = subparsers.add_parser('metadata',
                                           help='CICS metadata management')
    metadata_subparsers = metadata_parser.add_subparsers(dest='metadata_command', help='Metadata commands')
    
    # Metadata convert-csd subcommand
    convert_csd_parser = metadata_subparsers.add_parser('convert-csd',
                                                        help='Convert CSD file to CSV')
    convert_csd_parser.add_argument('--input', required=True,
                                   help='Input CSD file path')
    convert_csd_parser.add_argument('--output', required=True,
                                   help='Output CSV file path')
    convert_csd_parser.add_argument('--dry-run', action='store_true',
                                   help='Parse and validate without writing output')
    
    # Metadata scan subcommand
    scan_parser = metadata_subparsers.add_parser('scan',
                                                help='Scan directory for metadata files')
    scan_parser.add_argument('--source-dir', required=True,
                            help='Source directory to scan')
    scan_parser.add_argument('--file-types',
                            choices=['csd', 'csv', 'all'],
                            default='all',
                            help='Types of files to scan for (default: all)')
    scan_parser.add_argument('--recursive', action=argparse.BooleanOptionalAction,
                            default=True,
                            help='Enable/disable recursive directory scanning (default: enabled)')
    scan_parser.add_argument('--convert', action='store_true',
                            help='Automatically convert CSD files to CSV')
    scan_parser.add_argument('--output-dir',
                            help='Output directory for converted files (default: <source-dir>/exports)')
    
    # Migration command (NEW)
    migration_parser = subparsers.add_parser('migration',
                                            help='Migration flow analysis and export')
    migration_subparsers = migration_parser.add_subparsers(dest='migration_command', help='Migration commands')
    
    # Migration build-flows subcommand
    build_flows_parser = migration_subparsers.add_parser('build-flows',
                                                         help='Build migration flows from analysis')
    build_flows_parser.add_argument('--db', required=True,
                                   help='Path to database file')
    build_flows_parser.add_argument('--external-config',
                                   help='Path to external configuration YAML file')
    build_flows_parser.add_argument('--utility-threshold', type=int, default=5,
                                   help='Minimum number of flows to mark as utility (default: 5)')
    
    # Migration export-flows subcommand
    export_flows_parser = migration_subparsers.add_parser('export-flows',
                                                          help='Export migration flows to JSON')
    export_flows_parser.add_argument('--db', required=True,
                                    help='Path to database file')
    export_flows_parser.add_argument('--output', required=True,
                                    help='Output JSON file path')
    export_flows_parser.add_argument('--flows',
                                    help='Comma-separated list of flow IDs to export (optional, default: all)')
    export_flows_parser.add_argument('--min-complexity',
                                    choices=['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'],
                                    help='Minimum complexity tier to include (optional)')
    export_flows_parser.add_argument('--business-domain',
                                    help='Filter by business domain (optional)')
    export_flows_parser.add_argument('--sort',
                                    choices=['complexity-asc', 'complexity-desc', 'independence', 'dependencies', 'name'],
                                    help='Sort flows by migration strategy (default: database order)')
    export_flows_parser.add_argument('--extended-scope', action='store_true',
                                    help='Include utility metadata in scope output')
    
    # Migration export-jobs subcommand
    export_jobs_parser = migration_subparsers.add_parser('export-jobs',
                                                         help='Export JCL jobs to JSON')
    export_jobs_parser.add_argument('--db',
                                   default='analyzer.db',
                                   help='Path to database file (default: analyzer.db)')
    export_jobs_parser.add_argument('--output-dir',
                                   default='results/jobs',
                                   help='Output directory for job exports (default: results/jobs)')
    export_jobs_parser.add_argument('--sort-by',
                                   choices=['name', 'type', 'dependencies', 'complexity'],
                                   default='name',
                                   help='Sorting strategy for jobs (default: name)')
    
    # Report command (NEW)
    report_parser = subparsers.add_parser('report',
                                         help='Generate analysis reports')
    report_subparsers = report_parser.add_subparsers(dest='report_type',
                                                     help='Report type')
    
    # Summary report command
    summary_parser = report_subparsers.add_parser('summary',
                                                  help='Generate analysis summary report')
    summary_parser.add_argument('--db', required=True,
                               help='Path to database file')
    summary_parser.add_argument('--output',
                               help='Output file path (default: reports/analysis_summary.md)')
    
    # Status report command
    status_parser = report_subparsers.add_parser('status',
                                                 help='Generate source analysis status report')
    status_parser.add_argument('--db', required=True,
                              help='Path to database file')
    status_parser.add_argument('--output-dir', required=True,
                              help='Base output directory (where flows/, jobs/, reports/ exist)')
    status_parser.add_argument('--output',
                              help='Output file path (default: progress/source_analysis_status.json)')
    status_parser.add_argument('--project-name',
                              help='Project name (defaults to database filename)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate handler
    if args.command == 'analyze':
        return _handle_analyze(args)
    elif args.command == 'inventory':
        return _handle_inventory(args)
    elif args.command == 'dependencies':
        return _handle_dependencies(args)
    elif args.command == 'artifacts':
        return _handle_artifacts(args)
    elif args.command == 'program-level':
        return _handle_program_level(args)
    elif args.command == 'copybook-analysis':
        return _handle_copybook_analysis(args)
    elif args.command == 'status':
        return _handle_status(args)
    elif args.command == 'load':
        return _handle_load(args)
    elif args.command == 'service':
        return _handle_service(args)
    elif args.command == 'flow':
        return _handle_flow(args)
    elif args.command == 'metadata':
        return _handle_metadata(args)
    elif args.command == 'migration':
        return _handle_migration(args)
    elif args.command == 'report':
        return _handle_report(args)
    
    return 0


def _handle_analyze(args):
    """Handle complete analysis workflow."""
    try:
        # Validate source directory
        if not Path(args.source_dir).exists():
            print(f"Error: Directory not found: {args.source_dir}")
            return 1
        
        if not Path(args.source_dir).is_dir():
            print(f"Error: Path is not a directory: {args.source_dir}")
            return 1
        
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(db, args.log_file)
        
        # Run complete analysis
        results = orchestrator.run_complete_analysis(
            source_directory=args.source_dir,
            calculate_complexity=args.complexity,
            enable_program_level=not args.no_program_level,
            enable_copybook_analysis=not args.no_copybook_analysis
        )
        
        # Print final summary
        _print_analysis_summary(results)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_inventory(args):
    """Handle inventory discovery only."""
    try:
        # Validate source directory
        if not Path(args.source_dir).exists():
            print(f"Error: Directory not found: {args.source_dir}")
            return 1
        
        if not Path(args.source_dir).is_dir():
            print(f"Error: Path is not a directory: {args.source_dir}")
            return 1
        
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(db, args.log_file)
        
        # Run inventory only
        results = orchestrator.run_inventory_only(args.source_dir)
        
        # Print inventory summary
        _print_inventory_summary(results)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_dependencies(args):
    """Handle dependency analysis only."""
    try:
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(db, args.log_file)
        
        # Check if inventory exists
        if not _check_inventory_exists(db):
            print("Error: No inventory found in database. Run 'inventory' command first.")
            return 1
        
        # Load existing inventory
        _load_existing_inventory(orchestrator, db)
        
        # Run dependency analysis only
        results = orchestrator.run_dependency_analysis_only(
            calculate_complexity=args.complexity,
            enable_program_level=not args.no_program_level,
            enable_copybook_analysis=not args.no_copybook_analysis
        )
        
        # Print dependency summary
        _print_dependency_summary(results)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_artifacts(args):
    """Handle specialized artifact parsing only."""
    try:
        # Validate source directory
        if not Path(args.source_dir).exists():
            print(f"Error: Directory not found: {args.source_dir}")
            return 1
        
        if not Path(args.source_dir).is_dir():
            print(f"Error: Path is not a directory: {args.source_dir}")
            return 1
        
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(db, args.log_file)
        
        # Run specialized artifact parsing
        results = orchestrator.run_artifacts_only(args.source_dir, args.type)
        
        # Print artifact summary
        _print_artifacts_summary(results)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_program_level(args):
    """Handle program-level dependency analysis."""
    try:
        # Validate source directory
        if not Path(args.source_dir).exists():
            print(f"Error: Directory not found: {args.source_dir}")
            return 1
        
        if not Path(args.source_dir).is_dir():
            print(f"Error: Path is not a directory: {args.source_dir}")
            return 1
        
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(db, args.log_file)
        
        # Run complete analysis with program-level enabled, others disabled
        results = orchestrator.run_complete_analysis(
            source_directory=args.source_dir,
            calculate_complexity=False,
            enable_program_level=True,
            enable_copybook_analysis=False
        )
        
        # Print program-level summary
        _print_program_level_summary(results)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_copybook_analysis(args):
    """Handle copybook analysis."""
    try:
        # Validate source directory
        if not Path(args.source_dir).exists():
            print(f"Error: Directory not found: {args.source_dir}")
            return 1
        
        if not Path(args.source_dir).is_dir():
            print(f"Error: Path is not a directory: {args.source_dir}")
            return 1
        
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(db, args.log_file)
        
        # Run complete analysis with copybook analysis enabled, others disabled
        results = orchestrator.run_complete_analysis(
            source_directory=args.source_dir,
            calculate_complexity=False,
            enable_program_level=False,
            enable_copybook_analysis=True
        )
        
        # Print copybook analysis summary
        _print_copybook_analysis_summary(results)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_status(args):
    """Handle status check."""
    try:
        # Initialize database
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Check what exists in database
        status = _check_database_status(db)
        
        print("\n" + "="*60)
        print("DATABASE STATUS")
        print("="*60)
        print(f"Database: {args.db}")
        print(f"Inventory exists: {'Yes' if status['inventory_exists'] else 'No'}")
        print(f"Dependencies exist: {'Yes' if status['dependencies_exist'] else 'No'}")
        
        if status['inventory_exists']:
            print(f"Artifacts in inventory: {status['artifact_count']:,}")
        
        if status['dependencies_exist']:
            print(f"Dependencies stored: {status['dependency_count']:,}")
        
        # Check specialized tables
        specialized_status = _check_specialized_tables_status(db)
        print(f"CICS resources: {specialized_status['cics_count']:,}")
        print(f"JCL jobs: {specialized_status['jcl_count']:,}")
        print(f"Programs: {specialized_status['programs_count']:,}")
        print(f"Copybooks: {specialized_status['copybooks_count']:,}")
        print(f"Datasets: {specialized_status['datasets_count']:,}")
        print(f"Program boundaries: {specialized_status['program_boundaries_count']:,}")
        print(f"Copybook analysis: {specialized_status['copybook_analysis_count']:,}")
        
        print("="*60)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1


def _handle_load(args):
    """Handle inventory load command."""
    try:
        # Validate CSV file exists
        csv_path = Path(args.file)
        if not csv_path.exists():
            print(f"Error: File not found: {args.file}")
            return 1
        
        if not csv_path.is_file():
            print(f"Error: Path is not a file: {args.file}")
            return 1
        
        # Initialize database
        print(f"Connecting to database: {args.db}")
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Import inventory loader
        from .inventory.inventory_loader import InventoryLoader
        
        # Create inventory loader
        loader = InventoryLoader(db)
        
        # Create schema if needed
        loader.create_inventory_schema()
        
        # Load inventory based on type
        print(f"\nLoading {args.type} inventory from {args.file}...")
        loader.load_inventory(args.file, args.type)
        
        # Print success message
        print(f"\n✓ Successfully loaded {args.type} inventory")
        
        # Print statistics
        if loader.stats:
            print("\nStatistics:")
            for key, value in loader.stats.items():
                print(f"  {key}: {value:,}")
        
        # Close database
        db.close()
        
        return 0
        
    except ValueError as e:
        # Validation errors
        print(f"\nValidation Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_service(args):
    """Handle service grouping analysis command."""
    try:
        # Check if subcommand is provided
        if not hasattr(args, 'service_command') or not args.service_command:
            print("Error: No service subcommand specified. Use 'service candidates' or 'service --help'")
            return 1
        
        if args.service_command == 'candidates':
            return _handle_service_candidates(args)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_service_candidates(args):
    """Handle service candidates identification."""
    import json
    
    try:
        # Validate database exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        # Initialize database
        db = SQLiteAdapter(args.db)
        db.connect()
        
        # Import service grouping analyzer
        from .analysis.service_grouping import ServiceGroupingAnalyzer
        
        # Create analyzer
        analyzer = ServiceGroupingAnalyzer(db.conn)
        
        # Run all analysis strategies
        print("Analyzing service candidates...")
        
        cics_candidates = analyzer.analyze_by_cics_group()
        data_candidates = analyzer.analyze_by_data_ownership()
        program_candidates = analyzer.analyze_by_shared_programs()
        
        # Combine all candidates
        all_candidates = cics_candidates + data_candidates + program_candidates
        
        # Filter by confidence if specified
        if args.min_confidence:
            confidence_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            min_level = confidence_order[args.min_confidence]
            all_candidates = [
                c for c in all_candidates 
                if confidence_order.get(c.confidence, 0) >= min_level
            ]
        
        # Check if any candidates found
        if not all_candidates:
            print("\nNo service candidates found.")
            if args.min_confidence:
                print(f"(with minimum confidence: {args.min_confidence})")
            db.close()
            return 0
        
        # Generate output based on format
        if args.format == 'json':
            output_data = _format_service_candidates_json(all_candidates)
            
            if args.output:
                # Write to file
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"\n✓ Service candidates written to {args.output}")
            else:
                # Print to stdout
                print(json.dumps(output_data, indent=2))
        else:
            # Markdown format
            output_markdown = _format_service_candidates_markdown(all_candidates)
            
            if args.output:
                # Write to file
                with open(args.output, 'w') as f:
                    f.write(output_markdown)
                print(f"\n✓ Service candidates written to {args.output}")
            else:
                # Print to stdout
                print(output_markdown)
        
        # Close database
        db.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _format_service_candidates_json(candidates: list) -> dict:
    """Format service candidates as JSON."""
    # Calculate summary statistics
    summary = {
        'total_candidates': len(candidates),
        'by_grouping_strategy': {},
        'by_confidence_level': {}
    }
    
    # Count by grouping strategy
    for candidate in candidates:
        strategy = candidate.grouping_reason
        summary['by_grouping_strategy'][strategy] = summary['by_grouping_strategy'].get(strategy, 0) + 1
    
    # Count by confidence level
    for candidate in candidates:
        confidence = candidate.confidence
        summary['by_confidence_level'][confidence] = summary['by_confidence_level'].get(confidence, 0) + 1
    
    # Format candidates
    formatted_candidates = []
    for candidate in candidates:
        formatted_candidate = {
            'name': candidate.name,
            'grouping_reason': candidate.grouping_reason,
            'confidence': candidate.confidence,
            'recommendation': candidate.recommendation,
            'consolidation_score': candidate.total_complexity,
            'entry_points': [
                {
                    'program_name': ep.program_name,
                    'entry_type': ep.entry_type,
                    'confidence': ep.confidence,
                    'source': ep.source,
                    'transaction_id': ep.transaction_id,
                    'description': ep.description,
                    'status': ep.status
                }
                for ep in candidate.entry_points
            ],
            'shared_data': candidate.shared_data,
            'shared_programs': candidate.shared_programs,
            'cics_group': candidate.cics_group
        }
        formatted_candidates.append(formatted_candidate)
    
    return {
        'service_candidates': formatted_candidates,
        'summary': summary
    }


def _format_service_candidates_markdown(candidates: list) -> str:
    """Format service candidates as markdown."""
    lines = []
    
    lines.append("=" * 80)
    lines.append("SERVICE GROUPING ANALYSIS")
    lines.append("=" * 80)
    lines.append("")
    
    # Group by strategy
    by_strategy = {}
    for candidate in candidates:
        strategy = candidate.grouping_reason
        if strategy not in by_strategy:
            by_strategy[strategy] = []
        by_strategy[strategy].append(candidate)
    
    # Print each strategy group
    for strategy, strategy_candidates in by_strategy.items():
        lines.append(f"\n{strategy.replace('_', ' ').title()}:")
        lines.append("-" * 80)
        
        for candidate in strategy_candidates:
            lines.append(f"\nService: {candidate.name}")
            lines.append(f"  Confidence: {candidate.confidence}")
            lines.append(f"  Recommendation: {candidate.recommendation}")
            lines.append(f"  Consolidation Score: {candidate.total_complexity}")
            
            if candidate.cics_group:
                lines.append(f"  CICS Group: {candidate.cics_group}")
            
            lines.append(f"  Entry Points ({len(candidate.entry_points)}):")
            for ep in candidate.entry_points[:5]:  # Show first 5
                trans_info = f" (Transaction: {ep.transaction_id})" if ep.transaction_id else ""
                lines.append(f"    - {ep.program_name}{trans_info}")
            if len(candidate.entry_points) > 5:
                lines.append(f"    ... and {len(candidate.entry_points) - 5} more")
            
            if candidate.shared_data:
                lines.append(f"  Shared Data ({len(candidate.shared_data)}):")
                for data in candidate.shared_data[:3]:  # Show first 3
                    lines.append(f"    - {data}")
                if len(candidate.shared_data) > 3:
                    lines.append(f"    ... and {len(candidate.shared_data) - 3} more")
            
            if candidate.shared_programs:
                lines.append(f"  Shared Programs ({len(candidate.shared_programs)}):")
                for prog in candidate.shared_programs[:3]:  # Show first 3
                    lines.append(f"    - {prog}")
                if len(candidate.shared_programs) > 3:
                    lines.append(f"    ... and {len(candidate.shared_programs) - 3} more")
    
    # Summary statistics
    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY STATISTICS")
    lines.append("=" * 80)
    lines.append(f"Total Service Candidates: {len(candidates)}")
    
    # By grouping strategy
    lines.append("\nBy Grouping Strategy:")
    for strategy, strategy_candidates in by_strategy.items():
        lines.append(f"  {strategy.replace('_', ' ').title()}: {len(strategy_candidates)}")
    
    # By confidence level
    by_confidence = {}
    for candidate in candidates:
        confidence = candidate.confidence
        by_confidence[confidence] = by_confidence.get(confidence, 0) + 1
    
    lines.append("\nBy Confidence Level:")
    for confidence in ['HIGH', 'MEDIUM', 'LOW']:
        if confidence in by_confidence:
            lines.append(f"  {confidence}: {by_confidence[confidence]}")
    
    lines.append("=" * 80)
    
    return '\n'.join(lines)


def _check_inventory_exists(db) -> bool:
    """Check if inventory table exists and has data."""
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]
        return count > 0
    except:
        return False


def _load_existing_inventory(orchestrator, db):
    """Load existing inventory into orchestrator."""
    # This would need to be implemented to reload inventory from database
    # For now, we'll raise an error suggesting to run complete analysis
    raise NotImplementedError(
        "Loading existing inventory not yet implemented. "
        "Please run complete 'analyze' command instead."
    )


def _check_database_status(db) -> dict:
    """Check database status."""
    status = {
        'inventory_exists': False,
        'dependencies_exist': False,
        'artifact_count': 0,
        'dependency_count': 0
    }
    
    try:
        cursor = db.conn.cursor()
        
        # Check inventory
        cursor.execute("SELECT COUNT(*) FROM inventory")
        status['artifact_count'] = cursor.fetchone()[0]
        status['inventory_exists'] = status['artifact_count'] > 0
        
    except:
        pass
    
    try:
        cursor = db.conn.cursor()
        
        # Check dependencies
        cursor.execute("SELECT COUNT(*) FROM artifact_dependencies")
        status['dependency_count'] = cursor.fetchone()[0]
        status['dependencies_exist'] = status['dependency_count'] > 0
        
    except:
        pass
    
    return status


def _print_analysis_summary(results):
    """Print complete analysis summary."""
    summary = results['summary']
    
    print("\n" + "="*80)
    print("COMPLETE ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total artifacts discovered:     {summary['total_artifacts']:,}")
    print(f"Artifacts with dependencies:    {summary['artifacts_with_dependencies']:,}")
    print(f"Total dependencies found:       {summary['total_dependencies']:,}")
    print(f"Dependencies stored:            {summary['dependencies_stored']:,}")
    print(f"Missing artifacts detected:     {summary['missing_artifacts']:,}")
    print(f"Inventory completeness:         {summary['completeness_score']:.1%}")
    print("="*80)
    
    # Print language breakdown if available
    inventory_stats = results.get('inventory_stats', {})
    languages = [k for k in inventory_stats.keys() if k.upper() in ['COBOL', 'PLI', 'JCL', 'REXX', 'NATURAL', 'RPG', 'ASM']]
    
    if languages:
        print("\nLanguage Breakdown:")
        for lang in sorted(languages):
            count = inventory_stats.get(lang, 0)
            if count > 0:
                print(f"  {lang}: {count:,} artifacts")


def _print_inventory_summary(results):
    """Print inventory summary."""
    print("\n" + "="*60)
    print("INVENTORY SUMMARY")
    print("="*60)
    print(f"Artifacts discovered: {results['artifacts_discovered']:,}")
    print(f"Inventory complete:   {'Yes' if results['inventory_complete'] else 'No'}")
    print("="*60)


def _print_dependency_summary(results):
    """Print dependency analysis summary."""
    validation_result = results.get('validation_result')
    
    print("\n" + "="*60)
    print("DEPENDENCY ANALYSIS SUMMARY")
    print("="*60)
    print(f"Analysis results:     {results['analysis_results']:,}")
    print(f"Dependencies analyzed: {'Yes' if results['dependencies_analyzed'] else 'No'}")
    print(f"Dependencies validated: {'Yes' if results['dependencies_validated'] else 'No'}")
    
    if validation_result:
        print(f"Validated dependencies: {len(validation_result.validated_dependencies):,}")
        print(f"Missing artifacts:      {len(validation_result.missing_artifacts):,}")
        print(f"Completeness score:     {validation_result.completeness_score:.1%}")
    
    print("="*60)


def _print_artifacts_summary(results):
    """Print specialized artifacts summary."""
    print("\n" + "="*60)
    print("SPECIALIZED ARTIFACTS SUMMARY")
    print("="*60)
    print(f"CICS resources parsed:  {results.get('cics_resources', 0):,}")
    print(f"JCL jobs parsed:        {results.get('jcl_jobs', 0):,}")
    print(f"Programs populated:     {results.get('programs', 0):,}")
    print(f"Copybooks populated:    {results.get('copybooks', 0):,}")
    print("="*60)


def _print_program_level_summary(results):
    """Print program-level analysis summary."""
    print("\n" + "="*60)
    print("PROGRAM-LEVEL ANALYSIS SUMMARY")
    print("="*60)
    
    summary = results.get('summary', {})
    print(f"Total artifacts: {summary.get('total_artifacts', 0):,}")
    print(f"Program boundaries detected: {summary.get('program_boundaries_detected', 0):,}")
    print(f"Dependencies stored: {summary.get('dependencies_stored', 0):,}")
    print("="*60)


def _print_copybook_analysis_summary(results):
    """Print copybook analysis summary."""
    print("\n" + "="*60)
    print("COPYBOOK ANALYSIS SUMMARY")
    print("="*60)
    
    summary = results.get('summary', {})
    print(f"Total artifacts: {summary.get('total_artifacts', 0):,}")
    print(f"Copybooks analyzed: {summary.get('copybooks_analyzed', 0):,}")
    print(f"Dependencies stored: {summary.get('dependencies_stored', 0):,}")
    print("="*60)


def _print_analysis_summary(results):
    """Print complete analysis summary with file-level and program-level counts."""
    print("\n" + "="*80)
    print("COMPLETE ANALYSIS SUMMARY")
    print("="*80)
    
    summary = results.get('summary', {})
    inventory_stats = results.get('inventory_stats', {})
    
    # File-level statistics (new architecture)
    print("FILE-LEVEL STATISTICS:")
    print(f"  Total files discovered:         {summary.get('total_artifacts', 0):,}")
    print(f"  Files with dependencies:        {summary.get('artifacts_with_dependencies', 0):,}")
    print(f"  Multi-program files:            {inventory_stats.get('multi_program_files', 0):,}")
    print(f"  Single-program files:           {inventory_stats.get('single_program_files', 0):,}")
    print(f"  Mixed content files:            {inventory_stats.get('mixed_content_files', 0):,}")
    
    # Program-level statistics (if program-level analysis enabled)
    if 'program_boundaries_detected' in summary:
        print("\nPROGRAM-LEVEL STATISTICS:")
        print(f"  Program boundaries detected:    {summary['program_boundaries_detected']:,}")
        print(f"  Program-level dependencies:     {summary.get('program_dependencies_stored', 0):,}")
    
    # Dependency statistics
    print("\nDEPENDENCY STATISTICS:")
    print(f"  Total dependencies found:       {summary.get('total_dependencies', 0):,}")
    print(f"  Dependencies stored:            {summary.get('dependencies_stored', 0):,}")
    print(f"  Missing artifacts detected:     {summary.get('missing_artifacts', 0):,}")
    print(f"  Inventory completeness:         {summary.get('completeness_score', 0.0):.1%}")
    
    # Advanced analysis statistics
    if 'copybooks_analyzed' in summary:
        print("\nADVANCED ANALYSIS:")
        print(f"  Copybooks analyzed:             {summary['copybooks_analyzed']:,}")
    
    # Language breakdown
    languages = [k for k in inventory_stats.keys() if k.upper() in ['COBOL', 'PLI', 'JCL', 'REXX', 'NATURAL', 'RPG', 'ASM']]
    if languages:
        print("\nLANGUAGE BREAKDOWN:")
        for lang in sorted(languages):
            count = inventory_stats.get(lang, 0)
            if count > 0:
                print(f"  {lang}: {count:,} files")
    
    print("="*80)


def _print_inventory_summary(results):
    """Print inventory summary."""
    print("\n" + "="*60)
    print("INVENTORY SUMMARY")
    print("="*60)
    
    print(f"Inventory complete: {'Yes' if results.get('inventory_complete', False) else 'No'}")
    print(f"Artifacts discovered: {results.get('artifacts_discovered', 0):,}")
    
    inventory_stats = results.get('inventory_stats', {})
    if inventory_stats:
        print(f"Files scanned: {inventory_stats.get('files_scanned', 0):,}")
        print(f"Languages detected: {inventory_stats.get('languages_detected', 0):,}")
    
    print("="*60)


def _print_dependency_summary(results):
    """Print dependency analysis summary."""
    print("\n" + "="*60)
    print("DEPENDENCY ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"Dependencies analyzed: {'Yes' if results.get('dependencies_analyzed', False) else 'No'}")
    print(f"Dependencies validated: {'Yes' if results.get('dependencies_validated', False) else 'No'}")
    print(f"Analysis results: {results.get('analysis_results', 0):,}")
    
    analysis_stats = results.get('analysis_stats', {})
    if analysis_stats:
        print(f"Files analyzed: {analysis_stats.get('files_analyzed', 0):,}")
        print(f"Analysis errors: {analysis_stats.get('analysis_errors', 0):,}")
    
    print("="*60)


def _check_specialized_tables_status(db) -> dict:
    """Check specialized tables status."""
    status = {
        'cics_count': 0,
        'jcl_count': 0,
        'programs_count': 0,
        'copybooks_count': 0,
        'datasets_count': 0,
        'program_boundaries_count': 0,
        'copybook_analysis_count': 0
    }
    
    try:
        cursor = db.conn.cursor()
        
        # Check each specialized table
        for table, key in [
            ('inventory_cics', 'cics_count'),
            ('inventory_jcl', 'jcl_count'),
            ('inventory_programs', 'programs_count'),
            ('inventory_copybooks', 'copybooks_count'),
            ('inventory_datasets', 'datasets_count'),
            ('program_file_mapping', 'program_boundaries_count'),
            ('copybook_analysis', 'copybook_analysis_count')
        ]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                status[key] = cursor.fetchone()[0]
            except:
                status[key] = 0
        
    except:
        pass
    
    return status


def _handle_flow(args):
    """Handle flow analysis command."""
    try:
        # Check if subcommand is provided
        if not hasattr(args, 'flow_command') or not args.flow_command:
            print("Error: No flow subcommand specified. Use 'flow entry-points', 'flow analyze', 'flow graph', 'flow circular', or 'flow --help'")
            return 1
        
        if args.flow_command == 'entry-points':
            return _handle_flow_entry_points(args)
        elif args.flow_command == 'analyze':
            return _handle_flow_analyze(args)
        elif args.flow_command == 'graph':
            return _handle_flow_graph(args)
        elif args.flow_command == 'circular':
            return _handle_flow_circular(args)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_flow_entry_points(args):
    """Handle flow entry-points command."""
    import json
    import os
    
    try:
        # Validate database exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        # Import API
        from .api import LegacyAnalyzerAPI
        
        # Create API instance with database path
        api = LegacyAnalyzerAPI(args.db)
        
        # Detect entry points
        print("Detecting entry points...")
        
        if args.use_metadata:
            # Use metadata-enhanced detection
            entry_points = api.get_entry_points_with_metadata(
                include_disabled=args.include_disabled,
                include_inferred=True
            )
        else:
            # Use code analysis only
            entry_point_names = api.get_entry_points()
            # Convert to EntryPoint objects for consistent formatting
            from .models.flow import EntryPoint
            entry_points = [
                EntryPoint(
                    program_name=name,
                    entry_type='INFERRED',
                    confidence='INFERRED',
                    source='CODE_ANALYSIS',
                    description='Program not called by any other program'
                )
                for name in entry_point_names
            ]
        
        # Check if any entry points found
        if not entry_points:
            print("\nNo entry points found.")
            api.close()
            return 0
        
        # Generate output based on format
        if args.format == 'json':
            output_data = _format_entry_points_json(entry_points)
            
            if args.output:
                # Create entry_points directory if needed
                output_path = args.output
                if not os.path.dirname(output_path):
                    # No directory specified, use default entry_points folder
                    output_dir = 'entry_points'
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, 'entry_points.json')
                else:
                    # Ensure parent directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Write to file
                with open(output_path, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"\n✓ Entry points written to {output_path}")
            else:
                # Print to stdout
                print(json.dumps(output_data, indent=2))
        
        else:
            # Markdown format
            output_markdown = _format_entry_points_markdown(entry_points)
            
            if args.output:
                # Create entry_points directory if needed
                output_path = args.output
                if not os.path.dirname(output_path):
                    # No directory specified, use default entry_points folder
                    output_dir = 'entry_points'
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, 'entry_points.md')
                else:
                    # Ensure parent directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Write to file
                with open(output_path, 'w') as f:
                    f.write(output_markdown)
                print(f"\n✓ Entry points written to {output_path}")
            else:
                # Print to stdout
                print(output_markdown)
        
        # Close API
        api.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _format_entry_points_json(entry_points: list) -> dict:
    """Format entry points as JSON."""
    # Calculate summary statistics
    summary = {
        'total_entry_points': len(entry_points),
        'by_entry_type': {},
        'by_confidence': {}
    }
    
    # Count by entry type
    for ep in entry_points:
        entry_type = ep.entry_type
        summary['by_entry_type'][entry_type] = summary['by_entry_type'].get(entry_type, 0) + 1
    
    # Count by confidence
    for ep in entry_points:
        confidence = ep.confidence
        summary['by_confidence'][confidence] = summary['by_confidence'].get(confidence, 0) + 1
    
    # Format entry points
    formatted_entry_points = []
    for ep in entry_points:
        formatted_ep = {
            'program_name': ep.program_name,
            'entry_type': ep.entry_type,
            'confidence': ep.confidence,
            'source': ep.source,
            'description': ep.description
        }
        
        # Add optional fields if present
        if ep.transaction_id:
            formatted_ep['transaction_id'] = ep.transaction_id
        if ep.jcl_name:
            formatted_ep['jcl_name'] = ep.jcl_name
        if ep.status:
            formatted_ep['status'] = ep.status
        
        formatted_entry_points.append(formatted_ep)
    
    return {
        'entry_points': formatted_entry_points,
        'summary': summary
    }




def _format_entry_points_markdown(entry_points: list) -> str:
    """Format entry points as markdown."""
    lines = []
    
    lines.append("=" * 80)
    lines.append("ENTRY POINT DETECTION")
    lines.append("=" * 80)
    lines.append("")
    
    # Group by entry type
    by_type = {}
    for ep in entry_points:
        entry_type = ep.entry_type
        if entry_type not in by_type:
            by_type[entry_type] = []
        by_type[entry_type].append(ep)
    
    # Print each type group
    for entry_type in sorted(by_type.keys()):
        type_entry_points = by_type[entry_type]
        lines.append(f"\n{entry_type} Entry Points ({len(type_entry_points)}):")
        lines.append("-" * 80)
        
        for ep in sorted(type_entry_points, key=lambda x: x.program_name):
            lines.append(f"\n  Program: {ep.program_name}")
            lines.append(f"    Confidence: {ep.confidence}")
            lines.append(f"    Source: {ep.source}")
            
            if ep.transaction_id:
                lines.append(f"    Transaction: {ep.transaction_id}")
            if ep.jcl_name:
                lines.append(f"    JCL: {ep.jcl_name}")
            if ep.status:
                lines.append(f"    Status: {ep.status}")
            if ep.description:
                lines.append(f"    Description: {ep.description}")
    
    # Summary statistics
    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY STATISTICS")
    lines.append("=" * 80)
    lines.append(f"Total Entry Points: {len(entry_points)}")
    
    # By entry type
    lines.append("\nBy Entry Type:")
    for entry_type in sorted(by_type.keys()):
        lines.append(f"  {entry_type}: {len(by_type[entry_type])}")
    
    # By confidence
    by_confidence = {}
    for ep in entry_points:
        confidence = ep.confidence
        by_confidence[confidence] = by_confidence.get(confidence, 0) + 1
    
    lines.append("\nBy Confidence Level:")
    for confidence in sorted(by_confidence.keys()):
        lines.append(f"  {confidence}: {by_confidence[confidence]}")
    
    lines.append("=" * 80)
    
    return '\n'.join(lines)


def _handle_flow_analyze(args):
    """Handle flow analyze command."""
    print(f"Flow analysis for program '{args.program}' is not yet implemented.")
    print("This feature will analyze the call hierarchy starting from the specified program.")
    return 1


def _handle_flow_graph(args):
    """Handle flow graph command."""
    print("Flow graph generation is not yet implemented.")
    print("This feature will generate a visual graph of program dependencies.")
    return 1


def _handle_flow_circular(args):
    """Handle flow circular command."""
    print("Circular dependency detection is not yet implemented.")
    print("This feature will detect and report circular dependencies in the codebase.")
    return 1


def _handle_metadata(args):
    """Handle metadata management command."""
    try:
        # Check if subcommand is provided
        if not hasattr(args, 'metadata_command') or not args.metadata_command:
            print("Error: No metadata subcommand specified. Use 'metadata convert-csd', 'metadata scan', or 'metadata --help'")
            return 1
        
        if args.metadata_command == 'convert-csd':
            return _handle_metadata_convert_csd(args)
        elif args.metadata_command == 'scan':
            return _handle_metadata_scan(args)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_metadata_convert_csd(args):
    """Handle metadata convert-csd command."""
    try:
        # Validate input file exists
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}")
            return 1
        
        if not input_path.is_file():
            print(f"Error: Input path is not a file: {args.input}")
            return 1
        
        # Import CSD parser
        from .parsers.csd_parser import CSDParser
        
        # Create parser
        parser = CSDParser()
        
        # Parse CSD file
        print(f"Parsing CSD file: {args.input}")
        
        try:
            csd_data = parser.parse_file(args.input)
        except Exception as e:
            print(f"Error: Failed to parse CSD file: {e}")
            return 1
        
        # Display summary statistics
        print("\nParsing Summary:")
        print(f"  Transactions: {len(csd_data.transactions)}")
        print(f"  Programs:     {len(csd_data.programs)}")
        print(f"  Files:        {len(csd_data.files)}")
        print(f"  Mapsets:      {len(csd_data.mapsets)}")
        print(f"  Total:        {len(csd_data.get_all_resources())}")
        
        # Check if any resources were found
        if len(csd_data.get_all_resources()) == 0:
            print("\nWarning: No CICS resources found in CSD file.")
            print("The file may be empty or in an invalid format.")
        
        # Handle dry-run mode
        if args.dry_run:
            print("\nDry run mode - no file written.")
            print(f"Would have written to: {args.output}")
            return 0
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to CSV
        print(f"\nWriting CSV to: {args.output}")
        parser.to_csv(csd_data, args.output)
        
        print(f"\n✓ Conversion completed successfully")
        print(f"  Output file: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_metadata_scan(args):
    """Handle metadata scan command."""
    try:
        # Validate source directory exists
        source_dir = Path(args.source_dir)
        if not source_dir.exists():
            print(f"Error: Directory not found: {args.source_dir}")
            return 1
        
        if not source_dir.is_dir():
            print(f"Error: Path is not a directory: {args.source_dir}")
            return 1
        
        # Import metadata scanner
        from .metadata.scanner import MetadataFileScanner
        
        # Create scanner
        scanner = MetadataFileScanner()
        
        # Determine file types to scan
        file_types = {args.file_types} if args.file_types != 'all' else {'csd', 'csv'}
        
        # Scan directory
        print(f"Scanning directory: {args.source_dir}")
        print(f"  File types: {', '.join(file_types)}")
        print(f"  Recursive: {args.recursive}")
        
        metadata_files = scanner.scan_directory(
            str(source_dir),
            recursive=args.recursive,
            file_types=file_types
        )
        
        # Display scan results
        print("\nScan Results:")
        print(f"  CSD files:  {len(metadata_files.csd_files)}")
        print(f"  CSV files:  {len(metadata_files.csv_files)}")
        print(f"  Total:      {metadata_files.get_file_count()}")
        
        # List found files
        if metadata_files.csd_files:
            print("\nCSD Files:")
            for csd_file in metadata_files.csd_files:
                rel_path = Path(csd_file).relative_to(source_dir) if Path(csd_file).is_relative_to(source_dir) else Path(csd_file)
                print(f"  - {rel_path}")
        
        if metadata_files.csv_files:
            print("\nCSV Files:")
            for csv_file in metadata_files.csv_files:
                rel_path = Path(csv_file).relative_to(source_dir) if Path(csv_file).is_relative_to(source_dir) else Path(csv_file)
                print(f"  - {rel_path}")
        
        # Handle conversion if requested
        if args.convert and metadata_files.csd_files:
            print("\nConverting CSD files to CSV...")
            
            # Determine output directory
            if args.output_dir:
                output_dir = Path(args.output_dir)
            else:
                output_dir = source_dir / 'exports'
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Import CSD parser
            from .parsers.csd_parser import CSDParser
            parser = CSDParser()
            
            # Convert each CSD file
            converted_count = 0
            total_files = len(metadata_files.csd_files)
            for idx, csd_file in enumerate(metadata_files.csd_files, 1):
                try:
                    # Parse CSD file
                    csd_data = parser.parse_file(csd_file)
                    
                    # Generate output filename
                    csd_filename = Path(csd_file).stem
                    output_file = output_dir / f"{csd_filename}.csv"
                    
                    # Convert to CSV
                    parser.to_csv(csd_data, str(output_file))
                    
                    print(f"  [{idx}/{total_files}] ✓ Converted: {Path(csd_file).name} -> {output_file.name}")
                    converted_count += 1
                    
                except Exception as e:
                    print(f"  [{idx}/{total_files}] ✗ Failed to convert {Path(csd_file).name}: {e}")
            
            print(f"\nConversion complete: {converted_count}/{total_files} files converted")
            print(f"Output directory: {output_dir}")
        elif args.convert and not metadata_files.csd_files:
            print("\nNo CSD files found to convert.")
        
        print("\n✓ Scan completed successfully")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_migration(args):
    """Handle migration command."""
    try:
        # Check if subcommand is provided
        if not hasattr(args, 'migration_command') or not args.migration_command:
            print("Error: No migration subcommand specified. Use 'migration build-flows', 'migration export-flows', 'migration export-jobs', or 'migration --help'")
            return 1
        
        if args.migration_command == 'build-flows':
            return _handle_migration_build_flows(args)
        elif args.migration_command == 'export-flows':
            return _handle_migration_export_flows(args)
        elif args.migration_command == 'export-jobs':
            return _handle_migration_export_jobs(args)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_migration_build_flows(args):
    """Handle migration build-flows command."""
    import time
    
    try:
        # Validate database exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        # Import API
        from .api import LegacyAnalyzerAPI
        
        # Create API instance
        print(f"Connecting to database: {args.db}")
        api = LegacyAnalyzerAPI(args.db)
        
        # Build migration flows
        print("\nBuilding migration flows...")
        start_time = time.time()
        
        flow_ids = api.build_migration_flows(
            external_config_path=args.external_config
        )
        
        elapsed_time = time.time() - start_time
        
        # Print success message
        print(f"\n✓ Successfully built {len(flow_ids)} migration flows")
        print(f"  Time elapsed: {elapsed_time:.2f} seconds")
        
        # Print sample flow IDs
        if flow_ids:
            print(f"\nSample flow IDs:")
            for flow_id in flow_ids[:5]:
                print(f"  - {flow_id}")
            if len(flow_ids) > 5:
                print(f"  ... and {len(flow_ids) - 5} more")
        
        # Close API
        api.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_migration_export_flows(args):
    """Handle migration export-flows command."""
    import time
    import json
    
    try:
        # Validate database exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        # Import API
        from .api import LegacyAnalyzerAPI
        
        # Create API instance
        print(f"Connecting to database: {args.db}")
        api = LegacyAnalyzerAPI(args.db)
        
        # Parse flow IDs if provided
        flow_ids = None
        if args.flows:
            flow_ids = [fid.strip() for fid in args.flows.split(',')]
            print(f"\nExporting {len(flow_ids)} specific flows...")
        else:
            print("\nExporting all flows...")
        
        # Show filters if any
        filters = []
        if args.min_complexity:
            filters.append(f"min complexity: {args.min_complexity}")
        if args.business_domain:
            filters.append(f"business domain: {args.business_domain}")
        if filters:
            print(f"Filters: {', '.join(filters)}")
        
        # Export flows
        start_time = time.time()
        
        result = api.export_migration_flows(
            output_file=args.output,
            flow_ids=flow_ids,
            min_complexity=args.min_complexity,
            business_domain=args.business_domain,
            extended_scope=args.extended_scope,
            sort_order=args.sort if hasattr(args, 'sort') else None
        )
        
        elapsed_time = time.time() - start_time
        
        # Print success message
        flow_count = len(result.get('flows', []))
        print(f"\n✓ Successfully exported {flow_count} flows")
        print(f"  Output file: {args.output}")
        print(f"  Time elapsed: {elapsed_time:.2f} seconds")
        
        # Print summary statistics if available
        if result.get('flows'):
            flows = result['flows']
            
            # Count by complexity
            by_complexity = {}
            for flow in flows:
                tier = flow.get('complexity', {}).get('tier', 'UNKNOWN')
                by_complexity[tier] = by_complexity.get(tier, 0) + 1
            
            # Count by entry type
            by_entry_type = {}
            for flow in flows:
                entry_type = flow.get('entryPoint', {}).get('primaryType', 'UNKNOWN')
                by_entry_type[entry_type] = by_entry_type.get(entry_type, 0) + 1
            
            print(f"\nSummary:")
            print(f"  Total flows: {len(flows)}")
            
            if by_complexity:
                print(f"  By complexity:")
                for tier, count in sorted(by_complexity.items()):
                    print(f"    {tier}: {count}")
            
            if by_entry_type:
                print(f"  By entry type:")
                for entry_type, count in sorted(by_entry_type.items()):
                    print(f"    {entry_type}: {count}")
        
        # Close API
        api.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_migration_export_jobs(args):
    """Handle migration export-jobs command."""
    import time
    import os
    
    try:
        # Validate database file exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database file not found: {args.db}")
            print("Please run analysis first or provide a valid database path.")
            return 1
        
        if not db_path.is_file():
            print(f"Error: Path is not a file: {args.db}")
            return 1
        
        # Validate sort-by parameter (already validated by argparse choices, but double-check)
        valid_sort_strategies = ['name', 'type', 'dependencies', 'complexity']
        if args.sort_by not in valid_sort_strategies:
            print(f"Error: Invalid sort-by parameter: {args.sort_by}")
            print(f"Valid values are: {', '.join(valid_sort_strategies)}")
            return 1
        
        # Check if output directory is writable (if it exists)
        output_dir = Path(args.output_dir)
        if output_dir.exists():
            if not output_dir.is_dir():
                print(f"Error: Output path exists but is not a directory: {args.output_dir}")
                return 1
            if not os.access(output_dir, os.W_OK):
                print(f"Error: Output directory is not writable: {args.output_dir}")
                return 1
        else:
            # Check if parent directory is writable
            parent_dir = output_dir.parent
            if parent_dir.exists() and not os.access(parent_dir, os.W_OK):
                print(f"Error: Cannot create output directory (parent not writable): {args.output_dir}")
                return 1
        
        # Import JobExporter
        from .migration.job_exporter import JobExporter
        from .migration.exceptions import ExportError, MissingDataError
        
        # Create JobExporter instance
        print(f"Connecting to database: {args.db}")
        try:
            exporter = JobExporter(args.db)
        except ExportError as e:
            print(f"Error: Failed to connect to database: {e}")
            return 1
        
        # Export jobs
        print(f"\nExporting jobs with sort strategy: {args.sort_by}")
        start_time = time.time()
        
        try:
            result = exporter.export_jobs(
                output_dir=args.output_dir,
                sort_by=args.sort_by
            )
        except ExportError as e:
            print(f"\nError: Export failed: {e}")
            exporter.close()
            return 1
        except MissingDataError as e:
            print(f"\nError: Missing required data: {e}")
            exporter.close()
            return 1
        except ValueError as e:
            print(f"\nError: Invalid parameter: {e}")
            exporter.close()
            return 1
        except OSError as e:
            print(f"\nError: File system error: {e}")
            exporter.close()
            return 1
        
        elapsed_time = time.time() - start_time
        
        # Print success message
        job_count = len(result.get('jobs', []))
        summary = result.get('summary', {})
        
        print(f"\n✓ Successfully exported {job_count} jobs")
        print(f"  Time elapsed: {elapsed_time:.2f} seconds")
        
        # Print summary statistics
        if summary:
            print(f"\nSummary:")
            print(f"  Total jobs: {summary.get('totalJobs', 0)}")
            print(f"  Application jobs: {summary.get('applicationJobs', 0)}")
            print(f"  Infrastructure jobs: {summary.get('infrastructureJobs', 0)}")
            print(f"  Sorted by: {summary.get('sortedBy', 'unknown')}")
        
        # Warn if no jobs found
        if job_count == 0:
            print("\nWarning: No jobs found in database.")
            print("Please ensure the database contains JCL job inventory.")
        
        # Close exporter
        exporter.close()
        
        return 0
        
    except Exception as e:
        print(f"\nError: Unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_report(args):
    """Handle report command."""
    try:
        # Check if subcommand is provided
        if not hasattr(args, 'report_type') or not args.report_type:
            print("Error: No report subcommand specified. Use 'report summary', 'report status', or 'report --help'")
            return 1
        
        if args.report_type == 'summary':
            return _handle_report_summary(args)
        elif args.report_type == 'status':
            return _handle_report_status(args)
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_report_summary(args):
    """Handle report summary command."""
    try:
        # Validate database exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        if not db_path.is_file():
            print(f"Error: Path is not a file: {args.db}")
            return 1
        
        # Import generate_summary_report function
        from .reports.summary_report import generate_summary_report
        
        # Set default output path if not provided
        output_path = args.output or 'reports/analysis_summary.md'
        
        # Create output directory
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate summary report
        print(f"Generating summary report from: {args.db}")
        print(f"Output file: {output_path}")
        
        generate_summary_report(args.db, output_path)
        
        # Print success message
        print(f"\n✓ Summary report generated: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nError: {str(e)}")
        return 1
    except Exception as e:
        print(f"\nError: Failed to generate summary report: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def _handle_report_status(args):
    """Handle report status command."""
    try:
        # Validate database exists
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        if not db_path.is_file():
            print(f"Error: Path is not a file: {args.db}")
            return 1
        
        # Validate output directory
        output_dir = Path(args.output_dir)
        if not output_dir.exists():
            print(f"Error: Output directory not found: {args.output_dir}")
            return 1
        
        # Import generate_status_report function
        from .reports.status_report import generate_status_report
        
        # Set default output path if not provided
        output_path = args.output or None  # Will default to progress/source_analysis_status.json
        
        # Generate status report
        print(f"Generating status report from: {args.db}")
        print(f"Output directory: {args.output_dir}")
        if output_path:
            print(f"Output file: {output_path}")
        else:
            print(f"Output file: {args.output_dir}/progress/source_analysis_status.json")
        
        generate_status_report(
            db_path=args.db,
            output_dir=args.output_dir,
            output_path=output_path,
            project_name=args.project_name
        )
        
        # Print success message
        final_path = output_path or f"{args.output_dir}/progress/source_analysis_status.json"
        print(f"\n✓ Status report generated: {final_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nError: {str(e)}")
        return 1
    except Exception as e:
        print(f"\nError: Failed to generate status report: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())