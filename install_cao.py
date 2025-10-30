#!/usr/bin/env python3
"""
CAO (CLI Agent Orchestrator) Installation Script

This script should be run AFTER create_project.py to install and configure
the CLI Agent Orchestrator (CAO) from https://github.com/awslabs/cli-agent-orchestrator

Features:
1. Installs tmux (version 3.3+) using official installer
2. Installs uv using official installer
3. Installs CAO using uv tool install
4. Configures all agents found in the project's agents folder

Usage: python install_cao.py <project_directory>
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path


def run_command(command, shell=False, check=True, capture_output=False):
    """Run a command and handle errors gracefully."""
    try:
        # Ensure uv tools are in PATH
        import os
        uv_bin_path = os.path.expanduser("~/.local/bin")
        current_path = os.environ.get("PATH", "")
        if uv_bin_path not in current_path:
            os.environ["PATH"] = f"{uv_bin_path}:{current_path}"
        
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=shell, check=check)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(command) if isinstance(command, list) else command}")
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0] if isinstance(command, list) else command}")
        return False


def check_command_exists(command):
    """Check if a command exists in the system PATH."""
    # First try the standard approach
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # For CAO, try --help instead of --version
    if command == "cao":
        try:
            subprocess.run([command, "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # Try with explicit PATH including uv tools directory
    import os
    uv_bin_path = os.path.expanduser("~/.local/bin")
    current_path = os.environ.get("PATH", "")
    if uv_bin_path not in current_path:
        new_path = f"{uv_bin_path}:{current_path}"
        env = os.environ.copy()
        env["PATH"] = new_path
        
        try:
            if command == "cao":
                subprocess.run([command, "--help"], capture_output=True, check=True, env=env)
            else:
                subprocess.run([command, "--version"], capture_output=True, check=True, env=env)
            # Update the current process PATH for subsequent calls
            os.environ["PATH"] = new_path
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    return False


def install_tmux_fallback():
    """Fallback tmux installation using system package managers."""
    print("📦 Attempting fallback tmux installation...")
    
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        if check_command_exists("brew"):
            print("Using Homebrew to install tmux...")
            return run_command(["brew", "install", "tmux"])
        else:
            print("❌ Homebrew not found. Please install tmux manually:")
            print("  1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("  2. Run: brew install tmux")
            return False
    elif system == "linux":
        # Try different package managers
        if check_command_exists("apt"):
            print("Using apt to install tmux...")
            return (run_command(["sudo", "apt", "update"]) and 
                   run_command(["sudo", "apt", "install", "-y", "tmux"]))
        elif check_command_exists("yum"):
            print("Using yum to install tmux...")
            return run_command(["sudo", "yum", "install", "-y", "tmux"])
        elif check_command_exists("dnf"):
            print("Using dnf to install tmux...")
            return run_command(["sudo", "dnf", "install", "-y", "tmux"])
        else:
            print("❌ No supported package manager found. Please install tmux manually.")
            return False
    else:
        print(f"❌ Unsupported operating system: {system}")
        print("Please install tmux 3.3+ manually")
        return False


def install_tmux():
    """Install tmux using the official CAO installer script."""
    print("📦 Installing tmux (version 3.3+ required)...")
    
    # Check if tmux is already installed and version is sufficient
    if check_command_exists("tmux"):
        try:
            version_output = run_command(["tmux", "-V"], capture_output=True)
            if version_output:
                # Extract version number (format: "tmux 3.3a")
                version_str = version_output.split()[1]
                # Remove any letter suffix (like 'a' in '3.3a')
                version_num = ''.join(c for c in version_str if c.isdigit() or c == '.')
                major, minor = map(int, version_num.split('.')[:2])
                
                if major > 3 or (major == 3 and minor >= 3):
                    print("✅ tmux 3.3+ is already installed")
                    return True
                else:
                    print(f"⚠️  tmux version {version_str} found, but 3.3+ is required")
        except Exception:
            print("⚠️  Could not determine tmux version, proceeding with installation")
    
    # Install using official CAO tmux installer
    print("📥 Using official CAO tmux installer...")
    
    # Download and execute the script in two steps to avoid bash process substitution issues
    download_cmd = "curl -s https://raw.githubusercontent.com/awslabs/cli-agent-orchestrator/refs/heads/main/tmux-install.sh"
    execute_cmd = "bash"
    
    try:
        # Download the script
        result = subprocess.run(download_cmd, shell=True, capture_output=True, text=True, check=True)
        script_content = result.stdout
        
        # Execute the script
        process = subprocess.run(execute_cmd, input=script_content, shell=True, text=True, check=True)
        
        print("✅ tmux installation completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install tmux using CAO installer")
        print(f"Error: {e}")
        print("Trying fallback installation method...")
        return install_tmux_fallback()


def install_uv():
    """Install uv using the official installer."""
    print("📦 Installing uv...")
    
    if check_command_exists("uv"):
        print("✅ uv is already installed")
        return True
    
    # Install uv using the official installer
    install_script = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    if not run_command(install_script, shell=True):
        print("❌ Failed to install uv. Please install manually: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    
    print("✅ uv installation completed")
    print("📝 Note: You may need to restart your shell or run 'source ~/.bashrc' to use uv")
    return True


def install_cao():
    """Install CLI Agent Orchestrator using uv tool install."""
    print("📦 Installing CLI Agent Orchestrator...")
    
    # Check if cao is already installed
    if check_command_exists("cao"):
        print("✅ CAO is already installed")
        response = input("Upgrade to latest version? (Y/n): ")
        if response.lower() == 'n':
            return True
    
    # Install CAO using uv tool install
    install_command = [
        "uv", "tool", "install", 
        "git+https://github.com/awslabs/cli-agent-orchestrator.git@main",
        "--upgrade"
    ]
    
    if not run_command(install_command):
        print("❌ Failed to install CAO")
        print("Make sure uv is properly installed and in your PATH")
        return False
    
    print("✅ CAO installation completed")
    return True


def install_dependencies():
    """Install all required dependencies."""
    print("🔧 Installing required dependencies...")
    
    # Check git first
    if not check_command_exists("git"):
        print("❌ Git is required but not found. Please install git first.")
        return False
    else:
        print("✅ git is available")
    
    # Install tmux
    if not install_tmux():
        return False
    
    # Install uv
    if not install_uv():
        return False
    
    # Install CAO
    if not install_cao():
        return False
    
    return True


def verify_cao_installation():
    """Verify that CAO is properly installed and accessible."""
    print("🔍 Verifying CAO installation...")
    
    if not check_command_exists("cao"):
        print("❌ CAO command not found in PATH")
        print("You may need to restart your shell or add uv tools to your PATH")
        print("Try running: export PATH=\"$HOME/.local/bin:$PATH\"")
        return False
    
    # Test CAO help command
    try:
        result = run_command(["cao", "--help"], capture_output=True)
        if result:
            print("✅ CAO is properly installed and accessible")
            
            # Check available commands
            print("🔍 Checking available CAO commands...")
            help_output = run_command(["cao", "--help"], capture_output=True, check=False)
            if help_output and "install" in help_output.lower():
                print("✅ CAO install command is available")
            else:
                print("⚠️  CAO install command may not be available")
            
            return True
    except Exception as e:
        print(f"❌ Error testing CAO: {e}")
    
    print("❌ CAO installation verification failed")
    return False


def get_agent_files(project_dir):
    """Get all agent files from the agents directory and subdirectories."""
    agents_dir = project_dir / "agents"
    
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return []
    
    # Use recursive glob to find all .md files in agents directory and subdirectories
    agent_files = list(agents_dir.glob("**/*.md"))
    return agent_files


def parse_agent_metadata(agent_file):
    """Parse the YAML frontmatter from an agent file to get the agent name."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    metadata = yaml.safe_load(parts[1])
                    return metadata.get('name', agent_file.stem)
                except ImportError:
                    # Fallback: simple parsing for name field
                    for line in parts[1].split('\n'):
                        if line.strip().startswith('name:'):
                            return line.split(':', 1)[1].strip().strip('"\'')
                except Exception:
                    # If YAML parsing fails, fall back to simple parsing
                    for line in parts[1].split('\n'):
                        if line.strip().startswith('name:'):
                            return line.split(':', 1)[1].strip().strip('"\'')
        
        # Fallback to filename
        return agent_file.stem
    
    except Exception as e:
        print(f"Warning: Could not parse metadata from {agent_file}: {e}")
        return agent_file.stem


