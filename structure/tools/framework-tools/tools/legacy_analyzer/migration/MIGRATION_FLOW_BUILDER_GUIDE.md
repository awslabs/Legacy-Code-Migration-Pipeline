# MigrationFlowBuilder Guide

## Overview

The `MigrationFlowBuilder` is the main orchestrator for building migration-focused flow data from dependency analysis. It integrates all components (entry point detection, scope identification, interface identification, data operation inference, complexity calculation, and flow dependencies) to create complete migration flows.

## Key Concepts

### Flow

A **flow** represents a complete execution path starting from an entry point program and including all called programs, copybooks, and data operations. Each flow has:

- **Flow ID**: Unique identifier (format: `FLOW_{PROGRAM_NAME}`)
- **Entry Point**: The program that starts the flow
- **Entry Types**: All ways the entry point can be invoked
- **Scope**: Artifacts within the migration boundary
- **Interfaces**: Boundary crossing points
- **Data Operations**: Database and dataset operations
- **Complexity**: Aggregate complexity metrics
- **Dependencies**: Flow-to-flow dependencies

### One Flow Per Entry Point Program

**Important Design Principle**: A single entry point program generates ONE flow, regardless of how many ways it can be invoked.

Example:
```
Program: PAYROLL1
├── Invoked by JCL: PAYROLL01 (daily batch)
├── Invoked by JCL: PAYWEEK (weekly batch)
├── Invoked by CICS Transaction: PAY1 (online)
└── Defined in CSD as CICS Program: PAYROLL1

Result: ONE flow (FLOW_PAYROLL1) with FOUR entry types
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              MigrationFlowBuilder                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐          │
│  │  FlowAnalyzer    │      │  EntryPointType  │          │
│  │                  │      │  Detector        │          │
│  └──────────────────┘      └──────────────────┘          │
│           │                          │                     │
│  ┌────────▼──────────────────────────▼─────────┐         │
│  │     MigrationFlowBuilder                    │         │
│  │  - Identifies entry points                  │         │
│  │  - Builds flows                             │         │
│  │  - Integrates all components                │         │
│  │  - Writes to database                       │         │
│  └────────┬────────────────────────────────────┘         │
│           │                                               │
│  ┌────────▼────────────────────────────────────┐         │
│  │     Database (6 tables)                     │         │
│  │  - migration_flows                          │         │
│  │  - flow_entry_types                         │         │
│  │  - flow_scope                               │         │
│  │  - flow_interfaces                          │         │
│  │  - flow_data_operations                     │         │
│  │  - flow_dependencies                        │         │
│  └─────────────────────────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Basic Usage

```python
from tools.legacy_analyzer.migration.flow_builder import MigrationFlowBuilder
import sqlite3

# Initialize with database connection
conn = sqlite3.connect('analyzer.db')
builder = MigrationFlowBuilder(conn)

# Build all flows
flow_ids = builder.build_all_flows()
print(f"Built {len(flow_ids)} flows")

# Build specific flow
flow_id = builder.build_flow('PAYROLL1')
print(f"Built flow: {flow_id}")

# Update dependencies after all flows built
builder.update_flow_dependencies()
```

### Flow ID Generation

```python
from tools.legacy_analyzer.migration.flow_builder import generate_flow_id

# Generate flow IDs
flow_id = generate_flow_id("PAYROLL1")  # → FLOW_PAYROLL1
flow_id = generate_flow_id("PAY-ROLL#01")  # → FLOW_PAY_ROLL_01
flow_id = generate_flow_id("billing")  # → FLOW_BILLING
```

### Building Flows with External Configuration

```python
# External configuration is loaded automatically
# from external_program_config and external_caller_config tables

builder = MigrationFlowBuilder(conn)

