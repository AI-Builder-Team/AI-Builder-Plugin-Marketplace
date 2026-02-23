---
description: "Comprehensive PR review using specialized agents"
argument-hint: "[review-aspects]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Write", "Edit", "Task", "AskUserQuestion"]
---

# Comprehensive PR Review

Run a comprehensive pull request review using multiple specialized agents, each focusing on a different aspect of code quality. All findings are written to a tracking file, validated, user-triaged, then posted as a single GitHub PR review.

**Review Aspects (optional):** "$ARGUMENTS"

---

## Step 1 — Verify PR Exists and Gather Context

This command requires an open PR. Run:

```bash
gh pr view --json number,title,url,headRefName,baseRefName,body
```

If no PR is open, **stop immediately** and tell the user:
> "No open PR found for this branch. Please open a PR first, then re-run /review-pr."

Extract and store:
- `PR_NUMBER` — the PR number
- `PR_TITLE` — the PR title
- `PR_URL` — the PR URL
- `PR_BODY` — the PR description
- `HEAD_BRANCH` — the head branch name
- `BASE_BRANCH` — the base branch name (e.g. `main`)

---

## Step 2 — Identify Commits and Changed Files

Run the following to get commits on this branch **excluding merge commits**:

```bash
git log origin/main..HEAD --no-merges --oneline
```

Run the following to get all files changed relative to main:

```bash
git diff origin/main...HEAD --name-only
```

Also get the full diff for agent context:

```bash
git diff origin/main...HEAD
```

Store: list of commits, list of changed files, and the full diff text.

---

## Step 3 — Create the PR Review Tracking File

Check if `.ignore/` exists at repo root. If not, create it:

```bash
mkdir -p .ignore
```

Create the file `.ignore/pr-review-<PR_NUMBER>.md` with this structure:

```markdown
# PR Review: #<PR_NUMBER> — <PR_TITLE>

**Branch**: `<HEAD_BRANCH>` → `<BASE_BRANCH>`
**URL**: <PR_URL>

## PR Description

<PR_BODY>

---

## Commits (excluding merges from main)

<one line per commit: `- <sha> <message>`>

## Changed Files

<one line per file: `- path/to/file`>

---

## Findings

_Populated by review agents — see below._

---

## Validation Results

_Populated by validation agent._

---

## PR Comments Status

_Populated by PR comment agent._
```

---

## Step 4 — Determine Applicable Review Agents

Parse `$ARGUMENTS` for specific aspects: `comments`, `tests`, `errors`, `types`, `code`, `simplify`, `all`.
Default (no args or `all`): run all applicable agents.

**Always run:**
- `logical-bug-hunter` (new — see below)
- `code-reviewer`

**Run if test files changed** (files matching `test_*`, `*.test.*`, `*.spec.*`):
- `pr-test-analyzer`

**Run if comments or docstrings were added/changed:**
- `comment-analyzer`

**Run if error handling, try/catch, or exception logic changed:**
- `silent-failure-hunter`

**Run if new types, interfaces, schemas, or Pydantic models were added:**
- `type-design-analyzer`

**Always run last (polish pass):**
- `code-simplifier`

---

## Step 5 — Launch Review Agents in Parallel

Launch all applicable agents **simultaneously** using the Task tool. Each agent must receive:
1. The full git diff (`git diff origin/main...HEAD`)
2. The PR title and description
3. The list of changed files
4. Instruction: **"Do not edit any files. Return your findings as a structured list only."**

### logical-bug-hunter agent

Use `subagent_type: general-purpose` with this prompt:

