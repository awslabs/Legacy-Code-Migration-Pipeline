# Changelog

All notable changes to the Database Analyzer tool will be documented in this file.

## [3.0.0] - 2025

### Added
- **PROC File Support**: Default JCL extensions now include `.proc`/`.PROC` for cataloged procedure files containing DD/DSN statements
- **CTL File Parsing**: New `analyze_ctl_files()` extracts VSAM DEFINE CLUSTER key info (KEYS, RECSZ) from `.ctl` IDCAMS control files; key length used in DDL when no copybook matched
- **PL/I Copybook Parsing**: New `parse_pli_record()` and `analyze_pli_copybooks()` support `CHAR(n)`, `FIXED BIN(n)`, `FIXED DEC(n,m)`, `BIT(n)`, `FLOAT BIN(n)` types with SQL type mapping
- **Symbolic Parameter Resolution**: `_resolve_symbolic_in_dsn()` resolves `&param` references in DSNs using PROC default values
- **Smart Filtering**: Excludes JCL symbolic parameters (`&name` without dots), `NULLFILE`, `DUMMY`, and temporary datasets (`&&name`)
- **Configurable Copybook Mappings**: DSN-to-copybook mappings via `copybook_mappings` config dict (replaces hardcoded CardDemo patterns)
- **Leaf Field Handling**: `_get_leaf_fields()` handles both COBOL (level 05) and PL/I (level 03) field conventions for DDL generation
- **New CLI Options**:
  - `--ctl-extensions`: Customize CTL file extensions
  - `--pli-extensions`: Customize PL/I include file extensions
  - `--copybook-mappings`: JSON string for DSN→copybook mappings
- **New Config Options**: `ctl_extensions`, `pli_extensions`, `copybook_mappings` in config file

### Changed
- **Default JCL Extensions**: Now `.jcl`, `.JCL`, `.proc`, `.PROC` (was `.jcl`, `.JCL`)
- **Copybook Matching**: Tightened partial matching to require exact DSN segment match or 4+ char substring match
- **PL/I Fallback**: `analyze_copybooks()` falls back to PL/I parsing when COBOL parsing yields no fields

