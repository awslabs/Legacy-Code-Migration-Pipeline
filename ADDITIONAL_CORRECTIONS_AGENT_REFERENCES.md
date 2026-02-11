# Additional Corrections: Agent References and File Paths

## Issue Discovered
The orchestration file referenced non-existent agents and incorrect file paths for Phase 3 task documents.

---

## Problems Found

### 1. Non-Existent Agent: `business_context_analyst`
**Problem**: Phase 3.0 referenced `business_context_analyst` which doesn't exist

**Actual Agents Available**:
- `business_specialist_logic_extraction`
- `business_specialist_requirements`
- `business_specialist_test_design`
- `business_reviewer_logic_extraction`
- `business_reviewer_requirements`
- `business_reviewer_test_design`
- `business_team_supervisor`

**Solution**: Use `business_specialist_logic_extraction` for Phase 3.0 (context discovery) and Phase 3.1 (specification extraction)

**Rationale**: The `business_specialist_logic_extraction` agent's responsibilities include "Business Context Analysis" and can handle both phases.

### 2. Incorrect File Path Pattern
**Problem**: Orchestration referenced files with pattern `03_business_extraction_phase_X.X.md`

**Actual Files**:
- `phase_3.0_business_context_discovery.md.md`
- `phase_3.1_business_specification_extraction.md`
- `phase_3.2_business_specification_verification.md`

**Solution**: Updated all references to use correct file paths with subdirectory

---

## Corrections Applied

### File: `structure/prompts/03-business_extraction/01_business_specification_master-orchestration.md`

#### 1. Phase Task Document Paths
**Changed**:
```markdown
# OLD (incorrect paths)
- Phase 3.0: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.0.md
- Phase 3.1: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.1.md
- Phase 3.2: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.2.md

# NEW (correct paths)
- Phase 3.0: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0_business_context_discovery.md.md
- Phase 3.1: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1_business_specification_extraction.md
- Phase 3.2: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2_business_specification_verification.md
```

#### 2. Phase 3.0 Agent Assignment
**Changed**:
```markdown
# OLD (non-existent agent)
ASSIGN: business_context_analyst
PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.0.md

# NEW (correct agent and path)
ASSIGN: business_specialist_logic_extraction
PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0_business_context_discovery.md.md
```

#### 3. Phase 3.1 Task Path
**Changed**:
```markdown
# OLD (incorrect path)
PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.1.md

# NEW (correct path)
PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1_business_specification_extraction.md
```

#### 4. Phase 3.2 Task Path
**Changed**:
```markdown
# OLD (incorrect path)
PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.2.md

# NEW (correct path)
PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2_business_specification_verification.md
```

#### 5. Agent Assignments Section
**Changed**:
```markdown
# OLD
### Phase 3.0: Business Context Discovery
**Agent**: business_context_analyst
**Agent Definition**: structure/agents/business_team/business_context_analyst.md
**Task Document**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.0.md

# NEW
### Phase 3.0: Business Context Discovery
**Agent**: business_specialist_logic_extraction
**Agent Definition**: structure/agents/business_team/business_specialist_logic_extraction.md
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.0_business_context_discovery.md.md
```

```markdown
# OLD
### Phase 3.1: Business Specification Extraction
**Task Document**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.1.md

# NEW
### Phase 3.1: Business Specification Extraction
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.1_business_specification_extraction.md
```

```markdown
# OLD
### Phase 3.2: Business Specialist Review
**Task Document**: {{PROMPTS_BASE_PATH}}/03_business_extraction_phase_3.2.md

# NEW
### Phase 3.2: Business Specialist Review
**Task Document**: {{PROMPTS_BASE_PATH}}/03-business_extraction/phase_3.2_business_specification_verification.md
```

### File: `structure/prompts/03-business_extraction/phase_3.0_business_context_discovery.md.md`

**Changed**:
```markdown
# OLD
**Assigned Agent**: business_context_analyst

# NEW
**Assigned Agent**: business_specialist_logic_extraction
```

### File: `structure/prompts/03-business_extraction/phase_3.2_business_specification_verification.md`

**Changed**:
```markdown
# OLD
**Assigned Agent**: business_analyst_reviewer
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.2_business_analyst_review.md

# NEW
**Assigned Agent**: business_reviewer_requirements
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.2_business_specialist_review.md
```

---

## Agent Workflow Clarification

### Phase 3.0: Business Context Discovery
- **Agent**: `business_specialist_logic_extraction`
- **Purpose**: Understand business domain, identify stakeholders, extract vocabulary
- **Output**: Business context document, business glossary

### Phase 3.1: Business Specification Extraction
- **Agent**: `business_specialist_logic_extraction` (same agent, different phase)
- **Purpose**: Extract business entities, rules, functions, and processes
- **Output**: Business specification documents (EN and DN)

### Phase 3.2: Business Specialist Review
- **Agent**: `business_reviewer_requirements`
- **Purpose**: Validate specifications, ensure quality, approve for next phase
- **Output**: Review report, reviewed specifications

**Note**: The same agent (`business_specialist_logic_extraction`) handles both Phase 3.0 and 3.1 because:
1. Context discovery and specification extraction are closely related
2. The agent has capabilities for both "Business Context Analysis" and "Business Rule Extraction"
3. Continuity helps maintain consistency between context and specification

---

## Verification Checklist

After these corrections:

- [x] All agent names reference actual agents in `structure/agents/business_team/`
- [x] All task document paths reference actual files in `structure/prompts/03-business_extraction/`
- [x] Phase 3.0 uses `business_specialist_logic_extraction`
- [x] Phase 3.1 uses `business_specialist_logic_extraction`
- [x] Phase 3.2 uses `business_reviewer_requirements`
- [x] All file paths include subdirectory: `03-business_extraction/`
- [x] All file paths match actual filenames exactly

---

## Summary

Fixed 8 incorrect references:
1. ✅ Phase 3.0 agent: `business_context_analyst` → `business_specialist_logic_extraction`
2. ✅ Phase 3.0 task path: Added subdirectory and correct filename
3. ✅ Phase 3.1 task path: Added subdirectory and correct filename
4. ✅ Phase 3.2 agent: `business_analyst_reviewer` → `business_reviewer_requirements`
5. ✅ Phase 3.2 task path: Added subdirectory and correct filename
6. ✅ Agent assignments section: Updated all 3 phases
7. ✅ Orchestration workflow: Updated all 3 PROVIDE_TASK references
8. ✅ Task document list: Updated all 3 path references

All Phase 3 orchestration now references correct agents and file paths.
