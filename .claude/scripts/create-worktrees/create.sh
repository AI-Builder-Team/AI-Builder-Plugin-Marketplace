#!/bin/bash

################################################################################
# Git Worktree Creation Script with Cross-Platform Terminal Support
################################################################################
#
# Description:
#   Automatically creates git worktrees with sequential tree numbering and
#   branch naming based on feature names. Detects existing trees and fills
#   gaps if worktrees have been removed. Installs all dependencies and launches
#   services in a terminal window with appropriate port assignments.
#
# Usage:
#   ./create.sh <feature-name> [base-branch] [flags]
#
# Arguments:
#   feature-name  - Name of the feature (MUST be pre-sanitized)
#                   Valid characters: alphanumeric, hyphens (-), underscores (_), forward slashes (/)
#                   Examples: user-authentication, fix_bug_123, feature-v2, fix/invoicing-key-metric
#
#   base-branch   - (Optional) Branch to base the new worktree on
#                   Default: main
#
# Flags:
#   --branch <name> Use existing branch instead of creating new one
#   --full          Install all sub-project dependencies (not just client+api)
#   --no-install    Skip dependency installation entirely (fastest)
#   --no-terminal   Don't attempt to open terminal window
#   --no-claude     Skip opening Claude Code session
#   --task "desc"   Task description for Claude session
#
# Examples:
#   ./create.sh user-authentication
#     Creates: trees/tree2/ with branch tree2-user-authentication from main
#     Opens: terminal running services on ports 3002/5002
#
#   ./create.sh --branch feature/existing-branch
#     Creates: trees/tree2/ checking out existing branch feature/existing-branch
#     Opens: terminal running services on ports 3002/5002
#
#   ./create.sh payment-integration develop --full
#     Creates: trees/tree3/ with branch tree3-payment-integration from develop
#     Installs all sub-project dependencies
#
#   ./create.sh quick-fix --no-install --no-terminal
#     Creates: trees/tree4/ with branch tree4-quick-fix from main
#     Copies .env files only, no install, no terminal
#
# Port Assignments:
#   - Main worktree (repo root): frontend 3001, backend 5001
#   - Frontend: 3000 + tree_number (tree2 = 3002, tree3 = 3003, etc.)
#   - Backend:  5000 + tree_number (tree2 = 5002, tree3 = 5003, etc.)
#
# Environment Configuration:
#   - Branch 'main': Uses dev API (https://dev-adoption-api.klairvoyant.ai/)
#   - Branch 'prod': Uses prod API (https://adoption-api.klairvoyant.ai/)
#   - Other branches: Uses localhost with dynamic ports
#
################################################################################

# Parse optional flags first to check for --branch
SPAWN_CLAUDE=true
TASK_DESCRIPTION=""
FULL_INSTALL=false
NO_INSTALL=false
NO_TERMINAL=false
USE_EXISTING_BRANCH=false
EXISTING_BRANCH_NAME=""

