# Phase 3.1: Business Logic Extraction

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.1 - Business Logic Extraction
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_logic_extraction
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.1_business_logic_extraction.md

### Expected Deliverables

1. **Chapter 6: Legacy Implementation References (Draft)**
   - File: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md
   - Description: Complete technical implementation details with code evidence (draft for review)

2. **Logic Extraction Notes**
   - File: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md
   - Description: Documented abstractions and patterns identified

3. **Progress Tracking**
   - File: {{BUSINESS_TRACEABILITY_STATUS}}
   - Description: Updated progress tracking

### Success Criteria
- [ ] Chapter 6 created with complete technical details
- [ ] All code references documented (file names, line numbers, snippets)
- [ ] Database tables and access patterns documented
- [ ] Error codes and handling documented
- [ ] Technical architecture documented
- [ ] Logic patterns identified with evidence
- [ ] Allowed abstraction patterns applied and documented
- [ ] No forbidden patterns (drift indicators) present
- [ ] Ready for Phase 3.1.1 review

---

## Context

### Input Locations
- **Approved business context**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md`
- **Business glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- **Source code files**: `{{SOURCE_CODE}}`
- **Database source code**: `{{DATABASE_SOURCE_CODE}}`
- **Workpackage definitions**: `{{PROJECT_BASE_PATH}}/output/analysis/workpackages/`

### Output Locations
- **Chapter 6 (draft)**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md`
- **Logic extraction notes**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md`
- **Progress tracking**: `{{BUSINESS_TRACEABILITY_STATUS}}`

### Template Locations
- **Business specification template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}` (use Chapter 6 section only)

### Previous Phase Artifacts
- **From Phase 3.0.1**: Approved business context, business glossary

---

## Objective

Extract business logic patterns from legacy code and create Chapter 6 (Legacy Implementation References) as the complete evidence base. Document ALL technical implementation details with full traceability. Apply allowed abstraction patterns only and avoid forbidden patterns (drift indicators). This Chapter 6 will serve as the foundation for creating Chapters 1-5 in Phase 3.2.

**CRITICAL PRINCIPLES**:
1. **Complete technical documentation** - Document ALL implementation details in Chapter 6
2. **Evidence-based extraction** - Every abstraction must have code evidence
3. **Allowed patterns only** - Apply only the 6 allowed abstraction patterns
4. **Avoid drift** - Do not add functionality, invent entities, or assume patterns
5. **Full traceability** - Include file names, line numbers, and code snippets

---

## CRITICAL RULES - Artifact Creation

**YOU MUST ONLY CREATE THE EXPLICITLY DEFINED OUTPUT FILES. NO ADDITIONAL ARTIFACTS.**

