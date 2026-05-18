# Legacy Analyzer


## Overview

The Legacy Analyzer specializes in:
- **Multi-language source code analysis** (COBOL, PL/I, JCL, REXX, Natural, RPG, Assembler)
- **Dependency extraction and tracking** across different programming languages
- **Complexity analysis** with metrics like LOC, cyclomatic complexity, and dependency counts
- **Flow analysis** including entry point detection, call graphs, and circular dependency detection
- **CICS metadata integration** for accurate entry point identification
- **Migration planning** with package creation and modernization recommendations
- **Comprehensive reporting** in multiple formats (JSON, markdown)

## Quick Start

### Installation

```bash
# Install from project root
pip install -e .
```

### Basic Usage

```bash
# Complete analysis (recommended)
python -m tools.legacy_analyzer analyze \
  --source-dir ./mainframe-code \
  --db analysis.db

# Check what was discovered
python -m tools.legacy_analyzer status --db analysis.db

# Generate summary report
python -m tools.legacy_analyzer report summary \
  --db analysis.db \
  --output reports/analysis_summary.md

# Build migration flows
python -m tools.legacy_analyzer.api build-flows --db analysis.db

# Export flows for migration planning
python -m tools.legacy_analyzer.api export-flows \
  --db analysis.db \
  --output flows.json
```

### Python API

```python
from tools.legacy_analyzer.api import LegacyAnalyzerAPI

# Initialize API
with LegacyAnalyzerAPI("analysis.db") as api:
    # Build migration flows
    flow_ids = api.build_migration_flows()
    
    # Export flows
    result = api.export_migration_flows("flows.json")
    
    print(f"Exported {len(result['flows'])} flows")
```

## Key Features

### Complete Database Coverage (9/9 Tables)
- ✅ **inventory** - Main source code artifacts
- ✅ **inventory_cics** - CICS resources from CSD files
- ✅ **inventory_jcl** - JCL jobs
- ✅ **inventory_programs** - Program metadata
- ✅ **inventory_copybooks** - Copybook metadata
- ✅ **inventory_datasets** - VSAM datasets
- ✅ **artifact_dependencies** - Cross-artifact dependencies
- ✅ **program_file_mapping** - Program boundaries
- ✅ **copybook_analysis** - Executable code detection

### Advanced Analysis Features
- ✅ Program-level analysis with multi-program file boundary detection
- ✅ Copybook analysis for executable vs data-only classification
- ✅ VSAM dataset extraction from CSD files
- ✅ Integrated CSD parser with automatic discovery
- ✅ Multiple analysis modes (complete, inventory-only, dependencies-only)
- ✅ Enhanced CLI with specialized commands
- ✅ Cross-language dependency extraction and validation
- ✅ Entry point detection (JCL, CICS, inferred)
- ✅ Call graph generation and circular dependency detection
- ✅ Missing artifact detection
- ✅ Multi-format report generation

### Migration Planning Features
- Complete asset inventory of all mainframe components
- Dependency mapping with cross-language analysis
- Complexity assessment for effort estimation
- Data architecture analysis (VSAM relationships and access patterns)
- Risk assessment (missing artifacts, circular dependencies)
- Migration flow export with multiple sorting strategies
- JCL job export with orchestration and categorization

## Supported Languages

| Language | Extensions | Features |
|----------|-----------|----------|
| COBOL | .cbl, .cob, .cpy | Programs, copybooks, CICS calls |
| PL/I | .pli, .pl1, .inc | Programs, includes, CICS calls |
| JCL | .jcl | Job control, EXEC statements |
| REXX | .rexx, .rex | Scripts, procedures |
| Natural | .nsp, .nsn, .nsc, .nsa, .nsl, .nsg, .nsd, .ns8 | Programs, subprograms, data areas, functions, copycode |
| RPG | .rpg, .rpgle | Programs, procedures |
| Assembler | .asm, .s, .mac | Programs, macros, CSECT |

## Documentation

### Getting Started
- **[User Guide](docs/USER_GUIDE.md)** - Complete end-user documentation
- **[CLI Reference](docs/CLI_REFERENCE.md)** - Command-line interface reference
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Migration planning and execution

