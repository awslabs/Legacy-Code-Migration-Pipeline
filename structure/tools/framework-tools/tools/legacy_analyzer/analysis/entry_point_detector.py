"""Entry point detection with CICS metadata integration.

This module provides enhanced entry point detection by combining multiple sources:
1. ONLINE entry points from CICS transaction metadata (inventory_cics table)
2. BATCH entry points from JCL dependencies (artifact_dependencies table)
3. INFERRED entry points from call graph analysis (programs not called by others)

Entry points are prioritized: ONLINE > BATCH > INFERRED
"""

from typing import List, Dict, Set, Optional, Any
import sqlite3
import logging

from ..models.flow import EntryPoint
from ..utils.database_utils import check_table_exists
from ..constants import (
    ENTRY_TYPE_ONLINE,
    ENTRY_TYPE_BATCH,
    ENTRY_TYPE_INFERRED,
    CONFIDENCE_EXPLICIT,
    CONFIDENCE_INFERRED,
    SOURCE_CSD,
    SOURCE_JCL,
    SOURCE_CODE_ANALYSIS,
    STATUS_ENABLED,
)


logger = logging.getLogger(__name__)


class EntryPointDetector:
    """Detects entry points from multiple sources with confidence levels.
    
    This class integrates CICS metadata, JCL dependencies, and code analysis
    to provide comprehensive entry point detection with confidence scoring.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize entry point detector.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self._has_cics_table = check_table_exists(db_connection, 'inventory_cics')
        self._has_dependencies_table = check_table_exists(db_connection, 'artifact_dependencies')
    
    def get_online_entry_points(
        self,
        include_disabled: bool = False
    ) -> List[EntryPoint]:
        """
        Get ONLINE entry points from CICS transaction metadata.
        
        Queries the inventory_cics table for TRANSACTION type resources
        and returns them as EntryPoint objects with EXPLICIT confidence.
        
        Args:
            include_disabled: If True, include DISABLED transactions
            
        Returns:
            List of EntryPoint objects for CICS transactions
        """
        if not self._has_cics_table:
            logger.info("inventory_cics table not found, skipping ONLINE entry points")
            return []
        
        try:
            # Query CICS transactions
            query = """
                SELECT 
                    resource_name,
                    program_name,
                    group_name,
                    status,
                    description
                FROM inventory_cics
                WHERE resource_type = 'TRANSACTION'
            """
            
            if not include_disabled:
                query += " AND status = 'ENABLED'"
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            entry_points = []
            for row in rows:
                transaction_id, program_name, group_name, status, description = row
                
                # Skip if program_name is missing
                if not program_name:
                    logger.warning(
                        f"Transaction {transaction_id} has no program_name, skipping"
                    )
                    continue
                
                entry_point = EntryPoint(
                    program_name=program_name,
                    entry_type=ENTRY_TYPE_ONLINE,
                    confidence=CONFIDENCE_EXPLICIT,
                    source=SOURCE_CSD,
                    transaction_id=transaction_id,
                    cics_group=group_name,
                    status=status,
                    description=description
                )
                entry_points.append(entry_point)
            
            logger.info(f"Found {len(entry_points)} ONLINE entry points from CICS metadata")
            return entry_points
            
        except sqlite3.Error as e:
            logger.error(f"Error querying ONLINE entry points: {e}")
            return []
    
    def get_batch_entry_points(self) -> List[EntryPoint]:
        """
        Get BATCH entry points from JCL dependencies.
        
        Queries the artifact_dependencies table for JCL→PROGRAM relationships
        (EXEC_PGM dependency type) and returns them as EntryPoint objects
        with EXPLICIT confidence.
        
        Returns:
            List of EntryPoint objects for batch programs
        """
        if not self._has_dependencies_table:
            logger.info("artifact_dependencies table not found, skipping BATCH entry points")
            return []
        
        try:
            # Query JCL→PROGRAM dependencies
            query = """
                SELECT DISTINCT 
                    target_artifact_name,
                    source_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'JCL'
                  AND dependency_type = 'EXEC_PGM'
                  AND target_artifact_type = 'PROGRAM'
            """
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            entry_points = []
            for row in rows:
                program_name, jcl_name = row
                
                entry_point = EntryPoint(
                    program_name=program_name,
                    entry_type=ENTRY_TYPE_BATCH,
                    confidence=CONFIDENCE_EXPLICIT,
                    source=SOURCE_JCL,
                    jcl_name=jcl_name,
                    status=STATUS_ENABLED  # Assume enabled if in JCL
                )
                entry_points.append(entry_point)
            
            logger.info(f"Found {len(entry_points)} BATCH entry points from JCL")
            return entry_points
            
        except sqlite3.Error as e:
            logger.error(f"Error querying BATCH entry points: {e}")
            return []
    
    def get_inferred_entry_points(
        self,
        all_programs: Set[str],
        called_programs: Set[str]
    ) -> List[EntryPoint]:
        """
        Get INFERRED entry points from call graph analysis.
        
        Programs that are never called by other programs are potential
        entry points. These have INFERRED confidence since we're making
        an assumption based on code analysis.
        
        Args:
            all_programs: Set of all program names in the system
            called_programs: Set of programs that are called by others
            
        Returns:
            List of EntryPoint objects for inferred entry points
        """
        # Entry points are programs that are never called
        inferred_programs = all_programs - called_programs
        
        entry_points = []
        for program_name in inferred_programs:
            entry_point = EntryPoint(
                program_name=program_name,
                entry_type=ENTRY_TYPE_INFERRED,
                confidence=CONFIDENCE_INFERRED,
                source=SOURCE_CODE_ANALYSIS,
                description='Program not called by any other program'
            )
            entry_points.append(entry_point)
        
        logger.info(f"Found {len(entry_points)} INFERRED entry points from code analysis")
        return entry_points
    
    def detect_entry_points(
        self,
        all_programs: Optional[Set[str]] = None,
        called_programs: Optional[Set[str]] = None,
        include_disabled: bool = False,
        include_inferred: bool = True
    ) -> List[EntryPoint]:
        """
        Detect entry points from all sources with priority merging.
        
        Priority order: ONLINE > BATCH > INFERRED
        If a program appears in multiple sources, the higher priority source wins.
        
        Args:
            all_programs: Set of all program names (for inferred detection)
            called_programs: Set of called programs (for inferred detection)
            include_disabled: If True, include DISABLED CICS transactions
            include_inferred: If True, include inferred entry points
            
        Returns:
            List of EntryPoint objects, deduplicated by priority
        """
        # Track programs we've already seen (for deduplication)
        seen_programs: Dict[str, EntryPoint] = {}
        
        # Priority 1: ONLINE entry points (CICS transactions)
        online_entries = self.get_online_entry_points(include_disabled)
        for entry in online_entries:
            seen_programs[entry.program_name] = entry
        
        # Priority 2: BATCH entry points (JCL)
        batch_entries = self.get_batch_entry_points()
        for entry in batch_entries:
            # Only add if not already seen as ONLINE
            if entry.program_name not in seen_programs:
                seen_programs[entry.program_name] = entry
        
        # Priority 3: INFERRED entry points (code analysis)
        if include_inferred and all_programs is not None and called_programs is not None:
            inferred_entries = self.get_inferred_entry_points(
                all_programs,
                called_programs
            )
            for entry in inferred_entries:
                # Only add if not already seen as ONLINE or BATCH
                if entry.program_name not in seen_programs:
                    seen_programs[entry.program_name] = entry
        
        # Convert to list and sort by program name for consistency
        entry_points = list(seen_programs.values())
        entry_points.sort(key=lambda e: e.program_name)
        
        logger.info(
            f"Detected {len(entry_points)} total entry points: "
            f"{len(online_entries)} ONLINE, "
            f"{len(batch_entries)} BATCH, "
            f"{len(entry_points) - len(online_entries) - len(batch_entries)} INFERRED"
        )
        
        return entry_points
    
    def get_entry_point_statistics(
        self,
        entry_points: List[EntryPoint]
    ) -> Dict[str, Any]:
        """
        Calculate statistics about entry points.
        
        Args:
            entry_points: List of EntryPoint objects
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total': len(entry_points),
            'by_type': {
                'ONLINE': 0,
                'BATCH': 0,
                'INFERRED': 0
            },
            'by_confidence': {
                'EXPLICIT': 0,
                'INFERRED': 0
            },
            'by_status': {
                'ENABLED': 0,
                'DISABLED': 0,
                'UNKNOWN': 0
            }
        }
        
        for entry in entry_points:
            # Count by type
            stats['by_type'][entry.entry_type] = \
                stats['by_type'].get(entry.entry_type, 0) + 1
            
            # Count by confidence
            stats['by_confidence'][entry.confidence] = \
                stats['by_confidence'].get(entry.confidence, 0) + 1
            
            # Count by status
            if entry.status == 'ENABLED':
                stats['by_status']['ENABLED'] += 1
            elif entry.status == 'DISABLED':
                stats['by_status']['DISABLED'] += 1
            else:
                stats['by_status']['UNKNOWN'] += 1
        
        return stats
