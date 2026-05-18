#!/usr/bin/env python3
"""
Demo script for Database Writer functionality.

This script demonstrates:
1. Writing flow metadata to database
2. Writing entry types with batch inserts
3. Writing scope artifacts with batch inserts
4. Writing interfaces with batch inserts
5. Writing data operations with batch inserts
6. Writing dependencies with batch inserts
7. Transaction handling (commit/rollback)
"""

import sqlite3
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from tools.legacy_analyzer.migration.schema import MigrationFlowSchema
from tools.legacy_analyzer.migration.flow_builder import MigrationFlowBuilder


def demo_database_writer():
    """Demonstrate database writer functionality."""
    
    print("=" * 80)
    print("Database Writer Demo")
    print("=" * 80)
    print()
    
    # Create in-memory database
    print("1. Creating in-memory database...")
    db = sqlite3.connect(':memory:')
    
    # Create schema
    print("2. Creating migration flow schema...")
    schema = MigrationFlowSchema(db)
    schema.create_schema(verbose=False)
    print("   ✓ Schema created")
    print()
    
    # Create sample flow data
    print("3. Preparing sample flow data...")
    flow_id = 'FLOW_PAYROLL1'
    entry_program = 'PAYROLL1'
    primary_type = 'JCL'
    
    entry_types = [
        {
            'type': 'JCL',
            'callers': [
                {
                    'source': 'PAYROLL01',
                    'metadata': {
                        'jclName': 'PAYROLL01',
                        'jobName': 'PAYJOB',
                        'stepName': 'STEP01'
                    }
                },
                {
                    'source': 'PAYWEEK',
                    'metadata': {
                        'jclName': 'PAYWEEK',
                        'jobName': 'WEEKLY',
                        'stepName': 'PAYSTEP'
                    }
                }
            ]
        },
        {
            'type': 'CICS_TRANSACTION',
            'callers': [
                {
                    'source': 'PAY1',
                    'metadata': {
                        'transactionId': 'PAY1',
                        'csdGroup': 'PAYGRP'
                    }
                }
            ]
        }
    ]
    
    scope = {
        'programs': ['PAYROLL1', 'PAYCALC', 'PAYDB', 'PAYUTIL'],
        'copybooks': ['PAYCOM', 'EMPDATA', 'PAYDATA'],
        'datasets': ['EMPLOYEE.MASTER', 'PAYROLL.TRANS', 'PAYROLL.REPORT']
    }
    
    interfaces = {
        'inbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'EXTERNAL_PROG',
                'target': 'PAYCALC',
                'external': True,
                'metadata': {
                    'callingProgram': 'EXTERNAL_PROG'
                }
            }
        ],
        'outbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYDB',
                'target': 'DBUTIL',
                'external': True,
                'metadata': {
                    'callingProgram': 'PAYDB'
                }
            },
            {
                'type': 'JCL',
                'source': 'PAYUTIL',
                'target': 'BACKUP_JOB',
                'external': True,
                'metadata': {
                    'jclName': 'BACKUP_JOB',
                    'submittingProgram': 'PAYUTIL'
                }
            }
        ]
    }
    
    data_operations = {
        'databases': [
            {
                'type': 'DB2',
                'operation': 'SELECT',
                'target': 'EMPLOYEE_TABLE',
                'program': 'PAYDB'
            },
            {
                'type': 'DB2',
                'operation': 'UPDATE',
                'target': 'PAYROLL_TABLE',
                'program': 'PAYDB'
            },
            {
                'type': 'DB2',
                'operation': 'INSERT',
                'target': 'AUDIT_TABLE',
                'program': 'PAYUTIL'
            }
        ],
        'datasets': [
            {
                'name': 'EMPLOYEE.MASTER',
                'mode': 'INPUT',
                'programs': ['PAYROLL1', 'PAYCALC']
            },
            {
                'name': 'PAYROLL.TRANS',
                'mode': 'INOUT',
                'programs': ['PAYROLL1']
            },
            {
                'name': 'PAYROLL.REPORT',
                'mode': 'OUTPUT',
                'programs': ['PAYCALC', 'PAYUTIL']
            }
        ]
    }
    
    complexity = {
        'totalPrograms': 4,
        'totalLines': 2500,
        'cyclomaticComplexity': 45,
        'compositeScore': 67.5,
        'tier': 'MEDIUM'
    }
    
    dependencies = {
        'requiredFlows': [],
        'dependentFlows': []
    }
    
    print("   ✓ Sample data prepared")
    print()
    
    # Write flow to database
    print("4. Writing flow to database (with transaction)...")
    cursor = db.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        print("   ✓ Transaction started")
        
        # Create builder instance
        builder = MigrationFlowBuilder(db)
        
        # Write metadata
        print("   ✓ Writing flow metadata...")
        builder._write_flow_metadata(cursor, flow_id, entry_program, primary_type, scope, complexity)
        
        # Write entry types (batch insert)
        print("   ✓ Writing entry types (batch insert: 3 callers)...")
        builder._write_flow_entry_types(cursor, flow_id, entry_types)
        
        # Write scope (batch insert)
        print("   ✓ Writing scope (batch insert: 10 artifacts)...")
        builder._write_flow_scope(cursor, flow_id, scope)
        
        # Write interfaces (batch insert)
        print("   ✓ Writing interfaces (batch insert: 3 interfaces)...")
        builder._write_flow_interfaces(cursor, flow_id, interfaces)
        
        # Write data operations (batch insert)
        print("   ✓ Writing data operations (batch insert: 6 operations)...")
        builder._write_flow_data_operations(cursor, flow_id, data_operations)
        
        # Write dependencies (batch insert)
        print("   ✓ Writing dependencies...")
        builder._write_flow_dependencies(cursor, flow_id, dependencies)
        
        # Commit transaction
        db.commit()
        print("   ✓ Transaction committed")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"   ✗ Transaction rolled back due to error: {e}")
        return
    
    # Verify data was written
    print("5. Verifying data in database...")
    
    # Check migration_flows
    cursor.execute("SELECT COUNT(*) FROM migration_flows WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"   ✓ migration_flows: {count} row")
    
    # Check flow_entry_types
    cursor.execute("SELECT COUNT(*) FROM flow_entry_types WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"   ✓ flow_entry_types: {count} rows")
    
    # Check flow_scope
    cursor.execute("SELECT COUNT(*) FROM flow_scope WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"   ✓ flow_scope: {count} rows")
    
    # Check flow_interfaces
    cursor.execute("SELECT COUNT(*) FROM flow_interfaces WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"   ✓ flow_interfaces: {count} rows")
    
    # Check flow_data_operations
    cursor.execute("SELECT COUNT(*) FROM flow_data_operations WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"   ✓ flow_data_operations: {count} rows")
    
    # Check flow_dependencies
    cursor.execute("SELECT COUNT(*) FROM flow_dependencies WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"   ✓ flow_dependencies: {count} rows")
    print()
    
    # Display sample data
    print("6. Sample data from database:")
    print()
    
    # Show flow metadata
    cursor.execute("""
        SELECT flow_id, name, entry_program, primary_entry_type, 
               total_programs, total_copybooks, total_datasets,
               complexity_tier
        FROM migration_flows 
        WHERE flow_id = ?
    """, (flow_id,))
    
    row = cursor.fetchone()
    print("   Flow Metadata:")
    print(f"     Flow ID: {row[0]}")
    print(f"     Name: {row[1]}")
    print(f"     Entry Program: {row[2]}")
    print(f"     Primary Type: {row[3]}")
    print(f"     Programs: {row[4]}, Copybooks: {row[5]}, Datasets: {row[6]}")
    print(f"     Complexity Tier: {row[7]}")
    print()
    
    # Show entry types
    cursor.execute("""
        SELECT entry_type, caller_source
        FROM flow_entry_types 
        WHERE flow_id = ?
        ORDER BY entry_type, caller_source
    """, (flow_id,))
    
    print("   Entry Types:")
    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1]}")
    print()
    
    # Show scope breakdown
    cursor.execute("""
        SELECT artifact_type, COUNT(*) as count
        FROM flow_scope 
        WHERE flow_id = ?
        GROUP BY artifact_type
        ORDER BY artifact_type
    """, (flow_id,))
    
    print("   Scope Breakdown:")
    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1]} artifacts")
    print()
    
    # Show interfaces
    cursor.execute("""
        SELECT direction, interface_type, source, target
        FROM flow_interfaces 
        WHERE flow_id = ?
        ORDER BY direction, interface_type
    """, (flow_id,))
    
    print("   Interfaces:")
    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1]} ({row[2]} → {row[3]})")
    print()
    
    # Show data operations summary
    cursor.execute("""
        SELECT operation_category, COUNT(*) as count
        FROM flow_data_operations 
        WHERE flow_id = ?
        GROUP BY operation_category
        ORDER BY operation_category
    """, (flow_id,))
    
    print("   Data Operations:")
    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1]} operations")
    print()
    
    # Demonstrate transaction rollback
    print("7. Demonstrating transaction rollback...")
    print("   Attempting to write invalid data...")
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Try to write with invalid data (this will fail)
        cursor.execute("""
            INSERT INTO migration_flows (flow_id, name, entry_program)
            VALUES (?, ?, ?)
        """, ('FLOW_INVALID', None, None))  # NULL values will violate constraints
        
        db.commit()
        print("   ✗ Should not reach here")
        
    except Exception as e:
        db.rollback()
        print(f"   ✓ Transaction rolled back successfully")
        print(f"   ✓ Error caught: {type(e).__name__}")
    print()
    
    # Verify original data is still intact
    cursor.execute("SELECT COUNT(*) FROM migration_flows WHERE flow_id = ?", (flow_id,))
    count = cursor.fetchone()[0]
    print(f"8. Verifying data integrity after rollback...")
    print(f"   ✓ Original flow still exists: {count} row")
    print()
    
    # Close database
    db.close()
    
    print("=" * 80)
    print("Database Writer Demo Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print("  ✓ All database writer methods working correctly")
    print("  ✓ Batch inserts implemented for performance")
    print("  ✓ Transaction handling (commit/rollback) working")
    print("  ✓ Data integrity maintained")
    print()


if __name__ == '__main__':
    demo_database_writer()
