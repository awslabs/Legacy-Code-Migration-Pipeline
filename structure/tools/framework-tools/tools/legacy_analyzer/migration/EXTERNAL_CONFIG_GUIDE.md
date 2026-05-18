# External Program Configuration Guide

## Overview

The external program configuration feature allows you to define which programs are outside your migration boundary (external) and which external systems call into your codebase. This helps accurately identify flow boundaries and interfaces.

## Quick Start

### 1. Create Configuration File

Create a YAML file (e.g., `external_config.yaml`):

```yaml
external_programs:
  - pattern: "UTIL*"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  - name: "DBUTIL"
    type: "DATABASE_UTILITY"
    scope: "EXTERNAL"

external_callers:
  - caller: "EXTERNAL_SYSTEM_A"
    calls:
      - target: "PAYCALC"
        type: "PROGRAM_CALL"
```

### 2. Load Configuration

```python
from tools.legacy_analyzer.migration import load_external_config

# Load configuration into database
result = load_external_config(db_connection, 'external_config.yaml')
print(f"Loaded {result['programs_loaded']} programs")
```

### 3. Use Configuration

```python
from tools.legacy_analyzer.migration import is_external_program

# Check if program is external
if is_external_program(db_connection, 'UTIL123'):
    print("Program is external - exclude from scope")
```

## Configuration Format

### External Programs

Define programs that are outside your migration boundary:

```yaml
external_programs:
  # Pattern-based (with wildcards)
  - pattern: "UTIL*"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  - pattern: "COMMON?"
    type: "UTILITY"
    scope: "EXTERNAL"
  
  # Exact name
  - name: "DBUTIL"
    type: "DATABASE_UTILITY"
    scope: "EXTERNAL"
```

**Fields:**
- `pattern` or `name` (required): Program pattern or exact name
- `type` (optional): Program type (e.g., UTILITY, DATABASE_UTILITY, LOGGING)
- `scope` (optional): Scope (typically EXTERNAL)

**Wildcard Patterns:**
- `*` - Matches any characters (e.g., `UTIL*` matches UTIL, UTIL1, UTIL123)
- `?` - Matches single character (e.g., `PROG?` matches PROG1, PROGA)

### External Callers

Define external systems that call into your codebase:

```yaml
external_callers:
  - caller: "EXTERNAL_SYSTEM_A"
    calls:
      - target: "PAYCALC"
        type: "PROGRAM_CALL"
        system: "EXTERNAL_SYSTEM_A"
        description: "Legacy batch system"
      
      - target: "BILLING1"
        type: "CICS_LINK"
        transaction: "BILL"
```

**Fields:**
- `caller` (required): Name of external caller
- `calls` (required): List of calls from this caller
  - `target` (required): Target program name
  - `type` (optional): Call type (PROGRAM_CALL, CICS_LINK, etc.)
  - Additional fields stored as metadata

## API Reference

### Loading Configuration

```python
from tools.legacy_analyzer.migration import load_external_config

# Load configuration
result = load_external_config(
    db_connection,
    config_path='external_config.yaml',
    verbose=True
)

# Returns:
# {
#     'programs_loaded': 5,
#     'callers_loaded': 3,
#     'config_path': 'external_config.yaml'
# }
```

### Checking External Programs

```python
from tools.legacy_analyzer.migration import is_external_program

# Check if program is external
is_external = is_external_program(db_connection, 'UTIL123')
# Returns: True or False
```

### Getting External Callers

```python
from tools.legacy_analyzer.migration import get_external_callers

# Get all external callers
callers = get_external_callers(db_connection)
# Returns: {'EXTERNAL_SYSTEM_A': [{'target': 'PAYCALC', ...}], ...}

# Get callers for specific target
callers = get_external_callers(db_connection, target_program='BILLING1')
# Returns: {'LEGACY_BILLING': [{'target': 'BILLING1', ...}]}
```

### Advanced Usage

```python
from tools.legacy_analyzer.migration import ExternalConfigLoader

loader = ExternalConfigLoader(db_connection)

# Load configuration
loader.load_external_config('external_config.yaml')

# Check external programs
loader.is_external_program('DBUTIL')  # True (exact match)
loader.is_external_program('UTIL123')  # True (pattern match)

# Get external programs (exact matches only)
programs = loader.get_external_programs()
# Returns: {'DBUTIL', 'LOGGER', ...}

# Get external patterns
patterns = loader.get_external_patterns()
# Returns: ['UTIL*', 'COMMON*', ...]

# Check pattern matching
matches, pattern = loader.matches_external_pattern('UTIL123')
# Returns: (True, 'UTIL*')

# Get configuration summary
summary = loader.get_config_summary()
# Returns: {
#     'total_external_programs': 5,
#     'pattern_programs': 2,
#     'exact_programs': 3,
#     'unique_external_callers': 2,
#     'total_external_calls': 4
# }

# Clear configuration
loader.clear_external_config()
```

