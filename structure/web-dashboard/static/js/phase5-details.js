/**
 * Phase 5 (Test Generation) Details Handler
 * Handles Phase 5 specific rendering and interactions
 */

class Phase5DetailsHandler {
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
    
    renderPhase5Details(phaseData) {
        console.log('Phase 5 handler called with data:', phaseData);
        
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
        
        // Add progress bar for Phase 5
        if (phaseData.totalWorkpackages && phaseData.completedCount !== undefined) {
            const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
            console.log(`Phase 5 progress: ${phaseData.completedCount}/${phaseData.totalWorkpackages} = ${progressPercent}%`);
            
            content += `
                <div class="phase-progress-section">
                    <div class="progress-info">
                        <span class="progress-label">Progress: ${phaseData.completedCount} of ${phaseData.totalWorkpackages} workpackages completed</span>
                        <span class="progress-percent">${progressPercent}%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${Math.max(progressPercent, 6)}%; background: #17a2b8 !important; min-width: 15px !important; height: 100% !important;"></div>
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
        
        // Show test generation statistics first
        if (phaseData.phaseQualityMetrics) {
            const metrics = phaseData.phaseQualityMetrics;
            
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-chart-pie"></i> Test Generation Statistics</h4>
                    <div class="test-stats-overview">
                        <div class="stat-overview">
                            <span class="stat-number">${metrics.totalTestCasesGenerated || 0}</span>
                            <span class="stat-text">Total Test Cases</span>
                        </div>
                        <div class="stat-overview">
                            <span class="stat-number">${metrics.averageTestCaseCoverage || '100%'}</span>
                            <span class="stat-text">Avg Coverage</span>
                        </div>
                        <div class="stat-overview">
                            <span class="stat-number">${metrics.averageTraceability || '100%'}</span>
                            <span class="stat-text">Traceability</span>
                        </div>
                        <div class="stat-overview">
                            <span class="stat-number">${metrics.ieee829Compliance || '100%'}</span>
                            <span class="stat-text">IEEE 829</span>
                        </div>
                    </div>
                    
                    ${metrics.testTypeDistribution ? `
                        <div class="test-type-distribution">
                            <h5>Test Type Distribution</h5>
                            <div class="distribution-bars">
                                <div class="distribution-item">
                                    <span class="distribution-label">Positive Tests</span>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill positive" style="width: ${metrics.testTypeDistribution.positive}"></div>
                                    </div>
                                    <span class="distribution-percent">${metrics.testTypeDistribution.positive}</span>
                                </div>
                                <div class="distribution-item">
                                    <span class="distribution-label">Negative Tests</span>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill negative" style="width: ${metrics.testTypeDistribution.negative}"></div>
                                    </div>
                                    <span class="distribution-percent">${metrics.testTypeDistribution.negative}</span>
                                </div>
                                <div class="distribution-item">
                                    <span class="distribution-label">Boundary Tests</span>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill boundary" style="width: ${metrics.testTypeDistribution.boundary}"></div>
                                    </div>
                                    <span class="distribution-percent">${metrics.testTypeDistribution.boundary}</span>
                                </div>
                                <div class="distribution-item">
                                    <span class="distribution-label">Performance Tests</span>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill performance" style="width: ${metrics.testTypeDistribution.performance}"></div>
                                    </div>
                                    <span class="distribution-percent">${metrics.testTypeDistribution.performance}</span>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        // Show completed workpackages with test generation details
        if (completedWorkpackages && completedWorkpackages.length > 0) {
            content += `
                <div class="detail-section">
                    <h4><i class="fas fa-vial"></i> Test Generation Progress (${completedWorkpackages.length} completed)</h4>
                    <div class="test-generation-container">
                        ${completedWorkpackages.sort((a, b) => a.id.localeCompare(b.id)).map(wp => {
                            return `
                            <div class="test-generation-item-compact">
                                <div class="test-header">
                                    <div class="wp-info">
                                        <span class="wp-id">${wp.id}</span>
                                        <span class="wp-entry">${wp.flowId}</span>
                                        <span class="wp-domain-badge ${this.getDomainClass(wp.businessDomain)}">${wp.businessDomain}</span>
                                        ${wp.completedDate ? `<span class="wp-date">${this.formatDate(wp.completedDate)}</span>` : ''}
                                    </div>
                                    <div class="test-status">
                                        <span class="test-coverage">${wp.testCaseGeneration?.functionCoverage || '100%'}</span>
                                        <span class="quality-badge ${wp.qualityMetrics?.standardCompliance || 'excellent'}">${wp.qualityMetrics?.standardCompliance || 'excellent'}</span>
                                    </div>
                                </div>
                                
                                <div class="test-summary-row">
                                    <div class="test-summary-item">
                                        <span class="summary-label">Test Cases</span>
                                        <span class="summary-value">${wp.testCaseGeneration?.totalTestCases || 0} total</span>
                                        <span class="summary-breakdown">(${wp.testCaseGeneration?.positiveTests || 0}+ / ${wp.testCaseGeneration?.negativeTests || 0}- / ${wp.testCaseGeneration?.boundaryTests || 0}B)</span>
                                    </div>
                                    
                                    <div class="test-summary-item">
                                        <span class="summary-label">Priority</span>
                                        <div class="priority-compact">
                                            ${wp.testPrioritization?.critical > 0 ? `<span class="priority-compact-tag critical">${wp.testPrioritization.critical}</span>` : ''}
                                            ${wp.testPrioritization?.high > 0 ? `<span class="priority-compact-tag high">${wp.testPrioritization.high}</span>` : ''}
                                            ${wp.testPrioritization?.medium > 0 ? `<span class="priority-compact-tag medium">${wp.testPrioritization.medium}</span>` : ''}
                                        </div>
                                    </div>
                                    
                                    <div class="test-summary-item">
                                        <span class="summary-label">Documents</span>
                                        <div class="docs-compact">
                                            ${wp.bilingualDocuments ? `
                                                <button class="btn-test-spec" 
                                                    data-path-ko="output/specifications/tests/${wp.bilingualDocuments.koreanDocument}" 
                                                    data-path-en="output/specifications/tests/${wp.bilingualDocuments.englishDocument}"
                                                    title="View Test Cases">
                                                    <i class="fas fa-vial"></i> Test Cases
                                                </button>
                                            ` : ''}
                                        </div>
                                    </div>
                                    
                                    <div class="test-summary-item">
                                        <span class="summary-label">Coverage</span>
                                        <span class="summary-value">${wp.testCaseGeneration?.functionCoverage || '100%'}</span>
                                        <span class="summary-breakdown">F:${wp.testCaseGeneration?.functionCoverage || '100%'} | E:${wp.testCaseGeneration?.entityCoverage || '100%'} | BR:${wp.testCaseGeneration?.businessRulesCoverage || '100%'}</span>
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
        
        // Force progress bar styling after DOM update
        setTimeout(() => {
            const progressBar = container.querySelector('.progress-bar');
            const progressContainer = container.querySelector('.progress-bar-container');
            const progressSection = container.querySelector('.phase-progress-section');
            
            if (progressBar && phaseData.completedCount > 0) {
                const progressPercent = Math.round((phaseData.completedCount / phaseData.totalWorkpackages) * 100);
                const displayWidth = Math.max(progressPercent, 6);
                
                console.log(`Forcing Phase 5 progress bar style: ${displayWidth}%`);
                
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
                    background: #17a2b8 !important;
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
                
                console.log(`Applied Phase 5 progress bar styles:`, progressBar.style.cssText);
            }
        }, 100);
        
        // Setup click handlers for document view buttons
        this.setupDocumentViewHandlers();
    }
    
    getDomainClass(businessDomain) {
        const domainClasses = {
            'TRANSACTION': 'domain-transaction',
            'CUSTOMER': 'domain-customer',
            'CREDIT': 'domain-credit',
            'REPORTING': 'domain-reporting',
            'BATCH': 'domain-batch',
            'INQUIRY': 'domain-inquiry'
        };
        return domainClasses[businessDomain] || 'domain-default';
    }
    
    setupDocumentViewHandlers() {
        // Add click handlers for test specification buttons
        document.querySelectorAll('.btn-test-spec').forEach(button => {
            button.addEventListener('click', () => {
                const pathKO = button.dataset.pathKo;
                const pathEN = button.dataset.pathEn;
                
                if (pathKO && pathEN) {
                    // Multi-language file - extract workpackage ID for filename
                    const wpId = button.closest('.test-generation-item-compact').querySelector('.wp-id').textContent;
                    const fileName = `${wpId}-test-cases.md`;
                    if (window.fileModal) {
                        window.fileModal.showMultiLanguageFileContent(pathKO, pathEN, fileName);
                    }
                } else {
                    console.error('Missing Korean or English document path');
                }
            });
        });
        
        // Keep backward compatibility for any remaining single-language buttons
        document.querySelectorAll('.btn-view-doc').forEach(button => {
            button.addEventListener('click', () => {
                const docPath = button.dataset.docPath;
                this.showDocumentContent(docPath);
            });
        });
    }
    
    async showDocumentContent(docPath) {
        try {
            if (window.fileModal) {
                window.fileModal.showFileContent(docPath);
            } else {
                console.error('File modal not available');
            }
        } catch (error) {
            console.error('Error showing document content:', error);
        }
    }
}

// Create global instance
window.phase5DetailsHandler = new Phase5DetailsHandler();