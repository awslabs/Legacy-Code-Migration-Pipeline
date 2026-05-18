# Migration Flow Exporter Guide

## Overview

The MigrationFlowExporter exports migration flows from database to JSON format. It provides flexible querying and filtering capabilities to export flows that match specific criteria.

**New in this version:**
- **Internal Procedure Filtering**: Automatically excludes internal procedures (COBOL PERFORM targets, PL/I internal procedures) from flow scope for accurate migration analysis
- **File Metadata Enrichment**: Adds comprehensive file path metadata to programs, copybooks, and dependencies for better traceability

## Quick Start

```python
from tools.legacy_analyzer.migration import MigrationFlowExporter
import sqlite3

# Connect to database
conn = sqlite3.connect('analyzer.db')

# Create exporter with default configuration
# (filtering enabled, metadata enrichment enabled)
exporter = MigrationFlowExporter(conn)

# Export all flows
result = exporter.export_all_flows(output_file='flows.json')
print(f"Exported {len(result['flows'])} flows")
```

## Configuration Options

The exporter supports two configuration flags that control its behavior:

### filter_internal_procedures (default: True)

When enabled, excludes internal procedures from flow scope. Internal procedures are:
- COBOL PERFORM targets
- PL/I internal procedures
- Nested programs
- Internal functions

These cannot be executed independently and should not be counted as separate migration units.

### include_file_metadata (default: True)

When enabled, enriches exports with file location metadata including:
- File paths for programs and copybooks
- Line numbers (start and end) for programs
- Program types (MAIN, SUBPROGRAM, etc.)
- Programming language

### include_record_layouts (default: False)

When enabled, embeds full record layouts and BMS map definitions inline in each
copybook entry. This makes the flow JSON self-contained but significantly larger.
When disabled (default), copybooks only include `name`, `filePath`, and
`copybookType` — record layouts can be obtained by reading the copybook files
directly, and BMS screen definitions by reading the original `.bms` source files
(derivable from the BMS copybook's `filePath` by swapping `cpy-bms` → `bms` and
changing the extension to `.bms`).

### export_bms_screens (default: False)

When enabled, writes BMS screen definitions to a separate companion file
(`<output>_bms_screens.json`) alongside the flow export. Only takes effect when
`include_record_layouts=False` and an `output_file` is specified. Disabled by
default because the original `.bms` source files are already reachable via each
BMS copybook's `filePath`.

### Setting Configuration

```python
# Default configuration (recommended)
# Lean copybooks (name, filePath, copybookType only), no BMS companion file
exporter = MigrationFlowExporter(
    conn,
    filter_internal_procedures=True,
    include_file_metadata=True,
    include_record_layouts=False,
    export_bms_screens=False
)

# Inline record layouts and BMS map definitions in each copybook
exporter = MigrationFlowExporter(
    conn,
    include_record_layouts=True
)

# Lean copybooks with a separate BMS screens companion file
exporter = MigrationFlowExporter(
    conn,
    include_record_layouts=False,
    export_bms_screens=True
)

# Disable filtering (backward compatibility)
exporter = MigrationFlowExporter(
    conn,
    filter_internal_procedures=False,
    include_file_metadata=True
)

# Minimal mode (no filtering or metadata)
exporter = MigrationFlowExporter(
    conn,
    filter_internal_procedures=False,
    include_file_metadata=False
)
```

## Basic Operations

### Export All Flows

```python
# Export all flows (returns dictionary)
result = exporter.export_all_flows()

# Export all flows to file
result = exporter.export_all_flows(output_file='flows.json')
```

### Export Specific Flows

```python
# Export specific flows by ID
flow_ids = ['FLOW_PAYROLL1', 'FLOW_BILLING1', 'FLOW_ACCT1']
result = exporter.export_flows(flow_ids)

# Export to file
result = exporter.export_flows(flow_ids, output_file='selected_flows.json')
```

### Check Flow Existence

```python
# Check if a flow exists
if exporter.flow_exists('FLOW_PAYROLL1'):
    print("Flow exists")

# Get all flow IDs
flow_ids = exporter.get_flow_ids()
print(f"Found {len(flow_ids)} flows")

# Get flow count
count = exporter.get_flow_count()
print(f"Total flows: {count}")
```

## Filtering

