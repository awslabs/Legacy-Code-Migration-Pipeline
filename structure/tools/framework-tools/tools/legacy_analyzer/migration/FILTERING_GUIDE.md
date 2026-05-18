# Migration Flow Filtering Guide

## Overview

The MigrationFlowExporter provides powerful filtering capabilities to help you select and export specific subsets of flows based on various criteria. This guide explains all available filtering options and how to use them effectively.

## Available Filters

### 1. Filter by Flow IDs

Select specific flows by their flow IDs.

**Method:** `filter_by_flow_ids(flow_ids: List[str]) -> List[str]`

**Use Case:** Export a predefined list of flows for a specific migration wave or package.

**Example:**
```python
from tools.legacy_analyzer.migration.flow_exporter import MigrationFlowExporter

exporter = MigrationFlowExporter(db_connection)

# Filter specific flows
flow_ids = ['FLOW_PAYROLL1', 'FLOW_BILLING1', 'FLOW_ACCT1']
valid_ids = exporter.filter_by_flow_ids(flow_ids)

print(f"Valid flows: {valid_ids}")
# Output: ['FLOW_BILLING1', 'FLOW_PAYROLL1', 'FLOW_ACCT1']
```

**Behavior:**
- Returns only flow IDs that exist in the database
- Invalid flow IDs are silently filtered out
- Returns empty list if no valid IDs found
- Results are sorted alphabetically

### 2. Filter by Complexity Tier

Select flows based on minimum complexity tier.

**Method:** `filter_by_complexity(min_complexity: str) -> List[str]`

**Complexity Tiers (in order):**
- `LOW` - Simple flows with minimal complexity
- `MEDIUM` - Moderate complexity flows
- `HIGH` - Complex flows requiring careful planning
- `VERY_HIGH` - Highly complex flows with significant risk

**Use Case:** Focus on high-risk flows first, or identify simple flows for quick wins.

**Example:**
```python
# Get all HIGH and VERY_HIGH complexity flows
high_complexity = exporter.filter_by_complexity('HIGH')

print(f"High complexity flows: {len(high_complexity)}")
# Output: High complexity flows: 15

# Get all flows (LOW and above)
all_flows = exporter.filter_by_complexity('LOW')
```

**Behavior:**
- Returns flows with complexity >= specified tier
- Case-insensitive (accepts 'high', 'HIGH', 'High')
- Raises `ValueError` for invalid tier names
- Includes all higher tiers (e.g., 'MEDIUM' includes MEDIUM, HIGH, VERY_HIGH)

### 3. Filter by Business Domain

Select flows belonging to a specific business domain.

**Method:** `filter_by_business_domain(business_domain: str) -> List[str]`

**Use Case:** Organize migration by business area (Finance, HR, Operations, etc.).

**Example:**
```python
# Get all Finance flows
finance_flows = exporter.filter_by_business_domain('Finance')

print(f"Finance flows: {finance_flows}")
# Output: Finance flows: ['FLOW_ACCT1', 'FLOW_BILLING1', 'FLOW_PAYROLL1']

# Get all HR flows
hr_flows = exporter.filter_by_business_domain('HR')
```

**Behavior:**
- Exact string match (case-sensitive)
- Returns empty list if domain not found
- Domain names must match exactly as stored in database

### 4. Filter by Entry Type

Select flows based on how they are invoked.

**Method:** `filter_by_entry_type(entry_type: str) -> List[str]`

**Entry Types:**
- `JCL` - Invoked by JCL jobs
- `CICS_TRANSACTION` - Invoked by CICS transactions
- `CICS_PROGRAM` - Defined as CICS programs in CSD
- `SCREEN` - Invoked from BMS screens
- `BATCH` - Batch processing entry points
- `EXTERNAL_CALL` - Called from external systems

**Use Case:** Group flows by invocation mechanism for migration planning.

**Example:**
```python
# Get all JCL-invoked flows
jcl_flows = exporter.filter_by_entry_type('JCL')

print(f"JCL flows: {len(jcl_flows)}")
# Output: JCL flows: 42

# Get all CICS transaction flows
cics_flows = exporter.filter_by_entry_type('CICS_TRANSACTION')
```

**Behavior:**
- Returns flows that have the specified entry type
- A flow can have multiple entry types (e.g., both JCL and CICS)
- Returns empty list if no flows have that entry type

### 5. Combined Filters

Apply multiple filters simultaneously using AND logic.

**Method:** `apply_combined_filters(flow_ids, min_complexity, business_domain, entry_type) -> List[str]`

