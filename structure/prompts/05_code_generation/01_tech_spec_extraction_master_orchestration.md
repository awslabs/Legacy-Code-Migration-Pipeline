# Phase 5.0: Technical Implementation Guide Creation - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 5.1 - Technical Implementation Guide Creation
**Version**: 1.1
**Date**: 2026-03-04
**Owner**: tech_spec_team_supervisor

---

## CRITICAL - Delegation Check

**IF YOU ARE NOT THE OWNER OF THIS DOCUMENT, STOP AND DELEGATE**

This document is owned by: **tech_spec_team_supervisor**

**Before proceeding, check your role**:
- If you are **tech_spec_team_supervisor**: Continue with orchestration
- If you are **ANY OTHER AGENT**: 
  1. STOP immediately
  2. Delegate this entire prompt to **tech_spec_team_supervisor**
  3. Wait for their response
  4. Do NOT attempt to execute the orchestration yourself

**Why this matters**: Only the designated supervisor has the authority and context to orchestrate the entire phase across multiple agents. Attempting to execute orchestration from a non-supervisor role will result in incomplete or incorrect execution.

---

## Overview

This document provides orchestration instructions for the Technical Implementation Guide Creation phase, which creates workpackage-specific technical implementation guides that enable code generation agents to implement each workpackage.

**Purpose**: For each workpackage, create a technical implementation guide that:
- Extracts patterns from target specifications
- Defines implementation tasks for business functions
- Specifies data model and API design
- Documents integration points with other workpackages
- Provides clear guidance for code generation

**Sub-Phases**:
1. **Phase 5.1.0**: Technical Implementation Guide Creation (per workpackage)
2. **Phase 5.1.1**: Technical Implementation Guide Review (per workpackage)

---

## Phase Dependencies

```
Phase 4 (Test Case Generation) → Phase 5.0 (Database Modernization) → Phase 5.1 (Technical Specification Extraction)
                                                                              ↓
                                                                      Phase 5.1.0 (Tech Spec Creation)
                                                                              ↓
                                                                      Phase 5.1.1 (Tech Spec Review)
                                                                              ↓
                                                                      Phase 5.2 (Project Structure)
                                                                              ↓
                                                                      Phase 5.3/5.4/5.5 (Code Generation)
```

