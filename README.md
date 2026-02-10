# Legacy Code Migration Framework

## Agenda

### ✍️ Project Description
A comprehensive multi-agent framework for migrating legacy code using a **3-layer orchestration architecture**. This framework provides a standardized approach to analyze, plan, and execute legacy code migrations with AI-powered automation through hierarchical agent coordination.

This project enables systematic migration of legacy codebases (particularly COBOL and database systems) to modern architectures using 28 specialized AI agents organized in teams. The framework uses supervisor-based delegation, iterative quality assurance, and runtime task file creation to ensure consistent and reliable migration outcomes.

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

- **[Quick Start](QUICK_START.md)** - Get started in 3 simple steps (or 1 command!)
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Complete installation instructions
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Scripts Guide](SCRIPTS_GUIDE.md)** - Installation and uninstallation scripts reference
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive step-by-step usage guide
- **[Orchestration Architecture](structure/doc/orchestration_architecture.md)** - Complete architecture documentation
- **[Agent Documentation](structure/doc/agents/agents.md)** - AI agent configurations and team structure
- **[ACM Framework](structure/doc/acm/acm.md)** - Agent management and validation tools
- **[Prompt Documentation](structure/doc/prompts/prompts.md)** - AI prompts for migration phases
- **[Template Library](structure/doc/templates/templates.md)** - Standardized deliverable templates
- **[Task File Template](structure/doc/task_file_template.md)** - Guide for creating task files
- **[Documentation Index](structure/doc/README.md)** - Complete documentation overview

## Key Features

### Orchestration Architecture
- **3-Layer Hierarchical Model**: Migration Supervisor → Team Supervisors → Specialists/Reviewers
- **28 Specialized Agents**: Organized in 5 teams (Analysis, Planning, Business, Development, Deployment)
- **Supervisor-Based Delegation**: Team supervisors create task files and orchestrate work
- **Iterative Quality Assurance**: Built-in review cycles within each phase
- **Runtime Task Creation**: Dynamic task files combine generic agents with project-specific context

### Migration Capabilities
- **Standardized Project Structure**: Automated project setup with consistent folder organization
- **AI-Powered Analysis**: Intelligent source code and database analysis
- **Workpackage Management**: Structured approach to breaking down migration tasks
- **Template-Driven Workflows**: Pre-built templates for reports, tracking, and documentation
- **Validation Framework**: Built-in deliverable validation and quality assurance
- **Configuration Management**: Flexible path configuration system

## Quick Start

### One-Command Installation

For the fastest setup, use the all-in-one installation script:

```bash
./install_all.sh my_migration_project
```

This single command will:
1. Install CAO and its dependencies
2. Create your project structure
3. Install all 28 agents

**Options:**
```bash
# Install with a specific provider
./install_all.sh my_project --provider q_cli

# Skip validation (not recommended)
./install_all.sh my_project --skip-validation

# Get help
./install_all.sh --help
```

### Manual Step-by-Step Installation

If you prefer more control, follow these steps:

### Understanding the Architecture

The framework uses a **3-layer orchestration architecture**:

```
Layer 1: Migration Supervisor
    ↓ (delegates phases)
Layer 2: Team Supervisors (create task files, orchestrate review)
    ↓ (delegates tasks)
Layer 3: Specialists & Reviewers (execute work, validate deliverables)
```

**Key Principle**: Agents are generic and reusable. Project-specific context is provided through task files created at runtime by team supervisors.

For a complete understanding, see the [Orchestration Architecture Documentation](structure/doc/orchestration_architecture.md).

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

1. **Install CLI Agent Orchestrator (CAO) - Optional but Recommended:**
```bash
python install_cao.py
```

2. **Create the project structure:**
```bash
python create_project.py <project_name>
```

3. **Install agents (if you chose to skip during project creation):**
```bash
cd <project_name>
python acm/install_agents.py --provider kiro_cli
```

The first command installs [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator) and its dependencies (tmux, uv). The second command creates a complete project structure with all necessary folders, templates, and configuration files. The third command installs the 28 specialized agents into CAO with your chosen provider.

### CAO Installation Features

The installation process is now separated into two parts:

**CAO Installation (`install_cao.py`):**
- Installs required dependencies (tmux 3.3+, uv, CAO)
- Validates system prerequisites
- Sets up CAO for use across all projects

