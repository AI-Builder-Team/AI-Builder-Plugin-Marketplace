---
name: "m:plugin-packager"
description: Package skills, agents, commands into a Claude Code plugin from natural language instructions
argument-hint: "<describe what you want to package in plain English>"
---

# Plugin Packager

You are packaging Claude Code skills, agents, commands, hooks, and other assets from a source directory into a properly structured Claude Code plugin.

## User Request

The user said:

> $ARGUMENTS

## Step 0: Understand the request

Parse the user's natural language request to extract:

- **Source directory**: Where the components live. Could be a `.claude/` directory, a standalone folder, or any path. If not mentioned, default to `.claude/` in the current project.
- **Plugin name**: The kebab-case name for the plugin (becomes the namespace, e.g., `/plugin-name:command`). If not mentioned, infer from the source directory name or the dominant component names.
- **Target directory**: Where to create the plugin. If not mentioned, default to `./plugins/<plugin-name>` if a marketplace is involved, otherwise `./<plugin-name>`.
- **Marketplace**: Whether to register in a marketplace, and if so, its path. Look for mentions of "marketplace", "register", "add to marketplace", etc.
- **Component filter**: Whether the user wants all components or only specific ones. Look for mentions like "just the skills", "only the agents named X and Y", "skip hooks", etc. If not mentioned, include everything found.
- **Description**: Any description for the plugin. If not mentioned, generate one from the contents.
- **Version**: Auto-detected from existing plugin (see Step 1.5). Only override if the user specifies an explicit version.
- **Author**: If mentioned, use it. Otherwise leave as the user's name or omit.
- **Copy vs Move**: Default to copy. Only move if the user explicitly says "move" or "migrate".

If something critical is ambiguous (e.g., the source directory could be multiple things), ask the user to clarify before proceeding. Do NOT guess when the answer matters.

## Step 1: Validate source directory

Read the source directory and catalog what exists:

```
source/
├── agents/*.md
├── commands/*.md
├── skills/*/SKILL.md
├── hooks/ (hooks.json or individual configs)
├── scripts/
├── templates/
├── tests/
└── .mcp.json (if present)
```

List each component found with a count. If a component filter was specified, apply it. If the source directory doesn't exist or has no recognizable components, stop and tell the user.

## Step 1.5: Detect existing plugin and auto-version

Check if `<target>/.claude-plugin/plugin.json` already exists.

**If it does NOT exist** (fresh package): set version to `1.0.0`.

**If it DOES exist** (update): read it and extract the current version, then determine what changed:

1. **Catalog the source** (from Step 1) — build a set of source component names:
   - Skill names = directory names under `source/skills/`
   - Agent names = filenames (without `.md`) under `source/agents/`
   - Command names = filenames (without `.md`) under `source/commands/`

2. **Catalog the existing target** — build the same set from the current plugin:
   - Skill names = directory names under `<target>/skills/`
   - Agent names = filenames (without `.md`) under `<target>/agents/`
   - Command names = filenames (without `.md`) under `<target>/commands/`

3. **Diff the two sets**:
   - `added` = names in source but NOT in target (new components)
   - `updated` = names in BOTH source and target (existing components being overwritten)
   - `removed` = names in target but NOT in source (only relevant if user asked to remove stale components)

4. **Discover naming conventions** (for `updated` components):

   Source and target may use different naming patterns. The plugin's names are the canonical ones — source names must be mapped to match them during the copy.

   For each `updated` component, compare the source name to the target name and detect any systematic transform:

   - **Prefix stripping**: source has `m-bugfix.md` → target has `bugfix.md` (prefix `m-` was stripped)
   - **Prefix adding**: source has `bugfix.md` → target has `m-bugfix.md` (prefix `m-` was added)
   - **Prefix swapping**: source has `m-bugfix.md` → target has `munawar-bugfix.md` (prefix changed)
   - **No change**: names match exactly

   How to detect:
   a. For each matched pair in `updated`, check if the source name and target name differ only by a prefix (everything before the first `-` or `_`).
   b. If a consistent prefix transform applies to **all or most** matched pairs, record it as the naming convention.
   c. Print the discovered convention:
      ```
      Naming convention detected:
        Source prefix: "m-" → Target prefix: "" (stripped)
        Applies to: 8/8 matched components
      ```
   d. For `added` components (new ones), apply the same transform so they follow the plugin's existing pattern. For example, if source has `m-new-skill` and the convention strips `m-`, the target name becomes `new-skill`.
   e. If no consistent pattern is found (mixed naming), print a warning and keep source names as-is.

5. **Decide the bump**:
   - If `added` is non-empty (new skills, agents, or commands were introduced) → **MAJOR bump** (e.g. `1.2.0` → `2.0.0`)
   - If `added` is empty but `updated` is non-empty (only existing components changed) → **MINOR bump** (e.g. `1.2.0` → `1.3.0`)
   - If nothing changed at all → warn the user that source and target appear identical, ask whether to proceed

5. **Print the version decision** before proceeding:
   ```
   Existing plugin version: 1.2.0
   New components: skill/foo, agent/bar  (or "none")
   Updated components: skill/baz, agent/qux  (or "none")
   Version bump: MAJOR → 2.0.0  (or MINOR → 1.3.0)
   ```

