# Phase 4-ATX: ATX-Based Functional Equivalence Test Generation - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 4-ATX - ATX-Based Functional Equivalence Test Generation
**Version**: 1.0
**Date**: 2026-03-04
**Owner**: development_team_supervisor

---

## CRITICAL - Delegation Check

**IF YOU ARE NOT THE OWNER OF THIS DOCUMENT, STOP AND DELEGATE**

This document is owned by: **development_team_supervisor**

**Before proceeding, check your role**:
- If you are **development_team_supervisor**: Continue with orchestration
- If you are **ANY OTHER AGENT**: 
  1. STOP immediately
  2. Delegate this entire prompt to **development_team_supervisor**
  3. Wait for their response
  4. Do NOT attempt to execute the orchestration yourself

**Why this matters**: Only the designated supervisor has the authority and context to orchestrate the entire phase across multiple agents. Attempting to execute orchestration from a non-supervisor role will result in incomplete or incorrect execution.

---

## Overview

This document provides orchestration instructions for ATX-Based Functional Equivalence Test Generation, which creates test case specifications from AWS Transform (ATX) BRE analysis artifacts to verify that modernized systems behave identically to legacy systems.

**Purpose**: Generate functional equivalence test cases that:
- Verify modernized system produces same outputs as legacy system for same inputs
- Validate data transformations match legacy behavior
- Confirm business rules are applied identically
- Test edge cases and error handling equivalence
- Support comparative testing (legacy vs modern)

**Critical Principle**: Test for **behavioral equivalence**, not requirement conformance. The goal is to prove the new system replicates the old system's actual behavior, including quirks and edge cases.

**Sub-Phases**:
1. **Phase 4-ATX.0**: ATX-Based Test Case Generation (per domain/entrypoint)
2. **Phase 4-ATX.0.1**: ATX-Based Test Case Review (per domain/entrypoint)

---

## Phase Dependencies

```
Phase 1 (Analysis) → Phase 4-ATX (ATX-Based Test Generation) → Phase 5 (Code Generation)
        ↓                           ↓
   ATX BRE Analysis           Phase 4-ATX.0 (Test Case Creation)
   Legacy Code                       ↓
                              Phase 4-ATX.0.1 (Test Case Review)
                                      ↓
                              [Iterate until approved]
                                      ↓
                              Phase 5 (Code Generation)
```

**Prerequisites**:
- ATX BRE outputs: ApplicationLevelAnalysis with domains and entrypoints
- ATX data analysis: Data dictionary and lineage
- Legacy source code: COBOL, JCL, BMS, copybooks

**Outputs**:
- Functional equivalence test specifications (per domain/entrypoint)
- Test data sets (input/output pairs)
- Comparative test scenarios
- Test traceability to legacy code and ATX analysis
- Progress tracking

---

## Phase Task Documents

The complete task documents for each phase are located in the prompts directory:
- **Phase 4-ATX.0**: {{ATX_TEST_GENERATION_PROMPTS}}/phase_4.0_atx_test_case_generation.md
- **Phase 4-ATX.0.1**: {{ATX_TEST_GENERATION_PROMPTS}}/phase_4.0.1_atx_test_case_review.md

**The supervisor provides these task documents directly to agents** (no task file creation required).

---

## Orchestration Workflow

### For Each Domain and Entrypoint (from ATX BRE Analysis):

