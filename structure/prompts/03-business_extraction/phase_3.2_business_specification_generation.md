# Phase 3.2: Business Specification Generation

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.2 - Business Specification Generation
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_requirements
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.2_business_specification_generation.md

### Expected Deliverables

1. **Business Specification Document (Chapters 1-5) - Draft**
   - File: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-draft.md
   - Template: {{BUSINESS_SPECIFICATION_TEMPLATE}}
   - Description: IEEE 830-1998 formatted business specifications (Chapters 1-5 only, Chapter 6 already approved from Phase 3.1.1) - draft for review

2. **Traceability Matrix**
   - File: {{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md
   - Description: Mapping of business elements (Chapters 1-5) to Chapter 6 evidence

3. **Progress Tracking**
   - File: {{BUSINESS_SPECIFICATION_STATUS}}
   - Description: Updated progress tracking

### Success Criteria
- [ ] Chapters 1-5 created using approved Chapter 6 as evidence base
- [ ] All business entities extracted at business concept level
- [ ] All business rules represent business policies (not code patterns)
- [ ] All business functions represent business capabilities
- [ ] All business processes use business terminology
- [ ] Technology-agnostic language in Chapters 1-5 (no technical jargon)
- [ ] Every business element traces to Chapter 6 evidence
- [ ] Traceability matrix complete
- [ ] Ready for Phase 3.2.1 review

---

## Context

### Input Locations
- **Approved Chapter 6**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md`
- **Approved business context**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context-approved.md`
- **Business glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- **Logic extraction notes**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-logic-notes.md`

### Output Locations
- **Business specification - draft**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-draft.md`
- **Traceability matrix**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md`
- **Progress tracking**: `{{BUSINESS_SPECIFICATION_STATUS}}`

### Template Locations
- **Business specification template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`

### Previous Phase Artifacts
- **From Phase 3.1.1**: Approved Chapter 6, logic extraction review
- **From Phase 3.0.1**: Approved business context, business glossary

---

## Objective

Create business specification (Chapters 1-5) using approved Chapter 6 as evidence base. Transform technical implementation details into technology-agnostic business requirements while maintaining complete traceability. Use approved abstractions from Phase 3.1.1 and business vocabulary from Phase 3.0.1.

**CRITICAL PRINCIPLES**:
1. **Evidence-based specification** - Every business element must reference Chapter 6 evidence
2. **Use approved abstractions** - Apply only abstractions validated in Phase 3.1.1
3. **Business vocabulary** - Use terms from approved business glossary
4. **Technology-agnostic** - No technical jargon in Chapters 1-5
5. **Complete traceability** - Maintain explicit links to Chapter 6

---

## CRITICAL RULES - Artifact Creation

**YOU MUST ONLY CREATE THE EXPLICITLY DEFINED OUTPUT FILES. NO ADDITIONAL ARTIFACTS.**

**Allowed Outputs** (from Output Locations section above):
- Business specification - draft: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-draft.md`
- Traceability matrix: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md`
- Progress tracking: `{{BUSINESS_SPECIFICATION_STATUS}}`
- Error logs (if errors occur): `{{BUSINESS_SPECIFICATION_ERRORS}}`

**FORBIDDEN**:
- ❌ Summary documents (e.g., "phase_3.2_summary.md", "specification_generation_summary.md")
- ❌ Completion reports (e.g., "phase_X.X_completion.md")
- ❌ Additional review documents beyond those specified
- ❌ Extra markdown files for "documentation purposes"
- ❌ Any file not explicitly listed in "Output Locations" above

**Rationale**: We have defined deliverables, review reports, status tracking, and error logs. Additional summary documents create clutter and redundancy. All necessary information should be captured in the defined outputs.

---

## Instructions

### 1. Preparation
1. Review approved Chapter 6 document
2. Review approved business context from Phase 3.0.1
3. Review business glossary
4. Review logic extraction notes and approved abstractions
5. Prepare traceability tracking

### 2. Chapter 1: Introduction (Enhanced with Business Context)

**Source**: Use approved business context from Phase 3.0.1

#### Section 1.1: Purpose
- **Business Domain**: [From Phase 3.0.1 business context]
- **Business Problem Statement**: [From Phase 3.0.1 business context - explain the business problem this solves]
- **Business Value**: [From Phase 3.0.1 business context - list specific business benefits]
- **Confidence Level**: [From Phase 3.0.1 business context]

**Business Context Summary** (NEW):
- Provide a 2-3 sentence summary of the business context from Phase 3.0.1
- Explain why this functionality is important to the business
- Reference key stakeholders and their needs

#### Section 1.2: Scope
- **Business Stakeholders**: [From Phase 3.0.1 business context]
  - Primary Users: [Who directly uses this functionality]
  - Business Owners: [Who owns the business process]
  - Other Stakeholders: [Who else is impacted]
- **Business Processes Covered**: [Identify from Chapter 6 process flows]
- **Business Boundaries**:
  - Included: [What's in scope based on Chapter 6]
  - Excluded: [What's out of scope]

#### Section 1.3: Business Context
- **Why This Functionality Exists**: [From Phase 3.0.1 business context - explain the business need]
- **Business Constraints and Policies**: [High-level from Phase 3.0.1]
- **Business Vocabulary Reference**: See consolidated business glossary at [link to glossary file]

**Quality Check:**
- [ ] Uses business vocabulary from glossary
- [ ] No technical jargon
- [ ] Readable by business analysts
- [ ] References business context from Phase 3.0.1

### 3. Chapter 2: Business Entities (Business Concept Level)

**Source**: Transform Chapter 6 data structures using approved abstractions

**For each data structure in Chapter 6:**

1. **Apply NAMING abstraction**:
   - Technical name (Chapter 6): CUST-REC, WS-ORDER-AMT
   - Business name (Chapter 2): Customer, orderTotal
   - Use business glossary terms

2. **Apply DATA_TYPE abstraction**:
   - Technical type (Chapter 6): PIC X(8), PIC 9(7)V99
   - Business type (Chapter 2): Date, Numeric
   - Use generic types: String, Numeric, Date, Timestamp, Boolean

3. **Apply STRUCTURE abstraction**:
   - Technical structure (Chapter 6): Flat COBOL records
   - Business structure (Chapter 2): Normalized entities with relationships

4. **Extract business validation rules**:
   - Source: Chapter 6 validation logic
   - Transform: Technical constraints → Business rules
   - Example: "Field length 8" → "Must be valid date"

**Entity Format:**
```markdown
### BE-XXX-001: [Business Entity Name]

**Business Description**: [What business concept this represents]

**Attributes**:

| Attribute Name (camelCase) | Data Type | Length | Business Validation Rules | Legacy Variable Name |
|---------------------------|-----------|--------|---------------------------|---------------------|
| [attributeName] | [String/Numeric/Date/Timestamp/Boolean] | [length or N/A] | [Business rules] | [LEGACY-VAR] |

**Business Relationships**:
- [Relationship to other entities in business terms]

**Business Constraints**:
- [Business constraints - not technical]

**Database Alignment**: [Reference to Chapter 6 Section 6.4 table]

**Chapter 6 Reference**: [Section 6.2 or 6.3]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-62) [specific reference with markdown link]
```

**Traceability:**
- For each entity, document Chapter 6 reference
- Link to specific Section 6.4 database table
- Link to Section 6.2/6.3 implementation details

**Quality Check:**
- [ ] Entity names use business vocabulary
- [ ] Generic data types used
- [ ] Business validation rules (not technical constraints)
- [ ] Every entity traces to Chapter 6
- [ ] No technical jargon

### 4. Chapter 3: Business Rules (Business Policy Level)

**Source**: Transform Chapter 6 business rule implementations using approved abstractions

**For each business rule in Chapter 6 Section 6.2:**

1. **Apply LOGIC abstraction**:
   - Technical logic (Chapter 6): IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT
   - Business logic (Chapter 3): Orders must not exceed customer credit limits

2. **Apply CONSOLIDATION abstraction**:
   - Technical steps (Chapter 6): 8 separate validation steps
   - Business rule (Chapter 3): "Must be valid date"

3. **Extract business rationale**:
   - Source: Chapter 6 comments, legacy reason
   - Transform: Technical explanation → Business rationale
   - **Provide rich rationale**: Explain business impact, regulatory requirements, risk mitigation, operational efficiency, etc.
   - Example: "Unique user IDs prevent authentication conflicts, ensure proper audit trails, and support regulatory compliance for access control"

**Rule Format:**
```markdown
### BR-XXX-001: [Business Rule Name]

**WHEN**: [Business condition in business terms]

**THEN**: [Business action in business terms]

**RATIONALE**: [Why this rule exists - business reason with rich detail]
- Explain business impact (e.g., prevents fraud, ensures data integrity)
- Explain regulatory requirements (e.g., compliance with financial regulations)
- Explain operational benefits (e.g., reduces support calls, improves efficiency)
- Explain risk mitigation (e.g., prevents security breaches, protects customer data)

**RELATED ENTITIES**: [Business entities involved - use BE-XXX identifiers]

**EXCEPTION HANDLING**: [Business exceptions in business terms]

**BUSINESS CONSTANTS**: [Credit limits, thresholds - not technical constants]

**Chapter 6 Reference**: [Section 6.2 BR-XXX-001]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-62-br-xxx-001) [specific reference with markdown link]
```

**Important:**
- Only include business rules (would exist in any implementation)
- Technical rules stay in Chapter 6 Section 6.8
- Use business vocabulary from glossary
- Provide business rationale

**Traceability:**
- For each rule, document Chapter 6 Section 6.2 reference
- Link to specific code snippets
- Link to related entities (BE-XXX)

**Quality Check:**
- [ ] Rules represent business policies
- [ ] WHEN/THEN format clear
- [ ] Business rationale provided
- [ ] Every rule traces to Chapter 6
- [ ] No code patterns or technical jargon

### 5. Chapter 4: Business Functions (Business Capability Level)

**Source**: Transform Chapter 6 function implementations using approved abstractions

**For each function in Chapter 6 Section 6.3:**

1. **Apply NAMING abstraction**:
   - Technical name (Chapter 6): VALIDATE-CREDIT paragraph
   - Business name (Chapter 4): Validate Customer Credit Eligibility

2. **Apply LOGIC abstraction**:
   - Technical processing (Chapter 6): COBOL paragraph logic
   - Business processing (Chapter 4): Business operations description

3. **Transform inputs/outputs**:
   - Technical parameters (Chapter 6): WS-CREDIT-LIM, WS-ORDER-AMT
   - Business inputs/outputs (Chapter 4): Customer credit limit, Order total

**Function Format:**
```markdown
### F-XXX-001: [Business Function Name]

**PURPOSE**: [What business capability this provides]

**BUSINESS INPUTS**: [Business information required - not technical parameters]

**BUSINESS OUTPUTS**: [Business information produced - not technical return codes]

**BUSINESS PROCESSING**: [Business operations performed - in business terms]

**BUSINESS RULES APPLIED**: [List of BR-XXX identifiers]

**RELATED ENTITIES**: [Business entities involved - use BE-XXX identifiers]

**BUSINESS EXCEPTIONS**: [Business error conditions in business terms]

**Chapter 6 Reference**: [Section 6.3 F-XXX-001]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-63-f-xxx-001) [specific reference with markdown link]
```

**Traceability:**
- For each function, document Chapter 6 Section 6.3 reference
- Link to business rules applied (BR-XXX)
- Link to related entities (BE-XXX)

**Quality Check:**
- [ ] Function names use business vocabulary
- [ ] Inputs/outputs in business terms
- [ ] Processing logic in business terms
- [ ] Every function traces to Chapter 6
- [ ] No technical jargon

### 6. Chapter 5: Process Flows (Business Process Level)

**Source**: Transform Chapter 6 data flow architecture using approved abstractions

**For each process flow in Chapter 6 Section 6.7:**

1. **Apply PROCESS abstraction**:
   - Technical flow (Chapter 6): Program call graph, PERFORM sequences
   - Business flow (Chapter 5): Business process with activities

2. **Apply NAMING abstraction**:
   - Technical activities (Chapter 6): Program names, paragraph names
   - Business activities (Chapter 5): Business operations

3. **Transform decision points**:
   - Technical decisions (Chapter 6): IF statements, condition codes
   - Business decisions (Chapter 5): Business decision points

**Process Format:**
```markdown
### Process: [Business Process Name]

**Trigger**: [Business event that starts the process]

**Activities**:

1. **[Business Activity 1]** - Performed by [Business Actor from Phase 3.0.1]
   - **Decision Point**: [Business decision if applicable]
     - If [business condition]: [business action]
     - If [business condition]: [business action]
   - **Uses**: [Business entities/functions - use BE-XXX, F-XXX identifiers]

2. **[Business Activity 2]** - Performed by [Business Actor]
   - **Uses**: [Business entities/functions]
   - **Produces**: [Business outputs]

3. **[Business Activity 3]** - Performed by [Business Actor]

**Outcomes**:
- **Success**: [Business outcome when successful]
- **Failure**: [Business outcome when failed]

**Business Value**: [What business value this process delivers]

**Chapter 6 Reference**: [Section 6.7]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-67) [specific reference with markdown link]
```

**Traceability:**
- For each process, document Chapter 6 Section 6.7 reference
- Link to business functions used (F-XXX)
- Link to business entities used (BE-XXX)
- Link to business actors from Phase 3.0.1

**Quality Check:**
- [ ] Process names use business vocabulary
- [ ] Activities in business terms
- [ ] Decision points are business decisions
- [ ] Actors are business roles
- [ ] Every process traces to Chapter 6
- [ ] No technical jargon

### 7. Traceability Matrix Creation

**Create comprehensive traceability matrix:**

**File**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md`

**Purpose**: Provide complete mapping between business elements (Chapters 1-5) and technical evidence (Chapter 6)

```markdown
# Traceability Matrix: WP-XXX-FLOW_XXX

## Document Control
**Workpackage ID**: WP-XXX
**Flow ID**: FLOW_XXX
**Version**: 1.0
**Date**: [Date]
**Status**: Draft

## Overview
This traceability matrix maps all business elements in Chapters 1-5 to their corresponding technical implementation details in Chapter 6, ensuring complete evidence-based specification.

## Business Entities → Chapter 6
| Entity ID | Entity Name | Chapter 6 Reference | Database Table | Code Reference |
|-----------|-------------|---------------------|----------------|----------------|
| BE-XXX-001 | Customer | [Section 6.4, Table CUSTOMER]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-64) | CUSTOMER | CUST-REC |
| BE-XXX-002 | Order | [Section 6.4, Table ORDER]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-64) | ORDER | ORD-REC |

## Business Rules → Chapter 6
| Rule ID | Rule Name | Chapter 6 Reference | Code File | Line Numbers |
|---------|-----------|---------------------|-----------|--------------|
| BR-XXX-001 | Credit Limit Validation | [Section 6.2 BR-XXX-001]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-62-br-xxx-001) | ORDVAL.cbl | 150-175 |
| BR-XXX-002 | Date Validation | [Section 6.2 BR-XXX-002]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-62-br-xxx-002) | DATEUTIL.cbl | 200-250 |

