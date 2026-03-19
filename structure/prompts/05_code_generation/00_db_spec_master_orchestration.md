# Phase 5.0: Database Modernization - Master Orchestration

---

## Document Control

**Document Type**: Master Orchestration (Supervisor Level)
**Phase**: Phase 5.0 - Database Modernization
**Version**: 1.0
**Date**: 2026-03-04
**Owner**: development_team_supervisor

---

## CRITICAL - Delegation Check

**IF YOU ARE NOT THE OWNER OF THIS DOCUMENT, STOP AND DELEGATE**

This document is owned by: **development_team_supervisor**

**Before proceeding, check your role**:
- If you are **development_team_supervisor**: Continue with orchestration
- If you are **ANY OTHER AGENT**: 
  1. STOP immediately
  2. Delegate this entire prompt to **development_team_supervisor**
  3. Wait for their response
  4. Do NOT attempt to execute the orchestration yourself

**Why this matters**: Only the designated supervisor has the authority and context to orchestrate the entire phase across multiple agents. Attempting to execute orchestration from a non-supervisor role will result in incomplete or incorrect execution.

---

## Overview

This document provides orchestration instructions for the Database Modernization phase, which creates modernized database schemas based on business entities extracted from business specifications.

**Purpose**: For each workpackage, create modernized database schemas that:
- Reflect business entities from business specifications (technology-agnostic)
- Apply modern database design principles (surrogate keys, audit columns, proper indexes)
- Generate migration mappings from legacy to modern schemas
- Document schema changes and transformation requirements
- Support both SQLite and PostgreSQL targets

**Critical Principle**: Design databases from **business requirements** (Chapters 1-5), not from **legacy database structure**. The legacy schemas serve only as a reference for migration mapping.

**Sub-Phases**:
1. **Phase 5.0.0**: Database Schema Creation (per workpackage)
2. **Phase 5.0.1**: Database Schema Review (per workpackage)

---

## Phase Dependencies

```
Phase 3 (Business Specification) → Phase 4 (Test Case Generation) → Phase 5.0 (Database Modernization)
                                                                            ↓
                                                                    Phase 5.0.0 (DB Schema Creation)
                                                                            ↓
                                                                    Phase 5.0.1 (DB Schema Review)
                                                                            ↓
                                                                    Phase 5.1 (Tech Spec Extraction)
                                                                            ↓
                                                                    Phase 5.2+ (Code Generation)
```

**Prerequisites**:
- Phase 3 outputs: Business specifications (approved) with Chapter 2 (Business Entities)
- Phase 1 outputs: Legacy database schemas in `{{DATABASE_GEN_SRC}}/`
- Phase 2 outputs: Workpackage planning with migration sequence

**Outputs**:
- Modernized DDL: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql`
- Migration script: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_migration.sql`
- Schema comparison report: `{{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md`
- Field mapping: `{{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json`
- Progress tracking: `{{DATABASE_MODERNIZATION_STATUS}}`
- Error logs: `{{DATABASE_MODERNIZATION_ERRORS}}`

**Note**: `{DB_NAME}` is auto-detected from the legacy schema filename in `{{DATABASE_GEN_SRC}}/`. Only ONE legacy schema file should exist (e.g., `legacy_postgres_ddl.sql` OR `legacy_sqlite_ddl.sql` OR `legacy_db2_ddl.sql` OR `legacy_mysql_ddl.sql`).

---

## Orchestration Workflow

### For Each Workpackage (in migration sequence order):

