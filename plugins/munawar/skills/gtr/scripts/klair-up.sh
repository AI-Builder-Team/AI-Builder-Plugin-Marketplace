#!/bin/bash
# klair-up.sh — Launch frontend + backend for any worktree
#
# Resolves worktree paths via `git gtr` — no hardcoded paths needed.
# Must be run from inside any worktree of the target git repo.
#
# Usage:
#   klair-up                  # auto-detect worktree from cwd
#   klair-up 016              # launch worktree 016-*
#   klair-up main             # launch main worktree
#   klair-up --stop           # kill processes for current worktree
#   klair-up --stop 016       # kill processes for worktree 016
#   klair-up --list           # show running klair instances
#
# Port scheme (suffix always matches between frontend and backend):
#   Numbered branches (NNN-*):        frontend 3NNN, backend 8NNN
#   Unnumbered (including main):      auto-finds next free slot (3001/8001, 3002/8002, ...)
#
# Prerequisites:
#   - git gtr installed (brew tap coderabbitai/tap && brew install git-gtr)
#   - Each worktree must have klair-api/.venv and klair-client/node_modules
#   - .env files must exist in klair-api/ and klair-client/

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${GREEN}▸${NC} $*"; }
warn() { echo -e "${YELLOW}▸${NC} $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }

# ── Verify gtr is available ─────────────────────────────────────

if ! git gtr version &>/dev/null; then
    err "git gtr is not installed. Install via: brew tap coderabbitai/tap && brew install git-gtr"
    exit 1
fi

# ── Resolve worktree name ───────────────────────────────────────

resolve_worktree() {
    local arg="${1:-}"

    # No argument: detect from cwd
    if [[ -z "$arg" ]]; then
        local cwd
        cwd="$(pwd)"

        # Parse git worktree list: each line is "<path> <hash> [<branch>]"
        local first=true
        while IFS= read -r line; do
            local wt_path
            wt_path=$(echo "$line" | awk '{print $1}')

            if [[ "$cwd" == "$wt_path"* ]]; then
                if $first; then
                    echo "main"
                else
                    basename "$wt_path"
                fi
                return
            fi
            first=false
        done < <(git worktree list 2>/dev/null)

        err "Not inside a known worktree. Pass a worktree number or name (e.g. 016 or fix-login-bug)."
        exit 1
    fi

    # Normalize slashes to dashes (gtr replaces / with - in folder names)
    arg="${arg//\//-}"

    # Argument is "main"
    if [[ "$arg" == "main" ]]; then
        echo "main"
        return
    fi

    # Try exact match via gtr
    if git gtr go "$arg" &>/dev/null; then
        basename "$(git gtr go "$arg")"
        return
    fi

    # Number prefix — scan worktree list for NNN-* match
    local match
    match=$(git worktree list 2>/dev/null | awk '{print $1}' | xargs -I{} basename {} | grep "^${arg}-" | head -1)
    if [[ -n "$match" ]]; then
        echo "$match"
        return
    fi

    err "No worktree found matching '$arg'. Run 'git gtr list' to see available worktrees."
    exit 1
}

get_worktree_path() {
    local name="$1"
    if [[ "$name" == "main" ]]; then
        # Main worktree is always the first line of git worktree list
        git worktree list | head -1 | awk '{print $1}'
    else
        # Try gtr go with the folder name (which is typically the branch name)
        git gtr go "$name" 2>/dev/null || {
            # Fallback: scan worktree list for a path ending in this name
            local path
            path=$(git worktree list 2>/dev/null | awk '{print $1}' | while read -r p; do
                [[ "$(basename "$p")" == "$name" ]] && echo "$p" && break
            done)
            if [[ -n "$path" ]]; then
                echo "$path"
            else
                err "Could not resolve path for worktree '$name'"
                exit 1
            fi
        }
    fi
}

get_worktree_number() {
    local name="$1"
    # Extract leading digits from the directory name
    local digits
    digits=$(echo "$name" | sed 's/^\([0-9]*\).*/\1/' | sed 's/^0*//')
    if [[ -z "$digits" ]]; then
        echo ""  # unnumbered (including main) — needs auto-assignment
    else
        echo "$digits"
    fi
}

find_next_free_slot() {
    local slot=1
    while [[ $slot -lt 999 ]]; do
        if ! lsof -i ":$((3000 + slot))" &>/dev/null && ! lsof -i ":$((8000 + slot))" &>/dev/null; then
            echo "$slot"
            return
        fi
        slot=$((slot + 1))
    done
    err "No free port slot found in range 1-998!"
    exit 1
}

get_ports() {
    local num="$1"
    if [[ -z "$num" ]]; then
        # Unnumbered branch — find next free slot
        num=$(find_next_free_slot)
        log "Auto-assigned port slot ${num} for unnumbered branch"
    fi
    BACKEND_PORT=$((8000 + num))
    FRONTEND_PORT=$((3000 + num))
}

# ── PID file management ──────────────────────────────────────────

pid_dir() {
    local dir="/tmp/klair-up"
    mkdir -p "$dir"
    echo "$dir"
}

save_pids() {
    local name="$1" be_pid="$2" fe_pid="$3" be_port="$4" fe_port="$5"
    echo "${be_pid},${fe_pid},${be_port},${fe_port}" > "$(pid_dir)/${name}.pids"
}

# ── Stop command ─────────────────────────────────────────────────

do_stop() {
    local arg="${1:-}"
    local name
    name=$(resolve_worktree "$arg")
    local pidfile="$(pid_dir)/${name}.pids"

    if [[ ! -f "$pidfile" ]]; then
        err "No running instance found for '$name'. Use 'klair-up --list' to see running instances."
        exit 1
    fi

    IFS=',' read -r be_pid fe_pid be_port fe_port < "$pidfile"
    log "Stopping $name (backend :$be_port PID=$be_pid, frontend :$fe_port PID=$fe_pid)..."
    kill "$be_pid" 2>/dev/null || true
    kill "$fe_pid" 2>/dev/null || true
    rm -f "$pidfile"
    log "Stopped."
}

# ── List command ─────────────────────────────────────────────────

do_list() {
    local pdir
    pdir="$(pid_dir)"
    local found=false

    echo -e "${BOLD}Running Klair instances:${NC}"
    echo ""
    printf "  ${BOLD}%-35s %-12s %-12s %-10s${NC}\n" "WORKTREE" "BACKEND" "FRONTEND" "STATUS"
    printf "  %-35s %-12s %-12s %-10s\n" "--------" "-------" "--------" "------"

    for pidfile in "$pdir"/*.pids; do
        [[ -f "$pidfile" ]] || continue
        found=true
        local name
        name=$(basename "$pidfile" .pids)
        IFS=',' read -r be_pid fe_pid BACKEND_PORT FRONTEND_PORT < "$pidfile"

        local status="${GREEN}running${NC}"
        if ! kill -0 "$be_pid" 2>/dev/null && ! kill -0 "$fe_pid" 2>/dev/null; then
            rm -f "$pidfile"
            continue
        elif ! kill -0 "$be_pid" 2>/dev/null; then
            status="${YELLOW}backend down${NC}"
        elif ! kill -0 "$fe_pid" 2>/dev/null; then
            status="${YELLOW}frontend down${NC}"
        fi

        printf "  %-35s %-12s %-12s " "$name" ":$BACKEND_PORT" ":$FRONTEND_PORT"
        echo -e "$status"
    done

    if ! $found; then
        echo "  (none)"
    fi
    echo ""

    if $found; then
        echo -e "  ${CYAN}Tail logs:${NC}"
        echo -e "    tail -f /tmp/klair-up/logs/<worktree>-backend.log"
        echo -e "    tail -f /tmp/klair-up/logs/<worktree>-frontend.log"
        echo ""
    fi
}

# ── Main: launch ─────────────────────────────────────────────────

do_launch() {
    local arg="${1:-}"
    local name
    name=$(resolve_worktree "$arg")
    local wt_path
    wt_path=$(get_worktree_path "$name")
    local num
    num=$(get_worktree_number "$name")
    get_ports "$num"

    local api_dir="$wt_path/klair-api"
    local client_dir="$wt_path/klair-client"

    # Validate
    if [[ ! -d "$api_dir" ]]; then
        err "Backend not found: $api_dir"
        exit 1
    fi
    if [[ ! -d "$client_dir" ]]; then
        err "Frontend not found: $client_dir"
        exit 1
    fi

    # Check if already running
    local pidfile="$(pid_dir)/${name}.pids"
    if [[ -f "$pidfile" ]]; then
        IFS=',' read -r be_pid fe_pid _be_port _fe_port < "$pidfile"
        if kill -0 "$be_pid" 2>/dev/null || kill -0 "$fe_pid" 2>/dev/null; then
            warn "Worktree '$name' is already running (backend=$be_pid, frontend=$fe_pid)"
            warn "Use 'klair-up --stop $name' first, or 'klair-up --list' to see all."
            exit 1
        fi
        rm -f "$pidfile"
    fi

    # Check port availability
    if lsof -i ":$BACKEND_PORT" &>/dev/null; then
        err "Backend port $BACKEND_PORT is already in use!"
        exit 1
    fi
    if lsof -i ":$FRONTEND_PORT" &>/dev/null; then
        err "Frontend port $FRONTEND_PORT is already in use!"
        exit 1
    fi

    local log_dir="/tmp/klair-up/logs"
    mkdir -p "$log_dir"

    echo ""
    echo -e "${BOLD}${CYAN}Launching Klair: ${name}${NC}"
    echo -e "  Worktree:  $wt_path"
    echo -e "  Backend:   http://localhost:${BACKEND_PORT}"
    echo -e "  Frontend:  http://localhost:${FRONTEND_PORT}"
    echo ""

    # ── Start backend ──
    log "Starting backend on port $BACKEND_PORT..."
    (
        cd "$api_dir"
        # Activate venv if present
        if [[ -f .venv/bin/activate ]]; then
            source .venv/bin/activate
        fi
        # Source the .env file (simple approach - just export PORT override)
        set -a
        [[ -f .env ]] && source .env
        set +a
        PORT=$BACKEND_PORT exec python fast_endpoint.py \
            > "$log_dir/${name}-backend.log" 2>&1
    ) &
    local be_pid=$!

    # ── Start frontend ──
    log "Starting frontend on port $FRONTEND_PORT..."
    (
        cd "$client_dir"
        # Override the API URL to point to our backend port
        export VITE_AI_ADOPTION_API_URL="http://localhost:${BACKEND_PORT}"
        exec pnpm dev --port "$FRONTEND_PORT" \
            > "$log_dir/${name}-frontend.log" 2>&1
    ) &
    local fe_pid=$!

    save_pids "$name" "$be_pid" "$fe_pid" "$BACKEND_PORT" "$FRONTEND_PORT"

    # Wait a moment and verify processes started
    sleep 2
    local ok=true
    if ! kill -0 "$be_pid" 2>/dev/null; then
        err "Backend failed to start! Check: $log_dir/${name}-backend.log"
        ok=false
    fi
    if ! kill -0 "$fe_pid" 2>/dev/null; then
        err "Frontend failed to start! Check: $log_dir/${name}-frontend.log"
        ok=false
    fi

    if $ok; then
        echo ""
        log "${GREEN}Both services running!${NC}"
        echo -e "  Backend log:  ${CYAN}tail -f $log_dir/${name}-backend.log${NC}"
        echo -e "  Frontend log: ${CYAN}tail -f $log_dir/${name}-frontend.log${NC}"
        echo -e "  Stop:         ${CYAN}klair-up --stop${NC}"
        echo ""
    fi
}

# ── CLI dispatch ─────────────────────────────────────────────────

case "${1:-}" in
    --stop|-s)
        shift
        do_stop "${1:-}"
        ;;
    --list|-l)
        do_list
        ;;
    --help|-h)
        echo "Usage: klair-up [worktree-number|name|main]"
        echo "       klair-up --stop [worktree-number|name|main]"
        echo "       klair-up --list"
        echo ""
        echo "Examples:"
        echo "  klair-up              # auto-detect from cwd"
        echo "  klair-up 016          # launch worktree 016-* (ports 3016/8016)"
        echo "  klair-up fix-bug      # launch unnumbered worktree (auto-assigns ports)"
        echo "  klair-up main         # launch main worktree (auto-assigns ports)"
        echo "  klair-up --stop 016   # stop worktree 016"
        echo "  klair-up --stop       # stop worktree detected from cwd"
        echo "  klair-up --list       # show all running instances"
        ;;
    *)
        do_launch "${1:-}"
        ;;
esac