**Prerequisites**:
- Phase 3 outputs: Business specifications (approved)
- Phase 4 outputs: Test case specifications (approved)
- Phase 5.0 outputs: Modernized database schema (approved) - single target database
- Phase 2 outputs: Workpackage planning
- Input specifications: `{{TARGET_SPECIFICATION}}/`
- Sample code: `{{TARGET_SAMPLE_CODE}}/`
- Modernized database schema: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql` (DB_NAME auto-detected)

**Outputs**:
- Technical implementation guide per workpackage: `{{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md`
- Progress tracking: `{{TECH_SPEC_STATUS}}`
- Error logs: `{{TECH_SPEC_ERRORS}}`

---

## Orchestration Workflow

### For Each Workpackage (in priority order):

```
WORKPACKAGE_LOOP:
    SELECT next_workpackage FROM workpackage_planning ORDER BY priority

    # ========================================
    # PHASE 5.1.0: TECHNICAL IMPLEMENTATION GUIDE CREATION
    # ========================================
    
    EXECUTE Phase_5.1.0:
        ASSIGN: tech_spec_extraction_specialist
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1.0_tech_spec_creation.md
        PROVIDE_CONTEXT:
            - workpackage_id: current_workpackage.id
            - workpackage_name: current_workpackage.name
        
        INPUTS:
            - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification-approved.md
            - Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
            - Target specifications: {{TARGET_SPECIFICATION}}/
            - Modernized database schema: {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql (auto-detect DB_NAME)
            - Database migration mappings: {{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json
            - Sample code: {{TARGET_SAMPLE_CODE}}/
            - Workpackage planning: {{WORKPACKAGE_PLANNING}}
            - Previously created guides: {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide-approved.md
        
        EXPECTED_OUTPUTS:
            - Technical implementation guide (draft): {{TECH_SPEC_BASE_PATH}}/review/WP-{ID}-tech-implementation-guide-draft.md
            - Progress tracking: {{TECH_SPEC_STATUS}}
            - Error reports (if any): {{TECH_SPEC_ERRORS}}
        
        VERIFICATION:
            CHECK guide_exists(WP-{ID})
            CHECK all_sections_complete(WP-{ID})
            CHECK patterns_from_target_specs(WP-{ID})
            CHECK business_functions_covered(WP-{ID})
            CHECK integration_points_documented(WP-{ID})
            
            IF verification_failed:
                LOG error to {{TECH_SPEC_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{TECH_SPEC_STATUS}} with completion
                PROCEED to Phase_5.1.1

    # ========================================
    # PHASE 5.1.1: TECHNICAL IMPLEMENTATION GUIDE REVIEW
    # ========================================
    
    EXECUTE Phase_5.1.1:
        ASSIGN: tech_spec_review_specialist
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1.1_tech_spec_review.md
        PROVIDE_CONTEXT:
            - workpackage_id: current_workpackage.id
            - workpackage_name: current_workpackage.name
        
        INPUTS:
            - Technical implementation guide (draft): {{TECH_SPEC_BASE_PATH}}/review/WP-{ID}-tech-implementation-guide-draft.md
            - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification-approved.md
            - Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
            - Target specifications: {{TARGET_SPECIFICATION}}/
            - Previously approved guides: {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide-approved.md
        
        EXPECTED_OUTPUTS:
            - Approved guide: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md
            - Review report: {{TECH_SPEC_BASE_PATH}}/review/WP-{ID}-review-report.md
            - Progress tracking: {{TECH_SPEC_STATUS}}
        
        VERIFICATION:
            CHECK review_report_exists(WP-{ID})
            CHECK approval_decision_documented(WP-{ID})
            
            IF decision == "APPROVED":
                CHECK approved_guide_exists(WP-{ID})
                UPDATE {{TECH_SPEC_STATUS}} with approval
                PROCEED to WORKPACKAGE_COMPLETE
            
            ELSE IF decision == "REVISE":
                CHECK revision_feedback_documented(WP-{ID})
                UPDATE {{TECH_SPEC_STATUS}} with revision request
                RETURN to Phase_5.1.0 with feedback
            
            ELSE IF decision == "REJECT":
                CHECK rejection_rationale_documented(WP-{ID})
                UPDATE {{TECH_SPEC_STATUS}} with rejection
                ESCALATE to human supervisor
                HALT workpackage processing

    # ========================================
    # WORKPACKAGE COMPLETION
    # ========================================
    
    WORKPACKAGE_COMPLETE:
        LOG "Technical implementation guide for WP-{ID} completed successfully"
        UPDATE {{TECH_SPEC_STATUS}} with workpackage completion
        PROCEED to next workpackage in WORKPACKAGE_LOOP

END WORKPACKAGE_LOOP
```

---

## Agent Assignments

### Phase 5.1.0: Technical Implementation Guide Creation
**Agent**: tech_spec_extraction_specialist
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1.0_tech_spec_creation.md
**Capabilities**:
- Pattern extraction from target specifications
- Business requirement analysis
- Implementation task definition
- Data model and API design
- Integration point documentation
- Technical decision documentation

### Phase 5.1.1: Technical Implementation Guide Review
**Agent**: tech_spec_review_specialist
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1.1_tech_spec_review.md
**Capabilities**:
- Completeness verification
- Consistency checking (with target specs and other workpackages)
- Clarity assessment
- Traceability validation
- Integration point validation
- Quality assurance

---

## Input/Output Contracts

### Phase 3/4/5.0 → Phase 5.1.0
**Phase 3/4/5.0 Outputs** (Phase 5.1.0 Inputs):
- Business specifications: `WP-{ID}-specification-approved.md`
- Test cases: `WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md`
- Modernized database schemas: `new_sqlite_ddl.sql`, `new_postgres_ddl.sql`
- Database migration mappings: `field_mapping.json`
- Workpackage planning with dependencies
- Target specifications (provided by customer)

**Contract**:
- All business functions documented
- All test cases defined
- Modernized database schemas available
- Database migration mappings available
- Workpackage dependencies identified
- Target specifications available

### Phase 5.1.0 → Phase 5.1.1
**Phase 5.1.0 Outputs** (Phase 5.1.1 Inputs):
- Technical implementation guide (draft): `WP-{ID}-tech-implementation-guide.md`
- Progress tracking updated

**Contract**:
- Guide follows 9-section structure
- Patterns extracted from target specifications
- All business functions have implementation tasks
- Integration points documented
- Technical decisions documented with rationale

### Phase 5.1.1 → Phase 5.2
**Phase 5.1.1 Outputs** (Phase 5.2 Inputs):
- Approved technical implementation guide: `WP-{ID}-tech-implementation-guide-approved.md`
- Review report
- Progress tracking updated

**Contract**:
- Guide approved for code generation
- Patterns consistent with target specifications
- Consistent with other approved workpackage guides
- All business requirements covered
- Integration points validated
- Ready for code generation

---

## Verification Criteria

### Phase 5.1.0 Verification
```
CHECK guide_exists(workpackage_id):
    guide_path = {{TECH_SPEC_BASE_PATH}}/WP-{workpackage_id}-tech-implementation-guide.md
    RETURN file_exists(guide_path)

CHECK all_sections_complete(workpackage_id):
    guide = load_guide(workpackage_id)
    required_sections = [
        "Workpackage Overview",
        "Architecture and Structure",
        "Implementation Tasks",
        "Data Model Implementation",
        "API Design",
        "Integration Points",
        "Testing Guidance",
        "Technical Decisions",
        "Implementation Checklist"
    ]
    FOR EACH section IN required_sections:
        IF NOT guide.has_section(section) OR guide.section_is_empty(section):
            LOG "Missing or empty section: {section}"
            RETURN FALSE
    RETURN TRUE

CHECK patterns_from_target_specs(workpackage_id):
    guide = load_guide(workpackage_id)
    # Verify patterns reference target specifications
    IF NOT guide.has_target_spec_references():
        LOG "Missing target specification references"
        RETURN FALSE
    RETURN TRUE

CHECK business_functions_covered(workpackage_id):
    business_spec = load_business_specification(workpackage_id)
    guide = load_guide(workpackage_id)
    
    functions = business_spec.get_business_functions()
    FOR EACH function IN functions:
        IF NOT guide.has_implementation_task_for(function.id):
            LOG "Business function {function.id} not covered in implementation tasks"
            RETURN FALSE
    RETURN TRUE

CHECK integration_points_documented(workpackage_id):
    guide = load_guide(workpackage_id)
    workpackage = load_workpackage_metadata(workpackage_id)
    
    dependencies = workpackage.get_dependencies()
    FOR EACH dependency IN dependencies:
        IF NOT guide.documents_integration_with(dependency):
            LOG "Integration with {dependency} not documented"
            RETURN FALSE
    RETURN TRUE
```

### Phase 5.1.1 Verification
```
CHECK review_report_exists(workpackage_id):
    report_path = {{TECH_SPEC_BASE_PATH}}/WP-{workpackage_id}-review-report.md
    RETURN file_exists(report_path)

CHECK approval_decision_documented(workpackage_id):
    report = load_review_report(workpackage_id)
    RETURN report.has_field("decision") AND 
           report.decision IN ["APPROVED", "REVISE", "REJECT"]

CHECK approved_guide_exists(workpackage_id):
    approved_path = {{TECH_SPEC_BASE_PATH}}/WP-{workpackage_id}-tech-implementation-guide-approved.md
    RETURN file_exists(approved_path)
```

---

## Error Handling and Rework

### Rework Scenarios

#### Scenario 1: Incomplete Guide (Return to Phase 5.1.0)
**Triggers**:
- Missing required sections
- Insufficient implementation detail
- Missing business function coverage
- Incomplete integration point documentation

**Actions**:
1. Document gaps in review report
2. Update Phase 5.1.0 task with specific sections to complete
3. Re-assign tech_spec_extraction_specialist
4. Re-execute Phase 5.1.0 with focus on identified gaps
5. Re-verify completeness

#### Scenario 2: Inconsistencies Found (Return to Phase 5.1.0)
**Triggers**:
- Patterns don't match target specifications
- Inconsistent with other approved workpackage guides
- Conflicting integration approaches
- Naming convention mismatches

**Actions**:
1. Document inconsistencies in review report
2. Re-assign tech_spec_extraction_specialist
3. Re-execute Phase 5.1.0 to resolve inconsistencies
4. Re-verify consistency

#### Scenario 3: Missing Traceability (Return to Phase 5.1.0)
**Triggers**:
- Technical decisions without rationale
- Patterns without target spec references
- Implementation tasks not linked to business functions

**Actions**:
1. Document traceability gaps in review report
2. Re-assign tech_spec_extraction_specialist
3. Re-execute Phase 5.1.0 to add traceability
4. Re-verify traceability

#### Scenario 4: Critical Issues (Escalate to Human)
**Triggers**:
- Target specifications missing or incomplete
- Business specification ambiguities preventing implementation design
- Irreconcilable conflicts between workpackages
- Technical decisions requiring architectural input

**Actions**:
1. Document critical issues in error log
2. Escalate to human supervisor with detailed explanation
3. Halt workpackage processing
4. Await human guidance before proceeding

---

## Progress Tracking

### Status Tracking

**JSON File**: `{{TECH_SPEC_STATUS}}`
**Markdown File**: `{{TECH_SPEC_PROGRESS}}`

**Templates**:
- JSON: `{{TECH_SPEC_STATUS_TEMPLATE}}`
- Markdown: `{{TECH_SPEC_PROGRESS_TEMPLATE}}`

**Update Frequency**: After each specification completion and after review

### Resumption Logic

When resuming after interruption:
1. Read {{TECH_SPEC_STATUS}}
2. Check which specifications are completed
3. Check which specifications are in review
4. Resume from first incomplete specification or review step

---

## Quality Gates

### Phase 5.1.0 Quality Gate
**Criteria**:
- [ ] All four specifications created
- [ ] All required sections populated
- [ ] Source references documented
- [ ] Assumptions documented
- [ ] Code examples included
- [ ] No critical errors
- [ ] Progress tracking updated

**Gate Decision**:
- **PASS**: Proceed to Phase 5.1.1
- **FAIL**: Rework Phase 5.1.0 or escalate

### Phase 5.1.1 Quality Gate
**Criteria**:
- [ ] All specifications reviewed
- [ ] Completeness verified
- [ ] Consistency verified
- [ ] Clarity verified
- [ ] Traceability verified
- [ ] All specifications approved
- [ ] No blocking issues

**Gate Decision**:
- **PASS**: Proceed to Phase 5.2 (Project Structure)
- **FAIL**: Rework Phase 5.1.0 or escalate

---

## Configuration and Path Variables

### Input Paths
```
Business Specification Base Path = {{BUSINESS_SPECIFICATION_BASE_PATH}}
Test Case Generation Base Path = {{TEST_CASE_GENERATION_BASE_PATH}}
Target Specification = {{TARGET_SPECIFICATION}}
Target Sample Code = {{TARGET_SAMPLE_CODE}}
Modernized Database Schemas = {{DATABASE_MODERNIZATION_OUTPUT}}
Workpackage Planning = {{WORKPACKAGE_PLANNING}}
```

### Output Paths
```
Tech Spec Base Path = {{TECH_SPEC_BASE_PATH}}
Tech Spec Status = {{TECH_SPEC_STATUS}}
Tech Spec Errors = {{TECH_SPEC_ERRORS}}
```

### Template Paths
```
Tech Implementation Guide Template = {{TECH_IMPLEMENTATION_GUIDE_TEMPLATE}}
Tech Spec Status Template = {{TECH_SPEC_STATUS_TEMPLATE}}
Tech Spec Errors Template = {{TECH_SPEC_ERRORS_TEMPLATE}}
```

---

## Supervisor Responsibilities

### Pre-Execution
1. Verify all prerequisites exist
2. Verify all path variables are resolved
3. Verify all template files exist
4. Verify agents are available
5. Verify source specifications exist
6. Create output directories if needed
7. Initialize progress tracking

### During Execution
1. Assign appropriate agent for each sub-phase
2. Provide task document from {{PROMPTS_BASE_PATH}}
3. Monitor execution progress
4. Verify completion against quality gates
5. Handle errors and rework scenarios
6. Update progress tracking
7. Escalate critical issues

### Post-Execution
1. Verify all specifications approved
2. Verify all quality gates passed
3. Generate final summary
4. Archive artifacts
5. Prepare handoff to Phase 5.2

---

## Success Criteria

Phase 5.1 is considered complete when:
- [ ] All workpackages have technical implementation guides
- [ ] All guides reviewed and approved
- [ ] All guides follow patterns from target specifications
- [ ] All guides consistent with each other
- [ ] All business functions covered in implementation tasks
- [ ] All integration points documented
- [ ] Database schema references included
- [ ] No blocking issues remain
- [ ] Progress tracking shows 100% completion
- [ ] Ready for Phase 5.2 (Code Generation)

---

## Notes for Supervisor

**Critical Success Factors**:
1. **Pattern Extraction**: All patterns must come from target specifications, not assumptions
2. **Consistency**: Guides must be consistent across workpackages for integration
3. **Completeness**: All business functions must have implementation tasks
4. **Traceability**: All decisions must be traceable to requirements and specifications
5. **Integration**: Integration points must be carefully documented

**Common Pitfalls to Avoid**:
1. Hardcoding patterns instead of extracting from target specifications
2. Inconsistent naming conventions across workpackages
3. Missing integration point documentation
4. Insufficient detail for code generation
5. Technical decisions without rationale

**When to Escalate**:
1. Target specifications are missing or severely incomplete
2. Business specification ambiguities preventing implementation design
3. Irreconcilable conflicts between workpackages
4. Technical decisions requiring architectural expertise
5. Repeated rework cycles (more than 2 iterations per workpackage)

---

## End of Master Orchestration Document
