"""Parallel processing utilities for Legacy Analyzer.

This module provides parallel processing support for file parsing and analysis
operations to improve performance on large codebases.
"""

import os
import multiprocessing as mp
from typing import Any, Callable, Iterable, List, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class ProcessingResult:
    """Result of a parallel processing operation."""
    item: Any
    result: Any
    success: bool
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class ProgressInfo:
    """Progress information for parallel processing."""
    total: int
    completed: int
    successful: int
    failed: int
    elapsed_time: float
    estimated_remaining: float
    
    @property
    def percent_complete(self) -> float:
        """Calculate percentage complete."""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100
    
    @property
    def items_per_second(self) -> float:
        """Calculate processing rate."""
        if self.elapsed_time == 0:
            return 0.0
        return self.completed / self.elapsed_time


class ProgressTracker:
    """Tracks progress of parallel processing operations.
    
    Example:
        >>> tracker = ProgressTracker(total=100)
        >>> tracker.update(success=True)
        >>> print(tracker.get_progress())
    """
    
    def __init__(self, total: int, show_progress: bool = True, update_interval: float = 1.0):
        """Initialize progress tracker.
        
        Args:
            total: Total number of items to process.
            show_progress: Whether to print progress updates.
            update_interval: Minimum seconds between progress updates.
        """
        self.total = total
        self.completed = 0
        self.successful = 0
        self.failed = 0
        self.show_progress = show_progress
        self.update_interval = update_interval
        self.start_time = time.time()
        self.last_update_time = self.start_time
    
    def update(self, success: bool = True) -> None:
        """Update progress with a completed item.
        
        Args:
            success: Whether the item was processed successfully.
        """
        self.completed += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1
        
        # Print progress if enabled and enough time has passed
        if self.show_progress:
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                self._print_progress()
                self.last_update_time = current_time
    
    def _print_progress(self) -> None:
        """Print current progress to console."""
        progress = self.get_progress()
        print(f"\rProgress: {progress.completed}/{progress.total} "
              f"({progress.percent_complete:.1f}%) - "
              f"{progress.successful} successful, {progress.failed} failed - "
              f"{progress.items_per_second:.1f} items/sec - "
              f"ETA: {progress.estimated_remaining:.1f}s", end='', flush=True)
    
    def finish(self) -> None:
        """Mark processing as finished and print final progress."""
        if self.show_progress:
            self._print_progress()
            print()  # New line after progress
    
    def get_progress(self) -> ProgressInfo:
        """Get current progress information.
        
        Returns:
            ProgressInfo object with current progress.
        """
        elapsed = time.time() - self.start_time
        
        # Estimate remaining time
        if self.completed > 0:
            rate = self.completed / elapsed
            remaining_items = self.total - self.completed
            estimated_remaining = remaining_items / rate if rate > 0 else 0
        else:
            estimated_remaining = 0
        
        return ProgressInfo(
            total=self.total,
            completed=self.completed,
            successful=self.successful,
            failed=self.failed,
            elapsed_time=elapsed,
            estimated_remaining=estimated_remaining
        )


