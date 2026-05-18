#!/bin/bash
set -e  # Exit on error

# Configurable Analysis Script
# This script performs a comprehensive analysis with configurable parameters.
# Based on run_carddemo_analysis.sh but accepts mandatory input/output parameters.
#
# IMPORTANT: This script uses POSITIONAL ARGUMENTS (not flags like --source-dir)
#
# Usage:
#   ./run_configurable_analysis.sh <source_dir> <output_dir> [database_path]
#
# Example:
#   ./run_configurable_analysis.sh \
#     ./examples/code/cobol/carddemoV2/app \
#     ./results/my_analysis \
#     ./results/my_analysis/my_project.db
#
# Note: This script must be run from the repository root directory where
#       the tools/ directory is located, or you must cd to that directory first.

# Detect script directory and repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if we're in the correct directory (tools/ should exist)
if [ ! -d "$REPO_ROOT/tools" ]; then
    echo "Error: Cannot find tools/ directory"
    echo ""
    echo "This script must be run from the repository root, or the repository"
    echo "structure is not as expected."
    echo ""
    echo "Expected structure:"
    echo "  repository_root/"
    echo "    ├── tools/"
    echo "    ├── scripts/"
    echo "    └── ..."
    echo ""
    echo "Current directory: $(pwd)"
    echo "Repository root detected as: $REPO_ROOT"
    echo ""
    exit 1
fi

# Change to repository root to ensure Python module imports work
cd "$REPO_ROOT"

# Check for required arguments
if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments"
    echo ""
    echo "Usage: $0 <source_dir> <output_dir> [database_path]"
    echo ""
    echo "IMPORTANT: Use positional arguments, NOT flags like --source-dir"
    echo ""
    echo "Arguments:"
    echo "  source_dir     - Directory containing source code to analyze"
    echo "  output_dir     - Directory for output files (will be created)"
    echo "  database_path  - Path to SQLite database file (optional, default: <output_dir>/analysis.db)"
    echo ""
    echo "Example:"
    echo "  $0 \\"
    echo "    ./examples/code/cobol/carddemoV2/app \\"
    echo "    ./results/my_analysis"
    echo ""
    echo "  Or with custom database path:"
    echo "  $0 \\"
    echo "    ./examples/code/cobol/carddemoV2/app \\"
    echo "    ./results/my_analysis \\"
    echo "    ./results/my_analysis/my_project.db"
    echo ""
    echo "INCORRECT (will not work):"
    echo "  $0 --source-dir ./source --output-dir ./output"
    echo ""
    exit 1
fi

# Parse arguments
SOURCE_DIR="$1"
OUTPUT_DIR="$2"
DATABASE="${3:-$OUTPUT_DIR/analysis.db}"

echo "================================================================================"
echo "  Configurable Complete Analysis"
echo "================================================================================"
echo ""
echo "Configuration:"
echo "  Source:   $SOURCE_DIR"
echo "  Output:   $OUTPUT_DIR"
echo "  Database: $DATABASE"
echo "  Working:  $(pwd)"
echo ""

# Verify source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found: $SOURCE_DIR"
    echo ""
    echo "Please provide a valid source directory path."
    exit 1
fi

# Create directories
echo "Creating output directories..."
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/flows"
mkdir -p "$OUTPUT_DIR/reports"
echo "✓ Directories created"
echo ""

# Step 1: Complete Analysis (Inventory + Dependencies + Complexity)
echo "================================================================================"
echo "  Step 1: Complete Static Analysis"
echo "================================================================================"
echo ""
echo "Running complete analysis workflow..."
python3 -m tools.legacy_analyzer analyze \
  --source-dir "$SOURCE_DIR" \
  --db "$DATABASE" \
  --complexity

echo ""
echo "✓ Static analysis complete"
echo ""

# Step 2: Check Analysis Status
echo "================================================================================"
echo "  Step 2: Analysis Status Check"
echo "================================================================================"
echo ""
python3 -m tools.legacy_analyzer status --db "$DATABASE"
echo ""

# Step 3: Detect Entry Points
echo "================================================================================"
echo "  Step 3: Entry Point Detection"
echo "================================================================================"
echo ""
echo "Detecting entry points (JSON format)..."
python3 -m tools.legacy_analyzer flow entry-points \
  --db "$DATABASE" \
  --use-metadata \
  --format json \
  --output "$OUTPUT_DIR/entry_points/entry_points.json"

echo ""
echo "Detecting entry points (Markdown format)..."
python3 -m tools.legacy_analyzer flow entry-points \
  --db "$DATABASE" \
  --use-metadata \
  --format markdown \
  --output "$OUTPUT_DIR/entry_points/entry_points.md"

echo ""
echo "✓ Entry point detection complete"
echo ""

