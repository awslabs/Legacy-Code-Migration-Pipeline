# Orchestration Architecture Documentation

## Document Control
- **Version:** 1.0
- **Date:** 2024-01-15
- **Status:** Final
- **Purpose:** Comprehensive guide to the 3-layer orchestration architecture

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Layers](#2-architecture-layers)
3. [Information Flow](#3-information-flow)
4. [Delegation Protocol](#4-delegation-protocol)
5. [Review Orchestration](#5-review-orchestration)
6. [Task File Creation](#6-task-file-creation)
7. [End-to-End Example](#7-end-to-end-example)
8. [Troubleshooting Guide](#8-troubleshooting-guide)
9. [Best Practices](#9-best-practices)
10. [FAQ](#10-faq)

---

## 1. Overview

### 1.1 Purpose

The orchestration architecture enables a hierarchical, supervisor-based approach to legacy system migration. It separates concerns between:
- **Orchestration** (supervisors coordinate work)
- **Execution** (specialists perform technical work)
- **Validation** (reviewers ensure quality)

### 1.2 Key Principles

1. **Separation of Concerns**: Agents are generic; prompts are project-specific; task files are runtime-specific
2. **No Duplication**: Reference definitions rather than duplicating them
3. **Complete Context**: Each level has all information needed for its responsibilities
4. **Clear Delegation**: Explicit instructions on who does what and when
5. **Path Resolution**: All paths fully resolved before delegation
6. **Iterative Quality**: Review is built into each phase, not a separate step

### 1.3 Benefits

- **Scalability**: Add new phases or agents without restructuring
- **Reusability**: Generic agents work across different projects
- **Maintainability**: Clear separation makes updates easier
- **Quality**: Built-in review loops ensure deliverable quality
- **Flexibility**: Supervisors can adapt workflows based on feedback


---

## 2. Architecture Layers

### 2.1 The 3-Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: Migration Supervisor             │
│  Role: Top-level orchestrator                                │
│  Input: Main Migration Prompt (all phases)                   │
│  Output: Delegates phases to team supervisors                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Layer 2: Team Supervisors                 │
│  Role: Phase-level orchestrators                             │
│  Input: Phase Prompts (phase-specific instructions)          │
│  Output: Creates task files, delegates to specialists        │
│  Examples: analysis_team_supervisor,                         │
│            planning_team_supervisor,                         │
│            business_team_supervisor                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Layer 3: Specialist & Reviewer Agents           │
│  Role: Execute technical work and validate deliverables      │
│  Input: Task Files (agent-specific instructions + paths)     │
│  Output: Deliverables (reports, code, specifications)        │
│  Examples: analysis_specialist_legacy_code,                  │
│            analysis_reviewer_database,                       │
│            business_specialist_logic_extraction              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer 1: Migration Supervisor

**Responsibilities:**
- Receives the main migration prompt with all phases
- Understands phase dependencies and execution order
- Delegates entire phases to appropriate team supervisors
- Monitors phase completion and deliverable production
- Verifies phase outputs before proceeding to next phase
- Handles cross-phase coordination and escalations

**Critical Rules:**
- NEVER performs technical work directly
- ALWAYS delegates to team supervisors
- ALWAYS verifies deliverables before proceeding
- MAINTAINS phase sequence and dependencies

**Input:** `ReImagine_Main_Prompt.md` with:
- Project context (all paths)
- All phases with delegation instructions
- Expected deliverables for each phase
- Success criteria

**Output:**
- Phase delegation to team supervisors
- Progress monitoring
- Phase completion verification


### 2.3 Layer 2: Team Supervisors

**Responsibilities:**
- Receives phase prompts from Migration Supervisor
- Creates task files for specialist and reviewer agents
- Delegates tasks to appropriate team members
- Orchestrates iterative review within the phase
- Coordinates remediation when issues are found
- Reports phase completion only after review approval

**Critical Rules:**
- NEVER performs technical work directly
- ALWAYS creates task files before delegating
- ALWAYS orchestrates review iteratively (not as separate step)
- RESOLVES all paths before creating task files
- TRACKS iterations and escalates if excessive

**Input:** Phase-specific prompt files (e.g., `01_analysis.md`) with:
- Phase context and objectives
- Detailed instructions
- Team structure and agent assignments
- Expected deliverables with paths
- Quality criteria
- Task file creation protocol

**Output:**
- Task files for specialists and reviewers
- Task delegation to team members
- Iteration management (specialist → reviewer → remediation → repeat)
- Phase completion report to Migration Supervisor

**Examples:**
- `analysis_team_supervisor` - Coordinates legacy system analysis
- `planning_team_supervisor` - Coordinates workpackage planning
- `business_team_supervisor` - Coordinates business logic extraction

### 2.4 Layer 3: Specialist & Reviewer Agents

**Specialist Agents:**

**Responsibilities:**
- Receives task files from team supervisors
- Executes technical work according to instructions
- Produces deliverables at specified paths
- Reports completion to team supervisor
- Remediates issues when reviewer finds problems

**Critical Rules:**
- FOLLOWS task file instructions exactly
- PRODUCES deliverables at specified paths
- USES provided templates
- REPORTS issues to supervisor if blocked

**Input:** Task files with:
- Agent assignment information
- Project context (all resolved paths)
- Specific instructions for this task
- Expected deliverables with templates
- Quality and success criteria

**Output:**
- Deliverables (reports, code, specifications)
- Completion notification to supervisor

**Examples:**
- `analysis_specialist_legacy_code` - Analyzes COBOL source code
- `analysis_specialist_database` - Analyzes database schemas
- `business_specialist_logic_extraction` - Extracts business logic

**Reviewer Agents:**

**Responsibilities:**
- Receives review task files from team supervisors
- Validates deliverables against quality criteria
- Provides detailed feedback on issues found
- Approves deliverables when quality criteria met

**Critical Rules:**
- REVIEWS all specified deliverables
- APPLIES quality criteria systematically
- PROVIDES specific, actionable feedback
- CLEARLY states outcome (approved or issues found)

**Input:** Review task files with:
- Deliverables to review (with paths)
- Quality criteria from phase prompt
- Review methodology
- Outcome options

**Output:**
- Review outcome (approved or issues found)
- Detailed feedback if issues found
- Approval notification if quality criteria met

**Examples:**
- `analysis_reviewer_legacy_code` - Reviews source code analysis
- `analysis_reviewer_database` - Reviews database analysis
- `business_reviewer_logic_extraction` - Reviews business specifications


---

## 3. Information Flow

### 3.1 Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  Main Migration Prompt (ReImagine_Main_Prompt.md)            │
│  - All phases with delegation instructions                   │
│  - All paths resolved ({{PARAMETERS}} filled)                │
│  - Expected deliverables for each phase                      │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Given to
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Migration Supervisor                                         │
│  - Reads all phases                                           │
│  - Understands dependencies                                   │
│  - Delegates Phase 1 to analysis_team_supervisor              │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Provides phase prompt
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Phase Prompt (e.g., 01_analysis.md)                         │
│  - Phase context and objectives                              │
│  - Detailed instructions                                      │
│  - Team structure                                             │
│  - Expected deliverables with paths                          │
│  - Task file creation protocol                               │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Given to
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Team Supervisor (e.g., analysis_team_supervisor)            │
│  - Reads phase prompt                                         │
│  - Extracts instructions for Step 1                          │
│  - Resolves all paths                                         │
│  - Creates task file for specialist                          │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Creates
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Task File (analysis_sourcecode_specialist_task.md)          │
│  - Agent assignment                                           │
│  - Project context (resolved paths)                          │
│  - Specific instructions                                      │
│  - Expected deliverables                                      │
│  - Quality criteria                                           │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Given to
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Specialist Agent (analysis_specialist_legacy_code)          │
│  - Reads task file                                            │
│  - Executes work                                              │
│  - Produces deliverables                                      │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Produces
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Deliverables                                                 │
│  - Source Code Analysis Report                               │
│  - Dependency Analysis Table                                 │
│  - Business Flows                                             │
│  - Module Classifications                                     │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Team Supervisor creates review task
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Review Task File (analysis_sourcecode_review_task.md)       │
│  - Deliverables to review                                     │
│  - Quality criteria                                           │
│  - Review methodology                                         │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Given to
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Reviewer Agent (analysis_reviewer_legacy_code)              │
│  - Reviews deliverables                                       │
│  - Validates against quality criteria                        │
│  - Provides outcome (approved or issues)                     │
└──────────────────────────────────────────────────────────────┘
                         │
                         ├─ If APPROVED ──────────────────────┐
                         │                                     │
                         │                                     ▼
                         │                    Team Supervisor reports
                         │                    completion to Migration
                         │                    Supervisor
                         │
                         └─ If ISSUES FOUND ──────────────────┐
                                                               │
                                                               ▼
                                          Team Supervisor creates
                                          remediation task, delegates
                                          back to specialist
                                          (iterate until approved)
```

### 3.2 Information at Each Level

**Level 1 (Main Prompt):**
- Complete project context
- All phases and their dependencies
- All input/output base paths
- Expected deliverables across all phases
- Team supervisor assignments

**Level 2 (Phase Prompt):**
- Phase-specific context
- Detailed instructions for the phase
- Team structure and agent roles
- Phase-specific input/output paths
- Task file creation protocol
- Quality criteria for the phase

**Level 3 (Task File):**
- Agent-specific assignment
- Task-specific context
- Extracted instructions relevant to this agent
- Fully resolved paths for this task
- Expected deliverables for this task
- Quality and success criteria for this task


---

## 4. Delegation Protocol

### 4.1 Migration Supervisor Delegation

**When to Delegate:**
- After reading and understanding the main prompt
- When all dependencies for a phase are satisfied
- When previous phase deliverables are verified

**How to Delegate:**

1. **Identify the phase** to execute (e.g., Phase 1: Analysis)
2. **Identify the team supervisor** for that phase (e.g., analysis_team_supervisor)
3. **Locate the phase prompt file** (e.g., `prompts/01_analysis/01_analysis.md`)
4. **Verify dependencies** are satisfied (inputs from previous phases exist)
5. **Provide the phase prompt** to the team supervisor
6. **Wait for completion** notification from team supervisor
7. **Verify deliverables** exist at expected paths
8. **Proceed to next phase** or handle issues

**Example Delegation:**
```
TO: analysis_team_supervisor
PHASE: Phase 1 - Legacy System Analysis
PROMPT: /project/prompts/01_analysis/Database/01_analysis.md
CONTEXT: All input files are available in /project/input/legacy/
EXPECTED: Database analysis report, DDL scripts, migration scripts
```

### 4.2 Team Supervisor Delegation

**When to Delegate:**
- After reading and understanding the phase prompt
- After creating a task file for a specialist or reviewer
- When ready to execute a step in the phase

**How to Delegate to Specialist:**

1. **Read the phase prompt** to understand the step
2. **Extract relevant instructions** for this step
3. **Resolve all paths** for inputs and outputs
4. **Create task file** following the template
5. **Save task file** in {{TASKS_BASE_PATH}}
6. **Identify the specialist agent** (from phase prompt)
7. **Provide the task file path** to the specialist
8. **Wait for completion** notification
9. **Verify deliverables** exist at expected paths
10. **Create review task file** for reviewer

**How to Delegate to Reviewer:**

1. **After specialist completes**, create review task file
2. **List all deliverables** to review with paths
3. **Include quality criteria** from phase prompt
4. **Provide review methodology**
5. **Save review task file** in {{TASKS_BASE_PATH}}
6. **Provide the review task file path** to reviewer
7. **Wait for review outcome**
8. **Handle outcome** (approved or issues found)

**Example Delegation to Specialist:**
```
TO: analysis_specialist_legacy_code
TASK: Source Code Analysis
TASK_FILE: /project/tasks/analysis_sourcecode_specialist_task.md
CONTEXT: Legacy COBOL code in /project/input/legacy/source
EXPECTED: Analysis report, dependency table, business flows
```

**Example Delegation to Reviewer:**
```
TO: analysis_reviewer_legacy_code
TASK: Review Source Code Analysis
TASK_FILE: /project/tasks/analysis_sourcecode_review_task.md
DELIVERABLES: 
  - /project/output/analysis/source_code/reports/cobol_analysis.md
  - /project/output/analysis/source_code/reports/dependency_table.csv
EXPECTED: Approval or detailed feedback on issues
```

### 4.3 Specialist/Reviewer Execution

**Specialist Execution:**

1. **Receive task file path** from team supervisor
2. **Read task file** completely
3. **Understand objective** and instructions
4. **Locate input files** at specified paths
5. **Execute work** according to instructions
6. **Produce deliverables** at specified paths
7. **Use templates** if provided
8. **Verify quality criteria** are met
9. **Report completion** to team supervisor

**Reviewer Execution:**

1. **Receive review task file path** from team supervisor
2. **Read review task file** completely
3. **Locate deliverables** to review at specified paths
4. **Apply quality criteria** systematically
5. **Document findings** (issues or approval)
6. **Provide specific feedback** if issues found
7. **Report outcome** to team supervisor (approved or issues)

### 4.4 Delegation Best Practices

**DO:**
- Always provide complete context
- Always resolve paths before delegating
- Always specify expected deliverables
- Always verify completion before proceeding
- Always maintain clear communication

**DON'T:**
- Don't delegate without verifying dependencies
- Don't assume agents have information not provided
- Don't skip verification steps
- Don't proceed with errors unresolved
- Don't duplicate information across levels


---

## 5. Review Orchestration

### 5.1 Iterative Quality Assurance Model

**Key Principle:** Review is NOT a separate sequential step. It is an iterative quality loop orchestrated by the team supervisor within each phase.

**Traditional Waterfall Approach (WRONG):**
```
Step 1: Specialist creates deliverables
Step 2: Specialist completes
Step 3: Reviewer reviews deliverables (separate step)
Step 4: Phase complete
```

**Iterative Orchestration Approach (CORRECT):**
```
Team Supervisor orchestrates:
  1. Delegate to Specialist → Specialist produces deliverables
  2. Delegate to Reviewer → Reviewer validates deliverables
  3. IF issues found:
     - Reviewer provides detailed feedback
     - Supervisor creates remediation task for specialist
     - Specialist fixes issues
     - GOTO step 2 (iterate)
  4. IF approved:
     - Supervisor reports phase completion
```

### 5.2 Review Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Team Supervisor creates specialist task                     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Specialist executes work, produces deliverables             │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Team Supervisor creates review task                         │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Reviewer validates deliverables against quality criteria    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ├─────────────────┬─────────────────┐
                         │                 │                 │
                    APPROVED          ISSUES FOUND      BLOCKED
                         │                 │                 │
                         ▼                 ▼                 ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │ Supervisor   │  │ Supervisor   │  │ Escalate to  │
              │ reports      │  │ creates      │  │ Migration    │
              │ completion   │  │ remediation  │  │ Supervisor   │
              │              │  │ task         │  │              │
              └──────────────┘  └──────────────┘  └──────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ Specialist fixes │
                              │ issues           │
                              └──────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ Supervisor       │
                              │ delegates to     │
                              │ reviewer again   │
                              │ (iterate)        │
                              └──────────────────┘
```

### 5.3 Team Supervisor Review Responsibilities

**1. Create Review Task File**

After specialist completes work:
- Extract quality criteria from phase prompt
- List all deliverables to review with paths
- Provide review methodology
- Define outcome options (approved or issues)
- Save review task file

**2. Delegate to Reviewer**

- Provide review task file path to reviewer
- Wait for review completion
- Receive review outcome

**3. Handle Review Outcome**

**If APPROVED:**
- Document approval
- Update phase status
- Report completion to Migration Supervisor
- Provide deliverable paths

**If ISSUES FOUND:**
- Collect detailed feedback from reviewer
- Create remediation task file for specialist
- Include specific issues and guidance
- Delegate back to specialist
- Wait for remediation completion
- Create new review task (iteration N+1)
- Delegate to reviewer again
- Repeat until approved

**If BLOCKED:**
- Document blocking issue
- Escalate to Migration Supervisor
- Provide context and attempted solutions
- Request guidance or resources

**4. Track Iterations**

- Maintain count of specialist → reviewer cycles
- Escalate if excessive (>3 iterations)
- Document all iterations for audit trail

### 5.4 Review Task File Structure

```markdown
# Task: Review [Phase] Deliverables (Iteration N)

## Agent Assignment
**Agent**: [reviewer_agent_name]
**Task ID**: [phase]_review_iteration_N
**Created By**: [team_supervisor_name]
**Iteration**: N

## Deliverables to Review

1. **[Deliverable Name]**
   - Path: [full_path]
   - Template: [template_path]
   - Expected Content: [description]

2. **[Deliverable Name]**
   - Path: [full_path]
   - Template: [template_path]
   - Expected Content: [description]

## Quality Criteria

### Completeness
- [ ] All required sections present
- [ ] All required fields populated
- [ ] No missing data or placeholders

### Accuracy
- [ ] Data correctly extracted/transformed
- [ ] Calculations correct
- [ ] References valid

### Consistency
- [ ] Naming conventions followed
- [ ] Format matches templates
- [ ] Terminology consistent

## Review Methodology

1. Verify each deliverable exists at specified path
2. Check file format matches template
3. Validate content against quality criteria
4. Document any issues found
5. Provide clear outcome

## Review Outcome Options

### Option 1: APPROVED
All quality criteria met, no blocking issues, ready to proceed.

### Option 2: ISSUES FOUND
List specific issues with:
- Issue description
- Affected deliverable
- Severity (blocking, major, minor)
- Remediation guidance
- Quality criterion violated

### Option 3: BLOCKED
Unable to complete review due to:
- Missing dependencies
- Unclear requirements
- Technical limitations
```

### 5.5 Remediation Task File Structure

```markdown
# Task: Remediate [Phase] Issues (Iteration N)

## Agent Assignment
**Agent**: [specialist_agent_name]
**Task ID**: [phase]_remediation_iteration_N
**Created By**: [team_supervisor_name]
**Original Task**: [original_task_file]
**Review Feedback**: [review_task_file]

## Issues to Address

### Issue 1: [Issue Description]
- **Affected Deliverable**: [path]
- **Severity**: [blocking/major/minor]
- **Quality Criterion Violated**: [criterion]
- **Remediation Guidance**: [specific guidance]

### Issue 2: [Issue Description]
[Similar structure...]

## Original Deliverables
[Paths to deliverables that need fixes]

## Instructions

1. Review feedback from reviewer in [review_task_file]
2. Address each issue systematically
3. Update affected deliverables
4. Verify fixes against quality criteria
5. Report completion to supervisor

## Success Criteria
- [ ] All issues addressed
- [ ] Deliverables updated at original paths
- [ ] Quality criteria now met
- [ ] Ready for re-review
```

### 5.6 Escalation Protocol

**When to Escalate:**

1. **Excessive Iterations** (>3 cycles)
   - Indicates fundamental issue with requirements or capabilities
   - Team supervisor escalates to Migration Supervisor

2. **Conflicting Requirements**
   - Reviewer and specialist disagree on interpretation
   - Requires clarification from higher level

3. **Missing Information**
   - Phase prompt lacks necessary information
   - Dependencies from previous phases incomplete

4. **Resource Constraints**
   - Agent capabilities insufficient for requirements
   - Technical limitations encountered

**Escalation Message Format:**
```
TO: Migration Supervisor
FROM: [Team Supervisor Name]
PHASE: [Phase Name]
ITERATION: [Current iteration count]
ISSUE: [Brief description]
CONTEXT: [What was attempted, feedback received]
REQUEST: [What is needed to proceed]
DELIVERABLES: [Current state of deliverables]
```

### 5.7 Benefits of Iterative Review

1. **Quality Assurance Built-In**: No deliverable proceeds without validation
2. **Supervisor-Driven**: Team supervisor maintains control and can adapt
3. **No Sequential Bottleneck**: Review happens immediately after specialist completes
4. **Continuous Improvement**: Specialist learns from reviewer feedback
5. **Clear Accountability**: Team supervisor responsible for phase quality
6. **Audit Trail**: All iterations documented for traceability


---

## 6. Task File Creation

### 6.1 Team Supervisor Responsibilities

When creating a task file, the Team Supervisor MUST:

1. **Read the phase prompt** for the specific step
2. **Identify the target agent** (specialist or reviewer)
3. **Extract relevant instructions** from the phase prompt
4. **Resolve all paths** specific to this task
5. **Create the task file** following the template
6. **Save the task file** in {{TASKS_BASE_PATH}}
7. **Provide the task file path** when delegating

### 6.2 Information Extraction Guide

**From Phase Prompt, Extract:**
- Objective for this step
- Detailed instructions for this step
- Input locations and descriptions
- Output locations and templates
- Quality criteria relevant to this task
- Success criteria for this task
- Error handling guidance

**From Agent Definition, Reference:**
- Agent name
- Agent capabilities (reference, don't duplicate)
- Agent role description (reference, don't duplicate)

**From Project Context, Include:**
- Project name and base path
- All resolved paths for inputs/outputs
- Templates locations
- Reference data locations

### 6.3 Path Resolution Rules

**All paths in task files MUST be:**
- Absolute paths (full path from root)
- Verified to exist (for inputs) or creatable (for outputs)
- Consistent with paths.cfg definitions
- Resolved from {{PARAMETERS}} in phase prompt

**Example:**
- Phase Prompt: `{{COBOL_SOURCE_ANALYSIS_REPORT}}`
- Task File: `/absolute/path/to/project/output/analysis/source_code/reports/cobol_analysis_report.md`

### 6.4 Task File Naming Convention

**Format:** `[phase]_[step]_[agent-role]_task.md`

**Components:**
- `[phase]`: Phase identifier (e.g., "analysis", "workpackage", "business")
- `[step]`: Step identifier (e.g., "sourcecode", "database", "review")
- `[agent-role]`: Agent role (e.g., "specialist", "reviewer")

**Examples:**
- `analysis_sourcecode_specialist_task.md`
- `analysis_sourcecode_review_task.md`
- `analysis_database_specialist_task.md`
- `workpackage_planning_specialist_task.md`
- `business_extraction_specialist_task.md`

### 6.5 Task File Template

```markdown
# Task: [Task Name]

## Agent Assignment
**Agent**: [agent_name]
**Agent Definition**: [path to agent definition file]
**Task ID**: [unique_id]
**Created By**: [supervisor_agent_name]
**Created At**: [timestamp]
**Phase**: [phase_name]
**Step**: [step_name]

---

## Project Context

### Project Information
**Project Name**: [project_name]
**Project Base Path**: [base_path]

### Input Locations
- Input 1: [full_path]
  - Description: [what it contains]
  - Format: [file format]

### Output Locations
- Output 1: [full_path]
  - Template: [template_path]
  - Description: [what to produce]
  - Format: [file format]

### Reference Data
- Reference 1: [full_path]

---

## Task Instructions

### Objective
[Clear statement of what this task accomplishes]

### Detailed Steps

#### Step 1: [Step Name]
[Specific instructions]

**Actions:**
1. [Action 1]
2. [Action 2]

**Technical Specifications:**
- [Spec 1]
- [Spec 2]

### Business Rules and Constraints
- Rule 1: [description]

### Error Handling
- Scenario 1: [description and recovery]

---

## Expected Deliverables

### 1. [Deliverable Name]
**File**: [full_path]
**Template**: [template_path]
**Description**: [What it contains]
**Format**: [File format]

**Content Requirements:**
- Requirement 1
- Requirement 2

**Validation:**
- [ ] File exists at specified path
- [ ] File format matches template
- [ ] All required sections present

---

## Quality Criteria

### Completeness
- [ ] All required deliverables produced
- [ ] All required sections/fields populated

### Accuracy
- [ ] Data correctly extracted/transformed
- [ ] Calculations correct

### Consistency
- [ ] Naming conventions followed
- [ ] Format matches templates

---

## Success Criteria

**Task is complete when:**
- [ ] All deliverables produced at specified paths
- [ ] All quality criteria met
- [ ] All validation checks pass
- [ ] Ready for review

**Verification Steps:**
1. Check all output files exist
2. Validate file formats
3. Verify content completeness
4. Report completion to supervisor

---

## Notes

### Agent Definition Reference
Your complete role definition is in your agent definition file.
This task file provides project-specific context and instructions.

### Escalation
If you encounter issues:
1. Document the issue clearly
2. Report to [supervisor_name]
3. Provide context and attempted solutions
```

### 6.6 Task File Creation Workflow

```
1. Team Supervisor reads phase prompt
   ↓
2. Identifies Step 1 (e.g., "Source Code Analysis")
   ↓
3. Extracts instructions for Step 1
   ↓
4. Resolves all paths for Step 1
   ↓
5. Creates task file: analysis_sourcecode_specialist_task.md
   ↓
6. Saves to: {{TASKS_BASE_PATH}}/analysis_sourcecode_specialist_task.md
   ↓
7. Delegates to: analysis_specialist_legacy_code
   ↓
8. Provides: "Your task file is at [path]"
   ↓
9. Waits for completion
   ↓
10. Verifies deliverables
   ↓
11. Creates review task file: analysis_sourcecode_review_task.md
   ↓
12. Delegates to: analysis_reviewer_legacy_code
   ↓
[Iterate based on review outcome]
```

### 6.7 Common Mistakes to Avoid

**DON'T:**
- Don't duplicate agent definition in task file (reference it)
- Don't use relative paths (use absolute paths)
- Don't leave {{PARAMETERS}} unresolved
- Don't copy entire phase prompt (extract relevant parts)
- Don't omit quality criteria
- Don't forget to specify templates

**DO:**
- Reference agent definition file
- Resolve all paths to absolute paths
- Extract only relevant instructions
- Include complete context
- Specify all deliverables with paths
- Include quality and success criteria


---

## 7. End-to-End Example

### 7.1 Scenario: Analysis Phase Execution

This example demonstrates the complete flow from main prompt to deliverable production for the Analysis Phase.

### 7.2 Step-by-Step Walkthrough

#### Step 1: Migration Supervisor Receives Main Prompt

**Input:** `ReImagine_Main_Prompt.md`

```markdown
## Project Context
**Project Name**: MyMigration
**Project Base Path**: /project
**Task Files Location**: /project/tasks

### Phase 1: Source Code Analysis
**Team Supervisor**: analysis_team_supervisor
**Dependencies**: None

**Steps:**
1. Database Analysis (01_analysis.md)
2. Source Code Analysis (01_generate_cobol_analysis_tool.md)

**Expected Deliverables:**
- Database Analysis Report: /project/output/analysis/database/reports/db_analysis.md
- Source Code Analysis Report: /project/output/analysis/source_code/reports/cobol_analysis.md
- Dependency Table: /project/output/analysis/source_code/reports/dependency_table.csv
```

**Migration Supervisor Actions:**
1. Reads main prompt
2. Identifies Phase 1: Analysis
3. Identifies team supervisor: analysis_team_supervisor
4. Prepares to delegate Phase 1

#### Step 2: Migration Supervisor Delegates to Analysis Team Supervisor

**Delegation:**
```
TO: analysis_team_supervisor
PHASE: Phase 1 - Source Code Analysis
PROMPT_FILE: /project/prompts/01_analysis/Sourcecode/01_generate_cobol_analysis_tool.md
CONTEXT: Legacy code in /project/input/legacy/source
```

#### Step 3: Analysis Team Supervisor Reads Phase Prompt

**Input:** `01_generate_cobol_analysis_tool.md`

```markdown
# Source Code Analysis

## Orchestration Information
**Phase**: Phase 1 - Analysis
**Step**: 1.2 - Source Code Analysis
**Team Supervisor**: analysis_team_supervisor
**Assigned Agent**: analysis_specialist_legacy_code
**Task File Name**: {{TASKS_BASE_PATH}}/analysis_sourcecode_specialist_task.md

## Context
**Project Name**: MyMigration
**Project Base Path**: /project

### Input Locations
- Legacy Source Code: /project/input/legacy/source

### Output Locations
- Analysis Report: /project/output/analysis/source_code/reports/cobol_analysis.md
  - Template: /project/templates/Cobol_Source_Analysis_Report.md
- Dependency Table: /project/output/analysis/source_code/reports/dependency_table.csv
  - Template: /project/templates/Dependency_Analysis_Table.csv

## Instructions
[Detailed step-by-step instructions for source code analysis...]

## Quality Criteria
- All COBOL files analyzed
- All dependencies captured
- All business flows identified
```

**Analysis Team Supervisor Actions:**
1. Reads phase prompt
2. Understands Step 1.2: Source Code Analysis
3. Identifies assigned agent: analysis_specialist_legacy_code
4. Extracts instructions
5. Resolves all paths
6. Creates task file

#### Step 4: Analysis Team Supervisor Creates Task File

**Output:** `analysis_sourcecode_specialist_task.md`

```markdown
# Task: Source Code Analysis

## Agent Assignment
**Agent**: analysis_specialist_legacy_code
**Agent Definition**: /system/agents/analysis_team/analysis_specialist_legacy_code.md
**Task ID**: analysis-sourcecode-001
**Created By**: analysis_team_supervisor
**Created At**: 2024-01-15T10:00:00Z
**Phase**: analysis
**Step**: sourcecode

## Project Context

### Project Information
**Project Name**: MyMigration
**Project Base Path**: /project

### Input Locations
- Legacy Source Code: /project/input/legacy/source
  - Description: COBOL source files (.cbl, .cob)
  - Format: COBOL source code

### Output Locations
- Analysis Report: /project/output/analysis/source_code/reports/cobol_analysis.md
  - Template: /project/templates/Cobol_Source_Analysis_Report.md
  - Description: Comprehensive analysis findings
  - Format: Markdown

- Dependency Table: /project/output/analysis/source_code/reports/dependency_table.csv
  - Template: /project/templates/Dependency_Analysis_Table.csv
  - Description: Module dependency relationships
  - Format: CSV

## Task Instructions

### Objective
Analyze COBOL legacy source code to understand structure, dependencies, and business flows.

### Detailed Steps

#### Step 1: Source Code Discovery
Scan all source files in /project/input/legacy/source

**Actions:**
1. Identify all files with extensions: .cbl, .cob, .CBL, .COB
2. Create inventory with metadata
3. Log any files that cannot be parsed

#### Step 2: Dependency Analysis
Identify all dependencies between modules

**Actions:**
1. Recognize COBOL call patterns: CALL, CICS LINK, CICS XCTL
2. Map file operations: JCL DD statements, COBOL SELECT
3. Identify database operations: SQL statements

[Additional steps...]

## Expected Deliverables

### 1. Source Code Analysis Report
**File**: /project/output/analysis/source_code/reports/cobol_analysis.md
**Template**: /project/templates/Cobol_Source_Analysis_Report.md
**Description**: Comprehensive analysis methodology, findings, and recommendations

**Content Requirements:**
- Analysis methodology section
- Findings summary
- Dependency analysis results
- Module classification results

**Validation:**
- [ ] File exists at specified path
- [ ] File format matches template
- [ ] All required sections present

### 2. Dependency Analysis Table
**File**: /project/output/analysis/source_code/reports/dependency_table.csv
**Template**: /project/templates/Dependency_Analysis_Table.csv
**Description**: Complete module dependency relationships

**Content Requirements:**
- All modules listed
- All dependencies captured

## Quality Criteria

### Completeness
- [ ] All COBOL source files analyzed
- [ ] All dependency relationships captured

### Accuracy
- [ ] Module classifications consistent
- [ ] Dependency relationships verified

## Success Criteria
- [ ] All deliverables produced at specified paths
- [ ] All quality criteria met
- [ ] Ready for review
```

**Analysis Team Supervisor Actions:**
1. Saves task file to /project/tasks/analysis_sourcecode_specialist_task.md
2. Prepares to delegate to specialist

#### Step 5: Analysis Team Supervisor Delegates to Specialist

**Delegation:**
```
TO: analysis_specialist_legacy_code
TASK: Source Code Analysis
TASK_FILE: /project/tasks/analysis_sourcecode_specialist_task.md
```

#### Step 6: Specialist Executes Work

**Specialist Actions:**
1. Reads task file
2. Locates input files at /project/input/legacy/source
3. Analyzes COBOL source code
4. Identifies dependencies
5. Classifies modules
6. Generates analysis report at /project/output/analysis/source_code/reports/cobol_analysis.md
7. Generates dependency table at /project/output/analysis/source_code/reports/dependency_table.csv
8. Reports completion to analysis_team_supervisor

**Deliverables Produced:**
- `/project/output/analysis/source_code/reports/cobol_analysis.md` ✓
- `/project/output/analysis/source_code/reports/dependency_table.csv` ✓

#### Step 7: Analysis Team Supervisor Creates Review Task

**Output:** `analysis_sourcecode_review_task.md`

```markdown
# Task: Review Source Code Analysis (Iteration 1)

## Agent Assignment
**Agent**: analysis_reviewer_legacy_code
**Task ID**: analysis-sourcecode-review-001
**Created By**: analysis_team_supervisor
**Iteration**: 1

## Deliverables to Review

1. **Source Code Analysis Report**
   - Path: /project/output/analysis/source_code/reports/cobol_analysis.md
   - Template: /project/templates/Cobol_Source_Analysis_Report.md
   - Expected: Comprehensive analysis findings

2. **Dependency Analysis Table**
   - Path: /project/output/analysis/source_code/reports/dependency_table.csv
   - Template: /project/templates/Dependency_Analysis_Table.csv
   - Expected: Complete module dependencies

## Quality Criteria

### Completeness
- [ ] All COBOL files analyzed
- [ ] All dependencies captured
- [ ] All business flows identified

### Accuracy
- [ ] Module classifications consistent
- [ ] Dependency relationships verified

### Consistency
- [ ] Output formats match templates
- [ ] Naming conventions followed

## Review Outcome Options

### Option 1: APPROVED
All quality criteria met, ready to proceed.

### Option 2: ISSUES FOUND
List specific issues with remediation guidance.
```

#### Step 8: Analysis Team Supervisor Delegates to Reviewer

**Delegation:**
```
TO: analysis_reviewer_legacy_code
TASK: Review Source Code Analysis
TASK_FILE: /project/tasks/analysis_sourcecode_review_task.md
```

#### Step 9: Reviewer Validates Deliverables

**Reviewer Actions:**
1. Reads review task file
2. Locates deliverables
3. Validates against quality criteria
4. Checks completeness, accuracy, consistency

**Scenario A: APPROVED**
```
OUTCOME: APPROVED
All quality criteria met:
- All COBOL files analyzed ✓
- All dependencies captured ✓
- Module classifications consistent ✓
- Formats match templates ✓
```

**Analysis Team Supervisor Actions:**
1. Receives approval
2. Documents approval
3. Reports completion to Migration Supervisor

**Scenario B: ISSUES FOUND**
```
OUTCOME: ISSUES FOUND

Issue 1: Missing Business Flows
- Affected: cobol_analysis.md
- Severity: Blocking
- Criterion: Completeness
- Guidance: Section 4 "Business Flows" is empty. Analyze PERFORM statements to identify business flows.

Issue 2: Incomplete Dependency Table
- Affected: dependency_table.csv
- Severity: Major
- Criterion: Completeness
- Guidance: 15 modules have TargetFound=False. Investigate missing dependencies.
```

**Analysis Team Supervisor Actions:**
1. Receives issues
2. Creates remediation task file
3. Delegates back to specialist

#### Step 10: Remediation (If Issues Found)

**Output:** `analysis_sourcecode_remediation_task.md`

```markdown
# Task: Remediate Source Code Analysis Issues (Iteration 1)

## Agent Assignment
**Agent**: analysis_specialist_legacy_code
**Task ID**: analysis-sourcecode-remediation-001
**Original Task**: analysis_sourcecode_specialist_task.md
**Review Feedback**: analysis_sourcecode_review_task.md

## Issues to Address

### Issue 1: Missing Business Flows
- **Affected**: /project/output/analysis/source_code/reports/cobol_analysis.md
- **Severity**: Blocking
- **Guidance**: Analyze PERFORM statements to identify business flows. Add to Section 4.

### Issue 2: Incomplete Dependency Table
- **Affected**: /project/output/analysis/source_code/reports/dependency_table.csv
- **Severity**: Major
- **Guidance**: 15 modules have TargetFound=False. Investigate and resolve.

## Instructions
1. Review feedback from reviewer
2. Address Issue 1: Add business flows to report
3. Address Issue 2: Complete dependency investigation
4. Update deliverables
5. Report completion

## Success Criteria
- [ ] All issues addressed
- [ ] Deliverables updated
- [ ] Ready for re-review
```

**Specialist Actions:**
1. Reads remediation task
2. Addresses Issue 1: Analyzes PERFORM statements, adds business flows
3. Addresses Issue 2: Investigates missing dependencies
4. Updates deliverables
5. Reports completion

**Analysis Team Supervisor Actions:**
1. Creates new review task (iteration 2)
2. Delegates to reviewer again
3. Repeats until approved

#### Step 11: Phase Completion

**After Approval:**

**Analysis Team Supervisor Reports to Migration Supervisor:**
```
FROM: analysis_team_supervisor
TO: Migration Supervisor
PHASE: Phase 1 - Source Code Analysis
STATUS: COMPLETE
ITERATIONS: 2 (1 remediation cycle)

DELIVERABLES:
- Source Code Analysis Report: /project/output/analysis/source_code/reports/cobol_analysis.md ✓
- Dependency Table: /project/output/analysis/source_code/reports/dependency_table.csv ✓

QUALITY: All criteria met, approved by reviewer
```

**Migration Supervisor Actions:**
1. Verifies deliverables exist
2. Marks Phase 1 complete
3. Proceeds to Phase 2

### 7.3 Key Takeaways from Example

1. **Clear Delegation Chain**: Main Prompt → Migration Supervisor → Team Supervisor → Specialist
2. **Task File Creation**: Team Supervisor creates task files with complete context
3. **Path Resolution**: All paths resolved before delegation
4. **Iterative Review**: Review happens within phase, orchestrated by team supervisor
5. **Quality Assurance**: No phase proceeds without reviewer approval
6. **Complete Context**: Each agent receives all information needed


---

## 8. Troubleshooting Guide

### 8.1 Common Issues and Solutions

#### Issue 1: Agent Can't Find Input Files

**Symptoms:**
- Agent reports "file not found" errors
- Agent can't locate input data

**Causes:**
- Paths not resolved correctly in task file
- Relative paths used instead of absolute paths
- Input files don't exist at specified location

**Solutions:**
1. Verify paths in task file are absolute
2. Check input files exist at specified paths
3. Verify create_project.py filled all {{PARAMETERS}}
4. Check paths.cfg definitions match actual structure

**Prevention:**
- Always use absolute paths in task files
- Verify inputs exist before delegating
- Test path resolution with sample project

#### Issue 2: Deliverables Not Produced at Expected Paths

**Symptoms:**
- Specialist reports completion but deliverables missing
- Deliverables created in wrong location

**Causes:**
- Output paths not clearly specified in task file
- Agent misunderstood instructions
- Directory doesn't exist (agent can't create)

**Solutions:**
1. Verify output paths in task file are absolute and clear
2. Ensure output directories exist or agent can create them
3. Check specialist understood deliverable requirements
4. Verify template paths are correct

**Prevention:**
- Specify complete output paths in task files
- Include directory creation in instructions if needed
- Provide examples of expected deliverables

#### Issue 3: Review Iterations Excessive (>3 cycles)

**Symptoms:**
- Specialist → Reviewer cycle repeating many times
- Issues not being resolved effectively

**Causes:**
- Requirements unclear or conflicting
- Specialist lacks capability for requirements
- Reviewer expectations too high or unclear
- Missing information from previous phases

**Solutions:**
1. Team Supervisor escalates to Migration Supervisor
2. Clarify requirements with stakeholders
3. Adjust quality criteria if unrealistic
4. Provide additional resources or guidance
5. Consider different specialist agent if capability gap

**Prevention:**
- Clear, concrete quality criteria in phase prompts
- Realistic expectations for agent capabilities
- Complete information from previous phases
- Early escalation if issues persist

#### Issue 4: Task File Missing Information

**Symptoms:**
- Agent asks for clarification
- Agent can't complete task due to missing context

**Causes:**
- Team Supervisor didn't extract all relevant instructions
- Phase prompt incomplete
- Dependencies from previous phases not provided

**Solutions:**
1. Review phase prompt for missing information
2. Update task file with additional context
3. Provide dependencies from previous phases
4. Escalate if phase prompt is incomplete

**Prevention:**
- Complete phase prompts with all necessary information
- Task file creation checklist for supervisors
- Verify all dependencies before creating task file

#### Issue 5: Path Parameters Not Resolved

**Symptoms:**
- Task files contain {{PARAMETER}} placeholders
- Agents can't locate files due to unresolved paths

**Causes:**
- create_project.py didn't fill parameters
- New parameter added but not in paths.cfg
- Phase prompt not processed correctly

**Solutions:**
1. Verify paths.cfg contains all required parameters
2. Re-run create_project.py to regenerate prompts
3. Manually resolve paths in task file as workaround
4. Update paths.cfg and regenerate project

**Prevention:**
- Test create_project.py with sample project
- Verify all {{PARAMETERS}} resolved after project creation
- Maintain paths.cfg with all required variables

#### Issue 6: Duplicate Information Across Levels

**Symptoms:**
- Same information in multiple places
- Inconsistencies when information updated
- Large file sizes

**Causes:**
- Copying entire prompts instead of extracting
- Duplicating agent definitions in task files
- Not following reference pattern

**Solutions:**
1. Extract only relevant instructions, don't copy entire prompt
2. Reference agent definitions, don't duplicate
3. Use references for templates and dependencies
4. Review for duplication and refactor

**Prevention:**
- Follow extraction guidelines in phase prompts
- Use reference pattern consistently
- Review task files for duplication before delegating

#### Issue 7: Agent Doesn't Understand Role

**Symptoms:**
- Agent performs wrong type of work
- Agent asks for clarification on responsibilities

**Causes:**
- Task file doesn't reference agent definition
- Instructions conflict with agent role
- Wrong agent assigned to task

**Solutions:**
1. Verify correct agent assigned in task file
2. Include agent definition reference in task file
3. Ensure instructions align with agent capabilities
4. Reassign to correct agent if mismatch

**Prevention:**
- Always reference agent definition in task file
- Verify agent assignment matches task requirements
- Review agent capabilities before assignment

#### Issue 8: Reviewer and Specialist Disagree

**Symptoms:**
- Multiple remediation cycles with same issues
- Specialist believes work is correct, reviewer disagrees

**Causes:**
- Quality criteria ambiguous or conflicting
- Different interpretations of requirements
- Reviewer expectations not communicated clearly

**Solutions:**
1. Team Supervisor mediates discussion
2. Clarify quality criteria with concrete examples
3. Escalate to Migration Supervisor if unresolved
4. Update phase prompt with clearer criteria

**Prevention:**
- Concrete, measurable quality criteria
- Examples of acceptable deliverables
- Clear communication of expectations

### 8.2 Debugging Checklist

**When a task fails, check:**

1. **Task File Completeness**
   - [ ] Agent assignment present
   - [ ] All paths resolved (no {{PARAMETERS}})
   - [ ] Instructions clear and complete
   - [ ] Deliverables specified with paths
   - [ ] Quality criteria included

2. **Path Resolution**
   - [ ] All paths are absolute
   - [ ] Input paths point to existing files
   - [ ] Output paths are creatable
   - [ ] Template paths are correct

3. **Context Completeness**
   - [ ] Project information included
   - [ ] All inputs listed
   - [ ] All outputs listed
   - [ ] Dependencies provided

4. **Agent Assignment**
   - [ ] Correct agent for task type
   - [ ] Agent definition referenced
   - [ ] Agent capabilities match requirements

5. **Delegation Chain**
   - [ ] Dependencies satisfied
   - [ ] Previous phase outputs available
   - [ ] Supervisor verified prerequisites

### 8.3 Performance Optimization

**If orchestration is slow:**

1. **Parallel Execution** (Future Enhancement)
   - Some tasks within a phase can run in parallel
   - Requires dependency analysis
   - Not implemented in current design

2. **Task Batching**
   - Group similar tasks for same agent
   - Reduces delegation overhead
   - Requires careful dependency management

3. **Caching**
   - Cache task file templates
   - Reuse resolved paths
   - Cache agent definitions

4. **Incremental Processing**
   - Process large inputs in chunks
   - Produce intermediate deliverables
   - Resume from checkpoints if interrupted

### 8.4 Quality Assurance

**To ensure high-quality deliverables:**

1. **Clear Quality Criteria**
   - Concrete, measurable criteria
   - Examples of acceptable work
   - Validation checklists

2. **Iterative Review**
   - Review after each specialist task
   - Immediate feedback and remediation
   - Multiple iterations if needed

3. **Audit Trail**
   - Document all iterations
   - Track issues and resolutions
   - Maintain history for learning

4. **Escalation Protocol**
   - Clear escalation criteria
   - Timely escalation when needed
   - Resolution at appropriate level

### 8.5 Getting Help

**If you encounter issues not covered here:**

1. **Review Documentation**
   - Requirements document
   - Design document
   - Task file template documentation

2. **Check Examples**
   - End-to-end example in this document
   - Sample task files in design document
   - Agent definition examples

3. **Escalate**
   - Team Supervisor → Migration Supervisor
   - Migration Supervisor → Project Lead
   - Document issue clearly with context

4. **Update Documentation**
   - Add new issues to troubleshooting guide
   - Share solutions with team
   - Improve prompts and templates based on learnings


---

## 9. Best Practices

### 9.1 For Migration Supervisors

**DO:**
- Read and understand the entire main prompt before starting
- Verify all dependencies before delegating a phase
- Verify deliverables exist before proceeding to next phase
- Maintain clear communication with team supervisors
- Document phase completion and deliverables

**DON'T:**
- Don't perform technical work yourself
- Don't skip dependency verification
- Don't proceed without deliverable verification
- Don't ignore escalations from team supervisors
- Don't assume phases can run in parallel without checking dependencies

### 9.2 For Team Supervisors

**DO:**
- Read phase prompts completely before creating task files
- Extract only relevant instructions for each task
- Resolve all paths to absolute paths
- Create clear, complete task files
- Orchestrate review iteratively within the phase
- Track iterations and escalate if excessive
- Verify deliverables before reporting completion

**DON'T:**
- Don't perform technical work yourself
- Don't copy entire phase prompt into task file
- Don't duplicate agent definitions
- Don't use relative paths
- Don't skip review step
- Don't report completion without reviewer approval
- Don't let iterations exceed 3 without escalating

### 9.3 For Specialist Agents

**DO:**
- Read task files completely before starting
- Follow instructions exactly as specified
- Produce deliverables at specified paths
- Use provided templates
- Verify quality criteria before reporting completion
- Report issues to supervisor immediately
- Document any assumptions or decisions made

**DON'T:**
- Don't deviate from instructions without approval
- Don't produce deliverables at different paths
- Don't skip quality criteria verification
- Don't assume information not provided
- Don't ignore error conditions
- Don't report completion prematurely

### 9.4 For Reviewer Agents

**DO:**
- Review all specified deliverables systematically
- Apply quality criteria consistently
- Provide specific, actionable feedback
- Clearly state outcome (approved or issues)
- Document all findings
- Be constructive in feedback

**DON'T:**
- Don't skip deliverables
- Don't apply inconsistent criteria
- Don't provide vague feedback
- Don't approve work that doesn't meet criteria
- Don't be overly critical without justification
- Don't assume specialist understands implicit expectations

### 9.5 Task File Creation Best Practices

**Structure:**
- Follow the template consistently
- Include all required sections
- Use clear, descriptive headings

**Content:**
- Extract relevant instructions from phase prompt
- Provide complete context
- Specify all deliverables with paths
- Include quality and success criteria

**Paths:**
- Use absolute paths only
- Verify input paths exist
- Ensure output paths are creatable
- Include template paths

**Clarity:**
- Write clear, unambiguous instructions
- Provide examples where helpful
- Define technical terms
- Specify error handling

**Completeness:**
- Include all necessary information
- Don't assume agent has context
- Provide all dependencies
- Reference agent definition

### 9.6 Review Orchestration Best Practices

**Timing:**
- Review immediately after specialist completes
- Don't delay review to batch multiple tasks
- Iterate quickly to maintain momentum

**Feedback:**
- Be specific about issues found
- Provide remediation guidance
- Reference quality criteria violated
- Prioritize issues (blocking, major, minor)

**Iteration:**
- Track iteration count
- Escalate if >3 iterations
- Document all iterations for audit trail
- Learn from patterns to improve prompts

**Approval:**
- Only approve when all criteria met
- Document approval clearly
- Provide approval to team supervisor
- Enable phase progression

### 9.7 Communication Best Practices

**Delegation:**
- Provide complete context
- Specify expected deliverables
- Set clear success criteria
- Include escalation path

**Reporting:**
- Report completion clearly
- Provide deliverable paths
- Document any issues encountered
- Include quality verification

**Escalation:**
- Escalate early if blocked
- Provide complete context
- Suggest potential solutions
- Request specific help needed

**Documentation:**
- Document all decisions
- Maintain audit trail
- Update documentation based on learnings
- Share knowledge with team

### 9.8 Quality Assurance Best Practices

**Prevention:**
- Clear, concrete quality criteria
- Examples of acceptable work
- Validation checklists
- Template compliance

**Detection:**
- Systematic review process
- Consistent criteria application
- Multiple validation points
- Automated checks where possible

**Remediation:**
- Specific, actionable feedback
- Clear remediation guidance
- Timely iteration
- Verification after fixes

**Continuous Improvement:**
- Learn from issues
- Update prompts and templates
- Share best practices
- Refine quality criteria

### 9.9 Efficiency Best Practices

**Preparation:**
- Verify all prerequisites before starting
- Ensure all inputs available
- Validate paths and templates
- Review agent capabilities

**Execution:**
- Follow established workflows
- Use templates consistently
- Minimize rework through quality
- Document as you go

**Verification:**
- Verify at each step
- Don't defer verification
- Use checklists
- Automate where possible

**Learning:**
- Document lessons learned
- Update documentation
- Share knowledge
- Refine processes

### 9.10 Maintenance Best Practices

**Documentation:**
- Keep documentation current
- Update based on experience
- Include examples
- Maintain version history

**Templates:**
- Review and refine templates
- Ensure consistency
- Update based on feedback
- Version control

**Prompts:**
- Enhance based on learnings
- Keep instructions clear
- Update quality criteria
- Maintain modularity

**Agents:**
- Review agent definitions periodically
- Update capabilities as needed
- Ensure consistency across teams
- Document changes


---

## 10. FAQ

### 10.1 General Questions

**Q: What is the orchestration architecture?**

A: A 3-layer hierarchical system where supervisors coordinate work by delegating to specialized agents. The Migration Supervisor delegates phases to Team Supervisors, who create task files and delegate to Specialist and Reviewer agents.

**Q: Why use this architecture instead of direct agent execution?**

A: This architecture provides:
- Clear separation between orchestration and execution
- Reusable generic agents across projects
- Built-in quality assurance through review
- Scalability and maintainability
- Flexibility to adapt workflows

**Q: What are the three layers?**

A: 
1. **Layer 1**: Migration Supervisor (top-level orchestrator)
2. **Layer 2**: Team Supervisors (phase-level orchestrators)
3. **Layer 3**: Specialist & Reviewer Agents (workers)

### 10.2 Delegation Questions

**Q: When does the Migration Supervisor delegate to Team Supervisors?**

A: After reading the main prompt, understanding all phases, and verifying that dependencies for a phase are satisfied (previous phase outputs exist).

**Q: How does a Team Supervisor know which agent to assign?**

A: The phase prompt specifies the assigned agent for each step. For example, "Assigned Agent: analysis_specialist_legacy_code".

**Q: Can phases run in parallel?**

A: Not in the current design. Phases have dependencies and must run sequentially. Future enhancements may support parallel execution where dependencies allow.

**Q: Can tasks within a phase run in parallel?**

A: Not in the current design, but this is a potential future enhancement. Currently, Team Supervisors execute tasks sequentially.

### 10.3 Task File Questions

**Q: Who creates task files?**

A: Team Supervisors create task files for their team members (specialists and reviewers).

**Q: Where are task files stored?**

A: In the {{TASKS_BASE_PATH}} directory, typically `/project/tasks/`.

**Q: What's the naming convention for task files?**

A: `[phase]_[step]_[agent-role]_task.md`
Example: `analysis_sourcecode_specialist_task.md`

**Q: Should task files include the agent definition?**

A: No. Task files should reference the agent definition file, not duplicate it. This maintains a single source of truth.

**Q: What if a task file is missing information?**

A: The agent should report the issue to the team supervisor, who can update the task file or escalate if the phase prompt is incomplete.

### 10.4 Review Questions

**Q: When does review happen?**

A: Immediately after a specialist completes their work. Review is orchestrated by the team supervisor within the phase, not as a separate sequential step.

**Q: Who performs reviews?**

A: Reviewer agents (e.g., analysis_reviewer_legacy_code, business_reviewer_logic_extraction).

**Q: What happens if a reviewer finds issues?**

A: The team supervisor creates a remediation task file for the specialist, including specific issues and guidance. The specialist fixes the issues, and the reviewer reviews again. This iterates until approved.

**Q: How many review iterations are acceptable?**

A: Up to 3 iterations. If more are needed, the team supervisor should escalate to the Migration Supervisor.

**Q: Can a phase proceed without review approval?**

A: No. Team supervisors only report phase completion after reviewer approval.

### 10.5 Path Questions

**Q: Should paths be relative or absolute?**

A: Always absolute. Relative paths can cause confusion and errors.

**Q: What are {{PARAMETERS}} in prompts?**

A: Placeholders that get filled by create_project.py when a project is created. Example: `{{COBOL_SOURCE_ANALYSIS_REPORT}}` becomes `/project/output/analysis/source_code/reports/cobol_analysis.md`.

**Q: What if paths contain {{PARAMETERS}} in a task file?**

A: This is an error. All paths must be fully resolved before creating task files. Team supervisors must resolve all {{PARAMETERS}}.

**Q: Where are path definitions stored?**

A: In `config/paths.cfg`, which defines all path variables used in the project.

### 10.6 Quality Questions

**Q: How is quality ensured?**

A: Through iterative review orchestrated by team supervisors. Every deliverable is reviewed against quality criteria before the phase proceeds.

**Q: What are quality criteria?**

A: Specific, measurable requirements that deliverables must meet. Examples: "All COBOL files analyzed", "All dependencies captured", "Format matches template".

**Q: Who defines quality criteria?**

A: Quality criteria are defined in phase prompts and included in task files.

**Q: What if quality criteria are unclear?**

A: The team supervisor should escalate to the Migration Supervisor for clarification.

### 10.7 Error Handling Questions

**Q: What if an agent encounters an error?**

A: The agent should report the error to their supervisor with context and attempted solutions. The supervisor can provide guidance, update the task file, or escalate.

**Q: What if a specialist can't complete a task?**

A: The specialist reports to the team supervisor, who can:
- Provide additional guidance
- Update the task file with more information
- Assign a different agent
- Escalate to Migration Supervisor

**Q: What if dependencies from previous phases are missing?**

A: The team supervisor should report to the Migration Supervisor, who can verify the previous phase or coordinate remediation.

**Q: When should issues be escalated?**

A: Escalate when:
- More than 3 review iterations needed
- Conflicting requirements
- Missing information from previous phases
- Agent capabilities insufficient
- Blocking technical issues

### 10.8 Maintenance Questions

**Q: How do I add a new phase?**

A: 
1. Add phase to main prompt with delegation instructions
2. Create phase prompt file with detailed instructions
3. Update team supervisor agent if needed
4. Add path variables to paths.cfg
5. Test end-to-end

**Q: How do I add a new agent?**

A: 
1. Create agent definition file
2. Update team supervisor to include new agent
3. Update phase prompts to reference new agent
4. Test with sample task

**Q: How do I update quality criteria?**

A: Update the phase prompt with new criteria. Team supervisors will include updated criteria in task files for future tasks.

**Q: How do I update a template?**

A: Update the template file in the templates directory. Ensure all projects using the template are aware of the change.

### 10.9 Troubleshooting Questions

**Q: Agent can't find input files. What's wrong?**

A: Check:
- Paths in task file are absolute
- Input files exist at specified paths
- No {{PARAMETERS}} left unresolved
- Paths match actual file locations

**Q: Deliverables not produced at expected paths. Why?**

A: Check:
- Output paths clearly specified in task file
- Output directories exist or can be created
- Agent understood deliverable requirements
- Template paths are correct

**Q: Review iterations are excessive. What should I do?**

A: Team supervisor should:
- Escalate to Migration Supervisor
- Clarify requirements
- Adjust quality criteria if unrealistic
- Provide additional resources or guidance

**Q: Task file is missing information. How to fix?**

A: Team supervisor should:
- Review phase prompt for missing information
- Update task file with additional context
- Escalate if phase prompt is incomplete

### 10.10 Advanced Questions

**Q: Can I customize the orchestration for my project?**

A: Yes, but maintain the 3-layer structure. You can:
- Add new phases
- Add new agents
- Customize quality criteria
- Adjust workflows within phases

**Q: Can I skip the review step?**

A: Not recommended. Review ensures quality and catches issues early. If you must skip, document the decision and accept the risk.

**Q: Can I use different tools for task file creation?**

A: Yes. The current design expects team supervisors to create task files, but you could build tools to automate this. Ensure task files follow the template.

**Q: How do I measure orchestration performance?**

A: Track:
- Time per phase
- Number of review iterations
- Escalation frequency
- Deliverable quality
- Agent utilization

**Q: Can I integrate with CI/CD pipelines?**

A: Yes. The orchestration architecture can be integrated with CI/CD by:
- Triggering phases from pipeline stages
- Storing deliverables in version control
- Automating verification steps
- Reporting progress to pipeline

---

## 11. Glossary

**Agent**: An AI entity with a specific role and capabilities (e.g., specialist, reviewer, supervisor).

**Delegation**: The act of assigning work from a supervisor to a worker agent.

**Deliverable**: An output artifact produced by an agent (e.g., report, code, specification).

**Iteration**: One cycle of specialist work → review → remediation (if needed).

**Main Prompt**: The top-level prompt given to the Migration Supervisor containing all phases.

**Migration Supervisor**: The top-level orchestrator agent that coordinates all phases.

**Orchestration**: The coordination of multiple agents to accomplish a complex goal.

**Phase**: A major stage in the migration process (e.g., Analysis, Workpackage Planning, Business Extraction).

**Phase Prompt**: A phase-specific prompt given to a Team Supervisor with detailed instructions.

**Quality Criteria**: Specific, measurable requirements that deliverables must meet.

**Remediation**: The process of fixing issues found during review.

**Review**: The validation of deliverables against quality criteria by a reviewer agent.

**Reviewer Agent**: A worker agent that validates deliverables and provides feedback.

**Specialist Agent**: A worker agent that performs technical work and produces deliverables.

**Task File**: An agent-specific instruction file created by a Team Supervisor.

**Team Supervisor**: A phase-level orchestrator agent that creates task files and delegates to specialists and reviewers.

**Template**: A predefined structure for a deliverable (e.g., report template, specification template).

---

## 12. References

### 12.1 Related Documentation

- **Requirements Document**: `.kiro/specs/prompt-orchestration-refactor/requirements.md`
- **Design Document**: `.kiro/specs/prompt-orchestration-refactor/design.md`
- **Tasks Document**: `.kiro/specs/prompt-orchestration-refactor/tasks.md`
- **Task File Template**: `structure/doc/task_file_template.md`
- **Path Configuration**: `config/paths.cfg`

### 12.2 Example Files

- **Main Prompt**: `structure/prompts/ReImagine_Main_Prompt.md`
- **Phase Prompt Example**: `structure/prompts/01_analysis/Sourcecode/01_generate_cobol_analysis_tool.md`
- **Agent Definition Example**: `structure/agents/analysis_team/analysis_specialist_legacy_code.md`
- **Team Supervisor Example**: `structure/agents/analysis_team/analysis_team_supervisor.md`

### 12.3 Tools

- **Project Creation**: `create_project.py`
- **Deliverable Validation**: `structure/validate_deliverables.sh`

---

## 13. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | System | Initial comprehensive documentation |

---

## 14. Appendix: Visual Diagrams

### 14.1 Architecture Overview

```
                    ┌─────────────────────────────────┐
                    │   Main Migration Prompt         │
                    │   (All Phases + Paths)          │
                    └─────────────────────────────────┘
                                   │
                                   │ Given to
                                   ▼
                    ┌─────────────────────────────────┐
                    │   Migration Supervisor          │
                    │   (Layer 1: Top Orchestrator)   │
                    └─────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │  Analysis    │ │  Planning    │ │  Business    │
         │  Team        │ │  Team        │ │  Team        │
         │  Supervisor  │ │  Supervisor  │ │  Supervisor  │
         │  (Layer 2)   │ │  (Layer 2)   │ │  (Layer 2)   │
         └──────────────┘ └──────────────┘ └──────────────┘
                │                 │                 │
         ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
         │             │   │             │   │             │
         ▼             ▼   ▼             ▼   ▼             ▼
    ┌─────────┐  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │Specialist│ │Reviewer │ │Specialist│ │Reviewer │ │Specialist│
    │ (Layer 3)│ │(Layer 3)│ │(Layer 3) │ │(Layer 3)│ │(Layer 3) │
    └─────────┘  └─────────┘ └─────────┘ └─────────┘ └─────────┘
         │             │          │            │           │
         ▼             ▼          ▼            ▼           ▼
    Deliverables  Validation  Deliverables Validation Deliverables
```

### 14.2 Review Iteration Flow

```
    ┌─────────────────────────────────────────────────────────┐
    │                  Team Supervisor                         │
    └─────────────────────────────────────────────────────────┘
                            │
                            │ Creates specialist task
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │                     Specialist                           │
    │              Produces Deliverables                       │
    └─────────────────────────────────────────────────────────┘
                            │
                            │ Completes
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │                  Team Supervisor                         │
    │              Creates review task                         │
    └─────────────────────────────────────────────────────────┘
                            │
                            │ Delegates to reviewer
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │                      Reviewer                            │
    │          Validates Against Quality Criteria              │
    └─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         APPROVED                    ISSUES FOUND
              │                           │
              ▼                           ▼
    ┌──────────────────┐      ┌──────────────────────┐
    │ Phase Complete   │      │ Create Remediation   │
    │ Report to        │      │ Task for Specialist  │
    │ Migration Super  │      └──────────────────────┘
    └──────────────────┘                 │
                                         │ Iterate
                                         ▼
                              ┌──────────────────────┐
                              │ Specialist Fixes     │
                              │ Issues               │
                              └──────────────────────┘
                                         │
                                         │ Back to review
                                         ▼
                              ┌──────────────────────┐
                              │ Reviewer Validates   │
                              │ Again (Iteration N+1)│
                              └──────────────────────┘
```

---

**End of Orchestration Architecture Documentation**
