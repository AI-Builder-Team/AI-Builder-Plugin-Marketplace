---
name: review-pr-om
description: PR review using pr-review-toolkit specialized agents, senior verification, interactive triage, and GitHub inline comments
argument-hint: <pr-number>
disable-model-invocation: true
allowed-tools: Bash(gh repo view *), Bash(gh pr view *), Bash(gh pr diff *), Bash(gh api repos/*/pulls/*/reviews), Bash(gh auth status), Bash(git log *), Bash(git blame *), Bash(git show *), Bash(git diff *), Bash(jq *), Bash(grep *), Bash(awk *), Bash(head *), Bash(tail *), Bash(wc *), Bash(cat *), Bash(ls *), Read, Grep, Glob, Task, AskUserQuestion, WebFetch
---

# PR Review

You are running an interactive PR review workflow for PR **#$ARGUMENTS**.

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

## Phase 1: Specialized Review (Parallel Agents)

Launch ALL pr-review-toolkit agents in parallel using the **Task** tool with `run_in_background: true`.

**Agents to launch:**

| Agent | `subagent_type` | `model` | Focus |
|-------|----------------|---------|-------|
| Code Quality | `pr-review-toolkit:code-reviewer` | haiku | Bugs, security vulnerabilities, logic errors, API misuse, style guide compliance |
| Silent Failures | `pr-review-toolkit:silent-failure-hunter` | haiku | Swallowed exceptions, empty catch blocks, silent error suppression, inadequate fallbacks |
| Test Coverage | `pr-review-toolkit:pr-test-analyzer` | haiku | Test coverage gaps, test quality, missing edge case tests |
| Comments | `pr-review-toolkit:comment-analyzer` | haiku | Comment accuracy, stale/misleading docs, comment rot |
| Type Design | `pr-review-toolkit:type-design-analyzer` | haiku | Type invariants, schema design, encapsulation quality |
| Code Simplification | `pr-review-toolkit:code-simplifier` | haiku | Unnecessary complexity, readability improvements, over-engineering |

Skip `pr-review-toolkit:type-design-analyzer` if no new types or interfaces are introduced in the PR.

**Prompt template for each agent:**

> Review PR #$ARGUMENTS in {REPO}.
>
> **PR description:**
> {PR_BODY — fetch via `gh pr view $ARGUMENTS --json body --jq .body`}
>
> **Changed files:**
> {CHANGED_FILES_LIST from PR Context above}
>
> Get the full diff with `gh pr diff $ARGUMENTS` and read the source files using the Read tool to understand surrounding context. Do not review the diff in isolation.
>
> **Output format:** For EACH issue found, output:
>
> ```
> ### F{N}: {one-line title}
> - **File:** {exact file path}
> - **Line:** {line number in the NEW version of the file}
> - **Severity:** critical | warning | nit
> - **Category:** {your specialty area}
> - **Description:** {detailed explanation — what's wrong, why it matters, what could go wrong}
> - **Suggested comment:** {the exact text to post as a GitHub inline comment — concise, constructive, specific}
> ```
>
> **Do NOT flag:**
> - Style preferences (formatting, bracket placement) unless they cause confusion
> - Missing documentation unless it's a public API
> - "Nit" issues that don't affect correctness or readability
> - Things that are clearly intentional and well-reasoned
>
> If you find NO issues, say "NO_ISSUES_FOUND" — but you MUST justify this by listing the specific areas you examined and why each is clean. Do not just say "looks good". Example: "Checked error handling in X — all paths return or throw. Checked boundary conditions in Y — input is validated at line Z."

**After all agents complete — consolidate findings:**

1. Collect outputs from all agents.
2. Renumber all findings sequentially as F1, F2, F3, etc.
3. Deduplicate — if multiple agents flagged the same issue on the same line, merge into one finding keeping the most detailed description and combining insights from both agents.
4. Tag each finding with its source agent (e.g., "Source: code-reviewer") for traceability.
5. Save the consolidated findings list — this is the input for Phase 2.

## Phase 2: Senior Review (Verification & Calibration)

Spawn a `general-purpose` subagent with `model: "sonnet"`.

**Prompt for Senior Reviewer:**

