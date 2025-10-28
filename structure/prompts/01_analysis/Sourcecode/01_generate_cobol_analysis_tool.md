# Phase 1.1: Generate COBOL Source Code Analysis Tool
 
## Context
- Input Location:
  -- Directories with source code files: `{{SOURCE_CODE}}` 
  -- Directory with database related source code: `{{DATABASE_SOURCE_CODE}}`
  -- Legacy framework documentation: `{{PROJECT_ROOT_DIR}}/input/legacy_specifications/` 
  -- Preexisting tools (if any): `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/tools/`

- Output Location:
  -- Database analysis related files: `{{DATABASE_ANALYSIS_OUTPUT}}` 
  -- Reporting: `{{SOURCE_CODE_ANALYSIS_REPORTING}}`
  -- Module Dependency Table: `{{SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}`
  -- Progress Tracking: `{{SOURCE_CODE_ANALYSIS_PROGRESS_TRACKING}}`
  -- Business Flow: `{{SOURCE_CODE_ANALYSIS_BUSINESS_FLOW}}`
  -- Cobol Module Classification: `{{COBOL_MODULE_CLASSIFICATION}}`
  
 
## Objective
Analyze COBOL legacy source code that was written for the zKESA Framework. Understand structure, dependencies, and flows. Generate comprehensive dependency analysis, module classifications, end-to-end flow identification, and business domain assignments to support migration planning. Make use of preexisting tools if available or create them.
 
## Instructions
 
### Step 1: Source Code Discovery and Inventory
1. Scan all source files in the source directory
2. Include file extensions: .cbl, .cob, .CBL, .COB, .jcl, .JCL, .csd, .bms, .copy, .cpy, .txt
3. Create inventory of all discovered files with basic metadata (size, last modified, etc.)
4. Log any files that cannot be parsed or accessed
 
**System Utilities to Exclude:**
Exclude the following mainframe system utilities from dependency analysis as they are not business modules:
- `DMBATCH` (NDM file transfer), `IDCAMS` (VSAM utility), `IEBCOPY` (dataset copy)
- `ICEMAN` (DFSORT), `SORT`, `SYNCSORT` (sort utilities)
- `DSNTEP2`, `DSNTIAUL` (DB2 utilities), `IKJEFT01` (TSO utility)
- `FMNMAIN` (File Manager), `IEBGENER` (dataset utility), `IEFBR14` (dummy program)

 
### Step 2: Dependency Analysis
Using COBOL-specific call patterns, identify all dependencies between modules:
 
**COBOL Call Types to Recognize:**
- **Standard CALL**: `CALL 'program-name'` or `CALL "program-name"`
- **Dynamic CALL**: `CALL variable-name` (where variable contains program name)
- **CICS LINK**: `EXEC CICS LINK PROGRAM('program-name')`
- **CICS XCTL**: `EXEC CICS XCTL PROGRAM('program-name')`
- **CICS START**: `EXEC CICS START TRANSID('tranid')`
- **COPY**: `COPY copybook-name`
- **JCL EXEC**: `//stepname EXEC PGM=program-name`
- **DB2 RUN**: `RUN PROGRAM(program-name)`
- **CICS EXEC**: `DEFINE TRANSACTION(tranid) ... PROGRAM(program-name)`
- **SQL CALL**: `EXEC SQL CALL procedure-name`
- **IMS DL/I CALL**: `CALL 'CBLTDLI' USING function-code pcb-mask segment-io-area`
 
**File Operations to Recognize:**
- **JCL DD statements**: `//ddname DD DSN=dataset-name,DISP=...` (input/output file definitions)
- **COBOL FD/SD**: File descriptions in DATA DIVISION
- **COBOL SELECT**: `SELECT file-name ASSIGN TO ddname` statements
- **VSAM operations**: READ, WRITE, REWRITE, DELETE statements on VSAM files
 
**Database Table Access to Recognize:**
- **SQL table operations**: `SELECT * FROM table-name`, `INSERT INTO table-name`, `UPDATE table-name`, `DELETE FROM table-name`
- **DB2 table references**: Extract table names from SQL statements
- **DDL table definitions**: Match table names with files in the directory: `{{DATABASE_SOURCE_CODE}}` 
 
