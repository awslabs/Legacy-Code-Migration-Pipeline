# Installation Scripts Guide

This guide explains the installation and uninstallation scripts for the Legacy Code Migration Framework.

## Overview

The framework provides several scripts for managing installations:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `install_all.sh` | Complete installation in one command | First-time setup, quick demos |
| `install_framework_tools.py` | Download and install LCMP tools | Standalone or during project creation |
| `update_prompts.py` | Update prompts in existing projects | After modifying prompts in structure/prompts |
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
- Automatically installs LCMP tools from AWS Code repository
- Automatically answers "no" to agent installation prompt (agents installed in next step)
- Creates all necessary directories and files
- Copies templates, prompts, and agent configurations

#### Step 3: Install Agents
- Changes to project directory
- Runs `lcmp/install_agents.py` with specified provider
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

**Kiro CLI Authentication Error:**

If you see `AccessDeniedException` or "bearer token is invalid" error:
```bash
# Logout and login again to refresh authentication
kiro-cli logout
kiro-cli login
```

This is a common issue when your Kiro CLI session has expired or AWS credentials have been refreshed.

**Project already exists:**
- The script will warn you and ask for confirmation
- Continuing may overwrite existing files
- Consider using a different project name

**Agent installation fails:**
- Check CAO is working: `cao --help`
- Verify provider CLI is installed (if required)
- Retry manually: `cd project_name && python3 lcmp/install_agents.py`

## install_framework_tools.py

### Description

Downloads and installs LCMP (Agentic Code Migration) tools from the AWS Code repository. This script is automatically executed during project creation but can also be run standalone to install or update the tools.

### Usage

```bash
python3 install_framework_tools.py [OPTIONS]
```

### Options

- `--tools-dir PATH`: Target directory for tools installation (default: `./tools`)
- `--zip-file PATH`: Use existing ZIP file instead of downloading (useful for private repositories)
- `--skip-on-error`: Skip installation if download fails (for automation scripts)
- `--help`: Show help message

### Examples

**Install to default location (./tools):**
```bash
python3 install_framework_tools.py
```

**Install to custom location:**
```bash
python3 install_framework_tools.py --tools-dir /path/to/custom/tools
```

**Install from local ZIP file (private repository):**
```bash
# Download the ZIP file manually first, then:
python3 install_framework_tools.py --zip-file /path/to/framework-tools-main.zip --tools-dir ./tools
```

**Install to existing project:**
```bash
cd my_project
python3 ../install_framework_tools.py --tools-dir ./tools
```

**Skip on error (for automation):**
```bash
python3 install_framework_tools.py --skip-on-error
```

### What It Does

#### Step 1: Download LCMP Tools
- Downloads the latest LCMP tools from AWS Code repository
- URL: `https://code.aws.dev/personal_projects/alias_k/kerimman/framework-tools`
- Shows download progress with size and percentage
- Saves to temporary directory

#### Step 2: Extract LCMP Tools
- Extracts the downloaded ZIP archive
- Removes any existing `framework-tools` directory in target location
- Moves extracted files to `<tools-dir>/framework-tools/`
- Preserves all file permissions and structure

#### Step 3: Install Dependencies
- Locates `requirements.txt` in the extracted tools
- Installs Python dependencies using pip
- Reports success or provides manual installation instructions

### Output

The script provides:
- Formatted headers for each step
- Download progress indicator
- File extraction details
- Dependency installation status
- Final summary with installation location
- Next steps and usage instructions

### Exit Codes

- `0`: Success
- `1`: Error (download failed, extraction failed, etc.)

### Requirements

- **Python 3**: Required to run the script
- **pip/pip3**: Required for dependency installation
- **Internet connection**: Required to download from AWS Code
- **Write permissions**: Required for target directory

### When to Use

**Automatic (during project creation):**
- LCMP tools are automatically installed when you create a new project
- No manual intervention needed

**Manual (standalone execution):**
- Update LCMP tools to latest version
- Install tools in existing project
- Reinstall after corruption or deletion
- Install to custom location

### Troubleshooting

**Download fails:**
```bash
# Check internet connection
ping code.aws.dev

# Check firewall/proxy settings
# Retry the installation
python3 install_framework_tools.py
```

**Access denied (HTTP 403) - Private Repository:**
```bash
# Option 1: Use local ZIP file
# Download manually from the repository
python3 install_framework_tools.py --zip-file /path/to/framework-tools-main.zip --tools-dir ./tools

# Option 2: Request repository access
# Contact the repository owner

# Option 3: Skip installation (if optional)
python3 install_framework_tools.py --skip-on-error
```

