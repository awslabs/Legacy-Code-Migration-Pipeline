#!/usr/bin/env python3
"""
Command-line interface for database_analyzer tool
"""

import argparse
import sys
from pathlib import Path
from .core.analyzer import DatabaseAnalyzer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Database Analyzer for Legacy Mainframe Database Migration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze database structures (legacy code in base path)
  database-analyzer analyze --base-path . --output-dir output/database

  # Analyze with custom legacy root path
  database-analyzer analyze --base-path . --legacy-root input/legacy/legacy_code --output-dir output/db

  # Analyze with custom file extensions
  database-analyzer analyze --base-path . --legacy-root src/mainframe \\
    --jcl-extensions .jcl,.JCL,.job --cbl-extensions .cbl,.cob --output-dir output/db

  # Analyze with PL/I include files and CTL files
  database-analyzer analyze --base-path . --legacy-root src/mainframe \\
    --pli-extensions .inc,.INC,.pli --ctl-extensions .ctl,.CTL --output-dir output/db

  # Analyze with custom copybook mappings
  database-analyzer analyze --base-path . --output-dir output/db \\
    --copybook-mappings '{"ACCTDATA":"CVACT01Y","CUSTDATA":"CVCUS01Y"}'

  # Analyze with verbose output
  database-analyzer analyze --base-path . --output-dir output/db --verbose

For more information, see: tools/database_analyzer/docs/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze database structures')
    analyze_parser.add_argument('--base-path', required=True, help='Base path to project directory')
    analyze_parser.add_argument('--legacy-root', help='Root path for legacy code (defaults to base-path)')
    analyze_parser.add_argument('--output-dir', required=True, help='Output directory for generated files')
    analyze_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    analyze_parser.add_argument('--no-system-filter', action='store_true', help='Include system files')
    analyze_parser.add_argument('--no-backup-filter', action='store_true', help='Include backup files')
    analyze_parser.add_argument('--no-duplicate-filter', action='store_true', help='Include duplicate formats')
    analyze_parser.add_argument('--jcl-extensions', help='Comma-separated list of JCL file extensions (default: .jcl,.JCL,.proc,.PROC)')
    analyze_parser.add_argument('--cbl-extensions', help='Comma-separated list of COBOL file extensions (default: .cbl,.CBL,.cob,.COB)')
    analyze_parser.add_argument('--cpy-extensions', help='Comma-separated list of copybook file extensions (default: .cpy,.CPY)')
    analyze_parser.add_argument('--ctl-extensions', help='Comma-separated list of CTL file extensions (default: .ctl,.CTL)')
    analyze_parser.add_argument('--pli-extensions', help='Comma-separated list of PL/I include file extensions (default: .inc,.INC)')
    analyze_parser.add_argument('--natural-extensions', help='Comma-separated list of Natural file extensions (default: .nsp,.NSP,.nsn,.NSN,.nsc,.NSC,.nsl,.NSL,.nsg,.NSG,.nsd,.NSD,.nsa,.NSA,.ns8,.NS8)')
    analyze_parser.add_argument('--copybook-mappings', help='JSON string of DSN-to-copybook mappings (e.g. \'{"ACCTDATA":"CVACT01Y"}\')')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'analyze':
        return run_analyze(args)
    
    return 0


def run_analyze(args):
    """Run database analysis"""
    config = {
        'verbose': args.verbose,
        'exclude_system_files': not args.no_system_filter,
        'exclude_backups': not args.no_backup_filter,
        'exclude_duplicates': not args.no_duplicate_filter,
    }
    
    # Add legacy root if specified
    if args.legacy_root:
        config['legacy_root'] = args.legacy_root
    
    # Add custom file extensions if specified
    if args.jcl_extensions:
        config['jcl_extensions'] = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                                     for ext in args.jcl_extensions.split(',')]
    if args.cbl_extensions:
        config['cbl_extensions'] = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                                     for ext in args.cbl_extensions.split(',')]
    if args.cpy_extensions:
        config['cpy_extensions'] = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                                     for ext in args.cpy_extensions.split(',')]
    if args.ctl_extensions:
        config['ctl_extensions'] = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                                     for ext in args.ctl_extensions.split(',')]
    if args.pli_extensions:
        config['pli_extensions'] = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                                     for ext in args.pli_extensions.split(',')]
    if args.natural_extensions:
        config['natural_extensions'] = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                                         for ext in args.natural_extensions.split(',')]
    if args.copybook_mappings:
        import json
        try:
            config['copybook_mappings'] = json.loads(args.copybook_mappings)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --copybook-mappings: {e}")
            return 1
    
    analyzer = DatabaseAnalyzer(args.base_path, config)
    results = analyzer.run_analysis()
    
    # Generate DDL files
    sqlite_ddl = analyzer.generate_sqlite_ddl()
    postgresql_ddl = analyzer.generate_postgresql_ddl()
    
    # Generate migration scripts
    sqlite_migration = analyzer.generate_migration_scripts('sqlite')
    postgresql_migration = analyzer.generate_migration_scripts('postgresql')
    
    # Write output files
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'sqlite_ddl.sql', 'w') as f:
        f.write(sqlite_ddl)
    
    with open(output_dir / 'postgresql_ddl.sql', 'w') as f:
        f.write(postgresql_ddl)
    
    with open(output_dir / 'sqlite_migration.sql', 'w') as f:
        f.write(sqlite_migration)
    
    with open(output_dir / 'postgresql_migration.sql', 'w') as f:
        f.write(postgresql_migration)
    
    print(f"\nAnalysis complete. Files generated in {output_dir}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
