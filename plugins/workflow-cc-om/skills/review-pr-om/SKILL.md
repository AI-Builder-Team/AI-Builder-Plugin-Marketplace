---
name: review-pr-om
description: Adversarial 3-agent PR review with interactive issue triage and GitHub inline comments
argument-hint: <pr-number>
disable-model-invocation: true
allowed-tools: Bash(gh repo view *), Bash(gh pr view *), Bash(gh pr diff *), Bash(gh api repos/*/pulls/*/reviews), Bash(gh auth status), Bash(git log *), Bash(git blame *), Bash(git show *), Bash(git diff *), Bash(jq *), Bash(grep *), Bash(awk *), Bash(head *), Bash(tail *), Bash(wc *), Bash(cat *), Bash(ls *), Read, Grep, Glob, Task, AskUserQuestion, WebFetch
---

# Adversarial PR Review

You are running an interactive adversarial PR review workflow for PR **#$ARGUMENTS**.

ultrathink

## PR Context

- **PR Number:** $ARGUMENTS
- **Repository:** !`gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "UNKNOWN_REPO"`
- **PR Title:** !`gh pr view $0 --json title --jq .title 2>/dev/null || echo "UNKNOWN_TITLE"`
- **PR Author:** !`gh pr view $0 --json author --jq .author.login 2>/dev/null || echo "UNKNOWN_AUTHOR"`
- **HEAD SHA:** !`gh pr view $0 --json headRefOid --jq .headRefOid 2>/dev/null || echo "UNKNOWN_SHA"`
- **Base Branch:** !`gh pr view $0 --json baseRefName --jq .baseRefName 2>/dev/null || echo "UNKNOWN_BASE"`
- **Changed Files:**
!`gh pr view $0 --json files --jq '.files.[].path' 2>/dev/null || echo "UNKNOWN_FILES"`

## Pre-flight Checks

Before starting, verify:
1. The repository is not "UNKNOWN_REPO" — if it is, tell the user to run from within a git repo or specify `--repo`.
2. The PR title is not "UNKNOWN_TITLE" — if it is, the PR number may be invalid. Ask the user to verify.
3. If any context value is "UNKNOWN_*", stop and report the issue. Do NOT proceed with a broken context.

Store the HEAD SHA and repo info — you will need them for the final API call.

## Phase 1: Initial Review (Agent 1 — Reviewer)

Spawn a `general-purpose` subagent via the **Task** tool.

**Prompt for Agent 1:**

> You are a senior code reviewer. Your job is to find real, actionable issues in PR #$ARGUMENTS.
>
> **Step 1:** Run these commands to get context:
> - `gh pr diff $ARGUMENTS` — full diff
> - `gh pr view $ARGUMENTS --json body --jq .body` — PR description
> - `gh pr view $ARGUMENTS --json files --jq '.files.[] | {path, additions, deletions}'` — changed files with stats
>
> **Step 2:** Read the changed files in the repository (using Read tool) to understand surrounding context. Don't review the diff in isolation.
>
> **Step 3:** Analyze for these categories:
> - **Bugs** — logic errors, off-by-one, null/undefined access, wrong conditions
> - **Security** — injection, auth bypass, data exposure, unsafe deserialization
> - **Performance** — N+1 queries, unnecessary allocations, missing indexes, blocking I/O in hot paths
> - **Error handling** — swallowed exceptions, missing error paths, catch-all blocks
> - **Race conditions** — shared mutable state, missing locks, TOCTOU
> - **Edge cases** — boundary conditions, empty inputs, large inputs, unicode, timezone issues
> - **API misuse** — wrong method signatures, deprecated usage, contract violations
> - **Readability** — confusing names, overly complex logic, missing context for future readers
>
> **Do NOT flag:**
> - Style preferences (formatting, bracket placement) unless they cause confusion
> - Missing documentation unless it's a public API
> - "Nit" issues that don't affect correctness or readability
> - Things that are clearly intentional and well-reasoned
>
> **Step 4:** Output your findings in this exact format for EACH issue:
>
> ```
> ### F{N}: {one-line title}
> - **File:** {exact file path}
> - **Line:** {line number in the NEW version of the file}
> - **Severity:** critical | warning | nit
> - **Category:** {from the list above}
> - **Description:** {detailed explanation — what's wrong, why it matters, what could go wrong}
> - **Suggested comment:** {the exact text to post as a GitHub inline comment — concise, constructive, specific}
> ```
>
> If you find NO issues, say "NO_ISSUES_FOUND" and briefly explain why the PR looks good.
>
> **Bash hygiene:** Only run Bash for actual shell commands (gh, git, echo, etc.). Do ALL reasoning and analysis as plain text output — never inside bash script comments. Never write shell scripts with `#` comment blocks to think through logic. Avoid `->`, `=>`, or `>` characters (including `2>/dev/null`) inside any bash command you run. Do NOT chain commands with `;`, `&&`, or `||`. Use the **Read** tool instead of `cat`, use the **Glob** tool instead of `ls`, use the **Grep** tool instead of `grep`, `awk`, `head`, or `tail` — never run those via Bash.

