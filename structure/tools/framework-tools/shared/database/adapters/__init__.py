# Database adapters
"""
Common database adapters for the Migration Toolkit.

This module provides database adapter interfaces and implementations
for different database backends used across tools.
"""

from .base_adapter import BaseDatabaseAdapter
from .sqlite_adapter import SQLiteAdapter

__all__ = ['BaseDatabaseAdapter', 'SQLiteAdapter']
