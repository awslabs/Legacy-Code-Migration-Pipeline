"""
Content Type Classifier - Classifies content type for each section.

This module analyzes code content to determine the programming language
and program type, supporting mixed content detection in PDS-style files.
"""

import re
from typing import Tuple, Dict, List
from ..models.program_boundary import ProgramType


class ContentTypeClassifier:
    """Classifies content type for each section."""
    
    def __init__(self):
        """Initialize content type classifier."""
        # Define language detection patterns
        self.language_patterns = {
            'RPG': [
                r'^\s*[HhFfIiCcOoEe]\s',  # RPG specification types
                r'^\s*[HhFfIiCcOoEe][*]',  # RPG comments
                r'EVAL\s+',
                r'CHAIN\s+',
                r'READ\s+',
                r'WRITE\s+',
                r'UPDATE\s+',
                r'DELETE\s+',
                r'SETLL\s+',
                r'READE\s+',
                r'DCL-PR\s+',
                r'DCL-PROC\s+',
                r'END-PR\s*;',
                r'END-PROC\s*;'
            ],
            'JCL': [
                r'^//[A-Z0-9#@$]+\s+JOB\s+',  # Job statement
                r'^//[A-Z0-9#@$]+\s+EXEC\s+', # Exec statement
                r'^//[A-Z0-9#@$]+\s+DD\s+',   # DD statement
                r'^//\*',                      # JCL comment
                r'^\s*//\s*$',                 # JCL continuation
                r'DISP=',
                r'DSN=',
                r'UNIT=',
                r'VOL=SER=',
                r'SYSOUT=',
                r'CLASS=',
                r'MSGCLASS='
            ],
            'ASM': [
                r'^\s*[A-Z0-9#@$]+\s+CSECT\s*',  # Control section
                r'^\s*[A-Z0-9#@$]+\s+START\s+',  # Start directive
                r'^\s*ENTRY\s+',                  # Entry point
                r'^\s*TITLE\s+',                  # Title directive
                r'^\s*[A-Z0-9#@$]+\s+EQU\s+',    # Equate
                r'^\s*[A-Z0-9#@$]+\s+DC\s+',     # Define constant
                r'^\s*[A-Z0-9#@$]+\s+DS\s+',     # Define storage
                r'^\s*END\s*$',                   # End directive
                r'\s+LR\s+',                      # Load register
                r'\s+ST\s+',                      # Store
                r'\s+L\s+',                       # Load
                r'\s+BR\s+',                      # Branch register
                r'\s+BCR\s+',                     # Branch on condition register
                r'\s+BALR\s+',                    # Branch and link register
            ],
            'COBOL': [
                r'IDENTIFICATION\s+DIVISION',
                r'ENVIRONMENT\s+DIVISION',
                r'DATA\s+DIVISION',
                r'PROCEDURE\s+DIVISION',
                r'WORKING-STORAGE\s+SECTION',
                r'FILE\s+SECTION',
                r'LINKAGE\s+SECTION',
                r'PERFORM\s+',
                r'MOVE\s+',
                r'COMPUTE\s+',
                r'IF\s+.*\s+THEN',
                r'ELSE\s*$',
                r'END-IF',
                r'CALL\s+',
                r'COPY\s+'
            ],
            'PLI': [
                r'^\s*[A-Z0-9_]+:\s*PROC\s*',     # Procedure
                r'^\s*DCL\s+',                     # Declare
                r'^\s*DECLARE\s+',                # Declare (full form)
                r'PUT\s+SKIP',
                r'GET\s+LIST',
                r'PUT\s+LIST',
                r'IF\s+.*\s+THEN\s+DO',
                r'END\s*;',
                r'CALL\s+[A-Z0-9_]+\s*\(',
                r'%INCLUDE\s+'
            ],
            'NATURAL': [
                r'DEFINE\s+DATA\s+PROGRAM',
                r'DEFINE\s+DATA\s+SUBPROGRAM',
                r'DEFINE\s+DATA\s+PARAMETER',
                r'END-DEFINE',
                r'READ\s+[A-Z0-9_]+\s+BY\s+',
                r'FIND\s+[A-Z0-9_]+\s+WITH\s+',
                r'UPDATE\s*\(',
                r'STORE\s+[A-Z0-9_]+',
                r'DELETE\s+[A-Z0-9_]+',
                r'IF\s+.*\s+THEN',
                r'END-IF',
                r'FOR\s+.*\s+TO\s+',
                r'END-FOR'
            ],
            'REXX': [
                r'/\*\s*REXX\s*\*/',              # REXX comment header
                r'^\s*[A-Z0-9_]+:\s*PROCEDURE',   # Procedure definition
                r'SAY\s+',                        # Say statement
                r'PARSE\s+ARG\s+',               # Parse argument
                r'PARSE\s+VAR\s+',               # Parse variable
                r'IF\s+.*\s+THEN\s+DO',
                r'SELECT\s*$',
                r'WHEN\s+',
                r'OTHERWISE\s*$',
                r'END\s*$',
                r'CALL\s+[A-Z0-9_]+',
                r'RETURN\s+'
            ]
        }
        
        # Define program type patterns
        self.program_type_patterns = {
            ProgramType.JOB: [
                r'^//[A-Z0-9#@$]+\s+JOB\s+',
            ],
            ProgramType.MAIN: [
                r'^\s*[HhFfIiCcOoEe]\s',  # RPG main program specs
                r'IDENTIFICATION\s+DIVISION',  # COBOL main program
                r'DEFINE\s+DATA\s+PROGRAM',    # Natural main program
            ],
            ProgramType.SUBPROGRAM: [
                r'DEFINE\s+DATA\s+SUBPROGRAM', # Natural subprogram
                r'^\s*[A-Z0-9_]+:\s*PROC\s*', # PL/I procedure
                r'^\s*[A-Z0-9_]+:\s*PROCEDURE', # REXX procedure
            ],
            ProgramType.CSECT: [
                r'^\s*[A-Z0-9#@$]+\s+CSECT\s*',
            ],
            ProgramType.ENTRY_POINT: [
                r'^\s*ENTRY\s+',
            ]
        }
    
    def classify_section(self, section_content: str) -> Tuple[str, ProgramType]:
        """
        Classify section content.
        
        Args:
            section_content: Content of the section to classify
            
        Returns:
            (language, program_type) tuple
            Examples: ('RPG', ProgramType.MAIN), ('JCL', ProgramType.JOB), ('DATA', ProgramType.DATA)
        """
        if not section_content or not section_content.strip():
            return 'UNKNOWN', ProgramType.UNKNOWN
        
        # Detect language
        language = self._detect_language(section_content)
        
        # Detect program type
        program_type = self._detect_program_type(section_content, language)
        
        return language, program_type
    
    def _detect_language(self, content: str) -> str:
        """
        Detect the programming language of the content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected language string
        """
        content_upper = content.upper()
        lines = content_upper.splitlines()
        
        # Score each language based on pattern matches
        language_scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                compiled_pattern = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
                matches = compiled_pattern.findall(content_upper)
                score += len(matches)
            
            if score > 0:
                language_scores[language] = score
        
        # Special case: Check for data-only content
        if self._is_data_content(content):
            return 'DATA'
        
        # Return language with highest score
        if language_scores:
            return max(language_scores.keys(), key=lambda k: language_scores[k])
        
        # Fallback: Try to detect based on content characteristics
        return self._detect_language_fallback(content)
    
    def _detect_program_type(self, content: str, language: str) -> ProgramType:
        """
        Detect the program type based on content and language.
        
        Args:
            content: Content to analyze
            language: Detected language
            
        Returns:
            Detected program type
        """
        content_upper = content.upper()
        
        # Check specific program type patterns
        for prog_type, patterns in self.program_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_upper, re.MULTILINE | re.IGNORECASE):
                    return prog_type
        
        # Language-specific defaults
        if language == 'JCL':
            return ProgramType.JOB
        elif language == 'DATA':
            return ProgramType.DATA
        elif language == 'ASM':
            # Check for CSECT or START
            if re.search(r'^\s*[A-Z0-9#@$]+\s+CSECT\s*', content_upper, re.MULTILINE):
                return ProgramType.CSECT
            elif re.search(r'^\s*[A-Z0-9#@$]+\s+START\s+', content_upper, re.MULTILINE):
                return ProgramType.MAIN
            else:
                return ProgramType.ROUTINE
        else:
            return ProgramType.MAIN
    
    def _is_data_content(self, content: str) -> bool:
        """
        Check if content appears to be data rather than code.
        
        Args:
            content: Content to check
            
        Returns:
            True if content appears to be data
        """
        lines = content.strip().splitlines()
        if not lines:
            return False
        
        # Check for data patterns
        data_indicators = 0
        total_lines = len(lines)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for common data patterns
            if (
                # Numeric data with spaces (fixed-width records)
                re.match(r'^[0-9\s]+[A-Z\s]*[0-9\s]*$', line) or
                # Name-like data with addresses
                re.match(r'^[A-Z\s,]+\s+[0-9\s]+[A-Z\s,]*$', line) or
                # Mixed alphanumeric data records
                re.match(r'^[A-Z0-9\s]{20,}$', line) or
                # Date-like patterns
                re.search(r'[0-9]{6,8}', line) or
                # Address-like patterns
                re.search(r'[A-Z]{2}\s+[0-9]{5}', line)
            ):
                data_indicators += 1
        
        # If more than 70% of lines look like data, classify as data
        return data_indicators > (total_lines * 0.7)
    
    def _detect_language_fallback(self, content: str) -> str:
        """
        Fallback language detection based on content characteristics.
        
        Args:
            content: Content to analyze
            
        Returns:
            Best guess language
        """
        content_upper = content.upper()
        
        # Check for assembly-like characteristics
        if (re.search(r'^\s*[A-Z0-9#@$]+\s+[A-Z]{2,5}\s+', content_upper, re.MULTILINE) or
            re.search(r'\s+EQU\s+', content_upper) or
            re.search(r'TITLE\s+', content_upper)):
            return 'ASM'
        
        # Check for JCL-like characteristics
        if (content.startswith('//') or
            re.search(r'//[A-Z0-9#@$]+', content_upper)):
            return 'JCL'
        
        # Check for RPG-like characteristics (fixed format)
        lines = content.splitlines()
        rpg_like_lines = 0
        for line in lines[:10]:  # Check first 10 lines
            if len(line) > 6 and line[5:6] in 'HFICOEhficoe':
                rpg_like_lines += 1
        
        if rpg_like_lines > 2:
            return 'RPG'
        
        # Default to unknown
        return 'UNKNOWN'
    
    def get_confidence_score(self, content: str, language: str) -> float:
        """
        Get confidence score for language classification.
        
        Args:
            content: Content that was classified
            language: Detected language
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if language == 'UNKNOWN':
            return 0.0
        
        if language not in self.language_patterns:
            return 0.5  # Medium confidence for fallback detection
        
        patterns = self.language_patterns[language]
        content_upper = content.upper()
        
        matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if re.search(pattern, content_upper, re.MULTILINE | re.IGNORECASE):
                matches += 1
        
        # Calculate confidence based on pattern matches
        confidence = matches / total_patterns if total_patterns > 0 else 0.0
        
        # Boost confidence for strong indicators
        if language == 'JCL' and content.startswith('//'):
            confidence = min(1.0, confidence + 0.3)
        elif language == 'ASM' and 'TITLE' in content_upper:
            confidence = min(1.0, confidence + 0.2)
        elif language == 'RPG' and re.search(r'^\s*[HhFfIiCcOoEe]\s', content, re.MULTILINE):
            confidence = min(1.0, confidence + 0.3)
        
        return min(1.0, confidence)