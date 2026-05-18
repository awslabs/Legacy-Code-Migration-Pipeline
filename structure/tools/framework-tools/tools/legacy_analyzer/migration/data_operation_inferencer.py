"""
Data Operation Inferencer for Migration Flow Export.

This module infers data operations (database and dataset operations) from
existing dependency data in the artifact_dependencies table.
"""

import re
import sqlite3
from typing import List, Dict, Optional, Set, Tuple


class DataOperationInferencer:
    """
    Infers data operations from existing dependency data.
    
    This class analyzes the artifact_dependencies table to extract:
    - Database operations (SQL, CICS file operations)
    - Dataset operations (file I/O, JCL DD statements)
    
    It infers operation types and modes from dependency metadata without
    requiring re-parsing of source code.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize data operation inferencer.
        
        Args:
            db_connection: Database connection object
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def infer_all_operations(self, programs: List[str]) -> Dict[str, List[Dict]]:
        """
        Infer all data operations for a list of programs.
        
        Args:
            programs: List of program names to analyze
            
        Returns:
            Dictionary with 'databases' and 'datasets' keys containing
            lists of operation dictionaries
        """
        return {
            'databases': self.infer_database_operations(programs),
            'datasets': self.infer_dataset_operations(programs)
        }
    
    def infer_database_operations(self, programs: List[str]) -> List[Dict]:
        """
        Infer database operations from SQL, CICS, and Natural dependencies.
        
        Analyzes dependencies with types:
        - EXEC_SQL: SQL statements
        - CICS_READ: CICS file read operations
        - CICS_WRITE: CICS file write operations
        - CICS_REWRITE: CICS file update operations
        - CICS_DELETE: CICS file delete operations
        - FILE_REF: Natural VIEW OF references (Adabas database access)
        
        Args:
            programs: List of program names to analyze
            
        Returns:
            List of database operation dictionaries with keys:
            - type: Database type (DB2, IMS, VSAM, etc.)
            - operation: Operation type (READ, WRITE, UPDATE, DELETE, SELECT, INSERT)
            - target: Table/file name
            - program: Program performing the operation
        """
        if not programs:
            return []
        
        operations = []
        
        # Query database-related dependencies
        placeholders = ','.join('?' * len(programs))
        query = f"""
            SELECT DISTINCT
                source_artifact_name,
                target_artifact_name,
                dependency_type,
                target_artifact_type
            FROM artifact_dependencies
            WHERE source_artifact_name IN ({placeholders})
            AND (
                dependency_type LIKE 'EXEC_SQL%'
                OR dependency_type LIKE 'CICS_READ%'
                OR dependency_type LIKE 'CICS_WRITE%'
                OR dependency_type LIKE 'CICS_REWRITE%'
                OR dependency_type LIKE 'CICS_DELETE%'
                OR dependency_type LIKE 'CICS_BROWSE%'
                OR dependency_type LIKE 'CICS_STARTBR%'
                OR dependency_type LIKE 'CICS_READNEXT%'
                OR dependency_type LIKE 'CICS_READPREV%'
                OR dependency_type = 'FILE_REF'
                OR target_artifact_type IN ('TABLE', 'VIEW', 'FILE')
            )
        """
        
        self.cursor.execute(query, programs)
        rows = self.cursor.fetchall()
        
        for row in rows:
            source_program, target_name, dep_type, target_type = row
            
            # Infer database type
            db_type = self._infer_db_type(dep_type, target_type)
            
            # Infer operation type
            operation_type = self._infer_operation_type(dep_type, target_name)
            
            # Extract target name (table/file)
            target = self._extract_target_name(target_name, dep_type)
            
            if target and operation_type:
                operations.append({
                    'type': db_type,
                    'operation': operation_type,
                    'target': target,
                    'program': source_program
                })
        
        return operations
    
    def infer_dataset_operations(self, programs: List[str]) -> List[Dict]:
        """
        Infer dataset operations from file dependencies.
        
        Analyzes dependencies with types:
        - DATASET: Dataset access
        - FILE_READ: File read operations
        - FILE_WRITE: File write operations
        - JCL_DD: JCL DD statement references
        - WORK_FILE: Natural DEFINE/READ/WRITE WORK FILE operations
        
        Note: FILE_REF dependencies are excluded here as they represent
        Adabas database references (Natural VIEW OF) and are handled by
        infer_database_operations instead.
        
        Args:
            programs: List of program names to analyze
            
        Returns:
            List of dataset operation dictionaries with keys:
            - name: Dataset name
            - mode: Access mode (INPUT, OUTPUT, INOUT)
            - programs: List of programs accessing this dataset
        """
        if not programs:
            return []
        
        # Track datasets and their access patterns
        dataset_info: Dict[str, Dict] = {}
        
        # Query dataset-related dependencies
        placeholders = ','.join('?' * len(programs))
        query = f"""
            SELECT DISTINCT
                source_artifact_name,
                target_artifact_name,
                dependency_type,
                target_artifact_type
            FROM artifact_dependencies
            WHERE source_artifact_name IN ({placeholders})
            AND (
                target_artifact_type = 'DATASET'
                OR dependency_type LIKE 'FILE_%'
                OR dependency_type LIKE 'JCL_DD%'
                OR dependency_type LIKE 'DATASET%'
                OR dependency_type = 'WORK_FILE'
            )
            AND dependency_type != 'FILE_REF'
        """
        
        self.cursor.execute(query, programs)
        rows = self.cursor.fetchall()
        
        for row in rows:
            source_program, target_name, dep_type, target_type = row
            
            # Extract dataset name
            dataset_name = self._extract_dataset_name(target_name)
            
            if not dataset_name:
                continue
            
            # Infer access mode
            mode = self._infer_dataset_mode(dep_type, target_name)
            
            # Track dataset info
            if dataset_name not in dataset_info:
                dataset_info[dataset_name] = {
                    'name': dataset_name,
                    'modes': set(),
                    'programs': set()
                }
            
            dataset_info[dataset_name]['modes'].add(mode)
            dataset_info[dataset_name]['programs'].add(source_program)
        
        # Convert to list format
        operations = []
        for dataset_name, info in dataset_info.items():
            # Determine final mode (if both INPUT and OUTPUT, use INOUT)
            modes = info['modes']
            if 'INPUT' in modes and 'OUTPUT' in modes:
                final_mode = 'INOUT'
            elif 'OUTPUT' in modes:
                final_mode = 'OUTPUT'
            elif 'INPUT' in modes:
                final_mode = 'INPUT'
            else:
                final_mode = 'INOUT'  # Conservative default
            
            operations.append({
                'name': dataset_name,
                'mode': final_mode,
                'programs': sorted(list(info['programs']))
            })
        
        return sorted(operations, key=lambda x: x['name'])
    
    def _infer_db_type(self, dependency_type: str, target_type: str) -> str:
        """
        Infer database type from dependency information.
        
        Args:
            dependency_type: Type of dependency
            target_type: Type of target artifact
            
        Returns:
            Database type (DB2, IMS, VSAM, IDMS, ADABAS, SQL)
        """
        dep_upper = dependency_type.upper()
        
        if 'DB2' in dep_upper:
            return 'DB2'
        elif 'IMS' in dep_upper:
            return 'IMS'
        elif 'VSAM' in dep_upper or 'CICS' in dep_upper:
            return 'VSAM'
        elif 'IDMS' in dep_upper:
            return 'IDMS'
        elif 'ADABAS' in dep_upper:
            return 'ADABAS'
        elif 'SQL' in dep_upper:
            return 'SQL'
        elif dep_upper == 'FILE_REF' and target_type == 'FILE':
            # Natural VIEW OF references point to Adabas files
            return 'ADABAS'
        else:
            return 'SQL'  # Default to SQL
    
    def _infer_operation_type(self, dependency_type: str, target_name: str) -> str:
        """
        Infer operation type from dependency type and target name.
        
        Args:
            dependency_type: Type of dependency
            target_name: Name of target (may contain SQL statement)
            
        Returns:
            Operation type (READ, WRITE, UPDATE, DELETE, SELECT, INSERT)
        """
        dep_upper = dependency_type.upper()
        target_upper = target_name.upper() if target_name else ''
        
        # CICS operations
        if 'CICS_READ' in dep_upper or 'CICS_STARTBR' in dep_upper or 'CICS_READNEXT' in dep_upper or 'CICS_READPREV' in dep_upper:
            return 'READ'
        elif 'CICS_BROWSE' in dep_upper:
            return 'READ'
        elif 'CICS_WRITE' in dep_upper:
            return 'WRITE'
        elif 'CICS_REWRITE' in dep_upper:
            return 'UPDATE'
        elif 'CICS_DELETE' in dep_upper:
            return 'DELETE'
        
        # SQL operations - parse from statement
        if 'EXEC_SQL' in dep_upper or 'SQL' in dep_upper:
            return self._parse_sql_operation(target_name)
        
        # File operations
        if 'READ' in dep_upper:
            return 'READ'
        elif 'WRITE' in dep_upper:
            return 'WRITE'
        
        # Natural FILE_REF (VIEW OF) - Adabas file access, default to READ
        # since Natural uses FIND/READ statements against views
        if dep_upper == 'FILE_REF':
            return 'READ'
        
        return 'UNKNOWN'
    
    def _parse_sql_operation(self, sql_statement: str) -> str:
        """
        Parse SQL statement to determine operation type.
        
        Args:
            sql_statement: SQL statement or table name
            
        Returns:
            Operation type (SELECT, INSERT, UPDATE, DELETE, UNKNOWN)
        """
        if not sql_statement:
            return 'UNKNOWN'
        
        sql_upper = sql_statement.upper().strip()
        
        # Check for SQL keywords
        if sql_upper.startswith('SELECT') or 'SELECT ' in sql_upper:
            return 'SELECT'
        elif sql_upper.startswith('INSERT') or 'INSERT ' in sql_upper:
            return 'INSERT'
        elif sql_upper.startswith('UPDATE') or 'UPDATE ' in sql_upper:
            return 'UPDATE'
        elif sql_upper.startswith('DELETE') or 'DELETE ' in sql_upper:
            return 'DELETE'
        elif sql_upper.startswith('MERGE') or 'MERGE ' in sql_upper:
            return 'MERGE'
        elif sql_upper.startswith('CREATE') or 'CREATE ' in sql_upper:
            return 'CREATE'
        elif sql_upper.startswith('DROP') or 'DROP ' in sql_upper:
            return 'DROP'
        elif sql_upper.startswith('ALTER') or 'ALTER ' in sql_upper:
            return 'ALTER'
        
        # If no SQL keyword found, might be just a table name
        # Default to SELECT (most common read operation)
        return 'SELECT'
    
    def _extract_target_name(self, target_name: str, dependency_type: str) -> Optional[str]:
        """
        Extract table/file name from target name or SQL statement.
        
        Args:
            target_name: Target name (may be SQL statement)
            dependency_type: Type of dependency
            
        Returns:
            Extracted table/file name or None
        """
        if not target_name:
            return None
        
        # If it's a SQL statement, try to extract table name
        if 'EXEC_SQL' in dependency_type.upper() or 'SQL' in dependency_type.upper():
            table_name = self._extract_table_from_sql(target_name)
            if table_name:
                return table_name
        
        # Otherwise, use target name as-is (cleaned)
        return target_name.strip()
    
    def _extract_table_from_sql(self, sql_statement: str) -> Optional[str]:
        """
        Extract table name from SQL statement.
        
        Args:
            sql_statement: SQL statement
            
        Returns:
            Table name or None
        """
        if not sql_statement:
            return None
        
        sql_upper = sql_statement.upper().strip()
        
        # Pattern for SELECT ... FROM table
        match = re.search(r'FROM\s+([A-Z0-9_]+)', sql_upper)
        if match:
            return match.group(1)
        
        # Pattern for INSERT INTO table
        match = re.search(r'INSERT\s+INTO\s+([A-Z0-9_]+)', sql_upper)
        if match:
            return match.group(1)
        
        # Pattern for UPDATE table
        match = re.search(r'UPDATE\s+([A-Z0-9_]+)', sql_upper)
        if match:
            return match.group(1)
        
        # Pattern for DELETE FROM table
        match = re.search(r'DELETE\s+FROM\s+([A-Z0-9_]+)', sql_upper)
        if match:
            return match.group(1)
        
        # If no pattern matches, might be just a table name
        # Check if it looks like a table name (alphanumeric + underscore)
        if re.match(r'^[A-Z0-9_]+$', sql_upper):
            return sql_upper
        
        return None
    
    def _extract_dataset_name(self, target_name: str) -> Optional[str]:
        """
        Extract dataset name from target name.
        
        Args:
            target_name: Target name (may include qualifiers)
            
        Returns:
            Dataset name or None
        """
        if not target_name:
            return None
        
        # Clean up the name
        name = target_name.strip()
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(DD:|DDNAME:)', '', name, flags=re.IGNORECASE)
        
        return name if name else None
    
    def _infer_dataset_mode(self, dependency_type: str, target_name: str) -> str:
        """
        Infer dataset access mode from dependency type and metadata.
        
        Args:
            dependency_type: Type of dependency
            target_name: Target name (may contain mode hints)
            
        Returns:
            Access mode (INPUT, OUTPUT, INOUT)
        """
        dep_upper = dependency_type.upper()
        target_upper = target_name.upper() if target_name else ''
        
        # Check dependency type
        if 'READ' in dep_upper or 'INPUT' in dep_upper:
            return 'INPUT'
        elif 'WRITE' in dep_upper or 'OUTPUT' in dep_upper:
            return 'OUTPUT'
        elif 'INOUT' in dep_upper or 'I-O' in dep_upper or 'UPDATE' in dep_upper:
            return 'INOUT'
        elif dep_upper == 'WORK_FILE':
            # Natural WORK FILE - typically used for both read and write
            return 'INOUT'
        
        # Check for JCL DISP parameter hints in target name
        if 'DISP=SHR' in target_upper or 'DISP=(SHR' in target_upper:
            return 'INPUT'
        elif 'DISP=OLD' in target_upper or 'DISP=(OLD' in target_upper:
            return 'INOUT'
        elif 'DISP=NEW' in target_upper or 'DISP=(NEW' in target_upper:
            return 'OUTPUT'
        elif 'DISP=MOD' in target_upper or 'DISP=(MOD' in target_upper:
            return 'OUTPUT'
        
        # Default to INOUT (most conservative)
        return 'INOUT'
    
    def get_operation_summary(self, programs: List[str]) -> Dict[str, int]:
        """
        Get summary statistics for data operations.
        
        Args:
            programs: List of program names to analyze
            
        Returns:
            Dictionary with operation counts
        """
        operations = self.infer_all_operations(programs)
        
        return {
            'total_database_operations': len(operations['databases']),
            'total_datasets': len(operations['datasets']),
            'unique_tables': len(set(op['target'] for op in operations['databases'])),
            'unique_datasets': len(set(op['name'] for op in operations['datasets']))
        }
