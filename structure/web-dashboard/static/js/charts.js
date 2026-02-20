/**
 * Charts and Visualizations for Migration Dashboard
 * Uses Chart.js for creating interactive charts
 */

class MigrationCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#2563eb',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            info: '#06b6d4',
            secondary: '#64748b'
        };
    }
    
    /**
     * Create phase progress chart
     */
    createPhaseProgressChart(canvasId, phases) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        const statusCounts = {
            completed: 0,
            in_progress: 0,
            unknown: 0
        };
        
        phases.forEach(phase => {
            statusCounts[phase.status] = (statusCounts[phase.status] || 0) + 1;
        });
        
        this.charts.phaseProgress = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Not Started'],
                datasets: [{
                    data: [
                        statusCounts.completed,
                        statusCounts.in_progress,
                        statusCounts.unknown
                    ],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.warning,
                        this.colors.secondary
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Create business domain distribution chart
     */
    createDomainDistributionChart(canvasId, flows) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        const domainCounts = {};
        flows.forEach(flow => {
            const domain = flow.businessDomain || 'Unknown';
            domainCounts[domain] = (domainCounts[domain] || 0) + 1;
        });
        
        const labels = Object.keys(domainCounts);
        const data = Object.values(domainCounts);
        const colors = this.generateColors(labels.length);
        
        this.charts.domainDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Flows',
                    data: data,
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Domain: ${context[0].label}`;
                            },
                            label: function(context) {
                                return `Flows: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Create complexity distribution chart
     */
    createComplexityChart(canvasId, flows) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        const complexityRanges = {
            'Low (0-10)': 0,
            'Medium (11-25)': 0,
            'High (26-50)': 0,
            'Very High (50+)': 0
        };
        
        flows.forEach(flow => {
            const complexity = flow.complexity || 0;
            if (complexity <= 10) {
                complexityRanges['Low (0-10)']++;
            } else if (complexity <= 25) {
                complexityRanges['Medium (11-25)']++;
            } else if (complexity <= 50) {
                complexityRanges['High (26-50)']++;
            } else {
                complexityRanges['Very High (50+)']++;
            }
        });
        
        this.charts.complexity = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(complexityRanges),
                datasets: [{
                    data: Object.values(complexityRanges),
                    backgroundColor: [
                        this.colors.success,
                        this.colors.info,
                        this.colors.warning,
                        this.colors.error
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} flows (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Create workpackage timeline chart
     */
    createTimelineChart(canvasId, workpackages) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        const phaseData = {};
        workpackages.forEach(wp => {
            const phase = `Phase ${wp.phase}`;
            if (!phaseData[phase]) {
                phaseData[phase] = 0;
            }
            phaseData[phase]++;
        });
        
        const labels = Object.keys(phaseData).sort();
        const data = labels.map(label => phaseData[label]);
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Workpackages per Phase',
                    data: data,
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                return `Workpackages: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Generate colors for charts
     */
    generateColors(count) {
        const baseColors = [
            this.colors.primary,
            this.colors.success,
            this.colors.warning,
            this.colors.error,
            this.colors.info,
            this.colors.secondary
        ];
        
        const colors = [];
        for (let i = 0; i < count; i++) {
            const baseColor = baseColors[i % baseColors.length];
            const opacity = 0.8 - (Math.floor(i / baseColors.length) * 0.2);
            colors.push(baseColor + Math.round(opacity * 255).toString(16).padStart(2, '0'));
        }
        
        return colors;
    }
    
    /**
     * Update all charts with new data
     */
    updateCharts(data) {
        if (data.overview && data.overview.phases) {
            this.createPhaseProgressChart('phaseProgressChart', data.overview.phases);
        }
        
        if (data.flows && data.flows.flows) {
            this.createDomainDistributionChart('domainChart', data.flows.flows);
            this.createComplexityChart('complexityChart', data.flows.flows);
        }
        
        if (data.workpackages && data.workpackages.workpackages) {
            this.createTimelineChart('timelineChart', data.workpackages.workpackages);
        }
    }
    
    /**
     * Destroy all charts
     */
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.charts = {};
    }
    
    /**
     * Resize all charts
     */
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }
}

// Export for use in main dashboard
window.MigrationCharts = MigrationCharts;