"""
Demo script for Migration Flow Export Python API.

This script demonstrates how to use the LegacyAnalyzerAPI to build
and export migration flows programmatically.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.legacy_analyzer.api import LegacyAnalyzerAPI


def demo_basic_usage():
    """Demonstrate basic API usage."""
    print("=" * 80)
    print("DEMO 1: Basic Usage")
    print("=" * 80)
    
    # Use an in-memory database for demo
    api = LegacyAnalyzerAPI(":memory:")
    
    try:
        # Create migration schema (required for demo)
        from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
        create_migration_flow_schema(api.db.conn, verbose=False)
        
        # Note: In a real scenario, you would have already populated the database
        # with dependencies and inventory data using the static analyzer
        
        print("\n1. Building migration flows...")
        flow_ids = api.build_migration_flows()
        print(f"   ✓ Built {len(flow_ids)} flows")
        
        if flow_ids:
            print(f"   Flow IDs: {', '.join(flow_ids)}")
        else:
            print("   (No flows built - database has no entry points)")
        
        print("\n2. Exporting flows to JSON...")
        result = api.export_migration_flows("demo_flows.json")
        print(f"   ✓ Exported {len(result['flows'])} flows")
        
        # Clean up demo file
        Path("demo_flows.json").unlink(missing_ok=True)
        
    finally:
        api.close()
    
    print("\n✓ Demo 1 complete\n")


def demo_with_filters():
    """Demonstrate API usage with filters."""
    print("=" * 80)
    print("DEMO 2: Export with Filters")
    print("=" * 80)
    
    api = LegacyAnalyzerAPI(":memory:")
    
    try:
        # Create migration schema
        from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
        create_migration_flow_schema(api.db.conn, verbose=False)
        
        print("\n1. Building migration flows...")
        flow_ids = api.build_migration_flows()
        print(f"   ✓ Built {len(flow_ids)} flows")
        
        if flow_ids:
            print("\n2. Exporting high complexity flows...")
            result = api.export_migration_flows(
                output_file="high_complexity.json",
                min_complexity="HIGH"
            )
            print(f"   ✓ Exported {len(result['flows'])} high complexity flows")
            
            print("\n3. Exporting specific flows...")
            result = api.export_migration_flows(
                output_file="specific_flows.json",
                flow_ids=flow_ids[:2] if len(flow_ids) >= 2 else flow_ids
            )
            print(f"   ✓ Exported {len(result['flows'])} specific flows")
            
            # Clean up demo files
            Path("high_complexity.json").unlink(missing_ok=True)
            Path("specific_flows.json").unlink(missing_ok=True)
        else:
            print("   (No flows to export - database has no entry points)")
        
    finally:
        api.close()
    
    print("\n✓ Demo 2 complete\n")


def demo_context_manager():
    """Demonstrate API usage with context manager."""
    print("=" * 80)
    print("DEMO 3: Context Manager Usage")
    print("=" * 80)
    
    print("\n1. Using context manager for automatic cleanup...")
    
    with LegacyAnalyzerAPI(":memory:") as api:
        # Create migration schema
        from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
        create_migration_flow_schema(api.db.conn, verbose=False)
        
        flow_ids = api.build_migration_flows()
        print(f"   ✓ Built {len(flow_ids)} flows")
        
        if flow_ids:
            result = api.export_migration_flows("context_flows.json")
            print(f"   ✓ Exported {len(result['flows'])} flows")
            
            # Clean up demo file
            Path("context_flows.json").unlink(missing_ok=True)
        else:
            print("   (No flows to export - database has no entry points)")
    
    print("   ✓ Database connection automatically closed")
    print("\n✓ Demo 3 complete\n")


def demo_error_handling():
    """Demonstrate API error handling."""
    print("=" * 80)
    print("DEMO 4: Error Handling")
    print("=" * 80)
    
    api = LegacyAnalyzerAPI(":memory:")
    
    try:
        # Create migration schema
        from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
        create_migration_flow_schema(api.db.conn, verbose=False)
        
        print("\n1. Testing invalid complexity tier...")
        try:
            api.build_migration_flows()
            api.export_migration_flows(
                output_file="flows.json",
                min_complexity="INVALID"
            )
        except ValueError as e:
            print(f"   ✓ Caught expected error: {e}")
        
        print("\n2. Testing invalid flow_ids type...")
        try:
            api.export_migration_flows(
                output_file="flows.json",
                flow_ids="not_a_list"
            )
        except ValueError as e:
            print(f"   ✓ Caught expected error: {e}")
        
        print("\n3. Testing missing output file...")
        try:
            api.export_migration_flows("")
        except ValueError as e:
            print(f"   ✓ Caught expected error: {e}")
        
    finally:
        api.close()
    
    print("\n✓ Demo 4 complete\n")


def demo_complete_workflow():
    """Demonstrate complete workflow."""
    print("=" * 80)
    print("DEMO 5: Complete Workflow")
    print("=" * 80)
    
    print("\nThis demo shows a complete workflow:")
    print("1. Initialize API")
    print("2. Build migration flows")
    print("3. Export all flows")
    print("4. Export filtered flows")
    print("5. Clean up")
    
    with LegacyAnalyzerAPI(":memory:") as api:
        # Create migration schema
        from tools.legacy_analyzer.migration.schema import create_migration_flow_schema
        create_migration_flow_schema(api.db.conn, verbose=False)
        
        print("\n1. Building migration flows...")
        flow_ids = api.build_migration_flows()
        print(f"   ✓ Built {len(flow_ids)} flows")
        
        if flow_ids:
            print("\n2. Exporting all flows...")
            all_result = api.export_migration_flows("all_flows.json")
            print(f"   ✓ Exported {len(all_result['flows'])} flows")
            
            print("\n3. Exporting high complexity flows...")
            high_result = api.export_migration_flows(
                output_file="high_flows.json",
                min_complexity="HIGH"
            )
            print(f"   ✓ Exported {len(high_result['flows'])} high complexity flows")
            
            print("\n4. Exporting medium+ complexity flows...")
            medium_result = api.export_migration_flows(
                output_file="medium_flows.json",
                min_complexity="MEDIUM"
            )
            print(f"   ✓ Exported {len(medium_result['flows'])} medium+ complexity flows")
            
            # Clean up demo files
            Path("all_flows.json").unlink(missing_ok=True)
            Path("high_flows.json").unlink(missing_ok=True)
            Path("medium_flows.json").unlink(missing_ok=True)
        else:
            print("   (No flows to export - database has no entry points)")
    
    print("\n✓ Demo 5 complete\n")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("Migration Flow Export Python API - Demo")
    print("=" * 80)
    print("\nThis demo shows how to use the LegacyAnalyzerAPI for migration flows.")
    print("Note: These demos use in-memory databases with no data,")
    print("      so no actual flows will be built or exported.")
    print("\n")
    
    try:
        demo_basic_usage()
        demo_with_filters()
        demo_context_manager()
        demo_error_handling()
        demo_complete_workflow()
        
        print("=" * 80)
        print("All demos completed successfully!")
        print("=" * 80)
        print("\nFor more information, see:")
        print("  - tools/legacy_analyzer/migration/MIGRATION_API_GUIDE.md")
        print("  - tests/integration/test_migration_api.py")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
