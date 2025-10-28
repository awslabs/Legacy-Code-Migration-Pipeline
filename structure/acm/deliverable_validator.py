#!/usr/bin/env python3
"""
Deliverable Validator Tool

This tool validates that all deliverable files in the project output correspond to available 
templates and conform to their expected structure. It scans the output folder recursively 
and checks if each deliverable has a matching template in the templates folder. 
For supported file types, it also validates content structure:
- JSON: Validates JSON structure matches template
- Markdown: Validates chapter structure (headers) matches template
- CSV: Validates headers match template
"""

import os
import sys
import json
import csv
import re
from pathlib import Path
from typing import List, Tuple, Set, Dict, Any, Optional
import argparse


class ValidationResult:
    def __init__(self, file_path: str, template_exists: bool = False, 
                 content_valid: bool = False, errors: List[str] = None):
        self.file_path = file_path
        self.template_exists = template_exists
        self.content_valid = content_valid
        self.errors = errors or []


class DeliverableValidator:
    def __init__(self, project_base_path: str):
        self.project_base_path = Path(project_base_path)
        self.output_path = self.project_base_path / "output"
        self.templates_path = self.project_base_path / "templates"
        
    def get_template_files(self) -> Set[str]:
        """Get all available template filenames."""
        if not self.templates_path.exists():
            print(f"WARNING: Templates directory not found: {self.templates_path}")
            return set()
            
        template_files = set()
        for file_path in self.templates_path.rglob("*"):
            if file_path.is_file():
                template_files.add(file_path.name)
        
        return template_files
    
    def get_output_files(self) -> List[Path]:
        """Get all files in the output directory recursively."""
        if not self.output_path.exists():
            print(f"WARNING: Output directory not found: {self.output_path}")
            return []
            
        output_files = []
        for file_path in self.output_path.rglob("*"):
            if file_path.is_file():
                output_files.append(file_path)
        
        return output_files
    
    def get_json_structure(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract JSON structure (keys and types) from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._extract_json_structure(data)
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
            return None
    
    def _extract_json_structure(self, obj: Any, path: str = "") -> Dict[str, Any]:
        """Recursively extract structure from JSON object."""
        if isinstance(obj, dict):
            structure = {}
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, (dict, list)):
                    structure[key] = self._extract_json_structure(value, current_path)
                else:
                    structure[key] = type(value).__name__
            return structure
        elif isinstance(obj, list):
            if obj:
                # Use structure of first item as template for array
                return [self._extract_json_structure(obj[0], f"{path}[0]")]
            else:
                return []
        else:
            return type(obj).__name__
    
    def get_markdown_headers(self, file_path: Path) -> Optional[List[Tuple[int, str]]]:
        """Extract markdown headers (level and text) from a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            headers = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('#'):
                    # Count the number of # characters
                    level = 0
                    for char in line:
                        if char == '#':
                            level += 1
                        else:
                            break
                    
                    # Extract header text
                    header_text = line[level:].strip()
                    if header_text:
                        headers.append((level, header_text))
            
            return headers
        except (FileNotFoundError, UnicodeDecodeError):
            return None
    
    def get_csv_headers(self, file_path: Path) -> Optional[List[str]]:
        """Extract CSV headers from a CSV file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                return headers if headers else []
        except (FileNotFoundError, UnicodeDecodeError, csv.Error):
            return None
    
    def validate_json_content(self, output_file: Path, template_file: Path) -> List[str]:
        """Validate JSON structure matches template."""
        errors = []
        
        output_structure = self.get_json_structure(output_file)
        template_structure = self.get_json_structure(template_file)
        
        if output_structure is None:
            errors.append("Failed to parse output JSON file")
        if template_structure is None:
            errors.append("Failed to parse template JSON file")
        
        if output_structure is not None and template_structure is not None:
            structure_errors = self._compare_json_structures(
                template_structure, output_structure, "root"
            )
            errors.extend(structure_errors)
        
        return errors
    
    def _compare_json_structures(self, template: Any, output: Any, path: str) -> List[str]:
        """Compare JSON structures recursively."""
        errors = []
        
        if isinstance(template, dict) and isinstance(output, dict):
            # Check for missing keys in output
            for key in template.keys():
                if key not in output:
                    errors.append(f"Missing key '{key}' at {path}")
                else:
                    sub_errors = self._compare_json_structures(
                        template[key], output[key], f"{path}.{key}"
                    )
                    errors.extend(sub_errors)
            
            # Check for extra keys in output
            for key in output.keys():
                if key not in template:
                    errors.append(f"Extra key '{key}' at {path}")
        
        elif isinstance(template, list) and isinstance(output, list):
            if template and output:
                # Compare structure of first elements
                sub_errors = self._compare_json_structures(
                    template[0], output[0], f"{path}[0]"
                )
                errors.extend(sub_errors)
        
        elif isinstance(template, str) and isinstance(output, str):
            # Both are type names, they should match
            if template != output:
                errors.append(f"Type mismatch at {path}: expected {template}, got {output}")
        
        else:
            # Type mismatch
            template_type = type(template).__name__
            output_type = type(output).__name__
            errors.append(f"Structure mismatch at {path}: expected {template_type}, got {output_type}")
        
        return errors
    
    def validate_markdown_content(self, output_file: Path, template_file: Path) -> List[str]:
        """Validate markdown header structure matches template."""
        errors = []
        
        output_headers = self.get_markdown_headers(output_file)
        template_headers = self.get_markdown_headers(template_file)
        
        if output_headers is None:
            errors.append("Failed to parse output markdown file")
        if template_headers is None:
            errors.append("Failed to parse template markdown file")
        
        if output_headers is not None and template_headers is not None:
            if len(output_headers) != len(template_headers):
                errors.append(f"Header count mismatch: expected {len(template_headers)}, got {len(output_headers)}")
            
            for i, (template_header, output_header) in enumerate(zip(template_headers, output_headers)):
                template_level, template_text = template_header
                output_level, output_text = output_header
                
                if template_level != output_level:
                    errors.append(f"Header {i+1} level mismatch: expected level {template_level}, got level {output_level}")
                
                if template_text != output_text:
                    errors.append(f"Header {i+1} text mismatch: expected '{template_text}', got '{output_text}'")
        
        return errors
    
    def validate_csv_content(self, output_file: Path, template_file: Path) -> List[str]:
        """Validate CSV headers match template."""
        errors = []
        
        output_headers = self.get_csv_headers(output_file)
        template_headers = self.get_csv_headers(template_file)
        
        if output_headers is None:
            errors.append("Failed to parse output CSV file")
        if template_headers is None:
            errors.append("Failed to parse template CSV file")
        
        if output_headers is not None and template_headers is not None:
            if len(output_headers) != len(template_headers):
                errors.append(f"Header count mismatch: expected {len(template_headers)}, got {len(output_headers)}")
            
            for i, (template_header, output_header) in enumerate(zip(template_headers, output_headers)):
                if template_header != output_header:
                    errors.append(f"Header {i+1} mismatch: expected '{template_header}', got '{output_header}'")
            
            # Check for missing headers
            missing_headers = set(template_headers) - set(output_headers)
            if missing_headers:
                errors.append(f"Missing headers: {', '.join(missing_headers)}")
            
            # Check for extra headers
            extra_headers = set(output_headers) - set(template_headers)
            if extra_headers:
                errors.append(f"Extra headers: {', '.join(extra_headers)}")
        
        return errors
    
    def validate_file_content(self, output_file: Path, template_file: Path) -> List[str]:
        """Validate file content based on file extension."""
        file_ext = output_file.suffix.lower()
        
        if file_ext == '.json':
            return self.validate_json_content(output_file, template_file)
        elif file_ext in ['.md', '.markdown']:
            return self.validate_markdown_content(output_file, template_file)
        elif file_ext == '.csv':
            return self.validate_csv_content(output_file, template_file)
        else:
            # For other file types, just check if template exists
            return []
    
    def validate_files(self) -> List[ValidationResult]:
        """
        Validate output files against templates.
        
        Returns:
            List of ValidationResult objects
        """
        template_files = self.get_template_files()
        output_files = self.get_output_files()
        
        results = []
        
        for output_file in output_files:
            filename = output_file.name
            relative_path = str(output_file.relative_to(self.output_path))
            
            if filename in template_files:
                # Template exists, now validate content
                template_file = self.templates_path / filename
                content_errors = self.validate_file_content(output_file, template_file)
                
                result = ValidationResult(
                    file_path=relative_path,
                    template_exists=True,
                    content_valid=len(content_errors) == 0,
                    errors=content_errors
                )
            else:
                # No template found
                result = ValidationResult(
                    file_path=relative_path,
                    template_exists=False,
                    content_valid=False,
                    errors=["No corresponding template found"]
                )
            
            results.append(result)
        
        return results
    
    def print_validation_report(self):
        """Print a comprehensive validation report."""
        print("=" * 80)
        print("DELIVERABLE VALIDATION REPORT")
        print("=" * 80)
        print(f"Project Base Path: {self.project_base_path}")
        print(f"Output Path: {self.output_path}")
        print(f"Templates Path: {self.templates_path}")
        print()
        
        # Get available templates
        template_files = self.get_template_files()
        print(f"Available Templates ({len(template_files)}):")
        for template in sorted(template_files):
            print(f"  ✓ {template}")
        print()
        
        # Validate files
        results = self.validate_files()
        
        # Categorize results
        fully_valid = []
        template_exists_content_invalid = []
        no_template = []
        
        for result in results:
            if result.template_exists and result.content_valid:
                fully_valid.append(result)
            elif result.template_exists and not result.content_valid:
                template_exists_content_invalid.append(result)
            else:
                no_template.append(result)
        
        # Print fully valid files
        if fully_valid:
            print(f"✅ FULLY VALID FILES ({len(fully_valid)}):")
            for result in sorted(fully_valid, key=lambda x: x.file_path):
                print(f"  ✅ {result.file_path}")
            print()
        
        # Print files with template but content issues
        if template_exists_content_invalid:
            print(f"⚠️  FILES WITH CONTENT VALIDATION ERRORS ({len(template_exists_content_invalid)}):")
            for result in sorted(template_exists_content_invalid, key=lambda x: x.file_path):
                print(f"  ⚠️  {result.file_path}")
                for error in result.errors:
                    print(f"      • {error}")
            print()
        
        # Print files without templates
        if no_template:
            print(f"❌ FILES WITHOUT TEMPLATES ({len(no_template)}):")
            for result in sorted(no_template, key=lambda x: x.file_path):
                print(f"  ❌ {result.file_path}")
            print()
        
        # Summary
        print("=" * 80)
        print("SUMMARY:")
        print(f"  ✅ Fully Valid: {len(fully_valid)}")
        print(f"  ⚠️  Content Issues: {len(template_exists_content_invalid)}")
        print(f"  ❌ No Template: {len(no_template)}")
        print(f"  📊 Total Files: {len(results)}")
        
        if len(fully_valid) == len(results):
            print("\n🎉 All files are fully validated!")
        elif len(no_template) == 0:
            print(f"\n⚠️  All files have templates, but {len(template_exists_content_invalid)} have content issues.")
        else:
            print(f"\n❌ {len(no_template) + len(template_exists_content_invalid)} files need attention.")
        
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Validate deliverable files against available templates"
    )
    parser.add_argument(
        "--project-path",
        default=".",
        help="Path to the project base directory (default: current directory)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show warnings for files without templates"
    )
    
    args = parser.parse_args()
    
    # Resolve project path
    project_path = Path(args.project_path).resolve()
    
    # Check if we're in a valid project structure
    if not (project_path / "output").exists() or not (project_path / "templates").exists():
        # Try to find project root with output and templates folders
        current = Path.cwd()
        while current != current.parent:
            if (current / "output").exists() and (current / "templates").exists():
                project_path = current
                break
            current = current.parent
        else:
            print("ERROR: Could not find project structure with 'output' and 'templates' folders. Please run from project root or specify --project-path")
            sys.exit(1)
    
    validator = DeliverableValidator(project_path)
    
    if args.quiet:
        results = validator.validate_files()
        issues = [r for r in results if not r.template_exists or not r.content_valid]
        
        if issues:
            print("Files with validation issues:")
            for result in sorted(issues, key=lambda x: x.file_path):
                if not result.template_exists:
                    print(f"  ❌ {result.file_path} (no template)")
                else:
                    print(f"  ⚠️  {result.file_path} (content issues)")
                    for error in result.errors:
                        print(f"      • {error}")
        else:
            print("✅ All files are fully validated!")
    else:
        validator.print_validation_report()


if __name__ == "__main__":
    main()