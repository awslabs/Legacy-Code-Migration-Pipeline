# Phase 5.0.0: Database Schema Creation

---

## Document Control

**Document Type**: Task Document (Agent Level)
**Phase**: Phase 5.0.0 - Database Schema Creation
**Version**: 1.0
**Date**: 2026-03-04
**Agent**: development_specialist_code_generation

---

## Context

**Input Locations**:
- Business Specification: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-EN-approved.md`
- Legacy Database Schema: `{{DATABASE_GEN_SRC}}/legacy_{DB_NAME}_ddl.sql` (auto-detect DB_NAME from available file)
- Workpackage Planning: `{{WORKPACKAGE_PLANNING}}`
- Previously Created Schema: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql` (if exists)
- Previous Comparison Report: `{{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md` (if exists)
- Previous Field Mapping: `{{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json` (if exists)

**Output Locations**:
- Updated DDL: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql`
- Updated Migration: `{{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_migration.sql`
- Updated Comparison Report: `{{DATABASE_MODERNIZATION_OUTPUT}}/schema_comparison_report.md`
- Updated Field Mapping: `{{DATABASE_MODERNIZATION_OUTPUT}}/field_mapping.json`
- Progress Tracking: `{{DATABASE_MODERNIZATION_STATUS}}`
- Error Reports: `{{DATABASE_MODERNIZATION_ERRORS}}`

**Note**: `{DB_NAME}` is auto-detected from the legacy schema filename (e.g., `postgres`, `sqlite`, `db2`, `mysql`). Only ONE legacy schema file should exist in `{{DATABASE_GEN_SRC}}/`.

---

## Objective

For the given workpackage, analyze business entities from the business specification and create/update modernized database schema that:
1. Reflects business entities (not legacy database structure)
2. Applies modern database design principles
3. Generates migration mappings from legacy to modern schema
4. Documents all schema changes and transformations

**Critical Principle**: Design from **business requirements** (Chapter 2: Business Entities), not from **legacy database structure**. The legacy schema serves only as a reference for migration mapping.

**Database Type Detection**: The target database type is determined by detecting the legacy schema file in `{{DATABASE_GEN_SRC}}/`. Only ONE legacy schema file should exist (e.g., `legacy_postgres_ddl.sql` OR `legacy_sqlite_ddl.sql`). The system will:
1. Scan `{{DATABASE_GEN_SRC}}/` for files matching pattern `legacy_*_ddl.sql`
2. Extract database name from filename (e.g., `postgres`, `sqlite`, `db2`, `mysql`)
3. Use that database type for all generated schemas and migrations

---

## Instructions

### Step 0: Detect Target Database Type

1. **Scan for legacy schema file**:
   ```
   legacy_files = LIST_FILES({{DATABASE_GEN_SRC}}/, pattern="legacy_*_ddl.sql")
   
   IF legacy_files.count == 0:
       ERROR "No legacy schema file found. Expected: {{DATABASE_GEN_SRC}}/legacy_{DB_NAME}_ddl.sql"
       HALT
   
   IF legacy_files.count > 1:
       ERROR "Multiple legacy schema files found. Please keep only ONE: " + legacy_files
       HALT
   
   legacy_file = legacy_files[0]
   DB_NAME = EXTRACT_DB_NAME(legacy_file)  # e.g., "postgres", "sqlite", "db2", "mysql"
   
   LOG "Detected target database: " + DB_NAME
   ```

2. **Set file paths based on detected database**:
   ```
   LEGACY_DDL = {{DATABASE_GEN_SRC}}/legacy_{DB_NAME}_ddl.sql
   MODERN_DDL = {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_ddl.sql
   MODERN_MIGRATION = {{DATABASE_MODERNIZATION_OUTPUT}}/new_{DB_NAME}_migration.sql
   ```

3. **Document database type**:
   - Add to progress tracking
   - Add to comparison report header
   - Use for SQL syntax generation

---

## Instructions

---

### Step 1: Read Business Specification

1. **Load the approved business specification** for the current workpackage
   - File: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-FLOW_{FLOW_ID}-specification-EN-approved.md`

2. **Extract business entities from Chapter 2**:
   - Entity identifier (BE-XXX-YYY)
   - Entity name
   - Entity description
   - Entity attributes with data types
   - Relationships to other entities
   - Business rules affecting the entity (from Chapter 3)

3. **Document extracted entities**:
   ```markdown
   ## Workpackage WP-{ID}: Business Entities
   
   ### BE-{ID}-001: {Entity Name}
   - Description: {Entity description}
   - Attributes:
     - {attribute_name}: {data_type} - {description}
     - {attribute_name}: {data_type} - {description}
   - Relationships:
     - {relationship_type} to {other_entity}
   - Business Rules:
     - BR-{ID}-XXX: {rule description}
   ```

---

### Step 2: Design Modern Database Schema

For each business entity, create a modern table definition following these principles:

#### 2.1 Table Naming
- Use plural, lowercase, snake_case: `users`, `credit_cards`, `transactions`
- Avoid legacy COBOL naming conventions
- Use descriptive, business-oriented names

#### 2.2 Primary Key (Surrogate Key)
```sql
id BIGINT PRIMARY KEY AUTOINCREMENT  -- SQLite
id BIGSERIAL PRIMARY KEY             -- PostgreSQL
```
- Always use `id` as the surrogate primary key
- Auto-incrementing integer type

#### 2.3 Business Key (Natural Key)
```sql
user_id VARCHAR(8) NOT NULL UNIQUE
account_number VARCHAR(16) NOT NULL UNIQUE
```
- Add unique constraint on business identifier
- Index automatically created by UNIQUE constraint

#### 2.4 Audit Columns (Required for All Tables)
```sql
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
created_by VARCHAR(8) NOT NULL,
updated_by VARCHAR(8) NOT NULL
```
- Track who created and last modified the record
- Track when record was created and last modified

#### 2.5 Optimistic Locking (Required for All Tables)
```sql
version INTEGER NOT NULL DEFAULT 0  -- SQLite
version BIGINT NOT NULL DEFAULT 0   -- PostgreSQL
```
- Enables optimistic locking for concurrent updates
- Incremented on each update

#### 2.6 Business Attributes
- Map business entity attributes to columns
- Use modern data types (not COBOL equivalents):
  - `VARCHAR(n)` for strings
  - `INTEGER` or `BIGINT` for numbers
  - `DECIMAL(p,s)` for money/precise decimals
  - `TIMESTAMP` for dates/times
  - `BOOLEAN` for true/false
- Apply NOT NULL constraints based on business rules
- Apply CHECK constraints for validation rules

#### 2.7 Foreign Keys
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```
- Define relationships between tables
- Use appropriate ON DELETE/ON UPDATE actions

#### 2.8 Indexes
```sql
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
```
- Index foreign keys
- Index frequently queried columns
- Index columns used in WHERE clauses

---

### Step 3: Generate DDL Scripts

**Important**: Generate DDL using syntax appropriate for the detected `{DB_NAME}`.

#### 3.1 Database-Specific DDL Format

The DDL syntax varies by database type. Use the appropriate syntax based on detected `{DB_NAME}`:

##### PostgreSQL DDL Format (`DB_NAME=postgres`)
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Flow: {FLOW_ID}
-- Business Entity: BE-{ID}-{NUM} ({Entity Name})
-- Database: PostgreSQL
-- ============================================

CREATE TABLE {table_name} (
    -- Surrogate Key
    id BIGSERIAL PRIMARY KEY,
    
    -- Business Key
    {business_key} VARCHAR(n) NOT NULL UNIQUE,
    
    -- Business Attributes
    {attribute1} {datatype} NOT NULL,
    {attribute2} {datatype},
    
    -- Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(8) NOT NULL,
    updated_by VARCHAR(8) NOT NULL,
    
    -- Optimistic Locking
    version BIGINT NOT NULL DEFAULT 0,
    
    -- Foreign Keys
    CONSTRAINT fk_{table_name}_{foreign_key} 
        FOREIGN KEY ({foreign_key}) 
        REFERENCES {parent_table}(id) 
        ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_{table_name}_{business_key} ON {table_name}({business_key});
CREATE INDEX idx_{table_name}_{foreign_key} ON {table_name}({foreign_key});

-- Comments
COMMENT ON TABLE {table_name} IS 'Business Entity: BE-{ID}-{NUM} - {Entity Description}';
COMMENT ON COLUMN {table_name}.{column} IS '{Column Description}';
```

##### SQLite DDL Format (`DB_NAME=sqlite`)
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Flow: {FLOW_ID}
-- Business Entity: BE-{ID}-{NUM} ({Entity Name})
-- Database: SQLite
-- ============================================

CREATE TABLE {table_name} (
    -- Surrogate Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Business Key
    {business_key} VARCHAR(n) NOT NULL UNIQUE,
    
    -- Business Attributes
    {attribute1} {datatype} NOT NULL,
    {attribute2} {datatype},
    
    -- Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(8) NOT NULL,
    updated_by VARCHAR(8) NOT NULL,
    
    -- Optimistic Locking
    version INTEGER NOT NULL DEFAULT 0
);

-- Indexes
CREATE INDEX idx_{table_name}_{business_key} ON {table_name}({business_key});
CREATE INDEX idx_{table_name}_{foreign_key} ON {table_name}({foreign_key});

-- Foreign Keys (SQLite requires foreign_keys pragma to be enabled)
-- PRAGMA foreign_keys = ON;
```

##### MySQL DDL Format (`DB_NAME=mysql`)
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Flow: {FLOW_ID}
-- Business Entity: BE-{ID}-{NUM} ({Entity Name})
-- Database: MySQL
-- ============================================

CREATE TABLE {table_name} (
    -- Surrogate Key
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Business Key
    {business_key} VARCHAR(n) NOT NULL UNIQUE,
    
    -- Business Attributes
    {attribute1} {datatype} NOT NULL,
    {attribute2} {datatype},
    
    -- Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(8) NOT NULL,
    updated_by VARCHAR(8) NOT NULL,
    
    -- Optimistic Locking
    version BIGINT NOT NULL DEFAULT 0,
    
    -- Foreign Keys
    CONSTRAINT fk_{table_name}_{foreign_key} 
        FOREIGN KEY ({foreign_key}) 
        REFERENCES {parent_table}(id) 
        ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_{table_name}_{business_key} ({business_key}),
    INDEX idx_{table_name}_{foreign_key} ({foreign_key})
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

##### DB2 DDL Format (`DB_NAME=db2`)
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Flow: {FLOW_ID}
-- Business Entity: BE-{ID}-{NUM} ({Entity Name})
-- Database: DB2
-- ============================================

CREATE TABLE {table_name} (
    -- Surrogate Key
    id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Business Key
    {business_key} VARCHAR(n) NOT NULL UNIQUE,
    
    -- Business Attributes
    {attribute1} {datatype} NOT NULL,
    {attribute2} {datatype},
    
    -- Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(8) NOT NULL,
    updated_by VARCHAR(8) NOT NULL,
    
    -- Optimistic Locking
    version BIGINT NOT NULL DEFAULT 0,
    
    -- Foreign Keys
    CONSTRAINT fk_{table_name}_{foreign_key} 
        FOREIGN KEY ({foreign_key}) 
        REFERENCES {parent_table}(id) 
        ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_{table_name}_{business_key} ON {table_name}({business_key});
CREATE INDEX idx_{table_name}_{foreign_key} ON {table_name}({foreign_key});

-- Comments
COMMENT ON TABLE {table_name} IS 'Business Entity: BE-{ID}-{NUM} - {Entity Description}';
COMMENT ON COLUMN {table_name}.{column} IS '{Column Description}';
```

#### 3.2 Append to Existing File
- If `new_{DB_NAME}_ddl.sql` exists, append new tables
- Add clear section headers for each workpackage
- Maintain chronological order (WP-001, WP-002, etc.)
- Use database-specific syntax based on `{DB_NAME}`

---

### Step 4: Compare with Legacy Schema

1. **Load legacy schema**:
   - Read `{{DATABASE_GEN_SRC}}/legacy_{DB_NAME}_ddl.sql`
   - Identify legacy tables related to this workpackage

2. **Identify discrepancies**:
   - **New tables**: Business entities not in legacy
   - **Removed tables**: Legacy tables not needed in modern schema
   - **Renamed tables**: Legacy table name → Modern table name
   - **New columns**: Attributes not in legacy
   - **Removed columns**: Legacy columns not needed
   - **Renamed columns**: Legacy column → Modern column
   - **Changed data types**: COBOL types → Modern types
   - **Changed constraints**: New constraints or removed constraints

3. **Document in comparison report**:
   ```markdown
   ## Workpackage WP-{ID}: Schema Changes
   
   ### New Tables
   | Modern Table | Business Entity | Description |
   |--------------|-----------------|-------------|
   | users | BE-{ID}-001 | User accounts |
   
   ### Modified Tables
   | Legacy Table | Modern Table | Change Type | Description |
   |--------------|--------------|-------------|-------------|
   | USRSEC | users | Renamed | Modernized naming |
   
   ### Removed Tables
   | Legacy Table | Reason |
   |--------------|--------|
   | TEMP_TABLE | Temporary processing, not needed |
   
   ### Field Changes
   | Legacy Table | Legacy Field | Modern Table | Modern Field | Change Type | Transformation | Notes |
   |--------------|--------------|--------------|--------------|-------------|----------------|-------|
   | USRSEC | SEC-USR-ID | users | user_id | Renamed | TRIM(SEC-USR-ID) | COBOL to modern |
   | USRSEC | SEC-USR-FNAME | users | first_name | Renamed | TRIM(SEC-USR-FNAME) | COBOL to modern |
   | N/A | N/A | users | id | Added | AUTO_INCREMENT | Surrogate key |
   | N/A | N/A | users | version | Added | DEFAULT 0 | Optimistic locking |
   | N/A | N/A | users | created_at | Added | CURRENT_TIMESTAMP | Audit column |
   ```

---

### Step 5: Generate Migration Mappings

Create field-to-field mappings for data migration:

#### 5.1 Field Mapping JSON Format
```json
{
  "workpackages": [
    {
      "workpackageId": "WP-{ID}",
      "flowId": "{FLOW_ID}",
      "mappings": [
        {
          "legacyTable": "USRSEC",
          "modernTable": "users",
          "tableMapping": {
            "type": "one-to-one",
            "description": "Direct mapping with field transformations"
          },
          "fields": [
            {
              "legacyField": "SEC-USR-ID",
              "modernField": "user_id",
              "dataType": {
                "legacy": "CHAR(8)",
                "modern": "VARCHAR(8)"
              },
              "transformation": "TRIM(SEC-USR-ID)",
              "notes": "Remove trailing spaces from COBOL field"
            },
            {
              "legacyField": "SEC-USR-FNAME",
              "modernField": "first_name",
              "dataType": {
                "legacy": "CHAR(20)",
                "modern": "VARCHAR(20)"
              },
              "transformation": "TRIM(SEC-USR-FNAME)",
              "notes": "Remove trailing spaces"
            },
            {
              "legacyField": null,
              "modernField": "id",
              "dataType": {
                "legacy": null,
                "modern": "BIGINT"
              },
              "transformation": "AUTO_INCREMENT",
              "notes": "New surrogate key, auto-generated"
            },
            {
              "legacyField": null,
              "modernField": "created_at",
              "dataType": {
                "legacy": null,
                "modern": "TIMESTAMP"
              },
              "transformation": "CURRENT_TIMESTAMP",
              "notes": "New audit column, set to migration time"
            }
          ],
          "unmappableFields": [
            {
              "legacyField": "SEC-TEMP-FLAG",
              "reason": "Temporary processing flag, not needed in modern system",
              "action": "Discard"
            }
          ]
        }
      ]
    }
  ]
}
```

#### 5.2 Append to Existing Mapping File
- If `field_mapping.json` exists, append new workpackage mappings
- Maintain JSON structure
- Ensure valid JSON syntax

---

### Step 6: Generate Migration Scripts

Create SQL script to migrate data from legacy to modern schema:

#### 6.1 Database-Specific Migration Script Format

Use syntax appropriate for the detected `{DB_NAME}`:

##### PostgreSQL Migration Script
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Migration: {Legacy Table} → {Modern Table}
-- Database: PostgreSQL
-- ============================================

-- Insert data from legacy to modern table
INSERT INTO {modern_table} (
    {business_key},
    {attribute1},
    {attribute2},
    created_at,
    updated_at,
    created_by,
    updated_by,
    version
)
SELECT 
    TRIM({legacy_business_key}) AS {business_key},
    TRIM({legacy_attribute1}) AS {attribute1},
    {legacy_attribute2} AS {attribute2},
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at,
    'MIGRATION' AS created_by,
    'MIGRATION' AS updated_by,
    0 AS version
FROM {legacy_table}
WHERE {legacy_business_key} IS NOT NULL
ON CONFLICT ({business_key}) DO NOTHING;

-- Verification query
SELECT 
    'Migration Verification' AS check_type,
    COUNT(*) AS legacy_count,
    (SELECT COUNT(*) FROM {modern_table}) AS modern_count,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM {modern_table}) 
        THEN 'SUCCESS' 
        ELSE 'MISMATCH' 
    END AS status
FROM {legacy_table};
```

##### SQLite Migration Script
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Migration: {Legacy Table} → {Modern Table}
-- Database: SQLite
-- ============================================

-- Insert data from legacy to modern table
INSERT INTO {modern_table} (
    {business_key},
    {attribute1},
    {attribute2},
    created_at,
    updated_at,
    created_by,
    updated_by,
    version
)
SELECT 
    TRIM({legacy_business_key}) AS {business_key},
    TRIM({legacy_attribute1}) AS {attribute1},
    {legacy_attribute2} AS {attribute2},
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at,
    'MIGRATION' AS created_by,
    'MIGRATION' AS updated_by,
    0 AS version
FROM {legacy_table}
WHERE {legacy_business_key} IS NOT NULL;

-- Verification query
SELECT 
    'Migration Verification' AS check_type,
    COUNT(*) AS legacy_count,
    (SELECT COUNT(*) FROM {modern_table}) AS modern_count,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM {modern_table}) 
        THEN 'SUCCESS' 
        ELSE 'MISMATCH' 
    END AS status
FROM {legacy_table};
```

##### MySQL Migration Script
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Migration: {Legacy Table} → {Modern Table}
-- Database: MySQL
-- ============================================

-- Insert data from legacy to modern table
INSERT INTO {modern_table} (
    {business_key},
    {attribute1},
    {attribute2},
    created_at,
    updated_at,
    created_by,
    updated_by,
    version
)
SELECT 
    TRIM({legacy_business_key}) AS {business_key},
    TRIM({legacy_attribute1}) AS {attribute1},
    {legacy_attribute2} AS {attribute2},
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at,
    'MIGRATION' AS created_by,
    'MIGRATION' AS updated_by,
    0 AS version
FROM {legacy_table}
WHERE {legacy_business_key} IS NOT NULL
ON DUPLICATE KEY UPDATE {business_key} = {business_key};

-- Verification query
SELECT 
    'Migration Verification' AS check_type,
    COUNT(*) AS legacy_count,
    (SELECT COUNT(*) FROM {modern_table}) AS modern_count,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM {modern_table}) 
        THEN 'SUCCESS' 
        ELSE 'MISMATCH' 
    END AS status
FROM {legacy_table};
```

##### DB2 Migration Script
```sql
-- ============================================
-- Workpackage: WP-{ID} - {Workpackage Name}
-- Migration: {Legacy Table} → {Modern Table}
-- Database: DB2
-- ============================================

-- Insert data from legacy to modern table
INSERT INTO {modern_table} (
    {business_key},
    {attribute1},
    {attribute2},
    created_at,
    updated_at,
    created_by,
    updated_by,
    version
)
SELECT 
    TRIM({legacy_business_key}) AS {business_key},
    TRIM({legacy_attribute1}) AS {attribute1},
    {legacy_attribute2} AS {attribute2},
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at,
    'MIGRATION' AS created_by,
    'MIGRATION' AS updated_by,
    0 AS version
FROM {legacy_table}
WHERE {legacy_business_key} IS NOT NULL;

-- Verification query
SELECT 
    'Migration Verification' AS check_type,
    COUNT(*) AS legacy_count,
    (SELECT COUNT(*) FROM {modern_table}) AS modern_count,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM {modern_table}) 
        THEN 'SUCCESS' 
        ELSE 'MISMATCH' 
    END AS status
