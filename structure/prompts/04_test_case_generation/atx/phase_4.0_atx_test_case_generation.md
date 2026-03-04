# Phase 4-ATX.0: ATX-Based Functional Equivalence Test Case Generation

---

## Orchestration Information

**Phase**: Phase 4-ATX - ATX-Based Functional Equivalence Test Generation
**Step**: Step 4-ATX.0 - Test Case Generation
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_specialist_test_generation

### Expected Deliverables

1. **Functional Equivalence Test Specification (Draft)**
   - File: {{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md
   - Description: Test cases for verifying functional equivalence between legacy and modern systems

2. **Test Data Sets**
   - File: {{ATX_TEST_GENERATION_TEST_DATA}}/{domain_name}-{entrypoint_name}-test-data.json
   - Description: Input/output pairs extracted from legacy code and ATX BRE analysis

3. **Legacy Code Traceability Matrix**
   - File: {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-legacy-traceability.md
   - Description: Mapping of test cases to legacy programs, modules, and code sections

4. **Coverage Report**
   - File: {{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-coverage-notes.md
   - Description: Analysis of legacy code coverage and test scenario completeness

5. **Progress Tracking**
   - File: {{ATX_TEST_GENERATION_STATUS}}
   - Description: Test generation progress and status tracking

6. **Error Reports** (if applicable)
   - File: {{ATX_TEST_GENERATION_ERRORS}}
   - Description: Documentation of errors and issues encountered

### Success Criteria
- [ ] All legacy programs identified in ATX BRE entrypoint have test coverage
- [ ] Test data sets include realistic input/output pairs
- [ ] Comparative test scenarios defined (legacy vs modern)
- [ ] Equivalence validation points are explicit and measurable
- [ ] Edge cases and error handling scenarios included
- [ ] Traceability to legacy code and ATX BRE is complete
- [ ] All deliverables produced at specified paths
- [ ] Ready for review

---

## Context

### Input Locations
- **ATX BRE entrypoint analysis**: `{{ATX_APPLICATION_ANALYSIS}}/{domain_name}/entrypoint-{entrypoint_name}/entrypoint-{entrypoint_name}.json`
- **ATX domain analysis**: `{{ATX_APPLICATION_ANALYSIS}}/{domain_name}/{domain_name}.json`
- **ATX data dictionary**: `{{ATX_DATA_DICTIONARY}}/`
- **ATX data lineage**: `{{ATX_DATA_LINEAGE}}/`
- **Legacy source code**: `{{SOURCE_CODE}}/`

### Output Locations
- **Test specifications**: `{{ATX_TEST_GENERATION_SPECS}}/`
- **Test data**: `{{ATX_TEST_GENERATION_TEST_DATA}}/`
- **Traceability**: `{{ATX_TEST_GENERATION_TRACEABILITY}}/`
- **Progress tracking**: `{{ATX_TEST_GENERATION_PROGRESS}}/`
- **Error logs**: `{{ATX_TEST_GENERATION_LOGS}}/`

---

## Objective

Generate functional equivalence test cases from ATX BRE entrypoint analysis and legacy source code to verify that modernized systems produce identical outputs to legacy systems for the same inputs. Focus on behavioral equivalence, data transformation validation, and comparative testing scenarios.

**CRITICAL PRINCIPLES**:
1. **Behavioral Equivalence**: Test actual legacy behavior, not intended requirements
2. **Comparative Testing**: Every test must support legacy vs modern comparison
3. **Realistic Data**: Use actual legacy data patterns and edge cases
4. **Explicit Validation**: Equivalence criteria must be measurable and specific
5. **Complete Coverage**: All legacy code paths must be tested

---

## Instructions

### 1. ATX BRE Entrypoint Analysis Review and Legacy Code Mapping

**Purpose**: Understand legacy system behavior from ATX BRE entrypoint analysis and source code

#### 1.1 Review ATX BRE Entrypoint Analysis
1. **Load ATX BRE entrypoint JSON**:
   - Read `{{ATX_APPLICATION_ANALYSIS}}/{domain_name}/entrypoint-{entrypoint_name}/entrypoint-{entrypoint_name}.json`
   - Extract document_title, document_name, type
   - Review summary.overview for high-level understanding
   - Extract summary.business_functions list
   - Review summary.environment_summary for technical context

2. **Analyze functionality flow**:
   - Review functionality_flow section
   - Identify all programs in the flow (program_name, program_overview)
   - Document called_programs for each program
   - Understand program interactions and sequence

3. **Extract business functions**:
   - List all business_functions from summary
   - Understand what each function does
   - Identify validation rules and business logic
   - Note error handling patterns

#### 1.2 Review ATX Domain Analysis
1. **Load ATX domain JSON**:
   - Read `{{ATX_APPLICATION_ANALYSIS}}/{domain_name}/{domain_name}.json`
   - Extract domain-level context
   - Understand domain scope and boundaries
   - Note domain-level business rules

#### 1.3 Review ATX Data Dictionary
1. **Load ATX data dictionary artifacts**:
   - Read files in `{{ATX_DATA_DICTIONARY}}/`
   - Extract data structures and schemas
   - Identify data field definitions
   - Document data types and formats
   - Note data validation rules

#### 1.4 Review ATX Data Lineage
1. **Load ATX data lineage artifacts**:
   - Read files in `{{ATX_DATA_LINEAGE}}/`
   - Extract data flows and transformations
   - Identify source and target data elements
   - Document transformation logic
   - Note data dependencies

#### 1.5 Map to Legacy Source Code
1. **Identify relevant legacy programs from ATX BRE**:
   - Extract program names from functionality_flow
   - For each program, locate source files:
     - COBOL programs in `{{SOURCE_CODE}}/app/cbl/`
     - JCL scripts in `{{SOURCE_CODE}}/app/jcl/`
     - BMS maps in `{{SOURCE_CODE}}/app/bms/`
     - Copybooks in `{{SOURCE_CODE}}/app/cpy/`

2. **Analyze legacy code for each program**:
   - Read program source code
   - Identify input parameters and data structures
   - Identify output parameters and data structures
   - Extract business logic and calculations
   - Document error handling and edge cases
   - Note data validation rules
   - Identify external calls and dependencies

3. **Create legacy code inventory**:
   - List all programs in scope for entrypoint
   - Document program purpose and behavior
   - Map programs to ATX BRE business functions
   - Identify test-critical code sections

### 2. Test Scenario Identification

**Purpose**: Identify all scenarios requiring functional equivalence testing based on ATX BRE business functions

#### 2.1 Main Flow Scenarios (from ATX BRE business_functions)
1. **For each business function in ATX BRE**:
   - Identify happy path (normal processing)
   - Define typical input data
   - Define expected output data
   - Document processing steps
   - Note data transformations

2. **Create main flow test scenarios**:
   - Test ID: {domain_name}-{entrypoint_name}-TC-001 (main flow)
   - Business function reference
   - Input data specification
   - Expected legacy output
   - Expected modern output (should match legacy)
   - Comparison criteria

#### 2.2 Error Handling Scenarios
1. **For each legacy program in functionality_flow**:
   - Identify error conditions from code
   - Extract error messages and codes
   - Document error handling logic
   - Note error recovery mechanisms

2. **Create error handling test scenarios**:
   - Test ID: {domain_name}-{entrypoint_name}-TC-0XX (error scenarios)
   - Invalid input data specification
   - Expected error behavior (legacy)
   - Expected error behavior (modern - should match)
   - Error message comparison criteria

#### 2.3 Boundary and Edge Case Scenarios
1. **For each legacy program**:
   - Identify boundary conditions from code
   - Extract min/max values and limits
   - Document edge case handling
   - Note special value processing (zeros, nulls, spaces)

2. **Create boundary test scenarios**:
   - Test ID: {domain_name}-{entrypoint_name}-TC-1XX (boundary scenarios)
   - Boundary input data specification
   - Expected boundary behavior (legacy)
   - Expected boundary behavior (modern - should match)
   - Boundary validation criteria

#### 2.4 Data Transformation Scenarios
1. **From ATX data lineage**:
   - Identify all data transformations
   - Extract transformation logic from legacy code
   - Document input/output data formats
   - Note calculation formulas and algorithms

2. **Create data transformation test scenarios**:
   - Test ID: {domain_name}-{entrypoint_name}-TC-2XX (transformation scenarios)
   - Input data before transformation
   - Expected output data after transformation (legacy)
   - Expected output data after transformation (modern - should match)
   - Transformation validation criteria

#### 2.5 Integration Scenarios
1. **From ATX BRE functionality_flow**:
   - Identify program interactions (called_programs)
   - Extract integration patterns from legacy code
   - Document data exchange formats
   - Note integration error handling

2. **Create integration test scenarios**:
   - Test ID: {domain_name}-{entrypoint_name}-TC-3XX (integration scenarios)
   - Integration input data specification
   - Expected integration behavior (legacy)
   - Expected integration behavior (modern - should match)
   - Integration validation criteria

### 3. Test Data Extraction and Generation

**Purpose**: Create realistic test data sets based on legacy code and ATX analysis

#### 3.1 Extract Sample Data from Legacy Code
1. **Identify data sources**:
   - Sample data in `{{SOURCE_CODE}}/app/data/`
   - Data definitions in copybooks
   - Hardcoded values in COBOL programs
   - Test data in JCL scripts

2. **Extract data patterns**:
   - Data types and formats
   - Valid value ranges
   - Common data values
   - Special values (defaults, nulls, etc.)

#### 3.2 Generate Test Data Sets
1. **For each test scenario**:
   - Create input data set matching legacy format
   - Include realistic data values
   - Cover all data fields
   - Include edge cases and boundary values

2. **Document expected outputs**:
   - Expected legacy system output
   - Expected modern system output (should match legacy)
   - Comparison criteria for each output field

3. **Create test data JSON**:
   ```json
   {
     "domain_name": "{domain_name}",
     "entrypoint_name": "{entrypoint_name}",
     "document_title": "{from ATX BRE}",
     "test_data_sets": [
       {
         "test_case_id": "{domain_name}-{entrypoint_name}-TC-001",
         "scenario": "Main flow - valid transaction",
         "business_function": "{from ATX BRE business_functions}",
         "input_data": {
           "field1": "value1",
           "field2": "value2"
         },
         "expected_legacy_output": {
           "field1": "result1",
           "field2": "result2"
         },
         "expected_modern_output": {
           "field1": "result1",
           "field2": "result2"
         },
         "comparison_criteria": [
           "field1 must match exactly",
           "field2 must match exactly"
         ]
       }
     ]
   }
   ```

### 4. Equivalence Validation Point Definition

**Purpose**: Define explicit, measurable criteria for verifying functional equivalence

#### 4.1 Output Comparison Criteria
1. **For each test case**:
   - Identify all output fields
   - Define comparison method for each field:
     - Exact match (strings, IDs)
     - Numeric tolerance (calculations with rounding)
     - Format equivalence (dates, times)
     - Semantic equivalence (different format, same meaning)

2. **Document validation points**:
   - Field-by-field comparison criteria
   - Acceptable tolerances (if any)
   - Special handling for timestamps, generated IDs, etc.

#### 4.2 Behavior Comparison Criteria
1. **For each test case**:
   - Define expected system behavior
   - Document side effects (database updates, file writes, etc.)
   - Specify error handling expectations
   - Note performance expectations (if critical)

2. **Document behavioral validation**:
   - State changes that must match
   - External system interactions that must match
   - Error conditions that must match
   - Transaction boundaries that must match

#### 4.3 Data Transformation Validation
1. **For each transformation**:
   - Define transformation algorithm
   - Specify input/output formats
   - Document calculation precision
   - Note rounding rules

2. **Document transformation validation**:
   - Step-by-step transformation verification
   - Intermediate value checks (if needed)
   - Final result comparison criteria

### 5. Test Case Specification Creation

**Purpose**: Create comprehensive test specification document

#### 5.1 Document Structure
Create test specification: `{{ATX_TEST_GENERATION_SPECS}}/{domain_name}-{entrypoint_name}-atx-tests-draft.md`

**Structure**:
```markdown
# Functional Equivalence Test Specification

## Document Control
- Domain: {domain_name}
- Entrypoint: {entrypoint_name}
- Document Title: {from ATX BRE}
- Transaction/Program: {document_name from ATX BRE}
- Version: 1.0 (Draft)
- Date: [Date]
- Agent: development_specialist_test_generation

## Test Plan Overview
- Test Objective: Verify functional equivalence between legacy and modern systems
- Test Approach: Comparative testing with input/output validation
- Test Scope: [List legacy programs from ATX BRE functionality_flow]
- Test Data Source: ATX BRE analysis + legacy source code
- Comparison Method: Field-by-field output comparison

## ATX BRE Context
- Business Functions: [List from ATX BRE summary.business_functions]
- Functionality Flow: [List programs from ATX BRE functionality_flow]
- Environment: [From ATX BRE summary.environment_summary]
- Legacy Programs: [List]
- Legacy Data Structures: [List]

## Test Cases

### Test Case: {domain_name}-{entrypoint_name}-TC-001
- **Test ID**: {domain_name}-{entrypoint_name}-TC-001
- **Test Type**: Main Flow / Error Handling / Boundary / Transformation / Integration
- **Priority**: Critical / High / Medium / Low
- **Business Function**: [From ATX BRE business_functions]
- **Description**: [Clear description of what is being tested]
- **Legacy Programs**: [List from ATX BRE functionality_flow]
- **ATX BRE Reference**: [Reference to entrypoint JSON section]

#### Test Scenario
[Detailed description of the test scenario]

#### Preconditions
- [List all preconditions]
- [System state requirements]
- [Data setup requirements]

#### Test Data
- **Input Data**: [Reference to test data JSON]
- **Expected Legacy Output**: [Reference to test data JSON]
- **Expected Modern Output**: [Reference to test data JSON]

#### Test Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

#### Equivalence Validation Points
1. **Output Field 1**: Exact match required
2. **Output Field 2**: Numeric match within 0.01 tolerance
3. **System State**: Database records must match
4. **Error Handling**: Error codes and messages must match

#### Comparison Criteria
- [Detailed comparison criteria for each output]
- [Acceptable tolerances]
- [Special handling notes]

#### Dependencies
- [Dependencies on other test cases]
- [Dependencies on external systems]

#### Legacy Code Traceability
- **COBOL Program**: [Program name and line numbers]
- **Copybook**: [Copybook name]
- **JCL**: [JCL name if applicable]
- **Code Section**: [Specific code section being tested]
- **ATX BRE Business Function**: [Business function name]

---

[Repeat for each test case]

## Traceability Matrix
[See separate traceability document]

## Coverage Analysis
[See separate coverage document]
```

### 6. Legacy Code Traceability Matrix Creation

**Purpose**: Document mapping between test cases and legacy code

Create traceability matrix: `{{ATX_TEST_GENERATION_TRACEABILITY}}/WP-XXX-legacy-traceability.md`

**Structure**:
```markdown
# Legacy Code Traceability Matrix

## Workpackage: WP-XXX

### Legacy Program Coverage

| Legacy Program | Test Cases | Coverage % | Notes |
|---------------|------------|------------|-------|
| PROGRAM1.cbl  | TC-001, TC-002, TC-003 | 100% | All paths covered |
| PROGRAM2.cbl  | TC-004, TC-005 | 85% | Error path X not covered |

### Test Case to Legacy Code Mapping

#### Test Case: WP-XXX-ATX-TC-001
- **Legacy Program**: PROGRAM1.cbl
- **Code Section**: Lines 100-250 (Main processing logic)
- **Copybook**: COPYBOOK1.cpy (Data structures)
- **JCL**: JOB001.jcl (Batch execution)
- **ATX Analysis**: app-domain/analysis-section-1.md

#### Test Case: WP-XXX-ATX-TC-002
[Repeat for each test case]

### Legacy Code to Test Case Mapping

#### PROGRAM1.cbl
- **Lines 100-150**: Covered by TC-001 (main flow)
- **Lines 151-200**: Covered by TC-002 (error handling)
- **Lines 201-250**: Covered by TC-003 (boundary conditions)

[Repeat for each legacy program]
```

### 7. Coverage Analysis and Reporting

**Purpose**: Analyze and document test coverage of legacy code

Create coverage report: `{{ATX_TEST_GENERATION_TRACEABILITY}}/{domain_name}-{entrypoint_name}-coverage-notes.md`

**Analysis**:
1. **Calculate coverage metrics**:
   - Legacy programs covered: X / Y (percentage)
   - ATX BRE business functions covered: X / Y (percentage)
   - Code paths covered: X / Y (percentage)
   - Error scenarios covered: X / Y (percentage)
   - Edge cases covered: X / Y (percentage)

2. **Identify coverage gaps**:
   - Uncovered legacy programs
   - Uncovered business functions
   - Uncovered code paths
   - Missing error scenarios
   - Missing edge cases

3. **Document coverage rationale**:
   - Why certain code is not covered
   - Risk assessment for gaps
   - Recommendations for additional testing

### 8. Progress Tracking Update

Update progress tracking: `{{ATX_TEST_GENERATION_STATUS}}`

**Structure**:
```json
{
  "document_type": "ATX Test Generation Progress Tracking",
  "last_updated": "2026-03-04T10:00:00+01:00",
  "phase": "Phase 4-ATX - ATX-Based Functional Equivalence Test Generation",
  "domains": {
    "CreditCardAccountManagement": {
      "domain_name": "CreditCardAccountManagement",
      "status": "In Progress",
      "entrypoints": {
        "COACTUPC": {
          "entrypoint_name": "COACTUPC",
          "document_title": "CAUP Transaction Documentation",
          "status": "Draft Created",
          "completed_date": "2026-03-04",
          "test_cases": {
            "total": 15,
            "main_flow": 3,
            "error_handling": 5,
            "boundary": 4,
            "transformation": 2,
            "integration": 1
          },
          "legacy_coverage": {
            "programs_total": 2,
            "programs_covered": 2,
            "coverage_percentage": "100%",
            "programs": [
              {
                "name": "COACTUPC.cbl",
                "test_cases": ["TC-001", "TC-002", "TC-003"],
                "coverage": "100%"
              }
            ]
          },
          "business_function_coverage": {
            "functions_total": 12,
            "functions_covered": 12,
            "coverage_percentage": "100%"
          },
          "test_data": {
            "test_data_sets": 15,
            "input_scenarios": 15,
            "expected_outputs": 15,
            "status": "Complete"
          },
          "deliverables": {
            "test_specification_draft": {
              "path": "output/specifications/test_cases/atx/specs/CreditCardAccountManagement-COACTUPC-atx-tests-draft.md",
              "status": "Created",
              "test_cases_count": 15
            },
            "test_data": {
              "path": "output/specifications/test_cases/atx/test_data/CreditCardAccountManagement-COACTUPC-test-data.json",
              "status": "Created",
              "data_sets_count": 15
            },
            "traceability_matrix": {
              "path": "output/specifications/test_cases/atx/traceability/CreditCardAccountManagement-COACTUPC-legacy-traceability.md",
              "status": "Created"
            },
            "coverage_report": {
              "path": "output/specifications/test_cases/atx/traceability/CreditCardAccountManagement-COACTUPC-coverage-notes.md",
              "status": "Created"
            }
          },
          "quality_checks": {
            "legacy_code_coverage_complete": true,
            "business_function_coverage_complete": true,
            "test_data_sets_complete": true,
            "comparative_scenarios_defined": true,
            "traceability_to_legacy_complete": true,
            "equivalence_validation_points_defined": true
          },
          "ready_for_review": true
        }
      }
    }
  },
  "summary": {
    "total_domains": 9,
    "completed_domains": 0,
    "in_progress_domains": 1,
    "pending_domains": 8,
    "total_entrypoints": 50,
    "completed_entrypoints": 1,
    "in_progress_entrypoints": 0,
    "pending_entrypoints": 49,
    "overall_progress": "2%"
  }
}
```

---

## Quality Criteria

### Legacy Code Coverage Quality
- All legacy programs in workpackage scope have test coverage
- All main code paths are tested
- Error handling paths are tested
- Edge cases and boundary conditions are tested
- Coverage gaps are documented with rationale

### Test Data Quality
- Test data is realistic and matches legacy data patterns
- Input data covers all scenarios (main, error, boundary, edge)
- Expected outputs are extracted from legacy code analysis
- Test data includes sufficient variation
- Special values (nulls, zeros, spaces) are included

### Equivalence Validation Quality
- Validation points are explicit and measurable
- Comparison criteria are clearly defined
- Tolerances are specified where applicable
- Field-by-field comparison is documented
- Behavioral equivalence is defined

### Traceability Quality
- Every test case links to specific legacy code
- Legacy programs are mapped to test cases
- ATX analysis references are included
- Code sections are identified (line numbers)
- Dependencies are documented

### Test Specification Quality
- Test cases are clear and unambiguous
- Test steps are detailed and actionable
- Preconditions are clearly stated
- Expected results are specific and verifiable
- Comparative testing approach is explicit

---

## Error Handling

### Common Error Scenarios

1. **ATX BRE Analysis Incomplete or Ambiguous**
   - Detection: Missing business functions or unclear functionality flow
   - Recovery: Rely more heavily on legacy source code analysis
   - Escalation: Flag for human review if critical behavior is unclear

2. **Legacy Code Too Complex**
   - Detection: Complex logic that's difficult to test comprehensively
   - Recovery: Break into smaller test scenarios, focus on critical paths
   - Escalation: Request human expert review for complex algorithms

3. **Missing Test Data**
   - Detection: No sample data available in legacy system
   - Recovery: Generate synthetic data based on data structure definitions
   - Escalation: Request human input for realistic data values

4. **Unclear Equivalence Criteria**
   - Detection: Ambiguous output comparison requirements
   - Recovery: Default to exact match, document assumptions
   - Escalation: Request human clarification for critical comparisons

### Error Reporting Format
**File**: `{{ATX_TEST_GENERATION_ERRORS}}`
- Include: timestamp, error type, context, attempted resolution
- Update phase status to indicate issues

---

## End of Phase 4-ATX.0 Document