```
WORKPACKAGE_LOOP:
    SELECT next_workpackage FROM workpackage_planning ORDER BY migration_sequence

    # ========================================
    # PHASE 5.0.0: DATABASE SCHEMA CREATION
    # ========================================
    
    EXECUTE Phase_5.0.0:
        ASSIGN: development_specialist_code_generation
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0.0_db_spec_creation.md
        PROVIDE_CONTEXT:
            - workpackage_id: current_workpackage.id
            - workpackage_name: current_workpackage.name
            - flow_id: current_workpackage.flow_id
        
        INPUTS:
            - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-approved.md
            - Legacy database schema: {{DATABASE_GEN_SRC}}/legacy_{DB_NAME}_ddl.sql (auto-detect DB_NAME)
            - Workpackage planning: {{WORKPACKAGE_PLANNING}}
            - Previously created schema: {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql (if exists)
            - Previous comparison report: {{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md (if exists)
            - Previous field mapping: {{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json (if exists)
        
        EXPECTED_OUTPUTS:
            - Updated DDL: {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql
            - Updated migration script: {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_migration.sql
            - Updated comparison report: {{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md
            - Updated field mapping: {{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json
            - Progress tracking: {{DATABASE_MODERNIZATION_STATUS}}
            - Error reports (if any): {{DATABASE_MODERNIZATION_ERRORS}}
        
        VERIFICATION:
            CHECK schemas_updated(WP-{ID})
            CHECK all_business_entities_mapped(WP-{ID})
            CHECK modern_design_principles_applied(WP-{ID})
            CHECK comparison_report_updated(WP-{ID})
            CHECK field_mappings_documented(WP-{ID})
            CHECK migration_scripts_updated(WP-{ID})
            
            IF verification_failed:
                LOG error to {{DATABASE_MODERNIZATION_ERRORS}}
                ESCALATE to human supervisor
                HALT workpackage processing
            
            IF verification_passed:
                UPDATE {{DATABASE_MODERNIZATION_STATUS}} with completion
                PROCEED to Phase_5.0.1

    # ========================================
    # PHASE 5.0.1: DATABASE SCHEMA REVIEW
    # ========================================
    
    EXECUTE Phase_5.0.1:
        ASSIGN: development_reviewer_code_generation
        PROVIDE_TASK: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0.1_db_spec_review.md
        PROVIDE_CONTEXT:
            - workpackage_id: current_workpackage.id
            - workpackage_name: current_workpackage.name
            - flow_id: current_workpackage.flow_id
        
        INPUTS:
            - Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-approved.md
            - Modernized DDL: {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql
            - Migration script: {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_migration.sql
            - Comparison report: {{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md
            - Field mapping: {{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json
            - Legacy schema: {{DATABASE_GEN_SRC}}/legacy_{DB_NAME}_ddl.sql
        
        EXPECTED_OUTPUTS:
            - Review report: {{DATABASE_MODERNIZATION_OUTPUT}}/review/WP-{ID}-db-schema-review.md
            - Approved schemas (if approved): {{DATABASE_MODERNIZATION_OUTPUT}}/approved/
            - Progress tracking: {{DATABASE_MODERNIZATION_STATUS}}
        
        VERIFICATION:
            CHECK review_report_exists(WP-{ID})
            CHECK approval_decision_documented(WP-{ID})
            
            IF decision == "APPROVED":
                CHECK all_business_entities_have_tables(WP-{ID})
                CHECK modern_design_principles_verified(WP-{ID})
                CHECK migration_mappings_complete(WP-{ID})
                UPDATE {{DATABASE_MODERNIZATION_STATUS}} with approval
                PROCEED to WORKPACKAGE_COMPLETE
            
            ELSE IF decision == "REVISE":
                CHECK revision_feedback_documented(WP-{ID})
                UPDATE {{DATABASE_MODERNIZATION_STATUS}} with revision request
                RETURN to Phase_5.0.0 with feedback
            
            ELSE IF decision == "REJECT":
                CHECK rejection_rationale_documented(WP-{ID})
                UPDATE {{DATABASE_MODERNIZATION_STATUS}} with rejection
                ESCALATE to human supervisor
                HALT workpackage processing

    # ========================================
    # WORKPACKAGE COMPLETION
    # ========================================
    
    WORKPACKAGE_COMPLETE:
        LOG "Database modernization for WP-{ID} completed successfully"
        UPDATE {{DATABASE_MODERNIZATION_STATUS}} with workpackage completion
        PROCEED to next workpackage in WORKPACKAGE_LOOP

END WORKPACKAGE_LOOP
```

---

## Agent Assignments

