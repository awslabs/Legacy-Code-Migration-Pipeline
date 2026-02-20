# Phase 4: Test Case Generation - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 4 - Test Case Generation
**Version**: 1.0
**Date**: 2026-02-19
**Owner**: business_analyst_team_lead

---

## Overview

This document provides orchestration instructions for the Test Case Generation phase, which creates language-independent test case specifications from business requirements through a two-phase iterative process:

1. **Phase 4.0**: Test Case Specification Creation - Generate IEEE 829 compliant test cases
2. **Phase 4.0.1**: Test Case Specification Review - Validate test cases and approve for code generation

**Critical Principle**: Generate **language-independent test specifications** that validate business requirements rather than implementation-specific test code.

**Critical Quality Control**: All test cases must be traceable to business functions, entities, and rules from Phase 3 business specifications. Test coverage must be complete before approval.

---

## Phase Task Documents

The complete task documents for each phase are located in the prompts directory:
- **Phase 4.0**: {{PROMPTS_BASE_PATH}}/04_test_case_generation/phase_4.0_test_case_creation.md
- **Phase 4.0.1**: {{PROMPTS_BASE_PATH}}/04_test_case_generation/phase_4.0.1_test_case_review.md

**The supervisor provides these task documents directly to agents** (no task file creation required). Each phase document is self-contained with:
- Orchestration Information (phase, agent, deliverables, success criteria)
- Context (input/output/template locations with {{PATH_VARIABLES}})
- Detailed instructions (step-by-step execution guidance)
- Output format specifications
- Quality criteria
- Error handling procedures

Agents will resolve {{PATH_VARIABLES}} at runtime using the project configuration.

---

## Phase Dependencies

```
Phase 3 (Business Specification) → Phase 4 (Test Case Generation) → Phase 5 (Code Generation)
                                            ↓
                                    Phase 4.0 (Test Case Creation)
                                            ↓
                                    Phase 4.0.1 (Test Case Review)
                                            ↓
                                    [Iterate until approved]
                                            ↓
                                    Phase 5 (Code Generation)
```

**Prerequisites**:
- Phase 3 outputs: Approved business specifications with functions, entities, and business rules

---

## Orchestration Workflow

### For Each Workpackage (in priority order):

