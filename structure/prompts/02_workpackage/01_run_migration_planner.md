# Phase 2.1: Run Migration Planner Tool

## Objective

Execute the migration planner tool to analyze migration flows and generate workpackage planning with priorities and phase assignments.

## Instructions

### Run the Migration Planner

Execute the migration planner script:

```bash
cd {{PROJECT_BASE_PATH}}/tools/acm-tools
bash scripts/run_migration_planner.sh \
   {{SOURCE_CODE_ANALYSIS_OUTPUT}}/flows \
   {{WORKPACKAGE_BASE_PATH}}
```

The tool will automatically:
- Read the analysis database and migration flows
- Calculate workpackage priorities and complexity
- Assign flows to migration phases
- Generate planning documents and reports
- Display any errors in the console

### Verify Results

Check that the planning completed successfully:

```bash
# View the workpackage planning
cat {{WORKPACKAGE_PLANNING}}

# View the migration roadmap
cat {{WORKPACKAGE_ROADMAP}}

# View the workpackage definition report
cat {{WORKPACKAGE_DEFINITION_REPORT}}
```

## Expected Outputs

After successful planning, you'll find:

- `Workpackage_Planning.json` - Detailed workpackage plan with priorities and phases
- `reports/Workpackage_Definition_Report.md` - Human-readable workpackage definitions
- `reports/Migration_Roadmap.md` - Migration roadmap with timeline and phases
- `progress/Workpackage_Status.json` - Status tracking for workpackage execution

## Troubleshooting

If the planning fails, check the console output for error messages. Common issues:

- Input directory doesn't contain analysis results
- Analysis database is missing or corrupted
- Output directory is not writable
- No migration flows found in analysis

For detailed documentation, see: `{{PROJECT_BASE_PATH}}/tools/acm-tools/scripts/README_MIGRATION_PLANNER.md`