## Business Functions → Chapter 6
| Function ID | Function Name | Chapter 6 Reference | Code File | Paragraph/Section |
|-------------|---------------|---------------------|-----------|-------------------|
| F-XXX-001 | Validate Credit | [Section 6.3 F-XXX-001]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-63-f-xxx-001) | ORDVAL.cbl | VALIDATE-CREDIT |
| F-XXX-002 | Process Payment | [Section 6.3 F-XXX-002]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-63-f-xxx-002) | PAYMENT.cbl | PROCESS-PMT |

## Business Processes → Chapter 6
| Process Name | Chapter 6 Reference | Functions Used | Entities Used |
|--------------|---------------------|----------------|---------------|
| Order Validation | [Section 6.7]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-67) | F-XXX-001, F-XXX-002 | BE-XXX-001, BE-XXX-002 |

## Traceability Statistics
- Total Business Entities: [count]
- Total Business Rules: [count]
- Total Business Functions: [count]
- Total Business Processes: [count]
- Traceability Coverage: 100% (all elements trace to Chapter 6)

## Validation Notes
- All business elements have been validated against Chapter 6 evidence
- All abstractions follow approved patterns from Phase 3.1.1
- All references use markdown links for easy navigation
```

**Important**: 
- Use markdown links for all Chapter 6 references
- Format: `[Section 6.X](path/to/chapter6.md#section-6x)`
- Ensure all links are valid and navigable

### 8. Technology-Agnostic Verification

**Scan Chapters 1-5 for technical jargon:**
- Search for: COBOL, CICS, JCL, DB2, mainframe, batch, online, transaction, file, record, paragraph, PERFORM, MOVE, CALL, PIC, COMP, WORKING-STORAGE, etc.
- Replace any found with business terms from glossary
- Move technical details to Chapter 6 if needed

**Verification Checklist:**
- [ ] No COBOL-specific terms
- [ ] No mainframe-specific terms
- [ ] No technical implementation details
- [ ] All business vocabulary from glossary
- [ ] Readable by non-technical business analysts

### 9. Final Assembly

**Combine all chapters into complete specification:**

1. **Document Control Section**:
   - Document Type: Business Specification (IEEE 830-1998)
   - Workpackage ID, Flow ID
   - Version, Date
   - Status: Draft
   - Author, Confidence Level

2. **Chapter 1**: Introduction (from business context)
3. **Chapter 2**: Business Entities (from Chapter 6 data structures)
4. **Chapter 3**: Business Rules (from Chapter 6 business rules)
5. **Chapter 4**: Business Functions (from Chapter 6 functions)
6. **Chapter 5**: Process Flows (from Chapter 6 data flows)
7. **Chapter 6**: Legacy Implementation References
   - **Note**: Chapter 6 already exists from Phase 3.1 and is referenced via markdown link
   - **Reference**: See [Chapter 6: Legacy Implementation References]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md) for complete technical implementation details
   - **Do not duplicate**: Chapter 6 content should NOT be copied into this document
   - **Link format**: Use markdown links for all Chapter 6 references throughout the document

