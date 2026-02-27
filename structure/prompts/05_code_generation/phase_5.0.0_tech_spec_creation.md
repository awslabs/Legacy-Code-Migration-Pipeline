# Phase 5.0.0: Technical Implementation Guide Creation

---

## Orchestration Information

**Phase**: Phase 5.0.0 - Technical Specification Creation  
**Team Supervisor**: tech_spec_team_supervisor  
**Assigned Agent**: tech_spec_extraction_specialist  
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.0.0_tech_spec_creation.md

---

## Expected Deliverables

1. **Technical Implementation Guide (per workpackage)**
   - File: {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide.md
   - Template: {{TECH_IMPLEMENTATION_GUIDE_TEMPLATE}}
   - Description: Workpackage-specific technical implementation guidance for code generation

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
- Database schemas: {{DATABASE_GEN_SRC}}/
- Sample code: {{TARGET_SAMPLE_CODE}}/
- Workpackage planning: {{WORKPACKAGE_PLANNING}}
- Database analysis: {{DATABASE_ANALYSIS_OUTPUT}}/
- Previously created guides: {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide.md

### Output Locations
- Technical implementation guides: {{TECH_SPEC_BASE_PATH}}/
- Progress tracking: {{TECH_SPEC_STATUS}}
- Error logs: {{TECH_SPEC_ERRORS}}

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

---

## Instructions

### Step 1: Initialize Progress Tracking

1. Load workpackage list from {{WORKPACKAGE_PLANNING}}
2. Create progress tracking file at {{TECH_SPEC_STATUS}} using template
3. Set all workpackages to "not_started" status
4. Create error log at {{TECH_SPEC_ERRORS}}

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
- Read existing guides from {{TECH_SPEC_BASE_PATH}}/WP-*-tech-implementation-guide.md
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

#### 2.5 Generate Technical Implementation Guide

Create a comprehensive guide at {{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide.md that includes:

**Section 1: Workpackage Overview**
- Workpackage ID and name
- Business context summary
- Dependencies on other workpackages
- Tier(s) involved (frontend, backend, batch)

**Section 2: Architecture and Structure**
- Applicable architecture patterns (from target specs)
- Package/directory structure for this workpackage
- Component organization
- Layer responsibilities

**Section 3: Implementation Tasks**
For each business function in the workpackage:
- Task description
- Required components/classes/modules
- API endpoints (if applicable)
- Data access requirements
- Business rule implementations
- Validation requirements
- Error handling approach

**Section 4: Data Model Implementation**
- Entity/model definitions needed
- Database table mappings
- Relationships and constraints
- Data access patterns to use

**Section 5: API Design** (if applicable)
- Endpoint definitions
- Request/response structures
- HTTP methods and status codes
- Authentication/authorization requirements

**Section 6: Integration Points**
- Dependencies on other workpackages
- Shared components to use
- External system integrations
- Database dependencies

**Section 7: Testing Guidance**
- Test case references
- Testing approach per layer/component
- Integration testing requirements

**Section 8: Technical Decisions**
- Key technical decisions made
- Rationale with traceability to requirements
- Alternative approaches considered

**Section 9: Implementation Checklist**
- Ordered list of implementation steps
- Dependencies between steps
- Verification criteria

#### 2.6 Validate Technical Implementation Guide

Ensure the guide:
- [ ] Follows patterns from target specifications
- [ ] Is consistent with existing workpackage guides
- [ ] Covers all business functions from business spec
- [ ] Addresses all test cases
- [ ] Specifies all integration points
- [ ] Provides sufficient detail for code generation
- [ ] Does not duplicate content from business specs or target specs (references them instead)

#### 2.7 Update Progress Tracking

Update {{TECH_SPEC_STATUS}}:
- Set workpackage status to "completed"
- Record completion timestamp
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
4. Generate summary report of completed guides

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
