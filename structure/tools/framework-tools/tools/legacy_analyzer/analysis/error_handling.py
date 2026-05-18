"""Comprehensive error handling and recovery framework for program-level dependency tracking.

This module provides:
- Error recovery for malformed program boundaries
- Transaction management for atomic program-level updates
- Logging and monitoring for program-level analysis operations
- Validation for program boundary detection accuracy
"""

import logging
import time
import traceback
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
from enum import Enum
import sqlite3
from pathlib import Path

from ..exceptions import (
    LegacyAnalyzerError,
    DatabaseError,
    ValidationError,
    ScannerError
)
from ..models.program_boundary import ProgramBoundary, ProgramType
from .program_validation import ValidationResult, AccuracyMetrics


class ErrorSeverity(Enum):
    """Error severity levels for program-level analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategies for different types of errors."""
    IGNORE = "ignore"
    FALLBACK = "fallback"
    RETRY = "retry"
    ABORT = "abort"
    USER_INTERVENTION = "user_intervention"


@dataclass
class ErrorContext:
    """Context information for error handling and recovery."""
    operation: str
    file_path: Optional[str] = None
    language: Optional[str] = None
    program_name: Optional[str] = None
    line_number: Optional[int] = None
    source_code_snippet: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """Result of an error recovery operation."""
    success: bool
    strategy_used: RecoveryStrategy
    recovered_data: Optional[Any] = None
    fallback_data: Optional[Any] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class TransactionState:
    """State information for database transactions."""
    transaction_id: str
    start_time: float
    operations: List[str] = field(default_factory=list)
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


