/**
 * Workpackage Summary Handler
 * Handles Phase 2 Workpackage summary statistics and visualizations
 */

class WorkpackageSummaryHandler {
    constructor() {
        this.workpackageData = null;
        this.dependencyData = null;
    }
    
    async loadWorkpackageData() {
        try {
            console.log('Loading workpackage data...');
            // Load workpackage planning data from new location
            const planningResponse = await fetch('/api/file/content?path=output/analysis/workpackages/Workpackage_Planning.json');
            
            console.log('Fetch response status:', planningResponse.status);
            
            if (!planningResponse.ok) {
                console.error('Failed to fetch Workpackage_Planning.json:', planningResponse.status);
                return false;
            }
            
            const planningData = await planningResponse.json();
            console.log('Planning data received:', planningData);
            
            if (!planningData.content) {
                console.error('No content in Workpackage_Planning.json response');
                return false;
            }
            
            console.log('Parsing content...');
            const planning = JSON.parse(planningData.content);
            console.log('Parsed planning:', planning);
            
            this.workpackageData = planning.flowPriorities; // Extract flow priorities
            this.statistics = planning.statistics;
            this.phases = planning.phases;
            
            console.log('Workpackage data loaded successfully:', {
                totalFlows: this.statistics?.totalFlows,
                flowCount: Object.keys(this.workpackageData || {}).length,
                hasStatistics: !!this.statistics,
                hasWorkpackageData: !!this.workpackageData
            });
            
            return true;
        } catch (error) {
            console.error('Error loading workpackage data:', error);
            console.error('Error stack:', error.stack);
            return false;
        }
    }
    
