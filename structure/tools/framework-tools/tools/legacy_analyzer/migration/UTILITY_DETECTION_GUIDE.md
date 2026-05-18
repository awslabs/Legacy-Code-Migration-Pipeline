# Utility Program Detection Guide

## Overview

The Utility Program Detection feature identifies programs that are shared across multiple flows, helping migration architects understand which components are reusable utilities versus business-specific logic.

## What is a Utility Program?

A utility program is a program that:
1. Is called by multiple different entry points (flows)
2. Matches common utility naming patterns (e.g., UTIL*, COMMON*, etc.)
3. Provides shared functionality across the application

**Examples:**
- `UTIL_COMMON` - Common utility functions
- `UTIL_DB` - Database access utilities
- `COMMON_LOGGER` - Logging utilities
- `DATEUTIL` - Date manipulation utilities

## Detection Criteria

Utility programs are identified by **either** of these criteria:

### 1. Call Frequency Threshold
Programs called by **5 or more different flows** (configurable)

**Example:**
```
UTIL_COMMON is called by:
  - FLOW_PAYROLL1
  - FLOW_BILLING1
  - FLOW_ACCT1
  - FLOW_REPORT1
  - FLOW_BATCH1
  - FLOW_ONLINE1
→ 6 flows ≥ 5 threshold → Marked as UTILITY
```

### 2. Naming Patterns
Programs matching configured patterns with wildcards

**Common patterns:**
- `UTIL*` - Matches UTIL_COMMON, UTIL_DB, UTILPROG, etc.
- `COMMON*` - Matches COMMON_LOGGER, COMMONUTIL, etc.
- `*UTIL` - Matches DATEUTIL, FILEUTIL, etc.
- `LIB*` - Matches LIBMATH, LIBSTRING, etc.

## Usage

### Basic Usage

```python
from tools.legacy_analyzer.migration import UtilityDetector

# Initialize detector with threshold
detector = UtilityDetector(db_connection, call_threshold=5)

# Prepare flow data
all_flows = {
    'FLOW_APP1': {
        'entry_program': 'APP1',
        'start_program': 'APP1',
        'programs': ['APP1', 'UTIL_COMMON', 'HELPER1']
    },
    # ... more flows
}

# Detect utilities
utilities = detector.detect_utility_programs(
    all_flows,
    utility_patterns=['UTIL*', 'COMMON*', 'LIB*']
)

# Write to database
detector.write_utility_metadata(utilities)
```

### Using Convenience Function

```python
from tools.legacy_analyzer.migration import detect_utility_programs

utilities = detect_utility_programs(
    db_connection,
    all_flows,
    utility_patterns=['UTIL*', 'COMMON*'],
    call_threshold=5
)
```

### Querying Utilities

```python
# Get all utilities from database
utilities = detector.get_utility_programs()

# Check if specific program is a utility
is_util = detector.is_utility_program('UTIL_COMMON')

# Get flows sharing a utility
shared_flows = detector.get_shared_flows('UTIL_COMMON')
```

### Extended Scope Format

```python
# Format programs with utility metadata
programs = ['APP1', 'UTIL_COMMON', 'HELPER1']
extended_scope = detector.format_extended_scope(programs)

# Result:
# [
#   {'name': 'APP1', 'is_utility': False},
#   {
#     'name': 'UTIL_COMMON',
#     'is_utility': True,
#     'call_count': 6,
#     'shared_by_flows': ['FLOW_APP1', 'FLOW_APP2', ...],
#     'classification': 'UTILITY'
#   },
#   {'name': 'HELPER1', 'is_utility': False}
# ]
```

## Configuration

### Adjusting Call Threshold

```python
# More aggressive detection (lower threshold)
detector = UtilityDetector(db_connection, call_threshold=3)

# More conservative detection (higher threshold)
detector = UtilityDetector(db_connection, call_threshold=10)
```

### Custom Naming Patterns

```python
# Organization-specific patterns
utility_patterns = [
    'UTIL*',      # Standard utilities
    'COMMON*',    # Common libraries
    'LIB*',       # Library programs
    'SYS*',       # System programs
    '*UTIL',      # Programs ending with UTIL
    'ACME_*'      # Company-specific prefix
]

utilities = detector.detect_utility_programs(
    all_flows,
    utility_patterns=utility_patterns
)
```

