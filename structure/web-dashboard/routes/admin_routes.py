"""
Admin routes for file management
"""

import os
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify

# Configure logging
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Allowed directories for admin access
ALLOWED_DIRECTORIES = {
    'agents': PROJECT_ROOT / 'agents',
    'input': PROJECT_ROOT / 'input', 
    'prompts': PROJECT_ROOT / 'prompts',
    'config': PROJECT_ROOT  # Root directory for config files
}

@admin_bp.route('/admin')
def admin_panel():
    """Render admin panel page"""
    return render_template('admin.html')

@admin_bp.route('/api/admin/directory/<directory>')
def get_directory_files(directory):
    """Get files in a directory"""
    try:
        if directory not in ALLOWED_DIRECTORIES:
            return jsonify({'success': False, 'error': 'Directory not allowed'})
        
        dir_path = ALLOWED_DIRECTORIES[directory]
        if not dir_path.exists():
            return jsonify({'success': False, 'error': 'Directory not found'})
        
        if directory in ['input', 'prompts']:
            # For input and prompts directories, return tree structure
            tree = build_directory_tree(dir_path)
            return jsonify({'success': True, 'tree': tree, 'view_type': 'tree'})
        elif directory == 'config':
            # For config directory, return only config files in root
            files = []
            config_files = ['project-config.json', 'project-config.json.example']
            
            for filename in config_files:
                file_path = dir_path / filename
                if file_path.exists() and file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'file'
                    })
            
            return jsonify({'success': True, 'files': files, 'view_type': 'list'})
        else:
            # For agents directory, return flat file list
            files = []
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    # Get relative path from directory root
                    relative_path = file_path.relative_to(dir_path)
                    
                    # Get file stats
                    stat = file_path.stat()
                    
                    files.append({
                        'name': str(relative_path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'file'
                    })
            
            # Sort files by name
            files.sort(key=lambda x: x['name'])
            
            return jsonify({'success': True, 'files': files, 'view_type': 'list'})
        
    except Exception as e:
        logger.error(f"Error in get_directory_files: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'An internal error has occurred'}), 500

def build_directory_tree(root_path, max_depth=10):
    """Build a tree structure of directories and files"""
    def build_node(path, current_depth=0):
        if current_depth > max_depth:
            return None
            
        node = {
            'name': path.name,
            'path': str(path.relative_to(root_path)),
            'type': 'directory' if path.is_dir() else 'file',
            'children': []
        }
        
        if path.is_file():
            stat = path.stat()
            node.update({
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        elif path.is_dir() and current_depth < max_depth:
            try:
                children = []
                # Get directories first, then files
                dirs = [p for p in path.iterdir() if p.is_dir() and not p.name.startswith('.')]
                files = [p for p in path.iterdir() if p.is_file() and not p.name.startswith('.')]
                
                # Sort both lists
                dirs.sort(key=lambda x: x.name.lower())
                files.sort(key=lambda x: x.name.lower())
                
                # Add directories first
                for child_path in dirs:
                    child_node = build_node(child_path, current_depth + 1)
                    if child_node:
                        children.append(child_node)
                
                # Add files
                for child_path in files:
                    child_node = build_node(child_path, current_depth + 1)
                    if child_node:
                        children.append(child_node)
                
                node['children'] = children
                node['file_count'] = len(files)
                node['dir_count'] = len(dirs)
            except PermissionError:
                pass
        
        return node
    
    return build_node(root_path)

@admin_bp.route('/api/admin/counts')
def get_directory_counts():
    """Get file counts for each directory"""
    try:
        counts = {}
        
        for dir_name, dir_path in ALLOWED_DIRECTORIES.items():
            if dir_path.exists():
                count = sum(1 for f in dir_path.rglob('*') if f.is_file())
                counts[dir_name] = count
            else:
                counts[dir_name] = 0
        
        return jsonify({'success': True, 'counts': counts})
        
    except Exception as e:
        logger.error(f"Error in get_directory_counts: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'An internal error has occurred'}), 500

@admin_bp.route('/api/admin/file/<directory>/<path:filename>', methods=['GET'])
def get_file_content(directory, filename):
    """Get file content"""
    try:
        if directory not in ALLOWED_DIRECTORIES:
            return jsonify({'success': False, 'error': 'Directory not allowed'})
        
        file_path = ALLOWED_DIRECTORIES[directory] / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'File not found'})
        
        # Check if file is within allowed directory (security check)
        if not str(file_path.resolve()).startswith(str(ALLOWED_DIRECTORIES[directory].resolve())):
            return jsonify({'success': False, 'error': 'Access denied'})
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({'success': True, 'content': content})
        
    except Exception as e:
        logger.error(f"Error in get_file_content: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'An internal error has occurred'}), 500

@admin_bp.route('/api/admin/file/<directory>/<path:filename>', methods=['PUT'])
def save_file_content(directory, filename):
    """Save file content"""
    try:
        if directory not in ALLOWED_DIRECTORIES:
            return jsonify({'success': False, 'error': 'Directory not allowed'})
        
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'success': False, 'error': 'No content provided'})
        
        file_path = ALLOWED_DIRECTORIES[directory] / filename
        
        # Check if file is within allowed directory (security check)
        if not str(file_path.resolve()).startswith(str(ALLOWED_DIRECTORIES[directory].resolve())):
            return jsonify({'success': False, 'error': 'Access denied'})
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error in save_file_content: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'An internal error has occurred'}), 500

@admin_bp.route('/api/admin/file/<directory>/<path:filename>', methods=['POST'])
def create_file(directory, filename):
    """Create new file"""
    try:
        if directory not in ALLOWED_DIRECTORIES:
            return jsonify({'success': False, 'error': 'Directory not allowed'})
        
        data = request.get_json()
        content = data.get('content', '') if data else ''
        
        file_path = ALLOWED_DIRECTORIES[directory] / filename
        
        # Check if file already exists
        if file_path.exists():
            return jsonify({'success': False, 'error': 'File already exists'})
        
        # Check if file is within allowed directory (security check)
        if not str(file_path.resolve()).startswith(str(ALLOWED_DIRECTORIES[directory].resolve())):
            return jsonify({'success': False, 'error': 'Access denied'})
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error in create_file: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'An internal error has occurred'}), 500

@admin_bp.route('/api/admin/file/<directory>/<path:filename>', methods=['DELETE'])
def delete_file(directory, filename):
    """Delete file"""
    try:
        if directory not in ALLOWED_DIRECTORIES:
            return jsonify({'success': False, 'error': 'Directory not allowed'})
        
        file_path = ALLOWED_DIRECTORIES[directory] / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'File not found'})
        
        # Check if file is within allowed directory (security check)
        if not str(file_path.resolve()).startswith(str(ALLOWED_DIRECTORIES[directory].resolve())):
            return jsonify({'success': False, 'error': 'Access denied'})
        
        file_path.unlink()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error in delete_file: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': 'An internal error has occurred'}), 500