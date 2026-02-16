# Phase 3.3: Test Generation (Service-Based)

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.3 - Test Case Generation (Service-Based)
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_test_design
**Task File Name**: {{TASKS_BASE_PATH}}/test_generation_service_specialist_task.md

### Expected Deliverables

1. **Test Case Definition Documents**
   - File: {{TEST_GENERATION_SERVICE_BASE_PATH}}/S-XXX-[service-name]-tests.md
   - Template: {{TEST_CASE_DEFINITION_SERVICE_TEMPLATE}}
   - Description: IEEE 829 standard test case definitions for each service

2. **Progress Tracking**
   - File: {{TEST_GENERATION_SERVICE_STATUS}}
   - Template: {{TEST_GENERATION_SERVICE_STATUS_TEMPLATE}}
   - Description: Test generation progress and status tracking

3. **Error Reports** (if applicable)
   - File: {{TEST_GENERATION_SERVICE_ERRORS}}
   - Template: {{TEST_GENERATION_SERVICE_ERRORS_TEMPLATE}}
   - Description: Documentation of errors and issues encountered

### Success Criteria
- [ ] All services have test case definitions created
- [ ] Every function has at least one test case
- [ ] Every entity has validation test cases
- [ ] All positive, negative, and boundary conditions tested
- [ ] Cross-service interactions have dedicated test cases
- [ ] IEEE 829 standard compliance verified
- [ ] Language-independent test definitions achieved
- [ ] Complete traceability to business specifications
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for review

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: Generate language-independent test case definitions from business requirements
- **Detailed instructions**: All Steps 1-11 below (Test Planning, Function Coverage, Entity Coverage, Positive/Negative/Boundary Scenarios, etc.)
- **Technical specifications**: IEEE 829 standard structure, service-based organization, test prioritization
- **Business rules and constraints**: Language-agnostic format, comprehensive coverage, traceability requirements
- **Error handling guidance**: Incomplete function coverage, ambiguous test expectations, missing test data, cross-service inconsistencies
- **Output format requirements**: Test case definition documents, progress tracking, error reports
- **Quality criteria**: Test coverage quality, test case quality, traceability quality, IEEE compliance, language independence

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Business specifications: {{BUSINESS_SPECIFICATION_BASE_PATH}}/business/
  - Workpackage definitions: {{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/
  - Domain consolidation specs: {{DOMAIN_CONSOLIDATION_BASE_PATH}}
- **All output locations** (resolved paths):
  - Test case definitions: {{TEST_GENERATION_SERVICE_BASE_PATH}}
  - Progress tracking: {{TEST_GENERATION_SERVICE_STATUS}}
  - Error reports: {{TEST_GENERATION_SERVICE_ERRORS}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Test case definition template: {{TEST_CASE_DEFINITION_SERVICE_TEMPLATE}}
  - Status template: {{TEST_GENERATION_SERVICE_STATUS_TEMPLATE}}
  - Errors template: {{TEST_GENERATION_SERVICE_ERRORS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: business_specialist_test_design
- **Agent definition file**: structure/agents/business_team/business_specialist_test_design.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations (Phase 3 business specifications), output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-11), business rules, error handling
- **Expected Deliverables**: All 3 deliverables with paths, templates, descriptions, validation checklists
- **Quality Criteria**: Test coverage quality, test case quality, traceability quality, IEEE compliance, language independence
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

### 6. Dependencies from previous phases:
This step requires outputs from Phase 3 Steps 3.1 and 3.2:
- **From Step 3.1**: Business specifications with functions and entities
- **From Step 3.2**: Domain consolidation specifications (if applicable)
- Verify these artifacts exist before creating the task file

---

## Context
- Input Location: 
  - `{{BUSINESS_SPECIFICATION_BASE_PATH}}/business/` - Business Requirements documentation
- Output Location: 
  - `{{TEST_GENERATION_SERVICE_BASE_PATH}}` - Language-agnostic test definitions
  - `{{TEST_GENERATION_SERVICE_STATUS}}` - Phase completion tracking
  - `{{TEST_GENERATION_SERVICE_ERRORS}}` - Error log

## Objective
Generate programming language-independent test case definitions from business requirements that cover all services, functions, and entities. Create comprehensive test scenarios including positive, negative, and boundary test cases while maintaining full traceability to business specifications. Organize test cases by service and priority to facilitate systematic validation of migrated functionality against original business requirements.

## Instructions

### 1. Test Planning and Organization
1. Review all business requirements documents
2. For each service specified in the requirements:
   - Create a test plan document with IEEE 829 standard structure
   - Define test scope based on service boundaries
   - Establish test priorities based on function criticality
   - Create test organization structure by service function
   - Define test identification scheme using service identifiers (e.g., S001-TC-XXX)
   - Document dependencies between test cases and across services

### 2. Function Test Coverage Analysis
1. For each service specification:
   - Extract all functions from the specification
   - Create a coverage matrix mapping functions to test cases
   - Ensure every function has at least one test case
   - Identify functions requiring multiple test scenarios
   - Document coverage rationale for complex functions
   - Verify complete function coverage across all test cases

### 3. Entity Test Coverage Analysis
1. For each service specification:
   - Extract all business entities from the specification
   - Identify entity attributes requiring validation
   - Create data validation test cases for each entity
   - Ensure entity relationships are tested
   - Document entity coverage across test scenarios
   - Verify complete entity coverage across all test cases

### 4. Positive Test Scenario Generation
1. For each function:
   - Create test cases for valid input conditions
   - Define expected outcomes based on function specifications
   - Include test cases for all valid business scenarios
   - Create test data sets representing normal operations
   - Document traceability to specific functions
   - Ensure all positive paths through business logic are tested

### 5. Negative Test Scenario Generation
1. For each function:
   - Create test cases for invalid input conditions
   - Define expected error handling based on specifications
   - Include test cases for all error conditions
   - Create test data sets representing error scenarios
   - Document traceability to specific functions
   - Ensure all error handling paths are tested

### 6. Boundary Test Scenario Generation
1. For each function with numeric or range conditions:
   - Create test cases for boundary values
   - Define test cases for minimum valid values
   - Define test cases for maximum valid values
   - Create test cases for values just outside valid ranges
   - Document traceability to specific functions
   - Ensure all boundary conditions are tested

### 7. Cross-Service Test Scenario Generation
1. For identified cross-service relationships:
   - Create test cases that span service boundaries
   - Define test scenarios for integrated functionality
   - Include test cases for cross-service data flows
   - Create test data sets for cross-service operations
   - Document traceability to multiple service specifications
   - Ensure all cross-service interactions are tested

### 8. Test Case Prioritization
1. For all generated test cases:
   - Assign priority levels (Critical, High, Medium, Low)
   - Prioritize based on business impact and complexity
   - Group test cases by execution sequence
   - Define dependencies between test cases
   - Document rationale for priority assignments
   - Create execution order recommendations

### 9. Test Data Definition
1. For each test case:
   - Define required test data in language-agnostic format
   - Create sample input data sets
   - Define expected output data
   - Document data dependencies between test cases
   - Create data setup and teardown requirements
   - Ensure test data covers all scenarios

### 10. Traceability Documentation
1. For each test case:
   - Create explicit links to functions
   - Document relationships to business entities
   - Map test cases to original business requirements
   - Create bidirectional traceability matrix
   - Document coverage of legacy implementation
   - Ensure complete traceability chain

### 11. Progress Tracking
1. Update progress tracking for each completed service:
   - Record completion status and artifacts
   - Document any issues or exceptions
   - Update phase status in progress tracking system


## Output Format

### Test Case Definition Structure
**File**: `{{TEST_GENERATION_SERVICE_BASE_PATH}}/S-XXX-[service-name]-tests.md`
**Template**: `{{TEST_CASE_DEFINITION_SERVICE_TEMPLATE}}`

The template follows IEEE 829 standard and includes:
- Document control with service ID and related requirements
- Test plan overview with organization, prioritization, and dependencies
- Test cases with service-specific identifiers (S001-TC-XXX)
- Each test case includes: type, priority, description, functions, entities, preconditions, test data (inputs/outputs), test steps, validation points, and dependencies
- Traceability matrices for function coverage, entity coverage, and original requirement traceability

### Progress Tracking Format
**File**: `{{TEST_GENERATION_SERVICE_STATUS}}`
**Template**: `{{TEST_GENERATION_SERVICE_STATUS_TEMPLATE}}`

The template tracks:
- Phase ID and overall status
- Array of services with: serviceId, serviceName, status, test case counts (total, positive, negative, boundary), function/entity coverage percentages, test definition path, completedDate
- Completion counts and last updated timestamp

## Quality Criteria

### Test Coverage Quality
- Every function has at least one test case
- Every entity has validation test cases
- All positive, negative, and boundary conditions are tested
- Cross-service interactions have dedicated test cases
- Test coverage is documented and justified

### Test Case Quality
- Test cases are clearly defined and unambiguous
- Each test case has explicit validation points
- Test data is comprehensive and realistic
- Test steps are detailed and actionable
- Test dependencies are clearly documented

### Traceability Quality
- Each test case is linked to specific functions
- Test cases are mapped to entities
- Complete traceability to original business requirements
- Bidirectional traceability matrix is provided
- Coverage gaps are documented with rationale

### IEEE Standard Compliance
- Test documentation follows IEEE 829 standard
- Test cases have unique identifiers
- Test organization follows service structure
- Test prioritization is clear and justified
- Test dependencies are properly documented

### Language Independence
- Test cases are defined without implementation language specifics
- Test data is specified in technology-agnostic format
- Test steps are described in business terms
- Validation points are defined by business outcomes
- Test cases can be implemented in any target language

## Error Handling

### Common Error Scenarios

1. **Incomplete Function Coverage**
   - Detection: Functions without corresponding test cases
   - Recovery: Generate missing test cases with priority flags
   - Escalation: Flag for human review if function is ambiguous

2. **Ambiguous Test Expectations**
   - Detection: Test cases with unclear expected outcomes
   - Recovery: Revisit function specifications for clarification
   - Escalation: Request human clarification for critical test cases

3. **Missing Test Data**
   - Detection: Test cases without sufficient test data
   - Recovery: Generate synthetic test data based on entity definitions
   - Escalation: Flag for human review if data requirements are complex

4. **Cross-Service Inconsistencies**
   - Detection: Conflicting test expectations across services
   - Recovery: Document conflicts and prioritize based on service hierarchy
   - Escalation: Request human resolution for critical conflicts

### Error Reporting Format
**File**: `{{TEST_GENERATION_SERVICE_ERRORS}}`
**Template**: `{{TEST_GENERATION_SERVICE_ERRORS_TEMPLATE}}`
- Include: timestamp, error type, context, attempted resolution
- Update phase status to indicate partial completion or issues

### Fallback Strategies
- Generate minimal test sets for complex functions when complete coverage is challenging
- Use equivalence partitioning to reduce test case count while maintaining coverage
- Focus on critical functions when complete coverage is not feasible
- Document coverage gaps with explicit rationale
- Flag areas requiring human expert review

