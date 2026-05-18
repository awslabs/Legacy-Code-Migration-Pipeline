# Flow Dependencies Identification Guide

## Overview

Flow dependencies identify relationships between migration flows, enabling proper sequencing of migration activities. This guide explains how to use the `identify_flow_dependencies()` method to analyze and plan migration waves.

## Key Concepts

### Required Flows

**Definition:** Flows that must be migrated BEFORE the current flow.

**Identification:** Analyzed from outbound interfaces. When a flow calls external programs that are entry points of other flows, those flows are "required."

**Example:**
```
FLOW_PAYROLL calls DBUTIL (entry point of FLOW_DATABASE_UTIL)
→ FLOW_DATABASE_UTIL is a required flow for FLOW_PAYROLL
→ Must migrate FLOW_DATABASE_UTIL before FLOW_PAYROLL
```

### Dependent Flows

**Definition:** Flows that can only be migrated AFTER the current flow.

**Identification:** Analyzed from inbound interfaces. When external programs (from other flows) call into this flow, those flows are "dependent."

**Example:**
```
PAYROLL (from FLOW_PAYROLL) calls into FLOW_DATABASE_UTIL
→ FLOW_PAYROLL is a dependent flow of FLOW_DATABASE_UTIL
→ Must migrate FLOW_DATABASE_UTIL before FLOW_PAYROLL
```

### Circular Dependencies

**Definition:** Two or more flows that depend on each other, creating a cycle.

**Detection:** A flow appears in both `requiredFlows` and `dependentFlows` lists.

**Resolution Strategies:**
1. Migrate flows together in the same wave
2. Refactor to break the circular dependency
3. Use API versioning to maintain compatibility during migration

## Method Signature

```python
def identify_flow_dependencies(
    self,
    flow_id: str,
    entry_program: str,
    interfaces: Dict[str, List[Dict]]
) -> Dict[str, List[str]]:
    """
    Identify dependencies between flows.
    
    Args:
        flow_id: The flow ID for this flow
        entry_program: The entry point program name for this flow
        interfaces: Dictionary with 'inbound' and 'outbound' interface lists
        
    Returns:
        Dictionary with:
        {
            'requiredFlows': [flow_ids that must be migrated first],
            'dependentFlows': [flow_ids that depend on this flow]
        }
    """
```

## Usage Examples

### Example 1: Flow with No Dependencies

```python
from tools.legacy_analyzer.migration.flow_builder import MigrationFlowBuilder

builder = MigrationFlowBuilder(db_connection)

flow_id = "FLOW_STANDALONE"
entry_program = "STANDALONE"
interfaces = {
    'inbound': [],
    'outbound': []
}

dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)

# Result:
# {
#     'requiredFlows': [],
#     'dependentFlows': []
# }

# Interpretation: Can be migrated independently
```

### Example 2: Flow with Required Dependencies

```python
flow_id = "FLOW_PAYROLL"
entry_program = "PAYROLL"
interfaces = {
    'inbound': [],
    'outbound': [
        {
            'type': 'PROGRAM_CALL',
            'source': 'PAYROLL',
            'target': 'DBUTIL',  # Entry point of FLOW_DATABASE_UTIL
            'external': True
        },
        {
            'type': 'PROGRAM_CALL',
            'source': 'PAYROLL',
            'target': 'LOGGER',  # Entry point of FLOW_LOGGER
            'external': True
        }
    ]
}

dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)

# Result:
# {
#     'requiredFlows': ['FLOW_DATABASE_UTIL', 'FLOW_LOGGER'],
#     'dependentFlows': []
# }

# Migration order: FLOW_DATABASE_UTIL, FLOW_LOGGER → FLOW_PAYROLL
```

### Example 3: Flow with Dependent Flows

