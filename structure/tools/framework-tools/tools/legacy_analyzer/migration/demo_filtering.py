"""
Demo: Migration Flow Filtering

This script demonstrates the filtering capabilities of the MigrationFlowExporter.
It shows how to filter flows by:
- Flow IDs
- Complexity tier
- Business domain
- Entry type
- Combined filters
"""

import sqlite3
import json
from tools.legacy_analyzer.migration.flow_exporter import MigrationFlowExporter


def create_demo_database():
    """Create a demo database with sample flows."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables
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
            PRIMARY KEY (flow_id, entry_type, caller_source)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_scope (
            flow_id VARCHAR(100),
            artifact_type VARCHAR(20),
            artifact_name VARCHAR(44),
            PRIMARY KEY (flow_id, artifact_type, artifact_name)
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
            metadata_json TEXT
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
            mode VARCHAR(10)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE flow_dependencies (
            flow_id VARCHAR(100),
            depends_on_flow_id VARCHAR(100),
            dependency_type VARCHAR(20),
            PRIMARY KEY (flow_id, depends_on_flow_id, dependency_type)
        )
    """)
    
    # Insert sample flows
    flows = [
        ('FLOW_PAYROLL1', 'Payroll Processing', 'PAYROLL1', 'JCL', 5, 3, 2, 2500, 45, 67.5, 'MEDIUM', 1, 'Finance'),
        ('FLOW_BILLING1', 'Billing System', 'BILLING1', 'CICS_TRANSACTION', 8, 5, 4, 5000, 120, 150.0, 'HIGH', 2, 'Finance'),
        ('FLOW_ACCT1', 'Accounting', 'ACCT1', 'JCL', 12, 8, 6, 8000, 200, 250.0, 'VERY_HIGH', 1, 'Finance'),
        ('FLOW_EMPLOYEE1', 'Employee Management', 'EMPLOYEE1', 'CICS_TRANSACTION', 6, 4, 3, 3500, 80, 95.0, 'MEDIUM', 3, 'HR'),
        ('FLOW_TIMECARD1', 'Timecard Processing', 'TIMECARD1', 'JCL', 3, 2, 2, 1500, 25, 35.0, 'LOW', 4, 'HR'),
        ('FLOW_BACKUP1', 'Backup System', 'BACKUP1', 'JCL', 2, 1, 1, 800, 15, 20.0, 'LOW', 5, 'Operations'),
        ('FLOW_MONITOR1', 'System Monitor', 'MONITOR1', 'CICS_PROGRAM', 4, 2, 2, 2000, 40, 55.0, 'MEDIUM', 4, 'Operations'),
    ]
    
    for flow in flows:
        cursor.execute("""
            INSERT INTO migration_flows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)
        """, flow)
    
    # Insert entry types
    entry_types = [
        ('FLOW_PAYROLL1', 'JCL', 'PAYROLL01', None),
        ('FLOW_PAYROLL1', 'JCL', 'PAYWEEK', None),
        ('FLOW_BILLING1', 'CICS_TRANSACTION', 'BILL', None),
        ('FLOW_BILLING1', 'CICS_PROGRAM', 'BILLING1', None),
        ('FLOW_ACCT1', 'JCL', 'ACCTJOB', None),
        ('FLOW_EMPLOYEE1', 'CICS_TRANSACTION', 'EMP1', None),
        ('FLOW_TIMECARD1', 'JCL', 'TIMEJOB', None),
        ('FLOW_BACKUP1', 'JCL', 'BACKUP', None),
        ('FLOW_MONITOR1', 'CICS_PROGRAM', 'MONITOR1', None),
    ]
    
    for entry in entry_types:
        cursor.execute("""
            INSERT INTO flow_entry_types VALUES (?, ?, ?, ?)
        """, entry)
    
    # Insert minimal scope data
    for flow_id, _, entry_program, _, _, _, _, _, _, _, _, _, _ in flows:
        cursor.execute("""
            INSERT INTO flow_scope VALUES (?, 'PROGRAM', ?)
        """, (flow_id, entry_program))
    
    conn.commit()
    return conn


def demo_filter_by_flow_ids(exporter):
    """Demo: Filter by specific flow IDs."""
    print("\n" + "="*70)
    print("DEMO 1: Filter by Flow IDs")
    print("="*70)
    
    flow_ids = ['FLOW_PAYROLL1', 'FLOW_BILLING1', 'FLOW_INVALID']
    print(f"\nRequested flow IDs: {flow_ids}")
    
    result = exporter.filter_by_flow_ids(flow_ids)
    print(f"Valid flow IDs found: {result}")
    print(f"Count: {len(result)}")


def demo_filter_by_complexity(exporter):
    """Demo: Filter by complexity tier."""
    print("\n" + "="*70)
    print("DEMO 2: Filter by Complexity Tier")
    print("="*70)
    
    for tier in ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']:
        result = exporter.filter_by_complexity(tier)
        print(f"\n{tier} and above: {len(result)} flows")
        print(f"  Flow IDs: {result}")