```
WORKPACKAGE_LOOP:
    SELECT next_workpackage FROM workpackage_definitions ORDER BY priority

    # ========================================
    # PHASE 4.0: TEST CASE SPECIFICATION CREATION
    # ========================================
    
    EXECUTE Phase_4.0:
        ASSIGN: test_case_specialist
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/04_test_case_generation/phase_4.0_test_case_creation.md
        PROVIDE_CONTEXT:
            - workpackage_id: current_workpackage.id
            - workpackage_name: current_workpackage.name
            - flow_id: current_workpackage.flow_id
            - flow_name: current_workpackage.flow_name
        
        INPUTS:
            - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-specification-approved.md
            - Workpackage planning: {{WORKPACKAGE_PLANNING}}
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
        
        EXPECTED_OUTPUTS:
            - Test case specification (draft): {{TEST_CASE_GENERATION_BASE_PATH}}/WP-XXX-FLOW_XXX-tests-[LANG]-draft.md
            - Test traceability matrix: {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-XXX-FLOW_XXX-test-traceability-matrix.md
            - Test coverage report: {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-XXX-FLOW_XXX-coverage-notes.md
            - Progress tracking: {{TEST_CASE_GENERATION_STATUS}}
            - Error reports (if any): {{TEST_CASE_GENERATION_ERRORS}}
        
        VERIFICATION:
            CHECK test_specification_exists(WP-XXX)
            CHECK function_coverage_complete(WP-XXX)
            CHECK entity_coverage_complete(WP-XXX)
            CHECK business_rule_coverage_complete(WP-XXX)
            CHECK positive_negative_boundary_balance(WP-XXX)
            CHECK traceability_matrix_complete(WP-XXX)
            CHECK ieee_829_compliant(WP-XXX)
            
            IF verification_failed:
                LOG error to {{TEST_CASE_GENERATION_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{TEST_CASE_GENERATION_STATUS}} with completion
                PROCEED to Phase_4.0.1

    # ========================================
    # PHASE 4.0.1: TEST CASE SPECIFICATION REVIEW
    # ========================================
    
    EXECUTE Phase_4.0.1:
        ASSIGN: test_case_reviewer
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/04_test_case_generation/phase_4.0.1_test_case_review.md
        PROVIDE_CONTEXT:
            - workpackage_id: current_workpackage.id
            - workpackage_name: current_workpackage.name
            - flow_id: current_workpackage.flow_id
            - flow_name: current_workpackage.flow_name
        
        INPUTS:
            - Test case specification (draft): {{TEST_CASE_GENERATION_BASE_PATH}}/WP-XXX-FLOW_XXX-tests-[LANG]-draft.md
            - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-specification-approved.md
            - Test traceability matrix: {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-XXX-FLOW_XXX-test-traceability-matrix.md
            - Test coverage report: {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-XXX-FLOW_XXX-coverage-notes.md
        
        EXPECTED_OUTPUTS:
            - Test case review report: {{TEST_CASE_GENERATION_REVIEW}}/test-case-generation-WP-XXX-review.md
            - Approved test specification: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-XXX-FLOW_XXX-tests-[LANG]-approved.md (if approved)
            - Archived draft: {{TEST_CASE_GENERATION_REVIEW}}/WP-XXX-FLOW_XXX-tests-[LANG]-draft.md (moved to review folder)
            - Progress tracking: {{TEST_CASE_GENERATION_STATUS}}
        
        VERIFICATION:
            CHECK review_report_exists(WP-XXX, "test_case")
            CHECK approval_decision_documented(WP-XXX, "test_case")
            
            IF decision == "APPROVED":
                CHECK approved_specification_exists(WP-XXX, "test_case")
                CHECK draft_archived_to_review_folder(WP-XXX, "test_case")
                UPDATE {{TEST_CASE_GENERATION_STATUS}} with approval
                PROCEED to WORKPACKAGE_COMPLETE
            
            ELSE IF decision == "REVISE":
                CHECK revision_feedback_documented(WP-XXX, "test_case")
                UPDATE {{TEST_CASE_GENERATION_STATUS}} with revision request
                RETURN to Phase_4.0 with feedback
            
            ELSE IF decision == "REJECT":
                CHECK rejection_rationale_documented(WP-XXX, "test_case")
                UPDATE {{TEST_CASE_GENERATION_STATUS}} with rejection
                ESCALATE to human supervisor
                HALT workpackage processing

    # ========================================
    # WORKPACKAGE COMPLETION
    # ========================================
    
    WORKPACKAGE_COMPLETE:
        LOG "Test case generation for WP-{ID} completed successfully"
        UPDATE {{TEST_CASE_GENERATION_STATUS}} with workpackage completion
        PROCEED to next workpackage in WORKPACKAGE_LOOP

END WORKPACKAGE_LOOP
```

---

## Agent Assignments

### Phase 4.0: Test Case Specification Creation
**Agent**: test_case_specialist
**Agent Definition**: structure/agents/business_analyst_team/test_case_specialist.md
**Task Document**: {{PROMPTS_BASE_PATH}}/04_test_case_generation/phase_4.0_test_case_creation.md
**Capabilities**:
- IEEE 829 test case specification
- Test coverage analysis
- Traceability matrix creation
- Positive/negative/boundary test scenario generation
- Language-independent test design
- Test prioritization and categorization

### Phase 4.0.1: Test Case Specification Review
**Agent**: test_case_reviewer
**Agent Definition**: structure/agents/business_analyst_team/test_case_reviewer.md
**Task Document**: {{PROMPTS_BASE_PATH}}/04_test_case_generation/phase_4.0.1_test_case_review.md
**Capabilities**:
- Test specification quality review
- Coverage completeness verification
- Traceability validation
- IEEE 829 compliance checking
- Test case clarity and executability assessment
- Approval decision making

---

## Input/Output Contracts

### Phase 3 → Phase 4.0
**Phase 3 Outputs** (Phase 4.0 Inputs):
- Business specification: `WP-XXX-specification-approved.md`
- Business functions with F-XXX identifiers
- Business entities with BE-XXX identifiers
- Business rules with BR-XXX identifiers
- Process flows documented

**Contract**:
- All business functions are documented
- All business entities are defined
- All business rules are specified
- Traceability to legacy code is established

### Phase 4.0 → Phase 4.0.1
**Phase 4.0 Outputs** (Phase 4.0.1 Inputs):
- Test case specification (draft): `WP-XXX-FLOW_XXX-tests-[LANG]-draft.md`
- Test traceability matrix
- Test coverage report

**Contract**:
- Test cases follow IEEE 829 standard
- All functions have test coverage
- All entities have validation tests
- All business rules have test cases
- Positive, negative, and boundary scenarios included
- Traceability matrix is complete

