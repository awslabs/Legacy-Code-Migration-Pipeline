"""PL/I complexity calculator."""

import re
from typing import Dict
from .base_complexity_calculator import BaseComplexityCalculator


class PLIComplexityCalculator(BaseComplexityCalculator):
    """Calculates complexity metrics for PL/I source code."""
    
    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics for PL/I.
        
        Handles:
        - /* */ style comments
        - Blank lines
        
        Args:
            source_code: PL/I source code
            
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
            
            # Check for comment start
            if '/*' in stripped:
                in_comment = True
            
            # If in comment, count as comment line
            if in_comment:
                comment_lines += 1
            
            # Check for comment end
            if '*/' in stripped:
                in_comment = False
        
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
        Calculate cyclomatic complexity for PL/I.
        
        Decision points in PL/I:
        - IF statements
        - DO WHILE/UNTIL
        - SELECT/WHEN statements
        - DO loops with conditions
        - & (AND) and | (OR) operators
        
        Args:
            source_code: PL/I source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code
        normalized = source_code.upper()
        
        # Count IF statements
        complexity += len(re.findall(r'\bIF\b', normalized))
        
        # Count DO WHILE/UNTIL
        complexity += len(re.findall(r'\bDO\s+(?:WHILE|UNTIL)\b', normalized))
        
        # Count SELECT/WHEN statements
        complexity += len(re.findall(r'\bWHEN\b', normalized))
        
        # Count logical operators
        complexity += len(re.findall(r'&', normalized))  # AND
        complexity += len(re.findall(r'\|', normalized))  # OR
        
        return complexity
