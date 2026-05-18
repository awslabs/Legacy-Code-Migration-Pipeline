"""
Interface Schema Manager

This module manages database schema for external interface tables.
It provides functionality to create and manage the inbound_interfaces
and outbound_interfaces tables used for storing external system integration points.

Database Schema:
---------------

inbound_interfaces table:
    - Stores external systems calling INTO our codebase
    - Columns: id, source_name, target_program, dependency_type, is_configured, metadata, created_at
    - UNIQUE constraint on (source_name, target_program, dependency_type)
    - Indexes on target_program and source_name for query performance

outbound_interfaces table:
    - Stores our codebase calling OUT to external systems
    - Columns: id, program_name, reason, metadata, created_at
    - UNIQUE constraint on program_name
    - Index on program_name for query performance

Usage:
------
    >>> from interface_schema import InterfaceSchemaManager
    >>> schema_manager = InterfaceSchemaManager(db_connection)
    >>> schema_manager.create_tables()  # Idempotent - safe to call multiple times
    >>> schema_manager.table_exists('inbound_interfaces')  # True
"""

import logging
import sqlite3
from typing import Optional

logger = logging.getLogger(__name__)


class InterfaceSchemaManager:
    """
    Manages database schema for external interface tables.
    
    This class is responsible for creating and managing the database tables
    that store external interface configuration:
    - inbound_interfaces: External systems calling INTO our codebase
    - outbound_interfaces: Our codebase calling OUT to external systems
    
    Database Schema Details:
    -----------------------
    
    inbound_interfaces:
        CREATE TABLE inbound_interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,           -- External caller name
            target_program TEXT NOT NULL,        -- Program in our codebase
            dependency_type TEXT NOT NULL,       -- PROGRAM_CALL, CICS_LINK, etc.
            is_configured BOOLEAN DEFAULT 0,     -- Manually configured vs auto-detected
            metadata TEXT,                       -- JSON blob for additional info
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_name, target_program, dependency_type)
        );
        
        Indexes:
        - idx_inbound_target ON target_program
        - idx_inbound_source ON source_name
    
    outbound_interfaces:
        CREATE TABLE outbound_interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT NOT NULL UNIQUE,   -- External program name
            reason TEXT,                         -- "configured", "missing_source_code", etc.
            metadata TEXT,                       -- JSON blob
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        Indexes:
        - idx_outbound_program ON program_name
    
    Query Patterns:
    --------------
    
    Query inbound interfaces for a flow:
        SELECT source_name, target_program, dependency_type, metadata
        FROM inbound_interfaces
        WHERE target_program IN (?, ?, ...)  -- flow programs
    
    Query all outbound interfaces:
        SELECT program_name, reason, metadata
        FROM outbound_interfaces
    
    Insert with duplicate prevention:
        INSERT OR IGNORE INTO inbound_interfaces 
        (source_name, target_program, dependency_type, is_configured, metadata)
        VALUES (?, ?, ?, ?, ?)
    
    Example Usage:
    -------------
        >>> schema_manager = InterfaceSchemaManager(db_connection)
        >>> schema_manager.create_tables()
        >>> if schema_manager.table_exists('inbound_interfaces'):
        ...     print("Tables created successfully")
        >>> version = schema_manager.get_schema_version()
        >>> print(f"Schema version: {version}")
    """
    
    # Schema version for migration tracking
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize the InterfaceSchemaManager.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def create_tables(self) -> None:
        """
        Create inbound_interfaces and outbound_interfaces tables if they don't exist.
        
        This method is idempotent - it can be called multiple times without
        dropping or recreating existing tables.
        
        Tables created:
        - inbound_interfaces: External systems calling INTO our codebase
        - outbound_interfaces: Our codebase calling OUT to external systems
        
        Raises:
            sqlite3.Error: If table creation fails
        """
        cursor = self.db.cursor()
        
        try:
            # Create inbound_interfaces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inbound_interfaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    target_program TEXT NOT NULL,
                    dependency_type TEXT NOT NULL,
                    is_configured BOOLEAN DEFAULT 0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_name, target_program, dependency_type)
                )
            """)
            
            # Create indexes for inbound_interfaces
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inbound_target 
                ON inbound_interfaces(target_program)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inbound_source 
                ON inbound_interfaces(source_name)
            """)
            
            # Create outbound_interfaces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outbound_interfaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_name TEXT NOT NULL UNIQUE,
                    reason TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for outbound_interfaces
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_outbound_program 
                ON outbound_interfaces(program_name)
            """)
            
            self.db.commit()
            
            logger.info("External interface tables created successfully")
            
        except sqlite3.Error as e:
            self.db.rollback()
            logger.error(f"Failed to create external interface tables: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            result = cursor.fetchone()
            return result is not None
            
        except sqlite3.Error as e:
            logger.error(f"Error checking if table {table_name} exists: {e}")
            return False
    
    def get_schema_version(self) -> str:
        """
        Get current schema version for migration tracking.
        
        Returns:
            Schema version string (e.g., "1.0.0")
        """
        return self.SCHEMA_VERSION
    
    def drop_tables(self) -> None:
        """
        Drop inbound_interfaces and outbound_interfaces tables.
        
        WARNING: This will delete all data in these tables.
        Use with caution - typically only for testing or cleanup.
        
        Raises:
            sqlite3.Error: If table drop fails
        """
        cursor = self.db.cursor()
        
        try:
            cursor.execute("DROP TABLE IF EXISTS inbound_interfaces")
            cursor.execute("DROP TABLE IF EXISTS outbound_interfaces")
            
            self.db.commit()
            
            logger.info("External interface tables dropped successfully")
            
        except sqlite3.Error as e:
            self.db.rollback()
            logger.error(f"Failed to drop external interface tables: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Optional[list]:
        """
        Get schema information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information tuples, or None if table doesn't exist
        """
        if not self.table_exists(table_name):
            return None
        
        cursor = self.db.cursor()
        
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return None
