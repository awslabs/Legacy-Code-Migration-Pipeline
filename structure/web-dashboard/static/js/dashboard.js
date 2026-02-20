/**
 * Migration Dashboard JavaScript - Main Controller
 * Handles data loading, UI interactions, and coordinates other modules
 */

class MigrationDashboard {
    constructor() {
        this.data = {
            overview: null,
            flows: null,
            workpackages: null,
            files: null
        };
        
        this.filters = {
            domain: '',
            phase: '',
            search: ''
        };
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Migration Dashboard...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadAllData();
        
        // Hide loading overlay
        this.hideLoadingOverlay();
    }
    
    setupEventListeners() {
        // Phase card click handlers are set up in renderPhases method
        // No additional event listeners needed for now
    }
    
    async loadAllData() {
        try {
            console.log('Loading dashboard data...');
            
            // Load overview data
            const overviewResponse = await fetch('/api/overview');
            this.data.overview = await overviewResponse.json();
            this.renderOverview();
            
            // Load flows data
            const flowsResponse = await fetch('/api/flows');
            this.data.flows = await flowsResponse.json();
            this.updateDomainFilter();
            this.renderFlows();
            
            // Load workpackages data
            const workpackagesResponse = await fetch('/api/workpackages');
            this.data.workpackages = await workpackagesResponse.json();
            this.renderWorkpackages();
            
            console.log('All data loaded successfully');
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    renderOverview() {
        const overview = this.data.overview;
        if (!overview || overview.error) {
            console.error('Overview data error:', overview?.error);
            return;
        }
        
        // Update header
        document.getElementById('project-name').textContent = `Project: ${overview.projectName || 'Migration Project'}`;
        document.getElementById('last-updated').textContent = `Last updated: ${this.formatDate(overview.lastUpdated)}`;
        
        // Update project info (new structure)
        const legacySystem = overview.legacySystem || {};
        const targetSystem = overview.targetSystem || {};
        
        document.getElementById('legacy-language').textContent = legacySystem.language || '-';
        document.getElementById('legacy-framework').textContent = legacySystem.framework || '-';
        document.getElementById('target-language').textContent = targetSystem.language || '-';
        document.getElementById('target-framework').textContent = targetSystem.framework || '-';
        
        // Update project description
        const description = overview.projectDescription || 'No description available. Configure in project-config.json.';
        document.getElementById('project-description').textContent = description;
        
        // Update legacy analysis statistics
        const legacyStats = overview.stats?.legacy || {};
        document.getElementById('legacy-total-files').textContent = legacyStats.totalFiles || 0;
        document.getElementById('legacy-total-lines').textContent = legacyStats.totalLines || 0;
        document.getElementById('legacy-missing-files').textContent = legacyStats.missingFiles || 0;
        
        // Update file type categories (language-agnostic)
        document.getElementById('legacy-programs').textContent = legacyStats.programs || 0;
        document.getElementById('legacy-libraries').textContent = legacyStats.libraries || 0;
        document.getElementById('legacy-scripts').textContent = legacyStats.scripts || 0;
        document.getElementById('legacy-other-files').textContent = legacyStats.otherFiles || 0;
        
        // Update additional metrics
        document.getElementById('legacy-entry-points').textContent = legacyStats.entryPoints || 0;
        document.getElementById('legacy-cics-resources').textContent = legacyStats.cicsResources || 0;
        document.getElementById('legacy-database-files').textContent = legacyStats.databaseFiles || 0;
        
        // Update complexity distribution
        const complexity = legacyStats.complexityDistribution || { HIGH: 0, MEDIUM: 0, LOW: 0, UNKNOWN: 0 };
        const totalComplexity = complexity.HIGH + complexity.MEDIUM + complexity.LOW + complexity.UNKNOWN;
        
        document.getElementById('complexity-high-count').textContent = complexity.HIGH;
        document.getElementById('complexity-medium-count').textContent = complexity.MEDIUM;
        document.getElementById('complexity-low-count').textContent = complexity.LOW;
        document.getElementById('complexity-unknown-count').textContent = complexity.UNKNOWN;
        
        // Update complexity bars (percentage of total)
        if (totalComplexity > 0) {
            const highPercent = (complexity.HIGH / totalComplexity) * 100;
            const mediumPercent = (complexity.MEDIUM / totalComplexity) * 100;
            const lowPercent = (complexity.LOW / totalComplexity) * 100;
            const unknownPercent = (complexity.UNKNOWN / totalComplexity) * 100;
            
            document.getElementById('complexity-high-bar').style.width = `${highPercent}%`;
            document.getElementById('complexity-medium-bar').style.width = `${mediumPercent}%`;
            document.getElementById('complexity-low-bar').style.width = `${lowPercent}%`;
            document.getElementById('complexity-unknown-bar').style.width = `${unknownPercent}%`;
        } else {
            document.getElementById('complexity-high-bar').style.width = '0%';
            document.getElementById('complexity-medium-bar').style.width = '0%';
            document.getElementById('complexity-low-bar').style.width = '0%';
            document.getElementById('complexity-unknown-bar').style.width = '0%';
        }
        
        // Show source badge if data is estimated
        const sourceBadge = document.getElementById('legacy-source-badge');
        if (legacyStats.source === 'estimated') {
            sourceBadge.textContent = '⚠ Estimated using directory parsing';
            sourceBadge.style.display = 'inline-block';
            sourceBadge.className = 'source-badge estimated';
        } else if (legacyStats.source === 'database') {
            sourceBadge.textContent = '✓ From analysis database';
            sourceBadge.style.display = 'inline-block';
            sourceBadge.className = 'source-badge database';
        } else {
            sourceBadge.style.display = 'none';
        }
        
        // Update migration progress statistics (workpackage-based)
        const migrationStats = overview.stats?.migration || {};
        const totalWorkpackages = migrationStats.totalWorkpackages || 0;
        
        console.log('Migration stats:', migrationStats);
        
        document.getElementById('migration-total-workpackages').textContent = totalWorkpackages;
        
        // Get phase statuses from overview.phases
        const phases = overview.phases || [];
        const phase1 = phases.find(p => p.id === 1) || {};
        const phase2 = phases.find(p => p.id === 2) || {};
        
        // Update Phase 1 & 2 status (completed/in-progress/not-started)
        this.updatePhaseStatus('phase1', phase1.status || 'unknown');
        this.updatePhaseStatus('phase2', phase2.status || 'unknown');
        
        // Update progress values and bars for Phase 3, 4, 5 (workpackage-based)
        console.log('Updating progress bars...');
        this.updateProgressBar('phase3', migrationStats.businessExtractionCompleted || 0, totalWorkpackages);
        this.updateProgressBar('phase4', migrationStats.testCaseGenerationCompleted || 0, totalWorkpackages);
        this.updateProgressBar('phase5', migrationStats.codeGenerationCompleted || 0, totalWorkpackages);
        
        // Calculate overall completion percentage
        const phase1Complete = phase1.status === 'completed' ? 1 : 0;
        const phase2Complete = phase2.status === 'completed' ? 1 : 0;
        const phase3Percent = totalWorkpackages > 0 ? (migrationStats.businessExtractionCompleted || 0) / totalWorkpackages : 0;
        const phase4Percent = totalWorkpackages > 0 ? (migrationStats.testCaseGenerationCompleted || 0) / totalWorkpackages : 0;
        const phase5Percent = totalWorkpackages > 0 ? (migrationStats.codeGenerationCompleted || 0) / totalWorkpackages : 0;
        
        const overallPercent = Math.round(((phase1Complete + phase2Complete + phase3Percent + phase4Percent + phase5Percent) / 5) * 100);
        
        document.getElementById('overall-completion-percent').textContent = `${overallPercent}%`;
        document.getElementById('overall-progress-fill').style.width = `${overallPercent}%`;
        
        // Determine current phase (highest active phase with progress)
        let currentPhase = 'Not Started';
        
        // Check phases in reverse order (5 to 1) to find the highest active phase
        if ((migrationStats.codeGenerationCompleted || 0) > 0) {
            currentPhase = 'Phase 5: Code Generation';
        } else if ((migrationStats.testCaseGenerationCompleted || 0) > 0) {
            currentPhase = 'Phase 4: Test Case Generation';
        } else if ((migrationStats.businessExtractionCompleted || 0) > 0) {
            currentPhase = 'Phase 3: Business Extraction';
        } else if (phase2.status === 'completed' || phase2.status === 'in_progress') {
            currentPhase = 'Phase 2: Workpackage Definition';
        } else if (phase1.status === 'completed' || phase1.status === 'in_progress') {
            currentPhase = 'Phase 1: Source Analysis';
        }
        
        // If all phases are complete, show that
        if (phase1.status === 'completed' && 
            phase2.status === 'completed' && 
            phase3Percent === 1 && 
            phase4Percent === 1 && 
            phase5Percent === 1) {
            currentPhase = 'All Phases Complete';
        }
        
        document.getElementById('current-phase-name').textContent = currentPhase;
        
        // Update phases
        this.renderPhases(overview.phases || []);
    }
    
    updatePhaseStatus(phaseId, status) {
        const statusElement = document.getElementById(`migration-${phaseId}-status`);
        const progressElement = document.getElementById(`progress-${phaseId}`);
        
        if (statusElement) {
            // Map status to display text
            const statusMap = {
                'completed': 'Completed',
                'in_progress': 'In Progress',
                'not_started': 'Not Started',
                'unknown': 'Unknown'
            };
            statusElement.textContent = statusMap[status] || status;
        }
        
        if (progressElement) {
            // Set progress bar based on status
            const widthMap = {
                'completed': 100,
                'in_progress': 50,
                'not_started': 0,
                'unknown': 0
            };
            const width = widthMap[status] || 0;
            progressElement.style.width = `${width}%`;
            
            // Add status class for styling
            progressElement.className = `progress-fill phase-status ${status}`;
        }
    }
    
    updateProgressBar(phaseId, completed, total) {
        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
        
        console.log(`Updating progress bar ${phaseId}: ${completed}/${total} = ${percentage}%`);
        
        // Update text value
        const valueElement = document.getElementById(`migration-${phaseId}-completed`);
        if (valueElement) {
            valueElement.textContent = `${completed}/${total}`;
            console.log(`Updated text for migration-${phaseId}-completed: ${completed}/${total}`);
        } else {
            console.warn(`Element migration-${phaseId}-completed not found`);
            // List all elements with similar IDs for debugging
            const allElements = document.querySelectorAll('[id*="migration-"][id*="-completed"]');
            console.log('Available migration completed elements:', Array.from(allElements).map(el => el.id));
        }
        
        // Update progress bar
        console.log(`Looking for element: progress-${phaseId}`);
        const progressElement = document.getElementById(`progress-${phaseId}`);
        console.log(`Found element:`, progressElement);
        
        if (progressElement) {
            // For small percentages, ensure minimum visibility (6% minimum for any progress)
            const displayWidth = completed > 0 ? Math.max(percentage, 6) : 0;
            
            console.log(`Updating progress bar ${phaseId}: ${completed}/${total} = ${percentage}% (display: ${displayWidth}%)`);
            
            // Force styles directly with setProperty to use !important
            progressElement.style.setProperty('width', `${displayWidth}%`, 'important');
            progressElement.style.setProperty('display', 'block', 'important');
            progressElement.style.setProperty('opacity', '1', 'important');
            progressElement.style.setProperty('min-width', completed > 0 ? '30px' : '0px', 'important');
            progressElement.style.setProperty('height', '100%', 'important');
            progressElement.style.setProperty('transition', 'width 0.6s ease-in-out', 'important');
            
            // Set background color based on phase
            if (phaseId === 'phase3' && completed > 0) {
                progressElement.style.setProperty('background', 'linear-gradient(90deg, #28a745 0%, #1e7e34 100%)', 'important');
            } else if (phaseId === 'phase4' && completed > 0) {
                progressElement.style.setProperty('background', 'linear-gradient(90deg, #28a745 0%, #1e7e34 100%)', 'important');
            } else if (phaseId === 'phase5' && completed > 0) {
                progressElement.style.setProperty('background', 'linear-gradient(90deg, #17a2b8 0%, #138496 100%)', 'important');
            }
            
            console.log(`Applied styles to ${progressElement.id}:`, progressElement.style.cssText);
            
            // Simple approach: just make it very visible
            if (completed > 0) {
                const color = phaseId === 'phase3' ? '#28a745' : 
                             phaseId === 'phase4' ? '#28a745' : '#17a2b8';
                
                // Clear all existing styles and set new ones
                progressElement.removeAttribute('style');
                progressElement.style.cssText = `
                    width: ${displayWidth}% !important;
                    height: 100% !important;
                    background-color: ${color} !important;
                    border-radius: 5px !important;
                    display: block !important;
                    min-width: 15px !important;
                    position: relative !important;
                    top: 0 !important;
                    left: 0 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                `;
                
                console.log(`Set simple styles for ${phaseId}: ${progressElement.style.cssText}`);
            }
            
            // Debug parent element
            const parentElement = progressElement.parentElement;
            console.log(`Parent element (${parentElement.className}):`, {
                display: window.getComputedStyle(parentElement).display,
                width: window.getComputedStyle(parentElement).width,
                height: window.getComputedStyle(parentElement).height,
                overflow: window.getComputedStyle(parentElement).overflow,
                visibility: window.getComputedStyle(parentElement).visibility
            });
            
            // Debug the progress element itself
            console.log(`Progress element computed styles:`, {
                display: window.getComputedStyle(progressElement).display,
                width: window.getComputedStyle(progressElement).width,
                height: window.getComputedStyle(progressElement).height,
                background: window.getComputedStyle(progressElement).background,
                visibility: window.getComputedStyle(progressElement).visibility,
                opacity: window.getComputedStyle(progressElement).opacity
            });
            
            // Add percentage tooltip showing real percentage
            progressElement.setAttribute('title', `${percentage}% (${completed}/${total})`);
        } else {
            console.warn(`Element progress-${phaseId} not found`);
            
            // Debug: List all elements with progress in their ID
            const allProgressElements = document.querySelectorAll('[id*="progress"]');
            console.log('All elements with "progress" in ID:', Array.from(allProgressElements).map(el => ({
                id: el.id,
                tagName: el.tagName,
                className: el.className
            })));
            
            // Debug: List all elements with progress-fill class
            const allProgressFillElements = document.querySelectorAll('.progress-fill');
            console.log('All elements with progress-fill class:', Array.from(allProgressFillElements).map(el => ({
                id: el.id,
                tagName: el.tagName,
                className: el.className
            })));
        }
    }
    
    updateDomainFilter() {
        // This function is kept for compatibility but not used anymore
        // Domain filtering is now handled in the modal dropdown
    }
    
    renderFlows() {
        // This function is kept for compatibility
        // Flow visualization is now handled in the modal
    }
    
    renderPhases(phases) {
        const container = document.getElementById('phases-list');
        if (!container) return;
        
        container.innerHTML = phases.map(phase => `
            <div class="phase-card" data-phase-id="${phase.id}" onclick="dashboard.showPhaseDetails(${phase.id})">
                <div class="phase-number">${phase.id}</div>
                <div class="phase-info">
                    <div class="phase-status ${phase.status}">${phase.status.replace('_', ' ')}</div>
                    <div class="phase-name">${phase.name}</div>
                    ${phase.completedAt ? `<div class="phase-completed">${phase.completedAt}</div>` : 
                      phase.lastUpdated ? `<div class="phase-updated">Updated: ${this.formatLastUpdated(phase.lastUpdated)}</div>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    renderWorkpackages() {
        const container = document.getElementById('workpackages-container');
        if (!container) return;
        
        const workpackages = this.data.workpackages;
        if (!workpackages || workpackages.error) {
            container.innerHTML = '<div class="loading">Error loading workpackages</div>';
            return;
        }
        
        let filteredPackages = workpackages.workpackages || [];
        
        // Apply phase filter
        if (this.filters.phase) {
            filteredPackages = filteredPackages.filter(wp => 
                wp.phase.toString() === this.filters.phase
            );
        }
        
        if (filteredPackages.length === 0) {
            container.innerHTML = '<div class="loading">No workpackages match the current filters</div>';
            return;
        }
        
        container.innerHTML = filteredPackages.map(wp => `
            <div class="workpackage-card">
                <div class="workpackage-header">
                    <div class="workpackage-id">WP-${wp.id.toString().padStart(3, '0')}</div>
                    <div class="workpackage-phase">Phase ${wp.phase}</div>
                </div>
                <div class="flow-details">
                    <div class="flow-detail">
                        <strong>Flow:</strong> ${wp.flowId}
                    </div>
                    <div class="flow-detail">
                        <strong>Entry Point:</strong> ${wp.entryPoint}
                    </div>
                    <div class="flow-detail">
                        <strong>Modules:</strong> ${wp.modules ? wp.modules.length : 0}
                    </div>
                    <div class="flow-detail">
                        <strong>Priority Score:</strong> ${wp.priorityScore || 0}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
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
            return dateString;
        }
    }
    
    formatLastUpdated(dateString) {
        try {
            // Parse the date properly handling timezone
            let date;
            if (dateString.includes('Z')) {
                // UTC time - convert to Korean time
                date = new Date(dateString);
            } else if (dateString.includes('+09:00')) {
                // Already Korean time
                date = new Date(dateString);
            } else {
                // Assume UTC if no timezone specified
                date = new Date(dateString + 'Z');
            }
            
            // Get current time in Korean timezone
            const now = new Date();
            const kstOffset = 9 * 60; // KST is UTC+9
            const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
            const kstNow = new Date(utc + (kstOffset * 60000));
            
            const diffMs = kstNow - date;
            const diffMins = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffHours / 24);
            
            if (diffMins < 1) {
                return 'Just now';
            } else if (diffMins < 60) {
                return `${diffMins}m ago`;
            } else if (diffHours < 24) {
                return `${diffHours}h ago`;
            } else if (diffDays < 7) {
                return `${diffDays}d ago`;
            } else {
                return date.toLocaleDateString('ko-KR', { 
                    month: 'short', 
                    day: 'numeric',
                    timeZone: 'Asia/Seoul'
                });
            }
        } catch (e) {
            console.error('Error formatting date:', e);
            return 'Recently';
        }
    }
    
    showError(message) {
        console.error(message);
        // Could implement a toast notification here
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    // Phase details handler - will be initialized after modules are loaded
    showPhaseDetails(phaseId) {
        console.log('showPhaseDetails called for phase:', phaseId);
        if (window.phaseDetailsHandler) {
            window.phaseDetailsHandler.showPhaseDetails(phaseId);
        } else {
            console.error('Phase details handler not initialized. Available handlers:', {
                phaseDetailsHandler: window.phaseDetailsHandler,
                PhaseDetailsHandler: window.PhaseDetailsHandler
            });
            // Try to initialize if class is available
            if (window.PhaseDetailsHandler) {
                console.log('Attempting to initialize PhaseDetailsHandler...');
                window.phaseDetailsHandler = new PhaseDetailsHandler(this);
                window.phaseDetailsHandler.showPhaseDetails(phaseId);
            }
        }
    }
}

// Initialize dashboard and modules when DOM is loaded
let dashboard;
let phaseDetailsHandler;
let workpackageAnalysis;
let fileModal;
let tabNavigation;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    
    // Initialize tab navigation first
    if (window.TabNavigation) {
        console.log('Initializing TabNavigation...');
        tabNavigation = new TabNavigation();
        tabNavigation.initializeTabs();
        window.tabNavigation = tabNavigation;
    } else {
        console.error('TabNavigation class not found');
    }
    
    // Initialize main dashboard
    dashboard = new MigrationDashboard();
    
    // Wait a bit for other scripts to load, then initialize modules
    setTimeout(() => {
        console.log('Initializing modules...');
        console.log('Available classes:', {
            PhaseDetailsHandler: window.PhaseDetailsHandler,
            WorkpackageAnalysisHandler: window.WorkpackageAnalysisHandler,
            FileModalHandler: window.FileModalHandler
        });
        
        // Initialize modules
        if (window.PhaseDetailsHandler) {
            console.log('Initializing PhaseDetailsHandler...');
            phaseDetailsHandler = new PhaseDetailsHandler(dashboard);
            window.phaseDetailsHandler = phaseDetailsHandler;
        } else {
            console.error('PhaseDetailsHandler class not found');
        }
        
        if (window.WorkpackageAnalysisHandler) {
            console.log('Initializing WorkpackageAnalysisHandler...');
            workpackageAnalysis = new WorkpackageAnalysisHandler();
            window.workpackageAnalysis = workpackageAnalysis;
        } else {
            console.warn('WorkpackageAnalysisHandler class not found');
        }
        
        if (window.FileModalHandler) {
            console.log('Initializing FileModalHandler...');
            fileModal = new FileModalHandler();
            window.fileModal = fileModal;
        } else {
            console.warn('FileModalHandler class not found');
        }
        
        console.log('Module initialization complete');
    }, 200);
    
    // Make dashboard globally available
    window.dashboard = dashboard;
});