# Step 4: Build Migration Flows
echo "================================================================================"
echo "  Step 4: Build Migration Flows"
echo "================================================================================"
echo ""
echo "Building migration flows from analysis data..."
python3 -m tools.legacy_analyzer migration build-flows \
  --db "$DATABASE" \
  --utility-threshold 5

echo ""
echo "✓ Migration flows built"
echo ""

# Step 5: Export Migration Flows (All Sorting Strategies)
echo "================================================================================"
echo "  Step 5: Export Migration Flows (All Sorting Strategies)"
echo "================================================================================"
echo ""

# Export with all sorting strategies for comprehensive migration planning
echo "Exporting flows with all sorting strategies..."
echo ""

# 1. Complexity Ascending - Simplest first (recommended for initial migration)
echo "  1/6 Exporting: complexity-asc (simplest first)..."
python3 -m tools.legacy_analyzer migration export-flows \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/flows/flows_by_complexity_asc.json" \
  --extended-scope \
  --sort complexity-asc

# 2. Complexity Descending - Most complex first (high value first)
echo "  2/6 Exporting: complexity-desc (most complex first)..."
python3 -m tools.legacy_analyzer migration export-flows \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/flows/flows_by_complexity_desc.json" \
  --extended-scope \
  --sort complexity-desc

# 3. Independence - Fewest shared programs first (parallel migration)
echo "  3/6 Exporting: independence (minimal dependencies)..."
python3 -m tools.legacy_analyzer migration export-flows \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/flows/flows_by_independence.json" \
  --extended-scope \
  --sort independence

# 4. Dependencies - Most dependencies first (foundational flows)
echo "  4/6 Exporting: dependencies (foundational first)..."
python3 -m tools.legacy_analyzer migration export-flows \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/flows/flows_by_dependencies.json" \
  --extended-scope \
  --sort dependencies

# 5. Name - Alphabetical (documentation/reference)
echo "  5/6 Exporting: name (alphabetical)..."
python3 -m tools.legacy_analyzer migration export-flows \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/flows/flows_by_name.json" \
  --extended-scope \
  --sort name

# 6. Database order - No sorting (default)
echo "  6/6 Exporting: database order (no sorting)..."
python3 -m tools.legacy_analyzer migration export-flows \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/flows/flows_database_order.json" \
  --extended-scope

# Create default Business_Flows.json as a copy of complexity-asc (recommended for migration planning)
echo "  7/7 Creating Business_Flows.json (copy of complexity-asc)..."
if [ -f "$OUTPUT_DIR/flows/flows_by_complexity_asc.json" ]; then
    cp "$OUTPUT_DIR/flows/flows_by_complexity_asc.json" "$OUTPUT_DIR/flows/Business_Flows.json"
else
    echo '{"flows": [], "metadata": {"total_flows": 0}}' > "$OUTPUT_DIR/flows/Business_Flows.json"
    echo "  Warning: No flows exported, created empty Business_Flows.json"
fi

echo ""
echo "✓ Migration flows exported with all sorting strategies"
echo ""

# Step 6: Export JCL Jobs (All Sorting Strategies)
echo "================================================================================"
echo "  Step 6: Export JCL Jobs (All Sorting Strategies)"
echo "================================================================================"
echo ""
echo "Exporting JCL jobs with all sorting strategies..."
echo ""
echo "The dual-export approach provides both program flows (business logic) and"
echo "job orchestration (infrastructure and scheduling) for comprehensive migration"
echo "planning. Jobs are categorized as APPLICATION (invoke custom programs) or"
echo "INFRASTRUCTURE (utilities only) to support phased migration."
echo ""

# Create jobs directory
mkdir -p "$OUTPUT_DIR/jobs"

# Export with all sorting strategies
# 1. Name - Alphabetical (documentation/reference)
echo "  1/4 Exporting: name (alphabetical)..."
python3 -m tools.legacy_analyzer migration export-jobs \
  --db "$DATABASE" \
  --output-dir "$OUTPUT_DIR/jobs" \
  --sort-by name

# 2. Type - APPLICATION first, then INFRASTRUCTURE (phased migration)
echo "  2/4 Exporting: type (application first)..."
python3 -m tools.legacy_analyzer migration export-jobs \
  --db "$DATABASE" \
  --output-dir "$OUTPUT_DIR/jobs" \
  --sort-by type

# 3. Dependencies - Execution order (orchestration planning)
echo "  3/4 Exporting: dependencies (execution order)..."
python3 -m tools.legacy_analyzer migration export-jobs \
  --db "$DATABASE" \
  --output-dir "$OUTPUT_DIR/jobs" \
  --sort-by dependencies

# 4. Complexity - Most complex first (by step count)
echo "  4/4 Exporting: complexity (most complex first)..."
python3 -m tools.legacy_analyzer migration export-jobs \
  --db "$DATABASE" \
  --output-dir "$OUTPUT_DIR/jobs" \
  --sort-by complexity

