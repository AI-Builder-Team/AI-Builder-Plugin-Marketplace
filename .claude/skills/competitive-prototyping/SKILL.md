---
name: competitive-prototyping
description: Use when user wants to explore multiple implementation approaches for a feature by creating parallel Claude Code sessions. Triggers on phrases like "competitive prototyping", "prototype in parallel", "compare implementations", "try different approaches", or "race implementations".
---

# Competitive Prototyping

This skill helps users explore multiple implementation strategies for a single feature by spawning parallel Claude Code sessions in Warp terminal. Each session runs in a separate clone of the repository, allowing Claude instances to work independently without file conflicts.

## When to Use This Skill

Activate this skill when the user:
- Wants to prototype a feature with multiple different approaches
- Needs to compare different implementation strategies
- Wants to explore architectural alternatives
- Asks to "try multiple ways" or "see different implementations"
- Mentions wanting parallel development or competitive prototyping

## Workflow

### 1. Gather Feature Details and Create Concise Task Description

**Do NOT ask extensive clarifying questions at this stage.**

1. **Listen to the user's feature description** - they will provide the feature details
2. **Create a concise, high-level task description** that summarizes:
   - What the feature does (1-2 sentences)
   - Key requirements or constraints
   - Any technical context provided by the user
3. **Ask ONLY for glaring clarifications** if something is critically unclear or ambiguous
4. **Keep it concise** - the goal is a high-level overview, not a detailed spec

### 2. Format Task Description

Format the task description to be sent to both Claude instances. Keep it concise and focused:

```
# Task: [Feature Name]

[Concise description of what needs to be built - 1-3 paragraphs maximum]

## Key Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Technical Context
[Any relevant technical details, constraints, or codebase context]

---

run in plan mode. Read all the relevant code to understand the task better, before asking any clarifying questions. Think hard about the best approach to implement. Share approach before you start implementing
```

**CRITICAL**: The message MUST end with: "run in plan mode. Read all the relevant code to understand the task better, before asking any clarifying questions. Think hard about the best approach to implement. Share approach before you start implementing"

### 3. Generate and Execute Competitive Prototyping Script

**CRITICAL**: Use the clipboard-based approach to avoid AppleScript escaping issues with special characters, quotes, newlines, and markdown.

**Workflow**:
1. Read the `spawn-variants.sh` template file from the skill directory
2. Copy the entire template to `/tmp/competitive-prototyping.sh` using Bash heredoc (NOT Write tool)
3. Extract feature name from task description and sanitize it (lowercase, hyphens, alphanumeric only)
4. Use the Edit tool to replace `{{FEATURE_NAME}}` with the sanitized feature name
5. Use the Edit tool to replace `{{TASK_DESC}}` with the full task description
6. Make the script executable
7. Execute it - this will:
   - Clean up existing tree1/tree2 worktrees
   - Create tree1 worktree with services (ports 3001/5001)
   - Create tree2 worktree with services (ports 3002/5002)
   - Spawn Claude session in tree1
   - Spawn Claude session in tree2

**Why clipboard approach?**
- Handles multi-line text, special characters, markdown, quotes reliably
- Avoids complex AppleScript string escaping issues
- More robust than direct `keystroke` commands
- Standard macOS automation pattern

**Step 1**: Copy the template to /tmp using Bash (NOT Write tool):

```bash
# Read the spawn-variants.sh template and copy to /tmp
cat .claude/skills/competitive-prototyping/spawn-variants.sh > /tmp/competitive-prototyping.sh
chmod +x /tmp/competitive-prototyping.sh
```

**Step 2**: Replace the placeholders using Edit tool (TWO replacements required):

```python
# Step 2a: Extract and sanitize feature name from task description first line
# Take first line after "# Task:", remove markdown, sanitize, lowercase, limit to 50 chars
# Example: "# Task: BU Retention Metrics Trend Chart" -> "bu-retention-metrics-trend-chart"

# Step 2b: Replace {{FEATURE_NAME}} placeholder with sanitized feature name
Edit(
    file_path="/tmp/competitive-prototyping.sh",
    old_string="{{FEATURE_NAME}}",
    new_string="bu-retention-metrics-trend-chart"  # Your sanitized feature name
)

# Step 2c: Replace {{TASK_DESC}} placeholder with full task description
Edit(
    file_path="/tmp/competitive-prototyping.sh",
    old_string="{{TASK_DESC}}",
    new_string="[Your formatted task description here - can contain newlines, quotes, markdown, special chars]"
)
```

**IMPORTANT**: Replace `{{FEATURE_NAME}}` FIRST, then `{{TASK_DESC}}`. Do NOT use `replace_all: true` for either replacement!

**Step 3**: Execute the script:

```bash
/tmp/competitive-prototyping.sh
```

