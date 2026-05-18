"""
JCL Job Exporter

This module provides functionality for exporting JCL jobs from database
to JSON format. It queries job data from inventory tables and formats it
according to the job export schema with categorization, dependencies, and
cross-references to program flows.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Tuple

from .exceptions import ExportError, MissingDataError

# Configure logging
logger = logging.getLogger(__name__)

# Known utility programs on mainframe systems
UTILITY_PROGRAMS = {
    # IBM Utilities
    'IEFBR14',   # Dummy program (allocate/delete datasets)
    'IDCAMS',    # Access Method Services (VSAM operations)
    'IEBGENER',  # Sequential dataset copy
    'IEBCOPY',   # Partitioned dataset copy
    'IEBPTPCH',  # Print/punch utility
    'IEBUPDTE',  # Update utility
    'IEBEDIT',   # Edit utility
    'IEBCOMPR',  # Compare utility
    'IEBISAM',   # ISAM utility
    'IEBDG',     # Test data generator
    'IEBIMAGE',  # Image utility
    'IEHINITT',  # Tape initialization
    'IEHLIST',   # List utility
    'IEHMOVE',   # Move/copy utility
    'IEHPROGM',  # Program utility
    'IEHDASDR',  # DASD dump/restore
    'IEBUPDAT',  # Update utility (alternate spelling)
    
    # Sort utilities
    'SORT',      # Generic sort
    'SYNCSORT',  # Syncsort product
    'DFSORT',    # IBM DFSORT
    'ICETOOL',   # DFSORT tool
    'ICEMAN',    # DFSORT program
    
    # Database utilities
    'DSNTEP2',   # DB2 command processor
    'DSNTEP4',   # DB2 command processor (alternate)
    'DSNTIAD',   # DB2 interactive SQL
    'DSNTIAUL',  # DB2 unload utility
    'DSNUPROC',  # DB2 stored procedure
    
    # File transfer utilities
    'FTP',       # File Transfer Protocol
    'FTPBATCH',  # Batch FTP
    'NDM',       # Connect:Direct (NDM)
    'DMCLI',     # Connect:Direct CLI
    
    # Tape utilities
    'IEBGENER',  # Also used for tape operations
    'IEHINITT',  # Tape initialization
    
    # Other common utilities
    'IKJEFT01',  # TSO command processor
    'IKJEFT1A',  # TSO command processor (alternate)
    'IKJEFT1B',  # TSO command processor (alternate)
    'IRXJCL',    # REXX interpreter
    'ADRDSSU',   # DFSMSdss (backup/restore)
    'ADRDSSU',   # Dataset dump/restore
    'REPRO',     # IDCAMS REPRO command
    'LISTCAT',   # IDCAMS LISTCAT command
}


class JobExporter:
    """
    Exports JCL jobs from database to JSON format.
    
    This class provides methods to:
    1. Query job data from database tables
    2. Categorize jobs (APPLICATION vs INFRASTRUCTURE)
    3. Extract job steps and dependencies
    4. Link jobs to program flows
    5. Export jobs with multiple sorting strategies
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the JobExporter with database connection.
        
        Args:
            db_path: Path to SQLite database file
            
        Raises:
            ExportError: If database file doesn't exist or connection fails
        """
        import os
        
        # Validate database file exists before attempting connection
        if not os.path.exists(db_path):
            raise ExportError(
                f"Database file not found: {db_path}",
                operation='connect'
            )
        
        # Validate it's a file (not a directory)
        if not os.path.isfile(db_path):
            raise ExportError(
                f"Database path is not a file: {db_path}",
                operation='connect'
            )
        
        try:
            self.db_path = db_path
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
            logger.info(f"Connected to database: {db_path}")
        except sqlite3.Error as e:
            raise ExportError(
                f"Failed to connect to database: {db_path}",
                operation='connect',
                cause=e
            )
    
    def _query_jobs(self) -> List[Dict[str, Any]]:
        """
        Query all JCL jobs from inventory_jcl table.
        
        Returns:
            List of job dictionaries with basic metadata
            Returns empty list if no jobs found
            
        Raises:
            ExportError: If database query fails
            
        Note:
            If no jobs are found in the database, this method returns an empty
            list rather than raising an error. The caller should handle the
            empty database case appropriately (e.g., display a warning).
        """
        try:
            logger.info("Querying all jobs from inventory_jcl table")
            
            self.cursor.execute("""
                SELECT 
                    member_name,
                    library_name,
                    last_modified,
                    size_lines
                FROM inventory_jcl
                ORDER BY member_name
            """)
            
            rows = self.cursor.fetchall()
            
            jobs = []
            for row in rows:
                member_name, library_name, last_modified, size_lines = row
                jobs.append({
                    'jobName': member_name,
                    'library': library_name,
                    'lastModified': last_modified,
                    'sizeLines': size_lines
                })
            
            if not jobs:
                logger.warning("No jobs found in database")
            else:
                logger.info(f"Found {len(jobs)} jobs in database")
            
            return jobs
            
        except sqlite3.Error as e:
            raise ExportError(
                "Failed to query jobs from database",
                operation='query',
                cause=e
            )
    
    def _query_job_steps(self, job_name: str) -> List[Dict[str, Any]]:
        """
        Query all steps for a specific job.
        
        This method extracts step information from the database. In the current
        schema, step information is not stored separately, so this method
        queries related program dependencies to infer steps.
        
        Args:
            job_name: Name of the job to query steps for
            
        Returns:
            List of step dictionaries with step metadata including:
                - stepName: Sequential step identifier (STEP01, STEP02, etc.)
                - program: Program or utility name invoked by the step
                - type: Program type (CUSTOM or UTILITY) - set by _assign_step_types
                - purpose: Human-readable description of step purpose
                - flowEntry: Whether this step is a flow entry point - set by _assign_step_types
            
        Raises:
            ExportError: If database query fails
            
        Note:
            The current database schema doesn't have a dedicated steps table.
            This implementation queries artifact_dependencies to find programs
            invoked by the JCL job. Step order is maintained by the query order.
            Step types and flow entry flags are assigned by _assign_step_types method.
        """
        try:
            logger.debug(f"Querying steps for job: {job_name}")
            
            # Query programs invoked by this JCL job
            # Note: We use target_artifact_name for ordering to maintain consistency
            self.cursor.execute("""
                SELECT DISTINCT
                    target_artifact_name,
                    dependency_type
                FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND source_artifact_type = 'JCL'
                  AND target_artifact_type IN ('COBOL', 'PLI', 'UTILITY', 'PROGRAM')
                ORDER BY target_artifact_name
            """, (job_name,))
            
            rows = self.cursor.fetchall()
            
            steps = []
            for idx, row in enumerate(rows, start=1):
                program_name, dependency_type = row
                
                # Generate purpose based on program type
                purpose = self._generate_step_purpose(program_name)
                
                # Create step entry with all required fields
                # Note: Step names are inferred since they're not in the database
                steps.append({
                    'stepName': f'STEP{idx:02d}',  # Sequential step identifier
                    'program': program_name,
                    'type': 'UNKNOWN',  # Will be set by _assign_step_types
                    'purpose': purpose,
                    'flowEntry': False  # Will be set by _assign_step_types
                })
            
            logger.debug(f"Found {len(steps)} steps for job {job_name}")
            return steps
            
        except sqlite3.Error as e:
            raise ExportError(
                f"Failed to query steps for job {job_name}",
                operation='query',
                cause=e
            )
    
    def _generate_step_purpose(self, program_name: str) -> str:
        """
        Generate a human-readable purpose description for a step.
        
        This method creates descriptive purpose text based on the program type.
        For utility programs, it provides specific descriptions based on the
        utility's function. For custom programs, it provides a generic execution
        description.
        
        Args:
            program_name: Name of the program or utility
            
        Returns:
            Human-readable purpose description
            
        Examples:
            >>> exporter._generate_step_purpose('IEFBR14')
            'Allocate or delete datasets'
            
            >>> exporter._generate_step_purpose('IDCAMS')
            'VSAM dataset operations'
            
            >>> exporter._generate_step_purpose('CUSTPROG')
            'Execute CUSTPROG'
        """
        if not program_name:
            return 'Execute program'
        
        program_upper = program_name.upper().strip()
        
        # Provide specific descriptions for known utilities
        utility_purposes = {
            'IEFBR14': 'Allocate or delete datasets',
            'IDCAMS': 'VSAM dataset operations',
            'IEBGENER': 'Copy sequential dataset',
            'IEBCOPY': 'Copy partitioned dataset',
            'IEBPTPCH': 'Print or punch dataset',
            'IEBUPDTE': 'Update dataset',
            'IEBEDIT': 'Edit dataset',
            'IEBCOMPR': 'Compare datasets',
            'SORT': 'Sort dataset',
            'SYNCSORT': 'Sort dataset',
            'DFSORT': 'Sort dataset',
            'ICETOOL': 'Sort and data manipulation',
            'ICEMAN': 'Sort dataset',
            'DSNTEP2': 'Execute DB2 commands',
            'DSNTEP4': 'Execute DB2 commands',
            'DSNTIAD': 'Interactive DB2 SQL',
            'DSNTIAUL': 'Unload DB2 data',
            'FTP': 'File transfer',
            'FTPBATCH': 'Batch file transfer',
            'NDM': 'Connect:Direct file transfer',
            'IKJEFT01': 'Execute TSO commands',
            'IKJEFT1A': 'Execute TSO commands',
            'IKJEFT1B': 'Execute TSO commands',
            'IRXJCL': 'Execute REXX script',
            'ADRDSSU': 'Backup or restore datasets',
        }
        
        # Return specific purpose if known utility
        if program_upper in utility_purposes:
            return utility_purposes[program_upper]
        
        # For custom programs, return generic execution description
        return f'Execute {program_name}'
    
    def _is_custom_program(self, program_name: str) -> bool:
        """
        Check if a program is a custom program by querying the inventory table.
        
        This method queries the inventory table to determine if a program exists
        as a custom program (COBOL, PL/I, etc.) rather than a utility.
        
        Args:
            program_name: Name of the program to check
            
        Returns:
            True if the program is a custom program in inventory, False otherwise
            
        Note:
            This method queries the database, so it should be used judiciously.
            Programs not found in inventory are assumed to be utilities if they
            match known utility names, otherwise they're treated as custom.
        """
        if not program_name:
            return False
        
        try:
            # Query inventory table for this program
            self.cursor.execute("""
                SELECT artifact_type, is_entry_point
                FROM inventory
                WHERE artifact_name = ?
            """, (program_name,))
            
            row = self.cursor.fetchone()
            
            if row:
                program_type, _ = row
                # Custom programs are COBOL, PLI, NATURAL, REXX, etc.
                # Utilities have type 'UTILITY'
                return program_type != 'UTILITY'
            
            # If not in inventory, fall back to utility check
            # If it's a known utility, it's not custom
            # If it's not a known utility, assume it's custom
            return not self._is_utility_program(program_name)
            
        except sqlite3.Error as e:
            logger.warning(f"Error querying inventory for program {program_name}: {e}")
            # Fall back to utility check on error
            return not self._is_utility_program(program_name)
    
    def _is_flow_entry_point(self, program_name: str) -> bool:
        """
        Check if a program is a flow entry point.
        
        This method queries the inventory table to determine if a program
        is marked as a flow entry point (is_entry_point=true).
        
        Args:
            program_name: Name of the program to check
            
        Returns:
            True if the program is a flow entry point, False otherwise
        """
        if not program_name:
            return False
        
        try:
            # Query inventory table for entry point flag
            self.cursor.execute("""
                SELECT is_entry_point
                FROM inventory
                WHERE artifact_name = ?
            """, (program_name,))
            
            row = self.cursor.fetchone()
            
            if row:
                is_entry_point = row[0]
                # Handle different boolean representations
                return bool(is_entry_point) if is_entry_point is not None else False
            
            return False
            
        except sqlite3.Error as e:
            logger.warning(f"Error querying entry point status for program {program_name}: {e}")
            return False
    
    def _assign_step_types(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign types and flow entry flags to steps.
        
        This method processes a list of steps and assigns:
        1. Step type (CUSTOM or UTILITY) based on program type
        2. Flow entry flag based on whether the program is a flow entry point
        
        The method queries the inventory table to determine program types and
        entry point status. Steps are modified in place.
        
        Args:
            steps: List of step dictionaries to process
            
        Returns:
            The same list of steps with type and flowEntry fields updated
            
        Note:
            This method modifies the steps list in place and also returns it
            for convenience. Each step's 'type' field is set to either 'CUSTOM'
            or 'UTILITY', and the 'flowEntry' field is set to True or False.
        """
        for step in steps:
            program_name = step.get('program', '')
            
            # Determine step type
            if self._is_utility_program(program_name):
                step['type'] = 'UTILITY'
            elif self._is_custom_program(program_name):
                step['type'] = 'CUSTOM'
            else:
                # Default to CUSTOM if we can't determine
                # (better to assume custom than utility)
                step['type'] = 'CUSTOM'
            
            # Determine if this is a flow entry point
            step['flowEntry'] = self._is_flow_entry_point(program_name)
            
            logger.debug(
                f"Assigned type={step['type']}, flowEntry={step['flowEntry']} "
                f"to step {step['stepName']} (program={program_name})"
            )
        
        return steps
    
    def _is_utility_program(self, program_name: str) -> bool:
        """
        Check if a program is a known utility program.
        
        This method checks if the given program name matches any known
        mainframe utility programs (IEFBR14, IDCAMS, SORT, etc.).
        
        Args:
            program_name: Name of the program to check
            
        Returns:
            True if the program is a known utility, False otherwise
            
        Note:
            The check is case-insensitive and uses a predefined set of
            known utility program names defined in UTILITY_PROGRAMS.
        """
        if not program_name:
            return False
        
        # Convert to uppercase for case-insensitive comparison
        program_upper = program_name.upper().strip()
        
        return program_upper in UTILITY_PROGRAMS
    
    def _categorize_job(self, steps: List[Dict[str, Any]]) -> Tuple[str, bool]:
        """
        Categorize job as APPLICATION or INFRASTRUCTURE.
        
        A job is categorized as APPLICATION if it invokes at least one custom
        program (non-utility). Otherwise, it's categorized as INFRASTRUCTURE.
        Jobs with no steps are categorized as INFRASTRUCTURE.
        
        Args:
            steps: List of step dictionaries containing program information
            
        Returns:
            Tuple of (job_type, has_custom_code) where:
                - job_type is "APPLICATION" or "INFRASTRUCTURE"
                - has_custom_code is True if job invokes custom programs
                
        Examples:
            >>> exporter._categorize_job([{'program': 'IEFBR14'}])
            ('INFRASTRUCTURE', False)
            
            >>> exporter._categorize_job([{'program': 'CUSTPROG'}])
            ('APPLICATION', True)
            
            >>> exporter._categorize_job([])
            ('INFRASTRUCTURE', False)
        """
        # Handle edge case: job with no steps
        if not steps:
            logger.debug("Job has no steps, categorizing as INFRASTRUCTURE")
            return ('INFRASTRUCTURE', False)
        
        # Check if any step invokes a custom program (non-utility)
        has_custom_code = False
        
        for step in steps:
            program_name = step.get('program', '')
            
            # If program is not a utility, it's a custom program
            if not self._is_utility_program(program_name):
                has_custom_code = True
                logger.debug(f"Found custom program: {program_name}")
                break
        
        # Determine job type based on whether it has custom code
        if has_custom_code:
            job_type = 'APPLICATION'
            logger.debug("Job categorized as APPLICATION (has custom code)")
        else:
            job_type = 'INFRASTRUCTURE'
            logger.debug("Job categorized as INFRASTRUCTURE (utilities only)")
        
        return (job_type, has_custom_code)
    
    def _link_to_flow(self, steps: List[Dict[str, Any]]) -> Optional[str]:
        """
        Link job to flow if it invokes a flow entry point.
        
        This method checks if any step in the job invokes a program that is
        marked as a flow entry point. If multiple steps invoke entry points,
        the first one is used. The method also validates that the flow exists
        in the database.
        
        Args:
            steps: List of step dictionaries containing program information
            
        Returns:
            Flow name in format "FLOW_{program_name}" if a flow entry point
            is found and the flow exists, None otherwise
            
        Examples:
            >>> exporter._link_to_flow([{'program': 'MAINPROG', 'flowEntry': True}])
            'FLOW_MAINPROG'
            
            >>> exporter._link_to_flow([{'program': 'IEFBR14', 'flowEntry': False}])
            None
            
        Note:
            This method assumes that steps have already been processed by
            _assign_step_types() which sets the flowEntry flag.
        """
        if not steps:
            logger.debug("Job has no steps, no flow to link")
            return None
        
        # Find the first step that is a flow entry point
        entry_point_program = None
        
        for step in steps:
            if step.get('flowEntry', False):
                entry_point_program = step.get('program')
                logger.debug(f"Found flow entry point: {entry_point_program}")
                break
        
        # If no entry point found, return None
        if not entry_point_program:
            logger.debug("No flow entry point found in job steps")
            return None
        
        # Construct flow name using FLOW_{program} convention
        flow_name = f"FLOW_{entry_point_program}"
        
        # Validate that the flow exists in the database
        if self._validate_flow_exists(flow_name):
            logger.debug(f"Linked job to flow: {flow_name}")
            return flow_name
        else:
            logger.warning(
                f"Flow {flow_name} not found in database for entry point {entry_point_program}"
            )
            return None
    
    def _validate_flow_exists(self, flow_name: str) -> bool:
        """
        Validate that a flow exists in the database.
        
        This method checks if a flow with the given name exists in the
        migration_flows table. This validation ensures that job-to-flow
        links reference valid flows.
        
        Args:
            flow_name: Name of the flow to validate (format: FLOW_{program})
            
        Returns:
            True if the flow exists in the database, False otherwise
            
        Note:
            This method queries the migration_flows table. If the table
            doesn't exist or the query fails, it returns False and logs
            a warning.
        """
        if not flow_name:
            return False
        
        try:
            # Check if migration_flows table exists
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='migration_flows'
            """)
            
            if not self.cursor.fetchone():
                logger.debug("migration_flows table does not exist")
                return False
            
            # Query for the flow
            self.cursor.execute("""
                SELECT flow_id
                FROM migration_flows
                WHERE flow_id = ?
            """, (flow_name,))
            
            row = self.cursor.fetchone()
            exists = row is not None
            
            if exists:
                logger.debug(f"Flow {flow_name} exists in database")
            else:
                logger.debug(f"Flow {flow_name} not found in database")
            
            return exists
            
        except sqlite3.Error as e:
            logger.warning(f"Error validating flow existence for {flow_name}: {e}")
            return False
    
    def _query_explicit_dependencies(self, job_name: str) -> Dict[str, List[str]]:
        """
        Query explicit job-to-job dependencies from the database.
        
        This method queries the artifact_dependencies table for explicit
        dependencies where one JCL job directly references another JCL job.
        These are typically defined through JCL EXEC statements or job
        scheduling dependencies.
        
        Args:
            job_name: Name of the job to query dependencies for
            
        Returns:
            Dictionary with two keys:
                - 'mustRunAfter': List of job names that must run before this job
                - 'mustRunBefore': List of job names that must run after this job
            
        Raises:
            ExportError: If database query fails
            
        Note:
            In the current database schema, explicit JCL-to-JCL dependencies
            are stored in the artifact_dependencies table with:
            - source_artifact_type = 'JCL'
            - target_artifact_type = 'JCL'
            - dependency_type indicating the relationship type
        """
        try:
            logger.debug(f"Querying explicit dependencies for job: {job_name}")
            
            # Query jobs that this job depends on (must run after)
            # These are jobs that this job references as targets
            self.cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND source_artifact_type = 'JCL'
                  AND target_artifact_type = 'JCL'
                ORDER BY target_artifact_name
            """, (job_name,))
            
            must_run_after = [row[0] for row in self.cursor.fetchall()]
            
            # Query jobs that depend on this job (must run before)
            # These are jobs that reference this job as a target
            self.cursor.execute("""
                SELECT DISTINCT source_artifact_name
                FROM artifact_dependencies
                WHERE target_artifact_name = ?
                  AND source_artifact_type = 'JCL'
                  AND target_artifact_type = 'JCL'
                ORDER BY source_artifact_name
            """, (job_name,))
            
            must_run_before = [row[0] for row in self.cursor.fetchall()]
            
            logger.debug(
                f"Found {len(must_run_after)} mustRunAfter and "
                f"{len(must_run_before)} mustRunBefore dependencies for job {job_name}"
            )
            
            return {
                'mustRunAfter': must_run_after,
                'mustRunBefore': must_run_before
            }
            
        except sqlite3.Error as e:
            raise ExportError(
                f"Failed to query explicit dependencies for job {job_name}",
                operation='query',
                cause=e
            )
    
    def _infer_dataset_dependencies(self, job_name: str, all_jobs: List[str]) -> Dict[str, List[str]]:
        """
        Infer job-to-job dependencies based on dataset read/write patterns.
        
        This method analyzes dataset access patterns to infer dependencies:
        - If job A writes a dataset and job B reads it, then B must run after A
        - If job A reads a dataset and job B writes it, then A must run before B
        
        Args:
            job_name: Name of the job to infer dependencies for
            all_jobs: List of all job names in the database (for cross-referencing)
            
        Returns:
            Dictionary with two keys:
                - 'mustRunAfter': List of job names that must run before this job
                  (jobs that write datasets this job reads)
                - 'mustRunBefore': List of job names that must run after this job
                  (jobs that read datasets this job writes)
            
        Note:
            The current database schema does not store dataset access information
            (read vs write) for JCL jobs. This method returns empty dependencies
            until the schema is enhanced to include dataset access patterns.
            
            Future enhancement: When dataset access information is available,
            this method should:
            1. Query datasets read by this job
            2. Query datasets written by this job
            3. Find jobs that write datasets this job reads (mustRunAfter)
            4. Find jobs that read datasets this job writes (mustRunBefore)
            5. Return the inferred dependencies
        """
        logger.debug(
            f"Inferring dataset-based dependencies for job: {job_name} "
            "(Note: Dataset access information not available in current schema)"
        )
        
        # TODO: Implement dataset-based dependency inference when schema supports it
        # Current schema does not store dataset access information (read/write)
        # for JCL jobs, so we return empty dependencies
        
        return {
            'mustRunAfter': [],
            'mustRunBefore': []
        }
    
    def _extract_dependencies(self, job_name: str, all_jobs: List[str]) -> Dict[str, List[str]]:
        """
        Extract and combine all job-to-job dependencies.
        
        This method combines explicit dependencies (from artifact_dependencies table)
        and inferred dependencies (from dataset access patterns) to build a complete
        dependency graph for a job. It handles circular dependencies gracefully by
        detecting and logging them.
        
        Args:
            job_name: Name of the job to extract dependencies for
            all_jobs: List of all job names in the database (for validation)
            
        Returns:
            Dictionary with two keys:
                - 'mustRunAfter': List of unique job names that must run before this job
                - 'mustRunBefore': List of unique job names that must run after this job
            
        Note:
            - Duplicate dependencies are removed
            - Self-dependencies are removed (job cannot depend on itself)
            - Circular dependencies are detected and logged but not removed
            - Dependencies are sorted alphabetically for consistency
            
        Examples:
            >>> exporter._extract_dependencies('JOB2', ['JOB1', 'JOB2', 'JOB3'])
            {'mustRunAfter': ['JOB1'], 'mustRunBefore': ['JOB3']}
        """
        try:
            logger.debug(f"Extracting dependencies for job: {job_name}")
            
            # Query explicit dependencies from database
            explicit_deps = self._query_explicit_dependencies(job_name)
            
            # Infer dependencies from dataset access patterns
            inferred_deps = self._infer_dataset_dependencies(job_name, all_jobs)
            
            # Combine dependencies from both sources
            # Use sets to automatically handle duplicates
            must_run_after = set(explicit_deps['mustRunAfter']) | set(inferred_deps['mustRunAfter'])
            must_run_before = set(explicit_deps['mustRunBefore']) | set(inferred_deps['mustRunBefore'])
            
            # Remove self-dependencies (job cannot depend on itself)
            must_run_after.discard(job_name)
            must_run_before.discard(job_name)
            
            # Detect circular dependencies
            circular_deps = must_run_after & must_run_before
            if circular_deps:
                logger.warning(
                    f"Circular dependency detected for job {job_name}: "
                    f"Jobs {circular_deps} appear in both mustRunAfter and mustRunBefore"
                )
            
            # Convert to sorted lists for consistent output
            must_run_after_list = sorted(list(must_run_after))
            must_run_before_list = sorted(list(must_run_before))
            
            logger.debug(
                f"Extracted {len(must_run_after_list)} mustRunAfter and "
                f"{len(must_run_before_list)} mustRunBefore dependencies for job {job_name}"
            )
            
            return {
                'mustRunAfter': must_run_after_list,
                'mustRunBefore': must_run_before_list
            }
            
        except ExportError:
            # Re-raise ExportError from query methods
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise ExportError(
                f"Failed to extract dependencies for job {job_name}",
                operation='extract',
                cause=e
            )
    
    def _extract_datasets(self, job_name: str) -> List[str]:
        """
        Extract unique dataset references for a job.
        
        This method queries the database for dataset information associated with
        a JCL job. It extracts fully qualified dataset names, deduplicates them,
        and returns them in a sorted list for consistency.
        
        Args:
            job_name: Name of the job to extract datasets for
            
        Returns:
            List of unique, fully qualified dataset names (sorted alphabetically)
            Returns empty list if no datasets found or if dataset information is unavailable
            
        Note:
            The current database schema stores dataset information in the inventory_jcl
            table as a JSON array in the 'datasets' column. This method parses that
            JSON and extracts unique dataset names.
            
        Examples:
            >>> exporter._extract_datasets('JOBNAME')
            ['DATASET.ONE', 'DATASET.TWO']
            
            >>> exporter._extract_datasets('EMPTYJOB')
            []
        """
        try:
            logger.debug(f"Extracting datasets for job: {job_name}")
            
            # Query datasets from inventory_jcl table
            # The datasets column contains a JSON array of dataset information
            self.cursor.execute("""
                SELECT datasets
                FROM inventory_jcl
                WHERE member_name = ?
            """, (job_name,))
            
            row = self.cursor.fetchone()
            
            # Handle case where job is not found
            if not row:
                logger.debug(f"Job {job_name} not found in inventory_jcl table")
                return []
            
            datasets_json = row[0]
            
            # Handle case where datasets column is NULL or empty
            if not datasets_json:
                logger.debug(f"No dataset information for job {job_name}")
                return []
            
            # Parse JSON array
            try:
                import json
                datasets_data = json.loads(datasets_json)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse datasets JSON for job {job_name}: {e}")
                return []
            
            # Handle case where datasets is not a list
            if not isinstance(datasets_data, list):
                logger.warning(f"Datasets for job {job_name} is not a list: {type(datasets_data)}")
                return []
            
            # Extract dataset names and deduplicate
            # Use a set to automatically handle duplicates
            dataset_names = set()
            
            for dataset_entry in datasets_data:
                # Handle different dataset entry formats
                if isinstance(dataset_entry, str):
                    # Simple string format
                    dataset_name = dataset_entry.strip()
                    if dataset_name:
                        dataset_names.add(dataset_name)
                elif isinstance(dataset_entry, dict):
                    # Dictionary format (may have 'name', 'dsn', or 'dataset' key)
                    for key in ['name', 'dsn', 'dataset', 'datasetName']:
                        if key in dataset_entry:
                            dataset_name = str(dataset_entry[key]).strip()
                            if dataset_name:
                                dataset_names.add(dataset_name)
                            break
                else:
                    logger.debug(f"Skipping unexpected dataset entry format: {type(dataset_entry)}")
            
            # Convert to sorted list for consistent output
            result = sorted(list(dataset_names))
            
            logger.debug(f"Extracted {len(result)} unique datasets for job {job_name}")
            return result
            
        except sqlite3.Error as e:
            logger.warning(f"Database error extracting datasets for job {job_name}: {e}")
            # Return empty list on error rather than raising exception
            # This allows export to continue even if dataset extraction fails
            return []
        except Exception as e:
            logger.warning(f"Unexpected error extracting datasets for job {job_name}: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'db') and self.db:
            self.db.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    
    def _apply_sorting(
        self,
        jobs: List[Dict[str, Any]],
        sort_by: str = "name"
    ) -> List[Dict[str, Any]]:
        """
        Apply sorting strategy to jobs list.
        
        This method creates the appropriate sorting strategy instance based on
        the sort_by parameter and applies it to the jobs list. It supports
        multiple sorting strategies to help migration engineers view jobs in
        the most useful order for their task.
        
        Args:
            jobs: List of job dictionaries to sort
            sort_by: Sorting strategy to apply. Valid values:
                - "name": Alphabetical by job name (default)
                - "type": Group by APPLICATION/INFRASTRUCTURE, then by name
                - "dependencies": Topological sort based on dependencies
                - "complexity": Sort by number of steps (descending)
            
        Returns:
            New list of jobs sorted according to the selected strategy
            
        Raises:
            ValueError: If sort_by parameter is not a valid strategy name
            
        Note:
            If an invalid sort_by value is provided, the method raises ValueError
            rather than falling back to a default. This ensures the caller is
            aware of the invalid parameter.
            
        Examples:
            >>> exporter._apply_sorting(jobs, "name")
            [job1, job2, job3]  # Sorted alphabetically
            
            >>> exporter._apply_sorting(jobs, "type")
            [app_job1, app_job2, infra_job1]  # APPLICATION jobs first
        """
        from .sorting_strategies import (
            NameSortingStrategy,
            TypeSortingStrategy,
            DependencySortingStrategy,
            ComplexitySortingStrategy
        )
        
        logger.info(f"Applying {sort_by} sorting strategy to {len(jobs)} jobs")
        
        # Map strategy names to strategy classes
        strategies = {
            'name': NameSortingStrategy,
            'type': TypeSortingStrategy,
            'dependencies': DependencySortingStrategy,
            'complexity': ComplexitySortingStrategy
        }
        
        # Validate sort_by parameter
        if sort_by not in strategies:
            valid_strategies = ', '.join(strategies.keys())
            raise ValueError(
                f"Invalid sort_by parameter: '{sort_by}'. "
                f"Valid values are: {valid_strategies}"
            )
        
        # Create strategy instance and apply it
        strategy_class = strategies[sort_by]
        strategy = strategy_class()
        sorted_jobs = strategy.sort(jobs)
        
        logger.info(f"Sorting completed using {sort_by} strategy")
        return sorted_jobs
    
    def _generate_summary(
        self,
        jobs: List[Dict[str, Any]],
        sort_by: str
    ) -> Dict[str, Any]:
        """
        Generate export summary with job counts and metadata.
        
        This method calculates summary statistics for the exported jobs,
        including total counts, job type breakdown, timestamp, and export
        configuration. The summary provides a quick overview of the job
        landscape for migration planning.
        
        Args:
            jobs: List of exported job dictionaries
            sort_by: Sorting strategy used for the export
            
        Returns:
            Dictionary containing summary information:
                - totalJobs: Total number of jobs exported
                - applicationJobs: Count of APPLICATION type jobs
                - infrastructureJobs: Count of INFRASTRUCTURE type jobs
                - exportDate: ISO 8601 formatted timestamp
                - database: Path to the database file
                - sortedBy: Sorting strategy used
                
        Note:
            The exportDate is generated in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
            for consistent timestamp representation across different systems.
            
        Examples:
            >>> exporter._generate_summary(jobs, "name")
            {
                'totalJobs': 35,
                'applicationJobs': 28,
                'infrastructureJobs': 7,
                'exportDate': '2026-01-30T12:34:56.789Z',
                'database': '/path/to/analyzer.db',
                'sortedBy': 'name'
            }
        """
        from datetime import datetime, timezone
        
        logger.info("Generating export summary")
        
        # Count total jobs
        total_jobs = len(jobs)
        
        # Count jobs by type
        application_jobs = sum(1 for job in jobs if job.get('jobType') == 'APPLICATION')
        infrastructure_jobs = sum(1 for job in jobs if job.get('jobType') == 'INFRASTRUCTURE')
        
        # Generate ISO 8601 timestamp in UTC
        # Format: YYYY-MM-DDTHH:MM:SS.sssZ
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        # Build summary dictionary
        summary = {
            'totalJobs': total_jobs,
            'applicationJobs': application_jobs,
            'infrastructureJobs': infrastructure_jobs,
            'exportDate': export_date,
            'database': self.db_path,
            'sortedBy': sort_by
        }
        
        logger.info(
            f"Summary generated: {total_jobs} total jobs "
            f"({application_jobs} APPLICATION, {infrastructure_jobs} INFRASTRUCTURE)"
        )
        
        return summary
    
    def export_jobs(
        self,
        output_dir: str,
        sort_by: str = "name"
    ) -> Dict[str, Any]:
        """
        Export all jobs from database with specified sorting.
        
        This is the main export method that orchestrates the complete job export
        workflow. It queries jobs from the database, extracts steps and dependencies,
        categorizes jobs, links them to flows, applies sorting, generates a summary,
        and writes the output to a JSON file.
        
        Args:
            output_dir: Directory for output JSON file
            sort_by: Sorting strategy (name, type, dependencies, complexity)
                Default is "name"
            
        Returns:
            Dictionary containing jobs array and summary:
                {
                    'jobs': [...],
                    'summary': {...}
                }
            
        Raises:
            ExportError: If database queries fail or file operations fail
            ValueError: If sort_by parameter is invalid
            
        Note:
            This method performs the following steps:
            1. Query all jobs from database
            2. For each job:
               - Extract steps
               - Assign step types and flow entry flags
               - Categorize job (APPLICATION vs INFRASTRUCTURE)
               - Link to flow if applicable
               - Extract dependencies
               - Extract datasets
            3. Apply sorting strategy
            4. Generate summary
            5. Write JSON output file
            6. Display output path
            
        Examples:
            >>> exporter = JobExporter('analyzer.db')
            >>> result = exporter.export_jobs('results/jobs', sort_by='type')
            >>> print(result['summary']['totalJobs'])
            35
        """
        import os
        
        logger.info(f"Starting job export with sort_by={sort_by}")
        
        # Validate sort_by parameter early
        valid_strategies = ['name', 'type', 'dependencies', 'complexity']
        if sort_by not in valid_strategies:
            raise ValueError(
                f"Invalid sort_by parameter: '{sort_by}'. "
                f"Valid values are: {', '.join(valid_strategies)}"
            )
        
        try:
            # Query all jobs from database
            jobs_metadata = self._query_jobs()
            
            # Handle empty database case
            if not jobs_metadata:
                logger.warning("No jobs found in database - creating empty export")
                print("Warning: No jobs found in database")
                
                # Create empty export with summary
                export_data = {
                    'jobs': [],
                    'summary': self._generate_summary([], sort_by)
                }
                
                # Write empty export to file
                self._write_json_output(export_data, output_dir, sort_by)
                
                logger.info("Empty job export completed")
                return export_data
            
            all_job_names = [job['jobName'] for job in jobs_metadata]
            
            logger.info(f"Processing {len(jobs_metadata)} jobs")
            
            # Process each job to build complete job data
            processed_jobs = []
            
            for job_meta in jobs_metadata:
                job_name = job_meta['jobName']
                logger.debug(f"Processing job: {job_name}")
                
                try:
                    # Extract steps for this job
                    steps = self._query_job_steps(job_name)
                    
                    # Assign step types and flow entry flags
                    steps = self._assign_step_types(steps)
                    
                    # Categorize job
                    job_type, has_custom_code = self._categorize_job(steps)
                    
                    # Link to flow if applicable
                    linked_flow = self._link_to_flow(steps)
                    
                    # Extract dependencies
                    dependencies = self._extract_dependencies(job_name, all_job_names)
                    
                    # Extract datasets
                    datasets = self._extract_datasets(job_name)
                    
                    # Build complete job entry
                    job_entry = {
                        'jobName': job_name,
                        'jobType': job_type,
                        'hasCustomCode': has_custom_code,
                        'linkedFlow': linked_flow,
                        'steps': steps,
                        'datasets': datasets,
                        'dependencies': dependencies
                    }
                    
                    processed_jobs.append(job_entry)
                    logger.debug(f"Completed processing job: {job_name}")
                    
                except ExportError:
                    # Re-raise ExportError from helper methods
                    raise
                except Exception as e:
                    # Wrap unexpected errors in ExportError
                    raise ExportError(
                        f"Failed to process job {job_name}",
                        operation='process',
                        cause=e
                    )
            
            # Apply sorting strategy
            try:
                sorted_jobs = self._apply_sorting(processed_jobs, sort_by)
            except ValueError:
                # Re-raise ValueError for invalid sort_by parameter
                raise
            except Exception as e:
                raise ExportError(
                    f"Failed to apply sorting strategy: {sort_by}",
                    operation='sort',
                    cause=e
                )
            
            # Generate summary
            try:
                summary = self._generate_summary(sorted_jobs, sort_by)
            except Exception as e:
                raise ExportError(
                    "Failed to generate export summary",
                    operation='summary',
                    cause=e
                )
            
            # Build complete export structure
            export_data = {
                'jobs': sorted_jobs,
                'summary': summary
            }
            
            # Write to JSON file
            self._write_json_output(export_data, output_dir, sort_by)
            
            logger.info("Job export completed successfully")
            return export_data
            
        except ExportError:
            # Re-raise ExportError with full context
            raise
        except ValueError:
            # Re-raise ValueError for invalid parameters
            raise
        except Exception as e:
            # Catch any unexpected errors and wrap in ExportError
            raise ExportError(
                "Unexpected error during job export",
                operation='export',
                cause=e
            )
    
    def _write_json_output(
        self,
        export_data: Dict[str, Any],
        output_dir: str,
        sort_by: str
    ) -> str:
        """
        Write export data to JSON file.
        
        This method handles file system operations for writing the export data
        to a JSON file. It creates the output directory if needed, generates
        the filename based on the sorting strategy, and writes the JSON with
        proper formatting.
        
        Args:
            export_data: Complete export data (jobs + summary)
            output_dir: Directory for output file
            sort_by: Sorting strategy (used in filename)
            
        Returns:
            Full path to the created output file
            
        Raises:
            ExportError: If directory creation, file writing, or JSON serialization fails
            
        Note:
            - Output filename format: jobs_by_{sort_strategy}.json
            - JSON is formatted with 2-space indentation for readability
            - Existing files are overwritten without prompting
            - Full output path is displayed to console
        """
        import os
        
        logger.info(f"Writing export to {output_dir}")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Output directory created/verified: {output_dir}")
        except OSError as e:
            raise ExportError(
                f"Cannot create output directory: {output_dir}",
                operation='create_directory',
                cause=e
            )
        
        # Generate filename based on sort strategy
        filename = f"jobs_by_{sort_by}.json"
        output_path = os.path.join(output_dir, filename)
        
        # Check if directory is writable before attempting to write
        if not os.access(output_dir, os.W_OK):
            raise ExportError(
                f"Output directory is not writable: {output_dir}",
                operation='write'
            )
        
        try:
            # Attempt JSON serialization first to catch serialization errors early
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            logger.debug(f"JSON serialization successful ({len(json_str)} bytes)")
        except (TypeError, ValueError) as e:
            # Extract problematic data for error message
            problematic_data = str(export_data)[:200]  # First 200 chars
            raise ExportError(
                f"Failed to serialize export data to JSON. Problematic data: {problematic_data}...",
                operation='serialize',
                cause=e
            )
        
        try:
            # Write JSON to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.debug(f"JSON written to file: {output_path}")
        except OSError as e:
            raise ExportError(
                f"Failed to write export file: {output_path}",
                operation='write',
                cause=e
            )
        
        # Get absolute path for display
        try:
            abs_path = os.path.abspath(output_path)
        except Exception as e:
            # Fall back to relative path if absolute path fails
            logger.warning(f"Failed to get absolute path: {e}")
            abs_path = output_path
        
        logger.info(f"Export written to: {abs_path}")
        print(f"Job export written to: {abs_path}")
        
        return abs_path
