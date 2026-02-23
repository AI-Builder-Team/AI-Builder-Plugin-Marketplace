---
description: Fetch unresolved PR review comments, validate findings, and address them interactively
argument-hint: [pr-url]
allowed-tools: Bash(gh api:*), Bash(gh pr view:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git push), Bash(git log:*), Bash(git show:*), Bash(git status:*), Bash(pnpm:*), Bash(uv:*), Bash(cd:*)
---

## Context

You are helping address unresolved PR review comments.

## Phase 1: Identify the PR and Current User

- Determine the current GitHub username by running `gh api user --jq .login`. Store this as `$GH_USER` for use throughout the workflow.
- If `$ARGUMENTS` is provided, extract the PR number from the URL (e.g., `https://github.com/org/repo/pull/123` → `123`).
- If no arguments are provided, determine the PR for the current branch using `gh pr view --json number,url`.
- Store the PR number and repo info for later use.

## Phase 2: Fetch Unresolved Review Comments

Fetch all review comments and top-level PR comments:

1. **Review thread comments**: Use the following GraphQL query to fetch all review threads with resolution status. Only include threads where `isResolved == false`.

```bash
gh api graphql -f query='
query {
  repository(owner: "{owner}", name: "{repo}") {
    pullRequest(number: {number}) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          path
          line
          startLine
          comments(first: 50) {
            nodes {
              id
              databaseId
              author { login }
              body
              createdAt
              path
              startLine
              line
            }
          }
        }
      }
    }
  }
}'
```
2. **Top-level PR comments**: Fetch top-level PR comments (not review thread comments) using:

```bash
gh api repos/{owner}/{repo}/issues/{pull_number}/comments --paginate --jq '.[] | {id: .id, node_id: .node_id, user: .user.login, body: .body, created_at: .created_at}'
```

Evaluate each one — only include it if it is substantively reviewing code or requesting changes. Exclude general discussion, acknowledgments, or status updates.
3. **Filter out dismissed items**: For each unresolved comment thread, check if `$GH_USER` has replied with a natural language dismissal (e.g., "won't fix", "out of scope", "not addressing this", "intentional", "by design", etc.). If a dismissal reply exists, exclude that comment. Do NOT use rigid keyword matching — use natural language understanding. If it's unclear whether a reply is a dismissal, keep the comment in the list and flag it for clarification later.

## Phase 3: Create the MD File

Create a file at the repo root named `pr-<NUMBER>-addressing-reviews.md` where `<NUMBER>` is the actual PR number.

Write the file with this structure:

```markdown
# PR #<NUMBER> — Addressing Review Comments

**PR**: <pr-url>
**Date**: <today's date>
**Status**: Fetching comments...

---

## Unresolved Review Comments

### 1. <Short summary of the comment>
- **Reviewer**: <reviewer-username>
- **File**: `<file-path>` (lines <start>-<end> or line <line>)
- **Comment**: <full comment text>
- **Validation**: Pending...
- **Decision**: Pending
- **Response Draft**: Pending

---

### 2. ...
```

If there are top-level PR comments included, add a separate section:

```markdown
## Top-Level Review Comments

### T1. <Short summary>
- **Reviewer**: <reviewer-username>
- **Comment**: <full comment text>
- **Validation**: Pending...
- **Decision**: Pending
- **Response Draft**: Pending
```

## Phase 4: Validate Each Comment (Parallel)

For each comment in the MD file, launch a parallel task (using the Task tool) that:

1. Reads the relevant file and line range referenced by the comment.
2. Understands the reviewer's concern in context of the actual code.
3. Assesses validity using one of these labels:
   - **Valid** — the reviewer's finding is correct, code needs a fix
   - **Likely Valid** — probably correct but needs user confirmation
   - **Invalid** — the code is actually fine as-is
   - **Needs Clarification** — ambiguous, can't determine without more context
4. Writes a brief justification (2-3 sentences) explaining the assessment.

After all parallel tasks complete, update the MD file — replace each "Pending..." validation with the actual assessment and justification.

Update the file status to "Validation complete — ready for review".

## Phase 5: Interactive Decision Mode

Go through each comment **one at a time** with the user:

1. Present the comment summary, the reviewer's concern, the file/line reference, and the validation assessment.
2. Ask the user: **"Are we fixing this or not fixing this?"**
3. Record the decision in the MD file under the **Decision** field for that item.
4. If the user wants to provide additional context for the response, capture that too.

**IMPORTANT**: Do NOT start any fixes during this phase. Only collect decisions.

Continue until all items have a decision.

## Phase 6: Draft Responses to Reviewer

**Flavor check**: Before drafting, check if `~/.claude/flavor.md` exists. If it does, read it — it contains tone/style instructions for how to write responses (e.g., casual, witty, emoji-heavy, formal). Apply that flavor to all drafted responses below while keeping them concise and professional. If the file doesn't exist, use the default professional tone.

For each comment, draft a concise response on behalf of the user:

- For items being **fixed**: Acknowledge the finding and state the planned fix briefly (e.g., "Good catch — fixing this by [approach]." or "Agreed, will update [what] to [how].").
- For items **not being fixed**: Provide a clear, respectful explanation of why (e.g., "This is intentional because [reason]." or "Out of scope for this PR — tracking separately in [ticket/issue].").
- **Every response MUST be prefixed with a robot emoji** to indicate it was generated by an LLM (e.g., "robot-emoji Good catch — fixing this by...").

Write all draft responses into the MD file under each item's **Response Draft** field.

Update the file status to "Response drafts ready — awaiting approval".

**Present the drafts to the user for review.** Ask them to review the MD file and confirm or request edits. Wait for explicit approval before proceeding.

## Phase 7: Post Responses on GitHub

Once the user approves the response drafts:

For each review thread comment, post the response as an **inline reply** using the following command:

```bash
gh api repos/{owner}/{repo}/pulls/{pull_number}/comments \
  -f body="Your response text" \
  -F in_reply_to={comment_database_id}
```

Where `{comment_database_id}` is the `databaseId` of the last comment in the thread you're replying to (from the GraphQL query in Phase 2). This ensures the reply is posted on the correct review thread, not as a new top-level comment.

For top-level PR comments, reply on the same comment thread using:

```bash
gh api repos/{owner}/{repo}/issues/{pull_number}/comments \
  -f body="Your response text"
```

Update the file status to "Responses posted — starting fixes".

## Phase 8: Implement Fixes

For each comment where the decision is **"Fix"**, implement the fix:

1. Make the code change.
2. Run lint on changed files only (follow project CLAUDE.md lint practices — e.g., `pnpm lint <files>` for frontend, `uv run ruff check <files>` for backend).
3. Run build check if applicable (`pnpm build` for frontend, `pnpm tsc --noEmit` for type-check).
4. Present the change to the user for review.
5. Once approved, create a **single commit** for this fix. Use a descriptive commit message referencing the review comment.
6. Do **NOT** push yet.

Repeat for each fix item.

## Phase 9: Holistic Review

After all individual fixes are committed, perform a combined review before pushing:

1. Run `git diff HEAD~N` (where N is the number of fix commits) to see all changes together.
2. Review the combined diff for:
   - Duplicated logic across fixes
   - Conflicting or inconsistent changes
   - Opportunities to consolidate related fixes
3. Present the combined diff summary to the user for final approval.
4. If issues are found, address them in an additional commit before proceeding.

## Phase 10: Push

After all fixes are committed and the holistic review is approved:

1. Push all commits to the remote branch.
2. Update the MD file status to "All fixes implemented and pushed".
3. Provide a final summary of what was done.
