"""
Migration Flow Export Exceptions

This module defines custom exceptions for migration flow export operations.
These exceptions provide specific error handling for validation, missing data,
and export failures.
"""


class FlowValidationError(Exception):
    """
    Raised when flow data is invalid or fails validation.
    
    This exception is raised when:
    - Flow data structure is malformed
    - Required fields are missing or invalid
    - Data constraints are violated
    - Flow relationships are inconsistent
    
    Examples:
        - Entry point program name is empty
        - Flow ID format is invalid
        - Scope contains invalid artifact types
        - Interface references non-existent programs
        - Circular dependencies are detected
    """
    
    def __init__(self, message: str, flow_id: str = None, details: dict = None):
        """
        Initialize FlowValidationError.
        
        Args:
            message: Human-readable error message
            flow_id: Optional flow ID where validation failed
            details: Optional dictionary with additional error details
        """
        self.flow_id = flow_id
        self.details = details or {}
        
        # Build full error message
        full_message = message
        if flow_id:
            full_message = f"[{flow_id}] {message}"
        
        super().__init__(full_message)


class MissingDataError(Exception):
    """
    Raised when required data is missing from the database or analysis.
    
    This exception is raised when:
    - Entry point data is missing
    - Complexity metrics are not available
    - Dependencies are incomplete
    - Required database tables don't exist
    - Referenced artifacts cannot be found
    
    Examples:
        - Entry point program has no dependencies
        - Complexity metrics table doesn't exist
        - Flow references non-existent program
        - Interface target program not found
        - Data operation references missing dataset
    """
    
    def __init__(self, message: str, data_type: str = None, artifact_name: str = None):
        """
        Initialize MissingDataError.
        
        Args:
            message: Human-readable error message
            data_type: Optional type of missing data (e.g., 'complexity', 'dependencies')
            artifact_name: Optional name of missing artifact
        """
        self.data_type = data_type
        self.artifact_name = artifact_name
        
        # Build full error message
        full_message = message
        if data_type and artifact_name:
            full_message = f"Missing {data_type} for {artifact_name}: {message}"
        elif data_type:
            full_message = f"Missing {data_type}: {message}"
        
        super().__init__(full_message)


class ExportError(Exception):
    """
    Raised when flow export operation fails.
    
    This exception is raised when:
    - Database query fails during export
    - JSON serialization fails
    - File write operation fails
    - Export format is invalid
    - Transaction rollback occurs
    
    Examples:
        - Cannot connect to database
        - JSON encoding error
        - File permission denied
        - Disk space exhausted
        - Database transaction fails
    """
    
    def __init__(self, message: str, operation: str = None, cause: Exception = None):
        """
        Initialize ExportError.
        
        Args:
            message: Human-readable error message
            operation: Optional operation that failed (e.g., 'query', 'write', 'format')
            cause: Optional underlying exception that caused the error
        """
        self.operation = operation
        self.cause = cause
        
        # Build full error message
        full_message = message
        if operation:
            full_message = f"Export failed during {operation}: {message}"
        if cause:
            full_message = f"{full_message} (caused by: {type(cause).__name__}: {cause})"
        
        super().__init__(full_message)
