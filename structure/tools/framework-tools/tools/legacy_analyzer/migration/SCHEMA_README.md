# Migration Flow Schema

This directory contains the database schema for migration-focused flow export.

## Overview

The migration flow schema provides a structured way to store and query program flows optimized for migration planning. It separates scope (what's inside the migration boundary) from interfaces (what crosses the boundary), and integrates complexity metrics and data operations.

## Schema Tables

### 1. migration_flows

Primary table storing flow metadata.

**Columns:**
- `flow_id` (VARCHAR, PRIMARY KEY): Unique flow identifier (format: FLOW_{PROGRAM_NAME})
- `name` (VARCHAR): Human-readable flow name
- `entry_program` (VARCHAR): Entry point program name
- `primary_entry_type` (VARCHAR): Most common invocation type (JCL, CICS_TRANSACTION, etc.)
- `total_programs` (INTEGER): Count of programs in flow
- `total_copybooks` (INTEGER): Count of copybooks in flow
- `total_datasets` (INTEGER): Count of datasets in flow
- `complexity_total_lines` (INTEGER): Sum of LOC across all programs
- `complexity_cyclomatic` (INTEGER): Sum of cyclomatic complexity
- `complexity_score` (DECIMAL): Composite complexity score
- `complexity_tier` (VARCHAR): LOW, MEDIUM, HIGH, VERY_HIGH
- `priority` (INTEGER): Migration priority (optional)
- `business_domain` (VARCHAR): Business domain classification (optional)
- `created_date` (DATE): Creation date
- `updated_date` (DATE): Last update date

### 2. flow_entry_types

Tracks all invocation types and callers for each entry point.

**Key Concept:** A single program can be invoked in multiple ways (JCL, CICS, screen, etc.). This table tracks ALL invocation types and their callers.

**Columns:**
- `flow_id` (VARCHAR, FK): Reference to migration_flows
- `entry_type` (VARCHAR): JCL, CICS_TRANSACTION, CICS_PROGRAM, SCREEN, BATCH, EXTERNAL_CALL
- `caller_source` (VARCHAR): JCL name, transaction ID, screen name, etc.
- `metadata_json` (TEXT): Additional metadata as JSON

**Primary Key:** (flow_id, entry_type, caller_source)

**Example:**
```
FLOW_PAYROLL1 | JCL | PAYROLL01 | {"jclName": "PAYROLL01", "jobName": "PAYJOB"}
FLOW_PAYROLL1 | JCL | PAYWEEK   | {"jclName": "PAYWEEK", "jobName": "WEEKLY"}
FLOW_PAYROLL1 | CICS_TRANSACTION | PAY1 | {"transactionId": "PAY1"}
```

### 3. flow_scope

Stores artifacts within the migration boundary.

**Columns:**
- `flow_id` (VARCHAR, FK): Reference to migration_flows
- `artifact_type` (VARCHAR): PROGRAM, COPYBOOK, DATASET
- `artifact_name` (VARCHAR): Artifact name

**Primary Key:** (flow_id, artifact_type, artifact_name)

### 4. flow_interfaces

Stores boundary crossing points (inbound and outbound).

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Auto-increment ID
- `flow_id` (VARCHAR, FK): Reference to migration_flows
- `direction` (VARCHAR): INBOUND, OUTBOUND
- `interface_type` (VARCHAR): JCL, CICS_TRANSACTION, PROGRAM_CALL, etc.
- `source` (VARCHAR): Source artifact name
- `target` (VARCHAR): Target artifact name
- `external` (BOOLEAN): True if target is external
- `metadata_json` (TEXT): Additional metadata as JSON

**Note:** Entry point invocations are NOT stored as inbound interfaces. They are tracked in flow_entry_types.

### 5. flow_data_operations

Stores database and dataset operations.

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Auto-increment ID
- `flow_id` (VARCHAR, FK): Reference to migration_flows
- `operation_category` (VARCHAR): DATABASE, DATASET
- `operation_type` (VARCHAR): READ, WRITE, UPDATE, DELETE, SELECT, INSERT
- `db_type` (VARCHAR): DB2, IMS, VSAM, etc. (for DATABASE category)
- `target` (VARCHAR): Table/file/dataset name
- `program` (VARCHAR): Program performing operation
- `mode` (VARCHAR): INPUT, OUTPUT, INOUT (for DATASET category)

### 6. flow_dependencies

Stores flow-to-flow dependencies.

**Columns:**
- `flow_id` (VARCHAR, FK): Reference to migration_flows
- `depends_on_flow_id` (VARCHAR, FK): Reference to migration_flows
- `dependency_type` (VARCHAR): REQUIRED, DEPENDENT

**Primary Key:** (flow_id, depends_on_flow_id, dependency_type)

## Indexes

Performance indexes are created on:
- migration_flows: primary_entry_type, complexity_tier, business_domain, entry_program
- flow_entry_types: flow_id, entry_type, caller_source
- flow_scope: flow_id, artifact_type, artifact_name
- flow_interfaces: flow_id, direction, interface_type, source, target
- flow_data_operations: flow_id, operation_category, target, program
- flow_dependencies: flow_id, depends_on_flow_id, dependency_type

## Usage

### Creating Schema

```python
from tools.legacy_analyzer.migration import MigrationFlowSchema

# Create schema
conn = sqlite3.connect('analyzer.db')
schema = MigrationFlowSchema(conn)
schema.create_schema(verbose=True)
```

```python
# Using Python API
from tools.legacy_analyzer.migration import create_migration_flow_schema, verify_migration_flow_schema

# Create schema
success = create_migration_flow_schema(conn, verbose=True)

# Verify
is_complete = verify_migration_flow_schema(conn, verbose=True)
```

### Verifying Schema

```python
from tools.legacy_analyzer.migration import MigrationFlowSchema

conn = sqlite3.connect('analyzer.db')
schema = MigrationFlowSchema(conn)

# Check if complete
if schema.is_schema_complete():
    print("Schema is complete")
else:
    missing = schema.get_missing_tables()
    print(f"Missing tables: {missing}")

# Get table counts
counts = schema.get_table_counts()
for table, count in counts.items():
    print(f"{table}: {count} rows")
```

## Design Principles

### One Flow Per Entry Point Program

A key design principle is that each entry point program has ONE flow, regardless of how many ways it can be invoked.

**Example:**
- Program: PAYROLL1
- Invoked by: JCL (PAYROLL01, PAYWEEK), CICS (PAY1), Screen (PAYSCREEN)
- Result: ONE flow (FLOW_PAYROLL1) with FOUR invocation types

This correctly models the reality that a program's execution path (the flow) is independent of how it's invoked.

### Scope vs Interfaces

The schema clearly separates:
- **Scope**: Artifacts INSIDE the migration boundary (flow_scope table)
- **Interfaces**: Boundary crossing points (flow_interfaces table)

This separation enables precise service boundary definition for migration planning.

### Entry Points vs Inbound Interfaces

- **Entry point invocations** (JCL, CICS, screens) are stored in flow_entry_types
- **Inbound interfaces** are external programs calling INTO the flow (stored in flow_interfaces)

Entry point invocations are NOT inbound interfaces because they represent how the flow is triggered, not how external systems interact with it.

## Migration Strategy

The schema migration script:
1. Checks for existing tables
2. Creates backup (optional)
3. Creates missing tables
4. Creates indexes
5. Verifies schema completeness

The migration is idempotent - running it multiple times is safe.

## Testing

Run the test script to verify schema:

```bash
python tools/legacy_analyzer/migration/test_schema.py
```

This creates an in-memory database, creates the schema, and verifies all tables and constraints work correctly.

## Files

- `schema.py`: Schema definition and creation
- `test_schema.py`: Test script for schema verification
- `SCHEMA_README.md`: This file

## Next Steps

After creating the schema, the next tasks are:
1. Create data models (MigrationFlow, FlowScope, etc.)
2. Implement flow builder to populate tables
3. Implement flow exporter to generate JSON
4. Add CLI commands for building and exporting flows
