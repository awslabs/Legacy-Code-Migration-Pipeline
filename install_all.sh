#!/bin/bash
#
# Complete Installation Script for Legacy Code Migration Framework
#
# This script performs a complete installation:
# 1. Installs CAO (CLI Agent Orchestrator)
# 2. Creates a new migration project
# 3. Installs all agents into the project
#
# Usage: ./install_all.sh <project_name> [OPTIONS]
#
# Options:
#   --provider PROVIDER    CLI provider (kiro_cli, q_cli, claude_code; default: kiro_cli)
#   --skip-validation      Skip prerequisite validation
#   --help                 Show this help message
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
PROVIDER="kiro_cli"
SKIP_VALIDATION=""
PROJECT_NAME=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        --skip-validation)
            SKIP_VALIDATION="--skip-validation"
            shift
            ;;
        --help)
            echo "Usage: ./install_all.sh <project_name> [OPTIONS]"
            echo ""
            echo "Arguments:"
            echo "  project_name           Name of the migration project to create"
            echo ""
            echo "Options:"
            echo "  --provider PROVIDER    CLI provider (kiro_cli, q_cli, claude_code; default: kiro_cli)"
            echo "  --skip-validation      Skip prerequisite validation (not recommended)"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./install_all.sh my_migration_project"
            echo "  ./install_all.sh my_project --provider q_cli"
            echo "  ./install_all.sh my_project --provider kiro_cli --skip-validation"
            exit 0
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [ -z "$PROJECT_NAME" ]; then
                PROJECT_NAME="$1"
            else
                echo -e "${RED}Error: Multiple project names specified${NC}"
                echo "Use --help for usage information"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate project name
if [ -z "$PROJECT_NAME" ]; then
    echo -e "${RED}Error: Project name is required${NC}"
    echo "Usage: ./install_all.sh <project_name> [OPTIONS]"
    echo "Use --help for more information"
    exit 1
fi

# Validate provider
case $PROVIDER in
    kiro_cli|q_cli|claude_code)
        ;;
    *)
        echo -e "${RED}Error: Invalid provider '$PROVIDER'${NC}"
        echo "Valid providers: kiro_cli, q_cli, claude_code"
        exit 1
        ;;
esac

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Legacy Code Migration Framework - Complete Installation  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Installation Configuration:"
echo "  • Project Name: $PROJECT_NAME"
echo "  • Provider: $PROVIDER"
if [ -n "$SKIP_VALIDATION" ]; then
    echo "  • Validation: Skipped"
else
    echo "  • Validation: Enabled"
fi
echo ""

# Check if project already exists
if [ -d "$PROJECT_NAME" ]; then
    echo -e "${YELLOW}⚠️  Warning: Directory '$PROJECT_NAME' already exists${NC}"
    read -p "Do you want to continue? This may overwrite existing files. (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${BLUE}Installation cancelled.${NC}"
        exit 0
    fi
fi

echo -e "${BLUE}Starting installation...${NC}"
echo ""

# Step 1: Install CAO
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 1/3: Installing CAO                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if command -v cao &> /dev/null; then
    echo -e "${YELLOW}⚠️  CAO is already installed${NC}"
    read -p "Do you want to upgrade to the latest version? (y/N): " -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Upgrading CAO..."
        python3 install_cao.py $SKIP_VALIDATION
    else
        echo "Skipping CAO installation"
    fi
else
    echo "Installing CAO and dependencies..."
    python3 install_cao.py $SKIP_VALIDATION
fi

# Verify CAO installation
if ! command -v cao &> /dev/null; then
    echo -e "${RED}✗ CAO installation failed or not in PATH${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Restart your shell: source ~/.bashrc (or ~/.zshrc)"
    echo "  2. Add to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "  3. Check installation: which cao"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ CAO installation complete${NC}"
echo ""

# Step 2: Create Project
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 2/3: Creating Project                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Creating project: $PROJECT_NAME"
echo ""

# Create project with automatic "no" response to agent installation prompt
# We'll install agents in the next step with the specified provider
echo "n" | python3 create_project.py "$PROJECT_NAME"

if [ ! -d "$PROJECT_NAME" ]; then
    echo -e "${RED}✗ Project creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project created successfully${NC}"
echo ""

# Step 3: Install Agents
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 3/3: Installing Agents                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Installing agents with provider: $PROVIDER"
echo ""

# Change to project directory and install agents
cd "$PROJECT_NAME"

if [ ! -f "acm/install_agents.py" ]; then
    echo -e "${RED}✗ Agent installation script not found${NC}"
    echo "Expected: $PROJECT_NAME/acm/install_agents.py"
    exit 1
fi

# Install agents with automatic "yes" response
echo "Y" | python3 acm/install_agents.py --provider "$PROVIDER"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Agent installation completed with some issues${NC}"
    echo "You can retry later by running:"
    echo "  cd $PROJECT_NAME"
    echo "  python3 acm/install_agents.py --provider $PROVIDER"
else
    echo -e "${GREEN}✓ Agents installed successfully${NC}"
fi

# Return to original directory
cd ..

echo ""

# Final Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation Complete!                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Summary:"
echo "  ✓ CAO installed and verified"
echo "  ✓ Project '$PROJECT_NAME' created"
echo "  ✓ Agents installed with provider: $PROVIDER"
echo ""

echo "Project Location:"
echo "  📁 $(pwd)/$PROJECT_NAME"
echo ""

echo "Next Steps:"
echo ""
echo "1. Navigate to your project:"
echo "   cd $PROJECT_NAME"
echo ""
echo "2. Add your legacy code:"
echo "   cp -r /path/to/legacy/code input/legacy/"
echo ""
echo "3. Verify agent installation:"
echo "   cao list"
echo ""

# Provider-specific instructions
case $PROVIDER in
    kiro_cli)
        echo "4. Launch agents with Kiro CLI:"
        echo "   kiro-cli chat --agent migration_supervisor"
        echo ""
        echo "   Or use CAO directly:"
        echo "   cao launch --agents migration_supervisor"
        ;;
    q_cli)
        echo "4. Launch agents with Amazon Q CLI:"
        echo "   cao launch --agents migration_supervisor"
        ;;
    claude_code)
        echo "4. Launch agents with Claude Code:"
        echo "   cao launch --agents migration_supervisor"
        ;;
esac

echo ""
echo "Useful Commands:"
echo "  • List agents:        cao list"
echo "  • Update agents:      python3 acm/install_agents.py"
echo "  • Validate outputs:   ./validate_deliverables.sh"
echo "  • Get help:           cao --help"
echo ""

echo "Documentation:"
echo "  • Quick Start:        ../QUICK_START.md"
echo "  • Installation Guide: ../INSTALLATION_GUIDE.md"
echo "  • User Guide:         ../docs/USER_GUIDE.md"
echo "  • ACM Tools:          ../structure/doc/acm/acm.md"
echo ""

echo -e "${BLUE}Happy migrating! 🚀${NC}"
echo ""
