# Phase 4.0: Test Case Specification Creation

---

## Orchestration Information

**Phase**: Phase 4 - Test Case Generation
**Step**: Step 4.0 - Test Case Specification Creation
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_test_design
**Task File Name**: {{TASKS_BASE_PATH}}/phase_4.0_test_case_creation.md

### Expected Deliverables

1. **Test Case Definition Documents (Draft)**
   - File: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-XXX-FLOW_XXX-tests-[LANG]-draft.md
   - Template: {{TEST_CASE_DEFINITION_TEMPLATE}}
   - Description: IEEE 829 standard test case definitions for the workpackage (draft version for review)

2. **Test Traceability Matrix**
   - File: {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-XXX-FLOW_XXX-test-traceability-matrix.md
   - Description: Mapping of test cases to business functions, entities, and rules

3. **Test Coverage Report**
   - File: {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-XXX-FLOW_XXX-coverage-notes.md
   - Description: Coverage analysis and notes

4. **Progress Tracking**
   - File: {{TEST_CASE_GENERATION_STATUS}}
   - Template: {{TEST_CASE_GENERATION_STATUS_TEMPLATE}}
   - Description: Test generation progress and status tracking

5. **Error Reports** (if applicable)
   - File: {{TEST_CASE_GENERATION_ERRORS}}
   - Template: {{TEST_CASE_GENERATION_ERRORS_TEMPLATE}}
   - Description: Documentation of errors and issues encountered

### Success Criteria
- [ ] All workpackages have test case definitions created
- [ ] Every function has at least one test case
- [ ] Every entity has validation test cases
- [ ] All positive, negative, and boundary conditions tested
- [ ] Cross-workpackage interactions have dedicated test cases
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
- **Technical specifications**: IEEE 829 standard structure, workpackage-based organization, test prioritization
- **Business rules and constraints**: Language-agnostic format, comprehensive coverage, traceability requirements
- **Error handling guidance**: Incomplete function coverage, ambiguous test expectations, missing test data, cross-workpackage inconsistencies
- **Output format requirements**: Test case definition documents, progress tracking, error reports
- **Quality criteria**: Test coverage quality, test case quality, traceability quality, IEEE compliance, language independence

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Business specifications: {{BUSINESS_SPECIFICATION_BASE_PATH}}/business/
  - Workpackage definitions: {{PROJECT_BASE_PATH}}/output/analysis/workpackages/
  - Domain consolidation specs: {{DOMAIN_CONSOLIDATION_BASE_PATH}}
- **All output locations** (resolved paths):
  - Test case definitions: {{TEST_CASE_GENERATION_BASE_PATH}}
  - Progress tracking: {{TEST_CASE_GENERATION_STATUS}}
  - Error reports: {{TEST_CASE_GENERATION_ERRORS}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Test case definition template: {{TEST_CASE_DEFINITION_TEMPLATE}}
  - Status template: {{TEST_CASE_GENERATION_STATUS_TEMPLATE}}
  - Errors template: {{TEST_CASE_GENERATION_ERRORS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: business_specialist_test_design
- **Agent definition file**: structure/agents/business_team/business_specialist_test_design.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations (Phase 3 business specifications from previous phase), output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-11), business rules, error handling
- **Expected Deliverables**: All 3 deliverables with paths, templates, descriptions, validation checklists
- **Quality Criteria**: Test coverage quality, test case quality, traceability quality, IEEE compliance, language independence
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

### 6. Dependencies from previous phases:
This step requires outputs from Phase 3 (Business Extraction):
- **From Phase 3**: Business specifications with functions and entities
- **From Phase 3**: Domain consolidation specifications (if applicable)
- Verify these artifacts exist before creating the task file

---

## Context
- Input Location: 
  - `{{BUSINESS_SPECIFICATION_BASE_PATH}}` - Business Requirements documentation
  - `{{TEST_CASE_DEFINITION_TEMPLATE}}` - Test case definition template
- Output Location: 
  - `{{TEST_CASE_GENERATION_BASE_PATH}}` - Test case specifications (drafts and approved)
  - `{{TEST_CASE_GENERATION_BASE_PATH}}/progress` - Phase completion tracking
  - `{{TEST_CASE_GENERATION_BASE_PATH}}/logs` - Error logs and execution logs
  - `{{TEST_CASE_GENERATION_BASE_PATH}}/review` - Review feedback and approvals
  - `{{TEST_CASE_GENERATION_ROOT}}/traceability` - Traceability matrices and coverage reports

## Objective
Generate programming language-independent test case definitions from business requirements that cover all workpackages, functions, and entities. Create comprehensive test scenarios including positive, negative, and boundary test cases while maintaining full traceability to business specifications. Organize test cases by workpackage and priority to facilitate systematic validation of migrated functionality against original business requirements.

**CRITICAL**: This phase produces DRAFT documents for review. Only final and approved test case documents should remain in the specs folder after review approval. Any drafts, intermediate documents, or summaries should NOT be created. If something needs to be reported, it should go in the logs folder.

## Instructions

### 1. Test Planning and Organization
1. Review all business requirements documents
2. For each workpackage specified in the requirements:
   - Load the test case definition template from `{{TEST_CASE_DEFINITION_TEMPLATE}}`
   - Create a test plan document with IEEE 829 standard structure
   - Define test scope based on workpackage boundaries
   - Establish test priorities based on function criticality
   - Create test organization structure by workpackage function
   - Define test identification scheme using workpackage and flow identifiers (e.g., WP-XXX-TC-YYY)
   - Document dependencies between test cases and across workpackages

### 2. Function Test Coverage Analysis
1. For each workpackage specification:
   - Extract all functions from the specification
   - Create a coverage matrix mapping functions to test cases
   - Ensure every function has at least one test case
   - Identify functions requiring multiple test scenarios
   - Document coverage rationale for complex functions
   - Verify complete function coverage across all test cases

### 3. Entity Test Coverage Analysis
1. For each workpackage specification:
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

### 7. Cross-Workpackage Test Scenario Generation
1. For identified cross-workpackage relationships:
   - Create test cases that span workpackage boundaries
   - Define test scenarios for integrated functionality
   - Include test cases for cross-workpackage data flows
   - Create test data sets for cross-workpackage operations
   - Document traceability to multiple workpackage specifications
   - Ensure all cross-workpackage interactions are tested

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
1. Update progress tracking for each completed workpackage:
   - Record completion status and artifacts
   - Document any issues or exceptions
   - Update phase status in progress tracking system
   - DO NOT create summary documents or intermediate reports
   - Any execution logs or issues should go in the logs folder
   - Mark workpackage status as ready for review (Phase 4.0.1)

## Output Format

### Test Case Definition Structure
**File**: `{{TEST_CASE_GENERATION_BASE_PATH}}/WP-XXX-FLOW_XXX-tests-[LANG]-draft.md`
**Template**: `{{TEST_CASE_DEFINITION_TEMPLATE}}`

**CRITICAL**: This phase produces DRAFT documents. Only final, approved test case documents should be placed in the specs folder after review approval.

The template (located at `{{TEST_CASE_DEFINITION_TEMPLATE}}`) follows IEEE 829 standard and includes:
- Document control with workpackage ID, flow ID, and related requirements
- Test plan overview with organization, prioritization, and dependencies
- Test cases with workpackage-specific identifiers (WP-XXX-TC-YYY)
- Each test case includes: type, priority, description, functions, entities, business rules, preconditions, test data (inputs/outputs), test steps, expected results, validation points, and dependencies
- Traceability matrices for function coverage, entity coverage, and business rule coverage

**File Naming Convention**: `WP-XXX-FLOW_XXX-tests-[LANG]-draft.md`
- WP-XXX: Workpackage identifier
- FLOW_XXX: Flow identifier from business specification
- -draft: Indicates this is a draft version awaiting review

### Progress Tracking Format
**File**: `{{TEST_CASE_GENERATION_STATUS}}`
**Template**: `{{TEST_CASE_GENERATION_STATUS_TEMPLATE}}`

The template tracks:
```json
{
  "document_type": "Test Case Specification Progress Tracking",
  "last_updated": "2026-02-19T13:35:01+01:00",
  "phase": "Phase 4 - Test Case Generation",
  "workpackages": {
    "WP-001": {
      "workpackage_id": "WP-001",
      "flow_id": "FLOW_COSGN00C",
      "flow_name": "Sign-On Functionality",
      "status": "Approved",
      "completed_date": "2026-02-19",
      "specifications": {
        "en": {
          "original": "output/specifications/test_cases/specs/WP-001-FLOW_COSGN00C-tests-EN.md",
          "reviewed": "output/specifications/test_cases/specs/WP-001-FLOW_COSGN00C-tests-EN-approved.md",
          "version": "1.0",
          "status": "approved",
          "approval_date": "2026-02-19"
        }
      },
      "test_cases": {
        "total": 28,
        "positive": 12,
        "negative": 12,
        "boundary": 4,
        "by_category": {
          "authentication": 12,
          "authorization": 4,
          "sessionManagement": 4,
          "uiDisplay": 4,
          "integration": 4
        },
        "by_priority": {
          "critical": 12,
          "high": 8,
          "medium": 6,
          "low": 2
        }
      },
      "coverage": {
        "functions": {
          "total": 5,
          "covered": 5,
          "percentage": "100%",
          "list": [
            "F-001-001: Handle Credential Submission",
            "F-001-002: Display Sign-On Screen"
          ]
        },
        "entities": {
          "total": 2,
          "covered": 2,
          "percentage": "100%",
          "list": [
            "BE-001-001: User",
            "BE-001-002: Session"
          ]
        },
        "business_rules": {
          "total": 8,
          "covered": 8,
          "percentage": "100%",
          "list": [
            "BR-001-001: Mandatory User ID",
            "BR-001-002: Mandatory Password"
          ]
        }
      },
      "deliverables": {
        "test_specification_en_approved": {
          "path": "output/specifications/test_cases/specs/WP-001-FLOW_COSGN00C-tests-EN-approved.md",
          "status": "Approved",
          "approval_date": "2026-02-19",
          "language": "English",
          "test_cases_count": 28
        },
        "test_traceability_matrix": {
          "path": "output/specifications/test_cases/traceability/WP-001-FLOW_COSGN00C-test-traceability-matrix.md",
          "status": "Complete",
          "created_date": "2026-02-19",
          "coverage": "100%"
        },
        "review_report": {
          "path": "output/specifications/test_cases/specs/review/test-case-generation-WP-001-review.md",
          "status": "Complete",
          "review_date": "2026-02-19",
          "reviewer": "business_reviewer_test_design",
          "decision": "Approved"
        }
      },
      "quality_checks": {
        "function_coverage_complete": true,
        "entity_coverage_complete": true,
        "business_rule_coverage_complete": true,
        "positive_negative_boundary_balance": true,
        "traceability_established": true,
        "ieee_829_compliant": true,
        "language_independent": true
      },
      "metrics": {
        "total_test_cases": 28,
        "function_coverage": "100%",
        "entity_coverage": "100%",
        "business_rule_coverage": "100%",
        "traceability_coverage": "100%"
      },
      "next_phase": "Phase 5 - Code Generation",
      "ready_for_code_generation": true,
      "notes": "Test case generation complete. All business functions, entities, and rules covered."
    }
  },
  "summary": {
    "total_workpackages": 33,
    "completed_workpackages": 1,
    "approved_workpackages": 1,
    "in_progress_workpackages": 0,
    "pending_workpackages": 32,
    "overall_progress": "3%",
    "total_test_cases": 28,
    "total_functions_covered": 5,
    "total_entities_covered": 2,
    "total_business_rules_covered": 8,
    "overall_coverage": "100%",
    "ready_for_phase_5": 1,
    "quality_metrics": {
      "function_coverage_complete": 1,
      "entity_coverage_complete": 1,
      "business_rule_coverage_complete": 1,
      "positive_negative_boundary_balance": 1,
      "traceability_established": 1,
      "ieee_829_compliant": 1
    }
  }
}
```

## Quality Criteria

### Test Coverage Quality
- Every function has at least one test case
- Every entity has validation test cases
- All positive, negative, and boundary conditions are tested
- Cross-workpackage interactions have dedicated test cases
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
- Test organization follows workpackage structure
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

4. **Cross-Workpackage Inconsistencies**
   - Detection: Conflicting test expectations across workpackages
   - Recovery: Document conflicts and prioritize based on workpackage hierarchy
   - Escalation: Request human resolution for critical conflicts

### Error Reporting Format
**File**: `{{TEST_CASE_GENERATION_ERRORS}}`
**Template**: `{{TEST_CASE_GENERATION_ERRORS_TEMPLATE}}`
- Include: timestamp, error type, context, attempted resolution
- Update phase status to indicate partial completion or issues
- Place all error logs in the logs folder, not in specs folder

### Fallback Strategies
- Generate minimal test sets for complex functions when complete coverage is challenging
- Use equivalence partitioning to reduce test case count while maintaining coverage
- Focus on critical functions when complete coverage is not feasible
- Document coverage gaps with explicit rationale
- Flag areas requiring human expert review

