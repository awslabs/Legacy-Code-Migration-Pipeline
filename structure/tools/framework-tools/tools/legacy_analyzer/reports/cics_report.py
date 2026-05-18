"""CICS Transaction Report Generator.

This module generates comprehensive reports for CICS transactions including:
- Transaction details (ID, program, group, status)
- Call trees (programs called by each transaction)
- Data dependencies (files and datasets accessed)
- Complexity metrics per transaction
- Modernization suggestions (API endpoint mappings)
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3
import logging
import json

from ..models.flow import EntryPoint
from ..models.complexity import ComplexityMetrics


logger = logging.getLogger(__name__)


@dataclass
class TransactionCallTree:
    """Represents the call tree for a CICS transaction."""
    
    depth: int
    programs: List[str]
    total_programs: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'depth': self.depth,
            'programs': self.programs,
            'total_programs': self.total_programs
        }


@dataclass
class TransactionDataDependencies:
    """Represents data dependencies for a CICS transaction."""
    
    files: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'files': self.files,
            'datasets': self.datasets
        }


@dataclass
class TransactionComplexity:
    """Represents complexity metrics for a CICS transaction."""
    
    composite_score: float
    tier: str
    total_loc: int = 0
    total_cyclomatic: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'composite_score': self.composite_score,
            'tier': self.tier,
            'total_loc': self.total_loc,
            'total_cyclomatic': self.total_cyclomatic
        }


@dataclass
class ModernizationSuggestion:
    """Represents modernization suggestions for a CICS transaction."""
    
    suggested_api_endpoint: str
    suggested_service: str
    http_method: str = 'GET'
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'suggested_api_endpoint': self.suggested_api_endpoint,
            'suggested_service': self.suggested_service,
            'http_method': self.http_method
        }
        if self.notes:
            result['notes'] = self.notes
        return result


@dataclass
class CICSTransactionReport:
    """Complete report for a single CICS transaction."""
    
    transaction_id: str
    program: str
    group: str
    status: str
    description: Optional[str] = None
    mapset: Optional[str] = None
    call_tree: Optional[TransactionCallTree] = None
    data_dependencies: Optional[TransactionDataDependencies] = None
    complexity: Optional[TransactionComplexity] = None
    modernization: Optional[ModernizationSuggestion] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'transaction_id': self.transaction_id,
            'program': self.program,
            'group': self.group,
            'status': self.status
        }
        
        if self.description:
            result['description'] = self.description
        if self.mapset:
            result['mapset'] = self.mapset
        if self.call_tree:
            result['call_tree'] = self.call_tree.to_dict()
        if self.data_dependencies:
            result['data_dependencies'] = self.data_dependencies.to_dict()
        if self.complexity:
            result['complexity'] = self.complexity.to_dict()
        if self.modernization:
            result['modernization'] = self.modernization.to_dict()
        
        return result


class CICSReportGenerator:
    """Generates CICS transaction reports from database."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize CICS report generator.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def _get_call_tree(self, program_name: str, max_depth: int = 10) -> TransactionCallTree:
        """
        Build call tree for a program using recursive dependency traversal.
        
        Args:
            program_name: Starting program name
            max_depth: Maximum depth to traverse
            
        Returns:
            TransactionCallTree object
        """
        visited = set()
        programs = []
        
        def traverse(prog: str, depth: int):
            """Recursively traverse call tree."""
            if depth > max_depth or prog in visited:
                return depth - 1
            
            visited.add(prog)
            programs.append(prog)
            
            # Get programs called by this program
            try:
                self.cursor.execute("""
                    SELECT DISTINCT target_artifact_name
                    FROM artifact_dependencies
                    WHERE source_artifact_name = ?
                      AND dependency_type IN ('CALL', 'EXEC_PGM')
                      AND target_type = 'PROGRAM'
                """, (prog,))
                
                callees = [row[0] for row in self.cursor.fetchall()]
                
                max_child_depth = depth
                for callee in callees:
                    child_depth = traverse(callee, depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
                
                return max_child_depth
                
            except sqlite3.Error as e:
                logger.warning(f"Error traversing call tree for {prog}: {e}")
                return depth
        
        max_depth_reached = traverse(program_name, 0)
        
        return TransactionCallTree(
            depth=max_depth_reached,
            programs=programs,
            total_programs=len(programs)
        )
    
    def _get_data_dependencies(self, programs: List[str]) -> TransactionDataDependencies:
        """
        Get data dependencies (files and datasets) for a list of programs.
        
        Args:
            programs: List of program names
            
        Returns:
            TransactionDataDependencies object
        """
        if not programs:
            return TransactionDataDependencies()
        
        files = set()
        datasets = set()
        
        try:
            # Get file dependencies
            placeholders = ','.join('?' * len(programs))
            self.cursor.execute(f"""
                SELECT DISTINCT target_artifact_name, target_type
                FROM artifact_dependencies
                WHERE source_artifact_name IN ({placeholders})
                  AND target_type IN ('FILE', 'DATASET')
            """, programs)
            
            for target_name, target_type in self.cursor.fetchall():
                if target_type == 'FILE':
                    files.add(target_name)
                elif target_type == 'DATASET':
                    datasets.add(target_name)
            
            # Also check CICS file definitions for dataset mappings
            self.cursor.execute(f"""
                SELECT DISTINCT resource_name, dataset_name
                FROM inventory_cics
                WHERE resource_type = 'FILE'
                  AND dataset_name IS NOT NULL
                  AND dataset_name != ''
            """)
            
            file_to_dataset = {row[0]: row[1] for row in self.cursor.fetchall()}
            
            # Map CICS files to datasets
            for file_name in list(files):
                if file_name in file_to_dataset:
                    datasets.add(file_to_dataset[file_name])
            
        except sqlite3.Error as e:
            logger.warning(f"Error getting data dependencies: {e}")
        
        return TransactionDataDependencies(
            files=sorted(list(files)),
            datasets=sorted(list(datasets))
        )
    
    def _get_complexity_metrics(self, programs: List[str]) -> Optional[TransactionComplexity]:
        """
        Calculate aggregate complexity metrics for a list of programs.
        
        Args:
            programs: List of program names
            
        Returns:
            TransactionComplexity object or None if no metrics available
        """
        if not programs:
            return None
        
        try:
            # Get complexity metrics from database
            placeholders = ','.join('?' * len(programs))
            self.cursor.execute(f"""
                SELECT 
                    SUM(lines_of_code) as total_loc,
                    SUM(cyclomatic_complexity) as total_cyclomatic,
                    SUM(composite_score) as total_composite
                FROM complexity_metrics
                WHERE program_name IN ({placeholders})
            """, programs)
            
            row = self.cursor.fetchone()
            if row and row[0] is not None:
                total_loc, total_cyclomatic, total_composite = row
                
                # Determine tier based on composite score
                if total_composite < 50:
                    tier = 'LOW'
                elif total_composite < 100:
                    tier = 'MEDIUM'
                elif total_composite < 200:
                    tier = 'HIGH'
                else:
                    tier = 'VERY_HIGH'
                
                return TransactionComplexity(
                    composite_score=float(total_composite),
                    tier=tier,
                    total_loc=int(total_loc),
                    total_cyclomatic=int(total_cyclomatic)
                )
        
        except sqlite3.Error as e:
            logger.warning(f"Error getting complexity metrics: {e}")
        
        return None
    
    def _generate_modernization_suggestion(
        self,
        transaction_id: str,
        description: Optional[str],
        group: str
    ) -> ModernizationSuggestion:
        """
        Generate modernization suggestions for a CICS transaction.
        
        Args:
            transaction_id: Transaction ID
            description: Transaction description
            group: CICS group name
            
        Returns:
            ModernizationSuggestion object
        """
        # Infer HTTP method from transaction ID or description
        http_method = 'GET'
        notes = None
        
        # Common patterns for CRUD operations
        trans_lower = transaction_id.lower()
        desc_lower = (description or '').lower()
        
        if any(word in trans_lower or word in desc_lower 
               for word in ['add', 'create', 'new', 'insert']):
            http_method = 'POST'
        elif any(word in trans_lower or word in desc_lower 
                 for word in ['upd', 'edit', 'modify', 'change']):
            http_method = 'PUT'
        elif any(word in trans_lower or word in desc_lower 
                 for word in ['del', 'remove', 'delete']):
            http_method = 'DELETE'
        elif any(word in trans_lower or word in desc_lower 
                 for word in ['list', 'search', 'query', 'view', 'display']):
            http_method = 'GET'
        
        # Generate API endpoint suggestion
        # Use description to create meaningful endpoint
        if description:
            # Extract key words from description
            words = description.lower().split()
            # Filter out common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            key_words = [w for w in words if w not in stop_words and len(w) > 2]
            
            if key_words:
                resource = key_words[0] if key_words else 'resource'
                endpoint = f"/{resource}s"
                
                # Add ID parameter for specific operations
                if http_method in ['GET', 'PUT', 'DELETE'] and 'list' not in desc_lower:
                    endpoint += "/{id}"
            else:
                endpoint = f"/{transaction_id.lower()}"
        else:
            endpoint = f"/{transaction_id.lower()}"
        
        # Generate service name from group
        service_name = f"{group.title()} Service"
        
        return ModernizationSuggestion(
            suggested_api_endpoint=f"{http_method} {endpoint}",
            suggested_service=service_name,
            http_method=http_method,
            notes=notes
        )
    
    def generate_transaction_report(
        self,
        transaction_id: str
    ) -> Optional[CICSTransactionReport]:
        """
        Generate a complete report for a single CICS transaction.
        
        Args:
            transaction_id: CICS transaction ID
            
        Returns:
            CICSTransactionReport object or None if transaction not found
        """
        try:
            # Get transaction details
            self.cursor.execute("""
                SELECT 
                    resource_name,
                    program_name,
                    group_name,
                    status,
                    description
                FROM inventory_cics
                WHERE resource_type = 'TRANSACTION'
                  AND resource_name = ?
            """, (transaction_id,))
            
            row = self.cursor.fetchone()
            if not row:
                logger.warning(f"Transaction {transaction_id} not found")
                return None
            
            trans_id, program_name, group_name, status, description = row
            
            if not program_name:
                logger.warning(f"Transaction {transaction_id} has no program_name")
                return None
            
            # Get mapset if available
            mapset = None
            try:
                self.cursor.execute("""
                    SELECT resource_name
                    FROM inventory_cics
                    WHERE resource_type = 'MAPSET'
                      AND group_name = ?
                    LIMIT 1
                """, (group_name,))
                mapset_row = self.cursor.fetchone()
                if mapset_row:
                    mapset = mapset_row[0]
            except sqlite3.Error:
                pass
            
            # Build call tree
            call_tree = self._get_call_tree(program_name)
            
            # Get data dependencies
            data_dependencies = self._get_data_dependencies(call_tree.programs)
            
            # Get complexity metrics
            complexity = self._get_complexity_metrics(call_tree.programs)
            
            # Generate modernization suggestion
            modernization = self._generate_modernization_suggestion(
                trans_id,
                description,
                group_name
            )
            
            return CICSTransactionReport(
                transaction_id=trans_id,
                program=program_name,
                group=group_name,
                status=status,
                description=description,
                mapset=mapset,
                call_tree=call_tree,
                data_dependencies=data_dependencies,
                complexity=complexity,
                modernization=modernization
            )
        
        except sqlite3.Error as e:
            logger.error(f"Error generating transaction report: {e}")
            return None
    
    def generate_all_transactions_report(
        self,
        include_disabled: bool = False
    ) -> Dict[str, Any]:
        """
        Generate reports for all CICS transactions.
        
        Args:
            include_disabled: If True, include DISABLED transactions
            
        Returns:
            Dictionary with transaction reports and summary
        """
        try:
            # Get all transactions
            query = """
                SELECT resource_name
                FROM inventory_cics
                WHERE resource_type = 'TRANSACTION'
            """
            
            if not include_disabled:
                query += " AND status = 'ENABLED'"
            
            self.cursor.execute(query)
            transaction_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Generate report for each transaction
            transactions = []
            for trans_id in transaction_ids:
                report = self.generate_transaction_report(trans_id)
                if report:
                    transactions.append(report)
            
            # Calculate summary statistics
            summary = self._calculate_summary(transactions)
            
            return {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_transactions': len(transactions),
                    'include_disabled': include_disabled
                },
                'transactions': [t.to_dict() for t in transactions],
                'summary': summary
            }
        
        except sqlite3.Error as e:
            logger.error(f"Error generating all transactions report: {e}")
            return {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'error': str(e)
                },
                'transactions': [],
                'summary': {}
            }
    
    def _calculate_summary(
        self,
        transactions: List[CICSTransactionReport]
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics for transactions.
        
        Args:
            transactions: List of transaction reports
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_transactions': len(transactions),
            'enabled': 0,
            'disabled': 0,
            'by_group': {},
            'by_complexity_tier': {
                'LOW': 0,
                'MEDIUM': 0,
                'HIGH': 0,
                'VERY_HIGH': 0
            },
            'total_programs': 0,
            'total_files': 0,
            'total_datasets': 0
        }
        
        programs_set = set()
        files_set = set()
        datasets_set = set()
        
        for trans in transactions:
            # Count by status
            if trans.status == 'ENABLED':
                summary['enabled'] += 1
            else:
                summary['disabled'] += 1
            
            # Count by group
            summary['by_group'][trans.group] = \
                summary['by_group'].get(trans.group, 0) + 1
            
            # Count by complexity tier
            if trans.complexity:
                summary['by_complexity_tier'][trans.complexity.tier] += 1
            
            # Collect unique programs, files, datasets
            if trans.call_tree:
                programs_set.update(trans.call_tree.programs)
            
            if trans.data_dependencies:
                files_set.update(trans.data_dependencies.files)
                datasets_set.update(trans.data_dependencies.datasets)
        
        summary['total_programs'] = len(programs_set)
        summary['total_files'] = len(files_set)
        summary['total_datasets'] = len(datasets_set)
        
        return summary


