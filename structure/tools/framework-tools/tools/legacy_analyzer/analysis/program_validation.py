"""Program-level validation and statistics framework.

This module provides comprehensive validation for program boundary detection,
dependency tracking accuracy, and performance monitoring for program-level
analysis operations.
"""

import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import sqlite3
from pathlib import Path

from ..models.program_boundary import ProgramBoundary, ProgramParseResult
from ..models.dependency import Dependency
from .program_boundary_detector import ProgramBoundaryDetectorFactory


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccuracyMetrics:
    """Metrics for program detection and dependency tracking accuracy."""
    total_programs_detected: int = 0
    valid_programs: int = 0
    invalid_programs: int = 0
    programs_with_warnings: int = 0
    
    total_dependencies: int = 0
    valid_dependencies: int = 0
    invalid_dependencies: int = 0
    
    boundary_completeness_score: float = 0.0
    dependency_accuracy_score: float = 0.0
    overall_accuracy_score: float = 0.0
    
    def calculate_scores(self):
        """Calculate accuracy scores based on collected metrics."""
        if self.total_programs_detected > 0:
            self.boundary_completeness_score = self.valid_programs / self.total_programs_detected
        
        if self.total_dependencies > 0:
            self.dependency_accuracy_score = self.valid_dependencies / self.total_dependencies
        
        # Overall accuracy is weighted average of boundary and dependency accuracy
        if self.total_programs_detected > 0 and self.total_dependencies > 0:
            self.overall_accuracy_score = (
                (self.boundary_completeness_score * 0.6) + 
                (self.dependency_accuracy_score * 0.4)
            )
        elif self.total_programs_detected > 0:
            self.overall_accuracy_score = self.boundary_completeness_score
        elif self.total_dependencies > 0:
            self.overall_accuracy_score = self.dependency_accuracy_score


@dataclass
class PerformanceMetrics:
    """Performance metrics for program-level analysis operations."""
    operation_name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_seconds: float = 0.0
    
    files_processed: int = 0
    programs_detected: int = 0
    dependencies_extracted: int = 0
    
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    def calculate_duration(self):
        """Calculate operation duration."""
        if self.end_time > self.start_time:
            self.duration_seconds = self.end_time - self.start_time
    
    def get_throughput_metrics(self) -> Dict[str, float]:
        """Calculate throughput metrics."""
        if self.duration_seconds <= 0:
            return {}
        
        return {
            'files_per_second': self.files_processed / self.duration_seconds,
            'programs_per_second': self.programs_detected / self.duration_seconds,
            'dependencies_per_second': self.dependencies_extracted / self.duration_seconds
        }


@dataclass
class ValidationReport:
    """Comprehensive validation report for program-level dependency tracking."""
    file_path: str
    language: str
    
    boundary_validation: ValidationResult
    dependency_validation: ValidationResult
    accuracy_metrics: AccuracyMetrics
    performance_metrics: PerformanceMetrics
    
    programs_detected: List[ProgramBoundary] = field(default_factory=list)
    file_level_comparison: Dict[str, Any] = field(default_factory=dict)
    
    timestamp: float = field(default_factory=time.time)


