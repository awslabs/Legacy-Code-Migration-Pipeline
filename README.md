# Legacy Code Migration Framework

A comprehensive toolset and framework for migrating legacy code using agentic AI. This framework provides a standardized approach to analyze, plan, and execute legacy code migrations with AI-powered automation.

## Overview

This project enables systematic migration of legacy codebases (particularly COBOL and database systems) to modern architectures using AI agents. The framework provides structured workflows, templates, and validation tools to ensure consistent and reliable migration outcomes.

## Key Features

- **Standardized Project Structure**: Automated project setup with consistent folder organization
- **AI-Powered Analysis**: Intelligent source code and database analysis
- **Workpackage Management**: Structured approach to breaking down migration tasks
- **Template-Driven Workflows**: Pre-built templates for reports, tracking, and documentation
- **Validation Framework**: Built-in deliverable validation and quality assurance
- **Configuration Management**: Flexible path configuration system

## Quick Start

### Prerequisites

- Python 3.7+
- Access to AI agents/models for code analysis

### Creating a New Migration Project

```bash
python create_project.py <project_name>
```

This command creates a complete project structure in the specified directory with all necessary folders, templates, and configuration files.

### Project Structure

The framework creates the following standardized structure:

```
project_name/
├── input/                 # Source materials and specifications
├── output/               # Analysis results and generated artifacts
├── templates/            # Report and tracking templates
├── prompts/             # AI prompts for different migration phases
├── acm/                 # Framework tools and validators
└── agents/              # AI agent configurations
```

## Usage

1. **Initialize Project**: Use `create_project.py` to create your migration project
2. **Configure Paths**: Update `config/paths.cfg` if needed
3. **Add Legacy Code**: Place source code in `input/legacy/`
4. **Run Analysis**: Execute analysis workflows using the provided prompts
5. **Validate Deliverables**: Use `./validate_deliverables.sh` to ensure quality

### Validation

The framework includes comprehensive validation tools to ensure migration quality:

```bash
# Validate all deliverables against templates
./validate_deliverables.sh

# Quiet mode (only show issues)
./validate_deliverables.sh --quiet
```

## Documentation

Detailed documentation for each component is available in the `structure/doc/` directory:

- [ACM Framework](structure/doc/acm/) - Framework tools and validation
- [Templates](structure/doc/templates/) - Available templates and their usage
- [Prompts](structure/doc/prompts/) - AI prompts for migration phases
- [Input Structure](structure/doc/input/) - How to organize source materials
- [Output Structure](structure/doc/output/) - Understanding generated artifacts
- [Agents](structure/doc/agents/) - AI agent configuration and usage

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

