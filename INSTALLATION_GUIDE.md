# Installation Guide

This guide walks you through the complete installation process for the Legacy Code Migration Framework with CLI Agent Orchestrator (CAO) integration, including provider selection and agent management.

## Quick Installation

### One-Command Installation (Recommended for New Users)

The fastest way to get started is using the all-in-one installation script:

```bash
./install_all.sh my_migration_project
```

This single command performs all installation steps automatically:
1. Installs CAO and dependencies (tmux, uv)
2. Creates your project structure
3. Downloads and installs LCMP tools
4. Installs all 28 agents with your chosen provider

**Options:**
```bash
# Install with a specific provider
./install_all.sh my_project --provider kiro_cli  # Default
./install_all.sh my_project --provider q_cli
./install_all.sh my_project --provider claude_code

# Skip validation (not recommended)
./install_all.sh my_project --skip-validation

# Get help
./install_all.sh --help
```

**When to use:**
- First-time installation
- Quick setup for demos or testing
- When you want the default configuration

### Manual Installation (Recommended for Advanced Users)

If you prefer more control over each step, follow the manual installation process below. This is useful when:
- You want to customize each step
- You're installing CAO for multiple projects
- You need to troubleshoot specific steps
- You want to use different providers for different projects

## Overview

The installation process is separated into distinct steps for maximum flexibility:

1. **CAO Installation** - Install the CLI Agent Orchestrator (one-time setup)
2. **Project Creation** - Create a new migration project
3. **LCMP Tools Installation** - Download and install LCMP tools (automatic during project creation)
4. **Agent Installation** - Install agents into the project (can be repeated)

This separation allows you to:
- Install CAO once and use it for multiple projects
- Automatically get the latest LCMP tools with each project
- Modify agent files and easily reinstall them
- Switch providers without reinstalling CAO
- Update agents independently of CAO installation
- Update LCMP tools separately when needed

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

### Step 1: Install CLI Agent Orchestrator (CAO)

**This is a one-time setup.** Install CAO and its dependencies:

```bash
python3 install_cao.py
```

This installs:
- **tmux 3.3+**: Terminal multiplexer (uses official CAO installer)
- **uv**: Python package manager
- **CAO**: CLI Agent Orchestrator from the official repository

The script will:
- Validate system prerequisites
- Install required dependencies
- Verify CAO installation
- Provide next steps

**When to run**: Once on your system, before creating any projects.

### Step 2: Create Your Migration Project

Create a new migration project using the framework:

```bash
python3 create_project.py my_migration_project
```

This creates a complete project structure with:
- Input directories for legacy code and specifications
- Output directories for analysis results
- Template files for reports and tracking
- AI agent configurations (28 agents in 5 teams)
- Validation tools
- **LCMP tools** (automatically downloaded and installed to `./tools/framework-tools/`)

**LCMP Tools Installation**: The script automatically:
1. Downloads the latest LCMP tools from AWS Code repository
2. Extracts them to `<project>/tools/framework-tools/`
3. Installs Python dependencies from requirements.txt

**Interactive Prompt**: The script will ask if you want to install agents now:
```
🤖 Agent Installation
Would you like to install agents now?
(You can also install them later using: python lcmp/install_agents.py)
Install agents now? (y/N):
```

- Choose **Y** to install agents immediately (requires CAO)
- Choose **N** to install agents later

**When to run**: Once for each migration project.

### Step 2.5: LCMP Tools Installation (Automatic)

LCMP tools are automatically installed during project creation, but you can also install or update them manually:

```bash
# Install to default location (./tools)
python3 install_framework_tools.py

# Install from local ZIP file (if repository is private)
python3 install_framework_tools.py --zip-file /path/to/framework-tools-main.zip --tools-dir ./tools

# Install to custom location
python3 install_framework_tools.py --tools-dir /path/to/tools

# Update LCMP tools in existing project
cd my_existing_project
python3 ../install_framework_tools.py --tools-dir ./tools
```

**What gets installed:**
- Latest LCMP tools from AWS Code repository (or local ZIP file)
- Source: `https://code.aws.dev/personal_projects/alias_k/kerimman/framework-tools`
- Target: `<tools-dir>/framework-tools/`
- Python dependencies from requirements.txt