**Agent Installation (`acm/install_agents.py`):**
- Discovers and installs all 28 agents from the project's agents directory
- Supports provider selection (Kiro CLI default, Amazon Q CLI, Claude Code)
- Can be run at any time to install or update agents
- Provides organized agent listing with team structure visibility
- Supports multiple agent installation sources (built-in, local files, URLs)
- Shows command preview before execution for transparency

**Benefits of Separation:**
- Install CAO once, use for multiple projects
- Modify agent files and easily reinstall them
- Switch providers without reinstalling CAO
- Update agents independently of CAO installation

### Project Structure

The framework creates the following standardized structure:

```
project_name/
├── input/                 # Source materials and specifications
├── output/               # Analysis results and generated artifacts
├── templates/            # Report and tracking templates
├── prompts/             # AI prompts for different migration phases
├── tools/               # ACM tools and utilities
│   └── acm-tools/       # Downloaded ACM tools (auto-installed)
├── acm/                 # Framework tools and validators
│   ├── install_agents.py      # Agent installation/update script
│   └── deliverable_validator.py  # Deliverable validation tool
└── agents/              # AI agent configurations (28 agents in 5 teams)
    ├── migration_supervisor.md
    ├── analysis_team/    # Legacy code and database analysis (5 agents)
    ├── planning_team/    # Migration workpackage planning (3 agents)
    ├── business_team/    # Business logic and requirements (7 agents)
    ├── development_team/ # Code generation and testing (5 agents)
    └── deployment_team/  # Migration scripts and deployment (7 agents)
```

**Note**: 
- ACM tools are automatically downloaded and installed during project creation
- For detailed ACM documentation, see [structure/doc/acm/acm.md](structure/doc/acm/acm.md)
- To update ACM tools: `python install_acm_tools.py --tools-dir ./tools`

## Usage

### Getting Started

For a comprehensive step-by-step guide, see the **[User Guide](docs/USER_GUIDE.md)**.

**Quick Start Steps:**

1. **Install CAO**: Run `install_cao.py` to set up agent orchestration (one-time setup)
2. **Initialize Project**: Use `create_project.py` to create your migration project (ACM tools auto-installed)
3. **Install Agents**: Run `acm/install_agents.py` from your project directory
4. **Configure Paths**: Review `config/paths.cfg` (auto-configured)
5. **Add Legacy Code**: Place source code in `input/legacy/`
6. **Start Migration**: Use Migration Supervisor with main prompt
7. **Monitor Progress**: Check task files and deliverables
8. **Validate Deliverables**: Use `./validate_deliverables.sh` to ensure quality
9. **Update Agents**: Modify agent files and run `acm/install_agents.py` to reinstall
10. **Update ACM Tools**: Run `python ../install_acm_tools.py --tools-dir ./tools` when needed

### Understanding the Workflow

The framework uses a **supervisor-based orchestration model**:

1. **Migration Supervisor** receives the main prompt (`prompts/ReImagine_Main_Prompt.md`)
2. **Delegates phases** to team supervisors (Analysis, Planning, Business, Development, Deployment)
3. **Team Supervisors** create task files for specialists and reviewers
4. **Specialists** execute technical work and produce deliverables
5. **Reviewers** validate deliverables against quality criteria
6. **Iterative cycles** continue until reviewers approve
7. **Phase completes** only after review approval

For detailed workflow information, see the [Orchestration Architecture Documentation](structure/doc/orchestration_architecture.md).

### ACM Tools Installation

ACM tools are automatically installed during project creation. For manual installation or updates:

**Standard Installation:**
```bash
python3 install_acm_tools.py
```

**Private Repository (Use Local ZIP):**
```bash
# If repository is private, download ZIP manually then:
python3 install_acm_tools.py --zip-file /path/to/acm-tools-main.zip
```

**Update Existing Project:**
```bash
cd my_project
python3 ../install_acm_tools.py --tools-dir ./tools
```

**Available Options:**
- `--tools-dir PATH` - Target directory (default: ./tools)
- `--zip-file PATH` - Use local ZIP file instead of downloading
- `--skip-on-error` - Continue on failure (for automation)

