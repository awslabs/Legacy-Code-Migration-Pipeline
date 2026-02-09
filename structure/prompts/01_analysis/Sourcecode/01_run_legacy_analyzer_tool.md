# Phase 1.1: Run Legacy Analyzer Tool

---

## Orchestration Information

**Phase**: Phase 1 - Source Code Analysis
**Step**: Step 1.1 - Legacy Code Analysis Tool Execution
**Team Supervisor**: analysis_team_supervisor
**Assigned Agent**: analysis_specialist_legacy_code
**Task File Name**: {{TASKS_BASE_PATH}}/analysis_legacy_analyzer_task.md

### Expected Deliverables

1. **Analysis Database**
   - File: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db
   - Description: SQLite database containing all analysis data (inventory, dependencies, flows, entry points)

2. **Entry Points Report**
   - Files: 
     - {{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points.json
     - {{SOURCE_CODE_ANALYSIS_OUTPUT}}/exports/entry_points.csv
     - {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/entry_points.txt
   - Description: Detected entry points in JSON, CSV, and text formats

3. **Migration Flows**
   - Directory: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/
   - Description: Migration flows with 6 sorting strategies (complexity, independence, dependencies, name, database order)

4. **JCL Jobs**
   - Directory: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/
   - Description: JCL jobs with 4 sorting strategies (name, type, dependencies, complexity)

5. **Analysis Summary Report**
   - File: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.txt
   - Description: Comprehensive summary of inventory, dependencies, CICS resources, and migration flows

6. **Progress Tracking**
   - File: {{ANALYSIS_STATUS}}
   - Template: {{ANALYSIS_STATUS_TEMPLATE}}
   - Description: Analysis progress and status tracking

### Success Criteria
- [ ] Analysis database created and populated with all data
- [ ] Entry points detected and exported in 3 formats
- [ ] Migration flows exported with 6 sorting strategies
- [ ] JCL jobs exported with 4 sorting strategies
- [ ] Summary report generated with statistics
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for review

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: Execute legacy_analyzer tool for comprehensive static code analysis
- **Detailed instructions**: All Steps 1-4 below
- **Technical specifications**: Tool location, supported languages, output structure
- **Error handling guidance**: Common error scenarios and recovery strategies
- **Output format requirements**: All deliverables and their specifications
- **Quality criteria**: Completeness, accuracy, validation requirements

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Source code directory: {{SOURCE_CODE}}
  - Legacy specifications: {{LEGACY_SPECIFICATION}}
- **All output locations** (resolved paths):
  - Analysis output directory: {{SOURCE_CODE_ANALYSIS_OUTPUT}}
  - Analysis database: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db
  - Entry points: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points.json
  - Migration flows: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/
  - JCL jobs: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/
  - Reports: {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/
  - Progress tracking: {{ANALYSIS_STATUS}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Analysis status template: {{ANALYSIS_STATUS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: analysis_specialist_legacy_code
- **Agent definition file**: structure/agents/analysis_team/analysis_specialist_legacy_code.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations, output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-4), tool usage, error handling
- **Expected Deliverables**: All 6 deliverables with paths, descriptions, validation checklists
- **Quality Criteria**: Completeness, accuracy, consistency (from this prompt)
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

---

## Context

- **Input Locations**:
  - Source code directory: `{{SOURCE_CODE}}`
  - Legacy specifications: `{{LEGACY_SPECIFICATION}}`

- **Output Locations**:
  - Analysis output directory: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}`
  - Analysis database: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db`
  - Entry points: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points.json`
  - Migration flows: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/`
  - JCL jobs: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/`
  - Reports: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/`
  - Progress tracking: `{{ANALYSIS_STATUS}}`
  - Task files location: `{{TASKS_BASE_PATH}}`

- **Tool Location**:
  - Legacy analyzer tool: `{{PROJECT_BASE_PATH}}/tools/ACM-TOOLS/`

## Objective

Execute the legacy_analyzer tool on the provided source code directory to perform comprehensive static code analysis, dependency extraction, complexity calculation, migration flow building, and generate all required outputs for migration planning.

## Instructions

### Step 1: Verify Prerequisites

1. Ensure the legacy_analyzer tool is available:
   ```bash
   cd {{PROJECT_BASE_PATH}}/tools/ACM-TOOLS
   python3 -m tools.legacy_analyzer --help
   ```

2. Verify the source code directory exists and contains analyzable files:
   - Supported languages: COBOL, JCL, PL/I, Natural, REXX, RPG, Assembler, BMS
   - Supported extensions: `.cbl`, `.cob`, `.jcl`, `.pli`, `.nsp`, `.rpg`, `.asm`, `.bms`, etc.
   - Source directory: `{{SOURCE_CODE}}`

3. Ensure output directory is writable or will be created:
   - Output directory: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}`

### Step 2: Run Complete Analysis

Execute the configurable analysis script from the tools directory:

```bash
cd {{PROJECT_BASE_PATH}}/tools/ACM-TOOLS
./scripts/run_configurable_analysis.sh \
  "{{SOURCE_CODE}}" \
  "{{SOURCE_CODE_ANALYSIS_OUTPUT}}" \
  "{{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db"
```

**What this does:**
- Scans all source files in `{{SOURCE_CODE}}`
- Performs static code analysis (inventory, dependencies, complexity)
- Detects entry points (CICS transactions, JCL jobs, inferred)
- Builds migration flows with dependency analysis
- Exports flows with multiple sorting strategies
- Exports JCL jobs with multiple sorting strategies
- Generates comprehensive reports

### Step 3: Verify Results

After analysis completes, verify the following outputs exist:

#### Required Outputs

1. **Database**: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db`
   - Contains all analysis data in SQLite format
   - Tables: `inventory`, `artifact_dependencies`, `migration_flows`, `inventory_cics`, `inventory_programs`, `inventory_jcl`

2. **Entry Points**: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points.json`
   - JSON format with all detected entry points
   - Includes CICS transactions, JCL jobs, and inferred entry points
   - Fields: `program_name`, `entry_type`, `confidence`, `source`, `description`

3. **Entry Points CSV**: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/exports/entry_points.csv`
   - CSV export of entry points for spreadsheet analysis

4. **Entry Points Report**: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/entry_points.txt`
   - Human-readable text report of entry points

5. **Migration Flows** (6 sorting strategies):
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/migration_flows.json` - Default (symlink to complexity_asc)
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/flows_by_complexity_asc.json` - Simplest first (Phase 1)
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/flows_by_complexity_desc.json` - Most complex first (High value)
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/flows_by_independence.json` - Minimal dependencies (Parallel)
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/flows_by_dependencies.json` - Foundational first
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/flows_by_name.json` - Alphabetical
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/flows_database_order.json` - No sorting

6. **JCL Jobs** (4 sorting strategies):
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/jobs.json` - Default (symlink to jobs_by_type)
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/jobs_by_name.json` - Alphabetical
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/jobs_by_type.json` - APPLICATION first (Phased migration)
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/jobs_by_dependencies.json` - Execution order
   - `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/jobs_by_complexity.json` - Most complex first

7. **Summary Report**: `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.txt`
   - Inventory statistics (total artifacts, by language)
   - Dependency statistics (total dependencies, by type)
   - CICS resources (by resource type)
   - Program counts
   - Migration flow counts (by complexity tier)

### Step 4: Access Analysis Results

#### View Summary Report
```bash
cat {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.txt
```

#### View Entry Points
```bash
cat {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/entry_points.txt
```

#### View Migration Flows (JSON)
```bash
cat {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/migration_flows.json | python3 -m json.tool | less
```

#### Query Database Directly
```bash
sqlite3 {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db

# Example queries:
SELECT COUNT(*) FROM inventory;
SELECT language, COUNT(*) FROM inventory GROUP BY language;
SELECT * FROM migration_flows LIMIT 5;
SELECT * FROM artifact_dependencies WHERE source_name = 'PROGRAM_NAME';
```

#### Export Custom Reports
```bash
cd {{PROJECT_BASE_PATH}}/tools/ACM-TOOLS

# Export specific flows
python3 -m tools.legacy_analyzer migration export-flows \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/custom_flows.json \
  --complexity LOW \
  --sort complexity-asc

# Export entry points in different format
python3 -m tools.legacy_analyzer flow entry-points \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --format markdown \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points.md
```

## Output Structure

```
{{SOURCE_CODE_ANALYSIS_OUTPUT}}/
├── analysis.db                              # SQLite database with all analysis data
├── entry_points.json                        # Entry points (JSON)
├── flows/                                   # Migration flows
│   ├── migration_flows.json                 # Default (symlink)
│   ├── flows_by_complexity_asc.json         # Simplest first ⭐ Recommended for Phase 1
│   ├── flows_by_complexity_desc.json        # Most complex first
│   ├── flows_by_independence.json           # Minimal dependencies
│   ├── flows_by_dependencies.json           # Foundational first
│   ├── flows_by_name.json                   # Alphabetical
│   └── flows_database_order.json            # No sorting
├── jobs/                                    # JCL jobs
│   ├── jobs.json                            # Default (symlink)
│   ├── jobs_by_name.json                    # Alphabetical
│   ├── jobs_by_type.json                    # APPLICATION first ⭐ Recommended
│   ├── jobs_by_dependencies.json            # Execution order
│   └── jobs_by_complexity.json              # Most complex first
├── exports/                                 # CSV exports
│   └── entry_points.csv                     # Entry points (CSV)
├── reports/                                 # Text reports
│   ├── entry_points.txt                     # Entry points (text)
│   └── analysis_summary.txt                 # Summary report ⭐ Start here
└── temp/                                    # Temporary files
    └── generate_summary.py                  # Summary generator script
```

## Migration Flow Schema

Each flow in `migration_flows.json` contains:

```json
{
  "flow_id": "FLOW_001",
  "name": "Transaction: ACCT - Account Management",
  "entry_point": {
    "program": "COACTUPC",
    "types": [
      {
        "type": "CICS_TRANSACTION",
        "callers": [
          {
            "source": "ACCT",
            "metadata": {
              "resource_type": "TRANSACTION",
              "status": "ENABLED"
            }
          }
        ]
      }
    ],
    "primary_type": "CICS_TRANSACTION"
  },
  "scope": {
    "programs": [
      {"name": "COACTUPC", "is_utility": false},
      {"name": "COCOM01C", "is_utility": false}
    ],
    "copybooks": ["COCOM01Y", "COTTL01Y"],
    "datasets": ["ACCTDAT", "CUSTDAT"]
  },
  "interfaces": {
    "inbound": [],
    "outbound": []
  },
  "data_operations": {
    "databases": [
      {
        "type": "VSAM",
        "operation": "READ",
        "target": "ACCTDAT",
        "program": "COACTUPC"
      }
    ],
    "datasets": []
  },
  "complexity": {
    "total_programs": 2,
    "total_lines": 1250,
    "cyclomatic_complexity": 45,
    "composite_score": 22.25,
    "tier": "MEDIUM"
  },
  "dependencies": {
    "required_flows": ["FLOW_002", "FLOW_003"],
    "dependent_flows": []
  },
  "invoked_by_jobs": []
}
```

## Key Analysis Outputs Explained

### 1. Entry Points
- **ONLINE**: CICS transactions (from CSD or inferred)
- **BATCH**: JCL job entry points
- **INFERRED**: Programs with no callers (potential entry points)
- **Confidence**: EXPLICIT (from metadata) or INFERRED (from code analysis)

### 2. Migration Flows
- **Flow ID**: Unique identifier for each flow
- **Entry Point**: Starting point (transaction, job, or inferred)
- **Scope**: All programs, copybooks, and datasets in the flow
- **Complexity**: Metrics for migration effort estimation
- **Dependencies**: Required flows (must migrate first) and dependent flows

### 3. Complexity Tiers
- **LOW**: Composite score < 10 (simple, good for Phase 1)
- **MEDIUM**: Composite score 10-20 (moderate complexity)
- **HIGH**: Composite score ≥ 20 (complex, high value)

### 4. JCL Jobs
- **APPLICATION**: Jobs that execute custom programs
- **INFRASTRUCTURE**: Jobs that only run utilities (IDCAMS, IEFBR14, etc.)
- **hasCustomCode**: Boolean indicating if job contains application logic

## Error Handling

### Common Issues and Solutions

#### Issue 1: Source Directory Not Found
```
Error: Source directory not found: {{SOURCE_CODE}}
```
**Solution**: Verify the source directory path is correct and accessible

#### Issue 2: No Files Found
```
Warning: No source files found in directory
```
**Solution**: Check that the directory contains supported file types (.cbl, .jcl, .pli, etc.)

#### Issue 3: Database Creation Failed
```
Error: Cannot create database at {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db
```
**Solution**: Ensure the output directory exists and is writable, or the database parent directory exists

#### Issue 4: Analysis Fails Mid-Process
```
Error: Analysis failed at step X
```
**Solution**: Check the error message, verify source code is valid, check disk space

### Validation Checks

After analysis, verify:

1. **Database exists and is not empty**:
   ```bash
   ls -lh {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db
   sqlite3 {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db "SELECT COUNT(*) FROM inventory;"
   ```

2. **All output directories created**:
   ```bash
   ls -la {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/
   ls -la {{SOURCE_CODE_ANALYSIS_OUTPUT}}/jobs/
   ls -la {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/
   ```

3. **JSON files are valid**:
   ```bash
   python3 -m json.tool {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/migration_flows.json > /dev/null
   echo "✓ Valid JSON"
   ```

4. **Summary report contains data**:
   ```bash
   grep "Total Artifacts:" {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.txt
   ```

## Advanced Usage

### Custom Analysis Options

For more control, use the legacy_analyzer CLI directly from the tools directory:

```bash
cd {{PROJECT_BASE_PATH}}/tools/ACM-TOOLS

# Step 1: Analyze source code
python3 -m tools.legacy_analyzer analyze \
  --source-dir {{SOURCE_CODE}} \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --complexity

# Step 2: Detect entry points
python3 -m tools.legacy_analyzer flow entry-points \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --use-metadata \
  --format json \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points.json

# Step 3: Build migration flows
python3 -m tools.legacy_analyzer migration build-flows \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --utility-threshold 5

# Step 4: Export flows with custom filters
python3 -m tools.legacy_analyzer migration export-flows \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/custom_flows.json \
  --complexity LOW MEDIUM \
  --sort complexity-asc \
  --extended-scope
```

### Filtering and Customization

```bash
cd {{PROJECT_BASE_PATH}}/tools/ACM-TOOLS

# Export only LOW complexity flows
python3 -m tools.legacy_analyzer migration export-flows \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/low_complexity_flows.json \
  --complexity LOW

# Export specific flows by ID
python3 -m tools.legacy_analyzer migration export-flows \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/selected_flows.json \
  --flow-ids FLOW_001 FLOW_002 FLOW_003

# Export flows without extended scope (minimal)
python3 -m tools.legacy_analyzer migration export-flows \
  --db {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db \
  --output {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/minimal_flows.json \
  --sort name
```

## Success Criteria

✅ **Analysis Complete** when:
1. Database file exists and contains data
2. All output directories created (flows/, jobs/, reports/, exports/)
3. Entry points detected and exported in 3 formats (JSON, CSV, text)
4. Migration flows exported with 6 sorting strategies
5. JCL jobs exported with 4 sorting strategies
6. Summary report generated with statistics
7. No fatal errors in console output

✅ **Results Valid** when:
1. JSON files parse without errors
2. CSV files have proper headers and data
3. Database queries return expected data
4. Summary report shows non-zero counts
5. Flow dependencies are logical and complete
6. Entry points map to actual source files

## Next Steps

After successful analysis:

1. **Review Summary Report**: Start with `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.txt`
2. **Examine Entry Points**: Review `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/entry_points.txt`
3. **Plan Migration Phases**:
   - Phase 1: Use `flows_by_complexity_asc.json` (simplest first)
   - Phase 2: Use `flows_by_independence.json` (parallel migration)
   - Phase 3: Use `flows_by_complexity_desc.json` (high value)
4. **Analyze Dependencies**: Review `flows_by_dependencies.json` for foundational flows
5. **Job Orchestration**: Review `jobs_by_type.json` for batch processing
6. **Custom Queries**: Use SQLite to query specific patterns or relationships

## Quality Criteria

### Completeness
- [ ] All source files scanned and inventoried
- [ ] All dependencies extracted and stored
- [ ] All entry points detected (CICS, JCL, inferred)
- [ ] All migration flows built with dependencies
- [ ] All JCL jobs categorized and sorted
- [ ] All reports generated

### Accuracy
- [ ] Dependency relationships are correct
- [ ] Entry point detection is accurate
- [ ] Flow complexity calculations are consistent
- [ ] Job classifications are correct (APPLICATION vs INFRASTRUCTURE)

### Consistency
- [ ] All output files follow expected format
- [ ] Database schema is complete
- [ ] JSON files are valid and parseable
- [ ] CSV files have proper structure
- [ ] Cross-references between outputs are accurate

## Documentation References

- **Complete Analysis Guide**: `{{PROJECT_BASE_PATH}}/tools/ACM-TOOLS/docs/COMPLETE_ANALYSIS_GUIDE.md`
- **CLI Reference**: `{{PROJECT_BASE_PATH}}/tools/ACM-TOOLS/docs/CLI_REFERENCE.md`
- **Migration Planning**: `{{PROJECT_BASE_PATH}}/tools/ACM-TOOLS/docs/MIGRATION_WORKFLOW_GUIDE.md`
- **API Reference**: `{{PROJECT_BASE_PATH}}/tools/ACM-TOOLS/docs/API_REFERENCE.md`
- **Configurable Script**: `{{PROJECT_BASE_PATH}}/tools/ACM-TOOLS/scripts/README_CONFIGURABLE_ANALYSIS.md`
