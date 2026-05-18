"""
Migration Flow Exporter

This module provides functionality for exporting migration flows from database
to JSON format. It queries flow data from migration tables and formats it
according to the migration-focused JSON schema.
"""

import json
import logging
import os
import sqlite3
from typing import Dict, List, Optional, Any

from .exceptions import ExportError, MissingDataError
from ..analysis.copybook_analyzer import COBOLCopybookAnalyzer
from ..parsers.bms_map_parser import BMSMapParser

from dataclasses import dataclass


@dataclass
class FlowExportConfig:
    """
    Configuration options for flow export behavior.

    Attributes:
        filter_internal_procedures: If True, exclude internal procedures from flow scope.
                                   Default is True for accurate migration analysis.
        include_file_metadata: If True, enrich exports with file path metadata.
                              Default is True for comprehensive traceability.
        include_record_layouts: If True, embed full record layouts and BMS map definitions
                               inline in each copybook entry. Default is False to keep
                               the flow JSON lean. When False, copybooks only include
                               name, filePath, and copybookType.
        export_bms_screens: If True, write BMS screen definitions to a separate companion
                           file (<output>_bms_screens.json) alongside the flow export.
                           Default is False. The original .bms source files are already
                           reachable via each BMS copybook's filePath (swap cpy-bms → bms,
                           change extension to .bms). Only takes effect when an output_file
                           is specified and include_record_layouts is False.
    """
    filter_internal_procedures: bool = True
    include_file_metadata: bool = True
    include_record_layouts: bool = False
    export_bms_screens: bool = False

# Configure logging
logger = logging.getLogger(__name__)


