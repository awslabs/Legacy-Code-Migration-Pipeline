"""Parser factory for creating language-specific parsers."""

import os
from typing import Dict, Optional, List
from .base_parser import BaseDependencyParser
from .cobol_parser import COBOLDependencyParser
from .jcl_parser import JCLDependencyParser
from .pli_parser import PLIDependencyParser
from .rpg_parser import RPGDependencyParser
from .natural_parser import NaturalDependencyParser
from .rexx_parser import REXXDependencyParser


class ParserFactory:
    """Factory for creating language-specific dependency parsers."""
    
    # Registry of parsers by language name
    _parsers: Dict[str, type] = {
        'COBOL': COBOLDependencyParser,
        'JCL': JCLDependencyParser,
        'PLI': PLIDependencyParser,
        'PL/I': PLIDependencyParser,
        'RPG': RPGDependencyParser,
        'NATURAL': NaturalDependencyParser,
        'REXX': REXXDependencyParser,
    }
    
    # Extension to language mapping
    _extension_map: Dict[str, str] = {
        '.cbl': 'COBOL',
        '.cob': 'COBOL',
        '.cobol': 'COBOL',
        '.cpy': 'COBOL',  # COBOL copybooks
        '.jcl': 'JCL',
        '.pli': 'PLI',
        '.pl1': 'PLI',
        '.rpg': 'RPG',
        '.rpgle': 'RPG',
        '.sqlrpgle': 'RPG',
        '.nsp': 'NATURAL',
        '.nsn': 'NATURAL',
        '.nsc': 'NATURAL',
        '.nsl': 'NATURAL',
        '.nsg': 'NATURAL',
        '.nsd': 'NATURAL',
        '.nsa': 'NATURAL',
        '.ns8': 'NATURAL',
        '.rexx': 'REXX',
        '.rex': 'REXX',
    }
    
    @classmethod
    def create_parser(cls, language: str) -> BaseDependencyParser:
        """
        Create a parser for the specified language.
        
        Args:
            language: Programming language name (COBOL, JCL, PLI, etc.)
            
        Returns:
            Parser instance for the language
            
        Raises:
            ValueError: If language is not supported
        """
        language_upper = language.upper()
        
        if language_upper not in cls._parsers:
            supported = ', '.join(cls._parsers.keys())
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages: {supported}"
            )
        
        parser_class = cls._parsers[language_upper]
        return parser_class()
    
    @classmethod
    def get_parser_for_file(cls, file_path: str) -> Optional[BaseDependencyParser]:
        """
        Determine and create parser based on file extension.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Parser instance for the file, or None if extension not recognized
        """
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()
        
        if ext_lower not in cls._extension_map:
            return None
        
        language = cls._extension_map[ext_lower]
        return cls.create_parser(language)
    
    @classmethod
    def register_parser(cls, language: str, parser_class: type, 
                       extensions: Optional[List[str]] = None) -> None:
        """
        Register a new parser for a language.
        
        Args:
            language: Programming language name
            parser_class: Parser class (must inherit from BaseDependencyParser)
            extensions: Optional list of file extensions to associate with this parser
        """
        if not issubclass(parser_class, BaseDependencyParser):
            raise TypeError(
                f"Parser class must inherit from BaseDependencyParser"
            )
        
        language_upper = language.upper()
        cls._parsers[language_upper] = parser_class
        
        # Register extensions if provided
        if extensions:
            for ext in extensions:
                if not ext.startswith('.'):
                    ext = '.' + ext
                cls._extension_map[ext.lower()] = language_upper
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language names
        """
        return list(cls._parsers.keys())
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of file extensions
        """
        return list(cls._extension_map.keys())