```
DOMAIN_LOOP:
    FOR EACH domain IN {{ATX_APPLICATION_ANALYSIS}}:
        domain_name = domain.name  # e.g., CreditCardAccountManagement
        
        ENTRYPOINT_LOOP:
            FOR EACH entrypoint IN domain.entrypoints:
                entrypoint_name = entrypoint.name  # e.g., COACTUPC
                
                # ========================================
                # PHASE 4-ATX.0: ATX-BASED TEST CASE GENERATION
                # ========================================
                
                EXECUTE Phase_4_ATX_0:
                    ASSIGN: development_specialist_test_generation
                    PROVIDE_TASK: {{ATX_TEST_GENERATION_PROMPTS}}/phase_4.0_atx_test_case_generation.md
                    PROVIDE_CONTEXT:
                        - domain_name: domain_name
                        - entrypoint_name: entrypoint_name
                        - entrypoint_json: {{ATX_APPLICATION_ANALYSIS}}/{domain_name}/entrypoint-{entrypoint_name}/entrypoint-{entrypoint_name}.json
                    
                    INPUTS:
                        - ATX BRE entrypoint analysis: {{ATX_APPLICATION_ANALYSIS}}/{domain_name}/entrypoint-{entrypoint_name}/
                        - ATX domain analysis: {{ATX_APPLICATION_ANALYSIS}}/{domain_name}/{domain_name}.json
                        - ATX data dictionary: {{ATX_DATA_DICTIONARY}}/
                        - ATX data lineage: {{ATX_DATA_LINEAGE}}/
                        - Legacy source code: {{SOURCE_CODE}}/
                    
                    EXPECTED_OUTPUTS:
                        - Test case specification (draft): {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
                        - Test data sets: {{ATX_TEST_GENERATION_TEST_DATA}}/{domain_name}-{entrypoint_name}-test-data.json
                        - Legacy code traceability: {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-legacy-traceability.md
                        - Coverage report: {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-coverage-notes.md
                        - Progress tracking: {{ATX_TEST_GENERATION_STATUS}}
                        - Error reports (if any): {{ATX_TEST_GENERATION_ERRORS}}
                    
                    VERIFICATION:
                        CHECK test_specification_exists(domain_name, entrypoint_name)
                        CHECK legacy_code_coverage_complete(domain_name, entrypoint_name)
                        CHECK test_data_sets_complete(domain_name, entrypoint_name)
                        CHECK comparative_scenarios_defined(domain_name, entrypoint_name)
                        CHECK traceability_to_legacy_complete(domain_name, entrypoint_name)
                        CHECK equivalence_validation_points_defined(domain_name, entrypoint_name)
                        
                        IF verification_failed:
                            LOG error to {{ATX_TEST_GENERATION_ERRORS}}
                            ESCALATE to human supervisor
                            HALT entrypoint processing
                        
                        IF verification_passed:
                            UPDATE {{ATX_TEST_GENERATION_STATUS}} with completion
                            PROCEED to Phase_4_ATX_0_1

                # ========================================
                # PHASE 4-ATX.0.1: ATX-BASED TEST CASE REVIEW
                # ========================================
                
                EXECUTE Phase_4_ATX_0_1:
                    ASSIGN: development_reviewer_test_generation
                    PROVIDE_TASK: {{ATX_TEST_GENERATION_PROMPTS}}/phase_4.0.1_atx_test_case_review.md
                    PROVIDE_CONTEXT:
                        - domain_name: domain_name
                        - entrypoint_name: entrypoint_name
                    
                    INPUTS:
                        - Test case specification (draft): {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
                        - Test data sets: {{ATX_TEST_GENERATION_TEST_DATA}}/{domain_name}-{entrypoint_name}-test-data.json
                        - Legacy code traceability: {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-legacy-traceability.md
                        - Coverage report: {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-coverage-notes.md
                        - ATX BRE analysis: {{ATX_APPLICATION_ANALYSIS}}/{domain_name}/
                        - Legacy source code: {{SOURCE_CODE}}/
                    
                    EXPECTED_OUTPUTS:
                        - Review report: {{ATX_TEST_GENERATION_REVIEW}}/atx-test-generation-{domain_name}-{entrypoint_name}-review.md
                        - Approved test specification: {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-approved.md (if approved)
                        - Archived draft: {{ATX_TEST_GENERATION_REVIEW}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md (moved to review folder)
                        - Progress tracking: {{ATX_TEST_GENERATION_STATUS}}
                    
                    VERIFICATION:
                        CHECK review_report_exists(domain_name, entrypoint_name)
                        CHECK approval_decision_documented(domain_name, entrypoint_name)
                        
                        IF decision == "APPROVED":
                            CHECK approved_specification_exists(domain_name, entrypoint_name)
                            CHECK draft_archived_to_review_folder(domain_name, entrypoint_name)
                            UPDATE {{ATX_TEST_GENERATION_STATUS}} with approval
                            PROCEED to ENTRYPOINT_COMPLETE
                        
                        ELSE IF decision == "REVISE":
                            CHECK revision_feedback_documented(domain_name, entrypoint_name)
                            UPDATE {{ATX_TEST_GENERATION_STATUS}} with revision request
                            RETURN to Phase_4_ATX_0 with feedback
                        
                        ELSE IF decision == "REJECT":
                            CHECK rejection_rationale_documented(domain_name, entrypoint_name)
                            UPDATE {{ATX_TEST_GENERATION_STATUS}} with rejection
                            ESCALATE to human supervisor
                            HALT entrypoint processing

                # ========================================
                # ENTRYPOINT COMPLETION
                # ========================================
                
                ENTRYPOINT_COMPLETE:
                    LOG "ATX-based test generation for {domain_name}/{entrypoint_name} completed successfully"
                    UPDATE {{ATX_TEST_GENERATION_STATUS}} with entrypoint completion
                    PROCEED to next entrypoint in ENTRYPOINT_LOOP
            
            END ENTRYPOINT_LOOP
        
        DOMAIN_COMPLETE:
            LOG "ATX-based test generation for domain {domain_name} completed successfully"
            UPDATE {{ATX_TEST_GENERATION_STATUS}} with domain completion
            PROCEED to next domain in DOMAIN_LOOP
    
    END DOMAIN_LOOP
```

