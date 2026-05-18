# Migration Planner Scripts

This directory contains helper scripts for running the Migration Workpackage Planner.

## run_migration_planner.sh

A convenient shell script for running the migration planner with configurable options.

### Usage

```bash
./scripts/run_migration_planner.sh <flows_file> <output_dir> [classifications_file] [project_name] [log_level]
```

### Arguments

| Position | Parameter | Required | Description | Default |
|----------|----------|----------|-------------|---------|
|1| `flows_file` | Yes | Path to Business_Flows.json | - |
|2| `output_dir` | Yes | Output directory for planning files | - |
|3| `classifications_file` | No | Path to Module_Classifications.json | None |
|4| `project_name` | No | Project name for metadata | Auto-detected from path |
|5| `log_level` | No | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

### Examples

#### Basic Usage

```bash
# Run with minimal arguments
./scripts/run_migration_planner.sh \
    ./results/carddemo_analysis/flows/Business_Flows.json \
    ./results/carddemo_analysis/migration
```

#### With Project Name

```bash
# Specify project name
./scripts/run_migration_planner.sh \
    ./results/carddemo_analysis/flows/Business_Flows.json \
    ./results/carddemo_analysis/migration \
    "" \
    carddemo
```

#### With Classifications

```bash
# Include module classifications
./scripts/run_migration_planner.sh \
    ./data/flows.json \
    ./output \
    ./data/Module_Classifications.json \
    my-project
```

#### With Debug Logging

```bash
# Enable debug logging
./scripts/run_migration_planner.sh \
    ./data/flows.json \
    ./output \
    "" \
    my-project \
    DEBUG
```

### Output

The script generates three files in the output directory:

1. **Workpackage_Planning.json** - Complete planning data with metadata, priorities, phases, and migration sequence (root directory)
2. **progress/Workpackage_Status.json** - Initial status tracking for all workpackages with overall planning status (progress subfolder)
3. **reports/Workpackage_Definition_Roadmap.md** - Human-readable migration roadmap with planning status (reports subfolder)

### Output Directory Structure

```
output_dir/
├── Workpackage_Planning.json
├── progress/
│   └── Workpackage_Status.json      # Includes "status": "completed" field
└── reports/
    └── Workpackage_Definition_Roadmap.md  # Includes **Status:** completed line
```

**Note:** Both `Workpackage_Status.json` and `Workpackage_Definition_Roadmap.md` include a `status` field set to "completed" when the planning process finishes successfully.

### Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Planning completed successfully |
| 1 | Input validation error | Missing required fields, invalid JSON |
| 2 | File system error | Cannot read/write files, permission denied |
| 3 | Dependency validation error | Circular dependencies, missing flow references |
| 4 | Configuration error | Invalid command-line arguments |

### Features

- **Colored output** for better readability
- **Input validation** before running the planner
- **Automatic statistics display** from generated planning file
- **File size reporting** for generated outputs
- **Helpful error messages** with suggestions for common issues
- **Next steps guidance** after successful completion

### Troubleshooting

#### Script not executable

```bash
chmod +x scripts/run_migration_planner.sh
```

#### Python not found

The script uses `python3`. Ensure Python 3.8+ is installed:

```bash
python3 --version
```

#### Flows file not found

Verify the file path:

```bash
ls -la ./results/carddemo_analysis/flows/Business_Flows.json
```

#### Permission denied

Check directory permissions:

```bash
ls -ld ./results/carddemo_analysis/migration
```

## Direct Python Usage

You can also run the planner directly with Python:

```bash
# Basic usage
python3 -m tools.migration_planner \
    --flows-file ./results/carddemo_analysis/flows/Business_Flows.json \
    --output-base ./results/carddemo_analysis/migration

# With all options
python3 -m tools.migration_planner \
    --flows-file ./data/flows.json \
    --classifications-file ./data/classifications.json \
    --output-base ./output \
    --project-name my-project \
    --log-level DEBUG
```

## Integration Examples

### With Legacy Analyzer

```bash
# 1. Run legacy analyzer
python3 -m tools.legacy_analyzer analyze \
    --source-dir ./cobol-code \
    --db analyzer.db

# 2. Export flows
python3 -m tools.legacy_analyzer export-flows \
    --db analyzer.db \
    --output Business_Flows.json

# 3. Run migration planner
./scripts/run_migration_planner.sh \
    Business_Flows.json \
    ./migration-plan
```

### Batch Processing

```bash
#!/bin/bash
# Process multiple projects

for project in project1 project2 project3; do
    echo "Processing $project..."
    ./scripts/run_migration_planner.sh \
        "./data/${project}/Business_Flows.json" \
        "./output/${project}" \
        "" \
        "$project"
done
```

## See Also

- [Migration Planner README](../tools/migration_planner/README.md)
- [Usage Guide](../tools/migration_planner/docs/USAGE_GUIDE.md)
- [API Reference](../tools/migration_planner/docs/API_REFERENCE.md)