### Phase 4.0.1 → Phase 5
**Phase 4.0.1 Outputs** (Phase 5 Inputs):
- Approved test specification: `WP-XXX-FLOW_XXX-tests-[LANG]-approved.md`
- Test traceability matrix
- Test coverage report
- Review approval

**Contract**:
- Test specification is approved
- Coverage is 100% for functions, entities, and business rules
- Test cases are clear and executable
- Language-independent format
- Ready for code generation

---

## Verification Criteria

### Phase 4.0 Verification
```
CHECK test_specification_exists(workpackage_id):
    draft_path = {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{workpackage_id}-FLOW_XXX-tests-[LANG]-draft.md
    RETURN file_exists(draft_path)

CHECK function_coverage_complete(workpackage_id):
    spec = load_business_specification(workpackage_id)
    test_spec = load_test_specification(workpackage_id)
    
    functions = spec.chapter_2.functions
    test_cases = test_spec.test_cases
    
    FOR EACH function IN functions:
        has_test = any(tc.functions contains function.id for tc in test_cases)
        IF NOT has_test:
            LOG "Function {function.id} has no test coverage"
            RETURN FALSE
    
    RETURN TRUE

CHECK entity_coverage_complete(workpackage_id):
    spec = load_business_specification(workpackage_id)
    test_spec = load_test_specification(workpackage_id)
    
    entities = spec.chapter_2.entities
    test_cases = test_spec.test_cases
    
    FOR EACH entity IN entities:
        has_validation = any(tc.entities contains entity.id for tc in test_cases)
        IF NOT has_validation:
            LOG "Entity {entity.id} has no validation test"
            RETURN FALSE
    
    RETURN TRUE

CHECK business_rule_coverage_complete(workpackage_id):
    spec = load_business_specification(workpackage_id)
    test_spec = load_test_specification(workpackage_id)
    
    rules = spec.chapter_3.business_rules
    test_cases = test_spec.test_cases
    
    FOR EACH rule IN rules:
        has_test = any(tc.business_rules contains rule.id for tc in test_cases)
        IF NOT has_test:
            LOG "Business rule {rule.id} has no test coverage"
            RETURN FALSE
    
    RETURN TRUE

CHECK positive_negative_boundary_balance(workpackage_id):
    test_spec = load_test_specification(workpackage_id)
    test_cases = test_spec.test_cases
    
    positive_count = count(tc for tc in test_cases if tc.type == "positive")
    negative_count = count(tc for tc in test_cases if tc.type == "negative")
    boundary_count = count(tc for tc in test_cases if tc.type == "boundary")
    
    # At least some of each type should exist
    RETURN positive_count > 0 AND negative_count > 0 AND boundary_count > 0

CHECK traceability_matrix_complete(workpackage_id):
    matrix_path = {{TEST_CASE_GENERATION_ROOT}}/traceability/WP-{workpackage_id}-FLOW_XXX-test-traceability-matrix.md
    RETURN file_exists(matrix_path) AND file_not_empty(matrix_path)

CHECK ieee_829_compliant(workpackage_id):
    test_spec = load_test_specification(workpackage_id)
    
    # Check for required IEEE 829 sections
    has_test_plan = test_spec.has_section("Test Plan Overview")
    has_test_cases = test_spec.has_section("Test Cases")
    has_traceability = test_spec.has_section("Traceability Matrix")
    
    # Check test case structure
    FOR EACH test_case IN test_spec.test_cases:
        has_id = test_case.has_field("id")
        has_type = test_case.has_field("type")
        has_priority = test_case.has_field("priority")
        has_description = test_case.has_field("description")
        has_preconditions = test_case.has_field("preconditions")
        has_test_data = test_case.has_field("test_data")
        has_test_steps = test_case.has_field("test_steps")
        has_expected_results = test_case.has_field("expected_results")
        
        IF NOT (has_id AND has_type AND has_priority AND has_description AND 
                has_preconditions AND has_test_data AND has_test_steps AND has_expected_results):
            RETURN FALSE
    
    RETURN has_test_plan AND has_test_cases AND has_traceability
```

