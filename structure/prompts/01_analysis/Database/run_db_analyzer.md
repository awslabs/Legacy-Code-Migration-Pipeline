# Database Analysis - Using Database Analyzer Tool

## Objective

Analyze legacy database files (VSAM, Sequential, DDL) to generate equivalent relational database schemas and migration scripts for target systems (SQLite, PostgreSQL).

---

## Prerequisites

**Tool**: Database Analyzer (part of ACM Tools at `tools/acm-tools/tools/database_analyzer`)
**Input**: Legacy code in `{{SOURCE_CODE}}`
**Output**: `{{DATABASE_GEN_SRC}}`

---

## Execution Steps

### Step 1: Run the Database Analyzer

Execute the database analyzer tool:

```bash
python3 -m tools.acm-tools.tools.database_analyzer analyze \
  --base-path . \
  --legacy-root {{SOURCE_CODE}} \
  --output-dir {{DATABASE_GEN_SRC}} \
  --verbose
```

**Note**: Run this command from the project root directory (where the `tools/` folder is located).

**Note**: Run this command from the `{{PROJECT_BASE_PATH}}` directory.

The tool will:

**Note**: Run this command from the `carddemo` directory using the `cwd` parameter.

The tool will:
- Scan JCL files for DD statements (handles multi-line continuations)
- Discover VSAM files (KSDS, ESDS, RRDS) and Sequential files (PS)
- Parse COBOL copybooks for record structures
- Filter out system files, backups, and duplicate formats
- Generate DDL scripts for SQLite and PostgreSQL
- Generate migration scripts for both target systems
- Provide detailed statistics

### Step 2: Review Generated Deliverables

Check the following outputs in `carddemo/output/analysis/database/gen_src_db`:

1. **PostgreSQL DDL**: `postgresql_ddl.sql`
   - Table definitions with proper data types
   - Primary keys from VSAM key fields
   - Indexes for sequential files

2. **SQLite DDL**: `sqlite_ddl.sql`
   - SQLite-compatible table definitions
   - Auto-increment primary keys
   - Sequence tracking for PS files

3. **Migration Scripts**:
   - `postgresql_migration.sql`
   - `sqlite_migration.sql`

### Step 3: Validate Results

Verify the analyzer found the expected business tables:

```bash
grep "^CREATE TABLE" /Users/kerimman/Agentic_Code_Migrator/carddemo/output/analysis/database/gen_src_db/postgresql_ddl.sql | wc -l
```

Review the discovered tables and verify they match the expected business entities from the legacy system.

### Step 4: Create Analysis Report

Document findings in `carddemo/output/analysis/database/reports/DB_Source_Analysis_Report.md`:

**Required Sections**:
1. Executive Summary
   - Total tables discovered
   - VSAM files converted
   - Sequential files converted
   - Files excluded (system, backup, duplicates)

2. Database Inventory
   - List all tables with source type (VSAM KSDS/ESDS/RRDS or PS)
   - Copybook references
   - Primary key strategy

3. Target System Compatibility
   - PostgreSQL: Full support, SERIAL keys, NUMERIC types
   - SQLite: Full support, AUTOINCREMENT keys, simplified types

4. Migration Recommendations
   - Execution order (reference tables first)
   - Data validation steps
   - Rollback procedures

---

## Expected Deliverables

1. **DDL Scripts**: `carddemo/output/analysis/database/gen_src_db/`
   - `postgresql_ddl.sql` - PostgreSQL table definitions
   - `sqlite_ddl.sql` - SQLite table definitions
   - All constraints and indexes

2. **Migration Scripts**: `carddemo/output/analysis/database/gen_src_db/`
   - `postgresql_migration.sql` - PostgreSQL data migration procedures
   - `sqlite_migration.sql` - SQLite data migration procedures
   - Validation queries

3. **Analysis Report**: `carddemo/output/analysis/database/reports/DB_Source_Analysis_Report.md`
   - Comprehensive findings
   - Compatibility assessment
   - Migration strategy

4. **Progress Tracking**: `carddemo/output/analysis/database/progress/Analysis_Status.json`
   - Status: "Complete"
   - Tables analyzed count
   - Target systems evaluated

---

## Quality Checks

- [ ] All expected business tables discovered
- [ ] Multi-line DD statements handled correctly
- [ ] System files excluded (LOADLIB, SDFHLOAD, DFHCSD)
- [ ] Backup files excluded (*.BKUP, GDG generations)
- [ ] Duplicate formats excluded (prefer VSAM KSDS over PS)
- [ ] Column names preserved from copybooks
- [ ] Primary keys correctly mapped from VSAM key fields
- [ ] DDL scripts are syntactically valid

---

## Tool Configuration

The analyzer uses these default settings:
- `exclude_system_files`: True
- `exclude_backups`: True
- `exclude_duplicates`: True
- `verbose`: True (shows detailed progress)

To modify behavior, edit the `config` parameter in the database analyzer tool.

---

## Troubleshooting

**Issue**: Missing tables
- Check JCL files exist in legacy code directory
- Verify copybooks in legacy code directory
- Review verbose output for skipped files

**Issue**: Incorrect table structure
- Check copybook parsing in analyzer
- Verify PIC clause to SQL type mappings
- Review field-level comments in generated DDL

**Issue**: Too many tables
- Review excluded files list in verbose output
- Check if duplicate detection is working
- Verify system file patterns are correct

---

## Success Criteria

Task complete when:
- [ ] All deliverables generated
- [ ] Expected business tables found
- [ ] DDL scripts validated
- [ ] Analysis report comprehensive
- [ ] Progress tracking updated
- [ ] Ready for review
