#!/bin/bash

#
# Competitive Prototyping - Working Example Script (v1.2)
# This script demonstrates the clipboard-based approach that avoids escaping issues
# 
# USAGE:
# 1. Copy this file to /tmp/competitive-prototyping.sh
# 2. Replace {{TASK_DESC}} with your actual task description
# 3. Make executable: chmod +x /tmp/competitive-prototyping.sh
# 4. Run: /tmp/competitive-prototyping.sh
#
# KEY FEATURES:
# - Uses clipboard (pbcopy/paste) to avoid AppleScript escaping issues
# - Handles multi-line text, special characters, markdown, quotes
# - Fully automated - no manual user intervention required
# - Proper timing delays for Claude initialization
#

echo "🚀 Starting Competitive Prototyping (v1.2)..."
echo ""

# Detect current directory and parent
CURRENT_DIR=$(pwd)
PARENT_DIR=$(dirname "$CURRENT_DIR")

# Always use clone1 and clone2
CLONE1="$PARENT_DIR/clone1"
CLONE2="$PARENT_DIR/clone2"

echo "📂 Current directory: $CURRENT_DIR"
echo "📂 Parent directory: $PARENT_DIR"
echo ""

# Verify both clones exist
if [ ! -d "$CLONE1" ]; then
    echo "❌ Error: clone1 not found at $CLONE1"
    echo ""
    echo "📝 Please create clone1:"
    echo "   cd $PARENT_DIR"
    echo "   git clone <repo-url> clone1"
    echo ""
    exit 1
fi

if [ ! -d "$CLONE2" ]; then
    echo "❌ Error: clone2 not found at $CLONE2"
    echo ""
    echo "📝 Please create clone2:"
    echo "   cd $PARENT_DIR"
    echo "   git clone <repo-url> clone2"
    echo ""
    exit 1
fi

echo "✅ Found both required clones:"
echo "   Variant A → clone1: $CLONE1"
echo "   Variant B → clone2: $CLONE2"
echo ""

# Step 1: Write task description to temporary file
# This avoids all escaping issues with special characters
echo "📝 Creating task description..."
cat > /tmp/variant_task.txt << 'TASKEOF'
{{TASK_DESC}}

---

run in plan mode. Read all the relevant code to understand the task better, before asking any clarifying questions. Think hard about the best approach to implement. Share approach before you start implementing
TASKEOF

echo "✅ Task description created"
echo ""
echo "📋 Spawning 2 parallel Claude Code sessions..."
echo ""

#
# VARIANT A - Launch session in clone1
#
echo "🔄 Starting Variant A (clone1)..."

# Open new Warp tab and start Claude
osascript <<APPLESCRIPT
tell application "Warp"
    activate
    delay 1
    tell application "System Events"
        -- Open new tab
        keystroke "t" using command down
        delay 1
        
        -- Navigate to clone1 and start Claude
        keystroke "cd $CLONE1 && claude"
        delay 0.5
        key code 36  -- Return key
        
        -- Wait for Claude to initialize (CRITICAL: needs 4+ seconds)
        delay 4
    end tell
end tell
APPLESCRIPT

# Prepare clipboard with Variant A message
echo "VARIANT A (clone1):

$(cat /tmp/variant_task.txt)" | pbcopy

# Paste from clipboard into Claude session
osascript <<'APPLESCRIPT'
tell application "Warp"
    activate
    tell application "System Events"
        -- Paste using Cmd+V
        keystroke "v" using command down
        delay 0.5
        
        -- Submit
        key code 36  -- Return key
    end tell
end tell
APPLESCRIPT

echo "✅ Variant A session created in clone1"
sleep 2

#
# VARIANT B - Launch session in clone2
#
echo "🔄 Starting Variant B (clone2)..."

# Open new Warp tab and start Claude
osascript <<APPLESCRIPT
tell application "Warp"
    activate
    delay 1
    tell application "System Events"
        -- Open new tab
        keystroke "t" using command down
        delay 1
        
        -- Navigate to clone2 and start Claude
        keystroke "cd $CLONE2 && claude"
        delay 0.5
        key code 36  -- Return key
        
        -- Wait for Claude to initialize
        delay 4
    end tell
end tell
APPLESCRIPT

# Prepare clipboard with Variant B message
echo "VARIANT B (clone2):

$(cat /tmp/variant_task.txt)" | pbcopy

# Paste from clipboard into Claude session
osascript <<'APPLESCRIPT'
tell application "Warp"
    activate
    tell application "System Events"
        -- Paste using Cmd+V
        keystroke "v" using command down
        delay 0.5
        
        -- Submit
        key code 36  -- Return key
    end tell
end tell
APPLESCRIPT

echo "✅ Variant B session created in clone2"
echo ""

# Cleanup
rm -f /tmp/variant_task.txt

echo "🎉 Both competitive prototyping sessions created successfully!"
echo ""
echo "📍 Session Details:"
echo "  • Variant A working in clone1: $CLONE1"
echo "  • Variant B working in clone2: $CLONE2"
echo ""
echo "📍 What Happens Next:"
echo "  • Both sessions received the same task description"
echo "  • Both will run in PLAN MODE"
echo "  • Both will read relevant code before asking questions"
echo "  • Both will think about the best approach"
echo "  • Both will share their approach before implementing"
echo ""
echo "📍 Your Next Steps:"
echo "  1. Switch to the new Warp tabs to see both variants"
echo "  2. Monitor both as they plan their approaches"
echo "  3. Compare their implementation strategies"
echo "  4. Let them implement independently"
echo "  5. Choose the best implementation"
echo ""
echo "💡 Tip: Both Claude instances work in separate clones with no file"
echo "   conflicts. You can safely compare implementations later."
echo ""
