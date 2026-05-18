//LISTPGM  JOB (ACCT),'LIST LOAD MODULES',CLASS=A,MSGCLASS=X,
//             NOTIFY=&SYSUID
//*
//* Purpose: List all load modules from specified LOADLIB datasets
//* Output:  CSV format with program_name, library_name, link_date,
//*          size_bytes, entry_point
//*
//* Instructions:
//* 1. Update the library names in STEP1-STEP3 to match your environment
//* 2. Update the output dataset name if needed
//* 3. Submit this JCL
//* 4. Download the output dataset for analysis
//*
//*********************************************************************
//*
//* STEP1: List load modules from production libraries
//*
//STEP1    EXEC PGM=IEBLIST
//SYSPRINT DD DSN=&&TEMP1,DISP=(NEW,PASS),
//            SPACE=(TRK,(100,20)),
//            DCB=(RECFM=FBA,LRECL=121,BLKSIZE=12100)
//DD1      DD DSN=PROD.LOADLIB,DISP=SHR
//DD2      DD DSN=PROD.CICS.LOADLIB,DISP=SHR
//SYSIN    DD *
  LISTPDS DSNAME=PROD.LOADLIB,FORMAT
  LISTPDS DSNAME=PROD.CICS.LOADLIB,FORMAT
/*
//*
//* STEP2: List load modules from test libraries
//*
//STEP2    EXEC PGM=IEBLIST
//SYSPRINT DD DSN=&&TEMP2,DISP=(NEW,PASS),
//            SPACE=(TRK,(50,10)),
//            DCB=(RECFM=FBA,LRECL=121,BLKSIZE=12100)
//DD1      DD DSN=TEST.LOADLIB,DISP=SHR
//SYSIN    DD *
  LISTPDS DSNAME=TEST.LOADLIB,FORMAT
/*
//*
//* STEP3: Extract and format load module information
//*
//STEP3    EXEC PGM=IKJEFT01
//SYSTSPRT DD DSN=&&TEMP3,DISP=(NEW,PASS),
//            SPACE=(TRK,(100,20)),
//            DCB=(RECFM=FB,LRECL=200,BLKSIZE=20000)
//SYSTSIN  DD *
  LISTDS 'PROD.LOADLIB' MEMBERS
  LISTDS 'PROD.CICS.LOADLIB' MEMBERS
  LISTDS 'TEST.LOADLIB' MEMBERS
/*
//*
//* STEP4: Parse IEBLIST output and create CSV
//*
//STEP4    EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=&&TEMP1,DISP=(OLD,DELETE)
//         DD DSN=&&TEMP2,DISP=(OLD,DELETE)
//SORTOUT  DD DSN=&&PARSED,DISP=(NEW,PASS),
//            SPACE=(TRK,(50,10)),
//            DCB=(RECFM=FB,LRECL=150,BLKSIZE=15000)
//SYSIN    DD *
  SORT FIELDS=(1,8,CH,A)
  INCLUDE COND=(10,4,CH,EQ,C'NAME')
/*
//*
//* STEP5: Format as CSV with header
//*
//STEP5    EXEC PGM=ICETOOL
//TOOLMSG  DD SYSOUT=*
//DFSMSG   DD SYSOUT=*
//IN       DD DSN=&&PARSED,DISP=(OLD,DELETE)
//OUT      DD DSN=EXPORT.PROGRAM.INVENTORY.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(20,5),RLSE),
//            DCB=(RECFM=FB,LRECL=150,BLKSIZE=15000)
//TOOLIN   DD *
  COPY FROM(IN) TO(OUT) USING(CTL1)
/*
//CTL1CNTL DD *
  OPTION COPY
  HEADER1=(1:C'program_name,library_name,link_date,',
           C'size_bytes,entry_point')
  INREC BUILD=(1,8,C',',15,44,C',',60,10,C',',71,10,C',',82,8)
/*
//*
//* STEP6: Alternative - Use AMBLIST for detailed module info
//*
//STEP6    EXEC PGM=AMBLIST
//SYSPRINT DD DSN=&&AMBOUT,DISP=(NEW,PASS),
//            SPACE=(TRK,(50,10)),
//            DCB=(RECFM=FBA,LRECL=121,BLKSIZE=12100)
//SYSLIB   DD DSN=PROD.LOADLIB,DISP=SHR
//SYSIN    DD *
  LISTLOAD MEMBER=*,OUTPUT=XREF
/*
//*
//* Note: The output dataset EXPORT.PROGRAM.INVENTORY.CSV contains
//*       CSV formatted data ready for download and analysis
//*
//* Alternative: For more detailed information including CSECT info,
//*              use the AMBLIST output from STEP6
//*
