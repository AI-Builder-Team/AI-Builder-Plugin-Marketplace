---
name: skill-maker
description: Create new Claude Code skills with proper structure and documentation
argument-hint: "[skill-name-or-description]"
disable-model-invocation: false
model: opus
---

# Skill Maker - Create Claude Code Skills

You are an expert at creating Claude Code skills. Your task is to create a new skill based on the user's request: **$ARGUMENTS**

## Claude Code Skills - Complete Reference

### Folder Structure

Skills live in one of two locations:
- **Global skills**: `~/.claude/skills/` - Available in all projects
- **Project skills**: `<project>/.claude/skills/` - Project-specific

Each skill is a directory containing a `SKILL.md` file:
```
~/.claude/skills/
├── my-skill/
│   └── SKILL.md
├── another-skill/
│   └── SKILL.md
└── README.md
```

### SKILL.md Format

Every skill needs a `SKILL.md` with frontmatter and content:

```yaml
---
name: skill-name
description: Short description for autocomplete
argument-hint: "[optional-arg-hints]"
disable-model-invocation: false
context: fork|default
agent: general-purpose|Explore|Bash
allowed-tools: Bash(*), Read(*), Edit(*)
---

# Skill Content

This is the prompt that Claude receives when the skill is invoked.
You can include:
- Instructions
- Examples
- Context from commands: ! `git status`
- Arguments from user: $ARGUMENTS or $0, $1, $2...
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill identifier, used as `/name` |
| `description` | Yes | Shows in autocomplete |
| `argument-hint` | No | Help text for arguments, e.g., `"[file-path] [new-name]"` |
| `disable-model-invocation` | No | If true, skill only runs commands but doesn't send prompt to Claude |
| `model` | No | Pin to a specific model: `haiku`, `sonnet`, or `opus`. Overrides the currently selected model for this skill — use `haiku` for lightweight/fast tasks, `opus` for deep reasoning. |
| `context` | No | `fork` creates isolated context, `default` shares main context |
| `agent` | No | Specify agent type: `Explore`, `Bash`, `general-purpose`, etc. |
| `allowed-tools` | No | Whitelist tools for safety, e.g., `Bash(gh *, git *)` |

### Arguments System

**Passing arguments:**
```bash
/skill-name arg1 arg2 arg3
```

**Accessing in SKILL.md:**
- `$ARGUMENTS` - All arguments as single string
- `$ARGUMENTS[0]` or `$0` - First argument
- `$ARGUMENTS[1]` or `$1` - Second argument
- `$ARGUMENTS[N]` or `$N` - Nth argument (0-indexed)

**Key:** `$ARGUMENTS` is **text substitution**, not a shell variable. Claude Code replaces it with the literal argument text in the markdown *before* Claude sees the prompt. So just write `$ARGUMENTS` directly in your skill content — no `echo`, no backticks needed. If `$ARGUMENTS` is not referenced anywhere in the SKILL.md, Claude Code auto-appends `ARGUMENTS: <value>` at the end.

**Example:**
```yaml
---
name: migrate-component
argument-hint: "[component] [from-framework] [to-framework]"
---

Migrate the $0 component from $1 to $2.

Steps:
1. Read the component at: $0
2. Analyze $1 patterns
3. Convert to $2 syntax
4. Preserve all behavior and tests
```

Running `/migrate-component SearchBar React Vue` gives:
- `$0` = SearchBar
- `$1` = React
- `$2` = Vue

### Dynamic Context with Commands

Execute shell commands when the skill is invoked using "!" immediately followed by a backtick-wrapped command (no space between them). The command output replaces the placeholder **before Claude sees the prompt**. This is how you inject runtime context (current branch, repo, etc.) into a skill.

Syntax: "!" immediately followed by a backtick-wrapped command, with no space between them in your actual skill file.

> **Meta note:** The examples below use a space between "!" and the backtick to prevent execution inside THIS skill. When writing your skill file, remove the space.

```yaml
---
name: pr-context
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Current PR Context
- Branch: ! `git branch --show-current`
- Status: ! `git status --short`
- Diff summary: ! `gh pr diff --name-only`
- PR comments: ! `gh pr view --comments`

## Task
$ARGUMENTS
```

^ In the actual skill file, "!" must be directly touching the backtick with no space.

### Environment Variables Available

Claude Code provides these variables in skill context:
- `$CLAUDE_SESSION_ID` - Current session ID
- `$CLAUDE_PROJECT_ROOT` - Project root directory
- Other standard env vars from shell

### Common Patterns

**1. Investigation/Research Skill:**
```yaml
---
name: investigate
description: Deep dive into codebase feature
context: fork
agent: Explore
---

Investigate: $ARGUMENTS

Approach:
1. Search for related files and code
2. Read key implementations
3. Document findings in docs/YYYY-MM-DD_HHMMhrs_$0.md
4. Provide summary
```

**2. Git/GitHub Skill:**
```yaml
---
name: pr-ready
description: Prepare branch for PR
allowed-tools: Bash(git *, gh *)
---

Prepare branch for PR: $ARGUMENTS

Steps:
1. Check git status
2. Run linting/type checks
3. Review uncommitted changes
4. Create branch following convention: NNN-description
5. Stage and commit with proper message
```

**3. Code Generation Skill:**
```yaml
---
name: gen-component
description: Generate React component with tests
argument-hint: "[component-name] [component-type]"
---

Generate a $1 component named $0.

Requirements:
- TypeScript
- Props interface
- Unit tests with RTL
- Storybook story
- Documentation comments
```

**4. Pure Command Skill (no AI invocation):**
```yaml
---
name: quick-status
description: Show git and project status
disable-model-invocation: true
---

