# Flow Analysis Module


## **Dual-Source Architecture Integration**

The flow analysis module leverages both data sources for enhanced capabilities:

1. **Source Code Analysis** (primary): Direct parsing of program dependencies from source code
2. **Catalog Metadata** (enhancement): CICS, JCL, and program catalog information for context

### **Enhanced Analysis Capabilities**

- **Entry Point Classification**: ONLINE (CICS) + BATCH (JCL) + INFERRED (code analysis)
- **Dependency-Aware Reconciliation**: Smart classification based on call relationships
- **Program-Level Granularity**: Accurate program-to-program flows within multi-program files
- **Cached Performance**: Flow results stored in database for fast retrieval
- **Data Quality Assessment**: Cross-validation between catalog and discovered dependencies

## Components

### 1. FlowAnalyzer (`flow_analyzer.py`)
Main analyzer for program execution flows with **program-level granularity**.

**Program-Level Enhancements:**
- Operates on individual program names rather than file names
- Supports multi-program files (RPG, Assembler, Natural, REXX)
- Maintains accurate program-to-program call relationships
- Includes file location metadata for program-to-file mapping
- Handles program boundaries within single source files

**Key Features:**
- Analyze program flows starting from any program
- Recursive dependency traversal with configurable max depth
- Calculate flow depth for programs
- Identify entry points and leaf programs
- Get program statistics

**Usage:**
```python
from legacy_analyzer.analysis import FlowAnalyzer
from legacy_analyzer.models.dependency import Dependency

# Create analyzer with program-level dependencies
analyzer = FlowAnalyzer(dependencies)

# Analyze flow from a starting program (program name, not file name)
flow = analyzer.analyze_flow('PAYROLL1', max_depth=10)

# Get entry points (programs never called by other programs)
entry_points = analyzer.get_entry_points()

# Analyze all entry points with program-level granularity
flows = analyzer.analyze_all_entry_points()

# Program-level flow analysis maintains file location metadata
for program in flow.programs:
    print(f"Program: {program.name}, File: {program.file_path}")
```

### 2. CallGraphBuilder (`call_graph.py`)
Builds call graphs from dependency data with **program-level visualization**.

**Program-Level Enhancements:**
- Creates nodes for individual programs rather than files
- Connects specific programs with accurate call relationships
- Includes file location information for each program node
- Represents all programs from multi-program files as separate entities
- Provides program-to-file mapping information for traceability

**Key Features:**
- Build call graphs for specific programs
- Build complete system call graph
- Get callers and callees for any program
- Identify entry points and leaf programs
- Add metadata to graph nodes

**Usage:**
```python
from legacy_analyzer.analysis import CallGraphBuilder

builder = CallGraphBuilder(dependencies)

# Build graph for specific programs (program names, not file names)
graph = builder.build_call_graph(['PAYROLL_MAIN', 'PAYROLL_CALC'])

# Build complete program-level call graph
full_graph = builder.build_full_call_graph()

# Get callers/callees at program level
callers = builder.get_callers('PAYROLL_MAIN')
callees = builder.get_callees('PAYROLL_MAIN')

# Program nodes include file location metadata
for node in graph.nodes():
    program_info = graph.nodes[node]
    print(f"Program: {node}, File: {program_info.get('file_path', 'Unknown')}")
```

### 3. CircularDependencyDetector (`circular_detector.py`)
Detects circular dependencies using DFS algorithm with **program-level detection**.

**Program-Level Enhancements:**
- Detects cycles at the program level within and across files
- Reports program-level cycle information with file location details
- Handles circular dependencies between programs in the same file
- Provides accurate program-level circular dependency validation
- Maintains program-to-file mapping in cycle reports

**Key Features:**
- Detect all circular dependencies in the system
- Check if specific program is in a cycle
- Get all cycles involving a program
- Detect cycles from a starting program

