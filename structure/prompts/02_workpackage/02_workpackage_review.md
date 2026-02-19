# Phase 2.2: Workpackage Planning Review

---

## Orchestration Information

**Phase**: Phase 2 - Migration Wave Planning
**Step**: Step 2.2 - Workpackage Planning Review
**Team Supervisor**: planning_team_supervisor
**Assigned Agent**: planning_reviewer_workpackage
**Task File Name**: {{TASKS_BASE_PATH}}/workpackage_planning_review_task.md

### Expected Deliverables

1. **Workpackage Review Feedback Report**
   - File: {{WORKPACKAGE_REVIEW_FEEDBACK}}
   - Description: Comprehensive review findings with specific issues and recommendations

2. **Workpackage Phase Approval Document**
   - File: {{WORKPACKAGE_PHASE_APPROVAL}}
   - Description: Formal approval decision with quality assessment

3. **Remediation Tracking** (if issues found)
   - File: {{WORKPACKAGE_REMEDIATION_TRACKING}}
   - Description: Issue tracking and remediation progress

### Success Criteria
- [ ] All workpackage planning deliverables reviewed and validated
- [ ] All quality criteria assessed (completeness, accuracy, consistency)
- [ ] Priority calculations verified
- [ ] Dependency relationships validated (DAG structure)
- [ ] Phase assignments verified
- [ ] Approval decision documented with clear rationale
- [ ] If issues found: detailed feedback provided with remediation guidance
- [ ] If approved: confirmation that business specification phase can proceed
- [ ] Ready to proceed to Phase 3 (Business Specification)

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: The goal of reviewing and validating all workpackage planning outputs
- **Review scope**: All deliverables from Step 2.1
- **Review methodology**: Completeness, accuracy, consistency validation steps
- **Quality assessment categories**: Priority calculations, dependency validation, phase assignments
- **Approval/rejection workflow**: Decision criteria and feedback process
- **Remediation instructions**: How to handle issues and coordinate fixes

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (deliverables to review - resolved paths):
  - Migration roadmap: {{WORKPACKAGE_ROADMAP}}
  - Workpackage analyzer tool: {{WORKPACKAGE_ANALYZER_TOOL}}
  - Progress tracking: {{WORKPACKAGE_STATUS}}
- **All output locations** (resolved paths):
  - Review feedback: {{WORKPACKAGE_REVIEW_FEEDBACK}}
  - Phase approval: {{WORKPACKAGE_PHASE_APPROVAL}}
  - Remediation tracking: {{WORKPACKAGE_REMEDIATION_TRACKING}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Templates used by workpackage planning phase (for validation)

### 3. Reference agent definition:
- **Agent name**: planning_reviewer_workpackage
- **Agent definition file**: structure/agents/planning_team/planning_reviewer_workpackage.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations, output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-9), review methodology, approval workflow
- **Expected Deliverables**: All 3 deliverables with paths, descriptions, validation checklists
- **Quality Criteria**: Completeness, accuracy, consistency (from this prompt)
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

---

## For Team Supervisor: Dependencies Verification

Before creating the task file, verify that all Phase 2 Step 2.1 outputs are available:

**Required Workpackage Planning Deliverables:**
- [ ] Workpackage_Planning.json exists at {{WORKPACKAGE_PLANNING}}
- [ ] Migration_Roadmap.md exists at {{WORKPACKAGE_ROADMAP}}
- [ ] Workpackage analyzer tool exists at {{WORKPACKAGE_ANALYZER_TOOL}}
- [ ] Progress tracking exists at {{WORKPACKAGE_STATUS}}
- [ ] Step 2.1 (Workpackage Planning) completed

If any dependencies are missing, coordinate with planning_specialist_workpackage before proceeding.

---

## Context

### Project Information
**Project Name**: {{PROJECT_NAME}}
**Project Base Path**: {{PROJECT_BASE_PATH}}

### Deliverables to Review (from Step 2.1)

#### Workpackage Planning Deliverables
- **Workpackage Planning File**: {{WORKPACKAGE_PLANNING}}
  - Template: {{WORKPACKAGE_PLANNING_TEMPLATE}}
  - Description: Priority scores, workpackage assignments, phase groupings (references Business_Flows.json by flowId)
  