# First pass: check for --branch flag
TEMP_ARGS=("$@")
for ((i=0; i<${#TEMP_ARGS[@]}; i++)); do
    if [ "${TEMP_ARGS[$i]}" = "--branch" ]; then
        USE_EXISTING_BRANCH=true
        if [ -z "${TEMP_ARGS[$((i+1))]}" ] || [[ "${TEMP_ARGS[$((i+1))]}" =~ ^-- ]]; then
            echo "Error: --branch requires a branch name argument"
            exit 1
        fi
        EXISTING_BRANCH_NAME="${TEMP_ARGS[$((i+1))]}"
        break
    fi
done

# Validate arguments
if [ "$USE_EXISTING_BRANCH" = false ] && [ -z "$1" ]; then
    echo "Error: Feature name is required (or use --branch <branch-name>)"
    echo ""
    echo "Usage: $0 <feature-name> [base-branch] [flags]"
    echo "   OR: $0 --branch <existing-branch> [flags]"
    echo ""
    echo "Flags:"
    echo "  --branch <name> Use existing branch instead of creating new one"
    echo "  --full          Install all sub-project dependencies"
    echo "  --no-install    Skip dependency installation"
    echo "  --no-terminal   Don't open terminal window"
    echo "  --no-claude     Skip Claude Code session"
    echo "  --task \"desc\"   Task description for Claude"
    echo ""
    echo "Examples:"
    echo "  $0 user-authentication"
    echo "  $0 --branch feature/existing-branch"
    echo "  $0 payment-gateway develop"
    echo "  $0 feature-name main --no-claude"
    echo "  $0 feature-name main --full --task 'Task description here'"
    echo "  $0 quick-fix --no-install --no-terminal"
    exit 1
fi

# Set feature name and base branch
if [ "$USE_EXISTING_BRANCH" = false ]; then
    FEATURE_NAME="$1"
    BASE_BRANCH="main"

    # Check if second argument is a base branch (not a flag starting with --)
    if [ -n "$2" ] && [[ ! "$2" =~ ^-- ]]; then
        BASE_BRANCH="$2"
        shift 2
    else
        shift 1
    fi
else
    # For existing branch mode, feature name is not needed
    FEATURE_NAME=""
fi

# Parse all flags
while [[ $# -gt 0 ]]; do
    case $1 in
        --branch)
            # Already handled in first pass
            shift 2
            ;;
        --no-claude)
            SPAWN_CLAUDE=false
            shift
            ;;
        --task)
            if [ -z "$2" ] || [[ "$2" =~ ^-- ]]; then
                echo "Error: --task requires a description argument"
                exit 1
            fi
            TASK_DESCRIPTION="$2"
            shift 2
            ;;
        --full)
            FULL_INSTALL=true
            shift
            ;;
        --no-install)
            NO_INSTALL=true
            shift
            ;;
        --no-terminal)
            NO_TERMINAL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate feature name is pre-sanitized (only if creating new branch)
if [ "$USE_EXISTING_BRANCH" = false ]; then
    if ! [[ "$FEATURE_NAME" =~ ^[a-zA-Z0-9_/-]+$ ]]; then
        echo "Error: Feature name must be pre-sanitized"
        echo ""
        echo "Invalid feature name: '$FEATURE_NAME'"
        echo ""
        echo "Valid characters:"
        echo "  - Alphanumeric (a-z, A-Z, 0-9)"
        echo "  - Hyphens (-)"
        echo "  - Underscores (_)"
        echo "  - Forward slashes (/)"
        echo ""
        echo "Examples of valid names:"
        echo "  user-authentication"
        echo "  fix_bug_123"
        echo "  feature-v2"
        echo "  fix/invoicing-key-metric"
        exit 1
    fi
fi

# Ensure we're in the git repository root
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get to repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT" || exit 1

# Create trees directory if it doesn't exist
mkdir -p trees

# Find the next available tree number (fill gaps if any)
# Start at tree2 since tree1 (ports 3001/5001) is reserved for main worktree
TREE_NUM=2
while [ -d "trees/tree$TREE_NUM" ]; do
    TREE_NUM=$((TREE_NUM + 1))
done

TREE_NAME="tree$TREE_NUM"
TREE_PATH="trees/$TREE_NAME"

# Set branch name based on mode
if [ "$USE_EXISTING_BRANCH" = true ]; then
    BRANCH_NAME="$EXISTING_BRANCH_NAME"

    # Check if branch exists locally or remotely
    if git rev-parse --verify "$BRANCH_NAME" > /dev/null 2>&1; then
        echo "Found local branch: $BRANCH_NAME"
    else
        # Strip origin/ prefix if present
        REMOTE_BRANCH_NAME="${BRANCH_NAME#origin/}"
        if git ls-remote --heads origin "$REMOTE_BRANCH_NAME" | grep -q "$REMOTE_BRANCH_NAME"; then
            echo "Found remote branch: origin/$REMOTE_BRANCH_NAME"
            # Fetch the remote branch
            echo "Fetching remote branch..."
            git fetch origin "$REMOTE_BRANCH_NAME:$REMOTE_BRANCH_NAME" 2>/dev/null || {
                echo "Error: Failed to fetch remote branch '$REMOTE_BRANCH_NAME'"
                exit 1
            }
            BRANCH_NAME="$REMOTE_BRANCH_NAME"
        else
            echo "Error: Branch '$BRANCH_NAME' does not exist locally or remotely"
            echo ""
            echo "Available local branches:"
            git branch | head -10
            echo ""
            echo "Available remote branches:"
            git branch -r | head -10
            exit 1
        fi
    fi
