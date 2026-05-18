# Inventory Management

## Overview


### **Dual-Source Architecture**

This module works with two complementary data sources:

1. **CSV Inventory Tables** (this module): Mainframe catalog metadata loaded from CSV exports
   - `inventory_cics` - CICS resource definitions
   - `inventory_programs` - Load module catalog
   - `inventory_jcl` - JCL member listings
   - `inventory_datasets` - Dataset catalog information

2. **Unified Inventory Table** (code analysis): Artifacts discovered from source code parsing
   - `inventory` - All artifacts found in source code with metadata

### **Enhanced Analysis Capabilities**

The combination of both data sources enables:
- **Dependency-aware reconciliation** - Smart classification based on call relationships
- **Entry point detection** - ONLINE (CICS) + BATCH (JCL) + INFERRED (code analysis)
- **Data quality assessment** - Cross-validation between catalog and source code
- **Migration planning** - Complete visibility into artifact lifecycle

**📋 For complete CSV generation process**: See the **[CSV Export Process Guide](../docs/CSV_EXPORT_PROCESS.md)** for detailed instructions on extracting inventory data from mainframe systems and generating the CSV files that this module loads.

## Table of Contents

1. [Supported Inventory Types](#supported-inventory-types)
2. [CSV Format Specifications](#csv-format-specifications)
3. [Loading Inventory Data](#loading-inventory-data)
4. [Enhanced CICS CSV Format](#enhanced-cics-csv-format)
5. [Examples](#examples)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

## Supported Inventory Types

The inventory loader supports the following mainframe artifact types:

- **JCL**: JCL members and job definitions
- **Programs**: Compiled programs and load modules
- **Copybooks**: COBOL copybooks and include files
- **Datasets**: MVS datasets and files
- **CICS**: CICS resource definitions (transactions, programs, files, mapsets)

## CSV Format Specifications

### JCL Inventory

**Required Columns:**
- `member_name` (VARCHAR(8)) - JCL member name
- `library_name` (VARCHAR(44)) - Library/PDS name

**Optional Columns:**
- `last_modified` (DATE) - Last modification date
- `size_lines` (INTEGER) - Number of lines in member

**Example:**
```csv
member_name,library_name,last_modified,size_lines
DALYREJS,SYS1.PROCLIB,2024-01-15,250
MONTHRPT,USER.JCL,2024-02-20,180
```

### Program Inventory

**Required Columns:**
- `program_name` (VARCHAR(8)) - Program name
- `library_name` (VARCHAR(44)) - Load library name

**Optional Columns:**
- `link_date` (DATE) - Link-edit date
- `size_bytes` (INTEGER) - Program size in bytes
- `entry_point` (VARCHAR(16)) - Entry point name

**Example:**
```csv
program_name,library_name,link_date,size_bytes,entry_point
COACTUPC,PROD.LOADLIB,2024-01-10,45678,COACTUPC
CBACT01C,PROD.LOADLIB,2024-01-10,32456,CBACT01C
```

### Copybook Inventory

**Required Columns:**
- `copybook_name` (VARCHAR(8)) - Copybook name
- `library_name` (VARCHAR(44)) - Copybook library name

**Optional Columns:**
- `last_modified` (DATE) - Last modification date

**Example:**
```csv
copybook_name,library_name,last_modified
CUSTCOPY,SYS1.COPYLIB,2024-01-05
ACCTCOPY,SYS1.COPYLIB,2024-01-08
```

### Dataset Inventory

**Required Columns:**
- `dataset_name` (VARCHAR(44)) - MVS dataset name

**Optional Columns:**
- `creation_date` (DATE) - Dataset creation date
- `last_referenced` (DATE) - Last reference date
- `size_mb` (DECIMAL(12,2)) - Size in megabytes
- `volume` (VARCHAR(6)) - Volume serial
- `dataset_type` (VARCHAR(10)) - Dataset type (VSAM, PS, PO, etc.)

**Example:**
```csv
dataset_name,creation_date,last_referenced,size_mb,volume,dataset_type
AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS,2023-12-01,2024-03-15,125.50,VOL001,VSAM
PROD.PAYROLL.MASTER,2023-11-15,2024-03-14,89.25,VOL002,PS
```

### CICS Inventory (Standard Format)

**Required Columns:**
- `resource_name` (VARCHAR(8)) - CICS resource name
- `resource_type` (VARCHAR(20)) - Resource type (TRANSACTION, PROGRAM, FILE, MAPSET)

**Optional Columns:**
- `group_name` (VARCHAR(8)) - CICS group name
- `status` (VARCHAR(20)) - Resource status (ENABLED, DISABLED)
- `program_name` (VARCHAR(8)) - Associated program (for TRANSACTION resources)

**Example:**
```csv
resource_name,resource_type,group_name,status,program_name
CAUP,TRANSACTION,CARDDEMO,ENABLED,COACTUPC
COACTUPC,PROGRAM,CARDDEMO,ENABLED,
ACCTDAT,FILE,CARDDEMO,ENABLED,
COACTUP,MAPSET,CARDDEMO,ENABLED,
```

## Loading Inventory Data

### Command Line Interface

```bash
# Load JCL inventory
legacy-analyzer inventory load \
  --type jcl \
  --file exports/jcl_inventory.csv \
  --db results/analysis/analysis.db

# Load program inventory
legacy-analyzer inventory load \
  --type programs \
  --file exports/program_inventory.csv \
  --db results/analysis/analysis.db

# Load CICS inventory
legacy-analyzer inventory load \
  --type cics \
  --file exports/cics_inventory.csv \
  --db results/analysis/analysis.db
```

### Python API

```python
from legacy_analyzer.inventory.inventory_loader import InventoryLoader

# Initialize database and loader
db = SQLiteDatabase('results/analysis/analysis.db')
loader = InventoryLoader(db)

# Create inventory schema (if not exists)
loader.create_inventory_schema()

# Load JCL inventory
loader.load_jcl_inventory('exports/jcl_inventory.csv')

# Load program inventory
loader.load_program_inventory('exports/program_inventory.csv')

# Load CICS inventory
loader.load_cics_inventory('exports/cics_inventory.csv')

# Commit changes
db.commit()
db.close()
```

## Enhanced CICS CSV Format

### Overview

The enhanced CICS CSV format extends the standard format with additional columns for improved analysis and entry point detection. This format is **backward compatible** with the standard format.

### Enhanced Format Specification

**Required Columns:**
- `resource_name` (VARCHAR(8)) - CICS resource name
- `resource_type` (VARCHAR(20)) - Resource type (TRANSACTION, PROGRAM, FILE, MAPSET)
- `group_name` (VARCHAR(8)) - CICS group name
- `status` (VARCHAR(20)) - Resource status (ENABLED, DISABLED)

**Enhanced Columns:**
- `program_name` (VARCHAR(8)) - Associated program (for TRANSACTION resources)
- `dataset_name` (VARCHAR(44)) - MVS dataset name (for FILE resources)
- `description` (TEXT) - Human-readable description (all resource types)
- `language` (VARCHAR(20)) - Programming language (for PROGRAM resources: COBOL, PLI, ASM, C, etc.)

### Column Usage by Resource Type

| Column | TRANSACTION | PROGRAM | FILE | MAPSET |
|--------|-------------|---------|------|--------|
| `resource_name` | ✓ (4 chars) | ✓ (8 chars) | ✓ (8 chars) | ✓ (8 chars) |
| `resource_type` | ✓ | ✓ | ✓ | ✓ |
| `group_name` | ✓ | ✓ | ✓ | ✓ |
| `status` | ✓ | ✓ | ✓ | ✓ |
| `program_name` | ✓ (required) | - | - | - |
| `dataset_name` | - | - | ✓ (required) | - |
| `description` | ✓ (optional) | ✓ (optional) | ✓ (optional) | ✓ (optional) |
| `language` | - | ✓ (optional) | - | - |

### Enhanced CSV Example

```csv
resource_name,resource_type,group_name,status,program_name,dataset_name,description,language
CAUP,TRANSACTION,CARDDEMO,ENABLED,COACTUPC,,Credit Card Account Update,
CACT,TRANSACTION,CARDDEMO,ENABLED,COACTUP,,Credit Card Account List,
CCRD,TRANSACTION,CARDDEMO,ENABLED,COCRDLIC,,Credit Card List,
CMEN,TRANSACTION,CARDDEMO,ENABLED,COMENUC,,Main Menu,
COACTUPC,PROGRAM,CARDDEMO,ENABLED,,,Account Update Program,COBOL
COACTUP,PROGRAM,CARDDEMO,ENABLED,,,Account List Program,COBOL
COCRDLIC,PROGRAM,CARDDEMO,ENABLED,,,Credit Card List Program,COBOL
COMENUC,PROGRAM,CARDDEMO,ENABLED,,,Main Menu Program,COBOL
ACCTDAT,FILE,CARDDEMO,ENABLED,,AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS,Account Data File,
CUSTDAT,FILE,CARDDEMO,ENABLED,,AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS,Customer Data File,
CARDDAT,FILE,CARDDEMO,ENABLED,,AWS.M2.CARDDEMO.CARDDATA.VSAM.KSDS,Card Data File,
COACTUP,MAPSET,CARDDEMO,ENABLED,,,Account Update Map,
COCRDLI,MAPSET,CARDDEMO,ENABLED,,,Credit Card List Map,
COMENU,MAPSET,CARDDEMO,ENABLED,,,Main Menu Map,
```

### Benefits of Enhanced Format

1. **Entry Point Detection**: Transaction-to-program mapping enables explicit entry point identification
2. **Data Lineage**: File-to-dataset mapping supports data flow analysis
3. **Documentation**: Descriptions improve human readability and understanding
4. **Language Detection**: Language information aids in modernization planning
5. **Modernization**: Transaction IDs map to future API endpoints
6. **Service Grouping**: Group names suggest service boundaries

### Backward Compatibility

The enhanced CSV format is fully backward compatible:

- **Old loaders**: Can read enhanced CSV by ignoring extra columns
- **New loaders**: Can read standard CSV by treating extra columns as empty
- **Migration**: No data conversion required
- **Validation**: Both formats pass validation

**Standard Format (Still Supported):**
```csv
resource_name,resource_type,group_name,status
CAUP,TRANSACTION,CARDDEMO,ENABLED
COACTUPC,PROGRAM,CARDDEMO,ENABLED
```

**Enhanced Format (Recommended):**
```csv
resource_name,resource_type,group_name,status,program_name,dataset_name,description,language
CAUP,TRANSACTION,CARDDEMO,ENABLED,COACTUPC,,Account Update,
COACTUPC,PROGRAM,CARDDEMO,ENABLED,,,Account Update Program,COBOL
```

## Examples

### Example 1: Loading Standard CICS Inventory

```python
from legacy_analyzer.inventory.inventory_loader import InventoryLoader

# Initialize
db = SQLiteDatabase('analysis.db')
loader = InventoryLoader(db)

# Create schema
loader.create_inventory_schema()

# Load standard format CSV
loader.load_cics_inventory('cics_inventory_standard.csv')

# Query loaded data
cursor = db.execute("""
    SELECT resource_name, resource_type, group_name, status
    FROM inventory_cics
    WHERE status = 'ENABLED'
    ORDER BY resource_type, resource_name
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} in {row[2]} ({row[3]})")

db.close()
```

### Example 2: Loading Enhanced CICS Inventory

```python
from legacy_analyzer.inventory.inventory_loader import InventoryLoader

# Initialize
db = SQLiteDatabase('analysis.db')
loader = InventoryLoader(db)

# Create schema
loader.create_inventory_schema()

# Load enhanced format CSV
loader.load_cics_inventory('cics_inventory_enhanced.csv')

# Query transactions with program mappings
cursor = db.execute("""
    SELECT resource_name, program_name, description
    FROM inventory_cics
    WHERE resource_type = 'TRANSACTION'
      AND status = 'ENABLED'
    ORDER BY resource_name
""")

print("CICS Transactions:")
for row in cursor.fetchall():
    trans_id, program, desc = row
    print(f"  {trans_id} -> {program}: {desc or 'No description'}")

# Query files with dataset mappings
cursor = db.execute("""
    SELECT resource_name, dataset_name, description
    FROM inventory_cics
    WHERE resource_type = 'FILE'
      AND status = 'ENABLED'
    ORDER BY resource_name
""")

print("\nCICS Files:")
for row in cursor.fetchall():
    file_name, dataset, desc = row
    print(f"  {file_name} -> {dataset}: {desc or 'No description'}")

# Query programs with language information
cursor = db.execute("""
    SELECT resource_name, language, description
    FROM inventory_cics
    WHERE resource_type = 'PROGRAM'
      AND status = 'ENABLED'
    ORDER BY resource_name
""")

print("\nCICS Programs:")
for row in cursor.fetchall():
    prog_name, lang, desc = row
    print(f"  {prog_name} ({lang or 'Unknown'}): {desc or 'No description'}")

db.close()
```

### Example 3: Loading Multiple Inventory Types

```python
from legacy_analyzer.inventory.inventory_loader import InventoryLoader

# Initialize
db = SQLiteDatabase('analysis.db')
loader = InventoryLoader(db)

# Create schema
loader.create_inventory_schema()

# Load all inventory types
inventory_files = {
    'jcl': 'exports/jcl_inventory.csv',
    'programs': 'exports/program_inventory.csv',
    'copybooks': 'exports/copybook_inventory.csv',
    'datasets': 'exports/dataset_inventory.csv',
    'cics': 'exports/cics_inventory.csv'
}

for inv_type, csv_file in inventory_files.items():
    print(f"Loading {inv_type} inventory from {csv_file}...")
    loader.load_inventory(csv_file, inv_type)
    print(f"  ✓ Loaded {inv_type} inventory")

# Commit all changes
db.commit()
print("\n✓ All inventory data loaded successfully")

db.close()
```

### Example 4: Validating CSV Format Before Loading

```python
from legacy_analyzer.inventory.inventory_loader import InventoryLoader

# Initialize
db = SQLiteDatabase('analysis.db')
loader = InventoryLoader(db)

# Validate CSV format
csv_file = 'exports/cics_inventory.csv'
errors = loader.validate_csv_format(csv_file, 'cics')

if errors:
    print("Validation errors found:")
    for error in errors:
        print(f"  - {error}")
    print("\nPlease fix errors before loading.")
else:
    print("✓ CSV format is valid")
    
    # Load data
    loader.create_inventory_schema()
    loader.load_cics_inventory(csv_file)
    db.commit()
    print("✓ Data loaded successfully")

db.close()
```

### Example 5: Querying Entry Points from Enhanced CICS Inventory

```python

# Connect to database
db = SQLiteDatabase('analysis.db')

# Query ONLINE entry points (CICS transactions)
cursor = db.execute("""
    SELECT 
        resource_name as transaction_id,
        program_name,
        group_name,
        description
    FROM inventory_cics
    WHERE resource_type = 'TRANSACTION'
      AND status = 'ENABLED'
      AND program_name IS NOT NULL
    ORDER BY group_name, resource_name
""")

print("ONLINE Entry Points (CICS Transactions):")
print("-" * 80)
for row in cursor.fetchall():
    trans_id, program, group, desc = row
    print(f"{trans_id:8} -> {program:8} [{group:10}] {desc or ''}")

# Count entry points by group
cursor = db.execute("""
    SELECT 
        group_name,
        COUNT(*) as transaction_count
    FROM inventory_cics
    WHERE resource_type = 'TRANSACTION'
      AND status = 'ENABLED'
    GROUP BY group_name
    ORDER BY transaction_count DESC
""")

print("\n\nEntry Points by CICS Group:")
print("-" * 40)
for row in cursor.fetchall():
    group, count = row
    print(f"{group:15} {count:5} transactions")

db.close()
```

### Example 6: Converting CSD to Enhanced CSV

```bash
# Convert CSD file to enhanced CSV format
legacy-analyzer metadata convert-csd \
  --input app/csd/CARDDEMO.csd \
  --output exports/cics_inventory_enhanced.csv

# Load the enhanced CSV
legacy-analyzer inventory load \
  --type cics \
  --file exports/cics_inventory_enhanced.csv \
  --db results/analysis/analysis.db
```

### Example 7: Batch Loading with Error Handling

```python
from legacy_analyzer.inventory.inventory_loader import InventoryLoader
import os

def load_inventory_safe(loader, csv_file, inv_type):
    """Load inventory with error handling."""
    try:
        # Validate first
        errors = loader.validate_csv_format(csv_file, inv_type)
        if errors:
            print(f"✗ Validation failed for {csv_file}:")
            for error in errors:
                print(f"    {error}")
            return False
        
        # Load data
        loader.load_inventory(csv_file, inv_type)
        print(f"✓ Loaded {inv_type} from {csv_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error loading {csv_file}: {e}")
        return False

# Initialize
db = SQLiteDatabase('analysis.db')
loader = InventoryLoader(db)
loader.create_inventory_schema()

# Load all available inventory files
inventory_dir = 'exports'
inventory_files = [
    ('jcl_inventory.csv', 'jcl'),
    ('program_inventory.csv', 'programs'),
    ('copybook_inventory.csv', 'copybooks'),
    ('dataset_inventory.csv', 'datasets'),
    ('cics_inventory.csv', 'cics')
]

success_count = 0
for filename, inv_type in inventory_files:
    csv_path = os.path.join(inventory_dir, filename)
    if os.path.exists(csv_path):
        if load_inventory_safe(loader, csv_path, inv_type):
            success_count += 1
    else:
        print(f"⊘ Skipped {filename} (not found)")

# Commit if any succeeded
if success_count > 0:
    db.commit()
    print(f"\n✓ Successfully loaded {success_count} inventory files")
else:
    print("\n✗ No inventory files loaded")

db.close()
```

## API Reference

### InventoryLoader Class

#### Constructor

```python
loader = InventoryLoader(database: BaseDatabase)
```

**Parameters:**
- `database` (BaseDatabase): Database adapter instance (e.g., SQLiteDatabase)

#### Methods

##### create_inventory_schema()

Create all inventory tables in the database.

```python
loader.create_inventory_schema()
```

**Returns:** None

**Raises:** DatabaseError if table creation fails

##### load_inventory(csv_file: str, inventory_type: str)

Load inventory data from CSV file.

```python
loader.load_inventory('exports/cics_inventory.csv', 'cics')
```

**Parameters:**
- `csv_file` (str): Path to CSV file
- `inventory_type` (str): Type of inventory ('jcl', 'programs', 'copybooks', 'datasets', 'cics')

**Returns:** None

**Raises:** 
- ValueError: Invalid inventory type
- FileNotFoundError: CSV file not found
- IOError: Error reading CSV file

##### load_jcl_inventory(csv_file: str)

Load JCL inventory from CSV file.

```python
loader.load_jcl_inventory('exports/jcl_inventory.csv')
```

##### load_program_inventory(csv_file: str)

Load program inventory from CSV file.

```python
loader.load_program_inventory('exports/program_inventory.csv')
```

##### load_copybook_inventory(csv_file: str)

Load copybook inventory from CSV file.

```python
loader.load_copybook_inventory('exports/copybook_inventory.csv')
```

##### load_dataset_inventory(csv_file: str)

Load dataset inventory from CSV file.

```python
loader.load_dataset_inventory('exports/dataset_inventory.csv')
```

##### load_cics_inventory(csv_file: str)

Load CICS inventory from CSV file. Supports both standard and enhanced CSV formats.

```python
loader.load_cics_inventory('exports/cics_inventory.csv')
```

**Supported Formats:**
- Standard: `resource_name,resource_type,group_name,status`
- Enhanced: `resource_name,resource_type,group_name,status,program_name,dataset_name,description,language`

##### validate_csv_format(csv_file: str, inventory_type: str) → List[str]

Validate CSV file format before loading.

```python
errors = loader.validate_csv_format('exports/cics_inventory.csv', 'cics')
if errors:
    print("Validation errors:", errors)
```

**Parameters:**
- `csv_file` (str): Path to CSV file
- `inventory_type` (str): Type of inventory

**Returns:** List of error messages (empty if valid)

## Troubleshooting

### Common Issues

#### Issue 1: Missing Required Columns

**Error:**
```
ValueError: Missing required columns: resource_name, resource_type
```

**Solution:** Ensure CSV file has all required columns for the inventory type. Check the CSV format specification above.

#### Issue 2: File Not Found

**Error:**
```
FileNotFoundError: CSV file not found: exports/cics_inventory.csv
```

**Solution:** Verify the file path is correct and the file exists.

#### Issue 3: Invalid Inventory Type

**Error:**
```
ValueError: Unknown inventory type: cics_resources. Valid types: jcl, programs, copybooks, datasets, cics
```

**Solution:** Use one of the valid inventory types: `jcl`, `programs`, `copybooks`, `datasets`, or `cics`.

#### Issue 4: Encoding Issues

**Error:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Solution:** Convert CSV file to UTF-8 encoding:
```bash
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
```

#### Issue 5: Empty CSV File

**Warning:**
```
WARNING: No data rows found in CSV file
```

**Solution:** Ensure CSV file contains data rows (not just header).

### Getting Help

For additional help:

1. Check the [CICS Export Guide](exporters/docs/CICS_EXPORT_GUIDE.md) for CSD file export instructions
2. Review [CSD Parsing Guide](../docs/CSD_PARSING.md) for CSD file parsing details
3. See [CLI Reference](../docs/CLI_REFERENCE.md) for command-line usage
4. Run tests: `pytest tests/test_inventory_loader.py -v`

## Related Documentation

- [CICS Export Guide](exporters/docs/CICS_EXPORT_GUIDE.md) - How to export CICS metadata from mainframe
- [CSD Parsing Guide](../docs/CSD_PARSING.md) - Parsing CSD files
- [Entry Point Detection](../docs/ENTRY_POINT_DETECTION.md) - Using CICS metadata for entry point detection
- [Database Schema](../../DATABASE_SCHEMA.md) - Complete database schema documentation
- [CLI Reference](../docs/CLI_REFERENCE.md) - Command-line interface reference

## Changelog

### Version 1.1.0 (2025-11-21)

- Added support for enhanced CICS CSV format
- Added `dataset_name`, `description`, and `language` columns to `inventory_cics` table
- Maintained backward compatibility with standard CSV format
- Updated documentation with enhanced format examples

### Version 1.0.0 (Initial Release)

- Initial inventory loader implementation
- Support for JCL, programs, copybooks, datasets, and CICS inventory
- CSV-based loading with validation
- SQLite database integration
