"""
Optimized Database Queries

This module provides optimized SQL queries using JOINs instead of multiple
SELECT statements to improve performance for migration flow export.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class OptimizedFlowQueries:
    """
    Optimized database queries for migration flow export.
    
    This class provides methods that use JOIN queries to fetch related data
    in a single database round-trip instead of multiple SELECT statements.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize optimized queries.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        self.cursor = db_connection.cursor()
    
    def query_flows_with_metadata(
        self,
        flow_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Query flows with all metadata in a single query using JOINs.
        
        This method fetches flow metadata along with counts of related data
        (entry types, scope artifacts, interfaces, etc.) in a single query.
        
        Args:
            flow_ids: Optional list of specific flow IDs to query
            
        Returns:
            List of flow metadata dictionaries
        """
        # Build WHERE clause for flow IDs
        where_clause = ""
        params = []
        
        if flow_ids:
            placeholders = ','.join('?' * len(flow_ids))
            where_clause = f"WHERE mf.flow_id IN ({placeholders})"
            params = flow_ids
        
        query = f"""
            SELECT 
                mf.flow_id,
                mf.name,
                mf.entry_program,
                mf.primary_entry_type,
                mf.total_programs,
                mf.total_copybooks,
                mf.total_datasets,
                mf.complexity_total_lines,
                mf.complexity_cyclomatic,
                mf.complexity_score,
                mf.complexity_tier,
                mf.priority,
                mf.business_domain,
                COUNT(DISTINCT fet.entry_type) as entry_type_count,
                COUNT(DISTINCT fi_in.id) as inbound_interface_count,
                COUNT(DISTINCT fi_out.id) as outbound_interface_count,
                COUNT(DISTINCT fdo_db.id) as database_operation_count,
                COUNT(DISTINCT fdo_ds.id) as dataset_operation_count
            FROM migration_flows mf
            LEFT JOIN flow_entry_types fet ON mf.flow_id = fet.flow_id
            LEFT JOIN flow_interfaces fi_in ON mf.flow_id = fi_in.flow_id AND fi_in.direction = 'INBOUND'
            LEFT JOIN flow_interfaces fi_out ON mf.flow_id = fi_out.flow_id AND fi_out.direction = 'OUTBOUND'
            LEFT JOIN flow_data_operations fdo_db ON mf.flow_id = fdo_db.flow_id AND fdo_db.operation_category = 'DATABASE'
            LEFT JOIN flow_data_operations fdo_ds ON mf.flow_id = fdo_ds.flow_id AND fdo_ds.operation_category = 'DATASET'
            {where_clause}
            GROUP BY mf.flow_id
            ORDER BY mf.flow_id
        """
        
        self.cursor.execute(query, params)
        
        flows = []
        for row in self.cursor.fetchall():
            (flow_id, name, entry_program, primary_type, total_programs, total_copybooks,
             total_datasets, total_lines, cyclomatic, composite_score, tier,
             priority, business_domain, entry_type_count, inbound_count, outbound_count,
             db_op_count, ds_op_count) = row
            
            flows.append({
                'flowId': flow_id,
                'name': name,
                'entryProgram': entry_program,
                'primaryType': primary_type,
                'totalPrograms': total_programs,
                'totalCopybooks': total_copybooks,
                'totalDatasets': total_datasets,
                'complexityTotalLines': total_lines,
                'complexityCyclomatic': cyclomatic,
                'complexityScore': float(composite_score) if composite_score else 0.0,
                'complexityTier': tier,
                'priority': priority,
                'businessDomain': business_domain,
                'entryTypeCount': entry_type_count,
                'inboundInterfaceCount': inbound_count,
                'outboundInterfaceCount': outbound_count,
                'databaseOperationCount': db_op_count,
                'datasetOperationCount': ds_op_count
            })
        
        return flows
    
    def query_flow_complete_data(self, flow_id: str) -> Optional[Dict]:
        """
        Query complete flow data including all related tables in optimized queries.
        
        This method uses multiple optimized queries (with JOINs where appropriate)
        to fetch all flow data efficiently.
        
        Args:
            flow_id: Flow ID to query
            
        Returns:
            Complete flow data dictionary, or None if flow not found
        """
        # Query main flow metadata
        flow_data = self._query_flow_metadata_optimized(flow_id)
        if not flow_data:
            return None
        
        # Query entry types (already optimized with grouping)
        flow_data['entryPoint']['types'] = self._query_entry_types_optimized(flow_id)
        
        # Query scope (already optimized with grouping)
        flow_data['scope'] = self._query_scope_optimized(flow_id)
        
        # Query interfaces (already optimized with grouping)
        flow_data['interfaces'] = self._query_interfaces_optimized(flow_id)
        
        # Query data operations (already optimized with grouping)
        flow_data['dataOperations'] = self._query_data_operations_optimized(flow_id)
        
        # Query dependencies (simple query, already efficient)
        flow_data['dependencies'] = self._query_dependencies_optimized(flow_id)
        
        return flow_data
    
    def _query_flow_metadata_optimized(self, flow_id: str) -> Optional[Dict]:
        """Query flow metadata with basic structure."""
        self.cursor.execute("""
            SELECT 
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
                business_domain
            FROM migration_flows
            WHERE flow_id = ?
        """, (flow_id,))
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        (flow_id, name, entry_program, primary_type, total_programs, total_copybooks,
         total_datasets, total_lines, cyclomatic, composite_score, tier,
         priority, business_domain) = row
        
        flow = {
            'flowId': flow_id,
            'name': name,
            'entryPoint': {
                'program': entry_program,
                'types': []  # Will be populated separately
            },
            'complexity': {
                'totalPrograms': total_programs,
                'totalLines': total_lines,
                'cyclomaticComplexity': cyclomatic,
                'compositeScore': float(composite_score) if composite_score else 0.0,
                'tier': tier if tier else 'UNKNOWN'
            }
        }
        
        if primary_type:
            flow['entryPoint']['primaryType'] = primary_type
        
        if priority is not None:
            flow['priority'] = priority
        
        if business_domain:
            flow['businessDomain'] = business_domain
        
        return flow
    
    def _query_entry_types_optimized(self, flow_id: str) -> List[Dict]:
        """
        Query entry types with callers in a single query.
        
        This query fetches all entry types and their callers in one go,
        then groups them in Python.
        """
        self.cursor.execute("""
            SELECT 
                entry_type,
                caller_source,
                metadata_json
            FROM flow_entry_types
            WHERE flow_id = ?
            ORDER BY entry_type, caller_source
        """, (flow_id,))
        
        # Group callers by entry type
        types_dict = {}
        
        for row in self.cursor.fetchall():
            entry_type, caller_source, metadata_json = row
            
            if entry_type not in types_dict:
                types_dict[entry_type] = []
            
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            
            caller = {'source': caller_source}
            if metadata:
                caller['metadata'] = metadata
            
            types_dict[entry_type].append(caller)
        
        # Convert to list format
        return [
            {'type': entry_type, 'callers': callers}
            for entry_type, callers in types_dict.items()
        ]
    
    def _query_scope_optimized(self, flow_id: str) -> Dict[str, List[str]]:
        """
        Query scope artifacts in a single query.
        
        This query fetches all scope artifacts and groups them by type in Python.
        """
        self.cursor.execute("""
            SELECT 
                artifact_type,
                artifact_name
            FROM flow_scope
            WHERE flow_id = ?
            ORDER BY artifact_type, artifact_name
        """, (flow_id,))
        
        scope = {
            'programs': [],
            'copybooks': [],
            'datasets': []
        }
        
        for row in self.cursor.fetchall():
            artifact_type, artifact_name = row
            
            if artifact_type == 'PROGRAM':
                scope['programs'].append(artifact_name)
            elif artifact_type == 'COPYBOOK':
                scope['copybooks'].append(artifact_name)
            elif artifact_type == 'DATASET':
                scope['datasets'].append(artifact_name)
        
        return scope
    
    def _query_interfaces_optimized(self, flow_id: str) -> Dict[str, List[Dict]]:
        """
        Query interfaces in a single query.
        
        This query fetches all interfaces and groups them by direction in Python.
        """
        self.cursor.execute("""
            SELECT 
                direction,
                interface_type,
                source,
                target,
                external,
                metadata_json
            FROM flow_interfaces
            WHERE flow_id = ?
            ORDER BY direction, interface_type, source, target
        """, (flow_id,))
        
        interfaces = {
            'inbound': [],
            'outbound': []
        }
        
        for row in self.cursor.fetchall():
            direction, iface_type, source, target, external, metadata_json = row
            
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            
            interface = {
                'type': iface_type,
                'source': source,
                'target': target
            }
            
            if external:
                interface['external'] = True
            
            if metadata:
                interface['metadata'] = metadata
            
            if direction == 'INBOUND':
                interfaces['inbound'].append(interface)
            else:
                interfaces['outbound'].append(interface)
        
        return interfaces
    
    def _query_data_operations_optimized(self, flow_id: str) -> Dict[str, List[Dict]]:
        """
        Query data operations in a single query.
        
        This query fetches all data operations and groups them by category in Python.
        """
        self.cursor.execute("""
            SELECT 
                operation_category,
                operation_type,
                db_type,
                target,
                program,
                mode
            FROM flow_data_operations
            WHERE flow_id = ?
            ORDER BY operation_category, target, program
        """, (flow_id,))
        
        data_operations = {
            'databases': [],
            'datasets': []
        }
        
        # Track datasets to consolidate programs
        datasets_dict = {}
        
        for row in self.cursor.fetchall():
            category, op_type, db_type, target, program, mode = row
            
            if category == 'DATABASE':
                operation = {
                    'type': db_type if db_type else 'UNKNOWN',
                    'operation': op_type,
                    'target': target,
                    'program': program
                }
                data_operations['databases'].append(operation)
            
            elif category == 'DATASET':
                if target not in datasets_dict:
                    datasets_dict[target] = {
                        'name': target,
                        'operation': op_type if op_type else 'UNKNOWN',
                        'mode': mode if mode else 'UNKNOWN',
                        'programs': []
                    }
                
                if program not in datasets_dict[target]['programs']:
                    datasets_dict[target]['programs'].append(program)
        
        data_operations['datasets'] = list(datasets_dict.values())
        
        return data_operations
    
    def _query_dependencies_optimized(self, flow_id: str) -> Dict[str, List[str]]:
        """
        Query flow dependencies in optimized queries.
        
        This uses two simple queries (one for required, one for dependent)
        which is already efficient.
        """
        # Query required flows
        self.cursor.execute("""
            SELECT DISTINCT depends_on_flow_id
            FROM flow_dependencies
            WHERE flow_id = ? AND dependency_type = 'REQUIRED'
            ORDER BY depends_on_flow_id
        """, (flow_id,))
        
        required_flows = [row[0] for row in self.cursor.fetchall()]
        
        # Query dependent flows
        self.cursor.execute("""
            SELECT DISTINCT flow_id
            FROM flow_dependencies
            WHERE depends_on_flow_id = ? AND dependency_type = 'REQUIRED'
            ORDER BY flow_id
        """, (flow_id,))
        
        dependent_flows = [row[0] for row in self.cursor.fetchall()]
        
        return {
            'requiredFlows': required_flows,
            'dependentFlows': dependent_flows
        }
    
    def query_multiple_flows_batch(self, flow_ids: List[str]) -> Dict[str, Dict]:
        """
        Query multiple flows in batch using optimized queries.
        
        This method fetches data for multiple flows efficiently by:
        1. Fetching all flow metadata in one query
        2. Fetching all related data (entry types, scope, etc.) in batch queries
        3. Grouping results by flow_id in Python
        
        Args:
            flow_ids: List of flow IDs to query
            
        Returns:
            Dictionary mapping flow_id -> complete flow data
        """
        if not flow_ids:
            return {}
        
        # Query all flow metadata
        flows = {}
        for flow_data in self.query_flows_with_metadata(flow_ids):
            flow_id = flow_data['flowId']
            flows[flow_id] = {
                'flowId': flow_id,
                'name': flow_data['name'],
                'entryPoint': {
                    'program': flow_data['entryProgram'],
                    'types': []
                },
                'complexity': {
                    'totalPrograms': flow_data['totalPrograms'],
                    'totalLines': flow_data['complexityTotalLines'],
                    'cyclomaticComplexity': flow_data['complexityCyclomatic'],
                    'compositeScore': flow_data['complexityScore'],
                    'tier': flow_data['complexityTier']
                }
            }
            
            if flow_data['primaryType']:
                flows[flow_id]['entryPoint']['primaryType'] = flow_data['primaryType']
            
            if flow_data['priority'] is not None:
                flows[flow_id]['priority'] = flow_data['priority']
            
            if flow_data['businessDomain']:
                flows[flow_id]['businessDomain'] = flow_data['businessDomain']
        
        # Batch query entry types
        entry_types_map = self._batch_query_entry_types(flow_ids)
        for flow_id, entry_types in entry_types_map.items():
            if flow_id in flows:
                flows[flow_id]['entryPoint']['types'] = entry_types
        
        # Batch query scope
        scope_map = self._batch_query_scope(flow_ids)
        for flow_id, scope in scope_map.items():
            if flow_id in flows:
                flows[flow_id]['scope'] = scope
        
        # Batch query interfaces
        interfaces_map = self._batch_query_interfaces(flow_ids)
        for flow_id, interfaces in interfaces_map.items():
            if flow_id in flows:
                flows[flow_id]['interfaces'] = interfaces
        
        # Batch query data operations
        data_ops_map = self._batch_query_data_operations(flow_ids)
        for flow_id, data_ops in data_ops_map.items():
            if flow_id in flows:
                flows[flow_id]['dataOperations'] = data_ops
        
        # Batch query dependencies
        deps_map = self._batch_query_dependencies(flow_ids)
        for flow_id, deps in deps_map.items():
            if flow_id in flows:
                flows[flow_id]['dependencies'] = deps
        
        return flows
    
    def _batch_query_entry_types(self, flow_ids: List[str]) -> Dict[str, List[Dict]]:
        """Batch query entry types for multiple flows."""
        placeholders = ','.join('?' * len(flow_ids))
        self.cursor.execute(f"""
            SELECT 
                flow_id,
                entry_type,
                caller_source,
                metadata_json
            FROM flow_entry_types
            WHERE flow_id IN ({placeholders})
            ORDER BY flow_id, entry_type, caller_source
        """, flow_ids)
        
        # Group by flow_id and entry_type
        result = {}
        
        for row in self.cursor.fetchall():
            flow_id, entry_type, caller_source, metadata_json = row
            
            if flow_id not in result:
                result[flow_id] = {}
            
            if entry_type not in result[flow_id]:
                result[flow_id][entry_type] = []
            
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            
            caller = {'source': caller_source}
            if metadata:
                caller['metadata'] = metadata
            
            result[flow_id][entry_type].append(caller)
        
        # Convert to list format
        return {
            flow_id: [
                {'type': entry_type, 'callers': callers}
                for entry_type, callers in types_dict.items()
            ]
            for flow_id, types_dict in result.items()
        }
    
    def _batch_query_scope(self, flow_ids: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Batch query scope for multiple flows."""
        placeholders = ','.join('?' * len(flow_ids))
        self.cursor.execute(f"""
            SELECT 
                flow_id,
                artifact_type,
                artifact_name
            FROM flow_scope
            WHERE flow_id IN ({placeholders})
            ORDER BY flow_id, artifact_type, artifact_name
        """, flow_ids)
        
        # Group by flow_id
        result = {}
        
        for row in self.cursor.fetchall():
            flow_id, artifact_type, artifact_name = row
            
            if flow_id not in result:
                result[flow_id] = {
                    'programs': [],
                    'copybooks': [],
                    'datasets': []
                }
            
            if artifact_type == 'PROGRAM':
                result[flow_id]['programs'].append(artifact_name)
            elif artifact_type == 'COPYBOOK':
                result[flow_id]['copybooks'].append(artifact_name)
            elif artifact_type == 'DATASET':
                result[flow_id]['datasets'].append(artifact_name)
        
        return result
    
    def _batch_query_interfaces(self, flow_ids: List[str]) -> Dict[str, Dict[str, List[Dict]]]:
        """Batch query interfaces for multiple flows."""
        placeholders = ','.join('?' * len(flow_ids))
        self.cursor.execute(f"""
            SELECT 
                flow_id,
                direction,
                interface_type,
                source,
                target,
                external,
                metadata_json
            FROM flow_interfaces
            WHERE flow_id IN ({placeholders})
            ORDER BY flow_id, direction, interface_type
        """, flow_ids)
        
        # Group by flow_id
        result = {}
        
        for row in self.cursor.fetchall():
            flow_id, direction, iface_type, source, target, external, metadata_json = row
            
            if flow_id not in result:
                result[flow_id] = {
                    'inbound': [],
                    'outbound': []
                }
            
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            
            interface = {
                'type': iface_type,
                'source': source,
                'target': target
            }
            
            if external:
                interface['external'] = True
            
            if metadata:
                interface['metadata'] = metadata
            
            if direction == 'INBOUND':
                result[flow_id]['inbound'].append(interface)
            else:
                result[flow_id]['outbound'].append(interface)
        
        return result
    
    def _batch_query_data_operations(self, flow_ids: List[str]) -> Dict[str, Dict[str, List[Dict]]]:
        """Batch query data operations for multiple flows."""
        placeholders = ','.join('?' * len(flow_ids))
        self.cursor.execute(f"""
            SELECT 
                flow_id,
                operation_category,
                operation_type,
                db_type,
                target,
                program,
                mode
            FROM flow_data_operations
            WHERE flow_id IN ({placeholders})
            ORDER BY flow_id, operation_category, target
        """, flow_ids)
        
        # Group by flow_id
        result = {}
        
        for row in self.cursor.fetchall():
            flow_id, category, op_type, db_type, target, program, mode = row
            
            if flow_id not in result:
                result[flow_id] = {
                    'databases': [],
                    'datasets': {}
                }
            
            if category == 'DATABASE':
                operation = {
                    'type': db_type if db_type else 'UNKNOWN',
                    'operation': op_type,
                    'target': target,
                    'program': program
                }
                result[flow_id]['databases'].append(operation)
            
            elif category == 'DATASET':
                if target not in result[flow_id]['datasets']:
                    result[flow_id]['datasets'][target] = {
                        'name': target,
                        'mode': mode if mode else 'UNKNOWN',
                        'programs': []
                    }
                
                if program not in result[flow_id]['datasets'][target]['programs']:
                    result[flow_id]['datasets'][target]['programs'].append(program)
        
        # Convert datasets dict to list
        for flow_id in result:
            result[flow_id]['datasets'] = list(result[flow_id]['datasets'].values())
        
        return result
    
    def _batch_query_dependencies(self, flow_ids: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Batch query dependencies for multiple flows."""
        placeholders = ','.join('?' * len(flow_ids))
        
        # Query required flows
        self.cursor.execute(f"""
            SELECT 
                flow_id,
                depends_on_flow_id
            FROM flow_dependencies
            WHERE flow_id IN ({placeholders})
              AND dependency_type = 'REQUIRED'
            ORDER BY flow_id, depends_on_flow_id
        """, flow_ids)
        
        result = {}
        
        for row in self.cursor.fetchall():
            flow_id, depends_on_flow_id = row
            
            if flow_id not in result:
                result[flow_id] = {
                    'requiredFlows': [],
                    'dependentFlows': []
                }
            
            result[flow_id]['requiredFlows'].append(depends_on_flow_id)
        
        # Query dependent flows
        self.cursor.execute(f"""
            SELECT 
                depends_on_flow_id,
                flow_id
            FROM flow_dependencies
            WHERE depends_on_flow_id IN ({placeholders})
              AND dependency_type = 'REQUIRED'
            ORDER BY depends_on_flow_id, flow_id
        """, flow_ids)
        
        for row in self.cursor.fetchall():
            depends_on_flow_id, flow_id = row
            
            if depends_on_flow_id not in result:
                result[depends_on_flow_id] = {
                    'requiredFlows': [],
                    'dependentFlows': []
                }
            
            result[depends_on_flow_id]['dependentFlows'].append(flow_id)
        
        # Ensure all flow_ids have entries
        for flow_id in flow_ids:
            if flow_id not in result:
                result[flow_id] = {
                    'requiredFlows': [],
                    'dependentFlows': []
                }
        
        return result