```python
flow_id = "FLOW_DATABASE_UTIL"
entry_program = "DBUTIL"
interfaces = {
    'inbound': [
        {
            'type': 'PROGRAM_CALL',
            'source': 'PAYROLL',  # From FLOW_PAYROLL
            'target': 'DBUTIL_SUB',
            'metadata': {}
        },
        {
            'type': 'PROGRAM_CALL',
            'source': 'BILLING',  # From FLOW_BILLING
            'target': 'DBUTIL_SUB',
            'metadata': {}
        }
    ],
    'outbound': []
}

dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)

# Result:
# {
#     'requiredFlows': [],
#     'dependentFlows': ['FLOW_BILLING', 'FLOW_PAYROLL']
# }

# Migration order: FLOW_DATABASE_UTIL → FLOW_PAYROLL, FLOW_BILLING
```

### Example 4: Circular Dependencies

```python
flow_id = "FLOW_PAYROLL"
entry_program = "PAYROLL"
interfaces = {
    'inbound': [
        {
            'type': 'PROGRAM_CALL',
            'source': 'BILLING',  # From FLOW_BILLING
            'target': 'PAYROLL_SUB',
            'metadata': {}
        }
    ],
    'outbound': [
        {
            'type': 'PROGRAM_CALL',
            'source': 'PAYROLL',
            'target': 'BILLING',  # Entry point of FLOW_BILLING
            'external': True
        }
    ]
}

dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)

# Result:
# {
#     'requiredFlows': ['FLOW_BILLING'],
#     'dependentFlows': ['FLOW_BILLING']
# }

# Circular dependency detected!
# Check for circular dependencies:
circular = set(dependencies['requiredFlows']) & set(dependencies['dependentFlows'])
if circular:
    print(f"Circular dependency: {circular}")
    # Must migrate together or refactor
```

## Migration Planning Workflow

### Step 1: Analyze All Flows

```python
# Analyze dependencies for all flows
all_dependencies = {}

for flow_id, flow_data in all_flows.items():
    entry_program = flow_data['entry_program']
    interfaces = flow_data['interfaces']
    
    dependencies = builder.identify_flow_dependencies(
        flow_id, entry_program, interfaces
    )
    
    all_dependencies[flow_id] = dependencies
```

### Step 2: Calculate Migration Waves

```python
def calculate_migration_waves(all_dependencies):
    """Calculate migration waves based on dependencies."""
    waves = []
    remaining_flows = set(all_dependencies.keys())
    migrated_flows = set()
    
    while remaining_flows:
        # Find flows with no unmigrated required flows
        wave = []
        for flow_id in remaining_flows:
            required = set(all_dependencies[flow_id]['requiredFlows'])
            if required.issubset(migrated_flows):
                wave.append(flow_id)
        
        if not wave:
            # Circular dependency - all remaining flows depend on each other
            wave = list(remaining_flows)
            print(f"Warning: Circular dependencies in wave {len(waves) + 1}: {wave}")
        
        waves.append(wave)
        migrated_flows.update(wave)
        remaining_flows -= set(wave)
    
    return waves

# Calculate waves
waves = calculate_migration_waves(all_dependencies)

# Display migration plan
for i, wave in enumerate(waves, 1):
    print(f"Wave {i}: {', '.join(wave)}")
```

### Step 3: Identify Parallel Migration Opportunities

```python
def identify_parallel_opportunities(waves):
    """Identify flows that can be migrated in parallel."""
    for i, wave in enumerate(waves, 1):
        if len(wave) > 1:
            print(f"Wave {i}: {len(wave)} flows can be migrated in parallel")
            for flow_id in wave:
                print(f"  - {flow_id}")
        else:
            print(f"Wave {i}: {wave[0]} (sequential)")

identify_parallel_opportunities(waves)
```

### Step 4: Generate Migration Checklist