### Filter by Complexity

Export flows with minimum complexity tier:

```python
# Export HIGH and VERY_HIGH complexity flows
result = exporter.export_all_flows(min_complexity='HIGH')

# Export MEDIUM and above
result = exporter.export_all_flows(min_complexity='MEDIUM')

# Export LOW and above (all flows)
result = exporter.export_all_flows(min_complexity='LOW')
```

**Complexity Tiers:**
- `LOW` - Simple flows (score < 25)
- `MEDIUM` - Moderate complexity (25 ≤ score < 50)
- `HIGH` - Complex flows (50 ≤ score < 75)
- `VERY_HIGH` - Very complex flows (score ≥ 75)

### Filter by Business Domain

Export flows in a specific business domain:

```python
# Export Finance domain flows
result = exporter.export_all_flows(business_domain='Finance')

# Export Operations domain flows
result = exporter.export_all_flows(business_domain='Operations')
```

### Filter by Entry Type

Export flows with specific entry point types:

```python
# Export JCL entry point flows
result = exporter.export_all_flows(entry_type='JCL')

# Export CICS transaction flows
result = exporter.export_all_flows(entry_type='CICS_TRANSACTION')

# Export CICS program flows
result = exporter.export_all_flows(entry_type='CICS_PROGRAM')
```

**Entry Types:**
- `JCL` - Invoked by JCL jobs
- `CICS_TRANSACTION` - Invoked by CICS transactions
- `CICS_PROGRAM` - Defined in CSD
- `SCREEN` - Called from BMS screens
- `BATCH` - Batch processing
- `EXTERNAL_CALL` - External system calls

### Combined Filters

Combine multiple filters:

```python
# High-complexity Finance flows
result = exporter.export_all_flows(
    min_complexity='HIGH',
    business_domain='Finance'
)

# Medium+ complexity JCL flows in Operations
result = exporter.export_all_flows(
    min_complexity='MEDIUM',
    business_domain='Operations',
    entry_type='JCL'
)
```

## JSON Output Format

The exporter produces JSON in this structure. When file metadata enrichment is enabled (default), programs and copybooks include file location information:

```json
{
  "flows": [
    {
      "flowId": "FLOW_PAYROLL1",
      "name": "Payroll Processing",
      "entryPoint": {
        "program": "PAYROLL1",
        "types": [
          {
            "type": "JCL",
            "callers": [
              {
                "source": "PAYROLL01",
                "filePath": "jcl/PAYROLL01.jcl",
                "metadata": {
                  "jclName": "PAYROLL01",
                  "jobName": "PAYJOB"
                }
              }
            ]
          }
        ],
        "primaryType": "JCL"
      },
      "scope": {
        "programs": [
          {
            "name": "PAYROLL1",
            "filePath": "src/cobol/PAYROLL1.cbl",
            "startLine": 1,
            "endLine": 450,
            "programType": "MAIN",
            "language": "COBOL"
          },
          {
            "name": "PAYCALC",
            "filePath": "src/cobol/PAYCALC.cbl",
            "startLine": 1,
            "endLine": 320,
            "programType": "SUBPROGRAM",
            "language": "COBOL"
          },
          {
            "name": "PAYDB",
            "filePath": "src/cobol/PAYDB.cbl",
            "startLine": 1,
            "endLine": 280,
            "programType": "SUBPROGRAM",
            "language": "COBOL"
          }
        ],
        "copybooks": [
          {
            "name": "PAYCOM",
            "filePath": "src/copybooks/PAYCOM.cpy",
            "copybookType": "DATA"
          },
          {
            "name": "EMPDATA",
            "filePath": "src/copybooks/EMPDATA.cpy",
            "copybookType": "DATA"
          }
        ],
        "datasets": ["EMPLOYEE.MASTER", "PAYROLL.TRANS"]
      },
      "interfaces": {
        "inbound": [
          {
            "type": "PROGRAM_CALL",
            "source": "EXTERNAL_PROG",
            "target": "PAYCALC",
            "metadata": {
              "callingProgram": "EXTERNAL_PROG"
            }
          }
        ],
        "outbound": [
          {
            "type": "PROGRAM_CALL",
            "source": "PAYDB",
            "target": "DBUTIL",
            "external": true,
            "metadata": {
              "callingProgram": "PAYDB"
            }
          }
        ]
      },
      "dataOperations": {
        "databases": [
          {
            "type": "DB2",
            "operation": "SELECT",
            "target": "EMPLOYEE_TABLE",
            "program": "PAYDB"
          }
        ],
        "datasets": [
          {
            "name": "EMPLOYEE.MASTER",
            "mode": "INPUT",
            "programs": ["PAYROLL1"]
          }
        ]
      },
      "complexity": {
        "totalPrograms": 3,
        "totalLines": 2500,
        "cyclomaticComplexity": 45,
        "compositeScore": 67.5,
        "tier": "MEDIUM"
      },
      "priority": 1,
      "businessDomain": "Finance",
      "dependencies": {
        "requiredFlows": [
          {
            "flowId": "FLOW_DATEUTIL",
            "entryProgram": "DATEUTIL",
            "filePath": "src/cobol/DATEUTIL.cbl"
          }
        ],
        "dependentFlows": [
          {
            "flowId": "FLOW_BILLING1",
            "entryProgram": "BILLING1",
            "filePath": "src/cobol/BILLING1.cbl"
          }
        ]
      },
      "invokedByJobs": ["PAYROLL01", "PAYWEEK"]
    }
  ]
}
```

