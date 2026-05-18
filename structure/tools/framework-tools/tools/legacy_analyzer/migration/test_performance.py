"""
Performance Tests for Migration Flow Export

This module contains performance tests to ensure the migration flow export
system meets performance requirements.
"""

import time
import sqlite3
import tempfile
import os
from typing import List, Dict

# Test performance requirements
PERFORMANCE_REQUIREMENTS = {
    'export_1000_flows': 60.0,  # Export 1000 flows in < 60 seconds
    'single_flow_query': 0.1,   # Query single flow in < 100ms
    'batch_insert_100': 5.0,    # Insert 100 flows in < 5 seconds
    'filter_query': 1.0,        # Filter query in < 1 second
    'cache_hit_rate': 0.8       # Cache hit rate > 80% for repeated queries
}


def create_test_database() -> sqlite3.Connection:
    """Create a test database with schema."""
    # Create temporary database
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = db_file.name
    db_file.close()
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Create schema (simplified for testing)
    cursor.execute("""
        CREATE TABLE migration_flows (
            flow_id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(200),
            entry_program VARCHAR(44),
            primary_entry_type VARCHAR(20),
            total_programs INTEGER,
            total_copybooks INTEGER,
            total_datasets INTEGER,
            complexity_total_lines INTEGER,
            complexity_cyclomatic INTEGER,
            complexity_score DECIMAL(10,2),
            complexity_tier VARCHAR(10),
            priority INTEGER,
            business_domain VARCHAR(100),
            created_date DATE,
            updated_date DATE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_entry_types (
            flow_id VARCHAR(100),
            entry_type VARCHAR(20),
            caller_source VARCHAR(100),
            metadata_json TEXT,
            PRIMARY KEY (flow_id, entry_type, caller_source),
            FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_scope (
            flow_id VARCHAR(100),
            artifact_type VARCHAR(20),
            artifact_name VARCHAR(44),
            PRIMARY KEY (flow_id, artifact_type, artifact_name),
            FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flow_id VARCHAR(100),
            direction VARCHAR(10),
            interface_type VARCHAR(20),
            source VARCHAR(44),
            target VARCHAR(44),
            external BOOLEAN DEFAULT FALSE,
            metadata_json TEXT,
            FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_data_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flow_id VARCHAR(100),
            operation_category VARCHAR(20),
            operation_type VARCHAR(20),
            db_type VARCHAR(20),
            target VARCHAR(100),
            program VARCHAR(44),
            mode VARCHAR(10),
            FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_dependencies (
            flow_id VARCHAR(100),
            depends_on_flow_id VARCHAR(100),
            dependency_type VARCHAR(20),
            PRIMARY KEY (flow_id, depends_on_flow_id, dependency_type),
            FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE,
            FOREIGN KEY (depends_on_flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
        )
    """)
    
    db.commit()
    return db


def generate_test_flows(count: int) -> List[Dict]:
    """Generate test flow data."""
    flows = []
    
    for i in range(count):
        flow_id = f"FLOW_TEST_{i:05d}"
        
        flow = {
            'flowId': flow_id,
            'name': f"Test Flow {i}",
            'entryPoint': {
                'program': f"PROG{i:05d}",
                'types': [
                    {
                        'type': 'JCL',
                        'callers': [
                            {'source': f"JCL{i:05d}", 'metadata': {}}
                        ]
                    }
                ],
                'primaryType': 'JCL'
            },
            'scope': {
                'programs': [f"PROG{i:05d}", f"SUB{i:05d}"],
                'copybooks': [f"COPY{i:05d}"],
                'datasets': [f"DATA{i:05d}"]
            },
            'interfaces': {
                'inbound': [],
                'outbound': []
            },
            'dataOperations': {
                'databases': [],
                'datasets': [
                    {
                        'name': f"DATA{i:05d}",
                        'mode': 'INPUT',
                        'programs': [f"PROG{i:05d}"]
                    }
                ]
            },
            'complexity': {
                'totalPrograms': 2,
                'totalLines': 1000 + (i % 5000),
                'cyclomaticComplexity': 50 + (i % 200),
                'compositeScore': 25.0 + (i % 75),
                'tier': ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'][i % 4]
            },
            'dependencies': {
                'requiredFlows': [],
                'dependentFlows': []
            }
        }
        
        # Add business domain for some flows
        if i % 3 == 0:
            flow['businessDomain'] = ['Finance', 'HR', 'Operations'][i % 3]
        
        # Add priority for some flows
        if i % 2 == 0:
            flow['priority'] = (i % 5) + 1
        
        flows.append(flow)
    
    return flows