**Final Quality Check:**
- [ ] All chapters present
- [ ] IEEE 830-1998 format followed
- [ ] Technology-agnostic (Chapters 1-5)
- [ ] Complete traceability to Chapter 6
- [ ] Ready for Phase 3.2.1 review

### 10. Progress Tracking
- Update progress tracking with completion status
- Document any issues encountered
- Note confidence levels
- Flag areas requiring review attention

---

## Output Format

### Business Specification Document - Draft
**File**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-FLOW_XXX-specification-draft.md`
**Template**: `{{BUSINESS_SPECIFICATION_TEMPLATE}}`
**Note**: This is a draft version that will be reviewed in Phase 3.2.1

**Structure**:
- Document Control
- Chapter 1: Introduction (enhanced with business context from Phase 3.0.1)
- Chapter 2: Business Entities (with markdown links to Chapter 6)
- Chapter 3: Business Rules (with markdown links to Chapter 6)
- Chapter 4: Business Functions (with markdown links to Chapter 6)
- Chapter 5: Process Flows (with markdown links to Chapter 6)
- Chapter 6: Legacy Implementation References (markdown link to separate file from Phase 3.1)

**Markdown Link Format**:
- Chapter 6 references: `[Section 6.X]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-chapter6-approved.md#section-6x)` (note: Chapter 6 is in traceability folder)
- Business glossary: `[Business Glossary]({{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md)`
- Traceability matrix: `[Traceability Matrix]({{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md)`

