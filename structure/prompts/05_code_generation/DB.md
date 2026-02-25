# Phase: DB Adaption 

## Context
- Project Structure: Standard migration project folder structure
- Input Location: 
  - {{BUSINESS_SPECIFICATION_BASE_PATH}} - Workpackage-based business specifications
  - {{DATABASE_GEN_SRC}} - Schema and Migration files for the database
  - {{SOURCE_CODE_ANALYSIS_OUTPUT}} - Legacy code analysis and dependencies
  - {{SOURCE_CODE}} - Original legacy source code
  - {{LEGACY_SPECIFICATION}} - Legacy documentation (Chapter 6)
  - {{TARGET_SPECIFICATION}} - Target framework specifications (Spring Boot, Spring Modulith)

- Output Location: 
  - {{DATABASE_GEN_SRC}} - modified Schema and Migrartion files.
  - {{DATABASE_PROGRESS_TRACKING}} - Phase completion tracking

## Objective

Create a complete, maintainable, production-ready DB Schema application (new_sqlite_ddl.sql)that preserves all business entities and dependencies between them. Process workpackages sequentially but organize code by domain modules. Ensure full traceability between generated code and business specifications, and adhere to Java best practices and modern development standards.
Once done, correlate this to the legacy db's schemas and migration script.
Identify changes and provide a second (updated) migration script (new_sqlite_migration.sql).
There is no generated code yet. Only rely on the Business Specification.
Target Platform is sqlite.

