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
- Git
- Access to AI agents/models for code analysis

### Creating a New Migration Project

1. **Create the project structure:**
```bash
python create_project.py <project_name>
```

2. **Install CLI Agent Orchestrator (CAO) - Optional but Recommended:**
```bash
python install_cao.py <project_name>
```

The first command creates a complete project structure with all necessary folders, templates, and configuration files. The second command downloads and configures the [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator) which provides advanced agent management capabilities for your migration project.

### CAO Installation Features

The `install_cao.py` script automatically:
- Downloads CAO from the official GitHub repository
- Installs required dependencies (tmux, uv, etc.)
- Supports provider selection (K-CLI default, Amazon Q CLI, Claude Code)
- Discovers and configures all 28 agents across team subdirectories using `cao agent install` commands
- Sets up the CAO environment with your selected provider for immediate use
- Provides organized agent listing with team structure visibility
- Supports multiple agent installation sources (built-in, local files, URLs)

### Project Structure

The framework creates the following standardized structure:

```
project_name/
├── input/                 # Source materials and specifications
├── output/               # Analysis results and generated artifacts
├── templates/            # Report and tracking templates
├── prompts/             # AI prompts for different migration phases
├── acm/                 # Framework tools and validators
└── agents/              # AI agent configurations (28 agents in 5 teams)
    ├── migration_supervisor.md
    ├── analysis_team/    # Legacy code and database analysis (5 agents)
    ├── planning_team/    # Migration workpackage planning (3 agents)
    ├── business_team/    # Business logic and requirements (7 agents)
    ├── development_team/ # Code generation and testing (5 agents)
    └── deployment_team/  # Migration scripts and deployment (7 agents)
```

## Usage

1. **Initialize Project**: Use `create_project.py` to create your migration project
2. **Install CAO (Optional)**: Run `install_cao.py` to set up agent orchestration
3. **Configure Paths**: Update `config/paths.cfg` if needed
4. **Add Legacy Code**: Place source code in `input/legacy/`
5. **Run Analysis**: Execute analysis workflows using the provided prompts or CAO agents
6. **Validate Deliverables**: Use `./validate_deliverables.sh` to ensure quality

### Using CAO Agents

If you installed CAO, you can use the configured agents directly. The framework includes 28 specialized agents organized in teams:

```bash
cd <project_name>

# Install agents with provider selection (K-CLI is default)
python install_cao.py . --provider k_cli     # K-CLI (default)
python install_cao.py . --provider q_cli     # Amazon Q CLI  
python install_cao.py . --provider claude_code  # Claude Code

# Verify agent installation
cao agent list

# Install individual agents as needed
cao agent install ./structure/agents/migration_supervisor.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_team_supervisor.md --provider k_cli

# Examples of agent usage:
# Install and use the top-level migration orchestrator
cao agent install ./structure/agents/migration_supervisor.md --provider k_cli

# Install and use team supervisors
cao agent install ./structure/agents/analysis_team/analysis_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/business_team/business_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/development_team/development_team_supervisor.md --provider k_cli

# Install and use specialist agents
cao agent install ./structure/agents/analysis_team/analysis_specialist_legacy_code.md --provider k_cli
cao agent install ./structure/agents/business_team/business_specialist_requirements.md --provider k_cli
cao agent install ./structure/agents/development_team/development_specialist_code_generation.md --provider k_cli
```

#### Agent Organization

The framework uses a hierarchical team structure with provider selection support:

- **Analysis Team** (5 agents): Legacy code and database analysis
- **Planning Team** (3 agents): Migration workpackage planning  
- **Business Team** (7 agents): Business logic extraction and requirements
- **Development Team** (5 agents): Code generation and testing
- **Deployment Team** (7 agents): Migration scripts and deployment
- **Migration Supervisor** (1 agent): Top-level orchestration

Each team includes specialist agents paired with dedicated reviewers for quality assurance. All agents support multiple CLI providers:

- **K-CLI (default)**: Best integration with Kiro development environment
- **Amazon Q CLI**: AWS-native AI assistant integration  
- **Claude Code**: Anthropic Claude integration

Each team includes specialist agents paired with dedicated reviewers for quality assurance.

### Uninstalling CAO

If you need to remove CAO:

```bash
uv tool uninstall cli-agent-orchestrator
```

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

