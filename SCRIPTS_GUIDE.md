# Installation Scripts Guide

This guide explains the installation and uninstallation scripts for the Legacy Code Migration Framework.

## Overview

The framework provides two convenience scripts for managing installations:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `install_all.sh` | Complete installation in one command | First-time setup, quick demos |
| `uninstall_all.sh` | Remove CAO and all agents | Cleanup, troubleshooting |

## install_all.sh

### Description

Performs a complete installation of the Legacy Code Migration Framework:
1. Installs CAO (CLI Agent Orchestrator) and dependencies
2. Creates a new migration project
3. Installs all 28 agents with your chosen provider

### Usage

```bash
./install_all.sh <project_name> [OPTIONS]
```

### Arguments

- `project_name` (required): Name of the migration project to create

### Options

- `--provider PROVIDER`: CLI provider for agent integration
  - Choices: `kiro_cli` (default), `q_cli`, `claude_code`
- `--skip-validation`: Skip prerequisite validation (not recommended)
- `--help`: Show help message

### Examples

**Basic installation with default provider (Kiro CLI):**
```bash
./install_all.sh my_migration_project
```

**Install with Amazon Q CLI:**
```bash
./install_all.sh my_project --provider q_cli
```

**Install with Claude Code:**
```bash
./install_all.sh my_project --provider claude_code
```

**Skip validation (not recommended):**
```bash
./install_all.sh my_project --skip-validation
```

### What It Does

#### Step 1: Install CAO
- Checks if CAO is already installed
- If not installed: Runs `install_cao.py` to install CAO, tmux, and uv
- If already installed: Offers to upgrade to latest version
- Verifies CAO is accessible in PATH

#### Step 2: Create Project
- Runs `create_project.py` to create project structure
- Automatically answers "no" to agent installation prompt (agents installed in next step)
- Creates all necessary directories and files
- Copies templates, prompts, and agent configurations

#### Step 3: Install Agents
- Changes to project directory
- Runs `acm/install_agents.py` with specified provider
- Automatically answers "yes" to installation prompt
- Installs all 28 agents from the agents directory
- Configures agents for the selected provider

### Output

The script provides:
- Colored, formatted output for easy reading
- Progress indicators for each step
- Success/failure messages
- Final summary with next steps
- Provider-specific usage instructions

### Exit Codes

- `0`: Success
- `1`: Error (invalid arguments, installation failure, etc.)

### Error Handling

If any step fails:
- The script stops immediately (due to `set -e`)
- Error message is displayed
- Troubleshooting suggestions are provided
- You can retry individual steps manually

### Troubleshooting

