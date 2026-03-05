# Phase 5.0.0: Technical Implementation Guide Creation

---

## Orchestration Information

**Phase**: Phase 5.0.0 - Technical Specification Creation  
**Team Supervisor**: tech_spec_team_supervisor  
**Assigned Agent**: tech_spec_extraction_specialist  
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.0.0_tech_spec_creation.md

---

## Expected Deliverables

1. **Technical Implementation Guide (per workpackage) - Draft**
   - File: {{TECH_SPEC_BASE_PATH}}/review/WP-{ID}-tech-implementation-guide-draft.md
   - Template: {{TECH_IMPLEMENTATION_GUIDE_TEMPLATE}}
   - Description: Workpackage-specific technical implementation guidance for code generation (draft for review)

2. **Technical Implementation Guide (per workpackage) - Approved**
   - File: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md
   - Description: Approved guide ready for code generation (moved from review folder after approval)

2. **Progress Tracking**
   - File: {{TECH_SPEC_STATUS}}
   - Description: Track completion status of all workpackage technical guides

3. **Error Log**
   - File: {{TECH_SPEC_ERRORS}}
   - Description: Document any issues encountered during technical guide creation

---

## Context

### Input Locations
- Business specifications: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification-approved.md
- Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
- Target specifications: {{TARGET_SPECIFICATION}}/
  - 00-COMMON-SPECIFICATION.md
  - 01-FRONTEND-SPECIFICATION.md
  - 02-BACKEND-SPECIFICATION.md
  - 03-BATCH-SPECIFICATION.md
