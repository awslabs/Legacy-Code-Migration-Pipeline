"""
Query Profiler

This module provides query profiling and optimization tools for identifying
and optimizing slow database queries in the migration flow system.
"""

import time
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QueryProfile:
    """Profile data for a single query execution."""
    query: str
    params: tuple
    execution_time: float
    row_count: int
    timestamp: datetime
    explain_plan: Optional[str] = None


class QueryProfiler:
    """
    Query profiler for tracking and analyzing database query performance.
    
    This class provides:
    - Query execution timing
    - Query plan analysis (EXPLAIN QUERY PLAN)
    - Slow query detection
    - Performance statistics
    - Optimization recommendations
    """
    
    def __init__(
        self,
        db_connection: sqlite3.Connection,
        slow_query_threshold: float = 1.0,
        enable_explain: bool = False
    ):
        """
        Initialize the query profiler.
        
        Args:
            db_connection: SQLite database connection
            slow_query_threshold: Threshold in seconds for slow query detection (default: 1.0)
            enable_explain: Whether to capture EXPLAIN QUERY PLAN for queries (default: False)
        """
        self.db = db_connection
        self.slow_query_threshold = slow_query_threshold
        self.enable_explain = enable_explain
        
        # Query profiles storage
        self.profiles: List[QueryProfile] = []
        
        # Statistics
        self.total_queries = 0
        self.total_time = 0.0
        self.slow_queries = 0
    
    def profile_query(
        self,
        query: str,
        params: tuple = (),
        fetch_all: bool = True
    ) -> tuple:
        """
        Execute and profile a query.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_all: Whether to fetch all results (default: True)
            
        Returns:
            Tuple of (results, execution_time)
        """
        cursor = self.db.cursor()
        
        # Get explain plan if enabled
        explain_plan = None
        if self.enable_explain and query.strip().upper().startswith('SELECT'):
            explain_plan = self._get_explain_plan(query, params)
        
        # Execute and time the query
        start_time = time.time()
        cursor.execute(query, params)
        
        if fetch_all:
            results = cursor.fetchall()
        else:
            results = cursor.fetchone()
        
        execution_time = time.time() - start_time
        
        # Record profile
        row_count = len(results) if fetch_all and results else (1 if results else 0)
        profile = QueryProfile(
            query=query,
            params=params,
            execution_time=execution_time,
            row_count=row_count,
            timestamp=datetime.now(),
            explain_plan=explain_plan
        )
        
        self.profiles.append(profile)
        
        # Update statistics
        self.total_queries += 1
        self.total_time += execution_time
        
        if execution_time >= self.slow_query_threshold:
            self.slow_queries += 1
            logger.warning(
                f"Slow query detected ({execution_time:.3f}s): "
                f"{query[:100]}{'...' if len(query) > 100 else ''}"
            )
        
        return results, execution_time
    
    def _get_explain_plan(self, query: str, params: tuple) -> str:
        """Get EXPLAIN QUERY PLAN for a query."""
        cursor = self.db.cursor()
        
        try:
            cursor.execute(f"EXPLAIN QUERY PLAN {query}", params)
            plan_rows = cursor.fetchall()
            
            # Format explain plan
            plan_lines = []
            for row in plan_rows:
                # SQLite EXPLAIN QUERY PLAN returns: (id, parent, notused, detail)
                plan_lines.append(f"  {row[3]}")
            
            return "\n".join(plan_lines)
        
        except Exception as e:
            logger.debug(f"Failed to get explain plan: {e}")
            return None
    
    def get_slow_queries(self, limit: int = 10) -> List[QueryProfile]:
        """
        Get the slowest queries.
        
        Args:
            limit: Maximum number of queries to return (default: 10)
            
        Returns:
            List of QueryProfile objects sorted by execution time (descending)
        """
        sorted_profiles = sorted(
            self.profiles,
            key=lambda p: p.execution_time,
            reverse=True
        )
        
        return sorted_profiles[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get profiling statistics.
        
        Returns:
            Dictionary with profiling statistics
        """
        avg_time = self.total_time / self.total_queries if self.total_queries > 0 else 0.0
        slow_query_rate = self.slow_queries / self.total_queries if self.total_queries > 0 else 0.0
        
        return {
            'total_queries': self.total_queries,
            'total_time': self.total_time,
            'average_time': avg_time,
            'slow_queries': self.slow_queries,
            'slow_query_rate': slow_query_rate,
            'slow_query_threshold': self.slow_query_threshold
        }
    
    def print_report(self, top_n: int = 10) -> None:
        """
        Print a profiling report.
        
        Args:
            top_n: Number of slowest queries to include in report (default: 10)
        """
        stats = self.get_statistics()
        
        print("\n" + "=" * 80)
        print("QUERY PROFILING REPORT")
        print("=" * 80)
        
        print(f"\nTotal Queries: {stats['total_queries']}")
        print(f"Total Time: {stats['total_time']:.3f}s")
        print(f"Average Time: {stats['average_time']:.3f}s")
        print(f"Slow Queries: {stats['slow_queries']} ({stats['slow_query_rate']:.1%})")
        print(f"Slow Query Threshold: {stats['slow_query_threshold']}s")
        
        # Print slowest queries
        slow_queries = self.get_slow_queries(top_n)
        
        if slow_queries:
            print(f"\n{'-' * 80}")
            print(f"TOP {len(slow_queries)} SLOWEST QUERIES")
            print(f"{'-' * 80}")
            
            for i, profile in enumerate(slow_queries, 1):
                print(f"\n{i}. Execution Time: {profile.execution_time:.3f}s")
                print(f"   Row Count: {profile.row_count}")
                print(f"   Query: {profile.query[:200]}{'...' if len(profile.query) > 200 else ''}")
                
                if profile.explain_plan:
                    print(f"   Explain Plan:")
                    print(profile.explain_plan)
        
        print("\n" + "=" * 80 + "\n")
    
    def get_optimization_recommendations(self) -> List[str]:
        """
        Get optimization recommendations based on profiling data.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Analyze slow queries
        slow_queries = self.get_slow_queries(20)
        
        # Check for missing indexes
        for profile in slow_queries:
            if profile.explain_plan and 'SCAN' in profile.explain_plan.upper():
                recommendations.append(
                    f"Consider adding index for query: {profile.query[:100]}... "
                    f"(contains table scan)"
                )
        
        # Check for queries without WHERE clauses
        for profile in slow_queries:
            query_upper = profile.query.upper()
            if 'SELECT' in query_upper and 'WHERE' not in query_upper:
                recommendations.append(
                    f"Query without WHERE clause may be slow: {profile.query[:100]}..."
                )
        
        # Check for queries with many JOINs
        for profile in slow_queries:
            join_count = profile.query.upper().count('JOIN')
            if join_count > 5:
                recommendations.append(
                    f"Query with {join_count} JOINs may benefit from denormalization: "
                    f"{profile.query[:100]}..."
                )
        
        # Check for high row count queries
        for profile in slow_queries:
            if profile.row_count > 10000:
                recommendations.append(
                    f"Query returning {profile.row_count} rows may benefit from pagination: "
                    f"{profile.query[:100]}..."
                )
        
        # General recommendations based on statistics
        stats = self.get_statistics()
        
        if stats['slow_query_rate'] > 0.1:
            recommendations.append(
                f"High slow query rate ({stats['slow_query_rate']:.1%}). "
                f"Consider reviewing database indexes and query patterns."
            )
        
        if stats['average_time'] > 0.5:
            recommendations.append(
                f"High average query time ({stats['average_time']:.3f}s). "
                f"Consider using batch operations and caching."
            )
        
        return recommendations
    
    def reset(self) -> None:
        """Reset profiling data."""
        self.profiles.clear()
        self.total_queries = 0
        self.total_time = 0.0
        self.slow_queries = 0
        
        logger.info("Query profiler reset")


class QueryOptimizer:
    """
    Query optimizer for suggesting and applying query optimizations.
    
    This class provides:
    - Index recommendations
    - Query rewriting suggestions
    - Automatic index creation
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize the query optimizer.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        self.cursor = db_connection.cursor()
    
    def analyze_table_indexes(self, table_name: str) -> Dict[str, Any]:
        """
        Analyze indexes for a table.
        
        Args:
            table_name: Table name to analyze
            
        Returns:
            Dictionary with index analysis
        """
        # Get existing indexes
        self.cursor.execute(f"PRAGMA index_list('{table_name}')")
        indexes = self.cursor.fetchall()
        
        # Get table info
        self.cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns = self.cursor.fetchall()
        
        # Analyze index coverage
        indexed_columns = set()
        for index in indexes:
            index_name = index[1]
            self.cursor.execute(f"PRAGMA index_info('{index_name}')")
            index_columns = self.cursor.fetchall()
            
            for col in index_columns:
                indexed_columns.add(col[2])  # Column name
        
        # Find unindexed columns
        all_columns = {col[1] for col in columns}
        unindexed_columns = all_columns - indexed_columns
        
        return {
            'table_name': table_name,
            'total_columns': len(all_columns),
            'indexed_columns': len(indexed_columns),
            'unindexed_columns': list(unindexed_columns),
            'indexes': [idx[1] for idx in indexes]
        }
    
    def recommend_indexes(self, profiler: QueryProfiler) -> List[str]:
        """
        Recommend indexes based on profiling data.
        
        Args:
            profiler: QueryProfiler instance with profiling data
            
        Returns:
            List of index creation SQL statements
        """
        recommendations = []
        
        # Analyze slow queries for index opportunities
        slow_queries = profiler.get_slow_queries(20)
        
        for profile in slow_queries:
            # Look for WHERE clauses without indexes
            if 'WHERE' in profile.query.upper():
                # Simple heuristic: extract column names from WHERE clause
                # This is a simplified approach; a full SQL parser would be better
                where_clause = profile.query.upper().split('WHERE')[1].split('ORDER')[0]
                
                # Look for common patterns like "column_name ="
                import re
                column_matches = re.findall(r'(\w+)\s*=', where_clause)
                
                for column in column_matches:
                    # Check if this column might benefit from an index
                    if profile.execution_time > 0.5:
                        recommendations.append(
                            f"-- Consider adding index for column: {column}\n"
                            f"-- Query time: {profile.execution_time:.3f}s\n"
                            f"-- CREATE INDEX IF NOT EXISTS idx_{column} ON table_name({column});"
                        )
        
        return recommendations
    
    def create_recommended_indexes(self) -> int:
        """
        Create recommended indexes for migration flow tables.
        
        Returns:
            Number of indexes created
        """
        # Define recommended indexes for migration flow tables
        recommended_indexes = [
            # migration_flows indexes
            "CREATE INDEX IF NOT EXISTS idx_migration_flows_entry_type ON migration_flows(primary_entry_type)",
            "CREATE INDEX IF NOT EXISTS idx_migration_flows_complexity_tier ON migration_flows(complexity_tier)",
            "CREATE INDEX IF NOT EXISTS idx_migration_flows_business_domain ON migration_flows(business_domain)",
            
            # flow_entry_types indexes
            "CREATE INDEX IF NOT EXISTS idx_flow_entry_types_flow_id ON flow_entry_types(flow_id)",
            "CREATE INDEX IF NOT EXISTS idx_flow_entry_types_entry_type ON flow_entry_types(entry_type)",
            "CREATE INDEX IF NOT EXISTS idx_flow_entry_types_caller ON flow_entry_types(caller_source)",
            
            # flow_scope indexes
            "CREATE INDEX IF NOT EXISTS idx_flow_scope_artifact_type ON flow_scope(artifact_type)",
            "CREATE INDEX IF NOT EXISTS idx_flow_scope_artifact_name ON flow_scope(artifact_name)",
            "CREATE INDEX IF NOT EXISTS idx_flow_scope_flow_artifact ON flow_scope(flow_id, artifact_type)",
            
            # flow_interfaces indexes
            "CREATE INDEX IF NOT EXISTS idx_flow_interfaces_flow_id ON flow_interfaces(flow_id)",
            "CREATE INDEX IF NOT EXISTS idx_flow_interfaces_direction ON flow_interfaces(direction)",
            "CREATE INDEX IF NOT EXISTS idx_flow_interfaces_type ON flow_interfaces(interface_type)",
            "CREATE INDEX IF NOT EXISTS idx_flow_interfaces_source ON flow_interfaces(source)",
            "CREATE INDEX IF NOT EXISTS idx_flow_interfaces_target ON flow_interfaces(target)",
            
            # flow_data_operations indexes
            "CREATE INDEX IF NOT EXISTS idx_flow_data_ops_flow_id ON flow_data_operations(flow_id)",
            "CREATE INDEX IF NOT EXISTS idx_flow_data_ops_category ON flow_data_operations(operation_category)",
            "CREATE INDEX IF NOT EXISTS idx_flow_data_ops_target ON flow_data_operations(target)",
            "CREATE INDEX IF NOT EXISTS idx_flow_data_ops_program ON flow_data_operations(program)",
            
            # flow_dependencies indexes
            "CREATE INDEX IF NOT EXISTS idx_flow_deps_flow_id ON flow_dependencies(flow_id)",
            "CREATE INDEX IF NOT EXISTS idx_flow_deps_depends_on ON flow_dependencies(depends_on_flow_id)",
            "CREATE INDEX IF NOT EXISTS idx_flow_deps_type ON flow_dependencies(dependency_type)"
        ]
        
        created_count = 0
        
        try:
            for index_sql in recommended_indexes:
                try:
                    self.cursor.execute(index_sql)
                    created_count += 1
                except sqlite3.OperationalError as e:
                    # Index might already exist
                    logger.debug(f"Index creation skipped: {e}")
            
            self.db.commit()
            logger.info(f"Created {created_count} indexes")
            return created_count
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create indexes: {e}")
            raise
