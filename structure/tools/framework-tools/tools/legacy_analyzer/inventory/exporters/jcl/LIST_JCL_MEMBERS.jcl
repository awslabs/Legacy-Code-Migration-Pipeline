//LISTJCL  JOB (ACCT),'LIST JCL MEMBERS',CLASS=A,MSGCLASS=X,
//             NOTIFY=&SYSUID
//*
//* Purpose: List all JCL members from specified libraries
//* Output:  CSV format with member_name, library_name, last_modified
//*
//* Instructions:
//* 1. Update the library names in STEP2 SYSIN to match your environment
//* 2. Update the output dataset name in STEP3 if needed
//* 3. Submit this JCL
//* 4. Download the output dataset for analysis
//*
//*********************************************************************
//*
//* STEP1: List members from first JCL library
//*
//STEP1    EXEC PGM=IKJEFT01
//SYSTSPRT DD DSN=&&TEMP1,DISP=(NEW,PASS),
//            SPACE=(TRK,(50,10)),
//            DCB=(RECFM=FB,LRECL=133,BLKSIZE=13300)
//SYSTSIN  DD *
  LISTDS 'PROD.JCL.LIB' MEMBERS
/*
//*
//* STEP2: List members from additional JCL libraries
//*
//STEP2    EXEC PGM=IKJEFT01
//SYSTSPRT DD DSN=&&TEMP2,DISP=(NEW,PASS),
//            SPACE=(TRK,(50,10)),
//            DCB=(RECFM=FB,LRECL=133,BLKSIZE=13300)
//SYSTSIN  DD *
  LISTDS 'PROD.JCL.BACKUP' MEMBERS
  LISTDS 'TEST.JCL.LIB' MEMBERS
  LISTDS 'DEV.JCL.LIB' MEMBERS
/*
//*
//* STEP3: Format output as CSV
//*
//STEP3    EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=&&TEMP1,DISP=(OLD,DELETE)
//         DD DSN=&&TEMP2,DISP=(OLD,DELETE)
//SORTOUT  DD DSN=EXPORT.JCL.INVENTORY.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(10,5),RLSE),
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=8000)
//SYSIN    DD *
  SORT FIELDS=COPY
  INCLUDE COND=(1,8,CH,NE,C'        ')
/*
//*
//* STEP4: Add CSV header and format data
//*
//STEP4    EXEC PGM=ICETOOL
//TOOLMSG  DD SYSOUT=*
//DFSMSG   DD SYSOUT=*
//IN       DD DSN=EXPORT.JCL.INVENTORY.CSV,DISP=SHR
//OUT      DD DSN=EXPORT.JCL.INVENTORY.FINAL,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(10,5),RLSE),
//            DCB=(RECFM=FB,LRECL=120,BLKSIZE=12000)
//TOOLIN   DD *
  COPY FROM(IN) TO(OUT) USING(CTL1)
/*
//CTL1CNTL DD *
  OPTION COPY
  INREC IFTHEN=(WHEN=INIT,
    BUILD=(1,8,C',',9,44,C',',53,10))
  OUTREC IFTHEN=(WHEN=GROUP,BEGIN=(1,1,CH,EQ,C'M'),
    PUSH=(121:C'member_name,library_name,last_modified'))
/*
//*
//* Note: The output dataset EXPORT.JCL.INVENTORY.FINAL contains
//*       CSV formatted data ready for download and analysis
//*