### Phase 5.0.0: Database Schema Creation
**Agent**: development_specialist_code_generation
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0.0_db_spec_creation.md
**Capabilities**:
- Business entity analysis from specifications
- Modern database design (normalization, indexing, constraints)
- Schema generation (PostgreSQL, MySQL, SQLite, DB2, etc.)
- Legacy-to-modern mapping creation
- Migration script generation
- Change documentation

### Phase 5.0.1: Database Schema Review
**Agent**: development_reviewer_code_generation
**Task Document**: {{PROMPTS_BASE_PATH}}/05_code_generation/phase_5.0.1_db_spec_review.md
**Capabilities**:
- Schema completeness verification
- Modern design principle validation
- Business entity coverage checking
- Migration mapping validation
- SQL syntax verification
- Cross-workpackage consistency checking

---

## Input/Output Contracts

### Phase 3 → Phase 5.0.0
**Phase 3 Outputs** (Phase 5.0.0 Inputs):
- Business specifications: `WP-{ID}-FLOW_{FLOW_ID}-specification-approved.md`
- Chapter 2: Business Entities with attributes and relationships

**Contract**:
- All business entities documented with BE-XXX identifiers
- Entity attributes with data types specified
- Relationships between entities documented
- Business rules for entities documented

### Phase 5.0.0 → Phase 5.0.1
**Phase 5.0.0 Outputs** (Phase 5.0.1 Inputs):
- Modernized DDL scripts (SQLite and PostgreSQL)
- Migration scripts (SQLite and PostgreSQL)
- Schema comparison report
- Field mapping JSON

**Contract**:
- All business entities from spec have corresponding tables
- All tables follow modern design principles
- Migration mappings documented for all tables/fields
- Comparison report shows all changes
- SQL syntax is valid

### Phase 5.0.1 → Phase 5.1
**Phase 5.0.1 Outputs** (Phase 5.1 Inputs):
- Approved modernized schemas
- Approved migration scripts
- Review report with approval status

**Contract**:
- Schemas approved for use in code generation
- All business entities covered
- Migration path documented
- Ready for technical specification extraction

---

## Verification Criteria

### Phase 5.0.0 Verification
```
CHECK schemas_updated(workpackage_id):
    sqlite_ddl = file_exists({{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_ddl.sql)
    postgres_ddl = file_exists({{DATABASE_MODERNIZATION_OUTPUT}}/new_postgres_ddl.sql)
    RETURN sqlite_ddl AND postgres_ddl

CHECK all_business_entities_mapped(workpackage_id):
    business_spec = load_business_specification(workpackage_id)
    sqlite_ddl = load_file({{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_ddl.sql)
    
    entities = business_spec.chapter_2.get_entities()
    FOR EACH entity IN entities:
        IF NOT sqlite_ddl.contains_table_for_entity(entity.id):
            LOG "Business entity {entity.id} not mapped to table"
            RETURN FALSE
    RETURN TRUE

CHECK modern_design_principles_applied(workpackage_id):
    sqlite_ddl = load_file({{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_ddl.sql)
    
    # Check for surrogate keys
    tables = sqlite_ddl.get_tables()
    FOR EACH table IN tables:
        IF NOT table.has_column("id") OR NOT table.column("id").is_primary_key():
            LOG "Table {table.name} missing surrogate key"
            RETURN FALSE
        
        # Check for audit columns
        required_audit_columns = ["created_at", "updated_at", "created_by", "updated_by"]
        FOR EACH column IN required_audit_columns:
            IF NOT table.has_column(column):
                LOG "Table {table.name} missing audit column {column}"
                RETURN FALSE
        
        # Check for version column (optimistic locking)
        IF NOT table.has_column("version"):
            LOG "Table {table.name} missing version column"
            RETURN FALSE
    
    RETURN TRUE

CHECK comparison_report_updated(workpackage_id):
    report = file_exists({{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md)
    IF NOT report:
        RETURN FALSE
    
    report_content = load_file({{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md)
    RETURN report_content.contains(workpackage_id)

CHECK field_mappings_documented(workpackage_id):
    mapping = file_exists({{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json)
    IF NOT mapping:
        RETURN FALSE
    
    mapping_data = load_json({{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json)
    RETURN mapping_data.has_mappings_for_workpackage(workpackage_id)

CHECK migration_scripts_updated(workpackage_id):
    sqlite_migration = file_exists({{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_migration.sql)
    postgres_migration = file_exists({{DATABASE_MODERNIZATION_OUTPUT}}/new_postgres_migration.sql)
    RETURN sqlite_migration AND postgres_migration
```

