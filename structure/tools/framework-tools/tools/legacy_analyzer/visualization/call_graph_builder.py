"""
Call graph builder for visualization - compatibility wrapper.

This module provides a compatibility wrapper around the actual CallGraphBuilder
in the analysis module, adapting it for visualization and AI export needs.
"""

from typing import List, Dict, Set, Optional, Any
from ..analysis.call_graph import CallGraphBuilder as AnalysisCallGraphBuilder
from ..models.dependency import Dependency


class CallGraphBuilder:
    """
    Visualization-focused call graph builder.
    
    This is a wrapper around the analysis CallGraphBuilder that provides
    additional methods for AI export and visualization-specific functionality.
    """
    
    def __init__(self, database):
        """
        Initialize call graph builder with database connection.
        
        Args:
            database: Database connection or adapter
        """
        self.database = database
        self._dependencies = None
        self._program_file_mapping = None
        
        # Handle both raw connections and adapters
        if hasattr(database, 'cursor') and callable(database.cursor):
            self.cursor = database.cursor()
        elif hasattr(database, 'cursor'):
            self.cursor = database.cursor
        else:
            raise ValueError("Database must have a cursor attribute or method")
    
    def _load_dependencies(self) -> List[Dependency]:
        """Load dependencies from database."""
        if self._dependencies is not None:
            return self._dependencies
        
        dependencies = []
        
        try:
            self.cursor.execute("""
                SELECT source_artifact_name, source_artifact_type, target_artifact_name, 
                       target_artifact_type, dependency_type, source_file_path, line_number
                FROM artifact_dependencies
            """)
            
            for row in self.cursor.fetchall():
                dep = Dependency(
                    source_artifact=row[0],
                    source_type=row[1],
                    target_artifact=row[2],
                    target_type=row[3],
                    dependency_type=row[4],
                    source_file=row[5] or '',
                    line_number=row[6] or 0
                )
                dependencies.append(dep)
        
        except Exception as e:
            # Handle case where table doesn't exist
            print(f"Warning: Could not load dependencies: {e}")
        
        self._dependencies = dependencies
        return dependencies
    
    def _load_program_file_mapping(self) -> Dict[str, Dict]:
        """Load program-to-file mapping from database."""
        if self._program_file_mapping is not None:
            return self._program_file_mapping
        
        mapping = {}
        
        try:
            self.cursor.execute("""
                SELECT program_name, file_path, start_line, end_line, 
                       program_type, language, entry_points
                FROM program_file_mapping
            """)
            
            for row in self.cursor.fetchall():
                mapping[row[0]] = {
                    'file_path': row[1],
                    'start_line': row[2],
                    'end_line': row[3],
                    'program_type': row[4],
                    'language': row[5],
                    'entry_points': row[6]
                }
        
        except Exception as e:
            # Handle case where table doesn't exist
            print(f"Warning: Could not load program file mapping: {e}")
        
        self._program_file_mapping = mapping
        return mapping
    
    def build_program_call_graph(self, start_programs: List[str]):
        """
        Build call graph starting from specified programs.
        
        Args:
            start_programs: List of program names to start from
            
        Returns:
            CallGraph object
        """
        dependencies = self._load_dependencies()
        program_mapping = self._load_program_file_mapping()
        
        # Use the analysis CallGraphBuilder
        builder = AnalysisCallGraphBuilder(dependencies, program_mapping)
        return builder.build_call_graph(start_programs)
    
    def build_multi_language_call_graph(self, start_programs: List[str]):
        """
        Build call graph for multi-language scenarios.
        
        Args:
            start_programs: List of program names to start from
            
        Returns:
            CallGraph object with multi-language metadata
        """
        # For now, this is the same as regular call graph
        # Can be enhanced later for language-specific visualization
        return self.build_program_call_graph(start_programs)
    
    def export_for_ai_analysis(self) -> Dict[str, Any]:
        """
        Export call graph data in format suitable for AI analysis.
        
        Returns:
            Dictionary with nodes, edges, metadata, and statistics
        """
        dependencies = self._load_dependencies()
        program_mapping = self._load_program_file_mapping()
        
        # Build full call graph
        builder = AnalysisCallGraphBuilder(dependencies, program_mapping)
        call_graph = builder.build_full_call_graph()
        
        # Convert to AI-compatible format
        nodes = []
        edges = []
        
        # Create nodes from programs
        all_programs = set()
        for dep in dependencies:
            if dep.source_type == 'PROGRAM':
                all_programs.add(dep.source_artifact)
            if dep.target_type == 'PROGRAM':
                all_programs.add(dep.target_artifact)
        
        for program_name in all_programs:
            node_data = {
                'id': program_name,
                'program_name': program_name,
                'file_path': program_mapping.get(program_name, {}).get('file_path', ''),
                'program_type': program_mapping.get(program_name, {}).get('program_type', 'UNKNOWN'),
                'language': program_mapping.get(program_name, {}).get('language', 'UNKNOWN'),
                'start_line': program_mapping.get(program_name, {}).get('start_line', 0),
                'end_line': program_mapping.get(program_name, {}).get('end_line', 0),
                'complexity_score': 0.0  # Default, could be enhanced with actual complexity data
            }
            nodes.append(node_data)
        
        # Create edges from dependencies
        for dep in dependencies:
            if dep.source_type == 'PROGRAM' and dep.target_type == 'PROGRAM':
                edge_data = {
                    'source': dep.source_artifact,
                    'target': dep.target_artifact,
                    'dependency_type': str(dep.dependency_type),
                    'confidence': 1.0,  # Default confidence
                    'line_number': dep.line_number,
                    'call_context': 'direct'  # Default context
                }
                edges.append(edge_data)
        
        # Generate metadata
        languages = set()
        program_types = set()
        for mapping in program_mapping.values():
            if mapping.get('language'):
                languages.add(mapping['language'])
            if mapping.get('program_type'):
                program_types.add(mapping['program_type'])
        
        metadata = {
            'analysis_timestamp': '2024-01-01T00:00:00Z',  # Could be enhanced with actual timestamp
            'total_files': len(set(m.get('file_path', '') for m in program_mapping.values() if m.get('file_path'))),
            'total_programs': len(all_programs),
            'languages': list(languages),
            'program_types': list(program_types),
            'analysis_version': '1.0'
        }
        
        # Generate statistics
        language_counts = {}
        dependency_type_counts = {}
        
        for mapping in program_mapping.values():
            lang = mapping.get('language', 'UNKNOWN')
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        for dep in dependencies:
            dep_type = str(dep.dependency_type)
            dependency_type_counts[dep_type] = dependency_type_counts.get(dep_type, 0) + 1
        
        statistics = {
            'program_count_by_language': language_counts,
            'dependency_count_by_type': dependency_type_counts,
            'complexity_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'VERY_HIGH': 0},  # Default
            'file_program_mapping': {
                'total_files': metadata['total_files'],
                'total_programs': metadata['total_programs'],
                'avg_programs_per_file': metadata['total_programs'] / max(metadata['total_files'], 1)
            }
        }
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': metadata,
            'statistics': statistics
        }
    
    def export_multi_language_for_ai(self) -> Dict[str, Any]:
        """
        Export multi-language call graph data for AI analysis.
        
        Returns:
            Dictionary with enhanced multi-language statistics
        """
        base_data = self.export_for_ai_analysis()
        
        # Add multi-language specific statistics
        program_mapping = self._load_program_file_mapping()
        dependencies = self._load_dependencies()
        
        # Calculate cross-language dependencies
        cross_lang_deps = []
        for dep in dependencies:
            if dep.source_type == 'PROGRAM' and dep.target_type == 'PROGRAM':
                source_lang = program_mapping.get(dep.source_artifact, {}).get('language', 'UNKNOWN')
                target_lang = program_mapping.get(dep.target_artifact, {}).get('language', 'UNKNOWN')
                
                if source_lang != target_lang and source_lang != 'UNKNOWN' and target_lang != 'UNKNOWN':
                    cross_lang_deps.append({
                        'source_program': dep.source_artifact,
                        'target_program': dep.target_artifact,
                        'source_language': source_lang,
                        'target_language': target_lang,
                        'dependency_type': str(dep.dependency_type)
                    })
        
        # Create language interaction matrix
        languages = list(set(m.get('language', 'UNKNOWN') for m in program_mapping.values()))
        interaction_matrix = {}
        for source_lang in languages:
            interaction_matrix[source_lang] = {}
            for target_lang in languages:
                interaction_matrix[source_lang][target_lang] = 0
        
        for dep in cross_lang_deps:
            source_lang = dep['source_language']
            target_lang = dep['target_language']
            interaction_matrix[source_lang][target_lang] += 1
        
        # Add multi-language specific data
        base_data['cross_language_dependencies'] = cross_lang_deps
        base_data['language_interaction_matrix'] = interaction_matrix
        base_data['language_statistics'] = base_data['statistics']['program_count_by_language']
        
        return base_data