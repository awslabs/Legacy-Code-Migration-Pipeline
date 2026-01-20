# Installation Guide

This guide walks you through the complete installation process for the Legacy Code Migration Framework with CLI Agent Orchestrator (CAO) integration, including provider selection and agent management.

## Prerequisites

Before starting, ensure you have:
- Python 3.7 or higher
- Git
- Internet connection for downloading dependencies

**Optional (for CAO agent orchestration):**
- tmux 3.3+ (installed automatically by installer)
- uv (Python package manager, installed automatically)
- **Kiro CLI** (for `kiro_cli` provider, recommended) - Install from https://kiro.ai
  - Verify: `kiro-cli --version`
- Amazon Q CLI (for `q_cli` provider)
- Claude Code (for `claude_code` provider)

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

After creating your project, install CAO with your preferred provider. **Kiro CLI is the default provider** and provides the best integration with Kiro development environments.

#### Basic Installation (Kiro CLI Default)
```bash
python3 install_cao.py my_migration_project --provider kiro_cli
```

#### Provider Selection
Choose your preferred CLI provider for agent integration:

```bash
# Kiro CLI (Default - Recommended for Kiro users)
python3 install_cao.py my_migration_project --provider kiro_cli

# Amazon Q CLI
python3 install_cao.py my_migration_project --provider q_cli

# Claude Code
python3 install_cao.py my_migration_project --provider claude_code
```

#### Supported Providers

| Provider | Display Name | Description | CLI Required |
|----------|--------------|-------------|--------------|
| `kiro_cli` | Kiro CLI | **Default provider** - Best integration with Kiro development environment | Yes (`kiro-cli` command) |
| `q_cli` | Amazon Q CLI | AWS-native AI assistant integration | Yes (`q` command) |
| `claude_code` | Claude Code | Anthropic Claude integration | No |

#### Kiro CLI Setup Instructions

Kiro CLI is the recommended default provider. To set up Kiro CLI:

