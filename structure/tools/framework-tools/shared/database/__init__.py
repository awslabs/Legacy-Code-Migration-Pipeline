# Shared database infrastructure
"""
Common database components for the Migration Toolkit.

This module provides:
- Database adapters for different database backends
- Common database utilities and connection management
"""

# Re-export schemas for backward compatibility
from .schemas import dependencies_schema
from .schemas import inventory_schema
from .schemas import unified_schema
from .schemas import registry

# Also import the classes directly
from .schemas.dependencies_schema import *
from .schemas.inventory_schema import *
from .schemas.unified_schema import *
from .schemas.registry import *