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
cat {{SOURCE_CODE_ANALYSIS_OUTPUT}}/reports/analysis_summary.txt

# Verify the database was created
ls -lh {{SOURCE_CODE_ANALYSIS_OUTPUT}}/analysis.db
```

## Expected Outputs

After successful analysis, you'll find:

- `analysis.db` - SQLite database with all analysis data
- `flows/` - Migration flows in various sorting orders
- `jobs/` - JCL jobs categorized and sorted
- `reports/` - Summary and entry points reports
- `exports/` - CSV exports for spreadsheet analysis

## Troubleshooting

If the analysis fails, check the console output for error messages. Common issues:

- Source directory doesn't exist or is empty
- Output directory is not writable
- Invalid source code files