**Usage:**
```python
from legacy_analyzer.analysis import CircularDependencyDetector

detector = CircularDependencyDetector(dependencies)

# Detect all program-level cycles
cycles = detector.detect_all_cycles()

# Check if specific program is in a cycle
has_cycle = detector.has_cycle_involving('PAYROLL_MAIN')

# Get cycles involving a program (with file location info)
prog_cycles = detector.get_cycles_involving('PAYROLL_MAIN')

# Program-level cycle reporting includes file locations
for cycle in cycles:
    print(f"Cycle: {' -> '.join(cycle.programs)}")
    for program in cycle.programs:
        print(f"  {program}: {cycle.get_file_location(program)}")
```

### 4. ProgramBoundaryDetector (`program_boundary_detector.py`)
Framework for detecting program boundaries within multi-program files.

**Key Features:**
- Language-agnostic interface for program boundary detection
- Language-specific boundary detection patterns (RPG, Assembler, Natural, REXX)
- Returns start and end line numbers for each program
- Validates program boundary completeness and non-overlap
- Supports program type classification (MAIN, PROCEDURE, CSECT, SUBPROGRAM)

**Usage:**
```python
from legacy_analyzer.analysis import ProgramBoundaryDetector

detector = ProgramBoundaryDetector()

# Detect program boundaries in source code
boundaries = detector.detect_boundaries(source_code, language='RPG')

# Each boundary includes program metadata
for boundary in boundaries:
    print(f"Program: {boundary.program_name}")
    print(f"  Lines: {boundary.start_line}-{boundary.end_line}")
    print(f"  Type: {boundary.program_type}")
    print(f"  Language: {boundary.language}")
    print(f"  Entry Points: {boundary.entry_points}")

# Validate boundary completeness
is_complete = detector.validate_completeness(boundaries, total_lines)
```

**Supported Languages:**
- **RPG**: H-spec, F-spec, and procedure definitions
- **Assembler**: CSECT boundaries and ENTRY points
- **Natural**: DEFINE DATA PROGRAM/SUBPROGRAM boundaries
- **REXX**: Procedure definitions and boundaries

### 5. CopybookAnalyzer (`copybook_analyzer.py`)
Framework for analyzing copybook content to distinguish executable code from data structures.

**Key Features:**
- Executable code detection within copybooks and includes
- Content analysis with confidence scoring
- Distinguishes executable code from data structures
- Tracks dependencies found within included content
- Supports COBOL COPY, PL/I INCLUDE, and Natural USING statements

**Usage:**
```python
from legacy_analyzer.analysis import CopybookAnalyzer

analyzer = CopybookAnalyzer()

# Analyze copybook content
result = analyzer.analyze_content('path/to/copybook.cpy', language='COBOL')

# Check if copybook contains executable code
if result.has_executable_code:
    print(f"Executable copybook with confidence: {result.confidence_level}")
    print(f"Procedure calls found: {result.procedure_calls}")
    print(f"Program dependencies: {result.program_dependencies}")
else:
    print(f"Data structure copybook")
    print(f"Data structures: {result.data_structures}")

# Handle nested includes and circular references
nested_results = analyzer.analyze_with_includes('main_program.cbl')
```

**Analysis Results:**
- `has_executable_code`: Boolean indicating if copybook contains executable logic
- `confidence_level`: Float (0.0-1.0) indicating analysis confidence
- `data_structures`: List of data structure definitions found
- `procedure_calls`: List of procedure calls found in executable copybooks
- `program_dependencies`: List of dependencies found within the copybook

### 6. FlowVisualizer (`flow_visualizer.py`)
Export flows in various visualization formats.

**Key Features:**
- Export to DOT format (Graphviz)
- Export to Mermaid diagram format
- Export to JSON for programmatic use
- Include/exclude copybooks and datasets
- Highlight circular dependencies

**Usage:**
```python
from legacy_analyzer.analysis import FlowVisualizer

visualizer = FlowVisualizer(flow, dependencies)

# Export to DOT format
dot = visualizer.to_dot(include_copybooks=True, include_datasets=True)

# Export to Mermaid
mermaid = visualizer.to_mermaid()

# Export to JSON
json_str = visualizer.to_json()
```