```python
def generate_migration_checklist(flow_id, dependencies):
    """Generate pre-migration checklist for a flow."""
    print(f"Migration Checklist for {flow_id}")
    print("=" * 70)
    
    print("\n1. Pre-Migration Requirements:")
    if dependencies['requiredFlows']:
        print("   ✓ Ensure these flows are migrated first:")
        for req_flow in dependencies['requiredFlows']:
            print(f"     - {req_flow}")
    else:
        print("   ✓ No prerequisite flows")
    
    print("\n2. Impact Analysis:")
    if dependencies['dependentFlows']:
        print("   ⚠️  These flows will be affected:")
        for dep_flow in dependencies['dependentFlows']:
            print(f"     - {dep_flow}")
        print("   → Coordinate with teams owning these flows")
    else:
        print("   ✓ No dependent flows (low risk)")
    
    print("\n3. Migration Sequence:")
    if dependencies['requiredFlows']:
        print(f"   Step 1: Migrate {', '.join(dependencies['requiredFlows'])}")
        print(f"   Step 2: Migrate {flow_id}")
        if dependencies['dependentFlows']:
            print(f"   Step 3: Migrate {', '.join(dependencies['dependentFlows'])}")
    else:
        print(f"   Step 1: Migrate {flow_id}")
        if dependencies['dependentFlows']:
            print(f"   Step 2: Migrate {', '.join(dependencies['dependentFlows'])}")

# Generate checklist for a specific flow
generate_migration_checklist("FLOW_PAYROLL", all_dependencies["FLOW_PAYROLL"])
```

## Database Requirements

The `identify_flow_dependencies()` method requires these database tables:

### migration_flows Table

```sql
CREATE TABLE migration_flows (
    flow_id VARCHAR(100) PRIMARY KEY,
    entry_program VARCHAR(44),
    -- other columns...
);
```

Used to identify which programs are entry points of flows.

### flow_scope Table

```sql
CREATE TABLE flow_scope (
    flow_id VARCHAR(100),
    artifact_type VARCHAR(20),
    artifact_name VARCHAR(44),
    PRIMARY KEY (flow_id, artifact_type, artifact_name)
);
```

Used to identify which flows contain specific programs.

## Algorithm Details

### Identifying Required Flows

1. Extract target programs from outbound interfaces
2. Query `migration_flows` table to find flows where `entry_program` matches target programs
3. Exclude the current flow (no self-dependencies)
4. Return sorted list of flow IDs

### Identifying Dependent Flows

1. Extract source programs from inbound interfaces
2. Query `flow_scope` table to find flows containing these source programs
3. Exclude the current flow (no self-dependencies)
4. Return sorted list of flow IDs

### Handling Circular Dependencies

1. Calculate both required and dependent flows
2. Find intersection of the two sets
3. Log warning if circular dependencies detected
4. Return both lists (caller decides how to handle)

## Best Practices

### 1. Always Check for Circular Dependencies

```python
dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)

circular = set(dependencies['requiredFlows']) & set(dependencies['dependentFlows'])
if circular:
    print(f"Warning: Circular dependencies detected: {circular}")
    # Handle appropriately
```

### 2. Use Dependencies for Wave Planning

```python
# Calculate migration waves based on dependencies
waves = calculate_migration_waves(all_dependencies)

# Identify parallel migration opportunities
for wave in waves:
    if len(wave) > 1:
        print(f"Can migrate in parallel: {wave}")
```

### 3. Generate Migration Documentation

```python
# Document dependencies for each flow
for flow_id, deps in all_dependencies.items():
    print(f"\n{flow_id}:")
    print(f"  Requires: {deps['requiredFlows']}")
    print(f"  Depended on by: {deps['dependentFlows']}")
```

### 4. Validate Migration Order

```python
def validate_migration_order(migration_order, all_dependencies):
    """Validate that migration order respects dependencies."""
    migrated = set()
    
    for flow_id in migration_order:
        required = set(all_dependencies[flow_id]['requiredFlows'])
        
        if not required.issubset(migrated):
            missing = required - migrated
            print(f"Error: {flow_id} requires {missing} to be migrated first")
            return False
        
        migrated.add(flow_id)
    
    return True
```