class MigrationFlowExporter:
    """
    Exports migration flows from database to JSON format.
    
    This class provides methods to:
    1. Query flow data from database tables
    2. Format data into migration-focused JSON structure
    3. Export all flows or specific flows
    4. Apply filters (complexity, business domain, entry type)
    5. Filter internal procedures from flow scope
    6. Enrich exports with file path metadata
    
    The exporter supports two key enhancements:
    - Internal procedure filtering: Excludes internal procedures (COBOL PERFORM targets,
      PL/I internal procedures) from flow scope to provide accurate migration analysis
    - File metadata enrichment: Adds file paths, line numbers, program types, and language
      information to programs, copybooks, and dependencies for comprehensive traceability
    
    Both features are enabled by default and can be controlled via configuration flags.
    """
    
    def __init__(
        self, 
        db_connection: sqlite3.Connection,
        filter_internal_procedures: bool = True,
        include_file_metadata: bool = True,
        include_record_layouts: bool = False,
        export_bms_screens: bool = False
    ):
        """
        Initialize the MigrationFlowExporter.

        Args:
            db_connection: SQLite database connection
            filter_internal_procedures: If True, exclude internal procedures from flow scope.
                                       Default is True for accurate migration analysis.
            include_file_metadata: If True, enrich exports with file path metadata.
                                  Default is True for comprehensive traceability.
            include_record_layouts: If True, embed full record layouts and BMS map
                                   definitions inline in copybook entries. Default is
                                   False to keep the flow JSON lean.
            export_bms_screens: If True, write BMS screen definitions to a separate
                               companion file alongside the flow export. Default is False.
        """
        self.db = db_connection
        self.cursor = db_connection.cursor()
        self.extended_scope = False  # Default to normal scope format
        self.sort_order = None  # Default to no sorting

        # Store configuration options
        self.config = FlowExportConfig(
            filter_internal_procedures=filter_internal_procedures,
            include_file_metadata=include_file_metadata,
            include_record_layouts=include_record_layouts,
            export_bms_screens=export_bms_screens,
        )
        
        # Collected BMS screen data for separate export
        self._bms_screens: Dict[str, Dict[str, Any]] = {}

        # Initialize metadata cache for performance optimization
        self._program_metadata_cache: Dict[str, Dict[str, Any]] = {}
        
        # Flag to track if program_file_mapping table is available
        self._metadata_available = False
        
        # Initialize copybook and BMS analyzers for enrichment
        self._copybook_analyzer = COBOLCopybookAnalyzer()
        self._bms_parser = BMSMapParser()
        
        self._load_program_metadata_cache()

    
    def _load_program_metadata_cache(self) -> None:
        """
        Load all program_file_mapping data into cache on initialization.
        
        This method loads all program metadata from the program_file_mapping
        table into memory to avoid repeated database queries during export.
        The cache is stored as a dictionary mapping program names to their
        metadata dictionaries.
        
        If the program_file_mapping table doesn't exist, the cache remains
        empty and queries will gracefully return None.
        """
        try:
            # Load all program metadata from program_file_mapping
            # JOIN with inventory to get file_path (new schema with file_id)
            self.cursor.execute("""
                SELECT 
                    pfm.program_name,
                    inv.file_path,
                    pfm.start_line,
                    pfm.end_line,
                    pfm.program_type,
                    pfm.language
                FROM program_file_mapping pfm
                JOIN inventory inv ON pfm.file_id = inv.id
            """)
            
            # Build cache dictionary
            for row in self.cursor.fetchall():
                program_name, file_path, start_line, end_line, program_type, language = row
                
                self._program_metadata_cache[program_name] = {
                    'filePath': file_path,
                    'startLine': start_line,
                    'endLine': end_line,
                    'programType': program_type,
                    'language': language
                }
            
            self._metadata_available = True
            logger.debug(f"Loaded {len(self._program_metadata_cache)} program metadata entries into cache")
            
        except sqlite3.OperationalError as e:
            # JOIN with inventory failed — try legacy schema (file_path directly on pfm)
            try:
                self.cursor.execute("""
                    SELECT 
                        program_name,
                        file_path,
                        start_line,
                        end_line,
                        program_type,
                        language
                    FROM program_file_mapping
                """)
                
                for row in self.cursor.fetchall():
                    program_name, file_path, start_line, end_line, program_type, language = row
                    
                    self._program_metadata_cache[program_name] = {
                        'filePath': file_path,
                        'startLine': start_line,
                        'endLine': end_line,
                        'programType': program_type,
                        'language': language
                    }
                
                self._metadata_available = True
                logger.debug(
                    f"Loaded {len(self._program_metadata_cache)} program metadata entries "
                    "into cache (legacy schema without inventory JOIN)"
                )
                
            except sqlite3.OperationalError:
                # Table doesn't exist at all - cache remains empty
                self._metadata_available = False
                logger.error(
                    f"program_file_mapping table not found: {e}. "
                    "Falling back to export without file metadata and filtering."
                )
                logger.info("Export will continue with current behavior (no metadata enrichment or filtering)")

    @classmethod
    def _get_standalone_program_types(cls) -> List[str]:
        """
        Get list of program types that indicate standalone execution capability.

        Standalone programs are those that can be executed independently
        (e.g., via JCL EXEC, CICS LINK). Internal procedures cannot be
        executed independently.

        Returns:
            List of program type strings that indicate standalone programs

        Note:
            - MAIN: Main program entry point
            - SUBPROGRAM: Callable subprogram
            - ENTRY_POINT: Program with ENTRY statement
            - CSECT: Control section (assembler)
            - ROUTINE: Standalone routine
            - FUNCTION: Standalone function (Natural .NS8/.NSA modules)

            Excluded types (internal procedures):
            - PROCEDURE: Internal procedure (COBOL PERFORM target, PL/I procedure)
            - NESTED: Nested program
            - DATA: Data area / local data area (Natural .NSL/.NSG modules)
        """
        return ['MAIN', 'SUBPROGRAM', 'ENTRY_POINT', 'CSECT', 'ROUTINE', 'FUNCTION']

    def _is_standalone_program(self, program_name: str) -> bool:
        """
        Determine if a program is standalone (can be executed independently).

        This method queries the program_file_mapping table to check the
        program_type. Programs with types like MAIN, SUBPROGRAM, ENTRY_POINT,
        CSECT, ROUTINE, and FUNCTION are considered standalone. Programs with
        types like PROCEDURE, NESTED, and DATA are internal procedures.

        Args:
            program_name: Name of the program to check

        Returns:
            True if program is standalone, False if internal procedure.
            Returns True if no mapping found (backward compatibility).

        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> exporter._is_standalone_program('PAYROLL1')  # MAIN program
            True
            >>> exporter._is_standalone_program('CALC_TAX')  # PROCEDURE
            False
        """
        # If metadata is not available, assume standalone for backward compatibility
        if not self._metadata_available:
            return True
            
        try:
            # Query program_file_mapping for program_type
            self.cursor.execute("""
                SELECT program_type
                FROM program_file_mapping
                WHERE program_name = ?
            """, (program_name,))

            row = self.cursor.fetchone()

            if row is None:
                # No mapping found - assume standalone for backward compatibility
                return True

            program_type = row[0]

            # Check if program type indicates standalone execution
            standalone_types = self._get_standalone_program_types()
            return program_type in standalone_types

        except sqlite3.OperationalError as e:
            # Table doesn't exist or query failed - assume standalone for backward compatibility
            logger.debug(f"Error querying program_type for {program_name}: {e}")
            return True
    
    def _enrich_with_file_metadata(self, program_name: str) -> Optional[Dict[str, Any]]:
        """
        Get file location metadata for a program.
        
        This method retrieves file path, line numbers, program type, and
        language information for a given program. It first checks the
        metadata cache (populated from program_file_mapping), and if not
        found, falls back to querying the inventory table directly.
        
        Args:
            program_name: Name of the program
            
        Returns:
            Dictionary with file metadata or None if not found:
            {
                'filePath': str,
                'startLine': int (optional),
                'endLine': int (optional),
                'programType': str (optional),
                'language': str
            }
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> metadata = exporter._enrich_with_file_metadata('PAYROLL1')
            >>> print(metadata)
            {
                'filePath': 'src/cobol/PAYROLL1.cbl',
                'startLine': 1,
                'endLine': 450,
                'programType': 'MAIN',
                'language': 'COBOL'
            }
        """
        # First, lookup in cache (from program_file_mapping)
        cached_metadata = self._program_metadata_cache.get(program_name)
        if cached_metadata:
            return cached_metadata
        
        # Fall back to inventory table for programs not in program_file_mapping
        # This handles single-program files that don't have program boundaries
        try:
            self.cursor.execute("""
                SELECT file_path, language
                FROM inventory
                WHERE artifact_name = ?
                    AND artifact_type = 'PROGRAM'
                LIMIT 1
            """, (program_name,))
            
            row = self.cursor.fetchone()
            if row:
                file_path, language = row
                return {
                    'filePath': file_path,
                    'language': language
                }
        except sqlite3.Error as e:
            logger.debug(f"Error querying inventory for {program_name}: {e}")
        
        return None
    
    def _get_copybook_file_path(self, copybook_name: str) -> Optional[str]:
        """
        Get file path for a copybook from inventory.

        This method queries the inventory table to retrieve the file path
        for a given copybook. The inventory table stores all artifacts
        including copybooks with their file locations.

        Args:
            copybook_name: Name of the copybook

        Returns:
            File path string or None if not found

        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> path = exporter._get_copybook_file_path('CUSTCOPY')
            >>> print(path)
            'src/copybooks/CUSTCOPY.cpy'
        """
        try:
            # Query inventory table for copybook file path
            # Also check FUNCTION type since Natural USING statements create COPY
            # dependencies for Global Data Areas that may be classified as FUNCTION
            self.cursor.execute("""
                SELECT file_path
                FROM inventory
                WHERE artifact_name = ?
                  AND artifact_type IN ('COPYBOOK', 'FUNCTION', 'DATA')
            """, (copybook_name,))

            row = self.cursor.fetchone()

            if row is None:
                # No file path found - return None for graceful degradation
                return None

            return row[0]

        except sqlite3.OperationalError as e:
            # Table doesn't exist or query failed - return None for graceful degradation
            logger.debug(f"Error querying copybook file path for {copybook_name}: {e}")
            return None


    
    def export_all_flows(
        self,
        output_file: Optional[str] = None,
        flow_ids: Optional[List[str]] = None,
        min_complexity: Optional[str] = None,
        business_domain: Optional[str] = None,
        entry_type: Optional[str] = None,
        extended_scope: bool = False,
        sort_order: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Export all flows matching filters to JSON.
        
        This method:
        1. Queries all flows from database (with optional filters)
        2. For each flow, queries all related data
        3. Applies internal procedure filtering (if enabled in config)
        4. Enriches with file metadata (if enabled in config)
        5. Formats data into JSON structure
        6. Optionally writes to file
        7. Returns formatted JSON
        
        Args:
            output_file: Optional path to write JSON output
            flow_ids: Optional list of specific flow IDs to export
            min_complexity: Minimum complexity tier ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')
            business_domain: Filter by business domain
            entry_type: Filter by entry point type
            extended_scope: Include utility metadata in scope output (default False)
            sort_order: Sort flows by strategy (default None - database order)
                       Options: 'complexity-asc', 'complexity-desc', 'independence', 
                               'dependencies', 'name'
            
        Returns:
            Dictionary with 'flows' key containing list of flow objects.
            Each flow includes file metadata for programs, copybooks, and dependencies
            (if include_file_metadata=True). Internal procedures are excluded from
            scope (if filter_internal_procedures=True).
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> result = exporter.export_all_flows(
            ...     output_file='flows.json',
            ...     min_complexity='HIGH',
            ...     extended_scope=True,
            ...     sort_order='complexity-asc'
            ... )
            >>> print(f"Exported {len(result['flows'])} flows")
            
        Note:
            The exporter configuration controls filtering and metadata enrichment:
            - filter_internal_procedures=True: Excludes internal procedures from scope
            - include_file_metadata=True: Adds file paths and metadata to exports
        """
        # Store flags for use in export_flows
        self.extended_scope = extended_scope
        self.sort_order = sort_order
        
        # Apply combined filters to get flow IDs
        filtered_flow_ids = self.apply_combined_filters(
            flow_ids=flow_ids,
            min_complexity=min_complexity,
            business_domain=business_domain,
            entry_type=entry_type
        )
        
        # Export flows
        return self.export_flows(filtered_flow_ids, output_file)
    
    def export_flows(
        self,
        flow_ids: List[str],
        output_file: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Export specific flows to JSON.
        
        This method:
        1. Queries data for specified flow IDs
        2. Formats data into JSON structure
        3. Optionally writes to file
        4. Returns formatted JSON
        
        Args:
            flow_ids: List of flow IDs to export
            output_file: Optional path to write JSON output
            
        Returns:
            Dictionary with 'flows' key containing list of flow objects
            
        Raises:
            ExportError: If export operation fails
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> result = exporter.export_flows(
            ...     flow_ids=['FLOW_PAYROLL1', 'FLOW_BILLING1'],
            ...     output_file='selected_flows.json'
            ... )
        """
        if not flow_ids:
            logger.warning("No flow IDs provided for export")
            result = {'flows': [], 'metadata': {'total_flows': 0}}
            # Still write the output file so downstream consumers don't fail
            if output_file:
                try:
                    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    logger.info(f"Wrote empty flows file to {output_file}")
                except Exception as e:
                    logger.error(f"Failed to write empty flows file: {e}")
            return result
        
        logger.info(f"Exporting {len(flow_ids)} flows")
        
        # Query and format each flow
        flows = []
        failed_flows = []
        incomplete_flows = []
        
        for flow_id in flow_ids:
            try:
                flow_data = self._query_flow(flow_id)
                if flow_data:
                    # Check for incomplete data
                    is_incomplete, missing_items = self._is_incomplete_flow(flow_data)
                    if is_incomplete:
                        incomplete_flows.append((flow_id, missing_items))
                        logger.warning(
                            f"Flow {flow_id} has incomplete data: missing {', '.join(missing_items)}"
                        )
                    flows.append(flow_data)
                else:
                    failed_flows.append(flow_id)
                    logger.error(f"Failed to query flow {flow_id}: No data returned")
            except Exception as e:
                failed_flows.append(flow_id)
                logger.error(f"Failed to export flow {flow_id}: {e}")
        
        # Log summary
        if failed_flows:
            logger.warning(
                f"Failed to export {len(failed_flows)} flows: {', '.join(failed_flows[:5])}"
                f"{'...' if len(failed_flows) > 5 else ''}"
            )
        
        if incomplete_flows:
            logger.info(
                f"{len(incomplete_flows)} flows have incomplete data"
            )
            # Log details for first few flows
            for flow_id, missing_items in incomplete_flows[:5]:
                logger.info(f"  {flow_id}: missing {', '.join(missing_items)}")
            if len(incomplete_flows) > 5:
                logger.info(f"  ... and {len(incomplete_flows) - 5} more")
        
        logger.info(f"Successfully exported {len(flows)} flows")
        
        # Apply sorting if format is specified
        if hasattr(self, 'sort_order') and self.sort_order:
            flows = self._sort_flows(flows, self.sort_order)
        
        # Format into final JSON structure
        try:
            result = self._format_json(flows)
        except Exception as e:
            raise ExportError(
                "Failed to format flows as JSON",
                operation='format',
                cause=e
            )
        
        # Write to file if specified
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                logger.info(f"Exported {len(flows)} flows to {output_file}")
            except Exception as e:
                raise ExportError(
                    f"Failed to write to file {output_file}",
                    operation='write',
                    cause=e
                )
            
            # Write BMS screens companion file if collected
            if self._bms_screens and self.config.export_bms_screens:
                bms_file = self._derive_bms_screens_path(output_file)
                try:
                    bms_result = {
                        'metadata': {
                            'description': 'BMS screen definitions extracted from mainframe BMS map sources',
                            'total_screens': len(self._bms_screens),
                            'source_flows_file': os.path.basename(output_file),
                        },
                        'screens': list(self._bms_screens.values())
                    }
                    with open(bms_file, 'w') as f:
                        json.dump(bms_result, f, indent=2)
                    logger.info(
                        f"Exported {len(self._bms_screens)} BMS screen(s) to {bms_file}"
                    )
                except Exception as e:
                    logger.error(f"Failed to write BMS screens file: {e}")
        
        return result
    
    def _is_incomplete_flow(self, flow_data: Dict) -> tuple[bool, list[str]]:
        """
        Check if flow data is incomplete.
        
        A flow is considered incomplete if:
        - No entry point types
        - No programs in scope
        - Complexity tier is UNKNOWN
        - No data operations
        
        Args:
            flow_data: Flow data dictionary
            
        Returns:
            Tuple of (is_incomplete, list of missing items)
        """
        incomplete = False
        missing_items = []
        
        # Check entry point types
        entry_types = flow_data.get('entryPoint', {}).get('types', [])
        if not entry_types:
            logger.debug(f"Flow {flow_data.get('flowId')} has no entry point types")
            incomplete = True
            missing_items.append("entry point types")
        
        # Check scope programs
        programs = flow_data.get('scope', {}).get('programs', [])
        if not programs:
            logger.warning(f"Flow {flow_data.get('flowId')} has no programs in scope")
            incomplete = True
            missing_items.append("programs in scope")
        
        # Check complexity tier
        tier = flow_data.get('complexity', {}).get('tier')
        if tier == 'UNKNOWN':
            logger.debug(f"Flow {flow_data.get('flowId')} has UNKNOWN complexity tier")
            incomplete = True
            missing_items.append("complexity data")
        
        # Check data operations
        db_ops = flow_data.get('dataOperations', {}).get('databases', [])
        ds_ops = flow_data.get('dataOperations', {}).get('datasets', [])
        if not db_ops and not ds_ops:
            logger.debug(f"Flow {flow_data.get('flowId')} has no data operations")
            incomplete = True
            missing_items.append("data operations")
        
        return incomplete, missing_items

    @staticmethod
    def _derive_bms_screens_path(output_file: str) -> str:
        """Derive the BMS screens companion file path from the main output file path.

        For 'results/carddemo_flows.json' returns 'results/carddemo_flows_bms_screens.json'.
        """
        base, ext = os.path.splitext(output_file)
        return f"{base}_bms_screens{ext}"

    
    def _query_flow(self, flow_id: str) -> Optional[Dict]:
        """
        Query single flow from database.
        
        This method queries all data for a single flow:
        1. Flow metadata (migration_flows table)
        2. Entry point types (flow_entry_types table)
        3. Scope (flow_scope table)
        4. Interfaces (flow_interfaces table)
        5. Data operations (flow_data_operations table)
        6. Dependencies (flow_dependencies table)
        
        Args:
            flow_id: Flow ID to query
            
        Returns:
            Dictionary with complete flow data, or None if flow not found
        """
        # Query flow metadata
        self.cursor.execute("""
            SELECT 
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
                priority,
                business_domain
            FROM migration_flows
            WHERE flow_id = ?
        """, (flow_id,))
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        # Unpack metadata
        (flow_id, name, entry_program, primary_type, total_programs, total_copybooks,
         total_datasets, total_lines, cyclomatic, composite_score, tier,
         priority, business_domain) = row
        
        # Build flow object
        flow = {
            'flowId': flow_id,
            'name': name,
            'entryPoint': {
                'program': entry_program,
                'types': self._query_entry_types(flow_id)
            }
        }
        
        # Add primary type if available
        if primary_type:
            flow['entryPoint']['primaryType'] = primary_type
        
        # Add scope
        flow['scope'] = self._query_scope(flow_id)
        
        # Add interfaces
        flow['interfaces'] = self._query_interfaces(flow_id)
        
        # Add data operations
        flow['dataOperations'] = self._query_data_operations(flow_id)
        
        # Add complexity
        flow['complexity'] = {
            'totalPrograms': total_programs,
            'totalLines': total_lines,
            'cyclomaticComplexity': cyclomatic,
            'compositeScore': float(composite_score) if composite_score else 0.0,
            'tier': tier if tier else 'UNKNOWN'
        }
        
        # Add optional fields
        if priority is not None:
            flow['priority'] = priority
        
        if business_domain:
            flow['businessDomain'] = business_domain
        
        # Add dependencies
        flow['dependencies'] = self._query_dependencies(flow_id)
        
        # Add invokedByJobs (jobs that invoke this flow's entry point)
        flow['invokedByJobs'] = self._query_invoking_jobs(entry_program)
        
        return flow
    
    def _query_entry_types(self, flow_id: str) -> List[Dict]:
        """
        Query all invocation types for an entry point.
        
        This method queries the flow_entry_types table to get all ways
        the entry point can be invoked, along with all callers for each type.
        File metadata is added to caller sources when available.
        
        Args:
            flow_id: Flow ID to query
            
        Returns:
            List of entry type dictionaries, each with:
            - type: Entry point type (JCL, CICS_TRANSACTION, etc.)
            - callers: List of caller objects with source, metadata, and filePath
            
        Example:
            [
                {
                    'type': 'JCL',
                    'callers': [
                        {
                            'source': 'PAYROLL01',
                            'filePath': 'jcl/PAYROLL01.jcl',
                            'metadata': {...}
                        },
                        {
                            'source': 'PAYWEEK',
                            'filePath': 'jcl/PAYWEEK.jcl',
                            'metadata': {...}
                        }
                    ]
                },
                {
                    'type': 'CICS_TRANSACTION',
                    'callers': [
                        {'source': 'PAY1', 'metadata': {...}}
                    ]
                }
            ]
        """
        self.cursor.execute("""
            SELECT 
                entry_type,
                caller_source,
                metadata_json
            FROM flow_entry_types
            WHERE flow_id = ?
            ORDER BY entry_type, caller_source
        """, (flow_id,))
        
        # Group callers by entry type
        types_dict = {}
        
        for row in self.cursor.fetchall():
            entry_type, caller_source, metadata_json = row
            
            # Initialize type if not seen before
            if entry_type not in types_dict:
                types_dict[entry_type] = []
            
            # Parse metadata
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            
            # Build caller object
            caller = {
                'source': caller_source
            }
            
            # Add file metadata for caller programs if configuration enabled
            if self.config.include_file_metadata:
                file_metadata = self._enrich_with_file_metadata(caller_source)
                if file_metadata and 'filePath' in file_metadata:
                    caller['filePath'] = file_metadata['filePath']
            
            if metadata:
                caller['metadata'] = metadata
            
            types_dict[entry_type].append(caller)
        
        # Convert to list format
        entry_types = []
        for entry_type, callers in types_dict.items():
            entry_types.append({
                'type': entry_type,
                'callers': callers
            })
        
        return entry_types
    
    def _query_scope(self, flow_id: str) -> Dict[str, List]:
        """
        Query flow scope (programs, copybooks, datasets) with filtering and metadata.
        
        This method queries flow scope and:
        1. Filters out internal procedures from programs list (if config.filter_internal_procedures=True)
        2. Adds file path metadata to programs and copybooks (if config.include_file_metadata=True)
        3. Maintains backward compatibility with extended_scope flag
        
        Args:
            flow_id: Flow ID to query
            
        Returns:
            Dictionary with keys 'programs', 'copybooks', 'datasets'
            - programs: List of program objects with metadata
            - copybooks: List of copybook objects with metadata
            - datasets: List of dataset names (no metadata)
        """
        programs = []
        programs_without_metadata = []
        total_programs_before_filter = 0
        
        try:
            # Count total programs before filtering if needed
            if self._metadata_available and self.config.filter_internal_procedures:
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM flow_scope
                    WHERE flow_id = ?
                        AND artifact_type = 'PROGRAM'
                """, (flow_id,))
                total_programs_before_filter = self.cursor.fetchone()[0]
            
            # Build query based on configuration and metadata availability
            if self._metadata_available and self.config.filter_internal_procedures and self.config.include_file_metadata:
                # Query programs with LEFT JOIN to program_file_mapping for filtering and metadata
                self.cursor.execute("""
                    SELECT 
                        fs.artifact_name,
                        inv.file_path,
                        pfm.start_line,
                        pfm.end_line,
                        pfm.program_type,
                        pfm.language
                    FROM flow_scope fs
                    LEFT JOIN program_file_mapping pfm 
                        ON fs.artifact_name = pfm.program_name
                    LEFT JOIN inventory inv
                        ON pfm.file_id = inv.id
                    WHERE fs.flow_id = ?
                        AND fs.artifact_type = 'PROGRAM'
                        AND (
                            pfm.program_type IS NULL
                            OR pfm.program_type IN ('MAIN', 'SUBPROGRAM', 'ENTRY_POINT', 'CSECT', 'ROUTINE', 'FUNCTION')
                        )
                    ORDER BY fs.artifact_name
                """, (flow_id,))
            elif self._metadata_available and self.config.filter_internal_procedures:
                # Query programs with filtering but no metadata
                self.cursor.execute("""
                    SELECT 
                        fs.artifact_name,
                        pfm.program_type
                    FROM flow_scope fs
                    LEFT JOIN program_file_mapping pfm 
                        ON fs.artifact_name = pfm.program_name
                    WHERE fs.flow_id = ?
                        AND fs.artifact_type = 'PROGRAM'
                        AND (
                            pfm.program_type IS NULL
                            OR pfm.program_type IN ('MAIN', 'SUBPROGRAM', 'ENTRY_POINT', 'CSECT', 'ROUTINE', 'FUNCTION')
                        )
                    ORDER BY fs.artifact_name
                """, (flow_id,))
            elif self._metadata_available and self.config.include_file_metadata:
                # Query programs with metadata but no filtering
                self.cursor.execute("""
                    SELECT 
                        fs.artifact_name,
                        inv.file_path,
                        pfm.start_line,
                        pfm.end_line,
                        pfm.program_type,
                        pfm.language
                    FROM flow_scope fs
                    LEFT JOIN program_file_mapping pfm 
                        ON fs.artifact_name = pfm.program_name
                    LEFT JOIN inventory inv
                        ON pfm.file_id = inv.id
                    WHERE fs.flow_id = ?
                        AND fs.artifact_type = 'PROGRAM'
                    ORDER BY fs.artifact_name
                """, (flow_id,))
            else:
                # Simple query with no filtering or metadata
                self.cursor.execute("""
                    SELECT artifact_name
                    FROM flow_scope
                    WHERE flow_id = ?
                        AND artifact_type = 'PROGRAM'
                    ORDER BY artifact_name
                """, (flow_id,))
            
            for row in self.cursor.fetchall():
                program_name = row[0]
                
                # Build program object with metadata based on configuration
                program_obj = {'name': program_name}
                
                # Add file metadata if configuration enabled and available
                if self.config.include_file_metadata and len(row) > 1:
                    if row[1] is not None:
                        # Metadata from JOIN query
                        program_obj['filePath'] = row[1]
                        program_obj['startLine'] = row[2]
                        program_obj['endLine'] = row[3]
                        program_obj['programType'] = row[4]
                        program_obj['language'] = row[5]
                    else:
                        # Fall back to enrichment method (queries inventory table)
                        metadata = self._enrich_with_file_metadata(program_name)
                        if metadata:
                            program_obj.update(metadata)
                        else:
                            # Track programs without metadata
                            programs_without_metadata.append(program_name)
                
                programs.append(program_obj)
            
            # Log filtered programs summary
            if self._metadata_available and self.config.filter_internal_procedures and total_programs_before_filter > 0:
                filtered_count = total_programs_before_filter - len(programs)
                if filtered_count > 0:
                    logger.warning(
                        f"Flow {flow_id}: Filtered {filtered_count} internal procedure(s) from scope"
                    )
            
            # Log programs without metadata
            if programs_without_metadata:
                logger.warning(
                    f"Flow {flow_id}: {len(programs_without_metadata)} program(s) have no file mapping: "
                    f"{', '.join(programs_without_metadata[:5])}"
                    f"{'...' if len(programs_without_metadata) > 5 else ''}"
                )
                
        except sqlite3.OperationalError as e:
            # JOIN with inventory failed - try using program_file_mapping directly
            # for filtering and/or metadata (legacy schema has file_path on pfm)
            logger.error(f"Error querying programs for flow {flow_id}: {e}")
            
            try:
                if self._metadata_available and (self.config.filter_internal_procedures or self.config.include_file_metadata):
                    logger.info("Retrying with legacy schema (program_file_mapping without inventory JOIN)")
                    
                    if self.config.filter_internal_procedures:
                        self.cursor.execute("""
                            SELECT 
                                fs.artifact_name,
                                pfm.file_path,
                                pfm.start_line,
                                pfm.end_line,
                                pfm.program_type,
                                pfm.language
                            FROM flow_scope fs
                            LEFT JOIN program_file_mapping pfm 
                                ON fs.artifact_name = pfm.program_name
                            WHERE fs.flow_id = ?
                                AND fs.artifact_type = 'PROGRAM'
                                AND (
                                    pfm.program_type IS NULL
                                    OR pfm.program_type IN ('MAIN', 'SUBPROGRAM', 'ENTRY_POINT', 'CSECT', 'ROUTINE', 'FUNCTION')
                                )
                            ORDER BY fs.artifact_name
                        """, (flow_id,))
                    else:
                        self.cursor.execute("""
                            SELECT 
                                fs.artifact_name,
                                pfm.file_path,
                                pfm.start_line,
                                pfm.end_line,
                                pfm.program_type,
                                pfm.language
                            FROM flow_scope fs
                            LEFT JOIN program_file_mapping pfm 
                                ON fs.artifact_name = pfm.program_name
                            WHERE fs.flow_id = ?
                                AND fs.artifact_type = 'PROGRAM'
                            ORDER BY fs.artifact_name
                        """, (flow_id,))
                    
                    for row in self.cursor.fetchall():
                        program_obj = {'name': row[0]}
                        if self.config.include_file_metadata and row[1] is not None:
                            program_obj['filePath'] = row[1]
                            program_obj['startLine'] = row[2]
                            program_obj['endLine'] = row[3]
                            program_obj['programType'] = row[4]
                            program_obj['language'] = row[5]
                        elif self.config.include_file_metadata and row[1] is None:
                            # Try enrichment from cache
                            metadata = self._enrich_with_file_metadata(row[0])
                            if metadata and metadata.get('filePath') is not None:
                                program_obj.update(metadata)
                            else:
                                programs_without_metadata.append(row[0])
                        programs.append(program_obj)
                else:
                    raise sqlite3.OperationalError("No filtering or metadata needed, use simple fallback")
                    
            except sqlite3.OperationalError:
                logger.info("Falling back to simple query without filtering or metadata")
                
                self.cursor.execute("""
                    SELECT artifact_name
                    FROM flow_scope
                    WHERE flow_id = ?
                        AND artifact_type = 'PROGRAM'
                    ORDER BY artifact_name
                """, (flow_id,))
                
                for row in self.cursor.fetchall():
                    programs.append({'name': row[0]})
        
        copybooks = []
        copybooks_without_path = []
        
        try:
            # Query copybooks with file paths if metadata is enabled
            if self.config.include_file_metadata:
                self.cursor.execute("""
                    SELECT 
                        fs.artifact_name,
                        inv.file_path
                    FROM flow_scope fs
                    LEFT JOIN inventory inv
                        ON fs.artifact_name = inv.artifact_name
                        AND inv.artifact_type IN ('COPYBOOK', 'FUNCTION', 'DATA')
                    WHERE fs.flow_id = ?
                        AND fs.artifact_type = 'COPYBOOK'
                    ORDER BY fs.artifact_name
                """, (flow_id,))
                
                for row in self.cursor.fetchall():
                    copybook_name = row[0]
                    file_path = row[1]
                    
                    # Build copybook object
                    copybook_obj = {'name': copybook_name}
                    
                    # Add file path if available
                    if file_path is not None:
                        copybook_obj['filePath'] = file_path
                    else:
                        # Track copybooks without file path
                        copybooks_without_path.append(copybook_name)
                    
                    # Enrich copybook with classification, record layout, and BMS map
                    file_path_str = copybook_obj.get('filePath', '')

                    # Classify copybook type
                    if file_path_str and 'cpy-bms' in file_path_str:
                        copybook_obj['copybookType'] = 'BMS'
                    else:
                        copybook_obj['copybookType'] = 'DATA'

                    if self.config.include_record_layouts:
                        # Add record layout inline (legacy behavior)
                        if file_path_str:
                            try:
                                with open(file_path_str, 'r', encoding='utf-8', errors='ignore') as f:
                                    cpy_content = f.read()
                                fields, error_note = self._copybook_analyzer.extract_record_layout(cpy_content)
                                if error_note:
                                    copybook_obj['recordLayout'] = []
                                    copybook_obj['parseError'] = f"Failed to parse record layout: {error_note}"
                                else:
                                    copybook_obj['recordLayout'] = [f.to_dict() for f in fields]
                            except FileNotFoundError:
                                copybook_obj['recordLayout'] = None
                                copybook_obj['parseError'] = f"File not found: {file_path_str}"
                            except Exception as e:
                                copybook_obj['recordLayout'] = []
                                copybook_obj['parseError'] = f"Failed to read file: {e}"
                        else:
                            copybook_obj['recordLayout'] = None
                            if 'filePath' not in copybook_obj:
                                copybook_obj['parseError'] = "File path not found in inventory"

                        # Add BMS map definition inline for BMS copybooks
                        if copybook_obj.get('copybookType') == 'BMS' and file_path_str:
                            bms_path = file_path_str.replace('cpy-bms', 'bms')
                            bms_path = os.path.splitext(bms_path)[0] + '.bms'
                            try:
                                with open(bms_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    bms_content = f.read()
                                definition, bms_error = self._bms_parser.parse(bms_content)
                                if bms_error:
                                    copybook_obj['mapDefinition'] = None
                                    copybook_obj['parseError'] = f"Failed to parse BMS source: {bms_error}"
                                else:
                                    copybook_obj['mapDefinition'] = definition.to_dict()
                            except FileNotFoundError:
                                copybook_obj['mapDefinition'] = None
                            except Exception as e:
                                copybook_obj['mapDefinition'] = None
                                copybook_obj['parseError'] = f"Failed to read BMS source: {e}"
                    else:
                        # Lean mode: collect BMS screens separately for companion file
                        if copybook_obj.get('copybookType') == 'BMS' and file_path_str:
                            if self.config.export_bms_screens and copybook_name not in self._bms_screens:
                                bms_path = file_path_str.replace('cpy-bms', 'bms')
                                bms_path = os.path.splitext(bms_path)[0] + '.bms'
                                try:
                                    with open(bms_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        bms_content = f.read()
                                    definition, bms_error = self._bms_parser.parse(bms_content)
                                    if not bms_error:
                                        self._bms_screens[copybook_name] = {
                                            'name': copybook_name,
                                            'copybookPath': file_path_str,
                                            'bmsSourcePath': bms_path,
                                            'mapDefinition': definition.to_dict_compact(),
                                        }
                                except (FileNotFoundError, Exception):
                                    pass  # Skip silently — no BMS source available

                    copybooks.append(copybook_obj)
                
                # Log copybooks without file path
                if copybooks_without_path:
                    logger.warning(
                        f"Flow {flow_id}: {len(copybooks_without_path)} copybook(s) have no file path: "
                        f"{', '.join(copybooks_without_path[:5])}"
                        f"{'...' if len(copybooks_without_path) > 5 else ''}"
                    )
            else:
                # Simple query without metadata
                self.cursor.execute("""
                    SELECT artifact_name
                    FROM flow_scope
                    WHERE flow_id = ?
                        AND artifact_type = 'COPYBOOK'
                    ORDER BY artifact_name
                """, (flow_id,))
                
                for row in self.cursor.fetchall():
                    copybooks.append({'name': row[0], 'copybookType': 'DATA'})
                
        except sqlite3.OperationalError as e:
            # inventory table doesn't exist or query failed - fall back to simple query
            logger.error(f"Error querying copybooks for flow {flow_id}: {e}")
            logger.info("Falling back to simple query without metadata")
            
            self.cursor.execute("""
                SELECT artifact_name
                FROM flow_scope
                WHERE flow_id = ?
                    AND artifact_type = 'COPYBOOK'
                ORDER BY artifact_name
            """, (flow_id,))
            
            for row in self.cursor.fetchall():
                copybooks.append({'name': row[0], 'copybookType': 'DATA'})
        
        # Query datasets (no metadata)
        self.cursor.execute("""
            SELECT artifact_name
            FROM flow_scope
            WHERE flow_id = ?
                AND artifact_type = 'DATASET'
            ORDER BY artifact_name
        """, (flow_id,))
        
        datasets = [row[0] for row in self.cursor.fetchall()]
        
        # Apply extended scope format if requested (adds is_utility field)
        if self.extended_scope and programs:
            programs = self._format_extended_scope(programs)
        
        # Log summary of scope query
        programs_with_metadata = len(programs) - len(programs_without_metadata)
        copybooks_with_metadata = len(copybooks) - len(copybooks_without_path)
        
        logger.info(
            f"Flow {flow_id} scope: {len(programs)} program(s), "
            f"{len(copybooks)} copybook(s), {len(datasets)} dataset(s)"
        )
        
        if self.config.include_file_metadata and programs:
            logger.info(
                f"Flow {flow_id}: Added file metadata for {programs_with_metadata} of {len(programs)} program(s)"
            )
        
        if self.config.include_file_metadata and copybooks:
            logger.info(
                f"Flow {flow_id}: Added file metadata for {copybooks_with_metadata} of {len(copybooks)} copybook(s)"
            )
        
        return {
            'programs': programs,
            'copybooks': copybooks,
            'datasets': datasets
        }
    
    def _format_extended_scope(self, programs: List) -> List[Dict]:
        """
        Format program list with utility metadata for extended scope.
        
        This method handles both string and dict program formats for
        backward compatibility. It adds is_utility metadata when
        extended_scope=True.
        
        Args:
            programs: List of program names (strings) or program objects (dicts)
            
        Returns:
            List of program objects with utility metadata
        """
        from .utility_detector import UtilityDetector
        
        # Create utility detector
        detector = UtilityDetector(self.db)
        
        # Get utility programs
        utilities = detector.get_utility_programs()
        
        # Format programs with utility metadata
        extended_programs = []
        for program in programs:
            # Handle both string and dict formats
            if isinstance(program, str):
                program_name = program
                program_obj = {'name': program_name}
            else:
                program_name = program['name']
                program_obj = program.copy()  # Preserve existing metadata
            
            # Add utility metadata
            if program_name in utilities:
                # Get shared flows for this utility
                shared_flows = detector.get_shared_flows(program_name)
                
                program_obj.update({
                    'is_utility': True,
                    'shared_by_flows': shared_flows,
                    'call_count': utilities[program_name]['call_count'],
                    'classification': utilities[program_name]['classification']
                })
            else:
                program_obj['is_utility'] = False
            
            extended_programs.append(program_obj)
        
        return extended_programs
    
    def _query_interfaces(self, flow_id: str) -> Dict[str, List[Dict]]:
        """
        Query flow interfaces (inbound and outbound).
        
        Args:
            flow_id: Flow ID to query
            
        Returns:
            Dictionary with keys 'inbound' and 'outbound'
            Each value is a list of interface objects
        """
        self.cursor.execute("""
            SELECT 
                direction,
                interface_type,
                source,
                target,
                external,
                metadata_json
            FROM flow_interfaces
            WHERE flow_id = ?
            ORDER BY direction, interface_type, source, target
        """, (flow_id,))
        
        # Group interfaces by direction
        interfaces = {
            'inbound': [],
            'outbound': []
        }
        
        for row in self.cursor.fetchall():
            direction, iface_type, source, target, external, metadata_json = row
            
            # Parse metadata
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            
            # Build interface object
            interface = {
                'type': iface_type,
                'source': source,
                'target': target
            }
            
            if external:
                interface['external'] = True
            
            if metadata:
                interface['metadata'] = metadata
            
            # Add to appropriate list
            if direction == 'INBOUND':
                interfaces['inbound'].append(interface)
            else:
                interfaces['outbound'].append(interface)
        
        return interfaces
    
    def _query_data_operations(self, flow_id: str) -> Dict[str, List[Dict]]:
        """
        Query flow data operations (databases and datasets).
        
        Args:
            flow_id: Flow ID to query
            
        Returns:
            Dictionary with keys 'databases' and 'datasets'
            Each value is a list of operation objects
        """
        self.cursor.execute("""
            SELECT 
                operation_category,
                operation_type,
                db_type,
                target,
                program,
                mode
            FROM flow_data_operations
            WHERE flow_id = ?
            ORDER BY operation_category, target, program
        """, (flow_id,))
        
        # Group operations by category
        data_operations = {
            'databases': [],
            'datasets': []
        }
        
        # Track datasets to consolidate programs
        datasets_dict = {}
        
        for row in self.cursor.fetchall():
            category, op_type, db_type, target, program, mode = row
            
            if category == 'DATABASE':
                # Add database operation
                operation = {
                    'type': db_type if db_type else 'UNKNOWN',
                    'operation': op_type,
                    'target': target,
                    'program': program
                }
                data_operations['databases'].append(operation)
            
            elif category == 'DATASET':
                # Consolidate dataset operations by target
                if target not in datasets_dict:
                    datasets_dict[target] = {
                        'name': target,
                        'operation': op_type if op_type else 'UNKNOWN',
                        'mode': mode if mode else 'UNKNOWN',
                        'programs': []
                    }
                
                # Add program if not already in list
                if program not in datasets_dict[target]['programs']:
                    datasets_dict[target]['programs'].append(program)
        
        # Convert datasets dict to list
        data_operations['datasets'] = list(datasets_dict.values())
        
        return data_operations
    
    def _query_invoking_jobs(self, entry_program: str) -> List[str]:
        """
        Query jobs that invoke a flow's entry point program.
        
        This method queries the inventory_jcl table to find all jobs
        that have steps invoking the specified entry point program.
        
        Args:
            entry_program: Entry point program name
            
        Returns:
            Sorted list of job names that invoke this program
        """
        # Check if inventory_jcl table exists
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='inventory_jcl'
            """)
            if not self.cursor.fetchone():
                # Table doesn't exist, return empty list
                return []
        except Exception:
            # Error checking for table, return empty list
            return []
        
        # Query jobs that have steps invoking this program
        # The steps column contains JSON array of step objects
        try:
            self.cursor.execute("""
                SELECT DISTINCT name
                FROM inventory_jcl
                WHERE steps LIKE ?
                ORDER BY name
            """, (f'%{entry_program}%',))
        except Exception:
            # Error querying, return empty list
            return []
        
        job_names = []
        for row in self.cursor.fetchall():
            job_name = row[0]
            
            # Verify the program is actually in the steps (not just in a comment)
            # by parsing the steps JSON
            try:
                self.cursor.execute("""
                    SELECT steps
                    FROM inventory_jcl
                    WHERE name = ?
                """, (job_name,))
                
                steps_json = self.cursor.fetchone()
                if steps_json and steps_json[0]:
                    try:
                        steps = json.loads(steps_json[0])
                        # Check if any step invokes this program
                        for step in steps:
                            if isinstance(step, dict) and step.get('program') == entry_program:
                                job_names.append(job_name)
                                break
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse steps JSON for job {job_name}")
            except Exception:
                # Error querying specific job, skip it
                continue
        
        return sorted(job_names)
    
    def _query_dependencies(self, flow_id: str) -> Dict[str, List[Dict]]:
            """
            Query flow dependencies (required and dependent flows).

            Args:
                flow_id: Flow ID to query

            Returns:
                Dictionary with keys 'requiredFlows' and 'dependentFlows'
                Each value is a list of dictionaries containing:
                - flowId: The flow identifier
                - entryProgram: The entry program name for the flow
                - filePath: File path to the entry program (if configuration enabled and available)
            """
            # Query required flows (flows this flow depends on)
            self.cursor.execute("""
                SELECT DISTINCT fd.depends_on_flow_id, mf.entry_program
                FROM flow_dependencies fd
                JOIN migration_flows mf ON fd.depends_on_flow_id = mf.flow_id
                WHERE fd.flow_id = ?
                  AND fd.dependency_type = 'REQUIRED'
                ORDER BY fd.depends_on_flow_id
            """, (flow_id,))

            required_flows = []
            for row in self.cursor.fetchall():
                flow_id_dep, entry_program = row
                dependency_obj = {
                    'flowId': flow_id_dep,
                    'entryProgram': entry_program
                }

                # Add file metadata if configuration enabled
                if self.config.include_file_metadata:
                    metadata = self._enrich_with_file_metadata(entry_program)
                    if metadata and 'filePath' in metadata:
                        dependency_obj['filePath'] = metadata['filePath']

                required_flows.append(dependency_obj)

            # Query dependent flows (flows that depend on this flow)
            self.cursor.execute("""
                SELECT DISTINCT fd.flow_id, mf.entry_program
                FROM flow_dependencies fd
                JOIN migration_flows mf ON fd.flow_id = mf.flow_id
                WHERE fd.depends_on_flow_id = ?
                  AND fd.dependency_type = 'REQUIRED'
                ORDER BY fd.flow_id
            """, (flow_id,))

            dependent_flows = []
            for row in self.cursor.fetchall():
                flow_id_dep, entry_program = row
                dependency_obj = {
                    'flowId': flow_id_dep,
                    'entryProgram': entry_program
                }

                # Add file metadata if configuration enabled
                if self.config.include_file_metadata:
                    metadata = self._enrich_with_file_metadata(entry_program)
                    if metadata and 'filePath' in metadata:
                        dependency_obj['filePath'] = metadata['filePath']

                dependent_flows.append(dependency_obj)

            return {
                'requiredFlows': required_flows,
                'dependentFlows': dependent_flows
            }
    
    def _format_json(self, flows: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Format flows into final JSON structure.
        
        This method wraps the flows list in the standard JSON structure
        and ensures all fields are properly formatted.
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            Dictionary with 'flows' key containing the flows list
        """
        return {
            'flows': flows
        }
    
    def get_flow_count(self) -> int:
        """
        Get total number of flows in database.
        
        Returns:
            Number of flows
        """
        self.cursor.execute("SELECT COUNT(*) FROM migration_flows")
        return self.cursor.fetchone()[0]
    
    def get_flow_ids(self) -> List[str]:
        """
        Get list of all flow IDs in database.
        
        Returns:
            Sorted list of flow IDs
        """
        self.cursor.execute("SELECT flow_id FROM migration_flows ORDER BY flow_id")
        return [row[0] for row in self.cursor.fetchall()]
    
    def flow_exists(self, flow_id: str) -> bool:
        """
        Check if a flow exists in database.
        
        Args:
            flow_id: Flow ID to check
            
        Returns:
            True if flow exists, False otherwise
        """
        self.cursor.execute("""
            SELECT COUNT(*) FROM migration_flows WHERE flow_id = ?
        """, (flow_id,))
        return self.cursor.fetchone()[0] > 0
    
    def filter_by_flow_ids(self, flow_ids: List[str]) -> List[str]:
        """
        Filter flows by specific flow IDs.
        
        This method validates that the requested flow IDs exist in the database
        and returns only the valid ones.
        
        Args:
            flow_ids: List of flow IDs to filter
            
        Returns:
            List of valid flow IDs that exist in database
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> valid_ids = exporter.filter_by_flow_ids(['FLOW_PAYROLL1', 'FLOW_INVALID'])
            >>> print(valid_ids)  # ['FLOW_PAYROLL1']
        """
        if not flow_ids:
            return []
        
        # Query to check which flow IDs exist
        placeholders = ','.join('?' * len(flow_ids))
        query = f"""
            SELECT flow_id
            FROM migration_flows
            WHERE flow_id IN ({placeholders})
            ORDER BY flow_id
        """
        
        self.cursor.execute(query, flow_ids)
        return [row[0] for row in self.cursor.fetchall()]
    
    def filter_by_complexity(self, min_complexity: str) -> List[str]:
        """
        Filter flows by minimum complexity tier.
        
        This method returns all flows with complexity tier >= min_complexity.
        Tier ordering: LOW < MEDIUM < HIGH < VERY_HIGH
        
        Args:
            min_complexity: Minimum complexity tier ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')
            
        Returns:
            List of flow IDs matching the complexity filter
            
        Raises:
            ValueError: If min_complexity is not a valid tier
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> high_complexity_flows = exporter.filter_by_complexity('HIGH')
            >>> print(f"Found {len(high_complexity_flows)} high complexity flows")
        """
        # Map complexity tier to numeric value for comparison
        tier_order = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'VERY_HIGH': 4}
        
        min_complexity_upper = min_complexity.upper()
        if min_complexity_upper not in tier_order:
            raise ValueError(
                f"Invalid complexity tier: {min_complexity}. "
                f"Must be one of: {', '.join(tier_order.keys())}"
            )
        
        min_tier_value = tier_order[min_complexity_upper]
        
        # Build IN clause for tiers >= min_complexity
        valid_tiers = [tier for tier, value in tier_order.items() if value >= min_tier_value]
        placeholders = ','.join('?' * len(valid_tiers))
        
        query = f"""
            SELECT flow_id
            FROM migration_flows
            WHERE complexity_tier IN ({placeholders})
            ORDER BY flow_id
        """
        
        self.cursor.execute(query, valid_tiers)
        return [row[0] for row in self.cursor.fetchall()]
    
    def filter_by_business_domain(self, business_domain: str) -> List[str]:
        """
        Filter flows by business domain.
        
        This method returns all flows belonging to the specified business domain.
        
        Args:
            business_domain: Business domain to filter by (e.g., 'Finance', 'HR')
            
        Returns:
            List of flow IDs in the specified business domain
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> finance_flows = exporter.filter_by_business_domain('Finance')
            >>> print(f"Found {len(finance_flows)} finance flows")
        """
        query = """
            SELECT flow_id
            FROM migration_flows
            WHERE business_domain = ?
            ORDER BY flow_id
        """
        
        self.cursor.execute(query, (business_domain,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def filter_by_entry_type(self, entry_type: str) -> List[str]:
        """
        Filter flows by entry point type.
        
        This method returns all flows that have the specified entry point type.
        A flow can have multiple entry types, so this returns flows where the
        specified type is one of the entry types.
        
        Args:
            entry_type: Entry point type to filter by 
                       ('JCL', 'CICS_TRANSACTION', 'CICS_PROGRAM', 'SCREEN', 
                        'BATCH', 'EXTERNAL_CALL')
            
        Returns:
            List of flow IDs with the specified entry type
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> jcl_flows = exporter.filter_by_entry_type('JCL')
            >>> print(f"Found {len(jcl_flows)} JCL-invoked flows")
        """
        query = """
            SELECT DISTINCT flow_id
            FROM flow_entry_types
            WHERE entry_type = ?
            ORDER BY flow_id
        """
        
        self.cursor.execute(query, (entry_type,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def apply_combined_filters(
        self,
        flow_ids: Optional[List[str]] = None,
        min_complexity: Optional[str] = None,
        business_domain: Optional[str] = None,
        entry_type: Optional[str] = None
    ) -> List[str]:
        """
        Apply multiple filters and return intersection of results.
        
        This method applies all specified filters and returns only flows
        that match ALL criteria (AND logic).
        
        Args:
            flow_ids: Optional list of specific flow IDs to filter
            min_complexity: Minimum complexity tier
            business_domain: Business domain to filter by
            entry_type: Entry point type to filter by
            
        Returns:
            List of flow IDs matching all specified filters
            
        Example:
            >>> exporter = MigrationFlowExporter(db)
            >>> filtered = exporter.apply_combined_filters(
            ...     min_complexity='HIGH',
            ...     business_domain='Finance',
            ...     entry_type='JCL'
            ... )
            >>> print(f"Found {len(filtered)} high-complexity finance JCL flows")
        """
        # Start with all flows or specified flow IDs
        if flow_ids:
            result_set = set(self.filter_by_flow_ids(flow_ids))
        else:
            result_set = set(self.get_flow_ids())
        
        # Apply complexity filter
        if min_complexity:
            complexity_flows = set(self.filter_by_complexity(min_complexity))
            result_set = result_set.intersection(complexity_flows)
        
        # Apply business domain filter
        if business_domain:
            domain_flows = set(self.filter_by_business_domain(business_domain))
            result_set = result_set.intersection(domain_flows)
        
        # Apply entry type filter
        if entry_type:
            entry_type_flows = set(self.filter_by_entry_type(entry_type))
            result_set = result_set.intersection(entry_type_flows)
        
        # Return sorted list
        return sorted(list(result_set))

    def _sort_flows(self, flows: List[Dict], sort_order: str) -> List[Dict]:
        """
        Sort flows according to migration strategy.
        
        Args:
            flows: List of flow dictionaries
            sort_order: Sorting strategy
                       - 'complexity-asc': Simplest flows first (low risk)
                       - 'complexity-desc': Most complex flows first
                       - 'independence': Flows with fewest shared programs first
                       - 'dependencies': Flows with most dependencies first
                       - 'name': Alphabetical by flow name
                       
        Returns:
            Sorted list of flows
        """
        logger.info(f"Sorting flows by: {sort_order}")
        
        if sort_order == 'complexity-asc':
            # Sort by complexity score ascending (simplest first)
            # Tier order: LOW < MEDIUM < HIGH < VERY_HIGH < UNKNOWN
            tier_order = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'VERY_HIGH': 4, 'UNKNOWN': 5}
            flows.sort(key=lambda f: (
                tier_order.get(f.get('complexity', {}).get('tier', 'UNKNOWN'), 5),
                f.get('complexity', {}).get('compositeScore', 0)
            ))
            logger.info("Sorted by complexity ascending (simplest first)")
            
        elif sort_order == 'complexity-desc':
            # Sort by complexity score descending (most complex first)
            tier_order = {'VERY_HIGH': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4, 'UNKNOWN': 5}
            flows.sort(key=lambda f: (
                tier_order.get(f.get('complexity', {}).get('tier', 'UNKNOWN'), 5),
                -f.get('complexity', {}).get('compositeScore', 0)
            ))
            logger.info("Sorted by complexity descending (most complex first)")
            
        elif sort_order == 'independence':
            # Sort by number of shared programs (fewest first)
            # Count utility programs in scope
            def count_shared_programs(flow):
                programs = flow.get('scope', {}).get('programs', [])
                if not programs:
                    return 0
                
                # If extended scope, count utilities
                if isinstance(programs[0], dict):
                    return sum(1 for p in programs if p.get('is_utility', False))
                
                # Otherwise, query database for utilities
                # For now, use program count as proxy
                return len(programs)
            
            flows.sort(key=lambda f: (
                count_shared_programs(f),
                f.get('complexity', {}).get('compositeScore', 0)
            ))
            logger.info("Sorted by independence (fewest shared programs first)")
            
        elif sort_order == 'dependencies':
            # Sort by number of dependencies (most first - foundational flows)
            flows.sort(key=lambda f: (
                -len(f.get('dependencies', {}).get('requiredFlows', [])),
                -len(f.get('scope', {}).get('programs', []))
            ))
            logger.info("Sorted by dependencies (most dependencies first)")
            
        elif sort_order == 'name':
            # Sort alphabetically by flow name
            flows.sort(key=lambda f: f.get('name', '').lower())
            logger.info("Sorted alphabetically by name")
            
        else:
            logger.warning(f"Unknown sort order: {sort_order}. Using database order.")
        
        return flows
