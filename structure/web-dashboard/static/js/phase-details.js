/**
 * Phase Details Handler (Cleaned Version)
 * Handles phase detail display and interactions
 */

class PhaseDetailsHandler {
    constructor(dashboard) {
        this.dashboard = dashboard;
    }
    
    async showPhaseDetails(phaseId) {
        console.log(`Loading details for phase ${phaseId}`);
        
        // Scroll to phase details section when in Phase Details tab
        const phaseDetailsContainer = document.getElementById('phase-details-container');
        if (phaseDetailsContainer && window.tabNavigation) {
            const currentTab = window.tabNavigation.getCurrentTab();
            if (currentTab === 'phase-details') {
                phaseDetailsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
        
        try {
            const response = await fetch(`/api/phase/${phaseId}`);
            const phaseData = await response.json();
            
            // Route to phase-specific handlers
            switch(phaseId) {
                case 1:
                    if (window.phase1DetailsHandler) {
                        window.phase1DetailsHandler.renderPhase1Details(phaseData);
                    } else {
                        this.renderStandardPhaseDetails(phaseData);
                    }
                    break;
                case 2:
                    this.renderPhase2Details(phaseData);
                    break;
                case 3:
                    if (window.phase3DetailsHandler) {
                        // Pass dashboard reference to Phase 3 handler
                        window.phase3DetailsHandler.dashboard = this.dashboard;
                        window.phase3DetailsHandler.renderPhase3Details(phaseData);
                    } else {
                        this.renderStandardPhaseDetails(phaseData);
                    }
                    break;
                case 4:
                    if (window.phase4DetailsHandler) {
                        // Pass dashboard reference to Phase 4 handler
                        window.phase4DetailsHandler.dashboard = this.dashboard;
                        window.phase4DetailsHandler.renderPhase4Details(phaseData);
                    } else {
                        this.renderStandardPhaseDetails(phaseData);
                    }
                    break;
                case 5:
                    if (window.phase5DetailsHandler) {
                        // Pass dashboard reference to Phase 5 handler
                        window.phase5DetailsHandler.dashboard = this.dashboard;
                        window.phase5DetailsHandler.renderPhase5Details(phaseData);
                    } else {
                        this.renderStandardPhaseDetails(phaseData);
                    }
                    break;
                default:
                    this.renderStandardPhaseDetails(phaseData);
                    break;
            }
            
            // Highlight selected phase
            document.querySelectorAll('.phase-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`[data-phase-id="${phaseId}"]`).classList.add('selected');
            
        } catch (error) {
            console.error('Error loading phase details:', error);
            this.dashboard.showError('Failed to load phase details');
        }
    }
    
    renderPhase2Details(phaseData) {
        const container = document.getElementById('phase-details-container');
        if (!container) return;
        
        const { phaseId, name, status, artifacts, reports } = phaseData;
        
        let content = `
            <div class="phase-detail-header">
                <h3><span class="phase-badge">${phaseId}</span> ${name}</h3>
                <div class="phase-status ${status}">${status.replace('_', ' ')}</div>
            </div>
            
            <!-- Phase Navigation Controls -->
            <div class="phase-navigation-controls">
                ${phaseId > 1 ? `<button class="phase-nav-btn prev" onclick="dashboard.showPhaseDetails(${phaseId - 1})">
                    <i class="fas fa-chevron-left"></i> Previous Phase
                </button>` : '<div></div>'}
                ${phaseId < 8 ? `<button class="phase-nav-btn next" onclick="dashboard.showPhaseDetails(${phaseId + 1})">
                    Next Phase <i class="fas fa-chevron-right"></i>
                </button>` : '<div></div>'}
            </div>
        `;
        
        // Show workpackage summary statistics for Phase 2
        content += `
            <div class="detail-section">
                <h4>Workpackage Summary Statistics</h4>
                <div class="summary-stats" id="workpackage-summary-${phaseId}">
                    <div class="loading">Loading workpackage statistics...</div>
                </div>
            </div>
        `;
        
        // Show artifacts with interactive analysis
        if (artifacts && artifacts.length > 0) {
            // Separate interactive and regular artifacts
            const interactiveArtifacts = artifacts.filter(a => a.isInteractive);
            const regularArtifacts = artifacts.filter(a => !a.isInteractive);
            
            // Show interactive artifacts first
            if (interactiveArtifacts.length > 0) {
                content += `
                    <div class="detail-section">
                        <h4><i class="fas fa-chart-line"></i> Interactive Analysis</h4>
                        <div class="interactive-artifacts">
                            ${interactiveArtifacts.sort((a, b) => a.name.localeCompare(b.name)).map(artifact => `
                                <div class="interactive-artifact-card" onclick="workpackageAnalysis.showAnalysis('${artifact.analysisType}')">
                                    <div class="artifact-header">
                                        <h5>${artifact.name}</h5>
                                        <span class="artifact-type">${artifact.type}</span>
                                    </div>
                                    ${artifact.summary ? `
                                        <div class="artifact-summary">
                                            <div class="summary-stats-grid">
                                                ${artifact.analysisType === 'workpackages' ? `
                                                    <div class="stat-item">
                                                        <span class="stat-label">Total Workpackages:</span>
                                                        <span class="stat-value">${artifact.summary.totalWorkpackages}</span>
                                                    </div>
                                                    <div class="stat-item">
                                                        <span class="stat-label">High Priority:</span>
                                                        <span class="stat-value">${artifact.summary.highPriority}</span>
                                                    </div>
                                                    <div class="stat-item">
                                                        <span class="stat-label">Avg Complexity:</span>
                                                        <span class="stat-value">${artifact.summary.avgComplexity.toFixed(1)}</span>
                                                    </div>
                                                    <div class="stat-item">
                                                        <span class="stat-label">Phase Distribution:</span>
                                                        <span class="stat-value">P1:${artifact.summary.phases['1']} P2:${artifact.summary.phases['2']} P3:${artifact.summary.phases['3']}</span>
                                                    </div>
                                                ` : ''}
                                            </div>
                                        </div>
                                    ` : ''}
                                    <div class="artifact-action">
                                        <i class="fas fa-external-link-alt"></i> Open Analysis
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            // Show regular artifacts
            if (regularArtifacts.length > 0) {
                content += `
                    <div class="detail-section">
                        <h4><i class="fas fa-file-alt"></i> Generated Files (${regularArtifacts.length})</h4>
                        <ul class="simple-file-list">
                            ${regularArtifacts.sort((a, b) => a.name.localeCompare(b.name)).map(artifact => `
                                <li data-path="${artifact.path}">${artifact.name}</li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }
        }
        
        // Show reports
        if (reports && reports.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-chart-bar"></i> Reports (${reports.length})</h4>
                    <ul class="simple-file-list">
                        ${reports.sort((a, b) => a.name.localeCompare(b.name)).map(report => `
                            <li data-path="${report.path}">${report.name}</li>
                        `).join('')}
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
                        ${inputFiles.files.map(file => `
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
        
        // Load workpackage summary for Phase 2
        this.loadWorkpackageSummary(phaseData.phaseId);
        
        // Add click handlers for file items
        this.setupFileClickHandlers();
    }
    
    renderStandardPhaseDetails(phaseData) {
        const container = document.getElementById('phase-details-container');
        if (!container) return;
        
        const { phaseId, name, status, artifacts, reports, completedWorkpackages, details } = phaseData;
        
        let content = `
            <div class="phase-detail-header">
                <h3><span class="phase-badge">${phaseId}</span> ${name}</h3>
                <div class="phase-status ${status}">${status.replace('_', ' ')}</div>
            </div>
            
            <!-- Phase Navigation Controls -->
            <div class="phase-navigation-controls">
                ${phaseId > 1 ? `<button class="phase-nav-btn prev" onclick="dashboard.showPhaseDetails(${phaseId - 1})">
                    <i class="fas fa-chevron-left"></i> Previous Phase
                </button>` : '<div></div>'}
                ${phaseId < 8 ? `<button class="phase-nav-btn next" onclick="dashboard.showPhaseDetails(${phaseId + 1})">
                    Next Phase <i class="fas fa-chevron-right"></i>
                </button>` : '<div></div>'}
            </div>
        `;
        
        // Add progress bar for workpackage-based phases (3-7)
        if (phaseId >= 3 && phaseId <= 7) {
            if (phaseData.totalWorkpackages && phaseData.completedCount !== undefined) {
                const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
                content += `
                    <div class="phase-progress-section">
                        <div class="progress-info">
                            <span class="progress-label">Progress: ${phaseData.completedCount} of ${phaseData.totalWorkpackages} workpackages completed</span>
                            <span class="progress-percent">${progressPercent}%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: ${progressPercent}%"></div>
                        </div>
                    </div>
                `;
            } else if (status === 'completed') {
                content += `
                    <div class="phase-progress-section">
                        <div class="progress-info">
                            <span class="progress-label">Phase completed</span>
                            <span class="progress-percent">100%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar completed" style="width: 100%"></div>
                        </div>
                    </div>
                `;
            }
        }
        
        // Show completion details if available
        if (details && (details.completion_time || details.completedAt || details.timestamp)) {
            const completionTime = details.completion_time || details.completedAt || details.timestamp;
            try {
                // Parse the date properly handling timezone
                let dt;
                if (completionTime.includes('Z')) {
                    // UTC time
                    dt = new Date(completionTime);
                } else if (completionTime.includes('+09:00')) {
                    // Already Korean time
                    dt = new Date(completionTime);
                } else {
                    // Assume UTC if no timezone specified
                    dt = new Date(completionTime + 'Z');
                }
                
                // Format in Korean timezone
                const dateStr = dt.toLocaleDateString('ko-KR', { timeZone: 'Asia/Seoul' });
                const timeStr = dt.toLocaleTimeString('ko-KR', { timeZone: 'Asia/Seoul' });
                content += `<div class="completion-info">Completed: ${dateStr} ${timeStr}</div>`;
            } catch (e) {
                content += `<div class="completion-info">Completed</div>`;
            }
        }
        
        // Show summary statistics for Phase 1 (Source Analysis)
        if (phaseId === 1 && details && details.analysis_summary) {
            const summary = details.analysis_summary;
            content += `
                <div class="detail-section">
                    <div class="section-header-with-actions">
                        <h4>Summary Statistics</h4>
                        <div class="btn-group">
                            <button id="show-dependency-graph" class="btn-graph">View Dependency Graph</button>
                        </div>
                    </div>
                    <div class="summary-stats">
                        ${window.sourceAnalysisHandler.renderSummaryCharts(summary)}
                    </div>
                </div>
            `;
        }
        
        // Show artifacts (skip for Phase 3 as we'll show integrated workpackages)
        if (artifacts && artifacts.length > 0 && phaseId !== 3) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-file-alt"></i> Generated Files (${artifacts.length})</h4>
                    <ul class="simple-file-list">
                        ${artifacts.sort((a, b) => {
                            const nameA = typeof a === 'object' ? a.name : a;
                            const nameB = typeof b === 'object' ? b.name : b;
                            return nameA.localeCompare(nameB);
                        }).map(artifact => {
                            if (typeof artifact === 'object') {
                                if (artifact.hasMultipleLanguages && artifact.pathKO && artifact.pathEN) {
                                    return `<li data-path-ko="${artifact.pathKO}" data-path-en="${artifact.pathEN}">${artifact.name} <span class="multi-lang">(KO/EN)</span></li>`;
                                } else if (artifact.path) {
                                    return `<li data-path="${artifact.path}">${artifact.name}</li>`;
                                } else {
                                    return `<li>${artifact.name}</li>`;
                                }
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
                        ${reports.sort((a, b) => {
                            const nameA = typeof a === 'object' ? a.name : a;
                            const nameB = typeof b === 'object' ? b.name : b;
                            return nameA.localeCompare(nameB);
                        }).map(report => {
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
        
        // Show completed workpackages for other phases (not Phase 3)
        if (phaseId !== 3 && completedWorkpackages && completedWorkpackages.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-boxes"></i> Completed Workpackages (${completedWorkpackages.length})</h4>
                    <div class="workpackage-details">
                        ${completedWorkpackages.map(wp => `
                            <div class="workpackage-item">
                                <div class="workpackage-header">
                                    <span class="workpackage-id">${wp.id}</span>
                                    <span class="flow-id">${wp.flowId}</span>
                                    ${wp.completedDate ? `<span class="completion-date">${this.dashboard.formatDate(wp.completedDate)}</span>` : ''}
                                </div>
                                <div class="workpackage-stats">
                                    ${wp.businessEntities ? `<span class="stat">Entities: ${wp.businessEntities}</span>` : ''}
                                    ${wp.businessRules ? `<span class="stat">Rules: ${wp.businessRules}</span>` : ''}
                                    ${wp.businessFunctions ? `<span class="stat">Functions: ${wp.businessFunctions}</span>` : ''}
                                    ${wp.accuracyScore ? `<span class="stat accuracy">Accuracy: ${wp.accuracyScore}%</span>` : ''}
                                </div>
                                ${wp.extractionNotes ? `<div class="workpackage-notes">${wp.extractionNotes}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
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
                        ${inputFiles.files.map(file => `
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
    }
    
    setupFileClickHandlers() {
        // Add click handlers for files with paths
        document.querySelectorAll('[data-path]').forEach(item => {
            item.addEventListener('click', () => {
                const path = item.dataset.path;
                console.log('Single file clicked:', path);
                if (path && window.fileModal) {
                    window.fileModal.showFileContent(path);
                } else {
                    console.error('Missing path or fileModal not available:', { path, fileModal: window.fileModal });
                }
            });
        });
        
        // Add click handlers for multi-language files
        document.querySelectorAll('[data-path-ko][data-path-en]').forEach(item => {
            item.addEventListener('click', () => {
                const pathKO = item.dataset.pathKo;
                const pathEN = item.dataset.pathEn;
                const fileName = item.textContent.replace(' (KO/EN)', '').trim();
                console.log('Multi-language file clicked:', { pathKO, pathEN, fileName });
                if (pathKO && pathEN && window.fileModal) {
                    window.fileModal.showMultiLanguageFileContent(pathKO, pathEN, fileName);
                } else {
                    console.error('Missing paths or fileModal not available:', { pathKO, pathEN, fileModal: window.fileModal });
                }
            });
        });
        

        
        // Add click handler for dependency graph button
        const graphBtn = document.getElementById('show-dependency-graph');
        if (graphBtn) {
            graphBtn.addEventListener('click', () => {
                window.sourceAnalysisHandler.showDependencyGraph();
            });
        }
    }
    
    async loadWorkpackageSummary(phaseId) {
        if (phaseId !== 2) return;
        
        const summaryContainer = document.getElementById(`workpackage-summary-${phaseId}`);
        if (!summaryContainer) return;
        
        try {
            const summaryHtml = await window.workpackageSummaryHandler.renderWorkpackageSummary();
            summaryContainer.innerHTML = summaryHtml;
        } catch (error) {
            console.error('Error loading workpackage summary:', error);
            summaryContainer.innerHTML = '<div class="error">Failed to load workpackage summary</div>';
        }
    }
}

// Export for use in main dashboard
window.PhaseDetailsHandler = PhaseDetailsHandler;