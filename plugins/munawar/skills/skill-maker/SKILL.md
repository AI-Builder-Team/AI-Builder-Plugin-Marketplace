---
name: "m:skill-maker"
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

Each skill is a directory containing a `SKILL.md` file, and optionally helper scripts and reference docs:
```
~/.claude/skills/
├── my-skill/
│   └── SKILL.md
├── another-skill/
│   ├── SKILL.md
│   ├── scripts/          # Helper scripts live here
│   │   └── helper.py
│   └── reference.md      # Optional detailed docs
└── README.md
```

### Bundling Scripts with Skills

When a skill needs helper scripts (Python utilities, shell scripts, etc.), place them in a `scripts/` subdirectory alongside SKILL.md. This keeps the skill self-contained and portable.

**Structure:**
```
~/.claude/skills/my-skill/
├── SKILL.md
└── scripts/
    ├── fetch_data.py
    └── transform.sh
```

**Reference them in SKILL.md** with markdown links so Claude knows they exist and can Read them on demand:
```markdown
## Supporting Files
See [scripts/fetch_data.py](scripts/fetch_data.py) for the data fetcher.
```

Note on loading behavior — there are three tiers:
- **SKILL.md content**: fully injected into context on every invocation
- **Markdown-linked files**: Claude sees the link text but must explicitly `Read` the file — useful for large reference docs, API specs, or scripts that Claude may need to inspect
- **Unlisted files in the skill dir**: Claude won't know they exist unless it searches

So put essential instructions directly in SKILL.md. Use linked files for things Claude *might* need to reference but shouldn't pay the context cost for on every run.

**Execute bundled scripts in Bash commands** using the full path:
```bash
uv run --with some-package python ~/.claude/skills/my-skill/scripts/fetch_data.py "$URL"
```

This pattern is useful when your skill wraps a reusable utility — the script travels with the skill, and the SKILL.md stays lean and focused on orchestration instructions.

### Portable Paths for Plugin Skills

When a skill will be distributed as part of a plugin, use `${CLAUDE_PLUGIN_ROOT}` for all script and resource paths. Claude Code substitutes this with the plugin's actual install directory at runtime.

```bash
# Plugin-portable path:
python3 ${CLAUDE_PLUGIN_ROOT}/skills/my-skill/scripts/fetch_data.py "$URL"

# Personal skill path (non-portable):
python3 ~/.claude/skills/my-skill/scripts/fetch_data.py "$URL"
```

`${CLAUDE_PLUGIN_ROOT}` works in SKILL.md bash commands, hooks, MCP configs, and executed scripts. It is **not** a shell environment variable — it resolves only within Claude Code's plugin context.

### Plugin Skill Naming — Prefix Rules

When the target directory contains `plugins/` in its path, the skill is part of a bundled plugin. Apply these rules:

1. **Prefix the skill name with the plugin name** in the `name:` frontmatter field. Format: `<plugin-name>:<skill-name>`. The plugin name comes from the `name` field in the nearest `plugin.json` (at `.claude-plugin/plugin.json` relative to the plugin root).
   - Plugin `m` → `m:my-skill`
   - Plugin `klair-legacy` → `klair-legacy:my-skill`

2. **Detect the plugin name automatically**: Walk up from the skill directory to find `.claude-plugin/plugin.json` and read its `name` field. This is the authoritative prefix.

3. **Check existing sibling skills for consistency**: Look at other skills in the same plugin's `skills/` directory. Their `name:` frontmatter fields show the prefix convention already in use. Match it exactly.

4. **Use `${CLAUDE_PLUGIN_ROOT}`** for all script and resource paths (see Portable Paths above) — never hardcode `~/` paths in plugin skills.

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

**Limitation — no "rest of args" syntax:** `$N` always resolves to a single word. There is no built-in way to get "everything after the first argument" as one string. If your skill takes an ID plus a free-form instruction (e.g. `/audit abc123 show me all the errors`), use `$0` for the ID where you need it (like in a script call), and `$ARGUMENTS` where you need the full string. Claude will see both and naturally understand the structure from context — no parsing instructions needed.

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

**4. Skill with Bundled Scripts:**
```yaml
---
name: research-tool
description: Fetch and save web content for research
argument-hint: "[url] [topic-name]"
---

Fetch content from $0 and save it under the topic "$1".

## Supporting Files
See [scripts/fetch_content.py](scripts/fetch_content.py) for the content fetcher.

## Steps
1. Run the bundled script:
   ```bash
   uv run --with requests python ~/.claude/skills/research-tool/scripts/fetch_content.py "$0" "/tmp/research/$1"
   ```
2. Read the saved output and summarize key points
```

The script lives at `~/.claude/skills/research-tool/scripts/fetch_content.py` — self-contained, travels with the skill.

**5. Pure Command Skill (no AI invocation):**
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

**6. Routing Gate for Workflow Skills:**

When a skill has a stepwise workflow *and* reusable domain knowledge (scripts, schemas, conventions), add a routing section at the top of Instructions that lets the user bypass the default pipeline:

