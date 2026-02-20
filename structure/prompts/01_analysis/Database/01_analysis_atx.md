# Phase 1.1: Database Analysis (ATX Data Dictionary)

---

## Orchestration Information

**Phase**: Phase 1 - Source Code Analysis
**Step**: Step 1.1 - Database Analysis (ATX)
**Team Supervisor**: analysis_team_supervisor
**Assigned Agent**: analysis_specialist_database
**Task File Name**: {{TASKS_BASE_PATH}}/analysis_database_atx_specialist_task.md

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
- [ ] All database structures analyzed and documented
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
- **Objective section**: The goal of analyzing ATX data dictionary files
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
  - ATX data dictionary: {{ATX_DATA_DICTIONARY}}
  - ATX data lineage: {{ATX_DATA_LINEAGE}}
  - Legacy specifications: {{LEGACY_SPECIFICATION}}
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

## Context

### Project Information
**Project Name**: {{PROJECT_NAME}}
**Project Base Path**: {{PROJECT_BASE_PATH}}

### Input Locations
- **ATX Data Dictionary**: `{{ATX_DATA_DICTIONARY}}`
  - Description: CSV files containing database metadata extracted by ATX
  - Format: CSV files (data_dictionary_cpy.csv, data_dictionary_ddl.csv)
- **ATX Data Lineage**: `{{ATX_DATA_LINEAGE}}`
  - Description: CSV/JSON files showing data flow and relationships
  - Format: CSV/JSON files (program_to_dsn.csv, dsn_to_file.csv, jcl_to_dsn.csv)
- **Legacy Specifications**: `{{LEGACY_SPECIFICATION}}`
  - Description: Legacy framework documentation
  - Format: Documentation files

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

Analyze ATX data dictionary CSV files to understand database structures, VSAM files, and data relationships. Evaluate suitability of each target system for migration. Report findings and generate scripts for equivalent databases for target system(s). Usage of a Python tool for this task is optional - if it exists, use and adapt the existing database_analyzer tool for this task, or create a new one.

---

## Instructions

### Step 1: ATX Data Dictionary Discovery and Inventory

Scan all ATX data dictionary CSV files to extract database and VSAM file metadata.

#### 1.1 Relational Database Tables (data_dictionary_ddl.csv)

**File Location**: `{{ATX_DATA_DICTIONARY}}/data_dictionary_ddl.csv`

**CSV Columns**:
- `table_name`: Name of the database table
- `field_name`: Column name
- `db2_data_type`: DB2-specific data type
- `generic_data_type`: Generic data type classification
- `schema_name`: Database schema
- `column_position`: Ordinal position of column
- `data_length`: Length of the field
- `decimal_precision`: Precision for decimal types
- `decimal_scale`: Scale for decimal types
- `nullable`: Whether column allows NULL values
- `default_value`: Default value for column
- `primary_key`: Whether column is part of primary key (YES/NO)
- `foreign_key_schema`: Schema of referenced table (if FK)
- `foreign_key_table`: Referenced table name (if FK)
- `foreign_key_column`: Referenced column name (if FK)
- `check_constraint`: Check constraint definition
- `type`: Object type (TABLE, VIEW, etc.)
- `business_definition`: Business description of the field

**Actions**:
1. Parse CSV file and group rows by `table_name`
2. For each table, extract:
   - Schema name
   - All columns with data types, lengths, precision, scale
   - Primary key columns (where `primary_key` = 'YES')
   - Foreign key relationships (where `foreign_key_table` is not empty)
   - Nullable constraints
   - Default values
   - Business definitions
3. Create inventory of all tables with metadata

#### 1.2 VSAM File Definitions (data_dictionary_cpy.csv)

**File Location**: `{{ATX_DATA_DICTIONARY}}/data_dictionary_cpy.csv`

