"""Data models for complexity metrics."""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ComplexityTier(Enum):
    """Complexity tier classification."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    
    @classmethod
    def from_score(cls, score: float, 
                   low_threshold: float = 10.0,
                   medium_threshold: float = 25.0,
                   high_threshold: float = 50.0) -> 'ComplexityTier':
        """
        Determine tier from composite score.
        
        Args:
            score: Composite complexity score
            low_threshold: Threshold for LOW/MEDIUM boundary
            medium_threshold: Threshold for MEDIUM/HIGH boundary
            high_threshold: Threshold for HIGH/VERY_HIGH boundary
            
        Returns:
            ComplexityTier enum value
        """
        if score < low_threshold:
            return cls.LOW
        elif score < medium_threshold:
            return cls.MEDIUM
        elif score < high_threshold:
            return cls.HIGH
        else:
            return cls.VERY_HIGH


@dataclass
class ComplexityMetrics:
    """Complexity metrics for a program or artifact."""
    
    program_name: str
    language: str  # COBOL, PLI, JCL, etc.
    
    # Basic metrics
    lines_of_code: int
    cyclomatic_complexity: int
    
    # Dependency metrics
    dependency_count_in: int  # How many artifacts depend on this
    dependency_count_out: int  # How many artifacts this depends on
    
    # Composite score
    composite_score: float
    complexity_tier: str  # LOW, MEDIUM, HIGH, VERY_HIGH
    
    # Additional metrics
    comment_lines: Optional[int] = None
    blank_lines: Optional[int] = None
    total_lines: Optional[int] = None
    
    # Language-specific factors
    language_factor: float = 1.0
    
    # Flags
    is_god_program: bool = False  # Excessive complexity or dependencies
    
    def __post_init__(self):
        """Calculate derived metrics."""
        if self.total_lines is None and self.comment_lines and self.blank_lines:
            self.total_lines = self.lines_of_code + self.comment_lines + self.blank_lines
    
    @classmethod
    def calculate_composite_score(cls,
                                  loc: int,
                                  cyclomatic: int,
                                  deps_in: int,
                                  deps_out: int,
                                  loc_weight: float = 0.3,
                                  cyclomatic_weight: float = 0.4,
                                  deps_weight: float = 0.3,
                                  language_factor: float = 1.0) -> float:
        """
        Calculate composite complexity score.
        
        Formula: (LOC * loc_weight + cyclomatic * cyclomatic_weight + 
                  (deps_in + deps_out) * deps_weight) * language_factor
        
        Args:
            loc: Lines of code
            cyclomatic: Cyclomatic complexity
            deps_in: Incoming dependencies
            deps_out: Outgoing dependencies
            loc_weight: Weight for LOC (default 0.3)
            cyclomatic_weight: Weight for cyclomatic complexity (default 0.4)
            deps_weight: Weight for dependencies (default 0.3)
            language_factor: Language-specific multiplier (default 1.0)
            
        Returns:
            Composite complexity score
        """
        # Normalize LOC (divide by 100 to bring to similar scale)
        normalized_loc = loc / 100.0
        
        # Total dependencies
        total_deps = deps_in + deps_out
        
        # Calculate weighted score
        score = (
            normalized_loc * loc_weight +
            cyclomatic * cyclomatic_weight +
            total_deps * deps_weight
        ) * language_factor
        
        return score
    
    @classmethod
    def determine_tier(cls, score: float) -> str:
        """Determine complexity tier from score."""
        tier = ComplexityTier.from_score(score)
        return tier.value
    
    @classmethod
    def is_god_program_check(cls,
                            loc: int,
                            cyclomatic: int,
                            deps_total: int,
                            loc_threshold: int = 5000,
                            cyclomatic_threshold: int = 100,
                            deps_threshold: int = 50) -> bool:
        """
        Check if program qualifies as a "god program".
        
        A god program has excessive complexity or dependencies that make
        it difficult to maintain and migrate.
        
        Args:
            loc: Lines of code
            cyclomatic: Cyclomatic complexity
            deps_total: Total dependencies (in + out)
            loc_threshold: LOC threshold (default 5000)
            cyclomatic_threshold: Cyclomatic threshold (default 100)
            deps_threshold: Dependencies threshold (default 50)
            
        Returns:
            True if program is a god program
        """
        return (
            loc > loc_threshold or
            cyclomatic > cyclomatic_threshold or
            deps_total > deps_threshold
        )
    
    def get_maintainability_index(self) -> float:
        """
        Calculate maintainability index (0-100, higher is better).
        
        Based on simplified version of Microsoft's maintainability index.
        
        Returns:
            Maintainability index (0-100)
        """
        # Simplified formula
        # MI = max(0, (171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)) * 100 / 171)
        # Where V = Halstead Volume (approximated), G = cyclomatic complexity
        
        import math
        
        # Approximate Halstead volume as LOC * 2
        halstead_volume = self.lines_of_code * 2
        
        if halstead_volume <= 0 or self.lines_of_code <= 0:
            return 0.0
        
        mi = (
            171 - 
            5.2 * math.log(halstead_volume) - 
            0.23 * self.cyclomatic_complexity - 
            16.2 * math.log(self.lines_of_code)
        ) * 100 / 171
        
        return max(0.0, min(100.0, mi))
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self.program_name} ({self.language}): "
            f"LOC={self.lines_of_code}, "
            f"Cyclomatic={self.cyclomatic_complexity}, "
            f"Deps={self.dependency_count_in + self.dependency_count_out}, "
            f"Score={self.composite_score:.1f}, "
            f"Tier={self.complexity_tier}"
        )


@dataclass
class ComplexityThresholds:
    """Thresholds for complexity classification."""
    
    # Tier thresholds
    low_threshold: float = 10.0
    medium_threshold: float = 25.0
    high_threshold: float = 50.0
    
    # God program thresholds
    god_loc_threshold: int = 5000
    god_cyclomatic_threshold: int = 100
    god_deps_threshold: int = 50
    
    # Weights for composite score
    loc_weight: float = 0.3
    cyclomatic_weight: float = 0.4
    deps_weight: float = 0.3
    
    # Language factors
    language_factors: dict = None
    
    def __post_init__(self):
        """Initialize default language factors."""
        if self.language_factors is None:
            self.language_factors = {
                'COBOL': 1.0,
                'PLI': 1.0,
                'JCL': 0.8,  # JCL is generally simpler
                'REXX': 0.9,
                'ASSEMBLER': 1.5,  # Assembler is more complex
                'RPG': 1.1,
                'NATURAL': 0.9
            }
    
    def get_language_factor(self, language: str) -> float:
        """Get language factor for a language."""
        return self.language_factors.get(language.upper(), 1.0)
