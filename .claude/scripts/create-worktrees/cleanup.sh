#!/bin/bash

################################################################################
# Interactive Worktree Cleanup Script
################################################################################
#
# Description:
#   Interactively select and remove git worktrees with detailed status info
#   Supports both interactive and automated modes
#
# Usage:
#   ./cleanup.sh                              # Interactive mode
#   ./cleanup.sh --auto tree1,tree2           # Automated mode (no prompts)
#   ./cleanup.sh --auto *                     # Automated mode (clean all)
#   ./cleanup.sh --auto tree1 --update-main   # Cleanup and update main branch
#
# Behavior:
#   - Interactive: Lists worktrees, prompts for selection and confirmation
#   - Automated: Cleans specified trees without prompts (for scripts)
#   - --update-main: After cleanup, checkout main and pull latest changes
#
################################################################################

# Ensure we're in the git repository root
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get to repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT" || exit 1

# Check if trees directory exists
if [ ! -d "trees" ]; then
    echo "No worktrees found (trees/ directory doesn't exist)"
    exit 0
fi

# Parse arguments
AUTO_MODE=false
AUTO_SELECTION=""
UPDATE_MAIN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO_MODE=true
            AUTO_SELECTION="$2"
            shift 2
            ;;
        --update-main)
            UPDATE_MAIN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate auto mode
if [ "$AUTO_MODE" = true ] && [ -z "$AUTO_SELECTION" ]; then
    echo "Error: --auto requires a selection argument (e.g., tree1,tree2 or *)"
    exit 1
fi

# Find all tree directories (exclude parent trees/ directory)
TREES=($(find trees -maxdepth 1 -type d -name "tree[0-9]*" | sort -V))