def demo_filter_by_business_domain(exporter):
    """Demo: Filter by business domain."""
    print("\n" + "="*70)
    print("DEMO 3: Filter by Business Domain")
    print("="*70)
    
    for domain in ['Finance', 'HR', 'Operations']:
        result = exporter.filter_by_business_domain(domain)
        print(f"\n{domain}: {len(result)} flows")
        print(f"  Flow IDs: {result}")


def demo_filter_by_entry_type(exporter):
    """Demo: Filter by entry type."""
    print("\n" + "="*70)
    print("DEMO 4: Filter by Entry Type")
    print("="*70)
    
    for entry_type in ['JCL', 'CICS_TRANSACTION', 'CICS_PROGRAM']:
        result = exporter.filter_by_entry_type(entry_type)
        print(f"\n{entry_type}: {len(result)} flows")
        print(f"  Flow IDs: {result}")


def demo_combined_filters(exporter):
    """Demo: Combined filters."""
    print("\n" + "="*70)
    print("DEMO 5: Combined Filters")
    print("="*70)
    
    # Example 1: High complexity Finance flows
    print("\n--- High complexity Finance flows ---")
    result = exporter.apply_combined_filters(
        min_complexity='HIGH',
        business_domain='Finance'
    )
    print(f"Found {len(result)} flows: {result}")
    
    # Example 2: Medium+ complexity JCL flows
    print("\n--- Medium+ complexity JCL flows ---")
    result = exporter.apply_combined_filters(
        min_complexity='MEDIUM',
        entry_type='JCL'
    )
    print(f"Found {len(result)} flows: {result}")
    
    # Example 3: All three filters
    print("\n--- High complexity Finance JCL flows ---")
    result = exporter.apply_combined_filters(
        min_complexity='HIGH',
        business_domain='Finance',
        entry_type='JCL'
    )
    print(f"Found {len(result)} flows: {result}")
    
    # Example 4: Specific flows with complexity filter
    print("\n--- Specific flows (HIGH complexity only) ---")
    result = exporter.apply_combined_filters(
        flow_ids=['FLOW_PAYROLL1', 'FLOW_BILLING1', 'FLOW_ACCT1'],
        min_complexity='HIGH'
    )
    print(f"Found {len(result)} flows: {result}")


def demo_export_with_filters(exporter):
    """Demo: Export flows with filters."""
    print("\n" + "="*70)
    print("DEMO 6: Export Flows with Filters")
    print("="*70)
    
    # Export high complexity flows
    print("\n--- Exporting HIGH complexity flows ---")
    result = exporter.export_all_flows(min_complexity='HIGH')
    print(f"Exported {len(result['flows'])} flows")
    
    for flow in result['flows']:
        print(f"  - {flow['flowId']}: {flow['name']} ({flow['complexity']['tier']})")
    
    # Export Finance flows
    print("\n--- Exporting Finance flows ---")
    result = exporter.export_all_flows(business_domain='Finance')
    print(f"Exported {len(result['flows'])} flows")
    
    for flow in result['flows']:
        print(f"  - {flow['flowId']}: {flow['name']} ({flow['businessDomain']})")
    
    # Export with combined filters
    print("\n--- Exporting MEDIUM+ complexity Finance JCL flows ---")
    result = exporter.export_all_flows(
        min_complexity='MEDIUM',
        business_domain='Finance',
        entry_type='JCL'
    )
    print(f"Exported {len(result['flows'])} flows")
    
    for flow in result['flows']:
        print(f"  - {flow['flowId']}: {flow['name']}")
        print(f"    Complexity: {flow['complexity']['tier']}")
        print(f"    Domain: {flow['businessDomain']}")
        entry_types = [et['type'] for et in flow['entryPoint']['types']]
        print(f"    Entry Types: {', '.join(entry_types)}")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("MIGRATION FLOW FILTERING DEMO")
    print("="*70)
    
    # Create demo database
    print("\nCreating demo database with 7 sample flows...")
    conn = create_demo_database()
    
    # Create exporter
    exporter = MigrationFlowExporter(conn)
    
    # Show all flows
    print(f"\nTotal flows in database: {exporter.get_flow_count()}")
    print(f"Flow IDs: {exporter.get_flow_ids()}")
    
    # Run demos
    demo_filter_by_flow_ids(exporter)
    demo_filter_by_complexity(exporter)
    demo_filter_by_business_domain(exporter)
    demo_filter_by_entry_type(exporter)
    demo_combined_filters(exporter)
    demo_export_with_filters(exporter)
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("1. Filter by flow IDs to export specific flows")
    print("2. Filter by complexity tier to focus on high-risk flows")
    print("3. Filter by business domain to organize by business area")
    print("4. Filter by entry type to group by invocation mechanism")
    print("5. Combine multiple filters for precise flow selection")
    print("6. All filters use AND logic (intersection)")
    
    conn.close()


if __name__ == '__main__':
    main()
