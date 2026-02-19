#!/bin/bash

#
# Competitive Prototyping - Script Template (v2.0)
# This script spawns 2 parallel worktrees with running services and Claude Code sessions
# Services run in dedicated tabs, Claude sessions in separate tabs for prototyping
#
# IMPORTANT: Uses clipboard-based approach to avoid AppleScript escaping issues
# This reliably handles multi-line text, special characters, markdown, and quotes
#

echo "🚀 Starting Competitive Prototyping (v2.0)..."
echo ""

# Ensure we're in the git repository root
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT" || exit 1

echo "📂 Repository root: $REPO_ROOT"
echo ""

# Always use tree1 and tree2
TREE1="$REPO_ROOT/trees/tree1"
TREE2="$REPO_ROOT/trees/tree2"

# Cleanup existing prototyping worktrees (force clean slate)
echo "🧹 Cleaning up existing prototyping worktrees..."
.claude/scripts/create-worktrees/cleanup.sh --auto tree1,tree2
echo ""

# Feature name will be replaced by Claude during script generation
FEATURE_NAME="{{FEATURE_NAME}}"
BASE_BRANCH="${1:-main}"

echo "📝 Feature: $FEATURE_NAME"
echo "📝 Base branch: $BASE_BRANCH"
echo ""

# Step 1: Create tree1 worktree with Claude (opens Warp, starts services on 3001/5001, spawns Claude)
echo "🌲 Creating tree1 worktree with services and Claude..."
.claude/scripts/create-worktrees/create.sh "$FEATURE_NAME" "$BASE_BRANCH" --task "$TASK_DESCRIPTION"
echo ""
echo "✅ tree1 created with services running on ports 3001 (frontend) and 5001 (backend)"
echo "✅ Claude session opened with task description"
sleep 2

# Step 2: Create tree2 worktree with Claude (opens Warp, starts services on 3002/5002, spawns Claude)
echo "🌲 Creating tree2 worktree with services and Claude..."
.claude/scripts/create-worktrees/create.sh "$FEATURE_NAME" "$BASE_BRANCH" --task "$TASK_DESCRIPTION"
echo ""
echo "✅ tree2 created with services running on ports 3002 (frontend) and 5002 (backend)"
echo "✅ Claude session opened with task description"
sleep 2

echo ""
echo "📋 Both worktrees created with services and Claude sessions running!"
echo ""

echo "🎉 Competitive prototyping setup complete!"
echo ""
echo "📍 What Was Created:"
echo "  • 4 Warp tabs opened automatically:"
echo "    - Tab 1: tree1 services (frontend: 3001, backend: 5001)"
echo "    - Tab 2: tree1 Claude session (with task already submitted)"
echo "    - Tab 3: tree2 services (frontend: 3002, backend: 5002)"
echo "    - Tab 4: tree2 Claude session (with task already submitted)"
echo ""
echo "📍 Worktree Details:"
echo "  • Variant A: $TREE1 (branch: tree1-$FEATURE_NAME)"
echo "  • Variant B: $TREE2 (branch: tree2-$FEATURE_NAME)"
echo ""
echo "📍 Services Running:"
echo "  • Variant A: http://localhost:3001 (frontend) + http://localhost:5001 (backend)"
echo "  • Variant B: http://localhost:3002 (frontend) + http://localhost:5002 (backend)"
echo ""
echo "📍 What Happens Next:"
echo "  • Both Claude sessions already have the task description submitted"
echo "  • Both will run in PLAN MODE"
echo "  • Both will read relevant code before asking questions"
echo "  • Both will think about the best approach"
echo "  • Both will share their approach before implementing"
echo "  • Services are live - test implementations as they develop!"
echo ""
echo "📍 Your Next Steps:"
echo "  1. Check Claude tabs (2 & 4) to see both variants' plans"
echo "  2. Monitor both as they plan their approaches"
echo "  3. Compare their implementation strategies"
echo "  4. Test in real-time at localhost:3001 and localhost:3002"
echo "  5. Let them implement independently"
echo "  6. Choose the best implementation"
echo ""
echo "💡 Tip: Both Claude instances work in separate worktrees with no file"
echo "   conflicts. Worktrees share .git so they use ~66% less disk space!"
echo ""