### Phase 5.0.1 Verification
```
CHECK review_report_exists(workpackage_id):
    report_path = {{DATABASE_MODERNIZATION_OUTPUT}}/review/WP-{workpackage_id}-db-schema-review.md
    RETURN file_exists(report_path)

CHECK approval_decision_documented(workpackage_id):
    report = load_review_report(workpackage_id)
    RETURN report.has_field("decision") AND 
           report.decision IN ["APPROVED", "REVISE", "REJECT"]

CHECK all_business_entities_have_tables(workpackage_id):
    business_spec = load_business_specification(workpackage_id)
    review_report = load_review_report(workpackage_id)
    
    entities = business_spec.chapter_2.get_entities()
    FOR EACH entity IN entities:
        IF NOT review_report.confirms_table_exists_for(entity.id):
            LOG "Review did not confirm table for entity {entity.id}"
            RETURN FALSE
    RETURN TRUE

CHECK modern_design_principles_verified(workpackage_id):
    review_report = load_review_report(workpackage_id)
    RETURN review_report.design_principles_section.status == "VERIFIED"

CHECK migration_mappings_complete(workpackage_id):
    review_report = load_review_report(workpackage_id)
    RETURN review_report.migration_mappings_section.status == "COMPLETE"
```

---

## Error Handling and Rework

### Rework Scenarios

#### Scenario 1: Missing Business Entities (Return to Phase 5.0.0)
**Triggers**:
- Not all business entities from spec have tables
- Entity attributes missing in table definitions
- Relationships not properly modeled

**Actions**:
1. Document missing entities in review report
2. Update Phase 5.0.0 task with specific entities to add
3. Re-assign development_specialist_code_generation
4. Re-execute Phase 5.0.0 with focus on missing entities
5. Re-verify completeness

#### Scenario 2: Design Principle Violations (Return to Phase 5.0.0)
**Triggers**:
- Tables missing surrogate keys
- Tables missing audit columns
- Tables missing version columns
- Missing or incorrect indexes
- Missing foreign key constraints

**Actions**:
1. Document violations in review report
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.0.0 to fix design issues
4. Re-verify design principles

#### Scenario 3: Incomplete Migration Mappings (Return to Phase 5.0.0)
**Triggers**:
- Legacy tables not mapped to modern tables
- Legacy fields not mapped to modern fields
- Missing transformation logic
- Unmappable data not flagged

**Actions**:
1. Document mapping gaps in review report
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.0.0 to complete mappings
4. Re-verify migration completeness

#### Scenario 4: SQL Syntax Errors (Return to Phase 5.0.0)
**Triggers**:
- Invalid SQL syntax in DDL scripts
- Invalid SQL syntax in migration scripts
- Database-specific syntax issues

**Actions**:
1. Document syntax errors in review report
2. Re-assign development_specialist_code_generation
3. Re-execute Phase 5.0.0 to fix syntax
4. Re-verify SQL validity

#### Scenario 5: Critical Issues (Escalate to Human)
**Triggers**:
- Business specification ambiguities preventing schema design
- Irreconcilable conflicts between workpackages
- Complex legacy data structures requiring manual review
- Data migration risks requiring human decision

**Actions**:
1. Document critical issues in error log
2. Escalate to human supervisor with detailed explanation
3. Halt workpackage processing
4. Await human guidance before proceeding

---

## Progress Tracking

### Status Tracking

**JSON File**: `{{DATABASE_MODERNIZATION_STATUS}}`
**Markdown File**: `{{DATABASE_MODERNIZATION_PROGRESS}}`

**Update Frequency**: After each workpackage completion and after review

### Resumption Logic

When resuming after interruption:
1. Read {{DATABASE_MODERNIZATION_STATUS}}
2. Check which workpackages are completed
3. Check which workpackages are in review
4. Resume from first incomplete workpackage or review step

