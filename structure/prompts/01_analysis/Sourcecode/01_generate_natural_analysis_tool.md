# Phase 1.1: Generate Natural Source Code Analysis Tool
 
## Context
- Input Location:
  -- Directories with source code files: `{{SOURCE_CODE}}` 
  -- Directory with database related source code: `{{DATABASE_SOURCE_CODE}}`
  -- Legacy framework documentation: `{{PROJECT_BASE_PATH}}/input/legacy_specifications/` 
  -- Preexisting tools (if any): `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/tools/`

- Output Location:
  -- Database analysis related files: `{{DATABASE_ANALYSIS_OUTPUT}}` 
  -- Reporting: `{{NATURAL_SOURCE_ANALYSIS_REPORT}}`
  -- Progress Tracking: `{{ANALYSIS_STATUS}}`
  -- Business Flow: `{{BUSINESS_FLOWS}}`
  -- Module Classification: `{{MODULE_CLASSIFICATIONS}}`
  -- Location of task-related files: `{{TASKS_BASE_PATH}}`

## Objective
Analyze Natural legacy source code. Understand structure, dependencies, and flows. Generate comprehensive dependency analysis, module classifications, end-to-end flow identification, and business domain assignments to support migration planning. Make use of preexisting tools if available or create them.

## Instructions

### Step 1: Source Code Discovery and Inventory
1. Scan all source files in the source directory
2. Include file extensions: .NSN, .NSP, .NSM, .NSL, .NSG, .NSC, .nsn, .nsp, .nsm, .nsl, .nsg, .nsc
3. Create inventory of all discovered files with basic metadata (size, last modified, etc.)
4. Log any files that cannot be parsed or accessed
 
**System Utilities to Exclude:**
Exclude the following Natural system utilities from dependency analysis as they are not business modules:
- System programs and utilities that are part of the Natural runtime environment
- Built-in Natural functions and system subprograms

### Step 2: Dependency Analysis
Using Natural-specific call patterns, identify all dependencies between modules:

**Natural Call Types to Recognize:**
- **CALLNAT**: `CALLNAT 'program-name'` or `CALLNAT program-name`
- **PERFORM**: `PERFORM subroutine-name` (internal subroutines)
- **FETCH**: `FETCH 'program-name'` (dynamic program loading)
- **INCLUDE**: `INCLUDE copycode-name` (copycode inclusion)
- **PROCESS**: `PROCESS PAGE` or `PROCESS PAGE USING map-name`
- **INPUT**: `INPUT USING MAP map-name`
- **REINPUT**: `REINPUT USING MAP map-name`
- **External Calls**: Calls to external programs or system functions
- **Database Access**: `FIND`, `READ`, `STORE`, `UPDATE`, `DELETE` statements
- **ADABAS Calls**: Direct ADABAS database operations
- **RPC Calls**: Remote procedure calls in distributed Natural environments

**File Operations to Recognize:**
- **Natural Work Files**: Work file definitions and operations
- **Natural Sequential Files**: Sequential file access operations
- **Natural Report Output**: Report generation and output operations
 
**Database Table Access to Recognize:**
- **ADABAS operations**: `FIND`, `READ`, `STORE`, `UPDATE`, `DELETE` statements with database/file numbers
- **SQL table operations**: `SELECT * FROM table-name`, `INSERT INTO table-name`, `UPDATE table-name`, `DELETE FROM table-name`
- **Database file references**: Extract database file numbers and names from Natural statements
- **DDL table definitions**: Match table names with files in the directory: `{{DATABASE_SOURCE_CODE}}`
 
**Dependency Analysis Exclusions:**
- Exclude FILE_ACCESS operations from missing module analysis (these are file operations, not callable modules)
- Exclude system utilities listed above from all dependency analysis
- Mark DDL tables as TargetFound=True when they exist in directory: `{{DATABASE_SOURCE_CODE}}`
 
**Peculiarities in the code**
Dynamic CALLNATs may use variables, eg:
"MOVE 'SUBPROG' TO #PROGRAM-NAME
 CALLNAT #PROGRAM-NAME"
 
**Inter-Language Dependencies to Flag:**
- **COBOL Program Calls**: `CALLNAT 'program-name'` where program-name matches COBOL program naming conventions
- **Assembler Utility Calls**: External calls to assembler utilities or system programs
- **System Interface Calls**: Calls to system programs that may be in other languages
- **Dynamic Loading**: `FETCH 'program-name'` - flag for cross-language resolution
- **Mixed Environment Integration**: Natural programs that interface with COBOL/PL1 systems
- **Shared Copycode**: `INCLUDE copycode-name` where copycode might be shared with other languages
 
**Things to ignore:**
- Internal subroutine calls within the same program (PERFORM within same module)
- Built-in function calls (SUBSTR, VAL, etc.)
- Control flow statements (IF, FOR, REPEAT, DECIDE, etc.)
- Variable assignments and data manipulation
- Calls in commented lines
- System reserved subroutines and built-in Natural functions

### Step 3: Module Classification
Classify each Natural module using two separate categorizations:
 
**TYPE Classification (based on usage patterns):**
- **COMMONLY_USED**: Modules referenced by 2 or more other modules (excluding entry points)
- **SINGLE_USE**: Modules referenced by only one other module (excluding entry points)
- **ENTRY_POINT**: Modules not referenced by other modules, but called via transactions or batch jobs
 
**FUNCTIONALITY Classification (based on business logic):**
- **FUNCTIONAL**: Modules containing specific business logic or business relevant database statements
- **UTILITY**: Reusable modules with no business logic (logging, error handling, monitoring, date routines, string manipulation, validation functions, etc.)
 
