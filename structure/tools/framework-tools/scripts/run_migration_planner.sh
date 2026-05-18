#!/bin/bash
#
# Migration Workpackage Planner Runner
#
# This script runs the migration workpackage planner with configurable input and output paths.
#
# Usage:
#   ./scripts/run_migration_planner.sh <flows_file> <output_dir> [classifications_file] [project_name] [log_level]
#
# Arguments:
#   flows_file           - Path to Business_Flows.json (required)
#   output_dir           - Output directory for planning files (required)
#   classifications_file - Path to Module_Classifications.json (optional)
#   project_name         - Project name for metadata (optional, extracted from path if not provided)
#   log_level            - Logging level: DEBUG, INFO, WARNING, ERROR (optional, default: INFO)
#
# Examples:
#   # Basic usage
#   ./scripts/run_migration_planner.sh ./results/carddemo_analysis/flows/Business_Flows.json ./results/carddemo_analysis/migration
#
#   # With classifications
#   ./scripts/run_migration_planner.sh ./data/flows.json ./output ./data/classifications.json
#
#   # With all options
#   ./scripts/run_migration_planner.sh ./data/flows.json ./output ./data/classifications.json my-project DEBUG
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 <flows_file> <output_dir> [classifications_file] [project_name] [log_level]

Arguments:
  flows_file           Path to Business_Flows.json (required)
  output_dir           Output directory for planning files (required)
  classifications_file Path to Module_Classifications.json (optional)
  project_name         Project name for metadata (optional)
  log_level            Logging level: DEBUG, INFO, WARNING, ERROR (optional, default: INFO)

Examples:
  # Basic usage
  $0 ./results/carddemo_analysis/flows/Business_Flows.json ./results/carddemo_analysis/migration

  # With classifications
  $0 ./data/flows.json ./output ./data/classifications.json

  # With all options
  $0 ./data/flows.json ./output ./data/classifications.json my-project DEBUG

Output Files:
  - Workpackage_Planning.json          Complete planning data
  - Workpackage_Status.json            Initial status tracking
  - Workpackage_Definition_Roadmap.md  Human-readable roadmap

Exit Codes:
  0 - Success
  1 - Input validation error
  2 - File system error
  3 - Dependency validation error
  4 - Configuration error

EOF
    exit 1
}

# Check for minimum required arguments
if [ $# -lt 2 ]; then
    print_error "Missing required arguments"
    echo ""
    usage
fi

# Parse arguments
FLOWS_FILE="$1"
OUTPUT_DIR="$2"
CLASSIFICATIONS_FILE="${3:-}"
PROJECT_NAME="${4:-}"
LOG_LEVEL="${5:-INFO}"

# Validate flows file exists
if [ ! -f "$FLOWS_FILE" ]; then
    print_error "Flows file not found: $FLOWS_FILE"
    exit 2
fi

# Validate log level
case "$LOG_LEVEL" in
    DEBUG|INFO|WARNING|ERROR)
        ;;
    *)
        print_warning "Invalid log level '$LOG_LEVEL', using INFO"
        LOG_LEVEL="INFO"
        ;;
esac

# Print configuration
print_info "Migration Workpackage Planner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Configuration:"
echo "  Flows File:          $FLOWS_FILE"
echo "  Output Directory:    $OUTPUT_DIR"
if [ -n "$CLASSIFICATIONS_FILE" ]; then
    echo "  Classifications:     $CLASSIFICATIONS_FILE"
else
    echo "  Classifications:     (none)"
fi
if [ -n "$PROJECT_NAME" ]; then
    echo "  Project Name:        $PROJECT_NAME"
else
    echo "  Project Name:        (auto-detected)"
fi
echo "  Log Level:           $LOG_LEVEL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Build command
CMD="python3 -m tools.migration_planner --flows-file \"$FLOWS_FILE\" --output-base \"$OUTPUT_DIR\" --log-level $LOG_LEVEL"

