# Run Workpackage Analysis Tool

## Objective
Execute the workpackage analysis tool to generate migration workpackages and roadmap based on business flow analysis results.

## Prerequisites
- Phase 1 analysis must be completed with business flows and dependency data available
- Python environment with required dependencies (pandas, json, logging, csv)
- Input data files from Phase 1 analysis must exist

## Tool Location
**Primary Tool**:  `{{WORKPACKAGE_ANALYZER_TOOL}}`
**Validation Tool**: `{{ACM_TEMPLATE_VALIDATOR}}` : used to validate the results against the templates

## Input Data Requirements
The tool expects the following input files from Phase 1 analysis:
- **Business Flows**: `{{SOURCE_CODE_ANALYSIS_BUSINESS_FLOW}}`
- **Dependency Analysis**: `{{SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}`

## Execution Instructions

### Step 1: Verify Prerequisites
First, check that all required input files exist:

```bash
# Check if Phase 1 outputs exist
ls -la {{SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}
```

### Step 2: Create Output Directories
Ensure all required output directories exist:

```bash
# Create output directories if they don't exist
mkdir -p {{WORKPACKAGE_BASE_PATH}}/reports
mkdir -p {{WORKPACKAGE_BASE_PATH}}/progress
mkdir -p {{WORKPACKAGE_BASE_PATH}}/logs
```

### Step 3: Run the Workpackage Analysis Tool
Execute the main analysis tool:

```bash
cd PROJECT_BASE_PATH
python {{WORKPACKAGE_ANALYZER_TOOL}}
```

### Step 4: Validate Outputs
Run the validation tool to ensure all outputs are correct:

```bash
python {{ACM_TEMPLATE_VALIDATOR}}
```

### Step 5: Verify Completion
Check that all expected output files have been created:

```bash
# Check primary outputs
ls -la {{WORKPACKAGE_ANALYSIS_TABLE}}
ls -la {{WORKPACKAGE_ANALYSIS_DEPENDENCIES}}
ls -la {{WORKPACKAGE_REPORT}}
ls -la {{WORKPACKAGE_PROGRESS}}
ls -la {{WORKPACKAGE_ANALYSIS_ERRORS}}
ls -la {{WORKPACKAGE_ROADMAP}}

```

## Expected Outputs

### Primary Deliverables
1. **Workpackage Analysis Table** - `{{WORKPACKAGE_ANALYSIS_TABLE}}`
   - CSV file with workpackage details, priority scores, and flow information

2. **Workpackage Dependencies** - `{{WORKPACKAGE_ANALYSIS_DEPENDENCIES}}`
   - JSON file with workpackage relationships and phase organization

3. **Migration Roadmap** - `{{WORKPACKAGE_ROADMAP}}`
   - Markdown file with comprehensive migration roadmap and phase breakdown

4. **Workpackage Definition Report** - `{{WORKPACKAGE_REPORT}}`
   - Detailed report with methodology, workpackage definitions, and analysis

5. **Progress Tracking** - `{{WORKPACKAGE_PROGRESS}}`
   - JSON file tracking execution status and completion metrics

### Log Files
- **Error Log** - `{{WORKPACKAGE_ANALYSIS_ERRORS}}` (if errors occur)

## Tool Functionality Overview

### Priority Calculation Formula
The tool implements the following priority scoring formula:
```
Priority = (Modules × 2) + (Common Modules × 3) + (Complexity × 0.5) + (Pre-existent × 1) + Complete Flow Bonus (-5) + Simple Flow Bonus
```

Where:
- **Modules**: Total number of modules in the flow
- **Common Modules**: Number of modules used by multiple flows
- **Complexity**: Sum of complexity scores for all modules in the flow
- **Pre-existent**: Number of modules already included in higher priority workpackages
- **Complete Flow Bonus**: -5 points for flows that are complete (entry point to database)
- **Simple Flow Bonus**: -3 points for flows with ≤3 modules, -1 point for flows with ≤5 modules

### Processing Steps
1. **Load Phase 1 Data**: Reads business flows and dependency analysis results
2. **Calculate Complexity Metrics**: Computes module counts, complexity scores, and common module usage
3. **Apply Priority Formula**: Calculates priority scores for all flows
4. **Sort and Create Workpackages**: Orders flows by priority and creates workpackages
5. **Resolve Dependencies**: Identifies and resolves workpackage dependencies
6. **Generate Outputs**: Creates all required deliverable files
7. **Validate Results**: Ensures data integrity and completeness

## Error Handling

### Common Issues and Solutions

#### 1. Missing Input Files
**Error**: Input files from Phase 1 not found
**Solution**: Verify Phase 1 analysis has been completed and files exist in expected locations

#### 2. Permission Issues
**Error**: Cannot write to output directories
**Solution**: Check directory permissions and create directories if needed

#### 3. Data Format Issues
**Error**: Invalid data format in input files
**Solution**: Verify Phase 1 outputs are in correct format and not corrupted

#### 4. Python Dependencies
**Error**: Missing required Python packages
**Solution**: Install required packages: `pip install pandas`

### Troubleshooting Commands
```bash
# Check Python version and packages
python --version
python -c "import pandas, json, csv, logging; print('All required packages available')"

# Check file permissions
ls -la {{PROJECT_BASE_PATH}}/output/migration/
ls -la {{PROJECT_BASE_PATH}}/output/tools/phase_2_workpackage/

# View recent log entries
tail -20 {{PROJECT_BASE_PATH}}/output/migration/progress/workpackage_analyzer.log
```

## Success Criteria

### Completion Indicators
- All 5 primary output files are created
- Progress status shows "COMPLETED" in `{{PROJECT_BASE_PATH}}/output/migration/progress/02-workpackage-status.json`
- No errors in the execution log
- Validation tool runs successfully without issues

### Quality Checks
- All business flows from Phase 1 are assigned to workpackages
- Priority scores are calculated correctly
- Workpackage dependencies form a valid directed acyclic graph (DAG)
- Migration roadmap includes all workpackages in logical phases
- Output files match expected schemas and formats

## Post-Execution Actions

### Verification Steps
1. **Review Progress Status**: Check that status is "COMPLETED" with no errors
2. **Validate Output Count**: Ensure all expected flows are processed
3. **Check File Sizes**: Verify output files contain substantial data (not empty)
4. **Review Sample Data**: Spot-check a few workpackages for correctness
5. **Validate Dependencies**: Ensure dependency graph is logical and complete

### Next Steps
After successful completion:
1. Review the Migration Roadmap for strategic planning
2. Use the Workpackage Analysis Table for detailed implementation planning
3. Proceed to Phase 3 of the migration framework
4. Archive the workpackage definition outputs for future reference

## Notes
- The tool is designed to be idempotent - running it multiple times should produce consistent results
- All file paths are absolute to ensure consistent execution regardless of working directory
- The tool includes comprehensive logging for debugging and audit purposes
- Output files are formatted for both human readability and machine processing