# External programs and callers are used during flow building
flow_id = builder.build_flow('PAYROLL1')
```

## Flow Building Process

The builder follows a 9-step process for each flow:

### Step 1: Generate Flow ID

```python
flow_id = generate_flow_id(entry_program)
# Example: "PAYROLL1" → "FLOW_PAYROLL1"
```

### Step 2: Analyze Program Flow

```python
flow = self.flow_analyzer.analyze_flow(entry_program, max_depth=10)
# Returns: ProgramFlow object with programs and dependencies
```

### Step 3: Detect Entry Point Types

```python
entry_types = self.entry_point_detector.detect_entry_point_types(entry_program)
# Returns: List of entry type dictionaries with callers
```

Example result:
```python
[
    {
        'type': 'JCL',
        'callers': [
            {'source': 'PAYROLL01', 'metadata': {'jclName': 'PAYROLL01'}},
            {'source': 'PAYWEEK', 'metadata': {'jclName': 'PAYWEEK'}}
        ]
    },
    {
        'type': 'CICS_TRANSACTION',
        'callers': [
            {'source': 'PAY1', 'metadata': {'transactionId': 'PAY1'}}
        ]
    }
]
```

### Step 4: Identify Scope

```python
scope = self.identify_scope(flow)
# Returns: {'programs': [...], 'copybooks': [...], 'datasets': [...]}
```

### Step 5: Identify Interfaces

```python
interfaces = self.identify_interfaces(
    flow, entry_program, external_programs, external_callers
)
# Returns: {'inbound': [...], 'outbound': [...]}
```

### Step 6: Infer Data Operations

```python
data_operations = self.data_operation_inferencer.infer_all_operations(flow.programs)
# Returns: {'databases': [...], 'datasets': [...]}
```

### Step 7: Calculate Complexity

```python
complexity = self.calculate_flow_complexity(flow.programs)
# Returns: {
#     'totalPrograms': 3,
#     'totalLines': 2500,
#     'cyclomaticComplexity': 45,
#     'compositeScore': 67.5,
#     'tier': 'MEDIUM'
# }
```

### Step 8: Identify Flow Dependencies

```python
dependencies = self.identify_flow_dependencies(flow_id, entry_program, interfaces)
# Returns: {'requiredFlows': [...], 'dependentFlows': [...]}
```

### Step 9: Write to Database

```python
self._write_flow_to_database(
    flow_id, entry_program, primary_type, entry_types,
    scope, interfaces, data_operations, complexity, dependencies
)
```

## Database Schema

The builder writes to 6 tables:

### 1. migration_flows

Main flow metadata:
```sql
CREATE TABLE migration_flows (
    flow_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200),
    entry_program VARCHAR(44) NOT NULL,
    primary_entry_type VARCHAR(20),
    total_programs INTEGER,
    total_copybooks INTEGER,
    total_datasets INTEGER,
    complexity_total_lines INTEGER,
    complexity_cyclomatic INTEGER,
    complexity_score DECIMAL(10,2),
    complexity_tier VARCHAR(10),
    priority INTEGER,
    business_domain VARCHAR(100),
    created_date DATE,
    updated_date DATE
)
```

### 2. flow_entry_types

All invocation types and callers:
```sql
CREATE TABLE flow_entry_types (
    flow_id VARCHAR(100),
    entry_type VARCHAR(20),
    caller_source VARCHAR(100),
    metadata_json TEXT,
    PRIMARY KEY (flow_id, entry_type, caller_source)
)
```

### 3. flow_scope

Artifacts within migration boundary:
```sql
CREATE TABLE flow_scope (
    flow_id VARCHAR(100),
    artifact_type VARCHAR(20),  -- 'PROGRAM', 'COPYBOOK', 'DATASET'
    artifact_name VARCHAR(44),
    PRIMARY KEY (flow_id, artifact_type, artifact_name)
)
```

### 4. flow_interfaces

Boundary crossing points:
```sql
CREATE TABLE flow_interfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id VARCHAR(100),
    direction VARCHAR(10),  -- 'INBOUND', 'OUTBOUND'
    interface_type VARCHAR(20),
    source VARCHAR(44),
    target VARCHAR(44),
    external BOOLEAN,
    metadata_json TEXT
)
```

### 5. flow_data_operations

Database and dataset operations:
```sql
CREATE TABLE flow_data_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id VARCHAR(100),
    operation_category VARCHAR(20),  -- 'DATABASE', 'DATASET'
    operation_type VARCHAR(20),
    db_type VARCHAR(20),
    target VARCHAR(100),
    program VARCHAR(44),
    mode VARCHAR(10)
)
```

### 6. flow_dependencies

Flow-to-flow dependencies:
```sql
CREATE TABLE flow_dependencies (
    flow_id VARCHAR(100),
    depends_on_flow_id VARCHAR(100),
    dependency_type VARCHAR(20),  -- 'REQUIRED', 'DEPENDENT'
    PRIMARY KEY (flow_id, depends_on_flow_id, dependency_type)
)
```

## Entry Point Identification

The builder identifies entry points from multiple sources:

### 1. JCL Invocations

Programs invoked by JCL:
```sql
SELECT DISTINCT target_artifact_name
FROM artifact_dependencies
WHERE source_artifact_type = 'JCL'
  AND target_artifact_type = 'PROGRAM'
  AND dependency_type IN ('JCL_EXEC', 'EXEC_PGM', 'PROGRAM_CALL')
```

### 2. CICS Transactions

Programs invoked by CICS transactions:
```sql
SELECT DISTINCT target_artifact_name
FROM artifact_dependencies
WHERE dependency_type IN ('CICS_TRANSACTION', 'TRANSACTION')
  AND target_artifact_type = 'PROGRAM'
```

### 3. CSD Definitions

Programs defined in CSD:
```sql
SELECT DISTINCT target_artifact_name
FROM artifact_dependencies
WHERE dependency_type = 'CICS_PROGRAM'
  AND target_artifact_type = 'PROGRAM'
```

### 4. BMS Screens

Programs called from BMS screens:
```sql
SELECT DISTINCT target_artifact_name
FROM artifact_dependencies
WHERE source_artifact_type = 'SCREEN'
  AND target_artifact_type = 'PROGRAM'
  AND dependency_type IN ('SCREEN_CALL', 'BMS_MAP')
```

### 5. External Callers

Programs with configured external callers:
```python
for caller_name, calls in external_callers.items():
    for call_info in calls:
        target = call_info.get('target')
        if target:
            entry_points.add(target)
