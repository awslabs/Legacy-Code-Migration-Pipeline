"""Dependency data loader implementation."""

import csv
import json
import os
from typing import Dict, Any, List
from collections import defaultdict


class DependencyLoader:
    """Loads artifact dependency data from CSV or JSON files into database."""
    
    def __init__(self, database: BaseDatabase):
        """
        Initialize dependency loader with database adapter.
        
        Args:
            database: Database adapter instance
        """
        self.database = database
        self.stats = defaultdict(int)
    
    def create_dependencies_schema(self) -> None:
        """Create database tables for dependency tracking.
        
        Creates the artifact_dependencies table with indexes. Handles existing
        tables gracefully by using CREATE TABLE IF NOT EXISTS.
        """
        from shared.database.schemas import DependenciesSchema
        
        # Get table definitions from schema
        schema = DependenciesSchema()
        table_defs = schema.get_table_definitions()
        
        print("\nCreating dependencies schema...")
        
        # Create each table
        for table_name, table_def in table_defs.items():
            if self.database.table_exists(table_name):
                print(f"  ✓ Table {table_name} already exists")
            else:
                self.database.create_table(table_name, table_def)
                print(f"  ✓ Created table {table_name}")
        
        self.database.commit()
        print("✓ Dependencies schema created successfully\n")
    
    def load_from_csv(self, csv_file: str, skip_duplicates: bool = True) -> Dict[str, int]:
        """
        Load dependency data from CSV file.
        
        Expected CSV columns:
        - source_name: Source artifact name (44 chars max)
        - source_type: Source artifact type (20 chars max)
        - target_name: Target artifact name (44 chars max)
        - target_type: Target artifact type (20 chars max)
        - dependency_type: Type of dependency (20 chars max)
        - file_path: Optional source file path (255 chars max)
        - line_number: Optional line number (integer)
        
        Note: Language information is retrieved via JOIN with the inventory table.
        The inventory table is the authoritative source for artifact language data.
        
        Args:
            csv_file: Path to CSV file containing dependency data
            skip_duplicates: If True, skip duplicate entries; if False, update them
            
        Returns:
            Dictionary with load statistics:
            {
                'processed': int,
                'inserted': int,
                'updated': int,
                'skipped': int,
                'errors': int
            }
        """
        # Validate file exists
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        # Validate CSV format
        errors = self._validate_csv_format(csv_file)
        if errors:
            raise ValueError(f"CSV validation failed:\n  " + "\n  ".join(errors))
        
        print(f"\nLoading dependencies from {csv_file}...")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        rows_skipped = 0
        rows_errors = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                rows_processed += 1
                
                try:
                    # Build row data
                    row_data = {
                        'source_artifact_name': row['source_name'].strip()[:44],
                        'source_artifact_type': row['source_type'].strip()[:20],
                        'target_artifact_name': row['target_name'].strip()[:44],
                        'target_artifact_type': row['target_type'].strip()[:20],
                        'dependency_type': row['dependency_type'].strip()[:20],
                        'source_file_path': row.get('file_path', '').strip()[:255] or None,
                        'line_number': int(row['line_number']) if row.get('line_number', '').strip() else None
                    }
                    
                    # Validate required fields are not empty
                    if not all([
                        row_data['source_artifact_name'],
                        row_data['source_artifact_type'],
                        row_data['target_artifact_name'],
                        row_data['target_artifact_type'],
                        row_data['dependency_type']
                    ]):
                        print(f"  ⚠ Warning: Row {row_num} has empty required fields, skipping")
                        rows_skipped += 1
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
                            rows_skipped += 1
                            continue
                        else:
                            # Update existing record
                            cursor.execute(
                                "DELETE FROM artifact_dependencies WHERE id = ?",
                                (existing[0],)
                            )
                            rows_updated += 1
                    
                    rows_to_insert.append(row_data)
                    rows_inserted += 1
                    
                    # Batch insert every 1000 rows
                    if len(rows_to_insert) >= 1000:
                        self.database.insert_rows('artifact_dependencies', rows_to_insert)
                        self.database.commit()
                        rows_to_insert = []
                
                except Exception as e:
                    print(f"  ⚠ Warning: Error processing row {row_num}: {str(e)}")
                    rows_errors += 1
                    continue
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('artifact_dependencies', rows_to_insert)
            self.database.commit()
        
        # Update stats
        self.stats['processed'] = rows_processed
        self.stats['inserted'] = rows_inserted
        self.stats['updated'] = rows_updated
        self.stats['skipped'] = rows_skipped
        self.stats['errors'] = rows_errors
        
        print(f"  ✓ Processed {rows_processed:,} rows")
        print(f"  ✓ Inserted {rows_inserted:,} dependencies")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing dependencies")
        if rows_skipped > 0:
            print(f"  ⚠ Skipped {rows_skipped:,} duplicate/invalid rows")
        if rows_errors > 0:
            print(f"  ✗ Errors: {rows_errors:,} rows")
        
        return dict(self.stats)
    
    def load_from_json(self, json_file: str, skip_duplicates: bool = True) -> Dict[str, int]:
        """
        Load dependency data from JSON file.
        
        Expected JSON format:
        [
            {
                "source_name": "PROGRAM1",
                "source_type": "PROGRAM",
                "target_name": "COPYBOOK1",
                "target_type": "COPYBOOK",
                "dependency_type": "COPY",
                "file_path": "PROD.SOURCE.COBOL(PROGRAM1)",
                "line_number": 45
            },
            ...
        ]
        
        Note: Language information is retrieved via JOIN with the inventory table.
        The inventory table is the authoritative source for artifact language data.
        
        Args:
            json_file: Path to JSON file containing dependency data
            skip_duplicates: If True, skip duplicate entries; if False, update them
            
        Returns:
            Dictionary with load statistics
        """
        # Validate file exists
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        
        print(f"\nLoading dependencies from {json_file}...")
        
        # Load JSON data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Validate data structure
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of dependency records")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        rows_skipped = 0
        rows_errors = 0
        
        for idx, record in enumerate(data):
            rows_processed += 1
            
            try:
                # Validate record structure
                if not isinstance(record, dict):
                    print(f"  ⚠ Warning: Record {idx} is not a dictionary, skipping")
                    rows_skipped += 1
                    continue
                
                # Build row data
                row_data = {
                    'source_artifact_name': str(record.get('source_name', '')).strip()[:44],
                    'source_artifact_type': str(record.get('source_type', '')).strip()[:20],
                    'target_artifact_name': str(record.get('target_name', '')).strip()[:44],
                    'target_artifact_type': str(record.get('target_type', '')).strip()[:20],
                    'dependency_type': str(record.get('dependency_type', '')).strip()[:20],
                    'source_file_path': str(record.get('file_path', '')).strip()[:255] or None,
                    'line_number': int(record['line_number']) if record.get('line_number') else None
                }
                
                # Validate required fields are not empty
                if not all([
                    row_data['source_artifact_name'],
                    row_data['source_artifact_type'],
                    row_data['target_artifact_name'],
                    row_data['target_artifact_type'],
                    row_data['dependency_type']
                ]):
                    print(f"  ⚠ Warning: Record {idx} has empty required fields, skipping")
                    rows_skipped += 1
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
                        rows_skipped += 1
                        continue
                    else:
                        # Update existing record
                        cursor.execute(
                            "DELETE FROM artifact_dependencies WHERE id = ?",
                            (existing[0],)
                        )
                        rows_updated += 1
                
                rows_to_insert.append(row_data)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('artifact_dependencies', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
            
            except Exception as e:
                print(f"  ⚠ Warning: Error processing record {idx}: {str(e)}")
                rows_errors += 1
                continue
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('artifact_dependencies', rows_to_insert)
            self.database.commit()
        
        # Update stats
        self.stats['processed'] = rows_processed
        self.stats['inserted'] = rows_inserted
        self.stats['updated'] = rows_updated
        self.stats['skipped'] = rows_skipped
        self.stats['errors'] = rows_errors
        
        print(f"  ✓ Processed {rows_processed:,} records")
        print(f"  ✓ Inserted {rows_inserted:,} dependencies")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing dependencies")
        if rows_skipped > 0:
            print(f"  ⚠ Skipped {rows_skipped:,} duplicate/invalid records")
        if rows_errors > 0:
            print(f"  ✗ Errors: {rows_errors:,} records")
        
        return dict(self.stats)
    
    def bulk_insert(self, dependencies: List[Dict[str, Any]], 
                   skip_duplicates: bool = True) -> Dict[str, int]:
        """
        Bulk insert dependency records for performance.
        
        This method is optimized for inserting large numbers of dependencies
        from static code analysis or other programmatic sources.
        
        Note: Language information is retrieved via JOIN with the inventory table.
        The inventory table is the authoritative source for artifact language data.
        
        Args:
            dependencies: List of dependency dictionaries with keys:
                - source_artifact_name (required)
                - source_artifact_type (required)
                - target_artifact_name (required)
                - target_artifact_type (required)
                - dependency_type (required)
                - source_file_path (optional)
                - line_number (optional)
            skip_duplicates: If True, skip duplicate entries; if False, update them
            
        Returns:
            Dictionary with load statistics
        """
        # Bulk insert dependencies (silent mode for performance)
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        rows_skipped = 0
        rows_errors = 0
        
        # Track keys within the current batch to detect intra-batch duplicates
        batch_keys = set()
        
        for idx, dep in enumerate(dependencies):
            rows_processed += 1
            
            try:
                # Validate record structure
                if not isinstance(dep, dict):
                    rows_skipped += 1
                    continue
                
                # Build row data
                row_data = {
                    'source_artifact_name': str(dep.get('source_artifact_name', '')).strip()[:44],
                    'source_artifact_type': str(dep.get('source_artifact_type', '')).strip()[:20],
                    'target_artifact_name': str(dep.get('target_artifact_name', '')).strip()[:44],
                    'target_artifact_type': str(dep.get('target_artifact_type', '')).strip()[:20],
                    'dependency_type': str(dep.get('dependency_type', '')).strip()[:20],
                    'source_file_path': str(dep.get('source_file_path', '')).strip()[:255] or None,
                    'line_number': int(dep['line_number']) if dep.get('line_number') else None
                }
                
                # Validate required fields are not empty
                if not all([
                    row_data['source_artifact_name'],
                    row_data['source_artifact_type'],
                    row_data['target_artifact_name'],
                    row_data['target_artifact_type'],
                    row_data['dependency_type']
                ]):
                    rows_skipped += 1
                    continue
                
                # Build unique key for duplicate detection
                unique_key = (
                    row_data['source_artifact_name'],
                    row_data['target_artifact_name'],
                    row_data['dependency_type']
                )
                
                # Check for intra-batch duplicates
                if unique_key in batch_keys:
                    if skip_duplicates:
                        rows_skipped += 1
                        continue
                
                # Check for duplicates in database
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
                        rows_skipped += 1
                        continue
                    else:
                        # Update existing record
                        cursor.execute(
                            "DELETE FROM artifact_dependencies WHERE id = ?",
                            (existing[0],)
                        )
                        rows_updated += 1
                
                rows_to_insert.append(row_data)
                batch_keys.add(unique_key)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('artifact_dependencies', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
            
            except Exception as e:
                rows_errors += 1
                continue
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('artifact_dependencies', rows_to_insert)
            self.database.commit()
        
        # Update stats
        self.stats['processed'] = rows_processed
        self.stats['inserted'] = rows_inserted
        self.stats['updated'] = rows_updated
        self.stats['skipped'] = rows_skipped
        self.stats['errors'] = rows_errors
        
        print(f"  ✓ Processed {rows_processed:,} records")
        print(f"  ✓ Inserted {rows_inserted:,} dependencies")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing dependencies")
        if rows_skipped > 0:
            print(f"  ⚠ Skipped {rows_skipped:,} duplicate/invalid records")
        if rows_errors > 0:
            print(f"  ✗ Errors: {rows_errors:,} records")
        
        return dict(self.stats)
    
    def _validate_csv_format(self, csv_file: str) -> List[str]:
        """
        Validate CSV file format.
        
        Checks that required columns are present.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of validation error messages (empty list if valid)
        """
        errors = []
        
        required_columns = {
            'source_name', 'source_type', 'target_name', 
            'target_type', 'dependency_type'
        }
        
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
                missing = required_columns - actual_columns
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
