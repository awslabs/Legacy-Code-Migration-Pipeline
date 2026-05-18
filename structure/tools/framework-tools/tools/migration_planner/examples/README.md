# Migration Planner Examples

This directory contains example input files and usage scenarios for the Migration Workpackage Planner.

## Example Files

### Input Files

1. **minimal_flows.json** - Minimal example with 2 flows
   - Simple dependency relationship (FLOW001 → FLOW002)
   - Demonstrates basic priority calculation
   - Good for testing and learning

2. **sample_flows.json** - Realistic example with 5 flows
   - Complex dependency tree with multiple phases
   - Variety of flow sizes (2-9 programs)
   - Mix of database operations
   - Demonstrates pre-existent module tracking

3. **sample_classifications.json** - Module classification data
   - Classifies programs as COMMONLY_USED, BUSINESS_LOGIC, REPORTING
   - Used with sample_flows.json for enhanced priority calculation

## Usage Examples

### Example 1: Minimal Planning

Run the planner with the minimal example:

```bash
python -m tools.migration_planner \
    --flows-file tools/migration_planner/examples/minimal_flows.json \
    --output-base ./output/minimal \
    --project-name minimal-example
```

**Expected Output:**
- 2 workpackages
- 2 phases (FLOW001 in Phase 1, FLOW002 in Phase 2)
- FLOW001 has higher priority (lower score) due to database operations

**Output Files:**
- `./output/minimal/Workpackage_Planning.json`
- `./output/minimal/Workpackage_Status.json`
- `./output/minimal/Workpackage_Definition_Roadmap.md`

### Example 2: Sample Planning Without Classifications

Run with sample flows but no classifications:

```bash
python -m tools.migration_planner \
    --flows-file tools/migration_planner/examples/sample_flows.json \
    --output-base ./output/sample \
    --project-name sample-example
```

**Expected Output:**
- 5 workpackages
- 3 phases based on dependencies
- Priority based on program count, complexity, and flow characteristics

### Example 3: Sample Planning With Classifications

Run with both flows and classifications:

```bash
python -m tools.migration_planner \
    --flows-file tools/migration_planner/examples/sample_flows.json \
    --classifications-file tools/migration_planner/examples/sample_classifications.json \
    --output-base ./output/sample-classified \
    --project-name sample-classified
```

**Expected Output:**
- 5 workpackages with adjusted priorities
- Flows with COMMONLY_USED modules get lower priority (higher score)
- More accurate migration sequencing

**Priority Differences:**
- FLOW002 and FLOW004 have UTIL001 (commonly used) → lower priority
- FLOW003 has CBSTM03A (commonly used) → lower priority
- FLOW001 and FLOW005 have no commonly used modules → higher priority

### Example 4: Debug Mode

Run with debug logging to see detailed processing:

```bash
python -m tools.migration_planner \
    --flows-file tools/migration_planner/examples/sample_flows.json \
    --classifications-file tools/migration_planner/examples/sample_classifications.json \
    --output-base ./output/debug \
    --project-name debug-example \
    --log-level DEBUG
```

**Debug Output Includes:**
- Detailed flow loading information
- Priority calculation breakdown for each flow
- Workpackage assignment details
- Phase determination logic
- Dependency graph analysis

## Understanding the Examples

### Minimal Example Analysis

**FLOW001: Simple Batch Job**
- 2 programs
- Has database operations (TESTDB)
- No dependencies
- **Priority Factors:**
  - totalPrograms: 2 × 2 = 4
  - compositeScore: 5.0 × 0.5 = 2.5
  - completeFlowBonus: -5 (has databases)
  - simpleFlowBonus: -3 (≤3 programs)
  - **Total: 4 + 2.5 - 5 - 3 = -1.5**

**FLOW002: Report Generation**
- 1 program
- No database operations
- Depends on FLOW001
- **Priority Factors:**
  - totalPrograms: 1 × 2 = 2
  - compositeScore: 2.0 × 0.5 = 1.0
  - completeFlowBonus: 0 (no databases)
  - simpleFlowBonus: -3 (≤3 programs)
  - **Total: 2 + 1.0 + 0 - 3 = 0**

**Result:**
- FLOW001 gets Workpackage 1 (priority: -1.5, Phase 1)
- FLOW002 gets Workpackage 2 (priority: 0, Phase 2)

### Sample Example Analysis

**Phase Structure:**
```
Phase 1: FLOW001, FLOW005 (no dependencies)
Phase 2: FLOW002, FLOW003 (depend on FLOW001)
Phase 3: FLOW004 (depends on FLOW002)
```

**Priority Order (without classifications):**
1. FLOW005 (2 programs, no DB, simple) → Workpackage 1
2. FLOW001 (3 programs, has DB, simple) → Workpackage 2
3. FLOW003 (4 programs, has DB) → Workpackage 3
4. FLOW002 (6 programs, has DB) → Workpackage 4
5. FLOW004 (9 programs, has DB) → Workpackage 5

**Priority Order (with classifications):**
1. FLOW005 (no commonly used modules) → Workpackage 1
2. FLOW001 (no commonly used modules) → Workpackage 2
3. FLOW002 (has UTIL001, commonly used) → Workpackage 3
4. FLOW003 (has CBSTM03A, commonly used) → Workpackage 4
5. FLOW004 (has UTIL001, UTIL002, commonly used) → Workpackage 5

