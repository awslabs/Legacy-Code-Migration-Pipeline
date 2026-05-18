# Mainframe Inventory Export Scripts

This directory contains scripts and documentation for extracting mainframe inventory data for artifact lifecycle analysis.

## Overview

The artifact lifecycle analysis system requires inventory data from your mainframe environment. This data includes:

- **JCL Members**: All JCL jobs in your libraries
- **Load Modules**: All compiled programs in LOADLIB datasets
- **Datasets**: Catalog information for all datasets
- **CICS Resources**: CICS transaction and program definitions
- **DB2 Objects**: DB2 tables, programs, and packages

## Directory Structure

```
legacy_analyzer/mainframe_exports/
├── README.md                    # This file
├── jcl/                        # JCL scripts for data extraction
│   ├── LIST_JCL_MEMBERS.jcl   # Extract JCL member listings
│   ├── LIST_LOAD_MODULES.jcl  # Extract load module information
│   ├── LIST_DATASETS.jcl      # Extract dataset catalog
│   └── EXPORT_TO_CSV.jcl      # Generic CSV formatting utility
├── rexx/                       # REXX scripts for CICS extraction
│   ├── EXTRACT_CICS_CSD.rexx  # Extract CICS definitions
│   └── FORMAT_CSV.rexx        # Generic CSV formatting utility
├── sql/                        # SQL scripts for DB2 extraction
│   ├── DB2_CATALOG.sql        # Extract DB2 catalog
│   └── DB2_PROGRAMS.sql       # Extract DB2 program info
├── samples/                    # Sample output files
│   ├── jcl_inventory.csv
│   ├── program_inventory.csv
│   ├── dataset_inventory.csv
│   ├── cics_inventory.csv
│   └── db2_inventory.csv
└── docs/                       # Detailed documentation
    ├── JCL_EXPORT_GUIDE.md
    ├── DATASET_EXPORT_GUIDE.md
    └── CICS_EXPORT_GUIDE.md
```

**Note**: This directory is part of the `legacy_analyzer` module, as these scripts are used during the inventory loading phase of artifact lifecycle analysis.

## Quick Start

### 1. Extract JCL Inventory

```jcl
// Submit: LIST_JCL_MEMBERS.jcl
// Output: EXPORT.JCL.INVENTORY.FINAL
```

### 2. Extract Program Inventory

```jcl
// Submit: LIST_LOAD_MODULES.jcl
// Output: EXPORT.PROGRAM.INVENTORY.CSV
```

### 3. Extract Dataset Inventory

```jcl
// Submit: LIST_DATASETS.jcl
// Output: EXPORT.DATASET.INVENTORY.CSV
```

### 4. Extract CICS Inventory

```rexx
TSO %EXTRACT_CICS_CSD
Output: EXPORT.CICS.INVENTORY.CSV
```

### 5. Extract DB2 Inventory

```sql
-- Run in SPUFI or QMF: DB2_CATALOG.sql
-- Output: Multiple result sets (export each to CSV)
```

## Expected Output Formats

### JCL Inventory CSV Format

```csv
member_name,library_name,last_modified,size_lines
PAYROLL1,PROD.JCL.LIB,2024-01-15,250
BILLING2,PROD.JCL.LIB,2024-02-20,180
```

### Program Inventory CSV Format

```csv
program_name,library_name,link_date,size_bytes,entry_point
PAYROLL,PROD.LOADLIB,2024-01-10,524288,PAYROLL
BILLING,PROD.LOADLIB,2024-02-15,262144,BILLING
```

### Dataset Inventory CSV Format

```csv
dataset_name,creation_date,last_referenced,size_mb,volume,dataset_type
PROD.PAYROLL.MASTER,2023-01-01,2024-03-15,1024.5,VOL001,PS
PROD.BILLING.TRANS,2023-06-01,2024-03-14,512.25,VOL002,VSAM
```

### CICS Inventory CSV Format

```csv
resource_name,resource_type,group_name,status
PAY001,TRANSACTION,PAYGRP,ENABLED
PAYPROG,PROGRAM,PAYGRP,ENABLED
PAYFILE,FILE,PAYGRP,ENABLED
```

