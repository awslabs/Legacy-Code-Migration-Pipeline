"""Package optimizer for migration planning."""

from typing import List, Set, Dict, Optional, Tuple
from collections import defaultdict
from ..models.package import MigrationPackage, PackageConstraints, PackageConflict


class PackageOptimizer:
    """
    Optimizes migration packages to minimize conflicts and external dependencies.
    
    Optimization strategies:
    - Minimize cross-package dependencies
    - Respect size constraints
    - Suggest optimal package boundaries
    - Resolve conflicts by reassigning artifacts
    """
    
    def __init__(self, database):
        """
        Initialize package optimizer.
        
        Args:
            database: Database connection with dependency data
        """
        self.database = database
        self.cursor = database.cursor()
    
    def suggest_packages(self,
                        artifacts: List[str],
                        constraints: Optional[PackageConstraints] = None,
                        target_package_count: Optional[int] = None) -> List[MigrationPackage]:
        """
        Suggest optimal package groupings for a set of artifacts.
        
        Uses clustering based on dependency relationships to group
        tightly coupled artifacts together.
        
        Args:
            artifacts: List of artifact names to package
            constraints: Package constraints to respect
            target_package_count: Desired number of packages (optional)
            
        Returns:
            List of suggested MigrationPackage objects
        """
        if not artifacts:
            return []
        
        # Build dependency graph
        dep_graph = self._build_dependency_graph(artifacts)
        
        # Find strongly connected components (tightly coupled groups)
        clusters = self._find_clusters(dep_graph, artifacts)
        
        # If target package count specified, merge/split clusters
        if target_package_count and len(clusters) != target_package_count:
            clusters = self._adjust_cluster_count(
                clusters, dep_graph, target_package_count, constraints
            )
        
        # Create packages from clusters
        packages = []
        for i, cluster in enumerate(clusters):
            package_name = f"Package_{i+1}"
            
            # Create package (will be populated by PackageBuilder)
            package = MigrationPackage(
                name=package_name,
                artifacts=list(cluster)
            )
            
            packages.append(package)
        
        return packages
    
    def optimize_packages(self,
                         packages: List[MigrationPackage],
                         constraints: Optional[PackageConstraints] = None) -> List[MigrationPackage]:
        """
        Optimize existing packages to reduce conflicts and external dependencies.
        
        Strategies:
        1. Move conflicting artifacts to the package with most dependencies
        2. Move artifacts to reduce external dependencies
        3. Split packages that exceed constraints
        4. Merge small packages that are tightly coupled
        
        Args:
            packages: List of MigrationPackage objects to optimize
            constraints: Package constraints to respect
            
        Returns:
            List of optimized MigrationPackage objects
        """
        optimized = [self._copy_package(p) for p in packages]
        
        # Step 1: Resolve conflicts
        optimized = self._resolve_conflicts(optimized)
        
        # Step 2: Reduce external dependencies
        optimized = self._reduce_external_dependencies(optimized)
        
        # Step 3: Split packages exceeding constraints
        if constraints:
            optimized = self._split_oversized_packages(optimized, constraints)
        
        # Step 4: Merge small tightly-coupled packages
        optimized = self._merge_small_packages(optimized, constraints)
        
        return optimized
    
    def minimize_cross_package_dependencies(self,
                                           packages: List[MigrationPackage]) -> List[MigrationPackage]:
        """
        Minimize dependencies between packages by reassigning artifacts.
        
        Args:
            packages: List of MigrationPackage objects
            
        Returns:
            List of optimized packages
        """
        optimized = [self._copy_package(p) for p in packages]
        
        # Calculate cross-package dependency count
        initial_cross_deps = self._count_cross_package_dependencies(optimized)
        
        # Try moving artifacts to reduce cross-package dependencies
        improved = True
        iterations = 0
        max_iterations = 10
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for package in optimized:
                for artifact in list(package.artifacts):
                    # Try moving artifact to each other package
                    best_package = package
                    best_cross_deps = initial_cross_deps
                    
                    for target_package in optimized:
                        if target_package == package:
                            continue
                        
                        # Temporarily move artifact
                        self._move_artifact(artifact, package, target_package)
                        
                        # Calculate new cross-package dependencies
                        new_cross_deps = self._count_cross_package_dependencies(optimized)
                        
                        if new_cross_deps < best_cross_deps:
                            best_cross_deps = new_cross_deps
                            best_package = target_package
                        
                        # Move back
                        self._move_artifact(artifact, target_package, package)
                    
                    # If found better placement, move permanently
                    if best_package != package:
                        self._move_artifact(artifact, package, best_package)
                        initial_cross_deps = best_cross_deps
                        improved = True
        
        return optimized
    
    def _build_dependency_graph(self, artifacts: List[str]) -> Dict[str, Set[str]]:
        """
        Build dependency graph for artifacts.
        
        Args:
            artifacts: List of artifact names
            
        Returns:
            Dictionary mapping artifact -> set of dependent artifacts
        """
        graph = defaultdict(set)
        
        # Query dependencies for all artifacts
        placeholders = ','.join('?' * len(artifacts))
        self.cursor.execute(f"""
            SELECT source_artifact, target_artifact
            FROM dependencies
            WHERE source_artifact IN ({placeholders})
            AND target_artifact IN ({placeholders})
        """, artifacts + artifacts)
        
        for source, target in self.cursor.fetchall():
            graph[source].add(target)
            # Add reverse edge for undirected clustering
            graph[target].add(source)
        
        # Ensure all artifacts are in graph
        for artifact in artifacts:
            if artifact not in graph:
                graph[artifact] = set()
        
        return graph
    
    def _find_clusters(self,
                      dep_graph: Dict[str, Set[str]],
                      artifacts: List[str]) -> List[Set[str]]:
        """
        Find clusters of tightly coupled artifacts using connected components.
        
        Args:
            dep_graph: Dependency graph
            artifacts: List of all artifacts
            
        Returns:
            List of clusters (sets of artifact names)
        """
        visited = set()
        clusters = []
        
        def dfs(node: str, cluster: Set[str]):
            """Depth-first search to find connected component."""
            if node in visited:
                return
            visited.add(node)
            cluster.add(node)
            
            for neighbor in dep_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, cluster)
        
        # Find all connected components
        for artifact in artifacts:
            if artifact not in visited:
                cluster = set()
                dfs(artifact, cluster)
                if cluster:
                    clusters.append(cluster)
        
        return clusters
    
    def _adjust_cluster_count(self,
                             clusters: List[Set[str]],
                             dep_graph: Dict[str, Set[str]],
                             target_count: int,
                             constraints: Optional[PackageConstraints]) -> List[Set[str]]:
        """
        Adjust number of clusters to match target count.
        
        Args:
            clusters: Current clusters
            dep_graph: Dependency graph
            target_count: Desired number of clusters
            constraints: Package constraints
            
        Returns:
            Adjusted list of clusters
        """
        if len(clusters) == target_count:
            return clusters
        
        if len(clusters) < target_count:
            # Need to split clusters
            return self._split_clusters(clusters, target_count, constraints)
        else:
            # Need to merge clusters
            return self._merge_clusters(clusters, dep_graph, target_count)
    
    def _split_clusters(self,
                       clusters: List[Set[str]],
                       target_count: int,
                       constraints: Optional[PackageConstraints]) -> List[Set[str]]:
        """Split large clusters to reach target count."""
        result = list(clusters)
        
        while len(result) < target_count:
            # Find largest cluster
            largest_idx = max(range(len(result)), key=lambda i: len(result[i]))
            largest = result[largest_idx]
            
            if len(largest) <= 1:
                break  # Can't split further
            
            # Split into two roughly equal parts
            artifacts = list(largest)
            mid = len(artifacts) // 2
            
            cluster1 = set(artifacts[:mid])
            cluster2 = set(artifacts[mid:])
            
            result[largest_idx] = cluster1
            result.append(cluster2)
        
        return result
    
    def _merge_clusters(self,
                       clusters: List[Set[str]],
                       dep_graph: Dict[str, Set[str]],
                       target_count: int) -> List[Set[str]]:
        """Merge clusters to reach target count."""
        result = list(clusters)
        
        while len(result) > target_count:
            # Find two clusters with most inter-cluster dependencies
            best_pair = None
            best_deps = 0
            
            for i in range(len(result)):
                for j in range(i + 1, len(result)):
                    deps = self._count_inter_cluster_deps(
                        result[i], result[j], dep_graph
                    )
                    if deps > best_deps:
                        best_deps = deps
                        best_pair = (i, j)
            
            if best_pair is None:
                # No dependencies between clusters, merge smallest two
                sizes = [(i, len(result[i])) for i in range(len(result))]
                sizes.sort(key=lambda x: x[1])
                best_pair = (sizes[0][0], sizes[1][0])
            
            # Merge clusters
            i, j = best_pair
            result[i] = result[i].union(result[j])
            result.pop(j)
        
        return result
    
    def _count_inter_cluster_deps(self,
                                  cluster1: Set[str],
                                  cluster2: Set[str],
                                  dep_graph: Dict[str, Set[str]]) -> int:
        """Count dependencies between two clusters."""
        count = 0
        for artifact in cluster1:
            for dep in dep_graph.get(artifact, set()):
                if dep in cluster2:
                    count += 1
        return count
    
    def _resolve_conflicts(self, packages: List[MigrationPackage]) -> List[MigrationPackage]:
        """
        Resolve conflicts by moving artifacts to package with most dependencies.
        
        Args:
            packages: List of packages
            
        Returns:
            List of packages with conflicts resolved
        """
        # Find all conflicts
        artifact_packages = defaultdict(list)
        for package in packages:
            for artifact in package.artifacts:
                artifact_packages[artifact].append(package)
        
        # Resolve each conflict
        for artifact, pkg_list in artifact_packages.items():
            if len(pkg_list) <= 1:
                continue  # No conflict
            
            # Count dependencies to each package
            dep_counts = {}
            for package in pkg_list:
                count = self._count_dependencies_to_package(artifact, package)
                dep_counts[package] = count
            
            # Keep artifact in package with most dependencies
            best_package = max(dep_counts, key=dep_counts.get)
            
            # Remove from other packages
            for package in pkg_list:
                if package != best_package and artifact in package.artifacts:
                    package.artifacts.remove(artifact)
                    # Also remove from type-specific lists
                    for lst in [package.programs, package.copybooks, package.jcl, package.datasets]:
                        if artifact in lst:
                            lst.remove(artifact)
        
        return packages
    
    def _reduce_external_dependencies(self, packages: List[MigrationPackage]) -> List[MigrationPackage]:
        """
        Reduce external dependencies by moving artifacts between packages.
        
        Args:
            packages: List of packages
            
        Returns:
            List of optimized packages
        """
        # For each package, check if external dependencies could be internalized
        for package in packages:
            for ext_dep in list(package.external_dependencies):
                # Find which package contains this external dependency
                containing_package = None
                for other_package in packages:
                    if ext_dep in other_package.artifacts:
                        containing_package = other_package
                        break
                
                if containing_package:
                    # Check if moving ext_dep to current package reduces total external deps
                    # This is a simplified heuristic
                    pass  # Complex optimization, skip for now
        
        return packages
    
    def _split_oversized_packages(self,
                                  packages: List[MigrationPackage],
                                  constraints: PackageConstraints) -> List[MigrationPackage]:
        """Split packages that exceed constraints."""
        result = []
        
        for package in packages:
            if constraints.is_valid(package):
                result.append(package)
            else:
                # Split package
                split_packages = self._split_package(package, constraints)
                result.extend(split_packages)
        
        return result
    
    def _split_package(self,
                      package: MigrationPackage,
                      constraints: PackageConstraints) -> List[MigrationPackage]:
        """Split a single package into smaller packages."""
        # Simple strategy: split artifacts into roughly equal groups
        artifacts = package.artifacts
        
        # Estimate how many packages needed
        if constraints.max_artifacts:
            num_packages = (len(artifacts) + constraints.max_artifacts - 1) // constraints.max_artifacts
        else:
            num_packages = 2  # Default split in half
        
        # Split artifacts
        chunk_size = (len(artifacts) + num_packages - 1) // num_packages
        split_packages = []
        
        for i in range(num_packages):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(artifacts))
            chunk_artifacts = artifacts[start:end]
            
            split_package = MigrationPackage(
                name=f"{package.name}_part{i+1}",
                artifacts=chunk_artifacts
            )
            split_packages.append(split_package)
        
        return split_packages
    
    def _merge_small_packages(self,
                             packages: List[MigrationPackage],
                             constraints: Optional[PackageConstraints]) -> List[MigrationPackage]:
        """Merge small tightly-coupled packages."""
        # Simple heuristic: merge packages with < 5 artifacts
        min_size = 5
        
        result = []
        small_packages = []
        
        for package in packages:
            if len(package.artifacts) < min_size:
                small_packages.append(package)
            else:
                result.append(package)
        
        # Merge small packages
        if small_packages:
            merged = MigrationPackage(
                name="Merged_Small_Packages",
                artifacts=[]
            )
            for package in small_packages:
                merged.artifacts.extend(package.artifacts)
            
            # Check if merged package respects constraints
            if constraints and not constraints.is_valid(merged):
                # Don't merge, keep separate
                result.extend(small_packages)
            else:
                result.append(merged)
        
        return result
    
    def _count_cross_package_dependencies(self, packages: List[MigrationPackage]) -> int:
        """Count total dependencies between packages."""
        count = 0
        
        for package in packages:
            for artifact in package.artifacts:
                # Get dependencies for this artifact
                self.cursor.execute("""
                    SELECT target_artifact
                    FROM dependencies
                    WHERE source_artifact = ?
                """, (artifact,))
                
                for (target,) in self.cursor.fetchall():
                    # Check if target is in a different package
                    for other_package in packages:
                        if other_package != package and target in other_package.artifacts:
                            count += 1
                            break
        
        return count
    
    def _count_dependencies_to_package(self,
                                      artifact: str,
                                      package: MigrationPackage) -> int:
        """Count dependencies from artifact to artifacts in package."""
        count = 0
        
        self.cursor.execute("""
            SELECT target_artifact
            FROM dependencies
            WHERE source_artifact = ?
        """, (artifact,))
        
        for (target,) in self.cursor.fetchall():
            if target in package.artifacts:
                count += 1
        
        return count
    
    def _copy_package(self, package: MigrationPackage) -> MigrationPackage:
        """Create a deep copy of a package."""
        return MigrationPackage(
            name=package.name,
            artifacts=list(package.artifacts),
            total_loc=package.total_loc,
            total_complexity=package.total_complexity,
            total_artifacts=package.total_artifacts,
            external_dependencies=list(package.external_dependencies),
            conflicts=list(package.conflicts),
            created_date=package.created_date,
            description=package.description,
            priority=package.priority,
            programs=list(package.programs),
            copybooks=list(package.copybooks),
            jcl=list(package.jcl),
            datasets=list(package.datasets)
        )
    
    def _move_artifact(self,
                      artifact: str,
                      from_package: MigrationPackage,
                      to_package: MigrationPackage) -> None:
        """Move an artifact from one package to another."""
        if artifact in from_package.artifacts:
            from_package.artifacts.remove(artifact)
            # Remove from type-specific lists
            for lst in [from_package.programs, from_package.copybooks, 
                       from_package.jcl, from_package.datasets]:
                if artifact in lst:
                    lst.remove(artifact)
        
        if artifact not in to_package.artifacts:
            to_package.artifacts.append(artifact)
            # Add to appropriate type-specific list (would need artifact type)