FROM {legacy_table};
```

#### 6.2 Append to Existing Migration File
- If `new_{DB_NAME}_migration.sql` exists, append new migrations
- Add clear section headers for each workpackage
- Include verification queries
- Use database-specific syntax based on `{DB_NAME}`

---

### Step 7: Update Progress Tracking

Update `{{DATABASE_MODERNIZATION_STATUS}}` with:

```json
{
  "phaseId": "05.0.0-database-modernization",
  "status": "in_progress",
  "targetDatabase": "{DB_NAME}",
  "currentWorkpackage": "WP-{ID}",
  "workpackages": [
    {
      "workpackageId": "WP-{ID}",
      "workpackageName": "{Workpackage Name}",
      "flowId": "{FLOW_ID}",
      "status": "completed",
      "businessEntities": [
        {
          "entityId": "BE-{ID}-001",
          "entityName": "{Entity Name}",
          "modernTable": "{table_name}",
          "legacyTable": "{legacy_table}",
          "mappingStatus": "complete"
        }
      ],
      "tablesCreated": 3,
      "fieldsAdded": 15,
      "migrationMappings": 3,
      "completedDate": "2026-03-04"
    }
  ],
  "completedCount": 1,
  "totalCount": 26,
  "lastUpdated": "2026-03-04"
}
```

---

## Output Format Examples

### Example 1: DDL for User Entity (Database-Specific)

**For PostgreSQL** (`DB_NAME=postgres`):
```sql
-- ============================================
-- Workpackage: WP-002 - User Management
-- Flow: FLOW_COUSR01C
-- Business Entity: BE-002-001 (User)
-- Database: PostgreSQL
-- ============================================