```

## Primary Type Determination

The builder determines the primary invocation type using:

### 1. Caller Count

The type with the most callers is primary:
```python
type_counts = {}
for entry_type in entry_types:
    type_name = entry_type['type']
    caller_count = len(entry_type.get('callers', []))
    type_counts[type_name] = caller_count

max_count = max(type_counts.values())
```

### 2. Priority Order (for ties)

If multiple types have the same caller count:
```python
priority_order = [
    'JCL',              # Batch processing (highest priority)
    'CICS_TRANSACTION', # Online processing
    'CICS_PROGRAM',     # CSD definition
    'SCREEN',           # Screen-driven
    'EXTERNAL_CALL'     # External invocation
]
```

## Error Handling

The builder handles errors gracefully:

### 1. Transaction-Based Writes

All database writes use transactions:
```python
try:
    cursor.execute("BEGIN TRANSACTION")
    # ... write operations ...
    self.db.commit()
except Exception as e:
    self.db.rollback()
    raise Exception(f"Failed to write flow: {e}")
```

### 2. Missing Data Handling

- **Missing complexity data**: Uses default values (0, UNKNOWN)
- **Missing dependencies**: Returns empty arrays
- **Missing entry types**: Continues with empty list

### 3. Warning Messages

Non-critical errors are logged as warnings:
```python
print(f"Warning: Error loading dependencies: {e}")
```

## Performance Considerations

### 1. Dependency Loading

Dependencies are loaded once during initialization:
```python
self.dependencies = self._load_dependencies()
```

### 2. Batch Operations

Uses `INSERT OR REPLACE` for idempotent writes:
```python
cursor.execute("""
    INSERT OR REPLACE INTO migration_flows (...)
    VALUES (...)
""")
```

### 3. Transaction Management

Groups all writes in single transaction:
```python
cursor.execute("BEGIN TRANSACTION")
# ... multiple writes ...
self.db.commit()
```

### 4. Index Support

Leverages database indexes for queries:
- `idx_migration_flows_entry_program`
- `idx_flow_scope_artifact_name`
- `idx_flow_interfaces_source`
- `idx_flow_interfaces_target`

## Best Practices

### 1. Always Update Dependencies

After building all flows, update dependencies:
```python
builder.build_all_flows()
builder.update_flow_dependencies()
```

### 2. Use External Configuration

Configure external programs and callers for accurate boundaries:
```python
# Load external configuration before building
# (automatically loaded by builder)
```

### 3. Handle Errors

Wrap flow building in try-except:
```python
try:
    flow_id = builder.build_flow('PAYROLL1')
except Exception as e:
    print(f"Failed to build flow: {e}")
```

### 4. Verify Schema

Ensure schema exists before building:
```python
from tools.legacy_analyzer.migration.schema import MigrationFlowSchema

schema = MigrationFlowSchema(conn)
if not schema.is_schema_complete():
    schema.create_schema()
```

## Common Issues

### Issue 1: No Entry Points Found

**Symptom**: `build_all_flows()` returns empty list

**Solution**: Ensure dependencies are loaded and entry points exist:
```python
# Check for JCL invocations
cursor.execute("""
    SELECT COUNT(*) FROM artifact_dependencies
    WHERE source_artifact_type = 'JCL'
      AND target_artifact_type = 'PROGRAM'
""")
```

### Issue 2: Missing Complexity Data

**Symptom**: Complexity tier is "UNKNOWN"

**Solution**: Run complexity analysis first:
```python
from tools.legacy_analyzer.analysis.complexity_analyzer import ComplexityAnalyzer

analyzer = ComplexityAnalyzer(conn)
analyzer.analyze_all_programs()
```

### Issue 3: Empty Flow Scope

**Symptom**: Flow has no programs in scope

**Solution**: Check flow analysis results:
```python
flow = builder.flow_analyzer.analyze_flow('PAYROLL1')
print(f"Programs in flow: {flow.programs}")
```

## Examples

See `demo_migration_flow_builder.py` for complete examples:

1. Flow ID generation
2. Primary type determination
3. Database schema verification
4. Building a single flow
5. Building all flows

## Related Components

- **FlowAnalyzer**: Analyzes program execution flows
- **EntryPointTypeDetector**: Detects all invocation types
- **DataOperationInferencer**: Infers data operations
- **ExternalConfigLoader**: Loads external configuration
- **MigrationFlowSchema**: Database schema management

## Next Steps

After building flows:

1. **Export flows to JSON**: Use MigrationFlowExporter (Task 11)
2. **Filter flows**: Apply complexity/domain filters (Task 13)
3. **Visualize flows**: Generate diagrams (future enhancement)
4. **Plan migration**: Use flow dependencies for sequencing

## References

- Design Document: `.kiro/specs/migration-flow-export/design.md`
- Requirements: `.kiro/specs/migration-flow-export/requirements.md`
- Task List: `.kiro/specs/migration-flow-export/tasks.md`
- Test Suite: `tests/unit/test_legacy_analyzer/test_migration_flow_builder.py`
