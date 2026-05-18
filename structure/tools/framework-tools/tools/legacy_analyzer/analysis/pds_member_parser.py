"""
PDS Member Parser - Parses PDS-style member sections (./ ADD NAME=...).

This module handles the parsing of Partitioned Data Set (PDS) format files
commonly used in mainframe environments to store multiple programs/sections
in a single file.
"""

import re
from typing import List, Optional, NamedTuple
from dataclasses import dataclass


@dataclass
class PDSSection:
    """Represents a single PDS member section."""
    name: str
    start_line: int
    end_line: int
    content: str
    stats: Optional[str] = None  # The statistics part of the ADD NAME line


class PDSMemberParser:
    """Parses PDS-style member sections (./ ADD NAME=...)."""
    
    # Pattern to match PDS member headers
    # Format: ./ ADD NAME=membername   stats-info
    PDS_HEADER_PATTERN = re.compile(
        r'^\.\/ ADD NAME=([A-Z0-9$#@_]+)\s*(.*)$',
        re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize PDS member parser."""
        pass
    
    def is_pds_format(self, content: str) -> bool:
        """
        Check if content is in PDS format.
        
        Args:
            content: File content to check
            
        Returns:
            True if content contains PDS member markers, False otherwise
        """
        lines = content.splitlines()
        
        # Look for at least one PDS header in the first 50 lines
        for line in lines[:50]:
            if self.PDS_HEADER_PATTERN.match(line.strip()):
                return True
        
        return False
    
    def parse_sections(self, content: str) -> List[PDSSection]:
        """
        Parse PDS member sections from content.
        
        Args:
            content: File content containing PDS members
            
        Returns:
            List of PDSSection objects representing each member
        """
        lines = content.splitlines()
        sections = []
        current_section = None
        
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Check for PDS header
            match = self.PDS_HEADER_PATTERN.match(stripped_line)
            if match:
                # End previous section if exists
                if current_section:
                    current_section.end_line = i - 1
                    current_section.content = self._extract_section_content(
                        lines, current_section.start_line, current_section.end_line
                    )
                    sections.append(current_section)
                
                # Start new section
                member_name = match.group(1)
                stats = match.group(2).strip() if match.group(2) else None
                
                current_section = PDSSection(
                    name=member_name,
                    start_line=i + 1,  # Content starts after the header
                    end_line=len(lines),  # Will be updated when next section found
                    content="",  # Will be filled when section ends
                    stats=stats
                )
        
        # Handle the last section
        if current_section:
            current_section.end_line = len(lines)
            current_section.content = self._extract_section_content(
                lines, current_section.start_line, current_section.end_line
            )
            sections.append(current_section)
        
        return sections
    
    def _extract_section_content(self, lines: List[str], start_line: int, end_line: int) -> str:
        """
        Extract content for a section.
        
        Args:
            lines: All lines from the file
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based)
            
        Returns:
            Section content as string
        """
        # Convert to 0-based indexing
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        if start_idx >= end_idx:
            return ""
        
        section_lines = lines[start_idx:end_idx]
        return '\n'.join(section_lines)
    
    def get_section_by_name(self, sections: List[PDSSection], name: str) -> Optional[PDSSection]:
        """
        Get a specific section by name.
        
        Args:
            sections: List of parsed sections
            name: Name of the section to find
            
        Returns:
            PDSSection if found, None otherwise
        """
        for section in sections:
            if section.name.upper() == name.upper():
                return section
        return None
    
    def get_sections_by_pattern(self, sections: List[PDSSection], pattern: str) -> List[PDSSection]:
        """
        Get sections matching a name pattern.
        
        Args:
            sections: List of parsed sections
            pattern: Regular expression pattern to match names
            
        Returns:
            List of matching PDSSection objects
        """
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        matching_sections = []
        
        for section in sections:
            if compiled_pattern.match(section.name):
                matching_sections.append(section)
        
        return matching_sections
    
    def validate_sections(self, sections: List[PDSSection]) -> List[str]:
        """
        Validate parsed sections for common issues.
        
        Args:
            sections: List of parsed sections to validate
            
        Returns:
            List of validation error messages (empty if no errors)
        """
        errors = []
        
        if not sections:
            return ["No PDS sections found"]
        
        # Check for duplicate names
        names = [section.name for section in sections]
        duplicates = set([name for name in names if names.count(name) > 1])
        if duplicates:
            errors.append(f"Duplicate section names found: {', '.join(duplicates)}")
        
        # Check for invalid boundaries
        for section in sections:
            if section.start_line < 1:
                errors.append(f"Section '{section.name}' has invalid start_line: {section.start_line}")
            if section.end_line < section.start_line:
                errors.append(f"Section '{section.name}' has end_line before start_line")
            if not section.content.strip():
                errors.append(f"Section '{section.name}' has empty content")
        
        # Check for overlapping sections
        for i, section1 in enumerate(sections):
            for j, section2 in enumerate(sections[i+1:], i+1):
                if (section1.start_line <= section2.start_line <= section1.end_line or
                    section2.start_line <= section1.start_line <= section2.end_line):
                    errors.append(
                        f"Sections '{section1.name}' and '{section2.name}' overlap: "
                        f"{section1.start_line}-{section1.end_line} vs {section2.start_line}-{section2.end_line}"
                    )
        
        return errors
    
    def get_statistics(self, sections: List[PDSSection]) -> dict:
        """
        Get statistics about the parsed sections.
        
        Args:
            sections: List of parsed sections
            
        Returns:
            Dictionary with statistics
        """
        if not sections:
            return {}
        
        total_sections = len(sections)
        total_lines = sum(section.end_line - section.start_line + 1 for section in sections)
        
        # Analyze section name patterns
        name_patterns = {
            'index_sections': len([s for s in sections if s.name.startswith('$') or 'INDEX' in s.name.upper()]),
            'jcl_sections': len([s for s in sections if s.name.endswith('$')]),
            'data_sections': len([s for s in sections if s.name.endswith('D') or 'DATA' in s.name.upper()]),
            'assembly_sections': len([s for s in sections if s.name.endswith('A') or 'ASM' in s.name.upper()]),
            'program_sections': 0  # Will be calculated
        }
        
        # Calculate program sections (everything else)
        name_patterns['program_sections'] = (total_sections - 
                                           name_patterns['index_sections'] - 
                                           name_patterns['jcl_sections'] - 
                                           name_patterns['data_sections'] - 
                                           name_patterns['assembly_sections'])
        
        return {
            'total_sections': total_sections,
            'total_lines': total_lines,
            'average_section_size': total_lines / total_sections if total_sections > 0 else 0,
            'name_patterns': name_patterns,
            'section_names': [section.name for section in sections]
        }