"""
Database setup utilities for legacy analyzer.

This module provides utilities to create all required database tables
for the legacy analyzer system, including program-level dependency tracking.
"""

from typing import Optional
from .inventory.inventory_loader import InventoryLoader
from .analysis.complexity_analyzer import ComplexityAnalyzer


class DatabaseSetup:
    """Utility class for setting up all required database tables."""
    
    def __init__(self, database):
        """
        Initialize database setup utility.
        
        Args:
            database: Database adapter instance
        """
        self.database = database
        
        # Handle both raw connections and adapters
        if hasattr(database, 'cursor') and callable(database.cursor):
            self.cursor = database.cursor()
        elif hasattr(database, 'cursor'):
            self.cursor = database.cursor
        else:
            raise ValueError("Database must have a cursor attribute or method")
    
    def create_all_tables(self, verbose: bool = True, include_migration_flows: bool = False) -> None:
        """
        Create all required tables for the legacy analyzer system.
        
        This includes:
        - Inventory tables (JCL, programs, copybooks, datasets, CICS)
        - Complexity metrics table
        - Program-level dependency tracking tables
        - Artifact dependencies table
        - Migration flow tables (optional)
        
        Args:
            verbose: If True, print progress messages
            include_migration_flows: If True, create migration flow tables
        """
        if verbose:
            print("Setting up complete database schema for legacy analyzer...")
        
        # Create inventory schema
        self._create_inventory_tables(verbose)
        
        # Create complexity metrics table
        self._create_complexity_metrics_table(verbose)
        
        # Create program-level tracking tables
        self._create_program_level_tables(verbose)
        
        # Create artifact dependencies table
        self._create_artifact_dependencies_table(verbose)
        
        # Create migration flow tables (optional)
        if include_migration_flows:
            self._create_migration_flow_tables(verbose)
        
        # Commit all changes
        self.database.commit()
        
        if verbose:
            print("✓ Database schema setup complete")
    
    def _create_inventory_tables(self, verbose: bool = True) -> None:
        """Create inventory tables using InventoryLoader."""
        try:
            loader = InventoryLoader(self.database)
            loader.create_inventory_schema()
            if verbose:
                print("✓ Inventory tables created")
        except Exception as e:
            if verbose:
                print(f"⚠ Warning: Could not create inventory tables: {e}")
    
    def _create_complexity_metrics_table(self, verbose: bool = True) -> None:
        """Create complexity_metrics table using ComplexityAnalyzer."""
        try:
            complexity_analyzer = ComplexityAnalyzer(self.database)
            complexity_analyzer.create_schema()
            if verbose:
                print("✓ Complexity metrics table created")
        except Exception as e:
            if verbose:
                print(f"⚠ Warning: Could not create complexity_metrics table: {e}")
    
    def _create_program_level_tables(self, verbose: bool = True) -> None:
        """Create program-level dependency tracking tables."""
        try:
            # Create program_file_mapping table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS program_file_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    program_name VARCHAR(44) NOT NULL,
                    program_index INTEGER NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    program_type VARCHAR(20) NOT NULL,
                    language VARCHAR(20) NOT NULL,
                    entry_points TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_path, program_name)
                )
            """)
            
            # Create copybook_analysis table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS copybook_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    copybook_name VARCHAR(44) NOT NULL,
                    file_path TEXT NOT NULL,
                    has_executable_code BOOLEAN NOT NULL,
                    confidence_level DECIMAL(3,2) NOT NULL,
                    data_structures TEXT,
                    procedure_calls TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_path)
                )
            """)
            
            if verbose:
                print("✓ Program-level tracking tables created")
                
        except Exception as e:
            if verbose:
                print(f"⚠ Warning: Could not create program-level tables: {e}")
    
    def _create_artifact_dependencies_table(self, verbose: bool = True) -> None:
        """Create artifact_dependencies table for dependency tracking."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifact_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_artifact_name VARCHAR(44) NOT NULL,
                    source_artifact_type VARCHAR(20) NOT NULL,
                    target_artifact_name VARCHAR(44) NOT NULL,
                    target_artifact_type VARCHAR(20) NOT NULL,
                    dependency_type VARCHAR(20) NOT NULL,
                    source_file_path VARCHAR(255),
                    target_file_path VARCHAR(255),
                    line_number INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_artifact_name, target_artifact_name, dependency_type)
                )
            """)
            
            # Create indexes for performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_artifact_deps_source 
                ON artifact_dependencies(source_artifact_name)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_artifact_deps_target 
                ON artifact_dependencies(target_artifact_name)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_artifact_deps_type 
                ON artifact_dependencies(dependency_type)
            """)
            
            if verbose:
                print("✓ Artifact dependencies table created")
                
        except Exception as e:
            if verbose:
                print(f"⚠ Warning: Could not create artifact_dependencies table: {e}")
    
    def _create_migration_flow_tables(self, verbose: bool = True) -> None:
        """Create migration flow tables using MigrationFlowSchema."""
        try:
            from .migration.schema import MigrationFlowSchema
            
            schema = MigrationFlowSchema(self.database)
            schema.create_schema(verbose=verbose)
            
            if verbose:
                print("✓ Migration flow tables created")
                
        except Exception as e:
            if verbose:
                print(f"⚠ Warning: Could not create migration flow tables: {e}")
    
    def verify_schema(self, verbose: bool = True, include_migration_flows: bool = False) -> dict:
        """
        Verify that all required tables exist.
        
        Args:
            verbose: If True, print verification results
            include_migration_flows: If True, verify migration flow tables
            
        Returns:
            Dictionary with table existence status
        """
        required_tables = [
            'inventory_jcl',
            'inventory_programs', 
            'inventory_copybooks',
            'inventory_datasets',
            'inventory_cics',
            'complexity_metrics',
            'program_file_mapping',
            'copybook_analysis',
            'artifact_dependencies'
        ]
        
        if include_migration_flows:
            required_tables.extend([
                'migration_flows',
                'flow_entry_types',
                'flow_scope',
                'flow_interfaces',
                'flow_data_operations',
                'flow_dependencies'
            ])
        
        results = {}
        
        for table_name in required_tables:
            try:
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                exists = self.cursor.fetchone() is not None
                results[table_name] = exists
                
                if verbose:
                    status = "✓" if exists else "✗"
                    print(f"  {status} {table_name}")
                    
            except Exception as e:
                results[table_name] = False
                if verbose:
                    print(f"  ✗ {table_name} (error: {e})")
        
        return results
    
    def get_missing_tables(self) -> list:
        """
        Get list of missing required tables.
        
        Returns:
            List of missing table names
        """
        verification = self.verify_schema(verbose=False)
        return [table for table, exists in verification.items() if not exists]
    
    def is_schema_complete(self) -> bool:
        """
        Check if all required tables exist.
        
        Returns:
            True if all required tables exist, False otherwise
        """
        return len(self.get_missing_tables()) == 0


def setup_complete_database_schema(database, verbose: bool = True, include_migration_flows: bool = False) -> bool:
    """
    Convenience function to set up complete database schema.
    
    Args:
        database: Database adapter instance
        verbose: If True, print progress messages
        include_migration_flows: If True, create migration flow tables
        
    Returns:
        True if setup was successful, False otherwise
    """
    try:
        setup = DatabaseSetup(database)
        setup.create_all_tables(verbose, include_migration_flows)
        return setup.is_schema_complete()
    except Exception as e:
        if verbose:
            print(f"✗ Database setup failed: {e}")
        return False