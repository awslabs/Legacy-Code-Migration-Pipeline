# Visualization and Reporting Module

This module provides comprehensive visualization and reporting capabilities for the Legacy Analyzer.

## Components

### 1. GraphRenderer (`graph_renderer.py`)

Renders call graphs and program flows in multiple formats:

- **DOT Format**: For Graphviz rendering
- **Mermaid Format**: For markdown documentation
- **HTML Format**: Interactive visualizations using vis.js

**Features:**
- Color coding by complexity level (LOW, MEDIUM, HIGH, VERY_HIGH)
- Highlighting of missing artifacts in red
- Automatic legend generation
- Support for both CallGraph and ProgramFlow objects

**Example Usage:**
```python
from legacy_analyzer.visualization import GraphRenderer
from legacy_analyzer.models.flow import CallGraph

renderer = GraphRenderer(
    color_by_complexity=True,
    highlight_missing=True,
    include_legend=True
)

# Render as DOT
dot_output = renderer.render_dot(call_graph, complexity_data, missing_artifacts)

# Render as Mermaid
mermaid_output = renderer.render_mermaid(call_graph, complexity_data)

# Render as interactive HTML
html_output = renderer.render_html(call_graph, complexity_data, missing_artifacts)
```

### 2. ReportGenerator (`report_generator.py`)

Generates text-based reports for various analysis results:

- **Executive Summary**: High-level overview of analysis results
- **Artifact Detail Report**: Detailed information about a specific artifact
- **Package Report**: Migration package details
- **Complexity Summary**: Complexity distribution and top complex programs

**Example Usage:**
```python
from legacy_analyzer.visualization import ReportGenerator, AnalysisResults

generator = ReportGenerator()

# Generate executive summary
summary = generator.generate_executive_summary(analysis_results)

# Generate artifact report
artifact_report = generator.generate_artifact_report(
    'PROGRAM1',
    complexity_metrics=metrics,
    callers=['PROG2', 'PROG3'],
    callees=['PROG4']
)

# Generate package report
package_report = generator.generate_package_report(migration_package)
```

### 3. Report Exporters (`html_exporter.py`)

Export reports in various formats:

#### HTMLExporter
Exports reports as HTML using Jinja2 templates:
- Executive summary
- Artifact detail pages
- Interactive flow diagrams

**Requirements:** `jinja2`

#### MarkdownExporter
Exports reports as Markdown:
- Executive summary
- Artifact details
- Package reports

#### JSONExporter
Exports analysis results as JSON:
- Complete analysis results
- Program flows
- Structured data for programmatic use

#### PDFExporter
Exports reports as PDF:
- Converts HTML reports to PDF
- Executive summaries
- Artifact details

**Requirements:** `weasyprint`, `jinja2`

**Example Usage:**
```python
from legacy_analyzer.visualization import HTMLExporter, JSONExporter

# HTML Export
html_exporter = HTMLExporter()
html_exporter.export_executive_summary(analysis_results, 'report.html')
html_exporter.export_artifact_detail('PROG1', 'prog1.html', complexity_metrics=metrics)

# JSON Export
json_exporter = JSONExporter()
json_exporter.export_analysis_results(analysis_results, 'results.json')
json_exporter.export_flow(program_flow, 'flow.json')
```

## HTML Templates

The module includes three Jinja2 templates in the `templates/` directory:

### executive_summary.html
- Inventory overview with metric cards
- Complexity distribution bar charts
- Missing artifacts summary
- Key findings section
- Responsive design with modern styling

### artifact_detail.html
- Complexity metrics display
- Dependencies (callers and callees)
- Copybooks and datasets lists
- Program flow statistics
- Package assignment information
- Color-coded complexity badges

### flow_diagram.html
- Interactive network visualization using vis.js
- Hierarchical and force-directed layouts
- Zoom and pan controls
- Node click events
- Export capabilities
- Flow statistics display
- Color-coded legend

## Color Scheme

The visualization components use a consistent color scheme:

- **Low Complexity**: Light Green (#90EE90)
- **Medium Complexity**: Gold (#FFD700)
- **High Complexity**: Orange (#FFA500)
- **Very High Complexity**: Tomato Red (#FF6347)
- **Missing Artifacts**: Red (#FF0000)
- **Default**: Sky Blue (#87CEEB)

## Requirements Validation

This implementation satisfies the following requirements from the design document:

### Requirement 9.1: DOT Format
✅ `GraphRenderer.render_dot()` generates DOT format for Graphviz

### Requirement 9.2: Mermaid Format
✅ `GraphRenderer.render_mermaid()` generates Mermaid diagrams

### Requirement 9.3: HTML Reports
✅ `GraphRenderer.render_html()` generates interactive HTML
✅ `HTMLExporter` uses Jinja2 templates for HTML reports

### Requirement 9.4: Executive Summary
✅ `ReportGenerator.generate_executive_summary()` creates executive summaries

### Requirement 9.5: Artifact Reports
✅ `ReportGenerator.generate_artifact_report()` creates detailed artifact reports

### Requirement 9.6: Multiple Export Formats
✅ HTML, PDF, Markdown, and JSON exporters implemented

### Requirement 9.7: Color Coding
✅ Color coding by complexity level implemented in all renderers

### Requirement 9.8: Highlight Missing
✅ Missing artifacts highlighted in red with special borders

## Testing

Comprehensive unit tests are provided in `tests/test_visualization.py`:

- GraphRenderer tests (DOT, Mermaid, HTML rendering)
- ReportGenerator tests (all report types)
- Export functionality tests (JSON, Markdown)

Run tests with:
```bash
python -m pytest tests/test_visualization.py -v
```

## Dependencies

### Required
- Python 3.7+

### Optional
- `jinja2`: For HTML template rendering (HTMLExporter, PDFExporter)
- `weasyprint`: For PDF export (PDFExporter)

Install optional dependencies:
```bash
pip install jinja2 weasyprint
```

## Future Enhancements

Potential improvements for future versions:

1. **Additional Export Formats**: Excel, CSV for tabular data
2. **Custom Templates**: Allow users to provide custom Jinja2 templates
3. **Theme Support**: Multiple color schemes and themes
4. **Interactive Filtering**: Client-side filtering in HTML reports
5. **Chart Libraries**: Integration with Chart.js or D3.js for advanced visualizations
6. **Comparison Reports**: Compare analysis results across time periods
7. **Email Integration**: Send reports via email
8. **Dashboard**: Real-time dashboard with live updates
