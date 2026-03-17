---
name: "m:tmux"
description: Manage Claude Code sessions across 8, 10, or 12 tmux panes in a single workstation
argument-hint: "[status|launch|quit|send] [pane] [dir] [args]"
---

# tmux-claude — Manage Claude Code Workstation

Manage 8, 10, or 12 worker panes plus a driver pane (0) in a single tmux session called `work`. All panes live in one Ghostty window.

## Supporting Files

- [scripts/launch.sh](scripts/launch.sh) — Launch the Ghostty workstation
- [scripts/sessions.sh](scripts/sessions.sh) — Session/pane management script
- [scripts/equalize.sh](scripts/equalize.sh) — Equalize column widths

## Instructions

$ARGUMENTS

### Routing

- **Custom objective**: Use the scripts and tmux commands below to achieve whatever the user asks.
- **Default** (no arguments): Show session status.

**Process vs inference:**
- "launch", "quit", "start", "stop", "close" → process operations (`launch`, `quit`, `status`)
- "is it running?", "is it free?", "is it working?", "is it busy?", "what are they doing?", "which ones are inferring?", "can I use pane N?" → inference state (`state`)

### Terminology

The user may say **split**, **session**, **pane**, or **tmux number** — they all mean the same thing: a tmux pane identified by its index. Always extract the number and treat it as a pane index.

### Pane Layout

All panes live in tmux session `work`, window 0. Pane indices are 0-based by creation order. Three layouts are supported:

**8-pane layout** (default — 4 columns × 2 rows):
```
┌──────┬─────┬─────┬─────┬─────┐
│      │  1  │  2  │  3  │  4  │
│  0   ├─────┼─────┼─────┼─────┤
│      │  5  │  6  │  7  │  8  │
└──────┴─────┴─────┴─────┴─────┘
```

**10-pane layout** (5 columns × 2 rows):
```
┌──────┬────┬────┬────┬────┬────┐
│      │  1 │  2 │  3 │  4 │  5 │
│  0   ├────┼────┼────┼────┼────┤
│      │  6 │  7 │  8 │  9 │ 10 │
└──────┴────┴────┴────┴────┴────┘
```

**12-pane layout** (6 columns × 2 rows):
```
┌──────┬───┬───┬───┬───┬───┬───┐
│      │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │
│  0   ├───┼───┼───┼───┼───┼───┤
│      │ 7 │ 8 │ 9 │10 │11 │12 │
└──────┴───┴───┴───┴───┴───┴───┘
```

- **Pane 0**: Driver pane (full height, left side). Used to orchestrate the others.
- **Remaining panes**: Worker panes in grid. Run Claude Code instances.

### Launch the Workstation

```bash
bash scripts/launch.sh        # 8 panes (default)
bash scripts/launch.sh 10     # 10 panes
bash scripts/launch.sh 12     # 12 panes
```

This opens Ghostty with the full layout. Alias it in `~/.zshrc` for quick access.

### Equalize Columns

If panes get resized (e.g. by dragging), re-equalize columns (auto-detects layout):
```bash
bash scripts/equalize.sh
```

### Commands

All commands use `scripts/sessions.sh` relative to the skill directory.

**Check status** — see which panes are free/busy:
```bash
bash scripts/sessions.sh status
```

**Launch Claude Code** in a specific pane or the first free one:
```bash
# First free pane, current directory
bash scripts/sessions.sh launch

# Specific pane, specific directory, extra args
bash scripts/sessions.sh launch 3 ~/projects/myapp "--resume"
```

Claude should be configured with "don't ask" permissions mode.

**Quit a Claude session** (sends Ctrl+C twice):
```bash
bash scripts/sessions.sh quit 3
bash scripts/sessions.sh quit-all
```

**Send text to a pane** (types it + Enter, or bare Enter with no text):
```bash
bash scripts/sessions.sh send 3 "some text here"
bash scripts/sessions.sh send 3          # bare Enter — useful for paste-truncation retries
```

**Clear a Claude conversation** (resets context in a running Claude session):
```bash
bash scripts/sessions.sh clear 3
```

**Message a running Claude session** (sends a prompt + verifies inference started):
```bash
bash scripts/sessions.sh message 3 "fix the login bug in auth.ts"
bash scripts/sessions.sh message 3 "fix the bug" no-qc   # skip verification
```

The `message` command automatically verifies that Claude started inferring after the prompt is sent. If the prompt was truncated during paste (common with long prompts), it sends up to 2 extra Enters to trigger submission. Pass `no-qc` as the third argument to skip this check.

**Check Claude's UI state** (IDLE/INFERRING/NO_CLAUDE):
```bash
bash scripts/sessions.sh state 3    # single pane
bash scripts/sessions.sh state      # all panes
```

**Read what's on screen** in a pane:
```bash
bash scripts/sessions.sh read 3
```

### Pane Number Aliases

The user refers to panes in many ways. Extract the number and pass it to the script:

| User says | Means pane |
|-----------|------------|
| split 1, split 3 | 1, 3 |
| N1, N2 … N8 | 1, 2 … 8 |
| number 1, number 3 | 1, 3 |
| session 1, pane 5 | 1, 5 |
| tmux1, tmux 3 | 1, 3 |
| #1, #4 | 1, 4 |
| just "1", "3" | 1, 3 |

### Shorthands

| User says | Means | Command |
|-----------|-------|---------|
| "is Claude free?", "is it working?", "which are busy?" | Check inference state | `bash scripts/sessions.sh state` |
| "is pane 3 running?" | Check single pane inference | `bash scripts/sessions.sh state 3` |
| "clear claude N1" | Reset Claude's conversation | `bash scripts/sessions.sh clear 1` |
| "message claude N3 ..." | Send a prompt to running Claude | `bash scripts/sessions.sh message 3 "prompt"` |
| "quit session 5" | Stop Claude in pane 5 | `bash scripts/sessions.sh quit 5` |
| "launch in tmux2" | Start Claude in pane 2 | `bash scripts/sessions.sh launch 2` |

### Workflow: Hand Off a Task

1. Run `bash scripts/sessions.sh status` to find free panes
2. Pick the lowest free number
3. Launch with a directory: `bash scripts/sessions.sh launch N /path/to/project`
4. Wait a moment for Claude to start, then message it:
   ```bash
   bash scripts/sessions.sh message N "fix the login bug in auth.ts"
   ```

### Workflow: Launch Multiple Tasks

Fan out work across panes:
```bash
bash scripts/sessions.sh launch "" ~/project-a
bash scripts/sessions.sh launch "" ~/project-b
bash scripts/sessions.sh launch "" ~/project-c
```

Each picks the next available pane automatically.

### Claude Code UI Signals

The `state` command programmatically detects whether Claude is inferring. Trust its output — do not attempt to visually parse pane content yourself.

Long prompts sent via `tmux send-keys` sometimes get buffered by bracketed paste and need a second Enter. The `message` command handles this automatically with retries.

### Key Details

- The tmux session `work` is **persistent** — survives terminal close. Reconnect with `tmux attach -t work`.
- Free = shell prompt (zsh/bash), no `claude` child process running.
- Lower-numbered panes are preferred when auto-selecting.
- Quitting sends `Ctrl+C` twice with a 0.5s gap — enough for Claude Code's graceful shutdown.
- Pane 0 is the driver — not included in status/launch/quit operations.
- All pane targets use `work:0.N` format internally.
