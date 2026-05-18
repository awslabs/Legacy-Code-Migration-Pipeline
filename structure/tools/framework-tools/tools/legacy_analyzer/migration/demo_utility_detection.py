#!/usr/bin/env python3
"""
Demo script for utility program detection.

This script demonstrates how to use the UtilityDetector to identify
utility programs shared across multiple flows.
"""

import sqlite3
from tools.legacy_analyzer.migration.schema import MigrationFlowSchema
from tools.legacy_analyzer.migration.utility_detector import UtilityDetector


def main():
    """Run utility detection demo."""
    
    # Create in-memory database
    print("Setting up database...")
    conn = sqlite3.connect(':memory:')
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    print("✓ Database schema created\n")
    
    # Sample flows data
    print("Sample flows:")
    all_flows = {
        'FLOW_PAYROLL1': {
            'flow_id': 'FLOW_PAYROLL1',
            'entry_program': 'PAYROLL1',
            'start_program': 'PAYROLL1',
            'programs': ['PAYROLL1', 'PAYCALC', 'UTIL_COMMON', 'UTIL_DB', 'HELPER1']
        },
        'FLOW_BILLING1': {
            'flow_id': 'FLOW_BILLING1',
            'entry_program': 'BILLING1',
            'start_program': 'BILLING1',
            'programs': ['BILLING1', 'BILLCALC', 'UTIL_COMMON', 'UTIL_DB', 'HELPER2']
        },
        'FLOW_ACCT1': {
            'flow_id': 'FLOW_ACCT1',
            'entry_program': 'ACCT1',
            'start_program': 'ACCT1',
            'programs': ['ACCT1', 'ACCTCALC', 'UTIL_COMMON', 'COMMON_LOGGER']
        },
        'FLOW_REPORT1': {
            'flow_id': 'FLOW_REPORT1',
            'entry_program': 'REPORT1',
            'start_program': 'REPORT1',
            'programs': ['REPORT1', 'RPTGEN', 'UTIL_COMMON', 'UTIL_DB', 'COMMON_LOGGER']
        },
        'FLOW_BATCH1': {
            'flow_id': 'FLOW_BATCH1',
            'entry_program': 'BATCH1',
            'start_program': 'BATCH1',
            'programs': ['BATCH1', 'BATCHPROC', 'UTIL_COMMON', 'UTIL_DB', 'COMMON_LOGGER']
        },
        'FLOW_ONLINE1': {
            'flow_id': 'FLOW_ONLINE1',
            'entry_program': 'ONLINE1',
            'start_program': 'ONLINE1',
            'programs': ['ONLINE1', 'ONLINEPROC', 'UTIL_COMMON', 'COMMON_LOGGER']
        }
    }
    
    for flow_id, flow in all_flows.items():
        print(f"  {flow_id}: {len(flow['programs'])} programs")
    print()
    
    # Initialize detector
    print("Detecting utility programs...")
    detector = UtilityDetector(conn, call_threshold=5)
    
    # Detect utilities with patterns
    utility_patterns = ['UTIL*', 'COMMON*']
    print(f"  Using patterns: {utility_patterns}")
    print(f"  Call threshold: 5+ flows\n")
    
    utilities = detector.detect_utility_programs(all_flows, utility_patterns)
    
    # Display results
    print(f"Found {len(utilities)} utility programs:\n")
    
    for program_name, metadata in sorted(utilities.items()):
        print(f"  {program_name}:")
        print(f"    - Called by {metadata['call_count']} flows")
        print(f"    - Shared by {metadata['shared_by_flow_count']} flows")
        print(f"    - Classification: {metadata['classification']}")
        if metadata['naming_pattern']:
            print(f"    - Matched pattern: {metadata['naming_pattern']}")
        print()
    
    # Write to database
    print("Writing utility metadata to database...")
    detector.write_utility_metadata(utilities)
    print("✓ Metadata written\n")
    
    # Populate flow_scope for demonstration
    print("Populating flow_scope table...")
    cursor = conn.cursor()
    for flow_id, flow in all_flows.items():
        for program in flow['programs']:
            cursor.execute("""
                INSERT INTO flow_scope (flow_id, artifact_type, artifact_name)
                VALUES (?, 'PROGRAM', ?)
            """, (flow_id, program))
    conn.commit()
    print("✓ Flow scope populated\n")
    
    # Demonstrate extended scope format
    print("Extended scope format example:")
    print("=" * 60)
    
    sample_programs = ['PAYROLL1', 'PAYCALC', 'UTIL_COMMON', 'UTIL_DB', 'HELPER1']
    extended_scope = detector.format_extended_scope(sample_programs)
    
    print("\nPrograms in FLOW_PAYROLL1:")
    for prog in extended_scope:
        if prog['is_utility']:
            print(f"\n  {prog['name']} (UTILITY):")
            print(f"    - Call count: {prog['call_count']}")
            print(f"    - Shared by {len(prog['shared_by_flows'])} flows:")
            for flow_id in prog['shared_by_flows'][:3]:  # Show first 3
                print(f"      • {flow_id}")
            if len(prog['shared_by_flows']) > 3:
                print(f"      ... and {len(prog['shared_by_flows']) - 3} more")
        else:
            print(f"\n  {prog['name']} (regular program)")
    
    print("\n" + "=" * 60)
    
    # Query utilities from database
    print("\nQuerying utilities from database:")
    retrieved_utilities = detector.get_utility_programs()
    print(f"  Retrieved {len(retrieved_utilities)} utilities")
    
    # Check specific programs
    print("\nChecking specific programs:")
    test_programs = ['UTIL_COMMON', 'PAYROLL1', 'HELPER1']
    for prog in test_programs:
        is_util = detector.is_utility_program(prog)
        status = "✓ UTILITY" if is_util else "✗ Not a utility"
        print(f"  {prog}: {status}")
    
    # Get shared flows for a utility
    print("\nFlows sharing UTIL_COMMON:")
    shared_flows = detector.get_shared_flows('UTIL_COMMON')
    for flow_id in shared_flows:
        print(f"  • {flow_id}")
    
    print("\n✅ Demo complete!")
    
    conn.close()


if __name__ == '__main__':
    main()