# Create default jobs.json as a copy of jobs_by_type (recommended for phased migration)
cp "$OUTPUT_DIR/jobs/jobs_by_type.json" "$OUTPUT_DIR/jobs/jobs.json"

echo ""
echo "✓ JCL jobs exported with all sorting strategies"
echo ""

# Step 7: Generate Summary Report
echo "================================================================================"
echo "  Step 7: Generate Summary Report"
echo "================================================================================"
echo ""
python3 -m tools.legacy_analyzer report summary \
  --db "$DATABASE" \
  --output "$OUTPUT_DIR/reports/analysis_summary.md"

echo ""
echo "✓ Summary report generated"
echo ""

# Step 8: Generate Status Report
echo "================================================================================"
echo "  Step 8: Generate Status Report"
echo "================================================================================"
echo ""
python3 -m tools.legacy_analyzer report status \
  --db "$DATABASE" \
  --output-dir "$OUTPUT_DIR"

echo ""
echo "✓ Status report generated"
echo ""

# Step 9: Service Candidates Analysis
echo "================================================================================"
echo "  Step 9: Service Candidates Analysis"
echo "================================================================================"
echo ""
echo "Identifying service candidates..."
python3 -m tools.legacy_analyzer service candidates \
  --db "$DATABASE" \
  --format json \
  --output "$OUTPUT_DIR/reports/service_candidates.json"

echo ""
echo "Generating service candidates report (Markdown)..."
python3 -m tools.legacy_analyzer service candidates \
  --db "$DATABASE" \
  --format markdown \
  --output "$OUTPUT_DIR/reports/service_candidates.md"

echo ""
echo "✓ Service candidates analysis complete"
echo ""

# Summary
echo "================================================================================"
echo "  Analysis Complete!"
echo "================================================================================"
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Generated files:"
echo "  - Database:           $DATABASE"
echo "  - Entry points:       $OUTPUT_DIR/entry_points/entry_points.json"
echo "  - Entry points:       $OUTPUT_DIR/entry_points/entry_points.md"
echo "  - Summary report:     $OUTPUT_DIR/reports/analysis_summary.md"
echo "  - Service candidates: $OUTPUT_DIR/reports/service_candidates.json"
echo "  - Service candidates: $OUTPUT_DIR/reports/service_candidates.md"
echo "  - Status report:      $OUTPUT_DIR/progress/source_analysis_status.json"
echo ""
echo "Migration flows (all sorting strategies):"
echo "  - Complexity Asc:     $OUTPUT_DIR/flows/flows_by_complexity_asc.json"
echo "  - Complexity Desc:    $OUTPUT_DIR/flows/flows_by_complexity_desc.json"
echo "  - Independence:       $OUTPUT_DIR/flows/flows_by_independence.json"
echo "  - Dependencies:       $OUTPUT_DIR/flows/flows_by_dependencies.json"
echo "  - Alphabetical:       $OUTPUT_DIR/flows/flows_by_name.json"
echo "  - Database Order:     $OUTPUT_DIR/flows/flows_database_order.json"
echo "  - Default (copy):     $OUTPUT_DIR/flows/Business_Flows.json (from flows_by_complexity_asc.json)"
echo ""
echo "JCL jobs (all sorting strategies):"
echo "  - Alphabetical:       $OUTPUT_DIR/jobs/jobs_by_name.json"
echo "  - By Type:            $OUTPUT_DIR/jobs/jobs_by_type.json"
echo "  - By Dependencies:    $OUTPUT_DIR/jobs/jobs_by_dependencies.json"
echo "  - By Complexity:      $OUTPUT_DIR/jobs/jobs_by_complexity.json"
echo "  - Default (copy):     $OUTPUT_DIR/jobs/jobs.json (from jobs_by_type.json)"
echo ""
echo "View results:"
echo "  1. View summary report:"
echo "     cat $OUTPUT_DIR/reports/analysis_summary.md"
echo ""
echo "  2. View entry points (Markdown):"
echo "     cat $OUTPUT_DIR/entry_points/entry_points.md"
echo ""
echo "  3. View entry points (JSON):"
echo "     cat $OUTPUT_DIR/entry_points/entry_points.json | python3 -m json.tool | less"
echo ""
echo "  4. View business flows (recommended order - simplest first):"
echo "     cat $OUTPUT_DIR/flows/Business_Flows.json | python3 -m json.tool | less"
echo ""
echo "  5. View JCL jobs (recommended order - application first):"
echo "     cat $OUTPUT_DIR/jobs/jobs.json | python3 -m json.tool | less"
echo ""
echo "  6. View service candidates:"
echo "     cat $OUTPUT_DIR/reports/service_candidates.md"
echo ""
echo "  7. Query database:"
echo "     sqlite3 $DATABASE"
echo ""
echo "For more information, see: docs/COMPLETE_ANALYSIS_GUIDE.md"
echo ""
