"""Complexity analyzer for legacy code."""

import re
from typing import Dict, List, Optional, Set
from ..models.complexity import ComplexityMetrics, ComplexityThresholds


class ComplexityAnalyzer:
    """
    Analyzes complexity of legacy programs.
    
    Calculates:
    - Lines of code (LOC)
    - Cyclomatic complexity
    - Dependency counts
    - Composite complexity score
    - Complexity tier classification
    """
    
    def __init__(self, database=None, thresholds: Optional[ComplexityThresholds] = None):
        """
        Initialize complexity analyzer.
        
        Args:
            database: Database connection (optional)
            thresholds: Complexity thresholds (optional, uses defaults if not provided)
        """
        self.database = database
        self.thresholds = thresholds or ComplexityThresholds()
    
    def analyze_program(self,
                       program_name: str,
                       source_code: str,
                       language: str,
                       dependency_count_in: int = 0,
                       dependency_count_out: int = 0) -> ComplexityMetrics:
        """
        Analyze complexity of a single program.
        
        Args:
            program_name: Name of the program
            source_code: Source code content
            language: Programming language (COBOL, PLI, JCL, etc.)
            dependency_count_in: Number of incoming dependencies
            dependency_count_out: Number of outgoing dependencies
            
        Returns:
            ComplexityMetrics object with all calculated metrics
        """
        # Calculate LOC metrics
        loc_metrics = self.calculate_loc(source_code, language)
        
        # Calculate cyclomatic complexity
        cyclomatic = self.calculate_cyclomatic_complexity(source_code, language)
        
        # Get language factor
        language_factor = self.thresholds.get_language_factor(language)
        
        # Calculate composite score
        composite_score = ComplexityMetrics.calculate_composite_score(
            loc=loc_metrics['loc'],
            cyclomatic=cyclomatic,
            deps_in=dependency_count_in,
            deps_out=dependency_count_out,
            loc_weight=self.thresholds.loc_weight,
            cyclomatic_weight=self.thresholds.cyclomatic_weight,
            deps_weight=self.thresholds.deps_weight,
            language_factor=language_factor
        )
        
        # Determine complexity tier
        complexity_tier = ComplexityMetrics.determine_tier(composite_score)
        
        # Check if god program
        is_god_program = ComplexityMetrics.is_god_program_check(
            loc=loc_metrics['loc'],
            cyclomatic=cyclomatic,
            deps_total=dependency_count_in + dependency_count_out,
            loc_threshold=self.thresholds.god_loc_threshold,
            cyclomatic_threshold=self.thresholds.god_cyclomatic_threshold,
            deps_threshold=self.thresholds.god_deps_threshold
        )
        
        # Create metrics object
        metrics = ComplexityMetrics(
            program_name=program_name,
            language=language,
            lines_of_code=loc_metrics['loc'],
            cyclomatic_complexity=cyclomatic,
            dependency_count_in=dependency_count_in,
            dependency_count_out=dependency_count_out,
            composite_score=composite_score,
            complexity_tier=complexity_tier,
            comment_lines=loc_metrics['comment_lines'],
            blank_lines=loc_metrics['blank_lines'],
            total_lines=loc_metrics['total_lines'],
            language_factor=language_factor,
            is_god_program=is_god_program
        )
        
        return metrics
    
    def analyze_all_programs(self,
                            programs: Dict[str, Dict[str, any]]) -> Dict[str, ComplexityMetrics]:
        """
        Analyze complexity of multiple programs.
        
        Args:
            programs: Dictionary mapping program names to program info
                     Each program info should have:
                     - 'source_code': str
                     - 'language': str
                     - 'dependency_count_in': int (optional)
                     - 'dependency_count_out': int (optional)
        
        Returns:
            Dictionary mapping program names to ComplexityMetrics
        """
        results = {}
        
        for program_name, program_info in programs.items():
            source_code = program_info.get('source_code', '')
            language = program_info.get('language', 'UNKNOWN')
            deps_in = program_info.get('dependency_count_in', 0)
            deps_out = program_info.get('dependency_count_out', 0)
            
            try:
                metrics = self.analyze_program(
                    program_name=program_name,
                    source_code=source_code,
                    language=language,
                    dependency_count_in=deps_in,
                    dependency_count_out=deps_out
                )
                results[program_name] = metrics
            except Exception as e:
                # Log error but continue with other programs
                print(f"Error analyzing {program_name}: {e}")
                continue
        
        return results
    
    def calculate_loc(self, source_code: str, language: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics.
        
        Counts:
        - Total lines
        - Blank lines
        - Comment lines
        - Lines of code (total - blank - comments)
        
        Args:
            source_code: Source code content
            language: Programming language
            
        Returns:
            Dictionary with loc, comment_lines, blank_lines, total_lines
        """
        lines = source_code.split('\n')
        total_lines = len(lines)
        blank_lines = 0
        comment_lines = 0
        
        # Get comment patterns for language
        comment_patterns = self._get_comment_patterns(language)
        
        for line in lines:
            stripped = line.strip()
            
            # Check for blank line
            if not stripped:
                blank_lines += 1
                continue
            
            # Check for comment line
            is_comment = False
            for pattern in comment_patterns:
                if pattern.match(stripped):
                    comment_lines += 1
                    is_comment = True
                    break
            
            # For COBOL fixed format, check column 7 for comment indicator
            if language.upper() == 'COBOL' and len(line) >= 7:
                if line[6] in ('*', '/'):
                    if not is_comment:  # Don't double count
                        comment_lines += 1
        
        # Calculate LOC
        loc = total_lines - blank_lines - comment_lines
        
        return {
            'loc': loc,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'total_lines': total_lines
        }
    
    def _get_comment_patterns(self, language: str) -> List[re.Pattern]:
        """
        Get comment patterns for a language.
        
        Args:
            language: Programming language
            
        Returns:
            List of compiled regex patterns for comments
        """
        language_upper = language.upper()
        
        if language_upper == 'COBOL':
            return [
                re.compile(r'^\*'),  # * in column 1 (after strip)
                re.compile(r'^/'),   # / in column 1
            ]
        elif language_upper == 'PLI':
            return [
                re.compile(r'^/\*'),  # /* comment start
                re.compile(r'^\*'),   # * continuation
            ]
        elif language_upper == 'JCL':
            return [
                re.compile(r'^//\*'),  # //* comment
            ]
        elif language_upper in ('REXX', 'CLIST'):
            return [
                re.compile(r'^/\*'),  # /* comment
            ]
        elif language_upper == 'NATURAL':
            return [
                re.compile(r'^\*'),   # * comment
                re.compile(r'^/\*'),  # /* comment
            ]
        else:
            # Default patterns
            return [
                re.compile(r'^//'),   # // comment
                re.compile(r'^#'),    # # comment
                re.compile(r'^/\*'),  # /* comment
                re.compile(r'^\*'),   # * comment
            ]
    
    def calculate_cyclomatic_complexity(self, source_code: str, language: str) -> int:
        """
        Calculate cyclomatic complexity.
        
        Cyclomatic complexity = E - N + 2P
        Where:
        - E = number of edges in control flow graph
        - N = number of nodes
        - P = number of connected components (usually 1)
        
        Simplified approach: Count decision points + 1
        Decision points include: IF, WHILE, FOR, CASE, AND, OR, etc.
        
        Args:
            source_code: Source code content
            language: Programming language
            
        Returns:
            Cyclomatic complexity score
        """
        language_upper = language.upper()
        
        if language_upper == 'COBOL':
            return self._calculate_cobol_complexity(source_code)
        elif language_upper == 'PLI':
            return self._calculate_pli_complexity(source_code)
        elif language_upper == 'JCL':
            return self._calculate_jcl_complexity(source_code)
        elif language_upper == 'NATURAL':
            return self._calculate_natural_complexity(source_code)
        else:
            # Default: count basic control flow keywords
            return self._calculate_default_complexity(source_code)
    
    def _calculate_cobol_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for COBOL.
        
        Decision points in COBOL:
        - IF statements
        - EVALUATE statements (WHEN clauses)
        - PERFORM UNTIL/VARYING
        - SEARCH/SEARCH ALL (WHEN clauses)
        - AND/OR in conditions
        
        Args:
            source_code: COBOL source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code (uppercase for pattern matching)
        normalized = source_code.upper()
        
        # Count IF statements (but not END-IF)
        # Use negative lookbehind to exclude END-IF
        complexity += len(re.findall(r'(?<!END-)(?<!ELSE\s)\bIF\b', normalized))
        
        # Count EVALUATE statements (each WHEN adds complexity)
        complexity += len(re.findall(r'\bWHEN\b', normalized))
        
        # Count PERFORM UNTIL/VARYING
        complexity += len(re.findall(r'\bPERFORM\s+(?:UNTIL|VARYING)\b', normalized))
        
        # Count SEARCH WHEN clauses
        complexity += len(re.findall(r'\bSEARCH\b', normalized))
        
        # Count logical operators (AND, OR) - each adds a decision point
        complexity += len(re.findall(r'\bAND\b', normalized))
        complexity += len(re.findall(r'\bOR\b', normalized))
        
        return complexity
    
    def _calculate_pli_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for PL/I.
        
        Decision points in PL/I:
        - IF statements
        - DO WHILE/UNTIL
        - SELECT/WHEN statements
        - DO loops with conditions
        - & (AND) and | (OR) operators
        
        Args:
            source_code: PL/I source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code
        normalized = source_code.upper()
        
        # Count IF statements
        complexity += len(re.findall(r'\bIF\b', normalized))
        
        # Count DO WHILE/UNTIL
        complexity += len(re.findall(r'\bDO\s+(?:WHILE|UNTIL)\b', normalized))
        
        # Count SELECT/WHEN statements
        complexity += len(re.findall(r'\bWHEN\b', normalized))
        
        # Count logical operators
        complexity += len(re.findall(r'&', normalized))  # AND
        complexity += len(re.findall(r'\|', normalized))  # OR
        
        return complexity
    
    def _calculate_jcl_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for JCL.
        
        Decision points in JCL:
        - IF/THEN/ELSE statements
        - COND parameters on EXEC statements
        
        Args:
            source_code: JCL source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code
        normalized = source_code.upper()
        
        # Count IF statements
        complexity += len(re.findall(r'//\s*IF\b', normalized))
        
        # Count COND parameters (conditional execution)
        complexity += len(re.findall(r'\bCOND=', normalized))
        
        return complexity
    def _calculate_natural_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for Natural (Software AG).

        Decision points in Natural:
        - IF / DECIDE ON / DECIDE FOR
        - FOR / REPEAT / READ / FIND / HISTOGRAM (loops)
        - WHEN (case branches)
        - AND / OR (compound conditions)

        Args:
            source_code: Natural source code

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity

        # Remove comment lines
        clean_lines = []
        for line in source_code.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('*') and not stripped.startswith('/*'):
                clean_lines.append(stripped.upper())

        normalized = '\n'.join(clean_lines)

        keywords = [
            r'\bIF\b', r'\bDECIDE\b', r'\bFOR\b', r'\bREPEAT\b',
            r'\bREAD\b', r'\bFIND\b', r'\bHISTOGRAM\b',
            r'\bWHEN\b', r'\bAND\b', r'\bOR\b',
        ]

        for pattern in keywords:
            complexity += len(re.findall(pattern, normalized))

        return complexity
    
    def _calculate_default_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for unknown languages.
        
        Uses generic control flow keywords.
        
        Args:
            source_code: Source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Normalize source code
        normalized = source_code.upper()
        
        # Count common control flow keywords
        keywords = ['IF', 'WHILE', 'FOR', 'CASE', 'WHEN', 'AND', 'OR']
        
        for keyword in keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', normalized))
        
        return complexity
    
    def save_metrics(self, metrics: ComplexityMetrics) -> None:
        """
        Save complexity metrics to database.
        
        Uses INSERT OR REPLACE to handle duplicate program names gracefully.
        
        Args:
            metrics: ComplexityMetrics object to save
        """
        if not self.database:
            raise ValueError("Database connection required to save metrics")
        
        # Use INSERT OR REPLACE to handle duplicates
        cursor = self.database.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO complexity_metrics (
                program_name,
                lines_of_code,
                total_lines,
                cyclomatic_complexity,
                dependency_count_in,
                dependency_count_out,
                composite_score,
                complexity_tier,
                language_factor,
                is_god_program,
                analyzed_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            metrics.program_name,
            metrics.lines_of_code,
            metrics.total_lines,
            metrics.cyclomatic_complexity,
            metrics.dependency_count_in,
            metrics.dependency_count_out,
            metrics.composite_score,
            metrics.complexity_tier,
            metrics.language_factor,
            1 if metrics.is_god_program else 0
        ))
        self.database.commit()
    
    def load_metrics(self, program_name: str) -> Optional[ComplexityMetrics]:
        """
        Load complexity metrics from database.
        
        Args:
            program_name: Name of the program
            
        Returns:
            ComplexityMetrics object or None if not found
        """
        if not self.database:
            raise ValueError("Database connection required to load metrics")
        
        # Query database
        # Note: This assumes the database has a query method
        # Implementation depends on actual database interface
        raise NotImplementedError("Load metrics requires database query interface")
    
    def create_schema(self) -> None:
        """Create complexity_metrics table in database."""
        if not self.database:
            raise ValueError("Database connection required to create schema")
        
        # Define table schema in the format expected by the database adapter
        table_def = {
            'columns': [
                {'name': 'program_name', 'type': 'VARCHAR(44)', 'primary_key': True},
                {'name': 'lines_of_code', 'type': 'INTEGER'},  # Executable code lines (total - comments - blanks)
                {'name': 'total_lines', 'type': 'INTEGER'},
                {'name': 'cyclomatic_complexity', 'type': 'INTEGER'},
                {'name': 'dependency_count_in', 'type': 'INTEGER'},
                {'name': 'dependency_count_out', 'type': 'INTEGER'},
                {'name': 'composite_score', 'type': 'REAL'},
                {'name': 'complexity_tier', 'type': 'VARCHAR(10)'},
                {'name': 'language_factor', 'type': 'REAL'},
                {'name': 'is_god_program', 'type': 'INTEGER'},  # SQLite uses INTEGER for BOOLEAN
                {'name': 'analyzed_date', 'type': 'TEXT', 'default': "CURRENT_TIMESTAMP"}
            ],
            'indexes': [
                {'name': 'idx_complexity_tier', 'columns': ['complexity_tier']},
                {'name': 'idx_composite_score', 'columns': ['composite_score']},
                {'name': 'idx_god_program', 'columns': ['is_god_program']},
                {'name': 'idx_lines_of_code', 'columns': ['lines_of_code']}
            ]
        }
        
        self.database.create_table('complexity_metrics', table_def)
        self.database.commit()
