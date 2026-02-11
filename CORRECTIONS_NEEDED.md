# Documentation Corrections Needed

## Issue 1: "Business Analyst" → "Business Specialist"

The following files incorrectly reference "Business Analyst" when they should reference the actual agent names:

### Agent References to Fix:
- `business_analyst_reviewer` → `business_reviewer_requirements` (or appropriate reviewer)
- "Business Analyst" role → "Business Specialist" or specific specialist name

### Files Requiring Updates:

1. **structure/prompts/03-business_extraction/01_business_specification_master-orchestration.md**
   - Line 266: `business_analyst_reviewer` → `business_reviewer_requirements`
   - Line 267: Agent definition path needs correction

2. **structure/prompts/03-business_extraction/phase_3.2_business_specification_verification.md**
   - Title and references to "Business Analyst Review"
   - Should reference appropriate business reviewer agents

3. **docs/workshop/AWS_WORKSHOP_DELIVERABLES_MODULE_4-5.md**
   - Multiple references to "Business Analyst" as a role (lines 538, 1470, 1709, 3638, 3712, 6167, 6746)
   - These are in workshop context, may be intentional as human roles vs agent names
   - Review to determine if these should be "Business Specialist" or remain as human role references

4. **structure/templates/Business_Specification_Status.json**
   - Line 30: `"phaseName": "Business Analyst Review"` → `"Business Specialist Review"`

5. **structure/doc/prompts/Phase 3 Business Specification Extraction.md**
   - Line 82: "Phase 3.2: Business Analyst Review" → "Business Specialist Review"
   - Line 157: References to "business analyst" in context descriptions
   - Line 236: "business analyst review" → "business specialist review"

6. **structure/prompts/03-business_extraction/01_business_extractions.md**
   - Line 11: "Phase 3.2: Business Analyst Review" → "Business Specialist Review"
   - Multiple references to "business analyst input" and "business analyst review"

7. **structure/prompts/03-business_extraction/01_business_extractions_2.md**
   - References to "business analysts" in readability context
   - May be intentional (referring to human business analysts reading the output)

8. **structure/prompts/03-business_extraction/phase_3.0_business_context_discovery.md.md**
   - References to "business analyst input" and "business analyst" in context
   - Review to determine if these refer to human roles or agent names

9. **Analysis prompts** (01_analysis/Sourcecode/*.md):
   - References to "Flag for business analyst review"
   - These may be intentional (escalation to human business analysts)

## Issue 2: "WP-XXX-definition.md" → Correct File Reference

The following files reference a non-existent `WP-XXX-definition.md` file:

### Actual Structure:
- Phase 1 produces: `Business_Flows.json`
- Phase 2 produces: `Workpackage_Dependencies.json` (extends Business_Flows.json with workpackage fields)
- There is NO `WP-XXX-definition.md` file or template

### Files Requiring Updates:

1. **structure/prompts/03-business_extraction/01_business_specification_master-orchestration.md**
   - Line 84: `{{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/WP-XXX-definition.md`
   - Line 126: Same reference
   - Should reference: `{{WORKPACKAGE_DEPENDENCIES}}` which points to `Workpackage_Dependencies.json`

### Correct Path Variables:
```
WORKPACKAGE_DEPENDENCIES={{WORKPACKAGE_ANALYSIS_OUTPUT}}/Workpackage_Dependencies.json
WORKPACKAGE_DEPENDENCIES_TEMPLATE={{TEMPLATE_BASE_PATH}}/Workpackage_Dependencies.json
```

## Recommended Actions:

### Priority 1: Fix Agent References
1. Update all `business_analyst_reviewer` → `business_reviewer_requirements`
2. Update phase names from "Business Analyst Review" → "Business Specialist Review"
3. Verify agent definition paths point to correct files in `structure/agents/business_team/`

### Priority 2: Fix File Path References
1. Replace all `WP-XXX-definition.md` references with `{{WORKPACKAGE_DEPENDENCIES}}`
2. Update documentation to clarify the actual file structure:
   - Phase 1: `Business_Flows.json`
   - Phase 2: `Workpackage_Dependencies.json` (contains all Business_Flows data + workpackage fields)
   - Phase 3: Uses `Workpackage_Dependencies.json` as input

### Priority 3: Clarify Human vs Agent Roles
Review workshop materials and context descriptions to determine:
- Where "business analyst" refers to a human role (keep as-is)
- Where it should refer to the agent (change to "business specialist")

## Notes:

- The workshop materials (AWS_WORKSHOP_DELIVERABLES_MODULE_4-5.md) may intentionally use "Business Analyst" as a human role
- Analysis prompts may intentionally escalate to human "business analysts" for review
- Focus corrections on agent orchestration files and phase definitions where agent names must be accurate
