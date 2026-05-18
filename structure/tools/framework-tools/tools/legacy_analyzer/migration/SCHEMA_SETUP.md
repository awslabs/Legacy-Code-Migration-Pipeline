# Migration Flow Schema Setup

## Overview

The migration flow database schema is automatically created when needed. This document explains how the schema is set up and where it's managed.

## Schema Definition

The complete schema is defined in:
- **File:** `tools/legacy_analyzer/migration/schema.py`
- **Class:** `MigrationFlowSchema`

### Tables Created

The schema includes 9 tables:

1. **migration_flows** - Main flow metadata
2. **flow_entry_types** - Entry point types and callers for each flow
3. **flow_scope** - Artifacts within migration boundary (programs, copybooks, datasets)
4. **flow_interfaces** - Inbound and outbound interfaces
5. **flow_data_operations** - Database and dataset operations
6. **flow_dependencies** - Flow-to-flow dependencies
7. **external_program_config** - External program configuration
8. **external_caller_config** - External caller configuration
9. **program_metadata** - Program metadata including utility classification

### Indexes

The schema also creates comprehensive indexes for performance optimization on all tables.

## Automatic Schema Creation

### When Building Flows

The schema is **automatically created** when you call `build_migration_flows()`:

```python
from tools.legacy_analyzer.api import LegacyAnalyzerAPI

api = LegacyAnalyzerAPI("analyzer.db")
flow_ids = api.build_migration_flows()  # Schema created automatically if needed
```

**Implementation:** The `build_migration_flows()` method in `api.py` checks if the schema exists and creates it if needed:

```python
# Create migration flow schema if it doesn't exist
schema = MigrationFlowSchema(self.db.conn)
if not schema.is_schema_complete():
    schema.create_schema(verbose=False)
```

### Manual Schema Creation

You can also create the schema manually if needed:

```python
from tools.legacy_analyzer.migration.schema import MigrationFlowSchema

# Using the class
schema = MigrationFlowSchema(db_connection)
schema.create_schema(verbose=True)

# Or using the convenience function
from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
create_migration_flow_schema(db_connection, verbose=True)
```

## Schema Verification

### Check if Schema Exists

```python
from tools.legacy_analyzer.migration.schema import MigrationFlowSchema

schema = MigrationFlowSchema(db_connection)

# Check if all tables exist
if schema.is_schema_complete():
    print("Schema is complete")
else:
    missing = schema.get_missing_tables()
    print(f"Missing tables: {missing}")
```

### Verify Schema

```python
# Get detailed verification results
verification = schema.verify_schema(verbose=True)
# Returns: {'migration_flows': True, 'flow_entry_types': True, ...}
```

### Get Table Counts

```python
# Get row counts for all tables
counts = schema.get_table_counts()
# Returns: {'migration_flows': 10, 'flow_entry_types': 25, ...}
```

## Schema Management

### Drop Schema

**WARNING:** This deletes all migration flow data!

```python
schema = MigrationFlowSchema(db_connection)
schema.drop_schema(verbose=True)
```

## Integration with Analysis Process

The migration flow schema is **separate** from the main analysis schema (inventory, dependencies, etc.). This separation allows:

1. **Independent lifecycle** - Migration flows can be rebuilt without affecting analysis data
2. **Optional feature** - Users can run analysis without building migration flows
3. **Clean separation** - Migration-specific tables don't clutter the main schema

### Typical Workflow

```bash
# Step 1: Run analysis (creates inventory and dependencies tables)
python -m tools.legacy_analyzer analyze --source-dir ./code --db analyzer.db

# Step 2: Build migration flows (creates migration flow tables automatically)
python -m tools.legacy_analyzer migration build-flows --db analyzer.db

# Step 3: Export flows
python -m tools.legacy_analyzer migration export-flows --db analyzer.db --output flows.json
```

## Test Setup

In tests, the schema is created explicitly in the `setup_test_database()` function to ensure all required tables exist:

```python
def setup_test_database(db_path):
    """Set up a test database with migration flow schema."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    
    # Create all migration flow tables
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    conn.close()
```

This ensures tests have a complete database environment without relying on the automatic creation logic.

## Schema Evolution

When adding new tables or modifying the schema:

1. Update `MigrationFlowSchema` class in `schema.py`
2. Add new table creation method (e.g., `_create_new_table()`)
3. Call the new method in `create_schema()`
4. Update `verify_schema()` to include the new table
5. Update test setup if needed

## Best Practices

1. **Let it auto-create** - Don't manually create the schema unless you have a specific reason
2. **Check before dropping** - Always verify what data exists before dropping the schema
3. **Use verification** - Check schema completeness before operations that require it
4. **Separate concerns** - Keep migration schema separate from analysis schema

## Troubleshooting

### Schema Not Found Error

If you get "no such table" errors:

```python
# Check if schema exists
from tools.legacy_analyzer.migration.schema import verify_migration_flow_schema

if not verify_migration_flow_schema(db_connection):
    print("Schema is incomplete or missing")
    # Create it
    from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
    create_migration_flow_schema(db_connection)
```

### Incomplete Schema

If some tables are missing:

```python
schema = MigrationFlowSchema(db_connection)
missing = schema.get_missing_tables()
if missing:
    print(f"Missing tables: {missing}")
    # Recreate schema
    schema.create_schema()
```

### Schema Version Mismatch

If the schema structure has changed:

```python
# Drop old schema
schema.drop_schema()

# Create new schema
schema.create_schema()

# Note: This will delete all existing migration flow data!
```

## Summary

- ✅ Schema is **automatically created** when building flows
- ✅ Schema is **separate** from main analysis schema
- ✅ Schema can be **verified** and **managed** programmatically
- ✅ Tests create schema **explicitly** for complete test environment
- ✅ Schema includes **9 tables** and **comprehensive indexes**