- **Migration Roadmap**: {{WORKPACKAGE_ROADMAP}}
  - Template: {{WORKPACKAGE_ROADMAP_TEMPLATE}}
  - Description: Comprehensive migration roadmap with phase-by-phase breakdown and dependency visualization
  
- **Workpackage Prioritization Tool**: {{WORKPACKAGE_ANALYZER_TOOL}}
  - Description: Python tool that performs workpackage prioritization and generates all required outputs
  
- **Progress Tracking**: {{WORKPACKAGE_STATUS}}
  - Template: {{ANALYSIS_STATUS_TEMPLATE}}
  - Description: Workpackage planning progress and status tracking

### Review Output Locations
- **Review Feedback Report**: {{WORKPACKAGE_REVIEW_FEEDBACK}}
  - Description: Comprehensive review findings with specific issues and recommendations
  
- **Phase Approval Document**: {{WORKPACKAGE_PHASE_APPROVAL}}
  - Description: Formal approval decision with quality assessment
  
- **Remediation Tracking**: {{WORKPACKAGE_REMEDIATION_TRACKING}}
  - Description: Issue tracking and remediation progress (if issues found)

### Dependencies from Phase 1
  - Description: Input data for workpackage prioritization
- **Module Classifications**: {{MODULE_CLASSIFICATIONS}}
  - Description: Used for calculating common module dependencies

---

## Objective

Perform comprehensive review and validation of all workpackage planning deliverables from Step 2.1 (Workpackage Definition). Ensure all outputs meet quality standards, priority calculations are correct, dependency relationships are valid, and phase assignments are appropriate. Make final approval decision for workpackage planning phase completion.

---

## Instructions

### Step 1: Deliverable Inventory and Initial Validation

**Actions:**
1. Verify all required deliverables from Step 2.1 are present
2. Check that all files exist at specified paths
3. Verify file sizes are reasonable (not empty or corrupted)
4. Validate file formats match expected types (JSON, Markdown, Python)
5. Create initial inventory checklist

**Deliverables Checklist:**
- [ ] Workpackage Dependencies File exists
- [ ] Migration Roadmap exists
- [ ] Workpackage Prioritization Tool exists
- [ ] Progress Tracking exists

**If any deliverables are missing:**
- Document missing items with specific file paths
- Report to planning_team_supervisor
- Request completion before proceeding with detailed review

### Step 2: Template and Format Compliance Validation

**Actions:**
1. Validate all outputs against their specified templates
2. Check JSON files validate against schemas
3. Verify Markdown files include all required sections
4. Ensure file naming conventions are followed
5. Validate Python tool structure and documentation

**Format Validation Checks:**

**For JSON Files** (Workpackage Planning, Progress Tracking):
- [ ] Valid JSON syntax (no parsing errors)
- [ ] All required fields present per Workpackage_Planning.json template
- [ ] All flowIds reference valid flows in Business_Flows.json
- [ ] Field types match schema specifications
- [ ] No empty required fields (unless specified)
- [ ] Consistent structure across all flow entries

**For Markdown Files** (Migration Roadmap):
- [ ] All required sections present (Executive Summary, Phase Breakdown, Dependency Visualization, Risk Assessment)
- [ ] Section order matches template
- [ ] Proper markdown formatting
- [ ] Complete content in all sections
- [ ] Professional documentation quality
- [ ] Clear and actionable recommendations

**For Python Files** (Workpackage Analyzer Tool):
- [ ] Valid Python syntax
- [ ] Proper code structure and organization
- [ ] Documentation and comments present
- [ ] Error handling implemented
- [ ] Usage instructions included
- [ ] Input/output paths configurable

### Step 3: Completeness Validation

**Workpackage Planning Completeness:**
- [ ] All flows from Phase 1 Business_Flows.json are assigned workpackages in Workpackage_Planning.json
- [ ] All flows have priority scores calculated
- [ ] All flows have workpackage IDs assigned
- [ ] All flows have phase assignments
- [ ] All flows have preExistentModules arrays (even if empty)
- [ ] All flows have dependency relationships documented
- [ ] Migration roadmap includes all workpackages
- [ ] Migration roadmap includes all phases
- [ ] Workpackage analyzer tool is complete and functional
- [ ] Progress tracking shows "Complete" status