**CSV Columns**:
- `data_source_name`: Copybook/record name
- `field_name`: Field name within the record
- `field_type`: Type classification (FIELD, GROUP, RECORD, CONDITION)
- `mainframe_data_type`: COBOL/mainframe data type (e.g., X(10), S9(4) COMP)
- `generic_data_type`: Generic type (ALPHANUMERIC, NUMERIC, PACKED, BINARY, etc.)
- `level`: COBOL level number (01, 05, 10, 88, etc.)
- `data_length`: Length in bytes
- `business_definition`: Business description
- `logical_group`: Logical grouping of the field
- `display_format`: Display format pattern
- `display_length`: Display length
- `decimal_positions`: Number of decimal places
- `signed_indicator`: Whether field is signed (YES/NO)
- `usage_clause`: COBOL USAGE clause (DISPLAY, COMP, COMP-3, etc.)
- `occurs_min`, `occurs_max`, `occurs_depending`: Array/table information
- `redefines_field`: Field being redefined
- `root_record`: Root record structure name
- `field_position`: Byte position in record
- `synchronized`, `justified`, `blank_when_zero`: COBOL clauses
- `value_clause`: Initial value
- `condition_values`, `condition_ranges`: Level-88 condition values

**Actions**:
1. Parse CSV file and group rows by `data_source_name` (root record)
2. For each record structure:
   - Identify root record (level = 1 or root_record = data_source_name)
   - Build hierarchical field structure using `level` numbers
   - Extract field names, types, lengths, positions
   - Calculate total record length
   - Identify key fields (typically first field at position 1)
   - Note REDEFINES, OCCURS, and condition names (level 88)
3. Cross-reference with data lineage to identify VSAM files

#### 1.3 Data Lineage Analysis (program_to_dsn.csv)

**File Location**: `{{ATX_DATA_LINEAGE}}/program_to_dsn.csv`

**CSV Columns**:
- `File Name`: Source program name
- `File Path`: Path to source program
- `Data Source Name`: Dataset name (VSAM file, DB2 table, etc.)
- `DD Name`: JCL DD name
- `Logical Name`: Logical file name in program
- `Copybook Record Name`: Associated copybook record structure
- `Copybook File Path`: Path to copybook file
- `Data Source Type`: Type (VSAM-KSDS, VSAM-ESDS, VSAM-RRDS, VSAM-PATH, Dataset, GDG Base, DB2 Table)
- `Access Type`: How data is accessed (READ, WRITE, UPDATE, DELETE, etc.)

**Actions**:
1. Parse CSV file to identify all unique data sources
2. For each VSAM file (Data Source Type contains 'VSAM'):
   - Extract dataset name
   - Identify organization type (KSDS, ESDS, RRDS, AIX/PATH)
   - Find associated copybook record name
   - Match copybook record to data_dictionary_cpy.csv entries
   - Determine access patterns (READ, WRITE, UPDATE)
   - Identify programs that use the file
3. For DB2 tables:
   - Match to data_dictionary_ddl.csv entries
   - Document access patterns
4. Create mapping: Dataset Name → Copybook Record → Field Structure

#### 1.4 Create Comprehensive Inventory

For each discovered database object, record:
- Object name (table name or dataset name)
- Object type (DB2 Table, VSAM KSDS/ESDS/RRDS, etc.)
- Schema/catalog (for DB2)
- Record structure name (for VSAM)
- Field/column list with types and lengths
- Key fields (primary key for tables, VSAM key for files)
- Relationships (foreign keys, alternate indexes)
- Access patterns (programs that use it, READ/WRITE/UPDATE)
- Business definitions
- Source of definition (data_dictionary_ddl.csv or data_dictionary_cpy.csv)

#### 1.5 Error Handling
- Log any CSV files that cannot be parsed
- Flag records with missing or inconsistent data
- Note VSAM files without matching copybook definitions
- Document tables without primary keys



### Step 2: Compatibility Analysis

Analyze the database structures for incompatibilities or changes needed for each target system.

**Analysis Categories:**

1. **Datatype Compatibility**
   - Map mainframe/DB2 datatypes to target system datatypes
   - Identify datatypes not supported in target system
   - Document required mitigation/mapping
   - Examples:
     - COBOL `S9(4) COMP` (BINARY) → PostgreSQL `SMALLINT`, DB2 LUW `SMALLINT`
     - COBOL `S9(10)V99 COMP-3` (PACKED) → PostgreSQL `NUMERIC(12,2)`, DB2 LUW `DECIMAL(12,2)`
     - COBOL `X(50)` (ALPHANUMERIC) → PostgreSQL `VARCHAR(50)`, DB2 LUW `VARCHAR(50)`
     - DB2 `CHAR(16)` → PostgreSQL `CHAR(16)`, DB2 LUW `CHAR(16)`
     - DB2 `TIMESTAMP` → PostgreSQL `TIMESTAMP`, DB2 LUW `TIMESTAMP`

