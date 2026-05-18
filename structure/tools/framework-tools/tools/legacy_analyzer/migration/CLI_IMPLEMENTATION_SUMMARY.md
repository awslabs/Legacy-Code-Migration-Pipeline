# CLI Commands Implementation Summary

## Overview

Successfully implemented Task 15: CLI Commands for the migration flow export feature. This adds a new `migration` command group to the Legacy Analyzer CLI with two subcommands for building and exporting migration flows.

## Implementation Details

### 1. Migration Command Group

Added a new top-level command group `migration` with two subcommands:
- `migration build-flows` - Build migration flows from analysis data
- `migration export-flows` - Export migration flows to JSON format

### 2. Command: `migration build-flows`

**Purpose:** Build migration flows for all entry points in the database.

**Options:**
- `--db` (required): Path to database file
- `--external-config` (optional): Path to external configuration YAML file
- `--utility-threshold` (optional): Minimum number of flows to mark as utility (default: 5)

**Example Usage:**
```bash
# Basic usage
python -m tools.legacy_analyzer migration build-flows --db analyzer.db

# With external configuration
python -m tools.legacy_analyzer migration build-flows \
  --db analyzer.db \
  --external-config external_config.yaml

# With custom utility threshold
python -m tools.legacy_analyzer migration build-flows \
  --db analyzer.db \
  --utility-threshold 10
```

**Features:**
- Validates database exists before processing
- Shows progress indicators during build
- Displays elapsed time
- Shows sample flow IDs after completion
- Provides clear error messages

### 3. Command: `migration export-flows`

**Purpose:** Export migration flows from database to JSON format.

**Options:**
- `--db` (required): Path to database file
- `--output` (required): Output JSON file path
- `--flows` (optional): Comma-separated list of flow IDs to export
- `--min-complexity` (optional): Minimum complexity tier (LOW, MEDIUM, HIGH, VERY_HIGH)
- `--business-domain` (optional): Filter by business domain
- `--format` (optional): Export format (migration, standard) - default: migration
- `--extended-scope` (optional): Include utility metadata in scope output

**Example Usage:**
```bash
# Export all flows
python -m tools.legacy_analyzer migration export-flows \
  --db analyzer.db \
  --output flows.json

# Export specific flows
python -m tools.legacy_analyzer migration export-flows \
  --db analyzer.db \
  --output payroll_flows.json \
  --flows FLOW_PAYROLL1,FLOW_BILLING1

# Export with filters
python -m tools.legacy_analyzer migration export-flows \
  --db analyzer.db \
  --output high_complexity.json \
  --min-complexity HIGH \
  --business-domain Finance

# Export with extended scope
python -m tools.legacy_analyzer migration export-flows \
  --db analyzer.db \
  --output flows_extended.json \
  --extended-scope
```

**Features:**
- Validates database and output path before processing
- Shows progress indicators during export
- Displays filter information when filters are applied
- Shows summary statistics after export (by complexity, by entry type)
- Displays elapsed time
- Provides clear error messages

### 4. CLI Integration

**File Modified:** `tools/legacy_analyzer/cli.py`

**Changes:**
1. Added migration command group parser with subparsers
2. Added routing for migration command in main function
3. Implemented `_handle_migration()` dispatcher function
4. Implemented `_handle_migration_build_flows()` handler
5. Implemented `_handle_migration_export_flows()` handler

**Integration Points:**
- Uses `LegacyAnalyzerAPI` for all operations
- Follows existing CLI patterns and conventions
- Provides consistent error handling and user feedback
- Includes progress indicators and timing information

### 5. Test Coverage

**File Created:** `tests/unit/test_legacy_analyzer/test_migration_cli.py`

**Test Classes:**
1. `TestMigrationCommands` - Tests for individual migration commands
2. `TestMigrationWorkflow` - Tests for complete workflow

**Test Coverage:**
- Help command tests (3 tests)
- Error handling tests (6 tests)
- Basic functionality tests (6 tests)
- Filter and option tests (4 tests)
- Workflow integration test (1 test)

**Test Results:**
- Total tests: 19
- Passing: 19 (100%)
- Failing: 0

All tests pass successfully with complete database schema setup.

## Command Help Output

### Migration Command Group
```
$ python -m tools.legacy_analyzer migration --help

usage: __main__.py migration [-h] {build-flows,export-flows} ...

positional arguments:
  {build-flows,export-flows}
                        Migration commands
    build-flows         Build migration flows from analysis
    export-flows        Export migration flows to JSON

optional arguments:
  -h, --help            show this help message and exit
```

### Build Flows Command
```
$ python -m tools.legacy_analyzer migration build-flows --help

usage: __main__.py migration build-flows [-h] --db DB [--external-config EXTERNAL_CONFIG]
                                          [--utility-threshold UTILITY_THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  --db DB               Path to database file
  --external-config EXTERNAL_CONFIG
                        Path to external configuration YAML file
  --utility-threshold UTILITY_THRESHOLD
                        Minimum number of flows to mark as utility (default: 5)
```

### Export Flows Command
```
$ python -m tools.legacy_analyzer migration export-flows --help

usage: __main__.py migration export-flows [-h] --db DB --output OUTPUT [--flows FLOWS]
                                           [--min-complexity {LOW,MEDIUM,HIGH,VERY_HIGH}]
                                           [--business-domain BUSINESS_DOMAIN]
                                           [--format {migration,standard}]
                                           [--extended-scope]

optional arguments:
  -h, --help            show this help message and exit
  --db DB               Path to database file
  --output OUTPUT       Output JSON file path
  --flows FLOWS         Comma-separated list of flow IDs to export (optional, default: all)
  --min-complexity {LOW,MEDIUM,HIGH,VERY_HIGH}
                        Minimum complexity tier to include (optional)
  --business-domain BUSINESS_DOMAIN
                        Filter by business domain (optional)
  --format {migration,standard}
                        Export format (default: migration)
  --extended-scope      Include utility metadata in scope output
```

## Success Criteria

All subtasks completed:
- ✅ 15.1 Add 'migration' command group to CLI
- ✅ 15.2 Implement 'migration build-flows' command
- ✅ 15.3 Implement 'migration export-flows' command
- ✅ 15.4 Add --db option
- ✅ 15.5 Add --output option
- ✅ 15.6 Add --flows option (comma-separated list)
- ✅ 15.7 Add --min-complexity option
- ✅ 15.8 Add --business-domain option
- ✅ 15.9 Add --format option (migration/standard)
- ✅ 15.10 Add progress indicators
- ✅ 15.11 Write CLI tests

## Files Modified

1. `tools/legacy_analyzer/cli.py` - Added migration command group and handlers
2. `tests/unit/test_legacy_analyzer/test_migration_cli.py` - Created comprehensive test suite

## Next Steps

The CLI commands are now ready for use. Users can:
1. Run complete analysis to populate the database
2. Use `migration build-flows` to build migration flows
3. Use `migration export-flows` to export flows to JSON

The commands integrate seamlessly with the existing Legacy Analyzer CLI and follow established patterns for consistency.