- Database schemas: {{DATABASE_GEN_SRC}}/ (check for `new_sqlite_ddl.sql` and `new_sqlite_migration.sql`)
- Sample code: {{TARGET_SAMPLE_CODE}}/
- Workpackage planning: {{WORKPACKAGE_PLANNING}}
- Database analysis: {{DATABASE_ANALYSIS_OUTPUT}}/
- Previously created guides: {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide-approved.md

### Output Locations
- Technical implementation guides (draft): {{TECH_SPEC_BASE_PATH}}/review/WP-{ID}-tech-implementation-guide-draft.md
- Progress tracking: {{TECH_SPEC_STATUS}}
- Error logs: {{TECH_SPEC_ERRORS}}

---

## Standards Compliance

### IEEE 1016-2009: Software Design Descriptions (SDD)

This phase produces technical implementation guides following **IEEE 1016-2009** standards for Software Design Descriptions. An SDD is a representation of software design used to communicate design information to key stakeholders (in this case, code generation agents, reviewers, and developers).

**Required IEEE 1016-2009 Elements:**

1. **Design Stakeholders and Concerns** (Guide Section 1)
   - Primary: Code generation agents (need implementation patterns and details)
   - Secondary: Review agents (need traceability and rationale)
   - Tertiary: Human developers (need maintainability and integration context)

2. **Design Viewpoints** (Guide Sections 2-6)
   - **Architectural Viewpoint**: System structure, components, layers, patterns
   - **Interface Viewpoint**: APIs, data contracts, integration points
   - **Detailed Viewpoint**: Algorithms, data structures, implementation patterns
   - **Behavioral Viewpoint**: State machines, workflows, business logic flow

3. **Design Rationale** (Guide Section 8)
   - Justify pattern selections from target specifications
   - Document tradeoffs and alternatives considered
   - Explain integration decisions with traceability

4. **Design Languages and Notations** (Throughout)
   - Use consistent notation (UML, JSON schemas, code examples)
   - Reference target framework documentation
   - Provide implementation-ready pseudocode where appropriate

**Quality Criteria for IEEE Compliance:**
- ✓ All required SDD sections present and complete
- ✓ Design concerns of all stakeholders addressed
- ✓ Multiple viewpoints provided for comprehensive understanding
- ✓ Design rationale documented with traceability
- ✓ Consistent notation and terminology throughout

---

## Objective

For each workpackage, create a comprehensive technical implementation guide that enables a code generation agent to implement the workpackage by:

1. **Extracting patterns** from target specifications (architecture, structure, naming conventions)
2. **Analyzing business requirements** from the workpackage business specification
3. **Reviewing existing implementations** from previously completed workpackages
4. **Defining implementation tasks** specific to this workpackage
5. **Specifying integration points** with other workpackages and shared components
6. **Documenting technical decisions** with traceability to requirements and specifications

**Critical**: The guide must be derived from the actual target specifications provided in the project. Do NOT assume or hardcode any specific technology stack, framework, or architectural pattern.

**Standards Compliance**: All guides must follow IEEE 1016-2009 structure to ensure professional quality and completeness.

---

## Instructions

### Step 1: Initialize Progress Tracking

1. **Load workpackage list** from {{WORKPACKAGE_PLANNING}}
2. **Create progress tracking file** at {{TECH_SPEC_STATUS}}:
   - Copy template from {{TECH_SPEC_STATUS_TEMPLATE}}
   - Set `totalWorkpackages` to count from workpackage planning
   - Create entry for each workpackage with:
     ```json
     {
       "workpackageId": "WP-XXX",
       "workpackageName": "[Name from planning]",
       "status": "not_started",
       "startedAt": null,
       "completedAt": null,
       "reviewStatus": null,
       "approvedAt": null
     }
     ```
   - Set `notStarted` count to total workpackages
   - Set `lastUpdated` to current timestamp
3. **Create error log** at {{TECH_SPEC_ERRORS}} (empty array initially)
4. **Create progress directory** if it doesn't exist: {{TECH_SPEC_PROGRESS_PATH}}

### Step 2: For Each Workpackage (in priority order)

#### 2.1 Load Workpackage Context

Read the following inputs for the current workpackage:
- Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification-approved.md
- Test cases: {{TEST_CASE_GENERATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-tests-{LANG}-approved.md
- Workpackage metadata from {{WORKPACKAGE_PLANNING}}
- Database analysis relevant to this workpackage

#### 2.2 Extract Patterns from Target Specifications

**Read and analyze** the target specification files to discover:

**From 00-COMMON-SPECIFICATION.md**:
- Overall architecture approach
- Cross-cutting concerns (logging, error handling, security)
- Common patterns and conventions
- Shared libraries and utilities

**From tier-specific specifications** (01-FRONTEND, 02-BACKEND, 03-BATCH):
- Layer/component structure
- Package/directory organization
- Naming conventions
- Design patterns used
- API design patterns
- Data access patterns
- Validation approaches
- Error handling strategies

**Discovery approach**: Use keyword search for terms like "architecture", "structure", "pattern", "convention", "naming", "layer", "component", etc.

#### 2.3 Review Existing Technical Implementation Guides

If other workpackages have been completed:
- Read existing approved guides from {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide-approved.md
- Identify common patterns and structures
- Note integration points and shared components
- Ensure consistency with established patterns

#### 2.4 Analyze Business Requirements

From the business specification, identify:
- Business functions to implement
- Business entities and their relationships
- Business rules and validations
- Data operations required
- Integration requirements
- Non-functional requirements

#### 2.5 Generate Technical Implementation Guide (Draft)

Create a comprehensive guide at {{TECH_SPEC_BASE_PATH}}/review/WP-{ID}-tech-implementation-guide-draft.md that includes:

**Document Header (IEEE 1016-2009 Compliance)**
```markdown
---
# Technical Implementation Guide: WP-{ID}

## Document Control
- **Standard Compliance**: IEEE 1016-2009 (Software Design Descriptions)
- **Document Type**: Technical Implementation Guide
- **Workpackage**: WP-{ID} - {Workpackage Name}
- **Version**: 1.0
- **Date**: {Current Date}
- **Status**: Draft

## Standards Compliance Statement

This document follows IEEE 1016-2009 standards for Software Design Descriptions,
providing structured design information to enable code generation and implementation.

**IEEE 1016-2009 Coverage Map:**
| IEEE Requirement | This Document | Status |
|------------------|---------------|--------|
| Design Stakeholders | Section 1 | ✓ |
| Architectural Viewpoint | Section 2 | ✓ |
| Interface Viewpoint | Section 5 | ✓ |
| Detailed Design Viewpoint | Sections 3-4 | ✓ |
| Design Rationale | Section 8 | ✓ |
| Design Languages | Throughout | ✓ |
---
```

**Section 1: Design Stakeholders and Workpackage Overview**
- Workpackage ID and name
- Business context summary
- **Stakeholder Concerns**:
  - Code generation agents: Need implementation patterns, API specs, data models
  - Review agents: Need traceability, completeness, standards compliance
  - Human developers: Need maintainability, integration context, rationale
- Dependencies on other workpackages
- Tier(s) involved (frontend, backend, batch)

**Section 2: Architecture and Structure (Architectural Viewpoint)**
- Applicable architecture patterns (from target specs)
- Package/directory structure for this workpackage
- Component organization
- Layer responsibilities
- System context and boundaries

**Section 3: Implementation Tasks (Detailed Design Viewpoint)**
For each business function in the workpackage:
- Task description
- Required components/classes/modules
- API endpoints (if applicable)
- Data access requirements
- Business rule implementations
- Validation requirements
- Error handling approach

**Section 4: Data Model Implementation (Detailed Design Viewpoint)**
- Entity/model definitions needed
- Database table mappings
- Relationships and constraints
- Data access patterns to use

**Section 5: API Design (Interface Viewpoint)**
- Endpoint definitions
- Request/response structures
- HTTP methods and status codes
- Authentication/authorization requirements
- Data contracts and schemas

**Section 6: Integration Points (Interface Viewpoint)**
- Dependencies on other workpackages
- Shared components to use
- External system integrations
- Database dependencies
- Communication protocols

**Section 7: Testing Guidance**
- Test case references
- Testing approach per layer/component
- Integration testing requirements

**Section 8: Technical Decisions and Rationale (Design Rationale)**
- Key technical decisions made
- Rationale with traceability to requirements
- Alternative approaches considered
- Justification for pattern selections
- Tradeoff analysis

**Section 9: Implementation Checklist**
- Ordered list of implementation steps
- Dependencies between steps
- Verification criteria

#### 2.6 Validate Technical Implementation Guide

Ensure the guide:
- [ ] Follows IEEE 1016-2009 structure with all required sections
- [ ] Addresses concerns of all design stakeholders
- [ ] Provides multiple design viewpoints (architectural, interface, detailed)
- [ ] Documents design rationale with traceability
- [ ] Follows patterns from target specifications
- [ ] Is consistent with existing workpackage guides
- [ ] Covers all business functions from business spec
- [ ] Addresses all test cases
- [ ] Specifies all integration points
- [ ] Provides sufficient detail for code generation
- [ ] Does not duplicate content from business specs or target specs (references them instead)

#### 2.7 Update Progress Tracking

Update {{TECH_SPEC_STATUS}}:
- Set workpackage status to "draft_complete"
- Record completion timestamp in `completedAt`
- Update summary counts (decrement `inProgress`, increment `draftComplete`)
- Set `lastUpdated` to current timestamp

**Status Values**:
- `not_started` - Workpackage not yet started
- `in_progress` - Currently being worked on
- `draft_complete` - Draft guide completed, ready for review
- `in_review` - Under review in Phase 5.0.1
- `corrections_needed` - Review requested corrections
- `approved` - Review approved, ready for code generation
- `rejected` - Review rejected, escalated
- Note any issues or warnings

### Step 3: Handle Errors and Issues

If issues are encountered:
1. Document in {{TECH_SPEC_ERRORS}} with:
   - Workpackage ID
   - Issue description
   - Missing information or ambiguities
   - Recommended resolution
2. Set workpackage status to "blocked" in progress tracking
3. Continue with next workpackage if possible

### Step 4: Final Validation

After all workpackages are processed:
1. Review all technical implementation guides for consistency
2. Verify integration points are properly documented
3. Ensure shared components are identified across workpackages

---

## Quality Criteria

### Completeness
- [ ] All workpackages have technical implementation guides
- [ ] All business functions are covered
- [ ] All integration points are documented
- [ ] All data model requirements are specified

### Consistency
- [ ] Patterns match target specifications
- [ ] Naming conventions are consistent across workpackages
- [ ] Structure follows established patterns
- [ ] Integration points align between workpackages

### Clarity
- [ ] Implementation tasks are clearly defined
- [ ] Technical decisions are explained with rationale
- [ ] References to source documents are clear
- [ ] Code generation agents can implement without ambiguity

### Traceability
- [ ] Business functions traced to business spec
- [ ] Technical patterns traced to target spec
- [ ] Integration points traced to dependencies
- [ ] Test cases referenced appropriately

---

## Success Criteria

- All workpackages have complete technical implementation guides
- Guides follow patterns from target specifications
- Guides are consistent across workpackages
- Integration points are properly documented
- Code generation agents can implement workpackages using the guides
- Progress tracking shows 100% completion
- No critical errors in error log

---

## Notes

- The technical implementation guide is the bridge between business requirements and code generation
- It must be specific enough to guide implementation but not duplicate business logic details
- Patterns and conventions MUST come from target specifications, not assumptions
- Consistency across workpackages is critical for maintainability
- Integration points must be carefully documented to ensure workpackages work together
