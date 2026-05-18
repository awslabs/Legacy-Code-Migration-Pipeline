# Migration Workpackage Planner

The Migration Workpackage Planner is a Python CLI tool that automates the generation of migration workpackage plans from business flow analysis data. It transforms complex flow dependencies and complexity metrics into actionable migration plans with priority-based sequencing and phase assignments.

## Overview

The planner reads business flow analysis data, calculates priority scores based on complexity metrics, assigns sequential workpackage IDs, determines migration phases through dependency analysis, and generates comprehensive planning outputs in both JSON and Markdown formats.

**Key Features:**
- **Priority Calculation**: Weighted formula considering program count, common modules, complexity, and flow characteristics
- **Workpackage Assignment**: Sequential ID assignment with pre-existent module tracking
- **Phase Determination**: Topological sorting of dependencies with cycle detection
- **Pod Partitioning**: Cluster workpackages into pods for parallel execution across git worktrees
- **Comprehensive Output**: JSON planning data, status tracking, and human-readable roadmap
- **Validation**: Input validation, dependency validation, and circular dependency detection
- **CLI Interface**: Full command-line interface with configurable options
- **Python API**: Programmatic access for integration with other tools

## Documentation

- **[Usage Guide](docs/USAGE_GUIDE.md)** - Detailed usage instructions and workflows
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Pod Partitioning Guide](docs/POD_PARTITIONING.md)** - Pod partitioning for parallel migration execution
- **[Examples](examples/)** - Example input files and usage patterns

## Installation


```bash
# Install the toolkit
pip install -e .

# Or install just the migration planner dependencies
pip install -r tools/migration_planner/requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Run with default paths
python -m tools.migration_planner

# Specify custom flows file
python -m tools.migration_planner --flows-file ./data/Business_Flows.json

# Include module classifications for better priority calculation
python -m tools.migration_planner \
    --flows-file ./data/Business_Flows.json \
    --classifications-file ./data/Module_Classifications.json

# Custom output directory and project name
python -m tools.migration_planner \
    --flows-file ./data/Business_Flows.json \
    --output-base ./output/migration \
    --project-name my-project

# Enable debug logging
python -m tools.migration_planner --log-level DEBUG
```

### Python API

```python
from tools.migration_planner import MigrationPlanner, PlannerConfig
from pathlib import Path

# Configure the planner
config = PlannerConfig(
    flows_file=Path("./results/carddemo_analysis/flows/Business_Flows.json"),
    output_base=Path("./results/migration/"),
    project_name="carddemo",
    classifications_file=Path("./data/Module_Classifications.json"),  # Optional
    log_level="INFO"
)

# Run the planning pipeline
planner = MigrationPlanner(config)
result = planner.run()

if result.success:
    print(f"Planning completed successfully!")
    print(f"Generated files: {result.output_files}")
else:
    print(f"Planning failed: {result.error_message}")
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--flows-file` | Path to Business_Flows.json | `./results/carddemo_analysis/flows/Business_Flows.json` |
| `--classifications-file` | Path to Module_Classifications.json (optional) | None |
| `--output-base` | Output directory base path | `./results/migration/` |
| `--project-name` | Project name for metadata | Extracted from flows file path |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `--version` | Display version and exit | - |
| `--help` | Display help message and exit | - |

## Output Files

The planner generates three output files in the specified output directory:

1. **Workpackage_Planning.json** - Complete planning data with metadata, priorities, phases, and migration sequence (root directory)
2. **progress/Workpackage_Status.json** - Initial status tracking for all workpackages with overall planning status (progress subfolder)
3. **reports/Workpackage_Definition_Roadmap.md** - Human-readable migration roadmap with planning status (reports subfolder)

### Output Directory Structure

```
output_base/
├── Workpackage_Planning.json
├── progress/
│   └── Workpackage_Status.json      # Includes "status": "completed" field
└── reports/
    └── Workpackage_Definition_Roadmap.md  # Includes **Status:** completed line
```

**Note:** Both `Workpackage_Status.json` and `Workpackage_Definition_Roadmap.md` include a `status` field set to "completed" when the planning process finishes successfully.

## Priority Calculation

The priority score determines migration order (lower score = higher priority).

**Formula:**
```
priority = (totalPrograms × 2) + (commonModules × 3) + (compositeScore × 0.5) 
           + completeFlowBonus + simpleFlowBonus
```

