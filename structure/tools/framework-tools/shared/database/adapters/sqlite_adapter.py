"""Shared SQLite database adapter for use across all tools."""

import sqlite3
from typing import Dict, List, Any
from .base_adapter import BaseDatabaseAdapter


class SQLiteAdapter(BaseDatabaseAdapter):
    """
    Shared SQLite database adapter implementation.
    
    This adapter provides a common interface for SQLite database operations
    """
    
    def __init__(self, db_file: str = 'data.db'):
        """
        Initialize SQLite adapter.
        
        Args:
            db_file: Path to SQLite database file
        """
        self.db_file = db_file
        self.conn = None
        self._cursor = None
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_file)
        self._cursor = self.conn.cursor()
        print(f"✓ Connected to SQLite: {self.db_file}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print(f"✓ Database closed: {self.db_file}")
    
    def create_table(self, table_name: str, table_def: Dict[str, Any]):
        """Create a table based on schema definition."""
        columns = table_def.get('columns', [])
        indexes = table_def.get('indexes', [])
        foreign_keys = table_def.get('foreign_keys', [])
        
        # Build column definitions
        col_defs = []
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
                if col.get('autoincrement'):
                    col_def += " AUTOINCREMENT"
            
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            
            # Add default value if specified
            if 'default' in col:
                col_def += f" DEFAULT {col['default']}"
            
            col_defs.append(col_def)
        
        # Add foreign keys
        for fk in foreign_keys:
            col_defs.append(f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']}")
        
        # Create table
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  "
        create_sql += ",\n  ".join(col_defs)
        create_sql += "\n)"
        
        self._cursor.execute(create_sql)
        
        # Create indexes
        for idx in indexes:
            idx_name = idx.get('name', f"idx_{table_name}_{'_'.join(idx['columns'])}")
            cols = ', '.join(idx['columns'])
            unique = 'UNIQUE ' if idx.get('unique') else ''
            self._cursor.execute(f"CREATE {unique}INDEX IF NOT EXISTS {idx_name} ON {table_name}({cols})")
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]):
        """Insert rows into a table."""
        if not rows:
            return
        
        # Get column names from first row
        columns = list(rows[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        col_names = ', '.join(columns)
        
        insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        
        # Convert rows to tuples
        values = [tuple(row[col] for col in columns) for row in rows]
        
        self._cursor.executemany(insert_sql, values)
    
    def insert_and_get_id(self, table_name: str, row: Dict[str, Any]) -> int:
        """Insert a single row and return its ID."""
        columns = list(row.keys())
        placeholders = ', '.join(['?' for _ in columns])
        col_names = ', '.join(columns)
        
        insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        values = tuple(row[col] for col in columns)
        
        self._cursor.execute(insert_sql, values)
        return self._cursor.lastrowid
    
    def commit(self):
        """Commit current transaction."""
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """Rollback current transaction."""
        if self.conn:
            self.conn.rollback()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        self._cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return self._cursor.fetchone() is not None
    
    def get_row_count(self, table_name: str) -> int:
        """Get number of rows in a table."""
        self._cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return self._cursor.fetchone()[0]
    
    def execute(self, sql: str, params: tuple = None):
        """
        Execute a SQL statement.
        
        Args:
            sql: SQL statement to execute
            params: Optional parameters for the SQL statement
            
        Returns:
            Cursor object for fetching results
        """
        if params:
            return self._cursor.execute(sql, params)
        else:
            return self._cursor.execute(sql)
    
    def executemany(self, sql: str, params_list: list):
        """
        Execute a SQL statement multiple times with different parameters.
        
        Args:
            sql: SQL statement to execute
            params_list: List of parameter tuples
            
        Returns:
            Cursor object
        """
        return self._cursor.executemany(sql, params_list)
    
    def cursor(self):
        """
        Return the database cursor for direct access.
        
        This method provides compatibility with code that expects a
        sqlite3.Connection-like interface with a cursor() method.
        
        Returns:
            sqlite3.Cursor object
        """
        return self._cursor
    
    @property
    def dialect(self) -> str:
        """Return database dialect name."""
        return 'sqlite'