**Use Case:** Precise flow selection with multiple criteria.

**Example:**
```python
# High complexity Finance flows invoked by JCL
result = exporter.apply_combined_filters(
    min_complexity='HIGH',
    business_domain='Finance',
    entry_type='JCL'
)

print(f"Matching flows: {result}")
# Output: Matching flows: ['FLOW_ACCT1']

# Specific flows that are HIGH complexity
result = exporter.apply_combined_filters(
    flow_ids=['FLOW_PAYROLL1', 'FLOW_BILLING1', 'FLOW_ACCT1'],
    min_complexity='HIGH'
)
# Returns only FLOW_BILLING1 and FLOW_ACCT1 (FLOW_PAYROLL1 is MEDIUM)
```

**Behavior:**
- All filters use AND logic (intersection)
- Filters are applied in sequence
- Returns empty list if no flows match all criteria
- All parameters are optional

## Exporting with Filters

The `export_all_flows()` method accepts all filter parameters.

**Method:** `export_all_flows(output_file, flow_ids, min_complexity, business_domain, entry_type)`

**Example:**
```python
# Export high complexity Finance flows
result = exporter.export_all_flows(
    output_file='finance_high_complexity.json',
    min_complexity='HIGH',
    business_domain='Finance'
)

print(f"Exported {len(result['flows'])} flows")

# Export specific flows
result = exporter.export_all_flows(
    output_file='wave1_flows.json',
    flow_ids=['FLOW_PAYROLL1', 'FLOW_BILLING1']
)

# Export all JCL flows with medium+ complexity
result = exporter.export_all_flows(
    output_file='jcl_medium_plus.json',
    min_complexity='MEDIUM',
    entry_type='JCL'
)
```

## Common Use Cases

### Use Case 1: Migration Wave Planning

Export flows for each migration wave based on complexity and dependencies.

```python
# Wave 1: Low complexity flows (quick wins)
wave1 = exporter.export_all_flows(
    output_file='wave1_flows.json',
    min_complexity='LOW'
)

# Wave 2: Medium complexity flows
wave2 = exporter.export_all_flows(
    output_file='wave2_flows.json',
    min_complexity='MEDIUM'
)

# Wave 3: High complexity flows
wave3 = exporter.export_all_flows(
    output_file='wave3_flows.json',
    min_complexity='HIGH'
)
```

### Use Case 2: Business Domain Organization

Export flows by business area for domain-specific migration teams.

```python
# Finance team
finance = exporter.export_all_flows(
    output_file='finance_flows.json',
    business_domain='Finance'
)

# HR team
hr = exporter.export_all_flows(
    output_file='hr_flows.json',
    business_domain='HR'
)

# Operations team
ops = exporter.export_all_flows(
    output_file='operations_flows.json',
    business_domain='Operations'
)
```

### Use Case 3: Technology-Specific Migration

Export flows by invocation mechanism for technology-specific migration.

```python
# JCL batch flows (migrate to scheduled jobs)
jcl_flows = exporter.export_all_flows(
    output_file='jcl_batch_flows.json',
    entry_type='JCL'
)

# CICS online flows (migrate to REST APIs)
cics_flows = exporter.export_all_flows(
    output_file='cics_online_flows.json',
    entry_type='CICS_TRANSACTION'
)
```

### Use Case 4: Risk-Based Prioritization

Focus on high-risk flows first.

```python
# High-risk Finance flows
high_risk = exporter.export_all_flows(
    output_file='high_risk_finance.json',
    min_complexity='HIGH',
    business_domain='Finance'
)

# Critical JCL flows
critical_jcl = exporter.export_all_flows(
    output_file='critical_jcl.json',
    min_complexity='VERY_HIGH',
    entry_type='JCL'
)
```

### Use Case 5: Custom Flow Selection

Select specific flows for a migration package.

```python
# Predefined migration package
package_flows = [
    'FLOW_PAYROLL1',
    'FLOW_PAYCALC',
    'FLOW_PAYDB',
    'FLOW_PAYREPORT'
]

result = exporter.export_all_flows(
    output_file='payroll_package.json',
    flow_ids=package_flows
)
```

## Filter Combinations

### Example 1: High Complexity Finance JCL Flows

```python
result = exporter.apply_combined_filters(
    min_complexity='HIGH',
    business_domain='Finance',
    entry_type='JCL'
)
# Returns flows that are:
# - HIGH or VERY_HIGH complexity AND
# - In Finance domain AND
# - Invoked by JCL
```