### Field Descriptions

#### Program Objects (in scope.programs)

When `include_file_metadata=True` (default):
- `name`: Program name
- `filePath`: Path to source file
- `startLine`: Starting line number in file
- `endLine`: Ending line number in file
- `programType`: Program type (MAIN, SUBPROGRAM, ENTRY_POINT, CSECT, ROUTINE)
- `language`: Programming language (COBOL, PLI, ASSEMBLER, etc.)

When `include_file_metadata=False`:
- `name`: Program name only

#### Copybook Objects (in scope.copybooks)

When `include_file_metadata=True` (default):
- `name`: Copybook name
- `filePath`: Path to copybook file
- `copybookType`: `"DATA"` for regular data copybooks, `"BMS"` for BMS-generated copybooks (classified by whether `filePath` contains a `cpy-bms` directory segment)

When `include_record_layouts=True` (not default):
- `recordLayout`: Parsed field hierarchy from the copybook content (level numbers, PIC clauses, USAGE, OCCURS, REDEFINES)
- `mapDefinition`: For BMS copybooks only, the parsed BMS screen definition (mapset, maps, fields with position/length/attributes)
- `parseError`: Present only when parsing fails

When `include_file_metadata=False`:
- `name`: Copybook name only
- `copybookType`: `"DATA"` (default when no file path available)

#### Dependency Objects (in dependencies)

When `include_file_metadata=True` (default):
- `flowId`: Flow identifier
- `entryProgram`: Entry program name
- `filePath`: Path to entry program source file

When `include_file_metadata=False`:
- `flowId`: Flow identifier
- `entryProgram`: Entry program name

#### Entry Point Callers

When `include_file_metadata=True` (default):
- `source`: Caller name
- `filePath`: Path to caller source file (when available)
- `metadata`: Additional caller metadata

### Internal Procedure Filtering

When `filter_internal_procedures=True` (default), the scope.programs list excludes:
- COBOL PERFORM targets (program_type = 'PROCEDURE')
- PL/I internal procedures (program_type = 'PROCEDURE')
- Nested programs (program_type = 'NESTED')
- Internal functions (program_type = 'FUNCTION')

Only standalone programs that can be executed independently are included:
- Main programs (program_type = 'MAIN')
- Subprograms (program_type = 'SUBPROGRAM')
- Entry points (program_type = 'ENTRY_POINT')
- Control sections (program_type = 'CSECT')
- Routines (program_type = 'ROUTINE')

## Internal Procedure Filtering

### Overview

Internal procedures are code constructs that cannot be executed independently:
- COBOL PERFORM targets (sections or paragraphs called via PERFORM)
- PL/I internal procedures
- Nested programs
- Internal functions

These should not be counted as separate migration units because they are part of their containing program.

### How It Works

When `filter_internal_procedures=True` (default), the exporter:
1. Queries the `program_file_mapping` table for program type information
2. Excludes programs with types: PROCEDURE, NESTED, FUNCTION
3. Includes only standalone programs: MAIN, SUBPROGRAM, ENTRY_POINT, CSECT, ROUTINE
4. Logs the number of filtered procedures for each flow

