# Configurable Analysis Script

## Overview

`run_configurable_analysis.sh` is a flexible version of `run_carddemo_analysis.sh` that accepts configurable input and output parameters. This allows you to analyze any codebase without modifying the script.

## Important Notes

⚠️ **This script uses POSITIONAL ARGUMENTS, not named flags**

- ✅ CORRECT: `./script.sh /path/to/source /path/to/output`
- ❌ INCORRECT: `./script.sh --source-dir /path/to/source --output-dir /path/to/output`

⚠️ **This script must be run from the repository root directory** or it will automatically change to the repository root where the `tools/` directory is located.

## Usage

```bash
./scripts/run_configurable_analysis.sh <source_dir> <output_dir> [database_path]
```

### Parameters

| Position | Parameter | Required | Description |
|----------|-----------|----------|-------------|
| 1 | `source_dir` | Yes | Directory containing source code to analyze |
| 2 | `output_dir` | Yes | Directory for output files (will be created if it doesn't exist) |
| 3 | `database_path` | No | Path to SQLite database file (default: `<output_dir>/analysis.db`) |

**Note**: `TEMP_DIR` is automatically derived as `<output_dir>/temp` and is not a parameter.

## Examples

### Example 1: Analyze CardDemo V2

```bash
# Run from repository root
./scripts/run_configurable_analysis.sh \
  ./examples/code/cobol/carddemoV2/app \
  ./results/carddemo_v2_analysis

# Database will be created at: ./results/carddemo_v2_analysis/analysis.db
```

### Example 2: Analyze CardDemo V2 with Custom Database Path

```bash
./scripts/run_configurable_analysis.sh \
  ./examples/code/cobol/carddemoV2/app \
  ./results/carddemo_v2_analysis \
  ./databases/carddemo.db
```

### Example 3: Analyze PL/I CardDemo

```bash
./scripts/run_configurable_analysis.sh \
  ./examples/code/pli/carddemo \
  ./results/pli_carddemo_analysis
```

### Example 4: Analyze Natural N-One

```bash
./scripts/run_configurable_analysis.sh \
  ./examples/code/natural/n-one \
  ./results/natural_analysis
```

### Example 5: Analyze Custom Project with Absolute Paths

```bash
# If framework-tools is in /Users/kerimman/cardemo/tools/framework-tools
cd /Users/kerimman/cardemo/tools/framework-tools

./scripts/run_configurable_analysis.sh \
  /Users/kerimman/cardemo/input/legacy/legacy_code \
  /Users/kerimman/cardemo/output/analysis/source_code
```

## What It Does

The script performs a complete analysis workflow:

1. **Static Code Analysis**
   - Parses source code (COBOL, JCL, PL/I, Natural, REXX, RPG, Assembler)
   - Extracts dependencies
   - Calculates complexity metrics

2. **Entry Point Detection**
   - Identifies CICS transactions
   - Identifies JCL job entry points
   - Infers entry points from code analysis
   - Exports in JSON, CSV, and text formats

3. **Migration Flow Building**
   - Builds migration flows from analysis data
   - Calculates flow complexity
   - Identifies flow dependencies

4. **Migration Flow Export** (6 sorting strategies)
   - Complexity Ascending (simplest first - recommended for Phase 1)
   - Complexity Descending (most complex first - high value)
   - Independence (minimal dependencies - parallel migration)
   - Dependencies (foundational flows first)
   - Alphabetical (documentation/reference)
   - Database Order (no sorting)

5. **JCL Job Export** (4 sorting strategies)
   - Alphabetical (documentation/reference)
   - By Type (APPLICATION first - phased migration)
   - By Dependencies (execution order)
   - By Complexity (most complex first)

6. **Summary Report Generation**
   - Inventory statistics
   - Dependency statistics
   - CICS resources
   - Program counts
   - Migration flow counts
   - Generated using CLI command: `python -m tools.legacy_analyzer report summary`

## Output Structure

```
<output_dir>/
├── <database_file>                          # SQLite database
├── entry_points/                            # Entry points
│   ├── entry_points.json                    # Entry points (JSON)
│   └── entry_points.md                      # Entry points (Markdown)
├── flows/                                   # Migration flows
│   ├── Business_Flows.json                  # Default (copy of complexity_asc)
│   ├── flows_by_complexity_asc.json         # Simplest first
│   ├── flows_by_complexity_desc.json        # Most complex first
│   ├── flows_by_independence.json           # Minimal dependencies
│   ├── flows_by_dependencies.json           # Foundational first
│   ├── flows_by_name.json                   # Alphabetical
│   └── flows_database_order.json            # No sorting
├── jobs/                                    # JCL jobs
│   ├── jobs.json                            # Default (copy of jobs_by_type)
│   ├── jobs_by_name.json                    # Alphabetical
│   ├── jobs_by_type.json                    # APPLICATION first
│   ├── jobs_by_dependencies.json            # Execution order
│   └── jobs_by_complexity.json              # Most complex first
├── progress/                                # Status tracking
│   └── source_analysis_status.json          # Analysis completion status
└── reports/                                 # Reports
    └── analysis_summary.md                  # Summary report
```

## Differences from run_carddemo_analysis.sh

| Aspect | run_carddemo_analysis.sh | run_configurable_analysis.sh |
|--------|--------------------------|------------------------------|
| Source directory | Hardcoded | Parameter |
| Output directory | Hardcoded | Parameter |
| Database path | Hardcoded | Parameter |
| Temp directory | Hardcoded | Derived from output_dir |
| Use case | CardDemo only | Any project |
| Flexibility | Fixed | Configurable |

## Error Handling

The script will exit with an error if:
- Required parameters are missing
- Source directory doesn't exist
- Any analysis step fails (due to `set -e`)

## Tips

1. **Use absolute paths** for source directories outside the project:
   ```bash
   ./scripts/run_configurable_analysis.sh \
     /absolute/path/to/source \
     ./results/analysis \
     ./results/analysis/project.db
   ```

2. **Organize outputs by project**:
   ```bash
   # Project 1
   ./scripts/run_configurable_analysis.sh \
     ./source/project1 \
     ./results/project1 \
     ./results/project1/project1.db
   
   # Project 2
   ./scripts/run_configurable_analysis.sh \
     ./source/project2 \
     ./results/project2 \
     ./results/project2/project2.db
   ```

3. **Database path convention**: Keep database in output directory for easy cleanup:
   ```bash
   # Good: Database in output directory
   ./results/my_analysis/my_project.db
   
   # Also valid: Database in databases/ directory
   ./databases/my_project.db
   ```

## Viewing Results

After analysis completes, view results using the commands shown in the script output:

```bash
# View summary report (Markdown format)
cat ./results/my_analysis/reports/analysis_summary.md

# Or view with a Markdown viewer
mdless ./results/my_analysis/reports/analysis_summary.md

# View entry points
cat ./results/my_analysis/entry_points/entry_points.md

# View business flows (JSON)
cat ./results/my_analysis/flows/Business_Flows.json | python3 -m json.tool | less

# Query database
sqlite3 ./results/my_analysis/my_project.db
```

### Generate Summary Report Manually

You can also generate the summary report independently using the CLI command:

```bash
# Generate summary report with default output
python -m tools.legacy_analyzer report summary \
  --db ./results/my_analysis/analysis.db

# Generate summary report with custom output path
python -m tools.legacy_analyzer report summary \
  --db ./results/my_analysis/analysis.db \
  --output ./custom/path/summary.md
```

## Integration with Other Tools

This script can be integrated into automated workflows:

```bash
#!/bin/bash
# Batch analysis of multiple projects

projects=(
  "project1:./source/project1"
  "project2:./source/project2"
  "project3:./source/project3"
)

for project in "${projects[@]}"; do
  IFS=':' read -r name source <<< "$project"
  
  echo "Analyzing $name..."
  ./scripts/run_configurable_analysis.sh \
    "$source" \
    "./results/${name}_analysis" \
    "./results/${name}_analysis/${name}.db"
done

echo "All projects analyzed!"
```

## See Also

- `run_carddemo_analysis.sh` - Fixed version for CardDemo
- `run_all_projects_analysis.sh` - Batch analysis of example projects
- `docs/COMPLETE_ANALYSIS_GUIDE.md` - Detailed analysis guide