**Allowed Outputs** (from Output Locations section above):
- Chapter 6 (draft): `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md`
- Logic extraction notes: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md`
- Progress tracking: `{{BUSINESS_TRACEABILITY_STATUS}}`
- Error logs (if errors occur): `{{BUSINESS_TRACEABILITY_ERRORS}}`

**FORBIDDEN**:
- ❌ Summary documents (e.g., "phase_3.1_summary.md", "logic_extraction_summary.md")
- ❌ Completion reports (e.g., "phase_X.X_completion.md")
- ❌ Additional review documents beyond those specified
- ❌ Extra markdown files for "documentation purposes"
- ❌ Any file not explicitly listed in "Output Locations" above

**Rationale**: We have defined deliverables, review reports, status tracking, and error logs. Additional summary documents create clutter and redundancy. All necessary information should be captured in the defined outputs.

---

## Instructions

### 1. Preparation and Context Review
1. Review approved business context from Phase 3.0.1
2. Review business glossary
3. For each workpackage, identify all relevant source files:
   - COBOL programs
   - Copybooks and includes
   - JCL scripts
   - Maps and screens
   - Database definitions
4. Prepare to extract technical details with full traceability

### 2. Allowed Abstraction Patterns

**CRITICAL**: You may ONLY apply these 6 abstraction patterns. Document each abstraction in logic extraction notes.

#### Pattern 1: DATA_TYPE Abstraction
- **Purpose**: Convert COBOL data types to generic business types
- **Example**: PIC X(8) date field → Date type
- **Evidence Required**: Document original COBOL data type in Chapter 6
- **Documentation**: Note in logic extraction notes which fields were abstracted

#### Pattern 2: CONSOLIDATION Abstraction
- **Purpose**: Consolidate multiple technical steps into business-level description
- **Example**: 8 separate date validation steps → "must be valid date"
- **Evidence Required**: Document all consolidated steps in Chapter 6
- **Documentation**: List all steps consolidated and resulting business rule

#### Pattern 3: NAMING Abstraction
- **Purpose**: Convert technical names to business vocabulary
- **Example**: CUST-REC → Customer, WS-ORDER-AMT → orderTotal
- **Evidence Required**: Document original technical name in Chapter 6
- **Documentation**: Map technical name → business name using glossary

#### Pattern 4: STRUCTURE Abstraction
- **Purpose**: Transform flat COBOL records to normalized business entities
- **Example**: Flat records → normalized entities with relationships
- **Evidence Required**: Document original COBOL structure in Chapter 6
- **Documentation**: Show structure transformation

#### Pattern 5: LOGIC Abstraction
- **Purpose**: Extract business intent from code patterns
- **Example**: Code patterns → business logic description
- **Evidence Required**: Document code patterns with snippets in Chapter 6
- **Documentation**: Explain business intent derived from code

#### Pattern 6: PROCESS Abstraction
- **Purpose**: Transform call graphs to business workflows
- **Example**: PERFORM sequences → business process activities
- **Evidence Required**: Document technical call sequence in Chapter 6
- **Documentation**: Map technical flow → business process

### 3. Forbidden Patterns (Drift Indicators)

**CRITICAL**: You must NOT apply these patterns. They indicate analysis drift.

#### Forbidden 1: Adding Functionality
- **Example**: Adding timezone handling when code only validates date format
- **Why Forbidden**: Invents functionality not in code
- **Detection**: If abstraction includes logic not in Chapter 6 code, it's drift

#### Forbidden 2: Inventing Entities
- **Example**: Adding email field when database has no email column
- **Why Forbidden**: Creates entities not in database
- **Detection**: Cross-reference with database schema in Chapter 6

#### Forbidden 3: Assuming Standard Patterns
- **Example**: Assuming fiscal year logic when code only uses calendar dates
- **Why Forbidden**: Assumes patterns not implemented
- **Detection**: Verify each business rule has code evidence

#### Forbidden 4: Extrapolating Beyond Evidence
- **Example**: Inferring business rules not actually implemented
- **Why Forbidden**: Goes beyond what code actually does
- **Detection**: Every abstraction must trace to specific code

### 4. Chapter 6 Section 6.1: Source Files

**Purpose**: Document all source files involved

**For each source file:**
```markdown
### 6.1 Source Files

| File Name | File Type | Description | Path |
|-----------|-----------|-------------|------|
| ORDVAL.cbl | COBOL Program | Order validation main program | /src/cobol/ORDVAL.cbl |
| CUSTCOPY.cpy | Copybook | Customer record structure | /src/copybooks/CUSTCOPY.cpy |
| ORDPROC.jcl | JCL | Order processing batch job | /jcl/ORDPROC.jcl |
| ORDMAP.bms | Map | Order entry screen map | /maps/ORDMAP.bms |
```

**Quality Check:**
- [ ] All programs listed
- [ ] All copybooks listed
- [ ] All JCL scripts listed
- [ ] All maps/screens listed
- [ ] File paths provided
- [ ] File types identified

### 5. Chapter 6 Section 6.2: Business Rule Implementation

**Purpose**: Document how each business rule is implemented in legacy code

**For each business rule pattern identified:**

1. **Identify business rule from code**:
   - Look for validation logic
   - Look for conditional processing
   - Look for business constraints
   - Look for approval workflows

2. **Apply LOGIC abstraction**:
   - Extract business intent from code pattern
   - Use business vocabulary from glossary
   - Document in logic extraction notes

3. **Document technical implementation**:
```markdown
#### BR-XXX-001: [Business Rule Name from abstraction]

