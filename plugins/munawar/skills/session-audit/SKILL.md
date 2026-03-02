---
name: session-audit
description: Parse and audit Claude Code session transcripts
argument-hint: "<session-id> [instruction]"
---

# Session Audit

Audit a Claude Code session by its ID. Parses the JSONL transcript to show conversation flow, tool usage stats, errors, retries, and subagent activity.

## Arguments

- `$0` — Session UUID (required)
- `$ARGUMENTS` — Session ID followed by an optional free-form instruction

## Supporting Files

- [scripts/resolve.py](scripts/resolve.py) — Resolve session ID to JSONL file path(s)
- [scripts/conversation.py](scripts/conversation.py) — Extract readable conversation transcript
- [scripts/stats.py](scripts/stats.py) — Token usage, turn counts, tool call breakdown, timing
- [scripts/errors.py](scripts/errors.py) — Find errors, retries, and self-corrections (shows originating tool call, input, and turn)
- [scripts/context.py](scripts/context.py) — Extract N records before/after a specific line for drill-down
- [scripts/find.py](scripts/find.py) — Search transcript by keyword/regex with scoped filtering (user, both, all)
- [scripts/only.py](scripts/only.py) — Filter to show only one category: user, assistant, thinking, tools, results, errors, bash, edits, agents

## Instructions

### Step 1: Resolve the session

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/resolve.py "$0"
```

This outputs JSON with `main` (path to JSONL), `subagents` (list of subagent JSONLs), and `project_dir`.

If the session is not found, try searching with the current project directory:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/resolve.py "$0" --project-dir "$(pwd)"
```

If still not found, fall back to grep:
```bash
grep -rl "$0" ~/.claude/projects/*/  2>/dev/null | head -5
```

### Step 2: Run reports to answer the instruction

Use the resolved JSONL path from step 1. The `JSONL` placeholder below means the path returned by resolve.

If a specific instruction was provided, use your judgment to pick whatever combination of the tools below best answers it. Run as many times as needed.

If no instruction was provided (or the instruction does not override this default), perform a **lessons-learned audit**:
1. Run stats, errors, and conversation (with `--no-thinking --max-len 500`) on the main session
2. Run errors on each subagent session
3. Focus your analysis on identifying:
   - Points where the user had to clarify direction or redirect the agent
   - Places where the agent floundered, retried, or took a wrong path before finding the right approach
   - Tool/script errors and how they were resolved (or not)
   - Moments where the agent recovered from uncertainty and what triggered the recovery
4. For each finding, note whether any skills, agents, or commands were involved
5. Derive concise, actionable lessons — generic rules that could be baked into the relevant skill, agent, or system prompt so future sessions arrive at the right outcome more directly
6. Lessons must NOT make any skill or agent less generic or less able to function across varied contexts — they should improve precision without narrowing scope

### Available reports

**Stats:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/stats.py JSONL
```

**Conversation:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/conversation.py JSONL
```

Options: `--no-thinking` to hide thinking blocks, `--no-tools` to hide tool calls, `--max-len 300` to truncate long blocks.

**Errors:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/errors.py JSONL
```

### Step 2b: Drill into specific errors

When errors.py reports issues, use context.py to see surrounding records:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/context.py JSONL <LINE_NUM> [radius]
```

- `LINE_NUM` — the JSONL line number from the errors report
- `radius` — how many non-progress records before/after to show (default: 3, use 5-8 for deeper context)

The target line is marked with `>>>`. Progress records are skipped to keep the output focused.

Run this for each error that needs investigation. The output shows the tool call that was attempted, the error result, and what the assistant did next.

### Step 2c: Search for a keyword or pattern

Use find.py to locate which turns mention a specific term:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/find.py JSONL "pattern" [--scope user|both|all] [--max-len 300]
```

Scopes:
- `user` — only human text messages
- `both` — human text + assistant text (default)
- `all` — human text + assistant text + thinking + tool calls + tool results

The pattern is a regex (case-insensitive by default, add `--case-sensitive` to override). Each match shows the turn number, line, timestamp, which field matched, and a snippet with the match highlighted in `**` markers.

Combine with context.py to drill into any match: find.py gives you the line numbers, context.py shows the surrounding conversation.

### Step 2d: Filter to a single category

Use only.py to see just one type of record:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/session-audit/scripts/only.py JSONL <mode> [--max-len 500]
```

Modes:
- `user` — human text messages only
- `assistant` — assistant text responses only
- `thinking` — chain-of-thought blocks only
- `tools` — all tool calls (name + input summary)
- `results` — all tool results
- `errors` — only error results
- `bash` — bash commands paired with their output
- `edits` — Edit/Write calls with file paths and old/new strings
- `agents` — Agent tool calls (subagent spawns with type, desc, prompt)

### Step 3: Check subagents

If `resolve.py` returned subagent paths, run the same reports on each subagent JSONL.
Prefix each subagent report with its filename so the user can tell them apart.

### Step 4: Summarize

Provide a concise summary that directly answers the instruction. If running the default lessons-learned audit, present findings and lessons in whatever format best fits the session's content.

Constraints on lessons:
- Must not reduce the generality or flexibility of any skill/agent
- Must improve directness of future execution without over-fitting to this session's specifics
- If no meaningful lessons exist, say so — do not fabricate improvements

## JSONL Schema Reference

Each line is a JSON object with a `type` field:

| type | description | key fields |
|---|---|---|
| `user` | Human messages + tool results | `message.content` (string or tool_result blocks), `uuid`, `parentUuid`, `timestamp` |
| `assistant` | Model responses | `message.content[]` with blocks: `thinking`, `text`, `tool_use`. Also `message.usage` for tokens. |
| `progress` | Streaming progress for tool calls | `toolUseID`, `data` |
| `file-history-snapshot` | File state checkpoints | `snapshot.trackedFileBackups` |
| `system` | Internal bookkeeping | `subtype`, `durationMs` |

Content block types inside `message.content[]`:
- `thinking` — chain-of-thought (has `thinking` and `signature`)
- `text` — visible response text
- `tool_use` — tool invocation (`name`, `id`, `input`)
- `tool_result` — tool output (`tool_use_id`, `content`, `is_error`)