def install_agents(project_dir):
    """Install all agents found in the agents directory."""
    print("🤖 Installing agents in project directory...")
    
    agent_files = get_agent_files(project_dir)
    
    if not agent_files:
        print("❌ No agent files found in the agents directory")
        return False
    
    print(f"Found {len(agent_files)} agent files:")
    for agent_file in agent_files:
        agent_name = parse_agent_metadata(agent_file)
        print(f"  - {agent_name} ({agent_file.name})")
    
    # Ask user which agents to install
    response = input(f"\nInstall all {len(agent_files)} agents? (Y/n): ")
    if response.lower() == 'n':
        # Let user select specific agents
        selected_agents = []
        for agent_file in agent_files:
            agent_name = parse_agent_metadata(agent_file)
            response = input(f"Install {agent_name}? (y/N): ")
            if response.lower() == 'y':
                selected_agents.append(agent_file)
        agent_files = selected_agents
    
    if not agent_files:
        print("No agents selected for installation.")
        return True
    
    # Change to project directory for agent installation
    original_cwd = os.getcwd()
    success_count = 0
    
    try:
        os.chdir(project_dir)
        
        # First, check what CAO commands are available
        print("\n🔍 Checking available CAO commands...")
        help_output = run_command(["cao", "--help"], capture_output=True)
        if help_output:
            print("✅ CAO is responding")
        
        # Install each selected agent
        for agent_file in agent_files:
            agent_name = parse_agent_metadata(agent_file)
            print(f"\n📦 Installing agent: {agent_name}")
            print(f"   File: {agent_file.name}")
            
            # Method 1: Try cao install (correct command)
            install_command = ["cao", "install", str(agent_file.resolve())]
            
            if run_command(install_command, check=False):
                print(f"✅ Successfully installed agent: {agent_name}")
                success_count += 1
                continue
            
            # Method 3: Try copying the file to agents directory
            print(f"🔄 Trying direct file copy for {agent_name}...")
            agents_config_dir = project_dir / ".cao" / "agents"
            agents_config_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                target_file = agents_config_dir / f"{agent_name}.md"
                shutil.copy2(agent_file, target_file)
                print(f"✅ Successfully copied agent {agent_name} to CAO agents directory")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to copy agent {agent_name}: {e}")
    
    finally:
        os.chdir(original_cwd)
    
    print(f"\n🎉 Successfully installed {success_count}/{len(agent_files)} agents")
    
    # Verify agent installation by checking if agent files exist in project
    if success_count > 0:
        print("\n🔍 Verifying agent installation...")
        agents_dir = project_dir / "agents"
        if agents_dir.exists():
            # Use recursive glob to find all agent files including those in subdirectories
            installed_agents = list(agents_dir.glob("**/*.md"))
            print(f"✅ Found {len(installed_agents)} agent files in project:")
            for agent_file in installed_agents:
                agent_name = parse_agent_metadata(agent_file)
                # Show relative path from agents directory for better organization visibility
                relative_path = agent_file.relative_to(agents_dir)
                print(f"  - {agent_name} ({relative_path})")
        else:
            print("⚠️  Agents directory not found")
    
    return success_count > 0


