#!/usr/bin/env python3
"""
Migration script to add missing columns to existing databases.

This script adds:
1. 'datasets' column to inventory_jcl table (JSON array of dataset references)
2. 'is_entry_point' column to inventory table (entry point flag for migration flows)

Usage:
    python3 tools/legacy_analyzer/migrations/add_missing_columns.py <database_path>
    
Example:
    python3 tools/legacy_analyzer/migrations/add_missing_columns.py databases/carddemo_presentation.db
"""

import sqlite3
import sys
from pathlib import Path


def add_missing_columns(db_path: str) -> None:
    """Add missing columns to existing database."""
    
    print(f"Migrating database: {db_path}")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check and add 'datasets' column to inventory_jcl
        print("\n1. Checking inventory_jcl table...")
        cursor.execute("PRAGMA table_info(inventory_jcl)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'datasets' not in columns:
            print("   Adding 'datasets' column...")
            cursor.execute("ALTER TABLE inventory_jcl ADD COLUMN datasets TEXT")
            conn.commit()
            print("   ✓ Added 'datasets' column to inventory_jcl")
        else:
            print("   ✓ 'datasets' column already exists")
        
        # Check and add 'is_entry_point' column to inventory
        print("\n2. Checking inventory table...")
        cursor.execute("PRAGMA table_info(inventory)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_entry_point' not in columns:
            print("   Adding 'is_entry_point' column...")
            cursor.execute("ALTER TABLE inventory ADD COLUMN is_entry_point INTEGER DEFAULT 0")
            conn.commit()
            print("   ✓ Added 'is_entry_point' column to inventory")
            
            # Create index for the new column
            print("   Creating index...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_is_entry_point ON inventory(is_entry_point)")
            conn.commit()
            print("   ✓ Created index idx_inv_is_entry_point")
        else:
            print("   ✓ 'is_entry_point' column already exists")
        
        print("\n" + "=" * 80)
        print("✓ Migration completed successfully")
        print("")
        
    except sqlite3.Error as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 add_missing_columns.py <database_path>")
        print("")
        print("Example:")
        print("  python3 add_missing_columns.py databases/carddemo_presentation.db")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)
    
    add_missing_columns(db_path)


if __name__ == "__main__":
    main()
