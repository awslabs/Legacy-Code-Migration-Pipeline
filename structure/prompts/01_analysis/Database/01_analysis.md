# Phase 1: Database analysis

## Context
- Input Locations:
-- Sourcefiles for the Databases (DDL, SQL, VSAM definition): `{{PROJECT_BASE_PATH}}/input/legacy/database/` 

-Output locations:
-- Database analysis related files: `{{DATABASE_ANALYSIS_OUTPUT}}` 
-- Database creation or migration related files: `{{DATABASE_GEN_SRC}}` 
-- Progress Tracking: `{{DATABASE_PROGRESS_TRACKING}}`
-- Reporting: `{{DATABASE_REPORTING}}`
-- Database analyzer tool: `{{DATABASE_ANALYZER_TOOL}}`

- Target Systems to be evaluated:
-- DB2 LUW
-- PostgrSQL

## Objective
Analyze Database source files. Understand structure and dependencies. Evaluate suitability of each target system for a migration from legacy database to target system. Report findings. Generate scripts for equivalent databases for target system(s) and reports on success. Usage of a python tool for this task is optional. If it exists use and adapt the the existing database_analyzer tool for this task or create a new one.

## Instructions

### Step 1: Source Code Discovery and Inventory
1. Scan all DDL and SQL source files 
2. Create inventory of all discovered files with basic metadata (DB system, DB name, tables included in the files for the DB), 
3. Log any files that cannot be parsed or accessed

### Step 2: Compatibility Analysis
Analyze the database scripts for incompatibilities or changes needed for each target system.

**Sample for changes and issues:**
- **Datatype**: Datatype not in target system X. Needs mitigation/mapping to XXX
- **SQL dialect**: Dialect/commands not supported by target system X. Workaround possible/not possible.
- **DBFeature**: Feature of Source DB not found in Target System X.


### Step 3: Create equivalent DDLs for target systems
For each target system
- Create DDL/SQL that reproduces a functionally equivalent database.
- Do not change the column names themselves, ONLY change the labels.


### Step 4: Create migration script for target systems
For each target system
- Create script that will migrate data from source system to target system while keeping references consistent.


## Output Format

### Primary Outputs

#### 1. Source Code Analysis Report

**File**: `{{DATABASE_REPORTING}}`
**Template for the file**: `{{DATABASE_REPORTING_TEMPLATE}}`


#### 2. Progress Tracking
**File**: `{{DATABASE_PROGRESS_TRACKING}}`
**Template for the file**: `{{DATABASE_PROGRESS_TRACKING_TEMPLATE}}`


### Secondary Outputs 

#### 1. Dependency Analysis Tool
**File**: `{{DATABASE_ANALYZER_TOOL}}`
- Python tool that performs the analysis
- Should be reusable for similar Databases codebases
- Include comprehensive error handling and logging


## Quality Criteria: To be verified by review agent

### Completeness
- Target System should contain SAME amount of tables with all variables included as source db

### Accuracy
- Target DB should have same/equivalent data types

### Consistency
- After migration, referencial integrity must remain same as with source db