2. **VSAM to Relational Mapping**
   - **VSAM-KSDS** (Key-Sequenced Data Set):
     - Map to relational table with PRIMARY KEY
     - First field (at position 1) typically becomes primary key
     - Preserve all fields as columns
   - **VSAM-ESDS** (Entry-Sequenced Data Set):
     - Map to relational table with auto-increment surrogate key
     - Add SERIAL/IDENTITY/AUTO_INCREMENT column
   - **VSAM-RRDS** (Relative Record Data Set):
     - Map to relational table with INTEGER primary key
     - Relative record number becomes primary key
   - **VSAM-PATH/AIX** (Alternate Index):
     - Create secondary index or unique constraint
     - Map alternate key fields to INDEX

3. **Constraint Compatibility**
   - Preserve primary keys from DDL or infer from VSAM key fields
   - Preserve foreign keys from DDL
   - Map COBOL level-88 conditions to CHECK constraints (optional)
   - Preserve NOT NULL constraints from DDL nullable column

4. **Feature Compatibility**
   - Identify DB2-specific features not in target system
   - Document alternatives or limitations
   - Example: DB2 `GENERATED ALWAYS` → PostgreSQL `GENERATED ALWAYS` or `SERIAL`

**For Each Target System:**
- Document all incompatibilities found
- Provide migration strategy for each issue
- Rate migration complexity (Low/Medium/High)
- Identify blocking issues (if any)

### Step 3: Create Equivalent DDLs for Target Systems

For each target system (DB2 LUW, PostgreSQL):

1. **Generate DDL Scripts for DB2 Tables**
   - Read table definitions from data_dictionary_ddl.csv
   - Create CREATE TABLE statements with:
     - All columns with mapped data types
     - Primary key constraints
     - Foreign key constraints
     - NOT NULL constraints
     - Default values
     - Check constraints (if any)
   - Add comments with business definitions

2. **Generate DDL Scripts for VSAM Files**
   - Read record structures from data_dictionary_cpy.csv
   - Cross-reference with data lineage to identify VSAM organization type
   - Create CREATE TABLE statements with:
     - Table name derived from dataset name (e.g., AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS → ACCTDATA)
     - Columns from copybook fields (skip FILLER, GROUP, REDEFINES unless needed)
     - Primary key from first field (for KSDS) or surrogate key (for ESDS/RRDS)
     - Data types mapped from mainframe types to target SQL types
     - Comments documenting original VSAM structure
   - For VSAM-PATH/AIX, create secondary indexes

3. **Column Name Preservation**
   - **CRITICAL**: Do not change the column names themselves
   - Use field names from data_dictionary_ddl.csv or data_dictionary_cpy.csv
   - ONLY change column labels/comments if needed
   - Maintain exact column name spelling and case

4. **Referential Integrity**
   - Preserve all foreign key relationships from DDL
   - For VSAM files, infer relationships from data lineage if possible
   - Maintain primary key constraints
   - Preserve unique constraints and indexes

5. **Output Organization**
   - Save DDL scripts to: `{{DATABASE_GEN_SRC}}/[target_system]/ddl/`
   - Use naming convention: `[table_name]_[target_system].sql`
   - Include comment headers:
     ```sql
     -- Source: ATX Data Dictionary
     -- Original: [DB2 Table | VSAM-KSDS | VSAM-ESDS | VSAM-RRDS]
     -- Dataset/Table: [original name]
     -- Copybook: [copybook name] (for VSAM)
     -- Record Length: [bytes] (for VSAM)
     -- Business Definition: [from CSV]
     ```

### Step 4: Create Migration Scripts for Target Systems

For each target system (DB2 LUW, PostgreSQL):

1. **Data Migration Scripts**
   - Create scripts that migrate data from source system to target system
   - For DB2 tables: Direct table-to-table migration
   - For VSAM files: Extract data from VSAM → Load into relational table
   - Maintain referential integrity during migration
   - Handle datatype conversions

2. **Migration Order**
   - Use foreign key relationships from DDL to determine load order
   - Load parent tables before child tables
   - For VSAM files without explicit relationships, use data lineage access patterns
   - Document migration order with dependencies

3. **Data Validation**
   - Include row count validation
   - Include data integrity checks (FK constraints, NOT NULL)
   - Include data type validation
   - Provide rollback procedures

