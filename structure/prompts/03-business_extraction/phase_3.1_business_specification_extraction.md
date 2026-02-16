
# Phase 3.1: Business Specification Extraction

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.1 - Business Specification Extraction
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_logic_extraction
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.1_business_specification_extraction.md

### Expected Deliverables

1. **Business Specification Documents**
   - File: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md
   - File: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}.md
   - Template: {{BUSINESS_SPECIFICATION_TEMPLATE}}
   - Description: IEEE 830-1998 formatted business specifications for each workpackage flow (English version)

2. **Progress Tracking**
   - File: {{BUSINESS_SPECIFICATION_STATUS}}
   - Template: {{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}
   - Description: Business extraction progress and status tracking

3. **Review Files**
   - File: {{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md
   - Description: Review documentation for each workpackage (created by reviewer in Phase 3.2)

4. **Error Reports** (if applicable)
   - File: {{BUSINESS_SPECIFICATION_ERRORS}}
   - Template: {{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}
   - Description: Documentation of errors and issues encountered

### Success Criteria
- [ ] All workpackage flows have business specifications created (EN version)
- [ ] All business entities extracted at business concept level (not just cleaned code structures)
- [ ] All business rules identified and cataloged (business policies separated from technical rules)
- [ ] All business functions and processes specified
- [ ] IEEE 830-1998 standard compliance verified
- [ ] Technology-agnostic documentation achieved (Chapters 1-5)
- [ ] Legacy implementation references complete (Chapter 6)
- [ ] Business context from Phase 3.0 incorporated throughout
- [ ] EN and other language versions (if they exist) have identical structure and content
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for Phase 3.2 review

---

## Context

### Input Locations
- **Business context documents**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md`
- **Business glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- **Workpackage definitions**: `{{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/`
- **Source code files**: `{{SOURCE_CODE}}`
- **Database source code**: `{{DATABASE_SOURCE_CODE}}`
- **Database table definitions** (if available)
- **Legacy specifications**: `{{PROJECT_BASE_PATH}}/input/legacy_specifications/`
- **Module dependency table**: `{{DEPENDENCY_ANALYSIS_TABLE}}`

### Output Locations
- **Business specifications (EN)**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md`
- **Business specifications (other)**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}.md`
- **Review files**: `{{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md`
  - **IMPORTANT**: Reviewer creates review files in Phase 3.2, NOT output to STDOUT
- **Reporting**: `{{BUSINESS_SPECIFICATION_REPORTING}}`
- **Progress tracking**: `{{BUSINESS_SPECIFICATION_STATUS}}`
- **Error reports**: `{{BUSINESS_SPECIFICATION_ERRORS}}`
- **Task files location**: `{{TASKS_BASE_PATH}}`

### Template Locations
- **Business specification template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`
- **Status template**: `{{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}`
- **Errors template**: `{{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}`

### Previous Phase Artifacts
- **From Phase 3.0**: Business context documents, business glossary
- **From Phase 1**: Source code analysis, dependency analysis table, module classifications, business flows
- **From Phase 2**: Workpackage definitions with prioritized flows

---

## Objective

Extract business specifications from legacy code using the business context established in Phase 3.0. Create comprehensive IEEE 830-1998 formatted specifications that document business requirements (Chapters 1-5) separately from legacy implementation details (Chapter 6). Focus on extracting business concepts, policies, and processes rather than translating code structures.
On demand, versions for the deliverables in multiple languages might be requested by the user.

**CRITICAL PRINCIPLES**:
1. **Use business context to guide extraction** - Reference Phase 3.0 business context throughout
2. **Extract business concepts, not code structures** - Ask "What business concept does this represent?" not "What are the fields?"
3. **Distinguish business rules from technical rules** - Business rules would exist in any implementation; technical rules are mainframe-specific
4. **Focus on business intent, not implementation patterns** - Document what the business requires, not how the code implements it
5. **Maintain technology-agnostic language in Chapters 1-5** - No COBOL, mainframe, or technical jargon
6. **Preserve full traceability in Chapter 6** - Complete legacy implementation details with code references

---

## Instructions

### 1. Preparation and Context Review
1. Review the workpackage definitions from Phase 2
2. **CRITICAL**: For each workpackage, review the business context document from Phase 3.0:
   - Business domain and capability
   - Business stakeholders
   - Business problem statement
   - Business vocabulary and glossary
   - Business constraints and policies
   - Business outcomes and value
3. Review the consolidated business glossary
4. For each workpackage, in priority order:
   - Identify all relevant source files (programs, copybooks, includes, JCL, maps, etc.)
   - Locate the entry points and end-to-end flows
   - Prepare to extract business specifications using business context as the lens

### 2. Chapter 1: Introduction (Enhanced with Business Context)
1. **Use Phase 3.0 business context to populate Chapter 1**:
   - **Section 1.1 - Purpose**:
     - Business domain and capability (from Phase 3.0)
     - Business problem statement (from Phase 3.0)
     - Business value and outcomes (from Phase 3.0)
   - **Section 1.2 - Scope**:
     - Business stakeholders (from Phase 3.0)
     - Business processes covered
     - Business boundaries (what's included/excluded)
   - **Section 1.3 - Business Context**:
     - Why this functionality exists (from Phase 3.0)
     - Business constraints and policies (high-level from Phase 3.0)
     - Business vocabulary reference (link to glossary)

2. Write Chapter 1 from business perspective:
   - Use business terminology from Phase 3.0 glossary
   - Focus on business needs and value
   - Avoid technical implementation details
   - Make it readable by business analysts who have never seen the code

### 3. Chapter 2: Business Entity Extraction (Business Concept Level)
1. **CRITICAL**: Extract business entities at the business concept level, not code structure level:
   - **Ask**: "What real-world business concept does this data structure represent?"
   - **Not**: "What are the fields in this COBOL record?"

2. For each identified business entity:
   - **Use business vocabulary from Phase 3.0 glossary**
   - **Identify business entity name**: Use business terms (Customer, Order, Payment) not technical terms (CUST-REC, ORD-FILE)
   - **Extract business attributes**: Use business attribute names from glossary (creditLimit, orderTotal, paymentStatus)
   - **Convert variable names to camelCase** following these rules:
     1. Remove program-specific prefixes (e.g., XDIPA501-, WS-, LS-, etc.)
     2. Remove direction indicators (I-, O-, IO-)
     3. Convert remaining hyphenated parts to camelCase
     4. Examples: XDIPA501-I-CORP-CLCT-GROUP-CD → corpClctGroupCd, WS-CUSTOMER-NAME → customerName
   - **Use generic data types**: String, Numeric, Date, Timestamp, Boolean (not COBOL-specific types)
   - **Provide "N/A" as data length** for data objects (Date, Timestamp, Boolean), but keep the length for concrete data types (String, Numeric)
   - **Intelligently convert data types** to the most appropriate ones for the task (e.g., use Date with Length "N/A" instead of a String for 'YYYYMMDD')
   - **Document business validation rules** (not technical constraints like buffer sizes)
   - **Align with database table definitions** when available
   - **Assign unique identifiers** using BE-{workpackageID}-XXX numbering system (e.g., BE-001-001)

3. **Business entity relationships**:
   - Document business relationships (Customer HAS-MANY Orders, Order HAS-ONE Payment)
   - Use business terms to describe relationships
   - Focus on business meaning, not technical foreign keys

4. **Distinguish business attributes from technical attributes**:
   - **Business attributes**: Represent business concepts (creditLimit, orderDate, customerName)
   - **Technical attributes**: Implementation details (recordLength, bufferSize, lockFlag)
   - Document business attributes in Chapter 2
   - Document technical attributes in Chapter 6 (Legacy Implementation)

### 4. Chapter 3: Business Rule Extraction (Business Policy Level)
1. **CRITICAL**: Extract business rules that represent business policies, not code patterns:
   - **Ask**: "What business decision or policy is being enforced and why?"
   - **Not**: "What conditional logic exists in the code?"

2. **Use business context from Phase 3.0 to interpret rule intent**:
   - Reference business constraints and policies from Phase 3.0
   - Use business vocabulary from glossary
   - Focus on business rationale, not technical implementation

3. For each flow in the workpackage:
   - **Identify business decisions**: What business decision is being made?
   - **Extract business constraints**: What business policy is being enforced?
   - **Document business conditions**: When does this rule apply? (in business terms)
   - **Document business actions**: What happens when the rule is triggered? (in business terms)
   - **Document business rationale**: Why does this rule exist? (if discernible from context or comments)
   - **Include business constants**: Credit limits, thresholds, business dates (not technical constants like buffer sizes, timeouts)

4. **Business rule format** (WHEN/THEN structure):
   ```
   BR-{workpackageID}-XXX: [Business Rule Name]

   WHEN: [Business condition in business terms]
   THEN: [Business action in business terms]
   RATIONALE: [Why this rule exists - business reason]
   RELATED ENTITIES: [Business entities involved]
   EXCEPTION HANDLING: [Business exceptions and how they're handled]
   ```

5. **Distinguish business rules from technical rules**:
   - **Business rules**: Would exist in any implementation (credit limits, validation rules, approval workflows)
     - Example: "Orders must not be accepted if the total order value exceeds the customer's available credit limit"
   - **Technical rules**: Specific to mainframe implementation (batch restart logic, file locking, CICS transaction timeouts)
     - Example: "If CICS transaction times out after 30 seconds, rollback and retry"
   - **Document business rules in Chapter 3**
   - **Document technical rules in Chapter 6** (Legacy Implementation)

6. **Business rule abstraction level**:
   - **Too concrete** (code-level): "If customer credit limit field is less than order amount field, reject transaction"
   - **Too abstract** (useless): "System must validate customer eligibility"
   - **Right level** (business requirement): "Orders must not be accepted if the total order value exceeds the customer's available credit limit. Available credit = Credit Limit - Outstanding Balance."

7. **Assign unique identifiers** using BR-{workpackageID}-XXX numbering system (e.g., BR-001-001)

### 5. Chapter 4: Business Function Identification (Business Capability Level)
1. **CRITICAL**: Extract business functions that represent business capabilities, not program subroutines:
   - **Ask**: "What business capability or operation does this perform?"
   - **Not**: "What does this PERFORM paragraph do?"

2. For each flow in the workpackage:
   - **Identify business functions**: Cohesive units of business functionality
   - **Use business vocabulary**: Function names should use business terms from glossary
   - **Document business inputs**: What business information is required? (not technical parameters)
   - **Document business outputs**: What business information is produced? (not technical return codes)
   - **Document business processing logic**: What business operations are performed? (in business terms)
   - **Map relationships to business rules**: Which business rules apply to this function?
   - **Assign unique identifiers** using F-{workpackageID}-XXX numbering system (e.g., F-001-001)

3. **Business function format**:
   ```
   F-{workpackageID}-XXX: [Business Function Name]

   PURPOSE: [What business capability this provides]
   BUSINESS INPUTS: [Business information required]
   BUSINESS OUTPUTS: [Business information produced]
   BUSINESS PROCESSING: [Business operations performed - in business terms]
   BUSINESS RULES APPLIED: [List of BR-XXX identifiers]
   RELATED ENTITIES: [Business entities involved]
   BUSINESS EXCEPTIONS: [Business error conditions and handling]
   ```

4. **Focus on business operations, not technical implementation**:
   - **Good**: "Validate customer credit eligibility by comparing order total against available credit"
   - **Bad**: "Call VALIDATE-CREDIT subroutine passing WS-CREDIT-LIM and WS-ORDER-AMT"

### 6. Chapter 5: Process Flow Extraction (Business Process Level)
1. **CRITICAL**: Extract business process flows, not program call graphs:
   - **Ask**: "What business process is being executed and what are the business activities?"
   - **Not**: "What is the sequence of PERFORM statements?"

2. For each flow in the workpackage:
   - **Identify business process**: What business process is being implemented? (from Phase 3.0 context)
   - **Extract business activities**: What business operations occur? (not program calls)
   - **Identify business decision points**: Where are business decisions made? (not IF statements)
   - **Document business actors**: Who performs each activity? (from Phase 3.0 stakeholders)
   - **Describe business events**: What triggers the process? What are the outcomes?

3. **Business process flow format** (text-based):
   ```
   Process: [Business Process Name]

   Trigger: [Business event that starts the process]

   Activities:
   1. [Business Activity 1] - Performed by [Business Actor]
      - Decision Point: [Business decision if applicable]
      - If [business condition]: [business action]
      - If [business condition]: [business action]

   2. [Business Activity 2] - Performed by [Business Actor]
      - Uses: [Business entities/functions]
      - Produces: [Business outputs]

   3. [Business Activity 3] - Performed by [Business Actor]

   Outcomes:
   - Success: [Business outcome when successful]
   - Failure: [Business outcome when failed]

   Business Value: [What business value this process delivers]
   ```

4. **Use business vocabulary throughout**:
   - Business activities (not program names)
   - Business decision points (not conditional statements)
   - Business actors (not transaction codes)
   - Business outcomes (not return codes)

### 7. Chapter 6: Legacy Implementation References (Comprehensive Technical Details)
1. **CRITICAL**: Chapter 6 contains ALL technical implementation details:
   - This is where you document HOW the legacy system implements the business requirements
   - Use technical terminology and code references
   - Provide complete traceability to source code

2. **Section 6.1: Source Files**
   - List all source files involved (programs, copybooks, includes, JCL, maps)
   - Provide file paths and descriptions
   - Note file types and purposes

3. **Section 6.2: Business Rule Implementation**
   - For each business rule (BR-XXX) from Chapter 3:
     - **Legacy Technical Approach**: How the rule is implemented in legacy code
     - **Code References**: Specific source files, line numbers, and code snippets
     - **Legacy Reason**: Why this technical approach was used (mainframe constraints, performance, etc.)
     - **Technical Constants**: Buffer sizes, timeouts, technical thresholds
     - **Modern Cloud-Native Equivalent**: How this would be implemented in modern architecture
     - **Migration Guidance**: Specific guidance for modernizing this rule
     - **Obsolescence Flag**: Is this rule obsolete or still needed?

4. **Section 6.3: Function Implementation**
   - For each business function (F-XXX) from Chapter 4:
     - **Legacy Technical Approach**: How the function is implemented (COBOL paragraphs, subroutines)
     - **Code References**: Specific source files, line numbers, and code snippets
     - **Technical Parameters**: COBOL-specific parameters, working storage variables
     - **Legacy Reason**: Why this technical approach was used
     - **Modern Cloud-Native Equivalent**: How this would be implemented as a microservice/function
     - **Migration Guidance**: Specific guidance for modernizing this function
     - **Obsolescence Flag**: Is this function obsolete or still needed?

5. **Section 6.4: Database Tables**
   - For each database table accessed:
     - **Table Name**: Physical table name
     - **Table Type**: Internal, Common, or External
     - **Columns**: Column names, data types, constraints
     - **Access Patterns**: How the legacy code accesses the table (SQL, embedded SQL, file I/O)
     - **Code References**: Where table is accessed in source code
     - **Modern Equivalent**: How this would be modeled in modern database (DynamoDB, RDS, etc.)

6. **Section 6.5: Error Codes**
   - **Error Sets**: Groupings of related errors
   - **Treatment Codes**: How errors are handled in legacy system
   - **Custom Error Codes**: Application-specific error codes
   - **Code References**: Where errors are raised and handled
   - **Modern Equivalent**: How errors would be handled in modern architecture (exceptions, logging, monitoring)

7. **Section 6.6: Technical Architecture**
   - **BC Layer**: Business component layer details
   - **SQLIO Layer**: Database access layer details
   - **BATCH Layer**: Batch processing details
   - **Framework**: Framework components used
   - **Code References**: Where each layer is implemented
   - **Modern Equivalent**: How this would be architected in cloud-native design

8. **Section 6.7: Data Flow Architecture**
   - **Input**: How data enters the system (screens, files, messages)
   - **Database Access**: How data is read/written to databases
   - **Service Calls**: External system integrations
   - **Output**: How data exits the system (screens, files, reports)
   - **Error Handling**: Technical error handling mechanisms
   - **Code References**: Where each data flow is implemented
   - **Modern Equivalent**: How data would flow in modern architecture (APIs, event streams, etc.)

9. **Technical rule documentation** (rules that are NOT business rules):
   - Batch restart logic
   - File locking mechanisms
   - CICS transaction management
   - Buffer management
   - Technical workarounds for mainframe constraints
   - **Code References**: Where implemented
   - **Obsolescence Flag**: Mark as obsolete if not needed in modern architecture

### 8. Technology-Agnostic Documentation (Chapters 1-5)
1. **CRITICAL**: Ensure Chapters 1-5 are completely technology-agnostic:
   - **No references to**: COBOL, CICS, JCL, DB2, mainframe, batch, online, transaction, file, record, paragraph, PERFORM, MOVE, CALL, etc.
   - **Use instead**: Business terms from Phase 3.0 glossary
   - **Focus on**: Business requirements, business policies, business processes, business entities, business rules

2. **Test for technology-agnosticism**:
   - Could a business analyst who has never seen COBOL understand Chapters 1-5?
   - Could these requirements be implemented in Python, Java, or any other language?
   - Are all business concepts described in business terms?

3. **Preserve business logic without technical constraints**:
   - Document what the business requires, not how mainframe implements it
   - Remove technical workarounds and constraints from business requirements
   - Focus on business intent and outcomes

### 9. Bilingual Documentation (English and other language on demand)
1. **Create EN version** for each workpackage:
   - `WP-XXX-FLOW_XXX-specification-EN.md` (English)
   - `WP-XXX-FLOW_XXX-specification-{LANGUAGE SHORTFORM}.md` (English)

2. **Ensure identical structure and content**:
   - Same number of business entities (BE-XXX)
   - Same number of business rules (BR-XXX)
   - Same number of business functions (F-XXX)
   - Same business logic and requirements
   - Same Chapter 6 technical details

3. **Foreign terminology alongside English**:
   - Use format: "English Term (Foreign language TERM)"
   - Example: "Creation Initials (SKABELSESINITIALER)"
   - Maintain consistency with existing foreign language business vocabulary

4. **Translate business concepts, not technical terms**:
   - Business terms should be translated
   - Technical terms in Chapter 6 can remain in English (COBOL, CICS, etc.)
   - Code snippets remain in original language

### 10. Validation and Completeness Check
1. For each completed business specification:
   - **Chapter 1**: Business context from Phase 3.0 incorporated
   - **Chapter 2**: Business entities at business concept level (not code structures)
   - **Chapter 3**: Business rules represent business policies (technical rules in Chapter 6)
   - **Chapter 4**: Business functions represent business capabilities
   - **Chapter 5**: Business process flows use business terminology
   - **Chapter 6**: Complete legacy implementation details with code references
   - **Technology-agnostic**: Chapters 1-5 have no technical jargon
   - **Traceability**: All business requirements traced to legacy code in Chapter 6
   - **Bilingual**: EN and other language versions (if they exist) have identical structure and content

2. **Cross-reference with Phase 3.0 business context**:
   - Business domain matches Phase 3.0
   - Business stakeholders documented in Chapter 1
   - Business vocabulary from glossary used throughout
   - Business constraints from Phase 3.0 reflected in business rules
   - Business outcomes from Phase 3.0 reflected in process flows

3. **Verify business vs technical separation**:
   - All business requirements in Chapters 1-5
   - All technical implementation in Chapter 6
   - No technical jargon in Chapters 1-5
   - Complete technical details in Chapter 6

### 11. Progress Tracking
1. Update progress tracking for each completed workpackage:
   - Record completion status and artifacts
   - Document any issues or exceptions
   - **ENSURE reviewer creates review file in `{{BUSINESS_SPECIFICATION_REVIEW}}` directory in Phase 3.2**
   - Update phase status in progress tracking system
   - Note confidence levels and areas requiring BA input

### 12. Quality Assurance
1. Before marking workpackage as complete:
   - Run technology-agnostic test on Chapters 1-5
   - Verify all business entities use business vocabulary from Phase 3.0
   - Verify all business rules represent business policies (not code patterns)
   - Verify all business functions represent business capabilities (not subroutines)
   - Verify Chapter 6 has complete technical details with code references
   - Verify EN and other versions are identical in structure and content
   - Verify all BE-XXX, BR-XXX, F-XXX identifiers are unique and sequential

### 13. Pause Before Progressing to Next Workpackage
- Do not proceed to next workpackage until current workpackage is complete and validated
- Ensure both EN and other versions are created
- Ensure specification is ready for Phase 3.2 review

---

## Output Format

### Business Specification Document (English)
**File**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md`
**Template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`

**Structure** (6 Chapters):
1. **Introduction** (Enhanced with Phase 3.0 business context)
2. **Business Entities** (Business concept level with BE-XXX identifiers)
3. **Business Rules** (Business policy level with BR-XXX identifiers)
4. **Business Functions** (Business capability level with F-XXX identifiers)
5. **Process Flows** (Business process level in text format)
6. **Legacy Implementation References** (Comprehensive technical details)

### Business Specification Document (other language)
**File**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}.md`
**Template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`

**Structure**: Identical to English version with translations

### Progress Tracking
**File**: `{{BUSINESS_SPECIFICATION_STATUS}}`
**Template**: `{{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}`

### Error Reports
**File**: `{{BUSINESS_SPECIFICATION_ERRORS}}`
**Template**: `{{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}`

---

## Quality Criteria

### IEEE Standard Compliance
- Document follows IEEE 830-1998 Software Requirements Specification format
- All sections are properly numbered and structured
- Document control information is complete and accurate
- Requirements are uniquely identified and traceable (BE-XXX, BR-XXX, F-XXX)

### Business Context Integration
- Chapter 1 incorporates business context from Phase 3.0
- Business domain, stakeholders, and problem statement clearly documented
- Business vocabulary from Phase 3.0 glossary used throughout
- Business constraints and policies from Phase 3.0 reflected in business rules

### Business Entity Quality
- Entities represent business concepts (not code structures)
- Entity names use business vocabulary from Phase 3.0 glossary
- Attributes are business-meaningful (not technical fields)
- Generic data types used (String, Numeric, Date, Timestamp, Boolean)
- Variable names converted to camelCase (removing prefixes: XDIPA501-, WS-, LS-, I-, O-, IO-)
- Business validation rules documented (not technical constraints)
- Unique BE-XXX identifiers assigned

### Business Rule Quality
- Rules represent business policies (not code patterns)
- Rules are described in business terms using Phase 3.0 vocabulary
- Each rule has clear WHEN/THEN format with business rationale
- Business rules distinguished from technical rules (technical rules in Chapter 6)
- Business constants included (credit limits, thresholds) not technical constants (buffer sizes)
- Unique BR-XXX identifiers assigned
- Rules are specific enough to be testable but abstract enough to be implementation-independent

### Business Function Quality
- Functions represent business capabilities (not program subroutines)
- Function names use business vocabulary from Phase 3.0 glossary
- Inputs/outputs described in business terms (not technical parameters)
- Processing logic described in business terms (not code implementation)
- Relationships to business rules clearly mapped
- Unique F-XXX identifiers assigned

### Business Process Quality
- Process flows represent business processes (not program call graphs)
- Activities described in business terms (not program names)
- Decision points are business decisions (not IF statements)
- Actors are business roles from Phase 3.0 stakeholders (not transaction codes)
- Outcomes described in business terms (not return codes)
- Business value clearly articulated

### Technology Independence (Chapters 1-5)
- No references to COBOL, CICS, JCL, DB2, mainframe, or technical jargon
- Business logic described without implementation details
- Generic business terminology used throughout
- Business intent clearly separated from implementation approach
- Readable by business analysts who have never seen the code

### Legacy Implementation Completeness (Chapter 6)
- All technical implementation details documented
- Code references include specific file names and line numbers
- Code snippets provided for key implementations
- Database tables documented with access patterns
- Error codes and handling documented
- Technical architecture layers documented
- Data flow architecture documented
- Legacy reason and modern equivalent provided for each component
- Obsolescence flags assigned
- Technical rules (not business rules) documented

### Traceability
- Each business entity traced to legacy data structures in Chapter 6
- Each business rule traced to legacy implementation in Chapter 6
- Each business function traced to legacy code in Chapter 6
- Source file references include specific line numbers
- All legacy functionality accounted for in business specifications
- Clear mapping between business requirements (Chapters 1-5) and legacy implementation (Chapter 6)

### Bilingual Consistency
- EN and other versions have identical structure
- Same number of BE-XXX, BR-XXX, F-XXX identifiers
- Same business logic and requirements
- Foreign language terminology alongside English where appropriate
- Both versions complete and validated

---

## Error Handling

### Common Error Scenarios

1. **Incomplete Legacy Code**
   - Detection: Missing files or incomplete code sections
   - Recovery: Document the gap in Chapter 6 and proceed with available information
   - Escalation: Flag for human review if critical business functionality is affected

2. **Ambiguous Business Logic**
   - Detection: Multiple interpretations of code logic possible
   - Recovery: Use Phase 3.0 business context to guide interpretation; document all possible interpretations with confidence levels
   - Escalation: Request human clarification for critical business rules

3. **Complex Technical Implementation**
   - Detection: Highly technical code with unclear business intent
   - Recovery: Focus on observable behavior and inputs/outputs; use Phase 3.0 business context to infer intent
   - Escalation: Flag for expert review if business intent cannot be determined

4. **Missing Database Definitions**
   - Detection: Unable to align with database table definitions
   - Recovery: Create entity definitions based on code usage patterns and Phase 3.0 business vocabulary
   - Escalation: Document assumptions made and flag for validation

5. **Business vs Technical Rule Ambiguity**
   - Detection: Unclear whether a rule is business policy or technical constraint
   - Recovery: Use Phase 3.0 business context to determine; if still unclear, document in both Chapter 3 and Chapter 6 with note
   - Escalation: Flag for BA review in Phase 3.2

6. **Missing Business Context**
   - Detection: Phase 3.0 business context document incomplete or missing
   - Recovery: Proceed with code analysis but document lower confidence level
   - Escalation: Flag for BA review and request Phase 3.0 completion

7. **Bilingual Translation Issues**
   - Detection: Difficulty translating business concepts to foreign language
   - Recovery: Use English term with foreign language equivalent in parentheses
   - Escalation: Flag for native foreign language speaker review

### Error Reporting Format
**File**: `{{BUSINESS_SPECIFICATION_ERRORS}}`
**Template**: `{{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}`

**Structure**:
```markdown
# Business Specification Extraction Errors - WP-XXX

## Error 1: [Error Type]
- **Workpackage**: WP-XXX
- **Chapter Affected**: [1-6]
- **Severity**: High/Medium/Low
- **Description**: [What went wrong]
- **Impact**: [How this affects the specification]
- **Recovery Action**: [What was done]
- **Requires BA Input**: Yes/No
- **Status**: Open/Resolved
```

### Fallback Strategies
- When business context is incomplete, use code patterns and naming to infer business intent
- When business vs technical distinction is unclear, document in both locations with cross-reference
- When business vocabulary is missing, create reasonable business terms and flag for BA validation
- Focus on completing specifications over perfect accuracy
- Flag all uncertainties for Phase 3.2 review
- Prioritize business requirements extraction over technical details
- Use Phase 3.0 business context as primary guide for all extraction decisions

---

## End of Phase 3.1 Document
