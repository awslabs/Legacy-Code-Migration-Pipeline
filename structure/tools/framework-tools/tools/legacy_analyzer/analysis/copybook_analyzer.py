"""Copybook analysis framework for executable code detection."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set, Tuple
import re
import os
from ..models.program_boundary import CopybookAnalysisResult
from ..models.dependency import Dependency, DependencyType
from ..models.record_layout import RecordField


class CopybookAnalyzer:
    """Analyzer for detecting executable code within copybooks and includes.
    
    This class analyzes copybook content to distinguish between data structures
    and executable code, which is crucial for accurate dependency tracking.
    """
    
    def __init__(self):
        """Initialize the copybook analyzer."""
        self._language_analyzers = {
            'COBOL': COBOLCopybookAnalyzer(),
            'PLI': PLICopybookAnalyzer(),
            'NATURAL': NaturalCopybookAnalyzer(),
        }
    
    def analyze_content(self, copybook_path: str, language: str, content: Optional[str] = None) -> CopybookAnalysisResult:
        """
        Analyze copybook content to detect executable code.
        
        Args:
            copybook_path: Path to the copybook file
            language: Programming language of the copybook
            content: Optional content string (if None, will read from file)
            
        Returns:
            CopybookAnalysisResult with analysis findings
        """
        if content is None:
            try:
                with open(copybook_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except (IOError, OSError) as e:
                return CopybookAnalysisResult(
                    copybook_name=os.path.basename(copybook_path),
                    file_path=copybook_path,
                    has_executable_code=False,
                    data_structures=[],
                    procedure_calls=[],
                    program_dependencies=[],
                    confidence_level=0.0,
                    language=language,
                    analysis_notes=f"Failed to read file: {e}"
                )
        
        # Get language-specific analyzer
        analyzer = self._language_analyzers.get(language.upper())
        if not analyzer:
            # Use generic analyzer for unsupported languages
            analyzer = GenericCopybookAnalyzer()
        
        return analyzer.analyze(copybook_path, content, language)
    
    def register_language_analyzer(self, language: str, analyzer: 'LanguageCopybookAnalyzer'):
        """Register a language-specific copybook analyzer."""
        self._language_analyzers[language.upper()] = analyzer


class LanguageCopybookAnalyzer(ABC):
    """Abstract base class for language-specific copybook analyzers."""
    
    @abstractmethod
    def analyze(self, copybook_path: str, content: str, language: str) -> CopybookAnalysisResult:
        """Analyze copybook content for the specific language."""
        pass
    
    def _extract_copybook_name(self, copybook_path: str) -> str:
        """Extract copybook name from file path."""
        return os.path.splitext(os.path.basename(copybook_path))[0].upper()


class COBOLCopybookAnalyzer(LanguageCopybookAnalyzer):
    """Analyzer for COBOL copybooks."""
    
    def analyze(self, copybook_path: str, content: str, language: str) -> CopybookAnalysisResult:
        """Analyze COBOL copybook content."""
        copybook_name = self._extract_copybook_name(copybook_path)
        
        # Initialize analysis results
        has_executable_code = False
        data_structures = []
        procedure_calls = []
        program_dependencies = []
        confidence_level = 0.8  # Start with high confidence
        
        lines = content.splitlines()
        executable_indicators = 0
        data_indicators = 0
        
        for i, line in enumerate(lines, 1):
            line_upper = line.strip().upper()
            
            # Skip comments and empty lines
            if not line_upper or line_upper.startswith('*') or line_upper.startswith('/'):
                continue
            
            # Check for executable code patterns
            if self._is_executable_statement(line_upper):
                has_executable_code = True
                executable_indicators += 1
                
                # Extract program calls
                calls = self._extract_program_calls(line_upper)
                procedure_calls.extend(calls)
                
                # Create dependencies for calls
                for call in calls:
                    dependency = Dependency(
                        source_artifact=copybook_name,
                        source_type="COPYBOOK",
                        target_artifact=call,
                        target_type="PROGRAM",
                        dependency_type=DependencyType.CALL,
                        source_language="COBOL",
                        source_file=copybook_path,
                        line_number=i
                    )
                    program_dependencies.append(dependency)
            
            # Check for data structure patterns
            elif self._is_data_structure(line_upper):
                data_indicators += 1
                struct_name = self._extract_data_structure_name(line_upper)
                if struct_name:
                    data_structures.append(struct_name)
        
        # Adjust confidence based on analysis
        if executable_indicators == 0 and data_indicators > 0:
            confidence_level = 0.9  # High confidence it's data-only
        elif executable_indicators > 0 and data_indicators == 0:
            confidence_level = 0.9  # High confidence it's executable
        elif executable_indicators > 0 and data_indicators > 0:
            confidence_level = 0.7  # Mixed content, lower confidence
        
        return CopybookAnalysisResult(
            copybook_name=copybook_name,
            file_path=copybook_path,
            has_executable_code=has_executable_code,
            data_structures=list(set(data_structures)),  # Remove duplicates
            procedure_calls=list(set(procedure_calls)),  # Remove duplicates
            program_dependencies=program_dependencies,
            confidence_level=confidence_level,
            language=language
        )
    
    def _is_executable_statement(self, line: str) -> bool:
        """Check if line contains executable COBOL code."""
        executable_patterns = [
            r'\bCALL\s+',
            r'\bPERFORM\s+',
            r'\bIF\s+',
            r'\bEVALUATE\s+',
            r'\bMOVE\s+',
            r'\bADD\s+',
            r'\bSUBTRACT\s+',
            r'\bMULTIPLY\s+',
            r'\bDIVIDE\s+',
            r'\bCOMPUTE\s+',
            r'\bEXEC\s+CICS\s+',
            r'\bEXEC\s+SQL\s+',
            r'\bGO\s+TO\s+',
            r'\bSTOP\s+RUN\s+',
            r'\bEXIT\s+',
            r'\bRETURN\s+',
        ]
        
        return any(re.search(pattern, line) for pattern in executable_patterns)
    
    def _is_data_structure(self, line: str) -> bool:
        """Check if line defines a COBOL data structure."""
        data_patterns = [
            r'^\s*\d+\s+[A-Z0-9-]+',  # Level number followed by data name
            r'\bPIC\s+',
            r'\bPICTURE\s+',
            r'\bVALUE\s+',
            r'\bUSAGE\s+',
            r'\bREDEFINES\s+',
            r'\bOCCURS\s+',
        ]
        
        return any(re.search(pattern, line) for pattern in data_patterns)
    
    def _extract_program_calls(self, line: str) -> List[str]:
        """Extract program names from CALL statements."""
        calls = []
        
        # CALL statement pattern
        call_match = re.search(r'CALL\s+["\']?([A-Z0-9#@$-]+)["\']?', line)
        if call_match:
            calls.append(call_match.group(1))
        
        # PERFORM statement pattern (for paragraph/section calls)
        perform_match = re.search(r'PERFORM\s+([A-Z0-9-]+)', line)
        if perform_match:
            calls.append(perform_match.group(1))
        
        return calls
    
    def _extract_data_structure_name(self, line: str) -> Optional[str]:
        """Extract data structure name from data definition."""
        match = re.search(r'^\s*\d+\s+([A-Z0-9-]+)', line)
        return match.group(1) if match else None

    def extract_record_layout(self, content: str) -> Tuple[List[RecordField], Optional[str]]:
        """Parse COBOL copybook content into a hierarchical RecordField tree.

        Args:
            content: Raw text content of a COBOL copybook.

        Returns:
            A tuple of (fields, error_note).
            - On success: (list_of_top_level_fields, None)
            - On empty/whitespace input: ([], None)
            - On unparseable content: ([], error_note_string)
        """
        # Handle empty / whitespace-only content
        if not content or not content.strip():
            return ([], None)

        # Detect binary data: check for null bytes or high ratio of non-printable chars
        non_printable = sum(
            1 for ch in content
            if ord(ch) < 32 and ch not in ('\n', '\r', '\t', '\x0c')
        )
        if non_printable > len(content) * 0.1:
            return ([], "Content appears to be binary data and cannot be parsed as COBOL copybook")

        # Regex to parse a COBOL data definition line.
        # Handles fixed-format (cols 1-6 seq, col 7 indicator, cols 8-72 code)
        # and free-format lines.
        field_pattern = re.compile(
            r'^\s*(\d{1,2})\s+'           # level number
            r'([A-Z0-9][\w-]*|FILLER)'    # field name
            r'(.*?)\.\s*$',               # rest of clause up to period
            re.IGNORECASE
        )
        pic_pattern = re.compile(r'\bPIC(?:TURE)?\s+(\S+)', re.IGNORECASE)
        usage_pattern = re.compile(r'\bUSAGE\s+(?:IS\s+)?(\S+)', re.IGNORECASE)
        occurs_pattern = re.compile(r'\bOCCURS\s+(\d+)', re.IGNORECASE)
        redefines_pattern = re.compile(r'\bREDEFINES\s+([A-Z0-9][\w-]*)', re.IGNORECASE)

        lines = content.splitlines()
        parsed_fields: List[RecordField] = []

        for raw_line in lines:
            # Strip COBOL fixed-format: skip if col-7 is comment indicator
            if len(raw_line) > 6 and raw_line[6] in ('*', '/'):
                continue
            # Also skip lines that start with * (free-format comment)
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('*') or stripped.startswith('/'):
                continue

            # Remove sequence number area (cols 1-6) for fixed-format
            code_area = raw_line[6:] if len(raw_line) > 6 else raw_line

            match = field_pattern.match(code_area.strip())
            if not match:
                continue

            level = int(match.group(1))
            name = match.group(2).upper()
            rest = match.group(3)

            pic_val = None
            pic_m = pic_pattern.search(rest)
            if pic_m:
                pic_val = pic_m.group(1).rstrip('.')

            usage_val = None
            usage_m = usage_pattern.search(rest)
            if usage_m:
                usage_val = usage_m.group(1).rstrip('.')

            occurs_val = None
            occurs_m = occurs_pattern.search(rest)
            if occurs_m:
                occurs_val = int(occurs_m.group(1))

            redefines_val = None
            redefines_m = redefines_pattern.search(rest)
            if redefines_m:
                redefines_val = redefines_m.group(1).upper()

            parsed_fields.append(RecordField(
                level=level,
                name=name,
                pic=pic_val,
                usage=usage_val,
                occurs=occurs_val,
                redefines=redefines_val,
            ))

        if not parsed_fields:
            # Content had lines but nothing parseable — could be comments-only
            # which is valid but empty
            return ([], None)

        # Build hierarchical tree using a stack
        roots: List[RecordField] = []
        stack: List[RecordField] = []  # stack of (field) ordered by nesting

        for fld in parsed_fields:
            # Pop stack entries with level >= current level
            while stack and stack[-1].level >= fld.level:
                stack.pop()

            if stack:
                stack[-1].children.append(fld)
            else:
                roots.append(fld)

            stack.append(fld)

        return (roots, None)


class PLICopybookAnalyzer(LanguageCopybookAnalyzer):
    """Analyzer for PL/I include files."""
    
    def analyze(self, copybook_path: str, content: str, language: str) -> CopybookAnalysisResult:
        """Analyze PL/I include content."""
        copybook_name = self._extract_copybook_name(copybook_path)
        
        has_executable_code = False
        data_structures = []
        procedure_calls = []
        program_dependencies = []
        confidence_level = 0.8
        
        lines = content.splitlines()
        executable_indicators = 0
        data_indicators = 0
        
        for i, line in enumerate(lines, 1):
            line_upper = line.strip().upper()
            
            # Skip comments and empty lines
            if not line_upper or line_upper.startswith('/*'):
                continue
            
            # Check for executable code patterns
            if self._is_executable_statement(line_upper):
                has_executable_code = True
                executable_indicators += 1
                
                # Extract program calls
                calls = self._extract_program_calls(line_upper)
                procedure_calls.extend(calls)
                
                # Create dependencies for calls
                for call in calls:
                    dependency = Dependency(
                        source_artifact=copybook_name,
                        source_type="COPYBOOK",
                        target_artifact=call,
                        target_type="PROGRAM",
                        dependency_type=DependencyType.CALL,
                        source_language="PLI",
                        source_file=copybook_path,
                        line_number=i
                    )
                    program_dependencies.append(dependency)
            
            # Check for data structure patterns
            elif self._is_data_structure(line_upper):
                data_indicators += 1
                struct_name = self._extract_data_structure_name(line_upper)
                if struct_name:
                    data_structures.append(struct_name)
        
        # Adjust confidence based on analysis
        if executable_indicators == 0 and data_indicators > 0:
            confidence_level = 0.9
        elif executable_indicators > 0 and data_indicators == 0:
            confidence_level = 0.9
        elif executable_indicators > 0 and data_indicators > 0:
            confidence_level = 0.7
        
        return CopybookAnalysisResult(
            copybook_name=copybook_name,
            file_path=copybook_path,
            has_executable_code=has_executable_code,
            data_structures=list(set(data_structures)),
            procedure_calls=list(set(procedure_calls)),
            program_dependencies=program_dependencies,
            confidence_level=confidence_level,
            language=language
        )
    
    def _is_executable_statement(self, line: str) -> bool:
        """Check if line contains executable PL/I code."""
        # First check if this is a data declaration - if so, it's not executable
        if self._is_data_structure(line):
            return False
        
        executable_patterns = [
            r'\bCALL\s+',
            r'\bIF\s+.+\bTHEN\b',  # IF-THEN statements (require THEN to avoid false positives)
            r'\bDO\s+',
            r'\bSELECT\s+',
            r'\bGOTO\s+',
            r'\bRETURN\s+',
            r'\bSTOP\s+',
            r'\bPUT\s+',
            r'\bGET\s+',
            r'\bREAD\s+',
            r'\bWRITE\s+',
            r'\bREWRITE\s+',
            r'\bDELETE\s+',
            r'\bPROC\b',  # Procedure definitions
            r'\bPROCEDURE\b',  # Procedure definitions
            r'\bEND\s+\w+',  # End of procedures
            r'\bWHILE\s+',  # WHILE loops
            r'\bFOR\s+',  # FOR loops
        ]
        
        return any(re.search(pattern, line) for pattern in executable_patterns)
    
    def _is_data_structure(self, line: str) -> bool:
        """Check if line defines a PL/I data structure."""
        data_patterns = [
            r'\bDCL\s+',
            r'\bDECLARE\s+',
            r'\bSTRUCTURE\s+',
            r'\bBASED\s+',
            r'\bCONTROLLED\s+',
            r'\bSTATIC\s+',
            r'\bAUTOMATIC\s+',
        ]
        
        return any(re.search(pattern, line) for pattern in data_patterns)
    
    def _extract_program_calls(self, line: str) -> List[str]:
        """Extract program names from CALL statements."""
        calls = []
        
        call_match = re.search(r'CALL\s+([A-Z0-9#@$_]+)', line)
        if call_match:
            calls.append(call_match.group(1))
        
        return calls
    
    def _extract_data_structure_name(self, line: str) -> Optional[str]:
        """Extract data structure name from declaration."""
        match = re.search(r'DCL\s+([A-Z0-9_]+)', line)
        if not match:
            match = re.search(r'DECLARE\s+([A-Z0-9_]+)', line)
        return match.group(1) if match else None


class NaturalCopybookAnalyzer(LanguageCopybookAnalyzer):
    """Analyzer for Natural copycode."""
    
    def analyze(self, copybook_path: str, content: str, language: str) -> CopybookAnalysisResult:
        """Analyze Natural copycode content."""
        copybook_name = self._extract_copybook_name(copybook_path)
        
        has_executable_code = False
        data_structures = []
        procedure_calls = []
        program_dependencies = []
        confidence_level = 0.8
        
        lines = content.splitlines()
        executable_indicators = 0
        data_indicators = 0
        
        for i, line in enumerate(lines, 1):
            line_upper = line.strip().upper()
            
            # Skip comments and empty lines
            if not line_upper or line_upper.startswith('*'):
                continue
            
            # Check for executable code patterns
            if self._is_executable_statement(line_upper):
                has_executable_code = True
                executable_indicators += 1
                
                # Extract program calls
                calls = self._extract_program_calls(line_upper)
                procedure_calls.extend(calls)
                
                # Create dependencies for calls
                for call in calls:
                    dependency = Dependency(
                        source_artifact=copybook_name,
                        source_type="COPYBOOK",
                        target_artifact=call,
                        target_type="PROGRAM",
                        dependency_type=DependencyType.CALL,
                        source_language="NATURAL",
                        source_file=copybook_path,
                        line_number=i
                    )
                    program_dependencies.append(dependency)
            
            # Check for data structure patterns
            elif self._is_data_structure(line_upper):
                data_indicators += 1
                struct_name = self._extract_data_structure_name(line_upper)
                if struct_name:
                    data_structures.append(struct_name)
        
        # Adjust confidence based on analysis
        if executable_indicators == 0 and data_indicators > 0:
            confidence_level = 0.9
        elif executable_indicators > 0 and data_indicators == 0:
            confidence_level = 0.9
        elif executable_indicators > 0 and data_indicators > 0:
            confidence_level = 0.7
        
        return CopybookAnalysisResult(
            copybook_name=copybook_name,
            file_path=copybook_path,
            has_executable_code=has_executable_code,
            data_structures=list(set(data_structures)),
            procedure_calls=list(set(procedure_calls)),
            program_dependencies=program_dependencies,
            confidence_level=confidence_level,
            language=language
        )
    
    def _is_executable_statement(self, line: str) -> bool:
        """Check if line contains executable Natural code."""
        executable_patterns = [
            r'\bCALLNAT\s+',
            r'\bFETCH\s+',
            r'\bIF\s+',
            r'\bDECIDE\s+',
            r'\bFOR\s+',
            r'\bREPEAT\s+',
            r'\bWHILE\s+',
            r'\bMOVE\s+',
            r'\bADD\s+',
            r'\bSUBTRACT\s+',
            r'\bMULTIPLY\s+',
            r'\bDIVIDE\s+',
            r'\bCOMPUTE\s+',
            r'\bREAD\s+',
            r'\bFIND\s+',
            r'\bSTORE\s+',
            r'\bUPDATE\s+',
            r'\bDELETE\s+',
            r'\bESCAPE\s+',
            r'\bSTOP\s+',
        ]
        
        return any(re.search(pattern, line) for pattern in executable_patterns)
    
    def _is_data_structure(self, line: str) -> bool:
        """Check if line defines a Natural data structure."""
        data_patterns = [
            r'\bDEFINE\s+DATA\s+',
            r'^\s*\d+\s+[A-Z0-9#@$-]+',  # Level number followed by field name
            r'\bVIEW\s+OF\s+',
            r'\bLOCAL\s+',
            r'\bGLOBAL\s+',
            r'\bPARAMETER\s+',
        ]
        
        return any(re.search(pattern, line) for pattern in data_patterns)
    
    def _extract_program_calls(self, line: str) -> List[str]:
        """Extract program names from Natural statements."""
        calls = []
        
        # CALLNAT statement
        callnat_match = re.search(r'CALLNAT\s+["\']?([A-Z0-9#@$-]+)["\']?', line)
        if callnat_match:
            calls.append(callnat_match.group(1))
        
        # FETCH statement
        fetch_match = re.search(r'FETCH\s+["\']?([A-Z0-9#@$-]+)["\']?', line)
        if fetch_match:
            calls.append(fetch_match.group(1))
        
        return calls
    
    def _extract_data_structure_name(self, line: str) -> Optional[str]:
        """Extract data structure name from Natural definition."""
        match = re.search(r'^\s*\d+\s+([A-Z0-9#@$-]+)', line)
        if not match:
            match = re.search(r'VIEW\s+OF\s+([A-Z0-9#@$-]+)', line)
        return match.group(1) if match else None


class GenericCopybookAnalyzer(LanguageCopybookAnalyzer):
    """Generic analyzer for unsupported languages."""
    
    def analyze(self, copybook_path: str, content: str, language: str) -> CopybookAnalysisResult:
        """Provide basic analysis for unsupported languages."""
        copybook_name = self._extract_copybook_name(copybook_path)
        
        # Very basic analysis - look for common patterns
        has_executable_code = False
        lines = content.splitlines()
        
        for line in lines:
            line_upper = line.strip().upper()
            if any(keyword in line_upper for keyword in ['CALL', 'EXEC', 'PERFORM', 'IF', 'WHILE', 'FOR']):
                has_executable_code = True
                break
        
        return CopybookAnalysisResult(
            copybook_name=copybook_name,
            file_path=copybook_path,
            has_executable_code=has_executable_code,
            data_structures=[],
            procedure_calls=[],
            program_dependencies=[],
            confidence_level=0.3,  # Low confidence for generic analysis
            language=language,
            analysis_notes="Generic analysis - language-specific analyzer not available"
        )