> You are a logical bug hunter reviewing a pull request.
>
> **PR Title**: <PR_TITLE>
> **PR Description**: <PR_BODY>
> **Changed Files**: <file list>
> **Full Diff**:
> ```
> <full diff>
> ```
>
> Your task:
> 1. First, form a clear understanding of what this PR is trying to achieve holistically — read the PR title, description, and all changed code carefully.
> 2. Then, hunt specifically for **logical bugs**: incorrect conditions, wrong comparisons, off-by-one errors, incorrect business logic, data being used in the wrong order, state mutations that break assumptions, race conditions, incorrect calculations, missing edge cases that the PR's own intent implies should be handled.
> 3. Do NOT flag style issues, formatting, or things covered by linting. Focus only on logic correctness.
>
> Return your findings as a numbered list. For each finding include:
> - A one-sentence summary of the bug
> - The file and line number (e.g. `services/finance.py:142`)
> - A brief explanation of why it is a logical bug given the PR's intent
>
> If you find no logical bugs, say so explicitly.

### code-reviewer agent

Use `subagent_type: code-reviewer`. Provide the full diff and PR context. Instruct it to return findings as a numbered list with file:line references.

### pr-test-analyzer agent (if applicable)

Use `subagent_type: pr-test-analyzer`. Provide the full diff and PR context.

### comment-analyzer agent (if applicable)

Use `subagent_type: comment-analyzer`. Provide the full diff and PR context.

### silent-failure-hunter agent (if applicable)

Use `subagent_type: silent-failure-hunter`. Provide the full diff and PR context.

### type-design-analyzer agent (if applicable)

Use `subagent_type: type-design-analyzer`. Provide the full diff and PR context.

### code-simplifier agent

Use `subagent_type: code-simplifier`. Provide the full diff and PR context. Instruct it to return simplification suggestions as a numbered list only, **not** to make any edits.

---

## Step 6 — Aggregate Findings into the Tracking File

After all agents complete, collect every finding from every agent and merge them into a single flat numbered list.

**Numbering rules:**
- One global sequence: 1, 2, 3, 4, ...
- Each item includes the agent that found it in brackets
- Format per item:

```
<N>. **[<agent-name>]** <one-sentence summary> — `<file>:<line>`
   <brief explanation if agent provided one>
```

**Update the tracking file** — replace the `## Findings` section placeholder with the complete numbered list.

Example:

```markdown
## Findings

1. **[logical-bug-hunter]** Off-by-one in month range calculation causes January to be excluded — `services/finance.py:142`
   The loop uses `range(1, month)` but should use `range(1, month + 1)` per the PR's stated intent to include the current month.

2. **[code-reviewer]** Missing authorization check on the new `/export` endpoint — `routers/finance.py:88`
   Any authenticated user can export any organization's data; org-scoping is applied to all other endpoints in this file.

3. **[silent-failure-hunter]** Exception swallowed silently in batch processor — `services/batch.py:210`
   The except block logs a warning but returns an empty list, hiding the real error from callers.

4. **[pr-test-analyzer]** No test coverage for the edge case where `monthly_data` is empty — `tests/test_finance.py`
   The new aggregation logic has a branch for empty data but no test exercises it.
```

---

## Step 7 — Launch Validation Agent

After the tracking file is written, launch a **validation agent** using `subagent_type: general-purpose`.

The validation agent must:

1. Read the tracking file (`.ignore/pr-review-<PR_NUMBER>.md`) to get all findings.
2. Read the PR diff (`git diff origin/main...HEAD`) and PR context.
3. For each finding, **spawn a parallel sub-task** (using the Task tool with `subagent_type: general-purpose`) to:
   - Re-read the relevant source file at the relevant line
   - Consider the PR's holistic intent
   - Determine: is this issue **VALID**, **INVALID**, or **UNCERTAIN**?
   - Return a one-sentence verdict with reasoning
4. After all sub-tasks complete, update the `## Validation Results` section of the tracking file with verdicts for every issue:

```markdown
## Validation Results

**Issue 1** [VALID]: Confirmed — `range(1, month)` indeed excludes the current month; the PR description explicitly says it should be included.

**Issue 2** [VALID]: Confirmed — no `require_same_org` dependency is present on the new endpoint unlike all surrounding endpoints.

**Issue 3** [INVALID]: The caller at `routers/batch.py:55` checks for an empty return and raises an HTTPException, so the error is not actually hidden from the client.

**Issue 4** [UNCERTAIN]: The empty-data branch exists but whether it needs a test depends on whether the data pipeline can produce empty results in production — could not determine from the diff alone.
```