**What the script does** (worktree-based approach):
1. Gets repository root
2. Removes existing tree1/tree2 if present (clean slate)
3. Uses pre-filled feature name (replaced by Claude during script generation)
4. Calls `create.sh` twice to create tree1 and tree2 with services
5. Opens 2 additional Warp tabs for Claude sessions
6. Writes task description to `/tmp/variant_task.txt`
7. Copies task to clipboard and pastes into each Claude session
8. Cleans up temp file

**Result**: 4 Warp tabs
- Tab 1: tree1 services (3001/5001)
- Tab 2: tree2 services (3002/5002)
- Tab 3: tree1 Claude session
- Tab 4: tree2 Claude session

**How the script works** (clipboard-based approach):
1. Writes task description to `/tmp/variant_task.txt` (avoids escaping issues)
2. Opens new Warp tab
3. Navigates to worktree and starts Claude (`cd $TREE1 && claude`)
4. Waits 4 seconds for Claude to initialize (CRITICAL timing)
5. Copies task from temp file to clipboard using `pbcopy`
6. Pastes into Claude session using `keystroke "v" using command down`
7. Submits with Return key
8. Repeats for second variant in tree2
9. Cleans up temp file

**Key timing requirements**:
- After opening tab: 1 second
- After starting Claude: 4 seconds (CRITICAL - Claude needs time to initialize)
- After pasting: 0.5 seconds
- Between variants: 2 seconds

**Template structure** (already in spawn-variants.sh):
```bash
# Task written to temp file (handles all special characters)
cat > /tmp/variant_task.txt << 'TASKEOF'
{{TASK_DESC}}

---

run in plan mode. Read all the relevant code to understand the task better, before asking any clarifying questions. Think hard about the best approach to implement. Share approach before you start implementing
TASKEOF

# For each variant:
# 1. Open Warp tab, navigate to worktree, start Claude
osascript <<APPLESCRIPT
tell application "Warp"
    activate
    delay 1
    tell application "System Events"
        keystroke "t" using command down
        delay 1
        keystroke "cd $TREE1 && claude"
        delay 0.5
        key code 36
        delay 4  # Wait for Claude initialization
    end tell
end tell
APPLESCRIPT

# 2. Copy task to clipboard and paste
echo "VARIANT A (tree1):

$(cat /tmp/variant_task.txt)" | pbcopy

osascript <<'APPLESCRIPT'
tell application "Warp"
    activate
    tell application "System Events"
        keystroke "v" using command down  # Paste!
        delay 0.5
        key code 36  # Submit
    end tell
end tell
APPLESCRIPT
```

### 4. Execute and Guide User

**After executing the script**, inform the user about:

1. **What just happened**:
   - 4 Warp tabs opened:
     * Tab 1: tree1 services (frontend: 3001, backend: 5001)
     * Tab 2: tree2 services (frontend: 3002, backend: 5002)
     * Tab 3: Variant A Claude session in tree1
     * Tab 4: Variant B Claude session in tree2
   - Both worktrees created with branches: tree1-<feature> and tree2-<feature>
   - Both Claude sessions received the same task description automatically (fully automated!)
   - Both are running in plan mode
   - Services are live for real-time testing
   - No manual intervention was required

2. **What happens next**:
   - Both Claude instances will read relevant code
   - Both will think about the best approach
   - Both will share their plans before implementing
   - Both will implement independently
   - User can test implementations at localhost:3001 and localhost:3002 as they develop

3. **User's next steps**:
   - Switch to Claude tabs (3 & 4) to monitor both variants
   - Compare their planning approaches
   - Test implementations at localhost:3001 and localhost:3002
   - Let them implement independently
   - Choose the best implementation when both are done

4. **Cleanup**:
   - The script automatically cleaned up `/tmp/variant_task.txt`
   - User can manually remove unused worktree: `git worktree remove trees/tree1` (or tree2)
   - Or keep both for reference and delete later

**IMPORTANT**: The entire process is fully automated. The user should NOT need to manually type or paste anything.

## Important Notes

### Prerequisites
- **Git repository** with worktree support (git 2.5+)
- **trees/ directory** will be created automatically if it doesn't exist
- **Warp Terminal** must be installed and running
- **Claude Code CLI** must be installed (`claude` command available)
- **Accessibility Permissions** must be granted:
  - Go to System Settings → Privacy & Security → Accessibility
  - Enable the terminal app running this script
- **pnpm** and **uv** must be installed for dependency management

### Worktree Structure
The skill creates worktrees automatically:
```bash
/path/to/project/
  ├── .git/              # Shared git directory (~66% disk space savings!)
  ├── trees/
  │   ├── tree1/         # Auto-created with branch tree1-<feature>
  │   └── tree2/         # Auto-created with branch tree2-<feature>
  └── [main worktree files]
```

No manual setup required - the skill handles everything!

