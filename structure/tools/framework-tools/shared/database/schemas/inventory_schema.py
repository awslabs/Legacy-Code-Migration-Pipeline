"""Schema definition for mainframe artifact inventory tables."""

from typing import Dict, List, Any


class InventorySchema:
    """Schema for mainframe artifact inventory management.
    
    This schema defines tables for storing mainframe artifact catalogs
    including JCL members, programs, copybooks, datasets, and CICS resources.
    These tables are used for artifact lifecycle analysis by comparing
    """
    
    @property
    def record_type(self) -> int:
        return -1
    
    @property
    def record_name(self) -> str:
        return "Artifact Inventory"
    
    def get_table_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Return table definitions for inventory management."""
        return {
            'inventory_jcl': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'member_name', 'type': 'VARCHAR(8)', 'nullable': False},
                    {'name': 'library_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'last_modified', 'type': 'DATE'},
                    {'name': 'size_lines', 'type': 'INTEGER'},
                    {'name': 'datasets', 'type': 'TEXT'},  # JSON array of dataset references
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['member_name'], 'name': 'idx_inv_jcl_member'},
                    {'columns': ['library_name'], 'name': 'idx_inv_jcl_library'},
                ],
                'foreign_keys': []
            },
            
            'inventory_programs': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'program_name', 'type': 'VARCHAR(8)', 'nullable': False},
                    {'name': 'library_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'link_date', 'type': 'DATE'},
                    {'name': 'size_bytes', 'type': 'INTEGER'},
                    {'name': 'entry_point', 'type': 'VARCHAR(16)'},
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['program_name'], 'name': 'idx_inv_prog_name'},
                    {'columns': ['library_name'], 'name': 'idx_inv_prog_library'},
                ],
                'foreign_keys': []
            },
            
            'inventory_copybooks': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'copybook_name', 'type': 'VARCHAR(8)', 'nullable': False},
                    {'name': 'library_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'last_modified', 'type': 'DATE'},
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['copybook_name'], 'name': 'idx_inv_copy_name'},
                ],
                'foreign_keys': []
            },
            
            'inventory_datasets': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'dataset_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'creation_date', 'type': 'DATE'},
                    {'name': 'last_referenced', 'type': 'DATE'},
                    {'name': 'size_mb', 'type': 'DECIMAL(12,2)'},
                    {'name': 'volume', 'type': 'VARCHAR(6)'},
                    {'name': 'dataset_type', 'type': 'VARCHAR(10)'},
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['dataset_name'], 'name': 'idx_inv_ds_name'},
                    {'columns': ['size_mb'], 'name': 'idx_inv_ds_size'},
                ],
                'foreign_keys': []
            },
            
            'inventory_cics': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'resource_name', 'type': 'VARCHAR(8)', 'nullable': False},
                    {'name': 'resource_type', 'type': 'VARCHAR(20)', 'nullable': False},
                    {'name': 'group_name', 'type': 'VARCHAR(8)'},
                    {'name': 'status', 'type': 'VARCHAR(20)'},
                    {'name': 'program_name', 'type': 'VARCHAR(8)'},  # For TRANSACTION type: associated program
                    # Enhanced columns for CICS metadata integration (Task 1.2)
                    {'name': 'dataset_name', 'type': 'VARCHAR(44)'},  # For FILE resources: MVS dataset name
                    {'name': 'description', 'type': 'TEXT'},  # Description for all resource types
                    {'name': 'language', 'type': 'VARCHAR(20)'},  # For PROGRAM resources: COBOL, PLI, ASM, etc.
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['resource_name'], 'name': 'idx_inv_cics_name'},
                    {'columns': ['resource_type'], 'name': 'idx_inv_cics_type'},
                    {'columns': ['program_name'], 'name': 'idx_inv_cics_program'},
                    # New indexes for enhanced columns
                    {'columns': ['dataset_name'], 'name': 'idx_inv_cics_dataset'},
                    {'columns': ['language'], 'name': 'idx_inv_cics_language'},
                ],
                'foreign_keys': []
            },
            
            'inventory': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'artifact_name', 'type': 'VARCHAR(44)', 'nullable': False},  # File name (e.g., "ZEXAMPLS")
                    {'name': 'filename', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'artifact_type', 'type': 'VARCHAR(20)', 'nullable': False},  # PROGRAM, MIXED, JCL, COPYBOOK, DATA
                    {'name': 'language', 'type': 'VARCHAR(20)', 'nullable': False},      # RPG, COBOL, ASM, MIXED
                    {'name': 'file_path', 'type': 'TEXT', 'nullable': False},
                    {'name': 'file_size', 'type': 'INTEGER'},
                    {'name': 'program_count', 'type': 'INTEGER', 'default': 0},          # Number of programs in file (0, 1, or N)
                    {'name': 'dominant_language', 'type': 'VARCHAR(20)'},               # NULL if no dominant language
                    {'name': 'dominant_type', 'type': 'VARCHAR(20)'},                   # NULL if no dominant type
                    {'name': 'analyzed', 'type': 'INTEGER', 'default': 0},
                    {'name': 'last_modified', 'type': 'REAL'},
                    # Missing artifacts tracking (for dependency completeness)
                    {'name': 'found', 'type': 'INTEGER', 'default': 1},                 # 1=exists in source, 0=referenced but not found
                    {'name': 'artifact_source', 'type': 'VARCHAR(20)', 'default': "'LOCAL'"},  # LOCAL, SYSTEM, EXTERNAL, MISSING
                    # Entry point tracking (for migration flow analysis)
                    {'name': 'is_entry_point', 'type': 'INTEGER', 'default': 0},        # 1=entry point, 0=not entry point
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['artifact_name'], 'name': 'idx_inv_artifact_name'},
                    {'columns': ['artifact_type'], 'name': 'idx_inv_artifact_type'},
                    {'columns': ['language'], 'name': 'idx_inv_language'},
                    {'columns': ['program_count'], 'name': 'idx_inv_program_count'},
                    {'columns': ['dominant_language'], 'name': 'idx_inv_dominant_language'},
                    {'columns': ['dominant_type'], 'name': 'idx_inv_dominant_type'},
                    {'columns': ['found'], 'name': 'idx_inv_found'},
                    {'columns': ['artifact_source'], 'name': 'idx_inv_artifact_source'},
                    {'columns': ['is_entry_point'], 'name': 'idx_inv_is_entry_point'},
                ],
                'foreign_keys': []
            },
            
            'program_file_mapping': {
                'columns': [
                    {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'autoincrement': True},
                    {'name': 'file_id', 'type': 'INTEGER', 'nullable': False},           # Link to inventory(id)
                    {'name': 'program_name', 'type': 'VARCHAR(44)', 'nullable': False},
                    {'name': 'program_index', 'type': 'INTEGER', 'nullable': False},    # 0-based index within file (sequential)
                    {'name': 'program_type', 'type': 'VARCHAR(20)', 'nullable': False}, # MAIN, PROCEDURE, JCL, DATA
                    {'name': 'language', 'type': 'VARCHAR(20)', 'nullable': False},     # Specific language for this program
                    {'name': 'start_line', 'type': 'INTEGER', 'nullable': False},
                    {'name': 'end_line', 'type': 'INTEGER', 'nullable': False},
                    {'name': 'entry_points', 'type': 'TEXT'},                           # JSON array
                    {'name': 'lines_of_code', 'type': 'INTEGER'},                       # Calculated: end_line - start_line + 1
                    {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                ],
                'indexes': [
                    {'columns': ['file_id'], 'name': 'idx_pfm_file_id'},
                    {'columns': ['program_name'], 'name': 'idx_pfm_program_name'},
                    {'columns': ['program_type'], 'name': 'idx_pfm_program_type'},
                    {'columns': ['language'], 'name': 'idx_pfm_language'},
                    {'columns': ['file_id', 'program_index'], 'name': 'idx_pfm_file_program_index', 'unique': True},
                ],
                'foreign_keys': [
                    {'column': 'file_id', 'references': 'inventory(id)', 'name': 'fk_pfm_file_id'}
                ]
            },
        }
    
    def transform_record(self, json_record: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Transform inventory data into database-ready format.
        
        Note: This method is not used for inventory data as it's loaded from CSV files.
        Inventory data is loaded directly via the InventoryLoader component.
        
        Args:
            json_record: Not applicable for inventory schema
            
        Returns:
            Empty dict as this schema doesn't process JSON records
        """
        return {}
    
    def validate_record(self, json_record: Dict[str, Any]) -> bool:
        """
        Validate inventory record.
        
        Note: Inventory data validation is handled by the InventoryLoader component.
        
        Args:
            json_record: Not applicable for inventory schema
            
        Returns:
            False as this schema doesn't process JSON records
        """
        return False


__all__ = ['InventorySchema']