**Program Addition Context Integration:**
- For entry points: Include transaction code, transaction name, map name
- For BATCH programs: Include job name or batch context

### Step 4: Usage Classification
Determine usage context for each module:
- **Batch**: Only used in batch processing
- **Online**: Only used in online processing (interactive Natural programs)
- **Both**: Used in both batch and online contexts

### Step 5: End-to-End Flow Identification
1. Identify entry points 
2. Trace execution paths from entry points through all called modules:
  - Remove duplicates in the path and exclude database queries (FIND, READ, STORE, UPDATE, DELETE)
3. Identify database operations (ADABAS access, SQL statements if applicable)
4. Identify file operations (work files, sequential files from Natural file definitions)
5. Identify copycode usage (INCLUDE statements) for each flow
6. Identify map interactions (INPUT/OUTPUT operations with maps)
7. Map complete flows from entry to data persistence and file I/O
8. Calculate flow complexity based on:
   - Number of modules in the flow
   - Number of decision points (IF statements, DECIDE statements)
   - Number of database operations
   - Number of file operations
   - Number of map interactions
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
**File**: `{{NATURAL_SOURCE_ANALYSIS_REPORT}}`
**Template for the file**: `{{NATURAL_SOURCE_ANALYSIS_REPORT_TEMPLATE}}`
 
#### 2. Dependency Analysis Table
 
Where the fields of the template shall be filled like this:
- **Name**: Name of the calling module
- **Filetype**: NATURAL_PROGRAM|NATURAL_SUBPROGRAM|NATURAL_MAP|NATURAL_LDA|NATURAL_GDA|NATURAL_COPYCODE
- **ModuleType**: ENTRY_POINT|COMMONLY_USED|SINGLE_USE (usage pattern classification)
- **ModuleFunctionality**: FUNCTIONAL|UTILITY (business logic classification)
- **Language**: Natural
- **NaturalObjectType**: PROGRAM|SUBPROGRAM|MAP|LDA|GDA|COPYCODE
- **BusinessDomain**: Assigned business domain or NONE
- **Usage**: Batch|Online|Both
- **EntryPoint**: Yes|No (if module is an entry point)
- **CallType**: Type of Natural call or file operation (as defined in Step 2: Dependency Analysis)
- **TargetModule**: Name of the called module (empty for file operations)
- **TargetFound**: True|False - True if target module exists in any source directory OR if target table exists in DDL directory, False otherwise
- **FlowId**: Identifier for the end-to-end flow this call belongs to
- **Complexity**: Numeric complexity score for the calling module
- **FileOperation**: (leave empty for Natural - no file operations in CSV)
- **FileTarget**: (leave empty for Natural - no file operations in CSV)
 
#### 3. Business Flow Specifications
**File**: `{{BUSINESS_FLOWS}}`
**Template for the file**: `{{BUSINESS_FLOWS_TEMPLATE}}`
 
 
#### 4. Module Classification Report
**File**: `{{MODULE_CLASSIFICATIONS}}`
**Template for the file**: `{{MODULE_CLASSIFICATIONS_TEMPLATE}}`

 
#### 5. Dependency Analysis Tool
**File**: `{{NATURAL_SOURCE_CODE_ANALYSIS_ANALYZER_TOOL}}`
- Python tool that performs the analysis
- Should be reusable for similar Natural codebases
- Include comprehensive error handling and logging
 
#### 6. Progress Tracking
**File**: `{{ANALYSIS_STATUS}}`
**Template for the file**: `{{ANALYSIS_STATUS_TEMPLATE}}`

## Quality Criteria
 
### Completeness
- All Natural source files must be analyzed
- All dependency relationships must be captured
- All entry points must be identified
- All identified entry points must be mapped to end-to-end flows
 
### Accuracy
- Module classifications must be consistent and accurate
- Business domain assignments must be logical and well-documented
- Dependency relationships must be verified and complete
- Flow complexity calculations must be consistent
- Database operations must include actual queries (FIND, READ, STORE, UPDATE, DELETE) and real database file information
 
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
- Detection: CALLNAT statements referencing non-existent programs
- Recovery: Mark as "Missing" in dependency table, continue analysis
- Escalation: Document all missing dependencies for manual review

#### 3. **Ambiguous Business Domains**
- Detection: Module functionality doesn't clearly fit any domain
- Recovery: Assign "MIXED" or "UNKNOWN" domain, document rationale
- Escalation: Flag for business specialist review

#### 4. **Complex Dynamic Calls**
- Detection: CALLNAT statements using variables that cannot be resolved
- Recovery: Mark as "DYNAMIC_CALL" with variable name, continue analysis
- Escalation: Document for manual analysis

### Error Reporting Format
**File**: `{{ANALYSIS_ERRORS}}`
**Template for the file**: `{{ANALYSIS_ERRORS_TEMPLATE}}`

### Fallback Strategies
- **Simplified Analysis**: If full parsing fails, perform basic pattern matching
- **Partial Processing**: Continue with successfully analyzed modules
- **Manual Intervention**: Provide clear documentation for human review
- **Alternative Approaches**: Use different parsing strategies for problematic files

## Success Validation
- Verify all output files are created with valid content
- Validate JSON outputs against specified schemas
- Confirm all modules are accounted for in classification report
- Verify dependency relationships are bidirectional where appropriate
- Check that all entry points have corresponding flows identified
- Validate strict adherence to specified output formats:
  - JSON files must match exact schema structure and field names
  - Markdown files must include all required sections in correct order
  - File paths and names must match specifications exactly
  - All required fields must be populated (no empty values unless specified)