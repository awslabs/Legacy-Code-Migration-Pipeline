"""
Demo script for MigrationFlowBuilder.

This script demonstrates how to use the MigrationFlowBuilder to build
migration flows from analyzed code.
"""

import sqlite3
from flow_builder import MigrationFlowBuilder, generate_flow_id
from schema import MigrationFlowSchema


def demo_flow_id_generation():
    """Demonstrate flow ID generation."""
    print("=" * 60)
    print("DEMO: Flow ID Generation")
    print("=" * 60)
    
    programs = [
        "PAYROLL1",
        "PAY-ROLL#01",
        "billing",
        "ACCT_PROG"
    ]
    
    for program in programs:
        flow_id = generate_flow_id(program)
        print(f"  {program:20} → {flow_id}")
    
    print()


def demo_build_flow():
    """Demonstrate building a single flow."""
    print("=" * 60)
    print("DEMO: Building a Single Flow")
    print("=" * 60)
    
    # Create in-memory database
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    # Create sample dependencies
    cursor = conn.cursor()
    
    # Create artifact_dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artifact_dependencies (
            source_artifact_name VARCHAR(44),
            source_artifact_type VARCHAR(20),
            target_artifact_name VARCHAR(44),
            target_artifact_type VARCHAR(20),
            dependency_type VARCHAR(50),
            source_file_path TEXT,
            line_number INTEGER
        )
    """)
    
    # Add sample data
    cursor.execute("""
        INSERT INTO artifact_dependencies VALUES
        ('PAYROLL01', 'JCL', 'PAYROLL1', 'PROGRAM', 'JCL_EXEC', '/jcl/payroll01.jcl', 10)
    """)
    
    cursor.execute("""
        INSERT INTO artifact_dependencies VALUES
        ('PAYROLL1', 'PROGRAM', 'PAYCALC', 'PROGRAM', 'CALL', '/cobol/payroll1.cbl', 100)
    """)
    
    cursor.execute("""
        INSERT INTO artifact_dependencies VALUES
        ('PAYROLL1', 'PROGRAM', 'PAYCOM', 'COPYBOOK', 'COPY', '/cobol/payroll1.cbl', 20)
    """)
    
    conn.commit()
    
    # Build flow
    print("\nBuilding flow for PAYROLL1...")
    builder = MigrationFlowBuilder(conn)
    
    try:
        flow_id = builder.build_flow('PAYROLL1')
        print(f"✓ Successfully built flow: {flow_id}")
        
        # Query flow metadata
        cursor.execute("""
            SELECT flow_id, name, entry_program, primary_entry_type, total_programs
            FROM migration_flows WHERE flow_id = ?
        """, (flow_id,))
        
        row = cursor.fetchone()
        if row:
            print(f"\nFlow Metadata:")
            print(f"  Flow ID: {row[0]}")
            print(f"  Name: {row[1]}")
            print(f"  Entry Program: {row[2]}")
            print(f"  Primary Type: {row[3]}")
            print(f"  Total Programs: {row[4]}")
        
        # Query scope
        cursor.execute("""
            SELECT artifact_type, COUNT(*) 
            FROM flow_scope 
            WHERE flow_id = ?
            GROUP BY artifact_type
        """, (flow_id,))
        
        print(f"\nScope:")
        for artifact_type, count in cursor.fetchall():
            print(f"  {artifact_type}: {count}")
        
    except Exception as e:
        print(f"✗ Failed to build flow: {e}")
    
    conn.close()
    print()


def demo_build_all_flows():
    """Demonstrate building all flows."""
    print("=" * 60)
    print("DEMO: Building All Flows")
    print("=" * 60)
    
    # Create in-memory database
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    # Create sample dependencies
    cursor = conn.cursor()
    
    # Create artifact_dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artifact_dependencies (
            source_artifact_name VARCHAR(44),
            source_artifact_type VARCHAR(20),
            target_artifact_name VARCHAR(44),
            target_artifact_type VARCHAR(20),
            dependency_type VARCHAR(50),
            source_file_path TEXT,
            line_number INTEGER
        )
    """)
    
    # Add multiple entry points
    entry_points = [
        ('PAYROLL01', 'JCL', 'PAYROLL1', 'PROGRAM', 'JCL_EXEC'),
        ('BILLING01', 'JCL', 'BILLING1', 'PROGRAM', 'JCL_EXEC'),
        ('ACCT01', 'JCL', 'ACCTPROG', 'PROGRAM', 'JCL_EXEC')
    ]
    
    for source, source_type, target, target_type, dep_type in entry_points:
        cursor.execute("""
            INSERT INTO artifact_dependencies VALUES
            (?, ?, ?, ?, ?, ?, ?)
        """, (source, source_type, target, target_type, dep_type, f'/jcl/{source.lower()}.jcl', 10))
    
    conn.commit()
    
    # Build all flows
    print("\nBuilding all flows...")
    builder = MigrationFlowBuilder(conn)
    
    try:
        flow_ids = builder.build_all_flows()
        print(f"\n✓ Successfully built {len(flow_ids)} flows")
        
        # Query all flows
        cursor.execute("""
            SELECT flow_id, name, entry_program, total_programs
            FROM migration_flows
            ORDER BY flow_id
        """)
        
        print(f"\nFlows:")
        for flow_id, name, entry_program, total_programs in cursor.fetchall():
            print(f"  {flow_id:20} {name:20} ({total_programs} programs)")
        
    except Exception as e:
        print(f"✗ Failed to build flows: {e}")
    
    conn.close()
    print()


