/**
 * Business Flows Graph Visualization
 * Displays business flows as an interactive force-directed graph
 */

class BusinessFlowsGraphHandler {
    constructor() {
        this.graph = null;
        this.currentData = null;
    }
    
    async showBusinessFlowsGraph() {
        try {
            console.log('Loading business flows from: output/analysis/source_code/flows/Business_Flows.json');
            
            // Load Business_Flows.json by default
            const response = await fetch('/api/file/content?path=output/analysis/source_code/flows/Business_Flows.json');
            
            console.log('Response status:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Data received, has content:', !!data.content);
            
            if (!data.content) {
                throw new Error('No content in response');
            }
            
            const flowsData = JSON.parse(data.content);
            console.log('Flows data parsed, flow count:', flowsData.flows?.length || 0);
            
            this.displayBusinessFlowsModal(flowsData);
            
        } catch (error) {
            console.error('Error loading business flows graph:', error);
            alert(`Error loading business flows graph: ${error.message}`);
        }
    }
    
    displayBusinessFlowsModal(flowsData) {
        let modal = document.getElementById('business-flows-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'business-flows-modal';
            modal.className = 'file-modal';
            modal.innerHTML = `
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Business Flows Visualization</h3>
                        <div class="graph-controls">
                            <button id="load-flows-file" class="btn-graph">Load JSON File</button>
                            <input type="file" id="flows-file-input" accept=".json" style="display:none">
                            <span class="modal-close">&times;</span>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div id="business-flows-graph" style="height: 600px; border: 1px solid #ddd; background: #ffffff;"></div>
                        <div class="graph-legend horizontal">
                            <div class="legend-row">
                                <div class="legend-group">
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #E91E63;"></div>
                                        <span>Flow</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #2196F3;"></div>
                                        <span>Program</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #4CAF50;"></div>
                                        <span>Database (Active I/O)</span>
                                    </div>
                                    <div class="legend-item">
                                        <div class="legend-color" style="background: #FF9800;"></div>
                                        <span>Dataset (Referenced)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div id="flows-node-info" class="node-info-panel">
                            <h4>Node Information</h4>
                            <p>Click on a node to see details</p>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            this.setupModalEventListeners(modal);
        }
        
        modal.style.display = 'block';
        
        // Check if ForceGraph is available
        if (typeof ForceGraph !== 'undefined') {
            this.renderForceGraph(flowsData);
        } else {
            document.getElementById('business-flows-graph').innerHTML = 
                '<p style="padding: 20px;">Force Graph library not loaded. Please include the library.</p>';
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
        
        modal.querySelector('#load-flows-file').addEventListener('click', () => {
            modal.querySelector('#flows-file-input').click();
        });
        
        modal.querySelector('#flows-file-input').addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    this.renderForceGraph(data);
                } catch (error) {
                    alert('Error parsing JSON: ' + error.message);
                }
            };
            reader.readAsText(file);
        }
    }
    
    renderForceGraph(flowsData) {
        const container = document.getElementById('business-flows-graph');
        const graphData = this.transformBusinessFlows(flowsData);
        
        this.graph = ForceGraph()
            (container)
            .backgroundColor('#ffffff')
            .nodeLabel('name')
            .nodeColor(node => {
                switch(node.type) {
                    case 'flow': return '#E91E63';
                    case 'program': return '#2196F3';
                    case 'database': return '#4CAF50';
                    case 'dataset': return '#FF9800';
                    default: return '#9E9E9E';
                }
            })
            .nodeRelSize(6)
            .linkColor(() => 'rgba(0,0,0,0.15)')
            .linkWidth(2)
            .linkDirectionalArrowLength(3.5)
            .linkDirectionalArrowRelPos(1)
            .onNodeClick(node => {
                this.showNodeInfo(node);
            })
            .graphData(graphData);
        
        this.currentData = graphData;
    }
    
    transformBusinessFlows(data) {
        const nodes = [];
        const links = [];
        const nodeIds = new Set();

        data.flows.forEach(flow => {
            // Add flow node
            const flowId = flow.flowId;
            if (!nodeIds.has(flowId)) {
                nodes.push({
                    id: flowId,
                    name: flow.name || flowId,
                    type: 'flow',
                    complexity: flow.complexity?.compositeScore,
                    tier: flow.complexity?.tier,
                    entryPoint: flow.entryPoint?.program,
                    primaryType: flow.entryPoint?.primaryType
                });
                nodeIds.add(flowId);
            }

            // Add program nodes
            flow.scope?.programs?.forEach(prog => {
                const progId = `prog_${prog.name}`;
                if (!nodeIds.has(progId)) {
                    nodes.push({
                        id: progId,
                        name: prog.name,
                        type: 'program',
                        isUtility: prog.is_utility
                    });
                    nodeIds.add(progId);
                }
                links.push({
                    source: flowId,
                    target: progId,
                    type: 'contains'
                });
            });

            // Add database nodes and links
            flow.dataOperations?.databases?.forEach(db => {
                const dbId = `db_${db.target}`;
                if (!nodeIds.has(dbId)) {
                    nodes.push({
                        id: dbId,
                        name: db.target,
                        type: 'database',
                        dbType: db.type
                    });
                    nodeIds.add(dbId);
                }
                const sourceId = db.program ? `prog_${db.program}` : flowId;
                links.push({
                    source: sourceId,
                    target: dbId,
                    type: db.operation
                });
            });

            // Add dataset nodes (only if not already added as database)
            const databaseTargets = new Set(
                (flow.dataOperations?.databases || []).map(db => db.target)
            );
            
            flow.scope?.datasets?.forEach(ds => {
                // Skip if already added as a database
                if (databaseTargets.has(ds)) {
                    return;
                }
                
                const dsId = `ds_${ds}`;
                if (!nodeIds.has(dsId)) {
                    nodes.push({
                        id: dsId,
                        name: ds,
                        type: 'dataset'
                    });
                    nodeIds.add(dsId);
                }
                links.push({
                    source: flowId,
                    target: dsId,
                    type: 'uses'
                });
            });

            // Add flow dependencies
            flow.dependencies?.requiredFlows?.forEach(reqFlow => {
                links.push({
                    source: flowId,
                    target: reqFlow,
                    type: 'depends'
                });
            });
        });

        return { nodes, links };
    }
    
    showNodeInfo(node) {
        const infoPanel = document.getElementById('flows-node-info');
        
        let infoHtml = `
            <h4>Node Information</h4>
            <div class="node-detail-item">
                <strong>Name:</strong> ${node.name}
            </div>
            <div class="node-detail-item">
                <strong>Type:</strong> ${node.type}
            </div>
        `;
        
        if (node.complexity) {
            infoHtml += `
                <div class="node-detail-item">
                    <strong>Complexity:</strong> ${node.complexity}
                </div>
            `;
        }
        
        if (node.tier) {
            infoHtml += `
                <div class="node-detail-item">
                    <strong>Tier:</strong> ${node.tier}
                </div>
            `;
        }
        
        if (node.entryPoint) {
            infoHtml += `
                <div class="node-detail-item">
                    <strong>Entry Point:</strong> ${node.entryPoint}
                </div>
            `;
        }
        
        if (node.primaryType) {
            infoHtml += `
                <div class="node-detail-item">
                    <strong>Primary Type:</strong> ${node.primaryType}
                </div>
            `;
        }
        
        if (node.dbType) {
            infoHtml += `
                <div class="node-detail-item">
                    <strong>Database Type:</strong> ${node.dbType}
                </div>
            `;
        }
        
        if (node.isUtility !== undefined) {
            infoHtml += `
                <div class="node-detail-item">
                    <strong>Is Utility:</strong> ${node.isUtility ? 'Yes' : 'No'}
                </div>
            `;
        }
        
        infoPanel.innerHTML = infoHtml;
    }
}

// Create global instance
window.businessFlowsGraphHandler = new BusinessFlowsGraphHandler();
