# Step 2: Create the Skill

You've reached this step because the user wants to create a new skill. Follow the workflow below.

### 2.1 Determine Skill Purpose

What should the skill do? Clarify from the user's request. Ask clarifying questions only if the request is genuinely ambiguous.

### 2.2 Choose Skill Name

Follow convention: lowercase, hyphens, prefix per plugin naming rules if in a plugin repo. Short, memorable, easy to type.

### 2.3 Design Frontmatter

Set appropriate fields based on the skill's needs:
- `name` and `description` (required)
- `argument-hint` if it takes arguments
- `context: fork` if it should run in isolated context
- `agent` if it needs a specific agent type
- `allowed-tools` for safety whitelisting
- `model` to pin to haiku/sonnet/opus if needed
- `disable-model-invocation: true` for pure command skills

### 2.4 Write the Skill Prompt

Clear instructions for Claude. Consider:
- If the skill has a multi-step workflow, should it use a routing gate? (See Common Patterns #6 in Step 1)
- If the workflow is long (>200 lines of instructions), should it use lazy-loaded steps? (See Common Patterns #7 in Step 1)

### 2.5 Add Argument Handling

Use `$ARGUMENTS` for the full argument string, or `$0`, `$1`, `$N` for positional args. Set `argument-hint` in frontmatter to show users what to pass.

### 2.6 Determine Placement

Figure out whether this repo is a skills/plugin container or a real project:

**Signals of a skills/plugin repo:**
- The repo/directory name or CWD path contains "plugin", "skills", or "marketplace"
- A `plugin.json` exists somewhere in the repo
- The repo has a `skills/` directory with existing skill folders in it

**If this looks like a skills/plugin repo:** Create the skill here. Find the nearest `skills/` directory relative to CWD and create inside it. If the CWD is at the repo root and there are multiple plugin directories (each with their own `skills/`), ask the user which one. If a `plugin.json` exists, read it for the plugin name and apply plugin naming rules (prefix, `${CLAUDE_PLUGIN_ROOT}` paths).

**If the user explicitly says "home", "personal", or "global":** Create at `~/.claude/skills/[skill-name]/SKILL.md`.

**If the user explicitly says "project" or "project skill":** Create at `<project-root>/.claude/skills/[skill-name]/SKILL.md`.

**Otherwise (regular project repo, no plugin signals):** Default to `~/.claude/skills/[skill-name]/SKILL.md`.

### 2.7 Bundle Helper Scripts

If the skill needs utilities (Python scripts, shell scripts), put them in `[skill-name]/scripts/` and reference via markdown links in SKILL.md. Use relative paths (e.g. `scripts/fetch.py`) — the agent resolves them from the skill directory automatically.

### 2.8 Provide Usage Example

Show the user how to invoke the skill with example arguments.