---

## Quality Gates

### Phase 5.0.0 Quality Gate
**Criteria**:
- [ ] All business entities have tables
- [ ] All tables follow modern design principles
- [ ] All tables have surrogate keys
- [ ] All tables have audit columns
- [ ] All tables have version columns
- [ ] Proper indexes defined
- [ ] Foreign keys defined
- [ ] Migration mappings documented
- [ ] Comparison report updated
- [ ] No SQL syntax errors

**Gate Decision**:
- **PASS**: Proceed to Phase 5.0.1
- **FAIL**: Rework Phase 5.0.0 or escalate

### Phase 5.0.1 Quality Gate
**Criteria**:
- [ ] All schemas reviewed
- [ ] Completeness verified
- [ ] Design principles verified
- [ ] Migration mappings verified
- [ ] SQL syntax verified
- [ ] Cross-workpackage consistency verified
- [ ] All schemas approved
- [ ] No blocking issues

**Gate Decision**:
- **PASS**: Proceed to Phase 5.1 (Tech Spec Extraction)
- **FAIL**: Rework Phase 5.0.0 or escalate

---

## Configuration and Path Variables

### Input Paths
```
Business Specification Base Path = {{BUSINESS_SPECIFICATION_BASE_PATH}}
Legacy Database Schemas = {{DATABASE_GEN_SRC}}
Workpackage Planning = {{WORKPACKAGE_PLANNING}}
```

### Output Paths
```
Database Modernization Output = {{DATABASE_MODERNIZATION_OUTPUT}}
Database Modernization Status = {{DATABASE_MODERNIZATION_STATUS}}
Database Modernization Progress = {{DATABASE_MODERNIZATION_PROGRESS}}
Database Modernization Errors = {{DATABASE_MODERNIZATION_ERRORS}}
```

---

## Supervisor Responsibilities

### Pre-Execution
1. Verify all prerequisites exist
2. Verify all path variables are resolved
3. Verify legacy database schemas exist
4. Verify business specifications exist
5. Verify agents are available
6. Create output directories if needed
7. Initialize progress tracking

### During Execution
1. Assign appropriate agent for each sub-phase
2. Provide task document from {{PROMPTS_BASE_PATH}}
3. Monitor execution progress
4. Verify completion against quality gates
5. Handle errors and rework scenarios
6. Update progress tracking
7. Escalate critical issues

### Post-Execution
1. Verify all schemas approved
2. Verify all quality gates passed
3. Generate final summary
4. Archive artifacts
5. Prepare handoff to Phase 5.1 (Tech Spec Extraction)

---

## Success Criteria

Phase 5.0 is considered complete when:
- [ ] All workpackages have modernized database schemas
- [ ] All schemas reviewed and approved
- [ ] All business entities mapped to tables
- [ ] All tables follow modern design principles
- [ ] Migration mappings complete for all tables/fields
- [ ] Comparison reports document all changes
- [ ] No blocking issues remain
- [ ] Progress tracking shows 100% completion
- [ ] Ready for Phase 5.1 (Tech Spec Extraction)

---

## Notes for Supervisor

**Critical Success Factors**:
1. **Business-Driven Design**: Schemas must reflect business entities, not legacy structure
2. **Modern Principles**: All tables must have surrogate keys, audit columns, version columns
3. **Complete Mappings**: Every legacy table/field must be mapped or flagged as unmappable
4. **Incremental Build**: Schemas build up incrementally as workpackages are processed
5. **Consistency**: Naming conventions and design patterns must be consistent across workpackages

**Common Pitfalls to Avoid**:
1. Copying legacy database structure instead of designing from business entities
2. Missing audit columns or version columns
3. Incomplete migration mappings
4. Inconsistent naming conventions across workpackages
5. Missing indexes or foreign key constraints

**When to Escalate**:
1. Business specification ambiguities preventing schema design
2. Complex legacy data structures requiring manual review
3. Irreconcilable conflicts between workpackages
4. Data migration risks requiring human decision
5. Repeated rework cycles (more than 2 iterations per workpackage)

---

## End of Master Orchestration Document
