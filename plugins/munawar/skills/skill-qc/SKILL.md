---
name: "m:skill-qc"
description: Assess a skill for portability and apply generalization patterns
argument-hint: "[skill-path-or-name]"
disable-model-invocation: false
model: opus
---

# Skill QC — Portability & Generalization Audit

Assess and fix a Claude Code skill so it works across repositories, machines, and users.

## Target

$ARGUMENTS

## Step 1: Locate the skill

Never edit files under `~/.claude/plugins/cache/` — that's a read-only installed copy.

To find the editable source, first figure out what kind of repo you're in. If the CWD path or directory name contains "plugin", "skills", or "marketplace", or there's a `skills/` directory with skill folders in it, you're likely in a plugin or skills repo — search `plugins/*/skills/*/SKILL.md` and `skills/*/SKILL.md` relative to the repo root. If not found, check these fallbacks:

1. **Home skills** — `~/.claude/skills/<skill-name>/SKILL.md`
2. **Project-local skills** — `<project-root>/.claude/skills/<skill-name>/SKILL.md`
3. **Ask the user** — If not found at the above places, ask the user where it lives. Seek guidance instead of searching further.

Once found, read the SKILL.md and every file in the skill directory (scripts/, reference/,  docs/, assets/ etc.). Especially important are any paths referenced in the SKILL.md

## Step 2: Run the generalization audit

Evaluate the skill against the 10 patterns below. For each, report:

- **PASS** — follows the pattern or doesn't apply
- **WARN** — minor portability issue
- **FAIL** — hard break on other machines/repos

Only detail WARN and FAIL items. Summarize PASS as a count.

### The 10 Generalization Patterns

#### P01 — Self-contained bundling
Everything the skill needs lives inside its directory tree. No references to external scripts, configs, or assets that won't travel with it. No copying scripts to `~/bin` or `~/.local/bin`. No dependence on shell aliases, `.bashrc`, or profile modifications — scripts run non-interactively.

**Check:**
- Grep SKILL.md and scripts for paths outside the skill directory (excluding `/usr/bin`, `/tmp`, `$HOME`)
- Look for `cp`, `install`, `ln -s`, `mkdir -p ~/bin` patterns
- Look for `source ~/.bashrc`, `source ~/.zshrc`, or alias references

#### P02 — Dynamic paths
All paths derived from the environment — never hardcoded to a specific user's filesystem. SKILL.md references bundled scripts using **relative paths from the skill directory root** (e.g. `scripts/foo.sh`) — the agent resolves these automatically, no absolute paths needed. Reserve `${CLAUDE_PLUGIN_ROOT}` for non-SKILL.md contexts (hooks, MCP configs, executed scripts). Shell scripts use `$(dirname "$0")` to find siblings, not bare `./` references. Temp files use `mktemp` with cleanup traps, not hardcoded `/tmp/skillname-*`.

**Check:**
- Grep for `/Users/<username>/`, `/home/<username>/`, or any absolute path with a username
- Look for absolute script paths in SKILL.md that should be relative (including `~/.claude/skills/...` or `${CLAUDE_PLUGIN_ROOT}` paths that could be simple relative paths)
- In shell scripts, look for `source ./`, `cat ./` without a `SCRIPT_DIR` pattern
- Look for hardcoded temp file paths

#### P03 — Generic naming
Names describe function, not the project. No product names, company names, or repo names in the skill name, script filenames, or user-facing strings — unless the skill genuinely exists to manage that specific tool.

**Check:** Scan skill name, filenames, SKILL.md content, and script content for project-specific names.

#### P04 — Configuration
Anything that varies between projects (subdirectory names, start commands, env var names) must be configurable via arguments, env vars, or git config — with sensible defaults. Use existing config infrastructure (git config, env vars, project config files), don't invent new formats (`.skillrc`, `.skill.conf`). Precedence: CLI args > env vars > git config > skill defaults.

**Check:**
- Look for hardcoded subdirectory names (`src/`, `backend/`), start commands (`npm run dev`), or project-specific env vars that aren't parameterized
- Look for custom config files being created or read
- Does the skill accept arguments for values that vary by project?

#### P05 — Detect, don't assume
Check for capabilities (command existence, lockfiles, file presence) rather than hardcoding specific tools or platform names. Detect the package manager from lockfiles instead of assuming `npm`. Check `command -v` instead of branching on `uname`.

**Check:**
- Look for hardcoded `npm`, `pnpm`, `bun`, `yarn` without detection logic
- Look for `uname` checks or OS-specific branches where capability checks would work

#### P06 — Honest prerequisites
Document the contract: what tools, structure, or configuration must the host project have? Pin minimum versions for external tools (git, gh, jq, etc.). Don't pretend portability exists where it doesn't.

**Check:**
- Are there implicit assumptions about the host project that aren't documented?
- If external tools are required, are minimum versions specified?

#### P07 — Idempotency
Running the skill twice must not break anything. Check before writing files. Check if servers are already running before starting them.

**Check:** Look for file writes without existence checks, server starts without port checks, or operations that would fail or corrupt on re-run.

#### P08 — Externalized secrets
No API keys, tokens, or passwords in skill files. Read from env vars or credential stores.

**Check:** Grep for strings that look like secrets. Check for `.env` files being created with hardcoded values.

#### P09 — Separation of brain and hands
SKILL.md orchestrates; scripts/ executes. Don't embed large code blocks (>20 lines) in SKILL.md when they should be extracted to scripts.

**Check:** Are there large inline code blocks that should be scripts?

#### P10 — Glob allowed-tools
If `allowed-tools` is set in the frontmatter, use wildcards that survive version bumps and path changes.

**Check:** Are tool patterns broad enough? Exact paths will break on updates.

## Step 3: Report

Present findings as a table:

```
| # | Pattern | Status | Detail |
|---|---------|--------|--------|
| P01 | Self-contained bundling | PASS | — |
| P02 | Dynamic paths | FAIL | Hardcoded /Users/john/ on line 42 of scripts/setup.sh |
...
```

Then list the FAIL and WARN items with:
- **What's wrong** — the specific line/file/pattern
- **How to fix** — the concrete change to make
- **Risk if unfixed** — what breaks and where

## Step 4: Fix

Ask the user: "Should I apply the fixes?" If yes, make all FAIL and WARN fixes using the Edit tool. After fixing, re-run the audit mentally to confirm all issues are resolved.

If the skill is inside a plugin marketplace repo, remind the user to bump the version and push (but do NOT do it automatically — the user may want to batch changes).