class ProgramBoundaryValidator:
    """Validator for program boundary detection completeness and accuracy."""
    
    def __init__(self):
        """Initialize the program boundary validator."""
        self.detector_factory = ProgramBoundaryDetectorFactory()
    
    def validate_boundary_completeness(self, 
                                     source_code: str, 
                                     programs: List[ProgramBoundary],
                                     language: str) -> ValidationResult:
        """
        Validate that program boundaries cover all source code lines completely.
        
        Ensures that:
        1. All source code lines are assigned to exactly one program or marked as non-executable
        2. No gaps exist between program boundaries
        3. No overlaps exist between program boundaries
        
        Args:
            source_code: The source code content
            programs: List of detected program boundaries
            language: Programming language
            
        Returns:
            ValidationResult with completeness validation details
        """
        errors = []
        warnings = []
        details = {}
        
        if not programs:
            return ValidationResult(
                is_valid=False,
                errors=["No programs detected in source code"],
                details={'total_lines': len(source_code.splitlines())}
            )
        
        total_lines = len(source_code.splitlines())
        covered_lines = set()
        
        # Check each program boundary
        for i, program in enumerate(programs):
            # Validate boundary values
            if program.start_line < 1:
                errors.append(f"Program '{program.program_name}' has invalid start_line: {program.start_line}")
            
            if program.end_line < program.start_line:
                errors.append(f"Program '{program.program_name}' has end_line before start_line")
            
            if program.end_line > total_lines:
                warnings.append(f"Program '{program.program_name}' end_line ({program.end_line}) exceeds total lines ({total_lines})")
                program.end_line = total_lines  # Adjust for validation
            
            # Track covered lines
            for line_num in range(program.start_line, program.end_line + 1):
                if line_num in covered_lines:
                    errors.append(f"Line {line_num} is covered by multiple programs")
                else:
                    covered_lines.add(line_num)
        
        # Check for gaps
        all_lines = set(range(1, total_lines + 1))
        uncovered_lines = all_lines - covered_lines
        
        if uncovered_lines:
            # Analyze uncovered lines to see if they're non-executable
            non_executable_lines = self._identify_non_executable_lines(source_code, uncovered_lines, language)
            executable_gaps = uncovered_lines - non_executable_lines
            
            if executable_gaps:
                errors.append(f"Executable code lines not covered by any program: {sorted(executable_gaps)}")
            
            if non_executable_lines:
                details['non_executable_lines'] = sorted(non_executable_lines)
        
        # Check for overlaps
        overlap_errors = self._check_program_overlaps(programs)
        errors.extend(overlap_errors)
        
        # Calculate coverage statistics
        coverage_percentage = (len(covered_lines) / total_lines) * 100 if total_lines > 0 else 0
        details.update({
            'total_lines': total_lines,
            'covered_lines': len(covered_lines),
            'uncovered_lines': len(uncovered_lines),
            'coverage_percentage': coverage_percentage,
            'programs_count': len(programs)
        })
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, details=details)
    
    def _identify_non_executable_lines(self, source_code: str, line_numbers: Set[int], language: str) -> Set[int]:
        """
        Identify which lines contain non-executable content (comments, blank lines, etc.).
        
        Args:
            source_code: The source code content
            line_numbers: Set of line numbers to check
            language: Programming language
            
        Returns:
            Set of line numbers that contain non-executable content
        """
        non_executable = set()
        lines = source_code.splitlines()
        
        # Language-specific comment patterns
        comment_patterns = {
            'RPG': ['*', '//', 'C*'],
            'ASM': ['*', ';'],
            'ASSEMBLER': ['*', ';'],
            'NATURAL': ['*', '/*'],
            'REXX': ['/*', '*/', '--'],
            'COBOL': ['*', '/', 'C*'],
            'PLI': ['/*', '*/', '--']
        }
        
        patterns = comment_patterns.get(language.upper(), ['*', '//', '/*'])
        
        for line_num in line_numbers:
            if 1 <= line_num <= len(lines):
                line = lines[line_num - 1].strip()
                
                # Check if line is blank
                if not line:
                    non_executable.add(line_num)
                    continue
                
                # Check if line is a comment
                is_comment = False
                for pattern in patterns:
                    if line.startswith(pattern):
                        is_comment = True
                        break
                
                if is_comment:
                    non_executable.add(line_num)
        
        return non_executable
    
    def _check_program_overlaps(self, programs: List[ProgramBoundary]) -> List[str]:
        """Check for overlapping program boundaries."""
        errors = []
        
        for i, prog1 in enumerate(programs):
            for j, prog2 in enumerate(programs[i+1:], i+1):
                if prog1.overlaps_with(prog2):
                    errors.append(
                        f"Programs '{prog1.program_name}' and '{prog2.program_name}' overlap: "
                        f"lines {prog1.start_line}-{prog1.end_line} vs {prog2.start_line}-{prog2.end_line}"
                    )
        
        return errors


