"""Data models for dependencies between artifacts."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Dependency:
    """Represents a dependency relationship between two artifacts."""
    
    source_artifact: str
    source_type: str  # PROGRAM, JCL, COPYBOOK, etc.
    target_artifact: str
    target_type: str  # PROGRAM, COPYBOOK, DATASET, etc.
    dependency_type: str  # COPY, CALL, CICS_LINK, EXEC_PGM, DATASET_REF, etc.
    
    # Language information for cross-language tracking
    source_language: Optional[str] = None  # COBOL, PLI, JCL, REXX, NATURAL, RPG, ASM
    target_language: Optional[str] = None  # COBOL, PLI, JCL, REXX, NATURAL, RPG, ASM
    
    # Source location information
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    
    # Additional context
    library_name: Optional[str] = None
    notes: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of dependency."""
        return f"{self.source_artifact} --[{self.dependency_type}]--> {self.target_artifact}"
    
    def __hash__(self) -> int:
        """Hash based on source, target, and type."""
        return hash((self.source_artifact, self.target_artifact, self.dependency_type))
    
    def __eq__(self, other) -> bool:
        """Equality based on source, target, and type."""
        if not isinstance(other, Dependency):
            return False
        return (
            self.source_artifact == other.source_artifact and
            self.target_artifact == other.target_artifact and
            self.dependency_type == other.dependency_type
        )


@dataclass
class CircularDependency:
    """Represents a circular dependency chain."""
    
    artifacts: list[str]  # List of artifact names in the cycle
    dependency_types: list[str]  # List of dependency types in the cycle
    
    def __str__(self) -> str:
        """String representation of circular dependency."""
        cycle_str = " -> ".join(
            f"{art}[{dep}]" 
            for art, dep in zip(self.artifacts, self.dependency_types)
        )
        return f"Circular: {cycle_str} -> {self.artifacts[0]}"
    
    def __len__(self) -> int:
        """Length of the cycle."""
        return len(self.artifacts)


