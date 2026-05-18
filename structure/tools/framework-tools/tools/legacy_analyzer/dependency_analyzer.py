"""
Dependency Analyzer - Pure dependency extraction without database operations.

This class is responsible for:
1. Analyzing source files for dependencies
2. Extracting program boundaries
3. Returning structured dependency results
4. NO database operations (separation of concerns)
"""

import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

from .parsers import (
    COBOLDependencyParser, 
    JCLDependencyParser, 
    PLIDependencyParser,
    NaturalDependencyParser,
    RPGDependencyParser,
    REXXDependencyParser,
    ASMDependencyParser
)
from .models.artifact import Artifact
from .models.dependency import Dependency, DependencyType
from .models.program_boundary import ProgramBoundary
from .analysis.program_boundary_detector import ProgramBoundaryDetectorFactory
from .analysis.mixed_content_detector import MixedContentDetector


class DependencyAnalysisResult:
    """Container for dependency analysis results."""
    
    def __init__(self, artifact: Artifact):
        self.artifact = artifact
        self.file_level_dependencies: Dict[str, List[str]] = {}
        self.program_boundaries: List[ProgramBoundary] = []
        self.program_level_dependencies: Dict[str, Dict[str, List[str]]] = {}
        self.complexity_metrics: Optional[Dict] = None
        self.analysis_errors: List[str] = []
        self.analysis_warnings: List[str] = []
        self.store_program_boundaries: bool = False  # NEW - flag to store program boundaries
        self.copybook_analysis_results: List = []  # NEW - copybook analysis results
    
    @property
    def has_dependencies(self) -> bool:
        """Check if any dependencies were found."""
        file_deps = any(len(deps) > 0 for deps in self.file_level_dependencies.values() 
                       if isinstance(deps, list))
        prog_deps = bool(self.program_level_dependencies)
        return file_deps or prog_deps
    
    @property
    def has_program_boundaries(self) -> bool:
        """Check if program boundaries were detected."""
        return len(self.program_boundaries) > 0
    
    @property
    def dependency_count(self) -> int:
        """Get total dependency count."""
        if self.program_level_dependencies:
            # Count program-level dependencies
            total = 0
            for prog_deps in self.program_level_dependencies.values():
                if isinstance(prog_deps, dict):
                    for dep_list in prog_deps.values():
                        if isinstance(dep_list, list):
                            total += len(dep_list)
                elif isinstance(prog_deps, list):
                    total += len(prog_deps)
            return total
        else:
            # Count file-level dependencies
            return sum(len(deps) for deps in self.file_level_dependencies.values() 
                      if isinstance(deps, list))