def test_export_1000_flows_performance():
    """
    Test: Export 1000 flows in < 60 seconds
    
    This test verifies that the system can export 1000 flows
    within the required time limit.
    """
    print("\n" + "=" * 80)
    print("TEST: Export 1000 Flows Performance")
    print("=" * 80)
    
    # Create test database
    db = create_test_database()
    
    # Import required modules
    from .batch_operations import BatchDatabaseOperations
    from .flow_exporter import MigrationFlowExporter
    
    # Generate and insert test data
    print("Generating 1000 test flows...")
    flows = generate_test_flows(1000)
    
    print("Inserting test flows...")
    batch_ops = BatchDatabaseOperations(db, batch_size=100)
    insert_start = time.time()
    batch_ops.batch_insert_flows(flows)
    insert_time = time.time() - insert_start
    print(f"  Insert time: {insert_time:.2f}s")
    
    # Test export performance
    print("\nExporting 1000 flows...")
    exporter = MigrationFlowExporter(db)
    
    export_start = time.time()
    result = exporter.export_all_flows()
    export_time = time.time() - export_start
    
    print(f"  Export time: {export_time:.2f}s")
    print(f"  Flows exported: {len(result['flows'])}")
    print(f"  Average time per flow: {export_time / 1000:.4f}s")
    
    # Check performance requirement
    requirement = PERFORMANCE_REQUIREMENTS['export_1000_flows']
    passed = export_time < requirement
    
    print(f"\n  Requirement: < {requirement}s")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    
    # Cleanup
    db.close()
    os.unlink(db.connection.execute("PRAGMA database_list").fetchone()[2])
    
    assert passed, f"Export took {export_time:.2f}s, requirement is < {requirement}s"
    
    return export_time


def test_single_flow_query_performance():
    """
    Test: Query single flow in < 100ms
    
    This test verifies that querying a single flow is fast enough
    for interactive use.
    """
    print("\n" + "=" * 80)
    print("TEST: Single Flow Query Performance")
    print("=" * 80)
    
    # Create test database with 100 flows
    db = create_test_database()
    
    from .batch_operations import BatchDatabaseOperations
    from .flow_exporter import MigrationFlowExporter
    
    flows = generate_test_flows(100)
    batch_ops = BatchDatabaseOperations(db)
    batch_ops.batch_insert_flows(flows)
    
    # Test single flow query
    exporter = MigrationFlowExporter(db)
    flow_id = flows[50]['flowId']
    
    # Warm up
    exporter._query_flow(flow_id)
    
    # Measure query time
    query_times = []
    for _ in range(10):
        start = time.time()
        result = exporter._query_flow(flow_id)
        query_time = time.time() - start
        query_times.append(query_time)
    
    avg_time = sum(query_times) / len(query_times)
    min_time = min(query_times)
    max_time = max(query_times)
    
    print(f"  Average query time: {avg_time * 1000:.2f}ms")
    print(f"  Min query time: {min_time * 1000:.2f}ms")
    print(f"  Max query time: {max_time * 1000:.2f}ms")
    
    # Check performance requirement
    requirement = PERFORMANCE_REQUIREMENTS['single_flow_query']
    passed = avg_time < requirement
    
    print(f"\n  Requirement: < {requirement * 1000:.0f}ms")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    
    # Cleanup
    db.close()
    
    assert passed, f"Query took {avg_time * 1000:.2f}ms, requirement is < {requirement * 1000:.0f}ms"
    
    return avg_time


def test_batch_insert_performance():
    """
    Test: Insert 100 flows in < 5 seconds
    
    This test verifies that batch insert operations are efficient.
    """
    print("\n" + "=" * 80)
    print("TEST: Batch Insert Performance")
    print("=" * 80)
    
    # Create test database
    db = create_test_database()
    
    from .batch_operations import BatchDatabaseOperations
    
    # Generate test data
    flows = generate_test_flows(100)
    
    # Test batch insert
    batch_ops = BatchDatabaseOperations(db, batch_size=50)
    
    start = time.time()
    count = batch_ops.batch_insert_flows(flows)
    insert_time = time.time() - start
    
    print(f"  Flows inserted: {count}")
    print(f"  Insert time: {insert_time:.2f}s")
    print(f"  Average time per flow: {insert_time / count:.4f}s")
    
    # Check performance requirement
    requirement = PERFORMANCE_REQUIREMENTS['batch_insert_100']
    passed = insert_time < requirement
    
    print(f"\n  Requirement: < {requirement}s")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    
    # Cleanup
    db.close()
    
    assert passed, f"Insert took {insert_time:.2f}s, requirement is < {requirement}s"
    
    return insert_time


