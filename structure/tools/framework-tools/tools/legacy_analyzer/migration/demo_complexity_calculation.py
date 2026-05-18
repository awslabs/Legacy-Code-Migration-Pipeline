"""
Demo script for complexity calculation in migration flow builder.

This script demonstrates how to calculate aggregate complexity metrics
for migration flows using the MigrationFlowBuilder.
"""

import sqlite3
import tempfile
import os
from tools.legacy_analyzer.migration.flow_builder import MigrationFlowBuilder


def create_demo_database():
    """Create a demo database with sample complexity metrics."""
    # Create temporary database
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(path)
    
    # Create complexity_metrics table
    conn.execute("""
        CREATE TABLE complexity_metrics (
            program_name VARCHAR(44) PRIMARY KEY,
            lines_of_code INTEGER,
            total_lines INTEGER,
            cyclomatic_complexity INTEGER,
            dependency_count_in INTEGER,
            dependency_count_out INTEGER,
            composite_score REAL,
            complexity_tier VARCHAR(10),
            language_factor REAL,
            is_god_program INTEGER,
            analyzed_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert sample data for a payroll flow
    payroll_programs = [
        ('PAYROLL1', 1200, 60, 45.5, 'MEDIUM'),  # Entry point
        ('PAYCALC', 800, 40, 35.0, 'MEDIUM'),    # Calculation logic
        ('PAYDB', 500, 25, 28.0, 'LOW'),         # Database access
        ('PAYUTIL', 300, 15, 18.0, 'LOW')        # Utility functions
    ]
    
    for prog_name, loc, cyclomatic, composite, tier in payroll_programs:
        conn.execute("""
            INSERT INTO complexity_metrics 
            (program_name, lines_of_code, cyclomatic_complexity, composite_score, complexity_tier)
            VALUES (?, ?, ?, ?, ?)
        """, (prog_name, loc, cyclomatic, composite, tier))
    
    # Insert sample data for a billing flow (higher complexity)
    billing_programs = [
        ('BILLING1', 2500, 125, 75.0, 'HIGH'),   # Entry point
        ('BILLCALC', 1800, 90, 65.0, 'HIGH'),    # Complex calculations
        ('BILLDB', 1200, 60, 50.0, 'MEDIUM'),    # Database operations
        ('BILLRPT', 1000, 50, 45.0, 'MEDIUM'),   # Report generation
        ('BILLUTIL', 400, 20, 22.0, 'LOW')       # Utilities
    ]
    
    for prog_name, loc, cyclomatic, composite, tier in billing_programs:
        conn.execute("""
            INSERT INTO complexity_metrics 
            (program_name, lines_of_code, cyclomatic_complexity, composite_score, complexity_tier)
            VALUES (?, ?, ?, ?, ?)
        """, (prog_name, loc, cyclomatic, composite, tier))
    
    conn.commit()
    
    return conn, path


def demo_basic_complexity_calculation():
    """Demonstrate basic complexity calculation for a single flow."""
    print("=" * 80)
    print("DEMO 1: Basic Complexity Calculation")
    print("=" * 80)
    
    # Create demo database
    conn, db_path = create_demo_database()
    
    try:
        # Create flow builder
        builder = MigrationFlowBuilder(conn)
        
        # Calculate complexity for payroll flow
        print("\n1. Payroll Flow Complexity:")
        print("-" * 80)
        payroll_programs = ['PAYROLL1', 'PAYCALC', 'PAYDB', 'PAYUTIL']
        result = builder.calculate_flow_complexity(payroll_programs)
        
        print(f"Programs in flow: {result['totalPrograms']}")
        print(f"Total lines of code: {result['totalLines']:,}")
        print(f"Total cyclomatic complexity: {result['cyclomaticComplexity']}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Complexity tier: {result['tier']}")
        
        # Calculate complexity for billing flow
        print("\n2. Billing Flow Complexity:")
        print("-" * 80)
        billing_programs = ['BILLING1', 'BILLCALC', 'BILLDB', 'BILLRPT', 'BILLUTIL']
        result = builder.calculate_flow_complexity(billing_programs)
        
        print(f"Programs in flow: {result['totalPrograms']}")
        print(f"Total lines of code: {result['totalLines']:,}")
        print(f"Total cyclomatic complexity: {result['cyclomaticComplexity']}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Complexity tier: {result['tier']}")
        
    finally:
        conn.close()
        os.unlink(db_path)


def demo_missing_data_handling():
    """Demonstrate handling of missing complexity data."""
    print("\n" + "=" * 80)
    print("DEMO 2: Missing Data Handling")
    print("=" * 80)
    
    # Create demo database
    conn, db_path = create_demo_database()
    
    try:
        # Create flow builder
        builder = MigrationFlowBuilder(conn)
        
        # Calculate complexity for programs with no data
        print("\n1. Programs with No Complexity Data:")
        print("-" * 80)
        unknown_programs = ['UNKNOWN1', 'UNKNOWN2', 'UNKNOWN3']
        result = builder.calculate_flow_complexity(unknown_programs)
        
        print(f"Programs in flow: {result['totalPrograms']}")
        print(f"Total lines of code: {result['totalLines']:,}")
        print(f"Total cyclomatic complexity: {result['cyclomaticComplexity']}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Complexity tier: {result['tier']}")
        print("\nNote: Tier is 'UNKNOWN' when no complexity data is available")
        
        # Calculate complexity for mixed data (some programs have data, some don't)
        print("\n2. Mixed Data (Some Programs Have Data):")
        print("-" * 80)
        mixed_programs = ['PAYROLL1', 'PAYCALC', 'UNKNOWN1']
        result = builder.calculate_flow_complexity(mixed_programs)
        
        print(f"Programs in flow: {result['totalPrograms']}")
        print(f"Total lines of code: {result['totalLines']:,}")
        print(f"Total cyclomatic complexity: {result['cyclomaticComplexity']}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Complexity tier: {result['tier']}")
        print("\nNote: Metrics include only programs with available data")
        
    finally:
        conn.close()
        os.unlink(db_path)


def demo_complexity_tiers():
    """Demonstrate different complexity tiers."""
    print("\n" + "=" * 80)
    print("DEMO 3: Complexity Tiers")
    print("=" * 80)
    
    # Create demo database
    conn, db_path = create_demo_database()
    
    try:
        # Create flow builder
        builder = MigrationFlowBuilder(conn)
        
        # LOW tier (payroll utilities only)
        print("\n1. LOW Complexity Tier (< 25):")
        print("-" * 80)
        low_programs = ['PAYUTIL']
        result = builder.calculate_flow_complexity(low_programs)
        print(f"Programs: {low_programs}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Tier: {result['tier']}")
        
        # MEDIUM tier (payroll flow)
        print("\n2. MEDIUM Complexity Tier (25-50):")
        print("-" * 80)
        medium_programs = ['PAYROLL1', 'PAYCALC', 'PAYDB']
        result = builder.calculate_flow_complexity(medium_programs)
        print(f"Programs: {medium_programs}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Tier: {result['tier']}")
        
        # HIGH tier (billing flow)
        print("\n3. HIGH Complexity Tier (50-75):")
        print("-" * 80)
        high_programs = ['BILLING1', 'BILLCALC', 'BILLDB']
        result = builder.calculate_flow_complexity(high_programs)
        print(f"Programs: {high_programs}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Tier: {result['tier']}")
        
        # VERY_HIGH tier (all billing programs)
        print("\n4. VERY_HIGH Complexity Tier (>= 75):")
        print("-" * 80)
        very_high_programs = ['BILLING1', 'BILLCALC', 'BILLDB', 'BILLRPT']
        result = builder.calculate_flow_complexity(very_high_programs)
        print(f"Programs: {very_high_programs}")
        print(f"Composite score: {result['compositeScore']:.2f}")
        print(f"Tier: {result['tier']}")
        
    finally:
        conn.close()
        os.unlink(db_path)


def demo_composite_score_breakdown():
    """Demonstrate how composite score is calculated."""
    print("\n" + "=" * 80)
    print("DEMO 4: Composite Score Breakdown")
    print("=" * 80)
    
    # Create demo database
    conn, db_path = create_demo_database()
    
    try:
        # Create flow builder
        builder = MigrationFlowBuilder(conn)
        
        # Calculate complexity for payroll flow
        print("\nPayroll Flow Complexity Breakdown:")
        print("-" * 80)
        payroll_programs = ['PAYROLL1', 'PAYCALC', 'PAYDB', 'PAYUTIL']
        result = builder.calculate_flow_complexity(payroll_programs)
        
        print(f"\nInput Metrics:")
        print(f"  Total Programs: {result['totalPrograms']}")
        print(f"  Total Lines of Code: {result['totalLines']:,}")
        print(f"  Total Cyclomatic Complexity: {result['cyclomaticComplexity']}")
        
        print(f"\nComposite Score Calculation:")
        print(f"  Formula: (LOC * 0.4) + (Cyclomatic * 0.4) + (Programs * 0.2)")
        print(f"  Normalization factors:")
        print(f"    - LOC: divided by 50 (5,000 LOC = 100 points)")
        print(f"    - Cyclomatic: divided by 5 (500 cyclomatic = 100 points)")
        print(f"    - Programs: divided by 0.5 (50 programs = 100 points)")
        
        print(f"\nResult:")
        print(f"  Composite Score: {result['compositeScore']:.2f}")
        print(f"  Complexity Tier: {result['tier']}")
        
        print(f"\nTier Thresholds:")
        print(f"  LOW:       < 25")
        print(f"  MEDIUM:    25-50")
        print(f"  HIGH:      50-75")
        print(f"  VERY_HIGH: >= 75")
        
    finally:
        conn.close()
        os.unlink(db_path)


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COMPLEXITY CALCULATION DEMO" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    demo_basic_complexity_calculation()
    demo_missing_data_handling()
    demo_complexity_tiers()
    demo_composite_score_breakdown()
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


if __name__ == '__main__':
    main()