## Use Cases

### 1. Excluding Utility Programs

```yaml
external_programs:
  - pattern: "UTIL*"
    type: "UTILITY"
  - pattern: "COMMON*"
    type: "UTILITY"
  - name: "ERRHANDLER"
    type: "ERROR_HANDLER"
```

**Effect:** Programs matching these patterns will be excluded from flow scope and treated as external dependencies.

### 2. Defining External System Interfaces

```yaml
external_callers:
  - caller: "LEGACY_BILLING_SYSTEM"
    calls:
      - target: "BILLING1"
        type: "CICS_LINK"
        system: "LEGACY_BILLING"
      - target: "BILLING2"
        type: "PROGRAM_CALL"
```

**Effect:** Creates inbound interfaces for BILLING1 and BILLING2 from the external system.

### 3. Database Utilities

```yaml
external_programs:
  - name: "DBUTIL"
    type: "DATABASE_UTILITY"
  - name: "SQLEXEC"
    type: "DATABASE_UTILITY"
```

**Effect:** Database utility programs are treated as external, simplifying flow boundaries.

### 4. Logging and Monitoring

```yaml
external_programs:
  - pattern: "LOG*"
    type: "LOGGING"
  - pattern: "MON*"
    type: "MONITORING"
```

**Effect:** Logging and monitoring programs are excluded from migration scope.

## Pattern Matching Examples

| Pattern | Matches | Does Not Match |
|---------|---------|----------------|
| `UTIL*` | UTIL, UTIL1, UTIL123, UTILPROG | XUTIL, NOTUTIL |
| `*UTIL` | DBUTIL, FILEUTIL, UTIL | UTIL1, UTILPROG |
| `PROG?` | PROG1, PROGA, PROGX | PROG, PROG12 |
| `*PROG*` | MYPROG, PROG1, TESTPROG | PROGRAM (no match) |
| `COMMON??` | COMMON01, COMMONAB | COMMON, COMMON1 |

## Error Handling

### Invalid Configuration

```python
try:
    load_external_config(db_connection, 'invalid.yaml')
except ExternalConfigError as e:
    print(f"Configuration error: {e}")
```

### Common Errors

1. **Missing required fields:**
   ```
   ExternalConfigError: external_programs[0] must have 'pattern' or 'name'
   ```

2. **Invalid YAML syntax:**
   ```
   ExternalConfigError: Invalid YAML syntax: ...
   ```

3. **File not found:**
   ```
   ExternalConfigError: Configuration file not found: external_config.yaml
   ```

## Best Practices

1. **Use patterns for groups:** Define patterns for utility programs, common libraries, etc.
   ```yaml
   - pattern: "UTIL*"
   - pattern: "COMMON*"
   ```

2. **Use exact names for specific programs:** Define exact names for known external programs.
   ```yaml
   - name: "DBUTIL"
   - name: "LOGGER"
   ```

3. **Document external callers:** Add metadata to external callers for documentation.
   ```yaml
   - caller: "EXTERNAL_SYSTEM"
     calls:
       - target: "PROG1"
         description: "Called from legacy batch system"
         system: "EXTERNAL_SYSTEM"
   ```

4. **Validate configuration:** Test configuration with demo script before using in production.
   ```bash
   python tools/legacy_analyzer/migration/demo_external_config.py
   ```

5. **Version control:** Keep external configuration in version control with your code.

## Integration with Flow Export

The external configuration is used during migration flow export:

1. **Scope Identification:** External programs are excluded from flow scope
2. **Interface Identification:** 
   - Calls to external programs create outbound interfaces
   - External callers create inbound interfaces
3. **Flow Building:** External configuration is loaded at initialization

## Testing

### Run Unit Tests
```bash
python -m pytest tests/unit/test_legacy_analyzer/test_external_config.py -v
```

### Run Demo Script
```bash
python tools/legacy_analyzer/migration/demo_external_config.py
```

## Troubleshooting

### Configuration not loading

**Problem:** Configuration file not found
**Solution:** Check file path is correct and file exists

### Pattern not matching

**Problem:** Program not recognized as external
**Solution:** Verify pattern syntax and test with `matches_external_pattern()`

### Metadata not stored

**Problem:** Caller metadata not appearing
**Solution:** Ensure metadata fields are not named 'target' or 'type' (reserved)

## Examples

See the following files for complete examples:
- `demo_external_config.py` - Demonstration script
- `test_external_config.py` - Unit tests with examples
- `TASK_4A_COMPLETE.md` - Implementation details

## Support

For issues or questions:
1. Check unit tests for usage examples
2. Run demo script to verify setup
3. Review error messages for specific issues
4. Consult implementation documentation