### Customization
- Default parallel sessions: **2** (tree1 and tree2)
- Can be adjusted by modifying create.sh calls in spawn-variants.sh
- Timing delays can be adjusted for slower systems
- Port assignments: tree1 (3001/5001), tree2 (3002/5002)

### Best Practices
- Keep feature specifications clear and self-contained
- Each Claude instance works independently in its own worktree
- User should periodically check both Claude sessions (tabs 3 & 4)
- Test implementations in real-time at localhost:3001 and localhost:3002
- User decides which implementation to keep
- Remove unused worktrees when done: `git worktree remove trees/tree1`

## Example Usage

**User**: "I want to build a user authentication feature with JWT tokens and refresh token rotation. Let's do competitive prototyping."

**Claude Response**:
1. Creates a concise task description summarizing the auth feature requirements
2. Asks only if any critical details are missing (glaring clarifications)
3. Generates script that:
   - Cleans up existing tree1/tree2
   - Creates tree1 worktree with services (3001/5001)
   - Creates tree2 worktree with services (3002/5002)
   - Spawns 2 Claude Code sessions (tree1 and tree2)
4. Executes script - both sessions receive the task with plan mode instructions
5. Informs user that:
   - 4 Warp tabs are now open (2 services, 2 Claude sessions)
   - Both variants will run in plan mode
   - Both will read relevant code before asking questions
   - Both will think about and share their approach
   - Services are live for real-time testing
6. User monitors both tabs and tests at localhost:3001/3002

## Troubleshooting

### Common Issues and Solutions

**Worktree creation fails**:
- Check you're in a git repository: `git status`
- Ensure git version supports worktrees: `git --version` (need 2.5+)
- If tree1/tree2 directories exist but worktree command fails, run cleanup script manually

**Services not starting**:
- Check ports 3001/3002 and 5001/5002 are not already in use
- Verify pnpm is installed: `pnpm --version`
- Verify uv is installed: `uv --version`
- Check .env files exist and were copied correctly

**Sessions not opening**:
- Verify Warp is running
- Check accessibility permissions are granted (System Settings → Privacy & Security → Accessibility)

**Claude not starting**:
- Increase delay after pressing Return (from 4 to 5+ seconds in script)
- Test `claude` command in terminal manually
- Check Claude Code CLI is properly installed

**Too many tabs open**:
- This is expected! You should see 4 tabs:
  - 2 for services (tree1 and tree2)
  - 2 for Claude sessions (tree1 and tree2)

**Messages not sent to Claude sessions**:
- Increase delay after Claude starts (currently 4 seconds, try 5-6)
- Check clipboard is working: run `echo "test" | pbcopy && pbpaste`
- Verify AppleScript permissions are granted

**Plan mode not working**:
- Verify the task description ends with the exact plan mode instruction text
- Check the script template has the full instruction in the TASKEOF heredoc

**AppleScript escaping issues** (SHOULD NOT HAPPEN with v1.2):
- v1.2 uses clipboard approach which avoids ALL escaping issues
- If you're seeing escaping errors, verify you're using the updated spawn-variants.sh template
- The clipboard approach handles: newlines, quotes, backticks, markdown, special characters
- Never use direct `keystroke "text"` with embedded variables - always use clipboard!

**Task description has errors when displayed**:
- Check that you replaced `{{TASK_DESC}}` with actual content using Edit tool
- Verify no syntax errors in the heredoc (TASKEOF must not be indented)
- Keep task description concise (1-3 paragraphs max for readability)

**Both variants doing the same thing**:
- This can happen! Claude instances may converge on similar approaches
- Try running again - different timing can lead to different research paths
- Provide more open-ended task descriptions to encourage exploration

**Worktree already exists error**:
- Run cleanup script: `.claude/scripts/create-worktrees/cleanup.sh --auto tree1,tree2`
- Or manually remove: `git worktree remove trees/tree1 --force` (and tree2)
- The spawn-variants.sh script should handle this automatically

**Timing issues**:
- If commands execute too quickly: increase delay values
- If too slow: decrease delays (but keep Claude init at 4+ seconds)
- Slower systems may need longer delays

**Write tool errors when creating script**:
- Use Bash heredoc (`cat > file << EOF`) instead of Write tool for /tmp files
- Write tool requires reading file first, which doesn't work well for temp scripts
- The clipboard approach avoids this entirely

**Placeholder replacement errors / Script syntax errors**:
- CRITICAL: The template has TWO placeholders: `{{FEATURE_NAME}}` and `{{TASK_DESC}}`
- Replace `{{FEATURE_NAME}}` FIRST with sanitized feature name
- Replace `{{TASK_DESC}}` SECOND with full task description
- NEVER use `replace_all: true` - it will replace both placeholders with the same content!
- If worktrees fail to create, check line 37 has a valid feature name (not multi-line content)
