# Legacy Analyzer Utilities

This directory contains utility modules for the Legacy Analyzer system.

## Modules

### Configuration Management (`config.py`)

The `ConfigManager` class provides configuration loading, validation, and environment-specific configuration support.

**Features:**
- Load configuration from YAML files
- Environment-specific overrides (dev, test, prod)
- Configuration validation with clear error messages
- Type-safe configuration access through dataclasses
- Support for nested configuration keys with dot notation
- Save modified configuration back to YAML

**Example Usage:**
```python
from legacy_analyzer.utils import ConfigManager

# Load configuration
config = ConfigManager('config/legacy_analyzer.yaml')

# Get typed configuration objects
analysis_config = config.get_analysis_config()
print(f"Max flow depth: {analysis_config.max_flow_depth}")

# Get individual values with dot notation
max_workers = config.get('analysis.max_workers', default=4)

# Set configuration values
config.set('analysis.max_flow_depth', 20)

# Save configuration
config.save_config('config/custom_config.yaml')
```

**Environment-Specific Configuration:**
```python
# Load with environment override
config = ConfigManager('config/legacy_analyzer.yaml', environment='dev')

# Dev-specific settings will override defaults
```

### Caching (`cache.py`)

The `CacheManager` class provides file-based caching with support for expiration, file modification tracking, and size limits.

**Features:**
- Time-based cache expiration
- File modification time (mtime) invalidation
- Content hash-based invalidation
- Cache size limits with automatic cleanup
- Decorator support for easy function caching
- Specialized caches for parse results and analysis results

**Example Usage:**
```python
from legacy_analyzer.utils import CacheManager, ParseResultCache

# Create cache manager
cache = CacheManager(
    cache_dir='.cache/legacy_analyzer',
    expiration=86400,  # 24 hours
    max_size_mb=1000,
    invalidation_strategy='mtime'
)

# Basic caching
cache.set('my_key', {'data': 'value'})
result = cache.get('my_key')

# File-based caching with invalidation
cache.set('parsed_file', parse_result, file_path='program.cbl')
result = cache.get('parsed_file', file_path='program.cbl')

# Use decorator for automatic caching
@cache.cached(key_func=lambda path: f"parsed_{path}")
def parse_file(file_path):
    # Expensive parsing operation
    return parsed_data

# Specialized parse result cache
parse_cache = ParseResultCache(cache)
parse_cache.set_parsed_file('program.cbl', parse_result)
result = parse_cache.get_parsed_file('program.cbl')
```

**Cache Statistics:**
```python
stats = cache.get_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Cache size: {stats['size_mb']:.2f} MB")

# Cleanup expired entries
removed = cache.cleanup_expired()
print(f"Removed {removed} expired entries")
```

### Parallel Processing (`parallel.py`)

The `ParallelProcessor` class provides parallel processing support for file parsing and analysis operations.

**Features:**
- Multiprocessing and threading support
- Progress tracking with ETA
- Error handling and result collection
- Batch processing for small items
- Helper functions for common patterns
- Automatic worker count detection

**Example Usage:**
```python
from legacy_analyzer.utils import ParallelProcessor, parallel_map

# Create processor
processor = ParallelProcessor(max_workers=4, show_progress=True)

# Process items in parallel
def parse_file(file_path):
    # Parse the file
    return parsed_data

results = processor.process(parse_file, file_list)

# Check results
successful = [r for r in results if r.success]
failed = [r for r in results if not r.success]

print(f"Processed {len(successful)} files successfully")
print(f"Failed to process {len(failed)} files")

# Simple parallel map
file_list = ['file1.cbl', 'file2.cbl', 'file3.cbl']
parsed_results = parallel_map(parse_file, file_list, max_workers=4)
```

**Batch Processing:**
```python
from legacy_analyzer.utils import BatchProcessor

# Process many small items in batches
batch_processor = BatchProcessor(batch_size=100, max_workers=4)
results = batch_processor.process(process_item, items)
```

**Progress Tracking:**
```python
from legacy_analyzer.utils import ProgressTracker

tracker = ProgressTracker(total=1000, show_progress=True)

for item in items:
    # Process item
    success = process_item(item)
    tracker.update(success=success)

tracker.finish()

# Get progress information
progress = tracker.get_progress()
print(f"Completed: {progress.percent_complete:.1f}%")
print(f"Rate: {progress.items_per_second:.1f} items/sec")
```

## Configuration File

The default configuration file is located at `config/legacy_analyzer.yaml`. It contains comprehensive settings for:

- Analysis parameters (flow depth, circular detection, parallel processing)
- Complexity thresholds and weights
- Migration package constraints
- Parser settings for each language
- Dependency tracking configuration
- Visualization options
- Reporting formats
- Caching settings
- Database configuration
- Logging configuration
- Environment-specific overrides

See the configuration file for detailed documentation of all available options.

## Testing

Comprehensive unit tests are provided for all utility modules:

- `tests/test_config_manager.py` - Configuration management tests
- `tests/test_cache_manager.py` - Caching tests
- `tests/test_parallel_processor.py` - Parallel processing tests

Run tests with:
```bash
pytest tests/test_config_manager.py tests/test_cache_manager.py tests/test_parallel_processor.py -v
```

## Requirements

The utilities module requires:
- Python 3.7+
- PyYAML (for configuration loading)
- Standard library modules: multiprocessing, pickle, hashlib, pathlib

## Integration

These utilities are designed to be used throughout the Legacy Analyzer system:

- **Parsers** use caching to avoid re-parsing unchanged files
- **Analysis engines** use parallel processing for large codebases
- **All components** use configuration management for customization
- **CLI** uses progress tracking for user feedback

## Performance Considerations

- **Caching**: Reduces parsing time by 90%+ on subsequent runs
- **Parallel Processing**: Scales linearly with CPU cores for CPU-bound tasks
- **Configuration**: Minimal overhead, loaded once at startup
- **Memory**: Cache size limits prevent excessive memory usage

## Best Practices

1. **Configuration**: Load configuration once at application startup
2. **Caching**: Use file-based invalidation for source files
3. **Parallel Processing**: Use multiprocessing for CPU-bound tasks, threading for I/O-bound tasks
4. **Progress Tracking**: Always show progress for long-running operations
5. **Error Handling**: Check result.success before using result.result

## Future Enhancements

- Distributed caching (Redis, Memcached)
- Remote configuration management
- Advanced progress tracking (nested progress bars)
- Adaptive worker count based on system load
- Configuration hot-reloading