### 7. FlowDatabase (`flow_database.py`)
Database operations for persisting flow analysis results.

**Key Features:**
- Create database schema for flows
- Save and load program flows
- Query flows by various criteria
- Get flow statistics

**Usage:**
```python
from legacy_analyzer.analysis import FlowDatabase
import sqlite3

conn = sqlite3.connect('analyzer.db')
flow_db = FlowDatabase(conn)

# Create schema
flow_db.create_schema()

# Save flow
flow_id = flow_db.save_flow(flow)

# Load flow
loaded_flow = flow_db.load_flow('PROG1')

# Get statistics
stats = flow_db.get_flow_statistics()
```

## Database Schema

### program_flows
Stores program flow metadata.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| start_program | VARCHAR(44) | Starting program name |
| depth | INTEGER | Maximum depth of flow |
| total_programs | INTEGER | Total programs in flow |
| total_copybooks | INTEGER | Total copybooks referenced |
| total_datasets | INTEGER | Total datasets referenced |
| has_circular_deps | BOOLEAN | Whether flow has circular dependencies |
| analyzed_date | TIMESTAMP | When flow was analyzed |

### flow_programs
Stores programs in each flow.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| flow_id | INTEGER | Foreign key to program_flows |
| program_name | VARCHAR(44) | Program name |
| depth_level | INTEGER | Depth level in flow |

### flow_circular_deps
Stores circular dependencies found in flows.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| flow_id | INTEGER | Foreign key to program_flows |
| cycle_artifacts | TEXT | Comma-separated artifact names |
| cycle_dep_types | TEXT | Comma-separated dependency types |



### Enhanced Schema for Program-Level Tracking

#### program_file_mapping
Maps programs to their containing files with positional information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| file_path | TEXT | Path to source file |
| program_name | VARCHAR(44) | Program name within file |
| program_index | INTEGER | Program index within file |
| start_line | INTEGER | Starting line number |
| end_line | INTEGER | Ending line number |
| program_type | VARCHAR(20) | Program type (MAIN, PROCEDURE, CSECT, etc.) |
| language | VARCHAR(20) | Programming language |
| entry_points | TEXT | JSON array of entry point names |

#### copybook_analysis
Stores copybook analysis results for executable code detection.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| copybook_name | VARCHAR(44) | Copybook name |
| file_path | TEXT | Path to copybook file |
| has_executable_code | BOOLEAN | Whether copybook contains executable code |
| confidence_level | DECIMAL(3,2) | Analysis confidence (0.00-1.00) |
| data_structures | TEXT | JSON array of data structure names |
| procedure_calls | TEXT | JSON array of procedure calls found |
| analyzed_at | TIMESTAMP | Analysis timestamp |

#### Enhanced inventory table
Additional columns for program-level tracking.

| Column | Type | Description |
|--------|------|-------------|
| program_within_file | VARCHAR(44) | Program name within multi-program files |
| file_program_index | INTEGER | Program index within file |
| program_start_line | INTEGER | Starting line number of program |
| program_end_line | INTEGER | Ending line number of program |
| program_type | VARCHAR(20) | Program type classification |


## Requirements Satisfied

This implementation satisfies the following requirements from the design document:

- **Requirement 4.1**: Identify all programs called directly by a starting program
- **Requirement 4.2**: Recursively identify all programs called transitively
- **Requirement 4.3**: Detect circular dependencies and report them
- **Requirement 4.4**: Calculate depth of each program in call hierarchy
- **Requirement 4.5**: Generate call graph showing program-to-program relationships
- **Requirement 4.6**: Export program flows in DOT/Graphviz format
- **Requirement 4.7**: Export program flows in Mermaid format
- **Requirement 4.8**: Include copybook and dataset dependencies in visualization

## Testing

Comprehensive unit tests are provided in `tests/test_flow_analysis.py`:

- 36 test cases covering all components
- Tests for simple flows, complex flows, and circular dependencies
- Tests for all visualization formats
- Tests for database operations
- All tests passing ✓

Run tests with:
```bash
python3 -m pytest tests/test_flow_analysis.py -v
```