**Legacy Technical Approach**: [How the rule is implemented - use technical terms]
- IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT
- Uses COBOL conditional logic with working storage variables
- Calls REJECT-ORDER paragraph on failure

**Code References**:
- **File**: ORDVAL.cbl
- **Line Numbers**: 150-175
- **Code Snippet**:
```cobol
IF WS-CREDIT-LIM < WS-ORDER-AMT
    MOVE 'CREDIT_EXCEEDED' TO WS-ERROR-CODE
    PERFORM REJECT-ORDER
ELSE
    PERFORM APPROVE-ORDER
END-IF
```

**Legacy Reason**: Mainframe batch processing requires inline validation before database update to minimize rollback overhead

**Technical Constants**:
- WS-CREDIT-LIM: PIC 9(7)V99 COMP-3
- WS-ORDER-AMT: PIC 9(7)V99 COMP-3
- Buffer size: 1024 bytes

**Modern Cloud-Native Equivalent**: 
- Implement as validation service with REST API
- Use decimal types for currency
- Return structured error response

**Migration Guidance**:
- Extract validation logic to separate microservice
- Replace COBOL data types with standard decimal
- Implement as synchronous validation call

**Obsolescence Flag**: Still Needed - Core business rule
```

**Quality Check:**
- [ ] Legacy technical approach documented
- [ ] Code references complete (file, lines, snippet)
- [ ] Legacy reason explained
- [ ] Technical constants documented
- [ ] Modern equivalent suggested
- [ ] Migration guidance provided
- [ ] Obsolescence flag assigned

### 6. Chapter 6 Section 6.3: Function Implementation

**Purpose**: Document how each business function is implemented

**For each function/paragraph identified:**

1. **Identify function from code**:
   - COBOL paragraphs
   - Subroutines
   - Called programs
   - Cohesive units of logic

2. **Apply NAMING abstraction**:
   - Convert technical name to business name
   - Use business vocabulary from glossary
   - Document in logic extraction notes

3. **Document technical implementation**:
```markdown
#### F-XXX-001: [Business Function Name from abstraction]

**Legacy Technical Approach**: Implemented as COBOL paragraph VALIDATE-CREDIT
- Reads customer credit limit from DB2 table
- Compares against order amount
- Sets return code in working storage
- Calls error handling if validation fails

**Code References**:
- **File**: ORDVAL.cbl
- **Line Numbers**: 200-250
- **Code Snippet**:
```cobol
VALIDATE-CREDIT.
    EXEC SQL
        SELECT CREDIT_LIMIT
        INTO :WS-CREDIT-LIM
        FROM CUSTOMER
        WHERE CUST_ID = :WS-CUST-ID
    END-EXEC.
    
    IF SQLCODE NOT = 0
        MOVE 'DB_ERROR' TO WS-ERROR-CODE
        PERFORM ERROR-HANDLER
    ELSE
        IF WS-CREDIT-LIM < WS-ORDER-AMT
            MOVE 'CREDIT_EXCEEDED' TO WS-ERROR-CODE
            MOVE 'N' TO WS-VALID-FLAG
        ELSE
            MOVE 'Y' TO WS-VALID-FLAG
        END-IF
    END-IF.
```

**Technical Parameters**:
- Input: WS-CUST-ID (PIC X(10))
- Input: WS-ORDER-AMT (PIC 9(7)V99 COMP-3)
- Output: WS-VALID-FLAG (PIC X)
- Output: WS-ERROR-CODE (PIC X(20))

**Legacy Reason**: Embedded SQL used for direct DB2 access within CICS transaction

**Modern Cloud-Native Equivalent**:
- Implement as REST API endpoint: POST /validate-credit
- Use ORM for database access
- Return JSON response with validation result

**Migration Guidance**:
- Extract to separate validation microservice
- Replace embedded SQL with ORM queries
- Implement proper error handling with HTTP status codes

