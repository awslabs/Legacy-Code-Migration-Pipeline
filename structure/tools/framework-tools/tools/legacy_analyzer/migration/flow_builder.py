"""
Migration Flow Builder

This module provides functionality for building migration-focused flow data
from dependency analysis. It generates flow IDs, identifies scope, interfaces,
and integrates complexity metrics.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Set, Tuple
import sqlite3
from datetime import datetime

from .exceptions import FlowValidationError, MissingDataError

# Configure logging
logger = logging.getLogger(__name__)

# Artifact types that represent executable programs across all supported languages.
# COBOL/PL/I/ASM use 'PROGRAM', Natural uses 'MAIN', 'SUBPROGRAM', 'FUNCTION'.
PROGRAM_LIKE_TYPES = ('PROGRAM', 'MAIN', 'SUBPROGRAM', 'FUNCTION')


def generate_flow_id(program_name: str) -> str:
    """
    Generate unique flow ID from entry point program name.
    
    Flow IDs are based on PROGRAM NAME only, not invocation type.
    This ensures one flow per entry point program, regardless of how many
    ways it can be invoked (JCL, CICS, Screen, etc.).
    
    Format: FLOW_{PROGRAM_NAME}
    
    Examples:
        - PAYROLL1 (invoked by JCL + CICS) → FLOW_PAYROLL1
        - BILLING (invoked by JCL only) → FLOW_BILLING
        - ACCTPROG (invoked by CICS + Screen) → FLOW_ACCTPROG
        - PAY-ROLL#01 (special chars) → FLOW_PAY_ROLL_01
    
    Args:
        program_name: The entry point program name
        
    Returns:
        Unique flow ID in format FLOW_{SANITIZED_PROGRAM_NAME}
        
    Notes:
        - Flow IDs are deterministic (same program = same flow ID)
        - Special characters are replaced with underscores
        - Flow IDs are URL-safe (no spaces or special chars except underscore)
    """
    if not program_name:
        raise ValueError("program_name cannot be empty")
    
    # Convert to uppercase for consistency
    name = program_name.upper()
    
    # Sanitize: replace special characters with underscore
    # Keep only alphanumeric characters and underscores
    sanitized = re.sub(r'[^A-Z0-9_]', '_', name)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Collapse multiple consecutive underscores into one
    sanitized = re.sub(r'_+', '_', sanitized)
    
    if not sanitized:
        raise ValueError(f"program_name '{program_name}' resulted in empty flow ID after sanitization")
    
    return f"FLOW_{sanitized}"


class MigrationFlowBuilder:
    """
    Builds migration-focused flow data from dependency analysis.
    
    This class orchestrates the process of:
    1. Identifying entry points
    2. Generating flow IDs
    3. Identifying scope (programs, copybooks, datasets)
    4. Identifying interfaces (inbound/outbound)
    5. Extracting data operations
    6. Calculating complexity metrics
    7. Identifying flow dependencies
    8. Writing data to database
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize the MigrationFlowBuilder.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        
        # Import dependencies here to avoid circular imports
        from ..analysis.flow_analyzer import FlowAnalyzer
        from ..models.dependency import Dependency
        from .entry_point_type_detector import EntryPointTypeDetector
        from .data_operation_inferencer import DataOperationInferencer
        from .external_config import ExternalConfigLoader
        
        # Load dependencies from database
        self.dependencies = self._load_dependencies()
        
        # Initialize components
        self.flow_analyzer = FlowAnalyzer(self.dependencies, db_connection)
        self.entry_point_detector = EntryPointTypeDetector(db_connection)
        self.data_operation_inferencer = DataOperationInferencer(db_connection)
        self.external_config_loader = ExternalConfigLoader(db_connection)
        
        # Load external configuration
        self.external_programs = self.external_config_loader.get_external_programs()
        self.external_callers = self.external_config_loader.get_external_callers()
        
        # Initialize caches for database queries
        self._inbound_interfaces_cache = None
        self._outbound_interfaces_cache = None
        self._codebase_membership_cache = {}
    
    def _load_dependencies(self) -> List:
        """
        Load dependencies from database.
        
        Returns:
            List of Dependency objects
        """
        from ..models.dependency import Dependency, DependencyType
        
        cursor = self.db.cursor()
        dependencies = []
        
        try:
            cursor.execute("""
                SELECT 
                    source_artifact_name,
                    source_artifact_type,
                    target_artifact_name,
                    target_artifact_type,
                    dependency_type,
                    source_file_path,
                    line_number
                FROM artifact_dependencies
            """)
            
            for row in cursor.fetchall():
                source_name, source_type, target_name, target_type, dep_type, file_path, line_num = row
                
                # Convert string dependency type to enum if possible
                try:
                    # Try to get the enum value
                    if hasattr(DependencyType, dep_type):
                        dep_type_enum = getattr(DependencyType, dep_type)
                    else:
                        # Use the string value directly
                        dep_type_enum = dep_type
                except (KeyError, AttributeError):
                    # If not a valid enum, use the string value
                    dep_type_enum = dep_type
                
                dep = Dependency(
                    source_artifact=source_name,
                    source_type=source_type,
                    target_artifact=target_name,
                    target_type=target_type,
                    dependency_type=dep_type_enum,
                    source_file=file_path,
                    line_number=line_num
                )
                dependencies.append(dep)
        
        except Exception as e:
            print(f"Warning: Error loading dependencies: {e}")
        
        return dependencies
    
    def _query_inbound_interfaces(self) -> Dict[str, List[Dict]]:
        """
        Query inbound_interfaces table for configured external callers.
        
        Returns:
            Dict mapping source_name -> list of target dictionaries
            Format: {
                'EXTERNAL_SYSTEM_A': [
                    {'target': 'PROGRAM1', 'type': 'PROGRAM_CALL', 'metadata': {...}},
                    ...
                ]
            }
            
        Notes:
            - Replaces reading from YAML configuration
            - Queries database for persistent storage
            - Caches results per flow builder instance
        """
        # Return cached result if available (performance optimization)
        if self._inbound_interfaces_cache is not None:
            return self._inbound_interfaces_cache
        
        inbound_interfaces = {}
        cursor = self.db.cursor()
        
        try:
            # Check if inbound_interfaces table exists
            # This handles cases where schema hasn't been created yet
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='inbound_interfaces'
            """)
            
            if not cursor.fetchone():
                # Table doesn't exist, return empty dict
                # This is not an error - just means no external interfaces configured
                logger.debug("inbound_interfaces table does not exist, returning empty dict")
                self._inbound_interfaces_cache = {}
                return self._inbound_interfaces_cache
            
            # Query all configured inbound interfaces
            # Only get manually configured interfaces (is_configured = 1)
            # Auto-detected interfaces would have is_configured = 0
            cursor.execute("""
                SELECT source_name, target_program, dependency_type, metadata
                FROM inbound_interfaces
                WHERE is_configured = 1
            """)
            
            for row in cursor.fetchall():
                source_name, target_program, dependency_type, metadata_json = row
                
                # Parse metadata JSON blob
                # Metadata contains additional info like system name, description, etc.
                metadata = {}
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse metadata for {source_name} -> {target_program}")
                
                # Create target dictionary with all interface details
                target_dict = {
                    'target': target_program,
                    'type': dependency_type,
                    'metadata': metadata
                }
                
                # Build mapping: source_name -> list of targets
                # One external system can call multiple programs
                if source_name not in inbound_interfaces:
                    inbound_interfaces[source_name] = []
                
                inbound_interfaces[source_name].append(target_dict)
            
            logger.debug(f"Loaded {len(inbound_interfaces)} external callers from inbound_interfaces table")
        
        except Exception as e:
            logger.warning(f"Error querying inbound_interfaces table: {e}")
            inbound_interfaces = {}
        
        # Cache the result for subsequent calls (performance optimization)
        # Cache is per-instance, so different flow builder instances have separate caches
        self._inbound_interfaces_cache = inbound_interfaces
        return inbound_interfaces
    
    def _query_outbound_interfaces(self) -> Set[str]:
        """
        Query outbound_interfaces table for configured external programs.
        
        Returns:
            Set of external program names
            
        Notes:
            - Replaces reading from YAML configuration
            - Queries database for persistent storage
            - Caches results per flow builder instance
        """
        # Return cached result if available (performance optimization)
        if self._outbound_interfaces_cache is not None:
            return self._outbound_interfaces_cache
        
        outbound_programs = set()
        cursor = self.db.cursor()
        
        try:
            # Check if outbound_interfaces table exists
            # This handles cases where schema hasn't been created yet
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='outbound_interfaces'
            """)
            
            if not cursor.fetchone():
                # Table doesn't exist, return empty set
                # This is not an error - just means no external programs configured
                logger.debug("outbound_interfaces table does not exist, returning empty set")
                self._outbound_interfaces_cache = set()
                return self._outbound_interfaces_cache
            
            # Query all external programs (both configured and auto-detected)
            # No filter on reason - we want all external programs regardless of how they were identified
            cursor.execute("""
                SELECT program_name
                FROM outbound_interfaces
            """)
            
            for row in cursor.fetchall():
                program_name = row[0]
                outbound_programs.add(program_name)
            
            logger.debug(f"Loaded {len(outbound_programs)} external programs from outbound_interfaces table")
        
        except Exception as e:
            logger.warning(f"Error querying outbound_interfaces table: {e}")
            outbound_programs = set()
        
        # Cache the result for subsequent calls (performance optimization)
        # Cache is per-instance, so different flow builder instances have separate caches
        self._outbound_interfaces_cache = outbound_programs
        return outbound_programs
    
    def _is_program_in_codebase(self, program_name: str) -> bool:
        """
        Check if a program exists in the analyzed codebase.
        
        A program is considered "in the codebase" if it appears as a source_artifact_name
        in the artifact_dependencies table, meaning it was analyzed and has dependencies.
        
        This is used to filter out cross-flow calls (calls between programs in the codebase)
        from inbound interfaces.
        
        Args:
            program_name: The program name to check
            
        Returns:
            True if program exists in analyzed codebase, False otherwise
            
        Notes:
            - Uses a simple COUNT query for efficiency
            - Caches results to avoid repeated database queries
            - This does NOT determine inbound interfaces - only filters cross-flow calls
            - Inbound interfaces are determined by inbound_interfaces table
        """
        # Check cache first (performance optimization)
        # Codebase membership doesn't change during flow building, so caching is safe
        if program_name in self._codebase_membership_cache:
            return self._codebase_membership_cache[program_name]
        
        cursor = self.db.cursor()
        is_in_codebase = False
        
        try:
            # Check if program exists as source_artifact_name in artifact_dependencies
            # If a program has dependencies, it was analyzed and is part of the codebase
            # This is the key check that distinguishes:
            #   - Codebase programs (analyzed, have dependencies) -> cross-flow calls
            #   - External programs (not analyzed, no dependencies) -> inbound interfaces
            cursor.execute("""
                SELECT COUNT(*) 
                FROM artifact_dependencies 
                WHERE source_artifact_name = ?
            """, (program_name,))
            
            count = cursor.fetchone()[0]
            is_in_codebase = count > 0
            
            logger.debug(f"Codebase check for {program_name}: {is_in_codebase} (count={count})")
        
        except Exception as e:
            logger.warning(f"Error checking codebase membership for {program_name}: {e}")
            # Default to False (treat as external) for conservative approach
            # Better to over-report inbound interfaces than miss them
            is_in_codebase = False
        
        # Cache the result for subsequent calls (performance optimization)
        self._codebase_membership_cache[program_name] = is_in_codebase
        return is_in_codebase
    
    def build_all_flows(self) -> List[str]:
        """
        Build migration flows for all entry points.
        
        This method:
        1. Identifies all entry point programs
        2. For each entry point, builds a complete migration flow
        3. Writes flow data to database
        4. Returns list of flow IDs
        
        Returns:
            List of flow IDs that were built
            
        Raises:
            Exception: If flow building fails
        """
        print("Building migration flows...")
        
        # Get all entry point programs
        entry_points = self._identify_entry_points()
        
        if not entry_points:
            print("Warning: No entry points found")
            return []
        
        print(f"Found {len(entry_points)} entry point programs")
        
        # Build flows for each entry point
        flow_ids = []
        successful = 0
        failed = 0
        
        for entry_program in entry_points:
            try:
                flow_id = self.build_flow(entry_program)
                flow_ids.append(flow_id)
                successful += 1
                print(f"  ✓ Built flow: {flow_id}")
            except Exception as e:
                failed += 1
                print(f"  ✗ Failed to build flow for {entry_program}: {e}")
        
        print(f"\nCompleted: {successful} successful, {failed} failed")
        
        # Update flow dependencies after all flows are built
        if flow_ids:
            print("\nUpdating flow dependencies...")
            try:
                self.update_flow_dependencies()
                print("✓ Flow dependencies updated")
            except Exception as e:
                print(f"⚠ Warning: Failed to update flow dependencies: {e}")
        
        return flow_ids
    
    def _identify_entry_points(self) -> List[str]:
        """
        Identify all entry point programs.
        
        Entry points are programs that can be invoked from outside:
        - Programs invoked by JCL
        - Programs invoked by CICS transactions
        - Programs defined in CSD
        - Programs called from BMS screens
        - Programs with external callers (configured)
        
        Filters out system utilities (FTP, IEWL, IKJEFT01, etc.) that have no file_path
        in the inventory table, as these are mainframe system programs not application code.
        
        Returns:
            List of unique entry point program names
        """
        entry_points = set()
        cursor = self.db.cursor()
        
        try:
            # Find programs invoked by JCL
            cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'JCL'
                  AND target_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('JCL_EXEC', 'EXEC_PGM', 'PROGRAM_CALL')
            """)
            
            for row in cursor.fetchall():
                entry_points.add(row[0])
            
            # Find programs invoked by CICS transactions
            cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE dependency_type IN ('CICS_TRANSACTION', 'TRANSACTION')
                  AND target_artifact_type = 'PROGRAM'
            """)
            
            for row in cursor.fetchall():
                entry_points.add(row[0])
            
            # Find programs defined in CSD
            cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE dependency_type = 'CICS_PROGRAM'
                  AND target_artifact_type = 'PROGRAM'
            """)
            
            for row in cursor.fetchall():
                entry_points.add(row[0])
            
            # Find programs called from BMS screens
            cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'SCREEN'
                  AND target_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('SCREEN_CALL', 'BMS_MAP')
            """)
            
            for row in cursor.fetchall():
                entry_points.add(row[0])
            
            # Add programs with configured external callers
            for caller_name, calls in self.external_callers.items():
                for call_info in calls:
                    target = call_info.get('target')
                    if target:
                        entry_points.add(target)
        
        except Exception as e:
            print(f"Warning: Error identifying entry points: {e}")
        
        # Filter out system utilities (programs without file_path in inventory)
        # These are mainframe system programs like FTP, IEWL, IKJEFT01, etc.
        filtered_entry_points = self._filter_system_utilities(entry_points)
        
        # Fallback: if no explicit entry points found, use inferred entry points
        # (programs not called by any other program in the codebase)
        if not filtered_entry_points:
            print("No explicit entry points found, falling back to inferred entry points...")
            try:
                # Get all programs with source code (have file_path in inventory)
                cursor.execute("""
                    SELECT DISTINCT artifact_name
                    FROM inventory
                    WHERE artifact_type IN ('PROGRAM', 'MAIN', 'SUBPROGRAM', 'FUNCTION')
                      AND file_path IS NOT NULL
                      AND file_path != ''
                      AND file_path NOT LIKE 'MISSING/%'
                """)
                all_programs = {row[0] for row in cursor.fetchall()}
                
                # Get programs that are called by other programs
                # Include FETCH for Natural codebases (FETCH RETURN)
                cursor.execute("""
                    SELECT DISTINCT target_artifact_name
                    FROM artifact_dependencies
                    WHERE dependency_type IN ('CALL', 'FETCH', 'FETCH_RETURN')
                      AND target_artifact_type = 'PROGRAM'
                      AND source_artifact_type = 'PROGRAM'
                """)
                called_programs = {row[0] for row in cursor.fetchall()}
                
                # Inferred entry points = programs not called by others
                inferred = all_programs - called_programs
                if inferred:
                    print(f"Found {len(inferred)} inferred entry points (programs not called by others)")
                    filtered_entry_points = inferred
            except Exception as e:
                print(f"Warning: Error identifying inferred entry points: {e}")
        
        return sorted(list(filtered_entry_points))
    def _filter_system_utilities(self, entry_points: set) -> set:
        """
        Filter out system utilities from entry points.

        System utilities are mainframe system programs (FTP, IEWL, IKJEFT01, etc.)
        that are called by JCL but are not part of the application codebase.

        These programs are identified by:
        - No file_path in the inventory table (not in source code)
        - file_path starts with 'MISSING/' (placeholder for missing artifacts)
        - Not in artifact_dependencies as source_artifact_name (not analyzed)

        Args:
            entry_points: Set of entry point program names

        Returns:
            Filtered set of entry points (application programs only)
        """
        if not entry_points:
            return entry_points

        filtered = set()
        cursor = self.db.cursor()
        system_utilities = []

        for program in entry_points:
            try:
                # Check if program has a valid file_path in inventory table
                cursor.execute("""
                    SELECT file_path
                    FROM inventory
                    WHERE artifact_name = ?
                      AND artifact_type IN ('PROGRAM', 'MAIN', 'SUBPROGRAM', 'FUNCTION')
                      AND file_path IS NOT NULL
                      AND file_path != ''
                """, (program,))

                result = cursor.fetchone()

                if result:
                    file_path = result[0]
                    # Check if file_path is a placeholder for missing artifacts
                    if file_path.startswith('MISSING/'):
                        # This is a missing artifact (system utility)
                        system_utilities.append(program)
                    else:
                        # Valid file_path - it's application code
                        filtered.add(program)
                else:
                    # No file_path - likely a system utility
                    # Double-check: is it in artifact_dependencies as source?
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM artifact_dependencies
                        WHERE source_artifact_name = ?
                    """, (program,))

                    count = cursor.fetchone()[0]

                    if count > 0:
                        # Has dependencies - it's application code
                        filtered.add(program)
                    else:
                        # No file_path and no dependencies - system utility
                        system_utilities.append(program)

            except Exception as e:
                logger.warning(f"Error checking program {program}: {e}")
                # Conservative: include it if we can't determine
                filtered.add(program)

        if system_utilities:
            print(f"\nFiltered out {len(system_utilities)} system utilities:")
            for util in sorted(system_utilities):
                print(f"  - {util}")

        return filtered

    
    def build_flow(self, entry_program: str) -> str:
        """
        Build single migration flow for an entry point program.
        
        This method orchestrates the complete flow building process:
        1. Generate flow ID
        2. Analyze program flow
        3. Detect entry point types
        4. Identify scope
        5. Identify interfaces
        6. Infer data operations
        7. Calculate complexity
        8. Identify flow dependencies
        9. Write to database
        
        Args:
            entry_program: Entry point program name
            
        Returns:
            Flow ID for the built flow
            
        Raises:
            ValueError: If entry_program is invalid
            MissingDataError: If entry point data is missing
            Exception: If flow building fails
        """
        if not entry_program:
            raise ValueError("entry_program cannot be empty")
        
        # Step 1: Generate flow ID
        flow_id = generate_flow_id(entry_program)
        
        # Step 2: Analyze program flow
        try:
            flow = self.flow_analyzer.analyze_flow(entry_program, max_depth=10)
        except Exception as e:
            raise MissingDataError(
                f"Failed to analyze flow for {entry_program}: {e}",
                data_type='flow_analysis',
                artifact_name=entry_program
            )
        
        # Check if flow has any programs
        if not flow.programs:
            raise MissingDataError(
                f"No programs found in flow for entry point {entry_program}",
                data_type='programs',
                artifact_name=entry_program
            )
        
        # Step 3: Detect entry point types
        entry_types = self.entry_point_detector.detect_entry_point_types(entry_program)
        
        # Warn if no entry types detected (but continue with empty list)
        if not entry_types:
            logger.warning(
                f"No entry point types detected for {entry_program}. "
                f"Flow {flow_id} will have no entry point invocation types."
            )
        
        primary_type = self._determine_primary_type(entry_types)
        
        # Step 4: Identify scope
        scope = self.identify_scope(flow)
        
        # Step 5: Identify interfaces
        interfaces = self.identify_interfaces(
            flow,
            entry_program,
            self.external_programs,
            self.external_callers
        )
        
        # Step 6: Infer data operations
        data_operations = self.data_operation_inferencer.infer_all_operations(flow.programs)
        
        # Step 7: Calculate complexity
        complexity = self.calculate_flow_complexity(flow.programs)
        
        # Step 8: Identify flow dependencies (will be populated after all flows are built)
        # For now, we'll write empty dependencies and update them later
        dependencies = {
            'requiredFlows': [],
            'dependentFlows': []
        }
        
        # Step 9: Write to database
        self._write_flow_to_database(
            flow_id=flow_id,
            entry_program=entry_program,
            primary_type=primary_type,
            entry_types=entry_types,
            scope=scope,
            interfaces=interfaces,
            data_operations=data_operations,
            complexity=complexity,
            dependencies=dependencies
        )
        
        return flow_id
    
    def _determine_primary_type(self, entry_types: List[Dict]) -> Optional[str]:
        """
        Determine the primary entry point type.
        
        The primary type is the most common invocation mechanism.
        If there's a tie, prioritize in this order:
        1. JCL (batch processing is often primary)
        2. CICS_TRANSACTION (online processing)
        3. CICS_PROGRAM (CSD definition)
        4. SCREEN (screen-driven)
        5. EXTERNAL_CALL (external invocation)
        
        Args:
            entry_types: List of entry type dictionaries
            
        Returns:
            Primary entry type string, or None if no types
        """
        if not entry_types:
            return None
        
        # Count callers for each type
        type_counts = {}
        for entry_type in entry_types:
            type_name = entry_type['type']
            caller_count = len(entry_type.get('callers', []))
            type_counts[type_name] = caller_count
        
        # Find type with most callers
        if not type_counts:
            return entry_types[0]['type']
        
        max_count = max(type_counts.values())
        types_with_max = [t for t, c in type_counts.items() if c == max_count]
        
        # If tie, use priority order
        priority_order = ['JCL', 'CICS_TRANSACTION', 'CICS_PROGRAM', 'SCREEN', 'EXTERNAL_CALL']
        
        for priority_type in priority_order:
            if priority_type in types_with_max:
                return priority_type
        
        # Fallback to first type with max count
        return types_with_max[0]
    
    def identify_scope(self, flow: 'ProgramFlow') -> Dict[str, List[str]]:
        """
        Identify artifacts within migration boundary.
        
        Scope includes:
        - All programs in the flow
        - All copybooks used by programs in the flow
        - All datasets accessed by programs in the flow
        
        Args:
            flow: ProgramFlow object from flow analysis
            
        Returns:
            Dictionary with keys 'programs', 'copybooks', 'datasets'
            Each value is a list of unique artifact names
        """
        scope = {
            'programs': [],
            'copybooks': [],
            'datasets': []
        }
        
        # Extract programs from flow (already unique in flow.programs)
        # Safety check: exclude artifacts that exist in inventory as FILE type
        # (prevents Adabas files like EMPLOYEES from appearing as program nodes)
        file_artifacts = set()
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT artifact_name FROM inventory
                WHERE artifact_type = 'FILE'
            """)
            file_artifacts = {row[0] for row in cursor.fetchall()}
        except Exception:
            pass
        
        scope['programs'] = [p for p in flow.programs if p not in file_artifacts]
        
        # Extract copybooks and datasets from dependencies
        # NOTE: flow.dependencies only contains program call dependencies (CALL, CICS_LINK, etc.)
        # We need to query the database directly for COPY and dataset dependencies
        copybooks_set = set()
        datasets_set = set()
        
        # Query database for copybooks and datasets used by programs in the flow
        cursor = self.db.cursor()
        
        for program in flow.programs:
            # Get copybooks (COPY dependencies)
            cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND dependency_type = 'COPY'
                  AND target_artifact_type = 'COPYBOOK'
            """, (program,))
            
            for row in cursor.fetchall():
                copybooks_set.add(row[0])
            
            # Get datasets (DATASET_REF, FILE_REF, CICS_FILE dependencies)
            cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND target_artifact_type IN ('DATASET', 'FILE')
            """, (program,))
            
            for row in cursor.fetchall():
                datasets_set.add(row[0])
        
        # Convert sets to sorted lists for consistent output
        scope['copybooks'] = sorted(list(copybooks_set))
        scope['datasets'] = sorted(list(datasets_set))
        
        return scope
    
    def identify_interfaces(
        self,
        flow: 'ProgramFlow',
        entry_program: str,
        external_programs: Optional[set] = None,
        external_callers: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Identify inbound and outbound interfaces with external program/caller support.
        
        This method identifies boundary crossing points where the flow interacts
        with external systems:
        - Inbound: External artifacts calling into this flow (from inbound_interfaces table)
        - Outbound: Programs in this flow calling external artifacts (from outbound_interfaces table)
        
        IMPORTANT: Entry point invocations are NOT inbound interfaces.
        They are captured in entryPoint.types instead.
        
        Args:
            flow: ProgramFlow object from flow analysis
            entry_program: The entry point program name
            external_programs: DEPRECATED - No longer used, queries database instead
            external_callers: DEPRECATED - No longer used, queries database instead
            
        Returns:
            Dictionary with 'inbound' and 'outbound' interface lists
            Each interface is a dict with: type, source, target, external (optional), metadata
        """
        interfaces = {
            'inbound': [],
            'outbound': []
        }
        
        # Note: external_programs and external_callers parameters are deprecated
        # The method now queries the database tables (inbound_interfaces, outbound_interfaces)
        # Parameters kept for backward compatibility but are ignored
        
        # Get set of programs in this flow for quick lookup
        flow_programs = set(flow.programs)
        
        # Identify inbound interfaces (external systems calling into flow)
        # Now queries database instead of using external_callers parameter
        inbound = self._identify_inbound_interfaces(
            flow, entry_program, flow_programs
        )
        interfaces['inbound'].extend(inbound)
        
        # Identify outbound interfaces (flow programs calling external)
        outbound = self._identify_outbound_interfaces(
            flow, flow_programs
        )
        interfaces['outbound'].extend(outbound)
        
        # Identify JCL outbound interfaces (flow submitting external JCL)
        jcl_outbound = self._identify_jcl_outbound_interfaces(flow, flow_programs)
        interfaces['outbound'].extend(jcl_outbound)
        
        return interfaces
    
    def _identify_inbound_interfaces(
        self,
        flow: 'ProgramFlow',
        entry_program: str,
        flow_programs: set
    ) -> List[Dict]:
        """
        Identify inbound interfaces (external systems calling into flow).
        
        IMPORTANT: Only creates inbound interfaces for calls from TRUE external systems
        (not in the analyzed codebase or configured in inbound_interfaces table).
        
        Cross-flow calls (from programs in the codebase to programs in this flow) are
        NOT inbound interfaces - they are handled through flow dependency relationships.
        
        Args:
            flow: ProgramFlow object
            entry_program: The entry point program name
            flow_programs: Set of programs in this flow
            
        Returns:
            List of inbound interface dictionaries
            
        Notes:
            - Queries inbound_interfaces table instead of reading YAML config
            - Uses database for persistent storage and querying
        """
        inbound = []
        
        # Query database for configured external callers
        # This replaces reading from YAML configuration files
        # Returns dict: {source_name: [{'target': ..., 'type': ..., 'metadata': ...}]}
        external_callers = self._query_inbound_interfaces()
        
        # Process each configured external caller
        for caller_name, calls in external_callers.items():
            for call_info in calls:
                target = call_info['target']
                
                # Only create inbound interface if target program is in this flow
                # External callers may target programs in other flows
                if target in flow_programs:
                    # CRITICAL CHECK: Is the caller actually in our analyzed codebase?
                    # This is the key fix for the bug - we need to distinguish:
                    #   1. True external systems (not in codebase) -> CREATE inbound interface
                    #   2. Programs in codebase (cross-flow calls) -> SKIP (not inbound)
                    if self._is_program_in_codebase(caller_name):
                        logger.debug(
                            f"Skipping inbound interface from {caller_name} to {target}: "
                            f"caller is in analyzed codebase (cross-flow call)"
                        )
                        continue
                    
                    # This is a true external caller (not in our codebase)
                    # Create inbound interface record
                    interface = {
                        'type': call_info.get('type', 'EXTERNAL_CALL'),
                        'source': caller_name,
                        'target': target,
                        'external': True,  # Always true for inbound interfaces
                        'metadata': {
                            'callingProgram': caller_name,
                            **call_info.get('metadata', {})  # Merge in any additional metadata
                        }
                    }
                    inbound.append(interface)
        
        return inbound
    
    def _identify_outbound_interfaces(
        self,
        flow: 'ProgramFlow',
        flow_programs: set
    ) -> List[Dict]:
        """
        Identify outbound interfaces (flow programs calling external programs).
        
        ENHANCED: Now queries outbound_interfaces table instead of configuration.
        Auto-detects external programs (programs without source code) before building interfaces.
        
        Args:
            flow: ProgramFlow object
            flow_programs: Set of programs in this flow
            
        Returns:
            List of outbound interface dictionaries
            
        Notes:
            - Queries outbound_interfaces table for external programs
            - Includes reason metadata from table
            - Auto-detects programs without source code
        """
        outbound = []
        
        # Auto-detect external programs (programs without source code)
        # This populates the outbound_interfaces table with programs that have no source code
        self._auto_detect_external_programs(flow_programs)
        
        # Query external programs from database
        all_external_programs = self._query_outbound_interfaces()
        
        # Query all program calls from this flow
        cursor = self.db.cursor()
        
        try:
            # Get all calls where source is in this flow
            cursor.execute("""
                SELECT DISTINCT
                    source_artifact_name,
                    target_artifact_name,
                    dependency_type,
                    target_artifact_type,
                    source_file_path,
                    line_number
                FROM artifact_dependencies
                WHERE source_artifact_name IN ({})
                  AND target_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('PROGRAM_CALL', 'CICS_LINK', 'CICS_XCTL', 
                                         'CICS_START', 'CALL', 'EXTERNAL_CALL')
            """.format(','.join('?' * len(flow_programs))), tuple(flow_programs))
            
            for row in cursor.fetchall():
                source_prog, target_prog, dep_type, target_type, file_path, line_num = row
                
                # Check if target is external
                is_external = (
                    target_prog not in flow_programs or
                    target_prog in all_external_programs
                )
                
                if is_external:
                    # Program in this flow calling external program
                    interface = {
                        'type': dep_type,
                        'source': source_prog,
                        'target': target_prog,
                        'external': True,
                        'metadata': {
                            'callingProgram': source_prog
                        }
                    }
                    
                    # Add optional metadata
                    if file_path:
                        interface['metadata']['filePath'] = file_path
                    if line_num:
                        interface['metadata']['lineNumber'] = line_num
                    
                    # Add reason if program is in outbound_interfaces table
                    if target_prog in all_external_programs:
                        # Query reason from database
                        try:
                            cursor_reason = self.db.cursor()
                            cursor_reason.execute("""
                                SELECT reason, metadata
                                FROM outbound_interfaces
                                WHERE program_name = ?
                            """, (target_prog,))
                            
                            reason_row = cursor_reason.fetchone()
                            if reason_row:
                                reason, metadata_json = reason_row
                                if reason:
                                    interface['metadata']['reason'] = reason
                                if metadata_json:
                                    try:
                                        db_metadata = json.loads(metadata_json)
                                        interface['metadata'].update(db_metadata)
                                    except json.JSONDecodeError:
                                        pass
                        except Exception as e:
                            logger.warning(f"Failed to query reason for {target_prog}: {e}")
                    
                    outbound.append(interface)
        
        except Exception as e:
            print(f"Warning: Error identifying outbound program interfaces: {e}")
        
        return outbound
    
    def _identify_jcl_outbound_interfaces(
        self,
        flow: 'ProgramFlow',
        flow_programs: set
    ) -> List[Dict]:
        """
        Identify JCL outbound interfaces (flow submitting external JCL).
        
        This identifies cases where programs in the flow submit or invoke
        external JCL jobs.
        
        Args:
            flow: ProgramFlow object
            flow_programs: Set of programs in this flow
            
        Returns:
            List of JCL outbound interface dictionaries
        """
        outbound = []
        
        # Query for JCL submissions from programs in this flow
        cursor = self.db.cursor()
        
        try:
            # Get all JCL submissions where source is in this flow
            cursor.execute("""
                SELECT DISTINCT
                    source_artifact_name,
                    target_artifact_name,
                    dependency_type,
                    source_file_path,
                    line_number
                FROM artifact_dependencies
                WHERE source_artifact_name IN ({})
                  AND target_artifact_type = 'JCL'
                  AND dependency_type IN ('JCL_SUBMIT', 'JCL_CALL', 'SUBMIT')
            """.format(','.join('?' * len(flow_programs))), tuple(flow_programs))
            
            for row in cursor.fetchall():
                source_prog, target_jcl, dep_type, file_path, line_num = row
                
                # This is a program in the flow submitting external JCL
                interface = {
                    'type': 'JCL',
                    'source': source_prog,
                    'target': target_jcl,
                    'external': True,
                    'metadata': {
                        'jclName': target_jcl,
                        'submittingProgram': source_prog
                    }
                }
                
                # Add optional metadata
                if file_path:
                    interface['metadata']['filePath'] = file_path
                if line_num:
                    interface['metadata']['lineNumber'] = line_num
                
                outbound.append(interface)
        
        except Exception as e:
            print(f"Warning: Error identifying JCL outbound interfaces: {e}")
        
        return outbound
    
    def _auto_detect_external_programs(self, flow_programs: set) -> int:
        """
        Auto-detect external programs (programs without source code) and insert into database.
        
        This method identifies programs that are called by the flow but have no source code
        in the analyzed tree. These are automatically treated as external programs and
        inserted into the outbound_interfaces table.
        
        Args:
            flow_programs: Set of programs in current flow
            
        Returns:
            Number of external programs detected and inserted
            
        Notes:
            - Queries artifact_dependencies for programs called by flow
            - Checks program_file_mapping for source code existence
            - Inserts into outbound_interfaces with reason="missing_source_code"
            - Skips duplicates (UNIQUE constraint)
        """
        detected_count = 0
        cursor = self.db.cursor()
        
        try:
            # Check if outbound_interfaces table exists
            # If not, we can't auto-detect (schema not created yet)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='outbound_interfaces'
            """)
            
            if not cursor.fetchone():
                logger.debug("outbound_interfaces table does not exist, skipping auto-detection")
                return 0
            
            # Check if program_file_mapping table exists
            # This table maps programs to their source files
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='program_file_mapping'
            """)
            
            has_mapping_table = cursor.fetchone() is not None
            
            if not flow_programs:
                return 0
            
            # Query all programs called by this flow
            # These are potential external programs if they have no source code
            placeholders = ','.join('?' * len(flow_programs))
            cursor.execute(f"""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_name IN ({placeholders})
                  AND target_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('PROGRAM_CALL', 'CICS_LINK', 'CICS_XCTL', 
                                         'CICS_START', 'CALL', 'EXTERNAL_CALL')
            """, tuple(flow_programs))
            
            called_programs = [row[0] for row in cursor.fetchall()]
            
            # For each called program, check if it has source code
            for program_name in called_programs:
                has_source_code = False
                
                if has_mapping_table:
                    # Preferred method: Check program_file_mapping for source code
                    # This table explicitly maps programs to their source files
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM program_file_mapping 
                        WHERE program_name = ?
                    """, (program_name,))
                    
                    count = cursor.fetchone()[0]
                    has_source_code = count > 0
                else:
                    # Fallback method: Check if program exists as source in artifact_dependencies
                    # If a program has dependencies, it was analyzed and has source code
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM artifact_dependencies 
                        WHERE source_artifact_name = ?
                    """, (program_name,))
                    
                    count = cursor.fetchone()[0]
                    has_source_code = count > 0
                
                # If no source code found, this is an external program
                # Insert into outbound_interfaces table for tracking
                if not has_source_code:
                    try:
                        # INSERT OR IGNORE prevents duplicates (UNIQUE constraint on program_name)
                        # This is safe to run multiple times
                        cursor.execute("""
                            INSERT OR IGNORE INTO outbound_interfaces 
                            (program_name, reason, metadata, created_at)
                            VALUES (?, ?, ?, ?)
                        """, (
                            program_name,
                            'missing_source_code',  # Reason: auto-detected due to missing source
                            json.dumps({'auto_detected': True}),  # Metadata for tracking
                            datetime.now().isoformat()
                        ))
                        
                        # Check if row was inserted (rowcount > 0 means new insert)
                        # rowcount = 0 means duplicate (already exists)
                        if cursor.rowcount > 0:
                            detected_count += 1
                            logger.debug(f"Auto-detected external program: {program_name}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to insert external program {program_name}: {e}")
            
            # Commit all inserts at once (more efficient than per-row commits)
            self.db.commit()
            
            if detected_count > 0:
                logger.info(f"Auto-detected {detected_count} external programs without source code")
        
        except Exception as e:
            logger.warning(f"Error during auto-detection of external programs: {e}")
            detected_count = 0
        
        return detected_count
    
    def calculate_flow_complexity(self, programs: List[str]) -> Dict:
        """
        Calculate aggregate complexity metrics for a flow.
        
        This method sums complexity metrics across all programs in the flow
        and calculates a composite complexity score and tier.
        
        The complexity object contains:
        - totalPrograms: Count of programs in the flow
        - totalLines: Sum of lines of code across all programs
        - cyclomaticComplexity: Sum of cyclomatic complexity across all programs
        - compositeScore: Weighted composite complexity score
        - tier: One of "LOW", "MEDIUM", "HIGH", "VERY_HIGH", or "UNKNOWN"
        
        Args:
            programs: List of program names in the flow
            
        Returns:
            Dictionary with complexity metrics:
            {
                'totalPrograms': int,
                'totalLines': int,
                'cyclomaticComplexity': int,
                'compositeScore': float,
                'tier': str
            }
            
        Notes:
            - If complexity data is not available for a program, it uses default values (0)
            - If no programs have complexity data, tier is set to "UNKNOWN"
            - Composite score is calculated using the same formula as individual programs
        """
        # Initialize aggregated metrics
        total_programs = len(programs)
        total_lines = 0
        total_cyclomatic = 0
        programs_with_data = 0
        
        # Query complexity metrics from database
        cursor = self.db.cursor()
        
        try:
            # Check if complexity_metrics table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='complexity_metrics'
            """)
            
            if not cursor.fetchone():
                # Table doesn't exist, return default values
                return {
                    'totalPrograms': total_programs,
                    'totalLines': 0,
                    'cyclomaticComplexity': 0,
                    'compositeScore': 0.0,
                    'tier': 'UNKNOWN'
                }
            
            # Query complexity metrics for all programs in the flow
            if programs:
                placeholders = ','.join('?' * len(programs))
                cursor.execute(f"""
                    SELECT 
                        program_name,
                        lines_of_code,
                        cyclomatic_complexity,
                        composite_score
                    FROM complexity_metrics
                    WHERE program_name IN ({placeholders})
                """, programs)
                
                # Sum up metrics
                for row in cursor.fetchall():
                    prog_name, loc, cyclomatic, composite = row
                    
                    # Sum lines of code
                    if loc is not None:
                        total_lines += loc
                    
                    # Sum cyclomatic complexity
                    if cyclomatic is not None:
                        total_cyclomatic += cyclomatic
                    
                    programs_with_data += 1
        
        except Exception as e:
            logger.warning(f"Error querying complexity metrics: {e}")
            # Continue with default values
        
        # Log warning if no complexity data found
        if programs_with_data == 0 and total_programs > 0:
            logger.warning(
                "No complexity data found for any programs in flow. "
                "Using default values (tier=UNKNOWN). "
                f"Missing program count: {min(total_programs, 5)}"
            )
        elif programs_with_data < total_programs:
            # Find which programs are missing
            programs_with_metrics = set()
            cursor.execute(f"""
                SELECT program_name
                FROM complexity_metrics
                WHERE program_name IN ({placeholders})
            """, programs)
            programs_with_metrics = {row[0] for row in cursor.fetchall()}
            
            missing_count = total_programs - programs_with_data
            
            logger.info(
                f"Partial complexity data: {programs_with_data}/{total_programs} programs have metrics. "
                f"Missing count: {missing_count}"
            )
        
        # Calculate composite score
        # Use a simplified formula: weighted average of normalized metrics
        # This matches the approach in ComplexityMetrics.calculate_composite_score
        composite_score = self._calculate_composite_score(
            total_lines, 
            total_cyclomatic,
            total_programs
        )
        
        # Determine complexity tier
        tier = self._determine_complexity_tier(composite_score, programs_with_data)
        
        return {
            'totalPrograms': total_programs,
            'totalLines': total_lines,
            'cyclomaticComplexity': total_cyclomatic,
            'compositeScore': round(composite_score, 2),
            'tier': tier
        }
    
    def _calculate_composite_score(
        self, 
        total_lines: int, 
        total_cyclomatic: int,
        total_programs: int
    ) -> float:
        """
        Calculate composite complexity score for a flow.
        
        The composite score is a weighted combination of:
        - Lines of code (normalized)
        - Cyclomatic complexity (normalized)
        - Program count (normalized)
        
        Args:
            total_lines: Total lines of code across all programs
            total_cyclomatic: Total cyclomatic complexity across all programs
            total_programs: Number of programs in the flow
            
        Returns:
            Composite complexity score (0-100+)
            
        Notes:
            - Uses standard weights: LOC=0.4, Cyclomatic=0.4, Programs=0.2
            - Normalizes metrics to a 0-100 scale
            - Higher scores indicate higher complexity
        """
        # Standard weights for flow complexity
        LOC_WEIGHT = 0.4
        CYCLOMATIC_WEIGHT = 0.4
        PROGRAM_COUNT_WEIGHT = 0.2
        
        # Normalization factors (based on typical mainframe application scales)
        # These convert raw metrics to a 0-100 scale
        # Adjusted to produce reasonable scores for typical flows
        LOC_NORMALIZATION = 50.0  # 5,000 LOC = score of 100
        CYCLOMATIC_NORMALIZATION = 5.0  # 500 cyclomatic = score of 100
        PROGRAM_NORMALIZATION = 0.5  # 50 programs = score of 100
        
        # Normalize metrics
        normalized_loc = (total_lines / LOC_NORMALIZATION) if total_lines > 0 else 0
        normalized_cyclomatic = (total_cyclomatic / CYCLOMATIC_NORMALIZATION) if total_cyclomatic > 0 else 0
        normalized_programs = (total_programs / PROGRAM_NORMALIZATION) if total_programs > 0 else 0
        
        # Calculate weighted composite score
        composite = (
            (normalized_loc * LOC_WEIGHT) +
            (normalized_cyclomatic * CYCLOMATIC_WEIGHT) +
            (normalized_programs * PROGRAM_COUNT_WEIGHT)
        )
        
        return composite
    
    def _determine_complexity_tier(self, composite_score: float, programs_with_data: int) -> str:
        """
        Determine complexity tier based on composite score.
        
        Tiers are defined as:
        - LOW: score < 25
        - MEDIUM: 25 <= score < 50
        - HIGH: 50 <= score < 75
        - VERY_HIGH: score >= 75
        - UNKNOWN: no complexity data available
        
        Args:
            composite_score: Composite complexity score
            programs_with_data: Number of programs with complexity data
            
        Returns:
            Complexity tier string
        """
        # If no programs have complexity data, return UNKNOWN
        if programs_with_data == 0:
            return 'UNKNOWN'
        
        # Determine tier based on score thresholds
        if composite_score < 25:
            return 'LOW'
        elif composite_score < 50:
            return 'MEDIUM'
        elif composite_score < 75:
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    def identify_flow_dependencies(
        self,
        flow_id: str,
        entry_program: str,
        interfaces: Dict[str, List[Dict]]
    ) -> Dict[str, List[str]]:
        """
        Identify dependencies between flows.
        
        This method identifies:
        1. Required flows: Flows that must be migrated before this flow
           (flows containing programs that this flow calls)
        2. Dependent flows: Flows that depend on this flow
           (flows that call programs in this flow)
        
        The method analyzes interfaces to determine flow-to-flow dependencies:
        - Outbound interfaces → Required flows (this flow depends on them)
        - Inbound interfaces → Dependent flows (they depend on this flow)
        
        Args:
            flow_id: The flow ID for this flow
            entry_program: The entry point program name for this flow
            interfaces: Dictionary with 'inbound' and 'outbound' interface lists
            
        Returns:
            Dictionary with:
            {
                'requiredFlows': [flow_ids that must be migrated first],
                'dependentFlows': [flow_ids that depend on this flow]
            }
            
        Notes:
            - Handles circular dependencies by detecting and logging them
            - Returns empty arrays if no dependencies exist
            - Only includes flows that exist in the database
        """
        dependencies = {
            'requiredFlows': [],
            'dependentFlows': []
        }
        
        # Identify required flows (outbound dependencies)
        required = self._identify_required_flows(flow_id, interfaces.get('outbound', []))
        dependencies['requiredFlows'] = required
        
        # Identify dependent flows (inbound dependencies)
        dependent = self._identify_dependent_flows(flow_id, entry_program, interfaces.get('inbound', []))
        dependencies['dependentFlows'] = dependent
        
        # Check for circular dependencies
        circular = set(required) & set(dependent)
        if circular:
            print(f"Warning: Circular dependencies detected for flow {flow_id}: {circular}")
        
        return dependencies
    
    def _identify_required_flows(
        self,
        flow_id: str,
        outbound_interfaces: List[Dict]
    ) -> List[str]:
        """
        Identify required flows (flows that must be migrated before this flow).
        
        This method analyzes outbound interfaces to find external programs that
        are entry points of other flows. Those flows must be migrated first.
        
        Args:
            flow_id: The flow ID for this flow
            outbound_interfaces: List of outbound interface dictionaries
            
        Returns:
            List of flow IDs that must be migrated before this flow
        """
        required_flows = set()
        
        # Extract target programs from outbound interfaces
        target_programs = set()
        for interface in outbound_interfaces:
            target = interface.get('target')
            if target:
                target_programs.add(target)
        
        if not target_programs:
            return []
        
        # Query database to find which of these programs are entry points
        cursor = self.db.cursor()
        
        try:
            # Check if migration_flows table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='migration_flows'
            """)
            
            if not cursor.fetchone():
                # Table doesn't exist yet, return empty list
                return []
            
            # Find flows where entry_program matches our target programs
            placeholders = ','.join('?' * len(target_programs))
            cursor.execute(f"""
                SELECT DISTINCT flow_id
                FROM migration_flows
                WHERE entry_program IN ({placeholders})
                  AND flow_id != ?
            """, (*target_programs, flow_id))
            
            for row in cursor.fetchall():
                required_flow_id = row[0]
                required_flows.add(required_flow_id)
        
        except Exception as e:
            logger.warning(f"Error identifying required flows for {flow_id}: {e}")
        
        if not required_flows and target_programs:
            logger.debug(
                f"No required flows found for {flow_id}, "
                f"though {len(target_programs)} external programs are called"
            )
        
        return sorted(list(required_flows))
    
    def _identify_dependent_flows(
        self,
        flow_id: str,
        entry_program: str,
        inbound_interfaces: List[Dict]
    ) -> List[str]:
        """
        Identify dependent flows (flows that depend on this flow).
        
        This method analyzes inbound interfaces to find external programs that
        call into this flow. If those programs belong to other flows, those
        flows depend on this flow.
        
        Args:
            flow_id: The flow ID for this flow
            entry_program: The entry point program for this flow
            inbound_interfaces: List of inbound interface dictionaries
            
        Returns:
            List of flow IDs that depend on this flow
        """
        dependent_flows = set()
        
        # Extract source programs from inbound interfaces
        source_programs = set()
        for interface in inbound_interfaces:
            source = interface.get('source')
            if source:
                source_programs.add(source)
        
        if not source_programs:
            return []
        
        # Query database to find which flows contain these source programs
        cursor = self.db.cursor()
        
        try:
            # Check if migration_flows and flow_scope tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='migration_flows'
            """)
            
            if not cursor.fetchone():
                # Table doesn't exist yet, return empty list
                return []
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='flow_scope'
            """)
            
            if not cursor.fetchone():
                # Table doesn't exist yet, return empty list
                return []
            
            # Find flows that contain these source programs in their scope
            placeholders = ','.join('?' * len(source_programs))
            cursor.execute(f"""
                SELECT DISTINCT flow_id
                FROM flow_scope
                WHERE artifact_type = 'PROGRAM'
                  AND artifact_name IN ({placeholders})
                  AND flow_id != ?
            """, (*source_programs, flow_id))
            
            for row in cursor.fetchall():
                dependent_flow_id = row[0]
                dependent_flows.add(dependent_flow_id)
        
        except Exception as e:
            logger.warning(f"Error identifying dependent flows for {flow_id}: {e}")
        
        if not dependent_flows and source_programs:
            logger.debug(
                f"No dependent flows found for {flow_id}, "
                f"though {len(source_programs)} external programs call into it"
            )
        
        return sorted(list(dependent_flows))
    
    def _validate_flow_data(
        self,
        flow_id: str,
        entry_program: str,
        primary_type: Optional[str],
        entry_types: List[Dict],
        scope: Dict[str, List[str]],
        interfaces: Dict[str, List[Dict]],
        data_operations: Dict[str, List[Dict]],
        complexity: Dict,
        dependencies: Dict[str, List[str]]
    ) -> None:
        """
        Validate flow data before writing to database.
        
        This method performs comprehensive validation of flow data to ensure:
        - Required fields are present and valid
        - Data structures are well-formed
        - References are consistent
        - Constraints are satisfied
        
        Args:
            flow_id: Unique flow identifier
            entry_program: Entry point program name
            primary_type: Primary entry point type
            entry_types: List of all entry point types with callers
            scope: Dictionary with programs, copybooks, datasets
            interfaces: Dictionary with inbound/outbound interfaces
            data_operations: Dictionary with database and dataset operations
            complexity: Dictionary with complexity metrics
            dependencies: Dictionary with required/dependent flows
            
        Raises:
            FlowValidationError: If validation fails
        """
        # Validate flow ID
        if not flow_id:
            raise FlowValidationError("Flow ID cannot be empty")
        
        if not flow_id.startswith("FLOW_"):
            raise FlowValidationError(
                f"Flow ID must start with 'FLOW_': {flow_id}",
                flow_id=flow_id
            )
        
        # Validate entry program
        if not entry_program:
            raise FlowValidationError(
                "Entry program cannot be empty",
                flow_id=flow_id
            )
        
        # Validate entry types structure
        if not isinstance(entry_types, list):
            raise FlowValidationError(
                "Entry types must be a list",
                flow_id=flow_id,
                details={'entry_types_type': type(entry_types).__name__}
            )
        
        # Validate each entry type
        for i, entry_type in enumerate(entry_types):
            if not isinstance(entry_type, dict):
                raise FlowValidationError(
                    f"Entry type at index {i} must be a dictionary",
                    flow_id=flow_id
                )
            
            if 'type' not in entry_type:
                raise FlowValidationError(
                    f"Entry type at index {i} missing 'type' field",
                    flow_id=flow_id
                )
            
            if 'callers' not in entry_type:
                raise FlowValidationError(
                    f"Entry type at index {i} missing 'callers' field",
                    flow_id=flow_id
                )
            
            if not isinstance(entry_type['callers'], list):
                raise FlowValidationError(
                    f"Entry type at index {i} 'callers' must be a list",
                    flow_id=flow_id
                )
        
        # Validate scope structure
        if not isinstance(scope, dict):
            raise FlowValidationError(
                "Scope must be a dictionary",
                flow_id=flow_id,
                details={'scope_type': type(scope).__name__}
            )
        
        required_scope_keys = ['programs', 'copybooks', 'datasets']
        for key in required_scope_keys:
            if key not in scope:
                raise FlowValidationError(
                    f"Scope missing required key: {key}",
                    flow_id=flow_id
                )
            
            if not isinstance(scope[key], list):
                raise FlowValidationError(
                    f"Scope[{key}] must be a list",
                    flow_id=flow_id,
                    details={f'{key}_type': type(scope[key]).__name__}
                )
        
        # Validate that entry program is in scope programs
        if entry_program not in scope['programs']:
            logger.warning(
                f"Entry program {entry_program} not in scope programs for flow {flow_id}"
            )
        
        # Validate interfaces structure
        if not isinstance(interfaces, dict):
            raise FlowValidationError(
                "Interfaces must be a dictionary",
                flow_id=flow_id,
                details={'interfaces_type': type(interfaces).__name__}
            )
        
        required_interface_keys = ['inbound', 'outbound']
        for key in required_interface_keys:
            if key not in interfaces:
                raise FlowValidationError(
                    f"Interfaces missing required key: {key}",
                    flow_id=flow_id
                )
            
            if not isinstance(interfaces[key], list):
                raise FlowValidationError(
                    f"Interfaces[{key}] must be a list",
                    flow_id=flow_id,
                    details={f'{key}_type': type(interfaces[key]).__name__}
                )
        
        # Validate each interface
        for direction in ['inbound', 'outbound']:
            for i, interface in enumerate(interfaces[direction]):
                if not isinstance(interface, dict):
                    raise FlowValidationError(
                        f"{direction.capitalize()} interface at index {i} must be a dictionary",
                        flow_id=flow_id
                    )
                
                required_fields = ['type', 'source', 'target']
                for field in required_fields:
                    if field not in interface:
                        raise FlowValidationError(
                            f"{direction.capitalize()} interface at index {i} missing '{field}' field",
                            flow_id=flow_id
                        )
        
        # Validate data operations structure
        if not isinstance(data_operations, dict):
            raise FlowValidationError(
                "Data operations must be a dictionary",
                flow_id=flow_id,
                details={'data_operations_type': type(data_operations).__name__}
            )
        
        required_data_op_keys = ['databases', 'datasets']
        for key in required_data_op_keys:
            if key not in data_operations:
                raise FlowValidationError(
                    f"Data operations missing required key: {key}",
                    flow_id=flow_id
                )
            
            if not isinstance(data_operations[key], list):
                raise FlowValidationError(
                    f"Data operations[{key}] must be a list",
                    flow_id=flow_id,
                    details={f'{key}_type': type(data_operations[key]).__name__}
                )
        
        # Validate complexity structure
        if not isinstance(complexity, dict):
            raise FlowValidationError(
                "Complexity must be a dictionary",
                flow_id=flow_id,
                details={'complexity_type': type(complexity).__name__}
            )
        
        required_complexity_keys = ['totalPrograms', 'totalLines', 'cyclomaticComplexity', 
                                   'compositeScore', 'tier']
        for key in required_complexity_keys:
            if key not in complexity:
                raise FlowValidationError(
                    f"Complexity missing required key: {key}",
                    flow_id=flow_id
                )
        
        # Validate complexity tier
        valid_tiers = ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH', 'UNKNOWN']
        if complexity['tier'] not in valid_tiers:
            raise FlowValidationError(
                f"Invalid complexity tier: {complexity['tier']}. Must be one of: {', '.join(valid_tiers)}",
                flow_id=flow_id
            )
        
        # Validate dependencies structure
        if not isinstance(dependencies, dict):
            raise FlowValidationError(
                "Dependencies must be a dictionary",
                flow_id=flow_id,
                details={'dependencies_type': type(dependencies).__name__}
            )
        
        required_dep_keys = ['requiredFlows', 'dependentFlows']
        for key in required_dep_keys:
            if key not in dependencies:
                raise FlowValidationError(
                    f"Dependencies missing required key: {key}",
                    flow_id=flow_id
                )
            
            if not isinstance(dependencies[key], list):
                raise FlowValidationError(
                    f"Dependencies[{key}] must be a list",
                    flow_id=flow_id,
                    details={f'{key}_type': type(dependencies[key]).__name__}
                )
        
        logger.debug(f"Flow data validation passed for {flow_id}")
    
    def _write_flow_to_database(
        self,
        flow_id: str,
        entry_program: str,
        primary_type: Optional[str],
        entry_types: List[Dict],
        scope: Dict[str, List[str]],
        interfaces: Dict[str, List[Dict]],
        data_operations: Dict[str, List[Dict]],
        complexity: Dict,
        dependencies: Dict[str, List[str]]
    ) -> None:
        """
        Write complete flow data to database.
        
        This method writes to all migration flow tables:
        1. migration_flows (main metadata)
        2. flow_entry_types (all invocation types)
        3. flow_scope (programs, copybooks, datasets)
        4. flow_interfaces (inbound/outbound)
        5. flow_data_operations (database and dataset operations)
        6. flow_dependencies (flow-to-flow dependencies)
        
        Args:
            flow_id: Unique flow identifier
            entry_program: Entry point program name
            primary_type: Primary entry point type
            entry_types: List of all entry point types with callers
            scope: Dictionary with programs, copybooks, datasets
            interfaces: Dictionary with inbound/outbound interfaces
            data_operations: Dictionary with database and dataset operations
            complexity: Dictionary with complexity metrics
            dependencies: Dictionary with required/dependent flows
            
        Raises:
            FlowValidationError: If flow data validation fails
            Exception: If database write fails
        """
        # Validate flow data before writing
        self._validate_flow_data(
            flow_id, entry_program, primary_type, entry_types,
            scope, interfaces, data_operations, complexity, dependencies
        )
        
        cursor = self.db.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # 1. Write migration_flows (main metadata)
            self._write_flow_metadata(
                cursor, flow_id, entry_program, primary_type, scope, complexity
            )
            
            # 2. Write flow_entry_types (all invocation types)
            self._write_flow_entry_types(cursor, flow_id, entry_types)
            
            # 3. Write flow_scope (programs, copybooks, datasets)
            self._write_flow_scope(cursor, flow_id, scope)
            
            # 4. Write flow_interfaces (inbound/outbound)
            self._write_flow_interfaces(cursor, flow_id, interfaces)
            
            # 5. Write flow_data_operations (database and dataset operations)
            self._write_flow_data_operations(cursor, flow_id, data_operations)
            
            # 6. Write flow_dependencies (flow-to-flow dependencies)
            self._write_flow_dependencies(cursor, flow_id, dependencies)
            
            # Commit transaction
            self.db.commit()
        
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            raise Exception(f"Failed to write flow {flow_id} to database: {e}")
    
    def _write_flow_metadata(
        self,
        cursor,
        flow_id: str,
        entry_program: str,
        primary_type: Optional[str],
        scope: Dict[str, List[str]],
        complexity: Dict
    ) -> None:
        """Write flow metadata to migration_flows table."""
        
        # Generate flow name from entry program
        flow_name = entry_program.replace('_', ' ').title()
        
        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT OR REPLACE INTO migration_flows (
                flow_id,
                name,
                entry_program,
                primary_entry_type,
                total_programs,
                total_copybooks,
                total_datasets,
                complexity_total_lines,
                complexity_cyclomatic,
                complexity_score,
                complexity_tier,
                created_date,
                updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flow_id,
            flow_name,
            entry_program,
            primary_type,
            len(scope.get('programs', [])),
            len(scope.get('copybooks', [])),
            len(scope.get('datasets', [])),
            complexity.get('totalLines', 0),
            complexity.get('cyclomaticComplexity', 0),
            complexity.get('compositeScore', 0.0),
            complexity.get('tier', 'UNKNOWN'),
            current_date,
            current_date
        ))
    
    def _write_flow_entry_types(
        self,
        cursor,
        flow_id: str,
        entry_types: List[Dict]
    ) -> None:
        """Write entry point types to flow_entry_types table using batch inserts."""
        
        # Prepare batch data for all entry types and callers
        batch_data = []
        
        for entry_type in entry_types:
            type_name = entry_type['type']
            callers = entry_type.get('callers', [])
            
            for caller in callers:
                caller_source = caller.get('source', '')
                metadata = caller.get('metadata', {})
                metadata_json = json.dumps(metadata) if metadata else None
                
                batch_data.append((flow_id, type_name, caller_source, metadata_json))
        
        # Batch insert all entry types
        if batch_data:
            cursor.executemany("""
                INSERT OR REPLACE INTO flow_entry_types (
                    flow_id,
                    entry_type,
                    caller_source,
                    metadata_json
                ) VALUES (?, ?, ?, ?)
            """, batch_data)
    
    def _write_flow_scope(
        self,
        cursor,
        flow_id: str,
        scope: Dict[str, List[str]]
    ) -> None:
        """Write scope artifacts to flow_scope table using batch inserts."""
        
        # Prepare batch data for all artifacts
        batch_data = []
        
        # Add programs
        for program in scope.get('programs', []):
            batch_data.append((flow_id, 'PROGRAM', program))
        
        # Add copybooks
        for copybook in scope.get('copybooks', []):
            batch_data.append((flow_id, 'COPYBOOK', copybook))
        
        # Add datasets
        for dataset in scope.get('datasets', []):
            batch_data.append((flow_id, 'DATASET', dataset))
        
        # Batch insert all artifacts
        if batch_data:
            cursor.executemany("""
                INSERT OR REPLACE INTO flow_scope (
                    flow_id,
                    artifact_type,
                    artifact_name
                ) VALUES (?, ?, ?)
            """, batch_data)
    
    def _write_flow_interfaces(
        self,
        cursor,
        flow_id: str,
        interfaces: Dict[str, List[Dict]]
    ) -> None:
        """Write interfaces to flow_interfaces table using batch inserts."""
        
        # Prepare batch data for all interfaces
        batch_data = []
        
        # Add inbound interfaces
        for interface in interfaces.get('inbound', []):
            metadata = interface.get('metadata', {})
            metadata_json = json.dumps(metadata) if metadata else None
            
            batch_data.append((
                flow_id,
                'INBOUND',
                interface.get('type', 'UNKNOWN'),
                interface.get('source', ''),
                interface.get('target', ''),
                interface.get('external', False),
                metadata_json
            ))
        
        # Add outbound interfaces
        for interface in interfaces.get('outbound', []):
            metadata = interface.get('metadata', {})
            metadata_json = json.dumps(metadata) if metadata else None
            
            batch_data.append((
                flow_id,
                'OUTBOUND',
                interface.get('type', 'UNKNOWN'),
                interface.get('source', ''),
                interface.get('target', ''),
                interface.get('external', True),
                metadata_json
            ))
        
        # Batch insert all interfaces
        if batch_data:
            cursor.executemany("""
                INSERT INTO flow_interfaces (
                    flow_id,
                    direction,
                    interface_type,
                    source,
                    target,
                    external,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
    
    def _write_flow_data_operations(
        self,
        cursor,
        flow_id: str,
        data_operations: Dict[str, List[Dict]]
    ) -> None:
        """Write data operations to flow_data_operations table using batch inserts."""
        
        # Prepare batch data for all data operations
        batch_data = []
        
        # Add database operations
        for db_op in data_operations.get('databases', []):
            batch_data.append((
                flow_id,
                'DATABASE',
                db_op.get('operation', 'UNKNOWN'),
                db_op.get('type', 'UNKNOWN'),
                db_op.get('target', ''),
                db_op.get('program', ''),
                None  # mode is NULL for database operations
            ))
        
        # Add dataset operations (one row per program accessing the dataset)
        for ds_op in data_operations.get('datasets', []):
            programs = ds_op.get('programs', [])
            
            for program in programs:
                batch_data.append((
                    flow_id,
                    'DATASET',
                    'ACCESS',
                    None,  # db_type is NULL for dataset operations
                    ds_op.get('name', ''),
                    program,
                    ds_op.get('mode', 'UNKNOWN')
                ))
        
        # Batch insert all data operations
        if batch_data:
            cursor.executemany("""
                INSERT INTO flow_data_operations (
                    flow_id,
                    operation_category,
                    operation_type,
                    db_type,
                    target,
                    program,
                    mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
    
    def _write_flow_dependencies(
        self,
        cursor,
        flow_id: str,
        dependencies: Dict[str, List[str]]
    ) -> None:
        """Write flow dependencies to flow_dependencies table using batch inserts."""
        
        # Prepare batch data for all dependencies
        batch_data = []
        
        # Add required flows (this flow depends on them)
        for required_flow_id in dependencies.get('requiredFlows', []):
            batch_data.append((flow_id, required_flow_id, 'REQUIRED'))
        
        # Add dependent flows (they depend on this flow)
        for dependent_flow_id in dependencies.get('dependentFlows', []):
            batch_data.append((dependent_flow_id, flow_id, 'REQUIRED'))
        
        # Batch insert all dependencies
        if batch_data:
            cursor.executemany("""
                INSERT OR REPLACE INTO flow_dependencies (
                    flow_id,
                    depends_on_flow_id,
                    dependency_type
                ) VALUES (?, ?, ?)
            """, batch_data)
    
    def update_flow_dependencies(self) -> None:
        """
        Update flow dependencies after all flows have been built.
        
        This method should be called after build_all_flows() to populate
        the flow dependencies based on interfaces.
        
        It identifies:
        1. Required flows (outbound dependencies)
        2. Dependent flows (inbound dependencies)
        """
        print("Updating flow dependencies...")
        
        cursor = self.db.cursor()
        
        try:
            # Get all flows
            cursor.execute("SELECT flow_id, entry_program FROM migration_flows")
            flows = cursor.fetchall()
            
            updated = 0
            
            for flow_id, entry_program in flows:
                # Get interfaces for this flow
                cursor.execute("""
                    SELECT direction, interface_type, source, target
                    FROM flow_interfaces
                    WHERE flow_id = ?
                """, (flow_id,))
                
                interfaces = {
                    'inbound': [],
                    'outbound': []
                }
                
                for direction, iface_type, source, target in cursor.fetchall():
                    interface = {
                        'type': iface_type,
                        'source': source,
                        'target': target
                    }
                    
                    if direction == 'INBOUND':
                        interfaces['inbound'].append(interface)
                    else:
                        interfaces['outbound'].append(interface)
                
                # Identify dependencies
                dependencies = self.identify_flow_dependencies(
                    flow_id, entry_program, interfaces
                )
                
                # Clear existing dependencies for this flow
                cursor.execute("""
                    DELETE FROM flow_dependencies
                    WHERE flow_id = ?
                """, (flow_id,))
                
                # Write updated dependencies
                self._write_flow_dependencies(cursor, flow_id, dependencies)
                
                updated += 1
            
            self.db.commit()
            print(f"✓ Updated dependencies for {updated} flows")
        
        except Exception as e:
            self.db.rollback()
            print(f"✗ Failed to update flow dependencies: {e}")
            raise