if [ ${#TREES[@]} -eq 0 ]; then
    echo "No worktrees found"
    exit 0
fi

# Only display list in interactive mode
if [ "$AUTO_MODE" = false ]; then
    echo "Available worktrees:"
    echo ""
fi

# Function to get human-readable time ago
get_time_ago() {
    local timestamp=$1
    local now=$(date +%s)
    local diff=$((now - timestamp))

    if [ $diff -lt 3600 ]; then
        echo "$((diff / 60))m ago"
    elif [ $diff -lt 86400 ]; then
        echo "$((diff / 3600))h ago"
    elif [ $diff -lt 604800 ]; then
        echo "$((diff / 86400))d ago"
    else
        echo "$((diff / 604800))w ago"
    fi
}

# Store tree info for later use
declare -a TREE_PATHS
declare -a TREE_BRANCHES

# Display tree information
INDEX=1
for TREE_DIR in "${TREES[@]}"; do
    TREE_NAME=$(basename "$TREE_DIR")
    TREE_PATHS[$INDEX]="$TREE_DIR"

    # Get branch name
    BRANCH_NAME=$(cd "$TREE_DIR" && git branch --show-current 2>/dev/null)
    TREE_BRANCHES[$INDEX]="$BRANCH_NAME"

    # Only gather detailed info in interactive mode
    if [ "$AUTO_MODE" = false ]; then
        # Extract feature name (part after treeN-)
        if [[ "$BRANCH_NAME" =~ ^tree[0-9]+-(.+)$ ]]; then
            FEATURE_NAME="${BASH_REMATCH[1]}"
        else
            FEATURE_NAME="$BRANCH_NAME"
        fi

        # Get last modified time
        if [[ "$OSTYPE" == "darwin"* ]]; then
            MOD_TIME=$(stat -f %m "$TREE_DIR" 2>/dev/null)
        else
            MOD_TIME=$(stat -c %Y "$TREE_DIR" 2>/dev/null)
        fi
        TIME_AGO=$(get_time_ago "$MOD_TIME")

        # Check if pushed to remote
        REMOTE_STATUS=""
        if [ -n "$BRANCH_NAME" ]; then
            TRACKING_BRANCH=$(cd "$TREE_DIR" && git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
            if [ -n "$TRACKING_BRANCH" ]; then
                REMOTE_STATUS="↑"
            else
                REMOTE_STATUS="-"
            fi
        else
            REMOTE_STATUS="-"
        fi

        # Check for PR status (requires gh CLI)
        PR_STATUS=""
        if command -v gh &> /dev/null && [ -n "$BRANCH_NAME" ]; then
            PR_INFO=$(cd "$TREE_DIR" && gh pr list --head "$BRANCH_NAME" --json number,state,title 2>/dev/null | grep -o '"number":[0-9]*\|"state":"[^"]*"')
            if [ -n "$PR_INFO" ]; then
                PR_NUM=$(echo "$PR_INFO" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')
                PR_STATE=$(echo "$PR_INFO" | grep -o '"state":"[^"]*"' | cut -d'"' -f4)

                if [ "$PR_STATE" == "MERGED" ]; then
                    PR_STATUS="✓ #$PR_NUM"
                elif [ "$PR_STATE" == "OPEN" ]; then
                    PR_STATUS="○ #$PR_NUM"
                elif [ "$PR_STATE" == "CLOSED" ]; then
                    PR_STATUS="✕ #$PR_NUM"
                fi
            else
                PR_STATUS="-"
            fi
        else
            PR_STATUS="-"
        fi

        # Display in compact format
        printf "  %d. %-30s | %1s | %-8s | %s\n" "$INDEX" "$FEATURE_NAME" "$REMOTE_STATUS" "$PR_STATUS" "$TIME_AGO"
    fi

    INDEX=$((INDEX + 1))
done

if [ "$AUTO_MODE" = false ]; then
    echo ""
    echo "Legend: ↑=pushed to remote, ○=PR open, ✓=PR merged, ✕=PR closed, -=none"
    echo ""
    echo -n "Enter tree numbers to clean up (comma-separated) or * for all: "
    read -r SELECTION

    # Trim whitespace
    SELECTION=$(echo "$SELECTION" | xargs)

    if [ -z "$SELECTION" ]; then
        echo "No selection made. Exiting."
        exit 0
    fi
else
    # In auto mode, convert tree names to indices
    SELECTION=""
    if [ "$AUTO_SELECTION" == "*" ]; then
        SELECTION="*"
    else
        # Parse tree names (e.g., tree1,tree2) and convert to indices
        IFS=',' read -ra TREE_NAMES <<< "$AUTO_SELECTION"
        SELECTION_INDICES=()
        for TREE_NAME in "${TREE_NAMES[@]}"; do
            TREE_NAME=$(echo "$TREE_NAME" | xargs)
            # Find index for this tree name
            for i in "${!TREES[@]}"; do
                if [ "$(basename "${TREES[$i]}")" == "$TREE_NAME" ]; then
                    SELECTION_INDICES+=($((i + 1)))
                    break
                fi
            done
        done
        SELECTION=$(IFS=,; echo "${SELECTION_INDICES[*]}")
    fi

    if [ -z "$SELECTION" ]; then
        echo "No matching trees found for: $AUTO_SELECTION"
        exit 0
    fi
fi

# Parse selection
SELECTED_INDICES=()
if [ "$SELECTION" == "*" ]; then
    # Select all
    for i in $(seq 1 $((INDEX - 1))); do
        SELECTED_INDICES+=($i)
    done
else
    # Parse comma-separated list
    IFS=',' read -ra INDICES <<< "$SELECTION"
    for i in "${INDICES[@]}"; do
        # Trim whitespace
        i=$(echo "$i" | xargs)
        # Validate it's a number and in range
        if [[ "$i" =~ ^[0-9]+$ ]] && [ "$i" -ge 1 ] && [ "$i" -lt "$INDEX" ]; then
            SELECTED_INDICES+=($i)
        else
            echo "Warning: Invalid selection '$i' (ignored)"
        fi
    done
fi

if [ ${#SELECTED_INDICES[@]} -eq 0 ]; then
    echo "No valid trees selected. Exiting."
    exit 0
fi

# Show confirmation (skip in auto mode)
if [ "$AUTO_MODE" = false ]; then
    echo ""
    echo "You are about to delete the following worktrees:"
    for i in "${SELECTED_INDICES[@]}"; do
        TREE_PATH="${TREE_PATHS[$i]}"
        BRANCH_NAME="${TREE_BRANCHES[$i]}"
        echo "  - $(basename "$TREE_PATH") (branch: $BRANCH_NAME)"
    done
    echo ""
    echo -n "Continue? (y/n): "
    read -r CONFIRM

    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Perform deletion
echo ""
echo "Removing worktrees..."
echo ""

REMOVED_COUNT=0
FAILED_COUNT=0

for i in "${SELECTED_INDICES[@]}"; do
    TREE_PATH="${TREE_PATHS[$i]}"
    TREE_NAME=$(basename "$TREE_PATH")
    BRANCH_NAME="${TREE_BRANCHES[$i]}"

    echo "  Removing $TREE_NAME..."
    git worktree remove "$TREE_PATH" --force > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Removed $TREE_NAME"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    else
        echo "  ✗ Failed to remove $TREE_NAME via git worktree"
        # Try manual removal
        rm -rf "$TREE_PATH"
        if [ $? -eq 0 ]; then
            echo "  ✓ Manually removed $TREE_NAME directory"
            REMOVED_COUNT=$((REMOVED_COUNT + 1))
        else
            echo "  ✗ Failed to manually remove $TREE_NAME"
            FAILED_COUNT=$((FAILED_COUNT + 1))
        fi
    fi

    # Also delete the associated branch
    if [ -n "$BRANCH_NAME" ]; then
        git branch -D "$BRANCH_NAME" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "  ✓ Deleted branch: $BRANCH_NAME"
        else
            echo "  ⊘ Branch already deleted or doesn't exist: $BRANCH_NAME"
        fi
    fi
done

# Prune any stale worktree administrative data
git worktree prune > /dev/null 2>&1

echo ""
if [ $REMOVED_COUNT -gt 0 ]; then
    echo "✓ Successfully removed $REMOVED_COUNT worktree(s)"
fi
if [ $FAILED_COUNT -gt 0 ]; then
    echo "✗ Failed to remove $FAILED_COUNT worktree(s)"
fi
echo ""

# Update main branch if flag is set and cleanup was successful
if [ "$UPDATE_MAIN" = true ] && [ $REMOVED_COUNT -gt 0 ]; then
    echo "Updating main branch..."
    echo ""

    # Checkout main
    git checkout main > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Checked out main branch"

        # Pull latest changes
        git pull origin main
        if [ $? -eq 0 ]; then
            echo "  ✓ Pulled latest changes from remote"
        else
            echo "  ✗ Failed to pull latest changes"
        fi
    else
        echo "  ✗ Failed to checkout main branch"
    fi
    echo ""
fi