! `git status`
! `git log -5 --oneline`
! `git branch -v`
```

^ In the actual skill file, remove the space between "!" and the backtick.

### Best Practices

1. **Use clear, specific names** - Prefix with `m-` for meta/custom skills
2. **Provide argument-hint** - Help users understand what to pass
3. **Use fork context for research** - Keeps main context clean
4. **Whitelist tools** - Use `allowed-tools` for safety
5. **Document in skill content** - Explain what the skill does
6. **Use arguments for flexibility** - Make skills reusable
7. **Test with various inputs** - Ensure argument handling works

### Testing Your Skill

After creating a skill:
1. Restart Claude Code or run `/reload-skills` (if available)
2. Test with `/skill-name --help` or similar
3. Try various argument combinations
4. Check output and behavior
5. Iterate on prompt clarity

---

## Your Task

Now, based on the request "$ARGUMENTS", create a new skill:

1. **Determine skill purpose** - What should it do?
2. **Choose skill name** - Follow convention (lowercase, hyphens, prefix `m-` if custom)
3. **Design frontmatter** - Set appropriate fields
4. **Write skill prompt** - Clear instructions for Claude
5. **Add argument handling** - Use `$ARGUMENTS` or positional vars if needed
6. **Create the skill** - Write to `~/.claude/skills/[skill-name]/SKILL.md`
7. **Provide usage example** - Show how to invoke it

Ask clarifying questions if the request is ambiguous. Otherwise, proceed to create the skill.

---

## Post-Creation Validation

After creating the skill, run this validation workflow:

8. **Ask the user to test the skill** - Tell them to invoke the newly created skill (e.g., `/skill-name test-arg`) in their current session or a new one, then come back and confirm it ran.

9. **Trace the invocation session** - Once the user confirms they ran it, **ask the user for the session ID** where they invoked it. This is critical because:
   - The skill may have been invoked in a **long-running, reused session** — not a recently-created one
   - Skills with `context: default` (no fork) run inside the existing session, so there's no new JSONL file to find
   - The most-recently-modified JSONL is often the *current* audit session, not the invocation session
   - Searching by recency (`ls -lt`) is unreliable — a 3-hour-old session that was reused won't be at the top

   **How to get the session ID:** Tell the user to check their Claude Code status bar or run `/status` in the session where they invoked the skill. The session ID is a UUID like `01300e01-8a6c-4353-9c4d-02e5b67bd4b2`.

   Once you have the session ID, construct the path:
   ```bash
   # The JSONL lives in the project-specific directory under ~/.claude/projects/
   # Try both potential project path casings (macOS paths can vary)
   SESSION_ID="<paste-session-id-here>"
   PROJECT_DIR=$(pwd | tr '/' '-' | sed 's/^-//')
   ls -la ~/.claude/projects/${PROJECT_DIR}/${SESSION_ID}.jsonl

   # If skill used context:fork or agent, also check for subagent sessions
   # (they'll be separate JSONL files modified around the same time)
   ```

   **Fallback if user can't provide session ID:** Search all JSONL files for the skill's `<command-name>` tag:
   ```bash
   grep -l "command-name.*skill-name-here" ~/.claude/projects/${PROJECT_DIR}/*.jsonl
   ```
   Then among matches, exclude the current session (you know your own session ID from `$CLAUDE_SESSION_ID`) and pick the one with the most recent modification time.

10. **Audit the session JSONL for issues** - Read the identified session file(s) and check for ALL of the following:

    **a) Errors:**
    - Grep for `"error"`, `"Error"`, `"failed"`, `"exception"` in the JSONL
    - Check for tool calls that returned error results
    - Look for HTTP/API errors in tool outputs

    **b) Failed attempts / retries:**
    - Look for the same tool being called multiple times with slightly different parameters (indicates the agent had to retry)
    - Check for sequences where a Bash command fails then gets re-run with corrections
    - Count total tool calls vs unique tool calls — a high ratio suggests thrashing

    **c) Agent self-correction:**
    - Look for assistant messages containing phrases like "let me try", "that didn't work", "instead", "actually" — signs the agent had to course-correct mid-execution
    - Check if the agent read files it shouldn't have needed to (indicates confusion about what context it had)

    **d) Skill firing / context injection issues:**
    - **If the skill uses "!" backtick commands**: verify the command output appears as literal text in the first assistant message's context (not as a command to be run). If the agent is *running* the command itself via Bash tool, the "!" backtick preprocessing failed.
    - **If the skill uses `$ARGUMENTS`**: verify the arguments were substituted as literal text, not left as `$ARGUMENTS` or `$0` etc.
    - **If the skill uses `context: fork`**: verify a separate subagent JSONL was created (the skill should NOT have run in the main session)
    - **If the skill uses `agent: Explore` or similar**: verify the session used that agent type
    - **If the skill uses `allowed-tools`**: verify no tool calls outside the whitelist were attempted

    **e) Overall health signals:**
    - Total turn count — if a simple skill took >10 turns, something is off
    - Check that the skill's described purpose was actually achieved in the output
    - Look for the agent asking the user clarifying questions (suggests the skill prompt was ambiguous)

11. **Report findings** - Summarize:
    - Whether the skill fired correctly (context injected, args substituted)
    - Any errors or retries found
    - Whether the skill achieved its purpose in a reasonable number of turns
    - Specific fixes to apply to the SKILL.md if issues were found

12. **Fix and re-test** - If issues were found, update the SKILL.md and ask the user to test again.
