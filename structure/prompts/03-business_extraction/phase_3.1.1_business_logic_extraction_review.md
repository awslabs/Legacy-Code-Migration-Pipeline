# Phase 3.1.1: Business Logic Extraction Review

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.1.1 - Business Logic Extraction Review
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_reviewer_logic_extraction
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.1.1_business_logic_extraction_review.md

### Expected Deliverables

1. **Logic Extraction Review Report**
   - File: {{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-logic-extraction-review.md
   - Description: Review findings, drift detection results, and approval decision

2. **Approved Chapter 6 Document**
   - File: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md
   - Description: Validated and approved Chapter 6 with complete technical evidence (final deliverable)

3. **Archived Draft** (moved to review folder)
   - File: {{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-chapter6-draft.md
   - Description: Original draft moved to review folder for audit trail

4. **Drift Detection Report** (if issues found)
   - File: {{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-drift-report.md
   - Description: Detailed analysis of any drift indicators found

5. **Progress Tracking**
   - File: {{BUSINESS_TRACEABILITY_STATUS}}
   - Description: Updated progress tracking with review completion status

### Success Criteria
- [ ] Abstraction patterns validated (allowed patterns only)
- [ ] Drift detection performed (forbidden patterns flagged)
- [ ] Chapter 6 completeness verified
- [ ] Traceability from code to abstractions confirmed
- [ ] Evidence base quality assessed
- [ ] Approval decision documented
- [ ] Ready for Phase 3.2 (Business Specification Generation)

---

## Context

### Input Locations
- **Chapter 6 (draft)**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-draft.md`
- **Logic extraction notes**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md`
- **Business context**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md`
- **Source code files**: `{{SOURCE_CODE}}` (for verification)
- **Database definitions**: `{{DATABASE_SOURCE_CODE}}`

### Output Locations
- **Review report**: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-logic-extraction-review.md`
- **Approved Chapter 6**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md` (main folder - final deliverable)
- **Archived draft**: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-chapter6-draft.md` (moved from main folder)
- **Drift report**: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-drift-report.md` (if needed)
- **Progress tracking**: `{{BUSINESS_TRACEABILITY_STATUS}}`

### Previous Phase Artifacts
- **From Phase 3.1**: Chapter 6 documents, logic extraction notes
- **From Phase 3.0.1**: Approved business context

---

## Objective

Validate logic extraction accuracy and abstraction appropriateness. Ensure all abstractions follow allowed patterns, detect forbidden patterns (drift indicators), verify evidence completeness in Chapter 6, and confirm traceability from code to abstractions. Approve Chapter 6 for Phase 3.2 or return for revision.

**CRITICAL REVIEW PRINCIPLES**:
1. **Verify abstraction appropriateness** - Are abstractions following allowed patterns only?
2. **Detect analysis drift** - Are there forbidden patterns (added functionality, invented entities, assumptions)?
3. **Ensure evidence completeness** - Is Chapter 6 complete with all technical details?
4. **Confirm traceability** - Can every abstraction be traced to code evidence?
5. **Assess quality** - Is the evidence base sufficient for Chapters 1-5 generation?

---

## CRITICAL RULES - Artifact Creation

**YOU MUST ONLY CREATE THE EXPLICITLY DEFINED OUTPUT FILES. NO ADDITIONAL ARTIFACTS.**

**Allowed Outputs** (from Output Locations section above):
- Review report: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-logic-extraction-review.md`
- Approved Chapter 6: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md`
- Archived draft: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-chapter6-draft.md`
- Drift report (if needed): `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-drift-report.md`
- Progress tracking: `{{BUSINESS_TRACEABILITY_STATUS}}`

**FORBIDDEN**:
- ❌ Summary documents (e.g., "phase_3.1.1_summary.md", "logic_review_summary.md")
- ❌ Completion reports (e.g., "phase_X.X_completion.md")
- ❌ Additional review documents beyond those specified
- ❌ Extra markdown files for "documentation purposes"
- ❌ Any file not explicitly listed in "Output Locations" above

**Rationale**: We have defined deliverables, review reports, status tracking, and error logs. Additional summary documents create clutter and redundancy. All necessary information should be captured in the defined outputs.

---

## Instructions

### 1. Preparation and Review Planning
1. Review Chapter 6 document for the workpackage
2. Review logic extraction notes
3. Review approved business context from Phase 3.0.1
4. Prepare drift detection checklist
5. Prepare abstraction validation checklist

### 2. Abstraction Pattern Validation

#### Allowed Patterns (Should Be Present)
Review each abstraction and verify it follows one of these allowed patterns:

1. **DATA_TYPE Abstraction**
   - Example: PIC X(8) date field → Date type
   - Validation: Is the abstraction appropriate for the data's business purpose?
   - Evidence: Does Chapter 6 show the original COBOL data type?

2. **CONSOLIDATION Abstraction**
   - Example: 8 separate validation steps → "must be valid date"
   - Validation: Does the consolidation preserve business intent?
   - Evidence: Does Chapter 6 document all consolidated steps?

3. **NAMING Abstraction**
   - Example: CUST-REC → Customer, WS-ORDER-AMT → orderTotal
   - Validation: Does the business name match the glossary?
   - Evidence: Does Chapter 6 show the original technical name?

4. **STRUCTURE Abstraction**
   - Example: Flat COBOL records → normalized business entities
   - Validation: Does the structure reflect business relationships?
   - Evidence: Does Chapter 6 document the original structure?

5. **LOGIC Abstraction**
   - Example: Code patterns → business intent
   - Validation: Does the abstraction capture business logic accurately?
   - Evidence: Does Chapter 6 include code snippets showing the pattern?

6. **PROCESS Abstraction**
   - Example: Call graphs → business workflows
   - Validation: Does the workflow reflect business process?
   - Evidence: Does Chapter 6 document the technical call sequence?

**For each abstraction found:**
- Identify which allowed pattern it follows
- Verify evidence exists in Chapter 6
- Confirm appropriateness of the abstraction
- Document in review report

### 3. Drift Detection (Forbidden Patterns)

#### Forbidden Patterns (Should NOT Be Present)
Scan for these drift indicators:

1. **Added Functionality**
   - Example: Adding timezone handling when code only validates date format
   - Detection: Compare abstractions to code evidence in Chapter 6
   - Action: Flag as drift, require removal or evidence

2. **Invented Entities**
   - Example: Adding email field when database has no email column
   - Detection: Cross-reference entities with database schema in Chapter 6
   - Action: Flag as drift, require removal or evidence

3. **Assumed Standard Patterns**
   - Example: Assuming fiscal year logic when code only uses calendar dates
   - Detection: Verify each business rule has code evidence in Chapter 6
   - Action: Flag as drift, require removal or evidence

4. **Extrapolation Beyond Evidence**
   - Example: Inferring business rules not actually implemented
   - Detection: Check that every abstraction traces to specific code
   - Action: Flag as drift, require removal or evidence

**Drift Detection Process:**
1. For each abstraction, locate supporting evidence in Chapter 6
2. If no evidence found, flag as potential drift
3. Verify the abstraction doesn't add functionality beyond code
4. Check database schema for entity/attribute existence
5. Confirm business rules are actually implemented
6. Document all drift indicators in drift report

### 4. Chapter 6 Completeness Verification

#### Section 6.1: Source Files
- [ ] All source files listed (programs, copybooks, JCL, maps)
- [ ] File paths provided
- [ ] File types and purposes documented

#### Section 6.2: Business Rule Implementation
For each business rule abstraction:
- [ ] Legacy technical approach documented
- [ ] Code references include file names and line numbers
- [ ] Code snippets provided
- [ ] Legacy reason explained
- [ ] Technical constants documented
- [ ] Modern equivalent suggested
- [ ] Migration guidance provided
- [ ] Obsolescence flag assigned

#### Section 6.3: Function Implementation
For each business function abstraction:
- [ ] Legacy technical approach documented
- [ ] Code references complete
- [ ] Code snippets provided
- [ ] Technical parameters documented
- [ ] Legacy reason explained
- [ ] Modern equivalent suggested
- [ ] Migration guidance provided
- [ ] Obsolescence flag assigned

#### Section 6.4: Database Tables
- [ ] All accessed tables documented
- [ ] Table types identified (Internal/Common/External)
- [ ] Columns listed with data types
- [ ] Access patterns documented
- [ ] Code references provided
- [ ] Modern equivalent suggested

#### Section 6.5: Error Codes
- [ ] Error sets documented
- [ ] Treatment codes documented
- [ ] Custom error codes listed
- [ ] Code references provided
- [ ] Modern equivalent suggested

#### Section 6.6: Technical Architecture
- [ ] BC Layer documented
- [ ] SQLIO Layer documented
- [ ] BATCH Layer documented
- [ ] Framework components documented
- [ ] Code references provided
- [ ] Modern equivalents suggested

#### Section 6.7: Data Flow Architecture
- [ ] Input mechanisms documented
- [ ] Database access documented
- [ ] Service calls documented
- [ ] Output mechanisms documented
- [ ] Error handling documented
- [ ] Code references provided
- [ ] Modern equivalents suggested

#### Section 6.8: Technical Rules
- [ ] Technical rules (not business rules) documented
- [ ] Code references provided
- [ ] Legacy reasons explained
- [ ] Obsolescence flags assigned

**Completeness Assessment:**
- Calculate completeness percentage: (completed items / total items) × 100
- Flag missing sections
- Identify gaps in code references
- Note missing technical details

### 5. Traceability Verification

**Forward Traceability (Code → Abstractions):**
1. Select sample of code sections from Chapter 6
2. Verify each has corresponding abstraction
3. Confirm abstraction accurately represents code
4. Document any code not abstracted

**Backward Traceability (Abstractions → Code):**
1. Select sample of abstractions from logic notes
2. Verify each has code evidence in Chapter 6
3. Confirm code evidence supports abstraction
4. Document any abstractions without evidence

**Traceability Metrics:**
- Forward traceability: (code sections with abstractions / total code sections) × 100
- Backward traceability: (abstractions with evidence / total abstractions) × 100
- Target: Both metrics ≥ 95%

### 6. Evidence Base Quality Assessment

**Quality Criteria:**
1. **Specificity**: Are code references specific (file names, line numbers)?
2. **Completeness**: Are code snippets complete enough to understand logic?
3. **Clarity**: Are technical details clearly documented?
4. **Accuracy**: Do code references match actual source code?
5. **Sufficiency**: Is there enough detail for Phase 3.2 to create Chapters 1-5?

**Quality Score:**
- Excellent (90-100%): Ready for Phase 3.2
- Good (75-89%): Minor improvements needed
- Fair (60-74%): Moderate improvements needed
- Poor (<60%): Major rework required

### 7. Drift Metrics Calculation

**Drift Indicators Count:**
- Added functionality count: [number]
- Invented entities count: [number]
- Assumed patterns count: [number]
- Extrapolations count: [number]
- **Total drift indicators**: [sum]

**Abstraction Count:**
- Total abstractions: [number]
- Appropriate abstractions: [number]

**Drift Percentage:**
- Formula: (total drift indicators / total abstractions) × 100
- **Drift %**: [calculated percentage]

**Drift Assessment:**
- Drift < 5%: Acceptable, approve
- Drift 5-10%: Concerning, approve with corrections
- Drift > 10%: Unacceptable, reject and return to Phase 3.1

### 8. Review Report Creation

**Structure:**
```markdown
# Logic Extraction Review Report: WP-XXX

## Review Summary
- **Reviewer**: [Name/Role]
- **Review Date**: YYYY-MM-DD
- **Decision**: Approved / Approved with Changes / Rejected
- **Drift Percentage**: [X.X%]

## Abstraction Pattern Validation
### Allowed Patterns Found
- DATA_TYPE: [count] - [status]
- CONSOLIDATION: [count] - [status]
- NAMING: [count] - [status]
- STRUCTURE: [count] - [status]
- LOGIC: [count] - [status]
- PROCESS: [count] - [status]

### Validation Results
- [List findings for each pattern type]

## Drift Detection Results
### Drift Indicators Found
- Added Functionality: [count]
  - [List specific examples]
- Invented Entities: [count]
  - [List specific examples]
- Assumed Patterns: [count]
  - [List specific examples]
- Extrapolations: [count]
  - [List specific examples]

### Drift Metrics
- Total Abstractions: [number]
- Drift Indicators: [number]
- Drift Percentage: [X.X%]
- Assessment: [Acceptable / Concerning / Unacceptable]

## Chapter 6 Completeness
### Completeness by Section
- Section 6.1 (Source Files): [X%]
- Section 6.2 (Business Rules): [X%]
- Section 6.3 (Functions): [X%]
- Section 6.4 (Database Tables): [X%]
- Section 6.5 (Error Codes): [X%]
- Section 6.6 (Technical Architecture): [X%]
- Section 6.7 (Data Flow): [X%]
- Section 6.8 (Technical Rules): [X%]

### Overall Completeness: [X%]

### Missing Elements
- [List missing sections or details]

## Traceability Verification
- Forward Traceability: [X%]
- Backward Traceability: [X%]
- Traceability Issues: [List any issues]

## Evidence Base Quality
- Quality Score: [X%]
- Assessment: [Excellent / Good / Fair / Poor]
- Quality Issues: [List any issues]

## Required Changes
1. [Change 1]
2. [Change 2]
3. [Change 3]

## Approval Decision
- **Decision**: [Approved / Approved with Changes / Rejected]
- **Rationale**: [Explanation]
- **Next Steps**: [What happens next]
```

### 9. Approval Decision and File Management

**Approved:**
- Drift < 5%
- Completeness ≥ 90%
- Traceability ≥ 95%
- Quality score ≥ 75%
- **Actions**:
  - Create approved version in main folder: `chapter6-approved.md`
  - Move draft to review folder: `/review/chapter6-draft.md`
  - Ready for Phase 3.2

**Approved with Changes:**
- Drift 5-10% with specific corrections identified
- Completeness 75-89% with minor gaps
- Traceability 85-94% with minor issues
- Quality score 60-74%
- **Actions**:
  - Apply corrections to draft
  - Create approved version in main folder: `chapter6-approved.md`
  - Move original draft to review folder: `/review/chapter6-draft.md`
  - Can proceed to Phase 3.2 after corrections

**Rejected:**
- Drift > 10%
- Completeness < 75%
- Traceability < 85%
- Quality score < 60%
- **Actions**:
  - Keep draft in main folder
  - Return to Phase 3.1 with detailed feedback

### 10. Progress Tracking
- Update progress tracking with review completion
- Document approval decision
- Note any changes made
- Flag any issues requiring escalation

---

## Output Format

### Logic Extraction Review Report
**File**: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-logic-extraction-review.md`

### Drift Detection Report (if drift found)
**File**: `{{BUSINESS_TRACEABILITY_REVIEW}}/WP-XXX-FLOW_XXX-drift-report.md`

**Structure**:
```markdown
# Drift Detection Report: WP-XXX

## Drift Summary
- Total Drift Indicators: [number]
- Drift Percentage: [X.X%]
- Severity: [Low / Medium / High]

## Drift Details
### Added Functionality
1. **Abstraction**: [description]
   - **Evidence**: [what code shows]
   - **Drift**: [what was added]
   - **Action**: [remove or provide evidence]

### Invented Entities
1. **Entity**: [name]
   - **Database Check**: [not found in schema]
   - **Action**: [remove or provide evidence]

### Assumed Patterns
1. **Assumption**: [description]
   - **Evidence**: [what code actually shows]
   - **Action**: [remove or provide evidence]

### Extrapolations
1. **Extrapolation**: [description]
   - **Evidence**: [what code actually shows]
   - **Action**: [remove or provide evidence]

## Recommendations
- [List recommendations for Phase 3.1 rework]
```

### Approved Chapter 6 (if changes made)
**File**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md`

---

## Quality Criteria

### Abstraction Appropriateness
- All abstractions follow allowed patterns
- No forbidden patterns present
- Abstractions preserve business intent
- Abstractions are evidence-based

### Drift Control
- Drift percentage < 5% (acceptable)
- No added functionality without evidence
- No invented entities without database proof
- No assumed patterns without code proof
- No extrapolations beyond code

### Evidence Completeness
- All Chapter 6 sections complete
- Code references specific and accurate
- Code snippets provided for key logic
- Technical details comprehensive
- Sufficient for Phase 3.2 generation

### Traceability
- Forward traceability ≥ 95%
- Backward traceability ≥ 95%
- Every abstraction has code evidence
- Every code section has abstraction

### Quality
- Quality score ≥ 75%
- Code references specific
- Technical details clear
- Documentation sufficient

---

## Error Handling

### Common Error Scenarios

1. **High Drift Percentage (> 10%)**
   - Detection: Drift metrics calculation shows > 10%
   - Recovery: Reject and return to Phase 3.1 with detailed drift report
   - Escalation: If repeated, escalate to human supervisor

2. **Incomplete Chapter 6**
   - Detection: Completeness < 75%
   - Recovery: Identify missing sections and return to Phase 3.1
   - Escalation: If critical sections missing, escalate

3. **Poor Traceability**
   - Detection: Traceability < 85%
   - Recovery: Identify traceability gaps and return to Phase 3.1
   - Escalation: If systematic traceability issues, escalate

4. **Invented Entities**
   - Detection: Entity not found in database schema
   - Recovery: Flag as drift, require removal or evidence
   - Escalation: If multiple invented entities, reject

5. **Added Functionality**
   - Detection: Abstraction includes logic not in code
   - Recovery: Flag as drift, require removal or evidence
   - Escalation: If systematic additions, reject

---

## End of Phase 3.1.1 Document
