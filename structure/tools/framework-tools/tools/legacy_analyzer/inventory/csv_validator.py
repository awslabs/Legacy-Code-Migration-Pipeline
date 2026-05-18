"""CSV validation utilities for inventory data."""

import csv
import os
from typing import List, Dict, Set


class CSVValidator:
    """Validates CSV files for inventory loading."""
    
    # Define required columns for each inventory type
    REQUIRED_COLUMNS = {
        'jcl': {'member_name', 'library_name'},
        'programs': {'program_name', 'library_name'},
        'copybooks': {'copybook_name', 'library_name'},
        'datasets': {'dataset_name'},
        'cics': {'resource_name', 'resource_type'}
    }
    
    # Define optional columns for each inventory type
    OPTIONAL_COLUMNS = {
        'jcl': {'last_modified', 'size_lines'},
        'programs': {'link_date', 'size_bytes', 'entry_point'},
        'copybooks': {'last_modified'},
        'datasets': {'creation_date', 'last_referenced', 'size_mb', 'volume', 'dataset_type'},
        'cics': {'group_name', 'status', 'program_name'}
    }
    
    @classmethod
    def validate(cls, csv_file: str, inventory_type: str) -> List[str]:
        """
        Validate CSV file format.
        
        Checks that required columns are present and validates basic data types.
        
        Args:
            csv_file: Path to CSV file
            inventory_type: Type of inventory (jcl, programs, copybooks, datasets, cics)
            
        Returns:
            List of validation error messages (empty list if valid)
        """
        errors = []
        
        # Check file exists
        if not os.path.exists(csv_file):
            errors.append(f"File not found: {csv_file}")
            return errors
        
        # Check inventory type is valid
        if inventory_type not in cls.REQUIRED_COLUMNS:
            errors.append(f"Unknown inventory type: {inventory_type}")
            return errors
        
        required = cls.REQUIRED_COLUMNS[inventory_type]
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Check if file is empty
                if reader.fieldnames is None:
                    errors.append("CSV file is empty or has no header row")
                    return errors
                
                # Convert fieldnames to set for comparison (strip whitespace)
                actual_columns = {col.strip() for col in reader.fieldnames}
                
                # Check required columns
                missing = required - actual_columns
                if missing:
                    errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
                
                # Validate at least one data row exists
                row_count = 0
                for row in reader:
                    row_count += 1
                    if row_count >= 1:
                        break
                
                if row_count == 0:
                    errors.append("CSV file has no data rows")
        
        except Exception as e:
            errors.append(f"Error reading CSV file: {str(e)}")
        
        return errors
    
    @classmethod
    def get_column_info(cls, inventory_type: str) -> Dict[str, Set[str]]:
        """
        Get column information for an inventory type.
        
        Args:
            inventory_type: Type of inventory
            
        Returns:
            Dictionary with 'required' and 'optional' column sets
        """
        if inventory_type not in cls.REQUIRED_COLUMNS:
            raise ValueError(f"Unknown inventory type: {inventory_type}")
        
        return {
            'required': cls.REQUIRED_COLUMNS[inventory_type],
            'optional': cls.OPTIONAL_COLUMNS.get(inventory_type, set())
        }
