#!/usr/bin/env python3
"""
Demo script for migration flow schema.

This script demonstrates the complete functionality of the migration flow
schema implementation, including creation, data insertion, and querying.
"""

import sqlite3
from schema import MigrationFlowSchema
import json


def demo_schema():
    """Demonstrate migration flow schema functionality."""
    
    print("=" * 70)
    print("Migration Flow Schema Demo")
    print("=" * 70)
    
    # Create in-memory database
    print("\n1. Creating in-memory database...")
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    print("\n2. Creating migration flow schema...")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=True)
    
    # Verify schema
    print("\n3. Verifying schema...")
    if schema.is_schema_complete():
        print("✓ Schema is complete")
    else:
        print("✗ Schema is incomplete")
        return
    
    # Insert sample data
    print("\n4. Inserting sample data...")
    cursor = conn.cursor()
    
    # Sample flow: PAYROLL1 invoked by JCL and CICS
    print("\n   Creating FLOW_PAYROLL1...")
    cursor.execute("""
        INSERT INTO migration_flows (
            flow_id, name, entry_program, primary_entry_type,
            total_programs, total_copybooks, total_datasets,
            complexity_total_lines, complexity_cyclomatic,
            complexity_score, complexity_tier,
            priority, business_domain
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL',
        3, 2, 2,
        2500, 45, 67.5, 'MEDIUM',
        1, 'Finance'
    ))
    
    # Entry types - multiple invocation methods
    print("   Adding entry types (JCL x2, CICS x1)...")
    entry_types = [
        ('FLOW_PAYROLL1', 'JCL', 'PAYROLL01', json.dumps({
            'jclName': 'PAYROLL01',
            'jobName': 'PAYJOB',
            'stepName': 'STEP01'
        })),
        ('FLOW_PAYROLL1', 'JCL', 'PAYWEEK', json.dumps({
            'jclName': 'PAYWEEK',
            'jobName': 'WEEKLY',
            'stepName': 'PAYSTEP'
        })),
        ('FLOW_PAYROLL1', 'CICS_TRANSACTION', 'PAY1', json.dumps({
            'transactionId': 'PAY1',
            'csdGroup': 'PAYGRP'
        }))
    ]
    
    for entry in entry_types:
        cursor.execute("""
            INSERT INTO flow_entry_types (
                flow_id, entry_type, caller_source, metadata_json
            ) VALUES (?, ?, ?, ?)
        """, entry)
    
    # Scope - programs, copybooks, datasets
    print("   Adding scope (3 programs, 2 copybooks, 2 datasets)...")
    scope_items = [
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYROLL1'),
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYCALC'),
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYDB'),
        ('FLOW_PAYROLL1', 'COPYBOOK', 'PAYCOM'),
        ('FLOW_PAYROLL1', 'COPYBOOK', 'EMPDATA'),
        ('FLOW_PAYROLL1', 'DATASET', 'EMPLOYEE.MASTER'),
        ('FLOW_PAYROLL1', 'DATASET', 'PAYROLL.REPORT')
    ]
    
    for item in scope_items:
        cursor.execute("""
            INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
            VALUES (?, ?, ?)
        """, item)
    
    # Interfaces
    print("   Adding interfaces (1 inbound, 1 outbound)...")
    cursor.execute("""
        INSERT INTO flow_interfaces (
            flow_id, direction, interface_type, source, target, external
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'INBOUND', 'PROGRAM_CALL', 'EXTERNAL_PROG', 'PAYCALC', False))
    
    cursor.execute("""
        INSERT INTO flow_interfaces (
            flow_id, direction, interface_type, source, target, external
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'OUTBOUND', 'PROGRAM_CALL', 'PAYDB', 'DBUTIL', True))
    
    # Data operations
    print("   Adding data operations (2 database, 2 dataset)...")
    cursor.execute("""
        INSERT INTO flow_data_operations (
            flow_id, operation_category, operation_type, db_type, target, program
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'DATABASE', 'SELECT', 'DB2', 'EMPLOYEE_TABLE', 'PAYDB'))
    
    cursor.execute("""
        INSERT INTO flow_data_operations (
            flow_id, operation_category, operation_type, db_type, target, program
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'DATABASE', 'UPDATE', 'DB2', 'PAYROLL_TABLE', 'PAYDB'))
    
    cursor.execute("""
        INSERT INTO flow_data_operations (
            flow_id, operation_category, operation_type, target, program, mode
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'DATASET', 'READ', 'EMPLOYEE.MASTER', 'PAYROLL1', 'INPUT'))
    
    cursor.execute("""
        INSERT INTO flow_data_operations (
            flow_id, operation_category, operation_type, target, program, mode
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'DATASET', 'WRITE', 'PAYROLL.REPORT', 'PAYCALC', 'OUTPUT'))
    
    conn.commit()
    print("   ✓ Sample data inserted")
    
    # Query and display data
    print("\n5. Querying data...")
    
    # Flow metadata
    print("\n   Flow Metadata:")
    cursor.execute("SELECT * FROM migration_flows WHERE flow_id = ?", ('FLOW_PAYROLL1',))
    flow = cursor.fetchone()
    print(f"     Flow ID: {flow[0]}")
    print(f"     Name: {flow[1]}")
    print(f"     Entry Program: {flow[2]}")
    print(f"     Primary Entry Type: {flow[3]}")
    print(f"     Total Programs: {flow[4]}")
    print(f"     Complexity Tier: {flow[10]}")
    print(f"     Priority: {flow[11]}")
    print(f"     Business Domain: {flow[12]}")
    
    # Entry types
    print("\n   Entry Types:")
    cursor.execute("""
        SELECT entry_type, caller_source, metadata_json
        FROM flow_entry_types
        WHERE flow_id = ?
        ORDER BY entry_type, caller_source
    """, ('FLOW_PAYROLL1',))
    
    for entry_type, caller, metadata in cursor.fetchall():
        print(f"     {entry_type}: {caller}")
        if metadata:
            meta = json.loads(metadata)
            for key, value in meta.items():
                print(f"       - {key}: {value}")
    
    # Scope
    print("\n   Scope:")
    cursor.execute("""
        SELECT artifact_type, COUNT(*) as count
        FROM flow_scope
        WHERE flow_id = ?
        GROUP BY artifact_type
    """, ('FLOW_PAYROLL1',))
    
    for artifact_type, count in cursor.fetchall():
        print(f"     {artifact_type}: {count}")
    
    # Interfaces
    print("\n   Interfaces:")
    cursor.execute("""
        SELECT direction, interface_type, source, target, external
        FROM flow_interfaces
        WHERE flow_id = ?
    """, ('FLOW_PAYROLL1',))
    
    for direction, iface_type, source, target, external in cursor.fetchall():
        ext_flag = " (external)" if external else ""
        print(f"     {direction}: {source} -> {target} ({iface_type}){ext_flag}")
    
    # Data operations
    print("\n   Data Operations:")
    cursor.execute("""
        SELECT operation_category, operation_type, target, program
        FROM flow_data_operations
        WHERE flow_id = ?
    """, ('FLOW_PAYROLL1',))
    
    for category, op_type, target, program in cursor.fetchall():
        print(f"     {category}: {op_type} {target} (by {program})")
    
    # Table counts
    print("\n6. Table counts:")
    counts = schema.get_table_counts()
    for table, count in counts.items():
        print(f"   {table}: {count}")
    
    # Close connection
    conn.close()
    
    print("\n" + "=" * 70)
    print("✓ Demo completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    demo_schema()
