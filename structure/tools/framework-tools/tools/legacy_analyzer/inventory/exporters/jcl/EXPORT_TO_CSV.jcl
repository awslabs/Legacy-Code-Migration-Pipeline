//EXPCSV   JOB (ACCT),'EXPORT TO CSV',CLASS=A,MSGCLASS=X,
//             NOTIFY=&SYSUID
//*
//* Purpose: Generic utility to format mainframe data as CSV
//* Output:  CSV formatted dataset ready for download
//*
//* Instructions:
//* 1. Update INFILE DD to point to your source dataset
//* 2. Update field positions in SYSIN to match your data
//* 3. Update OUTFILE DD for output dataset name
//* 4. Submit this JCL
//*
//*********************************************************************
//*
//* STEP1: Convert fixed-width data to CSV format
//*
//STEP1    EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=YOUR.INPUT.DATASET,DISP=SHR
//SORTOUT  DD DSN=YOUR.OUTPUT.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(50,10),RLSE),
//            DCB=(RECFM=FB,LRECL=500,BLKSIZE=27500)
//SYSIN    DD *
  OPTION COPY
  INREC IFTHEN=(WHEN=INIT,
    BUILD=(1,8,C',',          Field 1: positions 1-8
           9,44,C',',         Field 2: positions 9-52
           53,10,C',',        Field 3: positions 53-62
           63,10,C',',        Field 4: positions 63-72
           73,8))             Field 5: positions 73-80
/*
//*
//* STEP2: Add CSV header row
//*
//STEP2    EXEC PGM=IEBGENER
//SYSUT1   DD *
field1,field2,field3,field4,field5
/*
//SYSUT2   DD DSN=&&HEADER,DISP=(NEW,PASS),
//            SPACE=(TRK,(1,1)),
//            DCB=(RECFM=FB,LRECL=500,BLKSIZE=27500)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//*
//* STEP3: Concatenate header and data
//*
//STEP3    EXEC PGM=IEBGENER
//SYSUT1   DD DSN=&&HEADER,DISP=(OLD,DELETE)
//         DD DSN=YOUR.OUTPUT.CSV,DISP=SHR
//SYSUT2   DD DSN=YOUR.OUTPUT.FINAL.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(50,10),RLSE),
//            DCB=(RECFM=FB,LRECL=500,BLKSIZE=27500)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//*
//* STEP4: Remove trailing spaces and clean data
//*
//STEP4    EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=YOUR.OUTPUT.FINAL.CSV,DISP=SHR
//SORTOUT  DD DSN=YOUR.OUTPUT.CLEAN.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(50,10),RLSE),
//            DCB=(RECFM=FB,LRECL=500,BLKSIZE=27500)
//SYSIN    DD *
  OPTION COPY
  INREC IFTHEN=(WHEN=INIT,
    FINDREP=(INOUT=(C'  ',C' ')))
/*
//*
//* STEP5: Convert EBCDIC to ASCII (if needed for download)
//*
//STEP5    EXEC PGM=IEBGENER
//SYSUT1   DD DSN=YOUR.OUTPUT.CLEAN.CSV,DISP=SHR
//SYSUT2   DD DSN=YOUR.OUTPUT.ASCII.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(50,10),RLSE),
//            DCB=(RECFM=FB,LRECL=500,BLKSIZE=27500)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  GENERATE MAXFLDS=1
  RECORD FIELD=(500,1,,1,TRAN=LTOU)
/*
//*
//* Alternative STEP5: Use SORT for EBCDIC to ASCII conversion
//*
//STEP5A   EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=YOUR.OUTPUT.CLEAN.CSV,DISP=SHR
//SORTOUT  DD DSN=YOUR.OUTPUT.ASCII.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(50,10),RLSE),
//            DCB=(RECFM=FB,LRECL=500,BLKSIZE=27500)
//SYSIN    DD *
  OPTION COPY,VLSCMP
  OUTFIL VTOF,CONVERT
/*
//*
//* Note: The final output dataset YOUR.OUTPUT.ASCII.CSV is ready
//*       for download via FTP or other file transfer method
//*
//* FTP Download Instructions:
//* 1. Connect to mainframe via FTP
//* 2. Use ASCII mode: quote site sbdataconn=(IBM-1047,ISO8859-1)
//* 3. GET YOUR.OUTPUT.ASCII.CSV local_file.csv
//*
