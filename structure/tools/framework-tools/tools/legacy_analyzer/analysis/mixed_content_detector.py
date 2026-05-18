"""
Mixed Content Detector - Detects program boundaries across multiple languages in a single file.

This module handles files that contain multiple programs/sections of different types,
such as PDS (Partitioned Data Set) members commonly found in mainframe environments.
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from ..models.program_boundary import ProgramBoundary, ProgramType
from .content_type_classifier import ContentTypeClassifier
from .pds_member_parser import PDSMemberParser


class MixedContentDetector:
    """Detects program boundaries across multiple languages in a single file."""
    
    def __init__(self):
        """Initialize mixed content detector."""
        self.pds_parser = PDSMemberParser()
        self.classifier = ContentTypeClassifier()
    
    def detect_boundaries(self, file_path: str, content: str) -> List[ProgramBoundary]:
        """
        Detect all program boundaries regardless of language.
        
        Args:
            file_path: Path to the source file
            content: File content to analyze
            
        Returns:
            List of ProgramBoundary objects with mixed languages/types
        """
        # Check if this is a PDS-style file
        if self.pds_parser.is_pds_format(content):
            return self._detect_pds_boundaries(file_path, content)
        
        # For non-PDS files, return empty list (fall back to language-specific detectors)
        return []
    
    def _detect_pds_boundaries(self, file_path: str, content: str) -> List[ProgramBoundary]:
        """
        Detect program boundaries in PDS-format files.
        
        Args:
            file_path: Path to the source file
            content: File content to analyze
            
        Returns:
            List of ProgramBoundary objects for each PDS member
        """
        # Parse PDS sections
        sections = self.pds_parser.parse_sections(content)
        
        if not sections:
            return []
        
        boundaries = []
        
        for section in sections:
            # Classify the content type
            language, program_type = self.classifier.classify_section(section.content)
            
            # Create program boundary
            boundary = ProgramBoundary(
                program_name=section.name,
                start_line=section.start_line,
                end_line=section.end_line,
                program_type=program_type,
                language=language,
                entry_points=[section.name],
                file_path=file_path,
                metadata={
                    'pds_member': True,
                    'pds_stats': section.stats,
                    'section_type': self._determine_section_type(section.name)
                }
            )
            
            boundaries.append(boundary)
        
        return boundaries
    
    def _determine_section_type(self, section_name: str) -> str:
        """
        Determine the type of PDS section based on naming conventions.
        
        Args:
            section_name: Name of the PDS section
            
        Returns:
            Section type string
        """
        name_upper = section_name.upper()
        
        # Index/directory sections
        if name_upper.startswith('$') or 'INDEX' in name_upper:
            return 'INDEX'
        
        # JCL sections (typically end with $)
        if name_upper.endswith('$'):
            return 'JCL'
        
        # Data sections (typically end with D or contain DATA)
        if (name_upper.endswith('D') or 
            name_upper.endswith('D1') or 
            name_upper.endswith('D2') or 
            name_upper.endswith('D3') or
            'DATA' in name_upper):
            return 'DATA'
        
        # Assembly sections (typically end with A or contain ASM)
        if (name_upper.endswith('A') or 
            'ASM' in name_upper or 
            'ASSEMBLER' in name_upper):
            return 'ASSEMBLY'
        
        # Default to program
        return 'PROGRAM'
    
    def is_mixed_content_file(self, content: str) -> bool:
        """
        Check if a file contains mixed content that should be handled by this detector.
        
        Args:
            content: File content to check
            
        Returns:
            True if file contains mixed content, False otherwise
        """
        return self.pds_parser.is_pds_format(content)
    
    def get_content_summary(self, boundaries: List[ProgramBoundary]) -> Dict[str, any]:
        """
        Get a summary of the mixed content detected.
        
        Args:
            boundaries: List of detected program boundaries
            
        Returns:
            Dictionary with content summary statistics
        """
        if not boundaries:
            return {}
        
        # Count by language
        language_counts = {}
        type_counts = {}
        
        for boundary in boundaries:
            lang = boundary.language
            ptype = boundary.program_type.value if hasattr(boundary.program_type, 'value') else str(boundary.program_type)
            
            language_counts[lang] = language_counts.get(lang, 0) + 1
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        # Determine dominance
        total_programs = len(boundaries)
        dominant_language = None
        dominant_type = None
        
        if language_counts:
            max_lang_count = max(language_counts.values())
            # Only consider dominant if > 50%
            if max_lang_count > total_programs * 0.5:
                dominant_language = max(language_counts.keys(), key=lambda k: language_counts[k])
        
        if type_counts:
            max_type_count = max(type_counts.values())
            # Only consider dominant if > 50%
            if max_type_count > total_programs * 0.5:
                dominant_type = max(type_counts.keys(), key=lambda k: type_counts[k])
        
        # Determine overall language
        if len(language_counts) == 1:
            overall_language = list(language_counts.keys())[0]
        else:
            overall_language = 'MIXED'
        
        return {
            'total_programs': total_programs,
            'language_counts': language_counts,
            'type_counts': type_counts,
            'overall_language': overall_language,
            'dominant_language': dominant_language,
            'dominant_type': dominant_type,
            'is_mixed': len(language_counts) > 1
        }