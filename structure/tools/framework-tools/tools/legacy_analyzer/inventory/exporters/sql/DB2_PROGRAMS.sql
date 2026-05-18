-- DB2 Program and Package Information Export Script
-- Purpose: Extract DB2 program bindings and package information
-- Output:  CSV format data about DB2 programs and their usage
--
-- Instructions:
-- 1. Connect to DB2 subsystem
-- 2. Run this script using SPUFI, QMF, or batch DB2
-- 3. Export results to CSV format
-- 4. Download for analysis
--
------------------------------------------------------------------------

-- Set output format (if using QMF)
-- SET PROFILE (FORM=CSV);

------------------------------------------------------------------------
-- Extract Plan Information
------------------------------------------------------------------------
SELECT 
    'PLAN' AS OBJECT_TYPE,
    NAME AS PLAN_NAME,
    CREATOR AS CREATOR,
    BINDDATE AS BIND_DATE,
    BINDTIME AS BIND_TIME,
    VALIDATE AS VALIDATION_TYPE,
    ISOLATION AS ISOLATION_LEVEL,
    RELEASE AS RELEASE_TYPE,
    ACQUIRE AS ACQUIRE_TYPE,
    EXPLAIN AS EXPLAIN_OPTION,
    OPTHINT AS OPTIMIZATION_HINT,
    DEGREE AS PARALLELISM_DEGREE,
    CASE OPERATIVE
        WHEN 'Y' THEN 'OPERATIVE'
        WHEN 'N' THEN 'INOPERATIVE'
        ELSE 'UNKNOWN'
    END AS STATUS,
    CASE VALID
        WHEN 'Y' THEN 'VALID'
        WHEN 'N' THEN 'INVALID'
        ELSE 'UNKNOWN'
    END AS VALIDITY,
    AVGSIZE AS AVG_SIZE
FROM SYSIBM.SYSPLAN
ORDER BY NAME;

------------------------------------------------------------------------
-- Extract Package Information
------------------------------------------------------------------------
SELECT 
    'PACKAGE' AS OBJECT_TYPE,
    COLLID AS COLLECTION_ID,
    NAME AS PACKAGE_NAME,
    VERSION AS VERSION,
    CREATOR AS CREATOR,
    BINDDATE AS BIND_DATE,
    BINDTIME AS BIND_TIME,
    VALIDATE AS VALIDATION_TYPE,
    ISOLATION AS ISOLATION_LEVEL,
    RELEASE AS RELEASE_TYPE,
    ACQUIRE AS ACQUIRE_TYPE,
    EXPLAIN AS EXPLAIN_OPTION,
    DEGREE AS PARALLELISM_DEGREE,
    CASE OPERATIVE
        WHEN 'Y' THEN 'OPERATIVE'
        WHEN 'N' THEN 'INOPERATIVE'
        ELSE 'UNKNOWN'
    END AS STATUS,
    CASE VALID
        WHEN 'Y' THEN 'VALID'
        WHEN 'N' THEN 'INVALID'
        ELSE 'UNKNOWN'
    END AS VALIDITY,
    AVGSIZE AS AVG_SIZE
FROM SYSIBM.SYSPACKAGE
ORDER BY COLLID, NAME, VERSION;

------------------------------------------------------------------------
-- Extract Plan-Package Dependencies
------------------------------------------------------------------------
SELECT 
    'PLAN_DEPENDENCY' AS DEPENDENCY_TYPE,
    PLANNAME AS PLAN_NAME,
    COLLID AS COLLECTION_ID,
    NAME AS PACKAGE_NAME,
    VERSION AS VERSION
FROM SYSIBM.SYSPACKDEP
ORDER BY PLANNAME, COLLID, NAME;

------------------------------------------------------------------------
-- Extract DBRM (Database Request Module) Information
------------------------------------------------------------------------
SELECT 
    'DBRM' AS OBJECT_TYPE,
    NAME AS DBRM_NAME,
    TIMESTAMP AS DBRM_TIMESTAMP,
    PDSNAME AS SOURCE_LIBRARY,
    PLNAME AS PLAN_NAME,
    PRECOMPTIME AS PRECOMPILE_TIME,
    PRECOMPDATE AS PRECOMPILE_DATE,
    QUOTE AS QUOTE_OPTION,
    COMMA AS COMMA_OPTION,
    DEC AS DECIMAL_OPTION,
    APOSTSQL AS APOSTROPHE_SQL,
    FLOATTYPE AS FLOAT_TYPE