## Output Formats

### Simple Format (Backward Compatible)

```json
{
  "scope": {
    "programs": ["APP1", "UTIL_COMMON", "HELPER1"]
  }
}
```

### Extended Format (With Utility Metadata)

```json
{
  "scope": {
    "programs": [
      {
        "name": "APP1",
        "is_utility": false
      },
      {
        "name": "UTIL_COMMON",
        "is_utility": true,
        "shared_by_flows": [
          "FLOW_PAYROLL1",
          "FLOW_BILLING1",
          "FLOW_ACCT1"
        ],
        "call_count": 6,
        "classification": "UTILITY"
      },
      {
        "name": "HELPER1",
        "is_utility": false
      }
    ]
  }
}
```

## Database Schema

### program_metadata Table

```sql
CREATE TABLE program_metadata (
    program_name VARCHAR(44) PRIMARY KEY,
    is_utility BOOLEAN DEFAULT FALSE,
    call_count INTEGER DEFAULT 0,
    classification VARCHAR(20),
    shared_by_flow_count INTEGER DEFAULT 0,
    naming_pattern VARCHAR(50),
    created_date DATE,
    updated_date DATE
)
```

**Columns:**
- `program_name`: Program identifier
- `is_utility`: Boolean flag indicating utility status
- `call_count`: Number of flows calling this program
- `classification`: Program classification (e.g., 'UTILITY')
- `shared_by_flow_count`: Number of flows sharing this program
- `naming_pattern`: Pattern that matched (if detected by pattern)
- `created_date`: When record was created
- `updated_date`: When record was last updated

## Integration with Flow Export

### CLI Integration (Future)

```bash
# Build flows with utility detection
legacy_analyzer migration build-flows \
  --db analyzer.db \
  --utility-threshold 5 \
  --utility-patterns "UTIL*,COMMON*,LIB*"

# Export with extended scope format
legacy_analyzer migration export-flows \
  --db analyzer.db \
  --output flows.json \
  --extended-scope
```

### Python API Integration (Future)

```python
from tools.legacy_analyzer import LegacyAnalyzer

analyzer = LegacyAnalyzer(db_path='analyzer.db')

# Build flows with utility detection
analyzer.build_migration_flows(
    utility_threshold=5,
    utility_patterns=['UTIL*', 'COMMON*']
)

# Export with extended scope
analyzer.export_migration_flows(
    output_file='flows.json',
    extended_scope=True
)
```

## Use Cases

### 1. Migration Planning

**Scenario:** Identify shared utilities that need special handling during migration.

```python
# Detect utilities
utilities = detector.detect_utility_programs(all_flows)

# Find high-impact utilities (used by many flows)
high_impact = {
    name: meta for name, meta in utilities.items()
    if meta['call_count'] >= 10
}

print(f"Found {len(high_impact)} high-impact utilities")
for name, meta in high_impact.items():
    print(f"  {name}: used by {meta['call_count']} flows")
```

### 2. Dependency Analysis

**Scenario:** Understand which flows depend on a specific utility.

```python
# Get flows using a specific utility
shared_flows = detector.get_shared_flows('UTIL_COMMON')

print(f"UTIL_COMMON is used by {len(shared_flows)} flows:")
for flow_id in shared_flows:
    print(f"  - {flow_id}")
```

### 3. Refactoring Candidates

**Scenario:** Identify programs that should be utilities but aren't named as such.

```python
# Detect by threshold only (no patterns)
utilities = detector.detect_utility_programs(
    all_flows,
    utility_patterns=None
)

# Find programs detected by frequency but not by naming
refactoring_candidates = {
    name: meta for name, meta in utilities.items()
    if meta['naming_pattern'] is None
}

print("Programs that should be renamed as utilities:")
for name, meta in refactoring_candidates.items():
    print(f"  {name}: called by {meta['call_count']} flows")
```

### 4. Service Boundary Definition

**Scenario:** Decide whether to include utilities in service scope or extract them.

