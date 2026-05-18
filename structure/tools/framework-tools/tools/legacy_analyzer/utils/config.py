"""Configuration management for Legacy Analyzer.

This module provides configuration loading, validation, and environment-specific
configuration support for the Legacy Analyzer system.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class AnalysisConfig:
    """Configuration for analysis operations."""
    max_flow_depth: int = 10
    enable_circular_detection: bool = True
    cache_parsed_results: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    parse_timeout: int = 30


@dataclass
class ComplexityConfig:
    """Configuration for complexity analysis."""
    thresholds: Dict[str, int] = field(default_factory=lambda: {
        'low': 10,
        'medium': 25,
        'high': 50
    })
    weights: Dict[str, float] = field(default_factory=lambda: {
        'loc': 0.3,
        'cyclomatic': 0.4,
        'dependencies': 0.3
    })
    god_program_threshold: int = 100


@dataclass
class PackageConfig:
    """Configuration for migration packages."""
    max_artifacts: int = 100
    max_loc: int = 50000
    max_complexity: float = 1000.0
    allow_external_deps: bool = False
    optimization_strategy: str = "minimize_deps"


@dataclass
class ParserConfig:
    """Configuration for a specific parser."""
    extensions: List[str] = field(default_factory=list)
    encoding: str = "utf-8"
    fallback_encoding: str = "utf-8"
    case_sensitive: bool = False


@dataclass
class CacheConfig:
    """Configuration for caching."""
    enabled: bool = True
    cache_dir: str = ".cache/legacy_analyzer"
    expiration: int = 86400
    max_size_mb: int = 1000
    invalidation_strategy: str = "mtime"


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    type: str = "sqlite"
    sqlite_path: str = "legacy_analyzer.db"
    wal_mode: bool = True
    synchronous: str = "NORMAL"
    max_connections: int = 10
    timeout: int = 30


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    file: str = ""
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    verbose_modules: List[str] = field(default_factory=list)
    rotation_enabled: bool = True
    max_size_mb: int = 10
    backup_count: int = 5


class ConfigManager:
    """Manages configuration loading, validation, and access.
    
    The ConfigManager loads configuration from YAML files and provides
    type-safe access to configuration values. It supports environment-specific
    configurations and validates configuration on load.
    
    Example:
        >>> config = ConfigManager()
        >>> config.load_config('config/legacy_analyzer.yaml')
        >>> max_depth = config.get_analysis_config().max_flow_depth
        >>> print(f"Max flow depth: {max_depth}")
    """
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default.
            environment: Environment name (dev, test, prod). If None, uses default config.
        """
        self._config: Dict[str, Any] = {}
        self._environment = environment
        self._config_path = config_path
        
        if config_path:
            self.load_config(config_path, environment)
    
    def load_config(self, config_path: str, environment: Optional[str] = None) -> None:
        """Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file.
            environment: Environment name to apply environment-specific overrides.
            
        Raises:
            ConfigValidationError: If configuration is invalid.
            FileNotFoundError: If configuration file doesn't exist.
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Failed to parse YAML configuration: {e}")
        
        if self._config is None:
            self._config = {}
        
        # Apply environment-specific overrides
        if environment:
            self._apply_environment_overrides(environment)
        
        # Validate configuration
        if self._config.get('validation', {}).get('validate_config', True):
            self._validate_config()
        
        self._config_path = config_path
        self._environment = environment
    
    def _apply_environment_overrides(self, environment: str) -> None:
        """Apply environment-specific configuration overrides.
        
        Args:
            environment: Environment name (dev, test, prod).
        """
        environments = self._config.get('environments', {})
        env_config = environments.get(environment, {})
        
        if env_config:
            self._deep_merge(self._config, env_config)
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Recursively merge override dict into base dict.
        
        Args:
            base: Base dictionary to merge into.
            override: Override dictionary with new values.
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration.
        
        Raises:
            ConfigValidationError: If configuration is invalid.
        """
        errors = []
        
        # Validate complexity weights sum to 1.0
        complexity = self._config.get('complexity', {})
        weights = complexity.get('weights', {})
        if weights:
            weight_sum = sum(weights.values())
            if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point errors
                errors.append(f"Complexity weights must sum to 1.0, got {weight_sum}")
        
        # Validate thresholds are in ascending order
        thresholds = complexity.get('thresholds', {})
        if thresholds:
            low = thresholds.get('low', 0)
            medium = thresholds.get('medium', 0)
            high = thresholds.get('high', 0)
            if not (low < medium < high):
                errors.append(f"Complexity thresholds must be in ascending order: low < medium < high")
        
        # Validate analysis max_workers
        analysis = self._config.get('analysis', {})
        max_workers = analysis.get('max_workers', 1)
        if max_workers < 0:
            errors.append(f"analysis.max_workers must be >= 0, got {max_workers}")
        
        # Validate package constraints
        packages = self._config.get('packages', {})
        if packages.get('max_artifacts', 1) <= 0:
            errors.append("packages.max_artifacts must be > 0")
        if packages.get('max_loc', 1) <= 0:
            errors.append("packages.max_loc must be > 0")
        if packages.get('max_complexity', 1) <= 0:
            errors.append("packages.max_complexity must be > 0")
        
        # Validate optimization strategy
        valid_strategies = ['minimize_deps', 'balance_size', 'minimize_complexity']
        strategy = packages.get('optimization_strategy', 'minimize_deps')
        if strategy not in valid_strategies:
            errors.append(f"Invalid optimization_strategy: {strategy}. Must be one of {valid_strategies}")
        
        # Validate logging level
        logging_config = self._config.get('logging', {})
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        level = logging_config.get('level', 'INFO')
        if level not in valid_levels:
            errors.append(f"Invalid logging level: {level}. Must be one of {valid_levels}")
        
        # Validate cache settings
        cache = self._config.get('cache', {})
        if cache.get('max_size_mb', 1) < 0:
            errors.append("cache.max_size_mb must be >= 0")
        if cache.get('expiration', 0) < 0:
            errors.append("cache.expiration must be >= 0")
        
        valid_invalidation = ['mtime', 'hash', 'manual']
        invalidation = cache.get('invalidation_strategy', 'mtime')
        if invalidation not in valid_invalidation:
            errors.append(f"Invalid cache invalidation_strategy: {invalidation}. Must be one of {valid_invalidation}")
        
        if errors:
            raise ConfigValidationError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    def get_analysis_config(self) -> AnalysisConfig:
        """Get analysis configuration.
        
        Returns:
            AnalysisConfig object with analysis settings.
        """
        analysis = self._config.get('analysis', {})
        return AnalysisConfig(
            max_flow_depth=analysis.get('max_flow_depth', 10),
            enable_circular_detection=analysis.get('enable_circular_detection', True),
            cache_parsed_results=analysis.get('cache_parsed_results', True),
            parallel_processing=analysis.get('parallel_processing', True),
            max_workers=analysis.get('max_workers', 4),
            parse_timeout=analysis.get('parse_timeout', 30)
        )
    
    def get_complexity_config(self) -> ComplexityConfig:
        """Get complexity analysis configuration.
        
        Returns:
            ComplexityConfig object with complexity settings.
        """
        complexity = self._config.get('complexity', {})
        return ComplexityConfig(
            thresholds=complexity.get('thresholds', {'low': 10, 'medium': 25, 'high': 50}),
            weights=complexity.get('weights', {'loc': 0.3, 'cyclomatic': 0.4, 'dependencies': 0.3}),
            god_program_threshold=complexity.get('god_program_threshold', 100)
        )
    
    def get_package_config(self) -> PackageConfig:
        """Get migration package configuration.
        
        Returns:
            PackageConfig object with package settings.
        """
        packages = self._config.get('packages', {})
        return PackageConfig(
            max_artifacts=packages.get('max_artifacts', 100),
            max_loc=packages.get('max_loc', 50000),
            max_complexity=packages.get('max_complexity', 1000.0),
            allow_external_deps=packages.get('allow_external_deps', False),
            optimization_strategy=packages.get('optimization_strategy', 'minimize_deps')
        )
    
    def get_parser_config(self, language: str) -> ParserConfig:
        """Get parser configuration for a specific language.
        
        Args:
            language: Language name (cobol, jcl, pli, rpg, natural, rexx).
            
        Returns:
            ParserConfig object with parser settings.
        """
        parsers = self._config.get('parsers', {})
        parser = parsers.get(language.lower(), {})
        
        return ParserConfig(
            extensions=parser.get('extensions', []),
            encoding=parser.get('encoding', 'utf-8'),
            fallback_encoding=parser.get('fallback_encoding', 'utf-8'),
            case_sensitive=parser.get('case_sensitive', False)
        )
    
    def get_cache_config(self) -> CacheConfig:
        """Get caching configuration.
        
        Returns:
            CacheConfig object with cache settings.
        """
        cache = self._config.get('cache', {})
        return CacheConfig(
            enabled=cache.get('enabled', True),
            cache_dir=cache.get('cache_dir', '.cache/legacy_analyzer'),
            expiration=cache.get('expiration', 86400),
            max_size_mb=cache.get('max_size_mb', 1000),
            invalidation_strategy=cache.get('invalidation_strategy', 'mtime')
        )
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration.
        
        Returns:
            DatabaseConfig object with database settings.
        """
        database = self._config.get('database', {})
        sqlite = database.get('sqlite', {})
        pool = database.get('pool', {})
        
        return DatabaseConfig(
            type=database.get('type', 'sqlite'),
            sqlite_path=sqlite.get('path', 'legacy_analyzer.db'),
            wal_mode=sqlite.get('wal_mode', True),
            synchronous=sqlite.get('synchronous', 'NORMAL'),
            max_connections=pool.get('max_connections', 10),
            timeout=pool.get('timeout', 30)
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration.
        
        Returns:
            LoggingConfig object with logging settings.
        """
        logging = self._config.get('logging', {})
        rotation = logging.get('rotation', {})
        
        return LoggingConfig(
            level=logging.get('level', 'INFO'),
            file=logging.get('file', ''),
            format=logging.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            verbose_modules=logging.get('verbose_modules', []),
            rotation_enabled=rotation.get('enabled', True),
            max_size_mb=rotation.get('max_size_mb', 10),
            backup_count=rotation.get('backup_count', 5)
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key path.
        
        Supports nested keys using dot notation (e.g., 'analysis.max_flow_depth').
        
        Args:
            key: Configuration key or key path.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key path.
        
        Supports nested keys using dot notation (e.g., 'analysis.max_flow_depth').
        
        Args:
            key: Configuration key or key path.
            value: Value to set.
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, output_path: Optional[str] = None) -> None:
        """Save current configuration to a YAML file.
        
        Args:
            output_path: Path to save configuration. If None, uses original path.
            
        Raises:
            ValueError: If no output path specified and no original path available.
        """
        path = output_path or self._config_path
        
        if not path:
            raise ValueError("No output path specified and no original config path available")
        
        output_file = Path(path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def get_all(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary.
        
        Returns:
            Complete configuration as a dictionary.
        """
        return self._config.copy()
    
    @staticmethod
    def get_default_config_path() -> str:
        """Get the default configuration file path.
        
        Returns:
            Path to the default configuration file.
        """
        # Look for config file in common locations
        possible_paths = [
            'config/legacy_analyzer.yaml',
            'legacy_analyzer.yaml',
            os.path.expanduser('~/.legacy_analyzer.yaml'),
            '/etc/legacy_analyzer/config.yaml'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return first path as default even if it doesn't exist
        return possible_paths[0]
