"""REXX complexity calculator."""

import re
from typing import Dict
from .base_complexity_calculator import BaseComplexityCalculator


class REXXComplexityCalculator(BaseComplexityCalculator):
    """Calculates complexity metrics for REXX source code."""
    
    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics for REXX.
        
        Handles:
        - Single-line comments (/* ... */)
        - Multi-line comments (/* ... */)
        - Blank lines
        
        Args:
            source_code: REXX source code
            
        Returns:
            Dictionary with loc, comment_lines, blank_lines, total_lines
        """
        lines = source_code.split('\n')
        total_lines = len(lines)
        blank_lines = 0
        comment_lines = 0
        
        in_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check for blank line
            if not stripped:
                blank_lines += 1
                continue
            
            # Track multi-line comments
            line_is_comment = False
            temp_line = stripped
            
            # Check if we're in a multi-line comment
            if in_comment:
                line_is_comment = True
                if '*/' in temp_line:
                    in_comment = False
            else:
                # Check for comment start
                if '/*' in temp_line:
                    # Check if comment ends on same line
                    if '*/' in temp_line:
                        # Single-line comment - check if there's code before it
                        before_comment = temp_line.split('/*')[0].strip()
                        if not before_comment:
                            line_is_comment = True
                    else:
                        # Multi-line comment starts
                        in_comment = True
                        before_comment = temp_line.split('/*')[0].strip()
                        if not before_comment:
                            line_is_comment = True
            
            if line_is_comment:
                comment_lines += 1
        
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
        Calculate cyclomatic complexity for REXX.
        
        Decision points in REXX:
        - IF/THEN statements
        - SELECT/WHEN statements
        - DO WHILE/UNTIL loops
        - AND/OR operators in conditions
        
        Args:
            source_code: REXX source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Remove comments for cleaner parsing
        normalized = self._remove_comments(source_code).upper()
        
        # Count IF statements
        complexity += len(re.findall(r'\bIF\b', normalized))
        
        # Count WHEN clauses in SELECT statements
        complexity += len(re.findall(r'\bWHEN\b', normalized))
        
        # Count DO WHILE/UNTIL loops
        complexity += len(re.findall(r'\bDO\s+WHILE\b', normalized))
        complexity += len(re.findall(r'\bDO\s+UNTIL\b', normalized))
        
        # Count logical operators (AND, OR)
        complexity += len(re.findall(r'\b&\b', normalized))  # & is AND in REXX
        complexity += len(re.findall(r'\b\|\b', normalized))  # | is OR in REXX
        complexity += len(re.findall(r'\bAND\b', normalized))
        complexity += len(re.findall(r'\bOR\b', normalized))
        
        return complexity
    
    def _remove_comments(self, source_code: str) -> str:
        """
        Remove comments from REXX source.
        
        Args:
            source_code: Raw source code
            
        Returns:
            Source code without comments
        """
        # Remove /* ... */ comments (both single and multi-line)
        result = re.sub(r'/\*.*?\*/', '', source_code, flags=re.DOTALL)
        return result
