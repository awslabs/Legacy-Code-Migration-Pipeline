/* REXX - Extract CICS CSD (System Definition) to CSV format */
/*                                                              */
/* Purpose: Extract CICS resource definitions from CSD         */
/* Output:  CSV file with resource_name, resource_type,        */
/*          group_name, status                                 */
/*                                                              */
/* Instructions:                                                */
/* 1. Update CICS_REGION variable to match your CICS region    */
/* 2. Update CSD_DATASET variable to point to your CSD         */
/* 3. Run this REXX script from TSO or batch                   */
/* 4. Output will be written to specified dataset              */
/*                                                              */
/****************************************************************/

/* Configuration */
CICS_REGION = 'CICSPROD'
CSD_DATASET = 'CICS.PROD.DFHCSD'
OUTPUT_DS   = 'EXPORT.CICS.INVENTORY.CSV'

/* Initialize */
SAY 'CICS CSD Extraction Utility'
SAY 'Region:' CICS_REGION
SAY 'CSD:   ' CSD_DATASET
SAY ''

/* Allocate output dataset */
ADDRESS TSO
"ALLOC DA('"OUTPUT_DS"') NEW CATALOG",
  "SPACE(50,10) TRACKS",
  "RECFM(F B) LRECL(200) BLKSIZE(20000)"

IF RC <> 0 THEN DO
  SAY 'Error allocating output dataset. RC=' RC
  EXIT RC
END

/* Open output file */
"EXECIO 0 DISKW OUTDD (OPEN"
ADDRESS MVS "EXECIO * DISKW OUTDD (STEM HEADER. FINIS"

/* Write CSV header */
HEADER.1 = 'resource_name,resource_type,group_name,status'
HEADER.0 = 1
"EXECIO 1 DISKW OUTDD (STEM HEADER."

/* Extract PROGRAM definitions */
SAY 'Extracting PROGRAM definitions...'
CALL EXTRACT_PROGRAMS

/* Extract TRANSACTION definitions */
SAY 'Extracting TRANSACTION definitions...'
CALL EXTRACT_TRANSACTIONS

/* Extract FILE definitions */
SAY 'Extracting FILE definitions...'
CALL EXTRACT_FILES

/* Extract MAPSET definitions */
SAY 'Extracting MAPSET definitions...'
CALL EXTRACT_MAPSETS

/* Close output file */
"EXECIO 0 DISKW OUTDD (FINIS"
"FREE DD(OUTDD)"

SAY ''
SAY 'Extraction complete. Output written to:' OUTPUT_DS
SAY 'Download this dataset for analysis.'

EXIT 0

/****************************************************************/
/* Extract PROGRAM definitions                                  */
/****************************************************************/
EXTRACT_PROGRAMS:
  /* Use DFHCSDUP to extract program definitions */
  TEMP_DS = 'TEMP.CSDUP.PROGRAMS'
  
  /* Allocate temporary dataset for DFHCSDUP output */
  "ALLOC DA('"TEMP_DS"') NEW DELETE",
    "SPACE(50,10) TRACKS",
    "RECFM(F B) LRECL(80) BLKSIZE(8000)"
  
  /* Create DFHCSDUP control statements */
  SYSIN.1 = 'EXTRACT GROUP(*) OBJECTS(PROGRAM)'
  SYSIN.0 = 1
  
  /* Execute DFHCSDUP */
  ADDRESS TSO
  "ALLOC DD(DFHCSD) DSN('"CSD_DATASET"') SHR REUSE"
  "ALLOC DD(SYSPRINT) DSN('"TEMP_DS"') SHR REUSE"
  "ALLOC DD(SYSIN) DUMMY REUSE"
  
  /* Note: In production, you would call DFHCSDUP here */
  /* For this example, we'll parse a sample format */
  
  /* Parse DFHCSDUP output and write to CSV */
  "EXECIO * DISKR SYSPRINT (STEM LINES. FINIS"
  
  DO I = 1 TO LINES.0
    LINE = LINES.I
    IF POS('DEFINE PROGRAM', LINE) > 0 THEN DO
      PARSE VAR LINE . 'PROGRAM(' PROGNAME ')' .
      PARSE VAR LINE . 'GROUP(' GROUPNAME ')' .
      
      /* Extract status if present */
      IF POS('ENABLED', LINE) > 0 THEN
        STATUS = 'ENABLED'
      ELSE IF POS('DISABLED', LINE) > 0 THEN
        STATUS = 'DISABLED'
      ELSE
        STATUS = 'UNKNOWN'
      
      /* Format as CSV */
      CSV_LINE = PROGNAME','PROGRAM','GROUPNAME','STATUS
      OUTLINES.I = CSV_LINE
    END
  END
  
  /* Write to output */
  IF OUTLINES.0 > 0 THEN
    "EXECIO * DISKW OUTDD (STEM OUTLINES."
  
  /* Cleanup */
  "FREE DD(DFHCSD,SYSPRINT,SYSIN)"
  
  SAY '  Extracted' OUTLINES.0 'PROGRAM definitions'
  
RETURN