def test_filter_query_performance():
    """
    Test: Filter query in < 1 second
    
    This test verifies that filtering operations are efficient.
    """
    print("\n" + "=" * 80)
    print("TEST: Filter Query Performance")
    print("=" * 80)
    
    # Create test database with 500 flows
    db = create_test_database()
    
    from .batch_operations import BatchDatabaseOperations
    from .flow_exporter import MigrationFlowExporter
    
    flows = generate_test_flows(500)
    batch_ops = BatchDatabaseOperations(db)
    batch_ops.batch_insert_flows(flows)
    
    # Test filter queries
    exporter = MigrationFlowExporter(db)
    
    # Test complexity filter
    start = time.time()
    high_complexity = exporter.filter_by_complexity('HIGH')
    complexity_time = time.time() - start
    
    print(f"  Complexity filter time: {complexity_time * 1000:.2f}ms")
    print(f"  Flows found: {len(high_complexity)}")
    
    # Test business domain filter
    start = time.time()
    finance_flows = exporter.filter_by_business_domain('Finance')
    domain_time = time.time() - start
    
    print(f"  Domain filter time: {domain_time * 1000:.2f}ms")
    print(f"  Flows found: {len(finance_flows)}")
    
    # Test combined filters
    start = time.time()
    combined = exporter.apply_combined_filters(
        min_complexity='MEDIUM',
        business_domain='Finance'
    )
    combined_time = time.time() - start
    
    print(f"  Combined filter time: {combined_time * 1000:.2f}ms")
    print(f"  Flows found: {len(combined)}")
    
    # Check performance requirement
    max_time = max(complexity_time, domain_time, combined_time)
    requirement = PERFORMANCE_REQUIREMENTS['filter_query']
    passed = max_time < requirement
    
    print(f"\n  Requirement: < {requirement}s")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    
    # Cleanup
    db.close()
    
    assert passed, f"Filter took {max_time:.2f}s, requirement is < {requirement}s"
    
    return max_time


def test_cache_performance():
    """
    Test: Cache hit rate > 80% for repeated queries
    
    This test verifies that caching is effective for repeated queries.
    """
    print("\n" + "=" * 80)
    print("TEST: Cache Performance")
    print("=" * 80)
    
    # Create test database
    db = create_test_database()
    
    from .batch_operations import BatchDatabaseOperations
    from .flow_exporter import MigrationFlowExporter
    from .flow_cache import FlowCache
    
    flows = generate_test_flows(100)
    batch_ops = BatchDatabaseOperations(db)
    batch_ops.batch_insert_flows(flows)
    
    # Create cache
    cache = FlowCache(max_size=50, ttl_seconds=3600)
    
    # Simulate repeated queries
    flow_ids = [f['flowId'] for f in flows[:20]]
    
    # First pass: populate cache
    exporter = MigrationFlowExporter(db)
    for flow_id in flow_ids:
        flow_data = exporter._query_flow(flow_id)
        cache.put_flow(flow_id, flow_data)
    
    # Second pass: test cache hits
    for _ in range(5):  # Repeat 5 times
        for flow_id in flow_ids:
            cached = cache.get_flow(flow_id)
            if cached is None:
                flow_data = exporter._query_flow(flow_id)
                cache.put_flow(flow_id, flow_data)
    
    # Get cache statistics
    stats = cache.get_stats()
    
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.1%}")
    print(f"  Cache size: {stats['size']}/{stats['max_size']}")
    
    # Check performance requirement
    requirement = PERFORMANCE_REQUIREMENTS['cache_hit_rate']
    passed = stats['hit_rate'] >= requirement
    
    print(f"\n  Requirement: > {requirement:.0%}")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    
    # Cleanup
    db.close()
    
    assert passed, f"Hit rate {stats['hit_rate']:.1%}, requirement is > {requirement:.0%}"
    
    return stats['hit_rate']


def run_all_performance_tests():
    """Run all performance tests and generate report."""
    print("\n" + "=" * 80)
    print("MIGRATION FLOW EXPORT - PERFORMANCE TEST SUITE")
    print("=" * 80)
    
    results = {}
    
    try:
        results['export_1000_flows'] = test_export_1000_flows_performance()
    except AssertionError as e:
        results['export_1000_flows'] = f"FAILED: {e}"
    
    try:
        results['single_flow_query'] = test_single_flow_query_performance()
    except AssertionError as e:
        results['single_flow_query'] = f"FAILED: {e}"
    
    try:
        results['batch_insert'] = test_batch_insert_performance()
    except AssertionError as e:
        results['batch_insert'] = f"FAILED: {e}"
    
    try:
        results['filter_query'] = test_filter_query_performance()
    except AssertionError as e:
        results['filter_query'] = f"FAILED: {e}"
    
    try:
        results['cache'] = test_cache_performance()
    except AssertionError as e:
        results['cache'] = f"FAILED: {e}"
    
    # Print summary
    print("\n" + "=" * 80)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        if isinstance(result, str) and result.startswith('FAILED'):
            print(f"  {test_name}: FAIL")
            failed += 1
        else:
            print(f"  {test_name}: PASS")
            passed += 1
    
    print(f"\n  Total: {passed + failed}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("=" * 80 + "\n")
    
    return passed, failed


if __name__ == '__main__':
    run_all_performance_tests()
