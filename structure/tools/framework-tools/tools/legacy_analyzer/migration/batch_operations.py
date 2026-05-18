"""
Batch Database Operations

This module provides batch database operations for efficient bulk inserts,
updates, and deletes in the migration flow system.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BatchDatabaseOperations:
    """
    Batch database operations for migration flow data.
    
    This class provides methods for:
    - Batch inserts with transaction management
    - Bulk updates
    - Efficient batch deletes
    - Transaction batching for large datasets
    """
    
    def __init__(self, db_connection: sqlite3.Connection, batch_size: int = 1000):
        """
        Initialize batch operations.
        
        Args:
            db_connection: SQLite database connection
            batch_size: Number of records to process in each batch (default: 1000)
        """
        self.db = db_connection
        self.batch_size = batch_size
        self.cursor = db_connection.cursor()
    
    def batch_insert_flows(self, flows: List[Dict]) -> int:
        """
        Batch insert multiple flows with all related data.
        
        This method inserts flows in batches with transaction management
        to ensure atomicity and improve performance.
        
        Args:
            flows: List of flow dictionaries with complete data
            
        Returns:
            Number of flows successfully inserted
            
        Raises:
            Exception: If batch insert fails
        """
        if not flows:
            return 0
        
        total_inserted = 0
        
        try:
            # Process flows in batches
            for i in range(0, len(flows), self.batch_size):
                batch = flows[i:i + self.batch_size]
                
                # Start transaction for this batch
                self.cursor.execute("BEGIN TRANSACTION")
                
                try:
                    for flow in batch:
                        self._insert_single_flow(flow)
                        total_inserted += 1
                    
                    # Commit batch
                    self.db.commit()
                    logger.debug(f"Inserted batch of {len(batch)} flows")
                
                except Exception as e:
                    # Rollback batch on error
                    self.db.rollback()
                    logger.error(f"Failed to insert batch: {e}")
                    raise
            
            logger.info(f"Batch inserted {total_inserted} flows")
            return total_inserted
        
        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            raise
    
    def _insert_single_flow(self, flow: Dict) -> None:
        """Insert a single flow with all related data."""
        flow_id = flow['flowId']
        
        # Insert flow metadata
        self._insert_flow_metadata(flow)
        
        # Insert entry types
        if 'entryPoint' in flow and 'types' in flow['entryPoint']:
            self._insert_entry_types(flow_id, flow['entryPoint']['types'])
        
        # Insert scope
        if 'scope' in flow:
            self._insert_scope(flow_id, flow['scope'])
        
        # Insert interfaces
        if 'interfaces' in flow:
            self._insert_interfaces(flow_id, flow['interfaces'])
        
        # Insert data operations
        if 'dataOperations' in flow:
            self._insert_data_operations(flow_id, flow['dataOperations'])
        
        # Insert dependencies
        if 'dependencies' in flow:
            self._insert_dependencies(flow_id, flow['dependencies'])
    
    def _insert_flow_metadata(self, flow: Dict) -> None:
        """Insert flow metadata."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO migration_flows (
                flow_id,
                name,
                entry_program,
                primary_entry_type,
                total_programs,
                total_copybooks,
                total_datasets,
                complexity_total_lines,
                complexity_cyclomatic,
                complexity_score,
                complexity_tier,
                priority,
                business_domain,
                created_date,
                updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flow['flowId'],
            flow.get('name', ''),
            flow['entryPoint']['program'],
            flow['entryPoint'].get('primaryType'),
            flow['complexity']['totalPrograms'],
            len(flow.get('scope', {}).get('copybooks', [])),
            len(flow.get('scope', {}).get('datasets', [])),
            flow['complexity']['totalLines'],
            flow['complexity']['cyclomaticComplexity'],
            flow['complexity']['compositeScore'],
            flow['complexity']['tier'],
            flow.get('priority'),
            flow.get('businessDomain'),
            current_date,
            current_date
        ))
    
    def _insert_entry_types(self, flow_id: str, entry_types: List[Dict]) -> None:
        """Batch insert entry types."""
        batch_data = []
        
        for entry_type in entry_types:
            type_name = entry_type['type']
            callers = entry_type.get('callers', [])
            
            for caller in callers:
                caller_source = caller.get('source', '')
                metadata = caller.get('metadata', {})
                metadata_json = json.dumps(metadata) if metadata else None
                
                batch_data.append((flow_id, type_name, caller_source, metadata_json))
        
        if batch_data:
            self.cursor.executemany("""
                INSERT OR REPLACE INTO flow_entry_types (
                    flow_id,
                    entry_type,
                    caller_source,
                    metadata_json
                ) VALUES (?, ?, ?, ?)
            """, batch_data)
    
    def _insert_scope(self, flow_id: str, scope: Dict[str, List[str]]) -> None:
        """Batch insert scope artifacts."""
        batch_data = []
        
        for program in scope.get('programs', []):
            batch_data.append((flow_id, 'PROGRAM', program))
        
        for copybook in scope.get('copybooks', []):
            batch_data.append((flow_id, 'COPYBOOK', copybook))
        
        for dataset in scope.get('datasets', []):
            batch_data.append((flow_id, 'DATASET', dataset))
        
        if batch_data:
            self.cursor.executemany("""
                INSERT OR REPLACE INTO flow_scope (
                    flow_id,
                    artifact_type,
                    artifact_name
                ) VALUES (?, ?, ?)
            """, batch_data)
    
    def _insert_interfaces(self, flow_id: str, interfaces: Dict[str, List[Dict]]) -> None:
        """Batch insert interfaces."""
        batch_data = []
        
        for interface in interfaces.get('inbound', []):
            metadata = interface.get('metadata', {})
            metadata_json = json.dumps(metadata) if metadata else None
            
            batch_data.append((
                flow_id,
                'INBOUND',
                interface.get('type', 'UNKNOWN'),
                interface.get('source', ''),
                interface.get('target', ''),
                interface.get('external', False),
                metadata_json
            ))
        
        for interface in interfaces.get('outbound', []):
            metadata = interface.get('metadata', {})
            metadata_json = json.dumps(metadata) if metadata else None
            
            batch_data.append((
                flow_id,
                'OUTBOUND',
                interface.get('type', 'UNKNOWN'),
                interface.get('source', ''),
                interface.get('target', ''),
                interface.get('external', True),
                metadata_json
            ))
        
        if batch_data:
            self.cursor.executemany("""
                INSERT INTO flow_interfaces (
                    flow_id,
                    direction,
                    interface_type,
                    source,
                    target,
                    external,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
    
    def _insert_data_operations(self, flow_id: str, data_operations: Dict[str, List[Dict]]) -> None:
        """Batch insert data operations."""
        batch_data = []
        
        for db_op in data_operations.get('databases', []):
            batch_data.append((
                flow_id,
                'DATABASE',
                db_op.get('operation', 'UNKNOWN'),
                db_op.get('type', 'UNKNOWN'),
                db_op.get('target', ''),
                db_op.get('program', ''),
                None
            ))
        
        for ds_op in data_operations.get('datasets', []):
            programs = ds_op.get('programs', [])
            
            for program in programs:
                batch_data.append((
                    flow_id,
                    'DATASET',
                    'ACCESS',
                    None,
                    ds_op.get('name', ''),
                    program,
                    ds_op.get('mode', 'UNKNOWN')
                ))
        
        if batch_data:
            self.cursor.executemany("""
                INSERT INTO flow_data_operations (
                    flow_id,
                    operation_category,
                    operation_type,
                    db_type,
                    target,
                    program,
                    mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
    
    def _insert_dependencies(self, flow_id: str, dependencies: Dict[str, List[str]]) -> None:
        """Batch insert dependencies."""
        batch_data = []
        
        for required_flow_id in dependencies.get('requiredFlows', []):
            batch_data.append((flow_id, required_flow_id, 'REQUIRED'))
        
        for dependent_flow_id in dependencies.get('dependentFlows', []):
            batch_data.append((dependent_flow_id, flow_id, 'REQUIRED'))
        
        if batch_data:
            self.cursor.executemany("""
                INSERT OR REPLACE INTO flow_dependencies (
                    flow_id,
                    depends_on_flow_id,
                    dependency_type
                ) VALUES (?, ?, ?)
            """, batch_data)
    
    def batch_update_flow_metadata(self, updates: List[Tuple[str, Dict]]) -> int:
        """
        Batch update flow metadata.
        
        Args:
            updates: List of tuples (flow_id, update_dict)
                    where update_dict contains fields to update
            
        Returns:
            Number of flows updated
        """
        if not updates:
            return 0
        
        updated_count = 0
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            
            for flow_id, update_dict in updates:
                # Build UPDATE query dynamically based on fields to update
                set_clauses = []
                values = []
                
                for field, value in update_dict.items():
                    set_clauses.append(f"{field} = ?")
                    values.append(value)
                
                # Always update updated_date
                set_clauses.append("updated_date = ?")
                values.append(current_date)
                
                # Add flow_id for WHERE clause
                values.append(flow_id)
                
                query = f"""
                    UPDATE migration_flows
                    SET {', '.join(set_clauses)}
                    WHERE flow_id = ?
                """
                
                self.cursor.execute(query, values)
                updated_count += 1
            
            self.db.commit()
            logger.info(f"Batch updated {updated_count} flows")
            return updated_count
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Batch update failed: {e}")
            raise
    
    def batch_delete_flows(self, flow_ids: List[str]) -> int:
        """
        Batch delete flows and all related data.
        
        This method deletes flows in batches with transaction management.
        All related data (entry types, scope, interfaces, etc.) is deleted
        automatically via CASCADE constraints.
        
        Args:
            flow_ids: List of flow IDs to delete
            
        Returns:
            Number of flows deleted
        """
        if not flow_ids:
            return 0
        
        deleted_count = 0
        
        try:
            # Process deletions in batches
            for i in range(0, len(flow_ids), self.batch_size):
                batch = flow_ids[i:i + self.batch_size]
                
                # Start transaction for this batch
                self.cursor.execute("BEGIN TRANSACTION")
                
                try:
                    placeholders = ','.join('?' * len(batch))
                    self.cursor.execute(f"""
                        DELETE FROM migration_flows
                        WHERE flow_id IN ({placeholders})
                    """, batch)
                    
                    deleted_count += self.cursor.rowcount
                    
                    # Commit batch
                    self.db.commit()
                    logger.debug(f"Deleted batch of {len(batch)} flows")
                
                except Exception as e:
                    # Rollback batch on error
                    self.db.rollback()
                    logger.error(f"Failed to delete batch: {e}")
                    raise
            
            logger.info(f"Batch deleted {deleted_count} flows")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Batch delete failed: {e}")
            raise
    
    def batch_upsert_complexity(self, complexity_data: List[Tuple[str, Dict]]) -> int:
        """
        Batch upsert (insert or update) complexity data.
        
        Args:
            complexity_data: List of tuples (program_name, complexity_dict)
            
        Returns:
            Number of records upserted
        """
        if not complexity_data:
            return 0
        
        batch_data = []
        
        for program_name, complexity in complexity_data.items():
            batch_data.append((
                program_name,
                complexity.get('lines_of_code', 0),
                complexity.get('cyclomatic_complexity', 0),
                complexity.get('composite_score', 0.0),
                complexity.get('tier', 'UNKNOWN')
            ))
        
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            
            self.cursor.executemany("""
                INSERT OR REPLACE INTO complexity_metrics (
                    program_name,
                    lines_of_code,
                    cyclomatic_complexity,
                    composite_score,
                    tier
                ) VALUES (?, ?, ?, ?, ?)
            """, batch_data)
            
            self.db.commit()
            logger.info(f"Batch upserted {len(batch_data)} complexity records")
            return len(batch_data)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Batch upsert complexity failed: {e}")
            raise
    
    def vacuum_database(self) -> None:
        """
        Vacuum the database to reclaim space and optimize performance.
        
        This should be called after large batch deletions.
        """
        try:
            logger.info("Vacuuming database...")
            self.cursor.execute("VACUUM")
            logger.info("Database vacuumed successfully")
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            raise
    
    def analyze_database(self) -> None:
        """
        Analyze the database to update query optimizer statistics.
        
        This should be called after large batch inserts or updates.
        """
        try:
            logger.info("Analyzing database...")
            self.cursor.execute("ANALYZE")
            logger.info("Database analyzed successfully")
        except Exception as e:
            logger.error(f"Failed to analyze database: {e}")
            raise