# Add optional arguments
if [ -n "$CLASSIFICATIONS_FILE" ]; then
    if [ ! -f "$CLASSIFICATIONS_FILE" ]; then
        print_warning "Classifications file not found: $CLASSIFICATIONS_FILE"
        print_warning "Continuing without classifications..."
    else
        CMD="$CMD --classifications-file \"$CLASSIFICATIONS_FILE\""
    fi
fi

if [ -n "$PROJECT_NAME" ]; then
    CMD="$CMD --project-name \"$PROJECT_NAME\""
fi

# Run the planner
print_info "Running migration planner..."
echo ""

if eval $CMD; then
    EXIT_CODE=$?
    echo ""
    print_success "Planning completed successfully!"
    echo ""
    
    # Display output files
    print_info "Generated files in $OUTPUT_DIR:"
    if [ -f "$OUTPUT_DIR/Workpackage_Planning.json" ]; then
        SIZE=$(ls -lh "$OUTPUT_DIR/Workpackage_Planning.json" | awk '{print $5}')
        echo "  ✓ Workpackage_Planning.json ($SIZE)"
    fi
    if [ -f "$OUTPUT_DIR/progress/Workpackage_Status.json" ]; then
        SIZE=$(ls -lh "$OUTPUT_DIR/progress/Workpackage_Status.json" | awk '{print $5}')
        echo "  ✓ progress/Workpackage_Status.json ($SIZE)"
    fi
    if [ -f "$OUTPUT_DIR/reports/Workpackage_Definition_Roadmap.md" ]; then
        SIZE=$(ls -lh "$OUTPUT_DIR/reports/Workpackage_Definition_Roadmap.md" | awk '{print $5}')
        echo "  ✓ reports/Workpackage_Definition_Roadmap.md ($SIZE)"
    fi
    echo ""
    
    # Display quick statistics from the planning file
    if [ -f "$OUTPUT_DIR/Workpackage_Planning.json" ] && command -v python3 &> /dev/null; then
        print_info "Planning Summary:"
        python3 << EOF
import json
try:
    with open("$OUTPUT_DIR/Workpackage_Planning.json") as f:
        data = json.load(f)
    stats = data.get("statistics", {})
    print(f"  Total Flows:         {stats.get('totalFlows', 'N/A')}")
    print(f"  Total Phases:        {stats.get('totalPhases', 'N/A')}")
    print(f"  Average Priority:    {stats.get('averagePriorityScore', 'N/A'):.2f}" if isinstance(stats.get('averagePriorityScore'), (int, float)) else f"  Average Priority:    N/A")
    
    flows_per_phase = stats.get('flowsPerPhase', {})
    if flows_per_phase:
        print("  Flows per Phase:")
        for phase, count in sorted(flows_per_phase.items(), key=lambda x: int(x[0])):
            print(f"    Phase {phase}: {count} workpackages")
except Exception as e:
    print(f"  (Could not parse statistics: {e})")
EOF
        echo ""
    fi
    
    print_info "Next steps:"
    echo "  1. Review Workpackage_Definition_Roadmap.md for migration overview"
    echo "  2. Examine Workpackage_Planning.json for detailed planning data"
    echo "  3. Use Workpackage_Status.json to track migration progress"
    echo ""
    
    exit 0
else
    EXIT_CODE=$?
    echo ""
    print_error "Planning failed with exit code $EXIT_CODE"
    echo ""
    
    case $EXIT_CODE in
        1)
            print_error "Input validation error"
            echo "  Check that Business_Flows.json has all required fields"
            ;;
        2)
            print_error "File system error"
            echo "  Check file paths and permissions"
            ;;
        3)
            print_error "Dependency validation error"
            echo "  Check for circular dependencies in Business_Flows.json"
            ;;
        4)
            print_error "Configuration error"
            echo "  Check command-line arguments"
            ;;
        *)
            print_error "Unexpected error"
            echo "  Run with --log-level DEBUG for more details"
            ;;
    esac
    echo ""
    
    exit $EXIT_CODE
fi
