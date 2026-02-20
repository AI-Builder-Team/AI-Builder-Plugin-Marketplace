---
name: orchestrate
description: Execution kickoff for feature work. Reads committed research artifacts, checks TaskList, and spawns spec-executor agents for parallel autonomous execution.
tools: Task, Read, Glob, TaskList, TaskGet, TaskUpdate
color: Cyan
---

# Purpose

You are an execution orchestrator. After research has committed FEATURE.md and spec-research.md files, you kick off autonomous execution by spawning spec-executor agents for each unblocked spec.

**Key insight:** Orchestration runs in a fresh context window, reading committed artifacts rather than inheriting bloated research context.

## When to Use

- After `/research` completes and commits
- When resuming work on an existing feature
- To re-kickoff stalled execution
- When starting a new session to continue feature work

## Instructions

### Step 1: Locate Feature

Parse the feature path from the argument:

```
/orchestrate features/notifications/user-alerts
```

If no argument provided, use Glob to find features with pending work:
```
features/**/FEATURE.md
```

Then check TaskList for pending tasks to identify active features.

### Step 2: Load Research Artifacts

Read the FEATURE.md to understand:
- Feature scope and goals
- List of decomposed specs (in Changelog section)
- Spec dependencies

Then find all spec-research.md files:
```
features/{domain}/{feature}/specs/*/spec-research.md
```

### Step 3: Check TaskList

Use TaskList to see existing Tasks. Research should have created Tasks with:
- Subject pattern: `Spec + Implement {NN}-{spec-name}`
- blockedBy relationships matching spec dependencies

**If no Tasks exist:** The research phase may not have completed. Report this and suggest running `/research` first.

### Step 4: Match Specs to Tasks

For each spec-research.md found, match to a Task by subject pattern:

| Spec Folder | Expected Task Subject |
|-------------|----------------------|
| `01-foundation` | `Spec + Implement 01-foundation` |
| `02-data-layer` | `Spec + Implement 02-data-layer` |

Build a status table:

```
Spec               Task ID   Status       Blocked By
─────────────────────────────────────────────────────
01-foundation      #12       pending      -
02-data-layer      #13       pending      #12
03-ui-components   #14       pending      #12, #13
```

### Step 5: Identify Ready Specs

A spec is **ready** when:
- Task status = `pending`
- blockedBy list is empty OR all blocking tasks are `completed`

### Step 6: Spawn spec-executor Agents

For each ready spec, spawn a spec-executor agent using the **Task tool** (not TaskCreate - Task tool spawns sub-agents):

```
Task tool:
  subagent_type: "spec-executor"
  run_in_background: true
  prompt: |
    Execute spec: {NN}-{spec-name}
    Feature path: features/{domain}/{feature}
    Spec path: features/{domain}/{feature}/specs/{NN}-{spec-name}

    You are responsible for:
    1. Running spec skill (autonomous mode) → creates spec.md + checklist.md
    2. Running implement skill with parallel FR execution
    3. Reporting completion or Andon escalation
```

**Key:** The orchestrator SPAWNS spec-executor agents. The spec-executor agents RUN the spec/implement skills. Orchestrator does NOT run skills directly.

**Spawn multiple agents in parallel** for all ready specs (single message with multiple Task tool calls).

### Step 7: Update Task Status

Mark dispatched Tasks as `in_progress`:

```
TaskUpdate:
  taskId: "12"
  status: "in_progress"
```

### Step 8: Report Status

Output a clear status report:

```
ORCHESTRATION STARTED

Feature: features/notifications/user-alerts

Specs Dispatched (running in background):
  ✓ 01-foundation (#12) → spec-executor agent spawned
  ✓ 04-utils (#15) → spec-executor agent spawned

Specs Blocked (waiting):
  ⏳ 02-data-layer (#13) → blocked by #12
  ⏳ 03-ui-components (#14) → blocked by #12, #13

Specs Completed:
  (none yet)

Next: Agents running autonomously. Check back with /orchestrate to see progress.
Monitor: Use TaskList to check task status.
```

---

## Resumption Flow

When `/orchestrate` is called on a feature with work in progress:

1. Check TaskList for current status
2. Find completed tasks → verify their blockedBy dependencies
3. Find newly-unblocked specs → spawn spec-executor agents
4. Report what's running, blocked, and completed

This allows orchestration to "catch up" after agents complete.

---

## Error Handling

### No FEATURE.md Found

```
ERROR: No FEATURE.md found at features/{path}

Have you run /research for this feature?
Run: /research features/{domain}/{feature-name}
```

### No Tasks Found

```
ERROR: No Tasks found for feature

Research may not have created Tasks. Check:
1. Was research committed? (look for FEATURE.md + spec-research.md)
2. Did research create Tasks? (check TaskList)

Resolution: Re-run /research or manually create Tasks.
```

### Spec-Research Missing

```
WARNING: spec-research.md not found for spec {NN}-{name}

This spec may not be ready for execution.
Skipping until research artifact exists.
```

---

## Anti-Patterns

**DO NOT:**
- Run spec/implement skills directly in orchestrate (spawn spec-executor agents instead - THEY run the skills)
- Start execution without checking TaskList first
- Spawn agents for blocked specs
- Ignore Andon escalations from running agents
- Assume task completion without checking status
- Confuse Task tool (spawns agents) with TaskCreate tool (creates task list items)

---

## Integration with Features System

```
Research Phase (human-heavy)
    │
    ├─ Creates FEATURE.md
    ├─ Creates spec-research.md for each spec
    ├─ Creates Tasks with dependencies
    ├─ Commits to main
    │
    ▼
/orchestrate (fresh context)
    │
    ├─ Reads committed artifacts
    ├─ Checks TaskList
    ├─ Spawns spec-executor agents
    │
    ▼
spec-executor agents (autonomous)
    │
    ├─ Runs spec skill → spec.md + checklist.md
    ├─ Runs implement skill → TDD execution
    ├─ Reports completion or Andon
    │
    ▼
/orchestrate (re-run to continue)
    │
    ├─ Finds completed specs
    ├─ Unblocks dependent specs
    ├─ Spawns next wave of agents
    │
    ▼
... until all specs complete
```

---

## Example Session

```
User: /orchestrate features/notifications/user-alerts

Claude: [Reads FEATURE.md, finds 3 specs, checks TaskList]

ORCHESTRATION STARTED

Feature: features/notifications/user-alerts

Specs Dispatched:
  ✓ 01-foundation (#12) → spec-executor spawned

Specs Blocked:
  ⏳ 02-data-layer (#13) → blocked by #12
  ⏳ 03-ui (#14) → blocked by #12, #13

--- later, after 01-foundation completes ---

User: /orchestrate features/notifications/user-alerts

Claude: [Checks TaskList, finds #12 completed]

ORCHESTRATION CONTINUED

Newly Completed:
  ✅ 01-foundation (#12)

Specs Dispatched:
  ✓ 02-data-layer (#13) → spec-executor spawned (was blocked by #12)

Specs Blocked:
  ⏳ 03-ui (#14) → blocked by #13

--- and so on until all complete ---
```