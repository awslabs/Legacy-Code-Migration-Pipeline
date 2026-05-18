"""REXX dependency parser."""

import re
from typing import Dict, List, Set, Optional
from .base_parser import BaseDependencyParser
from ..models.program_boundary import ProgramBoundary, ProgramParseResult, ProgramType


class REXXDependencyParser(BaseDependencyParser):
    """Parses REXX source for dependencies."""
    
    def __init__(self):
        """Initialize REXX parser with regex patterns."""
        # CALL statement patterns for program/subroutine dependencies
        # Handles: CALL PROGNAME, CALL 'PROGNAME', CALL label
        self.call_pattern = re.compile(
            r'\bCALL\s+([\'"]?)([A-Z0-9\-_@#$]+)\1',
            re.IGNORECASE
        )
        
        # Procedure definition patterns (label: PROCEDURE or just label:)
        # Handles: LABEL: PROCEDURE, LABEL:PROCEDURE, or LABEL: (subroutine label)
        self.procedure_pattern = re.compile(
            r'^([A-Z0-9_]+)\s*:\s*(?:PROCEDURE\b)?',
            re.IGNORECASE | re.MULTILINE
        )
        
        # EXECIO statement patterns for dataset references
        # Handles: EXECIO * DISKR DDNAME, EXECIO 1 DISKW OUTPUT
        self.execio_pattern = re.compile(
            r'\bEXECIO\s+(?:\*|\d+)\s+DISK[RW]\s+([A-Z0-9_]+)',
            re.IGNORECASE
        )
        
        # ADDRESS command patterns (TSO, ISPEXEC, ISREDIT, LINKMVS, etc.)
        # Handles: ADDRESS TSO, ADDRESS ISPEXEC 'command', ADDRESS LINKMVS 'PROG'
        self.address_pattern = re.compile(
            r'\bADDRESS\s+([A-Z0-9_]+)',
            re.IGNORECASE
        )
        
        # ADDRESS LINKMVS/LINKPGM patterns for program calls
        # Handles: ADDRESS LINKMVS 'PROGNAME', ADDRESS LINKPGM 'PROG'
        self.address_link_pattern = re.compile(
            r'\bADDRESS\s+(?:LINKMVS|LINKPGM)\s+[\'"]([A-Z0-9\-_@#$]+)[\'"]',
            re.IGNORECASE
        )
        
        # INCLUDE directive patterns
        # Handles: /* INCLUDE filename */
        self.include_pattern = re.compile(
            r'/\*\s*INCLUDE\s+([A-Z0-9\-_\.]+)\s*\*/',
            re.IGNORECASE
        )
        
        # TSO command patterns (common utilities)
        # Handles: 'ALLOCATE ...', 'LISTDSI ...', 'LISTCAT ...', etc.
        self.tso_command_pattern = re.compile(
            r'[\'"](?:ALLOCATE|LISTDSI|LISTCAT|DELETE|RENAME|SUBMIT|TRANSMIT|RECEIVE)\b',
            re.IGNORECASE
        )
        
        # ISPEXEC command patterns
        # Handles: 'LMINIT ...', 'LMOPEN ...', 'EDIT ...', etc.
        self.ispexec_command_pattern = re.compile(
            r'[\'"](?:LMINIT|LMOPEN|LMCLOSE|LMFREE|LMGET|LMPUT|EDIT|BROWSE|VIEW|VGET|VPUT)\b',
            re.IGNORECASE
        )
        
        # Function call patterns (built-in and external)
        # Handles: result = FUNCTION(args) or FUNCTION(args)
        self.function_call_pattern = re.compile(
            r'\b([A-Z][A-Z0-9_]*)\s*\(',
            re.IGNORECASE
        )
        
        # REXX file extensions
        self.supported_extensions = [
            '.rexx',  # Standard REXX extension
            '.rex',   # Alternative REXX extension
            '.txt'    # CBTapes format (text files containing REXX)
        ]
        
        # Built-in REXX functions and keywords to exclude from external calls
        self.builtin_functions = {
            'ABBREV', 'ABS', 'ADDRESS', 'ARG', 'B2X', 'BITAND', 'BITOR', 'BITXOR',
            'C2D', 'C2X', 'CENTER', 'CENTRE', 'CHANGESTR', 'CHARIN', 'CHAROUT',
            'CHARS', 'COMPARE', 'CONDITION', 'COPIES', 'COUNTSTR', 'D2C', 'D2X',
            'DATATYPE', 'DATE', 'DELSTR', 'DELWORD', 'DIGITS', 'ERRORTEXT', 'FORM',
            'FORMAT', 'FUZZ', 'INDEX', 'INSERT', 'LASTPOS', 'LEFT', 'LENGTH',
            'LINEIN', 'LINEOUT', 'LINES', 'MAX', 'MIN', 'OVERLAY', 'POS', 'QUEUED',
            'RANDOM', 'REVERSE', 'RIGHT', 'SIGN', 'SOURCELINE', 'SPACE', 'STREAM',
            'STRIP', 'SUBSTR', 'SUBWORD', 'SYMBOL', 'TIME', 'TRACE', 'TRANSLATE',
            'TRUNC', 'VALUE', 'VERIFY', 'WORD', 'WORDINDEX', 'WORDLENGTH', 'WORDPOS',
            'WORDS', 'X2B', 'X2C', 'X2D', 'XRANGE', 'USERID', 'SYSVAR', 'OUTTRAP',
            'LISTDSI', 'MSG', 'PROMPT', 'SYSCPUS', 'SYSDSN', 'SYSVAR', 'STORAGE',
            'MVSVAR', 'SETLANG',
            # REXX keywords and control structures
            'IF', 'THEN', 'ELSE', 'DO', 'END', 'SELECT', 'WHEN', 'OTHERWISE',
            'RETURN', 'EXIT', 'SIGNAL', 'CALL', 'PROCEDURE', 'EXPOSE', 'PARSE',
            'PULL', 'PUSH', 'QUEUE', 'SAY', 'NUMERIC', 'OPTIONS', 'INTERPRET',
            'ITERATE', 'LEAVE', 'NOP', 'DROP', 'UPPER',
            # Common ISPF/TSO functions
            'DATAID', 'DATASET', 'MEMBER', 'OPTION', 'MODE', 'STATS', 'ENQ',
            'DATALOC', 'DATALEN', 'MAXLEN', 'RECFM', 'LRECL', 'BLKSIZE'
        }
    
    def parse(self, source_code: str) -> Dict[str, List[str]]:
        """
        Extract dependencies from REXX source.
        
        Patterns detected:
        - CALL statements (program/subroutine dependencies)
        - Procedure definitions (label: PROCEDURE)
        - EXECIO statements (dataset references)
        - ADDRESS commands (TSO, ISPEXEC, ISREDIT, LINKMVS, etc.)
        - /* INCLUDE filename */ directives
        - External program calls (TSO commands, utilities)
        - Function calls (external functions)
        
        Args:
            source_code: REXX source code
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        # Normalize source code (remove comments, handle continuations)
        normalized_code = self._normalize_source(source_code)
        
        # Parse different dependency types
        call_deps = self.parse_call_statements(normalized_code)
        procedure_defs = self.parse_procedure_definitions(source_code)
        execio_deps = self.parse_execio_statements(normalized_code)
        address_envs = self.parse_address_commands(normalized_code)
        address_links = self.parse_address_link_commands(normalized_code)
        include_deps = self.parse_include_directives(source_code)
        tso_commands = self.parse_tso_commands(normalized_code)
        ispexec_commands = self.parse_ispexec_commands(normalized_code)
        function_calls = self.parse_function_calls(normalized_code, procedure_defs)
        
        result = {
            'calls': list(call_deps),
            'procedures': list(procedure_defs),
            'datasets': list(execio_deps),
            'address_environments': list(address_envs),
            'address_links': list(address_links),
            'includes': list(include_deps),
            'tso_commands': list(tso_commands),
            'ispexec_commands': list(ispexec_commands),
            'function_calls': list(function_calls)
        }
        
        return result
    
    def _normalize_source(self, source_code: str) -> str:
        """
        Normalize REXX source code by handling comments and continuations.
        
        Handles:
        - Block comments (/* ... */)
        - Line continuations (comma at end of line)
        - Multiple statements per line (semicolon separator)
        
        Args:
            source_code: Raw REXX source
            
        Returns:
            Normalized source code
        """
        # Remove block comments /* ... */
        # Handle multi-line comments
        normalized = re.sub(r'/\*.*?\*/', ' ', source_code, flags=re.DOTALL)
        
        # Handle line continuations (comma at end of line)
        lines = normalized.split('\n')
        continued_lines = []
        current_line = ''
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check if line ends with continuation character (comma)
            if line.rstrip().endswith(','):
                current_line += line.rstrip()[:-1] + ' '
            else:
                current_line += line
                continued_lines.append(current_line)
                current_line = ''
        
        # Add any remaining line
        if current_line:
            continued_lines.append(current_line)
        
        # Join lines and normalize whitespace
        normalized = ' '.join(continued_lines)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def parse_call_statements(self, source_code: str) -> Set[str]:
        """
        Extract program/subroutine names from CALL statements.
        
        Handles:
        - CALL PROGNAME
        - CALL 'PROGNAME'
        - CALL label
        - CALL PROGNAME arg1, arg2
        - result = PROGNAME(args) - function-style calls
        
        Args:
            source_code: Normalized REXX source
            
        Returns:
            Set of program/subroutine names
        """
        programs = set()
        
        # Explicit CALL statements
        for match in self.call_pattern.finditer(source_code):
            program_name = match.group(2)
            # Exclude built-in functions
            if program_name.upper() not in self.builtin_functions:
                programs.add(program_name)
        
        # Also look for function-style calls that might be external programs
        # Pattern: PROGNAME = FUNCTION(args) where FUNCTION looks like external
        func_call_pattern = re.compile(
            r'=\s*([A-Z][A-Z0-9_]*)\s*\(',
            re.IGNORECASE
        )
        for match in func_call_pattern.finditer(source_code):
            func_name = match.group(1)
            if func_name.upper() not in self.builtin_functions:
                programs.add(func_name)
        
        return programs
    
    def parse_procedure_definitions(self, source_code: str) -> Set[str]:
        """
        Extract procedure names from procedure definitions.
        
        Handles:
        - LABEL: PROCEDURE
        - LABEL:PROCEDURE
        - LABEL: (subroutine label at start of line)
        
        Args:
            source_code: Raw REXX source (not normalized, to preserve line structure)
            
        Returns:
            Set of procedure names
        """
        procedures = set()
        
        # Split into lines to check context
        lines = source_code.split('\n')
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('/*'):
                continue
            
            # Look for label at start of line (must be at least 2 chars to avoid false positives)
            match = re.match(r'^([A-Z0-9_]{2,})\s*:\s*(.*)$', line, re.IGNORECASE)
            if match:
                label = match.group(1)
                rest_of_line = match.group(2).strip()
                
                # It's a procedure if:
                # 1. Followed by PROCEDURE keyword, or
                # 2. Rest of line is empty or just a comment, or
                # 3. Next line starts with ARG, PARSE, or other procedure-like statements
                if (rest_of_line.upper().startswith('PROCEDURE') or
                    rest_of_line == '' or
                    rest_of_line.startswith('/*')):
                    procedures.add(label)
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip().upper()
                    if (next_line.startswith('ARG ') or
                        next_line.startswith('PARSE ') or
                        next_line.startswith('NUMERIC ') or
                        next_line.startswith('RETURN')):
                        procedures.add(label)
        
        return procedures
    
    def parse_execio_statements(self, source_code: str) -> Set[str]:
        """
        Extract dataset names from EXECIO statements.
        
        Handles:
        - EXECIO * DISKR DDNAME
        - EXECIO 1 DISKW OUTPUT
        - EXECIO 0 DISKR INPUT (OPEN
        
        Args:
            source_code: Normalized REXX source
            
        Returns:
            Set of dataset/DD names
        """
        datasets = set()
        
        for match in self.execio_pattern.finditer(source_code):
            dataset_name = match.group(1)
            datasets.add(dataset_name)
        
        return datasets
    
    def parse_address_commands(self, source_code: str) -> Set[str]:
        """
        Extract ADDRESS environment names.
        
        Handles:
        - ADDRESS TSO
        - ADDRESS ISPEXEC
        - ADDRESS ISREDIT
        - ADDRESS LINKMVS
        
        Args:
            source_code: Normalized REXX source
            
        Returns:
            Set of ADDRESS environment names
        """
        environments = set()
        
        for match in self.address_pattern.finditer(source_code):
            env_name = match.group(1)
            environments.add(env_name)
        
        return environments
    
    def parse_address_link_commands(self, source_code: str) -> Set[str]:
        """
        Extract program names from ADDRESS LINKMVS/LINKPGM commands.
        
        Handles:
        - ADDRESS LINKMVS 'PROGNAME'
        - ADDRESS LINKPGM 'PROG'
        
        Args:
            source_code: Normalized REXX source
            
        Returns:
            Set of program names
        """
        programs = set()
        
        for match in self.address_link_pattern.finditer(source_code):
            program_name = match.group(1)
            programs.add(program_name)
        
        return programs
    
    def parse_include_directives(self, source_code: str) -> Set[str]:
        """
        Extract file names from /* INCLUDE filename */ directives.
        
        Handles:
        - /* INCLUDE filename */
        - /* INCLUDE file.rex */
        
        Args:
            source_code: Raw REXX source (not normalized, to preserve comments)
            
        Returns:
            Set of include file names
        """
        includes = set()
        
        for match in self.include_pattern.finditer(source_code):
            include_name = match.group(1)
            includes.add(include_name)
        
        return includes
    
    def parse_tso_commands(self, source_code: str) -> Set[str]:
        """
        Extract TSO command names.
        
        Handles:
        - 'ALLOCATE ...'
        - 'LISTDSI ...'
        - 'LISTCAT ...'
        - etc.
        
        Args:
            source_code: Normalized REXX source
            
        Returns:
            Set of TSO command names
        """
        commands = set()
        
        for match in self.tso_command_pattern.finditer(source_code):
            # Extract the command name from the match
            command_text = match.group(0)
            # Remove quotes and get first word
            command_name = command_text.strip('\'"').split()[0]
            commands.add(command_name)
        
        return commands
    
    def parse_ispexec_commands(self, source_code: str) -> Set[str]:
        """
        Extract ISPEXEC command names.
        
        Handles:
        - 'LMINIT ...'
        - 'LMOPEN ...'
        - 'EDIT ...'
        - etc.
        
        Args:
            source_code: Normalized REXX source
            
        Returns:
            Set of ISPEXEC command names
        """
        commands = set()
        
        for match in self.ispexec_command_pattern.finditer(source_code):
            # Extract the command name from the match
            command_text = match.group(0)
            # Remove quotes and get first word
            command_name = command_text.strip('\'"').split()[0]
            commands.add(command_name)
        
        return commands
    
    def parse_function_calls(self, source_code: str, 
                            internal_procedures: Set[str]) -> Set[str]:
        """
        Extract external function calls.
        
        Filters out:
        - Built-in REXX functions
        - Internal procedures defined in the same file
        
        Args:
            source_code: Normalized REXX source
            internal_procedures: Set of procedure names defined in this file
            
        Returns:
            Set of external function names
        """
        functions = set()
        
        for match in self.function_call_pattern.finditer(source_code):
            function_name = match.group(1)
            function_upper = function_name.upper()
            
            # Exclude built-in functions and internal procedures
            if (function_upper not in self.builtin_functions and
                function_name not in internal_procedures):
                functions.add(function_name)
        
        return functions
    
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of dependency patterns this parser supports.
        
        Returns:
            List of pattern names
        """
        return [
            'CALL',
            'PROCEDURE',
            'EXECIO',
            'ADDRESS',
            'ADDRESS LINKMVS/LINKPGM',
            '/* INCLUDE */',
            'TSO COMMANDS',
            'ISPEXEC COMMANDS',
            'FUNCTION CALLS'
        ]
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser supports.
        
        Returns:
            List of file extensions
        """
        return self.supported_extensions
    
    def detect_program_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect REXX program boundaries using procedure definitions and function patterns.
        
        REXX programs are identified by:
        - Main program (everything not in procedures/functions)
        - Procedure definitions (label: PROCEDURE)
        - Function definitions (label: followed by function-like code)
        - Subroutine labels (labels followed by executable code)
        
        Args:
            source_code: REXX source code content
            file_path: Optional path to the source file
            
        Returns:
            List of ProgramBoundary objects representing detected programs
        """
        programs = []
        lines = source_code.splitlines()
        
        if not lines:
            return programs
        
        # Find all procedure and function definitions
        procedures = []
        functions = []
        subroutines = []
        
        # Track which lines are covered by procedures/functions
        covered_lines = set()
        
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith('/*'):
                continue
            
            # Check for explicit procedure definitions
            if self._is_explicit_procedure_definition(line):
                proc_name = self._extract_procedure_name(line)
                if proc_name:
                    end_line = self._find_procedure_end(lines, i - 1)  # Convert to 0-based
                    
                    procedure = ProgramBoundary(
                        program_name=proc_name,
                        start_line=i,
                        end_line=end_line,
                        program_type=ProgramType.PROCEDURE,
                        language="REXX",
                        entry_points=[proc_name],
                        file_path=file_path
                    )
                    procedures.append(procedure)
                    
                    # Mark lines as covered
                    for line_num in range(i, end_line + 1):
                        covered_lines.add(line_num)
            
            # Check for function-like labels (labels followed by function patterns)
            elif self._is_function_definition(line, lines, i - 1):
                func_name = self._extract_label_name(line)
                if func_name and func_name not in [p.program_name for p in procedures]:
                    end_line = self._find_function_end(lines, i - 1)
                    
                    function = ProgramBoundary(
                        program_name=func_name,
                        start_line=i,
                        end_line=end_line,
                        program_type=ProgramType.FUNCTION,
                        language="REXX",
                        entry_points=[func_name],
                        file_path=file_path
                    )
                    functions.append(function)
                    
                    # Mark lines as covered
                    for line_num in range(i, end_line + 1):
                        covered_lines.add(line_num)
            
            # Check for subroutine labels (labels that look like subroutines)
            elif self._is_subroutine_label(line, lines, i - 1):
                sub_name = self._extract_label_name(line)
                if (sub_name and 
                    sub_name not in [p.program_name for p in procedures] and
                    sub_name not in [f.program_name for f in functions] and
                    sub_name not in [s.program_name for s in subroutines]):
                    
                    end_line = self._find_subroutine_end(lines, i - 1)
                    
                    subroutine = ProgramBoundary(
                        program_name=sub_name,
                        start_line=i,
                        end_line=end_line,
                        program_type=ProgramType.PROCEDURE,  # Treat subroutines as procedures
                        language="REXX",
                        entry_points=[sub_name],
                        file_path=file_path
                    )
                    subroutines.append(subroutine)
                    
                    # Mark lines as covered
                    for line_num in range(i, end_line + 1):
                        covered_lines.add(line_num)
        
        # Create main program from uncovered lines
        main_lines = []
        for i in range(1, len(lines) + 1):
            if i not in covered_lines:
                main_lines.append(i)
        
        if main_lines:
            # Find contiguous ranges for main program
            # Group consecutive lines together
            main_ranges = []
            current_start = main_lines[0]
            current_end = main_lines[0]
            
            for line_num in main_lines[1:]:
                if line_num == current_end + 1:
                    current_end = line_num
                else:
                    # Gap found, close current range and start new one
                    main_ranges.append((current_start, current_end))
                    current_start = line_num
                    current_end = line_num
            
            # Add the last range
            main_ranges.append((current_start, current_end))
            
            # Create main program from the largest contiguous range
            if main_ranges:
                # Find the largest range (most lines)
                largest_range = max(main_ranges, key=lambda r: r[1] - r[0])
                main_start, main_end = largest_range
                
                main_name = self._extract_main_program_name(file_path) or "REXX_MAIN"
                
                main_program = ProgramBoundary(
                    program_name=main_name,
                    start_line=main_start,
                    end_line=main_end,
                    program_type=ProgramType.MAIN,
                    language="REXX",
                    entry_points=[main_name],
                    file_path=file_path
                )
                programs.append(main_program)
        
        # Add all detected procedures, functions, and subroutines
        programs.extend(procedures)
        programs.extend(functions)
        programs.extend(subroutines)
        
        # If no programs detected, create a default main program
        if not programs and lines:
            default_name = self._extract_main_program_name(file_path) or "REXX_MAIN"
            programs.append(ProgramBoundary(
                program_name=default_name,
                start_line=1,
                end_line=len(lines),
                program_type=ProgramType.MAIN,
                language="REXX",
                entry_points=[default_name],
                file_path=file_path
            ))
        
        return programs
    
    def _is_explicit_procedure_definition(self, line: str) -> bool:
        """Check if line defines an explicit REXX procedure with PROCEDURE keyword."""
        stripped = line.strip()
        # Match: LABEL: PROCEDURE or LABEL:PROCEDURE
        return bool(re.match(r'^[A-Z0-9_]+\s*:\s*PROCEDURE\b', stripped, re.IGNORECASE))
    
    def _is_function_definition(self, line: str, lines: List[str], line_index: int) -> bool:
        """
        Check if line defines a function (label followed by function-like patterns).
        
        A function is identified by:
        - A label at the start of line
        - Followed by ARG, PARSE ARG, or RETURN statements
        - Or followed by code that looks like it processes arguments
        """
        if not self._has_label(line):
            return False
        
        # Look at the next few lines for function patterns
        for i in range(line_index + 1, min(line_index + 5, len(lines))):
            next_line = lines[i].strip().upper()
            
            # Skip empty lines and comments
            if not next_line or next_line.startswith('/*'):
                continue
            
            # Function indicators
            if (next_line.startswith('ARG ') or
                next_line.startswith('PARSE ARG') or
                next_line.startswith('PARSE UPPER ARG') or
                next_line.startswith('PARSE VALUE') or
                'RETURN ' in next_line):
                return True
            
            # If we hit another label or procedure, stop looking
            if (self._has_label(lines[i]) or 
                'PROCEDURE' in next_line):
                break
        
        return False
    
    def _is_subroutine_label(self, line: str, lines: List[str], line_index: int) -> bool:
        """
        Check if line defines a subroutine (label followed by executable code).
        
        A subroutine is identified by:
        - A label at the start of line
        - Followed by executable REXX statements
        - Not already identified as a function or procedure
        """
        if not self._has_label(line):
            return False
        
        # Look at the next few lines for executable code
        for i in range(line_index + 1, min(line_index + 3, len(lines))):
            next_line = lines[i].strip().upper()
            
            # Skip empty lines and comments
            if not next_line or next_line.startswith('/*'):
                continue
            
            # Check for executable statements (not just declarations)
            if (next_line.startswith('SAY ') or
                next_line.startswith('IF ') or
                next_line.startswith('DO ') or
                next_line.startswith('SELECT') or
                next_line.startswith('CALL ') or
                next_line.startswith('ADDRESS ') or
                'EXECIO' in next_line or
                '=' in next_line):  # Assignment
                return True
            
            # If we hit another label, stop looking
            if self._has_label(lines[i]):
                break
        
        return False
    
    def _has_label(self, line: str) -> bool:
        """Check if line has a label at the beginning."""
        stripped = line.strip()
        if not stripped:
            return False
        
        # Match: LABEL: (with optional whitespace)
        match = re.match(r'^([A-Z0-9_]+)\s*:', stripped, re.IGNORECASE)
        if match:
            label = match.group(1).upper()
            # Exclude REXX keywords that might look like labels
            rexx_keywords = {'IF', 'THEN', 'ELSE', 'DO', 'END', 'SELECT', 'WHEN', 'OTHERWISE'}
            return label not in rexx_keywords
        
        return False
    
    def _extract_label_name(self, line: str) -> Optional[str]:
        """Extract label name from a line with a label."""
        stripped = line.strip()
        match = re.match(r'^([A-Z0-9_]+)\s*:', stripped, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_procedure_name(self, line: str) -> Optional[str]:
        """Extract procedure name from REXX procedure definition."""
        stripped = line.strip()
        match = re.match(r'^([A-Z0-9_]+)\s*:\s*PROCEDURE', stripped, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _find_procedure_end(self, lines: List[str], start_index: int) -> int:
        """Find the end line of a REXX procedure."""
        # Look for RETURN statement or next procedure/function
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip().upper()
            
            # End on RETURN statement
            if line.startswith('RETURN'):
                return i + 1  # Convert to 1-based line numbers
            
            # End on next procedure or function definition
            if (self._is_explicit_procedure_definition(lines[i]) or
                self._has_label(lines[i])):
                return i  # Previous line was the end
        
        return len(lines)
    
    def _find_function_end(self, lines: List[str], start_index: int) -> int:
        """Find the end line of a REXX function."""
        # Similar to procedure end, but look for RETURN with value
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip().upper()
            
            # End on RETURN statement
            if line.startswith('RETURN'):
                return i + 1
            
            # End on next label
            if self._has_label(lines[i]):
                return i
        
        return len(lines)
    
    def _find_subroutine_end(self, lines: List[str], start_index: int) -> int:
        """Find the end line of a REXX subroutine."""
        # Look for RETURN, EXIT, or next label
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip().upper()
            
            # End on RETURN or EXIT
            if line.startswith('RETURN') or line.startswith('EXIT'):
                return i + 1
            
            # End on next label
            if self._has_label(lines[i]):
                return i
        
        return len(lines)
    
    def _extract_main_program_name(self, file_path: Optional[str]) -> Optional[str]:
        """Extract main program name from file path."""
        if file_path:
            import os
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            # Clean up the name to be a valid REXX identifier
            return re.sub(r'[^A-Z0-9_]', '_', base_name.upper())
        return None
    
    def parse_with_program_detection(self, source_code: str, file_path: Optional[str] = None) -> ProgramParseResult:
        """
        Parse REXX source code to detect programs and extract dependencies.
        
        Args:
            source_code: REXX source code content
            file_path: Optional path to the source file
            
        Returns:
            ProgramParseResult with detected programs and dependencies
        """
        programs = self.detect_program_boundaries(source_code, file_path)
        dependencies = self._extract_program_level_dependencies(source_code, programs)
        
        total_lines = len(source_code.splitlines())
        
        result = ProgramParseResult(
            file_path=file_path or "unknown",
            language="REXX",
            programs=programs,
            dependencies=dependencies,
            total_lines=total_lines
        )
        
        return result
    
    def _extract_program_level_dependencies(self, source_code: str, programs: List[ProgramBoundary]) -> Dict[str, List[str]]:
        """
        Extract dependencies for each detected program based on their line boundaries.
        
        Args:
            source_code: REXX source code content
            programs: List of detected program boundaries
            
        Returns:
            Dictionary mapping program names to lists of dependencies
        """
        dependencies = {}
        lines = source_code.splitlines()
        
        for program in programs:
            program_dependencies = []
            
            # Extract the source code for this program
            start_idx = max(0, program.start_line - 1)  # Convert to 0-based
            end_idx = min(len(lines), program.end_line)
            program_source = '\n'.join(lines[start_idx:end_idx])
            
            # Parse dependencies from this program's source
            program_deps = self.parse(program_source)
            
            # Flatten all dependency types into a single list
            all_deps = []
            for dep_type, dep_list in program_deps.items():
                all_deps.extend(dep_list)
            
            dependencies[program.program_name] = list(set(all_deps))  # Remove duplicates
        
        return dependencies
