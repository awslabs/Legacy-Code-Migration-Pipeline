#!/usr/bin/env python3
"""
Script to remove project-specific path variables from agent definition files.
Makes agents generic and reusable across projects.
"""

import re
import os
from pathlib import Path

# Standard replacement texts
SPECIALIST_INPUT_REPLACEMENT = """## Input Requirements

All input file paths and requirements are provided through task files created by the team supervisor. Task files contain:
- Complete list of input files with absolute paths
- Required templates and reference data
- All necessary context for task execution

Refer to your assigned task file for specific input locations and requirements."""

SPECIALIST_DELIVERABLES_REPLACEMENT = """## Expected Deliverables

All output file paths and specifications are provided through task files created by the team supervisor. Task files specify:
- Complete list of deliverables with absolute paths
- Required content and format for each deliverable
- Templates to follow
- Quality criteria and success metrics

Typical deliverables for this agent role are described in the task file provided by the supervisor.

Refer to your assigned task file for specific deliverable locations and detailed requirements."""

REVIEWER_INPUT_REPLACEMENT = """## Deliverables to Review

All deliverable file paths and review requirements are provided through task files created by the team supervisor. Task files contain:
- Complete list of deliverables to review with absolute paths
- Quality criteria and validation requirements
- Review checklist and approval criteria

Refer to your assigned task file for specific deliverable locations and review requirements."""


def remove_path_variables_from_section(content, section_start_pattern, section_end_pattern, replacement_text):
    """Remove a section containing path variables and replace with generic text."""
    pattern = f"({section_start_pattern})(.*?)({section_end_pattern})"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Replace the entire section
        new_content = content[:match.start()] + replacement_text + "\n\n" + match.group(3) + content[match.end():]
        return new_content
    return content


def clean_specialist_agent(filepath):
    """Clean a specialist agent file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Remove Input Requirements section if it contains path variables
    if '{{' in content and '## Input Requirements' in content:
        content = remove_path_variables_from_section(
            content,
            r'## Input Requirements',
            r'##',
            SPECIALIST_INPUT_REPLACEMENT
        )
    
    # Remove Expected Deliverables section if it contains path variables
    if '{{' in content and '## Expected Deliverables' in content:
        content = remove_path_variables_from_section(
            content,
            r'## Expected Deliverables',
            r'##',
            SPECIALIST_DELIVERABLES_REPLACEMENT
        )
    
    # Remove any remaining {{VARIABLE}} references in text
    content = re.sub(r'`\{\{[A-Z_]+\}\}`', '[provided in task file]', content)
    content = re.sub(r'\{\{[A-Z_]+\}\}', '[provided in task file]', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False


def clean_reviewer_agent(filepath):
    """Clean a reviewer agent file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Remove Deliverables to Review section if it contains path variables
    if '{{' in content and 'Deliverables to Review' in content:
        content = remove_path_variables_from_section(
            content,
            r'###? Deliverables to Review',
            r'##',
            REVIEWER_INPUT_REPLACEMENT
        )
    
    # Remove path variables from Feedback Documentation Format
    content = re.sub(
        r'\*\*File\*\*: `\{\{PROJECT_BASE_PATH\}\}[^`]+`',
        '**File**: [Path provided in task file]',
        content
    )
    
    # Remove any remaining {{VARIABLE}} references
    content = re.sub(r'`\{\{[A-Z_]+\}\}`', '[provided in task file]', content)
    content = re.sub(r'\{\{[A-Z_]+\}\}', '[provided in task file]', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False


def clean_supervisor_agent(filepath):
    """Clean a supervisor agent file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Remove Task Description File references
    content = re.sub(
        r'\*\*Task Description File\*\*: `\{\{PROJECT_BASE_PATH\}\}/tasks/[^`]+`',
        '**Task File Creation**: Create task file with all paths resolved from phase prompt',
        content
    )
    
    # Remove path variables from deliverables lists
    content = re.sub(r': `\{\{[A-Z_]+\}\}`', ': [Path provided in phase prompt]', content)
    
    # Remove any remaining {{VARIABLE}} references
    content = re.sub(r'`\{\{[A-Z_]+\}\}`', '[provided in phase prompt]', content)
    content = re.sub(r'\{\{[A-Z_]+\}\}', '[provided in phase prompt]', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Main function to clean all agent files."""
    agents_dir = Path('structure/agents')
    
    cleaned_count = 0
    total_count = 0
    
    for agent_file in agents_dir.rglob('*.md'):
        total_count += 1
        filename = agent_file.name
        
        print(f"Processing: {agent_file}")
        
        if 'specialist' in filename and 'supervisor' not in filename:
            if clean_specialist_agent(agent_file):
                print(f"  ✓ Cleaned specialist agent")
                cleaned_count += 1
        elif 'reviewer' in filename:
            if clean_reviewer_agent(agent_file):
                print(f"  ✓ Cleaned reviewer agent")
                cleaned_count += 1
        elif 'supervisor' in filename:
            if clean_supervisor_agent(agent_file):
                print(f"  ✓ Cleaned supervisor agent")
                cleaned_count += 1
        else:
            print(f"  - Skipped (unknown type)")
    
    print(f"\nSummary: Cleaned {cleaned_count} of {total_count} agent files")


if __name__ == '__main__':
    main()
