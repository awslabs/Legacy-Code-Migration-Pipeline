"""Program boundary detection framework for multi-program files."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
import re
from ..models.program_boundary import (
    ProgramBoundary, 
    ProgramParseResult, 
    ProgramType
)


class ProgramBoundaryDetector(ABC):
    """Abstract base class for language-specific program boundary detection.
    
    This class provides the interface for detecting individual programs within
    multi-program source files, which is common in mainframe languages like
    RPG, Assembler, Natural, and REXX.
    """
    
    def __init__(self):
        """Initialize the program boundary detector."""
        self.language = self.get_language()
    
    @abstractmethod
    def get_language(self) -> str:
        """Get the language this detector supports."""
        pass
    
    @abstractmethod
    def detect_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect program boundaries within source code.
        
        Args:
            source_code: The source code content to analyze
            file_path: Optional path to the source file
            
        Returns:
            List of ProgramBoundary objects representing detected programs
        """
        pass
    
    def parse_with_program_detection(self, source_code: str, file_path: Optional[str] = None) -> ProgramParseResult:
        """
        Parse source code to detect programs and extract basic dependencies.
        
        Args:
            source_code: The source code content to analyze
            file_path: Optional path to the source file
            
        Returns:
            ProgramParseResult with detected programs and basic dependency info
        """
        programs = self.detect_boundaries(source_code, file_path)
        dependencies = self._extract_basic_dependencies(source_code, programs)
        
        total_lines = len(source_code.splitlines())
        
        result = ProgramParseResult(
            file_path=file_path or "unknown",
            language=self.language,
            programs=programs,
            dependencies=dependencies,
            total_lines=total_lines
        )
        
        return result
    
    def _extract_basic_dependencies(self, source_code: str, programs: List[ProgramBoundary]) -> Dict[str, List[str]]:
        """
        Extract basic dependencies for each detected program.
        
        This is a simple implementation that can be overridden by language-specific detectors.
        
        Args:
            source_code: The source code content
            programs: List of detected program boundaries
            
        Returns:
            Dictionary mapping program names to lists of dependencies
        """
        dependencies = {}
        lines = source_code.splitlines()
        
        for program in programs:
            program_dependencies = []
            
            # Extract dependencies from the program's lines
            for line_num in range(program.start_line - 1, min(program.end_line, len(lines))):
                line = lines[line_num].strip().upper()
                
                # Basic pattern matching for common dependency types
                deps = self._extract_dependencies_from_line(line)
                program_dependencies.extend(deps)
            
            dependencies[program.program_name] = list(set(program_dependencies))  # Remove duplicates
        
        return dependencies
    
    def _extract_dependencies_from_line(self, line: str) -> List[str]:
        """
        Extract dependencies from a single line of code.
        
        This is a basic implementation that can be overridden by language-specific detectors.
        
        Args:
            line: A single line of source code (already stripped and uppercased)
            
        Returns:
            List of dependency names found in the line
        """
        dependencies = []
        
        # Basic patterns for common dependency types
        patterns = [
            r'CALL\s+["\']?([A-Z0-9#@$-]+)["\']?',
            r'COPY\s+([A-Z0-9#@$-]+)',
            r'INCLUDE\s+([A-Z0-9#@$-]+)',
            r'EXEC\s+([A-Z0-9#@$-]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, line)
            dependencies.extend(matches)
        
        return dependencies
    
    def validate_boundaries(self, programs: List[ProgramBoundary]) -> Tuple[bool, List[str]]:
        """
        Validate that program boundaries are complete and non-overlapping.
        
        Args:
            programs: List of program boundaries to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        if not programs:
            return True, []
        
        # Check for overlaps
        for i, prog1 in enumerate(programs):
            for j, prog2 in enumerate(programs[i+1:], i+1):
                if prog1.overlaps_with(prog2):
                    errors.append(
                        f"Programs '{prog1.program_name}' and '{prog2.program_name}' overlap: "
                        f"{prog1.start_line}-{prog1.end_line} vs {prog2.start_line}-{prog2.end_line}"
                    )
        
        # Check for invalid boundaries
        for program in programs:
            if program.start_line < 1:
                errors.append(f"Program '{program.program_name}' has invalid start_line: {program.start_line}")
            if program.end_line < program.start_line:
                errors.append(f"Program '{program.program_name}' has end_line before start_line")
        
        return len(errors) == 0, errors
    
    def get_supported_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this detector supports.
        
        Returns:
            List of file extensions (e.g., ['.rpg', '.rpgle'])
        """
        return []


class RPGProgramBoundaryDetector(ProgramBoundaryDetector):
    """Program boundary detector for RPG source files."""
    
    def get_language(self) -> str:
        return "RPG"
    
    def detect_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect RPG program boundaries using H-spec, F-spec, and procedure patterns.
        
        RPG programs are identified by:
        - H-spec (Control specification) at the beginning
        - F-spec (File specification) declarations
        - Procedure definitions (DCL-PR/END-PR blocks)
        """
        programs = []
        lines = source_code.splitlines()
        
        current_program = None
        program_counter = 1
        
        for i, line in enumerate(lines, 1):
            line_upper = line.strip().upper()
            
            # Check for H-spec (new program start)
            if self._is_h_spec(line):
                if current_program:
                    # End previous program
                    current_program.end_line = i - 1
                    programs.append(current_program)
                
                # Start new program
                program_name = self._extract_program_name_from_h_spec(line) or f"RPG_PROGRAM_{program_counter}"
                current_program = ProgramBoundary(
                    program_name=program_name,
                    start_line=i,
                    end_line=len(lines),  # Will be updated when we find the end
                    program_type=ProgramType.MAIN,
                    language="RPG",
                    entry_points=[program_name],
                    file_path=file_path
                )
                program_counter += 1
            
            # Check for procedure definitions
            elif self._is_procedure_start(line):
                proc_name = self._extract_procedure_name(line)
                if proc_name and current_program:
                    # For now, we'll treat procedures as part of the main program
                    # In a more sophisticated implementation, we might create separate boundaries
                    current_program.entry_points.append(proc_name)
        
        # Close the last program
        if current_program:
            programs.append(current_program)
        
        return programs
    
    def _is_h_spec(self, line: str) -> bool:
        """Check if line is an RPG H-spec (control specification)."""
        stripped = line.strip()
        return len(stripped) > 0 and stripped[0].upper() == 'H'
    
    def _is_procedure_start(self, line: str) -> bool:
        """Check if line starts a procedure definition."""
        return 'DCL-PR' in line.upper() or 'DCL-PROC' in line.upper()
    
    def _extract_program_name_from_h_spec(self, line: str) -> Optional[str]:
        """Extract program name from H-spec line."""
        # This is a simplified implementation
        # Real RPG H-spec parsing would be more complex
        match = re.search(r'NOMAIN|MAIN\s*\(\s*([A-Z0-9_]+)\s*\)', line.upper())
        if match:
            return match.group(1) if match.lastindex else None
        return None
    
    def _extract_procedure_name(self, line: str) -> Optional[str]:
        """Extract procedure name from DCL-PR or DCL-PROC line."""
        match = re.search(r'DCL-PR\s+([A-Z0-9_]+)', line.upper())
        if not match:
            match = re.search(r'DCL-PROC\s+([A-Z0-9_]+)', line.upper())
        return match.group(1) if match else None
    
    def get_supported_file_extensions(self) -> List[str]:
        return ['.rpg', '.rpgle', '.sqlrpgle']


class AssemblerProgramBoundaryDetector(ProgramBoundaryDetector):
    """Program boundary detector for Assembler source files."""
    
    def get_language(self) -> str:
        return "ASM"
    
    def detect_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect Assembler program boundaries using CSECT and ENTRY patterns.
        
        Assembler programs are identified by:
        - CSECT (Control Section) definitions
        - START directives (alternative to CSECT)
        - ENTRY points as separate program entities
        """
        programs = []
        lines = source_code.splitlines()
        
        # Track ENTRY points that might be separate programs
        entry_points = {}
        
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('*'):
                continue  # Skip empty lines and comments
            
            upper_line = stripped_line.upper()
            
            # Check for CSECT definition - more flexible pattern
            csect_match = re.match(r'^(\S+)\s+CSECT\s*', upper_line)
            if csect_match:
                csect_name = csect_match.group(1)
                
                # Find the end of this CSECT (next CSECT, START, or END)
                end_line = len(lines)
                for j in range(i, len(lines)):
                    next_line = lines[j].strip().upper()
                    if (re.match(r'^\S+\s+(?:CSECT|START)\s*', next_line) or 
                        next_line.startswith('END') or
                        next_line == 'END'):
                        end_line = j
                        break
                
                # Collect ENTRY points within this CSECT
                csect_entries = [csect_name]  # CSECT name is always an entry point
                for k in range(i, min(end_line, len(lines))):
                    entry_match = re.match(r'^\s*ENTRY\s+(\S+)', lines[k].strip().upper())
                    if entry_match:
                        entry_name = entry_match.group(1)
                        csect_entries.append(entry_name)
                        entry_points[entry_name] = i  # Track for potential separate programs
                
                programs.append(ProgramBoundary(
                    program_name=csect_name,
                    start_line=i,
                    end_line=end_line,
                    program_type=ProgramType.CSECT,
                    language="ASM",
                    entry_points=csect_entries,
                    file_path=file_path
                ))
            
            # Check for START directive (alternative to CSECT)
            elif re.match(r'^(\S+)\s+START\s+', upper_line):
                start_match = re.match(r'^(\S+)\s+START\s+', upper_line)
                if start_match:
                    program_name = start_match.group(1)
                    
                    # Find the end (next START, CSECT, or END)
                    end_line = len(lines)
                    for j in range(i, len(lines)):
                        next_line = lines[j].strip().upper()
                        if (re.match(r'^\S+\s+(?:CSECT|START)\s*', next_line) or 
                            next_line.startswith('END') or
                            next_line == 'END'):
                            end_line = j
                            break
                    
                    # Collect ENTRY points within this program
                    start_entries = [program_name]
                    for k in range(i, min(end_line, len(lines))):
                        entry_match = re.match(r'^\s*ENTRY\s+(\S+)', lines[k].strip().upper())
                        if entry_match:
                            entry_name = entry_match.group(1)
                            start_entries.append(entry_name)
                            entry_points[entry_name] = i
                    
                    programs.append(ProgramBoundary(
                        program_name=program_name,
                        start_line=i,
                        end_line=end_line,
                        program_type=ProgramType.MAIN,  # START typically indicates main program
                        language="ASM",
                        entry_points=start_entries,
                        file_path=file_path
                    ))
        
        # Handle standalone ENTRY points that might be separate programs
        # (This is less common but can occur in some Assembler styles)
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('*'):
                continue
            
            upper_line = stripped_line.upper()
            entry_match = re.match(r'^\s*ENTRY\s+(\S+)', upper_line)
            if entry_match:
                entry_name = entry_match.group(1)
                
                # Check if this ENTRY is not already part of a CSECT/START program
                is_standalone = True
                for program in programs:
                    if (program.start_line <= i <= program.end_line and 
                        entry_name in program.entry_points):
                        is_standalone = False
                        break
                
                if is_standalone:
                    # Create a separate program for this ENTRY point
                    # Find reasonable boundaries (until next major directive or end)
                    end_line = len(lines)
                    for j in range(i, len(lines)):
                        next_line = lines[j].strip().upper()
                        if (re.match(r'^\S+\s+(?:CSECT|START)\s*', next_line) or 
                            re.match(r'^\s*ENTRY\s+', next_line) or
                            next_line.startswith('END') or
                            next_line == 'END'):
                            end_line = j
                            break
                    
                    programs.append(ProgramBoundary(
                        program_name=entry_name,
                        start_line=i,
                        end_line=end_line,
                        program_type=ProgramType.ENTRY_POINT,
                        language="ASM",
                        entry_points=[entry_name],
                        file_path=file_path
                    ))
        
        return programs
    
    def get_supported_file_extensions(self) -> List[str]:
        return ['.asm', '.s', '.hlasm']


class NaturalProgramBoundaryDetector(ProgramBoundaryDetector):
    """Program boundary detector for Natural source files."""
    
    def __init__(self):
        """Initialize Natural program boundary detector."""
        super().__init__()
        # Import here to avoid circular imports
        from ..parsers.natural_parser import NaturalDependencyParser
        self.parser = NaturalDependencyParser()
    
    def get_language(self) -> str:
        return "NATURAL"
    
    def detect_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect Natural program boundaries using enhanced Natural parser.
        
        Natural programs are identified by:
        - DEFINE DATA PROGRAM statements (main programs)
        - DEFINE DATA SUBPROGRAM statements (subprograms)
        - DEFINE DATA PARAMETER statements (subprograms with parameters)
        - File extension-based classification for single-program files
        
        Args:
            source_code: Natural source code content
            file_path: Optional path to the source file
            
        Returns:
            List of ProgramBoundary objects representing detected programs
        """
        # Use the enhanced Natural parser for program boundary detection
        programs = self.parser.detect_program_boundaries(source_code, file_path)
        
        # Set file_path for all detected programs
        for program in programs:
            program.file_path = file_path
        
        return programs
    
    def get_supported_file_extensions(self) -> List[str]:
        return ['.NSP', '.NSN', '.NSC', '.NSL', '.NSG', '.NSD', '.NSA', '.NS8']


class REXXProgramBoundaryDetector(ProgramBoundaryDetector):
    """Program boundary detector for REXX source files."""
    
    def __init__(self):
        """Initialize REXX program boundary detector."""
        super().__init__()
        # Import here to avoid circular imports
        from ..parsers.rexx_parser import REXXDependencyParser
        self.parser = REXXDependencyParser()
    
    def get_language(self) -> str:
        return "REXX"
    
    def detect_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect REXX program boundaries using enhanced REXX parser.
        
        REXX programs are identified by:
        - Main program (everything not in procedures/functions)
        - Procedure definitions (label: PROCEDURE)
        - Function definitions (labels followed by function-like code)
        - Subroutine labels (labels followed by executable code)
        
        Args:
            source_code: REXX source code content
            file_path: Optional path to the source file
            
        Returns:
            List of ProgramBoundary objects representing detected programs
        """
        # Use the enhanced REXX parser for program boundary detection
        programs = self.parser.detect_program_boundaries(source_code, file_path)
        
        # Set file_path for all detected programs
        for program in programs:
            program.file_path = file_path
        
        return programs
    
    def get_supported_file_extensions(self) -> List[str]:
        return ['.rexx', '.rex', '.exec', '.txt']


class ProgramBoundaryDetectorFactory:
    """Factory for creating language-specific program boundary detectors."""
    
    _detectors = {
        'RPG': RPGProgramBoundaryDetector,
        'ASM': AssemblerProgramBoundaryDetector,
        'ASSEMBLER': AssemblerProgramBoundaryDetector,
        'NATURAL': NaturalProgramBoundaryDetector,
        'REXX': REXXProgramBoundaryDetector,
    }
    
    @classmethod
    def create_detector(cls, language: str) -> Optional[ProgramBoundaryDetector]:
        """
        Create a program boundary detector for the specified language.
        
        Args:
            language: Programming language name (case-insensitive)
            
        Returns:
            ProgramBoundaryDetector instance or None if language not supported
        """
        detector_class = cls._detectors.get(language.upper())
        return detector_class() if detector_class else None
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of supported languages."""
        return list(cls._detectors.keys())
    
    @classmethod
    def register_detector(cls, language: str, detector_class: type):
        """Register a new detector for a language."""
        cls._detectors[language.upper()] = detector_class