```python
# Get extended scope for a flow
programs = flow['programs']
extended_scope = detector.format_extended_scope(programs)

# Separate utilities from business logic
business_programs = [p for p in extended_scope if not p['is_utility']]
utility_programs = [p for p in extended_scope if p['is_utility']]

print(f"Business programs: {len(business_programs)}")
print(f"Utility programs: {len(utility_programs)}")

# Decision: Extract utilities to shared library?
if len(utility_programs) > 5:
    print("Consider extracting utilities to shared library")
```

## Best Practices

### 1. Choose Appropriate Threshold

- **Low threshold (3-4)**: More aggressive, catches utilities used by fewer flows
- **Medium threshold (5-7)**: Balanced approach, recommended default
- **High threshold (10+)**: Conservative, only marks heavily-used programs

### 2. Define Organization-Specific Patterns

```python
# Customize for your organization
utility_patterns = [
    'UTIL*',           # Standard utilities
    'COMMON*',         # Common libraries
    f'{ORG_PREFIX}*',  # Organization prefix
    '*LIB',            # Library suffix
]
```

### 3. Review Detection Results

```python
# After detection, review results
utilities = detector.detect_utility_programs(all_flows, utility_patterns)

print("Detected utilities:")
for name, meta in utilities.items():
    reason = "pattern" if meta['naming_pattern'] else "frequency"
    print(f"  {name}: detected by {reason} ({meta['call_count']} calls)")
```

### 4. Update Periodically

```python
# Re-run detection after adding new flows
utilities = detector.detect_utility_programs(all_flows, utility_patterns)
detector.write_utility_metadata(utilities)  # Updates existing records
```

## Troubleshooting

### Issue: Program Not Detected as Utility

**Possible causes:**
1. Call count below threshold
2. Doesn't match any naming pattern
3. Program is entry point in most flows

**Solution:**
```python
# Check call count
counts = detector._count_program_calls(all_flows)
print(f"Program call count: {counts.get('MYPROGRAM', 0)}")

# Check pattern matching
matches = detector._matches_pattern('MYPROGRAM', 'UTIL*')
print(f"Matches pattern: {matches}")

# Lower threshold or add pattern
detector = UtilityDetector(db_connection, call_threshold=3)
```

### Issue: Entry Point Marked as Utility

**Cause:** Program is entry point in one flow but called in many others.

**Expected behavior:** This is correct! A program can be both an entry point and a utility.

**Example:**
```
UTIL_BATCH:
  - Entry point in FLOW_UTIL_BATCH (batch utility runner)
  - Called by FLOW_APP1, FLOW_APP2, FLOW_APP3
  → Correctly marked as utility (called by 3 flows)
```

### Issue: False Positives

**Cause:** Threshold too low or patterns too broad.

**Solution:**
```python
# Increase threshold
detector = UtilityDetector(db_connection, call_threshold=7)

# Use more specific patterns
utility_patterns = ['UTIL_*', 'COMMON_*']  # More specific
# Instead of: ['UTIL*', 'COMMON*']  # Too broad
```

## Performance Considerations

### Large Codebases

For codebases with 1000+ flows:

```python
# Detection is fast (< 1 second for 1000 flows)
utilities = detector.detect_utility_programs(all_flows, utility_patterns)

# Database writes are batched
detector.write_utility_metadata(utilities)  # Single transaction

# Queries are indexed
shared_flows = detector.get_shared_flows('UTIL_COMMON')  # Fast lookup
```

### Memory Usage

```python
# For very large codebases, process in batches
batch_size = 100
flow_ids = list(all_flows.keys())

for i in range(0, len(flow_ids), batch_size):
    batch = {fid: all_flows[fid] for fid in flow_ids[i:i+batch_size]}
    utilities = detector.detect_utility_programs(batch, utility_patterns)
    detector.write_utility_metadata(utilities)
```

## Examples

See `demo_utility_detection.py` for a complete working example.

## Related Documentation

- [Migration Flow Export Design](../../../.kiro/specs/migration-flow-export/design.md)
- [External Configuration Guide](EXTERNAL_CONFIG_GUIDE.md)
- [Task 4B Implementation](TASK_4B_COMPLETE.md)
