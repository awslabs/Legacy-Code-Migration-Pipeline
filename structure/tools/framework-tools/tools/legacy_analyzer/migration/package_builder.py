"""Migration package builder for grouping artifacts."""

from typing import List, Set, Dict, Optional, Tuple
from datetime import datetime
from ..models.package import MigrationPackage, PackageConstraints, PackageConflict
from ..models.dependency import Dependency, DependencyType


class PackageBuilder:
    """
    Builds migration packages by grouping related artifacts.
    
    A migration package includes:
    - Seed artifacts (explicitly specified)
    - Transitive dependencies (automatically included)
    - Size metrics (LOC, complexity, artifact count)
    - External dependencies (artifacts outside the package)
    """
    
    def __init__(self, database):
        """
        Initialize package builder.
        
        Args:
            database: Database connection or adapter with dependency and complexity data
        """
        self.database = database
        # Handle both raw connections and adapters
        if hasattr(database, 'cursor') and callable(database.cursor):
            self.cursor = database.cursor()
        elif hasattr(database, 'cursor'):
            self.cursor = database.cursor
        else:
            raise ValueError("Database must have a cursor attribute or method")
        
        # Cache for tracking which artifacts are in which packages
        self._package_assignments: Dict[str, List[str]] = {}  # artifact -> [package_names]
    
    def create_package(self,
                      name: str,
                      seed_artifacts: List[str],
                      include_transitive: bool = True,
                      max_depth: Optional[int] = None,
                      constraints: Optional[PackageConstraints] = None) -> MigrationPackage:
        """
        Create a migration package from seed artifacts.
        
        Automatically includes transitive dependencies unless disabled.
        
        Args:
            name: Package name
            seed_artifacts: List of seed artifact names to start from
            include_transitive: Whether to include transitive dependencies (default True)
            max_depth: Maximum depth for transitive dependencies (None = unlimited)
            constraints: Package constraints to validate against
            
        Returns:
            MigrationPackage object
        """
        # Initialize package
        package = MigrationPackage(
            name=name,
            artifacts=[],
            created_date=datetime.now()
        )
        
        # Track artifacts to process and already processed
        to_process = set(seed_artifacts)
        processed = set()
        all_artifacts = set()
        
        # Track depth for each artifact
        artifact_depths = {artifact: 0 for artifact in seed_artifacts}
        
        # Process artifacts and their dependencies
        while to_process:
            current_artifact = to_process.pop()
            
            if current_artifact in processed:
                continue
            
            processed.add(current_artifact)
            all_artifacts.add(current_artifact)
            
            current_depth = artifact_depths.get(current_artifact, 0)
            
            # Get artifact type
            artifact_type = self._get_artifact_type(current_artifact)
            if artifact_type:
                package.add_artifact(current_artifact, artifact_type)
            
            # If including transitive dependencies, get dependencies
            if include_transitive:
                # Check depth limit
                if max_depth is not None and current_depth >= max_depth:
                    continue
                
                # Get dependencies for this artifact
                dependencies = self._get_dependencies(current_artifact)
                
                for dep in dependencies:
                    target = dep.target_artifact
                    
                    if target not in processed and target not in to_process:
                        to_process.add(target)
                        artifact_depths[target] = current_depth + 1
        
        # Calculate package metrics
        self._calculate_package_metrics(package)
        
        # Identify external dependencies
        self._identify_external_dependencies(package)
        
        # Track package assignment for conflict detection
        for artifact in package.artifacts:
            if artifact not in self._package_assignments:
                self._package_assignments[artifact] = []
            self._package_assignments[artifact].append(name)
        
        # Validate against constraints if provided
        if constraints:
            validation_errors = constraints.validate_package(package)
            if validation_errors:
                # Store validation errors in package description
                package.description = "Validation errors: " + "; ".join(validation_errors)
        
        return package
    
    def _get_artifact_type(self, artifact_name: str) -> Optional[str]:
        """
        Get the type of an artifact from the database.
        
        Args:
            artifact_name: Name of the artifact
            
        Returns:
            Artifact type (PROGRAM, COPYBOOK, JCL, DATASET) or None
        """
        # Try to find in programs table
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM inventory_programs WHERE program_name = ?",
                (artifact_name,)
            )
        except:
            # Try old table name
            self.cursor.execute(
                "SELECT COUNT(*) FROM programs WHERE program_name = ?",
                (artifact_name,)
            )
        if self.cursor.fetchone()[0] > 0:
            return 'PROGRAM'
        
        # Try copybooks table
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM inventory_copybooks WHERE copybook_name = ?",
                (artifact_name,)
            )
        except:
            # Try old table name
            self.cursor.execute(
                "SELECT COUNT(*) FROM copybooks WHERE copybook_name = ?",
                (artifact_name,)
            )
        if self.cursor.fetchone()[0] > 0:
            return 'COPYBOOK'
        
        # Try JCL table
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM inventory_jcl WHERE member_name = ?",
                (artifact_name,)
            )
        except:
            # Try old table name
            self.cursor.execute(
                "SELECT COUNT(*) FROM jcl WHERE member_name = ?",
                (artifact_name,)
            )
        if self.cursor.fetchone()[0] > 0:
            return 'JCL'
        
        # Try datasets table
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM inventory_datasets WHERE dataset_name = ?",
                (artifact_name,)
            )
        except:
            # Try old table name
            self.cursor.execute(
                "SELECT COUNT(*) FROM datasets WHERE dataset_name = ?",
                (artifact_name,)
            )
        if self.cursor.fetchone()[0] > 0:
            return 'DATASET'
        
        return None
    
    def _get_dependencies(self, artifact_name: str) -> List[Dependency]:
        """
        Get all dependencies for an artifact.
        
        Args:
            artifact_name: Name of the artifact
            
        Returns:
            List of Dependency objects
        """
        dependencies = []
        
        # Query artifact_dependencies table
        self.cursor.execute("""
            SELECT source_artifact_name, source_artifact_type, target_artifact_name, target_artifact_type,
                   dependency_type, source_file_path, line_number
            FROM artifact_dependencies
            WHERE source_artifact_name = ?
        """, (artifact_name,))
        
        for row in self.cursor.fetchall():
            dep = Dependency(
                source_artifact=row[0],
                source_type=row[1],
                target_artifact=row[2],
                target_type=row[3],
                dependency_type=row[4],
                source_file=row[5],
                line_number=row[6]
            )
            dependencies.append(dep)
        
        return dependencies
    
    def _calculate_package_metrics(self, package: MigrationPackage) -> None:
        """
        Calculate size metrics for a package.
        
        Updates package.total_loc and package.total_complexity.
        
        Args:
            package: MigrationPackage to update
        """
        total_loc = 0
        total_complexity = 0.0
        
        # Check if complexity_metrics table exists
        complexity_table_exists = self._check_complexity_table_exists()
        
        # Get complexity metrics for programs in package
        for program in package.programs:
            if complexity_table_exists:
                try:
                    self.cursor.execute("""
                        SELECT lines_of_code, composite_score
                        FROM complexity_metrics
                        WHERE program_name = ?
                    """, (program,))
                    
                    row = self.cursor.fetchone()
                    if row:
                        total_loc += row[0] or 0
                        total_complexity += row[1] or 0.0
                    else:
                        # Estimate if not in complexity table
                        total_loc += 200  # Default estimate for programs
                except Exception:
                    # If query fails, fall back to estimation
                    total_loc += 200
            else:
                # Estimate if complexity table doesn't exist
                total_loc += 200  # Default estimate for programs
        
        # For copybooks and JCL, estimate LOC if not in complexity table
        for artifact in package.copybooks + package.jcl:
            if complexity_table_exists:
                try:
                    # Try to get from complexity table first
                    self.cursor.execute("""
                        SELECT lines_of_code, composite_score
                        FROM complexity_metrics
                        WHERE program_name = ?
                    """, (artifact,))
                    
                    row = self.cursor.fetchone()
                    if row:
                        total_loc += row[0] or 0
                        total_complexity += row[1] or 0.0
                    else:
                        # Estimate from artifact type
                        if artifact in package.copybooks:
                            # Copybooks typically smaller, estimate 100 LOC
                            total_loc += 100
                        elif artifact in package.jcl:
                            # JCL typically small, estimate 50 LOC
                            total_loc += 50
                except Exception:
                    # If query fails, fall back to estimation
                    if artifact in package.copybooks:
                        total_loc += 100
                    elif artifact in package.jcl:
                        total_loc += 50
            else:
                # Estimate if complexity table doesn't exist
                if artifact in package.copybooks:
                    total_loc += 100
                elif artifact in package.jcl:
                    total_loc += 50
        
        package.total_loc = total_loc
        package.total_complexity = total_complexity
    
    def _check_complexity_table_exists(self) -> bool:
        """
        Check if complexity_metrics table exists in the database.
        
        Returns:
            True if table exists, False otherwise
        """
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='complexity_metrics'
            """)
            return self.cursor.fetchone() is not None
        except Exception:
            return False
    
    def _identify_external_dependencies(self, package: MigrationPackage) -> None:
        """
        Identify external dependencies (artifacts outside the package).
        
        Updates package.external_dependencies.
        
        Args:
            package: MigrationPackage to update
        """
        external_deps = set()
        
        # For each artifact in package, check its dependencies
        for artifact in package.artifacts:
            dependencies = self._get_dependencies(artifact)
            
            for dep in dependencies:
                target = dep.target_artifact
                
                # If target is not in package, it's an external dependency
                if target not in package.artifacts:
                    external_deps.add(target)
        
        package.external_dependencies = list(external_deps)
    
    def detect_conflicts(self, packages: List[MigrationPackage]) -> List[PackageConflict]:
        """
        Detect artifacts that appear in multiple packages.
        
        Args:
            packages: List of MigrationPackage objects
            
        Returns:
            List of PackageConflict objects
        """
        # Build artifact -> packages mapping
        artifact_packages: Dict[str, List[str]] = {}
        
        for package in packages:
            for artifact in package.artifacts:
                if artifact not in artifact_packages:
                    artifact_packages[artifact] = []
                artifact_packages[artifact].append(package.name)
        
        # Find conflicts (artifacts in multiple packages)
        conflicts = []
        for artifact, package_names in artifact_packages.items():
            if len(package_names) > 1:
                conflicts.append(PackageConflict(
                    artifact_name=artifact,
                    packages=package_names
                ))
                
                # Update package conflict lists
                for package in packages:
                    if artifact in package.artifacts:
                        package.add_conflict(artifact)
        
        return conflicts
    
    def validate_package(self,
                        package: MigrationPackage,
                        constraints: Optional[PackageConstraints] = None) -> Tuple[bool, List[str]]:
        """
        Validate a package against constraints.
        
        Args:
            package: MigrationPackage to validate
            constraints: PackageConstraints (optional)
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check if package is self-contained
        if not package.is_self_contained():
            errors.append(
                f"Package has {len(package.external_dependencies)} external dependencies"
            )
        
        # Check for conflicts
        if package.has_conflicts():
            errors.append(
                f"Package has {len(package.conflicts)} conflicting artifacts"
            )
        
        # Validate against constraints if provided
        if constraints:
            constraint_errors = constraints.validate_package(package)
            errors.extend(constraint_errors)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_package_statistics(self, packages: List[MigrationPackage]) -> Dict:
        """
        Get statistics about a set of packages.
        
        Args:
            packages: List of MigrationPackage objects
            
        Returns:
            Dictionary with statistics
        """
        total_artifacts = sum(p.total_artifacts for p in packages)
        total_loc = sum(p.total_loc for p in packages)
        total_complexity = sum(p.total_complexity for p in packages)
        
        # Count packages with external dependencies
        packages_with_external = sum(
            1 for p in packages if len(p.external_dependencies) > 0
        )
        
        # Count packages with conflicts
        packages_with_conflicts = sum(
            1 for p in packages if p.has_conflicts()
        )
        
        # Average metrics
        avg_artifacts = total_artifacts / len(packages) if packages else 0
        avg_loc = total_loc / len(packages) if packages else 0
        avg_complexity = total_complexity / len(packages) if packages else 0
        
        return {
            'total_packages': len(packages),
            'total_artifacts': total_artifacts,
            'total_loc': total_loc,
            'total_complexity': total_complexity,
            'avg_artifacts_per_package': round(avg_artifacts, 1),
            'avg_loc_per_package': round(avg_loc, 1),
            'avg_complexity_per_package': round(avg_complexity, 1),
            'packages_with_external_deps': packages_with_external,
            'packages_with_conflicts': packages_with_conflicts
        }
