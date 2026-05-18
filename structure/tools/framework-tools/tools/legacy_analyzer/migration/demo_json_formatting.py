#!/usr/bin/env python3
"""
Demo: JSON Formatting for Migration Flow Export

This script demonstrates the JSON formatting capabilities of the
MigrationFlowExporter, showing how flow data is formatted into the
migration-focused JSON schema.

Usage:
    python demo_json_formatting.py
"""

import sqlite3
import json
from tools.legacy_analyzer.migration import (
    MigrationFlowExporter,
    MigrationFlowSchema
)


def create_demo_database():
    """Create an in-memory database with sample flow data."""
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    
    cursor = conn.cursor()
    
    # Insert sample flow: PAYROLL1
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
    
    # Insert entry types (multiple invocation mechanisms)
    cursor.executemany("""
        INSERT INTO flow_entry_types (flow_id, entry_type, caller_source, metadata_json)
        VALUES (?, ?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'JCL', 'PAYROLL01', 
         json.dumps({'jclName': 'PAYROLL01', 'jobName': 'PAYJOB', 'stepName': 'STEP01'})),
        ('FLOW_PAYROLL1', 'JCL', 'PAYWEEK', 
         json.dumps({'jclName': 'PAYWEEK', 'jobName': 'WEEKLY', 'stepName': 'PAYSTEP'})),
        ('FLOW_PAYROLL1', 'CICS_TRANSACTION', 'PAY1', 
         json.dumps({'transactionId': 'PAY1', 'csdGroup': 'PAYGRP'})),
        ('FLOW_PAYROLL1', 'CICS_PROGRAM', 'PAYROLL1',
         json.dumps({'programName': 'PAYROLL1', 'csdGroup': 'PAYGRP'}))
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
         json.dumps({'callingProgram': 'PAYDB'})),
        ('FLOW_PAYROLL1', 'OUTBOUND', 'CICS_LINK', 'PAYCALC', 'EXTCICS', 1,
         json.dumps({'program': 'EXTCICS'}))
    ])
    
    # Insert data operations
    cursor.executemany("""
        INSERT INTO flow_data_operations (
            flow_id, operation_category, operation_type, db_type, target, program, mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ('FLOW_PAYROLL1', 'DATABASE', 'SELECT', 'DB2', 'EMPLOYEE_TABLE', 'PAYDB', None),
        ('FLOW_PAYROLL1', 'DATABASE', 'UPDATE', 'DB2', 'PAYROLL_TABLE', 'PAYDB', None),
        ('FLOW_PAYROLL1', 'DATABASE', 'INSERT', 'DB2', 'AUDIT_TABLE', 'PAYCALC', None),
        ('FLOW_PAYROLL1', 'DATASET', 'ACCESS', None, 'EMPLOYEE.MASTER', 'PAYROLL1', 'INPUT'),
        ('FLOW_PAYROLL1', 'DATASET', 'ACCESS', None, 'PAYROLL.TRANS', 'PAYCALC', 'OUTPUT'),
        ('FLOW_PAYROLL1', 'DATASET', 'ACCESS', None, 'PAYROLL.TRANS', 'PAYDB', 'OUTPUT')
    ])
    
    # Insert dependencies
    cursor.execute("""
        INSERT INTO flow_dependencies (flow_id, depends_on_flow_id, dependency_type)
        VALUES (?, ?, ?)
    """, ('FLOW_PAYROLL1', 'FLOW_EMPMASTER', 'REQUIRED'))
    
    conn.commit()
    
    return conn


