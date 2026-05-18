# Parser Framework Documentation

This directory contains the enhanced parser framework for program-level dependency tracking in mainframe languages.

## Overview

The parser framework has been enhanced to support **program-level dependency tracking**, enabling accurate analysis of multi-program files common in mainframe environments. Each parser can now detect individual programs within files and track dependencies at program granularity.

## Enhanced Parsers

### Language Support

| Language | Parser | Multi-Program Support | Program Boundary Detection |
|----------|--------|----------------------|----------------------------|
| **RPG** | `rpg_parser.py` | ✅ Yes | H-spec, F-spec, Procedure definitions |
| **Assembler** | `asm_parser.py` | ✅ Yes | CSECT boundaries, ENTRY points |
| **Natural** | `natural_parser.py` | ✅ Yes | DEFINE DATA PROGRAM/SUBPROGRAM |
| **REXX** | `rexx_parser.py` | ✅ Yes | Procedure definitions |
| **COBOL** | `cobol_parser.py` | ✅ Enhanced | Program boundaries + copybook analysis |
| **PL/I** | `pli_parser.py` | ✅ Enhanced | Program boundaries + include analysis |
| **JCL** | `jcl_parser.py` | ➖ N/A | Job-level analysis |

### Key Features

#### 1. Program Boundary Detection
All enhanced parsers implement program boundary detection:

```python
from legacy_analyzer.parsers.rpg_parser import RPGDependencyParser

parser = RPGDependencyParser()
result = parser.parse_file("PAYROLL.rpgle")

# Access detected programs
for program in result.programs:
    print(f"Program: {program.program_name}")
    print(f"Lines: {program.start_line}-{program.end_line}")
    print(f"Type: {program.program_type}")
```

#### 2. Program-Level Dependencies
Dependencies are tracked per individual program:

```python
# Get dependencies for specific program
program_deps = result.program_dependencies.get("PayrollMain", {})
calls = program_deps.get("calls", [])
copybooks = program_deps.get("copybooks", [])
```

#### 3. Copybook/Include Analysis
COBOL and PL/I parsers analyze included content for executable code:

```python
from legacy_analyzer.parsers.cobol_parser import COBOLDependencyParser

parser = COBOLDependencyParser()
result = parser.parse_file("MAINPROG.cbl")

# Check copybook analysis results
for copybook_result in result.copybook_analysis:
    if copybook_result.has_executable_code:
        print(f"Executable copybook: {copybook_result.copybook_name}")
```

## Parser Architecture

### Base Classes

#### BaseDependencyParser
All parsers inherit from `BaseDependencyParser`:

```python
class BaseDependencyParser(ABC):
    @abstractmethod
    def parse(self, source_code: str) -> ParseResult:
        """Parse source code and extract dependencies."""
        pass
    
    @abstractmethod
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported file patterns."""
        pass
```

#### Enhanced Parse Results
Enhanced parsers return `EnhancedParseResult` with program-level data:

```python
@dataclass
class EnhancedParseResult:
    programs: List[ProgramBoundary]           # Individual programs detected
    program_dependencies: Dict[str, Dict]     # Dependencies per program
    dependencies: Dict[str, List]             # File-level dependencies (legacy)
    copybook_analysis: List[CopybookAnalysisResult]  # Copybook analysis results
    complexity: Optional[ComplexityMetrics]   # Complexity metrics
```

### Program Boundary Model

```python
@dataclass
class ProgramBoundary:
    program_name: str           # Name of the program
    start_line: int            # Starting line number
    end_line: int              # Ending line number
    program_type: ProgramType  # MAIN, PROCEDURE, CSECT, SUBPROGRAM
    language: str              # Programming language
    entry_points: List[str]    # Entry point names
    file_path: str             # Source file path
    confidence_level: float    # Detection confidence (0.0-1.0)
    metadata: Optional[Dict]   # Additional metadata
```

## Usage Examples

### Basic Program Analysis

```python
from legacy_analyzer.parsers.parser_factory import ParserFactory

# Get appropriate parser for file
parser = ParserFactory.get_parser("PAYROLL.rpgle")

# Parse file with program-level detection
result = parser.parse_file("PAYROLL.rpgle")

# Process detected programs
for program in result.programs:
    print(f"Found program: {program.program_name}")
    
    # Get program-specific dependencies
    prog_deps = result.program_dependencies.get(program.program_name, {})
    
    for call in prog_deps.get("calls", []):
        print(f"  Calls: {call}")
```

### Multi-Language Analysis

```python
from legacy_analyzer.parsers import (
    RPGDependencyParser, 
    COBOLDependencyParser,
    NaturalDependencyParser
)

parsers = {
    '.rpgle': RPGDependencyParser(),
    '.cbl': COBOLDependencyParser(), 
    '.NSP': NaturalDependencyParser()
}

for file_path in source_files:
    ext = Path(file_path).suffix
    if ext in parsers:
        result = parsers[ext].parse_file(file_path)
        # Process results...
```

### Integration with Enhanced Static Analyzer

```python
from legacy_analyzer.enhanced_static_analyzer import EnhancedStaticCodeAnalyzer

# Setup database
db_adapter = SQLiteAdapter("analysis.db")
db_adapter.connect()

# Create analyzer
analyzer = EnhancedStaticCodeAnalyzer(db_adapter)

# Analyze with program-level granularity
results = analyzer.analyze_source_file("PAYROLL.rpgle", "RPG")

# Results include program boundaries and dependencies
programs = results.get('programs', [])
program_deps = results.get('program_dependencies', {})
```

