#!/usr/bin/env python3
"""
Prompts Update Script

This script copies ONLY the contents of the ./structure/prompts directory
into the {PATH_TO_PROJECT}/prompts directory and replaces all {{PARAMETER}}
placeholders with actual paths based on config/paths.cfg and the project path.

Usage: python update_prompts.py <path_to_project>

Example:
    python update_prompts.py /Users/kerimman/cd
    
    This will:
    1. Copy all files from ./structure/prompts to /Users/kerimman/cd/prompts
    2. Replace {{PROJECT_BASE_PATH}} with /Users/kerimman/cd
    3. Replace all other parameters from config/paths.cfg
"""

import os
import sys
import shutil
import argparse
import re
from pathlib import Path


def load_config_parameters(config_path, project_path):
    """Load and resolve all parameters from config file with dependency resolution."""
    if not os.path.exists(config_path):
        print(f"Warning: Config file '{config_path}' not found. Only PROJECT_BASE_PATH will be replaced.")
        return {
            'PROJECT_BASE_PATH': str(project_path)
        }
    
    # Read config file manually to handle the custom format
    parameters = {
        'PROJECT_BASE_PATH': str(project_path)
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
            return True
        return False
    
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Skipping binary/protected file: {file_path} ({e})")
        return False
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False


def update_prompts(source_prompts_dir, target_project_path, config_path):
    """Copy prompts directory to target project and replace placeholders."""
    source_path = Path(source_prompts_dir)
    target_path = Path(target_project_path).resolve()
    target_prompts_path = target_path / "prompts"
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source prompts directory '{source_prompts_dir}' does not exist")
    
    if not target_path.exists():
        raise FileNotFoundError(f"Target project directory '{target_project_path}' does not exist")
    
    print(f"Source prompts: {source_path}")
    print(f"Target project: {target_path}")
    print(f"Target prompts: {target_prompts_path}")
    
    # Create target prompts directory if it doesn't exist
    target_prompts_path.mkdir(parents=True, exist_ok=True)
    
    # Copy all contents from source prompts to target prompts
    print("\nCopying prompts...")
    copied_count = 0
    for item in source_path.rglob('*'):
        if item.is_file():
            # Calculate relative path from source prompts
            relative_path = item.relative_to(source_path)
            target_file = target_prompts_path / relative_path
            
            # Create parent directories if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(item, target_file)
            copied_count += 1
            print(f"  Copied: {relative_path}")
    
    print(f"\n✅ Copied {copied_count} files")
    
    # Load and resolve all parameters from config
    print("\nLoading configuration parameters...")
    parameters = load_config_parameters(config_path, target_path)
    
    print("Resolved parameters (sample):")
    sample_params = list(parameters.items())[:5]
    for key, value in sample_params:
        print(f"  {key} = {value}")
    if len(parameters) > 5:
        print(f"  ... and {len(parameters) - 5} more")
    
    # Walk through all copied files and replace placeholders
    print("\nReplacing placeholders in prompt files...")
    updated_count = 0
    for root, dirs, files in os.walk(target_prompts_path):
        for file in files:
            file_path = Path(root) / file
            if replace_placeholders_in_file(file_path, parameters):
                updated_count += 1
                print(f"  Updated: {file_path.relative_to(target_prompts_path)}")
    
    print(f"\n✅ Updated {updated_count} files with resolved parameters")
    print(f"✅ Prompts updated successfully at: {target_prompts_path}")
    return target_prompts_path


def main():
    parser = argparse.ArgumentParser(
        description="Update prompts in a project by copying from structure/prompts and replacing placeholders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python update_prompts.py /Users/kerimman/cd
  
  This will copy all files from ./structure/prompts to /Users/kerimman/cd/prompts
  and replace placeholders like {{PROJECT_BASE_PATH}} with /Users/kerimman/cd
        """
    )
    parser.add_argument(
        "project_path",
        help="Path to the target project directory"
    )
    parser.add_argument(
        "--source",
        default="structure/prompts",
        help="Source prompts directory to copy from (default: structure/prompts)"
    )
    parser.add_argument(
        "--config",
        default="config/paths.cfg",
        help="Configuration file with parameter definitions (default: config/paths.cfg)"
    )
    
    args = parser.parse_args()
    
    try:
        # Update prompts
        final_path = update_prompts(args.source, args.project_path, args.config)
        
        print(f"\n🎉 Prompts update complete!")
        print(f"📁 Location: {final_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