else
    BRANCH_NAME="$TREE_NAME-$FEATURE_NAME"

    # Verify base branch exists
    if ! git rev-parse --verify "$BASE_BRANCH" > /dev/null 2>&1; then
        echo "Error: Base branch '$BASE_BRANCH' does not exist"
        echo ""
        echo "Available branches:"
        git branch -a | head -10
        exit 1
    fi
fi

# Calculate ports for this worktree
FRONTEND_PORT=$((3000 + TREE_NUM))
BACKEND_PORT=$((5000 + TREE_NUM))

# Calculate total steps based on flags
TOTAL_STEPS=4
if [ "$NO_INSTALL" = false ]; then
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
fi
if [ "$NO_TERMINAL" = false ]; then
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
fi
CURRENT_STEP=0

step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo ""
    echo "[$CURRENT_STEP/$TOTAL_STEPS] $1"
    echo ""
}

# Cleanup trap for failed worktrees
cleanup_on_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ] && [ -n "$TREE_PATH" ] && [ -d "$TREE_PATH" ]; then
        echo ""
        echo "Cleaning up failed worktree..."
        git worktree remove "$TREE_PATH" --force 2>/dev/null || {
            echo "Warning: Could not remove worktree automatically"
            echo "Please run: git worktree remove '$TREE_PATH' --force"
        }
    fi
}

# Set trap at the beginning of the script
trap cleanup_on_error EXIT

################################################################################
# Step 1: Create worktree
################################################################################
step "Creating worktree..."

if [ "$USE_EXISTING_BRANCH" = true ]; then
    # Checkout existing branch
    if ! git worktree add "$TREE_PATH" "$BRANCH_NAME"; then
        echo ""
        echo "Failed to create worktree with existing branch"
        exit 1
    fi
    echo "  Location:   $TREE_PATH"
    echo "  Branch:     $BRANCH_NAME (existing)"
else
    # Create new branch
    if ! git worktree add "$TREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH"; then
        echo ""
        echo "Failed to create worktree"
        exit 1
    fi
    echo "  Location:   $TREE_PATH"
    echo "  Branch:     $BRANCH_NAME (new)"
    echo "  Based on:   $BASE_BRANCH"
fi

# Validate worktree was actually created
if [ ! -d "$TREE_PATH" ]; then
    echo ""
    echo "ERROR: Worktree creation reported success but directory does not exist: $TREE_PATH"
    echo "This may indicate a file system or git configuration issue"
    exit 1
fi

# Validate it's a valid git directory
if ! git -C "$TREE_PATH" rev-parse --git-dir > /dev/null 2>&1; then
    echo ""
    echo "ERROR: Worktree directory exists but is not a valid git repository"
    git worktree remove "$TREE_PATH" --force 2>/dev/null || true
    exit 1
fi

################################################################################
# Step 2: Copy environment files
################################################################################
step "Copying environment files..."

# All known .env file locations in the monorepo
ENV_LOCATIONS=(
    "klair-api/.env"
    "klair-client/.env"
    "klair-misc/klair-mcp-ts/.env"
    "klair-misc/redshift-mcp-old/.env"
    "klair-misc/orphan-classes-lambda/.env"
    "klair-udm/brokerage-ocr/.env"
    "klair-udm/netsuite-reports-poc/.env"
    "klair-udm/kubera/.env"
    "klair-udm/ps_pipeline/.env"
    "klair-udm/netsuite-reports-poc-2/.env"
    "klair-udm/renewals-pipeline/.env"
)

