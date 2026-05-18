# Data Operation Inference Guide

## Overview

The `DataOperationInferencer` class infers data operations (database and dataset operations) from existing dependency data in the `artifact_dependencies` table. This eliminates the need to re-parse source code when building migration flows.

## Quick Start

```python
from tools.legacy_analyzer.migration import DataOperationInferencer

# Initialize with database connection
inferencer = DataOperationInferencer(db_connection)

# Infer all operations for a list of programs
operations = inferencer.infer_all_operations(["PAYROLL1", "BILLING1"])

# Access results
print(f"Database operations: {len(operations['databases'])}")
print(f"Dataset operations: {len(operations['datasets'])}")
```

## Supported Operation Types

### Database Operations

#### SQL Operations
- **SELECT**: Read data from tables
- **INSERT**: Add new records
- **UPDATE**: Modify existing records
- **DELETE**: Remove records
- **MERGE**: Upsert operations
- **CREATE/DROP/ALTER**: DDL operations

#### CICS File Operations
- **CICS_READ** → READ
- **CICS_WRITE** → WRITE
- **CICS_REWRITE** → UPDATE
- **CICS_DELETE** → DELETE
- **CICS_STARTBR** → READ (browse start)
- **CICS_READNEXT** → READ (browse next)
- **CICS_READPREV** → READ (browse previous)

#### Database Types
- **DB2**: IBM DB2 database
- **IMS**: IMS database
- **VSAM**: VSAM files (via CICS)
- **IDMS**: IDMS database
- **ADABAS**: ADABAS database
- **SQL**: Generic SQL database

### Dataset Operations

#### Access Modes
- **INPUT**: Read-only access
- **OUTPUT**: Write-only access
- **INOUT**: Read and write access

#### Mode Inference Rules

From dependency types:
- `FILE_READ` → INPUT
- `FILE_WRITE` → OUTPUT
- `FILE_INOUT` → INOUT

From JCL DD statements:
- `DISP=SHR` → INPUT (shared read)
- `DISP=OLD` → INOUT (exclusive update)
- `DISP=NEW` → OUTPUT (create new)
- `DISP=MOD` → OUTPUT (append)

Default: INOUT (most conservative)

## API Reference

### Main Methods

#### `infer_all_operations(programs: List[str]) -> Dict`

Infer both database and dataset operations.

**Parameters:**
- `programs`: List of program names to analyze

**Returns:**
```python
{
    'databases': [
        {
            'type': 'DB2',
            'operation': 'SELECT',
            'target': 'EMPLOYEE',
            'program': 'PAYROLL1'
        }
    ],
    'datasets': [
        {
            'name': 'EMPLOYEE.MASTER',
            'mode': 'INPUT',
            'programs': ['PAYROLL1']
        }
    ]
}
```

#### `infer_database_operations(programs: List[str]) -> List[Dict]`

Infer only database operations.

**Returns:**
```python
[
    {
        'type': 'SQL',
        'operation': 'SELECT',
        'target': 'CUSTOMER',
        'program': 'BILLING1'
    }
]
```

#### `infer_dataset_operations(programs: List[str]) -> List[Dict]`

Infer only dataset operations.

**Returns:**
```python
[
    {
        'name': 'EMPLOYEE.MASTER',
        'mode': 'INPUT',
        'programs': ['PAYROLL1', 'BILLING1']
    }
]
```

#### `get_operation_summary(programs: List[str]) -> Dict`

Get summary statistics.

**Returns:**
```python
{
    'total_database_operations': 10,
    'unique_tables': 5,
    'total_datasets': 3,
    'unique_datasets': 3
}
```

### Helper Methods

#### `_parse_sql_operation(sql_statement: str) -> str`

Parse SQL statement to determine operation type.

**Examples:**
```python
_parse_sql_operation("SELECT * FROM CUSTOMER")  # Returns: "SELECT"
_parse_sql_operation("INSERT INTO EMPLOYEE ...")  # Returns: "INSERT"
_parse_sql_operation("UPDATE PAYROLL SET ...")  # Returns: "UPDATE"
```

#### `_extract_table_from_sql(sql_statement: str) -> Optional[str]`

Extract table name from SQL statement.

