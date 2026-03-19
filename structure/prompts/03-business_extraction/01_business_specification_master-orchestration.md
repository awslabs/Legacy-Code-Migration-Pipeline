
# Phase 3: Business Specification - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 3 - Business Specification
**Version**: 1.2
**Date**: 2026-03-03
**Owner**: business_team_supervisor

---

## CRITICAL - Delegation Check

**IF YOU ARE NOT THE OWNER OF THIS DOCUMENT, STOP AND DELEGATE**

This document is owned by: **business_team_supervisor**

**Before proceeding, check your role**:
- If you are **business_team_supervisor**: Continue with orchestration
- If you are **ANY OTHER AGENT**: 
  1. STOP immediately
  2. Delegate this entire prompt to **business_team_supervisor**
  3. Wait for their response
  4. Do NOT attempt to execute the orchestration yourself

**Why this matters**: Only the designated supervisor has the authority and context to orchestrate the entire phase across multiple agents. Attempting to execute orchestration from a non-supervisor role will result in incomplete or incorrect execution.

---

## Overview

This document provides orchestration instructions for the Business Specification phase, which extracts business requirements from legacy code through a six-phase process:

1. **Phase 3.0**: Business Context Discovery - Understand business domain and intent
2. **Phase 3.0.1**: Business Context Review - Validate business context accuracy
3. **Phase 3.1**: Business Logic Extraction - Extract technical evidence (Chapter 6)
4. **Phase 3.1.1**: Business Logic Extraction Review - Validate abstractions and detect drift
5. **Phase 3.2**: Business Specification Generation - Create business requirements (Chapters 1-5)
6. **Phase 3.2.1**: Business Specification Review - Validate specifications and detect drift

**Critical Principle**: Extract **reimagined business requirements** (technology-agnostic) rather than **translated code structures** (technology-specific).

**Critical Quality Control**: Chapter 6 (Legacy Implementation References) serves as the evidence base and drift detection mechanism. All business abstractions in Chapters 1-5 must be traceable to code evidence in Chapter 6.

---

## Phase Task Documents

The complete task documents for each phase are located in the prompts directory:
- **Phase 3.0**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0_business_context_discovery.md
- **Phase 3.0.1**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0.1_business_context_review.md
- **Phase 3.1**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1_business_logic_extraction.md
- **Phase 3.1.1**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1.1_business_logic_extraction_review.md
- **Phase 3.2**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2_business_specification_generation.md
- **Phase 3.2.1**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2.1_business_specification_review.md

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
                                                    Phase 3.0.1 (Context Review)
                                                            ↓
                                                    Phase 3.1 (Logic Extraction - Chapter 6)
                                                            ↓
                                                    Phase 3.1.1 (Logic Extraction Review)
                                                            ↓
                                                    Phase 3.2 (Specification Generation - Chapters 1-5)
                                                            ↓
                                                    Phase 3.2.1 (Specification Review)
                                                            ↓
                                                    Phase 4 (Code Generation)