---

## Agent Assignments

### Phase 4-ATX.0: ATX-Based Test Case Generation
**Agent**: development_specialist_test_generation
**Task Document**: {{ATX_TEST_GENERATION_PROMPTS}}/phase_4.0_atx_test_case_generation.md
**Capabilities**:
- ATX analysis interpretation
- Legacy code analysis (COBOL, JCL, BMS)
- Functional equivalence test design
- Comparative test scenario creation
- Test data extraction from legacy code
- Input/output pair generation
- Edge case identification

### Phase 4-ATX.0.1: ATX-Based Test Case Review
**Agent**: development_reviewer_test_generation
**Task Document**: {{ATX_TEST_GENERATION_PROMPTS}}/phase_4.0.1_atx_test_case_review.md
**Capabilities**:
- Test specification quality review
- Legacy code coverage verification
- Test data completeness validation
- Equivalence validation point checking
- Comparative scenario verification
- Approval decision making

---

## Input/Output Contracts

### ATX BRE Analysis + Legacy Code → Phase 4-ATX.0
**Inputs**:
- ATX BRE entrypoint analysis: Business functions, functionality flows, programs
- ATX domain analysis: Domain-level business context
- ATX data dictionary: Data structures, field definitions
- ATX data lineage: Data flows and transformations
- Legacy source code: COBOL programs, JCL, BMS maps, copybooks

**Contract**:
- ATX BRE provides entrypoint-level behavioral patterns and business functions
- Legacy code provides implementation details
- Both sources are used to create comprehensive test scenarios

### Phase 4-ATX.0 → Phase 4-ATX.0.1
**Phase 4-ATX.0 Outputs** (Phase 4-ATX.0.1 Inputs):
- Test case specification (draft)
- Test data sets (input/output pairs)
- Legacy code traceability matrix
- Coverage report

**Contract**:
- Test cases focus on functional equivalence
- Test data includes realistic legacy data patterns
- Traceability links tests to specific legacy code sections
- Coverage includes all legacy program paths

### Phase 4-ATX.0.1 → Phase 5
**Phase 4-ATX.0.1 Outputs** (Phase 5 Inputs):
- Approved test specification
- Approved test data sets
- Review report with approval status

**Contract**:
- Tests approved for equivalence validation
- Test data ready for comparative testing
- Ready for code generation with equivalence validation

---

## Verification Criteria

### Phase 4-ATX.0 Verification
```
CHECK test_specification_exists(domain_name, entrypoint_name):
    draft_path = {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
    RETURN file_exists(draft_path)

CHECK legacy_code_coverage_complete(domain_name, entrypoint_name):
    atx_entrypoint = load_atx_entrypoint(domain_name, entrypoint_name)
    test_spec = load_test_specification(domain_name, entrypoint_name)
    
    legacy_programs = atx_entrypoint.functionality_flow.get_programs()
    FOR EACH program IN legacy_programs:
        has_test = any(tc.legacy_programs contains program.name for tc in test_spec.test_cases)
        IF NOT has_test:
            LOG "Legacy program {program.name} has no test coverage"
            RETURN FALSE
    
    RETURN TRUE

CHECK test_data_sets_complete(domain_name, entrypoint_name):
    test_data_path = {{ATX_TEST_GENERATION_TEST_DATA}}/{domain_name}-{entrypoint_name}-test-data.json
    IF NOT file_exists(test_data_path):
        RETURN FALSE
    
    test_data = load_json(test_data_path)
    test_spec = load_test_specification(domain_name, entrypoint_name)
    
    FOR EACH test_case IN test_spec.test_cases:
        has_data = test_data.has_data_for_test(test_case.id)
        IF NOT has_data:
            LOG "Test case {test_case.id} has no test data"
            RETURN FALSE
    
    RETURN TRUE

CHECK comparative_scenarios_defined(domain_name, entrypoint_name):
    test_spec = load_test_specification(domain_name, entrypoint_name)
    
    FOR EACH test_case IN test_spec.test_cases:
        has_legacy_output = test_case.has_field("expected_legacy_output")
        has_modern_output = test_case.has_field("expected_modern_output")
        has_comparison = test_case.has_field("comparison_criteria")
        
        IF NOT (has_legacy_output AND has_modern_output AND has_comparison):
            LOG "Test case {test_case.id} missing comparative scenario elements"
            RETURN FALSE
    
    RETURN TRUE

CHECK traceability_to_legacy_complete(domain_name, entrypoint_name):
    traceability_path = {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-legacy-traceability.md
    RETURN file_exists(traceability_path) AND file_not_empty(traceability_path)

CHECK equivalence_validation_points_defined(domain_name, entrypoint_name):
    test_spec = load_test_specification(domain_name, entrypoint_name)
    
    FOR EACH test_case IN test_spec.test_cases:
        has_validation_points = test_case.has_field("equivalence_validation_points")
        IF NOT has_validation_points OR len(test_case.equivalence_validation_points) == 0:
            LOG "Test case {test_case.id} missing equivalence validation points"
            RETURN FALSE
    
    RETURN TRUE
```

