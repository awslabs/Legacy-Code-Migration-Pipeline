"""Service grouping analysis using CICS metadata.

This module provides service grouping analysis by examining CICS metadata,
shared data access patterns, and shared program dependencies to identify
logical service boundaries for modernization planning.
"""

from typing import List, Dict, Set, Optional, Tuple
import sqlite3
import logging
from collections import defaultdict

from ..models.flow import ServiceCandidate, EntryPoint
from ..utils.database_utils import check_table_exists
from ..constants import (
    ENTRY_TYPE_ONLINE,
    ENTRY_TYPE_INFERRED,
    CONFIDENCE_EXPLICIT,
    CONFIDENCE_INFERRED,
    SOURCE_CSD,
    SOURCE_CODE_ANALYSIS,
    STATUS_ENABLED,
    MIN_ENTRY_POINTS_FOR_SERVICE,
    MIN_SHARED_DATA_FOR_HIGH_CONFIDENCE,
    MIN_SHARED_PROGRAMS_FOR_HIGH_CONFIDENCE,
    MIN_ENTRY_POINTS_FOR_HIGH_CONFIDENCE,
    CONSOLIDATION_SCORE_ENTRY_POINT_WEIGHT,
    CONSOLIDATION_SCORE_ENTRY_POINT_MAX,
    CONSOLIDATION_SCORE_DATA_WEIGHT,
    CONSOLIDATION_SCORE_DATA_MAX,
    CONSOLIDATION_SCORE_PROGRAM_WEIGHT,
    CONSOLIDATION_SCORE_PROGRAM_MAX,
    CONSOLIDATION_SCORE_HIGH_THRESHOLD,
    CONSOLIDATION_SCORE_LOW_THRESHOLD,
    RECOMMENDATION_CONSIDER_MERGE,
    RECOMMENDATION_KEEP_SEPARATE,
    RECOMMENDATION_NEEDS_REVIEW,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
    GROUPING_REASON_CICS_GROUP,
    GROUPING_REASON_DATA_OWNERSHIP,
    GROUPING_REASON_SHARED_PROGRAMS,
    DATASET_SKIP_PARTS,
)


logger = logging.getLogger(__name__)


