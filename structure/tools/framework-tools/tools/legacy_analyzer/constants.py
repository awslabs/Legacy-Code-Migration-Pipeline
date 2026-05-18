"""Constants used throughout the legacy analyzer.

This module defines constants to avoid magic numbers and improve code maintainability.
"""

# File size thresholds
FILE_SIZE_LARGE_MB = 10  # Files larger than this use streaming parser
FILE_SIZE_LARGE_BYTES = FILE_SIZE_LARGE_MB * 1024 * 1024

# Progress reporting
PROGRESS_REPORT_INTERVAL = 100  # Report progress every N items
PROGRESS_REPORT_BATCH_MULTIPLIER = 10  # Report every N batches

# Cache settings
DEFAULT_CACHE_SIZE = 10  # Default number of items to cache (LRU)
DEFAULT_CACHE_ENABLED = False  # Cache disabled by default

# Batch processing
DEFAULT_BATCH_SIZE = 1000  # Default batch size for database operations
LARGE_BATCH_SIZE = 5000  # Batch size for large operations

# File reading limits
MAX_PREVIEW_LINES = 50  # Maximum lines to read for file preview
MAX_PREVIEW_BYTES = 10240  # Maximum bytes to read for file preview (10KB)

# Validation limits
MAX_TRANSACTION_ID_LENGTH = 4  # CICS transaction IDs are 4 characters
MAX_PROGRAM_NAME_LENGTH = 8  # COBOL program names are typically 8 characters
MAX_GROUP_NAME_LENGTH = 20  # CICS group names
MAX_DATASET_NAME_LENGTH = 44  # MVS dataset names

# Resource types
RESOURCE_TYPE_TRANSACTION = 'TRANSACTION'
RESOURCE_TYPE_PROGRAM = 'PROGRAM'
RESOURCE_TYPE_FILE = 'FILE'
RESOURCE_TYPE_MAPSET = 'MAPSET'
RESOURCE_TYPE_LIBRARY = 'LIBRARY'
RESOURCE_TYPE_TDQUEUE = 'TDQUEUE'
RESOURCE_TYPE_TSQUEUE = 'TSQUEUE'
RESOURCE_TYPE_GROUP = 'GROUP'

# Resource status
STATUS_ENABLED = 'ENABLED'
STATUS_DISABLED = 'DISABLED'

# Entry point types
ENTRY_TYPE_ONLINE = 'ONLINE'
ENTRY_TYPE_BATCH = 'BATCH'
ENTRY_TYPE_INFERRED = 'INFERRED'

# Confidence levels
CONFIDENCE_EXPLICIT = 'EXPLICIT'
CONFIDENCE_INFERRED = 'INFERRED'

# Data sources
SOURCE_CSD = 'CSD'
SOURCE_JCL = 'JCL'
SOURCE_CODE_ANALYSIS = 'CODE_ANALYSIS'

# Service grouping
MIN_ENTRY_POINTS_FOR_SERVICE = 2  # Minimum entry points to consider as service
MIN_SHARED_DATA_FOR_HIGH_CONFIDENCE = 2  # Minimum shared datasets for high confidence
MIN_SHARED_PROGRAMS_FOR_HIGH_CONFIDENCE = 2  # Minimum shared programs for high confidence
MIN_ENTRY_POINTS_FOR_HIGH_CONFIDENCE = 3  # Minimum entry points for high confidence

# Consolidation scoring
CONSOLIDATION_SCORE_ENTRY_POINT_WEIGHT = 10  # Points per entry point
CONSOLIDATION_SCORE_ENTRY_POINT_MAX = 40  # Maximum points from entry points
CONSOLIDATION_SCORE_DATA_WEIGHT = 5  # Points per shared dataset
CONSOLIDATION_SCORE_DATA_MAX = 30  # Maximum points from shared data
CONSOLIDATION_SCORE_PROGRAM_WEIGHT = 3  # Points per shared program
CONSOLIDATION_SCORE_PROGRAM_MAX = 30  # Maximum points from shared programs

# Consolidation thresholds
CONSOLIDATION_SCORE_HIGH_THRESHOLD = 60  # Score >= this is high confidence
CONSOLIDATION_SCORE_LOW_THRESHOLD = 30  # Score < this is low confidence

# Recommendations
RECOMMENDATION_CONSIDER_MERGE = 'CONSIDER_MERGE'
RECOMMENDATION_KEEP_SEPARATE = 'KEEP_SEPARATE'
RECOMMENDATION_NEEDS_REVIEW = 'NEEDS_REVIEW'

# Confidence levels for service grouping
CONFIDENCE_HIGH = 'HIGH'
CONFIDENCE_MEDIUM = 'MEDIUM'
CONFIDENCE_LOW = 'LOW'

# Grouping reasons
GROUPING_REASON_CICS_GROUP = 'CICS_GROUP'
GROUPING_REASON_DATA_OWNERSHIP = 'DATA_OWNERSHIP'
GROUPING_REASON_SHARED_PROGRAMS = 'SHARED_PROGRAMS'

# Severity levels
SEVERITY_ERROR = 'ERROR'
SEVERITY_WARNING = 'WARNING'
SEVERITY_INFO = 'INFO'

# Issue types
ISSUE_TYPE_MISSING_IN_CODE = 'missing_in_code'
ISSUE_TYPE_MISSING_IN_CSD = 'missing_in_csd'
ISSUE_TYPE_STATUS_MISMATCH = 'status_mismatch'

# Dependency types
DEPENDENCY_TYPE_CALL = 'CALL'
DEPENDENCY_TYPE_EXEC_PGM = 'EXEC_PGM'
DEPENDENCY_TYPE_READ = 'READ'
DEPENDENCY_TYPE_WRITE = 'WRITE'
DEPENDENCY_TYPE_UPDATE = 'UPDATE'

# Artifact types
ARTIFACT_TYPE_PROGRAM = 'PROGRAM'
ARTIFACT_TYPE_DATASET = 'DATASET'
ARTIFACT_TYPE_JCL = 'JCL'

# File extensions
FILE_EXT_CSD = '.csd'
FILE_EXT_CSV = '.csv'
FILE_EXT_JCL = '.jcl'

# Skip directories during scanning
SKIP_DIRECTORIES = {
    '__pycache__',
    '.git',
    '.svn',
    'node_modules',
    'venv',
    'env',
    '.venv',
    'build',
    'dist',
    '.pytest_cache',
    '.mypy_cache',
}

# Dataset name parts to skip when generating service names
DATASET_SKIP_PARTS = {
    'AWS',
    'M2',
    'VSAM',
    'KSDS',
    'ESDS',
    'RRDS',
    'LDS',
}
