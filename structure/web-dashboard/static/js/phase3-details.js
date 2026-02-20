/**
 * Phase 3 (Business Extraction) Details Handler
 * Handles Phase 3 specific rendering and interactions
 */

class Phase3DetailsHandler {
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
            } else if (dateString.includes('+09:00')) {
                // Already Korean time
                date = new Date(dateString);
            } else {
                // Assume local date if no timezone specified
                date = new Date(dateString);
            }
            
            // Format in Korean timezone
            return date.toLocaleDateString('ko-KR', { 
                timeZone: 'Asia/Seoul',
                month: '2-digit', 
                day: '2-digit' 
            });
        } catch (e) {
            return dateString;
        }
    }
    
    renderPhase3Details(phaseData) {
        console.log('Phase 3 handler called with data:', phaseData);
        console.log('Phase 3 artifacts:', phaseData.artifacts);
        console.log('Phase 3 completedWorkpackages:', phaseData.completedWorkpackages);
        
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
        
        // Add progress bar for Phase 3
        if (phaseData.totalWorkpackages && phaseData.completedCount !== undefined) {
            const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
            console.log(`Phase 3 progress: ${phaseData.completedCount}/${phaseData.totalWorkpackages} = ${progressPercent}%`);
            
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
        
        // Show compact workpackages for Phase 3
        if (completedWorkpackages && completedWorkpackages.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-boxes"></i> Completed Workpackages (${completedWorkpackages.length})</h4>
                    <div class="workpackage-compact-list">
                        ${completedWorkpackages.sort((a, b) => a.id.localeCompare(b.id)).map(wp => {
                            // Find corresponding artifacts for this workpackage
                            const wpArtifacts = artifacts ? artifacts.filter(artifact => 
                                artifact.workpackage === wp.id || artifact.name.includes(wp.id)
                            ) : [];
                            
                            console.log(`Workpackage ${wp.id} artifacts:`, wpArtifacts);
                            
                            return `
                            <div class="workpackage-compact-item">
                                <div class="wp-main">
                                    <div class="wp-info">
                                        <span class="wp-id">${wp.id}</span>
                                        <span class="wp-flow">${wp.flowId}</span>
                                        ${wp.completedDate ? `<span class="wp-date">${this.dashboard ? this.dashboard.formatDate(wp.completedDate) : this.formatDate(wp.completedDate)}</span>` : ''}
                                    </div>
                                    <div class="wp-actions">
                                        ${wpArtifacts.map(artifact => {
                                            if (artifact.hasMultipleLanguages && artifact.pathKO && artifact.pathEN) {
                                                return `<button class="btn-spec" data-path-ko="${artifact.pathKO}" data-path-en="${artifact.pathEN}" title="View Business Specification">
                                                    <i class="fas fa-file-text"></i> Spec
                                                </button>`;
                                            } else if (artifact.path) {
                                                return `<button class="btn-spec" data-path="${artifact.path}" title="View ${artifact.type}">
                                                    <i class="fas fa-file"></i> File
                                                </button>`;
                                            }
                                            return '';
                                        }).join('')}
                                    </div>
                                </div>
                            </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
        
        // Show reports section
        if (phaseData.reports && phaseData.reports.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-chart-bar"></i> Reports & Generated Files (${phaseData.reports.length})</h4>
                    <ul class="simple-file-list two-column">
                        ${phaseData.reports.sort((a, b) => a.name.localeCompare(b.name)).map(report => `
                            <li data-path="${report.path}" title="${report.name}">
                                <span class="file-type-badge">${report.type}</span>
                                ${report.name}
                            </li>
                        `).join('')}
                    </ul>
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
        
        // Force progress bar styling after DOM update
        setTimeout(() => {
            const progressBar = container.querySelector('.progress-bar');
            const progressContainer = container.querySelector('.progress-bar-container');
            const progressSection = container.querySelector('.phase-progress-section');
            
            if (progressBar && phaseData.completedCount > 0) {
                const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
                const displayWidth = Math.max(progressPercent, 6);
                
                console.log(`Forcing progress bar style: ${displayWidth}%`);
                
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
                
                console.log(`Applied styles:`, progressBar.style.cssText);
                console.log(`Progress bar element:`, progressBar);
                console.log(`Progress container element:`, progressContainer);
                console.log(`Progress section element:`, progressSection);
            }
        }, 100);
        
        // Add click handlers for compact spec buttons
        this.setupFileClickHandlers();
    }
    
    setupFileClickHandlers() {
        // Add click handlers for compact spec buttons
        document.querySelectorAll('.btn-spec').forEach(button => {
            button.addEventListener('click', () => {
                const pathKO = button.dataset.pathKo;
                const pathEN = button.dataset.pathEn;
                const path = button.dataset.path;
                
                if (pathKO && pathEN) {
                    // Multi-language file
                    const fileName = `${button.closest('.workpackage-compact-item').querySelector('.wp-id').textContent}-specification.md`;
                    if (window.fileModal) {
                        window.fileModal.showMultiLanguageFileContent(pathKO, pathEN, fileName);
                    }
                } else if (path) {
                    // Single file
                    if (window.fileModal) {
                        window.fileModal.showFileContent(path);
                    }
                }
            });
        });
        
        // Add click handlers for report/file list items with data-path
        document.querySelectorAll('.simple-file-list li[data-path]').forEach(item => {
            item.addEventListener('click', () => {
                const path = item.dataset.path;
                console.log('File clicked:', path);
                if (path && window.fileModal) {
                    window.fileModal.showFileContent(path);
                } else {
                    console.error('Missing path or fileModal not available:', { path, fileModal: window.fileModal });
                }
            });
        });
    }
}

// Create global instance
window.phase3DetailsHandler = new Phase3DetailsHandler();