**Obsolescence Flag**: Still Needed - Core validation function
```

**Quality Check:**
- [ ] Legacy technical approach documented
- [ ] Code references complete
- [ ] Code snippet provided
- [ ] Technical parameters documented
- [ ] Legacy reason explained
- [ ] Modern equivalent suggested
- [ ] Migration guidance provided
- [ ] Obsolescence flag assigned

### 7. Chapter 6 Section 6.4: Database Tables

**Purpose**: Document all database tables accessed

**For each database table:**

1. **Identify from code**:
   - SQL statements
   - File I/O operations
   - Database calls

2. **Apply NAMING abstraction** (if appropriate):
   - Convert technical table name to business entity name
   - Document in logic extraction notes

3. **Document table details**:
```markdown
### 6.4 Database Tables

| Table Name | Table Type | Columns | Access Patterns | Code References | Modern Equivalent |
|------------|------------|---------|-----------------|-----------------|-------------------|
| CUSTOMER | Common | CUST_ID, NAME, CREDIT_LIMIT, STATUS | SELECT, UPDATE | ORDVAL.cbl:200-250 | DynamoDB or RDS |
| ORDER_HDR | Internal | ORDER_ID, CUST_ID, ORDER_DATE, TOTAL | INSERT, SELECT | ORDVAL.cbl:300-350 | DynamoDB or RDS |

**Detailed Table Definitions**:

#### CUSTOMER Table

**Columns**:
- CUST_ID: CHAR(10) PRIMARY KEY - Customer identifier
- NAME: VARCHAR(100) NOT NULL - Customer name
- CREDIT_LIMIT: DECIMAL(9,2) - Credit limit amount
- STATUS: CHAR(1) - Customer status (A=Active, I=Inactive)
- CREATED_DATE: DATE - Record creation date
- UPDATED_DATE: TIMESTAMP - Last update timestamp

**Access Patterns**:
- SELECT by CUST_ID (primary key lookup)
- UPDATE CREDIT_LIMIT by CUST_ID
- Embedded SQL in CICS transactions

**Code References**:
- ORDVAL.cbl lines 200-250: Credit validation query
- CUSTUPD.cbl lines 100-150: Credit limit update

**Modern Equivalent**:
- DynamoDB table with CUST_ID as partition key
- Or PostgreSQL RDS with indexed CUST_ID
- Access via ORM (e.g., SQLAlchemy, TypeORM)
```

**Quality Check:**
- [ ] All tables documented
- [ ] Table types identified
- [ ] Columns listed with data types
- [ ] Access patterns documented
- [ ] Code references provided
- [ ] Modern equivalent suggested

### 8. Chapter 6 Section 6.5: Error Codes

**Purpose**: Document all error codes and handling

**For each error code:**
```markdown
### 6.5 Error Codes

**Error Sets**: Validation Errors, Database Errors, Business Logic Errors

**Treatment Codes**: 
- ABEND: Abnormal termination with rollback
- WARN: Warning logged, processing continues
- REJECT: Transaction rejected, user notified

**Custom Error Codes**:

| Error Code | Description | Raised In | Handled In | Modern Equivalent |
|------------|-------------|-----------|------------|-------------------|
| CREDIT_EXCEEDED | Order exceeds credit limit | ORDVAL.cbl:165 | ERRHAND.cbl:50 | HTTP 400 with error detail |
| DB_ERROR | Database access failure | ORDVAL.cbl:210 | ERRHAND.cbl:100 | HTTP 500 with retry logic |
| INVALID_DATE | Date format validation failed | DATEUTIL.cbl:75 | ERRHAND.cbl:150 | HTTP 400 with validation error |
```

**Quality Check:**
- [ ] Error sets documented
- [ ] Treatment codes documented
- [ ] Custom error codes listed
- [ ] Code references provided
- [ ] Modern equivalent suggested

### 9. Chapter 6 Section 6.6: Technical Architecture

**Purpose**: Document technical architecture layers

**For each layer:**
```markdown
### 6.6 Technical Architecture

