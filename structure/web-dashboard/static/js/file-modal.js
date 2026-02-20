/**
 * File Modal Handler
 * Handles file content display in modals
 */

class FileModalHandler {
    constructor() {
        this.currentModal = null;
        this.modalInitialized = false;
        this.currentFileData = null;
    }
    
    closeCurrentModal() {
        if (this.currentModal) {
            this.currentModal.style.display = 'none';
            this.currentModal = null;
        }
    }
    
    resetModalScroll(modal) {
        // Multiple attempts to ensure scroll reset works
        const resetScroll = () => {
            // Reset modal body scroll
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
                modalBody.scrollLeft = 0;
            }
            
            // Reset modal content scroll
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.scrollTop = 0;
                modalContent.scrollLeft = 0;
            }
            
            // Reset file content scroll
            const fileContent = modal.querySelector('#modal-file-content');
            if (fileContent) {
                fileContent.scrollTop = 0;
                fileContent.scrollLeft = 0;
            }
            
            // Reset any pre elements (for code content)
            const preElements = modal.querySelectorAll('pre');
            preElements.forEach(pre => {
                pre.scrollTop = 0;
                pre.scrollLeft = 0;
            });
        };
        
        // Reset immediately
        resetScroll();
        
        // Reset after a short delay to ensure DOM is ready
        setTimeout(resetScroll, 50);
        
        // Reset after content is fully rendered
        setTimeout(resetScroll, 200);
    }
    
    setupModalCloseHandlers(modal) {
        // Remove existing listeners to prevent duplicates
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.replaceWith(closeBtn.cloneNode(true));
            modal.querySelector('.modal-close').addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.closeCurrentModal();
            });
        }
        
        // Background click to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeCurrentModal();
            }
        });
        
        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.closeCurrentModal();
            }
        });
    }
    
    async showFileContent(filePath) {
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(filePath)}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load file');
            }
            
            this.displayFileModal(data);
            
        } catch (error) {
            console.error('Error loading file:', error);
            alert(`Error loading file: ${error.message}`);
        }
    }
    
    async showMultiLanguageFileContent(pathKO, pathEN, fileName) {
        try {
            // Try to load Korean version first
            let response = await fetch(`/api/file/content?path=${encodeURIComponent(pathKO)}`);
            let data = await response.json();
            let defaultLanguage = 'ko';
            
            // If Korean version fails, try English version
            if (!response.ok) {
                console.log('Korean version not available, trying English version...');
                response = await fetch(`/api/file/content?path=${encodeURIComponent(pathEN)}`);
                data = await response.json();
                defaultLanguage = 'en';
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to load both language versions');
                }
            }
            
            // Add multi-language info
            data.hasMultipleLanguages = true;
            data.pathKO = pathKO;
            data.pathEN = pathEN;
            data.currentLanguage = defaultLanguage;
            data.file_name = fileName;
            
            this.displayMultiLanguageModal(data);
            
        } catch (error) {
            console.error('Error loading multi-language file:', error);
            alert(`Error loading file: ${error.message}`);
        }
    }
    
    displayMultiLanguageModal(fileData) {
        // Store current file data
        this.currentFileData = fileData;
        
        // Close any existing modal first
        this.closeCurrentModal();
        
        // Reset language toggle and scroll position when opening new file
        setTimeout(() => {
            const koBtn = document.getElementById('lang-ko');
            const enBtn = document.getElementById('lang-en');
            if (koBtn && enBtn) {
                document.querySelectorAll('.btn-lang').forEach(btn => btn.classList.remove('active'));
                // Activate button based on current language
                if (fileData.currentLanguage === 'en') {
                    enBtn.classList.add('active');
                } else {
                    koBtn.classList.add('active');
                }
            }
            
            // Reset scroll position to top
            const modalBody = document.querySelector('#file-modal .modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
            }
        }, 100);
        
        // Create modal if it doesn't exist
        let modal = document.getElementById('file-modal');
        if (!modal || !this.modalInitialized) {
            // Remove existing modal if any
            if (modal) {
                modal.remove();
            }
            
            modal = document.createElement('div');
            modal.id = 'file-modal';
            modal.className = 'file-modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3 id="modal-title"></h3>
                        <div class="modal-controls">
                            <div class="language-controls">
                                <button id="lang-ko" class="btn-lang active">Korean</button>
                                <button id="lang-en" class="btn-lang">English</button>
                            </div>
                            <span class="modal-close">&times;</span>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div id="modal-file-content"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Setup close handlers
            this.setupModalCloseHandlers(modal);
            
            // Add language switch handlers
            modal.querySelector('#lang-ko').addEventListener('click', () => {
                this.switchLanguage('ko');
            });
            
            modal.querySelector('#lang-en').addEventListener('click', () => {
                this.switchLanguage('en');
            });
            
            this.modalInitialized = true;
        }
        
        // Update modal content
        document.getElementById('modal-title').textContent = fileData.file_name;
        
        // Show language controls for multi-language files
        const languageControls = modal.querySelector('.language-controls');
        if (languageControls) {
            languageControls.style.display = 'flex';
        }
        
        // Render content
        this.renderFileContent(fileData);
        
        // Show modal
        modal.style.display = 'block';
        this.currentModal = modal;
        
        // Reset scroll position
        this.resetModalScroll(modal);
    }
    
    async switchLanguage(language) {
        if (!this.currentFileData) {
            console.error('No current file data available for language switch');
            return;
        }
        
        try {
            const path = language === 'ko' ? this.currentFileData.pathKO : this.currentFileData.pathEN;
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(path)}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load file');
            }
            
            // Update language buttons
            document.querySelectorAll('.btn-lang').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`lang-${language}`).classList.add('active');
            
            // Update content
            data.hasMultipleLanguages = true;
            data.pathKO = this.currentFileData.pathKO;
            data.pathEN = this.currentFileData.pathEN;
            data.currentLanguage = language;
            data.file_name = this.currentFileData.file_name;
            
            this.renderFileContent(data);
            
            // Reset scroll position to top after language switch
            this.resetModalScroll(document.getElementById('file-modal'));
            
        } catch (error) {
            console.error('Error switching language:', error);
            alert(`Error loading ${language.toUpperCase()} version: ${error.message}`);
        }
    }
    
    renderFileContent(fileData) {
        const contentDiv = document.getElementById('modal-file-content');
        let extension = fileData.file_extension?.toLowerCase() || '';
        
        // If no extension provided, extract from filename
        if (!extension && fileData.file_name) {
            const lastDot = fileData.file_name.lastIndexOf('.');
            if (lastDot > 0) {
                extension = fileData.file_name.substring(lastDot).toLowerCase();
            }
        }
        
        let renderedContent;
        if (extension === '.md') {
            renderedContent = this.renderMarkdown(fileData.content);
        } else if (extension === '.csv') {
            renderedContent = this.renderCSVTable(fileData.content);
        } else if (extension === '.json') {
            renderedContent = this.renderJSON(fileData.content);
        } else if (this.isCodeFile(extension)) {
            const language = this.getLanguageFromExtension(extension);
            const languageDisplay = language.charAt(0).toUpperCase() + language.slice(1);
            renderedContent = `
                <div class="code-header">
                    <span class="language-label">${languageDisplay}</span>
                    <button class="copy-btn" onclick="this.parentElement.nextElementSibling.querySelector('code') ? navigator.clipboard.writeText(this.parentElement.nextElementSibling.querySelector('code').textContent) : navigator.clipboard.writeText(this.parentElement.nextElementSibling.textContent)">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                </div>
                <pre><code class="language-${language}">${this.escapeHtml(fileData.content)}</code></pre>
            `;
        } else {
            renderedContent = `<pre class="raw-content">${this.escapeHtml(fileData.content)}</pre>`;
        }
        
        contentDiv.innerHTML = renderedContent;
        
        // Apply syntax highlighting if available
        if (typeof hljs !== 'undefined') {
            contentDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
            // Also highlight any existing code blocks
            contentDiv.querySelectorAll('pre:not(.raw-content)').forEach((block) => {
                if (!block.querySelector('code')) {
                    hljs.highlightElement(block);
                }
            });
        }
    }
    
    displayFileModal(fileData) {
        // Close any existing modal first
        this.closeCurrentModal();
        
        // Reset scroll position when opening new file
        setTimeout(() => {
            const modalBody = document.querySelector('#file-modal .modal-body');
            if (modalBody) {
                modalBody.scrollTop = 0;
            }
        }, 100);
        
        // Create modal if it doesn't exist
        let modal = document.getElementById('file-modal');
        if (!modal || !this.modalInitialized) {
            // Remove existing modal if any
            if (modal) {
                modal.remove();
            }
            
            modal = document.createElement('div');
            modal.id = 'file-modal';
            modal.className = 'file-modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3 id="modal-title"></h3>
                        <div class="modal-controls">
                            <div class="language-controls" style="display: none;">
                                <button id="lang-ko" class="btn-lang active">Korean</button>
                                <button id="lang-en" class="btn-lang">English</button>
                            </div>
                            <span class="modal-close">&times;</span>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div id="modal-file-content"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Setup close handlers
            this.setupModalCloseHandlers(modal);
            
            // Add language switch handlers
            modal.querySelector('#lang-ko').addEventListener('click', () => {
                this.switchLanguage('ko');
            });
            
            modal.querySelector('#lang-en').addEventListener('click', () => {
                this.switchLanguage('en');
            });
            
            this.modalInitialized = true;
        }
        
        // Update modal content
        document.getElementById('modal-title').textContent = fileData.file_name;
        
        // Hide language controls for single-language files
        const languageControls = modal.querySelector('.language-controls');
        if (languageControls) {
            languageControls.style.display = 'none';
        }
        
        // Render content
        this.renderFileContent(fileData);
        
        // Show modal
        modal.style.display = 'block';
        this.currentModal = modal;
        
        // Reset scroll position
        this.resetModalScroll(modal);
    }
    
    renderCSVTable(csvContent) {
        try {
            const lines = csvContent.trim().split('\n');
            if (lines.length === 0) return '<p>Empty CSV file</p>';
            
            // Parse CSV (simple parser - handles basic cases)
            const rows = lines.map(line => this.parseCSVLine(line));
            
            if (rows.length === 0) return '<p>No data found</p>';
            
            const headers = rows[0];
            const dataRows = rows.slice(1);
            
            let tableHTML = '<div class="csv-table-container"><table class="csv-table">';
            
            // Headers
            tableHTML += '<thead><tr>';
            headers.forEach(header => {
                tableHTML += `<th>${this.escapeHtml(header)}</th>`;
            });
            tableHTML += '</tr></thead>';
            
            // Data rows
            tableHTML += '<tbody>';
            dataRows.forEach((row, index) => {
                tableHTML += `<tr class="${index % 2 === 0 ? 'even' : 'odd'}">`;
                headers.forEach((_, colIndex) => {
                    const cellValue = row[colIndex] || '';
                    tableHTML += `<td>${this.escapeHtml(cellValue)}</td>`;
                });
                tableHTML += '</tr>';
            });
            tableHTML += '</tbody></table></div>';
            
            // Add summary info
            tableHTML += `<div class="csv-summary">
                <small>${dataRows.length} rows × ${headers.length} columns</small>
            </div>`;
            
            return tableHTML;
            
        } catch (error) {
            console.error('Error parsing CSV:', error);
            return `<p>Error parsing CSV: ${error.message}</p><pre class="raw-content">${this.escapeHtml(csvContent)}</pre>`;
        }
    }
    
    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        
        result.push(current.trim());
        return result;
    }
    
    renderJSON(jsonContent) {
        try {
            // Try to parse and format JSON
            const parsed = JSON.parse(jsonContent);
            const formatted = JSON.stringify(parsed, null, 2);
            
            return `<pre class="code-content"><code class="language-json">${this.escapeHtml(formatted)}</code></pre>`;
        } catch (error) {
            // If parsing fails, show as raw text
            return `<div class="error-message">Invalid JSON format</div><pre class="raw-content">${this.escapeHtml(jsonContent)}</pre>`;
        }
    }
    
    renderMarkdown(markdownContent) {
        try {
            // Use marked.js to render markdown if available
            if (typeof marked !== 'undefined') {
                const htmlContent = marked.parse(markdownContent);
                return `<div class="markdown-content">${htmlContent}</div>`;
            } else {
                return `<pre class="raw-content">${this.escapeHtml(markdownContent)}</pre>`;
            }
        } catch (error) {
            console.error('Error rendering markdown:', error);
            return `<div class="error-message">Error rendering markdown</div><pre class="raw-content">${this.escapeHtml(markdownContent)}</pre>`;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    isCodeFile(extension) {
        const codeExtensions = ['.py', '.js', '.html', '.css', '.sql', '.sh', '.bat', '.cbl', '.cob', '.cobol', '.java', '.c', '.cpp', '.h', '.hpp', '.uio', '.xsql', '.xio'];
        return codeExtensions.includes(extension.toLowerCase());
    }
    
    getLanguageFromExtension(extension) {
        const languageMap = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.cbl': 'cobol',
            '.cob': 'cobol',
            '.cobol': 'cobol',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.uio': 'xml',
            '.xsql': 'xml',
            '.xio': 'xml'
        };
        return languageMap[extension.toLowerCase()] || 'plaintext';
    }
}

// Export for use in other modules
window.FileModalHandler = FileModalHandler;