def demo_json_formatting():
    """Demonstrate JSON formatting capabilities."""
    print("=" * 80)
    print("JSON Formatting Demo")
    print("=" * 80)
    print()
    
    # Create demo database
    print("Creating demo database with sample flow...")
    db = create_demo_database()
    
    # Create exporter
    exporter = MigrationFlowExporter(db)
    
    print(f"✓ Database created with {exporter.get_flow_count()} flow(s)")
    print()
    
    # Export flow
    print("Exporting flow to JSON...")
    result = exporter.export_flows(['FLOW_PAYROLL1'])
    
    print("✓ Flow exported successfully")
    print()
    
    # Display JSON
    print("=" * 80)
    print("Formatted JSON Output")
    print("=" * 80)
    print()
    print(json.dumps(result, indent=2))
    print()
    
    # Highlight key features
    print("=" * 80)
    print("Key Features Demonstrated")
    print("=" * 80)
    print()
    
    flow = result['flows'][0]
    
    print("1. Flow Object Structure:")
    print(f"   - Flow ID: {flow['flowId']}")
    print(f"   - Name: {flow['name']}")
    print(f"   - Entry Program: {flow['entryPoint']['program']}")
    print()
    
    print("2. Multiple Entry Point Types:")
    for entry_type in flow['entryPoint']['types']:
        print(f"   - Type: {entry_type['type']}")
        print(f"     Callers: {len(entry_type['callers'])}")
        for caller in entry_type['callers']:
            print(f"       • {caller['source']}")
    print()
    
    print("3. Scope Separation:")
    print(f"   - Programs: {len(flow['scope']['programs'])} ({', '.join(flow['scope']['programs'])})")
    print(f"   - Copybooks: {len(flow['scope']['copybooks'])} ({', '.join(flow['scope']['copybooks'])})")
    print(f"   - Datasets: {len(flow['scope']['datasets'])} ({', '.join(flow['scope']['datasets'])})")
    print()
    
    print("4. Interface Boundaries:")
    print(f"   - Inbound: {len(flow['interfaces']['inbound'])} interface(s)")
    for iface in flow['interfaces']['inbound']:
        print(f"       • {iface['source']} → {iface['target']} ({iface['type']})")
    print(f"   - Outbound: {len(flow['interfaces']['outbound'])} interface(s)")
    for iface in flow['interfaces']['outbound']:
        print(f"       • {iface['source']} → {iface['target']} ({iface['type']})")
    print()
    
    print("5. Data Operations:")
    print(f"   - Database Operations: {len(flow['dataOperations']['databases'])}")
    for db_op in flow['dataOperations']['databases']:
        print(f"       • {db_op['program']}: {db_op['operation']} on {db_op['target']} ({db_op['type']})")
    print(f"   - Dataset Operations: {len(flow['dataOperations']['datasets'])}")
    for ds_op in flow['dataOperations']['datasets']:
        print(f"       • {ds_op['name']} ({ds_op['mode']}) - {len(ds_op['programs'])} program(s)")
    print()
    
    print("6. Complexity Metrics:")
    print(f"   - Total Programs: {flow['complexity']['totalPrograms']}")
    print(f"   - Total Lines: {flow['complexity']['totalLines']}")
    print(f"   - Cyclomatic Complexity: {flow['complexity']['cyclomaticComplexity']}")
    print(f"   - Composite Score: {flow['complexity']['compositeScore']}")
    print(f"   - Tier: {flow['complexity']['tier']}")
    print()
    
    print("7. Optional Fields:")
    if 'priority' in flow:
        print(f"   - Priority: {flow['priority']}")
    if 'businessDomain' in flow:
        print(f"   - Business Domain: {flow['businessDomain']}")
    if 'primaryType' in flow['entryPoint']:
        print(f"   - Primary Entry Type: {flow['entryPoint']['primaryType']}")
    print()
    
    print("8. Dependencies:")
    print(f"   - Required Flows: {len(flow['dependencies']['requiredFlows'])}")
    for req_flow in flow['dependencies']['requiredFlows']:
        print(f"       • {req_flow}")
    print(f"   - Dependent Flows: {len(flow['dependencies']['dependentFlows'])}")
    print()
    
    # Close database
    db.close()
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == '__main__':
    demo_json_formatting()
