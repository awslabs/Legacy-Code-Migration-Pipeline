"""Assembler complexity calculator."""

import re
from typing import Dict
from .base_complexity_calculator import BaseComplexityCalculator


class ASMComplexityCalculator(BaseComplexityCalculator):
    """Calculates complexity metrics for IBM z/OS Assembler code."""
    
    def __init__(self):
        """Initialize Assembler complexity calculator with patterns."""
        # Branch instructions (decision points)
        self.branch_instructions = {
            # Conditional branches
            'BC', 'BCR', 'BCT', 'BCTR', 'BXH', 'BXLE',
            'BE', 'BNE', 'BH', 'BL', 'BNH', 'BNL',
            'BZ', 'BNZ', 'BP', 'BM', 'BO', 'BNO',
            'BER', 'BNER', 'BHR', 'BLR', 'BNHR', 'BNLR',
            'BZR', 'BNZR', 'BPR', 'BMR', 'BOR', 'BNOR',
            # Extended branches
            'BRC', 'BRCL', 'BRCT', 'BRCTG', 'BRXH', 'BRXHG', 'BRXLE', 'BRXLG',
            'JE', 'JNE', 'JH', 'JL', 'JNH', 'JNL', 'JZ', 'JNZ',
            # Compare and branch
            'CRJ', 'CGRJ', 'CIJ', 'CGIJ', 'CLRJ', 'CLGRJ', 'CLIJ', 'CLGIJ',
            'CRB', 'CGRB', 'CIB', 'CGIB', 'CLRB', 'CLGRB', 'CLIB', 'CLGIB'
        }
        
        # Compare instructions (potential decision points)
        self.compare_instructions = {
            'C', 'CR', 'CH', 'CL', 'CLR', 'CLI', 'CLC', 'CLCL',
            'CG', 'CGR', 'CGH', 'CGHI', 'CLG', 'CLGR', 'CLGF',
            'CP', 'CDS', 'CDSG', 'CS', 'CSG', 'CSY'
        }
        
        # Loop-related instructions
        self.loop_instructions = {
            'BCT', 'BCTR', 'BXH', 'BXLE',
            'BRCT', 'BRCTG', 'BRXH', 'BRXHG', 'BRXLE', 'BRXLG'
        }
    
    def calculate_loc_metrics(self, source_code: str) -> Dict[str, int]:
        """
        Calculate lines of code metrics for Assembler.
        
        Args:
            source_code: Assembler source code
            
        Returns:
            Dictionary with loc, comment_lines, blank_lines, total_lines
        """
        lines = source_code.split('\n')
        total_lines = len(lines)
        comment_lines = 0
        blank_lines = 0
        code_lines = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Blank line
            if not stripped:
                blank_lines += 1
            # Full-line comment (starts with *)
            elif stripped.startswith('*'):
                comment_lines += 1
            # Code line (may have inline comment)
            else:
                code_lines += 1
                # Check for inline comment
                # In Assembler, comments typically start after column 40 or with *
                if '*' in line:
                    # Simple heuristic: if * appears after some content, it's likely a comment
                    before_star = line.split('*')[0].strip()
                    if not before_star:
                        # Actually a full-line comment
                        comment_lines += 1
                        code_lines -= 1
        
        return {
            'loc': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'total_lines': total_lines
        }
    
    def calculate_cyclomatic_complexity(self, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for Assembler.
        
        Counts:
        - Conditional branch instructions (BE, BNE, BH, BL, etc.)
        - Loop instructions (BCT, BCTR, BXH, BXLE)
        - Compare instructions followed by branches
        
        Base complexity is 1 (single path through program).
        Each decision point adds 1.
        
        Args:
            source_code: Assembler source code
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Remove comments for cleaner parsing
        normalized_code = self._remove_comments(source_code)
        
        # Pattern to match instruction lines
        # Format: [label] instruction [operands] [comment]
        instruction_pattern = re.compile(
            r'^\s*(?:[A-Z0-9@#$]+\s+)?([A-Z][A-Z0-9]*)\s+',
            re.MULTILINE | re.IGNORECASE
        )
        
        for match in instruction_pattern.finditer(normalized_code):
            instruction = match.group(1).upper()
            
            # Count branch instructions (decision points)
            if instruction in self.branch_instructions:
                complexity += 1
            
            # Count loop instructions (additional complexity)
            elif instruction in self.loop_instructions:
                complexity += 1
        
        return complexity
    
    def _remove_comments(self, source_code: str) -> str:
        """
        Remove comments from Assembler source.
        
        Args:
            source_code: Raw source code
            
        Returns:
            Source code without comments
        """
        lines = []
        for line in source_code.split('\n'):
            # Skip full-line comments
            if line.strip().startswith('*'):
                continue
            
            # Remove inline comments
            if '*' in line:
                # Find comment start (but not in quoted strings)
                in_quote = False
                for i, char in enumerate(line):
                    if char == "'":
                        in_quote = not in_quote
                    elif char == '*' and not in_quote and i > 0:
                        line = line[:i]
                        break
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def calculate_halstead_metrics(self, source_code: str) -> Dict[str, float]:
        """
        Calculate Halstead complexity metrics for Assembler.
        
        Operators: Instructions (LOAD, STORE, ADD, etc.)
        Operands: Registers, memory addresses, literals
        
        Args:
            source_code: Assembler source code
            
        Returns:
            Dictionary with Halstead metrics
        """
        normalized_code = self._remove_comments(source_code)
        
        operators = set()  # Unique instructions
        operands = set()   # Unique operands
        operator_count = 0
        operand_count = 0
        
        # Pattern to match instruction lines
        instruction_pattern = re.compile(
            r'^\s*(?:[A-Z0-9@#$]+\s+)?([A-Z][A-Z0-9]*)\s+(.+)?$',
            re.MULTILINE | re.IGNORECASE
        )
        
        for match in instruction_pattern.finditer(normalized_code):
            instruction = match.group(1).upper()
            operands_str = match.group(2)
            
            # Count operator (instruction)
            operators.add(instruction)
            operator_count += 1
            
            # Count operands
            if operands_str:
                # Split operands by comma
                for operand in operands_str.split(','):
                    operand = operand.strip()
                    if operand:
                        operands.add(operand)
                        operand_count += 1
        
        # Calculate Halstead metrics
        n1 = len(operators)  # Unique operators
        n2 = len(operands)   # Unique operands
        N1 = operator_count  # Total operators
        N2 = operand_count   # Total operands
        
        # Avoid division by zero
        if n1 == 0 or n2 == 0:
            return {
                'vocabulary': 0,
                'length': 0,
                'volume': 0,
                'difficulty': 0,
                'effort': 0
            }
        
        import math
        
        vocabulary = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = difficulty * volume
        
        return {
            'vocabulary': vocabulary,
            'length': length,
            'volume': volume,
            'difficulty': difficulty,
            'effort': effort,
            'unique_operators': n1,
            'unique_operands': n2,
            'total_operators': N1,
            'total_operands': N2
        }
    
    def calculate_all_metrics(self, source_code: str) -> Dict[str, any]:
        """
        Calculate all complexity metrics for Assembler.
        
        Args:
            source_code: Assembler source code
            
        Returns:
            Dictionary with all metrics
        """
        return {
            'loc_metrics': self.calculate_loc_metrics(source_code),
            'cyclomatic_complexity': self.calculate_cyclomatic_complexity(source_code),
            'halstead_metrics': self.calculate_halstead_metrics(source_code)
        }
