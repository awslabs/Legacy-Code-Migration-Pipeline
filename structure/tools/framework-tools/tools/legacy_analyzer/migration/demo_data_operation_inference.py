"""
Demo script for DataOperationInferencer.

This script demonstrates how to use the DataOperationInferencer to infer
data operations (database and dataset operations) from dependency data.
"""

import sqlite3
from data_operation_inferencer import DataOperationInferencer


def create_demo_database():
    """Create a demo database with sample dependencies."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create artifact_dependencies table
    cursor.execute("""
        CREATE TABLE artifact_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_artifact_name VARCHAR(44) NOT NULL,
            source_artifact_type VARCHAR(20) NOT NULL,
            target_artifact_name VARCHAR(44) NOT NULL,
            target_artifact_type VARCHAR(20) NOT NULL,
            dependency_type VARCHAR(20) NOT NULL,
            source_file_path VARCHAR(255),
            target_file_path VARCHAR(255),
            line_number INTEGER
        )
    """)
    
    # Insert sample dependencies
    sample_deps = [
        # SQL operations
        ("PAYROLL1", "PROGRAM", "SELECT * FROM EMPLOYEE WHERE DEPT = 'PAYROLL'", "TABLE", "EXEC_SQL"),
        ("PAYROLL1", "PROGRAM", "UPDATE PAYROLL SET AMOUNT = 1000", "TABLE", "EXEC_SQL"),
        ("BILLING1", "PROGRAM", "INSERT INTO INVOICE VALUES (1, 'ACME', 500.00)", "TABLE", "EXEC_SQL"),
        ("BILLING1", "PROGRAM", "DELETE FROM TEMP_INVOICE WHERE ID = 1", "TABLE", "EXEC_SQL"),
        
        # CICS file operations
        ("CUSTMGR", "PROGRAM", "CUSTFILE", "FILE", "CICS_READ"),
        ("CUSTMGR", "PROGRAM", "CUSTFILE", "FILE", "CICS_WRITE"),
        ("ORDERMGR", "PROGRAM", "ORDERFILE", "FILE", "CICS_REWRITE"),
        ("ORDERMGR", "PROGRAM", "ORDERFILE", "FILE", "CICS_DELETE"),
        
        # Dataset operations
        ("PAYROLL1", "PROGRAM", "EMPLOYEE.MASTER", "DATASET", "FILE_READ"),
        ("PAYROLL1", "PROGRAM", "PAYROLL.REPORT", "DATASET", "FILE_WRITE"),
        ("BILLING1", "PROGRAM", "INVOICE.DATA DISP=SHR", "DATASET", "JCL_DD"),
        ("BILLING1", "PROGRAM", "INVOICE.REPORT DISP=NEW", "DATASET", "JCL_DD"),
        
        # Shared dataset (multiple programs)
        ("PROG1", "PROGRAM", "SHARED.DATA", "DATASET", "FILE_READ"),
        ("PROG2", "PROGRAM", "SHARED.DATA", "DATASET", "FILE_WRITE"),
        ("PROG3", "PROGRAM", "SHARED.DATA", "DATASET", "FILE_READ"),
        
        # VSAM browse operations
        ("BROWSER", "PROGRAM", "VSAMFILE", "FILE", "CICS_STARTBR"),
        ("BROWSER", "PROGRAM", "VSAMFILE", "FILE", "CICS_READNEXT"),
    ]
    
    for dep in sample_deps:
        cursor.execute("""
            INSERT INTO artifact_dependencies 
            (source_artifact_name, source_artifact_type, target_artifact_name, 
             target_artifact_type, dependency_type)
            VALUES (?, ?, ?, ?, ?)
        """, dep)
    
    conn.commit()
    return conn


def demo_basic_usage():
    """Demonstrate basic usage of DataOperationInferencer."""
    print("=" * 80)
    print("Demo: Basic Usage of DataOperationInferencer")
    print("=" * 80)
    print()
    
    # Create demo database
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Infer operations for PAYROLL1
    print("1. Inferring operations for PAYROLL1:")
    print("-" * 80)
    operations = inferencer.infer_all_operations(["PAYROLL1"])
    
    print(f"\nDatabase Operations ({len(operations['databases'])}):")
    for op in operations['databases']:
        print(f"  - {op['operation']} on {op['target']} ({op['type']}) by {op['program']}")
    
    print(f"\nDataset Operations ({len(operations['datasets'])}):")
    for op in operations['datasets']:
        print(f"  - {op['name']} ({op['mode']}) accessed by {', '.join(op['programs'])}")
    
    print()
    
    conn.close()


def demo_database_operations():
    """Demonstrate database operation inference."""
    print("=" * 80)
    print("Demo: Database Operation Inference")
    print("=" * 80)
    print()
    
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Infer database operations for multiple programs
    programs = ["PAYROLL1", "BILLING1", "CUSTMGR", "ORDERMGR"]
    
    for program in programs:
        print(f"\n{program}:")
        print("-" * 40)
        operations = inferencer.infer_database_operations([program])
        
        if operations:
            for op in operations:
                print(f"  {op['type']:8} {op['operation']:8} {op['target']}")
        else:
            print("  No database operations found")
    
    print()
    conn.close()


def demo_dataset_operations():
    """Demonstrate dataset operation inference."""
    print("=" * 80)
    print("Demo: Dataset Operation Inference")
    print("=" * 80)
    print()
    
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Infer dataset operations for all programs
    programs = ["PAYROLL1", "BILLING1", "PROG1", "PROG2", "PROG3"]
    operations = inferencer.infer_dataset_operations(programs)
    
    print("Dataset Access Summary:")
    print("-" * 80)
    print(f"{'Dataset Name':<30} {'Mode':<10} {'Programs'}")
    print("-" * 80)
    
    for op in operations:
        programs_str = ', '.join(op['programs'])
        print(f"{op['name']:<30} {op['mode']:<10} {programs_str}")
    
    print()
    conn.close()


def demo_cics_operations():
    """Demonstrate CICS operation inference."""
    print("=" * 80)
    print("Demo: CICS Operation Inference")
    print("=" * 80)
    print()
    
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Infer CICS operations
    programs = ["CUSTMGR", "ORDERMGR", "BROWSER"]
    
    print("CICS File Operations:")
    print("-" * 80)
    
    for program in programs:
        operations = inferencer.infer_database_operations([program])
        
        if operations:
            print(f"\n{program}:")
            for op in operations:
                print(f"  {op['operation']:10} {op['target']} (VSAM)")
    
    print()
    conn.close()


def demo_operation_summary():
    """Demonstrate operation summary statistics."""
    print("=" * 80)
    print("Demo: Operation Summary Statistics")
    print("=" * 80)
    print()
    
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Get summary for different program groups
    program_groups = {
        "Payroll System": ["PAYROLL1"],
        "Billing System": ["BILLING1"],
        "Customer Management": ["CUSTMGR", "ORDERMGR"],
        "All Programs": ["PAYROLL1", "BILLING1", "CUSTMGR", "ORDERMGR", "PROG1", "PROG2", "PROG3", "BROWSER"]
    }
    
    for group_name, programs in program_groups.items():
        summary = inferencer.get_operation_summary(programs)
        
        print(f"\n{group_name}:")
        print("-" * 40)
        print(f"  Total Database Operations: {summary['total_database_operations']}")
        print(f"  Unique Tables/Files:        {summary['unique_tables']}")
        print(f"  Total Datasets:             {summary['total_datasets']}")
        print(f"  Unique Datasets:            {summary['unique_datasets']}")
    
    print()
    conn.close()


def demo_sql_parsing():
    """Demonstrate SQL statement parsing."""
    print("=" * 80)
    print("Demo: SQL Statement Parsing")
    print("=" * 80)
    print()
    
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Test SQL statements
    sql_statements = [
        "SELECT * FROM CUSTOMER WHERE ID = 1",
        "INSERT INTO EMPLOYEE VALUES (1, 'JOHN', 'DOE')",
        "UPDATE PAYROLL SET AMOUNT = 1000 WHERE ID = 5",
        "DELETE FROM TEMP_DATA WHERE DATE < '2024-01-01'",
        "MERGE INTO TARGET USING SOURCE ON ...",
        "CUSTOMER_TABLE",  # Plain table name
    ]
    
    print("SQL Statement Parsing:")
    print("-" * 80)
    print(f"{'SQL Statement':<50} {'Operation':<10} {'Table'}")
    print("-" * 80)
    
    for sql in sql_statements:
        operation = inferencer._parse_sql_operation(sql)
        table = inferencer._extract_table_from_sql(sql)
        sql_short = sql[:47] + "..." if len(sql) > 50 else sql
        print(f"{sql_short:<50} {operation:<10} {table or 'N/A'}")
    
    print()
    conn.close()


def demo_dataset_mode_inference():
    """Demonstrate dataset mode inference."""
    print("=" * 80)
    print("Demo: Dataset Mode Inference")
    print("=" * 80)
    print()
    
    conn = create_demo_database()
    inferencer = DataOperationInferencer(conn)
    
    # Test dataset mode inference
    test_cases = [
        ("FILE_READ", "EMPLOYEE.MASTER"),
        ("FILE_WRITE", "PAYROLL.REPORT"),
        ("JCL_DD", "INPUT.DATA DISP=SHR"),
        ("JCL_DD", "OUTPUT.DATA DISP=NEW"),
        ("JCL_DD", "UPDATE.DATA DISP=OLD"),
        ("JCL_DD", "APPEND.DATA DISP=MOD"),
        ("DATASET", "UNKNOWN.DATA"),
    ]
    
    print("Dataset Mode Inference:")
    print("-" * 80)
    print(f"{'Dependency Type':<20} {'Dataset Name':<30} {'Inferred Mode'}")
    print("-" * 80)
    
    for dep_type, dataset_name in test_cases:
        mode = inferencer._infer_dataset_mode(dep_type, dataset_name)
        print(f"{dep_type:<20} {dataset_name:<30} {mode}")
    
    print()
    conn.close()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DataOperationInferencer Demo" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    demo_basic_usage()
    demo_database_operations()
    demo_dataset_operations()
    demo_cics_operations()
    demo_operation_summary()
    demo_sql_parsing()
    demo_dataset_mode_inference()
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