> You are a senior staff engineer performing the final verification pass on a PR review. Your job is to verify each finding against the actual code, calibrate severity, catch what the specialists missed, and produce the final review.
>
> **Your default stance is inclusion** — a finding survives unless you can prove it's wrong. You are not here to argue the author's perspective or play devil's advocate. You are here to ensure the review is accurate and complete.
>
> **The PR:** #$ARGUMENTS
>
> **Step 1:** Run `gh pr diff $ARGUMENTS` and read the relevant source files to independently understand the code. Also read the PR description with `gh pr view $ARGUMENTS --json body --jq .body`.
>
> **Step 2:** For EACH finding below, read the flagged code in its surrounding context and assign a verdict:
>
> {INSERT CONSOLIDATED FINDINGS FROM PHASE 1 HERE}
>
> **Verdicts:**
> - **confirmed** — the finding is accurate as stated. Keep severity and comment as-is.
> - **escalated** — the finding is real but the specialists *understated* the severity. Explain what they missed and upgrade the severity.
> - **downgraded** — the finding is real but overstated. Adjust the severity downward and explain why.
> - **refined** — the finding is directionally correct but the description or comment needs improvement. Provide an improved comment.
> - **dismissed** — the finding is a false positive. **You MUST cite the specific line(s) of code, type constraint, or framework guarantee that proves this is safe.** Vague reasoning like "this is theoretical", "unlikely in practice", or "the author probably intended this" is NOT sufficient for dismissal.
>
> For each finding, also consider:
> - Does the surrounding code (callers, error boundaries, type system) make this safe? Cite the specific lines.
> - Is the severity calibrated correctly? Would this cause a production issue, a subtle bug, or just confusion?
> - Is the suggested comment accurate, actionable, and constructive? Improve it if not.
>
> **Step 3:** Independently scan for issues the specialists MISSED. Focus on:
> - Subtle bugs that require multi-file context
> - Security issues that only appear when you trace data flow end-to-end
> - Edge cases that require domain knowledge
> - Interaction effects between changes in different files
>
> **Step 4:** Output the FINAL review. Include all confirmed, escalated, downgraded, and refined findings. Include missed issues you discovered. Exclude only dismissed findings.
>
> **Output format:**
>
> ```
> ## Final Review: {total count} findings
>
> ### R{N}: {title}
> - **File:** {exact file path}
> - **Line:** {line number in the new version of the file}
> - **Severity:** critical | warning | nit
> - **Verdict:** {confirmed | escalated | downgraded | refined | new}
> - **Comment:** {final polished comment text — ready to post to GitHub as-is}
> - **Rationale:** {one sentence: why this verdict, what evidence}
> ```
>
> Then list any dismissed findings separately:
>
> ```
> ## Dismissed: {count} findings
>
> ### D{N}: {original title}
> - **Reason:** {specific code citation or guarantee that proves this is safe}
> ```
>
> If ALL findings are dismissed AND you found no new issues, output:
> ```
> ## Final Review: 0 findings
> This PR looks clean after verification. No actionable issues found.
>
> ## Dismissed: {count} findings
> {list each with specific dismissal reason}
> ```
>
> **Bash hygiene:** Only run Bash for actual shell commands (gh, git, echo, etc.). Do ALL reasoning and analysis as plain text output — never inside bash script comments. Never write shell scripts with `#` comment blocks to think through logic. Avoid `->`, `=>`, or `>` characters (including `2>/dev/null`) inside any bash command you run. Do NOT chain commands with `;`, `&&`, or `||`. Use the **Read** tool instead of `cat`, use the **Glob** tool instead of `ls`, use the **Grep** tool instead of `grep`, `awk`, `head`, or `tail` — never run those via Bash.

Wait for the Senior Reviewer to complete. Parse its output to extract the final findings list (R{N} items only — dismissed items are excluded from triage but preserved for the "Discuss" option).

## Phase 3: Interactive Triage

Present findings to the user ONE AT A TIME.

For each finding (R1, R2, R3...):

1. **Display it clearly** — show:
   - Severity badge and title
   - File path and line number
   - The proposed inline comment text
   - The senior reviewer's verdict and rationale (briefly)

