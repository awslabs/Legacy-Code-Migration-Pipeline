# Phase 5: Code Generation - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 5 - Code Generation
**Version**: 1.0
**Date**: 2026-02-16
**Owner**: development_team_supervisor

---

## Overview

This document provides orchestration instructions for the Code Generation phase, which implements modern code from business specifications through a workpackage-based process:

1. **Phase 5.0**: Technical Specification Extraction - Extract and document technical implementation details
2. **Phase 5.1**: Project Structure Establishment - Set up project scaffolding
3. **Phase 5.2**: Backend Code Generation - Implement backend tier
4. **Phase 5.3**: Frontend Code Generation - Implement frontend tier
5. **Phase 5.4**: Batch Code Generation - Implement batch tier

**Critical Principle**: Process **one workpackage at a time** in dependency order, implementing all required tiers for each workpackage before moving to the next.

---

## Phase Task Documents

The complete task documents for each phase are located in the prompts directory:
- **Phase 5.0**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0_tech_spec_extraction_master_orchestration.md
- **Phase 5.1**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1_project_structure.md
- **Phase 5.2**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.2_backend_generation.md
- **Phase 5.3**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.3_frontend_generation.md
- **Phase 5.4**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.4_batch_generation.md

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
Phase 4 (Test Case Generation) → Phase 5 (Code Generation)
                                        ↓
                                Phase 5.0 (Technical Specification Extraction)
                                        ↓
                                Phase 5.1 (Project Structure)
                                        ↓
                                WORKPACKAGE_LOOP:
                                    ↓
                                Phase 5.2 (Backend - if needed)
                                    ↓
                                Phase 5.3 (Frontend - if needed)
                                    ↓
                                Phase 5.4 (Batch - if needed)
                                    ↓
                                Next Workpackage
```

**Prerequisites**:
- Phase 3 outputs: Business specifications
- Phase 4 outputs: Test case definitions
- Workpackage planning with dependencies
- Target framework specifications

---

## Orchestration Workflow

### Phase 5.0: Technical Specification Extraction

```
EXECUTE Phase_5.0:
    # Phase 5.0 has its own master orchestration document
    # It delegates to Phase 5.0.0 (Creation) and Phase 5.0.1 (Review)
    PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0_tech_spec_extraction_master_orchestration.md
    
    INPUTS:
        - Target specifications: {{TARGET_SPECIFICATION}}/
        - Sample code: {{TARGET_SAMPLE_CODE}}/
        - Workpackage planning: {{WORKPACKAGE_PLANNING}}
    
    EXPECTED_OUTPUTS:
        - Backend tech spec: {{TECH_SPEC_BASE_PATH}}/specs/backend-tech-spec.md
        - Frontend tech spec: {{TECH_SPEC_BASE_PATH}}/specs/frontend-tech-spec.md
        - Batch tech spec: {{TECH_SPEC_BASE_PATH}}/specs/batch-tech-spec.md
        - Infrastructure tech spec: {{TECH_SPEC_BASE_PATH}}/specs/infrastructure-tech-spec.md
        - Progress tracking: {{TECH_SPEC_BASE_PATH}}/specs/progress/Tech_Spec_Status.json
        - Review artifacts: {{TECH_SPEC_BASE_PATH}}/specs/review/
    
    VERIFICATION:
        CHECK tech_specs_exist()
        CHECK tech_specs_reviewed_and_approved()
        CHECK progress_tracking_complete()
        
        IF verification_failed:
            LOG error to {{TECH_SPEC_BASE_PATH}}/specs/logs/tech-spec-errors.json
            ESCALATE to human supervisor
            HALT processing
        
        IF verification_passed:
            UPDATE {{CODE_GENERATION_STATUS}} with Phase 5.0 completion
            PROCEED to Phase_5.1