```

**Prerequisites**:
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
        ASSIGN: business_specialist_requirements
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0_business_context_discovery.md
        
        INPUTS:
            - Workpackage planning: {{WORKPACKAGE_PLANNING}}
            - Business flows: {{BUSINESS_FLOWS}}
            - Source code files: {{SOURCE_CODE}}
            - Database source code: {{DATABASE_SOURCE_CODE}}
            - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
            - Legacy documentation: {{PROJECT_BASE_PATH}}/input/legacy_documentation/
            - Business documentation: {{PROJECT_BASE_PATH}}/input/business_documentation/
        
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
                PROCEED to Phase_3.0.1

    # ========================================
    # PHASE 3.0.1: BUSINESS CONTEXT REVIEW
    # ========================================
    
    EXECUTE Phase_3.0.1:
        ASSIGN: business_reviewer_requirements
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0.1_business_context_review.md
        
        INPUTS:
            - Business context document: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
            - Source code files: {{SOURCE_CODE}} (for verification if needed)
            - Workpackage definitions: {{PROJECT_BASE_PATH}}/output/analysis/workpackages/
        
        EXPECTED_OUTPUTS:
            - Business context review report: {{BUSINESS_CONTEXT_REVIEW}}/WP-XXX-business-context-review.md
            - Approved business context: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md (main folder)
            - Archived draft: {{BUSINESS_CONTEXT_REVIEW}}/WP-XXX-business-context-draft.md (moved to review folder)
            - Progress tracking: {{BUSINESS_CONTEXT_STATUS}}
        
        VERIFICATION:
            CHECK review_report_exists(WP-XXX, "context")
            CHECK approval_decision_documented(WP-XXX, "context")
            
            approval_status = GET_CONTEXT_APPROVAL_STATUS(WP-XXX)
            
            IF approval_status == "APPROVED":
                UPDATE {{BUSINESS_CONTEXT_STATUS}} with "Approved"
                PROCEED to Phase_3.1
            
            ELSE IF approval_status == "APPROVED_WITH_CHANGES":
                CHECK approved_context_exists(WP-XXX)
                UPDATE {{BUSINESS_CONTEXT_STATUS}} with "Approved with Changes"
                PROCEED to Phase_3.1
            
            ELSE IF approval_status == "REJECTED":
                LOG "Business context rejected, returning to Phase 3.0"
                UPDATE {{BUSINESS_CONTEXT_STATUS}} with "Returned to Phase 3.0"
                RETURN_TO Phase_3.0

    # ========================================
    # PHASE 3.1: BUSINESS LOGIC EXTRACTION (CHAPTER 6)
    # ========================================
    
    EXECUTE Phase_3.1:
        ASSIGN: business_specialist_logic_extraction
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1_business_logic_extraction.md
        
        INPUTS:
            - Approved business context: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
            - Workpackage planning: {{WORKPACKAGE_PLANNING}}
            - Business flows: {{BUSINESS_FLOWS}}
            - Source code files: {{SOURCE_CODE}}
            - Database source code: {{DATABASE_SOURCE_CODE}}
            - Legacy specifications: {{PROJECT_BASE_PATH}}/input/legacy_specifications/
        
        EXPECTED_OUTPUTS:
            - Chapter 6 (draft): {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md
            - Logic extraction notes: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md
            - Progress tracking: {{BUSINESS_TRACEABILITY_STATUS}}
            - Error reports (if any): {{BUSINESS_TRACEABILITY_ERRORS}}
        
        VERIFICATION:
            CHECK chapter6_exists(WP-XXX)
            CHECK logic_notes_exist(WP-XXX)
            CHECK chapter6_section_complete(WP-XXX, "6.1")  # Source Files
            CHECK chapter6_section_complete(WP-XXX, "6.2")  # Business Rule Implementation
            CHECK chapter6_section_complete(WP-XXX, "6.3")  # Function Implementation
            CHECK chapter6_section_complete(WP-XXX, "6.4")  # Database Tables
            CHECK chapter6_section_complete(WP-XXX, "6.5")  # Error Codes
            CHECK chapter6_section_complete(WP-XXX, "6.6")  # Technical Architecture
            CHECK chapter6_section_complete(WP-XXX, "6.7")  # Data Flow Architecture
            CHECK chapter6_section_complete(WP-XXX, "6.8")  # Technical Rules
            CHECK abstractions_documented(WP-XXX)
            
            IF verification_failed:
                LOG error to {{BUSINESS_SPECIFICATION_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with completion
                PROCEED to Phase_3.1.1

    # ========================================
    # PHASE 3.1.1: BUSINESS LOGIC EXTRACTION REVIEW
    # ========================================
    
    EXECUTE Phase_3.1.1:
        ASSIGN: business_reviewer_logic_extraction
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1.1_business_logic_extraction_review.md
        
        INPUTS:
            - Chapter 6 (draft): {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md
            - Logic extraction notes: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md
            - Approved business context: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md
            - Source code files: {{SOURCE_CODE}} (for verification)
            - Database definitions: {{DATABASE_SOURCE_CODE}}
        
        EXPECTED_OUTPUTS:
            - Logic extraction review report: {{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-logic-extraction-review.md
            - Drift detection report (if issues): {{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-drift-report.md
            - Approved Chapter 6: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md (main folder)
            - Archived draft: {{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-chapter6-draft.md (moved to review folder)
            - Progress tracking: {{BUSINESS_TRACEABILITY_STATUS}}
        
        VERIFICATION:
            CHECK logic_review_report_exists(WP-XXX)
            CHECK drift_metrics_calculated(WP-XXX)
            CHECK approval_decision_documented(WP-XXX, "logic_extraction")
            
            approval_status = GET_LOGIC_APPROVAL_STATUS(WP-XXX)
            drift_percentage = GET_DRIFT_PERCENTAGE(WP-XXX)
            
            IF approval_status == "APPROVED" AND drift_percentage < 10:
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Logic Extraction Approved"
                PROCEED to Phase_3.2
            
            ELSE IF approval_status == "APPROVED_WITH_CHANGES" AND drift_percentage < 10:
                CHECK approved_chapter6_exists(WP-XXX)
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Logic Extraction Approved with Changes"
                PROCEED to Phase_3.2
            
            ELSE IF approval_status == "REJECTED" OR drift_percentage >= 10:
                LOG "Logic extraction rejected or drift too high, returning to Phase 3.1"
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Returned to Phase 3.1"
                RETURN_TO Phase_3.1

    # ========================================
    # PHASE 3.2: BUSINESS SPECIFICATION GENERATION (CHAPTERS 1-5)
    # ========================================
    
    EXECUTE Phase_3.2:
        ASSIGN: business_specialist_requirements
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2_business_specification_generation.md

        INPUTS:
            - Approved Chapter 6: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md
            - Approved business context: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
            - Logic extraction notes: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md
        
        EXPECTED_OUTPUTS:
            - Business specification - draft: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-draft.md
            - Traceability matrix: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md
            - Progress tracking: {{BUSINESS_SPECIFICATION_STATUS}}
        
        VERIFICATION:
            CHECK specification_exists(WP-XXX)
            CHECK traceability_matrix_exists(WP-XXX)
            CHECK ieee_830_compliance(WP-XXX)
            CHECK business_entities_extracted(WP-XXX)
            CHECK business_rules_extracted(WP-XXX)
            CHECK business_functions_extracted(WP-XXX)
            CHECK process_flows_extracted(WP-XXX)
            CHECK technology_agnostic_chapters_1_5(WP-XXX)
            CHECK all_elements_trace_to_chapter6(WP-XXX)
            
            IF verification_failed:
                LOG error to {{BUSINESS_SPECIFICATION_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with completion
                PROCEED to Phase_3.2.1

    # ========================================
    # PHASE 3.2.1: BUSINESS SPECIFICATION REVIEW
    # ========================================
    
    EXECUTE Phase_3.2.1:
        ASSIGN: business_reviewer_requirements
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2.1_business_specification_review.md
        
        INPUTS:
            - Business specification - draft: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-draft.md
            - Approved Chapter 6: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md
            - Traceability matrix: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md
            - Approved business context: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md
            - Business glossary: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
        
        EXPECTED_OUTPUTS:
            - Approved specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-approved.md (main folder)
            - Archived draft: {{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-draft.md (moved to review folder)
            - Review report: {{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md
            - Updated context (if needed): {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-updated.md
            - Updated glossary (if needed): {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md (living document)
            - Progress tracking: {{BUSINESS_SPECIFICATION_STATUS}}
            - Updated glossary (if needed): {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary-updated.md
            - Progress tracking: {{BUSINESS_SPECIFICATION_STATUS}}
        
        VERIFICATION:
            CHECK review_report_exists(WP-XXX)
            CHECK backward_validation_performed(WP-XXX)
            CHECK drift_metrics_calculated(WP-XXX)
            CHECK approval_decision_documented(WP-XXX)
            
            approval_status = GET_APPROVAL_STATUS(WP-XXX)
            drift_percentage = GET_SPEC_DRIFT_PERCENTAGE(WP-XXX)
            
            IF approval_status == "APPROVED" AND drift_percentage < 5:
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Approved"
                MARK workpackage as ready for Phase 4 (Code Generation)
                PROCEED to next workpackage
            
            ELSE IF approval_status == "APPROVED_WITH_CHANGES" AND drift_percentage < 5:
                CHECK reviewed_specifications_exist(WP-XXX)
                UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Approved with Changes"
                MARK workpackage as ready for Phase 4 (Code Generation)
                PROCEED to next workpackage
            
            ELSE IF approval_status == "REJECTED" OR drift_percentage >= 5:
                issue_type = GET_ISSUE_TYPE(WP-XXX)
                
                IF issue_type == "BUSINESS_CONTEXT":
                    LOG "Business context issues identified, returning to Phase 3.0"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Returned to Phase 3.0"
                    RETURN_TO Phase_3.0
                
                ELSE IF issue_type == "LOGIC_EXTRACTION":
                    LOG "Logic extraction issues identified, returning to Phase 3.1"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Returned to Phase 3.1"
                    RETURN_TO Phase_3.1
                
                ELSE IF issue_type == "SPECIFICATION":
                    LOG "Specification issues identified, returning to Phase 3.2"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Returned to Phase 3.2"
                    RETURN_TO Phase_3.2
                
                ELSE IF issue_type == "CRITICAL":
                    LOG "Critical issues identified, escalating to human supervisor"
                    ESCALATE to human supervisor
                    HALT workpackage processing
                
                ELSE:
                    LOG "Minor issues identified, fixing in Phase 3.2.1"
                    UPDATE {{BUSINESS_SPECIFICATION_STATUS}} with "Fixing in Phase 3.2.1"
                    RETRY Phase_3.2.1

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
**Agent**: business_specialist_requirements
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0_business_context_discovery.md
**Capabilities**:
- Business domain identification
- Stakeholder analysis
- Business vocabulary extraction
- Business constraint identification
- Business problem articulation

### Phase 3.0.1: Business Context Review
**Agent**: business_reviewer_requirements
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0.1_business_context_review.md
**Capabilities**:
- Business domain verification
- Stakeholder completeness validation
- Business vocabulary consistency checking
- Confidence assessment

### Phase 3.1: Business Logic Extraction (Chapter 6)
**Agent**: business_specialist_logic_extraction
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1_business_logic_extraction.md
**Capabilities**:
- Code analysis and interpretation
- Technical implementation documentation
- Evidence-based abstraction
- Chapter 6 creation with complete traceability
- Allowed abstraction pattern application

### Phase 3.1.1: Business Logic Extraction Review
**Agent**: business_reviewer_logic_extraction
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1.1_business_logic_extraction_review.md
**Capabilities**:
- Abstraction pattern validation
- Drift detection
- Chapter 6 completeness verification
- Traceability verification
- Evidence base quality assessment

### Phase 3.2: Business Specification Generation (Chapters 1-5)
**Agent**: business_specialist_requirements
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2_business_specification_generation.md
**Capabilities**:
- Business entity extraction from Chapter 6
- Business rule extraction from Chapter 6
- Business function identification from Chapter 6
- Process flow documentation from Chapter 6
- IEEE 830-1998 documentation
- Technology-agnostic specification writing

### Phase 3.2.1: Business Specification Review
**Agent**: business_reviewer_requirements
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2.1_business_specification_review.md
**Capabilities**:
- Backward validation against Chapter 6
- Drift metrics calculation
- Business policy validation
- Requirement completeness verification
- Technology-agnostic language verification
- Modernization readiness assessment

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
- Business specification: `WP-XXX-FLOW_XXX-specification.md`

**Contract**:
- IEEE 830-1998 format compliance
- 6 chapters complete (Introduction, Entities, Rules, Functions, Flows, Legacy Implementation)
- Business entities with BE-XXX identifiers
- Business rules with BR-XXX identifiers
- Business functions with F-XXX identifiers
- Technology-agnostic Chapters 1-5
- Complete legacy implementation in Chapter 6

### Phase 3.2 → Phase 4
**Phase 3.2 Outputs** (Phase 4 Inputs):
- Reviewed specification: `WP-XXX-FLOW_XXX-specification-reviewed.md`
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
CHECK specification_exists(workpackage_id):
    file_path = {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{workpackage_id}-FLOW_XXX-specification.md
    RETURN file_exists(file_path)

CHECK ieee_830_compliance(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    RETURN spec_doc.has_chapter(1, "Introduction")
        AND spec_doc.has_chapter(2, "Business Entities")
        AND spec_doc.has_chapter(3, "Business Rules")
        AND spec_doc.has_chapter(4, "Business Functions")
        AND spec_doc.has_chapter(5, "Process Flows")
        AND spec_doc.has_chapter(6, "Legacy Implementation References")

CHECK business_entities_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    RETURN spec_doc.chapter_2.entity_count >= 1
        AND all_entities_have_identifier(spec_doc.chapter_2, pattern="BE-{workpackage_id}-XXX")

CHECK business_rules_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    RETURN spec_doc.chapter_3.rule_count >= 1
        AND all_rules_have_identifier(spec_doc.chapter_3, pattern="BR-{workpackage_id}-XXX")

CHECK business_functions_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    RETURN spec_doc.chapter_4.function_count >= 1
        AND all_functions_have_identifier(spec_doc.chapter_4, pattern="F-{workpackage_id}-XXX")

CHECK process_flows_extracted(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    RETURN spec_doc.chapter_5.flow_count >= 1

CHECK legacy_implementation_documented(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    RETURN spec_doc.chapter_6.source_files IS NOT EMPTY
        AND spec_doc.chapter_6.business_rule_implementation IS NOT EMPTY
        AND spec_doc.chapter_6.function_implementation IS NOT EMPTY

CHECK technology_agnostic_chapters_1_5(workpackage_id):
    spec_doc = load_specification(workpackage_id)
    technical_terms = ["COBOL", "CICS", "JCL", "DB2", "mainframe", "batch", "online", 
                       "transaction", "file", "record", "paragraph", "PERFORM", "MOVE", "CALL"]
    
    FOR chapter IN [1, 2, 3, 4, 5]:
        chapter_text = spec_doc.get_chapter_text(chapter)
        FOR term IN technical_terms:
            IF term IN chapter_text:
                LOG "Technical term '{term}' found in Chapter {chapter}"
                RETURN FALSE
    
    RETURN TRUE

CHECK business_context_incorporated(workpackage_id):
    spec_doc = load_specification(workpackage_id)
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
- Minor business rationale additions

**Actions**:
1. Business specialist reviewer makes corrections directly
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

**Markdown File**: `{{BUSINESS_SPECIFICATION_MASTER_PROGRESS}}`
**JSON File**: `{{BUSINESS_SPECIFICATION_MASTER_PROGRESS_JSON}}`

**Templates**:
- Markdown: `{{BUSINESS_SPECIFICATION_MASTER_PROGRESS_TEMPLATE}}`
- JSON: `{{BUSINESS_SPECIFICATION_MASTER_PROGRESS_JSON_TEMPLATE}}`

Both files track the same information in different formats:
- **Markdown**: Human-readable progress report
- **JSON**: Machine-readable for programmatic analysis

**Structure** (both formats contain):
```
Overall Status:
- Total Workpackages
- Completed
- In Progress
- Blocked
- Last Updated