**Examples:**
```python
_extract_table_from_sql("SELECT * FROM CUSTOMER")  # Returns: "CUSTOMER"
_extract_table_from_sql("INSERT INTO EMPLOYEE ...")  # Returns: "EMPLOYEE"
```

#### `_infer_dataset_mode(dependency_type: str, target_name: str) -> str`

Infer dataset access mode.

**Examples:**
```python
_infer_dataset_mode("FILE_READ", "EMPLOYEE.MASTER")  # Returns: "INPUT"
_infer_dataset_mode("JCL_DD", "DATA DISP=SHR")  # Returns: "INPUT"
_infer_dataset_mode("JCL_DD", "DATA DISP=NEW")  # Returns: "OUTPUT"
```

## Usage Examples

### Example 1: Analyze Single Program

```python
inferencer = DataOperationInferencer(db_connection)

# Get all operations for PAYROLL1
operations = inferencer.infer_all_operations(["PAYROLL1"])

# Print database operations
print("Database Operations:")
for op in operations['databases']:
    print(f"  {op['operation']} on {op['target']} ({op['type']})")

# Print dataset operations
print("\nDataset Operations:")
for op in operations['datasets']:
    print(f"  {op['name']} ({op['mode']})")
```

### Example 2: Analyze Multiple Programs

```python
programs = ["PAYROLL1", "BILLING1", "CUSTMGR"]
operations = inferencer.infer_all_operations(programs)

# Group by operation type
by_operation = {}
for op in operations['databases']:
    op_type = op['operation']
    if op_type not in by_operation:
        by_operation[op_type] = []
    by_operation[op_type].append(op)

# Print summary
for op_type, ops in by_operation.items():
    print(f"{op_type}: {len(ops)} operations")
```

### Example 3: Find Shared Datasets

```python
operations = inferencer.infer_dataset_operations(all_programs)

# Find datasets accessed by multiple programs
shared_datasets = [
    op for op in operations 
    if len(op['programs']) > 1
]

print("Shared Datasets:")
for ds in shared_datasets:
    print(f"  {ds['name']}: {', '.join(ds['programs'])}")
```

### Example 4: Analyze CICS Operations

```python
# Get only CICS programs
cics_programs = ["CUSTMGR", "ORDERMGR", "INVMGR"]
operations = inferencer.infer_database_operations(cics_programs)

# Filter VSAM operations
vsam_ops = [op for op in operations if op['type'] == 'VSAM']

print("VSAM File Operations:")
for op in vsam_ops:
    print(f"  {op['program']}: {op['operation']} {op['target']}")
```

### Example 5: Generate Operation Report

```python
def generate_operation_report(programs):
    inferencer = DataOperationInferencer(db_connection)
    operations = inferencer.infer_all_operations(programs)
    summary = inferencer.get_operation_summary(programs)
    
    print("=" * 80)
    print("Data Operation Report")
    print("=" * 80)
    print(f"\nPrograms Analyzed: {len(programs)}")
    print(f"Total Database Operations: {summary['total_database_operations']}")
    print(f"Unique Tables/Files: {summary['unique_tables']}")
    print(f"Total Datasets: {summary['total_datasets']}")
    print(f"Unique Datasets: {summary['unique_datasets']}")
    
    print("\nDatabase Operations by Type:")
    db_by_type = {}
    for op in operations['databases']:
        db_type = op['type']
        db_by_type[db_type] = db_by_type.get(db_type, 0) + 1
    
    for db_type, count in sorted(db_by_type.items()):
        print(f"  {db_type}: {count}")
    
    print("\nDataset Operations by Mode:")
    ds_by_mode = {}
    for op in operations['datasets']:
        mode = op['mode']
        ds_by_mode[mode] = ds_by_mode.get(mode, 0) + 1
    
    for mode, count in sorted(ds_by_mode.items()):
        print(f"  {mode}: {count}")

# Usage
generate_operation_report(["PAYROLL1", "BILLING1", "CUSTMGR"])
```

## Integration with Migration Flow Export

### In MigrationFlowBuilder

```python
from tools.legacy_analyzer.migration import DataOperationInferencer

class MigrationFlowBuilder:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.inferencer = DataOperationInferencer(db_connection)
    
    def build_flow(self, entry_point, programs):
        # ... other flow building logic ...
        
        # Infer data operations
        operations = self.inferencer.infer_all_operations(programs)
        
        # Write to flow_data_operations table
        self._write_data_operations(flow_id, operations)
        
        return flow_id
```