**Pre-existent Modules:**
- Workpackage 3 (FLOW002): UTIL001 appears in no previous workpackages → []
- Workpackage 4 (FLOW003): UTIL001 appears in Workpackage 3 → ["UTIL001"]
- Workpackage 5 (FLOW004): UTIL001, UTIL002 appear in previous workpackages → ["UTIL001", "UTIL002"]

## Creating Your Own Examples

### Step 1: Create Business_Flows.json

```json
{
  "flows": [
    {
      "flowId": "YOUR_FLOW_ID",
      "name": "Your Flow Name",
      "scope": {
        "programs": [
          {
            "name": "PROGRAM_NAME",
            "type": "COBOL",
            "isUtility": false
          }
        ]
      },
      "complexity": {
        "totalPrograms": 1,
        "compositeScore": 5.0
      },
      "dataOperations": {
        "databases": ["DB_NAME"]
      },
      "dependencies": {
        "requiredFlows": [],
        "dependentFlows": []
      }
    }
  ]
}
```

### Step 2: (Optional) Create Module_Classifications.json

```json
{
  "classifications": {
    "PROGRAM_NAME": "COMMONLY_USED"
  }
}
```

### Step 3: Run the Planner

```bash
python -m tools.migration_planner \
    --flows-file your_flows.json \
    --classifications-file your_classifications.json \
    --output-base ./output \
    --project-name your-project
```

## Testing Scenarios

### Scenario 1: Simple Linear Dependencies

Create flows with linear dependencies (A → B → C) to test phase assignment.

### Scenario 2: Complex Dependency Tree

Create flows with multiple dependencies to test topological sorting.

### Scenario 3: Independent Flows

Create flows with no dependencies to test parallel phase assignment.

### Scenario 4: Circular Dependencies (Error Case)

Create flows with circular dependencies (A → B → C → A) to test error handling.

**Example:**
```json
{
  "flows": [
    {
      "flowId": "FLOW_A",
      "dependencies": {
        "requiredFlows": ["FLOW_C"],
        "dependentFlows": ["FLOW_B"]
      }
    },
    {
      "flowId": "FLOW_B",
      "dependencies": {
        "requiredFlows": ["FLOW_A"],
        "dependentFlows": ["FLOW_C"]
      }
    },
    {
      "flowId": "FLOW_C",
      "dependencies": {
        "requiredFlows": ["FLOW_B"],
        "dependentFlows": ["FLOW_A"]
      }
    }
  ]
}
```

**Expected Error:**
```
ERROR: Dependency validation error - Circular dependency detected: FLOW_A → FLOW_B → FLOW_C → FLOW_A
```

## Validation

After running the planner, validate the output:

### Check Planning JSON

```bash
# Verify JSON structure
python -c "import json; print(json.load(open('./output/Workpackage_Planning.json'))['metadata'])"

# Check statistics
python -c "import json; print(json.load(open('./output/Workpackage_Planning.json'))['statistics'])"
```

### Check Status JSON

```bash
# Verify all workpackages have NOT_STARTED status
python -c "import json; data = json.load(open('./output/Workpackage_Status.json')); print(all(wp['status'] == 'NOT_STARTED' for wp in data['workpackages']))"
```

### Check Roadmap Markdown

```bash
# View the roadmap
cat ./output/Workpackage_Definition_Roadmap.md

# Or open in a markdown viewer
open ./output/Workpackage_Definition_Roadmap.md
```

## Integration Examples

### With Legacy Analyzer

```bash
# 1. Run legacy analyzer (assuming it's set up)
python -m tools.legacy_analyzer analyze \
    --source-dir ./cobol-code \
    --db analyzer.db

# 2. Export flows (hypothetical command)
python -m tools.legacy_analyzer export-flows \
    --db analyzer.db \
    --output flows.json

# 3. Run migration planner
python -m tools.migration_planner \
    --flows-file flows.json \
    --output-base ./output
```

### With Custom Scripts

```python
# custom_planning.py
from tools.migration_planner import MigrationPlanner, PlannerConfig
from pathlib import Path
import json

# Load and modify flows
with open('sample_flows.json') as f:
    flows_data = json.load(f)

# Add custom processing
for flow in flows_data['flows']:
    # Custom logic here
    pass

# Save modified flows
with open('modified_flows.json', 'w') as f:
    json.dump(flows_data, f, indent=2)

# Run planner
config = PlannerConfig(
    flows_file=Path('modified_flows.json'),
    output_base=Path('./output'),
    project_name='custom-planning'
)

planner = MigrationPlanner(config)
result = planner.run()

if result.success:
    print(f"Planning completed: {result.output_files}")
else:
    print(f"Planning failed: {result.error_message}")
```

## Troubleshooting Examples

### Example: Missing Required Field

```json
{
  "flows": [
    {
      "flowId": "FLOW001",
      "scope": {
        "programs": []
      }
      // Missing complexity and dependencies
    }
  ]
}
```

**Error:**
```
ERROR: Validation error - Missing required field 'complexity' in flow FLOW001
```

### Example: Invalid Flow Reference

```json
{
  "flows": [
    {
      "flowId": "FLOW001",
      "dependencies": {
        "requiredFlows": ["FLOW999"],  // FLOW999 doesn't exist
        "dependentFlows": []
      }
    }
  ]
}
```

**Error:**
```
ERROR: Dependency validation error - Flow FLOW001 depends on non-existent flow: FLOW999
```

## Next Steps

1. Try the minimal example to understand basic functionality
2. Run the sample example to see complex scenarios
3. Create your own flows based on your project needs
4. Integrate with other toolkit tools for end-to-end workflows
5. Review the generated outputs and adjust priorities as needed

For more information, see the [main README](../README.md).
