"""Base interface for language-specific dependency parsers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseDependencyParser(ABC):
    """Abstract base class for language-specific dependency parsers.
    
    This interface defines the contract for parsing source code in different
    languages to extract dependencies and relationships between artifacts.
    """
    
    def __init__(self):
        """Initialize parser with optional complexity calculator."""
        self.complexity_calculator = None
    
    @abstractmethod
    def parse(self, source_code: str) -> Dict[str, List[str]]:
        """
        Parse source code to extract dependencies.
        
        Args:
            source_code: Source code content
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names.
            Common keys include:
            - 'copybooks': List of copybook/include file names
            - 'calls': List of called program names
            - 'cics_links': List of CICS linked programs
            - 'datasets': List of dataset references
            - 'includes': List of included JCL procedures
            - 'sql_includes': List of SQL include members
            - 'tables': List of database table references
        """
        pass
    
    def parse_with_complexity(self, source_code: str) -> Dict[str, Any]:
        """
        Parse source code to extract both dependencies and complexity metrics.
        
        This method combines dependency extraction and complexity calculation
        in a single pass to avoid redundant parsing.
        
        Args:
            source_code: Source code content
            
        Returns:
            Dictionary with:
            - 'dependencies': Dict mapping dependency types to lists of artifact names
            - 'complexity': Dict with complexity metrics (if calculator available)
                - 'loc_metrics': Dict with loc, comment_lines, blank_lines, total_lines
                - 'cyclomatic_complexity': int
        """
        result = {
            'dependencies': self.parse(source_code)
        }
        
        # Calculate complexity if calculator is available
        if self.complexity_calculator:
            result['complexity'] = self.complexity_calculator.calculate_all_metrics(source_code)
        
        return result
    
    @abstractmethod
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of dependency patterns this parser supports.
        
        Returns:
            List of pattern names (e.g., ['COPY', 'CALL', 'EXEC CICS'])
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser supports.
        
        Returns:
            List of file extensions (e.g., ['.cbl', '.cob', '.cobol'])
        """
        pass
    
    def parse_file(self, file_path: str) -> Dict[str, List[str]]:
        """
        Parse a source file to extract dependencies.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Dictionary mapping dependency types to lists of artifact names
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        return self.parse(source_code)
