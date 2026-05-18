"""
Complexity Cache Module

This module provides caching functionality for complexity calculations to avoid
redundant database queries and computations.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class ComplexityCache:
    """
    Cache for program complexity metrics and flow complexity calculations.
    
    This cache stores:
    - Individual program complexity metrics
    - Aggregated flow complexity calculations
    - Complexity tier mappings
    
    The cache is invalidated when complexity data is updated in the database.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize the complexity cache.
        
        Args:
            ttl_seconds: Time-to-live for cached entries in seconds (default: 3600 = 1 hour)
        """
        self.ttl_seconds = ttl_seconds
        
        # Program-level complexity cache: program_name -> (metrics, timestamp)
        self._program_cache: Dict[str, tuple] = {}
        
        # Flow-level complexity cache: flow_id -> (complexity_dict, timestamp)
        self._flow_cache: Dict[str, tuple] = {}
        
        # Batch complexity cache: frozenset(programs) -> (complexity_dict, timestamp)
        # This allows caching complexity for any set of programs
        self._batch_cache: Dict[frozenset, tuple] = {}
        
        # Statistics
        self.program_hits = 0
        self.program_misses = 0
        self.flow_hits = 0
        self.flow_misses = 0
        self.batch_hits = 0
        self.batch_misses = 0
    
    def get_program_complexity(self, program_name: str) -> Optional[Dict]:
        """
        Get complexity metrics for a single program.
        
        Args:
            program_name: Program name
            
        Returns:
            Dictionary with complexity metrics if cached and not expired, None otherwise
            {
                'lines_of_code': int,
                'cyclomatic_complexity': int,
                'composite_score': float,
                'tier': str
            }
        """
        if program_name in self._program_cache:
            metrics, timestamp = self._program_cache[program_name]
            
            if self._is_expired(timestamp):
                self._program_cache.pop(program_name, None)
                self.program_misses += 1
                return None
            
            self.program_hits += 1
            return metrics
        
        self.program_misses += 1
        return None
    
    def put_program_complexity(self, program_name: str, metrics: Dict) -> None:
        """
        Store complexity metrics for a single program.
        
        Args:
            program_name: Program name
            metrics: Complexity metrics dictionary
        """
        self._program_cache[program_name] = (metrics, datetime.now())
    
    def get_batch_program_complexity(self, programs: List[str]) -> Optional[Dict[str, Dict]]:
        """
        Get complexity metrics for multiple programs at once.
        
        Args:
            programs: List of program names
            
        Returns:
            Dictionary mapping program_name -> metrics if all programs are cached,
            None if any program is missing or expired
        """
        result = {}
        
        for program in programs:
            metrics = self.get_program_complexity(program)
            if metrics is None:
                return None
            result[program] = metrics
        
        return result
    
    def put_batch_program_complexity(self, program_metrics: Dict[str, Dict]) -> None:
        """
        Store complexity metrics for multiple programs at once.
        
        Args:
            program_metrics: Dictionary mapping program_name -> metrics
        """
        for program_name, metrics in program_metrics.items():
            self.put_program_complexity(program_name, metrics)
    
    def get_flow_complexity(self, flow_id: str) -> Optional[Dict]:
        """
        Get aggregated complexity for a flow.
        
        Args:
            flow_id: Flow ID
            
        Returns:
            Dictionary with aggregated complexity if cached and not expired, None otherwise
            {
                'totalPrograms': int,
                'totalLines': int,
                'cyclomaticComplexity': int,
                'compositeScore': float,
                'tier': str
            }
        """
        if flow_id in self._flow_cache:
            complexity, timestamp = self._flow_cache[flow_id]
            
            if self._is_expired(timestamp):
                self._flow_cache.pop(flow_id, None)
                self.flow_misses += 1
                return None
            
            self.flow_hits += 1
            return complexity
        
        self.flow_misses += 1
        return None
    
    def put_flow_complexity(self, flow_id: str, complexity: Dict) -> None:
        """
        Store aggregated complexity for a flow.
        
        Args:
            flow_id: Flow ID
            complexity: Aggregated complexity dictionary
        """
        self._flow_cache[flow_id] = (complexity, datetime.now())
    
    def get_programs_complexity(self, programs: List[str]) -> Optional[Dict]:
        """
        Get aggregated complexity for a set of programs.
        
        This is useful for calculating flow complexity without knowing the flow ID.
        
        Args:
            programs: List of program names
            
        Returns:
            Dictionary with aggregated complexity if cached, None otherwise
        """
        # Create a frozen set for cache key (order-independent)
        programs_key = frozenset(programs)
        
        if programs_key in self._batch_cache:
            complexity, timestamp = self._batch_cache[programs_key]
            
            if self._is_expired(timestamp):
                self._batch_cache.pop(programs_key, None)
                self.batch_misses += 1
                return None
            
            self.batch_hits += 1
            return complexity
        
        self.batch_misses += 1
        return None
    
    def put_programs_complexity(self, programs: List[str], complexity: Dict) -> None:
        """
        Store aggregated complexity for a set of programs.
        
        Args:
            programs: List of program names
            complexity: Aggregated complexity dictionary
        """
        programs_key = frozenset(programs)
        self._batch_cache[programs_key] = (complexity, datetime.now())
    
    def invalidate_program(self, program_name: str) -> None:
        """
        Invalidate cached complexity for a specific program.
        
        This also invalidates any flow or batch caches that include this program.
        
        Args:
            program_name: Program name to invalidate
        """
        self._program_cache.pop(program_name, None)
        
        # Invalidate batch caches containing this program
        keys_to_remove = []
        for programs_key in self._batch_cache.keys():
            if program_name in programs_key:
                keys_to_remove.append(programs_key)
        
        for key in keys_to_remove:
            self._batch_cache.pop(key, None)
        
        logger.debug(f"Invalidated complexity cache for program: {program_name}")
    
    def invalidate_flow(self, flow_id: str) -> None:
        """
        Invalidate cached complexity for a specific flow.
        
        Args:
            flow_id: Flow ID to invalidate
        """
        self._flow_cache.pop(flow_id, None)
    
    def invalidate_all(self) -> None:
        """Clear all cached complexity data."""
        self._program_cache.clear()
        self._flow_cache.clear()
        self._batch_cache.clear()
        
        logger.info("Complexity cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics for each cache type
        """
        program_total = self.program_hits + self.program_misses
        program_hit_rate = self.program_hits / program_total if program_total > 0 else 0.0
        
        flow_total = self.flow_hits + self.flow_misses
        flow_hit_rate = self.flow_hits / flow_total if flow_total > 0 else 0.0
        
        batch_total = self.batch_hits + self.batch_misses
        batch_hit_rate = self.batch_hits / batch_total if batch_total > 0 else 0.0
        
        return {
            'program_cache': {
                'size': len(self._program_cache),
                'hits': self.program_hits,
                'misses': self.program_misses,
                'hit_rate': program_hit_rate
            },
            'flow_cache': {
                'size': len(self._flow_cache),
                'hits': self.flow_hits,
                'misses': self.flow_misses,
                'hit_rate': flow_hit_rate
            },
            'batch_cache': {
                'size': len(self._batch_cache),
                'hits': self.batch_hits,
                'misses': self.batch_misses,
                'hit_rate': batch_hit_rate
            },
            'ttl_seconds': self.ttl_seconds
        }
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cached entry has expired."""
        age = datetime.now() - timestamp
        return age.total_seconds() > self.ttl_seconds
    
    def preload_programs(self, program_metrics: Dict[str, Dict]) -> None:
        """
        Preload complexity metrics for multiple programs.
        
        This is useful for bulk loading complexity data at startup or after
        a batch complexity calculation.
        
        Args:
            program_metrics: Dictionary mapping program_name -> metrics
        """
        count = 0
        for program_name, metrics in program_metrics.items():
            self.put_program_complexity(program_name, metrics)
            count += 1
        
        logger.info(f"Preloaded complexity metrics for {count} programs")
    
    def preload_flows(self, flow_complexity: Dict[str, Dict]) -> None:
        """
        Preload complexity data for multiple flows.
        
        Args:
            flow_complexity: Dictionary mapping flow_id -> complexity
        """
        count = 0
        for flow_id, complexity in flow_complexity.items():
            self.put_flow_complexity(flow_id, complexity)
            count += 1
        
        logger.info(f"Preloaded complexity data for {count} flows")
