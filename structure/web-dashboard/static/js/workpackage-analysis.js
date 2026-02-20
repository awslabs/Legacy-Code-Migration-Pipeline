/**
 * Workpackage Analysis Handler
 * Handles Phase 2 workpackage analysis and visualization
 */

class WorkpackageAnalysisHandler {
    constructor() {
        this.workpackageData = null;
        this.dependencyData = null;
    }
    
    async showAnalysis(analysisType) {
        console.log('Opening workpackage analysis:', analysisType);
        
        if (analysisType === 'workpackages') {
            await this.showWorkpackageAnalysis();
        } else if (analysisType === 'dependencies') {
            await this.showDependencyAnalysis();
        }
    }
    
    async showWorkpackageAnalysis() {
        try {
            const response = await fetch('/api/workpackage-analysis');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load workpackage data');
            }
            
            this.workpackageData = data;
            this.displayWorkpackageModal(data);
            
        } catch (error) {
            console.error('Error loading workpackage analysis:', error);
            alert(`Error loading workpackage analysis: ${error.message}`);
        }
    }
    
    displayWorkpackageModal(data) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('workpackage-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'workpackage-modal';
            modal.className = 'file-modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3><i class="fas fa-boxes"></i> Workpackage Analysis</h3>
                        <div class="modal-controls">
                            <select id="wp-phase-filter">
                                <option value="">All Phases</option>
                                <option value="1">Phase 1</option>
                                <option value="2">Phase 2</option>
                                <option value="3">Phase 3</option>
                            </select>
                            <select id="wp-priority-filter">
                                <option value="">All Priorities</option>
                                <option value="high">High Priority (1-15)</option>
                                <option value="medium">Medium Priority (16-35)</option>
                                <option value="low">Low Priority (36+)</option>
                            </select>
                            <span class="modal-close">&times;</span>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div id="workpackage-stats" class="workpackage-stats-summary"></div>
                        <div id="workpackage-grid" class="workpackages-container"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add close event listeners
            modal.querySelector('.modal-close').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
            
            // Add filter event listeners
            modal.querySelector('#wp-phase-filter').addEventListener('change', () => {
                this.filterWorkpackages();
            });
            
            modal.querySelector('#wp-priority-filter').addEventListener('change', () => {
                this.filterWorkpackages();
            });
        }
        
        // Show modal
        modal.style.display = 'block';
        
        // Render workpackages
        this.renderWorkpackages();
    }
    
    renderWorkpackages() {
        const statsContainer = document.getElementById('workpackage-stats');
        const gridContainer = document.getElementById('workpackage-grid');
        
        if (!statsContainer || !gridContainer || !this.workpackageData) return;
        
        const workpackages = this.workpackageData.workpackages || [];
        
        // Render summary stats
        const phaseStats = workpackages.reduce((acc, wp) => {
            acc[wp.phase] = (acc[wp.phase] || 0) + 1;
            return acc;
        }, {});
        
        const priorityStats = {
            high: workpackages.filter(wp => wp.priority <= 15).length,
            medium: workpackages.filter(wp => wp.priority > 15 && wp.priority <= 35).length,
            low: workpackages.filter(wp => wp.priority > 35).length
        };
        
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${workpackages.length}</div>
                    <div class="stat-label">Total Workpackages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${phaseStats[1] || 0}</div>
                    <div class="stat-label">Phase 1</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${phaseStats[2] || 0}</div>
                    <div class="stat-label">Phase 2</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${phaseStats[3] || 0}</div>
                    <div class="stat-label">Phase 3</div>
                </div>
                <div class="stat-card priority-high">
                    <div class="stat-value">${priorityStats.high}</div>
                    <div class="stat-label">High Priority</div>
                </div>
                <div class="stat-card priority-medium">
                    <div class="stat-value">${priorityStats.medium}</div>
                    <div class="stat-label">Medium Priority</div>
                </div>
                <div class="stat-card priority-low">
                    <div class="stat-value">${priorityStats.low}</div>
                    <div class="stat-label">Low Priority</div>
                </div>
            </div>
        `;
        
        // Apply filters and render grid
        this.filterWorkpackages();
    }
    
    filterWorkpackages() {
        const phaseFilter = document.getElementById('wp-phase-filter')?.value;
        const priorityFilter = document.getElementById('wp-priority-filter')?.value;
        const gridContainer = document.getElementById('workpackage-grid');
        
        if (!gridContainer || !this.workpackageData) return;
        
        let filteredWorkpackages = this.workpackageData.workpackages || [];
        
        // Apply phase filter
        if (phaseFilter) {
            filteredWorkpackages = filteredWorkpackages.filter(wp => wp.phase.toString() === phaseFilter);
        }
        
        // Apply priority filter
        if (priorityFilter) {
            if (priorityFilter === 'high') {
                filteredWorkpackages = filteredWorkpackages.filter(wp => wp.priority <= 15);
            } else if (priorityFilter === 'medium') {
                filteredWorkpackages = filteredWorkpackages.filter(wp => wp.priority > 15 && wp.priority <= 35);
            } else if (priorityFilter === 'low') {
                filteredWorkpackages = filteredWorkpackages.filter(wp => wp.priority > 35);
            }
        }
        
        // Render filtered workpackages
        gridContainer.innerHTML = filteredWorkpackages.map(wp => `
            <div class="workpackage-card ${this.getPriorityClass(wp.priority)}">
                <div class="workpackage-header">
                    <div class="workpackage-id">${wp.id}</div>
                    <div class="workpackage-priority ${this.getPriorityClass(wp.priority)}">
                        Priority ${wp.priority}
                    </div>
                </div>
                
                <div class="workpackage-details">
                    <div class="workpackage-detail">
                        <div class="detail-label">Flow ID</div>
                        <div class="detail-value">${wp.flowId}</div>
                    </div>
                    <div class="workpackage-detail">
                        <div class="detail-label">Entry Point</div>
                        <div class="detail-value">${wp.entryPoint}</div>
                    </div>
                    <div class="workpackage-detail">
                        <div class="detail-label">Phase</div>
                        <div class="detail-value">Phase ${wp.phase}</div>
                    </div>
                    <div class="workpackage-detail">
                        <div class="detail-label">Flow Type</div>
                        <div class="detail-value">${wp.flowType}</div>
                    </div>
                </div>
                
                <div class="workpackage-metrics">
                    <div class="metric">
                        <i class="fas fa-cubes metric-icon"></i>
                        <span class="metric-value">${wp.moduleCount}</span>
                        <span>modules</span>
                    </div>
                    <div class="metric">
                        <i class="fas fa-share-alt metric-icon"></i>
                        <span class="metric-value">${wp.commonModuleCount}</span>
                        <span>shared</span>
                    </div>
                    <div class="metric">
                        <i class="fas fa-chart-line metric-icon"></i>
                        <span class="metric-value">${wp.complexityScore}</span>
                        <span>complexity</span>
                    </div>
                    <div class="metric">
                        <i class="fas fa-star metric-icon"></i>
                        <span class="metric-value">${wp.priorityScore.toFixed(1)}</span>
                        <span>score</span>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    getPriorityClass(priority) {
        if (priority <= 15) return 'high';
        if (priority <= 35) return 'medium';
        return 'low';
    }
    
    async showDependencyAnalysis() {
        try {
            const response = await fetch('/api/workpackage-dependencies');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load dependency data');
            }
            
            this.dependencyData = data;
            this.displayDependencyModal(data);
            
        } catch (error) {
            console.error('Error loading dependency analysis:', error);
            alert(`Error loading dependency analysis: ${error.message}`);
        }
    }
    
    displayDependencyModal(data) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('dependency-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'dependency-modal';
            modal.className = 'file-modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3><i class="fas fa-project-diagram"></i> Workpackage Dependencies</h3>
                        <div class="modal-controls">
                            <span class="modal-close">&times;</span>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div id="dependency-visualization" class="dependency-container">
                            <div class="dependency-summary">
                                <h4>Dependency Summary</h4>
                                <div id="dependency-stats"></div>
                            </div>
                            <div class="dependency-list">
                                <h4>Dependency Details</h4>
                                <div id="dependency-details"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add close event listeners
            modal.querySelector('.modal-close').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        // Show modal
        modal.style.display = 'block';
        
        // Render dependency data
        this.renderDependencies(data);
    }
    
    renderDependencies(data) {
        const statsContainer = document.getElementById('dependency-stats');
        const detailsContainer = document.getElementById('dependency-details');
        
        if (!statsContainer || !detailsContainer) return;
        
        // Calculate stats
        const totalWorkpackages = Object.keys(data).length;
        const totalDependencies = Object.values(data).reduce((sum, deps) => sum + deps.length, 0);
        const avgDependencies = totalWorkpackages > 0 ? (totalDependencies / totalWorkpackages).toFixed(1) : 0;
        
        // Find most common shared modules
        const sharedModules = {};
        Object.values(data).forEach(deps => {
            deps.forEach(dep => {
                if (dep.sharedModules) {
                    dep.sharedModules.forEach(module => {
                        sharedModules[module] = (sharedModules[module] || 0) + 1;
                    });
                }
            });
        });
        
        const topSharedModules = Object.entries(sharedModules)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5);
        
        // Render stats
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${totalWorkpackages}</div>
                    <div class="stat-label">Workpackages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${totalDependencies}</div>
                    <div class="stat-label">Dependencies</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${avgDependencies}</div>
                    <div class="stat-label">Avg per WP</div>
                </div>
            </div>
            <div class="shared-modules">
                <h5>Most Shared Modules:</h5>
                <div class="module-tags">
                    ${topSharedModules.map(([module, count]) => 
                        `<span class="module-tag">${module} (${count})</span>`
                    ).join('')}
                </div>
            </div>
        `;
        
        // Render dependency details
        detailsContainer.innerHTML = `
            <div class="dependency-tree">
                ${Object.entries(data).map(([wp, deps]) => `
                    <div class="dependency-item">
                        <div class="dependency-header">
                            <strong>${wp}</strong>
                            <span class="dependency-count">${deps.length} dependencies</span>
                        </div>
                        <div class="dependency-list">
                            ${deps.map(dep => `
                                <div class="dependency-detail">
                                    <span class="depends-on">→ ${dep.dependsOn}</span>
                                    ${dep.sharedModules ? `
                                        <div class="shared-modules-list">
                                            ${dep.sharedModules.map(module => 
                                                `<span class="shared-module">${module}</span>`
                                            ).join('')}
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

// Export for use in other modules
window.WorkpackageAnalysisHandler = WorkpackageAnalysisHandler;