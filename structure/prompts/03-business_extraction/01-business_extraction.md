# Phase 3.1: Business Extraction

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.1 - Business Logic Extraction
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_logic_extraction
**Task File Name**: {{TASKS_BASE_PATH}}/business_extraction_specialist_task.md

### Expected Deliverables

1. **Business Specification Documents**
   - File: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md
   - Template: {{BUSINESS_SPECIFICATION_TEMPLATE}}
   - Description: IEEE-formatted business specifications for each workpackage flow

2. **Progress Tracking**
   - File: {{BUSINESS_SPECIFICATION_STATUS}}
   - Template: {{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}
   - Description: Business extraction progress and status tracking

3. **Review Files**
   - File: {{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md
   - Description: Review documentation for each workpackage (created by reviewer)

4. **Error Reports** (if applicable)
   - File: {{BUSINESS_SPECIFICATION_ERRORS}}
   - Template: {{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}
   - Description: Documentation of errors and issues encountered

### Success Criteria
- [ ] All workpackage flows have business specifications created
- [ ] All business entities extracted and documented
- [ ] All business rules identified and cataloged
- [ ] All business functions specified
- [ ] IEEE standard compliance verified
- [ ] Technology-agnostic documentation achieved
- [ ] Legacy implementation references complete
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for review

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: Extract business rules, entities, and functions from legacy code
- **Detailed instructions**: All Steps 1-10 below (Preparation, Business Entity Extraction, Business Rule Extraction, etc.)
- **Technical specifications**: IEEE 830-1998 format, generic data types, camelCase naming conventions
- **Business rules and constraints**: Technology-agnostic documentation, no invented rules, exact legacy code matching
- **Error handling guidance**: Incomplete legacy code, ambiguous business logic, complex technical implementation
- **Output format requirements**: Business specification documents, progress tracking
- **Quality criteria**: IEEE compliance, business rule quality, entity completeness, technology independence, traceability

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Workpackage definitions: {{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/
  - Source code files: {{SOURCE_CODE}}
  - Database source code: {{DATABASE_SOURCE_CODE}}
  - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
  - Module dependency table: {{DEPENDENCY_ANALYSIS_TABLE}}
- **All output locations** (resolved paths):
  - Business specifications: {{BUSINESS_SPECIFICATION_BASE_PATH}}
  - Review files: {{BUSINESS_SPECIFICATION_REVIEW}}
  - Reporting: {{BUSINESS_SPECIFICATION_REPORTING}}
  - Progress tracking: {{BUSINESS_SPECIFICATION_STATUS}}
  - Error reports: {{BUSINESS_SPECIFICATION_ERRORS}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Business specification template: {{BUSINESS_SPECIFICATION_TEMPLATE}}
  - Status template: {{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}
  - Errors template: {{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: business_specialist_logic_extraction
- **Agent definition file**: structure/agents/business_team/business_specialist_logic_extraction.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations (Phase 1 and Phase 2 outputs), output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-10), business rules, error handling
- **Expected Deliverables**: All 4 deliverables with paths, templates, descriptions, validation checklists
- **Quality Criteria**: IEEE compliance, business rule quality, entity completeness, technology independence, traceability
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

### 6. Dependencies from previous phases:
This step requires outputs from Phase 1 (Analysis) and Phase 2 (Workpackage Planning):
- **From Phase 1**: Source code analysis, dependency analysis table, module classifications, business flows
- **From Phase 2**: Workpackage definitions with prioritized flows
- Verify these artifacts exist before creating the task file

---

## Context
- Project Structure: Standard migration project folder structure

## Context
- Input Location:
  -- Prioritized migration roadmap: `{{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/` 
  -- Directories with source code files: `{{SOURCE_CODE}}` 
  -- Directory with database related source code: `{{DATABASE_SOURCE_CODE}}`
  -- Database table definitions (if available)
  -- Legacy framework documentation: `{{PROJECT_BASE_PATH}}/input/legacy_specifications/` 


- Output Location:
  -- IEEE-formatted business specifications: `{{BUSINESS_SPECIFICATION_BASE_PATH}}`
    --- English versions: `WP-XXX-FLOW_XXX-specification-EN.md`
  -- Review: `{{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md``
     --- (IMPORTANT: **Reviewer must create review files, NOT output to STDOUT**)
  -- Reporting: `{{BUSINESS_SPECIFICATION_REPORTING}}`
  -- Module Dependency Table: `{{DEPENDENCY_ANALYSIS_TABLE}}`
  -- Progress Tracking: `{{BUSINESS_SPECIFICATION_STATUS}}`
  -- Location of task-related files: `{{TASKS_BASE_PATH}}` 


- Previous Phase Artifacts:
  - Workpackage definitions with prioritized flows
  - Source code analysis with module classifications
  - Dependency graphs and business domain assignments
 
## Objective
Extract business rules, entities, and functions from legacy code in a technology-agnostic format following IEEE documentation standards. Create comprehensive business specifications that preserve all business logic while separating it from implementation details. **IMPORTANT** Do not invent business rules that do not exist in the code. 
 
## Instructions
 
### 1. Preparation
1. Review the workpackage definitions from Phase 2
2. For each workpackage, in priority order:
   - Identify all relevant source files (programs, copybooks, includes, JCL, maps, etc.)
   - Determine the business domain assignment
   - Locate the entry points and end-to-end flows
 
### 2. Business Entity Extraction
1. For each identified business entity:
   - Extract complete attribute definitions in a programming language-agnostic way
   - Use generic data types (String, Numeric, Date, Timestamp) instead of language-specific types
   - Provide "N/A" as data length for data objects (Date, TimeStamp, Boolean), but keep the length for concrete data types (String, Numeric) 
   - Intelligently "convert" the data types to the most apropriate ones for the task (eg use Date with Length "N/A" instead of a String for 'YYYYMMDD')
  
   - **Extract variable names**: Convert variable names to camelCase following these rules:
     1. Remove program-specific prefixes (e.g., XDIPA501-, WS-, LS-, etc.)
     2. Remove direction indicators (I-, O-, IO-)
     3. Convert remaining hyphenated parts to camelCase
     4. Examples: XDIPA501-I-CORP-CLCT-GROUP-CD → corpClctGroupCd, WS-CUSTOMER-NAME → customerName
   - Document validation rules and constraints.
   - Align data types with database table definitions when available
   - Assign unique identifiers using BE-XXX numbering system (e.g., BE-{workpackageID}-001)
 
### 3. Business Rule Extraction
1. For each flow in the workpackage:
   - Identify conditional logic that represents business decisions
   - Extract calculation formulas and algorithms
   - Document validation rules and constraints
   - Identify error handling specific to business requirements
   - Assign unique identifiers using BR-XXX numbering system (e.g., BR-{workpackageID}-001)
 
### 4. Business Function Identification
1. For each flow in the workpackage:
   - Identify cohesive units of business functionality
   - Document inputs, outputs, and processing logic
   - Map relationships between functions and business rules
   - Assign unique identifiers using F-XXX numbering system (e.g., F-{workpackageID}-001)
 
### 5. IEEE-Compliant Documentation Creation
1. **MANDATORY**: For each workpackage, create a business specification documents:


 
2. Both documents must include identical content structure:
   - Document control information (version, date, author, standard compliance)
   - Table of contents with section numbering
   - Introduction and purpose
   - Business entity definitions with validation rules
   - Business rule catalog with detailed descriptions
   - Business function specifications
   - Process flow diagrams in text format
   - Legacy implementation references (Chapter 6 only)
 
### 6. Technology-Agnostic Documentation
1. Ensure all business specifications are technology-agnostic:
   - Remove references to specific programming languages
   - Replace technical implementation details with business concepts
   - Use standard business terminology instead of technical jargon
   - Document business intent rather than implementation approach
   - Preserve all business logic without technical constraints
 
### 7. Legacy Implementation References
1. In Chapter 6 of each specification document:
   - Document technical details of the legacy implementation
   - Include references to specific source code files and line numbers
   - Map business rules to their legacy code implementations
   - Document any technical constraints or limitations
   - Preserve traceability between business rules and legacy code
 
### 8. Validation and Completeness Check
1. For each completed business specification:
   - Verify all business rules are documented
   - Ensure all business entities have complete definitions
   - Validate that all business functions are specified
   - Check that all legacy code functionality is represented
   - Confirm traceability to legacy implementation
   - **Verify EN and DN versions have identical structure and content (same BE/BR/F counts and logic)**
 
### 9. Progress Tracking
1. Update progress tracking for each completed workpackage:
   - Record completion status and artifacts
   - Document any issues or exceptions
   - **ENSURE reviewer creates review file in `{{BUSINESS_SPECIFICATION_REVIEW}}` directory**
   - Update phase status in progress tracking system

### 10. Pause before progressing to next workpackage
 
## Output Format
### Business Specification Document 
**File**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md`
**Template for the file**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`
 
 
### 6. Progress Tracking
**File**: `{{BUSINESS_SPECIFICATION_STATUS}}`
**Template for the file**: `{{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}`
 
## Quality Criteria
 
### IEEE Standard Compliance
- Document follows IEEE 830-1998 Software Requirements Specification format
- All sections are properly numbered and structured
- Document control information is complete and accurate
- Requirements are uniquely identified and traceable
 
### Business Rule Extraction Quality
- All conditional logic from legacy code is captured as business rules
- Business rules must include all constants and hardcoded values from legacy code
- Rules are described in technology-agnostic language
- Each rule has a clear condition-action format
- Rules are uniquely identified with BR-XXX numbering
 
### Business Entity Completeness
- All data structures from legacy code are represented as business entities
- Entities use generic data types instead of language-specific types
- All attributes are documented with proper descriptions
- Validation rules for entities are clearly specified
 
### Technology Independence
- No references to specific programming languages (except in Chapter 6)
- Business logic is described without implementation details
- Generic terminology is used instead of technical jargon
- Business intent is clearly separated from implementation approach
 
### Traceability
- Each business rule is linked to its legacy implementation
- Source file references include specific line numbers
- All legacy functionality is accounted for in business specifications
- Clear mapping between business entities and legacy data structures
- Extracted business entities, rules, and flows must exactly match legacy code implementation
 
 
## Error Handling
 
### Common Error Scenarios
 
1. **Incomplete Legacy Code**
   - Detection: Missing files or incomplete code sections
   - Recovery: Document the gap and proceed with available information
   - Escalation: Flag for human review if critical functionality is affected
 
2. **Ambiguous Business Logic**
   - Detection: Multiple interpretations of code logic possible
   - Recovery: Document all possible interpretations with confidence levels
   - Escalation: Request human clarification for critical business rules
 
3. **Complex Technical Implementation**
   - Detection: Highly technical code with unclear business intent
   - Recovery: Focus on observable behavior and inputs/outputs
   - Escalation: Flag for expert review if business intent cannot be determined
 
4. **Missing Database Definitions**
   - Detection: Unable to align with database table definitions
   - Recovery: Create entity definitions based on code usage patterns
   - Escalation: Document assumptions made and flag for validation
 

### Error Reporting Format
**File**: `{{BUSINESS_SPECIFICATION_ERRORS}}`
**Template for the file**: `{{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}`
 
### Fallback Strategies
- Focus on observable behavior when implementation details are unclear
- Document assumptions and confidence levels for ambiguous rules
- Use simplified entity models when complete definitions cannot be extracted
- Prioritize business rule extraction over technical details
- Flag areas requiring human expert review