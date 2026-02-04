# ACM (Application Configuration Management) Framework

The ACM framework provides quality assurance and validation tools for the legacy code migration process. It ensures that all deliverables meet specified standards and maintains consistency across migration projects.

## Integration with Orchestration Architecture

The ACM framework integrates with the 3-layer orchestration architecture at multiple points:

1. **Specialist Level**: Specialists can self-validate deliverables before reporting completion
2. **Reviewer Level**: Reviewers use ACM validation as part of their quality criteria checks
3. **Team Supervisor Level**: Supervisors can verify deliverables exist and are valid before proceeding
4. **Migration Supervisor Level**: Can validate entire phase outputs before moving to next phase

The iterative review process orchestrated by team supervisors ensures deliverables pass both ACM validation and reviewer quality checks before phase completion.

For more information on the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md)

## Framework Overview

The ACM framework is built around the principle of template-driven validation, where every deliverable in the migration process has a corresponding template that defines its expected structure and content.

### Core Components

#### Deliverable Validator
The primary tool for ensuring migration quality and completeness. See [Deliverable Validator Documentation](deliverable_validator.md) for detailed usage instructions.

**Key Features:**
- **Template Matching**: Ensures every output has a corresponding template
- **Content Validation**: Validates structure and format of JSON, Markdown, and CSV files
- **Comprehensive Reporting**: Detailed validation results with specific error messages
- **Integration Ready**: Designed for CI/CD pipeline integration

#### Validation Framework
The underlying framework that supports:
- **Multi-format Support**: JSON, Markdown, CSV validation with extensible architecture
- **Recursive Validation**: Deep validation of nested structures and hierarchies
- **Error Classification**: Distinguishes between missing templates and content issues
- **Batch Processing**: Validates entire project outputs efficiently

## Quality Assurance Process

### Validation Levels

#### Level 1: Template Existence
- Verifies that every deliverable has a corresponding template
- Ensures no outputs are generated without proper specification
- Identifies missing template definitions

#### Level 2: Structure Validation
- **JSON**: Validates key structure, data types, and nesting
- **Markdown**: Validates header structure and hierarchy
- **CSV**: Validates column headers and structure

#### Level 3: Content Validation
- Ensures content follows expected patterns and formats
- Validates data consistency and completeness
- Checks for required fields and proper formatting

### Integration Points

#### Project Creation
- Templates are automatically copied during project setup
- Path configurations ensure proper template resolution
- Validation scripts are included in every project

#### Orchestration Workflow
- **Specialist Agents**: Can run validation before reporting completion
- **Reviewer Agents**: Include ACM validation in quality criteria
- **Team Supervisors**: Verify deliverables before creating review tasks
- **Iterative Review**: Validation failures trigger remediation cycles
- **Phase Completion**: All deliverables validated before phase approval

#### Migration Workflow
- Validation checkpoints at each migration phase
- Continuous validation during deliverable generation
- Iterative review cycles ensure quality before proceeding
- Final validation before project completion

#### CI/CD Integration
- Command-line interface for automated validation
- Exit codes for build pipeline integration
- Quiet mode for automated processing

## Best Practices

### Template Management
- **Consistency**: Maintain consistent template structures across projects
- **Versioning**: Track template changes and maintain compatibility
- **Documentation**: Document template purposes and usage patterns
- **Validation**: Validate templates themselves for correctness

### Deliverable Generation
- **Template Compliance**: Generate outputs that match template structures
- **Incremental Validation**: Validate deliverables as they're created (specialists can self-check)
- **Error Handling**: Address validation issues promptly
- **Iterative Improvement**: Reviewer feedback + ACM validation = high quality deliverables
- **Documentation**: Document any deviations from standard templates

### Quality Assurance
- **Regular Validation**: Run validation checks frequently during migration
- **Iterative Review**: Team supervisors orchestrate specialist → reviewer → remediation cycles
- **Issue Resolution**: Address validation issues before proceeding to next phase
- **Continuous Improvement**: Update templates based on lessons learned
- **Stakeholder Communication**: Share validation results with project stakeholders

## Framework Extension

### Adding New File Types
The validation framework is designed for extensibility:
1. Implement validation logic for new file formats
2. Add format detection and routing
3. Update error reporting for new validation types
4. Test with representative files

### Custom Validation Rules
- **Business Rules**: Add domain-specific validation logic
- **Quality Metrics**: Implement custom quality measurements
- **Integration Checks**: Validate integration requirements
- **Performance Criteria**: Check performance-related deliverables

### Tool Integration
- **Static Analysis**: Integrate code quality tools
- **Security Scanning**: Add security validation capabilities
- **Performance Testing**: Include performance validation
- **Compliance Checking**: Ensure regulatory compliance