**Dependency Analysis Exclusions:**
- Exclude FILE_ACCESS operations from missing module analysis (these are file operations, not callable modules)
- Exclude system utilities listed above from all dependency analysis
- Mark DDL tables as TargetFound=True when they exist in directory: `{{DATABASE_SOURCE_CODE}}`
 
**Peculiarities in the code**
Dynamic CALLs are sometimes multilined, eg:
"MOVE  "ZSFDBLG"                  TO   YCFCTLAR-CALL-PGM
 CALL  YCFCTLAR-CALL-PGM        USING  DFHEIBLK"
 
**Things to ignore:**
- Internal PERFORM statements within the same module
- Internal GO TO statements within the same module
- SQL execution statements (not calls to other programs) like "SELECT" etc..
- Linkage section definitions
- Calls in commented lines
- System reserved subroutines:
  - **DSNTIAR**: DB2 error message formatting routine
 
### Step 3: Module Classification
Classify each COBOL module using two separate categorizations:
 
**TYPE Classification (based on usage patterns):**
- **COMMONLY_USED**: Modules referenced by 2 or more other modules (excluding entry points)
- **SINGLE_USE**: Modules referenced by only one other module (excluding entry points)
- **ENTRY_POINT**: Modules not referenced by other modules, but called via CICS or JCL or screens
 
**FUNCTIONALITY Classification (based on business logic):**
- **FUNCTIONAL**: Modules containing specific business logic or business relevant SQL statements
- **UTILITY**: Reusable modules with no business logic (logging, error handling, monitoring, date routines, string manipulation, etc.)
 
**Program Addition Context Integration:**
- For entry points: Include screen ID, screen name, transaction code, transaction name
- For BATCH programs: Include JCL name
 
### Step 4: Usage Classification
Determine usage context for each module:
- **Batch**: Only used in batch processing (JCL execution)
- **Online**: Only used in online processing (CICS transactions)
- **Both**: Used in both batch and online contexts


### Step 5: End-to-End Flow Identification
1. Identify entry points 
2. Trace execution paths from entry points through all called modules:
  - Remove duplicates in the path and exclude DB queries(SELECT, UPDATE, etc.)
3. Identify database operations (SQL statements, IMS calls, VSAM access)
4. Identify file operations (input/output files from JCL DD statements and COBOL file definitions)
5. Identify copybook usage (COPY statements) for each flow
6. Map complete flows from entry to data persistence and file I/O
7. Calculate flow complexity based on:
   - Number of modules in the flow
   - Number of decision points (IF statements, EVALUATE statements)
   - Number of database operations
   - Number of file operations
   - Number of external system calls
 
### Step 6: Business Domain Assignment
Analyze module functionality and assign business domains:
- Examine program names, comments, and business logic
- Look for domain indicators in variable names and data structures
- Common domains: CUSTOMER, ACCOUNT, TRANSACTION, REPORTING, SECURITY, etc.
- Mark utility modules as "NONE"
- Document rationale for domain assignments
 
## Output Format
 
### Primary Outputs
 
#### 1. Source Code Analysis Report
**File**: `{{SOURCE_CODE_ANALYSIS_REPORTING}}`
**Template for the file**: `{{SOURCE_CODE_ANALYSIS_REPORTING_TEMPLATE}}`
 
#### 2. Dependency Analysis Table
**File**: `{{SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}`
**Template for the file**: `{{SOURCE_CODE_ANALYSIS_REPORTING_TEMPLATE}}`
 
Where the fileds of the template shall be filled like this:
- **Name**: Name of the calling module
- **Filetype**: COBOL|COPYBOOK|JCL
- **ModuleType**: ENTRY_POINT|COMMONLY_USED|SINGLE_USE (usage pattern classification)
- **ModuleFunctionality**: FUNCTIONAL|UTILITY (business logic classification)
- **BusinessDomain**: Assigned business domain or NONE
- **Usage**: Batch|Online|Both
- **EntryPoint**: Yes|No (if module is an entry point)
- **CallType**: Type of COBOL call or file operation (as defined in Step 2: Dependency Analysis)
- **TargetModule**: Name of the called module (empty for file operations)
- **TargetFound**: True|False - True if target module exists in any source directory OR if target table exists in DDL directory, False otherwise
- **FlowId**: Identifier for the end-to-end flow this call belongs to
- **Complexity**: Numeric complexity score for the calling module
- **FileOperation**: IN|OUT|INOUT (for file operations, empty for module calls)
- **FileTarget**: Dataset name or file name (for file operations, empty for module calls)
 
