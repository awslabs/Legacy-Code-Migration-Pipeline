"""
Dependencies schema for artifact dependency tracking.

This module provides a DependenciesSchema class that defines both the artifact_dependencies
table and the inventory table. This allows JOIN-based queries to retrieve language information
for dependencies by joining with the inventory table.

During the reorganization phase, this provides the necessary schema definitions to support
cross-language dependency analysis and language-based filtering.
"""

class DependenciesSchema:
    """
    Dependencies schema for shared infrastructure.
    
    This schema defines both the artifact_dependencies table and the inventory table
    to support JOIN-based language retrieval. The inventory table provides language
    information that can be joined with dependencies for cross-language analysis.
    """
    
    @property
    def record_type(self) -> int:
        """Return -2 to indicate this is a dependencies schema."""
        return -2
    
    @property
    def record_name(self) -> str:
        return "Artifact Dependencies"
    
    def get_table_definitions(self):
        """Return basic table definitions for dependencies and inventory.
        
        This schema includes both the artifact_dependencies table and the inventory table
        to support JOIN-based language retrieval queries. The inventory table provides
        language information that can be joined with dependencies.
        
        Also includes program_file_mapping table for program-level dependency tracking.
        """
        return {
            'artifact_dependencies': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'source_artifact_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'source_artifact_type', 'type': 'VARCHAR(20)', 'nullable': False},
                    {'name': 'target_artifact_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'target_artifact_type', 'type': 'VARCHAR(20)', 'nullable': False},
                    {'name': 'dependency_type', 'type': 'VARCHAR(20)', 'nullable': False},
                    {'name': 'source_file_path', 'type': 'VARCHAR(255)'},
                    {'name': 'line_number', 'type': 'INTEGER'},
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['source_artifact_name'], 'name': 'idx_dep_source'},
                    {'columns': ['target_artifact_name'], 'name': 'idx_dep_target'},
                    {'columns': ['dependency_type'], 'name': 'idx_dep_type'},
                    {'columns': ['source_artifact_type'], 'name': 'idx_dep_source_type'},
                    {'columns': ['target_artifact_type'], 'name': 'idx_dep_target_type'},
                    {'columns': ['source_artifact_name', 'target_artifact_name', 'dependency_type'], 'name': 'idx_dep_unique_combo', 'unique': True},
                ],
                'foreign_keys': []
            },
            'inventory': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'artifact_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'artifact_type', 'type': 'VARCHAR(20)'},
                    {'name': 'language', 'type': 'VARCHAR(20)'},
                    {'name': 'file_path', 'type': 'TEXT', 'nullable': False},
                    {'name': 'file_size', 'type': 'INTEGER'},
                    {'name': 'last_modified', 'type': 'REAL'},
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['artifact_name'], 'name': 'idx_inv_artifact_name', 'unique': True},
                    {'columns': ['artifact_type'], 'name': 'idx_inv_artifact_type'},
                    {'columns': ['language'], 'name': 'idx_inv_language'},
                ],
                'foreign_keys': []
            },
            'program_file_mapping': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'file_id', 'type': 'INTEGER', 'nullable': False},
                    {'name': 'program_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'program_index', 'type': 'INTEGER', 'nullable': False},
                    {'name': 'start_line', 'type': 'INTEGER', 'nullable': False},
                    {'name': 'end_line', 'type': 'INTEGER', 'nullable': False},
                    {'name': 'program_type', 'type': 'VARCHAR(20)', 'nullable': False},
                    {'name': 'language', 'type': 'VARCHAR(20)', 'nullable': False},
                    {'name': 'entry_points', 'type': 'TEXT'},
                    {'name': 'lines_of_code', 'type': 'INTEGER'},
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['file_id'], 'name': 'idx_pfm_file_id'},
                    {'columns': ['program_name'], 'name': 'idx_pfm_program_name'},
                    {'columns': ['file_id', 'program_name'], 'name': 'idx_pfm_file_program', 'unique': True},
                ],
                'foreign_keys': [
                    {'column': 'file_id', 'references': 'inventory(id)'}
                ]
            }
        }

__all__ = ['DependenciesSchema']