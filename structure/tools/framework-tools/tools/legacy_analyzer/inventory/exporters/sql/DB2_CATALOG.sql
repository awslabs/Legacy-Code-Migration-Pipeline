-- DB2 Catalog Export Script
-- Purpose: Extract DB2 catalog information for artifact analysis
-- Output:  CSV format data about DB2 objects
--
-- Instructions:
-- 1. Connect to DB2 subsystem
-- 2. Run this script using SPUFI, QMF, or batch DB2
-- 3. Export results to CSV format
-- 4. Download for analysis
--
-- Usage in SPUFI:
--   - Set output dataset
--   - Set output format to CSV
--   - Execute script
--
-- Usage in batch:
--   - Use DSNTEP2 or DSNTIAUL utility
--   - Specify output dataset
--   - Submit JCL with this SQL
--
------------------------------------------------------------------------

-- Set output format (if using QMF)
-- SET PROFILE (FORM=CSV);

------------------------------------------------------------------------
-- Extract Table Information
------------------------------------------------------------------------
SELECT 
    'TABLE' AS OBJECT_TYPE,
    CREATOR AS SCHEMA_NAME,
    NAME AS OBJECT_NAME,
    TYPE AS TABLE_TYPE,
    CARDINALITY AS ROW_COUNT,
    NPAGES AS PAGE_COUNT,
    PCTPAGES AS PCT_PAGES_USED,
    CREATED AS CREATE_DATE,
    ALTEREDTS AS LAST_ALTERED,
    STATS_TIME AS LAST_STATS_DATE,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'C' THEN 'CHECK_PENDING'
        WHEN 'R' THEN 'RESTRICTED'
        ELSE 'UNKNOWN'
    END AS STATUS
FROM SYSIBM.SYSTABLES
WHERE TYPE IN ('T', 'G')  -- Tables and Global Temp Tables
    AND CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY CREATOR, NAME;

------------------------------------------------------------------------
-- Extract View Information
------------------------------------------------------------------------
SELECT 
    'VIEW' AS OBJECT_TYPE,
    CREATOR AS SCHEMA_NAME,
    NAME AS OBJECT_NAME,
    'VIEW' AS VIEW_TYPE,
    CREATED AS CREATE_DATE,
    ALTEREDTS AS LAST_ALTERED,
    CHECK AS CHECK_OPTION,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'I' THEN 'INOPERATIVE'
        ELSE 'UNKNOWN'
    END AS STATUS
FROM SYSIBM.SYSTABLES
WHERE TYPE = 'V'  -- Views
    AND CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY CREATOR, NAME;

------------------------------------------------------------------------
-- Extract Index Information
------------------------------------------------------------------------
SELECT 
    'INDEX' AS OBJECT_TYPE,
    CREATOR AS SCHEMA_NAME,
    NAME AS INDEX_NAME,
    TBCREATOR AS TABLE_SCHEMA,
    TBNAME AS TABLE_NAME,
    UNIQUERULE AS UNIQUE_TYPE,
    CLUSTERING AS IS_CLUSTERING,
    CREATED AS CREATE_DATE,
    STATS_TIME AS LAST_STATS_DATE,
    FULLKEYCARDINALITY AS DISTINCT_KEYS,
    NLEAF AS LEAF_PAGES,
    NLEVELS AS INDEX_LEVELS
FROM SYSIBM.SYSINDEXES
WHERE CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY CREATOR, NAME;

------------------------------------------------------------------------
-- Extract Stored Procedure Information
------------------------------------------------------------------------
SELECT 
    'PROCEDURE' AS OBJECT_TYPE,
    SCHEMA AS SCHEMA_NAME,
    NAME AS PROCEDURE_NAME,
    LANGUAGE AS PROC_LANGUAGE,
    DETERMINISTIC AS IS_DETERMINISTIC,
    EXTERNAL_ACTION AS HAS_EXTERNAL_ACTION,
    CREATED AS CREATE_DATE,
    LAST_REGEN AS LAST_REGENERATED,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'I' THEN 'INOPERATIVE'
        ELSE 'UNKNOWN'
    END AS STATUS
FROM SYSIBM.SYSROUTINES
WHERE ROUTINETYPE = 'P'  -- Procedures
    AND SCHEMA NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY SCHEMA, NAME;

------------------------------------------------------------------------
-- Extract User-Defined Function Information
------------------------------------------------------------------------
SELECT 
    'FUNCTION' AS OBJECT_TYPE,
    SCHEMA AS SCHEMA_NAME,
    NAME AS FUNCTION_NAME,
    LANGUAGE AS FUNC_LANGUAGE,
    DETERMINISTIC AS IS_DETERMINISTIC,
    EXTERNAL_ACTION AS HAS_EXTERNAL_ACTION,
    CREATED AS CREATE_DATE,
    LAST_REGEN AS LAST_REGENERATED,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'I' THEN 'INOPERATIVE'
        ELSE 'UNKNOWN'
    END AS STATUS
FROM SYSIBM.SYSROUTINES
WHERE ROUTINETYPE = 'F'  -- Functions
    AND SCHEMA NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY SCHEMA, NAME;

