"""
Demo script for MigrationFlowExporter.

This script demonstrates how to use the MigrationFlowExporter to export
migration flows from database to JSON format.
"""

import sqlite3
import json
from tools.legacy_analyzer.migration import (
    MigrationFlowSchema,
    MigrationFlowBuilder,
    MigrationFlowExporter
)


def demo_basic_export():
    """Demonstrate basic flow export."""
    print("=" * 80)
    print("DEMO: Basic Flow Export")
    print("=" * 80)
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    print("\n1. Creating migration flow schema...")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    print("   ✓ Schema created")
    
    # Insert sample flow data
    print("\n2. Inserting sample flow data...")
    cursor = conn.cursor()
    
    # Insert flow metadata
    cursor.execute("""
        INSERT INTO migration_flows (
            flow_id, name, entry_program, primary_entry_type,
            total_programs, total_copybooks, total_datasets,
            complexity_total_lines, complexity_cyclomatic,
            complexity_score, complexity_tier,
            priority, business_domain,
            created_date, updated_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL',
        3, 2, 2,
        2500, 45, 67.5, 'MEDIUM',
        1, 'Finance',
        '2024-01-01', '2024-01-01'
    ))
    
    # Insert entry types
    cursor.executemany("""
        INSERT INTO flow_entry_types (flow_id, entry_type, caller_source, metadata_json)
        VALUES (?, ?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'JCL', 'PAYROLL01', json.dumps({'jclName': 'PAYROLL01', 'jobName': 'PAYJOB'})),
        ('FLOW_PAYROLL1', 'JCL', 'PAYWEEK', json.dumps({'jclName': 'PAYWEEK', 'jobName': 'WEEKLY'})),
        ('FLOW_PAYROLL1', 'CICS_TRANSACTION', 'PAY1', json.dumps({'transactionId': 'PAY1'}))
    ])
    
    # Insert scope
    cursor.executemany("""
        INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
        VALUES (?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYROLL1'),
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYCALC'),
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYDB'),
        ('FLOW_PAYROLL1', 'COPYBOOK', 'PAYCOM'),
        ('FLOW_PAYROLL1', 'COPYBOOK', 'EMPDATA'),
        ('FLOW_PAYROLL1', 'DATASET', 'EMPLOYEE.MASTER'),
        ('FLOW_PAYROLL1', 'DATASET', 'PAYROLL.TRANS')
    ])
    
    # Insert interfaces
    cursor.executemany("""
        INSERT INTO flow_interfaces (
            flow_id, direction, interface_type, source, target, external, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'INBOUND', 'PROGRAM_CALL', 'EXTERNAL_PROG', 'PAYCALC', 0, 
         json.dumps({'callingProgram': 'EXTERNAL_PROG'})),
        ('FLOW_PAYROLL1', 'OUTBOUND', 'PROGRAM_CALL', 'PAYDB', 'DBUTIL', 1,
         json.dumps({'callingProgram': 'PAYDB'}))
    ])
    
    # Insert data operations
    cursor.executemany("""
        INSERT INTO flow_data_operations (
            flow_id, operation_category, operation_type, db_type, target, program, mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'DATABASE', 'SELECT', 'DB2', 'EMPLOYEE_TABLE', 'PAYDB', None),
        ('FLOW_PAYROLL1', 'DATABASE', 'UPDATE', 'DB2', 'PAYROLL_TABLE', 'PAYDB', None),
        ('FLOW_PAYROLL1', 'DATASET', 'ACCESS', None, 'EMPLOYEE.MASTER', 'PAYROLL1', 'INPUT'),
        ('FLOW_PAYROLL1', 'DATASET', 'ACCESS', None, 'PAYROLL.TRANS', 'PAYCALC', 'OUTPUT')
    ])
    
    conn.commit()
    print("   ✓ Sample data inserted")
    
    # Create exporter
    print("\n3. Creating MigrationFlowExporter...")
    exporter = MigrationFlowExporter(conn)
    print("   ✓ Exporter created")
    
    # Export flow
    print("\n4. Exporting flow...")
    result = exporter.export_flows(['FLOW_PAYROLL1'])
    
    print("\n5. Exported JSON:")
    print(json.dumps(result, indent=2))
    
    conn.close()


def demo_export_all_flows():
    """Demonstrate exporting all flows."""
    print("\n" + "=" * 80)
    print("DEMO: Export All Flows")
    print("=" * 80)
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    print("\n1. Creating schema and inserting multiple flows...")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    cursor = conn.cursor()
    
    # Insert multiple flows
    flows_data = [
        ('FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL', 3, 2, 2, 2500, 45, 67.5, 'MEDIUM', 1, 'Finance'),
        ('FLOW_BILLING1', 'Billing Processing', 'BILLING1', 'CICS_TRANSACTION', 2, 1, 1, 1500, 30, 45.0, 'LOW', 2, 'Finance'),
        ('FLOW_ACCT1', 'Accounting', 'ACCT1', 'JCL', 5, 3, 4, 5000, 80, 85.0, 'HIGH', 1, 'Finance')
    ]
    
    for flow_data in flows_data:
        cursor.execute("""
            INSERT INTO migration_flows (
                flow_id, name, entry_program, primary_entry_type,
                total_programs, total_copybooks, total_datasets,
                complexity_total_lines, complexity_cyclomatic,
                complexity_score, complexity_tier,
                priority, business_domain,
                created_date, updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*flow_data, '2024-01-01', '2024-01-01'))
        
        # Insert minimal entry type for each flow
        cursor.execute("""
            INSERT INTO flow_entry_types (flow_id, entry_type, caller_source, metadata_json)
            VALUES (?, ?, ?, ?)
        """, (flow_data[0], flow_data[3], flow_data[2], '{}'))
        
        # Insert minimal scope
        cursor.execute("""
            INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
            VALUES (?, ?, ?)
        """, (flow_data[0], 'PROGRAM', flow_data[2]))
    
    conn.commit()
    print("   ✓ 3 flows inserted")
    
    # Create exporter
    exporter = MigrationFlowExporter(conn)
    
    # Export all flows
    print("\n2. Exporting all flows...")
    result = exporter.export_all_flows()
    
    print(f"\n   ✓ Exported {len(result['flows'])} flows")
    for flow in result['flows']:
        print(f"     - {flow['flowId']}: {flow['name']} ({flow['complexity']['tier']} complexity)")
    
    conn.close()


