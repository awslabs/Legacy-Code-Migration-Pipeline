# Installation Guide

This guide walks you through the complete installation process for the Legacy Code Migration Framework with CLI Agent Orchestrator (CAO) integration.

## Prerequisites

Before starting, ensure you have:
- Python 3.7 or higher
- Git
- Internet connection for downloading dependencies

## Step-by-Step Installation

### 1. Create Your Migration Project

First, create a new migration project using the framework:

```bash
python3 create_project.py my_migration_project
```

This creates a complete project structure with:
- Input directories for legacy code and specifications
- Output directories for analysis results
- Template files for reports and tracking
- AI agent configurations
- Validation tools

### 2. Install CLI Agent Orchestrator (CAO)

After creating your project, install CAO for advanced agent management:

```bash
python3 install_cao.py my_migration_project
```

The CAO installation script will:
- **Install tmux**: Uses the official CAO tmux installer (version 3.3+ required)
- **Install uv**: Downloads and installs the uv Python package manager
- **Install CAO**: Uses `uv tool install` to install CAO from the official repository
- **Configure Agents**: Discovers and installs all agents from your project's `agents/` folder
- **Setup Environment**: Initializes CAO in your project directory for immediate use

### 3. Available Installation Options

#### Skip Dependency Installation
If you already have the required dependencies installed:
```bash
python3 install_cao.py my_migration_project --skip-deps
```

#### Skip Agent Installation
If you want to manually configure agents later:
```bash
python3 install_cao.py my_migration_project --skip-agents
```

#### Full Custom Installation
Skip both dependencies and agents:
```bash
python3 install_cao.py my_migration_project --skip-deps --skip-agents
```

## Post-Installation Usage

### Using CAO Agents

After installation, navigate to your project directory:

```bash
cd my_migration_project
```

#### Start CAO Server
The CAO server must be running to use agents:
```bash
cao-server
```

#### Launch an Agent Session
In another terminal:
```bash
cao launch --agents <agent_name>
```

#### Example Usage
```bash
# Terminal 1: Start server
cao-server

# Terminal 2: Launch developer agent
cao launch --agents developer
```

#### Get Help
```bash
cao --help
```

### Available Agents

Your project includes these pre-configured agents:

- **analysis_reviewer** - Reviews analysis deliverables
- **analysis_team_supervisor** - Supervises analysis team activities
- **business_team_supervisor** - Manages business requirements
- **code_developer** - Generates modern code from legacy systems
- **code_reviewer** - Reviews generated code quality
- **code_supervisor** - Supervises code generation activities
- **database_analyst** - Analyzes database structures and dependencies
- **deployment_team_supervisor** - Manages deployment activities
- **legacy_code_analyst** - Analyzes legacy code structures
- **migration_supervisor** - Oversees entire migration process
- **planning_reviewer** - Reviews migration plans
- **planning_team_supervisor** - Supervises planning activities
- **test_generator** - Creates test cases for validation
- **workpackage_planner** - Plans migration workpackages

## Troubleshooting

### Common Issues

#### Permission Errors
If you encounter permission errors during installation:
```bash
# Make scripts executable
chmod +x create_project.py install_cao.py
```

#### Missing Dependencies
If system dependencies fail to install:
- **tmux Installation**: The script first tries the official CAO tmux installer, then falls back to system package managers
- **macOS**: Install Homebrew first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- **Linux**: Ensure you have sudo access for package installation

#### CAO Installation Issues
If CAO installation fails:
- Ensure uv is properly installed and in your PATH
- Try restarting your shell: `source ~/.bashrc` or `source ~/.zshrc`
- Check that you have internet access for downloading from GitHub
- Verify Git is installed and configured

#### Agent Installation Issues
If agents fail to install:
- The script tries multiple installation methods automatically
- Agents may be copied to `.cao/agents/` directory as fallback
- Use `cao agent list` to verify which agents are available
- Check agent file format - they should have YAML frontmatter with `name:` field

#### Uninstalling CAO
If you need to uninstall CAO:
```bash
uv tool uninstall cli-agent-orchestrator
```

### Getting Help

For additional support:
1. Check the [CAO documentation](https://github.com/awslabs/cli-agent-orchestrator)
2. Review the project's README.md
3. Examine the generated project structure for guidance

## Next Steps

After successful installation:

1. **Add Legacy Code**: Place your legacy source code in `my_migration_project/input/legacy/`
2. **Configure Specifications**: Add target system specifications to `my_migration_project/input/target/`
3. **Run Analysis**: Use CAO agents or manual prompts to analyze your legacy system
4. **Generate Migration Plan**: Create workpackages and migration roadmap
5. **Execute Migration**: Generate and validate modern code implementations

Happy migrating! 🚀