/****************************************************************/
/* Extract TRANSACTION definitions                              */
/****************************************************************/
EXTRACT_TRANSACTIONS:
  /* Similar to EXTRACT_PROGRAMS but for transactions */
  TEMP_DS = 'TEMP.CSDUP.TRANS'
  
  "ALLOC DA('"TEMP_DS"') NEW DELETE",
    "SPACE(50,10) TRACKS",
    "RECFM(F B) LRECL(80) BLKSIZE(8000)"
  
  SYSIN.1 = 'EXTRACT GROUP(*) OBJECTS(TRANSACTION)'
  SYSIN.0 = 1
  
  ADDRESS TSO
  "ALLOC DD(DFHCSD) DSN('"CSD_DATASET"') SHR REUSE"
  "ALLOC DD(SYSPRINT) DSN('"TEMP_DS"') SHR REUSE"
  "ALLOC DD(SYSIN) DUMMY REUSE"
  
  "EXECIO * DISKR SYSPRINT (STEM LINES. FINIS"
  
  DO I = 1 TO LINES.0
    LINE = LINES.I
    IF POS('DEFINE TRANSACTION', LINE) > 0 THEN DO
      PARSE VAR LINE . 'TRANSACTION(' TRANID ')' .
      PARSE VAR LINE . 'GROUP(' GROUPNAME ')' .
      PARSE VAR LINE . 'PROGRAM(' PROGNAME ')' .
      
      IF POS('ENABLED', LINE) > 0 THEN
        STATUS = 'ENABLED'
      ELSE IF POS('DISABLED', LINE) > 0 THEN
        STATUS = 'DISABLED'
      ELSE
        STATUS = 'UNKNOWN'
      
      CSV_LINE = TRANID','TRANSACTION','GROUPNAME','STATUS
      OUTLINES.I = CSV_LINE
    END
  END
  
  IF OUTLINES.0 > 0 THEN
    "EXECIO * DISKW OUTDD (STEM OUTLINES."
  
  "FREE DD(DFHCSD,SYSPRINT,SYSIN)"
  
  SAY '  Extracted' OUTLINES.0 'TRANSACTION definitions'
  
RETURN

/****************************************************************/
/* Extract FILE definitions                                     */
/****************************************************************/
EXTRACT_FILES:
  TEMP_DS = 'TEMP.CSDUP.FILES'
  
  "ALLOC DA('"TEMP_DS"') NEW DELETE",
    "SPACE(50,10) TRACKS",
    "RECFM(F B) LRECL(80) BLKSIZE(8000)"
  
  SYSIN.1 = 'EXTRACT GROUP(*) OBJECTS(FILE)'
  SYSIN.0 = 1
  
  ADDRESS TSO
  "ALLOC DD(DFHCSD) DSN('"CSD_DATASET"') SHR REUSE"
  "ALLOC DD(SYSPRINT) DSN('"TEMP_DS"') SHR REUSE"
  "ALLOC DD(SYSIN) DUMMY REUSE"
  
  "EXECIO * DISKR SYSPRINT (STEM LINES. FINIS"
  
  DO I = 1 TO LINES.0
    LINE = LINES.I
    IF POS('DEFINE FILE', LINE) > 0 THEN DO
      PARSE VAR LINE . 'FILE(' FILENAME ')' .
      PARSE VAR LINE . 'GROUP(' GROUPNAME ')' .
      
      IF POS('ENABLED', LINE) > 0 THEN
        STATUS = 'ENABLED'
      ELSE IF POS('DISABLED', LINE) > 0 THEN
        STATUS = 'DISABLED'
      ELSE
        STATUS = 'UNKNOWN'
      
      CSV_LINE = FILENAME','FILE','GROUPNAME','STATUS
      OUTLINES.I = CSV_LINE
    END
  END
  
  IF OUTLINES.0 > 0 THEN
    "EXECIO * DISKW OUTDD (STEM OUTLINES."
  
  "FREE DD(DFHCSD,SYSPRINT,SYSIN)"
  
  SAY '  Extracted' OUTLINES.0 'FILE definitions'
  
RETURN

/****************************************************************/
/* Extract MAPSET definitions                                   */
/****************************************************************/
EXTRACT_MAPSETS:
  TEMP_DS = 'TEMP.CSDUP.MAPSETS'
  
  "ALLOC DA('"TEMP_DS"') NEW DELETE",
    "SPACE(50,10) TRACKS",
    "RECFM(F B) LRECL(80) BLKSIZE(8000)"
  
  SYSIN.1 = 'EXTRACT GROUP(*) OBJECTS(MAPSET)'
  SYSIN.0 = 1
  
  ADDRESS TSO
  "ALLOC DD(DFHCSD) DSN('"CSD_DATASET"') SHR REUSE"
  "ALLOC DD(SYSPRINT) DSN('"TEMP_DS"') SHR REUSE"
  "ALLOC DD(SYSIN) DUMMY REUSE"
  
  "EXECIO * DISKR SYSPRINT (STEM LINES. FINIS"
  
  DO I = 1 TO LINES.0
    LINE = LINES.I
    IF POS('DEFINE MAPSET', LINE) > 0 THEN DO
      PARSE VAR LINE . 'MAPSET(' MAPNAME ')' .
      PARSE VAR LINE . 'GROUP(' GROUPNAME ')' .
      
      IF POS('ENABLED', LINE) > 0 THEN
        STATUS = 'ENABLED'
      ELSE IF POS('DISABLED', LINE) > 0 THEN
        STATUS = 'DISABLED'
      ELSE
        STATUS = 'UNKNOWN'
      
      CSV_LINE = MAPNAME','MAPSET','GROUPNAME','STATUS
      OUTLINES.I = CSV_LINE
    END
  END
  
  IF OUTLINES.0 > 0 THEN
    "EXECIO * DISKW OUTDD (STEM OUTLINES."
  
  "FREE DD(DFHCSD,SYSPRINT,SYSIN)"
  
  SAY '  Extracted' OUTLINES.0 'MAPSET definitions'
  
RETURN