# All known credentials.json file locations in the monorepo
CREDENTIALS_LOCATIONS=(
    "klair-api/credentials.json"
    "klair-udm/brokerage-ocr/credentials.json"
    "klair-udm/netsuite-reports-poc/credentials.json"
)

CRITICAL_ENV_FILES=(
    "klair-api/.env"
    "klair-client/.env"
)

CRITICAL_CREDENTIALS_FILES=(
    "klair-api/credentials.json"
)

COPIED_FILES=0
SKIPPED_FILES=0
FAILED_CRITICAL=0
FAILED_OPTIONAL=0

for env_file in "${ENV_LOCATIONS[@]}"; do
    if [ -f "$env_file" ]; then
        # Ensure target directory exists (worktree clones directory structure,
        # but subdirectories may not exist if the sub-project is newly added)
        target_dir="$TREE_PATH/$(dirname "$env_file")"
        if [ -d "$target_dir" ]; then
            if ! cp "$env_file" "$TREE_PATH/$env_file"; then
                echo "  x Failed to copy $env_file"
                # Check if this is a critical file
                if [[ " ${CRITICAL_ENV_FILES[@]} " =~ " ${env_file} " ]]; then
                    FAILED_CRITICAL=$((FAILED_CRITICAL + 1))
                    echo "    ERROR: This is a critical file required for worktree operation"
                else
                    FAILED_OPTIONAL=$((FAILED_OPTIONAL + 1))
                fi
            else
                echo "  + Copied $env_file"
                COPIED_FILES=$((COPIED_FILES + 1))
            fi
        else
            SKIPPED_FILES=$((SKIPPED_FILES + 1))
        fi
    else
        SKIPPED_FILES=$((SKIPPED_FILES + 1))
    fi
done

echo ""
echo "  Copied $COPIED_FILES file(s), skipped $SKIPPED_FILES (not found in main worktree)"

# Check for critical failures
if [ $FAILED_CRITICAL -gt 0 ]; then
    echo ""
    echo "ERROR: Failed to copy $FAILED_CRITICAL critical .env file(s)"
    echo "Cannot proceed with worktree creation - configuration is incomplete"
    echo ""
    echo "Cleaning up failed worktree..."
    git worktree remove "$TREE_PATH" --force 2>/dev/null || true
    exit 1
fi

if [ $FAILED_OPTIONAL -gt 0 ]; then
    echo ""
    echo "WARNING: Failed to copy $FAILED_OPTIONAL optional .env file(s)"
    echo "Some sub-projects may not be properly configured"
fi

################################################################################
# Step 2.1: Copy credentials.json files
################################################################################
echo ""
echo "  Copying credentials.json files..."

CREDENTIALS_COPIED=0
CREDENTIALS_SKIPPED=0
CREDENTIALS_FAILED_CRITICAL=0
CREDENTIALS_FAILED_OPTIONAL=0

for cred_file in "${CREDENTIALS_LOCATIONS[@]}"; do
    if [ -f "$cred_file" ]; then
        # Ensure target directory exists
        target_dir="$TREE_PATH/$(dirname "$cred_file")"
        if [ -d "$target_dir" ]; then
            if ! cp "$cred_file" "$TREE_PATH/$cred_file"; then
                echo "  x Failed to copy $cred_file"
                # Check if this is a critical file
                if [[ " ${CRITICAL_CREDENTIALS_FILES[@]} " =~ " ${cred_file} " ]]; then
                    CREDENTIALS_FAILED_CRITICAL=$((CREDENTIALS_FAILED_CRITICAL + 1))
                    echo "    ERROR: This is a critical file required for worktree operation"
                else
                    CREDENTIALS_FAILED_OPTIONAL=$((CREDENTIALS_FAILED_OPTIONAL + 1))
                fi
            else
                echo "  + Copied $cred_file"
                CREDENTIALS_COPIED=$((CREDENTIALS_COPIED + 1))
            fi
        else
            # Target directory doesn't exist
            if [[ " ${CRITICAL_CREDENTIALS_FILES[@]} " =~ " ${cred_file} " ]]; then
                echo "  x Target directory missing for critical file: $cred_file"
                CREDENTIALS_FAILED_CRITICAL=$((CREDENTIALS_FAILED_CRITICAL + 1))
            else
                CREDENTIALS_SKIPPED=$((CREDENTIALS_SKIPPED + 1))
            fi
        fi
    else
        CREDENTIALS_SKIPPED=$((CREDENTIALS_SKIPPED + 1))
    fi