**Private Repository Access:**
If the repository is private or you encounter access issues:
1. Download the ZIP file manually
2. Use `--zip-file` option: `python3 install_framework_tools.py --zip-file /path/to/zip --tools-dir ./tools`
3. Or use `--skip-on-error` during project creation to continue without LCMP tools

**When to run manually:**
- To update LCMP tools to the latest version
- To install tools in an existing project
- To reinstall after corruption or deletion
- To install to a custom location
- When repository access is restricted (use --zip-file)

**Note**: During normal project creation, this step happens automatically with `--skip-on-error` flag, so the installation continues even if download fails.

## LCMP Tools Installation Reference

### Overview

LCMP tools are automatically installed during project creation. This section provides complete reference for manual installation, troubleshooting, and private repository scenarios.

### Automatic Installation

During project creation (`create_project.py`), LCMP tools are automatically:
1. Downloaded from AWS Code repository
2. Extracted to `<project>/tools/framework-tools/`
3. Dependencies installed from requirements.txt
4. Installation continues even if download fails (uses `--skip-on-error`)

### Manual Installation

#### Standard Installation (Public Repository)
```bash
python3 install_framework_tools.py
```

#### Private Repository Installation
If the repository is private or you encounter HTTP 403 errors:

**Step 1: Obtain ZIP File**
- Request access from repository owner
- Download manually: `https://code.aws.dev/personal_projects/alias_k/kerimman/framework-tools/-/archive/main/framework-tools-main.zip`
- Or receive ZIP file through approved channels

**Step 2: Install from Local ZIP**
```bash
python3 install_framework_tools.py --zip-file /path/to/framework-tools-main.zip --tools-dir ./tools
```

#### Custom Installation Location
```bash
python3 install_framework_tools.py --tools-dir /custom/path
```

#### Update Existing Project
```bash
cd my_project
python3 ../install_framework_tools.py --tools-dir ./tools

# Or with local ZIP
python3 ../install_framework_tools.py --zip-file /path/to/framework-tools.zip --tools-dir ./tools
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--tools-dir PATH` | Target directory | `--tools-dir ./tools` |
| `--zip-file PATH` | Use local ZIP file | `--zip-file ~/framework-tools.zip` |
| `--skip-on-error` | Continue on failure | `--skip-on-error` |
| `--help` | Show help message | `--help` |

### Common Scenarios

#### Scenario 1: First Time Installation
```bash
# Try automatic download
python3 install_framework_tools.py --tools-dir ./tools

# If fails with "Access Denied", use local ZIP
python3 install_framework_tools.py --zip-file /path/to/framework-tools-main.zip --tools-dir ./tools
```

#### Scenario 2: Project Creation with Private Repository
```bash
# Create project (LCMP tools installation may fail gracefully)
python3 create_project.py my_project

# Install LCMP tools manually with local ZIP
cd my_project
python3 ../install_framework_tools.py --zip-file /path/to/framework-tools.zip --tools-dir ./tools
```

#### Scenario 3: Automation/CI-CD
```bash
# Use skip-on-error for automation
python3 install_framework_tools.py --skip-on-error
```

### Error Handling

#### HTTP 403 - Access Denied (Private Repository)
**Error Message:**
```
❌ HTTP Error 403: Forbidden
⚠️  Access Denied - This may be a private repository
```

**Solutions:**
1. Download ZIP manually and use `--zip-file` option
2. Request repository access from owner
3. Use `--skip-on-error` to continue without LCMP tools

#### HTTP 404 - Repository Not Found
**Error Message:**
```
❌ HTTP Error 404: Not Found
⚠️  Repository Not Found
```

**Solutions:**
1. Verify repository URL is correct
2. Check if repository has been moved
3. Contact repository owner

#### Network/DNS Issues
**Error Message:**
```
❌ URL Error: [reason]
⚠️  Network or DNS issue
```

**Solutions:**
1. Check internet connection: `ping code.aws.dev`
2. Check firewall/proxy settings
3. Use `--zip-file` with local ZIP

### Verification

After installation, verify LCMP tools:
```bash
# Check directory exists
ls -la tools/framework-tools/

# View contents
ls tools/framework-tools/

# Read documentation
cat tools/framework-tools/README.md

# Verify dependencies
pip3 list | grep -i lcmp
```

