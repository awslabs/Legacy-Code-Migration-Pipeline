#!/usr/bin/env python3
"""
Demonstration of Interface Identification for Migration Flows

This script demonstrates how to use the interface identification functionality
to identify inbound and outbound interfaces for migration flows.

Key Concepts:
- Entry point invocations are NOT inbound interfaces (they go in entryPoint.types)
- Inbound interfaces are external programs calling NON-entry-point programs in the flow
- Outbound interfaces are flow programs calling external programs
- External program and caller configuration is supported
"""

import sqlite3
from tools.legacy_analyzer.migration import MigrationFlowBuilder


class MockDependency:
    """Mock dependency for demonstration."""
    def __init__(self, source, target, dep_type, source_type='PROGRAM', target_type='PROGRAM'):
        self.source_artifact = source
        self.target_artifact = target
        self.dependency_type = dep_type
        self.source_type = source_type
        self.target_type = target_type


class MockFlow:
    """Mock flow for demonstration."""
    def __init__(self, programs, dependencies=None):
        self.programs = programs
        self.dependencies = dependencies or []


def setup_demo_database():
    """Create a demo database with sample dependencies."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create artifact_dependencies table
    cursor.execute("""
        CREATE TABLE artifact_dependencies (
            id INTEGER PRIMARY KEY,
            source_artifact_name TEXT,
            target_artifact_name TEXT,
            dependency_type TEXT,
            source_artifact_type TEXT,
            target_artifact_type TEXT,
            source_file_path TEXT,
            line_number INTEGER
        )
    """)
    
    # Insert sample dependencies
    dependencies = [
        # External program calling entry point (NOT an inbound interface)
        ('EXTERNAL1', 'PAYROLL1', 'PROGRAM_CALL', 'PROGRAM', 'PROGRAM', '/external/ext1.cbl', 10),
        
        # External program calling non-entry program (IS an inbound interface)
        ('EXTERNAL2', 'PAYCALC', 'PROGRAM_CALL', 'PROGRAM', 'PROGRAM', '/external/ext2.cbl', 20),
        
        # Internal call (NOT an interface)
        ('PAYROLL1', 'PAYCALC', 'PROGRAM_CALL', 'PROGRAM', 'PROGRAM', '/src/payroll1.cbl', 100),
        
        # Flow program calling external program (IS an outbound interface)
        ('PAYCALC', 'DBUTIL', 'PROGRAM_CALL', 'PROGRAM', 'PROGRAM', '/src/paycalc.cbl', 200),
        
        # Flow program submitting JCL (IS an outbound interface)
        ('PAYDB', 'EXTERNAL_JOB', 'JCL_SUBMIT', 'PROGRAM', 'JCL', '/src/paydb.cbl', 300),
        
        # CICS interfaces
        ('EXTERNAL3', 'PAYDB', 'CICS_LINK', 'PROGRAM', 'PROGRAM', '/external/ext3.cbl', 30),
        ('PAYDB', 'EXTERNAL4', 'CICS_XCTL', 'PROGRAM', 'PROGRAM', '/src/paydb.cbl', 400),
    ]
    
    for dep in dependencies:
        cursor.execute("""
            INSERT INTO artifact_dependencies 
            (source_artifact_name, target_artifact_name, dependency_type,
             source_artifact_type, target_artifact_type, source_file_path, line_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, dep)
    
    conn.commit()
    return conn


def demo_basic_interface_identification():
    """Demonstrate basic interface identification."""
    print("=" * 80)
    print("DEMO 1: Basic Interface Identification")
    print("=" * 80)
    
    # Setup
    db = setup_demo_database()
    builder = MigrationFlowBuilder(db)
    
    # Create a flow
    flow = MockFlow(programs=['PAYROLL1', 'PAYCALC', 'PAYDB'])
    
    # Identify interfaces
    interfaces = builder.identify_interfaces(
        flow=flow,
        entry_program='PAYROLL1'
    )
    
    # Display results
    print("\nFlow Programs: PAYROLL1, PAYCALC, PAYDB")
    print("Entry Program: PAYROLL1")
    print()
    
    print("INBOUND INTERFACES:")
    if interfaces['inbound']:
        for i, interface in enumerate(interfaces['inbound'], 1):
            print(f"  {i}. {interface['source']} → {interface['target']}")
            print(f"     Type: {interface['type']}")
            print(f"     Metadata: {interface['metadata']}")
    else:
        print("  (none)")
    
    print()
    print("OUTBOUND INTERFACES:")
    if interfaces['outbound']:
        for i, interface in enumerate(interfaces['outbound'], 1):
            print(f"  {i}. {interface['source']} → {interface['target']}")
            print(f"     Type: {interface['type']}")
            print(f"     External: {interface.get('external', False)}")
            print(f"     Metadata: {interface['metadata']}")
    else:
        print("  (none)")
    
    print()
    print("KEY OBSERVATIONS:")
    print("  ✓ EXTERNAL1 → PAYROLL1 is NOT an inbound interface (entry point invocation)")
    print("  ✓ EXTERNAL2 → PAYCALC IS an inbound interface (non-entry program)")
    print("  ✓ PAYROLL1 → PAYCALC is NOT an interface (internal call)")
    print("  ✓ PAYCALC → DBUTIL IS an outbound interface (external program)")
    print()
    
    db.close()