FROM SYSIBM.SYSDBRM
ORDER BY NAME;

------------------------------------------------------------------------
-- Extract Statement Information (SQL in programs)
------------------------------------------------------------------------
SELECT 
    'STATEMENT' AS OBJECT_TYPE,
    NAME AS PACKAGE_NAME,
    COLLID AS COLLECTION_ID,
    STMTNO AS STATEMENT_NUMBER,
    SECTNO AS SECTION_NUMBER,
    SEQNO AS SEQUENCE_NUMBER,
    CASE STMTTYPE
        WHEN 'SE' THEN 'SELECT'
        WHEN 'IN' THEN 'INSERT'
        WHEN 'UP' THEN 'UPDATE'
        WHEN 'DE' THEN 'DELETE'
        WHEN 'CA' THEN 'CALL'
        ELSE STMTTYPE
    END AS STATEMENT_TYPE,
    CASE QUERYNO
        WHEN 0 THEN 'NOT_EXPLAINED'
        ELSE 'EXPLAINED'
    END AS EXPLAIN_STATUS
FROM SYSIBM.SYSSTMT
WHERE COLLID NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC')
ORDER BY COLLID, NAME, STMTNO;

------------------------------------------------------------------------
-- Extract Table Dependencies (what tables each program uses)
------------------------------------------------------------------------
SELECT 
    'TABLE_DEPENDENCY' AS DEPENDENCY_TYPE,
    DNAME AS DBRM_NAME,
    BNAME AS TABLE_NAME,
    BTYPE AS OBJECT_TYPE,
    BQUALIFIER AS SCHEMA_NAME,
    CASE BTYPE
        WHEN 'T' THEN 'TABLE'
        WHEN 'V' THEN 'VIEW'
        WHEN 'A' THEN 'ALIAS'
        WHEN 'S' THEN 'SYNONYM'
        ELSE 'UNKNOWN'
    END AS OBJECT_TYPE_DESC
FROM SYSIBM.SYSPLANDEP
ORDER BY DNAME, BNAME;

------------------------------------------------------------------------
-- Extract Program Authorization Information
------------------------------------------------------------------------
SELECT 
    'AUTHORIZATION' AS OBJECT_TYPE,
    GRANTEE AS USER_ID,
    GRANTOR AS GRANTED_BY,
    NAME AS PLAN_NAME,
    AUTHHOWGOT AS AUTH_METHOD,
    BINDAUTH AS BIND_PRIVILEGE,
    EXECUTEAUTH AS EXECUTE_PRIVILEGE,
    TIMESTAMP AS GRANT_DATE
FROM SYSIBM.SYSPLANAUTH
ORDER BY NAME, GRANTEE;

------------------------------------------------------------------------
-- Extract Package Authorization Information
------------------------------------------------------------------------
SELECT 
    'PACKAGE_AUTH' AS OBJECT_TYPE,
    GRANTEE AS USER_ID,
    GRANTOR AS GRANTED_BY,
    COLLID AS COLLECTION_ID,
    NAME AS PACKAGE_NAME,
    AUTHHOWGOT AS AUTH_METHOD,
    BINDAUTH AS BIND_PRIVILEGE,
    COPYAUTH AS COPY_PRIVILEGE,
    EXECUTEAUTH AS EXECUTE_PRIVILEGE,
    TIMESTAMP AS GRANT_DATE
FROM SYSIBM.SYSPACKAUTH
ORDER BY COLLID, NAME, GRANTEE;

------------------------------------------------------------------------
-- Extract Program Usage Statistics (if available)
------------------------------------------------------------------------
-- Note: This requires DB2 accounting/statistics to be enabled
SELECT 
    'USAGE_STATS' AS OBJECT_TYPE,
    PLANNAME AS PLAN_NAME,
    PROGNAME AS PROGRAM_NAME,
    COUNT(*) AS EXECUTION_COUNT,
    AVG(ELAPSED_TIME) AS AVG_ELAPSED_TIME,
    AVG(CPU_TIME) AS AVG_CPU_TIME,
    SUM(GETPAGES) AS TOTAL_GETPAGES,
    MAX(CONNTIME) AS LAST_EXECUTION
