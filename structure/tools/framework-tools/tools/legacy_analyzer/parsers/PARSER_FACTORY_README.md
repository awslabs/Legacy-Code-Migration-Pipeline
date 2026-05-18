# Parser Factory

The `ParserFactory` provides a centralized way to create and manage language-specific dependency parsers for the Legacy Analyzer system.

## Overview

The Parser Factory implements the Factory design pattern to:
- Create parsers by language name
- Auto-detect parsers from file extensions
- Register custom parsers dynamically
- Query supported languages and extensions

## Supported Languages

The factory currently supports the following languages:

| Language | Parser Class | File Extensions | Known Limitations |
|----------|-------------|-----------------|-------------------|
| COBOL | `COBOLDependencyParser` | `.cbl`, `.cob`, `.cobol`, `.cpy` | None |
| JCL | `JCLDependencyParser` | `.jcl` | None |
| PL/I | `PLIDependencyParser` | `.pli`, `.pl1`, `.inc` | None |
| RPG | `RPGDependencyParser` | `.rpg`, `.rpgle`, `.sqlrpgle`, `.rpg38`, `.mbr` | Embedded SQL with C-spec continuation lines not supported |
| Natural | `NaturalDependencyParser` | `.NSP`, `.NSN`, `.NSC`, `.NSL`, `.NSG`, `.NSD`, `.NSA`, `.NS8` | None |

## Usage

### Creating a Parser by Language Name

```python
from legacy_analyzer.parsers.parser_factory import ParserFactory

# Create a COBOL parser
cobol_parser = ParserFactory.create_parser('COBOL')

# Create a PL/I parser (case-insensitive)
pli_parser = ParserFactory.create_parser('pli')

# Create a Natural parser
natural_parser = ParserFactory.create_parser('NATURAL')
```

### Auto-Detecting Parser from File Extension

```python
from legacy_analyzer.parsers.parser_factory import ParserFactory

# Auto-detect parser based on file extension
parser = ParserFactory.get_parser_for_file('PAYROLL.cbl')
if parser:
    dependencies = parser.parse_file('PAYROLL.cbl')
else:
    print("No parser found for this file type")

# Works with full paths
parser = ParserFactory.get_parser_for_file('/path/to/PROGRAM.rpgle')

# Case-insensitive extension matching
parser = ParserFactory.get_parser_for_file('PROGRAM.CBL')  # Works
parser = ParserFactory.get_parser_for_file('program.cbl')  # Also works
```

### Querying Supported Languages and Extensions

```python
from legacy_analyzer.parsers.parser_factory import ParserFactory

# Get list of supported languages
languages = ParserFactory.get_supported_languages()
print(f"Supported languages: {', '.join(languages)}")

# Get list of supported file extensions
extensions = ParserFactory.get_supported_extensions()
print(f"Supported extensions: {', '.join(extensions)}")
```

### Registering Custom Parsers

You can extend the factory by registering custom parsers:

```python
from legacy_analyzer.parsers.parser_factory import ParserFactory
from legacy_analyzer.parsers.base_parser import BaseDependencyParser

# Define a custom parser
class FortranParser(BaseDependencyParser):
    def parse(self, source_code):
        # Implementation here
        return {'includes': [], 'calls': []}
    
    def get_supported_patterns(self):
        return ['INCLUDE', 'CALL']
    
    def get_supported_extensions(self):
        return ['.f', '.f90', '.for']

# Register the custom parser
ParserFactory.register_parser(
    'FORTRAN',
    FortranParser,
    extensions=['.f', '.f90', '.for']
)

# Now you can use it
fortran_parser = ParserFactory.create_parser('FORTRAN')
parser = ParserFactory.get_parser_for_file('program.f90')
```

## API Reference

### `create_parser(language: str) -> BaseDependencyParser`

Creates a parser instance for the specified language.

**Parameters:**
- `language` (str): Programming language name (case-insensitive)

**Returns:**
- `BaseDependencyParser`: Parser instance for the language

**Raises:**
- `ValueError`: If the language is not supported

**Example:**
```python
parser = ParserFactory.create_parser('COBOL')
```

### `get_parser_for_file(file_path: str) -> Optional[BaseDependencyParser]`

Auto-detects and creates a parser based on file extension.

**Parameters:**
- `file_path` (str): Path to source file (can be relative or absolute)

**Returns:**
- `BaseDependencyParser`: Parser instance for the file, or `None` if extension not recognized

**Example:**
```python
parser = ParserFactory.get_parser_for_file('PROGRAM.cbl')
if parser:
    dependencies = parser.parse_file('PROGRAM.cbl')
```

### `register_parser(language: str, parser_class: type, extensions: Optional[List[str]] = None) -> None`

Registers a new parser for a language.

**Parameters:**
- `language` (str): Programming language name
- `parser_class` (type): Parser class (must inherit from `BaseDependencyParser`)
- `extensions` (Optional[List[str]]): File extensions to associate with this parser