class DependencyAccuracyValidator:
    """Validator for program-level dependency tracking accuracy."""
    
    def __init__(self, database_path: str):
        """
        Initialize the dependency accuracy validator.
        
        Args:
            database_path: Path to the SQLite database containing dependency data
        """
        self.database_path = database_path
    
    def validate_dependency_accuracy(self, 
                                   programs: List[ProgramBoundary],
                                   program_dependencies: Dict[str, List[str]]) -> ValidationResult:
        """
        Validate the accuracy of program-level dependency tracking.
        
        Args:
            programs: List of detected program boundaries
            program_dependencies: Dictionary mapping program names to their dependencies
            
        Returns:
            ValidationResult with dependency validation details
        """
        errors = []
        warnings = []
        details = {}
        
        # Check referential integrity
        program_names = {prog.program_name for prog in programs}
        
        total_dependencies = 0
        valid_dependencies = 0
        invalid_dependencies = 0
        
        for source_program, dependencies in program_dependencies.items():
            if source_program not in program_names:
                errors.append(f"Source program '{source_program}' not found in detected programs")
                continue
            
            for dependency in dependencies:
                total_dependencies += 1
                
                # Check if dependency exists in inventory
                if self._dependency_exists_in_inventory(dependency):
                    valid_dependencies += 1
                else:
                    invalid_dependencies += 1
                    warnings.append(f"Dependency '{dependency}' from '{source_program}' not found in inventory")
        
        # Validate call relationships are technically valid
        technical_validation_errors = self._validate_technical_relationships(programs, program_dependencies)
        errors.extend(technical_validation_errors)
        
        details.update({
            'total_dependencies': total_dependencies,
            'valid_dependencies': valid_dependencies,
            'invalid_dependencies': invalid_dependencies,
            'dependency_accuracy': valid_dependencies / max(total_dependencies, 1)
        })
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, details=details)
    
    def _dependency_exists_in_inventory(self, dependency_name: str) -> bool:
        """Check if a dependency exists in the inventory database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM inventory 
                    WHERE artifact_name = ? OR program_within_file = ?
                """, (dependency_name, dependency_name))
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error:
            return False  # Assume invalid if we can't check
    
    def _validate_technical_relationships(self, 
                                        programs: List[ProgramBoundary],
                                        program_dependencies: Dict[str, List[str]]) -> List[str]:
        """Validate that call relationships are technically valid for the source language."""
        errors = []
        
        # Language-specific validation rules
        for program in programs:
            if program.program_name in program_dependencies:
                dependencies = program_dependencies[program.program_name]
                
                # Check for self-references (usually invalid)
                if program.program_name in dependencies:
                    errors.append(f"Program '{program.program_name}' has self-reference dependency")
                
                # Language-specific checks
                if program.language.upper() == 'RPG':
                    # RPG programs typically can't call certain system functions directly
                    invalid_rpg_calls = [dep for dep in dependencies if dep.startswith('SYS') and len(dep) > 8]
                    for invalid_call in invalid_rpg_calls:
                        errors.append(f"RPG program '{program.program_name}' has invalid system call: {invalid_call}")
        
        return errors


