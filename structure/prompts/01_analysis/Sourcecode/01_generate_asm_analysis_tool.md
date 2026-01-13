# Phase 1.1: Generate ASM (Assembler) Source Code Analysis Tool
 
## Context
- Input Location:
  -- Directories with source code files: `{{SOURCE_CODE}}` 
  -- Directory with database related source code: `{{DATABASE_SOURCE_CODE}}`
  -- Legacy framework documentation: `{{PROJECT_BASE_PATH}}/input/legacy_specifications/` 
  -- Preexisting tools (if any): `{{SOURCE_CODE_ANALYSIS_OUTPUT}}/tools/`

- Output Location:
  -- Database analysis related files: `{{DATABASE_ANALYSIS_OUTPUT}}` 
  -- Reporting: `{{ASM_SOURCE_CODE_ANALYSIS_REPORTING}}`
  -- Module Dependency Table: `{{ASM_SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}`
  -- Progress Tracking: `{{ASM_SOURCE_CODE_ANALYSIS_PROGRESS_TRACKING}}`
  -- Business Flow: `{{ASM_SOURCE_CODE_ANALYSIS_BUSINESS_FLOW}}`
  -- ASM Module Classification: `{{ASM_MODULE_CLASSIFICATION}}`
  -- Location of task-related files: `{{TASKS_BASE_PATH}}`

## Objective
Analyze Assembler legacy source code. Understand structure, dependencies, and flows. Generate comprehensive dependency analysis, module classifications, end-to-end flow identification, and business domain assignments to support migration planning. Make use of preexisting tools if available or create them.

## Instructions

### Step 1: Source Code Discovery and Inventory
1. Scan all source files in the source directory
2. Include file extensions: .asm, .ASM, .s, .S, .hlasm, .jcl, .JCL, .mac, .MAC
3. Create inventory of all discovered files with basic metadata (size, last modified, etc.)
4. Log any files that cannot be parsed or accessed
 
**System Utilities to Exclude:**
Exclude the following mainframe system utilities from dependency analysis as they are not business modules:
- System macros and utilities that are part of the operating system
- Standard IBM-supplied macros and modules
- System service routines

### Step 2: Dependency Analysis
Using Assembler-specific call patterns, identify all dependencies between modules:

**Assembler Call Types to Recognize:**
- **CALL**: `CALL program-name` or `L R15,=A(program-name)` followed by `BALR R14,R15`
- **BAL/BALR**: `BAL R14,subroutine` or `BALR R14,R15` (branch and link)
- **LINK**: `LINK EP=program-name` (dynamic linking)
- **LOAD**: `LOAD EP=program-name` (dynamic loading)
- **XCTL**: `XCTL EP=program-name` (transfer control)
- **ATTACH**: `ATTACH EP=program-name` (task attachment)
- **Macro Calls**: `macro-name MACRO` (macro invocations)
- **COPY**: `COPY member-name` (copybook inclusion)
- **INCLUDE**: `INCLUDE member-name` (include statements)
- **JCL EXEC**: `//stepname EXEC PGM=program-name`
- **SVC Calls**: `SVC nn` (supervisor calls)
- **CICS Calls**: `EXEC CICS` statements (if CICS-enabled assembler)

**File Operations to Recognize:**
- **DCB definitions**: Data Control Block definitions for file access
- **QSAM operations**: Sequential file access macros (GET, PUT, OPEN, CLOSE)
- **VSAM operations**: VSAM file access macros (READ, WRITE, etc.)
- **BDAM operations**: Direct access method operations
 
**Database Table Access to Recognize:**
- **DB2 operations**: SQL statements embedded in assembler (EXEC SQL)
- **IMS DL/I calls**: Database calls to IMS databases
- **Database file references**: Extract database file names from assembler statements
- **DDL table definitions**: Match table names with files in the directory: `{{DATABASE_SOURCE_CODE}}`
 
**Dependency Analysis Exclusions:**
- Exclude FILE_ACCESS operations from missing module analysis (these are file operations, not callable modules)
- Exclude system utilities listed above from all dependency analysis
- Mark DDL tables as TargetFound=True when they exist in directory: `{{DATABASE_SOURCE_CODE}}`
 
**Peculiarities in the code**
Dynamic calls may use register contents, eg:
"L R15,=A(SUBPROG)
 BALR R14,R15"
 
**Inter-Language Dependencies to Flag:**
- **COBOL Program Calls**: `CALL program-name` or `LINK EP=program-name` where program-name matches COBOL naming patterns
- **Natural Program Calls**: `LINK EP=program-name` where program-name matches Natural naming conventions
- **PL/1 Program Calls**: `CALL program-name` where program-name matches PL/1 naming conventions
- **High-Level Language Interfaces**: Assembler modules called from COBOL/Natural/PL1 (typically utilities, system interfaces)
- **System Exit Points**: Assembler programs that serve as exits for other languages
- **Dynamic Loading**: `LOAD EP=program-name` - flag for cross-language resolution
- **Shared Macros**: Macro calls that might be used across languages
 
**Things to ignore:**
- Internal branch instructions within the same module (B, BC, BRC, etc.)
- Register operations and data movement instructions
- Arithmetic and logical operations
- Storage allocation and deallocation
- Calls in commented lines
- System reserved macros and built-in system functions

### Step 3: Module Classification
Classify each Assembler module using two separate categorizations:
 
**TYPE Classification (based on usage patterns):**
- **COMMONLY_USED**: Modules referenced by 2 or more other modules (excluding entry points)
- **SINGLE_USE**: Modules referenced by only one other module (excluding entry points)
- **ENTRY_POINT**: Modules not referenced by other modules, but called via JCL, CICS, TSO, or system interfaces
 