### Phase 4-ATX.0.1 Verification
```
CHECK review_report_exists(domain_name, entrypoint_name):
    review_path = {{ATX_TEST_GENERATION_REVIEW}}/atx-test-generation-{domain_name}-{entrypoint_name}-review.md
    RETURN file_exists(review_path)

CHECK approval_decision_documented(domain_name, entrypoint_name):
    review_report = load_review_report(domain_name, entrypoint_name)
    RETURN review_report.has_field("decision") AND 
           review_report.decision IN ["APPROVED", "REVISE", "REJECT"]

CHECK approved_specification_exists(domain_name, entrypoint_name):
    approved_path = {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-approved.md
    RETURN file_exists(approved_path)

CHECK draft_archived_to_review_folder(domain_name, entrypoint_name):
    archived_path = {{ATX_TEST_GENERATION_REVIEW}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
    original_path = {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
    RETURN file_exists(archived_path) AND NOT file_exists(original_path)
```

---

## Error Handling and Rework

### Rework Scenarios

#### Scenario 1: Incomplete Legacy Code Coverage (Return to Phase 4-ATX.0)
**Triggers**:
- Legacy programs not covered by tests
- Missing test scenarios for legacy code paths
- Insufficient edge case coverage

**Actions**:
1. Document coverage gaps in review report
2. Update Phase 4-ATX.0 task with specific coverage requirements
3. Re-assign development_specialist_test_generation
4. Re-execute Phase 4-ATX.0 with focus on coverage gaps
5. Re-verify coverage completeness

#### Scenario 2: Incomplete Test Data (Return to Phase 4-ATX.0)
**Triggers**:
- Missing input/output pairs
- Unrealistic test data
- Insufficient data variation

**Actions**:
1. Document test data issues in review report
2. Re-assign development_specialist_test_generation
3. Re-execute Phase 4-ATX.0 to complete test data
4. Re-verify test data completeness

#### Scenario 3: Missing Equivalence Validation Points (Return to Phase 4-ATX.0)
**Triggers**:
- Test cases without clear equivalence criteria
- Missing comparison points
- Ambiguous validation expectations

**Actions**:
1. Document validation issues in review report
2. Re-assign development_specialist_test_generation
3. Re-execute Phase 4-ATX.0 to define validation points
4. Re-verify equivalence validation completeness

#### Scenario 4: Critical Issues (Escalate to Human)
**Triggers**:
- ATX analysis ambiguities preventing test creation
- Complex legacy code requiring manual review
- Conflicting behaviors in legacy code

**Actions**:
1. Document critical issues in error log
2. Escalate to human supervisor with detailed explanation
3. Halt workpackage processing
4. Await human guidance before proceeding

---

## Progress Tracking

### Status Tracking

**JSON File**: `{{ATX_TEST_GENERATION_STATUS}}`

**Update Frequency**: After each workpackage completion and after review

### Resumption Logic

When resuming after interruption:
1. Read {{ATX_TEST_GENERATION_STATUS}}
2. Check which domains are completed
3. Check which entrypoints are completed
4. Check which entrypoints are in review
5. Resume from first incomplete entrypoint or review step

