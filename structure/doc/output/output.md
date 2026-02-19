# Output Structure Documentation

This directory contains all generated artifacts, analysis results, and migration deliverables. The output structure is organized by analysis type and includes comprehensive tracking and reporting.

## Integration with Orchestration Architecture

Output paths are configured in `config/paths.cfg` and resolved in the orchestration workflow:

1. **Main Prompt Level**: Migration Supervisor sees all output base paths
2. **Phase Prompt Level**: Team Supervisors see phase-specific output paths with `{{PARAMETERS}}`
3. **Task File Level**: Specialists receive fully resolved absolute paths for each deliverable

This ensures:
- Agents know exactly where to write deliverables
- No path resolution or guessing required
- Consistent file locations across the project
- Easy verification of deliverable production

For more information on path resolution in the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md)

## Directory Structure

### Analysis Results (`analysis/`)

#### Source Code Analysis (`analysis/source_code/`)
- **Dependency Analysis**: Module relationships and dependencies
- **Business Flow Documentation**: Extracted business logic and workflows
- **Classification Results**: Categorization of COBOL modules and components
- **Progress Tracking**: Analysis status and completion metrics
- **Error Logs**: Issues encountered during analysis
- **Reports**: Comprehensive analysis summaries

#### Database Analysis (`analysis/database/`)
- **Schema Analysis**: Database structure and relationships
- **Data Flow Analysis**: Data movement and transformation patterns
- **Generated Source**: Converted database artifacts
- **Progress Tracking**: Database analysis status
- **Reports**: Database migration analysis summaries

### Workpackages (`workpackages/`)

Contains migration workpackage definitions and tracking:

#### Core Workpackage Files
- **Analysis Table**: Detailed workpackage breakdown and specifications
- **Dependencies**: Inter-workpackage relationships and constraints
- **Migration Roadmap**: Phased migration plan with timelines

#### Tracking and Reporting
- **Progress Tracking**: Workpackage completion status
- **Reports**: Detailed workpackage specifications and progress
- **Error Logs**: Issues and resolutions for workpackage execution

#### Tools and Utilities
- **Analysis Tools**: Custom tools generated for workpackage processing
- **Validation Scripts**: Quality assurance and validation utilities

## File Types and Formats

### Structured Data Files
- **JSON**: Configuration, status tracking, and structured analysis results
- **Markdown**: Human-readable reports and documentation

### Generated Code
- **Target Platform Code**: Converted legacy code in modern languages
- **Configuration Files**: Target system configuration and setup
- **Database Scripts**: DDL and migration scripts for target databases

### Reports and Documentation
- **Analysis Reports**: Comprehensive analysis summaries
- **Migration Plans**: Detailed migration strategies and timelines
- **Progress Reports**: Status updates and completion metrics

## Quality Assurance

### Validation Framework
All outputs are validated using the ACM (Application Configuration Management) framework within the orchestration architecture:
- **Deliverable Validation**: Ensures all required outputs are present
- **Format Validation**: Verifies file formats and structure
- **Content Validation**: Checks for completeness and consistency
- **Cross-Reference Validation**: Ensures traceability between inputs and outputs
- **Review Validation**: Reviewer agents validate deliverables against quality criteria in iterative cycles

### Iterative Quality Assurance
The orchestration architecture includes built-in quality assurance:
- Team supervisors orchestrate review cycles within each phase
- Specialists produce deliverables
- Reviewers validate against quality criteria
- If issues found, supervisors create remediation tasks
- Iteration continues until reviewer approves
- Only then does phase complete

### Tracking and Metrics
- **Progress Tracking**: Real-time status of all migration activities
- **Error Tracking**: Comprehensive logging of issues and resolutions
- **Quality Metrics**: Measurements of analysis completeness and accuracy
- **Iteration Tracking**: Number of review cycles per deliverable

## Integration Points

### Template Integration
Outputs are generated using standardized templates from the `templates/` directory, ensuring consistency across projects.

### Configuration Management
All output paths are configurable via `config/paths.cfg`, allowing for flexible project organization.

### Tool Integration
Generated tools and utilities integrate with the overall framework for seamless workflow execution.