### Writing to Database

```python
def write_data_operations(flow_id, operations):
    # Write database operations
    for op in operations['databases']:
        cursor.execute("""
            INSERT INTO flow_data_operations 
            (flow_id, operation_category, operation_type, db_type, target, program)
            VALUES (?, 'DATABASE', ?, ?, ?, ?)
        """, (flow_id, op['operation'], op['type'], op['target'], op['program']))
    
    # Write dataset operations
    for op in operations['datasets']:
        for program in op['programs']:
            cursor.execute("""
                INSERT INTO flow_data_operations 
                (flow_id, operation_category, operation_type, target, program, mode)
                VALUES (?, 'DATASET', 'ACCESS', ?, ?, ?)
            """, (flow_id, op['name'], program, op['mode']))
```

## Best Practices

### 1. Batch Processing

Process multiple programs at once for better performance:

```python
# Good: Process all programs in one call
operations = inferencer.infer_all_operations(all_programs)

# Avoid: Processing one at a time
for program in all_programs:
    operations = inferencer.infer_all_operations([program])
```

### 2. Error Handling

Always handle cases where no operations are found:

```python
operations = inferencer.infer_all_operations(programs)

if not operations['databases'] and not operations['datasets']:
    print("No data operations found")
else:
    # Process operations
    pass
```

### 3. Dataset Consolidation

The inferencer automatically consolidates datasets accessed by multiple programs:

```python
# If PROG1 reads and PROG2 writes the same dataset,
# you'll get one dataset operation with mode=INOUT and both programs listed
operations = inferencer.infer_dataset_operations(["PROG1", "PROG2"])
```

### 4. SQL Parsing Limitations

Be aware of SQL parsing limitations:

```python
# Works well:
"SELECT * FROM CUSTOMER"  # ✓ Extracts CUSTOMER
"INSERT INTO EMPLOYEE VALUES (...)"  # ✓ Extracts EMPLOYEE

# May not work:
"SELECT * FROM SCHEMA.TABLE"  # May extract SCHEMA or SCHEMA.TABLE
"SELECT * FROM TABLE1 JOIN TABLE2"  # Only extracts first table
```

### 5. Mode Inference

When in doubt, the inferencer uses conservative defaults:

```python
# If mode cannot be determined, defaults to INOUT
# This is safer than assuming INPUT or OUTPUT
```

## Troubleshooting

### No Operations Found

**Problem**: `infer_all_operations()` returns empty lists

**Solutions**:
1. Check that programs exist in `artifact_dependencies` table
2. Verify dependency types are correct (EXEC_SQL, CICS_READ, etc.)
3. Check that target_artifact_type is set correctly (TABLE, FILE, DATASET)

### Incorrect Operation Types

**Problem**: Operations have wrong type (e.g., SELECT instead of INSERT)

**Solutions**:
1. Check SQL statement in target_artifact_name
2. Verify dependency_type is correct
3. Review SQL parsing logic for edge cases

### Missing Datasets

**Problem**: Some datasets are not detected

**Solutions**:
1. Check that target_artifact_type = 'DATASET'
2. Verify dependency_type includes file operations
3. Check for DD: or DDNAME: prefixes that need stripping

## Performance Considerations

### Database Queries

The inferencer uses efficient SQL queries with:
- IN clauses for multiple programs
- DISTINCT to avoid duplicates
- Indexed columns for fast lookups

### Memory Usage

For large program lists:
- Operations are processed in batches
- Results are consolidated to reduce memory
- Duplicate datasets are merged

### Optimization Tips

1. **Use indexes**: Ensure `artifact_dependencies` table has indexes on:
   - `source_artifact_name`
   - `dependency_type`
   - `target_artifact_type`

2. **Batch operations**: Process multiple programs at once

3. **Cache results**: Cache operation results for frequently analyzed programs

## See Also

- [Migration Flow Export Design](../../../.kiro/specs/migration-flow-export/design.md)
- [Requirements Document](../../../.kiro/specs/migration-flow-export/requirements.md)
- [Task 6 Completion Report](TASK_6_COMPLETE.md)
- [Demo Script](demo_data_operation_inference.py)