```

### Phase 5.1: Project Structure Establishment

```
EXECUTE Phase_5.1:
    ASSIGN: development_specialist_code_generation
    PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1_project_structure.md
    
    INPUTS:
        - Technical specifications: {{TECH_SPEC_BASE_PATH}}/specs/
        - Target specifications: {{TARGET_SPECIFICATION}}/
        - Sample code: {{TARGET_SAMPLE_CODE}}/
        - Workpackage planning: {{WORKPACKAGE_PLANNING}}
    
    EXPECTED_OUTPUTS:
        - Backend project structure: {{CODE_GENERATION_BACKEND_OUTPUT}}/
        - Frontend project structure: {{CODE_GENERATION_FRONTEND_OUTPUT}}/
        - Batch project structure: {{CODE_GENERATION_BATCH_OUTPUT}}/
        - Build configuration files
        - Progress tracking: {{CODE_GENERATION_STATUS}}
    
    VERIFICATION:
        CHECK project_structure_exists()
        CHECK build_configuration_valid()
        CHECK progress_tracking_initialized()
        
        IF verification_failed:
            LOG error to {{CODE_GENERATION_ERRORS}}
            ESCALATE to human supervisor
            HALT processing
        
        IF verification_passed:
            UPDATE {{CODE_GENERATION_STATUS}} with Phase 5.1 completion
            PROCEED to WORKPACKAGE_LOOP
