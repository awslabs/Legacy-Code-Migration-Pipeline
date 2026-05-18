# Complexity Calculation Guide

## Overview

The complexity calculation feature in the Migration Flow Builder aggregates complexity metrics across all programs in a migration flow. This provides a holistic view of the effort required to migrate each flow.

## Purpose

Complexity metrics help migration planners:
- **Estimate migration effort** based on aggregate complexity
- **Prioritize flows** by complexity tier (LOW, MEDIUM, HIGH, VERY_HIGH)
- **Identify high-risk flows** that require more resources
- **Plan migration waves** by grouping flows of similar complexity

## How It Works

### Input Data

The complexity calculation requires:
1. **Program list**: Names of all programs in the flow
2. **Complexity metrics table**: Database table with per-program metrics

The `complexity_metrics` table contains:
- `program_name`: Program identifier
- `lines_of_code`: Executable lines of code (excluding comments/blanks)
- `cyclomatic_complexity`: Cyclomatic complexity score
- `composite_score`: Individual program complexity score
- `complexity_tier`: Individual program tier

### Calculation Process

1. **Query Database**: Retrieve complexity metrics for all programs in the flow
2. **Sum Metrics**: Aggregate lines of code and cyclomatic complexity
3. **Calculate Composite Score**: Apply weighted formula with normalization
4. **Determine Tier**: Classify flow based on composite score thresholds

### Composite Score Formula

```
Composite Score = (Normalized LOC × 0.4) + 
                  (Normalized Cyclomatic × 0.4) + 
                  (Normalized Programs × 0.2)
```

**Normalization Factors:**
- **LOC**: Divided by 50 (5,000 LOC = 100 points)
- **Cyclomatic**: Divided by 5 (500 cyclomatic = 100 points)
- **Programs**: Divided by 0.5 (50 programs = 100 points)

**Weights:**
- **LOC Weight**: 40% (code volume)
- **Cyclomatic Weight**: 40% (code complexity)
- **Program Count Weight**: 20% (integration complexity)

### Complexity Tiers

| Tier | Score Range | Description |
|------|-------------|-------------|
| **LOW** | < 25 | Simple flows with minimal complexity |
| **MEDIUM** | 25-50 | Moderate complexity, standard effort |
| **HIGH** | 50-75 | Complex flows requiring significant effort |
| **VERY_HIGH** | ≥ 75 | Highly complex flows, high risk |
| **UNKNOWN** | N/A | No complexity data available |

## Usage

### Python API

```python
from tools.legacy_analyzer.migration.flow_builder import MigrationFlowBuilder
import sqlite3

# Connect to database
conn = sqlite3.connect('analyzer.db')

# Create flow builder
builder = MigrationFlowBuilder(conn)

# Calculate complexity for a flow
programs = ['PAYROLL1', 'PAYCALC', 'PAYDB', 'PAYUTIL']
result = builder.calculate_flow_complexity(programs)

# Access results
print(f"Total Programs: {result['totalPrograms']}")
print(f"Total Lines: {result['totalLines']}")
print(f"Cyclomatic Complexity: {result['cyclomaticComplexity']}")
print(f"Composite Score: {result['compositeScore']}")
print(f"Tier: {result['tier']}")
```

### Result Structure

```python
{
    'totalPrograms': 4,           # Number of programs in flow
    'totalLines': 2800,           # Sum of LOC across programs
    'cyclomaticComplexity': 140,  # Sum of cyclomatic complexity
    'compositeScore': 35.20,      # Calculated composite score
    'tier': 'MEDIUM'              # Complexity tier
}
```

## Examples

### Example 1: Simple Flow (LOW Tier)

**Programs:**
- UTIL1: 200 LOC, 10 cyclomatic
- UTIL2: 150 LOC, 8 cyclomatic

**Result:**
```
Total Programs: 2
Total Lines: 350
Cyclomatic Complexity: 18
Composite Score: 6.40
Tier: LOW
```

### Example 2: Standard Flow (MEDIUM Tier)

**Programs:**
- PAYROLL1: 1200 LOC, 60 cyclomatic
- PAYCALC: 800 LOC, 40 cyclomatic
- PAYDB: 500 LOC, 25 cyclomatic

**Result:**
```
Total Programs: 3
Total Lines: 2500
Cyclomatic Complexity: 125
Composite Score: 31.20
Tier: MEDIUM
```

### Example 3: Complex Flow (HIGH Tier)

**Programs:**
- BILLING1: 2500 LOC, 125 cyclomatic
- BILLCALC: 1800 LOC, 90 cyclomatic
- BILLDB: 1200 LOC, 60 cyclomatic

**Result:**
```
Total Programs: 3
Total Lines: 5500
Cyclomatic Complexity: 275
Composite Score: 67.20
Tier: HIGH
```

### Example 4: Very Complex Flow (VERY_HIGH Tier)

**Programs:**
- ACCT1: 3000 LOC, 150 cyclomatic
- ACCT2: 2500 LOC, 125 cyclomatic
- ACCT3: 2000 LOC, 100 cyclomatic
- ACCT4: 1500 LOC, 75 cyclomatic

**Result:**
```
Total Programs: 4
Total Lines: 9000
Cyclomatic Complexity: 450
Composite Score: 109.60
Tier: VERY_HIGH
```

## Handling Missing Data

### No Complexity Data

When no complexity data exists for any program in the flow:

```python
result = builder.calculate_flow_complexity(['UNKNOWN1', 'UNKNOWN2'])

# Result:
{
    'totalPrograms': 2,
    'totalLines': 0,
    'cyclomaticComplexity': 0,
    'compositeScore': 0.80,  # Only program count contributes
    'tier': 'UNKNOWN'
}
```

