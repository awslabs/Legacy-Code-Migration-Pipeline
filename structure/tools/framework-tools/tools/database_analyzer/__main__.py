#!/usr/bin/env python3
"""
Main entry point for database_analyzer tool
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())
