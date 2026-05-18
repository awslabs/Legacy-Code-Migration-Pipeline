"""
Legacy Analyzer Tool CLI Entry Point.

This allows running the legacy analyzer tool with:
python -m tools.legacy_analyzer

This provides the same functionality as:
python -m legacy_analyzer
"""

import sys

def main():
    """Main entry point for legacy analyzer tool."""
    # Import the main function from the legacy analyzer CLI
    from .cli import main as legacy_main
    return legacy_main()

if __name__ == '__main__':
    sys.exit(main())