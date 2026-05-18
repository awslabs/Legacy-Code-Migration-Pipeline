"""
Sorting Strategies for JCL Job Export

This module provides pluggable sorting strategies for organizing exported JCL jobs.
Each strategy implements a different sorting approach to help migration engineers
view jobs in the most useful order for their specific task.

Available strategies:
- NameSortingStrategy: Alphabetical sorting by job name
- TypeSortingStrategy: Group by job type (APPLICATION vs INFRASTRUCTURE)
- DependencySortingStrategy: Topological sort based on dependencies
- ComplexitySortingStrategy: Sort by complexity (number of steps)
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Set

# Configure logging
logger = logging.getLogger(__name__)


class SortingStrategy(ABC):
    """
    Abstract base class for job sorting strategies.
    
    All sorting strategies must inherit from this class and implement
    the sort() method. This provides a consistent interface for applying
    different sorting approaches to job lists.
    """
    
    @abstractmethod
    def sort(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort jobs according to the strategy's algorithm.
        
        Args:
            jobs: List of job dictionaries to sort
            
        Returns:
            New list of jobs sorted according to the strategy
            
        Note:
            Implementations should not modify the input list in place.
            They should return a new sorted list.
        """
        pass



class NameSortingStrategy(SortingStrategy):
    """
    Sort jobs alphabetically by job name.
    
    This is the simplest and most predictable sorting strategy. Jobs are
    sorted in ascending alphabetical order by their jobName field. This
    makes it easy to locate specific jobs and provides a consistent ordering.
    
    Example:
        >>> strategy = NameSortingStrategy()
        >>> jobs = [{'jobName': 'JOBZ'}, {'jobName': 'JOBA'}, {'jobName': 'JOBM'}]
        >>> sorted_jobs = strategy.sort(jobs)
        >>> [j['jobName'] for j in sorted_jobs]
        ['JOBA', 'JOBM', 'JOBZ']
    """
    
    def sort(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort jobs alphabetically by jobName.
        
        Args:
            jobs: List of job dictionaries to sort
            
        Returns:
            New list of jobs sorted alphabetically by jobName
            
        Note:
            The sort is case-sensitive and uses Python's default string
            comparison. Jobs without a jobName field are placed at the end.
        """
        logger.debug(f"Sorting {len(jobs)} jobs by name")
        
        # Sort by jobName field, handling missing jobName gracefully
        sorted_jobs = sorted(
            jobs,
            key=lambda job: job.get('jobName', '')
        )
        
        logger.debug("Name sorting completed")
        return sorted_jobs



class TypeSortingStrategy(SortingStrategy):
    """
    Sort jobs by type, grouping APPLICATION jobs before INFRASTRUCTURE jobs.
    
    This strategy helps migration engineers prioritize work by separating
    jobs that contain business logic (APPLICATION) from those that only
    perform infrastructure tasks (INFRASTRUCTURE). Within each group,
    jobs are sorted alphabetically by name for consistency.
    
    Sort order:
    1. APPLICATION jobs (sorted by name)
    2. INFRASTRUCTURE jobs (sorted by name)
    
    Example:
        >>> strategy = TypeSortingStrategy()
        >>> jobs = [
        ...     {'jobName': 'INFRA1', 'jobType': 'INFRASTRUCTURE'},
        ...     {'jobName': 'APP2', 'jobType': 'APPLICATION'},
        ...     {'jobName': 'APP1', 'jobType': 'APPLICATION'}
        ... ]
        >>> sorted_jobs = strategy.sort(jobs)
        >>> [(j['jobName'], j['jobType']) for j in sorted_jobs]
        [('APP1', 'APPLICATION'), ('APP2', 'APPLICATION'), ('INFRA1', 'INFRASTRUCTURE')]
    """
    
    def sort(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort jobs by type (APPLICATION first, then INFRASTRUCTURE).
        
        Within each type group, jobs are sorted alphabetically by name.
        
        Args:
            jobs: List of job dictionaries to sort
            
        Returns:
            New list of jobs sorted by type, then by name
            
        Note:
            Jobs without a jobType field are treated as INFRASTRUCTURE
            and placed at the end. The sort is stable, preserving the
            relative order of jobs with the same type and name.
        """
        logger.debug(f"Sorting {len(jobs)} jobs by type")
        
        # Define sort order for job types
        # APPLICATION = 0 (comes first)
        # INFRASTRUCTURE = 1 (comes second)
        # Unknown/missing = 2 (comes last)
        type_order = {
            'APPLICATION': 0,
            'INFRASTRUCTURE': 1
        }
        
        # Sort by type (using order mapping), then by name
        sorted_jobs = sorted(
            jobs,
            key=lambda job: (
                type_order.get(job.get('jobType', ''), 2),  # Type order
                job.get('jobName', '')  # Name within type
            )
        )
        
        # Log statistics
        app_count = sum(1 for job in sorted_jobs if job.get('jobType') == 'APPLICATION')
        infra_count = sum(1 for job in sorted_jobs if job.get('jobType') == 'INFRASTRUCTURE')
        logger.debug(
            f"Type sorting completed: {app_count} APPLICATION jobs, "
            f"{infra_count} INFRASTRUCTURE jobs"
        )
        
        return sorted_jobs



class DependencySortingStrategy(SortingStrategy):
    """
    Sort jobs in dependency execution order using topological sort.
    
    This strategy arranges jobs so that dependencies are respected:
    if job A must run before job B, then A appears before B in the sorted list.
    This is useful for understanding execution order and planning migration
    sequences.
    
    The implementation uses Kahn's algorithm for topological sorting, which:
    1. Identifies jobs with no dependencies (in-degree = 0)
    2. Processes them in order, removing their edges from the graph
    3. Repeats until all jobs are processed
    
    Circular dependencies are detected and handled gracefully:
    - A warning is logged
    - Jobs involved in cycles are sorted by name and placed at the end
    
    Example:
        >>> strategy = DependencySortingStrategy()
        >>> jobs = [
        ...     {'jobName': 'JOB3', 'dependencies': {'mustRunAfter': ['JOB2'], 'mustRunBefore': []}},
        ...     {'jobName': 'JOB1', 'dependencies': {'mustRunAfter': [], 'mustRunBefore': ['JOB2']}},
        ...     {'jobName': 'JOB2', 'dependencies': {'mustRunAfter': ['JOB1'], 'mustRunBefore': ['JOB3']}}
        ... ]
        >>> sorted_jobs = strategy.sort(jobs)
        >>> [j['jobName'] for j in sorted_jobs]
        ['JOB1', 'JOB2', 'JOB3']
    """
    
    def sort(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort jobs using topological sort based on dependencies.
        
        Args:
            jobs: List of job dictionaries to sort
            
        Returns:
            New list of jobs sorted in dependency execution order
            
        Note:
            If circular dependencies are detected, affected jobs are
            sorted by name and placed at the end of the list. A warning
            is logged with details about the circular dependency.
        """
        logger.debug(f"Sorting {len(jobs)} jobs by dependencies")
        
        if not jobs:
            return []
        
        # Build job name to job mapping for quick lookup
        job_map = {job['jobName']: job for job in jobs}
        
        # Build dependency graph
        # in_degree: number of jobs that must run before this job
        # out_edges: jobs that must run after this job
        in_degree: Dict[str, int] = {}
        out_edges: Dict[str, List[str]] = {}
        
        # Initialize all jobs
        for job in jobs:
            job_name = job['jobName']
            in_degree[job_name] = 0
            out_edges[job_name] = []
        
        # Build the graph from dependencies
        for job in jobs:
            job_name = job['jobName']
            dependencies = job.get('dependencies', {})
            
            # mustRunAfter: jobs that must run before this job
            # These increase this job's in-degree
            must_run_after = dependencies.get('mustRunAfter', [])
            for predecessor in must_run_after:
                if predecessor in job_map:
                    in_degree[job_name] += 1
                    out_edges[predecessor].append(job_name)
        
        # Kahn's algorithm for topological sort
        # Start with jobs that have no dependencies (in-degree = 0)
        queue = [job_name for job_name in in_degree if in_degree[job_name] == 0]
        queue.sort()  # Sort alphabetically for deterministic ordering
        
        sorted_job_names = []
        
        while queue:
            # Process job with no remaining dependencies
            current = queue.pop(0)
            sorted_job_names.append(current)
            
            # Remove edges from this job to its dependents
            for dependent in out_edges[current]:
                in_degree[dependent] -= 1
                
                # If dependent now has no dependencies, add to queue
                if in_degree[dependent] == 0:
                    queue.append(dependent)
                    queue.sort()  # Keep queue sorted for deterministic ordering
        
        # Check for circular dependencies
        # If we haven't processed all jobs, there's a cycle
        if len(sorted_job_names) < len(jobs):
            # Find jobs involved in the cycle
            cycle_jobs = [name for name in in_degree if in_degree[name] > 0]
            
            logger.warning(
                f"Circular dependency detected involving {len(cycle_jobs)} jobs: "
                f"{', '.join(sorted(cycle_jobs))}. "
                f"These jobs will be sorted by name and placed at the end."
            )
            
            # Add cycle jobs sorted by name to the end
            sorted_job_names.extend(sorted(cycle_jobs))
        
        # Build final sorted job list
        sorted_jobs = [job_map[name] for name in sorted_job_names]
        
        logger.debug(
            f"Dependency sorting completed: {len(sorted_jobs)} jobs sorted, "
            f"{len(sorted_job_names) - len(sorted_jobs) if len(sorted_job_names) > len(jobs) else 0} "
            f"jobs in circular dependencies"
        )
        
        return sorted_jobs



class ComplexitySortingStrategy(SortingStrategy):
    """
    Sort jobs by complexity (number of steps) in descending order.
    
    This strategy helps migration engineers identify the most complex jobs
    first, which typically require more effort to migrate. Jobs with more
    steps are considered more complex and appear first in the sorted list.
    
    Within jobs of the same complexity (same number of steps), jobs are
    sorted alphabetically by name for consistency.
    
    Sort order:
    1. Jobs with most steps first (descending)
    2. Within same step count, sorted by name (ascending)
    
    Example:
        >>> strategy = ComplexitySortingStrategy()
        >>> jobs = [
        ...     {'jobName': 'SIMPLE', 'steps': [1, 2]},
        ...     {'jobName': 'COMPLEX', 'steps': [1, 2, 3, 4, 5]},
        ...     {'jobName': 'MEDIUM', 'steps': [1, 2, 3]}
        ... ]
        >>> sorted_jobs = strategy.sort(jobs)
        >>> [(j['jobName'], len(j['steps'])) for j in sorted_jobs]
        [('COMPLEX', 5), ('MEDIUM', 3), ('SIMPLE', 2)]
    """
    
    def sort(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort jobs by number of steps (descending), then by name.
        
        Args:
            jobs: List of job dictionaries to sort
            
        Returns:
            New list of jobs sorted by complexity (step count descending)
            
        Note:
            Jobs without a steps field are treated as having 0 steps
            and placed at the end. The name is used as a tiebreaker
            for jobs with the same number of steps.
        """
        logger.debug(f"Sorting {len(jobs)} jobs by complexity")
        
        # Sort by number of steps (descending), then by name (ascending)
        sorted_jobs = sorted(
            jobs,
            key=lambda job: (
                -len(job.get('steps', [])),  # Negative for descending order
                job.get('jobName', '')  # Name as tiebreaker
            )
        )
        
        # Log statistics
        if sorted_jobs:
            max_steps = len(sorted_jobs[0].get('steps', []))
            min_steps = len(sorted_jobs[-1].get('steps', []))
            avg_steps = sum(len(job.get('steps', [])) for job in sorted_jobs) / len(sorted_jobs)
            
            logger.debug(
                f"Complexity sorting completed: "
                f"max={max_steps} steps, min={min_steps} steps, avg={avg_steps:.1f} steps"
            )
        else:
            logger.debug("Complexity sorting completed: no jobs to sort")
        
        return sorted_jobs
