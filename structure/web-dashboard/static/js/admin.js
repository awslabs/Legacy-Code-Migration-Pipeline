/**
 * Admin Panel JavaScript
 * Handles file management for agents, input, and prompts directories
 */

class AdminPanel {
    constructor() {
        this.currentDirectory = 'agents';
        this.currentFile = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDirectory('agents');
        this.loadDirectoryCounts();
        this.loadProjectName();
    }

    setupEventListeners() {
        // Directory navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const directory = item.dataset.directory;
                this.switchDirectory(directory);
            });
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadDirectory(this.currentDirectory);
        });

        // New file button
        document.getElementById('new-file-btn').addEventListener('click', () => {
            this.showNewFileModal();
        });

        // Modal close buttons
        document.getElementById('close-editor-btn').addEventListener('click', () => {
            this.closeFileEditor();
        });

        document.getElementById('close-new-file-btn').addEventListener('click', () => {
            this.closeNewFileModal();
        });

        document.getElementById('cancel-new-file-btn').addEventListener('click', () => {
            this.closeNewFileModal();
        });

        // Save file button
        document.getElementById('save-file-btn').addEventListener('click', () => {
            this.saveFile();
        });

        // Create file button
        document.getElementById('create-file-btn').addEventListener('click', () => {
            this.createFile();
        });

        // Preview file button
        document.getElementById('preview-file-btn').addEventListener('click', () => {
            this.previewFile();
        });

        // Close preview button
        document.getElementById('close-preview-btn').addEventListener('click', () => {
            this.closePreview();
        });

        // Modal backdrop click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('show');
                }
            });
        });
    }

    switchDirectory(directory) {
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-directory="${directory}"]`).classList.add('active');

        // Update current directory
        this.currentDirectory = directory;
        document.getElementById('current-directory').textContent = directory;
        document.getElementById('current-path').textContent = `/${directory}`;

        // Load directory contents
        this.loadDirectory(directory);
    }

    async loadDirectory(directory) {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i> Loading files...</div>';

        try {
            const response = await fetch(`/api/admin/directory/${directory}`);
            const data = await response.json();

            if (data.success) {
                this.renderFileList(data);
            } else {
                fileList.innerHTML = `<div class="loading">Error: ${data.error}</div>`;
            }
        } catch (error) {
            console.error('Error loading directory:', error);
            fileList.innerHTML = '<div class="loading">Error loading files</div>';
        }
    }

    async loadDirectoryCounts() {
        try {
            const response = await fetch('/api/admin/counts');
            const data = await response.json();

            if (data.success) {
                document.getElementById('agents-count').textContent = data.counts.agents || 0;
                document.getElementById('input-count').textContent = data.counts.input || 0;
                document.getElementById('prompts-count').textContent = data.counts.prompts || 0;
            }
        } catch (error) {
            console.error('Error loading directory counts:', error);
        }
    }

    async loadProjectName() {
        try {
            const response = await fetch('/api/overview');
            const data = await response.json();
            
            if (data && data.projectName) {
                document.getElementById('admin-project-name').textContent = `Project: ${data.projectName}`;
                document.getElementById('admin-last-updated').textContent = `Last updated: ${this.formatDate(data.lastUpdated)}`;
            } else {
                document.getElementById('admin-project-name').textContent = 'Project: Migration Project';
                document.getElementById('admin-last-updated').textContent = 'Last updated: N/A';
            }
        } catch (error) {
            console.error('Error loading project name:', error);
            document.getElementById('admin-project-name').textContent = 'Project: Migration Project';
            document.getElementById('admin-last-updated').textContent = 'Last updated: N/A';
        }
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            
            // Format as YYYY-MM-DD HH:MM (24-hour format, locale-independent)
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            
            return `${year}-${month}-${day} ${hours}:${minutes}`;
        } catch (e) {
            return 'N/A';
        }
    }

    renderFileList(data) {
        const fileList = document.getElementById('file-list');
        
        if (data.view_type === 'tree') {
            this.renderTreeView(data.tree);
        } else {
            this.renderListView(data.files);
        }
    }

    renderListView(files) {
        const fileList = document.getElementById('file-list');
        
        // Show the file list header for list view
        const fileListHeader = document.querySelector('.file-list-header');
        if (fileListHeader) {
            fileListHeader.style.display = 'grid';
        }
        
        if (files.length === 0) {
            fileList.innerHTML = '<div class="loading">No files found</div>';
            return;
        }

        fileList.innerHTML = files.map(file => `
            <div class="file-item">
                <div class="file-name">
                    <i class="file-icon ${this.getFileIcon(file.name)}"></i>
                    ${file.name}
                </div>
                <div class="file-size">${this.formatFileSize(file.size)}</div>
                <div class="file-modified">${this.formatDate(file.modified)}</div>
                <div class="file-actions">
                    <button class="file-action-btn edit" onclick="adminPanel.editFile('${file.name}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="file-action-btn delete" onclick="adminPanel.deleteFile('${file.name}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderTreeView(tree) {
        const fileList = document.getElementById('file-list');
        
        // Hide the file list header for tree view
        const fileListHeader = document.querySelector('.file-list-header');
        if (fileListHeader) {
            fileListHeader.style.display = 'none';
        }
        
        fileList.innerHTML = `<div class="tree-view">${this.renderTreeNode(tree, 0, true)}</div>`;
        
        // Auto-expand first level directories after rendering
        setTimeout(() => {
            this.autoExpandFirstLevel();
        }, 100);
    }

    renderTreeNode(node, depth, isRoot = false) {
        const indent = depth * 20;
        let html = '';
        
        if (node.type === 'directory') {
            const hasChildren = node.children && node.children.length > 0;
            const fileCount = node.file_count || 0;
            const dirCount = node.dir_count || 0;
            const shouldAutoExpand = isRoot && depth === 0; // Auto-expand first level
            
            html += `
                <div class="tree-node directory" style="padding-left: ${indent}px">
                    <div class="tree-node-content" ${hasChildren ? 'onclick="adminPanel.toggleTreeNode(this)"' : ''}>
                        <div class="file-name">
                            <i class="tree-icon fas ${hasChildren ? (shouldAutoExpand ? 'fa-chevron-down' : 'fa-chevron-right') : ''}"></i>
                            <i class="folder-icon fas fa-folder"></i>
                            <span class="node-name">${node.name}</span>
                        </div>
                        <div class="node-info">(${dirCount} dirs, ${fileCount} files)</div>
                        <div class="node-modified"></div>
                        <div class="node-actions"></div>
                    </div>
                    ${hasChildren ? `<div class="tree-children" style="display: ${shouldAutoExpand ? 'block' : 'none'};">` : ''}
            `;
            
            if (hasChildren) {
                for (const child of node.children) {
                    html += this.renderTreeNode(child, depth + 1, false);
                }
            }
            
            html += hasChildren ? `
                    </div>
                </div>
            ` : `
                </div>
            `;
        } else {
            // File node
            html += `
                <div class="tree-node file" style="padding-left: ${indent}px">
                    <div class="tree-node-content">
                        <div class="file-name">
                            <i class="tree-icon"></i>
                            <i class="file-icon ${this.getFileIcon(node.name)}"></i>
                            <span class="node-name">${node.name}</span>
                        </div>
                        <div class="node-size">${this.formatFileSize(node.size)}</div>
                        <div class="node-modified">${this.formatDate(node.modified)}</div>
                        <div class="node-actions">
                            <button class="file-action-btn edit" onclick="adminPanel.editFile('${node.path}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="file-action-btn delete" onclick="adminPanel.deleteFile('${node.path}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return html;
    }

    toggleTreeNode(element) {
        const treeNode = element.closest('.tree-node');
        const children = treeNode.querySelector('.tree-children');
        const icon = element.querySelector('.tree-icon');
        
        if (children) {
            const isExpanded = children.style.display !== 'none';
            children.style.display = isExpanded ? 'none' : 'block';
            icon.className = `tree-icon fas ${isExpanded ? 'fa-chevron-right' : 'fa-chevron-down'}`;
        }
    }

    autoExpandFirstLevel() {
        // Auto-expand all first-level directories
        const firstLevelNodes = document.querySelectorAll('.tree-view > .tree-node.directory');
        firstLevelNodes.forEach(node => {
            const children = node.querySelector('.tree-children');
            const icon = node.querySelector('.tree-icon');
            
            if (children && icon) {
                children.style.display = 'block';
                icon.className = 'tree-icon fas fa-chevron-down';
            }
        });
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const iconMap = {
            'md': 'fab fa-markdown',
            'txt': 'fas fa-file-alt',
            'json': 'fas fa-file-code',
            'py': 'fab fa-python',
            'js': 'fab fa-js-square',
            'html': 'fab fa-html5',
            'css': 'fab fa-css3-alt',
            'yml': 'fas fa-file-code',
            'yaml': 'fas fa-file-code'
        };
        return iconMap[ext] || 'fas fa-file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    async editFile(filename) {
        try {
            const response = await fetch(`/api/admin/file/${this.currentDirectory}/${filename}`);
            const data = await response.json();

            if (data.success) {
                this.currentFile = filename;
                document.getElementById('editor-title').textContent = `Edit ${filename}`;
                document.getElementById('file-content').value = data.content;
                document.getElementById('file-editor-modal').classList.add('show');
            } else {
                alert(`Error loading file: ${data.error}`);
            }
        } catch (error) {
            console.error('Error loading file:', error);
            alert('Error loading file');
        }
    }

    async saveFile() {
        if (!this.currentFile) return;

        const content = document.getElementById('file-content').value;
        
        try {
            const response = await fetch(`/api/admin/file/${this.currentDirectory}/${this.currentFile}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content })
            });

            const data = await response.json();

            if (data.success) {
                alert('File saved successfully');
                this.closeFileEditor();
                this.loadDirectory(this.currentDirectory);
            } else {
                alert(`Error saving file: ${data.error}`);
            }
        } catch (error) {
            console.error('Error saving file:', error);
            alert('Error saving file');
        }
    }

    async deleteFile(filename) {
        if (!confirm(`Are you sure you want to delete ${filename}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/file/${this.currentDirectory}/${filename}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                alert('File deleted successfully');
                this.loadDirectory(this.currentDirectory);
                this.loadDirectoryCounts();
            } else {
                alert(`Error deleting file: ${data.error}`);
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            alert('Error deleting file');
        }
    }

    showNewFileModal() {
        document.getElementById('new-file-name').value = '';
        document.getElementById('new-file-content').value = '';
        document.getElementById('new-file-modal').classList.add('show');
    }

    closeNewFileModal() {
        document.getElementById('new-file-modal').classList.remove('show');
    }

    async createFile() {
        const filename = document.getElementById('new-file-name').value.trim();
        const content = document.getElementById('new-file-content').value;

        if (!filename) {
            alert('Please enter a filename');
            return;
        }

        try {
            const response = await fetch(`/api/admin/file/${this.currentDirectory}/${filename}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content })
            });

            const data = await response.json();

            if (data.success) {
                alert('File created successfully');
                this.closeNewFileModal();
                this.loadDirectory(this.currentDirectory);
                this.loadDirectoryCounts();
            } else {
                alert(`Error creating file: ${data.error}`);
            }
        } catch (error) {
            console.error('Error creating file:', error);
            alert('Error creating file');
        }
    }

    closeFileEditor() {
        document.getElementById('file-editor-modal').classList.remove('show');
        this.currentFile = null;
    }

    previewFile() {
        if (!this.currentFile) return;

        const content = document.getElementById('file-content').value;
        const fileExtension = this.getFileExtension(this.currentFile);
        
        document.getElementById('preview-title').textContent = `Preview: ${this.currentFile}`;
        
        this.renderPreview(content, fileExtension);
        document.getElementById('file-preview-modal').classList.add('show');
    }

    closePreview() {
        document.getElementById('file-preview-modal').classList.remove('show');
    }

    getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    renderPreview(content, extension) {
        const container = document.getElementById('preview-container');
        
        switch (extension) {
            case 'md':
                this.renderMarkdownPreview(content, container);
                break;
            case 'csv':
                this.renderCsvPreview(content, container);
                break;
            case 'json':
                this.renderJsonPreview(content, container);
                break;
            case 'js':
            case 'py':
            case 'java':
            case 'html':
            case 'css':
            case 'xml':
            case 'yml':
            case 'yaml':
                this.renderCodePreview(content, extension, container);
                break;
            default:
                this.renderTextPreview(content, container);
                break;
        }
    }

    renderMarkdownPreview(content, container) {
        // Enhanced markdown rendering with sanitization
        let html = content;
        
        // Split into lines for better processing
        const lines = html.split('\n');
        const processedLines = [];
        let inCodeBlock = false;
        let inList = false;
        let listItems = [];
        
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            
            // Handle code blocks
            if (line.trim().startsWith('```')) {
                if (inCodeBlock) {
                    processedLines.push('</code></pre>');
                    inCodeBlock = false;
                } else {
                    const language = this.escapeHtml(line.trim().substring(3));
                    processedLines.push(`<pre><code class="language-${language}">`);
                    inCodeBlock = true;
                }
                continue;
            }
            
            if (inCodeBlock) {
                processedLines.push(this.escapeHtml(line));
                continue;
            }
            
            // Handle headers
            if (line.match(/^#{1,6}\s/)) {
                const level = line.match(/^#+/)[0].length;
                const text = line.replace(/^#+\s*/, '');
                processedLines.push(`<h${level}>${this.escapeHtml(text)}</h${level}>`);
                continue;
            }
            
            // Handle lists
            if (line.match(/^[\s]*[-*+]\s/)) {
                const indent = line.match(/^[\s]*/)[0].length;
                const text = line.replace(/^[\s]*[-*+]\s/, '');
                
                if (!inList) {
                    inList = true;
                    listItems = [];
                }
                listItems.push(`<li>${this.processInlineMarkdown(this.escapeHtml(text))}</li>`);
                continue;
            } else if (inList) {
                // End of list
                processedLines.push(`<ul>${listItems.join('')}</ul>`);
                inList = false;
                listItems = [];
            }
            
            // Handle empty lines
            if (line.trim() === '') {
                if (!inList) {
                    processedLines.push('<br>');
                }
                continue;
            }
            
            // Handle regular paragraphs
            processedLines.push(`<p>${this.processInlineMarkdown(this.escapeHtml(line))}</p>`);
        }
        
        // Close any remaining list
        if (inList) {
            processedLines.push(`<ul>${listItems.join('')}</ul>`);
        }
        
        html = processedLines.join('\n');
        container.innerHTML = `<div class="markdown-preview">${html}</div>`;
        
        // Apply syntax highlighting to code blocks
        if (typeof hljs !== 'undefined') {
            container.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
    }
    
    processInlineMarkdown(text) {
        return text
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    }

    renderCsvPreview(content, container) {
        const lines = content.split('\n').filter(line => line.trim());
        if (lines.length === 0) {
            container.innerHTML = '<p>Empty CSV file</p>';
            return;
        }

        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
        const rows = lines.slice(1).map(line => 
            line.split(',').map(cell => cell.trim().replace(/"/g, ''))
        );

        let tableHtml = '<div class="csv-preview"><table class="csv-table">';
        tableHtml += '<thead><tr>';
        headers.forEach(header => {
            tableHtml += `<th>${header}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';

        rows.forEach(row => {
            tableHtml += '<tr>';
            row.forEach(cell => {
                tableHtml += `<td>${cell}</td>`;
            });
            tableHtml += '</tr>';
        });

        tableHtml += '</tbody></table></div>';
        container.innerHTML = tableHtml;
    }

    renderJsonPreview(content, container) {
        try {
            const parsed = JSON.parse(content);
            const formatted = JSON.stringify(parsed, null, 2);
            container.innerHTML = `<pre><code class="language-json">${this.escapeHtml(formatted)}</code></pre>`;
            
            // Apply syntax highlighting like file-modal.js
            if (typeof hljs !== 'undefined') {
                container.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        } catch (e) {
            container.innerHTML = `<div class="error">Invalid JSON: ${e.message}</div>`;
        }
    }

    renderCodePreview(content, extension, container) {
        const languageMap = {
            'js': 'javascript',
            'py': 'python',
            'yml': 'yaml',
            'md': 'markdown'
        };
        
        const language = languageMap[extension] || extension;
        container.innerHTML = `<pre><code class="language-${language}">${this.escapeHtml(content)}</code></pre>`;
        
        // Apply syntax highlighting like file-modal.js
        if (typeof hljs !== 'undefined') {
            container.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
    }

    renderTextPreview(content, container) {
        container.innerHTML = `<pre class="text-preview">${this.escapeHtml(content)}</pre>`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize admin panel when page loads
let adminPanel;
document.addEventListener('DOMContentLoaded', () => {
    adminPanel = new AdminPanel();
});