### Additional Resources

- **Script Reference**: [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) - See "install_framework_tools.py" section
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - See "LCMP Tools Issues" section

### Step 3: Install Agents

Install the 28 specialized agents into CAO with your preferred provider:


```bash
cd my_migration_project
python3 lcmp/install_agents.py
```

**Provider Selection**: Choose your preferred CLI provider for agent integration:

```bash
# Kiro CLI (Default - Recommended)
python3 lcmp/install_agents.py --provider kiro_cli

# Amazon Q CLI
python3 lcmp/install_agents.py --provider q_cli

# Claude Code
python3 lcmp/install_agents.py --provider claude_code
```

The script will:
- Discover all 28 agents from the agents directory
- Parse agent metadata (name, description, version)
- Install each agent using `cao install` commands
- Configure agents for your selected provider
- Show command preview before execution
- Provide installation summary

**When to run**:
- After creating a project (if you skipped during creation)
- After modifying agent markdown files
- When switching providers
- To reinstall/update agents

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
3. **Install Agents**: Run `python3 lcmp/install_agents.py --provider kiro_cli`

Example Kiro CLI usage:
```bash
# Install agents with Kiro CLI (default)
python3 lcmp/install_agents.py --provider kiro_cli

# Verify Kiro CLI integration
kiro-cli --version
kiro-cli --help

# Use agents with Kiro CLI
kiro-cli chat --agent migration_supervisor
```

### Installation Options

#### Install Specific Agents Only

```bash
# Install only certain agents
python3 lcmp/install_agents.py --agent-sources \
    migration_supervisor.md \
    agents/analysis_team/analysis_team_supervisor.md
```

#### Custom Agents Directory

```bash
# Install from a different directory
python3 lcmp/install_agents.py --agents-dir /path/to/custom/agents
```

## Common Workflows

### Initial Setup (New User)

```bash
# Step 1: Install CAO (one-time)
python3 install_cao.py

# Step 2: Create first project
python3 create_project.py project1

# Step 3: Install agents
cd project1
python3 lcmp/install_agents.py
```

### Creating Additional Projects

```bash
# CAO already installed, just create and configure
python3 create_project.py project2
# LCMP tools are automatically installed
cd project2
python3 lcmp/install_agents.py
```

### Updating LCMP Tools

```bash
# Update LCMP tools in existing project
cd my_project
python3 ../install_framework_tools.py --tools-dir ./tools

# Or from repository root
python3 install_framework_tools.py --tools-dir my_project/tools
```

### Updating Agents

```bash
# Modify agent files in agents/ directory
vim agents/migration_supervisor.md

# Reinstall agents
python3 lcmp/install_agents.py
```

### Switching Providers

```bash
# Reinstall with different provider
python3 lcmp/install_agents.py --provider q_cli
```

## Post-Installation Usage

### Verify Installation

```bash
# Check CAO is installed
cao --help

# List installed agents
cao list

# Verify provider CLI (if applicable)
kiro-cli --version  # For Kiro CLI
q --version         # For Amazon Q CLI
```

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

**Kiro CLI Authentication Error (AccessDeniedException)**:

If you see this error when using `kiro-cli`:
```
Error { code: "AccessDeniedException", message: "The bearer token included in the request is invalid." }
```

**Solution**: Logout and login again to refresh your authentication token:
```bash
# Logout from Kiro CLI
kiro-cli logout

# Login again to get a fresh token
kiro-cli login
```

This refreshes your bearer token and resolves authentication issues. This is a common issue when:
- Your session has expired
- You haven't used `kiro-cli` in a while
- AWS credentials have been refreshed

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

If you need to uninstall CAO and remove all agents:

```bash
# Complete uninstallation
./uninstall_all.sh

# Keep configuration files
./uninstall_all.sh --keep-config

# Keep agent cache
./uninstall_all.sh --keep-cache

# Get help
./uninstall_all.sh --help
```

**Note:** This removes CAO and agents but preserves:
- Project directories and files
- Python, uv, tmux, and Git
- Project-specific .cao directories

To reinstall after uninstalling:
```bash
./install_all.sh my_new_project
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