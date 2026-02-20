/**
 * Phase 4 (Test Case Generation) Details Handler
 * Handles Phase 4 specific rendering and interactions
 */

class Phase4DetailsHandler {
    constructor(dashboard) {
        this.dashboard = dashboard;
    }
    
    formatDate(dateString) {
        if (!dateString) return '';
        try {
            // Parse the date properly handling timezone
            let date;
            if (dateString.includes('Z')) {
                // UTC time
                date = new Date(dateString);
            } else if (dateString.includes('+')) {
                // Has timezone
                date = new Date(dateString);
            } else {
                // Assume local date if no timezone specified
                date = new Date(dateString);
            }
            
            // Format as YYYY-MM-DD
            return date.toISOString().split('T')[0];
        } catch (e) {
            return dateString;
        }
    }
    
    renderPhase4Details(phaseData) {
        console.log('Phase 4 handler called with data:', phaseData);
        
        const container = document.getElementById('phase-details-container');
        if (!container) {
            console.error('phase-details-container not found');
            return;
        }
        
        const { phaseId, name, status, artifacts, completedWorkpackages, inputFiles } = phaseData;
        
        let content = `
            <div class="phase-detail-header">
                <h3><span class="phase-badge">${phaseId}</span> ${name}</h3>
                <div class="phase-status ${status}">${status.replace('_', ' ')}</div>
            </div>
        `;
        
        // Add progress bar for Phase 4
        if (phaseData.totalWorkpackages && phaseData.completedCount !== undefined) {
            const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
            console.log(`Phase 4 progress: ${phaseData.completedCount}/${phaseData.totalWorkpackages} = ${progressPercent}%`);
            
            content += `
                <div class="phase-progress-section">
                    <div class="progress-info">
                        <span class="progress-label">Progress: ${phaseData.completedCount} of ${phaseData.totalWorkpackages} workpackages completed</span>
                        <span class="progress-percent">${progressPercent}%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${Math.max(progressPercent, 6)}%; background: #28a745 !important; min-width: 15px !important; height: 100% !important;"></div>
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
        
        // Show test case generation statistics
        if (completedWorkpackages && completedWorkpackages.length > 0) {
            // Calculate aggregate statistics
            const totalTestCases = completedWorkpackages.reduce((sum, wp) => sum + (wp.testCaseCount || 0), 0);
            
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-vial"></i> Test Case Generation Statistics</h4>
                    <div class="code-stats-simple">
                        <div class="stat-simple">
                            <span class="stat-number">${completedWorkpackages.length}</span>
                            <span class="stat-text">Workpackages</span>
                        </div>
                        <div class="stat-simple">
                            <span class="stat-number">${totalTestCases}</span>
                            <span class="stat-text">Test Cases</span>
                        </div>
                        <div class="stat-simple">
                            <span class="stat-number">${Math.round(totalTestCases / completedWorkpackages.length)}</span>
                            <span class="stat-text">Avg per WP</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Show completed workpackages with test case details
        if (completedWorkpackages && completedWorkpackages.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-check-circle"></i> Test Case Generation Progress (${completedWorkpackages.length} completed)</h4>
                    <div class="migration-comparison-container">
                        ${completedWorkpackages.sort((a, b) => a.id.localeCompare(b.id)).map(wp => {
                            return `
                            <div class="migration-item">
                                <div class="migration-header">
                                    <div class="wp-info">
                                        <span class="wp-id">${wp.id}</span>
                                        <span class="wp-entry">${wp.flowId || wp.name || ''}</span>
                                        <span class="wp-status-badge ${wp.status.toLowerCase()}">${wp.status}</span>
                                        ${wp.completedDate ? `<span class="wp-date">${this.formatDate(wp.completedDate)}</span>` : ''}
                                    </div>
                                    <div class="migration-status">
                                        ${wp.testCaseCount ? `<span class="test-count-badge">${wp.testCaseCount} test cases</span>` : ''}
                                    </div>
                                </div>
                                
                                <div class="test-spec-details">
                                    <div class="test-spec-section">
                                        <h5><i class="fas fa-file-alt"></i> Test Case Specification</h5>
                                        <div class="test-spec-files">
                                            ${wp.pathEN ? `
                                                <div class="file-item test-spec">
                                                    <span class="file-name">${wp.pathEN.split('/').pop()}</span>
                                                    <span class="file-type">Test Specification</span>
                                                    <button class="btn-view-file" data-file-path="${wp.pathEN}" title="View File">
                                                        <i class="fas fa-eye"></i>
                                                    </button>
                                                </div>
                                            ` : wp.path ? `
                                                <div class="file-item test-spec">
                                                    <span class="file-name">${wp.path.split('/').pop()}</span>
                                                    <span class="file-type">Test Specification</span>
                                                    <button class="btn-view-file" data-file-path="${wp.path}" title="View File">
                                                        <i class="fas fa-eye"></i>
                                                    </button>
                                                </div>
                                            ` : '<p class="no-files">No test specification file available</p>'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
        
        // Show input files section at the bottom
        if (inputFiles && inputFiles.files && inputFiles.files.length > 0) {
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
        
        // Force progress bar styling after DOM update (same as Phase 3)
        setTimeout(() => {
            const progressBar = container.querySelector('.progress-bar');
            const progressContainer = container.querySelector('.progress-bar-container');
            const progressSection = container.querySelector('.phase-progress-section');
            
            if (progressBar && phaseData.completedCount > 0) {
                const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
                const displayWidth = Math.max(progressPercent, 6);
                
                console.log(`Forcing Phase 4 progress bar style: ${displayWidth}%`);
                
                // Force parent elements to be visible
                if (progressSection) {
                    progressSection.style.cssText = `
                        display: block !important;
                        visibility: visible !important;
                        height: auto !important;
                        overflow: visible !important;
                        margin: 16px 0 !important;
                        padding: 16px !important;
                        background: #f8f9fa !important;
                        border: 1px solid #dee2e6 !important;
                        border-radius: 8px !important;
                    `;
                }
                
                if (progressContainer) {
                    progressContainer.style.cssText = `
                        width: 100% !important;
                        height: 12px !important;
                        background: #e9ecef !important;
                        border-radius: 6px !important;
                        overflow: hidden !important;
                        border: 1px solid #dee2e6 !important;
                        display: block !important;
                        visibility: visible !important;
                        position: relative !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    `;
                }
                
                progressBar.style.cssText = `
                    width: ${displayWidth}% !important;
                    background: #28a745 !important;
                    height: 100% !important;
                    min-width: 15px !important;
                    display: block !important;
                    border-radius: 5px !important;
                    visibility: visible !important;
                    position: relative !important;
                    top: 0 !important;
                    left: 0 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                `;
                
                console.log(`Applied Phase 4 styles:`, progressBar.style.cssText);
                console.log(`Progress bar element:`, progressBar);
                console.log(`Progress container element:`, progressContainer);
                console.log(`Progress section element:`, progressSection);
            }
        }, 100);
        
        // Setup click handlers for file view buttons
        this.setupFileViewHandlers();
    }
    
    setupFileViewHandlers() {
        // Add click handlers for file view buttons
        document.querySelectorAll('.btn-view-file').forEach(button => {
            button.addEventListener('click', () => {
                const filePath = button.dataset.filePath;
                this.showFileContent(filePath);
            });
        });
    }
    
    async showFileContent(filePath) {
        try {
            if (window.fileModal) {
                window.fileModal.showFileContent(filePath);
            } else {
                console.error('File modal not available');
            }
        } catch (error) {
            console.error('Error showing file content:', error);
        }
    }
}

// Create global instance
window.phase4DetailsHandler = new Phase4DetailsHandler();