**FUNCTIONALITY Classification (based on business logic):**
- **FUNCTIONAL**: Modules containing specific business logic or business relevant database statements
- **UTILITY**: Reusable modules with no business logic (logging, error handling, monitoring, system interfaces, I/O routines, date routines, string manipulation, etc.)
 
**Program Addition Context Integration:**
- For entry points: Include JCL name, CICS transaction code, TSO command name
- For BATCH programs: Include JCL name or batch context

### Step 4: Usage Classification
Determine usage context for each module:
- **Batch**: Only used in batch processing (JCL execution)
- **Online**: Only used in online processing (CICS, TSO)
- **Both**: Used in both batch and online contexts


### Step 5: End-to-End Flow Identification
1. Identify entry points 
2. Trace execution paths from entry points through all called modules:
  - Remove duplicates in the path and exclude database queries (SELECT, UPDATE, etc.)
3. Identify database operations (DB2 calls, IMS DL/I calls, VSAM access)
4. Identify file operations (QSAM, BDAM, VSAM file I/O from DCB definitions and file access macros)
5. Identify macro usage (COPY, INCLUDE statements) for each flow
6. Identify system service calls (SVC calls) for each flow
7. Map complete flows from entry to data persistence and file I/O
8. Calculate flow complexity based on:
   - Number of modules in the flow
   - Number of decision points (conditional branches)
   - Number of database operations
   - Number of file operations
   - Number of system service calls
   - Number of external calls

### Step 6: Business Domain Assignment
Analyze module functionality and assign business domains:
- Examine program names, comments, and business logic
- Look for domain indicators in data areas and processing logic
- Common domains: CUSTOMER, ACCOUNT, TRANSACTION, REPORTING, SECURITY, etc.
- Mark utility modules as "NONE"
- Document rationale for domain assignments

## Output Format
 
### Primary Outputs
 
#### 1. Source Code Analysis Report
**File**: `{{ASM_SOURCE_CODE_ANALYSIS_REPORTING}}`
**Template for the file**: `{{ASM_SOURCE_CODE_ANALYSIS_REPORTING_TEMPLATE}}`
 
#### 2. Dependency Analysis Table
**File**: `{{ASM_SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}`
**Template for the file**: `{{ASM_SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE_TEMPLATE}}`
 
Where the fields of the template shall be filled like this:
- **Name**: Name of the calling module
- **Filetype**: ASM|ASM_MACRO|JCL
- **ModuleType**: ENTRY_POINT|COMMONLY_USED|SINGLE_USE (usage pattern classification)
- **ModuleFunctionality**: FUNCTIONAL|UTILITY (business logic classification)
- **BusinessDomain**: Assigned business domain or NONE
- **Usage**: Batch|Online|Both
- **EntryPoint**: Yes|No (if module is an entry point)
- **CallType**: Type of Assembler call or file operation (as defined in Step 2: Dependency Analysis)
- **TargetModule**: Name of the called module (empty for file operations)
- **TargetFound**: True|False - True if target module exists in any source directory OR if target table exists in DDL directory, False otherwise
- **FlowId**: Identifier for the end-to-end flow this call belongs to
- **Complexity**: Numeric complexity score for the calling module
- **FileOperation**: IN|OUT|INOUT (for file operations, empty for module calls)
- **FileTarget**: Dataset name or file name (for file operations, empty for module calls)
 
#### 3. Business Flow Specifications
**File**: `{{ASM_SOURCE_CODE_ANALYSIS_BUSINESS_FLOW}}`
**Template for the file**: `{{ASM_SOURCE_CODE_ANALYSIS_BUSINESS_FLOW_TEMPLATE}}`
 
 
#### 4. Module Classification Report
**File**: `{{ASM_MODULE_CLASSIFICATION}}`
**Template for the file**: `{{ASM_MODULE_CLASSIFICATION_TEMPLATE}}`

 
#### 5. Dependency Analysis Tool
**File**: `{{ASM_SOURCE_CODE_ANALYSIS_ANALYZER_TOOL}}`
- Python tool that performs the analysis
- Should be reusable for similar Assembler codebases
- Include comprehensive error handling and logging
 
#### 6. Progress Tracking
**File**: `{{ASM_SOURCE_CODE_ANALYSIS_PROGRESS_TRACKING}}`
**Template for the file**: `{{ASM_SOURCE_CODE_ANALYSIS_PROGRESS_TRACKING_TEMPLATE}}`

## Quality Criteria
 
### Completeness
- All Assembler source files must be analyzed
- All dependency relationships must be captured
- All entry points must be identified
- All identified entry points must be mapped to end-to-end flows
 
### Accuracy
- Module classifications must be consistent and accurate
- Business domain assignments must be logical and well-documented
- Dependency relationships must be verified and complete
- Flow complexity calculations must be consistent
- Database operations must include actual operations (READ, WRITE, UPDATE, DELETE) and real database file information
 
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
- Detection: CALL/LINK statements referencing non-existent modules
- Recovery: Mark as "Missing" in dependency table, continue analysis
- Escalation: Document all missing dependencies for manual review

#### 3. **Ambiguous Business Domains**
- Detection: Module functionality doesn't clearly fit any domain
- Recovery: Assign "MIXED" or "UNKNOWN" domain, document rationale
- Escalation: Flag for business analyst review

#### 4. **Complex Dynamic Calls**
- Detection: Indirect calls using register contents that cannot be resolved
- Recovery: Mark as "DYNAMIC_CALL" with register details, continue analysis
- Escalation: Document for manual analysis

### Error Reporting Format
**File**: `{{ASM_SOURCE_CODE_ANALYSIS_ERRORS}}`
**Template for the file**: `{{ASM_SOURCE_CODE_ANALYSIS_ERRORS_TEMPLATE}}`

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