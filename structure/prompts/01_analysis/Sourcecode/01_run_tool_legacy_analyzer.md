# Phase 1.1: Run Legacy Analyzer Tool

## Objective

Execute the legacy analyzer tool to analyze the source code and generate analysis outputs.

## Instructions

### Run the Analysis

For detailed documentation, see: `{{PROJECT_BASE_PATH}}/tools/acm-tools/scripts/README_CONFIGURABLE_ANALYSIS.md`

Execute the analysis script:

```bash
cd {{PROJECT_BASE_PATH}}/tools/acm-tools
bash scripts/run_configurable_analysis.sh \
  {{SOURCE_CODE}} \
  {{SOURCE_CODE_ANALYSIS_OUTPUT}} 
```

The tool will automatically:
- Create all necessary output directories
- Analyze the source code
- Generate the database, reports, flows, and exports
- Display any errors in the console

### Verify Results

Check that the analysis completed successfully:

```bash
# View the summary report
cat {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.md

# View entry points report (Markdown)
cat {{SOURCE_CODE_ANALYSIS_OUTPUT}}/entry_points/entry_points.md

# Verify the database was created
ls -lh {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db

# Check business flows were generated
ls -lh {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows/Business_Flows.json
```

## Expected Outputs

After successful analysis, you'll find:

### Database
- `analysis.db` - SQLite database with all analysis data

### Entry Points
- `entry_points/entry_points.json` - Entry points in JSON format
- `entry_points/entry_points.md` - Entry points in Markdown format

### Flows (JSON format)
- `flows/Business_Flows.json` - Default business flows (copy of complexity_asc)
- `flows/flows_by_complexity_asc.json` - Flows sorted by complexity (simplest first)
- `flows/flows_by_complexity_desc.json` - Flows sorted by complexity (most complex first)
- `flows/flows_by_independence.json` - Flows with minimal dependencies
- `flows/flows_by_dependencies.json` - Foundational flows first
- `flows/flows_by_name.json` - Alphabetically sorted flows
- `flows/flows_database_order.json` - Flows in database order

### Jobs (JSON format)
- `jobs/jobs.json` - Default JCL jobs (copy of jobs_by_type)
- `jobs/jobs_by_name.json` - Jobs sorted alphabetically
- `jobs/jobs_by_type.json` - Jobs sorted by type (APPLICATION first)
- `jobs/jobs_by_dependencies.json` - Jobs sorted by execution order
- `jobs/jobs_by_complexity.json` - Jobs sorted by complexity

### Reports (Markdown format)
- `reports/analysis_summary.md` - Summary report with inventory and statistics

### Temporary Files
- `temp/` - Temporary files used during analysis (including generate_summary.py)

## Troubleshooting

If the analysis fails, check the console output for error messages. Common issues:

- Source directory doesn't exist or is empty
- Output directory is not writable
- Invalid source code files