**Data Integrity:**
- [ ] Business_Flows.json remains unchanged from Phase 1
- [ ] All flowIds in Workpackage_Planning.json reference valid flows in Business_Flows.json
- [ ] No data loss during planning process

### Step 4: Accuracy Validation

**Priority Score Calculation Accuracy:**

Verify priority scores are calculated correctly using the formula:
```
Priority = (TotalPrograms × 2) + (CommonModules × 3) + (CompositeScore × 0.5) + CompleteFlowBonus + SimpleFlowBonus
```

**Validation Steps:**
- [ ] Select 5-10 random flows and manually verify priority calculations
- [ ] Verify TotalPrograms matches complexity.totalPrograms from flow data
- [ ] Verify CommonModules count is correct (programs classified as COMMONLY_USED in Module_Classifications.json)
- [ ] Verify CompositeScore matches complexity.compositeScore from flow data
- [ ] Verify CompleteFlowBonus (-5 points) applied correctly for flows with database operations
- [ ] Verify SimpleFlowBonus applied correctly (-3 for ≤3 programs, -1 for ≤5 programs)
- [ ] Verify priority scores are consistent and logical (lower = higher priority)

**Workpackage ID Assignment Accuracy:**
- [ ] Workpackage IDs are sequential starting from 1
- [ ] Workpackage IDs are assigned in priority order (lowest priority score = ID 1)
- [ ] No duplicate workpackage IDs
- [ ] No gaps in workpackage ID sequence

**Pre-existent Modules Accuracy:**
- [ ] Pre-existent modules correctly identify programs already used in higher priority workpackages
- [ ] Pre-existent module lists are accurate for each workpackage
- [ ] Module reuse is properly tracked across workpackages

**Dependency Relationship Accuracy:**
- [ ] Dependency relationships are correctly identified
- [ ] Dependencies reference valid flow IDs
- [ ] Dependency direction is correct (which flow depends on which)
- [ ] All dependency relationships are documented

### Step 5: Consistency Validation

**Cross-Reference Validation:**
- [ ] Flow IDs in Workpackage_Planning.json match flows in Business_Flows.json
- [ ] Module names consistent with Module_Classifications.json
- [ ] Program references consistent across all outputs
- [ ] Business domain assignments preserved from Phase 1
- [ ] Complexity metrics preserved from Phase 1

**Workpackage Structure Consistency:**
- [ ] All workpackages follow same data structure
- [ ] All required fields present in every workpackage
- [ ] Field naming conventions consistent
- [ ] Data types consistent across all workpackages

**Migration Roadmap Consistency:**
- [ ] Roadmap phase numbers match workpackage phase assignments
- [ ] All workpackages in dependencies file are included in roadmap
- [ ] Workpackage counts match between dependencies file and roadmap
- [ ] Dependency descriptions in roadmap match dependency data

### Step 6: Dependency Validation (Critical)

**Directed Acyclic Graph (DAG) Validation:**
- [ ] Verify dependency relationships form a valid DAG (no circular dependencies)
- [ ] Check that no workpackage depends on itself (directly or indirectly)
- [ ] Validate that all dependency chains eventually terminate
- [ ] Confirm no cycles exist in the dependency graph

**Dependency Logic Validation:**
- [ ] Dependencies are based on module reuse (programs in one flow are entry points for another)
- [ ] Dependency direction is logical (dependent flow uses modules from prerequisite flow)
- [ ] All cross-flow module references are captured as dependencies
- [ ] No missing dependencies (all module reuse relationships documented)

**Phase Assignment Validation:**
- [ ] Phase 1 workpackages have no dependencies on other workpackages
- [ ] Phase N workpackages only depend on workpackages in phases 1 through N-1
- [ ] No workpackage depends on a workpackage in a later phase
- [ ] Phase assignments respect all dependency relationships

### Step 7: Migration Roadmap Quality Assessment

**Executive Summary Quality:**
- [ ] Clear overview of migration approach
- [ ] Total workpackage count accurate
- [ ] Total phase count accurate
- [ ] Migration strategy clearly articulated
- [ ] Risk mitigation approach explained

**Phase Breakdown Quality:**
- [ ] Each phase clearly defined with objectives
- [ ] All workpackages listed for each phase
- [ ] Workpackage priorities indicated
- [ ] Dependencies between phases explained
- [ ] Execution order recommendations provided

