---
name: address-pr-om
description: Respond to PR review comments (valid/invalid), fix valid issues, and reply with the fix commit SHA
argument-hint: <pr-number>
allowed-tools: Bash(gh repo view *), Bash(gh pr view *), Bash(gh pr diff *), Bash(gh api repos/*/pulls/*/comments), Bash(gh api repos/*/pulls/*/comments/*/replies), Bash(gh api repos/*/pulls/*/reviews), Bash(gh api repos/*/issues/*/comments), Bash(gh api repos/*/issues/*/comments/*), Bash(gh auth status), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git rev-parse *), Bash(git log *), Bash(git diff *), Bash(jq *), Read, Grep, Glob, Edit, Write, AskUserQuestion
---

# Address PR Review Comments

You are running an interactive workflow to respond to review comments on PR **#$ARGUMENTS**, fix valid issues, and confirm with a commit SHA.

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

Store the HEAD SHA and repo nameWithOwner — you will need them later. Parse `OWNER` and `REPO` from nameWithOwner (e.g., `"octocat/hello-world"` → OWNER=`octocat`, REPO=`hello-world`).

## Phase 1: Fetch & Assess

### 1.1 Fetch Comments

Run these commands substituting OWNER and REPO:

```bash
gh api repos/OWNER/REPO/pulls/$ARGUMENTS/comments --jq '[.[] | {id: .id, path: .path, line: .line, original_line: .original_line, body: .body, user: .user.login, created_at: .created_at, in_reply_to_id: .in_reply_to_id}]'
```

```bash
gh api repos/OWNER/REPO/pulls/$ARGUMENTS/reviews --jq '[.[] | {id: .id, user: .user.login, body: .body, state: .state, submitted_at: .submitted_at}]'
```

```bash
gh api repos/OWNER/REPO/issues/$ARGUMENTS/comments --jq '[.[] | {id: .id, body: .body, user: .user.login, created_at: .created_at}]'
```

**Process the data:**
- From inline comments: keep only **root comments** (where `in_reply_to_id` is null). Replies are context, not actionable items.
- From reviews: keep only reviews with a substantive body (skip empty bodies and bare "LGTM" / "Approved").
- From top-level PR comments (issue comments): keep only comments from users **other than the PR author** that have a substantive body (skip empty bodies, bare "LGTM" / "Approved", and bot-generated comments). These are general review comments posted outside of inline code review.
- Build the working list: all root inline comments + substantive review bodies + substantive top-level PR comments.

If there are NO root inline comments AND NO reviews with substantive body text AND NO substantive top-level PR comments:
> "No review feedback found on PR #$ARGUMENTS. Nothing to address."

Stop here.

### 1.2 Read Diff and Source Files

```bash
gh pr diff $ARGUMENTS
```

For each file referenced by a comment, use the **Read** tool to read the relevant file around the commented line (±20 lines of context). Do NOT rely only on the diff — understand the full surrounding code.

### 1.3 Assess Each Comment

For EACH item in the working list, assess:
- **VALID** — a real concern worth fixing (bug, logic error, missing handling, style rule violation, etc.)
- **INVALID** — not a real concern; explain why in 1-2 sentences (already handled, based on misunderstanding, intentional trade-off, etc.)

Draft a short 1-2 sentence reply for each:
- VALID: acknowledge the issue and state what will be fixed
- INVALID: politely explain why it is not a concern

### 1.4 Print Assessment Table

```
## Assessment: N comments

| # | Reviewer | Location | Verdict | Reply preview |
|---|----------|----------|---------|---------------|
| 1 | @alice   | foo.ts:42 | ✅ VALID | "Good catch — will extract to a named constant." |
| 2 | @bob     | bar.ts:17 | ❌ INVALID | "Not a concern — the null check at line 12 covers this path." |
```

For review body items without a line number, use the format `{file} (review body)` or `(top-level review)`.
For top-level PR comments (issue comments), use the format `(PR comment)`.

If there are ONLY invalid items and nothing to fix, proceed through Phase 2 (post replies) but skip Phase 3 (no fixes needed). Print a note to that effect.

## Phase 2: Confirm & Reply

### 2.1 Ask for Confirmation

Ask with `AskUserQuestion` (one question, not per-comment):
- **"Post all replies as shown"** — proceed with the assessments above
- **"Adjust before posting"** — user types adjustments via the "Other" input; apply them and confirm once more before posting
- **"Cancel"** — abort the entire workflow

If the user selects "Adjust before posting", apply their edits to the reply drafts and the valid/invalid verdicts, then re-display the updated table and ask again with the same two options (no "Adjust" loop — one round of adjustment only).

### 2.2 Post Replies

For each **inline comment** (has a comment id and path/line):
```bash
gh api repos/OWNER/REPO/pulls/$ARGUMENTS/comments/{comment_id}/replies --method POST --field body="..."
```

For each **review body** item:
```bash
gh api repos/OWNER/REPO/issues/$ARGUMENTS/comments --method POST --field body="Re: @{reviewer}'s review — {reply}"
```

For each **top-level PR comment** (issue comment), post a new issue comment as a reply (GitHub doesn't support threading on issue comments, so reference the reviewer and quote a snippet for context):
```bash
gh api repos/OWNER/REPO/issues/$ARGUMENTS/comments --method POST --field body="Re: @{reviewer}'s comment — {reply}"
```

Print `Replied to {N} comments.` when done.

## Phase 3: Fix & Commit

Skip this phase entirely if there are no VALID items.

### 3.1 Apply Fixes

For each VALID item (work through them in order):
1. Use the **Read** tool to read the current state of the relevant file.
2. Use the **Edit** tool to apply the fix. Do not change surrounding code that is not part of the issue.
3. Print: `Fixed: {brief description} in {file}:{line}`

### 3.2 Commit

Stage and commit all modified files:

```bash
git add {modified files}
```

```bash
git commit -m "fix: address review feedback on PR #$ARGUMENTS"
```

Use a separate `git add` call per file rather than `git add .` to avoid accidentally staging unrelated changes.

### 3.3 Push

Ask with `AskUserQuestion`:
- **"Push now"** — run `git push` immediately
- **"I'll push manually"** — skip push, continue to Phase 4

### 3.4 Get Short SHA

```bash
git rev-parse --short HEAD
```

Store this as `FIX_SHA`.

## Phase 4: Reply with Fix SHA

Skip this phase if there were no VALID items (nothing was committed).

For each VALID item that was fixed:

- If it was an **inline comment**, post a reply in the same thread:
  ```bash
  gh api repos/OWNER/REPO/pulls/$ARGUMENTS/comments/{comment_id}/replies --method POST --field body="Fixed in {FIX_SHA}."
  ```

- If it was a **review body** or **top-level PR comment**, post a new top-level comment:
  ```bash
  gh api repos/OWNER/REPO/issues/$ARGUMENTS/comments --method POST --field body="Fixed in {FIX_SHA} — addressed @{reviewer}'s concern about {brief topic}."
  ```

### Final Summary

Print:
```
Done.
- Replied to N comments (M valid, K invalid)
- Fixed M issues → commit {FIX_SHA}
```

If there were no valid items:
```
Done.
- Replied to N comments (0 valid, N invalid)
- No code changes needed
```

## Rules

- NEVER post replies without explicit user confirmation in Phase 2
- NEVER invent or fabricate comments — only work with items actually fetched from GitHub
- NEVER use `git add .` — always stage specific files by name
- NEVER commit if there are no VALID items with actual file changes
- For INVALID items, replies must be polite, specific, and cite the existing code or reason
- If a fix is ambiguous (the right approach is unclear), ask with `AskUserQuestion` before editing
- If the user says "stop" or "cancel" at any point, abort gracefully without posting or committing
- Use **Edit** for code changes — do NOT use Bash `sed` or `awk` to modify files
- If a `gh api` call fails with 401/403, tell the user to run `gh auth status`
- If a reply POST fails, print the error and continue with remaining replies — do not abort the whole workflow
