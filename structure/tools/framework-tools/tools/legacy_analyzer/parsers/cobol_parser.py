"""COBOL dependency parser."""

import re
import os
from typing import Dict, List, Set, Tuple, Optional
from .base_parser import BaseDependencyParser
from .cobol_complexity_calculator import COBOLComplexityCalculator
from ..analysis.copybook_analyzer import CopybookAnalyzer
from ..models.dependency import Dependency, DependencyType


class COBOLDependencyParser(BaseDependencyParser):
    """Parses COBOL source for dependencies."""
    
    def __init__(self):
        """Initialize COBOL parser with regex patterns and complexity calculator."""
        super().__init__()
        
        # Initialize complexity calculator
        self.complexity_calculator = COBOLComplexityCalculator()
        
        # Initialize copybook analyzer
        self.copybook_analyzer = CopybookAnalyzer()
        
        # Track processed copybooks to prevent circular references
        self._processed_copybooks = set()
        self._copybook_search_paths = []
        # COPY statement patterns
        # Must start with whitespace or beginning of line to avoid matching words ending in COPY
        # Handles both quoted and unquoted copybook names:
        # - COPY COPYBOOK1
        # - COPY 'COPYBOOK1'
        # - COPY "COPYBOOK1"
        # - COPY COPYBOOK1 IN LIBRARY1
        # - COPY 'COPYBOOK1' IN LIBRARY1
        self.copy_pattern = re.compile(
            r'(?:^|\s)COPY\s+(?:["\']([A-Z0-9\-]+)["\']|([A-Z0-9\-]+))(?:\s+(?:IN|OF)\s+([A-Z0-9\-]+))?(?:\s+REPLACING\s+.*?)?\.?',
            re.IGNORECASE | re.MULTILINE
        )
        
        # CALL statement patterns
        self.call_literal_pattern = re.compile(
            r'\bCALL\s+["\']([A-Z0-9\-]+)["\']',
            re.IGNORECASE
        )
        self.call_identifier_pattern = re.compile(
            r'\bCALL\s+([A-Z0-9\-]+)(?:\s+USING|\s+RETURNING|\s*$)',
            re.IGNORECASE
        )
        
        # CICS patterns
        self.cics_link_pattern = re.compile(
            r'EXEC\s+CICS\s+LINK\s+PROGRAM\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        self.cics_start_pattern = re.compile(
            r'EXEC\s+CICS\s+START\s+TRANSID\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        self.cics_read_pattern = re.compile(
            r'EXEC\s+CICS\s+READ\s+(?:FILE|DATASET)\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        self.cics_write_pattern = re.compile(
            r'EXEC\s+CICS\s+WRITE\s+(?:FILE|DATASET)\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        self.cics_rewrite_pattern = re.compile(
            r'EXEC\s+CICS\s+REWRITE\s+(?:FILE|DATASET)\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        self.cics_delete_pattern = re.compile(
            r'EXEC\s+CICS\s+DELETE\s+(?:FILE|DATASET)\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        self.cics_browse_pattern = re.compile(
            r'EXEC\s+CICS\s+(?:STARTBR|READNEXT|READPREV|ENDBR)\s+(?:FILE|DATASET)\s*\(\s*["\']?([A-Z0-9\-]+)["\']?\s*\)',
            re.IGNORECASE
        )
        
        # SQL patterns
        self.sql_include_pattern = re.compile(
            r'EXEC\s+SQL\s+INCLUDE\s+([A-Z0-9\-]+)',
            re.IGNORECASE
        )
        self.sql_table_pattern = re.compile(
            r'(?:FROM|INTO|UPDATE|JOIN)\s+([A-Z0-9_]+)',
            re.IGNORECASE
        )
        
        # Sequential I/O patterns
        self.open_pattern = re.compile(
            r'\bOPEN\s+(INPUT|OUTPUT|I-O|EXTEND)\s+([A-Z0-9\-]+)',
            re.IGNORECASE
        )
        self.seq_read_pattern = re.compile(
            r'\bREAD\s+([A-Z0-9\-]+)\b',
            re.IGNORECASE
        )
        self.seq_write_pattern = re.compile(
            r'\bWRITE\s+([A-Z0-9\-]+)\b',
            re.IGNORECASE
        )

        # Variable declaration with VALUE pattern
        # Matches: 05 WS-PGM-NAME PIC X(08) VALUE 'PROGRAM1'.
        # Works with both multiline and single-line normalized code
        self.variable_value_pattern = re.compile(
            r'\b\d+\s+([A-Z0-9\-]+)\s+PIC\s+X\(\d+\)\s+VALUE\s+["\']([A-Z0-9\-]+)["\']',
            re.IGNORECASE
        )
    
    def parse(self, source_code: str, source_file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Extract dependencies from COBOL source.
        
        Patterns detected:
        - COPY statements: COPY COPYBOOK1.
        - CALL statements: CALL 'PROGRAM1' or CALL WS-PROGRAM-NAME
        - EXEC CICS LINK: EXEC CICS LINK PROGRAM('PROG1') or PROGRAM(WS-PGM-NAME)
        - EXEC SQL INCLUDE: EXEC SQL INCLUDE SQLCA
        
        Handles dynamic calls by resolving variable names to their VALUE declarations.
        
        Args:
            source_code: COBOL source code
            source_file_path: Optional path to source file (enables copybook analysis)
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        # Normalize source code
        normalized_code = self._normalize_source(source_code)
        
        # Extract variable-to-value mappings for dynamic call resolution
        variable_values = self.extract_variable_values(normalized_code)
        
        # Parse different dependency types
        copybooks = self.parse_copy_statements(normalized_code)
        calls = self.parse_call_statements(normalized_code, variable_values)
        cics_deps = self.parse_cics_statements(normalized_code, variable_values)
        sql_deps = self.parse_sql_statements(normalized_code)
        seq_io = self.parse_sequential_io(normalized_code)
        
        # Build operation-specific file lists (deduplicated)
        file_ops = cics_deps.get('file_operations', [])
        cics_read_files = list({op['name'] for op in file_ops if op.get('operation') == 'CICS_READ'})
        cics_write_files = list({op['name'] for op in file_ops if op.get('operation') == 'CICS_WRITE'})
        cics_rewrite_files = list({op['name'] for op in file_ops if op.get('operation') == 'CICS_REWRITE'})
        cics_delete_files = list({op['name'] for op in file_ops if op.get('operation') == 'CICS_DELETE'})
        cics_browse_files = list({op['name'] for op in file_ops if op.get('operation') == 'CICS_BROWSE'})

        return {
            'copybooks': list(copybooks),
            'calls': list(calls),
            'cics_links': cics_deps.get('programs', []),
            'cics_transactions': cics_deps.get('transactions', []),
            'cics_files': cics_deps.get('files', []),
            'cics_read_files': cics_read_files,
            'cics_write_files': cics_write_files,
            'cics_rewrite_files': cics_rewrite_files,
            'cics_delete_files': cics_delete_files,
            'cics_browse_files': cics_browse_files,
            'sql_includes': sql_deps.get('includes', []),
            'sql_tables': sql_deps.get('tables', []),
            'sequential_files': seq_io.get('files', [])
        }
    
    def _normalize_source(self, source_code: str) -> str:
        """
        Normalize COBOL source code by handling format variations.
        
        Handles:
        - Fixed format (columns 7-72)
        - Free format
        - Comments (* or / in column 7, or line starting with *)
        - Continuations (- in column 7)
        
        Args:
            source_code: Raw COBOL source
            
        Returns:
            Normalized source code
        """
        lines = source_code.split('\n')
        normalized_lines = []
        continuation_buffer = ""
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check for free-format comment (line starting with * or / after whitespace)
            # But only if it's not in fixed format position (column 7)
            stripped = line.lstrip()
            if stripped and stripped[0] in ('*', '/'):
                # Check if this is truly a comment line or if * is in column 7
                # If line is long enough for fixed format, check column 7
                if len(line) < 7 or line[6] not in ('*', '/'):
                    # This is a free-format comment at the start of the line
                    continue
            
            # Check if this is fixed format (line length suggests columns)
            if len(line) >= 7:
                # Check for comment in column 7
                if line[6] in ('*', '/'):
                    continue
                
                # Check for continuation in column 7
                if line[6] == '-':
                    # This is a continuation line
                    if len(line) > 7:
                        continuation_buffer += line[7:72] if len(line) >= 72 else line[7:]
                    continue
                
                # Extract code from columns 8-72 for fixed format
                if len(line) >= 8:
                    code_part = line[7:72] if len(line) >= 72 else line[7:]
                else:
                    code_part = line
            else:
                # Free format or short line
                code_part = line
            
            # If we have a continuation buffer, append current line to it
            if continuation_buffer:
                normalized_lines.append(continuation_buffer + code_part)
                continuation_buffer = ""
            else:
                normalized_lines.append(code_part)
        
        # Join lines and remove inline comments
        normalized = ' '.join(normalized_lines)
        
        # Remove inline comments (after *)
        # But be careful not to remove * in strings
        return normalized
    
    def parse_copy_statements(self, source_code: str) -> Set[str]:
        """
        Extract copybook names from COPY statements.
        
        Handles:
        - COPY COPYBOOK1.
        - COPY 'COPYBOOK1'.
        - COPY "COPYBOOK1".
        - COPY COPYBOOK1 IN LIBRARY1.
        - COPY 'COPYBOOK1' IN LIBRARY1.
        - COPY COPYBOOK1 OF LIBRARY1.
        - COPY COPYBOOK1 REPLACING ...
        
        Args:
            source_code: Normalized COBOL source
            
        Returns:
            Set of copybook names
        """
        copybooks = set()
        
        for match in self.copy_pattern.finditer(source_code):
            # Group 1: quoted copybook name, Group 2: unquoted copybook name
            copybook_name = match.group(1) if match.group(1) else match.group(2)
            library_name = match.group(3) if match.lastindex >= 3 else None
            
            # If library is specified, include it in the name
            if library_name:
                copybooks.add(f"{library_name}.{copybook_name}")
            else:
                copybooks.add(copybook_name)
        
        return copybooks
    
    def extract_variable_values(self, source_code: str) -> Dict[str, str]:
        """
        Extract variable-to-value mappings from WORKING-STORAGE.
        
        Finds patterns like:
        05 WS-PGM-NAME PIC X(08) VALUE 'PROGRAM1'.
        
        Args:
            source_code: Normalized COBOL source
            
        Returns:
            Dictionary mapping variable names to their VALUES
        """
        variable_values = {}
        
        for match in self.variable_value_pattern.finditer(source_code):
            variable_name = match.group(1)
            value = match.group(2)
            variable_values[variable_name] = value
        
        return variable_values
    
    def parse_call_statements(self, source_code: str, variable_values: Dict[str, str] = None) -> Set[str]:
        """
        Extract program names from CALL statements.
        
        Handles:
        - CALL 'PROGRAM1' (static call with literal)
        - CALL "PROGRAM1" (static call with literal)
        - CALL PROGRAM-NAME (dynamic call with identifier - resolved via variable_values)
        
        Args:
            source_code: Normalized COBOL source
            variable_values: Dictionary mapping variable names to their VALUES
            
        Returns:
            Set of program names
        """
        if variable_values is None:
            variable_values = {}
        
        programs = set()
        
        # Extract literal calls (static)
        for match in self.call_literal_pattern.finditer(source_code):
            program_name = match.group(1)
            programs.add(program_name)
        
        # Extract identifier calls (dynamic) and resolve them
        for match in self.call_identifier_pattern.finditer(source_code):
            identifier = match.group(1)
            # Try to resolve the identifier to its VALUE
            if identifier in variable_values:
                program_name = variable_values[identifier]
                programs.add(program_name)
            # If not resolved, we could optionally add the identifier itself
            # but that would create false dependencies
        
        return programs
    
    def parse_cics_statements(self, source_code: str, variable_values: Dict[str, str] = None) -> Dict[str, List[str]]:
        """
        Extract CICS-related dependencies.
        
        Handles:
        - EXEC CICS LINK PROGRAM('PROG1') or PROGRAM(WS-PGM-NAME)
        - EXEC CICS START TRANSID('TRN1') or TRANSID(WS-TRANS-ID)
        - EXEC CICS READ FILE('FILE1') or FILE(WS-FILE-NAME)
        - EXEC CICS WRITE DATASET('DS1')
        
        Resolves variable names to their VALUES when possible.
        
        Args:
            source_code: Normalized COBOL source
            variable_values: Dictionary mapping variable names to their VALUES
            
        Returns:
            Dictionary with programs, transactions, and files
        """
        if variable_values is None:
            variable_values = {}
        
        programs = set()
        transactions = set()
        files = set()
        file_operations = []
        
        # Extract LINK programs
        for match in self.cics_link_pattern.finditer(source_code):
            identifier = match.group(1)
            # Try to resolve variable to its VALUE
            if identifier in variable_values:
                programs.add(variable_values[identifier])
            else:
                # If it's not a variable, it's a literal (quotes already removed by regex)
                programs.add(identifier)
        
        # Extract transaction IDs
        for match in self.cics_start_pattern.finditer(source_code):
            identifier = match.group(1)
            if identifier in variable_values:
                transactions.add(variable_values[identifier])
            else:
                transactions.add(identifier)
        
        # Extract file/dataset names from all five CICS file patterns
        cics_file_patterns = [
            (self.cics_read_pattern, 'CICS_READ'),
            (self.cics_write_pattern, 'CICS_WRITE'),
            (self.cics_rewrite_pattern, 'CICS_REWRITE'),
            (self.cics_delete_pattern, 'CICS_DELETE'),
            (self.cics_browse_pattern, 'CICS_BROWSE'),
        ]
        
        for pattern, op_type in cics_file_patterns:
            for match in pattern.finditer(source_code):
                identifier = match.group(1)
                if identifier in variable_values:
                    resolved = variable_values[identifier]
                else:
                    resolved = identifier
                files.add(resolved)
                file_operations.append({'name': resolved, 'operation': op_type})
        
        return {
            'programs': list(programs),
            'transactions': list(transactions),
            'files': list(files),
            'file_operations': file_operations
        }
    
    def parse_sql_statements(self, source_code: str) -> Dict[str, List[str]]:
        """
        Extract SQL-related dependencies.
        
        Handles:
        - EXEC SQL INCLUDE SQLCA
        - EXEC SQL INCLUDE MEMBER1
        - Table names from SELECT/INSERT/UPDATE/DELETE
        
        Args:
            source_code: Normalized COBOL source
            
        Returns:
            Dictionary with includes and tables
        """
        includes = set()
        tables = set()
        
        # Extract SQL includes
        for match in self.sql_include_pattern.finditer(source_code):
            includes.add(match.group(1))
        
        # Extract table names from SQL statements
        # Look for SQL blocks
        sql_blocks = re.finditer(
            r'EXEC\s+SQL\s+(.*?)\s+END-EXEC',
            source_code,
            re.IGNORECASE | re.DOTALL
        )
        
        for sql_block in sql_blocks:
            sql_text = sql_block.group(1)
            # Extract table names
            for match in self.sql_table_pattern.finditer(sql_text):
                table_name = match.group(1)
                # Filter out SQL keywords
                if table_name.upper() not in ('SELECT', 'WHERE', 'ORDER', 'GROUP', 'HAVING'):
                    tables.add(table_name)
        
        return {
            'includes': list(includes),
            'tables': list(tables)
        }
    
    def parse_sequential_io(self, source_code: str) -> Dict[str, any]:
        """
        Extract sequential I/O operations from COBOL source code.

        Detects OPEN INPUT/OUTPUT/I-O/EXTEND statements and standalone
        READ/WRITE verbs, tracking which files were opened with which mode.

        Args:
            source_code: Normalized COBOL source code

        Returns:
            Dictionary with:
                files: list of all file names found
                file_operations: list of dicts with 'name' and 'operation' keys
        """
        files = set()
        file_operations = []
        open_modes = {}  # filename -> mode (INPUT, OUTPUT, I-O, EXTEND)

        # First pass: collect OPEN statements and record modes
        for match in self.open_pattern.finditer(source_code):
            mode = match.group(1).upper()
            filename = match.group(2).upper()
            files.add(filename)
            open_modes[filename] = mode
            file_operations.append({'name': filename, 'operation': mode})

        # Second pass: collect READ statements and resolve operation type
        for match in self.seq_read_pattern.finditer(source_code):
            filename = match.group(1).upper()
            files.add(filename)
            mode = open_modes.get(filename)
            if mode == 'INPUT':
                operation = 'READ'
            elif mode == 'I-O':
                operation = 'READ'
            else:
                operation = 'UNKNOWN'
            file_operations.append({'name': filename, 'operation': operation})

        # Third pass: collect WRITE statements and resolve operation type
        for match in self.seq_write_pattern.finditer(source_code):
            filename = match.group(1).upper()
            files.add(filename)
            mode = open_modes.get(filename)
            if mode in ('OUTPUT', 'EXTEND'):
                operation = 'WRITE'
            elif mode == 'I-O':
                operation = 'WRITE'
            else:
                operation = 'UNKNOWN'
            file_operations.append({'name': filename, 'operation': operation})

        return {
            'files': list(files),
            'file_operations': file_operations
        }

    def get_supported_patterns(self) -> List[str]:
        """
        Get list of dependency patterns this parser supports.
        
        Returns:
            List of pattern names
        """
        return [
            'COPY',
            'CALL',
            'EXEC CICS LINK',
            'EXEC CICS START',
            'EXEC CICS READ/WRITE',
            'EXEC SQL INCLUDE',
            'SQL TABLES'
        ]
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser supports.
        
        Returns:
            List of file extensions
        """
        return ['.cbl', '.cob', '.cobol', '.cpy']
    
    def set_copybook_search_paths(self, paths: List[str]):
        """
        Set search paths for locating copybooks.
        
        Args:
            paths: List of directory paths to search for copybooks
        """
        self.copybook_search_paths = [os.path.abspath(path) for path in paths]
    
    def parse_with_copybook_analysis(self, source_code: str, source_file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Enhanced parse method that includes copybook content analysis.
        
        Args:
            source_code: COBOL source code
            source_file_path: Path to the source file (used for copybook resolution)
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names,
            including dependencies found within copybooks
        """
        # Reset processed copybooks for each new parse
        self._processed_copybooks = set()
        
        # Set default search paths if source file path is provided
        if source_file_path and not hasattr(self, 'copybook_search_paths'):
            source_dir = os.path.dirname(os.path.abspath(source_file_path))
            self.copybook_search_paths = [source_dir]
        
        # Get basic dependencies
        dependencies = self.parse(source_code)
        
        # Analyze copybooks for executable code and nested dependencies
        copybook_dependencies = self._analyze_copybooks(dependencies.get('copybooks', []), source_file_path)
        
        # Merge copybook dependencies with main dependencies
        for dep_type, deps in copybook_dependencies.items():
            if dep_type in dependencies:
                # Combine and deduplicate
                combined = list(set(dependencies[dep_type] + deps))
                dependencies[dep_type] = combined
            else:
                dependencies[dep_type] = deps
        
        return dependencies
    
    def _analyze_copybooks(self, copybook_names: List[str], source_file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Analyze copybooks for executable code and extract dependencies.
        
        Args:
            copybook_names: List of copybook names to analyze
            source_file_path: Path to the source file (for relative path resolution)
            
        Returns:
            Dictionary of dependencies found within copybooks
        """
        copybook_dependencies = {
            'copybook_calls': [],
            'copybook_cics_links': [],
            'copybook_cics_transactions': [],
            'copybook_cics_files': [],
            'copybook_sql_includes': [],
            'copybook_sql_tables': [],
            'nested_copybooks': []
        }
        
        for copybook_name in copybook_names:
            # Skip if already processed (circular reference prevention)
            if copybook_name in self._processed_copybooks:
                continue
            
            self._processed_copybooks.add(copybook_name)
            
            # Find copybook file
            copybook_path = self._find_copybook_file(copybook_name, source_file_path)
            if not copybook_path:
                continue
            
            try:
                # Analyze copybook content
                analysis_result = self.copybook_analyzer.analyze_content(
                    copybook_path, 'COBOL'
                )
                
                # Always parse copybook content for dependencies (both executable and data copybooks can include other copybooks)
                with open(copybook_path, 'r', encoding='utf-8', errors='ignore') as f:
                    copybook_content = f.read()
                
                # Parse copybook content for dependencies
                copybook_deps = self.parse(copybook_content)
                
                # If copybook has executable code, add its executable dependencies
                if analysis_result.has_executable_code:
                    # Add to copybook-specific dependency categories
                    copybook_dependencies['copybook_calls'].extend(copybook_deps.get('calls', []))
                    copybook_dependencies['copybook_cics_links'].extend(copybook_deps.get('cics_links', []))
                    copybook_dependencies['copybook_cics_transactions'].extend(copybook_deps.get('cics_transactions', []))
                    copybook_dependencies['copybook_cics_files'].extend(copybook_deps.get('cics_files', []))
                    copybook_dependencies['copybook_sql_includes'].extend(copybook_deps.get('sql_includes', []))
                    copybook_dependencies['copybook_sql_tables'].extend(copybook_deps.get('sql_tables', []))
                
                # Handle nested copybooks recursively (regardless of whether current copybook is executable)
                nested_copybooks = copybook_deps.get('copybooks', [])
                if nested_copybooks:
                    copybook_dependencies['nested_copybooks'].extend(nested_copybooks)
                    
                    # Recursively analyze nested copybooks
                    nested_deps = self._analyze_copybooks(nested_copybooks, copybook_path)
                    
                    # Merge nested dependencies
                    for dep_type, deps in nested_deps.items():
                        copybook_dependencies[dep_type].extend(deps)
                
            except (IOError, OSError) as e:
                # Log error but continue processing other copybooks
                print(f"Warning: Could not analyze copybook {copybook_name}: {e}")
                continue
        
        # Remove duplicates from all dependency lists
        for dep_type in copybook_dependencies:
            copybook_dependencies[dep_type] = list(set(copybook_dependencies[dep_type]))
        
        return copybook_dependencies
    
    def _find_copybook_file(self, copybook_name: str, source_file_path: Optional[str] = None) -> Optional[str]:
        """
        Find the actual file path for a copybook.
        
        Args:
            copybook_name: Name of the copybook (may include library prefix)
            source_file_path: Path to the source file (for relative resolution)
            
        Returns:
            Full path to copybook file if found, None otherwise
        """
        # Handle library.copybook format
        if '.' in copybook_name:
            library, copybook = copybook_name.split('.', 1)
            # For now, just use the copybook name
            copybook_name = copybook
        
        # Common copybook extensions
        extensions = ['.cpy', '.copy', '.inc', '.cbl', '.cob', '']
        
        # Build search paths
        search_paths = []
        
        # Add configured search paths
        if hasattr(self, 'copybook_search_paths'):
            search_paths.extend(self.copybook_search_paths)
        
        # Add source file directory if available
        if source_file_path:
            source_dir = os.path.dirname(os.path.abspath(source_file_path))
            if source_dir not in search_paths:
                search_paths.append(source_dir)
            
            # Also try common copybook subdirectories
            for subdir in ['cpy', 'copy', 'copybook', 'include']:
                copybook_dir = os.path.join(source_dir, subdir)
                if os.path.isdir(copybook_dir) and copybook_dir not in search_paths:
                    search_paths.append(copybook_dir)
        
        # Search for copybook file
        for search_path in search_paths:
            for ext in extensions:
                candidate_path = os.path.join(search_path, copybook_name + ext)
                if os.path.isfile(candidate_path):
                    return candidate_path
        
        return None
    
    def detect_circular_copybook_references(self, source_code: str, source_file_path: Optional[str] = None) -> List[List[str]]:
        """
        Detect circular references in copybook includes.
        
        Args:
            source_code: COBOL source code
            source_file_path: Path to the source file
            
        Returns:
            List of circular reference chains (each chain is a list of copybook names)
        """
        def build_dependency_graph(copybook_name: str, visited: Set[str], path: List[str]) -> List[List[str]]:
            """Recursively build dependency graph and detect cycles."""
            if copybook_name in visited:
                # Found a cycle
                cycle_start = path.index(copybook_name)
                return [path[cycle_start:] + [copybook_name]]
            
            copybook_path = self._find_copybook_file(copybook_name, source_file_path)
            if not copybook_path:
                return []
            
            try:
                with open(copybook_path, 'r', encoding='utf-8', errors='ignore') as f:
                    copybook_content = f.read()
                
                # Parse copybook for nested COPY statements
                nested_copybooks = self.parse_copy_statements(copybook_content)
                
                cycles = []
                for nested_copybook in nested_copybooks:
                    new_visited = visited.copy()
                    new_visited.add(copybook_name)
                    new_path = path + [copybook_name]
                    
                    cycles.extend(build_dependency_graph(nested_copybook, new_visited, new_path))
                
                return cycles
                
            except (IOError, OSError):
                return []
        
        # Get top-level copybooks
        top_level_copybooks = self.parse_copy_statements(source_code)
        
        all_cycles = []
        for copybook in top_level_copybooks:
            cycles = build_dependency_graph(copybook, set(), [])
            all_cycles.extend(cycles)
        
        return all_cycles
    
    def get_enhanced_dependencies(self, source_code: str, source_file_path: Optional[str] = None) -> Dict[str, any]:
        """
        Get comprehensive dependency analysis including copybook analysis.
        
        Args:
            source_code: COBOL source code
            source_file_path: Path to the source file
            
        Returns:
            Dictionary containing:
            - dependencies: Standard dependency mapping
            - copybook_analysis: List of copybook analysis results
            - circular_references: List of circular reference chains
            - executable_copybooks: List of copybooks containing executable code
        """
        # Get enhanced dependencies with copybook analysis
        dependencies = self.parse_with_copybook_analysis(source_code, source_file_path)
        
        # Analyze individual copybooks
        copybook_analysis_results = []
        executable_copybooks = []
        
        copybook_names = dependencies.get('copybooks', [])
        for copybook_name in copybook_names:
            copybook_path = self._find_copybook_file(copybook_name, source_file_path)
            if copybook_path:
                try:
                    analysis_result = self.copybook_analyzer.analyze_content(
                        copybook_path, 'COBOL'
                    )
                    copybook_analysis_results.append(analysis_result)
                    
                    if analysis_result.has_executable_code:
                        executable_copybooks.append(copybook_name)
                        
                except (IOError, OSError):
                    continue
        
        # Detect circular references
        circular_references = self.detect_circular_copybook_references(source_code, source_file_path)
        
        return {
            'dependencies': dependencies,
            'copybook_analysis': copybook_analysis_results,
            'circular_references': circular_references,
            'executable_copybooks': executable_copybooks
        }
    
    def parse_with_program_detection(self, source_code: str, file_path: Optional[str] = None):
        """
        Parse COBOL source code to detect individual programs and their dependencies.
        
        This method implements program-level dependency tracking for COBOL files,
        identifying individual programs using PROGRAM-ID statements and extracting
        dependencies separately for each program.
        
        Args:
            source_code: COBOL source code content
            file_path: Optional path to the source file
            
        Returns:
            ProgramParseResult with detected programs and their dependencies
        """
        from ..models.program_boundary import ProgramParseResult
        
        # Detect program boundaries using PROGRAM-ID statements
        programs = self.detect_program_boundaries(source_code, file_path)
        
        # Extract dependencies for each detected program
        program_dependencies = self._extract_program_level_dependencies(source_code, programs)
        
        # Calculate total lines for coverage statistics
        total_lines = len(source_code.splitlines())
        
        return ProgramParseResult(
            file_path=file_path or "unknown",
            language="COBOL",
            programs=programs,
            dependencies=program_dependencies,
            total_lines=total_lines
        )
    
    def detect_program_boundaries(self, source_code: str, file_path: Optional[str] = None):
        """
        Detect COBOL program boundaries using PROGRAM-ID statements.
        
        COBOL programs are identified by:
        - PROGRAM-ID statements that define the program name
        - END PROGRAM statements that close nested programs
        - File boundaries for main programs
        
        Args:
            source_code: COBOL source code content
            file_path: Optional path to the source file
            
        Returns:
            List of ProgramBoundary objects representing detected programs
        """
        from ..models.program_boundary import ProgramBoundary, ProgramType
        
        programs = []
        lines = source_code.splitlines()
        
        current_program = None
        program_stack = []  # For nested programs
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith('*'):
                continue
            
            # Check for PROGRAM-ID statement
            if 'PROGRAM-ID' in line_upper:
                program_name = self._extract_program_name_from_program_id(line)
                if program_name:
                    # End previous program if exists and not nested
                    if current_program and not program_stack:
                        current_program.end_line = i - 1
                        programs.append(current_program)
                    
                    # Determine program type
                    program_type = ProgramType.NESTED if program_stack else ProgramType.MAIN
                    
                    # Create new program boundary
                    new_program = ProgramBoundary(
                        program_name=program_name,
                        start_line=i,
                        end_line=len(lines),  # Will be updated when we find the end
                        program_type=program_type,
                        language="COBOL",
                        entry_points=[program_name],
                        file_path=file_path,
                        confidence_level=0.95  # High confidence for PROGRAM-ID detection
                    )
                    
                    if program_stack:
                        # This is a nested program
                        program_stack.append(new_program)
                        programs.append(new_program)
                    else:
                        # This is a main program
                        current_program = new_program
                        program_stack = [new_program]
            
            # Check for END PROGRAM statement
            elif 'END PROGRAM' in line_upper:
                if program_stack:
                    ending_program = program_stack.pop()
                    ending_program.end_line = i
                    
                    if not program_stack:
                        # Ended the main program
                        current_program = None
        
        # Close the last program if it exists
        if current_program:
            programs.append(current_program)
        
        # If no programs were detected but we have content, create a default main program
        if not programs and lines:
            default_name = self._extract_default_program_name(file_path) or "COBOL_MAIN"
            programs.append(ProgramBoundary(
                program_name=default_name,
                start_line=1,
                end_line=len(lines),
                program_type=ProgramType.MAIN,
                language="COBOL",
                entry_points=[default_name],
                file_path=file_path,
                confidence_level=0.7  # Lower confidence for default detection
            ))
        
        return programs
    
    def _extract_program_level_dependencies(self, source_code: str, programs):
        """
        Extract dependencies for each detected program based on their line boundaries.
        
        Args:
            source_code: COBOL source code content
            programs: List of detected program boundaries
            
        Returns:
            Dictionary mapping program names to their dependency dictionaries
        """
        program_dependencies = {}
        lines = source_code.splitlines()
        
        for program in programs:
            # Extract the source code for this specific program
            program_lines = []
            start_idx = max(0, program.start_line - 1)  # Convert to 0-based index
            end_idx = min(len(lines), program.end_line)
            
            for line_idx in range(start_idx, end_idx):
                program_lines.append(lines[line_idx])
            
            program_source = '\n'.join(program_lines)
            
            # Parse dependencies for this program's source
            program_deps = self.parse(program_source)
            
            # Store the full dependency dictionary
            program_dependencies[program.program_name] = program_deps
        
        return program_dependencies
    
    def _extract_program_name_from_program_id(self, line: str) -> Optional[str]:
        """
        Extract program name from PROGRAM-ID statement.
        
        Examples:
        - PROGRAM-ID. CBACT02C.
        - PROGRAM-ID.    MYPROGRAM
        - PROGRAM-ID. "QUOTED-NAME".
        
        Args:
            line: Line containing PROGRAM-ID statement
            
        Returns:
            Program name if found, None otherwise
        """
        line_upper = line.upper()
        
        # Look for PROGRAM-ID followed by program name
        match = re.search(r'PROGRAM-ID\s*\.\s*([A-Z0-9\-_"\']+)', line_upper)
        if match:
            program_name = match.group(1)
            # Remove quotes if present
            program_name = program_name.strip('"\'')
            # Remove trailing period if present
            program_name = program_name.rstrip('.')
            return program_name
        
        return None
    
    def _extract_default_program_name(self, file_path: Optional[str]) -> Optional[str]:
        """Extract a default program name from the file path."""
        if file_path:
            import os
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            return base_name.upper().replace('-', '_')
        return None
