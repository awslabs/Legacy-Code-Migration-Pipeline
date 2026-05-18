"""PL/I dependency parser."""

import re
import os
from typing import Dict, List, Set, Optional
from .base_parser import BaseDependencyParser
from .pli_complexity_calculator import PLIComplexityCalculator
from ..analysis.copybook_analyzer import CopybookAnalyzer
from ..models.dependency import Dependency, DependencyType


class PLIDependencyParser(BaseDependencyParser):
    """Parses PL/I source for dependencies."""
    
    def __init__(self):
        """Initialize PL/I parser with regex patterns and complexity calculator."""
        super().__init__()
        
        # Initialize complexity calculator
        self.complexity_calculator = PLIComplexityCalculator()
        
        # Initialize copybook analyzer
        self.copybook_analyzer = CopybookAnalyzer()
        
        # Track processed includes to prevent circular references
        self._processed_includes = set()
        self._include_stack = []
        # %INCLUDE statement patterns
        # Handles: %INCLUDE filename; or %INCLUDE library(member); or %INCLUDE library.member;
        self.include_pattern = re.compile(
            r'%INCLUDE\s+(?:([A-Z0-9_]+)[\(\.])?([A-Z0-9_]+)[\)\;]?',
            re.IGNORECASE
        )
        
        # CALL statement patterns
        # Handles: CALL program_name; or CALL program_name(params);
        self.call_pattern = re.compile(
            r'\bCALL\s+([A-Z0-9_]+)(?:\s*\(|\s*;)',
            re.IGNORECASE
        )
        
        # EXEC CICS XCTL patterns
        # Handles: EXEC CICS XCTL PROGRAM('PROGNAME') or PROGRAM(PROGNAME)
        self.cics_xctl_pattern = re.compile(
            r'EXEC\s+CICS\s+XCTL\s+PROGRAM\s*\(\s*[\'"]?([A-Z0-9_]+)[\'"]?\s*\)',
            re.IGNORECASE
        )
        
        # EXEC CICS LINK patterns
        # Handles: EXEC CICS LINK PROGRAM('PROGNAME') or PROGRAM(PROGNAME)
        self.cics_link_pattern = re.compile(
            r'EXEC\s+CICS\s+LINK\s+PROGRAM\s*\(\s*[\'"]?([A-Z0-9_]+)[\'"]?\s*\)',
            re.IGNORECASE
        )
        
        # FILE declaration patterns
        # Handles: DCL filename FILE RECORD ...
        self.file_dcl_pattern = re.compile(
            r'\bDCL\s+([A-Z0-9_]+)\s+FILE\s+RECORD',
            re.IGNORECASE
        )
        
        # READ FILE patterns
        # Handles: READ FILE(filename) INTO(...)
        self.read_file_pattern = re.compile(
            r'\bREAD\s+FILE\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # WRITE FILE patterns
        # Handles: WRITE FILE(filename) FROM(...)
        self.write_file_pattern = re.compile(
            r'\bWRITE\s+FILE\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # OPEN FILE patterns
        # Handles: OPEN FILE(filename)
        self.open_file_pattern = re.compile(
            r'\bOPEN\s+FILE\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # CLOSE FILE patterns
        # Handles: CLOSE FILE(filename)
        self.close_file_pattern = re.compile(
            r'\bCLOSE\s+FILE\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # EXEC CICS READ patterns
        # Handles: EXEC CICS READ DATASET(filename) or FILE(filename)
        self.cics_read_pattern = re.compile(
            r'EXEC\s+CICS\s+READ\s+(?:DATASET|FILE)\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # EXEC CICS WRITE patterns
        # Handles: EXEC CICS WRITE DATASET(filename) or FILE(filename)
        self.cics_write_pattern = re.compile(
            r'EXEC\s+CICS\s+WRITE\s+(?:DATASET|FILE)\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # EXEC CICS REWRITE patterns
        # Handles: EXEC CICS REWRITE DATASET(filename) or FILE(filename)
        self.cics_rewrite_pattern = re.compile(
            r'EXEC\s+CICS\s+REWRITE\s+(?:DATASET|FILE)\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # EXEC CICS DELETE patterns
        # Handles: EXEC CICS DELETE DATASET(filename) or FILE(filename)
        self.cics_delete_pattern = re.compile(
            r'EXEC\s+CICS\s+DELETE\s+(?:DATASET|FILE)\s*\(\s*([A-Z0-9_]+)\s*\)',
            re.IGNORECASE
        )
        
        # PROCEDURE OPTIONS(MAIN) pattern
        # Handles: PROCNAME: PROCEDURE OPTIONS(MAIN) or PROC OPTIONS(MAIN)
        self.main_proc_pattern = re.compile(
            r':\s*PROC(?:EDURE)?\s*(?:\([^)]*\))?\s*OPTIONS\s*\(\s*MAIN\s*\)',
            re.IGNORECASE
        )
        
        # PL/I built-in functions to exclude from CALL analysis
        self.builtin_functions = {
            'PUT', 'GET', 'READ', 'WRITE', 'OPEN', 'CLOSE',
            'ALLOCATE', 'FREE', 'SUBSTR', 'LENGTH', 'INDEX',
            'VERIFY', 'TRANSLATE', 'TRIM', 'DATETIME', 'DATE',
            'TIME', 'ADDR', 'STG', 'LOW', 'HIGH', 'PLIDUMP',
            'PROCEDURENAME', 'UNSPEC', 'STRING', 'HBOUND', 'LBOUND'
        }
    
    def parse(self, source_code: str) -> Dict[str, List[str]]:
        """
        Extract dependencies from PL/I source.
        
        Patterns detected:
        - %INCLUDE statements (include files)
        - CALL statements (program calls)
        - EXEC CICS XCTL (program transfers)
        - EXEC CICS LINK (program calls)
        - FILE declarations (data file references)
        - READ FILE statements (data read operations)
        - WRITE FILE statements (data write operations)
        - OPEN/CLOSE FILE statements (file operations)
        - EXEC CICS READ/WRITE/REWRITE/DELETE (CICS file operations)
        - PROCEDURE OPTIONS(MAIN) (main program identification)
        
        Args:
            source_code: PL/I source code
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        # Normalize source code
        normalized_code = self._normalize_source(source_code)
        
        # Parse different dependency types
        includes = self.parse_include_statements(normalized_code)
        calls = self.parse_call_statements(normalized_code)
        cics_xctl = self.parse_cics_xctl_statements(normalized_code)
        cics_link = self.parse_cics_link_statements(normalized_code)
        file_decls = self.parse_file_declarations(normalized_code)
        read_files = self.parse_read_file_statements(normalized_code)
        write_files = self.parse_write_file_statements(normalized_code)
        cics_reads = self.parse_cics_read_statements(normalized_code)
        cics_writes = self.parse_cics_write_statements(normalized_code)
        cics_rewrites = self.parse_cics_rewrite_statements(normalized_code)
        cics_deletes = self.parse_cics_delete_statements(normalized_code)
        is_main = self.is_main_program(normalized_code)
        
        result = {
            'includes': list(includes),
            'calls': list(calls),
            'cics_xctl': list(cics_xctl),
            'cics_link': list(cics_link),
            'file_declarations': list(file_decls),
            'file_reads': list(read_files),
            'file_writes': list(write_files),
            'cics_reads': list(cics_reads),
            'cics_writes': list(cics_writes),
            'cics_rewrites': list(cics_rewrites),
            'cics_deletes': list(cics_deletes),
            'is_main_program': is_main
        }
        
        return result
    
    def parse_with_include_analysis(self, source_code: str, source_file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Parse PL/I source with comprehensive include analysis.
        
        This method extends the basic parse functionality to:
        - Analyze included file content for executable code
        - Track dependencies found within included content
        - Handle nested includes and circular reference detection
        - Create dependency records for include relationships
        
        Args:
            source_code: PL/I source code
            source_file_path: Path to the source file (for resolving includes)
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names,
            including dependencies found within included files
        """
        # Reset circular reference tracking for new parse
        self._processed_includes = set()
        self._include_stack = []
        
        # Get basic dependencies
        result = self.parse(source_code)
        
        # If no source file path provided, can't analyze includes
        if not source_file_path:
            return result
        
        # Analyze includes for executable code and nested dependencies
        include_dependencies = self._analyze_includes_recursively(
            result.get('includes', []), 
            source_file_path
        )
        
        # Merge include dependencies into result
        for dep_type, deps in include_dependencies.items():
            if dep_type in result:
                # Combine and deduplicate
                combined = set(result[dep_type]) | set(deps)
                result[dep_type] = list(combined)
            else:
                result[dep_type] = deps
        
        return result
    
    def _analyze_includes_recursively(self, includes: List[str], source_file_path: str) -> Dict[str, List[str]]:
        """
        Recursively analyze include files for executable code and dependencies.
        
        Args:
            includes: List of include file names
            source_file_path: Path to the source file containing the includes
            
        Returns:
            Dictionary of dependencies found within include files
        """
        all_dependencies = {}
        source_dir = os.path.dirname(source_file_path)
        
        for include_name in includes:
            # Skip if already processed (circular reference prevention)
            if include_name in self._processed_includes:
                continue
            
            # Check for circular reference in current stack
            if include_name in self._include_stack:
                continue
            
            # Find include file
            include_path = self._resolve_include_path(include_name, source_dir)
            if not include_path or not os.path.exists(include_path):
                continue
            
            # Add to processing stack
            self._include_stack.append(include_name)
            self._processed_includes.add(include_name)
            
            try:
                # Read and analyze include content
                with open(include_path, 'r', encoding='utf-8', errors='ignore') as f:
                    include_content = f.read()
                
                # Analyze include for executable code
                analysis_result = self.copybook_analyzer.analyze_content(
                    include_path, 'PLI', include_content
                )
                
                # If include has executable code, extract its dependencies
                if analysis_result.has_executable_code:
                    include_deps = self.parse(include_content)
                    
                    # Merge dependencies
                    for dep_type, deps in include_deps.items():
                        if dep_type == 'is_main_program':
                            continue  # Skip boolean flags
                        
                        if dep_type not in all_dependencies:
                            all_dependencies[dep_type] = []
                        all_dependencies[dep_type].extend(deps)
                    
                    # Recursively analyze nested includes
                    nested_includes = include_deps.get('includes', [])
                    if nested_includes:
                        nested_deps = self._analyze_includes_recursively(
                            nested_includes, include_path
                        )
                        
                        # Merge nested dependencies
                        for dep_type, deps in nested_deps.items():
                            if dep_type not in all_dependencies:
                                all_dependencies[dep_type] = []
                            all_dependencies[dep_type].extend(deps)
                
            except (IOError, UnicodeDecodeError) as e:
                # Log error but continue processing other includes
                pass
            finally:
                # Remove from processing stack
                if include_name in self._include_stack:
                    self._include_stack.remove(include_name)
        
        # Deduplicate all dependency lists
        for dep_type in all_dependencies:
            all_dependencies[dep_type] = list(set(all_dependencies[dep_type]))
        
        return all_dependencies
    
    def _resolve_include_path(self, include_name: str, source_dir: str) -> Optional[str]:
        """
        Resolve the full path to an include file.
        
        Args:
            include_name: Name of the include file
            source_dir: Directory containing the source file
            
        Returns:
            Full path to include file, or None if not found
        """
        # Handle library.member format
        if '.' in include_name:
            library, member = include_name.split('.', 1)
            # Try library subdirectory
            library_path = os.path.join(source_dir, library.lower(), f"{member}.inc")
            if os.path.exists(library_path):
                return library_path
            # Try with different extensions
            for ext in ['.pli', '.pl1', '.inc']:
                library_path = os.path.join(source_dir, library.lower(), f"{member}{ext}")
                if os.path.exists(library_path):
                    return library_path
        
        # Try different common locations and extensions
        search_paths = [
            source_dir,
            os.path.join(source_dir, 'inc'),
            os.path.join(source_dir, 'include'),
            os.path.join(source_dir, 'copybooks'),
            os.path.join(source_dir, '..', 'inc'),
            os.path.join(source_dir, '..', 'include'),
            os.path.join(source_dir, '..', 'copybooks')
        ]
        
        extensions = ['.inc', '.pli', '.pl1', '']
        
        for search_dir in search_paths:
            if not os.path.exists(search_dir):
                continue
            
            for ext in extensions:
                candidate_path = os.path.join(search_dir, f"{include_name}{ext}")
                if os.path.exists(candidate_path):
                    return candidate_path
        
        return None
    
    def get_include_dependencies(self, source_code: str, source_file_path: str) -> List[Dependency]:
        """
        Get detailed dependency objects for include relationships.
        
        Args:
            source_code: PL/I source code
            source_file_path: Path to the source file
            
        Returns:
            List of Dependency objects representing include relationships
        """
        dependencies = []
        source_name = os.path.splitext(os.path.basename(source_file_path))[0]
        
        # Reset circular reference tracking
        self._processed_includes = set()
        self._include_stack = []
        
        # Parse includes from source
        normalized_code = self._normalize_source(source_code)
        includes = self.parse_include_statements(normalized_code)
        
        # Create dependencies for each include
        for include_name in includes:
            # Create basic include dependency
            include_dep = Dependency(
                source_artifact=source_name,
                source_type="PROGRAM",
                target_artifact=include_name,
                target_type="INCLUDE",
                dependency_type=DependencyType.INCLUDE,
                source_language="PLI",
                source_file=source_file_path,
                line_number=self._find_include_line_number(normalized_code, include_name)
            )
            dependencies.append(include_dep)
            
            # Analyze include content for additional dependencies
            include_path = self._resolve_include_path(include_name, os.path.dirname(source_file_path))
            if include_path and os.path.exists(include_path):
                nested_deps = self._get_nested_include_dependencies(
                    include_name, include_path, source_name, source_file_path
                )
                dependencies.extend(nested_deps)
        
        return dependencies
    
    def _get_nested_include_dependencies(self, include_name: str, include_path: str, 
                                       source_program: str, source_file: str) -> List[Dependency]:
        """
        Get dependencies from within an include file.
        
        Args:
            include_name: Name of the include file
            include_path: Full path to the include file
            source_program: Name of the program that includes this file
            source_file: Path to the source file
            
        Returns:
            List of dependencies found within the include file
        """
        dependencies = []
        
        # Skip if already processed (circular reference prevention)
        if include_name in self._processed_includes:
            return dependencies
        
        # Check for circular reference in current stack
        if include_name in self._include_stack:
            return dependencies
        
        # Add to processing stack
        self._include_stack.append(include_name)
        self._processed_includes.add(include_name)
        
        try:
            # Read include content
            with open(include_path, 'r', encoding='utf-8', errors='ignore') as f:
                include_content = f.read()
            
            # Analyze for executable code
            analysis_result = self.copybook_analyzer.analyze_content(
                include_path, 'PLI', include_content
            )
            
            # If include has executable code, get its dependencies
            if analysis_result.has_executable_code:
                # Add dependencies from copybook analysis
                dependencies.extend(analysis_result.program_dependencies)
                
                # Parse include content for additional dependencies
                include_deps = self.parse(include_content)
                
                # Create dependency objects for calls found in include
                for call in include_deps.get('calls', []):
                    call_dep = Dependency(
                        source_artifact=source_program,
                        source_type="PROGRAM",
                        target_artifact=call,
                        target_type="PROGRAM",
                        dependency_type=DependencyType.CALL,
                        source_language="PLI",
                        source_file=source_file,
                        line_number=None,  # Line number in include file
                        notes=f"via include {include_name}"
                    )
                    dependencies.append(call_dep)
                
                # Handle nested includes recursively
                for nested_include in include_deps.get('includes', []):
                    nested_path = self._resolve_include_path(
                        nested_include, os.path.dirname(include_path)
                    )
                    if nested_path and os.path.exists(nested_path):
                        nested_deps = self._get_nested_include_dependencies(
                            nested_include, nested_path, source_program, source_file
                        )
                        dependencies.extend(nested_deps)
        
        except (IOError, UnicodeDecodeError):
            # Log error but continue processing
            pass
        finally:
            # Remove from processing stack
            if include_name in self._include_stack:
                self._include_stack.remove(include_name)
        
        return dependencies
    
    def _find_include_line_number(self, source_code: str, include_name: str) -> Optional[int]:
        """
        Find the line number where an include statement appears.
        
        Args:
            source_code: Normalized source code
            include_name: Name of the include file
            
        Returns:
            Line number (1-based) or None if not found
        """
        lines = source_code.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(rf'%INCLUDE\s+.*{re.escape(include_name)}', line, re.IGNORECASE):
                return i
        return None
    
    def _normalize_source(self, source_code: str) -> str:
        """
        Normalize PL/I source code by handling syntax variations.
        
        Handles:
        - Comments (/* ... */)
        - Preprocessor directives (%)
        - Statement terminators (;)
        
        Args:
            source_code: Raw PL/I source
            
        Returns:
            Normalized source code
        """
        # Remove block comments /* ... */
        # Use non-greedy matching to handle multiple comments
        normalized = re.sub(r'/\*.*?\*/', ' ', source_code, flags=re.DOTALL)
        
        # Normalize whitespace (replace multiple spaces/newlines with single space)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def parse_include_statements(self, source_code: str) -> Set[str]:
        """
        Extract include files from %INCLUDE statements.
        
        Handles:
        - %INCLUDE filename;
        - %INCLUDE library(member);
        - %INCLUDE with library references
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of include file names
        """
        includes = set()
        
        for match in self.include_pattern.finditer(source_code):
            library_name = match.group(1) if match.lastindex >= 2 and match.group(1) else None
            member_name = match.group(2)
            
            # If library is specified, include it in the name
            if library_name:
                includes.add(f"{library_name}.{member_name}")
            else:
                includes.add(member_name)
        
        return includes
    
    def parse_call_statements(self, source_code: str) -> Set[str]:
        """
        Extract program names from CALL statements.
        
        Handles:
        - CALL program_name;
        - CALL program_name(param1, param2);
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of program names
        """
        programs = set()
        
        for match in self.call_pattern.finditer(source_code):
            program_name = match.group(1)
            # Filter out PL/I built-in functions
            if program_name.upper() not in self.builtin_functions:
                programs.add(program_name)
        
        return programs
    
    def parse_cics_xctl_statements(self, source_code: str) -> Set[str]:
        """
        Extract program names from EXEC CICS XCTL statements.
        
        Handles:
        - EXEC CICS XCTL PROGRAM('PROGNAME')
        - EXEC CICS XCTL PROGRAM(PROGNAME)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of program names
        """
        programs = set()
        
        for match in self.cics_xctl_pattern.finditer(source_code):
            program_name = match.group(1)
            programs.add(program_name)
        
        return programs
    
    def parse_cics_link_statements(self, source_code: str) -> Set[str]:
        """
        Extract program names from EXEC CICS LINK statements.
        
        Handles:
        - EXEC CICS LINK PROGRAM('PROGNAME')
        - EXEC CICS LINK PROGRAM(PROGNAME)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of program names
        """
        programs = set()
        
        for match in self.cics_link_pattern.finditer(source_code):
            program_name = match.group(1)
            programs.add(program_name)
        
        return programs
    
    def parse_file_declarations(self, source_code: str) -> Set[str]:
        """
        Extract file names from FILE declarations.
        
        Handles:
        - DCL filename FILE RECORD ...
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file names
        """
        files = set()
        
        for match in self.file_dcl_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def parse_read_file_statements(self, source_code: str) -> Set[str]:
        """
        Extract file names from READ FILE statements.
        
        Handles:
        - READ FILE(filename) INTO(...)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file names
        """
        files = set()
        
        for match in self.read_file_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def parse_write_file_statements(self, source_code: str) -> Set[str]:
        """
        Extract file names from WRITE FILE statements.
        
        Handles:
        - WRITE FILE(filename) FROM(...)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file names
        """
        files = set()
        
        for match in self.write_file_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def parse_cics_read_statements(self, source_code: str) -> Set[str]:
        """
        Extract file/dataset names from EXEC CICS READ statements.
        
        Handles:
        - EXEC CICS READ DATASET(filename)
        - EXEC CICS READ FILE(filename)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file/dataset names
        """
        files = set()
        
        for match in self.cics_read_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def parse_cics_write_statements(self, source_code: str) -> Set[str]:
        """
        Extract file/dataset names from EXEC CICS WRITE statements.
        
        Handles:
        - EXEC CICS WRITE DATASET(filename)
        - EXEC CICS WRITE FILE(filename)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file/dataset names
        """
        files = set()
        
        for match in self.cics_write_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def parse_cics_rewrite_statements(self, source_code: str) -> Set[str]:
        """
        Extract file/dataset names from EXEC CICS REWRITE statements.
        
        Handles:
        - EXEC CICS REWRITE DATASET(filename)
        - EXEC CICS REWRITE FILE(filename)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file/dataset names
        """
        files = set()
        
        for match in self.cics_rewrite_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def parse_cics_delete_statements(self, source_code: str) -> Set[str]:
        """
        Extract file/dataset names from EXEC CICS DELETE statements.
        
        Handles:
        - EXEC CICS DELETE DATASET(filename)
        - EXEC CICS DELETE FILE(filename)
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            Set of file/dataset names
        """
        files = set()
        
        for match in self.cics_delete_pattern.finditer(source_code):
            file_name = match.group(1)
            files.add(file_name)
        
        return files
    
    def is_main_program(self, source_code: str) -> bool:
        """
        Determine if this is a main program or subroutine.
        
        Checks for PROCEDURE OPTIONS(MAIN) declaration.
        
        Args:
            source_code: Normalized PL/I source
            
        Returns:
            True if main program, False if subroutine
        """
        return bool(self.main_proc_pattern.search(source_code))
    
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of dependency patterns this parser supports.
        
        Returns:
            List of pattern names
        """
        return [
            '%INCLUDE',
            '%INCLUDE with content analysis',
            'Nested %INCLUDE',
            'Circular reference detection',
            'CALL',
            'EXEC CICS XCTL',
            'EXEC CICS LINK',
            'FILE DECLARATION',
            'READ FILE',
            'WRITE FILE',
            'EXEC CICS READ',
            'EXEC CICS WRITE',
            'EXEC CICS REWRITE',
            'EXEC CICS DELETE',
            'PROCEDURE OPTIONS(MAIN)'
        ]
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser supports.
        
        Returns:
            List of file extensions
        """
        return ['.pli', '.pl1', '.inc']