CREATE TABLE users (
    -- Surrogate Key
    id BIGSERIAL PRIMARY KEY,
    
    -- Business Key
    user_id VARCHAR(8) NOT NULL UNIQUE,
    
    -- Business Attributes
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    
    -- Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(8) NOT NULL,
    updated_by VARCHAR(8) NOT NULL,
    
    -- Optimistic Locking
    version BIGINT NOT NULL DEFAULT 0,
    
    -- Constraints
    CHECK (user_type IN ('ADMIN', 'REGULAR'))
);

-- Indexes
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_user_type ON users(user_type);
```

**For SQLite** (`DB_NAME=sqlite`):
```sql
-- ============================================
-- Workpackage: WP-002 - User Management
-- Flow: FLOW_COUSR01C
-- Business Entity: BE-002-001 (User)
-- Database: SQLite
-- ============================================

CREATE TABLE users (
    -- Surrogate Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Business Key
    user_id VARCHAR(8) NOT NULL UNIQUE,
    
    -- Business Attributes
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    
    -- Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(8) NOT NULL,
    updated_by VARCHAR(8) NOT NULL,
    
    -- Optimistic Locking
    version INTEGER NOT NULL DEFAULT 0,
    
    -- Constraints
    CHECK (user_type IN ('ADMIN', 'REGULAR'))
);