class ServiceGroupingAnalyzer:
    """Analyzes service grouping opportunities using CICS metadata.
    
    This analyzer examines CICS transactions, data access patterns, and
    program dependencies to suggest logical service boundaries for
    modernization efforts.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize service grouping analyzer.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self._has_cics_table = check_table_exists(db_connection, 'inventory_cics')
        self._has_dependencies_table = check_table_exists(db_connection, 'artifact_dependencies')
    
    def analyze_by_cics_group(self) -> List[ServiceCandidate]:
        """
        Group entry points by CICS GROUP.
        
        CICS groups are logical groupings defined in the CSD that often
        represent functional areas or applications. These make natural
        service boundaries.
        
        Returns:
            List of ServiceCandidate objects grouped by CICS GROUP
        """
        if not self._has_cics_table:
            logger.warning("inventory_cics table not found, cannot analyze by CICS group")
            return []
        
        try:
            # Query transactions grouped by CICS group
            query = """
                SELECT 
                    group_name,
                    resource_name,
                    program_name,
                    status,
                    description
                FROM inventory_cics
                WHERE resource_type = 'TRANSACTION'
                  AND status = 'ENABLED'
                  AND group_name IS NOT NULL
                ORDER BY group_name, resource_name
            """
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # Group by CICS group
            groups: Dict[str, List[EntryPoint]] = defaultdict(list)
            for group_name, trans_id, program_name, status, description in rows:
                if not program_name:
                    continue
                
                entry_point = EntryPoint(
                    program_name=program_name,
                    entry_type='ONLINE',
                    confidence='EXPLICIT',
                    source='CSD',
                    transaction_id=trans_id,
                    description=description or '',
                    status=status,
                    cics_group=group_name
                )
                groups[group_name].append(entry_point)
            
            # Create service candidates
            candidates = []
            for group_name, entry_points in groups.items():
                # Get shared data and programs for this group
                shared_data = self._get_shared_data_for_group(group_name)
                shared_programs = self._get_shared_programs_for_group(group_name)
                
                # Calculate consolidation score
                consolidation_score = self._calculate_consolidation_score(
                    len(entry_points),
                    len(shared_data),
                    len(shared_programs)
                )
                
                # Determine confidence based on group size and shared resources
                confidence = self._determine_confidence(
                    len(entry_points),
                    len(shared_data),
                    len(shared_programs)
                )
                
                # Generate service name
                service_name = self._generate_service_name(group_name)
                
                candidate = ServiceCandidate(
                    name=service_name,
                    entry_points=entry_points,
                    grouping_reason='CICS_GROUP',
                    confidence=confidence,
                    cics_group=group_name,
                    shared_data=shared_data,
                    shared_programs=shared_programs,
                    total_complexity=consolidation_score,
                    recommendation=self._generate_recommendation(
                        len(entry_points),
                        consolidation_score
                    )
                )
                
                candidates.append(candidate)
            
            logger.info(f"Found {len(candidates)} service candidates by CICS group")
            return candidates
            
        except sqlite3.Error as e:
            logger.error(f"Error analyzing by CICS group: {e}")
            return []
    
    def analyze_by_data_ownership(self) -> List[ServiceCandidate]:
        """
        Group entry points by shared data access.
        
        Programs that access the same datasets often represent a logical
        service boundary. This analysis identifies programs that share
        data access patterns.
        
        Returns:
            List of ServiceCandidate objects grouped by data ownership
        """
        if not self._has_dependencies_table:
            logger.warning("artifact_dependencies table not found, cannot analyze by data ownership")
            return []
        
        try:
            # Get program -> dataset mappings
            query = """
                SELECT DISTINCT
                    source_artifact_name,
                    target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'PROGRAM'
                  AND target_artifact_type = 'DATASET'
                  AND dependency_type IN ('READ', 'WRITE', 'UPDATE')
            """
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # Build dataset -> programs mapping
            dataset_programs: Dict[str, Set[str]] = defaultdict(set)
            program_datasets: Dict[str, Set[str]] = defaultdict(set)
            
            for program, dataset in rows:
                dataset_programs[dataset].add(program)
                program_datasets[program].add(dataset)
            
            # Find clusters of programs that share significant data
            clusters = self._find_data_clusters(program_datasets, dataset_programs)
            
            # Create service candidates
            candidates = []
            for idx, (programs, datasets) in enumerate(clusters, 1):
                # Get entry points for these programs
                entry_points = self._get_entry_points_for_programs(programs)
                
                if not entry_points:
                    continue
                
                # Get shared programs (called by multiple programs in cluster)
                shared_programs = self._get_shared_programs_for_programs(programs)
                
                # Calculate consolidation score
                consolidation_score = self._calculate_consolidation_score(
                    len(entry_points),
                    len(datasets),
                    len(shared_programs)
                )
                
                # Determine confidence
                confidence = self._determine_confidence(
                    len(entry_points),
                    len(datasets),
                    len(shared_programs)
                )
                
                # Generate service name based on primary dataset
                primary_dataset = self._get_primary_dataset(datasets, dataset_programs)
                service_name = self._generate_service_name_from_dataset(primary_dataset)
                
                candidate = ServiceCandidate(
                    name=service_name,
                    entry_points=entry_points,
                    grouping_reason='DATA_OWNERSHIP',
                    confidence=confidence,
                    shared_data=sorted(list(datasets)),
                    shared_programs=shared_programs,
                    total_complexity=consolidation_score,
                    recommendation=self._generate_recommendation(
                        len(entry_points),
                        consolidation_score
                    )
                )
                
                candidates.append(candidate)
            
            logger.info(f"Found {len(candidates)} service candidates by data ownership")
            return candidates
            
        except sqlite3.Error as e:
            logger.error(f"Error analyzing by data ownership: {e}")
            return []
    
    def analyze_by_shared_programs(self) -> List[ServiceCandidate]:
        """
        Group entry points by shared program dependencies.
        
        Entry points that call the same utility programs or subprograms
        may represent a logical service boundary.
        
        Returns:
            List of ServiceCandidate objects grouped by shared programs
        """
        if not self._has_dependencies_table:
            logger.warning("artifact_dependencies table not found, cannot analyze by shared programs")
            return []
        
        try:
            # Get program -> called program mappings
            query = """
                SELECT DISTINCT
                    source_artifact_name,
                    target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'PROGRAM'
                  AND target_artifact_type = 'PROGRAM'
                  AND dependency_type = 'CALL'
            """
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # Build called program -> callers mapping
            called_program_callers: Dict[str, Set[str]] = defaultdict(set)
            caller_called: Dict[str, Set[str]] = defaultdict(set)
            
            for caller, called in rows:
                called_program_callers[called].add(caller)
                caller_called[caller].add(called)
            
            # Find programs that are called by multiple entry points
            # (these are shared utility programs)
            shared_programs = {
                prog: callers 
                for prog, callers in called_program_callers.items() 
                if len(callers) >= 2
            }
            
            # Find clusters of entry points that share significant programs
            clusters = self._find_program_clusters(caller_called, shared_programs)
            
            # Create service candidates
            candidates = []
            for idx, (entry_programs, shared_progs) in enumerate(clusters, 1):
                # Get entry points for these programs
                entry_points = self._get_entry_points_for_programs(entry_programs)
                
                if not entry_points:
                    continue
                
                # Get shared data for these programs
                shared_data = self._get_shared_data_for_programs(entry_programs)
                
                # Calculate consolidation score
                consolidation_score = self._calculate_consolidation_score(
                    len(entry_points),
                    len(shared_data),
                    len(shared_progs)
                )
                
                # Determine confidence
                confidence = self._determine_confidence(
                    len(entry_points),
                    len(shared_data),
                    len(shared_progs)
                )
                
                # Generate service name
                service_name = f"Shared Program Service {idx}"
                
                candidate = ServiceCandidate(
                    name=service_name,
                    entry_points=entry_points,
                    grouping_reason='SHARED_PROGRAMS',
                    confidence=confidence,
                    shared_data=shared_data,
                    shared_programs=sorted(list(shared_progs)),
                    total_complexity=consolidation_score,
                    recommendation=self._generate_recommendation(
                        len(entry_points),
                        consolidation_score
                    )
                )
                
                candidates.append(candidate)
            
            logger.info(f"Found {len(candidates)} service candidates by shared programs")
            return candidates
            
        except sqlite3.Error as e:
            logger.error(f"Error analyzing by shared programs: {e}")
            return []
    
    def _get_shared_data_for_group(self, group_name: str) -> List[str]:
        """Get datasets accessed by programs in a CICS group."""
        if not self._has_cics_table or not self._has_dependencies_table:
            return []
        
        try:
            query = """
                SELECT DISTINCT d.target_artifact_name
                FROM inventory_cics c
                JOIN artifact_dependencies d 
                  ON c.program_name = d.source_artifact_name
                WHERE c.group_name = ?
                  AND c.resource_type = 'TRANSACTION'
                  AND d.source_artifact_type = 'PROGRAM'
                  AND d.target_artifact_type = 'DATASET'
                ORDER BY d.target_artifact_name
            """
            
            self.cursor.execute(query, (group_name,))
            return [row[0] for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting shared data for group {group_name}: {e}")
            return []
    
    def _get_shared_programs_for_group(self, group_name: str) -> List[str]:
        """Get programs called by multiple programs in a CICS group."""
        if not self._has_cics_table or not self._has_dependencies_table:
            return []
        
        try:
            query = """
                SELECT d.target_artifact_name, COUNT(DISTINCT d.source_artifact_name) as caller_count
                FROM inventory_cics c
                JOIN artifact_dependencies d 
                  ON c.program_name = d.source_artifact_name
                WHERE c.group_name = ?
                  AND c.resource_type = 'TRANSACTION'
                  AND d.source_artifact_type = 'PROGRAM'
                  AND d.target_artifact_type = 'PROGRAM'
                  AND d.dependency_type = 'CALL'
                GROUP BY d.target_artifact_name
                HAVING caller_count >= 2
                ORDER BY caller_count DESC, d.target_artifact_name
            """
            
            self.cursor.execute(query, (group_name,))
            return [row[0] for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting shared programs for group {group_name}: {e}")
            return []
    
    def _get_entry_points_for_programs(self, programs: Set[str]) -> List[EntryPoint]:
        """Get entry point information for a set of programs.
        
        Returns:
            List of EntryPoint objects for the given programs
        """
        if not programs:
            return []
        
        entry_points = []
        
        # Try to get from CICS transactions first
        if self._has_cics_table:
            try:
                placeholders = ','.join('?' * len(programs))
                query = f"""
                    SELECT resource_name, program_name, description, status
                    FROM inventory_cics
                    WHERE resource_type = 'TRANSACTION'
                      AND program_name IN ({placeholders})
                      AND status = 'ENABLED'
                """
                
                self.cursor.execute(query, tuple(programs))
                for trans_id, program, description, status in self.cursor.fetchall():
                    entry_points.append(EntryPoint(
                        program_name=program,
                        entry_type='ONLINE',
                        confidence='EXPLICIT',
                        source='CSD',
                        transaction_id=trans_id,
                        description=description or '',
                        status=status
                    ))
            except sqlite3.Error as e:
                logger.error(f"Error getting entry points from CICS: {e}")
        
        # If no CICS entry points found, create inferred entry points
        if not entry_points:
            for program in sorted(programs):
                entry_points.append(EntryPoint(
                    program_name=program,
                    entry_type='INFERRED',
                    confidence='INFERRED',
                    source='CODE_ANALYSIS',
                    description='Entry point (inferred)'
                ))
        
        return entry_points
    
    def _get_shared_programs_for_programs(self, programs: Set[str]) -> List[str]:
        """Get programs called by multiple programs in the set."""
        if not self._has_dependencies_table or not programs:
            return []
        
        try:
            placeholders = ','.join('?' * len(programs))
            query = f"""
                SELECT target_artifact_name, COUNT(DISTINCT source_artifact_name) as caller_count
                FROM artifact_dependencies
                WHERE source_artifact_name IN ({placeholders})
                  AND source_artifact_type = 'PROGRAM'
                  AND target_artifact_type = 'PROGRAM'
                  AND dependency_type = 'CALL'
                GROUP BY target_artifact_name
                HAVING caller_count >= 2
                ORDER BY caller_count DESC
            """
            
            self.cursor.execute(query, tuple(programs))
            return [row[0] for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting shared programs: {e}")
            return []
    
    def _get_shared_data_for_programs(self, programs: Set[str]) -> List[str]:
        """Get datasets accessed by multiple programs in the set."""
        if not self._has_dependencies_table or not programs:
            return []
        
        try:
            placeholders = ','.join('?' * len(programs))
            query = f"""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_name IN ({placeholders})
                  AND source_artifact_type = 'PROGRAM'
                  AND target_artifact_type = 'DATASET'
                ORDER BY target_artifact_name
            """
            
            self.cursor.execute(query, tuple(programs))
            return [row[0] for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting shared data: {e}")
            return []
    
    def _find_data_clusters(
        self,
        program_datasets: Dict[str, Set[str]],
        dataset_programs: Dict[str, Set[str]]
    ) -> List[Tuple[Set[str], Set[str]]]:
        """
        Find clusters of programs that share significant data access.
        
        Returns:
            List of (programs, datasets) tuples
        """
        clusters = []
        processed_programs = set()
        
        # Sort datasets by number of programs accessing them (most shared first)
        sorted_datasets = sorted(
            dataset_programs.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for dataset, programs in sorted_datasets:
            # Skip if we've already processed most of these programs
            if len(programs - processed_programs) < 2:
                continue
            
            # Find all datasets shared by these programs
            shared_datasets = set([dataset])
            for prog in programs:
                if prog not in processed_programs:
                    shared_datasets.update(program_datasets.get(prog, set()))
            
            # Find all programs that access these datasets
            cluster_programs = set()
            for ds in shared_datasets:
                cluster_programs.update(dataset_programs.get(ds, set()))
            
            # Only create cluster if it has multiple programs
            if len(cluster_programs) >= 2:
                clusters.append((cluster_programs, shared_datasets))
                processed_programs.update(cluster_programs)
        
        return clusters
    
    def _find_program_clusters(
        self,
        caller_called: Dict[str, Set[str]],
        shared_programs: Dict[str, Set[str]]
    ) -> List[Tuple[Set[str], Set[str]]]:
        """
        Find clusters of entry points that share significant programs.
        
        Returns:
            List of (entry_programs, shared_programs) tuples
        """
        clusters = []
        processed_callers = set()
        
        # Sort shared programs by number of callers (most shared first)
        sorted_shared = sorted(
            shared_programs.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for shared_prog, callers in sorted_shared:
            # Skip if we've already processed most of these callers
            if len(callers - processed_callers) < 2:
                continue
            
            # Find all shared programs called by these callers
            cluster_shared_progs = set([shared_prog])
            for caller in callers:
                if caller not in processed_callers:
                    called = caller_called.get(caller, set())
                    # Add programs that are in our shared_programs dict
                    cluster_shared_progs.update(called & shared_programs.keys())
            
            # Find all callers that call these shared programs
            cluster_callers = set()
            for sp in cluster_shared_progs:
                cluster_callers.update(shared_programs.get(sp, set()))
            
            # Only create cluster if it has multiple callers
            if len(cluster_callers) >= 2:
                clusters.append((cluster_callers, cluster_shared_progs))
                processed_callers.update(cluster_callers)
        
        return clusters
    
    def _get_primary_dataset(
        self,
        datasets: Set[str],
        dataset_programs: Dict[str, Set[str]]
    ) -> str:
        """Get the most accessed dataset in a set."""
        if not datasets:
            return "UNKNOWN"
        
        # Return dataset with most programs accessing it
        return max(
            datasets,
            key=lambda ds: len(dataset_programs.get(ds, set()))
        )
    
    def _calculate_consolidation_score(
        self,
        entry_point_count: int,
        shared_data_count: int,
        shared_program_count: int
    ) -> float:
        """
        Calculate a consolidation score for a service candidate.
        
        Higher scores indicate stronger cohesion and better service boundaries.
        
        Args:
            entry_point_count: Number of entry points
            shared_data_count: Number of shared datasets
            shared_program_count: Number of shared programs
            
        Returns:
            Consolidation score (0-100)
        """
        # Base score from entry point count (more entry points = higher score)
        base_score = min(entry_point_count * 10, 40)
        
        # Bonus for shared data (indicates cohesion)
        data_score = min(shared_data_count * 5, 30)
        
        # Bonus for shared programs (indicates cohesion)
        program_score = min(shared_program_count * 3, 30)
        
        total_score = base_score + data_score + program_score
        
        return round(total_score, 2)
    
    def _determine_confidence(
        self,
        entry_point_count: int,
        shared_data_count: int,
        shared_program_count: int
    ) -> str:
        """
        Determine confidence level for a service candidate.
        
        Args:
            entry_point_count: Number of entry points
            shared_data_count: Number of shared datasets
            shared_program_count: Number of shared programs
            
        Returns:
            Confidence level: HIGH, MEDIUM, or LOW
        """
        # High confidence: multiple entry points with shared resources
        if entry_point_count >= 3 and (shared_data_count >= 2 or shared_program_count >= 2):
            return 'HIGH'
        
        # Medium confidence: some entry points with some shared resources
        if entry_point_count >= 2 and (shared_data_count >= 1 or shared_program_count >= 1):
            return 'MEDIUM'
        
        # Low confidence: few entry points or no shared resources
        return 'LOW'
    
    def _generate_recommendation(
        self,
        entry_point_count: int,
        consolidation_score: float
    ) -> str:
        """
        Generate a recommendation for a service candidate.
        
        Args:
            entry_point_count: Number of entry points
            consolidation_score: Consolidation score
            
        Returns:
            Recommendation: CONSIDER_MERGE, KEEP_SEPARATE, or NEEDS_REVIEW
        """
        # Strong candidates for merging
        if consolidation_score >= 60 and entry_point_count >= 3:
            return 'CONSIDER_MERGE'
        
        # Weak candidates - may be better kept separate
        if consolidation_score < 30 or entry_point_count < 2:
            return 'KEEP_SEPARATE'
        
        # Borderline cases need review
        return 'NEEDS_REVIEW'
    
    def _generate_service_name(self, cics_group: str) -> str:
        """Generate a service name from a CICS group name."""
        # Convert CICS group name to service name
        # e.g., CARDDEMO -> Card Demo Service
        words = []
        current_word = []
        
        for char in cics_group:
            if char.isupper() and current_word and current_word[-1].islower():
                words.append(''.join(current_word))
                current_word = [char]
            else:
                current_word.append(char)
        
        if current_word:
            words.append(''.join(current_word))
        
        # Capitalize first letter of each word
        service_name = ' '.join(word.capitalize() for word in words)
        
        return f"{service_name} Service"
    
    def _generate_service_name_from_dataset(self, dataset: str) -> str:
        """Generate a service name from a dataset name."""
        # Extract meaningful part from dataset name
        # e.g., AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS -> Account Data Service
        parts = dataset.split('.')
        
        # Look for meaningful parts (skip AWS, M2, VSAM, KSDS, etc.)
        skip_parts = {'AWS', 'M2', 'VSAM', 'KSDS', 'ESDS', 'RRDS', 'LDS'}
        meaningful_parts = [p for p in parts if p not in skip_parts and len(p) > 2]
        
        if meaningful_parts:
            # Use the last meaningful part
            name = meaningful_parts[-1]
            # Try to split camelCase or concatenated words
            words = []
            current_word = []
            
            for char in name:
                if char.isupper() and current_word and current_word[-1].islower():
                    words.append(''.join(current_word))
                    current_word = [char]
                else:
                    current_word.append(char)
            
            if current_word:
                words.append(''.join(current_word))
            
            service_name = ' '.join(word.capitalize() for word in words)
            return f"{service_name} Service"
        
        return "Data Service"
