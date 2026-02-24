---
name: check-review-om
description: Verify that PR review feedback was actionably implemented, then approve or re-request changes
argument-hint: <pr-number>
disable-model-invocation: true
allowed-tools: Bash(gh repo view *), Bash(gh pr view *), Bash(gh pr diff *), Bash(gh api repos/*/pulls/*/reviews), Bash(gh api repos/*/pulls/*/comments), Bash(gh auth status), Bash(git log *), Bash(git show *), Bash(git diff *), Bash(jq *), Bash(grep *), Bash(awk *), Bash(head *), Bash(tail *), Bash(wc *), Bash(cat *), Bash(ls *), Read, Grep, Glob, Task, AskUserQuestion
---

# Review Feedback Verification

You are running an interactive workflow to verify whether prior PR review feedback was implemented for PR **#$ARGUMENTS**.

ultrathink

## PR Context

- **PR Number:** $ARGUMENTS
- **Repository:** !`gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "UNKNOWN_REPO"`
- **PR Title:** !`gh pr view $0 --json title --jq .title 2>/dev/null || echo "UNKNOWN_TITLE"`
- **PR Author:** !`gh pr view $0 --json author --jq .author.login 2>/dev/null || echo "UNKNOWN_AUTHOR"`
- **HEAD SHA:** !`gh pr view $0 --json headRefOid --jq .headRefOid 2>/dev/null || echo "UNKNOWN_SHA"`
- **Base Branch:** !`gh pr view $0 --json baseRefName --jq .baseRefName 2>/dev/null || echo "UNKNOWN_BASE"`

## Pre-flight Checks

Before starting, verify:
1. The repository is not "UNKNOWN_REPO" — if it is, tell the user to run from within a git repo.
2. The PR title is not "UNKNOWN_TITLE" — if it is, the PR number may be invalid. Ask the user to verify.
3. If any context value is "UNKNOWN_*", stop and report the issue. Do NOT proceed.

Store the HEAD SHA and repo nameWithOwner — you will need them for the final API call. Parse the `OWNER` and `REPO` from nameWithOwner (e.g., `"octocat/hello-world"` → OWNER=`octocat`, REPO=`hello-world`).

## Phase 1: Fetch Prior Review Feedback

Run these commands, substituting OWNER and REPO from the context above:

1. Fetch inline review comments (comments anchored to specific lines):
```bash
gh api repos/OWNER/REPO/pulls/$ARGUMENTS/comments --jq '[.[] | {id: .id, path: .path, line: .line, original_line: .original_line, body: .body, user: .user.login, created_at: .created_at, in_reply_to_id: .in_reply_to_id}]'
```

2. Fetch review-level summaries (top-level bodies and states):
```bash
gh api repos/OWNER/REPO/pulls/$ARGUMENTS/reviews --jq '[.[] | {id: .id, user: .user.login, body: .body, state: .state, submitted_at: .submitted_at}]'
```

3. Get the current diff:
```bash
gh pr diff $ARGUMENTS
```

**Process the data:**
- From inline comments: keep only root comments (those where `in_reply_to_id` is null). Replies are context, not actionable items.
- From reviews: note which reviewers posted `REQUEST_CHANGES` state and what their top-level body said.
- Build the working list: all root inline comments + any substantive concerns expressed in review bodies (not just boilerplate like "LGTM").

If there are NO root inline comments AND NO reviews with `REQUEST_CHANGES` state AND no substantive review body feedback:
> "No review feedback found on PR #$ARGUMENTS. There is nothing to verify."

Stop here.

Otherwise print:
```
Found {N} inline comment(s) from: {reviewer logins}
Reviews requesting changes: {count}
Proceeding to verification…
```

## Phase 2: Verification Agent

Spawn a `general-purpose` subagent via the **Task** tool.

**Prompt for the Verification Agent:**

> You are verifying whether prior review feedback was addressed on PR #$ARGUMENTS.
>
> **Prior inline review comments (root comments only):**
> {INSERT FULL LIST — include comment id, path, line, body, reviewer login}
>
> **Review-level feedback (from REQUEST_CHANGES reviews):**
> {INSERT REVIEW BODIES AND STATES}
>
> **Current diff:**
> {INSERT FULL DIFF FROM PHASE 1}
>
> **Your tasks:**
>
> **Step 1:** For each inline comment, use the Read tool to read the current state of the file at the relevant location (±20 lines of context). Do NOT rely only on the diff.
>
> **Step 2:** Run `gh pr diff $ARGUMENTS` yourself if you need to cross-reference what changed.
>
> **Step 3:** For EACH inline comment, assess whether the underlying issue was addressed:
> - **ADDRESSED** — The code change directly resolves the concern. The issue no longer applies to the current code.
> - **PARTIALLY_ADDRESSED** — Something changed, but the core concern remains, the fix is incomplete, or the change introduces a related new problem.
> - **UNADDRESSED** — No relevant change was made, or the change does not resolve the issue described.
> - **OBSOLETE** — The code containing this issue was entirely removed (deleted function, removed file). The concern no longer applies by omission.
>
> **Step 4:** For any concerns raised only in review bodies (not inline), assess whether those broader points were addressed by the overall diff.
>
> **Step 5:** Output for EACH inline comment in this exact format:
>
> ```
> ### C{N}: {first 80 chars of original comment body}
> - **File:** {path}
> - **Line:** {original line number}
> - **Reviewer:** {login}
> - **Original feedback:** {full original comment body}
> - **Verdict:** ADDRESSED | PARTIALLY_ADDRESSED | UNADDRESSED | OBSOLETE
> - **Evidence:** {quote the relevant current code lines or describe exactly what changed. Be specific — no vague assertions.}
> - **Remaining concern:** {if PARTIALLY_ADDRESSED or UNADDRESSED: what specifically still needs fixing. Otherwise: N/A}
> ```
>
> Then for review-body feedback (if any), output:
>
> ```
> ### RB{N}: {first 80 chars of review body concern}
> - **Reviewer:** {login}
> - **Original concern:** {full text}
> - **Verdict:** ADDRESSED | PARTIALLY_ADDRESSED | UNADDRESSED | OBSOLETE
> - **Evidence:** {specific evidence}
> - **Remaining concern:** {if applicable. Otherwise: N/A}
> ```
>
> End with a summary block:
>
> ```
> ## Verification Summary
> - ADDRESSED: {count}
> - PARTIALLY_ADDRESSED: {count}
> - UNADDRESSED: {count}
> - OBSOLETE: {count}
> - Total: {count}
> ```
>
> **Bash hygiene:** Only run Bash for actual shell commands (gh, echo, etc.). Do ALL reasoning and analysis as plain text output — never inside bash script comments. Never write shell scripts with `#` comment blocks to think through logic. For file reading use the Read tool, for searching use the Grep and Glob tools — do not run grep, awk, head, or tail via Bash unless there is no alternative.

