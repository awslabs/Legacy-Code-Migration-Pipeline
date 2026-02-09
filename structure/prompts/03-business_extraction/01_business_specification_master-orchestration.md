
# Phase 3: Business Specification - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 3 - Business Specification
**Version**: 1.1
**Date**: 2026-02-09
**Owner**: business_team_supervisor

---

## Overview

This document provides orchestration instructions for the Business Specification phase, which extracts business requirements from legacy code through a three-step process:

1. **Phase 3.0**: Business Context Discovery - Understand business domain and intent
2. **Phase 3.1**: Business Specification Extraction - Extract business entities, rules, and processes
3. **Phase 3.2**: Business Analyst Review - Validate and refine specifications

**Critical Principle**: Extract **reimagined business requirements** (technology-agnostic) rather than **translated code structures** (technology-specific).

---

## Phase Task Documents

The complete task documents for each phase are located in the prompts directory:
- **Phase 3.0**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.0.md
- **Phase 3.1**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.1.md
- **Phase 3.2**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.2.md

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
Phase 1 (Analysis) → Phase 2 (Workpackage Planning) → Phase 3 (Business Specification)
                                                            ↓
                                                    Phase 3.0 (Context Discovery)
                                                            ↓
                                                    Phase 3.1 (Specification Extraction)
                                                            ↓
                                                    Phase 3.2 (BA Review)
                                                            ↓
                                                    Phase 4 (Code Generation)
