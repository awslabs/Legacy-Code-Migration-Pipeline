"""Custom exceptions for Legacy Analyzer.

This module defines a hierarchy of custom exceptions with error codes
for better error handling and troubleshooting.
"""


class LegacyAnalyzerError(Exception):
    """Base exception for all Legacy Analyzer errors.
    
    Attributes:
        error_code: Unique error code (format: CICS-XXX-YYY)
        message: Human-readable error message
        details: Additional context about the error
        suggestion: Suggested action to resolve the error
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "CICS-000-000",
        details: str = None,
        suggestion: str = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.suggestion = suggestion
        
        # Build full error message
        full_message = f"[{error_code}] {message}"
        if details:
            full_message += f"\n  Details: {details}"
        if suggestion:
            full_message += f"\n  Suggestion: {suggestion}"
        
        super().__init__(full_message)
    
    def __str__(self):
        return super().__str__()


# Parser Exceptions (CICS-PAR-XXX)

class CSDParserError(LegacyAnalyzerError):
    """Base exception for CSD parser errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-PAR-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class CSDSyntaxError(CSDParserError):
    """Exception for CSD syntax errors."""
    
    def __init__(
        self,
        message: str,
        line_number: int = None,
        line_content: str = None,
        **kwargs
    ):
        self.line_number = line_number
        self.line_content = line_content
        
        details = kwargs.get('details', '')
        if line_number:
            details = f"Line {line_number}: {details}" if details else f"Line {line_number}"
        if line_content:
            details += f"\n  Content: {line_content[:100]}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-PAR-001')
        kwargs.setdefault('suggestion', 'Check CSD file format and ensure it follows IBM CICS standards')
        
        super().__init__(message, **kwargs)


class CSDValidationError(CSDParserError):
    """Exception for CSD data validation errors."""
    
    def __init__(
        self,
        message: str,
        resource_name: str = None,
        resource_type: str = None,
        **kwargs
    ):
        self.resource_name = resource_name
        self.resource_type = resource_type
        
        details = kwargs.get('details', '')
        if resource_name:
            details = f"Resource: {resource_name}" + (f" ({details})" if details else "")
        if resource_type:
            details = f"Type: {resource_type}, {details}" if details else f"Type: {resource_type}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-PAR-002')
        
        super().__init__(message, **kwargs)


class CSDAttributeError(CSDParserError):
    """Exception for missing or invalid CSD attributes."""
    
    def __init__(
        self,
        message: str,
        attribute_name: str = None,
        resource_name: str = None,
        **kwargs
    ):
        self.attribute_name = attribute_name
        self.resource_name = resource_name
        
        details = kwargs.get('details', '')
        if attribute_name:
            details = f"Attribute: {attribute_name}" + (f", {details}" if details else "")
        if resource_name:
            details = f"Resource: {resource_name}, {details}" if details else f"Resource: {resource_name}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-PAR-003')
        
        super().__init__(message, **kwargs)


class CSDDuplicateError(CSDParserError):
    """Exception for duplicate CSD resources."""
    
    def __init__(
        self,
        message: str,
        resource_name: str = None,
        resource_type: str = None,
        locations: list = None,
        **kwargs
    ):
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.locations = locations or []
        
        details = kwargs.get('details', '')
        if resource_name and resource_type:
            details = f"{resource_type} '{resource_name}'" + (f": {details}" if details else "")
        if locations:
            details += f"\n  Found at: {', '.join(str(loc) for loc in locations)}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-PAR-004')
        kwargs.setdefault('suggestion', 'Remove duplicate definitions or use --skip-duplicates option')
        
        super().__init__(message, **kwargs)


# CLI Exceptions (CICS-CLI-XXX)

