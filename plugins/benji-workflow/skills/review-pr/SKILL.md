---
name: review-pr
description: Deep PR review with inline GitHub comments. Launches parallel review agents, validates findings, drafts casual inline comments, and posts after user approval.
tools: Task, Read, Glob, Grep, Bash, AskUserQuestion
color: Orange
---

# Purpose

Run a thorough, multi-agent code review on a pull request and post concise inline comments to GitHub. The review should feel like it came from a senior engineer who actually read the code -- not a linter or AI tool.

**When to use:** "review this PR", "review PR #123", "give me a code review", or just `/review-pr`

## Instructions

### Step 1: Identify the PR

Parse `$ARGUMENTS` for a PR number. If blank, detect from the current branch:

```bash
gh pr view --json number,title,state,headRefOid
```

Then get the scope:

```bash
git diff --name-only main...HEAD
git diff --stat main...HEAD -- '*.py' '*.ts' '*.tsx' '*.js'
```

Tell the user the PR number, title, and file count before proceeding.

### Step 2: Launch review agents in parallel

Launch ALL of the following simultaneously using the Task tool with `run_in_background: true`:

| Agent | subagent_type | Focus |
|-------|--------------|-------|
| Code quality | `pr-review-toolkit:code-reviewer` | CLAUDE.md compliance, bugs, security |
| Error handling | `pr-review-toolkit:silent-failure-hunter` | Silent failures, swallowed exceptions |
| Test coverage | `pr-review-toolkit:pr-test-analyzer` | Coverage gaps, test quality |
| Comments | `pr-review-toolkit:comment-analyzer` | Accuracy, staleness, misleading docs |
| Types | `pr-review-toolkit:type-design-analyzer` | Type invariants, design quality |

Skip the type-design-analyzer if no new types/schemas are introduced.

Each agent prompt should include:
- The PR number and branch
- Changed files relevant to that agent's specialty
- Instruction to use `git diff main...HEAD`

### Step 3: Collect results

Wait for all agents to complete. Read each output.

### Step 4: Validate findings

**This is the most important step.** For every finding:

- `Read` the actual source code at the reported location
- Confirm the issue exists as described
- Drop anything that's incorrect, already handled, or not worth commenting on

False positives destroy credibility. Be ruthless about cutting.

### Step 5: Draft inline comments

Write concise, casual comments. Follow these rules:

**Tone:**
- Like a thoughtful colleague, not a linter
- 1-2 sentences. Get to the point.
- No corporate speak. No "I would suggest..." -- just say what's up
- "Nit:" for non-blocking. "Suggestion:" for substantial with rationale
- "Not blocking" where appropriate

**Content:**
- Focus on what matters: bugs, silent failures, misleading behavior, dead code
- Skip pure style nits
- Short code suggestions are fine (3-5 lines max)
- Group related issues where it makes sense

**Volume:**
- 5-7 comments max. Quality over quantity.
- Not every finding deserves a comment

### Step 6: Draft PR review body

Short and human. Structure:

- 2-3 sentences acknowledging what's good (genuinely)
- Bullet the main concerns (2-4 bullets max)
- One-line overall assessment
- Review action: `COMMENT` unless there are truly blocking issues (`REQUEST_CHANGES`)

### Step 7: Present for approval

**CRITICAL: Do NOT post to GitHub yet.**

Show the user:
- All inline comments with file:line targets
- The review body
- The review action

Ask if they want to adjust anything.

### Step 8: Post the review

Only after explicit approval, post as a single GitHub review:

```bash
COMMIT=$(gh pr view <PR> --json headRefOid -q '.headRefOid')
OWNER=$(gh pr view <PR> --json headRepositoryOwner -q '.headRepositoryOwner.login')
REPO=$(gh pr view <PR> --json headRepository -q '.headRepository.name')
```

Build JSON payload:

```json
{
  "commit_id": "<COMMIT>",
  "event": "COMMENT",
  "body": "<review body>",
  "comments": [
    {
      "path": "relative/path/to/file.py",
      "line": 42,
      "side": "RIGHT",
      "body": "Comment text"
    }
  ]
}
```

Post via:

```bash
gh api repos/$OWNER/$REPO/pulls/<PR>/reviews \
  --method POST --input /tmp/pr_review.json \
  --jq '{ id: .id, state: .state, html_url: .html_url }'
```

Return the review URL.

---

## Anti-Patterns

- **Posting without approval** -- Never. The user must greenlight every comment.
- **Trusting agent output blindly** -- Always validate against actual code.
- **Over-commenting** -- 10 comments is too many. Prioritize.
- **Sounding like AI** -- No "I would recommend considering..." Just say it.
- **Commenting on things you didn't verify** -- If you didn't read the line, don't comment on it.
- **Mixing blocking and non-blocking** -- Be clear about what actually needs fixing vs nice-to-have.

---

## Example Session

```
User: /review-pr 1724

Claude: PR #1724 "feat(eval): implement complete evaluation framework"
        42 code files changed, +4512/-139 lines
        Launching 5 review agents in parallel...

        [agents complete]

        Validated 8 findings. Here are the proposed comments:

        Comment 1 - snapshot_utils.py:128
        > This empty except swallows JSON parse errors and then...

        Comment 2 - schemas.py:27
        > This DatasetError(Exception) collides with...

        [etc.]

        PR Review Body:
        > Solid work here -- the eval framework design is clean...

        Ready to post, or want to adjust anything?

User: Comment 3 is too long, trim it

Claude: [adjusts] Updated. Ready to post?

User: Ship it

Claude: Review posted: https://github.com/.../pull/1724#pullrequestreview-...
```
