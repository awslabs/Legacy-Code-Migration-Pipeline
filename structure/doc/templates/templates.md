# Templates Documentation

This directory contains standardized templates used throughout the migration process. These templates ensure consistency across projects and provide structured formats for reports, tracking, and analysis outputs.

## Integration with Orchestration Architecture

Templates are integrated into the orchestration workflow at multiple levels:

1. **Phase Prompts**: Reference templates using `{{TEMPLATES_BASE_PATH}}` parameters
2. **Task Files**: Include resolved template paths for each deliverable
3. **Specialists**: Use templates as structure guides when producing deliverables
4. **Reviewers**: Validate deliverables against template structure

**Example Flow:**
```
Phase Prompt: {{TEMPLATES_BASE_PATH}}/Cobol_Source_Analysis_Report.md
     ↓
Team Supervisor resolves to: /project/templates/Cobol_Source_Analysis_Report.md
     ↓
Task File includes: Template: /project/templates/Cobol_Source_Analysis_Report.md
     ↓
Specialist uses template to structure analysis report
     ↓
Reviewer validates report structure matches template
```

For more information on how templates flow through the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md)

## Available Templates

### Analysis Templates

#### Source Code Analysis
- **Source_Analysis_Report.md** - Comprehensive source code analysis report template (language-specific: Cobol, Natural, ASM)
- **Analysis_Status.json** - Unified progress tracking for all analysis phases (source code, database, workpackage)
- **Dependency_Analysis_Table.csv** - Unified dependencies between source code modules across all languages
- **Business_Flows.json** - Unified business flow documentation template for all languages
- **Module_Classifications.json** - Unified module categorization template for all languages
- **Analysis_Errors.json** - Unified error tracking for all analysis activities

#### Database Analysis
- **DB_Source_Analysis_Report.md** - Database analysis report template

### Workpackage Templates

#### Planning and Tracking
- **Workpackage_Definition_Report.md** - Detailed workpackage specifications
- **Workpackage_Planning.json** - Priority scores, workpackage assignments, phase groupings, and migration sequence
- **Workpackage_Status.json** - Progress tracking for workpackages

#### Migration Planning
- **Migration_Roadmap.md** - High-level migration roadmap with phases and dependencies

## Template Usage

Templates are automatically copied to your project when using `create_project.py`. All `{{PARAMETER}}` placeholders in templates are replaced with actual paths based on your project configuration.

### In the Orchestration Architecture

**Team Supervisors:**
- Read template paths from phase prompts
- Resolve `{{PARAMETERS}}` to absolute paths
- Include resolved template paths in task files

**Specialists:**
- Receive template paths in task files
- Use templates as structure guides
- Populate templates with analysis/generation results
- Save deliverables at specified paths

**Reviewers:**
- Receive template paths in review task files
- Validate deliverable structure matches template
- Check all required sections are present
- Verify content follows template format

### Customization

You can modify templates to fit your specific project needs. The framework will use your customized versions for new projects created after modification.

When customizing templates:
- Maintain the overall structure for validation compatibility
- Keep required sections that reviewers check
- Document any deviations from standard templates
- Update validation criteria if template structure changes

### Path Resolution

Templates use the path configuration system defined in `config/paths.cfg`. This ensures all file references are correctly resolved for your specific project structure.

The resolution happens at multiple levels:
1. **Project Creation**: `create_project.py` resolves paths in templates
2. **Phase Prompts**: Templates referenced with `{{PARAMETERS}}`
3. **Task Files**: Team supervisors resolve to absolute paths
4. **Agent Execution**: Specialists receive fully resolved paths