### Example 2: Specific Flows with Complexity Filter

```python
result = exporter.apply_combined_filters(
    flow_ids=['FLOW_A', 'FLOW_B', 'FLOW_C', 'FLOW_D'],
    min_complexity='MEDIUM'
)
# Returns only flows from the list that are MEDIUM or above
```

### Example 3: Domain and Entry Type

```python
result = exporter.apply_combined_filters(
    business_domain='HR',
    entry_type='CICS_TRANSACTION'
)
# Returns HR flows that are CICS transactions
```

## Best Practices

### 1. Start Broad, Then Narrow

```python
# First, see what's available
all_flows = exporter.get_flow_ids()
print(f"Total flows: {len(all_flows)}")

# Then filter by domain
finance = exporter.filter_by_business_domain('Finance')
print(f"Finance flows: {len(finance)}")

# Then add complexity filter
high_finance = exporter.apply_combined_filters(
    business_domain='Finance',
    min_complexity='HIGH'
)
print(f"High complexity Finance: {len(high_finance)}")
```

### 2. Validate Filter Results

```python
# Check if filter returns expected results
result = exporter.filter_by_complexity('HIGH')

if not result:
    print("Warning: No high complexity flows found")
else:
    print(f"Found {len(result)} high complexity flows")
```

### 3. Use Descriptive Output Filenames

```python
# Good: Descriptive filename
exporter.export_all_flows(
    output_file='finance_high_complexity_jcl_flows.json',
    min_complexity='HIGH',
    business_domain='Finance',
    entry_type='JCL'
)

# Bad: Generic filename
exporter.export_all_flows(
    output_file='flows.json',
    min_complexity='HIGH'
)
```

### 4. Document Filter Criteria

```python
# Document why these filters were chosen
filter_criteria = {
    'min_complexity': 'HIGH',
    'business_domain': 'Finance',
    'entry_type': 'JCL',
    'reason': 'Wave 1 migration: High-risk Finance batch flows'
}

result = exporter.export_all_flows(
    output_file='wave1_finance_batch.json',
    **{k: v for k, v in filter_criteria.items() if k != 'reason'}
)

print(f"Exported {len(result['flows'])} flows")
print(f"Reason: {filter_criteria['reason']}")
```

## Error Handling

### Invalid Complexity Tier

```python
try:
    result = exporter.filter_by_complexity('INVALID')
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Invalid complexity tier: INVALID. Must be one of: LOW, MEDIUM, HIGH, VERY_HIGH
```

### No Matching Flows

```python
result = exporter.apply_combined_filters(
    min_complexity='VERY_HIGH',
    business_domain='Marketing'  # Doesn't exist
)

if not result:
    print("No flows match the specified criteria")
```

### Invalid Flow IDs

```python
flow_ids = ['FLOW_VALID', 'FLOW_INVALID1', 'FLOW_INVALID2']
valid_ids = exporter.filter_by_flow_ids(flow_ids)

if len(valid_ids) < len(flow_ids):
    invalid = set(flow_ids) - set(valid_ids)
    print(f"Warning: Invalid flow IDs: {invalid}")
```

## Performance Considerations

### Filter Order Matters

For best performance, apply the most restrictive filter first:

```python
# Good: Most restrictive filter first
result = exporter.apply_combined_filters(
    flow_ids=['FLOW_A', 'FLOW_B'],  # Most restrictive (2 flows)
    min_complexity='HIGH',
    business_domain='Finance'
)

# Less efficient: Least restrictive filter first
# (but still works correctly)
result = exporter.apply_combined_filters(
    business_domain='Finance',  # Least restrictive (many flows)
    min_complexity='HIGH',
    flow_ids=['FLOW_A', 'FLOW_B']
)
```

### Caching Filter Results

If you need to apply the same filter multiple times:

```python
# Cache the result
high_complexity_flows = exporter.filter_by_complexity('HIGH')

# Reuse cached result
for flow_id in high_complexity_flows:
    # Process each flow
    pass
```

## Summary

The filtering system provides flexible flow selection with:

1. **Individual Filters**: Flow IDs, complexity, domain, entry type
2. **Combined Filters**: Apply multiple criteria with AND logic
3. **Export Integration**: All filters work with export_all_flows()
4. **Validation**: Invalid inputs are handled gracefully
5. **Performance**: Efficient database queries

Use filters to organize migration waves, focus on high-risk flows, and create targeted migration packages.