Wait for the Verification Agent to complete. Save its full output.

## Phase 3: Interactive Triage

Present findings ONE AT A TIME. Order: UNADDRESSED first, then PARTIALLY_ADDRESSED, then ADDRESSED, then OBSOLETE.

For each finding:

1. **Display clearly:**
   - Verdict badge: 🔴 UNADDRESSED / 🟡 PARTIALLY_ADDRESSED / 🟢 ADDRESSED / ⚪ OBSOLETE
   - File path and line number
   - Original feedback (full text)
   - Evidence from the verification agent
   - Remaining concern (if any)

2. **For 🔴 UNADDRESSED and 🟡 PARTIALLY_ADDRESSED**, ask with `AskUserQuestion`:
   - **"Re-request change"** — include this in the final review. After selecting, ask a follow-up where the user can edit/confirm comment text (pre-fill with the original feedback text as a starting point via "Other" prompt).
   - **"Accept as-is"** — override the verdict; treat as resolved. Do not include in re-request.
   - **"Discuss"** — explain in detail: what the original concern was, what changed (or didn't), why the agent gave this verdict, your own assessment. Then re-present the two options above.
   - **"Skip"** — exclude from the final review action entirely (neither re-request nor explicit acceptance).

3. **For 🟢 ADDRESSED and ⚪ OBSOLETE**, ask with `AskUserQuestion`:
   - **"Looks good"** — confirm resolved (default).
   - **"Actually unresolved"** — override; treat as UNADDRESSED and go through the re-request flow.

4. Record each decision.

If there are more than 8 findings, tell the user the total count upfront and ask:
- **"Triage all one by one"**
- **"Triage UNADDRESSED + PARTIALLY only, auto-accept the rest"** (Recommended if mostly resolved)
- **"Use agent verdicts directly"** — skip triage, go straight to Phase 4 using agent verdicts as-is

## Phase 4: Decision and Submission

After triage:

1. **Show triage summary:**
   ```
   Triage complete:
   - Re-requesting changes on {N} item(s)
   - Accepted as resolved: {M} item(s)
   - Skipped: {K} item(s)

   Re-requesting:
   1. {file}:{line} — {first ~60 chars of comment}
   ...

   Accepted as resolved:
   - {file}:{line} (ADDRESSED)
   ...
   ```

2. **Ask review type** with `AskUserQuestion`:
   - **"Request changes"** — re-request on remaining items (recommend this if any items are being re-requested)
   - **"Approve"** — approve the PR (recommend this if all feedback was addressed/accepted)
   - **"Comment only"** — leave comments without a formal approve/request decision

3. **Ask review body** with `AskUserQuestion`:
   - **"Generate summary"** — write a concise 2-3 sentence body summarizing what was addressed and what (if anything) remains
   - **"Write custom"** — user provides their own body via "Other"
   - **"No body"** — inline comments only (or no body if approving cleanly with nothing to say)

4. **Build and submit the review** in a single `gh api` call:

   ```bash
   gh api repos/OWNER/REPO/pulls/$ARGUMENTS/reviews \
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

   If approving with no inline comments, submit with `"comments": []`.

   **CRITICAL:** `line` must be the line number in the NEW version of the file. Always use `"side": "RIGHT"` unless commenting on a deleted line. Escape all special characters in comment text (quotes → `\"`, newlines → `\n`, backslashes → `\\`).

5. **Confirm success** — show the review URL from the API response.

6. **Error handling:**
   - 422 (validation error): likely a stale line number. Show the error, offer to submit as a top-level comment instead.
   - 401/403: authentication issue. Tell the user to run `gh auth status`.
   - "commit_id" mismatch: HEAD changed since the skill started. Re-fetch with `gh pr view $ARGUMENTS --json headRefOid --jq .headRefOid` and retry.

## Rules

- NEVER submit the review without explicit user confirmation in Phase 4
- NEVER invent feedback — only work with comments actually fetched from GitHub
- NEVER include a comment in the submission if the user chose "Accept as-is" or "Skip"
- Keep re-request comment texts concise — 1-3 sentences, specific to what remains unresolved
- If the user says "stop" or "cancel" at any point, abort gracefully
- When the agent verdict is borderline, surface the evidence and let the user decide rather than guessing