FROM SYSIBM.SYSPACKAGE_USAGE
WHERE CONNTIME >= CURRENT DATE - 365 DAYS
GROUP BY PLANNAME, PROGNAME
ORDER BY EXECUTION_COUNT DESC;

------------------------------------------------------------------------
-- Extract Invalid Objects (programs that need rebinding)
------------------------------------------------------------------------
SELECT 
    'INVALID_PLAN' AS OBJECT_TYPE,
    NAME AS PLAN_NAME,
    CREATOR AS CREATOR,
    BINDDATE AS BIND_DATE,
    CASE OPERATIVE
        WHEN 'N' THEN 'INOPERATIVE'
        ELSE 'OTHER'
    END AS REASON,
    CASE VALID
        WHEN 'N' THEN 'INVALID'
        ELSE 'OTHER'
    END AS VALIDITY_REASON
FROM SYSIBM.SYSPLAN
WHERE OPERATIVE = 'N' OR VALID = 'N'
ORDER BY NAME;

SELECT 
    'INVALID_PACKAGE' AS OBJECT_TYPE,
    COLLID AS COLLECTION_ID,
    NAME AS PACKAGE_NAME,
    VERSION AS VERSION,
    CREATOR AS CREATOR,
    BINDDATE AS BIND_DATE,
    CASE OPERATIVE
        WHEN 'N' THEN 'INOPERATIVE'
        ELSE 'OTHER'
    END AS REASON,
    CASE VALID
        WHEN 'N' THEN 'INVALID'
        ELSE 'OTHER'
    END AS VALIDITY_REASON
FROM SYSIBM.SYSPACKAGE
WHERE OPERATIVE = 'N' OR VALID = 'N'
ORDER BY COLLID, NAME, VERSION;

------------------------------------------------------------------------
-- Extract Program-to-Program Dependencies (via stored procedures)
------------------------------------------------------------------------
SELECT 
    'PROGRAM_DEPENDENCY' AS DEPENDENCY_TYPE,
    SCHEMA AS CALLER_SCHEMA,
    ROUTINENAME AS CALLER_ROUTINE,
    BSCHEMA AS CALLED_SCHEMA,
    BNAME AS CALLED_ROUTINE,
    BTYPE AS CALLED_TYPE
FROM SYSIBM.SYSROUTINEDEP
WHERE SCHEMA NOT IN ('SYSIBM', 'SYSCAT', 'SYSPROC', 'SYSSTAT')
ORDER BY SCHEMA, ROUTINENAME, BNAME;

------------------------------------------------------------------------
-- Summary Statistics
------------------------------------------------------------------------
SELECT 
    'SUMMARY' AS REPORT_TYPE,
    'TOTAL_PLANS' AS METRIC,
    COUNT(*) AS VALUE
FROM SYSIBM.SYSPLAN
UNION ALL
SELECT 
    'SUMMARY',
    'TOTAL_PACKAGES',
    COUNT(*)
FROM SYSIBM.SYSPACKAGE
UNION ALL
SELECT 
    'SUMMARY',
    'TOTAL_DBRMS',
    COUNT(*)
FROM SYSIBM.SYSDBRM
UNION ALL
SELECT 
    'SUMMARY',
    'INVALID_PLANS',
    COUNT(*)
FROM SYSIBM.SYSPLAN
WHERE OPERATIVE = 'N' OR VALID = 'N'
UNION ALL
SELECT 
    'SUMMARY',
    'INVALID_PACKAGES',
    COUNT(*)
FROM SYSIBM.SYSPACKAGE
WHERE OPERATIVE = 'N' OR VALID = 'N';

------------------------------------------------------------------------
-- Notes:
-- 1. Some queries may need adjustment based on DB2 version
-- 2. SYSPACKAGE_USAGE table may not exist in all environments
-- 3. For large catalogs, add WHERE clauses to filter results
-- 4. Consider running queries separately for better performance
-- 5. Export each result set to a separate CSV file
------------------------------------------------------------------------
