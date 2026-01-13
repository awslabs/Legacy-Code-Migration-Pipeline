# Installation Guide

This guide walks you through the complete installation process for the Legacy Code Migration Framework with CLI Agent Orchestrator (CAO) integration, including provider selection and agent management.

## Prerequisites

Before starting, ensure you have:
- Python 3.7 or higher
- Git
- Internet connection for downloading dependencies
- Your preferred CLI provider (K-CLI recommended as default)

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

### 2. Install CLI Agent Orchestrator (CAO) with Provider Selection

After creating your project, install CAO with your preferred provider. **K-CLI is the default provider** and provides the best integration with Kiro development environments.

#### Basic Installation (K-CLI Default)
```bash
python3 install_cao.py my_migration_project
```

#### Provider Selection
Choose your preferred CLI provider for agent integration:

```bash
# K-CLI (Default - Recommended for Kiro users)
python3 install_cao.py my_migration_project --provider k_cli

# Amazon Q CLI
python3 install_cao.py my_migration_project --provider q_cli

# Claude Code
python3 install_cao.py my_migration_project --provider claude_code
```

#### Supported Providers

| Provider | Display Name | Description | CLI Required |
|----------|--------------|-------------|--------------|
| `k_cli` | K-CLI (Kiro) | **Default provider** - Best integration with Kiro development environment | Yes (kiro command) |
| `q_cli` | Amazon Q CLI | AWS-native AI assistant integration | Yes (q command) |
| `claude_code` | Claude Code | Anthropic Claude integration | No |

#### K-CLI Setup Instructions

K-CLI is the recommended default provider. To set up K-CLI:

