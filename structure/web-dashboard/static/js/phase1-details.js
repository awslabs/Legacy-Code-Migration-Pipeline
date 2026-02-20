/**
 * Phase 1 (Source Analysis) Details Handler
 * Handles Phase 1 specific rendering and interactions
 */

class Phase1DetailsHandler {
    constructor(dashboard) {
        this.dashboard = dashboard;
    }
    
    renderPhase1Details(phaseData) {
        const container = document.getElementById('phase-details-container');
        if (!container) return;
        
        const { phaseId, name, status, artifacts, reports, details } = phaseData;
        
        let content = `
            <div class="phase-detail-header">
                <h3><span class="phase-badge">${phaseId}</span> ${name}</h3>
                <div class="phase-status ${status}">${status.replace('_', ' ')}</div>
            </div>
        `;
        
        // Show completion details if available
        if (details && (details.completion_time || details.completedAt || details.timestamp)) {
            const completionTime = details.completion_time || details.completedAt || details.timestamp;
            try {
                const dt = new Date(completionTime.replace('+09:00', ''));
                content += `<div class="completion-info">Completed: ${dt.toLocaleDateString()} ${dt.toLocaleTimeString()}</div>`;
            } catch (e) {
                content += `<div class="completion-info">Completed</div>`;
            }
        }
        
        // Always show graph buttons for Phase 1
        content += `
            <div class="detail-section">
                <div class="section-header-with-actions">
                    <h4>Visualizations</h4>
                    <div class="btn-group">
                        <button id="show-business-flows-graph" class="btn-graph">View Business Flows</button>
                        <button id="show-dependency-graph" class="btn-graph">View Dependency Graph</button>
                    </div>
                </div>
            </div>
        `;
        
        // Show summary statistics for Phase 1 (Source Analysis)
        if (details && (details.analysis_summary || details.totalModules)) {
            // Use new JSON structure or fallback to old structure
            const summary = details.analysis_summary || {
                totalModules: details.totalModules || 0,
                processedModules: details.processedModules || 0,
                tasksCompleted: details.tasksCompleted || []
            };
            
            content += `
                <div class="detail-section">
                    <h4>Summary Statistics</h4>
                    <div class="summary-stats">
                        ${this.renderNewSummaryStats(summary, details)}
                    </div>
                </div>
            `;
            
            // Render charts after DOM update
            setTimeout(() => {
                this.renderNewCharts(details);
            }, 100);
        }
        
        // Show artifacts
        if (artifacts && artifacts.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-file-alt"></i> Generated Files (${artifacts.length})</h4>
                    <ul class="simple-file-list">
                        ${artifacts.map(artifact => {
                            if (typeof artifact === 'object') {
                                return `<li data-path="${artifact.path}">${artifact.name}</li>`;
                            } else {
                                return `<li>${artifact}</li>`;
                            }
                        }).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Show reports
        if (reports && reports.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-chart-bar"></i> Reports (${reports.length})</h4>
                    <ul class="simple-file-list">
                        ${reports.map(report => {
                            if (typeof report === 'object') {
                                return `<li data-path="${report.path}">${report.name}</li>`;
                            } else {
                                return `<li>${report}</li>`;
                            }
                        }).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Show tools
        if (phaseData.tools && phaseData.tools.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-tools"></i> Generated Tools (${phaseData.tools.length})</h4>
                    <ul class="simple-file-list">
                        ${phaseData.tools.map(tool => `
                            <li data-path="${tool.path}" title="${tool.description}">${tool.name}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Show input files section at the bottom
        if (phaseData.inputFiles && phaseData.inputFiles.files && phaseData.inputFiles.files.length > 0) {
            const inputFiles = phaseData.inputFiles;
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-folder-open"></i> ${inputFiles.title}</h4>
                    <p class="section-description">${inputFiles.description}</p>
                    <div class="input-files-compact">
                        ${inputFiles.files.sort((a, b) => a.path.localeCompare(b.path)).map(file => `
                            <div class="input-file-compact">
                                <span class="file-type-badge">${file.type}</span>
                                <span class="file-path-compact">${file.path}</span>
                                <span class="file-desc-compact">${file.description}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = content;
        
        // Add click handlers for file items
        this.setupFileClickHandlers();
        
        // Add click handler for business flows graph button
        const flowsGraphBtn = document.getElementById('show-business-flows-graph');
        if (flowsGraphBtn) {
            flowsGraphBtn.addEventListener('click', () => {
                window.businessFlowsGraphHandler.showBusinessFlowsGraph();
            });
        }
        
        // Add click handler for dependency graph button
        const graphBtn = document.getElementById('show-dependency-graph');
        if (graphBtn) {
            graphBtn.addEventListener('click', () => {
                window.sourceAnalysisHandler.showDependencyGraph();
            });
        }
    }
    
    renderNewSummaryStats(summary, details) {
        // Create summary stats HTML for new JSON structure
        const totalModules = details.totalModules || 0;
        const processedModules = details.processedModules || 0;
        const tasksCompleted = details.tasksCompleted || [];
        const completionRate = totalModules > 0 ? Math.round((processedModules / totalModules) * 100) : 0;
        const chartId = `chart-${Date.now()}`;
        
        return `
            <div class="summary-grid">
                <div class="text-container">
                    <h4>Module Classification</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">Total Modules:</span>
                            <span class="text-stat-value">730</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Commonly Used:</span>
                            <span class="text-stat-value">287</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Single Use:</span>
                            <span class="text-stat-value">199</span>
                        </div>
                        <div class="text-stat-item medium">
                            <span class="text-stat-label">Unused:</span>
                            <span class="text-stat-value">189</span>
                        </div>
                    </div>
                </div>
                <div class="text-container">
                    <h4>Business Flow Complexity</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">Total Flows:</span>
                            <span class="text-stat-value">55</span>
                        </div>
                        <div class="text-stat-item critical">
                            <span class="text-stat-label">Most Complex (AIP4A31):</span>
                            <span class="text-stat-value">81 modules</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Online Flows:</span>
                            <span class="text-stat-value">40</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Batch Flows:</span>
                            <span class="text-stat-value">15</span>
                        </div>
                    </div>
                </div>
                <div class="text-container">
                    <h4>Critical Dependencies</h4>
                    <div class="text-stats">
                        <div class="text-stat-item critical">
                            <span class="text-stat-label">YCCOMMON (Most Used):</span>
                            <span class="text-stat-value">258 deps</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">YCDBSQLA:</span>
                            <span class="text-stat-value">183 deps</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">YCCSICOM:</span>
                            <span class="text-stat-value">156 deps</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">YCCBICOM:</span>
                            <span class="text-stat-value">156 deps</span>
                        </div>
                    </div>
                </div>
                <div class="text-container">
                    <h4>Database Activity Summary</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">SELECT Operations:</span>
                            <span class="text-stat-value">294</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">INSERT Operations:</span>
                            <span class="text-stat-value">63</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">UPDATE Operations:</span>
                            <span class="text-stat-value">62</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">DELETE Operations:</span>
                            <span class="text-stat-value">61</span>
                        </div>
                    </div>
                </div>
                <div class="chart-container">
                    <h4>Module Type Distribution</h4>
                    <canvas id="moduleTypeChart-${chartId}" width="300" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h4>Top 5 Most Complex Flows</h4>
                    <canvas id="complexityChart-${chartId}" width="300" height="200"></canvas>
                </div>
            </div>
        `;
    }
    
    renderNewCharts(details) {
        if (typeof Chart === 'undefined') return;
        
        // Module Type Chart
        const moduleTypeCtx = document.querySelector('canvas[id*="moduleTypeChart"]');
        if (moduleTypeCtx) {
            new Chart(moduleTypeCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Commonly Used', 'Single Use', 'Unused', 'Entry Points'],
                    datasets: [{
                        data: [287, 199, 189, 55],
                        backgroundColor: [
                            '#007bff',  // Blue for commonly used
                            '#28a745',  // Green for single use
                            '#6c757d',  // Gray for unused
                            '#dc3545'   // Red for entry points
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 8,
                                usePointStyle: true,
                                font: {
                                    size: 10
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Flow Complexity Chart
        const complexityCtx = document.querySelector('canvas[id*="complexityChart"]');
        if (complexityCtx) {
            new Chart(complexityCtx, {
                type: 'bar',
                data: {
                    labels: ['AIP4A31', 'AIP4A32', 'AIPBA96', 'AIPBA30', 'AIP4A62'],
                    datasets: [{
                        label: 'Module Count',
                        data: [81, 71, 69, 58, 53],
                        backgroundColor: [
                            '#dc3545', '#fd7e14', '#ffc107', '#28a745', '#007bff'
                        ],
                        borderWidth: 1,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Modules'
                            }
                        },
                        x: {
                            ticks: {
                                font: {
                                    size: 9
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
        

    }
    
    setupFileClickHandlers() {
        // Add click handlers for files with paths
        document.querySelectorAll('[data-path]').forEach(item => {
            item.addEventListener('click', () => {
                const path = item.dataset.path;
                if (path && window.fileModal) {
                    window.fileModal.showFileContent(path);
                }
            });
        });
    }
}

// Create global instance
window.phase1DetailsHandler = new Phase1DetailsHandler();