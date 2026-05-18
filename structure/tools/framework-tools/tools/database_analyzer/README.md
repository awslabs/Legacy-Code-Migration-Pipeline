# Database Analyzer Tool

Analyzes legacy mainframe database structures (VSAM files, Sequential files) and generates equivalent relational database schemas and migration scripts for modern target systems.

## Features

- **VSAM File Analysis**: Discovers and analyzes VSAM KSDS, ESDS, RRDS files
- **Sequential File Discovery**: Identifies PS (Physical Sequential) files from JCL and COBOL
- **PROC File Support**: Scans `.proc`/`.PROC` cataloged procedure files for DD/DSN statements
- **CTL File Parsing**: Extracts VSAM DEFINE CLUSTER key info from `.ctl` IDCAMS control files
- **Multi-line JCL Parsing**: Handles JCL continuation lines correctly
- **Smart Filtering**: Excludes system files, backups, duplicate formats, JCL symbolic parameters (`&name`), NULLFILE, and temporary datasets (`&&name`)
- **Symbolic Parameter Resolution**: Resolves `&param` references in DSNs using PROC default values
- **Copybook Parsing**: Extracts record structures from COBOL copybooks and PL/I include files
- **PL/I Type Support**: Maps PL/I types (`CHAR(n)`, `FIXED BIN(n)`, `FIXED DEC(n,m)`, `BIT(n)`) to SQL
- **Configurable Copybook Mappings**: DSN-to-copybook mappings via config instead of hardcoded patterns
- **Type Mapping**: Maps COBOL PIC clauses and PL/I types to SQL data types
- **Multi-Target Support**: Generates DDL for PostgreSQL and SQLite
- **Migration Scripts**: Creates data migration procedures with validation

## Installation

```bash
cd tools/framework-tools
pip install -e .
```

## Quick Start

```bash
# Analyze database structures (searches from base-path)
database-analyzer analyze \
    --base-path /path/to/project \
    --output-dir output/database

# Specify custom legacy code location
database-analyzer analyze \
    --base-path . \
    --legacy-root input/legacy/legacy_code \
    --output-dir output/database

# With verbose output
database-analyzer analyze \
    --base-path . \
    --output-dir output/db \
    --verbose
```

## Usage

### Analyze Command

Analyzes JCL, COBOL, and copybook files to discover database structures:

```bash
database-analyzer analyze [OPTIONS]

Options:
  --base-path PATH          Base path to project directory (required)
  --legacy-root PATH        Root path for legacy code (defaults to base-path)
  --output-dir PATH         Output directory for generated files (required)
  --verbose                 Enable verbose output
  --no-system-filter        Include system files (LOADLIB, SDFHLOAD, etc.)
  --no-backup-filter        Include backup files (*.BKUP, GDG generations)
  --no-duplicate-filter     Include duplicate formats (PS when VSAM exists)
  --jcl-extensions EXTS     Comma-separated JCL extensions (default: .jcl,.JCL,.proc,.PROC)
  --cbl-extensions EXTS     Comma-separated COBOL extensions (default: .cbl,.CBL,.cob,.COB)
  --cpy-extensions EXTS     Comma-separated copybook extensions (default: .cpy,.CPY)
  --ctl-extensions EXTS     Comma-separated CTL extensions (default: .ctl,.CTL)
  --pli-extensions EXTS     Comma-separated PL/I include extensions (default: .inc,.INC)
  --copybook-mappings JSON  JSON string of DSN→copybook mappings (e.g. '{"ACCTDATA":"CVACT01Y"}')
```

### Input Structure

**Flexible Structure**: The analyzer now recursively searches for files, so your legacy code can be organized in any structure. Simply point `--legacy-root` to the top-level directory containing your legacy files.

**Example structures supported**:

```
# Option 1: Organized by type
project/
├── jcl/          # All JCL files
├── cobol/        # All COBOL programs
└── copybooks/    # All copybooks

# Option 2: Organized by application
project/
├── app1/
│   ├── jcl/
│   ├── cbl/
│   └── cpy/
└── app2/
    ├── jcl/
    ├── cbl/
    └── cpy/

# Option 3: Mixed/nested structure
project/
├── src/
│   ├── batch/
│   │   ├── jobs/      # JCL files anywhere
│   │   └── programs/  # COBOL files anywhere
│   └── online/
│       └── copybooks/ # Copybooks anywhere
```

**Default structure** (backward compatible):
```
project/
├── input/
│   └── legacy/
│       └── legacy_code/
│           └── carddemoV2/
│               └── app/
│                   ├── jcl/          # JCL files with DD statements
│                   ├── cbl/          # COBOL programs
│                   └── cpy/          # COBOL copybooks
```

### Generated Outputs

```
output/database/
├── postgresql_ddl.sql          # PostgreSQL table definitions
├── sqlite_ddl.sql              # SQLite table definitions
├── postgresql_migration.sql   # PostgreSQL migration scripts
└── sqlite_migration.sql        # SQLite migration scripts
```

