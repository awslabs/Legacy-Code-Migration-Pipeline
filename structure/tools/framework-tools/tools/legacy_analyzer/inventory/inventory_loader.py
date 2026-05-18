"""Inventory loader implementation."""

import csv
import os
from typing import Dict, Any, List, Set
from collections import defaultdict
from .base_loader import BaseInventoryLoader


class InventoryLoader(BaseInventoryLoader):
    """Loads mainframe inventory data from CSV files into database."""
    
    def __init__(self, database: BaseDatabase):
        """
        Initialize inventory loader with database adapter.
        
        Args:
            database: Database adapter instance
        """
        super().__init__(database)
        self.stats = defaultdict(int)
    
    def create_inventory_schema(self) -> None:
        """Create database tables for inventory data.
        
        Creates all inventory tables with indexes. Handles existing tables gracefully
        by using CREATE TABLE IF NOT EXISTS.
        """
        from shared.database.schemas import InventorySchema
        
        # Get table definitions from schema
        schema = InventorySchema()
        table_defs = schema.get_table_definitions()
        
        print("\nCreating inventory schema...")
        
        # Create each table
        for table_name, table_def in table_defs.items():
            if self.database.table_exists(table_name):
                print(f"  ✓ Table {table_name} already exists")
            else:
                self.database.create_table(table_name, table_def)
                print(f"  ✓ Created table {table_name}")
        
        self.database.commit()
        print("✓ Inventory schema created successfully\n")
    
    def load_inventory(self, csv_file: str, inventory_type: str) -> None:
        """
        Load inventory data from CSV file.
        
        Routes to the appropriate type-specific loader method.
        
        Args:
            csv_file: Path to CSV file containing inventory data
            inventory_type: Type of inventory (jcl, programs, copybooks, datasets, cics)
        """
        loaders = {
            'jcl': self.load_jcl_inventory,
            'programs': self.load_program_inventory,
            'copybooks': self.load_copybook_inventory,
            'datasets': self.load_dataset_inventory,
            'cics': self.load_cics_inventory
        }
        
        if inventory_type not in loaders:
            raise ValueError(f"Unknown inventory type: {inventory_type}. "
                           f"Valid types: {', '.join(loaders.keys())}")
        
        loaders[inventory_type](csv_file)
    
    def validate_csv_format(self, csv_file: str, inventory_type: str) -> List[str]:
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
        
        # Define required columns for each inventory type
        required_columns = {
            'jcl': {'member_name', 'library_name'},
            'programs': {'program_name', 'library_name'},
            'copybooks': {'copybook_name', 'library_name'},
            'datasets': {'dataset_name'},
            'cics': {'resource_name', 'resource_type'}
        }
        
        if inventory_type not in required_columns:
            errors.append(f"Unknown inventory type: {inventory_type}")
            return errors
        
        required = required_columns[inventory_type]
        
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
    
    def load_jcl_inventory(self, csv_file: str) -> None:
        """
        Load JCL member inventory.
        
        Expected CSV columns:
        - member_name: JCL member name (8 chars)
        - library_name: PDS name (44 chars)
        - last_modified: Date last modified (optional)
        - size_lines: Number of lines (optional)
        
        Args:
            csv_file: Path to CSV file
        """
        # Validate CSV format
        errors = self.validate_csv_format(csv_file, 'jcl')
        if errors:
            raise ValueError(f"CSV validation failed:\n  " + "\n  ".join(errors))
        
        print(f"\nLoading JCL inventory from {csv_file}...")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                # Build row data
                row_data = {
                    'member_name': row['member_name'].strip()[:8],
                    'library_name': row['library_name'].strip()[:44],
                    'last_modified': row.get('last_modified', '').strip() or None,
                    'size_lines': int(row['size_lines']) if row.get('size_lines', '').strip() else None
                }
                
                # Check for duplicates - delete existing and insert new (update with most recent)
                cursor = self.database.cursor()
                cursor.execute(
                    "SELECT id FROM inventory_jcl WHERE member_name = ? AND library_name = ?",
                    (row_data['member_name'], row_data['library_name'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute(
                        "DELETE FROM inventory_jcl WHERE id = ?",
                        (existing[0],)
                    )
                    rows_updated += 1
                
                rows_to_insert.append(row_data)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('inventory_jcl', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('inventory_jcl', rows_to_insert)
            self.database.commit()
        
        self.stats['jcl_processed'] = rows_processed
        self.stats['jcl_inserted'] = rows_inserted
        self.stats['jcl_updated'] = rows_updated
        
        print(f"  ✓ Processed {rows_processed:,} rows")
        print(f"  ✓ Inserted {rows_inserted:,} JCL members")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing members")
    
    def load_program_inventory(self, csv_file: str) -> None:
        """
        Load program/load module inventory.
        
        Expected CSV columns:
        - program_name: Load module name (8 chars)
        - library_name: LOADLIB name (44 chars)
        - link_date: Date linked (optional)
        - size_bytes: Size in bytes (optional)
        - entry_point: Entry point address (optional)
        
        Args:
            csv_file: Path to CSV file
        """
        # Validate CSV format
        errors = self.validate_csv_format(csv_file, 'programs')
        if errors:
            raise ValueError(f"CSV validation failed:\n  " + "\n  ".join(errors))
        
        print(f"\nLoading program inventory from {csv_file}...")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                # Build row data
                row_data = {
                    'program_name': row['program_name'].strip()[:8],
                    'library_name': row['library_name'].strip()[:44],
                    'link_date': row.get('link_date', '').strip() or None,
                    'size_bytes': int(row['size_bytes']) if row.get('size_bytes', '').strip() else None,
                    'entry_point': row.get('entry_point', '').strip()[:16] or None
                }
                
                # Check for duplicates - delete existing and insert new
                cursor = self.database.cursor()
                cursor.execute(
                    "SELECT id FROM inventory_programs WHERE program_name = ? AND library_name = ?",
                    (row_data['program_name'], row_data['library_name'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute(
                        "DELETE FROM inventory_programs WHERE id = ?",
                        (existing[0],)
                    )
                    rows_updated += 1
                
                rows_to_insert.append(row_data)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('inventory_programs', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('inventory_programs', rows_to_insert)
            self.database.commit()
        
        self.stats['programs_processed'] = rows_processed
        self.stats['programs_inserted'] = rows_inserted
        self.stats['programs_updated'] = rows_updated
        
        print(f"  ✓ Processed {rows_processed:,} rows")
        print(f"  ✓ Inserted {rows_inserted:,} programs")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing programs")
    
    def load_copybook_inventory(self, csv_file: str) -> None:
        """
        Load copybook inventory.
        
        Expected CSV columns:
        - copybook_name: Copybook name (8 chars)
        - library_name: Source library name (44 chars)
        - last_modified: Date last modified (optional)
        
        Args:
            csv_file: Path to CSV file
        """
        # Validate CSV format
        errors = self.validate_csv_format(csv_file, 'copybooks')
        if errors:
            raise ValueError(f"CSV validation failed:\n  " + "\n  ".join(errors))
        
        print(f"\nLoading copybook inventory from {csv_file}...")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                # Build row data
                row_data = {
                    'copybook_name': row['copybook_name'].strip()[:8],
                    'library_name': row['library_name'].strip()[:44],
                    'last_modified': row.get('last_modified', '').strip() or None
                }
                
                # Check for duplicates - delete existing and insert new
                cursor = self.database.cursor()
                cursor.execute(
                    "SELECT id FROM inventory_copybooks WHERE copybook_name = ? AND library_name = ?",
                    (row_data['copybook_name'], row_data['library_name'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute(
                        "DELETE FROM inventory_copybooks WHERE id = ?",
                        (existing[0],)
                    )
                    rows_updated += 1
                
                rows_to_insert.append(row_data)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('inventory_copybooks', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('inventory_copybooks', rows_to_insert)
            self.database.commit()
        
        self.stats['copybooks_processed'] = rows_processed
        self.stats['copybooks_inserted'] = rows_inserted
        self.stats['copybooks_updated'] = rows_updated
        
        print(f"  ✓ Processed {rows_processed:,} rows")
        print(f"  ✓ Inserted {rows_inserted:,} copybooks")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing copybooks")
    
    def load_dataset_inventory(self, csv_file: str) -> None:
        """
        Load dataset catalog.
        
        Expected CSV columns:
        - dataset_name: Dataset name (44 chars)
        - creation_date: Date created (optional)
        - last_referenced: Date last referenced by catalog (optional)
        - size_mb: Size in megabytes (optional)
        - volume: Volume serial (optional)
        - dataset_type: Type (PS, PO, VS, etc.) (optional)
        
        Args:
            csv_file: Path to CSV file
        """
        # Validate CSV format
        errors = self.validate_csv_format(csv_file, 'datasets')
        if errors:
            raise ValueError(f"CSV validation failed:\n  " + "\n  ".join(errors))
        
        print(f"\nLoading dataset inventory from {csv_file}...")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                # Build row data
                row_data = {
                    'dataset_name': row['dataset_name'].strip()[:44],
                    'creation_date': row.get('creation_date', '').strip() or None,
                    'last_referenced': row.get('last_referenced', '').strip() or None,
                    'size_mb': float(row['size_mb']) if row.get('size_mb', '').strip() else None,
                    'volume': row.get('volume', '').strip()[:6] or None,
                    'dataset_type': row.get('dataset_type', '').strip()[:10] or None
                }
                
                # Check for duplicates - delete existing and insert new
                cursor = self.database.cursor()
                cursor.execute(
                    "SELECT id FROM inventory_datasets WHERE dataset_name = ?",
                    (row_data['dataset_name'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute(
                        "DELETE FROM inventory_datasets WHERE id = ?",
                        (existing[0],)
                    )
                    rows_updated += 1
                
                rows_to_insert.append(row_data)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('inventory_datasets', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('inventory_datasets', rows_to_insert)
            self.database.commit()
        
        self.stats['datasets_processed'] = rows_processed
        self.stats['datasets_inserted'] = rows_inserted
        self.stats['datasets_updated'] = rows_updated
        
        print(f"  ✓ Processed {rows_processed:,} rows")
        print(f"  ✓ Inserted {rows_inserted:,} datasets")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing datasets")
    
    def load_cics_inventory(self, csv_file: str) -> None:
        """
        Load CICS resource definitions.
        
        Expected CSV columns (required):
        - resource_name: Transaction ID or program name (8 chars)
        - resource_type: TRANSACTION, PROGRAM, FILE, etc. (20 chars)
        
        Optional CSV columns (backward compatible):
        - group_name: CSD group (8 chars)
        - status: ENABLED, DISABLED (20 chars)
        - program_name: For TRANSACTION type, the associated program (8 chars)
        - dataset_name: For FILE type, the MVS dataset name (44 chars) [NEW]
        - description: Description for all resource types (TEXT) [NEW]
        - language: For PROGRAM type, the programming language (20 chars) [NEW]
        
        Args:
            csv_file: Path to CSV file
        """
        # Validate CSV format
        errors = self.validate_csv_format(csv_file, 'cics')
        if errors:
            raise ValueError(f"CSV validation failed:\n  " + "\n  ".join(errors))
        
        print(f"\nLoading CICS inventory from {csv_file}...")
        
        rows_to_insert = []
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0
        
        # Track which enhanced columns are present
        enhanced_columns_found = {
            'dataset_name': False,
            'description': False,
            'language': False
        }
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check which enhanced columns are present in the CSV
            if reader.fieldnames:
                for col in enhanced_columns_found.keys():
                    if col in reader.fieldnames:
                        enhanced_columns_found[col] = True
            
            # Log enhanced columns if found
            enhanced_cols_present = [col for col, present in enhanced_columns_found.items() if present]
            if enhanced_cols_present:
                print(f"  ℹ Enhanced columns detected: {', '.join(enhanced_cols_present)}")
            
            for row in reader:
                rows_processed += 1
                
                # Build row data with required columns
                row_data = {
                    'resource_name': row['resource_name'].strip()[:8],
                    'resource_type': row['resource_type'].strip()[:20],
                    'group_name': row.get('group_name', '').strip()[:8] or None,
                    'status': row.get('status', '').strip()[:20] or None,
                    'program_name': row.get('program_name', '').strip()[:8] or None
                }
                
                # Add enhanced columns if present (backward compatible)
                if enhanced_columns_found['dataset_name']:
                    dataset_name = row.get('dataset_name', '').strip()[:44] or None
                    row_data['dataset_name'] = dataset_name
                    if dataset_name and row_data['resource_type'] == 'FILE':
                        # Log dataset mapping for FILE resources
                        pass  # Logging happens in batch summary
                
                if enhanced_columns_found['description']:
                    description = row.get('description', '').strip() or None
                    row_data['description'] = description
                
                if enhanced_columns_found['language']:
                    language = row.get('language', '').strip()[:20] or None
                    row_data['language'] = language
                    if language and row_data['resource_type'] == 'PROGRAM':
                        # Log language for PROGRAM resources
                        pass  # Logging happens in batch summary
                
                # Check for duplicates - delete existing and insert new
                cursor = self.database.cursor()
                cursor.execute(
                    "SELECT id FROM inventory_cics WHERE resource_name = ? AND resource_type = ?",
                    (row_data['resource_name'], row_data['resource_type'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute(
                        "DELETE FROM inventory_cics WHERE id = ?",
                        (existing[0],)
                    )
                    rows_updated += 1
                
                rows_to_insert.append(row_data)
                rows_inserted += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('inventory_cics', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('inventory_cics', rows_to_insert)
            self.database.commit()
        
        self.stats['cics_processed'] = rows_processed
        self.stats['cics_inserted'] = rows_inserted
        self.stats['cics_updated'] = rows_updated
        
        print(f"  ✓ Processed {rows_processed:,} rows")
        print(f"  ✓ Inserted {rows_inserted:,} CICS resources")
        if rows_updated > 0:
            print(f"  ✓ Updated {rows_updated:,} existing resources")
        
        # Log summary of enhanced data if present
        if enhanced_cols_present:
            cursor = self.database.cursor()
            
            if enhanced_columns_found['dataset_name']:
                cursor.execute(
                    "SELECT COUNT(*) FROM inventory_cics WHERE dataset_name IS NOT NULL"
                )
                dataset_count = cursor.fetchone()[0]
                if dataset_count > 0:
                    print(f"  ℹ Loaded {dataset_count:,} resources with dataset mappings")
            
            if enhanced_columns_found['description']:
                cursor.execute(
                    "SELECT COUNT(*) FROM inventory_cics WHERE description IS NOT NULL"
                )
                desc_count = cursor.fetchone()[0]
                if desc_count > 0:
                    print(f"  ℹ Loaded {desc_count:,} resources with descriptions")
            
            if enhanced_columns_found['language']:
                cursor.execute(
                    "SELECT COUNT(*) FROM inventory_cics WHERE language IS NOT NULL"
                )
                lang_count = cursor.fetchone()[0]
                if lang_count > 0:
                    print(f"  ℹ Loaded {lang_count:,} programs with language information")
        
        # Create CICS_TRANSACTION dependencies for migration flow builder
        self._create_cics_transaction_dependencies()

    def _create_cics_transaction_dependencies(self) -> None:
        """
        Create CICS_TRANSACTION dependencies from inventory_cics table.
        
        The migration flow builder expects entry points to be stored as dependencies
        in the artifact_dependencies table. This method creates dependencies linking
        CICS transactions to their associated programs.
        """
        cursor = self.database.cursor()
        
        # Ensure artifact_dependencies table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifact_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_artifact_name VARCHAR(44) NOT NULL,
                source_artifact_type VARCHAR(20),
                target_artifact_name VARCHAR(44) NOT NULL,
                target_artifact_type VARCHAR(20),
                dependency_type VARCHAR(30),
                line_number INTEGER
            )
        """)
        
        # Get CICS transactions with programs
        cursor.execute("""
            SELECT resource_name, program_name
            FROM inventory_cics
            WHERE resource_type = 'TRANSACTION' AND program_name IS NOT NULL
        """)
        
        transactions = cursor.fetchall()
        if not transactions:
            return
        
        created = 0
        for trans_id, program_name in transactions:
            # Check if dependency already exists
            cursor.execute("""
                SELECT COUNT(*) FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND target_artifact_name = ?
                  AND dependency_type = 'CICS_TRANSACTION'
            """, (trans_id, program_name))
            
            if cursor.fetchone()[0] > 0:
                continue
            
            # Create dependency
            cursor.execute("""
                INSERT INTO artifact_dependencies (
                    source_artifact_name,
                    source_artifact_type,
                    target_artifact_name,
                    target_artifact_type,
                    dependency_type,
                    line_number
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trans_id,
                'TRANSACTION',
                program_name,
                'PROGRAM',
                'CICS_TRANSACTION',
                None
            ))
            
            created += 1
        
        if created > 0:
            self.database.commit()
            print(f"  ℹ Created {created:,} CICS transaction dependencies")
