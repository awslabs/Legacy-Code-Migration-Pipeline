#!/bin/bash

# Configuration
THRESHOLD_HOURS=1
AUTO_MODE=false
DELETE_ALL=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--threshold)
            THRESHOLD_HOURS="$2"
            shift 2
            ;;
        -a|--auto)
            AUTO_MODE=true
            shift
            ;;
        --delete-all)
            DELETE_ALL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -t, --threshold HOURS    Set inactivity threshold in hours (default: 1)"
            echo "  -a, --auto               Auto mode: delete without confirmation"
            echo "  --delete-all             Delete all inactive windows automatically"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                       # Interactive mode, 1 hour threshold"
            echo "  $0 -t 2                  # Interactive mode, 2 hour threshold"
            echo "  $0 -t 1 -a               # Auto delete windows inactive > 1 hour"
            echo "  $0 -t 3 --delete-all     # Auto delete all windows inactive > 3 hours"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed"
    exit 1
fi

# Check if there are any tmux sessions
if ! tmux list-sessions &> /dev/null; then
    echo "No tmux sessions found"
    exit 0
fi

# Function to format time difference
format_time() {
    local time_diff=$1
    if [ $time_diff -lt 60 ]; then
        echo "${time_diff}s"
    elif [ $time_diff -lt 3600 ]; then
        echo "$((time_diff / 60))m"
    elif [ $time_diff -lt 86400 ]; then
        echo "$((time_diff / 3600))h"
    else
        echo "$((time_diff / 86400))d"
    fi
}

# Get current time
current_time=$(date +%s)
threshold_seconds=$((THRESHOLD_HOURS * 3600))

# Arrays to store inactive windows
declare -a inactive_sessions
declare -a inactive_windows
declare -a inactive_names
declare -a inactive_times

echo "=== TMUX Window Activity Report ==="
echo "Threshold: ${THRESHOLD_HOURS} hour(s)"
echo ""

# Print all windows header
printf "%-20s %-5s %-30s %-15s %-10s\n" "SESSION" "WIN#" "NAME" "LAST ACTIVITY" "STATUS"
printf "%-20s %-5s %-30s %-15s %-10s\n" "-------" "----" "----" "-------------" "------"

# Iterate through all sessions
tmux list-sessions -F "#{session_name}" | while read -r session_name; do
    # Get window information for this session
    tmux list-windows -t "$session_name" -F "#{window_index}|#{window_name}|#{window_activity}" | while IFS='|' read -r win_idx win_name win_activity; do
        # Calculate time since window activity
        time_diff=$((current_time - win_activity))
        time_str=$(format_time $time_diff)
        
        # Determine status
        if [ $time_diff -gt $threshold_seconds ]; then
            status="INACTIVE"
        else
            status="active"
        fi
        
        # Print window info
        printf "%-20s %-5s %-30s %-15s %-10s\n" "$session_name" "$win_idx" "$win_name" "$time_str" "$status"
    done
done

echo ""
echo "=== Inactive Windows (>${THRESHOLD_HOURS}h) ==="
echo ""

# Collect inactive windows
printf "%-5s %-20s %-5s %-30s %-15s\n" "ID" "SESSION" "WIN#" "NAME" "INACTIVE FOR"
printf "%-5s %-20s %-5s %-30s %-15s\n" "--" "-------" "----" "----" "------------"

counter=1
while read -r session_name; do
    tmux list-windows -t "$session_name" -F "#{window_index}|#{window_name}|#{window_activity}" | while IFS='|' read -r win_idx win_name win_activity; do
        time_diff=$((current_time - win_activity))
        
        if [ $time_diff -gt $threshold_seconds ]; then
            time_str=$(format_time $time_diff)
            printf "%-5s %-20s %-5s %-30s %-15s\n" "$counter" "$session_name" "$win_idx" "$win_name" "$time_str"
            
            # Store for deletion
            echo "$counter|$session_name|$win_idx|$win_name|$time_str" >> /tmp/tmux_inactive_$$
            counter=$((counter + 1))
        fi
    done
done < <(tmux list-sessions -F "#{session_name}")

# Check if there are any inactive windows
if [ ! -f /tmp/tmux_inactive_$$ ]; then
    echo "No inactive windows found."
    exit 0
fi

total_inactive=$((counter - 1))
echo ""
echo "Total inactive windows: $total_inactive"
echo ""

# Handle deletion based on mode
if [ "$AUTO_MODE" = true ] || [ "$DELETE_ALL" = true ]; then
    echo "Deleting inactive windows..."
    while IFS='|' read -r id session_name win_idx win_name time_str; do
        # Check if session still has multiple windows
        window_count=$(tmux list-windows -t "$session_name" 2>/dev/null | wc -l)
        if [ "$window_count" -gt 1 ]; then
            echo "Deleting: $session_name:$win_idx ($win_name)"
            tmux kill-window -t "$session_name:$win_idx" 2>/dev/null
        else
            echo "Skipping: $session_name:$win_idx (last window in session)"
        fi
    done < /tmp/tmux_inactive_$$
    rm -f /tmp/tmux_inactive_$$
    echo "Done."
else
    # Interactive mode
    echo "Options:"
    echo "  a - Delete ALL inactive windows"
    echo "  # - Delete specific window by ID (e.g., 1, 2, 3)"
    echo "  q - Quit without deleting"
    echo ""
    read -p "Enter your choice: " choice
    
    if [ "$choice" = "a" ]; then
        echo "Deleting all inactive windows..."
        while IFS='|' read -r id session_name win_idx win_name time_str; do
            window_count=$(tmux list-windows -t "$session_name" 2>/dev/null | wc -l)
            if [ "$window_count" -gt 1 ]; then
                echo "Deleting: $session_name:$win_idx ($win_name)"
                tmux kill-window -t "$session_name:$win_idx" 2>/dev/null
            else
                echo "Skipping: $session_name:$win_idx (last window in session)"
            fi
        done < /tmp/tmux_inactive_$$
        echo "Done."
    elif [ "$choice" = "q" ]; then
        echo "Cancelled."
    elif [[ "$choice" =~ ^[0-9]+$ ]]; then
        # Delete specific window
        target_line=$(sed -n "${choice}p" /tmp/tmux_inactive_$$)
        if [ -n "$target_line" ]; then
            IFS='|' read -r id session_name win_idx win_name time_str <<< "$target_line"
            window_count=$(tmux list-windows -t "$session_name" 2>/dev/null | wc -l)
            if [ "$window_count" -gt 1 ]; then
                echo "Deleting: $session_name:$win_idx ($win_name)"
                tmux kill-window -t "$session_name:$win_idx" 2>/dev/null
                echo "Done."
            else
                echo "Cannot delete: $session_name:$win_idx (last window in session)"
            fi
        else
            echo "Invalid ID: $choice"
        fi
    else
        echo "Invalid choice."
    fi
    
    rm -f /tmp/tmux_inactive_$$
fi