class DependencyAnalyzer:
    """Pure dependency extraction without database operations."""
    
    def __init__(self):
        """Initialize dependency analyzer."""
        # Register language-specific parsers
        self.parsers = {
            'COBOL': COBOLDependencyParser(),
            'PLI': PLIDependencyParser(),
            'JCL': JCLDependencyParser(),
            'NATURAL': NaturalDependencyParser(),
            'RPG': RPGDependencyParser(),
            'REXX': REXXDependencyParser(),
            'ASM': ASMDependencyParser()
        }
        
        # Initialize mixed content detector
        self.mixed_content_detector = MixedContentDetector()
        
        self.stats = defaultdict(int)
    
    def analyze_artifact(self, artifact: Artifact, 
                        calculate_complexity: bool = False,
                        enable_program_level: bool = True) -> DependencyAnalysisResult:
        """
        Analyze a single artifact for dependencies.
        
        Args:
            artifact: Artifact to analyze
            calculate_complexity: Whether to calculate complexity metrics
            enable_program_level: Whether to detect program boundaries
            
        Returns:
            DependencyAnalysisResult with all extracted information
        """
        result = DependencyAnalysisResult(artifact)
        
        try:
            # Read source code
            source_code = self._read_source_file(artifact.file_path)
            if not source_code:
                result.analysis_errors.append("Could not read source file")
                return result
            
            # Check for mixed content first
            if enable_program_level and self.mixed_content_detector.is_mixed_content_file(source_code):
                try:
                    self._analyze_mixed_content_directly(artifact, source_code, result, calculate_complexity)
                except Exception as e:
                    result.analysis_errors.append(f"Mixed content analysis failed: {str(e)}")
                    return result
            else:
                # Get appropriate parser for single-language files
                parser = self.parsers.get(artifact.language.upper())
                if not parser:
                    result.analysis_errors.append(f"No parser available for language: {artifact.language}")
                    return result
                
                # Try program-level analysis first if enabled
                if enable_program_level and self._supports_program_level_analysis(artifact.language):
                    try:
                        self._analyze_with_program_detection(artifact, source_code, parser, result, calculate_complexity)
                    except Exception as e:
                        result.analysis_warnings.append(f"Program-level analysis failed: {str(e)}")
                        # Fall back to file-level analysis
                        enable_program_level = False
                
                # Fall back to file-level analysis if needed
                if not enable_program_level or not result.has_program_boundaries:
                    self._analyze_file_level(source_code, parser, result, calculate_complexity)
            
            self.stats['files_analyzed'] += 1
            self.stats[f'{artifact.language.lower()}_files'] += 1
            
        except Exception as e:
            result.analysis_errors.append(f"Analysis failed: {str(e)}")
            self.stats['analysis_errors'] += 1
        
        return result
    
    def analyze_multiple_artifacts(self, artifacts: List[Artifact],
                                 calculate_complexity: bool = False,
                                 enable_program_level: bool = True) -> List[DependencyAnalysisResult]:
        """
        Analyze multiple artifacts for dependencies.
        
        Args:
            artifacts: List of artifacts to analyze
            calculate_complexity: Whether to calculate complexity metrics
            enable_program_level: Whether to detect program boundaries
            
        Returns:
            List of DependencyAnalysisResult objects
        """
        results = []
        
        print(f"\n=== Phase 5: Analyzing Dependencies ===")
        print(f"Analyzing {len(artifacts)} artifacts...")
        
        processed = 0
        for artifact in artifacts:
            try:
                result = self.analyze_artifact(artifact, calculate_complexity, enable_program_level)
                results.append(result)
                
                processed += 1
                if processed % 50 == 0:
                    print(f"  Analyzed {processed}/{len(artifacts)} artifacts...")
                    
            except Exception as e:
                print(f"  ⚠ Warning: Error analyzing {artifact.file_path}: {str(e)}")
                # Create error result
                error_result = DependencyAnalysisResult(artifact)
                error_result.analysis_errors.append(str(e))
                results.append(error_result)
                self.stats['analysis_errors'] += 1
        
        # Print summary
        successful = len([r for r in results if not r.analysis_errors])
        with_deps = len([r for r in results if r.has_dependencies])
        
        print(f"✓ Analyzed {processed} artifacts")
        print(f"✓ Successful analyses: {successful}")
        print(f"✓ Artifacts with dependencies: {with_deps}")
        if self.stats['analysis_errors'] > 0:
            print(f"⚠ Analysis errors: {self.stats['analysis_errors']}")
        
        return results
    
    def get_analysis_stats(self) -> Dict[str, int]:
        """Get analysis statistics."""
        return dict(self.stats)
    
    def _read_source_file(self, file_path: str) -> Optional[str]:
        """Read source file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def _supports_program_level_analysis(self, language: str) -> bool:
        """Check if language supports program-level analysis."""
        return language.upper() in ['RPG', 'ASM', 'ASSEMBLER', 'NATURAL', 'REXX']
    
    def _analyze_with_program_detection(self, artifact: Artifact, source_code: str, 
                                      parser, result: DependencyAnalysisResult,
                                      calculate_complexity: bool) -> None:
        """Analyze with program boundary detection."""
        
        # First, check if this is a mixed content file (e.g., PDS format)
        if self.mixed_content_detector.is_mixed_content_file(source_code):
            # Use mixed content detector for PDS-style files
            result.program_boundaries = self.mixed_content_detector.detect_boundaries(
                artifact.file_path, source_code
            )
            
            if result.program_boundaries:
                # Extract dependencies for each detected program
                result.program_level_dependencies = self._extract_mixed_content_dependencies(
                    source_code, result.program_boundaries
                )
                # Mark this as mixed content analysis
                result.analysis_warnings.append("Mixed content detected - using multi-language analysis")
                self.stats['mixed_content_files'] += 1
            else:
                result.analysis_warnings.append("Mixed content format detected but no programs found")
        
        # If no mixed content or mixed content detection failed, use language-specific detection
        if not result.program_boundaries:
            # Extract dependencies for each program
            if hasattr(parser, 'parse_with_program_detection'):
                # Use enhanced parser method - this has the most sophisticated program detection
                parse_result = parser.parse_with_program_detection(source_code, artifact.file_path)
                
                # Use program boundaries from parser if available (more accurate than generic detector)
                if hasattr(parse_result, 'programs') and parse_result.programs:
                    result.program_boundaries = parse_result.programs
                else:
                    # Fallback to generic detector if parser doesn't provide program boundaries
                    detector = ProgramBoundaryDetectorFactory.create_detector(artifact.language)
                    if detector:
                        result.program_boundaries = detector.detect_boundaries(source_code, artifact.file_path)
                    else:
                        result.program_boundaries = []
                
                # Extract dependencies from parser result
                if hasattr(parse_result, 'dependencies'):
                    result.program_level_dependencies = parse_result.dependencies
                elif isinstance(parse_result, dict) and 'program_dependencies' in parse_result:
                    result.program_level_dependencies = parse_result['program_dependencies']
                else:
                    result.program_level_dependencies = {}
            else:
                # Fallback: Use generic detector and manual dependency extraction
                detector = ProgramBoundaryDetectorFactory.create_detector(artifact.language)
                if not detector:
                    raise ValueError(f"No program boundary detector for {artifact.language}")
                
                # Detect program boundaries using generic detector
                programs = detector.detect_boundaries(source_code, artifact.file_path)
                result.program_boundaries = programs
                
                if not programs:
                    return  # No programs detected
                
                # Extract dependencies manually
                result.program_level_dependencies = self._extract_program_level_dependencies(
                    source_code, programs, parser
                )
        
        if not result.program_boundaries:
            return  # No programs detected
        
        # Aggregate file-level dependencies for backward compatibility
        aggregated_deps = {}
        for prog_deps in result.program_level_dependencies.values():
            for dep_type, dep_list in prog_deps.items():
                if isinstance(dep_list, list):
                    if dep_type not in aggregated_deps:
                        aggregated_deps[dep_type] = []
                    aggregated_deps[dep_type].extend(dep_list)
        
        # Remove duplicates
        for dep_type, dep_list in aggregated_deps.items():
            aggregated_deps[dep_type] = list(set(dep_list))
        
        result.file_level_dependencies = aggregated_deps
        
        # Calculate complexity if requested
        if calculate_complexity and hasattr(parser, 'parse_with_complexity'):
            complexity_result = parser.parse_with_complexity(source_code)
            if 'complexity' in complexity_result:
                result.complexity_metrics = complexity_result['complexity']
    
    def _analyze_file_level(self, source_code: str, parser, 
                          result: DependencyAnalysisResult,
                          calculate_complexity: bool) -> None:
        """Analyze at file level."""
        if calculate_complexity and hasattr(parser, 'parse_with_complexity'):
            parse_result = parser.parse_with_complexity(source_code)
            result.file_level_dependencies = parse_result.get('dependencies', {})
            result.complexity_metrics = parse_result.get('complexity')
        else:
            result.file_level_dependencies = parser.parse(source_code)
    
    def _extract_program_level_dependencies(self, source_code: str,
                                          programs: List[ProgramBoundary],
                                          parser) -> Dict[str, Dict[str, List[str]]]:
        """Extract dependencies for each program using line-based analysis."""
        program_dependencies = {}
        lines = source_code.splitlines()
        
        for program in programs:
            # Extract code for this program
            start_idx = max(0, program.start_line - 1)
            end_idx = min(len(lines), program.end_line)
            program_code = '\n'.join(lines[start_idx:end_idx])
            
            # Parse dependencies for this program's code
            try:
                prog_deps = parser.parse(program_code)
                program_dependencies[program.program_name] = prog_deps
            except Exception as e:
                # Log warning but continue
                program_dependencies[program.program_name] = {}
        
        return program_dependencies
    
    def _extract_mixed_content_dependencies(self, source_code: str,
                                          programs: List[ProgramBoundary]) -> Dict[str, Dict[str, List[str]]]:
        """Extract dependencies for each program in mixed content using appropriate parsers."""
        program_dependencies = {}
        lines = source_code.splitlines()
        
        for program in programs:
            # Extract code for this program
            start_idx = max(0, program.start_line - 1)
            end_idx = min(len(lines), program.end_line)
            program_code = '\n'.join(lines[start_idx:end_idx])
            
            # Get appropriate parser for this program's language
            parser = self.parsers.get(program.language.upper())
            if parser:
                try:
                    prog_deps = parser.parse(program_code)
                    program_dependencies[program.program_name] = prog_deps
                except Exception as e:
                    # Log warning but continue
                    program_dependencies[program.program_name] = {}
                    self.stats['mixed_content_parse_errors'] += 1
            else:
                # No parser available for this language
                program_dependencies[program.program_name] = {}
                self.stats['unsupported_languages'] += 1
        
        return program_dependencies
    
    def _analyze_mixed_content_directly(self, artifact: Artifact, source_code: str,
                                      result: DependencyAnalysisResult,
                                      calculate_complexity: bool) -> None:
        """Analyze mixed content files directly using the mixed content detector."""
        # Use mixed content detector for PDS-style files
        result.program_boundaries = self.mixed_content_detector.detect_boundaries(
            artifact.file_path, source_code
        )
        
        if result.program_boundaries:
            # Extract dependencies for each detected program
            result.program_level_dependencies = self._extract_mixed_content_dependencies(
                source_code, result.program_boundaries
            )
            # Mark this as mixed content analysis
            result.analysis_warnings.append("Mixed content detected - using multi-language analysis")
            self.stats['mixed_content_files'] += 1
        else:
            result.analysis_warnings.append("Mixed content format detected but no programs found")