### Partial Data

When only some programs have complexity data:

```python
# PROG1 has data, PROG2 doesn't
result = builder.calculate_flow_complexity(['PROG1', 'PROG2'])

# Result includes:
# - Metrics from PROG1 only
# - Total program count includes both
# - Tier is determined (not UNKNOWN)
```

### NULL Values

NULL values in the database are treated as 0:

```python
# Database has: PROG1 (LOC=NULL, Cyclomatic=NULL)
result = builder.calculate_flow_complexity(['PROG1'])

# Result:
{
    'totalPrograms': 1,
    'totalLines': 0,        # NULL treated as 0
    'cyclomaticComplexity': 0,  # NULL treated as 0
    'compositeScore': 0.40,
    'tier': 'LOW'
}
```

## Best Practices

### 1. Ensure Complexity Data Exists

Before calculating flow complexity, ensure complexity analysis has been run:

```python
from tools.legacy_analyzer.analysis.complexity_analyzer import ComplexityAnalyzer

# Analyze programs first
analyzer = ComplexityAnalyzer(database=conn)
for program in programs:
    metrics = analyzer.analyze_program(
        program_name=program,
        source_code=source_code,
        language='COBOL'
    )
    analyzer.save_metrics(metrics)

# Then calculate flow complexity
result = builder.calculate_flow_complexity(programs)
```

### 2. Handle UNKNOWN Tier

Always check for UNKNOWN tier and handle appropriately:

```python
result = builder.calculate_flow_complexity(programs)

if result['tier'] == 'UNKNOWN':
    print("Warning: No complexity data available for this flow")
    print("Run complexity analysis first")
else:
    print(f"Flow complexity: {result['tier']}")
```

### 3. Use Tier for Prioritization

Use complexity tiers to prioritize migration:

```python
# Group flows by tier
flows_by_tier = {
    'LOW': [],
    'MEDIUM': [],
    'HIGH': [],
    'VERY_HIGH': []
}

for flow_id, programs in all_flows.items():
    result = builder.calculate_flow_complexity(programs)
    if result['tier'] != 'UNKNOWN':
        flows_by_tier[result['tier']].append(flow_id)

# Migrate LOW complexity flows first
for flow_id in flows_by_tier['LOW']:
    print(f"Migrate {flow_id} (LOW complexity)")
```

### 4. Consider Composite Score

Use composite score for fine-grained ordering within tiers:

```python
# Sort flows within MEDIUM tier by score
medium_flows = []
for flow_id, programs in all_flows.items():
    result = builder.calculate_flow_complexity(programs)
    if result['tier'] == 'MEDIUM':
        medium_flows.append((flow_id, result['compositeScore']))

# Sort by score (ascending = easier first)
medium_flows.sort(key=lambda x: x[1])

for flow_id, score in medium_flows:
    print(f"{flow_id}: {score:.2f}")
```

## Integration with Migration Flow Export

The complexity calculation is integrated into the migration flow export:

```json
{
  "flowId": "FLOW_PAYROLL1",
  "name": "Payroll Processing",
  "complexity": {
    "totalPrograms": 4,
    "totalLines": 2800,
    "cyclomaticComplexity": 140,
    "compositeScore": 35.20,
    "tier": "MEDIUM"
  }
}
```

This allows migration planners to:
- Filter flows by complexity tier
- Sort flows by composite score
- Estimate effort based on complexity metrics
- Identify high-risk flows requiring additional resources

## Performance Considerations

### Database Queries

The complexity calculation performs a single database query:

```sql
SELECT program_name, lines_of_code, cyclomatic_complexity, composite_score
FROM complexity_metrics
WHERE program_name IN (?, ?, ?, ...)
```

**Performance Tips:**
- Ensure `program_name` is indexed (it's the primary key)
- Use batch calculations for multiple flows
- Cache results for frequently accessed flows

### Calculation Complexity

The calculation itself is O(n) where n is the number of programs:
- Query: O(n) database lookup
- Aggregation: O(n) iteration
- Score calculation: O(1)

For typical flows (5-20 programs), this is negligible.

## Troubleshooting

### Issue: All Flows Show UNKNOWN Tier

**Cause**: Complexity metrics table doesn't exist or is empty

**Solution**:
```python
# Check if table exists
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='complexity_metrics'
""")
if not cursor.fetchone():
    print("Complexity metrics table doesn't exist")
    print("Run complexity analysis first")
```

### Issue: Scores Seem Too Low/High

**Cause**: Normalization factors may need adjustment for your codebase

**Solution**: The normalization factors are tuned for typical mainframe applications. If your codebase has significantly different scales, you may need to adjust the factors in `_calculate_composite_score()`.

### Issue: Tier Doesn't Match Individual Programs

**Cause**: Flow tier is based on aggregate metrics, not individual program tiers

**Explanation**: A flow with multiple MEDIUM programs may be HIGH tier overall due to the cumulative complexity.

## Related Documentation

- [Flow Builder Guide](./FLOW_BUILDER_GUIDE.md)
- [Migration Flow Export Guide](./MIGRATION_FLOW_EXPORT_GUIDE.md)
- [Complexity Analyzer Documentation](../analysis/COMPLEXITY_ANALYZER.md)

## Demo Script

Run the demo script to see complexity calculation in action:

```bash
python tools/legacy_analyzer/migration/demo_complexity_calculation.py
```

The demo shows:
1. Basic complexity calculation for different flows
2. Handling of missing data
3. Different complexity tiers
4. Composite score breakdown