1. **Install Kiro CLI**: Follow the [Kiro installation guide](https://kiro.ai)
2. **Verify Installation**: Run `kiro-cli --version` to confirm Kiro CLI is available
3. **Configure Workspace**: Ensure your project is in a Kiro workspace (optional)

Example Kiro CLI usage:
```bash
# Install with Kiro CLI (default)
python3 install_cao.py my_migration_project --provider kiro_cli

# Verify Kiro CLI integration
kiro-cli --version
kiro-cli --help
```

The CAO installation script will:
- **Install tmux**: Uses the official CAO tmux installer (version 3.3+ required)
- **Install uv**: Downloads and installs the uv Python package manager
- **Install CAO**: Uses `uv tool install` to install CAO from the official repository
- **Configure Provider**: Sets up your selected provider (Kiro CLI by default)
- **Install Agents**: Discovers and installs all 28 agents using `cao install` commands
- **Setup Environment**: Initializes CAO in your project directory with provider integration
- **Show Progress**: Displays command preview before each installation for transparency

### 3. Agent Installation Methods

CAO supports multiple methods for installing agents, all using the `cao install` command syntax:

#### Built-in Agents
Install pre-packaged agents that come with CAO:
```bash
# Install a built-in agent with default provider (Kiro CLI)
cao install developer --provider kiro_cli

# Install with specific provider
cao install developer --provider q_cli
```

#### Local Agent Files
Install agents from local markdown files:
```bash
# Install from local file with default provider
cao install /path/to/my_agent.md --provider kiro_cli

# Install with specific provider
cao install ./agents/custom_agent.md --provider kiro_cli
```

#### URL-based Agents
Install agents directly from URLs:
```bash
# Install from URL with default provider
cao install https://example.com/agents/specialist_agent.md --provider kiro_cli

# Install with specific provider
cao install https://github.com/user/repo/agent.md --provider claude_code
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
# Kiro CLI with custom agents and skip dependencies
python3 install_cao.py my_migration_project --provider kiro_cli --agent-sources custom_agent --skip-deps

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
cao list

# Install additional agents
cao install <agent_name_or_path> --provider <provider>

# Remove an agent (if supported by CAO)
cao remove <agent_name>

# Get help
cao --help
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

**Kiro CLI Integration (Default)**:
```bash
# Terminal 1: Start server (if needed)
cao-server

# Terminal 2: Launch agent with Kiro CLI
cao launch --agents developer

# Or use Kiro CLI directly
kiro-cli chat --agent developer
kiro-cli chat --agent migration_supervisor
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

**Kiro CLI Workflow**:
```bash
# Use Kiro CLI to chat with agents
kiro-cli chat --agent migration_supervisor
kiro-cli chat --agent analysis_team_supervisor

# Or start CAO with Kiro CLI integration
cao launch --agents developer

# Check Kiro CLI version
kiro-cli --version
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

#### Kiro CLI (Default Provider) Issues

**Kiro CLI Not Found**:
```bash
# Check if Kiro CLI is installed
which kiro-cli
kiro-cli --version

# If not installed, install Kiro CLI first
# Follow: https://kiro.ai

# Verify Kiro CLI integration
python3 install_cao.py my_project --provider kiro_cli
```

**Kiro CLI Permission Issues**:
```bash
# Ensure Kiro workspace is properly configured (if using workspace features)
kiro-cli --help

# Check Kiro CLI installation
ls -la ~/.local/bin/kiro-cli
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

#### Command Syntax
Ensure you're using the correct command syntax:

```bash
# Correct syntax
cao install developer --provider kiro_cli
cao install /path/to/agent.md --provider q_cli
cao install https://example.com/agent.md --provider claude_code

# List installed agents
cao list

# NOT: cao agent install (old syntax, doesn't work)
# NOT: cao agent list (old syntax, doesn't work)
```

#### Common Command Errors

**Error: "No such command 'agent'"**
- **Cause**: Using old command syntax `cao agent install`
- **Solution**: Use `cao install` instead
```bash
# Wrong
cao agent install developer

# Correct
cao install developer --provider kiro_cli
```

**Error: "Invalid value for '--provider': 'k_cli'"**
- **Cause**: Using incorrect provider name
- **Solution**: Use `kiro_cli` not `k_cli`
```bash
# Wrong
cao install developer --provider k_cli

# Correct
cao install developer --provider kiro_cli
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
python3 install_cao.py my_project --provider kiro_cli  # Correct
python3 install_cao.py my_project --provider k_cli     # Incorrect - will fail

# Valid provider names:
# - kiro_cli (Kiro CLI)
# - q_cli (Amazon Q CLI)
# - claude_code (Claude Code)
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
If you're upgrading from an older CAO version or seeing old command references:
```bash
# Remove old agent installations (if any)
rm -rf .cao/agents/

# Use correct installation method
cao install developer --provider kiro_cli

# Verify with correct command
cao list

# NOT: cao agent list (old command)
```

#### Network Issues for URL-based Agents
```bash
# Test URL accessibility
curl -I https://example.com/agent.md

# Use local file as fallback
wget https://example.com/agent.md
cao install ./agent.md --provider kiro_cli
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
python3 install_cao.py my_migration_project --provider kiro_cli

# Verify new agent store location
ls -la ~/.aws/cli-agent-orchestrator/agent-store/

# Test correct command syntax
cao list
cao install developer --provider kiro_cli
```

#### Troubleshooting Migration Issues
```bash
# If agents don't appear after migration
cao install /path/to/old/agent.md --provider kiro_cli

# If provider integration fails
python3 install_cao.py my_project --provider kiro_cli --skip-agents
cao install developer --provider kiro_cli
```

#### Important: Command Changes
```bash
# OLD (doesn't work anymore)
cao agent install developer --provider k_cli
cao agent list

# NEW (correct)
cao install developer --provider kiro_cli
cao list
```

### Getting Help

For additional support:
1. Check the [CAO documentation](https://github.com/awslabs/cli-agent-orchestrator)
2. Review provider-specific documentation:
   - [Kiro CLI Documentation](https://kiro.ai)
   - [Amazon Q CLI Documentation](https://docs.aws.amazon.com/amazonq/)
   - [Claude Code Documentation](https://claude.ai/docs)
3. Review the project's README.md and fix documentation:
   - `README.md` - Main documentation
   - `KIRO_CLI_FIX.md` - CLI command fixes
   - `CAO_COMMAND_FIX.md` - Command and provider fixes
   - `COMPLETE_FIX_SUMMARY.md` - All fixes summary
4. Examine the generated project structure for guidance
5. Use `cao --help` for command reference

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
   - **Kiro CLI Users**: Use `kiro-cli chat --agent <name>` to interact with agents
   - **Q-CLI Users**: Leverage AWS Q integration for cloud-native modernization
   - **Claude Code Users**: Utilize Claude's code understanding for complex transformations
4. **Run Analysis**: Use CAO agents with your provider to analyze your legacy system
5. **Generate Migration Plan**: Create workpackages and migration roadmap with provider-specific tools
6. **Execute Migration**: Generate and validate modern code implementations using your chosen provider

### Provider-Specific Next Steps

#### Kiro CLI Users
```bash
# Use Kiro CLI to chat with agents
kiro-cli chat --agent migration_supervisor
kiro-cli chat --agent analysis_team_supervisor

# Or use CAO directly
cao launch --agents migration_supervisor

# Verify installation
kiro-cli --version
cao list
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

### Quick Command Reference

```bash
# List installed agents
cao list

# Install additional agents
cao install <agent_file> --provider kiro_cli

# Launch agent with Kiro CLI
kiro-cli chat --agent <agent_name>

# Launch agent with CAO
cao launch --agents <agent_name>

# Get help
cao --help
kiro-cli --help
```

Happy migrating with your chosen provider! 🚀