class CLIError(LegacyAnalyzerError):
    """Base exception for CLI errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-CLI-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class CLIFileNotFoundError(CLIError):
    """Exception for file not found errors."""
    
    def __init__(self, file_path: str, **kwargs):
        self.file_path = file_path
        
        kwargs.setdefault('details', f"Path: {file_path}")
        kwargs.setdefault('error_code', 'CICS-CLI-001')
        kwargs.setdefault('suggestion', 'Check the file path and ensure the file exists')
        
        super().__init__(f"File not found", **kwargs)


class CLIDirectoryNotFoundError(CLIError):
    """Exception for directory not found errors."""
    
    def __init__(self, dir_path: str, **kwargs):
        self.dir_path = dir_path
        
        kwargs.setdefault('details', f"Path: {dir_path}")
        kwargs.setdefault('error_code', 'CICS-CLI-002')
        kwargs.setdefault('suggestion', 'Check the directory path and ensure it exists')
        
        super().__init__(f"Directory not found", **kwargs)


class CLIInvalidOptionError(CLIError):
    """Exception for invalid CLI option combinations."""
    
    def __init__(self, message: str, options: list = None, **kwargs):
        self.options = options or []
        
        if options:
            kwargs.setdefault('details', f"Options: {', '.join(options)}")
        kwargs.setdefault('error_code', 'CICS-CLI-003')
        
        super().__init__(message, **kwargs)


class CLIPermissionError(CLIError):
    """Exception for permission denied errors."""
    
    def __init__(self, path: str, operation: str = "access", **kwargs):
        self.path = path
        self.operation = operation
        
        kwargs.setdefault('details', f"Path: {path}, Operation: {operation}")
        kwargs.setdefault('error_code', 'CICS-CLI-004')
        kwargs.setdefault('suggestion', 'Check file/directory permissions')
        
        super().__init__(f"Permission denied", **kwargs)


class CLIValidationError(CLIError):
    """Exception for CLI input validation errors."""
    
    def __init__(self, message: str, parameter: str = None, value: str = None, **kwargs):
        self.parameter = parameter
        self.value = value
        
        details = kwargs.get('details', '')
        if parameter:
            details = f"Parameter: {parameter}" + (f", {details}" if details else "")
        if value:
            details += f", Value: {value}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-CLI-005')
        
        super().__init__(message, **kwargs)


# Scanner Exceptions (CICS-SCN-XXX)

class ScannerError(LegacyAnalyzerError):
    """Base exception for metadata scanner errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-SCN-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class ScannerPermissionError(ScannerError):
    """Exception for scanner permission errors."""
    
    def __init__(self, path: str, **kwargs):
        self.path = path
        
        kwargs.setdefault('details', f"Path: {path}")
        kwargs.setdefault('error_code', 'CICS-SCN-001')
        kwargs.setdefault('suggestion', 'Check directory permissions or run with appropriate privileges')
        
        super().__init__(f"Permission denied while scanning", **kwargs)


class ScannerValidationError(ScannerError):
    """Exception for scanner validation errors."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'CICS-SCN-002')
        super().__init__(message, **kwargs)


# Loader Exceptions (CICS-LDR-XXX)

class LoaderError(LegacyAnalyzerError):
    """Base exception for inventory loader errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-LDR-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class LoaderCSVValidationError(LoaderError):
    """Exception for CSV validation errors."""
    
    def __init__(
        self,
        message: str,
        file_path: str = None,
        missing_columns: list = None,
        **kwargs
    ):
        self.file_path = file_path
        self.missing_columns = missing_columns or []
        
        details = kwargs.get('details', '')
        if file_path:
            details = f"File: {file_path}" + (f", {details}" if details else "")
        if missing_columns:
            details += f"\n  Missing columns: {', '.join(missing_columns)}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-LDR-001')
        kwargs.setdefault('suggestion', 'Check CSV format and ensure all required columns are present')
        
        super().__init__(message, **kwargs)


class LoaderDuplicateError(LoaderError):
    """Exception for duplicate entries during loading."""
    
    def __init__(
        self,
        message: str,
        resource_name: str = None,
        resource_type: str = None,
        **kwargs
    ):
        self.resource_name = resource_name
        self.resource_type = resource_type
        
        details = kwargs.get('details', '')
        if resource_name:
            details = f"Resource: {resource_name}" + (f", {details}" if details else "")
        if resource_type:
            details = f"Type: {resource_type}, {details}" if details else f"Type: {resource_type}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-LDR-002')
        kwargs.setdefault('suggestion', 'Use --update-duplicates to update existing entries')
        
        super().__init__(message, **kwargs)


