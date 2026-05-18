/* REXX - Format mainframe data as CSV                         */
/*                                                              */
/* Purpose: Generic utility to convert fixed-width mainframe   */
/*          data to CSV format                                 */
/*                                                              */
/* Usage:   TSO %FORMAT_CSV input_ds output_ds field_spec      */
/*                                                              */
/* Example: TSO %FORMAT_CSV 'MY.DATA' 'MY.CSV' '1-8,9-44,53-62'*/
/*                                                              */
/* Instructions:                                                */
/* 1. Specify input dataset (fixed-width format)               */
/* 2. Specify output dataset (CSV format)                      */
/* 3. Specify field positions (start-end pairs)                */
/*                                                              */
/****************************************************************/

PARSE ARG INPUT_DS OUTPUT_DS FIELD_SPEC

/* Validate arguments */
IF INPUT_DS = '' | OUTPUT_DS = '' | FIELD_SPEC = '' THEN DO
  SAY 'Usage: %FORMAT_CSV input_ds output_ds field_spec'
  SAY ''
  SAY 'Example: %FORMAT_CSV ''MY.DATA'' ''MY.CSV'' ''1-8,9-44,53-62'''
  SAY ''
  SAY 'Field spec format: start-end,start-end,...'
  SAY '  1-8      = positions 1 through 8'
  SAY '  9-44     = positions 9 through 44'
  SAY '  53-62    = positions 53 through 62'
  EXIT 8
END

/* Remove quotes if present */
INPUT_DS = STRIP(INPUT_DS, 'B', "'")
OUTPUT_DS = STRIP(OUTPUT_DS, 'B', "'")

SAY 'CSV Formatting Utility'
SAY 'Input:  ' INPUT_DS
SAY 'Output: ' OUTPUT_DS
SAY 'Fields: ' FIELD_SPEC
SAY ''

/* Parse field specifications */
FIELD_COUNT = 0
DO WHILE FIELD_SPEC <> ''
  PARSE VAR FIELD_SPEC FIELD ',' FIELD_SPEC
  FIELD_COUNT = FIELD_COUNT + 1
  PARSE VAR FIELD START '-' END
  FIELD_START.FIELD_COUNT = START
  FIELD_END.FIELD_COUNT = END
  FIELD_LEN.FIELD_COUNT = END - START + 1
END

SAY 'Parsed' FIELD_COUNT 'field specifications'

/* Allocate input dataset */
ADDRESS TSO
"ALLOC DD(INDD) DSN('"INPUT_DS"') SHR REUSE"
IF RC <> 0 THEN DO
  SAY 'Error allocating input dataset. RC=' RC
  EXIT RC
END

/* Allocate output dataset */
"ALLOC DA('"OUTPUT_DS"') NEW CATALOG",
  "SPACE(50,10) TRACKS",
  "RECFM(F B) LRECL(500) BLKSIZE(27500)"
IF RC <> 0 THEN DO
  SAY 'Error allocating output dataset. RC=' RC
  EXIT RC
END

/* Read input file */
"EXECIO * DISKR INDD (STEM INLINES. FINIS"
IF RC <> 0 THEN DO
  SAY 'Error reading input dataset. RC=' RC
  EXIT RC
END

SAY 'Read' INLINES.0 'records from input'

/* Process each line */
OUTLINES.0 = 0
DO I = 1 TO INLINES.0
  INLINE = INLINES.I
  OUTLINE = ''
  
  /* Extract each field and build CSV line */
  DO F = 1 TO FIELD_COUNT
    START_POS = FIELD_START.F
    FIELD_LENGTH = FIELD_LEN.F
    
    /* Extract field value */
    FIELD_VALUE = SUBSTR(INLINE, START_POS, FIELD_LENGTH)
    
    /* Trim trailing spaces */
    FIELD_VALUE = STRIP(FIELD_VALUE, 'T')
    
    /* Handle embedded commas and quotes */
    IF POS(',', FIELD_VALUE) > 0 | POS('"', FIELD_VALUE) > 0 THEN DO
      /* Escape quotes by doubling them */
      FIELD_VALUE = TRANSLATE(FIELD_VALUE, '""', '"')
      /* Enclose in quotes */
      FIELD_VALUE = '"' || FIELD_VALUE || '"'
    END
    
    /* Add to output line */
    IF F = 1 THEN
      OUTLINE = FIELD_VALUE
    ELSE
      OUTLINE = OUTLINE || ',' || FIELD_VALUE
  END
  
  /* Store output line */
  J = OUTLINES.0 + 1
  OUTLINES.J = OUTLINE
  OUTLINES.0 = J
END

SAY 'Formatted' OUTLINES.0 'records'

/* Write output file */
"EXECIO * DISKW OUTDD (STEM OUTLINES. FINIS"
IF RC <> 0 THEN DO
  SAY 'Error writing output dataset. RC=' RC
  EXIT RC
END

/* Cleanup */
"FREE DD(INDD,OUTDD)"

SAY ''
SAY 'CSV formatting complete!'
SAY 'Output written to:' OUTPUT_DS
SAY ''
SAY 'To download:'
SAY '  1. FTP to mainframe'
SAY '  2. Use ASCII mode'
SAY '  3. GET' OUTPUT_DS 'local_file.csv'

EXIT 0

/****************************************************************/
/* Helper function: Add CSV header                             */
/****************************************************************/
ADD_HEADER:
  PARSE ARG HEADER_LINE
  
  /* Prepend header to output */
  TEMP.0 = OUTLINES.0 + 1
  TEMP.1 = HEADER_LINE
  
  DO I = 1 TO OUTLINES.0
    J = I + 1
    TEMP.J = OUTLINES.I
  END
  
  /* Copy back */
  DO I = 1 TO TEMP.0
    OUTLINES.I = TEMP.I
  END
  OUTLINES.0 = TEMP.0
  
RETURN

/****************************************************************/
/* Helper function: Escape CSV special characters              */
/****************************************************************/
ESCAPE_CSV:
  PARSE ARG VALUE
  
  /* Check if value contains comma, quote, or newline */
  IF POS(',', VALUE) > 0 | POS('"', VALUE) > 0 | POS('0A'X, VALUE) > 0 THEN DO
    /* Double any quotes */
    NEW_VALUE = ''
    DO I = 1 TO LENGTH(VALUE)
      CHAR = SUBSTR(VALUE, I, 1)
      IF CHAR = '"' THEN
        NEW_VALUE = NEW_VALUE || '""'
      ELSE
        NEW_VALUE = NEW_VALUE || CHAR
    END
    /* Enclose in quotes */
    VALUE = '"' || NEW_VALUE || '"'
  END
  
RETURN VALUE

/****************************************************************/
/* Helper function: Trim whitespace                            */
/****************************************************************/
TRIM:
  PARSE ARG VALUE
  VALUE = STRIP(VALUE, 'B')
RETURN VALUE