**Factors:**
- `totalPrograms`: Number of programs in the flow (weight: 2)
- `commonModules`: Count of commonly-used modules (weight: 3)
- `compositeScore`: Complexity metric from analysis (weight: 0.5)
- `completeFlowBonus`: -5 if flow has database operations, 0 otherwise
- `simpleFlowBonus`: -3 if ≤3 programs, -1 if ≤5 programs, 0 otherwise

## Architecture

The planner follows a pipeline architecture with distinct stages:

```
Input → Priority → Workpackage → Phase → Output
```

**Modules:**
1. **Input Module** (`input/`): File reading, JSON parsing, validation
2. **Priority Module** (`priority/`): Priority score calculation with factor breakdown
3. **Workpackage Module** (`workpackage/`): Sequential ID assignment and pre-existent module tracking
4. **Phase Module** (`phase/`): Dependency analysis, phase assignment, DAG validation
5. **Pod Module** (`pod/`): Pod partitioning for parallel execution across git worktrees
6. **Output Module** (`output/`): JSON and Markdown generation
7. **CLI Module** (`cli.py`): Command-line interface and argument parsing
8. **Orchestrator** (`planner.py`): Pipeline coordination and error handling

## Testing

The planner includes comprehensive test coverage:

```bash
# Run all tests
pytest tests/

# Run unit tests
pytest tests/unit/test_migration_planner/

# Run property-based tests
pytest tests/property/ -k "migration"

# Run with coverage
pytest --cov=tools.migration_planner tests/
```

## Pod Partitioning

After workpackage planning, partition workpackages into pods for parallel execution in separate git worktrees. Each pod can independently proceed through migration phases 3→6.

### Quick Start

```bash
# Run pod partitioner after workpackage planning
python -m tools.migration_planner.pod.cli \
    --workpackage-planning ./results/migration/Workpackage_Planning.json \
    --business-flows ./results/flows/Business_Flows.json \
    --output ./output/analysis/workpackages/Pod_Assignment.json
```

### Python API

```python
from tools.migration_planner.pod import PodPartitioner

partitioner = PodPartitioner(
    workpackage_planning_path="./results/migration/Workpackage_Planning.json",
    business_flows_path="./results/flows/Business_Flows.json",
)
result = partitioner.run()
partitioner.write_output(result, "./output/Pod_Assignment.json")

# Check quality
report = result.validate()
print(f"Passed: {report['passed']}")
```

For full details, see the [Pod Partitioning Guide](docs/POD_PARTITIONING.md).

## Integration


### With Legacy Analyzer

```bash
# 1. Run legacy analyzer to generate flow analysis
python -m tools.legacy_analyzer analyze \
    --source-dir ./code \
    --db analyzer.db

# 2. Export flows to JSON
python -m tools.legacy_analyzer export-flows \
    --db analyzer.db \
    --output Business_Flows.json

# 3. Run migration planner
python -m tools.migration_planner \
    --flows-file Business_Flows.json
```


```bash
    --query program_usage \
    --output program_usage.json

# 2. Use program usage data to create classifications
python scripts/create_classifications.py \
    --usage program_usage.json \
    --output Module_Classifications.json

# 3. Run migration planner with classifications
python -m tools.migration_planner \
    --flows-file Business_Flows.json \
    --classifications-file Module_Classifications.json
```

## Error Handling

The planner provides clear error messages with context and suggestions.

**Exit Codes:**
- `0`: Success
- `1`: Input validation error (missing required fields, invalid JSON)
- `2`: File system error (cannot read/write files)
- `3`: Dependency validation error (circular dependencies, missing references)
- `4`: Configuration error (invalid arguments)

## Contributing

Contributions are welcome! Please follow the project's coding standards:

- **Code Style**: Black formatter (line length: 100)
- **Type Hints**: Use type hints for all function signatures
- **Documentation**: Docstrings for all public functions and classes
- **Testing**: Unit tests and property-based tests for new features

## License


## Support

For issues, questions, or contributions:
1. Check the [Usage Guide](docs/USAGE_GUIDE.md)
2. Review the [API Reference](docs/API_REFERENCE.md)
3. See the [examples directory](examples/)
4. Check the [main toolkit documentation](../../README.md)
5. Submit issues or pull requests on the project repository