### Example

```python
# With filtering enabled (default)
exporter = MigrationFlowExporter(conn, filter_internal_procedures=True)
result = exporter.export_all_flows()

# Flow with 10 programs in database:
# - 7 standalone programs (MAIN, SUBPROGRAM)
# - 3 internal procedures (PROCEDURE)
# Result: scope.programs contains 7 programs
# Log: "Flow FLOW_PAYROLL1: Filtered 3 internal procedure(s) from scope"
```

### Backward Compatibility

To maintain backward compatibility with existing workflows:

```python
# Disable filtering to include all programs
exporter = MigrationFlowExporter(conn, filter_internal_procedures=False)
result = exporter.export_all_flows()

# Result: scope.programs contains all 10 programs (including internal procedures)
```

### Graceful Degradation

If the `program_file_mapping` table doesn't exist:
- Filtering is automatically disabled
- All programs are included in scope
- A warning is logged
- Export continues with current behavior

## File Metadata Enrichment

### Overview

File metadata enrichment adds comprehensive location information to exported flows:
- **Programs**: File path, line numbers, program type, language
- **Copybooks**: File path
- **Dependencies**: File path for entry programs
- **Entry point callers**: File path for caller programs

This enables:
- Quick navigation to source code
- Understanding program organization
- Traceability for migration planning
- Integration with source control systems

### How It Works

When `include_file_metadata=True` (default), the exporter:
1. Loads all program metadata from `program_file_mapping` table into cache on initialization
2. Enriches program objects with file location data
3. Queries `inventory` table for copybook file paths
4. Adds file paths to dependency objects
5. Handles missing metadata gracefully (omits fields rather than including null)

### Example

```python
# With metadata enrichment enabled (default)
exporter = MigrationFlowExporter(conn, include_file_metadata=True)
result = exporter.export_all_flows()

# Program object in result:
{
    "name": "PAYROLL1",
    "filePath": "src/cobol/PAYROLL1.cbl",
    "startLine": 1,
    "endLine": 450,
    "programType": "MAIN",
    "language": "COBOL"
}

# Copybook object in result:
{
    "name": "PAYCOM",
    "filePath": "src/copybooks/PAYCOM.cpy",
    "copybookType": "DATA"
}

# Dependency object in result:
{
    "flowId": "FLOW_DATEUTIL",
    "entryProgram": "DATEUTIL",
    "filePath": "src/cobol/DATEUTIL.cbl"
}
```

### Without Metadata Enrichment

```python
# Disable metadata enrichment
exporter = MigrationFlowExporter(conn, include_file_metadata=False)
result = exporter.export_all_flows()

# Program object in result (name only):
{
    "name": "PAYROLL1"
}

# Copybook object in result (name and type only):
{
    "name": "PAYCOM",
    "copybookType": "DATA"
}

# Dependency object in result (no file path):
{
    "flowId": "FLOW_DATEUTIL",
    "entryProgram": "DATEUTIL"
}
```

### Graceful Degradation

If metadata is unavailable for specific programs:
- The program is still included in the export
- File metadata fields are omitted (not null)
- A warning is logged listing programs without metadata
- Export continues successfully

Example log output:
```
WARNING: Flow FLOW_PAYROLL1: 2 program(s) have no file mapping: LEGACY01, OLDPROG
WARNING: Flow FLOW_PAYROLL1: 1 copybook(s) have no file path: OLDCOPY
```

### Performance Optimization

The exporter uses caching for optimal performance:
- All program metadata is loaded once on initialization
- Metadata lookups use in-memory cache (no repeated database queries)
- Batch queries with JOINs minimize database round-trips

## Advanced Usage

### Query Individual Components