## Language-Specific Details

### RPG Parser (`rpg_parser.py`)
- **Program Detection**: H-spec (Header), F-spec (File), Procedure definitions
- **Boundary Markers**: `P ProcName B` (Begin) / `P ProcName E` (End)
- **Entry Points**: Procedure names, main program entry
- **Dependencies**: CALLP, EVAL, File operations

### Assembler Parser (`asm_parser.py`)
- **Program Detection**: CSECT (Control Sections), ENTRY points
- **Boundary Markers**: `CSECT`, `ENTRY`, `END`
- **Entry Points**: CSECT names, ENTRY labels
- **Dependencies**: CALL, LINK, External references

### Natural Parser (`natural_parser.py`)
- **Program Detection**: `DEFINE DATA PROGRAM`, `DEFINE DATA SUBPROGRAM`
- **Boundary Markers**: `DEFINE DATA` / `END-DEFINE`, `END`
- **Entry Points**: Program names, subprogram names
- **Dependencies**: CALLNAT, FETCH, FIND, READ

### REXX Parser (`rexx_parser.py`)
- **Program Detection**: Procedure definitions, function definitions
- **Boundary Markers**: Function/procedure start/end
- **Entry Points**: Function names, procedure names
- **Dependencies**: CALL, Function calls, External commands

### COBOL Parser (`cobol_parser.py`)
- **Program Detection**: `PROGRAM-ID` sections
- **Copybook Analysis**: Analyzes COPY statements for executable content
- **Boundary Markers**: `IDENTIFICATION DIVISION` / `END PROGRAM`
- **Dependencies**: CALL, COPY (with executable analysis), File operations

### PL/I Parser (`pli_parser.py`)
- **Program Detection**: PROCEDURE statements with OPTIONS(MAIN)
- **Include Analysis**: Analyzes %INCLUDE statements for executable content
- **Boundary Markers**: `PROCEDURE` / `END`
- **Dependencies**: CALL, %INCLUDE (with executable analysis), File operations

## Complexity Calculators

Each parser has an associated complexity calculator:

- `rpg_complexity_calculator.py` - RPG-specific complexity metrics
- `asm_complexity_calculator.py` - Assembler complexity metrics
- `natural_complexity_calculator.py` - Natural complexity metrics
- `rexx_complexity_calculator.py` - REXX complexity metrics
- `cobol_complexity_calculator.py` - COBOL complexity metrics
- `pli_complexity_calculator.py` - PL/I complexity metrics

## Error Handling

### Graceful Degradation
Parsers implement graceful degradation for malformed code:

```python
try:
    result = parser.parse_file(file_path)
    if not result.programs:
        # Fall back to file-level analysis
        print("No programs detected, using file-level analysis")
except ParseError as e:
    # Handle parse errors gracefully
    print(f"Parse error: {e}, falling back to basic analysis")
```

### Confidence Levels
Program boundary detection includes confidence scoring:

```python
for program in result.programs:
    if program.confidence_level < 0.8:
        print(f"Low confidence detection: {program.program_name}")
```

## Testing

### Unit Tests
Each parser has comprehensive unit tests:
- `tests/test_rpg_parser.py`
- `tests/test_asm_parser.py`
- `tests/test_natural_parser.py`
- `tests/test_rexx_parser.py`
- `tests/test_cobol_parser.py`
- `tests/test_pli_parser.py`

### Property-Based Tests
Property-based tests validate parser behavior:
- `tests/test_rpg_multi_program_properties.py`
- `tests/test_asm_multi_program_properties.py`
- `tests/test_natural_multi_program_properties.py`
- `tests/test_rexx_multi_program_properties.py`

### Integration Tests
- `tests/test_program_level_integration_simple.py`
- `tests/test_multi_language_integration.py`

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: Parse program boundaries first, detailed analysis on demand
2. **Caching**: Cache parse results for frequently accessed files
3. **Parallel Processing**: Process multiple files concurrently
4. **Incremental Analysis**: Only re-parse changed sections

### Memory Management
- Stream processing for large files
- Cleanup of temporary objects
- Efficient string handling for mainframe character sets

## Migration from File-Level Analysis

### Backward Compatibility
Enhanced parsers maintain backward compatibility:

```python
# Legacy file-level access still works
result = parser.parse_file("PROG.cbl")
file_level_deps = result.dependencies  # Still available

# New program-level access
program_level_deps = result.program_dependencies  # Enhanced
```

### Migration Strategy
1. **Phase 1**: Deploy enhanced parsers with dual output
2. **Phase 2**: Update analysis components to use program-level data
3. **Phase 3**: Migrate existing data from file-level to program-level
4. **Phase 4**: Deprecate file-level interfaces (optional)

## See Also

- [Parser Factory Documentation](PARSER_FACTORY_README.md)
- [Static Analysis Guide](../../docs/STATIC_ANALYSIS_GUIDE.md)
- [Flow Analysis Guide](../../docs/FLOW_ANALYSIS_GUIDE.md)
- [Migration Workflow Guide](../../docs/MIGRATION_WORKFLOW_GUIDE.md)