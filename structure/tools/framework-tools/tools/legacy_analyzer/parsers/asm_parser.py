"""Assembler (IBM z/OS) dependency parser."""

import re
from typing import Dict, List, Set
from .base_parser import BaseDependencyParser
from .asm_complexity_calculator import ASMComplexityCalculator


class ASMDependencyParser(BaseDependencyParser):
    """Parses IBM z/OS Assembler source for dependencies."""
    
    def __init__(self):
        """Initialize Assembler parser with regex patterns and complexity calculator."""
        super().__init__()
        
        # Initialize complexity calculator
        self.complexity_calculator = ASMComplexityCalculator()
        
        # COPY statement pattern (includes copybooks/macros)
        # Format: COPY membername
        self.copy_pattern = re.compile(
            r'^\s+COPY\s+([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # MACRO invocation pattern (macros are like includes)
        # Format: macroname parameters
        # Common macros: CALL, LINK, LOAD, etc.
        self.macro_pattern = re.compile(
            r'^\s+([A-Z][A-Z0-9@#$]*)\s+',
            re.MULTILINE
        )
        
        # CALL/LINK patterns for program calls
        # Format: CALL programname or LINK EP=programname
        self.call_pattern = re.compile(
            r'^\s+(?:CALL|LINK)\s+(?:EP=)?([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # LOAD pattern
        self.load_pattern = re.compile(
            r'^\s+LOAD\s+(?:EP=)?([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # XCTL pattern (transfer control)
        self.xctl_pattern = re.compile(
            r'^\s+XCTL\s+(?:EP=)?([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # ATTACH pattern (attach subtask)
        self.attach_pattern = re.compile(
            r'^\s+ATTACH\s+(?:EP=)?([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # DSECT pattern (dummy section - like copybook)
        self.dsect_pattern = re.compile(
            r'^([A-Z0-9@#$]+)\s+DSECT',
            re.IGNORECASE | re.MULTILINE
        )
        
        # CSECT pattern (control section - program entry)
        self.csect_pattern = re.compile(
            r'^([A-Z0-9@#$]+)\s+CSECT',
            re.IGNORECASE | re.MULTILINE
        )
        
        # ENTRY pattern (external entry point)
        self.entry_pattern = re.compile(
            r'^\s+ENTRY\s+([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # EXTRN pattern (external reference) - enhanced to handle more characters
        self.extrn_pattern = re.compile(
            r'^\s+EXTRN\s+([A-Z0-9À-ÿ@#$,\s_]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # WXTRN pattern (weak external reference) - enhanced to handle more characters
        self.wxtrn_pattern = re.compile(
            r'^\s+WXTRN\s+([A-Z0-9À-ÿ@#$,\s_]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # MACRO definition pattern
        self.macro_def_pattern = re.compile(
            r'^\s+MACRO\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        
        # MEND pattern (end of macro)
        self.mend_pattern = re.compile(
            r'^\s+MEND\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Enhanced CSECT pattern for program detection
        self.enhanced_csect_pattern = re.compile(
            r'^(\S+)\s+CSECT\s*',
            re.IGNORECASE | re.MULTILINE
        )
        
        # START pattern for program detection
        self.start_pattern = re.compile(
            r'^(\S+)\s+START\s+',
            re.IGNORECASE | re.MULTILINE
        )
        
        # DCB (Data Control Block) - file references
        self.dcb_pattern = re.compile(
            r'^\s+DCB\s+DDNAME=([A-Z0-9@#$]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Common system macros that shouldn't be treated as dependencies
        self.system_macros = {
            'STM', 'LM', 'LA', 'L', 'ST', 'LR', 'SR', 'AR', 'MVC', 'CLI', 'CLC',
            'BE', 'BNE', 'B', 'BR', 'BCR', 'BC', 'BALR', 'BAL', 'BAS', 'BASR',
            'MVI', 'MVZ', 'MVN', 'TR', 'TRT', 'ED', 'EDMK', 'PACK', 'UNPK',
            'AP', 'SP', 'MP', 'DP', 'ZAP', 'CP', 'CVB', 'CVD',
            'DS', 'DC', 'EQU', 'ORG', 'LTORG', 'DROP', 'USING', 'END',
            'SAVE', 'RETURN', 'GETMAIN', 'FREEMAIN', 'WTO', 'WTOR',
            'OPEN', 'CLOSE', 'GET', 'PUT', 'READ', 'WRITE', 'CHECK',
            'ABEND', 'SNAP', 'DUMP', 'ESPIE', 'ESTAE', 'SPIE', 'STAE'
        }
    
    def parse(self, source_code: str) -> Dict[str, List[str]]:
        """
        Extract dependencies from Assembler source.
        
        Patterns detected:
        - COPY statements: COPY COPYBOOK1
        - CALL/LINK: CALL PROGRAM1 or LINK EP=PROGRAM1
        - LOAD: LOAD EP=PROGRAM1
        - XCTL: XCTL EP=PROGRAM1
        - ATTACH: ATTACH EP=PROGRAM1
        - EXTRN: EXTRN SYMBOL1,SYMBOL2
        - WXTRN: WXTRN SYMBOL1
        - DCB: DCB DDNAME=FILENAME
        - Macros: Custom macro invocations
        
        Args:
            source_code: Assembler source code
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        # Normalize source code (remove comments, handle continuations)
        normalized_code = self._normalize_source(source_code)
        
        # Parse different dependency types
        copybooks = self._parse_copy_statements(normalized_code)
        calls = self._parse_call_statements(normalized_code)
        loads = self._parse_load_statements(normalized_code)
        xctls = self._parse_xctl_statements(normalized_code)
        attaches = self._parse_attach_statements(normalized_code)
        extrns = self._parse_extrn_statements(normalized_code)
        wxtrns = self._parse_wxtrn_statements(normalized_code)
        dcbs = self._parse_dcb_statements(normalized_code)
        macros = self._parse_macro_invocations(normalized_code)
        
        # Get program metadata
        csects = self._parse_csect_statements(normalized_code)
        dsects = self._parse_dsect_statements(normalized_code)
        entries = self._parse_entry_statements(normalized_code)
        starts = self._parse_start_statements(normalized_code)
        macros_defined = self._parse_macro_definitions(normalized_code)
        
        # Determine program type and characteristics
        is_main_program = len(csects) > 0 or len(starts) > 0
        has_macros = len(macros_defined) > 0
        program_type = self._determine_program_type(csects, starts, entries, has_macros)
        
        return {
            'copybooks': list(copybooks),
            'calls': list(calls),
            'loads': list(loads),
            'xctls': list(xctls),
            'attaches': list(attaches),
            'external_refs': list(extrns | wxtrns),
            'files': list(dcbs),
            'macros': list(macros),
            'is_main_program': is_main_program,
            'program_type': program_type,
            'has_macros': has_macros,
            'metadata': {
                'csects': list(csects),
                'dsects': list(dsects),
                'entries': list(entries),
                'starts': list(starts),
                'macros_defined': list(macros_defined)
            }
        }
    
    def _normalize_source(self, source_code: str) -> str:
        """
        Normalize Assembler source code.
        
        - Remove comment lines (starting with *)
        - Remove inline comments (after instruction)
        - Handle continuation lines
        - Preserve line structure for pattern matching
        
        Args:
            source_code: Raw source code
            
        Returns:
            Normalized source code
        """
        lines = []
        for line in source_code.split('\n'):
            # Skip full-line comments
            if line.strip().startswith('*'):
                continue
            
            # Remove inline comments (after instruction)
            # Assembler comments typically start after column 40 or with *
            if '*' in line:
                # Find comment start (but not in quoted strings)
                in_quote = False
                for i, char in enumerate(line):
                    if char == "'":
                        in_quote = not in_quote
                    elif char == '*' and not in_quote and i > 0:
                        line = line[:i]
                        break
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _parse_copy_statements(self, source_code: str) -> Set[str]:
        """Parse COPY statements."""
        copybooks = set()
        for match in self.copy_pattern.finditer(source_code):
            copybook = match.group(1).strip().upper()
            if copybook:
                copybooks.add(copybook)
        return copybooks
    
    def _parse_call_statements(self, source_code: str) -> Set[str]:
        """Parse CALL and LINK statements."""
        calls = set()
        for match in self.call_pattern.finditer(source_code):
            program = match.group(1).strip().upper()
            if program and not program.startswith('='):  # Skip literals
                calls.add(program)
        return calls
    
    def _parse_load_statements(self, source_code: str) -> Set[str]:
        """Parse LOAD statements."""
        loads = set()
        for match in self.load_pattern.finditer(source_code):
            program = match.group(1).strip().upper()
            if program and not program.startswith('='):
                loads.add(program)
        return loads
    
    def _parse_xctl_statements(self, source_code: str) -> Set[str]:
        """Parse XCTL (transfer control) statements."""
        xctls = set()
        for match in self.xctl_pattern.finditer(source_code):
            program = match.group(1).strip().upper()
            if program and not program.startswith('='):
                xctls.add(program)
        return xctls
    
    def _parse_attach_statements(self, source_code: str) -> Set[str]:
        """Parse ATTACH statements."""
        attaches = set()
        for match in self.attach_pattern.finditer(source_code):
            program = match.group(1).strip().upper()
            if program and not program.startswith('='):
                attaches.add(program)
        return attaches
    
    def _parse_extrn_statements(self, source_code: str) -> Set[str]:
        """Parse EXTRN (external reference) statements."""
        extrns = set()
        for match in self.extrn_pattern.finditer(source_code):
            symbols = match.group(1).strip().upper()
            # Split by comma and clean up
            for symbol in symbols.split(','):
                symbol = symbol.strip()
                if symbol:
                    extrns.add(symbol)
        return extrns
    
    def _parse_wxtrn_statements(self, source_code: str) -> Set[str]:
        """Parse WXTRN (weak external reference) statements."""
        wxtrns = set()
        for match in self.wxtrn_pattern.finditer(source_code):
            symbols = match.group(1).strip().upper()
            for symbol in symbols.split(','):
                symbol = symbol.strip()
                if symbol:
                    wxtrns.add(symbol)
        return wxtrns
    
    def _parse_dcb_statements(self, source_code: str) -> Set[str]:
        """Parse DCB (Data Control Block) statements for file references."""
        dcbs = set()
        for match in self.dcb_pattern.finditer(source_code):
            ddname = match.group(1).strip().upper()
            if ddname:
                dcbs.add(ddname)
        return dcbs
    
    def _parse_macro_invocations(self, source_code: str) -> Set[str]:
        """
        Parse macro invocations (excluding system macros).
        
        This identifies custom macros that might be dependencies.
        """
        macros = set()
        for match in self.macro_pattern.finditer(source_code):
            macro = match.group(1).strip().upper()
            # Skip system macros and common instructions
            if macro and macro not in self.system_macros and len(macro) > 1:
                # Additional filtering: skip if it looks like a label
                # (labels typically have specific patterns)
                if not macro.endswith(':'):
                    macros.add(macro)
        return macros
    
    def _parse_csect_statements(self, source_code: str) -> Set[str]:
        """Parse CSECT (Control Section) statements."""
        csects = set()
        for match in self.csect_pattern.finditer(source_code):
            csect = match.group(1).strip().upper()
            if csect:
                csects.add(csect)
        return csects
    
    def _parse_dsect_statements(self, source_code: str) -> Set[str]:
        """Parse DSECT (Dummy Section) statements."""
        dsects = set()
        for match in self.dsect_pattern.finditer(source_code):
            dsect = match.group(1).strip().upper()
            if dsect:
                dsects.add(dsect)
        return dsects
    
    def _parse_entry_statements(self, source_code: str) -> Set[str]:
        """Parse ENTRY statements."""
        entries = set()
        for match in self.entry_pattern.finditer(source_code):
            entry = match.group(1).strip().upper()
            if entry:
                entries.add(entry)
        return entries
    
    def _parse_start_statements(self, source_code: str) -> Set[str]:
        """Parse START statements."""
        starts = set()
        for match in self.start_pattern.finditer(source_code):
            start = match.group(1).strip().upper()
            if start:
                starts.add(start)
        return starts
    
    def _parse_macro_definitions(self, source_code: str) -> Set[str]:
        """Parse MACRO definitions to identify defined macros."""
        macros = set()
        lines = source_code.split('\n')
        in_macro = False
        current_macro = None
        
        for line in lines:
            stripped = line.strip().upper()
            
            if stripped == 'MACRO':
                in_macro = True
                continue
            elif stripped == 'MEND' and in_macro:
                if current_macro:
                    macros.add(current_macro)
                in_macro = False
                current_macro = None
            elif in_macro and not current_macro and stripped:
                # First non-empty line after MACRO is typically the macro name/prototype
                # Extract macro name (first word)
                words = stripped.split()
                if words and not words[0].startswith('*'):
                    # Handle macro prototype like "&NAME MYMACRO &PARM1,&PARM2"
                    for word in words:
                        if not word.startswith('&') and word.isalnum():
                            current_macro = word
                            break
        
        return macros
    
    def _determine_program_type(self, csects: Set[str], starts: Set[str], 
                               entries: Set[str], has_macros: bool) -> str:
        """Determine the type of Assembler program based on its characteristics."""
        if has_macros and not csects and not starts:
            return "MACRO_LIBRARY"
        elif len(csects) > 1:
            return "MULTI_CSECT"
        elif len(csects) == 1:
            return "CSECT_PROGRAM"
        elif len(starts) > 0:
            return "START_PROGRAM"
        elif len(entries) > 0:
            return "ENTRY_POINT"
        else:
            return "UNKNOWN"
    
    def get_supported_patterns(self) -> List[str]:
        """Get list of dependency patterns this parser supports."""
        return [
            'COPY',
            'CALL',
            'LINK',
            'LOAD',
            'XCTL',
            'ATTACH',
            'EXTRN',
            'WXTRN',
            'DCB',
            'MACRO'
        ]
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of file extensions this parser supports."""
        return ['.asm', '.s', '.mac', '.ASM', '.S', '.MAC']
    
    def parse_with_program_detection(self, source_code: str, file_path: str = None) -> Dict[str, any]:
        """
        Parse Assembler source code with program boundary detection.
        
        This method detects individual CSECT sections and ENTRY points as separate
        program entities, tracking dependencies for each program separately.
        
        Args:
            source_code: Assembler source code
            file_path: Optional path to the source file
            
        Returns:
            Dictionary with program boundaries and per-program dependencies
        """
        from ..analysis.program_boundary_detector import AssemblerProgramBoundaryDetector
        from ..models.program_boundary import ProgramParseResult
        
        # Use the boundary detector to find programs
        detector = AssemblerProgramBoundaryDetector()
        programs = detector.detect_boundaries(source_code, file_path)
        
        # Extract dependencies for each program
        dependencies = self._extract_program_level_dependencies(source_code, programs)
        
        # Create parse result
        total_lines = len(source_code.splitlines())
        result = ProgramParseResult(
            file_path=file_path or "unknown",
            language="ASM",
            programs=programs,
            dependencies=dependencies,
            total_lines=total_lines
        )
        
        return {
            'programs': programs,
            'dependencies': dependencies,
            'parse_result': result
        }
    
    def _extract_program_level_dependencies(self, source_code: str, programs: List) -> Dict[str, List[str]]:
        """
        Extract dependencies for each detected program separately.
        
        Args:
            source_code: Full source code
            programs: List of ProgramBoundary objects
            
        Returns:
            Dictionary mapping program names to their dependencies
        """
        dependencies = {}
        lines = source_code.splitlines()
        
        for program in programs:
            program_dependencies = []
            
            # Extract dependencies from this program's lines only
            start_idx = max(0, program.start_line - 1)  # Convert to 0-based index
            end_idx = min(len(lines), program.end_line)
            
            program_source = '\n'.join(lines[start_idx:end_idx])
            program_deps = self.parse(program_source)
            
            # Flatten all dependency types into a single list
            for dep_type, deps in program_deps.items():
                if isinstance(deps, list):
                    program_dependencies.extend(deps)
            
            dependencies[program.program_name] = list(set(program_dependencies))  # Remove duplicates
        
        return dependencies
