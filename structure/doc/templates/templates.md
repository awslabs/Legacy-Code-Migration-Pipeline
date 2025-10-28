# Templates Documentation

This directory contains standardized templates used throughout the migration process. These templates ensure consistency across projects and provide structured formats for reports, tracking, and analysis outputs.

## Available Templates

### Analysis Templates

#### Source Code Analysis
- **Source_Analysis_Report.md** - Comprehensive source code analysis report template
- **Source-Analysis-Status.json** - Progress tracking for source code analysis
- **Source_Dependency_Table.csv** - Dependencies between source code modules
- **Source_Business_Flows.json** - Business flow documentation template
- **Cobol_Module_Classifications.json** - COBOL module categorization template
- **Cobol_Source-Analysis-Errors.json** - Error tracking for COBOL analysis

#### Database Analysis
- **DB_Source_Analysis_Report.md** - Database analysis report template
- **DB_Analysis_Status.json** - Progress tracking for database analysis

### Workpackage Templates

#### Planning and Tracking
- **Workpackage_Analysis_Table.csv** - Workpackage breakdown and analysis
- **Workpackage_Definition_Report.md** - Detailed workpackage specifications
- **Workpackage_Dependencies.json** - Inter-workpackage dependencies
- **Workpackage_Status.json** - Progress tracking for workpackages
- **Workpackage_Analysis_Errors.json** - Error tracking for workpackage analysis

#### Migration Planning
- **Migration_Roadmap.md** - High-level migration roadmap with phases and dependencies

## Template Usage

Templates are automatically copied to your project when using `create_project.py`. All `{{PARAMETER}}` placeholders in templates are replaced with actual paths based on your project configuration.

### Customization

You can modify templates to fit your specific project needs. The framework will use your customized versions for new projects created after modification.

### Path Resolution

Templates use the path configuration system defined in `config/paths.cfg`. This ensures all file references are correctly resolved for your specific project structure.