**CAO not in PATH after installation:**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or restart your shell
source ~/.bashrc  # or ~/.zshrc
```

**Project already exists:**
- The script will warn you and ask for confirmation
- Continuing may overwrite existing files
- Consider using a different project name

**Agent installation fails:**
- Check CAO is working: `cao --help`
- Verify provider CLI is installed (if required)
- Retry manually: `cd project_name && python3 acm/install_agents.py`

## uninstall_all.sh

### Description

Uninstalls CAO and removes all agents, with options for selective cleanup.

### Usage

```bash
./uninstall_all.sh [OPTIONS]
```

### Options

- `--keep-config`: Keep CAO configuration files
- `--keep-cache`: Keep agent cache and store
- `--help`: Show help message

### Examples

**Complete uninstallation:**
```bash
./uninstall_all.sh
```

**Keep configuration files:**
```bash
./uninstall_all.sh --keep-config
```

**Keep agent cache:**
```bash
./uninstall_all.sh --keep-cache
```

**Keep both config and cache:**
```bash
./uninstall_all.sh --keep-config --keep-cache
```

### What It Does

#### Step 1: Check CAO Installation
- Verifies if CAO is installed
- Reports installation status

#### Step 2: List Installed Agents
- Lists all currently installed agents
- Shows total agent count
- Provides overview of what will be removed

#### Step 3: Uninstall CAO
- Uses `uv tool uninstall cli-agent-orchestrator`
- Removes CAO from system
- Reports success or failure

#### Step 4: Clean Up Files
- Removes agent store: `~/.aws/cli-agent-orchestrator/`
- Preserves project-specific `.cao` directories
- Respects `--keep-config` and `--keep-cache` options

### What Is NOT Removed

The script preserves:
- **Python** (python3)
- **uv** (Python package manager)
- **tmux** (terminal multiplexer)
- **Git**
- **Project directories** and all project files
- **Project-specific .cao directories**

These must be removed manually if desired.

### Output

The script provides:
- Warning message before uninstallation
- Confirmation prompt
- Progress indicators
- Summary of what was removed
- Instructions for manual cleanup (if needed)

### Exit Codes

- `0`: Success or user cancelled
- `1`: Error (invalid arguments, etc.)

### Safety Features

- **Confirmation prompt**: Requires explicit "yes" to proceed
- **Preserves projects**: Never touches project directories
- **Selective cleanup**: Options to keep config and cache
- **Clear warnings**: Shows exactly what will be removed

### Reinstalling After Uninstall

To reinstall after uninstalling:

```bash
./install_all.sh my_new_project
```

Or follow manual installation steps:

```bash
python3 install_cao.py
python3 create_project.py my_project
cd my_project
python3 acm/install_agents.py
```

## Comparison: Scripts vs Manual Installation

### Use install_all.sh When:

✅ You want the fastest setup  
✅ You're doing a first-time installation  
✅ You're okay with default settings  
✅ You want a demo or test environment  
✅ You're new to the framework  

### Use Manual Installation When:

✅ You want control over each step  
✅ You're installing CAO for multiple projects  
✅ You need to troubleshoot specific steps  
✅ You want different providers for different projects  
✅ You're an advanced user  

### Use uninstall_all.sh When:

✅ You want to completely remove CAO  
✅ You're troubleshooting installation issues  
✅ You want to start fresh  
✅ You're cleaning up after testing  

## Best Practices

### Installation

1. **First Time**: Use `install_all.sh` for quick setup
2. **Multiple Projects**: Install CAO once manually, then create projects as needed
3. **Testing**: Use `install_all.sh` with test project names
4. **Production**: Consider manual installation for better control

### Uninstallation

1. **Backup First**: Save any important project files before uninstalling
2. **Keep Config**: Use `--keep-config` if you plan to reinstall soon
3. **Complete Cleanup**: Run without options for fresh start
4. **Selective**: Use options to preserve specific components

### Troubleshooting

1. **Check Logs**: Scripts provide detailed output
2. **Verify Prerequisites**: Ensure Python, Git are installed
3. **PATH Issues**: Add `~/.local/bin` to PATH if needed
4. **Manual Steps**: Fall back to manual installation if scripts fail

## Script Maintenance

### Updating Scripts

The scripts are designed to work with the current framework version. If you update the framework:

1. Pull latest changes: `git pull`
2. Scripts are automatically updated
3. No additional configuration needed

### Customizing Scripts

To customize the scripts:

1. Copy the script: `cp install_all.sh my_install.sh`
2. Modify as needed
3. Make executable: `chmod +x my_install.sh`
4. Run your custom version

## Related Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Detailed installation instructions
- **[README.md](README.md)** - Main project documentation
- **[structure/doc/acm/acm.md](structure/doc/acm/acm.md)** - ACM framework documentation

## Support

If you encounter issues:

1. Check the script output for error messages
2. Review the [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
3. Try manual installation steps
4. Check prerequisites are installed
5. Verify PATH configuration

## Examples

### Complete Workflow

```bash
# Install everything
./install_all.sh my_migration_project

# Work on your project
cd my_migration_project
# ... do migration work ...

# When done, clean up
cd ..
./uninstall_all.sh
```

### Multiple Projects

```bash
# Install CAO once
python3 install_cao.py

# Create multiple projects
python3 create_project.py project1
python3 create_project.py project2

# Install agents for each
cd project1 && python3 acm/install_agents.py && cd ..
cd project2 && python3 acm/install_agents.py && cd ..
```

### Testing Different Providers

```bash
# Test with Kiro CLI
./install_all.sh test_kiro --provider kiro_cli

# Test with Q CLI
./install_all.sh test_q --provider q_cli

# Test with Claude Code
./install_all.sh test_claude --provider claude_code

# Clean up
./uninstall_all.sh
```

---

**Happy migrating! 🚀**
