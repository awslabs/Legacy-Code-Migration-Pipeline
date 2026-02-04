# Deliverable Validator

The deliverable validator ensures that all deliverable files in the project output have corresponding templates and validates their content structure against those templates.

## Integration with Orchestration Architecture

The validator can be used at multiple points in the orchestration workflow:

1. **Specialist Self-Check**: Specialists can run validation before reporting completion
2. **Reviewer Validation**: Reviewers can use validation as part of quality criteria checks
3. **Team Supervisor Verification**: Supervisors can verify deliverables before creating review tasks
4. **Phase Gate**: Migration Supervisor can validate all phase outputs before proceeding
5. **Continuous Integration**: Automated validation in CI/CD pipelines

The iterative review process ensures deliverables pass validation before phase completion.

## Usage

### Python Script
```bash
# Run from project root
python3 acm/deliverable_validator.py

# Run with custom project path
python3 acm/deliverable_validator.py --project-path /path/to/project

# Quiet mode (only show warnings)
python3 acm/deliverable_validator.py --quiet
```

### Shell Script (Recommended)
```bash
# Run from project root (script will be in project root)
./validate_deliverables.sh

# Quiet mode
./validate_deliverables.sh --quiet
```

## What it does

1. Scans all files in the `output/` directory recursively
2. Checks if each deliverable has a corresponding template in `templates/`
3. **Content Validation** for supported file types:
   - **JSON files**: Validates that the JSON structure (keys, types, nesting) matches the template
   - **Markdown files**: Validates that headers (levels and text) match the template structure
   - **CSV files**: Validates that column headers match the template headers
4. Reports deliverables that don't have matching templates as errors
5. Reports deliverables with content validation issues as warnings
6. Provides a comprehensive summary of validation results

**Use Cases in Orchestration:**
- **Specialists**: Run before reporting task completion
- **Reviewers**: Include in quality criteria validation
- **Team Supervisors**: Verify deliverables before review delegation
- **Migration Supervisor**: Validate phase outputs before proceeding

## Output

- **Full Report**: Shows available templates, fully valid deliverables, content validation errors, and deliverables without templates
- **Quiet Mode**: Only shows deliverables with validation issues (missing templates or content errors)
- **Console Indicators**: 
  - ✅ Fully valid deliverables (template exists and content matches)
  - ⚠️ Content validation errors (template exists but content doesn't match)
  - ❌ Missing template for deliverable
- **Detailed Error Messages**: Specific information about what doesn't match in the content

## Deliverable Matching

Deliverables are matched by filename only (not path). For example:
- `output/analysis/database/progress/DB_Analysis_Status.json` → `templates/DB_Analysis_Status.json`
- `output/analysis/source_code/reports/Source_Analysis_Report.md` → `templates/Source_Analysis_Report.md`

## Content Validation Details

### JSON Validation
- Checks that all required keys from the template are present
- Validates that data types match (string, number, boolean, array, object)
- Reports missing keys, extra keys, and type mismatches
- Recursively validates nested objects and arrays

### Markdown Validation  
- Extracts all headers (# ## ### etc.) from both files
- Validates that header levels match exactly
- Validates that header text matches exactly
- Reports missing headers, extra headers, level mismatches, and text differences

### CSV Validation
- Reads the first row as headers from both files
- Validates that all template headers are present
- Reports missing headers, extra headers, and header count mismatches
- Case-sensitive header matching

## Example Output

```
⚠️  analysis/database/progress/DB_Analysis_Status.json (content issues)
    • Type mismatch at root.totalDatabaseTables: expected str, got int
    • Extra key 'extraField' at root

⚠️  analysis/database/reports/DB_Source_Analysis_Report.md (content issues)  
    • Header count mismatch: expected 6, got 4
    • Header 1 text mismatch: expected 'DB Source Code Analysis Report', got 'Database Analysis Report'
```