## How It Works

### 1. JCL Analysis
- Scans JCL files for DD statements
- Handles multi-line continuations (DSN on next line)
- Identifies VSAM files (KSDS, ESDS, RRDS)
- Identifies Sequential files (PS)

### 2. Filtering
- **System Files**: Excludes LOADLIB, SDFHLOAD, DFHCSD, etc.
- **Backup Files**: Excludes *.BKUP, GDG generations (+1, -1, etc.)
- **Duplicates**: Prefers VSAM KSDS over PS versions

### 3. CTL File Analysis
- Parses IDCAMS DEFINE CLUSTER statements from `.ctl` files
- Extracts KEYS(length, offset) and RECSZ for VSAM files
- Uses key length for more accurate DDL when no copybook is matched

### 4. Copybook Parsing
- Extracts record structures from COBOL copybooks (PIC clauses)
- Parses PL/I include files (`CHAR(n)`, `FIXED BIN(n)`, `FIXED DEC(n,m)`, `BIT(n)`)
- Falls back to PL/I parsing when COBOL parsing yields no fields
- Maps both COBOL and PL/I types to SQL types

### 5. DDL Generation
- **VSAM KSDS**: Natural key as PRIMARY KEY
- **VSAM ESDS**: Surrogate key + sequence_number
- **VSAM RRDS**: Relative record number as PRIMARY KEY
- **Sequential Files**: Surrogate key + sequence_number

### 6. Type Mapping

| COBOL Type | PL/I Type | PostgreSQL | SQLite |
|------------|-----------|------------|--------|
| PIC X(n) | CHAR(n) | VARCHAR(n) | VARCHAR(n) |
| PIC 9(n) | FIXED DEC(n) | NUMERIC(n) | INTEGER |
| PIC S9(n)V99 | FIXED DEC(n,2) | NUMERIC(n+2,2) | DECIMAL(n+2,2) |
| COMP | FIXED BIN(31) | INTEGER | INTEGER |
| COMP-3 | FIXED BIN(15) | NUMERIC | SMALLINT |
| — | BIT(n) | VARCHAR(n/8) | VARCHAR(n/8) |
| — | FLOAT BIN(n) | REAL/DOUBLE | REAL/DOUBLE |

## Examples

### Example 1: Basic Analysis

```bash
database-analyzer analyze \
    --base-path . \
    --output-dir output/gen_src_db
```

**Output**:
```
Starting database analysis...

Analyzing JCL files...
  [INCLUDE] Sequential: AWS.M2.CARDDEMO.DALYTRAN.PS
  [INCLUDE] Sequential: AWS.M2.CARDDEMO.DATEPARM
  [INCLUDE] VSAM VSAM_KSDS: AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS
  [SKIP] System file: AWS.M2.CARDDEMO.LOADLIB
  [SKIP] Backup file: AWS.M2.CARDDEMO.TRANTYPE.BKUP(+1)
  ...

============================================================
JCL Analysis Summary:
============================================================
  Total files found:           94
  System files excluded:       15
  Backup files excluded:       13
  Duplicate formats excluded:  39
  Files included:              28
============================================================

Found 16 Sequential files
Found 12 VSAM files
Found 25 COBOL file definitions
Found 29 copybooks
Analysis complete. Files generated in output/gen_src_db
```

### Example 2: Include All Files (No Filtering)

```bash
database-analyzer analyze \
    --base-path . \
    --output-dir output/db_all \
    --no-system-filter \
    --no-backup-filter \
    --no-duplicate-filter
```

### Example 3: Verbose Mode

```bash
database-analyzer analyze \
    --base-path . \
    --output-dir output/db \
    --verbose
```

### Example 4: Custom File Extensions

```bash
database-analyzer analyze \
    --base-path . \
    --legacy-root src/mainframe \
    --jcl-extensions .jcl,.JCL,.job \
    --cbl-extensions .cbl,.cob,.cobol \
    --cpy-extensions .cpy,.copy \
    --output-dir output/db
```

### Example 5: Different Legacy Code Location

```bash
database-analyzer analyze \
    --base-path . \
    --legacy-root /path/to/legacy/source \
    --output-dir output/db
```

## Configuration

The analyzer uses these default settings:

```python
config = {
    'verbose': True,
    'exclude_system_files': True,
    'exclude_backups': True,
    'exclude_duplicates': True,
    'legacy_root': None,  # Defaults to base_path
    'jcl_extensions': ['.jcl', '.JCL', '.proc', '.PROC'],
    'cbl_extensions': ['.cbl', '.CBL', '.cob', '.COB'],
    'cpy_extensions': ['.cpy', '.CPY'],
    'ctl_extensions': ['.ctl', '.CTL'],
    'pli_extensions': ['.inc', '.INC'],
    'copybook_mappings': {},  # DSN pattern → copybook name mappings
}
```

### Configuration File (Optional)

You can also use a JSON configuration file:

```json
{
  "legacy_root": "input/legacy/legacy_code",
  "jcl_extensions": [".jcl", ".JCL", ".proc", ".PROC", ".job"],
  "cbl_extensions": [".cbl", ".CBL", ".cob", ".COB"],
  "cpy_extensions": [".cpy", ".CPY"],
  "ctl_extensions": [".ctl", ".CTL"],
  "pli_extensions": [".inc", ".INC"],
  "copybook_mappings": {
    "ACCTDATA": "CVACT01Y",
    "CUSTDATA": "CVCUS01Y"
  },
  "verbose": true,
  "exclude_system_files": true,
  "exclude_backups": true,
  "exclude_duplicates": true
}
```

See `config.example.json` for a complete example.

## Core Business Tables Discovered

The analyzer discovers these core business tables:

1. ACCTDATA - Account data
2. CARDDATA - Card data
3. CARDXREF - Card cross-reference
4. CUSTDATA - Customer data
5. DALYTRAN - Daily transactions
6. DATEPARM - Date parameters
7. DISCGRP - Discount groups
8. TCATBALF - Transaction category balance
9. TRANCATG - Transaction categories
10. TRANSACT - Transactions
11. TRANTYPE - Transaction types
12. TRXFL - Transaction file
13. USRSEC - User security

## Troubleshooting

### Missing Tables

**Problem**: Expected tables not found

**Solutions**:
- Verify `--legacy-root` points to the correct directory
- Check that JCL, COBOL, and copybook files exist in the legacy root
- Run with `--verbose` to see which files are being scanned
- Verify file extensions match (use `--jcl-extensions`, `--cbl-extensions`, `--cpy-extensions` if needed)
- Check if files are being filtered (system/backup/duplicate)

### Incorrect Table Structure

**Problem**: Generated DDL doesn't match expected structure

**Solutions**:
- Verify copybook parsing is correct
- Check PIC clause to SQL type mappings
- Review field-level comments in generated DDL
- Ensure copybook names match file references

### Too Many Tables

**Problem**: More tables than expected

**Solutions**:
- Review excluded files list in verbose output
- Verify duplicate detection is working
- Check system file patterns
- Use filtering options appropriately

## API Usage

```python
from tools.database_analyzer.core.analyzer import DatabaseAnalyzer

# Create analyzer with configuration
config = {
    'verbose': True,
    'exclude_system_files': True,
    'exclude_backups': True,
    'exclude_duplicates': True,
    'legacy_root': 'input/legacy/legacy_code',
    'jcl_extensions': ['.jcl', '.JCL', '.proc', '.PROC'],
    'cbl_extensions': ['.cbl', '.CBL', '.cob'],
    'cpy_extensions': ['.cpy', '.CPY'],
    'ctl_extensions': ['.ctl', '.CTL'],
    'pli_extensions': ['.inc', '.INC'],
    'copybook_mappings': {'ACCTDATA': 'CVACT01Y'},
}

analyzer = DatabaseAnalyzer('/path/to/project', config)

# Run analysis
results = analyzer.run_analysis()

# Generate DDL
postgresql_ddl = analyzer.generate_postgresql_ddl()
sqlite_ddl = analyzer.generate_sqlite_ddl()

# Generate migration scripts
postgresql_migration = analyzer.generate_migration_scripts('postgresql')
sqlite_migration = analyzer.generate_migration_scripts('sqlite')

# Access results
print(f"Sequential files: {len(results['sequential_files'])}")
print(f"VSAM files: {len(results['vsam_files'])}")
print(f"Excluded files: {len(results['excluded_files'])}")
print(f"Statistics: {results['stats']}")
```

## Documentation

### Quick Start
- [Getting Started Guide](docs/GETTING_STARTED.md) - Step-by-step tutorial
- [Documentation Index](docs/INDEX.md) - Complete documentation overview

### Recent Changes (v2.0)
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Upgrading from hardcoded paths
- [Path Analysis](docs/PATH_ANALYSIS.md) - Detailed path refactoring

### Integration & Design
- [Integration Summary](INTEGRATION_SUMMARY.md) - LCMP Tools integration
- [Design Philosophy](DESIGN_PHILOSOPHY.md) - Architecture decisions

### Technical Details
- [Analyzer Improvements](docs/ANALYZER_IMPROVEMENTS.md) - Technical improvements
- [Test Results](docs/IMPROVED_ANALYZER_TEST_RESULTS.md) - Validation results

### Configuration
- [Example Config](config.example.json) - Sample configuration file

## Recent Changes

### Version 2.0 - Flexible Path Support

- **Removed hardcoded paths**: No longer requires specific folder structure
- **Recursive file discovery**: Automatically finds files in any subdirectory
- **Configurable extensions**: Support for custom file extensions
- **Backward compatible**: Existing usage patterns still work
- **Enhanced statistics**: Track files scanned by type

See [Migration Guide](docs/MIGRATION_GUIDE.md) for details on upgrading.

## Contributing

See the main LCMP Tools documentation for contribution guidelines.

## License

Part of the LCMP Tools suite.
