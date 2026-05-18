# Migration Module

## Overview

The Migration module provides comprehensive export capabilities for planning and executing mainframe-to-cloud migration projects. It includes two complementary export features that together provide a complete view of your mainframe system:

1. **Flow Export** (`export-flows`): Exports program execution flows and business logic
2. **Job Export** (`export-jobs`): Exports JCL job orchestration and infrastructure

## Features

### Flow Export

Export program execution flows with various sorting strategies for migration planning.

**Key Capabilities:**
- Entry point identification (CICS transactions, batch programs)
- Program call chains and dependencies
- Complexity metrics and tier classification
- Extended scope metadata (copybooks, datasets, JCL, CICS resources)
- Multiple sorting strategies (complexity, independence, dependencies, name)

**Use Cases:**
- Application migration planning
- Wave planning based on complexity
- Resource estimation
- Parallel migration identification
- Infrastructure requirements planning

**Documentation:**
- [Flow Export Guide](../../../docs/MIGRATION_FLOW_EXPORT_QUICK_REFERENCE.md)
- [CLI Reference](../../../docs/CLI_REFERENCE.md#export-migration-flows)
- [API Reference](../../../docs/API_REFERENCE.md#export_migration_flows)

### Job Export

Export JCL jobs with orchestration, categorization, and dependencies for infrastructure and batch migration planning.

**Key Capabilities:**
- Job categorization (APPLICATION vs INFRASTRUCTURE)
- Job step extraction and type assignment
- Job-to-flow linking
- Job-to-job dependency extraction
- Dataset references
- Multiple sorting strategies (name, type, dependencies, complexity)

**Use Cases:**
- Infrastructure migration planning
- Batch orchestration planning
- Risk assessment
- Three-phase migration strategy
- Dependency analysis

**Documentation:**
- [Job Export Guide](README_JOB_EXPORT.md)
- [CLI Reference](../../../docs/CLI_REFERENCE.md#export-jcl-jobs)
- [API Reference](../../../docs/API_REFERENCE.md#export_jobs)

## Quick Start

### Command Line

```bash
# Export flows (application logic)
python -m legacy_analyzer migration export-flows \
    --db analyzer.db \
    --output Business_Flows.json \
    --sort complexity-asc \
    --extended-scope

# Export jobs (orchestration)
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --output-dir results/jobs \
    --sort-by type
```

### Python API

```python
from tools.legacy_analyzer.api import LegacyAnalyzerAPI

with LegacyAnalyzerAPI(db_path="analyzer.db") as api:
    # Export flows
    flows = api.export_migration_flows(
        output_file="Business_Flows.json",
        sort_strategy="complexity-asc",
        extended_scope=True
    )
    
    # Export jobs
    jobs = api.export_jobs(
        output_dir="results/jobs",
        sort_by="type"
    )
    
    print(f"Exported {len(flows['flows'])} flows")
    print(f"Exported {len(jobs['jobs'])} jobs")
```

## Dual Export Approach

For complete migration planning, use both exports together:

### Why Dual Export?

- **Flow Export**: Focuses on program execution flows and business logic
  - Entry point programs (CICS transactions, batch programs)
  - Program call chains and dependencies
  - Complexity metrics and shared components
  - Best for: Application migration planning

- **Job Export**: Focuses on JCL job orchestration and infrastructure
  - Job steps and execution sequences
  - Job-to-job dependencies
  - Dataset operations and file management
  - Best for: Batch orchestration and infrastructure migration

**Together, these exports provide a complete view of your mainframe system.**

### Cross-References

Jobs and flows are cross-referenced for coordinated migration:

- **Jobs → Flows**: Jobs link to flows via `linkedFlow` field
- **Flows → Jobs**: Flows link to jobs via `invokedByJobs` field

```bash
# Export both
python -m legacy_analyzer migration export-flows \
    --db analyzer.db \
    --output Business_Flows.json \
    --sort complexity-asc \
    --extended-scope

python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --output-dir results/jobs \
    --sort-by type

# Cross-reference jobs and flows
jq '.jobs[] | select(.linkedFlow != null) | {job: .jobName, flow: .linkedFlow}' \
    results/jobs/jobs_by_type.json

jq '.flows[] | select(.invokedByJobs | length > 0) | {flow: .flowId, jobs: .invokedByJobs}' \
    Business_Flows.json
```

## Three-Phase Migration Strategy

The dual export approach enables a three-phase migration strategy:

### Phase 1: Infrastructure Jobs (Weeks 1-4)

Migrate INFRASTRUCTURE jobs first (no custom code dependencies):

```bash
# Extract infrastructure jobs
jq '.jobs[] | select(.jobType == "INFRASTRUCTURE")' \
    results/jobs/jobs_by_type.json > phase1_infrastructure_jobs.json
```

**Characteristics:**
- No dependencies on application migration
- Can start immediately
- Often replaced with cloud-native equivalents
- Examples: Backups, dataset operations, file transfers

### Phase 2: Application Programs (Weeks 5-20)

Migrate program flows (business logic):

```bash
# Use flow export with complexity-asc sorting
cp Business_Flows.json phase2_application_flows.json
```

**Characteristics:**
- Migrate simplest flows first (complexity-asc)
- Build team confidence with quick wins
- Scale up with proven patterns
- Coordinate with APPLICATION jobs via linkedFlow field

### Phase 3: Batch Orchestration (Weeks 21-24)

Migrate APPLICATION jobs after their linked flows are migrated:

```bash
# Extract application jobs
jq '.jobs[] | select(.jobType == "APPLICATION")' \
    results/jobs/jobs_by_type.json > phase3_orchestration_jobs.json
```

**Characteristics:**
- Implement job scheduling and orchestration in cloud
- Use dependency information to build DAGs
- Replace JCL with cloud-native workflow tools (Airflow, Step Functions, etc.)
- Maintain correct execution order using mustRunAfter/mustRunBefore

## Sorting Strategies

### Flow Sorting Strategies

1. **complexity-asc** (⭐ RECOMMENDED for Pilot/POC)
   - Simplest flows first
   - Quick wins, lower risk
   - Build team confidence

2. **complexity-desc** (High Value)
   - Most complex flows first
   - Tackle technical debt early
   - For experienced teams

3. **independence** (Parallel Migration)
   - Minimal dependencies first
   - Enables parallel work
   - Reduces coordination overhead

4. **dependencies** (Shared Infrastructure)
   - Most dependencies first
   - Migrate shared utilities first
   - Reduces rework

5. **name** (Documentation)
   - Alphabetical order
   - Easy to locate specific flows
   - Consistent references

6. **none** (Baseline)
   - Database order
   - No sorting applied

### Job Sorting Strategies

1. **name** (Default - Documentation)
   - Alphabetical order
   - Easy to locate specific jobs
   - Consistent references

2. **type** (⭐ RECOMMENDED for Three-Phase Migration)
   - APPLICATION jobs first, then INFRASTRUCTURE
   - Clear separation of concerns
   - Enables parallel work streams

3. **dependencies** (Execution Order)
   - Topological sort
   - Maintains correct execution order
   - Identifies critical path

4. **complexity** (Risk Assessment)
   - Most complex jobs first
   - Helps allocate resources
   - Identifies high-risk jobs

## Job Categorization

Jobs are automatically categorized into two types:

### APPLICATION Jobs

**Definition**: Jobs that invoke at least one custom program (COBOL, PL/I, etc.)

**Characteristics:**
- Execute business logic
- Require program migration before job migration
- Linked to program flows when applicable
- Higher migration complexity

**Example**: DALYREJS job that runs CBACT01C program

### INFRASTRUCTURE Jobs

**Definition**: Jobs that only invoke utility programs (IEFBR14, IDCAMS, SORT, etc.)

**Characteristics:**
- Perform infrastructure tasks (dataset operations, backups, etc.)
- Can often be migrated independently
- May be replaced with cloud-native equivalents
- Lower migration complexity

**Example**: BACKUPJB job that runs ADRDSSU utility

## Module Structure

```
tools/legacy_analyzer/migration/
├── README.md                    # This file
├── README_JOB_EXPORT.md        # Detailed job export documentation
├── flow_exporter.py            # Flow export implementation
├── job_exporter.py             # Job export implementation
├── sorting_strategies.py       # Sorting strategy implementations
└── __init__.py                 # Module exports
```

## API Reference

### FlowExporter Class

```python
from tools.legacy_analyzer.migration.flow_exporter import FlowExporter

exporter = FlowExporter(db_path="analyzer.db")
result = exporter.export_flows(
    output_file="Business_Flows.json",
    sort_strategy="complexity-asc",
    extended_scope=True
)
```

See [Flow Export Guide](../../../docs/MIGRATION_FLOW_EXPORT_QUICK_REFERENCE.md) for details.

### JobExporter Class

```python
from tools.legacy_analyzer.migration.job_exporter import JobExporter

exporter = JobExporter(db_path="analyzer.db")
result = exporter.export_jobs(
    output_dir="results/jobs",
    sort_by="type"
)
```

See [Job Export Guide](README_JOB_EXPORT.md) for details.

### High-Level API

```python
from tools.legacy_analyzer.api import LegacyAnalyzerAPI

with LegacyAnalyzerAPI(db_path="analyzer.db") as api:
    # Export flows
    flows = api.export_migration_flows(
        output_file="Business_Flows.json",
        sort_strategy="complexity-asc",
        extended_scope=True
    )
    
    # Export jobs
    jobs = api.export_jobs(
        output_dir="results/jobs",
        sort_by="type"
    )
```

See [API Reference](../../../docs/API_REFERENCE.md) for complete API documentation.

## Examples

### Example 1: Complete Dual Export

```bash
#!/bin/bash
# Complete dual export with all sorting strategies

DB="analyzer.db"
FLOW_DIR="results/flows"
JOB_DIR="results/jobs"

# Create output directories
mkdir -p ${FLOW_DIR} ${JOB_DIR}

# Export flows with all strategies
for strategy in complexity-asc complexity-desc independence dependencies name none; do
    echo "Exporting flows with strategy: ${strategy}"
    python -m legacy_analyzer migration export-flows \
        --db ${DB} \
        --output ${FLOW_DIR}/flows_by_${strategy}.json \
        --sort ${strategy} \
        --extended-scope
done

# Export jobs with all strategies
for strategy in name type dependencies complexity; do
    echo "Exporting jobs with strategy: ${strategy}"
    python -m legacy_analyzer migration export-jobs \
        --db ${DB} \
        --output-dir ${JOB_DIR} \
        --sort-by ${strategy}
done

echo "Dual export complete!"
echo "Flows: ${FLOW_DIR}"
echo "Jobs: ${JOB_DIR}"
```

### Example 2: Three-Phase Migration Plan

```python
import json

# Load exports
with open('results/jobs/jobs_by_type.json') as f:
    jobs_data = json.load(f)

with open('results/flows/flows_by_complexity_asc.json') as f:
    flows_data = json.load(f)

# Phase 1: Infrastructure Jobs
infra_jobs = [j for j in jobs_data['jobs'] if j['jobType'] == 'INFRASTRUCTURE']
print(f"Phase 1: Migrate {len(infra_jobs)} infrastructure jobs")

# Phase 2: Application Flows
print(f"Phase 2: Migrate {len(flows_data['flows'])} program flows")

# Phase 3: Application Jobs (Orchestration)
app_jobs = [j for j in jobs_data['jobs'] if j['jobType'] == 'APPLICATION']
print(f"Phase 3: Migrate {len(app_jobs)} application jobs (orchestration)")

# Verify cross-references
for job in app_jobs:
    if job['linkedFlow']:
        print(f"  Job {job['jobName']} requires flow {job['linkedFlow']}")
```

### Example 3: Cross-Reference Analysis

```python
import json

# Load exports
with open('results/jobs/jobs_by_name.json') as f:
    jobs = json.load(f)['jobs']

with open('results/flows/flows_by_name.json') as f:
    flows = json.load(f)['flows']

# Build cross-reference map
job_to_flow = {j['jobName']: j['linkedFlow'] for j in jobs if j['linkedFlow']}
flow_to_jobs = {}

for flow in flows:
    flow_id = flow['flowId']
    invoking_jobs = flow.get('invokedByJobs', [])
    if invoking_jobs:
        flow_to_jobs[flow_id] = invoking_jobs

# Print cross-references
print("Job → Flow Cross-References:")
for job, flow in sorted(job_to_flow.items()):
    print(f"  {job} → {flow}")

print("\nFlow → Jobs Cross-References:")
for flow, jobs in sorted(flow_to_jobs.items()):
    print(f"  {flow} ← {', '.join(jobs)}")

# Validate cross-references
print("\nValidation:")
for job, flow in job_to_flow.items():
    if flow in flow_to_jobs and job in flow_to_jobs[flow]:
        print(f"  ✓ {job} ↔ {flow} (bidirectional)")
    else:
        print(f"  ✗ {job} → {flow} (missing reverse reference)")
```

## See Also

- [Migration Workflow Guide](../../../docs/MIGRATION_WORKFLOW_GUIDE.md) - Complete migration planning process
- [CLI Reference](../../../docs/CLI_REFERENCE.md) - Command-line interface reference
- [API Reference](../../../docs/API_REFERENCE.md) - Python API documentation
- [Flow Export Guide](../../../docs/MIGRATION_FLOW_EXPORT_QUICK_REFERENCE.md) - Flow export details
- [Job Export Guide](README_JOB_EXPORT.md) - Job export details