**Permission denied:**
```bash
# Ensure you have write permissions
ls -la ./tools

# Or install to a different location
python3 install_framework_tools.py --tools-dir ~/my-tools
```

**Dependency installation fails:**
```bash
# Install dependencies manually
cd tools/framework-tools
pip3 install -r requirements.txt
```

**Network/proxy issues:**
```bash
# If behind corporate proxy, set proxy environment variables
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
python3 install_framework_tools.py
```

### Integration with Project Creation

The `install_framework_tools.py` script is automatically called by `create_project.py`:

1. Project structure is created
2. LCMP tools are downloaded and installed to `<project>/tools/framework-tools/`
3. Dependencies are installed
4. User is prompted for agent installation

This ensures every new project has the latest LCMP tools available.

### Updating LCMP Tools

To update LCMP tools in an existing project:

```bash
cd my_existing_project
python3 ../install_framework_tools.py --tools-dir ./tools
```

This will:
- Remove the old `tools/framework-tools` directory
- Download the latest version
- Install updated dependencies

## update_prompts.py

### Description

Updates the prompts folder in an existing project with the latest versions from the structure directory. This script copies all prompt files and automatically resolves all path parameters to match the project's configuration.

### Usage

```bash
python3 update_prompts.py <path_to_project>
```

### Arguments

- `path_to_project` (required): Path to the existing migration project

### Examples

**Update prompts in a project:**
```bash
python3 update_prompts.py /Users/username/my-migration-project
```

**Update prompts in current directory:**
```bash
python3 update_prompts.py .
```

**Update prompts in relative path:**
```bash
python3 update_prompts.py ../my-project
```

### What It Does

#### Step 1: Copy Prompt Files
- Copies all files from `./structure/prompts` to `{project_path}/prompts`
- Overwrites existing prompt files with latest versions
- Preserves directory structure

#### Step 2: Resolve Path Parameters
- Reads `config/paths.cfg` from the project
- Replaces all `{{PARAMETER}}` placeholders with actual paths
- Resolves nested parameters (e.g., `{{OUTPUT_BASE_PATH}}` → `{{PROJECT_BASE_PATH}}/output`)
- Handles up to 10 levels of parameter nesting

#### Step 3: Update All Prompts
- Processes all `.md` files in the prompts directory
- Ensures all paths are absolute and project-specific
- Maintains prompt structure and formatting

### Example Transformation

**Before (in structure/prompts):**
```markdown
cd {{PROJECT_BASE_PATH}}/tools/framework-tools
Input: {{LEGACY_SOURCE_CODE}}
Output: {{COBOL_SOURCE_ANALYSIS_REPORT}}
```

**After (in project/prompts):**
```markdown
cd /Users/username/my-migration-project/tools/framework-tools
Input: /Users/username/my-migration-project/input/legacy/source
Output: /Users/username/my-migration-project/output/analysis/source_code/reports/cobol_analysis.md
```

### When to Use

**After modifying prompts in structure/prompts:**
- You've updated prompt instructions
- You've added new prompts
- You've fixed issues in existing prompts
- You want to distribute updates to existing projects

**For existing projects:**
- Update prompts to latest version
- Fix path resolution issues
- Sync with framework updates

### Output

The script provides:
- Confirmation of source and destination paths
- Progress indicator during copy
- Count of files updated
- Success message with project location

### Exit Codes

- `0`: Success
- `1`: Error (invalid path, missing config, etc.)

### Requirements

- **Python 3**: Required to run the script
- **Valid project**: Project must have `config/paths.cfg`
- **Write permissions**: Required for project's prompts directory

### Workflow for Updating Prompts

When you modify prompts in the framework:

1. **Edit prompts** in `structure/prompts/`
2. **Test changes** (optional but recommended)
3. **Update existing projects**:
   ```bash
   python3 update_prompts.py /path/to/project1
   python3 update_prompts.py /path/to/project2
   ```

### Troubleshooting

**Project path not found:**
```bash
# Verify the path exists
ls -la /path/to/project

# Use absolute path
python3 update_prompts.py /full/path/to/project
```

**Missing config/paths.cfg:**
```bash
# Verify project structure
ls -la /path/to/project/config/

# Project may be corrupted, recreate if needed
```

**Permission denied:**
```bash
# Check write permissions
ls -la /path/to/project/prompts/

# Fix permissions if needed
chmod -R u+w /path/to/project/prompts/
```

