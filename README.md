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

### Recent Updates (January 2026)

The installer has been updated with critical fixes:
- ✅ Fixed CAO command: Now uses `cao install` (not `cao agent install`)
- ✅ Fixed provider name: Now uses `kiro_cli` (not `k_cli`)
- ✅ Fixed CLI command: Now checks for `kiro-cli` (not `kiro`)
- ✅ Added command preview: Shows exact command before execution
- ✅ Tested with all 28 agents: Complete end-to-end verification

See `FINAL_SUMMARY.md` for complete details.

### Prerequisites

**Required:**
- Python 3.7+
- Git

**Optional (for CAO agent orchestration):**
- tmux 3.3+ (installed automatically by installer)
- uv (Python package manager, installed automatically)
- Kiro CLI (for `kiro_cli` provider) - Install from https://kiro.ai
  - Verify: `kiro-cli --version`
- Amazon Q CLI (for `q_cli` provider)
- Claude Code (for `claude_code` provider)

### Creating a New Migration Project

1. **Create the project structure:**
```bash
python create_project.py <project_name>
```

2. **Install CLI Agent Orchestrator (CAO) - Optional but Recommended:**
```bash
python install_cao.py <project_name> --provider kiro_cli
```

The first command creates a complete project structure with all necessary folders, templates, and configuration files. The second command installs and configures the [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator) which provides advanced agent management capabilities for your migration project.

### CAO Installation Features

The `install_cao.py` script automatically:
- Installs required dependencies (tmux 3.3+, uv, CAO)
- Supports provider selection (Kiro CLI default, Amazon Q CLI, Claude Code)
- Discovers and installs all 28 agents across team subdirectories using `cao install` commands
- Sets up the CAO environment with your selected provider for immediate use
- Provides organized agent listing with team structure visibility
- Supports multiple agent installation sources (built-in, local files, URLs)
- Shows command preview before execution for transparency and debugging

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

# Install all agents with provider selection (Kiro CLI is default)
python install_cao.py . --provider kiro_cli     # Kiro CLI (default, recommended)
python install_cao.py . --provider q_cli        # Amazon Q CLI  
python install_cao.py . --provider claude_code  # Claude Code

# Verify agent installation
cao list

# Install individual agents as needed
cao install ./agents/migration_supervisor.md --provider kiro_cli
cao install ./agents/analysis_team/analysis_team_supervisor.md --provider kiro_cli

# Examples of agent usage:
# Install and use the top-level migration orchestrator
cao install ./agents/migration_supervisor.md --provider kiro_cli

# Install and use team supervisors
cao install ./agents/analysis_team/analysis_team_supervisor.md --provider kiro_cli
cao install ./agents/business_team/business_team_supervisor.md --provider kiro_cli
cao install ./agents/development_team/development_team_supervisor.md --provider kiro_cli

# Install and use specialist agents
cao install ./agents/analysis_team/analysis_specialist_legacy_code.md --provider kiro_cli
cao install ./agents/business_team/business_specialist_requirements.md --provider kiro_cli
cao install ./agents/development_team/development_specialist_code_generation.md --provider kiro_cli

# Launch agents with Kiro CLI
kiro-cli chat --agent migration_supervisor
kiro-cli chat --agent analysis_team_supervisor

# Or use CAO directly
cao launch --agents migration_supervisor
```

#### Agent Organization

The framework uses a hierarchical team structure with provider selection support:

- **Migration Supervisor** (1 agent): Top-level orchestration
- **Analysis Team** (5 agents): Legacy code and database analysis
- **Planning Team** (3 agents): Migration workpackage planning  
- **Business Team** (7 agents): Business logic extraction and requirements
- **Development Team** (5 agents): Code generation and testing
- **Deployment Team** (7 agents): Migration scripts and deployment

**Total: 28 agents** organized in 5 specialized teams plus 1 supervisor

Each team includes specialist agents paired with dedicated reviewers for quality assurance. All agents support multiple CLI providers:

- **Kiro CLI** (`kiro_cli`, default): Best integration with Kiro development environment
  - Command: `kiro-cli chat --agent <agent_name>`
  - Verify: `kiro-cli --version`
- **Amazon Q CLI** (`q_cli`): AWS-native AI assistant integration  
- **Claude Code** (`claude_code`): Anthropic Claude integration

#### Installation Output

When you run the installer, you'll see:

```
📋 Found 28 agents to install:
============================================================
1. migration_supervisor
2-6. Development Team (5 agents)
7-13. Business Team (7 agents)
14-20. Deployment Team (7 agents)
21-23. Planning Team (3 agents)
24-28. Analysis Team (5 agents)
============================================================

Install all 28 agents with Kiro CLI? (Y/n): Y

📦 Installing agent: migration_supervisor
   🔧 Executing command: cao install /path/to/migration_supervisor.md --provider kiro_cli
✅ Successfully installed agent: migration_supervisor

... (continues for all 28 agents)

🎉 Successfully installed 28/28 agents

✅ Kiro CLI is available and ready for use
📋 After installation, you can use agents with:
   • kiro-cli chat --agent <agent_name>
   • Or through the Kiro IDE interface
```

### Uninstalling CAO

If you need to remove CAO:

```bash
uv tool uninstall cli-agent-orchestrator
```

### Troubleshooting

#### Verify Kiro CLI Installation
```bash
which kiro-cli
kiro-cli --version
```

#### Verify CAO Installation
```bash
which cao
cao --help
cao list  # List installed agents
```

#### Check Agent Installation
The installer shows the exact command being executed:
```
🔧 Executing command: cao install /path/to/agent.md --provider kiro_cli
```

If you see errors, verify:
1. CAO is installed: `which cao`
2. Kiro CLI is installed (if using kiro_cli provider): `which kiro-cli`
3. The agent file exists at the specified path

#### Common Issues

**Issue**: "No such command 'agent'"
- **Solution**: This was fixed. Ensure you're using the latest version of `install_cao.py`

**Issue**: "Invalid value for '--provider': 'k_cli'"
- **Solution**: Use `kiro_cli` not `k_cli`. The correct provider names are:
  - `kiro_cli` (Kiro CLI)
  - `q_cli` (Amazon Q CLI)
  - `claude_code` (Claude Code)

**Issue**: "Kiro CLI is not available"
- **Solution**: Install Kiro CLI from https://kiro.ai and ensure `kiro-cli` command is in your PATH

For more details, see:
- `KIRO_CLI_FIX.md` - CLI command fixes
- `CAO_COMMAND_FIX.md` - Command and provider fixes
- `FULL_INSTALLATION_TEST_REPORT.md` - Complete test results

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