done

echo ""
echo "  Copied $CREDENTIALS_COPIED credentials file(s), skipped $CREDENTIALS_SKIPPED (not found in main worktree)"

# Check for critical credentials failures
if [ $CREDENTIALS_FAILED_CRITICAL -gt 0 ]; then
    echo ""
    echo "ERROR: Failed to copy $CREDENTIALS_FAILED_CRITICAL critical credentials.json file(s)"
    echo "Cannot proceed with worktree creation - configuration is incomplete"
    echo ""
    echo "Cleaning up failed worktree..."
    git worktree remove "$TREE_PATH" --force 2>/dev/null || true
    exit 1
fi

if [ $CREDENTIALS_FAILED_OPTIONAL -gt 0 ]; then
    echo ""
    echo "WARNING: Failed to copy $CREDENTIALS_FAILED_OPTIONAL optional credentials.json file(s)"
    echo "Some sub-projects may not be properly configured"
fi

################################################################################
# Step 2.5: Configure environment files based on branch
################################################################################
step "Configuring environment files for branch '$BRANCH_NAME'..."

# Determine API URL based on branch
if [ "$BRANCH_NAME" = "main" ]; then
    API_URL="https://dev-adoption-api.klairvoyant.ai"
    echo "  Using DEV API: $API_URL"
elif [ "$BRANCH_NAME" = "prod" ]; then
    API_URL="https://adoption-api.klairvoyant.ai"
    echo "  Using PROD API: $API_URL"
else
    BACKEND_PORT=$((5000 + TREE_NUM))
    API_URL="http://localhost:$BACKEND_PORT"
    echo "  Using LOCAL API: $API_URL"
fi

# Update frontend .env
if [ -f "$TREE_PATH/klair-client/.env" ]; then
    if grep -q "VITE_AI_ADOPTION_API_URL" "$TREE_PATH/klair-client/.env"; then
        sed -i.bak "s|VITE_AI_ADOPTION_API_URL.*=.*https\?://[^[:space:]]*|VITE_AI_ADOPTION_API_URL = $API_URL|g" "$TREE_PATH/klair-client/.env"
        rm "$TREE_PATH/klair-client/.env.bak" 2>/dev/null
        echo "  + Updated frontend API URL"
    else
        echo "  ! Warning: VITE_AI_ADOPTION_API_URL not found in frontend .env"
    fi
else
    echo "  ! Warning: Frontend .env file not found"
fi

# Update backend .env with port (only for non-main/prod branches)
if [ "$BRANCH_NAME" != "main" ] && [ "$BRANCH_NAME" != "prod" ]; then
    if [ -f "$TREE_PATH/klair-api/.env" ]; then
        if grep -q "^PORT=" "$TREE_PATH/klair-api/.env"; then
            sed -i.bak "s|^PORT=.*|PORT=$BACKEND_PORT|g" "$TREE_PATH/klair-api/.env"
            rm "$TREE_PATH/klair-api/.env.bak" 2>/dev/null
            echo "  + Updated backend PORT to $BACKEND_PORT"
        else
            echo "  ! Warning: PORT not found in backend .env"
        fi
    else
        echo "  ! Warning: Backend .env file not found"
    fi