2. **Ask the user** with `AskUserQuestion`:
   - **"Post comment"** — use the comment text exactly as-is
   - **"Edit message"** — user wants to modify the comment. After they select this, ask a follow-up question where they can type their replacement text via the "Other" option. Present the original text as a starting point.
   - **"Discuss"** — user wants to understand this issue better before deciding. Explain the full context: what the specialized agents originally found (and which agent sourced it), the Senior Reviewer's verdict and reasoning (including any severity changes), and if the finding was refined, what changed and why. If the finding was escalated, emphasize what the specialists underestimated. Then re-present the triage options.
   - **"Discard"** — skip this finding entirely. Do not include it in the review.

3. **Record the decision**: For each finding, store whether it's included and the final comment text.

If there are more than 10 findings, tell the user the total count and ask if they want to:
- Triage all findings one by one
- Triage only critical + warning, auto-discard nits
- Triage only critical, auto-discard warning + nits

## Phase 4: Review Submission

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

4. **Validate all line numbers locally before submitting.** Run the diff through this Python snippet and remap any out-of-range lines to the last line of the nearest hunk in that file. Do this entirely locally — never make API calls to test individual line numbers.

   ```bash
   gh pr diff {PR_NUMBER} | python3 -c "
   import sys, re, json

   current_file = None
   valid_ranges = {}

   for line in sys.stdin:
       line = line.rstrip()
       if line.startswith('+++ b/'):
           current_file = line[6:]
           valid_ranges[current_file] = []
       elif line.startswith('@@ '):
           m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
           if m:
               start = int(m.group(1))
               count = int(m.group(2)) if m.group(2) else 1
               if current_file:
                   valid_ranges[current_file].append((start, start + count - 1))

   with open('/tmp/pr_review.json') as f:
       payload = json.load(f)

   for c in payload['comments']:
       ranges = valid_ranges.get(c['path'], [])
       if not any(s <= c['line'] <= e for s, e in ranges):
           # Remap to the end of the last hunk in this file
           if ranges:
               c['line'] = ranges[-1][1]
               print(f'REMAPPED {c[\"path\"]}:{c[\"line\"]} -> {ranges[-1][1]}', file=sys.stderr)
           else:
               print(f'SKIP {c[\"path\"]}:{c[\"line\"]} (file not in diff)', file=sys.stderr)

   with open('/tmp/pr_review.json', 'w') as f:
       json.dump(payload, f)
   "
   ```

   After running validation, review any REMAPPED/SKIP lines printed to stderr and adjust comment text if the remap changed the target line significantly.

5. **Build and submit the review** using a single `gh api` call:

   ```bash
   # Construct the JSON payload with ALL inline comments and submit in ONE call
   gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews \
     --method POST \
     --input /tmp/pr_review.json
   ```

   Write the payload to `/tmp/pr_review.json` using Python (`json.dump`) rather than shell heredoc to avoid escaping issues with quotes, newlines, and backslashes in comment text.

   **CRITICAL:** The `line` field must be the line number as it appears in the NEW version of the file (right side of the diff). The `side` should always be `"RIGHT"` unless commenting on a deleted line.

6. **Confirm success** — show the user the review URL from the API response.

7. If the API call fails:
   - If 422 (validation error): Re-run the local diff validation from step 4 to identify which line(s) are still out of range, remap them, and retry **once**. **NEVER test individual comments by submitting them as separate API reviews** — submitted reviews cannot be deleted and will appear as noise on the PR.
   - If 401/403: authentication issue. Tell the user to run `gh auth status` and re-authenticate.
   - If the error mentions "commit_id": the HEAD may have changed. Re-fetch with `gh pr view $ARGUMENTS --json headRefOid --jq .headRefOid`.

## Rules

- NEVER submit the review without explicit user confirmation in Phase 4
- NEVER skip phases — Phase 1 (all specialized agents) and Phase 2 (Senior Review) MUST both run
- Phase 1 agents run in PARALLEL. Phase 2 depends on Phase 1 output. Respect this dependency.
- Keep inline comments concise — aim for 1-3 sentences per comment
- If a finding lacks a precise line number, default to the first changed line in that file
- Write the JSON payload with Python `json.dump` to `/tmp/pr_review.json` — never use shell heredoc, which mishandles quotes and backslashes in comment text
- Always run local diff validation (Phase 4 step 4) before submitting — validate line numbers against hunk ranges from `gh pr diff`, never by making test API calls
- **NEVER submit individual comments as separate reviews to test line validity** — submitted reviews cannot be deleted and pollute the PR with noise
- If the user says "stop" or "cancel" at any point during triage, abort the workflow gracefully