**Dependency Visualization Quality:**
- [ ] Dependency relationships clearly visualized (textual or diagram)
- [ ] Critical path identified
- [ ] Bottleneck workpackages highlighted
- [ ] Parallel execution opportunities identified

**Risk Assessment Quality:**
- [ ] Risks identified for each phase
- [ ] Risk severity assessed (High, Medium, Low)
- [ ] Mitigation strategies provided
- [ ] Contingency plans outlined

**Execution Recommendations Quality:**
- [ ] Clear recommendations for execution order within phases
- [ ] Resource allocation guidance provided
- [ ] Timeline estimates reasonable
- [ ] Success criteria defined for each phase

### Step 8: Tool Verification (Optional but Recommended)

**If time and resources permit:**
1. Execute workpackage analyzer tool with Phase 1 outputs
2. Verify tool produces expected outputs (Workpackage_Planning.json, Migration_Roadmap.md)
3. Check error handling and logging functionality
4. Verify tool handles edge cases (missing data, invalid inputs)
5. Confirm tool documentation is clear and complete

### Step 9: Approval Decision and Documentation

**Decision Criteria:**

**APPROVE if:**
- [ ] All deliverables present and complete
- [ ] All quality criteria met (completeness, accuracy, consistency)
- [ ] All templates and formats compliant
- [ ] Priority calculations verified and correct
- [ ] Dependency relationships validated (valid DAG)
- [ ] Phase assignments appropriate and logical
- [ ] Migration roadmap comprehensive and actionable
- [ ] Tool functional and well-documented
- [ ] No blocking issues identified
- [ ] Ready for business specification phase

**REQUIRE REVISION if:**
- [ ] Missing deliverables
- [ ] Quality criteria not met
- [ ] Template violations
- [ ] Priority calculation errors
- [ ] Invalid dependency relationships (circular dependencies)
- [ ] Incorrect phase assignments
- [ ] Migration roadmap incomplete or unclear
- [ ] Tool non-functional or poorly documented
- [ ] Blocking issues identified

**Document Decision:**
Create formal approval document at {{WORKPACKAGE_PHASE_APPROVAL}} with:
- Approval status (APPROVED / REQUIRES_REVISION)
- Review date and reviewer identification
- List of all validated deliverables with paths
- Quality assessment summary
- Priority calculation verification results
- Dependency validation results
- Next phase readiness confirmation
- Any notes or observations

### Step 10: Feedback Generation (if issues found)

**If REQUIRES_REVISION:**

1. **Create Detailed Feedback Report** at {{WORKPACKAGE_REVIEW_FEEDBACK}}:
   - Review summary with overall status
   - Specific issues identified with file paths and details
   - Recommended remediation actions for each issue
   - Priority classification (Critical, High, Medium, Low)
   - Quality assessment breakdown
   - Specific examples of calculation errors or dependency issues

2. **Create Remediation Tracking** at {{WORKPACKAGE_REMEDIATION_TRACKING}}:
   - List of all issues requiring remediation
   - Assigned to (planning_specialist_workpackage)
   - Status tracking (Open, In Progress, Resolved)
   - Resolution verification checklist

3. **Communicate with Planning Team Supervisor**:
   - Provide clear, actionable feedback
   - Specify which deliverables need revision
   - Indicate expected timeline for remediation
   - Offer to answer questions or provide clarification

### Step 11: Remediation Cycle Management (if applicable)

**If issues were found and remediation is in progress:**

1. **Monitor Remediation Progress**:
   - Track issue resolution status
   - Verify updated deliverables are submitted
   - Check that all feedback has been addressed

2. **Re-Review Updated Deliverables**:
   - Validate all issues have been properly resolved
   - Ensure no new issues were introduced
   - Confirm quality criteria are now met
   - Re-verify priority calculations if changed
   - Re-validate dependency relationships if modified

3. **Final Approval**:
   - Once all issues resolved, update approval document
   - Change status to APPROVED
   - Confirm readiness for Phase 3

---

## Output Format

### Primary Outputs

#### 1. Workpackage Review Feedback Report
**File**: {{WORKPACKAGE_REVIEW_FEEDBACK}}

