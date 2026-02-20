# Migration Dashboard

A web-based dashboard for visualizing and monitoring the COBOL to Java migration process.

## Overview

This dashboard provides a comprehensive view of the migration progress, allowing users to:
- Monitor migration phases and their completion status
- View detailed analysis results and reports
- Track workpackage progress and dependencies
- Visualize business flows and code generation results
- Access generated artifacts and documentation

## Features

- **Real-time Progress Tracking**: Monitor each migration phase
- **Interactive Visualizations**: Business flow diagrams, dependency graphs
- **Artifact Browser**: Browse generated code, reports, and documentation
- **Phase Navigation**: Easy navigation between migration phases
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Visualization**: D3.js for charts and graphs
- **Backend**: Python Flask (lightweight web server)
- **Data**: JSON files from migration output directories

## Quick Start

1. Install dependencies:
   ```bash
   pip install flask
   ```

2. Start the dashboard:
   ```bash
   python app.py
   ```

3. Open browser to `http://localhost:5000`

## Directory Structure

```
web-dashboard/
├── app.py                 # Flask application
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Images and icons
├── templates/           # HTML templates
├── data/               # Data processing utilities
└── config.py           # Configuration settings
```