# Dependency type constants
class DependencyType:
    """Constants for dependency types.
    
    These constants provide normalized dependency types that work across
    multiple programming languages. For example, CALL represents a program
    call regardless of whether it's from COBOL, PL/I, Natural, RPG, or REXX.
    """
    
    # Code dependencies (normalized across languages)
    COPY = "COPY"  # COBOL COPY, PL/I %INCLUDE, RPG /COPY, Natural INCLUDE
    INCLUDE = "INCLUDE"  # JCL INCLUDE, REXX /* INCLUDE */
    CALL = "CALL"  # Program call (COBOL CALL, PL/I CALL, Natural CALLNAT, RPG CALL, REXX CALL)
    FETCH = "FETCH"  # Natural FETCH (similar to CALL but different semantics)
    FETCH_RETURN = "FETCH_RETURN"  # Natural FETCH RETURN (call-and-return)
    CICS_LINK = "CICS_LINK"  # CICS LINK command (COBOL, PL/I)
    CICS_XCTL = "CICS_XCTL"  # CICS XCTL command (PL/I)
    CICS_START = "CICS_START"  # CICS START command
    EXEC_PGM = "EXEC_PGM"  # JCL EXEC PGM
    EXEC_PROC = "EXEC_PROC"  # JCL EXEC PROC
    
    # Data dependencies
    DATASET_REF = "DATASET_REF"  # Dataset reference
    FILE_REF = "FILE_REF"  # File reference (PL/I FILE, RPG F-spec, Natural VIEW OF)
    CICS_FILE = "CICS_FILE"  # CICS file reference (generic/legacy)
    CICS_READ = "CICS_READ"  # CICS READ FILE
    CICS_WRITE = "CICS_WRITE"  # CICS WRITE FILE
    CICS_REWRITE = "CICS_REWRITE"  # CICS REWRITE FILE
    CICS_DELETE = "CICS_DELETE"  # CICS DELETE FILE
    CICS_BROWSE = "CICS_BROWSE"  # CICS STARTBR/READNEXT/READPREV/ENDBR
    SQL_TABLE = "SQL_TABLE"  # SQL table reference
    SQL_INCLUDE = "SQL_INCLUDE"  # SQL INCLUDE statement
    
    # Integration dependencies (Natural-specific)
    PAGE_REF = "PAGE_REF"  # Natural PROCESS PAGE USING (UI page reference)
    WEB_SERVICE = "WEB_SERVICE"  # Natural REQUEST DOCUMENT (web service call)
    WORK_FILE = "WORK_FILE"  # Natural DEFINE/READ/WRITE WORK FILE (file I/O)
    
    # Transaction dependencies
    CICS_TRANSACTION = "CICS_TRANSACTION"  # CICS transaction reference
    
    # Language-specific mappings for normalization
    LANGUAGE_MAPPINGS = {
        # COBOL mappings
        'copybooks': COPY,
        'calls': CALL,
        'cics_links': CICS_LINK,
        'cics_read_files': CICS_READ,
        'cics_write_files': CICS_WRITE,
        'cics_rewrite_files': CICS_REWRITE,
        'cics_delete_files': CICS_DELETE,
        'cics_browse_files': CICS_BROWSE,
        'sql_includes': SQL_INCLUDE,
        
        # PL/I mappings
        'includes': COPY,  # PL/I %INCLUDE
        'cics_xctl': CICS_XCTL,
        'cics_link': CICS_LINK,
        'file_declarations': FILE_REF,
        'file_reads': FILE_REF,
        'file_writes': FILE_REF,
        'cics_reads': CICS_READ,
        'cics_writes': CICS_WRITE,
        'cics_rewrites': CICS_REWRITE,
        'cics_deletes': CICS_DELETE,
        
        # JCL mappings
        'programs': EXEC_PGM,
        'procs': EXEC_PROC,
        'datasets': DATASET_REF,
        
        # Natural mappings
        'callnat': CALL,
        'fetch': FETCH,
        'using': COPY,  # Global data area reference
        'view_of': FILE_REF,
        'reads': FILE_REF,
        'page_ref': PAGE_REF,
        'web_service': WEB_SERVICE,
        'work_file': WORK_FILE,
        'fetch_return': FETCH_RETURN,
        
        # RPG mappings
        'files': FILE_REF,
        'sql_tables': SQL_TABLE,
        
        # REXX mappings
        'address_links': CALL,
        'function_calls': CALL,
    }
    
    @classmethod
    def normalize(cls, parser_dep_type: str) -> str:
        """
        Normalize a parser-specific dependency type to a standard type.
        
        Args:
            parser_dep_type: Dependency type from parser (e.g., 'copybooks', 'callnat')
            
        Returns:
            Normalized dependency type (e.g., 'COPY', 'CALL')
        """
        return cls.LANGUAGE_MAPPINGS.get(parser_dep_type, parser_dep_type.upper())
    
    @classmethod
    def is_code_dependency(cls, dep_type: str) -> bool:
        """Check if dependency type is a code dependency."""
        return dep_type in {
            cls.COPY, cls.INCLUDE, cls.CALL, cls.FETCH, cls.FETCH_RETURN,
            cls.CICS_LINK, cls.CICS_XCTL, cls.CICS_START, cls.EXEC_PGM,
            cls.EXEC_PROC
        }
    
    @classmethod
    def is_data_dependency(cls, dep_type: str) -> bool:
        """Check if dependency type is a data dependency."""
        return dep_type in {
            cls.DATASET_REF, cls.FILE_REF, cls.CICS_FILE,
            cls.CICS_READ, cls.CICS_WRITE, cls.CICS_REWRITE,
            cls.CICS_DELETE, cls.CICS_BROWSE,
            cls.SQL_TABLE, cls.SQL_INCLUDE, cls.WORK_FILE
        }
