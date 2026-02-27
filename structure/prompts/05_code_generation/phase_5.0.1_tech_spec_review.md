# Phase 5.0.1: Technical Implementation Guide Review

---

## Orchestration Information

**Phase**: Phase 5.0.1 - Technical Specification Review  
**Team Supervisor**: tech_spec_team_supervisor  
**Assigned Agent**: tech_spec_review_specialist  
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.0.1_tech_spec_review.md

---

## Expected Deliverables

1. **Review Report (per workpackage)**
   - File: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-review-report.md
   - Description: Detailed review feedback for the workpackage technical implementation guide

2. **Approved Technical Implementation Guide (per workpackage)**
   - File: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md
   - Description: Approved guide ready for code generation (if approved)

3. **Progress Tracking**
   - File: {{TECH_SPEC_STATUS}}
   - Description: Updated with review status for all workpackages

4. **Error Log**
   - File: {{TECH_SPEC_ERRORS}}
   - Description: Document any blocking issues

---

## Context

### Input Locations
- Technical implementation guides (draft): {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide.md
- Business specifications: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification-approved.md
- Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
- Target specifications: {{TARGET_SPECIFICATION}}/
- Database schemas: {{DATABASE_GEN_SRC}}/ (check for `new_sqlite_ddl.sql`)
- Workpackage planning: {{WORKPACKAGE_PLANNING}}
- Previously approved guides: {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide-approved.md

### Output Locations
- Review reports: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-review-report.md
- Approved guides: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md
- Progress tracking: {{TECH_SPEC_STATUS}}
- Error logs: {{TECH_SPEC_ERRORS}}

---

## Objective

Review technical implementation guides for each workpackage to ensure they:
1. Follow patterns extracted from target specifications
2. Are consistent with previously approved workpackage guides
3. Cover all business requirements from the business specification
4. Provide sufficient detail for code generation
5. Properly document integration points with other workpackages
6. Include clear traceability to requirements and specifications

**Review Principles**:
- **Completeness**: All required sections present with sufficient detail
- **Consistency**: Patterns match target specs and other workpackage guides
- **Clarity**: Clear, unambiguous, implementation-ready
- **Traceability**: All decisions traceable to requirements and specifications
- **Integration**: Integration points properly documented

---

## Instructions

### Step 1: Load Review Context

1. Read progress tracking from {{TECH_SPEC_STATUS}}
2. Identify workpackages with status "draft_complete"
3. Load workpackage list from {{WORKPACKAGE_PLANNING}}
4. Prioritize workpackages by dependency order (review dependencies first)

### Step 2: For Each Workpackage (in priority order)

#### 2.1 Load Workpackage Context

Read the following for the current workpackage:
- Technical implementation guide (draft): {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide.md
- Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification-approved.md
- Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
- Workpackage metadata from {{WORKPACKAGE_PLANNING}}

#### 2.2 Review Section 1: Workpackage Overview

**Completeness Check**:
- [ ] Workpackage ID and name present
- [ ] Business context summary present
- [ ] Dependencies on other workpackages listed
- [ ] Tier(s) involved clearly stated

**Accuracy Check**:
- [ ] Business context matches business specification
- [ ] Dependencies match workpackage planning
- [ ] Tiers match business specification requirements

**Issues to Document**:
- Missing or incomplete overview information
- Inaccurate business context
- Missing or incorrect dependencies

#### 2.3 Review Section 2: Architecture and Structure

**Completeness Check**:
- [ ] Architecture patterns documented
- [ ] Package/directory structure specified
- [ ] Component organization defined
- [ ] Layer responsibilities described

**Consistency Check**:
- [ ] Architecture patterns match target specifications
- [ ] Structure consistent with previously approved workpackages
- [ ] Naming conventions consistent across workpackages
- [ ] Layer organization follows target spec patterns

**Traceability Check**:
- [ ] Architecture patterns reference target specification sections
- [ ] Structure decisions justified with source references

**Issues to Document**:
- Patterns not matching target specifications
- Inconsistencies with other workpackages
- Missing source references
- Unclear structure definitions

#### 2.4 Review Section 3: Implementation Tasks

**Completeness Check**:

For EACH business function in the business specification:
- [ ] Implementation task defined
- [ ] Required components/classes/modules listed
- [ ] API endpoints specified (if applicable)
- [ ] Data access requirements documented
- [ ] Business rule implementations specified
- [ ] Validation requirements documented
- [ ] Error handling approach defined

**Coverage Check**:
- [ ] All business functions from business spec covered
- [ ] All business rules from business spec addressed
- [ ] All process flows from business spec mapped to tasks

**Clarity Check**:
- [ ] Tasks are clearly described
- [ ] Component names are specific (not generic)
- [ ] Implementation approach is unambiguous
- [ ] Sufficient detail for code generation

**Issues to Document**:
- Missing implementation tasks for business functions
- Vague or ambiguous task descriptions
- Insufficient detail for implementation
- Missing business rule implementations

#### 2.5 Review Section 4: Data Model Implementation

**Completeness Check**:
- [ ] All business entities have entity/model definitions
- [ ] Database table mappings specified
- [ ] Relationships and constraints documented
- [ ] Data access patterns specified

**Accuracy Check**:
- [ ] Entity definitions match business specification entities
- [ ] Table mappings match database schemas
- [ ] Relationships match business entity relationships
- [ ] Data access patterns match target specification

**Consistency Check**:
- [ ] Entity naming consistent with other workpackages
- [ ] Data access patterns consistent across workpackages
- [ ] Database conventions consistent

**Issues to Document**:
- Missing entity definitions
- Mismatches with business specification or database schemas
- Inconsistent naming or patterns
- Missing relationships or constraints

#### 2.6 Review Section 5: API Design (if applicable)

**Completeness Check**:
- [ ] All required endpoints defined
- [ ] Request/response structures specified
- [ ] HTTP methods and status codes documented
- [ ] Authentication/authorization requirements specified

**Accuracy Check**:
- [ ] Endpoints match business functions
- [ ] Request/response structures match business entities
- [ ] HTTP methods appropriate for operations
- [ ] Status codes follow target specification patterns

**Consistency Check**:
- [ ] API patterns match target specification
- [ ] Endpoint naming consistent with other workpackages
- [ ] Response formats consistent across workpackages

**Issues to Document**:
- Missing endpoint definitions
- Inconsistent API patterns
- Inappropriate HTTP methods or status codes
- Missing authentication/authorization requirements

#### 2.7 Review Section 6: Integration Points

**Completeness Check**:
- [ ] Dependencies on other workpackages documented
- [ ] Shared components identified
- [ ] External system integrations specified
- [ ] Database dependencies documented

**Accuracy Check**:
- [ ] Dependencies match workpackage planning
- [ ] Shared components exist in referenced workpackages
- [ ] Integration approaches are feasible

**Consistency Check**:
- [ ] Integration patterns consistent with other workpackages
- [ ] Shared component usage consistent

**Issues to Document**:
- Missing integration points
- Incorrect dependencies
- Inconsistent integration patterns
- References to non-existent components

#### 2.8 Review Section 7: Testing Guidance

**Completeness Check**:
- [ ] Test case references present
- [ ] Testing approach per layer/component specified
- [ ] Integration testing requirements documented

**Accuracy Check**:
- [ ] Test case references match test case specification
- [ ] Testing approaches appropriate for components
- [ ] Integration testing covers all integration points

**Issues to Document**:
- Missing testing guidance
- Incorrect test case references
- Insufficient testing coverage

#### 2.9 Review Section 8: Technical Decisions

**Completeness Check**:
- [ ] Key technical decisions documented
- [ ] Rationale provided for each decision
- [ ] Traceability to requirements established
- [ ] Alternative approaches considered (if applicable)

**Traceability Check**:
- [ ] Decisions traceable to business requirements
- [ ] Decisions traceable to target specifications
- [ ] Rationale references specific sources

**Issues to Document**:
- Missing technical decisions
- Decisions without rationale
- Missing traceability
- Unjustified deviations from patterns

#### 2.10 Review Section 9: Implementation Checklist

**Completeness Check**:
- [ ] Ordered list of implementation steps present
- [ ] Dependencies between steps documented
- [ ] Verification criteria specified

**Usability Check**:
- [ ] Steps are actionable and specific
- [ ] Order is logical and feasible
- [ ] Dependencies are clear
- [ ] Verification criteria are measurable

**Issues to Document**:
- Missing or incomplete checklist
- Vague or ambiguous steps
- Illogical ordering
- Missing verification criteria

#### 2.11 Cross-Workpackage Consistency Check

If other workpackages have been approved:
- [ ] Architecture patterns consistent
- [ ] Naming conventions consistent
- [ ] Data access patterns consistent
- [ ] API patterns consistent
- [ ] Integration approaches consistent
- [ ] Shared components properly referenced

**Issues to Document**:
- Inconsistencies with approved workpackages
- Conflicting patterns or approaches
- Incompatible integration points

#### 2.12 Generate Review Report

Create review report at {{TECH_SPEC_BASE_PATH}}/WP-{ID}-review-report.md:

```markdown
# Technical Implementation Guide Review Report

**Workpackage**: WP-{ID} - {Name}
**Review Date**: {Date}
**Reviewer**: tech_spec_review_specialist
**Review Status**: [APPROVED / REVISE / REJECT]

---

## Overall Assessment

**Summary**: [Brief assessment of the guide quality]

**Strengths**:
- [Strength 1]
- [Strength 2]

**Areas for Improvement**:
- [Area 1]
- [Area 2]

---

## Section-by-Section Review

### Section 1: Workpackage Overview
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 2: Architecture and Structure
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 3: Implementation Tasks
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 4: Data Model Implementation
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 5: API Design
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 6: Integration Points
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 7: Testing Guidance
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 8: Technical Decisions
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

### Section 9: Implementation Checklist
**Status**: [PASS / FAIL]
**Issues**:
- [Issue 1]
- [Issue 2]

---

## Quality Assessment

### Completeness: [PASS / FAIL]
- All required sections present: [YES / NO]
- All business functions covered: [YES / NO]
- All integration points documented: [YES / NO]

### Consistency: [PASS / FAIL]
- Patterns match target specifications: [YES / NO]
- Consistent with other workpackages: [YES / NO]
- Naming conventions consistent: [YES / NO]

### Clarity: [PASS / FAIL]
- Implementation tasks clear: [YES / NO]
- Technical decisions explained: [YES / NO]
- Sufficient detail for code generation: [YES / NO]

### Traceability: [PASS / FAIL]
- Business requirements traced: [YES / NO]
- Target spec patterns traced: [YES / NO]
- Technical decisions justified: [YES / NO]

### Integration: [PASS / FAIL]
- Dependencies properly documented: [YES / NO]
- Shared components identified: [YES / NO]
- Integration approaches feasible: [YES / NO]

---

## Required Corrections

### Critical (Must Fix Before Approval)
1. [Critical issue 1]
2. [Critical issue 2]

### Important (Should Fix)
1. [Important issue 1]
2. [Important issue 2]

### Minor (Nice to Have)
1. [Minor issue 1]
2. [Minor issue 2]

---

## Approval Decision

**Decision**: [APPROVED / REVISE / REJECT]

**Rationale**: [Explanation of decision]

**Next Steps**:
- [Step 1]
- [Step 2]

---

**End of Review Report**
```

#### 2.13 Make Approval Decision

**If ALL quality criteria met**:
1. Copy draft to approved file: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md
2. Set review status to "APPROVED" in review report
3. Update {{TECH_SPEC_STATUS}} with approval
4. Proceed to next workpackage

**If corrections needed**:
1. Set review status to "REVISE" in review report
2. Document all required corrections
3. Update {{TECH_SPEC_STATUS}} with "corrections_needed"
4. Return to Phase 5.0.0 for this workpackage
5. Do NOT approve until corrections made

**If critical issues found**:
1. Set review status to "REJECT" in review report
2. Document all critical issues
3. Update {{TECH_SPEC_STATUS}} with "rejected"
4. Log error in {{TECH_SPEC_ERRORS}}
5. Escalate to human supervisor

### Step 3: Final Validation

After all workpackages reviewed:

1. Verify all workpackages have review reports
2. Verify all approved workpackages have approved guides
3. Check for any blocking issues across workpackages
4. Generate summary of review results

### Step 4: Update Progress Tracking

Update {{TECH_SPEC_STATUS}} with final status:
- Total workpackages reviewed
- Total approved
- Total requiring corrections
- Total rejected
- Overall phase status

---

## Quality Criteria

### Review Completeness
- [ ] All workpackages reviewed
- [ ] All sections assessed for each workpackage
- [ ] Cross-workpackage consistency checked
- [ ] Review reports complete for all workpackages

### Review Quality
- [ ] Issues clearly documented
- [ ] Severity appropriately assigned
- [ ] Actionable feedback provided
- [ ] Rationale for decisions clear
- [ ] Next steps identified

### Review Consistency
- [ ] Consistent criteria applied across workpackages
- [ ] Evidence-based assessments
- [ ] Fair and balanced reviews

---

## Success Criteria

- All workpackages have review reports
- All approved guides follow target specification patterns
- All approved guides are consistent with each other
- All approved guides cover business requirements completely
- All approved guides provide sufficient detail for code generation
- All integration points properly documented
- No critical issues remain unresolved
- Progress tracking shows accurate status
- Ready for Phase 5.1 (Code Generation)

---

## Error Handling

### Guide File Not Found
If technical implementation guide missing:
1. Document error in {{TECH_SPEC_ERRORS}}
2. Set workpackage status to "blocked"
3. Escalate to supervisor

### Severely Incomplete Guide
If guide has >50% missing sections:
1. Set review status to "REVISE"
2. List all missing sections in review report
3. Return to Phase 5.0.0

### Irreconcilable Inconsistencies
If inconsistencies cannot be resolved:
1. Set review status to "REJECT"
2. Document in review report and error log
3. Escalate to human supervisor

---

## Notes

- Review workpackages in dependency order (dependencies first)
- Consistency across workpackages is critical for integration
- Patterns must match target specifications, not assumptions
- Sufficient detail is required for code generation without additional discovery
- Integration points must be carefully validated to ensure workpackages work together

---

**End of Phase 5.0.1 Document**
