# Phase 5.0: Database Modernization

## Context

**Phase**: 5.0 - Database Modernization (Before Tech Spec Generation)
**Orchestration**: See `00_db_spec_master_orchestration.md` for complete workflow

- Project Structure: Standard migration project folder structure
- Input Location: 
  - {{BUSINESS_SPECIFICATION_BASE_PATH}} - Workpackage-based business specifications (Chapter 2: Business Entities)
  - {{DATABASE_GEN_SRC}} - Legacy database schema (only ONE file: legacy_{DB_NAME}_ddl.sql)
  - {{WORKPACKAGE_PLANNING}} - Workpackage processing order and dependencies
  
- Output Location: 
  - {{DATABASE_MODERNIZATION_OUTPUT}} - Modernized database schema and migration script
    - `new_{DB_NAME}_ddl.sql` - Modernized schema (DB_NAME auto-detected from legacy file)
    - `new_{DB_NAME}_migration.sql` - Data migration script
    - `schema_comparison_report.md` - Legacy vs modern schema comparison
    - `field_mapping.json` - Field-level migration mappings
  - {{DATABASE_MODERNIZATION_STATUS}} - Phase completion tracking
  - {{DATABASE_MODERNIZATION_ERRORS}} - Error logs

**Important**: Only ONE legacy schema file should exist in `{{DATABASE_GEN_SRC}}/`. The database type is auto-detected from the filename (e.g., `legacy_postgres_ddl.sql` → PostgreSQL, `legacy_sqlite_ddl.sql` → SQLite).

## Objective

Create modernized database schema based on business entities from business specifications (NOT from legacy database structure). Process workpackages sequentially, building up the database model incrementally. Generate migration mappings and scripts to bridge legacy and modern schemas.

**Critical Principle**: Design from **business requirements** (Chapter 2: Business Entities), not from **legacy database structure**. The legacy schema serves only as a reference for migration mapping.

## Sub-Phases

### Phase 5.0.0: Database Schema Creation
**Agent**: development_specialist_code_generation
**Task Document**: `phase_5.0.0_db_spec_creation.md`

For each workpackage:
1. **Detect target database type** from legacy schema filename
2. Extract business entities from business specification (Chapter 2)
3. Design modern tables with:
   - Surrogate keys (id)
   - Business keys (unique constraints)
   - Audit columns (created_at, updated_at, created_by, updated_by)
   - Optimistic locking (version column)
   - Proper indexes and foreign keys
4. Compare with legacy schema and document changes
5. Generate migration mappings (legacy → modern)
6. Generate migration script using correct SQL syntax for target database

### Phase 5.0.1: Database Schema Review
**Agent**: development_reviewer_code_generation
**Task Document**: `phase_5.0.1_db_spec_review.md`

For each workpackage:
1. Verify all business entities have tables
2. Verify modern design principles applied
3. Verify migration mappings complete
4. Verify SQL syntax valid for target database
5. Verify cross-workpackage consistency
6. Decision: APPROVED / REVISE / REJECT

## Modern Database Design Principles

All tables must include:

### 1. Surrogate Key (Primary Key)
Database-specific syntax:
- **PostgreSQL**: `id BIGSERIAL PRIMARY KEY`
- **SQLite**: `id INTEGER PRIMARY KEY AUTOINCREMENT`
- **MySQL**: `id BIGINT AUTO_INCREMENT PRIMARY KEY`
- **DB2**: `id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY`

### 2. Business Key (Natural Key)
```sql
user_id VARCHAR(8) NOT NULL UNIQUE
account_number VARCHAR(16) NOT NULL UNIQUE
```

### 3. Audit Columns (Required)
```sql
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
created_by VARCHAR(8) NOT NULL,
updated_by VARCHAR(8) NOT NULL
```

### 4. Optimistic Locking (Required)
Database-specific syntax:
- **PostgreSQL**: `version BIGINT NOT NULL DEFAULT 0`
- **SQLite**: `version INTEGER NOT NULL DEFAULT 0`
- **MySQL**: `version BIGINT NOT NULL DEFAULT 0`
- **DB2**: `version BIGINT NOT NULL DEFAULT 0`

### 5. Business Attributes
- Map from business entity attributes
- Use modern data types (VARCHAR, INTEGER, DECIMAL, TIMESTAMP, BOOLEAN)
- Apply NOT NULL constraints based on business rules
- Apply CHECK constraints for validation

### 6. Foreign Keys
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

### 7. Indexes
```sql
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
```

## Database Type Detection

The system automatically detects the target database type by scanning for the legacy schema file:

1. Scans `{{DATABASE_GEN_SRC}}/` for files matching `legacy_*_ddl.sql`
2. Extracts database name from filename (e.g., `postgres`, `sqlite`, `mysql`, `db2`)
3. Uses that database type for all generated schemas and migrations
4. Applies database-specific SQL syntax

**Supported Databases**:
- PostgreSQL (`legacy_postgres_ddl.sql`)
- SQLite (`legacy_sqlite_ddl.sql`)
- MySQL (`legacy_mysql_ddl.sql`)
- DB2 (`legacy_db2_ddl.sql`)
- Others (custom naming supported)

## Workflow Integration

This phase sits between:
- **Phase 4** (Test Case Generation) → **Phase 5.0** (Database Modernization) → **Phase 5.1** (Tech Spec Extraction)

The modernized schema is used by:
- Phase 5.1 (Tech Spec Extraction) - Reference schema for implementation guidance
- Phase 5.2+ (Code Generation) - Generate JPA entities matching modern schema
- Data Migration - Use migration script to migrate legacy data

## Success Criteria

- [ ] All workpackages processed sequentially
- [ ] Target database type correctly detected
- [ ] All business entities have modern tables
- [ ] All tables follow modern design principles
- [ ] Migration mappings complete for all tables/fields
- [ ] Comparison report documents all changes
- [ ] SQL syntax valid for target database
- [ ] Cross-workpackage consistency maintained
- [ ] Ready for Phase 5.1 (Tech Spec Extraction)

## Single Database Approach

**Important**: This phase generates only ONE modernized schema for ONE target database type. This avoids confusion and ensures consistency across all subsequent phases.

**User Action Required**: Before running Phase 5.0, ensure only ONE legacy schema file exists in `{{DATABASE_GEN_SRC}}/`. Delete any other database schema files to specify your target database.