### Traceability Matrix
**File**: `{{BUSINESS_TRACEABILITY_BASE_PATH}}/WP-XXX-FLOW_XXX-traceability-matrix.md`

---

## Quality Criteria

### Evidence-Based Specification
- Every business entity traces to Chapter 6
- Every business rule traces to Chapter 6
- Every business function traces to Chapter 6
- Every business process traces to Chapter 6
- Traceability matrix complete

### Abstraction Quality
- Uses only approved abstractions from Phase 3.1.1
- Follows allowed patterns (DATA_TYPE, CONSOLIDATION, NAMING, STRUCTURE, LOGIC, PROCESS)
- No forbidden patterns (added functionality, invented entities, assumptions)

### Business Vocabulary
- Uses terms from approved business glossary
- Consistent terminology throughout
- Business-meaningful names

### Technology Independence
- No technical jargon in Chapters 1-5
- Business requirements implementation-independent
- Readable by non-technical business analysts

### Traceability
- Complete traceability matrix
- Every business element references Chapter 6
- Clear links between chapters

---

## Error Handling

### Common Error Scenarios

1. **Missing Chapter 6 Evidence**
   - Detection: Business element has no Chapter 6 reference
   - Recovery: Review Chapter 6 to find evidence or remove element
   - Escalation: If systematic, return to Phase 3.1

2. **Technical Jargon in Chapters 1-5**
   - Detection: Technical terms found during verification
   - Recovery: Replace with business terms from glossary
   - Escalation: If pervasive, review abstraction approach

3. **Unapproved Abstractions**
   - Detection: Abstraction not in Phase 3.1.1 approved list
   - Recovery: Remove or replace with approved abstraction
   - Escalation: Return to Phase 3.1.1 for approval

4. **Incomplete Traceability**
   - Detection: Traceability matrix has gaps
   - Recovery: Add missing references
   - Escalation: If systematic, review process

---

## End of Phase 3.2 Document
