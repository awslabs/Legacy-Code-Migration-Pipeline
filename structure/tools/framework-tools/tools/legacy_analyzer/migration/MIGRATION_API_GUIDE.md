# Migration Flow Export API Guide

## Overview

The Migration Flow Export API provides Python methods to build and export migration-focused flow data. This API is part of the `LegacyAnalyzerAPI` class and provides a high-level interface for working with migration flows.

## Key Concepts

### Migration Flows

A **migration flow** represents a complete execution path starting from an entry point program, including:
- **Scope**: Programs, copybooks, and datasets within the migration boundary
- **Interfaces**: Inbound and outbound boundary crossing points
- **Data Operations**: Database and dataset operations
- **Complexity**: Aggregate complexity metrics
- **Dependencies**: Flow-to-flow dependencies

### Entry Points

An **entry point** is a program that can be invoked directly from outside the application. A single program can be an entry point with multiple invocation types:
- JCL execution
- CICS transaction
- CICS program definition (CSD)
- BMS screen invocation
- External call

## API Methods

### build_migration_flows()

Build migration flows for all entry points in the database.

**Signature:**
```python
def build_migration_flows(
    self,
    external_config_path: Optional[str] = None
) -> List[str]
```

**Parameters:**
- `external_config_path` (str, optional): Path to external configuration YAML file for defining external programs and callers

**Returns:**
- List of flow IDs that were built

**Raises:**
- `FileNotFoundError`: If external_config_path is provided but file doesn't exist
- `ValueError`: If database is not properly initialized
- `Exception`: If flow building fails

**Example:**
```python
from tools.legacy_analyzer import LegacyAnalyzerAPI

# Initialize API
api = LegacyAnalyzerAPI("analyzer.db")

# Build all migration flows
flow_ids = api.build_migration_flows()
print(f"Built {len(flow_ids)} migration flows")

# With external configuration
flow_ids = api.build_migration_flows(
    external_config_path="external_config.yaml"
)
```

**What it does:**
1. Identifies all entry point programs
2. For each entry point:
   - Generates a unique flow ID
   - Analyzes program flow
   - Identifies scope (programs, copybooks, datasets)
   - Identifies interfaces (inbound/outbound)
   - Extracts data operations
   - Calculates complexity metrics
   - Identifies flow dependencies
3. Writes all data to migration_flows tables
4. Returns list of flow IDs

**Database Tables Created:**
- `migration_flows`: Flow metadata
- `flow_entry_types`: Entry point types and callers
- `flow_scope`: Scope artifacts
- `flow_interfaces`: Interfaces
- `flow_data_operations`: Data operations
- `flow_dependencies`: Flow dependencies

### export_migration_flows()

Export migration flows to JSON format.

**Signature:**
```python
def export_migration_flows(
    self,
    output_file: str,
    flow_ids: Optional[List[str]] = None,
    min_complexity: Optional[str] = None,
    business_domain: Optional[str] = None,
    entry_type: Optional[str] = None,
    include_priority: bool = True,
    include_business_domain: bool = True
) -> Dict[str, List[Dict]]
```

**Parameters:**
- `output_file` (str, required): Path to write JSON output
- `flow_ids` (List[str], optional): List of specific flow IDs to export (None = all)
- `min_complexity` (str, optional): Minimum complexity tier ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')
- `business_domain` (str, optional): Filter by business domain
- `entry_type` (str, optional): Filter by entry point type ('JCL', 'CICS_TRANSACTION', etc.)
- `include_priority` (bool): Include priority field in output (default True)
- `include_business_domain` (bool): Include businessDomain field in output (default True)

**Returns:**
- Dictionary with 'flows' key containing list of flow objects

**Raises:**
- `ValueError`: If database is not initialized or invalid parameters provided
- `FileNotFoundError`: If output directory doesn't exist
- `Exception`: If export fails

**Examples:**

**Export all flows:**
```python
api = LegacyAnalyzerAPI("analyzer.db")

result = api.export_migration_flows("Business_Flows.json")
print(f"Exported {len(result['flows'])} flows")
```

**Export specific flows:**
```python
result = api.export_migration_flows(
    output_file="payroll_flows.json",
    flow_ids=["FLOW_PAYROLL1", "FLOW_PAYCALC"]
)
```

**Export with complexity filter:**
```python
result = api.export_migration_flows(
    output_file="high_complexity.json",
    min_complexity="HIGH"
)
```

**Export with multiple filters:**
```python
result = api.export_migration_flows(
    output_file="finance_high_complexity.json",
    min_complexity="HIGH",
    business_domain="Finance",
    entry_type="JCL"
)
```

## Complete Workflow Example

### Basic Workflow

