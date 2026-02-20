"""
API routes for the web dashboard
"""

from flask import Blueprint, jsonify, request, current_app, send_from_directory
from pathlib import Path
from datetime import datetime
import json
import csv

api_bp = Blueprint('api', __name__)

@api_bp.route('/overview')
def overview():
    """API endpoint for project overview"""
    return jsonify(current_app.data_loader.get_project_overview())

@api_bp.route('/phases')
def phases():
    """API endpoint for phase status"""
    return jsonify(current_app.data_loader.get_phase_status())

@api_bp.route('/flows')
def flows():
    """API endpoint for business flows"""
    return jsonify(current_app.data_loader.get_business_flows())

@api_bp.route('/workpackages')
def workpackages():
    """API endpoint for workpackages"""
    return jsonify(current_app.data_loader.get_workpackages())

@api_bp.route('/files')
def files():
    """API endpoint for generated files"""
    return jsonify(current_app.data_loader.get_generated_files())

@api_bp.route('/phase/<int:phase_id>')
def phase_detail(phase_id):
    """API endpoint for detailed phase information"""
    try:
        phase_details = current_app.data_loader.get_phase_details(phase_id)
        return jsonify(phase_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/file/content')
def file_content():
    """API endpoint for file content preview"""
    try:
        file_path = request.args.get('path')
        language = request.args.get('language', 'ko')  # Default to Korean
        
        if not file_path:
            return jsonify({"error": "File path is required"}), 400
        
        # Security check - ensure file is within project directory
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = current_app.data_loader.project_root / file_path
        
        try:
            # Resolve to absolute path and check if it's within project directory
            resolved_path = full_path.resolve()
            project_root_resolved = current_app.data_loader.project_root.resolve()
            
            if not str(resolved_path).startswith(str(project_root_resolved)):
                return jsonify({"error": "Access denied: File outside project directory"}), 403
                
        except Exception:
            return jsonify({"error": "Invalid file path"}), 400
        
        if not resolved_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        if not resolved_path.is_file():
            return jsonify({"error": "Path is not a file"}), 400
        
        # Read file content
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(resolved_path, 'r', encoding='cp949') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return jsonify({"error": "Unable to decode file content"}), 400
        
        return jsonify({
            "file_name": resolved_path.name,
            "file_extension": resolved_path.suffix,
            "content": content,
            "path": str(resolved_path.relative_to(project_root_resolved))
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/dependency-graph')
def dependency_graph():
    """API endpoint for dependency graph data from SQLite database"""
    import sqlite3
    
    try:
        show_missing = request.args.get('showMissing', 'false').lower() == 'true'
        show_copybooks = request.args.get('showCopybooks', 'true').lower() == 'true'
        show_jcl = request.args.get('showJcl', 'true').lower() == 'true'
        show_external = request.args.get('showExternal', 'true').lower() == 'true'
        show_database = request.args.get('showDatabase', 'true').lower() == 'true'
        exclude_high_degree = request.args.get('excludeHighDegree', 'false').lower() == 'true'
        max_degree = int(request.args.get('maxDegree', '100'))
        exclude_nodes = request.args.get('excludeNodes', '').split(',') if request.args.get('excludeNodes') else []
        exclude_nodes = [node.strip() for node in exclude_nodes if node.strip()]
        
        # Connect to SQLite database
        db_path = current_app.data_loader.output_dir / "analysis" / "source_code" / "analysis.db"
        
        if not db_path.exists():
            return jsonify({"error": "Analysis database not found"}), 404
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First pass: collect all node information from inventory table
        node_info = {}
        
        # Get entry points from migration_flows
        entry_points = set()
        cursor.execute("SELECT DISTINCT entry_program FROM migration_flows")
        for row in cursor.fetchall():
            if row['entry_program']:
                entry_points.add(row['entry_program'])
        
        # Get all programs from inventory with metadata
        cursor.execute("""
            SELECT 
                i.artifact_name,
                i.artifact_type,
                i.is_entry_point,
                i.found,
                pm.classification,
                pm.is_utility,
                pm.call_count,
                cm.composite_score,
                cm.complexity_tier
            FROM inventory i
            LEFT JOIN program_metadata pm ON i.artifact_name = pm.program_name
            LEFT JOIN complexity_metrics cm ON i.artifact_name = cm.program_name
        """)
        
        for row in cursor.fetchall():
            name = row['artifact_name']
            item_type = row['artifact_type']
            found = row['found']
            
            # Map inventory type to node type
            if found == 0:
                # Any artifact not found in codebase is MISSING
                node_type = 'MISSING'
            elif item_type == 'COPYBOOK':
                node_type = 'COPYBOOK'
            elif item_type == 'JCL':
                node_type = 'JCL'
            elif item_type == 'PROGRAM':
                # Check if it's an entry point from migration_flows
                if name in entry_points:
                    node_type = 'ENTRY_POINT'
                # Determine if it's an entry point, commonly used, etc.
                elif row['is_entry_point']:
                    node_type = 'ENTRY_POINT'
                elif row['classification'] == 'UTILITY':
                    node_type = 'COMMONLY_USED'
                elif row['call_count'] is not None and row['call_count'] == 0:
                    node_type = 'UNUSED'
                else:
                    node_type = 'SINGLE_USE'
            elif item_type == 'FILE':
                node_type = 'DATABASE'
            else:
                node_type = 'EXTERNAL'
            
            node_info[name] = {
                "id": name,
                "type": node_type,
                "usage": row['classification'] or 'Unknown',
                "domain": 'Unknown',  # Not in current schema
                "moduleType": node_type,
                "functionality": item_type,
                "complexity": row['composite_score'] or 0,
                "complexityTier": row['complexity_tier'] or 'Unknown',
                "size": 10,
                "inDegree": 0,
                "outDegree": 0
            }
        
        # Add entry points from migration_flows that aren't in inventory
        # (system programs, external utilities, etc.)
        for entry_point in entry_points:
            if entry_point not in node_info:
                node_info[entry_point] = {
                    "id": entry_point,
                    "type": "ENTRY_POINT",
                    "usage": "System/External",
                    "domain": "Unknown",
                    "moduleType": "ENTRY_POINT",
                    "functionality": "EXTERNAL",
                    "complexity": 0,
                    "complexityTier": "Unknown",
                    "size": 10,
                    "inDegree": 0,
                    "outDegree": 0
                }
        
        # Get all dependencies (edges)
        edges = []
        cursor.execute("""
            SELECT 
                source_artifact_name,
                target_artifact_name,
                dependency_type
            FROM artifact_dependencies
            WHERE dependency_type != 'FILE_ACCESS'
        """)
        
        for row in cursor.fetchall():
            source = row['source_artifact_name']
            target = row['target_artifact_name']
            dep_type = row['dependency_type']
            
            if not source or not target:
                continue
            
            # Ensure source node exists
            if source not in node_info:
                node_info[source] = {
                    "id": source,
                    "type": "EXTERNAL",
                    "usage": "Unknown",
                    "domain": "Unknown",
                    "moduleType": "EXTERNAL",
                    "functionality": "Unknown",
                    "complexity": 0,
                    "size": 10,
                    "inDegree": 0,
                    "outDegree": 0
                }
            
            # Ensure target node exists and classify it
            if target not in node_info:
                # Determine target type based on dependency type
                if dep_type in ('SQL_TABLE', 'DATABASE', 'CICS_FILE'):
                    target_type = "DATABASE"
                elif dep_type == 'COPY':
                    target_type = "COPYBOOK"
                elif dep_type == 'CICS_TRANSACTION':
                    target_type = "EXTERNAL"
                elif target.startswith('TH'):
                    target_type = "DATABASE"
                else:
                    target_type = "EXTERNAL"
                
                node_info[target] = {
                    "id": target,
                    "type": target_type,
                    "usage": "Unknown",
                    "domain": "Unknown",
                    "moduleType": target_type,
                    "functionality": "Unknown",
                    "complexity": 0,
                    "size": 10,
                    "inDegree": 0,
                    "outDegree": 0
                }
            
            # Add edge
            edges.append({
                "source": source,
                "target": target,
                "type": dep_type
            })
        
        conn.close()
        
        # Calculate inDegree and outDegree for each node
        for edge in edges:
            source_id = edge["source"]
            target_id = edge["target"]
            
            # Update outDegree for source
            if source_id in node_info:
                node_info[source_id]["outDegree"] += 1
            
            # Update inDegree for target
            if target_id in node_info:
                node_info[target_id]["inDegree"] += 1
        
        # Convert node_info to nodes array and add totalDegree
        nodes = []
        for node in node_info.values():
            node["totalDegree"] = node["inDegree"] + node["outDegree"]
            nodes.append(node)
        
        # Apply filters
        filtered_nodes = []
        excluded_node_ids = set()
        
        for node in nodes:
            # Filter by specific node names
            if node["id"] in exclude_nodes:
                excluded_node_ids.add(node["id"])
                continue
                
            # Filter by node type
            if not show_missing and node["type"] == "MISSING":
                excluded_node_ids.add(node["id"])
                continue
            if not show_copybooks and node["type"] == "COPYBOOK":
                excluded_node_ids.add(node["id"])
                continue
            if not show_jcl and node["type"] == "JCL":
                excluded_node_ids.add(node["id"])
                continue
            if not show_external and node["type"] == "EXTERNAL":
                excluded_node_ids.add(node["id"])
                continue
            if not show_database and node["type"] == "DATABASE":
                excluded_node_ids.add(node["id"])
                continue
            
            # Filter by degree (exclude high-degree nodes)
            if exclude_high_degree and node["totalDegree"] > max_degree:
                excluded_node_ids.add(node["id"])
                continue
            
            filtered_nodes.append(node)
        
        # Filter edges to only include edges between remaining nodes
        filtered_edges = []
        for edge in edges:
            if edge["source"] not in excluded_node_ids and edge["target"] not in excluded_node_ids:
                filtered_edges.append(edge)
        
        # Sort nodes by totalDegree for easy identification of hubs
        nodes_sorted = sorted(filtered_nodes, key=lambda x: x["totalDegree"], reverse=True)
        
        return jsonify({
            "nodes": filtered_nodes,
            "edges": filtered_edges,
            "stats": {
                "totalNodes": len(filtered_nodes),
                "totalEdges": len(filtered_edges),
                "originalNodes": len(nodes),
                "originalEdges": len(edges),
                "excludedNodes": len(excluded_node_ids),
                "topNodes": nodes_sorted[:10]  # Top 10 most connected nodes
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/business-flows')
def business_flows():
    """API endpoint for business flow diagram data"""
    try:
        flows_data = current_app.data_loader.get_business_flows()
        
        # Transform for visualization
        flows = flows_data.get('flows', [])
        
        # Create nodes and edges for flow diagram
        nodes = []
        edges = []
        
        for flow in flows:
            flow_id = flow.get('id', '')
            entry_point = flow.get('entry_point', '')
            modules = flow.get('modules', [])
            
            # Add entry point node
            if entry_point:
                nodes.append({
                    "id": entry_point,
                    "label": entry_point,
                    "type": "entry_point",
                    "flowId": flow_id
                })
            
            # Add module nodes and edges
            prev_module = entry_point
            for module in modules:
                if module != entry_point:
                    nodes.append({
                        "id": module,
                        "label": module,
                        "type": "module",
                        "flowId": flow_id
                    })
                    
                    if prev_module:
                        edges.append({
                            "from": prev_module,
                            "to": module,
                            "flowId": flow_id
                        })
                    
                    prev_module = module
        
        return jsonify({
            "nodes": nodes,
            "edges": edges,
            "flows": flows
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/progress')
def progress():
    """API endpoint for detailed progress information"""
    try:
        from datetime import datetime
        progress_info = {
            "phases": current_app.data_loader.get_phase_status(),
            "overview": current_app.data_loader.get_project_overview(),
            "workpackages": current_app.data_loader.get_workpackage_progress(),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(progress_info)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/workpackage-progress')
def workpackage_progress():
    """API endpoint for workpackage progress statistics"""
    try:
        return jsonify(current_app.data_loader.get_workpackage_progress())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/workpackage/<workpackage_id>/cobol-files')
def workpackage_cobol_files(workpackage_id):
    """API endpoint for COBOL files associated with a workpackage"""
    
    try:
        # Get original entry module from progress data
        original_entry_module = None
        
        # Try to get from code generation progress
        code_progress_file = current_app.data_loader.migration_dir / "progress" / "04-code-generation-status.json"
        if code_progress_file.exists():
            with open(code_progress_file, 'r', encoding='utf-8') as f:
                code_data = json.load(f)
                
            for wp in code_data.get("workpackages", []):
                if wp.get("workpackageId") == workpackage_id:
                    original_entry_module = wp.get("originalEntryModule")
                    break
        
        cobol_files = current_app.data_loader.get_cobol_files_for_workpackage(
            workpackage_id, original_entry_module
        )
        

        return jsonify({
            "workpackageId": workpackage_id,
            "originalEntryModule": original_entry_module,
            "cobolFiles": cobol_files
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500