class ProgramLevelStatisticsGenerator:
    """Generator for program-level dependency tracking statistics and reports."""
    
    def __init__(self, database_path: str):
        """
        Initialize the statistics generator.
        
        Args:
            database_path: Path to the SQLite database containing analysis data
        """
        self.database_path = database_path
    
    def generate_accuracy_report(self, validation_results: List[ValidationReport]) -> Dict[str, Any]:
        """
        Generate comprehensive accuracy report for program-level dependency tracking.
        
        Args:
            validation_results: List of validation results from analyzed files
            
        Returns:
            Dictionary containing accuracy statistics and comparisons
        """
        if not validation_results:
            return {'error': 'No validation results provided'}
        
        # Aggregate metrics
        total_files = len(validation_results)
        total_programs = sum(len(result.programs_detected) for result in validation_results)
        
        # Accuracy metrics aggregation
        boundary_scores = [result.accuracy_metrics.boundary_completeness_score for result in validation_results]
        dependency_scores = [result.accuracy_metrics.dependency_accuracy_score for result in validation_results]
        overall_scores = [result.accuracy_metrics.overall_accuracy_score for result in validation_results]
        
        # Performance metrics aggregation
        total_duration = sum(result.performance_metrics.duration_seconds for result in validation_results)
        total_dependencies = sum(result.accuracy_metrics.total_dependencies for result in validation_results)
        
        # Language breakdown
        language_stats = defaultdict(lambda: {'files': 0, 'programs': 0, 'avg_accuracy': 0.0})
        for result in validation_results:
            lang = result.language
            language_stats[lang]['files'] += 1
            language_stats[lang]['programs'] += len(result.programs_detected)
            language_stats[lang]['avg_accuracy'] += result.accuracy_metrics.overall_accuracy_score
        
        # Calculate averages for languages
        for lang_data in language_stats.values():
            if lang_data['files'] > 0:
                lang_data['avg_accuracy'] /= lang_data['files']
        
        # File-level vs program-level comparison
        file_vs_program_comparison = self._generate_file_vs_program_comparison(validation_results)
        
        report = {
            'summary': {
                'total_files_analyzed': total_files,
                'total_programs_detected': total_programs,
                'average_programs_per_file': total_programs / max(total_files, 1),
                'total_analysis_duration_seconds': total_duration,
                'total_dependencies_tracked': total_dependencies
            },
            'accuracy_metrics': {
                'boundary_completeness': {
                    'average': sum(boundary_scores) / max(len(boundary_scores), 1),
                    'minimum': min(boundary_scores) if boundary_scores else 0,
                    'maximum': max(boundary_scores) if boundary_scores else 0
                },
                'dependency_accuracy': {
                    'average': sum(dependency_scores) / max(len(dependency_scores), 1),
                    'minimum': min(dependency_scores) if dependency_scores else 0,
                    'maximum': max(dependency_scores) if dependency_scores else 0
                },
                'overall_accuracy': {
                    'average': sum(overall_scores) / max(len(overall_scores), 1),
                    'minimum': min(overall_scores) if overall_scores else 0,
                    'maximum': max(overall_scores) if overall_scores else 0
                }
            },
            'language_breakdown': dict(language_stats),
            'file_vs_program_comparison': file_vs_program_comparison,
            'performance_summary': {
                'average_processing_time_per_file': total_duration / max(total_files, 1),
                'programs_detected_per_second': total_programs / max(total_duration, 1),
                'dependencies_tracked_per_second': total_dependencies / max(total_duration, 1)
            }
        }
        
        return report
    
    def _generate_file_vs_program_comparison(self, validation_results: List[ValidationReport]) -> Dict[str, Any]:
        """Generate comparison between file-level and program-level dependency counts."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get file-level dependency counts
                cursor.execute("""
                    SELECT COUNT(*) FROM dependencies 
                    WHERE source_artifact_name NOT LIKE '%.%'  -- Assume file-level if no program separator
                """)
                file_level_deps = cursor.fetchone()[0]
                
                # Get program-level dependency counts
                cursor.execute("""
                    SELECT COUNT(*) FROM dependencies 
                    WHERE source_artifact_name LIKE '%.%'  -- Assume program-level if has separator
                """)
                program_level_deps = cursor.fetchone()[0]
                
                # Calculate improvement metrics
                total_deps = file_level_deps + program_level_deps
                
                return {
                    'file_level_dependencies': file_level_deps,
                    'program_level_dependencies': program_level_deps,
                    'total_dependencies': total_deps,
                    'program_level_percentage': (program_level_deps / max(total_deps, 1)) * 100,
                    'granularity_improvement_factor': program_level_deps / max(file_level_deps, 1)
                }
        
        except sqlite3.Error as e:
            return {'error': f'Database error: {str(e)}'}
    
    def generate_performance_report(self, performance_metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """
        Generate performance analysis report for program-level operations.
        
        Args:
            performance_metrics: List of performance metrics from various operations
            
        Returns:
            Dictionary containing performance statistics and recommendations
        """
        if not performance_metrics:
            return {'error': 'No performance metrics provided'}
        
        # Aggregate performance data
        total_operations = len(performance_metrics)
        total_duration = sum(metric.duration_seconds for metric in performance_metrics)
        total_files = sum(metric.files_processed for metric in performance_metrics)
        total_programs = sum(metric.programs_detected for metric in performance_metrics)
        
        # Calculate throughput metrics
        durations = [metric.duration_seconds for metric in performance_metrics if metric.duration_seconds > 0]
        files_per_second = [metric.files_processed / metric.duration_seconds 
                           for metric in performance_metrics if metric.duration_seconds > 0]
        programs_per_second = [metric.programs_detected / metric.duration_seconds 
                              for metric in performance_metrics if metric.duration_seconds > 0]
        
        # Operation breakdown
        operation_stats = defaultdict(lambda: {'count': 0, 'total_duration': 0, 'avg_duration': 0})
        for metric in performance_metrics:
            op_name = metric.operation_name
            operation_stats[op_name]['count'] += 1
            operation_stats[op_name]['total_duration'] += metric.duration_seconds
        
        # Calculate averages
        for op_data in operation_stats.values():
            if op_data['count'] > 0:
                op_data['avg_duration'] = op_data['total_duration'] / op_data['count']
        
        report = {
            'summary': {
                'total_operations': total_operations,
                'total_duration_seconds': total_duration,
                'total_files_processed': total_files,
                'total_programs_detected': total_programs,
                'average_duration_per_operation': total_duration / max(total_operations, 1)
            },
            'throughput_metrics': {
                'average_files_per_second': sum(files_per_second) / max(len(files_per_second), 1),
                'average_programs_per_second': sum(programs_per_second) / max(len(programs_per_second), 1),
                'peak_files_per_second': max(files_per_second) if files_per_second else 0,
                'peak_programs_per_second': max(programs_per_second) if programs_per_second else 0
            },
            'operation_breakdown': dict(operation_stats),
            'performance_recommendations': self._generate_performance_recommendations(performance_metrics)
        }
        
        return report
    
    def _generate_performance_recommendations(self, performance_metrics: List[PerformanceMetrics]) -> List[str]:
        """Generate performance improvement recommendations based on metrics."""
        recommendations = []
        
        # Analyze average processing times
        durations = [metric.duration_seconds for metric in performance_metrics if metric.duration_seconds > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            if avg_duration > 5.0:  # More than 5 seconds average
                recommendations.append("Consider implementing parallel processing for large files")
            
            if max_duration > 30.0:  # More than 30 seconds for any single operation
                recommendations.append("Implement streaming processing for very large files")
        
        # Analyze throughput
        files_processed = [metric.files_processed for metric in performance_metrics]
        if files_processed and max(files_processed) > 100:
            recommendations.append("Consider batch processing optimizations for large file sets")
        
        # Memory usage recommendations (if available)
        memory_usage = [metric.memory_usage_mb for metric in performance_metrics 
                       if metric.memory_usage_mb is not None]
        if memory_usage and max(memory_usage) > 1000:  # More than 1GB
            recommendations.append("Implement memory-efficient processing for large codebases")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges")
        
        return recommendations


class PerformanceMonitor:
    """Monitor for tracking performance of program-level analysis operations."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.active_operations: Dict[str, PerformanceMetrics] = {}
    
    def start_operation(self, operation_name: str) -> str:
        """
        Start monitoring a new operation.
        
        Args:
            operation_name: Name of the operation to monitor
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        self.active_operations[operation_id] = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time()
        )
        
        return operation_id
    
    def update_operation(self, operation_id: str, **kwargs):
        """
        Update metrics for an active operation.
        
        Args:
            operation_id: ID of the operation to update
            **kwargs: Metrics to update (files_processed, programs_detected, etc.)
        """
        if operation_id in self.active_operations:
            metrics = self.active_operations[operation_id]
            
            for key, value in kwargs.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
    
    def end_operation(self, operation_id: str) -> PerformanceMetrics:
        """
        End monitoring for an operation and return final metrics.
        
        Args:
            operation_id: ID of the operation to end
            
        Returns:
            Final PerformanceMetrics for the operation
        """
        if operation_id not in self.active_operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        metrics = self.active_operations[operation_id]
        metrics.end_time = time.time()
        metrics.calculate_duration()
        
        # Remove from active operations
        del self.active_operations[operation_id]
        
        return metrics
    
    def get_active_operations(self) -> List[str]:
        """Get list of currently active operation IDs."""
        return list(self.active_operations.keys())


# Factory function for creating validation reports
def create_validation_report(file_path: str, 
                           language: str,
                           source_code: str,
                           programs: List[ProgramBoundary],
                           program_dependencies: Dict[str, List[str]],
                           database_path: str,
                           performance_metrics: PerformanceMetrics) -> ValidationReport:
    """
    Create a comprehensive validation report for a file analysis.
    
    Args:
        file_path: Path to the analyzed file
        language: Programming language
        source_code: Source code content
        programs: Detected program boundaries
        program_dependencies: Program-level dependencies
        database_path: Path to the analysis database
        performance_metrics: Performance metrics for the analysis
        
    Returns:
        ValidationReport with comprehensive validation results
    """
    # Validate program boundaries
    boundary_validator = ProgramBoundaryValidator()
    boundary_validation = boundary_validator.validate_boundary_completeness(
        source_code, programs, language
    )
    
    # Validate dependencies
    dependency_validator = DependencyAccuracyValidator(database_path)
    dependency_validation = dependency_validator.validate_dependency_accuracy(
        programs, program_dependencies
    )
    
    # Calculate accuracy metrics
    accuracy_metrics = AccuracyMetrics()
    accuracy_metrics.total_programs_detected = len(programs)
    accuracy_metrics.valid_programs = len(programs) - len(boundary_validation.errors)
    accuracy_metrics.invalid_programs = len(boundary_validation.errors)
    accuracy_metrics.programs_with_warnings = len(boundary_validation.warnings)
    
    accuracy_metrics.total_dependencies = sum(len(deps) for deps in program_dependencies.values())
    accuracy_metrics.valid_dependencies = dependency_validation.details.get('valid_dependencies', 0)
    accuracy_metrics.invalid_dependencies = dependency_validation.details.get('invalid_dependencies', 0)
    
    accuracy_metrics.calculate_scores()
    
    return ValidationReport(
        file_path=file_path,
        language=language,
        boundary_validation=boundary_validation,
        dependency_validation=dependency_validation,
        accuracy_metrics=accuracy_metrics,
        performance_metrics=performance_metrics,
        programs_detected=programs
    )