```yaml
---
name: my-workflow
description: Run a structured workflow or use its tools freely
---

# My Workflow Skill

## Supporting Files
See [scripts/tool.py](scripts/tool.py) for the utility script.

## Instructions

$ARGUMENTS

### Routing: read the user instruction first

- **Custom objective**: If the user's instruction requires a deviation
  from the default workflow (e.g. a different analysis, a one-off use
  of the bundled scripts), use whatever combination of the scripts and
  context below to achieve their objective. You are not bound to the
  workflow steps.

- **Default workflow** (when no instruction is provided, or when the
  user explicitly requests the standard workflow): Follow Steps 1–N
  below in sequence.

### Step 1: ...
```

Use this pattern when:
- The skill has a narrow multi-step workflow that would be too rigid for all use cases
- The skill bundles scripts, schemas, or domain knowledge that are independently useful
- Users might invoke the skill to leverage its context without wanting the full pipeline

### Best Practices

1. **Use clear, specific names** - short, memorable, easy to type
2. **Provide argument-hint** - Help users understand what to pass
3. **Use fork context for research** - Keeps main context clean
4. **Whitelist tools** - Use `allowed-tools` for safety
5. **Document in skill content** - Explain what the skill does
6. **Use arguments for flexibility** - Make skills reusable
7. **Test with various inputs** - Ensure argument handling works
8. **Bundle helper scripts in `scripts/`** - Keep skills self-contained; reference via markdown links in SKILL.md
9. **Consider a routing gate for workflow skills** - If your skill has a stepwise workflow, consider adding a routing section at the top of Instructions that lets the user's custom objective bypass the default steps while still leveraging the skill's knowledge and scripts. This makes the skill useful for a wider range of tasks without losing its default behavior (see Common Patterns #6)

### Editing Skill Files

Never edit files under `~/.claude/plugins/cache/` — that's a read-only installed copy.

To find the editable source, check these locations in order:

1. **Current project** — if it's a plugin marketplace repo (has `.claude-plugin/marketplace.json`), the skill source lives under `plugins/` here. Map from the cache path: `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<skill>/` → `<cwd>/plugins/<author>/skills/<skill>/`.
2. **Home directory skills** — `~/.claude/skills/` for personal skills.
3. **Project-local skills** — `.claude/skills/` in whatever project you're working in.
4. **Ask the user** — if you can't find the source in any of those places, ask where it lives.

#### After editing a skill in a marketplace plugin — version bump and push

When you edit an existing skill inside a marketplace plugin repo, follow these steps after the edit:

1. **Bump the plugin version** in both `plugin.json` and the corresponding `marketplace.json` entry:
   - **Patch bump** for edits to existing components (e.g. `4.3.0` → `4.3.1`)
   - **Minor bump** for adding a new skill, agent, or command (e.g. `4.3.0` → `4.4.0`)
   - **Major bump** only for breaking changes, large-scale restructuring, or significant new capabilities that change the plugin's scope (e.g. `4.3.0` → `5.0.0`)

2. **Push changes** — run `/m:push` from the repo root to commit and push.

### Testing Your Skill

After creating a skill, suggest the user run it on a real-world use case, then use `/m:session-audit` on the invocation session to identify issues and iterate on the skill's prompt.

---

## Your Task

**Routing:** If the user's request is something other than creating a new skill (e.g. editing an existing skill, reviewing one, adding a section, refactoring) — use the reference knowledge above to achieve their objective directly. Skip the creation steps below.

**User request:** $ARGUMENTS

**Default — create a new skill:**

1. **Determine skill purpose** - What should it do?
2. **Choose skill name** - Follow convention (lowercase, hyphens, prefix `m-` if custom)
3. **Design frontmatter** - Set appropriate fields
4. **Write skill prompt** - Clear instructions for Claude
   - If the skill has a multi-step workflow, consider whether a routing gate (see Common Patterns #6) would make it more flexible
5. **Add argument handling** - Use `$ARGUMENTS` or positional vars if needed
6. **Determine placement** - Figure out whether this repo is a skills/plugin container or a real project. Check these signals:
   - The repo/directory name or CWD path contains "plugin", "skills", or "marketplace"
   - A `plugin.json` exists somewhere in the repo
   - The repo has a `skills/` directory with existing skill folders in it

   **If this looks like a skills/plugin repo:** Create the skill here. Find the nearest `skills/` directory relative to CWD and create inside it. If the CWD is at the repo root and there are multiple plugin directories (each with their own `skills/`), ask the user which one. If a `plugin.json` exists, read it for the plugin name and apply plugin naming rules (prefix, `${CLAUDE_PLUGIN_ROOT}` paths).

   **If the user explicitly says "home", "personal", or "global":** Create at `~/.claude/skills/[skill-name]/SKILL.md`.

   **If the user explicitly says "project" or "project skill":** Create at `<project-root>/.claude/skills/[skill-name]/SKILL.md`.

   **Otherwise (regular project repo, no plugin signals):** Default to `~/.claude/skills/[skill-name]/SKILL.md`.

7. **Bundle any helper scripts** - If the skill needs utilities (Python scripts, shell scripts), put them in `[skill-name]/scripts/` and reference via markdown links in SKILL.md. Use `${CLAUDE_PLUGIN_ROOT}` for paths if the skill is in a plugin, or `~/.claude/skills/` for personal skills.
8. **Provide usage example** - Show how to invoke it

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