### Developer Resources
- **[API Reference](docs/API.md)** - Python API documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[Development Guide](docs/DEVELOPMENT.md)** - Developer setup and guidelines
- **[Contributing](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[Parsers](docs/PARSERS.md)** - Parser documentation and development

### Advanced Topics
- **[CICS Integration](docs/advanced/CICS_INTEGRATION.md)** - CICS metadata integration
- **[Complexity Analysis](docs/advanced/COMPLEXITY_ANALYSIS.md)** - Complexity metrics and scoring
- **[Flow Analysis](docs/advanced/FLOW_ANALYSIS.md)** - Flow analysis algorithms
- **[Service Grouping](docs/advanced/SERVICE_GROUPING.md)** - Service grouping methodology
- **[Error Handling](docs/advanced/ERROR_HANDLING.md)** - Error handling patterns

### Reference
- **[Query Reference](docs/QUERY_REFERENCE.md)** - Query catalog and reference
- **[Changelog](docs/CHANGELOG.md)** - Version history and changes

## Common Workflows

### Output Structure

The legacy_analyzer produces the following output structure:

```
results/{project}_analysis/
├── {project}.db              # SQLite database with all analysis data
├── entry_points/             # Entry point analysis
│   ├── entry_points.json     # Entry points in JSON format
│   └── entry_points.md       # Entry points in markdown format
├── flows/                    # Migration flow exports
│   ├── Business_Flows.json
│   ├── flows_by_complexity_asc.json
│   ├── flows_by_complexity_desc.json
│   ├── flows_by_dependencies.json
│   ├── flows_by_independence.json
│   ├── flows_by_name.json
│   └── flows_database_order.json
├── jobs/                     # JCL job exports
│   ├── jobs.json
│   ├── jobs_by_complexity.json
│   ├── jobs_by_dependencies.json
│   ├── jobs_by_name.json
│   └── jobs_by_type.json
├── progress/                 # Status tracking
│   └── source_analysis_status.json  # Analysis completion status
└── reports/                  # Analysis reports
    └── analysis_summary.md   # Executive summary (generated by report summary command)
```

**Note:** All reports are generated in markdown format (.md). The `exports/` and `temp/` folders are no longer created.

**Report Generation:** The reports are generated using CLI commands:
```bash
# Generate summary report
python -m tools.legacy_analyzer report summary --db {project}.db --output reports/analysis_summary.md

# Generate status report
python -m tools.legacy_analyzer report status --db {project}.db --output-dir results/{project}_analysis
```

### Complete Analysis Pipeline

```bash
# 1. Analyze source code
python -m tools.legacy_analyzer analyze \
  --source-dir ./mainframe-code \
  --db analysis.db \
  --complexity

# 2. Check status
python -m tools.legacy_analyzer status --db analysis.db

# 3. Generate summary report
python -m tools.legacy_analyzer report summary \
  --db analysis.db \
  --output reports/analysis_summary.md

# 4. Generate executive reports (markdown format is default)
python -m tools.legacy_analyzer report executive \
  --db analysis.db \
  --format markdown \
  --output reports/executive_summary.md
```

### Report Generation

```bash
# Generate summary report with default output location
python -m tools.legacy_analyzer report summary --db analysis.db

# Generate summary report with custom output path
python -m tools.legacy_analyzer report summary \
  --db analysis.db \
  --output custom/path/summary.md

# Use in bash scripts
DATABASE="analysis.db"
OUTPUT_DIR="results/carddemo_analysis"
python -m tools.legacy_analyzer report summary \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/reports/analysis_summary.md"
```

### Migration Flow Export

```bash
# Export flows sorted by complexity (simplest first)
python -m tools.legacy_analyzer.api export-flows \
  --db analysis.db \
  --output flows_by_complexity.json \
  --sort-strategy complexity-asc

# Export flows sorted by independence (parallel migration)
python -m tools.legacy_analyzer.api export-flows \
  --db analysis.db \
  --output flows_by_independence.json \
  --sort-strategy independence
```

### CICS Metadata Integration

```bash
# 1. Convert CSD to CSV
python -m tools.legacy_analyzer metadata convert-csd \
  --input app/csd/CARDDEMO.csd \
  --output exports/cics_inventory.csv

# 2. Load CICS inventory
python -m tools.legacy_analyzer load \
  --type cics \
  --file exports/cics_inventory.csv \
  --db analysis.db

# 3. Generate entry points report with metadata (markdown is default)
python -m tools.legacy_analyzer flow entry-points \
  --db analysis.db \
  --use-metadata \
  --format markdown \
  --output entry_points/entry_points.md

# Or generate in JSON format
python -m tools.legacy_analyzer flow entry-points \
  --db analysis.db \
  --use-metadata \
  --format json \
  --output entry_points/entry_points.json
```

## Project Structure

```
tools/legacy_analyzer/
├── README.md                      # This file
├── __init__.py                    # Module initialization
├── __main__.py                    # CLI entry point
├── cli.py                         # Command-line interface
├── api.py                         # High-level Python API
├── analysis_orchestrator.py      # Analysis workflow orchestrator
├── docs/                          # Documentation
│   ├── API.md                     # API reference
│   ├── ARCHITECTURE.md            # Architecture documentation
│   ├── USER_GUIDE.md              # User guide
│   ├── CLI_REFERENCE.md           # CLI reference
│   ├── MIGRATION_GUIDE.md         # Migration guide
│   ├── PARSERS.md                 # Parser documentation
│   ├── DEVELOPMENT.md             # Development guide
│   ├── CONTRIBUTING.md            # Contribution guidelines
│   ├── QUERY_REFERENCE.md         # Query reference
│   ├── CHANGELOG.md               # Version history
│   └── advanced/                  # Advanced topics
│       ├── CICS_INTEGRATION.md
│       ├── COMPLEXITY_ANALYSIS.md
│       ├── FLOW_ANALYSIS.md
│       ├── SERVICE_GROUPING.md
│       └── ERROR_HANDLING.md
├── parsers/                       # Language-specific parsers
│   ├── cobol_parser.py
│   ├── pli_parser.py
│   ├── jcl_parser.py
│   ├── rexx_parser.py
│   ├── natural_parser.py
│   ├── rpg_parser.py
│   └── asm_parser.py
├── analysis/                      # Analysis engines
│   ├── flow_analyzer.py
│   ├── complexity_analyzer.py
│   └── missing_code_detector.py
├── migration/                     # Migration planning
│   ├── flow_builder.py
│   ├── flow_exporter.py
│   ├── package_builder.py
│   └── job_exporter.py
├── inventory/                     # Inventory management
│   └── inventory_loader.py
├── models/                        # Data models
│   ├── dependency.py
│   ├── complexity.py
│   └── flow.py
└── utils/                         # Utilities
    ├── cache_manager.py
    └── parallel_processor.py
```

## Version Information

**Current Version:** v2.1.0 - Complete Integration with Advanced Analysis

**Recent Updates:**
- Complete database coverage (9/9 tables)
- Program-level analysis with boundary detection
- Copybook analysis for executable code detection
- VSAM dataset extraction from CSD files
- Enhanced CLI commands
- Flexible feature flags
- Enhanced reporting with advanced metrics
- Enhanced Natural language support:
  - Extended file extensions (.NSA, .NSL, .NSG, .NSD, .NS8)
  - Data area files (.NSC, .NSL, .NSG, .NSD) classified as COPYBOOK
  - New dependency types: FETCH_RETURN, PAGE_REF, WEB_SERVICE, WORK_FILE
  - Cross-file VIEW-to-physical-file resolution (e.g., EMPL1 VIEW → EMPLOYEES file)
  - PROCESS PAGE USING, REQUEST DOCUMENT, DEFINE/READ/WRITE WORK FILE detection
  - Complexity metrics for all Natural artifact types
  - Duplicate dependency prevention via UNIQUE constraint on artifact_dependencies
  - Improved dependency validation with cross-type artifact lookup

See [CHANGELOG.md](docs/CHANGELOG.md) for complete version history.

## Requirements

- Python 3.8 or higher
- SQLite (included with Python)
- Dependencies listed in `requirements.txt`

## Installation

```bash
# From project root
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Support

- **Documentation**: See `docs/` directory for comprehensive guides
- **Examples**: Check `examples/` directory for sample scripts
- **Issues**: Report problems on the project repository

## License


## Related Tools


---

**For detailed documentation, see the [docs/](docs/) directory.**
