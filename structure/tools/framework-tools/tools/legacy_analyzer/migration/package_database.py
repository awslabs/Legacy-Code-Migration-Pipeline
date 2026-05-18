"""Database operations for migration packages."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.package import MigrationPackage


class PackageDatabase:
    """Manages database operations for migration packages."""
    
    def __init__(self, db_connection):
        """
        Initialize package database manager.
        
        Args:
            db_connection: Database connection object (e.g., sqlite3.Connection)
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def create_schema(self) -> None:
        """Create database tables for migration packages."""
        
        # Create migration_packages table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                total_artifacts INTEGER DEFAULT 0,
                total_loc INTEGER DEFAULT 0,
                total_complexity DECIMAL(10,2) DEFAULT 0.0,
                description TEXT,
                priority INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create package_artifacts table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS package_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER NOT NULL,
                artifact_name VARCHAR(44) NOT NULL,
                artifact_type VARCHAR(20) NOT NULL,
                FOREIGN KEY (package_id) REFERENCES migration_packages(id) ON DELETE CASCADE,
                UNIQUE(package_id, artifact_name)
            )
        """)
        
        # Create package_external_deps table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS package_external_deps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER NOT NULL,
                external_artifact VARCHAR(44) NOT NULL,
                dependency_type VARCHAR(20),
                FOREIGN KEY (package_id) REFERENCES migration_packages(id) ON DELETE CASCADE,
                UNIQUE(package_id, external_artifact)
            )
        """)
        
        # Create package_conflicts table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS package_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER NOT NULL,
                artifact_name VARCHAR(44) NOT NULL,
                FOREIGN KEY (package_id) REFERENCES migration_packages(id) ON DELETE CASCADE,
                UNIQUE(package_id, artifact_name)
            )
        """)
        
        # Create indexes for performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_package_name 
            ON migration_packages(name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_package_artifacts_package_id 
            ON package_artifacts(package_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_package_artifacts_name 
            ON package_artifacts(artifact_name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_package_external_deps_package_id 
            ON package_external_deps(package_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_package_conflicts_package_id 
            ON package_conflicts(package_id)
        """)
        
        self.conn.commit()
    
    def save_package(self, package: MigrationPackage) -> int:
        """
        Save a migration package to the database.
        
        Args:
            package: MigrationPackage object to save
            
        Returns:
            Package ID
        """
        # Check if package already exists
        self.cursor.execute(
            "SELECT id FROM migration_packages WHERE name = ?",
            (package.name,)
        )
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing package
            package_id = existing[0]
            self.cursor.execute("""
                UPDATE migration_packages
                SET total_artifacts = ?,
                    total_loc = ?,
                    total_complexity = ?,
                    description = ?,
                    priority = ?
                WHERE id = ?
            """, (
                package.total_artifacts,
                package.total_loc,
                package.total_complexity,
                package.description,
                package.priority,
                package_id
            ))
            
            # Delete old artifacts, external deps, and conflicts
            self.cursor.execute("DELETE FROM package_artifacts WHERE package_id = ?", (package_id,))
            self.cursor.execute("DELETE FROM package_external_deps WHERE package_id = ?", (package_id,))
            self.cursor.execute("DELETE FROM package_conflicts WHERE package_id = ?", (package_id,))
        else:
            # Insert new package
            self.cursor.execute("""
                INSERT INTO migration_packages (
                    name, total_artifacts, total_loc, total_complexity,
                    description, priority, created_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                package.name,
                package.total_artifacts,
                package.total_loc,
                package.total_complexity,
                package.description,
                package.priority,
                package.created_date or datetime.now()
            ))
            package_id = self.cursor.lastrowid
        
        # Insert artifacts
        for artifact in package.programs:
            self.cursor.execute("""
                INSERT INTO package_artifacts (package_id, artifact_name, artifact_type)
                VALUES (?, ?, ?)
            """, (package_id, artifact, 'PROGRAM'))
        
        for artifact in package.copybooks:
            self.cursor.execute("""
                INSERT INTO package_artifacts (package_id, artifact_name, artifact_type)
                VALUES (?, ?, ?)
            """, (package_id, artifact, 'COPYBOOK'))
        
        for artifact in package.jcl:
            self.cursor.execute("""
                INSERT INTO package_artifacts (package_id, artifact_name, artifact_type)
                VALUES (?, ?, ?)
            """, (package_id, artifact, 'JCL'))
        
        for artifact in package.datasets:
            self.cursor.execute("""
                INSERT INTO package_artifacts (package_id, artifact_name, artifact_type)
                VALUES (?, ?, ?)
            """, (package_id, artifact, 'DATASET'))
        
        # Insert external dependencies
        for ext_dep in package.external_dependencies:
            self.cursor.execute("""
                INSERT INTO package_external_deps (package_id, external_artifact)
                VALUES (?, ?)
            """, (package_id, ext_dep))
        
        # Insert conflicts
        for conflict in package.conflicts:
            self.cursor.execute("""
                INSERT INTO package_conflicts (package_id, artifact_name)
                VALUES (?, ?)
            """, (package_id, conflict))
        
        self.conn.commit()
        return package_id
    
    def load_package(self, name: str) -> Optional[MigrationPackage]:
        """
        Load a migration package from the database.
        
        Args:
            name: Package name
            
        Returns:
            MigrationPackage object or None if not found
        """
        # Get package record
        self.cursor.execute("""
            SELECT id, name, total_artifacts, total_loc, total_complexity,
                   description, priority, created_date
            FROM migration_packages
            WHERE name = ?
        """, (name,))
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        package_id, pkg_name, total_artifacts, total_loc, total_complexity, \
            description, priority, created_date = row
        
        # Get artifacts by type
        self.cursor.execute("""
            SELECT artifact_name, artifact_type
            FROM package_artifacts
            WHERE package_id = ?
            ORDER BY artifact_type, artifact_name
        """, (package_id,))
        
        programs = []
        copybooks = []
        jcl = []
        datasets = []
        all_artifacts = []
        
        for artifact_name, artifact_type in self.cursor.fetchall():
            all_artifacts.append(artifact_name)
            if artifact_type == 'PROGRAM':
                programs.append(artifact_name)
            elif artifact_type == 'COPYBOOK':
                copybooks.append(artifact_name)
            elif artifact_type == 'JCL':
                jcl.append(artifact_name)
            elif artifact_type == 'DATASET':
                datasets.append(artifact_name)
        
        # Get external dependencies
        self.cursor.execute("""
            SELECT external_artifact
            FROM package_external_deps
            WHERE package_id = ?
        """, (package_id,))
        
        external_deps = [row[0] for row in self.cursor.fetchall()]
        
        # Get conflicts
        self.cursor.execute("""
            SELECT artifact_name
            FROM package_conflicts
            WHERE package_id = ?
        """, (package_id,))
        
        conflicts = [row[0] for row in self.cursor.fetchall()]
        
        # Create MigrationPackage object
        package = MigrationPackage(
            name=pkg_name,
            artifacts=all_artifacts,
            total_loc=total_loc,
            total_complexity=total_complexity,
            total_artifacts=total_artifacts,
            external_dependencies=external_deps,
            conflicts=conflicts,
            created_date=created_date,
            description=description,
            priority=priority,
            programs=programs,
            copybooks=copybooks,
            jcl=jcl,
            datasets=datasets
        )
        
        return package
    
    def delete_package(self, name: str) -> bool:
        """
        Delete a migration package from the database.
        
        Args:
            name: Package name
            
        Returns:
            True if deleted, False if not found
        """
        self.cursor.execute(
            "DELETE FROM migration_packages WHERE name = ?",
            (name,)
        )
        self.conn.commit()
        
        return self.cursor.rowcount > 0
    
    def get_all_packages(self) -> List[Dict[str, Any]]:
        """
        Get summary of all packages in the database.
        
        Returns:
            List of package summary dictionaries
        """
        self.cursor.execute("""
            SELECT name, total_artifacts, total_loc, total_complexity,
                   priority, created_date
            FROM migration_packages
            ORDER BY priority ASC NULLS LAST, name
        """)
        
        packages = []
        for row in self.cursor.fetchall():
            packages.append({
                'name': row[0],
                'total_artifacts': row[1],
                'total_loc': row[2],
                'total_complexity': row[3],
                'priority': row[4],
                'created_date': row[5]
            })
        
        return packages
    
    def get_packages_containing_artifact(self, artifact_name: str) -> List[str]:
        """
        Get all packages that contain a specific artifact.
        
        Args:
            artifact_name: Artifact to search for
            
        Returns:
            List of package names
        """
        self.cursor.execute("""
            SELECT DISTINCT mp.name
            FROM migration_packages mp
            JOIN package_artifacts pa ON mp.id = pa.package_id
            WHERE pa.artifact_name = ?
            ORDER BY mp.name
        """, (artifact_name,))
        
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_package_conflicts(self) -> List[Dict[str, Any]]:
        """
        Get all artifacts that appear in multiple packages.
        
        Returns:
            List of conflict dictionaries with artifact_name and packages
        """
        self.cursor.execute("""
            SELECT pa.artifact_name, GROUP_CONCAT(mp.name, ', ') as packages, COUNT(*) as count
            FROM package_artifacts pa
            JOIN migration_packages mp ON pa.package_id = mp.id
            GROUP BY pa.artifact_name
            HAVING COUNT(*) > 1
            ORDER BY count DESC, pa.artifact_name
        """)
        
        conflicts = []
        for row in self.cursor.fetchall():
            conflicts.append({
                'artifact_name': row[0],
                'packages': row[1].split(', '),
                'count': row[2]
            })
        
        return conflicts
    
    def get_package_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all packages in the database.
        
        Returns:
            Dictionary with statistics
        """
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_packages,
                SUM(total_artifacts) as total_artifacts,
                AVG(total_artifacts) as avg_artifacts,
                MAX(total_artifacts) as max_artifacts,
                SUM(total_loc) as total_loc,
                AVG(total_loc) as avg_loc,
                SUM(total_complexity) as total_complexity,
                AVG(total_complexity) as avg_complexity
            FROM migration_packages
        """)
        
        row = self.cursor.fetchone()
        
        # Count packages with external dependencies
        self.cursor.execute("""
            SELECT COUNT(DISTINCT package_id)
            FROM package_external_deps
        """)
        packages_with_external = self.cursor.fetchone()[0] or 0
        
        # Count packages with conflicts
        self.cursor.execute("""
            SELECT COUNT(DISTINCT package_id)
            FROM package_conflicts
        """)
        packages_with_conflicts = self.cursor.fetchone()[0] or 0
        
        return {
            'total_packages': row[0] or 0,
            'total_artifacts': row[1] or 0,
            'avg_artifacts': round(row[2], 1) if row[2] else 0,
            'max_artifacts': row[3] or 0,
            'total_loc': row[4] or 0,
            'avg_loc': round(row[5], 1) if row[5] else 0,
            'total_complexity': round(row[6], 1) if row[6] else 0,
            'avg_complexity': round(row[7], 1) if row[7] else 0,
            'packages_with_external_deps': packages_with_external,
            'packages_with_conflicts': packages_with_conflicts
        }