```

**Prerequisites**:
- Phase 1 outputs: Source code analysis, dependency analysis table, module classifications
- Phase 2 outputs: Workpackage definitions with prioritized flows

---

## Orchestration Workflow

### For Each Workpackage (in priority order):

```
WORKPACKAGE_LOOP:
    SELECT next_workpackage FROM workpackage_definitions ORDER BY priority

    # ========================================
    # PHASE 3.0: BUSINESS CONTEXT DISCOVERY
    # ========================================
    
    EXECUTE Phase_3.0:
        ASSIGN: business_context_analyst
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.0.md
        
        INPUTS:
            - Workpackage definition: {{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/WP-XXX-definition.md
            - Source code files: {{SOURCE_CODE}}
            - Database source code: {{DATABASE_SOURCE_CODE}}
            - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
            - Legacy documentation: {{PROJECT_BASE_PATH}}/input/legacy_documentation/
            - Business documentation: {{PROJECT_BASE_PATH}}/input/business_documentation/
            - Module dependency table: {{DEPENDENCY_ANALYSIS_TABLE}}
        
        EXPECTED_OUTPUTS:
            - Business context document: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md
            - Business glossary (consolidated): {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
            - Progress tracking: {{BUSINESS_CONTEXT_STATUS}}
            - Error reports (if any): {{BUSINESS_CONTEXT_ERRORS}}
        
        VERIFICATION:
            CHECK business_context_document_exists(WP-XXX)
            CHECK business_domain_identified(WP-XXX)
            CHECK business_stakeholders_documented(WP-XXX)
            CHECK business_vocabulary_extracted(WP-XXX)
            CHECK business_constraints_identified(WP-XXX)
            CHECK confidence_level_documented(WP-XXX)
            
            IF verification_failed:
                LOG error to {{BUSINESS_CONTEXT_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{BUSINESS_CONTEXT_STATUS}} with completion
                PROCEED to Phase_3.1

    # ========================================
    # PHASE 3.1: BUSINESS SPECIFICATION EXTRACTION
    # ========================================
    
    EXECUTE Phase_3.1:
        ASSIGN: business_specialist_logic_extraction
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.1.md
        
        INPUTS:
            - Business context document: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
            - Workpackage definition: {{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/WP-XXX-definition.md
            - Source code files: {{SOURCE_CODE}}
            - Database source code: {{DATABASE_SOURCE_CODE}}
            - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
            - Module dependency table: {{DEPENDENCY_ANALYSIS_TABLE}}
        
        EXPECTED_OUTPUTS:
            - Business specification (EN): {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md
            - Business specification (DN): {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-DN.md
            - Progress tracking: {{BUSINESS_SPECIFICATION_STATUS}}
            - Error reports (if any): {{BUSINESS_SPECIFICATION_ERRORS}}
        
        VERIFICATION:
            CHECK specification_exists(WP-XXX, language="EN")
            CHECK specification_exists(WP-XXX, language="DN")
            CHECK ieee_830_compliance(WP-XXX)
            CHECK business_entities_extracted(WP-XXX)
            CHECK business_rules_extracted(WP-XXX)
            CHECK business_functions_extracted(WP-XXX)
            CHECK process_flows_extracted(WP-XXX)
            CHECK legacy_implementation_documented(WP-XXX)
            CHECK technology_agnostic_chapters_1_5(WP-XXX)
            CHECK bilingual_consistency(WP-XXX)
            CHECK business_context_incorporated(WP-XXX)
            
            IF verification_failed:
                LOG error to {{BUSINESS_SPECIFICATION_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with completion
                PROCEED to Phase_3.2

    # ========================================
    # PHASE 3.2: BUSINESS ANALYST REVIEW
    # ========================================
    
    EXECUTE Phase_3.2:
        ASSIGN: business_analyst_reviewer
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.2.md
        
        INPUTS:
            - Business specification (EN): {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN.md
            - Business specification (DN): {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-DN.md
            - Business context document: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
            - Source code files: {{SOURCE_CODE}} (for verification)
            - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
        
        EXPECTED_OUTPUTS:
            - Reviewed specification (EN): {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN-reviewed.md
            - Reviewed specification (DN): {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-DN-reviewed.md
            - Review report: {{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md
            - Updated context (if needed): {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-updated.md
            - Updated glossary (if needed): {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary-updated.md
            - Progress tracking: {{BUSINESS_SPECIFICATION_STATUS}}
        
        VERIFICATION:
            CHECK review_report_exists(WP-XXX)
            CHECK approval_decision_documented(WP-XXX)
            
            approval_status = GET_APPROVAL_STATUS(WP-XXX)
            
            IF approval_status == "APPROVED":
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Approved"
                MARK workpackage as ready for Phase 4 (Code Generation)
                PROCEED to next workpackage
            
            ELSE IF approval_status == "APPROVED_WITH_CHANGES":
                CHECK reviewed_specifications_exist(WP-XXX)
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Approved with Changes"
                MARK workpackage as ready for Phase 4 (Code Generation)
                PROCEED to next workpackage
            
            ELSE IF approval_status == "REJECTED":
                issue_type = GET_ISSUE_TYPE(WP-XXX)
                
                IF issue_type == "BUSINESS_CONTEXT":
                    LOG "Business context issues identified, returning to Phase 3.0"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Returned to Phase 3.0"
                    RETURN_TO Phase_3.0
                
                ELSE IF issue_type == "EXTRACTION":
                    LOG "Extraction issues identified, returning to Phase 3.1"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Returned to Phase 3.1"
                    RETURN_TO Phase_3.1
                
                ELSE IF issue_type == "CRITICAL":
                    LOG "Critical issues identified, escalating to human supervisor"
                    ESCALATE to human supervisor
                    HALT workpackage processing
                
                ELSE:
                    LOG "Minor issues identified, fixing in Phase 3.2"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Fixing in Phase 3.2"
                    RETRY Phase_3.2

    # ========================================
    # WORKPACKAGE COMPLETION
    # ========================================
    
    WORKPACKAGE_COMPLETE:
        LOG "Workpackage WP-XXX completed successfully"
        UPDATE master progress tracking
        PROCEED to next workpackage

END WORKPACKAGE_LOOP
```

---

## Agent Assignments

### Phase 3.0: Business Context Discovery
**Agent**: business_context_analyst
**Agent Definition**: structure/agents/business_team/business_context_analyst.md
**Task Document**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.0.md
**Capabilities**:
- Business domain identification
- Stakeholder analysis
- Business vocabulary extraction
- Business constraint identification
- Business problem articulation

### Phase 3.1: Business Specification Extraction
**Agent**: business_specialist_logic_extraction
**Agent Definition**: structure/agents/business_team/business_specialist_logic_extraction.md
**Task Document**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.1.md
**Capabilities**:
- Code analysis and interpretation
- Business entity extraction
- Business rule extraction
- Business function identification
- Process flow documentation
- Legacy implementation traceability
- IEEE 830-1998 documentation

### Phase 3.2: Business Analyst Review
**Agent**: business_analyst_reviewer
**Agent Definition**: structure/agents/business_team/business_analyst_reviewer.md
**Task Document**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.2.md
**Capabilities**:
- Business policy validation
- Requirement completeness verification
- Technology-agnostic language verification
- Bilingual consistency verification
- Modernization readiness assessment
- Business rationale articulation

---

## Input/Output Contracts

### Phase 3.0 → Phase 3.1
**Phase 3.0 Outputs** (Phase 3.1 Inputs):
- Business context document: `WP-XXX-business-context.md`
- Business glossary: `business-glossary.md`

**Contract**:
- Business domain must be identified with confidence level
- Business stakeholders must be documented
- Business vocabulary must be extracted
- Business constraints must be identified
- Business outcomes must be documented

### Phase 3.1 → Phase 3.2
**Phase 3.1 Outputs** (Phase 3.2 Inputs):
- Business specification (EN): `WP-XXX-FLOW_XXX-specification-EN.md`
- Business specification (DN): `WP-XXX-FLOW_XXX-specification-DN.md`

**Contract**:
- IEEE 830-1998 format compliance
- 6 chapters complete (Introduction, Entities, Rules, Functions, Flows, Legacy Implementation)
- Business entities with BE-XXX identifiers
- Business rules with BR-XXX identifiers
- Business functions with F-XXX identifiers
- Technology-agnostic Chapters 1-5
- Complete legacy implementation in Chapter 6
- Bilingual consistency (EN and DN)

### Phase 3.2 → Phase 4
**Phase 3.2 Outputs** (Phase 4 Inputs):
- Reviewed specification (EN): `WP-XXX-FLOW_XXX-specification-EN-reviewed.md`
- Reviewed specification (DN): `WP-XXX-FLOW_XXX-specification-DN-reviewed.md`
- Review report: `business-extraction-WP-XXX-review.md`

**Contract**:
- Approval status: "Approved" or "Approved with Changes"
- Business requirements validated
- Missing requirements identified and added
- Accidental complexity removed
- Business rationale documented
- Ready for code generation

---

## Verification Criteria

### Phase 3.0 Verification
```
CHECK business_context_document_exists(workpackage_id):
    file_path = {{BUSINESS_CONTEXT_BASE_PATH}}/WP-{workpackage_id}-business-context.md
    RETURN file_exists(file_path)

CHECK business_domain_identified(workpackage_id):
    context_doc = load_document(workpackage_id)
    RETURN context_doc.section_1.business_domain IS NOT EMPTY
        AND context_doc.section_1.confidence_level IN ["High", "Medium", "Low"]

CHECK business_stakeholders_documented(workpackage_id):
    context_doc = load_document(workpackage_id)
    RETURN context_doc.section_2.primary_users IS NOT EMPTY
        OR context_doc.section_2.business_owners IS NOT EMPTY

CHECK business_vocabulary_extracted(workpackage_id):
    context_doc = load_document(workpackage_id)
    RETURN context_doc.section_4.business_entities.count >= 1
        OR context_doc.section_4.business_attributes.count >= 1

CHECK business_constraints_identified(workpackage_id):
    context_doc = load_document(workpackage_id)
    RETURN context_doc.section_5.business_rules IS NOT EMPTY
        OR context_doc.section_5.business_policies IS NOT EMPTY

CHECK confidence_level_documented(workpackage_id):
    context_doc = load_document(workpackage_id)
    RETURN context_doc.document_control.confidence_level IS NOT EMPTY
```

### Phase 3.1 Verification
```
CHECK specification_exists(workpackage_id, language):
    file_path = {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{workpackage_id}-FLOW_XXX-specification-{language}.md
    RETURN file_exists(file_path)

CHECK ieee_830_compliance(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    RETURN spec_doc.has_chapter(1, "Introduction")
        AND spec_doc.has_chapter(2, "Business Entities")
        AND spec_doc.has_chapter(3, "Business Rules")
        AND spec_doc.has_chapter(4, "Business Functions")
        AND spec_doc.has_chapter(5, "Process Flows")
        AND spec_doc.has_chapter(6, "Legacy Implementation References")

CHECK business_entities_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    RETURN spec_doc.chapter_2.entity_count >= 1
        AND all_entities_have_identifier(spec_doc.chapter_2, pattern="BE-{workpackage_id}-XXX")

CHECK business_rules_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    RETURN spec_doc.chapter_3.rule_count >= 1
        AND all_rules_have_identifier(spec_doc.chapter_3, pattern="BR-{workpackage_id}-XXX")

CHECK business_functions_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    RETURN spec_doc.chapter_4.function_count >= 1
        AND all_functions_have_identifier(spec_doc.chapter_4, pattern="F-{workpackage_id}-XXX")

CHECK process_flows_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    RETURN spec_doc.chapter_5.flow_count >= 1

CHECK legacy_implementation_documented(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    RETURN spec_doc.chapter_6.source_files IS NOT EMPTY
        AND spec_doc.chapter_6.business_rule_implementation IS NOT EMPTY
        AND spec_doc.chapter_6.function_implementation IS NOT EMPTY

CHECK technology_agnostic_chapters_1_5(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    technical_terms = ["COBOL", "CICS", "JCL", "DB2", "mainframe", "batch", "online", 
                       "transaction", "file", "record", "paragraph", "PERFORM", "MOVE", "CALL"]
    
    FOR chapter IN [1, 2, 3, 4, 5]:
        chapter_text = spec_doc.get_chapter_text(chapter)
        FOR term IN technical_terms:
            IF term IN chapter_text:
                LOG "Technical term '{term}' found in Chapter {chapter}"
                RETURN FALSE
    
    RETURN TRUE

CHECK bilingual_consistency(workpackage_id):
    spec_en = load_specification(workpackage_id, "EN")
    spec_dn = load_specification(workpackage_id, "DN")
    
    RETURN spec_en.chapter_2.entity_count == spec_dn.chapter_2.entity_count
        AND spec_en.chapter_3.rule_count == spec_dn.chapter_3.rule_count
        AND spec_en.chapter_4.function_count == spec_dn.chapter_4.function_count

CHECK business_context_incorporated(workpackage_id):
    spec_doc = load_specification(workpackage_id, "EN")
    context_doc = load_business_context(workpackage_id)
    
    RETURN spec_doc.chapter_1.business_domain == context_doc.section_1.business_domain
        AND spec_doc.chapter_1.business_stakeholders IS NOT EMPTY
```

### Phase 3.2 Verification
```
CHECK review_report_exists(workpackage_id):
    file_path = {{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-{workpackage_id}-review.md
    RETURN file_exists(file_path)

CHECK approval_decision_documented(workpackage_id):
    review_report = load_review_report(workpackage_id)
    RETURN review_report.section_8.decision IN ["Approved", "Approved with Changes", "Rejected"]

GET_APPROVAL_STATUS(workpackage_id):
    review_report = load_review_report(workpackage_id)
    RETURN review_report.section_8.decision

GET_ISSUE_TYPE(workpackage_id):
    review_report = load_review_report(workpackage_id)
    IF review_report.section_6.business_context_updates IS NOT EMPTY:
        RETURN "BUSINESS_CONTEXT"
    ELSE IF review_report.section_2.major_issues_count > 5:
        RETURN "EXTRACTION"
    ELSE IF review_report.section_8.severity == "Critical":
        RETURN "CRITICAL"
    ELSE:
        RETURN "MINOR"
```

---

## Error Handling and Rework

### Rework Scenarios

#### Scenario 1: Business Context Issues (Return to Phase 3.0)
**Triggers**:
- Business domain incorrectly identified
- Business stakeholders missing or incorrect
- Business vocabulary incomplete or inaccurate
- Business constraints misunderstood

**Actions**:
1. Update Phase 3.0 task with specific corrections needed
2. Re-assign business_context_analyst
3. Re-execute Phase 3.0 with focus on identified issues
4. Re-execute Phase 3.1 (business context changed)
5. Re-execute Phase 3.2 (new specification to review)

#### Scenario 2: Extraction Issues (Return to Phase 3.1)
**Triggers**:
- Business entities at code structure level (not business concept level)
- Business rules are code patterns (not business policies)
- Technical rules in Chapter 3 (should be in Chapter 6)
- Technology-agnostic language violations in Chapters 1-5
- Missing business requirements

**Actions**:
1. Update Phase 3.1 task with specific corrections needed
2. Re-assign business_specialist_logic_extraction
3. Re-execute Phase 3.1 with focus on identified issues
4. Re-execute Phase 3.2 (new specification to review)

#### Scenario 3: Minor Review Issues (Fix in Phase 3.2)
**Triggers**:
- Minor wording improvements
- Small clarifications needed
- Bilingual translation adjustments
- Minor business rationale additions

**Actions**:
1. Business analyst reviewer makes corrections directly
2. Update reviewed specification
3. Update review report with changes made
4. Mark as "Approved with Changes"

#### Scenario 4: Critical Issues (Escalate to Human)
**Triggers**:
- Major business requirement gaps that cannot be resolved from code
- Conflicting business policies requiring business decision
- Ambiguous business logic requiring domain expert input
- Technical implementation issues preventing extraction

**Actions**:
1. Document critical issues in review report
2. Escalate to human supervisor with detailed explanation
3. Halt workpackage processing
4. Await human guidance before proceeding

---

## Progress Tracking

### Master Progress Tracking
**File**: `{{PROJECT_BASE_PATH}}/output/migration/phase_3_master_progress.md`

**Structure**:
```markdown
# Phase 3: Business Specification - Master Progress

## Overall Status
- Total Workpackages: [count]
- Completed: [count]
- In Progress: [count]
- Blocked: [count]

## Workpackage Status

| WP ID | Name | Phase 3.0 | Phase 3.1 | Phase 3.2 | Overall Status | Notes |
|-------|------|-----------|-----------|-----------|----------------|-------|
| WP-001 | [Name] | ✅ Complete | ✅ Complete | ✅ Approved | Ready for Phase 4 | |
| WP-002 | [Name] | ✅ Complete | 🔄 In Progress | ⏸️ Pending | In Progress | |
| WP-003 | [Name] | 🔄 In Progress | ⏸️ Pending | ⏸️ Pending | In Progress | |
| WP-004 | [Name] | ⏸️ Pending | ⏸️ Pending | ⏸️ Pending | Not Started | |

## Phase-Specific Progress

### Phase 3.0: Business Context Discovery
- Completed: [count]
- In Progress: [count]
- Pending: [count]

### Phase 3.1: Business Specification Extraction
- Completed: [count]
- In Progress: [count]
- Pending: [count]

### Phase 3.2: Business Analyst Review
- Approved: [count]
- Approved with Changes: [count]
- Rejected (Rework): [count]
- In Review: [count]

## Issues and Blockers

| WP ID | Phase | Issue Type | Description | Status | Resolution |
|-------|-------|------------|-------------|--------|------------|
| WP-002 | 3.1 | Extraction | Missing business context | Open | Escalated to BA |
| WP-005 | 3.0 | Context | Ambiguous business domain | Open | Awaiting input |

## Rework History

| WP ID | Original Phase | Returned From | Reason | Rework Status |
|-------|----------------|---------------|--------|---------------|
| WP-001 | 3.1 | 3.2 | Technical rules in Chapter 3 | ✅ Resolved |
| WP-003 | 3.0 | 3.2 | Business domain incorrect | 🔄 In Progress |
```

---

## Quality Gates

### Phase 3.0 Quality Gate
**Criteria**:
- [ ] Business context document exists
- [ ] Business domain identified with confidence level
- [ ] Business stakeholders documented
- [ ] Business vocabulary extracted (minimum 5 terms)
- [ ] Business constraints identified
- [ ] Business outcomes documented
- [ ] Business glossary updated

**Gate Decision**:
- **PASS**: Proceed to Phase 3.1
- **FAIL**: Rework Phase 3.0 or escalate

### Phase 3.1 Quality Gate
**Criteria**:
- [ ] Business specification documents exist (EN and DN)
- [ ] IEEE 830-1998 compliance verified
- [ ] Business entities extracted (minimum 3 entities)
- [ ] Business rules extracted (minimum 5 rules)
- [ ] Business functions extracted (minimum 3 functions)
- [ ] Process flows documented
- [ ] Legacy implementation complete in Chapter 6
- [ ] Technology-agnostic language in Chapters 1-5
- [ ] Bilingual consistency verified
- [ ] Business context incorporated

**Gate Decision**:
- **PASS**: Proceed to Phase 3.2
- **FAIL**: Rework Phase 3.1 or escalate

### Phase 3.2 Quality Gate
**Criteria**:
- [ ] Review report exists
- [ ] All chapters reviewed
- [ ] Business accuracy verified
- [ ] Completeness verified
- [ ] Technology independence verified
- [ ] Modernization readiness verified
- [ ] Approval decision documented

**Gate Decision**:
- **APPROVED**: Proceed to Phase 4 (Code Generation)
- **APPROVED WITH CHANGES**: Apply changes, proceed to Phase 4
- **REJECTED**: Rework Phase 3.0 or 3.1 based on issue type
- **ESCALATED**: Await human guidance

---

## Configuration and Path Variables

### Project Paths
```
{{PROJECT_NAME}} = [Project name]
{{PROJECT_BASE_PATH}} = [Absolute path to project root]
{{PROMPTS_BASE_PATH}} = {{PROJECT_BASE_PATH}}/prompts
{{TASKS_BASE_PATH}} = {{PROJECT_BASE_PATH}}/tasks  # Not used for Phase 3 (task documents in prompts/)
```

### Input Paths
```
{{SOURCE_CODE}} = {{PROJECT_BASE_PATH}}/input/source_code
{{DATABASE_SOURCE_CODE}} = {{PROJECT_BASE_PATH}}/input/database_source_code
{{DEPENDENCY_ANALYSIS_TABLE}} = {{PROJECT_BASE_PATH}}/output/analysis/dependency_analysis_table.csv
```

### Output Paths
```
{{BUSINESS_CONTEXT_BASE_PATH}} = {{PROJECT_BASE_PATH}}/output/business_specification/context
{{BUSINESS_SPECIFICATION_BASE_PATH}} = {{PROJECT_BASE_PATH}}/output/business_specification/specifications
{{BUSINESS_SPECIFICATION_REVIEW}} = {{PROJECT_BASE_PATH}}/output/business_specification/review
{{BUSINESS_SPECIFICATION_REPORTING}} = {{PROJECT_BASE_PATH}}/output/business_specification/reporting
```

### Status and Error Tracking
```
{{BUSINESS_CONTEXT_STATUS}} = {{PROJECT_BASE_PATH}}/output/business_specification/context/status.md
{{BUSINESS_CONTEXT_ERRORS}} = {{PROJECT_BASE_PATH}}/output/business_specification/context/errors.md
{{BUSINESS_SPECIFICATION_STATUS}} = {{PROJECT_BASE_PATH}}/output/business_specification/specifications/status.md
{{BUSINESS_SPECIFICATION_ERRORS}} = {{PROJECT_BASE_PATH}}/output/business_specification/specifications/errors.md
```

### Template Paths
```
{{BUSINESS_CONTEXT_TEMPLATE}} = {{PROJECT_BASE_PATH}}/templates/business_context_template.md
{{BUSINESS_SPECIFICATION_TEMPLATE}} = {{PROJECT_BASE_PATH}}/templates/business_specification_template.md
{{BUSINESS_CONTEXT_STATUS_TEMPLATE}} = {{PROJECT_BASE_PATH}}/templates/business_context_status_template.md
{{BUSINESS_CONTEXT_ERRORS_TEMPLATE}} = {{PROJECT_BASE_PATH}}/templates/business_context_errors_template.json
{{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}} = {{PROJECT_BASE_PATH}}/templates/business_specification_status_template.md
{{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}} = {{PROJECT_BASE_PATH}}/templates/business_specification_errors_template.json
```

---

## Supervisor Responsibilities

### Pre-Execution
1. Verify all prerequisites from Phase 1 and Phase 2 exist
2. Verify all path variables are resolved to absolute paths
3. Verify all template files exist
4. Verify all agents are available and properly configured
5. Verify all phase task documents exist in {{PROMPTS_BASE_PATH}}
6. Create output directories if they don't exist
7. Initialize master progress tracking

### During Execution
1. Assign appropriate agent for each phase
2. Provide phase task document from {{PROMPTS_BASE_PATH}}
3. Monitor phase execution progress
4. Verify phase completion against quality gates
5. Handle errors and rework scenarios
6. Update master progress tracking
7. Escalate critical issues to human supervisor

### Post-Execution
1. Verify all workpackages completed successfully
2. Generate final summary report
3. Archive all artifacts
4. Prepare handoff to Phase 4 (Code Generation)

---

## Success Criteria

Phase 3 is considered complete when:
- [ ] All workpackages have completed Phase 3.0, 3.1, and 3.2
- [ ] All business specifications approved (or approved with changes)
- [ ] All review reports completed
- [ ] All business context documents finalized
- [ ] Business glossary consolidated and finalized
- [ ] Master progress tracking shows 100% completion
- [ ] No critical blockers remain
- [ ] All artifacts ready for Phase 4 (Code Generation)

---

## Notes for Supervisor

**Critical Success Factors**:
1. **Business context first**: Phase 3.0 must establish solid business understanding before extraction
2. **Technology-agnostic focus**: Chapters 1-5 must be free of technical jargon
3. **Business vs technical separation**: Business rules in Chapter 3, technical rules in Chapter 6
4. **Bilingual consistency**: EN and DN versions must have identical structure and logic
5. **Traceability**: All business requirements must trace to legacy code in Chapter 6

**Common Pitfalls to Avoid**:

1. Skipping Phase 3.0 and jumping to extraction (results in code translation, not business extraction)
2. Allowing technical jargon in Chapters 1-5 (violates technology-agnostic principle)
3. Documenting code patterns as business rules (results in translated COBOL, not business policies)
4. Incomplete Chapter 6 (breaks traceability)
5. Inconsistent EN/DN versions (breaks bilingual requirement)
**When to Escalate**:

1. Major business requirement gaps that cannot be resolved from code
2. Conflicting business policies requiring business decision
3. Ambiguous business logic requiring domain expert input
4. Technical implementation issues preventing extraction
5. Repeated rework cycles (more than 2 iterations per workpackage)

---

## End of Master Orchestration Document