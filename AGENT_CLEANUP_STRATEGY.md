# Agent Cleanup Strategy: Removing Project-Specific Paths

## Problem Statement

Agent definition files currently contain project-specific path variables (e.g., `{{PROJECT_BASE_PATH}}`, `{{FUNCTIONAL_REQUIREMENTS_SPECS}}`). This makes agents project-specific rather than generic and reusable.

## Solution

Remove ALL path variables from agent files. Agents should be completely generic. All project-specific information (paths, file locations, templates) should be provided through task files created by supervisors.

---

## Cleanup Rules

### 1. Remove Path Variables from Input Sections
**Before**:
```markdown
## Input Requirements

### Required Business Logic Inputs
- **Business Logic Inventory**: `{{BUSINESS_LOGIC_INVENTORY}}`
- **Business Rules Extraction**: `{{BUSINESS_RULES_EXTRACTION}}`
```

**After**:
```markdown
## Input Requirements

Agents receive all input file paths and requirements through task files provided by the team supervisor. Task files contain:
- Complete list of input files with absolute paths
- Required business logic inputs
- Required planning inputs
- All necessary context and reference data

Refer to your assigned task file for specific input locations.
```

### 2. Remove Path Variables from Deliverables Sections
**Before**:
```markdown
### 1. Functional Requirements Specifications
**File**: `{{FUNCTIONAL_REQUIREMENTS_SPECS}}`
**Content**: Comprehensive functional requirements
```

**After**:
```markdown
## Expected Deliverables

Agents receive all output file paths and specifications through task files provided by the team supervisor. Task files specify:
- Complete list of deliverables with absolute paths
- Required content and format for each deliverable
- Templates to follow
- Quality criteria and success metrics

Typical deliverables for this agent include:
1. **Functional Requirements Specifications** - Comprehensive functional requirements
2. **Non-Functional Requirements** - Performance, security requirements
...

Refer to your assigned task file for specific deliverable locations and detailed requirements.
```

### 3. Remove Path Variables from Supervisor Task Assignment Sections
**Before**:
```markdown
### Step 1: Business Logic Extraction
**Task Description File**: `{{PROJECT_BASE_PATH}}/tasks/business_logic_extraction_specialist_task.md`
**Expected Deliverables**:
- Business logic inventory: `{{BUSINESS_LOGIC_INVENTORY}}`
```

**After**:
```markdown
### Step 1: Business Logic Extraction
**Assigned to**: Business Logic Extraction Specialist

**Task Creation**: Create task file with:
- All input file paths (absolute)
- All output file paths (absolute)
- Templates to use
- Quality criteria

**Expected Deliverables**:
- Business logic inventory
- Business rules extraction
- Domain model specifications
...

Refer to phase prompt for specific paths and requirements.
```

### 4. Keep Generic Examples (No Paths)
**Acceptable**:
```markdown
## Quality Standards

### Requirements Quality Criteria
- **Completeness**: All business logic is translated into requirements
- **Clarity**: Requirements are clearly stated and unambiguous
- **Testability**: All requirements include measurable acceptance criteria
```

This is fine because it's generic guidance, not project-specific paths.

---

## Agent Types and Cleanup Approach

### Specialist Agents (11 agents)
**Files**: `*_specialist_*.md`

**Sections to Clean**:
- Input Requirements → Generic statement + "refer to task file"
- Expected Deliverables → Generic list + "refer to task file"
- Keep: Role, Responsibilities, Methodology, Quality Standards, Error Handling

### Reviewer Agents (11 agents)
**Files**: `*_reviewer_*.md`

**Sections to Clean**:
- Deliverables to Review → Generic statement + "refer to task file"
- Feedback Documentation Format → Remove specific paths, keep format structure
- Approval Documentation → Remove specific paths, keep format structure
- Keep: Role, Review Methodology, Quality Criteria, Error Handling

### Supervisor Agents (6 agents)
**Files**: `*_team_supervisor.md`, `migration_supervisor.md`

**Sections to Clean**:
- Step assignments → Remove `{{PROJECT_BASE_PATH}}/tasks/...` references
- Input Requirements → Remove path variables
- Expected Deliverables → Remove path variables
- Add: "Create task files with paths from phase prompt"
- Keep: Orchestration logic, workflow, quality gates, escalation procedures

---

## Standard Replacement Text

### For Specialist/Reviewer Input Sections:
```markdown
## Input Requirements

All input file paths and requirements are provided through task files created by the team supervisor. Task files contain:
- Complete list of input files with absolute paths
- Required templates and reference data
- All necessary context for task execution

Refer to your assigned task file for specific input locations and requirements.
```

### For Specialist/Reviewer Deliverables Sections:
```markdown
## Expected Deliverables

All output file paths and specifications are provided through task files created by the team supervisor. Task files specify:
- Complete list of deliverables with absolute paths
- Required content and format for each deliverable
- Templates to follow
- Quality criteria and success metrics

Typical deliverables for this agent include:
[List deliverable types without paths]

Refer to your assigned task file for specific deliverable locations and detailed requirements.
```

### For Supervisor Step Assignments:
```markdown
### Step X: [Step Name]
**Assigned to**: [Agent Name]

**Task File Creation**: Create task file containing:
- All input file paths (resolved from phase prompt)
- All output file paths (resolved from phase prompt)
- Template locations
- Quality criteria and success metrics
- Detailed instructions from phase prompt

**Expected Deliverables**:
[List deliverable types without paths]

Refer to phase prompt for path variables and their resolutions.
```

---

## Verification Checklist

After cleanup, each agent file should:
- [ ] Contain NO `{{VARIABLE}}` path references
- [ ] Contain NO hardcoded project paths
- [ ] Reference "task file" for all paths and specifics
- [ ] Keep generic role, responsibilities, and methodology
- [ ] Keep quality standards and error handling
- [ ] Be usable across ANY project without modification

---

## Benefits

1. **Reusability**: Agents work for any project without modification
2. **Maintainability**: Path changes only affect prompts/config, not agents
3. **Clarity**: Clear separation between generic agent logic and project specifics
4. **Flexibility**: Easy to adapt to different project structures
5. **Portability**: Agents can be shared across teams and projects

---

## Implementation Order

1. ✅ **Business Specialist Requirements** - Already cleaned (example)
2. **Remaining Business Team** (6 agents)
3. **Analysis Team** (5 agents)
4. **Planning Team** (3 agents)
5. **Development Team** (5 agents)
6. **Deployment Team** (7 agents)
7. **Migration Supervisor** (1 agent)

Total: 28 agents to clean

---

## Next Steps

1. Apply cleanup to all 28 agent files
2. Verify no `{{VARIABLE}}` references remain
3. Test that prompts contain all necessary path information
4. Update documentation to reflect new structure
5. Create migration guide for existing projects
