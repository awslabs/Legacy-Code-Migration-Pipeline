# Database Schemas Module

## Overview

The `shared/database/schemas/` module provides centralized database schema definitions for mainframe analysis tools. This module serves as a shared resource for:

- **legacy_analyzer**: Analyzing mainframe artifacts and dependencies

## Architecture

```
shared/database/schemas/
├── __init__.py              # Main module exports
├── inventory_schema.py      # Mainframe artifact inventory tables
├── unified_schema.py       # Combined schema for all record types
├── registry.py             # Schema registry for dynamic schema management
└── README.md               # This file
```

## Schema Types

### 1. Inventory Schema

The `InventorySchema` defines tables for storing mainframe artifact catalogs:

- **inventory_jcl**: JCL members and job definitions
- **inventory_programs**: Compiled programs and load modules
- **inventory_copybooks**: COBOL copybooks and include files
- **inventory_datasets**: MVS datasets and VSAM files
- **inventory_cics**: CICS resources (transactions, programs, files, mapsets)

The `inventory` table serves as the authoritative source for artifact metadata, including programming language information.




### 3. Unified Schema


### 4. Schema Registry

The `SchemaRegistry` provides dynamic schema management for registering and retrieving schemas by record type.

## Usage Examples

### Loading Inventory Data

```python
from shared.database.schemas import InventorySchema

# Create loader with inventory schema
schema = InventorySchema()
db = SQLiteAdapter('analysis.db')

# Tables are created automatically
loader.create_tables()
```


```python


```

## Migration from database_schemas


### Migration Guide

**Before (old imports):**
```python
```

**After (new imports):**
```python
```

### Backward Compatibility

