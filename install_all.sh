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
SKIP_AGENTS=""
ACM_TOOLS_ZIP=""

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
        --skip-agents)
            SKIP_AGENTS="true"
            shift
            ;;
        --acm-tools-zip)
            ACM_TOOLS_ZIP="$2"
            shift 2
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
            echo "  --skip-agents          Skip agent installation (use if agents already installed)"
            echo "  --acm-tools-zip PATH   Path to local ACM tools ZIP file (optional)"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./install_all.sh my_migration_project"
            echo "  ./install_all.sh my_project --provider q_cli"
            echo "  ./install_all.sh my_project --skip-agents"
            echo "  ./install_all.sh my_project --acm-tools-zip ./acm-tools-main.zip"
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
if [ -n "$SKIP_AGENTS" ]; then
    echo "  • Agent Installation: Skipped"
else
    echo "  • Agent Installation: Enabled"
fi
if [ -n "$ACM_TOOLS_ZIP" ]; then
    echo "  • ACM Tools ZIP: $ACM_TOOLS_ZIP"
else
    echo "  • ACM Tools ZIP: Will download from repository"
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
echo -e "${BLUE}║  Step 1/4: Installing CAO                                  ║${NC}"
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
echo -e "${BLUE}║  Step 2/4: Creating Project                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Creating project: $PROJECT_NAME"
echo ""

# Create project with automatic "no" response to agent installation prompt
# We'll install agents in a later step with the specified provider
echo "n" | python3 create_project.py "$PROJECT_NAME"

if [ ! -d "$PROJECT_NAME" ]; then
    echo -e "${RED}✗ Project creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project created successfully${NC}"
echo ""

# Step 3: Install Agents (Optional)
if [ -n "$SKIP_AGENTS" ]; then
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Step 3/4: Skipping Agent Installation                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Agent installation skipped (--skip-agents flag used)${NC}"
    echo ""
    echo "To install agents later, run:"
    echo "  cd $PROJECT_NAME"
    echo "  python3 acm/install_agents.py --provider $PROVIDER"
    echo ""
else
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Step 3/4: Installing Agents                               ║${NC}"
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
fi

# Step 4: Install ACM Tools (Optional)
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 4/4: Installing ACM Tools (Optional)                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "ACM tools provide validation and analysis utilities for your migration project."
echo ""

# Check if custom ZIP file was provided
if [ -n "$ACM_TOOLS_ZIP" ]; then
    echo "Custom ACM tools ZIP file specified: $ACM_TOOLS_ZIP"
    echo ""
fi

# Ask user if they want to install ACM tools
read -p "Do you want to install ACM tools? (y/N): " -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing ACM tools..."
    echo ""
    
    # Check if custom ZIP file was provided
    if [ -n "$ACM_TOOLS_ZIP" ]; then
        # Verify the ZIP file exists
        if [ ! -f "$ACM_TOOLS_ZIP" ]; then
            echo -e "${RED}✗ ACM tools ZIP file not found: $ACM_TOOLS_ZIP${NC}"
            echo "Skipping ACM tools installation"
        else
            echo "Using custom ZIP file: $ACM_TOOLS_ZIP"
            python3 install_acm_tools.py --tools-dir "$PROJECT_NAME/tools" --zip-file "$ACM_TOOLS_ZIP"
            
            if [ $? -eq 0 ] && [ -d "$PROJECT_NAME/tools/acm-tools" ]; then
                echo ""
                echo -e "${GREEN}✓ ACM tools installed successfully from custom ZIP${NC}"
            else
                echo ""
                echo -e "${YELLOW}⚠️  ACM tools installation from custom ZIP had issues${NC}"
                echo "You can retry manually:"
                echo "  cd $PROJECT_NAME"
                echo "  python3 ../install_acm_tools.py --tools-dir ./tools --zip-file $ACM_TOOLS_ZIP"
            fi
        fi
    else
        # Install from default URL
        echo "Attempting to download ACM tools from repository..."
        echo ""
        python3 install_acm_tools.py --tools-dir "$PROJECT_NAME/tools" --skip-on-error
        
        echo ""
        # Verify installation by checking if directory actually exists
        if [ -d "$PROJECT_NAME/tools/acm-tools" ] && [ "$(ls -A $PROJECT_NAME/tools/acm-tools 2>/dev/null)" ]; then
            echo -e "${GREEN}✓ ACM tools installed successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  ACM tools not installed${NC}"
            echo ""
            echo "This is expected if:"
            echo "  • The repository is private or requires authentication"
            echo "  • You have SSL certificate issues"
            echo "  • You don't have network access to the repository"
            echo ""
            echo "To install ACM tools later:"
            echo "  1. Download acm-tools-main.zip manually from the repository"
            echo "  2. Run: cd $PROJECT_NAME"
            echo "  3. Run: python3 ../install_acm_tools.py --tools-dir ./tools --zip-file /path/to/acm-tools-main.zip"
            echo ""
            echo "  Or specify the ZIP file location:"
            echo "  python3 ../install_acm_tools.py --tools-dir ./tools --zip-file /path/to/acm-tools-main.zip"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  ACM tools installation skipped${NC}"
    echo ""
    echo "To install ACM tools later:"
    echo "  1. Download acm-tools-main.zip and place it in the installation directory"
    echo "  2. Run: cd $PROJECT_NAME"
    echo "  3. Run: python3 ../install_acm_tools.py --tools-dir ./tools"
fi

echo ""

# Final Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation Complete!                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Summary:"
echo "  ✓ CAO installed and verified"
echo "  ✓ Project '$PROJECT_NAME' created"
if [ -n "$SKIP_AGENTS" ]; then
    echo "  ⊘ Agents installation skipped"
else
    echo "  ✓ Agents installed with provider: $PROVIDER"
fi
if [ -d "$PROJECT_NAME/tools/acm-tools" ] && [ "$(ls -A $PROJECT_NAME/tools/acm-tools 2>/dev/null)" ]; then
    echo "  ✓ ACM tools installed"
else
    echo "  ⊘ ACM tools not installed"
fi
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
