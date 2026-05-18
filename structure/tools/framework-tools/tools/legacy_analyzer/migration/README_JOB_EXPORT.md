# JCL Job Export Feature

## Overview

The JCL Job Export feature provides comprehensive export capabilities for all JCL jobs in the legacy analyzer database. This feature complements the existing flow-level export by focusing on job orchestration, categorization, and dependencies, enabling complete migration planning for mainframe-to-cloud projects.

## Table of Contents

- [Quick Start](#quick-start)
- [Job Categorization](#job-categorization)
- [Sorting Strategies](#sorting-strategies)
- [Output Format](#output-format)
- [Python API](#python-api)
- [Job vs Flow Distinction](#job-vs-flow-distinction)
- [Use Cases](#use-cases)
- [Examples](#examples)

## Quick Start

### Command Line

```bash
# Export jobs with default settings (sorted by name)
python -m legacy_analyzer migration export-jobs --db analyzer.db

# Export jobs sorted by type (APPLICATION first, then INFRASTRUCTURE)
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --output-dir results/jobs \
    --sort-by type

# Export all sorting strategies for comparison
for strategy in name type dependencies complexity; do
    python -m legacy_analyzer migration export-jobs \
        --db analyzer.db \
        --output-dir results/jobs \
        --sort-by ${strategy}
done
```

### Python API

```python
from tools.legacy_analyzer.migration.job_exporter import JobExporter

# Create exporter instance
exporter = JobExporter(db_path="analyzer.db")

# Export jobs with specific sorting
result = exporter.export_jobs(
    output_dir="results/jobs",
    sort_by="type"
)

# Access export data
print(f"Total jobs: {result['summary']['totalJobs']}")
print(f"Application jobs: {result['summary']['applicationJobs']}")
print(f"Infrastructure jobs: {result['summary']['infrastructureJobs']}")

# Iterate through jobs
for job in result['jobs']:
    print(f"{job['jobName']}: {job['jobType']}")
    if job['linkedFlow']:
        print(f"  Linked to flow: {job['linkedFlow']}")
```

## Job Categorization

Jobs are automatically categorized into two types based on the programs they invoke:

### APPLICATION Jobs

**Definition**: Jobs that invoke at least one custom program (COBOL, PL/I, etc.)

**Characteristics**:
- Execute business logic
- Require program migration before job migration
- Linked to program flows when applicable
- Higher migration complexity

**Example**:
```json
{
  "jobName": "DALYREJS",
  "jobType": "APPLICATION",
  "hasCustomCode": true,
  "linkedFlow": "FLOW_CBACT01C",
  "steps": [
    {
      "stepName": "STEP01",
      "program": "IEFBR14",
      "type": "UTILITY",
      "purpose": "Allocate or delete datasets",
      "flowEntry": false
    },
    {
      "stepName": "STEP02",
      "program": "CBACT01C",
      "type": "CUSTOM",
      "purpose": "Execute CBACT01C",
      "flowEntry": true
    }
  ]
}
```

### INFRASTRUCTURE Jobs

**Definition**: Jobs that only invoke utility programs (IEFBR14, IDCAMS, SORT, etc.)

**Characteristics**:
- Perform infrastructure tasks (dataset operations, backups, etc.)
- Can often be migrated independently
- May be replaced with cloud-native equivalents
- Lower migration complexity

**Example**:
```json
{
  "jobName": "BACKUPJB",
  "jobType": "INFRASTRUCTURE",
  "hasCustomCode": false,
  "linkedFlow": null,
  "steps": [
    {
      "stepName": "STEP01",
      "program": "IEFBR14",
      "type": "UTILITY",
      "purpose": "Allocate or delete datasets",
      "flowEntry": false
    },
    {
      "stepName": "STEP02",
      "program": "ADRDSSU",
      "type": "UTILITY",
      "purpose": "Backup or restore datasets",
      "flowEntry": false
    }
  ]
}
```

### Known Utility Programs

The exporter recognizes the following utility programs:

- **IEFBR14**: Allocate or delete datasets
- **IDCAMS**: VSAM dataset operations
- **IEBGENER**: Copy datasets
- **IEBCOPY**: Copy partitioned datasets
- **SORT**: Sort datasets
- **ICETOOL**: Advanced sort operations
- **DFSORT**: IBM sort utility
- **ADRDSSU**: Backup and restore
- **IEBUPDTE**: Update partitioned datasets
- **IEBPTPCH**: Print or punch datasets
- **IEHLIST**: List dataset information
- **IEHINITT**: Initialize tape volumes
- **IEHPROGM**: Maintain system control data

Any program not in this list is considered a custom program.

## Sorting Strategies

The exporter supports four sorting strategies to organize jobs for different migration approaches:

### 1. Name (Default)

**Description**: Alphabetical sorting by job name

**When to use**:
- Creating documentation
- Need predictable ordering
- Easy to locate specific jobs

**Example**:
```bash
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by name
```

**Output**: `jobs_by_name.json`

### 2. Type

**Description**: Groups APPLICATION jobs before INFRASTRUCTURE jobs, then sorts alphabetically within each group

**When to use**:
- Want to separate infrastructure from application migration
- Planning three-phase migration strategy
- Enabling parallel work streams

**Example**:
```bash
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by type
```

**Output**: `jobs_by_type.json`

**Migration Strategy**:
1. Migrate INFRASTRUCTURE jobs first (no dependencies)
2. Migrate APPLICATION jobs after their linked flows
3. Implement orchestration last

### 3. Dependencies

**Description**: Topological sort based on job dependencies (jobs that must run first appear earlier)

**When to use**:
- Need to maintain correct execution order
- Planning batch cycle migration
- Understanding critical path

**Example**:
```bash
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by dependencies
```

**Output**: `jobs_by_dependencies.json`

**Note**: If circular dependencies are detected, the exporter falls back to name sorting for affected jobs and logs a warning.

### 4. Complexity

**Description**: Sorts by number of steps (descending) - most complex jobs first

**When to use**:
- Want to identify high-risk jobs early
- Allocating resources based on complexity
- Risk assessment

**Example**:
```bash
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by complexity
```

**Output**: `jobs_by_complexity.json`

## Output Format

### JSON Structure

```json
{
  "jobs": [
    {
      "jobName": "DALYREJS",
      "jobType": "APPLICATION",
      "hasCustomCode": true,
      "linkedFlow": "FLOW_CBACT01C",
      "steps": [
        {
          "stepName": "STEP01",
          "program": "IEFBR14",
          "type": "UTILITY",
          "purpose": "Allocate or delete datasets",
          "flowEntry": false
        },
        {
          "stepName": "STEP02",
          "program": "CBACT01C",
          "type": "CUSTOM",
          "purpose": "Execute CBACT01C",
          "flowEntry": true
        }
      ],
      "datasets": [
        "ACCTDAT",
        "CUSTDAT",
        "TRANFILE"
      ],
      "dependencies": {
        "mustRunAfter": ["DAILYEXT"],
        "mustRunBefore": ["DAILYRPT"]
      }
    }
  ],
  "summary": {
    "totalJobs": 35,
    "applicationJobs": 28,
    "infrastructureJobs": 7,
    "exportDate": "2026-01-30T12:34:56.789Z",
    "database": "analyzer.db",
    "sortedBy": "name"
  }
}
```

### Field Descriptions

#### Job Fields

- **jobName** (string): JCL job name
- **jobType** (string): "APPLICATION" or "INFRASTRUCTURE"
- **hasCustomCode** (boolean): True if job invokes custom programs
- **linkedFlow** (string | null): Flow name (FLOW_{program}) if job invokes a flow entry point, null otherwise
- **steps** (array): Array of job steps
- **datasets** (array): Array of unique dataset names referenced by the job
- **dependencies** (object): Job-to-job dependencies

#### Step Fields

- **stepName** (string): Step identifier (STEP01, STEP02, etc.)
- **program** (string): Program or utility name
- **type** (string): "CUSTOM" or "UTILITY"
- **purpose** (string): Human-readable description
- **flowEntry** (boolean): True if this step starts a program flow

#### Dependency Fields

- **mustRunAfter** (array): Jobs that must run before this job
- **mustRunBefore** (array): Jobs that must run after this job

#### Summary Fields

- **totalJobs** (number): Total number of jobs exported
- **applicationJobs** (number): Number of APPLICATION jobs
- **infrastructureJobs** (number): Number of INFRASTRUCTURE jobs
- **exportDate** (string): ISO 8601 timestamp of export
- **database** (string): Database path used for export
- **sortedBy** (string): Sorting strategy used

## Python API

### JobExporter Class

```python
class JobExporter:
    """
    Exports JCL jobs with complete orchestration, categorization, and dependencies.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the job exporter with database connection.
        
        Args:
            db_path: Path to SQLite database file
            
        Raises:
            FileNotFoundError: If database file does not exist
            sqlite3.Error: If database connection fails
        """
        pass
    
    def export_jobs(
        self,
        output_dir: str,
        sort_by: str = "name"
    ) -> Dict[str, Any]:
        """
        Export all jobs from database with specified sorting.
        
        Args:
            output_dir: Directory for output JSON file
            sort_by: Sorting strategy (name, type, dependencies, complexity)
            
        Returns:
            Dictionary containing jobs array and summary
            
        Raises:
            ValueError: If sort_by is invalid
            OSError: If output directory is not writable
            sqlite3.Error: If database queries fail
        """
        pass
```

### Example Usage

#### Basic Export

```python
from tools.legacy_analyzer.migration.job_exporter import JobExporter

# Create exporter
exporter = JobExporter(db_path="analyzer.db")

# Export with default settings
result = exporter.export_jobs(output_dir="results/jobs")

print(f"Exported {result['summary']['totalJobs']} jobs")
```

#### Export with Custom Sorting

```python
# Export with type sorting
result = exporter.export_jobs(
    output_dir="results/jobs",
    sort_by="type"
)

# Separate APPLICATION and INFRASTRUCTURE jobs
app_jobs = [j for j in result['jobs'] if j['jobType'] == 'APPLICATION']
infra_jobs = [j for j in result['jobs'] if j['jobType'] == 'INFRASTRUCTURE']

print(f"Application jobs: {len(app_jobs)}")
print(f"Infrastructure jobs: {len(infra_jobs)}")
```

#### Analyze Job Dependencies

```python
# Export with dependency sorting
result = exporter.export_jobs(
    output_dir="results/jobs",
    sort_by="dependencies"
)

# Find jobs with many dependencies
critical_jobs = [
    j for j in result['jobs']
    if len(j['dependencies']['mustRunAfter']) + len(j['dependencies']['mustRunBefore']) > 5
]

for job in critical_jobs:
    print(f"{job['jobName']}: {len(job['dependencies']['mustRunAfter'])} before, "
          f"{len(job['dependencies']['mustRunBefore'])} after")
```

#### Cross-Reference with Flows

```python
# Export jobs
job_result = exporter.export_jobs(output_dir="results/jobs")

# Find jobs linked to specific flow
flow_name = "FLOW_CBACT01C"
linked_jobs = [j for j in job_result['jobs'] if j['linkedFlow'] == flow_name]

print(f"Jobs that invoke {flow_name}:")
for job in linked_jobs:
    print(f"  - {job['jobName']}")
```

## Job vs Flow Distinction

Understanding the difference between jobs and flows is crucial for migration planning:

### Jobs (JCL)

**What**: JCL files that define units of work on the mainframe

**Focus**: Orchestration and execution sequence

**Contains**:
- Job steps (sequence of program executions)
- Dataset allocations and operations
- Job-to-job dependencies
- Execution parameters

**Migration Target**: Cloud-native orchestration tools (Airflow, Step Functions, etc.)

**Example**: DALYREJS job runs CBACT01C program as one of its steps

### Flows (Programs)

**What**: Program execution flows representing business logic

**Focus**: Application logic and program call chains

**Contains**:
- Entry point programs
- Program-to-program calls
- Copybook dependencies
- Complexity metrics

**Migration Target**: Modern programming languages (Java, C#, Python, etc.)

**Example**: FLOW_CBACT01C represents the execution flow starting from CBACT01C program

### Relationship

- **Jobs invoke Flows**: A job step can invoke a program that is a flow entry point
- **Cross-References**: Jobs link to flows via `linkedFlow` field, flows link to jobs via `invokedByJobs` field
- **Coordinated Migration**: Application jobs should be migrated after their linked flows

### Dual Export Approach

For complete migration planning, export both:

```bash
# Export flows
python -m legacy_analyzer migration export-flows \
    --db analyzer.db \
    --output flows.json \
    --sort complexity-asc \
    --extended-scope

# Export jobs
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --output-dir results/jobs \
    --sort-by type
```

This provides:
- **Complete Coverage**: Both application logic (flows) and orchestration (jobs)
- **Clear Dependencies**: Cross-references ensure coordinated migration timing
- **Parallel Work Streams**: Infrastructure and application teams can work independently

## Use Cases

### 1. Infrastructure Migration

**Goal**: Migrate infrastructure jobs independently

**Approach**:
```bash
# Export jobs sorted by type
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by type

# Extract infrastructure jobs
jq '.jobs[] | select(.jobType == "INFRASTRUCTURE")' \
    results/jobs/jobs_by_type.json > infrastructure_jobs.json
```

**Benefits**:
- No dependencies on application migration
- Can start immediately
- Often replaced with cloud-native equivalents

### 2. Batch Orchestration Planning

**Goal**: Understand job execution order and dependencies

**Approach**:
```bash
# Export jobs sorted by dependencies
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by dependencies

# Build dependency graph
jq '.jobs[] | {job: .jobName, after: .dependencies.mustRunAfter, before: .dependencies.mustRunBefore}' \
    results/jobs/jobs_by_dependencies.json > job_dependency_graph.json
```

**Benefits**:
- Maintains correct execution order
- Identifies critical path
- Enables DAG construction for cloud orchestration

### 3. Risk Assessment

**Goal**: Identify high-risk jobs early

**Approach**:
```bash
# Export jobs sorted by complexity
python -m legacy_analyzer migration export-jobs \
    --db analyzer.db \
    --sort-by complexity

# Extract top 10 most complex jobs
jq '.jobs[0:10]' results/jobs/jobs_by_complexity.json > high_risk_jobs.json
```

**Benefits**:
- Allocate extra resources to complex jobs
- Plan for additional testing
- Identify jobs that may need refactoring

### 4. Three-Phase Migration

**Goal**: Migrate in phases (Infrastructure → Application → Orchestration)

**Approach**:
```bash
# Phase 1: Infrastructure jobs
jq '.jobs[] | select(.jobType == "INFRASTRUCTURE")' \
    results/jobs/jobs_by_type.json > phase1_infrastructure.json

# Phase 2: Application flows (use flow export)
python -m legacy_analyzer migration export-flows \
    --db analyzer.db \
    --output phase2_flows.json \
    --sort complexity-asc

# Phase 3: Application jobs (orchestration)
jq '.jobs[] | select(.jobType == "APPLICATION")' \
    results/jobs/jobs_by_type.json > phase3_orchestration.json
```

**Benefits**:
- Clear separation of concerns
- Parallel work streams
- Reduced risk

## Examples

### Example 1: Export All Strategies

```bash
#!/bin/bash
# Export jobs with all sorting strategies for comparison

DB="analyzer.db"
OUTPUT_DIR="results/jobs"

echo "Exporting jobs with all sorting strategies..."

for strategy in name type dependencies complexity; do
    echo "  Exporting with strategy: ${strategy}"
    python -m legacy_analyzer migration export-jobs \
        --db ${DB} \
        --output-dir ${OUTPUT_DIR} \
        --sort-by ${strategy}
done

echo "Done! Output files:"
ls -lh ${OUTPUT_DIR}/jobs_by_*.json
```

### Example 2: Analyze Job Distribution

```python
import json

# Load job export
with open('results/jobs/jobs_by_type.json') as f:
    data = json.load(f)

# Analyze distribution
total = data['summary']['totalJobs']
app = data['summary']['applicationJobs']
infra = data['summary']['infrastructureJobs']

print(f"Total Jobs: {total}")
print(f"Application Jobs: {app} ({app/total*100:.1f}%)")
print(f"Infrastructure Jobs: {infra} ({infra/total*100:.1f}%)")

# Analyze step complexity
step_counts = [len(job['steps']) for job in data['jobs']]
avg_steps = sum(step_counts) / len(step_counts)
max_steps = max(step_counts)

print(f"\nStep Complexity:")
print(f"Average steps per job: {avg_steps:.1f}")
print(f"Maximum steps in a job: {max_steps}")

# Find jobs with most dependencies
dep_counts = [
    (job['jobName'], 
     len(job['dependencies']['mustRunAfter']) + len(job['dependencies']['mustRunBefore']))
    for job in data['jobs']
]
dep_counts.sort(key=lambda x: x[1], reverse=True)

print(f"\nTop 5 jobs by dependency count:")
for name, count in dep_counts[:5]:
    print(f"  {name}: {count} dependencies")
```

### Example 3: Cross-Reference Jobs and Flows

```python
import json

# Load job and flow exports
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
```

### Example 4: Generate Migration Wave Plan

```python
import json

# Load exports
with open('results/jobs/jobs_by_type.json') as f:
    jobs_data = json.load(f)

with open('results/flows/flows_by_complexity_asc.json') as f:
    flows_data = json.load(f)

# Define waves
waves = {
    'Wave 1: Infrastructure': [
        j for j in jobs_data['jobs'] if j['jobType'] == 'INFRASTRUCTURE'
    ],
    'Wave 2: Simple Flows': flows_data['flows'][:10],
    'Wave 3: Medium Flows': flows_data['flows'][10:25],
    'Wave 4: Complex Flows': flows_data['flows'][25:],
    'Wave 5: Orchestration': [
        j for j in jobs_data['jobs'] if j['jobType'] == 'APPLICATION'
    ]
}

# Print wave summary
for wave_name, items in waves.items():
    print(f"\n{wave_name}:")
    print(f"  Items: {len(items)}")
    if 'Flow' in wave_name:
        total_loc = sum(f['complexity']['totalLoc'] for f in items)
        print(f"  Total LOC: {total_loc:,}")
    else:
        total_steps = sum(len(j['steps']) for j in items)
        print(f"  Total Steps: {total_steps}")
```

## See Also

- [CLI Reference](../../../docs/CLI_REFERENCE.md) - Complete command-line reference
- [Migration Workflow Guide](../../../docs/MIGRATION_WORKFLOW_GUIDE.md) - Complete migration planning process
- [Flow Export Documentation](README.md) - Flow export feature documentation
- [API Reference](../../../docs/API_REFERENCE.md) - Python API documentation