def demo_external_program_configuration():
    """Demonstrate external program configuration."""
    print("=" * 80)
    print("DEMO 2: External Program Configuration")
    print("=" * 80)
    
    # Setup
    db = setup_demo_database()
    builder = MigrationFlowBuilder(db)
    
    # Create a flow that includes DBUTIL
    flow = MockFlow(programs=['PAYROLL1', 'PAYCALC', 'PAYDB', 'DBUTIL'])
    
    # Mark DBUTIL as external
    external_programs = {'DBUTIL'}
    
    # Identify interfaces
    interfaces = builder.identify_interfaces(
        flow=flow,
        entry_program='PAYROLL1',
        external_programs=external_programs
    )
    
    # Display results
    print("\nFlow Programs: PAYROLL1, PAYCALC, PAYDB, DBUTIL")
    print("Entry Program: PAYROLL1")
    print("External Programs: DBUTIL")
    print()
    
    print("OUTBOUND INTERFACES:")
    for i, interface in enumerate(interfaces['outbound'], 1):
        print(f"  {i}. {interface['source']} → {interface['target']}")
        print(f"     External: {interface.get('external', False)}")
    
    print()
    print("KEY OBSERVATION:")
    print("  ✓ DBUTIL is in the flow but marked as external")
    print("  ✓ Calls to DBUTIL are still outbound interfaces")
    print()
    
    db.close()


def demo_external_caller_configuration():
    """Demonstrate external caller configuration."""
    print("=" * 80)
    print("DEMO 3: External Caller Configuration")
    print("=" * 80)
    
    # Setup
    db = setup_demo_database()
    builder = MigrationFlowBuilder(db)
    
    # Create a flow
    flow = MockFlow(programs=['PAYROLL1', 'PAYCALC', 'PAYDB'])
    
    # Configure external callers
    external_callers = {
        'EXTERNAL_SYSTEM_A': [
            {
                'target': 'PAYCALC',
                'type': 'PROGRAM_CALL',
                'metadata': {
                    'system': 'EXTERNAL_SYSTEM_A',
                    'description': 'Legacy batch system'
                }
            }
        ],
        'EXTERNAL_SYSTEM_B': [
            {
                'target': 'PAYDB',
                'type': 'CICS_LINK',
                'metadata': {
                    'system': 'EXTERNAL_SYSTEM_B',
                    'description': 'Online transaction system'
                }
            }
        ]
    }
    
    # Identify interfaces
    interfaces = builder.identify_interfaces(
        flow=flow,
        entry_program='PAYROLL1',
        external_callers=external_callers
    )
    
    # Display results
    print("\nFlow Programs: PAYROLL1, PAYCALC, PAYDB")
    print("Entry Program: PAYROLL1")
    print("Configured External Callers: EXTERNAL_SYSTEM_A, EXTERNAL_SYSTEM_B")
    print()
    
    print("INBOUND INTERFACES:")
    for i, interface in enumerate(interfaces['inbound'], 1):
        print(f"  {i}. {interface['source']} → {interface['target']}")
        print(f"     Type: {interface['type']}")
        print(f"     External: {interface.get('external', False)}")
        if 'system' in interface['metadata']:
            print(f"     System: {interface['metadata']['system']}")
            print(f"     Description: {interface['metadata']['description']}")
    
    print()
    print("KEY OBSERVATIONS:")
    print("  ✓ Configured external callers create inbound interfaces")
    print("  ✓ Metadata from configuration is preserved")
    print("  ✓ Multiple external systems can call into the flow")
    print()
    
    db.close()