#### 3. Business Flow Specifications
**File**: `{{SOURCE_CODE_ANALYSIS_BUSINESS_FLOW}}`
**Template for the file**:** `{{SOURCE_CODE_ANALYSIS_BUSINESS_FLOW_TEMPLATE}}`
 
 
#### 4. Module Classification Report
**File**: `{{COBOL_MODULE_CLASSIFICATION}}`
**Template for the file**: `{{COBOL_MODULE_CLASSIFICATION_TEMPLATE}}`

 
#### 5. Dependency Analysis Tool
**File**: `{{SOURCE_CODE_ANALYSIS_ANALYZER_TOOL}}`
- Python tool that performs the analysis
- Should be reusable for similar COBOL codebases
- Include comprehensive error handling and logging
 
#### 6. Progress Tracking
**File**: `{{SOURCE_CODE_ANALYSIS_PROGRESS_TRACKING}}`
**Template for the file**:`{{SOURCE_CODE_ANALYSIS_PROGRESS_TRACKING_TEMPLATE}}`

 
## Quality Criteria
 
### Completeness
- All COBOL source files must be analyzed
- All dependency relationships must be captured
- All entry points must be identified
- All identified entry points must be mapped to end-to-end flows
 
### Accuracy
- Module classifications must be consistent and accurate
- Business domain assignments must be logical and well-documented
- Dependency relationships must be verified and complete
- Flow complexity calculations must be consistent
- Database operations must include actual queries (SELECT, UPDATE, etc.) and real database table information
 
### Consistency
- All output formats must match specified schemas
- Naming conventions must be followed consistently
- All required fields must be populated
- Cross-references between outputs must be accurate


 
## Error Handling
 
### Common Error Scenarios
 
#### 1. **Unparseable Source Files**
- Detection: Syntax errors, encoding issues, corrupted files
- Recovery: Log error, skip file, continue with remaining files
- Escalation: If >10% of files cannot be parsed, request human intervention
 
#### 2. **Missing Dependencies**
- Detection: CALL statements referencing non-existent modules
- Recovery: Mark as "Missing" in dependency table, continue analysis
- Escalation: Document all missing dependencies for manual review
 
#### 3. **Ambiguous Business Domains**
- Detection: Module functionality doesn't clearly fit any domain
- Recovery: Assign "MIXED" or "UNKNOWN" domain, document rationale
- Escalation: Flag for business analyst review
 
#### 4. **Complex Dynamic Calls**
- Detection: CALL statements using variables that cannot be resolved
- Recovery: Mark as "DYNAMIC_CALL" with variable name, continue analysis
- Escalation: Document for manual analysis
 
### Error Reporting Format
**File**: `{{SOURCE_CODE_ANALYSIS_ERRORS}}`
**Template for the file**: `{{SOURCE_CODE_ANALYSIS_ERRORS_TEMPLATE}}`
 
### Fallback Strategies
- **Simplified Analysis**: If full parsing fails, perform basic pattern matching
- **Partial Processing**: Continue with successfully analyzed modules
- **Manual Intervention**: Provide clear documentation for human review
- **Alternative Approaches**: Use different parsing strategies for problematic files
 
## Success Validation
- Verify all output files are created with valid content
- Validate JSON outputs against specified schemas
- Ensure CSV files have proper headers and data formatting
- Confirm all modules are accounted for in classification report
- Verify dependency relationships are bidirectional where appropriate
- Check that all entry points have corresponding flows identified
- Validate strict adherence to specified output formats:
  - JSON files must match exact schema structure and field names
  - CSV files must have exact column headers as specified
  - Markdown files must include all required sections in correct order
  - File paths and names must match specifications exactly
  - All required fields must be populated (no empty values unless specified)