def demo_filtered_export():
    """Demonstrate filtered export."""
    print("\n" + "=" * 80)
    print("DEMO: Filtered Export")
    print("=" * 80)
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    print("\n1. Creating schema and inserting flows...")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    cursor = conn.cursor()
    
    # Insert flows with different characteristics
    flows_data = [
        ('FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL', 3, 2, 2, 2500, 45, 67.5, 'MEDIUM', 1, 'Finance'),
        ('FLOW_BILLING1', 'Billing Processing', 'BILLING1', 'CICS_TRANSACTION', 2, 1, 1, 1500, 30, 45.0, 'LOW', 2, 'Finance'),
        ('FLOW_ACCT1', 'Accounting', 'ACCT1', 'JCL', 5, 3, 4, 5000, 80, 85.0, 'HIGH', 1, 'Finance'),
        ('FLOW_INVENTORY1', 'Inventory', 'INV1', 'CICS_TRANSACTION', 4, 2, 3, 3500, 60, 72.0, 'MEDIUM', 3, 'Operations')
    ]
    
    for flow_data in flows_data:
        cursor.execute("""
            INSERT INTO migration_flows (
                flow_id, name, entry_program, primary_entry_type,
                total_programs, total_copybooks, total_datasets,
                complexity_total_lines, complexity_cyclomatic,
                complexity_score, complexity_tier,
                priority, business_domain,
                created_date, updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*flow_data, '2024-01-01', '2024-01-01'))
        
        # Insert minimal entry type
        cursor.execute("""
            INSERT INTO flow_entry_types (flow_id, entry_type, caller_source, metadata_json)
            VALUES (?, ?, ?, ?)
        """, (flow_data[0], flow_data[3], flow_data[2], '{}'))
        
        # Insert minimal scope
        cursor.execute("""
            INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
            VALUES (?, ?, ?)
        """, (flow_data[0], 'PROGRAM', flow_data[2]))
    
    conn.commit()
    print("   ✓ 4 flows inserted")
    
    # Create exporter
    exporter = MigrationFlowExporter(conn)
    
    # Filter by complexity
    print("\n2. Filter by complexity (HIGH and above)...")
    result = exporter.export_all_flows(min_complexity='HIGH')
    print(f"   ✓ Found {len(result['flows'])} flows:")
    for flow in result['flows']:
        print(f"     - {flow['flowId']}: {flow['complexity']['tier']} complexity")
    
    # Filter by business domain
    print("\n3. Filter by business domain (Finance)...")
    result = exporter.export_all_flows(business_domain='Finance')
    print(f"   ✓ Found {len(result['flows'])} flows:")
    for flow in result['flows']:
        print(f"     - {flow['flowId']}: {flow['businessDomain']}")
    
    # Filter by entry type
    print("\n4. Filter by entry type (JCL)...")
    result = exporter.export_all_flows(entry_type='JCL')
    print(f"   ✓ Found {len(result['flows'])} flows:")
    for flow in result['flows']:
        print(f"     - {flow['flowId']}: {flow['entryPoint']['primaryType']}")
    
    # Combined filters
    print("\n5. Combined filters (MEDIUM+ complexity AND Finance domain)...")
    result = exporter.export_all_flows(
        min_complexity='MEDIUM',
        business_domain='Finance'
    )
    print(f"   ✓ Found {len(result['flows'])} flows:")
    for flow in result['flows']:
        print(f"     - {flow['flowId']}: {flow['complexity']['tier']} complexity, {flow['businessDomain']}")
    
    conn.close()


def demo_export_to_file():
    """Demonstrate exporting to file."""
    print("\n" + "=" * 80)
    print("DEMO: Export to File")
    print("=" * 80)
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    print("\n1. Creating schema and inserting flow...")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    cursor = conn.cursor()
    
    # Insert sample flow
    cursor.execute("""
        INSERT INTO migration_flows (
            flow_id, name, entry_program, primary_entry_type,
            total_programs, total_copybooks, total_datasets,
            complexity_total_lines, complexity_cyclomatic,
            complexity_score, complexity_tier,
            created_date, updated_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL',
        3, 2, 2,
        2500, 45, 67.5, 'MEDIUM',
        '2024-01-01', '2024-01-01'
    ))
    
    cursor.execute("""
        INSERT INTO flow_entry_types (flow_id, entry_type, caller_source, metadata_json)
        VALUES (?, ?, ?, ?)
    """, ('FLOW_PAYROLL1', 'JCL', 'PAYROLL01', '{}'))
    
    cursor.execute("""
        INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
        VALUES (?, ?, ?)
    """, ('FLOW_PAYROLL1', 'PROGRAM', 'PAYROLL1'))
    
    conn.commit()
    print("   ✓ Flow inserted")
    
    # Create exporter
    exporter = MigrationFlowExporter(conn)
    
    # Export to file
    output_file = '/tmp/Business_Flows.json'
    print(f"\n2. Exporting to file: {output_file}")
    result = exporter.export_flows(['FLOW_PAYROLL1'], output_file=output_file)
    
    print(f"   ✓ Exported to {output_file}")
    print(f"   ✓ File contains {len(result['flows'])} flow(s)")
    
    # Read and display file
    print("\n3. File contents:")
    with open(output_file, 'r') as f:
        content = f.read()
        print(content[:500] + "..." if len(content) > 500 else content)
    
    conn.close()


