# Migration Flow Data Models

## Overview

This document describes the data models for migration-focused flow export. These models represent the complete structure of migration flows, including entry points, scope, interfaces, data operations, complexity metrics, and dependencies.

## Task Completion

✅ **Task 2: Data Models - COMPLETED**

All subtasks completed:
- ✅ 2.1 Create MigrationFlow data model
- ✅ 2.2 Create FlowScope data model
- ✅ 2.3 Create FlowInterface data model
- ✅ 2.4 Create DataOperation data model
- ✅ 2.5 Add to_dict() methods for JSON serialization

## File Location

`tools/legacy_analyzer/models/migration_flow.py`

## Data Models

### Core Models

#### 1. MigrationFlow
The main model representing a complete migration flow.

**Fields:**
- `flow_id`: Unique identifier (e.g., "FLOW_PAYROLL1")
- `name`: Human-readable name
- `entry_point`: EntryPoint object
- `scope`: FlowScope object
- `interfaces`: FlowInterfaces object
- `data_operations`: DataOperations object
- `complexity`: FlowComplexity object
- `dependencies`: FlowDependencies object
- `priority`: Optional migration priority
- `business_domain`: Optional business domain classification
- `created_date`: Optional creation timestamp
- `updated_date`: Optional update timestamp

**Methods:**
- `to_dict()`: Convert to dictionary for JSON serialization
- `get_total_artifacts()`: Get total count of artifacts in scope
- `get_total_interfaces()`: Get total count of interfaces
- `get_total_data_operations()`: Get total count of data operations
- `has_dependencies()`: Check if flow has dependencies
- `is_high_complexity()`: Check if flow has high/very high complexity

#### 2. EntryPoint → MigrationEntryPoint
Represents the entry point of a migration flow with multiple invocation types.

**Note:** Renamed to `MigrationEntryPoint` to avoid conflict with existing `EntryPoint` class in `flow.py`.

**Fields:**
- `program`: Entry point program name
- `types`: List of EntryPointTypeInfo objects
- `primary_type`: Most common invocation type (optional)

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_type()`: Add an entry point type and caller
- `get_all_callers()`: Get all caller sources across all types
- `determine_primary_type()`: Determine the most common entry point type

**Key Concept:** A single program can be an entry point invoked in multiple ways (JCL, CICS transaction, screen, etc.). The MigrationEntryPoint model captures ALL invocation types for a single program.

#### 3. EntryPointTypeInfo
Represents a specific invocation type with its callers.

**Fields:**
- `type`: Entry point type (JCL, CICS_TRANSACTION, CICS_PROGRAM, SCREEN, etc.)
- `callers`: List of EntryPointCaller objects

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_caller()`: Add a caller to this entry point type

#### 4. EntryPointCaller
Represents a specific caller of an entry point.

**Fields:**
- `source`: Caller source (JCL name, transaction ID, screen name, etc.)
- `metadata`: Additional metadata (dict)

**Methods:**
- `to_dict()`: Convert to dictionary

### Scope Models

#### 5. FlowScope
Represents artifacts within the migration boundary.

**Fields:**
- `programs`: List of program names
- `copybooks`: List of copybook names
- `datasets`: List of dataset names

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_program()`: Add a program to scope
- `add_copybook()`: Add a copybook to scope
- `add_dataset()`: Add a dataset to scope
- `get_total_artifacts()`: Get total count of all artifacts

### Interface Models

#### 6. FlowInterface
Represents a single interface crossing the migration boundary.

**Fields:**
- `type`: Interface type (JCL, PROGRAM_CALL, CICS_LINK, etc.)
- `source`: Source artifact name
- `target`: Target artifact name
- `direction`: INBOUND or OUTBOUND
- `external`: Boolean flag (True for outbound)
- `metadata`: Additional metadata (dict)

**Methods:**
- `to_dict()`: Convert to dictionary

#### 7. FlowInterfaces
Collection of inbound and outbound interfaces.

**Fields:**
- `inbound`: List of FlowInterface objects (external → flow)
- `outbound`: List of FlowInterface objects (flow → external)

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_inbound()`: Add an inbound interface
- `add_outbound()`: Add an outbound interface

### Data Operation Models

#### 8. DatabaseOperation
Represents a database operation.

**Fields:**
- `type`: Database type (DB2, IMS, VSAM, etc.)
- `operation`: Operation type (READ, WRITE, SELECT, INSERT, etc.)
- `target`: Table/file name
- `program`: Program performing operation

**Methods:**
- `to_dict()`: Convert to dictionary

#### 9. DatasetOperation
Represents a dataset operation.

**Fields:**
- `name`: Dataset name
- `mode`: Access mode (INPUT, OUTPUT, INOUT)
- `programs`: List of programs accessing this dataset

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_program()`: Add a program that accesses this dataset

#### 10. DataOperations
Collection of database and dataset operations.

**Fields:**
- `databases`: List of DatabaseOperation objects
- `datasets`: List of DatasetOperation objects

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_database_operation()`: Add a database operation
- `add_dataset_operation()`: Add a dataset operation (merges if exists)

### Complexity Models

#### 11. FlowComplexity
Complexity metrics for a migration flow.

**Fields:**
- `total_programs`: Count of programs in flow
- `total_lines`: Sum of lines of code
- `cyclomatic_complexity`: Sum of cyclomatic complexity
- `composite_score`: Weighted composite score
- `tier`: Complexity tier (LOW, MEDIUM, HIGH, VERY_HIGH)

**Methods:**
- `to_dict()`: Convert to dictionary

### Dependency Models

#### 12. FlowDependencies
Flow-to-flow dependencies.