class LoaderDataQualityError(LoaderError):
    """Exception for data quality issues during loading."""
    
    def __init__(
        self,
        message: str,
        row_number: int = None,
        column: str = None,
        value: str = None,
        **kwargs
    ):
        self.row_number = row_number
        self.column = column
        self.value = value
        
        details = kwargs.get('details', '')
        if row_number:
            details = f"Row {row_number}" + (f": {details}" if details else "")
        if column:
            details += f", Column: {column}"
        if value:
            details += f", Value: {value}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-LDR-003')
        
        super().__init__(message, **kwargs)


# Database Exceptions (CICS-DB-XXX)

class DatabaseError(LegacyAnalyzerError):
    """Base exception for database errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-DB-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class DatabaseConnectionError(DatabaseError):
    """Exception for database connection errors."""
    
    def __init__(self, db_path: str, **kwargs):
        self.db_path = db_path
        
        kwargs.setdefault('details', f"Database: {db_path}")
        kwargs.setdefault('error_code', 'CICS-DB-001')
        kwargs.setdefault('suggestion', 'Check database path and permissions')
        
        super().__init__(f"Failed to connect to database", **kwargs)


class DatabaseSchemaError(DatabaseError):
    """Exception for database schema errors."""
    
    def __init__(self, message: str, table_name: str = None, **kwargs):
        self.table_name = table_name
        
        if table_name:
            kwargs.setdefault('details', f"Table: {table_name}")
        kwargs.setdefault('error_code', 'CICS-DB-002')
        kwargs.setdefault('suggestion', 'Run schema migration or recreate database')
        
        super().__init__(message, **kwargs)


# Validation Exceptions (CICS-VAL-XXX)

class ValidationError(LegacyAnalyzerError):
    """Base exception for validation errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-VAL-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class ResourceNameValidationError(ValidationError):
    """Exception for invalid resource names."""
    
    def __init__(
        self,
        resource_name: str,
        resource_type: str = None,
        reason: str = None,
        **kwargs
    ):
        self.resource_name = resource_name
        self.resource_type = resource_type
        
        details = f"Name: {resource_name}"
        if resource_type:
            details = f"Type: {resource_type}, {details}"
        if reason:
            details += f", Reason: {reason}"
        
        kwargs.setdefault('details', details)
        kwargs.setdefault('error_code', 'CICS-VAL-001')
        
        super().__init__(f"Invalid resource name", **kwargs)


class AttributeValidationError(ValidationError):
    """Exception for invalid attribute values."""
    
    def __init__(
        self,
        attribute_name: str,
        value: str,
        expected: str = None,
        **kwargs
    ):
        self.attribute_name = attribute_name
        self.value = value
        self.expected = expected
        
        details = f"Attribute: {attribute_name}, Value: {value}"
        if expected:
            details += f", Expected: {expected}"
        
        kwargs.setdefault('details', details)
        kwargs.setdefault('error_code', 'CICS-VAL-002')
        
        super().__init__(f"Invalid attribute value", **kwargs)


# Reconciliation Exceptions (CICS-REC-XXX)

class ReconciliationError(LegacyAnalyzerError):
    """Base exception for reconciliation errors."""
    
    def __init__(self, message: str, error_code: str = "CICS-REC-000", **kwargs):
        super().__init__(message, error_code, **kwargs)


class ReconciliationMismatchError(ReconciliationError):
    """Exception for reconciliation mismatches."""
    
    def __init__(
        self,
        message: str,
        resource_name: str = None,
        mismatch_type: str = None,
        **kwargs
    ):
        self.resource_name = resource_name
        self.mismatch_type = mismatch_type
        
        details = kwargs.get('details', '')
        if resource_name:
            details = f"Resource: {resource_name}" + (f", {details}" if details else "")
        if mismatch_type:
            details = f"Type: {mismatch_type}, {details}" if details else f"Type: {mismatch_type}"
        
        kwargs['details'] = details
        kwargs.setdefault('error_code', 'CICS-REC-001')
        
        super().__init__(message, **kwargs)