    parsePhaseData(roadmapContent) {
        const phases = {};
        const lines = roadmapContent.split('\n');
        let currentPhase = null;
        
        for (const line of lines) {
            const phaseMatch = line.match(/### Phase (\d+)/);
            if (phaseMatch) {
                currentPhase = parseInt(phaseMatch[1]);
                phases[currentPhase] = { workpackages: [], count: 0 };
            } else if (currentPhase && line.includes('**Workpackages**:')) {
                const wpMatch = line.match(/\*\*Workpackages\*\*:\s*(.+)/);
                if (wpMatch) {
                    const wpList = wpMatch[1].split(',').map(wp => wp.trim());
                    phases[currentPhase].workpackages = wpList;
                    phases[currentPhase].count = wpList.length;
                }
            }
        }
        
        return phases;
    }
    
    async renderWorkpackageSummary() {
        const loaded = await this.loadWorkpackageData();
        if (!loaded || !this.workpackageData) {
            return '<div class="error">Failed to load workpackage data</div>';
        }
        
        const stats = this.calculateStatistics();
        const chartId = `wp-chart-${Date.now()}`;
        
        const summaryHtml = `
            <div class="summary-grid">
                <div class="text-container">
                    <h4>Workpackage Overview</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">Total Workpackages:</span>
                            <span class="text-stat-value">${stats.totalWorkpackages}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Total Phases:</span>
                            <span class="text-stat-value">${stats.totalPhases}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Average Complexity:</span>
                            <span class="text-stat-value">${stats.avgComplexity}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Total Modules:</span>
                            <span class="text-stat-value">${stats.totalModules}</span>
                        </div>
                        <div class="text-stat-item ${stats.highComplexityCount > 0 ? 'high' : ''}">
                            <span class="text-stat-label">High Complexity (20+):</span>
                            <span class="text-stat-value">${stats.highComplexityCount}</span>
                        </div>
                        <div class="text-stat-item ${stats.completionRate >= 80 ? 'success' : stats.completionRate >= 50 ? 'warning' : 'error'}">
                            <span class="text-stat-label">Complete Flows:</span>
                            <span class="text-stat-value">${stats.completionRate}%</span>
                        </div>
                    </div>
                </div>
                <div class="chart-container">
                    <h4>Complexity Distribution</h4>
                    <canvas id="complexityChart-${chartId}" width="300" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h4>Priority vs Complexity</h4>
                    <canvas id="priorityChart-${chartId}" width="300" height="200"></canvas>
                </div>
            </div>
        `;
        
        setTimeout(() => {
            this.renderCharts(stats, chartId);
        }, 100);
        
        return summaryHtml;
    }
    
    calculateStatistics() {
        if (!this.workpackageData || !this.statistics) {
            return {
                totalWorkpackages: 0,
                totalPhases: 0,
                avgComplexity: '0.0',
                totalModules: 0,
                highComplexityCount: 0,
                completionRate: 0
            };
        }
        
        const stats = {
            totalWorkpackages: this.statistics.totalFlows || 0,
            totalPhases: this.statistics.totalPhases || 0,
            avgComplexity: '0.0',
            totalModules: 0,
            highComplexityCount: 0,
            completionRate: 0,
            phaseDistribution: this.statistics.flowsPerPhase || {},
            businessDomains: {}
        };
        
        let totalComplexity = 0;
        let totalModules = 0;
        let completeFlows = 0;
        let count = 0;
        
        // Iterate through flowPriorities to calculate statistics
        Object.keys(this.workpackageData).forEach(flowId => {
            const wp = this.workpackageData[flowId];
            const complexity = wp.priorityFactors?.compositeScore || 0;
            const modules = wp.priorityFactors?.totalPrograms || 0;
            
            totalComplexity += complexity;
            totalModules += modules;
            count++;
            
            // High complexity count (composite score >= 20)
            if (complexity >= 20) {
                stats.highComplexityCount++;
            }
            
            // Complete flow bonus indicates complete flows
            if (wp.priorityFactors?.completeFlowBonus && wp.priorityFactors.completeFlowBonus < 0) {
                completeFlows++;
            }
        });
        
        if (count > 0) {
            stats.avgComplexity = (totalComplexity / count).toFixed(1);
            stats.totalModules = totalModules;
            stats.completionRate = Math.round((completeFlows / count) * 100);
        }
        
        console.log('Completion rate calculation:', {
            completeFlows,
            totalFlows: count,
            completionRate: stats.completionRate,
            completionRateType: typeof stats.completionRate,
            colorClass: stats.completionRate >= 80 ? 'success' : stats.completionRate >= 50 ? 'warning' : 'error',
            test80: stats.completionRate >= 80,
            test50: stats.completionRate >= 50
        });
        
        return stats;
    }
    
    renderPhaseDistribution(stats) {
        if (!stats.phaseDistribution) return '';
        
        const phases = Object.keys(stats.phaseDistribution)
            .sort((a, b) => parseInt(a) - parseInt(b));
        
        // Create compact 2-column layout
        let html = '<div class="phase-distribution-compact">';
        
        for (let i = 0; i < phases.length; i += 2) {
            html += '<div class="phase-row">';
            
            // Left column
            const phase1 = phases[i];
            const count1 = stats.phaseDistribution[phase1];
            html += `
                <div class="phase-item">
                    <span class="phase-label">P${phase1}</span>
                    <span class="phase-count">${count1}</span>
                </div>
            `;
            
            // Right column (if exists)
            if (i + 1 < phases.length) {
                const phase2 = phases[i + 1];
                const count2 = stats.phaseDistribution[phase2];
                html += `
                    <div class="phase-item">
                        <span class="phase-label">P${phase2}</span>
                        <span class="phase-count">${count2}</span>
                    </div>
                `;
            }
            
            html += '</div>';
        }
        
        html += '</div>';
        
        // Add expandable detailed view
        html += `
            <div class="phase-details-toggle" onclick="this.nextElementSibling.classList.toggle('expanded')">
                <span>View Details</span>
                <i class="fas fa-chevron-down"></i>
            </div>
            <div class="phase-details-expandable">
                ${this.renderDetailedPhaseDistribution(stats)}
            </div>
        `;
        
        return html;
    }
    
    renderDetailedPhaseDistribution(stats) {
        let html = '';
        Object.keys(stats.phaseDistribution)
            .sort((a, b) => parseInt(a) - parseInt(b))
            .forEach(phase => {
                const count = stats.phaseDistribution[phase];
                // Use this.phases instead of this.phaseData
                const phaseInfo = this.phases?.[phase] || {};
                const workpackages = phaseInfo.workpackages || [];
                
                html += `
                    <div class="phase-group-detailed">
                        <div class="phase-header-detailed">
                            <span class="phase-label">Phase ${phase}</span>
                            <span class="phase-count">${count} workpackages</span>
                        </div>
                        <div class="workpackage-list-compact">
                            ${workpackages.map(wpId => {
                                const wp = this.workpackageData.find(w => w.workpackage_id === wpId);
                                if (!wp) return '';
                                return `
                                    <span class="wp-tag complexity-${this.getComplexityLevel(wp.complexity)}" title="Complexity: ${wp.complexity}, Entry: ${wp.entry_point}">
                                        ${wp.workpackage_id}
                                    </span>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });
        
        return html;
    }
    

    
    getPriorityLevel(priority) {
        const p = parseInt(priority);
        if (p <= 10) return 'high';
        if (p <= 30) return 'medium';
        return 'low';
    }
    
    getComplexityLevel(complexityScore) {
        const c = parseFloat(complexityScore) || 0;
        if (c >= 20) return 'high';       // High complexity (20+)
        if (c >= 10) return 'medium';     // Medium complexity (10-19)
        return 'low';                     // Low complexity (0-9)
    }
    
    renderCharts(stats, chartId) {
        if (typeof Chart === 'undefined') return;
        
        // Complexity Distribution Chart
        this.renderComplexityDistribution(stats, chartId);
        
        // Priority vs Complexity Scatter Chart
        this.renderPriorityComplexityChart(chartId);
    }
    
    renderComplexityDistribution(stats, chartId) {
        if (!this.workpackageData) return;
        
        // Convert workpackageData object to array of values
        const workpackages = Object.values(this.workpackageData);
        const complexities = workpackages.map(wp => wp.priorityFactors?.compositeScore || 0);
        const ranges = {
            'Low (0-10)': complexities.filter(c => c >= 0 && c <= 10).length,
            'Medium (11-25)': complexities.filter(c => c >= 11 && c <= 25).length,
            'High (26-50)': complexities.filter(c => c >= 26 && c <= 50).length,
            'Very High (51+)': complexities.filter(c => c >= 51).length
        };
        
        const ctx = document.getElementById(`complexityChart-${chartId}`);
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(ranges),
                    datasets: [{
                        data: Object.values(ranges),
                        backgroundColor: ['#2ed573', '#ffa502', '#ff6348', '#ff4757']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { font: { size: 10 } }
                        }
                    }
                }
            });
        }
    }
    
    renderPriorityComplexityChart(chartId) {
        if (!this.workpackageData) return;
        
        // Convert workpackageData object to array of values
        const workpackages = Object.values(this.workpackageData);
        const scatterData = workpackages.map(wp => ({
            x: wp.priorityScore || 0,
            y: wp.priorityFactors?.compositeScore || 0,
            label: wp.workpackageId
        }));
        
        const ctx = document.getElementById(`priorityChart-${chartId}`);
        if (ctx) {
            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Workpackages',
                        data: scatterData,
                        backgroundColor: '#4ecdc4',
                        borderColor: '#4ecdc4'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            title: { display: true, text: 'Priority Score (lower = higher priority)' },
                            beginAtZero: false
                        },
                        y: {
                            title: { display: true, text: 'Complexity' },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.raw.label}: Priority ${context.parsed.x}, Complexity ${context.parsed.y}`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
}

// Create global instance
window.workpackageSummaryHandler = new WorkpackageSummaryHandler();