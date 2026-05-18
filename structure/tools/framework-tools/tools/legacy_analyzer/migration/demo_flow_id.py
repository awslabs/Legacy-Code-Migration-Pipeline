#!/usr/bin/env python3
"""
Demo script for flow ID generation.

This script demonstrates the generate_flow_id() function with various examples.
"""

from flow_builder import generate_flow_id


def demo_flow_id_generation():
    """Demonstrate flow ID generation with various examples."""
    
    print("=" * 70)
    print("Flow ID Generation Demo")
    print("=" * 70)
    print()
    
    # Example 1: Basic program names
    print("1. Basic Program Names:")
    print("-" * 70)
    examples = ["PAYROLL1", "BILLING", "ACCTPROG", "BATCH001"]
    for prog in examples:
        flow_id = generate_flow_id(prog)
        print(f"   {prog:20} → {flow_id}")
    print()
    
    # Example 2: Programs with special characters
    print("2. Programs with Special Characters:")
    print("-" * 70)
    examples = ["PAY-ROLL#01", "PROG@123", "TEST.PROG", "MY-PROG-01"]
    for prog in examples:
        flow_id = generate_flow_id(prog)
        print(f"   {prog:20} → {flow_id}")
    print()
    
    # Example 3: Case insensitivity
    print("3. Case Insensitivity (all produce same flow ID):")
    print("-" * 70)
    examples = ["PAYROLL", "payroll", "Payroll", "PaYrOlL"]
    for prog in examples:
        flow_id = generate_flow_id(prog)
        print(f"   {prog:20} → {flow_id}")
    print()
    
    # Example 4: One flow per program (key design principle)
    print("4. One Flow Per Program (Multiple Invocation Types):")
    print("-" * 70)
    print("   Program: PAYROLL1")
    print("   Can be invoked by:")
    print("     - JCL: PAYROLL01 (daily batch)")
    print("     - JCL: PAYWEEK (weekly batch)")
    print("     - CICS Transaction: PAY1")
    print("     - CICS Program (CSD): PAYROLL1")
    print("     - BMS Screen: PAYSCREEN")
    print()
    flow_id = generate_flow_id("PAYROLL1")
    print(f"   Result: ONE flow ID → {flow_id}")
    print("   (Invocation types tracked separately in flow_entry_types table)")
    print()
    
    # Example 5: Deterministic behavior
    print("5. Deterministic Behavior:")
    print("-" * 70)
    prog = "TESTPROG"
    ids = [generate_flow_id(prog) for _ in range(5)]
    print(f"   Program: {prog}")
    print(f"   Generated 5 times: {set(ids)}")
    print(f"   All identical: {len(set(ids)) == 1}")
    print()
    
    # Example 6: Real-world mainframe examples
    print("6. Real-World Mainframe Program Names:")
    print("-" * 70)
    examples = [
        "COBPROG1",
        "ONLINE99",
        "BATCH-001",
        "ACCT.PROG",
        "PAY_CALC",
        "DB2UTIL"
    ]
    for prog in examples:
        flow_id = generate_flow_id(prog)
        print(f"   {prog:20} → {flow_id}")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_flow_id_generation()