class ProgramBoundaryErrorRecovery:
    """Error recovery for malformed program boundaries."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize program boundary error recovery.
        
        Args:
            logger: Optional logger instance for error reporting
        """
        self.logger = logger or logging.getLogger(__name__)
        self.recovery_stats = {
            'boundaries_recovered': 0,
            'boundaries_failed': 0,
            'fallback_to_file_level': 0
        }
    
    def recover_malformed_boundaries(self, 
                                   source_code: str,
                                   language: str,
                                   malformed_programs: List[ProgramBoundary],
                                   error_context: ErrorContext) -> RecoveryResult:
        """
        Attempt to recover from malformed program boundaries.
        
        Args:
            source_code: Source code content
            language: Programming language
            malformed_programs: List of programs with boundary issues
            error_context: Context information about the error
            
        Returns:
            RecoveryResult with recovery outcome and data
        """
        self.logger.info(f"Attempting boundary recovery for {len(malformed_programs)} programs in {error_context.file_path}")
        
        recovered_programs = []
        warnings = []
        
        try:
            total_lines = len(source_code.splitlines())
            
            for program in malformed_programs:
                recovery_result = self._recover_single_boundary(
                    program, source_code, total_lines, language
                )
                
                if recovery_result.success:
                    recovered_programs.append(recovery_result.recovered_data)
                    self.recovery_stats['boundaries_recovered'] += 1
                    if recovery_result.warnings:
                        warnings.extend(recovery_result.warnings)
                else:
                    self.recovery_stats['boundaries_failed'] += 1
                    warnings.append(f"Could not recover program '{program.program_name}': {recovery_result.error_message}")
            
            if recovered_programs:
                # Validate recovered boundaries don't overlap
                validation_result = self._validate_recovered_boundaries(recovered_programs, total_lines)
                if not validation_result.is_valid:
                    # Fall back to file-level analysis
                    self.recovery_stats['fallback_to_file_level'] += 1
                    return RecoveryResult(
                        success=True,
                        strategy_used=RecoveryStrategy.FALLBACK,
                        fallback_data={'use_file_level': True},
                        warnings=warnings + validation_result.errors
                    )
                
                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.RETRY,
                    recovered_data=recovered_programs,
                    warnings=warnings
                )
            else:
                # No programs could be recovered, fall back to file-level
                self.recovery_stats['fallback_to_file_level'] += 1
                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.FALLBACK,
                    fallback_data={'use_file_level': True},
                    warnings=warnings
                )
        
        except Exception as e:
            self.logger.error(f"Error during boundary recovery: {str(e)}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.ABORT,
                error_message=str(e)
            )
    
    def _recover_single_boundary(self, 
                               program: ProgramBoundary,
                               source_code: str,
                               total_lines: int,
                               language: str) -> RecoveryResult:
        """Recover a single malformed program boundary."""
        warnings = []
        
        # Fix invalid start line
        if program.start_line < 1:
            program.start_line = 1
            warnings.append(f"Adjusted start_line for '{program.program_name}' from {program.start_line} to 1")
        
        # Fix invalid end line
        if program.end_line < program.start_line:
            # Try to find a reasonable end line
            program.end_line = min(program.start_line + 100, total_lines)  # Default to 100 lines or end of file
            warnings.append(f"Adjusted end_line for '{program.program_name}' to {program.end_line}")
        
        if program.end_line > total_lines:
            program.end_line = total_lines
            warnings.append(f"Adjusted end_line for '{program.program_name}' to file end ({total_lines})")
        
        # Validate program name
        if not program.program_name or not program.program_name.strip():
            program.program_name = f"RECOVERED_PROGRAM_{program.start_line}"
            warnings.append(f"Generated program name: {program.program_name}")
        
        # Set default program type if missing
        if not program.program_type:
            program.program_type = ProgramType.MAIN
            warnings.append(f"Set default program type for '{program.program_name}': {program.program_type}")
        
        # Ensure language is set
        if not program.language:
            program.language = language
        
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.RETRY,
            recovered_data=program,
            warnings=warnings
        )
    
    def _validate_recovered_boundaries(self, 
                                     programs: List[ProgramBoundary],
                                     total_lines: int) -> ValidationResult:
        """Validate that recovered boundaries are valid and non-overlapping."""
        errors = []
        
        # Check for overlaps
        for i, prog1 in enumerate(programs):
            for j, prog2 in enumerate(programs[i+1:], i+1):
                if prog1.overlaps_with(prog2):
                    errors.append(
                        f"Recovered programs still overlap: '{prog1.program_name}' "
                        f"({prog1.start_line}-{prog1.end_line}) and '{prog2.program_name}' "
                        f"({prog2.start_line}-{prog2.end_line})"
                    )
        
        # Check boundaries are within file
        for program in programs:
            if program.start_line < 1 or program.end_line > total_lines:
                errors.append(f"Program '{program.program_name}' boundaries outside file range")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)


