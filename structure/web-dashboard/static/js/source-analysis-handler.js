/**
 * Source Analysis Handler
 * Handles Phase 1 Source Analysis specific functionality including dependency graphs
 */

class SourceAnalysisHandler {
    constructor() {
        this.network = null;
        this.originalGraphData = null;
        this.currentNodes = null;
        this.currentEdges = null;
    }
    
    renderSummaryCharts(summary) {
        const chartId = `chart-${Date.now()}`;
        
        const chartsHtml = `
            <div class="summary-grid">
                <div class="text-container">
                    <h4>COBOL Source Analysis</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">Total Files:</span>
                            <span class="text-stat-value">${summary.cobol_source_analysis?.total_files_analyzed || 0}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Entry Points:</span>
                            <span class="text-stat-value">${summary.cobol_source_analysis?.entry_points_identified || 0}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Business Flows:</span>
                            <span class="text-stat-value">${summary.cobol_source_analysis?.business_flows_mapped || 0}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Dependencies:</span>
                            <span class="text-stat-value">${summary.cobol_source_analysis?.dependency_relationships || 0}</span>
                        </div>
                    </div>
                </div>
                <div class="text-container">
                    <h4>Completeness Analysis</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">Missing Modules:</span>
                            <span class="text-stat-value">${summary.completeness_analysis?.total_missing_modules || 0}</span>
                        </div>
                        <div class="text-stat-item critical">
                            <span class="text-stat-label">Critical Impact:</span>
                            <span class="text-stat-value">${summary.completeness_analysis?.critical_impact_modules || 0}</span>
                        </div>
                        <div class="text-stat-item high">
                            <span class="text-stat-label">High Impact:</span>
                            <span class="text-stat-value">${summary.completeness_analysis?.high_impact_modules || 0}</span>
                        </div>
                        <div class="text-stat-item medium">
                            <span class="text-stat-label">Medium Impact:</span>
                            <span class="text-stat-value">${summary.completeness_analysis?.medium_impact_modules || 0}</span>
                        </div>
                    </div>
                </div>
                <div class="text-container">
                    <h4>Database Analysis</h4>
                    <div class="text-stats">
                        <div class="text-stat-item">
                            <span class="text-stat-label">Tables Analyzed:</span>
                            <span class="text-stat-value">${summary.database_analysis?.total_tables_analyzed || 0}</span>
                        </div>
                        <div class="text-stat-item success">
                            <span class="text-stat-label">Migration Success:</span>
                            <span class="text-stat-value">${summary.database_analysis?.migration_success_rate || 'N/A'}</span>
                        </div>
                        <div class="text-stat-item ${(summary.database_analysis?.blocking_issues || 0) > 0 ? 'critical' : 'success'}">
                            <span class="text-stat-label">Blocking Issues:</span>
                            <span class="text-stat-value">${summary.database_analysis?.blocking_issues || 0}</span>
                        </div>
                        <div class="text-stat-item">
                            <span class="text-stat-label">Target Systems:</span>
                            <span class="text-stat-value">${summary.database_analysis?.target_systems?.length || 0}</span>
                        </div>
                    </div>
                </div>
                <div class="chart-container">
                    <h4>Module Classifications</h4>
                    <canvas id="moduleTypesChart-${chartId}" width="300" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h4>Complexity Distribution</h4>
                    <canvas id="complexityChart-${chartId}" width="300" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h4>Impact Analysis</h4>
                    <canvas id="impactChart-${chartId}" width="300" height="200"></canvas>
                </div>
            </div>
        `;
        
        setTimeout(() => {
            this.renderCharts(summary, chartId);
        }, 100);
        
        return chartsHtml;
    }
    