**If Download Fails:**
The repository may be private. Solutions:
1. Download ZIP manually and use `--zip-file` option
2. Request repository access from owner
3. Use `--skip-on-error` to continue without ACM tools

For complete details, see [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) (install_acm_tools.py section) or [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) (ACM Tools Installation Reference section).

### Using CAO Agents

If you installed CAO, you can use the configured agents directly. The framework includes 28 specialized agents organized in teams:

```bash
# Install CAO (one-time setup)
python install_cao.py

# Create a project
python create_project.py my_migration_project
cd my_migration_project

# Install all agents with provider selection (Kiro CLI is default)
python acm/install_agents.py --provider kiro_cli     # Kiro CLI (default, recommended)
python acm/install_agents.py --provider q_cli        # Amazon Q CLI  
python acm/install_agents.py --provider claude_code  # Claude Code

# Verify agent installation
cao list

# Update agents after modifying agent files
python acm/install_agents.py

# Install specific agents only
python acm/install_agents.py --agent-sources migration_supervisor.md

# Examples of agent usage:
# Launch agents with Kiro CLI
kiro-cli chat --agent migration_supervisor
kiro-cli chat --agent analysis_team_supervisor

# Or use CAO directly
cao launch --agents migration_supervisor
```

#### Agent Organization

The framework uses a **3-layer hierarchical team structure** with provider selection support:

**Layer 1 - Top-Level Orchestration:**
- **Migration Supervisor** (1 agent): Receives main prompt, delegates phases to team supervisors

**Layer 2 - Team Supervisors:**
- **Analysis Team Supervisor**: Creates task files, orchestrates analysis and review
- **Planning Team Supervisor**: Creates task files, orchestrates planning and review
- **Business Team Supervisor**: Creates task files, orchestrates business extraction and review
- **Development Team Supervisor**: Creates task files, orchestrates code generation and review
- **Deployment Team Supervisor**: Creates task files, orchestrates deployment and review

**Layer 3 - Specialists & Reviewers:**
- **Analysis Team** (5 agents): Legacy code and database analysis with reviewers
- **Planning Team** (3 agents): Migration workpackage planning with reviewers
- **Business Team** (7 agents): Business logic extraction and requirements with reviewers
- **Development Team** (5 agents): Code generation and testing with reviewers
- **Deployment Team** (7 agents): Migration scripts and deployment with reviewers

**Total: 28 agents** organized in 5 specialized teams plus 1 top-level supervisor

Each team includes specialist agents paired with dedicated reviewers for iterative quality assurance. All agents support multiple CLI providers:

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

### Quick Links

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive step-by-step usage guide
- **[Orchestration Architecture](structure/doc/orchestration_architecture.md)** - Complete architecture documentation
- **[Documentation Index](structure/doc/README.md)** - Complete documentation overview

### Detailed Documentation

Detailed documentation for each component is available in the `structure/doc/` directory:

- **[Orchestration Architecture](structure/doc/orchestration_architecture.md)** - 3-layer architecture, delegation protocol, review orchestration
- **[Task File Template](structure/doc/task_file_template.md)** - Guide for creating task files
- **[Agents](structure/doc/agents/agents.md)** - AI agent configuration, team structure, and usage
- **[Prompts](structure/doc/prompts/prompts.md)** - AI prompts for migration phases
- **[Templates](structure/doc/templates/templates.md)** - Available templates and their usage
- **[ACM Framework](structure/doc/acm/)** - Framework tools and validation
- **[Input Structure](structure/doc/input/)** - How to organize source materials
- **[Output Structure](structure/doc/output/)** - Understanding generated artifacts

### Key Concepts

**Orchestration Architecture**: The framework uses a 3-layer model where the Migration Supervisor delegates phases to team supervisors, who create task files for specialists and reviewers. This ensures agents remain generic while providing project-specific context at runtime.

**Task Files**: Runtime-generated documents that combine generic agent capabilities with project-specific context (paths, instructions, deliverables). Created by team supervisors for each task.

**Iterative Review**: Quality assurance is built into each phase through review cycles orchestrated by team supervisors. Specialists produce deliverables, reviewers validate, and the cycle repeats until approved.

**Path Resolution**: All paths flow through the architecture: `{{PARAMETERS}}` in prompts → resolved by supervisors → absolute paths in task files → used by specialists/reviewers.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

