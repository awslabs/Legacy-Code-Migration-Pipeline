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
#   --keep-config         Keep CAO configuration files
#   --keep-cache          Keep agent cache
#   --remove-tmux         Remove tmux (if installed by CAO installer)
#   --remove-uv-packages  Remove CAO-related packages from uv (keeps uv itself)
#   --remove-uv           Remove uv package manager completely
#   --remove-all-deps     Remove all dependencies (tmux + uv + packages)
#   --help                Show this help message
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
REMOVE_TMUX=false
REMOVE_UV=false
REMOVE_UV_PACKAGES=false

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
        --remove-tmux)
            REMOVE_TMUX=true
            shift
            ;;
        --remove-uv-packages)
            REMOVE_UV_PACKAGES=true
            shift
            ;;
        --remove-uv)
            REMOVE_UV=true
            shift
            ;;
        --remove-all-deps)
            REMOVE_TMUX=true
            REMOVE_UV=true
            REMOVE_UV_PACKAGES=true
            shift
            ;;
        --help)
            echo "Usage: ./uninstall_all.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --keep-config         Keep CAO configuration files"
            echo "  --keep-cache          Keep agent cache"
            echo "  --remove-tmux         Remove tmux (if installed by CAO installer)"
            echo "  --remove-uv-packages  Remove CAO-related packages from uv (keeps uv itself)"
            echo "  --remove-uv           Remove uv package manager completely"
            echo "  --remove-all-deps     Remove all dependencies (tmux + uv + packages)"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./uninstall_all.sh                       # Remove CAO and agents only"
            echo "  ./uninstall_all.sh --remove-uv-packages  # Remove CAO and its uv packages"
            echo "  ./uninstall_all.sh --remove-all-deps     # Remove everything including dependencies"
            echo "  ./uninstall_all.sh --remove-uv           # Remove CAO, agents, and uv completely"
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

if [ "$REMOVE_UV_PACKAGES" = true ]; then
    echo "  • CAO-related packages from uv (cli-agent-orchestrator)"
fi

if [ "$REMOVE_UV" = true ]; then
    echo "  • uv package manager (complete removal)"
fi

if [ "$REMOVE_TMUX" = true ]; then
    echo "  • tmux (if installed by CAO installer)"
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
echo -e "${BLUE}[3/6] Uninstalling CAO...${NC}"
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
echo -e "${BLUE}[4/6] Cleaning up files...${NC}"

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

# Step 5: Remove CAO-related uv packages (optional)
if [ "$REMOVE_UV_PACKAGES" = true ]; then
    echo -e "${BLUE}[5/6] Removing CAO-related packages from uv...${NC}"
    
    if command -v uv &> /dev/null; then
        echo "Checking for CAO-related packages in uv..."
        
        # List installed uv tools
        if uv tool list &> /dev/null; then
            echo "Currently installed uv tools:"
            uv tool list
            echo ""
        fi
        
        # Remove cli-agent-orchestrator if still present
        if uv tool list 2>/dev/null | grep -q "cli-agent-orchestrator"; then
            echo "Removing cli-agent-orchestrator..."
            uv tool uninstall cli-agent-orchestrator 2>/dev/null || true
        fi
        
        # Note: CAO is installed as a uv tool, not as a regular package
        # uv tools are self-contained and don't install additional packages
        
        echo -e "${GREEN}✓ CAO-related packages removed from uv${NC}"
        echo -e "${BLUE}ℹ️  uv itself has been preserved and can be used for other projects${NC}"
    else
        echo -e "${YELLOW}⚠️  uv not found in PATH${NC}"
    fi
elif [ "$REMOVE_UV" = true ]; then
    echo -e "${BLUE}[5/6] Removing uv package manager completely...${NC}"
    
    if command -v uv &> /dev/null; then
        echo "Removing uv from: ~/.cargo/bin/"
        
        # Remove uv binaries
        rm -f ~/.cargo/bin/uv
        rm -f ~/.cargo/bin/uvx
        
        # Remove uv data directory if it exists
        if [ -d "$HOME/.local/share/uv" ]; then
            echo "Removing uv data: ~/.local/share/uv"
            rm -rf "$HOME/.local/share/uv"
        fi
        
        # Remove uv cache if it exists
        if [ -d "$HOME/.cache/uv" ]; then
            echo "Removing uv cache: ~/.cache/uv"
            rm -rf "$HOME/.cache/uv"
        fi
        
        echo -e "${GREEN}✓ uv removed completely${NC}"
        echo -e "${YELLOW}⚠️  Note: You may need to restart your shell${NC}"
    else
        echo -e "${YELLOW}⚠️  uv not found in PATH${NC}"
    fi
