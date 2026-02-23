---
name: plugin-packager
description: Package any directory containing skills/, agents/, commands/ (or a subset) into a Claude Code plugin, optionally registering it in a marketplace
argument-hint: "[source-dir] [plugin-name] [--marketplace path/to/marketplace] [--only skills:a,b agents:x commands:y]"
---

# Plugin Packager

You are packaging Claude Code skills, agents, commands, hooks, and other assets from a source directory into a properly structured Claude Code plugin.

## Input

The user will provide:

1. **Source directory** (`$1`): Path to any directory that contains one or more of: `skills/`, `agents/`, `commands/`, `hooks/`, `scripts/`, `templates/` subdirectories. This could be a `.claude/` directory, a standalone folder, or any arbitrary path. At least one recognized component subdirectory must exist. Defaults to `.claude/` in the current project if not specified.

2. **Plugin name** (`$2`): The kebab-case name for the new plugin. This becomes the namespace for all commands (e.g., `/plugin-name:command`).

3. **Optional flags** (parsed from `$ARGUMENTS`):
   - `--marketplace <path>`: Path to an existing marketplace repo root (contains `.claude-plugin/marketplace.json`). If provided, register the new plugin in that marketplace's `marketplace.json`.
   - `--target <path>`: Where to create the plugin directory. Defaults to `./plugins/<plugin-name>` if a marketplace path is given, otherwise `./<plugin-name>` in the current directory.
   - `--only <filter>`: Cherry-pick specific components. Format: `skills:name1,name2 agents:name1,name2 commands:name1,name2`. If omitted, copy everything found.
   - `--description "<text>"`: Plugin description. If omitted, generate one from the contents.
   - `--version <semver>`: Plugin version. Defaults to `1.0.0`.
   - `--author "<name>"`: Author name for the manifest.

## Execution Steps

### Step 1: Validate source directory

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

List each component found with a count. If `--only` was provided, filter to just those named components. If the source directory doesn't exist or has no recognizable components, stop and tell the user.

### Step 2: Create plugin directory structure

Create the target directory with the correct plugin layout:

```bash
mkdir -p <target>/.claude-plugin
```

### Step 3: Move/copy components

For each component type found (respecting `--only` filter if provided):

- **agents/**: Copy `*.md` files to `<target>/agents/`
- **commands/**: Copy `*.md` files to `<target>/commands/`
- **skills/**: Copy entire skill directories (each containing `SKILL.md` plus any guidelines/, templates/, scripts/ subdirectories) to `<target>/skills/`
- **hooks/**: If `hooks.json` exists, copy to `<target>/hooks/hooks.json`. If hooks are in a settings file, extract the `hooks` object and write it to `<target>/hooks/hooks.json`.
- **scripts/**: Copy to `<target>/scripts/` and ensure shell scripts are executable (`chmod +x`)
- **templates/**: Copy to `<target>/templates/`
- **tests/**: Copy to `<target>/tests/`
- **.mcp.json**: Copy to `<target>/.mcp.json`

Use `cp -r` to preserve directory structure. If the user explicitly asks to migrate (move rather than copy), use `mv` instead of `cp`. Default to `cp` to be safe.

### Step 4: Create plugin.json manifest

Write `<target>/.claude-plugin/plugin.json`:

```json
{
  "name": "<plugin-name>",
  "description": "<description>",
  "version": "<version>",
  "author": {
    "name": "<author>"
  },
  "keywords": [<generated-from-contents>]
}
```

Generate keywords from the component names (e.g., skill names, agent names). Keep it to 5-8 relevant tags.

### Step 5: Register in marketplace (if --marketplace provided)

If a marketplace path was given:

1. Read `<marketplace>/.claude-plugin/marketplace.json`
2. Compute the relative source path from the marketplace root to the plugin directory (must start with `./`)
3. Add a new entry to the `plugins` array:

```json
{
  "name": "<plugin-name>",
  "source": "./<relative-path-to-plugin>",
  "description": "<description>",
  "version": "<version>",
  "category": "development",
  "tags": [<keywords>]
}
```

4. Write the updated `marketplace.json` back

If the marketplace.json does NOT exist yet but the user specified `--marketplace`, create the full marketplace structure:

```
<marketplace>/.claude-plugin/marketplace.json
```

With schema:
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

### Step 6: Verify and report

After all operations:

1. Run `find <target> -maxdepth 3 | sort` to show the created structure
2. Confirm `.claude-plugin/plugin.json` is valid JSON
3. If marketplace was updated, confirm `marketplace.json` is valid JSON
4. Print a summary:
   - Plugin name and path
   - Components packaged (with counts)
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