**Raises:**
- `TypeError`: If parser class doesn't inherit from `BaseDependencyParser`

**Example:**
```python
ParserFactory.register_parser('FORTRAN', FortranParser, ['.f', '.f90'])
```

### `get_supported_languages() -> List[str]`

Returns a list of all supported language names.

**Returns:**
- `List[str]`: List of language names

**Example:**
```python
languages = ParserFactory.get_supported_languages()
# ['COBOL', 'JCL', 'PLI', 'PL/I', 'RPG', 'NATURAL']
```

### `get_supported_extensions() -> List[str]`

Returns a list of all supported file extensions.

**Returns:**
- `List[str]`: List of file extensions (with leading dot)

**Example:**
```python
extensions = ParserFactory.get_supported_extensions()
# ['.cbl', '.cob', '.cobol', '.jcl', '.pli', '.pl1', ...]
```

## Design Patterns

### Factory Pattern

The Parser Factory implements the Factory design pattern, which:
- Encapsulates object creation logic
- Provides a single point of access for creating parsers
- Allows runtime selection of parser based on language or file extension
- Supports extensibility through registration

### Registry Pattern

The factory maintains internal registries:
- `_parsers`: Maps language names to parser classes
- `_extension_map`: Maps file extensions to language names

This allows for:
- Fast lookup of parsers
- Dynamic registration of new parsers
- Decoupling of parser selection from parser implementation

## Cross-Language Support

The Parser Factory is designed to support multi-language legacy systems:

```python
from legacy_analyzer.parsers.parser_factory import ParserFactory
import os

def analyze_project(project_dir):
    """Analyze all source files in a project."""
    dependencies = {}
    
    for root, dirs, files in os.walk(project_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # Auto-detect parser
            parser = ParserFactory.get_parser_for_file(file_path)
            
            if parser:
                # Parse the file
                deps = parser.parse_file(file_path)
                dependencies[filename] = deps
    
    return dependencies
```

## Error Handling

The factory provides clear error messages:

```python
# Unsupported language
try:
    parser = ParserFactory.create_parser('FORTRAN')
except ValueError as e:
    print(e)
    # Output: Unsupported language: FORTRAN. Supported languages: COBOL, JCL, PLI, PL/I, RPG, NATURAL

# Invalid parser class
try:
    class NotAParser:
        pass
    ParserFactory.register_parser('INVALID', NotAParser)
except TypeError as e:
    print(e)
    # Output: Parser class must inherit from BaseDependencyParser
```

## Testing

The Parser Factory includes comprehensive unit tests in `tests/test_parser_factory.py`:

- Parser creation by language name
- Auto-detection from file extensions
- Case-insensitive matching
- Custom parser registration
- Error handling
- Cross-language support

Run tests with:
```bash
pytest tests/test_parser_factory.py -v
```

## Integration with Legacy Analyzer

The Parser Factory is used throughout the Legacy Analyzer system:

1. **Static Analysis**: Auto-detect and parse source files
2. **Dependency Extraction**: Create appropriate parser for each file type
3. **Flow Analysis**: Parse programs to build call graphs
4. **Migration Planning**: Analyze multi-language codebases

## Performance Considerations

- Parser instances are created on-demand (not cached)
- Extension lookup is O(1) using dictionary
- Language lookup is O(1) using dictionary
- File extension matching is case-insensitive

## Future Enhancements

Potential future enhancements:

1. **Parser Caching**: Cache parser instances for reuse
2. **Lazy Loading**: Load parser classes only when needed
3. **Plugin System**: Load parsers from external modules
4. **Configuration**: Load parser registry from configuration file
5. **Versioning**: Support multiple versions of the same language
6. **Parallel Parsing**: Support parallel file parsing with factory

## Parser-Specific Limitations

### RPG Parser

The RPG parser has the following known limitation:

**Embedded SQL with C-spec Continuation Lines**

The parser does not currently support embedded SQL statements that use C-spec continuation lines. For example:

```rpg
C/EXEC SQL
C+ SELECT * FROM CUSTOMER WHERE CUSTID = :CUSTID
C/END-EXEC
```

**Workaround:** Use free-format EXEC SQL blocks or ensure SQL statements are on a single line:

```rpg
**FREE
EXEC SQL SELECT * FROM CUSTOMER WHERE CUSTID = :CUSTID END-EXEC;
```

This limitation affects only embedded SQL table extraction. All other RPG parsing features (CALL statements, /COPY statements, file declarations, etc.) work correctly.

## See Also

- [Base Parser Interface](base_parser.py)
- [COBOL Parser](cobol_parser.py)
- [JCL Parser](jcl_parser.py)
- [PL/I Parser](pli_parser.py)
- [RPG Parser](rpg_parser.py)
- [Natural Parser](natural_parser.py)
- [Parser Factory Tests](../../tests/test_parser_factory.py)
- [Parser Factory Demo](../../examples/parser_factory_demo.py)
