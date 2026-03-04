# Phase 5.0.1: Database Schema Review

---

## Document Control

**Document Type**: Task Document (Agent Level)
**Phase**: Phase 5.0.1 - Database Schema Review
**Version**: 1.0
**Date**: 2026-03-04
**Agent**: development_reviewer_code_generation

---

## Context

**Input Locations**:
- Business Specification: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-EN-approved.md`
- Modernized SQLite DDL: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_ddl.sql`
- Modernized PostgreSQL DDL: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_postgres_ddl.sql`
- SQLite Migration Script: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_migration.sql`
- PostgreSQL Migration Script: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_postgres_migration.sql`
- Comparison Report: `{{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md`
- Field Mapping: `{{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json`
- Legacy Schemas: `{{DATABASE_GEN_SRC}}/legacy_sqlite_ddl.sql`
- Legacy Schemas: `{{DATABASE_GEN_SRC}}/legacy_postgres_ddl.sql`

**Output Locations**:
- Review Report: `{{DATABASE_MODERNIZATION_OUTPUT}}/review/WP-{ID}-db-schema-review.md`
- Approved Schemas (if approved): `{{DATABASE_MODERNIZATION_OUTPUT}}/approved/`
- Progress Tracking: `{{DATABASE_MODERNIZATION_STATUS}}`

---

## Objective

Review the database schemas created in Phase 5.0.0 to ensure:
1. All business entities from the specification are represented
2. Modern database design principles are correctly applied
3. Migration mappings are complete and accurate
4. SQL syntax is valid for both SQLite and PostgreSQL
5. Cross-workpackage consistency is maintained

**Review Decision**: APPROVED, REVISE, or REJECT

---

## Instructions

### Step 1: Business Entity Coverage Verification

1. **Load business specification**:
   - Read `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-EN-approved.md`
   - Extract all business entities from Chapter 2

2. **Load modernized schemas**:
   - Read `{{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_ddl.sql`
   - Identify tables for current workpackage (WP-{ID})

3. **Verify coverage**:
   ```
   FOR EACH business_entity IN business_specification.chapter_2:
       table_exists = CHECK_TABLE_EXISTS(business_entity.id, sqlite_ddl)
       
       IF NOT table_exists:
           LOG_ERROR("Missing table for business entity: " + business_entity.id)
           coverage_complete = FALSE
       ELSE:
           # Verify attributes
           FOR EACH attribute IN business_entity.attributes:
               column_exists = CHECK_COLUMN_EXISTS(attribute.name, table)
               
               IF NOT column_exists:
                   LOG_ERROR("Missing column for attribute: " + attribute.name)
                   coverage_complete = FALSE
   ```

4. **Document findings**:
   ```markdown
   ## Business Entity Coverage
   
   ### Verified Entities
   | Entity ID | Entity Name | Modern Table | Status |
   |-----------|-------------|--------------|--------|
   | BE-{ID}-001 | User | users | ✓ Complete |
   
   ### Missing Entities
   | Entity ID | Entity Name | Issue |
   |-----------|-------------|-------|
   | BE-{ID}-002 | Account | Table not found |
   
   ### Missing Attributes
   | Entity ID | Attribute | Modern Table | Issue |
   |-----------|-----------|--------------|-------|
   | BE-{ID}-001 | email | users | Column not found |
   ```

---

### Step 2: Modern Design Principles Verification

For each table in the current workpackage, verify:

#### 2.1 Surrogate Key Check
```sql
-- Expected pattern
id INTEGER PRIMARY KEY AUTOINCREMENT  -- SQLite
id BIGSERIAL PRIMARY KEY             -- PostgreSQL
```

**Verification**:
- [ ] Table has `id` column
- [ ] `id` is PRIMARY KEY
- [ ] `id` is auto-incrementing (AUTOINCREMENT/SERIAL)
- [ ] `id` data type is INTEGER (SQLite) or BIGSERIAL (PostgreSQL)

#### 2.2 Business Key Check
```sql
-- Expected pattern
{business_key} VARCHAR(n) NOT NULL UNIQUE
```

**Verification**:
- [ ] Table has business key column (e.g., user_id, account_number)
- [ ] Business key has NOT NULL constraint
- [ ] Business key has UNIQUE constraint
- [ ] Business key is indexed (automatic with UNIQUE)

#### 2.3 Audit Columns Check
```sql
-- Expected pattern
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
created_by VARCHAR(8) NOT NULL,
updated_by VARCHAR(8) NOT NULL
```

**Verification**:
- [ ] Table has `created_at` column (TIMESTAMP, NOT NULL, DEFAULT)
- [ ] Table has `updated_at` column (TIMESTAMP, NOT NULL, DEFAULT)
- [ ] Table has `created_by` column (VARCHAR, NOT NULL)
- [ ] Table has `updated_by` column (VARCHAR, NOT NULL)

#### 2.4 Optimistic Locking Check
```sql
-- Expected pattern
version INTEGER NOT NULL DEFAULT 0  -- SQLite
version BIGINT NOT NULL DEFAULT 0   -- PostgreSQL
```

**Verification**:
- [ ] Table has `version` column
- [ ] `version` is NOT NULL
- [ ] `version` has DEFAULT 0
- [ ] `version` data type is INTEGER (SQLite) or BIGINT (PostgreSQL)

#### 2.5 Foreign Keys Check
```sql
-- Expected pattern (PostgreSQL)
CONSTRAINT fk_{table}_{column} 
    FOREIGN KEY ({column}) 
    REFERENCES {parent_table}(id) 
    ON DELETE CASCADE
```

**Verification**:
- [ ] Foreign key columns reference parent table's `id` (not business key)
- [ ] Foreign key constraints are named (fk_{table}_{column})
- [ ] ON DELETE/ON UPDATE actions are appropriate
- [ ] Foreign key columns are indexed

#### 2.6 Indexes Check
```sql
-- Expected patterns
CREATE INDEX idx_{table}_{column} ON {table}({column});
```

**Verification**:
- [ ] Business key is indexed (automatic with UNIQUE)
- [ ] Foreign key columns are indexed
- [ ] Frequently queried columns are indexed
- [ ] Index names follow convention (idx_{table}_{column})

#### 2.7 Constraints Check
```sql
-- Expected patterns
CHECK ({column} IN ('VALUE1', 'VALUE2'))
CHECK ({column} >= 0)
```

**Verification**:
- [ ] Business rules are enforced with CHECK constraints
- [ ] Enum values use CHECK constraints
- [ ] Range validations use CHECK constraints

**Document findings**:
```markdown
## Design Principles Verification

### Table: users

#### Surrogate Key
- [x] Has `id` column
- [x] `id` is PRIMARY KEY
- [x] `id` is auto-incrementing
- [x] Correct data type

#### Business Key
- [x] Has `user_id` column
- [x] `user_id` is NOT NULL
- [x] `user_id` is UNIQUE
- [x] `user_id` is indexed

#### Audit Columns
- [x] Has `created_at` (TIMESTAMP, NOT NULL, DEFAULT)
- [x] Has `updated_at` (TIMESTAMP, NOT NULL, DEFAULT)
- [x] Has `created_by` (VARCHAR, NOT NULL)
- [x] Has `updated_by` (VARCHAR, NOT NULL)

#### Optimistic Locking
- [x] Has `version` column
- [x] `version` is NOT NULL
- [x] `version` has DEFAULT 0
- [x] Correct data type

#### Foreign Keys
- N/A (no relationships in this table)

#### Indexes
- [x] Business key indexed (user_id)
- [x] user_type indexed

#### Constraints
- [x] CHECK constraint on user_type (IN ('ADMIN', 'REGULAR'))

**Status**: ✓ PASS
```

---

### Step 3: Migration Mapping Verification

1. **Load field mapping**:
   - Read `{{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json`
   - Extract mappings for current workpackage

2. **Verify mapping completeness**:
   ```
   FOR EACH legacy_table IN legacy_schema:
       IF legacy_table.is_related_to_workpackage(WP-{ID}):
           mapping_exists = CHECK_MAPPING_EXISTS(legacy_table, field_mapping)
           
           IF NOT mapping_exists:
               LOG_ERROR("Missing mapping for legacy table: " + legacy_table.name)
               mapping_complete = FALSE
           ELSE:
               # Verify field mappings
               FOR EACH legacy_field IN legacy_table.fields:
                   field_mapping_exists = CHECK_FIELD_MAPPING(legacy_field, mapping)
                   
                   IF NOT field_mapping_exists:
                       # Check if field is in unmappableFields
                       is_unmappable = CHECK_UNMAPPABLE(legacy_field, mapping)
                       
                       IF NOT is_unmappable:
                           LOG_ERROR("Missing field mapping: " + legacy_field.name)
                           mapping_complete = FALSE
   ```

3. **Verify transformation logic**:
   - Check that transformations are appropriate (TRIM, CASE, etc.)
   - Verify data type conversions are safe
   - Ensure no data loss in transformations

4. **Document findings**:
   ```markdown
   ## Migration Mapping Verification
   
   ### Verified Mappings
   | Legacy Table | Modern Table | Fields Mapped | Unmappable Fields | Status |
   |--------------|--------------|---------------|-------------------|--------|
   | USRSEC | users | 4 | 1 | ✓ Complete |
   
   ### Missing Mappings
   | Legacy Table | Issue |
   |--------------|-------|
   | OLDTABLE | No mapping found |
   
   ### Transformation Issues
   | Legacy Field | Modern Field | Issue | Recommendation |
   |--------------|--------------|-------|----------------|
   | SEC-DATE | created_at | Date format conversion unclear | Specify format |
   ```

---

### Step 4: SQL Syntax Verification

1. **Validate SQLite DDL**:
   - Check for syntax errors
   - Verify SQLite-specific syntax (AUTOINCREMENT, etc.)
   - Ensure foreign key pragma is documented

2. **Validate PostgreSQL DDL**:
   - Check for syntax errors
   - Verify PostgreSQL-specific syntax (BIGSERIAL, etc.)
   - Ensure constraints are properly named

3. **Validate migration scripts**:
   - Check INSERT statements are valid
   - Verify SELECT transformations are correct
   - Ensure verification queries are included

4. **Document findings**:
   ```markdown
   ## SQL Syntax Verification
   
   ### SQLite DDL
   - [x] No syntax errors
   - [x] SQLite-specific syntax correct
   - [x] Foreign key pragma documented
   
   ### PostgreSQL DDL
   - [x] No syntax errors
   - [x] PostgreSQL-specific syntax correct
   - [x] Constraints properly named
   
   ### Migration Scripts
   - [x] INSERT statements valid
   - [x] Transformations correct
   - [x] Verification queries included
   
   **Status**: ✓ PASS
   ```

---

### Step 5: Cross-Workpackage Consistency Check

1. **Load previously approved schemas**:
   - Read schemas from previous workpackages
   - Identify shared tables or relationships

2. **Verify naming consistency**:
   - Table names follow same convention
   - Column names follow same convention
   - Index names follow same convention
   - Constraint names follow same convention

3. **Verify relationship consistency**:
   - Foreign keys reference correct tables
   - Relationship types are consistent
   - ON DELETE/ON UPDATE actions are consistent

4. **Document findings**:
   ```markdown
   ## Cross-Workpackage Consistency
   
   ### Naming Conventions
   - [x] Table names consistent (plural, snake_case)
   - [x] Column names consistent (snake_case)
   - [x] Index names consistent (idx_{table}_{column})
   - [x] Constraint names consistent (fk_{table}_{column})
   
   ### Relationships
   - [x] Foreign keys reference correct tables
   - [x] Relationship types consistent
   - [x] ON DELETE/ON UPDATE actions consistent
   
   ### Shared Tables
   | Table | Workpackages | Status |
   |-------|--------------|--------|
   | users | WP-001, WP-002 | ✓ Consistent |
   
   **Status**: ✓ PASS
   ```

---

### Step 6: Comparison Report Verification

1. **Load comparison report**:
   - Read `{{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md`
   - Verify section for current workpackage exists

2. **Verify report completeness**:
   - [ ] New tables documented
   - [ ] Modified tables documented
   - [ ] Removed tables documented
   - [ ] Field changes documented with transformations
   - [ ] Rationale provided for changes

3. **Document findings**:
   ```markdown
   ## Comparison Report Verification
   
   - [x] Workpackage section exists
   - [x] New tables documented
   - [x] Modified tables documented
   - [x] Removed tables documented
   - [x] Field changes documented
   - [x] Transformations specified
   - [x] Rationale provided
   
   **Status**: ✓ PASS
   ```

---

### Step 7: Generate Review Report

Create comprehensive review report:

```markdown
# Database Schema Review Report

## Workpackage Information
- **Workpackage ID**: WP-{ID}
- **Workpackage Name**: {Workpackage Name}
- **Flow ID**: {FLOW_ID}
- **Review Date**: {Date}
- **Reviewer**: db_modernization_reviewer

---

## Executive Summary

**Overall Status**: [APPROVED / REVISE / REJECT]

**Summary**: [Brief summary of review findings]

**Key Findings**:
- [Finding 1]
- [Finding 2]
- [Finding 3]

---

## Detailed Review Results

### 1. Business Entity Coverage
[Results from Step 1]

**Status**: [PASS / FAIL]
**Issues Found**: [Number]
**Critical Issues**: [Number]

### 2. Modern Design Principles
[Results from Step 2]

**Status**: [PASS / FAIL]
**Issues Found**: [Number]
**Critical Issues**: [Number]

### 3. Migration Mappings
[Results from Step 3]

**Status**: [PASS / FAIL]
**Issues Found**: [Number]
**Critical Issues**: [Number]

### 4. SQL Syntax
[Results from Step 4]

**Status**: [PASS / FAIL]
**Issues Found**: [Number]
**Critical Issues**: [Number]

### 5. Cross-Workpackage Consistency
[Results from Step 5]

**Status**: [PASS / FAIL]
**Issues Found**: [Number]
**Critical Issues**: [Number]

### 6. Comparison Report
[Results from Step 6]

**Status**: [PASS / FAIL]
**Issues Found**: [Number]
**Critical Issues**: [Number]

---

## Issues Summary

### Critical Issues (Must Fix)
| Issue ID | Category | Description | Impact | Recommendation |
|----------|----------|-------------|--------|----------------|
| C-001 | Coverage | Missing table for BE-{ID}-002 | High | Create table |

### Major Issues (Should Fix)
| Issue ID | Category | Description | Impact | Recommendation |
|----------|----------|-------------|--------|----------------|
| M-001 | Design | Missing version column in table X | Medium | Add version column |

### Minor Issues (Nice to Fix)
| Issue ID | Category | Description | Impact | Recommendation |
|----------|----------|-------------|--------|----------------|
| N-001 | Naming | Inconsistent index naming | Low | Rename index |

---

## Review Decision

**Decision**: [APPROVED / REVISE / REJECT]

**Rationale**:
[Detailed explanation of decision]

**Conditions** (if APPROVED with conditions):
- [Condition 1]
- [Condition 2]

**Required Changes** (if REVISE):
- [Change 1]
- [Change 2]

**Rejection Reasons** (if REJECT):
- [Reason 1]
- [Reason 2]

---

## Recommendations

### Immediate Actions
1. [Action 1]
2. [Action 2]

### Future Considerations
1. [Consideration 1]
2. [Consideration 2]

---

## Approval Signatures

**Reviewed By**: db_modernization_reviewer
**Review Date**: {Date}
**Decision**: [APPROVED / REVISE / REJECT]

---

## Appendix

### Review Checklist
- [ ] All business entities have tables
- [ ] All tables have surrogate keys
- [ ] All tables have business keys
- [ ] All tables have audit columns
- [ ] All tables have version columns
- [ ] All foreign keys defined
- [ ] All indexes defined
- [ ] All constraints defined
- [ ] Migration mappings complete
- [ ] SQL syntax valid
- [ ] Cross-workpackage consistency maintained
- [ ] Comparison report complete

### Files Reviewed
- `{{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_ddl.sql`
- `{{DATABASE_MODERNIZATION_OUTPUT}}/new_postgres_ddl.sql`
- `{{DATABASE_MODERNIZATION_OUTPUT}}/new_sqlite_migration.sql`
- `{{DATABASE_MODERNIZATION_OUTPUT}}/new_postgres_migration.sql`
- `{{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md`
- `{{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json`

### Reference Documents
- `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-EN-approved.md`
- `{{DATABASE_GEN_SRC}}/legacy_sqlite_ddl.sql`
```

---

### Step 8: Update Progress Tracking

Update `{{DATABASE_MODERNIZATION_STATUS}}` with review results:

```json
{
  "phaseId": "05.0.1-database-schema-review",
  "status": "in_progress",
  "currentWorkpackage": "WP-{ID}",
  "workpackages": [
    {
      "workpackageId": "WP-{ID}",
      "workpackageName": "{Workpackage Name}",
      "flowId": "{FLOW_ID}",
      "status": "reviewed",
      "reviewDecision": "APPROVED",
      "reviewDate": "2026-03-04",
      "issuesFound": {
        "critical": 0,
        "major": 0,
        "minor": 2
      },
      "reviewChecklist": {
        "businessEntityCoverage": "PASS",
        "modernDesignPrinciples": "PASS",
        "migrationMappings": "PASS",
        "sqlSyntax": "PASS",
        "crossWorkpackageConsistency": "PASS",
        "comparisonReport": "PASS"
      }
    }
  ],
  "lastUpdated": "2026-03-04"
}
```

---

## Review Decision Criteria

### APPROVED
- All business entities have tables
- All modern design principles applied
- All migration mappings complete
- No SQL syntax errors
- Cross-workpackage consistency maintained
- No critical issues
- 0-2 major issues (with clear resolution path)

### REVISE
- Missing some business entities (can be added)
- Some design principle violations (can be fixed)
- Some migration mappings incomplete (can be completed)
- Minor SQL syntax errors (can be fixed)
- 1-3 critical issues OR 3-5 major issues
- Clear path to resolution

### REJECT
- Fundamental design flaws
- Multiple critical issues with no clear resolution
- Significant business entity coverage gaps
- Major SQL syntax errors
- Inconsistent with previous workpackages (breaking changes)
- 4+ critical issues OR 6+ major issues

---

## Quality Criteria

Before completing this review, verify:

- [ ] All verification steps completed
- [ ] All findings documented
- [ ] Review decision made with clear rationale
- [ ] Review report generated
- [ ] Progress tracking updated
- [ ] If APPROVED: No critical issues remain
- [ ] If REVISE: Required changes clearly specified
- [ ] If REJECT: Rejection reasons clearly documented

---

## Success Criteria

This review is complete when:
- [ ] Comprehensive review report generated
- [ ] Clear decision made (APPROVED / REVISE / REJECT)
- [ ] All issues documented with severity and recommendations
- [ ] Progress tracking updated
- [ ] If APPROVED: Schemas ready for Phase 5.1 (Tech Spec Extraction)
- [ ] If REVISE: Clear feedback provided for Phase 5.0.0 rework
- [ ] If REJECT: Escalation to human supervisor initiated

---

## End of Task Document
