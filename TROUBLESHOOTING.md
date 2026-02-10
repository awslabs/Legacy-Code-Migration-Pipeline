# Troubleshooting Guide

This guide covers common issues and solutions for the Legacy Code Migration Framework.

## Table of Contents

- [Installation Issues](#installation-issues)
- [ACM Tools Issues](#acm-tools-issues)
- [Kiro CLI Issues](#kiro-cli-issues)
- [CAO Issues](#cao-issues)
- [Agent Installation Issues](#agent-installation-issues)
- [Runtime Issues](#runtime-issues)

## Installation Issues

### CAO Not Found After Installation

**Problem**: `cao` command not found after running `install_cao.py`

**Solution**:
```bash
# Add uv tools to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make it permanent (choose your shell)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # for bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc   # for zsh

# Restart your shell
source ~/.bashrc  # or ~/.zshrc
```

**Verify**:
```bash
which cao
cao --help
```

### Python Not Found

**Problem**: `python3: command not found`

**Solution**:
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3

# Verify
python3 --version
```

### Git Not Found

**Problem**: `git: command not found`

**Solution**:
```bash
# macOS
brew install git
# or install Xcode Command Line Tools
xcode-select --install

# Ubuntu/Debian
sudo apt install git

# Verify
git --version
```

## ACM Tools Issues

### ACM Tools Download Fails

**Problem**: `install_acm_tools.py` fails to download from AWS Code

**Solution**:
```bash
# Check internet connection
ping code.aws.dev

# Check if behind proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Set proxy if needed
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Retry installation
python3 install_acm_tools.py --tools-dir ./tools
```

**Alternative**: Download manually
```bash
# Download the ZIP file manually from browser
# URL: https://code.aws.dev/personal_projects/alias_k/kerimman/acm-tools/-/archive/main/acm-tools-main.zip

# Extract to tools directory
unzip acm-tools-main.zip -d tools/
mv tools/acm-tools-main tools/acm-tools

# Install dependencies
cd tools/acm-tools
pip3 install -r requirements.txt
```

### ACM Tools Extraction Fails

**Problem**: ZIP extraction fails or corrupted archive

**Solution**:
```bash
# Remove corrupted download
rm -rf /tmp/acm-tools*

# Retry download
python3 install_acm_tools.py --tools-dir ./tools

# If still fails, download manually (see above)
```

### ACM Tools Dependencies Fail to Install

**Problem**: `pip install -r requirements.txt` fails

**Solution**:
```bash
# Ensure pip is up to date
pip3 install --upgrade pip

# Try installing dependencies manually
cd tools/acm-tools
pip3 install -r requirements.txt --verbose

# If specific package fails, install individually
pip3 install <package-name>

# Check Python version (requires 3.7+)
python3 --version
```

### Permission Denied for Tools Directory

**Problem**: Cannot write to tools directory

**Solution**:
```bash
# Check directory permissions
ls -la ./tools

# Fix permissions
chmod 755 ./tools

# Or install to different location
python3 install_acm_tools.py --tools-dir ~/my-tools

# Or use sudo (not recommended)
sudo python3 install_acm_tools.py --tools-dir ./tools
```

### ACM Tools Already Exist

**Problem**: Tools directory already exists

**Solution**:
```bash
# The script automatically removes old version
# But if you want to backup first:
mv tools/acm-tools tools/acm-tools.backup

# Then reinstall
python3 install_acm_tools.py --tools-dir ./tools

# Or force reinstall (script does this automatically)
rm -rf tools/acm-tools
python3 install_acm_tools.py --tools-dir ./tools
```

### Using Local ZIP File for Private Repository

**Problem**: Repository is private and you can't download directly

**Solution**:
```bash
# Step 1: Get the ZIP file
# - Request access from repository owner
# - Or receive the ZIP file through other means
# - Or download manually if you have access

# Step 2: Install from local ZIP
python3 install_acm_tools.py --zip-file /path/to/acm-tools-main.zip --tools-dir ./tools

# Step 3: Verify installation
ls -la tools/acm-tools/
```

**For Project Creation**:
```bash
# Create project first (will skip ACM tools if download fails)
python3 create_project.py my_project

# Then install ACM tools manually with local ZIP
cd my_project
python3 ../install_acm_tools.py --zip-file /path/to/acm-tools-main.zip --tools-dir ./tools
```

### Network Timeout During Download

**Problem**: Download times out or is very slow

**Solution**:
```bash
# Increase timeout (modify script if needed)
# Or download manually and extract

# Check network speed
curl -o /dev/null https://code.aws.dev/

# Try different network connection
# Or download during off-peak hours
```

## Kiro CLI Issues

### Authentication Error (AccessDeniedException)

**Problem**: When using `kiro-cli`, you see:
```
Error { code: "AccessDeniedException", 
        message: "The bearer token included in the request is invalid." }
```

**Cause**: Your Kiro CLI authentication token has expired or is invalid.

**Solution**:
```bash
# Logout from Kiro CLI
kiro-cli logout

# Login again to get a fresh token
kiro-cli login
```

**When This Happens**:
- Your session has expired
- You haven't used `kiro-cli` in a while
- AWS credentials have been refreshed
- After system restart or long idle time

**Verification**:
```bash
# Test with a simple prompt
kiro-cli chat "Hello, test message"
```

### Kiro CLI Not Found

**Problem**: `kiro-cli: command not found`

**Solution**:
```bash
# Check if installed
which kiro-cli

# If not found, install Kiro CLI
# Visit: https://kiro.ai

# Verify installation
kiro-cli --version
```

### Kiro CLI vs Kiro IDE

**Note**: Kiro CLI (command-line tool) and Kiro IDE are separate:
- **Kiro IDE**: The desktop application (what you're using now)
- **kiro-cli**: The command-line tool for terminal use

They have **separate authentication contexts**. If Kiro IDE works but `kiro-cli` doesn't, you need to authenticate `kiro-cli` separately using `kiro-cli logout` and `kiro-cli login`.

## CAO Issues

### CAO Commands Not Working

**Problem**: CAO commands fail or show errors

**Common Issues**:

1. **Wrong command syntax**:
   ```bash
   # Wrong
   cao agent install my_agent.md
   
   # Correct
   cao install my_agent.md --provider kiro_cli
   ```

2. **CAO not initialized**:
   ```bash
   # Initialize CAO
   cao init
   ```

3. **tmux not running**:
   ```bash
   # Check tmux version
   tmux -V
   
   # Should be 3.3 or higher
   ```

### CAO Installation Fails

**Problem**: `install_cao.py` fails during installation

**Solutions**:

1. **Check prerequisites**:
   ```bash
   # Verify Python
   python3 --version
   
   # Verify Git
   git --version
   ```

2. **Network issues**:
   ```bash
   # Test connectivity
   ping github.com
   
   # Check firewall settings
   ```

3. **Permission issues**:
   ```bash
   # Ensure you have write permissions
   ls -la ~/.local/bin
   
   # If needed, create directory
   mkdir -p ~/.local/bin
   ```

## Agent Installation Issues

### Agents Not Installing

**Problem**: `install_agents.py` fails to install agents

**Solutions**:

1. **CAO not installed**:
   ```bash
   # Verify CAO is installed
   cao --help
   
   # If not, install it
   python3 install_cao.py
   ```

2. **Wrong directory**:
   ```bash
   # Ensure you're in the project directory
   pwd
   
   # Should show: /path/to/your_project
   
   # Check agents directory exists
   ls -la agents/
   ```

3. **Provider not available**:
   ```bash
   # Check if provider CLI is installed
   kiro-cli --version  # for kiro_cli
   q --version         # for q_cli
   
   # Or use a different provider
   python3 acm/install_agents.py --provider claude_code
   ```

### Agent Files Not Found

**Problem**: Script can't find agent markdown files

**Solution**:
```bash
# Verify agents directory structure
ls -la agents/
ls -la agents/*/

# Should see .md files in subdirectories

# If missing, recreate project
cd ..
python3 create_project.py new_project_name
```

### Agents Not Visible in Kiro

**Problem**: Agents installed but not showing in Kiro IDE

**Solution**:
```bash
# Check agent files were created
ls -la ~/.kiro/agents/

# Should see .json files for each agent

# Restart Kiro IDE
# The agents should appear in the agent panel
```

## Runtime Issues

### Agent Fails to Launch

**Problem**: `cao launch --agents <name>` fails

**Solutions**:

1. **Agent not installed**:
   ```bash
   # Check agent exists
   ls ~/.kiro/agents/<agent_name>.json
   
   # Reinstall if missing
   cd your_project
   python3 acm/install_agents.py
   ```

2. **tmux issues**:
   ```bash
   # Check tmux is running
   tmux ls
   
   # Kill old sessions if needed
   cao shutdown
   ```

3. **Port conflicts**:
   ```bash
   # Check for port conflicts
   lsof -i :8000  # or whatever port CAO uses
   
   # Kill conflicting process if needed
   ```

### Agent Gives Unexpected Responses

**Problem**: Agent behavior is not as expected

**Solutions**:

1. **Check agent configuration**:
   ```bash
   # View agent config
   cat ~/.kiro/agents/<agent_name>.json
   
   # View agent context
   cat ~/.aws/cli-agent-orchestrator/agent-context/<agent_name>.md
   ```

2. **Update agents**:
   ```bash
   # Modify agent files in your project
   vim agents/<team>/<agent_name>.md
   
   # Reinstall
   python3 acm/install_agents.py
   ```

3. **Check paths in agent files**:
   - Ensure all `{{PARAMETER}}` placeholders were replaced
   - Verify paths point to correct locations

## AWS Credential Issues

### AWS Credentials Expired

**Problem**: AWS-related errors when using Kiro CLI

**Solution**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# If expired, refresh them
aws sso login  # if using SSO

# Or reconfigure
aws configure

# Then logout/login Kiro CLI
kiro-cli logout
kiro-cli login
```

## Network Issues

### Cannot Download Dependencies

**Problem**: Installation fails due to network issues

**Solutions**:

1. **Check connectivity**:
   ```bash
   ping github.com
   ping pypi.org
   ```

2. **Proxy settings**:
   ```bash
   # Set proxy if behind corporate firewall
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   ```

3. **Firewall**:
   - Check firewall settings
   - Ensure ports 80, 443 are open
   - Contact IT if behind corporate firewall

## Getting More Help

### Enable Debug Logging

```bash
# For Python scripts
export PYTHONVERBOSE=1
python3 install_cao.py

# For Kiro CLI
export RUST_BACKTRACE=1
kiro-cli chat "test"

# For CAO
# Check CAO logs (location varies)
```

### Check Log Files

```bash
# CAO logs
ls -la ~/.aws/cli-agent-orchestrator/

# Kiro logs
ls -la ~/.kiro/logs/

# Installation logs
cat install_test.log  # if you redirected output
```

### Collect System Information

```bash
# System info
uname -a

# Python version
python3 --version

# Installed tools
which cao
which kiro-cli
which tmux
which uv

# Tool versions
cao --help
kiro-cli --version
tmux -V
uv --version
```

## Common Error Messages

### "No such command 'list'"

**Error**: `cao list` gives "No such command 'list'"

**Explanation**: CAO doesn't have a `list` command. Agents are managed through Kiro.

**Solution**: Check agents in Kiro IDE or look at files:
```bash
ls ~/.kiro/agents/
```

### "Distribution not found"

**Error**: MCP server errors about distributions not found

**Explanation**: This is a Kiro IDE MCP configuration issue, not related to the migration framework.

**Solution**: Check your `~/.kiro/settings/mcp.json` and fix or disable problematic MCP servers.

### "Project directory already exists"

**Error**: `create_project.py` warns directory exists

**Solution**:
```bash
# Use a different name
python3 create_project.py different_name

# Or remove existing directory
rm -rf existing_project_name
```

## Still Having Issues?

If you're still experiencing problems:

1. **Review Documentation**:
   - [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
   - [QUICK_START.md](QUICK_START.md)
   - [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md)

2. **Check Prerequisites**:
   - Python 3.7+
   - Git
   - Internet connection
   - Sufficient disk space

3. **Try Clean Installation**:
   ```bash
   # Uninstall everything
   ./uninstall_all.sh
   
   # Reinstall
   ./install_all.sh new_project
   ```

4. **Use Alternative Provider**:
   ```bash
   # If kiro_cli has issues, try claude_code
   python3 acm/install_agents.py --provider claude_code
   ```

## Quick Reference

### Most Common Issues and Solutions

| Issue | Quick Fix |
|-------|-----------|
| CAO not found | `export PATH="$HOME/.local/bin:$PATH"` |
| Kiro CLI auth error | `kiro-cli logout && kiro-cli login` |
| Agents not installing | Check you're in project directory |
| Agent not launching | Verify agent installed: `ls ~/.kiro/agents/` |
| AWS credentials expired | `aws sso login` then `kiro-cli logout && kiro-cli login` |

---

**Remember**: Most issues are related to authentication, PATH configuration, or being in the wrong directory. Check these first!