**Fields:**
- `required_flows`: List of flow IDs that must be migrated first
- `dependent_flows`: List of flow IDs that depend on this flow

**Methods:**
- `to_dict()`: Convert to dictionary
- `add_required_flow()`: Add a required flow dependency
- `add_dependent_flow()`: Add a dependent flow

## Enumerations

### ComplexityTier
- `LOW`: Low complexity
- `MEDIUM`: Medium complexity
- `HIGH`: High complexity
- `VERY_HIGH`: Very high complexity
- `UNKNOWN`: Unknown complexity

### EntryPointType
- `JCL`: JCL job invocation
- `CICS_TRANSACTION`: CICS transaction invocation
- `CICS_PROGRAM`: CICS program definition (CSD)
- `SCREEN`: BMS screen invocation
- `BATCH`: Batch processing
- `EXTERNAL_CALL`: External program call

### InterfaceDirection
- `INBOUND`: External → Flow
- `OUTBOUND`: Flow → External

### DataOperationCategory
- `DATABASE`: Database operation
- `DATASET`: Dataset operation

### DataOperationType
- `READ`: Read operation
- `WRITE`: Write operation
- `UPDATE`: Update operation
- `DELETE`: Delete operation
- `SELECT`: SQL SELECT
- `INSERT`: SQL INSERT
- `UNKNOWN`: Unknown operation

### DatasetMode
- `INPUT`: Input only
- `OUTPUT`: Output only
- `INOUT`: Input and output

### DatabaseType
- `DB2`: IBM DB2
- `IMS`: IBM IMS
- `IDMS`: CA IDMS
- `ADABAS`: Software AG Adabas
- `VSAM`: VSAM files
- `SQL`: Generic SQL
- `UNKNOWN`: Unknown database

## Usage Example

```python
from tools.legacy_analyzer.models import (
    MigrationFlow,
    MigrationEntryPoint,
    FlowScope,
    FlowInterfaces,
    DataOperations,
    FlowComplexity,
    FlowDependencies,
    EntryPointType,
    MigrationComplexityTier
)

# Create entry point with multiple invocation types
entry_point = MigrationEntryPoint(program="PAYROLL1")
entry_point.add_type(
    EntryPointType.JCL.value, 
    "PAYROLL01", 
    {"jclName": "PAYROLL01", "jobName": "PAYJOB"}
)
entry_point.add_type(
    EntryPointType.CICS_TRANSACTION.value,
    "PAY1",
    {"transactionId": "PAY1"}
)
entry_point.primary_type = entry_point.determine_primary_type()

# Create scope
scope = FlowScope()
scope.add_program("PAYROLL1")
scope.add_program("PAYCALC")
scope.add_copybook("PAYCOM")
scope.add_dataset("EMPLOYEE.MASTER")

# Create interfaces
interfaces = FlowInterfaces()

# Create data operations
operations = DataOperations()

# Create complexity
complexity = FlowComplexity(
    total_programs=2,
    total_lines=1500,
    cyclomatic_complexity=30,
    composite_score=45.0,
    tier=ComplexityTier.MEDIUM.value
)

# Create dependencies
dependencies = FlowDependencies()

# Create migration flow
flow = MigrationFlow(
    flow_id="FLOW_PAYROLL1",
    name="Payroll Processing",
    entry_point=entry_point,
    scope=scope,
    interfaces=interfaces,
    data_operations=operations,
    complexity=complexity,
    dependencies=dependencies,
    priority=1,
    business_domain="Finance"
)

# Serialize to JSON
json_data = flow.to_dict()
```

## JSON Output Format

The `to_dict()` methods produce JSON-compatible dictionaries that match the migration flow export format:

```json
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
    "programs": ["PAYROLL1", "PAYCALC"],
    "copybooks": ["PAYCOM"],
    "datasets": ["EMPLOYEE.MASTER"]
  },
  "interfaces": {
    "inbound": [],
    "outbound": []
  },
  "dataOperations": {
    "databases": [],
    "datasets": []
  },
  "complexity": {
    "totalPrograms": 2,
    "totalLines": 1500,
    "cyclomaticComplexity": 30,
    "compositeScore": 45.0,
    "tier": "MEDIUM"
  },
  "dependencies": {
    "requiredFlows": [],
    "dependentFlows": []
  },
  "priority": 1,
  "businessDomain": "Finance"
}
```

## Testing

A test file is provided to verify all models work correctly:

```bash
python tools/legacy_analyzer/models/test_migration_flow_models.py
```

All tests pass successfully, verifying:
- Model instantiation
- Field assignment
- Method functionality
- JSON serialization
- Helper methods

## Integration

The models are exported from `tools/legacy_analyzer/models/__init__.py` and can be imported as:

```python
from tools.legacy_analyzer.models import (
    MigrationFlow,
    FlowScope,
    FlowInterface,
    FlowInterfaces,
    DatabaseOperation,
    DatasetOperation,
    DataOperations,
    FlowComplexity,
    FlowDependencies,
    EntryPointCaller,
    EntryPointTypeInfo,
    MigrationComplexityTier,
    EntryPointType,
    InterfaceDirection,
    DataOperationCategory,
    DataOperationType,
    DatasetMode,
    DatabaseType
)
```

## Next Steps

With the data models complete, the next tasks are:

1. **Task 3**: Flow ID Generation - Implement program-based flow ID generation
2. **Task 3A**: Entry Point Type Detection - Detect all invocation types for entry points
3. **Task 4**: Scope Identification - Identify artifacts within migration boundary
4. **Task 5**: Interface Identification - Identify inbound/outbound interfaces
5. **Task 6**: Data Operation Inference - Infer data operations from dependencies

These tasks will use the data models defined here to build and populate migration flows.