def demo_query_methods():
    """Demonstrate individual query methods."""
    print("\n" + "=" * 80)
    print("DEMO: Individual Query Methods")
    print("=" * 80)
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    print("\n1. Creating schema and inserting flow...")
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    cursor = conn.cursor()
    
    # Insert comprehensive flow data
    cursor.execute("""
        INSERT INTO migration_flows (
            flow_id, name, entry_program, primary_entry_type,
            total_programs, total_copybooks, total_datasets,
            complexity_total_lines, complexity_cyclomatic,
            complexity_score, complexity_tier,
            created_date, updated_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL',
        3, 2, 2,
        2500, 45, 67.5, 'MEDIUM',
        '2024-01-01', '2024-01-01'
    ))
    
    # Insert entry types
    cursor.executemany("""
        INSERT INTO flow_entry_types (flow_id, entry_type, caller_source, metadata_json)
        VALUES (?, ?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'JCL', 'PAYROLL01', json.dumps({'jclName': 'PAYROLL01'})),
        ('FLOW_PAYROLL1', 'CICS_TRANSACTION', 'PAY1', json.dumps({'transactionId': 'PAY1'}))
    ])
    
    # Insert scope
    cursor.executemany("""
        INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
        VALUES (?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYROLL1'),
        ('FLOW_PAYROLL1', 'PROGRAM', 'PAYCALC'),
        ('FLOW_PAYROLL1', 'COPYBOOK', 'PAYCOM'),
        ('FLOW_PAYROLL1', 'DATASET', 'EMPLOYEE.MASTER')
    ])
    
    conn.commit()
    print("   ✓ Flow inserted")
    
    # Create exporter
    exporter = MigrationFlowExporter(conn)
    
    # Query entry types
    print("\n2. Query entry types:")
    entry_types = exporter._query_entry_types('FLOW_PAYROLL1')
    for entry_type in entry_types:
        print(f"   - Type: {entry_type['type']}")
        for caller in entry_type['callers']:
            print(f"     Caller: {caller['source']}")
    
    # Query scope
    print("\n3. Query scope:")
    scope = exporter._query_scope('FLOW_PAYROLL1')
    print(f"   - Programs: {', '.join(scope['programs'])}")
    print(f"   - Copybooks: {', '.join(scope['copybooks'])}")
    print(f"   - Datasets: {', '.join(scope['datasets'])}")
    
    # Check flow existence
    print("\n4. Check flow existence:")
    print(f"   - FLOW_PAYROLL1 exists: {exporter.flow_exists('FLOW_PAYROLL1')}")
    print(f"   - FLOW_NONEXISTENT exists: {exporter.flow_exists('FLOW_NONEXISTENT')}")
    
    # Get flow count
    print("\n5. Get flow count:")
    print(f"   - Total flows: {exporter.get_flow_count()}")
    
    # Get flow IDs
    print("\n6. Get all flow IDs:")
    flow_ids = exporter.get_flow_ids()
    print(f"   - Flow IDs: {', '.join(flow_ids)}")
    
    conn.close()


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("MIGRATION FLOW EXPORTER DEMO")
    print("=" * 80)
    
    demo_basic_export()
    demo_export_all_flows()
    demo_filtered_export()
    demo_export_to_file()
    demo_query_methods()
    
    print("\n" + "=" * 80)
    print("ALL DEMOS COMPLETED")
    print("=" * 80)


if __name__ == '__main__':
    main()