**Parameters not resolved:**
```bash
# Check paths.cfg has all required parameters
cat /path/to/project/config/paths.cfg

# Verify PROJECT_BASE_PATH is set correctly
```

### Integration with Framework Updates

When the framework is updated with new prompts:

1. Pull latest changes: `git pull`
2. Update all your projects:
   ```bash
   python3 update_prompts.py ~/projects/migration1
   python3 update_prompts.py ~/projects/migration2
   ```

This ensures all projects use the latest prompt versions with correct paths.

**Agent installation fails:**
- Check CAO is working: `cao --help`
- Verify provider CLI is installed (if required)
- Retry manually: `cd project_name && python3 lcmp/install_agents.py`

## uninstall_all.sh

### Description

Uninstalls CAO and removes all agents, with options for selective cleanup including dependency removal.

### Usage

```bash
./uninstall_all.sh [OPTIONS]
```

### Options

- `--keep-config`: Keep CAO configuration files
- `--keep-cache`: Keep agent cache and store
- `--remove-tmux`: Remove tmux (if installed by CAO installer)
- `--remove-uv-packages`: Remove CAO-related packages from uv (keeps uv itself)
- `--remove-uv`: Remove uv package manager completely
- `--remove-all-deps`: Remove all dependencies (tmux + uv + packages)
- `--help`: Show help message

### Examples

**Complete uninstallation (CAO and agents only):**
```bash
./uninstall_all.sh
```

**Remove CAO and clean up its uv packages (recommended for most users):**
```bash
./uninstall_all.sh --remove-uv-packages
```

**Remove everything including all dependencies:**
```bash
./uninstall_all.sh --remove-all-deps
```

**Remove CAO and uv completely:**
```bash
./uninstall_all.sh --remove-uv
```

**Remove CAO and tmux only:**
```bash
./uninstall_all.sh --remove-tmux
```

**Keep configuration files:**
```bash
./uninstall_all.sh --keep-config
```

**Keep agent cache:**
```bash
./uninstall_all.sh --keep-cache
```

**Keep both config and cache, but remove uv packages:**
```bash
./uninstall_all.sh --keep-config --keep-cache --remove-uv-packages
```

### What It Does

#### Step 1: Check CAO Installation
- Verifies if CAO is installed
- Reports installation status

#### Step 2: List Installed Agents
- Lists all currently installed CAO agents
- Checks for Kiro agents in `~/.kiro/agents`
- Shows total agent count for both
- Provides overview of what will be removed

#### Step 3: Uninstall CAO
- Uses `uv tool uninstall cli-agent-orchestrator`
- Removes CAO from system
- Reports success or failure

#### Step 4: Clean Up Files
- Removes Kiro agents directory: `~/.kiro/agents`
- Removes agent store: `~/.aws/cli-agent-orchestrator/` (unless `--keep-cache`)
- Preserves project-specific `.cao` directories
- Respects `--keep-config` and `--keep-cache` options

#### Step 5: Remove CAO-related uv Packages (Optional)
When `--remove-uv-packages` is specified:
- Lists currently installed uv tools
- Removes `cli-agent-orchestrator` from uv
- Preserves uv itself for use with other projects
- Shows what tools remain installed

#### Step 6: Remove uv Completely (Optional)
When `--remove-uv` is specified:
- Removes uv binaries: `~/.cargo/bin/uv`, `~/.cargo/bin/uvx`
- Removes uv data directory: `~/.local/share/uv`
- Removes uv cache: `~/.cache/uv`
- Complete removal of uv from system

#### Step 7: Remove tmux (Optional)
When `--remove-tmux` is specified:
- Detects tmux installation location
- **User-local installations** (`~/.local/bin/tmux`, `~/bin/tmux`): Removes automatically
- **System-wide installations** (`/usr/local/bin/tmux`): Asks for confirmation (requires sudo)
- **Package manager installations** (`/usr/bin/tmux`): Provides instructions for appropriate package manager

### What Is NOT Removed (by default)

The script preserves:
- **Python** (python3)
- **uv** (Python package manager) and its packages
- **tmux** (terminal multiplexer)
- **Git**
- **Project directories** and all project files
- **Project-specific .cao directories**

Use the optional flags to remove these selectively.

### Dependency Removal Options

The script provides granular control over dependency removal:

| Option | Removes | Keeps | Use Case |
|--------|---------|-------|----------|
| (none) | CAO, agents | uv, tmux, packages | Default cleanup, keep tools for other projects |
| `--remove-uv-packages` | CAO, agents, CAO packages | uv, tmux | Clean CAO footprint, keep uv for other projects |
| `--remove-uv` | CAO, agents, uv completely | tmux | Remove uv, keep tmux |
| `--remove-tmux` | CAO, agents, tmux | uv, packages | Remove tmux, keep uv |
| `--remove-all-deps` | CAO, agents, uv, tmux, packages | Python, Git | Complete cleanup |

### Output

The script provides:
- Warning message before uninstallation
- List of what will be removed
- Confirmation prompt
- Progress indicators for each step
- Summary of what was removed and what was kept
- Instructions for manual cleanup (if needed)
- Suggestions for removing remaining dependencies

### Exit Codes

- `0`: Success or user cancelled
- `1`: Error (invalid arguments, etc.)

### Safety Features

- **Confirmation prompt**: Requires explicit "yes" to proceed
- **Preserves projects**: Never touches project directories
- **Selective cleanup**: Options to keep config, cache, or dependencies
- **Clear warnings**: Shows exactly what will be removed
- **Smart tmux detection**: Identifies installation method before removal
- **Preserves uv option**: Can remove only CAO packages while keeping uv

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
python3 lcmp/install_agents.py
```

### Understanding Dependency Removal

**When to use `--remove-uv-packages`:**
- You want to clean up CAO's footprint in uv
- You use uv for other Python projects
- You want to keep uv available for future use
- **Recommended for most users**

**When to use `--remove-uv`:**
- You don't use uv for anything else
- You want a complete cleanup
- You're switching to a different Python package manager

**When to use `--remove-tmux`:**
- tmux was installed by the CAO installer
- You don't use tmux for other purposes
- You want to remove all CAO-related tools

**When to use `--remove-all-deps`:**
- You want a complete system cleanup
- You're uninstalling permanently
- You don't use any of these tools for other purposes

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
✅ You want to clean up CAO's uv packages while keeping uv  
✅ You're troubleshooting installation issues  
✅ You want to start fresh  
✅ You're cleaning up after testing  
✅ You want to remove dependencies installed by CAO  

## Best Practices

### Installation

1. **First Time**: Use `install_all.sh` for quick setup
2. **Multiple Projects**: Install CAO once manually, then create projects as needed
3. **Testing**: Use `install_all.sh` with test project names
4. **Production**: Consider manual installation for better control

### Uninstallation

1. **Backup First**: Save any important project files before uninstalling
2. **Keep Config**: Use `--keep-config` if you plan to reinstall soon
3. **Clean uv Packages**: Use `--remove-uv-packages` to clean CAO footprint while keeping uv (recommended)
4. **Complete Cleanup**: Use `--remove-all-deps` for complete removal of all dependencies
5. **Selective**: Use individual options (`--remove-uv`, `--remove-tmux`) for targeted cleanup
6. **Check Other Projects**: Before removing uv or tmux, ensure they're not used by other projects

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
- **[structure/doc/lcmp/lcmp.md](structure/doc/lcmp/lcmp.md)** - LCMP framework documentation

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

# When done, clean up (recommended - keeps uv for other projects)
cd ..
./uninstall_all.sh --remove-uv-packages

# Or complete cleanup if not using uv/tmux elsewhere
./uninstall_all.sh --remove-all-deps
```

### Multiple Projects

```bash
# Install CAO once
python3 install_cao.py

# Create multiple projects
python3 create_project.py project1
python3 create_project.py project2

# Install agents for each
cd project1 && python3 lcmp/install_agents.py && cd ..
cd project2 && python3 lcmp/install_agents.py && cd ..

# When done with all projects, clean up
./uninstall_all.sh --remove-uv-packages  # Keeps uv for future use
```

### Testing Different Providers

```bash
# Test with Kiro CLI
./install_all.sh test_kiro --provider kiro_cli

# Test with Q CLI
./install_all.sh test_q --provider q_cli

# Test with Claude Code
./install_all.sh test_claude --provider claude_code

# Clean up after testing
./uninstall_all.sh --remove-uv-packages
```

### Selective Cleanup Scenarios

```bash
# Scenario 1: Keep uv for other Python projects
./uninstall_all.sh --remove-uv-packages

# Scenario 2: Remove only tmux (keep uv and its packages)
./uninstall_all.sh --remove-tmux

# Scenario 3: Remove uv but keep tmux
./uninstall_all.sh --remove-uv

# Scenario 4: Complete cleanup
./uninstall_all.sh --remove-all-deps

# Scenario 5: Keep everything for later use
./uninstall_all.sh --keep-config --keep-cache
```

---

**Happy migrating! 🚀**