Wait for Agent 1 to complete. Save its full output.

## Phase 2: Adversarial Challenge (Agent 2 — Challenger)

Spawn a second `general-purpose` subagent.

**Prompt for Agent 2:**

> You are a devil's advocate reviewer. Your job is to stress-test the findings of a code review. Challenge every finding — argue the author's perspective.
>
> **The PR:** #$ARGUMENTS
>
> **Step 1:** Run `gh pr diff $ARGUMENTS` and read the relevant source files to independently understand the code.
>
> **Step 2:** Read the PR description with `gh pr view $ARGUMENTS --json body --jq .body` to understand the author's intent.
>
> **Step 3:** For EACH finding below, argue the counter-position:
>
> {INSERT AGENT 1's FULL OUTPUT HERE}
>
> For each finding, consider:
> - Is this actually a problem in this specific context, or is it theoretical?
> - Is there surrounding code, framework behavior, or runtime guarantees that make this safe?
> - Is the severity correct? Would this actually cause a production issue?
> - Is the reviewer imposing their preference rather than catching a real issue?
> - Could the author have written it this way intentionally for a good reason?
> - Is the suggested comment accurate and actionable, or vague/misleading?
>
> **Step 4:** Also independently scan for issues Agent 1 MISSED. Focus especially on:
> - Subtle bugs that require multi-file context
> - Security issues that only appear when you trace data flow
> - Edge cases that require domain knowledge
>
> **Step 5:** Output for EACH of Agent 1's findings:
>
> ```
> ### F{N}: {original title}
> - **Verdict:** valid | false-positive | overstated | understated | needs-refinement
> - **Reasoning:** {detailed argument for your verdict — be specific, cite code}
> - **Refined comment:** {if needs-refinement: improved comment text. Otherwise: "N/A"}
> ```
>
> Then, if you found missed issues:
>
> ```
> ### MISSED ISSUES
>
> ### M{N}: {title}
> - **File:** {path}
> - **Line:** {line number}
> - **Severity:** critical | warning | nit
> - **Category:** {category}
> - **Description:** {explanation}
> - **Suggested comment:** {comment text}
> ```
>
> **Bash hygiene:** Only run Bash for actual shell commands (gh, git, echo, etc.). Do ALL reasoning and analysis as plain text output — never inside bash script comments. Never write shell scripts with `#` comment blocks to think through logic. Avoid `->`, `=>`, or `>` characters (including `2>/dev/null`) inside any bash command you run. Do NOT chain commands with `;`, `&&`, or `||`. Use the **Read** tool instead of `cat`, use the **Glob** tool instead of `ls`, use the **Grep** tool instead of `grep`, `awk`, `head`, or `tail` — never run those via Bash.

Wait for Agent 2 to complete. Save its full output.

## Phase 3: Arbitration (Agent 3 — Arbiter)

Spawn a third `general-purpose` subagent.

**Prompt for Agent 3:**

> You are an impartial arbiter. You have two perspectives on a PR review. Your job is to make the final call on what gets included.
>
> **The PR:** #$ARGUMENTS
>
> Run `gh pr diff $ARGUMENTS` and read the source files to form your own independent understanding.
>
> **Agent 1 (Reviewer) findings:**
> {INSERT AGENT 1's FULL OUTPUT}
>
> **Agent 2 (Challenger) analysis:**
> {INSERT AGENT 2's FULL OUTPUT}
>
> **Your task:**
>
> 1. For each finding, weigh both perspectives. You are NOT biased toward either agent.
> 2. Decide: **INCLUDE** or **EXCLUDE** from the final review.
>    - INCLUDE if: the finding identifies a genuine issue that the PR author should address or acknowledge
>    - EXCLUDE if: it's a false positive, purely stylistic, or theoretical with no practical impact
> 3. For included findings, select or write the best comment text:
>    - Use Agent 1's original if it was accurate and well-written
>    - Use Agent 2's refinement if it improved the comment
>    - Write your own if neither was ideal
> 4. Also INCLUDE any missed issues from Agent 2 that you verify as genuine.
> 5. Calibrate tone: professional, constructive, specific. No snark. No "you should have..." phrasing.
> 6. Adjust severity if warranted by both perspectives.
>
> **Output the FINAL review in this exact format:**
>
> ```
> ## Final Review: {total count} findings
>
> ### R{N}: {title}
> - **File:** {exact file path}
> - **Line:** {line number in the new version of the file}
> - **Severity:** critical | warning | nit
> - **Comment:** {final polished comment text — ready to post to GitHub as-is}
> - **Rationale:** {one sentence on why this was included and how the two agents' perspectives were reconciled}
> ```
>
> If after arbitration there are NO findings worth including, output:
> ```
> ## Final Review: 0 findings
> This PR looks clean. No actionable issues after adversarial review.
> ```
>
> **Bash hygiene:** Only run Bash for actual shell commands (gh, git, echo, etc.). Do ALL reasoning and analysis as plain text output — never inside bash script comments. Never write shell scripts with `#` comment blocks to think through logic. Avoid `->`, `=>`, or `>` characters (including `2>/dev/null`) inside any bash command you run. Do NOT chain commands with `;`, `&&`, or `||`. Use the **Read** tool instead of `cat`, use the **Glob** tool instead of `ls`, use the **Grep** tool instead of `grep`, `awk`, `head`, or `tail` — never run those via Bash.

Wait for Agent 3 to complete. Parse its output to extract the final findings list.

## Phase 4: Interactive Triage

Present findings to the user ONE AT A TIME.

For each finding (R1, R2, R3...):

1. **Display it clearly** — show:
   - Severity badge and title
   - File path and line number
   - The proposed inline comment text
   - The arbiter's rationale (briefly)

2. **Ask the user** with `AskUserQuestion`:
   - **"Post comment"** — use the comment text exactly as-is
   - **"Edit message"** — user wants to modify the comment. After they select this, ask a follow-up question where they can type their replacement text via the "Other" option. Present the original text as a starting point.
   - **"Discuss"** — user wants to understand this issue better before deciding. Explain the full context: what Agent 1 found, what Agent 2 challenged, how the Arbiter ruled, and your own assessment. Then re-present the triage options.
   - **"Discard"** — skip this finding entirely. Do not include it in the review.

3. **Record the decision**: For each finding, store whether it's included and the final comment text.

If there are more than 10 findings, tell the user the total count and ask if they want to:
- Triage all findings one by one
- Triage only critical + warning, auto-discard nits
- Triage only critical, auto-discard warning + nits

## Phase 5: Review Submission

After all findings are triaged:

1. **Show the summary** — list every comment that will be posted:
   ```
   Review Summary: {N} inline comments

   1. {file}:{line} — {first ~60 chars of comment}...
   2. {file}:{line} — {first ~60 chars of comment}...
   ...
   ```

2. **Ask review type** with `AskUserQuestion`:
   - **"Request changes"** — if there are critical findings (recommend this if any critical findings exist)
   - **"Comment"** — neutral review, just feedback
   - **"Approve"** — approve the PR, comments are suggestions only

3. **Ask review body** with `AskUserQuestion`:
   - **"Generate summary"** — you write a concise 2-3 sentence review summary based on the findings and their themes
   - **"Write custom"** — user provides their own review body via the "Other" option
   - **"No body"** — submit with inline comments only, no top-level body

4. **Build and submit the review** using a single `gh api` call:

   ```bash
   # Construct the JSON payload with ALL inline comments and submit in ONE call
   gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews \
     --method POST \
     --input - <<'EOF'
   {
     "commit_id": "{HEAD_SHA}",
     "body": "{review body or empty string}",
     "event": "{APPROVE|REQUEST_CHANGES|COMMENT}",
     "comments": [
       {
         "path": "{file}",
         "line": {line_number},
         "side": "RIGHT",
         "body": "{comment text}"
       }
     ]
   }
   EOF
   ```

   **CRITICAL:** The `line` field must be the line number as it appears in the NEW version of the file (right side of the diff). This is what the agents report. The `side` should always be `"RIGHT"` unless commenting on a deleted line.

5. **Confirm success** — show the user the review URL from the API response.

6. If the API call fails:
   - If 422 (validation error): likely a line number mapping issue. Show the error, offer to submit as a top-level comment instead.
   - If 401/403: authentication issue. Tell the user to run `gh auth status` and re-authenticate.
   - If the error mentions "commit_id": the HEAD may have changed. Re-fetch with `gh pr view $ARGUMENTS --json headRefOid --jq .headRefOid`.

## Rules

- NEVER submit the review without explicit user confirmation in Phase 5
- NEVER skip the adversarial phases — all 3 agents MUST run
- Run agents SEQUENTIALLY (each needs the previous agent's output)
- Keep inline comments concise — aim for 1-3 sentences per comment
- If a finding lacks a precise line number, default to the first changed line in that file
- Escape special characters in comment text before embedding in JSON (quotes, newlines, backslashes)
- If the user says "stop" or "cancel" at any point during triage, abort the workflow gracefully