def demo_primary_type_determination():
    """Demonstrate primary type determination."""
    print("=" * 60)
    print("DEMO: Primary Type Determination")
    print("=" * 60)
    
    conn = sqlite3.connect(":memory:")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    builder = MigrationFlowBuilder(conn)
    
    # Test case 1: Single type
    print("\nCase 1: Single invocation type")
    entry_types = [
        {
            'type': 'JCL',
            'callers': [
                {'source': 'PAYROLL01', 'metadata': {}}
            ]
        }
    ]
    primary = builder._determine_primary_type(entry_types)
    print(f"  Entry types: JCL (1 caller)")
    print(f"  Primary type: {primary}")
    
    # Test case 2: Multiple types, clear winner
    print("\nCase 2: Multiple types, JCL has more callers")
    entry_types = [
        {
            'type': 'JCL',
            'callers': [
                {'source': 'PAYROLL01', 'metadata': {}},
                {'source': 'PAYWEEK', 'metadata': {}}
            ]
        },
        {
            'type': 'CICS_TRANSACTION',
            'callers': [
                {'source': 'PAY1', 'metadata': {}}
            ]
        }
    ]
    primary = builder._determine_primary_type(entry_types)
    print(f"  Entry types: JCL (2 callers), CICS_TRANSACTION (1 caller)")
    print(f"  Primary type: {primary}")
    
    # Test case 3: Tie, use priority
    print("\nCase 3: Tie, use priority order")
    entry_types = [
        {
            'type': 'CICS_TRANSACTION',
            'callers': [
                {'source': 'PAY1', 'metadata': {}}
            ]
        },
        {
            'type': 'JCL',
            'callers': [
                {'source': 'PAYROLL01', 'metadata': {}}
            ]
        }
    ]
    primary = builder._determine_primary_type(entry_types)
    print(f"  Entry types: CICS_TRANSACTION (1 caller), JCL (1 caller)")
    print(f"  Primary type: {primary} (JCL has higher priority)")
    
    conn.close()
    print()


def demo_database_schema():
    """Demonstrate database schema verification."""
    print("=" * 60)
    print("DEMO: Database Schema Verification")
    print("=" * 60)
    
    # Create in-memory database
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    # Verify schema
    print("\nVerifying schema...")
    verification = schema.verify_schema(verbose=False)
    
    print(f"\nSchema Verification Results:")
    for table, exists in verification.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {table}")
    
    # Check if complete
    is_complete = schema.is_schema_complete()
    print(f"\nSchema complete: {'✓ Yes' if is_complete else '✗ No'}")
    
    # Get table counts
    counts = schema.get_table_counts()
    print(f"\nTable Counts:")
    for table, count in counts.items():
        if count is not None:
            print(f"  {table}: {count} rows")
    
    conn.close()
    print()


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MigrationFlowBuilder Demo")
    print("=" * 60 + "\n")
    
    demo_flow_id_generation()
    demo_primary_type_determination()
    demo_database_schema()
    demo_build_flow()
    demo_build_all_flows()
    
    print("=" * 60)
    print("Demo Complete")
    print("=" * 60)


if __name__ == '__main__':
    main()
