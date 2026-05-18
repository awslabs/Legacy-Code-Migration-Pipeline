"""
Integration test for migration flow schema with database setup.

This test verifies that the migration flow schema integrates properly
with the existing database setup utilities.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.legacy_analyzer.migration.schema import MigrationFlowSchema
from tools.legacy_analyzer.database_setup import DatabaseSetup


def test_standalone_schema():
    """Test creating migration flow schema standalone."""
    print("=" * 60)
    print("Test 1: Standalone Migration Flow Schema")
    print("=" * 60)
    
    conn = sqlite3.connect(':memory:')
    
    try:
        schema = MigrationFlowSchema(conn)
        schema.create_schema(verbose=True)
        
        if schema.is_schema_complete():
            print("\n✓ Standalone schema test passed")
            return True
        else:
            print("\n✗ Standalone schema test failed")
            return False
    finally:
        conn.close()


def test_integrated_schema():
    """Test creating migration flow schema via DatabaseSetup."""
    print("\n" + "=" * 60)
    print("Test 2: Integrated Migration Flow Schema")
    print("=" * 60)
    
    conn = sqlite3.connect(':memory:')
    
    try:
        setup = DatabaseSetup(conn)
        setup.create_all_tables(verbose=True, include_migration_flows=True)
        
        # Verify migration flow tables exist
        schema = MigrationFlowSchema(conn)
        if schema.is_schema_complete():
            print("\n✓ Integrated schema test passed")
            return True
        else:
            missing = schema.get_missing_tables()
            print(f"\n✗ Integrated schema test failed. Missing: {missing}")
            return False
    finally:
        conn.close()


def test_data_insertion():
    """Test inserting data into migration flow tables."""
    print("\n" + "=" * 60)
    print("Test 3: Data Insertion")
    print("=" * 60)
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    try:
        # Create schema
        schema = MigrationFlowSchema(conn)
        schema.create_schema(verbose=False)
        
        print("Inserting test data...")
        
        # Insert flow
        cursor.execute("""
            INSERT INTO migration_flows (
                flow_id, name, entry_program, primary_entry_type,
                total_programs, total_copybooks, total_datasets,
                complexity_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('FLOW_TEST01', 'Test Flow', 'TEST01', 'JCL', 3, 2, 1, 'MEDIUM'))
        
        # Insert multiple entry types
        cursor.execute("""
            INSERT INTO flow_entry_types (flow_id, entry_type, caller_source)
            VALUES (?, ?, ?)
        """, ('FLOW_TEST01', 'JCL', 'TESTJOB01'))
        
        cursor.execute("""
            INSERT INTO flow_entry_types (flow_id, entry_type, caller_source)
            VALUES (?, ?, ?)
        """, ('FLOW_TEST01', 'JCL', 'TESTJOB02'))
        
        cursor.execute("""
            INSERT INTO flow_entry_types (flow_id, entry_type, caller_source)
            VALUES (?, ?, ?)
        """, ('FLOW_TEST01', 'CICS_TRANSACTION', 'TST1'))
        
        # Insert scope
        for artifact_type, artifact_name in [
            ('PROGRAM', 'TEST01'),
            ('PROGRAM', 'TEST02'),
            ('PROGRAM', 'TEST03'),
            ('COPYBOOK', 'TESTCPY1'),
            ('COPYBOOK', 'TESTCPY2'),
            ('DATASET', 'TEST.DATA')
        ]:
            cursor.execute("""
                INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
                VALUES (?, ?, ?)
            """, ('FLOW_TEST01', artifact_type, artifact_name))
        
        # Insert interface
        cursor.execute("""
            INSERT INTO flow_interfaces (
                flow_id, direction, interface_type, source, target, external
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('FLOW_TEST01', 'OUTBOUND', 'PROGRAM_CALL', 'TEST03', 'EXTERNAL01', True))
        
        # Insert data operation
        cursor.execute("""
            INSERT INTO flow_data_operations (
                flow_id, operation_category, operation_type, target, program
            ) VALUES (?, ?, ?, ?, ?)
        """, ('FLOW_TEST01', 'DATABASE', 'SELECT', 'CUSTOMER_TABLE', 'TEST02'))
        
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM migration_flows")
        flow_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_entry_types")
        entry_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_scope")
        scope_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_interfaces")
        interface_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_data_operations")
        operation_count = cursor.fetchone()[0]
        
        print(f"  migration_flows: {flow_count}")
        print(f"  flow_entry_types: {entry_count}")
        print(f"  flow_scope: {scope_count}")
        print(f"  flow_interfaces: {interface_count}")
        print(f"  flow_data_operations: {operation_count}")
        
        if (flow_count == 1 and entry_count == 3 and scope_count == 6 and
            interface_count == 1 and operation_count == 1):
            print("\n✓ Data insertion test passed")
            return True
        else:
            print("\n✗ Data insertion test failed")
            return False
            
    finally:
        conn.close()


def test_query_performance():
    """Test query performance with indexes."""
    print("\n" + "=" * 60)
    print("Test 4: Query Performance")
    print("=" * 60)
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    try:
        # Create schema
        schema = MigrationFlowSchema(conn)
        schema.create_schema(verbose=False)
        
        print("Inserting 100 test flows...")
        
        # Insert 100 flows
        for i in range(100):
            flow_id = f"FLOW_TEST{i:03d}"
            cursor.execute("""
                INSERT INTO migration_flows (
                    flow_id, name, entry_program, primary_entry_type,
                    complexity_tier
                ) VALUES (?, ?, ?, ?, ?)
            """, (flow_id, f"Test Flow {i}", f"TEST{i:03d}", 'JCL', 'MEDIUM'))
            
            # Add entry types
            cursor.execute("""
                INSERT INTO flow_entry_types (flow_id, entry_type, caller_source)
                VALUES (?, ?, ?)
            """, (flow_id, 'JCL', f"JOB{i:03d}"))
            
            # Add scope
            cursor.execute("""
                INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
                VALUES (?, ?, ?)
            """, (flow_id, 'PROGRAM', f"TEST{i:03d}"))
        
        conn.commit()
        
        # Test queries
        print("Testing queries...")
        
        # Query by flow_id (indexed)
        cursor.execute("SELECT * FROM migration_flows WHERE flow_id = ?", ('FLOW_TEST050',))
        result = cursor.fetchone()
        assert result is not None, "Flow not found"
        
        # Query by complexity_tier (indexed)
        cursor.execute("SELECT COUNT(*) FROM migration_flows WHERE complexity_tier = ?", ('MEDIUM',))
        count = cursor.fetchone()[0]
        assert count == 100, f"Expected 100, got {count}"
        
        # Query entry types (indexed)
        cursor.execute("SELECT COUNT(*) FROM flow_entry_types WHERE entry_type = ?", ('JCL',))
        count = cursor.fetchone()[0]
        assert count == 100, f"Expected 100, got {count}"
        
        # Query scope (indexed)
        cursor.execute("SELECT COUNT(*) FROM flow_scope WHERE artifact_type = ?", ('PROGRAM',))
        count = cursor.fetchone()[0]
        assert count == 100, f"Expected 100, got {count}"
        
        print("  ✓ Query by flow_id")
        print("  ✓ Query by complexity_tier")
        print("  ✓ Query by entry_type")
        print("  ✓ Query by artifact_type")
        
        print("\n✓ Query performance test passed")
        return True
        
    finally:
        conn.close()


def main():
    """Run all integration tests."""
    print("\nMigration Flow Schema Integration Tests")
    print("=" * 60)
    
    tests = [
        test_standalone_schema,
        test_integrated_schema,
        test_data_insertion,
        test_query_performance
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
