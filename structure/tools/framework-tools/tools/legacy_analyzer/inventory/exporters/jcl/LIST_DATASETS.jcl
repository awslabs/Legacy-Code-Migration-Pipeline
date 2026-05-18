//LISTDS   JOB (ACCT),'LIST DATASETS',CLASS=A,MSGCLASS=X,
//             NOTIFY=&SYSUID
//*
//* Purpose: List all datasets using IDCAMS LISTCAT
//* Output:  CSV format with dataset_name, creation_date,
//*          last_referenced, size_mb, volume, dataset_type
//*
//* Instructions:
//* 1. Update the catalog name if needed (default is master catalog)
//* 2. Update high-level qualifiers to match your environment
//* 3. Submit this JCL
//* 4. Download the output dataset for analysis
//*
//*********************************************************************
//*
//* STEP1: List all non-VSAM datasets
//*
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD DSN=&&LISTCAT1,DISP=(NEW,PASS),
//            SPACE=(TRK,(500,100)),
//            DCB=(RECFM=FBA,LRECL=121,BLKSIZE=12100)
//SYSIN    DD *
  LISTCAT ENTRIES('PROD.**') -
    NONVSAM -
    ALL
  LISTCAT ENTRIES('TEST.**') -
    NONVSAM -
    ALL
  LISTCAT ENTRIES('DEV.**') -
    NONVSAM -
    ALL
/*
//*
//* STEP2: List all VSAM datasets
//*
//STEP2    EXEC PGM=IDCAMS
//SYSPRINT DD DSN=&&LISTCAT2,DISP=(NEW,PASS),
//            SPACE=(TRK,(500,100)),
//            DCB=(RECFM=FBA,LRECL=121,BLKSIZE=12100)
//SYSIN    DD *
  LISTCAT ENTRIES('PROD.**') -
    CLUSTER -
    ALL
  LISTCAT ENTRIES('TEST.**') -
    CLUSTER -
    ALL
  LISTCAT ENTRIES('DEV.**') -
    CLUSTER -
    ALL
/*
//*
//* STEP3: List GDG bases
//*
//STEP3    EXEC PGM=IDCAMS
//SYSPRINT DD DSN=&&LISTCAT3,DISP=(NEW,PASS),
//            SPACE=(TRK,(100,20)),
//            DCB=(RECFM=FBA,LRECL=121,BLKSIZE=12100)
//SYSIN    DD *
  LISTCAT ENTRIES('PROD.**') -
    GDG -
    ALL
  LISTCAT ENTRIES('TEST.**') -
    GDG -
    ALL
/*
//*
//* STEP4: Parse LISTCAT output and extract key fields
//*
//STEP4    EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=&&LISTCAT1,DISP=(OLD,DELETE)
//         DD DSN=&&LISTCAT2,DISP=(OLD,DELETE)
//         DD DSN=&&LISTCAT3,DISP=(OLD,DELETE)
//SORTOUT  DD DSN=&&PARSED,DISP=(NEW,PASS),
//            SPACE=(TRK,(200,50)),
//            DCB=(RECFM=FB,LRECL=200,BLKSIZE=20000)
//SYSIN    DD *
  SORT FIELDS=(1,44,CH,A)
  INCLUDE COND=((10,7,CH,EQ,C'NONVSAM'),OR,
                (10,7,CH,EQ,C'CLUSTER'),OR,
                (10,3,CH,EQ,C'GDG'))
/*
//*
//* STEP5: Format as CSV with calculated sizes
//*
//STEP5    EXEC PGM=ICETOOL
//TOOLMSG  DD SYSOUT=*
//DFSMSG   DD SYSOUT=*
//IN       DD DSN=&&PARSED,DISP=(OLD,DELETE)
//OUT      DD DSN=EXPORT.DATASET.INVENTORY.CSV,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(100,20),RLSE),
//            DCB=(RECFM=FB,LRECL=200,BLKSIZE=20000)
//TOOLIN   DD *
  COPY FROM(IN) TO(OUT) USING(CTL1)
/*
//CTL1CNTL DD *
  OPTION COPY
  HEADER1=(1:C'dataset_name,creation_date,last_referenced,',
           C'size_mb,volume,dataset_type')
  INREC BUILD=(1,44,C',',50,10,C',',65,10,C',',
               80,10,C',',95,6,C',',105,10)
/*
//*
//* STEP6: Alternative - Get space information using DCOLLECT
//*
//STEP6    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  DCOLLECT -
    OFILE(DCOUT) -
    VOLUMES(*)
/*
//DCOUT    DD DSN=EXPORT.DCOLLECT.DATA,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(TRK,(500,100),RLSE),
//            DCB=(RECFM=VB,LRECL=644,BLKSIZE=6480)
//*
//* Note: The output dataset EXPORT.DATASET.INVENTORY.CSV contains
//*       CSV formatted data ready for download and analysis
//*
//* Alternative: DCOLLECT output (STEP6) provides more detailed
//*              space and allocation information but requires
//*              additional parsing
//*
