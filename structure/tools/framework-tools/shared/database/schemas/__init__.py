# Database schemas
"""
Database schema definitions for the Migration Toolkit.

This module contains schema definitions for:
- Legacy code inventory (programs, copybooks, JCL)
- Cross-language dependencies
- Unified schemas for multi-type analysis
"""

# Import all schema modules for easy access
from .dependencies_schema import *
from .inventory_schema import *
from .unified_schema import *
from .registry import *

# Collect all exports
__all__ = []
try:
    from .dependencies_schema import __all__ as deps_all
    __all__.extend(deps_all)
except (ImportError, AttributeError):
    pass

try:
    from .inventory_schema import __all__ as inv_all
    __all__.extend(inv_all)
except (ImportError, AttributeError):
    pass

try:
except (ImportError, AttributeError):
    pass

try:
    from .unified_schema import __all__ as unified_all
    __all__.extend(unified_all)
except (ImportError, AttributeError):
    pass

try:
    from .registry import __all__ as registry_all
    __all__.extend(registry_all)
except (ImportError, AttributeError):
    pass