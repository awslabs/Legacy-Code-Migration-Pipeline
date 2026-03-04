# Phase 4-ATX.0.1: ATX-Based Functional Equivalence Test Case Review

---

## Orchestration Information

**Phase**: Phase 4-ATX - ATX-Based Functional Equivalence Test Generation
**Step**: Step 4-ATX.0.1 - Test Case Review
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_reviewer_test_generation

### Expected Deliverables

1. **Approved Test Specification**
   - File: {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-approved.md
   - Description: Validated and approved functional equivalence test specification

2. **Archived Draft** (moved to review folder)
   - File: {{ATX_TEST_GENERATION_REVIEW}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
   - Description: Original draft moved to review folder for audit trail

3. **Review Report**
   - File: {{ATX_TEST_GENERATION_REVIEW}}/atx-test-generation-{domain_name}-{entrypoint_name}-review.md
   - Description: Detailed review findings, changes made, and approval status

4. **Progress Tracking**
   - File: {{ATX_TEST_GENERATION_STATUS}}
   - Description: Updated progress tracking with review completion status

### Success Criteria
- [ ] All test specifications reviewed and validated
- [ ] Complete coverage of legacy programs (from ATX BRE) verified
- [ ] Complete coverage of ATX BRE business functions verified
- [ ] Test data completeness and realism verified
- [ ] Equivalence validation points are clear and measurable
- [ ] Comparative test scenarios verified
- [ ] Traceability to legacy code and ATX BRE verified
- [ ] All review reports completed
- [ ] Test specifications approved for code generation
- [ ] Ready for Phase 5 (Code Generation)

---

## Context

### Input Locations
- **Test specification (draft)**: `{{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md`
- **Test data sets**: `{{ATX_TEST_GENERATION_TEST_DATA}}/{domain_name}-{entrypoint_name}-test-data.json`
- **Legacy traceability**: `{{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-legacy-traceability.md`
- **Coverage report**: `{{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-coverage-notes.md`
- **ATX BRE analysis**: `{{ATX_APPLICATION_ANALYSIS}}/{domain_name}/`
- **Legacy source code**: `{{SOURCE_CODE}}/`

### Output Locations
- **Approved test specifications**: `{{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-approved.md`
- **Archived drafts**: `{{ATX_TEST_GENERATION_REVIEW}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md`
- **Review reports**: `{{ATX_TEST_GENERATION_REVIEW}}/atx-test-generation-{domain_name}-{entrypoint_name}-review.md`
- **Progress tracking**: `{{ATX_TEST_GENERATION_STATUS}}`
- **Error logs** (if needed): `{{ATX_TEST_GENERATION_ERRORS}}`

---

## Objective

Review and validate ATX-based functional equivalence test specifications to ensure complete legacy code coverage, complete ATX BRE business function coverage, realistic test data, clear equivalence validation points, and readiness for code generation.

**CRITICAL REVIEW PRINCIPLES**:
1. **Legacy Code Coverage** - Verify all legacy programs and code paths are tested
2. **Business Function Coverage** - Verify all ATX BRE business functions are tested
3. **Test Data Realism** - Ensure test data matches actual legacy data patterns
4. **Equivalence Clarity** - Confirm validation points are explicit and measurable
5. **Comparative Completeness** - Verify all tests support legacy vs modern comparison
6. **Traceability Verification** - Confirm all tests link to specific legacy code and ATX BRE

---

## Instructions

### 1. Preparation and Review Planning
1. Review the list of domains and entrypoints requiring test case review
2. For each entrypoint, gather all relevant materials:
   - Test case specification (draft)
   - Test data sets
   - Legacy code traceability matrix
   - Coverage report
   - ATX BRE entrypoint analysis
   - Legacy source code
3. Prioritize review based on domain/entrypoint criticality
4. Prepare coverage verification checklist
5. Prepare quality assessment checklist

### 2. Legacy Code Coverage Verification

**Purpose**: Verify complete coverage of all legacy programs and code paths

#### 2.1 Legacy Program Coverage Check
1. **Identify legacy programs in scope from ATX BRE**:
   - Review ATX BRE entrypoint JSON functionality_flow
   - List all legacy programs that should be covered
   - Count total legacy programs

2. **Verify test coverage for each program**:
   - For each legacy program:
     - Search test specification for program reference
     - Verify at least one test case covers this program
     - Check if test cases adequately cover program behavior
   - Record coverage status (covered/not covered)

3. **Calculate program coverage**:
   - Formula: (covered programs / total programs) × 100
   - **Program Coverage**: [percentage]

4. **Coverage assessment**:
   - Coverage = 100%: Pass
   - Coverage < 100%: Fail - identify missing coverage

**If coverage < 100%**: Document missing programs in review report and return for revision.

#### 2.2 ATX BRE Business Function Coverage Check
1. **Identify business functions from ATX BRE**:
   - Review ATX BRE entrypoint JSON summary.business_functions
   - List all business functions
   - Count total business functions

2. **Verify test coverage for each business function**:
   - For each business function:
     - Search test specification for business function reference
     - Verify at least one test case covers this function
     - Check if test cases adequately test the function
   - Record coverage status (covered/not covered)

3. **Calculate business function coverage**:
   - Formula: (covered functions / total functions) × 100
   - **Business Function Coverage**: [percentage]

4. **Coverage assessment**:
   - Coverage = 100%: Pass
   - Coverage < 100%: Fail - identify missing coverage

**If coverage < 100%**: Document missing business functions in review report and return for revision.

#### 2.3 Code Path Coverage Check
1. **For each legacy program**:
   - Review legacy source code
   - Identify main code paths
   - Identify error handling paths
   - Identify edge case paths

2. **Verify test coverage for each path**:
   - Main flow paths: Verify test cases exist
   - Error handling paths: Verify error test cases exist
   - Edge case paths: Verify boundary test cases exist
   - Record coverage status

3. **Calculate path coverage**:
   - Formula: (covered paths / total paths) × 100
   - **Path Coverage**: [percentage]

4. **Coverage assessment**:
   - Coverage >= 90%: Pass
   - Coverage < 90%: Fail - identify missing paths

**If coverage < 90%**: Document missing paths in review report and return for revision.

### 3. Test Data Quality Assessment

**Purpose**: Ensure test data is realistic and complete

#### 3.1 Test Data Completeness Check
1. **Load test data JSON**:
   - Read `{{ATX_TEST_GENERATION_TEST_DATA}}/{domain_name}-{entrypoint_name}-test-data.json`
   - Count test data sets
   - Verify one data set per test case

2. **For each test case**:
   - Verify input data is specified
   - Verify expected legacy output is specified
   - Verify expected modern output is specified
   - Verify comparison criteria are specified

3. **Data completeness assessment**:
   - All test cases have complete data: Pass
   - Any test case missing data: Fail

**If incomplete**: Document missing data in review report and return for revision.

#### 3.2 Test Data Realism Check
1. **Review test data values**:
   - Compare with legacy data patterns from ATX analysis
   - Check data types match legacy formats
   - Verify data values are realistic
   - Check for edge cases (nulls, zeros, spaces, max values)

2. **Verify data variation**:
   - Multiple scenarios with different data values
   - Coverage of valid value ranges
   - Coverage of invalid values (for error tests)
   - Coverage of boundary values

3. **Data realism assessment**:
   - Data matches legacy patterns: Pass
   - Data is unrealistic or incomplete: Fail

**If unrealistic**: Document data quality issues in review report and return for revision.

### 4. Equivalence Validation Point Verification

**Purpose**: Verify equivalence criteria are explicit and measurable

#### 4.1 Validation Point Completeness Check
1. **For each test case**:
   - Verify equivalence validation points are defined
   - Check if validation points cover all outputs
   - Verify comparison criteria are specified
   - Check if tolerances are defined (where applicable)

2. **Validation point assessment**:
   - All test cases have validation points: Pass
   - Any test case missing validation points: Fail

**If incomplete**: Document missing validation points in review report and return for revision.

#### 4.2 Validation Point Clarity Check
1. **For each validation point**:
   - Verify comparison method is explicit:
     - Exact match
     - Numeric tolerance
     - Format equivalence
     - Semantic equivalence
   - Check if criteria are measurable
   - Verify special handling is documented

2. **Clarity assessment**:
   - All validation points are clear: Pass
   - Any validation point is ambiguous: Fail

**If ambiguous**: Document clarity issues in review report and return for revision.

### 5. Comparative Test Scenario Verification

**Purpose**: Verify all tests support legacy vs modern comparison

#### 5.1 Comparative Structure Check
1. **For each test case**:
   - Verify test includes expected legacy output
   - Verify test includes expected modern output
   - Verify comparison criteria are defined
   - Check if test can be executed on both systems

2. **Comparative structure assessment**:
   - All test cases support comparison: Pass
   - Any test case missing comparative elements: Fail

**If incomplete**: Document missing comparative elements in review report and return for revision.

#### 5.2 Comparison Feasibility Check
1. **For each test case**:
   - Verify test can be executed on legacy system
   - Verify test can be executed on modern system
   - Check if outputs can be compared
   - Verify comparison is automated or manual

2. **Feasibility assessment**:
   - All comparisons are feasible: Pass
   - Any comparison is not feasible: Fail

**If not feasible**: Document feasibility issues in review report and return for revision.

### 6. Traceability Verification

**Purpose**: Verify all tests are traceable to specific legacy code

#### 6.1 Test-to-Code Traceability Check
1. **For each test case**:
   - Verify legacy program reference exists
   - Check if code section is identified (line numbers)
   - Verify copybook references (if applicable)
   - Check JCL references (if applicable)
   - Verify ATX analysis references

2. **Traceability assessment**:
   - All test cases have complete traceability: Pass
   - Any test case missing traceability: Fail

**If incomplete**: Document missing traceability in review report and return for revision.

#### 6.2 Code-to-Test Traceability Check
1. **For each legacy program**:
   - Verify traceability matrix includes program
   - Check if all code sections are mapped to tests
   - Verify coverage percentage is documented

2. **Reverse traceability assessment**:
   - All legacy programs have test mappings: Pass
   - Any legacy program missing mappings: Fail

**If incomplete**: Document missing mappings in review report and return for revision.

### 7. Test Specification Quality Assessment

**Purpose**: Ensure test specifications are clear and executable

#### 7.1 Test Case Clarity Check
1. **For each test case**:
   - Verify test ID follows naming convention
   - Check description is clear and unambiguous
   - Verify test type is specified
   - Check priority is specified
   - Verify preconditions are clear
   - Check test steps are detailed
   - Verify expected results are specific

2. **Clarity assessment**:
   - All test cases are clear: Pass
   - Any test case is unclear: Fail

**If unclear**: Document clarity issues in review report and return for revision.

#### 7.2 Test Executability Check
1. **For each test case**:
   - Verify test can be executed as written
   - Check if preconditions are achievable
   - Verify test data is sufficient
   - Check if test steps are actionable
   - Verify expected results are verifiable

2. **Executability assessment**:
   - All test cases are executable: Pass
   - Any test case is not executable: Fail

**If not executable**: Document executability issues in review report and return for revision.

### 8. Review Decision

Based on all verification checks, make one of three decisions:

#### Decision 1: APPROVED
**Criteria**:
- Legacy code coverage = 100% for programs, >= 90% for paths
- Test data is complete and realistic
- Equivalence validation points are clear and measurable
- All tests support comparative testing
- Traceability is complete
- Test specifications are clear and executable

**Actions**:
1. Create approved test specification:
   - Copy draft to approved file
   - Place in main specs folder
2. Archive draft:
   - Move draft to review folder
3. Create review report with approval
4. Update progress tracking:
   - Set status to "Approved"
   - Set ready_for_code_generation to true

#### Decision 2: REVISE
**Criteria**:
- Minor issues that can be corrected
- Coverage gaps that can be filled
- Quality issues that can be improved
- Traceability issues that can be fixed

**Actions**:
1. Create review report with revision feedback
2. Keep draft in main folder
3. Update progress tracking:
   - Set status to "Revision Requested"
   - Document revision feedback
4. Return to Phase 4-ATX.0 with feedback

#### Decision 3: REJECT
**Criteria**:
- Major issues that cannot be easily corrected
- Fundamental misunderstanding of legacy behavior
- Incomplete or inadequate coverage
- Critical quality issues

**Actions**:
1. Create review report with rejection rationale
2. Archive draft to review folder
3. Update progress tracking:
   - Set status to "Rejected"
   - Document rejection rationale
4. Escalate to human supervisor

### 9. Review Report Creation

Create review report: `{{ATX_TEST_GENERATION_REVIEW}}/atx-test-generation-{domain_name}-{entrypoint_name}-review.md`

**Report Structure**:
```markdown
# ATX-Based Functional Equivalence Test Review Report

## Document Control
- **Domain**: {domain_name}
- **Entrypoint**: {entrypoint_name}
- **Document Title**: {from ATX BRE}
- **Review Date**: [Date]
- **Reviewer**: development_reviewer_test_generation
- **Review Decision**: [APPROVED/REVISE/REJECT]

## Review Summary
[Brief summary of review findings and decision]

## Legacy Code Coverage Results

### Program Coverage
- Total Legacy Programs: [count]
- Covered Programs: [count]
- Coverage Percentage: [percentage]
- Status: [Pass/Fail]
- Missing Coverage: [list if any]

### ATX BRE Business Function Coverage
- Total Business Functions: [count]
- Covered Functions: [count]
- Coverage Percentage: [percentage]
- Status: [Pass/Fail]
- Missing Coverage: [list if any]

### Code Path Coverage
- Total Code Paths: [count]
- Covered Paths: [count]
- Coverage Percentage: [percentage]
- Status: [Pass/Fail]
- Missing Paths: [list if any]

## Test Data Quality Results

### Data Completeness
- Total Test Cases: [count]
- Test Cases with Complete Data: [count]
- Status: [Pass/Fail]
- Missing Data: [list if any]

### Data Realism
- Data Matches Legacy Patterns: [Yes/No]
- Data Variation Adequate: [Yes/No]
- Status: [Pass/Fail]
- Issues Found: [list if any]

## Equivalence Validation Results

### Validation Point Completeness
- Test Cases with Validation Points: [count]
- Test Cases Missing Validation Points: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

### Validation Point Clarity
- Clear Validation Points: [count]
- Ambiguous Validation Points: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

## Comparative Test Scenario Results

### Comparative Structure
- Test Cases Supporting Comparison: [count]
- Test Cases Missing Comparative Elements: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

### Comparison Feasibility
- Feasible Comparisons: [count]
- Infeasible Comparisons: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

## Traceability Results

### Test-to-Code Traceability
- Test Cases with Complete Traceability: [count]
- Test Cases Missing Traceability: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

### Test-to-ATX-BRE Traceability
- Test Cases with ATX BRE References: [count]
- Test Cases Missing ATX BRE References: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

### Code-to-Test Traceability
- Legacy Programs with Test Mappings: [count]
- Legacy Programs Missing Mappings: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

## Test Specification Quality Results

### Test Case Clarity
- Clear Test Cases: [count]
- Unclear Test Cases: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

### Test Executability
- Executable Test Cases: [count]
- Non-Executable Test Cases: [count]
- Status: [Pass/Fail]
- Issues Found: [list if any]

## Detailed Findings

### Critical Issues
[List critical issues that must be addressed]

### High Priority Issues
[List high priority issues]

### Medium Priority Issues
[List medium priority issues]

### Low Priority Issues
[List low priority issues]

## Revision Guidance (if decision = REVISE)
[Specific guidance for addressing issues]

## Rejection Rationale (if decision = REJECT)
[Detailed explanation of why specification was rejected]

## Approval Confirmation (if decision = APPROVED)
- Approved Date: [Date]
- Approved By: development_reviewer_test_generation
- Ready for Code Generation: Yes

## Next Steps
[What happens next based on decision]
```

### 10. Progress Tracking Update

Update progress tracking with review results.

---

## Quality Criteria

### Legacy Code Coverage Quality
- 100% legacy program coverage (from ATX BRE functionality_flow)
- 100% ATX BRE business function coverage
- >= 90% code path coverage
- All main flows tested
- All error paths tested
- Edge cases covered

### Test Data Quality
- Complete data for all test cases
- Realistic data matching legacy patterns
- Sufficient data variation
- Edge cases included

### Equivalence Validation Quality
- All validation points defined
- Comparison criteria are explicit
- Tolerances specified where needed
- Validation is measurable

### Traceability Quality
- All tests link to legacy code
- All tests link to ATX BRE business functions
- All legacy programs mapped to tests
- Code sections identified
- ATX BRE referenced

### Test Specification Quality
- All test cases are clear
- All test cases are executable
- Preconditions are achievable
- Expected results are verifiable

---

## Error Handling

### Common Error Scenarios

1. **Incomplete Coverage**
   - Detection: Coverage < required thresholds
   - Recovery: Document gaps in review report
   - Decision: REVISE with specific coverage requirements

2. **Poor Test Data Quality**
   - Detection: Unrealistic or incomplete data
   - Recovery: Document data issues in review report
   - Decision: REVISE with specific data requirements

3. **Unclear Equivalence Criteria**
   - Detection: Ambiguous validation points
   - Recovery: Document clarity issues in review report
   - Decision: REVISE with specific validation requirements

4. **Missing Traceability**
   - Detection: Tests not linked to legacy code
   - Recovery: Document traceability gaps in review report
   - Decision: REVISE with specific traceability requirements

### Error Reporting Format
**File**: `{{ATX_TEST_GENERATION_ERRORS}}`
- Include: timestamp, error type, context, attempted resolution

---

## End of Phase 4-ATX.0.1 Document