**Required Sections:**
```markdown
# Workpackage Planning Review Feedback

## Review Summary
- Review Date: [Date]
- Reviewer: planning_reviewer_workpackage
- Overall Status: [APPROVED / REQUIRES_REVISION]

## Workpackage Planning Review
### Deliverables Reviewed
- Workpackage Dependencies: [path]
- Migration Roadmap: [path]
- Workpackage Analyzer Tool: [path]
- Progress Tracking: [path]

### Issues Identified
#### Priority Calculation Issues
- [Specific issue with flow ID and calculation details]
- [Recommended remediation action]
- [Priority: Critical/High/Medium/Low]

#### Dependency Relationship Issues
- [Specific issue with flow IDs and dependency details]
- [Recommended remediation action]
- [Priority: Critical/High/Medium/Low]

#### Phase Assignment Issues
- [Specific issue with workpackage ID and phase assignment]
- [Recommended remediation action]
- [Priority: Critical/High/Medium/Low]

#### Migration Roadmap Issues
- [Specific issue with section and details]
- [Recommended remediation action]
- [Priority: Critical/High/Medium/Low]

### Quality Assessment
- Completeness: [PASS / FAIL - with details]
- Accuracy: [PASS / FAIL - with details]
- Consistency: [PASS / FAIL - with details]
- Dependency Validation: [PASS / FAIL - with details]

## Priority Calculation Verification
### Sample Verifications
- Flow ID: [ID] - Priority Score: [calculated] - Verified: [PASS/FAIL]
- [Details of verification for 5-10 sample flows]

## Dependency Validation Results
### DAG Validation
- Circular Dependencies Detected: [YES/NO]
- [Details of any circular dependencies found]

### Phase Assignment Validation
- Phase 1 Dependencies: [VALID/INVALID]
- Phase N Dependencies: [VALID/INVALID]
- [Details of any phase assignment issues]

## Approval Decision
- [Detailed rationale for approval or revision requirements]
- [Next steps]
```

#### 2. Workpackage Phase Approval Document
**File**: {{WORKPACKAGE_PHASE_APPROVAL}}

**Required Format (JSON):**
```json
{
  "approval_status": "APPROVED",
  "approval_date": "YYYY-MM-DD",
  "reviewer": "planning_reviewer_workpackage",
  "deliverables_validated": [
    "absolute path to Workpackage_Planning.json",
    "absolute path to Migration_Roadmap.md",
    "absolute path to workpackage analyzer tool",
    "absolute path to progress tracking"
  ],
  "quality_assessment": {
    "completeness": "PASS",
    "accuracy": "PASS",
    "consistency": "PASS",
    "dependency_validation": "PASS"
  },
  "priority_calculation_verification": {
    "samples_verified": 10,
    "samples_passed": 10,
    "verification_status": "PASS"
  },
  "dependency_validation": {
    "dag_valid": true,
    "circular_dependencies": false,
    "phase_assignments_valid": true
  },
  "next_phase_readiness": "CONFIRMED",
  "notes": "Any additional comments or observations"
}
```

#### 3. Remediation Tracking (if issues found)
**File**: {{WORKPACKAGE_REMEDIATION_TRACKING}}

**Required Format (JSON):**
```json
{
  "remediation_cycle": 1,
  "issues": [
    {
      "issue_id": "ISSUE-001",
      "description": "Specific issue description",
      "file_path": "absolute path to file",
      "flow_id": "Flow ID if applicable",
      "priority": "Critical",
      "assigned_to": "planning_specialist_workpackage",
      "status": "Open",
      "remediation_action": "Specific action required",
      "resolution_notes": ""
    }
  ],
  "overall_status": "In Progress",
  "next_review_date": "YYYY-MM-DD"
}
```

---

## Quality Criteria

### Review Process Quality
- [ ] All deliverables inventoried and checked
- [ ] All validation steps completed systematically
- [ ] Priority calculations verified with sample checks
- [ ] Dependency relationships validated thoroughly
- [ ] All issues documented with specific details
- [ ] All feedback is actionable and clear
- [ ] Approval decision is well-documented with rationale

### Feedback Quality (if issues found)
- [ ] Issues include specific flow IDs, workpackage IDs, or file paths
- [ ] Priority calculation errors include expected vs. actual values
- [ ] Dependency issues include specific flow relationships
- [ ] Remediation actions are clear and actionable
- [ ] Priority levels are appropriate
- [ ] Feedback is constructive and professional
- [ ] Timeline expectations are reasonable