------------------------------------------------------------------------
-- Extract Trigger Information
------------------------------------------------------------------------
SELECT 
    'TRIGGER' AS OBJECT_TYPE,
    SCHEMA AS SCHEMA_NAME,
    NAME AS TRIGGER_NAME,
    TBOWNER AS TABLE_SCHEMA,
    TBNAME AS TABLE_NAME,
    TRIGEVENT AS TRIGGER_EVENT,
    TRIGTIME AS TRIGGER_TIME,
    CREATED AS CREATE_DATE,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'I' THEN 'INOPERATIVE'
        ELSE 'UNKNOWN'
    END AS STATUS
FROM SYSIBM.SYSTRIGGERS
WHERE SCHEMA NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY SCHEMA, NAME;

------------------------------------------------------------------------
-- Extract Tablespace Information
------------------------------------------------------------------------
SELECT 
    'TABLESPACE' AS OBJECT_TYPE,
    DBNAME AS DATABASE_NAME,
    NAME AS TABLESPACE_NAME,
    CREATOR AS CREATOR,
    TYPE AS TS_TYPE,
    PGSIZE AS PAGE_SIZE,
    SEGSIZE AS SEGMENT_SIZE,
    CREATED AS CREATE_DATE,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'C' THEN 'CHECK_PENDING'
        WHEN 'R' THEN 'RESTRICTED'
        WHEN 'S' THEN 'STOPPED'
        ELSE 'UNKNOWN'
    END AS STATUS,
    NACTIVE AS ACTIVE_PAGES,
    SPACE AS TOTAL_SPACE_KB
FROM SYSIBM.SYSTABLESPACE
WHERE DBNAME NOT IN ('DSNDB01', 'DSNDB04', 'DSNDB06', 'DSNDB07')
ORDER BY DBNAME, NAME;

------------------------------------------------------------------------
-- Extract Database Information
------------------------------------------------------------------------
SELECT 
    'DATABASE' AS OBJECT_TYPE,
    NAME AS DATABASE_NAME,
    CREATOR AS CREATOR,
    CREATED AS CREATE_DATE,
    CASE STATUS
        WHEN 'A' THEN 'AVAILABLE'
        WHEN 'S' THEN 'STOPPED'
        ELSE 'UNKNOWN'
    END AS STATUS,
    STGROUP AS STOGROUP_NAME
FROM SYSIBM.SYSDATABASE
WHERE NAME NOT IN ('DSNDB01', 'DSNDB04', 'DSNDB06', 'DSNDB07')
ORDER BY NAME;

------------------------------------------------------------------------
-- Extract Alias Information
------------------------------------------------------------------------
SELECT 
    'ALIAS' AS OBJECT_TYPE,
    CREATOR AS SCHEMA_NAME,
    NAME AS ALIAS_NAME,
    TBCREATOR AS TARGET_SCHEMA,
    TBNAME AS TARGET_NAME,
    CREATED AS CREATE_DATE
FROM SYSIBM.SYSTABLES
WHERE TYPE = 'A'  -- Aliases
    AND CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY CREATOR, NAME;

------------------------------------------------------------------------
-- Extract Synonym Information
------------------------------------------------------------------------
SELECT 
    'SYNONYM' AS OBJECT_TYPE,
    CREATOR AS SCHEMA_NAME,
    NAME AS SYNONYM_NAME,
    TBCREATOR AS TARGET_SCHEMA,
    TBNAME AS TARGET_NAME,
    CREATED AS CREATE_DATE
FROM SYSIBM.SYSSYNONYMS
WHERE CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY CREATOR, NAME;

------------------------------------------------------------------------
-- Summary Statistics
------------------------------------------------------------------------
SELECT 
    'SUMMARY' AS REPORT_TYPE,
    'TOTAL_TABLES' AS METRIC,
    COUNT(*) AS VALUE
FROM SYSIBM.SYSTABLES
WHERE TYPE = 'T'
    AND CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
UNION ALL
SELECT 
    'SUMMARY',
    'TOTAL_VIEWS',
    COUNT(*)
FROM SYSIBM.SYSTABLES
WHERE TYPE = 'V'
    AND CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
UNION ALL
SELECT 
    'SUMMARY',
    'TOTAL_INDEXES',
    COUNT(*)
FROM SYSIBM.SYSINDEXES
WHERE CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
UNION ALL
SELECT 
    'SUMMARY',
    'TOTAL_PROCEDURES',
    COUNT(*)
FROM SYSIBM.SYSROUTINES
WHERE ROUTINETYPE = 'P'
    AND SCHEMA NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
UNION ALL
SELECT 
    'SUMMARY',
    'TOTAL_FUNCTIONS',
    COUNT(*)
FROM SYSIBM.SYSROUTINES
WHERE ROUTINETYPE = 'F'
    AND SCHEMA NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT');

------------------------------------------------------------------------
-- Notes:
-- 1. Adjust schema filters (CREATOR, SCHEMA) to match your environment
-- 2. Some columns may not exist in older DB2 versions - remove if needed
-- 3. For large catalogs, consider adding WHERE clauses to filter results
-- 4. Export each result set to a separate CSV file for easier processing
------------------------------------------------------------------------
