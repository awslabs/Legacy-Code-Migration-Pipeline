
# Phase 3.2.1: Business Specification Review

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.2.1 - Business Specification Review
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_reviewer_requirements
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.2.1_business_specification_review.md

### Expected Deliverables

1. **Approved Business Specification Documents**
   - File: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN-approved.md
   - File: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-approved.md
   - Description: Validated and refined business specifications ready for code generation (final deliverables)

2. **Archived Drafts** (moved to review folder)
   - File: {{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-EN-draft.md
   - File: {{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-draft.md
   - Description: Original drafts moved to review folder for audit trail

3. **Review Reports**
   - File: {{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md
   - Description: Detailed review findings, changes made, and approval status

4. **Business Context Updates** (if needed)
   - File: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-updated.md
   - Description: Updated business context based on review findings

5. **Business Glossary Updates** (if needed)
   - File: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
   - Description: Updated business glossary with clarifications (living document)

6. **Progress Tracking**
   - File: {{BUSINESS_SPECIFICATION_STATUS}}
   - Description: Updated progress tracking with review completion status

### Success Criteria
- [ ] All business specifications reviewed and validated
- [ ] Business requirements match actual business policies
- [ ] Missing business requirements identified and added
- [ ] Accidental complexity removed
- [ ] Business rationale and context added where missing
- [ ] Technology-agnostic language verified (Chapters 1-5)
- [ ] Legacy implementation details verified (Chapter 6)
- [ ] Bilingual consistency verified (EN and other versions)
- [ ] All review reports completed
- [ ] Specifications approved for modernization
- [ ] Ready for code generation phase

---

## Context

### Input Locations
- **Business specifications (EN) - draft**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN-draft.md`
- **Business specifications (other) - draft**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-draft.md`
- **Business context**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md`
- **Business glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- **Source code**: `{{SOURCE_CODE}}` (for verification)
- **Legacy specifications**: `{{PROJECT_BASE_PATH}}/input/legacy_specifications/`

### Output Locations
- **Approved specifications (EN)**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN-approved.md` (main folder - final deliverable)
- **Approved specifications (other)**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-approved.md` (main folder - final deliverable)
- **Archived drafts (EN)**: `{{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-EN-draft.md` (moved from main folder)
- **Archived drafts (other)**: `{{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-draft.md` (moved from main folder)
- **Review reports**: `{{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md`
- **Updated context**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-updated.md` (if needed)
- **Updated glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md` (living document)
- **Progress tracking**: `{{BUSINESS_SPECIFICATION_STATUS}}`

### Template Locations
- **Business specification template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`
- **Business context template**: `{{BUSINESS_CONTEXT_TEMPLATE}}`

### Previous Phase Artifacts
- **From Phase 3.1**: Business specification documents (EN and other versions)
- **From Phase 3.0**: Business context documents, business glossary

---

## Objective

Review and validate business specifications from Phase 3.2 against Chapter 6 evidence to detect drift. Perform backward validation using 20% sampling, calculate drift metrics, and ensure specifications accurately represent business requirements. Approve specifications for code generation or return for revision.

**CRITICAL REVIEW PRINCIPLES**:
1. **Backward validation against Chapter 6** - Verify business elements are supported by Chapter 6 evidence
2. **Drift detection** - Calculate drift percentage using 20% sample (full validation if drift ≥ 5%)
3. **Verify business accuracy** - Do business requirements match actual business policies?
4. **Ensure modernization readiness** - Are requirements clear enough for code generation?
5. **Technology-agnostic verification** - Confirm Chapters 1-5 have no technical jargon

---

## CRITICAL RULES - Artifact Creation

**YOU MUST ONLY CREATE THE EXPLICITLY DEFINED OUTPUT FILES. NO ADDITIONAL ARTIFACTS.**

**Allowed Outputs** (from Output Locations section above):
- Approved specifications (EN): `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN-approved.md`
- Approved specifications (other): `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANG}-approved.md`
- Archived drafts: `{{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-*-draft.md`
- Review report: `{{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md`
- Updated context (if needed): `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-updated.md`
- Updated glossary (if needed): `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- Progress tracking: `{{BUSINESS_SPECIFICATION_STATUS}}`

**FORBIDDEN**:
- ❌ Summary documents (e.g., "phase_3.2.1_summary.md", "specification_review_summary.md")
- ❌ Completion reports (e.g., "phase_X.X_completion.md")
- ❌ Additional review documents beyond those specified
- ❌ Extra markdown files for "documentation purposes"
- ❌ Any file not explicitly listed in "Output Locations" above

**Rationale**: We have defined deliverables, review reports, status tracking, and error logs. Additional summary documents create clutter and redundancy. All necessary information should be captured in the defined outputs.

---

## Instructions

### 1. Preparation and Review Planning
1. Review the list of workpackages requiring review
2. For each workpackage, gather all relevant materials:
   - Business specification (EN and other versions) from Phase 3.2
   - Approved Chapter 6 from Phase 3.1.1
   - Traceability matrix from Phase 3.2
   - Business context document from Phase 3.0.1
   - Business glossary
3. Prioritize review based on workpackage priority
4. Prepare backward validation sampling plan
5. Prepare drift detection checklist

### 2. Backward Validation Protocol

**Purpose**: Validate that business elements in Chapters 1-5 are supported by Chapter 6 evidence

**Sampling Strategy:**
1. **Calculate sample size** (20% of business elements):
   - Count total business entities (BE-XXX)
   - Count total business rules (BR-XXX)
   - Count total business functions (F-XXX)
   - Total elements = entities + rules + functions
   - Sample size = Total elements × 0.20 (round up)

2. **Select sample** (random or stratified):
   - Random: Select elements randomly across all types
   - Stratified: Select 20% from each type (entities, rules, functions)
   - Recommended: Stratified sampling for better coverage

**Validation Process for Each Sampled Element:**

1. **Locate element in Chapters 1-5**:
   - Find BE-XXX, BR-XXX, or F-XXX identifier
   - Read business description

2. **Find Chapter 6 reference**:
   - Check element's "Chapter 6 Reference" field
   - Locate corresponding section in Chapter 6
   - Read technical implementation details

3. **Validate evidence support**:
   - Does Chapter 6 evidence support this business element?
   - Is the abstraction appropriate (allowed patterns only)?
   - Are there drift indicators (forbidden patterns)?

4. **Check for drift indicators**:
   - **Added Functionality**: Does business element include logic not in Chapter 6 code?
   - **Invented Entities**: Does entity exist in Chapter 6 database schema?
   - **Assumed Patterns**: Is business rule actually implemented in Chapter 6 code?
   - **Inappropriate Abstraction**: Is abstraction level appropriate?

5. **Record validation result**:
   - **Pass**: Chapter 6 evidence supports element, appropriate abstraction
   - **Drift**: Evidence doesn't support element or inappropriate abstraction
   - **Missing Evidence**: No Chapter 6 reference or reference not found

**Drift Metrics Calculation:**

1. **Count validation results**:
   - Pass count: [number]
   - Drift count: [number]
   - Missing evidence count: [number]
   - Sample size: [number]

2. **Calculate drift percentage**:
   - Formula: (drift count + missing evidence count) / sample size × 100
   - **Drift %**: [calculated percentage]

3. **Drift assessment**:
   - Drift < 5%: Acceptable, approve
   - Drift 5-10%: Concerning, approve with corrections
   - Drift ≥ 10%: Unacceptable, reject

**Full Validation Trigger:**
- If drift ≥ 5% in sample, perform full validation of ALL elements
- Repeat validation process for 100% of elements
- Recalculate drift percentage
- Use full validation results for approval decision

**Backward Validation Report:**
```markdown
## Backward Validation Results

### Sample Information
- Total Elements: [number]
- Sample Size (20%): [number]
- Sampling Method: [Random / Stratified]

### Validation Results
- Pass: [number] ([X%])
- Drift: [number] ([X%])
- Missing Evidence: [number] ([X%])

### Drift Percentage: [X.X%]

### Drift Assessment: [Acceptable / Concerning / Unacceptable]

### Full Validation Triggered: [Yes / No]
- Reason: [Drift ≥ 5% in sample]

### Drift Examples
1. **Element**: BE-XXX-001 (Customer Email)
   - **Issue**: Entity not found in Chapter 6 database schema
   - **Drift Type**: Invented Entity
   - **Action**: Remove or provide evidence

2. **Element**: BR-XXX-005 (Timezone Handling)
   - **Issue**: Rule includes timezone logic not in Chapter 6 code
   - **Drift Type**: Added Functionality
   - **Action**: Remove or provide evidence
```

### 3. Chapter 1 Review: Introduction and Business Context
1. **Verify business context accuracy**:
   - Does the business domain match actual business organization?
   - Are business stakeholders correctly identified?
   - Is the business problem statement accurate and complete?
   - Does the business value align with organizational priorities?

2. **Check for completeness**:
   - Is the business purpose clearly articulated?
   - Are all relevant stakeholders documented?
   - Is the business context sufficient for understanding requirements?
   - Is the business vocabulary reference appropriate?

3. **Verify readability**:
   - Can a business analyst understand the purpose without technical knowledge?
   - Is the language business-focused (not technical)?
   - Are business terms used consistently?

4. **Review actions**:
   - Add missing stakeholders or business context
   - Clarify business problem statement if unclear
   - Enhance business value articulation
   - Update business vocabulary references

### 3. Chapter 2 Review: Business Entities
1. **Verify business concept level**:
   - Do entities represent real business concepts (Customer, Order) or just cleaned code structures?
   - Are entity names business-meaningful?
   - Do attributes represent business properties?

2. **Check business vocabulary alignment**:
   - Do entity and attribute names match business glossary?
   - Are business terms used consistently?
   - Are there missing business entities?

3. **Verify data type appropriateness**:
   - Are generic data types used (String, Numeric, Date, Timestamp, Boolean)?
   - Are data types appropriate for business concepts (Date for dates, not String)?
   - Are data lengths appropriate ("N/A" for Date/Timestamp/Boolean)?

4. **Check validation rules**:
   - Are validation rules business-focused (not technical constraints)?
   - Are business constraints clearly documented?
   - Are there missing validation rules?

5. **Review actions**:
   - Rename entities/attributes to match business vocabulary
   - Add missing business entities
   - Correct data types to be more business-appropriate
   - Add missing business validation rules
   - Remove technical constraints from entity definitions
   - Update business glossary if new terms identified

### 4. Chapter 3 Review: Business Rules
1. **Verify business policy level**:
   - Do rules represent business policies (would exist in any implementation)?
   - Are rules described in business terms (not code patterns)?
   - Is business rationale clear?

2. **Check for technical rules masquerading as business rules**:
   - Are there rules that are mainframe-specific (batch restart, file locking, CICS timeouts)?
   - Are there technical workarounds documented as business rules?
   - Should any rules be moved to Chapter 6?

3. **Verify rule completeness**:
   - Are all business policies documented?
   - Are there missing business rules?
   - Are business constants included (credit limits, thresholds)?
   - Are business exceptions documented?

4. **Check rule quality**:
   - Is the WHEN/THEN format clear?
   - Is business rationale provided?
   - Are related entities documented?
   - Is exception handling described in business terms?

5. **Verify abstraction level**:
   - Are rules specific enough to be testable?
   - Are rules abstract enough to be implementation-independent?
   - Are rules at the right level (not too concrete, not too abstract)?

6. **Review actions**:
   - Rewrite rules to focus on business policy (not code implementation)
   - Add business rationale where missing
   - Move technical rules to Chapter 6
   - Add missing business rules
   - Clarify business conditions and actions
   - Update business glossary if new terms identified

### 5. Chapter 4 Review: Business Functions
1. **Verify business capability level**:
   - Do functions represent business capabilities (not program subroutines)?
   - Are function names business-meaningful?
   - Are inputs/outputs described in business terms?

2. **Check processing logic**:
   - Is processing described in business terms (not code implementation)?
   - Is business logic clear and complete?
   - Are business rules properly referenced?

3. **Verify function completeness**:
   - Are all business capabilities documented?
   - Are there missing business functions?
   - Are business exceptions documented?

4. **Review actions**:
   - Rename functions to match business capabilities
   - Rewrite processing logic in business terms
   - Add missing business functions
   - Clarify business inputs/outputs
   - Add missing business rule references
   - Update business glossary if new terms identified

### 6. Chapter 5 Review: Process Flows
1. **Verify business process level**:
   - Do flows represent business processes (not program call graphs)?
   - Are activities described in business terms (not program names)?
   - Are decision points business decisions (not IF statements)?

2. **Check business actor alignment**:
   - Do actors match stakeholders from Chapter 1?
   - Are actor roles clearly defined?
   - Are there missing actors?

3. **Verify business outcomes**:
   - Are success/failure outcomes described in business terms?
   - Is business value clearly articulated?
   - Are business metrics included?

4. **Check flow completeness**:
   - Are all business processes documented?
   - Are there missing business activities?
   - Are business decision points clear?

5. **Review actions**:
   - Rewrite flows to focus on business processes
   - Add missing business activities
   - Clarify business decision points
   - Add missing business actors
   - Enhance business outcome descriptions
   - Update business glossary if new terms identified

### 7. Chapter 6 Review: Legacy Implementation References

**Note**: Chapter 6 was already validated in Phase 3.1.1. This review focuses on verifying that Chapter 6 references in Chapters 1-5 are correct and that traceability is complete.

1. **Verify technical completeness**:
   - Are all source files documented?
   - Are code references complete (file names, line numbers)?
   - Are code snippets provided for key implementations?
   - Are database tables fully documented?
   - Are error codes documented?
   - Is technical architecture documented?
   - Is data flow architecture documented?

2. **Check traceability**:
   - Is each business rule traced to legacy implementation?
   - Is each business function traced to legacy code?
   - Are all business entities traced to legacy data structures?
   - Are code references accurate?

3. **Verify modernization guidance**:
   - Is "Legacy Technical Approach" clearly documented?
   - Is "Legacy Reason" provided?
   - Is "Modern Cloud-Native Equivalent" suggested?
   - Is "Migration Guidance" provided?
   - Are "Obsolescence Flags" assigned?

4. **Check technical rule documentation**:
   - Are technical rules (not business rules) documented?
   - Are mainframe-specific constraints documented?
   - Are technical workarounds documented?
   - Are obsolescence flags appropriate?

5. **Review actions**:
   - Add missing code references
   - Enhance modernization guidance
   - Add missing technical details
   - Clarify legacy reasons
   - Update obsolescence flags
   - Move technical rules from Chapter 3 to Chapter 6

### 8. Technology-Agnostic Verification (Chapters 1-5)
1. **Scan for technical jargon**:
   - Search for: COBOL, CICS, JCL, DB2, mainframe, batch, online, transaction, file, record, paragraph, PERFORM, MOVE, CALL, etc.
   - Flag any technical terms found in Chapters 1-5

2. **Verify business language**:
   - Are all concepts described in business terms?
   - Is business vocabulary from glossary used consistently?
   - Can a non-technical business analyst understand Chapters 1-5?

3. **Test implementation independence**:
   - Could these requirements be implemented in Python, Java, or any language?
   - Are requirements free of technical constraints?
   - Is business logic separated from implementation details?

4. **Review actions**:
   - Replace technical jargon with business terms
   - Move technical details to Chapter 6
   - Rewrite sections to be technology-agnostic
   - Update business glossary if needed

### 9. Bilingual Consistency Verification
1. **Verify structural consistency**:
   - Do EN and other versions have same number of chapters?
   - Do EN and other versions have same number of BE-XXX identifiers?
   - Do EN and other versions have same number of BR-XXX identifiers?
   - Do EN and other versions have same number of F-XXX identifiers?

2. **Verify content consistency**:
   - Is business logic identical in EN and other versions?
   - Are business requirements identical?
   - Are Chapter 6 technical details identical?

3. **Verify translation quality**: (if translations exist)
   - Are translations accurate?
   - Is foreign language terminology consistent?
   - Are business terms properly translated?
   - Are technical terms appropriately handled?

4. **Review actions**:
   - Synchronize EN and other versions if inconsistent
   - Correct translation errors
   - Ensure identical business logic
   - Update foreign language terminology if needed

### 10. Overall Specification Review
1. **Verify completeness**:
   - Are all business requirements documented?
   - Are there gaps in business logic?
   - Are all legacy code functions represented?
   - Is traceability complete?

2. **Verify accuracy**:
   - Do business requirements match actual business policies?
   - Are business rules correct?
   - Are business entities accurate?
   - Is business context accurate?

3. **Verify modernization readiness**:
   - Are requirements clear enough for code generation?
   - Is business logic unambiguous?
   - Are business rules testable?
   - Is modernization guidance sufficient?

4. **Identify missing requirements**:
   - What business requirements are not documented?
   - What business rules are missing?
   - What business entities are missing?
   - What business processes are missing?

5. **Identify accidental complexity**:
   - What requirements are legacy technical constraints (not business requirements)?
   - What can be simplified in modern implementation?
   - What is obsolete and no longer needed?

6. **Add business rationale**:
   - Why do these requirements exist?
   - What business value do they provide?
   - What business problems do they solve?

### 11. Review Report Creation
1. **For each workpackage, create a comprehensive review report**:
   - **Section 1: Executive Summary**
     - Overall assessment (Approved / Approved with Changes / Rejected)
     - Drift percentage and assessment
     - Key findings summary
     - Major changes required
     - Approval status and next steps

   - **Section 2: Backward Validation Results**
     - Sample information (size, method)
     - Validation results (pass, drift, missing evidence)
     - Drift percentage calculation
     - Drift assessment (acceptable / concerning / unacceptable)
     - Full validation triggered (yes/no)
     - Drift examples with details

   - **Section 3: Chapter-by-Chapter Review**
     - Chapter 1: Introduction findings and changes
     - Chapter 2: Business Entities findings and changes
     - Chapter 3: Business Rules findings and changes
     - Chapter 4: Business Functions findings and changes
     - Chapter 5: Process Flows findings and changes
     - Chapter 6: Already validated in Phase 3.1.1

   - **Section 4: Cross-Cutting Issues**
     - Technology-agnostic language issues
     - Business vocabulary consistency issues
     - Bilingual consistency issues
     - Traceability issues

   - **Section 5: Missing Requirements**
     - Missing business entities
     - Missing business rules
     - Missing business functions
     - Missing business processes

   - **Section 6: Accidental Complexity**
     - Technical constraints documented as business requirements
     - Legacy workarounds that should be removed
     - Obsolete requirements

   - **Section 7: Business Context Updates**
     - Updates to business domain
     - Updates to business stakeholders
     - Updates to business vocabulary
     - Updates to business glossary

   - **Section 8: Recommendations**
     - Changes required before approval
     - Suggestions for modernization
     - Areas requiring further clarification
     - Risks and mitigation strategies

   - **Section 9: Approval Decision**
     - Approved: Drift < 5%, ready for code generation
     - Approved with Changes: Drift < 5%, minor changes required
     - Rejected: Drift ≥ 5%, return to Phase 3.2 with specific corrections

### 12. Specification Updates and File Management
1. **Apply approved changes to specifications**:
   - Update both EN and other versions
   - Maintain structural consistency
   - Preserve BE-XXX, BR-XXX, F-XXX identifiers
   - Update document version and date

2. **Update business context if needed**:
   - Add missing stakeholders
   - Clarify business domain
   - Enhance business problem statement
   - Update business vocabulary

3. **Update business glossary if needed**:
   - Add new business terms
   - Clarify existing terms
   - Resolve terminology conflicts
   - Ensure consistency across workpackages

4. **Create approved versions and archive drafts**:
   - Create: `WP-XXX-FLOW_XXX-specification-EN-approved.md` (main folder)
   - Create: `WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-approved.md` (main folder)
   - Move: `WP-XXX-FLOW_XXX-specification-EN-draft.md` → `/review/` (archive)
   - Move: `WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-draft.md` → `/review/` (archive)

### 13. Progress Tracking and Approval
1. **Update progress tracking**:
   - Record review completion status
   - Document approval decision
   - Note any changes made
   - Flag any issues requiring escalation

2. **Approval workflow and file management**:
   - **Approved**: 
     - Create approved versions in main folder
     - Move drafts to review folder for audit trail
     - Specification ready for code generation
   - **Approved with Changes**: 
     - Apply changes
     - Create approved versions in main folder
     - Move drafts to review folder for audit trail
     - Ready for code generation
   - **Rejected**: 
     - Keep drafts in main folder
     - Major revision required, return to Phase 3.2 or earlier

3. **Escalation criteria**:
   - Major business requirement gaps
   - Significant business policy misalignment
   - Critical technical implementation issues
   - Unresolvable ambiguities

---

## Output Format

### Review Report
**File**: `{{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md`

**Structure**:
```markdown
# Business Specification Review Report: WP-XXX

## Document Control
- **Workpackage**: WP-XXX
- **Reviewer**: [Name/Role]
- **Review Date**: YYYY-MM-DD
- **Specification Version**: [Version reviewed]
- **Review Status**: Approved / Approved with Changes / Rejected

## 1. Executive Summary
### Overall Assessment
[Approved / Approved with Changes / Rejected]

### Key Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

### Major Changes Required
- [Change 1]
- [Change 2]

### Approval Status
[Approved for code generation / Requires revision / Rejected]

## 2. Chapter-by-Chapter Review

### Chapter 1: Introduction
**Status**: [Approved / Changes Required / Rejected]

**Findings**:
- [Finding 1]
- [Finding 2]

**Changes Made**:
- [Change 1]
- [Change 2]

### Chapter 2: Business Entities
**Status**: [Approved / Changes Required / Rejected]

**Findings**:
- [Finding 1]
- [Finding 2]

**Changes Made**:
- [Change 1]
- [Change 2]

**Missing Entities**:
- [Entity 1]
- [Entity 2]

### Chapter 3: Business Rules
**Status**: [Approved / Changes Required / Rejected]

**Findings**:
- [Finding 1]
- [Finding 2]

**Changes Made**:
- [Change 1]
- [Change 2]

**Missing Rules**:
- [Rule 1]
- [Rule 2]

**Technical Rules Moved to Chapter 6**:
- [Rule 1]
- [Rule 2]

### Chapter 4: Business Functions
**Status**: [Approved / Changes Required / Rejected]

**Findings**:
- [Finding 1]
- [Finding 2]

**Changes Made**:
- [Change 1]
- [Change 2]

**Missing Functions**:
- [Function 1]
- [Function 2]

### Chapter 5: Process Flows
**Status**: [Approved / Changes Required / Rejected]

**Findings**:
- [Finding 1]
- [Finding 2]

**Changes Made**:
- [Change 1]
- [Change 2]

### Chapter 6: Legacy Implementation
**Status**: [Approved / Changes Required / Rejected]

**Note**: Chapter 6 was already validated in Phase 3.1.1. This review focuses on verifying references and traceability.

**Findings**:
- [Finding 1: Traceability issue]
- [Finding 2: Reference accuracy]

**Changes Made**:
- [Change 1: Updated references]
- [Change 2: Fixed traceability links]

**Missing Technical Details**:
- [Detail 1: If any gaps found]
- [Detail 2]

## 3. Cross-Cutting Issues

### Technology-Agnostic Language
**Status**: [Compliant / Issues Found]

**Issues**:
- [Issue 1: Technical jargon found in Chapter X]
- [Issue 2]

**Resolutions**:
- [Resolution 1]
- [Resolution 2]

### Business Vocabulary Consistency
**Status**: [Consistent / Issues Found]

**Issues**:
- [Issue 1]
- [Issue 2]

**Resolutions**:
- [Resolution 1]
- [Resolution 2]

### Bilingual Consistency
**Status**: [Consistent / Issues Found]

**Issues**:
- [Issue 1: EN and other versions have different number of rules]
- [Issue 2]

**Resolutions**:
- [Resolution 1]
- [Resolution 2]

### Traceability
**Status**: [Complete / Issues Found]

**Issues**:
- [Issue 1: Business rule BR-XXX not traced to legacy code]
- [Issue 2]

**Resolutions**:
- [Resolution 1]
- [Resolution 2]

## 4. Missing Requirements

### Missing Business Entities
- [Entity 1]: [Why it's needed]
- [Entity 2]: [Why it's needed]

### Missing Business Rules
- [Rule 1]: [Why it's needed]
- [Rule 2]: [Why it's needed]

### Missing Business Functions
- [Function 1]: [Why it's needed]
- [Function 2]: [Why it's needed]

### Missing Business Processes
- [Process 1]: [Why it's needed]
- [Process 2]: [Why it's needed]

## 5. Accidental Complexity

### Technical Constraints as Business Requirements
- [Constraint 1]: [Why it's accidental complexity]
- [Constraint 2]: [Why it's accidental complexity]

### Legacy Workarounds
- [Workaround 1]: [Why it should be removed]
- [Workaround 2]: [Why it should be removed]

### Obsolete Requirements
- [Requirement 1]: [Why it's obsolete]
- [Requirement 2]: [Why it's obsolete]

## 6. Business Context Updates

### Business Domain Updates
- [Update 1]
- [Update 2]

### Business Stakeholder Updates
- [Update 1]
- [Update 2]

### Business Vocabulary Updates
- [Update 1]
- [Update 2]

### Business Glossary Updates
- [New Term 1]: [Definition]
- [Clarified Term 2]: [Updated definition]

## 7. Recommendations

### Changes Required Before Approval
1. [Change 1]
2. [Change 2]

### Suggestions for Modernization
1. [Suggestion 1]
2. [Suggestion 2]

### Areas Requiring Further Clarification
1. [Area 1]
2. [Area 2]

### Risks and Mitigation Strategies
1. **Risk**: [Risk description]
   **Mitigation**: [Mitigation strategy]

2. **Risk**: [Risk description]
   **Mitigation**: [Mitigation strategy]

## 8. Approval Decision

**Decision**: [Approved / Approved with Changes / Rejected]

**Rationale**: [Explanation of decision]

**Next Steps**:
- [Step 1]
- [Step 2]

**Reviewer Signature**: [Name]
**Date**: YYYY-MM-DD
```

### Approved Specification Documents
**Files**:
- `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-EN-approved.md` (main folder - final deliverable)
- `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-approved.md` (main folder - final deliverable)

**Archived Drafts** (moved to review folder):
- `{{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-EN-draft.md`
- `{{BUSINESS_SPECIFICATION_REVIEW}}/WP-XXX-FLOW_XXX-specification-{LANGUAGE_SHORTCUT}-draft.md`

**Changes from draft**:
- Document version updated
- Review date added
- Approved changes incorporated
- Maintains IEEE 830-1998 format

### Updated Business Context (if needed)
**File**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-updated.md`

### Updated Business Glossary (if needed)
**File**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary-updated.md`

### Progress Tracking
**File**: `{{BUSINESS_SPECIFICATION_STATUS}}`

---

## Quality Criteria

### Business Accuracy
- Business requirements match actual business policies
- Business rules are correct and complete
- Business entities accurately represent business concepts
- Business processes reflect actual workflows

### Completeness
- All business requirements documented
- No gaps in business logic
- All legacy functionality represented
- Traceability complete

### Technology Independence
- Chapters 1-5 free of technical jargon
- Business requirements implementation-independent
- Business logic separated from technical details
- Readable by non-technical business analysts

### Modernization Readiness
- Requirements clear enough for code generation
- Business logic unambiguous
- Business rules testable
- Modernization guidance sufficient

### Bilingual Consistency
- EN and other versions structurally identical
- Business logic identical in both versions
- Translation quality verified
- Terminology consistent

---

## Error Handling

### Common Error Scenarios

1. **Incorrect Business Rules**
   - Detection: Rules don't match actual business policies
   - Recovery: Rewrite rules based on business context and stakeholder input
   - Escalation: Request clarification from business stakeholders

2. **Missing Business Requirements**
   - Detection: Gaps in business logic or functionality
   - Recovery: Identify missing requirements and add to specification
   - Escalation: Return to Phase 3.1 if extensive extraction needed

3. **Technical Jargon in Business Sections**
   - Detection: Technical terms found in Chapters 1-5
   - Recovery: Replace with business terms from glossary
   - Escalation: Return to Phase 3.1 if pervasive throughout your source document. **Bilingual Inconsistency**
   - Detection: EN and other versions have different structure or logic
   - Recovery: Synchronize versions to ensure identical content
   - Escalation: Return to Phase 3.1 if major discrepancies exist

5. **Incomplete Traceability**
   - Detection: Business requirements not traced to legacy code in Chapter 6
   - Recovery: Add missing code references and traceability
   - Escalation: Return to Phase 3.1 if extensive technical analysis needed

6. **Business Context Misalignment**
   - Detection: Specification doesn't match Phase 3.0 business context
   - Recovery: Update specification to align with business context
   - Escalation: Return to Phase 3.0 if business context is fundamentally incorrect

### Error Reporting Format
**File**: `{{BUSINESS_SPECIFICATION_REVIEW}}/business-extraction-WP-XXX-review.md`

**Include errors in Section 2 (Chapter-by-Chapter Review) and Section 3 (Cross-Cutting Issues)**

### Fallback Strategies
- When business accuracy is uncertain, consult Phase 3.0 business context
- When requirements are missing, review source code to identify gaps
- When technical jargon is found, replace with business glossary terms
- When bilingual inconsistency exists, use EN version as source of truth
- When traceability is incomplete, request Phase 3.1 rework
- Prioritize approval with minor changes over rejection when possible
- Flag all critical issues for human escalation

---

## End of Phase 3.2 Document