### Approval Documentation Quality
- [ ] Approval status is clear and unambiguous
- [ ] All validated deliverables are listed with paths
- [ ] Quality assessment is comprehensive
- [ ] Priority calculation verification documented
- [ ] Dependency validation results documented
- [ ] Next phase readiness is confirmed
- [ ] Documentation is professional and complete

---

## Error Handling

### Common Review Scenarios

#### 1. **Missing Deliverables**
- **Detection**: Required files not found at specified paths
- **Recovery**: Document missing items, report to supervisor, request completion
- **Escalation**: If deliverables remain missing after 2 requests, escalate to Migration Supervisor

#### 2. **Template Violations**
- **Detection**: Outputs don't match specified templates
- **Recovery**: Document specific violations, provide template reference, request correction
- **Escalation**: If violations persist after 2 remediation cycles, escalate to supervisor

#### 3. **Priority Calculation Errors**
- **Detection**: Manual verification reveals incorrect priority scores
- **Recovery**: Document specific calculation errors with expected vs. actual values, request recalculation
- **Escalation**: If calculation errors persist after 2 cycles, escalate with recommendation

#### 4. **Circular Dependencies Detected**
- **Detection**: DAG validation reveals circular dependency relationships
- **Recovery**: Document circular dependency chains, request dependency restructuring
- **Escalation**: Critical issue - escalate immediately if circular dependencies cannot be resolved

#### 5. **Invalid Phase Assignments**
- **Detection**: Workpackages depend on workpackages in later phases
- **Recovery**: Document invalid phase assignments, request phase reassignment
- **Escalation**: If phase assignment issues persist after 2 cycles, escalate to supervisor

#### 6. **Data Integrity Issues**
- **Detection**: Business_Flows.json modified or flowIds in Workpackage_Planning.json don't match Business_Flows.json
- **Recovery**: Document data integrity issue, verify Business_Flows.json unchanged, validate all flowId references
- **Escalation**: Critical issue - escalate immediately if data integrity cannot be ensured

#### 7. **Tool Failures**
- **Detection**: Workpackage analyzer tool fails to execute or produces unreliable results
- **Recovery**: Document tool issues, request debugging and fixes
- **Escalation**: If tool remains non-functional after 2 attempts, escalate as blocking issue

### Escalation Triggers
- Workpackage planning deliverables fail review more than 2 times
- Circular dependencies detected that cannot be resolved
- Critical priority calculation errors affecting migration strategy
- Data loss or corruption in transformation process
- Tool failures preventing automated workpackage generation
- Timeline constraints threaten overall migration schedule

---

## Success Validation

**Review is complete when:**
- [ ] All deliverables inventoried and validated
- [ ] All quality criteria assessed
- [ ] Priority calculations verified
- [ ] Dependency relationships validated (DAG confirmed)
- [ ] Phase assignments verified
- [ ] Approval decision documented
- [ ] If APPROVED: Phase approval document created, ready for Phase 3
- [ ] If REQUIRES_REVISION: Feedback report created, remediation tracking established
- [ ] Planning Team Supervisor notified of review completion
- [ ] All review outputs exist at specified paths

**Verification Steps:**
1. Check all review output files exist at specified locations
2. Validate approval document format and content
3. If issues found: verify feedback report is comprehensive and actionable
4. Confirm decision rationale is clear and well-documented
5. Verify priority calculation verification results are documented
6. Verify dependency validation results are documented
7. Report review completion to planning_team_supervisor

---

## Notes

### Agent Definition Reference
Complete role definition and capabilities are in:
- structure/agents/planning_team/planning_reviewer_workpackage.md

This prompt provides project-specific context and review instructions.

### Critical Validation Areas
- **Priority Calculations**: These drive the entire migration sequence - accuracy is critical
- **Dependency Relationships**: Invalid dependencies (especially circular) can block migration
- **Phase Assignments**: Incorrect phase assignments can lead to migration failures

### Escalation
If you encounter issues beyond your capability:
1. Document the issue clearly with specific details
2. Report to planning_team_supervisor
3. Provide context, attempted solutions, and recommendations

### Quality Gate Importance
Your approval is the quality gate that ensures the migration project proceeds with a valid, executable migration plan. Maintain high standards while providing constructive feedback that enables the planning team to deliver excellent results. The business specification phase (Phase 3) depends on accurate workpackage definitions.