Workpackage Status:
- WP ID, Name
- Phase 3.0 Status
- Phase 3.1 Status
- Phase 3.2 Status
- Overall Status
- Notes

Phase-Specific Progress:
- Phase 3.0: Completed, In Progress, Pending
- Phase 3.1: Completed, In Progress, Pending
- Phase 3.2: Approved, Approved with Changes, Rejected, In Review

Issues and Blockers:
- WP ID, Phase, Issue Type, Description, Status, Resolution

Rework History:
- WP ID, Original Phase, Returned From, Reason, Rework Status
```

**Update Frequency**: After each phase completion or status change

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
- [ ] Business specification document exists
- [ ] IEEE 830-1998 compliance verified
- [ ] Business entities extracted (minimum 3 entities)
- [ ] Business rules extracted (minimum 5 rules)
- [ ] Business functions extracted (minimum 3 functions)
- [ ] Process flows documented
- [ ] Legacy implementation complete in Chapter 6
- [ ] Technology-agnostic language in Chapters 1-5
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
Project Name = {{PROJECT_NAME}}
Project = {{PROJECT_BASE_PATH}}
Prompts = {{PROMPTS_BASE_PATH}}
Tasks = {{TASKS_BASE_PATH}}
```

### Input Paths
```
Source Code = {{SOURCE_CODE}}
Database Source Code = {{DATABASE_SOURCE_CODE}}
```

