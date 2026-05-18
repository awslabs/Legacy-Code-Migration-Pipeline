"""Database utility functions for common operations.

This module provides reusable database utility functions to reduce code duplication
across the codebase.
"""

import sqlite3
import logging
from typing import Optional, List, Set


logger = logging.getLogger(__name__)


def check_table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    """
    Check if a table exists in the SQLite database.
    
    Args:
        connection: SQLite database connection
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> if check_table_exists(conn, 'inventory_cics'):
        ...     print("Table exists")
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        result = cursor.fetchone() is not None
        logger.debug(f"Table '{table_name}' exists: {result}")
        return result
    except sqlite3.Error as e:
        logger.warning(f"Error checking for table '{table_name}': {e}")
        return False


def get_table_columns(connection: sqlite3.Connection, table_name: str) -> List[str]:
    """
    Get list of column names for a table.
    
    Args:
        connection: SQLite database connection
        table_name: Name of the table
        
    Returns:
        List of column names, empty list if table doesn't exist
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> columns = get_table_columns(conn, 'inventory_cics')
        >>> print(columns)
        ['resource_name', 'resource_type', 'group_name', ...]
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        logger.debug(f"Table '{table_name}' has {len(columns)} columns")
        return columns
    except sqlite3.Error as e:
        logger.warning(f"Error getting columns for table '{table_name}': {e}")
        return []


def table_has_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str
) -> bool:
    """
    Check if a table has a specific column.
    
    Args:
        connection: SQLite database connection
        table_name: Name of the table
        column_name: Name of the column to check
        
    Returns:
        True if column exists, False otherwise
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> if table_has_column(conn, 'inventory_cics', 'dataset_name'):
        ...     print("Column exists")
    """
    columns = get_table_columns(connection, table_name)
    return column_name in columns


def get_distinct_values(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    where_clause: Optional[str] = None
) -> Set[str]:
    """
    Get distinct values from a column.
    
    Args:
        connection: SQLite database connection
        table_name: Name of the table
        column_name: Name of the column
        where_clause: Optional WHERE clause (without 'WHERE' keyword)
        
    Returns:
        Set of distinct values
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> groups = get_distinct_values(conn, 'inventory_cics', 'group_name')
        >>> print(groups)
        {'CARDDEMO', 'PAYROLL', 'BILLING'}
    """
    try:
        cursor = connection.cursor()
        query = f"SELECT DISTINCT {column_name} FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        cursor.execute(query)
        values = {row[0] for row in cursor.fetchall() if row[0] is not None}
        logger.debug(
            f"Found {len(values)} distinct values in "
            f"{table_name}.{column_name}"
        )
        return values
    except sqlite3.Error as e:
        logger.error(
            f"Error getting distinct values from "
            f"{table_name}.{column_name}: {e}"
        )
        return set()


def count_rows(
    connection: sqlite3.Connection,
    table_name: str,
    where_clause: Optional[str] = None
) -> int:
    """
    Count rows in a table.
    
    Args:
        connection: SQLite database connection
        table_name: Name of the table
        where_clause: Optional WHERE clause (without 'WHERE' keyword)
        
    Returns:
        Number of rows
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> count = count_rows(conn, 'inventory_cics', "status='ENABLED'")
        >>> print(f"Found {count} enabled resources")
    """
    try:
        cursor = connection.cursor()
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        cursor.execute(query)
        count = cursor.fetchone()[0]
        logger.debug(f"Table '{table_name}' has {count} rows")
        return count
    except sqlite3.Error as e:
        logger.error(f"Error counting rows in '{table_name}': {e}")
        return 0


def execute_query_safe(
    connection: sqlite3.Connection,
    query: str,
    params: tuple = ()
) -> List[tuple]:
    """
    Execute a query safely with error handling.
    
    Args:
        connection: SQLite database connection
        query: SQL query to execute
        params: Query parameters (for parameterized queries)
        
    Returns:
        List of result tuples, empty list on error
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> results = execute_query_safe(
        ...     conn,
        ...     "SELECT * FROM inventory_cics WHERE group_name=?",
        ...     ('CARDDEMO',)
        ... )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        logger.debug(f"Query returned {len(results)} rows")
        return results
    except sqlite3.Error as e:
        logger.error(f"Error executing query: {e}")
        logger.debug(f"Query: {query}")
        logger.debug(f"Params: {params}")
        return []


def batch_insert(
    connection: sqlite3.Connection,
    table_name: str,
    columns: List[str],
    rows: List[tuple],
    batch_size: int = 1000
) -> int:
    """
    Insert multiple rows in batches for better performance.
    
    Args:
        connection: SQLite database connection
        table_name: Name of the table
        columns: List of column names
        rows: List of row tuples to insert
        batch_size: Number of rows per batch
        
    Returns:
        Number of rows inserted
        
    Example:
        >>> conn = sqlite3.connect('analysis.db')
        >>> rows = [
        ...     ('CAUP', 'TRANSACTION', 'CARDDEMO', 'ENABLED'),
        ...     ('CBIL', 'TRANSACTION', 'BILLING', 'ENABLED'),
        ... ]
        >>> count = batch_insert(
        ...     conn,
        ...     'inventory_cics',
        ...     ['resource_name', 'resource_type', 'group_name', 'status'],
        ...     rows
        ... )
    """
    if not rows:
        return 0
    
    try:
        cursor = connection.cursor()
        placeholders = ','.join(['?'] * len(columns))
        column_list = ','.join(columns)
        query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
        
        inserted = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            cursor.executemany(query, batch)
            inserted += len(batch)
            
            if i % (batch_size * 10) == 0 and i > 0:
                logger.debug(f"Inserted {inserted}/{len(rows)} rows")
        
        connection.commit()
        logger.info(f"Successfully inserted {inserted} rows into {table_name}")
        return inserted
        
    except sqlite3.Error as e:
        logger.error(f"Error during batch insert into {table_name}: {e}")
        connection.rollback()
        return 0