### 5. Handle Missing Data Gracefully

```python
# The method handles missing tables gracefully
# Returns empty lists if migration_flows or flow_scope tables don't exist
dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)

# Always returns valid structure:
# {'requiredFlows': [], 'dependentFlows': []}
```

## Common Patterns

### Pattern 1: Shared Utility Flow

```
Utility Flow (FLOW_UTIL)
├── No required flows
└── Multiple dependent flows (FLOW_APP1, FLOW_APP2, FLOW_APP3)

Migration Strategy:
- Migrate utility first
- Then migrate dependent applications in parallel
```

### Pattern 2: Layered Architecture

```
Wave 1: Data Layer (FLOW_DATABASE)
Wave 2: Business Logic (FLOW_BUSINESS)
Wave 3: Presentation (FLOW_UI)

Each layer depends on the previous layer
```

### Pattern 3: Circular Dependencies

```
FLOW_A ←→ FLOW_B

Migration Strategy:
- Migrate together in same wave
- Or refactor to break dependency
- Or use API versioning
```

### Pattern 4: Independent Flows

```
FLOW_STANDALONE
├── No required flows
└── No dependent flows

Migration Strategy:
- Can migrate at any time
- No coordination needed
```

## Troubleshooting

### Issue: Empty Dependency Lists

**Cause:** `migration_flows` or `flow_scope` tables don't exist yet.

**Solution:** Ensure flows are built and written to database before analyzing dependencies.

```python
# Build flows first
builder.build_all_flows()

# Then analyze dependencies
dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)
```

### Issue: Unexpected Circular Dependencies

**Cause:** Actual circular dependencies in the code.

**Solution:** 
1. Verify the dependencies are real (check source code)
2. Consider refactoring to break the cycle
3. If unavoidable, migrate flows together

### Issue: Missing Dependencies

**Cause:** Interfaces not properly identified.

**Solution:** Verify interface identification is working correctly:

```python
# Check interfaces
print(f"Inbound: {interfaces['inbound']}")
print(f"Outbound: {interfaces['outbound']}")

# Verify programs are entry points
cursor.execute("SELECT flow_id, entry_program FROM migration_flows")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
```

## Performance Considerations

### Database Queries

The method executes 2-4 database queries:
1. Check if `migration_flows` table exists
2. Query required flows (outbound dependencies)
3. Check if `flow_scope` table exists
4. Query dependent flows (inbound dependencies)

### Optimization Tips

1. **Use indexes:** Ensure indexes exist on `entry_program` and `artifact_name` columns
2. **Batch analysis:** Analyze all flows in one pass rather than individually
3. **Cache results:** Cache dependency analysis results for reuse

## Integration with Migration Planning

### Export Dependencies to JSON

```python
def export_dependencies_to_json(all_dependencies, output_file):
    """Export dependency graph to JSON."""
    import json
    
    with open(output_file, 'w') as f:
        json.dump(all_dependencies, f, indent=2)

export_dependencies_to_json(all_dependencies, 'flow_dependencies.json')
```

### Generate Dependency Graph Visualization

```python
def generate_dependency_graph(all_dependencies):
    """Generate Mermaid diagram of dependencies."""
    print("```mermaid")
    print("graph TD")
    
    for flow_id, deps in all_dependencies.items():
        for req_flow in deps['requiredFlows']:
            print(f"    {req_flow} --> {flow_id}")
    
    print("```")

generate_dependency_graph(all_dependencies)
```

## Summary

Flow dependencies enable:
1. **Proper migration sequencing** - Migrate flows in correct order
2. **Wave planning** - Group flows into migration waves
3. **Parallel migration** - Identify flows that can migrate simultaneously
4. **Risk assessment** - Understand impact of migrating each flow
5. **Circular dependency detection** - Identify and handle cycles

Use `identify_flow_dependencies()` as part of your migration planning workflow to ensure successful, coordinated migration of complex mainframe applications.
