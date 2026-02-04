# Phase 1.1: Database Analysis

---

## Orchestration Information

**Phase**: Phase 1 - Source Code Analysis
**Step**: Step 1.1 - Database Analysis
**Team Supervisor**: analysis_team_supervisor
**Assigned Agent**: analysis_specialist_database
**Task File Name**: {{TASKS_BASE_PATH}}/analysis_database_specialist_task.md

### Expected Deliverables

1. **Database Analysis Report**
   - File: {{DATABASE_ANALYSIS_REPORT}}
   - Template: {{DATABASE_REPORTING_TEMPLATE}}
   - Description: Comprehensive database analysis findings and compatibility assessment

2. **Target System DDL Scripts**
   - File: {{DATABASE_GEN_SRC}}/
   - Description: Functionally equivalent database DDL for each target system

3. **Migration Scripts**
   - File: {{DATABASE_GEN_SRC}}/migration/
   - Description: Data migration scripts for each target system

4. **Database Analyzer Tool**
   - File: {{DATABASE_ANALYZER_TOOL}}
   - Description: Python tool that performs the database analysis

5. **Progress Tracking**
   - File: {{DATABASE_PROGRESS_TRACKING}}
   - Template: {{ANALYSIS_STATUS_TEMPLATE}}
   - Description: Database analysis progress and status tracking

### Success Criteria
- [ ] All database schemas analyzed and documented
- [ ] Compatibility assessment complete for all target systems
- [ ] DDL scripts generated for all target systems
- [ ] Migration scripts created for all target systems
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for review

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: The goal of analyzing database source files
- **Detailed instructions**: All Steps 1-4 below
- **Technical specifications**: Target systems (DB2 LUW, PostgreSQL), compatibility analysis requirements
- **Business rules and constraints**: Column name preservation rules, datatype mapping requirements
- **Error handling guidance**: File parsing errors, compatibility issues
- **Output format requirements**: All primary outputs and their specifications
- **Quality criteria**: Completeness, accuracy, consistency requirements

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Database source files: {{PROJECT_BASE_PATH}}/input/legacy/database/
  - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
