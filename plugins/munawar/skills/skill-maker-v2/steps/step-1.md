# Step 1: Claude Code Skills — Complete Reference

Load this reference before creating or editing any skill.

## Folder Structure

Skills live in one of two locations:
- **Global skills**: `~/.claude/skills/` — Available in all projects
- **Project skills**: `<project>/.claude/skills/` — Project-specific

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

## Bundling Scripts with Skills

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

**Execute bundled scripts in SKILL.md** using relative paths from the skill directory:
```bash
python3 scripts/fetch_data.py "$URL"
uv run --with some-package python scripts/fetch_data.py "$URL"
```

The agent resolves relative paths from the skill directory root automatically — no absolute paths needed. This works for both personal skills and plugin skills, making scripts portable by default.

## Portable Paths for Plugin Skills

For scripts and resources referenced in **hooks, MCP configs, or executed scripts** (not SKILL.md), use `${CLAUDE_PLUGIN_ROOT}` — Claude Code substitutes this with the plugin's actual install directory at runtime.

```bash
# In SKILL.md — use relative paths (preferred, works everywhere):
python3 scripts/fetch_data.py "$URL"

# In hooks/MCP configs/executed scripts — use the plugin root token:
python3 ${CLAUDE_PLUGIN_ROOT}/skills/my-skill/scripts/fetch_data.py "$URL"
```

`${CLAUDE_PLUGIN_ROOT}` works in hooks, MCP configs, and executed scripts. It is **not** a shell environment variable — it resolves only within Claude Code's plugin context. Inside SKILL.md, prefer relative paths instead.

## Plugin Skill Naming — Prefix Rules

When the target directory contains `plugins/` in its path, the skill is part of a bundled plugin. Apply these rules:

1. **Prefix the skill name with the plugin name** in the `name:` frontmatter field. Format: `<plugin-name>:<skill-name>`. The plugin name comes from the `name` field in the nearest `plugin.json` (at `.claude-plugin/plugin.json` relative to the plugin root).
   - Plugin `m` → `m:my-skill`
   - Plugin `klair-legacy` → `klair-legacy:my-skill`

2. **Detect the plugin name automatically**: Walk up from the skill directory to find `.claude-plugin/plugin.json` and read its `name` field. This is the authoritative prefix.

3. **Check existing sibling skills for consistency**: Look at other skills in the same plugin's `skills/` directory. Their `name:` frontmatter fields show the prefix convention already in use. Match it exactly.

4. **Use `${CLAUDE_PLUGIN_ROOT}`** for all script and resource paths (see Portable Paths above) — never hardcode `~/` paths in plugin skills.

## SKILL.md Format

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
- Context from commands: !`git status`
- Arguments from user: $ARGUMENTS or $0, $1, $2...
```

## Frontmatter Fields

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

## Arguments System

`$ARGUMENTS` inserts all args as a single string; `$0`, `$1`, `$N` insert positional args (0-indexed). These are text-substituted into the prompt before Claude sees it. Use `argument-hint` in frontmatter to show users what to pass.

See [../reference/passing-arguments.md](../reference/passing-arguments.md) for full details, examples, and limitations.

## Dynamic Context with Commands

Execute shell commands when the skill is invoked using `!` immediately followed by a backtick-wrapped command (no space between them). The command output replaces the placeholder **before Claude sees the prompt**. This is how you inject runtime context (current branch, repo, etc.) into a skill.

```yaml
---
name: pr-context
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Current PR Context
- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Diff summary: !`gh pr diff --name-only`
- PR comments: !`gh pr view --comments`

## Task
$ARGUMENTS
```

## Environment Variables Available

Claude Code provides these variables in skill context:
- `$CLAUDE_SESSION_ID` — Current session ID
- `$CLAUDE_PROJECT_ROOT` — Project root directory
- Other standard env vars from shell

## Common Patterns

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
3. Document findings
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
   uv run --with requests python scripts/fetch_content.py "$0" "/tmp/research/$1"
   ```
2. Read the saved output and summarize key points
```

**5. Pure Command Skill (no AI invocation):**
```yaml
---
name: quick-status
description: Show git and project status
disable-model-invocation: true
---

!`git status`
!`git log -5 --oneline`
!`git branch -v`
```

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
  from the default workflow, use whatever combination of the scripts and
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

**7. Lazy-Loaded Steps Pattern:**

When a skill has a long multi-step workflow, keep the SKILL.md lean by putting detailed instructions in a `steps/` directory. The outer SKILL.md lists only step summaries with markdown links:

```yaml
---
name: my-workflow
description: Multi-step workflow with lazy-loaded instructions
---

# My Workflow

## Steps

### Step 1: Gather Context
**What**: Collect project info and user requirements.
**File**: [steps/step-1.md](steps/step-1.md)

### Step 2: Execute
**What**: Run the main transformation.
**File**: [steps/step-2.md](steps/step-2.md)

### Step 3: Validate
**What**: Check results and report findings.
**File**: [steps/step-3.md](steps/step-3.md)

## Execution
Read each step file only when you reach that step. Do not pre-load all steps.
```

Use this pattern when:
- The full workflow instructions exceed ~200 lines
- Steps are independent enough that earlier steps don't need to reference later ones
- You want to minimize initial context cost while keeping the full workflow available

## Best Practices

1. **Use clear, specific names** — short, memorable, easy to type
2. **Provide argument-hint** — Help users understand what to pass
3. **Use fork context for research** — Keeps main context clean
4. **Whitelist tools** — Use `allowed-tools` for safety
5. **Document in skill content** — Explain what the skill does
6. **Use arguments for flexibility** — Make skills reusable
7. **Test with various inputs** — Ensure argument handling works
8. **Bundle helper scripts in `scripts/`** — Keep skills self-contained; reference via markdown links in SKILL.md
9. **Consider a routing gate for workflow skills** — If your skill has a stepwise workflow, consider adding a routing section that lets the user's custom objective bypass the default steps while still leveraging the skill's knowledge and scripts
10. **Use lazy-loaded steps for long workflows** — Keep SKILL.md under 200 lines by putting detailed step instructions in linked files

## Editing Skill Files

Never edit files under `~/.claude/plugins/cache/` — that's a read-only installed copy.

To find the editable source, first figure out what kind of repo you're in. If the CWD path or directory name contains "plugin", "skills", or "marketplace", or there's a `skills/` directory with skill folders in it, you're likely in a plugin or skills repo — search `plugins/*/skills/*/SKILL.md` and `skills/*/SKILL.md` relative to the repo root. If not found, check these fallbacks:

1. **Home skills** — `~/.claude/skills/<skill-name>/SKILL.md`
2. **Project-local skills** — `<project-root>/.claude/skills/<skill-name>/SKILL.md`
3. **Ask the user** — If not found at the above places, ask the user where it lives.

### After editing a skill in a marketplace plugin — version bump and push

When you edit an existing skill inside a marketplace plugin repo, follow these steps after the edit:

1. **Bump the plugin version** in both `plugin.json` and the corresponding `marketplace.json` entry:
   - **Patch bump** for edits to existing components (e.g. `4.3.0` → `4.3.1`)
   - **Minor bump** for adding a new skill, agent, or command (e.g. `4.3.0` → `4.4.0`)
   - **Major bump** only for breaking changes or significant new capabilities

2. **Push changes** — run `/m:push` from the repo root to commit and push.

## Testing Your Skill

After creating a skill, suggest the user run it on a real-world use case, then use `/m:session-audit` on the invocation session to identify issues and iterate on the skill's prompt.
