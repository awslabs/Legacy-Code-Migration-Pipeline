#!/usr/bin/env python3
"""
Demo: Error Handling and Validation

This script demonstrates the error handling and validation features
of the migration flow export system.
"""

import sqlite3
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tools.legacy_analyzer.migration.exceptions import FlowValidationError, MissingDataError, ExportError
from tools.legacy_analyzer.migration.flow_builder import generate_flow_id, MigrationFlowBuilder
from tools.legacy_analyzer.migration.flow_exporter import MigrationFlowExporter
from tools.legacy_analyzer.migration.schema import create_migration_flow_schema


def demo_exception_classes():
    """Demonstrate custom exception classes."""
    print("=" * 70)
    print("DEMO: Custom Exception Classes")
    print("=" * 70)
    
    # FlowValidationError
    print("\n1. FlowValidationError:")
    try:
        raise FlowValidationError(
            "Invalid flow data structure",
            flow_id="FLOW_TEST",
            details={'field': 'programs', 'expected': 'list', 'actual': 'dict'}
        )
    except FlowValidationError as e:
        print(f"   Error: {e}")
        print(f"   Flow ID: {e.flow_id}")
        print(f"   Details: {e.details}")
    
    # MissingDataError
    print("\n2. MissingDataError:")
    try:
        raise MissingDataError(
            "Complexity metrics not found",
            data_type="complexity",
            artifact_name="PAYROLL1"
        )
    except MissingDataError as e:
        print(f"   Error: {e}")
        print(f"   Data Type: {e.data_type}")
        print(f"   Artifact: {e.artifact_name}")
    
    # ExportError
    print("\n3. ExportError:")
    try:
        cause = IOError("Permission denied")
        raise ExportError(
            "Cannot write to file",
            operation="write",
            cause=cause
        )
    except ExportError as e:
        print(f"   Error: {e}")
        print(f"   Operation: {e.operation}")
        print(f"   Cause: {type(e.cause).__name__}")


def demo_flow_id_validation():
    """Demonstrate flow ID generation validation."""
    print("\n" + "=" * 70)
    print("DEMO: Flow ID Generation Validation")
    print("=" * 70)
    
    # Valid flow ID
    print("\n1. Valid flow ID:")
    try:
        flow_id = generate_flow_id("PAYROLL1")
        print(f"   ✓ Generated: {flow_id}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Empty program name
    print("\n2. Empty program name:")
    try:
        flow_id = generate_flow_id("")
        print(f"   ✓ Generated: {flow_id}")
    except ValueError as e:
        print(f"   ✗ Expected error: {e}")
    
    # Special characters only
    print("\n3. Special characters only:")
    try:
        flow_id = generate_flow_id("###")
        print(f"   ✓ Generated: {flow_id}")
    except ValueError as e:
        print(f"   ✗ Expected error: {e}")
    
    # Valid with special characters
    print("\n4. Valid with special characters:")
    try:
        flow_id = generate_flow_id("PAY-ROLL#01")
        print(f"   ✓ Generated: {flow_id}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def demo_flow_data_validation():
    """Demonstrate flow data validation."""
    print("\n" + "=" * 70)
    print("DEMO: Flow Data Validation")
    print("=" * 70)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        create_migration_flow_schema(conn)
        
        # Mock the builder to avoid loading dependencies
        from unittest.mock import patch
        with patch.object(MigrationFlowBuilder, '_load_dependencies', return_value=[]):
            builder = MigrationFlowBuilder(conn)
        
        # Test 1: Invalid flow ID format
        print("\n1. Invalid flow ID format:")
        try:
            builder._validate_flow_data(
                flow_id="INVALID_ID",  # Missing FLOW_ prefix
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
            print("   ✓ Validation passed")
        except FlowValidationError as e:
            print(f"   ✗ Expected error: {e}")
        
        # Test 2: Missing scope key
        print("\n2. Missing scope key:")
        try:
            builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'copybooks': [], 'datasets': []},  # Missing 'programs'
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
            print("   ✓ Validation passed")
        except FlowValidationError as e:
            print(f"   ✗ Expected error: {e}")
        
        # Test 3: Invalid complexity tier
        print("\n3. Invalid complexity tier:")
        try:
            builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 
                           'tier': 'INVALID'},  # Invalid tier
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
            print("   ✓ Validation passed")
        except FlowValidationError as e:
            print(f"   ✗ Expected error: {e}")
        
        # Test 4: Valid flow data
        print("\n4. Valid flow data:")
        try:
            builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[
                    {'type': 'JCL', 'callers': [{'source': 'JOB1', 'metadata': {}}]}
                ],
                scope={'programs': ['PROG1'], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 1, 'totalLines': 100,
                           'cyclomaticComplexity': 10, 'compositeScore': 25.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
            print("   ✓ Validation passed")
        except FlowValidationError as e:
            print(f"   ✗ Unexpected error: {e}")
        
        conn.close()
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def demo_incomplete_flow_detection():
    """Demonstrate incomplete flow detection."""
    print("\n" + "=" * 70)
    print("DEMO: Incomplete Flow Detection")
    print("=" * 70)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        conn = sqlite3.connect(db_path)
        create_migration_flow_schema(conn)
        
        exporter = MigrationFlowExporter(conn)
        
        # Test 1: Flow with no entry types
        print("\n1. Flow with no entry types:")
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': []},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        is_incomplete = exporter._is_incomplete_flow(flow_data)
        print(f"   Incomplete: {is_incomplete}")
        
        # Test 2: Flow with no programs
        print("\n2. Flow with no programs:")
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': []},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        is_incomplete = exporter._is_incomplete_flow(flow_data)
        print(f"   Incomplete: {is_incomplete}")
        
        # Test 3: Flow with UNKNOWN complexity
        print("\n3. Flow with UNKNOWN complexity:")
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'UNKNOWN'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        is_incomplete = exporter._is_incomplete_flow(flow_data)
        print(f"   Incomplete: {is_incomplete}")
        
        # Test 4: Complete flow
        print("\n4. Complete flow:")
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {
                'databases': [{'type': 'DB2', 'operation': 'SELECT'}],
                'datasets': []
            }
        }
        is_incomplete = exporter._is_incomplete_flow(flow_data)
        print(f"   Incomplete: {is_incomplete}")
        
        conn.close()
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("MIGRATION FLOW ERROR HANDLING DEMO")
    print("=" * 70)
    
    demo_exception_classes()
    demo_flow_id_validation()
    demo_flow_data_validation()
    demo_incomplete_flow_detection()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nAll error handling features demonstrated successfully!")
    print("See test_error_handling.py for comprehensive test coverage.")


if __name__ == '__main__':
    main()
