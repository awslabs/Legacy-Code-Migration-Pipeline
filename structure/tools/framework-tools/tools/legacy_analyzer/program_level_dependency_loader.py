"""Program-level dependency loader implementation.

This module extends the base DependencyLoader to support program-level dependency
tracking with file mapping and referential integrity validation.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from .dependency_loader import DependencyLoader
from .models.program_boundary import ProgramBoundary
from .models.dependency import Dependency


class ProgramLevelDependencyLoader(DependencyLoader):
    """Loads program-level dependency data with file mapping and validation.
    
    This class extends DependencyLoader to support:
    - Program-level dependency storage with file mapping
    - Batch insert operations for program dependencies
    - Validation for program-level referential integrity
    - Migration from file-level to program-level dependencies
    """
    
    def __init__(self, database):
        """Initialize program-level dependency loader.
        
        Args:
            database: Database adapter instance
        """
        super().__init__(database)
        self.program_stats = defaultdict(int)
    
    def store_program_dependencies(self, 
                                 file_path: str,
                                 programs: List[ProgramBoundary],
                                 dependencies: Dict[str, Dict[str, List[str]]]) -> Dict[str, int]:
        """Store dependencies with program-level granularity.
        
        Args:
            file_path: Path to the source file containing programs
            programs: List of program boundaries detected in the file
            dependencies: Dictionary mapping program names to their dependencies
                         Format: {program_name: {dep_type: [dep_list]}}
            
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            'programs_processed': 0,
            'programs_stored': 0,
            'dependencies_processed': 0,
            'dependencies_stored': 0,
            'errors': 0
        }
        
        try:
            # Store program-file mappings with proper indexing (0, 1, 2, 3...)
            for index, program in enumerate(programs):
                try:
                    self._store_program_file_mapping(file_path, program, index)
                    stats['programs_processed'] += 1
                    stats['programs_stored'] += 1
                except Exception as e:
                    print(f"  ⚠ Warning: Error storing program {program.program_name}: {str(e)}")
                    stats['errors'] += 1
            
            # Store program-level dependencies
            for program_name, program_deps in dependencies.items():
                try:
                    # Handle both old format (List[Dependency]) and new format (Dict[str, List[str]])
                    if isinstance(program_deps, dict):
                        # New format: {dep_type: [dep_list]}
                        for dep_type, dep_list in program_deps.items():
                            for dep_name in dep_list:
                                try:
                                    self._store_program_dependency_simple(
                                        program_name, dep_name, dep_type, file_path
                                    )
                                    stats['dependencies_processed'] += 1
                                    stats['dependencies_stored'] += 1
                                except Exception as e:
                                    # Skip individual dependency errors but continue processing
                                    stats['errors'] += 1
                    elif isinstance(program_deps, list):
                        # Old format: List[Dependency]
                        for dep in program_deps:
                            try:
                                # Validate that dep is actually a Dependency object
                                if not hasattr(dep, 'target_artifact'):
                                    # Skip invalid dependency (might be a string or other type)
                                    stats['errors'] += 1
                                    continue
                                self._store_program_dependency(program_name, dep, file_path)
                                stats['dependencies_processed'] += 1
                                stats['dependencies_stored'] += 1
                            except Exception as e:
                                # Skip individual dependency errors but continue processing
                                stats['errors'] += 1
                    else:
                        # Unknown format
                        print(f"  ⚠ Warning: Unknown dependency format for {program_name}: {type(program_deps)}")
                        stats['errors'] += 1
                except Exception as e:
                    print(f"  ⚠ Warning: Error storing dependencies for {program_name}: {str(e)}")
                    stats['errors'] += 1
            
            self.database.commit()
            
        except Exception as e:
            self.database.rollback()
            print(f"  ✗ Error: Failed to store program dependencies: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    def bulk_insert_program_dependencies(self, 
                                       program_dependencies: List[Dict[str, Any]], 
                                       skip_duplicates: bool = True) -> Dict[str, int]:
        """Bulk insert program-level dependency records for performance.
        
        Args:
            program_dependencies: List of program dependency dictionaries with keys:
                - source_program_name (required)
                - source_file_path (required)
                - target_program_name (required)
                - target_file_path (optional)
                - dependency_type (required)
                - line_number (optional)
            skip_duplicates: If True, skip duplicate entries; if False, update them
            
        Returns:
            Dictionary with load statistics
        """
        rows_to_insert = []
        stats = {
            'processed': 0,
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for idx, dep in enumerate(program_dependencies):
            stats['processed'] += 1
            
            try:
                # Validate record structure
                if not isinstance(dep, dict):
                    stats['skipped'] += 1
                    continue
                
                # Build row data for artifact_dependencies table
                row_data = {
                    'source_artifact_name': str(dep.get('source_program_name', '')).strip()[:44],
                    'source_artifact_type': 'PROGRAM',
                    'target_artifact_name': str(dep.get('target_program_name', '')).strip()[:44],
                    'target_artifact_type': str(dep.get('target_artifact_type', 'PROGRAM')).strip()[:20],
                    'dependency_type': str(dep.get('dependency_type', '')).strip()[:20],
                    'source_file_path': str(dep.get('source_file_path', '')).strip()[:255] or None,
                    'line_number': int(dep['line_number']) if dep.get('line_number') else None
                }
                
                # Validate required fields are not empty
                if not all([
                    row_data['source_artifact_name'],
                    row_data['target_artifact_name'],
                    row_data['dependency_type']
                ]):
                    stats['skipped'] += 1
                    continue
                
                # Check for duplicates
                cursor = self.database.cursor()
                cursor.execute(
                    """SELECT id FROM artifact_dependencies 
                       WHERE source_artifact_name = ? 
                       AND target_artifact_name = ? 
                       AND dependency_type = ?""",
                    (row_data['source_artifact_name'], 
                     row_data['target_artifact_name'],
                     row_data['dependency_type'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    if skip_duplicates:
                        stats['skipped'] += 1
                        continue
                    else:
                        # Update existing record
                        cursor.execute(
                            "DELETE FROM artifact_dependencies WHERE id = ?",
                            (existing[0],)
                        )
                        stats['updated'] += 1
                
                rows_to_insert.append(row_data)
                stats['inserted'] += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('artifact_dependencies', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
            
            except Exception as e:
                stats['errors'] += 1
                continue
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('artifact_dependencies', rows_to_insert)
            self.database.commit()
        
        return stats
    
    def validate_program_referential_integrity(self) -> Dict[str, Any]:
        """Validate program-level referential integrity.
        
        Checks that:
        1. All source programs exist in program_file_mapping
        2. All target programs exist in program_file_mapping (where applicable)
        3. Dependencies reference valid program names
        
        Returns:
            Dictionary with validation results and statistics
        """
        validation_results = {
            'valid': True,
            'total_dependencies': 0,
            'missing_source_programs': [],
            'missing_target_programs': [],
            'invalid_dependencies': [],
            'orphaned_programs': [],
            'statistics': {}
        }
        
        cursor = self.database.cursor()
        
        try:
            # Get all program dependencies
            cursor.execute("""
                SELECT source_artifact_name, target_artifact_name, dependency_type, id
                FROM artifact_dependencies 
                WHERE source_artifact_type = 'PROGRAM'
            """)
            dependencies = cursor.fetchall()
            validation_results['total_dependencies'] = len(dependencies)
            
            # Get all programs from program_file_mapping
            cursor.execute("SELECT DISTINCT program_name FROM program_file_mapping")
            existing_programs = {row[0] for row in cursor.fetchall()}
            
            # Validate each dependency
            for source_prog, target_prog, dep_type, dep_id in dependencies:
                # Check source program exists
                if source_prog not in existing_programs:
                    validation_results['missing_source_programs'].append({
                        'program_name': source_prog,
                        'dependency_id': dep_id,
                        'dependency_type': dep_type
                    })
                    validation_results['valid'] = False
                
                # Check target program exists (only for program-to-program dependencies)
                if target_prog not in existing_programs and dep_type in ['CALL', 'LINK', 'EXEC']:
                    validation_results['missing_target_programs'].append({
                        'program_name': target_prog,
                        'dependency_id': dep_id,
                        'dependency_type': dep_type
                    })
                    validation_results['valid'] = False
            
            # Check for orphaned programs (programs with no dependencies)
            cursor.execute("""
                SELECT pfm.program_name 
                FROM program_file_mapping pfm
                LEFT JOIN artifact_dependencies ad ON pfm.program_name = ad.source_artifact_name
                WHERE ad.source_artifact_name IS NULL
            """)
            orphaned = cursor.fetchall()
            validation_results['orphaned_programs'] = [row[0] for row in orphaned]
            
            # Generate statistics
            validation_results['statistics'] = {
                'total_programs': len(existing_programs),
                'programs_with_dependencies': len(existing_programs) - len(orphaned),
                'orphaned_programs_count': len(orphaned),
                'missing_source_count': len(validation_results['missing_source_programs']),
                'missing_target_count': len(validation_results['missing_target_programs']),
                'integrity_score': (
                    validation_results['total_dependencies'] - 
                    len(validation_results['missing_source_programs']) - 
                    len(validation_results['missing_target_programs'])
                ) / max(validation_results['total_dependencies'], 1)
            }
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['error'] = str(e)
        
        return validation_results
    
    def migrate_file_to_program_level(self, file_path: str) -> Dict[str, Any]:
        """Convert existing file-level dependencies to program-level.
        
        Args:
            file_path: Path to file to migrate
            
        Returns:
            Dictionary with migration results
        """
        migration_results = {
            'success': False,
            'file_dependencies_found': 0,
            'program_dependencies_created': 0,
            'programs_detected': 0,
            'errors': []
        }
        
        try:
            cursor = self.database.cursor()
            
            # Find file-level dependencies for this file
            cursor.execute("""
                SELECT source_artifact_name, target_artifact_name, dependency_type, line_number
                FROM artifact_dependencies 
                WHERE source_file_path = ? AND source_artifact_type != 'PROGRAM'
            """, (file_path,))
            
            file_deps = cursor.fetchall()
            migration_results['file_dependencies_found'] = len(file_deps)
            
            if file_deps:
                # Get file_id from inventory
                cursor.execute("SELECT id FROM inventory WHERE file_path = ?", (file_path,))
                file_result = cursor.fetchone()
                if not file_result:
                    migration_results['errors'].append(f"File not found in inventory: {file_path}")
                    return migration_results
                
                file_id = file_result[0]
                
                # Get programs for this file
                cursor.execute("""
                    SELECT program_name, start_line, end_line 
                    FROM program_file_mapping 
                    WHERE file_id = ?
                    ORDER BY start_line
                """, (file_id,))
                
                programs = cursor.fetchall()
                migration_results['programs_detected'] = len(programs)
                
                if programs:
                    # Map dependencies to programs based on line numbers
                    for source_name, target_name, dep_type, line_num in file_deps:
                        if line_num:
                            # Find which program contains this line
                            for prog_name, start_line, end_line in programs:
                                if start_line <= line_num <= end_line:
                                    # Create program-level dependency
                                    cursor.execute("""
                                        INSERT OR IGNORE INTO artifact_dependencies 
                                        (source_artifact_name, source_artifact_type, 
                                         target_artifact_name, target_artifact_type,
                                         dependency_type, source_file_path, line_number)
                                        VALUES (?, 'PROGRAM', ?, ?, ?, ?, ?)
                                    """, (prog_name, target_name, dep_type, dep_type, file_path, line_num))
                                    migration_results['program_dependencies_created'] += 1
                                    break
                        else:
                            # No line number - assign to first program
                            if programs:
                                prog_name = programs[0][0]
                                cursor.execute("""
                                    INSERT OR IGNORE INTO artifact_dependencies 
                                    (source_artifact_name, source_artifact_type, 
                                     target_artifact_name, target_artifact_type,
                                     dependency_type, source_file_path, line_number)
                                    VALUES (?, 'PROGRAM', ?, ?, ?, ?, ?)
                                """, (prog_name, target_name, dep_type, dep_type, file_path, None))
                                migration_results['program_dependencies_created'] += 1
                    
                    self.database.commit()
                    migration_results['success'] = True
                else:
                    migration_results['errors'].append("No programs found for file")
            else:
                migration_results['success'] = True  # Nothing to migrate
                
        except Exception as e:
            self.database.rollback()
            migration_results['errors'].append(str(e))
        
        return migration_results
    
    def _store_program_file_mapping(self, file_path: str, program: ProgramBoundary, program_index: int) -> None:
        """Store program-to-file mapping in database.
        
        Args:
            file_path: Path to the source file
            program: Program boundary information
            program_index: Index of the program within the file (0-based)
        """
        cursor = self.database.cursor()
        
        # Get file_id from inventory table, or create it if it doesn't exist
        cursor.execute("SELECT id FROM inventory WHERE file_path = ?", (file_path,))
        result = cursor.fetchone()
        if not result:
            # Insert file into inventory if it doesn't exist
            cursor.execute("""
                INSERT INTO inventory (artifact_name, artifact_type, language, file_path)
                VALUES (?, ?, ?, ?)
            """, (
                os.path.basename(file_path),
                'FILE',
                program.language,
                file_path
            ))
            file_id = cursor.lastrowid
        else:
            file_id = result[0]
        
        # Convert entry points to JSON
        entry_points_json = json.dumps(program.entry_points) if program.entry_points else None
        
        # Calculate lines of code
        lines_of_code = program.end_line - program.start_line + 1 if program.end_line and program.start_line else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO program_file_mapping 
            (file_id, program_name, program_index, start_line, end_line, 
             program_type, language, entry_points, lines_of_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_id,
            program.program_name,
            program_index,  # Now using the actual sequential program index (0, 1, 2, 3...)
            program.start_line,
            program.end_line,
            program.program_type.value,
            program.language,
            entry_points_json,
            lines_of_code
        ))
    
    def _store_program_dependency(self, program_name: str, dependency: Dependency, file_path: str) -> None:
        """Store a single program dependency.
        
        Args:
            program_name: Name of the source program
            dependency: Dependency object
            file_path: Path to the source file
        """
        cursor = self.database.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO artifact_dependencies 
            (source_artifact_name, source_artifact_type, target_artifact_name, 
             target_artifact_type, dependency_type, source_file_path, line_number)
            VALUES (?, 'PROGRAM', ?, ?, ?, ?, ?)
        """, (
            program_name,
            dependency.target_artifact,
            dependency.target_type,
            dependency.dependency_type,
            file_path,
            dependency.line_number
        ))
    
    def _store_program_dependency_simple(self, program_name: str, target_name: str, 
                                       dependency_type: str, file_path: str) -> None:
        """Store a simple program dependency (for mixed content).
        
        Args:
            program_name: Name of the source program
            target_name: Name of the target artifact
            dependency_type: Type of dependency (e.g., 'copybooks', 'calls', 'cics_links')
            file_path: Path to the source file
        """
        cursor = self.database.cursor()
        
        # Determine target artifact type based on dependency type
        # Map dependency types to artifact types
        target_artifact_type = 'PROGRAM'  # Default
        if dependency_type in ['copybooks', 'COPY']:
            target_artifact_type = 'COPYBOOK'
        elif dependency_type in ['datasets', 'DATASET', 'FILE_REF']:
            target_artifact_type = 'DATASET'
        elif dependency_type in ['sql_tables', 'SQL_TABLE']:
            target_artifact_type = 'TABLE'
        
        cursor.execute("""
            INSERT OR IGNORE INTO artifact_dependencies 
            (source_artifact_name, source_artifact_type, target_artifact_name, 
             target_artifact_type, dependency_type, source_file_path, line_number)
            VALUES (?, 'PROGRAM', ?, ?, ?, ?, NULL)
        """, (
            program_name,
            target_name,
            target_artifact_type,
            dependency_type,
            file_path
        ))