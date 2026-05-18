"""Migration planning module for legacy analyzer."""

from .package_builder import PackageBuilder
from .package_optimizer import PackageOptimizer
from .package_exporter import PackageExporter
from .package_database import PackageDatabase
from .schema import MigrationFlowSchema, create_migration_flow_schema, verify_migration_flow_schema
from .flow_builder import generate_flow_id, MigrationFlowBuilder
from .entry_point_type_detector import EntryPointTypeDetector
from .external_config import (
    ExternalConfigLoader,
    ExternalConfigError,
    load_external_config,
    is_external_program,
    get_external_callers
)
from .utility_detector import UtilityDetector, detect_utility_programs
from .data_operation_inferencer import DataOperationInferencer
from .flow_exporter import MigrationFlowExporter, FlowExportConfig
from .json_schema_validator import JSONSchemaValidator
from .exceptions import FlowValidationError, MissingDataError, ExportError

# Performance optimization modules
from .flow_cache import FlowCache, QueryResultCache
from .complexity_cache import ComplexityCache
from .optimized_queries import OptimizedFlowQueries
from .batch_operations import BatchDatabaseOperations
from .query_profiler import QueryProfiler, QueryOptimizer

__all__ = [
    'PackageBuilder',
    'PackageOptimizer',
    'PackageExporter',
    'PackageDatabase',
    'MigrationFlowSchema',
    'create_migration_flow_schema',
    'verify_migration_flow_schema',
    'generate_flow_id',
    'MigrationFlowBuilder',
    'EntryPointTypeDetector',
    'ExternalConfigLoader',
    'ExternalConfigError',
    'load_external_config',
    'is_external_program',
    'get_external_callers',
    'UtilityDetector',
    'detect_utility_programs',
    'DataOperationInferencer',
    'MigrationFlowExporter',
    'FlowExportConfig',
    'JSONSchemaValidator',
    'FlowValidationError',
    'MissingDataError',
    'ExportError',
    # Performance optimization
    'FlowCache',
    'QueryResultCache',
    'ComplexityCache',
    'OptimizedFlowQueries',
    'BatchDatabaseOperations',
    'QueryProfiler',
    'QueryOptimizer'
]