- **All output locations** (resolved paths):
  - Database analysis output: {{DATABASE_ANALYSIS_OUTPUT}}
  - Database generation source: {{DATABASE_GEN_SRC}}
  - Database reporting: {{DATABASE_REPORTING}}
  - Progress tracking: {{DATABASE_PROGRESS_TRACKING}}
  - Database analyzer tool: {{DATABASE_ANALYZER_TOOL}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Reporting template: {{DATABASE_REPORTING_TEMPLATE}}
  - Analysis status template: {{ANALYSIS_STATUS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: analysis_specialist_database
- **Agent definition file**: structure/agents/analysis_team/analysis_specialist_database.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations, output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-4), business rules, error handling
- **Expected Deliverables**: All 5 deliverables with paths, templates, descriptions, validation checklists
- **Quality Criteria**: Completeness, accuracy, consistency (from this prompt)
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

---

## Task File Creation Example

Below is a concrete example showing how to create the task file for this step:

### Example: Creating analysis_database_specialist_task.md

**Given:**
- Project Name: MyMigration
- Project Base Path: /absolute/path/to/MyMigration
- Tasks Base Path: /absolute/path/to/MyMigration/tasks

**Step 1: Extract Objective from this prompt**
```
Objective: Analyze database source files to understand structure and dependencies. Evaluate suitability of each target system for migration. Generate scripts for equivalent databases for target systems.
```

**Step 2: Extract Instructions (Steps 1-4 from this prompt)**
```
Step 1: Source Code Discovery and Inventory
- Scan all DDL and SQL source files in the database source directory
- Create inventory of all discovered files with basic metadata
- Log any files that cannot be parsed or accessed
[... continue with all steps ...]
```

**Step 3: Resolve All Paths**
```
Input Locations:
- Database source files: /absolute/path/to/MyMigration/input/legacy/database
- Legacy specifications: /absolute/path/to/MyMigration/input/legacy_specifications

Output Locations:
- Database analysis output: /absolute/path/to/MyMigration/output/analysis/database
- Database generation source: /absolute/path/to/MyMigration/output/gen_src/database
- Database reporting: /absolute/path/to/MyMigration/output/analysis/database/reports/database_analysis.md
[... continue with all paths ...]
```

**Step 4: Create Task File Structure**

The resulting task file should look like this:

```markdown
# Task: Database Analysis

## Agent Assignment
**Agent**: analysis_specialist_database
**Agent Definition**: structure/agents/analysis_team/analysis_specialist_database.md
**Task ID**: analysis-database-001
**Created By**: analysis_team_supervisor
**Created At**: 2024-01-15T09:00:00Z
**Phase**: analysis
**Step**: database

---

## Project Context

### Project Information
**Project Name**: MyMigration
**Project Base Path**: /absolute/path/to/MyMigration

### Input Locations
- **Database Source Files**: /absolute/path/to/MyMigration/input/legacy/database
  - Description: DDL, SQL, VSAM definition files
  - Format: SQL DDL, database scripts
- **Legacy Specifications**: /absolute/path/to/MyMigration/input/legacy_specifications
  - Description: Legacy framework documentation
  - Format: Documentation files

### Output Locations
- **Database Analysis Report**: /absolute/path/to/MyMigration/output/analysis/database/reports/database_analysis.md
  - Template: /absolute/path/to/MyMigration/templates/DB_Source_Analysis_Report.md
  - Description: Comprehensive database analysis findings
  - Format: Markdown
- **Target System DDL Scripts**: /absolute/path/to/MyMigration/output/gen_src/database/[target_system]/ddl/
  - Description: Functionally equivalent database DDL for each target system
  - Format: SQL DDL
- **Migration Scripts**: /absolute/path/to/MyMigration/output/gen_src/database/[target_system]/migration/
  - Description: Data migration scripts for each target system
  - Format: SQL scripts
- **Database Analyzer Tool**: /absolute/path/to/MyMigration/output/analysis/database/tools/database_analyzer.py
  - Description: Python tool for database analysis
  - Format: Python script
- **Progress Tracking**: /absolute/path/to/MyMigration/output/analysis/database/progress/database_status.json
  - Template: /absolute/path/to/MyMigration/templates/Analysis_Status.json
  - Description: Database analysis progress tracking
  - Format: JSON

### Target Systems
- DB2 LUW
- PostgreSQL

---

## Task Instructions

### Objective
Analyze database source files to understand structure and dependencies. Evaluate suitability of DB2 LUW and PostgreSQL for migration from legacy database. Report findings and generate scripts for equivalent databases for target systems.

### Detailed Steps

#### Step 1: Source Code Discovery and Inventory
Scan all DDL and SQL source files in /absolute/path/to/MyMigration/input/legacy/database

**Actions:**
1. Identify all files with extensions: .ddl, .sql
2. Create inventory with metadata (database system type, database name, tables, file size, last modified)
3. Log any files that cannot be parsed

**File Types to Include:**
- DDL files (.ddl, .sql)
- SQL scripts (.sql)
- VSAM definitions
- Database configuration files

#### Step 2: Compatibility Analysis
Analyze database scripts for incompatibilities with each target system (DB2 LUW, PostgreSQL)

**Analysis Categories:**
1. **Datatype Compatibility**
   - Identify datatypes not supported in target system
   - Document required mitigation/mapping
   - Example: "DECIMAL(15,2) in source → NUMERIC(15,2) in PostgreSQL"

2. **SQL Dialect Compatibility**
   - Identify dialect/commands not supported by target system
   - Document workarounds (possible/not possible)
   - Example: "MERGE statement → Use INSERT...ON CONFLICT in PostgreSQL"

3. **Database Feature Compatibility**
   - Identify features of source DB not found in target system
   - Document alternatives or limitations
   - Example: "VSAM files → Relational tables with indexes"

**For Each Target System:**
- Document all incompatibilities found
- Provide migration strategy for each issue
- Rate migration complexity (Low/Medium/High)
- Identify blocking issues (if any)

#### Step 3: Create Equivalent DDLs for Target Systems
For each target system (DB2 LUW, PostgreSQL):

**Actions:**
1. Generate DDL scripts that reproduce functionally equivalent database
2. Maintain same table structure and relationships
3. Apply datatype mappings identified in Step 2
4. **CRITICAL**: Do not change column names - only change labels/comments if needed
5. Preserve all foreign key relationships, primary keys, unique constraints, and indexes

**Output Organization:**
- Save DDL scripts to: /absolute/path/to/MyMigration/output/gen_src/database/[target_system]/ddl/
- Use naming convention: [database_name]_[target_system].sql
- Include comments documenting any transformations

#### Step 4: Create Migration Scripts for Target Systems
For each target system (DB2 LUW, PostgreSQL):

**Actions:**
1. Create scripts that migrate data from source to target system
2. Maintain referential integrity during migration
3. Handle datatype conversions
4. Document migration order (to respect dependencies)
5. Include data validation steps and rollback procedures

**Output Organization:**
- Save migration scripts to: /absolute/path/to/MyMigration/output/gen_src/database/[target_system]/migration/
- Use naming convention: migrate_[database_name]_to_[target_system].sql
- Include execution instructions

---

## Expected Deliverables

### 1. Database Analysis Report
**File**: /absolute/path/to/MyMigration/output/analysis/database/reports/database_analysis.md
**Template**: /absolute/path/to/MyMigration/templates/DB_Source_Analysis_Report.md
**Description**: Comprehensive database analysis findings and compatibility assessment

**Content Requirements:**
- Executive Summary
- Database Inventory
- Compatibility Analysis (per target system)
- Migration Recommendations
- Risk Assessment
- Effort Estimation

**Validation:**
- [ ] File exists at specified path
- [ ] File format matches template
- [ ] All required sections present
- [ ] All target systems covered

### 2. Target System DDL Scripts
**Location**: /absolute/path/to/MyMigration/output/gen_src/database/[target_system]/ddl/
**Description**: Functionally equivalent database DDL for each target system

**Content Requirements:**
- One DDL file per database per target system
- Complete table definitions
- All constraints and indexes
- Comments documenting transformations

**Validation:**
- [ ] DDL files exist for all target systems
- [ ] All tables included
- [ ] Column names preserved exactly
- [ ] Constraints correctly translated

### 3. Migration Scripts
**Location**: /absolute/path/to/MyMigration/output/gen_src/database/[target_system]/migration/
**Description**: Data migration scripts for each target system

**Content Requirements:**
- Data migration scripts
- Execution order documentation
- Validation queries
- Rollback procedures

**Validation:**
- [ ] Migration scripts exist for all target systems
- [ ] All tables covered
- [ ] Execution instructions included
- [ ] Rollback procedures provided

### 4. Database Analyzer Tool
**File**: /absolute/path/to/MyMigration/output/analysis/database/tools/database_analyzer.py
**Description**: Python tool that performs the database analysis

**Content Requirements:**
- Reusable for similar database codebases
- Comprehensive error handling and logging
- Command-line interface
- Configuration file support

**Validation:**
- [ ] Tool file exists
- [ ] Tool is executable
- [ ] Error handling included
- [ ] Documentation provided

### 5. Progress Tracking
**File**: /absolute/path/to/MyMigration/output/analysis/database/progress/database_status.json
**Template**: /absolute/path/to/MyMigration/templates/Analysis_Status.json
**Description**: Database analysis progress and status tracking

**Content Requirements:**
- Analysis status (In Progress/Complete/Blocked)
- Databases analyzed count
- Target systems evaluated
- Issues encountered
- Completion percentage

**Validation:**
- [ ] File exists at specified path
- [ ] JSON format valid
- [ ] All required fields populated
- [ ] Status accurately reflects progress

---

## Quality Criteria

### Completeness
- [ ] All database files discovered and inventoried
- [ ] All tables analyzed for each target system
- [ ] Target systems contain SAME number of tables as source database
- [ ] All columns included in target DDL
- [ ] All constraints and indexes migrated
- [ ] Migration scripts cover all tables
- [ ] All incompatibilities documented

### Accuracy
- [ ] Target database has same/equivalent datatypes
- [ ] Datatype mappings are correct
- [ ] Column names preserved exactly (no changes)
- [ ] Referential integrity maintained
- [ ] Constraints correctly translated
- [ ] SQL dialect differences addressed

### Consistency
- [ ] After migration, referential integrity remains same as source database
- [ ] Foreign key relationships preserved
- [ ] Data relationships maintained
- [ ] Naming conventions consistent
- [ ] Documentation format consistent across target systems

---

## Success Criteria

**Task is complete when:**
- [ ] All deliverables produced at specified paths
- [ ] All quality criteria met
- [ ] All validation checks pass
- [ ] No blocking errors remain unresolved
- [ ] Ready for review by analysis_reviewer_database

**Verification Steps:**
1. Check all output files exist at specified locations
2. Validate DDL scripts are syntactically correct
3. Verify migration scripts include all tables
4. Confirm analysis report covers all requirements
5. Review error log for any blocking issues
6. Validate progress tracking is up to date
7. Report completion to analysis_team_supervisor

---

## Notes

### Agent Definition Reference
Your complete role definition and capabilities are in:
structure/agents/analysis_team/analysis_specialist_database.md

This task file provides project-specific context and instructions.

### Escalation
If you encounter issues beyond your capability:
1. Document the issue clearly
2. Report to analysis_team_supervisor
3. Provide context and attempted solutions

### Error Handling
- Log all errors to: /absolute/path/to/MyMigration/output/analysis/database/errors.log
- Include timestamp, file name, error type, and description
- Provide actionable recommendations for resolution
```

**Key Points:**
- All {{PARAMETERS}} replaced with actual absolute paths
- Instructions extracted and adapted from this prompt
- Agent definition referenced, not duplicated
- Complete deliverables list with validation checklists
- Quality and success criteria included
- Target systems (DB2 LUW, PostgreSQL) clearly specified

---

## Context

### Project Information
**Project Name**: {{PROJECT_NAME}}
**Project Base Path**: {{PROJECT_BASE_PATH}}

### Input Locations
- **Database Source Files**: `{{PROJECT_BASE_PATH}}/input/legacy/database/`
  - Description: DDL, SQL, VSAM definition files
  - Format: SQL DDL, database scripts

### Output Locations
- **Database Analysis Output**: `{{DATABASE_ANALYSIS_OUTPUT}}`
  - Description: Database analysis related files
- **Database Generation Source**: `{{DATABASE_GEN_SRC}}`
  - Description: Database creation or migration related files
- **Progress Tracking**: `{{DATABASE_PROGRESS_TRACKING}}`
  - Template: `{{ANALYSIS_STATUS_TEMPLATE}}`
  - Description: Analysis progress tracking
- **Reporting**: `{{DATABASE_REPORTING}}`
  - Template: `{{DATABASE_REPORTING_TEMPLATE}}`
  - Description: Database analysis report
- **Database Analyzer Tool**: `{{DATABASE_ANALYZER_TOOL}}`
  - Description: Python tool for database analysis

### Target Systems
The following target systems should be evaluated for migration compatibility:
- DB2 LUW
- PostgreSQL

---

## Objective

Analyze database source files to understand structure and dependencies. Evaluate suitability of each target system for migration from legacy database to target system. Report findings and generate scripts for equivalent databases for target system(s). Usage of a Python tool for this task is optional - if it exists, use and adapt the existing database_analyzer tool for this task, or create a new one.

---

## Instructions

### Step 1: Source Code Discovery and Inventory
1. Scan all DDL and SQL source files in the database source directory
2. Create inventory of all discovered files with basic metadata:
   - Database system type
   - Database name
   - Tables included in the files
   - File size and last modified date
3. Log any files that cannot be parsed or accessed

**File Types to Include:**
- DDL files (.ddl, .sql)
- SQL scripts (.sql)
- VSAM definitions
- Database configuration files

### Step 2: Compatibility Analysis
Analyze the database scripts for incompatibilities or changes needed for each target system.

**Analysis Categories:**

1. **Datatype Compatibility**
   - Identify datatypes not supported in target system
   - Document required mitigation/mapping
   - Example: "DECIMAL(15,2) in source → NUMERIC(15,2) in PostgreSQL"

2. **SQL Dialect Compatibility**
   - Identify dialect/commands not supported by target system
   - Document workarounds (possible/not possible)
   - Example: "MERGE statement → Use INSERT...ON CONFLICT in PostgreSQL"

3. **Database Feature Compatibility**
   - Identify features of source DB not found in target system
   - Document alternatives or limitations
   - Example: "VSAM files → Relational tables with indexes"

**For Each Target System:**
- Document all incompatibilities found
- Provide migration strategy for each issue
- Rate migration complexity (Low/Medium/High)
- Identify blocking issues (if any)

### Step 3: Create Equivalent DDLs for Target Systems
For each target system (DB2 LUW, PostgreSQL):

1. **Generate DDL Scripts**
   - Create DDL/SQL that reproduces a functionally equivalent database
   - Maintain same table structure and relationships
   - Apply datatype mappings identified in Step 2

2. **Column Name Preservation**
   - **CRITICAL**: Do not change the column names themselves
   - ONLY change the column labels/comments if needed
   - Maintain exact column name spelling and case

3. **Referential Integrity**
   - Preserve all foreign key relationships
   - Maintain primary key constraints
   - Preserve unique constraints and indexes

4. **Output Organization**
   - Save DDL scripts to: `{{DATABASE_GEN_SRC}}/[target_system]/ddl/`
   - Use naming convention: `[database_name]_[target_system].sql`
   - Include comments documenting any transformations

### Step 4: Create Migration Scripts for Target Systems
For each target system (DB2 LUW, PostgreSQL):

1. **Data Migration Scripts**
   - Create scripts that migrate data from source system to target system
   - Maintain referential integrity during migration
   - Handle datatype conversions

2. **Reference Consistency**
   - Ensure all foreign key references remain valid
   - Preserve data relationships
   - Maintain data integrity constraints

3. **Migration Strategy**
   - Document migration order (to respect dependencies)
   - Include data validation steps
   - Provide rollback procedures

4. **Output Organization**
   - Save migration scripts to: `{{DATABASE_GEN_SRC}}/[target_system]/migration/`
   - Use naming convention: `migrate_[database_name]_to_[target_system].sql`
   - Include execution instructions

---

## Output Format

### Primary Outputs

#### 1. Database Analysis Report

**File**: `{{DATABASE_REPORTING}}`
**Template**: `{{DATABASE_REPORTING_TEMPLATE}}`

**Required Sections:**
- Executive Summary
- Database Inventory
- Compatibility Analysis (per target system)
- Migration Recommendations
- Risk Assessment
- Effort Estimation

#### 2. Target System DDL Scripts

**Location**: `{{DATABASE_GEN_SRC}}/[target_system]/ddl/`

**Requirements:**
- One DDL file per database per target system
- Complete table definitions
- All constraints and indexes
- Comments documenting transformations

#### 3. Migration Scripts

**Location**: `{{DATABASE_GEN_SRC}}/[target_system]/migration/`

**Requirements:**
- Data migration scripts
- Execution order documentation
- Validation queries
- Rollback procedures

#### 4. Progress Tracking

**File**: `{{DATABASE_PROGRESS_TRACKING}}`
**Template**: `{{ANALYSIS_STATUS_TEMPLATE}}`

**Required Fields:**
- Analysis status (In Progress/Complete/Blocked)
- Databases analyzed count
- Target systems evaluated
- Issues encountered
- Completion percentage

### Secondary Outputs

#### 1. Database Analyzer Tool

**File**: `{{DATABASE_ANALYZER_TOOL}}`

**Requirements:**
- Python tool that performs the analysis
- Should be reusable for similar database codebases
- Include comprehensive error handling and logging
- Command-line interface for execution
- Configuration file support

**Tool Capabilities:**
- Parse DDL files
- Analyze compatibility
- Generate target DDL
- Generate migration scripts
- Produce analysis report

---

## Quality Criteria

### Completeness
- [ ] All database files discovered and inventoried
- [ ] All tables analyzed for each target system
- [ ] Target systems contain SAME number of tables as source database
- [ ] All columns included in target DDL
- [ ] All constraints and indexes migrated
- [ ] Migration scripts cover all tables
- [ ] All incompatibilities documented

### Accuracy
- [ ] Target database has same/equivalent datatypes
- [ ] Datatype mappings are correct
- [ ] Column names preserved exactly (no changes)
- [ ] Referential integrity maintained
- [ ] Constraints correctly translated
- [ ] SQL dialect differences addressed

### Consistency
- [ ] After migration, referential integrity remains same as source database
- [ ] Foreign key relationships preserved
- [ ] Data relationships maintained
- [ ] Naming conventions consistent
- [ ] Documentation format consistent across target systems

### Usability
- [ ] DDL scripts are executable
- [ ] Migration scripts include clear instructions
- [ ] Error handling is comprehensive
- [ ] Rollback procedures provided
- [ ] Documentation is clear and complete

---

## Error Handling

### Common Issues

1. **File Parsing Errors**
   - **Detection**: Unable to parse DDL file
   - **Recovery**: Log error with file name and line number; continue with remaining files
   - **Reporting**: Include in analysis report with recommendations

2. **Unsupported Datatypes**
   - **Detection**: Datatype not found in target system mapping
   - **Recovery**: Document as incompatibility; suggest manual review
   - **Reporting**: Flag as high-priority issue in report

3. **Missing Dependencies**
   - **Detection**: Referenced table/column not found
   - **Recovery**: Document as broken reference; flag for manual resolution
   - **Reporting**: Include in risk assessment section

4. **Complex SQL Constructs**
   - **Detection**: SQL feature not supported in target system
   - **Recovery**: Document workaround or flag as manual migration
   - **Reporting**: Include in compatibility analysis with alternatives

### Error Logging
- Log all errors to: `{{DATABASE_ANALYSIS_OUTPUT}}/errors.log`
- Include timestamp, file name, error type, and description
- Provide actionable recommendations for resolution

---

## Success Validation

**Task is complete when:**
- [ ] All deliverables exist at specified paths
- [ ] Database analysis report is comprehensive and complete
- [ ] DDL scripts generated for all target systems
- [ ] Migration scripts created for all target systems
- [ ] All quality criteria met
- [ ] Progress tracking updated to "Complete"
- [ ] No blocking errors remain unresolved
- [ ] Ready for review by analysis_reviewer_database

**Verification Steps:**
1. Check all output files exist at specified locations
2. Validate DDL scripts are syntactically correct
3. Verify migration scripts include all tables
4. Confirm analysis report covers all requirements
5. Review error log for any blocking issues
6. Validate progress tracking is up to date
7. Report completion to analysis_team_supervisor