The validation agent should **not** modify the Findings section — only write to Validation Results.

---

## Step 8 — Pause for User Triage

After the validation agent completes, tell the user:

> "The validation agent has finished. Please open `.ignore/pr-review-<PR_NUMBER>.md` and **delete any findings you consider invalid** (you can use the Validation Results section as a guide). When you're done, come back here and let me know."

Use `AskUserQuestion` to wait for the user to confirm they have finished triaging.

---

## Step 9 — Reorganize the Tracking File

After the user acknowledges they are done:

1. Read the current `.ignore/pr-review-<PR_NUMBER>.md`.
2. Re-read the `## Findings` section and collect all remaining items (some may have been deleted by the user).
3. Renumber the remaining findings sequentially from 1 with no gaps.
4. Update the `## Validation Results` section to match the new numbering (remove entries for deleted issues, renumber references).
5. Write the cleaned-up file back.

Tell the user how many findings remain after triage.

---

## Step 10 — Post PR Review Comments

Launch a **PR comment poster agent** using `subagent_type: general-purpose`.

The agent must:

1. Read `.ignore/pr-review-<PR_NUMBER>.md` to get the final numbered findings list.
2. Fetch the PR diff with line position data:
   ```bash
   gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/files
   ```
   Use `gh repo view --json nameWithOwner -q .nameWithOwner` to get `{owner}/{repo}`.
3. For each finding, attempt to map `file:line` to a **diff position** (the line number within the unified diff patch, which is what GitHub's review API requires). The diff position is the line offset within the `patch` field of the file in the API response.
4. Build a single PR review with all mappable comments:
   ```bash
   gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews \
     -X POST \
     -f body="Automated review via /review-pr" \
     -f event="COMMENT" \
     -f "comments[][path]=<file>" \
     -f "comments[][position]=<diff_position>" \
     -f "comments[][body]=**[<agent-name>]** <full finding text>"
   ```
   Post **one review** containing all inline comments at once (not separate API calls per comment).
5. For findings where the file:line could not be mapped to a diff position (e.g. the line was not part of the diff, or the file was not in the PR), **skip** that comment from the review but document it.
6. After posting, update the `## PR Comments Status` section of the tracking file:

```markdown
## PR Comments Status

**Issue 1**: Posted as inline comment on `services/finance.py` line 142.
**Issue 2**: Posted as inline comment on `routers/finance.py` line 88.
**Issue 3**: Skipped — line 210 of `services/batch.py` was not part of the diff (context-only line).
**Issue 4**: Posted as inline comment on `tests/test_finance.py`.
```

---

## Step 11 — Final Summary

After the PR comment agent completes, report to the user:

```
## PR Review Complete — #<PR_NUMBER>

**Findings after triage**: X issues
**Comments posted**: Y inline comments on the PR
**Skipped (not in diff)**: Z issues

Tracking file: .ignore/pr-review-<PR_NUMBER>.md
PR: <PR_URL>
```

---

## Available Review Aspects (for $ARGUMENTS filtering)

- **comments** — comment-analyzer only
- **tests** — pr-test-analyzer only
- **errors** — silent-failure-hunter only
- **types** — type-design-analyzer only
- **code** — code-reviewer only
- **logic** — logical-bug-hunter only
- **simplify** — code-simplifier only
- **all** — all applicable agents (default)

When specific aspects are requested, still always run `logical-bug-hunter` and `code-reviewer` unless the user explicitly named other aspects without `all`.

---

## Notes

- The tracking file persists after the session so you can reference findings later.
- Agents always receive the full diff for context even when scoped to specific files.
- The validation agent's parallel sub-tasks make verification fast regardless of finding count.
- GitHub's review comment API requires diff positions, not source line numbers — the poster agent handles this mapping.
- All agents are instructed not to edit source files during this workflow.