```python
# Query entry types for a flow
entry_types = exporter._query_entry_types('FLOW_PAYROLL1')
for entry_type in entry_types:
    print(f"Type: {entry_type['type']}")
    for caller in entry_type['callers']:
        print(f"  Caller: {caller['source']}")

# Query scope
scope = exporter._query_scope('FLOW_PAYROLL1')
print(f"Programs: {scope['programs']}")
print(f"Copybooks: {scope['copybooks']}")
print(f"Datasets: {scope['datasets']}")

# Query interfaces
interfaces = exporter._query_interfaces('FLOW_PAYROLL1')
print(f"Inbound: {len(interfaces['inbound'])}")
print(f"Outbound: {len(interfaces['outbound'])}")

# Query data operations
data_ops = exporter._query_data_operations('FLOW_PAYROLL1')
print(f"Database ops: {len(data_ops['databases'])}")
print(f"Dataset ops: {len(data_ops['datasets'])}")

# Query dependencies
deps = exporter._query_dependencies('FLOW_PAYROLL1')
print(f"Required flows: {deps['requiredFlows']}")
print(f"Dependent flows: {deps['dependentFlows']}")
```

### Query Complete Flow

```python
# Query complete flow data
flow = exporter._query_flow('FLOW_PAYROLL1')

if flow:
    print(f"Flow ID: {flow['flowId']}")
    print(f"Name: {flow['name']}")
    print(f"Entry Program: {flow['entryPoint']['program']}")
    print(f"Complexity: {flow['complexity']['tier']}")
    print(f"Programs: {len(flow['scope']['programs'])}")
else:
    print("Flow not found")
```

## Error Handling

The exporter handles errors gracefully:

```python
# Export with non-existent flows
flow_ids = ['FLOW_PAYROLL1', 'FLOW_NONEXISTENT', 'FLOW_BILLING1']
result = exporter.export_flows(flow_ids)

# Only existing flows are exported
# Warning is printed for missing flows
print(f"Exported {len(result['flows'])} flows")
```

## Performance Tips

1. **Use Filters**: Filter at database level for better performance
   ```python
   # Good: Filter in database
   result = exporter.export_all_flows(min_complexity='HIGH')
   
   # Less efficient: Filter after export
   result = exporter.export_all_flows()
   high_flows = [f for f in result['flows'] if f['complexity']['tier'] == 'HIGH']
   ```

2. **Export Specific Flows**: Export only needed flows
   ```python
   # Export only flows you need
   result = exporter.export_flows(['FLOW_PAYROLL1', 'FLOW_BILLING1'])
   ```

3. **Use File Output**: Write directly to file for large exports
   ```python
   # Write to file (more memory efficient)
   exporter.export_all_flows(output_file='flows.json')
   ```

## Common Use Cases

### Migration Planning

Export high-complexity flows for migration planning:

```python
# Get high-complexity flows
result = exporter.export_all_flows(
    min_complexity='HIGH',
    output_file='high_complexity_flows.json'
)

# Analyze for migration effort
for flow in result['flows']:
    print(f"{flow['flowId']}: {flow['complexity']['totalLines']} LOC")
```

### Service Boundary Definition

Export flows by business domain:

```python
# Export Finance domain flows
finance_flows = exporter.export_all_flows(
    business_domain='Finance',
    output_file='finance_flows.json'
)

# Export Operations domain flows
ops_flows = exporter.export_all_flows(
    business_domain='Operations',
    output_file='operations_flows.json'
)
```

### Dependency Analysis

Export flows with dependencies:

```python
# Export all flows
result = exporter.export_all_flows()

# Analyze dependencies
for flow in result['flows']:
    flow_id = flow['flowId']
    required = flow['dependencies']['requiredFlows']
    dependent = flow['dependencies']['dependentFlows']
    
    if required:
        print(f"{flow_id} requires: {', '.join(required)}")
    if dependent:
        print(f"{flow_id} is required by: {', '.join(dependent)}")
```

### Interface Contract Definition

Export flows to identify interfaces:

```python
# Export flows
result = exporter.export_all_flows()

# Analyze interfaces
for flow in result['flows']:
    flow_id = flow['flowId']
    inbound = flow['interfaces']['inbound']
    outbound = flow['interfaces']['outbound']
    
    print(f"\n{flow_id}:")
    print(f"  Inbound interfaces: {len(inbound)}")
    for iface in inbound:
        print(f"    {iface['source']} -> {iface['target']}")
    
    print(f"  Outbound interfaces: {len(outbound)}")
    for iface in outbound:
        print(f"    {iface['source']} -> {iface['target']}")
```

### Accurate Program Counting

Use filtering to get accurate program counts for migration sizing:

```python
# Export with filtering enabled (default)
exporter = MigrationFlowExporter(conn, filter_internal_procedures=True)
result = exporter.export_all_flows()

# Count standalone programs only (accurate for migration)
for flow in result['flows']:
    flow_id = flow['flowId']
    programs = flow['scope']['programs']
    
    # All programs in this list are standalone (can be migrated independently)
    print(f"{flow_id}: {len(programs)} standalone programs")
    
    # Calculate migration effort based on lines of code
    if programs and isinstance(programs[0], dict):
        total_lines = sum(
            p.get('endLine', 0) - p.get('startLine', 0) + 1 
            for p in programs
        )
        print(f"  Total LOC: {total_lines}")
```

### Source Code Navigation

Use file metadata to navigate to source code:

```python
# Export with metadata enrichment enabled (default)
exporter = MigrationFlowExporter(conn, include_file_metadata=True)
result = exporter.export_all_flows()

# Generate source code index
for flow in result['flows']:
    flow_id = flow['flowId']
    programs = flow['scope']['programs']
    
    print(f"\n{flow_id} Source Files:")
    for program in programs:
        if isinstance(program, dict) and 'filePath' in program:
            name = program['name']
            path = program['filePath']
            start = program.get('startLine', '?')
            end = program.get('endLine', '?')
            lang = program.get('language', 'UNKNOWN')
            
            print(f"  {name} ({lang}): {path} [lines {start}-{end}]")
```

### Dependency Traceability

Use file metadata in dependencies for complete traceability:

```python
# Export with metadata
exporter = MigrationFlowExporter(conn, include_file_metadata=True)
result = exporter.export_all_flows()

# Analyze dependencies with file paths
for flow in result['flows']:
    flow_id = flow['flowId']
    required = flow['dependencies']['requiredFlows']
    
    if required:
        print(f"\n{flow_id} depends on:")
        for dep in required:
            dep_flow = dep['flowId']
            entry_prog = dep['entryProgram']
            file_path = dep.get('filePath', 'unknown')
            
            print(f"  {dep_flow} ({entry_prog})")
            print(f"    Source: {file_path}")
```

### Migration Package Documentation

Generate comprehensive migration package documentation:

```python
# Export with all features enabled
exporter = MigrationFlowExporter(
    conn,
    filter_internal_procedures=True,
    include_file_metadata=True
)
result = exporter.export_all_flows(
    min_complexity='MEDIUM',
    output_file='migration_package.json'
)

# Generate markdown documentation
for flow in result['flows']:
    flow_id = flow['flowId']
    name = flow['name']
    programs = flow['scope']['programs']
    copybooks = flow['scope']['copybooks']
    
    print(f"\n## {name} ({flow_id})")
    print(f"\n### Programs ({len(programs)})")
    
    for program in programs:
        if isinstance(program, dict):
            prog_name = program['name']
            prog_type = program.get('programType', 'UNKNOWN')
            file_path = program.get('filePath', 'unknown')
            language = program.get('language', 'UNKNOWN')
            
            print(f"- **{prog_name}** ({prog_type}, {language})")
            print(f"  - Source: `{file_path}`")
    
    print(f"\n### Copybooks ({len(copybooks)})")
    for copybook in copybooks:
        if isinstance(copybook, dict):
            cb_name = copybook['name']
            cb_path = copybook.get('filePath', 'unknown')
            cb_type = copybook.get('copybookType', 'DATA')
            print(f"- **{cb_name}** ({cb_type}): `{cb_path}`")
```

## Integration with Workflow

Typical workflow:

1. **Analyze Code**: Use StaticCodeAnalyzer to analyze source code
2. **Build Flows**: Use MigrationFlowBuilder to build flows
3. **Export Flows**: Use MigrationFlowExporter to export flows with filtering and metadata
4. **Review JSON**: Review exported JSON for migration planning