---

## Quality Gates

### Phase 4-ATX.0 Quality Gate
**Criteria**:
- [ ] All legacy programs have test coverage
- [ ] Test data sets are complete and realistic
- [ ] Comparative scenarios defined for all tests
- [ ] Equivalence validation points are clear
- [ ] Traceability to legacy code is complete
- [ ] Edge cases and error handling covered

**Gate Decision**:
- **PASS**: Proceed to Phase 4-ATX.0.1
- **FAIL**: Rework Phase 4-ATX.0 or escalate

### Phase 4-ATX.0.1 Quality Gate
**Criteria**:
- [ ] All test specifications reviewed
- [ ] Legacy code coverage verified
- [ ] Test data completeness verified
- [ ] Equivalence validation points verified
- [ ] All test specifications approved
- [ ] No blocking issues

**Gate Decision**:
- **PASS**: Proceed to Phase 5 (Code Generation)
- **FAIL**: Rework Phase 4-ATX.0 or escalate

---

## Configuration and Path Variables

### Input Paths
```
ATX Analysis Base Path = /Users/kerimman/carddemo_migration_new/input/legacy/atx
ATX App Domain = /Users/kerimman/carddemo_migration_new/input/legacy/atx/app-domain
ATX Data Analysis = /Users/kerimman/carddemo_migration_new/input/legacy/atx/data-analysis
ATX Dependency Analysis = /Users/kerimman/carddemo_migration_new/input/legacy/atx/dependency-analysis
Legacy Source Code = /Users/kerimman/carddemo_migration_new/input/legacy/legacy_code/carddemoV2
Workpackage Planning = /Users/kerimman/carddemo_migration_new/output/analysis/workpackages/Workpackage_Planning.json
```

### Output Paths
```
ATX Test Generation Root = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx
ATX Test Specs = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx/specs
ATX Test Data = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx/test_data
ATX Test Traceability = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx/traceability
ATX Test Review = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx/review
ATX Test Status = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx/progress/ATX_Test_Generation_Status.json
ATX Test Errors = /Users/kerimman/carddemo_migration_new/output/specifications/test_cases/atx/logs/ATX_Test_Generation_Errors.json
```

---

## Supervisor Responsibilities

### Pre-Execution
1. Verify all prerequisites exist (ATX analysis, legacy code)
2. Verify all path variables are resolved
3. Verify agents are available
4. Create output directories if needed
5. Initialize progress tracking

### During Execution
1. Assign appropriate agent for each sub-phase
2. Provide task document from /Users/kerimman/carddemo_migration_new/prompts
3. Monitor execution progress
4. Verify completion against quality gates
5. Handle errors and rework scenarios
6. Update progress tracking
7. Escalate critical issues

### Post-Execution
1. Verify all test specifications approved
2. Verify all quality gates passed
3. Generate final summary
4. Archive artifacts
5. Prepare handoff to Phase 5 (Code Generation)

---

## Success Criteria

Phase 4-ATX is considered complete when:
- [ ] All domains have been processed
- [ ] All entrypoints have ATX-based test specifications
- [ ] All test specifications reviewed and approved
- [ ] All legacy programs (from ATX BRE) covered by tests
- [ ] Test data sets complete and realistic
- [ ] Equivalence validation points defined
- [ ] Traceability to legacy code and ATX BRE complete
- [ ] No blocking issues remain
- [ ] Progress tracking shows 100% completion
- [ ] Ready for Phase 5 (Code Generation)

---

## Notes for Supervisor

**Critical Success Factors**:
1. **Behavioral Equivalence Focus**: Tests must verify same behavior, not just same requirements
2. **Comprehensive Coverage**: All legacy code paths must be tested
3. **Realistic Test Data**: Use actual legacy data patterns
4. **Clear Validation Points**: Equivalence criteria must be explicit
5. **Traceability**: Every test must link to specific legacy code

**Common Pitfalls to Avoid**:
1. Testing requirements instead of actual legacy behavior
2. Missing edge cases that exist in legacy code
3. Unrealistic test data that doesn't match legacy patterns
4. Ambiguous equivalence criteria
5. Incomplete legacy code coverage

**When to Escalate**:
1. ATX analysis ambiguities preventing test creation
2. Complex legacy code requiring manual review
3. Conflicting behaviors in legacy code
4. Data migration risks requiring human decision
5. Repeated rework cycles (more than 2 iterations per workpackage)

---

## End of Master Orchestration Document
