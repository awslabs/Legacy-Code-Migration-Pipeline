"""Caching utilities for Legacy Analyzer.

This module provides caching support for parsed source files and analysis results
to improve performance on subsequent runs.
"""

import os
import json
import pickle
import hashlib
import shutil
from pathlib import Path
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    file_path: Optional[str] = None
    file_mtime: Optional[float] = None
    file_hash: Optional[str] = None


class CacheManager:
    """Manages caching of parsed results and analysis data.
    
    The CacheManager provides file-based caching with support for:
    - Time-based expiration
    - File modification time tracking
    - Content hash-based invalidation
    - Size limits
    - Cache cleanup
    
    Example:
        >>> cache = CacheManager('.cache/legacy_analyzer')
        >>> cache.set('parsed_file', parsed_data, file_path='program.cbl')
        >>> data = cache.get('parsed_file', file_path='program.cbl')
    """
    
    def __init__(self, cache_dir: str = '.cache/legacy_analyzer',
                 expiration: int = 86400,
                 max_size_mb: int = 1000,
                 invalidation_strategy: str = 'mtime'):
        """Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files.
            expiration: Cache expiration time in seconds (0 = never expire).
            max_size_mb: Maximum cache size in MB (0 = unlimited).
            invalidation_strategy: Strategy for cache invalidation ('mtime', 'hash', 'manual').
        """
        self.cache_dir = Path(cache_dir)
        self.expiration = expiration
        self.max_size_mb = max_size_mb
        self.invalidation_strategy = invalidation_strategy
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file to track cache entries
        self.metadata_file = self.cache_dir / 'cache_metadata.json'
        self._metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """Load cache metadata from disk.
        
        Returns:
            Dictionary of cache metadata.
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self._metadata, f, indent=2)
        except IOError:
            pass  # Fail silently if we can't save metadata
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key.
        
        Args:
            key: Cache key.
            
        Returns:
            Path to cache file.
        """
        # Hash the key to create a safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of a file.
        
        Args:
            file_path: Path to file.
            
        Returns:
            Hexadecimal hash string.
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _is_valid(self, key: str, file_path: Optional[str] = None) -> bool:
        """Check if a cache entry is valid.
        
        Args:
            key: Cache key.
            file_path: Optional source file path for invalidation checking.
            
        Returns:
            True if cache entry is valid, False otherwise.
        """
        if key not in self._metadata:
            return False
        
        entry_meta = self._metadata[key]
        
        # Check expiration
        if self.expiration > 0:
            created_at = datetime.fromisoformat(entry_meta['created_at'])
            expires_at = created_at + timedelta(seconds=self.expiration)
            if datetime.now() > expires_at:
                return False
        
        # Check file-based invalidation
        if file_path and self.invalidation_strategy != 'manual':
            if not os.path.exists(file_path):
                return False
            
            if self.invalidation_strategy == 'mtime':
                # Check if file has been modified
                current_mtime = os.path.getmtime(file_path)
                cached_mtime = entry_meta.get('file_mtime')
                if cached_mtime is None or current_mtime > cached_mtime:
                    return False
            
            elif self.invalidation_strategy == 'hash':
                # Check if file content has changed
                current_hash = self._compute_file_hash(file_path)
                cached_hash = entry_meta.get('file_hash')
                if cached_hash is None or current_hash != cached_hash:
                    return False
        
        return True
    
    def get(self, key: str, file_path: Optional[str] = None) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key.
            file_path: Optional source file path for invalidation checking.
            
        Returns:
            Cached value or None if not found or invalid.
        """
        if not self._is_valid(key, file_path):
            return None
        
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, IOError):
            # Cache file is corrupted, remove it
            self.delete(key)
            return None
    
    def set(self, key: str, value: Any, file_path: Optional[str] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            file_path: Optional source file path for invalidation tracking.
        """
        cache_path = self._get_cache_path(key)
        
        # Serialize and save the value
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except (pickle.PickleError, IOError) as e:
            # If we can't cache, just continue without caching
            return
        
        # Update metadata
        entry_meta = {
            'key': key,
            'created_at': datetime.now().isoformat(),
            'cache_file': str(cache_path)
        }
        
        if file_path:
            entry_meta['file_path'] = file_path
            if os.path.exists(file_path):
                entry_meta['file_mtime'] = os.path.getmtime(file_path)
                if self.invalidation_strategy == 'hash':
                    entry_meta['file_hash'] = self._compute_file_hash(file_path)
        
        self._metadata[key] = entry_meta
        self._save_metadata()
        
        # Check cache size and cleanup if needed
        self._enforce_size_limit()
    
    def delete(self, key: str) -> None:
        """Delete a cache entry.
        
        Args:
            key: Cache key to delete.
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
        
        if key in self._metadata:
            del self._metadata[key]
            self._save_metadata()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        # Remove all cache files
        for cache_file in self.cache_dir.glob('*.cache'):
            cache_file.unlink()
        
        # Clear metadata
        self._metadata = {}
        self._save_metadata()
    
    def get_size_mb(self) -> float:
        """Get current cache size in MB.
        
        Returns:
            Cache size in megabytes.
        """
        total_size = 0
        for cache_file in self.cache_dir.glob('*.cache'):
            total_size += cache_file.stat().st_size
        return total_size / (1024 * 1024)
    
    def _enforce_size_limit(self) -> None:
        """Enforce cache size limit by removing oldest entries."""
        if self.max_size_mb <= 0:
            return  # No size limit
        
        current_size = self.get_size_mb()
        if current_size <= self.max_size_mb:
            return  # Within limit
        
        # Sort entries by creation time (oldest first)
        sorted_entries = sorted(
            self._metadata.items(),
            key=lambda x: x[1].get('created_at', '')
        )
        
        # Remove oldest entries until we're under the limit
        for key, entry_meta in sorted_entries:
            if current_size <= self.max_size_mb:
                break
            
            cache_path = Path(entry_meta.get('cache_file', ''))
            if cache_path.exists():
                size_mb = cache_path.stat().st_size / (1024 * 1024)
                cache_path.unlink()
                current_size -= size_mb
            
            del self._metadata[key]
        
        self._save_metadata()
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries.
        
        Returns:
            Number of entries removed.
        """
        if self.expiration <= 0:
            return 0  # No expiration
        
        removed_count = 0
        keys_to_remove = []
        
        for key in list(self._metadata.keys()):
            if not self._is_valid(key):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self.delete(key)
            removed_count += 1
        
        return removed_count
    
    def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        return {
            'total_entries': len(self._metadata),
            'size_mb': self.get_size_mb(),
            'max_size_mb': self.max_size_mb,
            'expiration_seconds': self.expiration,
            'invalidation_strategy': self.invalidation_strategy,
            'cache_dir': str(self.cache_dir)
        }
    
    def cached(self, key_func: Optional[Callable] = None, file_path_func: Optional[Callable] = None):
        """Decorator for caching function results.
        
        Args:
            key_func: Function to generate cache key from function arguments.
            file_path_func: Function to extract file path from function arguments.
            
        Returns:
            Decorator function.
            
        Example:
            >>> cache = CacheManager()
            >>> @cache.cached(key_func=lambda path: f"parsed_{path}")
            ... def parse_file(file_path):
            ...     # Expensive parsing operation
            ...     return parsed_data
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default: use function name and arguments
                    cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
                
                # Get file path for invalidation
                file_path = None
                if file_path_func:
                    file_path = file_path_func(*args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(cache_key, file_path)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, file_path)
                return result
            
            return wrapper
        return decorator


class ParseResultCache:
    """Specialized cache for parser results.
    
    This is a convenience wrapper around CacheManager specifically for
    caching parsed source file results.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize with a cache manager.
        
        Args:
            cache_manager: CacheManager instance to use.
        """
        self.cache = cache_manager
    
    def get_parsed_file(self, file_path: str) -> Optional[Any]:
        """Get cached parse result for a file.
        
        Args:
            file_path: Path to source file.
            
        Returns:
            Cached parse result or None.
        """
        cache_key = f"parsed_{file_path}"
        return self.cache.get(cache_key, file_path)
    
    def set_parsed_file(self, file_path: str, parse_result: Any) -> None:
        """Cache parse result for a file.
        
        Args:
            file_path: Path to source file.
            parse_result: Parse result to cache.
        """
        cache_key = f"parsed_{file_path}"
        self.cache.set(cache_key, parse_result, file_path)
    
    def invalidate_file(self, file_path: str) -> None:
        """Invalidate cache for a specific file.
        
        Args:
            file_path: Path to source file.
        """
        cache_key = f"parsed_{file_path}"
        self.cache.delete(cache_key)


class AnalysisResultCache:
    """Specialized cache for analysis results.
    
    This is a convenience wrapper around CacheManager specifically for
    caching analysis results (complexity, flow, etc.).
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize with a cache manager.
        
        Args:
            cache_manager: CacheManager instance to use.
        """
        self.cache = cache_manager
    
    def get_complexity(self, program_name: str) -> Optional[Any]:
        """Get cached complexity analysis for a program.
        
        Args:
            program_name: Name of the program.
            
        Returns:
            Cached complexity result or None.
        """
        cache_key = f"complexity_{program_name}"
        return self.cache.get(cache_key)
    
    def set_complexity(self, program_name: str, complexity_result: Any) -> None:
        """Cache complexity analysis for a program.
        
        Args:
            program_name: Name of the program.
            complexity_result: Complexity result to cache.
        """
        cache_key = f"complexity_{program_name}"
        self.cache.set(cache_key, complexity_result)
    
    def get_flow(self, start_program: str) -> Optional[Any]:
        """Get cached flow analysis for a program.
        
        Args:
            start_program: Starting program name.
            
        Returns:
            Cached flow result or None.
        """
        cache_key = f"flow_{start_program}"
        return self.cache.get(cache_key)
    
    def set_flow(self, start_program: str, flow_result: Any) -> None:
        """Cache flow analysis for a program.
        
        Args:
            start_program: Starting program name.
            flow_result: Flow result to cache.
        """
        cache_key = f"flow_{start_program}"
        self.cache.set(cache_key, flow_result)