If the user specified an explicit version, skip this logic and use their version.

## Step 2: Create plugin directory structure

Create the target directory with the correct plugin layout:

```bash
mkdir -p <target>/.claude-plugin
```

## Step 3: Copy/move components

**IMPORTANT**: If Step 1.5 discovered a naming convention, apply it during the copy. Rename files/directories from source names to their target-convention names. For example, if the convention strips prefix `m-`, then `source/agents/m-bugfix.md` copies to `<target>/agents/bugfix.md`, and `source/skills/m-locator/` copies to `<target>/skills/locator/`.

For each component type found (respecting any filter):

- **agents/**: Copy `*.md` files to `<target>/agents/` (applying name transform)
- **commands/**: Copy `*.md` files to `<target>/commands/` (applying name transform)
- **skills/**: Copy entire skill directories (each containing `SKILL.md` plus any guidelines/, templates/, scripts/ subdirectories) to `<target>/skills/` (applying name transform to the directory name)
- **hooks/**: If `hooks.json` exists, copy to `<target>/hooks/hooks.json`. If hooks are in a settings file, extract the `hooks` object and write it to `<target>/hooks/hooks.json`.
- **scripts/**: Copy to `<target>/scripts/` and ensure shell scripts are executable (`chmod +x`)
- **templates/**: Copy to `<target>/templates/`
- **tests/**: Copy to `<target>/tests/`
- **.mcp.json**: Copy to `<target>/.mcp.json`

Use `cp -r` to preserve directory structure. Only use `mv` if the user explicitly asked to move/migrate.

## Step 4: Create plugin.json manifest

Write `<target>/.claude-plugin/plugin.json` using the version computed in Step 1.5:

```json
{
  "name": "<plugin-name>",
  "description": "<description>",
  "version": "<version-from-step-1.5>",
  "author": {
    "name": "<author>"
  },
  "keywords": [<generated-from-contents>]
}
```

Generate keywords from the component names (e.g., skill names, agent names). Keep it to 5-8 relevant tags.

## Step 5: Register in marketplace (if requested)

If the user wants marketplace registration:

1. Read `<marketplace>/.claude-plugin/marketplace.json`
2. Compute the relative source path from the marketplace root to the plugin directory (must start with `./`)
3. Search the `plugins` array for an existing entry with the same `"name"`:

   **If the plugin already exists** in the array: update the existing entry's `version`, `description`, and `tags` fields to match the new values. Do NOT add a duplicate entry.

   **If the plugin does NOT exist** in the array: add a new entry:

```json
{
  "name": "<plugin-name>",
  "source": "./<relative-path-to-plugin>",
  "description": "<description>",
  "version": "<version-from-step-1.5>",
  "category": "development",
  "tags": [<keywords>]
}
```

4. Write the updated `marketplace.json` back. The version in the marketplace entry MUST match the version in `plugin.json` — both come from Step 1.5.

If the marketplace.json does NOT exist yet but the user wants marketplace registration, create the full marketplace structure:

```json
{
  "name": "<derive-from-directory-name>",
  "owner": {
    "name": "<author or 'Team'>"
  },
  "metadata": {
    "description": "<marketplace description>",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    { <the new plugin entry> }
  ]
}
```

## Step 6: Verify and report

After all operations:

1. Run `find <target> -maxdepth 3 | sort` to show the created structure
2. Confirm `.claude-plugin/plugin.json` is valid JSON
3. If marketplace was updated, confirm `marketplace.json` is valid JSON
4. Print a summary:
   - Plugin name and path
   - Version (and whether it was a fresh `1.0.0`, MAJOR bump, or MINOR bump)
   - Components packaged (with counts), highlighting new vs updated
   - Whether marketplace was updated
   - How to test: `claude --plugin-dir <target>`
   - How to install (if marketplace): `/plugin marketplace add <marketplace-path>` then `/plugin install <name>@<marketplace-name>`

## Important Rules

- **Only `plugin.json` goes inside `.claude-plugin/`**. All component directories (agents/, commands/, skills/, hooks/) must be at the plugin root level.
- **Skills must have `SKILL.md`** (exact filename) inside a named subdirectory.
- **Commands are flat `.md` files** in the commands/ directory.
- **Agents are flat `.md` files** in the agents/ directory.
- **Hooks go in `hooks/hooks.json`**, not inside `.claude-plugin/`.
- **All paths in hooks/MCP configs should use `${CLAUDE_PLUGIN_ROOT}`** for portability. If you find hardcoded absolute paths in hook commands or MCP server configs during the copy, replace them with `${CLAUDE_PLUGIN_ROOT}/...` relative equivalents.
- **Preserve file permissions** on scripts.
- Default to `cp` (copy). Only use `mv` (migrate) if the user explicitly asks to move/migrate. If moving, remove the source directory afterward only if fully emptied.
- If the source directory also contains `settings.json`, `settings.local.json`, or `CLAUDE.md`, do NOT copy/move those -- they are project config, not plugin components. Leave them in place.
