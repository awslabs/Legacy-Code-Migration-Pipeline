"""
Simple test script to verify migration flow schema.

This script creates an in-memory database and verifies that all tables
and indexes are created correctly.
"""

import sqlite3
from tools.legacy_analyzer.migration.schema import MigrationFlowSchema


def test_schema_creation():
    """Test that schema can be created successfully."""
    print("Testing migration flow schema creation...")
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    try:
        # Create schema
        schema = MigrationFlowSchema(conn)
        schema.create_schema(verbose=True)
        
        # Verify schema
        print("\nVerifying schema...")
        is_complete = schema.is_schema_complete()
        
        if is_complete:
            print("✓ Schema verification passed")
        else:
            missing = schema.get_missing_tables()
            print(f"✗ Schema verification failed. Missing tables: {', '.join(missing)}")
            return False
        
        # Get table counts (should all be 0 for empty database)
        print("\nTable counts:")
        counts = schema.get_table_counts()
        for table, count in counts.items():
            print(f"  {table}: {count}")
        
        # Test inserting sample data
        print("\nTesting sample data insertion...")
        cursor = conn.cursor()
        
        # Insert a sample flow
        cursor.execute("""
            INSERT INTO migration_flows (
                flow_id, name, entry_program, primary_entry_type,
                total_programs, complexity_tier
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, ('FLOW_TEST01', 'Test Flow', 'TEST01', 'JCL', 3, 'MEDIUM'))
        
        # Insert entry types
        cursor.execute("""
            INSERT INTO flow_entry_types (
                flow_id, entry_type, caller_source
            ) VALUES (?, ?, ?)
        """, ('FLOW_TEST01', 'JCL', 'TESTJOB'))
        
        # Insert scope
        cursor.execute("""
            INSERT INTO flow_scope (
                flow_id, artifact_type, artifact_name
            ) VALUES (?, ?, ?)
        """, ('FLOW_TEST01', 'PROGRAM', 'TEST01'))
        
        conn.commit()
        
        # Verify data was inserted
        cursor.execute("SELECT COUNT(*) FROM migration_flows")
        flow_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_entry_types")
        entry_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_scope")
        scope_count = cursor.fetchone()[0]
        
        print(f"  migration_flows: {flow_count} row(s)")
        print(f"  flow_entry_types: {entry_count} row(s)")
        print(f"  flow_scope: {scope_count} row(s)")
        
        if flow_count == 1 and entry_count == 1 and scope_count == 1:
            print("✓ Sample data insertion successful")
        else:
            print("✗ Sample data insertion failed")
            return False
        
        # Test foreign key constraints
        print("\nTesting foreign key constraints...")
        try:
            cursor.execute("""
                INSERT INTO flow_entry_types (
                    flow_id, entry_type, caller_source
                ) VALUES (?, ?, ?)
            """, ('FLOW_NONEXISTENT', 'JCL', 'TEST'))
            conn.commit()
            print("⚠ Foreign key constraint not enforced (expected for SQLite without PRAGMA)")
        except sqlite3.IntegrityError:
            print("✓ Foreign key constraint working")
        
        print("\n✓ All schema tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    success = test_schema_creation()
    sys.exit(0 if success else 1)