```python
from tools.legacy_analyzer import LegacyAnalyzerAPI

# 1. Initialize API with database
api = LegacyAnalyzerAPI("analyzer.db")

# 2. Build migration flows
print("Building migration flows...")
flow_ids = api.build_migration_flows()
print(f"✓ Built {len(flow_ids)} flows")

# 3. Export all flows
print("Exporting flows...")
result = api.export_migration_flows("Business_Flows.json")
print(f"✓ Exported {len(result['flows'])} flows")

# 4. Close API
api.close()
```

### Advanced Workflow with External Configuration

```python
from tools.legacy_analyzer import LegacyAnalyzerAPI

# Initialize API
api = LegacyAnalyzerAPI("analyzer.db")

try:
    # Build flows with external configuration
    flow_ids = api.build_migration_flows(
        external_config_path="config/external_programs.yaml"
    )
    print(f"Built {len(flow_ids)} flows")
    
    # Export high complexity flows
    high_complexity = api.export_migration_flows(
        output_file="high_complexity_flows.json",
        min_complexity="HIGH"
    )
    print(f"Exported {len(high_complexity['flows'])} high complexity flows")
    
    # Export finance flows
    finance_flows = api.export_migration_flows(
        output_file="finance_flows.json",
        business_domain="Finance"
    )
    print(f"Exported {len(finance_flows['flows'])} finance flows")
    
    # Export specific flows
    critical_flows = api.export_migration_flows(
        output_file="critical_flows.json",
        flow_ids=["FLOW_PAYROLL1", "FLOW_BILLING1", "FLOW_ACCT1"]
    )
    print(f"Exported {len(critical_flows['flows'])} critical flows")
    
finally:
    api.close()
```

### Context Manager Usage

```python
from tools.legacy_analyzer import LegacyAnalyzerAPI

# Use context manager for automatic cleanup
with LegacyAnalyzerAPI("analyzer.db") as api:
    # Build flows
    flow_ids = api.build_migration_flows()
    
    # Export flows
    result = api.export_migration_flows("Business_Flows.json")
    
    print(f"Exported {len(result['flows'])} flows")
# Database connection automatically closed
```

## External Configuration

External configuration allows you to define:
- **External programs**: Programs outside the migration boundary
- **External callers**: Systems that call into your flows

### Configuration File Format

Create a YAML file (e.g., `external_config.yaml`):

```yaml
# External programs (excluded from flow scope)
external_programs:
  # Utility patterns
  - pattern: "UTIL*"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  - pattern: "COMMON*"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  # Specific external programs
  - name: "DBUTIL"
    type: "DATABASE_UTILITY"
    scope: "EXTERNAL"
  
  - name: "LOGGER"
    type: "LOGGING"
    scope: "EXTERNAL"

# External callers (create inbound interfaces)
external_callers:
  - caller: "EXTERNAL_SYSTEM_A"
    calls:
      - target: "PAYCALC"
        type: "PROGRAM_CALL"
        metadata:
          system: "EXTERNAL_SYSTEM_A"
          description: "Legacy batch system"
  
  - caller: "LEGACY_BILLING"
    calls:
      - target: "BILLING1"
        type: "CICS_LINK"
        metadata:
          system: "LEGACY_BILLING"
```

### Using External Configuration

```python
api = LegacyAnalyzerAPI("analyzer.db")

# Build flows with external configuration
flow_ids = api.build_migration_flows(
    external_config_path="external_config.yaml"
)
```

## Output Format

The exported JSON follows this structure:

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
                "metadata": {
                  "jclName": "PAYROLL01",
                  "jobName": "PAYJOB"
                }
              }
            ]
          },
          {
            "type": "CICS_TRANSACTION",
            "callers": [
              {
                "source": "PAY1",
                "metadata": {
                  "transactionId": "PAY1"
                }
              }
            ]
          }
        ],
        "primaryType": "JCL"
      },
      "scope": {
        "programs": ["PAYROLL1", "PAYCALC", "PAYDB"],
        "copybooks": ["PAYCOM", "EMPDATA"],
        "datasets": ["EMPLOYEE.MASTER", "PAYROLL.TRANS"]
      },
      "interfaces": {
        "inbound": [],
        "outbound": [
          {
            "type": "PROGRAM_CALL",
            "source": "PAYDB",
            "target": "DBUTIL",
            "external": true
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
      "dependencies": {
        "requiredFlows": [],
        "dependentFlows": ["FLOW_PAYREPORT"]
      }
    }
  ]
}
```

## Error Handling

### Common Errors

**Database not initialized:**
```python
try:
    api = LegacyAnalyzerAPI("nonexistent.db")
    flow_ids = api.build_migration_flows()
except ValueError as e:
    print(f"Error: {e}")
