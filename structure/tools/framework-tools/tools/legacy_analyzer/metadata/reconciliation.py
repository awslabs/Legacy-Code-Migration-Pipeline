"""Metadata reconciliation for CICS resources.

This module provides reconciliation between CICS metadata (from CSD files)
and actual source code inventory. It detects:
1. Programs defined in CSD but missing from source code
2. Programs in source code but not defined in CSD
3. Status mismatches between CSD and code analysis

This helps identify data quality issues and potential cleanup opportunities.
"""

from typing import List, Dict, Set, Optional, Any
import sqlite3
import logging
from dataclasses import dataclass, field

from ..utils.database_utils import check_table_exists
from ..constants import (
    SEVERITY_ERROR,
    SEVERITY_WARNING,
    SEVERITY_INFO,
    ISSUE_TYPE_MISSING_IN_CODE,
    ISSUE_TYPE_MISSING_IN_CSD,
    ISSUE_TYPE_STATUS_MISMATCH,
    STATUS_ENABLED,
    STATUS_DISABLED,
)


logger = logging.getLogger(__name__)


@dataclass
class ReconciliationIssue:
    """Represents a reconciliation issue between metadata and code."""
    
    issue_type: str  # 'missing_in_code', 'missing_in_csd', 'status_mismatch'
    program_name: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    issue: str  # Human-readable description
    recommendation: str  # Suggested action
    
    # Additional context
    transaction_id: Optional[str] = None
    cics_group: Optional[str] = None
    csd_status: Optional[str] = None
    code_status: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'issue_type': self.issue_type,
            'program': self.program_name,
            'severity': self.severity,
            'issue': self.issue,
            'recommendation': self.recommendation
        }
        
        # Add optional fields if present
        if self.transaction_id:
            result['transaction_id'] = self.transaction_id
        if self.cics_group:
            result['cics_group'] = self.cics_group
        if self.csd_status:
            result['csd_status'] = self.csd_status
        if self.code_status:
            result['code_status'] = self.code_status
        
        return result


