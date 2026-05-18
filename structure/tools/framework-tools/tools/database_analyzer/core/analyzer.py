#!/usr/bin/env python3
"""
Database Analyzer Tool for Legacy File System Analysis
Analyzes JCL, COBOL, and copybook files to discover Sequential and VSAM files
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

class DatabaseAnalyzer:
    def __init__(self, base_path: str, config: dict = None):
        self.base_path = Path(base_path)
        
        self.config = config or {}
        self.verbose = self.config.get('verbose', True)
        
        # Configurable root path for legacy code (defaults to base_path for backward compatibility)
        self.legacy_root = Path(self.config.get('legacy_root', self.base_path))
        
        # File extensions to search for (configurable)
        # Include .proc/.PROC for cataloged procedures containing DD/DSN statements
        self.jcl_extensions = self.config.get('jcl_extensions', ['.jcl', '.JCL', '.proc', '.PROC'])
        self.cbl_extensions = self.config.get('cbl_extensions', ['.cbl', '.CBL', '.cob', '.COB'])
        self.cpy_extensions = self.config.get('cpy_extensions', ['.cpy', '.CPY'])
        self.ctl_extensions = self.config.get('ctl_extensions', ['.ctl', '.CTL'])
        self.pli_extensions = self.config.get('pli_extensions', ['.inc', '.INC'])
        self.natural_extensions = self.config.get('natural_extensions', [
            '.nsp', '.NSP', '.nsn', '.NSN', '.nsc', '.NSC',
            '.nsl', '.NSL', '.nsg', '.NSG', '.nsd', '.NSD',
            '.nsa', '.NSA', '.ns8', '.NS8'
        ])

        # Filtering configuration
        self.exclude_system_files = self.config.get('exclude_system_files', True)
        self.exclude_backups = self.config.get('exclude_backups', True)
        self.exclude_duplicates = self.config.get('exclude_duplicates', True)

        # Configurable copybook-to-DSN mappings (replaces hardcoded CardDemo patterns)
        self.copybook_mappings = self.config.get('copybook_mappings', {})
        
        # VSAM key info extracted from .ctl DEFINE CLUSTER statements
        self.vsam_key_info = {}
        
        # PROC symbolic parameter defaults (resolved from PROC statements)
        self.proc_param_defaults = {}

        self.sequential_files = {}
        self.vsam_files = {}
        self.cobol_files = {}
        self.copybooks = {}
        self.file_to_table = {}
        self.excluded_files = {}
        self.processed_primaries = set()

        # Statistics
        self.stats = {
            'total_found': 0,
            'system_files': 0,
            'backups': 0,
            'duplicates': 0,
            'symbolic_params': 0,
            'nullfile_temp': 0,
            'included': 0,
            'jcl_files_scanned': 0,
            'cbl_files_scanned': 0,
            'cpy_files_scanned': 0,
            'ctl_files_scanned': 0,
            'pli_files_scanned': 0,
            'natural_files_scanned': 0
        }

    def is_system_file(self, dsn: str) -> bool:
        """Identify system/infrastructure files to exclude"""
        system_patterns = [
            r'\.LOADLIB$', r'SDFHLOAD', r'DFHCSD', r'\.STEPLIB',
            r'^OEM\.', r'\.PROCLIB', r'\.PARMLIB', r'ESDSRRDS\.PS$',
        ]
        dsn_upper = dsn.upper()
        return any(re.search(pattern, dsn_upper) for pattern in system_patterns)

    def is_backup_file(self, dsn: str) -> bool:
        """Identify backup files to exclude"""
        backup_patterns = [r'\.BKUP', r'\.BACKUP', r'\.BAK', r'\([\+\-]\d+\)']
        dsn_upper = dsn.upper()
        return any(re.search(pattern, dsn_upper) for pattern in backup_patterns)

    def get_primary_dsn(self, dsn: str) -> str:
        """Get primary DSN by removing format suffixes"""
        dsn_clean = re.sub(r'\.(PSCOMP|ARRYPS|VBPS|SEQ)$', '', dsn, flags=re.IGNORECASE)
        dsn_clean = re.sub(r'\.VSAM\.(ESDS|RRDS)$', '.VSAM.KSDS', dsn_clean, flags=re.IGNORECASE)
        dsn_clean = re.sub(r'\.PS$', '', dsn_clean, flags=re.IGNORECASE)
        return dsn_clean

    def should_prefer_over_existing(self, dsn: str, existing_dsn: str) -> bool:
        """Determine if new DSN should replace existing one"""
        if '.VSAM.KSDS' in dsn.upper() and '.VSAM.KSDS' not in existing_dsn.upper():
            return True
        if '.VSAM.' in dsn.upper() and '.PS' in existing_dsn.upper():
            return True
        return False


        
    def _find_files_by_extension(self, root_path: Path, extensions: List[str]) -> List[Path]:
        """Recursively find all files with given extensions under root_path"""
        files = []
        if not root_path.exists():
            if self.verbose:
                print(f"Warning: Path does not exist: {root_path}")
            return files
        
        for ext in extensions:
            # Use rglob for recursive search with pattern
            files.extend(root_path.rglob(f"*{ext}"))
        
        return sorted(files)
    
    def analyze_jcl_files(self):
        """Analyze JCL files for DD statements with improved multi-line handling and filtering"""
        jcl_files = self._find_files_by_extension(self.legacy_root, self.jcl_extensions)
        
        if self.verbose:
            print(f"Found {len(jcl_files)} JCL files to analyze")
        
        for jcl_file in jcl_files:
            self.stats['jcl_files_scanned'] += 1
            try:
                with open(jcl_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                # Merge JCL continuation lines
                merged_lines = []
                current_line = ""
                for line in lines:
                    # JCL continuation: line starts with // followed by spaces
                    if line.startswith('//') and len(line) > 2 and line[2] == ' ':
                        current_line += " " + line[2:].strip()
                    else:
                        if current_line:
                            merged_lines.append(current_line)
                        current_line = line.strip()
                if current_line:
                    merged_lines.append(current_line)

                content = "\n".join(merged_lines)

                # Find DD statements with DSN parameters
                dd_pattern = r'//(\w+)\s+DD\s+.*?DSN=([^,\s\n]+)'
                matches = re.findall(dd_pattern, content, re.IGNORECASE)

                # Also look for VSAM definitions in IDCAMS
                vsam_pattern = r'DEFINE\s+CLUSTER\s*\(\s*NAME\(([^)]+)\)'
                vsam_matches = re.findall(vsam_pattern, content, re.IGNORECASE | re.MULTILINE)

                for dd_name, dsn in matches:
                    self.stats['total_found'] += 1

                    # Filter NULLFILE and temporary datasets (&&name)
                    if self._is_nullfile_or_temp(dsn):
                        self.stats['nullfile_temp'] += 1
                        self.excluded_files[dsn] = "NULLFILE or temporary dataset"
                        if self.verbose:
                            print(f"  [SKIP] NULLFILE/temp: {dsn}")
                        continue

                    # Filter JCL symbolic parameters (DSNs starting with &)
                    if self._is_symbolic_parameter(dsn):
                        self.stats['symbolic_params'] += 1
                        self.excluded_files[dsn] = "JCL symbolic parameter (STEPLIB reference)"
                        if self.verbose:
                            print(f"  [SKIP] Symbolic parameter: {dsn}")
                        continue

                    # Resolve symbolic parameters within DSNs (e.g., E.VSAM.&TYP.MRTEO98)
                    dsn = self._resolve_symbolic_in_dsn(dsn, content)

                    # Apply filters
                    if self.exclude_system_files and self.is_system_file(dsn):
                        self.stats['system_files'] += 1
                        self.excluded_files[dsn] = "System file"
                        if self.verbose:
                            print(f"  [SKIP] System file: {dsn}")
                        continue

                    if self.exclude_backups and self.is_backup_file(dsn):
                        self.stats['backups'] += 1
                        self.excluded_files[dsn] = "Backup file"
                        if self.verbose:
                            print(f"  [SKIP] Backup file: {dsn}")
                        continue

                    primary_dsn = self.get_primary_dsn(dsn)

                    # Check for duplicates
                    if self.exclude_duplicates and primary_dsn in self.processed_primaries:
                        existing_dsn = None
                        for existing in list(self.sequential_files.keys()) + list(self.vsam_files.keys()):
                            if self.get_primary_dsn(existing) == primary_dsn:
                                existing_dsn = existing
                                break

                        if existing_dsn and self.should_prefer_over_existing(dsn, existing_dsn):
                            if existing_dsn in self.sequential_files:
                                del self.sequential_files[existing_dsn]
                            if existing_dsn in self.vsam_files:
                                del self.vsam_files[existing_dsn]
                            if self.verbose:
                                print(f"  [REPLACE] {existing_dsn} with {dsn}")
                        else:
                            self.stats['duplicates'] += 1
                            self.excluded_files[dsn] = f"Duplicate format (primary: {primary_dsn})"
                            if self.verbose:
                                print(f"  [SKIP] Duplicate format: {dsn}")
                            continue

                    # Process the file
                    file_type = self.determine_file_type(dsn, content)

                    if file_type == 'PS':
                        self.sequential_files[dsn] = {
                            'dd_name': dd_name,
                            'source_jcl': jcl_file.name,
                            'organization': 'PS',
                            'dsn': dsn,
                            'primary_dsn': primary_dsn
                        }
                        self.processed_primaries.add(primary_dsn)
                        self.stats['included'] += 1
                        if self.verbose:
                            print(f"  [INCLUDE] Sequential: {dsn}")

                    elif file_type in ['VSAM_KSDS', 'VSAM_ESDS', 'VSAM_RRDS']:
                        self.vsam_files[dsn] = {
                            'dd_name': dd_name,
                            'source_jcl': jcl_file.name,
                            'organization': file_type,
                            'dsn': dsn,
                            'primary_dsn': primary_dsn
                        }
                        self.processed_primaries.add(primary_dsn)
                        self.stats['included'] += 1
                        if self.verbose:
                            print(f"  [INCLUDE] VSAM {file_type}: {dsn}")

                # Process VSAM definitions
                for vsam_name in vsam_matches:
                    if not self.is_system_file(vsam_name) and not self.is_backup_file(vsam_name):
                        file_type = self.determine_file_type(vsam_name, content)
                        primary_dsn = self.get_primary_dsn(vsam_name)
                        if primary_dsn not in self.processed_primaries:
                            self.vsam_files[vsam_name] = {
                                'dd_name': 'VSAM_CLUSTER',
                                'source_jcl': jcl_file.name,
                                'organization': file_type,
                                'dsn': vsam_name,
                                'primary_dsn': primary_dsn
                            }
                            self.processed_primaries.add(primary_dsn)
                            self.stats['included'] += 1

            except Exception as e:
                print(f"Error processing JCL file {jcl_file}: {e}")
    def _is_nullfile_or_temp(self, dsn: str) -> bool:
        """Check if DSN is NULLFILE or a temporary dataset (&&name)."""
        dsn_upper = dsn.upper().strip()
        if dsn_upper == 'NULLFILE':
            return True
        if dsn_upper.startswith('&&'):
            return True
        if dsn_upper == 'DUMMY':
            return True
        return False

    def _is_symbolic_parameter(self, dsn: str) -> bool:
        """Check if DSN is entirely a JCL symbolic parameter (e.g., &EAFMLIB, &EY32LIB).

        These are typically STEPLIB references, not data files.
        A DSN that starts with & and contains no dots is a pure symbolic reference.
        DSNs containing & within a longer name (e.g., E.VSAM.&TYP.MRTEO98) are
        handled separately by _resolve_symbolic_in_dsn.
        """
        dsn_stripped = dsn.strip()
        if dsn_stripped.startswith('&') and '.' not in dsn_stripped:
            return True
        return False

    def _resolve_symbolic_in_dsn(self, dsn: str, content: str) -> str:
        """Resolve symbolic parameters embedded within DSNs.

        E.g., E.VSAM.&TYP.MRTEO98 should resolve &TYP using the PROC's
        default parameter value found in the PROC statement.
        """
        if '&' not in dsn:
            return dsn

        # Extract PROC default parameter values from content
        if not self.proc_param_defaults:
            self._extract_proc_defaults(content)

        resolved = dsn
        for param_name, param_value in self.proc_param_defaults.items():
            resolved = resolved.replace(f'&{param_name}', param_value)

        # Clean up any remaining unresolved symbolics by removing them
        # (e.g., &TYP with no default becomes empty, leaving E.VSAM..MRTEO98)
        resolved = re.sub(r'&\w+', '', resolved)
        # Clean up double dots from removed symbolics
        while '..' in resolved:
            resolved = resolved.replace('..', '.')
        # Remove leading/trailing dots
        resolved = resolved.strip('.')

        return resolved

    def _extract_proc_defaults(self, content: str) -> None:
        """Extract default parameter values from PROC statements in content."""
        # Match PROC statement and its continuation lines
        for line in content.split('\n'):
            if re.search(r'\bPROC\b', line, re.IGNORECASE):
                # Extract param=value pairs
                for match in re.finditer(r'(\w+)=([A-Za-z0-9#@$.]+)', line):
                    param_name, param_value = match.groups()
                    if param_name.upper() != 'PROC':
                        self.proc_param_defaults[param_name.upper()] = param_value

    def analyze_ctl_files(self):
        """Analyze .ctl files for IDCAMS DEFINE CLUSTER statements.

        Extracts VSAM key length/offset info that can improve VSAM KSDS
        primary key generation in DDL output.
        """
        ctl_files = self._find_files_by_extension(self.legacy_root, self.ctl_extensions)

        if self.verbose:
            print(f"Found {len(ctl_files)} CTL files to analyze")

        for ctl_file in ctl_files:
            self.stats['ctl_files_scanned'] += 1
            try:
                with open(ctl_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Remove JCL continuation markers (dash at end of line)
                content_clean = re.sub(r'\s*-\s*\n', ' ', content)

                # Look for DEFINE CLUSTER or DEF CL patterns
                # Use a simpler approach: find the keyword, then extract the full block
                cluster_start = re.compile(
                    r'DEF(?:INE)?\s+CL(?:USTER)?\s*\(',
                    re.IGNORECASE
                )

                for match in cluster_start.finditer(content_clean):
                    start_pos = match.end() - 1  # Position of opening (
                    # Find matching closing paren (handle nesting)
                    cluster_def = self._extract_balanced_parens(content_clean, start_pos)
                    if not cluster_def:
                        continue

                    # Extract NAME
                    name_match = re.search(r'NAME\(([^)]+)\)', cluster_def, re.IGNORECASE)
                    if not name_match:
                        continue
                    cluster_name = name_match.group(1).strip()

                    # Extract KEYS(length offset)
                    keys_match = re.search(r'KEYS\((\d+)\s+(\d+)\)', cluster_def, re.IGNORECASE)
                    key_length = int(keys_match.group(1)) if keys_match else None
                    key_offset = int(keys_match.group(2)) if keys_match else None

                    # Extract RECSZ(avg max)
                    recsz_match = re.search(r'RECSZ\((\d+)\s+(\d+)\)', cluster_def, re.IGNORECASE)
                    rec_avg = int(recsz_match.group(1)) if recsz_match else None
                    rec_max = int(recsz_match.group(2)) if recsz_match else None

                    self.vsam_key_info[cluster_name.upper()] = {
                        'key_length': key_length,
                        'key_offset': key_offset,
                        'record_size_avg': rec_avg,
                        'record_size_max': rec_max,
                        'source_file': ctl_file.name
                    }

                    if self.verbose:
                        keys_str = f"KEYS({key_length},{key_offset})" if key_length else "no keys"
                        print(f"  [CTL] {cluster_name}: {keys_str}")

            except Exception as e:
                print(f"Error processing CTL file {ctl_file}: {e}")

    def _extract_balanced_parens(self, text: str, start: int) -> Optional[str]:
        """Extract content within balanced parentheses starting at position start."""
        if start >= len(text) or text[start] != '(':
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    return text[start + 1:i]
        return None
    def _get_leaf_fields(self, copybook_info: Dict) -> List[Dict]:
        """Get leaf-level fields from a copybook, handling both COBOL and PL/I conventions.

        COBOL typically uses level 05 for data fields under a level 01 record.
        PL/I uses level 3 for leaf fields under a level 1 DCL.

        This method identifies leaf fields by finding fields that are not group headers
        (i.e., fields that have an sql_type that isn't just a group placeholder).
        It returns the lowest-level fields that have actual data types.
        """
        fields = copybook_info.get('fields', [])
        if not fields:
            return []

        # A field is a leaf if no other field has it as a parent (higher level before next same/lower level)
        # Simple approach: collect fields that have sql_type (actual data, not group headers)
        # Group headers in COBOL have no PIC clause, so they won't be in our parsed fields
        # All parsed fields are leaf fields since we only parse fields with PIC/type declarations
        leaf_fields = [f for f in fields if f.get('sql_type') and f['sql_type'] != 'TEXT' or f.get('sql_type') == 'TEXT']

        return leaf_fields

    def analyze_pli_copybooks(self):
        """Analyze PL/I include files (.inc) for record structures.

        PL/I uses CHAR(n), FIXED BIN(n), FIXED DEC(n,m), BIT(n) instead of
        COBOL PIC clauses. This method parses PL/I type declarations and adds
        them to the copybooks dictionary.
        """
        pli_files = self._find_files_by_extension(self.legacy_root, self.pli_extensions)

        if self.verbose:
            print(f"Found {len(pli_files)} PL/I include files to analyze")

        for pli_file in pli_files:
            self.stats['pli_files_scanned'] += 1
            try:
                with open(pli_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                fields = self.parse_pli_record(content)
                if fields:
                    self.copybooks[pli_file.stem] = {
                        'fields': fields,
                        'source_file': pli_file.name,
                        'language': 'PLI'
                    }

            except Exception as e:
                print(f"Error processing PL/I include {pli_file}: {e}")

    def analyze_natural_files(self):
        """Analyze Natural source files for database and file references.

        Natural programs access Adabas databases via VIEW OF statements and
        work files via DEFINE/READ/WRITE WORK FILE statements. Local/Global
        Data Areas (.NSL/.NSG) may contain VIEW definitions that map logical
        names to physical Adabas files.
        """
        natural_files = self._find_files_by_extension(self.legacy_root, self.natural_extensions)

        if self.verbose:
            print(f"Found {len(natural_files)} Natural files to analyze")

        # Patterns for Natural database/file access
        view_pattern = re.compile(
            r'\bDEFINE\s+DATA\b.*?\b(\w+)\s+VIEW\s+OF\s+(\w+)',
            re.IGNORECASE | re.DOTALL
        )
        work_file_pattern = re.compile(
            r'\bDEFINE\s+WORK\s+FILE\s+(\d+)\s+(?:[\'"]([^\'"]+)[\'"]|(\w+))',
            re.IGNORECASE
        )
        read_pattern = re.compile(
            r'\b(?:FIND|READ|GET|HISTOGRAM)\s+(\w+)\b',
            re.IGNORECASE
        )

        adabas_files = {}  # physical_file -> {sources, views}

        for nat_file in natural_files:
            self.stats['natural_files_scanned'] += 1
            try:
                with open(nat_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Extract VIEW OF references (maps logical name to Adabas file)
                for match in view_pattern.finditer(content):
                    logical_name = match.group(1)
                    physical_file = match.group(2)
                    if physical_file not in adabas_files:
                        adabas_files[physical_file] = {
                            'views': set(),
                            'sources': set()
                        }
                    adabas_files[physical_file]['views'].add(logical_name)
                    adabas_files[physical_file]['sources'].add(nat_file.name)

                # Extract WORK FILE references
                for match in work_file_pattern.finditer(content):
                    file_num = match.group(1)
                    target = match.group(2) or match.group(3)
                    if target:
                        dsn = f"WORK-FILE-{file_num}:{target}"
                        if dsn not in self.sequential_files:
                            self.sequential_files[dsn] = {
                                'dd_name': f'WORKFILE{file_num}',
                                'organization': 'PS',
                                'source_jcl': nat_file.name,
                                'dsn': dsn,
                                'primary_dsn': dsn,
                                'natural_work_file': True
                            }

            except Exception as e:
                print(f"Error processing Natural file {nat_file}: {e}")

        # Register discovered Adabas files as VSAM (Adabas uses similar keyed access)
        for physical_file, info in adabas_files.items():
            dsn = f"ADABAS:{physical_file}"
            if dsn not in self.vsam_files:
                self.vsam_files[dsn] = {
                    'dd_name': physical_file,
                    'organization': 'VSAM_KSDS',
                    'source_jcl': ', '.join(sorted(info['sources'])),
                    'dsn': dsn,
                    'primary_dsn': dsn,
                    'adabas_file': True,
                    'views': sorted(info['views']),
                    'source_natural': sorted(info['sources'])
                }

        if self.verbose and adabas_files:
            print(f"Found {len(adabas_files)} Adabas file references from Natural code")


    def parse_pli_record(self, content: str) -> List[Dict]:
        """Parse PL/I record structure from include file content.

        Handles PL/I type declarations:
        - CHAR(n) → VARCHAR(n)
        - FIXED BIN(n) → INTEGER or BIGINT
        - FIXED DEC(n,m) → DECIMAL(n,m)
        - BIT(n) → VARCHAR(ceil(n/8))
        - FLOAT BIN(n) → REAL or DOUBLE PRECISION
        """
        fields = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('/*') or line.startswith('*'):
                continue

            # Match PL/I field declarations:
            # level name TYPE(params) [UNALIGNED]
            # e.g., 3 FURN CHAR(3),
            # e.g., 3 NUM_SECOND_NAMES FIXED BIN(15) UNALIGNED,
            # e.g., 5 GROUP_CODE CHAR(1),
            pli_pattern = re.compile(
                r'(\d+)\s+(\w+)\s+'
                r'(CHAR|FIXED\s+BIN|FIXED\s+DEC|BIT|FLOAT\s+BIN|FLOAT\s+DEC)'
                r'\(([^)]+)\)',
                re.IGNORECASE
            )

            match = pli_pattern.search(line)
            if match:
                level = int(match.group(1))
                name = match.group(2)
                type_name = match.group(3).upper().strip()
                params = match.group(4).strip()

                sql_type, length, precision, scale = self._pli_type_to_sql(type_name, params)

                fields.append({
                    'level': level,
                    'name': name.replace('-', '_').lower(),
                    'pic': f"{type_name}({params})",
                    'sql_type': sql_type,
                    'length': length,
                    'precision': precision,
                    'scale': scale
                })
            else:
                # Also match group-level declarations without a type (structure grouping)
                group_pattern = re.compile(r'(\d+)\s+(\w+)\s*,', re.IGNORECASE)
                group_match = group_pattern.match(line)
                if group_match:
                    level = int(group_match.group(1))
                    name = group_match.group(2)
                    # Skip group-level entries (they don't map to columns)

        return fields

    def _pli_type_to_sql(self, type_name: str, params: str) -> Tuple[str, int, int, int]:
        """Convert PL/I type declaration to SQL type.

        Args:
            type_name: PL/I type (CHAR, FIXED BIN, FIXED DEC, BIT, FLOAT BIN)
            params: Parameter string (e.g., '3', '15', '10,2')

        Returns:
            Tuple of (sql_type, length, precision, scale)
        """
        type_name = re.sub(r'\s+', ' ', type_name.upper().strip())

        if type_name == 'CHAR':
            length = int(params)
            if length <= 255:
                return f'VARCHAR({length})', length, 0, 0
            return 'TEXT', length, 0, 0

        elif type_name == 'FIXED BIN':
            bits = int(params)
            if bits <= 15:
                return 'SMALLINT', 2, bits, 0
            elif bits <= 31:
                return 'INTEGER', 4, bits, 0
            else:
                return 'BIGINT', 8, bits, 0

        elif type_name == 'FIXED DEC':
            parts = [p.strip() for p in params.split(',')]
            precision = int(parts[0])
            scale = int(parts[1]) if len(parts) > 1 else 0
            return f'DECIMAL({precision},{scale})', precision, precision, scale

        elif type_name == 'BIT':
            bits = int(params)
            # Store as VARCHAR with byte-equivalent length
            byte_len = max(1, (bits + 7) // 8)
            return f'VARCHAR({byte_len})', byte_len, 0, 0

        elif type_name in ('FLOAT BIN', 'FLOAT DEC'):
            bits = int(params)
            if bits <= 21:
                return 'REAL', 4, bits, 0
            return 'DOUBLE PRECISION', 8, bits, 0

        return 'TEXT', 0, 0, 0

    
    def determine_file_type(self, dsn: str, content: str) -> str:
        """Determine file type based on DSN and JCL content"""
        dsn_upper = dsn.upper()
        
        if '.PS' in dsn_upper:
            return 'PS'
        elif '.VSAM.KSDS' in dsn_upper or dsn_upper.endswith('.KSDS'):
            return 'VSAM_KSDS'
        elif '.VSAM.ESDS' in dsn_upper or dsn_upper.endswith('.ESDS'):
            return 'VSAM_ESDS'
        elif '.VSAM.RRDS' in dsn_upper or dsn_upper.endswith('.RRDS'):
            return 'VSAM_RRDS'
        elif '.VSAM.' in dsn_upper:
            return 'VSAM_KSDS'  # Default VSAM type
        else:
            return 'PS'  # Default to sequential
    
    def analyze_cobol_files(self):
        """Analyze COBOL files for SELECT statements and file definitions"""
        cbl_files = self._find_files_by_extension(self.legacy_root, self.cbl_extensions)
        
        if self.verbose:
            print(f"Found {len(cbl_files)} COBOL files to analyze")
        
        for cbl_file in cbl_files:
            self.stats['cbl_files_scanned'] += 1
            try:
                with open(cbl_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Find SELECT statements with better pattern matching
                select_pattern = r'SELECT\s+(\w+(?:-\w+)*)\s+ASSIGN\s+TO\s+(\w+)(?:.*?ORGANIZATION\s+IS\s+(\w+))?'
                matches = re.findall(select_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                
                for file_name, assign_to, org in matches:
                    org = org or 'SEQUENTIAL'
                    self.cobol_files[file_name] = {
                        'assign_to': assign_to,
                        'organization': org,
                        'source_cobol': cbl_file.name
                    }
                    
                    # Match with JCL files
                    if org.upper() in ['SEQUENTIAL', '']:
                        for dsn, jcl_info in self.sequential_files.items():
                            if jcl_info['dd_name'].upper() == assign_to.upper():
                                jcl_info['cobol_file'] = file_name
                                jcl_info['cobol_source'] = cbl_file.name
                    elif org.upper() == 'INDEXED':
                        for dsn, vsam_info in self.vsam_files.items():
                            if vsam_info['dd_name'].upper() == assign_to.upper():
                                vsam_info['cobol_file'] = file_name
                                vsam_info['cobol_source'] = cbl_file.name
                                
            except Exception as e:
                print(f"Error processing COBOL file {cbl_file}: {e}")
    
    def analyze_copybooks(self):
        """Analyze copybooks for record structures.

        Tries COBOL PIC parsing first, then falls back to PL/I parsing
        if no COBOL fields are found (handles mixed-language copybooks).
        """
        cpy_files = self._find_files_by_extension(self.legacy_root, self.cpy_extensions)

        if self.verbose:
            print(f"Found {len(cpy_files)} copybook files to analyze")

        for cpy_file in cpy_files:
            self.stats['cpy_files_scanned'] += 1
            try:
                with open(cpy_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Try COBOL parsing first
                fields = self.parse_cobol_record(content)

                # If no COBOL fields found, try PL/I parsing
                if not fields:
                    fields = self.parse_pli_record(content)
                    if fields and self.verbose:
                        print(f"  [PLI] Parsed {cpy_file.stem} as PL/I ({len(fields)} fields)")

                self.copybooks[cpy_file.stem] = {
                    'fields': fields,
                    'source_file': cpy_file.name
                }

            except Exception as e:
                print(f"Error processing copybook {cpy_file}: {e}")
    
    def parse_cobol_record(self, content: str) -> List[Dict]:
        """Parse COBOL record structure from copybook content"""
        fields = []
        lines = content.split('\n')
        
        for line in lines:
            # Remove line numbers and clean up
            line = re.sub(r'^\d{6}', '', line)
            line = line.strip()
            
            if not line or line.startswith('*') or line.startswith('/'):
                continue
                
            # Match field definitions (01, 05, 10, etc. levels)
            field_pattern = r'(\d{2})\s+(\w+(?:-\w+)*)\s+(?:REDEFINES\s+\w+\s+)?PIC\s+([X9SAVCZ\(\)\d\-\+\.V]+)(?:\s+VALUE\s+[^.]+)?'
            match = re.search(field_pattern, line, re.IGNORECASE)
            
            if match:
                level, name, pic = match.groups()
                sql_type, length, precision, scale = self.parse_pic_clause(pic)
                
                fields.append({
                    'level': int(level),
                    'name': name.replace('-', '_').lower(),
                    'pic': pic,
                    'sql_type': sql_type,
                    'length': length,
                    'precision': precision,
                    'scale': scale
                })
        
        return fields
    
    def parse_pic_clause(self, pic: str) -> Tuple[str, int, int, int]:
        """Parse PIC clause to determine SQL type, length, precision, scale"""
        pic = pic.upper().strip()
        length = 0
        precision = 0
        scale = 0
        
        # Handle signed fields
        is_signed = 'S' in pic
        
        # Handle decimal fields
        has_decimal = 'V' in pic
        
        if 'X' in pic:
            # Character field - PIC X(n) or PIC XXX
            length_match = re.search(r'X\((\d+)\)', pic)
            if length_match:
                length = int(length_match.group(1))
            else:
                length = pic.count('X')
            
            if length <= 255:
                return f'VARCHAR({length})', length, 0, 0
            else:
                return 'TEXT', length, 0, 0
                
        elif '9' in pic:
            # Numeric field - PIC 9(n) or PIC 999
            if has_decimal:
                # Handle decimal: S9(7)V99 or 9(5)V9(2)
                parts = pic.split('V')
                integer_part = parts[0]
                decimal_part = parts[1] if len(parts) > 1 else ''
                
                # Extract integer digits
                int_match = re.search(r'9\((\d+)\)', integer_part)
                if int_match:
                    precision = int(int_match.group(1))
                else:
                    precision = integer_part.count('9')
                
                # Extract decimal digits
                dec_match = re.search(r'9\((\d+)\)', decimal_part)
                if dec_match:
                    scale = int(dec_match.group(1))
                else:
                    scale = decimal_part.count('9')
                
                total_precision = precision + scale
                return f'DECIMAL({total_precision}, {scale})', total_precision, precision, scale
            else:
                # Integer field
                length_match = re.search(r'9\((\d+)\)', pic)
                if length_match:
                    length = int(length_match.group(1))
                else:
                    length = pic.count('9')
                
                if length <= 4:
                    return 'INTEGER', length, length, 0
                elif length <= 9:
                    return 'BIGINT', length, length, 0
                else:
                    return f'DECIMAL({length}, 0)', length, length, 0
        
        elif 'A' in pic:
            # Alphabetic field - PIC A(n) or PIC AAA
            length_match = re.search(r'A\((\d+)\)', pic)
            if length_match:
                length = int(length_match.group(1))
            else:
                length = pic.count('A')
            return f'VARCHAR({length})', length, 0, 0
        
        # Handle COMP fields
        if 'COMP-3' in pic or 'COMP3' in pic:
            # Packed decimal
            return f'DECIMAL({precision or 15}, {scale or 2})', precision or 15, precision or 15, scale or 2
        elif 'COMP' in pic:
            # Binary
            return 'INTEGER', 4, 4, 0
            
        return 'TEXT', 0, 0, 0
    
    def find_matching_copybook(self, dsn: str) -> Optional[Dict]:
        """Find matching copybook for a given DSN with improved matching.

        Uses configurable copybook_mappings from config instead of hardcoded patterns.
        Falls back to partial name matching if no explicit mapping is found.
        """
        dsn_upper = dsn.upper()

        # Use configurable copybook mappings (from config)
        for pattern, copybook in self.copybook_mappings.items():
            if pattern.upper() in dsn_upper and copybook in self.copybooks:
                return self.copybooks[copybook]

        # Partial name matching: look for copybook names that appear as a
        # complete segment in the DSN (between dots). This avoids false matches
        # where a short copybook name appears as a substring of an unrelated segment.
        dsn_parts = dsn_upper.replace('.', ' ').replace('-', ' ').split()
        for dsn_part in dsn_parts:
            for cpy_name, cpy_info in self.copybooks.items():
                cpy_upper = cpy_name.upper()
                # Require exact match of a DSN segment to the copybook name
                if dsn_part == cpy_upper:
                    return cpy_info

        # Looser matching: check if copybook name is contained in a DSN segment
        # but only if the copybook name is at least 4 chars (avoid short false matches)
        for dsn_part in dsn_parts:
            for cpy_name, cpy_info in self.copybooks.items():
                cpy_upper = cpy_name.upper()
                if len(cpy_upper) >= 4 and (cpy_upper in dsn_part or dsn_part in cpy_upper):
                    return cpy_info

        return None
    
    def find_natural_key_field(self, copybook_info: Dict) -> Optional[str]:
        """Find the natural key field for VSAM KSDS from copybook"""
        if not copybook_info or not copybook_info.get('fields'):
            return None

        leaf_fields = self._get_leaf_fields(copybook_info)
        if not leaf_fields:
            return None

        # Look for fields that are likely to be keys
        for field in leaf_fields:
            field_name = field['name'].lower()
            if (field_name.endswith('_id') or 
                field_name.endswith('_num') or
                field_name.endswith('_key') or
                'id' in field_name or
                'key' in field_name or
                'num' in field_name):
                return field['name']

        # If no obvious key found, return the first leaf field
        return leaf_fields[0]['name'] if leaf_fields else None
    
    def generate_sqlite_ddl(self) -> str:
        """Generate SQLite DDL for all discovered files"""
        ddl = "-- SQLite DDL for Legacy File System\n"
        ddl += "-- Generated by Database Analyzer Tool\n\n"

        self.file_to_table.clear()  # Reset for fresh generation

        # Generate tables for Sequential files
        for dsn, info in self.sequential_files.items():
            table_name = self.sanitize_table_name(dsn)
            if dsn in self.file_to_table:
                continue  # Skip duplicates

            self.file_to_table[dsn] = table_name

            ddl += f"-- Source: JCL file {info['source_jcl']}, DD name {info['dd_name']}\n"
            ddl += f"-- Sequential File: {dsn}\n"
            ddl += f"CREATE TABLE {table_name} (\n"
            ddl += "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
            ddl += "    sequence_number INTEGER NOT NULL,\n"

            # Try to find matching copybook and use actual fields
            copybook_info = self.find_matching_copybook(dsn)
            leaf_fields = self._get_leaf_fields(copybook_info) if copybook_info else []
            if leaf_fields:
                for field in leaf_fields:
                    ddl += f"    {field['name']} {field['sql_type']},\n"
            else:
                ddl += "    record_data TEXT,\n"

            ddl = ddl.rstrip(',\n') + "\n);\n\n"
            ddl += f"CREATE INDEX idx_{table_name}_seq ON {table_name}(sequence_number);\n\n"

        # Generate tables for VSAM files
        for dsn, info in self.vsam_files.items():
            table_name = self.sanitize_table_name(dsn)
            if dsn in self.file_to_table:
                continue  # Skip duplicates

            self.file_to_table[dsn] = table_name

            ddl += f"-- Source: JCL file {info['source_jcl']}, DD name {info['dd_name']}\n"
            ddl += f"-- VSAM File ({info['organization']}): {dsn}\n"
            ddl += f"CREATE TABLE {table_name} (\n"

            # Try to find matching copybook
            copybook_info = self.find_matching_copybook(dsn)
            leaf_fields = self._get_leaf_fields(copybook_info) if copybook_info else []
            if leaf_fields:
                if info['organization'] == 'VSAM_KSDS':
                    natural_key = self.find_natural_key_field(copybook_info)
                    primary_key_set = False

                    for field in leaf_fields:
                        if field['name'] == natural_key and not primary_key_set:
                            ddl += f"    {field['name']} {field['sql_type']} PRIMARY KEY,\n"
                            primary_key_set = True
                        else:
                            ddl += f"    {field['name']} {field['sql_type']},\n"

                    if not primary_key_set and leaf_fields:
                        first_field = leaf_fields[0]
                        ddl_lines = ddl.split('\n')
                        for i, line in enumerate(ddl_lines):
                            if first_field['name'] in line and 'PRIMARY KEY' not in line:
                                ddl_lines[i] = line.replace(f"{first_field['sql_type']},", f"{first_field['sql_type']} PRIMARY KEY,")
                                break
                        ddl = '\n'.join(ddl_lines)

                elif info['organization'] == 'VSAM_ESDS':
                    ddl += "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                    ddl += "    sequence_number INTEGER NOT NULL,\n"
                    for field in leaf_fields:
                        ddl += f"    {field['name']} {field['sql_type']},\n"

                elif info['organization'] == 'VSAM_RRDS':
                    ddl += "    relative_record_number INTEGER PRIMARY KEY,\n"
                    for field in leaf_fields:
                        ddl += f"    {field['name']} {field['sql_type']},\n"
            else:
                # No copybook found - use default structure
                ctl_info = self.vsam_key_info.get(dsn.upper())
                if info['organization'] == 'VSAM_KSDS':
                    if ctl_info and ctl_info.get('key_length'):
                        key_len = ctl_info['key_length']
                        ddl += f"    record_key VARCHAR({key_len}) PRIMARY KEY,  -- from DEFINE CLUSTER KEYS({key_len},{ctl_info.get('key_offset', 0)})\n"
                    else:
                        ddl += "    record_key VARCHAR(50) PRIMARY KEY,\n"
                elif info['organization'] == 'VSAM_ESDS':
                    ddl += "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                    ddl += "    sequence_number INTEGER NOT NULL,\n"
                else:  # RRDS
                    ddl += "    relative_record_number INTEGER PRIMARY KEY,\n"
                ddl += "    record_data TEXT,\n"

            ddl = ddl.rstrip(',\n') + "\n);\n\n"

        return ddl
    
    def generate_postgresql_ddl(self) -> str:
        """Generate PostgreSQL DDL for all discovered files"""
        ddl = "-- PostgreSQL DDL for Legacy File System\n"
        ddl += "-- Generated by Database Analyzer Tool\n\n"

        self.file_to_table.clear()  # Reset for fresh generation

        # Generate tables for Sequential files
        for dsn, info in self.sequential_files.items():
            table_name = self.sanitize_table_name(dsn)
            if dsn in self.file_to_table:
                continue

            self.file_to_table[dsn] = table_name

            ddl += f"-- Source: JCL file {info['source_jcl']}, DD name {info['dd_name']}\n"
            ddl += f"-- Sequential File: {dsn}\n"
            ddl += f"CREATE TABLE {table_name} (\n"
            ddl += "    id SERIAL PRIMARY KEY,\n"
            ddl += "    sequence_number INTEGER NOT NULL,\n"

            copybook_info = self.find_matching_copybook(dsn)
            leaf_fields = self._get_leaf_fields(copybook_info) if copybook_info else []
            if leaf_fields:
                for field in leaf_fields:
                    ddl += f"    {field['name']} {field['sql_type']},\n"
            else:
                ddl += "    record_data TEXT,\n"

            ddl = ddl.rstrip(',\n') + "\n);\n\n"
            ddl += f"CREATE INDEX idx_{table_name}_seq ON {table_name}(sequence_number);\n\n"

        # Generate tables for VSAM files
        for dsn, info in self.vsam_files.items():
            table_name = self.sanitize_table_name(dsn)
            if dsn in self.file_to_table:
                continue

            self.file_to_table[dsn] = table_name

            ddl += f"-- Source: JCL file {info['source_jcl']}, DD name {info['dd_name']}\n"
            ddl += f"-- VSAM File ({info['organization']}): {dsn}\n"
            ddl += f"CREATE TABLE {table_name} (\n"

            copybook_info = self.find_matching_copybook(dsn)
            leaf_fields = self._get_leaf_fields(copybook_info) if copybook_info else []
            if leaf_fields:
                if info['organization'] == 'VSAM_KSDS':
                    natural_key = self.find_natural_key_field(copybook_info)
                    primary_key_set = False

                    for field in leaf_fields:
                        if field['name'] == natural_key and not primary_key_set:
                            ddl += f"    {field['name']} {field['sql_type']} PRIMARY KEY,\n"
                            primary_key_set = True
                        else:
                            ddl += f"    {field['name']} {field['sql_type']},\n"

                    if not primary_key_set and leaf_fields:
                        first_field = leaf_fields[0]
                        ddl_lines = ddl.split('\n')
                        for i, line in enumerate(ddl_lines):
                            if first_field['name'] in line and 'PRIMARY KEY' not in line:
                                ddl_lines[i] = line.replace(f"{first_field['sql_type']},", f"{first_field['sql_type']} PRIMARY KEY,")
                                break
                        ddl = '\n'.join(ddl_lines)

                elif info['organization'] == 'VSAM_ESDS':
                    ddl += "    id SERIAL PRIMARY KEY,\n"
                    ddl += "    sequence_number INTEGER NOT NULL,\n"
                    for field in leaf_fields:
                        ddl += f"    {field['name']} {field['sql_type']},\n"

                elif info['organization'] == 'VSAM_RRDS':
                    ddl += "    relative_record_number INTEGER PRIMARY KEY,\n"
                    for field in leaf_fields:
                        ddl += f"    {field['name']} {field['sql_type']},\n"
            else:
                ctl_info = self.vsam_key_info.get(dsn.upper())
                if info['organization'] == 'VSAM_KSDS':
                    if ctl_info and ctl_info.get('key_length'):
                        key_len = ctl_info['key_length']
                        ddl += f"    record_key VARCHAR({key_len}) PRIMARY KEY,  -- from DEFINE CLUSTER KEYS({key_len},{ctl_info.get('key_offset', 0)})\n"
                    else:
                        ddl += "    record_key VARCHAR(50) PRIMARY KEY,\n"
                elif info['organization'] == 'VSAM_ESDS':
                    ddl += "    id SERIAL PRIMARY KEY,\n"
                    ddl += "    sequence_number INTEGER NOT NULL,\n"
                else:  # RRDS
                    ddl += "    relative_record_number INTEGER PRIMARY KEY,\n"
                ddl += "    record_data TEXT,\n"

            ddl = ddl.rstrip(',\n') + "\n);\n\n"

        return ddl
    
    def sanitize_table_name(self, name: str) -> str:
        """Convert DSN or file name to valid SQL table name"""
        # Remove dots and special characters, convert to lowercase
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
        # Ensure it starts with a letter
        if clean_name and clean_name[0].isdigit():
            clean_name = 'tbl_' + clean_name
        return clean_name
    
    def generate_migration_scripts(self, target: str) -> str:
        """Generate data migration scripts"""
        script = f"-- {target.upper()} Data Migration Scripts\n"
        script += "-- Generated by Database Analyzer Tool\n\n"
        
        for dsn, info in self.sequential_files.items():
            table_name = self.sanitize_table_name(dsn)
            script += f"-- Migration for {table_name}\n"
            script += f"-- Source: {dsn}\n"
            script += f"INSERT INTO {table_name} (sequence_number, record_data) VALUES\n"
            script += "-- Data to be loaded from source files\n"
            script += "-- Use appropriate ETL process for data conversion\n\n"
        
        return script

    def print_statistics(self):
        """Print analysis statistics"""
        print(f"\n{'='*60}")
        print("Analysis Summary:")
        print(f"{'='*60}")
        print(f"  JCL/PROC files scanned:      {self.stats['jcl_files_scanned']}")
        print(f"  COBOL files scanned:         {self.stats['cbl_files_scanned']}")
        print(f"  Copybook files scanned:      {self.stats['cpy_files_scanned']}")
        print(f"  CTL files scanned:           {self.stats['ctl_files_scanned']}")
        print(f"  PL/I include files scanned:  {self.stats['pli_files_scanned']}")
        print(f"  Natural files scanned:       {self.stats['natural_files_scanned']}")
        print(f"  Total DSNs found:            {self.stats['total_found']}")
        print(f"  System files excluded:       {self.stats['system_files']}")
        print(f"  Backup files excluded:       {self.stats['backups']}")
        print(f"  Symbolic params excluded:    {self.stats['symbolic_params']}")
        print(f"  NULLFILE/temp excluded:      {self.stats['nullfile_temp']}")
        print(f"  Duplicate formats excluded:  {self.stats['duplicates']}")
        print(f"  Files included:              {self.stats['included']}")
        print(f"{'='*60}\n")

    
    def run_analysis(self):
        """Run complete analysis"""
        print("Starting database analysis...")

        print("\nAnalyzing CTL files for VSAM definitions...")
        self.analyze_ctl_files()

        print("\nAnalyzing JCL/PROC files...")
        self.analyze_jcl_files()

        print("\nAnalyzing COBOL files...")
        self.analyze_cobol_files()

        print("\nAnalyzing copybooks...")
        self.analyze_copybooks()

        print("\nAnalyzing PL/I include files...")
        self.analyze_pli_copybooks()

        print("\nAnalyzing Natural files...")
        self.analyze_natural_files()

        self.print_statistics()

        print(f"Found {len(self.sequential_files)} Sequential files")
        print(f"Found {len(self.vsam_files)} VSAM files")
        print(f"Found {len(self.cobol_files)} COBOL file definitions")
        print(f"Found {len(self.copybooks)} copybooks (COBOL + PL/I)")
        if self.vsam_key_info:
            print(f"Found {len(self.vsam_key_info)} VSAM DEFINE CLUSTER definitions")

        return {
            'sequential_files': self.sequential_files,
            'vsam_files': self.vsam_files,
            'cobol_files': self.cobol_files,
            'copybooks': self.copybooks,
            'excluded_files': self.excluded_files,
            'vsam_key_info': self.vsam_key_info,
            'stats': self.stats
        }


def main():
    parser = argparse.ArgumentParser(description='Database Analyzer for Legacy File Systems')
    parser.add_argument('--base-path', required=True, help='Base path to project directory')
    parser.add_argument('--output-dir', required=True, help='Output directory for generated files')
    
    args = parser.parse_args()
    
    analyzer = DatabaseAnalyzer(args.base_path)
    results = analyzer.run_analysis()
    
    # Generate DDL files
    sqlite_ddl = analyzer.generate_sqlite_ddl()
    postgresql_ddl = analyzer.generate_postgresql_ddl()
    
    # Generate migration scripts
    sqlite_migration = analyzer.generate_migration_scripts('sqlite')
    postgresql_migration = analyzer.generate_migration_scripts('postgresql')
    
    # Write output files
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'sqlite_ddl.sql', 'w') as f:
        f.write(sqlite_ddl)
    
    with open(output_dir / 'postgresql_ddl.sql', 'w') as f:
        f.write(postgresql_ddl)
    
    with open(output_dir / 'sqlite_migration.sql', 'w') as f:
        f.write(sqlite_migration)
    
    with open(output_dir / 'postgresql_migration.sql', 'w') as f:
        f.write(postgresql_migration)
    
    print(f"Analysis complete. Files generated in {output_dir}")

if __name__ == '__main__':
    main()