#!/usr/bin/env python3
"""
Project Creation Script

This script copies all files and directories from the 'structure' directory
to a target directory and replaces all {{PARAMETER}} placeholders with
the actual paths based on config/paths.cfg configuration.

Usage: python create_project.py <project_name>
"""

import os
import sys
import shutil
import argparse
import re
from pathlib import Path
from configparser import ConfigParser


def load_config_parameters(config_path, project_path, project_name):
    """Load and resolve all parameters from config file with dependency resolution."""
    if not os.path.exists(config_path):
        print(f"Warning: Config file '{config_path}' not found. Only PROJECT_BASE_PATH and PROJECT_NAME will be replaced.")
        return {
            'PROJECT_BASE_PATH': str(project_path),
            'PROJECT_NAME': project_name
        }
    
    # Read config file manually to handle the custom format
    parameters = {
        'PROJECT_BASE_PATH': str(project_path),
        'PROJECT_NAME': project_name
    }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                # Clean up value - remove leading colons, spaces, and backticks
                value = value.strip().lstrip(':').strip().strip('`').strip()
                parameters[key] = value
    
    # Resolve parameter dependencies (parameters that reference other parameters)
    max_iterations = 10  # Prevent infinite loops
    for iteration in range(max_iterations):
        resolved_any = False
        
        for key, value in parameters.items():
            # Find all {{PARAMETER}} references in the value
            placeholder_pattern = r'\{\{([^}]+)\}\}'
            matches = re.findall(placeholder_pattern, value)
            
            for match in matches:
                if match in parameters:
                    # Replace the placeholder with the resolved value
                    old_value = value
                    value = value.replace(f'{{{{{match}}}}}', parameters[match])
                    parameters[key] = value
                    if old_value != value:
                        resolved_any = True
        
        # If no more resolutions were made, we're done
        if not resolved_any:
            break
    
    return parameters


def replace_placeholders_in_file(file_path, parameters):
    """Replace all {{PARAMETER}} placeholders in a file with resolved values."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all parameter placeholders
        for param_name, param_value in parameters.items():
            placeholder = f'{{{{{param_name}}}}}'
            if placeholder in content:
                content = content.replace(placeholder, param_value)
        
        # Only write back if there were changes
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated placeholders in: {file_path}")
    
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Skipping binary/protected file: {file_path} ({e})")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def copy_structure_and_replace(source_dir, target_dir, config_path):
    """Copy structure directory to target and replace placeholders."""
    source_path = Path(source_dir)
    target_path = Path(target_dir).resolve()
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist")
    
    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Copying from: {source_path}")
    print(f"Copying to: {target_path}")
    
    # Copy all contents from structure to target
    for item in source_path.iterdir():
        if item.is_file():
            shutil.copy2(item, target_path)
        elif item.is_dir():
            shutil.copytree(item, target_path / item.name, dirs_exist_ok=True)
    
    print(f"Files copied successfully to: {target_path}")
    
    # Load and resolve all parameters from config
    print("Loading configuration parameters...")
    parameters = load_config_parameters(config_path, target_path, target_path.name)
    
    print("Resolved parameters:")
    for key, value in parameters.items():
        print(f"  {key} = {value}")
    
    # Walk through all copied files and replace placeholders
    print("\nReplacing placeholders in files...")
    for root, dirs, files in os.walk(target_path):
        for file in files:
            file_path = Path(root) / file
            replace_placeholders_in_file(file_path, parameters)
    
    print(f"Project created successfully at: {target_path}")
    return target_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a new project by copying structure directory and replacing placeholders"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project directory to create"
    )
    parser.add_argument(
        "--source",
        default="structure",
        help="Source directory to copy from (default: structure)"
    )
    parser.add_argument(
        "--config",
        default="config/paths.cfg",
        help="Configuration file with parameter definitions (default: config/paths.cfg)"
    )
    
    args = parser.parse_args()
    
    try:
        # Get current working directory and create absolute target path
        current_dir = Path.cwd()
        target_dir = current_dir / args.project_name
        
        # Check if target already exists
        if target_dir.exists():
            response = input(f"Directory '{target_dir}' already exists. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        # Copy structure and replace placeholders
        final_path = copy_structure_and_replace(args.source, target_dir, args.config)
        
        print(f"\n✅ Project '{args.project_name}' created successfully!")
        print(f"📁 Location: {final_path}")
        
        # Install web-dashboard requirements
        print(f"\n📦 Installing Web Dashboard Requirements")
        web_dashboard_requirements = final_path / "web-dashboard" / "requirements.txt"
        if web_dashboard_requirements.exists():
            try:
                import subprocess
                print("Installing web-dashboard dependencies...")
                result = subprocess.run(
                    ["pip", "install", "-r", str(web_dashboard_requirements)],
                    cwd=str(final_path / "web-dashboard")
                )
                
                if result.returncode == 0:
                    print("✅ Web dashboard requirements installed successfully!")
                else:
                    print("⚠️  Web dashboard requirements installation had issues")
                    print(f"   You can install manually later using:")
                    print(f"   pip install -r {web_dashboard_requirements}")
            except Exception as e:
                print(f"⚠️  Error installing web dashboard requirements: {e}")
                print(f"   You can install manually later using:")
                print(f"   pip install -r {web_dashboard_requirements}")
        else:
            print("⚠️  Web dashboard requirements.txt not found")
        
        # Ask if user wants to install agents
        print(f"\n🤖 Agent Installation")
        print("Would you like to install agents now?")
        print("(You can also install them later using: python lcmp/install_agents.py)")
        response = input("Install agents now? (y/N): ")
        
        if response.lower() == 'y':
            # Check if CAO is installed
            try:
                import subprocess
                subprocess.run(["cao", "--help"], capture_output=True, check=True)
                cao_installed = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                cao_installed = False
            
            if not cao_installed:
                print("\n⚠️  CAO (CLI Agent Orchestrator) is not installed")
                print("Please install CAO first using: python install_cao.py")
                print("Then run: python lcmp/install_agents.py from your project directory")
            else:
                # Run the agent installation script
                print("\n🚀 Running agent installation...")
                try:
                    import subprocess
                    install_script = final_path / "lcmp" / "install_agents.py"
                    result = subprocess.run(
                        ["python3", str(install_script), "--agents-dir", str(final_path / "agents")],
                        cwd=str(final_path)
                    )
                    if result.returncode == 0:
                        print("\n✅ Agents installed successfully!")
                    else:
                        print("\n⚠️  Agent installation completed with issues")
                        print("You can retry later using: python lcmp/install_agents.py")
                except Exception as e:
                    print(f"\n⚠️  Error running agent installation: {e}")
                    print("You can install agents manually using: python lcmp/install_agents.py")
        else:
            print("\n📝 To install agents later, run from your project directory:")
            print("   python lcmp/install_agents.py")
        
        print(f"\n🎉 Setup complete!")
        print(f"\nNext steps:")
        print(f"1. cd {final_path}")
        if response.lower() != 'y' or not cao_installed:
            print(f"2. Install agents: python lcmp/install_agents.py")
        print(f"{'2' if response.lower() == 'y' and cao_installed else '3'}. Start using your agents with CAO")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()