@dataclass
class ReconciliationReport:
    """Complete reconciliation report."""
    
    programs_in_csd_not_in_code: List[ReconciliationIssue] = field(default_factory=list)
    programs_in_code_not_in_csd: List[ReconciliationIssue] = field(default_factory=list)
    status_mismatches: List[ReconciliationIssue] = field(default_factory=list)
    
    def get_all_issues(self) -> List[ReconciliationIssue]:
        """Get all issues in a single list."""
        return (
            self.programs_in_csd_not_in_code +
            self.programs_in_code_not_in_csd +
            self.status_mismatches
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        all_issues = self.get_all_issues()
        
        return {
            'total_issues': len(all_issues),
            'missing_in_code': len(self.programs_in_csd_not_in_code),
            'missing_in_csd': len(self.programs_in_code_not_in_csd),
            'status_mismatches': len(self.status_mismatches),
            'by_severity': {
                'ERROR': sum(1 for i in all_issues if i.severity == 'ERROR'),
                'WARNING': sum(1 for i in all_issues if i.severity == 'WARNING'),
                'INFO': sum(1 for i in all_issues if i.severity == 'INFO')
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'reconciliation': {
                'programs_in_csd_not_in_code': [
                    issue.to_dict() for issue in self.programs_in_csd_not_in_code
                ],
                'programs_in_code_not_in_csd': [
                    issue.to_dict() for issue in self.programs_in_code_not_in_csd
                ],
                'status_mismatches': [
                    issue.to_dict() for issue in self.status_mismatches
                ]
            },
            'summary': self.get_summary()
        }


class MetadataReconciler:
    """Reconciles CICS metadata with source code inventory.
    
    This class compares CICS metadata (from CSD files stored in inventory_cics)
    with actual source code inventory to identify discrepancies and data quality issues.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize metadata reconciler.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self._has_cics_table = check_table_exists(db_connection, 'inventory_cics')
        self._has_inventory_table = check_table_exists(db_connection, 'inventory')
    
    def get_cics_programs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all programs defined in CICS metadata.
        
        Returns:
            Dictionary mapping program_name to metadata dict
        """
        if not self._has_cics_table:
            logger.warning("inventory_cics table not found")
            return {}
        
        try:
            # Get programs from TRANSACTION resources (these have program_name)
            self.cursor.execute("""
                SELECT DISTINCT
                    program_name,
                    resource_name as transaction_id,
                    group_name,
                    status,
                    description
                FROM inventory_cics
                WHERE resource_type = 'TRANSACTION'
                  AND program_name IS NOT NULL
                  AND program_name != ''
            """)
            
            programs = {}
            for row in self.cursor.fetchall():
                program_name, trans_id, group, status, description = row
                
                # If program already exists, keep the first one (or merge)
                if program_name not in programs:
                    programs[program_name] = {
                        'transaction_id': trans_id,
                        'cics_group': group,
                        'status': status,
                        'description': description
                    }
            
            # Also get programs from PROGRAM resources
            self.cursor.execute("""
                SELECT DISTINCT
                    resource_name as program_name,
                    group_name,
                    status,
                    description
                FROM inventory_cics
                WHERE resource_type = 'PROGRAM'
            """)
            
            for row in self.cursor.fetchall():
                program_name, group, status, description = row
                
                # Add if not already present from TRANSACTION
                if program_name not in programs:
                    programs[program_name] = {
                        'transaction_id': None,
                        'cics_group': group,
                        'status': status,
                        'description': description
                    }
            
            logger.info(f"Found {len(programs)} programs in CICS metadata")
            return programs
            
        except sqlite3.Error as e:
            logger.error(f"Error querying CICS programs: {e}")
            return {}
    
    def get_code_programs(self) -> Set[str]:
        """
        Get all programs from source code inventory.
        
        Returns:
            Set of program names found in source code
        """
        if not self._has_inventory_table:
            logger.warning("inventory table not found")
            return set()
        
        try:
            # Get programs from inventory table
            self.cursor.execute("""
                SELECT DISTINCT artifact_name
                FROM inventory
                WHERE artifact_type = 'PROGRAM'
            """)
            
            programs = {row[0] for row in self.cursor.fetchall()}
            logger.info(f"Found {len(programs)} programs in source code inventory")
            return programs
            
        except sqlite3.Error as e:
            logger.error(f"Error querying code programs: {e}")
            return set()
    
    def detect_programs_in_csd_not_in_code(
        self,
        cics_programs: Dict[str, Dict[str, Any]],
        code_programs: Set[str]
    ) -> List[ReconciliationIssue]:
        """
        Detect programs defined in CSD but not found in source code.
        
        Args:
            cics_programs: Programs from CICS metadata
            code_programs: Programs from source code
            
        Returns:
            List of reconciliation issues
        """
        issues = []
        
        for program_name, metadata in cics_programs.items():
            if program_name not in code_programs:
                # Determine severity based on status
                severity = 'WARNING' if metadata['status'] == 'DISABLED' else 'ERROR'
                
                # Build issue description
                if metadata['transaction_id']:
                    issue_desc = (
                        f"Program '{program_name}' is referenced by CICS transaction "
                        f"'{metadata['transaction_id']}' but source code not found"
                    )
                else:
                    issue_desc = (
                        f"Program '{program_name}' is defined in CICS metadata "
                        f"but source code not found"
                    )
                
                # Build recommendation
                if metadata['status'] == 'DISABLED':
                    recommendation = (
                        "Program is DISABLED in CICS. Consider removing from CSD "
                        "if no longer needed."
                    )
                else:
                    recommendation = (
                        "Verify program name is correct. If program was removed, "
                        "update CSD to disable or remove the definition."
                    )
                
                issue = ReconciliationIssue(
                    issue_type='missing_in_code',
                    program_name=program_name,
                    severity=severity,
                    issue=issue_desc,
                    recommendation=recommendation,
                    transaction_id=metadata['transaction_id'],
                    cics_group=metadata['cics_group'],
                    csd_status=metadata['status']
                )
                issues.append(issue)
        
        logger.info(f"Found {len(issues)} programs in CSD but not in code")
        return issues
    
    def detect_programs_in_code_not_in_csd(
        self,
        cics_programs: Dict[str, Dict[str, Any]],
        code_programs: Set[str]
    ) -> List[ReconciliationIssue]:
        """
        Detect programs in source code but not defined in CSD.
        
        Enhanced logic: Uses dependency information to distinguish between:
        - Programs with no incoming dependencies (potential missing entry points) - WARNING
        - Programs with incoming dependencies (likely subprograms/utilities) - INFO
        - When dependency information is unavailable, defaults to INFO
        
        Args:
            cics_programs: Programs from CICS metadata
            code_programs: Programs from source code
            
        Returns:
            List of reconciliation issues
        """
        issues = []
        
        # Get programs with incoming dependencies (called by other programs)
        programs_with_incoming_deps = self._get_programs_with_incoming_dependencies()
        
        # Check if programs are also called by JCL (batch entry points)
        programs_called_by_jcl = self._get_programs_called_by_jcl()
        
        # Check if dependency information is available
        has_dependency_info = bool(programs_with_incoming_deps or programs_called_by_jcl)
        
        for program_name in code_programs:
            if program_name not in cics_programs:
                # Determine if program has incoming dependencies
                has_incoming_deps = program_name in programs_with_incoming_deps
                called_by_jcl = program_name in programs_called_by_jcl
                
                # Enhanced logic based on dependency analysis
                if not has_dependency_info:
                    # No dependency information available - default to INFO
                    severity = 'INFO'
                    issue_text = (
                        f"Program '{program_name}' found in source code but no CICS "
                        f"transaction definition found"
                    )
                    recommendation = (
                        "Verify if CICS transaction definition is missing or if this is "
                        "a utility/subprogram. Run dependency analysis for more details."
                    )
                elif not has_incoming_deps and not called_by_jcl:
                    # No incoming dependencies and not in JCL = potential missing entry point
                    severity = 'WARNING'
                    issue_text = (
                        f"Program '{program_name}' found in source code WITHOUT incoming "
                        f"dependencies, but no CICS transaction or JCL job definition found"
                    )
                    recommendation = (
                        "This program appears to be an entry point but is not accessible "
                        "via CICS transactions or JCL jobs. Verify if: 1) CICS transaction "
                        "definition is missing, 2) JCL job definition is missing, or "
                        "3) program should be removed as unused code."
                    )
                elif called_by_jcl:
                    # Called by JCL but not in CICS = batch program (expected)
                    severity = 'INFO'
                    issue_text = (
                        f"Program '{program_name}' found in source code as batch program "
                        f"(called by JCL) but no CICS transaction definition found"
                    )
                    recommendation = (
                        "This is expected for batch programs. No action needed unless "
                        "this program should also be accessible via CICS transactions."
                    )
                else:
                    # Has incoming dependencies = likely subprogram/utility
                    severity = 'INFO'
                    dep_count = len(programs_with_incoming_deps.get(program_name, []))
                    issue_text = (
                        f"Program '{program_name}' found in source code WITH {dep_count} "
                        f"incoming dependencies, but no CICS transaction definition found"
                    )
                    recommendation = (
                        "This is likely a utility/subprogram (expected). Verify if this "
                        "is a called subprogram or if CICS metadata is missing."
                    )
                
                issue = ReconciliationIssue(
                    issue_type='missing_in_csd',
                    program_name=program_name,
                    severity=severity,
                    issue=issue_text,
                    recommendation=recommendation,
                    code_status='ACTIVE'
                )
                issues.append(issue)
        
        # Log summary with enhanced categorization
        warning_count = sum(1 for issue in issues if issue.severity == 'WARNING')
        info_count = sum(1 for issue in issues if issue.severity == 'INFO')
        
        if has_dependency_info:
            logger.info(
                f"Found {len(issues)} programs in code but not in CSD: "
                f"{warning_count} potential missing entry points (WARNING), "
                f"{info_count} likely subprograms/utilities (INFO)"
            )
        else:
            logger.info(
                f"Found {len(issues)} programs in code but not in CSD "
                f"(dependency information not available, all marked as INFO)"
            )
        return issues
    
    def detect_status_mismatches(
        self,
        cics_programs: Dict[str, Dict[str, Any]],
        code_programs: Set[str]
    ) -> List[ReconciliationIssue]:
        """
        Detect status mismatches between CSD and code.
        
        A program that is DISABLED in CSD but still present in active source code
        might indicate a cleanup opportunity.
        
        Args:
            cics_programs: Programs from CICS metadata
            code_programs: Programs from source code
            
        Returns:
            List of reconciliation issues
        """
        issues = []
        
        for program_name, metadata in cics_programs.items():
            # Check if program is DISABLED in CSD but present in code
            if metadata['status'] == 'DISABLED' and program_name in code_programs:
                issue = ReconciliationIssue(
                    issue_type='status_mismatch',
                    program_name=program_name,
                    severity='WARNING',
                    issue=(
                        f"Program '{program_name}' is DISABLED in CICS but source "
                        f"code is still present"
                    ),
                    recommendation=(
                        "Consider removing source code if program is no longer used, "
                        "or re-enable in CICS if still needed. Review with business "
                        "stakeholders before removing."
                    ),
                    transaction_id=metadata['transaction_id'],
                    cics_group=metadata['cics_group'],
                    csd_status='DISABLED',
                    code_status='ACTIVE'
                )
                issues.append(issue)
        
        logger.info(f"Found {len(issues)} status mismatches")
        return issues
    
    def reconcile(self) -> ReconciliationReport:
        """
        Perform complete reconciliation between CICS metadata and source code.
        
        Returns:
            ReconciliationReport with all detected issues
        """
        logger.info("Starting metadata reconciliation")
        
        # Check prerequisites
        if not self._has_cics_table:
            logger.error("Cannot reconcile: inventory_cics table not found")
            return ReconciliationReport()
        
        if not self._has_inventory_table:
            logger.error("Cannot reconcile: inventory table not found")
            return ReconciliationReport()
        
        # Get data from both sources
        cics_programs = self.get_cics_programs()
        code_programs = self.get_code_programs()
        
        if not cics_programs:
            logger.warning("No CICS programs found, reconciliation may be incomplete")
        
        if not code_programs:
            logger.warning("No code programs found, reconciliation may be incomplete")
        
        # Detect issues
        report = ReconciliationReport()
        
        report.programs_in_csd_not_in_code = self.detect_programs_in_csd_not_in_code(
            cics_programs,
            code_programs
        )
        
        report.programs_in_code_not_in_csd = self.detect_programs_in_code_not_in_csd(
            cics_programs,
            code_programs
        )
        
        report.status_mismatches = self.detect_status_mismatches(
            cics_programs,
            code_programs
        )
        
        # Log summary
        summary = report.get_summary()
        logger.info(
            f"Reconciliation complete: {summary['total_issues']} issues found "
            f"({summary['missing_in_code']} missing in code, "
            f"{summary['missing_in_csd']} missing in CSD, "
            f"{summary['status_mismatches']} status mismatches)"
        )
        
        return report
    
    def _get_programs_with_incoming_dependencies(self) -> Dict[str, List[str]]:
        """
        Get programs that have incoming dependencies (are called by other programs).
        
        Returns:
            Dictionary mapping program_name -> list of programs that call it
        """
        programs_with_deps = {}
        
        try:
            # Check if artifact_dependencies table exists
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='artifact_dependencies'
            """)
            
            if not self.cursor.fetchone():
                logger.warning("artifact_dependencies table not found")
                return programs_with_deps
            
            # Get all dependencies where target is a PROGRAM
            self.cursor.execute("""
                SELECT 
                    target_artifact_name,
                    source_artifact_name
                FROM artifact_dependencies
                WHERE target_artifact_type = 'PROGRAM'
                  AND dependency_type IN ('CALL', 'CICS_LINK', 'CICS_START')
            """)
            
            for target_program, source_program in self.cursor.fetchall():
                if target_program not in programs_with_deps:
                    programs_with_deps[target_program] = []
                programs_with_deps[target_program].append(source_program)
            
            logger.debug(f"Found {len(programs_with_deps)} programs with incoming dependencies")
            
        except sqlite3.Error as e:
            logger.error(f"Error querying program dependencies: {e}")
        
        return programs_with_deps
    
    def _get_programs_called_by_jcl(self) -> Set[str]:
        """
        Get programs that are called by JCL jobs (batch entry points).
        
        Returns:
            Set of program names called by JCL
        """
        jcl_programs = set()
        
        try:
            # Check if artifact_dependencies table exists
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='artifact_dependencies'
            """)
            
            if not self.cursor.fetchone():
                logger.warning("artifact_dependencies table not found")
                return jcl_programs
            
            # Get programs called by JCL
            self.cursor.execute("""
                SELECT DISTINCT target_artifact_name
                FROM artifact_dependencies
                WHERE source_artifact_type = 'JCL'
                  AND dependency_type = 'EXEC_PGM'
                  AND target_artifact_type = 'PROGRAM'
            """)
            
            jcl_programs = {row[0] for row in self.cursor.fetchall()}
            logger.debug(f"Found {len(jcl_programs)} programs called by JCL")
            
        except sqlite3.Error as e:
            logger.error(f"Error querying JCL program dependencies: {e}")
        
        return jcl_programs