**BC Layer** (Business Component):
- Purpose: Business logic orchestration
- Components: ORDVAL.cbl, CUSTVAL.cbl, INVVAL.cbl
- Code References: /src/cobol/bc/*.cbl
- Modern Equivalent: Business logic microservices

**SQLIO Layer** (Database Access):
- Purpose: Database access abstraction
- Components: CUSTIO.cbl, ORDIO.cbl, INVIO.cbl
- Code References: /src/cobol/sqlio/*.cbl
- Modern Equivalent: Data access layer with ORM

**BATCH Layer** (Batch Processing):
- Purpose: Batch job orchestration
- Components: ORDPROC.jcl, CUSTPROC.jcl
- Code References: /jcl/*.jcl
- Modern Equivalent: AWS Batch or Kubernetes CronJobs

**Framework** (Common Utilities):
- Purpose: Shared utilities and error handling
- Components: ERRHAND.cbl, DATEUTIL.cbl, STRUTIL.cbl
- Code References: /src/cobol/framework/*.cbl
- Modern Equivalent: Shared libraries or utility services
```

**Quality Check:**
- [ ] All layers documented
- [ ] Components listed
- [ ] Code references provided
- [ ] Modern equivalents suggested

### 10. Chapter 6 Section 6.7: Data Flow Architecture

**Purpose**: Document how data flows through the system

**Apply PROCESS abstraction** to identify business workflows from technical flows:

```markdown
### 6.7 Data Flow Architecture

**Input**: CICS transaction ORDV (Order Validation)
- Entry Point: ORDVAL.cbl
- Input Data: Order details from screen ORDMAP
- Code References: ORDVAL.cbl:50-100
- Modern Equivalent: REST API POST /orders/validate

**Database Access**: Customer and Order tables
- Read: CUSTOMER table for credit limit
- Write: ORDER_HDR table for new order
- Code References: ORDVAL.cbl:200-250, 300-350
- Modern Equivalent: Microservice with database access via ORM

**Service Calls**: Credit check service
- External Call: CICS LINK to CREDCHK program
- Purpose: Real-time credit bureau check
- Code References: ORDVAL.cbl:400-450
- Modern Equivalent: REST API call to credit service

**Output**: Order validation result
- Success: Order accepted, confirmation screen
- Failure: Order rejected, error message displayed
- Code References: ORDVAL.cbl:500-550
- Modern Equivalent: JSON response with status and details

**Error Handling**: Centralized error handler
- Error Handler: ERRHAND.cbl
- Logging: CICS temporary storage queue
- Code References: ERRHAND.cbl:50-200
- Modern Equivalent: Structured logging with CloudWatch/ELK
```

**Quality Check:**
- [ ] Input mechanisms documented
- [ ] Database access documented
- [ ] Service calls documented
- [ ] Output mechanisms documented
- [ ] Error handling documented
- [ ] Code references provided
- [ ] Modern equivalents suggested

### 11. Chapter 6 Section 6.8: Technical Rules (Not Business Rules)

**Purpose**: Document technical rules specific to mainframe that are NOT business requirements

**CRITICAL**: These are technical workarounds and constraints, not business policies.

```markdown
### 6.8 Technical Rules (Not Business Rules)

#### Technical Rule: Batch Restart Logic

**Description**: Checkpoint/restart mechanism for long-running batch jobs
- Writes checkpoint records every 1000 transactions
- On restart, reads last checkpoint and resumes processing
- Prevents reprocessing of completed transactions

**Code References**:
- File: ORDPROC.cbl
- Lines: 1000-1100
- Checkpoint logic in WRITE-CHECKPOINT paragraph

**Legacy Reason**: Mainframe batch jobs can run for hours; restart capability required for recovery

**Obsolescence Flag**: Obsolete - Modern batch processing uses different patterns (idempotent operations, message queues)

---

#### Technical Rule: CICS Transaction Timeout

**Description**: Automatic rollback after 30 seconds of inactivity
- CICS enforces 30-second timeout
- All database changes rolled back on timeout
- User must restart transaction

**Code References**:
- Configuration: CICS region definition
- Handling: ERRHAND.cbl:300-350

**Legacy Reason**: CICS resource management to prevent hung transactions

**Obsolescence Flag**: Obsolete - Modern APIs use different timeout patterns

---

#### Technical Rule: File Locking

**Description**: Exclusive file locks during batch processing
- VSAM file opened in exclusive mode
- Prevents concurrent access during batch
- Online transactions blocked during batch window

**Code References**:
- File: ORDPROC.jcl
- DISP=(OLD,KEEP) for exclusive access

**Legacy Reason**: VSAM file system limitations

**Obsolescence Flag**: Obsolete - Modern databases support concurrent access
```

**Quality Check:**
- [ ] Technical rules documented (not business rules)
- [ ] Code references provided
- [ ] Legacy reasons explained
- [ ] Obsolescence flags assigned

### 12. Logic Extraction Notes

**Purpose**: Document all abstractions applied for Phase 3.1.1 review

**Create separate logic extraction notes file:**

```markdown
# Logic Extraction Notes: WP-XXX

## Abstractions Applied

### DATA_TYPE Abstractions
1. **Field**: ORDER_DATE (PIC X(8))
   - **Abstraction**: Date type
   - **Evidence**: Chapter 6 Section 6.4, CUSTOMER table
   - **Pattern**: DATA_TYPE

2. **Field**: CREDIT_LIMIT (PIC 9(7)V99 COMP-3)
   - **Abstraction**: Numeric (Decimal)
   - **Evidence**: Chapter 6 Section 6.4, CUSTOMER table
   - **Pattern**: DATA_TYPE

### CONSOLIDATION Abstractions
1. **Logic**: Date validation (8 steps)
   - **Abstraction**: "Must be valid date"
   - **Evidence**: Chapter 6 Section 6.2, BR-XXX-002
   - **Pattern**: CONSOLIDATION
   - **Steps Consolidated**: Year validation, month validation, day validation, leap year check, etc.

### NAMING Abstractions
1. **Technical Name**: CUST-REC
   - **Business Name**: Customer
   - **Evidence**: Chapter 6 Section 6.4, CUSTOMER table
   - **Pattern**: NAMING
   - **Glossary Reference**: Business glossary entry "Customer"

2. **Technical Name**: WS-ORDER-AMT
   - **Business Name**: orderTotal
   - **Evidence**: Chapter 6 Section 6.3, F-XXX-001
   - **Pattern**: NAMING
   - **Glossary Reference**: Business glossary entry "Order Total"

### STRUCTURE Abstractions
1. **Technical Structure**: Flat COBOL record CUST-REC
   - **Business Structure**: Customer entity with normalized attributes
   - **Evidence**: Chapter 6 Section 6.4, CUSTOMER table
   - **Pattern**: STRUCTURE

### LOGIC Abstractions
1. **Code Pattern**: IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT
   - **Business Logic**: Orders must not exceed customer credit limits
   - **Evidence**: Chapter 6 Section 6.2, BR-XXX-001
   - **Pattern**: LOGIC

### PROCESS Abstractions
1. **Technical Flow**: PERFORM VALIDATE-CREDIT, PERFORM CHECK-INVENTORY, PERFORM APPROVE-ORDER
   - **Business Process**: Order Validation Process
   - **Evidence**: Chapter 6 Section 6.7, Data Flow Architecture
   - **Pattern**: PROCESS

## Drift Check

### Forbidden Patterns Avoided
- ✅ No functionality added beyond code
- ✅ No entities invented (all entities exist in database)
- ✅ No patterns assumed (all rules have code evidence)
- ✅ No extrapolations beyond code

### Evidence Completeness
- ✅ All abstractions have Chapter 6 references
- ✅ All code references include file names and line numbers
- ✅ All code snippets provided for key logic
- ✅ All database tables documented

## Ready for Phase 3.1.1 Review
- Total Abstractions: [count]
- Allowed Patterns Used: [count by type]
- Forbidden Patterns: 0
- Evidence Completeness: 100%
```

### 13. Quality Assurance

**Before completing Phase 3.1:**

1. **Completeness Check**:
   - [ ] All 8 Chapter 6 sections complete
   - [ ] All source files documented
   - [ ] All database tables documented
   - [ ] All error codes documented
   - [ ] All technical architecture documented
   - [ ] All data flows documented
   - [ ] All technical rules documented

2. **Evidence Check**:
   - [ ] All code references include file names
   - [ ] All code references include line numbers
   - [ ] Code snippets provided for key logic
   - [ ] Database schemas documented
   - [ ] Access patterns documented

3. **Abstraction Check**:
   - [ ] Only allowed patterns applied
   - [ ] No forbidden patterns present
   - [ ] All abstractions documented in logic notes
   - [ ] All abstractions have Chapter 6 evidence

4. **Traceability Check**:
   - [ ] Every abstraction traces to code
   - [ ] Every code section has abstraction
   - [ ] Logic extraction notes complete

### 14. Progress Tracking
- Update progress tracking with completion status
- Document any issues encountered
- Note confidence levels
- Flag areas requiring review attention

---

## Output Format

### Chapter 6 Document (Draft)
**File**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md`
**Note**: This is a draft version that will be reviewed in Phase 3.1.1

**Structure**:
```markdown
# Chapter 6: Legacy Implementation References - WP-XXX

## 6.1 Source Files
[Table of all source files]

## 6.2 Business Rule Implementation
[For each business rule: technical approach, code references, snippets, legacy reason, modern equivalent, migration guidance, obsolescence flag]

## 6.3 Function Implementation
[For each function: technical approach, code references, snippets, technical parameters, legacy reason, modern equivalent, migration guidance, obsolescence flag]

## 6.4 Database Tables
[Table summary and detailed definitions with access patterns, code references, modern equivalent]

## 6.5 Error Codes
[Error sets, treatment codes, custom error codes with references and modern equivalents]

## 6.6 Technical Architecture
[BC Layer, SQLIO Layer, BATCH Layer, Framework with code references and modern equivalents]

## 6.7 Data Flow Architecture
[Input, Database Access, Service Calls, Output, Error Handling with code references and modern equivalents]

## 6.8 Technical Rules (Not Business Rules)
[Technical rules with code references, legacy reasons, obsolescence flags]
```

### Logic Extraction Notes
**File**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md`

---

## Quality Criteria

### Completeness
- All 8 Chapter 6 sections complete
- All source files documented
- All database tables documented
- All error codes documented
- All technical details documented

### Evidence Quality
- Code references specific (file names, line numbers)
- Code snippets complete and accurate
- Database schemas documented
- Access patterns documented
- Technical architecture clear

### Abstraction Quality
- Only allowed patterns applied
- No forbidden patterns present
- All abstractions documented
- All abstractions have evidence

### Traceability
- Every abstraction traces to code
- Every code section documented
- Logic extraction notes complete
- Ready for Phase 3.1.1 review

---

## Error Handling

### Common Error Scenarios

1. **Incomplete Source Code**
   - Detection: Missing files or incomplete sections
   - Recovery: Document gaps in Chapter 6, proceed with available information
   - Escalation: Flag for human review if critical

2. **Ambiguous Business Logic**
   - Detection: Multiple interpretations possible
   - Recovery: Document all interpretations with evidence, flag for Phase 3.1.1 review
   - Escalation: Request clarification if critical

3. **Complex Technical Implementation**
   - Detection: Highly technical code with unclear business intent
   - Recovery: Document technical details completely, note uncertainty in logic notes
   - Escalation: Flag for Phase 3.1.1 review

4. **Missing Database Schema**
   - Detection: Database tables accessed but schema not available
   - Recovery: Infer schema from code, document as "inferred", flag for verification
   - Escalation: Request schema documentation

5. **Temptation to Add Functionality**
   - Detection: Desire to add "obvious" functionality not in code
   - Recovery: DO NOT ADD - document only what exists, note gap in logic notes
   - Escalation: Flag for Phase 3.1.1 review if seems like missing requirement

---

## End of Phase 3.1 Document
