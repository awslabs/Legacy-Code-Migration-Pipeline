"""Base interface for inventory loaders."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseInventoryLoader(ABC):
    """Abstract base class for inventory loaders.
    
    This interface defines the contract for loading different types of
    mainframe inventory data into the analysis database.
    """
    
    def __init__(self, database: BaseDatabase):
        """
        Initialize inventory loader with database adapter.
        
        Args:
            database: Database adapter instance
        """
        self.database = database
        self.stats: Dict[str, int] = {}
    
    @abstractmethod
    def create_inventory_schema(self) -> None:
        """Create database tables for inventory data.
        
        This method should create all necessary tables, indexes, and
        constraints for storing inventory data.
        """
        pass
    
    @abstractmethod
    def load_inventory(self, csv_file: str, inventory_type: str) -> None:
        """
        Load inventory data from CSV file.
        
        Args:
            csv_file: Path to CSV file containing inventory data
            inventory_type: Type of inventory (jcl, programs, copybooks, datasets, cics)
        """
        pass
    
    @abstractmethod
    def validate_csv_format(self, csv_file: str, inventory_type: str) -> bool:
        """
        Validate CSV file format.
        
        Args:
            csv_file: Path to CSV file
            inventory_type: Type of inventory
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get loading statistics.
        
        Returns:
            Dictionary with counts of loaded items by type
        """
        return self.stats.copy()
    
    def print_stats(self) -> None:
        """Print loading statistics."""
        print("\n" + "=" * 80)
        print("INVENTORY LOADING STATISTICS")
        print("=" * 80 + "\n")
        
        for inventory_type, count in self.stats.items():
            print(f"  {inventory_type:30}: {count:6,} items")
        
        print()