    renderCharts(summary, chartId) {
        const moduleTypesData = summary.cobol_source_analysis?.module_classifications || {};
        if (Object.keys(moduleTypesData).length > 0 && typeof Chart !== 'undefined') {
            const ctx2 = document.getElementById(`moduleTypesChart-${chartId}`);
            if (ctx2) {
                new Chart(ctx2, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(moduleTypesData).map(k => k.replace('_', ' ')),
                        datasets: [{
                            data: Object.values(moduleTypesData),
                            backgroundColor: ['#ff6b6b', '#4ecdc4', '#ffa726']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }
        }
        this.loadEnhancedStatistics(chartId);
        this.renderImpactChart(summary, chartId);
    }
    
    async loadEnhancedStatistics(chartId) {
        try {
            const moduleResponse = await fetch('/api/file/content?path=output/analysis/source_code_analysis/COBOL_Module_Classifications.json');
            const moduleData = await moduleResponse.json();
            
            if (moduleResponse.ok && moduleData.content) {
                const modules = JSON.parse(moduleData.content).modules;
                this.renderComplexityChart(modules, chartId);
                this.renderCodeMetrics(modules, chartId);
            }
        } catch (error) {
            console.error('Error loading enhanced statistics:', error);
        }
    }
    
    renderComplexityChart(modules, chartId) {
        if (typeof Chart === 'undefined') return;
        
        const complexities = modules.map(m => m.complexity || 0);
        const ranges = {
            'Low (1-5)': complexities.filter(c => c >= 1 && c <= 5).length,
            'Medium (6-15)': complexities.filter(c => c >= 6 && c <= 15).length,
            'High (16-25)': complexities.filter(c => c >= 16 && c <= 25).length,
            'Very High (26+)': complexities.filter(c => c >= 26).length
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
    
    renderCodeMetrics(modules, chartId) {
        const totalLOC = modules.reduce((sum, m) => sum + (m.linesOfCode || 0), 0);
        const avgComplexity = modules.length > 0 ? 
            (modules.reduce((sum, m) => sum + (m.complexity || 0), 0) / modules.length).toFixed(1) : 0;
        const maxComplexity = Math.max(...modules.map(m => m.complexity || 0));
        const avgLOC = modules.length > 0 ? Math.round(totalLOC / modules.length) : 0;
        
        const container = document.getElementById(`codeMetrics-${chartId}`);
        if (container) {
            container.innerHTML = `
                <div class="text-stat-item">
                    <span class="text-stat-label">Total Lines of Code:</span>
                    <span class="text-stat-value">${totalLOC.toLocaleString()}</span>
                </div>
                <div class="text-stat-item">
                    <span class="text-stat-label">Average Complexity:</span>
                    <span class="text-stat-value">${avgComplexity}</span>
                </div>
                <div class="text-stat-item ${maxComplexity > 25 ? 'high' : ''}">
                    <span class="text-stat-label">Max Complexity:</span>
                    <span class="text-stat-value">${maxComplexity}</span>
                </div>
                <div class="text-stat-item">
                    <span class="text-stat-label">Average LOC per Module:</span>
                    <span class="text-stat-value">${avgLOC}</span>
                </div>
            `;
        }
    }
    
    renderImpactChart(summary, chartId) {
        if (typeof Chart === 'undefined') return;
        
        const completeness = summary.completeness_analysis;
        if (!completeness) return;
        
        const impactData = {
            'Critical': completeness.critical_impact_modules || 0,
            'High': completeness.high_impact_modules || 0,
            'Medium': completeness.medium_impact_modules || 0,
            'Low': completeness.low_impact_modules || 0
        };
        
        const ctx = document.getElementById(`impactChart-${chartId}`);
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(impactData),
                    datasets: [{
                        data: Object.values(impactData),
                        backgroundColor: ['#ff4757', '#ff6348', '#ffa502', '#2ed573']
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
  
    async showDependencyGraph() {
        try {
            // Exclude high-degree copybooks and external modules that create noise
            // Also exclude copybooks by default for cleaner graph
            const excludeNodes = 'YCCOMMON,YCDBSQLA,YCCSICOM,YCCBICOM,YCDBIOCA,YCFCTLAR,INZUTILB,ZUGDBUD';
            const response = await fetch(`/api/dependency-graph?excludeNodes=${excludeNodes}&excludeHighDegree=true&maxDegree=100&showCopybooks=false`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load dependency data');
            }
            
            this.displayDependencyModal(data);
            
        } catch (error) {
            console.error('Error loading dependency graph:', error);
            alert(`Error loading dependency graph: ${error.message}`);
        }
    }
    
    displayDependencyModal(graphData) {
        let modal = document.getElementById('dependency-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'dependency-modal';
            modal.className = 'file-modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>COBOL Dependency Graph</h3>
                        <div class="graph-controls">
                            <span class="graph-stats">Nodes: ${graphData.stats.totalNodes} | Edges: ${graphData.stats.totalEdges}</span>
                            <span class="modal-close">&times;</span>
                        </div>
                    </div>
                    <div class="graph-filters compact">
                        <div class="filter-row">
                            <div class="filter-item">
                                <label>Entry Point:</label>
                                <select id="entry-point-filter">
                                    <option value="">Select Entry Point...</option>
                                    ${graphData.nodes.filter(node => node.type === 'ENTRY_POINT')
                                        .sort((a, b) => a.id.localeCompare(b.id))
                                        .map(node => {
                                            const complexity = node.complexityTier && node.complexityTier !== 'Unknown' 
                                                ? node.complexityTier 
                                                : (node.complexity > 0 ? node.complexity.toFixed(0) : 'N/A');
                                            const connections = node.totalDegree || 0;
                                            const displayText = `${node.id} - Complexity: ${complexity}, Connections: ${connections}`;
                                            return `<option value="${node.id}">${displayText}</option>`;
                                        }).join('')}
                                </select>
                            </div>
                            <div class="filter-item depth-controls" style="display: none;">
                                <label>Depth: <span id="depth-value">All</span></label>
                                <input type="range" id="depth-slider" min="1" max="5" value="5" step="1">
                            </div>
                            <div class="filter-item">
                                <label>
                                    <input type="checkbox" id="show-missing-checkbox"> Show Missing
                                </label>
                            </div>
                            <div class="filter-item">
                                <label>
                                    <input type="checkbox" id="show-copybooks-checkbox"> Show Copybooks
                                </label>
                            </div>
                            <div class="filter-item">
                                <label>
                                    <input type="checkbox" id="show-jcl-checkbox" checked> Show JCL
                                </label>
                            </div>
                            <div class="filter-item">
                                <button id="reset-filters" class="btn-reset">Reset</button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div id="dependency-network" style="height: 500px; border: 1px solid #ddd;"></div>
                        <div class="graph-legend horizontal">
                            <div class="legend-row">
                                <div class="legend-group">
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #fc8d62;"></div>
                                        <span>Entry Point</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #8da0cb;"></div>
                                        <span>Single Use</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #66c2a5;"></div>
                                        <span>Commonly Used</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #e78ac3;"></div>
                                        <span>Copybook</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #b19cd9;"></div>
                                        <span>JCL</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #ffd92f;"></div>
                                        <span>Database</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #a6d854;"></div>
                                        <span>External</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #ff6b6b;"></div>
                                        <span>Missing</span>
                                    </div>
                                </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            this.setupModalEventListeners(modal);
        }
        
        modal.style.display = 'block';
        
        if (typeof vis !== 'undefined') {
            this.renderNetworkGraph(graphData);
        } else {
            document.getElementById('dependency-network').innerHTML = '<p>Network visualization library not loaded</p>';
        }
    }
    
    setupModalEventListeners(modal) {
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        modal.querySelector('#entry-point-filter').addEventListener('change', (e) => {
            const entryPoint = e.target.value;
            if (entryPoint) {
                modal.querySelector('.depth-controls').style.display = 'flex';
                this.applyGraphFilters();
            } else {
                modal.querySelector('.depth-controls').style.display = 'none';
                this.resetGraphFilters();
            }
        });
        
        modal.querySelector('#depth-slider').addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            const depthText = value === 5 ? 'All' : value.toString();
            modal.querySelector('#depth-value').textContent = depthText;
            
            const entryPoint = modal.querySelector('#entry-point-filter').value;
            if (entryPoint) {
                this.applyGraphFilters();
            }
        });
        
        modal.querySelector('#reset-filters').addEventListener('click', () => {
            this.resetGraphFilters();
        });
        

        
        modal.querySelector('#show-missing-checkbox').addEventListener('change', () => {
            this.reloadDependencyGraph();
        });
        
        modal.querySelector('#show-copybooks-checkbox').addEventListener('change', () => {
            this.reloadDependencyGraph();
        });
        
        modal.querySelector('#show-jcl-checkbox').addEventListener('change', () => {
            this.reloadDependencyGraph();
        });
    }
    
    renderNetworkGraph(graphData) {
        const container = document.getElementById('dependency-network');
        
        const nodes = graphData.nodes.map(node => {
            const nodeSize = this.calculateNodeSize(node);
            const nodeColor = this.getNodeColor(node.type);
            
            return {
                id: node.id,
                label: node.id,
                color: {
                    background: nodeColor,
                    border: this.getDarkerColor(nodeColor),
                    highlight: {
                        background: this.getLighterColor(nodeColor),
                        border: nodeColor
                    }
                },
                size: nodeSize,
                title: this.createNodeTooltip(node),
                font: {
                    size: Math.max(10, Math.min(16, nodeSize / 2)),
                    color: '#333333'
                },
                borderWidth: 2,
                shadow: node.type === 'ENTRY_POINT'
            };
        });
        
        const edges = graphData.edges.map(edge => ({
            from: edge.source,
            to: edge.target,
            color: {
                color: this.getEdgeColor(edge.type),
                highlight: this.getDarkerColor(this.getEdgeColor(edge.type))
            },
            title: `${edge.source} → ${edge.target}\nType: ${edge.type}`,
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 0.8
                }
            },
            width: this.getEdgeWidth(edge.type),
            smooth: { type: 'continuous' }
        }));
        
        const data = { nodes, edges };
        const options = {
            nodes: {
                shape: 'dot',
                font: { 
                    size: 12,
                    face: 'Arial',
                    strokeWidth: 2,
                    strokeColor: '#ffffff'
                },
                borderWidth: 2,
                scaling: {
                    min: 10,
                    max: 500
                },
                chosen: {
                    node: (values, id, selected, hovering) => {
                        values.size = values.size * 1.2;
                        values.borderWidth = 3;
                    }
                }
            },
            edges: {
                width: 2,
                smooth: { 
                    type: 'continuous',
                    forceDirection: 'none',
                    roundness: 0.1
                },
                chosen: {
                    edge: (values, id, selected, hovering) => {
                        values.width = values.width * 1.5;
                    }
                }
            },
            physics: {
                enabled: true,
                stabilization: { 
                    iterations: 150,
                    updateInterval: 25
                },
                barnesHut: {
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true,
                hideNodesOnDrag: false
            },
            layout: {
                improvedLayout: false
            }
        };
        
        this.network = new vis.Network(container, data, options);
        this.originalGraphData = graphData;
        this.currentNodes = nodes;
        this.currentEdges = edges;
        
        // Add network event listeners
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                this.onNodeClick(params.nodes[0], graphData);
            }
        });
    }
    
    getNodeColor(nodeType) {
        const colors = {
            'ENTRY_POINT': '#fc8d62',      // Orange - Entry points
            'COMMONLY_USED': '#66c2a5',    // Teal - Commonly used modules
            'UNUSED': '#8da0cb',           // Light blue - Unused modules
            'COPYBOOK': '#e78ac3',         // Pink - Copybooks
            'EXTERNAL': '#a6d854',         // Light green - External modules
            'DATABASE': '#ffd92f',         // Yellow - Database tables
            'SINGLE_USE': '#8da0cb',       // Light blue - Single use modules
            'MISSING': '#ff6b6b',          // Red - Missing modules
            'JCL': '#b19cd9'               // Purple - JCL scripts
        };
        return colors[nodeType] || '#9ca3af';
    }
    
    calculateNodeSize(node) {
        const baseSize = 10;
        
        // Size based on complexity tier
        let sizeMultiplier = 1;
        
        // First check complexity tier
        if (node.complexityTier) {
            switch (node.complexityTier) {
                case 'LOW':
                    sizeMultiplier = 1.0;   // 10 pixels
                    break;
                case 'MEDIUM':
                    sizeMultiplier = 2.0;   // 20 pixels
                    break;
                case 'HIGH':
                    sizeMultiplier = 3.0;   // 30 pixels
                    break;
                case 'VERY_HIGH':
                    sizeMultiplier = 4.0;   // 40 pixels
                    break;
                default:
                    sizeMultiplier = 1.0;
            }
        } else {
            // Fallback to node type if no complexity tier
            switch (node.type) {
                case 'ENTRY_POINT':
                    sizeMultiplier = 2.0;
                    break;
                case 'COMMONLY_USED':
                    sizeMultiplier = 1.5;
                    break;
                case 'DATABASE':
                    sizeMultiplier = 1.3;
                    break;
                case 'COPYBOOK':
                    sizeMultiplier = 1.1;
                    break;
                default:
                    sizeMultiplier = 1.0;
            }
        }
        
        return baseSize * sizeMultiplier;
    }
    
    createNodeTooltip(node) {
        const lines = [
            `${node.id}`,
            `Type: ${node.type}`,
            `Functionality: ${node.functionality || 'Unknown'}`,
            `Connections: ${(node.inDegree || 0) + (node.outDegree || 0)} (In: ${node.inDegree || 0}, Out: ${node.outDegree || 0})`
        ];
        
        if (node.complexity && node.complexity > 0) {
            lines.push(`Complexity: ${node.complexity.toFixed(1)}`);
        }
        
        if (node.complexityTier && node.complexityTier !== 'Unknown') {
            lines.push(`Complexity Tier: ${node.complexityTier}`);
        }
        
        return lines.join('\n');
    }
    
    getDarkerColor(color) {
        // Simple color darkening
        const hex = color.replace('#', '');
        const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - 40);
        const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - 40);
        const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - 40);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }
    
    getLighterColor(color) {
        // Simple color lightening
        const hex = color.replace('#', '');
        const r = Math.min(255, parseInt(hex.substr(0, 2), 16) + 40);
        const g = Math.min(255, parseInt(hex.substr(2, 2), 16) + 40);
        const b = Math.min(255, parseInt(hex.substr(4, 2), 16) + 40);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }
    
    getEdgeColor(edgeType) {
        const colors = {
            // High importance - based on node colors but with reduced opacity
            'ZKESA_DYCALL': 'rgba(252, 141, 98, 0.6)',    // Orange with 60% opacity - Dynamic calls
            'ZKESA_DYDBIO': 'rgba(255, 217, 47, 0.7)',    // Yellow with 70% opacity - Database I/O
            'DYNAMIC_CALL': 'rgba(252, 141, 98, 0.6)',    // Orange with 60% opacity - Dynamic calls
            
            // Medium importance - medium opacity
            'TABLE_ACCESS': 'rgba(255, 217, 47, 0.7)',    // Yellow with 70% opacity - Table access
            'ZKESA_DYSQLA': 'rgba(255, 217, 47, 0.7)',    // Yellow with 70% opacity - SQL access
            'SQL_TABLE': 'rgba(255, 217, 47, 0.7)',       // Yellow with 70% opacity - SQL table access
            'CALL': 'rgba(102, 194, 165, 0.8)',           // Teal with 80% opacity - Function calls
            
            // Low importance - very light colors
            'COPY': 'rgba(156, 163, 175, 0.5)',           // Gray with 50% opacity - Copy statements
            'JCL_EXEC': 'rgba(156, 163, 175, 0.3)',       // Gray with 30% opacity - JCL execution
            'INCLUDE': 'rgba(156, 163, 175, 0.3)',        // Gray with 30% opacity - Include statements
            'EXTERNAL': 'rgba(156, 163, 175, 0.2)'        // Gray with 20% opacity - External references
        };
        return colors[edgeType] || 'rgba(156, 163, 175, 0.3)';
    }
    
    getEdgeWidth(edgeType) {
        const widths = {
            'ZKESA_DYCALL': 3,      // Thicker for dynamic calls
            'ZKESA_DYDBIO': 3,      // Thicker for database I/O
            'ZKESA_DYSQLA': 2.5,    // Medium for SQL access
            'DYNAMIC_CALL': 3,      // Thicker for dynamic calls
            'TABLE_ACCESS': 2.5,    // Medium for table access
            'JCL_EXEC': 2,          // Standard for JCL
            'SQL_TABLE': 2.5,       // Medium for SQL
            'CALL': 2,              // Standard for calls
            'COPY': 1.5,            // Thinner for copy
            'INCLUDE': 1.5,         // Thinner for include
            'EXTERNAL': 1           // Thinnest for external
        };
        return widths[edgeType] || 2;
    }
    
    onNodeClick(nodeId, graphData) {
        const node = graphData.nodes.find(n => n.id === nodeId);
        if (!node) return;
        
        // Show detailed node information
        const info = `
            <div class="node-details">
                <h4>${node.id}</h4>
                <p><strong>Type:</strong> ${node.type}</p>
                <p><strong>Domain:</strong> ${node.domain || 'Unknown'}</p>
                <p><strong>Usage:</strong> ${node.usage || 'Unknown'}</p>
                <p><strong>Functionality:</strong> ${node.functionality || 'Unknown'}</p>
                <p><strong>Connections:</strong> ${(node.inDegree || 0) + (node.outDegree || 0)} total</p>
                <p><strong>Incoming:</strong> ${node.inDegree || 0}</p>
                <p><strong>Outgoing:</strong> ${node.outDegree || 0}</p>
                ${node.complexity ? `<p><strong>Complexity:</strong> ${node.complexity}</p>` : ''}
            </div>
        `;
        
        // You could show this in a tooltip or sidebar
        console.log('Node clicked:', node);
    }
    
    applyGraphFilters() {
        const modal = document.getElementById('dependency-modal');
        const entryPoint = modal.querySelector('#entry-point-filter').value;
        const depth = parseInt(modal.querySelector('#depth-slider').value);
        
        if (!entryPoint || !this.originalGraphData) return;
        
        const filteredData = this.filterGraphByEntryPoint(entryPoint, depth);
        this.updateNetworkGraph(filteredData);
    }
    
    filterGraphByEntryPoint(entryPointId, maxDepth) {
        const visited = new Set();
        const nodesToInclude = new Set();
        const edgesToInclude = new Set();
        
        const traverse = (nodeId, currentDepth) => {
            if (currentDepth > maxDepth || visited.has(nodeId)) return;
            
            visited.add(nodeId);
            nodesToInclude.add(nodeId);
            
            if (currentDepth < maxDepth) {
                this.originalGraphData.edges.forEach(edge => {
                    if (edge.source === nodeId) {
                        edgesToInclude.add(`${edge.source}-${edge.target}`);
                        traverse(edge.target, currentDepth + 1);
                    }
                });
            }
        };
        
        traverse(entryPointId, 0);
        
        return {
            nodes: this.originalGraphData.nodes.filter(node => nodesToInclude.has(node.id)),
            edges: this.originalGraphData.edges.filter(edge => 
                edgesToInclude.has(`${edge.source}-${edge.target}`)
            )
        };
    }
    
    updateNetworkGraph(filteredData) {
        if (!this.network) return;
        
        const nodes = filteredData.nodes.map(node => ({
            id: node.id,
            label: node.id,
            color: this.getNodeColor(node.type),
            size: Math.max(10, Math.min(30, node.size * 3)),
            title: this.createNodeTooltip(node)
        }));
        
        const edges = filteredData.edges.map(edge => ({
            from: edge.source,
            to: edge.target,
            color: this.getEdgeColor(edge.type),
            title: `${edge.source} → ${edge.target}\nType: ${edge.type}`,
            arrows: 'to'
        }));
        
        this.network.setData({ nodes, edges });
        this.currentNodes = nodes;
        this.currentEdges = edges;
    }
    
    resetGraphFilters() {
        const modal = document.getElementById('dependency-modal');
        modal.querySelector('#entry-point-filter').value = '';
        modal.querySelector('#depth-slider').value = '5';
        modal.querySelector('#depth-value').textContent = 'All';
        modal.querySelector('.depth-controls').style.display = 'none';
        
        if (this.network && this.originalGraphData) {
            this.renderNetworkGraph(this.originalGraphData);
        }
    }
    
    async reloadDependencyGraph() {
        const modal = document.getElementById('dependency-modal');
        const showMissing = modal.querySelector('#show-missing-checkbox').checked;
        const showCopybooks = modal.querySelector('#show-copybooks-checkbox').checked;
        const showJcl = modal.querySelector('#show-jcl-checkbox').checked;
        
        // Save current filter state
        const currentEntryPoint = modal.querySelector('#entry-point-filter').value;
        const currentDepth = modal.querySelector('#depth-slider').value;
        const depthControlsVisible = modal.querySelector('.depth-controls').style.display !== 'none';
        
        try {
            // Build filter parameters
            const excludeNodes = 'YCCOMMON,YCDBSQLA,YCCSICOM,YCCBICOM,YCDBIOCA,YCFCTLAR,INZUTILB,ZUGDBUD';
            const params = new URLSearchParams({
                showMissing: showMissing,
                showCopybooks: showCopybooks,
                showJcl: showJcl,
                excludeNodes: excludeNodes,
                excludeHighDegree: 'true',
                maxDegree: '100'
            });
            
            const response = await fetch(`/api/dependency-graph?${params.toString()}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to reload dependency data');
            }
            
            // Update stats
            modal.querySelector('.graph-stats').textContent = 
                `Nodes: ${data.stats.totalNodes} | Edges: ${data.stats.totalEdges}`;
            
            if (currentEntryPoint) {
                // Update entry point dropdown with new data
                const entryPointSelect = modal.querySelector('#entry-point-filter');
                entryPointSelect.innerHTML = `
                    <option value="">Select Entry Point...</option>
                    ${data.nodes.filter(node => node.type === 'ENTRY_POINT')
                        .sort((a, b) => a.id.localeCompare(b.id))
                        .map(node => {
                            const complexity = node.complexityTier && node.complexityTier !== 'Unknown' 
                                ? node.complexityTier 
                                : (node.complexity > 0 ? node.complexity.toFixed(0) : 'N/A');
                            const connections = node.totalDegree || 0;
                            const displayText = `${node.id} - Complexity: ${complexity}, Connections: ${connections}`;
                            return `<option value="${node.id}">${displayText}</option>`;
                        }).join('')}
                `;
                
                // Restore previous selection if it still exists
                if ([...entryPointSelect.options].some(option => option.value === currentEntryPoint)) {
                    entryPointSelect.value = currentEntryPoint;
                    modal.querySelector('#depth-slider').value = currentDepth;
                    modal.querySelector('#depth-value').textContent = currentDepth === '5' ? 'All' : currentDepth;
                    modal.querySelector('.depth-controls').style.display = depthControlsVisible ? 'flex' : 'none';
                    
                    // Apply filters with new data
                    this.originalGraphData = data;
                    this.applyGraphFilters();
                } else {
                    // Entry point no longer exists, reset filters
                    this.originalGraphData = data;
                    this.resetGraphFilters();
                }
            } else {
                // No filters applied, just update the graph
                this.renderNetworkGraph(data);
            }
            
        } catch (error) {
            console.error('Error reloading dependency graph:', error);
            alert(`Error reloading dependency graph: ${error.message}`);
        }
    }
    
    async reloadGraphWithFilters() {
        try {
            const modal = document.getElementById('dependency-modal');
            const showMissing = modal.querySelector('#show-missing-checkbox').checked;
            const showCopybooks = modal.querySelector('#show-copybooks-checkbox').checked;
            
            // Build filter parameters
            let params = new URLSearchParams();
            params.append('showMissing', showMissing);
            params.append('excludeHighDegree', 'true');
            params.append('maxDegree', '100');
            
            if (!showCopybooks) {
                // If copybooks are disabled, exclude all copybooks
                params.append('showCopybooks', 'false');
            } else {
                // If copybooks are enabled, still exclude the major noise ones
                const excludeNodes = 'YCCOMMON,YCDBSQLA,YCCSICOM,YCCBICOM,YCDBIOCA';
                params.append('excludeNodes', excludeNodes);
            }
            
            const response = await fetch(`/api/dependency-graph?${params.toString()}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to reload dependency data');
            }
            
            // Update stats
            const statsSpan = modal.querySelector('.graph-stats');
            statsSpan.textContent = `Nodes: ${data.stats.totalNodes} | Edges: ${data.stats.totalEdges}`;
            
            // Reload the network
            this.createDependencyNetwork(data);
            
        } catch (error) {
            console.error('Error reloading dependency graph:', error);
            alert(`Error reloading dependency graph: ${error.message}`);
        }
    }
}

// Create global instance
window.sourceAnalysisHandler = new SourceAnalysisHandler();