class TransactionManager:
    """Transaction management for atomic program-level updates."""
    
    def __init__(self, database, logger: Optional[logging.Logger] = None):
        """Initialize transaction manager.
        
        Args:
            database: Database adapter instance
            logger: Optional logger instance
        """
        self.database = database
        self.logger = logger or logging.getLogger(__name__)
        self.active_transactions: Dict[str, TransactionState] = {}
        self.transaction_counter = 0
    
    @contextmanager
    def atomic_operation(self, operation_name: str, rollback_data: Optional[Dict[str, Any]] = None):
        """
        Context manager for atomic database operations.
        
        Args:
            operation_name: Name of the operation for logging
            rollback_data: Optional data needed for rollback
            
        Yields:
            Transaction ID for tracking
        """
        transaction_id = self._start_transaction(operation_name, rollback_data or {})
        
        try:
            yield transaction_id
            self._commit_transaction(transaction_id)
        except Exception as e:
            self._rollback_transaction(transaction_id, e)
            raise
        finally:
            self._cleanup_transaction(transaction_id)
    
    def _start_transaction(self, operation_name: str, rollback_data: Dict[str, Any]) -> str:
        """Start a new transaction."""
        self.transaction_counter += 1
        transaction_id = f"tx_{self.transaction_counter}_{int(time.time() * 1000)}"
        
        # Begin database transaction
        try:
            if hasattr(self.database, 'begin_transaction'):
                self.database.begin_transaction()
            elif hasattr(self.database, 'cursor'):
                self.database.cursor.execute("BEGIN TRANSACTION")
        except Exception as e:
            self.logger.error(f"Failed to begin database transaction: {str(e)}")
            raise DatabaseError(f"Failed to begin transaction for {operation_name}", str(e))
        
        # Track transaction state
        self.active_transactions[transaction_id] = TransactionState(
            transaction_id=transaction_id,
            start_time=time.time(),
            rollback_data=rollback_data
        )
        
        self.logger.debug(f"Started transaction {transaction_id} for operation: {operation_name}")
        return transaction_id
    
    def _commit_transaction(self, transaction_id: str):
        """Commit a transaction."""
        if transaction_id not in self.active_transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        try:
            self.database.commit()
            
            transaction = self.active_transactions[transaction_id]
            duration = time.time() - transaction.start_time
            
            self.logger.info(f"Committed transaction {transaction_id} in {duration:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to commit transaction {transaction_id}: {str(e)}")
            raise DatabaseError(f"Failed to commit transaction {transaction_id}", str(e))
    
    def _rollback_transaction(self, transaction_id: str, error: Exception):
        """Rollback a transaction and attempt recovery."""
        if transaction_id not in self.active_transactions:
            self.logger.warning(f"Attempted to rollback unknown transaction: {transaction_id}")
            return
        
        transaction = self.active_transactions[transaction_id]
        
        try:
            # Rollback database changes
            self.database.rollback()
            
            # Attempt to restore any application state if rollback_data provided
            if transaction.rollback_data:
                self._restore_application_state(transaction.rollback_data)
            
            duration = time.time() - transaction.start_time
            self.logger.warning(f"Rolled back transaction {transaction_id} after {duration:.3f}s due to: {str(error)}")
            
        except Exception as rollback_error:
            self.logger.error(f"Failed to rollback transaction {transaction_id}: {str(rollback_error)}")
            # This is a critical error - we may have inconsistent state
            raise DatabaseError(
                f"Critical: Failed to rollback transaction {transaction_id}",
                f"Original error: {str(error)}, Rollback error: {str(rollback_error)}"
            )
    
    def _restore_application_state(self, rollback_data: Dict[str, Any]):
        """Restore application state using rollback data."""
        # This is a placeholder for application-specific rollback logic
        # In a real implementation, this would restore in-memory state,
        # file system changes, etc.
        self.logger.debug(f"Restoring application state with data: {rollback_data}")
    
    def _cleanup_transaction(self, transaction_id: str):
        """Clean up transaction resources."""
        if transaction_id in self.active_transactions:
            del self.active_transactions[transaction_id]
    
    def get_active_transactions(self) -> List[str]:
        """Get list of active transaction IDs."""
        return list(self.active_transactions.keys())
    
    def force_rollback_all(self):
        """Force rollback of all active transactions (emergency cleanup)."""
        self.logger.warning(f"Force rolling back {len(self.active_transactions)} active transactions")
        
        for transaction_id in list(self.active_transactions.keys()):
            try:
                self._rollback_transaction(transaction_id, Exception("Force rollback"))
                self._cleanup_transaction(transaction_id)
            except Exception as e:
                self.logger.error(f"Error during force rollback of {transaction_id}: {str(e)}")


