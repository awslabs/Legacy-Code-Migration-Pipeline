"""Command-line interface for migration workpackage planner."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .phase import ValidationError


def parse_arguments(args: Optional[list] = None) -> argparse.Namespace:
    """
    Parse and validate command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv if None)
        
    Returns:
        Parsed arguments namespace
        
    Raises:
        SystemExit: If validation fails or --help/--version is used
    """
    parser = argparse.ArgumentParser(
        prog='migration-planner',
        description='Migration Workpackage Planner - Automated migration planning from business flow analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults
  %(prog)s
  
  # Custom flows file
  %(prog)s --flows-file ./data/flows.json
  
  # With module classifications
  %(prog)s --flows-file ./data/flows.json --classifications-file ./data/classifications.json
  
  # Custom output directory and project name
  %(prog)s --output-base ./output --project-name my-project
  
  # Enable debug logging
  %(prog)s --log-level DEBUG
        """
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # Input files
    parser.add_argument(
        '--flows-file',
        type=str,
        required=True,
        help='Path to Business_Flows.json (e.g. ./results/<project>_analysis/flows/Business_Flows.json)'
    )
    
    parser.add_argument(
        '--classifications-file',
        type=str,
        default=None,
        help='Path to Module_Classifications.json (optional)'
    )
    
    # Output configuration
    parser.add_argument(
        '--output-base',
        type=str,
        default='./results/migration/',
        help='Output directory base path (default: %(default)s)'
    )
    
    parser.add_argument(
        '--project-name',
        type=str,
        default=None,
        help='Project name for metadata (default: extracted from flows file path)'
    )
    
    # Logging
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: %(default)s)'
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Convert paths to Path objects
    flows_path = Path(parsed_args.flows_file)
    output_path = Path(parsed_args.output_base)
    classifications_path = Path(parsed_args.classifications_file) if parsed_args.classifications_file else None
    
    # Validate flows file exists
    if not flows_path.exists():
        parser.error(f"Flows file does not exist: {flows_path}")
    
    # Extract project name from flows file path if not provided
    if parsed_args.project_name is None:
        # Extract from path: ./results/carddemo_analysis/flows/... -> carddemo_analysis
        parts = flows_path.parts
        if 'results' in parts:
            results_idx = parts.index('results')
            if results_idx + 1 < len(parts):
                parsed_args.project_name = parts[results_idx + 1]
            else:
                parsed_args.project_name = 'migration_project'
        else:
            parsed_args.project_name = 'migration_project'
    
    # Update with Path objects
    parsed_args.flows_file = flows_path
    parsed_args.output_base = output_path
    parsed_args.classifications_file = classifications_path
    
    return parsed_args


def main() -> int:
    """
    Entry point for the CLI.
    
    Returns:
        Exit code:
        - 0: Success
        - 1: Input validation error (missing required fields, invalid JSON)
        - 2: File system error (cannot read/write files)
        - 3: Dependency validation error (circular dependencies, missing references)
        - 4: Configuration error (invalid arguments)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Import here to avoid circular imports
        from .models import PlannerConfig
        from .planner import MigrationPlanner
        from .logging_config import setup_logging
        
        # Set up logging
        logger = setup_logging(log_level=args.log_level)
        
        # Create configuration
        config = PlannerConfig(
            flows_file=args.flows_file,
            output_base=args.output_base,
            project_name=args.project_name,
            classifications_file=args.classifications_file,
            log_level=args.log_level
        )
        
        logger.info(f"Starting migration planner: {config}")
        
        # Create and run planner
        planner = MigrationPlanner(config)
        result = planner.run()
        
        if result.success:
            logger.info(f"Planning completed successfully")
            logger.info(f"Generated {len(result.output_files)} output files")
            return 0
        else:
            # Error already logged by planner
            print(f"ERROR: {result.error_message}", file=sys.stderr)
            
            # Determine exit code based on error type
            if "File not found" in result.error_message:
                return 2
            elif "Validation error" in result.error_message:
                return 1
            elif "Dependency validation" in result.error_message:
                return 3
            else:
                return 2
        
    except FileNotFoundError as e:
        print(f"ERROR: File not found - {e}", file=sys.stderr)
        print(f"Context: Unable to locate required input file", file=sys.stderr)
        print(f"Suggestion: Verify the file path and ensure the file exists", file=sys.stderr)
        return 2
    
    except ValueError as e:
        print(f"ERROR: Validation error - {e}", file=sys.stderr)
        print(f"Context: Input data validation failed", file=sys.stderr)
        print(f"Suggestion: Check input file format and required fields", file=sys.stderr)
        return 1
    
    except ValidationError as e:
        print(f"ERROR: Dependency validation error - {e}", file=sys.stderr)
        print(f"Context: Dependency graph validation failed", file=sys.stderr)
        print(f"Suggestion: Review flow dependencies and resolve circular references", file=sys.stderr)
        return 3
    
    except PermissionError as e:
        print(f"ERROR: Permission denied - {e}", file=sys.stderr)
        print(f"Context: Unable to read or write files", file=sys.stderr)
        print(f"Suggestion: Check file permissions and directory access", file=sys.stderr)
        return 2
    
    except OSError as e:
        print(f"ERROR: File system error - {e}", file=sys.stderr)
        print(f"Context: Unable to perform file operation", file=sys.stderr)
        print(f"Suggestion: Check disk space and file system permissions", file=sys.stderr)
        return 2
    
    except KeyboardInterrupt:
        print("\nERROR: Operation cancelled by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}", file=sys.stderr)
        print(f"Context: An unexpected error occurred during execution", file=sys.stderr)
        print(f"Suggestion: Enable debug logging with --log-level DEBUG for more details", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
