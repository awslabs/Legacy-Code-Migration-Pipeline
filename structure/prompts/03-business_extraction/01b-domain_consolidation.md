# Phase 3.2: Domain Consolidation

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.2 - Domain Consolidation
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_requirements
**Task File Name**: {{TASKS_BASE_PATH}}/domain_consolidation_specialist_task.md

### Expected Deliverables

1. **Domain Specification Documents**
   - File: {{DOMAIN_CONSOLIDATION_BASE_PATH}}/D-XXX-[domain-name].md
   - Template: {{DOMAIN_CONSOLIDATION_SPECIFICATION_TEMPLATE}}
   - Description: Consolidated domain specifications following IEEE standard structure

2. **Progress Tracking**
   - File: {{DOMAIN_CONSOLIDATION_STATUS}}
   - Template: {{DOMAIN_CONSOLIDATION_STATUS_TEMPLATE}}
   - Description: Domain consolidation progress and status tracking

3. **Error Reports** (if applicable)
   - File: {{DOMAIN_CONSOLIDATION_ERRORS}}
   - Template: {{DOMAIN_CONSOLIDATION_ERRORS_TEMPLATE}}
   - Description: Documentation of errors and issues encountered during consolidation

### Success Criteria
- [ ] All business specifications assigned to appropriate domains
- [ ] All business entities consolidated without loss
- [ ] All business rules preserved during consolidation
- [ ] All business functions included in domain specifications
- [ ] Cross-domain relationships documented
- [ ] Traceability matrix complete for all consolidated items
- [ ] IEEE standard compliance maintained
- [ ] No duplicate or conflicting rules across domains
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for review

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: Consolidate related business specifications into domain-specific documents
- **Detailed instructions**: All Steps 1-9 below (Domain Identification, Domain Specification Structure, Business Entity Consolidation, etc.)
- **Technical specifications**: IEEE 830-1998 format, domain-specific identifiers (D-XXX, D001-BE-XXX, D001-BR-XXX, D001-F-XXX)
- **Business rules and constraints**: Maintain full traceability, eliminate redundancy, preserve all business rules, ensure consistency
- **Error handling guidance**: Domain classification ambiguity, conflicting business rules, incomplete traceability, duplicate entity definitions
- **Output format requirements**: Domain specification documents, progress tracking, error reports
- **Quality criteria**: Domain classification quality, consolidation completeness, traceability quality, IEEE compliance, consistency and non-redundancy

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Business specifications: {{BUSINESS_SPECIFICATION_BASE_PATH}}/business/
  - Workpackage definitions: {{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/
  - Source code analysis: {{PROJECT_BASE_PATH}}/output/analysis/
- **All output locations** (resolved paths):
  - Domain specifications: {{DOMAIN_CONSOLIDATION_BASE_PATH}}
  - Progress tracking: {{DOMAIN_CONSOLIDATION_STATUS}}
  - Error reports: {{DOMAIN_CONSOLIDATION_ERRORS}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Domain specification template: {{DOMAIN_CONSOLIDATION_SPECIFICATION_TEMPLATE}}
  - Status template: {{DOMAIN_CONSOLIDATION_STATUS_TEMPLATE}}
  - Errors template: {{DOMAIN_CONSOLIDATION_ERRORS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: business_specialist_requirements
- **Agent definition file**: structure/agents/business_team/business_specialist_requirements.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations (Phase 3.1 outputs), output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-9), business rules, error handling
- **Expected Deliverables**: All 3 deliverables with paths, templates, descriptions, validation checklists
- **Quality Criteria**: Domain classification quality, consolidation completeness, traceability quality, IEEE compliance, consistency
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

### 6. Dependencies from previous steps:
This step requires outputs from Phase 3.1 (Business Logic Extraction):
- **From Phase 3.1**: Individual business specifications for each workpackage with IEEE-formatted entities, rules, and functions
- Verify these artifacts exist before creating the task file

---

## Context

### Project Information
**Project Name**: {{PROJECT_NAME}}
**Project Base Path**: {{PROJECT_BASE_PATH}}

### Input Locations
- **Business Specifications**: {{BUSINESS_SPECIFICATION_BASE_PATH}}/business/
  - Description: Business specifications from Phase 3.1
  - Format: IEEE-formatted markdown documents with entities, rules, and functions
- **Workpackage Definitions**: {{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/
  - Description: Workpackage definitions with domain assignments
  - Format: Markdown documents with workpackage metadata

### Output Locations
- **Domain Specifications**: {{DOMAIN_CONSOLIDATION_BASE_PATH}}
  - Template: {{DOMAIN_CONSOLIDATION_SPECIFICATION_TEMPLATE}}
  - Description: Consolidated domain specifications
  - Format: IEEE-formatted markdown documents
- **Progress Tracking**: {{DOMAIN_CONSOLIDATION_STATUS}}
  - Template: {{DOMAIN_CONSOLIDATION_STATUS_TEMPLATE}}
  - Description: Phase completion tracking
  - Format: JSON status file
- **Error Reports**: {{DOMAIN_CONSOLIDATION_ERRORS}}
  - Template: {{DOMAIN_CONSOLIDATION_ERRORS_TEMPLATE}}
  - Description: Error log for consolidation issues
  - Format: JSON error log

### Previous Phase Artifacts
- Individual business specifications for each workpackage
- IEEE-formatted business rules, entities, and functions
- Legacy implementation references with traceability
- Domain assignments from workpackage definitions

### Task Files Location
- **Task Files**: {{TASKS_BASE_PATH}}
  - Description: Location for task-related files created by team supervisor

---

## Objective
Consolidate related business specifications into domain-specific documents by identifying and grouping specifications by business domain. Create comprehensive domain specification documents that maintain full traceability to original flow specifications while eliminating redundancy and ensuring all business rules are preserved.

## Instructions

### 1. Domain Identification and Classification
1. Review all business specifications from Phase 3
2. Identify business domains across all specifications:
   - Extract domain assignments from document control information
   - Group specifications by assigned business domain
   - Identify cross-domain specifications that span multiple domains
   - Create a domain classification map with all identified domains
   - Assign unique domain identifiers using D-XXX numbering system (e.g., D-001)

### 2. Domain Specification Structure Creation
1. For each identified business domain:
   - Create a domain specification document with IEEE standard structure
   - Include document control information with domain identifier
   - Create a comprehensive table of contents with section numbering
   - Establish traceability section to map to original specifications
   - Define domain-specific terminology and concepts section
   - Create consolidated sections for entities, rules, and functions

### 3. Business Entity Consolidation
1. For each business domain:
   - Identify all business entities from related specifications
   - Merge duplicate entities while preserving all attributes
   - Resolve naming conflicts with standardized domain terminology
   - Create consolidated entity definitions with complete attributes
   - Maintain original entity identifiers with mapping to consolidated entities
   - Document entity relationships and dependencies
   - Assign domain-specific entity identifiers using D001-BE-XXX format

### 4. Business Rule Consolidation
1. For each business domain:
   - Identify all business rules from related specifications
   - Eliminate duplicate rules while preserving all conditions
   - Resolve conflicts between similar rules with different conditions
   - Create consolidated rule definitions with complete conditions
   - Maintain original rule identifiers with mapping to consolidated rules
   - Document rule dependencies and relationships
   - Assign domain-specific rule identifiers using D001-BR-XXX format

### 5. Business Function Consolidation
1. For each business domain:
   - Identify all business functions from related specifications
   - Merge duplicate functions while preserving all inputs/outputs
   - Resolve naming conflicts with standardized domain terminology
   - Create consolidated function definitions with complete processing logic
   - Maintain original function identifiers with mapping to consolidated functions
   - Document function dependencies and relationships
   - Assign domain-specific function identifiers using D001-F-XXX format

### 6. Cross-Domain Relationship Documentation
1. For each domain specification:
   - Identify dependencies on other domains
   - Document cross-domain entity relationships
   - Map cross-domain rule dependencies
   - Define cross-domain function interactions
   - Create cross-reference section for domain interfaces
   - Ensure consistent terminology across domain boundaries

### 7. Traceability Preservation
1. For each consolidated domain specification:
   - Create comprehensive traceability matrix
   - Map each consolidated entity to original entities
   - Map each consolidated rule to original rules
   - Map each consolidated function to original functions
   - Include references to original specification documents
   - Maintain legacy implementation references from original specifications
   - Document any transformations or merges performed during consolidation

### 8. Completeness Validation
1. For each domain specification:
   - Verify all business entities from original specifications are represented
   - Ensure all business rules from original specifications are preserved
   - Confirm all business functions from original specifications are included
   - Validate that no business logic has been lost during consolidation
   - Check that all cross-domain relationships are documented
   - Verify traceability to original specifications is complete

### 9. Progress Tracking
1. Update progress tracking for each completed domain:
   - Record completion status and artifacts
   - Document any issues or exceptions
   - Update phase status in progress tracking system

## Output Format

### Domain Specification Document Structure
**File**: `{{DOMAIN_CONSOLIDATION_BASE_PATH}}/D-XXX-[domain-name].md`
**Template**: `{{DOMAIN_CONSOLIDATION_SPECIFICATION_TEMPLATE}}`

The template follows IEEE 830-1998 standard and includes:
- Document control with domain ID and related workpackages
- Domain terminology and key concepts
- Business entities with domain-specific identifiers (D001-BE-XXX)
- Business rules with domain-specific identifiers (D001-BR-XXX)
- Business functions with domain-specific identifiers (D001-F-XXX)
- Cross-domain relationships (entity dependencies, rule dependencies, function interactions)
- Comprehensive traceability matrix mapping to original specifications
- Legacy implementation references

### Progress Tracking Format
**File**: `{{DOMAIN_CONSOLIDATION_STATUS}}`
**Template**: `{{DOMAIN_CONSOLIDATION_STATUS_TEMPLATE}}`

The template tracks:
- Phase ID and overall status
- Array of domains with: domainId, domainName, status, specification path, relatedWorkpackages, completedDate
- Completion counts and last updated timestamp

## Quality Criteria

### Domain Classification Quality
- All business specifications are assigned to appropriate domains
- Domain boundaries are clearly defined and logical
- Cross-domain relationships are properly identified
- Domain terminology is consistent and well-defined

### Consolidation Completeness
- All business entities from original specifications are represented
- All business rules from original specifications are preserved
- All business functions from original specifications are included
- No business logic is lost during consolidation process
- Duplicate entities, rules, and functions are properly merged

### Traceability Quality
- Each consolidated entity, rule, and function is linked to original items
- Clear mapping between domain specifications and original specifications
- Complete traceability matrix for all consolidated items
- Legacy implementation references are preserved from original specifications
- Cross-domain relationships are fully documented

### IEEE Standard Compliance
- Document follows IEEE 830-1998 Software Requirements Specification format
- All sections are properly numbered and structured
- Document control information is complete and accurate
- Requirements are uniquely identified and traceable

### Consistency and Non-Redundancy
- No duplicate business rules across domain specifications
- Consistent terminology used throughout domain specifications
- Entity definitions are non-contradictory across domains
- Cross-domain relationships are consistently defined in both domains
- No conflicting business rules within or across domains

## Error Handling

### Common Error Scenarios

1. **Domain Classification Ambiguity**
   - Detection: Business specification could belong to multiple domains
   - Recovery: Assign to primary domain and document cross-domain relationships
   - Escalation: Flag for human review if domain assignment is unclear

2. **Conflicting Business Rules**
   - Detection: Rules with similar conditions but different actions
   - Recovery: Document all variations with context-specific applicability
   - Escalation: Request human clarification for critical business rule conflicts

3. **Incomplete Traceability**
   - Detection: Missing links between consolidated and original items
   - Recovery: Document gaps and attempt to reconstruct based on content
   - Escalation: Flag for human review if traceability cannot be established

4. **Duplicate Entity Definitions**
   - Detection: Similar entities with different attributes or validation rules
   - Recovery: Create consolidated entity with union of all attributes and rules
   - Escalation: Request human review for complex entity merges

### Error Reporting Format
**File**: `{{DOMAIN_CONSOLIDATION_ERRORS}}`
**Template**: `{{DOMAIN_CONSOLIDATION_ERRORS_TEMPLATE}}`
- Include: timestamp, error type, context, attempted resolution
- Update phase status to indicate partial completion or issues

### Fallback Strategies
- Create separate domain for ambiguous specifications if classification is unclear
- Document rule conflicts as variations with context-specific applicability
- Use content-based matching when explicit traceability is missing
- Create comprehensive entity definitions when merging is complex
- Flag areas requiring human expert review