fi

################################################################################
# Step 3: Install dependencies (unless --no-install)
################################################################################
if [ "$NO_INSTALL" = false ]; then
    step "Installing dependencies..."

    INSTALL_FAILED=false

    # Frontend (always)
    if [ -d "$TREE_PATH/klair-client" ]; then
        echo "  Installing frontend dependencies (pnpm)..."
        INSTALL_OUTPUT=$(cd "$TREE_PATH/klair-client" && pnpm install --silent 2>&1)
        INSTALL_EXIT=$?

        if [ $INSTALL_EXIT -eq 0 ]; then
            echo "  + Frontend dependencies installed"
        else
            echo "  x Failed to install frontend dependencies"
            echo "    Error output:"
            echo "$INSTALL_OUTPUT" | sed 's/^/    /'
            INSTALL_FAILED=true
        fi
    fi

    # Backend API (always)
    if [ -d "$TREE_PATH/klair-api" ]; then
        echo "  Installing backend dependencies (uv)..."
        INSTALL_OUTPUT=$(cd "$TREE_PATH/klair-api" && uv sync --quiet 2>&1)
        INSTALL_EXIT=$?

        if [ $INSTALL_EXIT -eq 0 ]; then
            echo "  + Backend dependencies installed"
        else
            echo "  x Failed to install backend dependencies"
            echo "    Error output:"
            echo "$INSTALL_OUTPUT" | sed 's/^/    /'
            INSTALL_FAILED=true
        fi
    fi

    # Check if core installations failed
    if [ "$INSTALL_FAILED" = true ]; then
        echo ""
        echo "ERROR: Failed to install core dependencies (frontend or backend)"
        echo "Cleaning up failed worktree..."
        echo ""
        # Let the cleanup trap handle removal
        exit 1
    fi

    # Additional sub-projects (only with --full)
    if [ "$FULL_INSTALL" = true ]; then
        echo ""
        echo "  Installing additional sub-project dependencies (--full)..."

        # klair-misc/klair-mcp-ts (npm)
        if [ -d "$TREE_PATH/klair-misc/klair-mcp-ts" ] && [ -f "$TREE_PATH/klair-misc/klair-mcp-ts/package.json" ]; then
            echo "  Installing klair-mcp-ts dependencies (npm)..."
            if (cd "$TREE_PATH/klair-misc/klair-mcp-ts" && npm install --silent) > /dev/null 2>&1; then
                echo "  + klair-mcp-ts dependencies installed"
            else
                echo "  x Failed to install klair-mcp-ts dependencies"
            fi
        fi

        # klair-lambdas/hubspot_sync_v2 (uv)
        if [ -d "$TREE_PATH/klair-lambdas/hubspot_sync_v2" ] && [ -f "$TREE_PATH/klair-lambdas/hubspot_sync_v2/pyproject.toml" ]; then
            echo "  Installing hubspot_sync_v2 dependencies (uv)..."
            if (cd "$TREE_PATH/klair-lambdas/hubspot_sync_v2" && uv sync --quiet) > /dev/null 2>&1; then
                echo "  + hubspot_sync_v2 dependencies installed"
            else
                echo "  x Failed to install hubspot_sync_v2 dependencies"
            fi
        fi

        # klair-udm/renewals-pipeline (uv)
        if [ -d "$TREE_PATH/klair-udm/renewals-pipeline" ] && [ -f "$TREE_PATH/klair-udm/renewals-pipeline/pyproject.toml" ]; then
            echo "  Installing renewals-pipeline dependencies (uv)..."
            if (cd "$TREE_PATH/klair-udm/renewals-pipeline" && uv sync --quiet) > /dev/null 2>&1; then
                echo "  + renewals-pipeline dependencies installed"
            else
                echo "  x Failed to install renewals-pipeline dependencies"
            fi
        fi
    fi
fi

################################################################################
# Step 4: Configure direnv
################################################################################
step "Configuring direnv..."

