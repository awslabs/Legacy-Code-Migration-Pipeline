"""
Flow Cache Module

This module provides caching functionality for migration flow data to improve
performance by avoiding redundant database queries and computations.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FlowCache:
    """
    In-memory cache for migration flow data.
    
    This cache stores:
    - Complete flow objects (from export queries)
    - Flow metadata
    - Scope data
    - Interface data
    - Data operations
    - Dependencies
    
    The cache uses a simple LRU (Least Recently Used) eviction policy
    when the cache size exceeds the maximum.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the flow cache.
        
        Args:
            max_size: Maximum number of flows to cache (default: 1000)
            ttl_seconds: Time-to-live for cached entries in seconds (default: 3600 = 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        
        # Cache storage: flow_id -> (data, timestamp)
        self._flow_cache: Dict[str, tuple] = {}
        self._scope_cache: Dict[str, tuple] = {}
        self._interfaces_cache: Dict[str, tuple] = {}
        self._data_ops_cache: Dict[str, tuple] = {}
        self._dependencies_cache: Dict[str, tuple] = {}
        
        # Access tracking for LRU eviction
        self._access_order: List[str] = []
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def get_flow(self, flow_id: str) -> Optional[Dict]:
        """
        Get complete flow data from cache.
        
        Args:
            flow_id: Flow ID to retrieve
            
        Returns:
            Flow data dictionary if cached and not expired, None otherwise
        """
        if flow_id in self._flow_cache:
            data, timestamp = self._flow_cache[flow_id]
            
            # Check if expired
            if self._is_expired(timestamp):
                self._evict_flow(flow_id)
                self.misses += 1
                return None
            
            # Update access order
            self._update_access(flow_id)
            self.hits += 1
            return data
        
        self.misses += 1
        return None
    
    def put_flow(self, flow_id: str, data: Dict) -> None:
        """
        Store complete flow data in cache.
        
        Args:
            flow_id: Flow ID
            data: Complete flow data dictionary
        """
        # Evict if cache is full
        if len(self._flow_cache) >= self.max_size:
            self._evict_lru()
        
        # Store with current timestamp
        self._flow_cache[flow_id] = (data, datetime.now())
        self._update_access(flow_id)
    
    def get_scope(self, flow_id: str) -> Optional[Dict]:
        """Get scope data from cache."""
        return self._get_from_cache(self._scope_cache, flow_id)
    
    def put_scope(self, flow_id: str, data: Dict) -> None:
        """Store scope data in cache."""
        self._put_to_cache(self._scope_cache, flow_id, data)
    
    def get_interfaces(self, flow_id: str) -> Optional[Dict]:
        """Get interfaces data from cache."""
        return self._get_from_cache(self._interfaces_cache, flow_id)
    
    def put_interfaces(self, flow_id: str, data: Dict) -> None:
        """Store interfaces data in cache."""
        self._put_to_cache(self._interfaces_cache, flow_id, data)
    
    def get_data_operations(self, flow_id: str) -> Optional[Dict]:
        """Get data operations from cache."""
        return self._get_from_cache(self._data_ops_cache, flow_id)
    
    def put_data_operations(self, flow_id: str, data: Dict) -> None:
        """Store data operations in cache."""
        self._put_to_cache(self._data_ops_cache, flow_id, data)
    
    def get_dependencies(self, flow_id: str) -> Optional[Dict]:
        """Get dependencies from cache."""
        return self._get_from_cache(self._dependencies_cache, flow_id)
    
    def put_dependencies(self, flow_id: str, data: Dict) -> None:
        """Store dependencies in cache."""
        self._put_to_cache(self._dependencies_cache, flow_id, data)
    
    def invalidate_flow(self, flow_id: str) -> None:
        """
        Invalidate all cached data for a specific flow.
        
        Args:
            flow_id: Flow ID to invalidate
        """
        self._evict_flow(flow_id)
        
        # Also remove from component caches
        self._scope_cache.pop(flow_id, None)
        self._interfaces_cache.pop(flow_id, None)
        self._data_ops_cache.pop(flow_id, None)
        self._dependencies_cache.pop(flow_id, None)
    
    def invalidate_all(self) -> None:
        """Clear all cached data."""
        self._flow_cache.clear()
        self._scope_cache.clear()
        self._interfaces_cache.clear()
        self._data_ops_cache.clear()
        self._dependencies_cache.clear()
        self._access_order.clear()
        
        logger.info("Flow cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics:
            - size: Current number of cached flows
            - max_size: Maximum cache size
            - hits: Number of cache hits
            - misses: Number of cache misses
            - hit_rate: Cache hit rate (0.0 to 1.0)
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self._flow_cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }
    
    def _get_from_cache(self, cache: Dict, flow_id: str) -> Optional[Dict]:
        """Generic get from cache with expiration check."""
        if flow_id in cache:
            data, timestamp = cache[flow_id]
            
            if self._is_expired(timestamp):
                cache.pop(flow_id, None)
                self.misses += 1
                return None
            
            self.hits += 1
            return data
        
        self.misses += 1
        return None
    
    def _put_to_cache(self, cache: Dict, flow_id: str, data: Dict) -> None:
        """Generic put to cache with timestamp."""
        cache[flow_id] = (data, datetime.now())
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cached entry has expired."""
        age = datetime.now() - timestamp
        return age.total_seconds() > self.ttl_seconds
    
    def _update_access(self, flow_id: str) -> None:
        """Update access order for LRU eviction."""
        # Remove from current position if exists
        if flow_id in self._access_order:
            self._access_order.remove(flow_id)
        
        # Add to end (most recently used)
        self._access_order.append(flow_id)
    
    def _evict_lru(self) -> None:
        """Evict least recently used flow from cache."""
        if not self._access_order:
            return
        
        # Get least recently used flow
        lru_flow_id = self._access_order[0]
        self._evict_flow(lru_flow_id)
        
        logger.debug(f"Evicted LRU flow from cache: {lru_flow_id}")
    
    def _evict_flow(self, flow_id: str) -> None:
        """Remove a flow from cache and access order."""
        self._flow_cache.pop(flow_id, None)
        
        if flow_id in self._access_order:
            self._access_order.remove(flow_id)


class QueryResultCache:
    """
    Cache for database query results.
    
    This cache stores results of common queries to avoid repeated
    database access. It's particularly useful for:
    - Flow ID lists
    - Filter results
    - Lookup queries
    """
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize the query result cache.
        
        Args:
            ttl_seconds: Time-to-live for cached results in seconds (default: 300 = 5 minutes)
        """
        self.ttl_seconds = ttl_seconds
        
        # Cache storage: query_key -> (result, timestamp)
        self._cache: Dict[str, tuple] = {}
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def get(self, query_key: str) -> Optional[Any]:
        """
        Get query result from cache.
        
        Args:
            query_key: Unique key identifying the query
            
        Returns:
            Cached result if available and not expired, None otherwise
        """
        if query_key in self._cache:
            result, timestamp = self._cache[query_key]
            
            # Check if expired
            if self._is_expired(timestamp):
                self._cache.pop(query_key, None)
                self.misses += 1
                return None
            
            self.hits += 1
            return result
        
        self.misses += 1
        return None
    
    def put(self, query_key: str, result: Any) -> None:
        """
        Store query result in cache.
        
        Args:
            query_key: Unique key identifying the query
            result: Query result to cache
        """
        self._cache[query_key] = (result, datetime.now())
    
    def invalidate(self, query_key: str) -> None:
        """
        Invalidate a specific cached query result.
        
        Args:
            query_key: Query key to invalidate
        """
        self._cache.pop(query_key, None)
    
    def invalidate_all(self) -> None:
        """Clear all cached query results."""
        self._cache.clear()
        logger.info("Query result cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self._cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cached entry has expired."""
        age = datetime.now() - timestamp
        return age.total_seconds() > self.ttl_seconds