def setup_cao_environment(project_dir):
    """Set up CAO environment in the project directory."""
    print("⚙️  Setting up CAO environment in project...")
    
    # Change to project directory
    original_cwd = os.getcwd()
    try:
        os.chdir(project_dir)
        
        # Initialize CAO in project directory
        print("🔧 Initializing CAO in project directory...")
        if not run_command(["cao", "init"], check=False):
            print("Note: CAO init may have failed, but this might be expected if already initialized")
        
        # Create .cao directory if it doesn't exist
        cao_config_dir = project_dir / ".cao"
        cao_config_dir.mkdir(exist_ok=True)
        
        print("✅ CAO environment setup complete")
        return True
        
    finally:
        os.chdir(original_cwd)


def main():
    parser = argparse.ArgumentParser(
        description="Install CLI Agent Orchestrator (CAO) and configure agents"
    )
    parser.add_argument(
        "project_directory",
        help="Path to the project directory created by create_project.py"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation"
    )
    parser.add_argument(
        "--skip-agents",
        action="store_true", 
        help="Skip agent installation"
    )
    
    args = parser.parse_args()
    
    # Validate project directory
    project_dir = Path(args.project_directory).resolve()
    if not project_dir.exists():
        print(f"❌ Project directory does not exist: {project_dir}")
        print("Please run create_project.py first to create the project structure.")
        sys.exit(1)
    
    print(f"🚀 Installing CAO for project: {project_dir}")
    
    try:
        # Step 1: Install dependencies
        if not args.skip_deps:
            if not install_dependencies():
                print("❌ Failed to install dependencies")
                sys.exit(1)
        else:
            print("⏭️  Skipping dependency installation")
        
        # Step 2: Verify CAO installation
        if not verify_cao_installation():
            print("❌ CAO installation verification failed")
            sys.exit(1)
        
        # Step 3: Setup CAO environment in project
        if not setup_cao_environment(project_dir):
            print("❌ Failed to setup CAO environment")
            sys.exit(1)
        
        # Step 4: Install agents
        if not args.skip_agents:
            if not install_agents(project_dir):
                print("⚠️  Agent installation completed with some issues")
        else:
            print("⏭️  Skipping agent installation")
        
        print(f"\n🎉 CAO installation complete!")
        print(f"📁 Project location: {project_dir}")
        print("\nNext steps:")
        print(f"1. cd {project_dir}")
        print("2. Start CAO server: cao-server")
        print("3. In another terminal: cao launch --agents <agent_name>")
        print("\nUseful commands:")
        print("• Start server: cao-server")
        print("• Install agent: cao install <agent_file>")
        print("• Launch session: cao launch --agents <agent_name>")
        print("• Get help: cao --help")
        print("• Available agents are in the agents/ directory")
        print("\nNote: The CAO server must be running to launch agent sessions.")
        print("\nUninstall CAO (if needed):")
        print("• uv tool uninstall cli-agent-orchestrator")
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()