echo "  Ports assigned:"
echo "    Frontend: $FRONTEND_PORT"
echo "    Backend:  $BACKEND_PORT"

# Auto-allow direnv files if direnv is installed
if command -v direnv &>/dev/null; then
    echo ""
    echo "  Allowing direnv configuration..."

    # Allow all .envrc files in the worktree
    ENVRC_FILES=(
        "$TREE_PATH/.envrc"
        "$TREE_PATH/klair-api/.envrc"
        "$TREE_PATH/klair-client/.envrc"
        "$TREE_PATH/klair-misc/klair-mcp-ts/.envrc"
        "$TREE_PATH/klair-udm/renewals-pipeline/.envrc"
    )

    for envrc in "${ENVRC_FILES[@]}"; do
        if [ -f "$envrc" ]; then
            direnv allow "$envrc" &>/dev/null && echo "  + Allowed $envrc"
        fi
    done

    echo ""
    echo "  Ports are now available as env vars when you cd into the worktree:"
    echo "    KLAIR_FRONTEND_PORT=$FRONTEND_PORT"
    echo "    KLAIR_BACKEND_PORT=$BACKEND_PORT"
else
    echo ""
    echo "  These ports are also available as env vars if direnv is configured:"
    echo "    (Requires direnv setup - see CLAUDE.md for instructions)"
    echo "    KLAIR_FRONTEND_PORT=$FRONTEND_PORT"
    echo "    KLAIR_BACKEND_PORT=$BACKEND_PORT"
fi

################################################################################
# Step 5: Open terminal (only if --no-terminal not set)
################################################################################
if [ "$NO_TERMINAL" = false ]; then
    step "Opening terminal..."
fi

ABSOLUTE_TREE_PATH="$REPO_ROOT/$TREE_PATH"

# Detect terminal and open accordingly
open_terminal() {
    local tree_path="$1"
    local cmd="$2"
    local error_output

    # 1. Warp on macOS (checks if Warp process exists, not if it's the active terminal)
    if [[ "$OSTYPE" == darwin* ]] && command -v osascript &>/dev/null; then
        if ! osascript -e 'tell application "System Events" to get name of every process' 2>/dev/null | grep -q "Warp"; then
            :  # Warp not running, try next option
        else
            error_output=$(osascript <<APPLESCRIPT 2>&1
tell application "Warp"
    activate
    delay 1
    tell application "System Events"
        keystroke "t" using command down
        delay 1
        keystroke "$cmd"
        delay 0.5
        key code 36
    end tell
end tell
APPLESCRIPT
            )
            if [ $? -eq 0 ]; then
                return 0
            else
                echo "  ! Warp detection succeeded but AppleScript failed:" >&2
                echo "$error_output" | sed 's/^/    /' >&2
            fi
        fi
    fi

    # 2. WezTerm (cross-platform)
    if command -v wezterm &>/dev/null; then
        error_output=$(wezterm cli spawn --cwd "$tree_path" -- bash -c "$cmd" 2>&1)
        if [ $? -eq 0 ]; then
            return 0
        else
            echo "  ! WezTerm available but spawn failed:" >&2
            echo "$error_output" | sed 's/^/    /' >&2
        fi
    fi

    # 3. tmux (cross-platform)
    if command -v tmux &>/dev/null && [ -n "$TMUX" ]; then
        error_output=$(tmux new-window -c "$tree_path" -n "TREE $TREE_NUM" "$cmd" 2>&1)
        if [ $? -eq 0 ]; then
            return 0
        else
            echo "  ! tmux available but new-window failed:" >&2
            echo "$error_output" | sed 's/^/    /' >&2
        fi
    fi

    # 4. Fallback -- print instructions
    return 1
}

