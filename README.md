# Legacy Code Migration Framework

## Agenda

### ✍️ Project Description
A comprehensive toolset and framework for migrating legacy code using agentic AI. This framework provides a standardized approach to analyze, plan, and execute legacy code migrations with AI-powered automation.

This project enables systematic migration of legacy codebases (particularly COBOL and database systems) to modern architectures using AI agents. The framework provides structured workflows, templates, and validation tools to ensure consistent and reliable migration outcomes.

### 🎯 Goals

1. **Systematic Legacy System Analysis and Understanding**  
   Transform complex, undocumented legacy systems (particularly COBOL and database systems) into well-understood, documented architectures through AI-powered analysis that extracts business logic, dependencies, and data flows.

2. **Structured Migration Planning and Risk Management**  
   Break down monolithic legacy migrations into manageable, prioritized workpackages with clear dependencies, timelines, and risk assessments to ensure predictable and controlled migration execution.

3. **Business Rule Extraction and Test Case Definition**  
   Extract embedded business rules from legacy code and define comprehensive test cases that validate both functional requirements and edge cases, ensuring business logic preservation during migration.

4. **Quality-Assured Automated Code Generation**  
   Generate modern, maintainable code from legacy systems using AI agents while maintaining comprehensive validation and quality assurance through template-driven deliverables and automated validation frameworks.

5. **Test Case Implementation and Validation**  
   Implement automated test suites that validate migrated code against extracted business rules and original system behavior, ensuring functional equivalence and regression prevention throughout the migration process.

### 👥 Team

| Role | Name |
|------|------|
| Project Manager | kerimman@amazon.de |
| Implementation | @[add someone] |
| Marketing / Sales| @[add someone] |
| QA Lead | @[add someone] |
| Technical Architect | kerimman@amazon.de |

### ✅ Task Tracker

We use this task tracker to keep track of team tasks: TBD

### 🔑 Key Resources

- [Migration Best Practices Guide](structure/doc/)
- [AI Agent Configuration](structure/doc/agents/)
- [Template Library](structure/doc/templates/)

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

