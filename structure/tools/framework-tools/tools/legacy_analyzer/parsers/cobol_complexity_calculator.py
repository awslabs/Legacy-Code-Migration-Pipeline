"""COBOL complexity calculator."""

import re
from typing import Dict
from .base_complexity_calculator import BaseComplexityCalculator


class COBOLComplexityCalculator(BaseComplexityCalculator):
    """Calculates complexity metrics for COBOL source code."""
    
    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics for COBOL.
        
        Handles:
        - Fixed format (columns 7-72)
        - Free format
        - Comments (* or / in column 7)
        - Blank lines
        
        Args:
            source_code: COBOL source code
            
        Returns:
            Dictionary with loc, comment_lines, blank_lines, total_lines
        """
        lines = source_code.split('\n')
        total_lines = len(lines)
        blank_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Check for blank line
            if not stripped:
                blank_lines += 1
                continue
            
            # Check for comment line
            # COBOL comments: * or / in column 7 (position 6 in 0-indexed)
            if len(line) >= 7 and line[6] in ('*', '/'):
                comment_lines += 1
                continue
            
            # Check for free-format comment (line starting with * or /)
            if stripped[0] in ('*', '/'):
                comment_lines += 1
                continue
        
        # Calculate LOC
        loc = total_lines - blank_lines - comment_lines
        
        return {
            'loc': loc,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'total_lines': total_lines
        }
    
    def calculate_cyclomatic_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for COBOL.
        
        Decision points in COBOL:
        - IF statements
        - EVALUATE statements (WHEN clauses)
        - PERFORM UNTIL/VARYING
        - SEARCH/SEARCH ALL (WHEN clauses)
        - AND/OR in conditions
        
        Args:
            source_code: COBOL source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code (uppercase for pattern matching)
        normalized = source_code.upper()
        
        # Count IF statements (but not END-IF)
        complexity += len(re.findall(r'(?<!END-)(?<!ELSE\s)\bIF\b', normalized))
        
        # Count EVALUATE statements (each WHEN adds complexity)
        complexity += len(re.findall(r'\bWHEN\b', normalized))
        
        # Count PERFORM UNTIL/VARYING
        complexity += len(re.findall(r'\bPERFORM\s+(?:UNTIL|VARYING)\b', normalized))
        
        # Count SEARCH WHEN clauses
        complexity += len(re.findall(r'\bSEARCH\b', normalized))
        
        # Count logical operators (AND, OR) - each adds a decision point
        complexity += len(re.findall(r'\bAND\b', normalized))
        complexity += len(re.findall(r'\bOR\b', normalized))
        
        return complexity
