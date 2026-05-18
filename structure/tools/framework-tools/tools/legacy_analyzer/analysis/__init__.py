"""Analysis module for legacy code analysis."""

from .flow_analyzer import FlowAnalyzer
from .call_graph import CallGraphBuilder
from .circular_detector import CircularDependencyDetector
from .flow_visualizer import FlowVisualizer, CallGraphVisualizer
from .flow_database import FlowDatabase
from .data_flow_analyzer import DataFlowAnalyzer
from .extended_flow_visualizer import ExtendedFlowVisualizer, DataLineageVisualizer
from .complexity_analyzer import ComplexityAnalyzer
from .missing_code_detector import MissingCodeDetector
from .missing_code_database import MissingCodeDatabase
from .missing_code_reporter import MissingCodeReporter
from .entry_point_detector import EntryPointDetector
from .service_grouping import ServiceGroupingAnalyzer, ServiceCandidate
from .program_boundary_detector import (
    ProgramBoundaryDetector,
    ProgramBoundaryDetectorFactory,
    RPGProgramBoundaryDetector,
    AssemblerProgramBoundaryDetector,
    NaturalProgramBoundaryDetector,
    REXXProgramBoundaryDetector
)
from .copybook_analyzer import (
    CopybookAnalyzer,
    LanguageCopybookAnalyzer,
    COBOLCopybookAnalyzer,
    PLICopybookAnalyzer,
    NaturalCopybookAnalyzer
)

__all__ = [
    'FlowAnalyzer',
    'CallGraphBuilder',
    'CircularDependencyDetector',
    'FlowVisualizer',
    'CallGraphVisualizer',
    'FlowDatabase',
    'DataFlowAnalyzer',
    'ExtendedFlowVisualizer',
    'DataLineageVisualizer',
    'ComplexityAnalyzer',
    'MissingCodeDetector',
    'MissingCodeDatabase',
    'MissingCodeReporter',
    'EntryPointDetector',
    'ServiceGroupingAnalyzer',
    'ServiceCandidate',
    'ProgramBoundaryDetector',
    'ProgramBoundaryDetectorFactory',
    'RPGProgramBoundaryDetector',
    'AssemblerProgramBoundaryDetector',
    'NaturalProgramBoundaryDetector',
    'REXXProgramBoundaryDetector',
    'CopybookAnalyzer',
    'LanguageCopybookAnalyzer',
    'COBOLCopybookAnalyzer',
    'PLICopybookAnalyzer',
    'NaturalCopybookAnalyzer',
]
