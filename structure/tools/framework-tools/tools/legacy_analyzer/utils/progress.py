"""Progress indicator utilities for long-running operations."""

import sys
import time
from typing import Optional


class ProgressIndicator:
    """Simple progress indicator for CLI operations.
    
    Displays progress as a percentage with optional message.
    Supports both determinate (known total) and indeterminate progress.
    
    Example usage:
        progress = ProgressIndicator(total=100, message="Processing")
        for i in range(100):
            progress.update(i + 1)
            # do work
        progress.complete()
    """
    
    def __init__(
        self,
        total: Optional[int] = None,
        message: str = "Progress",
        show_percentage: bool = True,
        show_count: bool = True,
        show_rate: bool = False,
        width: int = 40
    ):
        """Initialize progress indicator.
        
        Args:
            total: Total number of items (None for indeterminate)
            message: Message to display
            show_percentage: Show percentage complete
            show_count: Show current/total count
            show_rate: Show items per second
            width: Width of progress bar in characters
        """
        self.total = total
        self.message = message
        self.show_percentage = show_percentage
        self.show_count = show_count
        self.show_rate = show_rate
        self.width = width
        
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_update_count = 0
        self.completed = False
        
        # Don't show progress if not a TTY (e.g., piped output)
        self.enabled = sys.stdout.isatty()
    
    def update(self, current: int, message: Optional[str] = None):
        """Update progress indicator.
        
        Args:
            current: Current progress value
            message: Optional message to display (overrides default)
        """
        if not self.enabled or self.completed:
            return
        
        self.current = current
        
        # Build progress string
        parts = []
        
        # Message
        display_message = message if message is not None else self.message
        if display_message:
            parts.append(display_message)
        
        # Progress bar (if total is known)
        if self.total is not None and self.total > 0:
            percentage = min(100, int(100 * current / self.total))
            filled = int(self.width * current / self.total)
            bar = '█' * filled + '░' * (self.width - filled)
            parts.append(f"[{bar}]")
            
            if self.show_percentage:
                parts.append(f"{percentage}%")
        
        # Count
        if self.show_count:
            if self.total is not None:
                parts.append(f"({current:,}/{self.total:,})")
            else:
                parts.append(f"({current:,})")
        
        # Rate
        if self.show_rate:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                rate = current / elapsed
                parts.append(f"{rate:.1f}/s")
        
        # Write progress (with carriage return to overwrite)
        progress_str = " ".join(parts)
        sys.stdout.write(f"\r{progress_str}")
        sys.stdout.flush()
    
    def complete(self, message: Optional[str] = None):
        """Mark progress as complete and move to next line.
        
        Args:
            message: Optional completion message
        """
        if not self.enabled or self.completed:
            return
        
        self.completed = True
        
        if message:
            sys.stdout.write(f"\r{message}\n")
        else:
            # Show final progress
            if self.total is not None:
                self.update(self.total)
            sys.stdout.write("\n")
        
        sys.stdout.flush()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if not self.completed:
            if exc_type is None:
                self.complete()
            else:
                # Error occurred, clear progress line
                if self.enabled:
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    sys.stdout.flush()


class SpinnerIndicator:
    """Indeterminate progress spinner for operations without known duration.
    
    Example usage:
        with SpinnerIndicator("Processing...") as spinner:
            # do work
            spinner.update("Still processing...")
    """
    
    SPINNER_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str = "Working"):
        """Initialize spinner indicator.
        
        Args:
            message: Message to display
        """
        self.message = message
        self.current_frame = 0
        self.start_time = time.time()
        self.completed = False
        
        # Don't show spinner if not a TTY
        self.enabled = sys.stdout.isatty()
    
    def update(self, message: Optional[str] = None):
        """Update spinner with optional new message.
        
        Args:
            message: Optional new message to display
        """
        if not self.enabled or self.completed:
            return
        
        if message is not None:
            self.message = message
        
        # Get current spinner character
        spinner_char = self.SPINNER_CHARS[self.current_frame % len(self.SPINNER_CHARS)]
        self.current_frame += 1
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time
        elapsed_str = f"{elapsed:.1f}s"
        
        # Write spinner
        sys.stdout.write(f"\r{spinner_char} {self.message} ({elapsed_str})")
        sys.stdout.flush()
    
    def complete(self, message: Optional[str] = None):
        """Mark spinner as complete and move to next line.
        
        Args:
            message: Optional completion message
        """
        if not self.enabled or self.completed:
            return
        
        self.completed = True
        
        if message:
            sys.stdout.write(f"\r✓ {message}\n")
        else:
            sys.stdout.write(f"\r✓ {self.message}\n")
        
        sys.stdout.flush()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if not self.completed:
            if exc_type is None:
                self.complete()
            else:
                # Error occurred, clear spinner line
                if self.enabled:
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    sys.stdout.flush()


def create_progress_callback(message: str = "Processing"):
    """Create a progress callback function for use with parsers.
    
    Args:
        message: Base message to display
        
    Returns:
        Callback function(current, total, message) that updates progress
    """
    progress = ProgressIndicator(message=message)
    
    def callback(current: int, total: int, msg: Optional[str] = None):
        """Progress callback function.
        
        Args:
            current: Current progress value
            total: Total items
            msg: Optional message override
        """
        if progress.total is None:
            progress.total = total
        
        progress.update(current, message=msg)
        
        # Complete when done
        if current >= total:
            progress.complete()
    
    return callback
