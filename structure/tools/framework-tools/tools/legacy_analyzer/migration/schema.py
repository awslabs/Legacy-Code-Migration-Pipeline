"""
Database schema for migration-focused flow export.

This module defines the database schema for storing migration flow data,
including flow metadata, entry point types, scope, interfaces, data operations,
and dependencies.
"""

from typing import Optional
from datetime import datetime


class MigrationFlowSchema:
    """Manages database schema for migration flows."""
    
    def __init__(self, db_connection):
        """
        Initialize migration flow schema manager.
        
        Args:
            db_connection: Database connection object (e.g., sqlite3.Connection)
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def create_schema(self, verbose: bool = True) -> None:
        """
        Create all migration flow tables and indexes.
        
        Args:
            verbose: If True, print progress messages
        """
        if verbose:
            print("Creating migration flow schema...")
        
        self._create_migration_flows_table(verbose)
        self._create_flow_entry_types_table(verbose)
        self._create_flow_scope_table(verbose)
        self._create_flow_interfaces_table(verbose)
        self._create_flow_data_operations_table(verbose)
        self._create_flow_dependencies_table(verbose)
        self._create_external_program_config_table(verbose)
        self._create_external_caller_config_table(verbose)
        self._create_program_metadata_table(verbose)
        self._create_indexes(verbose)
        
        self.conn.commit()
        
        if verbose:
            print("✓ Migration flow schema created successfully")
    
    def _create_migration_flows_table(self, verbose: bool = True) -> None:
        """Create migration_flows table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_flows (
                flow_id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(200),
                entry_program VARCHAR(44) NOT NULL,
                primary_entry_type VARCHAR(20),
                total_programs INTEGER DEFAULT 0,
                total_copybooks INTEGER DEFAULT 0,
                total_datasets INTEGER DEFAULT 0,
                complexity_total_lines INTEGER DEFAULT 0,
                complexity_cyclomatic INTEGER DEFAULT 0,
                complexity_score DECIMAL(10,2) DEFAULT 0.0,
                complexity_tier VARCHAR(10),
                priority INTEGER,
                business_domain VARCHAR(100),
                created_date DATE,
                updated_date DATE
            )
        """)
        
        if verbose:
            print("  ✓ migration_flows table created")
    
    def _create_flow_entry_types_table(self, verbose: bool = True) -> None:
        """Create flow_entry_types table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_entry_types (
                flow_id VARCHAR(100) NOT NULL,
                entry_type VARCHAR(20) NOT NULL,
                caller_source VARCHAR(100) NOT NULL,
                metadata_json TEXT,
                PRIMARY KEY (flow_id, entry_type, caller_source),
                FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
            )
        """)
        
        if verbose:
            print("  ✓ flow_entry_types table created")
    
    def _create_flow_scope_table(self, verbose: bool = True) -> None:
        """Create flow_scope table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_scope (
                flow_id VARCHAR(100) NOT NULL,
                artifact_type VARCHAR(20) NOT NULL,
                artifact_name VARCHAR(44) NOT NULL,
                PRIMARY KEY (flow_id, artifact_type, artifact_name),
                FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
            )
        """)
        
        if verbose:
            print("  ✓ flow_scope table created")
    
    def _create_flow_interfaces_table(self, verbose: bool = True) -> None:
        """Create flow_interfaces table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_interfaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id VARCHAR(100) NOT NULL,
                direction VARCHAR(10) NOT NULL,
                interface_type VARCHAR(20) NOT NULL,
                source VARCHAR(44) NOT NULL,
                target VARCHAR(44) NOT NULL,
                external BOOLEAN DEFAULT FALSE,
                metadata_json TEXT,
                FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
            )
        """)
        
        if verbose:
            print("  ✓ flow_interfaces table created")
    
    def _create_flow_data_operations_table(self, verbose: bool = True) -> None:
        """Create flow_data_operations table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_data_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id VARCHAR(100) NOT NULL,
                operation_category VARCHAR(20) NOT NULL,
                operation_type VARCHAR(20) NOT NULL,
                db_type VARCHAR(20),
                target VARCHAR(100) NOT NULL,
                program VARCHAR(44) NOT NULL,
                mode VARCHAR(10),
                FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
            )
        """)
        
        if verbose:
            print("  ✓ flow_data_operations table created")
    
    def _create_flow_dependencies_table(self, verbose: bool = True) -> None:
        """Create flow_dependencies table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_dependencies (
                flow_id VARCHAR(100) NOT NULL,
                depends_on_flow_id VARCHAR(100) NOT NULL,
                dependency_type VARCHAR(20) NOT NULL,
                PRIMARY KEY (flow_id, depends_on_flow_id, dependency_type),
                FOREIGN KEY (flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE,
                FOREIGN KEY (depends_on_flow_id) REFERENCES migration_flows(flow_id) ON DELETE CASCADE
            )
        """)
        
        if verbose:
            print("  ✓ flow_dependencies table created")
    
    def _create_external_program_config_table(self, verbose: bool = True) -> None:
        """Create external_program_config table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_program_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern VARCHAR(100) NOT NULL,
                program_type VARCHAR(50),
                scope VARCHAR(20),
                is_pattern BOOLEAN DEFAULT FALSE,
                created_date DATE
            )
        """)
        
        if verbose:
            print("  ✓ external_program_config table created")
    
    def _create_external_caller_config_table(self, verbose: bool = True) -> None:
        """Create external_caller_config table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_caller_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caller_name VARCHAR(100) NOT NULL,
                target_program VARCHAR(44) NOT NULL,
                call_type VARCHAR(20),
                metadata_json TEXT,
                created_date DATE
            )
        """)
        
        if verbose:
            print("  ✓ external_caller_config table created")
    
    def _create_program_metadata_table(self, verbose: bool = True) -> None:
        """Create program_metadata table."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS program_metadata (
                program_name VARCHAR(44) PRIMARY KEY,
                is_utility BOOLEAN DEFAULT FALSE,
                call_count INTEGER DEFAULT 0,
                classification VARCHAR(20),
                shared_by_flow_count INTEGER DEFAULT 0,
                naming_pattern VARCHAR(50),
                created_date DATE,
                updated_date DATE
            )
        """)
        
        if verbose:
            print("  ✓ program_metadata table created")
    
    def _create_indexes(self, verbose: bool = True) -> None:
        """Create indexes for performance optimization."""
        
        # Indexes for migration_flows table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_migration_flows_entry_type 
            ON migration_flows(primary_entry_type)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_migration_flows_complexity_tier 
            ON migration_flows(complexity_tier)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_migration_flows_business_domain 
            ON migration_flows(business_domain)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_migration_flows_entry_program 
            ON migration_flows(entry_program)
        """)
        
        # Indexes for flow_entry_types table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_entry_types_flow_id 
            ON flow_entry_types(flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_entry_types_entry_type 
            ON flow_entry_types(entry_type)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_entry_types_caller 
            ON flow_entry_types(caller_source)
        """)
        
        # Indexes for flow_scope table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_scope_flow_id 
            ON flow_scope(flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_scope_artifact_type 
            ON flow_scope(artifact_type)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_scope_artifact_name 
            ON flow_scope(artifact_name)
        """)
        
        # Indexes for flow_interfaces table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_interfaces_flow_id 
            ON flow_interfaces(flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_interfaces_direction 
            ON flow_interfaces(direction)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_interfaces_type 
            ON flow_interfaces(interface_type)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_interfaces_source 
            ON flow_interfaces(source)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_interfaces_target 
            ON flow_interfaces(target)
        """)
        
        # Indexes for flow_data_operations table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_data_ops_flow_id 
            ON flow_data_operations(flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_data_ops_category 
            ON flow_data_operations(operation_category)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_data_ops_target 
            ON flow_data_operations(target)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_data_ops_program 
            ON flow_data_operations(program)
        """)
        
        # Indexes for flow_dependencies table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_deps_flow_id 
            ON flow_dependencies(flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_deps_depends_on 
            ON flow_dependencies(depends_on_flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_deps_type 
            ON flow_dependencies(dependency_type)
        """)
        
        # Indexes for external_program_config table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_external_program_pattern 
            ON external_program_config(pattern)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_external_program_type 
            ON external_program_config(program_type)
        """)
        
        # Indexes for external_caller_config table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_external_caller_name 
            ON external_caller_config(caller_name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_external_caller_target 
            ON external_caller_config(target_program)
        """)
        
        # Indexes for program_metadata table
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_program_metadata_is_utility 
            ON program_metadata(is_utility)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_program_metadata_classification 
            ON program_metadata(classification)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_program_metadata_call_count 
            ON program_metadata(call_count)
        """)
        
        if verbose:
            print("  ✓ Indexes created")
    
    def drop_schema(self, verbose: bool = True) -> None:
        """
        Drop all migration flow tables.
        
        WARNING: This will delete all migration flow data!
        
        Args:
            verbose: If True, print progress messages
        """
        if verbose:
            print("Dropping migration flow schema...")
        
        # Drop tables in reverse order to handle foreign key constraints
        tables = [
            'flow_dependencies',
            'flow_data_operations',
            'flow_interfaces',
            'flow_scope',
            'flow_entry_types',
            'migration_flows',
            'external_caller_config',
            'external_program_config',
            'program_metadata'
        ]
        
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
            if verbose:
                print(f"  ✓ Dropped {table}")
        
        self.conn.commit()
        
        if verbose:
            print("✓ Migration flow schema dropped")
    
    def verify_schema(self, verbose: bool = True) -> dict:
        """
        Verify that all migration flow tables exist.
        
        Args:
            verbose: If True, print verification results
            
        Returns:
            Dictionary with table existence status
        """
        required_tables = [
            'migration_flows',
            'flow_entry_types',
            'flow_scope',
            'flow_interfaces',
            'flow_data_operations',
            'flow_dependencies',
            'external_program_config',
            'external_caller_config',
            'program_metadata'
        ]
        
        results = {}
        
        if verbose:
            print("Verifying migration flow schema...")
        
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
    
    def is_schema_complete(self) -> bool:
        """
        Check if all required migration flow tables exist.
        
        Returns:
            True if all required tables exist, False otherwise
        """
        verification = self.verify_schema(verbose=False)
        return all(verification.values())
    
    def get_missing_tables(self) -> list:
        """
        Get list of missing required tables.
        
        Returns:
            List of missing table names
        """
        verification = self.verify_schema(verbose=False)
        return [table for table, exists in verification.items() if not exists]
    
    def get_table_counts(self) -> dict:
        """
        Get row counts for all migration flow tables.
        
        Returns:
            Dictionary with table names and row counts
        """
        tables = [
            'migration_flows',
            'flow_entry_types',
            'flow_scope',
            'flow_interfaces',
            'flow_data_operations',
            'flow_dependencies',
            'external_program_config',
            'external_caller_config',
            'program_metadata'
        ]
        
        counts = {}
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = self.cursor.fetchone()[0]
            except Exception:
                counts[table] = None
        
        return counts


def create_migration_flow_schema(db_connection, verbose: bool = True) -> bool:
    """
    Convenience function to create migration flow schema.
    
    Args:
        db_connection: Database connection object
        verbose: If True, print progress messages
        
    Returns:
        True if schema was created successfully, False otherwise
    """
    try:
        schema = MigrationFlowSchema(db_connection)
        schema.create_schema(verbose)
        return schema.is_schema_complete()
    except Exception as e:
        if verbose:
            print(f"✗ Migration flow schema creation failed: {e}")
        return False


def verify_migration_flow_schema(db_connection, verbose: bool = True) -> bool:
    """
    Convenience function to verify migration flow schema.
    
    Args:
        db_connection: Database connection object
        verbose: If True, print verification results
        
    Returns:
        True if all tables exist, False otherwise
    """
    try:
        schema = MigrationFlowSchema(db_connection)
        return schema.is_schema_complete()
    except Exception as e:
        if verbose:
            print(f"✗ Migration flow schema verification failed: {e}")
        return False