4. **Output Organization**
   - Save migration scripts to: `{{DATABASE_GEN_SRC}}/[target_system]/migration/`
   - Use naming convention: `migrate_[table_name]_to_[target_system].sql`
   - Include execution instructions and prerequisites

---

## Output Format

### Primary Outputs

#### 1. Database Analysis Report

**File**: `{{DATABASE_REPORTING}}`
**Template**: `{{DATABASE_REPORTING_TEMPLATE}}`

**Required Sections:**
- Executive Summary
- Database Inventory
  - DB2 Tables (from data_dictionary_ddl.csv)
  - VSAM Files (from data_dictionary_cpy.csv + data lineage)
  - Data Lineage Summary
- Compatibility Analysis (per target system)
  - Datatype mappings
  - VSAM to relational mappings
  - Constraint compatibility
  - Feature compatibility
- Migration Recommendations
- Risk Assessment
- Effort Estimation

#### 2. Target System DDL Scripts

**Location**: `{{DATABASE_GEN_SRC}}/[target_system]/ddl/`

**Requirements:**
- One DDL file per table/VSAM file per target system
- Complete table definitions with all columns
- All constraints and indexes
- Comments documenting source (ATX CSV file, original name, business definition)

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
- Tables analyzed count (DB2 + VSAM)
- Target systems evaluated
- Issues encountered
- Completion percentage

### Secondary Outputs

#### 1. Database Analyzer Tool

**File**: `{{DATABASE_ANALYZER_TOOL}}`

**Requirements:**
- Python tool that performs the analysis
- Should be reusable for similar ATX data dictionary outputs
- Include comprehensive error handling and logging
- Command-line interface for execution
- Configuration file support

**Tool Capabilities:**
- Parse ATX CSV files (data_dictionary_ddl.csv, data_dictionary_cpy.csv)
- Parse data lineage CSV files (program_to_dsn.csv, etc.)
- Cross-reference VSAM files with copybook definitions
- Map mainframe/DB2 datatypes to target SQL datatypes
- Map VSAM structures to relational tables
- Analyze compatibility with target systems
- Generate target DDL scripts
- Generate migration scripts
- Produce analysis report

---

## Quality Criteria

### Completeness
- [ ] All DB2 tables from data_dictionary_ddl.csv analyzed
- [ ] All VSAM files from data_dictionary_cpy.csv + data lineage analyzed
- [ ] Target systems contain SAME number of tables as source (DB2 + VSAM)
- [ ] All columns/fields included in target DDL
- [ ] All constraints and indexes migrated
- [ ] Migration scripts cover all tables
- [ ] All incompatibilities documented

### Accuracy
- [ ] Target database has same/equivalent datatypes
- [ ] Datatype mappings are correct (mainframe → SQL)
- [ ] Column names preserved exactly (no changes)
- [ ] VSAM key fields correctly mapped to primary keys
- [ ] Referential integrity maintained
- [ ] Constraints correctly translated

### Consistency
- [ ] After migration, referential integrity remains same as source
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

1. **CSV Parsing Errors**
   - **Detection**: Unable to parse CSV file or malformed rows
   - **Recovery**: Log error with file name and row number; continue with remaining rows
   - **Reporting**: Include in analysis report with recommendations

2. **Missing Data Dictionary Entries**
   - **Detection**: VSAM file in data lineage but no matching copybook in data_dictionary_cpy.csv
   - **Recovery**: Flag for manual investigation; document in report
   - **Reporting**: List all VSAM files with missing definitions

3. **Unsupported Datatypes**
   - **Detection**: Mainframe datatype not found in target system mapping
   - **Recovery**: Document as incompatibility; suggest manual review
   - **Reporting**: Flag as high-priority issue in report

4. **Inconsistent Metadata**
   - **Detection**: Conflicting information between CSV files
   - **Recovery**: Document discrepancy; use most authoritative source
   - **Reporting**: Flag as data quality issue

5. **Missing Primary Keys**
   - **Detection**: DB2 table with no primary_key='YES' columns
   - **Recovery**: Suggest candidate keys based on NOT NULL + unique patterns
   - **Reporting**: Flag for manual review

6. **Complex COBOL Structures**
   - **Detection**: REDEFINES, OCCURS DEPENDING ON, complex hierarchies
   - **Recovery**: Document structure; suggest manual review for mapping
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
