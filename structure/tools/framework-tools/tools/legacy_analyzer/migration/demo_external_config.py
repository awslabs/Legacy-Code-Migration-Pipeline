"""
Demo script for external program and caller configuration.

This script demonstrates how to:
1. Create a migration flow schema
2. Load external configuration from YAML
3. Query external programs and callers
"""

import sqlite3
import tempfile
import os
from tools.legacy_analyzer.migration.schema import MigrationFlowSchema
from tools.legacy_analyzer.migration.external_config import ExternalConfigLoader


def create_sample_config():
    """Create a sample external configuration YAML file."""
    config_content = """
# External programs (excluded from flow scope)
external_programs:
  # Utility patterns
  - pattern: "UTIL*"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  - pattern: "COMMON*"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  # Specific external programs
  - name: "DBUTIL"
    type: "DATABASE_UTILITY"
    scope: "EXTERNAL"
  
  - name: "LOGGER"
    type: "LOGGING"
    scope: "EXTERNAL"
  
  - name: "ERRHANDLER"
    type: "ERROR_HANDLER"
    scope: "EXTERNAL"

# External callers (create inbound interfaces)
external_callers:
  - caller: "EXTERNAL_SYSTEM_A"
    calls:
      - target: "PAYCALC"
        type: "PROGRAM_CALL"
        system: "EXTERNAL_SYSTEM_A"
        description: "Legacy batch system"
  
  - caller: "LEGACY_BILLING"
    calls:
      - target: "BILLING1"
        type: "CICS_LINK"
        system: "LEGACY_BILLING"
      - target: "BILLING2"
        type: "PROGRAM_CALL"
        system: "LEGACY_BILLING"
  
  - caller: "EXTERNAL_PAYROLL"
    calls:
      - target: "PAYROLL1"
        type: "CICS_LINK"
        transaction: "PAY1"
      - target: "PAYROLL2"
        type: "PROGRAM_CALL"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        return f.name


def demo_external_config():
    """Demonstrate external configuration loading and querying."""
    print("=" * 70)
    print("External Program and Caller Configuration Demo")
    print("=" * 70)
    
    # Create in-memory database
    print("\n1. Creating database with migration flow schema...")
    conn = sqlite3.connect(':memory:')
    schema = MigrationFlowSchema(conn)
    schema.create_schema(verbose=False)
    print("   ✓ Schema created")
    
    # Create sample configuration file
    print("\n2. Creating sample external configuration file...")
    config_path = create_sample_config()
    print(f"   ✓ Configuration file created: {config_path}")
    
    try:
        # Load external configuration
        print("\n3. Loading external configuration...")
        loader = ExternalConfigLoader(conn)
        result = loader.load_external_config(config_path, verbose=True)
        
        # Get configuration summary
        print("\n4. Configuration Summary:")
        summary = loader.get_config_summary()
        print(f"   Total external programs: {summary['total_external_programs']}")
        print(f"   - Pattern-based: {summary['pattern_programs']}")
        print(f"   - Exact matches: {summary['exact_programs']}")
        print(f"   Unique external callers: {summary['unique_external_callers']}")
        print(f"   Total external calls: {summary['total_external_calls']}")
        
        # Test external program checking
        print("\n5. Testing External Program Detection:")
        test_programs = [
            'DBUTIL',      # Exact match
            'LOGGER',      # Exact match
            'UTIL001',     # Pattern match (UTIL*)
            'UTILPROG',    # Pattern match (UTIL*)
            'COMMON01',    # Pattern match (COMMON*)
            'PAYROLL1',    # Not external
            'BILLING1'     # Not external
        ]
        
        for program in test_programs:
            is_external = loader.is_external_program(program)
            status = "EXTERNAL" if is_external else "INTERNAL"
            print(f"   {program:15} -> {status}")
        
        # Test pattern matching
        print("\n6. Testing Pattern Matching:")
        test_patterns = [
            ('UTIL123', 'Should match UTIL*'),
            ('COMMONLIB', 'Should match COMMON*'),
            ('NOTUTIL', 'Should not match any pattern')
        ]
        
        for program, description in test_patterns:
            matches, pattern = loader.matches_external_pattern(program)
            if matches:
                print(f"   {program:15} -> Matches pattern: {pattern}")
            else:
                print(f"   {program:15} -> No match")
        
        # Get external callers
        print("\n7. External Callers:")
        callers = loader.get_external_callers()
        for caller_name, calls in callers.items():
            print(f"   {caller_name}:")
            for call in calls:
                print(f"      -> {call['target']} ({call['type']})")
                if 'metadata' in call:
                    for key, value in call['metadata'].items():
                        print(f"         {key}: {value}")
        
        # Get external callers for specific target
        print("\n8. External Callers for BILLING1:")
        callers = loader.get_external_callers(target_program='BILLING1')
        for caller_name, calls in callers.items():
            print(f"   {caller_name}:")
            for call in calls:
                print(f"      -> {call['target']} ({call['type']})")
        
        # Get external programs and patterns
        print("\n9. External Programs (exact matches):")
        programs = loader.get_external_programs()
        for program in sorted(programs):
            print(f"   - {program}")
        
        print("\n10. External Patterns:")
        patterns = loader.get_external_patterns()
        for pattern in sorted(patterns):
            print(f"   - {pattern}")
        
        print("\n" + "=" * 70)
        print("✓ Demo completed successfully!")
        print("=" * 70)
        
    finally:
        # Cleanup
        conn.close()
        if os.path.exists(config_path):
            os.unlink(config_path)


if __name__ == '__main__':
    demo_external_config()
