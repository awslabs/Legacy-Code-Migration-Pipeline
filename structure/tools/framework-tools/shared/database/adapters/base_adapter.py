"""Base database interface for different database backends."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseDatabaseAdapter(ABC):
    """Abstract base class for database adapters."""
    
    @abstractmethod
    def connect(self):
        """Establish database connection."""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection."""
        pass
    
    @abstractmethod
    def create_table(self, table_name: str, table_def: Dict[str, Any]):
        """
        Create a table based on schema definition.
        
        Args:
            table_name: Name of the table
            table_def: Table definition from schema (columns, indexes, foreign_keys)
        """
        pass
    
    @abstractmethod
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]):
        """
        Insert rows into a table.
        
        Args:
            table_name: Name of the table
            rows: List of row dictionaries with column names as keys
        """
        pass
    
    @abstractmethod
    def insert_and_get_id(self, table_name: str, row: Dict[str, Any]) -> int:
        """
        Insert a single row and return its ID.
        
        Args:
            table_name: Name of the table
            row: Row dictionary with column names as keys
            
        Returns:
            The ID of the inserted row
        """
        pass
    
    @abstractmethod
    def commit(self):
        """Commit current transaction."""
        pass
    
    @abstractmethod
    def rollback(self):
        """Rollback current transaction."""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        pass
    
    @abstractmethod
    def get_row_count(self, table_name: str) -> int:
        """Get number of rows in a table."""
        pass
    
    @abstractmethod
    def execute(self, sql: str, params: tuple = None):
        """
        Execute a SQL statement.
        
        Args:
            sql: SQL statement to execute
            params: Optional parameters for the SQL statement
            
        Returns:
            Cursor object for fetching results
        """
        pass
    
    @abstractmethod
    def executemany(self, sql: str, params_list: list):
        """
        Execute a SQL statement multiple times with different parameters.
        
        Args:
            sql: SQL statement to execute
            params_list: List of parameter tuples
            
        Returns:
            Cursor object
        """
        pass
    
    @abstractmethod
    def cursor(self):
        """
        Return the database cursor for direct access.
        
        Returns:
            Database cursor object
        """
        pass
    
    @property
    @abstractmethod
    def dialect(self) -> str:
        """Return database dialect name (e.g., 'sqlite', 'postgresql', 'duckdb')."""
        pass
