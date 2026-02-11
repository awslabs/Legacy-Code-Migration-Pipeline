#!/bin/bash
#
# Uninstall Script for Legacy Code Migration Framework
#
# This script uninstalls CAO (CLI Agent Orchestrator) and removes all agents.
# It provides options for complete cleanup or selective removal.
#
# Usage: ./uninstall_all.sh [OPTIONS]
#
# Options:
#   --keep-config    Keep CAO configuration files
#   --keep-cache     Keep agent cache
#   --help           Show this help message
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
KEEP_CONFIG=false
KEEP_CACHE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-config)
            KEEP_CONFIG=true
            shift
            ;;
        --keep-cache)
            KEEP_CACHE=true
            shift
            ;;
        --help)
            echo "Usage: ./uninstall_all.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --keep-config    Keep CAO configuration files"
            echo "  --keep-cache     Keep agent cache"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Legacy Code Migration Framework - Uninstall Script       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Warning message
echo -e "${YELLOW}⚠️  WARNING: This will uninstall CAO and remove all agents${NC}"
echo ""
echo "The following will be removed:"
echo "  • CLI Agent Orchestrator (CAO)"
echo "  • All installed agents (CAO and Kiro)"
echo "  • Kiro agents directory (~/.kiro/agents)"

if [ "$KEEP_CONFIG" = false ]; then
    echo "  • CAO configuration files"
fi

if [ "$KEEP_CACHE" = false ]; then
    echo "  • Agent cache and store"
fi

echo ""
echo -e "${YELLOW}Project files and directories will NOT be removed.${NC}"
echo ""

# Ask for confirmation
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${BLUE}Uninstallation cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting uninstallation...${NC}"
echo ""

# Step 1: Check if CAO is installed
echo -e "${BLUE}[1/4] Checking CAO installation...${NC}"
if command -v cao &> /dev/null; then
    echo -e "${GREEN}✓ CAO is installed${NC}"
    CAO_INSTALLED=true
else
    echo -e "${YELLOW}⚠️  CAO is not installed or not in PATH${NC}"
    CAO_INSTALLED=false
fi
echo ""

# Step 2: List installed agents (check both CAO and Kiro)
if [ "$CAO_INSTALLED" = true ]; then
    echo -e "${BLUE}[2/4] Listing installed agents...${NC}"
    if cao list &> /dev/null; then
        echo "Currently installed agents (CAO):"
        cao list | head -20
        AGENT_COUNT=$(cao list 2>/dev/null | wc -l)
        echo -e "${YELLOW}Total CAO agents: $AGENT_COUNT${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not list CAO agents${NC}"
    fi
else
    echo -e "${BLUE}[2/4] Checking for installed agents...${NC}"
fi

# Check for Kiro agents
if [ -d "$HOME/.kiro/agents" ]; then
    KIRO_AGENT_COUNT=$(find "$HOME/.kiro/agents" -name "*.md" -type f 2>/dev/null | wc -l)
    if [ "$KIRO_AGENT_COUNT" -gt 0 ]; then
        echo ""
        echo "Found Kiro agents in: $HOME/.kiro/agents"
        echo -e "${YELLOW}Total Kiro agents: $KIRO_AGENT_COUNT${NC}"
        echo ""
        echo "Agent files:"
        find "$HOME/.kiro/agents" -name "*.md" -type f 2>/dev/null | head -10
        if [ "$KIRO_AGENT_COUNT" -gt 10 ]; then
            echo "... and $((KIRO_AGENT_COUNT - 10)) more"
        fi
    fi
fi
echo ""

# Step 3: Uninstall CAO
echo -e "${BLUE}[3/4] Uninstalling CAO...${NC}"
if command -v uv &> /dev/null; then
    if uv tool uninstall cli-agent-orchestrator 2>/dev/null; then
        echo -e "${GREEN}✓ CAO uninstalled successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  CAO may not have been installed via uv tool${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  uv not found, skipping CAO uninstallation${NC}"
    echo "   If CAO was installed differently, please uninstall manually"
fi
echo ""

# Step 4: Clean up configuration and cache
echo -e "${BLUE}[4/4] Cleaning up files...${NC}"

# Remove Kiro agents
if [ -d "$HOME/.kiro/agents" ]; then
    echo "Removing Kiro agents: $HOME/.kiro/agents"
    rm -rf "$HOME/.kiro/agents"
    echo -e "${GREEN}✓ Kiro agents removed${NC}"
else
    echo -e "${YELLOW}⚠️  Kiro agents directory not found${NC}"
fi

# Remove agent store
if [ "$KEEP_CACHE" = false ]; then
    if [ -d "$HOME/.aws/cli-agent-orchestrator" ]; then
        echo "Removing CAO agent store: $HOME/.aws/cli-agent-orchestrator"
        rm -rf "$HOME/.aws/cli-agent-orchestrator"
        echo -e "${GREEN}✓ CAO agent store removed${NC}"
    else
        echo -e "${YELLOW}⚠️  CAO agent store not found${NC}"
    fi
else
    echo -e "${BLUE}ℹ️  Keeping agent cache (--keep-cache specified)${NC}"
fi

# Remove CAO configuration (if exists in project directories)
if [ "$KEEP_CONFIG" = false ]; then
    # Note: This only removes .cao directories in current location
    # Project-specific .cao directories are preserved
    echo -e "${BLUE}ℹ️  Project-specific .cao directories are preserved${NC}"
    echo "   To remove them, delete manually from each project"
else
    echo -e "${BLUE}ℹ️  Keeping configuration files (--keep-config specified)${NC}"
fi

echo ""

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Uninstallation Complete                                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Summary:"
echo "  • CAO has been uninstalled"
echo "  • CAO agents have been removed"
echo "  • Kiro agents have been removed (~/.kiro/agents)"

if [ "$KEEP_CONFIG" = false ]; then
    echo "  • Configuration files have been cleaned up"
else
    echo "  • Configuration files have been preserved"
fi

if [ "$KEEP_CACHE" = false ]; then
    echo "  • Agent cache has been removed"
else
    echo "  • Agent cache has been preserved"
fi

echo ""
echo "What was NOT removed:"
echo "  • Python (python3)"
echo "  • uv (Python package manager)"
echo "  • tmux (terminal multiplexer)"
echo "  • Git"
echo "  • Project directories and files"
echo "  • Project-specific .cao directories"
echo ""

echo "To remove these manually:"
echo "  • uv: Follow instructions at https://docs.astral.sh/uv/"
echo "  • tmux: Use your system package manager (brew, apt, etc.)"
echo "  • Projects: Delete project directories manually"
echo ""

echo -e "${BLUE}If you want to reinstall, run: ./install_all.sh${NC}"
echo ""
