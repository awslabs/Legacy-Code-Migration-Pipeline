"""Legacy Analyzer - Comprehensive Migration Analysis System.

This module provides functionality for loading and managing mainframe artifact
inventories, including JCL, programs, copybooks, datasets, and CICS resources,
as well as advanced analysis capabilities for migration planning.

The new architecture provides proper separation of concerns:
- InventoryManager: Complete inventory discovery and population
- DependencyAnalyzer: Pure dependency extraction
- DependencyValidator: Validation against complete inventory
- AnalysisOrchestrator: Workflow coordination
"""

__version__ = "3.0.0"

from .inventory.inventory_loader import InventoryLoader
from .inventory_manager import InventoryManager
from .dependency_analyzer import DependencyAnalyzer
from .dependency_validator import DependencyValidator
from .analysis_orchestrator import AnalysisOrchestrator
from .api import LegacyAnalyzerAPI

__all__ = [
    "InventoryLoader",
    "InventoryManager", 
    "DependencyAnalyzer",
    "DependencyValidator",
    "AnalysisOrchestrator",
    "LegacyAnalyzerAPI",
]
