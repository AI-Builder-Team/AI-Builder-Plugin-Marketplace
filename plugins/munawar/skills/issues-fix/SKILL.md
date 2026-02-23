---
name: "m:issues-fix"
description: "Parse QC-annotated PR comments and launch bugfix agents in phased batches grouped by file domain"
argument-hint: "<path-to-qc-annotated-pr-comments-file>"
---

Read the file at `$ARGUMENTS`.

## Step 0: QC Gate (Circuit Breaker)

Before doing anything else, check whether the file contains **any** `QC_BOT_COMMENTS:` annotations. Search for the literal string `QC_BOT_COMMENTS:` in the file content.

- **If NO `QC_BOT_COMMENTS:` lines are found:** STOP immediately. Do NOT proceed to parsing or launching agents. Tell the user:

  > "This file has not been QC-annotated yet. Run `/m:m:issues-eval <file>` first to have each issue independently validated before fixing. If you want to proceed anyway without QC, re-run with explicit instruction to skip the QC gate."

  Then **wait for the user's response**. Only continue if the user explicitly says to proceed (e.g., "proceed anyway", "skip QC", "go ahead"). Otherwise, end here.

- **If `QC_BOT_COMMENTS:` lines ARE found:** Proceed to Step 1.

## Step 1: Parse issue blocks

Find every section that starts with `##### \`<file>:<line>\` 🟡 Unresolved`. Each issue block runs from that header down through the `QC_BOT_COMMENTS:` line and ends at the next `---` separator. Record the start and end line numbers for each block, and extract the target file path from the header (the part before the colon).

## Step 2: Consolidate and plan phases

First, **consolidate** issues that target the same file — they go to a single agent with all their blocks concatenated. Then group consolidated units into phases for parallel execution:

- Units targeting **different files** go in the same phase (parallel) since the agents won't conflict on edits.
- Units targeting files in the **same directory or module** that are tightly coupled (e.g. a router + its service, or a hook + the screen that consumes it) should be in **separate phases** to avoid conflicts from overlapping changes.

Present the phasing plan to the user before launching. Example:

```
Phase 1 (parallel):
  - Agent A: models/action_hub.py (Issue #1)
  - Agent B: hooks/useActionHubPainPoints.ts (Issue #6)
  - Agent C: scripts/extract_pain_points.py (Issues #7, #8, #9, #10, #11 — consolidated)
Phase 2 (parallel):
  - Agent D: routers/action_hub_router.py (Issues #2, #3, #4, #5 — consolidated)
```

## Step 3: Launch phases

For each phase, launch `m:bugfix` agents via the Task tool (`subagent_type: "m:bugfix"`). Launch all agents within a phase in parallel — do not wait for any agent in the phase to finish before launching the next agent in that phase. **Do** wait for all agents in a phase to complete before starting the next phase.

Each agent prompt must include the **raw issue block(s) verbatim** — the entire text from the `#####` header through the `QC_BOT_COMMENTS:` line for each issue. Do not summarize, reformat, or add your own interpretation. Pass it wholesale. When an agent receives multiple consolidated issues, include all blocks sequentially.

Use this template for each agent:

```
Fix the following PR review issue(s). The block(s) below are copied verbatim from the QC-annotated PR comments file.

**Source file:** <path to $ARGUMENTS>
**Issue block lines:** <start_line>-<end_line> [, <start_line>-<end_line>, ...]

---
<paste all raw issue blocks for this file here verbatim, in order>
---

Read the source code file(s) referenced in the issues, understand the concerns and QC analysis, then implement the fixes. If a QC verdict is PARTIAL or INVALID, use your judgement on whether a fix is still warranted.
```

## Step 4: Report

After all phases complete, summarize what was done:

| Phase | Issue | File | Agent Result |
|-------|-------|------|-------------|