if [ "$NO_TERMINAL" = false ]; then
    if open_terminal "$ABSOLUTE_TREE_PATH" "cd '$ABSOLUTE_TREE_PATH' && ./start-services.sh $FRONTEND_PORT $BACKEND_PORT"; then
        echo "  + Terminal opened successfully"
        echo "  Services starting on ports $FRONTEND_PORT (frontend) and $BACKEND_PORT (backend)"
    else
        echo "  No supported terminal detected (Warp, WezTerm, tmux)."
        echo ""
        echo "  Start services manually:"
        echo "    cd $TREE_PATH"
        echo "    ./start-services.sh $FRONTEND_PORT $BACKEND_PORT"
    fi

    # Spawn Claude session if requested (default behavior)
    if [ "$SPAWN_CLAUDE" = true ]; then
        echo ""
        echo "  Opening Claude Code session..."
        sleep 2

        # Try to open Claude in terminal
        if [[ "$OSTYPE" == darwin* ]] && command -v osascript &>/dev/null; then
            osascript <<APPLESCRIPT
tell application "Warp"
    activate
    delay 1
    tell application "System Events"
        keystroke "t" using command down
        delay 1
        keystroke "cd '$ABSOLUTE_TREE_PATH' && claude"
        delay 1.5
        keystroke return
        delay 5
    end tell
end tell
APPLESCRIPT

            # If task description provided, paste it into Claude session
            if [ -n "$TASK_DESCRIPTION" ]; then
                # Write task to temporary file to avoid escaping issues
                cat > /tmp/claude_task_$$.txt << TASKEOF
$TASK_DESCRIPTION
TASKEOF

                # Copy to clipboard (cross-platform)
                if command -v pbcopy &>/dev/null; then
                    cat /tmp/claude_task_$$.txt | pbcopy
                elif command -v xclip &>/dev/null; then
                    cat /tmp/claude_task_$$.txt | xclip -selection clipboard
                elif command -v xsel &>/dev/null; then
                    cat /tmp/claude_task_$$.txt | xsel --clipboard
                fi

                osascript <<'APPLESCRIPT'
tell application "Warp"
    activate
    tell application "System Events"
        keystroke "v" using command down
        delay 1.5
        keystroke return
    end tell
end tell
APPLESCRIPT

                rm -f /tmp/claude_task_$$.txt
                echo "  + Claude session opened with task description"
            else
                echo "  + Claude session opened"
            fi
        elif command -v wezterm &>/dev/null; then
            # WezTerm support
            if [ -n "$TASK_DESCRIPTION" ]; then
                wezterm cli spawn --cwd "$ABSOLUTE_TREE_PATH" -- bash -c "claude '$TASK_DESCRIPTION'"
            else
                wezterm cli spawn --cwd "$ABSOLUTE_TREE_PATH" -- bash -c "claude"
            fi
            echo "  + Claude session opened in WezTerm"
        elif command -v tmux &>/dev/null && [ -n "$TMUX" ]; then
            if [ -n "$TASK_DESCRIPTION" ]; then
                tmux new-window -c "$ABSOLUTE_TREE_PATH" -n "Claude" "claude '$TASK_DESCRIPTION'"
            else
                tmux new-window -c "$ABSOLUTE_TREE_PATH" -n "Claude" "claude"
            fi
            echo "  + Claude session opened in tmux"
        else
            echo ""
            echo "  Start Claude manually:"
            echo "    cd $TREE_PATH && claude"
            if [ -n "$TASK_DESCRIPTION" ]; then
                echo "    Then paste your task: $TASK_DESCRIPTION"
            fi
        fi
    fi
else
    echo "  Skipped (--no-terminal)"
fi

################################################################################
# Summary
################################################################################
# Disable cleanup trap on successful completion
trap - EXIT

echo ""
echo "============================================"
echo "  Worktree ready: $TREE_PATH"
echo "  Branch:         $BRANCH_NAME"
echo "  Ports:          $FRONTEND_PORT (frontend) / $BACKEND_PORT (backend)"
echo "============================================"
echo ""
echo "To start working:"
echo "  cd $TREE_PATH"
echo ""