def generate_cics_transactions_report(
    db_path: str,
    output_format: str = 'json',
    include_disabled: bool = False
) -> str:
    """
    Generate CICS transactions report from database.
    
    This is a convenience function that creates a CICSReportGenerator
    and generates the report.
    
    Args:
        db_path: Path to SQLite database
        output_format: Output format ('json' or 'html')
        include_disabled: If True, include DISABLED transactions
        
    Returns:
        Report as string (JSON or HTML)
    """
    try:
        conn = sqlite3.connect(db_path)
        generator = CICSReportGenerator(conn)
        
        report_data = generator.generate_all_transactions_report(include_disabled)
        
        if output_format == 'json':
            return json.dumps(report_data, indent=2)
        elif output_format == 'html':
            return _generate_html_report(report_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    except Exception as e:
        logger.error(f"Error generating CICS transactions report: {e}")
        return json.dumps({
            'error': str(e),
            'metadata': {
                'generated_at': datetime.now().isoformat()
            }
        }, indent=2)
    finally:
        if 'conn' in locals():
            conn.close()


def _generate_html_report(report_data: Dict[str, Any]) -> str:
    """
    Generate HTML report from report data.
    
    Args:
        report_data: Report data dictionary
        
    Returns:
        HTML report as string
    """
    html_parts = []
    
    # HTML header
    html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CICS Transactions Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .summary {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .transaction {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .transaction-header {
            background-color: #007bff;
            color: white;
            padding: 10px;
            margin: -15px -15px 15px -15px;
            border-radius: 5px 5px 0 0;
        }
        .status-enabled {
            color: green;
            font-weight: bold;
        }
        .status-disabled {
            color: red;
            font-weight: bold;
        }
        .complexity-low { color: green; }
        .complexity-medium { color: orange; }
        .complexity-high { color: red; }
        .complexity-very-high { color: darkred; font-weight: bold; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
        }
        .api-suggestion {
            background-color: #d1ecf1;
            padding: 10px;
            border-left: 4px solid #0c5460;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>CICS Transactions Report</h1>
""")
    
    # Metadata
    metadata = report_data.get('metadata', {})
    html_parts.append(f"""
        <div class="summary">
            <p><strong>Generated:</strong> {metadata.get('generated_at', 'N/A')}</p>
            <p><strong>Total Transactions:</strong> {metadata.get('total_transactions', 0)}</p>
        </div>
""")
    
    # Summary
    summary = report_data.get('summary', {})
    if summary:
        html_parts.append("""
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
""")
        html_parts.append(f"""
            <tr><td>Total Transactions</td><td>{summary.get('total_transactions', 0)}</td></tr>
            <tr><td>Enabled</td><td class="status-enabled">{summary.get('enabled', 0)}</td></tr>
            <tr><td>Disabled</td><td class="status-disabled">{summary.get('disabled', 0)}</td></tr>
            <tr><td>Total Programs</td><td>{summary.get('total_programs', 0)}</td></tr>
            <tr><td>Total Files</td><td>{summary.get('total_files', 0)}</td></tr>
            <tr><td>Total Datasets</td><td>{summary.get('total_datasets', 0)}</td></tr>
        </table>
""")
    
    # Transactions
    transactions = report_data.get('transactions', [])
    if transactions:
        html_parts.append("<h2>Transactions</h2>")
        
        for trans in transactions:
            status_class = 'status-enabled' if trans.get('status') == 'ENABLED' else 'status-disabled'
            
            html_parts.append(f"""
        <div class="transaction">
            <div class="transaction-header">
                <h3>{trans.get('transaction_id')} - {trans.get('description', 'No description')}</h3>
            </div>
            <p><strong>Program:</strong> {trans.get('program')}</p>
            <p><strong>Group:</strong> {trans.get('group')}</p>
            <p><strong>Status:</strong> <span class="{status_class}">{trans.get('status')}</span></p>
""")
            
            # Call tree
            call_tree = trans.get('call_tree')
            if call_tree:
                html_parts.append(f"""
            <p><strong>Call Tree:</strong> Depth {call_tree.get('depth')}, {call_tree.get('total_programs')} programs</p>
""")
            
            # Complexity
            complexity = trans.get('complexity')
            if complexity:
                tier = complexity.get('tier', 'UNKNOWN').lower().replace('_', '-')
                html_parts.append(f"""
            <p><strong>Complexity:</strong> 
                <span class="complexity-{tier}">{complexity.get('tier')}</span> 
                (Score: {complexity.get('composite_score', 0):.2f}, 
                LOC: {complexity.get('total_loc', 0):,})
            </p>
""")
            
            # Modernization suggestion
            modernization = trans.get('modernization')
            if modernization:
                html_parts.append(f"""
            <div class="api-suggestion">
                <strong>Modernization Suggestion:</strong><br>
                API Endpoint: <code>{modernization.get('suggested_api_endpoint')}</code><br>
                Service: {modernization.get('suggested_service')}
            </div>
""")
            
            html_parts.append("        </div>")
    
    # HTML footer
    html_parts.append("""
    </div>
</body>
</html>
""")
    
    return ''.join(html_parts)