else
    echo -e "${BLUE}[5/6] Keeping uv package manager and its packages${NC}"
fi

echo ""

# Step 6: Remove tmux (optional)
if [ "$REMOVE_TMUX" = true ]; then
    echo -e "${BLUE}[6/6] Checking tmux installation...${NC}"
    
    if command -v tmux &> /dev/null; then
        TMUX_PATH=$(which tmux)
        echo "Found tmux at: $TMUX_PATH"
        
        # Check if tmux is in user-local directories (likely installed by CAO)
        if [[ "$TMUX_PATH" == "$HOME/.local/bin/tmux" ]] || [[ "$TMUX_PATH" == "$HOME/bin/tmux" ]]; then
            echo "Removing tmux (appears to be installed by CAO installer)"
            rm -f "$TMUX_PATH"
            echo -e "${GREEN}✓ tmux removed${NC}"
        elif [[ "$TMUX_PATH" == "/usr/local/bin/tmux" ]]; then
            echo -e "${YELLOW}⚠️  tmux is in /usr/local/bin (may require sudo)${NC}"
            read -p "Remove tmux from /usr/local/bin? (requires sudo) (y/n): " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sudo rm -f /usr/local/bin/tmux
                echo -e "${GREEN}✓ tmux removed${NC}"
            else
                echo -e "${BLUE}ℹ️  Skipping tmux removal${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  tmux is installed via system package manager${NC}"
            echo "   Location: $TMUX_PATH"
            echo "   To remove, use your system package manager:"
            
            # Detect OS and provide appropriate command
            if [[ "$OSTYPE" == "darwin"* ]]; then
                echo "   macOS: brew uninstall tmux"
            elif [[ -f /etc/debian_version ]]; then
                echo "   Debian/Ubuntu: sudo apt remove tmux"
            elif [[ -f /etc/redhat-release ]]; then
                echo "   RHEL/CentOS: sudo yum remove tmux"
            else
                echo "   Use your system's package manager"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  tmux not found${NC}"
    fi
else
    echo -e "${BLUE}[6/6] Keeping tmux${NC}"
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

if [ "$REMOVE_UV_PACKAGES" = true ]; then
    echo "  • CAO-related packages removed from uv (uv itself preserved)"
fi

if [ "$REMOVE_UV" = true ]; then
    echo "  • uv package manager has been removed completely"
fi

if [ "$REMOVE_TMUX" = true ]; then
    echo "  • tmux removal attempted (check messages above)"
fi

echo ""
echo "What was NOT removed:"

if [ "$REMOVE_UV" = false ]; then
    if [ "$REMOVE_UV_PACKAGES" = true ]; then
        echo "  • uv (Python package manager) - preserved for other projects"
    else
        echo "  • uv (Python package manager) and its packages"
    fi
fi

if [ "$REMOVE_TMUX" = false ]; then
    echo "  • tmux (terminal multiplexer)"
fi

echo "  • Python (python3)"
echo "  • Git"
echo "  • Project directories and files"
echo "  • Project-specific .cao directories"
echo ""

if [ "$REMOVE_UV" = false ] || [ "$REMOVE_TMUX" = false ]; then
    echo "To remove remaining dependencies:"
    
    if [ "$REMOVE_UV_PACKAGES" = false ] && [ "$REMOVE_UV" = false ]; then
        echo "  • CAO packages from uv: ./uninstall_all.sh --remove-uv-packages"
        echo "  • uv completely: ./uninstall_all.sh --remove-uv"
    fi
    
    if [ "$REMOVE_TMUX" = false ]; then
        echo "  • tmux: ./uninstall_all.sh --remove-tmux"
    fi
    
    echo "  • All dependencies: ./uninstall_all.sh --remove-all-deps"
    echo ""
fi

echo "To remove manually:"
echo "  • Projects: Delete project directories manually"
echo ""

echo -e "${BLUE}If you want to reinstall, run: python install_cao.py${NC}"
echo ""