### DB2 Inventory CSV Format

```csv
object_type,schema_name,object_name,create_date,status
TABLE,PROD,EMPLOYEE,2023-01-15,AVAILABLE
VIEW,PROD,EMP_SUMMARY,2023-02-20,AVAILABLE
PROCEDURE,PROD,UPDATE_SALARY,2023-03-10,AVAILABLE
```

## Download Instructions

### Using FTP

1. Connect to mainframe:
   ```
   ftp mainframe.company.com
   ```

2. Set transfer mode to ASCII:
   ```
   ascii
   quote site sbdataconn=(IBM-1047,ISO8859-1)
   ```

3. Download files:
   ```
   get 'EXPORT.JCL.INVENTORY.FINAL' jcl_inventory.csv
   get 'EXPORT.PROGRAM.INVENTORY.CSV' program_inventory.csv
   get 'EXPORT.DATASET.INVENTORY.CSV' dataset_inventory.csv
   ```

### Using SFTP

```bash
sftp user@mainframe.company.com
get EXPORT.JCL.INVENTORY.FINAL jcl_inventory.csv
get EXPORT.PROGRAM.INVENTORY.CSV program_inventory.csv
get EXPORT.DATASET.INVENTORY.CSV dataset_inventory.csv
```

### Using File Transfer Tools

- **IBM Personal Communications**: Use file transfer feature
- **Zowe CLI**: Use `zowe files download` command
- **Connect:Direct**: Configure transfer jobs

## Loading Data into Analysis System

Once you have downloaded the CSV files, load them into the analysis database:

```bash
# Load JCL inventory
python -m legacy_analyzer load --type jcl \
  --file jcl_inventory.csv \

# Load program inventory
python -m legacy_analyzer load --type programs \
  --file program_inventory.csv \

# Load dataset inventory
python -m legacy_analyzer load --type datasets \
  --file dataset_inventory.csv \

# Load CICS inventory
python -m legacy_analyzer load --type cics \
  --file cics_inventory.csv \
```

## Customization

### Updating Library Names

Edit the JCL scripts to include your specific library names:

```jcl
//SYSTSIN  DD *
  LISTDS 'YOUR.JCL.LIB' MEMBERS
  LISTDS 'YOUR.OTHER.JCL.LIB' MEMBERS
/*
```

### Filtering by High-Level Qualifier

Edit the IDCAMS LISTCAT commands:

```jcl
//SYSIN    DD *
  LISTCAT ENTRIES('YOUR.HLQ.**') -
    NONVSAM -
    ALL
/*
```

### Adjusting DB2 Filters

Edit the SQL WHERE clauses:

```sql
WHERE CREATOR NOT IN ('SYSIBM', 'SYSCAT', 'YOUR_SYSTEM_SCHEMA')
  AND CREATOR LIKE 'PROD%'
```

## Troubleshooting

### JCL Submission Errors

- **Error**: Dataset not found
  - **Solution**: Update dataset names to match your environment

- **Error**: Insufficient space
  - **Solution**: Increase SPACE parameter in JCL

### REXX Execution Errors

- **Error**: DFHCSDUP not found
  - **Solution**: Ensure CICS libraries are in STEPLIB

- **Error**: Permission denied
  - **Solution**: Verify you have READ access to CSD

### DB2 Query Errors

- **Error**: Table not found
  - **Solution**: Some catalog tables vary by DB2 version

- **Error**: Insufficient authority
  - **Solution**: Request SELECT on SYSIBM.* tables

## Best Practices

1. **Schedule Regular Exports**: Run exports monthly or quarterly
2. **Version Control**: Keep dated copies of inventory files
3. **Validate Data**: Check row counts and spot-check entries
4. **Document Changes**: Note any customizations to scripts
5. **Test First**: Run on test environment before production

## Support

For issues or questions:

1. Check the detailed guides in the `docs/` directory
2. Review sample output files in `samples/` directory
3. Consult your mainframe systems programmer

## Next Steps

After extracting and loading inventory data:

2. Run artifact analysis queries
3. Generate unreferenced artifact reports
4. Perform risk assessment
5. Create cleanup recommendations