class ParallelProcessor:
    """Manages parallel processing of items using multiprocessing.
    
    The ParallelProcessor provides a simple interface for processing items
    in parallel with progress tracking and error handling.
    
    Example:
        >>> processor = ParallelProcessor(max_workers=4)
        >>> results = processor.process(parse_file, file_list)
        >>> successful = [r for r in results if r.success]
    """
    
    def __init__(self, max_workers: Optional[int] = None, show_progress: bool = True,
                 use_threads: bool = False):
        """Initialize parallel processor.
        
        Args:
            max_workers: Maximum number of worker processes (None = CPU count).
            show_progress: Whether to show progress indicators.
            use_threads: Use threads instead of processes (for I/O-bound tasks).
        """
        if max_workers is None or max_workers == 0:
            max_workers = mp.cpu_count()
        
        self.max_workers = max_workers
        self.show_progress = show_progress
        self.use_threads = use_threads
    
    def process(self, func: Callable, items: Iterable[Any],
                *args, **kwargs) -> List[ProcessingResult]:
        """Process items in parallel using the given function.
        
        Args:
            func: Function to apply to each item. Should accept item as first argument.
            items: Iterable of items to process.
            *args: Additional positional arguments to pass to func.
            **kwargs: Additional keyword arguments to pass to func.
            
        Returns:
            List of ProcessingResult objects.
        """
        items_list = list(items)
        total = len(items_list)
        
        if total == 0:
            return []
        
        tracker = ProgressTracker(total, self.show_progress)
        results = []
        
        # Choose executor based on use_threads flag
        executor_class = ThreadPoolExecutor if self.use_threads else ProcessPoolExecutor
        
        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(self._process_item, func, item, args, kwargs): item
                for item in items_list
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    tracker.update(success=result.success)
                except Exception as e:
                    # Handle unexpected errors
                    error_result = ProcessingResult(
                        item=item,
                        result=None,
                        success=False,
                        error=f"Unexpected error: {str(e)}"
                    )
                    results.append(error_result)
                    tracker.update(success=False)
        
        tracker.finish()
        return results
    
    @staticmethod
    def _process_item(func: Callable, item: Any, args: tuple, kwargs: dict) -> ProcessingResult:
        """Process a single item and return result.
        
        Args:
            func: Function to apply.
            item: Item to process.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.
            
        Returns:
            ProcessingResult object.
        """
        start_time = time.time()
        
        try:
            result = func(item, *args, **kwargs)
            duration = time.time() - start_time
            
            return ProcessingResult(
                item=item,
                result=result,
                success=True,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            
            return ProcessingResult(
                item=item,
                result=None,
                success=False,
                error=str(e),
                duration=duration
            )
    
    def process_with_callback(self, func: Callable, items: Iterable[Any],
                             callback: Optional[Callable[[ProcessingResult], None]] = None,
                             *args, **kwargs) -> List[ProcessingResult]:
        """Process items in parallel with a callback for each result.
        
        Args:
            func: Function to apply to each item.
            items: Iterable of items to process.
            callback: Optional callback function called with each result.
            *args: Additional positional arguments to pass to func.
            **kwargs: Additional keyword arguments to pass to func.
            
        Returns:
            List of ProcessingResult objects.
        """
        items_list = list(items)
        total = len(items_list)
        
        if total == 0:
            return []
        
        tracker = ProgressTracker(total, self.show_progress)
        results = []
        
        executor_class = ThreadPoolExecutor if self.use_threads else ProcessPoolExecutor
        
        with executor_class(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(self._process_item, func, item, args, kwargs): item
                for item in items_list
            }
            
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    tracker.update(success=result.success)
                    
                    # Call callback if provided
                    if callback:
                        callback(result)
                        
                except Exception as e:
                    error_result = ProcessingResult(
                        item=item,
                        result=None,
                        success=False,
                        error=f"Unexpected error: {str(e)}"
                    )
                    results.append(error_result)
                    tracker.update(success=False)
                    
                    if callback:
                        callback(error_result)
        
        tracker.finish()
        return results


class BatchProcessor:
    """Processes items in batches for better performance.
    
    Useful when processing many small items where the overhead of
    multiprocessing would be too high.
    """
    
    def __init__(self, batch_size: int = 100, max_workers: Optional[int] = None,
                 show_progress: bool = True):
        """Initialize batch processor.
        
        Args:
            batch_size: Number of items per batch.
            max_workers: Maximum number of worker processes.
            show_progress: Whether to show progress indicators.
        """
        self.batch_size = batch_size
        self.processor = ParallelProcessor(max_workers, show_progress)
    
    def process(self, func: Callable, items: Iterable[Any],
                *args, **kwargs) -> List[ProcessingResult]:
        """Process items in batches.
        
        Args:
            func: Function to apply to each item.
            items: Iterable of items to process.
            *args: Additional positional arguments to pass to func.
            **kwargs: Additional keyword arguments to pass to func.
            
        Returns:
            List of ProcessingResult objects.
        """
        items_list = list(items)
        
        # Create batches
        batches = [
            items_list[i:i + self.batch_size]
            for i in range(0, len(items_list), self.batch_size)
        ]
        
        # Process batches in parallel
        batch_results = self.processor.process(
            self._process_batch,
            batches,
            func, args, kwargs
        )
        
        # Flatten results
        all_results = []
        for batch_result in batch_results:
            if batch_result.success and batch_result.result:
                all_results.extend(batch_result.result)
        
        return all_results
    
    @staticmethod
    def _process_batch(batch: List[Any], func: Callable, args: tuple,
                      kwargs: dict) -> List[ProcessingResult]:
        """Process a batch of items sequentially.
        
        Args:
            batch: List of items to process.
            func: Function to apply.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.
            
        Returns:
            List of ProcessingResult objects.
        """
        results = []
        for item in batch:
            start_time = time.time()
            try:
                result = func(item, *args, **kwargs)
                duration = time.time() - start_time
                results.append(ProcessingResult(
                    item=item,
                    result=result,
                    success=True,
                    duration=duration
                ))
            except Exception as e:
                duration = time.time() - start_time
                results.append(ProcessingResult(
                    item=item,
                    result=None,
                    success=False,
                    error=str(e),
                    duration=duration
                ))
        return results


def parallel_map(func: Callable, items: Iterable[Any], max_workers: Optional[int] = None,
                show_progress: bool = True) -> List[Any]:
    """Simple parallel map function.
    
    Args:
        func: Function to apply to each item.
        items: Iterable of items to process.
        max_workers: Maximum number of worker processes.
        show_progress: Whether to show progress indicators.
        
    Returns:
        List of results (only successful results).
    """
    processor = ParallelProcessor(max_workers, show_progress)
    results = processor.process(func, items)
    return [r.result for r in results if r.success]


def parallel_filter(func: Callable, items: Iterable[Any], max_workers: Optional[int] = None,
                   show_progress: bool = True) -> List[Any]:
    """Parallel filter function.
    
    Args:
        func: Predicate function that returns True/False.
        items: Iterable of items to filter.
        max_workers: Maximum number of worker processes.
        show_progress: Whether to show progress indicators.
        
    Returns:
        List of items where func returned True.
    """
    processor = ParallelProcessor(max_workers, show_progress)
    results = processor.process(func, items)
    return [r.item for r in results if r.success and r.result]


def get_optimal_worker_count(task_type: str = 'cpu') -> int:
    """Get optimal number of workers for a task type.
    
    Args:
        task_type: Type of task ('cpu' or 'io').
        
    Returns:
        Recommended number of workers.
    """
    cpu_count = mp.cpu_count()
    
    if task_type == 'cpu':
        # For CPU-bound tasks, use CPU count
        return cpu_count
    elif task_type == 'io':
        # For I/O-bound tasks, use more workers
        return cpu_count * 2
    else:
        return cpu_count
