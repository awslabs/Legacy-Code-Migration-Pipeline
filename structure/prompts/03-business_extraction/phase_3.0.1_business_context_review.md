# Phase 3.0.1: Business Context Review

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.0.1 - Business Context Review
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_reviewer_requirements
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.0.1_business_context_review.md

### Expected Deliverables

1. **Business Context Review Report**
   - File: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-review.md
   - Description: Review findings and approval decision for business context

2. **Approved Business Context Document** (if changes needed)
   - File: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md
   - Description: Validated and approved business context document

3. **Progress Tracking**
   - File: {{BUSINESS_CONTEXT_STATUS}}
   - Description: Updated progress tracking with review completion status

### Success Criteria
- [ ] Business domain identification accuracy verified
- [ ] Stakeholder completeness verified
- [ ] Business vocabulary consistency verified
- [ ] Business problem statement clarity confirmed
- [ ] Confidence levels assessed and acceptable
- [ ] Approval decision documented
- [ ] Ready for Phase 3.1 (Business Logic Extraction)

---

## Context

### Input Locations
- **Business context documents**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md`
- **Business glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- **Source code files**: `{{SOURCE_CODE}}` (for verification if needed)
- **Workpackage definitions**: `{{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/`

### Output Locations
- **Review reports**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-review.md`
- **Approved context**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md`
- **Progress tracking**: `{{BUSINESS_CONTEXT_STATUS}}``

### Previous Phase Artifacts
- **From Phase 3.0**: Business context documents, business glossary

---

## Objective

Validate business context accuracy before proceeding to logic extraction. Ensure business domain identification is correct, stakeholders are complete, business vocabulary is consistent, and confidence levels are acceptable. Approve context for Phase 3.1 or return for revision.

---

## Instructions

### 1. Business Domain Verification
- Verify business domain identification accuracy
- Check evidence sources and confidence levels
- Validate sub-domain and business capability alignment
- Confirm domain assignment is appropriate

### 2. Stakeholder Completeness Check
- Verify all relevant stakeholders identified
- Check stakeholder roles and descriptions
- Validate evidence sources
- Flag missing stakeholders

### 3. Business Vocabulary Consistency
- Review business terms and definitions
- Check for conflicts or ambiguities
- Verify glossary completeness
- Validate technical mappings

### 4. Business Problem Statement Clarity
- Verify problem statement is clear and business-focused
- Check business value articulation
- Validate business context and rationale
- Confirm readability for business analysts

### 5. Confidence Assessment
- Review confidence levels for each section
- Validate confidence rationale
- Identify areas requiring clarification
- Flag low-confidence areas for attention

### 6. Approval Decision
- **Approved**: Ready for Phase 3.1
- **Approved with Changes**: Minor fixes applied, ready for Phase 3.1
- **Rejected**: Return to Phase 3.0 with specific corrections

---

## Output Format

### Business Context Review Report
**File**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-review.md`

**Structure**:
```markdown
# Business Context Review Report: WP-XXX

## Review Summary
- **Reviewer**: [Name/Role]
- **Review Date**: YYYY-MM-DD
- **Decision**: Approved / Approved with Changes / Rejected

## Domain Verification
- **Status**: [Verified / Issues Found]
- **Findings**: [List findings]
- **Changes**: [List changes if any]

## Stakeholder Completeness
- **Status**: [Complete / Issues Found]
- **Findings**: [List findings]
- **Changes**: [List changes if any]

## Vocabulary Consistency
- **Status**: [Consistent / Issues Found]
- **Findings**: [List findings]
- **Changes**: [List changes if any]

## Problem Statement Clarity
- **Status**: [Clear / Issues Found]
- **Findings**: [List findings]
- **Changes**: [List changes if any]

## Confidence Assessment
- **Overall Confidence**: [High / Medium / Low]
- **Areas of Concern**: [List areas]
- **Recommendations**: [List recommendations]

## Approval Decision
- **Decision**: [Approved / Approved with Changes / Rejected]
- **Rationale**: [Explanation]
- **Next Steps**: [What happens next]
```

---

## End of Phase 3.0.1 Document
