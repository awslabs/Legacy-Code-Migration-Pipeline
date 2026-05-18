"""JCL dependency parser."""

import re
from typing import Dict, List, Set, Tuple
from .base_parser import BaseDependencyParser


class JCLDependencyParser(BaseDependencyParser):
    """Parses JCL for dependencies."""
    
    def __init__(self):
        """Initialize JCL parser with regex patterns."""
        # EXEC statement patterns
        self.exec_pgm_pattern = re.compile(
            r'//[A-Z0-9#@$]+\s+EXEC\s+PGM=([A-Z0-9#@$]+)',
            re.IGNORECASE
        )
        self.exec_proc_pattern = re.compile(
            r'//[A-Z0-9#@$]+\s+EXEC\s+(?:PROC=)?([A-Z0-9#@$]+)',
            re.IGNORECASE
        )
        
        # INCLUDE statement pattern
        self.include_pattern = re.compile(
            r'//\s*INCLUDE\s+MEMBER=([A-Z0-9#@$]+)',
            re.IGNORECASE
        )
        
        # DD statement patterns
        # Match both named DD and continuation DD (with spaces instead of name)
        self.dd_dsn_pattern = re.compile(
            r'//([A-Z0-9#@$\s]+)\s+DD\s+.*?DSN=([A-Z0-9.()&\-]+)',
            re.IGNORECASE
        )
        
        # Symbolic parameter pattern
        self.symbolic_param_pattern = re.compile(r'&[A-Z0-9]+')
    
    def parse(self, jcl_code: str) -> Dict[str, List[str]]:
        """
        Extract dependencies from JCL.
        
        Patterns detected:
        - EXEC PGM= statements
        - EXEC PROC= statements
        - INCLUDE statements
        - Dataset references (DD DSN=)
        
        Args:
            jcl_code: JCL source code
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        # Normalize JCL code
        normalized_code = self._normalize_jcl(jcl_code)
        
        # Parse different dependency types
        programs = self.parse_exec_statements(normalized_code)
        includes = self.parse_include_statements(normalized_code)
        datasets = self.parse_dd_statements(normalized_code)
        
        return {
            'programs': programs.get('programs', []),
            'procs': programs.get('procs', []),
            'includes': includes,
            'datasets': datasets.get('datasets', []),
            'dataset_usage': datasets.get('usage', {})
        }
    
    def _normalize_jcl(self, jcl_code: str) -> str:
        """
        Normalize JCL code by handling syntax variations.
        
        Handles:
        - Continuations (comma at end of line, continued on next line)
        - Comments (//* or //)
        - In-stream data (DD *)
        - IF/THEN/ENDIF blocks (preserves EXEC statements inside)
        
        Args:
            jcl_code: Raw JCL source
            
        Returns:
            Normalized JCL code
        """
        lines = jcl_code.split('\n')
        normalized_lines = []
        continuation_buffer = ""
        in_stream_data = False
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check for comment lines (but not IF/THEN/ENDIF which start with //)
            # IF/THEN/ENDIF statements look like: //IF0001   IF (RC LE 4) THEN
            # We need to preserve these but skip actual comments like //*
            if line.startswith('//*'):
                continue
            
            # Check for IF/THEN/ENDIF control statements - preserve them but don't treat as executable
            # These are JCL control flow statements, not comments
            if re.match(r'//[A-Z0-9#@$]+\s+IF\s+', line, re.IGNORECASE):
                # This is an IF statement, preserve it
                normalized_lines.append(line)
                continue
            
            if re.match(r'//[A-Z0-9#@$]+\s+ENDIF', line, re.IGNORECASE):
                # This is an ENDIF statement, preserve it
                normalized_lines.append(line)
                continue
            
            if re.match(r'//[A-Z0-9#@$]+\s+ELSE', line, re.IGNORECASE):
                # This is an ELSE statement, preserve it
                normalized_lines.append(line)
                continue
            
            # Check for end of in-stream data
            if in_stream_data:
                if line.startswith('//'):
                    in_stream_data = False
                else:
                    # Skip in-stream data lines
                    continue
            
            # Check for in-stream data start (DD *)
            if re.search(r'DD\s+\*', line, re.IGNORECASE):
                in_stream_data = True
                # Still process the DD * line itself
            
            # Handle continuations
            # JCL continuation: comma at end, next line continues
            stripped = line.rstrip()
            
            if continuation_buffer:
                # This line is a continuation of previous
                # Remove leading // if present on continuation
                if line.startswith('//'):
                    # Find first non-space after //
                    match = re.match(r'//\s*(.*)', line)
                    if match:
                        line_content = match.group(1)
                    else:
                        line_content = line[2:]
                else:
                    line_content = line
                
                continuation_buffer += line_content.strip()
                
                # Check if this line also continues
                if not stripped.endswith(','):
                    normalized_lines.append(continuation_buffer)
                    continuation_buffer = ""
            else:
                # Check if this line continues to next
                if stripped.endswith(','):
                    continuation_buffer = stripped
                else:
                    normalized_lines.append(line)
        
        # Add any remaining continuation buffer
        if continuation_buffer:
            normalized_lines.append(continuation_buffer)
        
        return '\n'.join(normalized_lines)
    
    def parse_exec_statements(self, jcl_code: str) -> Dict[str, List[str]]:
        """
        Extract program and proc names from EXEC statements.
        
        Handles:
        - EXEC PGM=PROGRAM1
        - EXEC PROC=PROC1
        - EXEC PROC1 (implicit PROC=)
        - Symbolic parameters (&PARM)
        
        Args:
            jcl_code: Normalized JCL source
            
        Returns:
            Dictionary with programs and procs lists
        """
        programs = set()
        procs = set()
        
        # Extract EXEC PGM= statements
        for match in self.exec_pgm_pattern.finditer(jcl_code):
            program_name = match.group(1)
            # Skip if it's a symbolic parameter
            if not program_name.startswith('&'):
                programs.add(program_name)
        
        # Extract EXEC PROC= statements
        # Need to be careful not to match EXEC PGM=
        for line in jcl_code.split('\n'):
            if not line.strip().startswith('//'):
                continue
            
            # Skip if it's EXEC PGM=
            if re.search(r'EXEC\s+PGM=', line, re.IGNORECASE):
                continue
            
            # Look for EXEC PROC= or EXEC procname
            match = re.search(r'EXEC\s+(?:PROC=)?([A-Z0-9#@$]+)', line, re.IGNORECASE)
            if match:
                proc_name = match.group(1)
                # Skip if it's a symbolic parameter
                if not proc_name.startswith('&'):
                    procs.add(proc_name)
        
        return {
            'programs': list(programs),
            'procs': list(procs)
        }
    
    def parse_include_statements(self, jcl_code: str) -> List[str]:
        """
        Extract member names from INCLUDE statements.
        
        Handles:
        - INCLUDE MEMBER=MEMBER1
        - Library references (tracked in member name)
        
        Args:
            jcl_code: Normalized JCL source
            
        Returns:
            List of included member names
        """
        includes = set()
        
        for match in self.include_pattern.finditer(jcl_code):
            member_name = match.group(1)
            # Skip if it's a symbolic parameter
            if not member_name.startswith('&'):
                includes.add(member_name)
        
        return list(includes)
    
    def parse_dd_statements(self, jcl_code: str) -> Dict[str, any]:
        """
        Extract dataset names from DD statements.
        
        Handles:
        - DD DSN=DATASET.NAME
        - DD DSN=DATASET.NAME,DISP=(NEW,CATLG) - track as OUTPUT
        - DD DSN=DATASET.NAME,DISP=SHR - track as INPUT
        - Concatenated datasets (multiple DD with same ddname)
        - Symbolic parameters (&PARM)
        
        Args:
            jcl_code: Normalized JCL source
            
        Returns:
            Dictionary with datasets list and usage mapping
        """
        datasets = set()
        dataset_usage = {}  # Maps dataset to usage type (INPUT/OUTPUT)
        concatenated_groups = {}  # Track concatenated DD statements
        
        for line in jcl_code.split('\n'):
            match = self.dd_dsn_pattern.search(line)
            if match:
                dd_name = match.group(1)
                dataset_name = match.group(2)
                
                # Remove parentheses if present (for GDG references)
                # Handle both (0), (+1), (-1) patterns
                # Also handle incomplete parentheses from regex capture
                dataset_name = re.sub(r'\([+\-]?\d*\)?$', '', dataset_name)
                
                # Skip if it's a symbolic parameter
                if '&' in dataset_name:
                    # Try to extract non-symbolic parts
                    dataset_name = self.symbolic_param_pattern.sub('', dataset_name)
                    # Clean up any remaining dots
                    dataset_name = re.sub(r'\.+', '.', dataset_name).strip('.')
                    if not dataset_name or dataset_name in ('.', '..', ''):
                        continue
                
                # Determine usage type from DISP parameter
                usage_type = 'INPUT'  # Default
                if 'DISP=' in line.upper():
                    # Look for DISP=(NEW or DISP=(MOD or DISP=(OLD
                    if re.search(r'DISP=\(?\s*(?:NEW|MOD)', line, re.IGNORECASE):
                        usage_type = 'OUTPUT'
                    elif re.search(r'DISP=\(?\s*(?:SHR|OLD)', line, re.IGNORECASE):
                        usage_type = 'INPUT'
                
                datasets.add(dataset_name)
                dataset_usage[dataset_name] = usage_type
                
                # Track concatenated datasets
                if dd_name in concatenated_groups:
                    concatenated_groups[dd_name].append(dataset_name)
                else:
                    concatenated_groups[dd_name] = [dataset_name]
        
        return {
            'datasets': list(datasets),
            'usage': dataset_usage,
            'concatenated': {k: v for k, v in concatenated_groups.items() if len(v) > 1}
        }
    
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of dependency patterns this parser supports.
        
        Returns:
            List of pattern names
        """
        return [
            'EXEC PGM',
            'EXEC PROC',
            'INCLUDE MEMBER',
            'DD DSN',
            'Concatenated Datasets',
            'Symbolic Parameters'
        ]
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser supports.
        
        Returns:
            List of file extensions
        """
        return ['.jcl']
