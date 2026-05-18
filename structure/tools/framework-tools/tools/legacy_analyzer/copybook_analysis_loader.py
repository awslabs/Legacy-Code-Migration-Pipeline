"""Copybook analysis loader for storing copybook analysis results in database."""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

from .models.program_boundary import CopybookAnalysisResult


class CopybookAnalysisLoader:
    """Loads copybook analysis results into database tables."""
    
    def __init__(self, database: BaseDatabase):
        """Initialize copybook analysis loader.
        
        Args:
            database: Database adapter instance
        """
        self.database = database
        self.stats = defaultdict(int)
    
    def store_copybook_analysis(self, analysis_results: List[CopybookAnalysisResult]) -> Dict[str, int]:
        """Store copybook analysis results in database.
        
        Args:
            analysis_results: List of copybook analysis results
            
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            'processed': 0,
            'stored': 0,
            'skipped': 0,
            'errors': 0
        }
        
        if not analysis_results:
            return stats
        
        print(f"\n=== Storing Copybook Analysis Results ===")
        print(f"Processing {len(analysis_results)} copybook analysis results...")
        
        try:
            # Prepare batch data for insertion
            rows_to_insert = []
            
            for result in analysis_results:
                stats['processed'] += 1
                
                try:
                    # Convert analysis result to database row
                    row_data = self._convert_to_row_data(result)
                    if row_data:
                        rows_to_insert.append(row_data)
                        stats['stored'] += 1
                    else:
                        stats['skipped'] += 1
                        
                except Exception as e:
                    print(f"  ⚠ Warning: Error processing {result.copybook_name}: {str(e)}")
                    stats['errors'] += 1
            
            # Batch insert all rows
            if rows_to_insert:
                self.database.insert_rows('copybook_analysis', rows_to_insert)
                self.database.commit()
                print(f"✓ Stored {len(rows_to_insert)} copybook analysis results")
            else:
                print("✓ No copybook analysis results to store")
                
        except Exception as e:
            self.database.rollback()
            print(f"  ✗ Error: Failed to store copybook analysis: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    def bulk_insert_copybook_analysis(self, 
                                    copybook_data: List[Dict[str, Any]], 
                                    skip_duplicates: bool = True) -> Dict[str, int]:
        """Bulk insert copybook analysis records for performance.
        
        Args:
            copybook_data: List of copybook analysis dictionaries
            skip_duplicates: If True, skip duplicate entries; if False, update them
            
        Returns:
            Dictionary with load statistics
        """
        rows_to_insert = []
        stats = {
            'processed': 0,
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for idx, data in enumerate(copybook_data):
            stats['processed'] += 1
            
            try:
                # Validate record structure
                if not isinstance(data, dict):
                    stats['skipped'] += 1
                    continue
                
                # Build row data for copybook_analysis table
                row_data = {
                    'copybook_name': str(data.get('copybook_name', '')).strip()[:100],
                    'file_path': str(data.get('file_path', '')).strip()[:255],
                    'has_executable_code': bool(data.get('has_executable_code', False)),
                    'data_structures': json.dumps(data.get('data_structures', [])),
                    'procedure_calls': json.dumps(data.get('procedure_calls', [])),
                    'confidence_level': float(data.get('confidence_level', 0.0)),
                    'language': str(data.get('language', '')).strip()[:20] or None,
                    'analysis_notes': str(data.get('analysis_notes', '')).strip()[:500] or None
                }
                
                # Validate required fields
                if not all([
                    row_data['copybook_name'],
                    row_data['file_path']
                ]):
                    stats['skipped'] += 1
                    continue
                
                # Check for duplicates
                cursor = self.database.cursor
                cursor.execute(
                    """SELECT id FROM copybook_analysis 
                       WHERE copybook_name = ? AND file_path = ?""",
                    (row_data['copybook_name'], row_data['file_path'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    if skip_duplicates:
                        stats['skipped'] += 1
                        continue
                    else:
                        # Update existing record
                        cursor.execute(
                            "DELETE FROM copybook_analysis WHERE id = ?",
                            (existing[0],)
                        )
                        stats['updated'] += 1
                
                rows_to_insert.append(row_data)
                stats['inserted'] += 1
                
                # Batch insert every 1000 rows
                if len(rows_to_insert) >= 1000:
                    self.database.insert_rows('copybook_analysis', rows_to_insert)
                    self.database.commit()
                    rows_to_insert = []
            
            except Exception as e:
                stats['errors'] += 1
                continue
        
        # Insert remaining rows
        if rows_to_insert:
            self.database.insert_rows('copybook_analysis', rows_to_insert)
            self.database.commit()
        
        return stats
    
    def get_copybook_analysis_summary(self) -> Dict[str, Any]:
        """Get summary statistics of stored copybook analysis."""
        cursor = self.database.cursor
        
        try:
            # Total copybooks analyzed
            cursor.execute("SELECT COUNT(*) FROM copybook_analysis")
            total_copybooks = cursor.fetchone()[0]
            
            # Copybooks with executable code
            cursor.execute("SELECT COUNT(*) FROM copybook_analysis WHERE has_executable_code = 1")
            executable_copybooks = cursor.fetchone()[0]
            
            # Data-only copybooks
            data_only_copybooks = total_copybooks - executable_copybooks
            
            # Average confidence level
            cursor.execute("SELECT AVG(confidence_level) FROM copybook_analysis")
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            # Language breakdown
            cursor.execute("""
                SELECT language, COUNT(*) 
                FROM copybook_analysis 
                WHERE language IS NOT NULL 
                GROUP BY language 
                ORDER BY COUNT(*) DESC
            """)
            language_breakdown = dict(cursor.fetchall())
            
            return {
                'total_copybooks': total_copybooks,
                'executable_copybooks': executable_copybooks,
                'data_only_copybooks': data_only_copybooks,
                'executable_percentage': (executable_copybooks / max(total_copybooks, 1)) * 100,
                'average_confidence': avg_confidence,
                'language_breakdown': language_breakdown
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _convert_to_row_data(self, result: CopybookAnalysisResult) -> Optional[Dict[str, Any]]:
        """Convert CopybookAnalysisResult to database row data.
        
        Args:
            result: Copybook analysis result
            
        Returns:
            Dictionary with row data or None if invalid
        """
        try:
            # Validate required fields
            if not result.copybook_name or not result.file_path:
                return None
            
            return {
                'copybook_name': result.copybook_name[:100],
                'file_path': result.file_path[:255],
                'has_executable_code': result.has_executable_code,
                'data_structures': json.dumps(result.data_structures),
                'procedure_calls': json.dumps(result.procedure_calls),
                'confidence_level': result.confidence_level,
                'language': result.language[:20] if result.language else None,
                'analysis_notes': result.analysis_notes[:500] if result.analysis_notes else None
            }
            
        except Exception:
            return None