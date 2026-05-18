"""RPG complexity calculator."""

import re
from typing import Dict
from .base_complexity_calculator import BaseComplexityCalculator


class RPGComplexityCalculator(BaseComplexityCalculator):
    """Calculates complexity metrics for RPG/RPG IV source code."""
    
    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics for RPG.
        
        Handles:
        - Fixed format (columns 6-80)
        - Free format (/FREE ... /END-FREE)
        - Comment lines (* in column 7 for fixed, // for free)
        - Blank lines
        
        Args:
            source_code: RPG source code
            
        Returns:
            Dictionary with loc, comment_lines, blank_lines, total_lines
        """
        lines = source_code.split('\n')
        total_lines = len(lines)
        blank_lines = 0
        comment_lines = 0
        in_free_format = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check for blank line
            if not stripped:
                blank_lines += 1
                continue
            
            # Check for free format markers
            if stripped.upper().startswith('/FREE'):
                in_free_format = True
                continue
            elif stripped.upper().startswith('/END-FREE'):
                in_free_format = False
                continue
            
            # Check for comment line
            if in_free_format:
                # Free format comments start with //
                if stripped.startswith('//'):
                    comment_lines += 1
                    continue
            else:
                # Fixed format comments: * in column 7 (position 6)
                if len(line) >= 7 and line[6] == '*':
                    comment_lines += 1
                    continue
                # Also check for lines starting with *
                if stripped.startswith('*'):
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
        Calculate cyclomatic complexity for RPG.
        
        Decision points in RPG:
        - IF/ELSEIF statements
        - SELECT/WHEN statements
        - DOW (Do While) loops
        - DOU (Do Until) loops
        - FOR loops
        - AND/OR operators in conditions
        - WHEN clauses
        
        Args:
            source_code: RPG source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code (uppercase for pattern matching)
        normalized = source_code.upper()
        
        # Count IF statements
        complexity += len(re.findall(r'\bIF\b', normalized))
        
        # Count ELSEIF statements
        complexity += len(re.findall(r'\bELSEIF\b', normalized))
        
        # Count WHEN clauses in SELECT statements
        complexity += len(re.findall(r'\bWHEN\b', normalized))
        
        # Count DOW (Do While) loops
        complexity += len(re.findall(r'\bDOW\b', normalized))
        
        # Count DOU (Do Until) loops
        complexity += len(re.findall(r'\bDOU\b', normalized))
        
        # Count FOR loops
        complexity += len(re.findall(r'\bFOR\b', normalized))
        
        # Count logical operators (AND, OR)
        complexity += len(re.findall(r'\bAND\b', normalized))
        complexity += len(re.findall(r'\bOR\b', normalized))
        
        return complexity