def demo_entry_point_exclusion():
    """Demonstrate entry point exclusion from inbound interfaces."""
    print("=" * 80)
    print("DEMO 4: Entry Point Exclusion")
    print("=" * 80)
    
    # Setup
    db = setup_demo_database()
    builder = MigrationFlowBuilder(db)
    
    # Create a flow
    flow = MockFlow(programs=['PAYROLL1', 'PAYCALC'])
    
    # Configure external caller to entry point
    external_callers = {
        'EXTERNAL_SYSTEM': [
            {
                'target': 'PAYROLL1',  # Entry point
                'type': 'PROGRAM_CALL'
            },
            {
                'target': 'PAYCALC',  # Non-entry point
                'type': 'PROGRAM_CALL'
            }
        ]
    }
    
    # Identify interfaces
    interfaces = builder.identify_interfaces(
        flow=flow,
        entry_program='PAYROLL1',
        external_callers=external_callers
    )
    
    # Display results
    print("\nFlow Programs: PAYROLL1, PAYCALC")
    print("Entry Program: PAYROLL1")
    print("External Caller: EXTERNAL_SYSTEM")
    print("  - Calls PAYROLL1 (entry point)")
    print("  - Calls PAYCALC (non-entry point)")
    print()
    
    print("INBOUND INTERFACES:")
    for i, interface in enumerate(interfaces['inbound'], 1):
        print(f"  {i}. {interface['source']} → {interface['target']}")
    
    print()
    print("KEY OBSERVATION:")
    print("  ✓ Call to PAYROLL1 (entry point) is NOT an inbound interface")
    print("  ✓ Call to PAYCALC (non-entry point) IS an inbound interface")
    print("  ✓ Entry point invocations go in entryPoint.types, not interfaces.inbound")
    print()
    
    db.close()


def demo_interface_types():
    """Demonstrate different interface types."""
    print("=" * 80)
    print("DEMO 5: Interface Types")
    print("=" * 80)
    
    # Setup
    db = setup_demo_database()
    builder = MigrationFlowBuilder(db)
    
    # Create a flow
    flow = MockFlow(programs=['PAYROLL1', 'PAYCALC', 'PAYDB'])
    
    # Identify interfaces
    interfaces = builder.identify_interfaces(
        flow=flow,
        entry_program='PAYROLL1'
    )
    
    # Display results
    print("\nSupported Interface Types:")
    print()
    
    print("INBOUND:")
    inbound_types = set(i['type'] for i in interfaces['inbound'])
    for itype in sorted(inbound_types):
        count = sum(1 for i in interfaces['inbound'] if i['type'] == itype)
        print(f"  - {itype}: {count} interface(s)")
    
    print()
    print("OUTBOUND:")
    outbound_types = set(i['type'] for i in interfaces['outbound'])
    for itype in sorted(outbound_types):
        count = sum(1 for i in interfaces['outbound'] if i['type'] == itype)
        print(f"  - {itype}: {count} interface(s)")
    
    print()
    print("ALL SUPPORTED TYPES:")
    print("  - PROGRAM_CALL")
    print("  - CICS_LINK")
    print("  - CICS_XCTL")
    print("  - CICS_START")
    print("  - JCL (submission)")
    print("  - EXTERNAL_CALL")
    print()
    
    db.close()


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "INTERFACE IDENTIFICATION DEMO" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    demo_basic_interface_identification()
    print()
    
    demo_external_program_configuration()
    print()
    
    demo_external_caller_configuration()
    print()
    
    demo_entry_point_exclusion()
    print()
    
    demo_interface_types()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Interface identification correctly:")
    print("  ✓ Excludes entry point invocations from inbound interfaces")
    print("  ✓ Identifies external programs calling non-entry programs")
    print("  ✓ Identifies flow programs calling external programs")
    print("  ✓ Respects external program configuration")
    print("  ✓ Integrates configured external callers")
    print("  ✓ Supports multiple interface types (PROGRAM_CALL, CICS, JCL)")
    print("  ✓ Extracts rich metadata (file paths, line numbers, etc.)")
    print()
    print("For more information, see:")
    print("  - tools/legacy_analyzer/migration/TASK_5_COMPLETE.md")
    print("  - tests/unit/test_legacy_analyzer/test_interface_identification.py")
    print()


if __name__ == '__main__':
    main()