```python
from tools.legacy_analyzer import StaticCodeAnalyzer
from tools.legacy_analyzer.migration import (
    MigrationFlowBuilder,
    MigrationFlowExporter
)

# 1. Analyze code
analyzer = StaticCodeAnalyzer(db_path='analyzer.db')
analyzer.analyze_directory('./source-code')

# 2. Build flows
builder = MigrationFlowBuilder(analyzer.db)
flow_ids = builder.build_all_flows()
print(f"Built {len(flow_ids)} flows")

# 3. Export flows with filtering and metadata (default configuration)
exporter = MigrationFlowExporter(
    analyzer.db,
    filter_internal_procedures=True,  # Exclude internal procedures
    include_file_metadata=True,        # Add file paths and metadata
    include_record_layouts=False,      # Lean copybooks (name, path, type)
    export_bms_screens=False           # No BMS companion file
)
result = exporter.export_all_flows(output_file='flows.json')
print(f"Exported {len(result['flows'])} flows")

# 4. Review JSON
# Open flows.json in editor or use for migration planning
# Each flow now includes:
# - Only standalone programs (internal procedures filtered out)
# - File paths for all programs and copybooks
# - Copybook classification (DATA vs BMS)
# - Line numbers and program types
# - Resolved data operation types (CICS_READ, CICS_WRITE, INPUT, OUTPUT, etc.)
# - Complete traceability for dependencies
# - BMS screen source files reachable via BMS copybook filePath
```

## Troubleshooting

### No Flows Exported

```python
# Check if flows exist
count = exporter.get_flow_count()
if count == 0:
    print("No flows in database. Run MigrationFlowBuilder first.")
```

### Missing Flow Data

```python
# Check if flow exists
if not exporter.flow_exists('FLOW_PAYROLL1'):
    print("Flow not found. Check flow ID.")

# List all flow IDs
flow_ids = exporter.get_flow_ids()
print(f"Available flows: {', '.join(flow_ids)}")
```

### Empty Filter Results

```python
# Check filter criteria
result = exporter.export_all_flows(min_complexity='VERY_HIGH')
if len(result['flows']) == 0:
    print("No flows match filter. Try lower complexity tier.")
    
    # Try with lower tier
    result = exporter.export_all_flows(min_complexity='HIGH')
    print(f"Found {len(result['flows'])} HIGH+ complexity flows")
```

### Missing File Metadata

If programs or copybooks are missing file metadata:

```python
# Check if program_file_mapping table exists
import sqlite3
conn = sqlite3.connect('analyzer.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='program_file_mapping'
""")

if not cursor.fetchone():
    print("program_file_mapping table not found.")
    print("File metadata enrichment will be disabled.")
    print("Run StaticCodeAnalyzer with file mapping enabled.")
else:
    # Check if table has data
    cursor.execute("SELECT COUNT(*) FROM program_file_mapping")
    count = cursor.fetchone()[0]
    print(f"Found {count} program mappings")
    
    if count == 0:
        print("program_file_mapping table is empty.")
        print("Analyze source code to populate file mappings.")
```

### Programs Filtered Unexpectedly

If you expect more programs in scope:

```python
# Check if filtering is enabled
exporter = MigrationFlowExporter(conn)
print(f"Filtering enabled: {exporter.config.filter_internal_procedures}")

# Disable filtering to see all programs
exporter_no_filter = MigrationFlowExporter(
    conn,
    filter_internal_procedures=False
)
result = exporter_no_filter.export_all_flows()

# Compare program counts
for flow in result['flows']:
    flow_id = flow['flowId']
    programs = flow['scope']['programs']
    print(f"{flow_id}: {len(programs)} programs (unfiltered)")
```

### Checking Program Types

To understand why programs are filtered:

```python
# Query program types directly
import sqlite3
conn = sqlite3.connect('analyzer.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT program_name, program_type
    FROM program_file_mapping
    WHERE program_name IN (
        SELECT artifact_name 
        FROM flow_scope 
        WHERE flow_id = ? AND artifact_type = 'PROGRAM'
    )
    ORDER BY program_type, program_name
""", ('FLOW_PAYROLL1',))

print("Program types in flow:")
for program_name, program_type in cursor.fetchall():
    filtered = program_type in ['PROCEDURE', 'NESTED', 'FUNCTION']
    status = "FILTERED" if filtered else "INCLUDED"
    print(f"  {program_name}: {program_type} [{status}]")
```

## See Also

- **MigrationFlowBuilder**: Build flows from analyzed code
- **MigrationFlowSchema**: Database schema for migration flows
- **StaticCodeAnalyzer**: Analyze source code
- **Flow Analysis Guide**: Understanding flow analysis
