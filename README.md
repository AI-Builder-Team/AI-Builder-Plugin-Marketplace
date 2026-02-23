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

Have skills, agents, or commands in `~/.claude/` you want to package? Use the plugin packager with plain English:

```
/m:plugin-packager package my ~/.claude skills and agents into a plugin called my-tools and register it in this marketplace
```

Cherry-pick specific components:

```
/m:plugin-packager package just the review and deploy skills from ~/.claude into my-tools plugin, register in this marketplace
```

The packager parses your request, scans the source directory, copies components into `plugins/my-tools/`, generates the plugin manifest, and registers it in the marketplace. It auto-detects version bumps when updating existing plugins. Commit and push to distribute.

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
