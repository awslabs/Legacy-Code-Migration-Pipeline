"""
Database Analyzer Tool for Legacy Mainframe Database Migration

Analyzes VSAM files, Sequential files, and database structures from legacy
mainframe systems and generates equivalent relational database schemas and
migration scripts for modern target systems.
"""

__version__ = "1.0.0"
__author__ = "LCMP Tools Team"

from .core.analyzer import DatabaseAnalyzer

__all__ = ['DatabaseAnalyzer']
