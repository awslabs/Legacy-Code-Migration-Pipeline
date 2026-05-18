"""
Demo: Flow Dependencies Identification

This script demonstrates how to identify dependencies between migration flows.
It shows how to:
1. Identify required flows (flows that must be migrated first)
2. Identify dependent flows (flows that depend on this flow)
3. Handle circular dependencies
4. Use flow dependencies for migration planning
"""

import sqlite3
from tools.legacy_analyzer.migration.flow_builder import MigrationFlowBuilder


def setup_demo_database():
    """Create a demo database with sample flows and dependencies."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create migration_flows table
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
    
    # Create flow_scope table
    cursor.execute("""
        CREATE TABLE flow_scope (
            flow_id VARCHAR(100),
            artifact_type VARCHAR(20),
            artifact_name VARCHAR(44),
            PRIMARY KEY (flow_id, artifact_type, artifact_name),
            FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
        )
    """)
    
    # Insert sample flows
    flows = [
        ('FLOW_DATABASE_UTIL', 'Database Utility', 'DBUTIL', 'BATCH'),
        ('FLOW_LOGGER', 'Logging Utility', 'LOGGER', 'BATCH'),
        ('FLOW_PAYROLL', 'Payroll Processing', 'PAYROLL', 'JCL'),
        ('FLOW_BILLING', 'Billing System', 'BILLING', 'CICS_TRANSACTION'),
        ('FLOW_REPORTING', 'Report Generator', 'REPORT', 'JCL'),
    ]
    
    for flow_id, name, entry_prog, entry_type in flows:
        cursor.execute("""
            INSERT INTO migration_flows (flow_id, name, entry_program, primary_entry_type)
            VALUES (?, ?, ?, ?)
        """, (flow_id, name, entry_prog, entry_type))
        
        # Add entry program to scope
        cursor.execute("""
            INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
            VALUES (?, 'PROGRAM', ?)
        """, (flow_id, entry_prog))
    
    conn.commit()
    return conn


def demo_no_dependencies():
    """Demo: Flow with no dependencies."""
    print("=" * 70)
    print("Demo 1: Flow with No Dependencies")
    print("=" * 70)
    
    conn = setup_demo_database()
    builder = MigrationFlowBuilder(conn)
    
    # LOGGER has no dependencies
    flow_id = "FLOW_LOGGER"
    entry_program = "LOGGER"
    interfaces = {
        'inbound': [],
        'outbound': []
    }
    
    dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)
    
    print(f"\nFlow: {flow_id}")
    print(f"Entry Program: {entry_program}")
    print(f"\nRequired Flows: {dependencies['requiredFlows']}")
    print(f"Dependent Flows: {dependencies['dependentFlows']}")
    print("\nInterpretation:")
    print("  - This flow can be migrated independently")
    print("  - No other flows need to be migrated first")
    print("  - No other flows depend on this flow")
    
    conn.close()


def demo_required_flows():
    """Demo: Flow with required dependencies."""
    print("\n" + "=" * 70)
    print("Demo 2: Flow with Required Dependencies")
    print("=" * 70)
    
    conn = setup_demo_database()
    builder = MigrationFlowBuilder(conn)
    
    # PAYROLL depends on DBUTIL and LOGGER
    flow_id = "FLOW_PAYROLL"
    entry_program = "PAYROLL"
    interfaces = {
        'inbound': [],
        'outbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYROLL',
                'target': 'DBUTIL',  # Entry point of FLOW_DATABASE_UTIL
                'external': True,
                'metadata': {'callingProgram': 'PAYROLL'}
            },
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYROLL',
                'target': 'LOGGER',  # Entry point of FLOW_LOGGER
                'external': True,
                'metadata': {'callingProgram': 'PAYROLL'}
            }
        ]
    }
    
    dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)
    
    print(f"\nFlow: {flow_id}")
    print(f"Entry Program: {entry_program}")
    print(f"\nOutbound Interfaces:")
    for interface in interfaces['outbound']:
        print(f"  - {interface['source']} → {interface['target']} ({interface['type']})")
    
    print(f"\nRequired Flows: {dependencies['requiredFlows']}")
    print(f"Dependent Flows: {dependencies['dependentFlows']}")
    
    print("\nInterpretation:")
    print("  - This flow calls external programs that are entry points of other flows")
    print("  - Required flows must be migrated BEFORE this flow")
    print("  - Migration order: FLOW_DATABASE_UTIL, FLOW_LOGGER → FLOW_PAYROLL")
    
    conn.close()


def demo_dependent_flows():
    """Demo: Flow with dependent flows."""
    print("\n" + "=" * 70)
    print("Demo 3: Flow with Dependent Flows")
    print("=" * 70)
    
    conn = setup_demo_database()
    builder = MigrationFlowBuilder(conn)
    
    # DBUTIL is called by PAYROLL and BILLING
    flow_id = "FLOW_DATABASE_UTIL"
    entry_program = "DBUTIL"
    interfaces = {
        'inbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYROLL',  # From FLOW_PAYROLL
                'target': 'DBUTIL_SUB',  # Not the entry point
                'metadata': {'callingProgram': 'PAYROLL'}
            },
            {
                'type': 'PROGRAM_CALL',
                'source': 'BILLING',  # From FLOW_BILLING
                'target': 'DBUTIL_SUB',  # Not the entry point
                'metadata': {'callingProgram': 'BILLING'}
            }
        ],
        'outbound': []
    }
    
    dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)
    
    print(f"\nFlow: {flow_id}")
    print(f"Entry Program: {entry_program}")
    print(f"\nInbound Interfaces:")
    for interface in interfaces['inbound']:
        print(f"  - {interface['source']} → {interface['target']} ({interface['type']})")
    
    print(f"\nRequired Flows: {dependencies['requiredFlows']}")
    print(f"Dependent Flows: {dependencies['dependentFlows']}")
    
    print("\nInterpretation:")
    print("  - This flow is called by programs in other flows")
    print("  - Dependent flows can only be migrated AFTER this flow")
    print("  - Migration order: FLOW_DATABASE_UTIL → FLOW_PAYROLL, FLOW_BILLING")
    print("  - This is a shared utility used by multiple flows")
    
    conn.close()


def demo_circular_dependencies():
    """Demo: Circular dependencies between flows."""
    print("\n" + "=" * 70)
    print("Demo 4: Circular Dependencies")
    print("=" * 70)
    
    conn = setup_demo_database()
    cursor = conn.cursor()
    
    # BILLING is already added to scope in setup_demo_database()
    # No need to add it again
    
    builder = MigrationFlowBuilder(conn)
    
    # PAYROLL calls BILLING and is called by BILLING (circular)
    flow_id = "FLOW_PAYROLL"
    entry_program = "PAYROLL"
    interfaces = {
        'inbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'BILLING',  # From FLOW_BILLING
                'target': 'PAYROLL_SUB',
                'metadata': {'callingProgram': 'BILLING'}
            }
        ],
        'outbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYROLL',
                'target': 'BILLING',  # Entry point of FLOW_BILLING
                'external': True,
                'metadata': {'callingProgram': 'PAYROLL'}
            }
        ]
    }
    
    dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)
    
    print(f"\nFlow: {flow_id}")
    print(f"Entry Program: {entry_program}")
    print(f"\nInterfaces:")
    print("  Inbound:")
    for interface in interfaces['inbound']:
        print(f"    - {interface['source']} → {interface['target']}")
    print("  Outbound:")
    for interface in interfaces['outbound']:
        print(f"    - {interface['source']} → {interface['target']}")
    
    print(f"\nRequired Flows: {dependencies['requiredFlows']}")
    print(f"Dependent Flows: {dependencies['dependentFlows']}")
    
    # Check for circular dependencies
    circular = set(dependencies['requiredFlows']) & set(dependencies['dependentFlows'])
    if circular:
        print(f"\n⚠️  CIRCULAR DEPENDENCY DETECTED: {circular}")
    
    print("\nInterpretation:")
    print("  - FLOW_PAYROLL and FLOW_BILLING depend on each other")
    print("  - These flows must be migrated together as a unit")
    print("  - Consider refactoring to break the circular dependency")
    print("  - Or migrate both flows in the same migration wave")
    
    conn.close()


def demo_complex_dependency_graph():
    """Demo: Complex dependency graph with multiple levels."""
    print("\n" + "=" * 70)
    print("Demo 5: Complex Dependency Graph")
    print("=" * 70)
    
    conn = setup_demo_database()
    # Programs are already added to scopes in setup_demo_database()
    
    builder = MigrationFlowBuilder(conn)
    
    # Analyze each flow
    flows_analysis = []
    
    # 1. DBUTIL (no dependencies)
    deps1 = builder.identify_flow_dependencies(
        "FLOW_DATABASE_UTIL", "DBUTIL",
        {'inbound': [], 'outbound': []}
    )
    flows_analysis.append(("FLOW_DATABASE_UTIL", deps1))
    
    # 2. LOGGER (no dependencies)
    deps2 = builder.identify_flow_dependencies(
        "FLOW_LOGGER", "LOGGER",
        {'inbound': [], 'outbound': []}
    )
    flows_analysis.append(("FLOW_LOGGER", deps2))
    
    # 3. PAYROLL (depends on DBUTIL and LOGGER)
    deps3 = builder.identify_flow_dependencies(
        "FLOW_PAYROLL", "PAYROLL",
        {
            'inbound': [],
            'outbound': [
                {'type': 'PROGRAM_CALL', 'source': 'PAYROLL', 'target': 'DBUTIL', 'external': True},
                {'type': 'PROGRAM_CALL', 'source': 'PAYROLL', 'target': 'LOGGER', 'external': True}
            ]
        }
    )
    flows_analysis.append(("FLOW_PAYROLL", deps3))
    
    # 4. BILLING (depends on DBUTIL and LOGGER)
    deps4 = builder.identify_flow_dependencies(
        "FLOW_BILLING", "BILLING",
        {
            'inbound': [],
            'outbound': [
                {'type': 'PROGRAM_CALL', 'source': 'BILLING', 'target': 'DBUTIL', 'external': True},
                {'type': 'PROGRAM_CALL', 'source': 'BILLING', 'target': 'LOGGER', 'external': True}
            ]
        }
    )
    flows_analysis.append(("FLOW_BILLING", deps4))
    
    # 5. REPORTING (depends on PAYROLL and BILLING)
    deps5 = builder.identify_flow_dependencies(
        "FLOW_REPORTING", "REPORT",
        {
            'inbound': [],
            'outbound': [
                {'type': 'PROGRAM_CALL', 'source': 'REPORT', 'target': 'PAYROLL', 'external': True},
                {'type': 'PROGRAM_CALL', 'source': 'REPORT', 'target': 'BILLING', 'external': True}
            ]
        }
    )
    flows_analysis.append(("FLOW_REPORTING", deps5))
    
    # Display dependency graph
    print("\nDependency Graph:")
    print("-" * 70)
    for flow_id, deps in flows_analysis:
        print(f"\n{flow_id}:")
        if deps['requiredFlows']:
            print(f"  Requires: {', '.join(deps['requiredFlows'])}")
        else:
            print(f"  Requires: (none)")
        if deps['dependentFlows']:
            print(f"  Depended on by: {', '.join(deps['dependentFlows'])}")
        else:
            print(f"  Depended on by: (none)")
    
    # Calculate migration waves
    print("\n" + "=" * 70)
    print("Migration Wave Planning:")
    print("=" * 70)
    
    print("\nWave 1 (Foundation - no dependencies):")
    print("  - FLOW_DATABASE_UTIL")
    print("  - FLOW_LOGGER")
    
    print("\nWave 2 (Core Applications - depend on Wave 1):")
    print("  - FLOW_PAYROLL")
    print("  - FLOW_BILLING")
    
    print("\nWave 3 (Reporting - depends on Wave 2):")
    print("  - FLOW_REPORTING")
    
    print("\nMigration Strategy:")
    print("  1. Migrate utilities first (DBUTIL, LOGGER)")
    print("  2. Migrate core applications in parallel (PAYROLL, BILLING)")
    print("  3. Migrate reporting last (REPORTING)")
    print("  4. Total waves: 3")
    print("  5. Parallel opportunities: Wave 1 (2 flows), Wave 2 (2 flows)")
    
    conn.close()


def demo_migration_planning():
    """Demo: Using flow dependencies for migration planning."""
    print("\n" + "=" * 70)
    print("Demo 6: Migration Planning with Dependencies")
    print("=" * 70)
    
    conn = setup_demo_database()
    builder = MigrationFlowBuilder(conn)
    
    # Sample flow with dependencies
    flow_id = "FLOW_PAYROLL"
    entry_program = "PAYROLL"
    interfaces = {
        'inbound': [],
        'outbound': [
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYROLL',
                'target': 'DBUTIL',
                'external': True
            },
            {
                'type': 'PROGRAM_CALL',
                'source': 'PAYROLL',
                'target': 'LOGGER',
                'external': True
            }
        ]
    }
    
    dependencies = builder.identify_flow_dependencies(flow_id, entry_program, interfaces)
    
    print(f"\nPlanning Migration for: {flow_id}")
    print("-" * 70)
    
    print("\n1. Pre-Migration Checklist:")
    if dependencies['requiredFlows']:
        print(f"   ✓ Ensure these flows are migrated first:")
        for req_flow in dependencies['requiredFlows']:
            print(f"     - {req_flow}")
    else:
        print("   ✓ No prerequisite flows (can migrate independently)")
    
    print("\n2. Migration Impact Analysis:")
    if dependencies['dependentFlows']:
        print(f"   ⚠️  These flows will be affected:")
        for dep_flow in dependencies['dependentFlows']:
            print(f"     - {dep_flow}")
        print("   → Coordinate with teams owning these flows")
        print("   → Plan API compatibility or migration together")
    else:
        print("   ✓ No dependent flows (low migration risk)")
    
    print("\n3. Interface Contracts:")
    if interfaces['outbound']:
        print("   Outbound interfaces to maintain:")
        for interface in interfaces['outbound']:
            print(f"     - {interface['source']} → {interface['target']} ({interface['type']})")
        print("   → Ensure API compatibility with required flows")
    
    print("\n4. Migration Sequence:")
    if dependencies['requiredFlows']:
        print(f"   Step 1: Migrate {', '.join(dependencies['requiredFlows'])}")
        print(f"   Step 2: Migrate {flow_id}")
        if dependencies['dependentFlows']:
            print(f"   Step 3: Migrate {', '.join(dependencies['dependentFlows'])}")
    else:
        print(f"   Step 1: Migrate {flow_id}")
        if dependencies['dependentFlows']:
            print(f"   Step 2: Migrate {', '.join(dependencies['dependentFlows'])}")
    
    conn.close()


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("FLOW DEPENDENCIES IDENTIFICATION - DEMO")
    print("=" * 70)
    print("\nThis demo shows how to identify and use flow dependencies")
    print("for migration planning.")
    
    demo_no_dependencies()
    demo_required_flows()
    demo_dependent_flows()
    demo_circular_dependencies()
    demo_complex_dependency_graph()
    demo_migration_planning()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Required flows must be migrated before the current flow")
    print("  2. Dependent flows can only be migrated after the current flow")
    print("  3. Circular dependencies require coordinated migration")
    print("  4. Use dependencies to plan migration waves")
    print("  5. Identify shared utilities that affect multiple flows")
    print("\nNext Steps:")
    print("  - Use identify_flow_dependencies() in your migration planning")
    print("  - Analyze dependency graphs to optimize migration sequence")
    print("  - Identify opportunities for parallel migration")
    print("  - Plan API contracts for interface compatibility")


if __name__ == '__main__':
    main()
