"""Natural language complexity calculator."""

import re
from typing import Dict
from .base_complexity_calculator import BaseComplexityCalculator


class NATURALComplexityCalculator(BaseComplexityCalculator):
    """Calculates complexity metrics for Natural (Software AG) source code."""

    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """Calculate lines of code metrics for Natural.

        Natural comments start with * or /* in the first non-blank position.
        Header metadata lines (e.g., * :Mode S) are also comments.
        """
        lines = source_code.split('\n')
        total_lines = len(lines)
        comment_lines = 0
        blank_lines = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('*') or stripped.startswith('/*'):
                comment_lines += 1
            elif stripped.startswith('**'):
                comment_lines += 1

        loc = total_lines - blank_lines - comment_lines
        return {
            'loc': loc,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'total_lines': total_lines
        }

    def calculate_cyclomatic_complexity(self, source_code: str) -> int:
        """Calculate cyclomatic complexity for Natural.

        Decision points in Natural:
        - IF / ELSE IF
        - DECIDE ON / DECIDE FOR (CASE equivalent)
        - FOR / REPEAT / READ (loop constructs)
        - FIND / HISTOGRAM (database loops)
        - AND / OR (compound conditions)
        """
        complexity = 1  # Base complexity

        # Remove comments
        clean_lines = []
        for line in source_code.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('*') and not stripped.startswith('/*'):
                clean_lines.append(stripped.upper())

        normalized = '\n'.join(clean_lines)

        # Count decision keywords
        decision_keywords = [
            r'\bIF\b',
            r'\bDECIDE\b',
            r'\bFOR\b',
            r'\bREPEAT\b',
            r'\bREAD\b',
            r'\bFIND\b',
            r'\bHISTOGRAM\b',
            r'\bWHEN\b',
            r'\bAND\b',
            r'\bOR\b',
        ]

        for pattern in decision_keywords:
            complexity += len(re.findall(pattern, normalized))

        return complexity