### Phase 4.0.1 Verification
```
CHECK review_report_exists(workpackage_id, phase_type):
    review_path = {{TEST_CASE_GENERATION_REVIEW}}/test-case-generation-WP-{workpackage_id}-review.md
    RETURN file_exists(review_path)

CHECK approval_decision_documented(workpackage_id, phase_type):
    review_report = load_review_report(workpackage_id, phase_type)
    RETURN review_report.has_field("decision") AND 
           review_report.decision IN ["APPROVED", "REVISE", "REJECT"]

CHECK approved_specification_exists(workpackage_id, phase_type):
    approved_path = {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{workpackage_id}-FLOW_XXX-tests-[LANG]-approved.md
    RETURN file_exists(approved_path)

CHECK draft_archived_to_review_folder(workpackage_id, phase_type):
    archived_path = {{TEST_CASE_GENERATION_REVIEW}}/WP-{workpackage_id}-FLOW_XXX-tests-[LANG]-draft.md
    original_path = {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{workpackage_id}-FLOW_XXX-tests-[LANG]-draft.md
    RETURN file_exists(archived_path) AND NOT file_exists(original_path)
```

---

## Error Handling and Rework

### Rework Scenarios

#### Scenario 1: Incomplete Coverage (Return to Phase 4.0)
**Triggers**:
- Missing function coverage
- Missing entity validation tests
- Missing business rule tests
- Insufficient test scenario types (positive/negative/boundary)

**Actions**:
1. Document coverage gaps in review report
2. Update Phase 4.0 task with specific coverage requirements
3. Re-assign test_case_specialist
4. Re-execute Phase 4.0 with focus on coverage gaps
5. Re-verify coverage completeness

#### Scenario 2: Quality Issues (Return to Phase 4.0)
**Triggers**:
- Test cases not clear or executable
- Missing traceability
- IEEE 829 non-compliance
- Language-specific implementation details in tests
- Ambiguous test data or expected results

**Actions**:
1. Document quality issues in review report
2. Update Phase 4.0 task with specific quality improvements needed
3. Re-assign test_case_specialist
4. Re-execute Phase 4.0 with focus on quality issues
5. Re-verify quality criteria

#### Scenario 3: Traceability Issues (Return to Phase 4.0)
**Triggers**:
- Test cases not linked to business functions
- Test cases not linked to business entities
- Test cases not linked to business rules
- Traceability matrix incomplete or incorrect

**Actions**:
1. Document traceability gaps in review report
2. Update Phase 4.0 task with specific traceability requirements
3. Re-assign test_case_specialist
4. Re-execute Phase 4.0 with focus on traceability
5. Re-verify traceability completeness

#### Scenario 4: Critical Issues (Escalate to Human)
**Triggers**:
- Business specification ambiguities preventing test creation
- Conflicting business rules
- Missing business requirements
- Technical blockers requiring clarification

**Actions**:
1. Document critical issues in error log
2. Escalate to human supervisor with detailed explanation
3. Halt workpackage processing
4. Await human guidance before proceeding

---

## Progress Tracking

### Master Progress Tracking

**JSON File**: `{{TEST_CASE_GENERATION_STATUS}}`