### Fixed
- PROC files with DD/DSN statements were not scanned (Bug #3 from customer testing)
- Spurious tables generated from JCL symbolic parameters like `&EAFMLIB`
- `NULLFILE` and `&&name` temporary datasets not filtered out

---

## [2.0.0] - 2024

### Added
- **Configurable Legacy Root**: New `--legacy-root` parameter to specify where legacy code lives
- **Recursive File Discovery**: Automatically finds files in any subdirectory structure
- **Custom File Extensions**: Support for configurable file extensions via CLI and config
  - `--jcl-extensions`: Customize JCL file extensions
  - `--cbl-extensions`: Customize COBOL file extensions
  - `--cpy-extensions`: Customize copybook file extensions
- **Enhanced Statistics**: Track files scanned by type (JCL, COBOL, copybooks)
- **Configuration File Support**: Example configuration file (`config.example.json`)
- **Comprehensive Documentation**:
  - Migration Guide for upgrading from v1.x
  - Path Analysis document detailing all path changes
  - Documentation Index for easy navigation
  - Updated Getting Started guide

### Changed
- **Path Handling**: Removed hardcoded paths (`input/legacy/legacy_code/carddemoV2/app/`)
- **File Discovery**: Changed from direct `glob()` to recursive `rglob()` search
- **Statistics Output**: Enhanced to show file scan counts by type
- **CLI Help**: Updated with new parameters and examples

### Improved
- **Flexibility**: Works with any folder organization
- **Usability**: No need to reorganize existing codebases
- **Maintainability**: No hardcoded paths to update

### Backward Compatibility
- ✅ Fully backward compatible with v1.x
- ✅ Existing usage patterns work without changes
- ✅ Defaults to `base_path` if `legacy_root` not specified

### Migration
See [Migration Guide](docs/MIGRATION_GUIDE.md) for detailed upgrade instructions.

---

## [1.0.0] - Initial Release

### Features
- **JCL Analysis**: Parse JCL files for DD statements
- **Multi-line JCL Parsing**: Handle JCL continuation lines
- **COBOL Analysis**: Parse COBOL programs for SELECT statements
- **Copybook Parsing**: Extract record structures from copybooks
- **VSAM Support**: Discover VSAM KSDS, ESDS, RRDS files
- **Sequential Files**: Identify PS (Physical Sequential) files
- **Smart Filtering**:
  - Exclude system files (LOADLIB, SDFHLOAD, etc.)
  - Exclude backup files (*.BKUP, GDG generations)
  - Exclude duplicate formats (prefer VSAM over PS)
- **DDL Generation**:
  - PostgreSQL DDL with proper data types
  - SQLite DDL with proper data types
- **Type Mapping**: Map COBOL PIC clauses to SQL types
- **Primary Key Detection**: Identify natural keys for VSAM KSDS
- **Migration Scripts**: Generate data migration procedures
- **Statistics**: Detailed analysis statistics
- **Verbose Mode**: Optional detailed logging

### Supported File Types
- JCL files (`.jcl`)
- COBOL programs (`.cbl`)
- COBOL copybooks (`.cpy`)

### Output Files
- `postgresql_ddl.sql` - PostgreSQL table definitions
- `sqlite_ddl.sql` - SQLite table definitions
- `postgresql_migration.sql` - PostgreSQL migration scripts
- `sqlite_migration.sql` - SQLite migration scripts

### Core Tables Discovered
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

---

## Version Comparison

| Feature | v1.0 | v2.0 | v3.0 |
|---------|------|------|------|
| Hardcoded paths | ❌ Yes | ✅ No | ✅ No |
| Configurable root | ❌ No | ✅ Yes | ✅ Yes |
| Recursive search | ❌ No | ✅ Yes | ✅ Yes |
| Custom extensions | ❌ No | ✅ Yes | ✅ Yes |
| File scan stats | ❌ No | ✅ Yes | ✅ Yes |
| PROC file support | ❌ No | ❌ No | ✅ Yes |
| CTL file parsing | ❌ No | ❌ No | ✅ Yes |
| PL/I copybook parsing | ❌ No | ❌ No | ✅ Yes |
| Symbolic param resolution | ❌ No | ❌ No | ✅ Yes |
| NULLFILE/temp filtering | ❌ No | ❌ No | ✅ Yes |
| Copybook mappings config | ❌ No | ❌ No | ✅ Yes |
| JCL parsing | ✅ Yes | ✅ Yes | ✅ Yes |
| COBOL parsing | ✅ Yes | ✅ Yes | ✅ Yes |
| Copybook parsing | ✅ Yes | ✅ Yes | ✅ Yes |
| Smart filtering | ✅ Yes | ✅ Yes | ✅ Yes |
| DDL generation | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Upgrade Path

### From v1.0 to v2.0

**No changes required** if using default structure:
```bash
# This still works exactly as before
database-analyzer analyze --base-path . --output-dir output/database
```

**For custom structures**, add `--legacy-root`:
```bash
# New capability in v2.0
database-analyzer analyze \
  --base-path . \
  --legacy-root your/custom/path \
  --output-dir output/database
```

---

## Future Roadmap

### Planned Features
- [ ] Support for additional target databases (MySQL, Oracle)
- [ ] Configuration file loading (JSON/YAML)
- [ ] Exclude patterns for directories
- [ ] Include patterns for more specific searches
- [ ] Parallel file processing for large codebases
- [ ] Caching for repeated runs
- [ ] HTML report generation
- [ ] Relationship detection between tables
- [ ] Foreign key inference

### Under Consideration
- [ ] IMS database support
- [ ] DB2 DDL parsing
- [ ] Data profiling capabilities
- [ ] Sample data generation
- [ ] Test data creation

---

## Breaking Changes

### v2.0
- None - fully backward compatible

### v1.0
- Initial release

---

## Contributors

See the main LCMP Tools documentation for contributor information.

---

## License

Part of the LCMP Tools suite.