-- Indexes
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_user_type ON users(user_type);
```

### Example 2: Comparison Report Entry

```markdown
## Workpackage WP-002: User Management

### New Tables
| Modern Table | Business Entity | Description |
|--------------|-----------------|-------------|
| users | BE-002-001 | System user accounts with authentication |

### Field Changes
| Legacy Table | Legacy Field | Modern Table | Modern Field | Change Type | Transformation | Notes |
|--------------|--------------|--------------|--------------|-------------|----------------|-------|
| USRSEC | SEC-USR-ID | users | user_id | Renamed | TRIM(SEC-USR-ID) | COBOL to modern naming |
| USRSEC | SEC-USR-FNAME | users | first_name | Renamed | TRIM(SEC-USR-FNAME) | COBOL to modern naming |
| USRSEC | SEC-USR-LNAME | users | last_name | Renamed | TRIM(SEC-USR-LNAME) | COBOL to modern naming |
| USRSEC | SEC-USR-TYPE | users | user_type | Renamed + Type Change | CASE WHEN SEC-USR-TYPE='A' THEN 'ADMIN' ELSE 'REGULAR' END | Single char to enum string |
| N/A | N/A | users | id | Added | AUTO_INCREMENT | New surrogate key |
| N/A | N/A | users | version | Added | DEFAULT 0 | Optimistic locking |
| N/A | N/A | users | created_at | Added | CURRENT_TIMESTAMP | Audit column |
| N/A | N/A | users | updated_at | Added | CURRENT_TIMESTAMP | Audit column |
| N/A | N/A | users | created_by | Added | 'MIGRATION' | Audit column |
| N/A | N/A | users | updated_by | Added | 'MIGRATION' | Audit column |
```

---

## Quality Criteria

Before completing this phase, verify:

- [ ] Target database type detected from legacy schema filename
- [ ] All business entities from Chapter 2 have corresponding tables
- [ ] All tables have surrogate key (`id`) with correct data type for target database
- [ ] All tables have business key with UNIQUE constraint
- [ ] All tables have audit columns (created_at, updated_at, created_by, updated_by)
- [ ] All tables have version column for optimistic locking
- [ ] All business attributes mapped to columns
- [ ] All relationships modeled with foreign keys
- [ ] Appropriate indexes defined
- [ ] DDL script generated using correct syntax for target database
- [ ] Comparison report updated with all changes
- [ ] Field mapping JSON updated with all mappings
- [ ] Migration script generated using correct syntax for target database
- [ ] Progress tracking updated with target database type
- [ ] No SQL syntax errors for target database

---

## Error Handling

### Common Errors and Solutions

1. **Business Entity Ambiguity**
   - Error: Business entity description unclear
   - Solution: Document ambiguity in error log, use best judgment, flag for review
   - Log to: `{{DATABASE_MODERNIZATION_ERRORS}}`

2. **Complex Relationships**
   - Error: Many-to-many or complex relationships
   - Solution: Create junction tables with proper foreign keys
   - Document: Add explanation in comparison report

3. **Legacy Data Type Mapping**
   - Error: Unclear how to map legacy COBOL type to modern SQL type
   - Solution: Use conservative mapping (e.g., COBOL PIC 9(5)V99 → DECIMAL(7,2))
   - Document: Add notes in field mapping JSON

4. **Unmappable Legacy Fields**
   - Error: Legacy field has no modern equivalent
   - Solution: Document in unmappableFields section of mapping JSON
   - Action: Flag for manual review

5. **SQL Syntax Errors**
   - Error: Invalid SQL syntax
   - Solution: Validate SQL before writing to file
   - Test: Use SQL parser if available

---

## Success Criteria

This phase is complete when:
- [ ] Target database type detected and documented
- [ ] All business entities have modern table definitions
- [ ] DDL script updated using correct syntax for target database
- [ ] Migration script updated using correct syntax for target database
- [ ] Comparison report documents all changes
- [ ] Field mapping JSON documents all mappings
- [ ] Progress tracking updated with database type
- [ ] No critical errors logged
- [ ] Ready for Phase 5.0.1 (Review)

---

## End of Task Document