```

**External config file not found:**
```python
try:
    flow_ids = api.build_migration_flows(
        external_config_path="missing.yaml"
    )
except FileNotFoundError as e:
    print(f"Error: {e}")
```

**Invalid complexity tier:**
```python
try:
    result = api.export_migration_flows(
        output_file="Business_Flows.json",
        min_complexity="INVALID"
    )
except ValueError as e:
    print(f"Error: {e}")
```

**Migration flows not built:**
```python
try:
    # Trying to export without building first
    result = api.export_migration_flows("Business_Flows.json")
except ValueError as e:
    print(f"Error: {e}")
    # Solution: Run build_migration_flows() first
```

### Best Practices

1. **Always build before export:**
   ```python
   api.build_migration_flows()
   api.export_migration_flows("flows.json")
   ```

2. **Use context manager:**
   ```python
   with LegacyAnalyzerAPI("analyzer.db") as api:
       # Your code here
       pass
   # Automatic cleanup
   ```

3. **Validate external config:**
   ```python
   from pathlib import Path
   
   config_path = "external_config.yaml"
   if Path(config_path).exists():
       api.build_migration_flows(external_config_path=config_path)
   else:
       api.build_migration_flows()
   ```

4. **Check results:**
   ```python
   result = api.export_migration_flows("flows.json")
   if not result['flows']:
       print("Warning: No flows exported")
   ```

## Integration with Other API Methods

The migration flow API integrates with other LegacyAnalyzerAPI methods:

### Analyze Flow Before Building

```python
api = LegacyAnalyzerAPI("analyzer.db")

# Analyze a specific flow first
flow = api.analyze_flow("PAYROLL1")
print(f"Flow depth: {flow.depth}")
print(f"Programs: {len(flow.programs)}")

# Then build migration flows
flow_ids = api.build_migration_flows()
```

### Get Entry Points

```python
# Get entry points with metadata
entry_points = api.get_entry_points_with_metadata()

for ep in entry_points:
    print(f"{ep.program_name} ({ep.entry_type})")

# Build flows for these entry points
flow_ids = api.build_migration_flows()
```

### Analyze Complexity

```python
# Analyze complexity first
with open("PAYROLL1.cbl") as f:
    source = f.read()

metrics = api.analyze_complexity("PAYROLL1", source, "COBOL")
print(f"Complexity tier: {metrics.complexity_tier}")

# Build flows (includes complexity)
flow_ids = api.build_migration_flows()
```

## Performance Considerations

### Large Codebases

For large codebases (1000+ programs):

```python
import time

api = LegacyAnalyzerAPI("analyzer.db")

# Build flows (may take time)
start = time.time()
flow_ids = api.build_migration_flows()
elapsed = time.time() - start
print(f"Built {len(flow_ids)} flows in {elapsed:.1f} seconds")

# Export in batches
batch_size = 100
for i in range(0, len(flow_ids), batch_size):
    batch = flow_ids[i:i+batch_size]
    output = f"flows_batch_{i//batch_size + 1}.json"
    api.export_migration_flows(output, flow_ids=batch)
```

### Incremental Updates

To update only changed flows:

```python
# Get flows that need updating
cursor = api.db.conn.cursor()
cursor.execute("""
    SELECT flow_id FROM migration_flows
    WHERE updated_date < ?
""", (last_analysis_date,))

stale_flow_ids = [row[0] for row in cursor.fetchall()]

# Rebuild only stale flows
# (Note: Currently rebuilds all flows, incremental update is future enhancement)
flow_ids = api.build_migration_flows()
```

## Troubleshooting

### No flows built

**Problem:** `build_migration_flows()` returns empty list

**Solutions:**
1. Check that entry points exist:
   ```python
   entry_points = api.get_entry_points()
   print(f"Found {len(entry_points)} entry points")
   ```

2. Check that dependencies exist:
   ```python
   cursor = api.db.conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM artifact_dependencies")
   count = cursor.fetchone()[0]
   print(f"Found {count} dependencies")
   ```

### Export fails

**Problem:** `export_migration_flows()` raises exception

**Solutions:**
1. Ensure flows are built:
   ```python
   cursor = api.db.conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM migration_flows")
   count = cursor.fetchone()[0]
   if count == 0:
       api.build_migration_flows()
   ```

2. Check output directory exists:
   ```python
   from pathlib import Path
   output_path = Path("output/flows.json")
   output_path.parent.mkdir(parents=True, exist_ok=True)
   ```

## See Also

- [Flow Builder Guide](MIGRATION_FLOW_BUILDER_GUIDE.md)
- [Flow Exporter Guide](FLOW_EXPORTER_GUIDE.md)
- [External Configuration Guide](EXTERNAL_CONFIG_GUIDE.md)
- [Filtering Guide](FILTERING_GUIDE.md)