1. **Install Kiro**: Follow the [Kiro installation guide](https://kiro.ai/docs/installation)
2. **Verify Installation**: Run `kiro --version` to confirm K-CLI is available
3. **Configure Workspace**: Ensure your project is in a Kiro workspace

Example K-CLI usage:
```bash
# Install with K-CLI (default)
python3 install_cao.py my_migration_project

# Verify K-CLI integration
kiro --help
```

The CAO installation script will:
- **Install tmux**: Uses the official CAO tmux installer (version 3.3+ required)
- **Install uv**: Downloads and installs the uv Python package manager
- **Install CAO**: Uses `uv tool install` to install CAO from the official repository
- **Configure Provider**: Sets up your selected provider (K-CLI by default)
- **Install Agents**: Discovers and installs agents using the new `cao agent install` commands
- **Setup Environment**: Initializes CAO in your project directory with provider integration

### 3. Agent Installation Methods

CAO supports multiple methods for installing agents, all using the modern `cao agent install` command syntax:

#### Built-in Agents
Install pre-packaged agents that come with CAO:
```bash
# Install a built-in agent with default provider (K-CLI)
cao agent install developer

# Install with specific provider
cao agent install developer --provider q_cli
```

#### Local Agent Files
Install agents from local markdown files:
```bash
# Install from local file with default provider
cao agent install /path/to/my_agent.md

# Install with specific provider
cao agent install ./agents/custom_agent.md --provider k_cli
```

#### URL-based Agents
Install agents directly from URLs:
```bash
# Install from URL with default provider
cao agent install https://example.com/agents/specialist_agent.md

# Install with specific provider
cao agent install https://github.com/user/repo/agent.md --provider claude_code
```

#### Agent Source Selection
You can specify which agents to install during the initial setup:
```bash
# Install specific agents only
python3 install_cao.py my_migration_project --agent-sources developer analyst

# Install from mixed sources
python3 install_cao.py my_migration_project --agent-sources developer /path/to/custom.md https://example.com/agent.md
```

### 4. Installation Options and Customization

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

#### Combined Options
Combine provider selection with installation options:
```bash
# K-CLI with custom agents and skip dependencies
python3 install_cao.py my_migration_project --provider k_cli --agent-sources custom_agent --skip-deps

# Q-CLI with no agents initially
python3 install_cao.py my_migration_project --provider q_cli --skip-agents
```

## Post-Installation Usage

### Agent Store Location

CAO stores installed agents in the following location:
```
~/.aws/cli-agent-orchestrator/agent-store/
```

This centralized location allows for:
- Easy agent management across projects
- Provider-specific agent configurations
- Shared agent access between different CAO installations

### Agent Management Commands

Use these commands to manage your installed agents:

```bash
# List all installed agents
cao agent list

# Install additional agents
cao agent install <agent_name_or_path> --provider <provider>

# Remove an agent
cao agent remove <agent_name>

# Update agent information
cao agent info <agent_name>
```

### Using CAO Agents

After installation, navigate to your project directory:

```bash
cd my_migration_project
```

### Using CAO Agents with Providers

After installation, navigate to your project directory:

```bash
cd my_migration_project
```

#### Start CAO Server
The CAO server must be running to use agents:
```bash
cao-server
```

#### Launch Agent Sessions with Provider Integration

**K-CLI Integration (Default)**:
```bash
# Terminal 1: Start server
cao-server

# Terminal 2: Launch agent with K-CLI
cao launch --agents developer --provider k_cli

# Use Kiro commands within the agent session
kiro --help
```

**Amazon Q CLI Integration**:
```bash
# Launch agent with Q-CLI
cao launch --agents developer --provider q_cli

# Use Q commands within the agent session
q --help
```

**Claude Code Integration**:
```bash
# Launch agent with Claude Code
cao launch --agents developer --provider claude_code
```

#### Provider-Specific Examples

**K-CLI Workflow**:
```bash
# Start CAO with K-CLI integration
cao launch --agents developer --provider k_cli

# Within the agent session, use Kiro features
kiro analyze legacy_code/
kiro generate modern_equivalent.py
```

**Q-CLI Workflow**:
```bash
# Start CAO with Q-CLI integration
cao launch --agents developer --provider q_cli

# Within the agent session, use Q features
q chat "Help me modernize this COBOL code"
q generate --language python
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

### Provider-Specific Issues

#### K-CLI (Default Provider) Issues

**K-CLI Not Found**:
```bash
# Check if Kiro is installed
kiro --version

# If not installed, install Kiro first
# Follow: https://kiro.ai/docs/installation

# Verify K-CLI integration
python3 install_cao.py my_project --provider k_cli
```

**K-CLI Permission Issues**:
```bash
# Ensure Kiro workspace is properly configured
kiro workspace init

# Check workspace permissions
ls -la ~/.kiro/
```

#### Amazon Q CLI Issues

**Q-CLI Not Found**:
```bash
# Install Amazon Q CLI
# Follow AWS documentation for Q CLI installation

# Verify installation
q --version

# Retry CAO installation with Q-CLI
python3 install_cao.py my_project --provider q_cli
```

**Q-CLI Authentication Issues**:
```bash
# Configure AWS credentials
aws configure

# Login to Q CLI
q auth login
```

#### Claude Code Issues

**Claude Code Integration**:
```bash
# Claude Code doesn't require separate CLI installation
# Verify CAO installation with Claude Code
python3 install_cao.py my_project --provider claude_code

# Check agent installation
cao agent list
```

### Agent Installation Issues

#### New Command Syntax Issues
If you encounter issues with agent installation, ensure you're using the new command syntax:

```bash
# Correct new syntax
cao agent install developer --provider k_cli
cao agent install /path/to/agent.md --provider q_cli
cao agent install https://example.com/agent.md --provider claude_code

# Verify installation
cao agent list
```

#### Agent Store Issues
```bash
# Check agent store location
ls -la ~/.aws/cli-agent-orchestrator/agent-store/

# If directory doesn't exist, create it
mkdir -p ~/.aws/cli-agent-orchestrator/agent-store/

# Reinstall agents
cao agent install developer
```

#### Provider Validation Errors
```bash
# Check supported providers
python3 install_cao.py --help

# Use valid provider names
python3 install_cao.py my_project --provider k_cli    # Correct
python3 install_cao.py my_project --provider kiro     # Incorrect
```

### General Installation Issues

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

#### CAO Installation Issues
If CAO installation fails:
- Ensure uv is properly installed and in your PATH
- Try restarting your shell: `source ~/.bashrc` or `source ~/.zshrc`
- Check that you have internet access for downloading from GitHub
- Verify Git is installed and configured
- For provider-specific issues, see the Provider-Specific Issues section above

#### Legacy Agent Installation Issues
If you're upgrading from an older CAO version:
```bash
# Remove old agent installations
rm -rf .cao/agents/

# Use new installation method
cao agent install developer --provider k_cli

# Verify with new command
cao agent list
```

#### Network Issues for URL-based Agents
```bash
# Test URL accessibility
curl -I https://example.com/agent.md

# Use local file as fallback
wget https://example.com/agent.md
cao agent install ./agent.md --provider k_cli
```

### Migration from Legacy Installations

If you have an existing CAO installation with the old command syntax:

#### Backup Existing Configuration
```bash
# Backup old agent configurations
cp -r .cao/agents/ .cao/agents_backup/

# Backup project configuration
cp -r .cao/ .cao_backup/
```

#### Update to New System
```bash
# Reinstall with new system and provider selection
python3 install_cao.py my_migration_project --provider k_cli

# Verify new agent store location
ls -la ~/.aws/cli-agent-orchestrator/agent-store/

# Test new command syntax
cao agent list
cao agent install developer --provider k_cli
```

#### Troubleshooting Migration Issues
```bash
# If agents don't appear after migration
cao agent install /path/to/old/agent.md --provider k_cli

# If provider integration fails
python3 install_cao.py my_project --provider k_cli --skip-agents
cao agent install developer --provider k_cli
```

### Getting Help

For additional support:
1. Check the [CAO documentation](https://github.com/awslabs/cli-agent-orchestrator)
2. Review provider-specific documentation:
   - [K-CLI Documentation](https://kiro.ai/docs)
   - [Amazon Q CLI Documentation](https://docs.aws.amazon.com/amazonq/)
   - [Claude Code Documentation](https://claude.ai/docs)
3. Review the project's README.md
4. Examine the generated project structure for guidance
5. Use `cao --help` and `cao agent --help` for command reference

### Uninstalling CAO
If you need to uninstall CAO:
```bash
# Uninstall CAO
uv tool uninstall cli-agent-orchestrator

# Clean up agent store (optional)
rm -rf ~/.aws/cli-agent-orchestrator/

# Clean up project CAO configuration (optional)
rm -rf .cao/
```

## Next Steps

After successful installation with your chosen provider:

1. **Add Legacy Code**: Place your legacy source code in `my_migration_project/input/legacy/`
2. **Configure Specifications**: Add target system specifications to `my_migration_project/input/target/`
3. **Choose Your Provider Workflow**:
   - **K-CLI Users**: Use `kiro` commands alongside CAO agents for integrated development
   - **Q-CLI Users**: Leverage AWS Q integration for cloud-native modernization
   - **Claude Code Users**: Utilize Claude's code understanding for complex transformations
4. **Run Analysis**: Use CAO agents with your provider to analyze your legacy system
5. **Generate Migration Plan**: Create workpackages and migration roadmap with provider-specific tools
6. **Execute Migration**: Generate and validate modern code implementations using your chosen provider

### Provider-Specific Next Steps

#### K-CLI (Kiro) Users
```bash
# Initialize Kiro workspace
kiro workspace init

# Use CAO agents with Kiro integration
cao launch --agents developer --provider k_cli

# Leverage Kiro's development tools
kiro analyze legacy_system/
kiro generate modern_code/
```

#### Amazon Q CLI Users
```bash
# Configure AWS environment
aws configure

# Use CAO agents with Q integration
cao launch --agents developer --provider q_cli

# Leverage Q's AWS-native features
q chat "Help modernize this mainframe application"
```

#### Claude Code Users
```bash
# Use CAO agents with Claude integration
cao launch --agents developer --provider claude_code

# Leverage Claude's advanced code understanding
# (No additional CLI setup required)
```

Happy migrating with your chosen provider! 🚀