**Structure**:
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
          "original": "output/specifications/test_cases/specs/WP-001-FLOW_COSGN00C-tests-EN-draft.md",
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
        "boundary": 4
      },
      "coverage": {
        "functions": {
          "total": 5,
          "covered": 5,
          "percentage": "100%"
        },
        "entities": {
          "total": 2,
          "covered": 2,
          "percentage": "100%"
        },
        "business_rules": {
          "total": 8,
          "covered": 8,
          "percentage": "100%"
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
      "ready_for_code_generation": true
    }
  },
  "summary": {
    "total_workpackages": 33,
    "completed_workpackages": 1,
    "approved_workpackages": 1,
    "in_progress_workpackages": 0,
    "pending_workpackages": 32,
    "overall_progress": "3%",
    "ready_for_phase_5": 1
  }
}
```

**Update Frequency**: After each phase completion or status change

### Resumption Logic

When resuming after interruption:
1. Read {{TEST_CASE_GENERATION_STATUS}}
2. Find first workpackage with status != "Approved"
3. Check current phase status for that workpackage
4. Resume from appropriate phase (4.0 or 4.0.1)
5. Continue workpackage loop from that point

---

## Quality Gates

### Phase 4.0 Quality Gate
**Criteria**:
- [ ] Test specification document exists (draft)
- [ ] All functions have test coverage
- [ ] All entities have validation tests
- [ ] All business rules have test coverage
- [ ] Positive, negative, and boundary test scenarios included
- [ ] Test cases follow IEEE 829 standard
- [ ] Traceability matrix is complete
- [ ] Test cases are language-independent
- [ ] Test data is specified
- [ ] Expected results are clear

**Gate Decision**:
- **PASS**: Proceed to Phase 4.0.1 (Review)
- **FAIL**: Rework Phase 4.0 or escalate

### Phase 4.0.1 Quality Gate
**Criteria**:
- [ ] Review report exists
- [ ] Approval decision documented
- [ ] Coverage verified as complete
- [ ] Quality issues addressed
- [ ] Traceability validated
- [ ] IEEE 829 compliance confirmed
- [ ] Language independence confirmed
- [ ] Test cases are clear and executable

**Gate Decision**:
- **APPROVED**: Proceed to next workpackage or Phase 5
- **REVISE**: Return to Phase 4.0 with feedback
- **REJECT**: Escalate to human supervisor

---

## Configuration and Path Variables

### Project Paths
```
Project Name = {{PROJECT_NAME}}
Project = {{PROJECT_BASE_PATH}}
Prompts = {{PROMPTS_BASE_PATH}}
```

### Input Paths
```
Workpackage Planning = {{WORKPACKAGE_PLANNING}}
Business Specification = {{BUSINESS_SPECIFICATION_BASE_PATH}}
Business Context = {{BUSINESS_CONTEXT_BASE_PATH}}
```

### Output Paths
```
Test Case Generation Root = {{TEST_CASE_GENERATION_ROOT}}
Test Case Generation Specs = {{TEST_CASE_GENERATION_BASE_PATH}}
Test Case Generation Review = {{TEST_CASE_GENERATION_REVIEW}}
Test Case Generation Status = {{TEST_CASE_GENERATION_STATUS}}
Test Case Generation Errors = {{TEST_CASE_GENERATION_ERRORS}}
```

### Template Paths
```
Test Case Status Template = {{TEST_CASE_GENERATION_STATUS_TEMPLATE}}
Test Case Definition Template = {{TEST_CASE_DEFINITION_TEMPLATE}}
Test Case Errors Template = {{TEST_CASE_GENERATION_ERRORS_TEMPLATE}}
```

---

## Supervisor Responsibilities

### Pre-Execution
1. Verify all prerequisites from Phase 3 exist
2. Verify all path variables are resolved to absolute paths
3. Verify all template files exist
4. Verify all agents are available and properly configured
5. Verify all phase task documents exist in {{PROMPTS_BASE_PATH}}
6. Create output directories if they don't exist
7. Initialize master progress tracking

### During Execution
1. Assign appropriate agent for each phase
2. Provide phase task document from {{PROMPTS_BASE_PATH}}
3. Provide workpackage context for each workpackage
4. Monitor phase execution progress
5. Verify phase completion against quality gates
6. Handle errors and rework scenarios
7. Update master progress tracking
8. Escalate critical issues to human supervisor

### Post-Execution
1. Verify all workpackages completed successfully
2. Verify all test specifications approved
3. Generate final summary report
4. Archive all artifacts
5. Prepare handoff to Phase 5 (Code Generation)

---

## Success Criteria

Phase 4 is considered complete when:
- [ ] All workpackages processed
- [ ] All test specifications approved
- [ ] 100% coverage of functions, entities, and business rules
- [ ] All test cases follow IEEE 829 standard
- [ ] All test cases are language-independent
- [ ] Complete traceability established
- [ ] Progress tracking shows 100% completion
- [ ] No critical blockers remain
- [ ] All artifacts ready for Phase 5 (Code Generation)

---

## Notes for Supervisor

**Critical Success Factors**:
1. **Complete coverage**: All functions, entities, and business rules must have test coverage
2. **Quality over quantity**: Test cases must be clear, executable, and valuable
3. **Language independence**: No implementation-specific details in test specifications
4. **Traceability**: Every test case must link to business requirements
5. **IEEE 829 compliance**: Follow standard structure for consistency

**Common Pitfalls to Avoid**:
1. Skipping review phase (breaks quality control)
2. Approving incomplete coverage (breaks validation)
3. Including implementation details (breaks language independence)
4. Missing traceability (breaks requirement validation)
5. Ignoring IEEE 829 standard (breaks consistency)

**When to Escalate**:
1. Business specification ambiguities preventing test creation
2. Conflicting business rules requiring clarification
3. Missing business requirements not documented in specifications
4. Repeated rework cycles (more than 2 iterations per workpackage)
5. Critical quality issues that cannot be resolved by agents

---

## End of Master Orchestration Document
