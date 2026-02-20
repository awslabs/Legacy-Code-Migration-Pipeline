# Business Flows Graph Integration

## Overview
The business flows visualization from `html-test/index.html` has been integrated into the web-dashboard.

## Setup

The dashboard runs on port 5001 by default. Access it at: `http://localhost:5001`

## What Was Added

### 1. New JavaScript Handler
**File**: `web-dashboard/static/js/business-flows-graph.js`
- `BusinessFlowsGraphHandler` class that manages the force-directed graph visualization
- Loads `Business_Flows.json` by default
- Supports loading custom JSON files
- Transforms business flows data into graph nodes and links
- Interactive node clicking to show details

### 2. Updated Files

**File**: `web-dashboard/templates/index.html`
- Added force-graph library: `<script src="https://unpkg.com/force-graph"></script>`
- Added business-flows-graph.js script reference

**File**: `web-dashboard/static/js/phase1-details.js`
- Added "View Business Flows" button next to "View Dependency Graph" button
- Added click handler to open business flows graph modal

**File**: `web-dashboard/static/css/style.css`
- Added styles for node info panel
- Added styles for graph buttons
- Added button group layout styles

## How to Use

1. Navigate to the dashboard
2. Click on "Phase Details" tab
3. Click on "Phase 1: Source Analysis"
4. In the Summary Statistics section, click "View Business Flows" button
5. The graph will load with `Business_Flows.json` by default
6. Click on nodes to see details in the info panel
7. Use "Load JSON File" button to load a different JSON file

## Features

- **Interactive Graph**: Force-directed layout with draggable nodes
- **Color-Coded Nodes**:
  - Pink: Flow nodes
  - Blue: Program nodes
  - Green: Database nodes
  - Orange: Dataset nodes
- **Node Information**: Click any node to see details
- **Custom Data**: Load any compatible JSON file
- **Directional Links**: Shows relationships between nodes

## Data Format

The graph expects JSON in this format:
```json
{
  "flows": [
    {
      "flowId": "FLOW001",
      "name": "Flow Name",
      "entryPoint": { "program": "PROG1", "primaryType": "TYPE" },
      "scope": {
        "programs": [{ "name": "PROG1", "is_utility": false }],
        "datasets": ["DATASET1"]
      },
      "dataOperations": {
        "databases": [{ "type": "DB2", "operation": "READ", "target": "TABLE1", "program": "PROG1" }]
      },
      "complexity": { "compositeScore": 50, "tier": "MEDIUM" },
      "dependencies": { "requiredFlows": ["FLOW002"] }
    }
  ]
}
```

## Technical Details

- Uses force-graph library for visualization
- Renders in a modal overlay
- Graph is fully interactive with zoom and pan
- Automatically transforms business flows data into graph format
- Handles flow dependencies, program relationships, database operations, and dataset usage
