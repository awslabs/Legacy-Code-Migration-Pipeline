"""Base interface for language-specific complexity calculators."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseComplexityCalculator(ABC):
    """Abstract base class for language-specific complexity calculators.
    
    This interface defines the contract for calculating complexity metrics
    from source code in different languages.
    """
    
    @abstractmethod
    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics.
        
        Args:
            source_code: Source code content
            
        Returns:
            Dictionary with:
            - 'loc': Lines of code (excluding comments and blanks)
            - 'comment_lines': Number of comment lines
            - 'blank_lines': Number of blank lines
            - 'total_lines': Total number of lines
        """
        pass
    
    @abstractmethod
    def calculate_cyclomatic_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity.
        
        Counts decision points (IF, WHILE, FOR, CASE, AND, OR, etc.)
        
        Args:
            source_code: Source code content
            
        Returns:
            Cyclomatic complexity score
        """
        pass
    
    def calculate_all_metrics(self, source_code: str) -> Dict[str, Any]:
        """
        Calculate all complexity metrics.
        
        Args:
            source_code: Source code content
            
        Returns:
            Dictionary with all metrics:
            - loc_metrics: Dict with loc, comment_lines, blank_lines, total_lines
            - cyclomatic_complexity: int
        """
        return {
            'loc_metrics': self.calculate_loc_metrics(source_code),
            'cyclomatic_complexity': self.calculate_cyclomatic_complexity(source_code)
        }