class ProgramAnalysisLogger:
    """Specialized logger for program-level analysis operations."""
    
    def __init__(self, 
                 log_file: Optional[str] = None,
                 log_level: int = logging.INFO,
                 enable_performance_logging: bool = True):
        """Initialize program analysis logger.
        
        Args:
            log_file: Optional path to log file
            log_level: Logging level
            enable_performance_logging: Whether to log performance metrics
        """
        self.logger = logging.getLogger('program_analysis')
        self.logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        self.enable_performance_logging = enable_performance_logging
        self.operation_timers: Dict[str, float] = {}
    
    def log_operation_start(self, operation: str, context: ErrorContext):
        """Log the start of a program analysis operation."""
        if self.enable_performance_logging:
            self.operation_timers[operation] = time.time()
        
        context_info = []
        if context.file_path:
            context_info.append(f"file={context.file_path}")
        if context.language:
            context_info.append(f"language={context.language}")
        if context.program_name:
            context_info.append(f"program={context.program_name}")
        
        context_str = ", ".join(context_info) if context_info else "no context"
        self.logger.info(f"Starting {operation} ({context_str})")
    
    def log_operation_end(self, operation: str, success: bool, details: Optional[Dict[str, Any]] = None):
        """Log the end of a program analysis operation."""
        duration = None
        if self.enable_performance_logging and operation in self.operation_timers:
            duration = time.time() - self.operation_timers[operation]
            del self.operation_timers[operation]
        
        status = "SUCCESS" if success else "FAILED"
        duration_str = f" in {duration:.3f}s" if duration else ""
        
        details_str = ""
        if details:
            detail_items = [f"{k}={v}" for k, v in details.items()]
            details_str = f" ({', '.join(detail_items)})"
        
        self.logger.info(f"Completed {operation}: {status}{duration_str}{details_str}")
    
    def log_error_with_context(self, 
                             error: Exception,
                             context: ErrorContext,
                             severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        """Log an error with full context information."""
        error_msg = f"[{severity.value.upper()}] {str(error)}"
        
        if context.file_path:
            error_msg += f" (file: {context.file_path}"
            if context.line_number:
                error_msg += f", line: {context.line_number}"
            error_msg += ")"
        
        if context.program_name:
            error_msg += f" (program: {context.program_name})"
        
        if context.source_code_snippet:
            error_msg += f"\nCode snippet: {context.source_code_snippet[:100]}..."
        
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(error_msg)
            if severity == ErrorSeverity.CRITICAL:
                self.logger.error(f"Stack trace: {traceback.format_exc()}")
        else:
            self.logger.warning(error_msg)
    
    def log_recovery_attempt(self, 
                           strategy: RecoveryStrategy,
                           context: ErrorContext,
                           result: RecoveryResult):
        """Log an error recovery attempt and its result."""
        status = "SUCCESS" if result.success else "FAILED"
        
        msg = f"Recovery attempt using {strategy.value}: {status}"
        if context.file_path:
            msg += f" (file: {context.file_path})"
        if context.program_name:
            msg += f" (program: {context.program_name})"
        
        if result.warnings:
            msg += f" (warnings: {len(result.warnings)})"
        
        if result.success:
            self.logger.info(msg)
        else:
            self.logger.warning(msg)
            if result.error_message:
                self.logger.warning(f"Recovery error: {result.error_message}")


class ProgramBoundaryAccuracyValidator:
    """Validator for program boundary detection accuracy with error handling."""
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 accuracy_threshold: float = 0.8):
        """Initialize accuracy validator.
        
        Args:
            logger: Optional logger instance
            accuracy_threshold: Minimum accuracy threshold (0.0 to 1.0)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.accuracy_threshold = accuracy_threshold
        self.validation_stats = {
            'files_validated': 0,
            'files_passed': 0,
            'files_failed': 0,
            'total_accuracy_score': 0.0
        }
    
    def validate_program_detection_accuracy(self,
                                          file_path: str,
                                          source_code: str,
                                          language: str,
                                          detected_programs: List[ProgramBoundary],
                                          program_dependencies: Dict[str, List[str]]) -> ValidationResult:
        """
        Validate the accuracy of program boundary detection.
        
        Args:
            file_path: Path to the analyzed file
            source_code: Source code content
            language: Programming language
            detected_programs: List of detected program boundaries
            program_dependencies: Program-level dependencies
            
        Returns:
            ValidationResult with accuracy assessment
        """
        self.validation_stats['files_validated'] += 1
        
        errors = []
        warnings = []
        details = {}
        
        try:
            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(
                source_code, detected_programs, program_dependencies
            )
            
            details['accuracy_metrics'] = accuracy_metrics
            
            # Check if accuracy meets threshold
            if accuracy_metrics['overall_accuracy'] < self.accuracy_threshold:
                errors.append(
                    f"Program detection accuracy ({accuracy_metrics['overall_accuracy']:.2f}) "
                    f"below threshold ({self.accuracy_threshold:.2f})"
                )
                self.validation_stats['files_failed'] += 1
            else:
                self.validation_stats['files_passed'] += 1
            
            self.validation_stats['total_accuracy_score'] += accuracy_metrics['overall_accuracy']
            
            # Validate program boundaries are reasonable
            boundary_validation = self._validate_boundary_reasonableness(
                source_code, detected_programs, language
            )
            
            errors.extend(boundary_validation['errors'])
            warnings.extend(boundary_validation['warnings'])
            details['boundary_validation'] = boundary_validation
            
            # Validate dependencies make sense
            dependency_validation = self._validate_dependency_reasonableness(
                detected_programs, program_dependencies, language
            )
            
            errors.extend(dependency_validation['errors'])
            warnings.extend(dependency_validation['warnings'])
            details['dependency_validation'] = dependency_validation
            
            is_valid = len(errors) == 0
            
            self.logger.debug(
                f"Validated {file_path}: accuracy={accuracy_metrics['overall_accuracy']:.2f}, "
                f"valid={is_valid}, programs={len(detected_programs)}"
            )
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                details=details
            )
        
        except Exception as e:
            self.logger.error(f"Error during accuracy validation of {file_path}: {str(e)}")
            self.validation_stats['files_failed'] += 1
            
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                details={'exception': str(e)}
            )
    
    def _calculate_accuracy_metrics(self,
                                  source_code: str,
                                  programs: List[ProgramBoundary],
                                  dependencies: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate accuracy metrics for program detection."""
        total_lines = len(source_code.splitlines())
        
        # Coverage accuracy (how much of the file is covered by programs)
        covered_lines = set()
        for program in programs:
            for line_num in range(program.start_line, program.end_line + 1):
                covered_lines.add(line_num)
        
        coverage_accuracy = len(covered_lines) / max(total_lines, 1)
        
        # Boundary accuracy (how reasonable are the boundaries)
        boundary_accuracy = 1.0
        if programs:
            # Check for overlaps (reduces accuracy)
            overlaps = 0
            for i, prog1 in enumerate(programs):
                for prog2 in programs[i+1:]:
                    if prog1.overlaps_with(prog2):
                        overlaps += 1
            
            # Penalize overlaps
            boundary_accuracy = max(0.0, 1.0 - (overlaps * 0.2))
        
        # Dependency accuracy (basic check for reasonable dependency counts)
        dependency_accuracy = 1.0
        if dependencies:
            total_deps = sum(len(deps) for deps in dependencies.values())
            avg_deps_per_program = total_deps / len(dependencies)
            
            # Reasonable range is 0-20 dependencies per program
            if avg_deps_per_program > 20:
                dependency_accuracy = max(0.5, 1.0 - ((avg_deps_per_program - 20) * 0.02))
        
        # Overall accuracy is weighted average
        overall_accuracy = (
            coverage_accuracy * 0.4 +
            boundary_accuracy * 0.4 +
            dependency_accuracy * 0.2
        )
        
        return {
            'coverage_accuracy': coverage_accuracy,
            'boundary_accuracy': boundary_accuracy,
            'dependency_accuracy': dependency_accuracy,
            'overall_accuracy': overall_accuracy
        }
    
    def _validate_boundary_reasonableness(self,
                                        source_code: str,
                                        programs: List[ProgramBoundary],
                                        language: str) -> Dict[str, List[str]]:
        """Validate that program boundaries are reasonable for the language."""
        errors = []
        warnings = []
        
        total_lines = len(source_code.splitlines())
        
        for program in programs:
            # Check minimum program size
            program_size = program.end_line - program.start_line + 1
            
            if program_size < 5:
                warnings.append(f"Program '{program.program_name}' is very small ({program_size} lines)")
            elif program_size > total_lines * 0.8:
                warnings.append(f"Program '{program.program_name}' covers most of the file ({program_size}/{total_lines} lines)")
            
            # Language-specific validation
            if language.upper() == 'RPG':
                # RPG programs should have reasonable names
                if not program.program_name.replace('_', '').replace('-', '').isalnum():
                    warnings.append(f"RPG program name '{program.program_name}' contains unusual characters")
            
            elif language.upper() == 'ASM':
                # Assembler CSECTs should follow naming conventions
                if program.program_type == ProgramType.CSECT and len(program.program_name) > 8:
                    warnings.append(f"Assembler CSECT name '{program.program_name}' exceeds 8 characters")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_dependency_reasonableness(self,
                                          programs: List[ProgramBoundary],
                                          dependencies: Dict[str, List[str]],
                                          language: str) -> Dict[str, List[str]]:
        """Validate that dependencies are reasonable for the language."""
        errors = []
        warnings = []
        
        program_names = {prog.program_name for prog in programs}
        
        for program_name, deps in dependencies.items():
            if program_name not in program_names:
                errors.append(f"Dependencies found for unknown program: {program_name}")
                continue
            
            # Check for self-references
            if program_name in deps:
                warnings.append(f"Program '{program_name}' has self-reference")
            
            # Check dependency count
            if len(deps) > 50:
                warnings.append(f"Program '{program_name}' has unusually high dependency count: {len(deps)}")
            
            # Language-specific checks
            if language.upper() == 'NATURAL':
                # Natural programs shouldn't call system functions directly
                system_calls = [dep for dep in deps if dep.startswith('SYS')]
                if system_calls:
                    warnings.append(f"Natural program '{program_name}' has system calls: {system_calls}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation statistics."""
        avg_accuracy = 0.0
        if self.validation_stats['files_validated'] > 0:
            avg_accuracy = self.validation_stats['total_accuracy_score'] / self.validation_stats['files_validated']
        
        return {
            'files_validated': self.validation_stats['files_validated'],
            'files_passed': self.validation_stats['files_passed'],
            'files_failed': self.validation_stats['files_failed'],
            'pass_rate': self.validation_stats['files_passed'] / max(self.validation_stats['files_validated'], 1),
            'average_accuracy': avg_accuracy,
            'accuracy_threshold': self.accuracy_threshold
        }


# Factory function for creating error handling components
def create_error_handler(database, 
                        log_file: Optional[str] = None,
                        accuracy_threshold: float = 0.8) -> Tuple[ProgramBoundaryErrorRecovery, 
                                                                TransactionManager,
                                                                ProgramAnalysisLogger,
                                                                ProgramBoundaryAccuracyValidator]:
    """
    Create a complete error handling suite for program-level analysis.
    
    Args:
        database: Database adapter instance
        log_file: Optional path to log file
        accuracy_threshold: Minimum accuracy threshold for validation
        
    Returns:
        Tuple of (error_recovery, transaction_manager, logger, validator)
    """
    # Create logger first
    logger = ProgramAnalysisLogger(log_file=log_file)
    
    # Create components with shared logger
    error_recovery = ProgramBoundaryErrorRecovery(logger.logger)
    transaction_manager = TransactionManager(database, logger.logger)
    validator = ProgramBoundaryAccuracyValidator(logger.logger, accuracy_threshold)
    
    return error_recovery, transaction_manager, logger, validator