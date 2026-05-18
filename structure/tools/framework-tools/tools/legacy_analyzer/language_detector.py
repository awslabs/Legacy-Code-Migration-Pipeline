"""
Language detection module with content-based analysis.

This module provides intelligent language detection that combines:
1. Extension-based guessing
2. Content analysis for language-specific syntax patterns
3. Fallback logic when extension doesn't match content
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects programming language using extension and content analysis."""
    
    # Language-specific syntax patterns for content analysis
    LANGUAGE_PATTERNS = {
        'COBOL': [
            # COBOL programs always have these divisions
            # Account for mainframe format with sequence numbers (columns 1-6)
            (r'^\s*(\d{6})?\s*IDENTIFICATION\s+DIVISION', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\s*(\d{6})?\s*PROCEDURE\s+DIVISION', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\s*(\d{6})?\s*PROGRAM-ID[\.\s]', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\s*(\d{6})?\s*DATA\s+DIVISION', re.MULTILINE | re.IGNORECASE, 'medium'),
            (r'^\s*(\d{6})?\s*ENVIRONMENT\s+DIVISION', re.MULTILINE | re.IGNORECASE, 'medium'),
            (r'^\s*(\d{6})?\s*WORKING-STORAGE\s+SECTION', re.MULTILINE | re.IGNORECASE, 'medium'),
            # COBOL copybooks often have data structures
            (r'^\s*(\d{6})?\s*\d{2}\s+[A-Z0-9\-]+', re.MULTILINE, 'low'),  # Level numbers
            # COBOL statements end with period
            (r'^\d{6}?\s*[A-Z\-]+\s+.*\.$', re.MULTILINE, 'low'),
            # Common COBOL keywords - made more specific to avoid false positives in documentation
            (r'\b(MOVE\s+|PERFORM\s+|DISPLAY\s+|ACCEPT\s+|EVALUATE\s+|EXEC\s+SQL|EXEC\s+CICS)\b', re.IGNORECASE, 'medium'),
            (r'\b(IF\s+.*\s+THEN|END-IF)\b', re.IGNORECASE, 'medium'),  # More specific IF patterns
            (r'\bPIC\s+[X9SV\(]+', re.IGNORECASE, 'medium'),  # PICTURE clause
            (r'\b(COMP|COMP-3|BINARY|PACKED-DECIMAL)\b', re.IGNORECASE, 'medium'),  # COBOL data types
        ],
        'REXX': [
            # REXX-specific patterns - made more context-aware to avoid false positives
            (r'^/\*.*\*/$', re.MULTILINE, 'medium'),  # REXX comments
            (r'^\s*ARG\s+', re.MULTILINE | re.IGNORECASE, 'high'),  # ARG statement
            (r'^\s*PARSE\s+(ARG|VAR|VALUE|SOURCE)', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\s*SAY\s+', re.MULTILINE | re.IGNORECASE, 'medium'),
            (r'^\s*INTERPRET\s+', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\s*NUMERIC\s+DIGITS', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\s*SIGNAL\s+(ON|OFF)', re.MULTILINE | re.IGNORECASE, 'medium'),
            # More specific patterns to avoid documentation false positives
            (r'^\s*CALL\s+[A-Z0-9_]+', re.MULTILINE | re.IGNORECASE, 'medium'),  # Actual CALL statement
            (r'^\s*EXIT\s*$', re.MULTILINE | re.IGNORECASE, 'medium'),           # Actual EXIT statement
            (r'^\s*RETURN\s*$', re.MULTILINE | re.IGNORECASE, 'medium'),         # Actual RETURN statement
            # REXX label pattern (label followed by colon)
            (r'^[A-Z][A-Z0-9_]*:\s*$', re.MULTILINE, 'medium'),
        ],
        'PLI': [
            # PL/I specific patterns - made more specific to avoid false positives
            (r'^\s*[A-Z0-9_]+\s*:\s*PROC(?:EDURE)?', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'\bDCL\s+[A-Z0-9_]+', re.IGNORECASE, 'medium'),  # DECLARE with variable name
            (r'\b(PUT|GET)\s+(SKIP|DATA|LIST|EDIT)', re.IGNORECASE, 'high'),
            (r'\bEXEC\s+CICS\b', re.IGNORECASE, 'medium'),
            (r'\b(FIXED|FLOAT|BIT|CHAR|VARYING)\s+(BINARY|DECIMAL)', re.IGNORECASE, 'medium'),  # More specific data types
        ],
        'JCL': [
            # JCL specific patterns
            (r'^//[A-Z0-9#@$]+\s+JOB\s+', re.MULTILINE, 'high'),
            (r'^//[A-Z0-9#@$]+\s+EXEC\s+', re.MULTILINE, 'high'),
            (r'^//[A-Z0-9#@$]+\s+DD\s+', re.MULTILINE, 'high'),
            (r'^//\*', re.MULTILINE, 'medium'),  # JCL comment
            (r'^\s*PROC\s+', re.MULTILINE | re.IGNORECASE, 'medium'),
        ],
        'NATURAL': [
            # Natural specific patterns (must be very specific to avoid false positives)
            (r'^\d{6}?\s*DEFINE\s+DATA', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\d{6}?\s*END-DEFINE', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\d{6}?\s*CALLNAT\s+', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'^\d{6}?\s*FETCH\s+RETURN', re.MULTILINE | re.IGNORECASE, 'high'),  # More specific
            (r'\b(END-FOR|END-REPEAT|END-NOREC)\b', re.IGNORECASE, 'medium'),  # Removed END-IF (also in COBOL)
            (r'\b(COMPRESS|EXAMINE|MOVE\s+LEFT|RESET)\b', re.IGNORECASE, 'low'),  # Natural-specific
        ],
        'RPG': [
            # RPG specific patterns - very specific to avoid false positives in documentation
            (r'^\s*[HFDICOP]\s+[A-Z0-9]', re.MULTILINE, 'high'),  # RPG spec types with typical RPG identifiers
            (r'^\s*DCL-', re.MULTILINE | re.IGNORECASE, 'high'),  # Free-form RPG
            (r'\b(BEGSR|ENDSR|EXSR)\b', re.IGNORECASE, 'high'),
            (r'\b(CHAIN|SETLL|READE)\b', re.IGNORECASE, 'medium'),
        ],
        'ASM': [
            # Assembler specific patterns - made more specific to avoid false positives
            (r'^\s*[A-Z0-9]+\s+CSECT', re.MULTILINE, 'high'),
            (r'^\s*ENTRY\s+', re.MULTILINE | re.IGNORECASE, 'high'),
            (r'\b(BALR|BCR|MVC|CLI)\b', 0, 'medium'),  # Removed single letters LA, LR, ST, L
            (r'^\s*DC\s+[ACFHPXZ]', re.MULTILINE | re.IGNORECASE, 'medium'),  # Define constant with type
            (r'^\s*DS\s+[0-9]', re.MULTILINE | re.IGNORECASE, 'medium'),  # Define storage with length
        ],
    }
    
    # Confidence weights for pattern matching
    CONFIDENCE_WEIGHTS = {
        'high': 10,
        'medium': 5,
        'low': 2
    }
    
    # Documentation detection patterns - these indicate the content is documentation, not code
    DOCUMENTATION_PATTERNS = [
        (r'\btutorial\b', re.IGNORECASE, 'high'),
        (r'\bspecification\b.*\bused to\b', re.IGNORECASE, 'high'),
        (r'\bcolumn\b.*\bfield name\b', re.IGNORECASE, 'high'),
        (r'\benter\b.*\bif\b.*\bblank\b', re.IGNORECASE, 'medium'),
        (r'\boperation\b.*\bperformed\b', re.IGNORECASE, 'medium'),
        (r'\bexample\b.*\bprogram\b', re.IGNORECASE, 'medium'),
        (r'\bdescription\b.*\bsummary\b', re.IGNORECASE, 'medium'),
        (r'\bmust be\b.*\brequired\b', re.IGNORECASE, 'medium'),
        (r'\bpage was\b.*\bwritten\b', re.IGNORECASE, 'medium'),
        # Patterns specific to programming tutorials/documentation
        (r'calling\s+\w+\s+from\s+\w+', re.IGNORECASE, 'medium'),
        (r'external\s+subroutines', re.IGNORECASE, 'medium'),
        (r'calculation\s+specifications', re.IGNORECASE, 'medium'),
        # Column specification patterns (common in mainframe documentation)
        (r'^\s*\d+\s*-\s*\d+\s+[A-Za-z\s]+\s+[a-z]', re.MULTILINE, 'high'),  # "7 - 8   Control Level   enter a..."
        (r'^\s*-+\s+-+\s+-+', re.MULTILINE, 'medium'),  # Separator lines like "-----   -----   ---"
        (r'\bcolumn\(s\)\b', re.IGNORECASE, 'medium'),  # "Column(s)" header
        (r'\badvanced\s+statement\s+types\b', re.IGNORECASE, 'medium'),  # Tutorial section titles
        (r'\bextension\s+and\s+line\s+counter\b', re.IGNORECASE, 'medium'),  # Specific tutorial content
    ]
    
    # Extension to language mapping
    EXTENSION_MAP = {
        '.cbl': 'COBOL',
        '.cob': 'COBOL',
        '.cobol': 'COBOL',
        '.cpy': 'COBOL',
        '.copy': 'COBOL',
        '.pli': 'PLI',
        '.pl1': 'PLI',
        '.inc': 'PLI',
        '.jcl': 'JCL',
        '.rexx': 'REXX',
        '.rex': 'REXX',
        '.nsp': 'NATURAL',
        '.nsn': 'NATURAL',
        '.nsc': 'NATURAL',
        '.nsl': 'NATURAL',
        '.nsg': 'NATURAL',
        '.nsd': 'NATURAL',
        '.nsa': 'NATURAL',
        '.ns8': 'NATURAL',
        '.rpg': 'RPG',
        '.rpgle': 'RPG',
        '.sqlrpgle': 'RPG',
        '.rpg38': 'RPG',
        '.mbr': 'RPG',
        '.asm': 'ASM',
        '.s': 'ASM',
        '.mac': 'ASM',
    }
    
    # Ambiguous extensions that need content analysis
    AMBIGUOUS_EXTENSIONS = {'.txt', '.dat', '.src', '.mbr'}
    
    def __init__(self, max_lines_to_scan: int = 200):
        """
        Initialize language detector.
        
        Args:
            max_lines_to_scan: Maximum number of lines to scan for patterns
        """
        self.max_lines_to_scan = max_lines_to_scan
    
    def detect_language(self, file_path: str, content: Optional[str] = None) -> Optional[str]:
        """
        Detect programming language using a priority-based detection algorithm.
        
        This method implements a two-stage detection process that prioritizes
        extension-based detection over content-based analysis to ensure reliable
        and efficient language identification.
        
        Detection Algorithm:
        1. Extension-Based Detection (Primary):
           - Checks file extension against EXTENSION_MAP
           - Returns immediately if extension is definitive (not ambiguous)
           - Skips content analysis for known extensions
        
        2. Content-Based Detection (Fallback):
           - Used only when extension is unknown or ambiguous
           - Analyzes file content for language-specific patterns
           - Returns language with highest confidence score
        
        This priority-based approach ensures that files with reliable extensions
        (e.g., .nsp for Natural, .cbl for COBOL) are correctly identified without
        being influenced by potentially misleading content patterns.
        
        Args:
            file_path: Path to the source file to analyze
            content: Optional pre-loaded file content. If not provided, the file
                    will be read automatically (up to 50KB)
            
        Returns:
            Detected language name in uppercase (e.g., 'NATURAL', 'COBOL', 'JCL')
            or None if language cannot be determined
            
        Examples:
            >>> detector = LanguageDetector()
            
            # Natural file with definitive extension
            >>> detector.detect_language('PROGRAM.nsp')
            'NATURAL'
            
            # COBOL file with definitive extension
            >>> detector.detect_language('PAYROLL.cbl')
            'COBOL'
            
            # File with ambiguous extension - uses content analysis
            >>> detector.detect_language('script.txt')
            'REXX'  # or None if no patterns match
            
            # Provide content directly to avoid file I/O
            >>> content = "DEFINE DATA\\nEND-DEFINE"
            >>> detector.detect_language('unknown.dat', content=content)
            'NATURAL'
        
        Note:
            - Extension detection is case-insensitive
            - Content analysis is limited to first 200 lines for performance
            - Binary files or encoding errors are handled gracefully
        """
        # Step 1: Try extension-based detection first
        language = self._detect_by_extension(file_path)
        
        # Step 2: If extension provides definitive answer, return immediately
        if language is not None:
            logger.debug(f"Detected {language} for {file_path} using extension method")
            return language
        
        # Step 3: Fall back to content-based detection
        if content is None:
            content = self._read_file_content(file_path)
        
        if not content:
            logger.debug(f"No content available for {file_path}, cannot detect language")
            return None
        
        # Step 4: Use content analysis
        detected_language = self._detect_by_content(content)
        if detected_language:
            logger.debug(f"Detected {detected_language} for {file_path} using content method")
        else:
            logger.debug(f"Could not detect language for {file_path} using content method")
        
        return detected_language
    
    def _detect_by_extension(self, file_path: str) -> Optional[str]:
        """
        Detect language purely from file extension without content analysis.
        
        This method provides fast, reliable language detection for files with
        known extensions. It distinguishes between three categories of extensions:
        
        1. Definitive Extensions: Extensions that reliably indicate a specific
           language (e.g., .nsp → Natural, .cbl → COBOL, .jcl → JCL)
           
        2. Ambiguous Extensions: Extensions that could represent multiple languages
           (e.g., .txt, .dat, .src, .mbr) - returns None to trigger content analysis
           
        3. Unknown Extensions: Extensions not in EXTENSION_MAP - returns None
        
        This method is the first stage of the detection algorithm and ensures that
        files with reliable extensions are correctly identified without being
        influenced by potentially misleading content patterns.
        
        Args:
            file_path: Path to the source file (only extension is examined)
            
        Returns:
            Language name in uppercase (e.g., 'NATURAL', 'COBOL') if extension
            is definitive, or None if extension is ambiguous or unknown
            
        Examples:
            >>> detector = LanguageDetector()
            
            # Definitive Natural extension
            >>> detector._detect_by_extension('PROGRAM.nsp')
            'NATURAL'
            
            # Definitive COBOL extension
            >>> detector._detect_by_extension('PAYROLL.cbl')
            'COBOL'
            
            # Ambiguous extension - requires content analysis
            >>> detector._detect_by_extension('script.txt')
            None
            
            # Unknown extension
            >>> detector._detect_by_extension('file.xyz')
            None
            
            # Case-insensitive matching
            >>> detector._detect_by_extension('PROGRAM.NSP')
            'NATURAL'
        
        Note:
            - Extension matching is case-insensitive
            - Only the file extension is examined; file content is not read
            - This method never triggers content-based analysis
        """
        ext = Path(file_path).suffix.lower()
        
        # Check if extension is ambiguous
        if ext in self.AMBIGUOUS_EXTENSIONS:
            return None
        
        # Return mapped language for definitive extensions
        return self.EXTENSION_MAP.get(ext)
    
    def _guess_from_extension(self, file_path: str) -> Optional[str]:
        """
        Guess language from file extension.
        
        DEPRECATED: Use _detect_by_extension() instead.
        Kept for backward compatibility.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Guessed language or None
        """
        ext = Path(file_path).suffix.lower()
        return self.EXTENSION_MAP.get(ext)
    
    def _read_file_content(self, file_path: str, max_bytes: int = 50000) -> Optional[str]:
        """
        Read file content safely.
        
        Args:
            file_path: Path to the file
            max_bytes: Maximum bytes to read (to avoid huge files)
            
        Returns:
            File content or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_bytes)
            return content
        except Exception:
            return None
    
    def _detect_by_content(self, content: str) -> Optional[str]:
        """
        Detect language by analyzing file content for language-specific patterns.
        
        This method serves as the fallback detection mechanism when extension-based
        detection cannot provide a definitive answer. It analyzes the file content
        for language-specific syntax patterns, keywords, and structural elements.
        
        The detection process:
        1. First checks if content appears to be documentation rather than code
        2. Checks for mixed-content PDS format (ADD NAME= directives)
        3. If mixed content detected, analyzes individual sections by type
        4. Otherwise, scans content for patterns defined in LANGUAGE_PATTERNS
        5. Assigns confidence scores and returns language with highest score
        6. Applies minimum confidence threshold to avoid false positives on documentation
        
        Pattern matching includes:
        - COBOL: IDENTIFICATION DIVISION, PROCEDURE DIVISION, PROGRAM-ID, PIC clauses
        - Natural: DEFINE DATA, END-DEFINE, CALLNAT, FETCH RETURN
        - REXX: ARG, PARSE, SAY, INTERPRET statements
        - JCL: Job control statements (//name JOB, //name EXEC, //name DD)
        - PLI: PROC declarations, DCL statements, PUT/GET operations
        - RPG: Specification types, DCL- declarations, BEGSR/ENDSR
        - ASM: CSECT, ENTRY, assembler opcodes (BALR, MVC, etc.)
        
        Args:
            content: Source file content to analyze (typically first 200 lines)
            
        Returns:
            Language name in uppercase (e.g., 'NATURAL', 'COBOL') with highest
            confidence score, or None if no patterns match or confidence too low
            
        Examples:
            >>> detector = LanguageDetector()
            
            # Natural program content
            >>> natural_code = '''
            ... DEFINE DATA
            ... LOCAL
            ... 1 #VAR (A10)
            ... END-DEFINE
            ... '''
            >>> detector._detect_by_content(natural_code)
            'NATURAL'
            
            # Mixed PDS content with RPG programs
            >>> mixed_pds = '''
            ... ./ ADD NAME=EX1
            ... H
            ... FINCARDS IPE F  80  80
            ... ./ ADD NAME=EX1$
            ... //EXAMPLE1 JOB
            ... '''
            >>> detector._detect_by_content(mixed_pds)
            'RPG'  # Dominant language based on program analysis
        
        Note:
            - Only the first max_lines_to_scan lines are analyzed (default: 200)
            - Pattern matching uses regular expressions with various flags
            - Mainframe format with sequence numbers (columns 1-6) is supported
            - Mixed PDS content gets special handling to identify dominant language
            - Minimum confidence threshold prevents false positives on documentation
        """
        # First, check if this appears to be documentation rather than code
        if self._is_documentation_content(content):
            logger.debug("Content appears to be documentation, not code")
            return None
        
        # Check for mixed-content PDS format first
        if self._is_mixed_content_pds(content):
            return self._detect_dominant_language_in_pds(content)
        
        # Standard content analysis
        scores = self._analyze_content(content)
        
        if not scores:
            return None
        
        # Get the highest scoring language
        best_language = max(scores, key=scores.get)
        best_score = scores[best_language]
        
        # Apply minimum confidence threshold to prevent false positives on documentation
        # Require at least 8 points (just under 1 high-confidence pattern, allows strong medium patterns)
        MIN_CONFIDENCE_THRESHOLD = 8
        
        if best_score < MIN_CONFIDENCE_THRESHOLD:
            return None
        
        return best_language
    
    def _analyze_content(self, content: str) -> Dict[str, int]:
        """
        Analyze content for language-specific patterns.
        
        Args:
            content: File content to analyze
            
        Returns:
            Dictionary mapping language to confidence score
        """
        # Limit content to first N lines for performance
        lines = content.split('\n')[:self.max_lines_to_scan]
        sample_content = '\n'.join(lines)
        
        scores = {}
        
        for language, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern, flags, confidence in patterns:
                if re.search(pattern, sample_content, flags):
                    score += self.CONFIDENCE_WEIGHTS[confidence]
            
            if score > 0:
                scores[language] = score
        
        return scores
    
    def _is_documentation_content(self, content: str) -> bool:
        """
        Check if content appears to be documentation rather than actual code.
        
        This method helps prevent false positives when analyzing documentation
        files that contain programming-related terms but are not actual code.
        
        Args:
            content: Content to analyze
            
        Returns:
            True if content appears to be documentation, False if it might be code
        """
        lines = content.splitlines()
        
        # Count documentation indicators vs code indicators
        doc_score = 0
        code_score = 0
        total_non_empty_lines = 0
        
        for line in lines:
            if not line.strip():
                continue
                
            total_non_empty_lines += 1
            line_lower = line.lower()
            
            # Check for documentation patterns
            for pattern, flags, confidence in self.DOCUMENTATION_PATTERNS:
                if re.search(pattern, line, flags):
                    doc_score += self.CONFIDENCE_WEIGHTS[confidence]
                    break  # Only count one pattern per line
            
            # Check for structured code patterns (positive indicators of actual code)
            # These are more specific than the general language patterns
            # Made more restrictive to avoid matching documentation that describes code formats
            if (re.match(r'^\s*[HFDCIOP]\s+[A-Z0-9_]{2,}', line) or  # RPG specs (require longer identifiers)
                re.match(r'^\s*\d{2}\s+[A-Z0-9\-_]{3,}\s+(PIC|PICTURE|COMP|BINARY|PACKED)', line, re.IGNORECASE) or   # COBOL level numbers with data types
                re.match(r'^//[A-Z0-9#@$]+\s+(JOB|EXEC|DD)\s+', line) or  # JCL statements
                re.match(r'^\s*DEFINE\s+DATA\s*$', line, re.IGNORECASE) or  # Natural (exact match)
                re.match(r'^\s*[A-Z0-9_]+\s*:\s*PROC(?:EDURE)?\s*[\(;]', line, re.IGNORECASE) or  # PL/I (with parameters or semicolon)
                re.search(r'ADD\s+NAME=[A-Z0-9_]+\s+\d', line, re.IGNORECASE)):  # Mainframe library format (with sequence numbers)
                code_score += 10  # High confidence for structured code
            
            # Check for prose patterns (negative indicators - suggests documentation)
            prose_patterns = [
                r'\b(the|and|or|to|of|in|is|are|this|that|with|for|from|by|at)\b.*\b(the|and|or|to|of|in|is|are|this|that|with|for|from|by|at)\b',
                r'\b(must be|should be|can be|will be|may be)\b',
                r'\b(example|description|summary|explanation|tutorial)\b',
                r'\b(enter|specify|indicate|contains|represents)\b.*\b(field|column|value)\b'
            ]
            
            for pattern in prose_patterns:
                if re.search(pattern, line_lower):
                    doc_score += 3  # Medium confidence for prose
                    break
        
        # If we have very few lines, be conservative
        if total_non_empty_lines < 5:
            return doc_score > code_score
        
        # Calculate ratios
        doc_ratio = doc_score / total_non_empty_lines if total_non_empty_lines > 0 else 0
        code_ratio = code_score / total_non_empty_lines if total_non_empty_lines > 0 else 0
        
        # If documentation score is significantly higher than code score, it's likely documentation
        # But if there's substantial code content, don't classify as documentation
        # Also consider high documentation ratio as indicator
        if code_score >= 20:  # Strong code indicators present
            return False  # Don't classify as documentation if there's substantial code
        
        return (doc_score > code_score * 1.5) or (doc_ratio > 2.0 and code_ratio < 1.0) or (doc_score >= 20 and code_score < 5)
    
    def detect_with_confidence(self, file_path: str, 
                              content: Optional[str] = None) -> Tuple[Optional[str], str, Dict]:
        """
        Detect language with detailed confidence information.
        
        Args:
            file_path: Path to the file
            content: Optional file content
            
        Returns:
            Tuple of (language, confidence_level, details)
            - language: Detected language or None
            - confidence_level: 'high', 'medium', 'low', or 'none'
            - details: Dictionary with analysis details
        """
        # Try extension-based detection first
        extension_language = self._detect_by_extension(file_path)
        extension_guess = self._guess_from_extension(file_path)  # For details
        
        # Determine detection method and result
        method = None
        final_language = None
        content_scores = {}
        
        if extension_language is not None:
            # Extension provided definitive answer
            final_language = extension_language
            method = 'extension'
            logger.debug(f"Detected {final_language} for {file_path} using extension method (confidence: high)")
        else:
            # Fall back to content analysis
            if content is None:
                content = self._read_file_content(file_path)
            
            if content:
                content_scores = self._analyze_content(content)
                final_language = self._detect_by_content(content)
                method = 'content'
                if final_language:
                    logger.debug(f"Detected {final_language} for {file_path} using content method (scores: {content_scores})")
                else:
                    logger.debug(f"Could not detect language for {file_path} using content method (scores: {content_scores})")
            else:
                logger.debug(f"No content available for {file_path}, cannot detect language")
        
        # Determine confidence level
        confidence = 'none'
        if final_language:
            if method == 'extension':
                confidence = 'high'
            elif method == 'content' and content_scores.get(final_language, 0) >= 15:
                confidence = 'medium'
            else:
                confidence = 'low'
        
        details = {
            'extension_guess': extension_guess,
            'content_scores': content_scores,
            'final_language': final_language,
            'method': method if method else 'none'
        }
        
        return final_language, confidence, details
    
    def _is_mixed_content_pds(self, content: str) -> bool:
        """
        Check if content appears to be a mixed-content PDS (Partitioned Data Set) file.
        
        PDS files contain multiple members with ADD NAME= directives and often mix
        different content types (source code, JCL, data) in a single file.
        
        Args:
            content: File content to analyze
            
        Returns:
            True if content appears to be mixed PDS format
        """
        lines = content.split('\n')[:50]  # Check first 50 lines
        
        add_name_count = 0
        has_mixed_indicators = False
        
        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            # Count ADD NAME= directives
            if line_stripped.startswith('./') and 'ADD NAME=' in line_upper:
                add_name_count += 1
                
                # Check if we have indicators of mixed content types
                if add_name_count >= 2:
                    # Look for naming patterns that suggest mixed content
                    # e.g., EX1 (source), EX1$ (JCL), EX1D (data)
                    has_mixed_indicators = True
        
        # Consider it mixed PDS if we have multiple ADD NAME directives
        return add_name_count >= 2 and has_mixed_indicators
    
    def _detect_dominant_language_in_pds(self, content: str) -> Optional[str]:
        """
        Detect the dominant programming language in a mixed-content PDS file.
        
        This method analyzes individual sections between ADD NAME= directives
        and determines which language represents the primary content type.
        
        Args:
            content: PDS file content
            
        Returns:
            Dominant language name or None if cannot be determined
        """
        lines = content.split('\n')
        sections = self._split_pds_into_sections(lines)
        
        language_scores = {}
        program_type_counts = {}
        
        for section_name, section_lines in sections.items():
            section_content = '\n'.join(section_lines)
            
            # Classify the section type based on naming convention
            section_type = self._classify_pds_section_type(section_name)
            
            # Only analyze source code sections for language detection
            if section_type in ['SOURCE', 'UNKNOWN']:
                section_scores = self._analyze_content(section_content)
                
                # Weight scores based on section type and content quality
                weight = self._calculate_section_weight(section_name, section_content, section_type)
                
                for lang, score in section_scores.items():
                    weighted_score = score * weight
                    language_scores[lang] = language_scores.get(lang, 0) + weighted_score
                
                # Track program types for additional context
                if section_type == 'SOURCE':
                    program_type_counts[section_type] = program_type_counts.get(section_type, 0) + 1
        
        # Return the language with the highest weighted score
        if language_scores:
            dominant_language = max(language_scores, key=language_scores.get)
            
            # Apply minimum threshold to avoid false positives
            if language_scores[dominant_language] >= 10:  # Require at least medium confidence
                logger.debug(f"Detected dominant language {dominant_language} in PDS with scores: {language_scores}")
                return dominant_language
        
        logger.debug(f"Could not determine dominant language in PDS, scores: {language_scores}")
        return None
    
    def _split_pds_into_sections(self, lines: List[str]) -> Dict[str, List[str]]:
        """
        Split PDS content into individual sections based on ADD NAME= directives.
        
        Args:
            lines: List of content lines
            
        Returns:
            Dictionary mapping section names to their content lines
        """
        sections = {}
        current_section = None
        current_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            # Check for ADD NAME= directive
            if line_stripped.startswith('./') and 'ADD NAME=' in line_upper:
                # Save previous section if exists
                if current_section and current_lines:
                    sections[current_section] = current_lines.copy()
                
                # Extract section name
                import re
                match = re.search(r'ADD\s+NAME=([A-Z0-9#@$_]+)', line_upper)
                if match:
                    current_section = match.group(1)
                    current_lines = []
            elif current_section:
                # Add line to current section
                current_lines.append(line)
        
        # Save the last section
        if current_section and current_lines:
            sections[current_section] = current_lines
        
        return sections
    
    def _classify_pds_section_type(self, section_name: str) -> str:
        """
        Classify PDS section type based on naming conventions.
        
        Common mainframe naming patterns:
        - EX1, PROG1, etc. -> SOURCE (source code)
        - EX1$, PROG1$ -> JCL (job control language)
        - EX1D, PROG1D, EX1D1 -> DATA (test data)
        - EX1A, PROG1A -> ASSEMBLER (assembler routines)
        - $INDEX, INDEX -> INDEX (member list/documentation)
        
        Args:
            section_name: Name of the PDS section
            
        Returns:
            Section type: 'SOURCE', 'JCL', 'DATA', 'ASSEMBLER', 'INDEX', 'UNKNOWN'
        """
        name_upper = section_name.upper()
        
        # Index/documentation sections
        if name_upper in ['$INDEX', 'INDEX', '$DOC', 'README']:
            return 'INDEX'
        
        # JCL sections (typically end with $)
        if name_upper.endswith('$'):
            return 'JCL'
        
        # Data sections (typically end with D, D1, D2, etc.)
        if re.match(r'.*D\d*$', name_upper):
            return 'DATA'
        
        # Assembler sections (often end with A)
        if name_upper.endswith('A') and len(name_upper) > 2:
            return 'ASSEMBLER'
        
        # Default to source code for simple names
        if re.match(r'^[A-Z0-9]+$', name_upper) and not name_upper.endswith(('$', 'D', 'A')):
            return 'SOURCE'
        
        return 'UNKNOWN'
    
    def _calculate_section_weight(self, section_name: str, content: str, section_type: str) -> float:
        """
        Calculate weight for a PDS section based on type and content quality.
        
        Args:
            section_name: Name of the section
            content: Section content
            section_type: Classified section type
            
        Returns:
            Weight multiplier (0.1 to 2.0)
        """
        base_weights = {
            'SOURCE': 2.0,      # Source code sections get highest weight
            'ASSEMBLER': 1.5,   # Assembler sections get good weight
            'UNKNOWN': 1.0,     # Unknown sections get neutral weight
            'JCL': 0.3,         # JCL sections get low weight (not primary language)
            'DATA': 0.1,        # Data sections get minimal weight
            'INDEX': 0.1       # Index sections get minimal weight
        }
        
        weight = base_weights.get(section_type, 1.0)
        
        # Adjust weight based on content length and quality
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        non_empty_lines = len(lines)
        
        if non_empty_lines < 5:
            weight *= 0.5  # Reduce weight for very short sections
        elif non_empty_lines > 50:
            weight *= 1.2  # Increase weight for substantial sections
        
        # Boost weight for sections with clear programming patterns
        if section_type == 'SOURCE':
            # Look for strong programming indicators
            content_upper = content.upper()
            strong_patterns = ['PROCEDURE DIVISION', 'DEFINE DATA', 'DCL-PR', 'BEGSR']
            if any(pattern in content_upper for pattern in strong_patterns):
                weight *= 1.5
        
        return min(weight, 2.0)  # Cap at 2.0