```

### Workpackage Loop

```
WORKPACKAGE_LOOP:
    # Read workpackage planning
    workpackages = READ {{WORKPACKAGE_PLANNING}}
    progress = READ {{CODE_GENERATION_STATUS}}
    
    # Find next unprocessed workpackage
    FOR EACH workpackage IN workpackages ORDER BY priority:
        IF workpackage NOT IN progress.completed:
            current_workpackage = workpackage
            BREAK
    
    IF no_unprocessed_workpackages:
        LOG "All workpackages completed"
        PROCEED to Phase_4_Complete
    
    # Determine which tiers are needed
    tiers_needed = DETERMINE_TIERS(current_workpackage)
    
    # ========================================
    # PHASE 5.2: BACKEND CODE GENERATION
    # ========================================
    
    IF "backend" IN tiers_needed:
        EXECUTE Phase_5.2:
            ASSIGN: development_specialist_code_generation
            PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.2_backend_generation.md
            PROVIDE_CONTEXT:
                - workpackage_id: current_workpackage.id
                - workpackage_name: current_workpackage.name
            
            INPUTS:
                - Technical specifications: {{TECH_SPEC_BASE_PATH}}/specs/backend-tech-spec.md
                - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md
                - Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
                - Target specification: {{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md
                - Sample code: {{TARGET_SAMPLE_CODE}}/backend/
            
            EXPECTED_OUTPUTS:
                - Backend code: {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/
                - Progress update: {{CODE_GENERATION_STATUS}}
            
            VERIFICATION:
                CHECK backend_code_exists(workpackage_id)
                CHECK code_compiles(workpackage_id, "backend")
                CHECK business_rules_implemented(workpackage_id)
                
                IF verification_failed:
                    LOG error to {{CODE_GENERATION_ERRORS}}
                    MARK workpackage as failed
                    ESCALATE to human supervisor
                    HALT workpackage processing
                
                IF verification_passed:
                    UPDATE {{CODE_GENERATION_STATUS}} with backend completion
                    PROCEED to Phase_5.3
    
    # ========================================
    # PHASE 5.3: FRONTEND CODE GENERATION
    # ========================================
    
    IF "frontend" IN tiers_needed:
        EXECUTE Phase_5.3:
            ASSIGN: development_specialist_code_generation
            PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.3_frontend_generation.md
            PROVIDE_CONTEXT:
                - workpackage_id: current_workpackage.id
                - workpackage_name: current_workpackage.name
            
            INPUTS:
                - Technical specifications: {{TECH_SPEC_BASE_PATH}}/specs/frontend-tech-spec.md
                - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md
                - Backend API: {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/
                - Target specification: {{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md
                - Sample code: {{TARGET_SAMPLE_CODE}}/frontend/
            
            EXPECTED_OUTPUTS:
                - Frontend code: {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/
                - Progress update: {{CODE_GENERATION_STATUS}}
            
            VERIFICATION:
                CHECK frontend_code_exists(workpackage_id)
                CHECK code_compiles(workpackage_id, "frontend")
                CHECK ui_components_implemented(workpackage_id)
                CHECK accessibility_compliance(workpackage_id)
                
                IF verification_failed:
                    LOG error to {{CODE_GENERATION_ERRORS}}
                    MARK workpackage as failed
                    ESCALATE to human supervisor
                    HALT workpackage processing
                
                IF verification_passed:
                    UPDATE {{CODE_GENERATION_STATUS}} with frontend completion
                    PROCEED to Phase_5.4
    
    # ========================================
    # PHASE 5.4: BATCH CODE GENERATION
    # ========================================
    
    IF "batch" IN tiers_needed:
        EXECUTE Phase_5.4:
            ASSIGN: development_specialist_code_generation
            PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.4_batch_generation.md
            PROVIDE_CONTEXT:
                - workpackage_id: current_workpackage.id
                - workpackage_name: current_workpackage.name
            
            INPUTS:
                - Technical specifications: {{TECH_SPEC_BASE_PATH}}/specs/batch-tech-spec.md
                - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md
                - Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
                - Target specification: {{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md
                - Sample code: {{TARGET_SAMPLE_CODE}}/batch/
            
            EXPECTED_OUTPUTS:
                - Batch code: {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/
                - Progress update: {{CODE_GENERATION_STATUS}}
            
            VERIFICATION:
                CHECK batch_code_exists(workpackage_id)
                CHECK code_compiles(workpackage_id, "batch")
                CHECK batch_jobs_implemented(workpackage_id)
                CHECK restart_capability_implemented(workpackage_id)
                
                IF verification_failed:
                    LOG error to {{CODE_GENERATION_ERRORS}}
                    MARK workpackage as failed
                    ESCALATE to human supervisor
                    HALT workpackage processing
                
                IF verification_passed:
                    UPDATE {{CODE_GENERATION_STATUS}} with batch completion
                    PROCEED to WORKPACKAGE_COMPLETE
    
    # ========================================
    # WORKPACKAGE COMPLETION
    # ========================================
    
    WORKPACKAGE_COMPLETE:
        LOG "Workpackage WP-{ID} completed successfully"
        UPDATE {{CODE_GENERATION_STATUS}} with workpackage completion
        UPDATE {{CODE_GENERATION_MASTER_PROGRESS}} with summary
        PROCEED to next workpackage in WORKPACKAGE_LOOP

END WORKPACKAGE_LOOP
```

---

## Agent Assignments

### Phase 5.0: Technical Specification Extraction
**Orchestration**: Phase 5.0 has its own master orchestration document
**Sub-phases**: 
- Phase 5.0.0 (Creation) - Assigned to tech_spec_extraction_specialist
- Phase 5.0.1 (Review) - Assigned to tech_spec_review_specialist
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0_tech_spec_extraction_master_orchestration.md
**Capabilities**:
- Discovery-based specification extraction
- Keyword-based search across specifications
- Technical pattern identification
- Assumption documentation
- Traceability management

### Phase 5.1: Project Structure Establishment
**Agent**: development_specialist_code_generation
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.1_project_structure.md
**Capabilities**:
- Project scaffolding setup
- Build configuration management
- Directory structure creation
- Configuration template setup
- Multi-tier project initialization

### Phase 5.2: Backend Code Generation
**Agent**: development_specialist_code_generation
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.2_backend_generation.md
**Capabilities**:
- Domain model implementation
- Repository layer development
- Service layer implementation
- API layer development
- Business rule implementation
- Validation and error handling
- Backend framework expertise

### Phase 5.3: Frontend Code Generation
**Agent**: development_specialist_code_generation
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.3_frontend_generation.md
**Capabilities**:
- UI component development
- State management implementation
- API integration
- Routing configuration
- Accessibility compliance
- Frontend framework expertise
- Responsive design implementation

### Phase 5.4: Batch Code Generation
**Agent**: development_specialist_code_generation
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.4_batch_generation.md
**Capabilities**:
- Batch job configuration
- Reader/processor/writer implementation
- Error handling and recovery
- Restart capability implementation
- Scheduling configuration
- Batch framework expertise

---

## Input/Output Contracts

### Phase 5.0 → Phase 5.1
**Phase 5.0 Outputs** (Phase 5.1 Inputs):
- Backend technical specification with all implementation details
- Frontend technical specification with all implementation details
- Batch technical specification with all implementation details
- Infrastructure technical specification with all implementation details
- Progress tracking and review approval

**Contract**:
- All technical specifications extracted and documented
- All specifications reviewed and approved
- Discovery-based approach used (no hardcoded assumptions)
- Traceability to source specifications maintained
- Assumptions documented where specifications unclear

### Phase 5.1 → Phase 5.2/5.3/5.4
**Phase 5.1 Outputs** (Phase 5.2/5.3/5.4 Inputs):
- Backend project structure with build files
- Frontend project structure with build files
- Batch project structure with build files
- Configuration templates
- Progress tracking initialized

**Contract**:
- All project directories created
- Build configuration files valid and compilable
- Configuration templates in place
- Progress tracking file initialized with project structure status

### Phase 3 → Phase 5.2
**Phase 3 Outputs** (Phase 5.2 Inputs):
- Business specification: `WP-XXX-specification.md`
- Test case definitions: `WP-XXX-tests.md`

**Contract**:
- Business entities with BE-XXX identifiers
- Business rules with BR-XXX identifiers
- Business functions with F-XXX identifiers
- Process flows documented
- Test cases defined for all business rules

### Phase 5.2 → Phase 5.3
**Phase 5.2 Outputs** (Phase 5.3 Inputs):
- Backend code: Domain model, repositories, services, API controllers
- API endpoints documented
- DTOs defined

**Contract**:
- Backend code compiles successfully
- API endpoints accessible
- Business rules implemented in backend
- DTOs available for frontend integration

### Phase 5.2/5.3/5.4 → Phase 6
**Phase 5 Outputs** (Phase 6 Inputs):
- Complete backend implementation
- Complete frontend implementation
- Complete batch implementation
- All code compiles successfully
- Progress tracking shows 100% completion

**Contract**:
- All workpackages implemented
- All tiers completed for each workpackage
- Code compiles without errors
- Business rules implemented and traceable
- Ready for integration testing

---

## Verification Criteria

### Phase 5.0 Verification
```
CHECK tech_specs_exist():
    backend_spec = file_exists({{TECH_SPEC_BASE_PATH}}/specs/backend-tech-spec.md)
    frontend_spec = file_exists({{TECH_SPEC_BASE_PATH}}/specs/frontend-tech-spec.md)
    batch_spec = file_exists({{TECH_SPEC_BASE_PATH}}/specs/batch-tech-spec.md)
    infra_spec = file_exists({{TECH_SPEC_BASE_PATH}}/specs/infrastructure-tech-spec.md)
    RETURN backend_spec AND frontend_spec AND batch_spec AND infra_spec

CHECK tech_specs_reviewed_and_approved():
    review_file = file_exists({{TECH_SPEC_BASE_PATH}}/specs/review/Tech_Spec_Review_Approval.json)
    IF NOT review_file:
        RETURN FALSE
    approval_data = load_json({{TECH_SPEC_BASE_PATH}}/specs/review/Tech_Spec_Review_Approval.json)
    RETURN approval_data.overallApproval == "approved"

CHECK progress_tracking_complete():
    status_file = file_exists({{TECH_SPEC_BASE_PATH}}/specs/progress/Tech_Spec_Status.json)
    IF NOT status_file:
        RETURN FALSE
    status_data = load_json({{TECH_SPEC_BASE_PATH}}/specs/progress/Tech_Spec_Status.json)
    RETURN status_data.status == "completed"
```

### Phase 5.1 Verification
```
CHECK project_structure_exists():
    backend_exists = directory_exists({{CODE_GENERATION_BACKEND_OUTPUT}})
    frontend_exists = directory_exists({{CODE_GENERATION_FRONTEND_OUTPUT}})
    batch_exists = directory_exists({{CODE_GENERATION_BATCH_OUTPUT}})
    RETURN backend_exists AND frontend_exists AND batch_exists

CHECK build_configuration_valid():
    backend_build = file_exists({{CODE_GENERATION_BACKEND_OUTPUT}}/pom.xml) 
                    OR file_exists({{CODE_GENERATION_BACKEND_OUTPUT}}/build.gradle)
    frontend_build = file_exists({{CODE_GENERATION_FRONTEND_OUTPUT}}/package.json)
    RETURN backend_build AND frontend_build

CHECK progress_tracking_initialized():
    status_file = file_exists({{CODE_GENERATION_STATUS}})
    status_data = load_json({{CODE_GENERATION_STATUS}})
    RETURN status_file AND status_data.projectStructureEstablished == true
```

### Phase 5.2 Verification
```
CHECK backend_code_exists(workpackage_id):
    code_path = {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{workpackage_id}
    RETURN directory_exists(code_path) AND directory_not_empty(code_path)

CHECK code_compiles(workpackage_id, tier):
    IF tier == "backend":
        result = execute_build({{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{workpackage_id})
    ELSE IF tier == "frontend":
        result = execute_build({{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{workpackage_id})
    ELSE IF tier == "batch":
        result = execute_build({{CODE_GENERATION_BATCH_OUTPUT}}/wp-{workpackage_id})
    
    RETURN result.exit_code == 0 AND result.errors.count == 0

CHECK business_rules_implemented(workpackage_id):
    spec = load_specification(workpackage_id)
    business_rules = spec.chapter_3.rules
    
    code_path = {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{workpackage_id}
    
    FOR EACH rule IN business_rules:
        rule_implemented = search_code_for_rule(code_path, rule.id)
        IF NOT rule_implemented:
            LOG "Business rule {rule.id} not found in code"
            RETURN FALSE
    
    RETURN TRUE
```

### Phase 5.3 Verification
```
CHECK frontend_code_exists(workpackage_id):
    code_path = {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{workpackage_id}
    RETURN directory_exists(code_path) AND directory_not_empty(code_path)

CHECK ui_components_implemented(workpackage_id):
    spec = load_specification(workpackage_id)
    ui_requirements = spec.chapter_5.ui_components
    
    code_path = {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{workpackage_id}
    
    FOR EACH component IN ui_requirements:
        component_exists = file_exists(code_path + "/" + component.name)
        IF NOT component_exists:
            LOG "UI component {component.name} not found"
            RETURN FALSE
    
    RETURN TRUE

CHECK accessibility_compliance(workpackage_id):
    code_path = {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{workpackage_id}
    
    # Check for basic accessibility attributes
    has_aria_labels = search_code_for_pattern(code_path, "aria-label")
    has_semantic_html = search_code_for_pattern(code_path, "<button|<nav|<main|<header")
    has_alt_text = search_code_for_pattern(code_path, "alt=")
    
    RETURN has_aria_labels OR has_semantic_html OR has_alt_text
```

### Phase 5.4 Verification
```
CHECK batch_code_exists(workpackage_id):
    code_path = {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{workpackage_id}
    RETURN directory_exists(code_path) AND directory_not_empty(code_path)

CHECK batch_jobs_implemented(workpackage_id):
    spec = load_specification(workpackage_id)
    batch_jobs = spec.chapter_5.batch_jobs
    
    code_path = {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{workpackage_id}
    
    FOR EACH job IN batch_jobs:
        job_config_exists = file_exists(code_path + "/jobs/" + job.name + ".xml")
        IF NOT job_config_exists:
            LOG "Batch job {job.name} configuration not found"
            RETURN FALSE
    
    RETURN TRUE

CHECK restart_capability_implemented(workpackage_id):
    code_path = {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{workpackage_id}
    
    # Check for restart/recovery patterns
    has_restart_config = search_code_for_pattern(code_path, "restartable|restart")
    has_checkpoint = search_code_for_pattern(code_path, "checkpoint|savepoint")
    
    RETURN has_restart_config OR has_checkpoint
```

---

## Error Handling and Rework

### Rework Scenarios

#### Scenario 0: Technical Specification Issues (Return to Phase 5.0)
**Triggers**:
- Incomplete technical specifications
- Missing critical implementation details
- Specification ambiguities preventing code generation
- Inconsistencies between specifications

**Actions**:
1. Update Phase 5.0 task with specific corrections needed
2. Re-execute Phase 5.0 with focus on identified issues
3. Re-review specifications
4. Verify all code generation phases can proceed with corrected specifications

#### Scenario 1: Project Structure Issues (Return to Phase 5.1)
**Triggers**:
- Build configuration invalid
- Missing directories
- Template configuration errors
- Incompatible framework versions

**Actions**:
1. Update Phase 5.1 task with specific corrections needed
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.1 with focus on identified issues
4. Verify all workpackages can proceed with corrected structure

#### Scenario 2: Backend Implementation Issues (Rework Phase 5.2)
**Triggers**:
- Code compilation errors
- Business rules not implemented
- Missing domain entities
- API layer incomplete
- Test failures

**Actions**:
1. Update Phase 5.2 task with specific corrections needed
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.2 for the affected workpackage
4. Re-verify compilation and business rule implementation

#### Scenario 3: Frontend Implementation Issues (Rework Phase 5.3)
**Triggers**:
- Code compilation errors
- UI components missing
- API integration failures
- Accessibility violations
- Routing errors

**Actions**:
1. Update Phase 5.3 task with specific corrections needed
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.3 for the affected workpackage
4. Re-verify compilation and UI implementation

#### Scenario 4: Batch Implementation Issues (Rework Phase 5.4)
**Triggers**:
- Code compilation errors
- Batch job configuration errors
- Missing restart capability
- Reader/processor/writer errors

**Actions**:
1. Update Phase 5.4 task with specific corrections needed
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.4 for the affected workpackage
4. Re-verify compilation and batch job implementation

#### Scenario 5: Critical Issues (Escalate to Human)
**Triggers**:
- Specification ambiguities preventing implementation
- Framework compatibility issues
- Missing business requirements
- Technical blockers requiring architectural decisions

**Actions**:
1. Document critical issues in error log
2. Escalate to human supervisor with detailed explanation
3. Halt workpackage processing
4. Await human guidance before proceeding

---

## Progress Tracking

### Master Progress Tracking

**JSON File**: `{{CODE_GENERATION_STATUS}}`
**Markdown File**: `{{CODE_GENERATION_MASTER_PROGRESS}}`

**Templates**:
- JSON: `{{CODE_GENERATION_STATUS_TEMPLATE}}`
- Markdown: `{{CODE_GENERATION_MASTER_PROGRESS_TEMPLATE}}`

**JSON Structure**:
```json
{
  "phaseId": "04-code-generation",
  "status": "in_progress|completed",
  "projectStructureEstablished": true,
  "workpackages": [
    {
      "workpackageId": "WP-001",
      "workpackageName": "Customer Management",
      "status": "completed|in_progress|not_started|failed",
      "tiersNeeded": ["backend", "frontend"],
      "tiersCompleted": ["backend", "frontend"],
      "backend": {
        "status": "completed|in_progress|not_started|failed",
        "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-001",
        "completedDate": "2026-02-16T10:30:00Z",
        "components": {
          "entities": 5,
          "repositories": 3,
          "services": 4,
          "controllers": 3
        }
      },
      "frontend": {
        "status": "completed|in_progress|not_started|failed",
        "outputLocation": "{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-001",
        "completedDate": "2026-02-16T11:45:00Z",
        "components": {
          "pages": 3,
          "components": 12,
          "services": 2
        }
      },
      "batch": null,
      "completedDate": "2026-02-16T11:45:00Z"
    }
  ],
  "completedCount": 1,
  "totalCount": 10,
  "lastUpdated": "2026-02-16T14:30:00Z"
}
```

**Markdown Structure**:
```markdown
# Code Generation Master Progress

## Overall Status
- Total Workpackages: 10
- Completed: 1
- In Progress: 1
- Not Started: 8
- Failed: 0
- Last Updated: 2026-02-16T14:30:00Z

## Workpackage Status

### WP-001: Customer Management
- Status: Completed
- Tiers Needed: Backend, Frontend
- Backend: ✓ Completed (2026-02-16T10:30:00Z)
- Frontend: ✓ Completed (2026-02-16T11:45:00Z)
- Batch: N/A

### WP-002: Order Processing
- Status: In Progress
- Tiers Needed: Backend, Batch
- Backend: ✓ Completed (2026-02-16T14:20:00Z)
- Frontend: N/A
- Batch: ⏳ In Progress
```

**Update Frequency**: After each tier completion or status change

### Resumption Logic

When resuming after interruption:
1. Read {{CODE_GENERATION_STATUS}}
2. Find first workpackage with status != "completed"
3. Check which tiers are completed for that workpackage
4. Resume from first incomplete tier
5. Continue workpackage loop from that point

---

## Quality Gates

### Phase 5.0 Quality Gate
**Criteria**:
- [ ] Backend technical specification created
- [ ] Frontend technical specification created
- [ ] Batch technical specification created
- [ ] Infrastructure technical specification created
- [ ] All specifications reviewed and approved
- [ ] Progress tracking shows completion
- [ ] All discoveries documented with traceability
- [ ] All assumptions documented

**Gate Decision**:
- **PASS**: Proceed to Phase 5.1
- **FAIL**: Rework Phase 5.0 or escalate

### Phase 5.1 Quality Gate
**Criteria**:
- [ ] Backend project structure created
- [ ] Frontend project structure created
- [ ] Batch project structure created
- [ ] Backend build configuration valid
- [ ] Frontend build configuration valid
- [ ] Configuration templates in place
- [ ] Progress tracking initialized

**Gate Decision**:
- **PASS**: Proceed to WORKPACKAGE_LOOP
- **FAIL**: Rework Phase 5.1 or escalate

### Phase 5.2 Quality Gate
**Criteria**:
- [ ] Backend code exists for workpackage
- [ ] Code compiles without errors
- [ ] All business entities implemented
- [ ] All business rules implemented
- [ ] Repository layer complete
- [ ] Service layer complete
- [ ] API layer complete
- [ ] Validation implemented
- [ ] Error handling implemented

**Gate Decision**:
- **PASS**: Proceed to Phase 5.3 (if needed) or Phase 5.4 (if needed) or WORKPACKAGE_COMPLETE
- **FAIL**: Rework Phase 5.2 or escalate

### Phase 5.3 Quality Gate
**Criteria**:
- [ ] Frontend code exists for workpackage
- [ ] Code compiles without errors
- [ ] All UI components implemented
- [ ] State management implemented
- [ ] API integration complete
- [ ] Routing configured
- [ ] Accessibility compliance verified
- [ ] Responsive design implemented

**Gate Decision**:
- **PASS**: Proceed to Phase 5.4 (if needed) or WORKPACKAGE_COMPLETE
- **FAIL**: Rework Phase 5.3 or escalate

### Phase 5.4 Quality Gate
**Criteria**:
- [ ] Batch code exists for workpackage
- [ ] Code compiles without errors
- [ ] All batch jobs configured
- [ ] Readers/processors/writers implemented
- [ ] Error handling implemented
- [ ] Restart capability implemented
- [ ] Scheduling configured

**Gate Decision**:
- **PASS**: Proceed to WORKPACKAGE_COMPLETE
- **FAIL**: Rework Phase 5.4 or escalate

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
Test Case Generation = {{TEST_CASE_GENERATION_BASE_PATH}}
Target Specification = {{TARGET_SPECIFICATION}}
Target Sample Code = {{TARGET_SAMPLE_CODE}}
```

### Output Paths
```
Code Generation = {{CODE_GENERATION_BASE_PATH}}
Code Generation Backend Output = {{CODE_GENERATION_BACKEND_OUTPUT}}
Code Generation Frontend Output = {{CODE_GENERATION_FRONTEND_OUTPUT}}
Code Generation Batch Output = {{CODE_GENERATION_BATCH_OUTPUT}}
Code Generation Status = {{CODE_GENERATION_STATUS}}
Code Generation Errors = {{CODE_GENERATION_ERRORS}}
Code Generation Master Progress = {{CODE_GENERATION_MASTER_PROGRESS}}
```

### Template Paths
```
Code Generation Status Template = {{CODE_GENERATION_STATUS_TEMPLATE}}
Code Generation Master Progress Template = {{CODE_GENERATION_MASTER_PROGRESS_TEMPLATE}}
```

---

## Supervisor Responsibilities

### Pre-Execution
1. Verify all prerequisites from Phase 3 exist
2. Verify all path variables are resolved to absolute paths
3. Verify all template files exist
4. Verify all agents are available and properly configured
5. Verify all phase task documents exist in {{PROMPTS_BASE_PATH}}
6. Verify target specifications exist
7. Verify sample code exists
8. Create output directories if they don't exist
9. Initialize master progress tracking

### During Execution
1. Assign appropriate agent for each phase
2. Provide phase task document from {{PROMPTS_BASE_PATH}}
3. Provide workpackage context for tier-specific phases
4. Monitor phase execution progress
5. Verify phase completion against quality gates
6. Handle errors and rework scenarios
7. Update master progress tracking
8. Escalate critical issues to human supervisor

### Post-Execution
1. Verify all workpackages completed successfully
2. Verify all code compiles
3. Generate final summary report
4. Archive all artifacts
5. Prepare handoff to Phase 5 (Integration Testing)

---

## Success Criteria

Phase 5 is considered complete when:
- [ ] Technical specifications extracted successfully (Phase 5.0)
- [ ] Project structure established successfully (Phase 5.1)
- [ ] All workpackages processed
- [ ] All required tiers implemented for each workpackage
- [ ] All code compiles successfully
- [ ] All business rules implemented and traceable
- [ ] Progress tracking shows 100% completion
- [ ] No critical blockers remain
- [ ] All artifacts ready for Phase 6 (Integration Testing)

---

## Notes for Supervisor

**Critical Success Factors**:
1. **Technical specifications first**: Phase 5.0 must complete before project structure
2. **Project structure second**: Phase 5.1 must complete before any code generation
3. **Workpackage-by-workpackage**: Complete all tiers for one workpackage before moving to next
4. **Specification references**: Always reference technical specifications from Phase 5.0
5. **Business rule traceability**: All business rules from specifications must be implemented
6. **Compilation verification**: Code must compile before marking tier complete

**Common Pitfalls to Avoid**:
1. Skipping Phase 5.0 and jumping to project structure (results in repeated discovery work)
2. Skipping Phase 5.1 and jumping to code generation (results in build failures)
3. Processing multiple workpackages in parallel (breaks dependency order)
4. Embedding implementation details in prompts (violates specification reference principle)
5. Marking tier complete without compilation verification (breaks quality gate)
6. Ignoring accessibility requirements in frontend (violates compliance)

**When to Escalate**:
1. Specification ambiguities preventing technical specification extraction
2. Specification ambiguities preventing implementation
3. Framework compatibility issues requiring architectural decisions
4. Missing business requirements not documented in specifications
5. Technical blockers requiring infrastructure changes
6. Repeated rework cycles (more than 2 iterations per workpackage/tier)

---

## End of Master Orchestration Document