### Output Paths
```
Business Context = {{BUSINESS_CONTEXT_BASE_PATH}}
Business Specification = {{BUSINESS_SPECIFICATION_BASE_PATH}}
Business Specification Review = {{BUSINESS_SPECIFICATION_REVIEW}}
```

### Status and Error Tracking
```
Business Context Status = {{BUSINESS_CONTEXT_STATUS}}
Business Context Errors = {{BUSINESS_CONTEXT_ERRORS}}
Business Specification Status = {{BUSINESS_SPECIFICATION_STATUS}}
Business Specification Errors = {{BUSINESS_SPECIFICATION_ERRORS}}
```

### Template Paths
```
Business Context Template = {{BUSINESS_CONTEXT_TEMPLATE}}
Business Specification Template = {{BUSINESS_SPECIFICATION_TEMPLATE}}
Business Context Status Template = {{BUSINESS_CONTEXT_STATUS_TEMPLATE}}
Business Context Errors Template = {{BUSINESS_CONTEXT_ERRORS_TEMPLATE}}
Business Specification Status Template = {{BUSINESS_SPECIFICATION_STATUS_TEMPLATE}}
Business Specification Errors Template = {{BUSINESS_SPECIFICATION_ERRORS_TEMPLATE}}
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
2. Archive all artifacts
3. Prepare handoff to Phase 4 (Code Generation)

**Note**: Do NOT create additional summary reports. All necessary information is captured in:
- Approved deliverables (specifications, Chapter 6, context)
- Review reports (in `/review` folders)
- Progress tracking (status JSON files)
- Error logs (if any issues occurred)

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
4. **Traceability**: All business requirements must trace to legacy code in Chapter 6

**Common Pitfalls to Avoid**:

1. Skipping Phase 3.0 and jumping to extraction (results in code translation, not business extraction)
2. Allowing technical jargon in Chapters 1-5 (violates technology-agnostic principle)
3. Documenting code patterns as business rules (results in translated COBOL, not business policies)
4. Incomplete Chapter 6 (breaks traceability)
**When to Escalate**:

1. Major business requirement gaps that cannot be resolved from code
2. Conflicting business policies requiring business decision
3. Ambiguous business logic requiring domain expert input
4. Technical implementation issues preventing extraction
5. Repeated rework cycles (more than 2 iterations per workpackage)

---

## End of Master Orchestration Document