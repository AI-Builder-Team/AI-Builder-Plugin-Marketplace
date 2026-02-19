# Claude Code Plugin Marketplace

## Quick Start

### 1. Add the marketplace

In Claude Code, run:

```
/plugin marketplace add https://github.com/AI-Builder-Team/claude-code-plugin-marketplace
```

### 2. Install a plugin

```
/plugin install m@klair-marketplace
```

Skills are now available as `/m:gtr`, `/m:push`, `/m:pr-reader`, etc.

## Package your own stuff

Have skills, agents, or commands in `~/.claude/` you want to package? Use the plugin packager:

```
/m:plugin-packager ~/.claude my-tools --marketplace /path/to/this/repo
```

Cherry-pick specific components with `--only`:

```
/m:plugin-packager ~/.claude my-tools --marketplace /path/to/this/repo --only skills:review,deploy agents:security-checker
```

This scans the source directory, copies components into `plugins/my-tools/`, generates the plugin manifest, and registers it in the marketplace. Commit and push to distribute.

## Updating plugins

Bump the version in the plugin's `.claude-plugin/plugin.json`, commit, and push. Users pull updates with:

```
/plugin marketplace update
```

## Local testing

Test a plugin directly without installing through the marketplace:

```shell
claude --plugin-dir ./plugins/m
```
