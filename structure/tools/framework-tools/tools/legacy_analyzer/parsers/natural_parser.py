"""Natural (Software AG) dependency parser."""

import re
import os
from typing import Dict, List, Set, Optional
from .base_parser import BaseDependencyParser
from ..models.program_boundary import ProgramBoundary, ProgramType
from ..analysis.copybook_analyzer import CopybookAnalyzer
from ..models.dependency import Dependency, DependencyType


class NaturalDependencyParser(BaseDependencyParser):
    """Parses Natural source for dependencies."""
    
    def __init__(self):
        """Initialize Natural parser with regex patterns."""
        
        # Initialize complexity calculator
        from .natural_complexity_calculator import NATURALComplexityCalculator
        self.complexity_calculator = NATURALComplexityCalculator()
        
        # Initialize copybook analyzer
        self.copybook_analyzer = CopybookAnalyzer()
        
        # Track processed USING references to prevent circular references
        self._processed_using = set()
        self._using_stack = []
        # CALLNAT statement patterns
        # Handles: CALLNAT 'PROGNAME' or CALLNAT "PROGNAME"
        self.callnat_pattern = re.compile(
            r'\bCALLNAT\s+[\'"]([A-Z0-9\-_]+)[\'"]',
            re.IGNORECASE
        )
        
        # FETCH statement patterns
        # Handles: FETCH 'PROGNAME' or FETCH RETURN 'PROGNAME'
        self.fetch_pattern = re.compile(
            r'\bFETCH\s+(?:RETURN\s+)?[\'"]([A-Z0-9\-_]+)[\'"]',
            re.IGNORECASE
        )
        
        # FETCH RETURN pattern (must be checked BEFORE the generic fetch pattern)
        self.fetch_return_pattern = re.compile(
            r'\bFETCH\s+RETURN\s+[\'"]([A-Z0-9\-_]+)[\'"]',
            re.IGNORECASE
        )
        
        # Plain FETCH pattern (excludes FETCH RETURN)
        self.fetch_plain_pattern = re.compile(
            r'\bFETCH\s+(?!RETURN\b)[\'"]([A-Z0-9\-_]+)[\'"]',
            re.IGNORECASE
        )
        
        # PROCESS PAGE USING pattern
        self.process_page_pattern = re.compile(
            r'\bPROCESS\s+PAGE\s+(?:\(.*?\)\s+)?USING\s+[\'"]([A-Z0-9\-_]+)[\'"]',
            re.IGNORECASE
        )
        
        # REQUEST DOCUMENT FROM pattern
        self.request_document_pattern = re.compile(
            r'\bREQUEST\s+DOCUMENT\s+FROM\s+(?:[\'"]([^\'"]+)[\'"]|(#[A-Z0-9\-_]+))',
            re.IGNORECASE
        )
        
        # DEFINE WORK FILE pattern
        self.define_work_file_pattern = re.compile(
            r'\bDEFINE\s+WORK\s+FILE\s+(\d+)\s+(?:[\'"]([^\'"]+)[\'"]|([A-Z0-9\-_#]+))'
            r'(?:\s+TYPE\s+[\'"]([A-Z0-9]+)[\'"])?',
            re.IGNORECASE
        )
        
        # READ/WRITE WORK FILE pattern
        self.rw_work_file_pattern = re.compile(
            r'\b(?:READ|WRITE)\s+WORK\s+FILE\s+(\d+)',
            re.IGNORECASE
        )
        
        # INCLUDE statement patterns
        # Handles: INCLUDE COPYCODE
        self.include_pattern = re.compile(
            r'\bINCLUDE\s+([A-Z0-9\-_]+)',
            re.IGNORECASE
        )
        
        # USING statement patterns (for global data areas)
        # Handles: USING AJY00G00 or GLOBAL USING AJY00G00 or LOCAL USING AJY00L00
        self.using_pattern = re.compile(
            r'(?:GLOBAL|LOCAL)?\s*USING\s+([A-Z0-9\-_]+)',
            re.IGNORECASE
        )
        
        # DEFINE DATA GLOBAL pattern
        # Handles: DEFINE DATA GLOBAL
        self.define_global_pattern = re.compile(
            r'\bDEFINE\s+DATA\s+GLOBAL\b',
            re.IGNORECASE
        )
        
        # VIEW OF statement patterns (for data file/database references)
        # Handles: VIEW OF EMPLOYEES or 1 EMPLOYEE VIEW OF EMPLOYEES
        self.view_of_pattern = re.compile(
            r'\bVIEW\s+OF\s+([A-Z0-9\-_]+)',
            re.IGNORECASE
        )
        
        # READ statement patterns (for data access operations)
        # Handles: READ EMPLOYEE WITH NAME or FIND EMPL1 WITH PERSONNEL-ID
        self.read_pattern = re.compile(
            r'\b(?:READ|FIND|HISTOGRAM)\s+([A-Z0-9\-_]+)\s+(?:WITH|BY|IN|FOR)',
            re.IGNORECASE
        )
        
        # VIEW definition pattern (for tracking VIEW to physical file mappings)
        # Handles: 1 EMPL1 VIEW OF EMPLOYEES or 2 EMP2 VIEW OF EMPLOYEES
        self.view_definition_pattern = re.compile(
            r'^\s*\d+\s+([A-Z0-9\-_]+)\s+VIEW\s+OF\s+([A-Z0-9\-_]+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # .NSD file header pattern (for extracting physical file names from DDM files)
        # Handles: DB: 000 FILE: 011  - EMPLOYEES
        self.nsd_file_header_pattern = re.compile(
            r'DB:\s*\d+\s+FILE:\s*\d+\s*-\s*([A-Z0-9\-_]+)',
            re.IGNORECASE
        )
        
        # Natural source header patterns for metadata extraction
        # Handles: * :Mode S or /* :Mode S or * :CP windows-1252 or * :LineIncrement 10
        self.header_mode_pattern = re.compile(
            r'^\s*/?\*+\s*:Mode\s+([A-Z])',
            re.IGNORECASE | re.MULTILINE
        )
        self.header_cp_pattern = re.compile(
            r'^\s*/?\*+\s*:CP\s*([^\n\r]*)$',
            re.IGNORECASE | re.MULTILINE
        )
        self.header_lineincrement_pattern = re.compile(
            r'^\s*/?\*+\s*:LineIncrement\s+(\d+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Natural file extensions
        self.supported_extensions = [
            '.NSP',  # Programs
            '.NSN',  # Subprograms
            '.NSC',  # Copycodes
            '.NSL',  # Local data areas
            '.NSG',  # Global data areas
            '.NSD',  # Data definitions
            '.NSA',  # Subroutines
            '.NS8'   # Helproutines
        ]
        
        # Program boundary detection patterns
        self.define_data_program_pattern = re.compile(
            r'^\s*DEFINE\s+DATA\s+PROGRAM\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        
        self.define_data_subprogram_pattern = re.compile(
            r'^\s*DEFINE\s+DATA\s+SUBPROGRAM\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        
        self.define_data_parameter_pattern = re.compile(
            r'^\s*DEFINE\s+DATA\s+PARAMETER\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        
        self.end_define_pattern = re.compile(
            r'^\s*END-DEFINE\s*$',
            re.IGNORECASE | re.MULTILINE
        )
        
        self.end_program_pattern = re.compile(
            r'^\s*END\s*$',
            re.IGNORECASE | re.MULTILINE
        )
    
    def parse(self, source_code: str) -> Dict[str, List[str]]:
        """
        Extract dependencies from Natural source with VIEW resolution.
        
        Patterns detected:
        - CALLNAT statements (program dependencies)
        - FETCH statements (program dependencies)
        - INCLUDE statements (copycode dependencies)
        - USING statements (global data area references)
        - DEFINE DATA GLOBAL (global data area definitions)
        - VIEW OF statements (data file/database references)
        - READ/FIND statements (data access operations)
        - VIEW definitions (VIEW name to physical file mappings)
        - .NSD file headers (DDM to physical file mappings)
        - Source header metadata (Mode, CP, LineIncrement)
        
        Args:
            source_code: Natural source code
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        # Check if this is a .NSD file (Data Definition Module)
        nsd_info = self.parse_nsd_file(source_code)
        if nsd_info.get('is_ddm'):
            # This is a DDM file - return minimal info
            return {
                'callnat': [],
                'fetch': [],
                'fetch_return': [],
                'includes': [],
                'using': [],
                'is_global_data_area': False,
                'view_of': [],
                'reads': [],
                'view_definitions': {},
                'physical_file': nsd_info.get('physical_file'),
                'is_ddm': True,
                'metadata': self.extract_header_metadata(source_code),
                'page_ref': [],
                'web_service': [],
                'work_file': [],
            }
        
        # Normalize source code
        normalized_code = self._normalize_source(source_code)
        
        # Parse VIEW definitions first (to resolve VIEW names to physical files)
        view_definitions = self.parse_view_definitions(source_code)
        
        # Parse different dependency types
        callnat_deps = self.parse_callnat_statements(normalized_code)
        fetch_deps = self.parse_fetch_plain_statements(normalized_code)
        fetch_return_deps = self.parse_fetch_return_statements(normalized_code)
        include_deps = self.parse_include_statements(normalized_code)
        using_deps = self.parse_using_statements(normalized_code)
        is_global = self.is_global_data_area(normalized_code)
        view_deps = self.parse_view_of_statements(normalized_code)
        read_deps = self.parse_read_statements(normalized_code)
        page_ref_deps = self.parse_process_page_statements(normalized_code)
        web_service_deps = self.parse_request_document_statements(normalized_code)
        work_file_deps = self.parse_work_file_statements(normalized_code)
        
        # Resolve VIEW names to physical files
        resolved_files = set()
        
        # Add physical files from VIEW OF statements
        resolved_files.update(view_deps)
        
        # Resolve READ/FIND statements
        for read_target in read_deps:
            if read_target in view_definitions:
                # It's a VIEW - use the physical file
                resolved_files.add(view_definitions[read_target])
            else:
                # It's a direct file reference or unknown VIEW
                # Add it anyway - might be defined elsewhere
                resolved_files.add(read_target)
        
        # Extract metadata from header
        metadata = self.extract_header_metadata(source_code)
        
        result = {
            'callnat': list(callnat_deps),
            'fetch': list(fetch_deps),              # plain FETCH only
            'fetch_return': list(fetch_return_deps), # FETCH RETURN only
            'includes': list(include_deps),
            'using': list(using_deps),
            'is_global_data_area': is_global,
            'view_of': list(resolved_files),  # Now contains resolved physical files
            'reads': [],  # Empty - resolved into view_of
            'view_definitions': view_definitions,  # For reference/debugging
            'is_ddm': False,
            'metadata': metadata,
            'page_ref': list(page_ref_deps),
            'web_service': list(web_service_deps),
            'work_file': work_file_deps,             # already a list
        }
        
        return result
    
    def parse_with_using_analysis(self, source_code: str, source_file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Parse Natural source with comprehensive USING analysis.
        
        This method extends the basic parse functionality to:
        - Analyze referenced Natural modules for executable procedures
        - Track dependencies found within referenced Natural modules
        - Handle nested USING statements and circular reference detection
        - Create dependency records for USING relationships
        
        Args:
            source_code: Natural source code
            source_file_path: Path to the source file (for resolving USING references)
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names,
            including dependencies found within referenced modules
        """
        # Reset circular reference tracking for new parse
        self._processed_using = set()
        self._using_stack = []
        
        # Get basic dependencies
        result = self.parse(source_code)
        
        # If no source file path provided, can't analyze USING references
        if not source_file_path:
            return result
        
        # Analyze USING references for executable code and nested dependencies
        using_dependencies = self._analyze_using_recursively(
            result.get('using', []), 
            source_file_path
        )
        
        # Merge USING dependencies into result
        for dep_type, deps in using_dependencies.items():
            if dep_type in result:
                # Combine and deduplicate
                combined = set(result[dep_type]) | set(deps)
                result[dep_type] = list(combined)
            else:
                result[dep_type] = deps
        
        return result
    
    def _analyze_using_recursively(self, using_refs: List[str], source_file_path: str) -> Dict[str, List[str]]:
        """
        Recursively analyze USING references for executable code and dependencies.
        
        Args:
            using_refs: List of USING reference names
            source_file_path: Path to the source file containing the USING statements
            
        Returns:
            Dictionary of dependencies found within USING references
        """
        all_dependencies = {}
        source_dir = os.path.dirname(source_file_path)
        
        for using_ref in using_refs:
            # Skip if already processed (circular reference prevention)
            if using_ref in self._processed_using:
                continue
            
            # Check for circular reference in current stack
            if using_ref in self._using_stack:
                continue
            
            # Find USING reference file
            using_path = self._resolve_using_path(using_ref, source_dir)
            if not using_path or not os.path.exists(using_path):
                continue
            
            # Add to processing stack
            self._using_stack.append(using_ref)
            self._processed_using.add(using_ref)
            
            try:
                # Read and analyze USING content
                with open(using_path, 'r', encoding='utf-8', errors='ignore') as f:
                    using_content = f.read()
                
                # Analyze USING reference for executable code
                analysis_result = self.copybook_analyzer.analyze_content(
                    using_path, 'NATURAL', using_content
                )
                
                # If USING reference has executable code, extract its dependencies
                if analysis_result.has_executable_code:
                    using_deps = self.parse(using_content)
                    
                    # Merge dependencies
                    for dep_type, deps in using_deps.items():
                        if dep_type in ['is_global_data_area', 'is_ddm']:
                            continue  # Skip boolean flags
                        
                        if dep_type not in all_dependencies:
                            all_dependencies[dep_type] = []
                        all_dependencies[dep_type].extend(deps)
                    
                    # Recursively analyze nested USING references
                    nested_using = using_deps.get('using', [])
                    if nested_using:
                        nested_deps = self._analyze_using_recursively(
                            nested_using, using_path
                        )
                        
                        # Merge nested dependencies
                        for dep_type, deps in nested_deps.items():
                            if dep_type not in all_dependencies:
                                all_dependencies[dep_type] = []
                            all_dependencies[dep_type].extend(deps)
                
            except (IOError, UnicodeDecodeError) as e:
                # Log error but continue processing other USING references
                pass
            finally:
                # Remove from processing stack
                if using_ref in self._using_stack:
                    self._using_stack.remove(using_ref)
        
        # Deduplicate all dependency lists
        for dep_type in all_dependencies:
            all_dependencies[dep_type] = list(set(all_dependencies[dep_type]))
        
        return all_dependencies
    
    def _resolve_using_path(self, using_ref: str, source_dir: str) -> Optional[str]:
        """
        Resolve the full path to a USING reference file.
        
        Args:
            using_ref: Name of the USING reference
            source_dir: Directory containing the source file
            
        Returns:
            Full path to USING reference file, or None if not found
        """
        # Try different common locations and extensions for Natural modules
        search_paths = [
            source_dir,
            os.path.join(source_dir, 'copycode'),
            os.path.join(source_dir, 'gda'),  # Global Data Areas
            os.path.join(source_dir, 'lda'),  # Local Data Areas
            os.path.join(source_dir, 'natural'),
            os.path.join(source_dir, '..', 'copycode'),
            os.path.join(source_dir, '..', 'gda'),
            os.path.join(source_dir, '..', 'lda'),
            os.path.join(source_dir, '..', 'natural')
        ]
        
        # Natural file extensions in order of preference
        extensions = ['.NSG', '.NSL', '.NSC', '.NSD', '.NSP', '.NSN', '']
        
        for search_dir in search_paths:
            if not os.path.exists(search_dir):
                continue
            
            for ext in extensions:
                candidate_path = os.path.join(search_dir, f"{using_ref}{ext}")
                if os.path.exists(candidate_path):
                    return candidate_path
        
        return None
    
    def get_using_dependencies(self, source_code: str, source_file_path: str) -> List[Dependency]:
        """
        Get detailed dependency objects for USING relationships.
        
        Args:
            source_code: Natural source code
            source_file_path: Path to the source file
            
        Returns:
            List of Dependency objects representing USING relationships
        """
        dependencies = []
        source_name = os.path.splitext(os.path.basename(source_file_path))[0]
        
        # Reset circular reference tracking
        self._processed_using = set()
        self._using_stack = []
        
        # Parse USING statements from source
        normalized_code = self._normalize_source(source_code)
        using_refs = self.parse_using_statements(normalized_code)
        
        # Create dependencies for each USING reference
        for using_ref in using_refs:
            # Create basic USING dependency
            using_dep = Dependency(
                source_artifact=source_name,
                source_type="PROGRAM",
                target_artifact=using_ref,
                target_type="GLOBAL_DATA_AREA",
                dependency_type=DependencyType.COPY,  # USING is similar to COPY/INCLUDE
                source_language="NATURAL",
                source_file=source_file_path,
                line_number=self._find_using_line_number(normalized_code, using_ref)
            )
            dependencies.append(using_dep)
            
            # Analyze USING reference content for additional dependencies
            using_path = self._resolve_using_path(using_ref, os.path.dirname(source_file_path))
            if using_path and os.path.exists(using_path):
                nested_deps = self._get_nested_using_dependencies(
                    using_ref, using_path, source_name, source_file_path
                )
                dependencies.extend(nested_deps)
        
        return dependencies
    
    def _get_nested_using_dependencies(self, using_ref: str, using_path: str, 
                                     source_program: str, source_file: str) -> List[Dependency]:
        """
        Get dependencies from within a USING reference.
        
        Args:
            using_ref: Name of the USING reference
            using_path: Full path to the USING reference file
            source_program: Name of the program that uses this reference
            source_file: Path to the source file
            
        Returns:
            List of dependencies found within the USING reference
        """
        dependencies = []
        
        # Skip if already processed (circular reference prevention)
        if using_ref in self._processed_using:
            return dependencies
        
        # Check for circular reference in current stack
        if using_ref in self._using_stack:
            return dependencies
        
        # Add to processing stack
        self._using_stack.append(using_ref)
        self._processed_using.add(using_ref)
        
        try:
            # Read USING reference content
            with open(using_path, 'r', encoding='utf-8', errors='ignore') as f:
                using_content = f.read()
            
            # Analyze for executable code
            analysis_result = self.copybook_analyzer.analyze_content(
                using_path, 'NATURAL', using_content
            )
            
            # If USING reference has executable code, get its dependencies
            if analysis_result.has_executable_code:
                # Add dependencies from copybook analysis
                dependencies.extend(analysis_result.program_dependencies)
                
                # Parse USING reference content for additional dependencies
                using_deps = self.parse(using_content)
                
                # Create dependency objects for calls found in USING reference
                for call in using_deps.get('callnat', []):
                    call_dep = Dependency(
                        source_artifact=source_program,
                        source_type="PROGRAM",
                        target_artifact=call,
                        target_type="PROGRAM",
                        dependency_type=DependencyType.CALL,
                        source_language="NATURAL",
                        source_file=source_file,
                        line_number=None,  # Line number in USING reference file
                        notes=f"via using {using_ref}"
                    )
                    dependencies.append(call_dep)
                
                # Create dependency objects for FETCH statements
                for fetch in using_deps.get('fetch', []):
                    fetch_dep = Dependency(
                        source_artifact=source_program,
                        source_type="PROGRAM",
                        target_artifact=fetch,
                        target_type="PROGRAM",
                        dependency_type=DependencyType.FETCH,
                        source_language="NATURAL",
                        source_file=source_file,
                        line_number=None,
                        notes=f"via using {using_ref}"
                    )
                    dependencies.append(fetch_dep)
                
                # Handle nested USING references recursively
                for nested_using in using_deps.get('using', []):
                    nested_path = self._resolve_using_path(
                        nested_using, os.path.dirname(using_path)
                    )
                    if nested_path and os.path.exists(nested_path):
                        nested_deps = self._get_nested_using_dependencies(
                            nested_using, nested_path, source_program, source_file
                        )
                        dependencies.extend(nested_deps)
        
        except (IOError, UnicodeDecodeError):
            # Log error but continue processing
            pass
        finally:
            # Remove from processing stack
            if using_ref in self._using_stack:
                self._using_stack.remove(using_ref)
        
        return dependencies
    
    def _find_using_line_number(self, source_code: str, using_ref: str) -> Optional[int]:
        """
        Find the line number where a USING statement appears.
        
        Args:
            source_code: Normalized source code
            using_ref: Name of the USING reference
            
        Returns:
            Line number (1-based) or None if not found
        """
        lines = source_code.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(rf'(?:GLOBAL|LOCAL)?\s*USING\s+{re.escape(using_ref)}', line, re.IGNORECASE):
                return i
        return None
    
    def _normalize_source(self, source_code: str) -> str:
        """
        Normalize Natural source code by handling syntax variations.
        
        Handles:
        - Comments (/* ... */ and * at line start)
        - Statement terminators
        - Line continuations
        
        Args:
            source_code: Raw Natural source
            
        Returns:
            Normalized source code
        """
        lines = source_code.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Skip comment lines (starting with *)
            if line.strip().startswith('*'):
                continue
            
            # Skip Natural source header markers
            if ':Mode' in line or ':CP' in line or ':LineIncrement' in line:
                continue
            if '>Natural Source Header' in line or '<Natural Source Header' in line:
                continue
            
            # Remove inline comments (/** ... or /* ... )
            # Be careful not to remove /* in strings
            comment_pos = line.find('/*')
            if comment_pos >= 0:
                # Check if it's in a string
                before_comment = line[:comment_pos]
                single_quotes = before_comment.count("'")
                double_quotes = before_comment.count('"')
                # If odd number of quotes, we're inside a string
                if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                    line = line[:comment_pos]
            
            normalized_lines.append(line)
        
        # Join lines and normalize whitespace
        normalized = ' '.join(normalized_lines)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def parse_callnat_statements(self, source_code: str) -> Set[str]:
        """
        Extract program names from CALLNAT statements.
        
        Handles:
        - CALLNAT 'PROGNAME'
        - CALLNAT "PROGNAME"
        - CALLNAT 'AJY00N21' #PARAM
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            Set of program names
        """
        programs = set()
        
        for match in self.callnat_pattern.finditer(source_code):
            program_name = match.group(1)
            programs.add(program_name)
        
        return programs
    
    def parse_fetch_statements(self, source_code: str) -> Set[str]:
        """
        Extract program names from FETCH statements.
        
        Handles:
        - FETCH 'PROGNAME'
        - FETCH RETURN 'PROGNAME'
        - FETCH 'LOGIN'
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            Set of program names
        """
        programs = set()
        
        for match in self.fetch_pattern.finditer(source_code):
            program_name = match.group(1)
            programs.add(program_name)
        
        return programs
    
    def parse_fetch_return_statements(self, source_code: str) -> Set[str]:
        """Extract program names from FETCH RETURN statements."""
        programs = set()
        for match in self.fetch_return_pattern.finditer(source_code):
            programs.add(match.group(1))
        return programs

    def parse_fetch_plain_statements(self, source_code: str) -> Set[str]:
        """Extract program names from plain FETCH statements (not FETCH RETURN)."""
        programs = set()
        for match in self.fetch_plain_pattern.finditer(source_code):
            programs.add(match.group(1))
        return programs

    def parse_process_page_statements(self, source_code: str) -> Set[str]:
        """Extract page names from PROCESS PAGE USING statements."""
        pages = set()
        for match in self.process_page_pattern.finditer(source_code):
            pages.add(match.group(1))
        return pages

    def parse_request_document_statements(self, source_code: str) -> Set[str]:
        """Extract endpoint references from REQUEST DOCUMENT FROM statements."""
        endpoints = set()
        for match in self.request_document_pattern.finditer(source_code):
            # Group 1 = string literal, Group 2 = variable reference
            endpoint = match.group(1) or match.group(2)
            if endpoint:
                endpoints.add(endpoint)
        return endpoints

    def parse_work_file_statements(self, source_code: str) -> List[str]:
        """Extract work file targets from DEFINE/READ/WRITE WORK FILE statements.
        
        Returns list of target artifact strings. For DEFINE WORK FILE, uses the
        path/variable. For standalone READ/WRITE without DEFINE, uses WORKFILE-N.
        """
        targets = set()
        defined_files = {}  # file_number -> target
        
        # First pass: collect DEFINE WORK FILE statements
        for match in self.define_work_file_pattern.finditer(source_code):
            file_num = match.group(1)
            target = match.group(2) or match.group(3)  # string literal or variable
            if target:
                defined_files[file_num] = target
                targets.add(target)
        
        # Second pass: collect READ/WRITE WORK FILE statements
        for match in self.rw_work_file_pattern.finditer(source_code):
            file_num = match.group(1)
            if file_num in defined_files:
                targets.add(defined_files[file_num])
            else:
                targets.add(f"WORKFILE-{file_num}")
        
        return list(targets)

    def parse_include_statements(self, source_code: str) -> Set[str]:
        """
        Extract copycode names from INCLUDE statements.
        
        Handles:
        - INCLUDE ERRHANDL
        - INCLUDE AJY00C01
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            Set of copycode names
        """
        copycodes = set()
        
        for match in self.include_pattern.finditer(source_code):
            copycode_name = match.group(1)
            copycodes.add(copycode_name)
        
        return copycodes
    
    def parse_using_statements(self, source_code: str) -> Set[str]:
        """
        Extract global data area names from USING statements.
        
        Handles:
        - USING AJY00G00
        - GLOBAL USING AJY00G00
        - LOCAL USING AJY00L00
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            Set of data area names
        """
        data_areas = set()
        
        for match in self.using_pattern.finditer(source_code):
            data_area_name = match.group(1)
            data_areas.add(data_area_name)
        
        return data_areas
    
    def is_global_data_area(self, source_code: str) -> bool:
        """
        Determine if this is a global data area definition.
        
        Checks for DEFINE DATA GLOBAL declaration.
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            True if global data area, False otherwise
        """
        return bool(self.define_global_pattern.search(source_code))
    
    def parse_view_of_statements(self, source_code: str) -> Set[str]:
        """
        Extract data file/database names from VIEW OF statements.
        
        Handles:
        - VIEW OF EMPLOYEES
        - 1 EMPLOYEE VIEW OF EMPLOYEES
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            Set of data file/database names
        """
        data_files = set()
        
        for match in self.view_of_pattern.finditer(source_code):
            data_file_name = match.group(1)
            data_files.add(data_file_name)
        
        return data_files
    
    def parse_read_statements(self, source_code: str) -> Set[str]:
        """
        Extract data file names from READ/FIND/HISTOGRAM statements.
        
        Handles:
        - READ EMPLOYEE WITH NAME
        - FIND EMPL1 WITH PERSONNEL-ID
        - HISTOGRAM EMP FOR DEPT
        
        Args:
            source_code: Normalized Natural source
            
        Returns:
            Set of data file names (may include VIEW names)
        """
        data_files = set()
        
        for match in self.read_pattern.finditer(source_code):
            data_file_name = match.group(1)
            data_files.add(data_file_name)
        
        return data_files
    
    def parse_view_definitions(self, source_code: str) -> Dict[str, str]:
        """
        Extract VIEW definitions mapping VIEW names to physical files.
        
        Handles:
        - 1 EMPL1 VIEW OF EMPLOYEES
        - 2 EMP2 VIEW OF EMPLOYEES
        - 1 EMPLOYEE VIEW OF EMPLOYEES
        
        Args:
            source_code: Raw Natural source (not normalized)
            
        Returns:
            Dictionary mapping VIEW names to physical file names
        """
        view_map = {}
        
        for match in self.view_definition_pattern.finditer(source_code):
            view_name = match.group(1)
            physical_file = match.group(2)
            view_map[view_name] = physical_file
        
        return view_map
    
    def parse_nsd_file(self, source_code: str) -> Dict[str, any]:
        """
        Parse Natural Data Definition Module (.NSD) files.
        
        Extracts:
        - Physical file name from header (DB: xxx FILE: yyy - FILENAME)
        
        Args:
            source_code: Raw Natural source
            
        Returns:
            Dictionary with file metadata:
            - physical_file: Name of the physical database file
            - is_ddm: True if this is a DDM file
        """
        match = self.nsd_file_header_pattern.search(source_code)
        if match:
            physical_file_name = match.group(1)
            return {
                'physical_file': physical_file_name,
                'is_ddm': True
            }
        
        return {'is_ddm': False}
    
    def extract_header_metadata(self, source_code: str) -> Dict[str, Optional[str]]:
        """
        Extract metadata from Natural source header.
        
        Extracts:
        - Mode (R, S, etc.)
        - CP (Code Page, e.g., windows-1252)
        - LineIncrement (e.g., 10)
        
        Args:
            source_code: Raw Natural source (not normalized)
            
        Returns:
            Dictionary with metadata fields
        """
        metadata = {
            'mode': None,
            'code_page': None,
            'line_increment': None
        }
        
        # Extract Mode
        mode_match = self.header_mode_pattern.search(source_code)
        if mode_match:
            metadata['mode'] = mode_match.group(1)
        
        # Extract Code Page
        cp_match = self.header_cp_pattern.search(source_code)
        if cp_match:
            cp_value = cp_match.group(1).strip()
            # Only set if not empty and doesn't start with * (next line)
            if cp_value and not cp_value.startswith('*'):
                metadata['code_page'] = cp_value
        
        # Extract Line Increment
        li_match = self.header_lineincrement_pattern.search(source_code)
        if li_match:
            metadata['line_increment'] = li_match.group(1)
        
        return metadata
    
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of dependency patterns this parser supports.
        
        Returns:
            List of pattern names
        """
        return [
            'CALLNAT',
            'FETCH',
            'FETCH RETURN',
            'INCLUDE',
            'USING',
            'USING with content analysis',
            'Nested USING',
            'Circular reference detection',
            'DEFINE DATA GLOBAL',
            'VIEW OF',
            'READ/FIND/HISTOGRAM',
            'VIEW DEFINITIONS',
            'NSD FILE HEADERS',
            'HEADER METADATA',
            'PROCESS PAGE USING',
            'REQUEST DOCUMENT',
            'DEFINE WORK FILE / READ WORK FILE / WRITE WORK FILE',
        ]
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser supports.
        
        Returns:
            List of file extensions
        """
        return self.supported_extensions
    
    # Natural reserved keywords that should never be treated as program names
    NATURAL_KEYWORDS = {
        'LOCAL', 'CONST', 'INIT', 'MOVE', 'END', 'DEFINE', 'RESET', 'DATA',
        'PARAMETER', 'GLOBAL', 'INDEPENDENT', 'OBJECT', 'CONTEXT', 'RESULT',
        'IF', 'ELSE', 'FOR', 'WHILE', 'REPEAT', 'UNTIL', 'DECIDE', 'ON',
        'PERFORM', 'ESCAPE', 'STOP', 'TERMINATE', 'INPUT', 'OUTPUT', 'PRINT',
        'WRITE', 'READ', 'FIND', 'GET', 'STORE', 'UPDATE', 'DELETE', 'SORT',
        'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'COMPUTE', 'COMPRESS',
        'EXAMINE', 'SEPARATE', 'STACK', 'TOP', 'BOTTOM', 'PAGE', 'USING',
        'WITH', 'WHERE', 'FROM', 'TO', 'BY', 'INTO', 'VALUE', 'VALUES',
        'NONE', 'TRUE', 'FALSE', 'FIRST', 'EVERY', 'ANY', 'ALL', 'BEFORE',
        'AFTER', 'ACCEPT', 'REJECT', 'IGNORE', 'SUSPEND', 'RESUME',
        'SUBROUTINE', 'PROGRAM', 'SUBPROGRAM', 'FUNCTION', 'MAP',
    }
    
    # Extensions that indicate single-program files (skip multi-program detection)
    SINGLE_PROGRAM_EXTENSIONS = {'.NSP', '.NSN', '.NSC', '.NSL', '.NSG', '.NSD', '.NSA', '.NS8'}

    def detect_program_boundaries(self, source_code: str, file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Detect Natural program boundaries using DEFINE DATA PROGRAM/SUBPROGRAM patterns.
        
        Natural programs are identified by:
        - DEFINE DATA PROGRAM statements (main programs)
        - DEFINE DATA SUBPROGRAM statements (subprograms)  
        - DEFINE DATA PARAMETER statements (subprograms with parameters)
        - File extension-based classification for single-program files
        
        Args:
            source_code: Natural source code content
            file_path: Optional path to the source file for context
            
        Returns:
            List of ProgramBoundary objects representing detected programs
        """
        programs = []
        lines = source_code.splitlines()
        
        if not lines:
            return programs
        
        # For files with known single-program extensions, skip multi-program detection
        # This prevents phantom boundaries from DEFINE DATA LOCAL/PARAMETER blocks
        is_single_program_file = False
        if file_path:
            _, ext = os.path.splitext(file_path)
            is_single_program_file = ext.upper() in self.SINGLE_PROGRAM_EXTENSIONS
        
        # Check for explicit program/subprogram definitions (only for multi-program files)
        program_definitions = []
        if not is_single_program_file:
            program_definitions = self._find_program_definitions(source_code, lines, file_path)
        
        if program_definitions:
            # Multi-program file with explicit definitions
            programs.extend(program_definitions)
        else:
            # Single program file - classify by file extension and content
            program_name = self._extract_program_name_from_file_path(file_path)
            program_type = self._classify_program_type_by_extension_and_content(file_path, source_code)
            
            # Create a single program boundary covering the entire file
            programs.append(ProgramBoundary(
                program_name=program_name,
                start_line=1,
                end_line=len(lines),
                program_type=program_type,
                language="NATURAL",
                entry_points=[program_name],
                file_path=file_path,
                confidence_level=0.9  # High confidence for single-program files
            ))
        
        return programs
    
    def _find_program_definitions(self, source_code: str, lines: List[str], file_path: Optional[str] = None) -> List[ProgramBoundary]:
        """
        Find explicit program/subprogram definitions in Natural source.

        Only matches DEFINE DATA PROGRAM and DEFINE DATA SUBPROGRAM — these indicate
        true program boundaries. DEFINE DATA LOCAL and DEFINE DATA PARAMETER within
        an already-identified program are ignored (they are data sections, not new programs).

        Args:
            source_code: Full source code content
            lines: Source code split into lines
            file_path: Optional path to the source file for extracting program names

        Returns:
            List of ProgramBoundary objects for explicitly defined programs
        """
        programs = []
        current_program = None
        program_counter = 1

        for i, line in enumerate(lines, 1):
            # Check for DEFINE DATA PROGRAM (true main program boundary)
            if self.define_data_program_pattern.match(line):
                if current_program:
                    current_program.end_line = i - 1
                    programs.append(current_program)

                if file_path and program_counter == 1:
                    program_name = self._extract_program_name_from_file_path(file_path)
                else:
                    program_name = f"NATURAL_PROGRAM_{program_counter}"

                current_program = ProgramBoundary(
                    program_name=program_name,
                    start_line=i,
                    end_line=len(lines),
                    program_type=ProgramType.MAIN,
                    language="NATURAL",
                    entry_points=[program_name],
                    file_path=file_path,
                    confidence_level=1.0
                )
                program_counter += 1

            # Check for DEFINE DATA SUBPROGRAM (true subprogram boundary)
            elif self.define_data_subprogram_pattern.match(line):
                if current_program:
                    current_program.end_line = i - 1
                    programs.append(current_program)

                if file_path and program_counter == 1:
                    program_name = self._extract_program_name_from_file_path(file_path)
                else:
                    program_name = f"NATURAL_SUBPROGRAM_{program_counter}"

                current_program = ProgramBoundary(
                    program_name=program_name,
                    start_line=i,
                    end_line=len(lines),
                    program_type=ProgramType.SUBPROGRAM,
                    language="NATURAL",
                    entry_points=[program_name],
                    file_path=file_path,
                    confidence_level=1.0
                )
                program_counter += 1

            # DEFINE DATA PARAMETER / DEFINE DATA LOCAL are NOT new program boundaries.
            # They are data sections within an existing program. Only create a boundary
            # if no program has been started yet (first definition in file).
            elif self.define_data_parameter_pattern.match(line):
                if not current_program:
                    if file_path and program_counter == 1:
                        program_name = self._extract_program_name_from_file_path(file_path)
                    else:
                        program_name = f"NATURAL_SUBPROGRAM_{program_counter}"

                    current_program = ProgramBoundary(
                        program_name=program_name,
                        start_line=i,
                        end_line=len(lines),
                        program_type=ProgramType.SUBPROGRAM,
                        language="NATURAL",
                        entry_points=[program_name],
                        file_path=file_path,
                        confidence_level=1.0
                    )
                    program_counter += 1
                # else: inside an existing program — skip, not a new boundary

        # Close the last program
        if current_program:
            programs.append(current_program)

        # Filter out any programs with keyword names (safety net)
        programs = [p for p in programs if p.program_name.upper() not in self.NATURAL_KEYWORDS]

        return programs
    
    def _extract_program_name_from_file_path(self, file_path: Optional[str]) -> str:
        """
        Extract program name from file path.
        
        Args:
            file_path: Path to the Natural source file
            
        Returns:
            Program name derived from file path or default name
        """
        if file_path:
            import os
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            return base_name.upper()
        return "NATURAL_PROGRAM_1"
    
    def _classify_program_type_by_extension_and_content(self, file_path: Optional[str], source_code: str) -> ProgramType:
        """
        Classify program type based on file extension and content analysis.
        
        Args:
            file_path: Path to the Natural source file
            source_code: Source code content
            
        Returns:
            ProgramType classification
        """
        if file_path:
            import os
            _, ext = os.path.splitext(file_path)
            ext_upper = ext.upper()
            
            # Classify by file extension
            if ext_upper == '.NSP':
                return ProgramType.MAIN  # Natural Program
            elif ext_upper == '.NSN':
                return ProgramType.SUBPROGRAM  # Natural Subprogram
            elif ext_upper == '.NSA':
                return ProgramType.FUNCTION  # Natural Subroutine
            elif ext_upper == '.NS8':
                return ProgramType.FUNCTION  # Natural Helproutine
            elif ext_upper in ['.NSC', '.NSL', '.NSG', '.NSD']:
                # Data structures, copycodes, data areas — not executable programs
                return ProgramType.DATA
        
        # Analyze content for additional clues
        if 'DEFINE DATA PARAMETER' in source_code.upper():
            return ProgramType.SUBPROGRAM
        elif 'DEFINE DATA GLOBAL' in source_code.upper():
            return ProgramType.MAIN  # Global data areas are typically main-level
        
        # Default classification
        return ProgramType.MAIN
