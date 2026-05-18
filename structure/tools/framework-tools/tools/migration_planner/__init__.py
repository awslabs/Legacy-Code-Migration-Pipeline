"""
Migration Planner Tool - Workpackage Planning and Migration Orchestration

This module provides automated migration workpackage planning from business flow analysis.
It calculates priority scores, assigns workpackage IDs, determines migration phases based
on dependencies, and generates comprehensive planning outputs.

Capabilities:
- Priority score calculation based on complexity metrics
- Sequential workpackage assignment with pre-existent module tracking
- Migration phase determination through dependency analysis
- Comprehensive JSON and Markdown output generation
- Dependency validation and circular dependency detection

Example Usage:
    from tools.migration_planner import MigrationPlanner
    from tools.migration_planner.models import PlannerConfig
    
    # Configure planner
    config = PlannerConfig(
        flows_file="./results/carddemo_analysis/flows/Business_Flows.json",
        output_base="./results/migration/",
        project_name="carddemo"
    )
    
    # Run planning pipeline
    planner = MigrationPlanner(config)
    result = planner.run()
"""

__version__ = "0.2.0-dev"

# Import data models
from .models import (
    BusinessFlow,
    Program,
    PriorityResult,
    PriorityFactors,
    WorkpackageAssignment,
    PhaseAssignment,
    MigrationSequenceItem,
    PlanningData,
    Metadata,
    Statistics,
    PlannerConfig,
)

# Import logging configuration
from .logging_config import setup_logging, get_logger

# Import orchestrator
from .planner import MigrationPlanner, PlanningResult

# Export main classes and functions
__all__ = [
    # Data models
    'BusinessFlow',
    'Program',
    'PriorityResult',
    'PriorityFactors',
    'WorkpackageAssignment',
    'PhaseAssignment',
    'MigrationSequenceItem',
    'PlanningData',
    'Metadata',
    'Statistics',
    'PlannerConfig',
    # Logging
    'setup_logging',
    'get_logger',
    # Orchestrator
    'MigrationPlanner',
    'PlanningResult',
]


def get_version():
    """Get the migration planner version."""
    return __version__